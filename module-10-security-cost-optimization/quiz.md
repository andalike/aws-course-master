# Module 10: Security and Cost Optimization Quiz

## Instructions

- Total Questions: 30
- Time Limit: 45 minutes (suggested)
- Passing Score: 80% (24 correct answers)
- Question Types: Multiple Choice, Multiple Select, Scenario-Based

---

## Section 1: Shared Responsibility Model (Questions 1-4)

### Question 1

**In the AWS Shared Responsibility Model, which of the following is the CUSTOMER's responsibility?**

A) Physical security of data centers
B) Patching the hypervisor
C) Configuring security groups and NACLs
D) Hardware maintenance of servers

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Configuring security groups and NACLs**

**Explanation:**
- AWS is responsible for "Security OF the Cloud" - physical infrastructure, hypervisor, hardware
- Customers are responsible for "Security IN the Cloud" - including network configuration like security groups and NACLs
- Security groups and NACLs are customer-managed controls that determine what traffic can access your resources

**Key Point:** Anything you configure or control in your AWS account is your responsibility.
</details>

---

### Question 2

**How does the Shared Responsibility Model differ between IaaS (like EC2) and managed services (like RDS)?**

A) There is no difference; customer responsibilities are identical
B) With managed services, AWS takes on more responsibility (like OS patching)
C) With IaaS, AWS handles all security
D) Managed services shift all responsibility to the customer

<details>
<summary>Show Answer</summary>

**Correct Answer: B) With managed services, AWS takes on more responsibility (like OS patching)**

**Explanation:**
- For **EC2 (IaaS)**: Customer is responsible for OS patching, security configuration, firewall rules, application security
- For **RDS (Managed)**: AWS handles OS patching, database software patching, and hardware maintenance
- The more managed the service, the more AWS takes on, but customers are always responsible for data and access control

**Example:**
- EC2: You patch the OS
- RDS: AWS patches the database engine
- S3: AWS manages everything except your data and access policies
</details>

---

### Question 3

**Which of the following is ALWAYS the customer's responsibility regardless of the AWS service used?**

A) Encryption key management
B) Patching operating systems
C) Physical security
D) Customer data and IAM configuration

<details>
<summary>Show Answer</summary>

**Correct Answer: D) Customer data and IAM configuration**

**Explanation:**
- Customer data protection and IAM configuration are ALWAYS customer responsibilities
- Even if AWS provides encryption services, you decide what to encrypt and who has access
- IAM policies determine who can access your resources - this is always your responsibility
- Options A, B are sometimes AWS responsibilities depending on the service

**Key Point:** You always control WHO has access (IAM) and WHAT data you store.
</details>

---

### Question 4

**A security auditor asks who is responsible for encrypting data at rest in an S3 bucket. What is the correct response?**

A) AWS is fully responsible for encryption
B) The customer must provide and manage encryption
C) Shared - AWS provides encryption mechanisms, customer decides to enable them
D) S3 encryption is automatic and neither party needs to manage it

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Shared - AWS provides encryption mechanisms, customer decides to enable them**

**Explanation:**
- AWS provides multiple encryption options: SSE-S3, SSE-KMS, SSE-C, client-side encryption
- The customer is responsible for choosing to enable encryption and selecting the appropriate method
- For SSE-S3: AWS manages the keys
- For SSE-KMS: Customer manages key policies
- For SSE-C: Customer provides and manages the keys entirely

**Best Practice:** Enable default bucket encryption with SSE-S3 or SSE-KMS.
</details>

---

## Section 2: GuardDuty and Threat Detection (Questions 5-8)

### Question 5

**What type of data sources does Amazon GuardDuty analyze for threat detection?**

A) Application logs only
B) VPC Flow Logs, CloudTrail Events, and DNS Logs
C) S3 access logs only
D) Database query logs and performance metrics

<details>
<summary>Show Answer</summary>

**Correct Answer: B) VPC Flow Logs, CloudTrail Events, and DNS Logs**

