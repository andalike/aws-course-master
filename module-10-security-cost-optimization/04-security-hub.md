# AWS Security Hub - Centralized Security Management

## Introduction

AWS Security Hub provides a comprehensive view of your security state across AWS accounts. It aggregates, organizes, and prioritizes security findings from multiple AWS services and partner solutions.

---

## How Security Hub Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY HUB ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FINDING PROVIDERS                SECURITY HUB                ACTIONS    │
│  ┌─────────────────┐            ┌─────────────────┐        ┌─────────┐  │
│  │ GuardDuty       │───┐        │                 │        │ Custom  │  │
│  │ Inspector       │───┤        │   Aggregation   │────────│ Actions │  │
│  │ Macie           │───┤        │                 │        │         │  │
│  │ Firewall Mgr    │───┼───────►│   Normalization │        └────┬────┘  │
│  │ IAM Access      │───┤        │   (ASFF Format) │             │       │
│  │ Config          │───┤        │                 │             ▼       │
│  │ 3rd Party       │───┘        │   Security      │        ┌─────────┐  │
│  └─────────────────┘            │   Standards     │        │ Lambda  │  │
│                                 │                 │        │ EventBr │  │
│  SECURITY STANDARDS             │   Insights      │        │ Ticket  │  │
│  ┌─────────────────┐            │                 │        │ SIEM    │  │
│  │ AWS FSBP        │───────────►│   Dashboard     │        └─────────┘  │
│  │ CIS Benchmark   │            │                 │                      │
│  │ PCI DSS         │            └─────────────────┘                      │
│  │ NIST CSF        │                     │                               │
│  └─────────────────┘                     ▼                               │
│                                   Security Score                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Finding Aggregation** | Collect findings from 50+ sources |
| **Normalization** | Standard format (ASFF) for all findings |
| **Security Standards** | Automated compliance checks |
| **Security Score** | Aggregate metric for security posture |
| **Custom Actions** | Trigger automated responses |
| **Cross-Account** | Centralized multi-account view |

---

## Enabling Security Hub

### Via Console

1. Navigate to Security Hub console
2. Click "Go to Security Hub"
3. Select security standards to enable
4. Click "Enable Security Hub"

### Via CLI

```bash
# Enable Security Hub
aws securityhub enable-security-hub \
  --enable-default-standards

# Enable with specific standards
aws securityhub enable-security-hub \
  --no-enable-default-standards

# Enable specific standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests \
    StandardsArn=arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0 \
    StandardsArn=arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0
```

### Via CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Enable Security Hub with standards

Resources:
  SecurityHub:
    Type: AWS::SecurityHub::Hub
    Properties:
      Tags:
        Environment: Production

  CISStandard:
    Type: AWS::SecurityHub::Standard
    DependsOn: SecurityHub
    Properties:
      StandardsArn: !Sub 'arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0'

  AWSFoundational:
    Type: AWS::SecurityHub::Standard
    DependsOn: SecurityHub
    Properties:
      StandardsArn: !Sub 'arn:aws:securityhub:${AWS::Region}::standards/aws-foundational-security-best-practices/v/1.0.0'
```

### Via Terraform

```hcl
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  depends_on    = [aws_securityhub_account.main]
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0"
}

