# IAM Best Practices and Security

## Introduction

This document covers AWS-recommended best practices for IAM security. Following these practices helps protect your AWS environment from common security threats and ensures compliance with security standards.

---

## The Principle of Least Privilege

### What is Least Privilege?

```
+------------------------------------------------------------------+
|                  PRINCIPLE OF LEAST PRIVILEGE                     |
+------------------------------------------------------------------+
|                                                                   |
|  Definition:                                                      |
|  Grant only the permissions required to perform a task,          |
|  nothing more.                                                    |
|                                                                   |
|  Visual:                                                          |
|                                                                   |
|  BAD: Overly permissive                                          |
|  +----------------------------------------------------------+    |
|  |                    FULL ADMIN ACCESS                      |    |
|  |   +--------------------------------------------------+   |    |
|  |   |   Actual permissions needed: s3:GetObject         |   |    |
|  |   |   (tiny compared to what's granted)               |   |    |
|  |   +--------------------------------------------------+   |    |
|  +----------------------------------------------------------+    |
|                                                                   |
|  GOOD: Least privilege                                           |
|  +------------------+                                             |
|  |  s3:GetObject    |  <-- Only what's needed                    |
|  |  on bucket/path  |                                             |
|  +------------------+                                             |
|                                                                   |
+------------------------------------------------------------------+
```

### Implementing Least Privilege

#### Step 1: Start with Minimum Access

```json
// Start with NO permissions
{
    "Version": "2012-10-17",
    "Statement": []
}

// Add only what's needed, tested, and verified
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowReadProductionLogs",
            "Effect": "Allow",
            "Action": [
                "logs:GetLogEvents",
                "logs:FilterLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/production-*"
        }
    ]
}
```

#### Step 2: Use AWS Access Analyzer

```bash
# Generate policy from CloudTrail activity
aws accessanalyzer generate-policy \
    --policy-generation-details '{
        "principalArn": "arn:aws:iam::123456789012:role/MyRole"
    }' \
    --cloud-trail-details '{
        "trails": [
            {
                "cloudTrailArn": "arn:aws:cloudtrail:us-east-1:123456789012:trail/management-events"
            }
        ],
        "startTime": "2024-01-01T00:00:00Z",
        "endTime": "2024-01-31T23:59:59Z"
    }'

# Get the generated policy
aws accessanalyzer get-generated-policy --job-id <job-id>
```

#### Step 3: Regularly Review with Last Accessed Data

```bash
# Generate service last accessed report
aws iam generate-service-last-accessed-details \
    --arn arn:aws:iam::123456789012:user/john

# Get the report
aws iam get-service-last-accessed-details \
    --job-id <job-id>

# Shows which services were accessed and when
# Remove permissions for services not used in 90+ days
```

### Least Privilege Checklist

```
+------------------------------------------------------------------+
|               LEAST PRIVILEGE CHECKLIST                           |
+------------------------------------------------------------------+

[ ] Use specific actions instead of wildcards (s3:GetObject vs s3:*)
[ ] Specify exact resource ARNs instead of *
[ ] Use conditions to further restrict access
[ ] Start with AWS managed policies, then create custom ones
[ ] Use IAM Access Analyzer to generate minimal policies
[ ] Review permissions quarterly using last accessed data
[ ] Remove unused permissions promptly
[ ] Use separate roles for different functions
[ ] Implement permission boundaries for delegated admins
[ ] Use resource-based policies where appropriate

+------------------------------------------------------------------+
```

---

## Multi-Factor Authentication (MFA)

### Why MFA is Critical

```
+------------------------------------------------------------------+
|                    MFA PROTECTION                                 |
+------------------------------------------------------------------+
|                                                                   |
|  WITHOUT MFA:                                                    |
|  +----------+          +----------+                              |
|  | Attacker |--STOLEN->| Password |--ACCESS!->| AWS Account |   |
|  +----------+ PASSWORD +----------+            +--------------+   |
|                                                                   |
|  WITH MFA:                                                       |
|  +----------+          +----------+          +--------+          |
|  | Attacker |--STOLEN->| Password |--BLOCKED-| MFA    |          |
|  +----------+ PASSWORD +----------+     |    | Code   |          |
|                                         |    +--------+          |
|                                         v                        |
|                                  +-------------+                 |
|                                  | ACCESS      |                 |
|                                  | DENIED!     |                 |
|                                  +-------------+                 |
|                                                                   |
+------------------------------------------------------------------+
```

### MFA Types Supported by AWS

