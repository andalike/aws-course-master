# 06 - Key Pairs and Access Methods

## Overview

Accessing EC2 instances securely is fundamental to managing your infrastructure. AWS provides multiple access methods, each suited for different scenarios and security requirements.

```
┌─────────────────────────────────────────────────────────────────┐
│                    EC2 Access Methods                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   SSH Keys      │  │ EC2 Instance    │  │ Session Manager │  │
│  │   (Linux)       │  │ Connect         │  │ (SSM)           │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   RDP           │  │ Serial Console  │  │ EC2 Connect     │  │
│  │   (Windows)     │  │ (Troubleshoot)  │  │ Endpoint        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## SSH Key Pairs

### What are Key Pairs?

Key pairs consist of a public key (stored by AWS) and a private key (stored by you). They use asymmetric cryptography for secure authentication.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Key Pair Authentication                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Your Computer                    EC2 Instance                  │
│   ┌────────────────┐              ┌────────────────┐            │
│   │ Private Key    │              │ Public Key     │            │
│   │ (my-key.pem)   │──────────────│ (authorized_   │            │
│   │                │  Challenge/  │  keys)         │            │
│   │ KEEP SECRET!   │  Response    │                │            │
│   └────────────────┘              └────────────────┘            │
│                                                                  │
│   1. Client initiates connection                                │
│   2. Server sends challenge                                     │
│   3. Client signs challenge with private key                    │
│   4. Server verifies with public key                            │
│   5. Access granted                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Creating Key Pairs

#### Using AWS Console

1. Navigate to **EC2** > **Key Pairs**
2. Click **Create key pair**
3. Enter name and choose format:
   - **.pem** for Linux/macOS (OpenSSH)
   - **.ppk** for Windows (PuTTY)
4. Download and store securely

#### Using AWS CLI

```bash
# Create key pair and save private key
aws ec2 create-key-pair \
    --key-name my-key-pair \
    --key-type rsa \
    --key-format pem \
    --query 'KeyMaterial' \
    --output text > my-key-pair.pem

# Set correct permissions (Linux/macOS)
chmod 400 my-key-pair.pem

# Create ED25519 key pair (more secure)
aws ec2 create-key-pair \
    --key-name my-ed25519-key \
    --key-type ed25519 \
    --query 'KeyMaterial' \
    --output text > my-ed25519-key.pem
```

#### Import Existing Key

```bash
# Generate key pair locally
ssh-keygen -t rsa -b 4096 -f my-key-pair

# Import public key to AWS
aws ec2 import-key-pair \
    --key-name my-imported-key \
    --public-key-material fileb://my-key-pair.pub
```

### Managing Key Pairs

```bash
# List key pairs
aws ec2 describe-key-pairs \
    --query 'KeyPairs[*].[KeyName,KeyType,CreateTime]' \
    --output table

# Delete key pair
aws ec2 delete-key-pair --key-name my-key-pair

# Get key pair fingerprint
aws ec2 describe-key-pairs \
    --key-names my-key-pair \
    --query 'KeyPairs[0].KeyFingerprint'
```

---

## Connecting from Different Operating Systems

### Linux/macOS

```bash
# Basic SSH connection
ssh -i /path/to/key.pem ec2-user@ec2-ip-address

# For Amazon Linux, RHEL, Fedora
ssh -i my-key.pem ec2-user@54.123.45.67

# For Ubuntu
ssh -i my-key.pem ubuntu@54.123.45.67

# For Debian
ssh -i my-key.pem admin@54.123.45.67

# For SUSE
ssh -i my-key.pem ec2-user@54.123.45.67

# With verbose output (debugging)
ssh -i my-key.pem -v ec2-user@54.123.45.67

# Using specific port
ssh -i my-key.pem -p 22 ec2-user@54.123.45.67

# SSH config file (~/.ssh/config)
cat << 'EOF' >> ~/.ssh/config
Host my-ec2
    HostName 54.123.45.67
    User ec2-user
    IdentityFile ~/.ssh/my-key.pem
    Port 22
EOF