**Explanation:**
GuardDuty analyzes multiple data sources:
- **VPC Flow Logs**: Network traffic patterns, unusual connections
- **CloudTrail Events**: API activity, suspicious account behavior
- **DNS Logs**: Queries to known malicious domains
- **S3 Data Events**: Suspicious data access patterns (optional)
- **EKS Audit Logs**: Kubernetes activity (optional)

**Key Point:** GuardDuty uses machine learning to identify threats from these data sources without requiring you to configure log analysis.
</details>

---

### Question 6

**Your security team receives a GuardDuty finding with severity level "High" indicating potential cryptocurrency mining on an EC2 instance. What should be the FIRST response?**

A) Immediately terminate the instance
B) Investigate the finding and verify if it's a true positive
C) Ignore it as GuardDuty has false positives
D) Wait 24 hours to see if more findings appear

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Investigate the finding and verify if it's a true positive**

**Explanation:**
- High-severity findings require immediate attention but should be investigated first
- Verify by checking: instance metadata, network traffic, running processes
- If confirmed, then take action: isolate the instance, capture forensic data, then terminate
- Immediate termination could destroy forensic evidence
- Never ignore high-severity findings

**Recommended Steps:**
1. Investigate the finding details
2. Correlate with other logs (CloudTrail, VPC Flow Logs)
3. Isolate the resource if confirmed
4. Remediate and document
</details>

---

### Question 7

**How is GuardDuty priced?**

A) Flat monthly fee per account
B) Based on the number of findings generated
C) Based on volume of data analyzed (CloudTrail events, VPC Flow Logs, DNS queries)
D) Free, as it's included with all AWS accounts

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Based on volume of data analyzed (CloudTrail events, VPC Flow Logs, DNS queries)**

**Explanation:**
GuardDuty pricing is based on:
- Volume of CloudTrail events analyzed
- Volume of VPC Flow Logs analyzed
- Volume of DNS logs analyzed
- S3 data events (if enabled)
- EKS audit logs (if enabled)

**Free Tier:** 30-day free trial for new accounts

**Cost Tip:** Most accounts cost $1-10/month. Large accounts with high API activity may be higher.
</details>

---

### Question 8 (Multiple Select)

**Which of the following are valid actions you can take on GuardDuty findings? (Select THREE)**

A) Archive findings that are false positives
B) Automatically remediate using EventBridge rules
C) Delete findings permanently from GuardDuty
D) Suppress findings matching specific criteria
E) Export findings to S3 for long-term retention

<details>
<summary>Show Answer</summary>

**Correct Answers: A, B, D**

**Explanation:**
- **A) Archive findings**: Mark as reviewed without deleting
- **B) EventBridge automation**: Trigger Lambda functions for auto-remediation
- **D) Suppression rules**: Filter out known false positives based on criteria

Incorrect options:
- C) Findings cannot be permanently deleted - they age out after 90 days
- E) GuardDuty exports to Security Hub, not directly to S3 (though you can configure S3 export through Security Hub)

**Best Practice:** Create suppression rules for known benign patterns to reduce noise.
</details>

---

## Section 3: WAF and Shield (Questions 9-12)

### Question 9

**Which AWS service provides protection against DDoS attacks at layers 3 and 4 (network and transport layers)?**

A) AWS WAF
B) AWS Shield Standard
C) AWS GuardDuty
D) AWS Network Firewall

<details>
<summary>Show Answer</summary>

**Correct Answer: B) AWS Shield Standard**

**Explanation:**
- **Shield Standard**: Free, automatic L3/L4 protection against common DDoS attacks
- **Shield Advanced**: Paid, enhanced protection with DDoS Response Team access
- **WAF**: Works at Layer 7 (application layer) to filter HTTP/HTTPS traffic
- GuardDuty is for threat detection, not DDoS prevention

**Key Point:** Shield Standard is automatically enabled for all AWS customers at no additional cost.
</details>

---

### Question 10

**A web application is experiencing SQL injection attacks. Which AWS WAF rule type should you configure?**

A) Rate-based rule
B) AWS Managed Rules - SQL injection protection
C) Geographic match condition
D) IP set rule

<details>
<summary>Show Answer</summary>

