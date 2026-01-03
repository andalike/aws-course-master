# IAM Users and Groups: Complete Management Guide

## Introduction

This document covers the practical aspects of creating and managing IAM users and groups, including credential management, password policies, and organizational best practices.

---

## Part 1: IAM Users

### User Lifecycle

```
+------------------------------------------------------------------+
|                       USER LIFECYCLE                              |
+------------------------------------------------------------------+
|                                                                   |
|  1. CREATE       2. CONFIGURE      3. MAINTAIN      4. OFFBOARD  |
|  +----------+    +------------+    +------------+   +----------+ |
|  | Create   |    | Add to     |    | Rotate     |   | Remove   | |
|  | user     |--->| groups     |--->| credentials|--->| from     | |
|  |          |    | Set perms  |    | Audit      |   | groups   | |
|  +----------+    | Enable MFA |    | access     |   | Delete   | |
|                  +------------+    +------------+   +----------+ |
|                                                                   |
+------------------------------------------------------------------+
```

### Creating IAM Users

#### Via AWS Console

1. Navigate to IAM Dashboard
2. Click "Users" in left sidebar
3. Click "Create user"
4. Enter username (follow naming convention)
5. Select access type:
   - Console access: for AWS Management Console
   - Programmatic access: for CLI/SDK/API
6. Set permissions (via groups or direct policies)
7. Review and create
8. **IMPORTANT**: Download or save credentials immediately

#### Via AWS CLI

```bash
# Create a basic user
aws iam create-user --user-name john.smith

# Create user with path (organizational structure)
aws iam create-user \
    --user-name john.smith \
    --path /developers/backend/ \
    --tags Key=Department,Value=Engineering Key=CostCenter,Value=12345

# Create user with permission boundary
aws iam create-user \
    --user-name intern.jane \
    --permissions-boundary arn:aws:iam::123456789012:policy/InternBoundary

# Verify user creation
aws iam get-user --user-name john.smith
```

### User Naming Conventions

```
+------------------------------------------------------------------+
|                     NAMING CONVENTIONS                            |
+------------------------------------------------------------------+
|                                                                   |
|  Pattern: firstname.lastname or email                            |
|                                                                   |
|  Examples:                                                        |
|  - john.smith          (simple, common)                          |
|  - jsmith              (short, may conflict)                     |
|  - john.smith@company.com (matches corporate identity)           |
|                                                                   |
|  Service Accounts:                                                |
|  - svc-application-name                                          |
|  - app-jenkins-deploy                                            |
|  - bot-cicd-pipeline                                             |
|                                                                   |
|  Constraints:                                                     |
|  - Max 64 characters                                             |
|  - Alphanumeric plus: + = , . @ - _                              |
|  - Must be unique in account                                     |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Part 2: User Credentials

### Console Access (Password)

#### Create Console Password

```bash
# Create login profile with auto-generated password
aws iam create-login-profile \
    --user-name john.smith \
    --password 'TempP@ssw0rd123!' \
    --password-reset-required

# Note: User must change password on first login
```

#### Update Console Password

```bash
# Admin changes user password
aws iam update-login-profile \
    --user-name john.smith \
    --password 'NewP@ssw0rd456!' \
    --password-reset-required

# User changes own password
aws iam change-password \
    --old-password 'CurrentPassword' \
    --new-password 'NewPassword123!'
```

#### Delete Console Access

```bash
aws iam delete-login-profile --user-name john.smith
```

### Programmatic Access (Access Keys)

```
+------------------------------------------------------------------+
|                       ACCESS KEYS                                 |
+------------------------------------------------------------------+
|                                                                   |
|  Components:                                                      |
|  +-------------------+  +--------------------------------+        |
|  | Access Key ID     |  | AKIA...                        |        |
|  | (Public, 20 char) |  | (OK to share for reference)    |        |
|  +-------------------+  +--------------------------------+        |
|  +-------------------+  +--------------------------------+        |
|  | Secret Access Key |  | wJalrXUtnFEMI/K7MDENG...       |        |
|  | (Secret, 40 char) |  | (NEVER share, shown once!)     |        |
|  +-------------------+  +--------------------------------+        |
|                                                                   |
|  Rules:                                                           |
|  - Max 2 access keys per user                                    |
|  - Secret key shown ONLY at creation                             |
|  - Should be rotated every 90 days                               |
|  - Never commit to code repositories                             |
|                                                                   |
+------------------------------------------------------------------+
```

#### Create Access Keys

```bash
# Create access key
aws iam create-access-key --user-name john.smith

