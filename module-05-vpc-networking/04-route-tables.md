# 04 - Route Tables

## Understanding Route Tables

A route table contains a set of rules (routes) that determine where network traffic from your subnet or gateway is directed.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROUTE TABLE CONCEPT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Route Table = Traffic GPS                                                 │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Packet arrives: "I need to go to 8.8.8.8"                         │   │
│   │                                                                      │   │
│   │   Route Table:                                                       │   │
│   │   ┌─────────────────┬─────────────────┬────────────────────────┐    │   │
│   │   │ Destination     │ Target          │ Match?                 │    │   │
│   │   ├─────────────────┼─────────────────┼────────────────────────┤    │   │
│   │   │ 10.0.0.0/16     │ local           │ No (8.8.8.8 not in)    │    │   │
│   │   │ 172.16.0.0/16   │ pcx-xxxxx       │ No (8.8.8.8 not in)    │    │   │
│   │   │ 0.0.0.0/0       │ igw-xxxxx       │ YES! (matches all)     │    │   │
│   │   └─────────────────┴─────────────────┴────────────────────────┘    │   │
│   │                                                                      │   │
│   │   Decision: Send to Internet Gateway (igw-xxxxx)                    │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Route Table Components

### Route Entry Structure

| Component | Description | Example |
|-----------|-------------|---------|
| **Destination** | CIDR block for traffic matching | 10.0.0.0/16, 0.0.0.0/0 |
| **Target** | Where to send matched traffic | local, igw-xxx, nat-xxx |
| **Status** | Active or Blackhole | Active |
| **Propagated** | Added by VPN/Direct Connect | Yes/No |

### Common Route Targets

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROUTE TARGETS REFERENCE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Target Type           │ Prefix    │ Use Case                              │
│   ──────────────────────┼───────────┼─────────────────────────────────────  │
│   Local                 │ local     │ VPC internal traffic                  │
│   Internet Gateway      │ igw-      │ Internet access (public)              │
│   NAT Gateway           │ nat-      │ Internet access (private)             │
│   NAT Instance          │ eni-/i-   │ Internet access (legacy)              │
│   VPC Peering           │ pcx-      │ Cross-VPC traffic                     │
│   VPN Gateway           │ vgw-      │ On-premises via VPN                   │
│   Transit Gateway       │ tgw-      │ Hub connectivity                      │
│   VPC Endpoint (GW)     │ vpce-     │ S3/DynamoDB access                    │
│   Network Interface     │ eni-      │ Appliance/firewall                    │
│   Egress-Only IGW       │ eigw-     │ IPv6 outbound                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Main Route Table vs Custom Route Tables

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAIN vs CUSTOM ROUTE TABLES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   MAIN ROUTE TABLE                         CUSTOM ROUTE TABLE               │
│   ─────────────────                        ───────────────────              │
│                                                                              │
│   ┌─────────────────────────┐             ┌─────────────────────────┐       │
│   │ • Created automatically │             │ • You create manually   │       │
│   │   with VPC              │             │                         │       │
│   │                         │             │ • Explicitly associate  │       │
│   │ • Default for subnets   │             │   with subnets          │       │
│   │   not explicitly        │             │                         │       │
│   │   associated            │             │ • More control and      │       │
│   │                         │             │   security              │       │
│   │ • Cannot be deleted     │             │                         │       │
│   │   (but can replace)     │             │ • Can be deleted        │       │
│   └─────────────────────────┘             └─────────────────────────┘       │
│                                                                              │
│   ⚠️  Best Practice: Keep main route table simple (local only)             │
│                      Use custom route tables for specific routing           │
│                                                                              │
│   Example VPC Setup:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Main Route Table (rtb-main)          Custom RT: Public (rtb-pub)  │   │
│   │   ┌────────────────────────────┐       ┌────────────────────────┐   │   │
│   │   │ 10.0.0.0/16 → local        │       │ 10.0.0.0/16 → local    │   │   │
│   │   │ (No internet route)        │       │ 0.0.0.0/0 → igw-xxx    │   │   │
│   │   └────────────────────────────┘       └────────────────────────┘   │   │
│   │                                                                      │   │
│   │   Custom RT: Private-A (rtb-prv-a)     Custom RT: Private-B         │   │
│   │   ┌────────────────────────────┐       ┌────────────────────────┐   │   │
│   │   │ 10.0.0.0/16 → local        │       │ 10.0.0.0/16 → local    │   │   │
│   │   │ 0.0.0.0/0 → nat-a          │       │ 0.0.0.0/0 → nat-b      │   │   │
│   │   └────────────────────────────┘       └────────────────────────┘   │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Longest Prefix Match

