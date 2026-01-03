# 07 - Elastic IPs and Elastic Network Interfaces

## Overview

Understanding EC2 networking is essential for designing robust architectures. This section covers IP addressing, Elastic IPs, and Elastic Network Interfaces (ENIs).

---

## IP Addressing in EC2

### Types of IP Addresses

```
┌─────────────────────────────────────────────────────────────────┐
│                    EC2 IP Address Types                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Private IP                            │    │
│  │  • Automatically assigned from subnet CIDR              │    │
│  │  • Persists until instance termination                  │    │
│  │  • Used for internal VPC communication                  │    │
│  │  • Cannot be reassigned                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Public IP                             │    │
│  │  • Assigned from AWS pool (if enabled)                  │    │
│  │  • Released when instance stops/terminates              │    │
│  │  • New IP assigned on restart                           │    │
│  │  • Free to use                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Elastic IP                            │    │
│  │  • Static public IP you own                             │    │
│  │  • Persists until you release it                        │    │
│  │  • Can be remapped between instances                    │    │
│  │  • Charged when not associated with running instance    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### IP Address Comparison

| Feature | Private IP | Public IP | Elastic IP |
|---------|-----------|-----------|------------|
| Assigned from | Subnet CIDR | AWS pool | AWS pool (allocated) |
| Persistence | Until termination | Until stop | Until released |
| Reassignable | No | No | Yes |
| Cost | Free | Free | Free when associated* |
| Use case | Internal comms | Temporary access | Permanent public endpoint |

*Charged when not associated with a running instance

---

## Elastic IP Addresses

### What is an Elastic IP?

An Elastic IP (EIP) is a static, public IPv4 address that you can allocate to your AWS account. It remains associated with your account until you release it.

### Elastic IP Pricing (2024)

| Condition | Cost |
|-----------|------|
| Associated with running instance | Free |
| Associated with stopped instance | ~$0.005/hour (~$3.65/month) |
| Not associated with any instance | ~$0.005/hour |
| Additional EIPs on running instance | ~$0.005/hour each |
| EIP remapping (first 100/month) | Free |
| EIP remapping (over 100/month) | $0.10 each |

### Managing Elastic IPs

```bash
# Allocate new Elastic IP
aws ec2 allocate-address --domain vpc

# Output:
# {
#     "PublicIp": "54.123.45.67",
#     "AllocationId": "eipalloc-12345678",
#     "Domain": "vpc"
# }

# Allocate with specific pool (BYOIP)
aws ec2 allocate-address \
    --domain vpc \
    --public-ipv4-pool ipv4pool-ec2-012345678

# List Elastic IPs
aws ec2 describe-addresses \
    --query 'Addresses[*].[PublicIp,InstanceId,AssociationId]' \
    --output table

# Associate EIP with instance
aws ec2 associate-address \
    --instance-id i-1234567890abcdef0 \
    --allocation-id eipalloc-12345678

# Associate EIP with specific network interface
aws ec2 associate-address \
    --allocation-id eipalloc-12345678 \
    --network-interface-id eni-12345678 \
    --private-ip-address 10.0.1.100

# Disassociate EIP
aws ec2 disassociate-address \
    --association-id eipassoc-12345678

# Release EIP (return to AWS pool)
aws ec2 release-address \
    --allocation-id eipalloc-12345678
```

### Elastic IP Use Cases

| Use Case | Description |
|----------|-------------|
| DNS A records | Permanent IP for domain name resolution |
| Whitelisting | When external services need static IP |
| High availability | Remap to standby instance during failure |
| Legacy applications | Apps requiring fixed public IP |
| API endpoints | Consistent endpoint for API consumers |

### Elastic IP Best Practices

1. **Don't use EIPs unless necessary** - Use Load Balancers or DNS names instead
2. **Clean up unused EIPs** - You're charged for unassociated EIPs
3. **Use tags** - Track purpose and ownership
4. **Consider quotas** - Default 5 per region (can request increase)
5. **Plan for IPv6** - EIPs are IPv4 only; IPv6 addresses are different

---

## Elastic Network Interfaces (ENI)

### What is an ENI?

An Elastic Network Interface is a virtual network card that you can attach to an EC2 instance. Every instance has at least one ENI (primary network interface).

```
┌─────────────────────────────────────────────────────────────────┐
│                    Elastic Network Interface                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Primary Private IPv4 Address                           │    │
│  │  • Automatically assigned from subnet                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Secondary Private IPv4 Addresses (optional)            │    │
│  │  • Multiple IPs on same ENI                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Elastic IP (optional)                                  │    │
│  │  • Associated with private IP                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  IPv6 Addresses (optional)                              │    │
│  │  • Assigned from subnet IPv6 CIDR                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Security Groups                                        │    │
│  │  • One or more security groups                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  MAC Address                                            │    │
│  │  • Unique identifier                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Source/Destination Check                               │    │
│  │  • Enable/disable for NAT scenarios                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### ENI Characteristics

