# 10 - Hybrid Connectivity

## Overview

Hybrid connectivity enables communication between your on-premises data center and AWS cloud resources. AWS provides multiple options for establishing secure, reliable connections.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        HYBRID CONNECTIVITY OPTIONS                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                     ON-PREMISES DATA CENTER                                      │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐            │   │
│   │   │ Servers  │   │ Database │   │ Storage  │   │ Users    │            │   │
│   │   └──────────┘   └──────────┘   └──────────┘   └──────────┘            │   │
│   │                                                                          │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │                    Customer Gateway                              │   │   │
│   │   │              (Router/Firewall Device)                           │   │   │
│   │   └───────────────────────────┬─────────────────────────────────────┘   │   │
│   └───────────────────────────────┼─────────────────────────────────────────┘   │
│                                   │                                              │
│           ┌───────────────────────┼───────────────────────┐                     │
│           │                       │                       │                     │
│           ▼                       ▼                       ▼                     │
│   ┌───────────────┐      ┌───────────────┐      ┌───────────────┐              │
│   │  Site-to-Site │      │    Direct     │      │    Client     │              │
│   │     VPN       │      │   Connect     │      │     VPN       │              │
│   │               │      │               │      │               │              │
│   │ • Over internet      │ • Dedicated   │      │ • Remote users│              │
│   │ • Encrypted   │      │   private link│      │ • Over internet│             │
│   │ • Quick setup │      │ • Consistent  │      │ • OpenVPN     │              │
│   │ • Up to 1.25Gbps     │   latency     │      │   compatible  │              │
│   │               │      │ • 1-100 Gbps  │      │               │              │
│   └───────┬───────┘      └───────┬───────┘      └───────┬───────┘              │
│           │                      │                      │                       │
│           └──────────────────────┼──────────────────────┘                       │
│                                  │                                              │
│                                  ▼                                              │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                           AWS CLOUD                                       │  │
│   │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │  │
│   │   │    VPC A     │   │    VPC B     │   │    VPC C     │                 │  │
│   │   │              │   │              │   │              │                 │  │
│   │   └──────────────┘   └──────────────┘   └──────────────┘                 │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## AWS Site-to-Site VPN

### What is Site-to-Site VPN?

AWS Site-to-Site VPN creates an encrypted connection between your on-premises network and your VPCs over the public internet.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        SITE-TO-SITE VPN ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ON-PREMISES                          AWS CLOUD                                │
│   ┌──────────────────────┐             ┌──────────────────────────────────────┐ │
│   │                      │             │                                       │ │
│   │   ┌──────────────┐   │             │   ┌──────────────────────────────┐   │ │
│   │   │  Servers     │   │             │   │           VPC                │   │ │
│   │   │  10.1.0.0/16 │   │             │   │        10.0.0.0/16           │   │ │
│   │   └──────┬───────┘   │             │   │                              │   │ │
│   │          │           │             │   │   ┌───────┐    ┌───────┐     │   │ │
│   │          │           │             │   │   │  EC2  │    │  RDS  │     │   │ │
│   │   ┌──────▼───────┐   │             │   │   └───────┘    └───────┘     │   │ │
│   │   │   Customer   │   │             │   │                              │   │ │
│   │   │   Gateway    │   │             │   └──────────────┬───────────────┘   │ │
│   │   │  (CGW)       │   │             │                  │                   │ │
│   │   │              │   │             │         ┌────────▼────────┐          │ │
│   │   │ Public IP:   │   │             │         │   Virtual       │          │ │
│   │   │ 203.0.113.50 │   │             │         │   Private       │          │ │
│   │   └──────┬───────┘   │             │         │   Gateway       │          │ │
│   │          │           │             │         │   (VGW)         │          │ │
│   └──────────┼───────────┘             │         └────────┬────────┘          │ │
│              │                          │                  │                   │ │
│              │      INTERNET           │                  │                   │ │
│              │                          │                  │                   │ │
│              │   ╔════════════════════════════════════╗   │                   │ │
│              │   ║     IPsec VPN Tunnel 1             ║   │                   │ │
│              └───╬════════════════════════════════════╬───┘                   │ │
│                  ║     IPsec VPN Tunnel 2             ║                       │ │
│                  ╚════════════════════════════════════╝                       │ │
│                                                                                  │
│   KEY COMPONENTS:                                                               │
│   • VGW (Virtual Private Gateway): AWS-side VPN endpoint                       │
│   • CGW (Customer Gateway): Your on-premises VPN device                        │
│   • VPN Connection: Contains 2 tunnels for redundancy                          │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### VPN Components

