# 01 - VPC Fundamentals

## What is Amazon VPC?

Amazon Virtual Private Cloud (VPC) is a logically isolated section of the AWS cloud where you can launch AWS resources in a virtual network that you define. You have complete control over your virtual networking environment, including:

- Selection of IP address ranges
- Creation of subnets
- Configuration of route tables
- Network gateways

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         YOUR VPC (10.0.0.0/16)                         │  │
│  │                                                                        │  │
│  │   ┌─────────────────────┐         ┌─────────────────────┐             │  │
│  │   │   Public Subnet     │         │   Private Subnet    │             │  │
│  │   │   10.0.1.0/24       │         │   10.0.2.0/24       │             │  │
│  │   │                     │         │                     │             │  │
│  │   │   ┌─────────┐       │         │   ┌─────────┐       │             │  │
│  │   │   │   EC2   │       │         │   │   RDS   │       │             │  │
│  │   │   └─────────┘       │         │   └─────────┘       │             │  │
│  │   │                     │         │                     │             │  │
│  │   └─────────────────────┘         └─────────────────────┘             │  │
│  │                                                                        │  │
│  │   Your isolated network space - YOU control who gets in!              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   Other customers' VPCs (completely isolated from yours)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Key Characteristics

| Feature | Description |
|---------|-------------|
| **Region-Specific** | A VPC spans all Availability Zones in a region |
| **Soft Limit** | 5 VPCs per region (can be increased) |
| **CIDR Range** | /16 (65,536 IPs) to /28 (16 IPs) |
| **Tenancy** | Default (shared) or Dedicated hardware |
| **DNS** | Optional DNS hostnames and resolution |

## Default VPC

Every AWS account comes with a default VPC in each region.

### Default VPC Characteristics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEFAULT VPC STRUCTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC: 172.31.0.0/16 (65,536 IP addresses)                                  │
│                                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │   Subnet 1   │  │   Subnet 2   │  │   Subnet 3   │  │   Subnet N   │   │
│   │172.31.0.0/20 │  │172.31.16.0/20│  │172.31.32.0/20│  │    .../20    │   │
│   │    AZ-1a     │  │    AZ-1b     │  │    AZ-1c     │  │    AZ-1n     │   │
│   │  4,096 IPs   │  │  4,096 IPs   │  │  4,096 IPs   │  │  4,096 IPs   │   │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                              │
│   ✓ Internet Gateway attached                                               │
│   ✓ Default route table with route to IGW                                   │
│   ✓ Default Security Group                                                  │
│   ✓ Default Network ACL                                                     │
│   ✓ DHCP options set configured                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Default vs Custom VPC Comparison

| Feature | Default VPC | Custom VPC |
|---------|-------------|------------|
| CIDR Block | 172.31.0.0/16 | You choose |
| Subnets | One per AZ (public) | You create |
| Internet Gateway | Pre-attached | You attach |
| Route Table | Routes to IGW | You configure |
| Security Group | Default created | You create |
| EC2 Public IP | Auto-assigned | You choose |

> **Best Practice:** Use custom VPCs for production workloads. Default VPCs are convenient for learning but don't provide the security isolation needed for production.

## CIDR Blocks (Classless Inter-Domain Routing)

CIDR notation defines IP address ranges. Understanding CIDR is essential for VPC design.

### CIDR Notation Explained

```
         IP Address      /    Prefix Length
             │                     │
             ▼                     ▼
        10.0.0.0         /        16
             │                     │
             │                     └── Network bits (fixed)
             └── Base network address


    10  .   0   .   0   .   0
    │       │       │       │
  8 bits  8 bits  8 bits  8 bits = 32 bits total

  For /16:
  ├── 16 bits network ──┤├── 16 bits host ──┤
       (FIXED)                (VARIABLE)
```

### CIDR Block Size Reference

| CIDR | Subnet Mask | Total IPs | Usable IPs* | Use Case |
|------|-------------|-----------|-------------|----------|
| /16 | 255.255.0.0 | 65,536 | 65,531 | Large VPC |
| /17 | 255.255.128.0 | 32,768 | 32,763 | Large VPC |
| /18 | 255.255.192.0 | 16,384 | 16,379 | Medium VPC |
| /19 | 255.255.224.0 | 8,192 | 8,187 | Medium VPC |
| /20 | 255.255.240.0 | 4,096 | 4,091 | Default subnet |
| /21 | 255.255.248.0 | 2,048 | 2,043 | Medium subnet |
| /22 | 255.255.252.0 | 1,024 | 1,019 | Medium subnet |
| /23 | 255.255.254.0 | 512 | 507 | Small subnet |
| /24 | 255.255.255.0 | 256 | 251 | Common subnet |
| /25 | 255.255.255.128 | 128 | 123 | Small subnet |
| /26 | 255.255.255.192 | 64 | 59 | Small subnet |
| /27 | 255.255.255.224 | 32 | 27 | Tiny subnet |
| /28 | 255.255.255.240 | 16 | 11 | Minimum VPC |

