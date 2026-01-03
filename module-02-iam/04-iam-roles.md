# IAM Roles: Complete Guide

## Introduction

IAM roles are one of the most powerful and frequently used features in AWS. Unlike users, roles don't have permanent credentials. Instead, they provide temporary security credentials to whoever (or whatever) assumes them.

---

## Why Roles Matter

### The Problem with Static Credentials

```
+------------------------------------------------------------------+
|                    THE PROBLEM                                    |
+------------------------------------------------------------------+
|                                                                   |
|  EC2 Instance needs to access S3:                                |
|                                                                   |
|  BAD APPROACH (Access Keys in Code):                             |
|  +-------------+                                                  |
|  |    EC2      |  Hardcoded credentials in:                      |
|  |  Instance   |  - Environment variables                        |
|  |             |  - Configuration files                          |
|  | AWS_ACCESS_ |  - Application code                             |
|  | KEY_ID=AKIA.|                                                  |
|  +-------------+                                                  |
|                                                                   |
|  Problems:                                                        |
|  - Credentials can be stolen if instance is compromised         |
|  - Credentials don't rotate automatically                        |
|  - Credentials may leak into logs, version control              |
|  - Must update all instances when credentials rotate             |
|                                                                   |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                    THE SOLUTION: IAM ROLES                        |
+------------------------------------------------------------------+
|                                                                   |
|  EC2 Instance with IAM Role:                                     |
|  +-------------+     +----------------+     +-------------+       |
|  |    EC2      |<--->| Instance       |<--->|    STS      |       |
|  |  Instance   |     | Profile (Role) |     | (Temporary  |       |
|  |             |     |                |     |  Creds)     |       |
|  | No static   |     | Auto-rotated   |     |             |       |
|  | credentials |     | every ~1 hour  |     |             |       |
|  +-------------+     +----------------+     +-------------+       |
|                                                                   |
|  Benefits:                                                        |
|  - No credentials to manage or rotate                            |
|  - Credentials auto-refresh before expiration                    |
|  - Instance metadata service provides credentials                 |
|  - Cannot leak what doesn't exist in code                        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Role Components

Every IAM role has two types of policies:

```
+------------------------------------------------------------------+
|                         IAM ROLE                                  |
+------------------------------------------------------------------+
|                                                                   |
|  +---------------------------+   +----------------------------+   |
|  |      TRUST POLICY         |   |    PERMISSIONS POLICY      |   |
|  |    (AssumeRolePolicyDoc)  |   |     (What can be done)     |   |
|  +---------------------------+   +----------------------------+   |
|  |                           |   |                            |   |
|  | WHO can assume this role: |   | WHAT the role can do:      |   |
|  |                           |   |                            |   |
|  | - AWS Services            |   | - Read from S3             |   |
|  | - IAM Users               |   | - Write to DynamoDB        |   |
|  | - Other Roles             |   | - Invoke Lambda            |   |
|  | - AWS Accounts            |   | - Access Secrets Manager   |   |
|  | - Federated Users         |   | - etc.                     |   |
|  |                           |   |                            |   |
|  +---------------------------+   +----------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Types of IAM Roles

### 1. Service Roles

Used by AWS services to perform actions on your behalf.

```
+------------------------------------------------------------------+
|                       SERVICE ROLES                               |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------+     +-------------+     +-------------+          |
|  |    EC2      |     |   Lambda    |     |    ECS      |          |
|  |  Instance   |     |  Function   |     |    Task     |          |
|  +------+------+     +------+------+     +------+------+          |
|         |                   |                   |                 |
|         v                   v                   v                 |
|  +-------------+     +-------------+     +-------------+          |
|  | EC2-S3-Role |     | Lambda-Exec |     | ECS-Task-   |          |
|  |             |     |    Role     |     |    Role     |          |
|  +------+------+     +------+------+     +------+------+          |
|         |                   |                   |                 |
|         v                   v                   v                 |
|  +----------------------------------------------------------+    |
|  |                    AWS RESOURCES                          |    |
|  |   (S3, DynamoDB, SQS, SNS, Secrets Manager, etc.)        |    |
|  +----------------------------------------------------------+    |
|                                                                   |
+------------------------------------------------------------------+
```

**Common Service Roles:**

