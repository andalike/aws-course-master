# Amazon GuardDuty - Intelligent Threat Detection

## Introduction

Amazon GuardDuty is a threat detection service that continuously monitors your AWS accounts and workloads for malicious activity. It uses machine learning, anomaly detection, and integrated threat intelligence to identify threats.

---

## How GuardDuty Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GUARDDUTY ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DATA SOURCES                    ANALYSIS                    OUTPUT      │
│  ┌──────────────┐              ┌──────────────┐          ┌───────────┐  │
│  │ VPC Flow Logs│──────┐       │              │          │           │  │
│  └──────────────┘      │       │  Machine     │          │  Findings │  │
│  ┌──────────────┐      │       │  Learning    │          │           │  │
│  │ DNS Logs     │──────┼──────►│              │─────────►│  ● Low    │  │
│  └──────────────┘      │       │  Anomaly     │          │  ● Medium │  │
│  ┌──────────────┐      │       │  Detection   │          │  ● High   │  │
│  │ CloudTrail   │──────┤       │              │          │           │  │
│  └──────────────┘      │       │  Threat      │          └───────────┘  │
│  ┌──────────────┐      │       │  Intelligence│               │         │
│  │ S3 Data      │──────┤       │              │               ▼         │
│  │ Events       │      │       └──────────────┘          ┌───────────┐  │
│  └──────────────┘      │                                 │EventBridge│  │
│  ┌──────────────┐      │                                 │  Lambda   │  │
│  │ EKS Audit    │──────┘                                 │  SNS      │  │
│  │ Logs         │                                        │  Sec Hub  │  │
│  └──────────────┘                                        └───────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Sources Explained

| Data Source | What It Analyzes | Threats Detected |
|-------------|------------------|------------------|
| **VPC Flow Logs** | Network traffic metadata | Port scanning, data exfiltration, crypto mining |
| **DNS Logs** | DNS query patterns | Malware callbacks, crypto mining pools, C&C servers |
| **CloudTrail Events** | API calls | Credential abuse, unusual API patterns |
| **S3 Data Events** | S3 operations | Unusual bucket access, data theft |
| **EKS Audit Logs** | Kubernetes API | Container compromise, privilege escalation |

---

## Enabling GuardDuty

### Via Console

1. Navigate to GuardDuty console
2. Click "Get Started"
3. Click "Enable GuardDuty"

### Via CLI

```bash
# Enable GuardDuty
aws guardduty create-detector --enable

# Get detector ID
aws guardduty list-detectors

# Check detector status
aws guardduty get-detector --detector-id <detector-id>
```

### Via CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Enable GuardDuty

Resources:
  GuardDutyDetector:
    Type: AWS::GuardDuty::Detector
    Properties:
      Enable: true
      DataSources:
        S3Logs:
          Enable: true
        Kubernetes:
          AuditLogs:
            Enable: true
        MalwareProtection:
          ScanEc2InstanceWithFindings:
            EbsVolumes: true
      FindingPublishingFrequency: FIFTEEN_MINUTES
      Tags:
        - Key: Environment
          Value: Production
