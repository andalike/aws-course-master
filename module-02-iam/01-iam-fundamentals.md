# IAM Fundamentals: Users, Groups, Roles, and Policies

## Introduction

AWS Identity and Access Management (IAM) is built on four fundamental building blocks. Understanding these components and how they interact is essential for securing your AWS environment.

---

## The Four Pillars of IAM

```
                    +------------------+
                    |    POLICIES      |
                    | (The Permission  |
                    |    Documents)    |
                    +--------+---------+
                             |
           +-----------------+-----------------+
           |                 |                 |
           v                 v                 v
    +------+------+   +------+------+   +------+------+
    |    USERS    |   |   GROUPS    |   |    ROLES    |
    | (Identities)|   | (User       |   | (Temporary  |
    |             |   |  Collections)|   |  Identities)|
    +-------------+   +-------------+   +-------------+
```

---

## 1. IAM Users

### What is an IAM User?

An IAM user is an identity that represents a person or application that interacts with AWS. Each user has a unique name within your AWS account and has their own credentials.

### Real-World Analogy: Employee ID Badge

Think of an IAM user like an employee at a company:

```
COMPANY                              AWS
-------                              ---
Employee Name: John Smith     -->    IAM User: john.smith
Employee ID: 12345           -->    User ARN: arn:aws:iam::123456789012:user/john.smith
ID Badge                     -->    Access Keys or Password
Department Access Card       -->    Attached Policies
```

### User Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Unique Name** | Must be unique within the AWS account |
| **ARN** | Amazon Resource Name uniquely identifying the user globally |
| **Credentials** | Password (console) and/or Access Keys (programmatic) |
| **Path** | Optional organizational path (e.g., /developers/frontend/) |

### Types of User Credentials

```
+------------------+------------------------+----------------------+
|   CREDENTIAL     |      USE CASE          |     COMPONENTS       |
+------------------+------------------------+----------------------+
| Console Password | AWS Management Console | Username + Password  |
|                  | (Web Browser)          | + Optional MFA       |
+------------------+------------------------+----------------------+
| Access Keys      | AWS CLI, SDKs, APIs    | Access Key ID +      |
|                  | (Programmatic)         | Secret Access Key    |
+------------------+------------------------+----------------------+
```

### When to Create IAM Users

**Do Create Users For:**
- Human employees who need AWS console access
- Applications that cannot assume roles
- Long-term, static credentials requirements

**Don't Create Users For:**
- AWS services (use roles instead)
- Temporary access needs
- Large numbers of external users (use federation)

### AWS CLI: Managing Users

```bash
# Create a new user
aws iam create-user --user-name john.smith

# Create user with path (organizational structure)
aws iam create-user --user-name jane.doe --path /developers/backend/

# List all users
aws iam list-users

# Get specific user details
aws iam get-user --user-name john.smith

# Delete a user (must remove dependencies first)
aws iam delete-user --user-name john.smith
```

---

## 2. IAM Groups

### What is an IAM Group?

A group is a collection of IAM users. Groups let you specify permissions for multiple users, making it easier to manage permissions for collections of users.

### Real-World Analogy: Department Access

```
COMPANY SCENARIO                           AWS EQUIVALENT
----------------                           --------------
Marketing Department                  -->  IAM Group: Marketing
  - Can access marketing tools             - Has S3 read policy
  - Can view campaign data                 - Has CloudWatch read policy
  - Cannot modify infrastructure           - No EC2/RDS policies

Engineering Department                -->  IAM Group: Engineering
  - Can deploy code                        - Has CodeDeploy access
  - Can view logs                          - Has CloudWatch full access
  - Can manage dev environments            - Has EC2/RDS dev access
```

### Group Characteristics

| Characteristic | Description |
|---------------|-------------|
| **No Nesting** | Groups cannot contain other groups |
| **User Membership** | A user can belong to multiple groups (max 10) |
| **No Credentials** | Groups don't have their own credentials |
| **Policy Inheritance** | Users inherit all policies attached to their groups |