| Type | Description | Security Level |
|------|-------------|----------------|
| Virtual MFA | Smartphone app (Google Authenticator, Authy) | Good |
| Hardware MFA | Physical device (YubiKey, Gemalto) | Better |
| SMS MFA | Text message (deprecated for root) | Basic |
| FIDO2/WebAuthn | Security keys, biometrics | Best |

### Enabling MFA for Users

```bash
# Step 1: Create virtual MFA device
aws iam create-virtual-mfa-device \
    --virtual-mfa-device-name john-mfa \
    --outfile /tmp/QRCode.png \
    --bootstrap-method QRCodePNG

# Step 2: User scans QR code with authenticator app
# Step 3: Enable MFA with two consecutive codes
aws iam enable-mfa-device \
    --user-name john \
    --serial-number arn:aws:iam::123456789012:mfa/john-mfa \
    --authentication-code1 123456 \
    --authentication-code2 789012

# List MFA devices for user
aws iam list-mfa-devices --user-name john

# Deactivate MFA device
aws iam deactivate-mfa-device \
    --user-name john \
    --serial-number arn:aws:iam::123456789012:mfa/john-mfa
```

### Enforcing MFA with Policies

#### Deny All Without MFA (Self-Service Exception)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowViewAccountInfo",
            "Effect": "Allow",
            "Action": [
                "iam:GetAccountPasswordPolicy",
                "iam:ListVirtualMFADevices"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowManageOwnMFA",
            "Effect": "Allow",
            "Action": [
                "iam:CreateVirtualMFADevice",
                "iam:DeleteVirtualMFADevice",
                "iam:EnableMFADevice",
                "iam:ListMFADevices",
                "iam:ResyncMFADevice"
            ],
            "Resource": [
                "arn:aws:iam::*:mfa/${aws:username}",
                "arn:aws:iam::*:user/${aws:username}"
            ]
        },
        {
            "Sid": "AllowDeactivateOwnMFAOnlyWhenUsingMFA",
            "Effect": "Allow",
            "Action": [
                "iam:DeactivateMFADevice"
            ],
            "Resource": [
                "arn:aws:iam::*:mfa/${aws:username}",
                "arn:aws:iam::*:user/${aws:username}"
            ],
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": "true"
                }
            }
        },
        {
            "Sid": "DenyAllExceptListedIfNoMFA",
            "Effect": "Deny",
            "NotAction": [
                "iam:CreateVirtualMFADevice",
                "iam:EnableMFADevice",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ListVirtualMFADevices",
                "iam:ResyncMFADevice",
                "sts:GetSessionToken"
            ],
            "Resource": "*",
            "Condition": {
                "BoolIfExists": {
                    "aws:MultiFactorAuthPresent": "false"
                }
            }
        }
    ]
}
```

#### Require MFA for Sensitive Operations

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowEC2ReadAlways",
            "Effect": "Allow",
            "Action": "ec2:Describe*",
            "Resource": "*"
        },
        {
            "Sid": "AllowEC2ActionsWithMFA",
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:StopInstances",
                "ec2:StartInstances"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": "true"
                }
            }
        }
    ]
}
```

---

## Password Policies

### AWS Recommended Password Policy

```bash
aws iam update-account-password-policy \
    --minimum-password-length 14 \
    --require-symbols \
    --require-numbers \
    --require-uppercase-characters \
    --require-lowercase-characters \
    --allow-users-to-change-password \
    --max-password-age 90 \
    --password-reuse-prevention 24 \
    --no-hard-expiry
```

### Password Policy Comparison

```
+------------------------------------------------------------------+
|              PASSWORD POLICY COMPARISON                           |
+------------------------------------------------------------------+

+----------------------+------------+------------+------------+
|     Setting          |  Minimum   | Recommended| Maximum    |
+----------------------+------------+------------+------------+
| Password Length      |     6      |    14+     |    128     |
+----------------------+------------+------------+------------+
| Require Uppercase    |     No     |    Yes     |    Yes     |
+----------------------+------------+------------+------------+
| Require Lowercase    |     No     |    Yes     |    Yes     |
+----------------------+------------+------------+------------+
| Require Numbers      |     No     |    Yes     |    Yes     |
+----------------------+------------+------------+------------+
| Require Symbols      |     No     |    Yes     |    Yes     |
+----------------------+------------+------------+------------+
| Max Password Age     |   None     |   90 days  | 1095 days  |
+----------------------+------------+------------+------------+
| Password Reuse       |   None     |    24      |    24      |
+----------------------+------------+------------+------------+
| Allow User Change    |     No     |    Yes     |    Yes     |
+----------------------+------------+------------+------------+

+------------------------------------------------------------------+
```

