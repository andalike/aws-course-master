# 05 - S3 Security

## Introduction

Security in Amazon S3 involves multiple layers: access control, encryption, auditing, and network security. This module covers encryption options, security best practices, and advanced access control mechanisms.

---

## Security Layers Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          S3 SECURITY LAYERS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: IDENTITY & ACCESS                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • IAM Policies         • Bucket Policies      • Access Points       │    │
│  │ • Block Public Access  • ACLs (Legacy)        • Pre-signed URLs     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Layer 2: ENCRYPTION                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • Server-Side Encryption (SSE-S3, SSE-KMS, SSE-C)                   │    │
│  │ • Client-Side Encryption                                            │    │
│  │ • Encryption in Transit (HTTPS/TLS)                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Layer 3: NETWORK SECURITY                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • VPC Endpoints (Gateway & Interface)                               │    │
│  │ • VPC Endpoint Policies                                             │    │
│  │ • IP-based restrictions                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Layer 4: MONITORING & AUDITING                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • S3 Access Logs          • CloudTrail           • S3 Inventory     │    │
│  │ • CloudWatch Metrics      • IAM Access Analyzer  • Macie            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Encryption Overview

### Encryption Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        S3 ENCRYPTION OPTIONS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SERVER-SIDE ENCRYPTION (Data at Rest)                                      │
│  ─────────────────────────────────────                                      │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │    SSE-S3       │  │    SSE-KMS      │  │    SSE-C        │              │
│  │                 │  │                 │  │                 │              │
│  │ AWS managed     │  │ KMS managed     │  │ Customer        │              │
│  │ keys            │  │ keys            │  │ provided keys   │              │
│  │                 │  │                 │  │                 │              │
│  │ AES-256         │  │ CMK in KMS      │  │ You manage      │              │
│  │ No extra cost   │  │ Audit trail     │  │ keys completely │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                             │
│  CLIENT-SIDE ENCRYPTION                                                     │
│  ─────────────────────                                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Encrypt data before sending to S3                                   │    │
│  │ You manage encryption/decryption and keys                           │    │
│  │ S3 receives and stores already-encrypted data                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ENCRYPTION IN TRANSIT                                                      │
│  ────────────────────                                                       │
│  HTTPS/TLS for all API calls and data transfer                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## SSE-S3 (Server-Side Encryption with S3-Managed Keys)

### Overview

SSE-S3 uses AES-256 encryption with keys managed entirely by AWS. This is the simplest and default encryption option.

```
How SSE-S3 Works:
────────────────────────────────────────────────────────────────────────────

Client                              S3                          AWS
  │                                  │                            │
  │  PUT object                      │                            │
  │  x-amz-server-side-encryption:   │                            │
  │  AES256                          │                            │
  ├─────────────────────────────────▶│                            │
  │                                  │  Request data key          │
  │                                  ├───────────────────────────▶│
  │                                  │                            │
  │                                  │  Data key                  │
  │                                  │◀───────────────────────────┤
  │                                  │                            │
  │                                  │  Encrypt object            │
  │                                  │  with data key             │
  │                                  │                            │
  │                                  │  Store encrypted object    │
  │                                  │                            │
  │  200 OK                          │                            │
  │◀─────────────────────────────────┤                            │
  │                                  │                            │
```

### Enabling SSE-S3

#### AWS CLI

```bash
# Upload with SSE-S3 encryption
aws s3 cp myfile.txt s3://my-bucket/ --sse AES256

# Set default encryption for bucket
aws s3api put-bucket-encryption \
    --bucket my-bucket \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                },
                "BucketKeyEnabled": false
            }
        ]
    }'

# Check bucket encryption settings
aws s3api get-bucket-encryption --bucket my-bucket
```

#### Python (Boto3)

