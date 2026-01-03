# 05 - Security Groups

## What are Security Groups?

Security groups act as virtual firewalls for EC2 instances, controlling inbound and outbound traffic at the instance level. They are fundamental to AWS security.

### Key Characteristics

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Group Characteristics                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ Stateful      - Return traffic automatically allowed         │
│  ✓ Allow Only    - Only allow rules (no explicit deny)          │
│  ✓ Instance-level - Attached to ENI (network interface)         │
│  ✓ Multiple SGs   - Instance can have up to 5 security groups   │
│  ✓ VPC-bound     - Security groups belong to a VPC              │
│  ✓ Chainable     - Can reference other security groups          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Security Groups vs NACLs

| Feature | Security Groups | Network ACLs |
|---------|----------------|--------------|
| Level | Instance (ENI) | Subnet |
| State | Stateful | Stateless |
| Rules | Allow only | Allow and Deny |
| Evaluation | All rules evaluated | Rules processed in order |
| Default | Deny all inbound, allow all outbound | Allow all |
| Association | Multiple per instance | One per subnet |

---

## Understanding Stateful Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│                    Stateful Security Groups                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Client (IP: 203.0.113.50)         EC2 Instance                 │
│       │                                  │                       │
│       │  1. Request (Port 80)           │                       │
│       ├─────────────────────────────────▶│                       │
│       │     ✓ Inbound rule allows       │                       │
│       │       HTTP on port 80           │                       │
│       │                                  │                       │
│       │  2. Response (Random Port)       │                       │
│       │◀─────────────────────────────────┤                       │
│       │     ✓ Automatically allowed      │                       │
│       │       (stateful - no outbound    │                       │
│       │        rule needed)              │                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Key Point: If you allow inbound HTTP (port 80), the response traffic
is automatically allowed regardless of outbound rules.
```

---

## Inbound and Outbound Rules

### Rule Components

| Component | Description | Example |
|-----------|-------------|---------|
| Type | Predefined protocol type | HTTP, SSH, Custom TCP |
| Protocol | TCP, UDP, ICMP, All | TCP |
| Port Range | Single port or range | 80, 443, 1024-65535 |
| Source/Destination | IP, CIDR, or security group | 0.0.0.0/0, sg-xxx |
| Description | Rule description | Allow HTTP from internet |

### Default Rules

**Default Security Group:**
```
Inbound:
  - All traffic from same security group (allows instances to communicate)

Outbound:
  - All traffic to 0.0.0.0/0 (allows all outbound)
```

**Custom Security Group (Initial):**
```
Inbound:
  - (empty - all inbound denied)

Outbound:
  - All traffic to 0.0.0.0/0 (allows all outbound)
```

---

## Common Security Group Configurations

### Web Server Security Group

```bash
# Create security group
aws ec2 create-security-group \
    --group-name web-server-sg \
    --description "Security group for web servers" \
    --vpc-id vpc-12345678

# Allow HTTP from anywhere
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 22 \
    --cidr 203.0.113.0/24

# View security group rules
aws ec2 describe-security-groups \
    --group-ids sg-0123456789abcdef0
```

### Database Security Group

```bash
# Create database security group
aws ec2 create-security-group \
    --group-name database-sg \
    --description "Security group for databases" \
    --vpc-id vpc-12345678

# Allow MySQL from web server security group only
aws ec2 authorize-security-group-ingress \
    --group-id sg-database \
    --protocol tcp \
    --port 3306 \
    --source-group sg-webserver

# Allow PostgreSQL from application tier
aws ec2 authorize-security-group-ingress \
    --group-id sg-database \
    --protocol tcp \
    --port 5432 \
    --source-group sg-application
```

### Application Server Security Group

```bash
# Create application security group
aws ec2 create-security-group \
    --group-name app-server-sg \
    --description "Security group for application servers" \
    --vpc-id vpc-12345678

# Allow traffic from load balancer only
aws ec2 authorize-security-group-ingress \
    --group-id sg-application \
    --protocol tcp \
    --port 8080 \
    --source-group sg-loadbalancer

# Allow health checks from load balancer
aws ec2 authorize-security-group-ingress \
    --group-id sg-application \
    --protocol tcp \
    --port 8081 \
    --source-group sg-loadbalancer
