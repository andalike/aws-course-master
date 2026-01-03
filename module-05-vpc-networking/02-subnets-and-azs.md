# 02 - Subnets and Availability Zones

## Understanding Subnets

A subnet is a range of IP addresses in your VPC. Subnets allow you to group resources based on security and operational needs.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUBNET CONCEPT                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC: 10.0.0.0/16 ─────────► "The Building"                                │
│         │                                                                    │
│         ├── Subnet A: 10.0.1.0/24 ───► "Floor 1 - Public Reception"         │
│         │                                                                    │
│         ├── Subnet B: 10.0.2.0/24 ───► "Floor 2 - Private Offices"          │
│         │                                                                    │
│         └── Subnet C: 10.0.3.0/24 ───► "Basement - Secure Vault"            │
│                                                                              │
│   Each subnet has its own:                                                   │
│   • IP address range (CIDR block)                                           │
│   • Route table                                                              │
│   • Network ACL                                                              │
│   • Availability Zone                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Public vs Private Subnets

The distinction between public and private subnets is determined by routing, not by any inherent property.

### What Makes a Subnet Public?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PUBLIC SUBNET REQUIREMENTS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PUBLIC SUBNET = Route to Internet Gateway + Public IP Assignment          │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      PUBLIC SUBNET                                   │   │
│   │                                                                      │   │
│   │   ┌─────────────┐         Route Table:                              │   │
│   │   │    EC2      │         ┌────────────────────────────────┐        │   │
│   │   │ Public IP:  │         │ Destination    │ Target        │        │   │
│   │   │ 54.x.x.x    │         ├────────────────┼───────────────┤        │   │
│   │   │             │         │ 10.0.0.0/16    │ local         │        │   │
│   │   │ Private IP: │         │ 0.0.0.0/0      │ igw-xxxxxx ◄──┼── IGW  │   │
│   │   │ 10.0.1.10   │         └────────────────┴───────────────┘        │   │
│   │   └──────┬──────┘                                                    │   │
│   │          │                                                           │   │
│   │          ▼                                                           │   │
│   │   ┌─────────────────┐                                               │   │
│   │   │ Internet Gateway│ ◄──────── Attached to VPC                     │   │
│   │   └────────┬────────┘                                               │   │
│   │            │                                                         │   │
│   │            ▼                                                         │   │
│   │        INTERNET                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What Makes a Subnet Private?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRIVATE SUBNET CHARACTERISTICS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PRIVATE SUBNET = No direct route to IGW (routes through NAT if needed)    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      PRIVATE SUBNET                                  │   │
│   │                                                                      │   │
│   │   ┌─────────────┐         Route Table:                              │   │
│   │   │    EC2      │         ┌────────────────────────────────┐        │   │
│   │   │ NO Public   │         │ Destination    │ Target        │        │   │
│   │   │ IP          │         ├────────────────┼───────────────┤        │   │
│   │   │             │         │ 10.0.0.0/16    │ local         │        │   │
│   │   │ Private IP: │         │ 0.0.0.0/0      │ nat-xxxxxx ◄──┼── NAT  │   │
│   │   │ 10.0.2.10   │         └────────────────┴───────────────┘        │   │
│   │   └──────┬──────┘                                                    │   │
│   │          │                                                           │   │
│   │          ▼                                                           │   │
│   │   ┌──────────────────┐                                              │   │
│   │   │   NAT Gateway    │ (in public subnet)                           │   │
│   │   └────────┬─────────┘                                              │   │
│   │            │                                                         │   │
│   │            ▼                                                         │   │
│   │   ┌─────────────────┐                                               │   │
│   │   │ Internet Gateway│                                               │   │
│   │   └────────┬────────┘                                               │   │
│   │            ▼                                                         │   │
│   │        INTERNET (outbound only)                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Comparison Table

