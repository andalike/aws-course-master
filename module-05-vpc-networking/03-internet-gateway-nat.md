# 03 - Internet Gateway and NAT

## Internet Gateway (IGW)

An Internet Gateway is a horizontally scaled, redundant, and highly available VPC component that allows communication between your VPC and the internet.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INTERNET GATEWAY CONCEPT                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              INTERNET                                        │
│                                 │                                            │
│                                 │                                            │
│                    ┌────────────▼────────────┐                              │
│                    │    INTERNET GATEWAY     │                              │
│                    │                         │                              │
│                    │  • Horizontally scaled  │                              │
│                    │  • Highly available     │                              │
│                    │  • No bandwidth limit   │                              │
│                    │  • No single point of   │                              │
│                    │    failure              │                              │
│                    └────────────┬────────────┘                              │
│                                 │                                            │
│   ┌─────────────────────────────┼─────────────────────────────────────────┐ │
│   │                   VPC       │                                          │ │
│   │                             │                                          │ │
│   │   ┌─────────────────────────▼─────────────────────────────────────┐   │ │
│   │   │                    PUBLIC SUBNET                               │   │ │
│   │   │                                                                │   │ │
│   │   │    ┌─────────┐    ┌─────────┐    ┌─────────┐                  │   │ │
│   │   │    │   EC2   │    │   EC2   │    │   ALB   │                  │   │ │
│   │   │    │Public IP│    │Public IP│    │         │                  │   │ │
│   │   │    └─────────┘    └─────────┘    └─────────┘                  │   │ │
│   │   │                                                                │   │ │
│   │   └────────────────────────────────────────────────────────────────┘   │ │
│   │                                                                         │ │
│   └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Internet Gateway Key Points

| Feature | Details |
|---------|---------|
| Attachment | One IGW per VPC |
| Scaling | Automatic, no limits |
| Availability | Managed by AWS, HA |
| Cost | Free (data transfer charges apply) |
| IPv6 | Supports both IPv4 and IPv6 |

### IGW Functions

1. **Route Target** - Acts as a target in route tables for internet-routable traffic
2. **NAT for Public IPs** - Performs 1:1 NAT for instances with public IPv4 addresses
3. **IPv6 Connectivity** - Provides internet connectivity for IPv6 addresses

## Setting Up Internet Connectivity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERNET CONNECTIVITY CHECKLIST                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   For an instance to communicate with the internet, you need:               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  ✓ 1. Internet Gateway attached to VPC                              │   │
│   │                                                                      │   │
│   │  ✓ 2. Route table with route to IGW:                                │   │
│   │       0.0.0.0/0 → igw-xxxxxxxx                                      │   │
│   │                                                                      │   │
│   │  ✓ 3. Public IP address (Elastic IP or auto-assigned)              │   │
│   │                                                                      │   │
│   │  ✓ 4. Security Group allows outbound traffic                        │   │
│   │                                                                      │   │
│   │  ✓ 5. Network ACL allows traffic (default allows all)               │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Missing ANY of these = NO internet connectivity!                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## NAT Gateway

NAT Gateway enables instances in private subnets to connect to the internet while preventing the internet from initiating connections to those instances.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NAT GATEWAY FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              INTERNET                                        │
│                                 │                                            │
│                                 │                                            │
│                    ┌────────────▼────────────┐                              │
│                    │    INTERNET GATEWAY     │                              │
│                    └────────────┬────────────┘                              │
│                                 │                                            │
│   ┌─────────────────────────────┼─────────────────────────────────────────┐ │
│   │                   VPC       │                                          │ │
│   │                             │                                          │ │
│   │   ┌─────────────────────────▼─────────────────────────────────────┐   │ │
│   │   │                    PUBLIC SUBNET                               │   │ │
│   │   │                                                                │   │ │
│   │   │    ┌───────────────────────────────────────┐                  │   │ │
│   │   │    │           NAT GATEWAY                 │                  │   │ │
│   │   │    │  Elastic IP: 54.x.x.x                 │                  │   │ │
│   │   │    │                                       │                  │   │ │
│   │   │    │  Translates: Private IP → Elastic IP  │                  │   │ │
│   │   │    └───────────────────┬───────────────────┘                  │   │ │
│   │   │                        │                                       │   │ │
│   │   └────────────────────────┼───────────────────────────────────────┘   │ │
│   │                            │                                            │ │
│   │   ┌────────────────────────▼───────────────────────────────────────┐   │ │
│   │   │                   PRIVATE SUBNET                                │   │ │
│   │   │                                                                 │   │ │
│   │   │    ┌─────────┐    ┌─────────┐    ┌─────────┐                   │   │ │
│   │   │    │   EC2   │    │   EC2   │    │   RDS   │                   │   │ │
│   │   │    │10.0.2.5 │    │10.0.2.6 │    │10.0.2.10│                   │   │ │
│   │   │    └─────────┘    └─────────┘    └─────────┘                   │   │ │
│   │   │                                                                 │   │ │
│   │   │    Route Table: 0.0.0.0/0 → nat-xxxxxxxx                       │   │ │
│   │   └─────────────────────────────────────────────────────────────────┘   │ │
│   │                                                                         │ │
│   └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### NAT Gateway Specifications

