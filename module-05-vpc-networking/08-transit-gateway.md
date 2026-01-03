# 08 - AWS Transit Gateway

## What is Transit Gateway?

AWS Transit Gateway is a network transit hub that you can use to interconnect your Virtual Private Clouds (VPCs) and on-premises networks. It acts as a central hub for routing traffic between all connected networks.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TRANSIT GATEWAY CONCEPT                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   BEFORE Transit Gateway (VPC Peering - Full Mesh):                             │
│                                                                                  │
│       VPC-A ──────────── VPC-B                                                  │
│         │ \            / │                                                      │
│         │  \          /  │        n VPCs = n(n-1)/2 connections                 │
│         │   \        /   │        4 VPCs = 6 connections                        │
│         │    \      /    │       10 VPCs = 45 connections                       │
│         │     \    /     │      100 VPCs = 4,950 connections!                   │
│       VPC-C ──────────── VPC-D                                                  │
│                                                                                  │
│   AFTER Transit Gateway (Hub-and-Spoke):                                        │
│                                                                                  │
│       VPC-A          VPC-B                                                      │
│           \          /                                                          │
│            \        /           n VPCs = n connections                          │
│         ┌───────────────┐       4 VPCs = 4 connections                          │
│         │    Transit    │      10 VPCs = 10 connections                         │
│         │    Gateway    │     100 VPCs = 100 connections                        │
│         └───────────────┘                                                       │
│            /        \                                                           │
│           /          \                                                          │
│       VPC-C          VPC-D                                                      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Why Use Transit Gateway?

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Simplified Architecture** | Single connection point for multiple VPCs |
| **Transitive Routing** | Any-to-any connectivity between attachments |
| **Centralized Management** | One place to manage routing |
| **Scalability** | Up to 5,000 VPC attachments |
| **Cross-Region Peering** | Connect Transit Gateways across regions |
| **Hybrid Connectivity** | Connect VPN and Direct Connect |

### Use Cases

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TRANSIT GATEWAY USE CASES                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. MULTI-VPC CONNECTIVITY                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Production    Staging       Dev        Shared Services                │   │
│   │   VPC           VPC           VPC        VPC                            │   │
│   │      \           |            /            /                            │   │
│   │       \          |           /            /                             │   │
│   │        ┌─────────────────────────────────┐                              │   │
│   │        │       Transit Gateway           │                              │   │
│   │        └─────────────────────────────────┘                              │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   2. HYBRID CLOUD ARCHITECTURE                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   On-Premises         AWS Cloud                                         │   │
│   │   Data Center                                                           │   │
│   │   ┌─────────┐    VPN    ┌──────────────┐    VPC-1  VPC-2              │   │
│   │   │ Servers │◄─────────►│   Transit    │◄──►  │      │               │   │
│   │   └─────────┘  Direct   │   Gateway    │                              │   │
│   │                Connect  └──────────────┘    VPC-3  VPC-4              │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   3. GLOBAL NETWORK (Cross-Region)                                              │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   US-EAST-1               EU-WEST-1               AP-NORTHEAST-1        │   │
│   │   ┌─────────┐             ┌─────────┐             ┌─────────┐           │   │
│   │   │   TGW   │◄───────────►│   TGW   │◄───────────►│   TGW   │           │   │
│   │   └────┬────┘  Peering    └────┬────┘  Peering    └────┬────┘           │   │
│   │        │                       │                       │                 │   │
│   │    VPCs-US                 VPCs-EU                 VPCs-APAC            │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Transit Gateway Components

### Core Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TRANSIT GATEWAY COMPONENTS                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                          TRANSIT GATEWAY                                 │   │
│   │                                                                          │   │
│   │   ┌───────────────────────────────────────────────────────────────────┐ │   │
│   │   │                    ROUTE TABLES                                    │ │   │
│   │   │                                                                    │ │   │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │ │   │
│   │   │   │  Default RT  │  │  Custom RT   │  │ Isolated RT  │           │ │   │
│   │   │   │              │  │  (Shared)    │  │  (Security)  │           │ │   │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘           │ │   │
│   │   │                                                                    │ │   │
│   │   └───────────────────────────────────────────────────────────────────┘ │   │
│   │                                                                          │   │
│   │   ┌───────────────────────────────────────────────────────────────────┐ │   │
│   │   │                      ATTACHMENTS                                   │ │   │
│   │   │                                                                    │ │   │
│   │   │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │ │   │
│   │   │   │    VPC     │  │    VPN     │  │   Direct   │  │    TGW     │ │ │   │
│   │   │   │ Attachment │  │ Attachment │  │  Connect   │  │  Peering   │ │ │   │
│   │   │   └────────────┘  └────────────┘  └────────────┘  └────────────┘ │ │   │
│   │   │                                                                    │ │   │
│   │   └───────────────────────────────────────────────────────────────────┘ │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Key Concepts:                                                                 │
│   • Attachment: Connection between TGW and VPC/VPN/DX/TGW                      │
│   • Route Table: Determines how traffic is routed between attachments          │
│   • Association: Links attachment to a route table                             │
│   • Propagation: Automatically adds routes from attachment to route table      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Attachment Types

