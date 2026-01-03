# Module 10: Security & Cost Optimization - Complete Hands-on Lab

## Lab Overview

In this comprehensive lab, you will implement a complete security and cost optimization solution for an AWS environment. You'll configure multiple security services, set up cost monitoring, and implement best practices.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Lab Architecture                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         ┌──────────────────┐                                │
│                         │   Security Hub   │                                │
│                         │   (Aggregator)   │                                │
│                         └────────┬─────────┘                                │
│                                  │                                          │
│          ┌───────────────────────┼───────────────────────┐                 │
│          │                       │                       │                 │
│   ┌──────▼──────┐        ┌───────▼──────┐        ┌───────▼──────┐         │
│   │  GuardDuty  │        │  Inspector   │        │    Macie     │         │
│   │  (Threats)  │        │ (Vuln Scan)  │        │ (Data Disc)  │         │
│   └─────────────┘        └──────────────┘        └──────────────┘         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                         VPC with Security                            │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│   │  │   WAF + ALB     │  │   EC2 + SSM     │  │   RDS + KMS     │      │  │
│   │  │                 │  │   (Scanned)     │  │   (Encrypted)   │      │  │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │  │
│   │                                                                      │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│   │  │ Secrets Manager │  │    S3 Bucket    │  │   CloudTrail    │      │  │
│   │  │  (DB Creds)     │  │  (Macie Scan)   │  │   (Logging)     │      │  │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    Cost Management                                   │  │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │  │
│   │  │ Cost Explorer   │  │    Budgets      │  │ Trusted Advisor │      │  │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS Account with administrative access
- AWS CLI configured
- Basic understanding of VPC, EC2, and S3
- Estimated time: 2-3 hours
- Estimated cost: $5-15 (clean up promptly)

## Lab Sections

1. Enable and Configure GuardDuty
2. Set up Security Hub
3. Create WAF Web ACL
4. Implement KMS Encryption
5. Configure Secrets Manager
6. Set up Cost Budgets and Alerts
7. Security Audit with Trusted Advisor
8. Complete Cleanup

---

## Section 1: Enable and Configure GuardDuty

### Step 1.1: Enable GuardDuty

```bash
#!/bin/bash
echo "=== Section 1: Enabling GuardDuty ==="

# Get account ID and region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"

# Enable GuardDuty
echo "Enabling GuardDuty..."
DETECTOR_ID=$(aws guardduty create-detector \
    --enable \
    --finding-publishing-frequency FIFTEEN_MINUTES \
    --data-sources '{
        "S3Logs": {"Enable": true},
        "Kubernetes": {"AuditLogs": {"Enable": true}},
        "MalwareProtection": {"ScanEc2InstanceWithFindings": {"EbsVolumes": true}}
    }' \
    --features '[
        {"Name": "S3_DATA_EVENTS", "Status": "ENABLED"},
        {"Name": "EKS_AUDIT_LOGS", "Status": "ENABLED"},
        {"Name": "EBS_MALWARE_PROTECTION", "Status": "ENABLED"},
        {"Name": "RDS_LOGIN_EVENTS", "Status": "ENABLED"},
        {"Name": "LAMBDA_NETWORK_LOGS", "Status": "ENABLED"}
    ]' \
    --query 'DetectorId' --output text 2>/dev/null)

if [ -z "$DETECTOR_ID" ]; then
    DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
    echo "GuardDuty already enabled. Detector ID: $DETECTOR_ID"
else
    echo "GuardDuty enabled. Detector ID: $DETECTOR_ID"
fi

# Export for later use
export GUARDDUTY_DETECTOR_ID=$DETECTOR_ID
echo "export GUARDDUTY_DETECTOR_ID=$DETECTOR_ID" >> ~/.lab_env
```

### Step 1.2: Create SNS Topic for GuardDuty Alerts

```bash
echo "Creating SNS topic for GuardDuty alerts..."

# Create SNS topic
GUARDDUTY_TOPIC_ARN=$(aws sns create-topic \
    --name guardduty-alerts \
    --query 'TopicArn' --output text)

echo "SNS Topic created: $GUARDDUTY_TOPIC_ARN"

# Add your email subscription (replace with your email)
EMAIL="your-email@example.com"
aws sns subscribe \
    --topic-arn $GUARDDUTY_TOPIC_ARN \
    --protocol email \
    --notification-endpoint $EMAIL

echo "Check your email and confirm the subscription!"

# Export for later use
export GUARDDUTY_TOPIC_ARN=$GUARDDUTY_TOPIC_ARN
echo "export GUARDDUTY_TOPIC_ARN=$GUARDDUTY_TOPIC_ARN" >> ~/.lab_env
```