```python
import boto3

s3_client = boto3.client('s3')

# Upload with SSE-S3
s3_client.put_object(
    Bucket='my-bucket',
    Key='encrypted-file.txt',
    Body=b'Sensitive data',
    ServerSideEncryption='AES256'
)

# Set default encryption
s3_client.put_bucket_encryption(
    Bucket='my-bucket',
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            }
        ]
    }
)

# Verify object encryption
response = s3_client.head_object(Bucket='my-bucket', Key='encrypted-file.txt')
print(f"Encryption: {response.get('ServerSideEncryption')}")
```

---

## SSE-KMS (Server-Side Encryption with KMS Keys)

### Overview

SSE-KMS uses AWS Key Management Service (KMS) for key management, providing additional features like audit trails and key rotation.

```
How SSE-KMS Works:
────────────────────────────────────────────────────────────────────────────

Client                              S3                          KMS
  │                                  │                            │
  │  PUT object                      │                            │
  │  x-amz-server-side-encryption:   │                            │
  │  aws:kms                         │                            │
  │  x-amz-server-side-encryption-   │                            │
  │  aws-kms-key-id: key-id          │                            │
  ├─────────────────────────────────▶│                            │
  │                                  │  GenerateDataKey           │
  │                                  │  (with CMK)                │
  │                                  ├───────────────────────────▶│
  │                                  │                            │
  │                                  │  Plaintext key +           │
  │                                  │  Encrypted key             │
  │                                  │◀───────────────────────────┤
  │                                  │                            │
  │                                  │  Encrypt object with       │
  │                                  │  plaintext key             │
  │                                  │                            │
  │                                  │  Store encrypted object +  │
  │                                  │  encrypted data key        │
  │                                  │                            │
  │  200 OK                          │                            │
  │◀─────────────────────────────────┤                            │
  │                                  │                            │
```

### Benefits of SSE-KMS

| Feature | Benefit |
|---------|---------|
| **CloudTrail Integration** | Audit trail of key usage |
| **Key Rotation** | Automatic annual rotation option |
| **Key Policies** | Fine-grained key access control |
| **Separation of Duties** | Different permissions for data vs keys |
| **DSSE-KMS** | Dual-layer server-side encryption option |

### Creating and Using KMS Keys

```bash
# Create a KMS key
aws kms create-key \
    --description "S3 encryption key" \
    --key-usage ENCRYPT_DECRYPT

# Create an alias for easier reference
aws kms create-alias \
    --alias-name alias/s3-encryption-key \
    --target-key-id <key-id>

# Upload with SSE-KMS
aws s3 cp myfile.txt s3://my-bucket/ \
    --sse aws:kms \
    --sse-kms-key-id alias/s3-encryption-key

# Set bucket default encryption with KMS
aws s3api put-bucket-encryption \
    --bucket my-bucket \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms",
                    "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
                },
                "BucketKeyEnabled": true
            }
        ]
    }'
```

### Python (Boto3)

```python
import boto3

s3_client = boto3.client('s3')
kms_client = boto3.client('kms')

# Create KMS key
key_response = kms_client.create_key(
    Description='S3 encryption key',
    KeyUsage='ENCRYPT_DECRYPT'
)
key_id = key_response['KeyMetadata']['KeyId']

# Create alias
kms_client.create_alias(
    AliasName='alias/s3-encryption-key',
    TargetKeyId=key_id
)

# Upload with SSE-KMS
s3_client.put_object(
    Bucket='my-bucket',
    Key='kms-encrypted-file.txt',
    Body=b'Sensitive data',
    ServerSideEncryption='aws:kms',
    SSEKMSKeyId=key_id
)

# Set bucket default encryption with KMS and Bucket Key
s3_client.put_bucket_encryption(
    Bucket='my-bucket',
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'aws:kms',
                    'KMSMasterKeyID': key_id
                },
                'BucketKeyEnabled': True  # Reduces KMS costs
            }
        ]
    }
)
```

### S3 Bucket Keys

S3 Bucket Keys reduce KMS costs by reducing the number of KMS API calls.