**Correct Answer: B) AWS Managed Rules - SQL injection protection**

**Explanation:**
- AWS provides managed rule groups including SQL injection protection
- The **AWSManagedRulesSQLiRuleSet** specifically protects against SQL injection
- Rate-based rules are for limiting request rates
- Geographic rules block by location
- IP set rules block specific IPs

**Best Practice:** Enable the AWS Managed Rules Core Rule Set and SQL Injection Rule Set for baseline protection.
</details>

---

### Question 11

**What is the primary difference between AWS Shield Standard and AWS Shield Advanced?**

A) Shield Standard is for EC2, Advanced is for all services
B) Shield Advanced provides DDoS Response Team support and financial protection
C) Shield Standard protects Layer 7, Advanced protects Layer 3/4
D) Shield Advanced is free for all customers

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Shield Advanced provides DDoS Response Team support and financial protection**

**Explanation:**
**Shield Standard (Free):**
- Automatic L3/L4 protection
- No cost
- No DRT access

**Shield Advanced ($3,000/month + data charges):**
- 24/7 DDoS Response Team (DRT) access
- Cost protection - credits for scaling during attacks
- Advanced attack diagnostics
- WAF integration at no extra cost
- Health-based detection

**When to use Advanced:** High-profile applications, regulatory requirements, need for guaranteed response.
</details>

---

### Question 12

**You want to limit API requests from any single IP address to 1000 requests per 5 minutes. Which WAF rule type should you use?**

A) Regular rule with IP match condition
B) Rate-based rule with threshold of 1000
C) SQL injection rule
D) Size constraint rule

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Rate-based rule with threshold of 1000**

**Explanation:**
- Rate-based rules track and limit requests from individual IP addresses
- They can block IPs that exceed the threshold within a 5-minute period
- The blocked IPs are automatically unblocked when rates drop below threshold
- Regular IP rules would require manual management of blocked IPs

**Configuration:**
```json
{
  "RateLimit": 1000,
  "AggregateKeyType": "IP"
}
```

**Use Cases:** Preventing brute force attacks, API abuse, web scraping.
</details>

---

## Section 4: KMS and Encryption (Questions 13-16)

### Question 13

**What is the maximum size of data that can be encrypted directly using AWS KMS?**

A) 4 KB
B) 64 KB
C) 256 KB
D) 1 MB

<details>
<summary>Show Answer</summary>

**Correct Answer: A) 4 KB**

**Explanation:**
- KMS can directly encrypt a maximum of 4 KB of data
- For larger data, use **envelope encryption**:
  1. Generate a data key using KMS
  2. Use the data key to encrypt your data locally
  3. Store the encrypted data key alongside the encrypted data
- This is more efficient and reduces KMS API costs

**Key Point:** Most AWS services (S3, EBS, RDS) use envelope encryption automatically when you enable encryption with a KMS key.
</details>

---

### Question 14

**A company policy requires that encryption keys cannot be used until approved by two administrators. Which KMS feature supports this?**

A) Key rotation
B) Key policies
C) Multi-region keys
D) Custom key stores with CloudHSM

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Key policies**

**Explanation:**
While KMS itself doesn't have native multi-party approval, you can implement this through:
- **Key policies** combined with IAM policies requiring multiple principals
- Using AWS Systems Manager Automation with approval steps
- Integrating with CloudHSM for hardware-based key management

However, for true dual-control (m-of-n authentication), you would use:
- **D) Custom key stores with CloudHSM** - provides quorum-based key usage

**Note:** This question tests understanding of KMS limitations and alternatives. The most architecturally correct answer for dual-control is CloudHSM.

**Revised Answer: D) Custom key stores with CloudHSM**
</details>

---

### Question 15

**What happens when you schedule a KMS customer managed key for deletion?**

A) The key is immediately deleted
B) There is a mandatory waiting period of 7-30 days
C) The key is archived but can be restored anytime
D) All data encrypted with the key is automatically decrypted

<details>
<summary>Show Answer</summary>

**Correct Answer: B) There is a mandatory waiting period of 7-30 days**

