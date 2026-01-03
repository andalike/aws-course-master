# 01 - S3 Fundamentals

## Introduction

Amazon S3 (Simple Storage Service) is an object storage service that offers industry-leading scalability, data availability, security, and performance. Unlike traditional file systems that organize data hierarchically, S3 uses a flat structure where objects are stored in buckets.

---

## Core Concepts

### What is Object Storage?

Object storage manages data as objects, unlike file systems (hierarchical) or block storage (fixed-size blocks). Each object includes:

```
┌────────────────────────────────────────────────────────┐
│                       OBJECT                           │
├────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │     KEY      │  │    VALUE     │  │   METADATA   │  │
│  │              │  │              │  │              │  │
│  │ Unique       │  │ The actual   │  │ System +     │  │
│  │ identifier   │  │ data (file)  │  │ User-defined │  │
│  │ (path/name)  │  │ up to 5TB    │  │ attributes   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────┘
```

### S3 vs. Other Storage Types

| Feature | S3 (Object) | EBS (Block) | EFS (File) |
|---------|-------------|-------------|------------|
| Structure | Flat | Volumes | Hierarchical |
| Max Size | 5 TB per object | 64 TB per volume | Petabytes |
| Access | HTTP/HTTPS | EC2 only | NFS (EC2, on-prem) |
| Latency | Milliseconds | Microseconds | Milliseconds |
| Use Case | Web content, backups | Databases, OS | Shared file systems |

---

## Buckets

### What is a Bucket?

A bucket is a container for objects stored in S3. Every object is contained in a bucket. Buckets serve as the top-level namespace for S3.

```
Amazon S3 Global Namespace
│
├── bucket-name-1 (us-east-1)
│   ├── images/logo.png
│   ├── images/banner.jpg
│   └── documents/report.pdf
│
├── bucket-name-2 (eu-west-1)
│   ├── data/file1.csv
│   └── data/file2.csv
│
└── bucket-name-3 (ap-southeast-1)
    └── backup/db-snapshot.bak
```

### Bucket Properties

| Property | Description |
|----------|-------------|
| **Name** | Globally unique across ALL AWS accounts |
| **Region** | Physical location where bucket is created |
| **Objects** | Unlimited number and total size |
| **Flat Structure** | No true directories (prefixes simulate folders) |

### Bucket Naming Rules

Bucket names must follow these rules:

```
✓ VALID Names:
  - my-bucket-name
  - mybucket123
  - 2024-data-archive
  - my.bucket.name (not recommended for website hosting)

✗ INVALID Names:
  - MyBucket (uppercase)
  - my_bucket (underscore)
  - my bucket (space)
  - -mybucket (starts with hyphen)
  - mybucket- (ends with hyphen)
  - 192.168.1.1 (IP format)
  - ab (less than 3 characters)
  - verylongbucketnamethatexceedssixtythreecharacterslimit (>63 chars)
```

**Complete Rules:**
1. 3-63 characters long
2. Only lowercase letters, numbers, and hyphens
3. Must start with letter or number
4. Cannot end with hyphen
5. Cannot contain consecutive periods
6. Cannot be formatted as IP address
7. Must be unique across ALL AWS accounts globally

### Creating Buckets

#### AWS CLI

```bash
# Create bucket in default region
aws s3 mb s3://my-unique-bucket-name-2024

# Create bucket in specific region
aws s3 mb s3://my-unique-bucket-name-2024 --region eu-west-1

# Verify bucket creation
aws s3 ls
```

#### Python (Boto3)

```python
import boto3
from botocore.exceptions import ClientError

def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region."""
    try:
        if region is None or region == 'us-east-1':
            # us-east-1 doesn't require LocationConstraint
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location
            )
        print(f"Bucket '{bucket_name}' created successfully")
        return True
    except ClientError as e:
        print(f"Error: {e}")
        return False

# Usage
create_bucket('my-unique-bucket-name-2024', 'us-west-2')
```

#### Node.js (AWS SDK v3)

```javascript
import { S3Client, CreateBucketCommand } from "@aws-sdk/client-s3";

const s3Client = new S3Client({ region: "us-west-2" });

async function createBucket(bucketName) {
    try {
        const command = new CreateBucketCommand({
            Bucket: bucketName,
            CreateBucketConfiguration: {
                LocationConstraint: "us-west-2"
            }
        });

        const response = await s3Client.send(command);
        console.log(`Bucket created: ${bucketName}`);
        return response;
    } catch (error) {
        console.error("Error creating bucket:", error);
        throw error;
    }
}

// Usage
createBucket("my-unique-bucket-name-2024");
```

---

## Objects

### What is an Object?

An object is the fundamental entity stored in S3. It consists of object data and metadata.

