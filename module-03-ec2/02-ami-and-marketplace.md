# 02 - Amazon Machine Images (AMI) and AWS Marketplace

## What is an Amazon Machine Image (AMI)?

An Amazon Machine Image (AMI) is a template that contains the software configuration (operating system, application server, and applications) required to launch an EC2 instance. Think of it as a "snapshot" or "blueprint" of a server that you can use to create multiple identical instances.

### AMI Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Amazon Machine Image (AMI)                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Root Volume Template                  │    │
│  │  • Operating System (Linux, Windows, etc.)              │    │
│  │  • Installed Applications                                │    │
│  │  • Configuration Files                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Launch Permissions                    │    │
│  │  • Public: Available to all AWS accounts                 │    │
│  │  • Private: Only your account (default)                  │    │
│  │  • Shared: Specific AWS accounts                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                Block Device Mapping                      │    │
│  │  • Specifies EBS volumes to attach                       │    │
│  │  • Volume sizes and types                                │    │
│  │  • Delete on termination settings                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### AMI Characteristics

| Characteristic | Description |
|---------------|-------------|
| Region-specific | AMIs are created in and belong to a specific region |
| Architecture | x86_64 (Intel/AMD) or arm64 (Graviton) |
| Virtualization | HVM (Hardware Virtual Machine) or PV (Paravirtual) |
| Root Device | EBS-backed or Instance Store-backed |
| Boot Mode | UEFI, Legacy BIOS, or UEFI Preferred |

---

## Types of AMIs

### 1. AWS-Provided AMIs

Quick Start AMIs provided and maintained by AWS:

| AMI Type | Description | Use Case |
|----------|-------------|----------|
| Amazon Linux 2023 | AWS-optimized Linux | Production workloads |
| Amazon Linux 2 | Previous generation | Legacy compatibility |
| Ubuntu | Canonical Ubuntu Server | Development, containers |
| Red Hat Enterprise Linux | Enterprise RHEL | Enterprise applications |
| SUSE Linux Enterprise | SUSE Linux | SAP workloads |
| Windows Server 2019/2022 | Microsoft Windows | Windows applications |
| macOS | Apple macOS | iOS/macOS development |

### 2. AWS Marketplace AMIs

Pre-configured AMIs from third-party vendors:

| Category | Examples |
|----------|----------|
| Security | Trend Micro, Palo Alto, Fortinet |
| Databases | Oracle, SQL Server, MongoDB |
| DevOps | Jenkins, GitLab, Atlassian |
| CMS | WordPress, Drupal, Magento |
| Machine Learning | NVIDIA, Databricks |

### 3. Community AMIs

AMIs shared publicly by the AWS community:

- Free to use (you pay for EC2 resources)
- No AWS support
- Use with caution (verify source)

### 4. Custom AMIs

AMIs you create from your own instances:

- Tailored to your requirements
- Pre-installed applications
- Custom configurations
- Golden images for standardization

---

## Finding AMIs

### Using AWS Console

1. Navigate to **EC2 Dashboard**
2. Click **AMIs** in the left navigation
3. Use filters:
   - Owner: Amazon, AWS Marketplace, My AMIs, Community
   - Platform: Linux, Windows
   - Architecture: x86_64, arm64

### Using AWS CLI

```bash
# List Amazon Linux 2023 AMIs
aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-*" \
              "Name=architecture,Values=x86_64" \
              "Name=virtualization-type,Values=hvm" \
    --query 'Images | sort_by(@, &CreationDate) | [-1]' \
    --output json

# List Ubuntu AMIs
aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text

# List Windows Server 2022 AMIs
aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=Windows_Server-2022-English-Full-Base-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text

# Find Red Hat AMIs
aws ec2 describe-images \
    --owners 309956199498 \
    --filters "Name=name,Values=RHEL-9*" \
    --query 'sort_by(Images, &CreationDate)[-1]' \
    --output json
```

### SSM Parameter Store (Recommended for Automation)

AWS publishes the latest AMI IDs to Systems Manager Parameter Store:

```bash
# Get latest Amazon Linux 2023 AMI
aws ssm get-parameter \
    --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64 \
    --query 'Parameter.Value' \
    --output text

# Get latest Amazon Linux 2 AMI
aws ssm get-parameter \
    --name /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
    --query 'Parameter.Value' \
    --output text

# Get latest Ubuntu 22.04 AMI
aws ssm get-parameter \
    --name /aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id \
    --query 'Parameter.Value' \
    --output text

# List all available Amazon Linux parameters
aws ssm get-parameters-by-path \
    --path /aws/service/ami-amazon-linux-latest \
    --query 'Parameters[*].[Name,Value]' \
    --output table
```

---

## Creating Custom AMIs