| Service | Role Purpose | Trust Principal |
|---------|-------------|-----------------|
| EC2 | Access AWS resources from instances | `ec2.amazonaws.com` |
| Lambda | Execute and access resources | `lambda.amazonaws.com` |
| ECS | Run tasks with permissions | `ecs-tasks.amazonaws.com` |
| API Gateway | Invoke Lambda, access logs | `apigateway.amazonaws.com` |
| CloudFormation | Create/manage resources | `cloudformation.amazonaws.com` |
| CodePipeline | Orchestrate deployments | `codepipeline.amazonaws.com` |

### 2. Cross-Account Roles

Allow access from other AWS accounts.

```
+------------------------------------------------------------------+
|                    CROSS-ACCOUNT ACCESS                           |
+------------------------------------------------------------------+
|                                                                   |
|  Account A (111111111111)          Account B (222222222222)       |
|  +----------------------+          +----------------------+       |
|  |                      |          |                      |       |
|  |  +----------------+  |          |  +----------------+  |       |
|  |  |  User: Alice   |  |  Assume  |  | Role: S3Access |  |       |
|  |  |                |------------->  |                |  |       |
|  |  +----------------+  |  Role    |  +-------+--------+  |       |
|  |                      |          |          |           |       |
|  |                      |          |          v           |       |
|  |                      |          |  +----------------+  |       |
|  |                      |          |  |   S3 Bucket    |  |       |
|  |                      |          |  |   in Acct B    |  |       |
|  |                      |          |  +----------------+  |       |
|  |                      |          |                      |       |
|  +----------------------+          +----------------------+       |
|                                                                   |
+------------------------------------------------------------------+
```

### 3. Service-Linked Roles

Predefined by AWS services, automatically created when needed.

```
+------------------------------------------------------------------+
|                    SERVICE-LINKED ROLES                           |
+------------------------------------------------------------------+
|                                                                   |
|  Characteristics:                                                 |
|  - Created automatically by AWS services                         |
|  - Permissions predefined and cannot be modified                 |
|  - Trust policy locked to specific service                       |
|  - Naming: AWSServiceRoleFor<ServiceName>                        |
|                                                                   |
|  Examples:                                                        |
|  - AWSServiceRoleForElasticLoadBalancing                         |
|  - AWSServiceRoleForAutoScaling                                  |
|  - AWSServiceRoleForAmazonEKS                                    |
|  - AWSServiceRoleForRDS                                          |
|  - AWSServiceRoleForOrganizations                                |
|                                                                   |
+------------------------------------------------------------------+
```

### 4. Federation Roles

Used by external identity providers.

```
+------------------------------------------------------------------+
|                    FEDERATION ROLES                               |
+------------------------------------------------------------------+
|                                                                   |
|  SAML 2.0 Federation:                                            |
|  +----------------+     +----------------+     +----------------+ |
|  |  Corporate     |     |    AWS IAM     |     |   AWS         | |
|  |    IdP         |---->|   (SAML        |---->|  Resources    | |
|  |  (Okta, ADFS)  |     |   Provider)    |     |               | |
|  +----------------+     +----------------+     +----------------+ |
|                                                                   |
|  Web Identity Federation:                                         |
|  +----------------+     +----------------+     +----------------+ |
|  |  Social IdP    |     |    Cognito /   |     |   AWS         | |
|  |  (Google,      |---->|    STS         |---->|  Resources    | |
|  |   Facebook)    |     |                |     |               | |
|  +----------------+     +----------------+     +----------------+ |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Creating IAM Roles

### Step 1: Define Trust Policy

The trust policy determines WHO can assume the role.

#### Trust Policy for EC2

```json
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
```

#### Trust Policy for Lambda

```json
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
```

#### Trust Policy for Cross-Account

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111111111111:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "unique-external-id-12345"
                }
            }
        }
    ]
}
```

#### Trust Policy for Specific User

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111111111111:user/alice"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": "true"
                }
            }
        }
    ]
}
```

### Step 2: Create the Role

```bash
# Create the role with trust policy
aws iam create-role \
    --role-name EC2-S3-Access \
    --assume-role-policy-document file://trust-policy.json \
    --description "Role for EC2 instances to access S3"

# Add tags
aws iam tag-role \
    --role-name EC2-S3-Access \
    --tags Key=Environment,Value=Production Key=Team,Value=Platform
```

### Step 3: Attach Permissions

```bash
# Attach AWS managed policy
aws iam attach-role-policy \
    --role-name EC2-S3-Access \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Attach customer managed policy