### Step 1.3: Create EventBridge Rule for GuardDuty Findings

```bash
echo "Creating EventBridge rule for GuardDuty findings..."

# Create EventBridge rule
aws events put-rule \
    --name "GuardDuty-HighSeverity-Findings" \
    --event-pattern '{
        "source": ["aws.guardduty"],
        "detail-type": ["GuardDuty Finding"],
        "detail": {
            "severity": [{"numeric": [">=", 7]}]
        }
    }' \
    --state ENABLED

# Add SNS target
aws events put-targets \
    --rule "GuardDuty-HighSeverity-Findings" \
    --targets "Id"="sns-target","Arn"="$GUARDDUTY_TOPIC_ARN"

# Grant EventBridge permission to publish to SNS
aws sns add-permission \
    --topic-arn $GUARDDUTY_TOPIC_ARN \
    --label "EventBridge-GuardDuty" \
    --aws-account-id $ACCOUNT_ID \
    --action-name Publish

echo "EventBridge rule created for high-severity findings"
```

### Step 1.4: Generate Sample Findings

```bash
echo "Generating sample GuardDuty findings..."

aws guardduty create-sample-findings \
    --detector-id $GUARDDUTY_DETECTOR_ID \
    --finding-types \
        "UnauthorizedAccess:EC2/SSHBruteForce" \
        "Recon:EC2/PortProbeUnprotectedPort" \
        "CryptoCurrency:EC2/BitcoinTool.B!DNS"

echo "Sample findings generated. Check the GuardDuty console."

# List recent findings
echo "Recent findings:"
aws guardduty list-findings \
    --detector-id $GUARDDUTY_DETECTOR_ID \
    --max-results 5
```

---

## Section 2: Set up Security Hub

### Step 2.1: Enable Security Hub

```bash
echo "=== Section 2: Setting up Security Hub ==="

# Enable Security Hub
echo "Enabling Security Hub..."
aws securityhub enable-security-hub \
    --enable-default-standards \
    --control-finding-generator SECURITY_CONTROL 2>/dev/null || \
    echo "Security Hub may already be enabled"

# Wait for Security Hub to initialize
sleep 10

# Get enabled standards
echo "Enabled security standards:"
aws securityhub get-enabled-standards \
    --query 'StandardsSubscriptions[].StandardsArn'
```

### Step 2.2: Enable Additional Standards

```bash
echo "Enabling additional security standards..."

# Enable CIS AWS Foundations Benchmark
aws securityhub batch-enable-standards \
    --standards-subscription-requests '[
        {
            "StandardsArn": "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0"
        }
    ]' 2>/dev/null || echo "Standard may already be enabled"

# Enable AWS Foundational Security Best Practices
aws securityhub batch-enable-standards \
    --standards-subscription-requests '[
        {
            "StandardsArn": "arn:aws:securityhub:'"$REGION"'::standards/aws-foundational-security-best-practices/v/1.0.0"
        }
    ]' 2>/dev/null || echo "Standard may already be enabled"

echo "Security standards enabled"
```

### Step 2.3: Enable Product Integrations

```bash
echo "Enabling product integrations..."

# Enable GuardDuty integration (usually auto-enabled)
aws securityhub enable-import-findings-for-product \
    --product-arn "arn:aws:securityhub:$REGION::product/aws/guardduty" 2>/dev/null || \
    echo "GuardDuty integration already enabled"

# Enable Inspector integration
aws securityhub enable-import-findings-for-product \
    --product-arn "arn:aws:securityhub:$REGION::product/aws/inspector" 2>/dev/null || \
    echo "Inspector integration already enabled"

# Enable Macie integration
aws securityhub enable-import-findings-for-product \
    --product-arn "arn:aws:securityhub:$REGION::product/aws/macie" 2>/dev/null || \
    echo "Macie integration already enabled"

# List enabled integrations
echo "Enabled integrations:"
aws securityhub list-enabled-products-for-import \
    --query 'ProductSubscriptions'
```

### Step 2.4: Create Custom Insight