```
Without Bucket Key:
──────────────────────────────────────────────────────────────────────────
Each object requires a KMS API call to generate a unique data key
1000 objects = 1000 KMS API calls = $0.003 (at $0.03 per 10,000 requests)

With Bucket Key:
──────────────────────────────────────────────────────────────────────────
One bucket-level key is used to derive keys for multiple objects
1000 objects = ~1 KMS API call = $0.000003

Cost Savings: Up to 99%
```

```bash
# Enable Bucket Key
aws s3api put-bucket-encryption \
    --bucket my-bucket \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms",
                    "KMSMasterKeyID": "alias/s3-encryption-key"
                },
                "BucketKeyEnabled": true
            }
        ]
    }'
```

---

## SSE-C (Server-Side Encryption with Customer-Provided Keys)

### Overview

With SSE-C, you manage the encryption keys, but S3 performs the encryption and decryption.

```
SSE-C Requirements:
────────────────────────────────────────────────────────────────────────────

1. HTTPS is REQUIRED (keys sent in headers)
2. You must provide the same key for decryption
3. S3 does NOT store your key
4. Key must be 256-bit AES key

Request Headers:
• x-amz-server-side-encryption-customer-algorithm: AES256
• x-amz-server-side-encryption-customer-key: Base64-encoded key
• x-amz-server-side-encryption-customer-key-MD5: Base64-encoded MD5
```

### Using SSE-C

```bash
# Generate a 256-bit key
ENCRYPTION_KEY=$(openssl rand -base64 32)
KEY_MD5=$(echo -n "$ENCRYPTION_KEY" | base64 -d | openssl md5 -binary | base64)

# Upload with SSE-C
aws s3api put-object \
    --bucket my-bucket \
    --key sse-c-file.txt \
    --body myfile.txt \
    --sse-customer-algorithm AES256 \
    --sse-customer-key "$ENCRYPTION_KEY" \
    --sse-customer-key-md5 "$KEY_MD5"

# Download with SSE-C (must use same key)
aws s3api get-object \
    --bucket my-bucket \
    --key sse-c-file.txt \
    --sse-customer-algorithm AES256 \
    --sse-customer-key "$ENCRYPTION_KEY" \
    --sse-customer-key-md5 "$KEY_MD5" \
    ./downloaded-file.txt
```

### Python (Boto3)

```python
import boto3
import base64
import hashlib
import os

s3_client = boto3.client('s3')

# Generate a 256-bit key
encryption_key = os.urandom(32)
encryption_key_b64 = base64.b64encode(encryption_key).decode('utf-8')
key_md5 = base64.b64encode(hashlib.md5(encryption_key).digest()).decode('utf-8')

# Upload with SSE-C
s3_client.put_object(
    Bucket='my-bucket',
    Key='sse-c-file.txt',
    Body=b'Sensitive data',
    SSECustomerAlgorithm='AES256',
    SSECustomerKey=encryption_key_b64,
    SSECustomerKeyMD5=key_md5
)

# Download with SSE-C
response = s3_client.get_object(
    Bucket='my-bucket',
    Key='sse-c-file.txt',
    SSECustomerAlgorithm='AES256',
    SSECustomerKey=encryption_key_b64,
    SSECustomerKeyMD5=key_md5
)

data = response['Body'].read()
print(f"Decrypted data: {data}")

# IMPORTANT: Store the key securely - you cannot retrieve data without it!
```

### SSE-C Considerations

```
Advantages:
✓ Full control over encryption keys
✓ Keys never stored by AWS
✓ No additional KMS costs

Disadvantages:
✗ Key management is your responsibility
✗ Lost key = Lost data (unrecoverable)
✗ Must use HTTPS
✗ Cannot use with S3 features that require AWS access to data
  (e.g., some replication scenarios)
```

---

## Client-Side Encryption

### Overview

With client-side encryption, you encrypt data before sending it to S3. S3 stores the already-encrypted data.

