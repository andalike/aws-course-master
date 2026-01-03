# IAM Access Analyzer

## Introduction

IAM Access Analyzer helps you identify resources in your organization and accounts that are shared with an external entity. This is crucial for security because unintended public or cross-account access can lead to data breaches.

---

## What is IAM Access Analyzer?

```
+------------------------------------------------------------------+
|                    IAM ACCESS ANALYZER                            |
+------------------------------------------------------------------+
|                                                                   |
|  Purpose: Identify and review resource-based policies that        |
|           grant access to external principals                     |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                      ANALYZER                               |  |
|  |                                                             |  |
|  |  Zone of Trust: Your AWS Account (or Organization)         |  |
|  |                                                             |  |
|  |  +----------+  +----------+  +----------+  +----------+    |  |
|  |  | S3       |  | IAM      |  | KMS      |  | Lambda   |    |  |
|  |  | Buckets  |  | Roles    |  | Keys     |  | Functions|    |  |
|  |  +----+-----+  +----+-----+  +----+-----+  +----+-----+    |  |
|  |       |             |             |             |          |  |
|  |       +-------------+-------------+-------------+          |  |
|  |                           |                                |  |
|  |                           v                                |  |
|  |              +------------------------+                    |  |
|  |              |    FINDINGS            |                    |  |
|  |              | (External Access Found)|                    |  |
|  |              +------------------------+                    |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### Key Concepts

| Term | Definition |
|------|------------|
| **Zone of Trust** | The boundary within which access is considered trusted (account or organization) |
| **External Principal** | Any entity outside your zone of trust that has access |
| **Finding** | A detailed report of external access to a resource |
| **Archive Rule** | Automatically archive findings that match specific criteria |
| **Analyzer** | The Access Analyzer instance that monitors your resources |

---

## Why You Need Access Analyzer

### The Problem: Shadow Access

```
+------------------------------------------------------------------+
|                    THE SHADOW ACCESS PROBLEM                      |
+------------------------------------------------------------------+
|                                                                   |
|  Without Access Analyzer:                                        |
|                                                                   |
|  +------------------------+                                       |
|  |     Your AWS Account   |                                       |
|  |                        |                                       |
|  |  +------------------+  |      +------------------+             |
|  |  | S3 Bucket        |  |      | Unknown External |             |
|  |  | "company-data"   |<------->| Account 9999... |             |
|  |  | (policy allows   |  |  ?   | Who is this?    |             |
|  |  |  external access)|  |      | Why access?     |             |
|  |  +------------------+  |      +------------------+             |
|  |                        |                                       |
|  |  You don't know        |                                       |
|  |  this exists!          |                                       |
|  +------------------------+                                       |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  With Access Analyzer:                                           |
|                                                                   |
|  +------------------------+                                       |
|  |     Your AWS Account   |      ALERT!                          |
|  |                        |      +------------------+             |
|  |  +------------------+  |      | FINDING:         |             |
|  |  | S3 Bucket        |  |      | S3 bucket allows |             |
|  |  | "company-data"   |  |----->| access from      |             |
|  |  |                  |  |      | account 9999...  |             |
|  |  +------------------+  |      |                  |             |
|  |                        |      | Actions: Review  |             |
|  |                        |      | or Archive       |             |
|  +------------------------+      +------------------+             |
|                                                                   |
+------------------------------------------------------------------+
```

### Real-World Use Cases

1. **Compliance Auditing**: Prove that sensitive data is not shared externally
2. **Security Reviews**: Identify overly permissive policies before they're exploited
3. **Incident Response**: Quickly find all externally accessible resources
4. **Continuous Monitoring**: Get alerts when new external access is granted

---

## Supported Resource Types

Access Analyzer can analyze the following resource types:

```
+------------------------------------------------------------------+
|                    SUPPORTED RESOURCES                            |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  | Amazon S3        |  | AWS IAM          |  | AWS KMS          | |
|  | Buckets          |  | Roles            |  | Keys             | |
|  | (Bucket Policy,  |  | (Trust Policy)   |  | (Key Policy)     | |
|  |  ACLs)           |  |                  |  |                  | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  | AWS Lambda       |  | Amazon SQS       |  | AWS Secrets      | |
|  | Functions        |  | Queues           |  | Manager          | |
|  | (Resource Policy)|  | (Queue Policy)   |  | (Resource Policy)| |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  | Amazon SNS       |  | Amazon EFS       |  | Amazon ECR       | |
|  | Topics           |  | File Systems     |  | Repositories     | |
|  | (Topic Policy)   |  | (File System     |  | (Repository      | |
|  |                  |  |  Policy)         |  |  Policy)         | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
|  +------------------+  +------------------+                       |
|  | Amazon RDS DB    |  | Amazon RDS DB    |                       |
|  | Snapshots        |  | Cluster Snapshots|                       |
|  | (Sharing)        |  | (Sharing)        |                       |
|  +------------------+  +------------------+                       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Setting Up Access Analyzer