```
Object Components:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  KEY: "images/2024/january/photo.jpg"                      │
│                                                             │
│  VALUE: [Binary data - the actual file content]            │
│         Maximum size: 5 TB                                  │
│                                                             │
│  METADATA:                                                  │
│  ├── System Metadata (AWS managed)                          │
│  │   ├── Content-Type: image/jpeg                          │
│  │   ├── Content-Length: 1048576                           │
│  │   ├── Last-Modified: 2024-01-15T10:30:00Z               │
│  │   └── ETag: "d41d8cd98f00b204e9800998ecf8427e"          │
│  │                                                          │
│  └── User Metadata (Custom, x-amz-meta-* prefix)           │
│      ├── x-amz-meta-author: "John Doe"                     │
│      └── x-amz-meta-project: "Website Redesign"            │
│                                                             │
│  VERSION ID: "3sL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X"  │
│  (Only if versioning enabled)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Object Size Limits

| Upload Method | Minimum Size | Maximum Size |
|---------------|--------------|--------------|
| Single PUT | 0 bytes | 5 GB |
| Multipart Upload | 5 MB per part | 5 TB total |

**Recommendation:** Use multipart upload for objects larger than 100 MB.

### Uploading Objects

#### AWS CLI

```bash
# Upload single file
aws s3 cp myfile.txt s3://my-bucket/

# Upload with custom metadata
aws s3 cp myfile.txt s3://my-bucket/ \
    --metadata '{"author":"John Doe","project":"demo"}'

# Upload with specific content type
aws s3 cp image.png s3://my-bucket/ \
    --content-type "image/png"

# Upload entire directory
aws s3 cp ./my-folder s3://my-bucket/folder/ --recursive

# Sync directory (only uploads changed files)
aws s3 sync ./my-folder s3://my-bucket/folder/
```

#### Python (Boto3)

```python
import boto3

s3_client = boto3.client('s3')

# Upload file
s3_client.upload_file(
    'local_file.txt',
    'my-bucket',
    'folder/remote_file.txt',
    ExtraArgs={
        'ContentType': 'text/plain',
        'Metadata': {
            'author': 'John Doe',
            'project': 'demo'
        }
    }
)

# Upload with put_object (for small files or data in memory)
s3_client.put_object(
    Bucket='my-bucket',
    Key='folder/data.json',
    Body=b'{"key": "value"}',
    ContentType='application/json'
)

# Upload file with progress callback
from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,  # 8MB
    max_concurrency=10,
    multipart_chunksize=8 * 1024 * 1024,  # 8MB
    use_threads=True
)

def upload_progress(bytes_transferred):
    print(f"Uploaded: {bytes_transferred} bytes")

s3_client.upload_file(
    'large_file.zip',
    'my-bucket',
    'backups/large_file.zip',
    Config=config,
    Callback=upload_progress
)
```

#### Node.js (AWS SDK v3)

```javascript
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { readFileSync } from "fs";

const s3Client = new S3Client({ region: "us-east-1" });

async function uploadFile(bucketName, key, filePath) {
    const fileContent = readFileSync(filePath);

    const command = new PutObjectCommand({
        Bucket: bucketName,
        Key: key,
        Body: fileContent,
        ContentType: "application/octet-stream",
        Metadata: {
            "author": "John Doe",
            "project": "demo"
        }
    });

    try {
        const response = await s3Client.send(command);
        console.log("File uploaded successfully:", response.ETag);
        return response;
    } catch (error) {
        console.error("Error uploading file:", error);
        throw error;
    }
}

// Usage
uploadFile("my-bucket", "folder/file.txt", "./local-file.txt");
```

---

## Keys and Prefixes

### Understanding Keys

A key is the unique identifier for an object within a bucket. The full path is the key.

```
Bucket: my-photos-bucket

Objects and their Keys:
├── vacation/2024/beach.jpg          Key: "vacation/2024/beach.jpg"
├── vacation/2024/mountain.jpg       Key: "vacation/2024/mountain.jpg"
├── vacation/2023/sunset.jpg         Key: "vacation/2023/sunset.jpg"
├── profile.png                      Key: "profile.png"
└── documents/resume.pdf             Key: "documents/resume.pdf"
```

### Prefixes (Virtual Folders)

S3 has a flat structure - there are no real folders. The "/" in keys creates the illusion of hierarchy.

```
Key: "images/photos/2024/january/photo.jpg"

├── images/                    ← Prefix
│   └── photos/                ← Prefix
│       └── 2024/              ← Prefix
│           └── january/       ← Prefix
│               └── photo.jpg  ← Object name
```

#### Listing Objects by Prefix

```bash
# List all objects with prefix "images/"
aws s3 ls s3://my-bucket/images/

