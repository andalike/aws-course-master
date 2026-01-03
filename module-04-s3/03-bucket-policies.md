# 03 - Bucket Policies and Access Control

## Introduction

Amazon S3 provides multiple mechanisms to control access to buckets and objects. Understanding these access control options is crucial for securing your data while enabling appropriate access for users and applications.

---

## Access Control Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        S3 ACCESS CONTROL MECHANISMS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ IAM Policies    │    │ Bucket Policies │    │ ACLs (Legacy)   │         │
│  │                 │    │                 │    │                 │         │
│  │ - User/Role     │    │ - Resource-based│    │ - Object/Bucket │         │
│  │   based         │    │ - Cross-account │    │ - Limited       │         │
│  │ - Attached to   │    │ - Public access │    │ - Being phased  │         │
│  │   principal     │    │ - JSON format   │    │   out           │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ Block Public    │    │ Access Points   │    │ Pre-signed URLs │         │
│  │ Access          │    │                 │    │                 │         │
│  │                 │    │ - Named network │    │ - Temporary     │         │
│  │ - Account level │    │   endpoints     │    │   access        │         │
│  │ - Bucket level  │    │ - Dedicated     │    │ - Time-limited  │         │
│  │ - Override all  │    │   policies      │    │   credentials   │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Bucket Policies

### What are Bucket Policies?

Bucket policies are resource-based policies attached directly to S3 buckets. They define who can access the bucket and what actions they can perform.

### Policy Structure

```json
{
    "Version": "2012-10-17",
    "Id": "PolicyIdentifier",
    "Statement": [
        {
            "Sid": "StatementIdentifier",
            "Effect": "Allow | Deny",
            "Principal": "Who",
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

### Policy Elements Explained

| Element | Description | Required |
|---------|-------------|----------|
| **Version** | Policy language version (use "2012-10-17") | Yes |
| **Id** | Optional identifier for the policy | No |
| **Statement** | Array of individual statements | Yes |
| **Sid** | Statement identifier | No |
| **Effect** | Allow or Deny | Yes |
| **Principal** | Who the statement applies to | Yes |
| **Action** | Which S3 actions | Yes |
| **Resource** | Which bucket/objects | Yes |
| **Condition** | When the statement applies | No |

### Common Principals

```json
// Anyone (public)
"Principal": "*"

// Specific AWS account
"Principal": {"AWS": "arn:aws:iam::123456789012:root"}

// Specific IAM user
"Principal": {"AWS": "arn:aws:iam::123456789012:user/username"}

// Specific IAM role
"Principal": {"AWS": "arn:aws:iam::123456789012:role/rolename"}

// AWS service
"Principal": {"Service": "cloudfront.amazonaws.com"}

// Multiple principals
"Principal": {
    "AWS": [
        "arn:aws:iam::111111111111:root",
        "arn:aws:iam::222222222222:root"
    ]
}
```

### Common Actions

```json
// All S3 actions
"Action": "s3:*"

// Read operations
"Action": [
    "s3:GetObject",
    "s3:GetObjectVersion",
    "s3:GetBucketLocation"
]

// Write operations
"Action": [
    "s3:PutObject",
    "s3:DeleteObject"
]

// List operations
"Action": [
    "s3:ListBucket",
    "s3:ListBucketVersions"
]

// Bucket management
"Action": [
    "s3:CreateBucket",
    "s3:DeleteBucket",
    "s3:PutBucketPolicy"
]
```

### Resource Formats

```json
// Entire bucket (for bucket-level operations like ListBucket)
"Resource": "arn:aws:s3:::my-bucket"

// All objects in bucket
"Resource": "arn:aws:s3:::my-bucket/*"

// Both bucket and objects
"Resource": [
    "arn:aws:s3:::my-bucket",
    "arn:aws:s3:::my-bucket/*"
]

// Specific prefix
"Resource": "arn:aws:s3:::my-bucket/images/*"

// Specific object
"Resource": "arn:aws:s3:::my-bucket/documents/report.pdf"
```

---

## Bucket Policy Examples

### 1. Public Read Access (Static Website)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-website-bucket/*"
        }
    ]
}
```

