# AWS Shield Layer 4 Protection - Console Setup Guide

This guide walks you through setting up the AWS Shield Layer 4 protection architecture using the AWS Management Console.

## Table of Contents

1. [Create VPC and Networking](#1-create-vpc-and-networking)
2. [Create Security Groups](#2-create-security-groups)
3. [Create EC2 Instances](#3-create-ec2-instances)
4. [Create Network Load Balancer](#4-create-network-load-balancer)
5. [Create Auto Scaling Group](#5-create-auto-scaling-group)
6. [Set Up CloudWatch Monitoring](#6-set-up-cloudwatch-monitoring)
7. [Create SNS Topic for Alerts](#7-create-sns-topic-for-alerts)
8. [Create CloudWatch Alarms](#8-create-cloudwatch-alarms)
9. [Enable Shield Advanced (Optional)](#9-enable-shield-advanced-optional)
10. [Verification](#10-verification)
11. [Cleanup](#11-cleanup)

---

## 1. Create VPC and Networking

### 1.1 Create VPC

1. Navigate to **VPC Console** → **Your VPCs** → **Create VPC**
2. Configure:
   - **Resources to create**: VPC and more
   - **Name tag**: `shield-demo`
   - **IPv4 CIDR block**: `10.0.0.0/16`
   - **Number of Availability Zones**: 2
   - **Number of public subnets**: 2
   - **Number of private subnets**: 2
   - **NAT gateways**: 1 per AZ (or None for cost savings)
   - **VPC endpoints**: None
3. Click **Create VPC**

### 1.2 Note Your Subnet IDs

After creation, note down:
- Public Subnet 1 ID (e.g., `subnet-xxxxx`)
- Public Subnet 2 ID (e.g., `subnet-yyyyy`)
- Private Subnet 1 ID
- Private Subnet 2 ID

---

## 2. Create Security Groups

### 2.1 Create NLB Security Group

1. Navigate to **VPC Console** → **Security Groups** → **Create security group**
2. Configure:
   - **Security group name**: `shield-demo-nlb-sg`
   - **Description**: Security group for Network Load Balancer
   - **VPC**: Select `shield-demo-vpc`
3. **Inbound rules** → **Add rule**:
   | Type | Port Range | Source | Description |
   |------|------------|--------|-------------|
   | HTTP | 80 | 0.0.0.0/0 | Allow HTTP from internet |
   | HTTPS | 443 | 0.0.0.0/0 | Allow HTTPS from internet |
4. Click **Create security group**

### 2.2 Create EC2 Security Group

1. **Create security group**
2. Configure:
   - **Security group name**: `shield-demo-ec2-sg`
   - **Description**: Security group for EC2 instances
   - **VPC**: Select `shield-demo-vpc`
3. **Inbound rules** → **Add rule**:
   | Type | Port Range | Source | Description |
   |------|------------|--------|-------------|
   | HTTP | 80 | shield-demo-nlb-sg | Allow from NLB |
   | SSH | 22 | Your IP | SSH access (optional) |
4. Click **Create security group**

---

## 3. Create EC2 Instances

### 3.1 Create Launch Template

1. Navigate to **EC2 Console** → **Launch Templates** → **Create launch template**
2. Configure:
   - **Launch template name**: `shield-demo-template`
   - **Template version description**: Initial version

3. **Application and OS Images**:
   - Select **Amazon Linux 2023 AMI**

4. **Instance type**: `t3.micro`

5. **Key pair**: Select existing or create new

6. **Network settings**:
   - **Security groups**: Select `shield-demo-ec2-sg`

7. **Advanced details** → **User data**:
   ```bash
   #!/bin/bash
   yum update -y
   yum install -y httpd
   systemctl start httpd
   systemctl enable httpd

   # Get instance metadata
   TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
   INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
   AZ=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)

   # Create health check page
   cat > /var/www/html/index.html << EOF
   <!DOCTYPE html>
   <html>
   <head><title>Shield Demo</title></head>
   <body>
   <h1>AWS Shield Layer 4 Demo</h1>
   <p>Instance ID: $INSTANCE_ID</p>
   <p>Availability Zone: $AZ</p>
   <p>Status: Healthy</p>
   </body>
   </html>
   EOF
   ```

8. Click **Create launch template**

### 3.2 Launch Initial Instances (Optional)

You can launch instances manually or skip to Auto Scaling:

1. Select the launch template → **Actions** → **Launch instance from template**
2. **Number of instances**: 2
3. **Subnet**: Select private subnets
4. Click **Launch instance**

---

## 4. Create Network Load Balancer

### 4.1 Create Target Group

1. Navigate to **EC2 Console** → **Target Groups** → **Create target group**
2. Configure:
   - **Target type**: Instances
   - **Target group name**: `shield-demo-tg`
   - **Protocol**: TCP
   - **Port**: 80
   - **VPC**: Select `shield-demo-vpc`

3. **Health checks**:
   - **Health check protocol**: HTTP
   - **Health check path**: `/`
   - **Healthy threshold**: 2
   - **Unhealthy threshold**: 2
   - **Timeout**: 5 seconds
   - **Interval**: 10 seconds

4. Click **Next**
5. **Register targets**: Select your EC2 instances (if created) → **Include as pending below**
6. Click **Create target group**

### 4.2 Create Network Load Balancer

1. Navigate to **EC2 Console** → **Load Balancers** → **Create Load Balancer**
2. Select **Network Load Balancer** → **Create**
3. Configure:
   - **Load balancer name**: `shield-demo-nlb`
   - **Scheme**: Internet-facing
   - **IP address type**: IPv4

4. **Network mapping**:
   - **VPC**: Select `shield-demo-vpc`
   - **Mappings**: Select both public subnets

5. **Listeners and routing**:
   - **Protocol**: TCP
   - **Port**: 80
   - **Default action**: Forward to `shield-demo-tg`

6. Click **Create load balancer**

7. Note the **DNS name** (e.g., `shield-demo-nlb-xxxx.elb.region.amazonaws.com`)

---

## 5. Create Auto Scaling Group

### 5.1 Create Auto Scaling Group

1. Navigate to **EC2 Console** → **Auto Scaling Groups** → **Create Auto Scaling group**

2. **Step 1 - Choose launch template**:
   - **Auto Scaling group name**: `shield-demo-asg`
   - **Launch template**: Select `shield-demo-template`
   - Click **Next**

3. **Step 2 - Choose instance launch options**:
   - **VPC**: Select `shield-demo-vpc`
   - **Availability Zones and subnets**: Select both private subnets
   - Click **Next**

4. **Step 3 - Configure advanced options**:
   - **Load balancing**: Attach to an existing load balancer
   - **Existing load balancer target groups**: Select `shield-demo-tg`
   - **Health checks**: Enable ELB health checks
   - **Health check grace period**: 300 seconds
   - Click **Next**

5. **Step 4 - Configure group size and scaling**:
   - **Desired capacity**: 2
   - **Minimum capacity**: 2
   - **Maximum capacity**: 6

   **Scaling policies**:
   - Select **Target tracking scaling policy**
   - **Metric type**: Average CPU utilization
   - **Target value**: 70
   - Click **Next**

6. **Step 5 - Add notifications** (optional):
   - Skip for now or configure SNS
   - Click **Next**

7. **Step 6 - Add tags**:
   - **Key**: `Name`, **Value**: `shield-demo-instance`
   - Click **Next**

8. **Review** and click **Create Auto Scaling group**

---

## 6. Set Up CloudWatch Monitoring

### 6.1 Create CloudWatch Dashboard

1. Navigate to **CloudWatch Console** → **Dashboards** → **Create dashboard**
2. **Dashboard name**: `shield-demo-dashboard`
3. Click **Create dashboard**

4. **Add widgets**:

#### Widget 1: New Flow Count
- Click **Add widget** → **Line**
- **Metrics** → **NetworkELB** → **Per-LB Metrics**
- Select `NewFlowCount` for your NLB
- **Label**: New Connections/min
- Click **Create widget**

#### Widget 2: Active Flow Count
- Click **Add widget** → **Line**
- Select `ActiveFlowCount` for your NLB
- **Label**: Active Connections
- Click **Create widget**

#### Widget 3: TCP Client Resets
- Click **Add widget** → **Line**
- Select `TCP_Client_Reset_Count` for your NLB
- **Label**: TCP Resets
- Click **Create widget**

#### Widget 4: Processed Bytes
- Click **Add widget** → **Line**
- Select `ProcessedBytes` for your NLB
- **Label**: Data Processed
- Click **Create widget**

5. Click **Save dashboard**

---

## 7. Create SNS Topic for Alerts

### 7.1 Create SNS Topic

1. Navigate to **SNS Console** → **Topics** → **Create topic**
2. Configure:
   - **Type**: Standard
   - **Name**: `shield-demo-alerts`
   - **Display name**: Shield Demo Alerts
3. Click **Create topic**

### 7.2 Create Subscription

1. Select the topic → **Create subscription**
2. Configure:
   - **Protocol**: Email
   - **Endpoint**: Your email address
3. Click **Create subscription**
4. **Confirm** the subscription via the email you receive

---

## 8. Create CloudWatch Alarms

### 8.1 High Connection Rate Alarm

1. Navigate to **CloudWatch Console** → **Alarms** → **Create alarm**
2. Click **Select metric**
3. **NetworkELB** → **Per-LB Metrics** → Select `NewFlowCount` for your NLB
4. Click **Select metric**

5. Configure:
   - **Statistic**: Sum
   - **Period**: 1 minute
   - **Threshold type**: Static
   - **Whenever NewFlowCount is**: Greater than 10000

6. **Notification**:
   - **Alarm state trigger**: In alarm
   - **SNS topic**: Select `shield-demo-alerts`

7. **Name and description**:
   - **Alarm name**: `shield-demo-high-connection-rate`
   - **Description**: Potential DDoS - High connection rate detected

8. Click **Create alarm**

### 8.2 High TCP Reset Alarm

1. **Create alarm** → **Select metric**
2. **NetworkELB** → **Per-LB Metrics** → Select `TCP_Client_Reset_Count`
3. Configure:
   - **Statistic**: Sum
   - **Period**: 1 minute
   - **Threshold**: Greater than 1000

4. **Notification**: Select `shield-demo-alerts`

5. **Name**: `shield-demo-high-tcp-resets`
6. **Description**: Potential SYN flood attack detected

7. Click **Create alarm**

---

## 9. Enable Shield Advanced (Optional)

> **Note**: Shield Advanced costs $3,000/month. Skip this section for testing.

### 9.1 Subscribe to Shield Advanced

1. Navigate to **AWS Shield Console**
2. Click **Get started with Shield Advanced**
3. Review pricing and click **Subscribe to Shield Advanced**
4. Acknowledge the commitment and click **Subscribe**

### 9.2 Add Protected Resources

1. In Shield Console → **Protected resources** → **Add resources to protect**
2. Select resource types:
   - **Elastic Load Balancers**: Select your NLB
3. Click **Protect with Shield Advanced**

### 9.3 Configure DRT Access (Optional)

1. **Settings** → **Configure AWS DRT access**
2. Create an IAM role for DRT team access
3. This allows AWS DDoS Response Team to help during attacks

---

## 10. Verification

### 10.1 Test the Application

1. Get NLB DNS name from **EC2 Console** → **Load Balancers**
2. Open in browser: `http://shield-demo-nlb-xxxx.elb.region.amazonaws.com`
3. You should see the demo page with instance information

### 10.2 Verify Shield Protection

1. Navigate to **AWS Shield Console**
2. Under **Overview**, confirm Shield Standard is active
3. Your NLB is automatically protected by Shield Standard

### 10.3 Check CloudWatch Dashboard

1. Navigate to **CloudWatch Console** → **Dashboards**
2. Open `shield-demo-dashboard`
3. Verify metrics are being collected

### 10.4 Test Alarms (Optional)

1. Generate some traffic to your NLB:
   ```bash
   NLB_DNS="your-nlb-dns-name"
   for i in {1..100}; do curl -s http://$NLB_DNS > /dev/null; done
   ```
2. Monitor the CloudWatch dashboard for activity

---

## 11. Cleanup

To avoid ongoing charges, delete resources in this order:

### 11.1 Delete Auto Scaling Group
1. **EC2 Console** → **Auto Scaling Groups**
2. Select `shield-demo-asg` → **Delete**
3. Confirm deletion

### 11.2 Delete Load Balancer
1. **EC2 Console** → **Load Balancers**
2. Select `shield-demo-nlb` → **Actions** → **Delete**
3. Confirm deletion

### 11.3 Delete Target Group
1. **EC2 Console** → **Target Groups**
2. Select `shield-demo-tg` → **Actions** → **Delete**

### 11.4 Delete Launch Template
1. **EC2 Console** → **Launch Templates**
2. Select `shield-demo-template` → **Actions** → **Delete template**

### 11.5 Delete EC2 Instances (if any remain)
1. **EC2 Console** → **Instances**
2. Select any remaining instances → **Instance state** → **Terminate**

### 11.6 Delete CloudWatch Resources
1. **CloudWatch Console** → **Alarms** → Delete alarms
2. **Dashboards** → Delete `shield-demo-dashboard`

### 11.7 Delete SNS Topic
1. **SNS Console** → **Topics**
2. Select `shield-demo-alerts` → **Delete**

### 11.8 Delete Security Groups
1. **VPC Console** → **Security Groups**
2. Delete `shield-demo-ec2-sg` and `shield-demo-nlb-sg`

### 11.9 Delete VPC
1. **VPC Console** → **Your VPCs**
2. Select `shield-demo-vpc` → **Actions** → **Delete VPC**
3. This will delete associated subnets, route tables, and internet gateway

### 11.10 Unsubscribe from Shield Advanced (if enabled)
1. **AWS Shield Console** → **Overview**
2. Click **Unsubscribe** (requires AWS Support for commitment removal)

---

## Cost Summary

| Component | Monthly Cost |
|-----------|-------------|
| Shield Standard | Free |
| Network Load Balancer | ~$20 + data |
| EC2 (2x t3.micro) | ~$15 |
| NAT Gateway (if used) | ~$32 + data |
| CloudWatch | ~$3 |
| **Total (Standard)** | **~$70/month** |
| Shield Advanced (optional) | +$3,000/month |

---

## Troubleshooting

### Instances Not Healthy in Target Group
1. Check security group allows traffic from NLB on port 80
2. Verify httpd service is running on instances
3. Check instance can reach the internet (for package installation)

### No Metrics in CloudWatch
1. Wait 5-10 minutes for metrics to appear
2. Verify NLB is receiving traffic
3. Check correct metric namespace (AWS/NetworkELB)

### Alarms Not Triggering
1. Verify SNS subscription is confirmed
2. Check alarm threshold values
3. Review alarm history in CloudWatch

---

## Additional Resources

- [AWS Shield Documentation](https://docs.aws.amazon.com/waf/latest/developerguide/shield-chapter.html)
- [Network Load Balancer User Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/)
- [CloudWatch User Guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/)
- [Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/ec2/userguide/)