| Feature | Public Subnet | Private Subnet |
|---------|---------------|----------------|
| Route to IGW | Yes (0.0.0.0/0 → IGW) | No |
| Public IP | Auto-assign enabled | Not assigned |
| Internet Access | Direct (inbound + outbound) | Via NAT (outbound only) |
| Use Cases | Web servers, bastion hosts | Databases, application servers |
| Security Level | Lower (internet exposed) | Higher (isolated) |

## Availability Zones

Availability Zones (AZs) are isolated locations within a region. Each AZ has independent power, cooling, and networking.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AWS REGION: us-east-1                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐              │
│   │   AZ: 1a      │    │   AZ: 1b      │    │   AZ: 1c      │   ...        │
│   │               │    │               │    │               │              │
│   │ ┌───────────┐ │    │ ┌───────────┐ │    │ ┌───────────┐ │              │
│   │ │Data Center│ │    │ │Data Center│ │    │ │Data Center│ │              │
│   │ │  Cluster  │ │    │ │  Cluster  │ │    │ │  Cluster  │ │              │
│   │ └───────────┘ │    │ └───────────┘ │    │ └───────────┘ │              │
│   │               │    │               │    │               │              │
│   │ • Independent │    │ • Independent │    │ • Independent │              │
│   │   power       │    │   power       │    │   power       │              │
│   │ • Independent │    │ • Independent │    │ • Independent │              │
│   │   network     │    │   network     │    │   network     │              │
│   │ • Independent │    │ • Independent │    │ • Independent │              │
│   │   cooling     │    │   cooling     │    │   cooling     │              │
│   │               │    │               │    │               │              │
│   └───────┬───────┘    └───────┬───────┘    └───────┬───────┘              │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                │                                            │
│                    ┌───────────▼───────────┐                               │
│                    │  High-Speed Private   │                               │
│                    │  Fiber Connections    │                               │
│                    │  (< 1ms latency)      │                               │
│                    └───────────────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AZ Naming Convention

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AZ NAMING AND MAPPING                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Account A:                           Account B:                           │
│   us-east-1a → Physical AZ "X"         us-east-1a → Physical AZ "Y"        │
│   us-east-1b → Physical AZ "Y"         us-east-1b → Physical AZ "Z"        │
│   us-east-1c → Physical AZ "Z"         us-east-1c → Physical AZ "X"        │
│                                                                              │
│   ⚠️  AZ names are MAPPED DIFFERENTLY per account!                          │
│                                                                              │
│   Use AZ IDs for consistent reference:                                      │
│   • use1-az1                                                                │
│   • use1-az2                                                                │
│   • use1-az4                                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Subnet Sizing Best Practices

### Calculating Subnet Size

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SUBNET SIZING WORKSHEET                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Step 1: Count required resources                                          │
│   ───────────────────────────────────                                       │
│   EC2 instances:              50                                            │
│   Load balancer nodes:         2                                            │
│   Lambda ENIs:                20                                            │
│   RDS instances:               2                                            │
│   ElastiCache nodes:           3                                            │
│   ─────────────────────────────────                                         │
│   Subtotal:                   77                                            │
│                                                                              │
│   Step 2: Add growth buffer (2-3x)                                          │
│   ─────────────────────────────────                                         │
│   77 × 2.5 = 193                                                            │
│                                                                              │
│   Step 3: Add AWS reserved (5)                                              │
│   ─────────────────────────────────                                         │
│   193 + 5 = 198                                                             │
│                                                                              │
│   Step 4: Find appropriate CIDR                                             │
│   ─────────────────────────────────                                         │
│   /24 = 256 IPs (251 usable) ✓                                              │
│   /25 = 128 IPs (123 usable) ✗ Too small                                    │
│                                                                              │
│   Recommendation: Use /24 subnet                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Subnet Size Recommendations by Use Case

