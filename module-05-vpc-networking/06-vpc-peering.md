# 06 - VPC Peering

## What is VPC Peering?

VPC Peering is a networking connection between two VPCs that enables you to route traffic between them using private IPv4 or IPv6 addresses.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VPC PEERING CONCEPT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────┐     ┌─────────────────────────────┐       │
│   │         VPC A               │     │         VPC B               │       │
│   │      10.0.0.0/16            │     │      172.16.0.0/16          │       │
│   │                             │     │                             │       │
│   │   ┌───────────────────┐     │     │     ┌───────────────────┐   │       │
│   │   │      EC2          │     │     │     │      RDS          │   │       │
│   │   │   10.0.1.10       │     │     │     │   172.16.1.20     │   │       │
│   │   └─────────┬─────────┘     │     │     └─────────┬─────────┘   │       │
│   │             │               │     │               │             │       │
│   │             │               │     │               │             │       │
│   └─────────────┼───────────────┘     └───────────────┼─────────────┘       │
│                 │                                     │                      │
│                 │     ┌───────────────────────┐       │                      │
│                 │     │                       │       │                      │
│                 └────►│   VPC PEERING         │◄──────┘                      │
│                       │   CONNECTION          │                              │
│                       │   (pcx-xxxxxxxx)      │                              │
│                       │                       │                              │
│                       │ • Private IP routing  │                              │
│                       │ • No bandwidth limit  │                              │
│                       │ • No single point of  │                              │
│                       │   failure             │                              │
│                       └───────────────────────┘                              │
│                                                                              │
│   Traffic between 10.0.1.10 and 172.16.1.20 stays on AWS backbone           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Peering Characteristics

| Feature | Description |
|---------|-------------|
| **Scope** | Same region or cross-region |
| **Accounts** | Same account or cross-account |
| **CIDR** | Must NOT overlap |
| **Bandwidth** | No limit (AWS backbone) |
| **Cost** | Data transfer charges apply |
| **Latency** | Inter-region peering has higher latency |
| **Encryption** | Traffic encrypted for cross-region |

## VPC Peering Setup Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC PEERING SETUP STEPS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Step 1: Create Peering Request (Requester VPC)                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   VPC A (Requester)              VPC B (Accepter)                   │   │
│   │   ┌─────────────────┐            ┌─────────────────┐                │   │
│   │   │                 │  Request   │                 │                │   │
│   │   │   10.0.0.0/16   │ ────────►  │  172.16.0.0/16  │                │   │
│   │   │                 │  Pending   │                 │                │   │
│   │   └─────────────────┘            └─────────────────┘                │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Step 2: Accept Peering Request (Accepter VPC)                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   VPC A (Requester)              VPC B (Accepter)                   │   │
│   │   ┌─────────────────┐            ┌─────────────────┐                │   │
│   │   │                 │  Active    │                 │                │   │
│   │   │   10.0.0.0/16   │ ◄───────►  │  172.16.0.0/16  │                │   │
│   │   │                 │            │                 │                │   │
│   │   └─────────────────┘            └─────────────────┘                │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Step 3: Update Route Tables (BOTH VPCs!)                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   VPC A Route Table:             VPC B Route Table:                 │   │
│   │   ┌─────────────────────────┐    ┌─────────────────────────┐        │   │
│   │   │ 10.0.0.0/16 → local     │    │ 172.16.0.0/16 → local   │        │   │
│   │   │ 172.16.0.0/16 → pcx-xxx │    │ 10.0.0.0/16 → pcx-xxx   │        │   │
│   │   └─────────────────────────┘    └─────────────────────────┘        │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Step 4: Update Security Groups                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   VPC A SG: Allow inbound from 172.16.0.0/16                        │   │
│   │   VPC B SG: Allow inbound from 10.0.0.0/16                          │   │
│   │                                                                      │   │
│   │   (Or reference SG by ID for same-region peering)                   │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Transitive Peering - THE LIMITATION