resource "aws_securityhub_standards_subscription" "aws_foundational" {
  depends_on    = [aws_securityhub_account.main]
  standards_arn = "arn:aws:securityhub:${data.aws_region.current.name}::standards/aws-foundational-security-best-practices/v/1.0.0"
}
```

---

## Security Standards

### Available Standards

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY STANDARDS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AWS FOUNDATIONAL SECURITY BEST PRACTICES (FSBP)                        │
│  ├── 200+ controls                                                      │
│  ├── AWS-specific best practices                                        │
│  ├── Covers all major AWS services                                      │
│  └── Recommended as baseline                                            │
│                                                                          │
│  CIS AWS FOUNDATIONS BENCHMARK                                          │
│  ├── 50+ controls                                                       │
│  ├── Industry-standard security                                         │
│  ├── Levels 1 and 2                                                     │
│  └── Widely recognized certification                                    │
│                                                                          │
│  PCI DSS v3.2.1                                                         │
│  ├── Payment Card Industry standard                                     │
│  ├── Controls relevant to PCI compliance                                │
│  └── Required for card payment processing                               │
│                                                                          │
│  NIST CYBERSECURITY FRAMEWORK                                           │
│  ├── Identify, Protect, Detect, Respond, Recover                       │
│  ├── Comprehensive cybersecurity approach                               │
│  └── US federal standard                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Control Categories (AWS FSBP)

| Category | Example Controls |
|----------|-----------------|
| **IAM** | MFA enabled, no root access keys, password policy |
| **S3** | Block public access, encryption, logging |
| **EC2** | EBS encryption, no public IPs, IMDSv2 |
| **RDS** | Encryption, no public access, backups |
| **Lambda** | No sensitive env vars, VPC configuration |
| **CloudTrail** | Enabled, encrypted, multi-region |
| **VPC** | Flow logs, no default SG rules |
| **KMS** | Key rotation, proper policies |

### Control Status

```
┌─────────────┬────────────────────────────────────────────────────────┐
│  Status     │  Description                                           │
├─────────────┼────────────────────────────────────────────────────────┤
│  PASSED     │  Resource complies with the control                    │
│  FAILED     │  Resource does not comply                              │
│  WARNING    │  Insufficient data to determine                        │
│  NOT_AVAILABLE │  Control not applicable in this region             │
│  NO_DATA    │  No resources to evaluate                              │
└─────────────┴────────────────────────────────────────────────────────┘
```

---

## Finding Management

### AWS Security Finding Format (ASFF)

```json
{
  "SchemaVersion": "2018-10-08",
  "Id": "arn:aws:securityhub:us-east-1:123456789012:subscription/aws-foundational-security-best-practices/v/1.0.0/S3.1/finding/abc123",
  "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
  "GeneratorId": "aws-foundational-security-best-practices/v/1.0.0/S3.1",
  "AwsAccountId": "123456789012",
  "Types": [
    "Software and Configuration Checks/Industry and Regulatory Standards"
  ],
  "CreatedAt": "2024-01-15T10:00:00.000Z",
  "UpdatedAt": "2024-01-15T10:00:00.000Z",
  "Severity": {
    "Label": "HIGH",
    "Normalized": 70
  },
  "Title": "S3.1 S3 Block Public Access setting should be enabled",
  "Description": "This AWS control checks whether the following public access block settings are configured at the account level...",
  "Remediation": {
    "Recommendation": {
      "Text": "For information on how to correct this issue, consult the AWS Security Hub documentation.",
      "Url": "https://docs.aws.amazon.com/..."
    }
  },
  "ProductFields": {
    "StandardsArn": "arn:aws:securityhub:::standards/aws-foundational-security-best-practices/v/1.0.0",
    "StandardsControlArn": "arn:aws:securityhub:us-east-1:123456789012:control/aws-foundational-security-best-practices/v/1.0.0/S3.1"
  },
  "Resources": [
    {
      "Type": "AwsAccount",
      "Id": "AWS::::Account:123456789012",
      "Region": "us-east-1"
    }
  ],
  "Compliance": {
    "Status": "FAILED"
  },
  "WorkflowState": "NEW",
  "Workflow": {
    "Status": "NEW"
  },
  "RecordState": "ACTIVE"
}
```

### Finding Severity Levels

| Severity | Score | Description | SLA |
|----------|-------|-------------|-----|
| CRITICAL | 90-100 | Immediate threat | Immediate |
| HIGH | 70-89 | Significant risk | 24 hours |
| MEDIUM | 40-69 | Moderate risk | 7 days |
| LOW | 1-39 | Minor issues | 30 days |
| INFORMATIONAL | 0 | Best practice | Track |

### Workflow Status

```
NEW ──────► NOTIFIED ──────► SUPPRESSED
  │              │               ▲
  │              │               │
  └──────► RESOLVED ◄────────────┘
```

---

## Insights

### Built-in Insights

Security Hub provides managed insights for common queries:

| Insight | Description |
|---------|-------------|
| AWS resources with most findings | Top resources by finding count |
| S3 buckets with public access | Public S3 bucket findings |
| EC2 instances with public IPs | Exposed EC2 instances |
| IAM users with stale credentials | Unused access keys |
| Resources without required tags | Tag compliance |

### Custom Insights

```bash
# Create custom insight
aws securityhub create-insight \
  --name "Critical Findings Last 7 Days" \
  --filters '{
    "SeverityLabel": [{"Value": "CRITICAL", "Comparison": "EQUALS"}],
    "CreatedAt": [{"DateRange": {"Value": 7, "Unit": "DAYS"}}],
    "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]
  }' \
  --group-by-attribute "ResourceType"