| Component | Description |
|-----------|-------------|
| **Virtual Private Gateway (VGW)** | AWS-managed VPN concentrator, attached to VPC |
| **Customer Gateway (CGW)** | Represents your on-premises VPN device |
| **VPN Connection** | Secure connection containing 2 IPsec tunnels |
| **VPN Tunnel** | Encrypted link (each connection has 2 for HA) |

### Site-to-Site VPN Setup Steps

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VPN SETUP PROCESS                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Step 1: Create Customer Gateway                                               │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   aws ec2 create-customer-gateway \                                     │   │
│   │       --type ipsec.1 \                                                  │   │
│   │       --public-ip 203.0.113.50 \                                        │   │
│   │       --bgp-asn 65000 \                                                 │   │
│   │       --tag-specifications 'ResourceType=customer-gateway,              │   │
│   │           Tags=[{Key=Name,Value=my-cgw}]'                               │   │
│   │                                                                          │   │
│   │   Note: BGP ASN required even for static routing                        │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Step 2: Create Virtual Private Gateway                                        │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   aws ec2 create-vpn-gateway \                                          │   │
│   │       --type ipsec.1 \                                                  │   │
│   │       --amazon-side-asn 64512 \                                         │   │
│   │       --tag-specifications 'ResourceType=vpn-gateway,                   │   │
│   │           Tags=[{Key=Name,Value=my-vgw}]'                               │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Step 3: Attach VGW to VPC                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   aws ec2 attach-vpn-gateway \                                          │   │
│   │       --vpn-gateway-id vgw-0123456789abcdef0 \                          │   │
│   │       --vpc-id vpc-0123456789abcdef0                                    │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Step 4: Create VPN Connection                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   aws ec2 create-vpn-connection \                                       │   │
│   │       --type ipsec.1 \                                                  │   │
│   │       --customer-gateway-id cgw-0123456789abcdef0 \                     │   │
│   │       --vpn-gateway-id vgw-0123456789abcdef0 \                          │   │
│   │       --options '{"StaticRoutesOnly":false}'                            │   │
│   │                                                                          │   │
│   │   # For static routing:                                                 │   │
│   │   --options '{"StaticRoutesOnly":true}'                                 │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Step 5: Download VPN Configuration                                            │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   # Download configuration for your specific device                     │   │
│   │   # Supported vendors: Cisco, Juniper, Palo Alto, Fortinet, etc.       │   │
│   │   # Apply configuration to your customer gateway device                 │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Step 6: Update VPC Route Table                                                │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   # Enable route propagation (for BGP)                                  │   │
│   │   aws ec2 enable-vgw-route-propagation \                                │   │
│   │       --gateway-id vgw-0123456789abcdef0 \                              │   │
│   │       --route-table-id rtb-0123456789abcdef0                            │   │
│   │                                                                          │   │
│   │   # Or add static route                                                 │   │
│   │   aws ec2 create-route \                                                │   │
│   │       --route-table-id rtb-0123456789abcdef0 \                          │   │
│   │       --destination-cidr-block 10.1.0.0/16 \                            │   │
│   │       --gateway-id vgw-0123456789abcdef0                                │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### VPN Routing Options

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VPN ROUTING OPTIONS                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   STATIC ROUTING                                                                │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   On-Premises          VPN          AWS                                 │   │
│   │   10.1.0.0/16         Tunnel       10.0.0.0/16                          │   │
│   │                                                                          │   │
│   │   Manual Configuration:                                                 │   │
│   │   • AWS Route Table: 10.1.0.0/16 -> VGW                                │   │
│   │   • On-Prem Router: 10.0.0.0/16 -> VPN Tunnel                          │   │
│   │                                                                          │   │
│   │   Pros:                             Cons:                               │   │
│   │   • Simple to configure            • Manual updates needed              │   │
│   │   • Works with any device          • No automatic failover              │   │
│   │                                    • Doesn't scale well                 │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   DYNAMIC ROUTING (BGP)                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   On-Premises          BGP Session        AWS                           │   │
│   │   ASN: 65000          ◄──────────►       ASN: 64512                     │   │
│   │                                                                          │   │
│   │   Automatic Route Exchange:                                             │   │
│   │   • Routes learned via BGP                                              │   │
│   │   • VPC CIDR advertised automatically                                   │   │
│   │   • On-prem routes propagated to VPC                                    │   │
│   │                                                                          │   │
│   │   Pros:                             Cons:                               │   │
│   │   • Automatic updates              • Requires BGP-capable device        │   │
│   │   • Automatic failover             • More complex configuration         │   │
│   │   • Scales well                                                         │   │
│   │                                                                          │   │
│   │   AWS BGP Configuration:                                                │   │
│   │   • Amazon ASN: 64512 (default) or custom                              │   │
│   │   • Customer ASN: Your choice (1-65534)                                │   │
│   │   • BGP Peer: Inside tunnel IPs (169.254.x.x/30)                       │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### VPN with Transit Gateway

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VPN WITH TRANSIT GATEWAY                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Use Transit Gateway instead of VGW for:                                       │
│   • Connecting VPN to multiple VPCs                                            │
│   • ECMP (Equal Cost Multi-Path) for higher bandwidth                          │
│   • Centralized VPN management                                                  │
│                                                                                  │
│   ON-PREMISES                              AWS CLOUD                            │
│   ┌──────────────┐                                                              │
│   │   Customer   │         VPN Tunnels                                          │
│   │   Gateway    │═════════════════════════════════════╗                        │
│   │              │═════════════════════════════════════╬════════╗               │
│   └──────────────┘                                     ║        ║               │
│                                                        ║        ║               │
│                                            ┌───────────▼────────▼───────────┐   │
│                                            │      Transit Gateway           │   │
│                                            │                                │   │
│                                            │   VPN Attachment               │   │
│                                            │   (ECMP Enabled)               │   │
│                                            │                                │   │
│                                            └─────────────┬──────────────────┘   │
│                                                          │                      │
│                              ┌────────────────┬──────────┴─────────┬────────┐   │
│                              │                │                    │        │   │
│                              ▼                ▼                    ▼        ▼   │
│                         ┌────────┐       ┌────────┐          ┌────────┐         │
│                         │ VPC-A  │       │ VPC-B  │          │ VPC-C  │         │
│                         └────────┘       └────────┘          └────────┘         │
│                                                                                  │
│   ECMP Benefits:                                                                │
│   • 2 VPN connections = 2 × 1.25 Gbps = 2.5 Gbps                               │
│   • Up to 50 VPN connections per TGW attachment                                │
│   • Load balancing across tunnels                                              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## AWS Direct Connect