| Feature | Specification |
|---------|---------------|
| Bandwidth | Up to 100 Gbps (scales automatically) |
| Availability | AWS managed, HA within single AZ |
| Scope | AZ-specific resource |
| IP Address | Requires Elastic IP |
| Protocols | TCP, UDP, ICMP |
| Cost | ~$0.045/hour + data processing |

### High Availability NAT Gateway Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HA NAT GATEWAY ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │     INTERNET    │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│                         ┌────────▼────────┐                                 │
│                         │       IGW       │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│   ┌──────────────────────────────┼───────────────────────────────────┐      │
│   │                    VPC       │                                    │      │
│   │                              │                                    │      │
│   │  ┌───────────────────────────┼───────────────────────────────┐   │      │
│   │  │              ┌────────────┴────────────┐                  │   │      │
│   │  │              │                         │                  │   │      │
│   │  │   ┌──────────▼──────────┐   ┌─────────▼───────────┐      │   │      │
│   │  │   │   Public Subnet     │   │   Public Subnet     │      │   │      │
│   │  │   │       AZ-1a         │   │       AZ-1b         │      │   │      │
│   │  │   │                     │   │                     │      │   │      │
│   │  │   │  ┌──────────────┐   │   │  ┌──────────────┐   │      │   │      │
│   │  │   │  │  NAT GW - A  │   │   │  │  NAT GW - B  │   │      │   │      │
│   │  │   │  │ EIP: 54.1.x.x│   │   │  │ EIP: 54.2.x.x│   │      │   │      │
│   │  │   │  └──────┬───────┘   │   │  └──────┬───────┘   │      │   │      │
│   │  │   │         │           │   │         │           │      │   │      │
│   │  │   └─────────┼───────────┘   └─────────┼───────────┘      │   │      │
│   │  │             │                         │                   │   │      │
│   │  │   ┌─────────▼───────────┐   ┌─────────▼───────────┐      │   │      │
│   │  │   │  Private Subnet     │   │  Private Subnet     │      │   │      │
│   │  │   │       AZ-1a         │   │       AZ-1b         │      │   │      │
│   │  │   │                     │   │                     │      │   │      │
│   │  │   │  Route Table A:     │   │  Route Table B:     │      │   │      │
│   │  │   │  0.0.0.0/0 → NAT-A  │   │  0.0.0.0/0 → NAT-B  │      │   │      │
│   │  │   │                     │   │                     │      │   │      │
│   │  │   │    ┌─────────┐      │   │    ┌─────────┐      │      │   │      │
│   │  │   │    │   EC2   │      │   │    │   EC2   │      │      │   │      │
│   │  │   │    └─────────┘      │   │    └─────────┘      │      │   │      │
│   │  │   └─────────────────────┘   └─────────────────────┘      │   │      │
│   │  │                                                           │   │      │
│   │  └───────────────────────────────────────────────────────────┘   │      │
│   │                                                                   │      │
│   │  Key: Each AZ has its own NAT Gateway and route table           │      │
│   │       AZ failure = Only that AZ loses internet (others OK)      │      │
│   │                                                                   │      │
│   └───────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## NAT Gateway vs NAT Instance

### Comparison Table

| Feature | NAT Gateway | NAT Instance |
|---------|-------------|--------------|
| **Availability** | Managed by AWS, HA | You manage, use scripts |
| **Bandwidth** | Up to 100 Gbps | Depends on instance type |
| **Maintenance** | AWS managed | You patch/maintain |
| **Cost** | Higher (pay per hour + data) | Lower (EC2 pricing) |
| **Security Groups** | Cannot be associated | Can use SGs |
| **Bastion Host** | Cannot be used as | Can be combined |
| **Port Forwarding** | Not supported | Supported |
| **Traffic Metrics** | CloudWatch | CloudWatch |
| **Timeout Behavior** | 350s idle timeout | Configurable |