aws iam attach-role-policy \
    --role-name EC2-S3-Access \
    --policy-arn arn:aws:iam::123456789012:policy/CustomS3Policy

# Add inline policy
aws iam put-role-policy \
    --role-name EC2-S3-Access \
    --policy-name AdditionalPermissions \
    --policy-document file://additional-policy.json
```

### Step 4: Create Instance Profile (for EC2)

```bash
# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name EC2-S3-Access-Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name EC2-S3-Access-Profile \
    --role-name EC2-S3-Access

# Associate with EC2 instance (at launch or existing)
aws ec2 associate-iam-instance-profile \
    --instance-id i-1234567890abcdef0 \
    --iam-instance-profile Name=EC2-S3-Access-Profile
```

---

## Assuming Roles

### How Role Assumption Works

```
+------------------------------------------------------------------+
|                    ASSUME ROLE PROCESS                            |
+------------------------------------------------------------------+
|                                                                   |
|  Step 1: Request                                                  |
|  +-------------+     sts:AssumeRole      +-------------+          |
|  |  Principal  | ----------------------> |    AWS      |          |
|  |  (User/Svc) |                         |    STS      |          |
|  +-------------+                         +------+------+          |
|                                                 |                 |
|  Step 2: Validation                            |                 |
|                                                 v                 |
|                                          +-------------+          |
|                                          | Check Trust |          |
|                                          | Policy      |          |
|                                          +------+------+          |
|                                                 |                 |
|                              +------------------+------------------+
|                              |                                    |
|                           ALLOWED                              DENIED
|                              |                                    |
|                              v                                    v
|  Step 3: Issue Credentials   |                              Access
|  +---------------------------+--------------+               Denied
|  |  Temporary Security Credentials          |                     |
|  |  +-------------------------------------+ |                     |
|  |  | AccessKeyId: ASIA...                | |                     |
|  |  | SecretAccessKey: wJalr...           | |                     |
|  |  | SessionToken: FwoGZX...             | |                     |
|  |  | Expiration: 2024-01-15T13:00:00Z    | |                     |
|  |  +-------------------------------------+ |                     |
|  +------------------------------------------+                     |
|                                                                   |
+------------------------------------------------------------------+
```

### Assuming Roles via CLI

```bash
# Basic assume role
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/MyRole \
    --role-session-name MySession

# With external ID (for cross-account)
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/CrossAccountRole \
    --role-session-name PartnerSession \
    --external-id unique-external-id-12345

# With MFA
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/AdminRole \
    --role-session-name AdminSession \
    --serial-number arn:aws:iam::111111111111:mfa/alice \
    --token-code 123456

# With custom duration (seconds, default 3600)
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/MyRole \
    --role-session-name LongSession \
    --duration-seconds 43200  # 12 hours (max depends on role settings)
```

### Using Assumed Role Credentials

```bash
# Method 1: Set environment variables
export AWS_ACCESS_KEY_ID="ASIAXXX..."
export AWS_SECRET_ACCESS_KEY="wJalr..."
export AWS_SESSION_TOKEN="FwoGZX..."

# Method 2: Use named profile
aws configure set aws_access_key_id ASIAXXX... --profile assumed-role
aws configure set aws_secret_access_key wJalr... --profile assumed-role
aws configure set aws_session_token FwoGZX... --profile assumed-role

aws s3 ls --profile assumed-role

# Method 3: Use credential_process in config
# ~/.aws/config
[profile cross-account]
role_arn = arn:aws:iam::123456789012:role/MyRole
source_profile = default
```

### AWS CLI Profile Configuration for Roles

```ini
# ~/.aws/config

# Source profile with permanent credentials
[profile developer]
region = us-east-1
output = json

# Role assumption using source profile
[profile production-admin]
role_arn = arn:aws:iam::123456789012:role/ProductionAdmin
source_profile = developer
mfa_serial = arn:aws:iam::111111111111:mfa/myuser
region = us-east-1

# Cross-account role
[profile partner-account]
role_arn = arn:aws:iam::999888777666:role/PartnerAccess
source_profile = developer
external_id = my-external-id-12345
region = us-west-2