# List only immediate "folders" (CommonPrefixes)
aws s3 ls s3://my-bucket/images/ --delimiter /
```

```python
import boto3

s3_client = boto3.client('s3')

# List objects with prefix
response = s3_client.list_objects_v2(
    Bucket='my-bucket',
    Prefix='images/2024/',
    Delimiter='/'
)

# Get "folders" (common prefixes)
for prefix in response.get('CommonPrefixes', []):
    print(f"Folder: {prefix['Prefix']}")

# Get objects
for obj in response.get('Contents', []):
    print(f"Object: {obj['Key']}, Size: {obj['Size']}")
```

---

## S3 Regions

### Region Selection Considerations

| Factor | Consideration |
|--------|--------------|
| **Latency** | Choose region closest to users |
| **Compliance** | Data residency requirements |
| **Cost** | Pricing varies by region |
| **Services** | Not all services available in all regions |
| **Disaster Recovery** | Use multiple regions for resilience |

### Available Regions (Sample)

```
US Regions:
├── us-east-1      (N. Virginia) - Default, most services
├── us-east-2      (Ohio)
├── us-west-1      (N. California)
└── us-west-2      (Oregon)

Europe Regions:
├── eu-west-1      (Ireland)
├── eu-west-2      (London)
├── eu-central-1   (Frankfurt)
└── eu-north-1     (Stockholm)

Asia Pacific:
├── ap-southeast-1 (Singapore)
├── ap-southeast-2 (Sydney)
├── ap-northeast-1 (Tokyo)
└── ap-south-1     (Mumbai)
```

### S3 Endpoint URLs

```
Virtual-hosted-style (Recommended):
https://bucket-name.s3.region.amazonaws.com/key-name

Path-style (Legacy):
https://s3.region.amazonaws.com/bucket-name/key-name

Examples:
https://my-photos.s3.us-east-1.amazonaws.com/vacation/beach.jpg
https://my-photos.s3.eu-west-1.amazonaws.com/vacation/beach.jpg
```

---

## S3 Consistency Model

### Strong Read-After-Write Consistency

As of December 2020, S3 provides **strong read-after-write consistency** for all operations.

```
Timeline:
────────────────────────────────────────────────────────────────►
    │                    │                    │
    ▼                    ▼                    ▼
 PUT object         GET object           DELETE object
 (upload)           (immediately         (delete)
                    sees new data)            │
                                              ▼
                                         GET object
                                         (immediately
                                         returns 404)
```

### What This Means

| Operation | Guarantee |
|-----------|-----------|
| **PUT (new object)** | Subsequent reads immediately return new object |
| **PUT (overwrite)** | Subsequent reads immediately return updated object |
| **DELETE** | Subsequent reads immediately return 404 |
| **LIST** | Reflects all successful write operations |

### Consistency Examples

```python
import boto3

s3_client = boto3.client('s3')

# Example 1: Write then Read (always consistent)
s3_client.put_object(
    Bucket='my-bucket',
    Key='test.txt',
    Body=b'Hello World'
)

# Immediately read - will ALWAYS return "Hello World"
response = s3_client.get_object(
    Bucket='my-bucket',
    Key='test.txt'
)
print(response['Body'].read())  # b'Hello World' - guaranteed

# Example 2: Update then Read (always consistent)
s3_client.put_object(
    Bucket='my-bucket',
    Key='test.txt',
    Body=b'Updated Content'
)

# Immediately read - will ALWAYS return "Updated Content"
response = s3_client.get_object(
    Bucket='my-bucket',
    Key='test.txt'
)
print(response['Body'].read())  # b'Updated Content' - guaranteed
```

---

## S3 Object URL Formats

### URL Structures

```
1. Virtual-hosted-style URL (Recommended):
   https://bucket-name.s3.region.amazonaws.com/key-name
   https://my-bucket.s3.us-east-1.amazonaws.com/images/photo.jpg

2. Virtual-hosted-style URL (Legacy, region implied):
   https://bucket-name.s3.amazonaws.com/key-name
   https://my-bucket.s3.amazonaws.com/images/photo.jpg

3. Path-style URL (Deprecated for new buckets):
   https://s3.region.amazonaws.com/bucket-name/key-name
   https://s3.us-east-1.amazonaws.com/my-bucket/images/photo.jpg

4. S3 Access Point URL:
   https://access-point-name-account-id.s3-accesspoint.region.amazonaws.com/key-name

5. S3 Website Endpoint:
   http://bucket-name.s3-website-region.amazonaws.com
   http://bucket-name.s3-website.region.amazonaws.com
```

### Getting Object URLs

```python
import boto3
from botocore.config import Config