| Use Case | Recommended CIDR | Usable IPs | Notes |
|----------|------------------|------------|-------|
| Public/Web Tier | /24 | 251 | Load balancers, NAT GW, bastion |
| Application Tier | /23 or /22 | 507-1,019 | Auto-scaling groups |
| Database Tier | /24 or /25 | 123-251 | Fixed instance count |
| Lambda Functions | /22 or /21 | 1,019-2,043 | ENI scaling |
| Container/EKS | /19 or /18 | 8,187-16,379 | Many pods per node |

## Multi-AZ Architecture

### High Availability Design Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-AZ VPC ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                            ┌───────────────┐                                │
│                            │   Internet    │                                │
│                            └───────┬───────┘                                │
│                                    │                                         │
│                            ┌───────▼───────┐                                │
│                            │Internet Gateway│                               │
│                            └───────┬───────┘                                │
│                                    │                                         │
│   ┌────────────────────────────────┼────────────────────────────────┐       │
│   │                     VPC: 10.0.0.0/16                            │       │
│   │                                │                                 │       │
│   │         ┌──────────────────────┼──────────────────────┐         │       │
│   │         │                      │                      │         │       │
│   │         ▼                      ▼                      ▼         │       │
│   │   ┌───────────┐          ┌───────────┐          ┌───────────┐   │       │
│   │   │    ALB    │──────────│    ALB    │──────────│    ALB    │   │       │
│   │   │   Node    │          │   Node    │          │   Node    │   │       │
│   │   └─────┬─────┘          └─────┬─────┘          └─────┬─────┘   │       │
│   │         │                      │                      │         │       │
│   │   ┌─────▼─────┐          ┌─────▼─────┐          ┌─────▼─────┐   │       │
│   │   │  PUBLIC   │          │  PUBLIC   │          │  PUBLIC   │   │       │
│   │   │10.0.1.0/24│          │10.0.2.0/24│          │10.0.3.0/24│   │       │
│   │   │   AZ-1a   │          │   AZ-1b   │          │   AZ-1c   │   │       │
│   │   │┌─────────┐│          │┌─────────┐│          │┌─────────┐│   │       │
│   │   ││ NAT GW  ││          ││ NAT GW  ││          ││ NAT GW  ││   │       │
│   │   │└─────────┘│          │└─────────┘│          │└─────────┘│   │       │
│   │   └─────┬─────┘          └─────┬─────┘          └─────┬─────┘   │       │
│   │         │                      │                      │         │       │
│   │   ┌─────▼─────┐          ┌─────▼─────┐          ┌─────▼─────┐   │       │
│   │   │  PRIVATE  │          │  PRIVATE  │          │  PRIVATE  │   │       │
│   │   │10.0.11.0/24│         │10.0.12.0/24│         │10.0.13.0/24│  │       │
│   │   │   AZ-1a   │          │   AZ-1b   │          │   AZ-1c   │   │       │
│   │   │┌─────────┐│          │┌─────────┐│          │┌─────────┐│   │       │
│   │   ││   EC2   ││          ││   EC2   ││          ││   EC2   ││   │       │
│   │   │└─────────┘│          │└─────────┘│          │└─────────┘│   │       │
│   │   └─────┬─────┘          └─────┬─────┘          └─────┬─────┘   │       │
│   │         │                      │                      │         │       │
│   │   ┌─────▼─────┐          ┌─────▼─────┐          ┌─────▼─────┐   │       │
│   │   │ DATABASE  │          │ DATABASE  │          │ DATABASE  │   │       │
│   │   │10.0.21.0/24│         │10.0.22.0/24│         │10.0.23.0/24│  │       │
│   │   │   AZ-1a   │          │   AZ-1b   │          │   AZ-1c   │   │       │
│   │   │┌─────────┐│          │┌─────────┐│          │┌─────────┐│   │       │
│   │   ││   RDS   ││◄────────►││   RDS   ││◄────────►││   RDS   ││   │       │
│   │   ││ Primary ││ Replica  ││ Standby ││ Replica  ││  Reader ││   │       │
│   │   │└─────────┘│          │└─────────┘│          │└─────────┘│   │       │
│   │   └───────────┘          └───────────┘          └───────────┘   │       │
│   │                                                                  │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Multi-AZ Benefits

