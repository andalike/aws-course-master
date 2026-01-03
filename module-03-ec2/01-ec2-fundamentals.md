# 01 - EC2 Fundamentals

## What is Amazon EC2?

Amazon Elastic Compute Cloud (Amazon EC2) is a web service that provides resizable compute capacity in the cloud. In simple terms, EC2 allows you to rent virtual computers on which you can run your own applications.

### Traditional vs. Cloud Computing

| Aspect | Traditional Data Center | Amazon EC2 |
|--------|------------------------|------------|
| Provisioning Time | Weeks to months | Minutes |
| Upfront Cost | High (CAPEX) | None (OPEX) |
| Capacity | Fixed | Elastic |
| Maintenance | Your responsibility | AWS responsibility |
| Global Reach | Limited | 30+ regions |
| Scaling | Manual, slow | Automatic, instant |

### Key EC2 Concepts

```
┌─────────────────────────────────────────────────────────────────┐
│                        EC2 Instance                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  AMI (Operating System + Pre-installed Software)         │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Instance Type │  │ Security     │  │ Key Pair             │  │
│  │ (CPU, Memory) │  │ Group        │  │ (SSH Access)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Storage (EBS Volumes / Instance Store)                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Network (VPC, Subnet, IP Address, ENI)                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## EC2 Instance Types Explained

EC2 instance types are named using a specific convention:

```
m5.xlarge
│ │  │
│ │  └── Size (nano, micro, small, medium, large, xlarge, 2xlarge...)
│ └───── Generation (higher = newer)
└─────── Family (m = general purpose)
```

### Instance Families Overview

#### General Purpose (T, M, A)

**T-Series: Burstable Performance**

T instances provide a baseline level of CPU performance with the ability to burst above baseline when needed.

| Instance | vCPU | Memory | Network | Use Case |
|----------|------|--------|---------|----------|
| t3.nano | 2 | 0.5 GB | Up to 5 Gbps | Micro-services |
| t3.micro | 2 | 1 GB | Up to 5 Gbps | Development, testing |
| t3.small | 2 | 2 GB | Up to 5 Gbps | Small web apps |
| t3.medium | 2 | 4 GB | Up to 5 Gbps | Web servers |
| t3.large | 2 | 8 GB | Up to 5 Gbps | Light databases |
| t3.xlarge | 4 | 16 GB | Up to 5 Gbps | Application servers |
| t3.2xlarge | 8 | 32 GB | Up to 5 Gbps | Larger workloads |

**CPU Credits System**:
```
┌─────────────────────────────────────────────────────────────┐
│                    T3 CPU Credits                            │
├─────────────────────────────────────────────────────────────┤
│  • Earn credits when CPU usage < baseline                    │
│  • Spend credits when CPU usage > baseline                   │
│  • t3.micro baseline: 10% (earns 6 credits/hour)            │
│  • 1 credit = 1 vCPU at 100% for 1 minute                   │
│  • Unlimited mode: Pay for extra usage (default)            │
│  • Standard mode: Throttled when credits exhausted          │
└─────────────────────────────────────────────────────────────┘
```

**M-Series: Balanced Performance**

General purpose instances with a balance of compute, memory, and networking.

| Instance | vCPU | Memory | Network | Use Case |
|----------|------|--------|---------|----------|
| m5.large | 2 | 8 GB | Up to 10 Gbps | Web servers |
| m5.xlarge | 4 | 16 GB | Up to 10 Gbps | Application servers |
| m5.2xlarge | 8 | 32 GB | Up to 10 Gbps | Backend servers |
| m5.4xlarge | 16 | 64 GB | Up to 10 Gbps | Mid-size databases |
| m5.8xlarge | 32 | 128 GB | 10 Gbps | Large applications |
| m5.12xlarge | 48 | 192 GB | 12 Gbps | Enterprise apps |
| m5.16xlarge | 64 | 256 GB | 20 Gbps | Large databases |
| m5.24xlarge | 96 | 384 GB | 25 Gbps | Large workloads |

**M7i/M7g: Latest Generation**
- M7i: Intel Xeon (Sapphire Rapids) - up to 15% better price-performance vs M6i
- M7g: AWS Graviton3 (ARM) - up to 25% better price-performance vs M6g

---

#### Compute Optimized (C)

Designed for compute-intensive tasks requiring high-performance processors.

| Instance | vCPU | Memory | Network | Use Case |
|----------|------|--------|---------|----------|
| c5.large | 2 | 4 GB | Up to 10 Gbps | Batch processing |
| c5.xlarge | 4 | 8 GB | Up to 10 Gbps | Gaming servers |
| c5.2xlarge | 8 | 16 GB | Up to 10 Gbps | Scientific modeling |
| c5.4xlarge | 16 | 32 GB | Up to 10 Gbps | Ad serving |
| c5.9xlarge | 36 | 72 GB | 10 Gbps | Video encoding |
| c5.18xlarge | 72 | 144 GB | 25 Gbps | HPC |

**Best For**:
- Batch processing workloads
- Media transcoding
- High-performance web servers
- Scientific modeling
- Dedicated gaming servers
- Machine learning inference

---

#### Memory Optimized (R, X, z)

Designed for memory-intensive applications.

**R-Series: High Memory-to-CPU Ratio**

| Instance | vCPU | Memory | Network | Use Case |
|----------|------|--------|---------|----------|
| r5.large | 2 | 16 GB | Up to 10 Gbps | Small Redis |
| r5.xlarge | 4 | 32 GB | Up to 10 Gbps | In-memory cache |
| r5.2xlarge | 8 | 64 GB | Up to 10 Gbps | Mid-size databases |
| r5.4xlarge | 16 | 128 GB | Up to 10 Gbps | In-memory databases |
| r5.8xlarge | 32 | 256 GB | 10 Gbps | SAP HANA |
| r5.12xlarge | 48 | 384 GB | 10 Gbps | Large in-memory |
| r5.24xlarge | 96 | 768 GB | 25 Gbps | Very large databases |

**X-Series: Extreme Memory**

| Instance | vCPU | Memory | Use Case |
|----------|------|--------|----------|
| x1.16xlarge | 64 | 976 GB | SAP HANA |
| x1.32xlarge | 128 | 1,952 GB | Large SAP HANA |
| x2idn.32xlarge | 128 | 2,048 GB | SAP, Oracle |

**Best For**:
- High-performance relational databases
- In-memory databases (Redis, Memcached)
- Real-time big data analytics
- SAP HANA

---

#### Storage Optimized (I, D, H)

Designed for workloads requiring high, sequential read/write access to large datasets.

**I-Series: High IOPS (NVMe SSD)**

| Instance | vCPU | Memory | Storage | IOPS |
|----------|------|--------|---------|------|
| i3.large | 2 | 15.25 GB | 1 x 475 GB NVMe | 100K |
| i3.xlarge | 4 | 30.5 GB | 1 x 950 GB NVMe | 206K |
| i3.2xlarge | 8 | 61 GB | 1 x 1.9 TB NVMe | 412K |
| i3.4xlarge | 16 | 122 GB | 2 x 1.9 TB NVMe | 825K |
| i3.8xlarge | 32 | 244 GB | 4 x 1.9 TB NVMe | 1.65M |
| i3.16xlarge | 64 | 488 GB | 8 x 1.9 TB NVMe | 3.3M |

**D-Series: Dense HDD Storage**

| Instance | vCPU | Memory | Storage |
|----------|------|--------|---------|
| d2.xlarge | 4 | 30.5 GB | 3 x 2 TB HDD |
| d2.2xlarge | 8 | 61 GB | 6 x 2 TB HDD |
| d2.4xlarge | 16 | 122 GB | 12 x 2 TB HDD |
| d2.8xlarge | 36 | 244 GB | 24 x 2 TB HDD |

**Best For**:
- Data warehousing
- Distributed file systems (HDFS)
- Log processing
- Data-intensive applications

---

#### Accelerated Computing (P, G, Inf, Trn)

Instances with hardware accelerators (GPUs, FPGAs).

**P-Series: GPU for ML Training**

| Instance | vCPU | Memory | GPU | GPU Memory |
|----------|------|--------|-----|------------|
| p3.2xlarge | 8 | 61 GB | 1x V100 | 16 GB |
| p3.8xlarge | 32 | 244 GB | 4x V100 | 64 GB |
| p3.16xlarge | 64 | 488 GB | 8x V100 | 128 GB |
| p4d.24xlarge | 96 | 1,152 GB | 8x A100 | 320 GB |
| p5.48xlarge | 192 | 2,048 GB | 8x H100 | 640 GB |

**G-Series: Graphics & ML Inference**

| Instance | vCPU | Memory | GPU | Use Case |
|----------|------|--------|-----|----------|
| g4dn.xlarge | 4 | 16 GB | 1x T4 | ML inference |
| g4dn.2xlarge | 8 | 32 GB | 1x T4 | Gaming |
| g5.xlarge | 4 | 16 GB | 1x A10G | Graphics |
| g5.2xlarge | 8 | 32 GB | 1x A10G | Video rendering |

**Inf/Trn-Series: AWS Custom Silicon**

| Instance | Chip | Use Case |
|----------|------|----------|
| inf1.xlarge | 1x Inferentia | ML inference |
| inf2.xlarge | 1x Inferentia2 | ML inference |
| trn1.2xlarge | 1x Trainium | ML training |
| trn1.32xlarge | 16x Trainium | Large ML training |

---

## Choosing the Right Instance Type

### Decision Framework

```
                    ┌─────────────────┐
                    │ What's your     │
                    │ primary need?   │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Balanced │      │   CPU    │      │  Memory  │
    └────┬─────┘      └────┬─────┘      └────┬─────┘
         │                 │                 │
         ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │Variable? │      │    C5    │      │    R5    │
    └────┬─────┘      │    C6i   │      │    R6i   │
    Yes  │  No        │    C7g   │      │    X1    │
    ┌────┴────┐       └──────────┘      └──────────┘
    ▼         ▼
