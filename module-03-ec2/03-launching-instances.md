# 03 - Launching EC2 Instances

## Overview

This section covers the complete process of launching EC2 instances, from using the console launch wizard to automation with user data scripts and accessing the instance metadata service.

---

## Launch Instance Wizard (Console)

### Step-by-Step Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                    EC2 Launch Wizard Steps                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Name and Tags                                          │
│     └─▶ Give your instance a meaningful name                    │
│                                                                  │
│  Step 2: Application and OS Images (AMI)                        │
│     └─▶ Choose operating system and software                    │
│                                                                  │
│  Step 3: Instance Type                                          │
│     └─▶ Select CPU, memory, network capacity                    │
│                                                                  │
│  Step 4: Key Pair (Login)                                       │
│     └─▶ Create or select SSH key for access                     │
│                                                                  │
│  Step 5: Network Settings                                       │
│     └─▶ VPC, subnet, security groups, public IP                 │
│                                                                  │
│  Step 6: Configure Storage                                      │
│     └─▶ Root volume and additional volumes                      │
│                                                                  │
│  Step 7: Advanced Details                                       │
│     └─▶ User data, IAM role, placement, etc.                    │
│                                                                  │
│  Step 8: Review and Launch                                      │
│     └─▶ Verify settings and launch                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Configuration Options

#### 1. Name and Tags
```
Name: web-server-production-01
Additional tags:
  - Environment: Production
  - Application: WebServer
  - Owner: TeamA
  - CostCenter: CC-12345
```

#### 2. AMI Selection
| Category | Recommendation |
|----------|---------------|
| Quick Start | Amazon Linux 2023 (free tier eligible) |
| My AMIs | Your custom/golden AMIs |
| AWS Marketplace | Pre-configured software |
| Community AMIs | Use with caution |

#### 3. Instance Type
- Development: t3.micro (free tier)
- Testing: t3.small or t3.medium
- Production: m5.large or higher

#### 4. Key Pair
```bash
# Create key pair via CLI if needed
aws ec2 create-key-pair \
    --key-name my-key-pair \
    --query 'KeyMaterial' \
    --output text > my-key-pair.pem

# Set proper permissions
chmod 400 my-key-pair.pem
```

#### 5. Network Settings
| Setting | Production Recommendation |
|---------|-------------------------|
| VPC | Use custom VPC (not default) |
| Subnet | Private subnet for backend |
| Auto-assign Public IP | Disable for private instances |
| Security Group | Create specific, minimal rules |

#### 6. Storage Configuration
```
Root Volume:
  - Size: 20 GB (minimum recommended)
  - Type: gp3
  - Delete on termination: Yes (for dev), No (for prod data)
  - Encrypted: Yes

Additional Volumes:
  - /dev/sdb: 100 GB gp3 for application data
```

#### 7. Advanced Details

| Option | Description |
|--------|-------------|
| Purchasing option | Spot, On-Demand |
| IAM instance profile | Attach IAM role |
| Hostname type | IP name or Resource name |
| User data | Bootstrap scripts |
| Metadata version | IMDSv2 (recommended) |
| Tenancy | Shared, Dedicated, Host |
| Placement group | For HPC/low latency |
| Shutdown behavior | Stop or Terminate |
| Termination protection | Enable for production |
| Credit specification | Unlimited or Standard (T instances) |

---

## Launching Instances with AWS CLI

### Basic Launch Command

```bash
# Launch a single instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --key-name my-key-pair \
    --security-group-ids sg-0123456789abcdef0 \
    --subnet-id subnet-0123456789abcdef0 \
    --count 1
```

### Complete Launch Command

```bash
# Launch with all common options
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.medium \
    --key-name my-key-pair \
    --security-group-ids sg-0123456789abcdef0 \
    --subnet-id subnet-0123456789abcdef0 \
    --count 1 \
    --associate-public-ip-address \
    --iam-instance-profile Name=MyInstanceRole \
    --block-device-mappings '[
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "VolumeSize": 20,
                "VolumeType": "gp3",
                "DeleteOnTermination": true,
                "Encrypted": true
            }
        },
        {
            "DeviceName": "/dev/xvdb",
            "Ebs": {
                "VolumeSize": 100,
                "VolumeType": "gp3",
                "DeleteOnTermination": false,
                "Encrypted": true
            }
        }
    ]' \
    --tag-specifications '[
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": "web-server-01"},
                {"Key": "Environment", "Value": "Production"}
            ]
        },
        {
            "ResourceType": "volume",
            "Tags": [
                {"Key": "Name", "Value": "web-server-01-volume"}
            ]
        }
    ]' \
    --user-data file://user-data.sh \
    --metadata-options "HttpTokens=required,HttpEndpoint=enabled" \
    --disable-api-termination
```

