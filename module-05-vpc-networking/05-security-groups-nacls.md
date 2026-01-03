# 05 - Security Groups and Network ACLs

## Network Security Layers

AWS VPC provides two layers of network security: Security Groups (instance level) and Network ACLs (subnet level).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NETWORK SECURITY LAYERS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              INTERNET                                        │
│                                 │                                            │
│                                 ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         VPC                                          │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                      SUBNET                                  │   │   │
│   │   │   ┌─────────────────────────────────────────────────────┐   │   │   │
│   │   │   │    NETWORK ACL (NACL) ◄── Layer 1: Subnet Level    │   │   │   │
│   │   │   │    • Stateless                                      │   │   │   │
│   │   │   │    • Rules evaluated in order                       │   │   │   │
│   │   │   │    • Allow AND Deny rules                           │   │   │   │
│   │   │   └─────────────────────────────────────────────────────┘   │   │   │
│   │   │                           │                                  │   │   │
│   │   │                           ▼                                  │   │   │
│   │   │   ┌─────────────────────────────────────────────────────┐   │   │   │
│   │   │   │    SECURITY GROUP ◄── Layer 2: Instance Level      │   │   │   │
│   │   │   │    • Stateful                                       │   │   │   │
│   │   │   │    • All rules evaluated                            │   │   │   │
│   │   │   │    • Allow rules only (implicit deny)               │   │   │   │
│   │   │   │                                                      │   │   │   │
│   │   │   │   ┌─────────────────────────────────────────────┐   │   │   │   │
│   │   │   │   │              EC2 INSTANCE                    │   │   │   │   │
│   │   │   │   │                                              │   │   │   │   │
│   │   │   │   └─────────────────────────────────────────────┘   │   │   │   │
│   │   │   └─────────────────────────────────────────────────────┘   │   │   │
│   │   │                                                              │   │   │
│   │   └──────────────────────────────────────────────────────────────┘   │   │
│   │                                                                      │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Security Groups

Security Groups act as a virtual firewall for your instances to control inbound and outbound traffic.

### Security Group Characteristics

| Feature | Description |
|---------|-------------|
| **Level** | Instance (ENI) level |
| **State** | Stateful - return traffic automatically allowed |
| **Default** | Denies all inbound, allows all outbound |
| **Rules** | Allow only (no explicit deny) |
| **Evaluation** | All rules evaluated before decision |
| **Scope** | VPC-specific |

### Stateful Behavior Explained

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATEFUL SECURITY GROUP                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Security Group Rules:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Inbound: Allow TCP/443 from 0.0.0.0/0                               │   │
│   │ Outbound: (not configured for 443)                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│                                                                              │
│   Client (1.2.3.4)                           EC2 Instance                   │
│   ┌───────────────┐                         ┌───────────────┐               │
│   │               │ ═══ HTTPS Request ════► │               │               │
│   │               │   src: 1.2.3.4:54321    │               │               │
│   │   Browser     │   dst: 10.0.1.5:443     │   Web Server  │               │
│   │               │                          │               │               │
│   │               │ ◄══ HTTPS Response ════ │               │               │
│   │               │   src: 10.0.1.5:443     │               │               │
│   │               │   dst: 1.2.3.4:54321    │               │               │
│   └───────────────┘                         └───────────────┘               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   INBOUND REQUEST (port 443):                                       │   │
│   │   ✓ Allowed by inbound rule                                         │   │
│   │                                                                      │   │
│   │   OUTBOUND RESPONSE:                                                │   │
│   │   ✓ Automatically allowed (STATEFUL!)                               │   │
│   │     Security Group "remembers" the connection                       │   │
│   │     No outbound rule needed for response traffic                    │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security Group Rule Components

| Component | Description | Examples |
|-----------|-------------|----------|
| **Type** | Protocol type | SSH, HTTP, Custom TCP |
| **Protocol** | IP protocol | TCP, UDP, ICMP |
| **Port Range** | Port or range | 22, 443, 1024-65535 |
| **Source/Destination** | Traffic origin/target | CIDR, SG, Prefix List |
| **Description** | Optional note | "Allow web traffic" |