```
Client-Side Encryption Flow:
────────────────────────────────────────────────────────────────────────────

┌────────┐          ┌───────────────┐          ┌──────────────┐
│ Client │          │  Encrypt      │          │    S3        │
│        │          │  Library      │          │              │
└────┬───┘          └───────┬───────┘          └──────┬───────┘
     │                      │                         │
     │  Plaintext data      │                         │
     ├─────────────────────▶│                         │
     │                      │                         │
     │  Generate data key   │                         │
     │  (from master key)   │                         │
     │                      │                         │
     │  Encrypted data +    │                         │
     │  encrypted data key  │                         │
     │◀─────────────────────┤                         │
     │                      │                         │
     │  PUT encrypted object                          │
     ├───────────────────────────────────────────────▶│
     │                                                │
     │  200 OK                                        │
     │◀───────────────────────────────────────────────┤
     │                                                │
```

### AWS Encryption SDK Example (Python)

```python
# Install: pip install aws-encryption-sdk boto3

import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy
import boto3

# Create a KMS master key provider
kms_key_arn = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
master_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(
    key_ids=[kms_key_arn]
)

# Create encryption client
client = aws_encryption_sdk.EncryptionSDKClient(
    commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
)

# Encrypt data
plaintext = b"Sensitive data to encrypt"
ciphertext, encryptor_header = client.encrypt(
    source=plaintext,
    key_provider=master_key_provider
)

# Upload encrypted data to S3
s3_client = boto3.client('s3')
s3_client.put_object(
    Bucket='my-bucket',
    Key='client-encrypted-file.bin',
    Body=ciphertext
)

# Download and decrypt
response = s3_client.get_object(
    Bucket='my-bucket',
    Key='client-encrypted-file.bin'
)
downloaded_ciphertext = response['Body'].read()

decrypted, decryptor_header = client.decrypt(
    source=downloaded_ciphertext,
    key_provider=master_key_provider
)
print(f"Decrypted: {decrypted}")
```

---

## Encryption Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ENCRYPTION COMPARISON MATRIX                           │
├─────────────┬──────────────┬──────────────┬──────────────┬─────────────────┤
│ Feature     │ SSE-S3       │ SSE-KMS      │ SSE-C        │ Client-Side     │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ Key Mgmt    │ AWS          │ AWS KMS      │ Customer     │ Customer        │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ Encryption  │ S3           │ S3           │ S3           │ Client          │
│ Performed   │              │              │              │                 │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ Audit Trail │ No           │ Yes          │ No           │ Depends         │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ Key Rotation│ Automatic    │ Configurable │ Manual       │ Manual          │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ Extra Cost  │ No           │ KMS fees     │ No           │ Maybe KMS       │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ HTTPS Req'd │ No           │ No           │ Yes          │ Recommended     │
├─────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ Compliance  │ Basic        │ High         │ High         │ Highest         │
└─────────────┴──────────────┴──────────────┴──────────────┴─────────────────┘

Choose:
• SSE-S3: Simple encryption with minimal management
• SSE-KMS: Audit requirements, key control, regulatory compliance
• SSE-C: Full key control, no key storage in AWS
• Client-Side: Maximum security, data encrypted before leaving your environment
```

---

## Enforcing Encryption

### Bucket Policy to Require Encryption

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyUnencryptedObjectUploads",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "Null": {
                    "s3:x-amz-server-side-encryption": "true"
                }
            }
        }
    ]
}
```

### Require Specific Encryption Type

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyNonKMSEncryption",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "aws:kms"
                }
            }
        },
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
        }
    ]
}
```

### Require Specific KMS Key

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RequireSpecificKMSKey",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
                }
            }
        }
    ]
}
```

---

## Encryption in Transit (HTTPS/TLS)

### Enforcing HTTPS

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyHTTP",
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

