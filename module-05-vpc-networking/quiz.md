# VPC and Networking Quiz

## Module 5 Assessment - 30 Questions

**Time Estimate:** 45 minutes
**Passing Score:** 80% (24/30)

---

## Section 1: VPC Fundamentals and CIDR (Questions 1-6)

### Question 1
**What is the maximum size CIDR block you can assign to a VPC?**

A) /8
B) /12
C) /16
D) /20

<details>
<summary>Click to reveal answer</summary>

**Answer: C) /16**

Explanation: AWS VPCs support CIDR blocks from /16 (65,536 IP addresses) to /28 (16 IP addresses). The /16 block provides the maximum number of IP addresses for a single VPC.

```
VPC CIDR Range Limits:
┌──────────────────────────────────────────────────────┐
│  Minimum: /28 = 16 IPs (11 usable)                   │
│  Maximum: /16 = 65,536 IPs (65,531 usable)           │
└──────────────────────────────────────────────────────┘
```
</details>

---

### Question 2
**How many IP addresses does AWS reserve in each subnet?**

A) 3
B) 4
C) 5
D) 6

<details>
<summary>Click to reveal answer</summary>

**Answer: C) 5**

Explanation: AWS reserves 5 IP addresses in each subnet:

```
Example: 10.0.1.0/24 Subnet
┌─────────────────────────────────────────────────────┐
│  10.0.1.0   - Network address                       │
│  10.0.1.1   - VPC Router                            │
│  10.0.1.2   - DNS Server                            │
│  10.0.1.3   - Reserved for future use               │
│  10.0.1.255 - Broadcast address                     │
├─────────────────────────────────────────────────────┤
│  Usable: 10.0.1.4 to 10.0.1.254 = 251 addresses     │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 3
**You need to allocate a subnet that can support 500 EC2 instances. What is the minimum CIDR block size you should use?**

A) /24 (256 IPs)
B) /23 (512 IPs)
C) /22 (1024 IPs)
D) /21 (2048 IPs)

<details>
<summary>Click to reveal answer</summary>

**Answer: B) /23 (512 IPs)**

Explanation: Calculation:
```
Required: 500 instances
Reserved: 5 AWS IPs
Total needed: 505 IPs

/24 = 256 total - 5 reserved = 251 usable  (Too small)
/23 = 512 total - 5 reserved = 507 usable  (Sufficient)

Answer: /23 provides 507 usable IPs
```
</details>

---

### Question 4
**Which of the following is the default CIDR block for the AWS default VPC?**

A) 10.0.0.0/16
B) 192.168.0.0/16
C) 172.31.0.0/16
D) 172.16.0.0/16

<details>
<summary>Click to reveal answer</summary>

**Answer: C) 172.31.0.0/16**

Explanation: Every AWS account comes with a default VPC in each region with the CIDR block 172.31.0.0/16. This is in the RFC 1918 private range 172.16.0.0/12.

```
Default VPC Structure:
┌─────────────────────────────────────────────────────┐
│  VPC: 172.31.0.0/16                                 │
│  ├── Subnet AZ-a: 172.31.0.0/20                     │
│  ├── Subnet AZ-b: 172.31.16.0/20                    │
│  └── Subnet AZ-c: 172.31.32.0/20                    │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 5
**Calculate the IP address range for the CIDR block 192.168.10.0/25.**

A) 192.168.10.0 - 192.168.10.127
B) 192.168.10.0 - 192.168.10.255
C) 192.168.10.0 - 192.168.10.63
D) 192.168.10.0 - 192.168.11.255

<details>
<summary>Click to reveal answer</summary>

**Answer: A) 192.168.10.0 - 192.168.10.127**

Explanation:
```
CIDR Calculation for /25:
┌─────────────────────────────────────────────────────┐
│  /25 means 25 network bits, 7 host bits             │
│  2^7 = 128 total addresses                          │
│                                                      │
│  Network: 192.168.10.0                              │
│  First IP: 192.168.10.0                             │
│  Last IP: 192.168.10.0 + 127 = 192.168.10.127       │
│  Broadcast: 192.168.10.127                          │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 6
**Which RFC 1918 private IP ranges are valid for VPC CIDR blocks? (Select TWO)**

A) 10.0.0.0/8
B) 169.254.0.0/16
C) 172.16.0.0/12
D) 224.0.0.0/4

<details>
<summary>Click to reveal answer</summary>

**Answer: A) 10.0.0.0/8 and C) 172.16.0.0/12**

Explanation: RFC 1918 defines three private IP ranges:
```
RFC 1918 Private Ranges:
┌─────────────────────────────────────────────────────┐
│  10.0.0.0/8      - Class A (16,777,216 IPs)         │
│  172.16.0.0/12   - Class B (1,048,576 IPs)          │
│  192.168.0.0/16  - Class C (65,536 IPs)             │
├─────────────────────────────────────────────────────┤
│  169.254.0.0/16 = Link-local (NOT for VPCs)         │
│  224.0.0.0/4 = Multicast (NOT for VPCs)             │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Section 2: Subnets and Route Tables (Questions 7-11)

### Question 7
**What makes a subnet "public" in AWS?**