```bash
echo "Creating custom Security Hub insight..."

# Create insight for critical findings
aws securityhub create-insight \
    --name "Critical-Findings-Last-7-Days" \
    --filters '{
        "SeverityLabel": [{"Value": "CRITICAL", "Comparison": "EQUALS"}],
        "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}],
        "CreatedAt": [{"DateRange": {"Value": 7, "Unit": "DAYS"}}]
    }' \
    --group-by-attribute "ProductName"

echo "Custom insight created"

# Get insights
echo "Available insights:"
aws securityhub get-insights \
    --query 'Insights[].Name'
```

---

## Section 3: Create WAF Web ACL

### Step 3.1: Create WAF Web ACL

```bash
echo "=== Section 3: Creating WAF Web ACL ==="

# Create WAF Web ACL
echo "Creating WAF Web ACL..."

WAF_ACL_ARN=$(aws wafv2 create-web-acl \
    --name "SecurityLabWebACL" \
    --scope REGIONAL \
    --default-action '{"Allow": {}}' \
    --visibility-config '{
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "SecurityLabWebACL"
    }' \
    --rules '[
        {
            "Name": "AWS-AWSManagedRulesCommonRuleSet",
            "Priority": 0,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesCommonRuleSet"
                }
            },
            "OverrideAction": {"None": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "CommonRuleSet"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesKnownBadInputsRuleSet",
            "Priority": 1,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesKnownBadInputsRuleSet"
                }
            },
            "OverrideAction": {"None": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "KnownBadInputs"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesSQLiRuleSet",
            "Priority": 2,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesSQLiRuleSet"
                }
            },
            "OverrideAction": {"None": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "SQLiRules"
            }
        }
    ]' \
    --query 'Summary.ARN' --output text)

echo "WAF Web ACL created: $WAF_ACL_ARN"
export WAF_ACL_ARN=$WAF_ACL_ARN
echo "export WAF_ACL_ARN=$WAF_ACL_ARN" >> ~/.lab_env
```

### Step 3.2: Create Rate Limiting Rule

```bash
echo "Adding rate limiting rule..."

# Get current Web ACL
WAF_ACL_ID=$(echo $WAF_ACL_ARN | cut -d'/' -f3)

# Get current lock token
LOCK_TOKEN=$(aws wafv2 get-web-acl \
    --name "SecurityLabWebACL" \
    --scope REGIONAL \
    --id $WAF_ACL_ID \
    --query 'LockToken' --output text)

# Update with rate limiting rule
aws wafv2 update-web-acl \
    --name "SecurityLabWebACL" \
    --scope REGIONAL \
    --id $WAF_ACL_ID \
    --lock-token $LOCK_TOKEN \
    --default-action '{"Allow": {}}' \
    --visibility-config '{
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "SecurityLabWebACL"
    }' \
    --rules '[
        {
            "Name": "RateLimitRule",
            "Priority": 0,
            "Statement": {
                "RateBasedStatement": {
                    "Limit": 1000,
                    "AggregateKeyType": "IP"
                }
            },
            "Action": {"Block": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "RateLimit"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesCommonRuleSet",
            "Priority": 1,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesCommonRuleSet"
                }
            },
            "OverrideAction": {"None": {}},
            "VisibilityConfig": {
                "SampledRequestsEnabled": true,
                "CloudWatchMetricsEnabled": true,
                "MetricName": "CommonRuleSet"
            }
        }
    ]'

echo "Rate limiting rule added"
```

---

## Section 4: Implement KMS Encryption

### Step 4.1: Create Customer Managed Key

```bash
echo "=== Section 4: Implementing KMS Encryption ==="

# Create KMS key
echo "Creating KMS Customer Managed Key..."

KMS_KEY_ID=$(aws kms create-key \
    --description "Security Lab CMK for encryption" \
    --key-usage ENCRYPT_DECRYPT \
    --origin AWS_KMS \
    --tags TagKey=Purpose,TagValue=SecurityLab TagKey=Environment,TagValue=Lab \
    --query 'KeyMetadata.KeyId' --output text)

echo "KMS Key created: $KMS_KEY_ID"

# Create alias
aws kms create-alias \
    --alias-name "alias/security-lab-key" \
    --target-key-id $KMS_KEY_ID

echo "KMS alias created: alias/security-lab-key"

# Enable automatic key rotation
aws kms enable-key-rotation \
    --key-id $KMS_KEY_ID

echo "Automatic key rotation enabled"

export KMS_KEY_ID=$KMS_KEY_ID
echo "export KMS_KEY_ID=$KMS_KEY_ID" >> ~/.lab_env
```

