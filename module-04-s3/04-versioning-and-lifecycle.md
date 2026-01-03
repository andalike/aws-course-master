# 04 - Versioning and Lifecycle Management

## Introduction

S3 Versioning and Lifecycle policies are powerful features for data protection and cost optimization. Versioning preserves every version of every object, while Lifecycle rules automate transitions and expirations.

---

## S3 Versioning

### What is Versioning?

Versioning keeps multiple variants of an object in the same bucket. When enabled, S3 preserves all versions of every object, including delete markers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         S3 VERSIONING CONCEPT                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Object: document.txt                                                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Version 1 (v1)  │  "Hello World"        │ 2024-01-01 │ 100 bytes   │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ Version 2 (v2)  │  "Hello World v2"     │ 2024-01-15 │ 150 bytes   │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ Version 3 (v3)  │  "Hello World v3"     │ 2024-02-01 │ 200 bytes   │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │ Delete Marker   │  (null content)       │ 2024-02-15 │ CURRENT     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  GET document.txt → Returns 404 (delete marker is current)                  │
│  GET document.txt?versionId=v3 → Returns "Hello World v3"                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Versioning States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VERSIONING STATES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. UNVERSIONED (Default)                                                   │
│     - No version history                                                    │
│     - Objects have versionId: null                                          │
│     - Delete permanently removes object                                     │
│                                                                             │
│  2. ENABLED                                                                 │
│     - All new objects get unique versionId                                  │
│     - All versions preserved                                                │
│     - Delete adds delete marker                                             │
│                                                                             │
│  3. SUSPENDED                                                               │
│     - New objects get versionId: null                                       │
│     - Existing versions preserved                                           │
│     - Cannot return to unversioned state                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

State Transitions:
    Unversioned ──► Enabled ──► Suspended ──► Enabled
                        ◄──────────────────────┘
    (Cannot go back to Unversioned once Enabled)
```

### Enabling Versioning

#### AWS CLI

```bash
# Enable versioning
aws s3api put-bucket-versioning \
    --bucket my-bucket \
    --versioning-configuration Status=Enabled

# Check versioning status
aws s3api get-bucket-versioning --bucket my-bucket

# Suspend versioning
aws s3api put-bucket-versioning \
    --bucket my-bucket \
    --versioning-configuration Status=Suspended
```

#### Python (Boto3)

```python
import boto3

s3_client = boto3.client('s3')

# Enable versioning
s3_client.put_bucket_versioning(
    Bucket='my-bucket',
    VersioningConfiguration={'Status': 'Enabled'}
)

# Check status
response = s3_client.get_bucket_versioning(Bucket='my-bucket')
print(f"Versioning Status: {response.get('Status', 'Not enabled')}")

# Suspend versioning
s3_client.put_bucket_versioning(
    Bucket='my-bucket',
    VersioningConfiguration={'Status': 'Suspended'}
)
```

#### Node.js (AWS SDK v3)

```javascript
import { S3Client, PutBucketVersioningCommand, GetBucketVersioningCommand } from "@aws-sdk/client-s3";

const s3Client = new S3Client({ region: "us-east-1" });

async function enableVersioning(bucketName) {
    const command = new PutBucketVersioningCommand({
        Bucket: bucketName,
        VersioningConfiguration: { Status: "Enabled" }
    });
    await s3Client.send(command);
    console.log(`Versioning enabled for ${bucketName}`);
}

async function getVersioningStatus(bucketName) {
    const command = new GetBucketVersioningCommand({ Bucket: bucketName });
    const response = await s3Client.send(command);
    return response.Status || "Not enabled";
}
```

---

## Working with Versions

### Listing Versions

```bash
# List all versions
aws s3api list-object-versions --bucket my-bucket

# List versions for specific prefix
aws s3api list-object-versions \
    --bucket my-bucket \
    --prefix "documents/"

# List with max items
aws s3api list-object-versions \
    --bucket my-bucket \
    --max-items 100
```

```python
import boto3

s3_client = boto3.client('s3')

# List all versions
response = s3_client.list_object_versions(Bucket='my-bucket')

# Current versions
for version in response.get('Versions', []):
    print(f"Key: {version['Key']}")
    print(f"  VersionId: {version['VersionId']}")
    print(f"  IsLatest: {version['IsLatest']}")
    print(f"  Size: {version['Size']}")
    print(f"  LastModified: {version['LastModified']}")