### Step 1: Create an Analyzer

#### Via AWS Console

1. Navigate to **IAM** > **Access Analyzer**
2. Click **Create analyzer**
3. Enter a name for the analyzer
4. Select the zone of trust:
   - **Current account** - Analyzes resources in this account only
   - **Current organization** - Analyzes resources across all accounts in the organization
5. (Optional) Add tags
6. Click **Create analyzer**

#### Via AWS CLI

```bash
# Create an account-level analyzer
aws accessanalyzer create-analyzer \
    --analyzer-name my-account-analyzer \
    --type ACCOUNT \
    --tags Environment=Production,Team=Security

# Create an organization-level analyzer (requires Organizations)
aws accessanalyzer create-analyzer \
    --analyzer-name my-org-analyzer \
    --type ORGANIZATION \
    --tags Environment=Production,Team=Security

# Verify the analyzer was created
aws accessanalyzer list-analyzers
```

### Step 2: Review Findings

```bash
# List all findings
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer

# List only active findings
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --filter '{"status": {"eq": ["ACTIVE"]}}'

# List findings for a specific resource type
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --filter '{"resourceType": {"eq": ["AWS::S3::Bucket"]}}'

# List public access findings
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --filter '{"isPublic": {"eq": ["true"]}}'
```

---

## Understanding Findings

### Finding Structure

```
+------------------------------------------------------------------+
|                    FINDING ANATOMY                                |
+------------------------------------------------------------------+
|                                                                   |
|  {                                                                |
|    "id": "finding-id-123",                                       |
|    "resourceType": "AWS::S3::Bucket",                            |
|    "resource": "arn:aws:s3:::my-bucket",                         |
|    "status": "ACTIVE",                                           |
|    "isPublic": false,                                            |
|    "principal": {                                                 |
|      "AWS": "arn:aws:iam::999888777666:root"                     |
|    },                                                             |
|    "action": ["s3:GetObject", "s3:ListBucket"],                  |
|    "condition": {                                                 |
|      "IpAddress": {                                               |
|        "aws:SourceIp": "203.0.113.0/24"                          |
|      }                                                            |
|    },                                                             |
|    "createdAt": "2024-01-15T10:30:00Z",                          |
|    "analyzedAt": "2024-01-15T10:30:00Z",                         |
|    "updatedAt": "2024-01-15T10:30:00Z"                           |
|  }                                                                |
|                                                                   |
+------------------------------------------------------------------+
```

### Finding Statuses

| Status | Description | Action Required |
|--------|-------------|-----------------|
| **ACTIVE** | Finding is current and needs review | Yes - Investigate |
| **ARCHIVED** | Finding has been reviewed and archived | No |
| **RESOLVED** | The external access has been removed | No |

### Types of External Access

```
+------------------------------------------------------------------+
|                    EXTERNAL ACCESS TYPES                          |
+------------------------------------------------------------------+
|                                                                   |
|  1. PUBLIC ACCESS                                                 |
|     +-------------------+                                         |
|     | Anyone on the     |---> Your Resource                      |
|     | internet (*)      |                                         |
|     +-------------------+                                         |
|     Severity: CRITICAL                                            |
|                                                                   |
|  2. CROSS-ACCOUNT ACCESS                                         |
|     +-------------------+                                         |
|     | Specific AWS      |---> Your Resource                      |
|     | Account           |                                         |
|     +-------------------+                                         |
|     Severity: Depends on account relationship                    |
|                                                                   |
|  3. CROSS-ORGANIZATION ACCESS                                    |
|     +-------------------+                                         |
|     | Account outside   |---> Your Resource                      |
|     | your Organization |                                         |
|     +-------------------+                                         |
|     Severity: HIGH (if unintended)                               |
|                                                                   |
|  4. FEDERATED ACCESS                                             |
|     +-------------------+                                         |
|     | External IdP      |---> Your Resource                      |
|     | users             |                                         |
|     +-------------------+                                         |
|     Severity: Medium (review IdP configuration)                  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Working with Findings

### Investigating a Finding

```bash
# Get detailed information about a finding
aws accessanalyzer get-finding \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --id finding-id-123