### Step 4.2: Create Key Policy

```bash
echo "Updating KMS key policy..."

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create key policy
aws kms put-key-policy \
    --key-id $KMS_KEY_ID \
    --policy-name default \
    --policy '{
        "Version": "2012-10-17",
        "Id": "security-lab-key-policy",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::'"$ACCOUNT_ID"':root"
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "Allow administration of the key",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::'"$ACCOUNT_ID"':root"
                },
                "Action": [
                    "kms:Create*",
                    "kms:Describe*",
                    "kms:Enable*",
                    "kms:List*",
                    "kms:Put*",
                    "kms:Update*",
                    "kms:Revoke*",
                    "kms:Disable*",
                    "kms:Get*",
                    "kms:Delete*",
                    "kms:TagResource",
                    "kms:UntagResource",
                    "kms:ScheduleKeyDeletion",
                    "kms:CancelKeyDeletion"
                ],
                "Resource": "*"
            },
            {
                "Sid": "Allow use of the key for encryption",
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "secretsmanager.amazonaws.com",
                        "rds.amazonaws.com",
                        "s3.amazonaws.com"
                    ]
                },
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": "*"
            }
        ]
    }'

echo "Key policy updated"
```

### Step 4.3: Create Encrypted S3 Bucket

```bash
echo "Creating encrypted S3 bucket..."

BUCKET_NAME="security-lab-encrypted-${ACCOUNT_ID}"

# Create bucket
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION 2>/dev/null || \
    aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION

# Enable server-side encryption with KMS
aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms",
                    "KMSMasterKeyID": "alias/security-lab-key"
                },
                "BucketKeyEnabled": true
            }
        ]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration '{
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }'

echo "Encrypted bucket created: $BUCKET_NAME"
export ENCRYPTED_BUCKET=$BUCKET_NAME
echo "export ENCRYPTED_BUCKET=$BUCKET_NAME" >> ~/.lab_env
```

---

## Section 5: Configure Secrets Manager

### Step 5.1: Create Database Secret

```bash
echo "=== Section 5: Configuring Secrets Manager ==="

# Create secret for database credentials
echo "Creating database credentials secret..."

SECRET_ARN=$(aws secretsmanager create-secret \
    --name "security-lab/database/credentials" \
    --description "Database credentials for security lab" \
    --kms-key-id "alias/security-lab-key" \
    --secret-string '{
        "username": "dbadmin",
        "password": "'"$(openssl rand -base64 24)"'",
        "engine": "mysql",
        "host": "localhost",
        "port": 3306,
        "dbname": "securitylab"
    }' \
    --tags Key=Environment,Value=Lab Key=Purpose,Value=SecurityLab \
    --query 'ARN' --output text)

echo "Secret created: $SECRET_ARN"
export DB_SECRET_ARN=$SECRET_ARN
echo "export DB_SECRET_ARN=$SECRET_ARN" >> ~/.lab_env
```

### Step 5.2: Create API Key Secret

```bash
echo "Creating API key secret..."

API_SECRET_ARN=$(aws secretsmanager create-secret \
    --name "security-lab/api/external-service" \
    --description "API key for external service" \
    --kms-key-id "alias/security-lab-key" \
    --secret-string '{
        "api_key": "'"$(openssl rand -hex 32)"'",
        "api_endpoint": "https://api.example.com",
        "api_version": "v2"
    }' \
    --query 'ARN' --output text)

echo "API Secret created: $API_SECRET_ARN"
export API_SECRET_ARN=$API_SECRET_ARN
echo "export API_SECRET_ARN=$API_SECRET_ARN" >> ~/.lab_env
```

### Step 5.3: Configure Secret Rotation

```bash
echo "Note: Rotation requires a Lambda function and database."
echo "For this lab, we'll configure the rotation schedule without enabling it."

# Create rotation policy (without enabling - requires Lambda)
aws secretsmanager rotate-secret \
    --secret-id "security-lab/database/credentials" \
    --rotation-rules '{"AutomaticallyAfterDays": 30}' 2>/dev/null || \
    echo "Rotation not enabled (requires Lambda function)"

echo "Rotation schedule configured for 30 days"
```

### Step 5.4: Retrieve Secret