┌──────┐  ┌──────┐
│  T3  │  │  M5  │
│  T3a │  │  M6i │
└──────┘  │  M7g │
          └──────┘
```

### Workload-Based Recommendations

| Workload | Recommended | Reason |
|----------|-------------|--------|
| Development/Testing | t3.micro, t3.small | Cost-effective, burstable |
| Small Web Server | t3.small, t3.medium | Handles variable traffic |
| Production Web Server | m5.large, m6i.large | Consistent performance |
| API Server | c5.large, c6i.large | Fast request processing |
| WordPress/CMS | t3.medium, m5.large | Balanced resources |
| MySQL/PostgreSQL | r5.large, r6i.large | Memory for caching |
| Redis/Memcached | r5.large, r6g.large | Memory-optimized |
| Machine Learning | p3.2xlarge, g4dn.xlarge | GPU acceleration |
| Video Encoding | c5.2xlarge, c6i.2xlarge | CPU-intensive |
| Data Analytics | i3.xlarge, d2.xlarge | Fast storage access |

### Right-Sizing Process

1. **Start Small**: Begin with smaller instances
2. **Monitor Metrics**: Use CloudWatch to track CPU, memory, network
3. **Analyze Patterns**: Look for consistent under/over-utilization
4. **Adjust Accordingly**: Scale up or down based on data

```bash
# Get CPU utilization metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-08T00:00:00Z \
    --period 3600 \
    --statistics Average