```

### Bastion Host Security Group

```bash
# Create bastion security group
aws ec2 create-security-group \
    --group-name bastion-sg \
    --description "Security group for bastion hosts" \
    --vpc-id vpc-12345678

# Allow SSH from corporate IP range
aws ec2 authorize-security-group-ingress \
    --group-id sg-bastion \
    --protocol tcp \
    --port 22 \
    --cidr 198.51.100.0/24

# Private instances allow SSH from bastion
aws ec2 authorize-security-group-ingress \
    --group-id sg-private-instances \
    --protocol tcp \
    --port 22 \
    --source-group sg-bastion
```

---

## Three-Tier Architecture Security Groups

```
┌─────────────────────────────────────────────────────────────────┐
│                    Three-Tier Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Internet                                                        │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  ALB Security Group (sg-alb)                         │       │
│  │  Inbound: 80, 443 from 0.0.0.0/0                    │       │
│  │  Outbound: All                                       │       │
│  └──────────────────────────────────────────────────────┘       │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Web Tier Security Group (sg-web)                    │       │
│  │  Inbound: 80, 443 from sg-alb only                  │       │
│  │  Outbound: 8080 to sg-app, 443 to 0.0.0.0/0         │       │
│  └──────────────────────────────────────────────────────┘       │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  App Tier Security Group (sg-app)                    │       │
│  │  Inbound: 8080 from sg-web only                     │       │
│  │  Outbound: 3306 to sg-db, 443 to 0.0.0.0/0          │       │
│  └──────────────────────────────────────────────────────┘       │
│      │                                                           │
│      ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Database Tier Security Group (sg-db)                │       │
│  │  Inbound: 3306 from sg-app only                     │       │
│  │  Outbound: None needed (stateful)                   │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```bash
# 1. Create ALB Security Group
aws ec2 create-security-group \
    --group-name alb-sg \
    --description "ALB security group" \
    --vpc-id vpc-12345678

aws ec2 authorize-security-group-ingress \
    --group-id sg-alb \
    --ip-permissions '[
        {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTP"}]},
        {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTPS"}]}
    ]'

# 2. Create Web Tier Security Group
aws ec2 create-security-group \
    --group-name web-sg \
    --description "Web tier security group" \
    --vpc-id vpc-12345678

aws ec2 authorize-security-group-ingress \
    --group-id sg-web \
    --protocol tcp \
    --port 80 \
    --source-group sg-alb

aws ec2 authorize-security-group-ingress \
    --group-id sg-web \
    --protocol tcp \
    --port 443 \
    --source-group sg-alb

# 3. Create App Tier Security Group
aws ec2 create-security-group \
    --group-name app-sg \
    --description "App tier security group" \
    --vpc-id vpc-12345678

aws ec2 authorize-security-group-ingress \
    --group-id sg-app \
    --protocol tcp \
    --port 8080 \
    --source-group sg-web

# 4. Create Database Security Group
aws ec2 create-security-group \
    --group-name db-sg \
    --description "Database security group" \
    --vpc-id vpc-12345678

aws ec2 authorize-security-group-ingress \
    --group-id sg-db \
    --protocol tcp \
    --port 3306 \
    --source-group sg-app
```

---

## Security Group Best Practices

### 1. Principle of Least Privilege

```
❌ Bad: Allow all traffic from 0.0.0.0/0
✓ Good: Allow specific ports from specific sources

❌ Bad: Allow SSH from 0.0.0.0/0
✓ Good: Allow SSH from corporate IP range or bastion only

❌ Bad: Use default security group
✓ Good: Create purpose-specific security groups
```

### 2. Use Security Group References

```bash
# Instead of IP addresses, reference security groups
# This way, if IP changes, no rule updates needed

# Good - Reference security group
aws ec2 authorize-security-group-ingress \
    --group-id sg-app \
    --protocol tcp \
    --port 3306 \
    --source-group sg-web

# Less ideal - Reference IP (may change)
aws ec2 authorize-security-group-ingress \
    --group-id sg-app \
    --protocol tcp \
    --port 3306 \
    --cidr 10.0.1.50/32
```

### 3. Use Descriptive Names and Tags

