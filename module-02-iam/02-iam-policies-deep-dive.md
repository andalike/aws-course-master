# IAM Policies Deep Dive

## Introduction

IAM policies are the heart of AWS security. This document provides a comprehensive guide to understanding, writing, and debugging IAM policies.

---

## Policy Document Structure

Every IAM policy follows this structure:

```json
{
    "Version": "2012-10-17",
    "Id": "Optional-Policy-Identifier",
    "Statement": [
        {
            "Sid": "Optional-Statement-Identifier",
            "Effect": "Allow | Deny",
            "Principal": "Who this applies to",
            "Action": "What actions",
            "Resource": "Which resources",
            "Condition": {
                "Operator": {
                    "Key": "Value"
                }
            }
        }
    ]
}
```

---

## Line-by-Line Policy Explanation

Let's analyze a complete policy:

```json
{
    "Version": "2012-10-17",
```
**Line 1-2: Version**
- Always use `"2012-10-17"` (current version)
- Older version `"2008-10-17"` lacks features like policy variables
- This is NOT a date you set - it's the policy language version

```json
    "Id": "S3-Bucket-Access-Policy",
```
**Line 3: Id (Optional)**
- Human-readable identifier for the policy
- Useful for documentation and debugging
- Some services (like S3, SQS) may require this

```json
    "Statement": [
```
**Line 4: Statement Array**
- Contains one or more permission statements
- Each statement is an independent permission rule
- Multiple statements are evaluated together

```json
        {
            "Sid": "AllowS3BucketRead",
```
**Line 5-6: Sid (Statement ID)**
- Optional but highly recommended
- Unique identifier within the policy
- Makes policies self-documenting
- Helps identify which statement triggered allow/deny

```json
            "Effect": "Allow",
```
**Line 7: Effect**
- Only two values: `"Allow"` or `"Deny"`
- `Deny` always overrides `Allow`
- No effect = implicit deny

```json
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:user/john"
            },
```
**Line 8-10: Principal**
- WHO the policy applies to
- Only used in resource-based policies (not identity-based)
- Can be: AWS account, IAM user, IAM role, AWS service, or `"*"` (anyone)

```json
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
```
**Line 11-14: Action**
- WHAT operations are allowed/denied
- Format: `service:ActionName`
- Wildcards allowed: `s3:*`, `s3:Get*`
- Can be a single string or array

```json
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
```
**Line 15-18: Resource**
- WHICH AWS resources this applies to
- ARN format: `arn:partition:service:region:account:resource`
- Wildcards allowed: `*` for all resources
- Some services require specific resource formats

```json
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "192.168.1.0/24"
                },
                "Bool": {
                    "aws:SecureTransport": "true"
                }
            }
```
**Line 19-26: Condition (Optional)**
- WHEN the policy applies
- Multiple conditions are AND-ed together
- Multiple values within a condition are OR-ed
- Powerful for fine-grained access control

```json
        }
    ]
}
```

---

## The Effect Element

### Allow vs Deny

```
+------------------------------------------------------------------+
|                     POLICY EVALUATION                             |
+------------------------------------------------------------------+
|                                                                   |
|  1. Start with IMPLICIT DENY (default)                           |
|     - If no policy says "Allow", access is denied                |
|                                                                   |
|  2. Check for EXPLICIT DENY                                       |
|     - If ANY policy says "Deny", access is denied                |
|     - Explicit Deny cannot be overridden                         |
|                                                                   |
|  3. Check for EXPLICIT ALLOW                                      |
|     - If a policy says "Allow" (and no Deny), access is granted  |
|                                                                   |
+------------------------------------------------------------------+

EVALUATION ORDER:
+----------------+     +----------------+     +----------------+
| Explicit Deny  | >   | Explicit Allow | >   | Implicit Deny  |
| (WINS ALWAYS)  |     | (If no deny)   |     | (Default)      |
+----------------+     +----------------+     +----------------+
```

### Example: How Deny Overrides Allow

```json
// Policy 1: Attached to user (via group)
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

// Policy 2: Also attached to user (inline)
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": "s3:DeleteBucket",
            "Resource": "*"
        }
    ]
}

// RESULT: User can do everything in S3 EXCEPT delete buckets
// The Deny in Policy 2 overrides the Allow in Policy 1
```