### Security Group Reference Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY GROUP REFERENCING                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Pattern 1: CIDR-based (Less flexible)                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Web-SG                              App-SG                        │   │
│   │   Inbound: 0.0.0.0/0:443              Inbound: 10.0.1.0/24:8080    │   │
│   │                                                                      │   │
│   │   ┌─────────────┐                     ┌─────────────┐               │   │
│   │   │  Web Tier   │ ──────────────────► │  App Tier   │               │   │
│   │   │ 10.0.1.x    │    10.0.1.0/24      │ 10.0.2.x    │               │   │
│   │   └─────────────┘                     └─────────────┘               │   │
│   │                                                                      │   │
│   │   Problem: Must update if IPs change                                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Pattern 2: Security Group Reference (Recommended)                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Web-SG (sg-web)                     App-SG (sg-app)               │   │
│   │   Inbound: 0.0.0.0/0:443              Inbound: sg-web:8080         │   │
│   │                                                                      │   │
│   │   ┌─────────────┐                     ┌─────────────┐               │   │
│   │   │  Web Tier   │ ──────────────────► │  App Tier   │               │   │
│   │   │  sg-web     │    Reference SG     │  sg-app     │               │   │
│   │   └─────────────┘                     └─────────────┘               │   │
│   │                                                                      │   │
│   │   ✓ Automatically applies to all instances in sg-web                │   │
│   │   ✓ Works regardless of IP address                                  │   │
│   │   ✓ Scales with Auto Scaling                                        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Three-Tier Security Group Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THREE-TIER SECURITY GROUP ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              Internet                                        │
│                                 │                                            │
│                                 ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     ALB Security Group (sg-alb)                      │   │
│   │   Inbound:  443 from 0.0.0.0/0                                      │   │
│   │   Outbound: All (default)                                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                 │                                            │
│                                 ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     Web Security Group (sg-web)                      │   │
│   │   Inbound:  80 from sg-alb                                          │   │
│   │   Outbound: All (default)                                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                 │                                            │
│                                 ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     App Security Group (sg-app)                      │   │
│   │   Inbound:  8080 from sg-web                                        │   │
│   │   Outbound: All (default)                                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                 │                                            │
│                                 ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     DB Security Group (sg-db)                        │   │
│   │   Inbound:  3306 from sg-app                                        │   │
│   │   Outbound: (none needed for RDS)                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Key Points:                                                               │
│   • Each tier only accepts traffic from the tier above                      │
│   • Database never exposed to internet or web tier                          │
│   • Security group chaining provides defense in depth                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Network ACLs (NACLs)

Network ACLs provide an additional layer of security at the subnet level.

### NACL Characteristics

| Feature | Description |
|---------|-------------|
| **Level** | Subnet level |
| **State** | Stateless - return traffic must be explicitly allowed |
| **Default** | Allows all inbound and outbound |
| **Rules** | Allow AND Deny rules |
| **Evaluation** | Rules evaluated in order (lowest number first) |
| **Scope** | VPC-specific, one per subnet |

### Stateless Behavior Explained

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATELESS NETWORK ACL                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Network ACL Rules:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Inbound:                                                             │   │
│   │   100  Allow  TCP  443  0.0.0.0/0                                   │   │
│   │   *    Deny   All  All  0.0.0.0/0                                   │   │
│   │                                                                      │   │
│   │ Outbound:                                                            │   │
│   │   100  Allow  TCP  1024-65535  0.0.0.0/0  ◄── MUST ADD THIS!        │   │
│   │   *    Deny   All  All  0.0.0.0/0                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Client (1.2.3.4)                           EC2 Instance                   │
│   ┌───────────────┐                         ┌───────────────┐               │
│   │               │ ═══ HTTPS Request ════► │               │               │
│   │               │   src: 1.2.3.4:54321    │               │               │
│   │   Browser     │   dst: 10.0.1.5:443     │   Web Server  │               │
│   │               │                          │               │               │
│   │               │ ◄══ HTTPS Response ════ │               │               │
│   │               │   src: 10.0.1.5:443     │               │               │
│   │               │   dst: 1.2.3.4:54321    │               │               │
│   └───────────────┘                         └───────────────┘               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   INBOUND REQUEST (port 443):                                       │   │
│   │   ✓ Allowed by inbound rule 100                                     │   │
│   │                                                                      │   │
│   │   OUTBOUND RESPONSE (ephemeral port 54321):                         │   │
│   │   ⚠️  Must be explicitly allowed!                                   │   │
│   │   ✓ Allowed by outbound rule 100 (1024-65535)                       │   │
│   │                                                                      │   │
│   │   Without outbound rule for ephemeral ports = CONNECTION FAILS      │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Ephemeral Port Ranges

| Operating System | Ephemeral Port Range |
|------------------|---------------------|
| Linux | 32768-65535 |
| Windows | 49152-65535 |
| NAT Gateway | 1024-65535 |
| ELB | 1024-65535 |

**Best Practice:** Allow 1024-65535 for outbound to cover all cases.