# Output (SAVE THIS!):
# {
#     "AccessKey": {
#         "UserName": "john.smith",
#         "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
#         "Status": "Active",
#         "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
#         "CreateDate": "2024-01-15T12:00:00Z"
#     }
# }
```

#### List and Manage Access Keys

```bash
# List access keys for a user
aws iam list-access-keys --user-name john.smith

# Get last used info
aws iam get-access-key-last-used --access-key-id AKIAIOSFODNN7EXAMPLE

# Deactivate (but keep) access key
aws iam update-access-key \
    --user-name john.smith \
    --access-key-id AKIAIOSFODNN7EXAMPLE \
    --status Inactive

# Reactivate access key
aws iam update-access-key \
    --user-name john.smith \
    --access-key-id AKIAIOSFODNN7EXAMPLE \
    --status Active

# Delete access key
aws iam delete-access-key \
    --user-name john.smith \
    --access-key-id AKIAIOSFODNN7EXAMPLE
```

#### Access Key Rotation Process

```
+------------------------------------------------------------------+
|                   ACCESS KEY ROTATION                             |
+------------------------------------------------------------------+
|                                                                   |
|  Step 1: Create new access key (user now has 2 keys)            |
|  +----------+                                                     |
|  | Key 1    | Active (old)                                       |
|  | Key 2    | Active (new)                                       |
|  +----------+                                                     |
|                                                                   |
|  Step 2: Update applications to use new key                      |
|  +----------+                                                     |
|  | App 1    | Uses Key 2                                         |
|  | App 2    | Uses Key 2                                         |
|  +----------+                                                     |
|                                                                   |
|  Step 3: Deactivate old key (test period)                        |
|  +----------+                                                     |
|  | Key 1    | Inactive                                           |
|  | Key 2    | Active                                             |
|  +----------+                                                     |
|                                                                   |
|  Step 4: Delete old key after confirming everything works        |
|  +----------+                                                     |
|  | Key 2    | Active (only key)                                  |
|  +----------+                                                     |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Part 3: Password Policies

### Account Password Policy

The password policy applies to all IAM users in the account.

```bash
# Get current password policy
aws iam get-account-password-policy

# Update password policy
aws iam update-account-password-policy \
    --minimum-password-length 14 \
    --require-symbols \
    --require-numbers \
    --require-uppercase-characters \
    --require-lowercase-characters \
    --allow-users-to-change-password \
    --max-password-age 90 \
    --password-reuse-prevention 12 \
    --hard-expiry
```

### Password Policy Options

| Option | Description | Recommended |
|--------|-------------|-------------|
| `--minimum-password-length` | Min characters (6-128) | 14+ |
| `--require-symbols` | Special characters required | Yes |
| `--require-numbers` | Numbers required | Yes |
| `--require-uppercase-characters` | Uppercase required | Yes |
| `--require-lowercase-characters` | Lowercase required | Yes |
| `--allow-users-to-change-password` | Users can change own | Yes |
| `--max-password-age` | Days until expiry (1-1095) | 90 |
| `--password-reuse-prevention` | Previous passwords blocked (1-24) | 12 |
| `--hard-expiry` | Require admin reset after expiry | Depends |

### Recommended Password Policy

```json
{
    "MinimumPasswordLength": 14,
    "RequireSymbols": true,
    "RequireNumbers": true,
    "RequireUppercaseCharacters": true,
    "RequireLowercaseCharacters": true,
    "AllowUsersToChangePassword": true,
    "MaxPasswordAge": 90,
    "PasswordReusePrevention": 12,
    "HardExpiry": false
}
```

---

## Part 4: IAM Groups

### Group Strategy

```
+------------------------------------------------------------------+
|                       GROUP STRATEGIES                            |
+------------------------------------------------------------------+

STRATEGY 1: BY JOB FUNCTION
+-------------+-------------+-------------+-------------+
| Admins      | Developers  | QA          | Finance     |
+-------------+-------------+-------------+-------------+
| Full access | Dev access  | Test access | Billing     |
| to all      | to dev      | to test     | access      |
| resources   | resources   | resources   | only        |
+-------------+-------------+-------------+-------------+

STRATEGY 2: BY ENVIRONMENT
+-------------+-------------+-------------+
| Production  | Staging     | Development |
+-------------+-------------+-------------+
| Prod-only   | Stage-only  | Dev-only    |
| resources   | resources   | resources   |
+-------------+-------------+-------------+

STRATEGY 3: BY PROJECT
+-------------+-------------+-------------+
| Project-A   | Project-B   | Project-C   |
+-------------+-------------+-------------+
| All Project | All Project | All Project |
| A resources | B resources | C resources |
+-------------+-------------+-------------+

STRATEGY 4: HYBRID (RECOMMENDED)
+------------------------------------------------------------------+
|                                                                   |
|   FUNCTIONAL GROUPS          ENVIRONMENT GROUPS                   |
|   (What you can do)          (Where you can do it)               |
|   +-------------+            +-------------+                      |
|   | Developers  |            | DevEnv      |                      |
|   +-------------+            +-------------+                      |
|   +-------------+            +-------------+                      |
|   | DataScience |            | StageEnv    |                      |
|   +-------------+            +-------------+                      |
|   +-------------+            +-------------+                      |
|   | Operations  |            | ProdEnv     |                      |
|   +-------------+            +-------------+                      |
|                                                                   |
|   A developer might be in: Developers + DevEnv + StageEnv        |
|   A senior dev might be in: Developers + DevEnv + StageEnv + Prod|
|                                                                   |
+------------------------------------------------------------------+
```