A) The subnet has a public IP range
B) The subnet has a route to an Internet Gateway
C) The subnet is in the first Availability Zone
D) The subnet has public DNS enabled

<details>
<summary>Click to reveal answer</summary>

**Answer: B) The subnet has a route to an Internet Gateway**

Explanation: A public subnet is defined by its route table configuration, not by any inherent property. If the route table has a route to an Internet Gateway (typically 0.0.0.0/0 -> igw-xxx), the subnet is public.

```
Public vs Private Subnet Determination:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  PUBLIC SUBNET Route Table:                         │
│  ┌─────────────────────────────────────────┐        │
│  │ 10.0.0.0/16    -> local                 │        │
│  │ 0.0.0.0/0      -> igw-xxxxxxxx  <-- KEY │        │
│  └─────────────────────────────────────────┘        │
│                                                      │
│  PRIVATE SUBNET Route Table:                        │
│  ┌─────────────────────────────────────────┐        │
│  │ 10.0.0.0/16    -> local                 │        │
│  │ 0.0.0.0/0      -> nat-xxxxxxxx          │        │
│  └─────────────────────────────────────────┘        │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 8
**A subnet can span multiple Availability Zones.**

A) True
B) False

<details>
<summary>Click to reveal answer</summary>

**Answer: B) False**

Explanation: A subnet is ALWAYS confined to a single Availability Zone. This is a fundamental AWS networking principle.

```
Subnet-AZ Relationship:
┌─────────────────────────────────────────────────────┐
│                    VPC (Region-wide)                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │    AZ-1a     │  │    AZ-1b     │  │   AZ-1c   │ │
│  │  ┌────────┐  │  │  ┌────────┐  │  │ ┌──────┐  │ │
│  │  │Subnet-A│  │  │  │Subnet-B│  │  │ │Sub-C │  │ │
│  │  └────────┘  │  │  └────────┘  │  │ └──────┘  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  Each subnet exists in exactly ONE AZ               │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 9
**How many route tables can be associated with a subnet?**

A) Unlimited
B) One
C) One per Availability Zone
D) Five

<details>
<summary>Click to reveal answer</summary>

**Answer: B) One**

Explanation: Each subnet can be associated with exactly ONE route table at a time. However, a single route table can be associated with multiple subnets.

```
Route Table Association Rules:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Route Table                                        │
│  ┌─────────────┐                                    │
│  │ RT-Public   │─────┬─────────────────────┐        │
│  └─────────────┘     │                     │        │
│                      ▼                     ▼        │
│              ┌─────────────┐       ┌─────────────┐  │
│              │  Subnet-A   │       │  Subnet-B   │  │
│              └─────────────┘       └─────────────┘  │
│                                                      │
│  One RT -> Many Subnets: YES                        │
│  One Subnet -> Many RTs: NO                         │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 10
**What happens if you delete a custom route table that has associated subnets?**

A) The subnets are deleted
B) The subnets automatically associate with the main route table
C) You cannot delete it until subnets are disassociated
D) The subnets become unreachable

<details>
<summary>Click to reveal answer</summary>

**Answer: C) You cannot delete it until subnets are disassociated**

Explanation: AWS prevents deletion of route tables that have subnet associations. You must first disassociate all subnets before deleting the route table. Subnets without explicit associations use the main route table.
</details>

---

### Question 11
**Which route has the HIGHEST priority in a route table?**

A) The route with the lowest metric
B) The most specific route (longest prefix match)
C) The route added first
D) The route to the Internet Gateway

<details>
<summary>Click to reveal answer</summary>

**Answer: B) The most specific route (longest prefix match)**

Explanation: AWS uses longest prefix match for routing decisions. The most specific route wins.

```
Longest Prefix Match Example:
┌─────────────────────────────────────────────────────┐
│  Route Table:                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │ 10.0.0.0/16      -> local                   │    │
│  │ 10.0.1.0/24      -> nat-gateway             │    │
│  │ 10.0.1.128/25    -> vpn-gateway             │    │
│  │ 0.0.0.0/0        -> igw                     │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  Traffic to 10.0.1.150:                             │
│  ├── Matches 10.0.0.0/16   (/16 = 16 bits)         │
│  ├── Matches 10.0.1.0/24   (/24 = 24 bits)         │
│  └── Matches 10.0.1.128/25 (/25 = 25 bits) WINNER  │
│                                                      │
│  Route: 10.0.1.128/25 -> vpn-gateway               │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Section 3: Internet Gateway and NAT (Questions 12-16)

### Question 12
**How many Internet Gateways can you attach to a VPC?**

A) Unlimited
B) One per Availability Zone
C) One per VPC
D) One per subnet

<details>
<summary>Click to reveal answer</summary>

**Answer: C) One per VPC**

Explanation: A VPC can have only ONE Internet Gateway attached. The IGW is horizontally scaled, redundant, and highly available by design - no need for multiple IGWs.

