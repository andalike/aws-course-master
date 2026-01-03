# 02 - S3 Storage Classes

## Introduction

Amazon S3 offers a range of storage classes designed for different use cases. Choosing the right storage class can significantly reduce costs while maintaining the performance and availability your application needs.

---

## Storage Classes Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           S3 STORAGE CLASSES                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  FREQUENT ACCESS                      INFREQUENT ACCESS                         │
│  ┌─────────────────┐                  ┌─────────────────┐  ┌─────────────────┐  │
│  │   S3 Standard   │                  │  S3 Standard-IA │  │ S3 One Zone-IA  │  │
│  │                 │                  │                 │  │                 │  │
│  │ - High durability│                 │ - Lower storage │  │ - Single AZ     │  │
│  │ - High availabil│                  │   cost          │  │ - 20% cheaper   │  │
│  │ - Low latency   │                  │ - Retrieval fee │  │   than Std-IA   │  │
│  └─────────────────┘                  └─────────────────┘  └─────────────────┘  │
│                                                                                 │
│  INTELLIGENT                          ARCHIVE                                   │
│  ┌─────────────────┐                  ┌─────────────────┐  ┌─────────────────┐  │
│  │ S3 Intelligent- │                  │  S3 Glacier     │  │ S3 Glacier Deep │  │
│  │    Tiering      │                  │  Instant        │  │    Archive      │  │
│  │                 │                  │  Retrieval      │  │                 │  │
│  │ - Auto-tiering  │                  │ - Milliseconds  │  │ - Lowest cost   │  │
│  │ - Monitoring fee│                  │   access        │  │ - 12-48 hr      │  │
│  └─────────────────┘                  └─────────────────┘  └─────────────────┘  │
│                                                                                 │
│  ┌─────────────────┐                  ┌─────────────────┐                       │
│  │  S3 Glacier     │                  │ S3 Express One  │                       │
│  │  Flexible       │                  │     Zone        │                       │
│  │  Retrieval      │                  │                 │                       │
│  │                 │                  │ - Single-digit  │                       │
│  │ - Min to hours  │                  │   ms latency    │                       │
│  └─────────────────┘                  └─────────────────┘                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Storage Class Comparison

### Summary Table

| Storage Class | Use Case | Availability | Min Storage Duration | Retrieval Fee | First Byte Latency |
|--------------|----------|--------------|---------------------|---------------|-------------------|
| **S3 Standard** | Frequently accessed data | 99.99% | None | None | Milliseconds |
| **S3 Intelligent-Tiering** | Unknown/changing access | 99.9% | None | None | Milliseconds |
| **S3 Standard-IA** | Infrequent access, quick retrieval | 99.9% | 30 days | Per GB retrieved | Milliseconds |
| **S3 One Zone-IA** | Infrequent, recreatable data | 99.5% | 30 days | Per GB retrieved | Milliseconds |
| **S3 Glacier Instant** | Archive, instant access | 99.9% | 90 days | Per GB retrieved | Milliseconds |
| **S3 Glacier Flexible** | Archive, flexible retrieval | 99.99% | 90 days | Per GB + request | Minutes to hours |
| **S3 Glacier Deep Archive** | Long-term archive | 99.99% | 180 days | Per GB + request | Hours |
| **S3 Express One Zone** | Performance-critical workloads | 99.95% | 1 hour | None | Single-digit ms |

### Durability & Availability

```
All S3 storage classes provide 99.999999999% (11 9's) durability*
(*Except S3 One Zone classes - data in single AZ)

Availability SLA:
┌────────────────────────────────────────────────────────┐
│ Storage Class              │ Availability SLA          │
├────────────────────────────┼───────────────────────────┤
│ S3 Standard                │ 99.99%                    │
│ S3 Intelligent-Tiering     │ 99.9%                     │
│ S3 Standard-IA             │ 99.9%                     │
│ S3 One Zone-IA             │ 99.5%                     │
│ S3 Glacier Instant         │ 99.9%                     │
│ S3 Glacier Flexible        │ 99.99%                    │
│ S3 Glacier Deep Archive    │ 99.99%                    │
│ S3 Express One Zone        │ 99.95%                    │
└────────────────────────────┴───────────────────────────┘
```

---

## 1. S3 Standard

### Overview
The default storage class for frequently accessed data. Offers high durability, availability, and performance.

