# AWS Security Services Overview

## Introduction

AWS provides a comprehensive suite of security services that help you protect your infrastructure, data, and applications. This overview introduces the key security services and how they work together to provide defense in depth.

---

## Security Services Landscape

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AWS SECURITY SERVICES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     THREAT DETECTION & RESPONSE                       │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  GuardDuty        Security Hub      Detective       Incident Mgr     │   │
│  │  (Threats)        (Aggregation)     (Investigation) (Response)       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     VULNERABILITY MANAGEMENT                          │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  Inspector                    Macie                                   │   │
│  │  (Vulnerabilities)            (Data Discovery)                        │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     NETWORK & APPLICATION PROTECTION                  │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  WAF              Shield           Firewall Mgr    Network Firewall  │   │
│  │  (Web Apps)       (DDoS)           (Central Mgmt)  (VPC Filtering)   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     DATA PROTECTION                                   │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  KMS              CloudHSM         Secrets Mgr     Certificate Mgr   │   │
│  │  (Keys)           (HSM)            (Secrets)       (Certificates)    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     IDENTITY & ACCESS                                 │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  IAM              IAM Identity     Cognito         Directory Svc     │   │
│  │  (Access)         Center (SSO)     (App Users)     (AD Integration)  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     COMPLIANCE & GOVERNANCE                           │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  Config           CloudTrail       Audit Manager   Control Tower     │   │
│  │  (Compliance)     (API Logging)    (Audits)        (Multi-Account)   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Amazon GuardDuty

### What It Does
GuardDuty is an intelligent threat detection service that continuously monitors for malicious activity and unauthorized behavior.

### Data Sources Analyzed

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GUARDDUTY DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  VPC Flow Logs ──────► Network traffic patterns                         │
│                        - Unusual ports                                   │
│                        - Suspicious IPs                                  │
│                        - Data exfiltration                              │
│                                                                          │
│  DNS Logs ───────────► DNS query analysis                               │
│                        - Malicious domains                              │
│                        - Crypto mining pools                            │
│                        - Command & control servers                       │
│                                                                          │
│  CloudTrail ─────────► API activity                                     │
│                        - Unusual API calls                              │
│                        - Credential theft                               │
│                        - Unauthorized access                            │
│                                                                          │
│  S3 Data Events ─────► S3 access patterns                               │
│                        - Unusual access                                 │
│                        - Data theft                                     │
│                                                                          │
│  EKS Audit Logs ─────► Kubernetes activity                              │
│                        - Compromised containers                         │
│                        - Suspicious workloads                           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Features
- **Machine learning-based detection** - Learns normal behavior, detects anomalies
- **Threat intelligence** - Uses AWS and third-party feeds
- **Multi-account support** - Centralized management
- **Automated remediation** - Integration with Lambda, EventBridge

### Finding Types

| Category | Examples |
|----------|----------|
| **Reconnaissance** | Port scanning, API enumeration |
| **Instance Compromise** | Crypto mining, malware callbacks |
| **Account Compromise** | Credential theft, unusual API usage |
| **Bucket Compromise** | Unusual S3 access patterns |
| **Kubernetes** | Privileged container, suspicious exec |

---

## AWS Security Hub

### What It Does
Security Hub provides a comprehensive view of security alerts and security posture across your AWS accounts.

### Core Functions

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY HUB ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    FINDING AGGREGATION                           │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  GuardDuty ─────┐                                               │    │
│  │  Inspector ─────┤                                               │    │
│  │  Macie ─────────┼──────► Security Hub ──────► Dashboard         │    │
│  │  IAM Access ────┤              │              Insights          │    │
│  │  Firewall Mgr ──┤              │              Automated Actions │    │
│  │  3rd Party ─────┘              ▼                                │    │
│  │                         Findings (ASFF)                         │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    SECURITY STANDARDS                            │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │  ● AWS Foundational Security Best Practices                     │    │
│  │  ● CIS AWS Foundations Benchmark                                │    │
│  │  ● PCI DSS                                                      │    │
│  │  ● NIST Cybersecurity Framework                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Features
- **Centralized findings** - Single pane of glass for security
- **Automated checks** - Continuous compliance monitoring
- **Security score** - Aggregate security posture metric
- **Cross-account** - Aggregate findings from member accounts
- **Custom actions** - Trigger Lambda for remediation

### Security Standards

| Standard | Focus | Controls |
|----------|-------|----------|
| AWS Foundational | AWS-specific best practices | 200+ |
| CIS Benchmark | Industry security standards | 50+ |
| PCI DSS | Payment card security | 30+ |
| NIST CSF | Cybersecurity framework | 100+ |

---

