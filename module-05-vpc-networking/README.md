# Module 05: VPC and Networking

## Module Overview

Amazon Virtual Private Cloud (VPC) is the foundational networking layer of AWS. Understanding VPC is critical for any AWS architect, developer, or administrator. This module provides comprehensive coverage of AWS networking concepts, from basic VPC components to advanced architectures involving Transit Gateway, Direct Connect, and global content delivery.

## Why Networking Matters in AWS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE NETWORKING FOUNDATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│   │   Compute   │    │   Storage   │    │  Database   │    │   Security  │  │
│   │    (EC2)    │    │    (S3)     │    │   (RDS)     │    │   (IAM)     │  │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│          │                  │                  │                  │          │
│          └──────────────────┴──────────────────┴──────────────────┘          │
│                                    │                                         │
│                        ┌───────────▼───────────┐                            │
│                        │      NETWORKING       │                            │
│                        │   (VPC, Route 53,     │                            │
│                        │  CloudFront, ELB)     │                            │
│                        └───────────────────────┘                            │
│                                                                              │
│   "Networking is the foundation upon which all other services depend"       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Reasons Networking is Critical

1. **Security Isolation** - VPCs provide network-level isolation for your resources
2. **Compliance Requirements** - Many regulations require private network connectivity
3. **Cost Optimization** - Proper network design reduces data transfer costs
4. **Performance** - Network architecture directly impacts application latency
5. **Hybrid Connectivity** - Connects on-premises infrastructure to AWS

## Learning Objectives

By the end of this module, you will be able to:

### Foundation Level
- [ ] Understand VPC components and their relationships
- [ ] Design CIDR blocks for optimal IP address allocation
- [ ] Differentiate between public and private subnets
- [ ] Configure Internet Gateway and NAT Gateway

### Intermediate Level
- [ ] Implement Security Groups and NACLs effectively
- [ ] Set up VPC peering and understand its limitations
- [ ] Configure VPC endpoints for AWS service access
- [ ] Design multi-AZ architectures for high availability

### Advanced Level
- [ ] Architect hub-spoke topologies with Transit Gateway
- [ ] Plan hybrid connectivity with VPN and Direct Connect
- [ ] Implement global content delivery with CloudFront
- [ ] Design DNS strategies with Route 53

## Module Structure

| File | Topic | Duration |
|------|-------|----------|
| 01-vpc-fundamentals.md | VPC basics, CIDR, Default VPC | 45 min |
| 02-subnets-and-azs.md | Subnet design, Multi-AZ | 40 min |
| 03-internet-gateway-nat.md | IGW, NAT Gateway/Instance | 35 min |
| 04-route-tables.md | Routing concepts | 30 min |
| 05-security-groups-nacls.md | Network security | 45 min |
| 06-vpc-peering.md | VPC connectivity | 30 min |
| 07-vpc-endpoints.md | Private AWS access | 35 min |
| 08-vpn-direct-connect.md | Hybrid connectivity | 45 min |
| 09-transit-gateway.md | Advanced networking | 40 min |
| 10-elastic-load-balancing.md | Load balancer types | 50 min |
| 11-route53.md | DNS and routing | 45 min |
| 12-cloudfront.md | CDN and caching | 40 min |
| 13-hands-on-labs.md | Practical exercises | 180 min |
| quiz.md | Assessment | 30 min |

**Total Estimated Time: 10-12 hours**

## Prerequisites

Before starting this module, you should have:

- AWS account with appropriate permissions
- Basic understanding of networking concepts (IP addresses, ports, protocols)
- Familiarity with the AWS Management Console
- Completion of Module 01-04 (recommended)

## Key Concepts Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VPC COMPONENT HIERARCHY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Region (e.g., us-east-1)                                                  │
│   │                                                                          │
│   └── VPC (10.0.0.0/16)                                                     │
│       │                                                                      │
│       ├── Availability Zone 1 (us-east-1a)                                  │
│       │   ├── Public Subnet (10.0.1.0/24)                                   │
│       │   │   └── EC2, NAT Gateway, Load Balancer                           │
│       │   └── Private Subnet (10.0.2.0/24)                                  │
│       │       └── EC2, RDS, ElastiCache                                     │
│       │                                                                      │
│       ├── Availability Zone 2 (us-east-1b)                                  │
│       │   ├── Public Subnet (10.0.3.0/24)                                   │
│       │   └── Private Subnet (10.0.4.0/24)                                  │
│       │                                                                      │
│       ├── Internet Gateway                                                  │
│       ├── NAT Gateway                                                       │
│       ├── Route Tables                                                       │
│       ├── Security Groups                                                   │
│       └── Network ACLs                                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Exam Tips for AWS Certifications

This module covers topics heavily tested in:
- **AWS Solutions Architect Associate (SAA-C03)**
- **AWS Solutions Architect Professional (SAP-C02)**
- **AWS Advanced Networking Specialty (ANS-C01)**

### High-Priority Topics
1. VPC peering limitations (no transitive peering)
2. Security Groups vs NACLs (stateful vs stateless)
3. NAT Gateway vs NAT Instance differences
4. Transit Gateway use cases
5. Route 53 routing policies
6. CloudFront signed URLs vs signed cookies

## Resources

### AWS Documentation
- [VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/)
- [Route 53 Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/)
- [CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/)

### Additional Learning
- AWS re:Invent networking sessions
- AWS Networking blog posts
- AWS Well-Architected Framework - Reliability Pillar

---

**Next:** [01-vpc-fundamentals.md](01-vpc-fundamentals.md) - Start with VPC basics and CIDR blocks
