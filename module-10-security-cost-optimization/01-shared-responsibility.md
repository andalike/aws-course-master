# Shared Responsibility Model

## Introduction

The AWS Shared Responsibility Model is the foundation of cloud security. It defines the division of security responsibilities between AWS (the cloud provider) and you (the customer). Understanding this model is critical for maintaining a secure AWS environment.

---

## The Core Concept

### AWS Responsibility: "Security OF the Cloud"

AWS is responsible for protecting the infrastructure that runs all AWS services:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS RESPONSIBILITIES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHYSICAL SECURITY                                                  │
│  ├── Data centers with 24/7 security guards                        │
│  ├── Biometric access controls                                      │
│  ├── Video surveillance                                             │
│  ├── Environmental controls (fire, flood, power)                    │
│  └── Secure hardware destruction                                    │
│                                                                      │
│  INFRASTRUCTURE                                                      │
│  ├── Global network backbone                                        │
│  ├── Hardware servers, storage, networking equipment                │
│  ├── Hypervisor and virtualization layer                           │
│  ├── Managed services software stack                                │
│  └── Regional and AZ architecture                                   │
│                                                                      │
│  SOFTWARE (for managed services)                                    │
│  ├── Operating system patches (for managed services)                │
│  ├── Database engine updates (RDS, DynamoDB)                        │
│  ├── Service software updates                                       │
│  └── Security of AWS APIs                                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Customer Responsibility: "Security IN the Cloud"

Customers are responsible for security of everything they put in or configure on AWS:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CUSTOMER RESPONSIBILITIES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DATA                                                               │
│  ├── Customer data classification                                   │
│  ├── Encryption choices (in-transit and at-rest)                    │
│  ├── Data backup and recovery                                       │
│  └── Data residency and sovereignty                                 │
│                                                                      │
│  IDENTITY & ACCESS                                                  │
│  ├── IAM users, groups, roles, policies                            │
│  ├── MFA configuration                                              │
│  ├── Password policies                                              │
│  ├── API key management                                             │
│  └── Federation and SSO setup                                       │
│                                                                      │
│  APPLICATION SECURITY                                               │
│  ├── Application code security                                      │
│  ├── Application-level authentication                               │
│  ├── Input validation                                               │
│  └── Security testing (SAST, DAST)                                 │
│                                                                      │
│  OPERATING SYSTEM (for IaaS)                                        │
│  ├── OS patching                                                    │
│  ├── OS hardening                                                   │
│  ├── Anti-malware                                                   │
│  └── System configuration                                           │
│                                                                      │
│  NETWORK CONFIGURATION                                              │
│  ├── VPC design                                                     │
│  ├── Security groups                                                │
│  ├── NACLs                                                          │
│  ├── Route tables                                                   │
│  └── Firewall rules                                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Responsibility Varies by Service Type

The division of responsibility changes based on the service type:

### Infrastructure Services (IaaS)

**Example: Amazon EC2**

```
┌─────────────────────────────────────────────────────┐
│                CUSTOMER RESPONSIBILITY              │
├─────────────────────────────────────────────────────┤
│  Customer Data                                      │
│  Platform, Applications, Identity & Access Mgmt     │
│  Operating System, Network & Firewall Config        │
│  Client-side Encryption, Server-side Encryption     │
│  Network Traffic Protection                         │
├─────────────────────────────────────────────────────┤
│                  AWS RESPONSIBILITY                 │
├─────────────────────────────────────────────────────┤
│  Compute │ Storage │ Database │ Networking          │
│  Hardware/AWS Global Infrastructure                 │
│  Regions │ Availability Zones │ Edge Locations      │
└─────────────────────────────────────────────────────┘
```

**Customer must:**
- Patch the operating system
- Configure security groups
- Manage IAM roles for EC2
- Install and configure firewalls
- Encrypt data at rest (EBS encryption)
- Encrypt data in transit (TLS)

### Container Services

**Example: Amazon ECS on EC2 vs ECS on Fargate**