```bash
echo "Retrieving secrets..."

# Retrieve database secret
echo "Database credentials:"
aws secretsmanager get-secret-value \
    --secret-id "security-lab/database/credentials" \
    --query 'SecretString' --output text | jq .

# Retrieve API secret
echo "API credentials:"
aws secretsmanager get-secret-value \
    --secret-id "security-lab/api/external-service" \
    --query 'SecretString' --output text | jq .
```

---

## Section 6: Set up Cost Budgets and Alerts

### Step 6.1: Create Monthly Budget

```bash
echo "=== Section 6: Setting up Cost Management ==="

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
EMAIL="your-email@example.com"  # Replace with your email

# Create SNS topic for budget alerts
BUDGET_TOPIC_ARN=$(aws sns create-topic \
    --name cost-budget-alerts \
    --query 'TopicArn' --output text)

echo "Budget SNS Topic: $BUDGET_TOPIC_ARN"

# Subscribe email
aws sns subscribe \
    --topic-arn $BUDGET_TOPIC_ARN \
    --protocol email \
    --notification-endpoint $EMAIL

# Create monthly budget
echo "Creating monthly cost budget..."

aws budgets create-budget \
    --account-id $ACCOUNT_ID \
    --budget '{
        "BudgetName": "SecurityLab-Monthly-Budget",
        "BudgetLimit": {
            "Amount": "100",
            "Unit": "USD"
        },
        "BudgetType": "COST",
        "TimeUnit": "MONTHLY",
        "CostTypes": {
            "IncludeTax": true,
            "IncludeSubscription": true,
            "UseBlended": false,
            "IncludeRefund": false,
            "IncludeCredit": false,
            "IncludeUpfront": true,
            "IncludeRecurring": true,
            "IncludeOtherSubscription": true,
            "IncludeSupport": true,
            "IncludeDiscount": true,
            "UseAmortized": false
        }
    }' \
    --notifications-with-subscribers '[
        {
            "Notification": {
                "NotificationType": "ACTUAL",
                "ComparisonOperator": "GREATER_THAN",
                "Threshold": 50,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "SubscriptionType": "EMAIL",
                    "Address": "'"$EMAIL"'"
                }
            ]
        },
        {
            "Notification": {
                "NotificationType": "ACTUAL",
                "ComparisonOperator": "GREATER_THAN",
                "Threshold": 80,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "SubscriptionType": "SNS",
                    "Address": "'"$BUDGET_TOPIC_ARN"'"
                }
            ]
        },
        {
            "Notification": {
                "NotificationType": "FORECASTED",
                "ComparisonOperator": "GREATER_THAN",
                "Threshold": 100,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "SubscriptionType": "EMAIL",
                    "Address": "'"$EMAIL"'"
                }
            ]
        }
    ]'

echo "Monthly budget created with alerts at 50%, 80%, and 100% forecast"
```

### Step 6.2: Create Service-Specific Budget

```bash
echo "Creating EC2-specific budget..."

aws budgets create-budget \
    --account-id $ACCOUNT_ID \
    --budget '{
        "BudgetName": "SecurityLab-EC2-Budget",
        "BudgetLimit": {
            "Amount": "50",
            "Unit": "USD"
        },
        "BudgetType": "COST",
        "TimeUnit": "MONTHLY",
        "CostFilters": {
            "Service": ["Amazon Elastic Compute Cloud - Compute"]
        }
    }' \
    --notifications-with-subscribers '[
        {
            "Notification": {
                "NotificationType": "ACTUAL",
                "ComparisonOperator": "GREATER_THAN",
                "Threshold": 80,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "SubscriptionType": "EMAIL",
                    "Address": "'"$EMAIL"'"
                }
            ]
        }
    ]'

echo "EC2-specific budget created"
```

### Step 6.3: Set up Cost Anomaly Detection

```bash
echo "Setting up Cost Anomaly Detection..."

# Create anomaly monitor
MONITOR_ARN=$(aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "MonitorName": "SecurityLab-Service-Monitor",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }' \
    --query 'MonitorArn' --output text)

echo "Anomaly Monitor created: $MONITOR_ARN"

# Create anomaly subscription
aws ce create-anomaly-subscription \
    --anomaly-subscription '{
        "SubscriptionName": "SecurityLab-Anomaly-Alerts",
        "MonitorArnList": ["'"$MONITOR_ARN"'"],
        "Subscribers": [
            {
                "Type": "EMAIL",
                "Address": "'"$EMAIL"'"
            }
        ],
        "Threshold": 50,
        "Frequency": "DAILY"
    }'

echo "Anomaly subscription created"
```