When multiple routes match, AWS uses the most specific (longest prefix) match.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LONGEST PREFIX MATCH EXPLAINED                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Route Table:                                                              │
│   ┌──────────────────────┬──────────────────────┐                          │
│   │ Destination          │ Target               │                          │
│   ├──────────────────────┼──────────────────────┤                          │
│   │ 10.0.0.0/16          │ local                │  /16 = 16 bits           │
│   │ 10.0.1.0/24          │ vpce-s3              │  /24 = 24 bits           │
│   │ 10.0.1.128/25        │ tgw-xxxxx            │  /25 = 25 bits           │
│   │ 0.0.0.0/0            │ igw-xxxxx            │  /0 = 0 bits             │
│   └──────────────────────┴──────────────────────┘                          │
│                                                                              │
│   Scenario: Packet destined for 10.0.1.200                                  │
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────────┐    │
│   │                                                                    │    │
│   │   Check 1: 10.0.0.0/16                                            │    │
│   │            10.0.1.200 in 10.0.0.0 - 10.0.255.255? ✓ MATCH        │    │
│   │            Prefix length: 16 bits                                  │    │
│   │                                                                    │    │
│   │   Check 2: 10.0.1.0/24                                            │    │
│   │            10.0.1.200 in 10.0.1.0 - 10.0.1.255? ✓ MATCH          │    │
│   │            Prefix length: 24 bits (MORE SPECIFIC!)                │    │
│   │                                                                    │    │
│   │   Check 3: 10.0.1.128/25                                          │    │
│   │            10.0.1.200 in 10.0.1.128 - 10.0.1.255? ✓ MATCH        │    │
│   │            Prefix length: 25 bits (MOST SPECIFIC!)                │    │
│   │                                                                    │    │
│   │   Check 4: 0.0.0.0/0                                              │    │
│   │            Always matches, but /0 is least specific              │    │
│   │                                                                    │    │
│   │   ═══════════════════════════════════════════════════════════════ │    │
│   │   WINNER: 10.0.1.128/25 → tgw-xxxxx                              │    │
│   │   (Longest prefix = 25 bits = Most specific match)               │    │
│   │                                                                    │    │
│   └───────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Prefix Match Examples

| Destination IP | Matching Routes | Winner | Reason |
|----------------|-----------------|--------|--------|
| 10.0.1.200 | /16, /24, /25, /0 | /25 | Most specific |
| 10.0.1.50 | /16, /24, /0 | /24 | /25 doesn't match |
| 10.0.2.100 | /16, /0 | /16 | /24, /25 don't match |
| 8.8.8.8 | /0 | /0 | Only match |

## Route Propagation