---

## The Action Element

### Action Format

```
service-prefix:ActionName

Examples:
- s3:GetObject           (S3 service, GetObject action)
- ec2:RunInstances       (EC2 service, RunInstances action)
- lambda:InvokeFunction  (Lambda service, InvokeFunction action)
```

### Wildcard Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `*` | All actions in all services | Everything |
| `s3:*` | All S3 actions | GetObject, PutObject, DeleteBucket, etc. |
| `s3:Get*` | All S3 Get actions | GetObject, GetBucketPolicy, GetBucketAcl |
| `s3:*Object` | Actions ending in "Object" | GetObject, PutObject, DeleteObject |

### Action Categories by Service

```
+------------------------------------------------------------------+
|                     COMMON S3 ACTIONS                             |
+------------------------------------------------------------------+
| Bucket Operations     | Object Operations      | Permission Ops   |
|-----------------------|------------------------|------------------|
| s3:CreateBucket       | s3:GetObject          | s3:GetBucketAcl  |
| s3:DeleteBucket       | s3:PutObject          | s3:PutBucketAcl  |
| s3:ListBucket         | s3:DeleteObject       | s3:GetBucketPolicy|
| s3:ListAllMyBuckets   | s3:GetObjectVersion   | s3:PutBucketPolicy|
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                     COMMON EC2 ACTIONS                            |
+------------------------------------------------------------------+
| Instance Ops          | Network Ops            | Security Ops     |
|-----------------------|------------------------|------------------|
| ec2:RunInstances      | ec2:CreateVpc         | ec2:AuthorizeSG* |
| ec2:TerminateInstances| ec2:CreateSubnet      | ec2:RevokeSG*    |
| ec2:StartInstances    | ec2:AttachInternetGW  | ec2:CreateKeyPair|
| ec2:StopInstances     | ec2:AllocateAddress   | ec2:ImportKeyPair|
| ec2:DescribeInstances | ec2:AssociateAddress  |                  |
+------------------------------------------------------------------+
```

### Finding Available Actions

```bash
# Use AWS CLI to list available actions for a service
aws iam list-policies --scope AWS --query 'Policies[?contains(PolicyName, `S3`)].Arn'

# Use the IAM policy simulator
# https://policysim.aws.amazon.com/

# Reference documentation
# https://docs.aws.amazon.com/service-authorization/latest/reference/
```

---

## The Resource Element

### ARN Format

```
arn:partition:service:region:account-id:resource-type/resource-id

Components:
- arn          : Literal string "arn"
- partition    : aws, aws-cn (China), aws-us-gov (GovCloud)
- service      : Service namespace (s3, ec2, iam, lambda, etc.)
- region       : AWS region (us-east-1, eu-west-1, etc.) - some services are global
- account-id   : 12-digit AWS account ID (or blank for some services)
- resource     : Resource-specific identifier
```

### ARN Examples by Service

```
+------------------------------------------------------------------+
|                     ARN EXAMPLES                                  |
+------------------------------------------------------------------+
| Service  | Example ARN                                           |
|----------|-------------------------------------------------------|
| S3       | arn:aws:s3:::bucket-name                              |
| S3       | arn:aws:s3:::bucket-name/folder/object.txt            |
| S3       | arn:aws:s3:::bucket-name/*                            |
| EC2      | arn:aws:ec2:us-east-1:123456789012:instance/i-abc123  |
| EC2      | arn:aws:ec2:us-east-1:123456789012:volume/vol-xyz789  |
| Lambda   | arn:aws:lambda:us-east-1:123456789012:function:MyFunc |
| IAM      | arn:aws:iam::123456789012:user/john                   |
| IAM      | arn:aws:iam::123456789012:role/EC2Role                |
| DynamoDB | arn:aws:dynamodb:us-east-1:123456789012:table/MyTable |
| RDS      | arn:aws:rds:us-east-1:123456789012:db:mydb            |
| SNS      | arn:aws:sns:us-east-1:123456789012:my-topic           |
| SQS      | arn:aws:sqs:us-east-1:123456789012:my-queue           |
+------------------------------------------------------------------+

Note: IAM and S3 are global services, so region is empty in their ARNs
```