VPC Peering is NOT transitive. This is a critical exam topic!

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRANSITIVE PEERING PROBLEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Scenario: VPC A peered with VPC B, VPC B peered with VPC C                │
│                                                                              │
│                        ┌─────────────────┐                                  │
│                        │      VPC B      │                                  │
│                        │  172.16.0.0/16  │                                  │
│                        └────────┬────────┘                                  │
│                                 │                                            │
│                    ┌────────────┴────────────┐                              │
│                    │                         │                              │
│                    │  pcx-1         pcx-2    │                              │
│                    │                         │                              │
│          ┌─────────▼─────────┐   ┌──────────▼────────┐                     │
│          │      VPC A        │   │      VPC C        │                     │
│          │   10.0.0.0/16     │   │   192.168.0.0/16  │                     │
│          └───────────────────┘   └───────────────────┘                     │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   CAN communicate:                                                  │   │
│   │   ✓ VPC A ◄──────► VPC B (via pcx-1)                               │   │
│   │   ✓ VPC B ◄──────► VPC C (via pcx-2)                               │   │
│   │                                                                      │   │
│   │   CANNOT communicate:                                               │   │
│   │   ✗ VPC A ◄──────► VPC C (NO transitive routing!)                  │   │
│   │                                                                      │   │
│   │   Even though B is connected to both A and C,                       │   │
│   │   traffic CANNOT flow from A → B → C                                │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   SOLUTION: Create direct peering between VPC A and VPC C (pcx-3)          │
│                                                                              │
│                        ┌─────────────────┐                                  │
│                        │      VPC B      │                                  │
│                        └────────┬────────┘                                  │
│                                 │                                            │
│                    ┌────────────┴────────────┐                              │
│                    │  pcx-1         pcx-2    │                              │
│          ┌─────────▼─────────┐   ┌──────────▼────────┐                     │
│          │      VPC A        │   │      VPC C        │                     │
│          └─────────┬─────────┘   └──────────┬────────┘                     │
│                    │                         │                              │
│                    └──────────┬──────────────┘                              │
│                               │                                              │
│                            pcx-3 (Direct peering)                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Peering Limitations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC PEERING LIMITATIONS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. NO Transitive Peering                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   A ←→ B ←→ C does NOT mean A ←→ C                                  │   │
│   │   Must create direct peering for each pair                          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   2. NO Overlapping CIDRs                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   VPC A: 10.0.0.0/16                                                │   │
│   │   VPC B: 10.0.0.0/16  ✗ Cannot peer - CIDR overlap!                │   │
│   │   VPC C: 10.1.0.0/16  ✓ Can peer - no overlap                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   3. NO Edge-to-Edge Routing                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   Cannot route through peered VPC to:                               │   │
│   │   • Internet Gateway                                                 │   │
│   │   • NAT Gateway                                                      │   │
│   │   • VPN Connection                                                   │   │
│   │   • Direct Connect                                                   │   │
│   │   • VPC Endpoint                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   4. One Peering Per VPC Pair                                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   Cannot have multiple peering connections between same two VPCs    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   5. Cross-Region Limitations                                               │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   • Cannot reference SG by ID (must use CIDR)                       │   │
│   │   • Higher latency                                                   │   │
│   │   • Data transfer costs higher                                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Edge-to-Edge Routing Explained

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EDGE-TO-EDGE ROUTING RESTRICTION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ✗ INVALID: Using peered VPC's Internet Gateway                           │
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐                               │
│   │      VPC A      │    │      VPC B      │                               │
│   │   (No IGW)      │    │   (Has IGW)     │                               │
│   │                 │    │                 │                               │
│   │   ┌─────────┐   │    │   ┌─────────┐   │     ┌────────────┐            │
│   │   │  EC2    │───┼────┼──►│   IGW   │───┼────►│  Internet  │            │
│   │   └─────────┘   │    │   └─────────┘   │     └────────────┘            │
│   │                 │    │                 │                               │
│   └─────────────────┘    └─────────────────┘                               │
│                                                                              │
│   ✗ This does NOT work! VPC A cannot use VPC B's IGW.                      │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   ✗ INVALID: Using peered VPC's NAT Gateway                                │
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐                               │
│   │      VPC A      │    │      VPC B      │                               │
│   │   (No NAT)      │    │   (Has NAT)     │                               │
│   │                 │    │                 │                               │
│   │   ┌─────────┐   │    │   ┌─────────┐   │                               │
│   │   │  EC2    │───┼────┼──►│  NAT GW │───┼────► Internet                 │
│   │   │(Private)│   │    │   └─────────┘   │                               │
│   │   └─────────┘   │    │                 │                               │
│   │                 │    │                 │                               │
│   └─────────────────┘    └─────────────────┘                               │
│                                                                              │
│   ✗ This does NOT work! VPC A cannot use VPC B's NAT Gateway.              │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   ✗ INVALID: Using peered VPC's VPN/Direct Connect                         │
│                                                                              │
│   On-Prem ◄──► VPC B (VPN) ◄──► VPC A (peered)                             │
│                                                                              │
│   ✗ VPC A cannot reach on-premises through VPC B's VPN.                    │
│     Solution: Use Transit Gateway for hub-spoke topology.                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Peering Use Cases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC PEERING USE CASES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Cross-Account Resource Sharing                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Account A (Dev)              Account B (Shared Services)          │   │
│   │   ┌─────────────────┐          ┌─────────────────┐                  │   │
│   │   │    Dev VPC      │ ◄──────► │   Shared VPC    │                  │   │
│   │   │                 │          │                 │                  │   │
│   │   │   App Servers   │          │ • AD/LDAP       │                  │   │
│   │   │                 │          │ • Monitoring    │                  │   │
│   │   │                 │          │ • CI/CD         │                  │   │
│   │   └─────────────────┘          └─────────────────┘                  │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   2. Environment Isolation with Connectivity                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐                        │   │
│   │   │   DEV    │   │  STAGING │   │   PROD   │                        │   │
│   │   │   VPC    │   │   VPC    │   │   VPC    │                        │   │
│   │   └────┬─────┘   └────┬─────┘   └────┬─────┘                        │   │
│   │        │              │              │                               │   │
│   │        └──────────────┼──────────────┘                               │   │
│   │                       │                                              │   │
│   │              ┌────────▼────────┐                                     │   │
│   │              │   Shared VPC    │                                     │   │
│   │              │   (Database)    │                                     │   │
│   │              └─────────────────┘                                     │   │
│   │                                                                      │   │
│   │   Note: Each environment peered to shared, not to each other        │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   3. Cross-Region Disaster Recovery                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   us-east-1                         us-west-2                       │   │
│   │   ┌─────────────────┐              ┌─────────────────┐              │   │
│   │   │   Primary VPC   │ ◄──────────► │    DR VPC       │              │   │
│   │   │                 │  Cross-region│                 │              │   │
│   │   │   Production    │   peering    │   Standby       │              │   │
│   │   └─────────────────┘              └─────────────────┘              │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Scaling Challenges

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC PEERING SCALING PROBLEM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Full Mesh with N VPCs requires: N × (N-1) / 2 peering connections        │
│                                                                              │
│   4 VPCs = 6 peering connections:                                           │
│                                                                              │
│              VPC-A ──────────── VPC-B                                       │
│              │ \               / │                                          │
│              │   \           /   │                                          │
│              │     \       /     │                                          │
│              │       \   /       │                                          │
│              │         X         │                                          │
│              │       /   \       │                                          │
│              │     /       \     │                                          │
│              │   /           \   │                                          │
│              │ /               \ │                                          │
│              VPC-C ──────────── VPC-D                                       │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   VPCs    │ Peering Connections │ Route Table Entries               │   │
│   ├───────────┼─────────────────────┼───────────────────────────────────┤   │
│   │     2     │          1          │         2                         │   │
│   │     3     │          3          │         6                         │   │
│   │     4     │          6          │        12                         │   │
│   │     5     │         10          │        20                         │   │
│   │    10     │         45          │        90                         │   │
│   │    20     │        190          │       380                         │   │
│   │    50     │       1225          │      2450 ← Unmanageable!         │   │
│   └───────────┴─────────────────────┴───────────────────────────────────┘   │
│                                                                              │
│   SOLUTION: Use Transit Gateway for more than 3-4 VPCs                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Peering with AWS CLI