```
ECS on EC2:                      ECS on Fargate:
┌───────────────────────┐       ┌───────────────────────┐
│ Customer: Container   │       │ Customer: Container   │
│ Customer: OS & Infra  │       │ AWS: OS & Infra       │
│ AWS: Compute          │       │ AWS: Compute          │
└───────────────────────┘       └───────────────────────┘
```

### Managed Services (PaaS)

**Example: Amazon RDS**

```
┌─────────────────────────────────────────────────────┐
│                CUSTOMER RESPONSIBILITY              │
├─────────────────────────────────────────────────────┤
│  Customer Data                                      │
│  Application Integration                            │
│  IAM & Network Configuration                        │
│  Encryption Options                                 │
├─────────────────────────────────────────────────────┤
│                  AWS RESPONSIBILITY                 │
├─────────────────────────────────────────────────────┤
│  Operating System Patching                          │
│  Database Engine Patching                           │
│  High Availability Configuration                    │
│  Underlying Infrastructure                          │
└─────────────────────────────────────────────────────┘
```

**Customer must:**
- Configure security groups for database access
- Set up IAM authentication (if used)
- Enable encryption at rest
- Configure SSL/TLS connections
- Manage database users and permissions
- Back up and protect backups

**AWS handles:**
- OS patches
- Database engine updates
- Hardware maintenance
- Backup automation (customer enables)
- Multi-AZ failover

### Serverless / Abstracted Services

**Example: AWS Lambda, S3, DynamoDB**

```
┌─────────────────────────────────────────────────────┐
│                CUSTOMER RESPONSIBILITY              │
├─────────────────────────────────────────────────────┤
│  Customer Data                                      │
│  Application Code                                   │
│  Identity & Access Management                       │
│  Client-side Encryption                             │
├─────────────────────────────────────────────────────┤
│                  AWS RESPONSIBILITY                 │
├─────────────────────────────────────────────────────┤
│  Platform Software                                  │
│  Operating System                                   │
│  Network Infrastructure                             │
│  Physical Infrastructure                            │
└─────────────────────────────────────────────────────┘
```

**Customer must:**
- Write secure application code
- Configure IAM permissions correctly
- Choose encryption settings
- Configure access policies (S3 bucket policies, etc.)
- Protect API keys and secrets

---

## Service Comparison Matrix

| Responsibility | EC2 | RDS | Lambda | S3 | DynamoDB |
|---------------|-----|-----|--------|-----|----------|
| Physical Security | AWS | AWS | AWS | AWS | AWS |
| Network Infrastructure | AWS | AWS | AWS | AWS | AWS |
| Hypervisor | AWS | AWS | AWS | AWS | AWS |
| Operating System | **Customer** | AWS | AWS | AWS | AWS |
| Network Config (SG/NACL) | **Customer** | **Customer** | **Customer** | N/A | N/A |
| Platform/Application | **Customer** | Shared | **Customer** | N/A | N/A |
| IAM Permissions | **Customer** | **Customer** | **Customer** | **Customer** | **Customer** |
| Data Encryption | **Customer** | **Customer** | **Customer** | **Customer** | **Customer** |
| Customer Data | **Customer** | **Customer** | **Customer** | **Customer** | **Customer** |

---

## AWS Compliance and Certifications

AWS maintains numerous compliance certifications that demonstrate security of their infrastructure:

### Global Certifications

| Certification | Description |
|--------------|-------------|
| **SOC 1, 2, 3** | Service Organization Control reports for security, availability, and confidentiality |
| **ISO 27001** | International security management standard |
| **ISO 27017** | Cloud-specific security guidance |
| **ISO 27018** | Protection of personal data in the cloud |
| **ISO 9001** | Quality management systems |
| **CSA STAR** | Cloud Security Alliance registry |

### Regional/Industry Certifications

| Certification | Region/Industry |
|--------------|-----------------|
| **FedRAMP** | US Federal Government |
| **HIPAA** | US Healthcare |
| **PCI DSS** | Payment Card Industry |
| **SOX** | US Financial Reporting |
| **GDPR** | European Union Data Protection |
| **IRAP** | Australian Government |
| **C5** | German Federal Security |
| **MTCS** | Singapore Multi-Tier Cloud Security |

