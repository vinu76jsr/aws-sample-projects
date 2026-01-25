# Get latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# IAM Role for EC2 instances
resource "aws_iam_role" "ec2" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ec2-role"
  }
}

# Attach SSM managed policy for Session Manager access
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance Profile
resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# Launch Template for application servers
resource "aws_launch_template" "app" {
  name_prefix   = "${var.project_name}-app-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2.name
  }

  vpc_security_group_ids = [
    aws_security_group.app.id,
    aws_security_group.ssh.id
  ]

  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y nginx

    # Create a simple health check page
    cat > /usr/share/nginx/html/index.html <<'HTMLEOF'
    <!DOCTYPE html>
    <html>
    <head>
        <title>AWS Shield Layer 4 Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { color: green; font-weight: bold; }
            .info { background: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>AWS Shield Layer 4 Protection Demo</h1>
        <p class="status">Server is running and protected!</p>
        <div class="info">
            <h3>Protection Details:</h3>
            <ul>
                <li><strong>AWS Shield Standard:</strong> Active (automatic)</li>
                <li><strong>Layer 4 (TCP/UDP) Protection:</strong> Enabled via NLB</li>
                <li><strong>DDoS Mitigation:</strong> Automatic</li>
            </ul>
        </div>
        <div class="info">
            <h3>Instance Metadata:</h3>
            <p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>
            <p>Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)</p>
        </div>
    </body>
    </html>
    HTMLEOF

    systemctl enable nginx
    systemctl start nginx
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.project_name}-app-server"
    }
  }

  tags = {
    Name = "${var.project_name}-launch-template"
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "${var.project_name}-asg"
  desired_capacity    = 2
  max_size            = 4
  min_size            = 1
  target_group_arns   = [aws_lb_target_group.tcp.arn]
  vpc_zone_identifier = aws_subnet.private[*].id

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "${var.project_name}-app-server"
    propagate_at_launch = true
  }
}

# Auto Scaling Policy - Scale up on high network traffic (potential DDoS)
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "${var.project_name}-scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.app.name
}

# CloudWatch Alarm for high network traffic
resource "aws_cloudwatch_metric_alarm" "high_network" {
  alarm_name          = "${var.project_name}-high-network-in"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "NetworkIn"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 100000000 # 100 MB/min
  alarm_description   = "Triggered when network traffic is unusually high"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
}
