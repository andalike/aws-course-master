# Project 2: Deploy a Scalable Web Application

## Project Overview

Deploy a highly available, scalable web application using EC2, RDS, Application Load Balancer, and Auto Scaling. This project covers the core architecture patterns for running production workloads on AWS.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           VPC (10.0.0.0/16)                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      INTERNET GATEWAY                                    │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    APPLICATION LOAD BALANCER                             │   │
│  │                    (Public - Multi-AZ)                                   │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│     Availability Zone 1           │          Availability Zone 2                │
│  ┌────────────────────────┐      │       ┌────────────────────────┐            │
│  │   PUBLIC SUBNET        │      │       │   PUBLIC SUBNET        │            │
│  │   10.0.1.0/24          │      │       │   10.0.2.0/24          │            │
│  │ ┌──────────────────┐   │      │       │ ┌──────────────────┐   │            │
│  │ │   NAT Gateway    │   │◄─────┴──────►│ │   NAT Gateway    │   │            │
│  │ └──────────────────┘   │              │ └──────────────────┘   │            │
│  └────────────┬───────────┘              └────────────┬───────────┘            │
│               │                                       │                         │
│  ┌────────────▼───────────┐              ┌────────────▼───────────┐            │
│  │   PRIVATE SUBNET       │              │   PRIVATE SUBNET       │            │
│  │   10.0.3.0/24          │              │   10.0.4.0/24          │            │
│  │ ┌────────────────────┐ │              │ ┌────────────────────┐ │            │
│  │ │  ┌──────┐ ┌──────┐ │ │              │ │  ┌──────┐ ┌──────┐ │ │            │
│  │ │  │ EC2  │ │ EC2  │ │ │◄─Auto──────►│ │  │ EC2  │ │ EC2  │ │ │            │
│  │ │  │      │ │      │ │ │  Scaling     │ │  │      │ │      │ │ │            │
│  │ │  └──────┘ └──────┘ │ │              │ │  └──────┘ └──────┘ │ │            │
│  │ └────────────────────┘ │              │ └────────────────────┘ │            │
│  └────────────┬───────────┘              └────────────┬───────────┘            │
│               │                                       │                         │
│  ┌────────────▼───────────┐              ┌────────────▼───────────┐            │
│  │   DATABASE SUBNET      │              │   DATABASE SUBNET      │            │
│  │   10.0.5.0/24          │              │   10.0.6.0/24          │            │
│  │ ┌────────────────────┐ │              │ ┌────────────────────┐ │            │
│  │ │     RDS MySQL      │ │◄──Multi-AZ──►│ │   RDS Standby      │ │            │
│  │ │     (Primary)      │ │   Sync       │ │    (Standby)       │ │            │
│  │ └────────────────────┘ │              │ └────────────────────┘ │            │
│  └────────────────────────┘              └────────────────────────┘            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Learning Objectives

By completing this project, you will:

- [ ] Create a multi-AZ VPC with public and private subnets
- [ ] Launch EC2 instances with proper security groups
- [ ] Set up Application Load Balancer with health checks
- [ ] Configure Auto Scaling for high availability
- [ ] Deploy RDS MySQL with Multi-AZ
- [ ] Implement proper IAM roles for EC2
- [ ] Use Systems Manager Parameter Store for configuration

---

## Prerequisites

- Completed Modules 1-6 of this course
- AWS Account with Free Tier access
- SSH key pair created
- Basic Linux command line knowledge

---

## Estimated Time

| Phase | Time |
|-------|------|
| VPC Setup | 45 minutes |
| RDS Configuration | 30 minutes |
| EC2 & ALB Setup | 60 minutes |
| Auto Scaling | 45 minutes |
| Testing | 30 minutes |
| **Total** | **~3.5 hours** |

---

## Step 1: Create VPC Infrastructure

### VPC and Subnets

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=webapp-vpc}]' \
    --query 'Vpc.VpcId' \
    --output text)

echo "VPC ID: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=webapp-igw}]' \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

aws ec2 attach-internet-gateway \
    --vpc-id $VPC_ID \
    --internet-gateway-id $IGW_ID

# Create Public Subnets
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1}]' \
    --query 'Subnet.SubnetId' \
    --output text)

PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-2}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Create Private Subnets (for EC2)
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1}]' \
    --query 'Subnet.SubnetId' \
    --output text)

PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.4.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-2}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Create Database Subnets
DB_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.5.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=db-subnet-1}]' \
    --query 'Subnet.SubnetId' \
    --output text)

DB_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.6.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=db-subnet-2}]' \
    --query 'Subnet.SubnetId' \
    --output text)

echo "Subnets created successfully"
```

### NAT Gateways and Route Tables

```bash
# Allocate Elastic IPs for NAT Gateways
EIP_1=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
EIP_2=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)

# Create NAT Gateways
NAT_1=$(aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_1 \
    --allocation-id $EIP_1 \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=nat-gateway-1}]' \
    --query 'NatGateway.NatGatewayId' \
    --output text)