```

---

## Instance Type Comparison Chart

### General Purpose Comparison

| Feature | t3.medium | m5.large | m6i.large | m7g.large |
|---------|-----------|----------|-----------|-----------|
| vCPU | 2 | 2 | 2 | 2 |
| Memory | 4 GB | 8 GB | 8 GB | 8 GB |
| Network | Up to 5 Gbps | Up to 10 Gbps | Up to 12.5 Gbps | Up to 12.5 Gbps |
| EBS Bandwidth | Up to 2,085 Mbps | Up to 4,750 Mbps | Up to 10,000 Mbps | Up to 10,000 Mbps |
| Processor | Intel Xeon | Intel Xeon | Intel Xeon | AWS Graviton3 |
| Architecture | x86_64 | x86_64 | x86_64 | arm64 |
| Price/hour* | $0.0416 | $0.096 | $0.096 | $0.0816 |

*Prices are approximate for us-east-1, On-Demand, Linux

### Performance per Dollar

| Instance | vCPU/$ | Memory/$  | Best Value For |
|----------|--------|-----------|----------------|
| t3.micro | 48.08 | 24.04 GB | Development |
| m6i.large | 20.83 | 83.33 GB | Production |
| c6i.large | 20.83 | 41.67 GB | CPU workloads |
| r6i.large | 15.87 | 126.98 GB | Memory workloads |
| m7g.large | 24.51 | 98.04 GB | ARM-compatible |

---

## Instance Metadata and User Data

### Instance Metadata

EC2 instances can query information about themselves using the Instance Metadata Service (IMDS).

```bash
# Get instance ID
curl http://169.254.169.254/latest/meta-data/instance-id

# Get instance type
curl http://169.254.169.254/latest/meta-data/instance-type

# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Get availability zone
curl http://169.254.169.254/latest/meta-data/placement/availability-zone

# Get IAM role credentials
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name
```

### IMDSv2 (Recommended)

```bash
# Get token (required for IMDSv2)
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
    -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Use token to get metadata
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
    http://169.254.169.254/latest/meta-data/instance-id
```

---

## AWS CLI Commands for EC2

### Describe Instances

```bash
# List all instances
aws ec2 describe-instances

# List running instances only
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running"

# Get specific instance details
aws ec2 describe-instances \
    --instance-ids i-1234567890abcdef0

# List instances with specific tag
aws ec2 describe-instances \
    --filters "Name=tag:Environment,Values=Production"

# Output in table format
aws ec2 describe-instances \
    --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,PublicIpAddress]' \
    --output table
```

### Describe Instance Types

```bash
# List all available instance types
aws ec2 describe-instance-types

# Get details for specific type
aws ec2 describe-instance-types \
    --instance-types m5.large

# Filter by vCPUs
aws ec2 describe-instance-types \
    --filters "Name=vcpu-info.default-vcpus,Values=4"

# Filter by memory (in MB)
aws ec2 describe-instance-types \
    --filters "Name=memory-info.size-in-mib,Values=16384"
```

### Instance Lifecycle Commands

```bash
# Start an instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0

# Stop an instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Reboot an instance
aws ec2 reboot-instances --instance-ids i-1234567890abcdef0

# Terminate an instance
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Change instance type (must be stopped first)
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --instance-type "{\"Value\": \"m5.xlarge\"}"
```

---

## CloudFormation Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 Instance with different instance types'

Parameters:
  EnvironmentType:
    Description: The environment type
    Type: String
    Default: development
    AllowedValues:
      - development
      - testing
      - production
    ConstraintDescription: Must be development, testing, or production

  InstanceTypeParameter:
    Description: EC2 instance type
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - m5.large
      - m5.xlarge
      - c5.large
      - r5.large

Mappings:
  EnvironmentToInstanceType:
    development:
      instanceType: t3.micro
    testing:
      instanceType: t3.small
    production:
      instanceType: m5.large

  RegionAMI:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    us-west-2:
      AMI: ami-0892d3c7ee96c0bf7
    eu-west-1:
      AMI: ami-0d75513e7a9b0e7a7

Resources:
  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionAMI, !Ref 'AWS::Region', AMI]
      InstanceType: !FindInMap [EnvironmentToInstanceType, !Ref EnvironmentType, instanceType]
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentType}-server'
        - Key: Environment
          Value: !Ref EnvironmentType

Outputs:
  InstanceId:
    Description: Instance ID
    Value: !Ref EC2Instance

  InstanceType:
    Description: Instance Type
    Value: !GetAtt EC2Instance.InstanceType

  PublicIP:
    Description: Public IP address
    Value: !GetAtt EC2Instance.PublicIp
```

---

## Troubleshooting Guide

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Instance won't start | Insufficient capacity | Try different AZ or instance type |
| Instance stuck in pending | AMI issues | Check AMI status, try different AMI |
| Cannot connect | Security group | Check inbound rules for SSH/RDP |
| Performance issues | Wrong instance type | Monitor CloudWatch, right-size |
| High CPU credits usage | Undersized T instance | Upgrade instance or switch to M |

### Status Checks

```bash
# View instance status checks
aws ec2 describe-instance-status \
    --instance-ids i-1234567890abcdef0

# System Status Check: AWS infrastructure issues
# Instance Status Check: Guest OS issues
```

### Performance Troubleshooting

```bash
# Check instance metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 300 \
    --statistics Average Maximum

# On the instance - check processes
top -bn1 | head -20

# Check memory usage
free -h

# Check disk usage
df -h
```

---

## Key Takeaways

1. **Instance families** are optimized for different workloads (T/M for general, C for compute, R for memory)
2. **T instances** use CPU credits and are ideal for variable workloads
3. **M instances** provide balanced resources for consistent workloads
4. **Always start small** and scale based on monitored metrics
5. **Graviton instances** (suffix 'g') offer better price-performance for ARM-compatible workloads
6. **Latest generations** (7th gen) offer best performance per dollar
7. **Right-sizing** is an ongoing process, not a one-time decision

---

## Next Steps

Continue to [02-ami-and-marketplace.md](./02-ami-and-marketplace.md) to learn about Amazon Machine Images and the AWS Marketplace.