```

### Via Terraform

```hcl
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  finding_publishing_frequency = "FIFTEEN_MINUTES"

  tags = {
    Environment = "Production"
  }
}
```

---

## Finding Types

### Finding Categories

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GUARDDUTY FINDING TYPES                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  RECONNAISSANCE                                                         │
│  ├── Recon:EC2/PortProbeUnprotectedPort                                │
│  ├── Recon:EC2/Portscan                                                │
│  └── Discovery:S3/TorIPCaller                                          │
│                                                                          │
│  INSTANCE COMPROMISE                                                    │
│  ├── Backdoor:EC2/C&CActivity.B                                        │
│  ├── CryptoCurrency:EC2/BitcoinTool.B                                  │
│  ├── Trojan:EC2/BlackholeTraffic                                       │
│  ├── UnauthorizedAccess:EC2/TorClient                                  │
│  └── Behavior:EC2/NetworkPortUnusual                                   │
│                                                                          │
│  ACCOUNT COMPROMISE                                                     │
│  ├── UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration         │
│  ├── PenTest:IAMUser/KaliLinux                                         │
│  ├── Stealth:IAMUser/CloudTrailLoggingDisabled                         │
│  └── Policy:IAMUser/RootCredentialUsage                                │
│                                                                          │
│  BUCKET COMPROMISE                                                      │
│  ├── Policy:S3/BucketPublicAccessGranted                               │
│  ├── UnauthorizedAccess:S3/TorIPCaller                                 │
│  └── Exfiltration:S3/ObjectRead.Unusual                                │
│                                                                          │
│  KUBERNETES THREATS                                                     │
│  ├── PrivilegeEscalation:Kubernetes/PrivilegedContainer                │
│  ├── Persistence:Kubernetes/ContainerWithSensitiveMount                │
│  └── Execution:Kubernetes/ExecInKubeSystemPod                          │
│                                                                          │
│  MALWARE                                                                │
│  ├── Execution:EC2/MaliciousFile                                       │
│  └── Execution:ECS/MaliciousFile                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Finding Severity Levels

| Severity | Range | Action Required |
|----------|-------|-----------------|
| **Critical** | N/A | Immediate (used for malware) |
| **High** | 7.0-8.9 | Investigate immediately |
| **Medium** | 4.0-6.9 | Investigate within 24 hours |
| **Low** | 0.1-3.9 | Review and track |

### Example Findings

#### High Severity: Cryptocurrency Mining

```json
{
  "type": "CryptoCurrency:EC2/BitcoinTool.B!DNS",
  "severity": 8,
  "resource": {
    "resourceType": "Instance",
    "instanceDetails": {
      "instanceId": "i-0abc12345def67890",
      "instanceType": "c5.4xlarge",
      "launchTime": "2024-01-15T10:30:00Z"
    }
  },
  "service": {
    "action": {
      "actionType": "DNS_REQUEST",
      "dnsRequestAction": {
        "domain": "pool.minergate.com"
      }
    }
  },
  "description": "EC2 instance is querying a domain associated with cryptocurrency mining."
}
```

#### Medium Severity: Unusual API Activity

```json
{
  "type": "UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B",
  "severity": 5,
  "resource": {
    "resourceType": "AccessKey",
    "accessKeyDetails": {
      "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
      "userName": "admin-user"
    }
  },
  "service": {
    "action": {
      "actionType": "AWS_API_CALL",
      "remoteIpDetails": {
        "country": {
          "countryName": "Russia"
        }
      }
    }
  },
  "description": "A console login was observed from an unusual location."
}
```

---

## Suppression Rules

Suppress findings that are known false positives or expected behavior.

### Creating Suppression Rules

#### Via Console

1. Navigate to GuardDuty > Findings
2. Select a finding to suppress
3. Click "Suppress findings"
4. Define filter criteria
5. Name the suppression rule

#### Via CLI

```bash
# Create a suppression rule (filter)
aws guardduty create-filter \
  --detector-id <detector-id> \
  --name "SuppressInternalPenTest" \
  --action ARCHIVE \
  --finding-criteria '{
    "Criterion": {
      "type": {
        "Eq": ["Recon:EC2/Portscan"]
      },
      "resource.instanceDetails.tags.value": {
        "Eq": ["pen-test-instance"]
      }
    }
  }'
```

### Common Suppression Scenarios

```yaml
# Suppress findings for security scanners
Scenario: Internal vulnerability scanner
Filter:
  type: Recon:EC2/Portscan
  resource.instanceDetails.networkInterfaces.privateIpAddress:
    Eq: ["10.0.1.100"]  # Scanner IP

# Suppress findings for approved tools
Scenario: Approved penetration testing
Filter:
  type:
    Eq: ["PenTest:IAMUser/KaliLinux"]
  resource.accessKeyDetails.userName:
    Eq: ["security-team-pentest"]

# Suppress findings for known services
Scenario: Expected Tor access for research
Filter:
  type: UnauthorizedAccess:EC2/TorClient
  resource.instanceDetails.tags.value:
    Eq: ["tor-research-node"]