**Explanation:**
- Minimum waiting period: 7 days
- Maximum waiting period: 30 days
- Default: 30 days if not specified
- During this period, the key cannot be used
- You can cancel deletion anytime during the waiting period
- After deletion, the key and all data encrypted with it become unrecoverable

**Best Practice:** Use 30-day waiting period and set up CloudWatch alarms for pending deletions.
</details>

---

### Question 16

**Which of the following describes envelope encryption?**

A) Encrypting the same data multiple times with different keys
B) Using a data key to encrypt data, then encrypting the data key with a master key
C) Storing encrypted data inside encrypted S3 buckets
D) Using separate keys for different AWS regions

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Using a data key to encrypt data, then encrypting the data key with a master key**

**Explanation:**
Envelope encryption process:
1. Request a data key from KMS
2. KMS returns plaintext data key + encrypted data key
3. Use plaintext data key to encrypt your data
4. Discard plaintext data key
5. Store encrypted data + encrypted data key together

Benefits:
- Only 4 KB limit for KMS operations
- Data key can encrypt unlimited data
- Reduced KMS API costs
- Better performance for large data

**Key Point:** AWS services like S3 use envelope encryption automatically.
</details>

---

## Section 5: Secrets Manager and Security Services (Questions 17-20)

### Question 17

**What is the PRIMARY advantage of AWS Secrets Manager over storing secrets in AWS Systems Manager Parameter Store?**

A) Lower cost
B) Automatic secret rotation
C) Larger storage capacity
D) Better IAM integration

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Automatic secret rotation**

**Explanation:**
**Secrets Manager advantages:**
- Built-in automatic rotation with Lambda functions
- Native integration with RDS, Redshift, DocumentDB for automatic credential rotation
- Designed specifically for secrets management

**Parameter Store:**
- Lower cost (free tier available)
- Manual rotation only
- Good for configuration data, not primarily secrets
- Can store secrets as SecureString

**Cost Comparison:**
- Secrets Manager: $0.40/secret/month + $0.05/10,000 API calls
- Parameter Store: Free tier + $0.05/10,000 API calls for Standard
</details>

---

### Question 18

**Which AWS service uses machine learning to automatically discover and protect sensitive data like PII in S3 buckets?**

A) Amazon GuardDuty
B) AWS Inspector
C) Amazon Macie
D) AWS Config

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Amazon Macie**

**Explanation:**
- **Macie**: Uses ML to discover, classify, and protect sensitive data (PII, financial data, credentials) in S3
- **GuardDuty**: Threat detection for account activity
- **Inspector**: Vulnerability assessment for EC2 and containers
- **Config**: Configuration compliance tracking

**Macie capabilities:**
- Automatic sensitive data discovery
- Data classification (PII, PHI, financial)
- Alerts for unencrypted/public buckets
- Integration with Security Hub
</details>

---

### Question 19

**Your company needs to perform vulnerability assessments on EC2 instances to check for software vulnerabilities and network exposure. Which service should you use?**

A) AWS Macie
B) AWS Inspector
C) AWS Config
D) AWS Security Hub

<details>
<summary>Show Answer</summary>

**Correct Answer: B) AWS Inspector**

**Explanation:**
**AWS Inspector** provides:
- Automated vulnerability management
- Software vulnerability detection (CVE database)
- Network reachability analysis
- Container image scanning in ECR
- Integration with Security Hub

**How it works:**
1. Install the SSM Agent on EC2 instances (usually pre-installed)
2. Inspector automatically scans for vulnerabilities
3. Findings are prioritized by severity
4. Remediation guidance provided

**Pricing:** Based on instance scanning hours and container images scanned.
</details>

---

### Question 20

**What is the main purpose of AWS Security Hub?**

A) To replace all individual security services
B) To provide a centralized view of security findings across AWS accounts and services
C) To automatically fix security vulnerabilities
D) To manage IAM policies

<details>
<summary>Show Answer</summary>

**Correct Answer: B) To provide a centralized view of security findings across AWS accounts and services**

