# Module 03: Amazon EC2 (Elastic Compute Cloud)

## Module Overview

Amazon Elastic Compute Cloud (Amazon EC2) is the backbone of AWS compute services. It provides scalable computing capacity in the AWS cloud, eliminating the need to invest in hardware upfront. EC2 enables you to develop and deploy applications faster, launch as many or as few virtual servers as you need, configure security and networking, and manage storage.

This module provides comprehensive coverage of EC2, from fundamental concepts to advanced configurations, preparing you for real-world deployments and AWS certification exams.

---

## Why EC2 is Critical

### The Foundation of Cloud Computing

EC2 is often the first service that organizations adopt when migrating to AWS. Understanding EC2 is essential because:

1. **Core Compute Service**: EC2 powers most AWS workloads, from simple web servers to complex distributed systems
2. **Foundation for Other Services**: Many AWS services (ECS, EKS, Elastic Beanstalk) run on EC2 under the hood
3. **Exam Importance**: EC2 features heavily in all AWS certifications
4. **Cost Management**: EC2 often represents the largest portion of AWS bills
5. **Career Essential**: Every AWS professional must master EC2

### Real-World Applications

| Use Case | Description |
|----------|-------------|
| Web Hosting | Host websites and web applications |
| Application Servers | Run backend services and APIs |
| Development/Testing | Create development and staging environments |
| Big Data Processing | Run Hadoop, Spark, and analytics workloads |
| Machine Learning | Train and deploy ML models |
| Gaming | Host game servers and backends |
| High-Performance Computing | Run scientific simulations |

---

## Learning Objectives

By the end of this module, you will be able to:

### Fundamental Skills
- [ ] Explain what EC2 is and its role in cloud computing
- [ ] Differentiate between EC2 instance families and their use cases
- [ ] Understand the EC2 pricing models and optimize costs
- [ ] Launch and configure EC2 instances using the console and CLI

### Intermediate Skills
- [ ] Create and manage Amazon Machine Images (AMIs)
- [ ] Configure security groups and network access
- [ ] Attach and manage EBS volumes and snapshots
- [ ] Connect to instances using SSH, Session Manager, and EC2 Instance Connect

### Advanced Skills
- [ ] Design and implement Auto Scaling solutions
- [ ] Configure Application and Network Load Balancers
- [ ] Implement cost optimization strategies using Spot and Reserved Instances
- [ ] Troubleshoot common EC2 issues

---

## Module Contents

| File | Topic | Duration |
|------|-------|----------|
| [01-ec2-fundamentals.md](./01-ec2-fundamentals.md) | EC2 Basics & Instance Types | 45 min |
| [02-ami-and-marketplace.md](./02-ami-and-marketplace.md) | AMIs and AWS Marketplace | 30 min |
| [03-launching-instances.md](./03-launching-instances.md) | Launch Wizard & User Data | 45 min |
| [04-storage-options.md](./04-storage-options.md) | EBS, Instance Store, Snapshots | 60 min |
| [05-security-groups.md](./05-security-groups.md) | Security Groups Deep Dive | 45 min |
| [06-key-pairs-and-access.md](./06-key-pairs-and-access.md) | Access Methods & SSH | 30 min |
| [07-elastic-ips-and-eni.md](./07-elastic-ips-and-eni.md) | Networking Components | 30 min |
| [08-ec2-pricing.md](./08-ec2-pricing.md) | Pricing Models & Optimization | 45 min |
| [09-auto-scaling.md](./09-auto-scaling.md) | Auto Scaling Deep Dive | 60 min |
| [10-load-balancing.md](./10-load-balancing.md) | Elastic Load Balancing | 60 min |
| [11-hands-on-labs.md](./11-hands-on-labs.md) | Practical Labs (7 Labs) | 180 min |
| [quiz.md](./quiz.md) | Module Assessment | 30 min |

**Total Estimated Time: 10-12 hours**

---

## Prerequisites

Before starting this module, ensure you have:

1. **AWS Account**: Active AWS account with appropriate permissions
2. **AWS CLI**: Installed and configured with credentials
3. **Basic Knowledge**:
   - Linux command line basics
   - Networking fundamentals (IP addresses, ports, protocols)
   - Basic understanding of virtualization
4. **Completed Modules**:
   - Module 01: AWS Fundamentals
   - Module 02: IAM and Security

---

## Key Concepts Preview

### EC2 Instance Lifecycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Pending   │────▶│   Running   │────▶│  Stopping   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           │                   ▼
                           │            ┌─────────────┐
                           │            │   Stopped   │
                           │            └─────────────┘
                           │                   │
                           ▼                   │
                    ┌─────────────┐            │
                    │Shutting-down│◀───────────┘
                    └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Terminated  │
                    └─────────────┘
```

### Instance Types at a Glance

| Family | Purpose | Use Case Example |
|--------|---------|------------------|
| **T** | Burstable | Development, small web apps |
| **M** | General Purpose | Production web servers |
| **C** | Compute Optimized | Batch processing, gaming |
| **R** | Memory Optimized | In-memory databases |
| **I** | Storage Optimized | Data warehousing |
| **G/P** | GPU Instances | Machine learning, graphics |

---

## Tools You'll Use

### AWS Console
- EC2 Dashboard
- Launch Instance Wizard
- Security Groups Manager
- Auto Scaling Console

### AWS CLI Commands
```bash
# Core EC2 Commands
aws ec2 describe-instances
aws ec2 run-instances
aws ec2 start-instances
aws ec2 stop-instances
aws ec2 terminate-instances

# Security Groups
aws ec2 create-security-group
aws ec2 authorize-security-group-ingress

# EBS Volumes
aws ec2 create-volume
aws ec2 attach-volume

# AMIs
aws ec2 create-image
aws ec2 describe-images
```

### Infrastructure as Code
- AWS CloudFormation
- AWS CDK (optional)
- Terraform (optional)

---

## Cost Considerations

> **Warning**: EC2 instances incur charges while running. Always stop or terminate instances when not in use during learning.

### Free Tier Eligibility
- **750 hours/month** of t2.micro or t3.micro (Linux and Windows)
- **30 GB** of EBS storage (General Purpose SSD)
- **1 GB** of snapshots
- Valid for **12 months** from account creation

### Cost-Saving Tips for This Module
1. Use t2.micro/t3.micro instances when possible
2. Stop instances when not in use
3. Delete unused EBS volumes and snapshots
4. Use the AWS Pricing Calculator to estimate costs
5. Set up billing alerts

---

## Getting Help

### AWS Resources
- [EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/)
- [EC2 API Reference](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/)
- [AWS re:Post](https://repost.aws/)

### Troubleshooting
Each section includes a troubleshooting guide for common issues. Key resources:
- EC2 Instance Status Checks
- VPC Flow Logs
- CloudWatch Logs

---

## Next Steps

Ready to begin? Start with [01-ec2-fundamentals.md](./01-ec2-fundamentals.md) to learn the core concepts of Amazon EC2.

---

**Module Version**: 2.0
**Last Updated**: January 2025
**Compatibility**: AWS Console (Current), AWS CLI v2
