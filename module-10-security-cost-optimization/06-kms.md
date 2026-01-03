# AWS Key Management Service (KMS)

## Introduction

AWS Key Management Service (KMS) is a managed service that makes it easy to create and control cryptographic keys used to encrypt your data. KMS integrates with most AWS services and provides a secure, centralized approach to key management.

---

## KMS Concepts

### Key Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    KMS KEY HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    AWS MANAGED KEYS                              │    │
│  │  ● Alias: aws/s3, aws/ebs, aws/rds, etc.                        │    │
│  │  ● Created automatically by AWS services                        │    │
│  │  ● Rotated every 3 years (cannot change)                        │    │
│  │  ● Cannot view or modify key policy                             │    │
│  │  ● Free (no monthly cost, only usage)                           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    CUSTOMER MANAGED KEYS (CMK)                   │    │
│  │  ● Created and managed by you                                   │    │
│  │  ● Full control over key policy                                 │    │
│  │  ● Can enable automatic rotation (annually)                     │    │
│  │  ● Can create aliases                                           │    │
│  │  ● Cost: $1/month + usage                                       │    │
│  │  ● Can be symmetric or asymmetric                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    IMPORTED KEY MATERIAL                         │    │
│  │  ● Bring your own key (BYOK)                                    │    │
│  │  ● You manage key material externally                           │    │
│  │  ● No automatic rotation (manual only)                          │    │
│  │  ● Can set expiration date                                      │    │
│  │  ● For compliance requirements                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    AWS OWNED KEYS                                │    │
│  │  ● Managed entirely by AWS                                      │    │
│  │  ● Used for some AWS services                                   │    │
│  │  ● Not visible in your account                                  │    │
│  │  ● Free                                                          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Types

| Type | Algorithm | Use Case |
|------|-----------|----------|
| **Symmetric** | AES-256-GCM | Most encryption needs, AWS service integration |
| **Asymmetric RSA** | RSA_2048/3072/4096 | Encryption, sign/verify |
| **Asymmetric ECC** | ECC_NIST/SECG curves | Sign/verify only |
| **HMAC** | HMAC_224/256/384/512 | Generate and verify MACs |

---

## Creating KMS Keys

### Via Console

1. Navigate to KMS console
2. Click "Create key"
3. Choose key type (Symmetric/Asymmetric)
4. Add alias and description
5. Define key administrators
6. Define key users
7. Review and create

### Via CLI

```bash
# Create a symmetric encryption key
aws kms create-key \
  --description "Production database encryption key" \
  --tags TagKey=Environment,TagValue=Production \
  --policy file://key-policy.json

# Create an alias
aws kms create-alias \
  --alias-name alias/production-db-key \
  --target-key-id <key-id>

# Enable key rotation
aws kms enable-key-rotation \
  --key-id <key-id>

# Create an asymmetric key
aws kms create-key \
  --description "Code signing key" \
  --key-spec RSA_2048 \
  --key-usage SIGN_VERIFY
```

### Via CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: KMS Keys for Production

Resources:
  # Symmetric encryption key
  DatabaseEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Encryption key for production database
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Id: key-policy
        Statement:
          # Allow root account full access
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'

          # Allow key administrators
          - Sid: Allow Key Administrators
            Effect: Allow
            Principal:
              AWS:
                - !Sub 'arn:aws:iam::${AWS::AccountId}:role/KeyAdminRole'
            Action:
              - 'kms:Create*'
              - 'kms:Describe*'
              - 'kms:Enable*'
              - 'kms:List*'
              - 'kms:Put*'
              - 'kms:Update*'
              - 'kms:Revoke*'
              - 'kms:Disable*'
              - 'kms:Get*'
              - 'kms:Delete*'
              - 'kms:ScheduleKeyDeletion'
              - 'kms:CancelKeyDeletion'
            Resource: '*'

          # Allow key usage
          - Sid: Allow Key Usage
            Effect: Allow
            Principal:
              AWS:
                - !Sub 'arn:aws:iam::${AWS::AccountId}:role/AppRole'
            Action:
              - 'kms:Encrypt'
              - 'kms:Decrypt'
              - 'kms:ReEncrypt*'
              - 'kms:GenerateDataKey*'
              - 'kms:DescribeKey'
            Resource: '*'

          # Allow AWS services
          - Sid: Allow AWS Services
            Effect: Allow
            Principal:
              Service:
                - rds.amazonaws.com
                - s3.amazonaws.com
            Action:
              - 'kms:Encrypt'
              - 'kms:Decrypt'
              - 'kms:ReEncrypt*'
              - 'kms:GenerateDataKey*'
              - 'kms:DescribeKey'
            Resource: '*'
            Condition:
              StringEquals:
                'kms:CallerAccount': !Ref AWS::AccountId
      Tags:
        - Key: Environment
          Value: Production

  DatabaseKeyAlias:
    Type: AWS::KMS::Alias
    Properties:
      AliasName: alias/production-db-key
      TargetKeyId: !Ref DatabaseEncryptionKey

  # Multi-region key
  GlobalEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Multi-region key for global encryption
      MultiRegion: true
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'