### Characteristics
- **Durability**: 99.999999999% (11 9's)
- **Availability**: 99.99%
- **Availability Zones**: >= 3
- **Minimum Storage Duration**: None
- **Minimum Object Size**: None
- **Retrieval Fee**: None

### Use Cases
- Websites and content distribution
- Mobile and gaming applications
- Big data analytics
- Frequently accessed data

### Pricing (US East - N. Virginia, as reference)
```
Storage:           $0.023 per GB/month (first 50 TB)
PUT/COPY/POST:     $0.005 per 1,000 requests
GET/SELECT:        $0.0004 per 1,000 requests
Data Retrieval:    Free
```

### CLI Example
```bash
# Upload with Standard storage class (default)
aws s3 cp myfile.txt s3://my-bucket/myfile.txt

# Explicitly specify Standard
aws s3 cp myfile.txt s3://my-bucket/myfile.txt --storage-class STANDARD
```

---

## 2. S3 Intelligent-Tiering

### Overview
Automatically moves data between access tiers based on changing access patterns, optimizing costs without performance impact.

### Access Tiers
```
┌─────────────────────────────────────────────────────────────────┐
│              S3 INTELLIGENT-TIERING TIERS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AUTOMATIC TIERS (No retrieval fees)                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Frequent Access Tier     - Objects accessed regularly       ││
│  │ Infrequent Access Tier   - After 30 days without access     ││
│  │ Archive Instant Access   - After 90 days without access     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  OPTIONAL TIERS (Must be enabled, async retrieval)              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Archive Access Tier      - After 90-730 days (configurable) ││
│  │ Deep Archive Access Tier - After 180-730 days (configurable)││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Characteristics
- **Durability**: 99.999999999%
- **Availability**: 99.9%
- **Minimum Storage Duration**: None
- **Minimum Object Size**: 128 KB (smaller objects stored but not monitored)
- **Monitoring Fee**: $0.0025 per 1,000 objects/month

### Use Cases
- Data with unknown or unpredictable access patterns
- Datasets with changing access over time
- Cost optimization without managing lifecycle policies

### Pricing
```
Frequent Access Tier:     Same as S3 Standard
Infrequent Access Tier:   Same as S3 Standard-IA
Archive Instant Access:   Same as S3 Glacier Instant Retrieval
Monitoring Fee:           $0.0025 per 1,000 objects/month
```

### CLI/SDK Example
```bash
# Upload to Intelligent-Tiering
aws s3 cp myfile.txt s3://my-bucket/ --storage-class INTELLIGENT_TIERING
```

```python
import boto3

s3_client = boto3.client('s3')

# Configure Intelligent-Tiering with optional archive tiers
s3_client.put_bucket_intelligent_tiering_configuration(
    Bucket='my-bucket',
    Id='my-tiering-config',
    IntelligentTieringConfiguration={
        'Id': 'my-tiering-config',
        'Status': 'Enabled',
        'Tierings': [
            {
                'Days': 90,
                'AccessTier': 'ARCHIVE_ACCESS'
            },
            {
                'Days': 180,
                'AccessTier': 'DEEP_ARCHIVE_ACCESS'
            }
        ]
    }
)
```

---

## 3. S3 Standard-IA (Infrequent Access)

### Overview
For data accessed less frequently but requires rapid access when needed. Lower storage cost than Standard, but with a retrieval fee.

### Characteristics
- **Durability**: 99.999999999%
- **Availability**: 99.9%
- **Availability Zones**: >= 3
- **Minimum Storage Duration**: 30 days
- **Minimum Object Size**: 128 KB (charged for 128 KB minimum)
- **Retrieval Fee**: Per GB retrieved

### Use Cases
- Disaster recovery and backups
- Data that's accessed monthly
- Long-lived, less frequently accessed data

### Pricing
```
Storage:           $0.0125 per GB/month
PUT/COPY/POST:     $0.01 per 1,000 requests
GET/SELECT:        $0.001 per 1,000 requests
Data Retrieval:    $0.01 per GB
```

### CLI Example
```bash
# Upload to Standard-IA
aws s3 cp backup.zip s3://my-bucket/ --storage-class STANDARD_IA
```

### Important Considerations
```
⚠️ Minimum Storage Duration: 30 days
   - Deleting before 30 days: charged for full 30 days

⚠️ Minimum Object Size: 128 KB
   - Smaller objects charged as 128 KB

⚠️ Retrieval Costs
   - Factor in retrieval costs for access planning
```

---

## 4. S3 One Zone-IA

### Overview
Similar to Standard-IA but stores data in a single Availability Zone. 20% cheaper than Standard-IA.

### Characteristics
- **Durability**: 99.999999999% (within single AZ)
- **Availability**: 99.5%
- **Availability Zones**: 1
- **Minimum Storage Duration**: 30 days
- **Minimum Object Size**: 128 KB

### Use Cases
- Secondary backup copies
- Easily recreatable data
- Cross-region replication destination
- Development/test environments

### Pricing
```
Storage:           $0.01 per GB/month
Data Retrieval:    $0.01 per GB
```

### Risk Consideration
```
⚠️ RISK: If the AZ is destroyed, data is LOST
   - Not suitable for primary copies
   - Not suitable for compliance data
   - Use for recreatable or secondary copies only
```

### CLI Example
```bash
# Upload to One Zone-IA
aws s3 cp secondary-backup.zip s3://my-bucket/ --storage-class ONEZONE_IA
```

---

## 5. S3 Glacier Instant Retrieval

### Overview
Archive storage class with millisecond retrieval. Ideal for data accessed once per quarter.

### Characteristics
- **Durability**: 99.999999999%
- **Availability**: 99.9%
- **Minimum Storage Duration**: 90 days
- **Minimum Object Size**: 128 KB
- **First Byte Latency**: Milliseconds

### Use Cases
- Medical images
- News media assets
- User-generated content archives
- Data accessed once per quarter

### Pricing
```
Storage:           $0.004 per GB/month
Data Retrieval:    $0.03 per GB
PUT Requests:      $0.02 per 1,000
GET Requests:      $0.01 per 1,000
```

### CLI Example
```bash
aws s3 cp archive.zip s3://my-bucket/ --storage-class GLACIER_IR
```

---

## 6. S3 Glacier Flexible Retrieval

### Overview
Low-cost archive storage for data that doesn't require immediate access. Retrieval times from minutes to hours.

### Retrieval Options
```
┌─────────────────────────────────────────────────────────────────┐
│              GLACIER FLEXIBLE RETRIEVAL OPTIONS                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  EXPEDITED                                                      │
│  ├── Time: 1-5 minutes                                          │
│  ├── Cost: $0.03 per GB + $10.00 per 1,000 requests            │
│  └── Use: Urgent access to subset of archives                  │
│                                                                 │
│  STANDARD                                                       │
│  ├── Time: 3-5 hours                                            │
│  ├── Cost: $0.01 per GB + $0.05 per 1,000 requests             │
│  └── Use: Regular archive access                               │
│                                                                 │
│  BULK                                                           │
│  ├── Time: 5-12 hours                                           │
│  ├── Cost: $0.0025 per GB + $0.025 per 1,000 requests          │
│  └── Use: Large-scale data retrieval, petabytes                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Characteristics
- **Durability**: 99.999999999%
- **Availability**: 99.99%
- **Minimum Storage Duration**: 90 days
- **Minimum Object Size**: 40 KB (charged minimum)

### Use Cases
- Long-term backups
- Disaster recovery data
- Compliance archives

### Pricing
```
Storage:           $0.0036 per GB/month
```

### Restore and Access

```bash
# Initiate restore (Standard tier, available for 7 days)
aws s3api restore-object \
    --bucket my-bucket \
    --key archive/large-file.zip \
    --restore-request '{"Days":7,"GlacierJobParameters":{"Tier":"Standard"}}'

# Check restore status
aws s3api head-object --bucket my-bucket --key archive/large-file.zip
# Look for: "Restore": "ongoing-request=\"false\", expiry-date=\"...\""

# Download after restore completes
aws s3 cp s3://my-bucket/archive/large-file.zip ./
```

```python
import boto3

s3_client = boto3.client('s3')

# Initiate restore
s3_client.restore_object(
    Bucket='my-bucket',
    Key='archive/large-file.zip',
    RestoreRequest={
        'Days': 7,
        'GlacierJobParameters': {
            'Tier': 'Standard'  # 'Expedited', 'Standard', or 'Bulk'
        }
    }
)

# Check restore status
response = s3_client.head_object(Bucket='my-bucket', Key='archive/large-file.zip')
restore_status = response.get('Restore', 'No restore in progress')
print(f"Restore status: {restore_status}")
```

---

## 7. S3 Glacier Deep Archive

### Overview
Lowest-cost storage class for long-term archive. Data retrieval takes 12-48 hours.

### Retrieval Options
```
STANDARD:   Within 12 hours
BULK:       Within 48 hours (lowest cost)
```

### Characteristics
- **Durability**: 99.999999999%
- **Availability**: 99.99%
- **Minimum Storage Duration**: 180 days
- **Minimum Object Size**: 40 KB

### Use Cases
- Regulatory compliance archives (7-10 year retention)
- Financial records
- Healthcare records
- Media asset preservation

### Pricing
```
Storage:           $0.00099 per GB/month (less than $1 per TB/month!)
Standard Retrieval: $0.02 per GB
Bulk Retrieval:     $0.0025 per GB
```

### CLI Example
```bash
# Upload to Glacier Deep Archive
aws s3 cp compliance-archive.zip s3://my-bucket/ --storage-class DEEP_ARCHIVE

# Restore with Bulk tier (48 hours)
aws s3api restore-object \
    --bucket my-bucket \
    --key compliance-archive.zip \
    --restore-request '{"Days":30,"GlacierJobParameters":{"Tier":"Bulk"}}'
```

---

## 8. S3 Express One Zone

### Overview
High-performance, single-AZ storage class with single-digit millisecond latency. Introduced in late 2023.

### Characteristics
- **Durability**: 99.999999999% (within single AZ)
- **Availability**: 99.95%
- **First Byte Latency**: Single-digit milliseconds
- **Request Performance**: 10x faster than S3 Standard
- **Storage Type**: Directory bucket (different from general purpose)

### Use Cases
- Machine learning training
- Interactive analytics
- Media content creation
- High-frequency trading data
- Real-time data processing

### Key Differences
```
S3 Express One Zone uses DIRECTORY BUCKETS:
- Bucket name format: bucket-name--azid--x-s3
- Example: my-data--use1-az4--x-s3
- Different API endpoint
- Session-based authentication for performance
```

### Pricing
```
Storage:           $0.16 per GB/month
PUT/COPY/POST:     $0.0025 per 1,000 requests
GET/SELECT:        $0.0002 per 1,000 requests
```

### CLI Example
```bash
# Create directory bucket
aws s3api create-bucket \
    --bucket my-express-bucket--use1-az4--x-s3 \
    --create-bucket-configuration '{"Location":{"Type":"AvailabilityZone","Name":"use1-az4"},"Bucket":{"Type":"Directory","DataRedundancy":"SingleAvailabilityZone"}}'
```

---

## Cost Comparison Calculator

### Sample: 1 TB of Data for 1 Year

```
Assumptions:
- 1 TB (1,024 GB) stored for 12 months
- Varying access patterns

┌─────────────────────────────────────────────────────────────────────────┐
│                    ANNUAL COST COMPARISON (1 TB)                        │
├─────────────────────────┬───────────────┬──────────────┬────────────────┤
│ Storage Class           │ Storage Cost  │ Savings vs   │ Best For       │
│                         │ (per year)    │ Standard     │                │
├─────────────────────────┼───────────────┼──────────────┼────────────────┤
│ S3 Standard             │ $282.62       │ -            │ Frequent access│
│ S3 Standard-IA          │ $153.60       │ 46%          │ Monthly access │
│ S3 One Zone-IA          │ $122.88       │ 57%          │ Recreatable    │
│ S3 Glacier Instant      │ $49.15        │ 83%          │ Quarterly      │
│ S3 Glacier Flexible     │ $44.24        │ 84%          │ Archive        │
│ S3 Glacier Deep Archive │ $12.17        │ 96%          │ Long-term      │
└─────────────────────────┴───────────────┴──────────────┴────────────────┘

Note: Does not include retrieval costs, request costs, or data transfer
```

### Total Cost of Ownership Formula

```
Total Monthly Cost = Storage Cost + Request Costs + Retrieval Costs + Data Transfer

Where:
- Storage Cost = (GB stored) x (price per GB/month)
- Request Costs = (PUT requests x PUT price) + (GET requests x GET price)
- Retrieval Costs = (GB retrieved) x (retrieval price per GB)
- Data Transfer = (GB transferred out) x (transfer price per GB)
```

### Python Cost Calculator

```python
def calculate_s3_cost(storage_gb, put_requests, get_requests,
                       retrieval_gb=0, storage_class='STANDARD'):
    """
    Calculate monthly S3 costs for different storage classes.
    Prices are for US East (N. Virginia) as reference.
    """

    pricing = {
        'STANDARD': {
            'storage': 0.023,
            'put': 0.005 / 1000,
            'get': 0.0004 / 1000,
            'retrieval': 0
        },
        'STANDARD_IA': {
            'storage': 0.0125,
            'put': 0.01 / 1000,
            'get': 0.001 / 1000,
            'retrieval': 0.01
        },
        'ONEZONE_IA': {
            'storage': 0.01,
            'put': 0.01 / 1000,
            'get': 0.001 / 1000,
            'retrieval': 0.01
        },
        'GLACIER_IR': {
            'storage': 0.004,
            'put': 0.02 / 1000,
            'get': 0.01 / 1000,
            'retrieval': 0.03
        },
        'GLACIER': {
            'storage': 0.0036,
            'put': 0.03 / 1000,
            'get': 0.0004 / 1000,
            'retrieval': 0.01  # Standard tier
        },
        'DEEP_ARCHIVE': {
            'storage': 0.00099,
            'put': 0.05 / 1000,
            'get': 0.0004 / 1000,
            'retrieval': 0.02  # Standard tier
        }
    }

    p = pricing.get(storage_class, pricing['STANDARD'])

    storage_cost = storage_gb * p['storage']
    put_cost = put_requests * p['put']
    get_cost = get_requests * p['get']
    retrieval_cost = retrieval_gb * p['retrieval']

    total = storage_cost + put_cost + get_cost + retrieval_cost

    return {
        'storage_class': storage_class,
        'storage_cost': round(storage_cost, 2),
        'put_cost': round(put_cost, 2),
        'get_cost': round(get_cost, 2),
        'retrieval_cost': round(retrieval_cost, 2),
        'total_monthly': round(total, 2)
    }

# Example: Compare costs for 500 GB with 10K PUTs, 100K GETs, 50 GB retrieval
storage_classes = ['STANDARD', 'STANDARD_IA', 'GLACIER_IR', 'DEEP_ARCHIVE']

for sc in storage_classes:
    result = calculate_s3_cost(
        storage_gb=500,
        put_requests=10000,
        get_requests=100000,
        retrieval_gb=50,
        storage_class=sc
    )
    print(f"{sc}: ${result['total_monthly']}/month")
```

---

## Storage Class Selection Decision Tree

```
                            ┌─────────────────────────────┐
                            │   How often is data        │
                            │   accessed?                │
                            └─────────────┬───────────────┘
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              │                           │                           │
              ▼                           ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
    │  Frequently     │         │  Infrequently   │         │  Rarely/Never   │
    │  (daily/weekly) │         │  (monthly)      │         │  (archive)      │
    └────────┬────────┘         └────────┬────────┘         └────────┬────────┘
             │                           │                           │
             ▼                           ▼                           │
    ┌─────────────────┐         ┌─────────────────┐                  │
    │ Access pattern  │         │ Is data easily  │                  │
    │ predictable?    │         │ recreatable?    │                  │
    └────────┬────────┘         └────────┬────────┘                  │
             │                           │                           │
      ┌──────┴──────┐             ┌──────┴──────┐                    │
      │             │             │             │                    │
      ▼             ▼             ▼             ▼                    │
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐              │
│    YES    │ │    NO     │ │    YES    │ │    NO     │              │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘              │
      │             │             │             │                    │
      ▼             ▼             ▼             ▼                    │
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐              │
│    S3     │ │    S3     │ │  One Zone │ │ Standard  │              │
│ Standard  │ │Intelligent│ │    IA     │ │    IA     │              │
└───────────┘ │ Tiering   │ └───────────┘ └───────────┘              │
              └───────────┘                                          │
                                                                     │
                            ┌────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ Need immediate  │
                  │ access when     │
                  │ retrieved?      │
                  └────────┬────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     ┌─────────────────┐       ┌─────────────────┐
     │       YES       │       │       NO        │
     └────────┬────────┘       └────────┬────────┘
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ Glacier Instant │       │ How long until  │
    │   Retrieval     │       │ needed?         │
    └─────────────────┘       └────────┬────────┘
                                       │
                       ┌───────────────┴───────────────┐
                       │                               │
                       ▼                               ▼
              ┌─────────────────┐             ┌─────────────────┐
              │  Minutes/Hours  │             │   12-48 hours   │
              │    is okay      │             │   is okay       │
              └────────┬────────┘             └────────┬────────┘
                       │                               │
                       ▼                               ▼
              ┌─────────────────┐             ┌─────────────────┐
              │ Glacier Flexible│             │ Glacier Deep    │
              │   Retrieval     │             │   Archive       │
              └─────────────────┘             └─────────────────┘
```

---

## Changing Storage Classes

### Methods to Change Storage Class

1. **During Upload**
```bash
aws s3 cp file.txt s3://my-bucket/ --storage-class STANDARD_IA
```

2. **Copy to Same Location with New Class**
```bash
aws s3 cp s3://my-bucket/file.txt s3://my-bucket/file.txt --storage-class GLACIER_IR
```

3. **Using Lifecycle Policies** (Recommended for automation)
```json
{
    "Rules": [
        {
            "ID": "Move to IA after 30 days",
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
                    "StorageClass": "GLACIER_IR"
                },
                {
                    "Days": 365,
                    "StorageClass": "DEEP_ARCHIVE"
                }
            ]
        }
    ]
}
```

### Storage Class Transition Constraints

```
Valid transitions (can only move DOWN this list):

S3 Standard
    ↓
S3 Intelligent-Tiering
    ↓
S3 Standard-IA / S3 One Zone-IA
    ↓
S3 Glacier Instant Retrieval
    ↓
S3 Glacier Flexible Retrieval
    ↓
S3 Glacier Deep Archive

⚠️ Cannot transition directly from:
   - Glacier → Standard (must restore first)
   - One Zone-IA → Standard-IA
```

---

## S3 Storage Lens

S3 Storage Lens provides visibility into storage usage and activity trends across your organization.

### Key Metrics
```
- Total storage by storage class
- Request activity patterns
- Cost by bucket and storage class
- Error rates
- Data transfer analysis
```

### Enabling Storage Lens
```bash
# Create default dashboard
aws s3control put-storage-lens-configuration \
    --account-id 123456789012 \
    --config-id my-dashboard \
    --storage-lens-configuration '{
        "Id": "my-dashboard",
        "IsEnabled": true,
        "AccountLevel": {
            "ActivityMetrics": {"IsEnabled": true},
            "BucketLevel": {}
        }
    }'
```

---

## Best Practices

### 1. Use Intelligent-Tiering for Unknown Patterns
```
If you're unsure about access patterns, start with Intelligent-Tiering.
The small monitoring fee is worth the automatic optimization.
```

### 2. Set Up Lifecycle Policies
```
Automate transitions rather than manual storage class changes.
This ensures consistent cost optimization across all objects.
```

### 3. Consider Minimum Durations
```
Standard-IA/One Zone-IA: 30 days minimum
Glacier Instant: 90 days minimum
Glacier Flexible: 90 days minimum
Deep Archive: 180 days minimum

Delete before minimum = charged for full duration
```

### 4. Factor in Retrieval Costs
```
For frequently accessed data, Standard might be cheaper than IA classes
even though the storage cost is higher.

Break-even calculation:
If retrieval_cost > (Standard_storage - IA_storage), use Standard
```

### 5. Use S3 Analytics
```
Enable S3 Analytics to get recommendations on when to transition
objects to less expensive storage classes.
```

---

## Summary

| Storage Class | Monthly Cost (per GB) | Best For |
|--------------|----------------------|----------|
| Standard | $0.023 | Frequent access |
| Intelligent-Tiering | Variable | Unknown patterns |
| Standard-IA | $0.0125 | Infrequent, multi-AZ |
| One Zone-IA | $0.01 | Infrequent, recreatable |
| Glacier Instant | $0.004 | Archive, instant access |
| Glacier Flexible | $0.0036 | Archive, hours retrieval |
| Deep Archive | $0.00099 | Long-term, days retrieval |

---

## Next Steps

Continue to [03-bucket-policies.md](./03-bucket-policies.md) to learn about securing your S3 buckets with policies and access controls.
