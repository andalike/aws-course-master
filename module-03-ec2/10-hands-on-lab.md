# EC2 Comprehensive Hands-On Lab

## Table of Contents

1. [Lab Overview](#lab-overview)
2. [Prerequisites](#prerequisites)
3. [Lab 1: Launch EC2 Instance with User Data](#lab-1-launch-ec2-instance-with-user-data)
4. [Lab 2: Attach and Manage EBS Volumes](#lab-2-attach-and-manage-ebs-volumes)
5. [Lab 3: Create Custom AMI](#lab-3-create-custom-ami)
6. [Lab 4: Set Up Auto Scaling Group](#lab-4-set-up-auto-scaling-group)
7. [Lab 5: Configure Application Load Balancer](#lab-5-configure-application-load-balancer)
8. [Lab 6: Implement Blue-Green Deployment](#lab-6-implement-blue-green-deployment)
9. [Lab 7: Full Stack Integration](#lab-7-full-stack-integration)
10. [Complete Cleanup](#complete-cleanup)
11. [Troubleshooting Guide](#troubleshooting-guide)

---

## Lab Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FINAL LAB ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              Internet                                        │
│                                  │                                          │
│                                  ▼                                          │
│                         ┌───────────────┐                                   │
│                         │      ALB      │                                   │
│                         │ (HTTPS/HTTP)  │                                   │
│                         └───────┬───────┘                                   │
│                                 │                                           │
│              ┌──────────────────┼──────────────────┐                        │
│              │                  │                  │                        │
│    ┌─────────▼─────────┐  ┌─────▼─────┐  ┌────────▼────────┐               │
│    │   Target Group    │  │  Target   │  │  Target Group   │               │
│    │   (Blue - v1)     │  │   Group   │  │  (Green - v2)   │               │
│    └─────────┬─────────┘  │  (API)    │  └────────┬────────┘               │
│              │            └─────┬─────┘           │                        │
│              │                  │                  │                        │
│              ▼                  ▼                  ▼                        │
│    ┌─────────────────────────────────────────────────────────────┐         │
│    │                  Auto Scaling Group                         │         │
│    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │         │
│    │  │  EC2    │  │  EC2    │  │  EC2    │  │  EC2    │        │         │
│    │  │ (AZ-a)  │  │ (AZ-b)  │  │ (AZ-a)  │  │ (AZ-b)  │        │         │
│    │  │         │  │         │  │         │  │         │        │         │
│    │  │ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │        │         │
│    │  │ │ EBS │ │  │ │ EBS │ │  │ │ EBS │ │  │ │ EBS │ │        │         │
│    │  │ └─────┘ │  │ └─────┘ │  │ └─────┘ │  │ └─────┘ │        │         │
│    │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │         │
│    └─────────────────────────────────────────────────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What You Will Learn

| Lab | Skills |
|-----|--------|
| Lab 1 | EC2 launch, User Data, metadata, tagging |
| Lab 2 | EBS volumes, snapshots, encryption |
| Lab 3 | AMI creation, cross-region copy |
| Lab 4 | Auto Scaling groups, launch templates, policies |
| Lab 5 | ALB configuration, target groups, health checks |
| Lab 6 | Blue-green deployment, weighted routing |
| Lab 7 | Full integration with all components |

### Time Estimate

- **Total Duration**: 3-4 hours
- **Cost Warning**: Resources will incur charges. Clean up after completion.

---

## Prerequisites

### Required Setup

```bash
# 1. Configure AWS CLI
aws configure
# Enter your Access Key ID, Secret Access Key, Region (us-east-1), Output (json)

# 2. Verify configuration
aws sts get-caller-identity

# 3. Set environment variables
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
echo "Account ID: $AWS_ACCOUNT_ID"

# 4. Get default VPC and subnets
export VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=is-default,Values=true" \
    --query 'Vpcs[0].VpcId' --output text)
echo "VPC ID: $VPC_ID"

export SUBNET_1=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[0].SubnetId' --output text)
export SUBNET_2=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --query 'Subnets[1].SubnetId' --output text)
echo "Subnet 1: $SUBNET_1"
echo "Subnet 2: $SUBNET_2"

# 5. Get latest Amazon Linux 2023 AMI
export AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-2023*-x86_64" \
              "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)
echo "AMI ID: $AMI_ID"
```

### Create Key Pair

```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name ec2-lab-key \
    --query 'KeyMaterial' \
    --output text > ec2-lab-key.pem

# Set permissions
chmod 400 ec2-lab-key.pem

echo "Key pair created: ec2-lab-key.pem"
```

---

## Lab 1: Launch EC2 Instance with User Data

### Objective

Launch an EC2 instance with a web server installed via User Data script.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAB 1 ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                          Internet                               │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                         │
│                    │ Security Group  │                         │
│                    │ (HTTP + SSH)    │                         │
│                    └────────┬────────┘                         │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                         │
│                    │   EC2 Instance  │                         │
│                    │  (Amazon Linux) │                         │
│                    │                 │                         │
│                    │  User Data:     │                         │
│                    │  - Install httpd│                         │
│                    │  - Create page  │                         │
│                    │  - Start service│                         │
│                    └─────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Create Security Group

```bash
# Create security group
export LAB_SG=$(aws ec2 create-security-group \
    --group-name lab-web-sg \
    --description "Lab Web Server Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

echo "Security Group: $LAB_SG"

# Add HTTP rule
aws ec2 authorize-security-group-ingress \
    --group-id $LAB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Add SSH rule (restrict to your IP in production)
aws ec2 authorize-security-group-ingress \
    --group-id $LAB_SG \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

echo "Security group rules added"
```

### Step 2: Create User Data Script

```bash
# Create user data script
cat << 'EOF' > user-data.sh
#!/bin/bash
# Update system
dnf update -y

# Install Apache
dnf install -y httpd

# Get instance metadata
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)
PRIVATE_IP=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/local-ipv4)
INSTANCE_TYPE=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-type)

# Create web page
cat << HTML > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>EC2 Lab Instance</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #232f3e; }
        .info { background: #e7f3fe; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .label { font-weight: bold; color: #232f3e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to EC2 Lab!</h1>
        <div class="info">
            <p><span class="label">Instance ID:</span> ${INSTANCE_ID}</p>
            <p><span class="label">Availability Zone:</span> ${AZ}</p>
            <p><span class="label">Private IP:</span> ${PRIVATE_IP}</p>
            <p><span class="label">Instance Type:</span> ${INSTANCE_TYPE}</p>
            <p><span class="label">Hostname:</span> $(hostname)</p>
            <p><span class="label">Server Time:</span> $(date)</p>
        </div>
        <h2>Version: 1.0 (Blue)</h2>
    </div>
</body>
</html>
HTML

# Create health check endpoint
echo "OK" > /var/www/html/health

# Start Apache
systemctl start httpd
systemctl enable httpd

# Create log entry
echo "User data script completed at $(date)" >> /var/log/user-data.log
EOF

echo "User data script created"
```

### Step 3: Launch EC2 Instance

```bash
# Launch instance
export INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name ec2-lab-key \
    --security-group-ids $LAB_SG \
    --subnet-id $SUBNET_1 \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=lab-web-server},{Key=Environment,Value=Lab},{Key=Project,Value=EC2-Lab}]" \
    --metadata-options "HttpTokens=required,HttpPutResponseHopLimit=2,HttpEndpoint=enabled" \
    --query 'Instances[0].InstanceId' --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
export PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "Public IP: $PUBLIC_IP"
echo ""
echo "Wait 2-3 minutes for user data to complete, then visit:"
echo "http://$PUBLIC_IP"
```

### Step 4: Verify Instance

```bash
# Check instance status
aws ec2 describe-instance-status \
    --instance-ids $INSTANCE_ID \
    --query 'InstanceStatuses[0].{InstanceState:InstanceState.Name,SystemStatus:SystemStatus.Status,InstanceStatus:InstanceStatus.Status}'

# Test web server (wait 2-3 minutes first)
curl -s http://$PUBLIC_IP | head -20

# Connect via SSH
ssh -i ec2-lab-key.pem ec2-user@$PUBLIC_IP

# View user data log (on instance)
sudo cat /var/log/user-data.log

# Exit SSH
exit
```

### Checkpoint: Lab 1 Complete

```
+------------------------------------------------------------------+
|                    LAB 1 VERIFICATION                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Security group created with HTTP and SSH rules              |
|  [ ] EC2 instance launched with user data                         |
|  [ ] Web server accessible via browser                            |
|  [ ] Instance metadata displayed on web page                      |
|  [ ] SSH connection successful                                    |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Lab 2: Attach and Manage EBS Volumes

### Objective

Create, attach, and manage EBS volumes and snapshots.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAB 2 ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────────┐                         │
│                    │   EC2 Instance  │                         │
│                    │   (from Lab 1)  │                         │
│                    └────────┬────────┘                         │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              │              │              │                    │
│              ▼              ▼              ▼                    │
│       ┌───────────┐  ┌───────────┐  ┌───────────┐             │
│       │ Root Vol  │  │ Data Vol  │  │ Logs Vol  │             │
│       │ /dev/xvda │  │ /dev/xvdf │  │ /dev/xvdg │             │
│       │   8 GB    │  │   10 GB   │  │   5 GB    │             │
│       │   gp3     │  │   gp3     │  │   gp3     │             │
│       └───────────┘  └───────────┘  └───────────┘             │
│                             │                                   │
│                             ▼                                   │
│                      ┌───────────┐                             │
│                      │ Snapshot  │                             │
│                      │ (backup)  │                             │
│                      └───────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Create EBS Volume

```bash
# Get instance AZ
export INSTANCE_AZ=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].Placement.AvailabilityZone' --output text)

echo "Instance AZ: $INSTANCE_AZ"

# Create 10GB gp3 data volume
export DATA_VOL=$(aws ec2 create-volume \
    --availability-zone $INSTANCE_AZ \
    --size 10 \
    --volume-type gp3 \
    --iops 3000 \
    --throughput 125 \
    --encrypted \
    --tag-specifications "ResourceType=volume,Tags=[{Key=Name,Value=lab-data-volume},{Key=Purpose,Value=Data}]" \
    --query 'VolumeId' --output text)

echo "Data Volume: $DATA_VOL"

# Create 5GB gp3 logs volume
export LOGS_VOL=$(aws ec2 create-volume \
    --availability-zone $INSTANCE_AZ \
    --size 5 \
    --volume-type gp3 \
    --iops 3000 \
    --throughput 125 \
    --encrypted \
    --tag-specifications "ResourceType=volume,Tags=[{Key=Name,Value=lab-logs-volume},{Key=Purpose,Value=Logs}]" \
    --query 'VolumeId' --output text)

echo "Logs Volume: $LOGS_VOL"

# Wait for volumes to be available
echo "Waiting for volumes to be available..."
aws ec2 wait volume-available --volume-ids $DATA_VOL $LOGS_VOL
echo "Volumes ready"
```

### Step 2: Attach Volumes

```bash
# Attach data volume
aws ec2 attach-volume \
    --volume-id $DATA_VOL \
    --instance-id $INSTANCE_ID \
    --device /dev/xvdf

# Attach logs volume
aws ec2 attach-volume \
    --volume-id $LOGS_VOL \
    --instance-id $INSTANCE_ID \
    --device /dev/xvdg

echo "Volumes attached"

# Verify attachments
aws ec2 describe-volumes \
    --volume-ids $DATA_VOL $LOGS_VOL \
    --query 'Volumes[*].{VolumeId:VolumeId,State:State,Device:Attachments[0].Device}'
```

### Step 3: Format and Mount Volumes (SSH into instance)

```bash
# Connect to instance
ssh -i ec2-lab-key.pem ec2-user@$PUBLIC_IP

# View available disks
lsblk

# Format data volume (xvdf)
sudo mkfs -t xfs /dev/xvdf

# Format logs volume (xvdg)
sudo mkfs -t xfs /dev/xvdg

# Create mount points
sudo mkdir -p /data
sudo mkdir -p /logs

# Mount volumes
sudo mount /dev/xvdf /data
sudo mount /dev/xvdg /logs

# Verify mounts
df -h

# Make mounts persistent (add to fstab)
echo "/dev/xvdf /data xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab
echo "/dev/xvdg /logs xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab

# Create test files
sudo touch /data/test-file.txt
sudo touch /logs/app.log
echo "Test data created at $(date)" | sudo tee /data/test-file.txt
echo "Log entry at $(date)" | sudo tee /logs/app.log

# Verify
ls -la /data
ls -la /logs

# Exit SSH
exit
```

### Step 4: Create Snapshot

```bash
# Create snapshot of data volume
export SNAPSHOT_ID=$(aws ec2 create-snapshot \
    --volume-id $DATA_VOL \
    --description "Lab data volume backup" \
    --tag-specifications "ResourceType=snapshot,Tags=[{Key=Name,Value=lab-data-snapshot},{Key=Source,Value=$DATA_VOL}]" \
    --query 'SnapshotId' --output text)

echo "Snapshot ID: $SNAPSHOT_ID"

# Wait for snapshot to complete
echo "Waiting for snapshot to complete..."
aws ec2 wait snapshot-completed --snapshot-ids $SNAPSHOT_ID
echo "Snapshot complete"

# Describe snapshot
aws ec2 describe-snapshots \
    --snapshot-ids $SNAPSHOT_ID \
    --query 'Snapshots[0].{Id:SnapshotId,Size:VolumeSize,State:State,Progress:Progress}'
```

### Step 5: Create Volume from Snapshot

```bash
# Create new volume from snapshot
export RESTORED_VOL=$(aws ec2 create-volume \
    --availability-zone $INSTANCE_AZ \
    --snapshot-id $SNAPSHOT_ID \
    --volume-type gp3 \
    --tag-specifications "ResourceType=volume,Tags=[{Key=Name,Value=lab-restored-volume},{Key=Source,Value=Snapshot}]" \
    --query 'VolumeId' --output text)

echo "Restored Volume: $RESTORED_VOL"

aws ec2 wait volume-available --volume-ids $RESTORED_VOL
echo "Restored volume ready"
```

### Checkpoint: Lab 2 Complete

```
+------------------------------------------------------------------+
|                    LAB 2 VERIFICATION                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Two EBS volumes created (data and logs)                     |
|  [ ] Volumes attached to EC2 instance                             |
|  [ ] Volumes formatted and mounted                                |
|  [ ] Mount entries added to /etc/fstab                           |
|  [ ] Snapshot created from data volume                            |
|  [ ] New volume created from snapshot                             |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Lab 3: Create Custom AMI

### Objective

Create a custom AMI from the configured instance.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LAB 3 ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     ┌─────────────────┐         ┌─────────────────┐            │
│     │   EC2 Instance  │ ──────► │   Custom AMI    │            │
│     │   (Configured)  │  Create │   (Golden)      │            │
│     └─────────────────┘         └────────┬────────┘            │
│                                          │                      │
│                          ┌───────────────┼───────────────┐     │
│                          │               │               │     │
│                          ▼               ▼               ▼     │
│                    ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│                    │ Instance │   │ Instance │   │ Instance │ │
│                    │  (new)   │   │  (new)   │   │  (new)   │ │
│                    └──────────┘   └──────────┘   └──────────┘ │
│                                                                 │
│     Benefits:                                                   │
│     - Faster launch (pre-configured)                           │
│     - Consistent deployments                                   │
│     - Version control                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Prepare Instance for AMI

```bash
# Connect to instance
ssh -i ec2-lab-key.pem ec2-user@$PUBLIC_IP

# Clean up instance for AMI creation
# Remove SSH keys (optional, will be regenerated)
# sudo rm -f /home/ec2-user/.ssh/authorized_keys

# Clear logs
sudo rm -rf /var/log/*.log
sudo rm -rf /var/log/httpd/*

# Clear history
history -c

# Exit
exit
```

### Step 2: Create AMI

```bash
# Create AMI from instance
export CUSTOM_AMI=$(aws ec2 create-image \
    --instance-id $INSTANCE_ID \
    --name "lab-web-server-ami-$(date +%Y%m%d-%H%M%S)" \
    --description "Custom web server AMI with Apache" \
    --no-reboot \
    --tag-specifications "ResourceType=image,Tags=[{Key=Name,Value=lab-custom-ami},{Key=Version,Value=1.0},{Key=Environment,Value=Lab}]" \
    --query 'ImageId' --output text)

echo "Custom AMI: $CUSTOM_AMI"

# Wait for AMI to be available (this can take several minutes)
echo "Waiting for AMI to be available (this may take 5-10 minutes)..."
aws ec2 wait image-available --image-ids $CUSTOM_AMI
echo "AMI ready"

# Describe AMI
aws ec2 describe-images \
    --image-ids $CUSTOM_AMI \
    --query 'Images[0].{ImageId:ImageId,Name:Name,State:State,CreationDate:CreationDate}'
```

### Step 3: Launch Instance from Custom AMI

```bash
# Launch new instance from custom AMI
export NEW_INSTANCE=$(aws ec2 run-instances \
    --image-id $CUSTOM_AMI \
    --instance-type t3.micro \
    --key-name ec2-lab-key \
    --security-group-ids $LAB_SG \
    --subnet-id $SUBNET_2 \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=lab-from-ami},{Key=Source,Value=CustomAMI}]" \
    --query 'Instances[0].InstanceId' --output text)

echo "New Instance: $NEW_INSTANCE"

aws ec2 wait instance-running --instance-ids $NEW_INSTANCE

export NEW_PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $NEW_INSTANCE \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "New Instance Public IP: $NEW_PUBLIC_IP"
echo "Test: http://$NEW_PUBLIC_IP"
```

### Step 4: Copy AMI to Another Region (Optional)

```bash
# Copy AMI to us-west-2
export COPIED_AMI=$(aws ec2 copy-image \
    --source-region $AWS_REGION \
    --source-image-id $CUSTOM_AMI \
    --name "lab-web-server-ami-copy" \
    --description "Copied from us-east-1" \
    --region us-west-2 \
    --query 'ImageId' --output text)

echo "Copied AMI (us-west-2): $COPIED_AMI"
```

### Checkpoint: Lab 3 Complete

```
+------------------------------------------------------------------+
|                    LAB 3 VERIFICATION                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Custom AMI created from configured instance                  |
|  [ ] AMI is in available state                                    |
|  [ ] New instance launched from custom AMI                        |
|  [ ] Web server accessible on new instance                        |
|  [ ] (Optional) AMI copied to another region                      |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Lab 4: Set Up Auto Scaling Group

### Objective

Create a launch template and Auto Scaling group with scaling policies.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LAB 4 ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                     ┌───────────────────────────┐                      │
│                     │     Launch Template       │                      │
│                     │ - AMI: Custom AMI         │                      │
│                     │ - Type: t3.micro          │                      │
│                     │ - User Data               │                      │
│                     └────────────┬──────────────┘                      │
│                                  │                                      │
│                                  ▼                                      │
│                     ┌───────────────────────────┐                      │
│                     │   Auto Scaling Group      │                      │
│                     │   Min: 2, Max: 4, Des: 2  │                      │
│                     └────────────┬──────────────┘                      │
│                                  │                                      │
│              ┌───────────────────┼───────────────────┐                 │
│              │                   │                   │                  │
│              ▼                   ▼                   ▼                  │
│        ┌──────────┐        ┌──────────┐        ┌──────────┐           │
│        │   EC2    │        │   EC2    │        │   EC2    │           │
│        │  (AZ-a)  │        │  (AZ-b)  │        │  (AZ-a)  │           │
│        └──────────┘        └──────────┘        └──────────┘           │
│                                  │                                      │
│                                  ▼                                      │
│                     ┌───────────────────────────┐                      │
│                     │    Scaling Policies       │                      │
│                     │ - Target Tracking (CPU)   │                      │
│                     │ - Scheduled Scaling       │                      │
│                     └───────────────────────────┘                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create Launch Template

```bash
# Create user data for ASG instances
cat << 'EOF' > asg-user-data.sh
#!/bin/bash
dnf update -y
dnf install -y httpd stress

TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)

cat << HTML > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Auto Scaling Instance</title>
    <style>
        body { font-family: Arial; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto; }
        h1 { color: #667eea; }
        .info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Auto Scaling Instance</h1>
        <div class="info">
            <p><strong>Instance ID:</strong> ${INSTANCE_ID}</p>
            <p><strong>AZ:</strong> ${AZ}</p>
            <p><strong>Time:</strong> $(date)</p>
        </div>
        <h2>Version: 1.0 (Blue)</h2>
    </div>
</body>
</html>
HTML

echo "OK" > /var/www/html/health
systemctl start httpd
systemctl enable httpd
EOF

# Base64 encode user data
USER_DATA_B64=$(base64 < asg-user-data.sh)

# Create launch template
aws ec2 create-launch-template \
    --launch-template-name lab-web-template \
    --version-description "v1 - Initial version" \
    --launch-template-data "{
        \"ImageId\": \"$AMI_ID\",
        \"InstanceType\": \"t3.micro\",
        \"KeyName\": \"ec2-lab-key\",
        \"SecurityGroupIds\": [\"$LAB_SG\"],
        \"UserData\": \"$USER_DATA_B64\",
        \"Monitoring\": {\"Enabled\": true},
        \"TagSpecifications\": [{
            \"ResourceType\": \"instance\",
            \"Tags\": [{\"Key\": \"Name\", \"Value\": \"asg-web-server\"}, {\"Key\": \"Environment\", \"Value\": \"Lab\"}]
        }]
    }"

echo "Launch template created"

# Describe launch template
aws ec2 describe-launch-templates \
    --launch-template-names lab-web-template \
    --query 'LaunchTemplates[0].{Name:LaunchTemplateName,Version:LatestVersionNumber,Id:LaunchTemplateId}'
```

### Step 2: Create Auto Scaling Group

```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name lab-web-asg \
    --launch-template "LaunchTemplateName=lab-web-template,Version=\$Latest" \
    --min-size 2 \
    --max-size 4 \
    --desired-capacity 2 \
    --vpc-zone-identifier "$SUBNET_1,$SUBNET_2" \
    --health-check-type EC2 \
    --health-check-grace-period 300 \
    --tags "Key=Name,Value=asg-instance,PropagateAtLaunch=true" \
           "Key=Environment,Value=Lab,PropagateAtLaunch=true"

echo "Auto Scaling Group created"

# Wait for instances to launch
echo "Waiting for instances to launch..."
sleep 60

# Describe ASG
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names lab-web-asg \
    --query 'AutoScalingGroups[0].{Name:AutoScalingGroupName,Min:MinSize,Max:MaxSize,Desired:DesiredCapacity,Instances:Instances[*].InstanceId}'
```

### Step 3: Create Scaling Policies

```bash
# Create Target Tracking Scaling Policy
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name lab-web-asg \
    --policy-name cpu-target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0,
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60
    }'

echo "Target tracking policy created"

# Create scheduled scaling actions
# Scale up at 9 AM
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name lab-web-asg \
    --scheduled-action-name scale-up-morning \
    --recurrence "0 9 * * MON-FRI" \
    --desired-capacity 3

# Scale down at 6 PM
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name lab-web-asg \
    --scheduled-action-name scale-down-evening \
    --recurrence "0 18 * * MON-FRI" \
    --desired-capacity 2

echo "Scheduled actions created"

# View policies
aws autoscaling describe-policies \
    --auto-scaling-group-name lab-web-asg \
    --query 'ScalingPolicies[*].{PolicyName:PolicyName,PolicyType:PolicyType}'
```

### Step 4: Test Auto Scaling

```bash
# Get instance IPs from ASG
aws ec2 describe-instances \
    --filters "Name=tag:aws:autoscaling:groupName,Values=lab-web-asg" \
              "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].[PublicIpAddress,AvailabilityZone]' --output table

# Manually trigger scaling
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name lab-web-asg \
    --desired-capacity 3

echo "Scaling to 3 instances..."
sleep 60

# Check activities
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name lab-web-asg \
    --max-items 5 \
    --query 'Activities[*].{Activity:Description,Status:StatusCode}'

# Scale back to 2
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name lab-web-asg \
    --desired-capacity 2

echo "Scaling back to 2 instances..."
```

### Checkpoint: Lab 4 Complete

```
+------------------------------------------------------------------+
|                    LAB 4 VERIFICATION                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Launch template created with user data                       |
|  [ ] Auto Scaling Group created with min=2, max=4                |
|  [ ] Target tracking scaling policy configured                    |
|  [ ] Scheduled scaling actions created                            |
|  [ ] Manual scaling tested successfully                           |
|  [ ] Instances distributed across AZs                             |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Lab 5: Configure Application Load Balancer

### Objective

Create an ALB and integrate it with the Auto Scaling group.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LAB 5 ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                              Internet                                    │
│                                  │                                      │
│                                  ▼                                      │
│                    ┌─────────────────────────┐                         │
│                    │    Security Group       │                         │
│                    │    (ALB - HTTP/HTTPS)   │                         │
│                    └────────────┬────────────┘                         │
│                                 │                                       │
│                                 ▼                                       │
│                    ┌─────────────────────────┐                         │
│                    │   Application Load      │                         │
│                    │      Balancer           │                         │
│                    │                         │                         │
│                    │  ┌─────────────────┐    │                         │
│                    │  │ Listener :80    │    │                         │
│                    │  └────────┬────────┘    │                         │
│                    │           │             │                         │
│                    │  ┌────────▼────────┐    │                         │
│                    │  │  Default Rule   │    │                         │
│                    │  │  Forward to TG  │    │                         │
│                    │  └─────────────────┘    │                         │
│                    └────────────┬────────────┘                         │
│                                 │                                       │
│                                 ▼                                       │
│                    ┌─────────────────────────┐                         │
│                    │     Target Group        │                         │
│                    │   (Health: /health)     │                         │
│                    └────────────┬────────────┘                         │
│                                 │                                       │
│              ┌──────────────────┼──────────────────┐                   │
│              │                  │                  │                    │
│              ▼                  ▼                  ▼                    │
│        ┌──────────┐       ┌──────────┐       ┌──────────┐             │
│        │   EC2    │       │   EC2    │       │   EC2    │             │
│        │  (ASG)   │       │  (ASG)   │       │  (ASG)   │             │
│        └──────────┘       └──────────┘       └──────────┘             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create ALB Security Group

```bash
# Create ALB security group
export ALB_SG=$(aws ec2 create-security-group \
    --group-name lab-alb-sg \
    --description "ALB Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

echo "ALB Security Group: $ALB_SG"

# Allow HTTP
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Update instance security group to allow traffic from ALB only
aws ec2 authorize-security-group-ingress \
    --group-id $LAB_SG \
    --protocol tcp \
    --port 80 \
    --source-group $ALB_SG

echo "Security groups configured"
```

### Step 2: Create Target Group

```bash
# Create target group
export TG_ARN=$(aws elbv2 create-target-group \
    --name lab-web-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --target-type instance \
    --health-check-enabled \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --matcher "HttpCode=200" \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

echo "Target Group ARN: $TG_ARN"
```

### Step 3: Create Application Load Balancer

```bash
# Create ALB
export ALB_ARN=$(aws elbv2 create-load-balancer \
    --name lab-web-alb \
    --type application \
    --subnets $SUBNET_1 $SUBNET_2 \
    --security-groups $ALB_SG \
    --scheme internet-facing \
    --ip-address-type ipv4 \
    --tags Key=Environment,Value=Lab \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text)

echo "ALB ARN: $ALB_ARN"

# Get ALB DNS name
export ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].DNSName' --output text)

echo "ALB DNS: $ALB_DNS"
```

### Step 4: Create Listener

```bash
# Create HTTP listener
export LISTENER_ARN=$(aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN \
    --query 'Listeners[0].ListenerArn' --output text)

echo "Listener ARN: $LISTENER_ARN"
```

### Step 5: Attach ASG to Target Group

```bash
# Update ASG to use target group
aws autoscaling attach-load-balancer-target-groups \
    --auto-scaling-group-name lab-web-asg \
    --target-group-arns $TG_ARN

# Update ASG health check to ELB
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name lab-web-asg \
    --health-check-type ELB \
    --health-check-grace-period 300

echo "ASG attached to Target Group"

# Wait for targets to be healthy
echo "Waiting for targets to register and become healthy..."
sleep 60

# Check target health
aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN
```

### Step 6: Test Load Balancer

```bash
# Test ALB
echo "Testing ALB..."
echo "URL: http://$ALB_DNS"

# Make multiple requests to see load balancing
for i in {1..5}; do
    echo "Request $i:"
    curl -s http://$ALB_DNS | grep "Instance ID"
    sleep 1
done
```

### Step 7: Add Path-Based Routing (Optional)

```bash
# Create API target group
export API_TG_ARN=$(aws elbv2 create-target-group \
    --name lab-api-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --target-type instance \
    --health-check-path /health \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

# Add path-based rule
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 10 \
    --conditions Field=path-pattern,Values='/api/*' \
    --actions Type=forward,TargetGroupArn=$API_TG_ARN

echo "Path-based routing rule created"
```

### Checkpoint: Lab 5 Complete

```
+------------------------------------------------------------------+
|                    LAB 5 VERIFICATION                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] ALB security group created                                   |
|  [ ] Target group created with health check                       |
|  [ ] Application Load Balancer created                            |
|  [ ] HTTP listener configured                                     |
|  [ ] ASG attached to target group                                 |
|  [ ] Load balancing working (requests distributed)                |
|  [ ] (Optional) Path-based routing configured                     |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Lab 6: Implement Blue-Green Deployment

### Objective

Set up blue-green deployment using weighted target groups.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   BLUE-GREEN DEPLOYMENT ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                              Internet                                    │
│                                  │                                      │
│                                  ▼                                      │
│                    ┌─────────────────────────┐                         │
│                    │   Application Load      │                         │
│                    │      Balancer           │                         │
│                    └────────────┬────────────┘                         │
│                                 │                                       │
│                    ┌────────────┴────────────┐                         │
│                    │    Weighted Routing     │                         │
│                    │                         │                         │
│                    │  Blue: 90%  Green: 10%  │ ◄── Canary              │
│                    │  Blue: 50%  Green: 50%  │ ◄── 50/50 Split         │
│                    │  Blue: 0%   Green: 100% │ ◄── Full Switch         │
│                    │                         │                         │
│                    └────────────┬────────────┘                         │
│                                 │                                       │
│           ┌─────────────────────┴─────────────────────┐               │
│           │                                           │                │
│           ▼                                           ▼                │
│  ┌─────────────────────┐                 ┌─────────────────────┐      │
│  │   Blue Target Group │                 │  Green Target Group │      │
│  │     (Version 1.0)   │                 │    (Version 2.0)    │      │
│  └─────────┬───────────┘                 └──────────┬──────────┘      │
│            │                                        │                  │
│    ┌───────┴───────┐                        ┌───────┴───────┐         │
│    ▼               ▼                        ▼               ▼         │
│ ┌──────┐       ┌──────┐                 ┌──────┐       ┌──────┐      │
│ │ EC2  │       │ EC2  │                 │ EC2  │       │ EC2  │      │
│ │ Blue │       │ Blue │                 │Green │       │Green │      │
│ └──────┘       └──────┘                 └──────┘       └──────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Step 1: Create Green Target Group and Instances

```bash
# Create Green target group
export GREEN_TG_ARN=$(aws elbv2 create-target-group \
    --name lab-green-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --target-type instance \
    --health-check-enabled \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

echo "Green Target Group: $GREEN_TG_ARN"

# Create user data for Green version
cat << 'EOF' > green-user-data.sh
#!/bin/bash
dnf update -y
dnf install -y httpd

TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)

cat << HTML > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Green Deployment</title>
    <style>
        body { font-family: Arial; margin: 40px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); min-height: 100vh; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto; }
        h1 { color: #11998e; }
        .info { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .version { background: #11998e; color: white; padding: 10px; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Green Deployment</h1>
        <div class="info">
            <p><strong>Instance ID:</strong> ${INSTANCE_ID}</p>
            <p><strong>AZ:</strong> ${AZ}</p>
            <p><strong>Time:</strong> $(date)</p>
        </div>
        <div class="version">
            <h2>Version: 2.0 (GREEN)</h2>
            <p>New Features: Enhanced UI, Better Performance</p>
        </div>
    </div>
</body>
</html>
HTML

echo "OK" > /var/www/html/health
systemctl start httpd
systemctl enable httpd
EOF

GREEN_USER_DATA_B64=$(base64 < green-user-data.sh)

# Launch Green instances
export GREEN_INSTANCE_1=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name ec2-lab-key \
    --security-group-ids $LAB_SG \
    --subnet-id $SUBNET_1 \
    --user-data file://green-user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=green-web-1},{Key=Version,Value=2.0},{Key=Deployment,Value=Green}]" \
    --query 'Instances[0].InstanceId' --output text)

export GREEN_INSTANCE_2=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name ec2-lab-key \
    --security-group-ids $LAB_SG \
    --subnet-id $SUBNET_2 \
    --user-data file://green-user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=green-web-2},{Key=Version,Value=2.0},{Key=Deployment,Value=Green}]" \
    --query 'Instances[0].InstanceId' --output text)

echo "Green Instance 1: $GREEN_INSTANCE_1"
echo "Green Instance 2: $GREEN_INSTANCE_2"

# Wait for instances
aws ec2 wait instance-running --instance-ids $GREEN_INSTANCE_1 $GREEN_INSTANCE_2

# Register to target group
aws elbv2 register-targets \
    --target-group-arn $GREEN_TG_ARN \
    --targets Id=$GREEN_INSTANCE_1 Id=$GREEN_INSTANCE_2

echo "Green instances registered to target group"

# Wait for health checks
sleep 60
```

### Step 2: Implement Weighted Routing

```bash
# Rename original TG for clarity
export BLUE_TG_ARN=$TG_ARN

# Get default rule ARN
export DEFAULT_RULE_ARN=$(aws elbv2 describe-rules \
    --listener-arn $LISTENER_ARN \
    --query "Rules[?IsDefault==\`true\`].RuleArn" --output text)

echo "Default Rule ARN: $DEFAULT_RULE_ARN"

# Phase 1: Canary (90% Blue, 10% Green)
echo "Phase 1: Canary deployment (90/10)"
aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions '[
        {
            "Type": "forward",
            "ForwardConfig": {
                "TargetGroups": [
                    {
                        "TargetGroupArn": "'$BLUE_TG_ARN'",
                        "Weight": 90
                    },
                    {
                        "TargetGroupArn": "'$GREEN_TG_ARN'",
                        "Weight": 10
                    }
                ],
                "TargetGroupStickinessConfig": {
                    "Enabled": true,
                    "DurationSeconds": 120
                }
            }
        }
    ]'

echo "Waiting 30 seconds for canary testing..."
sleep 30

# Test canary
echo "Testing traffic distribution:"
for i in {1..10}; do
    curl -s http://$ALB_DNS | grep -o "Version: [0-9.]*"
done
```

### Step 3: Progressive Traffic Shifting

```bash
# Phase 2: 50/50 Split
echo ""
echo "Phase 2: 50/50 split"
aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions '[
        {
            "Type": "forward",
            "ForwardConfig": {
                "TargetGroups": [
                    {
                        "TargetGroupArn": "'$BLUE_TG_ARN'",
                        "Weight": 50
                    },
                    {
                        "TargetGroupArn": "'$GREEN_TG_ARN'",
                        "Weight": 50
                    }
                ]
            }
        }
    ]'

sleep 10

# Test 50/50
echo "Testing 50/50 distribution:"
for i in {1..10}; do
    curl -s http://$ALB_DNS | grep -o "Version: [0-9.]*"
done

# Phase 3: Full switch to Green
echo ""
echo "Phase 3: Full switch to Green (100%)"
aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions '[
        {
            "Type": "forward",
            "ForwardConfig": {
                "TargetGroups": [
                    {
                        "TargetGroupArn": "'$BLUE_TG_ARN'",
                        "Weight": 0
                    },
                    {
                        "TargetGroupArn": "'$GREEN_TG_ARN'",
                        "Weight": 100
                    }
                ]
            }
        }
    ]'

sleep 10

# Verify full switch
echo "Verifying all traffic goes to Green:"
for i in {1..5}; do
    curl -s http://$ALB_DNS | grep -o "Version: [0-9.]*"
done
```

### Step 4: Rollback Procedure

```bash
# Rollback to Blue if issues detected
echo ""
echo "Rollback procedure:"
echo "Rolling back to Blue..."

aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --default-actions Type=forward,TargetGroupArn=$BLUE_TG_ARN

echo "Rollback complete - all traffic now goes to Blue"

# Verify rollback
for i in {1..3}; do
    curl -s http://$ALB_DNS | grep -o "Version: [0-9.]*"
done
```

### Checkpoint: Lab 6 Complete

```
+------------------------------------------------------------------+
|                    LAB 6 VERIFICATION                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Green target group created                                   |
|  [ ] Green instances launched and registered                      |
|  [ ] Weighted routing configured (90/10)                          |
|  [ ] Traffic progressively shifted (50/50, then 100%)            |
|  [ ] Rollback procedure tested                                    |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Lab 7: Full Stack Integration

### Objective

Integrate all components into a production-like architecture.

### Final Architecture Test

```bash
echo "============================================"
echo "        FULL STACK INTEGRATION TEST        "
echo "============================================"
echo ""

# 1. Check ALB status
echo "1. ALB Status:"
aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].{Name:LoadBalancerName,State:State.Code,DNS:DNSName}'

echo ""

# 2. Check Target Groups
echo "2. Target Groups:"
aws elbv2 describe-target-groups \
    --target-group-arns $BLUE_TG_ARN $GREEN_TG_ARN \
    --query 'TargetGroups[*].{Name:TargetGroupName,HealthyCount:length(HealthyHosts[])}'

echo ""

# 3. Check Auto Scaling Group
echo "3. Auto Scaling Group:"
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names lab-web-asg \
    --query 'AutoScalingGroups[0].{Name:AutoScalingGroupName,Min:MinSize,Max:MaxSize,Desired:DesiredCapacity,InstanceCount:length(Instances)}'

echo ""

# 4. Check all instances
echo "4. All Running Instances:"
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
              "Name=tag:Environment,Values=Lab" \
    --query 'Reservations[*].Instances[*].{InstanceId:InstanceId,Type:InstanceType,AZ:Placement.AvailabilityZone,PublicIP:PublicIpAddress}' \
    --output table

echo ""

# 5. Health check all targets
echo "5. Target Health (Blue):"
aws elbv2 describe-target-health \
    --target-group-arn $BLUE_TG_ARN \
    --query 'TargetHealthDescriptions[*].{Target:Target.Id,Health:TargetHealth.State}'

echo ""
echo "   Target Health (Green):"
aws elbv2 describe-target-health \
    --target-group-arn $GREEN_TG_ARN \
    --query 'TargetHealthDescriptions[*].{Target:Target.Id,Health:TargetHealth.State}'

echo ""

# 6. Test the application
echo "6. Application Test:"
echo "   URL: http://$ALB_DNS"
curl -s http://$ALB_DNS | grep -E "(Instance ID|Version)"

echo ""
echo "============================================"
echo "        INTEGRATION TEST COMPLETE          "
echo "============================================"
```

### Create Monitoring Dashboard Commands

```bash
# View CloudWatch metrics for ALB
echo "CloudWatch Metrics Commands:"
echo ""

# Healthy host count
echo "# Healthy Host Count"
echo "aws cloudwatch get-metric-statistics \\"
echo "    --namespace AWS/ApplicationELB \\"
echo "    --metric-name HealthyHostCount \\"
echo "    --dimensions Name=TargetGroup,Value=targetgroup/lab-web-tg/xxx \\"
echo "                 Name=LoadBalancer,Value=app/lab-web-alb/xxx \\"
echo "    --start-time \$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \\"
echo "    --end-time \$(date -u +%Y-%m-%dT%H:%M:%SZ) \\"
echo "    --period 300 \\"
echo "    --statistics Average"

echo ""

# Request count
echo "# Request Count"
echo "aws cloudwatch get-metric-statistics \\"
echo "    --namespace AWS/ApplicationELB \\"
echo "    --metric-name RequestCount \\"
echo "    --dimensions Name=LoadBalancer,Value=app/lab-web-alb/xxx \\"
echo "    --start-time \$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \\"
echo "    --end-time \$(date -u +%Y-%m-%dT%H:%M:%SZ) \\"
echo "    --period 300 \\"
echo "    --statistics Sum"
```

---

## Complete Cleanup

### Cleanup Script

```bash
#!/bin/bash
echo "============================================"
echo "           COMPLETE CLEANUP                 "
echo "============================================"
echo ""
echo "This will delete ALL resources created in the labs."
echo "Press Ctrl+C within 10 seconds to cancel..."
sleep 10

echo ""
echo "Starting cleanup..."

# 1. Delete Auto Scaling Group
echo "1. Deleting Auto Scaling Group..."
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name lab-web-asg \
    --min-size 0 \
    --max-size 0 \
    --desired-capacity 0 2>/dev/null || true

sleep 30

aws autoscaling delete-auto-scaling-group \
    --auto-scaling-group-name lab-web-asg \
    --force-delete 2>/dev/null || true

echo "   ASG deletion initiated"

# 2. Delete Launch Template
echo "2. Deleting Launch Template..."
aws ec2 delete-launch-template \
    --launch-template-name lab-web-template 2>/dev/null || true

# 3. Delete ALB Listeners
echo "3. Deleting ALB Listeners..."
for LISTENER in $(aws elbv2 describe-listeners \
    --load-balancer-arn $ALB_ARN \
    --query 'Listeners[*].ListenerArn' --output text 2>/dev/null); do
    aws elbv2 delete-listener --listener-arn $LISTENER 2>/dev/null || true
done

# 4. Delete Target Groups
echo "4. Deleting Target Groups..."
for TG in lab-web-tg lab-green-tg lab-api-tg; do
    TG_ARN=$(aws elbv2 describe-target-groups \
        --names $TG \
        --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null)
    if [ "$TG_ARN" != "None" ] && [ -n "$TG_ARN" ]; then
        aws elbv2 delete-target-group --target-group-arn $TG_ARN 2>/dev/null || true
    fi
done

# 5. Delete Load Balancer
echo "5. Deleting Load Balancer..."
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN 2>/dev/null || true

echo "   Waiting for ALB deletion..."
sleep 60

# 6. Terminate all lab instances
echo "6. Terminating EC2 Instances..."
INSTANCE_IDS=$(aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=Lab" \
              "Name=instance-state-name,Values=running,stopped,pending" \
    --query 'Reservations[*].Instances[*].InstanceId' --output text)

if [ -n "$INSTANCE_IDS" ]; then
    aws ec2 terminate-instances --instance-ids $INSTANCE_IDS 2>/dev/null || true
    echo "   Waiting for instances to terminate..."
    aws ec2 wait instance-terminated --instance-ids $INSTANCE_IDS 2>/dev/null || true
fi

# 7. Delete EBS Volumes
echo "7. Deleting EBS Volumes..."
for VOL in $DATA_VOL $LOGS_VOL $RESTORED_VOL; do
    if [ -n "$VOL" ]; then
        aws ec2 delete-volume --volume-id $VOL 2>/dev/null || true
    fi
done

# 8. Delete Snapshots
echo "8. Deleting Snapshots..."
if [ -n "$SNAPSHOT_ID" ]; then
    aws ec2 delete-snapshot --snapshot-id $SNAPSHOT_ID 2>/dev/null || true
fi

# 9. Deregister AMI
echo "9. Deregistering Custom AMI..."
if [ -n "$CUSTOM_AMI" ]; then
    # Get snapshot IDs from AMI
    SNAPSHOT_IDS=$(aws ec2 describe-images \
        --image-ids $CUSTOM_AMI \
        --query 'Images[0].BlockDeviceMappings[*].Ebs.SnapshotId' --output text 2>/dev/null)

    aws ec2 deregister-image --image-id $CUSTOM_AMI 2>/dev/null || true

    # Delete associated snapshots
    for SNAP in $SNAPSHOT_IDS; do
        aws ec2 delete-snapshot --snapshot-id $SNAP 2>/dev/null || true
    done
fi

# 10. Delete Security Groups (wait for dependencies to clear)
echo "10. Deleting Security Groups..."
sleep 30

# Remove ingress rules first
aws ec2 revoke-security-group-ingress \
    --group-id $LAB_SG \
    --protocol tcp --port 80 \
    --source-group $ALB_SG 2>/dev/null || true

aws ec2 delete-security-group --group-id $ALB_SG 2>/dev/null || true
aws ec2 delete-security-group --group-id $LAB_SG 2>/dev/null || true

# 11. Delete Key Pair
echo "11. Deleting Key Pair..."
aws ec2 delete-key-pair --key-name ec2-lab-key 2>/dev/null || true
rm -f ec2-lab-key.pem

# 12. Cleanup local files
echo "12. Cleaning up local files..."
rm -f user-data.sh asg-user-data.sh green-user-data.sh

echo ""
echo "============================================"
echo "           CLEANUP COMPLETE                 "
echo "============================================"
echo ""
echo "All lab resources have been deleted."
echo ""
echo "Verify in AWS Console:"
echo "  - EC2 Dashboard: No lab instances"
echo "  - Load Balancers: No lab ALB"
echo "  - Auto Scaling: No lab ASG"
echo "  - EBS Volumes: No lab volumes"
echo "  - AMIs: No lab AMIs"
echo "  - Security Groups: No lab SGs"
```

### Manual Cleanup Verification

```bash
# Verify all resources are deleted
echo "Verification Commands:"
echo ""

echo "# Check for remaining instances"
aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=Lab" \
    --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'

echo ""
echo "# Check for remaining volumes"
aws ec2 describe-volumes \
    --filters "Name=tag:Purpose,Values=Data,Logs" \
    --query 'Volumes[*].[VolumeId,State]'

echo ""
echo "# Check for remaining load balancers"
aws elbv2 describe-load-balancers \
    --names lab-web-alb 2>/dev/null || echo "No lab ALB found"

echo ""
echo "# Check for remaining ASG"
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names lab-web-asg 2>/dev/null || echo "No lab ASG found"
```

---

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Instance not launching | Quota limit | Check EC2 limits in Service Quotas |
| User data not running | Script error | Check `/var/log/cloud-init-output.log` |
| Health check failing | Wrong path/port | Verify health check config, check SG |
| Cannot SSH | Security group | Verify port 22 is open to your IP |
| ALB 502 error | Targets unhealthy | Check target group health, app logs |
| ASG not scaling | Policy not triggered | Check CloudWatch alarms, metrics |
| EBS attach fails | Wrong AZ | Volume and instance must be in same AZ |

### Debug Commands

```bash
# Check instance system log
aws ec2 get-console-output --instance-id $INSTANCE_ID --output text

# Check instance status
aws ec2 describe-instance-status --instance-ids $INSTANCE_ID

# Check CloudWatch logs (if configured)
aws logs get-log-events \
    --log-group-name /var/log/messages \
    --log-stream-name $INSTANCE_ID

# Check ASG activities
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name lab-web-asg \
    --max-items 10

# Check ELB access logs
aws s3 ls s3://your-logs-bucket/AWSLogs/

# Test security group connectivity
nc -zv $PUBLIC_IP 80
nc -zv $PUBLIC_IP 22
```

### SSH Troubleshooting

```bash
# If SSH connection times out
# 1. Check security group
aws ec2 describe-security-groups \
    --group-ids $LAB_SG \
    --query 'SecurityGroups[0].IpPermissions'

# 2. Check instance is running
aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].State.Name'

# 3. Verify key pair permissions
ls -la ec2-lab-key.pem
# Should be -r-------- (400)

# 4. SSH with verbose output
ssh -v -i ec2-lab-key.pem ec2-user@$PUBLIC_IP
```

---

## Summary

### What You Learned

1. **EC2 Fundamentals**: Instance launch, user data, metadata
2. **Storage Management**: EBS volumes, snapshots, encryption
3. **AMI Creation**: Custom AMIs, cross-region copy
4. **Auto Scaling**: Launch templates, ASG, scaling policies
5. **Load Balancing**: ALB, target groups, health checks
6. **Deployment Strategies**: Blue-green, weighted routing

### Next Steps

- Explore more advanced scenarios
- Add HTTPS with ACM certificates
- Implement monitoring with CloudWatch
- Set up CI/CD pipelines for deployments
- Study for AWS certifications

---

**Lab Version**: 1.0
**Last Updated**: January 2025
**Estimated Duration**: 3-4 hours