# Chained role assumption
[profile super-admin]
role_arn = arn:aws:iam::123456789012:role/SuperAdmin
source_profile = production-admin
```

---

## Service Role Deep Dives

### EC2 Instance Roles

```
+------------------------------------------------------------------+
|                    EC2 INSTANCE ROLE                              |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------+     +------------------+     +----------------+  |
|  |    EC2      |     | Instance Metadata|     | Instance       |  |
|  |  Instance   |<--->|    Service       |<--->| Profile        |  |
|  |             |     | 169.254.169.254  |     | (Role wrapper) |  |
|  +-------------+     +------------------+     +--------+-------+  |
|                                                        |          |
|                                                        v          |
|                                               +--------+-------+  |
|                                               |   IAM Role     |  |
|                                               | (Permissions)  |  |
|                                               +----------------+  |
|                                                                   |
|  How it works:                                                   |
|  1. EC2 calls instance metadata: 169.254.169.254/latest/        |
|     meta-data/iam/security-credentials/<role-name>              |
|  2. Receives temporary credentials (auto-refreshed ~1hr)        |
|  3. AWS SDKs do this automatically                              |
|                                                                   |
+------------------------------------------------------------------+
```

**Creating EC2 Role:**

```bash
# 1. Create trust policy file
cat > ec2-trust-policy.json << 'EOF'
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

# 2. Create the role
aws iam create-role \
    --role-name EC2-Application-Role \
    --assume-role-policy-document file://ec2-trust-policy.json

# 3. Attach policies
aws iam attach-role-policy \
    --role-name EC2-Application-Role \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-role-policy \
    --role-name EC2-Application-Role \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# 4. Create instance profile
aws iam create-instance-profile \
    --instance-profile-name EC2-Application-Profile

# 5. Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name EC2-Application-Profile \
    --role-name EC2-Application-Role

# 6. Launch EC2 with profile
aws ec2 run-instances \
    --image-id ami-12345678 \
    --instance-type t3.micro \
    --iam-instance-profile Name=EC2-Application-Profile
```

### Lambda Execution Roles

```
+------------------------------------------------------------------+
|                    LAMBDA EXECUTION ROLE                          |
+------------------------------------------------------------------+
|                                                                   |
|  +----------------+                                               |
|  |    Lambda      |                                               |
|  |   Function     |                                               |
|  +-------+--------+                                               |
|          |                                                        |
|          | Uses execution role for:                               |
|          |                                                        |
|  +-------v--------+     +----------------------------------+      |
|  |  Execution     |---->| CloudWatch Logs (always needed) |      |
|  |    Role        |---->| S3 (if accessing buckets)       |      |
|  |                |---->| DynamoDB (if accessing tables)  |      |
|  |                |---->| VPC (if in VPC)                 |      |
|  |                |---->| Other AWS services...           |      |
|  +----------------+     +----------------------------------+      |
|                                                                   |
+------------------------------------------------------------------+
```

**Creating Lambda Role:**

```bash
# 1. Create trust policy
cat > lambda-trust-policy.json << 'EOF'
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

# 2. Create role
aws iam create-role \
    --role-name Lambda-DynamoDB-Role \
    --assume-role-policy-document file://lambda-trust-policy.json

# 3. Attach basic execution policy (CloudWatch Logs)
aws iam attach-role-policy \
    --role-name Lambda-DynamoDB-Role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# 4. Create and attach custom policy for DynamoDB
cat > lambda-dynamodb-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name Lambda-DynamoDB-Role \
    --policy-name DynamoDBAccess \
    --policy-document file://lambda-dynamodb-policy.json
```

---

## Cross-Account Access

### The External ID Confused Deputy Problem

```
+------------------------------------------------------------------+
|                  THE CONFUSED DEPUTY PROBLEM                      |
+------------------------------------------------------------------+
|                                                                   |
|  WITHOUT External ID:                                            |
|                                                                   |
|  Account A        Your Account       Account B (Malicious)       |
|  (Legitimate)     (Target)                                       |
|  +-----------+    +------------+     +-----------+               |
|  | Partner A |    |            |     | Attacker  |               |
|  |           |    | Cross-Acct |     |           |               |
|  | Provides  |--->|   Role     |<----| Also uses |               |
|  | their ID  |    |            |     | A's info! |               |
|  +-----------+    +------------+     +-----------+               |
|                                                                   |
|  The attacker can impersonate Partner A!                         |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  WITH External ID:                                               |
|                                                                   |
|  Account A        Your Account       Account B (Malicious)       |
|  (Legitimate)     (Target)                                       |
|  +-----------+    +------------+     +-----------+               |
|  | Partner A |    |            |     | Attacker  |               |
|  |           |    | Cross-Acct |     |           |               |
|  | Provides  |--->|   Role     |<-X--| Doesn't   |               |
|  | A's ID +  |    | + External |     | know the  |               |
|  | ExternalID|    |   ID check |     | External  |               |
|  +-----------+    +------------+     | ID!       |               |
|                                      +-----------+               |
|                                                                   |
|  Attacker blocked - doesn't know the secret External ID         |
|                                                                   |
+------------------------------------------------------------------+
```

### Setting Up Cross-Account Access

**In the Target Account (Account B - 222222222222):**

```bash
# Create trust policy with external ID
cat > cross-account-trust.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111111111111:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "partner-unique-id-abc123"
                }
            }
        }
    ]
}
EOF

