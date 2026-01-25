# Network Load Balancer - Layer 4 (TCP/UDP)
# Automatically protected by AWS Shield Standard
# Can be protected by AWS Shield Advanced for enhanced protection

resource "aws_lb" "network" {
  name               = "${var.project_name}-nlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  # Enable cross-zone load balancing for better distribution
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "${var.project_name}-nlb"
  }
}

# Target Group for TCP traffic (Layer 4)
resource "aws_lb_target_group" "tcp" {
  name        = "${var.project_name}-tcp-tg"
  port        = 80
  protocol    = "TCP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    enabled             = true
    protocol            = "TCP"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
  }

  tags = {
    Name = "${var.project_name}-tcp-tg"
  }
}

# TCP Listener (Port 80)
resource "aws_lb_listener" "tcp_80" {
  load_balancer_arn = aws_lb.network.arn
  port              = 80
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tcp.arn
  }
}

# Optional: TCP Listener (Port 443 for TLS passthrough)
resource "aws_lb_target_group" "tcp_443" {
  name        = "${var.project_name}-tcp-443-tg"
  port        = 443
  protocol    = "TCP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    enabled             = true
    protocol            = "TCP"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 30
  }

  tags = {
    Name = "${var.project_name}-tcp-443-tg"
  }
}

resource "aws_lb_listener" "tcp_443" {
  load_balancer_arn = aws_lb.network.arn
  port              = 443
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tcp_443.arn
  }
}