### 2. Cross-Account Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CrossAccountAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::987654321098:root"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::shared-bucket",
                "arn:aws:s3:::shared-bucket/*"
            ]
        }
    ]
}
```

### 3. Restrict Access to Specific IP Addresses

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "IPAllow",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "NotIpAddress": {
                    "aws:SourceIp": [
                        "192.168.1.0/24",
                        "10.0.0.0/8",
                        "203.0.113.0/24"
                    ]
                }
            }
        }
    ]
}
```

### 4. Require HTTPS (SSL/TLS)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RequireSSL",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
```

### 5. Require Encryption at Upload

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyUnencryptedUploads",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "Null": {
                    "s3:x-amz-server-side-encryption": "true"
                }
            }
        },
        {
            "Sid": "RequireKMSEncryption",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "aws:kms"
                }
            }
        }
    ]
}
```

### 6. VPC Endpoint Access Only

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VPCEndpointOnly",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "StringNotEquals": {
                    "aws:sourceVpce": "vpce-1234567890abcdef0"
                }
            }
        }
    ]
}
```

### 7. CloudFront Origin Access Control (OAC)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/EDFDVBD6EXAMPLE"
                }
            }
        }
    ]
}
```

### 8. Allow Only Specific IAM Roles

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSpecificRoles",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::123456789012:role/Application-Role",
                    "arn:aws:iam::123456789012:role/Admin-Role"
                ]
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        },
        {
            "Sid": "DenyEveryone Else",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "StringNotLike": {
                    "aws:userId": [
                        "AROAEXAMPLEID1:*",
                        "AROAEXAMPLEID2:*"
                    ]
                }
            }
        }
    ]
}
```

---

## Managing Bucket Policies

### AWS CLI

```bash
# Get current bucket policy
aws s3api get-bucket-policy --bucket my-bucket --output text

# Put bucket policy from file
aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json

# Delete bucket policy
aws s3api delete-bucket-policy --bucket my-bucket

# Example: Create policy file and apply
cat > policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json
```

### Python (Boto3)

```python
import boto3
import json

s3_client = boto3.client('s3')

# Define policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}

# Apply policy
s3_client.put_bucket_policy(
    Bucket='my-bucket',
    Policy=json.dumps(policy)
)

# Get policy
response = s3_client.get_bucket_policy(Bucket='my-bucket')
current_policy = json.loads(response['Policy'])
print(json.dumps(current_policy, indent=2))

# Delete policy
s3_client.delete_bucket_policy(Bucket='my-bucket')
```

### Node.js (AWS SDK v3)

```javascript
import {
    S3Client,
    PutBucketPolicyCommand,
    GetBucketPolicyCommand,
    DeleteBucketPolicyCommand
} from "@aws-sdk/client-s3";

const s3Client = new S3Client({ region: "us-east-1" });

// Define policy
const policy = {
    Version: "2012-10-17",
    Statement: [
        {
            Sid: "PublicRead",
            Effect: "Allow",
            Principal: "*",
            Action: "s3:GetObject",
            Resource: "arn:aws:s3:::my-bucket/*"
        }
    ]
};

// Apply policy
async function putBucketPolicy(bucketName, policy) {
    const command = new PutBucketPolicyCommand({
        Bucket: bucketName,
        Policy: JSON.stringify(policy)
    });
    await s3Client.send(command);
    console.log("Policy applied successfully");
}

// Get policy
async function getBucketPolicy(bucketName) {
    const command = new GetBucketPolicyCommand({ Bucket: bucketName });
    const response = await s3Client.send(command);
    return JSON.parse(response.Policy);
}

// Delete policy
async function deleteBucketPolicy(bucketName) {
    const command = new DeleteBucketPolicyCommand({ Bucket: bucketName });
    await s3Client.send(command);
    console.log("Policy deleted");
}
```

---

## Bucket Policies vs IAM Policies

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    BUCKET POLICIES vs IAM POLICIES                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  BUCKET POLICY (Resource-based)      │  IAM POLICY (Identity-based)       │
│  ────────────────────────────────    │  ────────────────────────────────  │
│                                      │                                     │
│  • Attached to S3 bucket             │  • Attached to IAM user/role/group │
│  • Can grant cross-account access    │  • Cannot grant cross-account alone│
│  • Can make resources public         │  • Cannot make resources public    │
│  • Size limit: 20 KB                 │  • Size limit: 6 KB (inline)       │
│  • Principal element required        │  • No Principal (implicit)         │
│                                      │                                     │
│  Use when:                           │  Use when:                          │
│  • Cross-account access needed       │  • Controlling what users can do   │
│  • Public access required            │  • Managing permissions at scale   │
│  • VPC/IP restrictions               │  • Consistent permissions          │
│  • Service principal access          │  • User/role specific access       │
│                                      │                                     │
└────────────────────────────────────────────────────────────────────────────┘

EVALUATION: Both policies are evaluated together
            Access = IAM allows + Bucket Policy allows - Explicit Denies
```