### What is Direct Connect?

AWS Direct Connect is a dedicated, private network connection from your premises to AWS, bypassing the public internet entirely.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DIRECT CONNECT ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   YOUR DATA CENTER                                                              │
│   ┌────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                         │   │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐                           │   │
│   │   │ Servers  │   │ Database │   │ Storage  │                           │   │
│   │   └────┬─────┘   └────┬─────┘   └────┬─────┘                           │   │
│   │        │              │              │                                  │   │
│   │        └──────────────┼──────────────┘                                  │   │
│   │                       │                                                 │   │
│   │               ┌───────▼───────┐                                         │   │
│   │               │    Router     │                                         │   │
│   │               └───────┬───────┘                                         │   │
│   │                       │                                                 │   │
│   └───────────────────────┼─────────────────────────────────────────────────┘   │
│                           │                                                      │
│                           │  Your network or                                    │
│                           │  carrier connection                                 │
│                           │                                                      │
│   ┌───────────────────────▼─────────────────────────────────────────────────┐   │
│   │                   DIRECT CONNECT LOCATION                                │   │
│   │                   (Colocation Facility)                                  │   │
│   │                                                                          │   │
│   │   ┌──────────────────────────────────────────────────────────────────┐  │   │
│   │   │                  AWS Direct Connect Cage                          │  │   │
│   │   │                                                                   │  │   │
│   │   │   ┌─────────────────────────────────────────────────────────┐    │  │   │
│   │   │   │           AWS Direct Connect Router                      │    │  │   │
│   │   │   │                                                          │    │  │   │
│   │   │   │   Cross Connect (Physical Cable)                        │    │  │   │
│   │   │   │   ←──────────────────────────────────────────────────── │    │  │   │
│   │   │   │                                                          │    │  │   │
│   │   │   │   Connection Speed: 1 Gbps, 10 Gbps, or 100 Gbps        │    │  │   │
│   │   │   └─────────────────────────────────────────────────────────┘    │  │   │
│   │   │                                                                   │  │   │
│   │   └───────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                          │   │
│   └──────────────────────────────────────────────────────────────────────────┘   │
│                                       │                                          │
│                                       │ AWS Backbone                             │
│                                       │                                          │
│   ┌───────────────────────────────────▼──────────────────────────────────────┐  │
│   │                              AWS CLOUD                                    │  │
│   │                                                                           │  │
│   │   ┌──────────────────────────────────────────────────────────────────┐   │  │
│   │   │             Direct Connect Gateway (Optional)                     │   │  │
│   │   │                                                                   │   │  │
│   │   │   Enables connectivity to multiple VPCs/Regions                  │   │  │
│   │   │                                                                   │   │  │
│   │   └─────────────────────────────┬────────────────────────────────────┘   │  │
│   │                                 │                                         │  │
│   │       ┌─────────────────────────┼─────────────────────────┐              │  │
│   │       │                         │                         │              │  │
│   │       ▼                         ▼                         ▼              │  │
│   │   ┌────────┐              ┌──────────┐              ┌────────┐          │  │
│   │   │ VPC-A  │              │  VPC-B   │              │ VPC-C  │          │  │
│   │   │(VGW)   │              │  (VGW)   │              │ (VGW)  │          │  │
│   │   └────────┘              └──────────┘              └────────┘          │  │
│   │                                                                           │  │
│   └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Direct Connect Connection Types