---

## Section 7: Security Audit with Trusted Advisor

### Step 7.1: Review Security Status

```bash
echo "=== Section 7: Security Audit ==="

echo "Performing security audit..."

# Note: Full Trusted Advisor requires Business/Enterprise support
# These commands work with Basic support for limited checks

# Check for security groups with unrestricted access
echo "Checking security groups..."
aws ec2 describe-security-groups \
    --filters "Name=ip-permission.cidr,Values=0.0.0.0/0" \
    --query 'SecurityGroups[].{GroupId:GroupId,GroupName:GroupName,Description:Description}' \
    --output table

# Check for public S3 buckets
echo "Checking S3 bucket public access..."
for bucket in $(aws s3api list-buckets --query 'Buckets[].Name' --output text); do
    STATUS=$(aws s3api get-public-access-block --bucket $bucket 2>/dev/null \
        --query 'PublicAccessBlockConfiguration' --output json || echo "No block")
    echo "Bucket: $bucket"
    echo "Public Access Block: $STATUS"
done

# Check for unencrypted EBS volumes
echo "Checking unencrypted EBS volumes..."
aws ec2 describe-volumes \
    --filters "Name=encrypted,Values=false" \
    --query 'Volumes[].{VolumeId:VolumeId,Size:Size,State:State}' \
    --output table

# Check for unused Elastic IPs
echo "Checking for unused Elastic IPs..."
aws ec2 describe-addresses \
    --query 'Addresses[?InstanceId==`null`].{PublicIp:PublicIp,AllocationId:AllocationId}' \
    --output table
```

### Step 7.2: Generate Security Report

```bash
echo "Generating security summary report..."

cat << 'EOF' > /tmp/security-report.sh
#!/bin/bash
echo "======================================"
echo "     AWS Security Audit Report"
echo "     Date: $(date)"
echo "======================================"
echo ""

echo "1. GuardDuty Status:"
aws guardduty list-detectors --query 'DetectorIds' --output text

echo ""
echo "2. Security Hub Enabled Standards:"
aws securityhub get-enabled-standards --query 'StandardsSubscriptions[].StandardsArn' --output table

echo ""
echo "3. Open Security Groups (Port 22 from 0.0.0.0/0):"
aws ec2 describe-security-groups \
    --filters "Name=ip-permission.from-port,Values=22" "Name=ip-permission.cidr,Values=0.0.0.0/0" \
    --query 'SecurityGroups[].GroupId' --output text

echo ""
echo "4. Unencrypted S3 Buckets:"
for bucket in $(aws s3api list-buckets --query 'Buckets[].Name' --output text); do
    ENCRYPTION=$(aws s3api get-bucket-encryption --bucket $bucket 2>/dev/null || echo "NOT ENCRYPTED")
    if [[ $ENCRYPTION == "NOT ENCRYPTED" ]]; then
        echo "  - $bucket"
    fi
done

echo ""
echo "5. Secrets Manager Secrets:"
aws secretsmanager list-secrets --query 'SecretList[].Name' --output table

echo ""
echo "6. KMS Keys:"
aws kms list-keys --query 'Keys[].KeyId' --output table

echo ""
echo "7. Active Budgets:"
aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text) \
    --query 'Budgets[].BudgetName' --output table

echo ""
echo "======================================"
echo "          End of Report"
echo "======================================"
EOF

chmod +x /tmp/security-report.sh
/tmp/security-report.sh
```

---

## Section 8: Complete Cleanup

### Step 8.1: Cleanup Script