# Now connect with
ssh my-ec2
```

### Windows (PowerShell/OpenSSH)

```powershell
# Windows 10+ has built-in OpenSSH
ssh -i C:\path\to\key.pem ec2-user@54.123.45.67

# Set correct permissions on key file
icacls.exe "C:\path\to\key.pem" /reset
icacls.exe "C:\path\to\key.pem" /grant:r "$($env:USERNAME):(R)"
icacls.exe "C:\path\to\key.pem" /inheritance:r
```

### Windows (PuTTY)

```
1. Convert .pem to .ppk using PuTTYgen:
   - Open PuTTYgen
   - Load .pem file
   - Save as .ppk file

2. Configure PuTTY:
   - Host Name: ec2-user@54.123.45.67
   - Connection > SSH > Auth > Credentials: Browse to .ppk file
   - Save session for future use

3. Click Open to connect
```

---

## EC2 Instance Connect

### What is EC2 Instance Connect?

EC2 Instance Connect provides a simple and secure way to connect to instances using SSH without managing key pairs. It pushes a temporary public key to instance metadata.

### Requirements

- Amazon Linux 2, Amazon Linux 2023, or Ubuntu 16.04+
- EC2 Instance Connect package installed
- Security group allows SSH (port 22)
- Instance has public IP or accessible via VPC endpoint

### Using EC2 Instance Connect

#### From Console

1. Select instance in EC2 console
2. Click **Connect**
3. Choose **EC2 Instance Connect**
4. Click **Connect**

#### Using AWS CLI

```bash
# Send SSH public key to instance
aws ec2-instance-connect send-ssh-public-key \
    --instance-id i-1234567890abcdef0 \
    --instance-os-user ec2-user \
    --ssh-public-key file://my-key.pub

# Connect within 60 seconds
ssh -i my-key ec2-user@54.123.45.67

# Using mssh (EC2 Instance Connect CLI)
pip install ec2instanceconnectcli
mssh ec2-user@i-1234567890abcdef0
```

### EC2 Instance Connect Endpoint

For private instances without public IPs:

```bash
# Create EC2 Instance Connect Endpoint
aws ec2 create-instance-connect-endpoint \
    --subnet-id subnet-12345678 \
    --security-group-ids sg-12345678

# Connect to private instance
aws ec2-instance-connect ssh \
    --instance-id i-1234567890abcdef0 \
    --os-user ec2-user
```

---

## AWS Systems Manager Session Manager

### What is Session Manager?

Session Manager provides secure shell access without opening inbound ports, managing SSH keys, or using bastion hosts.

### Benefits

| Benefit | Description |
|---------|-------------|
| No SSH Keys | No key management required |
| No Bastion | Direct access to private instances |
| No Port 22 | No inbound SSH port needed |
| Audit Logging | Session activity logged to CloudWatch/S3 |
| IAM Integration | Access controlled via IAM policies |
| Cross-Platform | Works with Linux and Windows |

### Prerequisites

```bash
# 1. Install SSM Agent (pre-installed on Amazon Linux 2+)
# For other Linux:
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent

# 2. IAM Role with SSM permissions
# Attach AmazonSSMManagedInstanceCore policy to instance role
```

### IAM Role for Session Manager

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:StartSession",
                "ssm:TerminateSession",
                "ssm:ResumeSession"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:instance/*",
                "arn:aws:ssm:*::document/AWS-StartSSHSession",
                "arn:aws:ssm:*::document/AWS-StartPortForwardingSession"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeSessions",
                "ssm:GetConnectionStatus",
                "ssm:DescribeInstanceProperties",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

### Using Session Manager

#### From Console

1. Select instance in EC2 console
2. Click **Connect**
3. Choose **Session Manager**
4. Click **Connect**

#### Using AWS CLI

```bash
# Install Session Manager plugin
# macOS
brew install session-manager-plugin

# Linux (64-bit)
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb

# Start session
aws ssm start-session --target i-1234567890abcdef0

# Start session with port forwarding
aws ssm start-session \
    --target i-1234567890abcdef0 \
    --document-name AWS-StartPortForwardingSession \
    --parameters '{"portNumber":["3306"],"localPortNumber":["3306"]}'