```

### Suppression Best Practices

1. **Document reasons** - Keep records of why findings are suppressed
2. **Review regularly** - Audit suppression rules quarterly
3. **Be specific** - Use narrow criteria to avoid hiding real threats
4. **Time-box** - Consider expiration for temporary suppressions
5. **Alert on rule creation** - Monitor when new suppressions are added

---

## Multi-Account Management

### Organization Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GUARDDUTY MULTI-ACCOUNT                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌──────────────────────────┐                         │
│                    │   Delegated Admin        │                         │
│                    │   (Security Account)     │                         │
│                    │   ● Centralized view     │                         │
│                    │   ● Manage all members   │                         │
│                    │   ● Create suppressions  │                         │
│                    └───────────┬──────────────┘                         │
│                                │                                        │
│            ┌───────────────────┼───────────────────┐                    │
│            │                   │                   │                    │
│            ▼                   ▼                   ▼                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ Member Account  │ │ Member Account  │ │ Member Account  │           │
│  │ (Production)    │ │ (Development)   │ │ (Staging)       │           │
│  │ ● Local detect  │ │ ● Local detect  │ │ ● Local detect  │           │
│  │ ● Findings sent │ │ ● Findings sent │ │ ● Findings sent │           │
│  │   to admin      │ │   to admin      │ │   to admin      │           │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Setting Up Delegated Administrator

```bash
# In the management account, designate a delegated admin
aws guardduty enable-organization-admin-account \
  --admin-account-id 123456789012

# In the delegated admin account, enable auto-enable for new members
aws guardduty update-organization-configuration \
  --detector-id <detector-id> \
  --auto-enable

# Create member accounts (if not using Organizations)
aws guardduty create-members \
  --detector-id <detector-id> \
  --account-details AccountId=111111111111,Email=member@example.com
```

### CloudFormation StackSet for Multi-Account

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Enable GuardDuty in member accounts

Parameters:
  AdminAccountId:
    Type: String
    Description: GuardDuty admin account ID

Resources:
  GuardDutyDetector:
    Type: AWS::GuardDuty::Detector
    Properties:
      Enable: true
      DataSources:
        S3Logs:
          Enable: true
        Kubernetes:
          AuditLogs:
            Enable: true

  GuardDutyMember:
    Type: AWS::GuardDuty::Member
    DependsOn: GuardDutyDetector
    Properties:
      DetectorId: !Ref GuardDutyDetector
      Email: !Sub "security@${AWS::AccountId}.example.com"
      MemberId: !Ref AdminAccountId
      Status: Invited
```

---

## Automated Response

### EventBridge Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTOMATED RESPONSE FLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  GuardDuty ──► EventBridge Rule ──► Lambda Function                     │
│      │               │                    │                              │
│      │               │                    ├──► Isolate EC2 instance     │
│      │               │                    ├──► Disable IAM credentials  │
│      │               │                    ├──► Block IP in WAF          │
│      │               │                    └──► Send Slack notification  │
│      │               │                                                   │
│      │               └──► SNS Topic ──► Email/PagerDuty                 │
│      │                                                                   │
│      └──► Security Hub (for aggregation)                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### EventBridge Rule

```json
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"],
  "detail": {
    "severity": [
      { "numeric": [">=", 7] }
    ]
  }
}
```

### Lambda Remediation Function