### TLS Version Requirements

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RequireTLS12",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ],
            "Condition": {
                "NumericLessThan": {
                    "s3:TlsVersion": "1.2"
                }
            }
        }
    ]
}
```

---

## VPC Endpoints

### Gateway Endpoint (Free)

Gateway endpoints provide private connectivity to S3 without traversing the internet.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VPC GATEWAY ENDPOINT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                              VPC                                      │  │
│  │                                                                       │  │
│  │  ┌─────────────┐     ┌─────────────────┐     ┌────────────────────┐   │  │
│  │  │  Private    │────▶│ Gateway Endpoint│────▶│    S3 Service      │   │  │
│  │  │  Subnet     │     │    (Free)       │     │                    │   │  │
│  │  │  (EC2)      │     │                 │     │  my-bucket         │   │  │
│  │  └─────────────┘     └─────────────────┘     └────────────────────┘   │  │
│  │                                                                       │  │
│  │  Route Table: pl-xxxxxxxx → vpce-xxxxxxxx                            │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Traffic stays within AWS network - no internet traversal                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

```bash
# Create gateway endpoint
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345678 \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids rtb-12345678

# List endpoints
aws ec2 describe-vpc-endpoints \
    --filters "Name=service-name,Values=com.amazonaws.us-east-1.s3"
```

### VPC Endpoint Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAccessToSpecificBucket",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::my-approved-bucket/*"
        },
        {
            "Sid": "AllowListBucket",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::my-approved-bucket"
        }
    ]
}
```

### Bucket Policy Restricting to VPC Endpoint

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyNonVPCEndpoint",
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

---

## Access Points for Security

### Creating Secure Access Points

```bash
# Create VPC-only access point
aws s3control create-access-point \
    --account-id 123456789012 \
    --name secure-access-point \
    --bucket my-bucket \
    --vpc-configuration VpcId=vpc-12345678

# Apply access point policy
aws s3control put-access-point-policy \
    --account-id 123456789012 \
    --name secure-access-point \
    --policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "RestrictToVPC",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::123456789012:role/ApplicationRole"
                },
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": "arn:aws:s3:us-east-1:123456789012:accesspoint/secure-access-point/object/*"
            }
        ]
    }'
```

---

## Monitoring and Auditing

### S3 Server Access Logging

```bash
# Enable access logging
aws s3api put-bucket-logging \
    --bucket source-bucket \
    --bucket-logging-status '{
        "LoggingEnabled": {
            "TargetBucket": "logging-bucket",
            "TargetPrefix": "s3-access-logs/source-bucket/"
        }
    }'
```

### CloudTrail for S3

```bash
# Create trail for S3 data events
aws cloudtrail create-trail \
    --name s3-data-events-trail \
    --s3-bucket-name cloudtrail-logs-bucket

# Enable S3 data events
aws cloudtrail put-event-selectors \
    --trail-name s3-data-events-trail \
    --event-selectors '[
        {
            "ReadWriteType": "All",
            "IncludeManagementEvents": true,
            "DataResources": [
                {
                    "Type": "AWS::S3::Object",
                    "Values": ["arn:aws:s3:::my-bucket/"]
                }
            ]
        }
    ]'
```

### IAM Access Analyzer

```bash
# Create analyzer
aws accessanalyzer create-analyzer \
    --analyzer-name s3-analyzer \
    --type ACCOUNT

# List findings
aws accessanalyzer list-findings \
    --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/s3-analyzer
```

### Python: Security Audit Script