```
Internet Gateway Design:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  ┌───────────────────────────────────────────┐      │
│  │                    VPC                     │      │
│  │                                            │      │
│  │  ┌────────┐  ┌────────┐  ┌────────┐       │      │
│  │  │ AZ-1a  │  │ AZ-1b  │  │ AZ-1c  │       │      │
│  │  └───┬────┘  └───┬────┘  └───┬────┘       │      │
│  │      │           │           │             │      │
│  │      └─────────┬─┴───────────┘             │      │
│  │                │                           │      │
│  └────────────────┼───────────────────────────┘      │
│                   │                                  │
│         ┌─────────▼─────────┐                       │
│         │  Internet Gateway │  <- ONE per VPC       │
│         │   (Highly Available)                      │
│         └─────────┬─────────┘                       │
│                   │                                  │
│                   ▼                                  │
│              INTERNET                               │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 13
**What is the key difference between NAT Gateway and NAT Instance?**

A) NAT Gateway is free, NAT Instance is paid
B) NAT Gateway is managed by AWS, NAT Instance is self-managed
C) NAT Instance supports more bandwidth than NAT Gateway
D) NAT Gateway can be used as a bastion host

<details>
<summary>Click to reveal answer</summary>

**Answer: B) NAT Gateway is managed by AWS, NAT Instance is self-managed**

Explanation: NAT Gateway is a fully managed service, while NAT Instance is an EC2 instance you manage yourself.

```
NAT Gateway vs NAT Instance:
┌────────────────────┬──────────────────┬──────────────────┐
│ Feature            │ NAT Gateway      │ NAT Instance     │
├────────────────────┼──────────────────┼──────────────────┤
│ Management         │ AWS Managed      │ You Manage       │
│ Availability       │ Highly Available │ Use scripts/ASG  │
│ Bandwidth          │ Up to 100 Gbps   │ Instance-based   │
│ Maintenance        │ None required    │ Patching needed  │
│ Security Groups    │ Cannot associate │ Can associate    │
│ Bastion Host       │ No               │ Yes              │
│ Port Forwarding    │ No               │ Yes              │
│ Cost               │ Hourly + Data    │ Instance + Data  │
└────────────────────┴──────────────────┴──────────────────┘
```
</details>

---

### Question 14
**An EC2 instance in a private subnet needs to download software updates from the internet. What is the RECOMMENDED solution?**

A) Move the instance to a public subnet
B) Use a NAT Gateway in a public subnet
C) Create an Internet Gateway
D) Use VPC peering

<details>
<summary>Click to reveal answer</summary>

**Answer: B) Use a NAT Gateway in a public subnet**

Explanation: NAT Gateway allows instances in private subnets to access the internet for outbound traffic while remaining unreachable from the internet.

```
NAT Gateway Architecture:
┌─────────────────────────────────────────────────────┐
│                         VPC                          │
│  ┌─────────────────────┐  ┌─────────────────────┐   │
│  │   Public Subnet     │  │   Private Subnet    │   │
│  │                     │  │                     │   │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │   │
│  │  │  NAT Gateway  │  │  │  │      EC2      │  │   │
│  │  │   (nat-xxx)   │  │  │  │   Instance    │  │   │
│  │  └───────┬───────┘  │  │  └───────┬───────┘  │   │
│  │          │          │  │          │          │   │
│  └──────────┼──────────┘  └──────────┼──────────┘   │
│             │                        │              │
│             │     Route: 0.0.0.0/0 -> nat-xxx       │
│             │◄───────────────────────┘              │
│             │                                       │
│      ┌──────▼──────┐                               │
│      │     IGW     │                               │
│      └──────┬──────┘                               │
└─────────────┼───────────────────────────────────────┘
              ▼
          INTERNET
```
</details>

---

### Question 15
**Which component performs Network Address Translation for IPv6 traffic?**

A) NAT Gateway
B) NAT Instance
C) Egress-only Internet Gateway
D) Internet Gateway

<details>
<summary>Click to reveal answer</summary>

**Answer: C) Egress-only Internet Gateway**

Explanation: NAT Gateway and NAT Instance work only with IPv4. For IPv6, AWS provides Egress-only Internet Gateway, which allows outbound IPv6 traffic while blocking inbound connections.

```
IPv4 vs IPv6 Outbound Access:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  IPv4 Outbound (Private Subnet):                    │
│  EC2 ──► NAT Gateway ──► IGW ──► Internet           │
│                                                      │
│  IPv6 Outbound (Private Subnet):                    │
│  EC2 ──► Egress-only IGW ──► Internet               │
│                                                      │
│  Note: IPv6 addresses are globally unique,          │
│        so NAT is not needed for address translation │
│        Only for blocking inbound connections        │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 16
**A NAT Gateway in AZ-1a fails. What happens to instances in AZ-1b using this NAT Gateway?**

A) They automatically failover to another NAT Gateway
B) They lose internet connectivity
C) They continue working because NAT Gateway is multi-AZ
D) AWS automatically creates a new NAT Gateway

<details>
<summary>Click to reveal answer</summary>

**Answer: B) They lose internet connectivity**

Explanation: NAT Gateway is AZ-specific and NOT automatically multi-AZ. For high availability, you must create a NAT Gateway in each AZ.

