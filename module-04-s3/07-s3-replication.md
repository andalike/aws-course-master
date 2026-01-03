# S3 Replication: Complete Guide

## Table of Contents
1. [Introduction to S3 Replication](#introduction-to-s3-replication)
2. [Same-Region Replication (SRR)](#same-region-replication-srr)
3. [Cross-Region Replication (CRR)](#cross-region-replication-crr)
4. [Replication Rules and Filters](#replication-rules-and-filters)
5. [Replication Time Control (RTC)](#replication-time-control-rtc)
6. [Bidirectional Replication](#bidirectional-replication)
7. [Hands-On: Setting Up Replication](#hands-on-setting-up-replication)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [Cost Considerations](#cost-considerations)
10. [Best Practices](#best-practices)

---

## Introduction to S3 Replication

S3 Replication enables automatic, asynchronous copying of objects across S3 buckets. This feature is essential for disaster recovery, compliance, latency reduction, and data sovereignty requirements.

### Replication Architecture

```
+-------------------+                      +-------------------+
|   Source Bucket   |                      | Destination Bucket|
|   (Versioning ON) |                      |  (Versioning ON)  |
+-------------------+                      +-------------------+
         |                                          ^
         |        +--------------------+            |
         +------->|  Replication Rule  |------------+
                  | - Filter (prefix)  |
                  | - Destination      |
                  | - IAM Role         |
                  +--------------------+
                           |
                  +--------v--------+
                  |    IAM Role     |
                  | - Read source   |
                  | - Write dest    |
                  +-----------------+
```

### Key Concepts

| Feature | Description |
|---------|-------------|
| **Versioning** | Must be enabled on both buckets |
| **Replication Rule** | Defines what and where to replicate |
| **IAM Role** | Provides permissions for replication |
| **Async Process** | Objects are replicated asynchronously |
| **Object Metadata** | Metadata and tags are preserved |

### Types of Replication

```
+---------------------------+---------------------------+
|  Same-Region Replication  |  Cross-Region Replication |
|         (SRR)             |          (CRR)            |
+---------------------------+---------------------------+
| - Same AWS Region         | - Different AWS Regions   |
| - Log aggregation         | - Disaster recovery       |
| - Dev/Test environments   | - Compliance requirements |
| - Data sovereignty        | - Latency reduction       |
+---------------------------+---------------------------+
```

---

## Same-Region Replication (SRR)

Same-Region Replication copies objects to a destination bucket within the same AWS Region.

### Use Cases for SRR

1. **Log Aggregation**
   - Collect logs from multiple buckets into one
   - Centralized log analysis

2. **Development and Testing**
   - Replicate production data to test environments
   - Maintain data consistency across environments

3. **Data Sovereignty**
   - Keep copies within the same region
   - Meet data residency requirements

4. **Account Isolation**
   - Replicate between accounts in the same region
   - Separate production from analytics

### SRR Architecture

```
                    AWS Region: us-east-1
+-------------------------------------------------------+
|                                                       |
|  Account A                    Account B               |
|  +---------------+            +---------------+       |
|  | Source Bucket | ---------> | Dest Bucket   |       |
|  | (Production)  |    SRR     | (Analytics)   |       |
|  +---------------+            +---------------+       |
|                                                       |
+-------------------------------------------------------+
```

### SRR Configuration Example

```bash
# Step 1: Create source bucket with versioning
aws s3api create-bucket \
    --bucket source-bucket-srr-demo \
    --region us-east-1

aws s3api put-bucket-versioning \
    --bucket source-bucket-srr-demo \
    --versioning-configuration Status=Enabled

# Step 2: Create destination bucket with versioning
aws s3api create-bucket \
    --bucket dest-bucket-srr-demo \
    --region us-east-1

aws s3api put-bucket-versioning \
    --bucket dest-bucket-srr-demo \
    --versioning-configuration Status=Enabled
```

---

## Cross-Region Replication (CRR)

Cross-Region Replication copies objects to a destination bucket in a different AWS Region.

### Use Cases for CRR

1. **Disaster Recovery**
   - Geographic redundancy
   - Business continuity

2. **Compliance Requirements**
   - Data backup in different regions
   - Regulatory requirements for geographic separation

3. **Latency Reduction**
   - Replicate data closer to users
   - Improve application performance

4. **Operational Efficiency**
   - Regional data processing
   - Distributed analytics

### CRR Architecture

```
+---------------------+                    +---------------------+
|  AWS Region:        |                    |  AWS Region:        |
|  us-east-1          |                    |  eu-west-1          |
|                     |                    |                     |
| +---------------+   |       CRR          | +---------------+   |
| | Source Bucket |---+------------------->+-| Dest Bucket   |   |
| | (Primary)     |   |   (Automatic)      | | (DR Copy)     |   |
| +---------------+   |                    | +---------------+   |
|                     |                    |                     |
+---------------------+                    +---------------------+
         |                                          |
         v                                          v
   Primary Users                            DR / EU Users
   (Americas)                               (Europe)
```

### CRR vs SRR Comparison

| Feature | SRR | CRR |
|---------|-----|-----|
| **Region** | Same | Different |
| **Data Transfer Cost** | Lower | Higher (cross-region) |
| **Latency** | Lower | Higher |
| **DR Capability** | Limited | Full geographic DR |
| **Compliance** | Data residency | Geographic separation |
| **Use Case** | Log aggregation | Disaster recovery |

---

## Replication Rules and Filters

### Rule Components

```
Replication Rule Structure:
+----------------------------------------+
| Rule ID: "ReplicateImages"             |
+----------------------------------------+
| Priority: 1                            |
+----------------------------------------+
| Status: Enabled                        |
+----------------------------------------+
| Filter:                                |
|   - Prefix: "images/"                  |
|   - Tags: [{"Key": "replicate",        |
|            "Value": "true"}]           |
+----------------------------------------+
| Destination:                           |
|   - Bucket: dest-bucket                |
|   - Storage Class: STANDARD_IA         |
|   - Account: 123456789012              |
+----------------------------------------+
| Delete Marker Replication: Enabled     |
+----------------------------------------+
| Replica Modifications: Enabled         |
+----------------------------------------+
```

### Filter Types

#### 1. Prefix Filter

Replicate objects with a specific key prefix:

```json
{
    "Filter": {
        "Prefix": "documents/"
    }
}
```

#### 2. Tag Filter

Replicate objects with specific tags:

```json
{
    "Filter": {
        "Tag": {
            "Key": "replicate",
            "Value": "true"
        }
    }
}
```

#### 3. Combined Filter (AND)

Replicate objects matching both prefix AND tag:

```json
{
    "Filter": {
        "And": {
            "Prefix": "documents/",
            "Tags": [
                {
                    "Key": "department",
                    "Value": "finance"
                }
            ]
        }
    }
}
```

### Multiple Replication Rules

```
Source Bucket:
+--------------------------------+
| /images/photo1.jpg             |  --> Rule 1: Images bucket
| /images/photo2.jpg             |
+--------------------------------+
| /documents/report.pdf          |  --> Rule 2: Documents bucket
| /documents/invoice.pdf         |
+--------------------------------+
| /logs/app.log                  |  --> Rule 3: Logs bucket
+--------------------------------+
| /other/file.txt                |  --> No match (not replicated)
+--------------------------------+

Rules evaluated by priority (lower number = higher priority)
```

### Replication Rule JSON Example

```json
{
    "Rules": [
        {
            "ID": "ReplicateImages",
            "Priority": 1,
            "Status": "Enabled",
            "Filter": {
                "Prefix": "images/"
            },
            "Destination": {
                "Bucket": "arn:aws:s3:::images-backup-bucket",
                "StorageClass": "STANDARD_IA"
            },
            "DeleteMarkerReplication": {
                "Status": "Enabled"
            }
        },
        {
            "ID": "ReplicateDocuments",
            "Priority": 2,
            "Status": "Enabled",
            "Filter": {
                "And": {
                    "Prefix": "documents/",
                    "Tags": [
                        {
                            "Key": "replicate",
                            "Value": "true"
                        }
                    ]
                }
            },
            "Destination": {
                "Bucket": "arn:aws:s3:::documents-backup-bucket"
            }
        }
    ]
}
```

---

## Replication Time Control (RTC)

Replication Time Control (RTC) provides a predictable replication time backed by an SLA.

### RTC Features

```
Standard Replication              With RTC
+------------------+             +------------------+
| Best Effort      |             | SLA-backed       |
| - Usually fast   |             | - 99.99% within  |
| - No guarantee   |             |   15 minutes     |
| - No metrics     |             | - CloudWatch     |
+------------------+             |   metrics        |
                                 | - Replication    |
                                 |   notifications  |
                                 +------------------+
```

### RTC SLA

- **99.99%** of new objects replicated within **15 minutes**
- Remaining 0.01% replicated within a reasonable timeframe
- Backed by AWS Service Level Agreement

### RTC Configuration

```json
{
    "Rules": [
        {
            "ID": "RTC-Rule",
            "Priority": 1,
            "Status": "Enabled",
            "Filter": {},
            "Destination": {
                "Bucket": "arn:aws:s3:::dest-bucket",
                "ReplicationTime": {
                    "Status": "Enabled",
                    "Time": {
                        "Minutes": 15
                    }
                },
                "Metrics": {
                    "Status": "Enabled",
                    "EventThreshold": {
                        "Minutes": 15
                    }
                }
            }
        }
    ]
}
```

### RTC Metrics

RTC provides these CloudWatch metrics:

| Metric | Description |
|--------|-------------|
| `ReplicationLatency` | Time for replication |
| `BytesPendingReplication` | Bytes waiting to replicate |
| `OperationsPendingReplication` | Objects waiting to replicate |
| `OperationsFailedReplication` | Failed replication operations |

### When to Use RTC

```
+-----------------------------------+
|         Use RTC When:             |
+-----------------------------------+
| - Compliance requires defined RPO |
| - Critical data needs SLA         |
| - Disaster recovery requirements  |
| - Need replication monitoring     |
+-----------------------------------+

+-----------------------------------+
|      Skip RTC When:               |
+-----------------------------------+
| - Cost optimization is priority   |
| - Best-effort is acceptable       |
| - Non-critical data replication   |
+-----------------------------------+
```

---

## Bidirectional Replication

Bidirectional replication enables two-way sync between buckets.

### Architecture

```
        Bidirectional Replication
+---------------+      +---------------+
|   Bucket A    |<---->|   Bucket B    |
|  (us-east-1)  |      |  (eu-west-1)  |
+---------------+      +---------------+
       ^                      ^
       |                      |
  Write here            Write here
  Replicates -->      <-- Replicates
```

### Preventing Replication Loops

S3 uses replica modification sync to prevent infinite loops:

```
Object uploaded to Bucket A:
1. Object marked as "original"
2. Replicated to Bucket B
3. Replica marked as "replica"
4. Bucket B's rule sees "replica" flag
5. Does NOT replicate back to A

Result: One-time replication, no loop
```

### Bidirectional Replication Configuration

**Bucket A -> Bucket B:**
```json
{
    "Rules": [
        {
            "ID": "A-to-B",
            "Status": "Enabled",
            "Priority": 1,
            "Filter": {},
            "Destination": {
                "Bucket": "arn:aws:s3:::bucket-b"
            },
            "SourceSelectionCriteria": {
                "ReplicaModifications": {
                    "Status": "Enabled"
                }
            },
            "DeleteMarkerReplication": {
                "Status": "Enabled"
            }
        }
    ]
}
```

**Bucket B -> Bucket A:**
```json
{
    "Rules": [
        {
            "ID": "B-to-A",
            "Status": "Enabled",
            "Priority": 1,
            "Filter": {},
            "Destination": {
                "Bucket": "arn:aws:s3:::bucket-a"
            },
            "SourceSelectionCriteria": {
                "ReplicaModifications": {
                    "Status": "Enabled"
                }
            },
            "DeleteMarkerReplication": {
                "Status": "Enabled"
            }
        }
    ]
}
```

---

## Hands-On: Setting Up Replication

### Lab 1: Cross-Region Replication Setup

#### Prerequisites
- AWS CLI configured with appropriate permissions
- Two AWS regions available

#### Step 1: Create IAM Role for Replication

```bash
# Create trust policy
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the role
aws iam create-role \
    --role-name S3ReplicationRole \
    --assume-role-policy-document file://trust-policy.json
```

#### Step 2: Create Replication Permission Policy

```bash
# Create permission policy
cat > replication-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::source-bucket-crr-demo"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObjectVersionForReplication",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectVersionTagging"
            ],
            "Resource": "arn:aws:s3:::source-bucket-crr-demo/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ReplicateTags"
            ],
            "Resource": "arn:aws:s3:::dest-bucket-crr-demo/*"
        }
    ]
}
EOF

# Attach policy to role
aws iam put-role-policy \
    --role-name S3ReplicationRole \
    --policy-name S3ReplicationPolicy \
    --policy-document file://replication-policy.json
```

#### Step 3: Create Source and Destination Buckets

```bash
# Create source bucket in us-east-1
aws s3api create-bucket \
    --bucket source-bucket-crr-demo-$(date +%s) \
    --region us-east-1

# Enable versioning on source
aws s3api put-bucket-versioning \
    --bucket source-bucket-crr-demo-$(date +%s) \
    --versioning-configuration Status=Enabled

# Create destination bucket in eu-west-1
aws s3api create-bucket \
    --bucket dest-bucket-crr-demo-$(date +%s) \
    --region eu-west-1 \
    --create-bucket-configuration LocationConstraint=eu-west-1

# Enable versioning on destination
aws s3api put-bucket-versioning \
    --bucket dest-bucket-crr-demo-$(date +%s) \
    --versioning-configuration Status=Enabled \
    --region eu-west-1
```

#### Step 4: Configure Replication

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create replication configuration
cat > replication-config.json << EOF
{
    "Role": "arn:aws:iam::${ACCOUNT_ID}:role/S3ReplicationRole",
    "Rules": [
        {
            "ID": "CrossRegionReplication",
            "Priority": 1,
            "Status": "Enabled",
            "Filter": {},
            "Destination": {
                "Bucket": "arn:aws:s3:::dest-bucket-crr-demo-TIMESTAMP",
                "StorageClass": "STANDARD"
            },
            "DeleteMarkerReplication": {
                "Status": "Enabled"
            }
        }
    ]
}
EOF

# Apply replication configuration
aws s3api put-bucket-replication \
    --bucket source-bucket-crr-demo-TIMESTAMP \
    --replication-configuration file://replication-config.json
```

#### Step 5: Test Replication

```bash
# Upload a test file
echo "Test content for replication" > test-file.txt

aws s3 cp test-file.txt s3://source-bucket-crr-demo-TIMESTAMP/

# Wait a moment and check destination
sleep 30

aws s3 ls s3://dest-bucket-crr-demo-TIMESTAMP/ --region eu-west-1
```

### Lab 2: Same-Region Replication with Filters

#### Step 1: Create Buckets

```bash
# Source bucket
aws s3api create-bucket \
    --bucket logs-source-bucket \
    --region us-east-1

aws s3api put-bucket-versioning \
    --bucket logs-source-bucket \
    --versioning-configuration Status=Enabled

# Destination for application logs
aws s3api create-bucket \
    --bucket app-logs-archive \
    --region us-east-1

aws s3api put-bucket-versioning \
    --bucket app-logs-archive \
    --versioning-configuration Status=Enabled

# Destination for access logs
aws s3api create-bucket \
    --bucket access-logs-archive \
    --region us-east-1

aws s3api put-bucket-versioning \
    --bucket access-logs-archive \
    --versioning-configuration Status=Enabled
```

#### Step 2: Configure Filtered Replication

```bash
cat > filtered-replication.json << 'EOF'
{
    "Role": "arn:aws:iam::ACCOUNT_ID:role/S3ReplicationRole",
    "Rules": [
        {
            "ID": "ReplicateAppLogs",
            "Priority": 1,
            "Status": "Enabled",
            "Filter": {
                "Prefix": "app-logs/"
            },
            "Destination": {
                "Bucket": "arn:aws:s3:::app-logs-archive",
                "StorageClass": "STANDARD_IA"
            }
        },
        {
            "ID": "ReplicateAccessLogs",
            "Priority": 2,
            "Status": "Enabled",
            "Filter": {
                "Prefix": "access-logs/"
            },
            "Destination": {
                "Bucket": "arn:aws:s3:::access-logs-archive",
                "StorageClass": "GLACIER"
            }
        }
    ]
}
EOF

aws s3api put-bucket-replication \
    --bucket logs-source-bucket \
    --replication-configuration file://filtered-replication.json
```

### Lab 3: Cross-Account Replication

#### Step 1: Source Account Configuration

```bash
# In source account
# Create bucket and enable versioning (same as before)

# Create replication configuration with cross-account settings
cat > cross-account-replication.json << 'EOF'
{
    "Role": "arn:aws:iam::SOURCE_ACCOUNT:role/S3ReplicationRole",
    "Rules": [
        {
            "ID": "CrossAccountReplication",
            "Priority": 1,
            "Status": "Enabled",
            "Filter": {},
            "Destination": {
                "Bucket": "arn:aws:s3:::dest-bucket-other-account",
                "Account": "DEST_ACCOUNT_ID",
                "AccessControlTranslation": {
                    "Owner": "Destination"
                }
            }
        }
    ]
}
EOF
```

#### Step 2: Destination Account Bucket Policy

```bash
# In destination account, add bucket policy
cat > dest-bucket-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowReplicationFromSourceAccount",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::SOURCE_ACCOUNT_ID:role/S3ReplicationRole"
            },
            "Action": [
                "s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ReplicateTags",
                "s3:ObjectOwnerOverrideToBucketOwner"
            ],
            "Resource": "arn:aws:s3:::dest-bucket-other-account/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket dest-bucket-other-account \
    --policy file://dest-bucket-policy.json
```

---

## Monitoring and Troubleshooting

### CloudWatch Metrics

```bash
# Get replication metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/S3 \
    --metric-name BytesPendingReplication \
    --dimensions Name=SourceBucket,Value=source-bucket \
                 Name=DestinationBucket,Value=dest-bucket \
                 Name=RuleId,Value=ReplicationRule \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average
```

### Replication Status Check

```bash
# Check object replication status
aws s3api head-object \
    --bucket source-bucket \
    --key my-object.txt \
    --query 'ReplicationStatus'

# Possible values:
# PENDING - Replication in progress
# COMPLETED - Successfully replicated
# FAILED - Replication failed
# REPLICA - Object is a replica
```

### Common Issues and Solutions

```
+----------------------------------+----------------------------------+
|            Issue                 |           Solution               |
+----------------------------------+----------------------------------+
| Versioning not enabled           | Enable versioning on both        |
|                                  | source and destination buckets   |
+----------------------------------+----------------------------------+
| IAM role permissions             | Verify role has GetObject on     |
| insufficient                     | source and ReplicateObject on    |
|                                  | destination                      |
+----------------------------------+----------------------------------+
| Cross-account: objects not       | Add bucket policy on destination |
| appearing                        | allowing replication role        |
+----------------------------------+----------------------------------+
| Existing objects not replicated  | Use S3 Batch Replication for     |
|                                  | existing objects                 |
+----------------------------------+----------------------------------+
| Delete markers not replicating   | Enable DeleteMarkerReplication   |
|                                  | in replication rule              |
+----------------------------------+----------------------------------+
```

### S3 Batch Replication for Existing Objects

```bash
# Create a batch replication job for existing objects
aws s3control create-job \
    --account-id 123456789012 \
    --confirmation-required \
    --operation '{"S3ReplicateObject":{}}' \
    --manifest '{"Spec":{"Format":"S3BatchOperations_CSV_20180820","Fields":["Bucket","Key"]},"Location":{"ObjectArn":"arn:aws:s3:::manifest-bucket/manifest.csv","ETag":"example-etag"}}' \
    --report '{"Bucket":"arn:aws:s3:::report-bucket","Prefix":"reports/","Format":"Report_CSV_20180820","Enabled":true,"ReportScope":"AllTasks"}' \
    --priority 10 \
    --role-arn arn:aws:iam::123456789012:role/BatchReplicationRole \
    --region us-east-1
```

---

## Cost Considerations

### Replication Costs

```
+---------------------------------------------+
|           Replication Cost Components       |
+---------------------------------------------+
| 1. Data Transfer                            |
|    - SRR: $0.00/GB (within region)          |
|    - CRR: $0.02/GB (inter-region, varies)   |
+---------------------------------------------+
| 2. Replication PUT Requests                 |
|    - Same as standard PUT pricing           |
|    - ~$0.005 per 1,000 requests             |
+---------------------------------------------+
| 3. Storage at Destination                   |
|    - Based on destination storage class     |
+---------------------------------------------+
| 4. RTC (if enabled)                         |
|    - Additional per-GB charge               |
|    - CloudWatch metrics charges             |
+---------------------------------------------+
```

### Cost Optimization Strategies

1. **Use Appropriate Storage Class**
   ```
   Source: S3 Standard ($0.023/GB)
      |
      v Replicate to
   Destination: S3 Standard-IA ($0.0125/GB) = 45% savings
   ```

2. **Filter to Essential Data**
   - Only replicate critical data
   - Use prefix/tag filters to exclude temp files

3. **Consider RTC Necessity**
   - Skip RTC for non-critical data
   - Use only when SLA is required

### Cost Comparison Example

```
Scenario: 1TB data, CRR from us-east-1 to eu-west-1

Standard CRR:
- Data Transfer: 1,000 GB x $0.02 = $20.00
- PUT Requests (1M objects): $5.00
- Storage (dest, Standard-IA): $12.50/month
- Total Initial: $25.00 + $12.50/month ongoing

With RTC:
- RTC Fee: ~$0.015/GB = $15.00
- Data Transfer: $20.00
- Metrics: ~$0.30/metric
- Total Initial: $35.30 + $12.50/month ongoing
```

---

## Best Practices

### 1. Replication Design

```
+------------------------------------------------+
|              Best Practices                     |
+------------------------------------------------+
| - Enable versioning before replication         |
| - Use specific filters to control costs        |
| - Test with a subset of data first             |
| - Monitor replication metrics                  |
| - Document replication rules                   |
+------------------------------------------------+
```

### 2. Security Considerations

```bash
# Use least privilege IAM roles
# Example: Restrict to specific buckets and prefixes
{
    "Effect": "Allow",
    "Action": "s3:GetObjectVersionForReplication",
    "Resource": "arn:aws:s3:::source-bucket/critical-data/*"
}
```

### 3. Operational Excellence

- **Tag replicated objects** for easy identification
- **Set up alerts** for replication failures
- **Regular audits** of replication status
- **Document disaster recovery procedures**

### 4. Compliance and Governance

```
Compliance Checklist:
[ ] Verify destination bucket encryption
[ ] Confirm cross-region data transfer compliance
[ ] Document retention policies
[ ] Test recovery procedures regularly
[ ] Audit access to replicated data
```

---

## Summary

### Key Takeaways

| Topic | Key Points |
|-------|------------|
| **Versioning** | Required for all replication |
| **SRR** | Same region, log aggregation, dev/test |
| **CRR** | Cross region, disaster recovery, latency |
| **Filters** | Prefix and tag-based filtering |
| **RTC** | 15-minute SLA for 99.99% of objects |
| **Bidirectional** | Two-way sync with loop prevention |
| **Existing Objects** | Use Batch Replication |

### Decision Tree

```
Do you need replication?
         |
    +----+----+
    |         |
   Yes        No --> Skip replication
    |
Same region or different?
    |
+---+---+
|       |
Same    Different
|       |
SRR     CRR
|       |
+-------+-------+
        |
Need guaranteed time?
        |
   +----+----+
   |         |
  Yes        No
   |         |
Enable RTC  Standard
```

---

## Next Steps

1. Complete the hands-on labs in this guide
2. Set up monitoring dashboards for replication
3. Practice cross-account replication scenarios
4. Review the quiz questions on replication
5. Proceed to S3 Performance Optimization guide

---

## Additional Resources

- [AWS S3 Replication Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [S3 Replication Time Control](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-time-control.html)
- [S3 Batch Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-batch-replication-batch.html)