| Type | Description | Use Case |
|------|-------------|----------|
| **VPC Attachment** | Connects a VPC to TGW | Inter-VPC communication |
| **VPN Attachment** | Site-to-Site VPN connection | Hybrid connectivity |
| **Direct Connect Gateway** | DX connection | High-bandwidth hybrid |
| **Transit Gateway Peering** | Cross-region TGW connection | Global networking |
| **Connect Attachment** | SD-WAN/third-party appliances | Advanced routing |

## Hub-and-Spoke Architecture

### Basic Hub-and-Spoke Design

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        HUB-AND-SPOKE ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                              ┌───────────────────────────────────┐              │
│                              │        Shared Services VPC        │              │
│                              │         (10.0.0.0/16)             │              │
│                              │                                    │              │
│                              │  ┌──────┐  ┌──────┐  ┌──────┐    │              │
│                              │  │ DNS  │  │ AD   │  │ NTP  │    │              │
│                              │  └──────┘  └──────┘  └──────┘    │              │
│                              └──────────────┬────────────────────┘              │
│                                             │                                    │
│                                             │ VPC Attachment                     │
│                                             │                                    │
│    ┌───────────────────────────────────────┬┴┬───────────────────────────────┐  │
│    │                                       │ │                                │  │
│    │                              ┌────────▼─▼────────┐                      │  │
│    │                              │                    │                      │  │
│    │                              │   TRANSIT GATEWAY  │                      │  │
│    │                              │                    │                      │  │
│    │                              └────────┬──────────┘                      │  │
│    │                                       │                                  │  │
│    │              ┌────────────────────────┼────────────────────────┐        │  │
│    │              │                        │                        │        │  │
│    │              │                        │                        │        │  │
│    │     ┌───────▼───────┐        ┌───────▼───────┐        ┌───────▼───────┐ │  │
│    │     │  Production   │        │    Staging    │        │  Development  │ │  │
│    │     │     VPC       │        │     VPC       │        │     VPC       │ │  │
│    │     │ 10.1.0.0/16   │        │ 10.2.0.0/16   │        │ 10.3.0.0/16   │ │  │
│    │     │               │        │               │        │               │ │  │
│    │     │ ┌───┐ ┌───┐   │        │ ┌───┐ ┌───┐   │        │ ┌───┐ ┌───┐   │ │  │
│    │     │ │EC2│ │RDS│   │        │ │EC2│ │RDS│   │        │ │EC2│ │RDS│   │ │  │
│    │     │ └───┘ └───┘   │        │ └───┘ └───┘   │        │ └───┘ └───┘   │ │  │
│    │     │               │        │               │        │               │ │  │
│    │     └───────────────┘        └───────────────┘        └───────────────┘ │  │
│    │                                                                          │  │
│    └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   All VPCs can communicate with each other and shared services                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Isolated Spoke Design (Security Segmentation)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ISOLATED SPOKE ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Use Case: Prod and Dev should NOT communicate directly                        │
│             Both need access to Shared Services                                 │
│                                                                                  │
│                              ┌─────────────────────┐                            │
│                              │   Shared Services   │                            │
│                              │    (10.0.0.0/16)    │                            │
│                              └──────────┬──────────┘                            │
│                                         │                                        │
│                                         │ Associated: Shared-RT                  │
│                                         │                                        │
│                              ┌──────────▼──────────┐                            │
│                              │                      │                            │
│                              │   TRANSIT GATEWAY    │                            │
│                              │                      │                            │
│                              └──────────┬──────────┘                            │
│                                         │                                        │
│                    ┌────────────────────┼────────────────────┐                  │
│                    │                    │                    │                  │
│           Associated:            Associated:           Associated:              │
│           Prod-RT               Shared-RT              Dev-RT                   │
│                    │                    │                    │                  │
│           ┌───────▼───────┐            │            ┌───────▼───────┐          │
│           │   Production  │                         │  Development  │          │
│           │  (10.1.0.0/16)│                         │ (10.2.0.0/16) │          │
│           └───────────────┘                         └───────────────┘          │
│                                                                                  │
│   ROUTE TABLE CONFIGURATION:                                                    │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Prod-RT:                    Dev-RT:                                   │   │
│   │   ┌───────────────────────┐   ┌───────────────────────┐                 │   │
│   │   │ 10.0.0.0/16 → Shared  │   │ 10.0.0.0/16 → Shared  │                 │   │
│   │   │ (No route to Dev!)    │   │ (No route to Prod!)   │                 │   │
│   │   └───────────────────────┘   └───────────────────────┘                 │   │
│   │                                                                          │   │
│   │   Shared-RT:                                                            │   │
│   │   ┌───────────────────────┐                                             │   │
│   │   │ 10.1.0.0/16 → Prod    │   (Can reach both Prod and Dev)            │   │
│   │   │ 10.2.0.0/16 → Dev     │                                             │   │
│   │   └───────────────────────┘                                             │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Result:                                                                       │
│   ✓ Prod ↔ Shared Services: OK                                                 │
│   ✓ Dev ↔ Shared Services: OK                                                  │
│   ✗ Prod ↔ Dev: BLOCKED (no route!)                                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Transit Gateway Route Tables