```
High Availability NAT Design:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  POOR DESIGN (Single NAT Gateway):                  │
│  ┌──────────────────────────────────────────────┐   │
│  │         NAT-GW in AZ-1a (Single Point)       │   │
│  │              ▲           ▲                    │   │
│  │              │           │                    │   │
│  │  ┌─────────────┐    ┌─────────────┐          │   │
│  │  │  AZ-1a      │    │  AZ-1b      │          │   │
│  │  │  Private    │    │  Private    │          │   │
│  │  └─────────────┘    └─────────────┘          │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  GOOD DESIGN (NAT Gateway per AZ):                  │
│  ┌──────────────────────────────────────────────┐   │
│  │  ┌─────────────────┐  ┌─────────────────┐    │   │
│  │  │     AZ-1a       │  │     AZ-1b       │    │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │    │   │
│  │  │  │  NAT-GW   │  │  │  │  NAT-GW   │  │    │   │
│  │  │  └─────┬─────┘  │  │  └─────┬─────┘  │    │   │
│  │  │        │        │  │        │        │    │   │
│  │  │  ┌─────▼─────┐  │  │  ┌─────▼─────┐  │    │   │
│  │  │  │  Private  │  │  │  │  Private  │  │    │   │
│  │  │  └───────────┘  │  │  └───────────┘  │    │   │
│  │  └─────────────────┘  └─────────────────┘    │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Section 4: Security Groups vs NACLs (Questions 17-21)

### Question 17
**Which statement correctly describes the difference between Security Groups and Network ACLs?**

A) Security Groups are stateless, NACLs are stateful
B) Security Groups operate at subnet level, NACLs operate at instance level
C) Security Groups are stateful, NACLs are stateless
D) Security Groups can have deny rules, NACLs cannot

<details>
<summary>Click to reveal answer</summary>

**Answer: C) Security Groups are stateful, NACLs are stateless**

Explanation: This is a critical distinction for the exam.

```
Security Groups vs NACLs:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  SECURITY GROUPS (Stateful):                        │
│  ┌─────────────────────────────────────────────┐    │
│  │ - Instance (ENI) level                      │    │
│  │ - ALLOW rules only                          │    │
│  │ - Return traffic automatically allowed      │    │
│  │ - All rules evaluated                       │    │
│  │ - Applied to instances you specify          │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  NETWORK ACLs (Stateless):                          │
│  ┌─────────────────────────────────────────────┐    │
│  │ - Subnet level                              │    │
│  │ - ALLOW and DENY rules                      │    │
│  │ - Must explicitly allow return traffic      │    │
│  │ - Rules evaluated in order (lowest first)   │    │
│  │ - Applied to all traffic in subnet          │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 18
**In a Network ACL, if you have the following rules, what happens to incoming HTTP traffic?**

```
Rule 100: Allow HTTP (80) from 0.0.0.0/0
Rule 200: Deny all traffic from 0.0.0.0/0
Rule *: Deny all traffic
```

A) Denied by Rule 200
B) Denied by Rule *
C) Allowed by Rule 100
D) Depends on Security Group

<details>
<summary>Click to reveal answer</summary>

**Answer: C) Allowed by Rule 100**

Explanation: NACL rules are evaluated in order from lowest to highest rule number. Rule 100 matches first and allows the traffic; subsequent rules are not evaluated.

```
NACL Rule Evaluation:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Incoming HTTP Traffic (Port 80):                   │
│                                                      │
│  Rule 100: Allow HTTP? ──► YES ──► ALLOW (STOP)     │
│                │                                    │
│                └── If NO, continue to Rule 200      │
│                                                      │
│  Rule 200: Never reached for HTTP                   │
│  Rule *: Never reached                              │
│                                                      │
│  Key: First matching rule wins!                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 19
**You have a Security Group allowing inbound SSH (port 22). Do you need an outbound rule for SSH responses?**

A) Yes, you must add an outbound rule for port 22
B) No, Security Groups are stateful
C) Yes, you must add an outbound rule for ephemeral ports
D) No, outbound is allowed by default

<details>
<summary>Click to reveal answer</summary>

**Answer: B) No, Security Groups are stateful**

Explanation: Security Groups are stateful - return traffic is automatically allowed regardless of outbound rules. However, answer D is partially true as well (default SG allows all outbound), but B is the more accurate reason.

```
Stateful Security Group:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Security Group: Inbound Allow SSH (22)             │
│                                                      │
│  Client                        EC2 Instance         │
│  ┌─────────┐                   ┌─────────┐          │
│  │         │ ═══ SSH Request ══►         │          │
│  │         │    (Port 22)      │         │          │
│  │         │                   │         │          │
│  │         │ ◄═ SSH Response ══│         │          │
│  │         │    (Auto-allowed) │         │          │
│  └─────────┘                   └─────────┘          │
│                                                      │
│  STATEFUL = Response traffic automatically allowed  │
│             No outbound rule needed!                │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 20
**What is the default behavior of a newly created Network ACL?**

A) Allows all inbound and outbound traffic
B) Denies all inbound and outbound traffic
C) Allows all inbound, denies all outbound
D) Denies all inbound, allows all outbound

<details>
<summary>Click to reveal answer</summary>

**Answer: B) Denies all inbound and outbound traffic**

Explanation: A custom (non-default) Network ACL denies all traffic by default. You must explicitly add allow rules. Note: The DEFAULT Network ACL that comes with a VPC allows all traffic.