| Type | Speed | Lead Time | Use Case |
|------|-------|-----------|----------|
| **Dedicated Connection** | 1, 10, 100 Gbps | Weeks | Large enterprises, consistent high bandwidth |
| **Hosted Connection** | 50 Mbps - 10 Gbps | Days | Smaller bandwidth needs, faster setup |
| **Hosted Virtual Interface** | Shared | Days | Accessing specific VPC via partner |

### Virtual Interfaces (VIFs)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VIRTUAL INTERFACES                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   A Direct Connect connection can have multiple Virtual Interfaces              │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                    Direct Connect (10 Gbps)                              │   │
│   │                                                                          │   │
│   │   ┌──────────────────────────────────────────────────────────────────┐  │   │
│   │   │                                                                   │  │   │
│   │   │   Private VIF              Public VIF            Transit VIF     │  │   │
│   │   │   (VLAN 100)               (VLAN 200)            (VLAN 300)      │  │   │
│   │   │       │                        │                      │          │  │   │
│   │   │       │                        │                      │          │  │   │
│   │   │       ▼                        ▼                      ▼          │  │   │
│   │   │   ┌───────┐              ┌───────────┐         ┌──────────┐     │  │   │
│   │   │   │  VPC  │              │   AWS     │         │ Transit  │     │  │   │
│   │   │   │ (VGW) │              │ Public    │         │ Gateway  │     │  │   │
│   │   │   │       │              │ Services  │         │          │     │  │   │
│   │   │   │       │              │           │         │          │     │  │   │
│   │   │   │ EC2   │              │ S3, DynamoDB        │ Multiple │     │  │   │
│   │   │   │ RDS   │              │ Glacier   │         │ VPCs     │     │  │   │
│   │   │   └───────┘              └───────────┘         └──────────┘     │  │   │
│   │   │                                                                   │  │   │
│   │   └──────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   VIF TYPES:                                                                    │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                                                                           │  │
│   │   PRIVATE VIF                                                            │  │
│   │   • Access VPC resources via private IP                                  │  │
│   │   • Connects to Virtual Private Gateway (VGW)                           │  │
│   │   • Uses BGP for routing                                                 │  │
│   │   • Most common use case                                                 │  │
│   │                                                                           │  │
│   │   PUBLIC VIF                                                             │  │
│   │   • Access AWS public services (S3, DynamoDB, etc.)                     │  │
│   │   • Uses AWS public IP ranges                                           │  │
│   │   • Good for accessing public endpoints privately                       │  │
│   │   • Does NOT go through internet                                        │  │
│   │                                                                           │  │
│   │   TRANSIT VIF                                                            │  │
│   │   • Connects to Transit Gateway                                         │  │
│   │   • Access multiple VPCs via single VIF                                 │  │
│   │   • Recommended for multi-VPC architectures                             │  │
│   │                                                                           │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Direct Connect Gateway

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DIRECT CONNECT GATEWAY                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Direct Connect Gateway enables access to VPCs in multiple regions            │
│   from a single Direct Connect connection                                       │
│                                                                                  │
│   ON-PREMISES                                                                   │
│   ┌──────────────┐                                                              │
│   │   Customer   │                                                              │
│   │   Router     │                                                              │
│   └──────┬───────┘                                                              │
│          │                                                                       │
│          │ Direct Connect                                                        │
│          │                                                                       │
│   ┌──────▼────────────────────────────────────────────────────────────────────┐ │
│   │                  DIRECT CONNECT LOCATION (us-east-1)                       │ │
│   │                                                                             │ │
│   │   Private VIF                                                              │ │
│   │       │                                                                     │ │
│   └───────┼─────────────────────────────────────────────────────────────────────┘ │
│           │                                                                      │
│           │                                                                      │
│   ┌───────▼─────────────────────────────────────────────────────────────────────┐│
│   │                      DIRECT CONNECT GATEWAY                                  ││
│   │                          (Global Resource)                                   ││
│   │                                                                              ││
│   │   ┌──────────────────────────────────────────────────────────────────────┐  ││
│   │   │  Associations:                                                        │  ││
│   │   │                                                                       │  ││
│   │   │  VGW-1 (us-east-1)  ◄──────────────────────────────►  VPC-A           │  ││
│   │   │  VGW-2 (us-west-2)  ◄──────────────────────────────►  VPC-B           │  ││
│   │   │  VGW-3 (eu-west-1)  ◄──────────────────────────────►  VPC-C           │  ││
│   │   │  TGW-1 (ap-south-1) ◄──────────────────────────────►  Multiple VPCs   │  ││
│   │   │                                                                       │  ││
│   │   └──────────────────────────────────────────────────────────────────────┘  ││
│   │                                                                              ││
│   └──────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│   BENEFITS:                                                                     │
│   • Single Direct Connect to multiple VPCs in different regions               │
│   • Global reach from single connection                                        │
│   • Simplified architecture                                                    │
│   • Up to 10 VGWs per Direct Connect Gateway                                   │
│                                                                                  │
│   LIMITATIONS:                                                                  │
│   • VPCs connected to same DX Gateway cannot have overlapping CIDRs           │
│   • Traffic between VPCs doesn't go through DX Gateway (use TGW)              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Direct Connect Resilience

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DIRECT CONNECT RESILIENCE PATTERNS                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SINGLE CONNECTION (No Resilience - NOT Recommended)                           │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │   Data Center ────────────── DX Location ────────────── AWS            │   │
│   │                                                                          │   │
│   │   Single Point of Failure at every component!                           │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   HIGH RESILIENCE (Recommended for Production)                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Data Center                                                           │   │
│   │   ┌───────────────────────────────────────────────────────────────┐     │   │
│   │   │  Router-1 ─────────────────────────────────────┐              │     │   │
│   │   │     │                                          │              │     │   │
│   │   │  Router-2 ──────────────────────────────┐      │              │     │   │
│   │   └─────┼───────────────────────────────────┼──────┼──────────────┘     │   │
│   │         │                                   │      │                    │   │
│   │         │                                   │      │                    │   │
│   │   ┌─────▼──────┐                     ┌──────▼──────▼────┐               │   │
│   │   │ DX Location│                     │   DX Location    │               │   │
│   │   │     A      │                     │       B          │               │   │
│   │   └─────┬──────┘                     └─────────┬────────┘               │   │
│   │         │                                      │                        │   │
│   │         └─────────────────┬────────────────────┘                        │   │
│   │                           │                                             │   │
│   │                           ▼                                             │   │
│   │                    ┌──────────────┐                                     │   │
│   │                    │     VPC      │                                     │   │
│   │                    │    (VGW)     │                                     │   │
│   │                    └──────────────┘                                     │   │
│   │                                                                          │   │
│   │   Features:                                                             │   │
│   │   • Two connections to different DX locations                          │   │
│   │   • Redundant customer routers                                         │   │
│   │   • BGP for automatic failover                                         │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   MAXIMUM RESILIENCE (Critical Workloads)                                       │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Data Center-1              Data Center-2                              │   │
│   │   ┌──────────┐               ┌──────────┐                               │   │
│   │   │ Router   │               │ Router   │                               │   │
│   │   └────┬─────┘               └────┬─────┘                               │   │
│   │        │                          │                                     │   │
│   │   ┌────▼────┐                ┌────▼────┐                               │   │
│   │   │ DX Loc A│                │ DX Loc B│                               │   │
│   │   └────┬────┘                └────┬────┘                               │   │
│   │        │                          │                                     │   │
│   │        │     ┌──────────────┐     │                                     │   │
│   │        └────►│   VPC (VGW)  │◄────┘                                     │   │
│   │              └──────────────┘                                           │   │
│   │                    +                                                    │   │
│   │              ┌──────────────┐                                           │   │
│   │              │  VPN Backup  │  ◄── Backup via internet                 │   │
│   │              └──────────────┘                                           │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## AWS VPN CloudHub