| Benefit | Description |
|---------|-------------|
| **High Availability** | Survive AZ failure |
| **Low Latency** | Users connect to nearest AZ |
| **Disaster Recovery** | Automatic failover capability |
| **Compliance** | Meet redundancy requirements |

### Cost vs Availability Trade-offs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-AZ COST CONSIDERATIONS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Single AZ Architecture:                                                   │
│   ┌─────────────────────┐                                                   │
│   │        AZ-1a        │                                                   │
│   │  ┌───────────────┐  │   Cost: $                                        │
│   │  │ All Resources │  │   Availability: ~99.9%                           │
│   │  └───────────────┘  │   Risk: AZ failure = complete outage             │
│   └─────────────────────┘                                                   │
│                                                                              │
│   Two AZ Architecture:                                                      │
│   ┌─────────────┐  ┌─────────────┐                                         │
│   │    AZ-1a    │  │    AZ-1b    │   Cost: $$                              │
│   │ ┌─────────┐ │  │ ┌─────────┐ │   Availability: ~99.99%                 │
│   │ │Resources│ │  │ │Resources│ │   Risk: Can survive 1 AZ failure        │
│   │ └─────────┘ │  │ └─────────┘ │                                         │
│   └─────────────┘  └─────────────┘                                         │
│                                                                              │
│   Three AZ Architecture (Recommended):                                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                                    │
│   │  AZ-1a  │  │  AZ-1b  │  │  AZ-1c  │   Cost: $$$                        │
│   │┌───────┐│  │┌───────┐│  │┌───────┐│   Availability: ~99.999%           │
│   ││ Res.  ││  ││ Res.  ││  ││ Res.  ││   Risk: Can survive 2 AZ failures  │
│   │└───────┘│  │└───────┘│  │└───────┘│   (better quorum for databases)    │
│   └─────────┘  └─────────┘  └─────────┘                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Subnet Design Patterns