```bash
# Step 1: Create VPC Peering Connection (from requester)
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-requester-id \
    --peer-vpc-id vpc-accepter-id \
    --peer-owner-id 123456789012 \
    --peer-region us-west-2

# Step 2: Accept VPC Peering Connection (from accepter)
aws ec2 accept-vpc-peering-connection \
    --vpc-peering-connection-id pcx-12345678

# Step 3: Add routes in requester VPC
aws ec2 create-route \
    --route-table-id rtb-requester \
    --destination-cidr-block 172.16.0.0/16 \
    --vpc-peering-connection-id pcx-12345678

# Step 4: Add routes in accepter VPC
aws ec2 create-route \
    --route-table-id rtb-accepter \
    --destination-cidr-block 10.0.0.0/16 \
    --vpc-peering-connection-id pcx-12345678

# Step 5: Update Security Groups
aws ec2 authorize-security-group-ingress \
    --group-id sg-requester \
    --protocol all \
    --cidr 172.16.0.0/16

aws ec2 authorize-security-group-ingress \
    --group-id sg-accepter \
    --protocol all \
    --cidr 10.0.0.0/16
```

## Troubleshooting VPC Peering

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC PEERING TROUBLESHOOTING                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   "Cannot communicate between peered VPCs"                                  │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────────────────┐                                      │
│   │ Check peering connection status  │                                      │
│   │ (Must be "Active")               │                                      │
│   └──────────────┬───────────────────┘                                      │
│                  │                                                           │
│        ┌─────────┴─────────┐                                                │
│   Pending?             Active?                                              │
│        │                   │                                                │
│        ▼                   ▼                                                │
│   Accept the          ┌───────────────────────────┐                         │
│   request             │ Check route tables (BOTH) │                         │
│                       │ for peering routes        │                         │
│                       └─────────────┬─────────────┘                         │
│                                     │                                        │
│                           ┌─────────┴─────────┐                             │
│                      Missing?              Present?                          │
│                           │                    │                             │
│                           ▼                    ▼                             │
│                      Add routes to        ┌────────────────────┐            │
│                      BOTH VPCs            │ Check Security     │            │
│                                           │ Groups (BOTH)      │            │
│                                           └─────────┬──────────┘            │
│                                                     │                        │
│                                           ┌─────────┴─────────┐             │
│                                       Missing?            Present?           │
│                                           │                   │              │
│                                           ▼                   ▼              │
│                                      Add inbound         Check NACLs        │
│                                      rules for           (both subnets)     │
│                                      peer CIDR                              │
│                                                                              │
│   Pro Tips:                                                                 │
│   • Use VPC Reachability Analyzer to diagnose connectivity issues          │
│   • Check DNS resolution if using hostnames                                 │
│   • Verify no overlapping CIDRs                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **No Transitive Peering** - Must create direct connection for each pair
2. **No Overlapping CIDRs** - Plan IP addressing carefully
3. **No Edge-to-Edge Routing** - Cannot share IGW, NAT, VPN, DX
4. **Update BOTH VPCs** - Routes and Security Groups needed on both sides
5. **Cross-Region Supported** - But with higher latency and cost
6. **Use Transit Gateway** - For more than 3-4 VPCs (hub-spoke model)

---

**Next:** [07-vpc-endpoints.md](07-vpc-endpoints.md) - Private access to AWS services