### Creating and Managing Groups

```bash
# Create a group
aws iam create-group --group-name Developers

# Create group with path
aws iam create-group \
    --group-name BackendDevelopers \
    --path /engineering/

# List all groups
aws iam list-groups

# Get group details
aws iam get-group --group-name Developers

# Delete a group (must be empty)
aws iam delete-group --group-name Developers
```

### Managing Group Membership

```bash
# Add user to group
aws iam add-user-to-group \
    --user-name john.smith \
    --group-name Developers

# Add user to multiple groups
for group in Developers DevEnvironment ProjectAlpha; do
    aws iam add-user-to-group --user-name john.smith --group-name $group
done

# List groups for a user
aws iam list-groups-for-user --user-name john.smith

# List users in a group
aws iam get-group --group-name Developers

# Remove user from group
aws iam remove-user-from-group \
    --user-name john.smith \
    --group-name Developers
```

### Attaching Policies to Groups

```bash
# Attach AWS managed policy
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Attach customer managed policy
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::123456789012:policy/DevEnvironmentAccess

# List attached policies
aws iam list-attached-group-policies --group-name Developers

# Detach policy from group
aws iam detach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

---

## Part 5: Recommended Group Structure

### Standard Group Template

```bash
#!/bin/bash
# Script to create standard group structure

# Administrative Groups
aws iam create-group --group-name Administrators
aws iam create-group --group-name SecurityAuditors
aws iam create-group --group-name BillingAdministrators

# Development Groups
aws iam create-group --group-name Developers
aws iam create-group --group-name SeniorDevelopers
aws iam create-group --group-name DevOps

# Environment Groups
aws iam create-group --group-name DevelopmentEnv
aws iam create-group --group-name StagingEnv
aws iam create-group --group-name ProductionReadOnly
aws iam create-group --group-name ProductionAdmin

# Service-Specific Groups
aws iam create-group --group-name DatabaseAdmins
aws iam create-group --group-name NetworkAdmins
aws iam create-group --group-name S3Admins

# Read-Only Groups
aws iam create-group --group-name ReadOnlyAll
aws iam create-group --group-name ReadOnlyBilling

# Attach appropriate policies (examples)
aws iam attach-group-policy \
    --group-name Administrators \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

aws iam attach-group-policy \
    --group-name ReadOnlyAll \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

aws iam attach-group-policy \
    --group-name SecurityAuditors \
    --policy-arn arn:aws:iam::aws:policy/SecurityAudit
```

### Example Group Policies

#### Developer Group Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowDeveloperServices",
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:RunInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "s3:*",
                "dynamodb:*",
                "lambda:*",
                "logs:*",
                "cloudwatch:*",
                "sns:*",
                "sqs:*"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Sid": "DenyProductionResources",
            "Effect": "Deny",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:ResourceTag/Environment": "Production"
                }
            }
        }
    ]
}
```