```

### Useful Custom Insight Examples

```python
# Python SDK to create insights

import boto3

securityhub = boto3.client('securityhub')

# Insight: Failed controls by service
securityhub.create_insight(
    Name='Failed Controls by AWS Service',
    Filters={
        'ComplianceStatus': [{'Value': 'FAILED', 'Comparison': 'EQUALS'}],
        'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
    },
    GroupByAttribute='ProductFields.ControlId'
)

# Insight: GuardDuty high severity findings
securityhub.create_insight(
    Name='GuardDuty High Severity',
    Filters={
        'ProductName': [{'Value': 'GuardDuty', 'Comparison': 'EQUALS'}],
        'SeverityLabel': [
            {'Value': 'HIGH', 'Comparison': 'EQUALS'},
            {'Value': 'CRITICAL', 'Comparison': 'EQUALS'}
        ],
        'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
    },
    GroupByAttribute='Type'
)

# Insight: Unresolved findings by account
securityhub.create_insight(
    Name='Unresolved by Account',
    Filters={
        'WorkflowStatus': [{'Value': 'NEW', 'Comparison': 'EQUALS'}],
        'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
    },
    GroupByAttribute='AwsAccountId'
)
```

---

## Integrations

### AWS Service Integrations

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY HUB INTEGRATIONS                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AWS NATIVE INTEGRATIONS (Auto-enabled)                                 │
│  ├── Amazon GuardDuty                                                   │
│  ├── Amazon Inspector                                                   │
│  ├── Amazon Macie                                                       │
│  ├── AWS Config                                                         │
│  ├── AWS Firewall Manager                                               │
│  ├── IAM Access Analyzer                                                │
│  ├── AWS Systems Manager Patch Manager                                  │
│  └── AWS Health                                                         │
│                                                                          │
│  3RD PARTY INTEGRATIONS (Marketplace)                                   │
│  ├── CrowdStrike Falcon                                                 │
│  ├── Palo Alto Networks                                                 │
│  ├── Splunk                                                             │
│  ├── Sumo Logic                                                         │
│  ├── Rapid7                                                             │
│  ├── Qualys                                                             │
│  └── Trend Micro                                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Enable Integration

```bash
# List available integrations
aws securityhub describe-products

# Enable an integration
aws securityhub enable-import-findings-for-product \
  --product-arn "arn:aws:securityhub:us-east-1::product/aws/guardduty"
```

---

## Multi-Account Management

### Organization Setup

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MULTI-ACCOUNT SECURITY HUB                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌──────────────────────────┐                         │
│                    │   Admin Account          │                         │
│                    │   (Delegated Admin)      │                         │
│                    │                          │                         │
│                    │   ● Aggregated findings  │                         │
│                    │   ● Central dashboard    │                         │
│                    │   ● Cross-account view   │                         │
│                    └───────────┬──────────────┘                         │
│                                │                                        │
│            ┌───────────────────┼───────────────────┐                    │
│            │                   │                   │                    │
│            ▼                   ▼                   ▼                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ Member Account  │ │ Member Account  │ │ Member Account  │           │
│  │ Production      │ │ Development     │ │ Staging         │           │
│  │                 │ │                 │ │                 │           │
│  │ Local findings  │ │ Local findings  │ │ Local findings  │           │
│  │ sent to admin   │ │ sent to admin   │ │ sent to admin   │           │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Configure Delegated Administrator

```bash
# In management account, designate admin
aws securityhub enable-organization-admin-account \
  --admin-account-id 123456789012

# In admin account, enable auto-enable for members
aws securityhub update-organization-configuration \
  --auto-enable

# Configure which standards to auto-enable
aws securityhub update-organization-configuration \
  --auto-enable \
  --auto-enable-standards SECURITY_CONTROL
```

### Cross-Region Aggregation

```bash
# Create finding aggregator
aws securityhub create-finding-aggregator \
  --region-linking-mode ALL_REGIONS

# Or specify regions
aws securityhub create-finding-aggregator \
  --region-linking-mode SPECIFIED_REGIONS \
  --regions us-east-1 us-west-2 eu-west-1