### How Group Permissions Work

```
                        +------------------+
                        |   Developers     |
                        |     Group        |
                        +--------+---------+
                                 |
                    +------------+------------+
                    |                         |
           +--------v--------+       +--------v--------+
           | EC2ReadOnly     |       | S3FullAccess    |
           | Policy          |       | Policy          |
           +-----------------+       +-----------------+
                    |                         |
                    +-----------+-------------+
                                |
                    +-----------v-----------+
                    |     User: Alice       |
                    | (Member of Developers)|
                    |                       |
                    | Effective Permissions:|
                    | - EC2 Read Only       |
                    | - S3 Full Access      |
                    +-----------------------+
```

### AWS CLI: Managing Groups

```bash
# Create a group
aws iam create-group --group-name Developers

# Add user to group
aws iam add-user-to-group --user-name john.smith --group-name Developers

# List groups
aws iam list-groups

# List users in a group
aws iam get-group --group-name Developers

# Remove user from group
aws iam remove-user-from-group --user-name john.smith --group-name Developers

# Delete a group (must be empty)
aws iam delete-group --group-name Developers
```

### Common Group Structures

```
                            +------------------+
                            |   AWS Account    |
                            +--------+---------+
                                     |
          +--------------------------+---------------------------+
          |              |              |              |         |
    +-----v-----+  +-----v-----+  +-----v-----+  +-----v-----+  +-----v-----+
    |   Admin   |  |   Dev     |  |    QA     |  |  DevOps   |  |  ReadOnly |
    |   Group   |  |   Group   |  |   Group   |  |   Group   |  |   Group   |
    +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
    | Full Admin|  | Dev Envs  |  | Test Envs |  | All Envs  |  | View Only |
    | Access    |  | Only      |  | Only      |  | + Deploy  |  | Access    |
    +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
```

---

## 3. IAM Roles

### What is an IAM Role?

An IAM role is an identity with specific permissions that can be assumed by anyone or anything that needs it. Unlike users, roles don't have permanent credentials - they provide temporary security credentials.

### Real-World Analogy: Wearing Different Hats

```
REAL WORLD SCENARIO                        AWS EQUIVALENT
-------------------                        --------------
A contractor visits your office:      -->  External user assumes role:
  - Gets a visitor badge                   - Receives temporary credentials
  - Badge expires at end of day            - Credentials expire (1-12 hours)
  - Limited to specific areas              - Limited to role's permissions

An employee covers for a manager:     -->  User assumes admin role:
  - Temporarily has manager access         - Gets temporary elevated permissions
  - Returns to normal after task           - Returns to normal user permissions
```

### Role Components

```
+------------------------------------------------------------------+
|                         IAM ROLE                                  |
+------------------------------------------------------------------+
|                                                                   |
|  +---------------------------+   +----------------------------+   |
|  |    TRUST POLICY           |   |    PERMISSIONS POLICY      |   |
|  |    (Who can assume)       |   |    (What they can do)      |   |
|  +---------------------------+   +----------------------------+   |
|  | - AWS Services            |   | - S3 Read/Write            |   |
|  | - IAM Users               |   | - DynamoDB Access          |   |
|  | - Other AWS Accounts      |   | - Lambda Invoke            |   |
|  | - Federated Users         |   | - EC2 Operations           |   |
|  +---------------------------+   +----------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

### Types of Roles

| Role Type | Who Assumes It | Example Use Case |
|-----------|---------------|------------------|
| **Service Role** | AWS Services | EC2 instance accessing S3 |
| **Cross-Account Role** | Users in other AWS accounts | Partner company access |
| **Federation Role** | External identity providers | Corporate SSO users |
| **Service-Linked Role** | Specific AWS services | Auto-created for some services |

### When to Use Roles (Decision Tree)

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
    | Use SERVICE ROLE |          | Is access needed  |
    | (EC2, Lambda,    |          | cross-account?    |
    |  ECS, etc.)      |          +--------+----------+
    +------------------+                   |
                               +-----------+-----------+
                               |                       |
                             YES                      NO
                               |                       |
                               v                       v
                    +------------------+     +-------------------+
                    | Use CROSS-ACCT   |     | Is this for       |
                    | ROLE             |     | temporary access? |
                    +------------------+     +--------+----------+
                                                      |
                                          +-----------+-----------+
                                          |                       |
                                        YES                      NO
                                          |                       |
                                          v                       v
                               +------------------+    +------------------+
                               | Use ROLE with    |    | Use IAM USER     |
                               | AssumeRole       |    | (long-term       |
                               +------------------+    |  credentials)    |
                                                       +------------------+
```