| Characteristic | Description |
|---------------|-------------|
| Subnet-bound | ENI belongs to specific subnet |
| AZ-bound | Cannot move ENI to different AZ |
| Attachable | Can attach/detach from instances |
| Persistent | Exists independently of instances |
| Security groups | Has own security group associations |

### Maximum ENIs per Instance Type

| Instance Size | Max ENIs | IPv4 per ENI |
|--------------|----------|--------------|
| t3.micro | 2 | 2 |
| t3.small | 3 | 4 |
| t3.medium | 3 | 6 |
| t3.large | 3 | 12 |
| m5.large | 3 | 10 |
| m5.xlarge | 4 | 15 |
| m5.2xlarge | 4 | 15 |
| m5.4xlarge | 8 | 30 |

### Managing ENIs

```bash
# Create ENI
aws ec2 create-network-interface \
    --subnet-id subnet-12345678 \
    --description "My secondary ENI" \
    --groups sg-12345678 \
    --private-ip-address 10.0.1.100

# Create ENI with multiple IPs
aws ec2 create-network-interface \
    --subnet-id subnet-12345678 \
    --groups sg-12345678 \
    --secondary-private-ip-address-count 3

# List ENIs
aws ec2 describe-network-interfaces \
    --query 'NetworkInterfaces[*].[NetworkInterfaceId,Description,PrivateIpAddress,Status]' \
    --output table

# Attach ENI to instance
aws ec2 attach-network-interface \
    --network-interface-id eni-12345678 \
    --instance-id i-1234567890abcdef0 \
    --device-index 1

# Detach ENI
aws ec2 detach-network-interface \
    --attachment-id eni-attach-12345678

# Force detach (if instance not responding)
aws ec2 detach-network-interface \
    --attachment-id eni-attach-12345678 \
    --force

# Delete ENI
aws ec2 delete-network-interface \
    --network-interface-id eni-12345678

# Assign secondary private IP
aws ec2 assign-private-ip-addresses \
    --network-interface-id eni-12345678 \
    --secondary-private-ip-address-count 1

# Assign specific secondary IP
aws ec2 assign-private-ip-addresses \
    --network-interface-id eni-12345678 \
    --private-ip-addresses 10.0.1.101

# Unassign secondary IP
aws ec2 unassign-private-ip-addresses \
    --network-interface-id eni-12345678 \
    --private-ip-addresses 10.0.1.101

# Modify ENI attribute (source/dest check)
aws ec2 modify-network-interface-attribute \
    --network-interface-id eni-12345678 \
    --no-source-dest-check  # For NAT instance
```

### Configuring Secondary ENI on Linux

```bash
# List network interfaces
ip link show

# Configure secondary interface
# Create config file (Amazon Linux 2)
sudo cat << 'EOF' > /etc/sysconfig/network-scripts/ifcfg-eth1
DEVICE=eth1
BOOTPROTO=dhcp
ONBOOT=yes
TYPE=Ethernet
USERCTL=yes
PEERDNS=yes
DHCPV6C=yes
DHCPV6C_OPTIONS=-nw
PERSISTENT_DHCLIENT=yes
RES_OPTIONS="timeout:2 attempts:5"
DHCP_ARP_CHECK=no
EOF

# Bring up interface
sudo ifup eth1

# Or for immediate configuration
sudo ip addr add 10.0.1.100/24 dev eth1
sudo ip link set eth1 up

# Add routing for secondary interface
sudo ip route add 10.0.1.0/24 dev eth1 table 1000
sudo ip route add default via 10.0.1.1 dev eth1 table 1000
sudo ip rule add from 10.0.1.100/32 table 1000
```