### Method 1: Create from Running Instance (Console)

1. Select running instance in EC2 console
2. **Actions** > **Image and templates** > **Create image**
3. Configure:
   - Image name and description
   - No reboot option (creates consistent image, brief downtime)
   - Add additional EBS volumes if needed
4. Click **Create image**

### Method 2: Create from Running Instance (CLI)

```bash
# Create AMI from instance (with reboot for consistency)
aws ec2 create-image \
    --instance-id i-1234567890abcdef0 \
    --name "my-web-server-ami-$(date +%Y%m%d)" \
    --description "Web server with Apache and PHP installed" \
    --tag-specifications 'ResourceType=image,Tags=[{Key=Environment,Value=Production},{Key=Application,Value=WebServer}]'

# Create AMI without reboot (may have inconsistent filesystem)
aws ec2 create-image \
    --instance-id i-1234567890abcdef0 \
    --name "my-ami-no-reboot" \
    --no-reboot

# Check AMI creation status
aws ec2 describe-images \
    --image-ids ami-0123456789abcdef0 \
    --query 'Images[0].State'
```

### Method 3: Using EC2 Image Builder

EC2 Image Builder automates the creation, maintenance, and deployment of customized AMIs.

```yaml
# Image Builder CloudFormation Example
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 Image Builder Pipeline'

Resources:
  ImageRecipe:
    Type: AWS::ImageBuilder::ImageRecipe
    Properties:
      Name: WebServerRecipe
      Version: 1.0.0
      ParentImage: !Sub 'arn:aws:imagebuilder:${AWS::Region}:aws:image/amazon-linux-2023-x86/x.x.x'
      Components:
        - ComponentArn: !Sub 'arn:aws:imagebuilder:${AWS::Region}:aws:component/update-linux/x.x.x'
        - ComponentArn: !Sub 'arn:aws:imagebuilder:${AWS::Region}:aws:component/apache-tomcat-8-linux/x.x.x'

  InfrastructureConfiguration:
    Type: AWS::ImageBuilder::InfrastructureConfiguration
    Properties:
      Name: WebServerInfra
      InstanceTypes:
        - t3.medium
      SubnetId: !Ref SubnetId

  ImagePipeline:
    Type: AWS::ImageBuilder::ImagePipeline
    Properties:
      Name: WebServerPipeline
      ImageRecipeArn: !Ref ImageRecipe
      InfrastructureConfigurationArn: !Ref InfrastructureConfiguration
      Schedule:
        ScheduleExpression: 'cron(0 0 * * ? *)'
        PipelineExecutionStartCondition: EXPRESSION_MATCH_ONLY
```

---

## AMI Lifecycle Management

### Sharing AMIs

```bash
# Share AMI with specific AWS account
aws ec2 modify-image-attribute \
    --image-id ami-0123456789abcdef0 \
    --launch-permission "Add=[{UserId=123456789012}]"

# Make AMI public (use with caution!)
aws ec2 modify-image-attribute \
    --image-id ami-0123456789abcdef0 \
    --launch-permission "Add=[{Group=all}]"

# Remove sharing
aws ec2 modify-image-attribute \
    --image-id ami-0123456789abcdef0 \
    --launch-permission "Remove=[{UserId=123456789012}]"

# View current permissions
aws ec2 describe-image-attribute \
    --image-id ami-0123456789abcdef0 \
    --attribute launchPermission
```

### Copying AMIs Across Regions

```bash
# Copy AMI to another region
aws ec2 copy-image \
    --source-region us-east-1 \
    --source-image-id ami-0123456789abcdef0 \
    --region us-west-2 \
    --name "my-ami-us-west-2-copy" \
    --description "Copy of my-ami from us-east-1"

# Copy with encryption
aws ec2 copy-image \
    --source-region us-east-1 \
    --source-image-id ami-0123456789abcdef0 \
    --region us-west-2 \
    --name "my-ami-encrypted" \
    --encrypted \
    --kms-key-id alias/my-key
```

### Deregistering (Deleting) AMIs

```bash
# First, find the snapshot IDs associated with the AMI
aws ec2 describe-images \
    --image-ids ami-0123456789abcdef0 \
    --query 'Images[0].BlockDeviceMappings[*].Ebs.SnapshotId' \
    --output text

# Deregister the AMI
aws ec2 deregister-image --image-id ami-0123456789abcdef0

# Delete associated snapshots (must do separately)
aws ec2 delete-snapshot --snapshot-id snap-0123456789abcdef0
```

### AMI Deprecation