```python
import boto3
import json
import os

def lambda_handler(event, context):
    """
    Automated response to GuardDuty findings
    """
    finding = event['detail']
    finding_type = finding['type']
    severity = finding['severity']

    # Route to appropriate handler
    if 'EC2' in finding_type:
        return handle_ec2_finding(finding)
    elif 'IAMUser' in finding_type:
        return handle_iam_finding(finding)
    elif 'S3' in finding_type:
        return handle_s3_finding(finding)

    return {'statusCode': 200, 'body': 'No action taken'}

def handle_ec2_finding(finding):
    """
    Handle EC2-related findings
    """
    ec2 = boto3.client('ec2')

    instance_id = finding['resource']['instanceDetails']['instanceId']
    finding_type = finding['type']

    # For cryptocurrency mining, isolate the instance
    if 'CryptoCurrency' in finding_type:
        # Create isolation security group
        vpc_id = finding['resource']['instanceDetails']['networkInterfaces'][0]['vpcId']

        # Check if isolation SG exists
        try:
            response = ec2.describe_security_groups(
                Filters=[
                    {'Name': 'group-name', 'Values': ['GuardDuty-Isolation']},
                    {'Name': 'vpc-id', 'Values': [vpc_id]}
                ]
            )

            if response['SecurityGroups']:
                isolation_sg = response['SecurityGroups'][0]['GroupId']
            else:
                # Create isolation security group
                sg_response = ec2.create_security_group(
                    GroupName='GuardDuty-Isolation',
                    Description='Isolation SG for compromised instances',
                    VpcId=vpc_id
                )
                isolation_sg = sg_response['GroupId']
        except Exception as e:
            print(f"Error with security group: {e}")
            return {'statusCode': 500, 'body': str(e)}

        # Apply isolation security group
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[isolation_sg]
        )

        # Tag the instance
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[
                {'Key': 'GuardDuty-Isolated', 'Value': 'true'},
                {'Key': 'GuardDuty-Finding', 'Value': finding_type}
            ]
        )

        # Send notification
        notify_security_team(finding, 'Instance isolated')

        return {
            'statusCode': 200,
            'body': f'Instance {instance_id} isolated'
        }

    return {'statusCode': 200, 'body': 'No action taken'}

def handle_iam_finding(finding):
    """
    Handle IAM-related findings
    """
    iam = boto3.client('iam')

    access_key_id = finding['resource']['accessKeyDetails']['accessKeyId']
    user_name = finding['resource']['accessKeyDetails']['userName']
    finding_type = finding['type']

    # For credential exfiltration, disable the access key
    if 'CredentialExfiltration' in finding_type or 'ConsoleLoginSuccess.B' in finding_type:
        iam.update_access_key(
            UserName=user_name,
            AccessKeyId=access_key_id,
            Status='Inactive'
        )

        notify_security_team(finding, f'Access key {access_key_id} disabled')

        return {
            'statusCode': 200,
            'body': f'Access key {access_key_id} disabled'
        }

    return {'statusCode': 200, 'body': 'No action taken'}

def handle_s3_finding(finding):
    """
    Handle S3-related findings
    """
    s3 = boto3.client('s3')

    bucket_name = finding['resource']['s3BucketDetails'][0]['name']
    finding_type = finding['type']

    # For public access, block it
    if 'BucketPublicAccessGranted' in finding_type:
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )

        notify_security_team(finding, f'Bucket {bucket_name} public access blocked')

        return {
            'statusCode': 200,
            'body': f'Bucket {bucket_name} public access blocked'
        }

    return {'statusCode': 200, 'body': 'No action taken'}

def notify_security_team(finding, action_taken):
    """
    Send notification to security team
    """
    sns = boto3.client('sns')

    message = {
        'finding_type': finding['type'],
        'severity': finding['severity'],
        'region': finding['region'],
        'action_taken': action_taken,
        'finding_id': finding['id']
    }

    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject=f"GuardDuty Alert: {finding['type']}",
        Message=json.dumps(message, indent=2)
    )
```

### Terraform for Automated Response

```hcl
# EventBridge rule for GuardDuty findings
resource "aws_cloudwatch_event_rule" "guardduty_findings" {
  name        = "guardduty-high-severity"
  description = "Capture high severity GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [{ numeric = [">=", 7] }]
    }
  })
}

# Lambda target
resource "aws_cloudwatch_event_target" "guardduty_lambda" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "GuardDutyRemediation"
  arn       = aws_lambda_function.guardduty_remediation.arn
}

# Lambda permission
resource "aws_lambda_permission" "guardduty" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.guardduty_remediation.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.guardduty_findings.arn
}

# SNS topic for notifications
resource "aws_sns_topic" "security_alerts" {
  name = "guardduty-security-alerts"
}

# SNS target for email notifications
resource "aws_cloudwatch_event_target" "guardduty_sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_findings.name
  target_id = "GuardDutySNS"
  arn       = aws_sns_topic.security_alerts.arn
}
```

---

## Threat Intelligence

### Trusted IP Lists

Prevent findings for known good IPs:

```bash
# Upload trusted IP list to S3
echo "10.0.0.0/8" > trusted-ips.txt
echo "192.168.1.0/24" >> trusted-ips.txt
aws s3 cp trusted-ips.txt s3://my-security-bucket/guardduty/

# Create the trusted IP list
aws guardduty create-ip-set \
  --detector-id <detector-id> \
  --name "InternalNetworks" \
  --format TXT \
  --location s3://my-security-bucket/guardduty/trusted-ips.txt \
  --activate
```

### Threat Intel Lists

Add custom threat indicators:

```bash
# Upload threat IP list to S3
echo "203.0.113.50" > threat-ips.txt
echo "198.51.100.100" >> threat-ips.txt
aws s3 cp threat-ips.txt s3://my-security-bucket/guardduty/

# Create the threat intel list
aws guardduty create-threat-intel-set \
  --detector-id <detector-id> \
  --name "CustomThreatIntel" \
  --format TXT \
  --location s3://my-security-bucket/guardduty/threat-ips.txt \
  --activate
```