Route propagation automatically adds routes learned from VPN or Direct Connect.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROUTE PROPAGATION                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   On-Premises Network                     AWS VPC                           │
│   ┌─────────────────────┐                ┌─────────────────────┐            │
│   │                     │                │                     │            │
│   │  192.168.0.0/16     │  Site-to-Site  │  10.0.0.0/16        │            │
│   │  ┌───────────────┐  │     VPN        │  ┌───────────────┐  │            │
│   │  │ Customer      │  │◄═══════════════►  │ Virtual       │  │            │
│   │  │ Gateway       │  │                │  │ Private GW    │  │            │
│   │  └───────────────┘  │                │  └───────┬───────┘  │            │
│   │                     │                │          │          │            │
│   └─────────────────────┘                │          │ BGP      │            │
│                                          │          ▼          │            │
│                                          │  Route Table:       │            │
│                                          │  ┌────────────────┐ │            │
│                                          │  │Static Routes:  │ │            │
│                                          │  │10.0.0.0/16→local│            │
│                                          │  │                │ │            │
│                                          │  │Propagated:     │ │            │
│                                          │  │192.168.0.0/16  │ │            │
│                                          │  │ → vgw-xxx (P)  │ │            │
│                                          │  │                │ │            │
│                                          │  │(P) = Propagated│ │            │
│                                          │  └────────────────┘ │            │
│                                          │                     │            │
│                                          └─────────────────────┘            │
│                                                                              │
│   To Enable Propagation:                                                    │
│   1. Edit Route Table                                                       │
│   2. Route Propagation tab                                                  │
│   3. Enable for Virtual Private Gateway                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Route Table Architecture Patterns