```bash
#!/bin/bash
echo "=== Section 8: Cleanup ==="
echo "This will delete all resources created in this lab."
echo "Press Ctrl+C within 10 seconds to cancel..."
sleep 10

# Load environment variables
source ~/.lab_env 2>/dev/null

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Starting cleanup..."

# 1. Delete Secrets
echo "Deleting Secrets Manager secrets..."
aws secretsmanager delete-secret \
    --secret-id "security-lab/database/credentials" \
    --force-delete-without-recovery 2>/dev/null || true

aws secretsmanager delete-secret \
    --secret-id "security-lab/api/external-service" \
    --force-delete-without-recovery 2>/dev/null || true

# 2. Delete S3 bucket
echo "Deleting S3 bucket..."
BUCKET_NAME="security-lab-encrypted-${ACCOUNT_ID}"
aws s3 rb s3://$BUCKET_NAME --force 2>/dev/null || true

# 3. Delete WAF Web ACL
echo "Deleting WAF Web ACL..."
WAF_ACL_ID=$(aws wafv2 list-web-acls \
    --scope REGIONAL \
    --query 'WebACLs[?Name==`SecurityLabWebACL`].Id' --output text)

if [ -n "$WAF_ACL_ID" ]; then
    LOCK_TOKEN=$(aws wafv2 get-web-acl \
        --name "SecurityLabWebACL" \
        --scope REGIONAL \
        --id $WAF_ACL_ID \
        --query 'LockToken' --output text)

    aws wafv2 delete-web-acl \
        --name "SecurityLabWebACL" \
        --scope REGIONAL \
        --id $WAF_ACL_ID \
        --lock-token $LOCK_TOKEN
fi

# 4. Delete KMS key (schedule deletion)
echo "Scheduling KMS key deletion..."
if [ -n "$KMS_KEY_ID" ]; then
    aws kms schedule-key-deletion \
        --key-id $KMS_KEY_ID \
        --pending-window-in-days 7
fi

# 5. Delete EventBridge rules
echo "Deleting EventBridge rules..."
aws events remove-targets \
    --rule "GuardDuty-HighSeverity-Findings" \
    --ids "sns-target" 2>/dev/null || true

aws events delete-rule \
    --name "GuardDuty-HighSeverity-Findings" 2>/dev/null || true

# 6. Delete SNS topics
echo "Deleting SNS topics..."
for topic in guardduty-alerts cost-budget-alerts; do
    TOPIC_ARN=$(aws sns list-topics --query "Topics[?contains(TopicArn, '$topic')].TopicArn" --output text)
    if [ -n "$TOPIC_ARN" ]; then
        aws sns delete-topic --topic-arn $TOPIC_ARN
    fi
done

# 7. Delete Budgets
echo "Deleting budgets..."
aws budgets delete-budget \
    --account-id $ACCOUNT_ID \
    --budget-name "SecurityLab-Monthly-Budget" 2>/dev/null || true

aws budgets delete-budget \
    --account-id $ACCOUNT_ID \
    --budget-name "SecurityLab-EC2-Budget" 2>/dev/null || true

# 8. Delete Cost Anomaly resources
echo "Deleting Cost Anomaly resources..."
SUBSCRIPTION_ARN=$(aws ce get-anomaly-subscriptions \
    --query 'AnomalySubscriptions[?SubscriptionName==`SecurityLab-Anomaly-Alerts`].SubscriptionArn' \
    --output text)
if [ -n "$SUBSCRIPTION_ARN" ]; then
    aws ce delete-anomaly-subscription --subscription-arn $SUBSCRIPTION_ARN
fi

MONITOR_ARN=$(aws ce get-anomaly-monitors \
    --query 'AnomalyMonitors[?MonitorName==`SecurityLab-Service-Monitor`].MonitorArn' \
    --output text)
if [ -n "$MONITOR_ARN" ]; then
    aws ce delete-anomaly-monitor --monitor-arn $MONITOR_ARN
fi

# 9. Disable GuardDuty (optional - comment out if you want to keep it)
echo "Disabling GuardDuty..."
DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
if [ -n "$DETECTOR_ID" ] && [ "$DETECTOR_ID" != "None" ]; then
    # Delete sample findings first
    aws guardduty delete-detector --detector-id $DETECTOR_ID
fi

# 10. Disable Security Hub (optional - comment out if you want to keep it)
echo "Disabling Security Hub..."
aws securityhub disable-security-hub 2>/dev/null || true

# 11. Delete Security Hub insights
echo "Deleting Security Hub insights..."
INSIGHT_ARN=$(aws securityhub get-insights \
    --query 'Insights[?Name==`Critical-Findings-Last-7-Days`].InsightArn' \
    --output text 2>/dev/null)
if [ -n "$INSIGHT_ARN" ]; then
    aws securityhub delete-insight --insight-arn $INSIGHT_ARN
fi

# 12. Clean up environment file
rm -f ~/.lab_env

echo ""
echo "======================================"
echo "        Cleanup Complete!"
echo "======================================"
echo ""
echo "Resources that may take time to fully delete:"
echo "- KMS key: Scheduled for deletion in 7 days"
echo "- GuardDuty: Detector deleted"
echo "- Security Hub: Disabled"
echo ""
echo "Please verify in the AWS Console that all resources are deleted."
```