### Pattern 1: Simple Two-Tier

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TWO-TIER SUBNET DESIGN                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC: 10.0.0.0/16                                                          │
│                                                                              │
│   ┌───────────────────────────────┬───────────────────────────────┐         │
│   │           AZ-1a               │           AZ-1b               │         │
│   ├───────────────────────────────┼───────────────────────────────┤         │
│   │  Public: 10.0.0.0/24          │  Public: 10.0.1.0/24          │         │
│   │  Private: 10.0.2.0/24         │  Private: 10.0.3.0/24         │         │
│   └───────────────────────────────┴───────────────────────────────┘         │
│                                                                              │
│   Use case: Simple web application with database                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pattern 2: Three-Tier (Recommended)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THREE-TIER SUBNET DESIGN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC: 10.0.0.0/16                                                          │
│                                                                              │
│   ┌─────────────────────┬─────────────────────┬─────────────────────┐       │
│   │       AZ-1a         │       AZ-1b         │       AZ-1c         │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Public              │ Public              │ Public              │       │
│   │ 10.0.0.0/24         │ 10.0.1.0/24         │ 10.0.2.0/24         │       │
│   │ (ALB, NAT, Bastion) │ (ALB, NAT)          │ (ALB, NAT)          │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Private/App         │ Private/App         │ Private/App         │       │
│   │ 10.0.10.0/24        │ 10.0.11.0/24        │ 10.0.12.0/24        │       │
│   │ (EC2, Containers)   │ (EC2, Containers)   │ (EC2, Containers)   │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Private/Data        │ Private/Data        │ Private/Data        │       │
│   │ 10.0.20.0/24        │ 10.0.21.0/24        │ 10.0.22.0/24        │       │
│   │ (RDS, ElastiCache)  │ (RDS, ElastiCache)  │ (RDS, ElastiCache)  │       │
│   └─────────────────────┴─────────────────────┴─────────────────────┘       │
│                                                                              │
│   Use case: Production applications requiring security isolation            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pattern 3: Large-Scale Enterprise

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE SUBNET DESIGN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC: 10.0.0.0/16                                                          │
│                                                                              │
│   ┌─────────────────────┬─────────────────────┬─────────────────────┐       │
│   │       AZ-1a         │       AZ-1b         │       AZ-1c         │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ DMZ/Edge            │ DMZ/Edge            │ DMZ/Edge            │       │
│   │ 10.0.0.0/26         │ 10.0.0.64/26        │ 10.0.0.128/26       │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Public              │ Public              │ Public              │       │
│   │ 10.0.1.0/24         │ 10.0.2.0/24         │ 10.0.3.0/24         │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Private/Web         │ Private/Web         │ Private/Web         │       │
│   │ 10.0.10.0/23        │ 10.0.12.0/23        │ 10.0.14.0/23        │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Private/App         │ Private/App         │ Private/App         │       │
│   │ 10.0.20.0/22        │ 10.0.24.0/22        │ 10.0.28.0/22        │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Private/Data        │ Private/Data        │ Private/Data        │       │
│   │ 10.0.32.0/24        │ 10.0.33.0/24        │ 10.0.34.0/24        │       │
│   ├─────────────────────┼─────────────────────┼─────────────────────┤       │
│   │ Private/Management  │ Private/Management  │ Private/Management  │       │
│   │ 10.0.40.0/26        │ 10.0.40.64/26       │ 10.0.40.128/26      │       │
│   └─────────────────────┴─────────────────────┴─────────────────────┘       │
│                                                                              │
│   Reserved: 10.0.64.0/18 - Future expansion                                 │
│   Reserved: 10.0.128.0/17 - Additional environments                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Creating Subnets with AWS CLI

```bash
# Create public subnet in AZ-1a
aws ec2 create-subnet \
    --vpc-id vpc-12345678 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Public-1a}]'

# Create private subnet in AZ-1a
aws ec2 create-subnet \
    --vpc-id vpc-12345678 \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Private-1a}]'

# Enable auto-assign public IP for public subnet
aws ec2 modify-subnet-attribute \
    --subnet-id subnet-public1a \
    --map-public-ip-on-launch
```

## Troubleshooting Subnet Issues

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SUBNET TROUBLESHOOTING FLOWCHART                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   "Cannot create subnet"                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────┐                                                  │
│   │ CIDR overlaps with   │                                                  │
│   │ existing subnet?     │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       Yes    ├──── Use non-overlapping CIDR                                 │
│              │                                                               │
│       No     ▼                                                               │
│   ┌──────────────────────┐                                                  │
│   │ CIDR within VPC      │                                                  │
│   │ CIDR range?          │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       No     ├──── Subnet must be subset of VPC CIDR                        │
│              │                                                               │
│       Yes    ▼                                                               │
│   ┌──────────────────────┐                                                  │
│   │ AZ available in      │                                                  │
│   │ your account?        │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       No     ├──── Choose different AZ                                      │
│              │                                                               │
│       Yes    ▼                                                               │
│   ┌──────────────────────┐                                                  │
│   │ IAM permissions      │                                                  │
│   │ for CreateSubnet?    │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       No     ├──── Add ec2:CreateSubnet permission                          │
│              │                                                               │
│       Yes    ▼                                                               │
│      Contact AWS Support                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Public vs Private** is determined by route table, not naming
2. **Multi-AZ** is essential for production high availability
3. **Plan subnet sizes** with 2-3x growth buffer
4. **Three AZs** is recommended for production workloads
5. **Reserved IPs** - Remember AWS takes 5 per subnet

---

**Next:** [03-internet-gateway-nat.md](03-internet-gateway-nat.md) - Internet connectivity options