**Explanation:**
**Security Hub provides:**
- Centralized dashboard for security findings
- Aggregates data from GuardDuty, Inspector, Macie, IAM Access Analyzer, Firewall Manager
- Compliance checks against standards (CIS, PCI-DSS, NIST)
- Cross-account consolidation with AWS Organizations
- Automated actions via EventBridge

**Security Hub does NOT:**
- Replace individual security services
- Automatically remediate issues (but can trigger automation)
- Manage IAM policies

**Key Point:** Think of Security Hub as the "single pane of glass" for security.
</details>

---

## Section 6: Cost Management (Questions 21-24)

### Question 21

**Which AWS tool would you use to forecast future AWS costs based on historical usage patterns?**

A) AWS Budgets
B) AWS Cost Explorer
C) AWS Pricing Calculator
D) AWS Trusted Advisor

<details>
<summary>Show Answer</summary>

**Correct Answer: B) AWS Cost Explorer**

**Explanation:**
**Cost Explorer features:**
- View historical costs (up to 12 months)
- Forecast future costs (up to 12 months)
- Filter by service, region, tags, linked accounts
- Identify trends and anomalies
- Reservation and Savings Plan recommendations

**Other tools:**
- AWS Budgets: Set spending limits and alerts
- Pricing Calculator: Estimate costs for new workloads
- Trusted Advisor: Optimization recommendations (not forecasting)
</details>

---

### Question 22

**A company wants to receive an alert when their AWS spending exceeds $5,000 in any month. Which service should they use?**

A) AWS Cost Explorer with custom reports
B) AWS Budgets with threshold alerts
C) CloudWatch billing alarms
D) Both B and C are valid options

<details>
<summary>Show Answer</summary>

**Correct Answer: D) Both B and C are valid options**

**Explanation:**
**Option 1 - AWS Budgets:**
- Create a monthly cost budget of $5,000
- Configure email alerts at threshold (e.g., 80%, 100%, 120%)
- Can trigger SNS notifications or Lambda functions
- 2 budgets free per account

**Option 2 - CloudWatch Billing Alarms:**
- Create a CloudWatch alarm on the billing metric
- Set threshold at $5,000
- Trigger SNS notification when exceeded
- Simple but less flexible than Budgets

**Best Practice:** Use AWS Budgets for more advanced alerting with forecasted spend alerts.
</details>

---

### Question 23

**Which cost allocation tag strategy would help identify costs for a specific project that spans multiple AWS services?**

A) Use service-specific tags only
B) Apply a consistent "Project" tag across all resources
C) Use separate AWS accounts for each project
D) Tag only the most expensive resources

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Apply a consistent "Project" tag across all resources**

**Explanation:**
**Tagging best practices:**
- Use consistent tag keys across all resources (e.g., "Project", "Environment", "CostCenter")
- Activate user-defined cost allocation tags in Billing Console
- Tags appear in Cost Explorer and Cost and Usage Reports
- Implement tag policies in AWS Organizations

**Required steps:**
1. Define tagging strategy
2. Apply tags to all resources
3. Activate tags as cost allocation tags
4. Wait 24 hours for tags to appear in billing data

**Key Point:** Tags must be activated as cost allocation tags to appear in billing reports.
</details>

---

### Question 24 (Multiple Select)

**Which of the following are valid strategies to reduce EC2 costs? (Select THREE)**

A) Use Reserved Instances for steady-state workloads
B) Use Spot Instances for fault-tolerant batch processing
C) Enable Auto Scaling to match capacity with demand
D) Always use the largest instance type for best price-per-performance
E) Run instances 24/7 for consistency

<details>
<summary>Show Answer</summary>

**Correct Answers: A, B, C**

**Explanation:**
- **A) Reserved Instances**: Up to 72% discount for 1-3 year commitments
- **B) Spot Instances**: Up to 90% discount for interruptible workloads
- **C) Auto Scaling**: Only pay for capacity you need

Incorrect options:
- D) Larger instances are not always better value - right-sizing is key
- E) Stop instances when not needed - dev/test environments especially