---

## Access Key Best Practices

### Access Key Security Rules

```
+------------------------------------------------------------------+
|                 ACCESS KEY BEST PRACTICES                         |
+------------------------------------------------------------------+

1. DON'T CREATE ACCESS KEYS FOR ROOT ACCOUNT - EVER

2. Rotate access keys every 90 days
   +----------+     +----------+     +----------+
   | Create   |     | Test new |     | Delete   |
   | new key  |---->| key      |---->| old key  |
   +----------+     +----------+     +----------+

3. Use IAM roles instead of access keys where possible

   +-----------+              +-----------+
   | EC2 with  |  BETTER     | EC2 with  |
   | access    |  THAN >>    | IAM Role  |
   | keys      |              |           |
   +-----------+              +-----------+

4. Never share access keys between users

5. Never commit access keys to code repositories

6. Monitor and alert on unused access keys

7. Use temporary credentials (STS) when possible

+------------------------------------------------------------------+
```

### Detecting and Removing Unused Keys

```bash
#!/bin/bash
# Script to find old/unused access keys

echo "=== Access Keys Older Than 90 Days ==="
aws iam list-users --query 'Users[*].UserName' --output text | while read user; do
    aws iam list-access-keys --user-name "$user" \
        --query 'AccessKeyMetadata[?Status==`Active`].[UserName,AccessKeyId,CreateDate]' \
        --output text | while read u key created; do

        age=$(( ($(date +%s) - $(date -d "$created" +%s)) / 86400 ))

        if [ "$age" -gt 90 ]; then
            last_used=$(aws iam get-access-key-last-used \
                --access-key-id "$key" \
                --query 'AccessKeyLastUsed.LastUsedDate' \
                --output text)
            echo "User: $u | Key: $key | Age: $age days | Last Used: $last_used"
        fi
    done
done

echo ""
echo "=== Access Keys Never Used ==="
aws iam list-users --query 'Users[*].UserName' --output text | while read user; do
    aws iam list-access-keys --user-name "$user" \
        --query 'AccessKeyMetadata[?Status==`Active`].AccessKeyId' \
        --output text | while read key; do

        last_used=$(aws iam get-access-key-last-used \
            --access-key-id "$key" \
            --query 'AccessKeyLastUsed.LastUsedDate' \
            --output text)

        if [ "$last_used" == "None" ]; then
            echo "User: $user | Key: $key | NEVER USED"
        fi
    done
done
```

---

## IAM Access Analyzer

### What is Access Analyzer?

```
+------------------------------------------------------------------+
|                    IAM ACCESS ANALYZER                            |
+------------------------------------------------------------------+
|                                                                   |
|  Purpose: Identify resources shared with external entities       |
|                                                                   |
|  +------------------+                                             |
|  |  Access Analyzer |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           | Analyzes:                                            |
|           v                                                       |
|  +------------------+------------------+------------------+       |
|  | S3 Buckets       | IAM Roles        | KMS Keys         |       |
|  | (Bucket policies)| (Trust policies) | (Key policies)   |       |
|  +------------------+------------------+------------------+       |
|  | Lambda Functions | SQS Queues       | Secrets Manager  |       |
|  | (Resource policy)| (Queue policies) | (Resource policy)|       |
|  +------------------+------------------+------------------+       |
|           |                                                       |
|           v                                                       |
|  +--------------------------------------------------+            |
|  |              FINDINGS                             |            |
|  | - Public access detected                          |            |
|  | - Cross-account access found                      |            |
|  | - External principal has access                   |            |
|  +--------------------------------------------------+            |
|                                                                   |
+------------------------------------------------------------------+
```

### Setting Up Access Analyzer

```bash
# Create an analyzer
aws accessanalyzer create-analyzer \
    --analyzer-name my-account-analyzer \
    --type ACCOUNT

# Or for organization-level analysis
aws accessanalyzer create-analyzer \
    --analyzer-name my-org-analyzer \
    --type ORGANIZATION

# List findings
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer

# Get finding details
aws accessanalyzer get-finding \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --id <finding-id>

# Archive a finding (after investigation)
aws accessanalyzer update-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
    --ids <finding-id> \
    --status ARCHIVED
```

### Responding to Findings