### Launch Multiple Instances

```bash
# Launch 3 identical instances
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --key-name my-key-pair \
    --security-group-ids sg-0123456789abcdef0 \
    --subnet-id subnet-0123456789abcdef0 \
    --count 3 \
    --tag-specifications '[
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": "web-cluster"},
                {"Key": "Role", "Value": "WebServer"}
            ]
        }
    ]'
```

---

## User Data Scripts

### What is User Data?

User data is a script that runs automatically when an EC2 instance launches for the first time. It's used for:
- Installing software
- Applying configurations
- Downloading application code
- Starting services

### User Data Execution

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Data Execution Flow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Instance launches                                            │
│         │                                                        │
│         ▼                                                        │
│  2. cloud-init runs (Linux) or EC2Launch (Windows)              │
│         │                                                        │
│         ▼                                                        │
│  3. User data script fetched from metadata service               │
│         │                                                        │
│         ▼                                                        │
│  4. Script executed as root (Linux) or Administrator (Windows)  │
│         │                                                        │
│         ▼                                                        │
│  5. Output logged to /var/log/cloud-init-output.log             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Linux User Data Examples

#### Basic Web Server Setup

```bash
#!/bin/bash
# Update system
yum update -y

# Install Apache
yum install -y httpd

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Create a simple webpage
cat << 'EOF' > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to EC2</title>
</head>
<body>
    <h1>Hello from EC2!</h1>
    <p>Instance ID: INSTANCE_ID</p>
    <p>Availability Zone: AZ</p>
</body>
</html>
EOF

# Get instance metadata and update HTML
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)

sed -i "s/INSTANCE_ID/$INSTANCE_ID/g" /var/www/html/index.html
sed -i "s/AZ/$AZ/g" /var/www/html/index.html
```

#### LAMP Stack Setup

```bash
#!/bin/bash
# Install LAMP stack on Amazon Linux 2023

# Update system
dnf update -y

# Install Apache
dnf install -y httpd
systemctl start httpd
systemctl enable httpd

# Install MariaDB
dnf install -y mariadb105-server
systemctl start mariadb
systemctl enable mariadb

# Install PHP
dnf install -y php php-mysqlnd php-fpm
systemctl start php-fpm
systemctl enable php-fpm

# Secure MariaDB (set root password)
mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';"
mysql -e "DELETE FROM mysql.user WHERE User='';"
mysql -e "DROP DATABASE IF EXISTS test;"
mysql -e "FLUSH PRIVILEGES;"

# Create PHP info page
echo "<?php phpinfo(); ?>" > /var/www/html/info.php

# Set permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Restart Apache to load PHP
systemctl restart httpd
```

#### Node.js Application Deployment

```bash
#!/bin/bash
# Deploy Node.js application

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# Install PM2 for process management
npm install -g pm2

# Create application directory
mkdir -p /opt/app
cd /opt/app

# Download application from S3
aws s3 cp s3://my-bucket/app.tar.gz .
tar -xzf app.tar.gz

# Install dependencies
npm install --production

# Start application with PM2
pm2 start app.js --name "my-app"
pm2 startup
pm2 save

# Configure nginx as reverse proxy
yum install -y nginx
cat << 'EOF' > /etc/nginx/conf.d/app.conf
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

systemctl start nginx
systemctl enable nginx
```

#### Docker Installation

```bash
#!/bin/bash
# Install and configure Docker

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -aG docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Pull and run a container
docker pull nginx:latest
docker run -d -p 80:80 --name web nginx

# Log into ECR (if using private registry)
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### Windows User Data Examples

#### IIS Web Server Setup

```powershell
<powershell>
# Install IIS
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Create a simple webpage
$instanceId = Invoke-RestMethod -Uri http://169.254.169.254/latest/meta-data/instance-id
$content = @"
<!DOCTYPE html>
<html>
<head>
    <title>Windows EC2</title>
</head>
<body>
    <h1>Hello from Windows EC2!</h1>
    <p>Instance ID: $instanceId</p>
</body>
</html>
"@

Set-Content -Path "C:\inetpub\wwwroot\index.html" -Value $content