**Cost optimization priority:**
1. Right-size instances
2. Use Auto Scaling
3. Apply Reserved Instances/Savings Plans for steady-state
4. Use Spot for fault-tolerant workloads
5. Schedule start/stop for non-production
</details>

---

## Section 7: Trusted Advisor and Cost Optimization (Questions 25-27)

### Question 25

**Which AWS Trusted Advisor check is available to ALL AWS customers, regardless of support plan?**

A) Security Groups - Specific Ports Unrestricted
B) IAM Access Key Rotation
C) S3 Bucket Permissions
D) All core security checks are available to all customers

<details>
<summary>Show Answer</summary>

**Correct Answer: D) All core security checks are available to all customers**

**Explanation:**
**Free Trusted Advisor checks (all customers):**
- S3 Bucket Permissions (public access)
- Security Groups - Specific Ports Unrestricted (high-risk ports)
- EBS Public Snapshots
- RDS Public Snapshots
- IAM Use
- MFA on Root Account
- Service Limits

**Business/Enterprise support required for:**
- All 50+ checks across all categories
- Programmatic access via API
- Weekly email reports
- CloudWatch integration
</details>

---

### Question 26

**You notice AWS Trusted Advisor recommends purchasing Reserved Instances to save money. The recommendation shows potential monthly savings of $2,000. What should you verify BEFORE purchasing?**

A) Nothing - always follow Trusted Advisor recommendations
B) Verify the workload is stable and will run for the commitment period
C) Check if the instance family will be deprecated soon
D) Both B and C

<details>
<summary>Show Answer</summary>

**Correct Answer: D) Both B and C**

**Explanation:**
Before purchasing Reserved Instances:

**1. Workload stability (B):**
- Will this workload exist for 1-3 years?
- Is the application being migrated or retired?
- Historical usage patterns consistent?

**2. Instance family longevity (C):**
- Newer instance families may offer better value
- Convertible RIs allow changing instance types
- Standard RIs are locked to specific instance type

**Additional considerations:**
- Payment option (all upfront vs. partial vs. no upfront)
- Regional vs. Zonal RIs
- Consider Savings Plans as alternative

**Key Point:** Trusted Advisor provides recommendations, but business context is required for decisions.
</details>

---

### Question 27

**A Trusted Advisor check shows idle load balancers with no active connections. What is the recommended action?**

A) Ignore - load balancers are needed for high availability
B) Delete the load balancers if they are truly unused
C) Scale up instances behind the load balancer
D) Contact AWS support to investigate

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Delete the load balancers if they are truly unused**

**Explanation:**
**Idle Load Balancer check identifies:**
- Load balancers with no healthy backend instances
- Load balancers with minimal request count
- Unused load balancers still incurring costs

**Action steps:**
1. Verify the load balancer is truly unused (check CloudWatch metrics)
2. Confirm with application team
3. Take a snapshot of the configuration
4. Delete if confirmed unused

**Cost impact:** ALB costs ~$0.0225/hour + LCU charges = ~$16/month minimum
</details>

---

## Section 8: Scenario-Based Questions (Questions 28-30)

### Question 28

**Scenario:** A healthcare company storing PHI (Protected Health Information) in S3 needs to ensure data is encrypted, access is logged, and any public bucket access is immediately flagged. Which combination of services provides the BEST solution?

A) GuardDuty + CloudTrail + S3 Default Encryption
B) Macie + CloudTrail + S3 Block Public Access + KMS
C) Inspector + Config + Shield
D) Security Hub + VPC Flow Logs + WAF

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Macie + CloudTrail + S3 Block Public Access + KMS**

**Explanation:**
**Why this combination:**
- **Macie**: Discovers and monitors PHI in S3 buckets
- **CloudTrail**: Logs all S3 API access for audit requirements
- **S3 Block Public Access**: Prevents accidental public exposure
- **KMS**: Provides encryption with customer-managed keys for compliance

**HIPAA requirements addressed:**
- Encryption at rest (KMS)
- Access logging (CloudTrail)
- Data discovery and classification (Macie)
- Access controls (S3 policies, Block Public Access)

**Other options lack:**
- A) No PII/PHI discovery capability
- C) Wrong use cases (vulnerabilities, config compliance)
- D) Not focused on data protection
</details>