### Resource Wildcards

```json
// Match ALL resources (dangerous!)
"Resource": "*"

// Match all objects in a specific bucket
"Resource": "arn:aws:s3:::my-bucket/*"

// Match all resources in a specific region/account
"Resource": "arn:aws:ec2:us-east-1:123456789012:*"

// Match specific pattern
"Resource": "arn:aws:s3:::my-bucket/logs/*"

// Multiple resources
"Resource": [
    "arn:aws:s3:::bucket-a/*",
    "arn:aws:s3:::bucket-b/*"
]
```

### Important: S3 Bucket vs Object ARNs

```json
// COMMON MISTAKE: Not including both bucket and object ARNs

// This FAILS for ListBucket:
{
    "Effect": "Allow",
    "Action": ["s3:ListBucket", "s3:GetObject"],
    "Resource": "arn:aws:s3:::my-bucket/*"  // Objects only!
}

// CORRECT: Include both bucket and object resources
{
    "Effect": "Allow",
    "Action": "s3:ListBucket",
    "Resource": "arn:aws:s3:::my-bucket"    // Bucket level
},
{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"  // Object level
}
```

---

## The Condition Element

### Condition Structure

```json
"Condition": {
    "ConditionOperator": {
        "ConditionKey": "ConditionValue"
    }
}
```

### Common Condition Operators

| Operator | Description | Example Use |
|----------|-------------|-------------|
| `StringEquals` | Exact string match (case-sensitive) | Matching tags, usernames |
| `StringLike` | String with wildcards (* and ?) | Pattern matching |
| `NumericEquals` | Exact number match | Port numbers |
| `NumericLessThan` | Less than | Date comparisons |
| `DateGreaterThan` | Date after specified | Time-based access |
| `Bool` | Boolean comparison | MFA requirement |
| `IpAddress` | IP range match | Network restrictions |
| `ArnLike` | ARN pattern match | Resource patterns |

### Common Condition Keys

```
+------------------------------------------------------------------+
|                     GLOBAL CONDITION KEYS                         |
+------------------------------------------------------------------+
| Key                        | Description                          |
|----------------------------|--------------------------------------|
| aws:SourceIp               | IP address of requester              |
| aws:CurrentTime            | Current date/time                    |
| aws:SecureTransport        | True if HTTPS used                   |
| aws:MultiFactorAuthPresent | True if MFA was used                 |
| aws:MultiFactorAuthAge     | Seconds since MFA authentication     |
| aws:PrincipalTag/key       | Tags on the principal                |
| aws:RequestTag/key         | Tags in the request                  |
| aws:ResourceTag/key        | Tags on the resource                 |
| aws:userid                 | User ID of the caller                |
| aws:username               | Friendly name of the caller          |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                     SERVICE-SPECIFIC KEYS                         |
+------------------------------------------------------------------+
| Service | Key                    | Description                    |
|---------|------------------------|--------------------------------|
| S3      | s3:prefix              | Object key prefix              |
| S3      | s3:x-amz-acl           | ACL specified in request       |
| EC2     | ec2:InstanceType       | Type of EC2 instance           |
| EC2     | ec2:Region             | Region of the resource         |
| RDS     | rds:DatabaseEngine     | Database engine type           |
+------------------------------------------------------------------+
```

### Condition Examples

#### Example 1: Require MFA for Destructive Actions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAllS3Actions",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        },
        {
            "Sid": "DenyDeleteWithoutMFA",
            "Effect": "Deny",
            "Action": [
                "s3:DeleteBucket",
                "s3:DeleteObject"
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

#### Example 2: IP-Based Access Restriction

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowFromCorporateNetwork",
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": [
                        "203.0.113.0/24",
                        "198.51.100.0/24"
                    ]
                }
            }
        }
    ]
}
```

#### Example 3: Time-Based Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowDuringBusinessHours",
            "Effect": "Allow",
            "Action": "ec2:*",
            "Resource": "*",
            "Condition": {
                "DateGreaterThan": {
                    "aws:CurrentTime": "2024-01-01T09:00:00Z"
                },
                "DateLessThan": {
                    "aws:CurrentTime": "2024-12-31T17:00:00Z"
                }
            }
        }
    ]
}
```