# Open firewall for HTTP
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Port 80 -Protocol TCP -Action Allow
</powershell>
```

#### Join Active Directory

```powershell
<powershell>
# Set computer name
$instanceId = Invoke-RestMethod -Uri http://169.254.169.254/latest/meta-data/instance-id
Rename-Computer -NewName "WEB-$instanceId" -Force

# Install AD tools
Install-WindowsFeature RSAT-AD-PowerShell

# Join domain
$domain = "mydomain.local"
$password = ConvertTo-SecureString "DomainPassword123!" -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential ("MYDOMAIN\admin", $password)
Add-Computer -DomainName $domain -Credential $credential -Restart -Force
</powershell>
```

### User Data Best Practices

```bash
#!/bin/bash
# Best Practices Example

# 1. Exit on any error
set -e

# 2. Enable logging
exec > >(tee /var/log/user-data.log) 2>&1
echo "User data script started at $(date)"

# 3. Use IMDSv2
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
REGION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/placement/region)

# 4. Signal CloudFormation (if using)
# /opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource MyInstance --region ${AWS::Region}

# 5. Handle errors gracefully
install_package() {
    local package=$1
    local max_attempts=3
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if yum install -y "$package"; then
            echo "Successfully installed $package"
            return 0
        fi
        echo "Attempt $attempt failed, retrying..."
        ((attempt++))
        sleep 5
    done

    echo "Failed to install $package after $max_attempts attempts"
    return 1
}

# 6. Store secrets in Secrets Manager, not user data
DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id my-db-password \
    --query SecretString \
    --output text \
    --region $REGION)

echo "User data script completed at $(date)"
```

---

## Instance Metadata Service (IMDS)

### What is IMDS?

The Instance Metadata Service provides information about a running instance that can be used to configure or manage the instance.

### IMDS Endpoints

```
http://169.254.169.254/latest/meta-data/        # Instance metadata
http://169.254.169.254/latest/user-data         # User data script
http://169.254.169.254/latest/dynamic/          # Dynamic data
```

### IMDSv1 vs IMDSv2

| Feature | IMDSv1 | IMDSv2 |
|---------|--------|--------|
| Method | Simple GET | Session-based (PUT + GET) |
| Security | Vulnerable to SSRF | Protected against SSRF |
| Hop Limit | No restriction | Default 1 (configurable) |
| Recommendation | Legacy | **Always use IMDSv2** |

### IMDSv2 Usage

```bash
# Step 1: Get a session token
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Step 2: Use token for all metadata requests
# Get instance ID
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/instance-id

# Get instance type
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/instance-type

# Get AMI ID
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/ami-id

# Get security groups
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/security-groups

# Get IAM role name
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Get IAM role credentials
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/iam/security-credentials/MyRole
```

### Available Metadata Categories

```bash
# List all metadata categories
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/

# Common categories:
# ami-id                     - AMI ID used to launch instance
# ami-launch-index           - Instance launch index
# hostname                   - Private hostname
# instance-id                - Instance ID
# instance-type              - Instance type
# local-ipv4                 - Private IP address
# mac                        - MAC address
# network/                   - Network interface info
# placement/                 - Region and AZ
# public-hostname            - Public DNS name
# public-ipv4                - Public IP address
# security-groups            - Security group names
# iam/                       - IAM role information
# block-device-mapping/      - Block device mapping
# tags/                      - Instance tags (if enabled)
```

### Enable IMDS Tags

```bash
# Enable instance tags in metadata
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --instance-metadata-tags enabled

# Access tags via IMDS
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/tags/instance/Name
```

### Require IMDSv2

```bash
# Enforce IMDSv2 on new instance
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --metadata-options "HttpTokens=required,HttpEndpoint=enabled"

# Modify existing instance to require IMDSv2
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --http-tokens required \
    --http-endpoint enabled