Outputs:
  DatabaseKeyArn:
    Value: !GetAtt DatabaseEncryptionKey.Arn
    Export:
      Name: DatabaseEncryptionKeyArn
```

### Via Terraform

```hcl
# Customer managed key
resource "aws_kms_key" "database" {
  description             = "Encryption key for production database"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  multi_region           = false

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Key Usage"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.app.arn
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Environment = "Production"
    Name        = "database-encryption-key"
  }
}

# Alias
resource "aws_kms_alias" "database" {
  name          = "alias/production-db-key"
  target_key_id = aws_kms_key.database.key_id
}

# Multi-region key
resource "aws_kms_key" "global" {
  description             = "Multi-region key for global encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  multi_region           = true
}

# Replica in another region
resource "aws_kms_replica_key" "global_replica" {
  provider = aws.us-west-2

  description             = "Multi-region replica key"
  primary_key_arn         = aws_kms_key.global.arn
  deletion_window_in_days = 30
}
```

---

## Key Policies

### Key Policy Structure

```json
{
  "Version": "2012-10-17",
  "Id": "key-policy-example",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow administration of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/KeyAdminRole"
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
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/AppRole"
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
}
```

### Cross-Account Access

```json
{
  "Sid": "Allow cross-account use",
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::999888777666:root"
  },
  "Action": [
    "kms:Encrypt",
    "kms:Decrypt",
    "kms:ReEncrypt*",
    "kms:GenerateDataKey*",
    "kms:DescribeKey"
  ],
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "kms:ViaService": "s3.us-east-1.amazonaws.com"
    }
  }
}
```

---

## Grants

Grants provide temporary, fine-grained permissions to use KMS keys.

### Creating a Grant

```bash
# Create a grant
aws kms create-grant \
  --key-id alias/production-db-key \
  --grantee-principal arn:aws:iam::123456789012:role/LambdaRole \
  --operations Decrypt GenerateDataKey \
  --retiring-principal arn:aws:iam::123456789012:role/AdminRole \
  --constraints EncryptionContextSubset={"Department":"Finance"}

# List grants
aws kms list-grants --key-id alias/production-db-key

# Retire a grant
aws kms retire-grant --grant-token <grant-token>

# Revoke a grant
aws kms revoke-grant \
  --key-id alias/production-db-key \
  --grant-id <grant-id>
