# IAM Hands-On Lab: Complete Practical Exercises

## Lab Overview

This comprehensive lab will give you hands-on experience with all major IAM concepts. You will create users, groups, policies, and roles while implementing security best practices.

---

## Prerequisites

Before starting this lab, ensure you have:

1. **AWS Account**: An AWS account with administrative access
2. **AWS CLI**: Installed and configured with credentials
3. **Text Editor**: For creating JSON policy files
4. **MFA Device**: A smartphone with an authenticator app (Google Authenticator, Authy, etc.)

### Verify Your Setup

```bash
# Check AWS CLI version
aws --version

# Verify your credentials
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAXXXXXXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }
```

> **WARNING**: This lab creates real AWS resources. While IAM is free, some resources may incur charges. Make sure to complete the cleanup section at the end.

---

## Lab Architecture

```
+------------------------------------------------------------------+
|                    LAB ENVIRONMENT                                |
+------------------------------------------------------------------+
|                                                                   |
|  USERS:                    GROUPS:                                |
|  +---------------+        +------------------+                    |
|  | lab-admin     |------->| lab-admins       |                    |
|  +---------------+        +------------------+                    |
|  | lab-developer |------->| lab-developers   |                    |
|  +---------------+        +------------------+                    |
|  | lab-auditor   |------->| lab-auditors     |                    |
|  +---------------+        +------------------+                    |
|                                                                   |
|  ROLES:                    POLICIES:                              |
|  +------------------+     +----------------------+                 |
|  | lab-ec2-s3-role  |     | lab-developer-policy |                 |
|  +------------------+     | lab-auditor-policy   |                 |
|  | lab-lambda-role  |     | lab-mfa-required     |                 |
|  +------------------+     +----------------------+                 |
|                                                                   |
|  RESOURCES:                                                       |
|  +------------------+                                              |
|  | lab-iam-bucket   | (S3 bucket for testing)                     |
|  +------------------+                                              |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Exercise 1: Create IAM Users and Groups

### Objective
Create a basic IAM structure with users organized into groups by job function.

### Duration: 15-20 minutes

### Step 1.1: Create IAM Groups

#### Via AWS Console

1. Navigate to **IAM** > **User groups**
2. Click **Create group**
3. Create three groups:
   - Name: `lab-admins` - Click **Create group**
   - Name: `lab-developers` - Click **Create group**
   - Name: `lab-auditors` - Click **Create group**

#### Via AWS CLI

```bash
# Create the groups
aws iam create-group --group-name lab-admins
aws iam create-group --group-name lab-developers
aws iam create-group --group-name lab-auditors

# Verify groups were created
aws iam list-groups --query 'Groups[?starts_with(GroupName, `lab-`)].GroupName'
```

**Expected Output:**
```json
[
    "lab-admins",
    "lab-developers",
    "lab-auditors"
]
```

### Step 1.2: Create IAM Users

#### Via AWS Console

1. Navigate to **IAM** > **Users**
2. Click **Create user**
3. For each user:
   - User name: `lab-admin`, `lab-developer`, `lab-auditor`
   - Select **Provide user access to the AWS Management Console**
   - Select **I want to create an IAM user**
   - Choose **Custom password** and enter a temporary password
   - Check **Users must create a new password at next sign-in**
   - Click **Next** > **Create user**

#### Via AWS CLI

```bash
# Create users
aws iam create-user --user-name lab-admin
aws iam create-user --user-name lab-developer
aws iam create-user --user-name lab-auditor

# Create console passwords (users will need to change on first login)
# Replace 'TempPassword123!' with a secure password
aws iam create-login-profile \
    --user-name lab-admin \
    --password 'TempPassword123!' \
    --password-reset-required

aws iam create-login-profile \
    --user-name lab-developer \
    --password 'TempPassword123!' \
    --password-reset-required

aws iam create-login-profile \
    --user-name lab-auditor \
    --password 'TempPassword123!' \
    --password-reset-required

# Verify users were created
aws iam list-users --query 'Users[?starts_with(UserName, `lab-`)].UserName'
```

### Step 1.3: Add Users to Groups

#### Via AWS Console

1. Navigate to **IAM** > **User groups** > Select `lab-admins`
2. Click **Users** tab > **Add users**
3. Select `lab-admin` and click **Add users**
4. Repeat for other groups:
   - Add `lab-developer` to `lab-developers`
   - Add `lab-auditor` to `lab-auditors`

#### Via AWS CLI

```bash
# Add users to their respective groups
aws iam add-user-to-group --user-name lab-admin --group-name lab-admins
aws iam add-user-to-group --user-name lab-developer --group-name lab-developers
aws iam add-user-to-group --user-name lab-auditor --group-name lab-auditors