```bash
# Deprecate an AMI (warn users it will be removed)
aws ec2 enable-image-deprecation \
    --image-id ami-0123456789abcdef0 \
    --deprecate-at "2024-12-31T23:59:59Z"

# Check deprecation status
aws ec2 describe-images \
    --image-ids ami-0123456789abcdef0 \
    --query 'Images[0].DeprecationTime'

# Cancel deprecation
aws ec2 disable-image-deprecation \
    --image-id ami-0123456789abcdef0
```

---

## AWS Marketplace

### What is AWS Marketplace?

AWS Marketplace is a digital catalog with thousands of software listings from independent software vendors. It provides:

- Pre-configured AMIs with licensed software
- SaaS applications
- Containers
- Machine learning algorithms
- Data products

### Pricing Models

| Model | Description | Example |
|-------|-------------|---------|
| Free | No software charge | WordPress, many open-source |
| BYOL | Bring Your Own License | Oracle Database |
| Hourly | Pay per hour of use | Trend Micro |
| Monthly | Fixed monthly fee | Splunk |
| Annual | Yearly subscription | Enterprise software |
| Usage-based | Pay for what you use | API calls, data processed |

### Finding Marketplace AMIs

```bash
# Search AWS Marketplace AMIs
aws ec2 describe-images \
    --owners aws-marketplace \
    --filters "Name=name,Values=*wordpress*" \
    --query 'Images[*].[ImageId,Name,Description]' \
    --output table

# Get product code for marketplace AMI
aws ec2 describe-images \
    --image-ids ami-marketplace-id \
    --query 'Images[0].ProductCodes'
```

### Popular Marketplace Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Marketplace Categories                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Security          Infrastructure       Developer Tools         │
│  ├─ Firewalls      ├─ Databases         ├─ IDEs                │
│  ├─ Antivirus      ├─ Storage           ├─ CI/CD               │
│  ├─ WAF            ├─ Networking        ├─ Testing             │
│  └─ SIEM           └─ Monitoring        └─ Version Control     │
│                                                                  │
│  Business Apps     Machine Learning     Operating Systems       │
│  ├─ CRM            ├─ Frameworks        ├─ Linux Distros       │
│  ├─ ERP            ├─ Pre-trained       ├─ Windows Server      │
│  ├─ CMS            │   Models           └─ Container OS        │
│  └─ Analytics      └─ Data Science                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Golden AMI Pattern

### What is a Golden AMI?

A Golden AMI is a standardized, company-approved base image that includes:
- Required security patches
- Monitoring agents
- Compliance configurations
- Standard software packages

### Golden AMI Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Base AMI   │───▶│   Configure  │───▶│   Validate   │
│  (AWS/Vendor)│    │   & Harden   │    │   & Test     │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Approve    │◀───│   Security   │◀───│   Create     │
│   & Publish  │    │   Scan       │    │   AMI        │
└──────────────┘    └──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐
│  Distribute  │
│  to Accounts │
└──────────────┘
```

### Golden AMI Automation Script

```bash
#!/bin/bash
# golden-ami-builder.sh

set -e

# Variables
BASE_AMI="ami-0123456789abcdef0"
INSTANCE_TYPE="t3.medium"
SECURITY_GROUP="sg-0123456789abcdef0"
SUBNET_ID="subnet-0123456789abcdef0"
KEY_NAME="my-key-pair"

# Launch temporary instance
echo "Launching temporary instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $BASE_AMI \
    --instance-type $INSTANCE_TYPE \
    --security-group-ids $SECURITY_GROUP \
    --subnet-id $SUBNET_ID \
    --key-name $KEY_NAME \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=GoldenAMI-Builder}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Instance IP: $PUBLIC_IP"

# Wait for SSH to be available
echo "Waiting for SSH..."
sleep 60