### How AWS Certifications Help You

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INHERITANCE OF COMPLIANCE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  AWS CERTIFIED                    YOUR RESPONSIBILITY               │
│  ┌─────────────────────┐          ┌─────────────────────┐           │
│  │ Physical security   │  ───►    │ Application security│           │
│  │ Network isolation   │          │ Data classification │           │
│  │ Hardware security   │          │ Access controls     │           │
│  │ Virtualization      │          │ Encryption choices  │           │
│  └─────────────────────┘          └─────────────────────┘           │
│                                                                      │
│  You inherit AWS's compliance controls for the infrastructure       │
│  layer, but must implement your own controls for your workloads     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Accessing Compliance Reports

**AWS Artifact** provides access to AWS compliance reports:

```bash
# Access AWS Artifact through Console:
# 1. Navigate to AWS Artifact
# 2. Accept the NDA (for some reports)
# 3. Download compliance reports

# Available reports include:
# - SOC reports
# - ISO certificates
# - PCI DSS Attestation of Compliance
# - HIPAA Business Associate Addendum
```

---

## Real-World Responsibility Scenarios

### Scenario 1: Data Breach on EC2

**Situation:** A company's EC2 instance was compromised due to an unpatched vulnerability.

```
Analysis:
┌─────────────────────────────────────────────────────────────────────┐
│  Q: Who is responsible?                                             │
│  A: The CUSTOMER                                                    │
│                                                                      │
│  Reason:                                                            │
│  - Customer chose to use EC2 (IaaS)                                 │
│  - Customer is responsible for OS patching on EC2                   │
│  - Customer should have implemented patch management                 │
│                                                                      │
│  Customer should have:                                              │
│  ├── Used Systems Manager Patch Manager                             │
│  ├── Implemented automated patching                                 │
│  ├── Used vulnerability scanning (Inspector)                        │
│  └── Followed CIS benchmarks for hardening                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Scenario 2: S3 Data Exposure

**Situation:** Company's S3 bucket was publicly accessible and data was leaked.

```
Analysis:
┌─────────────────────────────────────────────────────────────────────┐
│  Q: Who is responsible?                                             │
│  A: The CUSTOMER                                                    │
│                                                                      │
│  Reason:                                                            │
│  - S3 bucket policies are customer's responsibility                 │
│  - Public access settings are customer-configured                    │
│  - Data classification is customer's responsibility                 │
│                                                                      │
│  Customer should have:                                              │
│  ├── Enabled S3 Block Public Access                                 │
│  ├── Reviewed bucket policies regularly                             │
│  ├── Used Macie to discover sensitive data                          │
│  ├── Enabled server-side encryption                                 │
│  └── Implemented IAM policies with least privilege                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Scenario 3: RDS Database Failure

**Situation:** RDS database became unavailable due to hardware failure.