# Get the actual resource policy that caused the finding
# For S3 bucket:
aws s3api get-bucket-policy --bucket my-bucket

# For IAM role:
aws iam get-role --role-name MyRole

# For KMS key:
aws kms get-key-policy --key-id alias/my-key --policy-name default
```

### Finding Investigation Workflow

```
+------------------------------------------------------------------+
|                FINDING INVESTIGATION WORKFLOW                      |
+------------------------------------------------------------------+
|                                                                   |
|  1. NEW FINDING DETECTED                                         |
|     |                                                             |
|     v                                                             |
|  2. REVIEW FINDING DETAILS                                       |
|     - Who has access? (principal)                                |
|     - What actions? (action)                                     |
|     - Under what conditions? (condition)                         |
|     - To what resource? (resource)                               |
|     |                                                             |
|     v                                                             |
|  3. DETERMINE INTENT                                             |
|     +------------------------+                                    |
|     |                        |                                    |
|     v                        v                                    |
|  INTENTIONAL             UNINTENTIONAL                           |
|     |                        |                                    |
|     v                        v                                    |
|  4a. DOCUMENT & ARCHIVE   4b. REMEDIATE                          |
|     - Add comment            - Update policy                     |
|     - Create archive rule    - Remove external access            |
|     - Set up monitoring      - Verify change                     |
|     |                        |                                    |
|     v                        v                                    |
|  5. MONITOR               5. VERIFY RESOLVED                     |
|     - Set up alerts          - Finding status changes            |
|     - Regular reviews        - to RESOLVED                       |
|                                                                   |
+------------------------------------------------------------------+
```

### Archiving Findings

```bash
# Archive a single finding
aws accessanalyzer update-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --ids finding-id-123 \
    --status ARCHIVED

# Archive multiple findings
aws accessanalyzer update-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --ids finding-id-123 finding-id-456 finding-id-789 \
    --status ARCHIVED
```

### Creating Archive Rules

Archive rules automatically archive findings that match specific criteria.

```bash
# Create an archive rule for a specific trusted account
aws accessanalyzer create-archive-rule \
    --analyzer-name my-account-analyzer \
    --rule-name trusted-partner-account \
    --filter '{
        "principal.AWS": {"eq": ["arn:aws:iam::999888777666:root"]},
        "resourceType": {"eq": ["AWS::S3::Bucket"]}
    }'

# Create an archive rule for internal organization accounts
aws accessanalyzer create-archive-rule \
    --analyzer-name my-account-analyzer \
    --rule-name internal-accounts \
    --filter '{
        "principal.AWS": {"contains": ["111111111111", "222222222222", "333333333333"]}
    }'

# List archive rules
aws accessanalyzer list-archive-rules \
    --analyzer-name my-account-analyzer

# Delete an archive rule
aws accessanalyzer delete-archive-rule \
    --analyzer-name my-account-analyzer \
    --rule-name trusted-partner-account
```

---

## Remediating Issues

### Remediation by Resource Type

#### S3 Bucket - Remove Public Access

```bash
# View current bucket policy
aws s3api get-bucket-policy --bucket my-bucket

# Delete the bucket policy entirely
aws s3api delete-bucket-policy --bucket my-bucket

# Or update with a more restrictive policy
cat > restricted-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowInternalOnly",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": ["s3:GetObject", "s3:ListBucket"],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket my-bucket --policy file://restricted-policy.json

# Block all public access (recommended)
aws s3api put-public-access-block --bucket my-bucket \
    --public-access-block-configuration \
    'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'
```

#### IAM Role - Update Trust Policy

```bash
# View current trust policy
aws iam get-role --role-name MyRole --query 'Role.AssumeRolePolicyDocument'