# Delete markers
for marker in response.get('DeleteMarkers', []):
    print(f"Delete Marker: {marker['Key']}")
    print(f"  VersionId: {marker['VersionId']}")
    print(f"  IsLatest: {marker['IsLatest']}")
```

### Retrieving Specific Versions

```bash
# Get specific version
aws s3api get-object \
    --bucket my-bucket \
    --key document.txt \
    --version-id "3HL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X" \
    ./document-old.txt

# Get object metadata for specific version
aws s3api head-object \
    --bucket my-bucket \
    --key document.txt \
    --version-id "3HL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X"
```

```python
import boto3

s3_client = boto3.client('s3')

# Get specific version
response = s3_client.get_object(
    Bucket='my-bucket',
    Key='document.txt',
    VersionId='3HL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X'
)

content = response['Body'].read().decode('utf-8')
print(f"Content: {content}")
print(f"Version: {response['VersionId']}")
```

### Deleting Objects and Versions

```
Delete Operations:
─────────────────────────────────────────────────────────────────────────────

WITHOUT VersionId (Simple Delete):
┌──────────────────────────────────────────────────────────────────────────┐
│ DELETE document.txt                                                      │
│                                                                          │
│ Before:                           After:                                 │
│ ┌─────────┐                       ┌─────────┐                            │
│ │ v3 ★    │ (current)             │ Delete  │ ★ (current)                │
│ ├─────────┤                       │ Marker  │                            │
│ │ v2      │                       ├─────────┤                            │
│ ├─────────┤                       │ v3      │                            │
│ │ v1      │                       ├─────────┤                            │
│ └─────────┘                       │ v2      │                            │
│                                   ├─────────┤                            │
│                                   │ v1      │                            │
│                                   └─────────┘                            │
│ Object appears deleted but all versions still exist                      │
└──────────────────────────────────────────────────────────────────────────┘

WITH VersionId (Permanent Delete):
┌──────────────────────────────────────────────────────────────────────────┐
│ DELETE document.txt?versionId=v2                                         │
│                                                                          │
│ Before:                           After:                                 │
│ ┌─────────┐                       ┌─────────┐                            │
│ │ v3 ★    │                       │ v3 ★    │                            │
│ ├─────────┤                       ├─────────┤                            │
│ │ v2      │ ←── Deleted           │ v1      │                            │
│ ├─────────┤                       └─────────┘                            │
│ │ v1      │                                                              │
│ └─────────┘                       v2 is permanently gone                 │
└──────────────────────────────────────────────────────────────────────────┘
```

```bash
# Add delete marker (soft delete)
aws s3 rm s3://my-bucket/document.txt

# Permanently delete specific version
aws s3api delete-object \
    --bucket my-bucket \
    --key document.txt \
    --version-id "3HL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X"

# Delete the delete marker (undelete)
aws s3api delete-object \
    --bucket my-bucket \
    --key document.txt \
    --version-id "DeleteMarkerVersionId"
```

```python
import boto3

s3_client = boto3.client('s3')

# Delete specific version permanently
s3_client.delete_object(
    Bucket='my-bucket',
    Key='document.txt',
    VersionId='3HL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X'
)

# Delete all versions of an object
def delete_all_versions(bucket, key):
    """Delete all versions of an object including delete markers."""
    versions = s3_client.list_object_versions(
        Bucket=bucket,
        Prefix=key
    )

    # Delete all versions
    for version in versions.get('Versions', []):
        if version['Key'] == key:
            s3_client.delete_object(
                Bucket=bucket,
                Key=key,
                VersionId=version['VersionId']
            )
            print(f"Deleted version: {version['VersionId']}")

    # Delete all delete markers
    for marker in versions.get('DeleteMarkers', []):
        if marker['Key'] == key:
            s3_client.delete_object(
                Bucket=bucket,
                Key=key,
                VersionId=marker['VersionId']
            )
            print(f"Deleted marker: {marker['VersionId']}")

delete_all_versions('my-bucket', 'document.txt')
```

### Restoring Previous Versions

```python
import boto3

s3_client = boto3.client('s3')

def restore_version(bucket, key, version_id):
    """
    Restore a previous version by copying it to become the current version.
    """
    # Copy the old version to the same key (creates new current version)
    s3_client.copy_object(
        Bucket=bucket,
        Key=key,
        CopySource={
            'Bucket': bucket,
            'Key': key,
            'VersionId': version_id
        }
    )
    print(f"Restored {key} to version {version_id}")

