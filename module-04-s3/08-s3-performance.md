# S3 Performance Optimization

## Table of Contents
1. [Understanding S3 Performance](#understanding-s3-performance)
2. [Transfer Acceleration](#transfer-acceleration)
3. [Multipart Uploads](#multipart-uploads)
4. [S3 Select and Glacier Select](#s3-select-and-glacier-select)
5. [Byte-Range Fetches](#byte-range-fetches)
6. [Prefix Optimization](#prefix-optimization)
7. [Caching Strategies](#caching-strategies)
8. [Practical Examples](#practical-examples)
9. [Performance Benchmarking](#performance-benchmarking)
10. [Best Practices](#best-practices)

---

## Understanding S3 Performance

### S3 Performance Baseline

Amazon S3 provides impressive baseline performance that scales automatically:

```
+-----------------------------------------------+
|           S3 Performance Limits               |
+-----------------------------------------------+
| Per Prefix:                                   |
|   - 3,500 PUT/COPY/POST/DELETE requests/sec   |
|   - 5,500 GET/HEAD requests/sec               |
+-----------------------------------------------+
| Per Object:                                   |
|   - Max object size: 5 TB                     |
|   - Single PUT limit: 5 GB                    |
|   - Recommended multipart: > 100 MB           |
+-----------------------------------------------+
```

### Performance Architecture

```
                         Internet
                            |
                            v
+----------------------------------------------------------+
|                    AWS Global Network                     |
+----------------------------------------------------------+
       |                    |                    |
       v                    v                    v
+-------------+     +-------------+     +-------------+
| CloudFront  |     | Transfer    |     | Direct S3   |
| Edge        |     | Acceleration|     | Endpoint    |
| Locations   |     | Endpoints   |     |             |
+-------------+     +-------------+     +-------------+
       |                    |                    |
       +--------------------+--------------------+
                            |
                            v
                    +---------------+
                    |   S3 Bucket   |
                    +---------------+
```

### Key Performance Factors

| Factor | Impact | Optimization |
|--------|--------|--------------|
| **Network Latency** | High for distant regions | Transfer Acceleration |
| **Object Size** | Large files need special handling | Multipart uploads |
| **Request Pattern** | Hot partitions slow down | Prefix distribution |
| **Data Format** | Full object downloads waste bandwidth | S3 Select |
| **Concurrency** | Sequential operations are slow | Parallel requests |

---

## Transfer Acceleration

### How Transfer Acceleration Works

S3 Transfer Acceleration uses CloudFront's globally distributed edge locations to accelerate uploads and downloads over long distances.

```
Without Transfer Acceleration:
+--------+                                        +-----------+
| Client |------------ Long Distance ----------->| S3 Bucket |
| Tokyo  |          (High Latency)               | Virginia  |
+--------+                                        +-----------+
         Latency: ~200-300ms per request

With Transfer Acceleration:
+--------+     +----------------+                 +-----------+
| Client |---->| CloudFront     |--- AWS ------->| S3 Bucket |
| Tokyo  |     | Edge (Tokyo)   |   Backbone     | Virginia  |
+--------+     +----------------+                 +-----------+
   ~20ms           Optimized Network Path

Total improvement: 50-500% faster uploads
```

### Enabling Transfer Acceleration

```bash
# Enable Transfer Acceleration on a bucket
aws s3api put-bucket-accelerate-configuration \
    --bucket my-bucket \
    --accelerate-configuration Status=Enabled

# Verify configuration
aws s3api get-bucket-accelerate-configuration \
    --bucket my-bucket
```

### Using Accelerated Endpoints

```bash
# Standard endpoint
aws s3 cp large-file.zip s3://my-bucket/ \
    --endpoint-url https://my-bucket.s3.us-east-1.amazonaws.com

# Accelerated endpoint
aws s3 cp large-file.zip s3://my-bucket/ \
    --endpoint-url https://my-bucket.s3-accelerate.amazonaws.com
```

### Python SDK Example

```python
import boto3
from boto3.s3.transfer import TransferConfig

# Create S3 client with transfer acceleration
s3_client = boto3.client(
    's3',
    config=boto3.session.Config(
        s3={'use_accelerate_endpoint': True}
    )
)

# Upload with acceleration
s3_client.upload_file(
    'large-file.zip',
    'my-bucket',
    'large-file.zip'
)

# Or configure per-request
s3_client.upload_file(
    'large-file.zip',
    'my-bucket',
    'large-file.zip',
    ExtraArgs={'ACL': 'private'},
    Config=TransferConfig(use_threads=True)
)
```

### When to Use Transfer Acceleration

```
+--------------------------------+--------------------------------+
|         USE When:              |        SKIP When:              |
+--------------------------------+--------------------------------+
| - Uploading from far regions   | - Same-region uploads          |
| - Need consistent fast uploads | - Small files (< 1MB)          |
| - Global user base uploading   | - VPC endpoint available       |
| - Time-sensitive large files   | - Cost is primary concern      |
+--------------------------------+--------------------------------+
```

### Speed Comparison Tool

AWS provides a speed comparison tool to test if acceleration helps:

```bash
# Test acceleration benefit
curl -s http://s3-accelerate-speedtest.s3-accelerate.amazonaws.com/en/accelerate-speed-comparsion.html
```

### Cost Comparison

```
Transfer Acceleration Pricing (example):
+---------------------------+------------------+------------------+
|      Transfer Type        |   Standard       |   Accelerated    |
+---------------------------+------------------+------------------+
| Data Transfer OUT         | $0.09/GB         | $0.09/GB         |
| Acceleration Fee (US/EU)  | N/A              | +$0.04/GB        |
| Acceleration Fee (Other)  | N/A              | +$0.08/GB        |
+---------------------------+------------------+------------------+

Note: You only pay if acceleration is faster than standard transfer
```

---

## Multipart Uploads

### When to Use Multipart

```
Object Size Guidelines:
+------------------+------------------------+
|    File Size     |     Recommendation     |
+------------------+------------------------+
| < 100 MB         | Single PUT request     |
| 100 MB - 5 GB    | Multipart recommended  |
| > 5 GB           | Multipart REQUIRED     |
+------------------+------------------------+
```

### How Multipart Works

```
5 GB File Upload Process:
+-------------------------------------------------------+
|                    Original File (5 GB)               |
+-------------------------------------------------------+
          |              |              |              |
          v              v              v              v
     +--------+     +--------+     +--------+     +--------+
     | Part 1 |     | Part 2 |     | Part 3 |     | Part N |
     | 100 MB |     | 100 MB |     | 100 MB |     | ...    |
     +--------+     +--------+     +--------+     +--------+
          |              |              |              |
          |    Parallel Upload (concurrent streams)    |
          v              v              v              v
     +-------------------------------------------------------+
     |                    S3 Bucket                          |
     |  (Assembles parts into complete object on completion) |
     +-------------------------------------------------------+

Benefits:
- Parallel upload = faster throughput
- Retry individual parts on failure
- Pause and resume capability
- Upload before knowing total size
```

### Multipart Upload Steps

```
1. Initiate Multipart Upload
   +--------+                    +--------+
   | Client | --- Initiate ----> |   S3   |
   +--------+   Multipart        +--------+
                                     |
                              Upload ID returned

2. Upload Parts (Parallel)
   +--------+     Part 1         +--------+
   | Client | -----------------> |   S3   |
   +--------+     Part 2         +--------+
              ----------------->
                  Part 3
              ----------------->
                                     |
                              ETags returned for each part

3. Complete Multipart Upload
   +--------+     List of        +--------+
   | Client | --- Parts+ETags -> |   S3   |
   +--------+                    +--------+
                                     |
                              Object assembled
```

### CLI Multipart Configuration

```bash
# Configure AWS CLI multipart settings
aws configure set default.s3.multipart_threshold 64MB
aws configure set default.s3.multipart_chunksize 16MB
aws configure set default.s3.max_concurrent_requests 20

# View current configuration
aws configure get default.s3.multipart_threshold

# Upload with custom multipart settings
aws s3 cp large-file.zip s3://my-bucket/ \
    --expected-size 5368709120
```

### Python SDK Multipart Example

```python
import boto3
from boto3.s3.transfer import TransferConfig

s3_client = boto3.client('s3')

# Configure multipart settings
config = TransferConfig(
    multipart_threshold=100 * 1024 * 1024,  # 100 MB
    multipart_chunksize=50 * 1024 * 1024,   # 50 MB chunks
    max_concurrency=10,                      # 10 parallel uploads
    use_threads=True
)

# Upload large file
s3_client.upload_file(
    'large-file.zip',
    'my-bucket',
    'large-file.zip',
    Config=config,
    Callback=lambda bytes_transferred: print(f'Transferred: {bytes_transferred}')
)
```

### Low-Level Multipart API

```python
import boto3
import os

s3_client = boto3.client('s3')
bucket_name = 'my-bucket'
key_name = 'large-file.zip'
file_path = 'large-file.zip'
part_size = 50 * 1024 * 1024  # 50 MB

# Step 1: Initiate multipart upload
response = s3_client.create_multipart_upload(
    Bucket=bucket_name,
    Key=key_name
)
upload_id = response['UploadId']
print(f"Upload ID: {upload_id}")

# Step 2: Upload parts
parts = []
file_size = os.path.getsize(file_path)
part_number = 1

try:
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(part_size)
            if not data:
                break

            response = s3_client.upload_part(
                Bucket=bucket_name,
                Key=key_name,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=data
            )

            parts.append({
                'PartNumber': part_number,
                'ETag': response['ETag']
            })

            print(f"Uploaded part {part_number}")
            part_number += 1

    # Step 3: Complete multipart upload
    s3_client.complete_multipart_upload(
        Bucket=bucket_name,
        Key=key_name,
        UploadId=upload_id,
        MultipartUpload={'Parts': parts}
    )
    print("Upload completed successfully!")

except Exception as e:
    # Abort on failure
    s3_client.abort_multipart_upload(
        Bucket=bucket_name,
        Key=key_name,
        UploadId=upload_id
    )
    print(f"Upload failed: {e}")
```

### Managing Incomplete Multipart Uploads

```bash
# List incomplete multipart uploads
aws s3api list-multipart-uploads --bucket my-bucket

# Abort specific incomplete upload
aws s3api abort-multipart-upload \
    --bucket my-bucket \
    --key large-file.zip \
    --upload-id "UPLOAD_ID"

# Configure lifecycle rule to auto-cleanup
cat > lifecycle-abort-incomplete.json << 'EOF'
{
    "Rules": [
        {
            "ID": "AbortIncompleteMultipartUploads",
            "Status": "Enabled",
            "Filter": {},
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": 7
            }
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket \
    --lifecycle-configuration file://lifecycle-abort-incomplete.json
```

---

## S3 Select and Glacier Select

### S3 Select Overview

S3 Select allows you to retrieve only the data you need from an object using SQL expressions, dramatically reducing data transfer.

```
Traditional Approach:
+------------+     Download Full     +-----------+     Process     +--------+
| S3 Object  | ---> 10 GB File ---> | Your App  | ---> Filter --> | 10 MB  |
| (10 GB)    |     (100% transfer)  |           |                 | Result |
+------------+                       +-----------+                 +--------+
                   Cost: $0.90 data transfer + compute time

With S3 Select:
+------------+     SQL Query         +--------+
| S3 Object  | ---> Filter at S3 -> | 10 MB  |
| (10 GB)    |     (0.1% transfer)  | Result |
+------------+                       +--------+
                   Cost: ~$0.01 + S3 Select charges

Savings: ~99% less data transfer!
```

### Supported Formats

```
+-------------------+------------------------+
|     Format        |     Compression        |
+-------------------+------------------------+
| CSV               | None, GZIP, BZIP2      |
| JSON              | None, GZIP, BZIP2      |
| Apache Parquet    | None, Snappy, GZIP     |
+-------------------+------------------------+

Note: Parquet is columnar, providing additional
performance benefits for column-specific queries
```

### S3 Select SQL Syntax

```sql
-- Basic SELECT
SELECT * FROM s3object s LIMIT 100

-- Column selection
SELECT s.name, s.age, s.city FROM s3object s

-- Filtering with WHERE
SELECT * FROM s3object s WHERE s.age > 25

-- Aggregations
SELECT COUNT(*) FROM s3object s WHERE s.status = 'active'

-- String functions
SELECT * FROM s3object s WHERE s.name LIKE '%Smith%'

-- Type casting
SELECT CAST(s.price AS FLOAT) * 1.1 AS adjusted_price FROM s3object s
```

### Python S3 Select Example

```python
import boto3
import json

s3_client = boto3.client('s3')

# Query CSV file
response = s3_client.select_object_content(
    Bucket='my-bucket',
    Key='data/sales.csv',
    ExpressionType='SQL',
    Expression="""
        SELECT s.product, s.quantity, s.price
        FROM s3object s
        WHERE CAST(s.price AS FLOAT) > 100
    """,
    InputSerialization={
        'CSV': {
            'FileHeaderInfo': 'USE',
            'FieldDelimiter': ',',
            'QuoteCharacter': '"'
        },
        'CompressionType': 'NONE'
    },
    OutputSerialization={
        'CSV': {}
    }
)

# Process streaming response
for event in response['Payload']:
    if 'Records' in event:
        records = event['Records']['Payload'].decode('utf-8')
        print(records)
    elif 'Stats' in event:
        stats = event['Stats']['Details']
        print(f"Bytes Scanned: {stats['BytesScanned']}")
        print(f"Bytes Returned: {stats['BytesReturned']}")
```

### JSON Query Example

```python
# Query JSON file
response = s3_client.select_object_content(
    Bucket='my-bucket',
    Key='data/users.json',
    ExpressionType='SQL',
    Expression="""
        SELECT s.user.name, s.user.email
        FROM s3object[*].users[*] s
        WHERE s.user.age > 30
    """,
    InputSerialization={
        'JSON': {
            'Type': 'DOCUMENT'  # or 'LINES' for JSON Lines format
        }
    },
    OutputSerialization={
        'JSON': {}
    }
)
```

### Parquet Query Example

```python
# Query Parquet file (column-level selection)
response = s3_client.select_object_content(
    Bucket='my-bucket',
    Key='data/analytics.parquet',
    ExpressionType='SQL',
    Expression="""
        SELECT timestamp, user_id, event_type
        FROM s3object s
        WHERE event_type = 'purchase'
    """,
    InputSerialization={
        'Parquet': {}
    },
    OutputSerialization={
        'JSON': {}
    }
)
```

### Glacier Select

Glacier Select allows you to query archived data without restoring the entire object:

```python
# Initiate Glacier Select job
response = s3_client.select_object_content(
    Bucket='my-bucket',
    Key='archived-data.csv',
    ExpressionType='SQL',
    Expression="SELECT * FROM s3object s WHERE s.year = '2023'",
    InputSerialization={
        'CSV': {'FileHeaderInfo': 'USE'}
    },
    OutputSerialization={
        'CSV': {}
    },
    # For Glacier objects
    ScanRange={
        'Start': 0,
        'End': 1048576  # First 1MB
    }
)
```

### S3 Select Cost Comparison

```
Cost Analysis for 100 GB CSV file, extracting 1 GB of matching data:

Traditional Download:
- Data Transfer: 100 GB x $0.09/GB = $9.00
- Processing time on EC2

S3 Select:
- Data Scanned: 100 GB x $0.002/GB = $0.20
- Data Returned: 1 GB x $0.0007/GB = $0.0007
- Total: ~$0.20

Savings: ~97% cost reduction + faster processing!
```

---

## Byte-Range Fetches

### How Byte-Range Fetches Work

Byte-range fetches allow you to retrieve specific portions of an object using the HTTP Range header.

```
10 GB Video File:
+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
| 0-1GB | 1-2GB | 2-3GB | 3-4GB | 4-5GB | 5-6GB | 6-7GB | 7-8GB | 8-9GB | 9-10GB|
+-------+-------+-------+-------+-------+-------+-------+-------+-------+-------+
    |
    | Range: bytes=0-1073741823
    v
+-------+
| 0-1GB |  Only this portion is transferred
+-------+
```

### Use Cases

```
+---------------------------------------------------+
|           Byte-Range Fetch Use Cases              |
+---------------------------------------------------+
| 1. Video/Audio Streaming                          |
|    - Load chunks as needed for playback           |
|    - Seek to specific timestamps                  |
+---------------------------------------------------+
| 2. Large File Headers                             |
|    - Read metadata without full download          |
|    - Extract file information quickly             |
+---------------------------------------------------+
| 3. Parallel Downloads                             |
|    - Split large files across connections         |
|    - Maximize bandwidth utilization               |
+---------------------------------------------------+
| 4. Resume Failed Downloads                        |
|    - Continue from last successful byte           |
|    - Avoid re-downloading completed portions      |
+---------------------------------------------------+
```

### CLI Examples

```bash
# Fetch first 1 MB of a file
aws s3api get-object \
    --bucket my-bucket \
    --key large-video.mp4 \
    --range bytes=0-1048575 \
    first-mb.mp4

# Fetch bytes 1MB to 2MB
aws s3api get-object \
    --bucket my-bucket \
    --key large-video.mp4 \
    --range bytes=1048576-2097151 \
    second-mb.mp4

# Fetch last 1 MB
aws s3api get-object \
    --bucket my-bucket \
    --key large-video.mp4 \
    --range bytes=-1048576 \
    last-mb.mp4
```

### Python Byte-Range Example

```python
import boto3
import concurrent.futures
import os

s3_client = boto3.client('s3')

def download_chunk(bucket, key, start_byte, end_byte, part_num, output_dir):
    """Download a specific byte range of an S3 object."""
    response = s3_client.get_object(
        Bucket=bucket,
        Key=key,
        Range=f'bytes={start_byte}-{end_byte}'
    )

    chunk_file = f"{output_dir}/part_{part_num:04d}"
    with open(chunk_file, 'wb') as f:
        f.write(response['Body'].read())

    return chunk_file

def parallel_download(bucket, key, output_file, chunk_size=50*1024*1024, max_workers=10):
    """Download an S3 object in parallel using byte-range fetches."""

    # Get object size
    response = s3_client.head_object(Bucket=bucket, Key=key)
    file_size = response['ContentLength']

    # Calculate chunks
    chunks = []
    start = 0
    part_num = 0
    while start < file_size:
        end = min(start + chunk_size - 1, file_size - 1)
        chunks.append((start, end, part_num))
        start = end + 1
        part_num += 1

    # Create temp directory
    output_dir = f"/tmp/download_{os.getpid()}"
    os.makedirs(output_dir, exist_ok=True)

    # Download chunks in parallel
    chunk_files = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                download_chunk, bucket, key, start, end, pn, output_dir
            ): pn for start, end, pn in chunks
        }

        for future in concurrent.futures.as_completed(futures):
            chunk_files.append(future.result())

    # Combine chunks
    chunk_files.sort()
    with open(output_file, 'wb') as outfile:
        for chunk_file in chunk_files:
            with open(chunk_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(chunk_file)

    os.rmdir(output_dir)
    print(f"Downloaded {file_size} bytes to {output_file}")

# Usage
parallel_download('my-bucket', 'large-file.zip', 'downloaded-file.zip')
```

### Video Streaming Example

```python
from flask import Flask, Response, request
import boto3

app = Flask(__name__)
s3_client = boto3.client('s3')

@app.route('/video/<key>')
def stream_video(key):
    """Stream video with byte-range support."""
    bucket = 'video-bucket'

    # Get object metadata
    head = s3_client.head_object(Bucket=bucket, Key=key)
    file_size = head['ContentLength']

    # Parse Range header
    range_header = request.headers.get('Range')

    if range_header:
        # Parse range
        byte_range = range_header.replace('bytes=', '').split('-')
        start = int(byte_range[0])
        end = int(byte_range[1]) if byte_range[1] else file_size - 1

        # Fetch range from S3
        response = s3_client.get_object(
            Bucket=bucket,
            Key=key,
            Range=f'bytes={start}-{end}'
        )

        def generate():
            for chunk in response['Body'].iter_chunks(chunk_size=1024*1024):
                yield chunk

        return Response(
            generate(),
            status=206,
            headers={
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': end - start + 1,
                'Content-Type': 'video/mp4'
            }
        )

    # Full file request
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return Response(
        response['Body'].read(),
        headers={
            'Accept-Ranges': 'bytes',
            'Content-Length': file_size,
            'Content-Type': 'video/mp4'
        }
    )
```

---

## Prefix Optimization

### Understanding S3 Partitioning

S3 automatically partitions data based on key prefixes. Each prefix can handle:
- 3,500 PUT/COPY/POST/DELETE requests per second
- 5,500 GET/HEAD requests per second

```
Key-Based Partitioning:
+--------------------+     +--------------------+
|    Prefix: /a      |     |    Prefix: /b      |
| 5,500 GET/s limit  |     | 5,500 GET/s limit  |
+--------------------+     +--------------------+
| /a/file1.txt       |     | /b/file1.txt       |
| /a/file2.txt       |     | /b/file2.txt       |
| /a/subdir/file.txt |     | /b/subdir/file.txt |
+--------------------+     +--------------------+

Total capacity: 2 x 5,500 = 11,000 GET/s
```

### Anti-Pattern: Sequential Prefixes

```
BAD: Sequential/timestamp prefixes concentrate requests
+-----------------------------------------------+
| /2024/01/01/00/file001.log                    |
| /2024/01/01/00/file002.log                    |  All requests hit
| /2024/01/01/00/file003.log                    |  the same prefix!
| /2024/01/01/00/file004.log                    |
+-----------------------------------------------+
                 |
                 v
         Single partition
         (bottleneck!)
```

### Optimization: Distributed Prefixes

```
GOOD: Hash-based prefixes distribute load
+-----------------------------------------------+
| /a1b2c3/2024/01/01/00/file001.log            |  Partition 1
| /d4e5f6/2024/01/01/00/file002.log            |  Partition 2
| /g7h8i9/2024/01/01/00/file003.log            |  Partition 3
| /j0k1l2/2024/01/01/00/file004.log            |  Partition 4
+-----------------------------------------------+
                 |
                 v
         Requests distributed
         across partitions!
```

### Prefix Distribution Strategies

#### Strategy 1: Hash Prefix

```python
import hashlib

def generate_distributed_key(original_key):
    """Add hash prefix to distribute across partitions."""
    hash_prefix = hashlib.md5(original_key.encode()).hexdigest()[:4]
    return f"{hash_prefix}/{original_key}"

# Example
original = "logs/2024/01/01/app.log"
distributed = generate_distributed_key(original)
# Result: "a1b2/logs/2024/01/01/app.log"
```

#### Strategy 2: Reversed Date Prefix

```python
from datetime import datetime

def generate_reversed_date_key(filename):
    """Reverse date components for better distribution."""
    now = datetime.now()
    # Instead of: 2024/01/15/file.log
    # Use: 51/10/4202/file.log (reversed)
    reversed_date = f"{now.day:02d}/{now.month:02d}/{str(now.year)[::-1]}"
    return f"{reversed_date}/{filename}"
```

#### Strategy 3: Random Prefix

```python
import random
import string

def generate_random_prefix_key(original_key, prefix_length=4):
    """Add random prefix for maximum distribution."""
    prefix = ''.join(random.choices(string.hexdigits.lower(), k=prefix_length))
    return f"{prefix}/{original_key}"
```

### Performance Comparison

```
Scenario: 20,000 requests/second to log files

Sequential Keys (/logs/2024/01/01/...):
+------------------+
| Single Partition | --> 5,500 GET/s limit
| Bottleneck!      |     Request failures
+------------------+

Distributed Keys (hash/logs/2024/01/01/...):
+------------------+------------------+------------------+------------------+
| Partition /0-3   | Partition /4-7   | Partition /8-b   | Partition /c-f   |
| 5,500 GET/s      | 5,500 GET/s      | 5,500 GET/s      | 5,500 GET/s      |
+------------------+------------------+------------------+------------------+
                            |
                   Total: 22,000 GET/s capacity
                   20,000 requests handled easily!
```

---

## Caching Strategies

### CloudFront Integration

```
+----------+     Miss     +------------+     +----------+
|  Client  | -----------> | CloudFront | --> | S3       |
+----------+              | (Cache)    |     | (Origin) |
     |                    +------------+     +----------+
     |                         |
     |        Hit              |
     +<------------------------+
          (Low latency)
```

### CloudFront Distribution for S3

```bash
# Create CloudFront distribution for S3 bucket
aws cloudfront create-distribution \
    --origin-domain-name my-bucket.s3.amazonaws.com \
    --default-root-object index.html

# With Origin Access Control (recommended)
cat > distribution-config.json << 'EOF'
{
    "Origins": {
        "Items": [
            {
                "DomainName": "my-bucket.s3.us-east-1.amazonaws.com",
                "Id": "S3Origin",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                },
                "OriginAccessControlId": "OAC_ID"
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3Origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"
    },
    "Enabled": true
}
EOF
```

### Application-Level Caching

```python
import boto3
import redis
import json
from datetime import timedelta

# Redis cache client
cache = redis.Redis(host='localhost', port=6379, db=0)
s3_client = boto3.client('s3')

def get_s3_object_cached(bucket, key, ttl_seconds=3600):
    """Get S3 object with Redis caching."""
    cache_key = f"s3:{bucket}:{key}"

    # Check cache first
    cached = cache.get(cache_key)
    if cached:
        print("Cache HIT")
        return json.loads(cached)

    # Cache miss - fetch from S3
    print("Cache MISS")
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read().decode('utf-8')

    # Store in cache
    cache.setex(cache_key, ttl_seconds, json.dumps(data))

    return data

def invalidate_cache(bucket, key):
    """Invalidate cached S3 object."""
    cache_key = f"s3:{bucket}:{key}"
    cache.delete(cache_key)
```

---

## Practical Examples

### Example 1: High-Throughput Log Ingestion

```python
import boto3
import hashlib
import concurrent.futures
from datetime import datetime

s3_client = boto3.client('s3')

def upload_log_entry(log_data, bucket):
    """Upload log with distributed key for high throughput."""
    timestamp = datetime.now().isoformat()

    # Generate distributed key
    hash_prefix = hashlib.md5(f"{timestamp}{log_data[:50]}".encode()).hexdigest()[:4]
    key = f"{hash_prefix}/logs/{datetime.now().strftime('%Y/%m/%d/%H')}/{timestamp}.json"

    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=log_data,
        ContentType='application/json'
    )
    return key

def batch_upload_logs(log_entries, bucket, max_workers=50):
    """Upload multiple logs in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(upload_log_entry, entry, bucket)
            for entry in log_entries
        ]

        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    return results

# Usage
logs = [f'{{"event": "login", "user_id": {i}}}' for i in range(10000)]
uploaded_keys = batch_upload_logs(logs, 'high-throughput-logs')
print(f"Uploaded {len(uploaded_keys)} logs")
```

### Example 2: Large File Transfer with Progress

```python
import boto3
import sys
from boto3.s3.transfer import TransferConfig

class ProgressPercentage:
    def __init__(self, filename, filesize):
        self._filename = filename
        self._size = filesize
        self._seen_so_far = 0

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        percentage = (self._seen_so_far / self._size) * 100
        sys.stdout.write(
            f"\r{self._filename}: {self._seen_so_far}/{self._size} bytes "
            f"({percentage:.2f}%)"
        )
        sys.stdout.flush()

def optimized_upload(file_path, bucket, key):
    """Upload large file with all optimizations."""
    import os

    s3_client = boto3.client(
        's3',
        config=boto3.session.Config(
            s3={'use_accelerate_endpoint': True}  # Transfer Acceleration
        )
    )

    file_size = os.path.getsize(file_path)

    # Optimize chunk size based on file size
    if file_size < 100 * 1024 * 1024:  # < 100 MB
        chunk_size = 8 * 1024 * 1024   # 8 MB chunks
    elif file_size < 1024 * 1024 * 1024:  # < 1 GB
        chunk_size = 50 * 1024 * 1024  # 50 MB chunks
    else:
        chunk_size = 100 * 1024 * 1024  # 100 MB chunks

    config = TransferConfig(
        multipart_threshold=100 * 1024 * 1024,
        multipart_chunksize=chunk_size,
        max_concurrency=20,
        use_threads=True
    )

    s3_client.upload_file(
        file_path,
        bucket,
        key,
        Config=config,
        Callback=ProgressPercentage(file_path, file_size)
    )
    print(f"\nUpload complete: s3://{bucket}/{key}")

# Usage
optimized_upload('large-dataset.zip', 'my-bucket', 'datasets/large-dataset.zip')
```

### Example 3: Efficient Data Analysis with S3 Select

```python
import boto3
import pandas as pd
from io import StringIO

s3_client = boto3.client('s3')

def analyze_sales_data(bucket, key, min_amount=1000):
    """Analyze sales data using S3 Select."""

    # Query only relevant data
    query = f"""
        SELECT s.date, s.product, s.quantity, s.amount
        FROM s3object s
        WHERE CAST(s.amount AS FLOAT) > {min_amount}
    """

    response = s3_client.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType='SQL',
        Expression=query,
        InputSerialization={
            'CSV': {
                'FileHeaderInfo': 'USE',
                'FieldDelimiter': ','
            }
        },
        OutputSerialization={'CSV': {}}
    )

    # Collect results
    records = []
    for event in response['Payload']:
        if 'Records' in event:
            records.append(event['Records']['Payload'].decode('utf-8'))

    # Parse into DataFrame
    csv_data = ''.join(records)
    df = pd.read_csv(StringIO(csv_data), names=['date', 'product', 'quantity', 'amount'])

    # Analyze
    print(f"Total high-value transactions: {len(df)}")
    print(f"Total revenue: ${df['amount'].sum():,.2f}")
    print(f"Top products:\n{df.groupby('product')['amount'].sum().nlargest(5)}")

    return df

# Usage
df = analyze_sales_data('sales-bucket', 'data/sales_2024.csv', min_amount=1000)
```

---

## Performance Benchmarking

### Benchmark Script

```python
import boto3
import time
import statistics
import concurrent.futures
from boto3.s3.transfer import TransferConfig

def benchmark_upload(bucket, file_path, iterations=10):
    """Benchmark upload performance with different configurations."""
    results = {}

    # Standard upload
    s3_client = boto3.client('s3')
    times = []
    for _ in range(iterations):
        start = time.time()
        s3_client.upload_file(file_path, bucket, 'benchmark/standard')
        times.append(time.time() - start)
    results['standard'] = {
        'mean': statistics.mean(times),
        'std': statistics.stdev(times) if len(times) > 1 else 0
    }

    # Multipart upload
    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,
        multipart_chunksize=8 * 1024 * 1024,
        max_concurrency=10
    )
    times = []
    for _ in range(iterations):
        start = time.time()
        s3_client.upload_file(file_path, bucket, 'benchmark/multipart', Config=config)
        times.append(time.time() - start)
    results['multipart'] = {
        'mean': statistics.mean(times),
        'std': statistics.stdev(times) if len(times) > 1 else 0
    }

    # Transfer Acceleration
    s3_accel = boto3.client(
        's3',
        config=boto3.session.Config(s3={'use_accelerate_endpoint': True})
    )
    times = []
    for _ in range(iterations):
        start = time.time()
        s3_accel.upload_file(file_path, bucket, 'benchmark/accelerated', Config=config)
        times.append(time.time() - start)
    results['accelerated'] = {
        'mean': statistics.mean(times),
        'std': statistics.stdev(times) if len(times) > 1 else 0
    }

    return results

def benchmark_download(bucket, key, iterations=10):
    """Benchmark download performance."""
    results = {}
    s3_client = boto3.client('s3')

    # Standard download
    times = []
    for _ in range(iterations):
        start = time.time()
        s3_client.download_file(bucket, key, '/tmp/benchmark_standard')
        times.append(time.time() - start)
    results['standard'] = statistics.mean(times)

    # Byte-range parallel download
    # (Implementation would use the parallel_download function from earlier)

    return results

# Run benchmarks
print("Upload Benchmarks:")
upload_results = benchmark_upload('my-bucket', 'test-file-100mb.bin')
for method, data in upload_results.items():
    print(f"  {method}: {data['mean']:.2f}s (+/- {data['std']:.2f}s)")
```

---

## Best Practices

### Performance Optimization Checklist

```
+---------------------------------------------------------------+
|               S3 Performance Best Practices                    |
+---------------------------------------------------------------+

[ ] Use multipart upload for files > 100 MB
    - Configure appropriate chunk size
    - Set up lifecycle rule for incomplete uploads

[ ] Enable Transfer Acceleration for distant uploads
    - Test with speed comparison tool first
    - Only pay if acceleration is faster

[ ] Use S3 Select for data filtering
    - Supports CSV, JSON, Parquet
    - Reduces data transfer significantly

[ ] Implement byte-range fetches for large files
    - Parallel downloads improve throughput
    - Enable video/audio streaming

[ ] Distribute keys across prefixes
    - Avoid sequential prefixes
    - Use hash or random prefixes for high throughput

[ ] Cache frequently accessed objects
    - CloudFront for global distribution
    - Application-level cache for hot data

[ ] Use appropriate storage class
    - Standard for frequent access
    - IA for infrequent access
    - Match access patterns to storage class

[ ] Monitor and optimize
    - Use CloudWatch metrics
    - S3 Storage Lens for insights
    - Regular performance testing
```

### Quick Reference Table

| Scenario | Solution | Improvement |
|----------|----------|-------------|
| Large file upload | Multipart upload | 2-10x faster |
| Global uploads | Transfer Acceleration | 50-500% faster |
| Query large datasets | S3 Select | 90%+ cost reduction |
| Video streaming | Byte-range fetches | On-demand loading |
| High request rate | Prefix distribution | Unlimited scale |
| Global read access | CloudFront cache | 10-100ms latency |

---

## Summary

### Key Takeaways

1. **Transfer Acceleration** - Use CloudFront edges for faster uploads from distant locations
2. **Multipart Uploads** - Required for files > 5GB, recommended for > 100MB
3. **S3 Select** - Query data at the source to reduce transfer and compute costs
4. **Byte-Range Fetches** - Retrieve only needed portions for streaming and parallel downloads
5. **Prefix Optimization** - Distribute keys to achieve virtually unlimited throughput
6. **Caching** - Use CloudFront and application caching for frequently accessed data

### Performance Decision Tree

```
Uploading Data?
    |
    +-- File > 100MB? --> Use Multipart Upload
    |
    +-- Distant location? --> Enable Transfer Acceleration
    |
    +-- High throughput needed? --> Distribute prefixes

Downloading Data?
    |
    +-- Need partial data? --> Use Byte-Range Fetches
    |
    +-- Query structured data? --> Use S3 Select
    |
    +-- Frequent access? --> Add CloudFront/Cache
    |
    +-- Large files? --> Parallel downloads
```

---

## Next Steps

1. Complete the hands-on examples in this guide
2. Run benchmarks in your environment
3. Implement optimization strategies for your use case
4. Review S3 Event Notifications guide
5. Practice with the comprehensive lab

---

## Additional Resources

- [S3 Performance Guidelines](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)
- [Transfer Acceleration Speed Test](http://s3-accelerate-speedtest.s3-accelerate.amazonaws.com/en/accelerate-speed-comparsion.html)
- [S3 Select Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/selecting-content-from-objects.html)
- [Multipart Upload Overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