### Route Table Concepts

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TGW ROUTE TABLE CONCEPTS                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ASSOCIATIONS (1:1 relationship)                                               │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Each attachment MUST be associated with exactly ONE route table       │   │
│   │                                                                          │   │
│   │   Attachment (VPC-A) ────────────────► Route Table (RT-1)               │   │
│   │                        Associated                                        │   │
│   │                                                                          │   │
│   │   The associated route table determines:                                │   │
│   │   "Where can traffic FROM this attachment go?"                          │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   PROPAGATIONS (1:Many relationship)                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   An attachment can propagate to MULTIPLE route tables                  │   │
│   │                                                                          │   │
│   │                         ┌──────────────────┐                            │   │
│   │                         │                  │                            │   │
│   │   Attachment ──────────►│   Route Table-1  │  (Route: 10.1.0.0/16)     │   │
│   │   (VPC-A)              │                  │                            │   │
│   │   10.1.0.0/16  ────────►│   Route Table-2  │  (Route: 10.1.0.0/16)     │   │
│   │                         │                  │                            │   │
│   │                ────────►│   Route Table-3  │  (Route: 10.1.0.0/16)     │   │
│   │                         │                  │                            │   │
│   │                         └──────────────────┘                            │   │
│   │                                                                          │   │
│   │   Propagation adds routes automatically:                                │   │
│   │   "Other route tables learn about this attachment's CIDR"               │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   STATIC ROUTES                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   You can manually add routes (overrides propagated routes)             │   │
│   │                                                                          │   │
│   │   Route Table:                                                          │   │
│   │   ┌───────────────────────────────────────────────────────────────┐     │   │
│   │   │ Destination      │ Attachment      │ Type                      │     │   │
│   │   ├───────────────────────────────────────────────────────────────┤     │   │
│   │   │ 10.0.0.0/8       │ tgw-attach-xxx  │ Static (manual)          │     │   │
│   │   │ 10.1.0.0/16      │ tgw-attach-aaa  │ Propagated (automatic)   │     │   │
│   │   │ 10.2.0.0/16      │ tgw-attach-bbb  │ Propagated (automatic)   │     │   │
│   │   │ 0.0.0.0/0        │ tgw-attach-vpn  │ Static (default route)   │     │   │
│   │   └───────────────────────────────────────────────────────────────┘     │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Route Table Flow Example

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ROUTE TABLE TRAFFIC FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Traffic from VPC-A (10.1.0.0/16) to VPC-B (10.2.0.0/16):                      │
│                                                                                  │
│   Step 1: EC2 in VPC-A sends packet to 10.2.1.50                               │
│                                                                                  │
│   ┌───────────────────┐                                                         │
│   │      VPC-A        │                                                         │
│   │   ┌─────────┐     │                                                         │
│   │   │   EC2   │     │  VPC Route Table:                                       │
│   │   │10.1.1.10│     │  ┌─────────────────────────────────┐                   │
│   │   └────┬────┘     │  │ 10.2.0.0/16 → tgw-xxxxxxxx     │                   │
│   │        │          │  └─────────────────────────────────┘                   │
│   │        │ Packet   │                                                         │
│   │        │ to       │                                                         │
│   │        │ 10.2.1.50│                                                         │
│   │        │          │                                                         │
│   │        ▼          │                                                         │
│   │ [TGW Attachment]  │                                                         │
│   └────────┼──────────┘                                                         │
│            │                                                                     │
│   Step 2:  │ Packet arrives at Transit Gateway                                  │
│            │                                                                     │
│            ▼                                                                     │
│   ┌────────────────────────────────────────────────────────────────────────┐   │
│   │                        TRANSIT GATEWAY                                  │   │
│   │                                                                         │   │
│   │   VPC-A Attachment Associated to: TGW-RT-1                             │   │
│   │                                                                         │   │
│   │   TGW-RT-1 Route Table:                                                │   │
│   │   ┌────────────────────────────────────────────────────────────────┐   │   │
│   │   │ Destination      │ Target           │ Type                     │   │   │
│   │   ├────────────────────────────────────────────────────────────────┤   │   │
│   │   │ 10.1.0.0/16      │ VPC-A Attachment │ Propagated              │   │   │
│   │   │ 10.2.0.0/16      │ VPC-B Attachment │ Propagated  ◄── MATCH   │   │   │
│   │   │ 10.3.0.0/16      │ VPC-C Attachment │ Propagated              │   │   │
│   │   └────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                         │   │
│   └────────────────────────────────────────────────────────────────────────┘   │
│            │                                                                     │
│   Step 3:  │ TGW forwards to VPC-B Attachment                                   │
│            │                                                                     │
│            ▼                                                                     │
│   ┌───────────────────┐                                                         │
│   │      VPC-B        │                                                         │
│   │ [TGW Attachment]  │                                                         │
│   │        │          │                                                         │
│   │        ▼          │                                                         │
│   │   ┌─────────┐     │                                                         │
│   │   │   EC2   │     │  Packet delivered to destination!                      │
│   │   │10.2.1.50│     │                                                         │
│   │   └─────────┘     │                                                         │
│   │                   │                                                         │
│   └───────────────────┘                                                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Cross-Region Transit Gateway Peering