### Pattern 1: Simple Public/Private

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIMPLE TWO-TIER ROUTING                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                            Internet                                          │
│                               │                                              │
│                               │                                              │
│                        ┌──────▼──────┐                                      │
│                        │    IGW      │                                      │
│                        └──────┬──────┘                                      │
│                               │                                              │
│   ┌───────────────────────────┼───────────────────────────────────────┐     │
│   │              VPC          │                                        │     │
│   │                           │                                        │     │
│   │   ┌───────────────────────┴───────────────────────┐               │     │
│   │   │                                               │               │     │
│   │   ▼                                               ▼               │     │
│   │ ┌─────────────────────────┐   ┌─────────────────────────────┐    │     │
│   │ │     PUBLIC SUBNET       │   │     PUBLIC SUBNET           │    │     │
│   │ │        AZ-1a            │   │        AZ-1b                │    │     │
│   │ │                         │   │                             │    │     │
│   │ │ Route Table: rtb-public │   │ Route Table: rtb-public     │    │     │
│   │ │ ┌─────────────────────┐ │   │ (Same route table)          │    │     │
│   │ │ │10.0.0.0/16 → local  │ │   │                             │    │     │
│   │ │ │0.0.0.0/0 → igw-xxx  │ │   │ ┌─────┐  NAT GW             │    │     │
│   │ │ └─────────────────────┘ │   │ └──┬──┘                     │    │     │
│   │ └─────────────────────────┘   └────┼────────────────────────┘    │     │
│   │                                    │                              │     │
│   │                                    │                              │     │
│   │ ┌─────────────────────────┐   ┌────▼────────────────────────┐    │     │
│   │ │     PRIVATE SUBNET      │   │     PRIVATE SUBNET          │    │     │
│   │ │        AZ-1a            │   │        AZ-1b                │    │     │
│   │ │                         │   │                             │    │     │
│   │ │ Route Table: rtb-priv   │   │ Route Table: rtb-priv       │    │     │
│   │ │ ┌─────────────────────┐ │   │ (Same route table)          │    │     │
│   │ │ │10.0.0.0/16 → local  │ │   │                             │    │     │
│   │ │ │0.0.0.0/0 → nat-xxx  │ │   │                             │    │     │
│   │ │ └─────────────────────┘ │   │                             │    │     │
│   │ └─────────────────────────┘   └─────────────────────────────┘    │     │
│   │                                                                   │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pattern 2: HA NAT with Per-AZ Route Tables

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HA ROUTING WITH PER-AZ NAT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         Internet                                             │
│                            │                                                 │
│                     ┌──────▼──────┐                                         │
│                     │    IGW      │                                         │
│                     └──────┬──────┘                                         │
│                            │                                                 │
│   ┌────────────────────────┼────────────────────────────────────────┐       │
│   │           VPC          │                                         │       │
│   │                        │                                         │       │
│   │   ┌────────────────────┴────────────────────┐                   │       │
│   │   │                                         │                   │       │
│   │   ▼                                         ▼                   │       │
│   │ ┌───────────────────────┐   ┌───────────────────────┐          │       │
│   │ │  PUBLIC SUBNET AZ-1a  │   │  PUBLIC SUBNET AZ-1b  │          │       │
│   │ │                       │   │                       │          │       │
│   │ │  ┌─────┐              │   │  ┌─────┐              │          │       │
│   │ │  │NAT-A│              │   │  │NAT-B│              │          │       │
│   │ │  └──┬──┘              │   │  └──┬──┘              │          │       │
│   │ │     │                 │   │     │                 │          │       │
│   │ │  rtb-public           │   │  rtb-public           │          │       │
│   │ │  10.0.0.0/16→local    │   │  10.0.0.0/16→local    │          │       │
│   │ │  0.0.0.0/0→igw        │   │  0.0.0.0/0→igw        │          │       │
│   │ └─────────┼─────────────┘   └─────────┼─────────────┘          │       │
│   │           │                           │                         │       │
│   │           │                           │                         │       │
│   │ ┌─────────▼─────────────┐   ┌─────────▼─────────────┐          │       │
│   │ │ PRIVATE SUBNET AZ-1a  │   │ PRIVATE SUBNET AZ-1b  │          │       │
│   │ │                       │   │                       │          │       │
│   │ │ rtb-private-a         │   │ rtb-private-b         │          │       │
│   │ │ ┌───────────────────┐ │   │ ┌───────────────────┐ │          │       │
│   │ │ │10.0.0.0/16→local  │ │   │ │10.0.0.0/16→local  │ │          │       │
│   │ │ │0.0.0.0/0→NAT-A    │ │   │ │0.0.0.0/0→NAT-B    │ │          │       │
│   │ │ └───────────────────┘ │   │ └───────────────────┘ │          │       │
│   │ │                       │   │                       │          │       │
│   │ │ Traffic stays in AZ   │   │ Traffic stays in AZ   │          │       │
│   │ └───────────────────────┘   └───────────────────────┘          │       │
│   │                                                                  │       │
│   │  Benefits: No cross-AZ data transfer, AZ isolation              │       │
│   │                                                                  │       │
│   └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pattern 3: Hybrid with VPN

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HYBRID CONNECTIVITY ROUTING                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   On-Premises                      AWS VPC                                  │
│   192.168.0.0/16                   10.0.0.0/16                              │
│                                                                              │
│   ┌──────────────────┐            ┌──────────────────────────────────────┐  │
│   │                  │   VPN      │                                      │  │
│   │  ┌────────────┐  │◄══════════►│  ┌───────────┐                       │  │
│   │  │ Customer   │  │            │  │   VGW     │                       │  │
│   │  │ Gateway    │  │            │  └─────┬─────┘                       │  │
│   │  └────────────┘  │            │        │                             │  │
│   │                  │            │        │                             │  │
│   └──────────────────┘            │  ┌─────▼─────────────────────────┐   │  │
│                                   │  │      Route Table               │   │  │
│                                   │  │  ┌─────────────────────────┐  │   │  │
│                                   │  │  │ Destination    Target   │  │   │  │
│                                   │  │  ├─────────────────────────┤  │   │  │
│                                   │  │  │ 10.0.0.0/16   local     │  │   │  │
│                                   │  │  │ 0.0.0.0/0     nat-xxx   │  │   │  │
│                                   │  │  │ 192.168.0.0/16 vgw-xxx  │◄─┼── Static or │
│                                   │  │  └─────────────────────────┘  │   Propagated │
│                                   │  └───────────────────────────────┘   │  │
│                                   │                                      │  │
│                                   └──────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Managing Route Tables with AWS CLI