# Example: Restore to a previous version
restore_version('my-bucket', 'document.txt', 'old-version-id')
```

---

## MFA Delete

### Overview

MFA Delete adds an extra layer of protection by requiring multi-factor authentication for:
- Permanently deleting object versions
- Changing versioning state

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MFA DELETE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Protected Operations:                                                      │
│  ├── Permanently delete an object version                                   │
│  └── Change bucket versioning state (enable/suspend)                        │
│                                                                             │
│  Requirements:                                                              │
│  ├── Bucket versioning must be enabled                                      │
│  ├── Only root account can enable MFA Delete                                │
│  ├── Requires virtual or hardware MFA device                                │
│  └── Cannot be enabled via AWS Console (CLI/API only)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enabling MFA Delete

```bash
# Enable MFA Delete (must use root account)
# Serial number is from your MFA device
# Token code is the current 6-digit code

aws s3api put-bucket-versioning \
    --bucket my-bucket \
    --versioning-configuration Status=Enabled,MFADelete=Enabled \
    --mfa "arn:aws:iam::123456789012:mfa/root-account-mfa-device 123456"
```

### Deleting with MFA

```bash
# Delete version with MFA
aws s3api delete-object \
    --bucket my-bucket \
    --key document.txt \
    --version-id "VersionId" \
    --mfa "arn:aws:iam::123456789012:mfa/device 123456"
```

---

## S3 Lifecycle Policies

### What are Lifecycle Policies?

Lifecycle policies automate object management by defining rules that transition objects between storage classes or expire them after a specified time.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LIFECYCLE POLICY ACTIONS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TRANSITION ACTIONS                                                         │
│  ─────────────────                                                          │
│  Move objects between storage classes:                                      │
│                                                                             │
│  Day 0         Day 30          Day 90          Day 365                      │
│    │             │               │               │                          │
│    ▼             ▼               ▼               ▼                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐                    │
│  │Standard │─▶│Standard │─▶│ Glacier │─▶│ Glacier Deep │                    │
│  │         │  │   IA    │  │ Instant │  │   Archive    │                    │
│  └─────────┘  └─────────┘  └─────────┘  └──────────────┘                    │
│                                                                             │
│  EXPIRATION ACTIONS                                                         │
│  ─────────────────                                                          │
│  Permanently delete objects:                                                │
│  ├── Delete current versions after N days                                   │
│  ├── Delete previous versions after N days                                  │
│  ├── Delete expired delete markers                                          │
│  └── Abort incomplete multipart uploads                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Lifecycle Rule Components

```json
{
    "Rules": [
        {
            "ID": "RuleIdentifier",
            "Status": "Enabled | Disabled",
            "Filter": {
                "Prefix": "logs/",
                "Tag": {"Key": "...", "Value": "..."},
                "ObjectSizeGreaterThan": 1000,
                "ObjectSizeLessThan": 1000000,
                "And": { ... }
            },
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                }
            ],
            "NoncurrentVersionTransitions": [
                {
                    "NoncurrentDays": 30,
                    "StorageClass": "GLACIER"
                }
            ],
            "Expiration": {
                "Days": 365
            },
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 90
            },
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": 7
            },
            "ExpiredObjectDeleteMarker": true
        }
    ]
}
```

### Transition Constraints

```
Valid Storage Class Transitions:
───────────────────────────────────────────────────────────────────────────

STANDARD ─────────────────────────────────────────────────────────────────┐
    │                                                                     │
    ├──► INTELLIGENT_TIERING ─────────────────────────────────────────┐   │
    │           │                                                     │   │
    ├───────────┼──► STANDARD_IA ──────────────────────────────────┐  │   │
    │           │        │                                         │  │   │
    ├───────────┼────────┼──► ONEZONE_IA ──────────────────────┐   │  │   │
    │           │        │        │                            │   │  │   │
    ├───────────┼────────┼────────┼──► GLACIER_IR ─────────┐   │   │  │   │
    │           │        │        │        │               │   │   │  │   │
    ├───────────┼────────┼────────┼────────┼──► GLACIER ───┼───┼───┼──┼───┘
    │           │        │        │        │       │       │   │   │  │
    └───────────┴────────┴────────┴────────┴───────┼───────┴───┴───┴──┘
                                                   │
                                           DEEP_ARCHIVE