## Amazon Inspector

### What It Does
Inspector is an automated vulnerability management service that scans for software vulnerabilities and unintended network exposure.

### Scanning Capabilities

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INSPECTOR SCANNING                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  EC2 INSTANCES                          CONTAINER IMAGES                 │
│  ┌─────────────────────────────┐       ┌─────────────────────────────┐  │
│  │ ● OS vulnerabilities (CVE)  │       │ ● Container CVEs            │  │
│  │ ● Package vulnerabilities   │       │ ● Base image issues         │  │
│  │ ● Network reachability      │       │ ● Dependency scanning       │  │
│  │ ● SSM Agent based           │       │ ● ECR integration           │  │
│  └─────────────────────────────┘       └─────────────────────────────┘  │
│                                                                          │
│  LAMBDA FUNCTIONS                       CODE REPOSITORIES               │
│  ┌─────────────────────────────┐       ┌─────────────────────────────┐  │
│  │ ● Dependency vulnerabilities│       │ ● Source code scanning      │  │
│  │ ● Runtime issues            │       │ ● Secret detection          │  │
│  │ ● Automatic scanning        │       │ ● CodeGuru integration      │  │
│  └─────────────────────────────┘       └─────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Features
- **Continuous scanning** - Automatic discovery and assessment
- **Risk-based prioritization** - CVSS scores with context
- **SBOM export** - Software Bill of Materials
- **Integration** - Security Hub, EventBridge

### Vulnerability Severity

```
Critical (9.0-10.0) ───► Immediate action required
High (7.0-8.9) ────────► Address within 7 days
Medium (4.0-6.9) ──────► Address within 30 days
Low (0.1-3.9) ─────────► Address at next cycle
Informational ─────────► Best practice recommendations
```

---

## Amazon Macie

### What It Does
Macie is a data security service that uses machine learning to discover, classify, and protect sensitive data in S3.

### Sensitive Data Discovery

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MACIE DATA DISCOVERY                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PERSONAL IDENTIFIABLE INFORMATION (PII)                                │
│  ├── Names, addresses, phone numbers                                    │
│  ├── Email addresses                                                    │
│  ├── Social Security Numbers                                            │
│  ├── Passport numbers                                                   │
│  └── Driver's license numbers                                           │
│                                                                          │
│  FINANCIAL DATA                                                         │
│  ├── Credit card numbers                                                │
│  ├── Bank account numbers                                               │
│  ├── Financial statements                                               │
│  └── Tax forms                                                          │
│                                                                          │
│  PROTECTED HEALTH INFORMATION (PHI)                                     │
│  ├── Medical record numbers                                             │
│  ├── Health insurance IDs                                               │
│  └── Medical diagnoses                                                  │
│                                                                          │
│  CREDENTIALS & SECRETS                                                  │
│  ├── API keys                                                           │
│  ├── Private keys                                                       │
│  └── Passwords in files                                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Features
- **Automated discovery** - Continuously scans S3 buckets
- **Custom data identifiers** - Create patterns for your data
- **Policy findings** - Bucket security issues
- **Sensitive data findings** - Discovered sensitive data
- **Data maps** - Visual overview of data sensitivity

---

## Amazon Detective

### What It Does
Detective automatically collects and analyzes log data to help you investigate security issues.

### Investigation Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DETECTIVE INVESTIGATION FLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Finding Trigger                                                      │
│     └── GuardDuty finding detected                                      │
│                                                                          │
│  2. One-Click Investigation                                             │
│     └── Navigate to Detective from finding                              │
│                                                                          │
│  3. Automatic Analysis                                                  │
│     ├── Behavior graphs                                                 │
│     ├── Entity relationships                                            │
│     ├── Timeline of activities                                          │
│     └── Statistical analysis                                            │
│                                                                          │
│  4. Visualizations                                                      │
│     ├── IP address connections                                          │
│     ├── User activity patterns                                          │
│     ├── Resource interactions                                           │
│     └── Geolocation data                                                │
│                                                                          │
│  5. Root Cause Analysis                                                 │
│     └── Determine scope and impact                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Sources
- CloudTrail logs (12 months)
- VPC Flow Logs
- GuardDuty findings
- EKS audit logs

---

## AWS WAF (Web Application Firewall)

### What It Does
WAF protects web applications from common web exploits and bots.

