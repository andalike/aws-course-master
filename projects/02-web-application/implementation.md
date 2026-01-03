# 3-Tier Web Application on AWS - Complete Implementation Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [VPC and Networking Setup](#vpc-and-networking-setup)
4. [Database Tier (RDS)](#database-tier-rds)
5. [Application Tier (EC2 + Auto Scaling)](#application-tier-ec2--auto-scaling)
6. [Load Balancer Configuration](#load-balancer-configuration)
7. [Security Configuration](#security-configuration)
8. [Complete CloudFormation Template](#complete-cloudformation-template)
9. [Deployment Scripts](#deployment-scripts)
10. [Application Code](#application-code)
11. [Monitoring and Logging](#monitoring-and-logging)
12. [Cost Analysis](#cost-analysis)
13. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
                            3-TIER WEB APPLICATION ARCHITECTURE
    ===========================================================================================

                                    INTERNET
                                        |
                                        v
                              +------------------+
                              |   Route 53       |
                              |   (DNS)          |
                              +--------+---------+
                                       |
                              +--------v---------+
                              |    Internet      |
                              |    Gateway       |
                              +--------+---------+
                                       |
    +----------------------------------+----------------------------------+
    |                              VPC (10.0.0.0/16)                      |
    |                                                                      |
    |  +------------------+     +------------------+                       |
    |  | Public Subnet    |     | Public Subnet    |                       |
    |  | AZ-a (10.0.1.0)  |     | AZ-b (10.0.2.0)  |                       |
    |  |                  |     |                  |                       |
    |  |  +------------+  |     |  +------------+  |                       |
    |  |  | NAT GW     |  |     |  | NAT GW     |  |                       |
    |  |  +------------+  |     |  +------------+  |                       |
    |  |                  |     |                  |                       |
    |  +--------+---------+     +--------+---------+                       |
    |           |                        |                                 |
    |           +----------+  +----------+                                 |
    |                      |  |                                            |
    |              +-------v--v-------+                                    |
    |              | Application      |                                    |
    |              | Load Balancer    |                                    |
    |              +-------+--+-------+                                    |
    |                      |  |                                            |
    |  +-------------------+  +-------------------+                        |
    |  |                                          |                        |
    |  v                                          v                        |
    |  +------------------+     +------------------+                       |
    |  | Private Subnet   |     | Private Subnet   |                       |
    |  | AZ-a (10.0.3.0)  |     | AZ-b (10.0.4.0)  |                       |
    |  |                  |     |                  |                       |
    |  | +-------------+  |     | +-------------+  |  <-- Auto Scaling    |
    |  | | EC2 (App)   |  |     | | EC2 (App)   |  |      Group           |
    |  | +-------------+  |     | +-------------+  |                       |
    |  |                  |     |                  |                       |
    |  +--------+---------+     +--------+---------+                       |
    |           |                        |                                 |
    |           +----------+  +----------+                                 |
    |                      |  |                                            |
    |  +------------------+|  |+------------------+                        |
    |  | DB Subnet        ||  || DB Subnet        |                        |
    |  | AZ-a (10.0.5.0)  |v  v| AZ-b (10.0.6.0)  |                        |
    |  |                  |    |                  |                        |
    |  | +-------------+  |    | +-------------+  |                        |
    |  | | RDS Primary |<-+--->| | RDS Standby |  |  <-- Multi-AZ         |
    |  | | (MySQL)     |  |    | | (MySQL)     |  |                        |
    |  | +-------------+  |    | +-------------+  |                        |
    |  |                  |    |                  |                        |
    |  +------------------+    +------------------+                        |
    |                                                                      |
    +----------------------------------------------------------------------+

    COMPONENTS:
    +------------------+-----------------------------------------------+
    | VPC              | Isolated network with public/private subnets  |
    | ALB              | Distributes traffic across EC2 instances      |
    | EC2 Auto Scaling | Automatically scales application tier         |
    | RDS MySQL        | Managed database with Multi-AZ deployment     |
    | NAT Gateway      | Enables outbound internet for private subnets |
    | Security Groups  | Virtual firewalls for each tier               |
    +------------------+-----------------------------------------------+
```

---

## Prerequisites

### Required Tools

```bash
# AWS CLI v2
aws --version

# Verify credentials
aws sts get-caller-identity

# Required IAM permissions:
# - VPC: Full access
# - EC2: Full access
# - RDS: Full access
# - ELB: Full access
# - IAM: PassRole, CreateRole
# - CloudWatch: Full access
```

### Environment Variables

```bash
export AWS_REGION="us-east-1"
export PROJECT_NAME="webapp"
export KEY_PAIR_NAME="webapp-key"
export DB_USERNAME="admin"
export DB_PASSWORD="YourSecurePassword123!"  # Use Secrets Manager in production
```

---

## VPC and Networking Setup

### Create VPC Infrastructure

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value='${PROJECT_NAME}'-vpc}]' \
    --query 'Vpc.VpcId' \
    --output text)

echo "VPC ID: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value='${PROJECT_NAME}'-igw}]' \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

# Attach IGW to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID
```

### Create Subnets

```bash
# Public Subnet 1 (AZ-a)
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone ${AWS_REGION}a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='${PROJECT_NAME}'-public-1}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Public Subnet 2 (AZ-b)
PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone ${AWS_REGION}b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='${PROJECT_NAME}'-public-2}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Private Subnet 1 (AZ-a) - Application Tier
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone ${AWS_REGION}a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='${PROJECT_NAME}'-private-1}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Private Subnet 2 (AZ-b) - Application Tier
PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.4.0/24 \
    --availability-zone ${AWS_REGION}b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='${PROJECT_NAME}'-private-2}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Database Subnet 1 (AZ-a)
DB_SUBNET_1=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.5.0/24 \
    --availability-zone ${AWS_REGION}a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='${PROJECT_NAME}'-db-1}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Database Subnet 2 (AZ-b)
DB_SUBNET_2=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.6.0/24 \
    --availability-zone ${AWS_REGION}b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value='${PROJECT_NAME}'-db-2}]' \
    --query 'Subnet.SubnetId' \
    --output text)

echo "Subnets created successfully"
```

### Create NAT Gateways

```bash
# Allocate Elastic IP for NAT Gateway 1
EIP_1=$(aws ec2 allocate-address \
    --domain vpc \
    --query 'AllocationId' \
    --output text)

# Create NAT Gateway in Public Subnet 1
NAT_GW_1=$(aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_1 \
    --allocation-id $EIP_1 \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value='${PROJECT_NAME}'-nat-1}]' \
    --query 'NatGateway.NatGatewayId' \
    --output text)

echo "Waiting for NAT Gateway to become available..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_1

# For production, create a second NAT Gateway in AZ-b
EIP_2=$(aws ec2 allocate-address \
    --domain vpc \
    --query 'AllocationId' \
    --output text)

NAT_GW_2=$(aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_2 \
    --allocation-id $EIP_2 \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value='${PROJECT_NAME}'-nat-2}]' \
    --query 'NatGateway.NatGatewayId' \
    --output text)

aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_2
```

### Configure Route Tables

```bash
# Public Route Table
PUBLIC_RT=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value='${PROJECT_NAME}'-public-rt}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $PUBLIC_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate public subnets
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_2

# Enable auto-assign public IP for public subnets
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_1 --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_2 --map-public-ip-on-launch

# Private Route Table 1 (for AZ-a)
PRIVATE_RT_1=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value='${PROJECT_NAME}'-private-rt-1}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --route-table-id $PRIVATE_RT_1 \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_GW_1

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1 --subnet-id $PRIVATE_SUBNET_1
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1 --subnet-id $DB_SUBNET_1

# Private Route Table 2 (for AZ-b)
PRIVATE_RT_2=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value='${PROJECT_NAME}'-private-rt-2}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --route-table-id $PRIVATE_RT_2 \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_GW_2

aws ec2 associate-route-table --route-table-id $PRIVATE_RT_2 --subnet-id $PRIVATE_SUBNET_2
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_2 --subnet-id $DB_SUBNET_2
```

---

## Database Tier (RDS)

### Create Security Group for RDS

```bash
# RDS Security Group
RDS_SG=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-rds-sg \
    --description "Security group for RDS MySQL" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Tag the security group
aws ec2 create-tags \
    --resources $RDS_SG \
    --tags Key=Name,Value=${PROJECT_NAME}-rds-sg
```

### Create DB Subnet Group

```bash
# Create DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name ${PROJECT_NAME}-db-subnet-group \
    --db-subnet-group-description "Subnet group for RDS" \
    --subnet-ids $DB_SUBNET_1 $DB_SUBNET_2
```

### Create RDS Parameter Group

```bash
# Create custom parameter group
aws rds create-db-parameter-group \
    --db-parameter-group-name ${PROJECT_NAME}-mysql-params \
    --db-parameter-group-family mysql8.0 \
    --description "Custom parameters for MySQL 8.0"

# Set custom parameters
aws rds modify-db-parameter-group \
    --db-parameter-group-name ${PROJECT_NAME}-mysql-params \
    --parameters \
        "ParameterName=max_connections,ParameterValue=200,ApplyMethod=pending-reboot" \
        "ParameterName=slow_query_log,ParameterValue=1,ApplyMethod=pending-reboot" \
        "ParameterName=long_query_time,ParameterValue=2,ApplyMethod=pending-reboot"
```

### Create RDS Instance

```bash
# Create RDS MySQL instance
aws rds create-db-instance \
    --db-instance-identifier ${PROJECT_NAME}-mysql \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --engine-version 8.0 \
    --master-username $DB_USERNAME \
    --master-user-password $DB_PASSWORD \
    --allocated-storage 20 \
    --max-allocated-storage 100 \
    --storage-type gp3 \
    --db-subnet-group-name ${PROJECT_NAME}-db-subnet-group \
    --vpc-security-group-ids $RDS_SG \
    --db-parameter-group-name ${PROJECT_NAME}-mysql-params \
    --db-name webapp \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "Mon:04:00-Mon:05:00" \
    --multi-az \
    --storage-encrypted \
    --enable-cloudwatch-logs-exports '["error","slowquery"]' \
    --deletion-protection \
    --no-publicly-accessible \
    --tags Key=Name,Value=${PROJECT_NAME}-mysql

echo "Waiting for RDS instance to become available (this may take 10-15 minutes)..."
aws rds wait db-instance-available --db-instance-identifier ${PROJECT_NAME}-mysql

# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier ${PROJECT_NAME}-mysql \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"
```

---

## Application Tier (EC2 + Auto Scaling)

### Create Security Groups

```bash
# ALB Security Group
ALB_SG=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-alb-sg \
    --description "Security group for Application Load Balancer" \
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

aws ec2 create-tags --resources $ALB_SG --tags Key=Name,Value=${PROJECT_NAME}-alb-sg

# EC2 Application Security Group
APP_SG=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-app-sg \
    --description "Security group for Application EC2 instances" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow HTTP from ALB only
aws ec2 authorize-security-group-ingress \
    --group-id $APP_SG \
    --protocol tcp \
    --port 80 \
    --source-group $ALB_SG

# Allow SSH from bastion/VPN (optional - use Session Manager instead)
# aws ec2 authorize-security-group-ingress \
#     --group-id $APP_SG \
#     --protocol tcp \
#     --port 22 \
#     --cidr 10.0.0.0/16

aws ec2 create-tags --resources $APP_SG --tags Key=Name,Value=${PROJECT_NAME}-app-sg

# Update RDS Security Group to allow from App tier
aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG \
    --protocol tcp \
    --port 3306 \
    --source-group $APP_SG
```

### Create IAM Role for EC2

```bash
# Create trust policy
cat > ec2-trust-policy.json << 'EOF'
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

# Create IAM role
aws iam create-role \
    --role-name ${PROJECT_NAME}-ec2-role \
    --assume-role-policy-document file://ec2-trust-policy.json

# Attach managed policies
aws iam attach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

aws iam attach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Create custom policy for Secrets Manager access
cat > secrets-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:${AWS_REGION}:*:secret:${PROJECT_NAME}/*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-name ${PROJECT_NAME}-secrets-access \
    --policy-document file://secrets-policy.json

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-ec2-profile

aws iam add-role-to-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-ec2-profile \
    --role-name ${PROJECT_NAME}-ec2-role
```

### Create Launch Template

```bash
# Get latest Amazon Linux 2023 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters \
        "Name=name,Values=al2023-ami-2023*-x86_64" \
        "Name=state,Values=available" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

echo "Using AMI: $AMI_ID"

# Create user data script
cat > user-data.sh << 'EOF'
#!/bin/bash
set -e

# Update system
dnf update -y

# Install required packages
dnf install -y nginx python3 python3-pip mysql

# Install Python dependencies
pip3 install flask gunicorn pymysql boto3

# Create application directory
mkdir -p /opt/webapp
cd /opt/webapp

# Create Flask application
cat > app.py << 'APPEOF'
from flask import Flask, jsonify, request
import pymysql
import os
import boto3
from botocore.exceptions import ClientError
import json

app = Flask(__name__)

def get_db_credentials():
    """Retrieve database credentials from Secrets Manager"""
    secret_name = os.environ.get('DB_SECRET_NAME', 'webapp/db-credentials')
    region_name = os.environ.get('AWS_REGION', 'us-east-1')

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError:
        # Fallback to environment variables
        return {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'username': os.environ.get('DB_USER', 'admin'),
            'password': os.environ.get('DB_PASS', ''),
            'database': os.environ.get('DB_NAME', 'webapp')
        }

def get_db_connection():
    """Create database connection"""
    creds = get_db_credentials()
    return pymysql.connect(
        host=creds['host'],
        user=creds['username'],
        password=creds['password'],
        database=creds.get('database', 'webapp'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AWS 3-Tier Web Application</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #232f3e; }
            .info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .success { color: #1d8102; }
            .btn { background: #ff9900; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #ec7211; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AWS 3-Tier Web Application</h1>
            <p class="success">Application is running successfully!</p>
            <div class="info">
                <strong>Instance ID:</strong> <span id="instance-id">Loading...</span><br>
                <strong>Availability Zone:</strong> <span id="az">Loading...</span>
            </div>
            <h2>API Endpoints</h2>
            <ul>
                <li><a href="/api/health">Health Check</a></li>
                <li><a href="/api/info">Instance Info</a></li>
                <li><a href="/api/db-status">Database Status</a></li>
            </ul>
        </div>
        <script>
            fetch('/api/info')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('instance-id').textContent = d.instance_id;
                    document.getElementById('az').textContent = d.availability_zone;
                });
        </script>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'webapp'})

@app.route('/api/info')
def info():
    import urllib.request
    try:
        token = urllib.request.urlopen(urllib.request.Request(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
            method='PUT'
        )).read().decode()

        instance_id = urllib.request.urlopen(urllib.request.Request(
            'http://169.254.169.254/latest/meta-data/instance-id',
            headers={'X-aws-ec2-metadata-token': token}
        )).read().decode()

        az = urllib.request.urlopen(urllib.request.Request(
            'http://169.254.169.254/latest/meta-data/placement/availability-zone',
            headers={'X-aws-ec2-metadata-token': token}
        )).read().decode()

        return jsonify({
            'instance_id': instance_id,
            'availability_zone': az,
            'region': az[:-1]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/db-status')
def db_status():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()
            cursor.execute('SELECT NOW()')
            now = cursor.fetchone()
        conn.close()
        return jsonify({
            'status': 'connected',
            'mysql_version': version['VERSION()'],
            'server_time': str(now['NOW()'])
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/items', methods=['GET', 'POST'])
def items():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if request.method == 'POST':
                data = request.json
                cursor.execute(
                    'INSERT INTO items (name, description) VALUES (%s, %s)',
                    (data['name'], data.get('description', ''))
                )
                conn.commit()
                return jsonify({'status': 'created', 'id': cursor.lastrowid}), 201
            else:
                cursor.execute('SELECT * FROM items ORDER BY created_at DESC LIMIT 100')
                return jsonify(cursor.fetchall())
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
APPEOF

# Create systemd service for Gunicorn
cat > /etc/systemd/system/webapp.service << 'SVCEOF'
[Unit]
Description=Gunicorn instance for webapp
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/webapp
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SVCEOF

# Configure Nginx as reverse proxy
cat > /etc/nginx/conf.d/webapp.conf << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        return 200 'healthy\n';
        add_header Content-Type text/plain;
    }
}
NGINXEOF

# Remove default nginx config
rm -f /etc/nginx/conf.d/default.conf

# Set ownership
chown -R ec2-user:ec2-user /opt/webapp

# Start services
systemctl daemon-reload
systemctl enable nginx webapp
systemctl start nginx webapp

echo "Application deployment complete!"
EOF

# Base64 encode user data
USER_DATA=$(base64 -i user-data.sh)

# Create launch template
aws ec2 create-launch-template \
    --launch-template-name ${PROJECT_NAME}-launch-template \
    --version-description "Initial version" \
    --launch-template-data '{
        "ImageId": "'$AMI_ID'",
        "InstanceType": "t3.micro",
        "IamInstanceProfile": {
            "Name": "'${PROJECT_NAME}'-ec2-profile"
        },
        "SecurityGroupIds": ["'$APP_SG'"],
        "UserData": "'$USER_DATA'",
        "Monitoring": {
            "Enabled": true
        },
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "'${PROJECT_NAME}'-app"},
                    {"Key": "Environment", "Value": "production"}
                ]
            }
        ],
        "MetadataOptions": {
            "HttpTokens": "required",
            "HttpEndpoint": "enabled"
        }
    }'
```

---

## Load Balancer Configuration

### Create Application Load Balancer

```bash
# Create ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
    --name ${PROJECT_NAME}-alb \
    --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
    --security-groups $ALB_SG \
    --scheme internet-facing \
    --type application \
    --ip-address-type ipv4 \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text)

ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

echo "ALB ARN: $ALB_ARN"
echo "ALB DNS: $ALB_DNS"

# Create Target Group
TG_ARN=$(aws elbv2 create-target-group \
    --name ${PROJECT_NAME}-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --health-check-protocol HTTP \
    --health-check-path /api/health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --target-type instance \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

echo "Target Group ARN: $TG_ARN"

# Create HTTP Listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

# For HTTPS (requires ACM certificate)
# aws elbv2 create-listener \
#     --load-balancer-arn $ALB_ARN \
#     --protocol HTTPS \
#     --port 443 \
#     --certificates CertificateArn=$CERT_ARN \
#     --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

### Create Auto Scaling Group

```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name ${PROJECT_NAME}-asg \
    --launch-template LaunchTemplateName=${PROJECT_NAME}-launch-template,Version='$Latest' \
    --min-size 2 \
    --max-size 6 \
    --desired-capacity 2 \
    --target-group-arns $TG_ARN \
    --vpc-zone-identifier "$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2" \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --tags \
        Key=Name,Value=${PROJECT_NAME}-asg-instance,PropagateAtLaunch=true \
        Key=Environment,Value=production,PropagateAtLaunch=true

# Create Target Tracking Scaling Policy
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name ${PROJECT_NAME}-asg \
    --policy-name ${PROJECT_NAME}-cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 70.0,
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
    }'

# Create scaling policy based on request count
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name ${PROJECT_NAME}-asg \
    --policy-name ${PROJECT_NAME}-request-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ALBRequestCountPerTarget",
            "ResourceLabel": "'$(echo $ALB_ARN | cut -d'/' -f2-)'/'$(echo $TG_ARN | cut -d':' -f6)'"
        },
        "TargetValue": 1000.0,
        "ScaleOutCooldown": 300,
        "ScaleInCooldown": 300
    }'
```

---

## Security Configuration

### Security Groups Summary

```
+-------------------+------------------+--------+-----------------+
| Security Group    | Inbound Rules    | Port   | Source          |
+-------------------+------------------+--------+-----------------+
| ALB-SG            | HTTP             | 80     | 0.0.0.0/0       |
|                   | HTTPS            | 443    | 0.0.0.0/0       |
+-------------------+------------------+--------+-----------------+
| APP-SG            | HTTP             | 80     | ALB-SG          |
|                   | (SSH - optional) | 22     | Bastion/VPN     |
+-------------------+------------------+--------+-----------------+
| RDS-SG            | MySQL            | 3306   | APP-SG          |
+-------------------+------------------+--------+-----------------+
```

### Store Database Credentials in Secrets Manager

```bash
# Create secret for database credentials
aws secretsmanager create-secret \
    --name ${PROJECT_NAME}/db-credentials \
    --description "Database credentials for webapp" \
    --secret-string '{
        "host": "'$RDS_ENDPOINT'",
        "username": "'$DB_USERNAME'",
        "password": "'$DB_PASSWORD'",
        "database": "webapp",
        "port": 3306
    }'
```

---

## Complete CloudFormation Template

Save as `3-tier-webapp-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete 3-Tier Web Application Infrastructure'

Parameters:
  ProjectName:
    Type: String
    Default: webapp
    Description: Name prefix for all resources

  EnvironmentType:
    Type: String
    Default: production
    AllowedValues:
      - development
      - staging
      - production

  VpcCidr:
    Type: String
    Default: 10.0.0.0/16

  DBInstanceClass:
    Type: String
    Default: db.t3.micro
    AllowedValues:
      - db.t3.micro
      - db.t3.small
      - db.t3.medium
      - db.r5.large

  DBUsername:
    Type: String
    Default: admin
    NoEcho: true

  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database password (min 8 characters)

  EC2InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large

  MinInstances:
    Type: Number
    Default: 2
    MinValue: 1

  MaxInstances:
    Type: Number
    Default: 6
    MinValue: 2

Mappings:
  RegionAMI:
    us-east-1:
      AMI: ami-0c7217cdde317cfec
    us-west-2:
      AMI: ami-0b20a6f09484773af
    eu-west-1:
      AMI: ami-0905a3c97561e0b69

Resources:
  # ==================== VPC ====================
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-vpc

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-igw

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # ==================== SUBNETS ====================
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [0, !Cidr [!Ref VpcCidr, 8, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-1

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [1, !Cidr [!Ref VpcCidr, 8, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-2

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [2, !Cidr [!Ref VpcCidr, 8, 8]]
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-1

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [3, !Cidr [!Ref VpcCidr, 8, 8]]
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-2

  DBSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [4, !Cidr [!Ref VpcCidr, 8, 8]]
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-db-1

  DBSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [5, !Cidr [!Ref VpcCidr, 8, 8]]
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-db-2

  # ==================== NAT GATEWAY ====================
  NatEIP1:
    Type: AWS::EC2::EIP
    DependsOn: AttachGateway
    Properties:
      Domain: vpc

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatEIP1.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-nat-1

  # ==================== ROUTE TABLES ====================
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-rt

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable

  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-rt

  PrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !Ref PrivateRouteTable

  DBSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref DBSubnet1
      RouteTableId: !Ref PrivateRouteTable

  DBSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref DBSubnet2
      RouteTableId: !Ref PrivateRouteTable

  # ==================== SECURITY GROUPS ====================
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ALB
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-alb-sg

  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for application instances
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-app-sg

  RDSSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-rds-sg

  # ==================== DATABASE ====================
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds:
        - !Ref DBSubnet1
        - !Ref DBSubnet2
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-db-subnet-group

  DBSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub ${ProjectName}/db-credentials
      Description: Database credentials
      SecretString: !Sub |
        {
          "username": "${DBUsername}",
          "password": "${DBPassword}",
          "host": "${RDSInstance.Endpoint.Address}",
          "port": "3306",
          "database": "webapp"
        }

  RDSInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub ${ProjectName}-mysql
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      MaxAllocatedStorage: 100
      StorageType: gp3
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref RDSSecurityGroup
      DBName: webapp
      BackupRetentionPeriod: 7
      MultiAZ: true
      StorageEncrypted: true
      PubliclyAccessible: false
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-mysql

  # ==================== IAM ====================
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub ${ProjectName}-ec2-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Policies:
        - PolicyName: SecretsAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref DBSecret

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub ${ProjectName}-ec2-profile
      Roles:
        - !Ref EC2Role

  # ==================== LOAD BALANCER ====================
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub ${ProjectName}-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-alb

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub ${ProjectName}-tg
      Protocol: HTTP
      Port: 80
      VpcId: !Ref VPC
      HealthCheckPath: /api/health
      HealthCheckIntervalSeconds: 30
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
      TargetType: instance

  HTTPListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Protocol: HTTP
      Port: 80
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup

  # ==================== AUTO SCALING ====================
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub ${ProjectName}-launch-template
      LaunchTemplateData:
        ImageId: !FindInMap [RegionAMI, !Ref 'AWS::Region', AMI]
        InstanceType: !Ref EC2InstanceType
        IamInstanceProfile:
          Name: !Ref EC2InstanceProfile
        SecurityGroupIds:
          - !Ref AppSecurityGroup
        MetadataOptions:
          HttpTokens: required
          HttpEndpoint: enabled
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            set -e
            dnf update -y
            dnf install -y nginx python3 python3-pip mysql
            pip3 install flask gunicorn pymysql boto3

            mkdir -p /opt/webapp
            cat > /opt/webapp/app.py << 'APPEOF'
            from flask import Flask, jsonify
            import pymysql
            import os
            import boto3
            import json

            app = Flask(__name__)

            def get_db_credentials():
                client = boto3.client('secretsmanager', region_name='${AWS::Region}')
                response = client.get_secret_value(SecretId='${DBSecret}')
                return json.loads(response['SecretString'])

            @app.route('/')
            def home():
                return '<h1>AWS 3-Tier Web Application</h1><p>Running on EC2 with RDS backend</p>'

            @app.route('/api/health')
            def health():
                return jsonify({'status': 'healthy'})

            @app.route('/api/db-status')
            def db_status():
                try:
                    creds = get_db_credentials()
                    conn = pymysql.connect(
                        host=creds['host'],
                        user=creds['username'],
                        password=creds['password'],
                        database=creds['database']
                    )
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT VERSION()')
                        version = cursor.fetchone()
                    conn.close()
                    return jsonify({'status': 'connected', 'version': version[0]})
                except Exception as e:
                    return jsonify({'status': 'error', 'message': str(e)}), 500

            if __name__ == '__main__':
                app.run(host='0.0.0.0', port=5000)
            APPEOF

            cat > /etc/systemd/system/webapp.service << 'SVCEOF'
            [Unit]
            Description=Webapp
            After=network.target

            [Service]
            User=ec2-user
            WorkingDirectory=/opt/webapp
            ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
            Restart=always

            [Install]
            WantedBy=multi-user.target
            SVCEOF

            cat > /etc/nginx/conf.d/webapp.conf << 'NGINXEOF'
            server {
                listen 80;
                location / {
                    proxy_pass http://127.0.0.1:5000;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                }
            }
            NGINXEOF

            rm -f /etc/nginx/conf.d/default.conf
            chown -R ec2-user:ec2-user /opt/webapp
            systemctl daemon-reload
            systemctl enable nginx webapp
            systemctl start nginx webapp

  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub ${ProjectName}-asg
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: !Ref MinInstances
      MaxSize: !Ref MaxInstances
      DesiredCapacity: !Ref MinInstances
      TargetGroupARNs:
        - !Ref TargetGroup
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-asg-instance
          PropagateAtLaunch: true

  CPUScalingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub ${ProjectName}-VpcId

  ALBDNSName:
    Description: Application Load Balancer DNS Name
    Value: !GetAtt ApplicationLoadBalancer.DNSName
    Export:
      Name: !Sub ${ProjectName}-ALBDNSName

  RDSEndpoint:
    Description: RDS Endpoint
    Value: !GetAtt RDSInstance.Endpoint.Address
    Export:
      Name: !Sub ${ProjectName}-RDSEndpoint

  ApplicationURL:
    Description: Application URL
    Value: !Sub http://${ApplicationLoadBalancer.DNSName}
```

### Deploy CloudFormation Stack

```bash
# Deploy the stack
aws cloudformation create-stack \
    --stack-name webapp-infrastructure \
    --template-body file://3-tier-webapp-stack.yaml \
    --parameters \
        ParameterKey=ProjectName,ParameterValue=webapp \
        ParameterKey=DBUsername,ParameterValue=admin \
        ParameterKey=DBPassword,ParameterValue=YourSecurePassword123 \
    --capabilities CAPABILITY_NAMED_IAM

# Monitor stack creation
aws cloudformation wait stack-create-complete --stack-name webapp-infrastructure

# Get outputs
aws cloudformation describe-stacks \
    --stack-name webapp-infrastructure \
    --query 'Stacks[0].Outputs'
```

---

## Deployment Scripts

### deploy.sh - Complete Deployment Script

```bash
#!/bin/bash
set -euo pipefail

# Configuration
STACK_NAME="${1:-webapp-infrastructure}"
TEMPLATE_FILE="3-tier-webapp-stack.yaml"
REGION="${AWS_REGION:-us-east-1}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Prompt for database password securely
read -sp "Enter database password (min 8 chars): " DB_PASSWORD
echo

if [[ ${#DB_PASSWORD} -lt 8 ]]; then
    log_error "Password must be at least 8 characters"
    exit 1
fi

log_info "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://${TEMPLATE_FILE} > /dev/null

log_info "Deploying stack: ${STACK_NAME}"
aws cloudformation deploy \
    --stack-name ${STACK_NAME} \
    --template-file ${TEMPLATE_FILE} \
    --parameter-overrides \
        ProjectName=webapp \
        DBPassword="${DB_PASSWORD}" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${REGION}

log_info "Waiting for stack to complete..."
aws cloudformation wait stack-create-complete \
    --stack-name ${STACK_NAME} \
    --region ${REGION}

# Get outputs
log_info "Deployment complete! Getting outputs..."
aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs' \
    --region ${REGION}
```

### update-app.sh - Application Update Script

```bash
#!/bin/bash
set -euo pipefail

ASG_NAME="${1:-webapp-asg}"
INSTANCE_REFRESH_PERCENTAGE="${2:-50}"

echo "Starting instance refresh for ${ASG_NAME}..."

aws autoscaling start-instance-refresh \
    --auto-scaling-group-name ${ASG_NAME} \
    --preferences '{
        "MinHealthyPercentage": '${INSTANCE_REFRESH_PERCENTAGE}',
        "InstanceWarmup": 300
    }'

echo "Instance refresh initiated. Monitor with:"
echo "aws autoscaling describe-instance-refreshes --auto-scaling-group-name ${ASG_NAME}"
```

---

## Application Code

### Database Schema (db-schema.sql)

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS webapp;
USE webapp;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sessions table for application sessions
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INT NOT NULL,
    data JSON,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data
INSERT INTO users (email, name, password_hash) VALUES
    ('admin@example.com', 'Admin User', 'hashed_password_here'),
    ('user@example.com', 'Regular User', 'hashed_password_here');

INSERT INTO items (name, description, user_id) VALUES
    ('Sample Item 1', 'This is a sample item', 1),
    ('Sample Item 2', 'Another sample item', 2);
```

---

## Monitoring and Logging

### CloudWatch Dashboard

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name webapp-dashboard \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "title": "ALB Request Count",
                    "metrics": [
                        ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/webapp-alb/xxx"]
                    ],
                    "period": 60,
                    "stat": "Sum"
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "title": "EC2 CPU Utilization",
                    "metrics": [
                        ["AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "webapp-asg"]
                    ],
                    "period": 60,
                    "stat": "Average"
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6, "width": 12, "height": 6,
                "properties": {
                    "title": "RDS Connections",
                    "metrics": [
                        ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "webapp-mysql"]
                    ],
                    "period": 60,
                    "stat": "Average"
                }
            }
        ]
    }'
```

### CloudWatch Alarms

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name webapp-high-cpu \
    --alarm-description "High CPU utilization on webapp instances" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=AutoScalingGroupName,Value=webapp-asg \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts

# RDS connection alarm
aws cloudwatch put-metric-alarm \
    --alarm-name webapp-rds-connections \
    --alarm-description "High RDS connection count" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 150 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=webapp-mysql \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

---

## Cost Analysis

### Monthly Cost Breakdown (Production)

| Resource | Specification | Monthly Cost |
|----------|---------------|--------------|
| EC2 Instances (2x t3.micro) | 2 x 730 hours | $15.18 |
| RDS MySQL (db.t3.micro, Multi-AZ) | Multi-AZ | $25.55 |
| NAT Gateway | 1 gateway + data | $32.40 |
| Application Load Balancer | 1 ALB | $16.43 |
| Data Transfer | 100 GB | $9.00 |
| **Total Estimate** | | **~$100/month** |

### Cost Optimization Tips

1. Use Reserved Instances for predictable workloads
2. Consider Aurora Serverless for variable database loads
3. Use single NAT Gateway for dev/test environments
4. Enable Auto Scaling to match demand
5. Use Spot Instances for non-critical workloads

---

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Cannot connect to RDS | Security group misconfigured | Verify APP-SG can access RDS-SG on port 3306 |
| 502 Bad Gateway | Application not running | SSH to instance and check `systemctl status webapp` |
| Instance not healthy | Health check failing | Verify /api/health endpoint returns 200 |
| Timeout connecting to internet | NAT Gateway issue | Check route tables and NAT Gateway status |
| Auto Scaling not working | Launch template error | Check CloudWatch logs for launch failures |

### Debug Commands

```bash
# Check Auto Scaling group status
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names webapp-asg

# Check target health
aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN

# View instance logs
aws logs get-log-events \
    --log-group-name /var/log/messages \
    --log-stream-name i-1234567890abcdef0

# Check RDS status
aws rds describe-db-instances \
    --db-instance-identifier webapp-mysql \
    --query 'DBInstances[0].DBInstanceStatus'

# Connect to instance via Session Manager
aws ssm start-session --target i-1234567890abcdef0
```

---

## Cleanup

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name webapp-infrastructure

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name webapp-infrastructure

# If stack deletion fails due to RDS deletion protection:
aws rds modify-db-instance \
    --db-instance-identifier webapp-mysql \
    --no-deletion-protection

# Then retry deletion
aws cloudformation delete-stack --stack-name webapp-infrastructure
```

---

**Congratulations!** You have deployed a production-ready 3-tier web application on AWS with high availability, auto scaling, and proper security configuration.

[Back to Project Overview](./README.md) | [Next: Serverless API Project](../03-serverless-api/implementation.md)