```
NACL Default Behavior:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  DEFAULT Network ACL (auto-created with VPC):       │
│  ┌─────────────────────────────────────────────┐    │
│  │ Rule 100: Allow ALL inbound                 │    │
│  │ Rule 100: Allow ALL outbound                │    │
│  │ Rule *: Deny ALL (fallback)                 │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  CUSTOM Network ACL (you create):                   │
│  ┌─────────────────────────────────────────────┐    │
│  │ Rule *: Deny ALL inbound (only rule!)       │    │
│  │ Rule *: Deny ALL outbound (only rule!)      │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  Must add explicit ALLOW rules to custom NACLs      │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 21
**How many Security Groups can be associated with a single EC2 instance?**

A) One
B) Up to 5 by default
C) Up to 16
D) Unlimited

<details>
<summary>Click to reveal answer</summary>

**Answer: B) Up to 5 by default**

Explanation: By default, you can associate up to 5 security groups per network interface. This limit can be increased by contacting AWS support. Rules from all associated SGs are aggregated.

```
Multiple Security Groups:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  EC2 Instance                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │                                                │  │
│  │  Associated Security Groups:                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │  │
│  │  │   SG-1   │ │   SG-2   │ │   SG-3   │      │  │
│  │  │ SSH:22   │ │ HTTP:80  │ │ HTTPS:443│      │  │
│  │  └──────────┘ └──────────┘ └──────────┘      │  │
│  │                                                │  │
│  │  Effective Rules (aggregated):                │  │
│  │  - Allow SSH (22)                             │  │
│  │  - Allow HTTP (80)                            │  │
│  │  - Allow HTTPS (443)                          │  │
│  │                                                │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  Max: 5 SGs per ENI (default, can be increased)     │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Section 5: VPC Peering and Transit Gateway (Questions 22-25)

### Question 22
**VPC A is peered with VPC B, and VPC B is peered with VPC C. Can VPC A communicate with VPC C through VPC B?**

A) Yes, this is called transitive peering
B) No, VPC peering is not transitive
C) Yes, if you configure route tables correctly
D) Only if all VPCs are in the same region

<details>
<summary>Click to reveal answer</summary>

**Answer: B) No, VPC peering is not transitive**

Explanation: VPC peering connections are NOT transitive. You cannot route traffic from VPC A to VPC C through VPC B. You must create a direct peering connection between A and C.

```
Transitive Peering - NOT Supported:
┌─────────────────────────────────────────────────────┐
│                                                      │
│                    VPC B                            │
│                  (172.16.0.0/16)                    │
│                       │                             │
│          ┌───────────┴───────────┐                  │
│          │                       │                  │
│       pcx-1                   pcx-2                 │
│          │                       │                  │
│    ┌─────▼─────┐           ┌─────▼─────┐           │
│    │   VPC A   │           │   VPC C   │           │
│    │(10.0.0.0) │           │(192.168.0)│           │
│    └───────────┘           └───────────┘           │
│                                                      │
│    VPC A <--> VPC B: OK                             │
│    VPC B <--> VPC C: OK                             │
│    VPC A <--> VPC C: NOT POSSIBLE via B            │
│                                                      │
│    Solution: Create direct pcx-3 between A and C   │
│              OR use Transit Gateway                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 23
**What is the primary benefit of using Transit Gateway over VPC Peering for connecting multiple VPCs?**

A) Transit Gateway is free while VPC Peering has costs
B) Transit Gateway supports transitive routing (hub-and-spoke)
C) Transit Gateway provides higher bandwidth
D) Transit Gateway works across regions while VPC Peering does not

<details>
<summary>Click to reveal answer</summary>

**Answer: B) Transit Gateway supports transitive routing (hub-and-spoke)**

Explanation: Transit Gateway acts as a central hub that allows transitive routing between all connected VPCs and on-premises networks. This eliminates the need for a full mesh of peering connections.

```
VPC Peering vs Transit Gateway:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  VPC Peering (Full Mesh - N*(N-1)/2 connections):   │
│                                                      │
│       VPC-A ────── VPC-B                            │
│         │ \      / │                                │
│         │  \    /  │                                │
│         │   \  /   │                                │
│         │    \/    │                                │
│         │    /\    │                                │
│         │   /  \   │                                │
│         │  /    \  │                                │
│         │ /      \ │                                │
│       VPC-C ────── VPC-D                            │
│                                                      │
│       4 VPCs = 6 peering connections                │
│       10 VPCs = 45 peering connections!             │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Transit Gateway (Hub-and-Spoke - N connections):   │
│                                                      │
│       VPC-A    VPC-B                                │
│          \      /                                   │
│           \    /                                    │
│       ┌────────────┐                                │
│       │  Transit   │                                │
│       │  Gateway   │                                │
│       └────────────┘                                │
│           /    \                                    │
│          /      \                                   │
│       VPC-C    VPC-D                                │
│                                                      │
│       4 VPCs = 4 TGW attachments                    │
│       10 VPCs = 10 TGW attachments                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 24
**Which statement about VPC Peering is TRUE?**