```python
import boto3
import json

def audit_bucket_security(bucket_name):
    """Audit security settings for an S3 bucket."""
    s3_client = boto3.client('s3')
    findings = []

    # Check encryption
    try:
        encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
        findings.append(f"[PASS] Encryption enabled: {encryption['ServerSideEncryptionConfiguration']}")
    except s3_client.exceptions.ClientError:
        findings.append("[FAIL] Default encryption not enabled")

    # Check public access block
    try:
        pab = s3_client.get_public_access_block(Bucket=bucket_name)
        config = pab['PublicAccessBlockConfiguration']
        if all([config['BlockPublicAcls'], config['IgnorePublicAcls'],
                config['BlockPublicPolicy'], config['RestrictPublicBuckets']]):
            findings.append("[PASS] All public access blocked")
        else:
            findings.append(f"[WARN] Public access block not fully enabled: {config}")
    except s3_client.exceptions.ClientError:
        findings.append("[FAIL] Public access block not configured")

    # Check versioning
    try:
        versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
        if versioning.get('Status') == 'Enabled':
            findings.append("[PASS] Versioning enabled")
        else:
            findings.append("[WARN] Versioning not enabled")
    except Exception as e:
        findings.append(f"[ERROR] Could not check versioning: {e}")

    # Check logging
    try:
        logging = s3_client.get_bucket_logging(Bucket=bucket_name)
        if 'LoggingEnabled' in logging:
            findings.append("[PASS] Access logging enabled")
        else:
            findings.append("[WARN] Access logging not enabled")
    except Exception as e:
        findings.append(f"[ERROR] Could not check logging: {e}")

    # Check bucket policy
    try:
        policy = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy_doc = json.loads(policy['Policy'])
        for statement in policy_doc.get('Statement', []):
            if statement.get('Effect') == 'Allow' and statement.get('Principal') == '*':
                if 'Condition' not in statement:
                    findings.append("[WARN] Bucket policy allows public access without conditions")
                    break
        else:
            findings.append("[PASS] Bucket policy does not allow unrestricted public access")
    except s3_client.exceptions.NoSuchBucketPolicy:
        findings.append("[INFO] No bucket policy configured")

    return findings

# Usage
bucket = 'my-bucket'
results = audit_bucket_security(bucket)
for finding in results:
    print(finding)
```

---

## Security Best Practices Checklist

```
ACCESS CONTROL
─────────────────────────────────────────────────────────────────────────────
□ Enable Block Public Access at account level
□ Use bucket policies instead of ACLs
□ Implement least privilege access
□ Use IAM roles instead of access keys
□ Review permissions regularly with IAM Access Analyzer

ENCRYPTION
─────────────────────────────────────────────────────────────────────────────
□ Enable default encryption (SSE-S3 minimum)
□ Use SSE-KMS for sensitive data (audit trail)
□ Enforce encryption via bucket policy
□ Require HTTPS for all access
□ Enable S3 Bucket Keys for KMS cost optimization

NETWORK SECURITY
─────────────────────────────────────────────────────────────────────────────
□ Use VPC endpoints for private access
□ Restrict access by IP/VPC when possible
□ Consider S3 Access Points for large-scale access management

MONITORING
─────────────────────────────────────────────────────────────────────────────
□ Enable S3 access logging
□ Enable CloudTrail data events for sensitive buckets
□ Set up CloudWatch alarms for unusual access patterns
□ Use Amazon Macie for sensitive data discovery
□ Regular security audits

DATA PROTECTION
─────────────────────────────────────────────────────────────────────────────
□ Enable versioning for critical buckets
□ Consider MFA Delete for highly sensitive data
□ Implement lifecycle policies for data retention
□ Test backup and recovery procedures
□ Enable Cross-Region Replication for disaster recovery
```

---

## Summary

| Security Feature | Purpose | Recommended Setting |
|-----------------|---------|-------------------|
| **Block Public Access** | Prevent unintended public exposure | Enable all settings |
| **Default Encryption** | Encrypt all objects at rest | SSE-S3 or SSE-KMS |
| **HTTPS Enforcement** | Encrypt data in transit | Require via bucket policy |
| **VPC Endpoints** | Private network access | Use for internal workloads |
| **Access Logging** | Audit trail of access | Enable for all buckets |
| **CloudTrail** | API call logging | Enable for sensitive buckets |
| **Versioning** | Protect against deletes | Enable for critical data |

---

## Next Steps

Continue to [06-static-website-hosting.md](./06-static-website-hosting.md) to learn how to host static websites on S3.