*AWS reserves 5 IP addresses in each subnet

### AWS Reserved IP Addresses

In each subnet, AWS reserves 5 IP addresses:

```
Example: Subnet 10.0.1.0/24 (256 total IPs)

┌─────────────────────────────────────────────────────────────────────────────┐
│                          RESERVED IP ADDRESSES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   10.0.1.0     - Network address (cannot be used)                           │
│   10.0.1.1     - Reserved for VPC router                                    │
│   10.0.1.2     - Reserved for DNS (Amazon-provided)                         │
│   10.0.1.3     - Reserved for future use                                    │
│   10.0.1.255   - Broadcast address (not supported in VPC)                   │
│                                                                              │
│   Usable IPs: 10.0.1.4 to 10.0.1.254 = 251 addresses                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### CIDR Calculation Examples

**Example 1: Calculate available IPs for 10.0.0.0/20**

```
Step 1: Calculate host bits
         32 (total) - 20 (network) = 12 host bits

Step 2: Calculate total IPs
         2^12 = 4,096 total IP addresses

Step 3: Calculate usable IPs
         4,096 - 5 (reserved) = 4,091 usable

Answer: 4,091 usable IP addresses
```

**Example 2: What CIDR block for 500 hosts?**

```
Step 1: Add reserved IPs
         500 + 5 = 505 minimum IPs needed

Step 2: Find smallest power of 2 >= 505
         2^9 = 512 ✓ (next is 2^8 = 256, too small)

Step 3: Calculate prefix length
         32 - 9 = /23

Answer: Use /23 (512 IPs, 507 usable)
```

### CIDR Block Planning Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC CIDR PLANNING EXAMPLE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC: 10.0.0.0/16 (65,536 IPs)                                             │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Production Environment: 10.0.0.0/17 (32,768 IPs)                    │   │
│   │                                                                      │   │
│   │   AZ-1a                    AZ-1b                    AZ-1c           │   │
│   │   ┌──────────────┐         ┌──────────────┐         ┌────────────┐  │   │
│   │   │Public        │         │Public        │         │Public      │  │   │
│   │   │10.0.0.0/20   │         │10.0.16.0/20  │         │10.0.32.0/20│  │   │
│   │   └──────────────┘         └──────────────┘         └────────────┘  │   │
│   │   ┌──────────────┐         ┌──────────────┐         ┌────────────┐  │   │
│   │   │Private       │         │Private       │         │Private     │  │   │
│   │   │10.0.48.0/20  │         │10.0.64.0/20  │         │10.0.80.0/20│  │   │
│   │   └──────────────┘         └──────────────┘         └────────────┘  │   │
│   │   ┌──────────────┐         ┌──────────────┐         ┌────────────┐  │   │
│   │   │Database      │         │Database      │         │Database    │  │   │
│   │   │10.0.96.0/21  │         │10.0.104.0/21 │         │10.0.112.0/21│ │   │
│   │   └──────────────┘         └──────────────┘         └────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Development Environment: 10.0.128.0/17 (32,768 IPs) - Reserved      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Subnets Overview

Subnets are subdivisions of a VPC's IP address range where you place resources.

### Subnet Key Points

- **AZ-Specific**: Each subnet exists in exactly one Availability Zone
- **Non-Overlapping**: Subnet CIDRs cannot overlap within a VPC
- **Public vs Private**: Determined by route table, not an inherent property

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             VPC: 10.0.0.0/16                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│        Availability Zone A              Availability Zone B                  │
│   ┌────────────────────────────┐   ┌────────────────────────────┐           │
│   │                            │   │                            │           │
│   │  ┌──────────────────────┐  │   │  ┌──────────────────────┐  │           │
│   │  │   PUBLIC SUBNET      │  │   │  │   PUBLIC SUBNET      │  │           │
│   │  │   10.0.1.0/24        │  │   │  │   10.0.3.0/24        │  │           │
│   │  │   251 usable IPs     │  │   │  │   251 usable IPs     │  │           │
│   │  │                      │  │   │  │                      │  │           │
│   │  │   Route: 0.0.0.0/0   │  │   │  │   Route: 0.0.0.0/0   │  │           │
│   │  │         → IGW        │  │   │  │         → IGW        │  │           │
│   │  └──────────────────────┘  │   │  └──────────────────────┘  │           │
│   │                            │   │                            │           │
│   │  ┌──────────────────────┐  │   │  ┌──────────────────────┐  │           │
│   │  │   PRIVATE SUBNET     │  │   │  │   PRIVATE SUBNET     │  │           │
│   │  │   10.0.2.0/24        │  │   │  │   10.0.4.0/24        │  │           │
│   │  │   251 usable IPs     │  │   │  │   251 usable IPs     │  │           │
│   │  │                      │  │   │  │                      │  │           │
│   │  │   Route: 0.0.0.0/0   │  │   │  │   Route: 0.0.0.0/0   │  │           │
│   │  │         → NAT GW     │  │   │  │         → NAT GW     │  │           │
│   │  └──────────────────────┘  │   │  └──────────────────────┘  │           │
│   │                            │   │                            │           │
│   └────────────────────────────┘   └────────────────────────────┘           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Components Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VPC COMPONENT REFERENCE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Component           │ Scope        │ Purpose                              │
│   ────────────────────┼──────────────┼───────────────────────────────────── │
│   VPC                 │ Region       │ Isolated virtual network             │
│   Subnet              │ AZ           │ IP address range segment             │
│   Route Table         │ VPC/Subnet   │ Traffic routing rules                │
│   Internet Gateway    │ VPC          │ Internet connectivity                │
│   NAT Gateway         │ AZ           │ Outbound internet for private        │
│   Security Group      │ VPC          │ Instance-level firewall              │
│   Network ACL         │ Subnet       │ Subnet-level firewall                │
│   VPC Endpoint        │ VPC          │ Private AWS service access           │
│   VPC Peering         │ Cross-VPC    │ VPC-to-VPC connectivity              │
│   Transit Gateway     │ Region       │ Hub for multiple VPCs                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Creating a VPC with AWS CLI

```bash
# Create VPC
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyVPC}]'

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id vpc-12345678 \
    --enable-dns-hostnames '{"Value":true}'