### What is VPN CloudHub?

VPN CloudHub enables secure communication between multiple remote sites using AWS as the hub.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VPN CLOUDHUB ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Use Case: Connect multiple branch offices through AWS                         │
│                                                                                  │
│                                                                                  │
│   Branch Office A                            Branch Office B                    │
│   (New York)                                 (London)                           │
│   ┌──────────────┐                           ┌──────────────┐                   │
│   │  CGW-A       │                           │  CGW-B       │                   │
│   │  ASN: 65001  │                           │  ASN: 65002  │                   │
│   └──────┬───────┘                           └──────┬───────┘                   │
│          │                                          │                           │
│          │ VPN                                 VPN │                            │
│          │                                          │                           │
│          │         ┌────────────────────┐          │                           │
│          │         │                    │          │                           │
│          └────────►│  Virtual Private   │◄─────────┘                           │
│                    │  Gateway (VGW)     │                                       │
│          ┌────────►│                    │◄─────────┐                           │
│          │         │  AWS VPN CloudHub  │          │                           │
│          │         └─────────┬──────────┘          │                           │
│          │                   │                     │                           │
│          │ VPN               │ VPC                VPN │                         │
│          │                   │                     │                           │
│   ┌──────┴───────┐    ┌──────▼──────┐      ┌──────┴───────┐                   │
│   │  CGW-C       │    │    VPC      │      │  CGW-D       │                   │
│   │  ASN: 65003  │    │ 10.0.0.0/16 │      │  ASN: 65004  │                   │
│   └──────────────┘    │             │      └──────────────┘                   │
│                       │   AWS       │                                          │
│   Branch Office C     │  Resources  │      Branch Office D                     │
│   (Tokyo)             └─────────────┘      (Sydney)                            │
│                                                                                  │
│   HOW IT WORKS:                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   1. Each branch has VPN connection to same VGW                         │   │
│   │   2. Each branch uses unique BGP ASN                                    │   │
│   │   3. Routes advertised via BGP between all sites                        │   │
│   │   4. Branch-to-branch traffic flows through VGW                         │   │
│   │                                                                          │   │
│   │   Traffic Path: Branch A → VGW → Branch B                               │   │
│   │                                                                          │   │
│   │   Benefits:                                                             │   │
│   │   • No need for separate site-to-site VPNs between branches            │   │
│   │   • Centralized management                                              │   │
│   │   • Cost-effective for multiple sites                                   │   │
│   │   • Branches can also access VPC resources                              │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   REQUIREMENTS:                                                                 │
│   • BGP-capable customer gateway devices                                        │
│   • Unique BGP ASN for each site                                               │
│   • VPN connections to same VGW                                                │
│   • Dynamic routing enabled                                                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Comparison Table

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        HYBRID CONNECTIVITY COMPARISON                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Feature           │ Site-to-Site VPN  │ Direct Connect  │ Client VPN         │
│   ──────────────────┼───────────────────┼─────────────────┼────────────────     │
│   Connection        │ Over internet     │ Dedicated link  │ Over internet      │
│   Bandwidth         │ Up to 1.25 Gbps   │ 1-100 Gbps     │ Per connection     │
│   Latency           │ Variable          │ Consistent     │ Variable           │
│   Encryption        │ IPsec             │ Optional MACsec│ TLS                │
│   Setup Time        │ Minutes           │ Weeks/Months   │ Minutes            │
│   Cost              │ Hourly + data     │ Port + data    │ Hourly + data      │
│   Redundancy        │ Dual tunnels      │ Build yourself │ AWS managed        │
│   Use Case          │ Quick hybrid      │ Large, consistent│ Remote users      │
│                     │ connectivity      │ workloads       │                    │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   WHEN TO USE WHAT:                                                             │
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   SITE-TO-SITE VPN:                                                     │   │
│   │   • Quick connectivity needed                                           │   │
│   │   • Backup for Direct Connect                                           │   │
│   │   • Variable/bursty traffic                                             │   │
│   │   • Cost-sensitive                                                      │   │
│   │   • Acceptable latency variability                                      │   │
│   │                                                                          │   │
│   │   DIRECT CONNECT:                                                       │   │
│   │   • Large data transfers (TB+)                                          │   │
│   │   • Consistent, low latency required                                    │   │
│   │   • High bandwidth needed (>1 Gbps)                                     │   │
│   │   • Regulatory/compliance requirements                                  │   │
│   │   • Predictable network performance                                     │   │
│   │                                                                          │   │
│   │   VPN + DIRECT CONNECT:                                                 │   │
│   │   • Primary: Direct Connect                                             │   │
│   │   • Backup: VPN over internet                                           │   │
│   │   • Provides resilience against DX failures                             │   │
│   │                                                                          │   │
│   │   CLIENT VPN:                                                           │   │
│   │   • Remote employee access                                              │   │
│   │   • Contractor/partner access                                           │   │
│   │   • Mobile workforce                                                    │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Pricing Summary