---

## Multiple IP Addresses

### Use Cases for Multiple IPs

| Use Case | Description |
|----------|-------------|
| Hosting multiple SSL websites | Each domain needs its own IP for SSL |
| Running multiple services | Separate IPs for different services |
| Network appliances | Firewalls, load balancers need multiple IPs |
| High availability | Quick IP failover between instances |
| License management | Software licensed by IP address |

### Configuring Multiple IPs

```bash
# Assign multiple secondary IPs to ENI
aws ec2 assign-private-ip-addresses \
    --network-interface-id eni-12345678 \
    --secondary-private-ip-address-count 3

# On the instance, configure additional IPs
# List assigned IPs from metadata
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/network/interfaces/macs/

# Get secondary IPs for specific interface
MAC=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/mac)
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/network/interfaces/macs/$MAC/local-ipv4s

# Configure secondary IPs on interface
sudo ip addr add 10.0.1.101/24 dev eth0
sudo ip addr add 10.0.1.102/24 dev eth0
```

---

## ENI Use Cases

### 1. Management Network

```
┌─────────────────────────────────────────────────────────────────┐
│                    Management Network Pattern                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Public Subnet                     Private Subnet               │
│   ┌────────────────┐               ┌────────────────┐           │
│   │ Management ENI │───────────────│ Application    │           │
│   │ (eth0)         │               │ ENI (eth1)     │           │
│   │ Public IP      │               │ Private only   │           │
│   └────────────────┘               └────────────────┘           │
│          │                                │                      │
│          │                                │                      │
│   ┌──────┴───────┐                ┌──────┴───────┐              │
│   │ Mgmt Traffic │                │ App Traffic  │              │
│   │ SSH, Mgmt    │                │ Database,    │              │
│   │ Tools        │                │ Backend      │              │
│   └──────────────┘                └──────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. High Availability with ENI Failover

```bash
# Create standby ENI with production IP
aws ec2 create-network-interface \
    --subnet-id subnet-12345678 \
    --groups sg-12345678 \
    --private-ip-address 10.0.1.100

# During failover, move ENI to standby instance
# Detach from failed instance
aws ec2 detach-network-interface \
    --attachment-id eni-attach-12345678 \
    --force

# Attach to standby instance
aws ec2 attach-network-interface \
    --network-interface-id eni-12345678 \
    --instance-id i-standby-instance \
    --device-index 1
```

### 3. Network Appliance (NAT Instance)

```bash
# Disable source/destination check for NAT
aws ec2 modify-network-interface-attribute \
    --network-interface-id eni-12345678 \
    --no-source-dest-check

# Configure NAT on instance
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

### 4. Dual-Homed Instance

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dual-Homed Instance                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Subnet A (10.0.1.0/24)          Subnet B (10.0.2.0/24)        │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                     EC2 Instance                         │   │
│   │   ┌──────────────┐              ┌──────────────┐        │   │
│   │   │   eth0       │              │   eth1       │        │   │
│   │   │   10.0.1.10  │              │   10.0.2.10  │        │   │
│   │   └──────┬───────┘              └──────┬───────┘        │   │
│   └──────────┼──────────────────────────────┼───────────────┘   │
│              │                              │                    │
│              ▼                              ▼                    │
│        ┌─────────────┐              ┌─────────────┐             │
│        │  Frontend   │              │  Backend    │             │
│        │  Network    │              │  Network    │             │
│        └─────────────┘              └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## CloudFormation Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 with Multiple ENIs and Elastic IPs'

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id

  PublicSubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: Public subnet for management interface

  PrivateSubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: Private subnet for application interface

  InstanceType:
    Type: String
    Default: t3.medium