# Create role
aws iam create-role \
    --role-name PartnerAccessRole \
    --assume-role-policy-document file://cross-account-trust.json

# Attach permissions
aws iam attach-role-policy \
    --role-name PartnerAccessRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

**In the Source Account (Account A - 111111111111):**

```bash
# Create policy allowing users to assume the role
cat > assume-role-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::222222222222:role/PartnerAccessRole"
        }
    ]
}
EOF

# Attach to user or group
aws iam create-policy \
    --policy-name AssumePartnerRole \
    --policy-document file://assume-role-policy.json

aws iam attach-user-policy \
    --user-name alice \
    --policy-arn arn:aws:iam::111111111111:policy/AssumePartnerRole

# User assumes the role
aws sts assume-role \
    --role-arn arn:aws:iam::222222222222:role/PartnerAccessRole \
    --role-session-name AliceSession \
    --external-id partner-unique-id-abc123
```

---

## Decision Trees

### When to Use User vs Role

```
                            START
                              |
                              v
                    +-------------------+
                    | Is the principal  |
                    | an AWS service?   |
                    +--------+----------+
                             |
              +--------------+--------------+
              |                             |
            YES                            NO
              |                             |
              v                             v
    +------------------+          +-------------------+
    | Use SERVICE ROLE |          | Is access from   |
    | Examples:        |          | outside AWS?     |
    | - EC2 role       |          | (Federation)     |
    | - Lambda role    |          +--------+----------+
    | - ECS task role  |                   |
    +------------------+        +-----------+-----------+
                                |                       |
                              YES                      NO
                                |                       |
                                v                       v
                    +------------------+     +-------------------+
                    | Use FEDERATION   |     | Is access from   |
                    | ROLE             |     | another account? |
                    | Examples:        |     +--------+----------+
                    | - SAML role      |              |
                    | - Cognito role   |   +-----------+-----------+
                    +------------------+   |                       |
                                         YES                      NO
                                           |                       |
                                           v                       v
                                +------------------+    +-------------------+
                                | Use CROSS-ACCT   |    | Is access for a   |
                                | ROLE             |    | human? (Console)  |
                                | With ExternalId  |    +--------+----------+
                                +------------------+             |
                                                      +-----------+-----------+
                                                      |                       |
                                                    YES                      NO
                                                      |                       |
                                                      v                       v
                                           +------------------+    +------------------+
                                           | Use IAM USER     |    | Consider ROLE    |
                                           | - Console pass   |    | if app can       |
                                           | - MFA enabled    |    | assume roles     |
                                           +------------------+    +------------------+
```

### Choosing the Right Role Type

```
+------------------------------------------------------------------+
|               ROLE TYPE DECISION MATRIX                           |
+------------------------------------------------------------------+

+------------------+------------------+------------------+
|    Scenario      |    Role Type     |    Example       |
+------------------+------------------+------------------+
| EC2 needs S3     | Service Role     | EC2-to-S3 role   |
| access           | for EC2          |                  |
+------------------+------------------+------------------+
| Lambda needs DB  | Service Role     | Lambda execution |
| access           | for Lambda       | role             |
+------------------+------------------+------------------+
| Partner company  | Cross-Account    | Partner-Access   |
| needs access     | Role             | role + ExternalId|
+------------------+------------------+------------------+
| Dev account needs| Cross-Account    | Dev-to-Prod role |
| prod access      | Role             |                  |
+------------------+------------------+------------------+
| Corp employees   | SAML Federation  | ADFS-to-AWS role |
| via SSO          | Role             |                  |
+------------------+------------------+------------------+
| Mobile app users | Web Identity     | Cognito-Auth role|
|                  | Federation Role  |                  |
+------------------+------------------+------------------+
| ELB needs access | Service-Linked   | Auto-created by  |
|                  | Role             | AWS              |
+------------------+------------------+------------------+
```