```
+------------------------------------------------------------------+
|              ACCESS ANALYZER FINDING WORKFLOW                     |
+------------------------------------------------------------------+
|                                                                   |
|  1. FINDING GENERATED                                            |
|     "S3 bucket 'company-data' allows public access"              |
|     |                                                             |
|     v                                                             |
|  2. INVESTIGATE                                                  |
|     - Is this intentional?                                       |
|     - Who configured this?                                       |
|     - What data is exposed?                                      |
|     |                                                             |
|     +----------+----------+                                       |
|     |                     |                                       |
|  INTENDED             UNINTENDED                                  |
|     |                     |                                       |
|     v                     v                                       |
|  3a. ARCHIVE           3b. REMEDIATE                             |
|  (Mark as resolved)    (Fix the policy)                          |
|     |                     |                                       |
|     v                     v                                       |
|  4. DOCUMENT           4. VERIFY                                 |
|  (Add comment)         (Re-scan)                                 |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Security Audit Checklist

### Weekly Audit Tasks

```
+------------------------------------------------------------------+
|                    WEEKLY AUDIT CHECKLIST                         |
+------------------------------------------------------------------+

[ ] Review new IAM users created in the past week
[ ] Check for any new access keys created
[ ] Verify MFA is enabled for all console users
[ ] Review Access Analyzer findings
[ ] Check CloudTrail for unusual IAM activity
[ ] Verify no root account usage (except emergencies)

+------------------------------------------------------------------+
```

### Monthly Audit Tasks

```
+------------------------------------------------------------------+
|                   MONTHLY AUDIT CHECKLIST                         |
+------------------------------------------------------------------+

[ ] Generate and review credential report
[ ] Identify and investigate unused credentials (90+ days)
[ ] Review all cross-account roles and their access
[ ] Audit inline policies for policy sprawl
[ ] Check for overly permissive policies (wildcards)
[ ] Verify password policy compliance
[ ] Review and update group memberships
[ ] Test backup admin access procedures
[ ] Review service-linked roles for unused services

+------------------------------------------------------------------+
```

### Quarterly Audit Tasks

```
+------------------------------------------------------------------+
|                  QUARTERLY AUDIT CHECKLIST                        |
+------------------------------------------------------------------+

[ ] Full IAM policy review
    - Remove unused permissions (last accessed data)
    - Consolidate duplicate policies
    - Update policies for new requirements

[ ] Access key rotation
    - Rotate all active access keys
    - Deactivate and remove old keys

[ ] Role review
    - Verify trust policies are current
    - Update permission boundaries
    - Review cross-account relationships

[ ] Compliance verification
    - Document exceptions
    - Update security procedures
    - Train team on changes

[ ] Emergency access review
    - Verify break-glass procedures
    - Test emergency admin accounts
    - Update contact lists

+------------------------------------------------------------------+
```

### Audit Commands

```bash
# Generate credential report
aws iam generate-credential-report
sleep 5
aws iam get-credential-report --query 'Content' --output text | base64 -d > credential-report.csv

# Find users without MFA
aws iam list-users --query 'Users[*].UserName' --output text | while read user; do
    mfa=$(aws iam list-mfa-devices --user-name "$user" --query 'MFADevices' --output text)
    if [ -z "$mfa" ]; then
        echo "NO MFA: $user"
    fi
done

# Find policies with admin access
aws iam list-policies --scope Local --query 'Policies[*].Arn' --output text | while read arn; do
    version=$(aws iam get-policy --policy-arn "$arn" --query 'Policy.DefaultVersionId' --output text)
    doc=$(aws iam get-policy-version --policy-arn "$arn" --version-id "$version" --query 'PolicyVersion.Document' --output json)
    if echo "$doc" | grep -q '"Action": "\*"'; then
        echo "ADMIN ACCESS: $arn"
    fi
done

# Find resources with public access (Access Analyzer)
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-analyzer \
    --filter 'isPublic={"eq": ["true"]}'

# List all cross-account role assumptions in last 24 hours (CloudTrail)
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRole \
    --start-time $(date -d '24 hours ago' --iso-8601=seconds) \
    --query 'Events[*].CloudTrailEvent' --output text
```

---

## Root Account Protection

### Root Account Best Practices

```
+------------------------------------------------------------------+
|                  ROOT ACCOUNT PROTECTION                          |
+------------------------------------------------------------------+

1. ENABLE MFA IMMEDIATELY
   - Use hardware MFA if possible
   - Store backup codes securely (offline)

2. DO NOT CREATE ACCESS KEYS
   - Root should never have programmatic access
   - Delete any existing root access keys

3. USE ONLY FOR SPECIFIC TASKS
   Allowed root account operations:
   - Change account settings (email, password)
   - View certain billing reports
   - Close the AWS account
   - Restore IAM user permissions (if all admins locked out)
   - Change AWS support plan
   - Register as seller in Marketplace