### How Role Assumption Works

```
Step 1: Request to Assume Role
+-------------+                              +-------------+
|   User or   |  ---- AssumeRole Request --> |    AWS      |
|   Service   |                              |    STS      |
+-------------+                              +------+------+
                                                    |
Step 2: STS Validates and Returns Credentials       |
                                                    v
                                           +----------------+
                                           | Check Trust    |
                                           | Policy         |
                                           +-------+--------+
                                                   |
                                    +--------------+--------------+
                                    |                             |
                                 ALLOWED                       DENIED
                                    |                             |
                                    v                             v
                           +----------------+            +----------------+
                           | Return Temp    |            | Access Denied  |
                           | Credentials:   |            | Error          |
                           | - Access Key   |            +----------------+
                           | - Secret Key   |
                           | - Session Token|
                           | - Expiration   |
                           +----------------+

Step 3: Use Temporary Credentials
+-------------+                              +-------------+
|   User or   |  ---- API Call with -------> |    AWS      |
|   Service   |      Temp Credentials        |   Service   |
+-------------+                              +-------------+
```

### AWS CLI: Managing Roles

```bash
# Create a role (requires trust policy document)
aws iam create-role \
    --role-name EC2-S3-Access \
    --assume-role-policy-document file://trust-policy.json

# Attach a policy to the role
aws iam attach-role-policy \
    --role-name EC2-S3-Access \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# List roles
aws iam list-roles

# Assume a role (get temporary credentials)
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/EC2-S3-Access \
    --role-session-name MySession

# Delete a role (must detach policies first)
aws iam delete-role --role-name EC2-S3-Access
```

### Example Trust Policy

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

---

## 4. IAM Policies

### What is an IAM Policy?

A policy is a JSON document that defines permissions. Policies specify what actions are allowed or denied on which AWS resources.

### Real-World Analogy: Permission Slips

```
SCHOOL PERMISSION SLIP                    AWS IAM POLICY
---------------------                     --------------
"Johnny Smith may:                   -->  {
  - Leave school early                      "Effect": "Allow",
  - Only on Fridays                         "Action": "s3:GetObject",
  - Only for doctor appointments            "Resource": "arn:aws:s3:::bucket/*",
  - Signed by: Parent"                      "Condition": {...}
                                          }
```

### Policy Structure Overview

```json
{
    "Version": "2012-10-17",           // Policy language version
    "Statement": [                      // Array of permission statements
        {
            "Sid": "DescriptiveName",   // Optional statement ID
            "Effect": "Allow",          // Allow or Deny
            "Action": [                 // What actions
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [               // On what resources
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {              // Under what conditions (optional)
                "IpAddress": {
                    "aws:SourceIp": "192.168.1.0/24"
                }
            }
        }
    ]
}
```

### Types of Policies