# SSH over Session Manager
# Add to ~/.ssh/config:
Host i-* mi-*
    ProxyCommand sh -c "aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'"

# Then use SSH normally
ssh -i my-key.pem ec2-user@i-1234567890abcdef0
```

### Session Manager Logging

```bash
# Enable session logging in Systems Manager console
# Or via AWS CLI:

aws ssm update-document \
    --name "SSM-SessionManagerRunShell" \
    --content '{
        "schemaVersion": "1.0",
        "description": "Session Manager settings",
        "sessionType": "Standard_Stream",
        "inputs": {
            "s3BucketName": "my-session-logs-bucket",
            "s3KeyPrefix": "session-logs",
            "cloudWatchLogGroupName": "/aws/ssm/session-logs",
            "cloudWatchEncryptionEnabled": true,
            "runAsEnabled": true,
            "runAsDefaultUser": "ssm-user"
        }
    }' \
    --document-version "\$LATEST"
```

---

## Remote Desktop Protocol (RDP) for Windows

### Getting Windows Password

```bash
# Get Windows administrator password
aws ec2 get-password-data \
    --instance-id i-1234567890abcdef0 \
    --priv-launch-key my-key.pem
```

### Connecting to Windows Instances

#### From Windows

1. Open Remote Desktop Connection
2. Enter instance public IP
3. Enter credentials:
   - Username: Administrator
   - Password: (from get-password-data)

#### From macOS

```bash
# Install Microsoft Remote Desktop from App Store
# Or use command line
open rdp://full%20address=s:54.123.45.67

# With credentials
open "rdp://full%20address=s:54.123.45.67&username=s:Administrator"
```

#### From Linux

```bash
# Install rdesktop or Remmina
sudo apt-get install remmina remmina-plugin-rdp

# Connect with rdesktop
rdesktop -u Administrator -p 'password' 54.123.45.67

# Or use xfreerdp
xfreerdp /v:54.123.45.67 /u:Administrator /p:'password'
```

---

## EC2 Serial Console

### What is Serial Console?

EC2 Serial Console provides text-based access to an instance's serial port for troubleshooting boot and network issues.

### When to Use

- Instance unreachable via SSH
- Boot problems
- Network configuration issues
- GRUB/kernel debugging

### Enabling Serial Console

```bash
# Enable for account (one-time)
aws ec2 enable-serial-console-access

# Check status
aws ec2 get-serial-console-access-status

# Instance must be Nitro-based
# Enable enhanced networking
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --ena-support
```

### Using Serial Console

```bash
# Connect via AWS CLI
aws ec2-instance-connect send-serial-console-ssh-public-key \
    --instance-id i-1234567890abcdef0 \
    --serial-port 0 \
    --ssh-public-key file://my-key.pub

# Connect via SSH
ssh -i my-key i-1234567890abcdef0.port0@serial-console.ec2-instance-connect.us-east-1.aws

# Or use console:
# EC2 > Instance > Connect > EC2 Serial Console
```

---

## Best Practices

### Key Management

| Practice | Description |
|----------|-------------|
| Never share private keys | Each user should have their own key |
| Use ED25519 | More secure than RSA |
| Rotate keys regularly | Replace old keys periodically |
| Store securely | Use secrets manager or HSM |
| Disable unused keys | Remove from instances when not needed |
| Use IAM for access | Session Manager with IAM is preferred |

### Access Control

```bash
# Restrict SSH to specific users
# /etc/ssh/sshd_config
AllowUsers ec2-user admin
DenyUsers root

# Disable password authentication
PasswordAuthentication no

# Disable root login
PermitRootLogin no

# Use specific authorized_keys location
AuthorizedKeysFile /etc/ssh/authorized_keys/%u
```

### Security Recommendations

```
┌─────────────────────────────────────────────────────────────────┐
│                    Access Method Comparison                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Method              Security    Audit     Ease      Recommend  │
│  ──────────────────────────────────────────────────────────────│
│  SSH Keys            Medium      No        Easy      Dev/Test   │
│  EC2 Instance Connect High       Yes       Easy      Good       │
│  Session Manager     Highest     Yes       Easy      Production │
│  Bastion + SSH       High        Partial   Complex   Legacy     │
│                                                                  │
│  Recommendation: Use Session Manager for production workloads   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## CloudFormation for Access Configuration

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 Instance with Session Manager Access'