### NAT Instance Setup (Legacy)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NAT INSTANCE CONFIGURATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        NAT INSTANCE                                  │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  AMI: Amazon Linux NAT AMI (amzn-ami-vpc-nat-*)            │   │   │
│   │   │  or: Regular AMI with IP forwarding enabled                 │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │   Required Settings:                                                │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  1. Disable Source/Dest Check                               │   │   │
│   │   │     aws ec2 modify-instance-attribute \                     │   │   │
│   │   │       --instance-id i-xxxxx \                               │   │   │
│   │   │       --no-source-dest-check                                │   │   │
│   │   │                                                              │   │   │
│   │   │  2. Enable IP Forwarding (in OS)                            │   │   │
│   │   │     echo 1 > /proc/sys/net/ipv4/ip_forward                  │   │   │
│   │   │                                                              │   │   │
│   │   │  3. Configure iptables                                       │   │   │
│   │   │     iptables -t nat -A POSTROUTING \                        │   │   │
│   │   │       -o eth0 -j MASQUERADE                                 │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   │   Security Group:                                                   │   │
│   │   ┌──────────────────────────────────────────────────────────┐     │   │
│   │   │ Inbound:                                                  │     │   │
│   │   │   HTTP (80)   - from Private Subnet CIDR                 │     │   │
│   │   │   HTTPS (443) - from Private Subnet CIDR                 │     │   │
│   │   │                                                           │     │   │
│   │   │ Outbound:                                                 │     │   │
│   │   │   HTTP (80)   - to 0.0.0.0/0                             │     │   │
│   │   │   HTTPS (443) - to 0.0.0.0/0                             │     │   │
│   │   └──────────────────────────────────────────────────────────┘     │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use NAT Instance vs NAT Gateway

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DECISION FLOWCHART                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Need NAT functionality?                                                   │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────┐                                                  │
│   │ Need port forwarding │                                                  │
│   │ or bastion host?     │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       Yes    ├──── NAT Instance (or separate bastion + NAT GW)             │
│              │                                                               │
│       No     ▼                                                               │
│   ┌──────────────────────┐                                                  │
│   │ Budget constrained   │                                                  │
│   │ and low bandwidth?   │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       Yes    ├──── NAT Instance (t3.nano ~$3/month vs $32/month)           │
│              │                                                               │
│       No     ▼                                                               │
│   ┌──────────────────────┐                                                  │
│   │ Production workload? │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│       Yes    ├──── NAT Gateway (managed, HA, high bandwidth)               │
│              │                                                               │
│       No     ▼                                                               │
│   ┌──────────────────────┐                                                  │
│   │ Dev/Test environment │──── Either works; NAT GW preferred              │
│   └──────────────────────┘                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Egress-Only Internet Gateway

An Egress-Only Internet Gateway is used for IPv6 traffic only. It allows outbound traffic while preventing inbound connections.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EGRESS-ONLY INTERNET GATEWAY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   IPv4 World:                          IPv6 World:                          │
│   ┌────────────────────┐               ┌────────────────────┐               │
│   │                    │               │                    │               │
│   │  Private Subnet    │               │  Private Subnet    │               │
│   │  (No public IP)    │               │  (Has IPv6 addr)   │               │
│   │        │           │               │        │           │               │
│   │        ▼           │               │        ▼           │               │
│   │   NAT Gateway      │               │  Egress-Only IGW   │               │
│   │        │           │               │        │           │               │
│   │        ▼           │               │        ▼           │               │
│   │      IGW           │               │    (Same device)   │               │
│   │        │           │               │        │           │               │
│   │        ▼           │               │        ▼           │               │
│   │    Internet        │               │    Internet        │               │
│   │                    │               │                    │               │
│   └────────────────────┘               └────────────────────┘               │
│                                                                              │
│   Why Egress-Only for IPv6?                                                 │
│   ─────────────────────────                                                 │
│   • IPv6 addresses are globally unique (no private ranges)                  │
│   • NAT not needed for IPv6 (no address translation)                        │
│   • Egress-only provides security (blocks inbound)                          │
│                                                                              │
│   Route Table Entry:                                                        │
│   ::/0 → eigw-xxxxxxxx                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Comparison: IGW, NAT GW, Egress-Only IGW

| Feature | Internet Gateway | NAT Gateway | Egress-Only IGW |
|---------|------------------|-------------|-----------------|
| Protocol | IPv4 & IPv6 | IPv4 only | IPv6 only |
| Direction | Bidirectional | Outbound only | Outbound only |
| Subnet Type | Public | Public (for NAT GW itself) | Private (IPv6) |
| Public IP Required | Yes | EIP for NAT GW | No (IPv6 is public) |
| Cost | Free | ~$0.045/hr + data | Free |

## Creating NAT Gateway with AWS CLI