```

### Grant Use Cases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GRANT USE CASES                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. TEMPORARY ACCESS                                                    │
│     Lambda function needs temporary access to decrypt secrets           │
│     ├── Create grant when Lambda is deployed                           │
│     └── Retire grant when Lambda is deleted                            │
│                                                                          │
│  2. DELEGATED ACCESS                                                    │
│     AWS service needs access on your behalf                            │
│     ├── EBS creates grant when creating encrypted volume               │
│     └── Allows EC2 to use key for volume decryption                    │
│                                                                          │
│  3. CROSS-ACCOUNT WORKFLOWS                                            │
│     Share encrypted data across accounts                                │
│     ├── Create grant for specific role in other account                │
│     └── Retire when access no longer needed                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Envelope Encryption

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ENVELOPE ENCRYPTION                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ENCRYPTION PROCESS:                                                    │
│                                                                          │
│  1. Generate Data Key                                                   │
│     ┌─────────────────────────────────────────────────────────────┐     │
│     │  Request: GenerateDataKey(KeyId)                            │     │
│     │                      │                                       │     │
│     │                      ▼                                       │     │
│     │  Response: Plaintext Data Key + Encrypted Data Key          │     │
│     └─────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  2. Encrypt Data                                                        │
│     ┌─────────────────────────────────────────────────────────────┐     │
│     │  Plaintext Data + Plaintext Data Key                        │     │
│     │                      │                                       │     │
│     │                      ▼  (Local encryption)                   │     │
│     │  Encrypted Data + Encrypted Data Key                        │     │
│     └─────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  3. Store (discard plaintext data key)                                 │
│     ┌─────────────────────────────────────────────────────────────┐     │
│     │  Store Together:                                            │     │
│     │  [Encrypted Data Key] + [Encrypted Data]                    │     │
│     └─────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  DECRYPTION PROCESS:                                                    │
│                                                                          │
│  1. Retrieve encrypted data key and data                               │
│  2. Decrypt data key using KMS                                         │
│  3. Decrypt data locally using plaintext data key                      │
│  4. Discard plaintext data key                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Envelope Encryption Example (Python)

```python
import boto3
from cryptography.fernet import Fernet
import base64

def encrypt_data(plaintext, key_id):
    """
    Encrypt data using envelope encryption
    """
    kms = boto3.client('kms')

    # Generate data key
    response = kms.generate_data_key(
        KeyId=key_id,
        KeySpec='AES_256'
    )

    # Get plaintext and encrypted data key
    plaintext_key = response['Plaintext']
    encrypted_key = response['CiphertextBlob']

    # Encrypt data locally using the plaintext key
    # (Using Fernet for simplicity - production would use AES-GCM)
    fernet_key = base64.urlsafe_b64encode(plaintext_key)
    fernet = Fernet(fernet_key)
    encrypted_data = fernet.encrypt(plaintext.encode())

    # Clear plaintext key from memory
    del plaintext_key
    del fernet_key

    # Return encrypted key and data
    return {
        'encrypted_key': base64.b64encode(encrypted_key).decode(),
        'encrypted_data': encrypted_data.decode()
    }

def decrypt_data(encrypted_key_b64, encrypted_data, key_id):
    """
    Decrypt data using envelope encryption
    """
    kms = boto3.client('kms')

    # Decode the encrypted key
    encrypted_key = base64.b64decode(encrypted_key_b64)

    # Decrypt the data key using KMS
    response = kms.decrypt(
        KeyId=key_id,
        CiphertextBlob=encrypted_key
    )

    plaintext_key = response['Plaintext']

    # Decrypt data locally
    fernet_key = base64.urlsafe_b64encode(plaintext_key)
    fernet = Fernet(fernet_key)
    decrypted_data = fernet.decrypt(encrypted_data.encode())

    # Clear plaintext key from memory
    del plaintext_key
    del fernet_key

    return decrypted_data.decode()

# Usage
key_id = 'alias/my-key'
sensitive_data = 'This is my secret data'

# Encrypt
result = encrypt_data(sensitive_data, key_id)
print(f"Encrypted Key: {result['encrypted_key'][:50]}...")
print(f"Encrypted Data: {result['encrypted_data'][:50]}...")

# Decrypt
decrypted = decrypt_data(result['encrypted_key'], result['encrypted_data'], key_id)
print(f"Decrypted: {decrypted}")
```

### Data Key Caching

```python
from aws_encryption_sdk import CommitmentPolicy
from aws_encryption_sdk.caches.local import LocalCryptoMaterialsCache
from aws_encryption_sdk.key_providers.kms import KMSMasterKeyProvider
import aws_encryption_sdk

# Create a master key provider
key_provider = KMSMasterKeyProvider(key_ids=['alias/my-key'])