### Combined Access Decision Flow

```
Request comes in
        │
        ▼
┌───────────────────┐
│ Check Explicit    │───▶ DENY found ───▶ ACCESS DENIED
│ Deny in any       │
│ policy            │
└─────────┬─────────┘
          │ No explicit deny
          ▼
┌───────────────────┐
│ Check IAM Policy  │
│ (if same account) │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Check Bucket      │
│ Policy            │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Any ALLOW found?  │───▶ No ───▶ ACCESS DENIED
└─────────┬─────────┘
          │ Yes
          ▼
    ACCESS ALLOWED
```

---

## Access Control Lists (ACLs)

### Overview

ACLs are a legacy access control mechanism. AWS now recommends using bucket policies and IAM policies instead.

```
⚠️ IMPORTANT: ACLs are being deprecated for new buckets

   As of April 2023, new buckets have ACLs disabled by default
   (S3 Object Ownership set to "Bucket owner enforced")

   Best Practice: Use bucket policies instead of ACLs
```

### ACL Types

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           S3 ACL GRANTEES                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  CANNED ACLs (Predefined)                                                  │
│  ─────────────────────────                                                 │
│  • private              - Owner gets FULL_CONTROL, no one else             │
│  • public-read          - Owner FULL_CONTROL, everyone READ                │
│  • public-read-write    - Owner FULL_CONTROL, everyone READ/WRITE          │
│  • authenticated-read   - Owner FULL_CONTROL, authenticated users READ     │
│  • bucket-owner-read    - Object owner FULL_CONTROL, bucket owner READ     │
│  • bucket-owner-full-control - Both owners get FULL_CONTROL                │
│                                                                            │
│  ACL PERMISSIONS                                                           │
│  ─────────────────                                                         │
│  • READ                 - List objects (bucket) / Read object (object)     │
│  • WRITE                - Create/delete objects (bucket only)              │
│  • READ_ACP             - Read ACL                                         │
│  • WRITE_ACP            - Write ACL                                        │
│  • FULL_CONTROL         - All of the above                                 │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### S3 Object Ownership Settings

```
1. Bucket owner enforced (Recommended - Default for new buckets)
   - ACLs are disabled
   - Bucket owner owns all objects
   - Access controlled by policies only

2. Bucket owner preferred
   - ACLs enabled
   - Objects uploaded with bucket-owner-full-control ACL are owned by bucket owner

3. Object writer (Legacy)
   - ACLs enabled
   - Object owner can be different from bucket owner
```

### Disable ACLs (Recommended)

```bash
# Set bucket owner enforced (disables ACLs)
aws s3api put-bucket-ownership-controls \
    --bucket my-bucket \
    --ownership-controls '{
        "Rules": [
            {
                "ObjectOwnership": "BucketOwnerEnforced"
            }
        ]
    }'
```

```python
import boto3

s3_client = boto3.client('s3')

# Disable ACLs
s3_client.put_bucket_ownership_controls(
    Bucket='my-bucket',
    OwnershipControls={
        'Rules': [
            {'ObjectOwnership': 'BucketOwnerEnforced'}
        ]
    }
)
```

---

## Block Public Access

### Overview

Block Public Access settings provide an additional layer of security to prevent unintended public access to S3 resources.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BLOCK PUBLIC ACCESS SETTINGS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Can be applied at:                                                         │
│  ┌──────────────────┐  ┌──────────────────┐                                 │
│  │  Account Level   │  │  Bucket Level    │                                 │
│  │  (All buckets)   │  │  (Single bucket) │                                 │
│  └──────────────────┘  └──────────────────┘                                 │
│                                                                             │
│  FOUR SETTINGS:                                                             │
│  ──────────────                                                             │
│  1. BlockPublicAcls                                                         │
│     Blocks PUT operations with public ACLs                                  │
│                                                                             │
│  2. IgnorePublicAcls                                                        │
│     Ignores all public ACLs (existing and new)                              │
│                                                                             │
│  3. BlockPublicPolicy                                                       │
│     Blocks PUT of bucket policies that grant public access                  │
│                                                                             │
│  4. RestrictPublicBuckets                                                   │
│     Restricts access to buckets with public policies                        │
│     to only AWS services and authorized users                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Settings Explained