```bash
# Create route table
aws ec2 create-route-table \
    --vpc-id vpc-12345678 \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Private-RT}]'

# Add route to NAT Gateway
aws ec2 create-route \
    --route-table-id rtb-12345678 \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id nat-12345678

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id rtb-87654321 \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-12345678

# Add route to VPC Peering
aws ec2 create-route \
    --route-table-id rtb-12345678 \
    --destination-cidr-block 172.16.0.0/16 \
    --vpc-peering-connection-id pcx-12345678

# Associate route table with subnet
aws ec2 associate-route-table \
    --route-table-id rtb-12345678 \
    --subnet-id subnet-12345678

# Replace main route table
aws ec2 replace-route-table-association \
    --association-id rtbassoc-12345678 \
    --route-table-id rtb-87654321

# Enable route propagation
aws ec2 enable-vgw-route-propagation \
    --route-table-id rtb-12345678 \
    --gateway-id vgw-12345678
```

## Route Table Troubleshooting

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ROUTING TROUBLESHOOTING FLOWCHART                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Traffic not reaching destination?                                         │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────────────────┐                                      │
│   │ 1. Identify source subnet        │                                      │
│   └──────────────┬───────────────────┘                                      │
│                  │                                                           │
│                  ▼                                                           │
│   ┌──────────────────────────────────┐                                      │
│   │ 2. Find associated route table   │                                      │
│   │    (Subnet → Route Tables tab)   │                                      │
│   └──────────────┬───────────────────┘                                      │
│                  │                                                           │
│                  ▼                                                           │
│   ┌──────────────────────────────────┐                                      │
│   │ 3. Check for matching route      │                                      │
│   └──────────────┬───────────────────┘                                      │
│                  │                                                           │
│        ┌─────────┴─────────┐                                                │
│        │                   │                                                │
│   No Route              Route Exists                                        │
│        │                   │                                                │
│        ▼                   ▼                                                │
│   ┌───────────────┐   ┌───────────────────┐                                │
│   │ Add route to  │   │ Check route status│                                │
│   │ destination   │   │ (Active/Blackhole)│                                │
│   └───────────────┘   └─────────┬─────────┘                                │
│                                 │                                           │
│                    ┌────────────┴────────────┐                             │
│                    │                         │                              │
│                 Active                   Blackhole                          │
│                    │                         │                              │
│                    ▼                         ▼                              │
│   ┌───────────────────────────┐   ┌─────────────────────────┐              │
│   │ Check Security Group      │   │ Target is deleted/down  │              │
│   │ and Network ACL rules     │   │ (NAT GW, Instance, etc) │              │
│   └───────────────────────────┘   └─────────────────────────┘              │
│                                                                              │
│   Common Issues:                                                            │
│   • Subnet associated with wrong route table                                │
│   • Route pointing to deleted NAT Gateway (blackhole)                       │
│   • More specific route overriding expected route                           │
│   • Missing route propagation for VPN routes                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Route Table Limits

| Resource | Default Limit | Can Increase? |
|----------|---------------|---------------|
| Route tables per VPC | 200 | Yes |
| Routes per route table | 50 | Yes (up to 1000) |
| BGP advertised routes per route table | 100 | Yes |

## Key Takeaways

1. **Route tables determine traffic flow** - Every packet is evaluated against routes
2. **Longest prefix match wins** - Most specific route is selected
3. **Main vs Custom** - Keep main simple, use custom for control
4. **Per-AZ route tables** - Enable HA NAT Gateway architecture
5. **Route propagation** - Automatic route addition for VPN/DX
6. **Blackhole routes** - Indicate deleted/unavailable targets

---

**Next:** [05-security-groups-nacls.md](05-security-groups-nacls.md) - Network security with Security Groups and NACLs