#### Example 4: Tag-Based Access Control (ABAC)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAccessToOwnProject",
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Project": "${aws:PrincipalTag/Project}"
                }
            }
        }
    ]
}
```

### Condition Logic

```
+------------------------------------------------------------------+
|                     CONDITION EVALUATION                          |
+------------------------------------------------------------------+
|                                                                   |
|  Multiple Condition Operators = AND                               |
|  +-----------------------------------------------------------+   |
|  | "Condition": {                                             |   |
|  |     "IpAddress": {...},     <-- Must be true               |   |
|  |     "Bool": {...}           <-- AND must be true           |   |
|  | }                                                          |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
|  Multiple Values within Operator = OR                             |
|  +-----------------------------------------------------------+   |
|  | "IpAddress": {                                             |   |
|  |     "aws:SourceIp": [                                      |   |
|  |         "10.0.0.0/8",       <-- If this matches            |   |
|  |         "192.168.0.0/16"    <-- OR this matches            |   |
|  |     ]                                                      |   |
|  | }                                                          |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Policy Types

### Type 1: AWS Managed Policies

```
+------------------------------------------------------------------+
|                     AWS MANAGED POLICIES                          |
+------------------------------------------------------------------+
|                                                                   |
|  Characteristics:                                                 |
|  - Created and maintained by AWS                                  |
|  - Updated automatically when services change                     |
|  - Cannot be modified                                             |
|  - Broad permissions for common use cases                         |
|                                                                   |
|  Naming Convention:                                               |
|  - arn:aws:iam::aws:policy/PolicyName                            |
|                                                                   |
|  Examples:                                                        |
|  +------------------------------------------------------------+  |
|  | AdministratorAccess      | Full access to all AWS services |  |
|  | PowerUserAccess          | Full access except IAM          |  |
|  | ReadOnlyAccess           | View-only across all services   |  |
|  | AmazonS3FullAccess       | Full S3 access                  |  |
|  | AmazonS3ReadOnlyAccess   | Read-only S3 access             |  |
|  | AmazonEC2FullAccess      | Full EC2 access                 |  |
|  | AmazonDynamoDBFullAccess | Full DynamoDB access            |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### Type 2: Customer Managed Policies

```
+------------------------------------------------------------------+
|                   CUSTOMER MANAGED POLICIES                       |
+------------------------------------------------------------------+
|                                                                   |
|  Characteristics:                                                 |
|  - Created and maintained by you                                  |
|  - Full control over permissions                                  |
|  - Reusable across users, groups, roles                          |
|  - Supports versioning (up to 5 versions)                        |
|                                                                   |
|  Naming Convention:                                               |
|  - arn:aws:iam::ACCOUNT_ID:policy/PolicyName                     |
|                                                                   |
|  Best Practices:                                                  |
|  - Use for organization-specific permissions                     |
|  - Version control for audit trail                               |
|  - Use meaningful names and descriptions                         |
|                                                                   |
+------------------------------------------------------------------+
```

### Type 3: Inline Policies

```
+------------------------------------------------------------------+
|                       INLINE POLICIES                             |
+------------------------------------------------------------------+
|                                                                   |
|  Characteristics:                                                 |
|  - Embedded directly in a user, group, or role                   |
|  - 1:1 relationship with the entity                              |
|  - Deleted when the entity is deleted                            |
|  - Cannot be reused                                               |
|                                                                   |
|  When to Use:                                                     |
|  - Strict 1:1 relationship needed                                |
|  - Policy should not accidentally apply to others                |
|  - Temporary exceptions or special cases                         |
|                                                                   |
|  When NOT to Use:                                                 |
|  - Common permissions shared by multiple entities                |
|  - Policies that need versioning                                 |
|  - Anything you want to reuse                                    |
|                                                                   |
+------------------------------------------------------------------+
```

### Comparison Table

| Aspect | AWS Managed | Customer Managed | Inline |
|--------|-------------|------------------|--------|
| Creator | AWS | You | You |
| Reusable | Yes | Yes | No |
| Versioning | N/A (AWS handles) | Yes (5 versions) | No |
| Maintenance | AWS | You | You |
| Deletion | Cannot delete | Must have no attachments | With entity |
| Use Case | Common scenarios | Org-specific needs | Exceptions |

---

## Policy Variables

Policy variables enable dynamic policies that adapt to the context of the request.

### Common Variables

```json
// ${aws:username} - The username of the requester
// ${aws:userid} - The user ID
// ${aws:PrincipalTag/key} - Tag on the principal
// ${aws:ResourceTag/key} - Tag on the resource
// ${aws:CurrentTime} - Current time
// ${aws:EpochTime} - Current time in epoch
// ${aws:SourceIp} - Source IP address
// ${s3:prefix} - S3 key prefix
// ${s3:x-amz-acl} - Requested S3 ACL
```

### Example: User-Specific S3 Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowUserSpecificS3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::company-bucket/users/${aws:username}/*"
        },
        {
            "Sid": "AllowListingOwnFolder",
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::company-bucket",
            "Condition": {
                "StringLike": {
                    "s3:prefix": ["users/${aws:username}/*"]
                }
            }
        }
    ]
}
```