# Create client with specific signature version
s3_client = boto3.client(
    's3',
    region_name='us-east-1',
    config=Config(signature_version='s3v4')
)

# Generate URL for an object
bucket_name = 'my-bucket'
object_key = 'images/photo.jpg'
region = 'us-east-1'

# Construct URL manually
url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"
print(f"Object URL: {url}")

# For public objects, this URL works directly
# For private objects, you need presigned URLs (covered in later section)
```

---

## Common S3 Operations

### List Buckets

```bash
# AWS CLI
aws s3 ls
```

```python
import boto3

s3_client = boto3.client('s3')
response = s3_client.list_buckets()

for bucket in response['Buckets']:
    print(f"Bucket: {bucket['Name']}, Created: {bucket['CreationDate']}")
```

### List Objects

```bash
# AWS CLI - Simple listing
aws s3 ls s3://my-bucket/

# With details
aws s3 ls s3://my-bucket/ --recursive --human-readable --summarize
```

```python
import boto3

s3_client = boto3.client('s3')

# List all objects (handles pagination)
paginator = s3_client.get_paginator('list_objects_v2')

for page in paginator.paginate(Bucket='my-bucket'):
    for obj in page.get('Contents', []):
        print(f"Key: {obj['Key']}, Size: {obj['Size']}, Modified: {obj['LastModified']}")
```

### Download Objects

```bash
# AWS CLI
aws s3 cp s3://my-bucket/file.txt ./local-file.txt

# Download directory
aws s3 cp s3://my-bucket/folder/ ./local-folder/ --recursive
```

```python
import boto3

s3_client = boto3.client('s3')

# Download file
s3_client.download_file('my-bucket', 'file.txt', 'local-file.txt')

# Download with get_object (for processing in memory)
response = s3_client.get_object(Bucket='my-bucket', Key='data.json')
data = response['Body'].read().decode('utf-8')
print(data)
```

### Delete Objects

```bash
# AWS CLI - Single object
aws s3 rm s3://my-bucket/file.txt

# Delete all objects with prefix
aws s3 rm s3://my-bucket/folder/ --recursive

# Delete bucket (must be empty)
aws s3 rb s3://my-bucket

# Delete bucket and all contents
aws s3 rb s3://my-bucket --force
```

```python
import boto3

s3_client = boto3.client('s3')

# Delete single object
s3_client.delete_object(Bucket='my-bucket', Key='file.txt')

# Delete multiple objects
s3_client.delete_objects(
    Bucket='my-bucket',
    Delete={
        'Objects': [
            {'Key': 'file1.txt'},
            {'Key': 'file2.txt'},
            {'Key': 'folder/file3.txt'}
        ]
    }
)
```

### Copy Objects

```bash
# AWS CLI - Copy within S3
aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/file.txt

# Copy with new storage class
aws s3 cp s3://my-bucket/file.txt s3://my-bucket/file.txt \
    --storage-class STANDARD_IA
```

```python
import boto3

s3_client = boto3.client('s3')

# Copy object
s3_client.copy_object(
    CopySource={'Bucket': 'source-bucket', 'Key': 'source-key'},
    Bucket='dest-bucket',
    Key='dest-key'
)

# Copy with metadata
s3_client.copy_object(
    CopySource={'Bucket': 'my-bucket', 'Key': 'file.txt'},
    Bucket='my-bucket',
    Key='file.txt',
    Metadata={'new-key': 'new-value'},
    MetadataDirective='REPLACE'  # Use 'COPY' to keep original metadata
)
```

---

## Best Practices

### Bucket Naming
- Use lowercase letters, numbers, and hyphens
- Include purpose and environment: `myapp-prod-data`, `myapp-dev-logs`
- Avoid personal or sensitive information in names

### Object Key Design
- Use meaningful prefixes for organization
- Consider access patterns for prefix design
- Avoid sequential prefixes for high-throughput scenarios

### Security
- Enable Block Public Access by default
- Use bucket policies for access control
- Enable server-side encryption
- Enable access logging

### Cost Optimization
- Use appropriate storage classes
- Implement lifecycle policies
- Clean up incomplete multipart uploads
- Monitor with S3 Storage Lens

---

## Summary

| Concept | Key Points |
|---------|------------|
| **Bucket** | Container for objects, globally unique name, region-specific |
| **Object** | File + metadata, up to 5TB, identified by key |
| **Key** | Unique identifier within bucket, full path including "folders" |
| **Prefix** | Virtual folder structure, "/" delimiter |
| **Consistency** | Strong read-after-write for all operations |
| **URLs** | Virtual-hosted style recommended |

---

## Next Steps

Continue to [02-storage-classes.md](./02-storage-classes.md) to learn about S3 Storage Classes and cost optimization strategies.