A) VPC peering can only be done within the same AWS account
B) VPC peering requires non-overlapping CIDR blocks
C) VPC peering automatically updates route tables
D) VPC peering traffic goes over the public internet

<details>
<summary>Click to reveal answer</summary>

**Answer: B) VPC peering requires non-overlapping CIDR blocks**

Explanation: VPC peering requires that the CIDR blocks of the two VPCs do NOT overlap. Traffic stays on AWS backbone (not public internet), can be cross-account, and route tables must be manually updated.

```
VPC Peering Requirements:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  VALID PEERING:                                     │
│  ┌──────────────┐      ┌──────────────┐            │
│  │ VPC A        │      │ VPC B        │            │
│  │ 10.0.0.0/16  │◄────►│ 172.16.0.0/16│            │
│  └──────────────┘      └──────────────┘            │
│  Different CIDR blocks - OK                         │
│                                                      │
│  INVALID PEERING:                                   │
│  ┌──────────────┐      ┌──────────────┐            │
│  │ VPC A        │      │ VPC B        │            │
│  │ 10.0.0.0/16  │  X   │ 10.0.0.0/16  │            │
│  └──────────────┘      └──────────────┘            │
│  Same CIDR blocks - NOT ALLOWED                     │
│                                                      │
│  Also Invalid:                                      │
│  VPC A: 10.0.0.0/16                                 │
│  VPC B: 10.0.1.0/24 (overlaps with A!)             │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 25
**You have 100 VPCs that need to communicate with each other. What is the most scalable solution?**

A) Create 4,950 VPC peering connections
B) Use a single Transit Gateway
C) Use NAT Gateways in each VPC
D) Use VPN connections between VPCs

<details>
<summary>Click to reveal answer</summary>

**Answer: B) Use a single Transit Gateway**

Explanation: Transit Gateway can support up to 5,000 VPC attachments per gateway. Using VPC peering for 100 VPCs would require 100*99/2 = 4,950 peering connections, which is unmanageable.

```
Scaling VPC Connectivity:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  100 VPCs with VPC Peering:                         │
│  Formula: N*(N-1)/2 = 100*99/2 = 4,950 connections  │
│                                                      │
│  Management nightmare!                               │
│  - 4,950 peering connections                        │
│  - 4,950 route table updates per VPC               │
│  - Complex troubleshooting                          │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  100 VPCs with Transit Gateway:                     │
│                                                      │
│        VPC-1  VPC-2  VPC-3  ...  VPC-100           │
│           \    |    /            /                  │
│            \   |   /            /                   │
│             \  |  /            /                    │
│           ┌────────────────────┐                    │
│           │   Transit Gateway  │                    │
│           │   (Central Hub)    │                    │
│           └────────────────────┘                    │
│                                                      │
│  - 100 TGW attachments                              │
│  - Centralized route tables                         │
│  - Easy management and visibility                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Section 6: VPC Endpoints (Questions 26-28)

### Question 26
**What is the main difference between Gateway Endpoints and Interface Endpoints?**

A) Gateway Endpoints are free, Interface Endpoints have hourly charges
B) Gateway Endpoints work with all AWS services
C) Interface Endpoints are faster
D) Gateway Endpoints require DNS resolution

<details>
<summary>Click to reveal answer</summary>

**Answer: A) Gateway Endpoints are free, Interface Endpoints have hourly charges**

Explanation: Gateway Endpoints (S3 and DynamoDB only) are free and use route table entries. Interface Endpoints have hourly charges and create ENIs in your subnets.

```
Gateway vs Interface Endpoints:
┌────────────────────┬──────────────────┬──────────────────┐
│ Feature            │ Gateway Endpoint │ Interface        │
│                    │                  │ Endpoint         │
├────────────────────┼──────────────────┼──────────────────┤
│ Services           │ S3, DynamoDB     │ 100+ services    │
│ Cost               │ FREE             │ ~$0.01/hour      │
│ Implementation     │ Route table      │ ENI in subnet    │
│ Security           │ Endpoint policy  │ Security Groups  │
│ DNS                │ Uses AWS DNS     │ Private DNS      │
│ Access from        │ Same VPC only    │ On-prem via      │
│ on-prem            │                  │ VPN/DX           │
└────────────────────┴──────────────────┴──────────────────┘
```
</details>

---

### Question 27
**You want to access S3 from a private subnet without going through the internet. Which is the MOST cost-effective solution?**

A) NAT Gateway
B) Gateway Endpoint
C) Interface Endpoint
D) AWS PrivateLink

<details>
<summary>Click to reveal answer</summary>

**Answer: B) Gateway Endpoint**

Explanation: Gateway Endpoints for S3 are FREE. NAT Gateway has data processing and hourly charges. Interface Endpoints have hourly charges. Gateway Endpoints are the most cost-effective option for S3 access.