#### Security Auditor Group Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSecurityAudit",
            "Effect": "Allow",
            "Action": [
                "access-analyzer:*",
                "cloudtrail:Describe*",
                "cloudtrail:Get*",
                "cloudtrail:List*",
                "cloudtrail:LookupEvents",
                "config:Describe*",
                "config:Get*",
                "config:List*",
                "guardduty:Get*",
                "guardduty:List*",
                "iam:Get*",
                "iam:List*",
                "iam:GenerateCredentialReport",
                "iam:GenerateServiceLastAccessedDetails",
                "inspector:Describe*",
                "inspector:Get*",
                "inspector:List*",
                "kms:Describe*",
                "kms:Get*",
                "kms:List*",
                "s3:GetBucket*",
                "s3:ListBucket*",
                "securityhub:*"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Part 6: User and Group Auditing

### Generate Credential Report

```bash
# Request credential report generation
aws iam generate-credential-report

# Download credential report
aws iam get-credential-report --query 'Content' --output text | base64 -d > credential-report.csv
```

### Credential Report Contents

| Field | Description |
|-------|-------------|
| `user` | Username |
| `arn` | User ARN |
| `user_creation_time` | When user was created |
| `password_enabled` | Has console access |
| `password_last_used` | Last console login |
| `password_last_changed` | Last password change |
| `password_next_rotation` | When password expires |
| `mfa_active` | MFA enabled |
| `access_key_1_active` | First key active |
| `access_key_1_last_used_date` | First key last used |
| `access_key_2_active` | Second key active |
| `access_key_2_last_used_date` | Second key last used |

### Audit Script

```bash
#!/bin/bash
# IAM User Audit Script

echo "=== IAM Users with Console Access but No MFA ==="
aws iam list-users --query 'Users[*].UserName' --output text | while read user; do
    mfa=$(aws iam list-mfa-devices --user-name "$user" --query 'MFADevices[*].SerialNumber' --output text)
    login=$(aws iam get-login-profile --user-name "$user" 2>/dev/null)
    if [ -n "$login" ] && [ -z "$mfa" ]; then
        echo "WARNING: $user has console access but no MFA"
    fi
done

echo ""
echo "=== IAM Users with Old Access Keys (>90 days) ==="
aws iam list-users --query 'Users[*].UserName' --output text | while read user; do
    aws iam list-access-keys --user-name "$user" --query 'AccessKeyMetadata[*].[AccessKeyId,CreateDate]' --output text | while read keyid created; do
        age=$(( ( $(date +%s) - $(date -d "$created" +%s) ) / 86400 ))
        if [ "$age" -gt 90 ]; then
            echo "WARNING: $user has access key $keyid that is $age days old"
        fi
    done
done

echo ""
echo "=== IAM Users with No Activity in 90 Days ==="
aws iam list-users --query 'Users[*].UserName' --output text | while read user; do
    last_used=$(aws iam get-user --user-name "$user" --query 'User.PasswordLastUsed' --output text 2>/dev/null)
    if [ "$last_used" != "None" ] && [ -n "$last_used" ]; then
        age=$(( ( $(date +%s) - $(date -d "$last_used" +%s) ) / 86400 ))
        if [ "$age" -gt 90 ]; then
            echo "WARNING: $user last logged in $age days ago"
        fi
    fi
done
```

---

## Part 7: User Offboarding

### Offboarding Checklist

```
+------------------------------------------------------------------+
|                   USER OFFBOARDING CHECKLIST                      |
+------------------------------------------------------------------+

[ ] 1. Disable console password (or delete login profile)
[ ] 2. Deactivate all access keys
[ ] 3. Remove from all groups
[ ] 4. Detach all directly attached policies
[ ] 5. Delete inline policies
[ ] 6. Deactivate MFA devices
[ ] 7. Delete signing certificates
[ ] 8. Delete SSH public keys
[ ] 9. Delete Git credentials
[ ] 10. Delete the user

Optional:
[ ] Review CloudTrail logs for recent activity
[ ] Check for any resources owned by the user
[ ] Update any shared credentials/secrets
+------------------------------------------------------------------+
```

### Offboarding Script

```bash
#!/bin/bash
# User Offboarding Script
# Usage: ./offboard-user.sh username

USER=$1

if [ -z "$USER" ]; then
    echo "Usage: $0 username"
    exit 1
fi

echo "Offboarding user: $USER"

# 1. Delete login profile (console access)
echo "Removing console access..."
aws iam delete-login-profile --user-name "$USER" 2>/dev/null

# 2. Deactivate and delete access keys
echo "Removing access keys..."
aws iam list-access-keys --user-name "$USER" --query 'AccessKeyMetadata[*].AccessKeyId' --output text | while read key; do
    aws iam update-access-key --user-name "$USER" --access-key-id "$key" --status Inactive
    aws iam delete-access-key --user-name "$USER" --access-key-id "$key"
done

# 3. Remove from groups
echo "Removing from groups..."
aws iam list-groups-for-user --user-name "$USER" --query 'Groups[*].GroupName' --output text | while read group; do
    aws iam remove-user-from-group --user-name "$USER" --group-name "$group"
done

# 4. Detach managed policies
echo "Detaching managed policies..."
aws iam list-attached-user-policies --user-name "$USER" --query 'AttachedPolicies[*].PolicyArn' --output text | while read policy; do
    aws iam detach-user-policy --user-name "$USER" --policy-arn "$policy"
done

# 5. Delete inline policies
echo "Deleting inline policies..."
aws iam list-user-policies --user-name "$USER" --query 'PolicyNames[*]' --output text | while read policy; do
    aws iam delete-user-policy --user-name "$USER" --policy-name "$policy"
done

# 6. Deactivate and delete MFA devices
echo "Removing MFA devices..."
aws iam list-mfa-devices --user-name "$USER" --query 'MFADevices[*].SerialNumber' --output text | while read mfa; do
    aws iam deactivate-mfa-device --user-name "$USER" --serial-number "$mfa"
    aws iam delete-virtual-mfa-device --serial-number "$mfa" 2>/dev/null
done

# 7. Delete signing certificates
echo "Removing signing certificates..."
aws iam list-signing-certificates --user-name "$USER" --query 'Certificates[*].CertificateId' --output text | while read cert; do
    aws iam delete-signing-certificate --user-name "$USER" --certificate-id "$cert"
done

# 8. Delete SSH public keys
echo "Removing SSH keys..."
aws iam list-ssh-public-keys --user-name "$USER" --query 'SSHPublicKeys[*].SSHPublicKeyId' --output text | while read key; do
    aws iam delete-ssh-public-key --user-name "$USER" --ssh-public-key-id "$key"
done

# 9. Delete service specific credentials (CodeCommit)
echo "Removing service credentials..."
aws iam list-service-specific-credentials --user-name "$USER" --query 'ServiceSpecificCredentials[*].ServiceSpecificCredentialId' --output text | while read cred; do
    aws iam delete-service-specific-credential --user-name "$USER" --service-specific-credential-id "$cred"
done

# 10. Delete the user
echo "Deleting user..."
aws iam delete-user --user-name "$USER"

echo "User $USER has been offboarded successfully."
```

---

## Part 8: Common Mistakes and Solutions

### Mistake 1: Not Using Groups

```
PROBLEM:
+--------+     +-----------+
| User 1 |---->| Policy A  |
| User 2 |---->| Policy A  |  (Policy attached 3 times)
| User 3 |---->| Policy A  |
+--------+     +-----------+

To update permissions, you must update all 3 users individually.

SOLUTION:
+--------+     +----------+     +-----------+
| User 1 |---->|          |     |           |
| User 2 |---->|  Group   |---->| Policy A  |
| User 3 |---->|          |     |           |
+--------+     +----------+     +-----------+

Update the group policy once, all users get the change.
```

### Mistake 2: Shared Credentials

```
PROBLEM:
Multiple developers sharing one set of access keys
- Cannot audit individual actions
- Cannot revoke individual access
- Credential leak affects everyone

SOLUTION:
Each developer has their own IAM user with own credentials
- Individual CloudTrail audit logs
- Revoke one user without affecting others
- Specific permissions per user if needed
```

### Mistake 3: Not Rotating Credentials

```
PROBLEM:
Access keys created 2 years ago, never rotated
- Higher risk of compromise over time
- May violate compliance requirements
- Harder to track if leaked

SOLUTION:
Implement 90-day rotation policy
- Use AWS Config rules to detect old keys
- Automate rotation reminders
- Set up alerts for unused credentials
```

### Mistake 4: Overly Permissive Policies

```
PROBLEM:
{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
}

SOLUTION:
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::specific-bucket/*"
}
```

---

## Summary

### Key Commands Reference

```bash
# USER MANAGEMENT
aws iam create-user --user-name <name>
aws iam delete-user --user-name <name>
aws iam list-users

# CREDENTIALS
aws iam create-login-profile --user-name <name> --password <pass>
aws iam create-access-key --user-name <name>
aws iam delete-access-key --user-name <name> --access-key-id <key>

# GROUP MANAGEMENT
aws iam create-group --group-name <name>
aws iam delete-group --group-name <name>
aws iam add-user-to-group --user-name <user> --group-name <group>
aws iam remove-user-from-group --user-name <user> --group-name <group>

# POLICY ATTACHMENT
aws iam attach-group-policy --group-name <group> --policy-arn <arn>
aws iam attach-user-policy --user-name <user> --policy-arn <arn>
aws iam detach-group-policy --group-name <group> --policy-arn <arn>

# AUDITING
aws iam generate-credential-report
aws iam get-credential-report
aws iam get-access-key-last-used --access-key-id <key>
```

---

## Next Steps

Continue to [04-iam-roles.md](./04-iam-roles.md) to learn about IAM roles, which provide temporary credentials and are essential for secure AWS architecture.