# Create a local cache (reduces KMS API calls)
cache = LocalCryptoMaterialsCache(capacity=100)

# Create a caching CMM (Cryptographic Materials Manager)
caching_cmm = aws_encryption_sdk.CachingCryptoMaterialsManager(
    master_key_provider=key_provider,
    cache=cache,
    max_age=600.0,  # 10 minutes
    max_messages_encrypted=1000
)

# Encrypt with caching
client = aws_encryption_sdk.EncryptionSDKClient(
    commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
)

ciphertext, _ = client.encrypt(
    source=b'my sensitive data',
    materials_manager=caching_cmm
)
```

---

## Key Rotation

### Automatic Rotation

```bash
# Enable automatic rotation (annual)
aws kms enable-key-rotation --key-id alias/my-key

# Check rotation status
aws kms get-key-rotation-status --key-id alias/my-key

# Disable rotation
aws kms disable-key-rotation --key-id alias/my-key
```

### How Rotation Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    KEY ROTATION                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AUTOMATIC ROTATION (Customer Managed Keys):                            │
│                                                                          │
│  Year 1:  Key ID: abc123                                                │
│           └── Backing Key v1 (active)                                   │
│                                                                          │
│  Year 2:  Key ID: abc123 (same!)                                        │
│           ├── Backing Key v1 (for decryption)                          │
│           └── Backing Key v2 (active, for encryption)                  │
│                                                                          │
│  Year 3:  Key ID: abc123 (same!)                                        │
│           ├── Backing Key v1 (for decryption)                          │
│           ├── Backing Key v2 (for decryption)                          │
│           └── Backing Key v3 (active, for encryption)                  │
│                                                                          │
│  KEY BENEFITS:                                                          │
│  ● No code changes needed                                               │
│  ● Old data still decryptable                                          │
│  ● Same key ID, alias, ARN                                             │
│  ● Transparent to applications                                         │
│                                                                          │
│  LIMITATIONS:                                                           │
│  ● Only symmetric keys                                                  │
│  ● Only AWS-generated key material                                     │
│  ● Fixed annual schedule (365 days)                                    │
│  ● Cannot manually trigger                                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Manual Key Rotation

For more control or asymmetric keys:

```bash
# Create new key
aws kms create-key --description "New production key v2"

# Update alias to point to new key
aws kms update-alias \
  --alias-name alias/production-key \
  --target-key-id <new-key-id>

# Keep old key for decryption (don't delete immediately)
# Re-encrypt data with new key as needed
```

---

## Multi-Region Keys

### Creating Multi-Region Keys

```bash
# Create primary key
aws kms create-key \
  --multi-region \
  --description "Multi-region key for global encryption" \
  --region us-east-1

# Create replica in another region
aws kms replicate-key \
  --key-id mrk-1234abcd \
  --replica-region us-west-2 \
  --region us-east-1
```

### Multi-Region Key Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MULTI-REGION KEY ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐        ┌──────────────────────┐               │
│  │     US-EAST-1        │        │     US-WEST-2        │               │
│  │                      │        │                      │               │
│  │  mrk-1234abcd        │        │  mrk-1234abcd        │               │
│  │  (Primary)           │◄──────►│  (Replica)           │               │
│  │                      │        │                      │               │
│  │  Key Material: xxx   │  Same  │  Key Material: xxx   │               │
│  │  Key ID: mrk-*       │  Key   │  Key ID: mrk-*       │               │
│  │                      │        │                      │               │
│  └──────────────────────┘        └──────────────────────┘               │
│                                                                          │
│  USE CASES:                                                             │
│  ● Disaster recovery (decrypt in backup region)                        │
│  ● Global applications (local encryption/decryption)                   │
│  ● Low latency (use nearest replica)                                   │
│  ● Compliance (data locality requirements)                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Using KMS with AWS Services

### S3 Encryption

```bash
# Enable default encryption with KMS
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/my-key"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

### EBS Encryption