This policy allows each user to only access their own folder in S3.

---

## Identity-Based vs Resource-Based Policies

### Identity-Based Policies

```
+------------------------------------------------------------------+
|                   IDENTITY-BASED POLICIES                         |
+------------------------------------------------------------------+
|                                                                   |
|  Attached to: Users, Groups, Roles                               |
|  Answer: "What can this identity do?"                            |
|  NO Principal element (identity IS the principal)                |
|                                                                   |
|  Example:                                                         |
|  {                                                                |
|      "Version": "2012-10-17",                                    |
|      "Statement": [                                               |
|          {                                                        |
|              "Effect": "Allow",                                   |
|              "Action": "s3:GetObject",                           |
|              "Resource": "arn:aws:s3:::bucket/*"                 |
|          }                                                        |
|      ]                                                            |
|  }                                                                |
+------------------------------------------------------------------+
```

### Resource-Based Policies

```
+------------------------------------------------------------------+
|                   RESOURCE-BASED POLICIES                         |
+------------------------------------------------------------------+
|                                                                   |
|  Attached to: Resources (S3 buckets, SQS queues, etc.)           |
|  Answer: "Who can access this resource?"                         |
|  REQUIRES Principal element                                       |
|                                                                   |
|  Example (S3 Bucket Policy):                                      |
|  {                                                                |
|      "Version": "2012-10-17",                                    |
|      "Statement": [                                               |
|          {                                                        |
|              "Effect": "Allow",                                   |
|              "Principal": {                                       |
|                  "AWS": "arn:aws:iam::111122223333:root"         |
|              },                                                   |
|              "Action": "s3:GetObject",                           |
|              "Resource": "arn:aws:s3:::my-bucket/*"              |
|          }                                                        |
|      ]                                                            |
|  }                                                                |
+------------------------------------------------------------------+
```

### When Both Apply

```
SAME ACCOUNT:
+------------------+     +------------------+
| Identity-Based   | OR  | Resource-Based   | = ACCESS GRANTED
| Policy ALLOWS    |     | Policy ALLOWS    |   (if no DENY)
+------------------+     +------------------+

CROSS-ACCOUNT:
+------------------+     +------------------+
| Identity-Based   | AND | Resource-Based   | = ACCESS GRANTED
| Policy ALLOWS    |     | Policy ALLOWS    |   (BOTH required)
+------------------+     +------------------+
```

---

## Permission Boundaries

### What is a Permission Boundary?

```
+------------------------------------------------------------------+
|                     PERMISSION BOUNDARIES                         |
+------------------------------------------------------------------+
|                                                                   |
|  Definition:                                                      |
|  A managed policy that sets the MAXIMUM permissions that an      |
|  identity-based policy can grant to an IAM entity.               |
|                                                                   |
|  Visual:                                                          |
|  +-------------------------------+                                |
|  |    Permission Boundary        |                                |
|  |    (Maximum possible)         |                                |
|  |   +----------------------+    |                                |
|  |   |  Identity Policy     |    |                                |
|  |   |  (Requested perms)   |    |                                |
|  |   |   +-----------+      |    |                                |
|  |   |   | EFFECTIVE |      |    |                                |
|  |   |   | (Overlap) |      |    |                                |
|  |   |   +-----------+      |    |                                |
|  |   +----------------------+    |                                |
|  +-------------------------------+                                |
|                                                                   |
|  Effective = Identity Policy ∩ Permission Boundary               |
|                                                                   |
+------------------------------------------------------------------+
```