# Update with more restrictive trust policy
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "unique-secret-id"
                }
            }
        }
    ]
}
EOF

aws iam update-assume-role-policy \
    --role-name MyRole \
    --policy-document file://trust-policy.json
```

#### KMS Key - Update Key Policy

```bash
# View current key policy
aws kms get-key-policy --key-id alias/my-key --policy-name default

# Update with more restrictive policy
cat > key-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Enable IAM policies",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow specific users",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::123456789012:user/admin",
                    "arn:aws:iam::123456789012:role/ApplicationRole"
                ]
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:GenerateDataKey*"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws kms put-key-policy --key-id alias/my-key --policy-name default --policy file://key-policy.json
```

---

## Policy Validation

Access Analyzer can also validate policies before you deploy them.

### Validating Policies

```bash
# Validate an identity-based policy
aws accessanalyzer validate-policy \
    --policy-type IDENTITY_POLICY \
    --policy-document file://my-policy.json

# Validate a resource-based policy
aws accessanalyzer validate-policy \
    --policy-type RESOURCE_POLICY \
    --policy-document file://resource-policy.json

# Validate a service control policy (SCP)
aws accessanalyzer validate-policy \
    --policy-type SERVICE_CONTROL_POLICY \
    --policy-document file://scp-policy.json
```

### Validation Finding Types

```
+------------------------------------------------------------------+
|                 POLICY VALIDATION FINDINGS                        |
+------------------------------------------------------------------+
|                                                                   |
|  SECURITY WARNINGS:                                              |
|  +------------------------------------------------------------+  |
|  | - Pass role with overly permissive resource               |  |
|  | - Cross-account access without condition                  |  |
|  | - Resource exposure due to wildcard in principal          |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  ERRORS:                                                         |
|  +------------------------------------------------------------+  |
|  | - Invalid action in policy                                 |  |
|  | - Invalid ARN format                                       |  |
|  | - Invalid condition key                                    |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  WARNINGS:                                                       |
|  +------------------------------------------------------------+  |
|  | - Missing version element                                  |  |
|  | - Empty array in action                                    |  |
|  | - Redundant action                                         |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  SUGGESTIONS:                                                    |
|  +------------------------------------------------------------+  |
|  | - Add condition for extra security                         |  |
|  | - Use more specific resource ARN                           |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Policy Generation

Access Analyzer can generate policies based on actual CloudTrail activity.

### Generating Policies from Activity

```bash
# Start policy generation
aws accessanalyzer start-policy-generation \
    --policy-generation-details '{
        "principalArn": "arn:aws:iam::123456789012:role/MyRole"
    }' \
    --cloud-trail-details '{
        "trails": [
            {
                "cloudTrailArn": "arn:aws:cloudtrail:us-east-1:123456789012:trail/management-events",
                "allRegions": true
            }
        ],
        "startTime": "2024-01-01T00:00:00Z",
        "endTime": "2024-01-31T23:59:59Z"
    }'

# Check generation status
aws accessanalyzer get-generated-policy \
    --job-id job-id-from-start-command

# The response includes generated policies based on actual usage
```

### Policy Generation Workflow

```
+------------------------------------------------------------------+
|               POLICY GENERATION WORKFLOW                          |
+------------------------------------------------------------------+
|                                                                   |
|  1. CURRENT STATE                                                |
|     +------------------+                                          |
|     | Role/User with   |                                          |
|     | broad permissions|                                          |
|     | (AdministratorAcc|                                          |
|     |  ess)            |                                          |
|     +------------------+                                          |
|              |                                                    |
|              v                                                    |
|  2. CLOUDTRAIL ANALYSIS (30-90 days)                             |
|     +------------------+                                          |
|     | Access Analyzer  |                                          |
|     | reviews all API  |                                          |
|     | calls made by    |                                          |
|     | the principal    |                                          |
|     +------------------+                                          |
|              |                                                    |
|              v                                                    |
|  3. GENERATED POLICY                                             |
|     +------------------+                                          |
|     | Minimum required |                                          |
|     | permissions      |                                          |
|     | based on actual  |                                          |
|     | activity         |                                          |
|     +------------------+                                          |
|              |                                                    |
|              v                                                    |
|  4. REVIEW & REFINE                                              |
|     - May need additional permissions for occasional tasks       |
|     - Review for any missing permissions                         |
|     - Test thoroughly before replacing current policy            |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Monitoring and Alerting

### CloudWatch Integration

```bash
# Create CloudWatch alarm for new findings
aws cloudwatch put-metric-alarm \
    --alarm-name AccessAnalyzerNewFindings \
    --alarm-description "Alert when Access Analyzer finds new external access" \
    --metric-name ExternalAccessFindingsCreated \
    --namespace AWS/AccessAnalyzer \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:security-alerts \
    --dimensions Name=AnalyzerArn,Value=arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-analyzer