```bash
# Create encrypted volume
aws ec2 create-volume \
  --availability-zone us-east-1a \
  --size 100 \
  --encrypted \
  --kms-key-id alias/my-key

# Set default encryption for account
aws ec2 enable-ebs-encryption-by-default
aws ec2 modify-ebs-default-kms-key-id --kms-key-id alias/my-key
```

### RDS Encryption

```bash
# Create encrypted RDS instance
aws rds create-db-instance \
  --db-instance-identifier my-database \
  --db-instance-class db.m5.large \
  --engine mysql \
  --storage-encrypted \
  --kms-key-id alias/my-key \
  # ... other parameters
```

### Lambda Environment Variables

```yaml
# CloudFormation
MyFunction:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: my-function
    KmsKeyArn: !GetAtt MyKey.Arn
    Environment:
      Variables:
        SECRET_KEY: encrypted-value
```

---

## Best Practices

### Key Management

1. **Use customer managed keys** for sensitive workloads
2. **Enable key rotation** for symmetric keys
3. **Use separate keys** for different environments/applications
4. **Implement least privilege** in key policies
5. **Monitor key usage** with CloudTrail

### Security

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    KMS SECURITY BEST PRACTICES                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. KEY POLICY SECURITY                                                 │
│     ├── Always include root account for recovery                       │
│     ├── Separate admin and usage permissions                           │
│     ├── Use conditions for context restrictions                        │
│     └── Avoid wildcard principals                                      │
│                                                                          │
│  2. ACCESS CONTROL                                                      │
│     ├── Use IAM policies with key policies                             │
│     ├── Implement resource-based controls                              │
│     ├── Use grants for temporary access                                │
│     └── Regularly audit key access                                     │
│                                                                          │
│  3. KEY LIFECYCLE                                                       │
│     ├── Enable automatic rotation                                      │
│     ├── Set appropriate deletion window (7-30 days)                    │
│     ├── Tag keys for organization                                      │
│     └── Document key purposes                                          │
│                                                                          │
│  4. MONITORING                                                          │
│     ├── Enable CloudTrail for KMS API calls                            │
│     ├── Set up CloudWatch alarms for suspicious activity               │
│     ├── Monitor key usage patterns                                     │
│     └── Alert on key deletion attempts                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### CloudWatch Alarms

```yaml
# Alert on key deletion
KeyDeletionAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: KMS-KeyDeletionScheduled
    MetricName: KeyDeletionScheduled
    Namespace: AWS/KMS
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 0
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SecurityAlarmTopic
```

---

## Cost Optimization

### KMS Pricing

| Item | Cost |
|------|------|
| Customer managed key | $1/month |
| AWS managed key | Free |
| API requests (first 20,000/month) | Free |
| API requests (after) | $0.03 per 10,000 |
| Asymmetric key operations | Higher than symmetric |

### Cost Reduction Strategies

1. **Use S3 Bucket Keys** - Reduces KMS API calls by up to 99%
2. **Implement data key caching** - Reduce GenerateDataKey calls
3. **Consolidate keys** - Don't create unnecessary keys
4. **Use AWS managed keys** - When you don't need key policy control

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| AccessDeniedException | Missing permissions | Check key policy and IAM |
| KMSInvalidStateException | Key disabled/pending deletion | Check key state |
| InvalidCiphertextException | Wrong key or corrupted data | Verify key ID and data |
| DependencyTimeoutException | KMS throttling | Implement caching, retry |

### Debugging Commands

```bash
# Check key details
aws kms describe-key --key-id alias/my-key

# Get key policy
aws kms get-key-policy --key-id alias/my-key --policy-name default

# List grants
aws kms list-grants --key-id alias/my-key

# View CloudTrail events
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventSource,AttributeValue=kms.amazonaws.com
```

---

## Key Takeaways

1. **Use customer managed keys** for sensitive data
2. **Enable key rotation** for symmetric keys
3. **Implement envelope encryption** for large data
4. **Use grants** for temporary access
5. **Monitor with CloudTrail** for audit and security
6. **Consider multi-region** for global applications
7. **Optimize costs** with bucket keys and caching

---

## Next Steps

Continue to [07-secrets-manager.md](07-secrets-manager.md) to learn about secure secrets storage and rotation.