```bash
# Step 1: Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Step 2: Create NAT Gateway
aws ec2 create-nat-gateway \
    --subnet-id subnet-public1a \
    --allocation-id eipalloc-xxxxxxxx \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=NAT-1a}]'

# Step 3: Wait for NAT Gateway to become available
aws ec2 wait nat-gateway-available --nat-gateway-ids nat-xxxxxxxx

# Step 4: Update private subnet route table
aws ec2 create-route \
    --route-table-id rtb-private \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id nat-xxxxxxxx
```

## Cost Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NAT GATEWAY COST OPTIMIZATION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   NAT Gateway Costs:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Hourly charge: ~$0.045/hour × 730 hours = ~$32.85/month           │   │
│   │  Data processing: ~$0.045/GB                                        │   │
│   │                                                                      │   │
│   │  3 AZs × $32.85 = ~$98.55/month (just for hourly!)                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Optimization Strategies:                                                  │
│                                                                              │
│   1. Use VPC Endpoints for AWS Services                                     │
│      ┌──────────────────────────────────────────────────────────────┐      │
│      │  S3, DynamoDB → Gateway Endpoints (FREE)                     │      │
│      │  Other AWS services → Interface Endpoints                     │      │
│      │  Savings: Avoid NAT data processing charges                   │      │
│      └──────────────────────────────────────────────────────────────┘      │
│                                                                              │
│   2. Single NAT Gateway for Dev/Test                                        │
│      ┌──────────────────────────────────────────────────────────────┐      │
│      │  Use 1 NAT GW across AZs (accept cross-AZ data charges)      │      │
│      │  Only for non-production environments                         │      │
│      └──────────────────────────────────────────────────────────────┘      │
│                                                                              │
│   3. NAT Instance for Low-Traffic Environments                              │
│      ┌──────────────────────────────────────────────────────────────┐      │
│      │  t4g.nano: ~$3/month vs NAT GW: ~$33/month                   │      │
│      │  Good for: dev, sandbox, low-bandwidth needs                  │      │
│      └──────────────────────────────────────────────────────────────┘      │
│                                                                              │
│   4. Analyze Traffic Patterns                                               │
│      ┌──────────────────────────────────────────────────────────────┐      │
│      │  Use VPC Flow Logs to identify top talkers                   │      │
│      │  Move high-bandwidth to VPC endpoints                         │      │
│      └──────────────────────────────────────────────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Troubleshooting Internet Connectivity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              INTERNET CONNECTIVITY TROUBLESHOOTING                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Instance cannot reach internet?                                           │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────┐                                                  │
│   │ Public or Private    │                                                  │
│   │ subnet?              │                                                  │
│   └──────────┬───────────┘                                                  │
│              │                                                               │
│   ┌──────────┴──────────┐                                                   │
│   │                     │                                                   │
│   ▼                     ▼                                                   │
│ PUBLIC               PRIVATE                                                │
│   │                     │                                                   │
│   ▼                     ▼                                                   │
│ ┌────────────────┐   ┌────────────────┐                                    │
│ │Has public IP?  │   │NAT GW exists?  │                                    │
│ └───────┬────────┘   └───────┬────────┘                                    │
│   No    │ Yes          No    │ Yes                                         │
│   │     │              │     │                                              │
│   ▼     ▼              ▼     ▼                                              │
│ Assign  │           Create  │                                               │
│ EIP     │           NAT GW  │                                               │
│         │                   │                                                │
│         ▼                   ▼                                                │
│ ┌────────────────┐   ┌────────────────┐                                    │
│ │Route to IGW?   │   │Route to NAT?   │                                    │
│ │0.0.0.0/0→igw   │   │0.0.0.0/0→nat   │                                    │
│ └───────┬────────┘   └───────┬────────┘                                    │
│   No    │ Yes          No    │ Yes                                         │
│   │     │              │     │                                              │
│   ▼     ▼              ▼     ▼                                              │
│ Add    Check SG      Add    Check SG                                        │
│ route  & NACL        route  & NACL                                          │
│                                                                              │
│   Common Issues:                                                            │
│   • Security Group: Missing outbound rules                                  │
│   • NACL: Ephemeral ports blocked (1024-65535)                             │
│   • NAT GW: In wrong subnet or not in same AZ                              │
│   • Route Table: Not associated with subnet                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Internet Gateway** - Free, highly available, one per VPC
2. **NAT Gateway** - Managed, per-AZ, requires Elastic IP
3. **NAT Instance** - Self-managed, flexible, lower cost for small workloads
4. **Egress-Only IGW** - IPv6 only, outbound only, free
5. **HA Design** - One NAT Gateway per AZ for production
6. **Cost** - Use VPC endpoints to reduce NAT Gateway charges

---

**Next:** [04-route-tables.md](04-route-tables.md) - Understanding route tables and traffic flow