Resources:
  # Security Groups
  ManagementSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Management interface security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/8
      Tags:
        - Key: Name
          Value: management-sg

  ApplicationSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Application interface security group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 10.0.0.0/8
      Tags:
        - Key: Name
          Value: application-sg

  # Primary ENI (Management)
  ManagementENI:
    Type: AWS::EC2::NetworkInterface
    Properties:
      Description: Management network interface
      SubnetId: !Ref PublicSubnetId
      GroupSet:
        - !Ref ManagementSecurityGroup
      Tags:
        - Key: Name
          Value: management-eni

  # Secondary ENI (Application)
  ApplicationENI:
    Type: AWS::EC2::NetworkInterface
    Properties:
      Description: Application network interface
      SubnetId: !Ref PrivateSubnetId
      GroupSet:
        - !Ref ApplicationSecurityGroup
      Tags:
        - Key: Name
          Value: application-eni

  # Elastic IP for Management Interface
  ManagementEIP:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: management-eip

  # Associate EIP with Management ENI
  EIPAssociation:
    Type: AWS::EC2::EIPAssociation
    Properties:
      AllocationId: !GetAtt ManagementEIP.AllocationId
      NetworkInterfaceId: !Ref ManagementENI

  # EC2 Instance
  DualHomedInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}'
      InstanceType: !Ref InstanceType
      NetworkInterfaces:
        - NetworkInterfaceId: !Ref ManagementENI
          DeviceIndex: '0'
        - NetworkInterfaceId: !Ref ApplicationENI
          DeviceIndex: '1'
      UserData:
        Fn::Base64: |
          #!/bin/bash
          # Configure secondary network interface
          cat << 'EOF' > /etc/sysconfig/network-scripts/ifcfg-eth1
          DEVICE=eth1
          BOOTPROTO=dhcp
          ONBOOT=yes
          TYPE=Ethernet
          USERCTL=yes
          PEERDNS=no
          EOF

          # Bring up secondary interface
          ifup eth1
      Tags:
        - Key: Name
          Value: dual-homed-instance

  # Additional Secondary IPs (optional)
  SecondaryPrivateIpAssignment:
    Type: Custom::SecondaryIP
    # Use Lambda to assign secondary IPs
    # Or do it in UserData

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref DualHomedInstance

  ManagementIP:
    Description: Management Elastic IP
    Value: !Ref ManagementEIP

  ManagementPrivateIP:
    Description: Management Private IP
    Value: !GetAtt ManagementENI.PrimaryPrivateIpAddress

  ApplicationPrivateIP:
    Description: Application Private IP
    Value: !GetAtt ApplicationENI.PrimaryPrivateIpAddress
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Cannot assign EIP | Limit reached | Request limit increase |
| ENI attach fails | Wrong AZ | ENI must be in same AZ as instance |
| Secondary ENI no traffic | No route table | Configure routing on instance |
| EIP not accessible | Security group | Check inbound rules |
| ENI stuck detaching | Force detach | Use --force flag |

### Debugging Commands

```bash
# Check EIP associations
aws ec2 describe-addresses \
    --query 'Addresses[*].[PublicIp,InstanceId,NetworkInterfaceId]'

# Check ENI attachments
aws ec2 describe-network-interfaces \
    --query 'NetworkInterfaces[*].[NetworkInterfaceId,Status,Attachment.InstanceId]'

# On instance - check interface status
ip addr show

# Check routing table
ip route show

# Check connectivity from secondary interface
ping -I eth1 8.8.8.8

# Verify security group allows traffic
aws ec2 describe-network-interface-attribute \
    --network-interface-id eni-12345678 \
    --attribute groupSet
```

---

## Key Takeaways

1. **Use Elastic IPs sparingly** - Prefer Load Balancers for public access
2. **EIPs cost money when unused** - Release or associate with running instances
3. **ENIs are AZ-bound** - Cannot move between AZs
4. **Multiple ENIs enable network segmentation** - Management vs application traffic
5. **ENIs persist independently** - Survive instance termination
6. **Secondary IPs useful for hosting** - Multiple websites/services on one instance
7. **Disable source/dest check for NAT** - Required for network appliances

---

## Next Steps

Continue to [08-ec2-pricing.md](./08-ec2-pricing.md) to learn about EC2 pricing models and cost optimization.