NAT_2=$(aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_2 \
    --allocation-id $EIP_2 \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=nat-gateway-2}]' \
    --query 'NatGateway.NatGatewayId' \
    --output text)

echo "Waiting for NAT Gateways to become available..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_1 $NAT_2

# Create Route Tables
# Public Route Table
PUBLIC_RT=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --route-table-id $PUBLIC_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_2

# Private Route Tables
PRIVATE_RT_1=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-rt-1}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --route-table-id $PRIVATE_RT_1 \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_1

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1 --subnet-id $PRIVATE_SUBNET_1
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1 --subnet-id $DB_SUBNET_1

PRIVATE_RT_2=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-rt-2}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --route-table-id $PRIVATE_RT_2 \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_2

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_2 --subnet-id $PRIVATE_SUBNET_2
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_2 --subnet-id $DB_SUBNET_2

echo "Route tables configured"
```

---

## Step 2: Create Security Groups

```bash
# ALB Security Group
ALB_SG=$(aws ec2 create-security-group \
    --group-name alb-sg \
    --description "Security group for ALB" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# EC2 Security Group
EC2_SG=$(aws ec2 create-security-group \
    --group-name ec2-sg \
    --description "Security group for EC2 instances" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $EC2_SG \
    --protocol tcp \
    --port 80 \
    --source-group $ALB_SG

# RDS Security Group
RDS_SG=$(aws ec2 create-security-group \
    --group-name rds-sg \
    --description "Security group for RDS" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG \
    --protocol tcp \
    --port 3306 \
    --source-group $EC2_SG

echo "Security Groups created"
echo "ALB SG: $ALB_SG"
echo "EC2 SG: $EC2_SG"
echo "RDS SG: $RDS_SG"
```

---

## Step 3: Create RDS MySQL Database

```bash
# Create DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name webapp-db-subnet \
    --db-subnet-group-description "Subnet group for webapp RDS" \
    --subnet-ids $DB_SUBNET_1 $DB_SUBNET_2

# Store database password in Secrets Manager
aws secretsmanager create-secret \
    --name webapp/db-password \
    --secret-string '{"username":"admin","password":"YourSecurePassword123!"}'

# Create RDS Instance
aws rds create-db-instance \
    --db-instance-identifier webapp-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --engine-version 8.0 \
    --master-username admin \
    --master-user-password "YourSecurePassword123!" \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids $RDS_SG \
    --db-subnet-group-name webapp-db-subnet \
    --multi-az \
    --backup-retention-period 7 \
    --no-publicly-accessible \
    --db-name webappdb

echo "Waiting for RDS instance to be available (this takes 10-15 minutes)..."
aws rds wait db-instance-available --db-instance-identifier webapp-db

# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier webapp-db \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"

# Store endpoint in Parameter Store
aws ssm put-parameter \
    --name "/webapp/db-endpoint" \
    --type String \
    --value $RDS_ENDPOINT
```

---

## Step 4: Create IAM Role for EC2

```bash
# Create trust policy
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create IAM Role
aws iam create-role \
    --role-name webapp-ec2-role \
    --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
    --role-name webapp-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

aws iam attach-role-policy \
    --role-name webapp-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name webapp-ec2-profile

aws iam add-role-to-instance-profile \
    --instance-profile-name webapp-ec2-profile \
    --role-name webapp-ec2-role

# Wait for profile to be available
sleep 10
```

---

## Step 5: Create Application Load Balancer

```bash
# Create ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name webapp-alb \
    --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
    --security-groups $ALB_SG \
    --scheme internet-facing \
    --type application \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

# Create Target Group
TG_ARN=$(aws elbv2 create-target-group \
    --name webapp-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --target-type instance \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

# Create Listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Get ALB DNS Name
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

echo "ALB DNS: $ALB_DNS"
```

---

## Step 6: Create Launch Template and Auto Scaling Group

### User Data Script

```bash
cat > user-data.sh << 'USERDATA'
#!/bin/bash
yum update -y
yum install -y httpd php php-mysqlnd

# Start Apache
systemctl start httpd
systemctl enable httpd

# Get DB endpoint from Parameter Store
DB_ENDPOINT=$(aws ssm get-parameter --name "/webapp/db-endpoint" --region us-east-1 --query 'Parameter.Value' --output text)

# Create index.php
cat > /var/www/html/index.php << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>AWS Web Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #232f3e; }
        .info { background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .success { color: #2e7d32; }
        .error { color: #c62828; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AWS Web Application</h1>
        <div class="info">
            <strong>Instance ID:</strong> <?php echo file_get_contents('http://169.254.169.254/latest/meta-data/instance-id'); ?><br>
            <strong>Availability Zone:</strong> <?php echo file_get_contents('http://169.254.169.254/latest/meta-data/placement/availability-zone'); ?><br>
            <strong>Private IP:</strong> <?php echo file_get_contents('http://169.254.169.254/latest/meta-data/local-ipv4'); ?>
        </div>
        <h2>Database Connection Test</h2>
        <?php
        $db_endpoint = getenv('DB_ENDPOINT') ?: 'localhost';
        $conn = @new mysqli($db_endpoint, 'admin', 'YourSecurePassword123!', 'webappdb');
        if ($conn->connect_error) {
            echo "<p class='error'>Database connection failed: " . $conn->connect_error . "</p>";
        } else {
            echo "<p class='success'>Database connection successful!</p>";
            $conn->close();
        }
        ?>
        <h2>Server Time</h2>
        <p><?php echo date('Y-m-d H:i:s'); ?></p>
    </div>
</body>
</html>
EOF

# Create health check endpoint
cat > /var/www/html/health << 'EOF'
OK
EOF

# Set permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

echo "Setup complete"
USERDATA

# Encode user data
USER_DATA_BASE64=$(base64 -i user-data.sh)
```

### Launch Template

```bash
# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

# Create Launch Template
aws ec2 create-launch-template \
    --launch-template-name webapp-lt \
    --version-description "Initial version" \
    --launch-template-data "{
        \"ImageId\": \"$AMI_ID\",
        \"InstanceType\": \"t2.micro\",
        \"IamInstanceProfile\": {
            \"Name\": \"webapp-ec2-profile\"
        },
        \"SecurityGroupIds\": [\"$EC2_SG\"],
        \"UserData\": \"$USER_DATA_BASE64\",
        \"TagSpecifications\": [
            {
                \"ResourceType\": \"instance\",
                \"Tags\": [
                    {\"Key\": \"Name\", \"Value\": \"webapp-instance\"}
                ]
            }
        ]
    }"
```

### Auto Scaling Group

```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name webapp-asg \
    --launch-template LaunchTemplateName=webapp-lt,Version='$Latest' \
    --min-size 2 \
    --max-size 6 \
    --desired-capacity 2 \
    --vpc-zone-identifier "$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2" \
    --target-group-arns $TG_ARN \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --tags Key=Name,Value=webapp-asg-instance,PropagateAtLaunch=true

# Create Scaling Policies
# Scale Up Policy
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name webapp-asg \
    --policy-name scale-up \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
    }'

echo "Auto Scaling Group created"
```

---

## Step 7: Testing

### Verify Deployment

```bash
# Check Auto Scaling Group instances
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names webapp-asg \
    --query 'AutoScalingGroups[0].Instances'

# Check Target Group health
aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN

# Test the application
echo "Application URL: http://$ALB_DNS"
curl http://$ALB_DNS
```

### Load Testing

```bash
# Install Apache Bench
# On macOS: Already installed
# On Linux: sudo yum install httpd-tools

# Run load test
ab -n 1000 -c 100 http://$ALB_DNS/

# Watch Auto Scaling
watch -n 5 'aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names webapp-asg \
    --query "AutoScalingGroups[0].{Desired:DesiredCapacity,Running:Instances|length(@)}"'
```

---

## Cost Breakdown

| Service | Monthly Cost (Estimate) |
|---------|------------------------|
| EC2 t2.micro x 2 | Free Tier / ~$17 |
| RDS db.t3.micro Multi-AZ | Free Tier / ~$25 |
| NAT Gateway x 2 | ~$65 |
| ALB | ~$22 |
| Data Transfer | Variable |
| **Total** | **~$130/month** |

> **Note**: For learning, you can use single NAT Gateway to reduce costs

---

## Cleanup

```bash
# Delete in reverse order of dependencies

# 1. Delete Auto Scaling Group
aws autoscaling delete-auto-scaling-group \
    --auto-scaling-group-name webapp-asg \
    --force-delete

# 2. Delete Launch Template
aws ec2 delete-launch-template --launch-template-name webapp-lt

# 3. Delete Load Balancer
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# 4. Delete RDS
aws rds delete-db-instance \
    --db-instance-identifier webapp-db \
    --skip-final-snapshot

# 5. Delete NAT Gateways
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_1
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_2

# 6. Release Elastic IPs (after NAT Gateways are deleted)
aws ec2 release-address --allocation-id $EIP_1
aws ec2 release-address --allocation-id $EIP_2

# 7. Delete Subnets, Route Tables, Security Groups, IGW, VPC
# (Use console for easier cleanup or script the deletion)
```

---

## Verification Checklist

- [ ] VPC with proper CIDR blocks
- [ ] All subnets created across 2 AZs
- [ ] Internet Gateway attached
- [ ] NAT Gateways in public subnets
- [ ] Route tables properly configured
- [ ] Security groups with correct rules
- [ ] RDS Multi-AZ deployment running
- [ ] Launch template created
- [ ] Auto Scaling Group with 2+ instances
- [ ] ALB distributing traffic
- [ ] Health checks passing
- [ ] Application accessible via ALB DNS

---

**Congratulations!** You've deployed a production-ready, highly available web application!

[← Back to Projects](../) | [Previous: Static Website](../01-static-website/) | [Next: Serverless API →](../03-serverless-api/)