```
+------------------------------------------------------------------+
|                      POLICY TYPES                                 |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+  +-------------------+  +----------------+ |
|  | AWS MANAGED       |  | CUSTOMER MANAGED  |  | INLINE         | |
|  +-------------------+  +-------------------+  +----------------+ |
|  | - Created by AWS  |  | - Created by you  |  | - Embedded in  | |
|  | - Updated by AWS  |  | - Full control    |  |   user/group/  | |
|  | - Common use cases|  | - Reusable        |  |   role         | |
|  | - Cannot modify   |  | - Versioned       |  | - Not reusable | |
|  +-------------------+  +-------------------+  +----------------+ |
|                                                                   |
|  Example:              Example:              Example:             |
|  AdministratorAccess   CompanyS3Policy       Specific user       |
|  ReadOnlyAccess        ProjectDBAccess       exception           |
|  AmazonS3FullAccess                                              |
+------------------------------------------------------------------+
```

### Policy Evaluation Logic

When a principal makes a request, AWS evaluates all applicable policies:

```
                    +------------------+
                    |  API Request     |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Is there an      |
                    | explicit DENY?   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
            YES                            NO
              |                             |
              v                             v
    +------------------+          +------------------+
    |  ACCESS DENIED   |          | Is there an      |
    |  (Final)         |          | explicit ALLOW?  |
    +------------------+          +--------+---------+
                                           |
                                +-----------+-----------+
                                |                       |
                              YES                      NO
                                |                       |
                                v                       v
                    +------------------+     +------------------+
                    |  ACCESS ALLOWED  |     |  ACCESS DENIED   |
                    +------------------+     |  (Implicit Deny) |
                                             +------------------+
```

**Key Rule: Explicit Deny > Explicit Allow > Implicit Deny**

### AWS CLI: Managing Policies

```bash
# List AWS managed policies
aws iam list-policies --scope AWS

# List customer managed policies
aws iam list-policies --scope Local

# Create a customer managed policy
aws iam create-policy \
    --policy-name MyCustomPolicy \
    --policy-document file://policy.json

# Attach policy to user
aws iam attach-user-policy \
    --user-name john.smith \
    --policy-arn arn:aws:iam::123456789012:policy/MyCustomPolicy

# Attach policy to group
aws iam attach-group-policy \
    --group-name Developers \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Attach policy to role
aws iam attach-role-policy \
    --role-name EC2-S3-Access \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

---

## How Everything Works Together

### Complete Example Scenario

```
SCENARIO: A development team needs access to development S3 buckets and EC2 instances

+------------------------------------------------------------------+
|                         AWS ACCOUNT                               |
+------------------------------------------------------------------+
|                                                                   |
|  GROUPS:                                                          |
|  +------------------+                                             |
|  |   Developers     |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           |  Attached Policies:                                   |
|           |  +---------------------------------------------+      |
|           +->| DevS3Access (Customer Managed)              |      |
|           |  | - s3:* on arn:aws:s3:::dev-*               |      |
|           |  +---------------------------------------------+      |
|           |  +---------------------------------------------+      |
|           +->| DevEC2Access (Customer Managed)             |      |
|              | - ec2:Describe* on all resources            |      |
|              | - ec2:Start/StopInstances on dev instances  |      |
|              +---------------------------------------------+      |
|                                                                   |
|  USERS (Members of Developers):                                   |
|  +-------------+  +-------------+  +-------------+                |
|  | alice       |  | bob         |  | charlie     |                |
|  | (Dev Lead)  |  | (Backend)   |  | (Frontend)  |                |
|  +------+------+  +-------------+  +-------------+                |
|         |                                                         |
|         |  Additional Inline Policy (special permission):         |
|         |  +---------------------------------------------+        |
|         +->| Can also access prod S3 for deployments     |        |
|            +---------------------------------------------+        |
|                                                                   |
|  ROLES:                                                           |
|  +------------------+                                             |
|  | EC2-Dev-Role     | <-- Assumed by EC2 instances                |
|  +--------+---------+                                             |
|           |                                                       |
|           |  Attached Policies:                                   |
|           |  +---------------------------------------------+      |
|           +->| AmazonS3ReadOnlyAccess (AWS Managed)        |      |
|           |  +---------------------------------------------+      |
|           |  +---------------------------------------------+      |
|           +->| CloudWatchLogsFullAccess (AWS Managed)      |      |
|              +---------------------------------------------+      |
|                                                                   |
+------------------------------------------------------------------+
```

### Effective Permissions Calculation

For user `alice`:

```
Group Permissions (from Developers):
  + DevS3Access: s3:* on dev-* buckets
  + DevEC2Access: ec2:Describe*, ec2:Start/Stop on dev instances