```
Cost Comparison for S3 Access:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Option 1: NAT Gateway                              │
│  ┌───────────────────────────────────────────────┐  │
│  │ Cost: $0.045/hour + $0.045/GB data processing │  │
│  │ Monthly: ~$32 + data costs                    │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  Option 2: Interface Endpoint                       │
│  ┌───────────────────────────────────────────────┐  │
│  │ Cost: ~$0.01/hour per AZ + $0.01/GB data     │  │
│  │ Monthly: ~$7/AZ + data costs                 │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  Option 3: Gateway Endpoint (WINNER)               │
│  ┌───────────────────────────────────────────────┐  │
│  │ Cost: FREE!                                   │  │
│  │ Monthly: $0                                   │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 28
**Which statement about VPC Endpoints is correct?**

A) Interface Endpoints can be accessed from on-premises via VPN
B) Gateway Endpoints can be accessed from on-premises via VPN
C) Gateway Endpoints use Security Groups
D) Interface Endpoints modify route tables

<details>
<summary>Click to reveal answer</summary>

**Answer: A) Interface Endpoints can be accessed from on-premises via VPN**

Explanation: Interface Endpoints create ENIs with private IP addresses, so they can be accessed from on-premises networks via VPN or Direct Connect. Gateway Endpoints only work from within the VPC.

```
Endpoint Access from On-Premises:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  On-Premises Data Center                            │
│  ┌───────────────────────────────────────────────┐  │
│  │                                                │  │
│  │   Server                                      │  │
│  │     │                                         │  │
│  └─────┼─────────────────────────────────────────┘  │
│        │                                            │
│        │ VPN / Direct Connect                       │
│        │                                            │
│  ┌─────▼─────────────────────────────────────────┐  │
│  │                    VPC                         │  │
│  │                                                │  │
│  │  ┌────────────────┐    ┌────────────────────┐ │  │
│  │  │ Gateway        │    │ Interface          │ │  │
│  │  │ Endpoint       │    │ Endpoint           │ │  │
│  │  │                │    │                    │ │  │
│  │  │ (Route-based)  │    │ ENI: 10.0.1.50     │ │  │
│  │  │                │    │ (IP-addressable)   │ │  │
│  │  │ Access from    │    │                    │ │  │
│  │  │ on-prem: NO    │    │ Access from        │ │  │
│  │  │                │    │ on-prem: YES       │ │  │
│  │  └────────────────┘    └────────────────────┘ │  │
│  │                                                │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Section 7: Hybrid Connectivity (Questions 29-30)

### Question 29
**What is the maximum bandwidth for a single AWS Site-to-Site VPN connection?**

A) 500 Mbps
B) 1.25 Gbps
C) 10 Gbps
D) 100 Gbps

<details>
<summary>Click to reveal answer</summary>

**Answer: B) 1.25 Gbps**

Explanation: A single AWS Site-to-Site VPN connection supports up to 1.25 Gbps throughput. For higher bandwidth, you can use multiple VPN connections with ECMP (Equal Cost Multi-Path) or use Direct Connect.