| Setting | Effect |
|---------|--------|
| **BlockPublicAcls** | Prevents new public ACLs from being applied |
| **IgnorePublicAcls** | Ignores any existing public ACLs |
| **BlockPublicPolicy** | Rejects bucket policies that grant public access |
| **RestrictPublicBuckets** | Limits access to buckets with public policies |

### AWS CLI Commands

```bash
# Get current Block Public Access settings (bucket level)
aws s3api get-public-access-block --bucket my-bucket

# Put Block Public Access (block all)
aws s3api put-public-access-block \
    --bucket my-bucket \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Remove Block Public Access
aws s3api delete-public-access-block --bucket my-bucket

# Account-level settings
aws s3control put-public-access-block \
    --account-id 123456789012 \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Python (Boto3)

```python
import boto3

s3_client = boto3.client('s3')

# Block all public access
s3_client.put_public_access_block(
    Bucket='my-bucket',
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
)

# Get current settings
response = s3_client.get_public_access_block(Bucket='my-bucket')
print(response['PublicAccessBlockConfiguration'])

# Allow public access (for static website)
s3_client.put_public_access_block(
    Bucket='my-bucket',
    PublicAccessBlockConfiguration={
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': False,  # Allow public bucket policy
        'RestrictPublicBuckets': False
    }
)
```

### When to Allow Public Access

```
Use Case                              │ Block Settings
─────────────────────────────────────┼─────────────────────────────
Private bucket (default)              │ All TRUE
Static website (direct S3 access)     │ Policy settings FALSE
CloudFront origin (OAC)               │ All TRUE (use bucket policy)
Application uploads                   │ All TRUE (use presigned URLs)
```

---

## S3 Access Points

### Overview

Access Points are named network endpoints with dedicated access policies, simplifying data access management for shared datasets.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           S3 ACCESS POINTS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌────────────────────┐                               │
│                        │     S3 Bucket      │                               │
│                        │   (shared-data)    │                               │
│                        └─────────┬──────────┘                               │
│                                  │                                          │
│            ┌─────────────────────┼─────────────────────┐                    │
│            │                     │                     │                    │
│            ▼                     ▼                     ▼                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Access Point:   │  │ Access Point:   │  │ Access Point:   │              │
│  │ analytics-ap    │  │ finance-ap      │  │ marketing-ap    │              │
│  │                 │  │                 │  │                 │              │
│  │ Policy:         │  │ Policy:         │  │ Policy:         │              │
│  │ /analytics/*    │  │ /finance/*      │  │ /marketing/*    │              │
│  │ Read only       │  │ Read/Write      │  │ Read only       │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                       │
│           ▼                    ▼                    ▼                       │
│    Analytics Team        Finance Team         Marketing Team                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Benefits

1. **Simplified Permissions**: Each access point has its own policy
2. **Scalable**: Create hundreds of access points per bucket
3. **VPC Restrictions**: Restrict access to specific VPCs
4. **Separate Endpoints**: Unique hostnames for each access point

### Creating Access Points

```bash
# Create access point
aws s3control create-access-point \
    --account-id 123456789012 \
    --name finance-ap \
    --bucket my-shared-bucket

# Create VPC-restricted access point
aws s3control create-access-point \
    --account-id 123456789012 \
    --name internal-ap \
    --bucket my-shared-bucket \
    --vpc-configuration VpcId=vpc-1234567890abcdef0

# List access points
aws s3control list-access-points --account-id 123456789012

# Delete access point
aws s3control delete-access-point \
    --account-id 123456789012 \
    --name finance-ap
```

### Access Point Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "FinanceTeamAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:role/FinanceRole"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:us-east-1:123456789012:accesspoint/finance-ap/object/finance/*"
        }
    ]
}
```

### Using Access Points

```bash
# Access via access point ARN
aws s3api get-object \
    --bucket arn:aws:s3:us-east-1:123456789012:accesspoint/finance-ap \
    --key finance/report.pdf \
    ./report.pdf

# Access via access point alias
aws s3 cp s3://finance-ap-123456789012.s3-accesspoint.us-east-1.amazonaws.com/finance/report.pdf ./
```