# Run configuration commands via SSH
ssh -o StrictHostKeyChecking=no -i ~/.ssh/my-key.pem ec2-user@$PUBLIC_IP << 'EOF'
    # Update system
    sudo yum update -y

    # Install required packages
    sudo yum install -y \
        aws-cli \
        amazon-cloudwatch-agent \
        amazon-ssm-agent

    # Install security tools
    sudo yum install -y aide
    sudo aide --init

    # Configure CloudWatch agent
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
        -a fetch-config \
        -m ec2 \
        -s

    # Harden SSH
    sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

    # Clean up
    sudo yum clean all
    sudo rm -rf /var/cache/yum
    sudo rm -rf /tmp/*

    # Clear history
    history -c
EOF

# Stop instance for AMI creation
echo "Stopping instance..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

# Create AMI
echo "Creating AMI..."
AMI_NAME="golden-ami-$(date +%Y%m%d-%H%M%S)"
AMI_ID=$(aws ec2 create-image \
    --instance-id $INSTANCE_ID \
    --name "$AMI_NAME" \
    --description "Golden AMI created on $(date)" \
    --tag-specifications "ResourceType=image,Tags=[{Key=Name,Value=$AMI_NAME},{Key=Type,Value=GoldenAMI}]" \
    --query 'ImageId' \
    --output text)

echo "AMI ID: $AMI_ID"

# Wait for AMI to be available
echo "Waiting for AMI to be available..."
aws ec2 wait image-available --image-ids $AMI_ID

# Terminate temporary instance
echo "Terminating temporary instance..."
aws ec2 terminate-instances --instance-ids $INSTANCE_ID

echo "Golden AMI created successfully: $AMI_ID"
```

---

## CloudFormation for AMI Management

### Using Latest AMI with SSM Parameter

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Launch instance with latest Amazon Linux AMI'

Parameters:
  InstanceType:
    Type: String
    Default: t3.micro

Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      # Use SSM parameter for latest AMI
      ImageId: '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}'
      InstanceType: !Ref InstanceType
      Tags:
        - Key: Name
          Value: LatestAMIInstance
```

### AMI with Custom Mapping

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Multi-region AMI mapping'

Mappings:
  RegionAMI:
    us-east-1:
      HVM64: ami-0c55b159cbfafe1f0
      HVM64ARM: ami-0d8d212151031f51c
    us-west-2:
      HVM64: ami-0892d3c7ee96c0bf7
      HVM64ARM: ami-0c29a2c5cf69b5c5c
    eu-west-1:
      HVM64: ami-0d75513e7a9b0e7a7
      HVM64ARM: ami-0ed961fa828560210

Parameters:
  Architecture:
    Type: String
    Default: HVM64
    AllowedValues:
      - HVM64
      - HVM64ARM

Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionAMI, !Ref 'AWS::Region', !Ref Architecture]
      InstanceType: !If [IsARM, t4g.micro, t3.micro]

Conditions:
  IsARM: !Equals [!Ref Architecture, HVM64ARM]
```

---

## Best Practices

### AMI Creation Best Practices

| Practice | Description |
|----------|-------------|
| Clean before capture | Remove logs, temp files, credentials |
| Use consistent naming | Include date, version, purpose |
| Tag comprehensively | Environment, owner, application |
| Document changes | Maintain changelog |
| Test before deploying | Validate in staging first |
| Encrypt sensitive AMIs | Use KMS encryption |

### AMI Security Best Practices

```bash
# Before creating AMI, clean sensitive data:

# Remove SSH host keys (regenerated on boot)
sudo rm -f /etc/ssh/ssh_host_*

# Remove user SSH keys
rm -rf ~/.ssh/authorized_keys

# Clear shell history
history -c
rm -f ~/.bash_history

# Remove AWS credentials (if accidentally placed)
rm -rf ~/.aws/credentials

# Clear cloud-init data (will run on next boot)
sudo rm -rf /var/lib/cloud/instances/*

# Remove temporary files
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Clear logs
sudo rm -rf /var/log/*
```

### AMI Lifecycle Best Practices

1. **Regular Updates**: Create new AMIs with latest patches monthly
2. **Version Control**: Use semantic versioning (v1.0.0, v1.1.0)
3. **Deprecation Policy**: Deprecate old AMIs, give 30-day notice
4. **Cross-Region**: Copy critical AMIs to DR regions
5. **Backup Snapshots**: Keep underlying snapshots for recovery

---

## Troubleshooting

### Common AMI Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| AMI not appearing | Wrong region selected | Check region filter |
| Launch fails | Instance type incompatible | Check AMI architecture |
| Boot fails | Corrupted root volume | Recreate AMI with --no-reboot |
| Missing data | Instance store not included | Use EBS-backed AMI |
| Permission denied | AMI not shared | Check launch permissions |

### Debugging AMI Launch Issues

```bash
# Check AMI details
aws ec2 describe-images --image-ids ami-0123456789abcdef0

# Check instance launch issues
aws ec2 describe-instances \
    --instance-ids i-1234567890abcdef0 \
    --query 'Reservations[0].Instances[0].StateReason'

# Get system log (may show boot errors)
aws ec2 get-console-output \
    --instance-id i-1234567890abcdef0 \
    --output text
```

---

## Key Takeaways

1. **AMIs are region-specific** - Copy to other regions as needed
2. **Use SSM Parameters** for automation to always get latest AMIs
3. **Golden AMIs** ensure consistency and security across your fleet
4. **Clean instances** before creating AMIs to avoid exposing sensitive data
5. **AWS Marketplace** provides pre-configured software solutions
6. **EC2 Image Builder** automates AMI creation and maintenance
7. **Tag and version** your AMIs for better management

---

## Next Steps

Continue to [03-launching-instances.md](./03-launching-instances.md) to learn how to launch EC2 instances step by step.