```
Analysis:
┌─────────────────────────────────────────────────────────────────────┐
│  Q: Who is responsible?                                             │
│  A: AWS (for the failure), but shared for recovery                  │
│                                                                      │
│  AWS's responsibility:                                              │
│  ├── Hardware maintenance                                           │
│  ├── Automatic failover (if Multi-AZ enabled)                       │
│  └── Restore from automated backups                                 │
│                                                                      │
│  Customer's responsibility:                                         │
│  ├── Enabling Multi-AZ for high availability                        │
│  ├── Configuring backup retention period                            │
│  ├── Testing recovery procedures                                    │
│  └── Designing for failure in application                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Shared Responsibility for Different Domains

### Encryption

| Aspect | AWS | Customer |
|--------|-----|----------|
| Encryption algorithms | Provides secure algorithms | Chooses to use them |
| Key management infrastructure | Provides KMS/CloudHSM | Manages key policies |
| SSL/TLS certificates | Provides ACM | Configures and applies |
| Client-side encryption | Provides SDKs | Implements in code |

### Patch Management

| Service Type | AWS Patches | Customer Patches |
|-------------|-------------|------------------|
| EC2 | Hypervisor only | OS, middleware, applications |
| RDS | Engine and OS | Nothing (managed) |
| Lambda | Runtime | Application dependencies |
| ECS on EC2 | None | OS and container images |
| ECS on Fargate | OS | Container images |

### Network Security

| Layer | AWS | Customer |
|-------|-----|----------|
| Physical network | Secure backbone | N/A |
| VPC isolation | Provides technology | Configures VPCs |
| DDoS protection | Shield Standard | Shield Advanced (optional) |
| Firewall | Provides SG/NACL | Configures rules |
| SSL/TLS | Provides certificates | Implements in applications |

---

## Compliance Responsibility Matrix

| Compliance Requirement | AWS Provides | Customer Implements |
|-----------------------|--------------|---------------------|
| **HIPAA** | BAA, HIPAA-eligible services | Access controls, encryption, audit logging |
| **PCI DSS** | Level 1 service provider | Cardholder data protection, network segmentation |
| **GDPR** | DPA, data residency options | Data processing policies, consent management |
| **SOC 2** | SOC reports for AWS | SOC controls for customer systems |
| **FedRAMP** | FedRAMP authorized regions | Customer authorization packages |

---

## Best Practices for Customers

### 1. Understand Your Services

```python
# Document your service usage and responsibilities

services_used = {
    "EC2": {
        "type": "IaaS",
        "customer_responsible_for": [
            "OS patching",
            "Security groups",
            "Application security",
            "Data encryption"
        ]
    },
    "RDS": {
        "type": "PaaS",
        "customer_responsible_for": [
            "Network access configuration",
            "Database user management",
            "Encryption settings",
            "Backup verification"
        ]
    },
    "Lambda": {
        "type": "Serverless",
        "customer_responsible_for": [
            "Function code security",
            "IAM permissions",
            "VPC configuration (if used)",
            "Environment variables encryption"
        ]
    }
}
```

### 2. Implement Defense in Depth

```
Layer 1: Identity & Access ─────► IAM, MFA, least privilege
        │
Layer 2: Network ────────────────► VPC, SGs, NACLs, PrivateLink
        │
Layer 3: Data ───────────────────► Encryption, tokenization, masking
        │
Layer 4: Application ────────────► WAF, input validation, secure coding
        │
Layer 5: Monitoring ─────────────► CloudTrail, GuardDuty, CloudWatch
```

### 3. Automate Security Controls

```yaml
# AWS Config Rule for compliance checking
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  S3PublicAccessCheck:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-public-read-prohibited
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_READ_PROHIBITED

  EncryptedVolumesCheck:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: encrypted-volumes
      Source:
        Owner: AWS
        SourceIdentifier: ENCRYPTED_VOLUMES
```

### 4. Regular Security Assessments

```
Weekly:
├── Review GuardDuty findings
├── Check Security Hub score
└── Review access logs

Monthly:
├── IAM access review
├── Vulnerability scans
└── Patch compliance check

Quarterly:
├── Penetration testing
├── Compliance audit
└── Disaster recovery test

Annually:
├── Well-Architected Review
├── Third-party security audit
└── Compliance recertification
```

---

## Key Takeaways

1. **AWS secures the cloud infrastructure** - physical, network, hypervisor
2. **Customers secure what they put in the cloud** - data, applications, access
3. **Responsibility varies by service type** - more control = more responsibility
4. **Compliance is shared** - inherit AWS controls, implement your own
5. **Understand each service** - know exactly what you're responsible for
6. **Automate security** - use AWS services to enforce security at scale
7. **Regular assessments** - continuously verify your security posture

---

## Knowledge Check

1. If your EC2 instance is compromised due to an unpatched vulnerability, who is responsible?
2. Who patches the database engine for Amazon RDS?
3. For a Lambda function, who is responsible for the runtime security?
4. If your S3 bucket is exposed publicly, who is responsible?
5. What AWS service provides compliance reports and certifications?

---

## Next Steps

Continue to [02-security-services-overview.md](02-security-services-overview.md) to learn about the AWS security services that help you fulfill your responsibilities.