# Enable DNS resolution
aws ec2 modify-vpc-attribute \
    --vpc-id vpc-12345678 \
    --enable-dns-support '{"Value":true}'
```

## Best Practices

1. **Plan CIDR blocks carefully** - Cannot modify primary CIDR after creation
2. **Avoid overlapping CIDRs** - Especially if planning VPC peering or hybrid connectivity
3. **Use RFC 1918 ranges** - 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
4. **Leave room for growth** - Use larger blocks than immediately needed
5. **Document your IP scheme** - Maintain an IP address management (IPAM) record

## Common CIDR Mistakes to Avoid

| Mistake | Problem | Solution |
|---------|---------|----------|
| Too small VPC CIDR | Running out of IPs | Start with /16 for production |
| Overlapping CIDRs | Cannot peer VPCs | Plan across all VPCs |
| Using 172.31.x.x | Conflicts with default VPC | Use 10.x.x.x instead |
| No future planning | No room for expansion | Reserve extra CIDR blocks |

## Troubleshooting Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC CREATION TROUBLESHOOTING                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   VPC Creation Failed?                                                       │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────┐                                                      │
│   │ Check CIDR block │                                                      │
│   │ validity         │                                                      │
│   └────────┬─────────┘                                                      │
│            │                                                                 │
│     Valid? ├──── No ───► Fix CIDR: Must be /16 to /28                       │
│            │                                                                 │
│     Yes    ▼                                                                 │
│   ┌──────────────────┐                                                      │
│   │ Check VPC limit  │                                                      │
│   │ (5 per region)   │                                                      │
│   └────────┬─────────┘                                                      │
│            │                                                                 │
│   Reached? ├──── Yes ──► Request limit increase                             │
│            │                                                                 │
│     No     ▼                                                                 │
│   ┌──────────────────┐                                                      │
│   │ Check IAM        │                                                      │
│   │ permissions      │                                                      │
│   └────────┬─────────┘                                                      │
│            │                                                                 │
│ Permitted? ├──── No ───► Add ec2:CreateVpc permission                       │
│            │                                                                 │
│     Yes    ▼                                                                 │
│   ┌──────────────────┐                                                      │
│   │ Contact AWS      │                                                      │
│   │ Support          │                                                      │
│   └──────────────────┘                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. VPC is your isolated network space in AWS
2. CIDR blocks define your IP address range
3. Plan for growth - CIDR changes are limited
4. Understand reserved IPs (5 per subnet)
5. Default VPC is convenient but use custom VPCs for production

---

**Next:** [02-subnets-and-azs.md](02-subnets-and-azs.md) - Deep dive into subnets and multi-AZ architecture