```

### EventBridge Integration

```bash
# Create EventBridge rule for new findings
aws events put-rule \
    --name AccessAnalyzerFindingRule \
    --event-pattern '{
        "source": ["aws.access-analyzer"],
        "detail-type": ["Access Analyzer Finding"],
        "detail": {
            "status": ["ACTIVE"],
            "isPublic": [true]
        }
    }' \
    --state ENABLED

# Add target (e.g., SNS topic)
aws events put-targets \
    --rule AccessAnalyzerFindingRule \
    --targets Id=1,Arn=arn:aws:sns:us-east-1:123456789012:security-alerts
```

### Sample EventBridge Event

```json
{
    "version": "0",
    "id": "12345678-1234-1234-1234-123456789012",
    "detail-type": "Access Analyzer Finding",
    "source": "aws.access-analyzer",
    "account": "123456789012",
    "time": "2024-01-15T10:30:00Z",
    "region": "us-east-1",
    "resources": [
        "arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-analyzer"
    ],
    "detail": {
        "id": "finding-id-123",
        "status": "ACTIVE",
        "resourceType": "AWS::S3::Bucket",
        "resource": "arn:aws:s3:::my-bucket",
        "isPublic": true,
        "principal": "*"
    }
}
```

---

## Hands-On Examples

### Example 1: Finding and Fixing a Public S3 Bucket

```bash
# Step 1: Create an analyzer if you don't have one
aws accessanalyzer create-analyzer \
    --analyzer-name security-analyzer \
    --type ACCOUNT

# Step 2: List all S3 findings
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/security-analyzer \
    --filter '{"resourceType": {"eq": ["AWS::S3::Bucket"]}, "isPublic": {"eq": ["true"]}}'

# Step 3: For each finding, investigate
aws accessanalyzer get-finding \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/security-analyzer \
    --id <finding-id>

# Step 4: Remediate - Block public access
aws s3api put-public-access-block \
    --bucket <bucket-name> \
    --public-access-block-configuration \
    'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'

# Step 5: Verify the finding is resolved (may take a few minutes)
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/security-analyzer \
    --filter '{"id": {"eq": ["<finding-id>"]}}'
```

### Example 2: Identifying Cross-Account Role Access

```bash
# Find all roles with external trust relationships
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/security-analyzer \
    --filter '{"resourceType": {"eq": ["AWS::IAM::Role"]}}'

# Review each finding
aws accessanalyzer get-finding \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/security-analyzer \
    --id <finding-id>

# If the cross-account access is intentional, create an archive rule
aws accessanalyzer create-archive-rule \
    --analyzer-name security-analyzer \
    --rule-name trusted-partner-roles \
    --filter '{
        "resourceType": {"eq": ["AWS::IAM::Role"]},
        "principal.AWS": {"eq": ["arn:aws:iam::999888777666:root"]}
    }'
```

### Example 3: Validating a Policy Before Deployment

```bash
# Create a policy to validate
cat > test-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        }
    ]
}
EOF

# Validate the policy
aws accessanalyzer validate-policy \
    --policy-type IDENTITY_POLICY \
    --policy-document file://test-policy.json

# Review findings and fix issues before deploying
# Common findings:
# - WARNING: Use specific actions instead of s3:*
# - SUGGESTION: Use specific resource ARNs instead of *
```

---

## Best Practices

### Access Analyzer Best Practices

```
+------------------------------------------------------------------+
|              ACCESS ANALYZER BEST PRACTICES                       |
+------------------------------------------------------------------+

1. ENABLE IN EVERY REGION
   - Access Analyzer is regional
   - Create an analyzer in each region you use
   - Consider organization-wide analyzer for complete coverage