### Inter-Region Peering Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CROSS-REGION TGW PEERING                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌────────────────────────────────┐  ┌────────────────────────────────┐        │
│   │          US-EAST-1             │  │          EU-WEST-1             │        │
│   │                                │  │                                │        │
│   │  VPC-A    VPC-B    VPC-C       │  │  VPC-X    VPC-Y    VPC-Z       │        │
│   │   │        │        │          │  │   │        │        │          │        │
│   │   └────────┼────────┘          │  │   └────────┼────────┘          │        │
│   │            │                   │  │            │                   │        │
│   │   ┌────────▼────────┐          │  │   ┌────────▼────────┐          │        │
│   │   │    TGW-US       │          │  │   │    TGW-EU       │          │        │
│   │   │  (tgw-us-xxx)   │◄────────────────►│  (tgw-eu-xxx)   │          │        │
│   │   └─────────────────┘  Peering │  │   └─────────────────┘          │        │
│   │                        Attach  │  │                                │        │
│   └────────────────────────────────┘  └────────────────────────────────┘        │
│                                                                                  │
│   ROUTE CONFIGURATION:                                                          │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   TGW-US Route Table:                  TGW-EU Route Table:              │   │
│   │   ┌──────────────────────────┐         ┌──────────────────────────┐     │   │
│   │   │ 10.1.0.0/16 → VPC-A     │         │ 10.4.0.0/16 → VPC-X     │     │   │
│   │   │ 10.2.0.0/16 → VPC-B     │         │ 10.5.0.0/16 → VPC-Y     │     │   │
│   │   │ 10.3.0.0/16 → VPC-C     │         │ 10.6.0.0/16 → VPC-Z     │     │   │
│   │   │ 10.4.0.0/14 → TGW-EU    │ Static  │ 10.0.0.0/14 → TGW-US    │     │   │
│   │   │ (EU CIDRs)   Peering    │         │ (US CIDRs)   Peering    │     │   │
│   │   └──────────────────────────┘         └──────────────────────────┘     │   │
│   │                                                                          │   │
│   │   Note: Peering routes must be added STATICALLY (no propagation)        │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   KEY POINTS:                                                                   │
│   • Inter-region peering uses AWS backbone (encrypted)                         │
│   • Static routes required (routes don't propagate across peering)             │
│   • Data transfer charges apply between regions                                │
│   • Supports different accounts                                                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Hands-On: Setting Up Transit Gateway

### Step 1: Create Transit Gateway

```bash
# Create Transit Gateway
aws ec2 create-transit-gateway \
    --description "My Transit Gateway" \
    --options "AmazonSideAsn=64512,AutoAcceptSharedAttachments=enable,DefaultRouteTableAssociation=enable,DefaultRouteTablePropagation=enable,DnsSupport=enable,VpnEcmpSupport=enable" \
    --tag-specifications 'ResourceType=transit-gateway,Tags=[{Key=Name,Value=my-tgw}]'

# Output:
# {
#     "TransitGateway": {
#         "TransitGatewayId": "tgw-0123456789abcdef0",
#         "TransitGatewayArn": "arn:aws:ec2:us-east-1:123456789012:transit-gateway/tgw-0123456789abcdef0",
#         "State": "pending",
#         "OwnerId": "123456789012",
#         "Options": {
#             "AmazonSideAsn": 64512,
#             "AutoAcceptSharedAttachments": "enable",
#             "DefaultRouteTableAssociation": "enable",
#             "DefaultRouteTablePropagation": "enable",
#             "DnsSupport": "enable",
#             "VpnEcmpSupport": "enable"
#         }
#     }
# }
```

### Step 2: Create VPC Attachments

```bash
# Create VPC attachment for Production VPC
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --vpc-id vpc-prod-12345678 \
    --subnet-ids subnet-prod-a subnet-prod-b \
    --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=prod-vpc-attachment}]'

# Create VPC attachment for Development VPC
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --vpc-id vpc-dev-87654321 \
    --subnet-ids subnet-dev-a subnet-dev-b \
    --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=dev-vpc-attachment}]'

# Create VPC attachment for Shared Services VPC
aws ec2 create-transit-gateway-vpc-attachment \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --vpc-id vpc-shared-11111111 \
    --subnet-ids subnet-shared-a subnet-shared-b \
    --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=shared-vpc-attachment}]'
```

### Step 3: Create Custom Route Tables (For Isolation)

```bash
# Create route table for production
aws ec2 create-transit-gateway-route-table \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=prod-rt}]'

# Create route table for development
aws ec2 create-transit-gateway-route-table \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=dev-rt}]'

# Create route table for shared services
aws ec2 create-transit-gateway-route-table \
    --transit-gateway-id tgw-0123456789abcdef0 \
    --tag-specifications 'ResourceType=transit-gateway-route-table,Tags=[{Key=Name,Value=shared-rt}]'
```

### Step 4: Configure Associations and Propagations

```bash
# Associate production VPC with prod-rt
aws ec2 associate-transit-gateway-route-table \
    --transit-gateway-route-table-id tgw-rtb-prod-xxxxx \
    --transit-gateway-attachment-id tgw-attach-prod-xxxxx

# Enable propagation from shared services to prod-rt
aws ec2 enable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-prod-xxxxx \
    --transit-gateway-attachment-id tgw-attach-shared-xxxxx

# Associate development VPC with dev-rt
aws ec2 associate-transit-gateway-route-table \
    --transit-gateway-route-table-id tgw-rtb-dev-xxxxx \
    --transit-gateway-attachment-id tgw-attach-dev-xxxxx

# Enable propagation from shared services to dev-rt
aws ec2 enable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-dev-xxxxx \
    --transit-gateway-attachment-id tgw-attach-shared-xxxxx

# Associate shared services with shared-rt
aws ec2 associate-transit-gateway-route-table \
    --transit-gateway-route-table-id tgw-rtb-shared-xxxxx \
    --transit-gateway-attachment-id tgw-attach-shared-xxxxx

# Enable propagation from both prod and dev to shared-rt
aws ec2 enable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-shared-xxxxx \
    --transit-gateway-attachment-id tgw-attach-prod-xxxxx

aws ec2 enable-transit-gateway-route-table-propagation \
    --transit-gateway-route-table-id tgw-rtb-shared-xxxxx \
    --transit-gateway-attachment-id tgw-attach-dev-xxxxx
```

### Step 5: Update VPC Route Tables

```bash
# Add route in Production VPC to reach other VPCs via TGW
aws ec2 create-route \
    --route-table-id rtb-prod-xxxxx \
    --destination-cidr-block 10.0.0.0/8 \
    --transit-gateway-id tgw-0123456789abcdef0

# Add route in Development VPC
aws ec2 create-route \
    --route-table-id rtb-dev-xxxxx \
    --destination-cidr-block 10.0.0.0/8 \
    --transit-gateway-id tgw-0123456789abcdef0

# Add route in Shared Services VPC
aws ec2 create-route \
    --route-table-id rtb-shared-xxxxx \
    --destination-cidr-block 10.0.0.0/8 \
    --transit-gateway-id tgw-0123456789abcdef0
```

### Step 6: Verify Configuration

```bash
# List Transit Gateway attachments
aws ec2 describe-transit-gateway-attachments \
    --filters "Name=transit-gateway-id,Values=tgw-0123456789abcdef0"

# Get route table routes
aws ec2 search-transit-gateway-routes \
    --transit-gateway-route-table-id tgw-rtb-prod-xxxxx \
    --filters "Name=state,Values=active"

# Verify VPC route tables
aws ec2 describe-route-tables \
    --route-table-ids rtb-prod-xxxxx
```

## Transit Gateway vs VPC Peering Comparison

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    TRANSIT GATEWAY vs VPC PEERING                               │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   Feature              │ Transit Gateway          │ VPC Peering                │
│   ─────────────────────┼──────────────────────────┼──────────────────────────  │
│   Transitive Routing   │ Yes                      │ No                         │
│   Scalability          │ Up to 5,000 attachments  │ 125 peerings per VPC       │
│   Bandwidth            │ Up to 50 Gbps per VPC    │ No limit                   │
│   Latency              │ Slightly higher          │ Lowest                     │
│   Cost                 │ Hourly + data            │ Data transfer only         │
│   Cross-Region         │ Yes (via TGW peering)    │ Yes                        │
│   Cross-Account        │ Yes (via RAM sharing)    │ Yes                        │
│   Network Segmentation │ Multiple route tables    │ Security Groups only       │
│   VPN/DX Integration   │ Native                   │ Not supported              │
│   Centralized Routing  │ Yes                      │ No (distributed)           │
│   Management           │ Centralized              │ Per-connection             │
│                                                                                 │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   WHEN TO USE WHAT:                                                            │
│                                                                                 │
│   Use VPC Peering when:                                                        │
│   • Connecting 2-3 VPCs                                                        │
│   • Need lowest possible latency                                               │
│   • Cost-sensitive (no hourly charges)                                         │
│   • Simple point-to-point connectivity                                         │
│                                                                                 │
│   Use Transit Gateway when:                                                    │
│   • Connecting many VPCs (>3)                                                  │
│   • Need hybrid connectivity (VPN/DX)                                          │
│   • Require network segmentation                                               │
│   • Building hub-and-spoke architecture                                        │
│   • Need centralized routing management                                        │
│   • Multi-region connectivity                                                  │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Pricing

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TRANSIT GATEWAY PRICING                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Cost Components:                                                              │
│                                                                                  │
│   1. Attachment Hours                                                           │
│      ┌──────────────────────────────────────────────────────────────────────┐   │
│      │ • $0.05 per VPC attachment per hour                                  │   │
│      │ • $0.05 per VPN attachment per hour                                  │   │
│      │ • $0.05 per Direct Connect attachment per hour                       │   │
│      │ • $0.05 per TGW peering attachment per hour                          │   │
│      │                                                                       │   │
│      │ Example: 10 VPC attachments for 1 month                              │   │
│      │ Cost = 10 × $0.05 × 730 hours = $365/month                           │   │
│      └──────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   2. Data Processing                                                            │
│      ┌──────────────────────────────────────────────────────────────────────┐   │
│      │ • $0.02 per GB of data processed                                     │   │
│      │                                                                       │   │
│      │ Example: 1 TB of data processed per month                            │   │
│      │ Cost = 1,000 GB × $0.02 = $20/month                                  │   │
│      └──────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   3. Cross-Region Data Transfer (if applicable)                                 │
│      ┌──────────────────────────────────────────────────────────────────────┐   │
│      │ • Standard AWS data transfer rates apply                             │   │
│      │ • Typically $0.02/GB between regions                                 │   │
│      └──────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   COST EXAMPLE:                                                                 │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                           │  │
│   │   Scenario: 5 VPCs, 1 VPN, 500 GB data/month                             │  │
│   │                                                                           │  │
│   │   Attachments: (5 VPC + 1 VPN) × $0.05 × 730 = $219.00                   │  │
│   │   Data Processing: 500 GB × $0.02 = $10.00                               │  │
│   │   ─────────────────────────────────────────────                          │  │
│   │   Total: $229.00/month                                                   │  │
│   │                                                                           │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Best Practices

### Design Best Practices

1. **Plan CIDR Blocks Carefully**
   - Ensure no overlapping CIDRs across all connected VPCs
   - Use summarization where possible (e.g., 10.0.0.0/8 for all internal)

2. **Use Multiple Route Tables**
   - Implement network segmentation for security
   - Separate production and development traffic

3. **High Availability**
   - Create attachments in multiple AZs
   - Use at least 2 subnets per VPC attachment

4. **Monitoring**
   - Enable TGW Flow Logs
   - Set up CloudWatch alarms for metrics

### Security Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TRANSIT GATEWAY SECURITY                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. Network Segmentation                                                       │
│      • Use separate route tables for different environments                     │
│      • Implement least-privilege routing                                        │
│      • Block direct prod-to-dev communication if not needed                     │
│                                                                                  │
│   2. Resource Access Manager (RAM)                                              │
│      • Share TGW only with required accounts                                    │
│      • Use Organizations for controlled sharing                                 │
│      • Review shared resources regularly                                        │
│                                                                                  │
│   3. Inspection VPC Pattern                                                     │
│      ┌──────────────────────────────────────────────────────────────────────┐   │
│      │                                                                       │   │
│      │   VPC-A                    Inspection VPC                VPC-B       │   │
│      │     │                           │                          │         │   │
│      │     └───────► Transit ◄─────────┼─────────► Transit ◄──────┘         │   │
│      │               Gateway           │           Gateway                  │   │
│      │                                 │                                    │   │
│      │                        ┌────────▼────────┐                           │   │
│      │                        │    Firewall     │                           │   │
│      │                        │   Appliance     │                           │   │
│      │                        └─────────────────┘                           │   │
│      │                                                                       │   │
│      │   All traffic between VPCs flows through firewall for inspection     │   │
│      │                                                                       │   │
│      └──────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   4. Monitoring and Auditing                                                    │
│      • Enable VPC Flow Logs on all attached VPCs                               │
│      • Use CloudTrail for API auditing                                         │
│      • Set up alerts for route table changes                                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't reach destination VPC | Missing route in VPC route table | Add route to TGW |
| One-way connectivity | Asymmetric routing | Check routes in both directions |
| Intermittent connectivity | Wrong AZ subnet attachment | Ensure attachments in all AZs |
| Cross-region not working | Missing static route | Add static route for peered TGW |
| Attachment pending | VPC/subnet not ready | Wait or check VPC configuration |

### Troubleshooting Steps

```bash
# 1. Verify Transit Gateway state
aws ec2 describe-transit-gateways \
    --transit-gateway-ids tgw-0123456789abcdef0

# 2. Check attachment state
aws ec2 describe-transit-gateway-attachments \
    --filters "Name=transit-gateway-id,Values=tgw-0123456789abcdef0"

# 3. Verify route table routes
aws ec2 search-transit-gateway-routes \
    --transit-gateway-route-table-id tgw-rtb-xxxxx \
    --filters "Name=state,Values=active"

# 4. Check VPC route tables
aws ec2 describe-route-tables \
    --filters "Name=vpc-id,Values=vpc-xxxxx"

# 5. Verify security groups allow traffic
aws ec2 describe-security-groups \
    --group-ids sg-xxxxx
```

## Key Takeaways

1. **Transit Gateway** is a central hub for connecting VPCs and on-premises networks
2. **Transitive routing** is the key differentiator from VPC peering
3. **Route tables** control traffic flow between attachments
4. **Associations** determine where traffic FROM an attachment goes
5. **Propagations** automatically add routes TO route tables
6. Use **multiple route tables** for network segmentation
7. **Cross-region peering** requires static routes
8. Consider **cost** - attachment hours + data processing

---

**Next:** [09-vpc-flow-logs.md](09-vpc-flow-logs.md) - Learn how to monitor network traffic with VPC Flow Logs