---

## Cost Optimization

### GuardDuty Pricing

| Data Source | Price |
|-------------|-------|
| CloudTrail Events | $4.00 per 1M events (first 500M), then $0.80 |
| VPC Flow Logs | $1.00 per GB (first 500GB), then $0.25 |
| DNS Logs | $1.00 per 1M queries (first 500M), then $0.25 |
| S3 Events | $0.80 per 1M events (first 500M), then $0.40 |
| EKS Events | $2.00 per 1M events |

### Cost Reduction Strategies

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GUARDDUTY COST OPTIMIZATION                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. REVIEW DATA SOURCES                                                 │
│     ├── Disable S3 protection if not storing sensitive data            │
│     ├── Disable EKS protection if not using Kubernetes                 │
│     └── Evaluate malware protection necessity                          │
│                                                                          │
│  2. OPTIMIZE VPC FLOW LOGS                                              │
│     ├── Review VPC configurations generating most traffic              │
│     ├── Consider VPC consolidation                                      │
│     └── Reduce unnecessary cross-AZ traffic                            │
│                                                                          │
│  3. REVIEW CLOUDTRAIL VOLUME                                            │
│     ├── Reduce unnecessary API calls                                    │
│     ├── Review automation scripts for efficiency                        │
│     └── Consider consolidating accounts                                 │
│                                                                          │
│  4. USE USAGE METRICS                                                   │
│     └── Review GuardDuty usage statistics monthly                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### View Usage Statistics

```bash
# Get usage statistics
aws guardduty get-usage-statistics \
  --detector-id <detector-id> \
  --usage-statistic-type SUM_BY_DATA_SOURCE \
  --usage-criteria '{
    "DataSources": ["FLOW_LOGS", "CLOUD_TRAIL", "DNS_LOGS", "S3_LOGS"]
  }'
```

---

## Best Practices

### 1. Enable in All Regions

```bash
# Enable GuardDuty in all regions
for region in $(aws ec2 describe-regions --query 'Regions[].RegionName' --output text); do
  echo "Enabling GuardDuty in $region"
  aws guardduty create-detector --enable --region $region
done
```

### 2. Centralize Findings

- Use Organizations with delegated administrator
- Aggregate to Security Hub
- Export to SIEM

### 3. Automate Response

- Create EventBridge rules for high-severity findings
- Implement Lambda remediation functions
- Test runbooks regularly

### 4. Regular Review

```
Daily:
└── Review high-severity findings

Weekly:
├── Review medium-severity findings
└── Check suppression rule effectiveness

Monthly:
├── Review all finding trends
├── Update threat intel lists
└── Audit suppression rules

Quarterly:
├── Review GuardDuty coverage
├── Test automated responses
└── Optimize costs
```

### 5. Integration Checklist

- [ ] Security Hub integration enabled
- [ ] EventBridge rules configured
- [ ] SNS notifications set up
- [ ] Lambda remediation deployed
- [ ] SIEM integration (if applicable)
- [ ] Trusted IP lists configured
- [ ] Custom threat intel (if applicable)

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No findings generated | Normal environment | Generate sample findings |
| Missing S3 findings | S3 protection disabled | Enable S3 data source |
| High costs | High traffic volume | Review VPC configurations |
| False positives | Normal business activity | Create suppression rules |

### Generate Sample Findings

```bash
# Generate sample findings for testing
aws guardduty create-sample-findings \
  --detector-id <detector-id> \
  --finding-types \
    "Backdoor:EC2/C&CActivity.B" \
    "CryptoCurrency:EC2/BitcoinTool.B!DNS" \
    "UnauthorizedAccess:IAMUser/ConsoleLoginSuccess.B"
```

---

## Key Takeaways

1. **Enable everywhere** - GuardDuty should be enabled in all regions and accounts
2. **Centralize management** - Use Organizations for multi-account setup
3. **Automate response** - Implement automated remediation for high-severity findings
4. **Tune carefully** - Use suppression rules to reduce noise, not hide threats
5. **Monitor costs** - Review usage statistics monthly
6. **Integrate broadly** - Connect to Security Hub, SIEM, and notification systems

---

## Next Steps

Continue to [04-security-hub.md](04-security-hub.md) to learn how to aggregate and manage security findings centrally.