Minimum Days Between Transitions:
- STANDARD → STANDARD_IA/ONEZONE_IA: 30 days
- Any → GLACIER_IR: 90 days
- Any → GLACIER: 90 days
- Any → DEEP_ARCHIVE: 180 days

Minimum Object Size for IA classes: 128 KB
(Smaller objects can transition but are charged as 128 KB)
```

---

## Lifecycle Policy Examples

### Example 1: Basic Transition and Expiration

```json
{
    "Rules": [
        {
            "ID": "StandardLifecycle",
            "Status": "Enabled",
            "Filter": {},
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER_IR"
                },
                {
                    "Days": 365,
                    "StorageClass": "DEEP_ARCHIVE"
                }
            ],
            "Expiration": {
                "Days": 2555
            }
        }
    ]
}
```

### Example 2: Logs Management

```json
{
    "Rules": [
        {
            "ID": "LogsLifecycle",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "logs/"
            },
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ],
            "Expiration": {
                "Days": 365
            }
        }
    ]
}
```

### Example 3: Versioned Bucket Management

```json
{
    "Rules": [
        {
            "ID": "VersioningLifecycle",
            "Status": "Enabled",
            "Filter": {},
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                }
            ],
            "NoncurrentVersionTransitions": [
                {
                    "NoncurrentDays": 30,
                    "StorageClass": "GLACIER"
                }
            ],
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 90,
                "NewerNoncurrentVersions": 5
            },
            "ExpiredObjectDeleteMarker": true
        }
    ]
}
```

### Example 4: Size-Based Rules

```json
{
    "Rules": [
        {
            "ID": "LargeFilesToGlacier",
            "Status": "Enabled",
            "Filter": {
                "And": {
                    "Prefix": "archives/",
                    "ObjectSizeGreaterThan": 1073741824
                }
            },
            "Transitions": [
                {
                    "Days": 1,
                    "StorageClass": "GLACIER_IR"
                }
            ]
        }
    ]
}
```

### Example 5: Tag-Based Rules

```json
{
    "Rules": [
        {
            "ID": "ArchiveTaggedObjects",
            "Status": "Enabled",
            "Filter": {
                "Tag": {
                    "Key": "archive",
                    "Value": "true"
                }
            },
            "Transitions": [
                {
                    "Days": 0,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
```

### Example 6: Abort Incomplete Multipart Uploads

```json
{
    "Rules": [
        {
            "ID": "AbortIncompleteUploads",
            "Status": "Enabled",
            "Filter": {},
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": 7
            }
        }
    ]
}
```

---

## Managing Lifecycle Policies

### AWS CLI

```bash
# Get current lifecycle configuration
aws s3api get-bucket-lifecycle-configuration --bucket my-bucket

# Put lifecycle configuration from file
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket \
    --lifecycle-configuration file://lifecycle.json

# Delete lifecycle configuration
aws s3api delete-bucket-lifecycle --bucket my-bucket

# Example: Create and apply lifecycle policy
cat > lifecycle.json << 'EOF'
{
    "Rules": [
        {
            "ID": "TransitionToIA",
            "Status": "Enabled",
            "Filter": {"Prefix": "data/"},
            "Transitions": [
                {"Days": 30, "StorageClass": "STANDARD_IA"}
            ]
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket \
    --lifecycle-configuration file://lifecycle.json
```

### Python (Boto3)

```python
import boto3
import json

s3_client = boto3.client('s3')

# Define lifecycle configuration
lifecycle_config = {
    'Rules': [
        {
            'ID': 'ArchiveOldData',
            'Status': 'Enabled',
            'Filter': {'Prefix': 'data/'},
            'Transitions': [
                {'Days': 30, 'StorageClass': 'STANDARD_IA'},
                {'Days': 90, 'StorageClass': 'GLACIER_IR'},
                {'Days': 365, 'StorageClass': 'DEEP_ARCHIVE'}
            ],
            'NoncurrentVersionTransitions': [
                {'NoncurrentDays': 30, 'StorageClass': 'GLACIER'}
            ],
            'NoncurrentVersionExpiration': {
                'NoncurrentDays': 90
            }
        },
        {
            'ID': 'CleanupUploads',
            'Status': 'Enabled',
            'Filter': {},
            'AbortIncompleteMultipartUpload': {
                'DaysAfterInitiation': 7
            }
        }
    ]
}

# Apply lifecycle configuration
s3_client.put_bucket_lifecycle_configuration(
    Bucket='my-bucket',
    LifecycleConfiguration=lifecycle_config
)

# Get lifecycle configuration
response = s3_client.get_bucket_lifecycle_configuration(Bucket='my-bucket')
print(json.dumps(response['Rules'], indent=2))

# Delete lifecycle configuration
s3_client.delete_bucket_lifecycle(Bucket='my-bucket')
```

### Node.js (AWS SDK v3)

```javascript
import {
    S3Client,
    PutBucketLifecycleConfigurationCommand,
    GetBucketLifecycleConfigurationCommand,
    DeleteBucketLifecycleCommand
} from "@aws-sdk/client-s3";

const s3Client = new S3Client({ region: "us-east-1" });

async function putLifecyclePolicy(bucketName) {
    const command = new PutBucketLifecycleConfigurationCommand({
        Bucket: bucketName,
        LifecycleConfiguration: {
            Rules: [
                {
                    ID: "ArchiveRule",
                    Status: "Enabled",
                    Filter: { Prefix: "logs/" },
                    Transitions: [
                        { Days: 30, StorageClass: "STANDARD_IA" },
                        { Days: 90, StorageClass: "GLACIER" }
                    ],
                    Expiration: { Days: 365 }
                }
            ]
        }
    });

    await s3Client.send(command);
    console.log("Lifecycle policy applied");
}

async function getLifecyclePolicy(bucketName) {
    const command = new GetBucketLifecycleConfigurationCommand({
        Bucket: bucketName
    });

    const response = await s3Client.send(command);
    return response.Rules;
}
```

---

## Cost Considerations

### Storage Class Transition Costs

```
TRANSITION REQUESTS:
────────────────────────────────────────────────────────────────────────────

Each object transition counts as a request:

To STANDARD_IA / ONEZONE_IA:    $0.01 per 1,000 requests
To GLACIER_IR:                   $0.02 per 1,000 requests
To GLACIER:                      $0.03 per 1,000 requests
To DEEP_ARCHIVE:                 $0.05 per 1,000 requests

MINIMUM STORAGE DURATION CHARGES:
────────────────────────────────────────────────────────────────────────────

If you delete or transition BEFORE minimum duration:

STANDARD_IA / ONEZONE_IA:  Charged for full 30 days
GLACIER_IR:                Charged for full 90 days
GLACIER:                   Charged for full 90 days
DEEP_ARCHIVE:              Charged for full 180 days

Example:
- Upload 1 GB to GLACIER_IR on Day 1
- Transition to DEEP_ARCHIVE on Day 45
- You pay for: 90 days of GLACIER_IR storage (not 45)
```

### Cost Optimization Calculator

```python
def calculate_lifecycle_savings(
    storage_gb,
    months,
    access_frequency  # 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
):
    """
    Calculate potential savings from implementing lifecycle policies.
    """
    # Monthly prices per GB (US East)
    prices = {
        'STANDARD': 0.023,
        'STANDARD_IA': 0.0125,
        'GLACIER_IR': 0.004,
        'GLACIER': 0.0036,
        'DEEP_ARCHIVE': 0.00099
    }

    # Recommended storage class by access frequency
    recommendations = {
        'daily': 'STANDARD',
        'weekly': 'STANDARD',
        'monthly': 'STANDARD_IA',
        'quarterly': 'GLACIER_IR',
        'yearly': 'DEEP_ARCHIVE'
    }

    recommended_class = recommendations[access_frequency]
    standard_cost = storage_gb * prices['STANDARD'] * months
    optimized_cost = storage_gb * prices[recommended_class] * months

    savings = standard_cost - optimized_cost
    savings_percent = (savings / standard_cost) * 100

    return {
        'current_storage_class': 'STANDARD',
        'recommended_storage_class': recommended_class,
        'standard_cost': round(standard_cost, 2),
        'optimized_cost': round(optimized_cost, 2),
        'savings': round(savings, 2),
        'savings_percent': round(savings_percent, 1)
    }

# Example: 1 TB accessed quarterly for 12 months
result = calculate_lifecycle_savings(1024, 12, 'quarterly')
print(f"Current cost: ${result['standard_cost']}")
print(f"Optimized cost: ${result['optimized_cost']}")
print(f"Savings: ${result['savings']} ({result['savings_percent']}%)")
```

---

## Best Practices

### Versioning Best Practices

```
1. Enable versioning for critical buckets
   - Protects against accidental deletes
   - Enables point-in-time recovery

2. Use lifecycle policies with versioning
   - Expire old versions to control costs
   - Keep recent versions for recovery

3. Consider MFA Delete for sensitive data
   - Extra protection against malicious deletes
   - Requires root account to enable

4. Monitor version count and storage
   - Use S3 Inventory for auditing
   - Set up alerts for storage growth
```

### Lifecycle Best Practices

```
1. Start with analysis
   - Use S3 Analytics to understand access patterns
   - Make data-driven transition decisions

2. Test policies on non-production first
   - Validate transitions work as expected
   - Check for unintended expirations

3. Use appropriate filters
   - Apply rules to specific prefixes or tags
   - Avoid broad rules that affect all objects

4. Clean up incomplete multipart uploads
   - Always include AbortIncompleteMultipartUpload
   - 7 days is a reasonable default

5. Consider minimum storage durations
   - Don't transition too frequently
   - Factor in minimum duration charges

6. Document your policies
   - Keep track of why rules exist
   - Review policies periodically
```

### Common Patterns

```
Pattern 1: Log Archival
├── 0-30 days:   STANDARD (active analysis)
├── 30-90 days:  STANDARD_IA (occasional access)
├── 90-365 days: GLACIER (compliance retention)
└── 365+ days:   Delete or DEEP_ARCHIVE

Pattern 2: Backup Retention
├── Current version: STANDARD
├── Previous versions: GLACIER after 7 days
└── Delete old versions: After 90 days, keep 3 latest

Pattern 3: Media Archive
├── 0-7 days:    STANDARD (active editing)
├── 7-30 days:   STANDARD_IA (review period)
└── 30+ days:    GLACIER_IR (archive with fast access)

Pattern 4: Compliance Archive
├── 0-30 days:   STANDARD
├── 30-90 days:  GLACIER_IR
├── 90-365 days: GLACIER
└── 1-7 years:   DEEP_ARCHIVE
```

---

## Monitoring and Troubleshooting

### S3 Inventory for Version Analysis

```bash
# Configure S3 Inventory to track versions
aws s3api put-bucket-inventory-configuration \
    --bucket my-bucket \
    --id version-inventory \
    --inventory-configuration '{
        "Destination": {
            "S3BucketDestination": {
                "Bucket": "arn:aws:s3:::inventory-bucket",
                "Format": "CSV",
                "Prefix": "inventory"
            }
        },
        "IsEnabled": true,
        "Id": "version-inventory",
        "IncludedObjectVersions": "All",
        "OptionalFields": [
            "Size",
            "LastModifiedDate",
            "StorageClass",
            "IsMultipartUploaded"
        ],
        "Schedule": {"Frequency": "Daily"}
    }'
```

### Checking Lifecycle Execution

```python
import boto3
from datetime import datetime, timedelta

s3_client = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

# Check lifecycle transition metrics
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/S3',
    MetricName='LifecycleTransitions',
    Dimensions=[
        {'Name': 'BucketName', 'Value': 'my-bucket'},
        {'Name': 'StorageType', 'Value': 'StandardIAStorage'}
    ],
    StartTime=datetime.utcnow() - timedelta(days=7),
    EndTime=datetime.utcnow(),
    Period=86400,
    Statistics=['Sum']
)

for point in response['Datapoints']:
    print(f"Date: {point['Timestamp']}, Transitions: {point['Sum']}")
```

---

## Summary

| Feature | Purpose | Key Considerations |
|---------|---------|-------------------|
| **Versioning** | Preserve all object versions | Increases storage costs |
| **MFA Delete** | Protect against malicious deletes | Root account required |
| **Transitions** | Move to cheaper storage classes | Minimum duration charges |
| **Expirations** | Automatically delete objects | Cannot be undone |
| **Noncurrent Versions** | Manage old versions | Control version sprawl |
| **Incomplete Uploads** | Clean up failed uploads | Reduces wasted storage |

---

## Next Steps

Continue to [05-s3-security.md](./05-s3-security.md) to learn about encryption and advanced security features for S3.