| Service | Cost Components |
|---------|-----------------|
| **Site-to-Site VPN** | $0.05/hour per VPN connection + data transfer |
| **Direct Connect** | Port hours ($0.30/hr for 1G, $2.25/hr for 10G) + data transfer OUT |
| **Direct Connect Gateway** | No additional charge |
| **Client VPN** | $0.05/hour per subnet association + $0.05/hour per connection |

## Best Practices

1. **Always use dual tunnels** for VPN (AWS provides 2 tunnels)
2. **Use BGP** when possible for automatic failover
3. **Implement Direct Connect + VPN** for maximum resilience
4. **Monitor tunnel status** with CloudWatch
5. **Plan CIDR blocks** to avoid overlap with on-premises
6. **Use Transit Gateway** for connecting VPN to multiple VPCs
7. **Enable acceleration** on VPN for improved performance
8. **Document your BGP ASN** allocation

## Troubleshooting

| Issue | Check |
|-------|-------|
| VPN not coming up | Security group, NACL, CGW configuration, IKE/IPsec settings |
| Tunnel flapping | Dead Peer Detection settings, internet stability |
| Routes not propagating | BGP session status, route table propagation enabled |
| Slow performance | Bandwidth limits, MTU size (reduce to 1400 for VPN) |
| One-way traffic | Security groups, route tables on both sides |

---

**Next:** [11-hands-on-lab.md](11-hands-on-lab.md) - Complete hands-on lab to build a production-ready VPC