```

---

## Automated Remediation

### Custom Actions with EventBridge

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED REMEDIATION FLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Failed Control Finding                                              │
│     └── S3 bucket without encryption                                    │
│                                                                          │
│  2. EventBridge Rule Triggers                                           │
│     └── Pattern matches control ID and FAILED status                    │
│                                                                          │
│  3. Lambda Remediation                                                  │
│     └── Enables S3 bucket encryption                                    │
│                                                                          │
│  4. Finding Updated                                                     │
│     └── Status changes to RESOLVED                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### EventBridge Rule for Security Hub

```json
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported"],
  "detail": {
    "findings": {
      "Compliance": {
        "Status": ["FAILED"]
      },
      "Severity": {
        "Label": ["CRITICAL", "HIGH"]
      },
      "Workflow": {
        "Status": ["NEW"]
      },
      "RecordState": ["ACTIVE"]
    }
  }
}
```

### Remediation Lambda Examples

```python
import boto3
import json

def lambda_handler(event, context):
    """
    Automated remediation for Security Hub findings
    """
    findings = event['detail']['findings']

    for finding in findings:
        control_id = finding.get('ProductFields', {}).get('ControlId', '')

        # Route to appropriate remediation
        if control_id == 'S3.4':
            remediate_s3_encryption(finding)
        elif control_id == 'S3.1':
            remediate_s3_public_access(finding)
        elif control_id == 'EC2.2':
            remediate_default_sg(finding)
        elif control_id == 'IAM.3':
            remediate_inactive_keys(finding)

    return {'statusCode': 200}

def remediate_s3_encryption(finding):
    """
    S3.4 - S3 buckets should have server-side encryption enabled
    """
    s3 = boto3.client('s3')

    # Get bucket name from finding
    for resource in finding['Resources']:
        if resource['Type'] == 'AwsS3Bucket':
            bucket_name = resource['Id'].split(':')[-1]

            # Enable default encryption
            s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )

            # Update finding status
            update_finding_status(finding, 'RESOLVED')

def remediate_s3_public_access(finding):
    """
    S3.1 - S3 Block Public Access setting should be enabled
    """
    s3_control = boto3.client('s3control')

    account_id = finding['AwsAccountId']

    # Enable account-level block public access
    s3_control.put_public_access_block(
        AccountId=account_id,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

    update_finding_status(finding, 'RESOLVED')

def remediate_default_sg(finding):
    """
    EC2.2 - The VPC default security group should not allow inbound or outbound traffic
    """
    ec2 = boto3.client('ec2')

    for resource in finding['Resources']:
        if resource['Type'] == 'AwsEc2SecurityGroup':
            sg_id = resource['Details']['AwsEc2SecurityGroup']['GroupId']

            # Revoke all inbound rules
            sg_details = ec2.describe_security_groups(GroupIds=[sg_id])
            for permission in sg_details['SecurityGroups'][0]['IpPermissions']:
                ec2.revoke_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[permission]
                )

            # Revoke all outbound rules
            for permission in sg_details['SecurityGroups'][0]['IpPermissionsEgress']:
                ec2.revoke_security_group_egress(
                    GroupId=sg_id,
                    IpPermissions=[permission]
                )

    update_finding_status(finding, 'RESOLVED')

def remediate_inactive_keys(finding):
    """
    IAM.3 - IAM users' access keys should be rotated every 90 days
    """
    iam = boto3.client('iam')

    for resource in finding['Resources']:
        if resource['Type'] == 'AwsIamUser':
            user_name = resource['Details']['AwsIamUser']['UserName']

            # Deactivate old access keys
            keys = iam.list_access_keys(UserName=user_name)
            for key in keys['AccessKeyMetadata']:
                iam.update_access_key(
                    UserName=user_name,
                    AccessKeyId=key['AccessKeyId'],
                    Status='Inactive'
                )

    update_finding_status(finding, 'NOTIFIED')  # Human action needed

def update_finding_status(finding, status):
    """
    Update finding workflow status
    """
    securityhub = boto3.client('securityhub')

    securityhub.batch_update_findings(
        FindingIdentifiers=[{
            'Id': finding['Id'],
            'ProductArn': finding['ProductArn']
        }],
        Workflow={'Status': status}
    )
```

### Terraform for Automated Remediation

```hcl
# EventBridge rule for Security Hub findings
resource "aws_cloudwatch_event_rule" "securityhub_remediation" {
  name        = "securityhub-auto-remediate"
  description = "Trigger remediation for Security Hub findings"

  event_pattern = jsonencode({
    source      = ["aws.securityhub"]
    detail-type = ["Security Hub Findings - Imported"]
    detail = {
      findings = {
        Compliance = {
          Status = ["FAILED"]
        }
        ProductFields = {
          ControlId = ["S3.4", "S3.1", "EC2.2"]
        }
      }
    }
  })
}