4. SET UP ALERTS
   - CloudWatch alarm for any root account usage
   - SNS notification for root console login

5. STORE CREDENTIALS SECURELY
   - Use a password manager
   - Store MFA device in secure location
   - Document break-glass procedure

+------------------------------------------------------------------+
```

### Root Account Monitoring

```bash
# Create CloudWatch alarm for root account usage
aws cloudwatch put-metric-alarm \
    --alarm-name RootAccountUsage \
    --alarm-description "Alarm when root account is used" \
    --metric-name RootAccountUsageCount \
    --namespace CloudTrailMetrics \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:security-alerts
```

---

## Common Security Mistakes

### Mistake 1: Using Root Account Daily

```
PROBLEM:
Root account used for everyday tasks

RISKS:
- No audit trail per person
- Cannot use MFA conditions
- Full account access if compromised
- Cannot limit permissions

SOLUTION:
- Create IAM admin user/role
- Lock root credentials
- Use root only for account-level tasks
- Set up alerts for root usage
```

### Mistake 2: Sharing Access Keys

```
PROBLEM:
Multiple developers using same access keys

RISKS:
- Cannot audit individual actions
- Cannot revoke individual access
- Key rotation affects everyone
- Increased exposure risk

SOLUTION:
- Each developer gets own IAM user
- Use IAM roles where possible
- Implement key rotation procedures
- Monitor key usage per user
```

### Mistake 3: Not Using Groups

```
PROBLEM:
Policies attached directly to users

RISKS:
- Inconsistent permissions
- Difficult to audit
- Time-consuming to update
- Easy to miss users during changes

SOLUTION:
- Create groups by function/team
- Attach policies to groups
- Add users to appropriate groups
- Use groups for permission changes
```

### Mistake 4: Ignoring Old Credentials

```
PROBLEM:
Access keys and passwords never rotated

RISKS:
- Longer exposure window
- May violate compliance
- Former employee access
- Harder to detect compromise

SOLUTION:
- Enforce 90-day rotation
- Use AWS Config rules
- Monitor last used dates
- Automate credential reports
```

### Mistake 5: Overly Permissive Policies

```json
// PROBLEM: The classic "it works" policy
{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
}

// SOLUTION: Specific permissions
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSpecificS3Actions",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "10.0.0.0/8"
                }
            }
        }
    ]
}
```

---

## AWS Config Rules for IAM

### Essential IAM Config Rules

```bash
# Enable AWS Config first, then add rules:

# Check for root MFA
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "root-account-mfa-enabled",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "ROOT_ACCOUNT_MFA_ENABLED"
    }
}'

# Check for user MFA
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "iam-user-mfa-enabled",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "IAM_USER_MFA_ENABLED"
    }
}'

# Check for unused credentials
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "iam-user-unused-credentials-check",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "IAM_USER_UNUSED_CREDENTIALS_CHECK"
    },
    "InputParameters": "{\"maxCredentialUsageAge\":\"90\"}"
}'

# Check for access key rotation
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "access-keys-rotated",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "ACCESS_KEYS_ROTATED"
    },
    "InputParameters": "{\"maxAccessKeyAge\":\"90\"}"
}'

# Check for password policy
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "iam-password-policy",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "IAM_PASSWORD_POLICY"
    },
    "InputParameters": "{\"RequireUppercaseCharacters\":\"true\",\"RequireLowercaseCharacters\":\"true\",\"RequireSymbols\":\"true\",\"RequireNumbers\":\"true\",\"MinimumPasswordLength\":\"14\",\"PasswordReusePrevention\":\"24\",\"MaxPasswordAge\":\"90\"}"
}'
```

---

## Summary: IAM Security Commandments

```
+------------------------------------------------------------------+
|                 THE 10 IAM SECURITY COMMANDMENTS                  |
+------------------------------------------------------------------+

1. Thou shalt not use root account for daily tasks

2. Thou shalt enable MFA for all human users

3. Thou shalt follow the principle of least privilege

4. Thou shalt use roles instead of long-term credentials

5. Thou shalt rotate access keys every 90 days

6. Thou shalt use groups for permission management

7. Thou shalt monitor and audit IAM activity regularly

8. Thou shalt not share credentials between users

9. Thou shalt use conditions for additional security

10. Thou shalt automate security checks with AWS Config

+------------------------------------------------------------------+
```

---

## Next Steps

Continue to [06-identity-federation.md](./06-identity-federation.md) to learn about integrating external identity providers with AWS IAM.