### Step 8.2: Verification

```bash
echo "Verifying cleanup..."

# Check GuardDuty
echo "GuardDuty detectors:"
aws guardduty list-detectors --query 'DetectorIds'

# Check Security Hub
echo "Security Hub status:"
aws securityhub get-enabled-standards 2>/dev/null || echo "Security Hub disabled"

# Check Secrets
echo "Secrets:"
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `security-lab`)].Name'

# Check S3 buckets
echo "Lab S3 buckets:"
aws s3api list-buckets --query 'Buckets[?contains(Name, `security-lab`)].Name'

# Check WAF
echo "WAF Web ACLs:"
aws wafv2 list-web-acls --scope REGIONAL --query 'WebACLs[?Name==`SecurityLabWebACL`].Name'

echo "Verification complete!"
```

---

## Lab Summary

### What You Accomplished

In this comprehensive lab, you:

1. **GuardDuty**: Enabled threat detection with sample findings and alerts
2. **Security Hub**: Aggregated findings with multiple security standards
3. **WAF**: Created Web ACL with managed rules and rate limiting
4. **KMS**: Implemented customer-managed encryption keys
5. **Secrets Manager**: Stored and managed sensitive credentials
6. **Cost Management**: Set up budgets, alerts, and anomaly detection
7. **Security Audit**: Performed infrastructure security assessment

### Key Security Concepts Practiced

| Service | Key Concept |
|---------|-------------|
| GuardDuty | Continuous threat detection and monitoring |
| Security Hub | Centralized security findings aggregation |
| WAF | Layer 7 protection with managed rules |
| KMS | Encryption key management and rotation |
| Secrets Manager | Secure credential storage and rotation |
| Budgets | Cost governance and alerting |
| Trusted Advisor | Best practice recommendations |

### Best Practices Implemented

1. **Defense in Depth**: Multiple security layers (WAF, GuardDuty, Security Hub)
2. **Encryption at Rest**: KMS-encrypted S3 and Secrets Manager
3. **Least Privilege**: Specific key policies and IAM permissions
4. **Monitoring**: EventBridge rules for security alerts
5. **Cost Control**: Budgets with threshold alerts
6. **Automation**: Scripted deployment and cleanup

### Next Steps

1. **Production Deployment**: Adapt these configurations for production
2. **Multi-Account**: Implement with AWS Organizations
3. **Compliance**: Map controls to regulatory frameworks
4. **Automation**: Create CloudFormation/Terraform templates
5. **Integration**: Connect to SIEM and ticketing systems

---

## Appendix: CloudFormation Template

For production use, deploy this CloudFormation template:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Security Lab Infrastructure'

Parameters:
  AlertEmail:
    Type: String
    Description: Email for security alerts

Resources:
  # GuardDuty
  GuardDutyDetector:
    Type: AWS::GuardDuty::Detector
    Properties:
      Enable: true
      FindingPublishingFrequency: FIFTEEN_MINUTES

  # Security Alert Topic
  SecurityAlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: security-alerts
      KmsMasterKeyId: alias/aws/sns

  SecurityAlertSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref SecurityAlertTopic
      Protocol: email
      Endpoint: !Ref AlertEmail

  # GuardDuty Alert Rule
  GuardDutyAlertRule:
    Type: AWS::Events::Rule
    Properties:
      Name: GuardDuty-High-Severity
      EventPattern:
        source:
          - aws.guardduty
        detail-type:
          - GuardDuty Finding
        detail:
          severity:
            - numeric:
                - '>='
                - 7
      Targets:
        - Id: sns
          Arn: !Ref SecurityAlertTopic

  # KMS Key
  SecurityKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Security Lab encryption key
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: kms:*
            Resource: '*'

  SecurityKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: alias/security-lab
      TargetKeyId: !Ref SecurityKey

  # Encrypted S3 Bucket
  EncryptedBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: !Ref SecurityKey
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  GuardDutyDetectorId:
    Value: !Ref GuardDutyDetector
  SecurityTopicArn:
    Value: !Ref SecurityAlertTopic
  KMSKeyId:
    Value: !Ref SecurityKey
  BucketName:
    Value: !Ref EncryptedBucket
```

---

**Congratulations!** You have completed the Security & Cost Optimization hands-on lab!