# Lambda target
resource "aws_cloudwatch_event_target" "remediation_lambda" {
  rule      = aws_cloudwatch_event_rule.securityhub_remediation.name
  target_id = "SecurityHubRemediation"
  arn       = aws_lambda_function.remediation.arn
}
```

---

## Custom Actions

### Create Custom Action

```bash
# Create a custom action
aws securityhub create-action-target \
  --name "SendToSlack" \
  --description "Send finding to Slack channel" \
  --id "SendToSlack"

# Create another custom action
aws securityhub create-action-target \
  --name "CreateJiraTicket" \
  --description "Create Jira ticket for finding" \
  --id "CreateJiraTicket"
```

### Custom Action EventBridge Rule

```json
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Custom Action"],
  "detail": {
    "actionName": ["SendToSlack"]
  }
}
```

---

## Security Score

### Understanding the Score

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SECURITY SCORE CALCULATION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Score = (Passed Controls / Total Enabled Controls) * 100               │
│                                                                          │
│  Example:                                                               │
│  ├── Total Controls: 200                                                │
│  ├── Passed: 170                                                        │
│  ├── Failed: 25                                                         │
│  └── Not Applicable: 5                                                  │
│                                                                          │
│  Score = (170 / 195) * 100 = 87%                                        │
│                                                                          │
│  SCORE RANGES:                                                          │
│  ├── 90-100%: Excellent                                                 │
│  ├── 70-89%: Good                                                       │
│  ├── 50-69%: Needs Improvement                                          │
│  └── <50%: Critical                                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Improving Security Score

| Priority | Focus Area | Impact |
|----------|------------|--------|
| 1 | Fix CRITICAL severity findings | High |
| 2 | Fix HIGH severity findings | High |
| 3 | Address most common failed controls | Medium |
| 4 | Disable controls not applicable | Score |
| 5 | Enable automation for common issues | Long-term |

---

## Best Practices

### 1. Enable All Regions

```bash
# Enable Security Hub in all regions
for region in $(aws ec2 describe-regions --query 'Regions[].RegionName' --output text); do
  echo "Enabling Security Hub in $region"
  aws securityhub enable-security-hub --enable-default-standards --region $region
done
```

### 2. Use Finding Aggregation

```bash
# Create cross-region aggregator
aws securityhub create-finding-aggregator \
  --region-linking-mode ALL_REGIONS
```

### 3. Implement Automated Remediation

- Start with high-impact, low-risk remediations
- Test in non-production first
- Log all automated actions
- Have rollback procedures

### 4. Regular Reviews

```
Daily:
├── Review new CRITICAL/HIGH findings
└── Check automated remediation logs

Weekly:
├── Review security score trends
├── Analyze top failed controls
└── Review suppressed findings

Monthly:
├── Audit custom actions
├── Review insight trends
└── Update automation rules

Quarterly:
├── Review enabled standards
├── Assess new AWS controls
└── Update documentation
```

### 5. Suppress Appropriately

```bash
# Suppress a finding with documentation
aws securityhub batch-update-findings \
  --finding-identifiers '[
    {
      "Id": "arn:aws:securityhub:...",
      "ProductArn": "arn:aws:securityhub:..."
    }
  ]' \
  --workflow '{"Status": "SUPPRESSED"}' \
  --note '{"Text": "False positive - Development environment", "UpdatedBy": "security-team"}'
```

---

## Cost Considerations

### Pricing

| Component | Cost |
|-----------|------|
| Security Checks | $0.0010 per check per account per region |
| Finding Ingestion Events | $0.00003 per finding ingestion event |
| First 10,000 events/month | Free |

### Cost Optimization

- Disable unused security standards
- Use finding aggregation (pay once per finding)
- Automate remediation to reduce recurring checks
- Review and disable controls not applicable to your environment

---

## Key Takeaways

1. **Centralize security** - Aggregate all findings in Security Hub
2. **Enable standards** - Use FSBP as baseline, add CIS/PCI as needed
3. **Track security score** - Monitor and improve over time
4. **Automate remediation** - Reduce manual effort and response time
5. **Multi-account** - Use Organizations for centralized management
6. **Cross-region** - Aggregate findings from all regions
7. **Integrate** - Connect with SIEM and ticketing systems

---

## Next Steps

Continue to [05-waf-shield.md](05-waf-shield.md) to learn about protecting web applications from attacks.