# Verify group membership
aws iam get-group --group-name lab-admins --query 'Users[*].UserName'
aws iam get-group --group-name lab-developers --query 'Users[*].UserName'
aws iam get-group --group-name lab-auditors --query 'Users[*].UserName'
```

### Verification

```bash
# List all lab users and their groups
for user in lab-admin lab-developer lab-auditor; do
    echo "=== $user ==="
    aws iam list-groups-for-user --user-name $user --query 'Groups[*].GroupName'
done
```

**Expected Output:**
```
=== lab-admin ===
[
    "lab-admins"
]
=== lab-developer ===
[
    "lab-developers"
]
=== lab-auditor ===
[
    "lab-auditors"
]
```

> **CHECKPOINT**: You should now have 3 users and 3 groups. Each user belongs to one group.

---

## Exercise 2: Write Custom IAM Policies

### Objective
Create custom policies with least-privilege permissions for each group.

### Duration: 20-25 minutes

### Step 2.1: Create Developer Policy

This policy allows developers to work with EC2, S3, Lambda, and CloudWatch in a development context.

#### Create the Policy File

```bash
# Create a directory for policy files
mkdir -p ~/iam-lab-policies

# Create the developer policy
cat > ~/iam-lab-policies/lab-developer-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowEC2DescribeAndDevInstances",
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:RunInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:RebootInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Sid": "AllowEC2TerminateOnlyDevTagged",
            "Effect": "Allow",
            "Action": "ec2:TerminateInstances",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Environment": "Development"
                }
            }
        },
        {
            "Sid": "AllowS3ReadWriteDevBuckets",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::*-dev-*",
                "arn:aws:s3:::*-dev-*/*",
                "arn:aws:s3:::lab-*",
                "arn:aws:s3:::lab-*/*"
            ]
        },
        {
            "Sid": "AllowLambdaDev",
            "Effect": "Allow",
            "Action": [
                "lambda:CreateFunction",
                "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration",
                "lambda:InvokeFunction",
                "lambda:GetFunction",
                "lambda:ListFunctions",
                "lambda:DeleteFunction"
            ],
            "Resource": "arn:aws:lambda:us-east-1:*:function:dev-*"
        },
        {
            "Sid": "AllowCloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowIAMReadOnly",
            "Effect": "Allow",
            "Action": [
                "iam:GetUser",
                "iam:GetRole",
                "iam:GetPolicy",
                "iam:ListRoles",
                "iam:ListPolicies"
            ],
            "Resource": "*"
        }
    ]
}
EOF
```

#### Create the Policy in AWS

##### Via AWS Console

1. Navigate to **IAM** > **Policies** > **Create policy**
2. Click **JSON** tab
3. Paste the policy JSON content
4. Click **Next**
5. Policy name: `lab-developer-policy`
6. Description: `Custom policy for lab developers with limited access`
7. Click **Create policy**

##### Via AWS CLI

```bash
aws iam create-policy \
    --policy-name lab-developer-policy \
    --policy-document file://~/iam-lab-policies/lab-developer-policy.json \
    --description "Custom policy for lab developers with limited access"