---

### Question 29

**Scenario:** Your company runs a production web application on EC2. Last month's bill was $50,000 with the following breakdown:
- EC2 instances: $30,000 (running 24/7)
- Data transfer: $10,000
- EBS storage: $5,000
- Other: $5,000

The workload is predictable with steady usage. What would be the MOST impactful cost optimization strategy?

A) Enable S3 Intelligent-Tiering
B) Purchase EC2 Reserved Instances or Compute Savings Plans
C) Move to Spot Instances
D) Reduce EBS volume sizes

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Purchase EC2 Reserved Instances or Compute Savings Plans**

**Explanation:**
**Analysis:**
- EC2 is 60% of the bill ($30,000)
- Workload is "predictable with steady usage" - perfect for RIs
- Reserved Instances can save up to 72%
- Potential savings: $30,000 × 0.60 = $18,000/month

**Why other options are less impactful:**
- A) S3 tiering won't help EC2/EBS costs
- C) Spot Instances are risky for production workloads
- D) EBS is only $5,000 - less impact than EC2 optimization

**Recommendation:**
1. Use Savings Plans (more flexible) or Reserved Instances
2. Choose 1-year or 3-year commitment based on confidence
3. Start with Compute Savings Plan for flexibility across instance families
</details>

---

### Question 30

**Scenario:** A startup is concerned about security but has limited budget and staff. They need to implement a security monitoring solution that requires minimal management. Which approach provides the BEST balance of security and operational simplicity?

A) Manually review CloudTrail logs daily
B) Enable GuardDuty, Security Hub, and set up SNS notifications
C) Hire a dedicated security team to monitor AWS
D) Deploy third-party security tools on EC2

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Enable GuardDuty, Security Hub, and set up SNS notifications**

**Explanation:**
**Why this is best:**
- **GuardDuty**: Automated threat detection, no infrastructure to manage
- **Security Hub**: Centralized view, compliance checks, prioritized findings
- **SNS notifications**: Alert on high-severity findings

**Benefits for startups:**
- Low cost: ~$5-30/month for small accounts
- Zero infrastructure management
- Machine learning-powered detection
- Compliance frameworks included
- Grows with your infrastructure

**Other options:**
- A) Manual review doesn't scale, easy to miss threats
- C) Expensive and not necessary for AWS-native monitoring
- D) Adds operational overhead and cost

**Quick setup:**
```bash
aws guardduty create-detector --enable
aws securityhub enable-security-hub
```
</details>

---

## Scoring Guide

| Score | Rating | Recommendation |
|-------|--------|----------------|
| 27-30 | Excellent | Ready for advanced topics and certification |
| 24-26 | Good | Review missed concepts, then proceed |
| 20-23 | Fair | Revisit the module content before moving on |
| Below 20 | Needs Improvement | Re-read all lessons and complete labs again |

---

## Topics to Review by Question

| Questions | Topic | Lesson |
|-----------|-------|--------|
| 1-4 | Shared Responsibility Model | 01-shared-responsibility.md |
| 5-8 | GuardDuty and Threat Detection | 03-guardduty.md |
| 9-12 | WAF and Shield | 05-waf-shield.md |
| 13-16 | KMS and Encryption | 06-kms.md |
| 17-20 | Secrets Manager & Security Services | 07-secrets-manager.md, 08-inspector.md, 09-macie.md |
| 21-24 | Cost Management | 10-cost-explorer.md |
| 25-27 | Trusted Advisor | 11-trusted-advisor.md |
| 28-30 | Scenario Application | All lessons |

---

## Next Steps

Congratulations on completing the Security and Cost Optimization module!

**If you scored 80% or higher:**
- You have a solid understanding of AWS security and cost optimization
- Proceed to the capstone projects
- Consider pursuing AWS Security Specialty certification

**If you scored below 80%:**
- Review the lessons for topics you missed
- Complete the hands-on labs again
- Retake the quiz after a few days of review

---

*Quiz Version: 1.0*
*Last Updated: January 2025*