### Example: Limiting Admin Delegation

```json
// Permission Boundary: DeveloperBoundary
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "dynamodb:*",
                "lambda:*",
                "logs:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Deny",
            "Action": [
                "iam:*",
                "organizations:*",
                "account:*"
            ],
            "Resource": "*"
        }
    ]
}
```

Even if a developer gets AdministratorAccess attached, they cannot access IAM, Organizations, or Account settings.

---

## Debugging Policies

### Using the IAM Policy Simulator

```bash
# Web-based simulator
# https://policysim.aws.amazon.com/

# CLI-based simulation
aws iam simulate-principal-policy \
    --policy-source-arn arn:aws:iam::123456789012:user/john \
    --action-names s3:GetObject \
    --resource-arns arn:aws:s3:::my-bucket/file.txt
```

### Common Policy Errors

```
+------------------------------------------------------------------+
|                     COMMON POLICY ERRORS                          |
+------------------------------------------------------------------+

ERROR 1: MalformedPolicyDocument
---------------------------------
Cause: Invalid JSON syntax
Fix: Validate JSON (use jsonlint or AWS console)

ERROR 2: Invalid Action
------------------------
Cause: Typo in action name
Fix: Check service prefix and action spelling

ERROR 3: Invalid Resource
--------------------------
Cause: Wrong ARN format
Fix: Verify ARN structure for the service

ERROR 4: Policy exceeds size limit
-----------------------------------
Cause: Policy too large (2KB inline, 6KB managed)
Fix: Split into multiple policies or use wildcards

ERROR 5: Access Denied despite Allow
-------------------------------------
Cause: Explicit Deny somewhere, missing Resource, SCP blocking
Fix: Check all applicable policies, service control policies
```

### Policy Evaluation Debugging

```bash
# Get the last accessed service data
aws iam get-service-last-accessed-details \
    --job-id <job-id-from-generate>

# Generate a service last accessed report
aws iam generate-service-last-accessed-details \
    --arn arn:aws:iam::123456789012:user/john

# Get policy version
aws iam get-policy-version \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy \
    --version-id v1
```

---

## AWS CLI Commands for Policy Management

```bash
# List all customer managed policies
aws iam list-policies --scope Local

# Create a new policy
aws iam create-policy \
    --policy-name MyPolicy \
    --policy-document file://policy.json \
    --description "My custom policy"

# Get policy details
aws iam get-policy \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy

# List policy versions
aws iam list-policy-versions \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy

# Create a new policy version
aws iam create-policy-version \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy \
    --policy-document file://new-policy.json \
    --set-as-default

# Delete a policy version
aws iam delete-policy-version \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy \
    --version-id v1

# Attach policy to user
aws iam attach-user-policy \
    --user-name john \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy

# Attach policy to group
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy

# Attach policy to role
aws iam attach-role-policy \
    --role-name MyRole \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy

# List attached user policies
aws iam list-attached-user-policies --user-name john

# Put inline policy on user
aws iam put-user-policy \
    --user-name john \
    --policy-name InlinePolicy \
    --policy-document file://inline-policy.json

# Delete policy
aws iam delete-policy \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy
```

---

## Key Takeaways

1. **Version**: Always use `"2012-10-17"`
2. **Effect**: Only `Allow` or `Deny` - Deny always wins
3. **Action**: Format is `service:ActionName` - wildcards are powerful but dangerous
4. **Resource**: Use ARNs - remember bucket vs object distinction for S3
5. **Condition**: AND between operators, OR within operators
6. **Policy Types**: Prefer customer managed for reusability
7. **Least Privilege**: Start with nothing, add what's needed

---

## Next Steps

Continue to [03-iam-users-groups.md](./03-iam-users-groups.md) to learn how to manage IAM users and groups effectively.