User Inline Policy:
  + s3:GetObject on prod-deployment bucket

TOTAL EFFECTIVE PERMISSIONS:
  = DevS3Access + DevEC2Access + Inline Policy
  = Full S3 on dev buckets
    + EC2 describe all, start/stop dev
    + S3 read on prod-deployment bucket
```

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Not Using Groups

```
BAD: Attaching policies directly to each user
+--------+     +-----------+
| User 1 |---->| Policy A  |
+--------+     +-----------+
+--------+     +-----------+
| User 2 |---->| Policy A  |  (Same policy attached multiple times!)
+--------+     +-----------+
+--------+     +-----------+
| User 3 |---->| Policy A  |
+--------+     +-----------+

GOOD: Using groups for common permissions
+--------+     +----------+     +-----------+
| User 1 |---->|          |     |           |
+--------+     |  Group   |---->| Policy A  |
+--------+     |          |     |           |
| User 2 |---->|          |     +-----------+
+--------+     +----------+
+--------+         ^
| User 3 |---------+
+--------+
```

### Mistake 2: Using Users Instead of Roles for Services

```
BAD: Hardcoding user credentials in EC2 application
+-------------+                    +-------------+
|    EC2      |  Access Key ID +   |     S3      |
|  Instance   |  Secret Key        |   Bucket    |
| (has creds) |  (INSECURE!)       |             |
+-------------+ -----------------> +-------------+

GOOD: Using instance profile with role
+-------------+     +-------------+     +-------------+
|    EC2      |     | Instance    |     |     S3      |
|  Instance   |<--->| Profile     |---->|   Bucket    |
| (no creds)  |     | (IAM Role)  |     |             |
+-------------+     +-------------+     +-------------+
                    Temp credentials
                    auto-rotated
```

### Mistake 3: Overly Permissive Policies

```json
// BAD: The "god mode" policy
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

// GOOD: Specific permissions
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-specific-bucket",
                "arn:aws:s3:::my-specific-bucket/*"
            ]
        }
    ]
}
```

---

## Summary Comparison Table

| Aspect | User | Group | Role | Policy |
|--------|------|-------|------|--------|
| **Purpose** | Represent a person/app | Organize users | Temporary identity | Define permissions |
| **Credentials** | Password, Access Keys | None | Temporary (STS) | N/A |
| **Can have policies** | Yes | Yes | Yes | N/A (is the policy) |
| **Reusable** | No (unique) | Yes | Yes | Yes |
| **Best for** | Humans, legacy apps | Permission management | Services, federation | All of the above |

---

## Key Takeaways

1. **Users** = Long-term identities for humans and applications
2. **Groups** = Organizational units for managing user permissions efficiently
3. **Roles** = Temporary identities assumed by services, users, or federated identities
4. **Policies** = JSON documents that define what actions are allowed on what resources

---

## Next Steps

Now that you understand the fundamental building blocks, proceed to [02-iam-policies-deep-dive.md](./02-iam-policies-deep-dive.md) to learn how to write effective IAM policies.

---

## Practice Questions

1. A developer needs to access S3 and EC2 from their laptop. What should you create?
2. An EC2 instance needs to read from DynamoDB. What should you use?
3. You have 50 developers who all need the same permissions. What's the best approach?
4. A partner company needs temporary access to your S3 bucket. What's the solution?

*Answers are in the quiz at the end of this module.*