---

## Role Management Commands

### Complete CLI Reference

```bash
# CREATE ROLE
aws iam create-role \
    --role-name MyRole \
    --assume-role-policy-document file://trust.json \
    --description "My role description" \
    --max-session-duration 43200  # 12 hours max

# UPDATE TRUST POLICY
aws iam update-assume-role-policy \
    --role-name MyRole \
    --policy-document file://new-trust.json

# ATTACH MANAGED POLICY
aws iam attach-role-policy \
    --role-name MyRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# DETACH MANAGED POLICY
aws iam detach-role-policy \
    --role-name MyRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# ADD INLINE POLICY
aws iam put-role-policy \
    --role-name MyRole \
    --policy-name InlinePolicy \
    --policy-document file://inline.json

# DELETE INLINE POLICY
aws iam delete-role-policy \
    --role-name MyRole \
    --policy-name InlinePolicy

# LIST ROLES
aws iam list-roles

# GET ROLE DETAILS
aws iam get-role --role-name MyRole

# LIST ATTACHED POLICIES
aws iam list-attached-role-policies --role-name MyRole

# LIST INLINE POLICIES
aws iam list-role-policies --role-name MyRole

# DELETE ROLE (must remove all policies first)
aws iam detach-role-policy --role-name MyRole --policy-arn <arn>
aws iam delete-role-policy --role-name MyRole --policy-name <name>
aws iam delete-role --role-name MyRole

# INSTANCE PROFILE MANAGEMENT
aws iam create-instance-profile --instance-profile-name MyProfile
aws iam add-role-to-instance-profile --instance-profile-name MyProfile --role-name MyRole
aws iam remove-role-from-instance-profile --instance-profile-name MyProfile --role-name MyRole
aws iam delete-instance-profile --instance-profile-name MyProfile

# STS OPERATIONS
aws sts assume-role --role-arn <arn> --role-session-name <name>
aws sts get-caller-identity  # Who am I?
aws sts get-session-token    # Get temp creds from IAM user
```

---

## Common Mistakes

### Mistake 1: Forgetting Instance Profile for EC2

```
PROBLEM:
Role created but EC2 can't assume it

SOLUTION:
EC2 requires an Instance Profile (wrapper around the role)
- Create instance profile
- Add role to instance profile
- Attach instance profile to EC2
```

### Mistake 2: Wrong Trust Policy Principal

```json
// WRONG: Using account number without proper format
{
    "Principal": "123456789012"  // Invalid!
}

// CORRECT: Using full ARN
{
    "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
    }
}

// OR for specific user
{
    "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/alice"
    }
}
```

### Mistake 3: Missing sts:AssumeRole Permission

```json
// User policy must ALLOW assuming the role
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::123456789012:role/TargetRole"
        }
    ]
}

// AND the role's trust policy must ALLOW the user
// Both are required for cross-account
```

### Mistake 4: Overly Long Session Duration

```bash
# Role's max session duration limits what can be requested
# Default is 1 hour (3600 seconds)
# Max configurable is 12 hours (43200 seconds)

# Update role's max session duration
aws iam update-role \
    --role-name MyRole \
    --max-session-duration 43200

# Then can request up to 12 hours
aws sts assume-role \
    --role-arn <arn> \
    --role-session-name <name> \
    --duration-seconds 43200
```

---

## Summary

| Role Type | Use Case | Trust Principal |
|-----------|----------|-----------------|
| Service Role | AWS service needs access | `service.amazonaws.com` |
| Cross-Account | Another AWS account | `arn:aws:iam::ACCOUNT:root` |
| SAML Federation | Corporate SSO | `arn:aws:iam::ACCOUNT:saml-provider/NAME` |
| Web Identity | Mobile/Web apps | `cognito-identity.amazonaws.com` |
| Service-Linked | AWS-managed service | Predefined by AWS |

---

## Next Steps

Continue to [05-iam-best-practices.md](./05-iam-best-practices.md) to learn security best practices for IAM.