```

### Step 2.2: Create Auditor Policy

This policy provides read-only access for security auditing purposes.

```bash
# Create the auditor policy
cat > ~/iam-lab-policies/lab-auditor-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSecurityAuditRead",
            "Effect": "Allow",
            "Action": [
                "access-analyzer:Get*",
                "access-analyzer:List*",
                "cloudtrail:Describe*",
                "cloudtrail:Get*",
                "cloudtrail:List*",
                "cloudtrail:LookupEvents",
                "cloudwatch:Describe*",
                "cloudwatch:Get*",
                "cloudwatch:List*",
                "config:Describe*",
                "config:Get*",
                "config:List*",
                "ec2:Describe*",
                "guardduty:Get*",
                "guardduty:List*",
                "iam:Get*",
                "iam:List*",
                "iam:GenerateCredentialReport",
                "iam:GenerateServiceLastAccessedDetails",
                "kms:Describe*",
                "kms:Get*",
                "kms:List*",
                "logs:Describe*",
                "logs:Get*",
                "logs:FilterLogEvents",
                "s3:GetBucket*",
                "s3:GetEncryptionConfiguration",
                "s3:GetLifecycleConfiguration",
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "securityhub:Get*",
                "securityhub:List*",
                "sns:Get*",
                "sns:List*",
                "sqs:Get*",
                "sqs:List*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DenyDataAccess",
            "Effect": "Deny",
            "Action": [
                "s3:GetObject",
                "dynamodb:GetItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the policy
aws iam create-policy \
    --policy-name lab-auditor-policy \
    --policy-document file://~/iam-lab-policies/lab-auditor-policy.json \
    --description "Read-only security audit policy for lab auditors"
```

### Step 2.3: Attach Policies to Groups

#### Via AWS Console

1. Navigate to **IAM** > **User groups** > Select `lab-admins`
2. Click **Permissions** tab > **Add permissions** > **Attach policies**
3. Search for `AdministratorAccess` and select it
4. Click **Attach policies**
5. Repeat for other groups:
   - `lab-developers`: Attach `lab-developer-policy`
   - `lab-auditors`: Attach `lab-auditor-policy`

#### Via AWS CLI

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Attach AdministratorAccess to lab-admins
aws iam attach-group-policy \
    --group-name lab-admins \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Attach custom developer policy to lab-developers
aws iam attach-group-policy \
    --group-name lab-developers \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-developer-policy

# Attach custom auditor policy to lab-auditors
aws iam attach-group-policy \
    --group-name lab-auditors \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-auditor-policy

# Verify attached policies
echo "=== lab-admins policies ==="
aws iam list-attached-group-policies --group-name lab-admins

echo "=== lab-developers policies ==="
aws iam list-attached-group-policies --group-name lab-developers

echo "=== lab-auditors policies ==="
aws iam list-attached-group-policies --group-name lab-auditors
```

### Verification

```bash
# Use the IAM Policy Simulator to test the developer policy
aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::${ACCOUNT_ID}:user/lab-developer \
    --action-names s3:GetObject ec2:TerminateInstances iam:CreateUser \
    --query 'EvaluationResults[*].[EvalActionName,EvalDecision]' \
    --output table
```

**Expected Output:**
```
-----------------------------------
|    SimulatePrincipalPolicy      |
+-----------------------+---------+
|  s3:GetObject         |  allowed|
|  ec2:TerminateInstances| allowed |
|  iam:CreateUser       |  implicitDeny |
+-----------------------+---------+
```

> **CHECKPOINT**: You should now have custom policies attached to each group.

---

## Exercise 3: Create and Assume IAM Roles

### Objective
Create IAM roles for EC2 instances and cross-account access, then practice assuming roles.

### Duration: 25-30 minutes

### Step 3.1: Create an EC2 Service Role

This role allows EC2 instances to access S3 and write to CloudWatch Logs.

#### Create Trust Policy

```bash
# Create trust policy for EC2
cat > ~/iam-lab-policies/ec2-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
```

#### Create Permission Policy

```bash
# Create permission policy for the role
cat > ~/iam-lab-policies/ec2-s3-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::lab-*",
                "arn:aws:s3:::lab-*/*"
            ]
        },
        {
            "Sid": "AllowCloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/ec2/*"
        }
    ]
}
EOF
```

#### Create the Role

##### Via AWS Console

1. Navigate to **IAM** > **Roles** > **Create role**
2. Select **AWS service** > **EC2**
3. Click **Next**
4. Skip adding permissions for now (we'll add custom policy)
5. Click **Next**
6. Role name: `lab-ec2-s3-role`
7. Description: `Role for EC2 instances to access S3 and CloudWatch`
8. Click **Create role**
9. Select the created role > **Add permissions** > **Create inline policy**
10. Click **JSON** tab, paste the `ec2-s3-policy.json` content
11. Click **Review policy** > Name: `ec2-s3-access` > **Create policy**

##### Via AWS CLI

```bash
# Create the role with trust policy
aws iam create-role \
    --role-name lab-ec2-s3-role \
    --assume-role-policy-document file://~/iam-lab-policies/ec2-trust-policy.json \
    --description "Role for EC2 instances to access S3 and CloudWatch"

# Create and attach the permission policy
aws iam put-role-policy \
    --role-name lab-ec2-s3-role \
    --policy-name ec2-s3-access \
    --policy-document file://~/iam-lab-policies/ec2-s3-policy.json

# Create instance profile (required for EC2)
aws iam create-instance-profile \
    --instance-profile-name lab-ec2-s3-profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name lab-ec2-s3-profile \
    --role-name lab-ec2-s3-role

# Verify the role
aws iam get-role --role-name lab-ec2-s3-role --query 'Role.Arn'
```

### Step 3.2: Create a Lambda Execution Role

```bash
# Create Lambda trust policy
cat > ~/iam-lab-policies/lambda-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the Lambda role
aws iam create-role \
    --role-name lab-lambda-execution-role \
    --assume-role-policy-document file://~/iam-lab-policies/lambda-trust-policy.json \
    --description "Execution role for Lambda functions"

# Attach basic execution policy (CloudWatch Logs)
aws iam attach-role-policy \
    --role-name lab-lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Verify
aws iam list-attached-role-policies --role-name lab-lambda-execution-role
```

### Step 3.3: Create a Role for User Assumption

This role can be assumed by the lab-admin user for elevated access.

```bash
# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create trust policy allowing lab-admin to assume the role
cat > ~/iam-lab-policies/admin-elevated-trust.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${ACCOUNT_ID}:user/lab-admin"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": "false"
                }
            }
        }
    ]
}
EOF

# Note: In production, you would set "aws:MultiFactorAuthPresent": "true"
# We set it to "false" for lab purposes only

# Create the role
aws iam create-role \
    --role-name lab-elevated-access-role \
    --assume-role-policy-document file://~/iam-lab-policies/admin-elevated-trust.json \
    --description "Elevated access role for lab-admin user"

# Attach PowerUserAccess policy
aws iam attach-role-policy \
    --role-name lab-elevated-access-role \
    --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
```

### Step 3.4: Practice Assuming a Role

```bash
# First, create access keys for lab-admin
aws iam create-access-key --user-name lab-admin

# Save the output! You'll need the Access Key ID and Secret Access Key
# Example output:
# {
#     "AccessKey": {
#         "UserName": "lab-admin",
#         "AccessKeyId": "AKIAXXXXXXXXXXXXXXXX",
#         "Status": "Active",
#         "SecretAccessKey": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#         "CreateDate": "2024-01-15T12:00:00+00:00"
#     }
# }

# Configure a new profile for lab-admin
aws configure --profile lab-admin
# Enter the Access Key ID and Secret Access Key when prompted
# Region: us-east-1
# Output format: json

# Allow lab-admin to assume roles
aws iam put-user-policy \
    --user-name lab-admin \
    --policy-name allow-assume-role \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": "arn:aws:iam::*:role/lab-*"
            }
        ]
    }'

# Now assume the role using the lab-admin profile
aws sts assume-role \
    --role-arn arn:aws:iam::${ACCOUNT_ID}:role/lab-elevated-access-role \
    --role-session-name lab-session \
    --profile lab-admin

# The output contains temporary credentials
# You can use these to make API calls as the assumed role
```

### Verification

```bash
# List all lab roles
aws iam list-roles --query 'Roles[?starts_with(RoleName, `lab-`)].RoleName'

# Verify instance profile
aws iam list-instance-profiles --query 'InstanceProfiles[?starts_with(InstanceProfileName, `lab-`)].InstanceProfileName'
```

> **CHECKPOINT**: You should now have 3 roles and 1 instance profile created.

---

## Exercise 4: Set Up Multi-Factor Authentication (MFA)

### Objective
Enable MFA for IAM users and create policies that require MFA for sensitive operations.

### Duration: 15-20 minutes

### Step 4.1: Create MFA-Required Policy

This policy denies all actions except MFA setup when MFA is not present.

```bash
cat > ~/iam-lab-policies/lab-mfa-required.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowViewAccountInfo",
            "Effect": "Allow",
            "Action": [
                "iam:GetAccountPasswordPolicy",
                "iam:ListVirtualMFADevices",
                "iam:ListUsers"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowManageOwnVirtualMFADevice",
            "Effect": "Allow",
            "Action": [
                "iam:CreateVirtualMFADevice",
                "iam:DeleteVirtualMFADevice"
            ],
            "Resource": "arn:aws:iam::*:mfa/${aws:username}"
        },
        {
            "Sid": "AllowManageOwnUserMFA",
            "Effect": "Allow",
            "Action": [
                "iam:DeactivateMFADevice",
                "iam:EnableMFADevice",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ResyncMFADevice"
            ],
            "Resource": "arn:aws:iam::*:user/${aws:username}"
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
EOF

# Create the policy
aws iam create-policy \
    --policy-name lab-mfa-required \
    --policy-document file://~/iam-lab-policies/lab-mfa-required.json \
    --description "Requires MFA for all actions except MFA setup"
```

### Step 4.2: Enable MFA for a User (Console Method)

1. Sign in as the IAM user (e.g., `lab-developer`)
2. Navigate to **IAM** > **Users** > Select your user
3. Go to **Security credentials** tab
4. In **Multi-factor authentication (MFA)** section, click **Assign MFA device**
5. Select **Authenticator app**
6. Click **Next**
7. Open your authenticator app (Google Authenticator, Authy, etc.)
8. Scan the QR code or enter the secret key manually
9. Enter two consecutive MFA codes from the app
10. Click **Add MFA**

### Step 4.3: Enable MFA via CLI (Virtual MFA)

```bash
# Create a virtual MFA device
aws iam create-virtual-mfa-device \
    --virtual-mfa-device-name lab-admin-mfa \
    --outfile ~/iam-lab-policies/lab-admin-mfa-qr.png \
    --bootstrap-method QRCodePNG

# The QR code is saved to lab-admin-mfa-qr.png
# Open this file and scan with your authenticator app

# Get the serial number
MFA_ARN=$(aws iam list-virtual-mfa-devices \
    --query 'VirtualMFADevices[?SerialNumber==`arn:aws:iam::'${ACCOUNT_ID}':mfa/lab-admin-mfa`].SerialNumber' \
    --output text)

echo "MFA ARN: $MFA_ARN"

# Enable MFA for the user (replace CODE1 and CODE2 with actual codes from your app)
# Wait for the first code, then wait for it to change and use the second code
# aws iam enable-mfa-device \
#     --user-name lab-admin \
#     --serial-number $MFA_ARN \
#     --authentication-code1 123456 \
#     --authentication-code2 789012

# Verify MFA is enabled
aws iam list-mfa-devices --user-name lab-admin
```

### Step 4.4: Test MFA Requirement

```bash
# Attach the MFA-required policy to lab-developers group
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws iam attach-group-policy \
    --group-name lab-developers \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-mfa-required

# Now, if lab-developer tries to perform actions without MFA, they will be denied
# (except for MFA setup actions)
```

### Verification

```bash
# List MFA devices for all lab users
for user in lab-admin lab-developer lab-auditor; do
    echo "=== $user MFA devices ==="
    aws iam list-mfa-devices --user-name $user
done

# Verify MFA policy is attached
aws iam list-attached-group-policies --group-name lab-developers
```

> **CHECKPOINT**: You should understand how to enable MFA and create MFA-required policies.

---

## Exercise 5: Implement Least Privilege with Access Analyzer

### Objective
Use IAM Access Analyzer to identify overly permissive policies and validate new policies.

### Duration: 15-20 minutes

### Step 5.1: Create an Access Analyzer

```bash
# Create an Access Analyzer
aws accessanalyzer create-analyzer \
    --analyzer-name lab-access-analyzer \
    --type ACCOUNT \
    --tags Lab=IAM-Training

# Verify creation
aws accessanalyzer list-analyzers
```

### Step 5.2: Create a Test S3 Bucket with External Access

```bash
# Create a test bucket (use a unique name)
BUCKET_NAME="lab-iam-test-$(date +%s)"
aws s3 mb s3://${BUCKET_NAME}

# Create a bucket policy with public read (for testing - NOT for production!)
cat > ~/iam-lab-policies/test-bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF

# Apply the policy
aws s3api put-bucket-policy \
    --bucket ${BUCKET_NAME} \
    --policy file://~/iam-lab-policies/test-bucket-policy.json

echo "Created bucket: ${BUCKET_NAME}"
echo "Save this name for cleanup later!"
```

### Step 5.3: Check Access Analyzer Findings

```bash
# Wait a minute for Access Analyzer to scan
echo "Waiting 60 seconds for Access Analyzer to analyze..."
sleep 60

# Get the analyzer ARN
ANALYZER_ARN=$(aws accessanalyzer list-analyzers \
    --query 'analyzers[?name==`lab-access-analyzer`].arn' \
    --output text)

# List findings
aws accessanalyzer list-findings \
    --analyzer-arn ${ANALYZER_ARN}

# List only public access findings
aws accessanalyzer list-findings \
    --analyzer-arn ${ANALYZER_ARN} \
    --filter '{"isPublic": {"eq": ["true"]}}'
```

### Step 5.4: Validate a Policy Before Deployment

```bash
# Create a policy to validate
cat > ~/iam-lab-policies/policy-to-validate.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}
EOF

# Validate the policy
aws accessanalyzer validate-policy \
    --policy-type IDENTITY_POLICY \
    --policy-document file://~/iam-lab-policies/policy-to-validate.json

# You should see security warnings about the overly permissive policy
```

### Step 5.5: Remediate the Finding

```bash
# Remove the public policy from the bucket
aws s3api delete-bucket-policy --bucket ${BUCKET_NAME}

# Block public access
aws s3api put-public-access-block \
    --bucket ${BUCKET_NAME} \
    --public-access-block-configuration \
    'BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true'

# Wait and verify the finding is resolved
echo "Waiting 60 seconds for finding to resolve..."
sleep 60

aws accessanalyzer list-findings \
    --analyzer-arn ${ANALYZER_ARN} \
    --filter '{"status": {"eq": ["ACTIVE"]}}'
```

### Verification

```bash
# Verify public access is blocked
aws s3api get-public-access-block --bucket ${BUCKET_NAME}
```

> **CHECKPOINT**: You should understand how to use Access Analyzer to find and fix security issues.

---

## Exercise 6: Create Access Keys and Configure Credential Rotation

### Objective
Understand access key management and set up a credential rotation process.

### Duration: 10-15 minutes

### Step 6.1: Create Access Keys

```bash
# Create access key for lab-developer
aws iam create-access-key --user-name lab-developer

# IMPORTANT: Save the SecretAccessKey - it's only shown once!
# Output example:
# {
#     "AccessKey": {
#         "UserName": "lab-developer",
#         "AccessKeyId": "AKIAXXXXXXXXXXXXXXXX",
#         "Status": "Active",
#         "SecretAccessKey": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#         "CreateDate": "2024-01-15T12:00:00+00:00"
#     }
# }

# List access keys
aws iam list-access-keys --user-name lab-developer
```

### Step 6.2: Simulate Credential Rotation

```bash
# Step 1: Create a NEW access key (user now has 2 keys)
echo "Step 1: Creating new access key..."
aws iam create-access-key --user-name lab-developer

# Step 2: Update applications to use new key (simulated)
echo "Step 2: Update applications with new key (simulated)..."

# Step 3: Check last used for both keys
echo "Step 3: Checking key usage..."
aws iam list-access-keys --user-name lab-developer --query 'AccessKeyMetadata[*].[AccessKeyId,Status,CreateDate]' --output table

# Step 4: Deactivate old key
OLD_KEY_ID=$(aws iam list-access-keys --user-name lab-developer \
    --query 'AccessKeyMetadata | sort_by(@, &CreateDate) | [0].AccessKeyId' \
    --output text)

echo "Step 4: Deactivating old key: ${OLD_KEY_ID}"
aws iam update-access-key \
    --user-name lab-developer \
    --access-key-id ${OLD_KEY_ID} \
    --status Inactive

# Step 5: After confirming everything works, delete old key
echo "Step 5: Deleting old key..."
aws iam delete-access-key \
    --user-name lab-developer \
    --access-key-id ${OLD_KEY_ID}

# Verify only one active key remains
aws iam list-access-keys --user-name lab-developer
```

### Step 6.3: Check Key Age and Usage

```bash
# Create a script to audit access key ages
cat > ~/iam-lab-policies/audit-keys.sh << 'EOF'
#!/bin/bash
echo "=== Access Key Audit ==="

for user in lab-admin lab-developer lab-auditor; do
    echo ""
    echo "User: $user"
    aws iam list-access-keys --user-name $user \
        --query 'AccessKeyMetadata[*].[AccessKeyId,Status,CreateDate]' \
        --output table 2>/dev/null || echo "  No access keys"

    # Check last used
    for key in $(aws iam list-access-keys --user-name $user \
        --query 'AccessKeyMetadata[*].AccessKeyId' --output text 2>/dev/null); do
        echo "  Key $key last used:"
        aws iam get-access-key-last-used --access-key-id $key \
            --query 'AccessKeyLastUsed.[LastUsedDate,ServiceName,Region]' \
            --output text 2>/dev/null || echo "    Never used"
    done
done
EOF

chmod +x ~/iam-lab-policies/audit-keys.sh
~/iam-lab-policies/audit-keys.sh
```

> **CHECKPOINT**: You should understand how to manage and rotate access keys.

---

## Exercise 7: Configure Password Policy

### Objective
Set up a secure password policy for the AWS account.

### Duration: 5-10 minutes

### Step 7.1: View Current Password Policy

```bash
# Get current password policy
aws iam get-account-password-policy

# If no policy exists, you'll get an error
```

### Step 7.2: Create a Secure Password Policy

```bash
# Set a comprehensive password policy
aws iam update-account-password-policy \
    --minimum-password-length 14 \
    --require-symbols \
    --require-numbers \
    --require-uppercase-characters \
    --require-lowercase-characters \
    --allow-users-to-change-password \
    --max-password-age 90 \
    --password-reuse-prevention 12 \
    --no-hard-expiry

# Verify the policy
aws iam get-account-password-policy
```

### Verification

```bash
# The output should show all your security requirements
aws iam get-account-password-policy --query '{
    MinimumPasswordLength: MinimumPasswordLength,
    RequireSymbols: RequireSymbols,
    RequireNumbers: RequireNumbers,
    RequireUppercase: RequireUppercaseCharacters,
    RequireLowercase: RequireLowercaseCharacters,
    MaxPasswordAge: MaxPasswordAge,
    PasswordReusePrevention: PasswordReusePrevention
}'
```

> **CHECKPOINT**: You should have a secure password policy configured.

---

## Troubleshooting Guide

### Common Issues and Solutions

```
+------------------------------------------------------------------+
|                    TROUBLESHOOTING GUIDE                          |
+------------------------------------------------------------------+

ISSUE: "Access Denied" when creating resources
SOLUTION:
- Verify you have admin credentials configured
- Run: aws sts get-caller-identity
- Check attached policies: aws iam list-attached-user-policies

ISSUE: MFA device not syncing
SOLUTION:
- Ensure your phone's time is synchronized
- Use the resync command:
  aws iam resync-mfa-device --user-name USER \
      --serial-number ARN --authentication-code1 CODE1 \
      --authentication-code2 CODE2

ISSUE: "Entity already exists" errors
SOLUTION:
- Resources may exist from a previous attempt
- List existing resources: aws iam list-users/groups/roles
- Delete and recreate, or use different names

ISSUE: Can't delete user/group/role
SOLUTION:
- Must remove all attached policies first
- For users: remove from groups, delete access keys, login profile
- See cleanup section for detailed steps

ISSUE: Policy validation errors
SOLUTION:
- Check JSON syntax (missing commas, brackets)
- Validate with: aws iam create-policy --policy-document ... --dry-run
- Use a JSON validator online

ISSUE: Access Analyzer not showing findings
SOLUTION:
- Findings can take several minutes to appear
- Ensure analyzer is in same region as resources
- Check analyzer status: aws accessanalyzer list-analyzers

+------------------------------------------------------------------+
```

---

## Cleanup Instructions

> **IMPORTANT**: Complete this section to avoid any potential security risks or confusion with existing resources.

### Step-by-Step Cleanup

```bash
#!/bin/bash
# IAM Lab Cleanup Script

echo "=== IAM Lab Cleanup ==="
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Step 1: Remove users from groups
echo "Removing users from groups..."
aws iam remove-user-from-group --user-name lab-admin --group-name lab-admins 2>/dev/null
aws iam remove-user-from-group --user-name lab-developer --group-name lab-developers 2>/dev/null
aws iam remove-user-from-group --user-name lab-auditor --group-name lab-auditors 2>/dev/null

# Step 2: Detach policies from groups
echo "Detaching policies from groups..."
aws iam detach-group-policy --group-name lab-admins --policy-arn arn:aws:iam::aws:policy/AdministratorAccess 2>/dev/null
aws iam detach-group-policy --group-name lab-developers --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-developer-policy 2>/dev/null
aws iam detach-group-policy --group-name lab-developers --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-mfa-required 2>/dev/null
aws iam detach-group-policy --group-name lab-auditors --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-auditor-policy 2>/dev/null

# Step 3: Delete user resources
echo "Deleting user resources..."
for user in lab-admin lab-developer lab-auditor; do
    echo "  Cleaning up $user..."

    # Delete login profile
    aws iam delete-login-profile --user-name $user 2>/dev/null

    # Delete access keys
    for key in $(aws iam list-access-keys --user-name $user --query 'AccessKeyMetadata[*].AccessKeyId' --output text 2>/dev/null); do
        aws iam delete-access-key --user-name $user --access-key-id $key
    done

    # Deactivate and delete MFA devices
    for mfa in $(aws iam list-mfa-devices --user-name $user --query 'MFADevices[*].SerialNumber' --output text 2>/dev/null); do
        aws iam deactivate-mfa-device --user-name $user --serial-number $mfa
    done

    # Delete inline policies
    for policy in $(aws iam list-user-policies --user-name $user --query 'PolicyNames[*]' --output text 2>/dev/null); do
        aws iam delete-user-policy --user-name $user --policy-name $policy
    done

    # Delete user
    aws iam delete-user --user-name $user 2>/dev/null
done

# Step 4: Delete groups
echo "Deleting groups..."
aws iam delete-group --group-name lab-admins 2>/dev/null
aws iam delete-group --group-name lab-developers 2>/dev/null
aws iam delete-group --group-name lab-auditors 2>/dev/null

# Step 5: Delete roles
echo "Deleting roles..."
for role in lab-ec2-s3-role lab-lambda-execution-role lab-elevated-access-role; do
    echo "  Cleaning up $role..."

    # Detach managed policies
    for policy in $(aws iam list-attached-role-policies --role-name $role --query 'AttachedPolicies[*].PolicyArn' --output text 2>/dev/null); do
        aws iam detach-role-policy --role-name $role --policy-arn $policy
    done

    # Delete inline policies
    for policy in $(aws iam list-role-policies --role-name $role --query 'PolicyNames[*]' --output text 2>/dev/null); do
        aws iam delete-role-policy --role-name $role --policy-name $policy
    done

    aws iam delete-role --role-name $role 2>/dev/null
done

# Step 6: Delete instance profile
echo "Deleting instance profile..."
aws iam remove-role-from-instance-profile --instance-profile-name lab-ec2-s3-profile --role-name lab-ec2-s3-role 2>/dev/null
aws iam delete-instance-profile --instance-profile-name lab-ec2-s3-profile 2>/dev/null

# Step 7: Delete custom policies
echo "Deleting custom policies..."
aws iam delete-policy --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-developer-policy 2>/dev/null
aws iam delete-policy --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-auditor-policy 2>/dev/null
aws iam delete-policy --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/lab-mfa-required 2>/dev/null

# Step 8: Delete virtual MFA devices
echo "Deleting virtual MFA devices..."
aws iam delete-virtual-mfa-device --serial-number arn:aws:iam::${ACCOUNT_ID}:mfa/lab-admin-mfa 2>/dev/null

# Step 9: Delete Access Analyzer
echo "Deleting Access Analyzer..."
aws accessanalyzer delete-analyzer --analyzer-name lab-access-analyzer 2>/dev/null

# Step 10: Delete S3 bucket (if created)
echo "Deleting S3 bucket..."
# List buckets starting with 'lab-iam-test-'
for bucket in $(aws s3 ls | grep 'lab-iam-test-' | awk '{print $3}'); do
    echo "  Deleting bucket: $bucket"
    aws s3 rb s3://$bucket --force 2>/dev/null
done

# Step 11: Clean up local files
echo "Cleaning up local files..."
rm -rf ~/iam-lab-policies 2>/dev/null

echo ""
echo "=== Cleanup Complete ==="
echo "Verify no lab resources remain:"
echo "  aws iam list-users --query 'Users[?starts_with(UserName, \`lab-\`)]'"
echo "  aws iam list-groups --query 'Groups[?starts_with(GroupName, \`lab-\`)]'"
echo "  aws iam list-roles --query 'Roles[?starts_with(RoleName, \`lab-\`)]'"
```

### Manual Cleanup Verification

```bash
# Verify all lab resources are deleted
echo "=== Verification ==="

echo "Users:"
aws iam list-users --query 'Users[?starts_with(UserName, `lab-`)].UserName' --output table

echo "Groups:"
aws iam list-groups --query 'Groups[?starts_with(GroupName, `lab-`)].GroupName' --output table

echo "Roles:"
aws iam list-roles --query 'Roles[?starts_with(RoleName, `lab-`)].RoleName' --output table

echo "Policies:"
aws iam list-policies --scope Local --query 'Policies[?starts_with(PolicyName, `lab-`)].PolicyName' --output table

echo "Instance Profiles:"
aws iam list-instance-profiles --query 'InstanceProfiles[?starts_with(InstanceProfileName, `lab-`)].InstanceProfileName' --output table

echo "S3 Buckets:"
aws s3 ls | grep 'lab-'
```

---

## Lab Summary

### What You Learned

| Exercise | Skills Gained |
|----------|---------------|
| Exercise 1 | Creating and organizing IAM users and groups |
| Exercise 2 | Writing custom IAM policies with conditions |
| Exercise 3 | Creating service roles and assuming roles |
| Exercise 4 | Implementing MFA for enhanced security |
| Exercise 5 | Using Access Analyzer for security auditing |
| Exercise 6 | Managing and rotating access keys |
| Exercise 7 | Configuring account password policies |

### Key Takeaways

1. **Use Groups**: Always manage permissions through groups, not individual users
2. **Least Privilege**: Start with no permissions and add only what's needed
3. **Use Roles**: Prefer roles over access keys for services and cross-account access
4. **Enable MFA**: MFA is essential for all human users
5. **Regular Audits**: Use Access Analyzer and credential reports regularly
6. **Rotate Credentials**: Implement 90-day credential rotation policies
7. **Document Everything**: Keep records of who has access to what and why

---

## Additional Practice

Want more practice? Try these additional challenges:

1. **Create a permission boundary** that limits developers to specific regions
2. **Set up cross-account access** between two AWS accounts (if available)
3. **Create a Lambda function** that uses the lab-lambda-execution-role
4. **Write a policy** that allows access only during business hours
5. **Generate a least-privilege policy** using Access Analyzer policy generation

---

## Next Steps

Congratulations on completing the IAM hands-on lab! Continue to [quiz.md](./quiz.md) to test your knowledge.