### NACL Rule Evaluation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NACL RULE EVALUATION ORDER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Inbound NACL Rules:                                                       │
│   ┌────────┬────────┬──────────┬────────┬─────────────────────────────┐    │
│   │ Rule # │ Type   │ Protocol │ Port   │ Source        │ Allow/Deny │    │
│   ├────────┼────────┼──────────┼────────┼───────────────┼────────────┤    │
│   │ 100    │ HTTP   │ TCP      │ 80     │ 0.0.0.0/0     │ ALLOW      │    │
│   │ 110    │ HTTPS  │ TCP      │ 443    │ 0.0.0.0/0     │ ALLOW      │    │
│   │ 120    │ SSH    │ TCP      │ 22     │ 10.0.0.0/8    │ ALLOW      │    │
│   │ 130    │ Custom │ TCP      │ 22     │ 192.168.1.100 │ DENY       │    │
│   │ *      │ ALL    │ ALL      │ ALL    │ 0.0.0.0/0     │ DENY       │    │
│   └────────┴────────┴──────────┴────────┴───────────────┴────────────┘    │
│                                                                              │
│   Evaluation Process for SSH from 192.168.1.100:                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Rule 100 (HTTP/80): Does not match SSH/22 → CONTINUE              │   │
│   │        │                                                             │   │
│   │        ▼                                                             │   │
│   │   Rule 110 (HTTPS/443): Does not match SSH/22 → CONTINUE            │   │
│   │        │                                                             │   │
│   │        ▼                                                             │   │
│   │   Rule 120 (SSH from 10.0.0.0/8):                                   │   │
│   │        192.168.1.100 NOT in 10.0.0.0/8 → CONTINUE                   │   │
│   │        │                                                             │   │
│   │        ▼                                                             │   │
│   │   Rule 130 (SSH from 192.168.1.100): MATCH! → DENY                  │   │
│   │        │                                                             │   │
│   │        ╳ ═══ TRAFFIC DENIED ═══                                     │   │
│   │                                                                      │   │
│   │   ⚠️  Rule 130 evaluated BEFORE implicit deny (*)                   │   │
│   │      Even though 192.168.1.100 could match 10.0.0.0/8              │   │
│   │      with a /8 prefix, rule 120 doesn't match this specific IP     │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ⚠️  ORDER MATTERS! Lower rule numbers are evaluated first.               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Security Groups vs NACLs Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY GROUPS vs NACLs                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────┬────────────────────────────────────────────┐   │
│   │      Feature           │  Security Group   │   Network ACL          │   │
│   ├────────────────────────┼───────────────────┼────────────────────────┤   │
│   │ Operates at            │ Instance (ENI)    │ Subnet                 │   │
│   │ State                  │ Stateful          │ Stateless              │   │
│   │ Rules                  │ Allow only        │ Allow AND Deny         │   │
│   │ Rule processing        │ All rules         │ In order (number)      │   │
│   │ Default inbound        │ Deny all          │ Allow all (default)    │   │
│   │ Default outbound       │ Allow all         │ Allow all (default)    │   │
│   │ Return traffic         │ Automatic         │ Must be allowed        │   │
│   │ Association            │ Multiple per ENI  │ One per subnet         │   │
│   │ Changes apply          │ Immediately       │ Immediately            │   │
│   │ Can reference SG       │ Yes               │ No                     │   │
│   └────────────────────────┴───────────────────┴────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRAFFIC FLOW THROUGH BOTH LAYERS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INBOUND TRAFFIC:                                                          │
│                                                                              │
│   Internet ──► NACL Inbound ──► Security Group Inbound ──► Instance        │
│                    │                    │                                    │
│               (Evaluate in         (Evaluate all                            │
│                order, stop          rules, any                              │
│                on match)            match = allow)                          │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   OUTBOUND TRAFFIC:                                                         │
│                                                                              │
│   Instance ──► Security Group Outbound ──► NACL Outbound ──► Internet      │
│                    │                           │                             │
│               (Evaluate all              (Evaluate in                       │
│                rules, any                 order, stop                       │
│                match = allow)             on match)                         │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   Both must ALLOW for traffic to flow!                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## When to Use Each

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHEN TO USE SG vs NACL                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   USE SECURITY GROUPS:                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ ✓ Primary network security control                                  │   │
│   │ ✓ Instance-specific rules                                           │   │
│   │ ✓ When you need to reference other security groups                  │   │
│   │ ✓ When you want stateful behavior (simpler rule management)         │   │
│   │ ✓ Application-level security boundaries                             │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   USE NETWORK ACLs:                                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ ✓ Block specific IP addresses or CIDR ranges                        │   │
│   │ ✓ Explicit deny rules (e.g., block known malicious IPs)             │   │
│   │ ✓ Subnet-wide security policies                                     │   │
│   │ ✓ Additional defense layer (defense in depth)                       │   │
│   │ ✓ Quick emergency blocking during security incidents                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   COMMON PATTERN:                                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   NACL: Coarse-grained filtering (block bad actors)                 │   │
│   │      │                                                               │   │
│   │      ▼                                                               │   │
│   │   Security Group: Fine-grained access control (allow good traffic)  │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Best Practices