### Python Example

```python
import boto3

s3_control = boto3.client('s3control')
s3_client = boto3.client('s3')

# Create access point
s3_control.create_access_point(
    AccountId='123456789012',
    Name='analytics-ap',
    Bucket='my-shared-bucket'
)

# Put access point policy
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AnalyticsAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:role/AnalyticsRole"
            },
            "Action": ["s3:GetObject"],
            "Resource": "arn:aws:s3:us-east-1:123456789012:accesspoint/analytics-ap/object/analytics/*"
        }
    ]
}

s3_control.put_access_point_policy(
    AccountId='123456789012',
    Name='analytics-ap',
    Policy=json.dumps(policy)
)

# Access objects through access point
response = s3_client.get_object(
    Bucket='arn:aws:s3:us-east-1:123456789012:accesspoint/analytics-ap',
    Key='analytics/data.csv'
)
```

---

## AWS Policy Generator

AWS provides a visual tool to generate bucket policies:

### Using the Policy Generator

1. Go to: https://awspolicygen.s3.amazonaws.com/policygen.html
2. Select **S3 Bucket Policy**
3. Configure:
   - Effect: Allow/Deny
   - Principal: Who
   - Actions: What operations
   - ARN: Which resources
4. Add conditions if needed
5. Generate and copy the policy

### Common Policy Templates

```bash
# Generate policy to allow CloudFront access
cat > cloudfront-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::BUCKET_NAME/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
                }
            }
        }
    ]
}
EOF
```

---

## Condition Keys Reference

### Common Condition Keys

| Key | Description | Example |
|-----|-------------|---------|
| `aws:SourceIp` | Requester's IP address | `"192.168.1.0/24"` |
| `aws:SourceVpc` | VPC ID | `"vpc-12345678"` |
| `aws:SourceVpce` | VPC Endpoint ID | `"vpce-12345678"` |
| `aws:SecureTransport` | HTTPS used | `"true"` |
| `aws:PrincipalArn` | ARN of principal | `"arn:aws:iam::*:role/Admin"` |
| `s3:x-amz-server-side-encryption` | Encryption type | `"aws:kms"` |
| `s3:x-amz-acl` | ACL requested | `"public-read"` |
| `s3:prefix` | Object prefix | `"finance/"` |
| `s3:max-keys` | Max keys in list | `"100"` |

### Condition Operators

| Operator | Use |
|----------|-----|
| `StringEquals` | Exact string match |
| `StringNotEquals` | String doesn't match |
| `StringLike` | Wildcard match (*,?) |
| `IpAddress` | IP in CIDR range |
| `NotIpAddress` | IP not in CIDR range |
| `Bool` | Boolean comparison |
| `Null` | Check if key exists |
| `DateGreaterThan` | Date comparison |

---

## Best Practices

### Security Best Practices

```
1. Enable Block Public Access by default
   - Only disable when specifically needed

2. Use bucket policies over ACLs
   - ACLs are legacy and being phased out

3. Require HTTPS
   - Add condition for aws:SecureTransport

4. Implement least privilege
   - Grant minimum required permissions

5. Use VPC endpoints for private access
   - Restrict bucket to VPC traffic only

6. Enable access logging
   - Track who accesses what

7. Use IAM roles, not access keys
   - Temporary credentials are more secure

8. Regular policy audits
   - Use IAM Access Analyzer
```

### Common Mistakes to Avoid

```
❌ Using "Principal": "*" without conditions
❌ Leaving BlockPublicPolicy disabled unnecessarily
❌ Overly permissive "Action": "s3:*"
❌ Not using Resource correctly (bucket vs objects)
❌ Forgetting both bucket and object ARNs when needed
❌ Using outdated policy version (use 2012-10-17)
```

---

## Summary

| Feature | Purpose | When to Use |
|---------|---------|-------------|
| **Bucket Policies** | Resource-based permissions | Cross-account, public access, conditions |
| **IAM Policies** | Identity-based permissions | Same-account user/role permissions |
| **Block Public Access** | Prevent public exposure | Always (disable selectively) |
| **ACLs** | Legacy access control | Avoid (use policies instead) |
| **Access Points** | Named endpoints with policies | Large shared datasets |

---

## Next Steps

Continue to [04-versioning-and-lifecycle.md](./04-versioning-and-lifecycle.md) to learn about versioning objects and automating data lifecycle management.