```bash
# Create with descriptive name
aws ec2 create-security-group \
    --group-name prod-web-server-sg \
    --description "Production web server - allows HTTP/HTTPS" \
    --vpc-id vpc-12345678

# Add tags
aws ec2 create-tags \
    --resources sg-0123456789abcdef0 \
    --tags \
        Key=Name,Value=prod-web-server-sg \
        Key=Environment,Value=production \
        Key=Application,Value=web-frontend \
        Key=Owner,Value=platform-team
```

### 4. Add Descriptions to Rules

```bash
# Add rule with description
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --ip-permissions '[
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [
                {
                    "CidrIp": "198.51.100.0/24",
                    "Description": "SSH from corporate network"
                }
            ]
        }
    ]'
```

### 5. Restrict Outbound Traffic

```bash
# Create security group with no default outbound rules
aws ec2 create-security-group \
    --group-name restricted-sg \
    --description "Restricted outbound access" \
    --vpc-id vpc-12345678

# Remove default outbound rule
aws ec2 revoke-security-group-egress \
    --group-id sg-restricted \
    --protocol all \
    --port all \
    --cidr 0.0.0.0/0

# Add specific outbound rules
aws ec2 authorize-security-group-egress \
    --group-id sg-restricted \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-egress \
    --group-id sg-restricted \
    --protocol tcp \
    --port 3306 \
    --source-group sg-database
```

---

## Common Port References

### Standard Services

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| SSH | 22 | TCP | Secure Shell |
| RDP | 3389 | TCP | Remote Desktop |
| HTTP | 80 | TCP | Web (unencrypted) |
| HTTPS | 443 | TCP | Web (encrypted) |
| SMTP | 25 | TCP | Email sending |
| DNS | 53 | UDP/TCP | Domain resolution |
| NTP | 123 | UDP | Time sync |
| LDAP | 389 | TCP | Directory services |
| LDAPS | 636 | TCP | Secure LDAP |

### Databases

| Service | Port | Protocol |
|---------|------|----------|
| MySQL/MariaDB | 3306 | TCP |
| PostgreSQL | 5432 | TCP |
| Oracle | 1521 | TCP |
| SQL Server | 1433 | TCP |
| MongoDB | 27017 | TCP |
| Redis | 6379 | TCP |
| Memcached | 11211 | TCP |
| Elasticsearch | 9200/9300 | TCP |

### AWS Services

| Service | Port | Description |
|---------|------|-------------|
| EFS | 2049 | NFS mount |
| SSM Agent | 443 | Systems Manager |
| CloudWatch | 443 | Monitoring |

---

## Modifying Security Groups

### Add Rules

```bash
# Add single rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 8443 \
    --cidr 10.0.0.0/8

# Add multiple rules at once
aws ec2 authorize-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --ip-permissions '[
        {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "10.0.0.0/8"}]}
    ]'
```

### Remove Rules

```bash
# Remove specific inbound rule
aws ec2 revoke-security-group-ingress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Remove outbound rule
aws ec2 revoke-security-group-egress \
    --group-id sg-0123456789abcdef0 \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0
```

### List and Describe

```bash
# List all security groups
aws ec2 describe-security-groups \
    --query 'SecurityGroups[*].[GroupId,GroupName,Description]' \
    --output table

# Describe specific security group
aws ec2 describe-security-groups \
    --group-ids sg-0123456789abcdef0

# Find security groups with specific rule
aws ec2 describe-security-groups \
    --filters "Name=ip-permission.from-port,Values=22" \
              "Name=ip-permission.cidr,Values=0.0.0.0/0" \
    --query 'SecurityGroups[*].[GroupId,GroupName]'

# Find unused security groups
aws ec2 describe-network-interfaces \
    --query 'NetworkInterfaces[*].Groups[*].GroupId' \
    --output text | tr '\t' '\n' | sort -u > used-sgs.txt

aws ec2 describe-security-groups \
    --query 'SecurityGroups[*].GroupId' \
    --output text | tr '\t' '\n' | sort -u > all-sgs.txt

comm -23 all-sgs.txt used-sgs.txt
```

---

## CloudFormation Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Security Groups for Three-Tier Architecture'

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  AllowedSSHCidr:
    Type: String
    Default: 10.0.0.0/8
    Description: CIDR block for SSH access