### Security Group Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY GROUP BEST PRACTICES                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Principle of Least Privilege                                           │
│      ┌──────────────────────────────────────────────────────────────────┐  │
│      │ ✗ Bad:  Inbound: All traffic from 0.0.0.0/0                     │  │
│      │ ✓ Good: Inbound: TCP/443 from 0.0.0.0/0 (only HTTPS)            │  │
│      └──────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   2. Use Security Group References                                          │
│      ┌──────────────────────────────────────────────────────────────────┐  │
│      │ ✗ Bad:  Allow TCP/3306 from 10.0.1.0/24                         │  │
│      │ ✓ Good: Allow TCP/3306 from sg-app-servers                      │  │
│      └──────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   3. Add Descriptions to Rules                                              │
│      ┌──────────────────────────────────────────────────────────────────┐  │
│      │ Description: "Allow HTTPS from corporate network for admin"     │  │
│      └──────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   4. Regular Audit                                                          │
│      ┌──────────────────────────────────────────────────────────────────┐  │
│      │ • Review unused security groups                                  │  │
│      │ • Check for overly permissive rules (0.0.0.0/0)                 │  │
│      │ • Use AWS Config rules for compliance                            │  │
│      └──────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   5. Separate Security Groups by Function                                   │
│      ┌──────────────────────────────────────────────────────────────────┐  │
│      │ • sg-bastion - SSH access                                        │  │
│      │ • sg-web - HTTP/HTTPS                                            │  │
│      │ • sg-db - Database ports                                         │  │
│      │ • sg-monitoring - Monitoring tools access                        │  │
│      └──────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Troubleshooting Network Security

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY TROUBLESHOOTING FLOWCHART                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   "Connection refused" or "Connection timeout"                              │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────────────────┐                                      │
│   │ Check Security Group inbound     │                                      │
│   │ rules for destination instance   │                                      │
│   └──────────────┬───────────────────┘                                      │
│                  │                                                           │
│        ┌─────────┴─────────┐                                                │
│   Rule exists?             │                                                │
│        │                   │                                                │
│   No   │              Yes  │                                                │
│        ▼                   ▼                                                │
│   Add inbound        ┌───────────────────────────┐                          │
│   rule               │ Check NACL inbound rules  │                          │
│                      │ for destination subnet    │                          │
│                      └─────────────┬─────────────┘                          │
│                                    │                                         │
│                          ┌─────────┴─────────┐                              │
│                     Allowed?                  │                              │
│                          │                    │                              │
│                     No   │               Yes  │                              │
│                          ▼                    ▼                              │
│                     Add allow           ┌───────────────────────────┐       │
│                     rule (before        │ Check NACL outbound rules │       │
│                     deny rule)          │ for ephemeral ports       │       │
│                                         └─────────────┬─────────────┘       │
│                                                       │                      │
│                                             ┌─────────┴─────────┐           │
│                                        Allowed?                  │           │
│                                             │                    │           │
│                                        No   │               Yes  │           │
│                                             ▼                    ▼           │
│                                        Add rule for        Check route      │
│                                        1024-65535          table and IGW    │
│                                                                              │
│   Pro Tip: Use VPC Flow Logs to see what traffic is being rejected          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## AWS CLI Commands

```bash
# Security Groups
# ---------------

# Create security group
aws ec2 create-security-group \
    --group-name WebServerSG \
    --description "Security group for web servers" \
    --vpc-id vpc-12345678

# Add inbound rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# Add rule referencing another SG
aws ec2 authorize-security-group-ingress \
    --group-id sg-db-12345678 \
    --protocol tcp \
    --port 3306 \
    --source-group sg-app-12345678

# Network ACLs
# ------------

# Create NACL
aws ec2 create-network-acl \
    --vpc-id vpc-12345678

# Add inbound rule
aws ec2 create-network-acl-entry \
    --network-acl-id acl-12345678 \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=443,To=443 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --ingress

# Add outbound rule for ephemeral ports
aws ec2 create-network-acl-entry \
    --network-acl-id acl-12345678 \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=1024,To=65535 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --egress
```

## Key Takeaways

1. **Security Groups are stateful** - Return traffic automatically allowed
2. **NACLs are stateless** - Must allow both directions explicitly
3. **Use SGs as primary control** - NACLs for additional defense
4. **Reference security groups** - More flexible than CIDR-based rules
5. **Don't forget ephemeral ports** - Essential for NACL outbound rules
6. **Rule order matters for NACLs** - Lower numbers evaluated first

---

**Next:** [06-vpc-peering.md](06-vpc-peering.md) - Connecting VPCs together