```
VPN Bandwidth Options:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Single VPN Connection: Up to 1.25 Gbps             │
│                                                      │
│  For Higher Bandwidth:                              │
│  ┌───────────────────────────────────────────────┐  │
│  │                                                │  │
│  │  Option 1: Multiple VPN + ECMP                │  │
│  │  - Use Transit Gateway                        │  │
│  │  - Enable ECMP routing                        │  │
│  │  - Up to 50 VPN connections                   │  │
│  │  - Max ~50 Gbps aggregated                    │  │
│  │                                                │  │
│  │  Option 2: AWS Direct Connect                 │  │
│  │  - 1 Gbps or 10 Gbps dedicated               │  │
│  │  - 100 Gbps dedicated                        │  │
│  │  - More consistent latency                    │  │
│  │                                                │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

### Question 30
**Which AWS service provides a dedicated, private network connection from your data center to AWS?**

A) Site-to-Site VPN
B) Client VPN
C) AWS Direct Connect
D) Transit Gateway

<details>
<summary>Click to reveal answer</summary>

**Answer: C) AWS Direct Connect**

Explanation: AWS Direct Connect provides a dedicated, private network connection from your premises to AWS. It does NOT go over the public internet, unlike VPN which creates an encrypted tunnel over the internet.

```
VPN vs Direct Connect:
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Site-to-Site VPN:                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │                                                │  │
│  │  On-Prem ═══╗                    ┌────────┐   │  │
│  │             ║ Encrypted Tunnel   │  VPC   │   │  │
│  │             ╠════════════════════╣        │   │  │
│  │             ║   PUBLIC INTERNET  │        │   │  │
│  │             ╚════════════════════╝        │   │  │
│  │                                  └────────┘   │  │
│  │  - Up to 1.25 Gbps                           │  │
│  │  - Variable latency                          │  │
│  │  - Quick to set up                           │  │
│  │                                                │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  AWS Direct Connect:                                │
│  ┌───────────────────────────────────────────────┐  │
│  │                                                │  │
│  │  On-Prem ──────────────────────── AWS         │  │
│  │          │ Private, Dedicated   │ Region      │  │
│  │          │ Physical Connection  │             │  │
│  │          │ (Colocation/Partner) │             │  │
│  │          └──────────────────────┘             │  │
│  │                                                │  │
│  │  - 1/10/100 Gbps options                     │  │
│  │  - Consistent latency                        │  │
│  │  - Weeks to provision                        │  │
│  │  - Does NOT traverse internet               │  │
│  │                                                │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```
</details>

---

## Answer Key Summary

| Question | Answer | Topic |
|----------|--------|-------|
| 1 | C | VPC CIDR Limits |
| 2 | C | Reserved IPs |
| 3 | B | CIDR Calculation |
| 4 | C | Default VPC |
| 5 | A | CIDR Range Calculation |
| 6 | A, C | RFC 1918 Ranges |
| 7 | B | Public Subnet Definition |
| 8 | B | Subnet-AZ Relationship |
| 9 | B | Route Table Association |
| 10 | C | Route Table Deletion |
| 11 | B | Longest Prefix Match |
| 12 | C | IGW Limits |
| 13 | B | NAT Gateway vs Instance |
| 14 | B | Private Subnet Internet Access |
| 15 | C | Egress-only IGW |
| 16 | B | NAT Gateway Availability |
| 17 | C | SG vs NACL |
| 18 | C | NACL Rule Evaluation |
| 19 | B | Stateful Security Groups |
| 20 | B | Default NACL Behavior |
| 21 | B | Security Group Limits |
| 22 | B | Transitive Peering |
| 23 | B | Transit Gateway Benefits |
| 24 | B | VPC Peering Requirements |
| 25 | B | Scaling VPC Connectivity |
| 26 | A | Gateway vs Interface Endpoints |
| 27 | B | Cost-Effective S3 Access |
| 28 | A | Endpoint On-Prem Access |
| 29 | B | VPN Bandwidth |
| 30 | C | Direct Connect |

---

## Scoring Guide

- **27-30 Correct (90-100%):** Expert Level - Ready for AWS Advanced Networking exam
- **24-26 Correct (80-86%):** Proficient - Solid understanding of VPC concepts
- **20-23 Correct (67-76%):** Developing - Review weak areas before proceeding
- **Below 20 (< 67%):** Needs Review - Revisit module content thoroughly

---

## Network Diagram Reference

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE VPC ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                              INTERNET                                            │
│                                  │                                               │
│                    ┌─────────────▼─────────────┐                                │
│                    │     Internet Gateway       │                                │
│                    └─────────────┬─────────────┘                                │
│                                  │                                               │
│  ┌───────────────────────────────┴───────────────────────────────┐              │
│  │                           VPC (10.0.0.0/16)                   │              │
│  │                                                                │              │
│  │  ┌────────────────────────────────────────────────────────┐   │              │
│  │  │                    Public Subnet (10.0.1.0/24)         │   │              │
│  │  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │   │              │
│  │  │  │   Bastion   │   │     ALB     │   │ NAT Gateway │  │   │              │
│  │  │  │    Host     │   │             │   │             │  │   │              │
│  │  │  └─────────────┘   └─────────────┘   └──────┬──────┘  │   │              │
│  │  │         │                 │                  │         │   │              │
│  │  │         │       Route: 0.0.0.0/0 -> IGW     │         │   │              │
│  │  └─────────┼─────────────────┼──────────────────┼─────────┘   │              │
│  │            │                 │                  │             │              │
│  │  ┌─────────┼─────────────────┼──────────────────┼─────────┐   │              │
│  │  │         │    Private Subnet (10.0.2.0/24)    │         │   │              │
│  │  │         ▼                 │                  │         │   │              │
│  │  │  ┌─────────────┐   ┌─────────────┐          │         │   │              │
│  │  │  │     EC2     │   │     EC2     │◄─────────┘         │   │              │
│  │  │  │   App Tier  │   │   App Tier  │                    │   │              │
│  │  │  └─────────────┘   └─────────────┘                    │   │              │
│  │  │         │                 │                            │   │              │
│  │  │         │       Route: 0.0.0.0/0 -> NAT-GW            │   │              │
│  │  └─────────┼─────────────────┼────────────────────────────┘   │              │
│  │            │                 │                                │              │
│  │  ┌─────────┼─────────────────┼────────────────────────────┐   │              │
│  │  │         │    Private Subnet (10.0.3.0/24)              │   │              │
│  │  │         ▼                 ▼                             │   │              │
│  │  │  ┌─────────────┐   ┌─────────────┐                     │   │              │
│  │  │  │    RDS      │   │ ElastiCache │                     │   │              │
│  │  │  │  Primary    │   │   Cluster   │                     │   │              │
│  │  │  └─────────────┘   └─────────────┘                     │   │              │
│  │  │                                                         │   │              │
│  │  │         Route: No internet route (isolated)            │   │              │
│  │  └─────────────────────────────────────────────────────────┘   │              │
│  │                                                                │              │
│  │  ┌────────────────────────────────────────────────────────┐   │              │
│  │  │ Gateway Endpoint ──► S3 (com.amazonaws.region.s3)      │   │              │
│  │  └────────────────────────────────────────────────────────┘   │              │
│  │                                                                │              │
│  │  Security:                                                    │              │
│  │  - Security Groups: Web-SG, App-SG, DB-SG                    │              │
│  │  - NACLs: Public-NACL, Private-NACL                          │              │
│  │                                                                │              │
│  └────────────────────────────────────────────────────────────────┘              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

**Congratulations on completing the VPC Module Quiz!**

Review any questions you missed and revisit the corresponding sections in the module materials.