Resources:
  # ALB Security Group
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: alb-sg
      GroupDescription: Security group for Application Load Balancer
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: Allow HTTP from internet
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: Allow HTTPS from internet
      Tags:
        - Key: Name
          Value: alb-sg

  # Web Tier Security Group
  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: web-sg
      GroupDescription: Security group for web servers
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: Allow HTTP from ALB
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: Allow HTTPS from ALB
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHCidr
          Description: Allow SSH from corporate network
      Tags:
        - Key: Name
          Value: web-sg

  # App Tier Security Group
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: app-sg
      GroupDescription: Security group for application servers
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref WebSecurityGroup
          Description: Allow application traffic from web tier
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHCidr
          Description: Allow SSH from corporate network
      Tags:
        - Key: Name
          Value: app-sg

  # Database Security Group
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: db-sg
      GroupDescription: Security group for databases
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: Allow MySQL from app tier
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref AppSecurityGroup
          Description: Allow PostgreSQL from app tier
      Tags:
        - Key: Name
          Value: db-sg

  # Bastion Security Group
  BastionSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: bastion-sg
      GroupDescription: Security group for bastion hosts
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref AllowedSSHCidr
          Description: Allow SSH from corporate network
      Tags:
        - Key: Name
          Value: bastion-sg

  # Allow SSH from bastion to all instances
  WebFromBastionIngress:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      GroupId: !Ref WebSecurityGroup
      IpProtocol: tcp
      FromPort: 22
      ToPort: 22
      SourceSecurityGroupId: !Ref BastionSecurityGroup
      Description: Allow SSH from bastion

  AppFromBastionIngress:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      GroupId: !Ref AppSecurityGroup
      IpProtocol: tcp
      FromPort: 22
      ToPort: 22
      SourceSecurityGroupId: !Ref BastionSecurityGroup
      Description: Allow SSH from bastion

Outputs:
  ALBSecurityGroupId:
    Description: ALB Security Group ID
    Value: !Ref ALBSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-ALBSecurityGroup'

  WebSecurityGroupId:
    Description: Web Security Group ID
    Value: !Ref WebSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-WebSecurityGroup'

  AppSecurityGroupId:
    Description: App Security Group ID
    Value: !Ref AppSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-AppSecurityGroup'

  DatabaseSecurityGroupId:
    Description: Database Security Group ID
    Value: !Ref DatabaseSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-DatabaseSecurityGroup'

  BastionSecurityGroupId:
    Description: Bastion Security Group ID
    Value: !Ref BastionSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-BastionSecurityGroup'
```

---

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Cannot connect | No inbound rule | Add appropriate rule |
| Timeout | Wrong port/protocol | Verify port and protocol |
| Connection refused | Service not running | Check service on instance |
| Intermittent issues | Rule with wrong source | Verify CIDR/source SG |

### Debugging Commands

```bash
# Check security groups attached to instance
aws ec2 describe-instances \
    --instance-ids i-1234567890abcdef0 \
    --query 'Reservations[0].Instances[0].SecurityGroups'

# Check all rules for a security group
aws ec2 describe-security-groups \
    --group-ids sg-0123456789abcdef0 \
    --query 'SecurityGroups[0].{Inbound:IpPermissions,Outbound:IpPermissionsEgress}'

# Test connectivity from instance
# SSH into instance and run:
nc -zv target-ip port

# Check if port is listening
sudo netstat -tlnp | grep :80

# Verify security group allows traffic
aws ec2 describe-security-groups \
    --filters "Name=ip-permission.from-port,Values=80" \
    --query 'SecurityGroups[*].[GroupId,GroupName]'
```

### VPC Flow Logs

Enable VPC Flow Logs to debug traffic that is being rejected:

```bash
# Create flow log
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-12345678 \
    --traffic-type REJECT \
    --log-destination-type cloud-watch-logs \
    --log-group-name vpc-flow-logs
```

---

## Key Takeaways

1. **Security groups are stateful** - Response traffic is automatically allowed
2. **Default is deny** - Explicitly allow required traffic
3. **Reference security groups** - More flexible than IP addresses
4. **Least privilege** - Only allow what is needed
5. **Document everything** - Use descriptions and tags
6. **Regular audits** - Review and remove unused rules
7. **Multiple security groups** - Layer security with multiple groups

---

## Next Steps

Continue to [06-key-pairs-and-access.md](./06-key-pairs-and-access.md) to learn about connecting to EC2 instances.