Parameters:
  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: SSH Key Pair (optional, for SSH access)

Resources:
  # IAM Role for Session Manager
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
      Policies:
        - PolicyName: SessionManagerLogging
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:PutObjectAcl
                Resource: !Sub 'arn:aws:s3:::${SessionLogBucket}/*'
              - Effect: Allow
                Action:
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogGroups
                  - logs:DescribeLogStreams
                Resource: '*'

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref InstanceRole

  # Security Group - No SSH needed for Session Manager
  InstanceSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Instance security group
      VpcId: !Ref VpcId
      # Note: No inbound SSH rule needed for Session Manager
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS for SSM endpoint
      Tags:
        - Key: Name
          Value: session-manager-sg

  # S3 Bucket for Session Logs
  SessionLogBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'session-logs-${AWS::AccountId}'
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # CloudWatch Log Group for Sessions
  SessionLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/ssm/session-logs
      RetentionInDays: 30

  # EC2 Instance
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}'
      InstanceType: t3.micro
      IamInstanceProfile: !Ref InstanceProfile
      SecurityGroupIds:
        - !Ref InstanceSecurityGroup
      KeyName: !Ref KeyName  # Optional - not needed for Session Manager
      Tags:
        - Key: Name
          Value: session-manager-instance

  # VPC Endpoints for Session Manager (if in private subnet)
  SSMEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub 'com.amazonaws.${AWS::Region}.ssm'
      VpcId: !Ref VpcId
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref PrivateSubnetId
      SecurityGroupIds:
        - !Ref EndpointSecurityGroup

  SSMMessagesEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub 'com.amazonaws.${AWS::Region}.ssmmessages'
      VpcId: !Ref VpcId
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref PrivateSubnetId
      SecurityGroupIds:
        - !Ref EndpointSecurityGroup

  EC2MessagesEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ServiceName: !Sub 'com.amazonaws.${AWS::Region}.ec2messages'
      VpcId: !Ref VpcId
      VpcEndpointType: Interface
      SubnetIds:
        - !Ref PrivateSubnetId
      SecurityGroupIds:
        - !Ref EndpointSecurityGroup
```

---

## Troubleshooting

### SSH Connection Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Permission denied | Wrong key | Verify key pair matches |
| Connection timed out | Security group | Check inbound SSH rule |
| Connection refused | SSH not running | Check sshd service |
| Host key changed | Instance replaced | Remove old key from known_hosts |

### Debugging SSH

```bash
# Verbose SSH connection
ssh -vvv -i my-key.pem ec2-user@54.123.45.67

# Check SSH daemon status
sudo systemctl status sshd

# Check SSH logs
sudo tail -f /var/log/secure  # Amazon Linux
sudo tail -f /var/log/auth.log  # Ubuntu

# Test connectivity
nc -zv 54.123.45.67 22

# Check authorized keys
cat ~/.ssh/authorized_keys
```

### Session Manager Issues

```bash
# Check SSM agent status
sudo systemctl status amazon-ssm-agent

# Check SSM agent logs
sudo tail -f /var/log/amazon/ssm/amazon-ssm-agent.log

# Verify IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test SSM connectivity
aws ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=i-1234567890abcdef0"
```

---

## Key Takeaways

1. **Use Session Manager** for production - no keys, full audit logging
2. **EC2 Instance Connect** is great for quick, secure access
3. **SSH keys** are still useful for development and automation
4. **Never share private keys** - each user gets their own
5. **Use ED25519 keys** for better security than RSA
6. **Enable session logging** for compliance and troubleshooting
7. **VPC endpoints** enable Session Manager for private instances

---

## Next Steps

Continue to [07-elastic-ips-and-eni.md](./07-elastic-ips-and-eni.md) to learn about EC2 networking components.