### Protection Capabilities

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WAF PROTECTION LAYERS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  WEB ACL                                                                │
│  ├── Rule Groups                                                        │
│  │   ├── AWS Managed Rules                                              │
│  │   │   ├── Core Rule Set (OWASP Top 10)                              │
│  │   │   ├── SQL Injection                                              │
│  │   │   ├── Known Bad Inputs                                           │
│  │   │   ├── IP Reputation                                              │
│  │   │   └── Bot Control                                                │
│  │   │                                                                  │
│  │   ├── AWS Marketplace Rules                                          │
│  │   │   ├── F5, Imperva, Fortinet                                     │
│  │   │   └── Trend Micro, etc.                                         │
│  │   │                                                                  │
│  │   └── Custom Rules                                                   │
│  │       ├── Rate limiting                                              │
│  │       ├── Geo-blocking                                               │
│  │       ├── IP blacklists                                              │
│  │       └── Custom regex patterns                                      │
│  │                                                                      │
│  └── Protected Resources                                                │
│      ├── CloudFront distributions                                       │
│      ├── Application Load Balancers                                     │
│      ├── API Gateway                                                    │
│      └── AppSync                                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Rule Actions
- **Allow** - Permit the request
- **Block** - Deny the request
- **Count** - Count but allow (testing)
- **CAPTCHA** - Challenge suspicious requests

---

## AWS Shield

### What It Does
Shield provides managed DDoS protection for your AWS resources.

### Tiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHIELD COMPARISON                                     │
├──────────────────────────────┬──────────────────────────────────────────┤
│      SHIELD STANDARD         │         SHIELD ADVANCED                  │
├──────────────────────────────┼──────────────────────────────────────────┤
│                              │                                          │
│  ● Free for all AWS          │  ● $3,000/month + data transfer          │
│    customers                 │                                          │
│                              │  ● 24/7 DDoS Response Team (DRT)         │
│  ● Layer 3/4 protection      │                                          │
│                              │  ● Layer 3/4/7 protection                │
│  ● Automatic                 │                                          │
│                              │  ● Real-time metrics                     │
│  ● Always on                 │                                          │
│                              │  ● Cost protection                       │
│  ● Protects:                 │                                          │
│    - CloudFront              │  ● Advanced mitigation                   │
│    - Route 53                │                                          │
│    - Global Accelerator      │  ● SLA with financial protection         │
│                              │                                          │
│                              │  ● Additional protected resources:       │
│                              │    - ELB                                 │
│                              │    - EC2                                 │
│                              │    - Elastic IP                          │
│                              │                                          │
└──────────────────────────────┴──────────────────────────────────────────┘
```

---

## AWS KMS (Key Management Service)

### What It Does
KMS creates and manages cryptographic keys for encrypting your data.

### Key Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    KMS KEY HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    AWS MANAGED KEYS                              │    │
│  │  ● Created automatically by AWS services                         │    │
│  │  ● Rotated every 3 years                                         │    │
│  │  ● Cannot manage key policy                                      │    │
│  │  ● Example: aws/s3, aws/ebs, aws/rds                            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    CUSTOMER MANAGED KEYS (CMK)                   │    │
│  │  ● Created and managed by you                                    │    │
│  │  ● Full control over key policy                                  │    │
│  │  ● Optional automatic rotation (annual)                          │    │
│  │  ● Audit via CloudTrail                                          │    │
│  │  ● Can be multi-region                                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    CUSTOMER MANAGED (IMPORTED)                   │    │
│  │  ● Bring your own key material                                   │    │
│  │  ● Manual rotation required                                      │    │
│  │  ● Can set expiration                                            │    │
│  │  ● For compliance requirements                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Envelope Encryption

```
Plain Data ──► Encrypted with Data Key ──► Ciphertext
                        │
                        ▼
Data Key ───► Encrypted with KMS Key ──► Encrypted Data Key
                        │
                        ▼
                 Store together:
              [Encrypted Data Key + Ciphertext]