2. REVIEW FINDINGS REGULARLY
   - Daily: Check for new critical/public findings
   - Weekly: Review all active findings
   - Monthly: Audit archive rules and resolved findings

3. CREATE MEANINGFUL ARCHIVE RULES
   - Document why access is intentional
   - Use specific criteria to avoid over-archiving
   - Review archive rules quarterly

4. INTEGRATE WITH SECURITY WORKFLOWS
   - Connect to ticketing systems
   - Set up automated alerts
   - Include in incident response procedures

5. USE POLICY VALIDATION IN CI/CD
   - Validate policies before deployment
   - Block deployments with security warnings
   - Automate policy reviews

6. GENERATE LEAST PRIVILEGE POLICIES
   - Use policy generation for existing roles
   - Review and refine generated policies
   - Track policy changes over time

+------------------------------------------------------------------+
```

### Common Mistakes to Avoid

```
+------------------------------------------------------------------+
|                    COMMON MISTAKES                                |
+------------------------------------------------------------------+

MISTAKE 1: Archiving without investigation
+---------------------------------------------------------+
| DON'T: Archive findings to clear the dashboard           |
| DO: Investigate each finding before archiving            |
+---------------------------------------------------------+

MISTAKE 2: Not enabling in all regions
+---------------------------------------------------------+
| DON'T: Only enable in your "main" region                 |
| DO: Enable in all regions where you have resources       |
+---------------------------------------------------------+

MISTAKE 3: Ignoring policy validation findings
+---------------------------------------------------------+
| DON'T: Deploy policies with security warnings            |
| DO: Fix warnings before deployment or document exception |
+---------------------------------------------------------+

MISTAKE 4: Not setting up alerts
+---------------------------------------------------------+
| DON'T: Check the console manually for new findings       |
| DO: Set up EventBridge rules for automatic alerts        |
+---------------------------------------------------------+

MISTAKE 5: Overly broad archive rules
+---------------------------------------------------------+
| DON'T: Archive all findings from a certain type          |
| DO: Use specific criteria (account ID, resource name)    |
+---------------------------------------------------------+

+------------------------------------------------------------------+
```

---

## CLI Quick Reference

```bash
# ANALYZER MANAGEMENT
aws accessanalyzer create-analyzer --analyzer-name NAME --type ACCOUNT|ORGANIZATION
aws accessanalyzer list-analyzers
aws accessanalyzer delete-analyzer --analyzer-name NAME

# FINDINGS
aws accessanalyzer list-findings --analyzer-arn ARN [--filter FILTER]
aws accessanalyzer get-finding --analyzer-arn ARN --id FINDING_ID
aws accessanalyzer update-findings --analyzer-arn ARN --ids ID1 ID2 --status ACTIVE|ARCHIVED

# ARCHIVE RULES
aws accessanalyzer create-archive-rule --analyzer-name NAME --rule-name RULE --filter FILTER
aws accessanalyzer list-archive-rules --analyzer-name NAME
aws accessanalyzer delete-archive-rule --analyzer-name NAME --rule-name RULE

# POLICY VALIDATION
aws accessanalyzer validate-policy --policy-type TYPE --policy-document file://POLICY.json

# POLICY GENERATION
aws accessanalyzer start-policy-generation --policy-generation-details DETAILS --cloud-trail-details TRAIL
aws accessanalyzer get-generated-policy --job-id JOB_ID
```

---

## Summary

| Feature | Purpose | Use When |
|---------|---------|----------|
| **Findings** | Identify external access | Always - continuous monitoring |
| **Archive Rules** | Auto-archive known-good access | After validating trusted relationships |
| **Policy Validation** | Check policies before deployment | In CI/CD pipelines, before IAM changes |
| **Policy Generation** | Create least-privilege policies | Implementing least privilege for existing roles |

---

## Key Takeaways

1. **Enable Access Analyzer in all regions** where you have resources
2. **Review findings regularly** - don't let them accumulate
3. **Document intentional external access** with archive rules and comments
4. **Integrate with your security workflows** using EventBridge
5. **Use policy validation** before deploying new policies
6. **Generate least-privilege policies** from actual CloudTrail activity

---

## Next Steps

Continue to [08-hands-on-lab.md](./08-hands-on-lab.md) for practical exercises covering all IAM concepts.