```

---

## CloudFormation Template

### Complete EC2 Instance with User Data

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Launch EC2 instance with user data'

Parameters:
  EnvironmentName:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t3.medium, m5.large]

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Name of an existing EC2 key pair

  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC to launch into

  SubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: Subnet to launch into

Mappings:
  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      VolumeSize: 20
    staging:
      InstanceType: t3.small
      VolumeSize: 30
    prod:
      InstanceType: m5.large
      VolumeSize: 50

Resources:
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web server
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
          Description: SSH access
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP access
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS access
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-web-sg'

  InstanceRole:
    Type: AWS::IAM::Role
    Properties:
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
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-instance-role'

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref InstanceRole

  WebServer:
    Type: AWS::EC2::Instance
    Metadata:
      AWS::CloudFormation::Init:
        config:
          packages:
            yum:
              httpd: []
              php: []
          files:
            /var/www/html/index.html:
              content: !Sub |
                <!DOCTYPE html>
                <html>
                <head><title>Welcome</title></head>
                <body>
                    <h1>Hello from ${EnvironmentName}!</h1>
                    <p>Stack: ${AWS::StackName}</p>
                    <p>Region: ${AWS::Region}</p>
                </body>
                </html>
              mode: '000644'
              owner: apache
              group: apache
          services:
            sysvinit:
              httpd:
                enabled: true
                ensureRunning: true
    Properties:
      ImageId: '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}'
      InstanceType: !FindInMap [EnvironmentConfig, !Ref EnvironmentName, InstanceType]
      KeyName: !Ref KeyName
      IamInstanceProfile: !Ref InstanceProfile
      SubnetId: !Ref SubnetId
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: !FindInMap [EnvironmentConfig, !Ref EnvironmentName, VolumeSize]
            VolumeType: gp3
            Encrypted: true
            DeleteOnTermination: true
      MetadataOptions:
        HttpTokens: required
        HttpEndpoint: enabled
        InstanceMetadataTags: enabled
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash -xe
          # Update and install cfn-bootstrap
          yum update -y
          yum install -y aws-cfn-bootstrap

          # Run cfn-init
          /opt/aws/bin/cfn-init -v \
              --stack ${AWS::StackName} \
              --resource WebServer \
              --region ${AWS::Region}

          # Signal completion
          /opt/aws/bin/cfn-signal -e $? \
              --stack ${AWS::StackName} \
              --resource WebServer \
              --region ${AWS::Region}
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-web-server'
        - Key: Environment
          Value: !Ref EnvironmentName
    CreationPolicy:
      ResourceSignal:
        Count: 1
        Timeout: PT10M

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref WebServer
    Export:
      Name: !Sub '${AWS::StackName}-InstanceId'

  PublicIP:
    Description: Public IP address
    Value: !GetAtt WebServer.PublicIp

  PublicDNS:
    Description: Public DNS name
    Value: !GetAtt WebServer.PublicDnsName

  WebsiteURL:
    Description: Website URL
    Value: !Sub 'http://${WebServer.PublicDnsName}'
```

---

## Troubleshooting Launch Issues

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| InsufficientInstanceCapacity | No capacity in AZ | Try different AZ or instance type |
| InstanceLimitExceeded | Account limit reached | Request limit increase |
| InvalidAMI | AMI not found/available | Check AMI ID and region |
| InvalidSubnetID | Subnet doesn't exist | Verify subnet ID |
| InvalidKeyPair | Key pair not found | Create or use existing key pair |
| Unauthorized | IAM permission denied | Check IAM policies |

### Debugging User Data Issues

```bash
# Check cloud-init logs
sudo cat /var/log/cloud-init.log
sudo cat /var/log/cloud-init-output.log

# Check user data execution
sudo cat /var/lib/cloud/instance/user-data.txt

# Re-run cloud-init manually
sudo cloud-init clean
sudo cloud-init init

# Check if user data ran
sudo cloud-init status

# View cloud-init errors
sudo cat /var/log/cloud-init.log | grep -i error
```

### Instance Connect Issues

```bash
# Verify instance is running
aws ec2 describe-instance-status \
    --instance-ids i-1234567890abcdef0 \
    --query 'InstanceStatuses[0].[InstanceState.Name,SystemStatus.Status,InstanceStatus.Status]'

# Check security group allows SSH
aws ec2 describe-security-groups \
    --group-ids sg-0123456789abcdef0 \
    --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]'

# Get console output
aws ec2 get-console-output \
    --instance-id i-1234567890abcdef0 \
    --output text
```

---

## Key Takeaways

1. **Launch Wizard** provides a comprehensive GUI for launching instances
2. **User Data** scripts run once at first boot - use for initial configuration
3. **IMDSv2** is more secure and should always be used
4. **Tags** help organize resources and enable cost allocation
5. **IAM Roles** provide secure access to AWS services without storing credentials
6. **CloudFormation Init** provides advanced configuration management
7. Always **test user data scripts** before using in production

---

## Next Steps

Continue to [04-storage-options.md](./04-storage-options.md) to learn about EBS volumes and storage options for EC2.