```

---

## AWS Secrets Manager

### What It Does
Secrets Manager helps you protect access to applications, services, and IT resources without upfront cost and on-going maintenance.

### Core Capabilities

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECRETS MANAGER FEATURES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  SECRET STORAGE                                                         │
│  ├── Database credentials                                               │
│  ├── API keys                                                           │
│  ├── OAuth tokens                                                       │
│  └── Arbitrary secrets (up to 64KB)                                     │
│                                                                          │
│  AUTOMATIC ROTATION                                                     │
│  ├── Built-in rotation for RDS, Redshift, DocumentDB                   │
│  ├── Custom Lambda rotation for other secrets                          │
│  └── Configurable rotation schedules                                    │
│                                                                          │
│  ACCESS CONTROL                                                         │
│  ├── IAM policies                                                       │
│  ├── Resource-based policies                                            │
│  └── Cross-account access                                               │
│                                                                          │
│  ENCRYPTION                                                             │
│  ├── Encrypted at rest with KMS                                         │
│  └── Encrypted in transit                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## AWS Organizations

### What It Does
Organizations helps you centrally manage and govern multiple AWS accounts.

### Organization Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ORGANIZATIONS HIERARCHY                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                           Root                                          │
│                            │                                            │
│               ┌────────────┼────────────┐                               │
│               │            │            │                               │
│              OU:          OU:          OU:                              │
│           Security    Production    Development                         │
│               │            │            │                               │
│        ┌──────┴──────┐     │      ┌─────┴─────┐                         │
│        │             │     │      │           │                         │
│    Log Archive   Security  │    Dev Team 1  Dev Team 2                  │
│     Account      Tooling   │     Account     Account                    │
│                  Account   │                                            │
│                            │                                            │
│                    ┌───────┴───────┐                                    │
│                    │               │                                    │
│                 Prod App 1    Prod App 2                                │
│                  Account       Account                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Service Control Policies (SCPs)

```
Root (All Services)
    │
    ├── OU: Production
    │   SCP: Deny ec2:TerminateInstances without MFA
    │       │
    │       └── Account: Prod-App
    │           Effective: Cannot terminate without MFA
    │
    └── OU: Development
        SCP: Deny expensive instance types
            │
            └── Account: Dev-Team
                Effective: Limited instance types
```

---

## How Services Work Together

### Security Operations Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    INTEGRATED SECURITY OPERATIONS                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. DETECT ──────────────────────────────────────────────────────────►  │
│     │                                                                    │
│     ├── GuardDuty ──► Threat detection                                  │
│     ├── Inspector ──► Vulnerability scanning                            │
│     ├── Macie ─────► Sensitive data discovery                           │
│     └── Config ────► Configuration compliance                           │
│                                                                          │
│  2. AGGREGATE ───────────────────────────────────────────────────────►  │
│     │                                                                    │
│     └── Security Hub ──► Unified findings dashboard                     │
│                                                                          │
│  3. INVESTIGATE ─────────────────────────────────────────────────────►  │
│     │                                                                    │
│     ├── Detective ──► Deep investigation                                │
│     └── CloudTrail ─► API audit trail                                   │
│                                                                          │
│  4. RESPOND ─────────────────────────────────────────────────────────►  │
│     │                                                                    │
│     ├── EventBridge ──► Trigger automation                              │
│     ├── Lambda ──────► Custom remediation                               │
│     └── Systems Mgr ─► Patching, configuration                          │
│                                                                          │
│  5. PROTECT ─────────────────────────────────────────────────────────►  │
│     │                                                                    │
│     ├── WAF ─────────► Web application firewall                         │
│     ├── Shield ──────► DDoS protection                                  │
│     └── Network FW ──► VPC traffic filtering                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Protection Flow

```
Application ──► Secrets Manager ──► Retrieve credentials
                     │
                     ▼
              Encrypted with KMS
                     │
                     ▼
              CloudTrail logging
                     │
                     ▼
              Security Hub findings
```

---

## Service Pricing Overview

| Service | Pricing Model | Estimated Monthly Cost |
|---------|---------------|----------------------|
| GuardDuty | Per GB analyzed + per event | $10-100+ |
| Security Hub | Per finding check + findings | $5-50+ |
| Inspector | Per EC2/container scan | $1.25/instance |
| Macie | Per bucket + GB scanned | $0.10/bucket + $1/GB |
| Detective | Per GB ingested | ~$2/GB |
| WAF | Per ACL + rules + requests | $5+ per ACL |
| Shield Advanced | $3,000/month + data | $3,000+ |
| KMS | Per key + requests | $1/key + requests |
| Secrets Manager | Per secret + API calls | $0.40/secret |

---

## Quick Reference: When to Use What

| Need | Service |
|------|---------|
| Detect threats | GuardDuty |
| Centralized security view | Security Hub |
| Find vulnerabilities | Inspector |
| Discover sensitive data | Macie |
| Investigate incidents | Detective |
| Protect web apps | WAF |
| DDoS protection | Shield |
| Manage encryption keys | KMS |
| Store secrets | Secrets Manager |
| Multi-account management | Organizations |
| Configuration compliance | Config |
| API auditing | CloudTrail |

---

## Next Steps

Now that you have an overview of AWS security services, dive deeper into each service:

- [03-guardduty.md](03-guardduty.md) - Threat Detection with GuardDuty
- [04-security-hub.md](04-security-hub.md) - Centralized Security with Security Hub
- [05-waf-shield.md](05-waf-shield.md) - Web Application and DDoS Protection
- [06-kms.md](06-kms.md) - Key Management Service
- [07-secrets-manager.md](07-secrets-manager.md) - Secrets Management
