# Event-Driven Data Pipeline - Complete Implementation Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [S3 Bucket Setup](#s3-bucket-setup)
4. [Lambda Processing Functions](#lambda-processing-functions)
5. [SNS/SQS Integration](#snssqs-integration)
6. [Error Handling](#error-handling)
7. [Monitoring Setup](#monitoring-setup)
8. [Complete CloudFormation Template](#complete-cloudformation-template)
9. [Deployment Scripts](#deployment-scripts)
10. [Testing](#testing)
11. [Cost Analysis](#cost-analysis)
12. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
                        EVENT-DRIVEN DATA PIPELINE ARCHITECTURE
    =======================================================================================

    DATA SOURCES                    PROCESSING                      OUTPUTS
    ============                    ==========                      =======

    +-----------+                                                 +-----------+
    | CSV Files |--+                                          +-->| Processed |
    +-----------+  |                                          |   |    S3     |
                   |    +-----------+                         |   +-----------+
    +-----------+  +--->|           |     +-------------+     |
    |JSON Files |------>|  S3 Input |---->| S3 Event    |     |   +-----------+
    +-----------+  +--->|  Bucket   |     | Notification|     +-->| DynamoDB  |
                   |    +-----------+     +------+------+     |   |  Table    |
    +-----------+  |                             |            |   +-----------+
    |Image Files|--+                             |            |
    +-----------+                                |            |   +-----------+
                                                 v            +-->|CloudWatch |
                                          +------+------+     |   |  Metrics  |
                                          |    SQS      |     |   +-----------+
                                          | Input Queue |     |
                                          +------+------+     |   +-----------+
                                                 |            +-->|    SNS    |
                                                 v            |   |  Alerts   |
                                          +------+------+     |   +-----------+
                                          |   Lambda    |     |
                                          |  Processor  |-----+
                                          +------+------+
                                                 |
                            +--------------------+--------------------+
                            |                    |                    |
                            v                    v                    v
                     +------+------+      +------+------+      +------+------+
                     | CSV Parser  |      |JSON Parser  |      |Image Resize |
                     |   Lambda    |      |   Lambda    |      |   Lambda    |
                     +------+------+      +------+------+      +------+------+
                            |                    |                    |
                            v                    v                    v
                     +------+------+      +------+------+      +------+------+
                     |   Success   |      |   Success   |      |   Success   |
                     |    Queue    |      |    Queue    |      |    Queue    |
                     +-------------+      +-------------+      +-------------+

    ERROR HANDLING:
                     +-------------+
                     |    DLQ      |<---- Failed messages after 3 retries
                     | Dead Letter |
                     |    Queue    |
                     +------+------+
                            |
                            v
                     +------+------+
                     | Error Alert |----> Email/Slack notification
                     |    Lambda   |
                     +-------------+

    FLOW:
    1. Files uploaded to S3 input bucket
    2. S3 event notification triggers SQS message
    3. Lambda reads from SQS and processes file
    4. Processed data written to output bucket/DynamoDB
    5. Success/failure notifications sent via SNS
    6. Failed messages sent to DLQ after retries
```

---

## Prerequisites

### Required Tools

```bash
# AWS CLI v2
aws --version

# Python 3.9+ for Lambda
python3 --version

# Verify AWS credentials
aws sts get-caller-identity
```

### Environment Setup

```bash
export AWS_REGION="us-east-1"
export PROJECT_NAME="data-pipeline"
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

---

## S3 Bucket Setup

### Create Input and Output Buckets

```bash
# Create input bucket
aws s3 mb s3://${PROJECT_NAME}-input-${ACCOUNT_ID} --region ${AWS_REGION}

# Create output bucket
aws s3 mb s3://${PROJECT_NAME}-output-${ACCOUNT_ID} --region ${AWS_REGION}

# Create archive bucket for processed files
aws s3 mb s3://${PROJECT_NAME}-archive-${ACCOUNT_ID} --region ${AWS_REGION}

# Enable versioning on all buckets
for bucket in input output archive; do
    aws s3api put-bucket-versioning \
        --bucket ${PROJECT_NAME}-${bucket}-${ACCOUNT_ID} \
        --versioning-configuration Status=Enabled
done

# Add lifecycle policy for archive bucket
aws s3api put-bucket-lifecycle-configuration \
    --bucket ${PROJECT_NAME}-archive-${ACCOUNT_ID} \
    --lifecycle-configuration '{
        "Rules": [
            {
                "ID": "MoveToGlacier",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Transitions": [
                    {
                        "Days": 30,
                        "StorageClass": "GLACIER"
                    }
                ],
                "Expiration": {
                    "Days": 365
                }
            }
        ]
    }'
```

### Create Folder Structure

```bash
# Create folder structure for organization
aws s3api put-object --bucket ${PROJECT_NAME}-input-${ACCOUNT_ID} --key csv/
aws s3api put-object --bucket ${PROJECT_NAME}-input-${ACCOUNT_ID} --key json/
aws s3api put-object --bucket ${PROJECT_NAME}-input-${ACCOUNT_ID} --key images/

aws s3api put-object --bucket ${PROJECT_NAME}-output-${ACCOUNT_ID} --key processed/
aws s3api put-object --bucket ${PROJECT_NAME}-output-${ACCOUNT_ID} --key transformed/
aws s3api put-object --bucket ${PROJECT_NAME}-output-${ACCOUNT_ID} --key thumbnails/
```

---

## Lambda Processing Functions

### Project Structure

```
data-pipeline/
├── src/
│   ├── processor/
│   │   ├── __init__.py
│   │   ├── main.py           # Main dispatcher
│   │   ├── csv_handler.py    # CSV processing
│   │   ├── json_handler.py   # JSON processing
│   │   └── image_handler.py  # Image processing
│   ├── notifier/
│   │   ├── __init__.py
│   │   └── handler.py        # Error notification
│   └── utils/
│       ├── __init__.py
│       ├── s3_utils.py
│       └── metrics.py
├── template.yaml
└── requirements.txt
```

### src/processor/main.py - Main Dispatcher

```python
"""
Main Lambda handler - Dispatches files to appropriate processors
"""
import json
import os
import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.typing import LambdaContext

from csv_handler import process_csv
from json_handler import process_json
from image_handler import process_image

logger = Logger()
tracer = Tracer()
metrics = Metrics()
processor = BatchProcessor(event_type=EventType.SQS)

s3_client = boto3.client('s3')

# Configuration
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET')
ARCHIVE_BUCKET = os.environ.get('ARCHIVE_BUCKET')


def get_file_type(key: str) -> str:
    """Determine file type from S3 key"""
    extension = key.lower().split('.')[-1]

    type_mapping = {
        'csv': 'csv',
        'json': 'json',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image',
        'txt': 'text'
    }

    return type_mapping.get(extension, 'unknown')


@tracer.capture_method
def record_handler(record: dict) -> dict:
    """
    Process a single SQS record containing S3 event

    Args:
        record: SQS record with S3 event notification

    Returns:
        Processing result
    """
    # Parse S3 event from SQS message body
    body = json.loads(record['body'])

    # Handle S3 event notification format
    if 'Records' in body:
        s3_event = body['Records'][0]
    else:
        s3_event = body

    bucket = s3_event['s3']['bucket']['name']
    key = s3_event['s3']['object']['key']
    size = s3_event['s3']['object'].get('size', 0)

    logger.info(f"Processing file: s3://{bucket}/{key}")
    metrics.add_metric(name="FilesProcessed", unit=MetricUnit.Count, value=1)

    file_type = get_file_type(key)
    logger.info(f"Detected file type: {file_type}")

    try:
        # Route to appropriate handler
        if file_type == 'csv':
            result = process_csv(bucket, key, OUTPUT_BUCKET)
        elif file_type == 'json':
            result = process_json(bucket, key, OUTPUT_BUCKET)
        elif file_type == 'image':
            result = process_image(bucket, key, OUTPUT_BUCKET)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            result = {'status': 'skipped', 'reason': f'Unsupported file type: {file_type}'}

        # Archive processed file
        if result.get('status') == 'success':
            archive_file(bucket, key, ARCHIVE_BUCKET)
            metrics.add_metric(name="FilesSuccessful", unit=MetricUnit.Count, value=1)
        else:
            metrics.add_metric(name="FilesSkipped", unit=MetricUnit.Count, value=1)

        return result

    except Exception as e:
        logger.exception(f"Error processing file: {key}")
        metrics.add_metric(name="FilesFailed", unit=MetricUnit.Count, value=1)
        raise


@tracer.capture_method
def archive_file(source_bucket: str, key: str, archive_bucket: str):
    """Move processed file to archive bucket"""
    try:
        # Copy to archive
        s3_client.copy_object(
            Bucket=archive_bucket,
            CopySource={'Bucket': source_bucket, 'Key': key},
            Key=f"processed/{key}"
        )

        # Delete from source
        s3_client.delete_object(Bucket=source_bucket, Key=key)

        logger.info(f"Archived file: {key}")

    except Exception as e:
        logger.error(f"Failed to archive file {key}: {e}")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event: dict, context: LambdaContext) -> dict:
    """
    Lambda handler for processing S3 events from SQS

    Args:
        event: SQS event with S3 notifications
        context: Lambda context

    Returns:
        Batch processing result
    """
    batch = event['Records']
    logger.info(f"Received {len(batch)} records to process")

    with processor(records=batch, handler=record_handler):
        result = processor.process()

    logger.info(f"Processing complete: {result}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': len(result),
            'successful': sum(1 for r in result if r.get('status') == 'success'),
            'failed': sum(1 for r in result if r.get('status') == 'failed')
        })
    }
```

### src/processor/csv_handler.py

```python
"""
CSV file processing handler
"""
import csv
import io
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import boto3
from aws_lambda_powertools import Logger, Tracer

logger = Logger(child=True)
tracer = Tracer()

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ.get('DYNAMODB_TABLE')


@tracer.capture_method
def process_csv(source_bucket: str, key: str, output_bucket: str) -> Dict[str, Any]:
    """
    Process a CSV file

    - Parse CSV content
    - Validate data
    - Transform to JSON
    - Store in DynamoDB
    - Write processed output to S3

    Args:
        source_bucket: Source S3 bucket
        key: S3 object key
        output_bucket: Output S3 bucket

    Returns:
        Processing result
    """
    logger.info(f"Processing CSV: {key}")

    try:
        # Download file from S3
        response = s3_client.get_object(Bucket=source_bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        # Parse CSV
        reader = csv.DictReader(io.StringIO(content))
        records = list(reader)

        if not records:
            return {
                'status': 'skipped',
                'reason': 'Empty CSV file',
                'key': key
            }

        logger.info(f"Parsed {len(records)} records from CSV")

        # Validate and transform records
        valid_records = []
        invalid_records = []

        for i, record in enumerate(records):
            is_valid, errors = validate_csv_record(record)
            if is_valid:
                transformed = transform_csv_record(record, i, key)
                valid_records.append(transformed)
            else:
                invalid_records.append({
                    'row': i + 2,  # +2 for header and 0-indexing
                    'errors': errors,
                    'data': record
                })

        # Store valid records in DynamoDB
        if TABLE_NAME and valid_records:
            store_in_dynamodb(valid_records)

        # Write processed JSON to S3
        output_key = f"processed/{key.replace('.csv', '.json')}"
        output_data = {
            'source_file': key,
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'total_records': len(records),
            'valid_records': len(valid_records),
            'invalid_records': len(invalid_records),
            'data': valid_records
        }

        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=json.dumps(output_data, indent=2),
            ContentType='application/json'
        )

        # Write error report if there are invalid records
        if invalid_records:
            error_key = f"errors/{key.replace('.csv', '_errors.json')}"
            s3_client.put_object(
                Bucket=output_bucket,
                Key=error_key,
                Body=json.dumps(invalid_records, indent=2),
                ContentType='application/json'
            )

        return {
            'status': 'success',
            'key': key,
            'output_key': output_key,
            'records_processed': len(valid_records),
            'records_failed': len(invalid_records)
        }

    except Exception as e:
        logger.exception(f"Error processing CSV: {key}")
        return {
            'status': 'failed',
            'key': key,
            'error': str(e)
        }


def validate_csv_record(record: Dict[str, str]) -> tuple:
    """
    Validate a CSV record

    Args:
        record: Dictionary of CSV values

    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []

    # Check required fields (customize based on your data)
    required_fields = ['id', 'name']
    for field in required_fields:
        if field not in record or not record[field].strip():
            errors.append(f"Missing required field: {field}")

    # Validate data types
    if 'price' in record and record['price']:
        try:
            float(record['price'])
        except ValueError:
            errors.append("Invalid price format")

    if 'quantity' in record and record['quantity']:
        try:
            int(record['quantity'])
        except ValueError:
            errors.append("Invalid quantity format")

    if 'email' in record and record['email']:
        if '@' not in record['email']:
            errors.append("Invalid email format")

    return len(errors) == 0, errors


def transform_csv_record(record: Dict[str, str], index: int, source_file: str) -> Dict[str, Any]:
    """
    Transform a CSV record for storage

    Args:
        record: Original CSV record
        index: Row index
        source_file: Source file name

    Returns:
        Transformed record
    """
    transformed = {
        'pk': f"CSV#{source_file}",
        'sk': f"ROW#{index:06d}",
        'source_file': source_file,
        'row_number': index,
        'processed_at': datetime.utcnow().isoformat() + 'Z'
    }

    # Copy all fields, converting types where appropriate
    for key, value in record.items():
        if value:
            # Try to convert to appropriate type
            if key in ['price', 'amount', 'total']:
                try:
                    transformed[key] = float(value)
                except ValueError:
                    transformed[key] = value
            elif key in ['quantity', 'count', 'id']:
                try:
                    transformed[key] = int(value)
                except ValueError:
                    transformed[key] = value
            else:
                transformed[key] = value.strip()

    return transformed


@tracer.capture_method
def store_in_dynamodb(records: List[Dict[str, Any]]):
    """
    Store records in DynamoDB using batch write

    Args:
        records: List of records to store
    """
    table = dynamodb.Table(TABLE_NAME)

    # Use batch writer for efficiency
    with table.batch_writer() as batch:
        for record in records:
            batch.put_item(Item=record)

    logger.info(f"Stored {len(records)} records in DynamoDB")
```

### src/processor/json_handler.py

```python
"""
JSON file processing handler
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
import boto3
from aws_lambda_powertools import Logger, Tracer

logger = Logger(child=True)
tracer = Tracer()

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ.get('DYNAMODB_TABLE')


@tracer.capture_method
def process_json(source_bucket: str, key: str, output_bucket: str) -> Dict[str, Any]:
    """
    Process a JSON file

    - Parse and validate JSON
    - Apply transformations
    - Store in DynamoDB
    - Write processed output

    Args:
        source_bucket: Source S3 bucket
        key: S3 object key
        output_bucket: Output S3 bucket

    Returns:
        Processing result
    """
    logger.info(f"Processing JSON: {key}")

    try:
        # Download file from S3
        response = s3_client.get_object(Bucket=source_bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        # Parse JSON
        data = json.loads(content)

        # Handle both single objects and arrays
        if isinstance(data, list):
            records = data
        else:
            records = [data]

        if not records:
            return {
                'status': 'skipped',
                'reason': 'Empty JSON file',
                'key': key
            }

        logger.info(f"Parsed {len(records)} records from JSON")

        # Transform records
        transformed_records = []
        for i, record in enumerate(records):
            transformed = transform_json_record(record, i, key)
            transformed_records.append(transformed)

        # Store in DynamoDB
        if TABLE_NAME:
            store_records(transformed_records)

        # Calculate aggregations (if applicable)
        aggregations = calculate_aggregations(transformed_records)

        # Write processed output
        output_key = f"transformed/{key}"
        output_data = {
            'source_file': key,
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'record_count': len(transformed_records),
            'aggregations': aggregations,
            'data': transformed_records
        }

        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=json.dumps(output_data, indent=2),
            ContentType='application/json'
        )

        return {
            'status': 'success',
            'key': key,
            'output_key': output_key,
            'records_processed': len(transformed_records)
        }

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file: {key}")
        return {
            'status': 'failed',
            'key': key,
            'error': f"Invalid JSON: {str(e)}"
        }
    except Exception as e:
        logger.exception(f"Error processing JSON: {key}")
        return {
            'status': 'failed',
            'key': key,
            'error': str(e)
        }


def transform_json_record(record: Dict[str, Any], index: int, source_file: str) -> Dict[str, Any]:
    """
    Transform a JSON record

    Args:
        record: Original record
        index: Record index
        source_file: Source file name

    Returns:
        Transformed record
    """
    transformed = {
        'pk': f"JSON#{source_file}",
        'sk': f"REC#{index:06d}",
        'source_file': source_file,
        'record_index': index,
        'processed_at': datetime.utcnow().isoformat() + 'Z',
        'original_data': record
    }

    # Extract and normalize common fields
    if 'timestamp' in record:
        transformed['event_timestamp'] = record['timestamp']

    if 'type' in record:
        transformed['event_type'] = record['type']

    if 'user_id' in record or 'userId' in record:
        transformed['user_id'] = record.get('user_id') or record.get('userId')

    return transformed


def calculate_aggregations(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregations over the records

    Args:
        records: List of transformed records

    Returns:
        Aggregation results
    """
    aggregations = {
        'total_records': len(records),
        'event_types': {},
        'users': set()
    }

    for record in records:
        # Count event types
        event_type = record.get('event_type', 'unknown')
        aggregations['event_types'][event_type] = aggregations['event_types'].get(event_type, 0) + 1

        # Track unique users
        if record.get('user_id'):
            aggregations['users'].add(record['user_id'])

    # Convert set to count
    aggregations['unique_users'] = len(aggregations['users'])
    del aggregations['users']

    return aggregations


@tracer.capture_method
def store_records(records: List[Dict[str, Any]]):
    """Store records in DynamoDB"""
    table = dynamodb.Table(TABLE_NAME)

    with table.batch_writer() as batch:
        for record in records:
            # Remove non-DynamoDB compatible types
            clean_record = {
                k: v for k, v in record.items()
                if not isinstance(v, set)
            }
            batch.put_item(Item=clean_record)

    logger.info(f"Stored {len(records)} records in DynamoDB")
```

### src/processor/image_handler.py

```python
"""
Image file processing handler
"""
import io
import os
from datetime import datetime
from typing import Dict, Any, Tuple
import boto3
from PIL import Image
from aws_lambda_powertools import Logger, Tracer

logger = Logger(child=True)
tracer = Tracer()

s3_client = boto3.client('s3')

# Thumbnail sizes
THUMBNAIL_SIZES = {
    'small': (150, 150),
    'medium': (300, 300),
    'large': (600, 600)
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


@tracer.capture_method
def process_image(source_bucket: str, key: str, output_bucket: str) -> Dict[str, Any]:
    """
    Process an image file

    - Validate image
    - Generate thumbnails
    - Extract metadata
    - Write processed outputs

    Args:
        source_bucket: Source S3 bucket
        key: S3 object key
        output_bucket: Output S3 bucket

    Returns:
        Processing result
    """
    logger.info(f"Processing image: {key}")

    try:
        # Get object metadata first
        head_response = s3_client.head_object(Bucket=source_bucket, Key=key)
        file_size = head_response['ContentLength']

        if file_size > MAX_FILE_SIZE:
            return {
                'status': 'failed',
                'key': key,
                'error': f'File too large: {file_size} bytes (max: {MAX_FILE_SIZE})'
            }

        # Download image
        response = s3_client.get_object(Bucket=source_bucket, Key=key)
        image_data = response['Body'].read()

        # Open image with Pillow
        image = Image.open(io.BytesIO(image_data))

        # Extract metadata
        metadata = extract_image_metadata(image, key, file_size)

        # Generate thumbnails
        thumbnails = generate_thumbnails(image, key, output_bucket)

        # Write metadata to S3
        metadata_key = f"metadata/{key}.json"
        import json
        s3_client.put_object(
            Bucket=output_bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2),
            ContentType='application/json'
        )

        return {
            'status': 'success',
            'key': key,
            'metadata': metadata,
            'thumbnails': thumbnails
        }

    except Exception as e:
        logger.exception(f"Error processing image: {key}")
        return {
            'status': 'failed',
            'key': key,
            'error': str(e)
        }


def extract_image_metadata(image: Image.Image, key: str, file_size: int) -> Dict[str, Any]:
    """
    Extract metadata from an image

    Args:
        image: PIL Image object
        key: S3 object key
        file_size: File size in bytes

    Returns:
        Image metadata
    """
    metadata = {
        'filename': key.split('/')[-1],
        'key': key,
        'format': image.format,
        'mode': image.mode,
        'width': image.width,
        'height': image.height,
        'file_size': file_size,
        'processed_at': datetime.utcnow().isoformat() + 'Z'
    }

    # Extract EXIF data if available
    if hasattr(image, '_getexif') and image._getexif():
        exif = image._getexif()
        if exif:
            # Common EXIF tags
            exif_tags = {
                271: 'make',
                272: 'model',
                274: 'orientation',
                306: 'datetime',
                36867: 'datetime_original'
            }
            metadata['exif'] = {}
            for tag, name in exif_tags.items():
                if tag in exif:
                    metadata['exif'][name] = str(exif[tag])

    return metadata


@tracer.capture_method
def generate_thumbnails(image: Image.Image, key: str, output_bucket: str) -> Dict[str, str]:
    """
    Generate thumbnails of various sizes

    Args:
        image: PIL Image object
        key: Original S3 object key
        output_bucket: Output S3 bucket

    Returns:
        Dict mapping size names to S3 keys
    """
    thumbnails = {}
    base_name = key.split('/')[-1].rsplit('.', 1)[0]
    extension = key.split('.')[-1].lower()

    # Convert to RGB if necessary (for PNG with transparency)
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')

    for size_name, dimensions in THUMBNAIL_SIZES.items():
        try:
            # Create thumbnail (maintains aspect ratio)
            thumb = image.copy()
            thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)

            # Save to buffer
            buffer = io.BytesIO()
            thumb.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)

            # Upload to S3
            thumb_key = f"thumbnails/{size_name}/{base_name}_{size_name}.jpg"
            s3_client.put_object(
                Bucket=output_bucket,
                Key=thumb_key,
                Body=buffer,
                ContentType='image/jpeg',
                CacheControl='max-age=31536000'
            )

            thumbnails[size_name] = thumb_key
            logger.info(f"Generated {size_name} thumbnail: {thumb_key}")

        except Exception as e:
            logger.error(f"Error generating {size_name} thumbnail: {e}")

    return thumbnails
```

### src/notifier/handler.py - Error Notification Handler

```python
"""
Error notification handler for DLQ messages
"""
import json
import os
from datetime import datetime
import boto3
from aws_lambda_powertools import Logger

logger = Logger()

sns_client = boto3.client('sns')
ALERT_TOPIC_ARN = os.environ.get('ALERT_TOPIC_ARN')


def handler(event: dict, context) -> dict:
    """
    Process DLQ messages and send alerts

    Args:
        event: SQS event with failed messages
        context: Lambda context

    Returns:
        Processing result
    """
    logger.info(f"Processing {len(event['Records'])} failed messages")

    for record in event['Records']:
        try:
            # Parse the failed message
            body = json.loads(record['body'])

            # Extract S3 event info if available
            s3_info = None
            if 'Records' in body:
                s3_event = body['Records'][0]
                s3_info = {
                    'bucket': s3_event['s3']['bucket']['name'],
                    'key': s3_event['s3']['object']['key']
                }

            # Get failure attributes
            attributes = record.get('messageAttributes', {})
            error_message = attributes.get('ErrorMessage', {}).get('stringValue', 'Unknown error')

            # Build alert message
            alert = {
                'alert_type': 'DATA_PIPELINE_ERROR',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'message_id': record['messageId'],
                's3_info': s3_info,
                'error': error_message,
                'approximate_receive_count': record.get('attributes', {}).get('ApproximateReceiveCount', '?'),
                'lambda_request_id': context.aws_request_id
            }

            # Send SNS alert
            if ALERT_TOPIC_ARN:
                sns_client.publish(
                    TopicArn=ALERT_TOPIC_ARN,
                    Subject='Data Pipeline Processing Error',
                    Message=json.dumps(alert, indent=2),
                    MessageAttributes={
                        'alert_type': {
                            'DataType': 'String',
                            'StringValue': 'error'
                        }
                    }
                )
                logger.info(f"Sent alert for message: {record['messageId']}")
            else:
                logger.warning("No ALERT_TOPIC_ARN configured")

        except Exception as e:
            logger.exception(f"Error processing DLQ message: {e}")

    return {
        'statusCode': 200,
        'body': f"Processed {len(event['Records'])} DLQ messages"
    }
```

### requirements.txt

```
boto3>=1.26.0
aws-lambda-powertools>=2.0.0
Pillow>=9.0.0
```

---

## SNS/SQS Integration

### Create SNS Topics

```bash
# Create alert topic
ALERT_TOPIC_ARN=$(aws sns create-topic \
    --name ${PROJECT_NAME}-alerts \
    --query 'TopicArn' \
    --output text)

# Create success notification topic
SUCCESS_TOPIC_ARN=$(aws sns create-topic \
    --name ${PROJECT_NAME}-success \
    --query 'TopicArn' \
    --output text)

# Subscribe email to alerts (replace with your email)
aws sns subscribe \
    --topic-arn $ALERT_TOPIC_ARN \
    --protocol email \
    --notification-endpoint your-email@example.com

echo "Alert Topic ARN: $ALERT_TOPIC_ARN"
echo "Success Topic ARN: $SUCCESS_TOPIC_ARN"
```

### Create SQS Queues

```bash
# Create Dead Letter Queue
DLQ_ARN=$(aws sqs create-queue \
    --queue-name ${PROJECT_NAME}-dlq \
    --attributes '{
        "MessageRetentionPeriod": "1209600",
        "VisibilityTimeout": "300"
    }' \
    --query 'QueueUrl' \
    --output text)

DLQ_ARN=$(aws sqs get-queue-attributes \
    --queue-url $DLQ_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

# Create main processing queue
QUEUE_URL=$(aws sqs create-queue \
    --queue-name ${PROJECT_NAME}-input-queue \
    --attributes '{
        "VisibilityTimeout": "900",
        "MessageRetentionPeriod": "345600",
        "RedrivePolicy": "{\"deadLetterTargetArn\":\"'$DLQ_ARN'\",\"maxReceiveCount\":\"3\"}"
    }' \
    --query 'QueueUrl' \
    --output text)

QUEUE_ARN=$(aws sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "Queue URL: $QUEUE_URL"
echo "Queue ARN: $QUEUE_ARN"
echo "DLQ ARN: $DLQ_ARN"
```

### Configure S3 Event Notification

```bash
# Create SQS policy to allow S3 to send messages
aws sqs set-queue-attributes \
    --queue-url $QUEUE_URL \
    --attributes '{
        "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"s3.amazonaws.com\"},\"Action\":\"sqs:SendMessage\",\"Resource\":\"'$QUEUE_ARN'\",\"Condition\":{\"ArnLike\":{\"aws:SourceArn\":\"arn:aws:s3:::'${PROJECT_NAME}'-input-'${ACCOUNT_ID}'\"}}}]}"
    }'

# Configure S3 bucket notification
aws s3api put-bucket-notification-configuration \
    --bucket ${PROJECT_NAME}-input-${ACCOUNT_ID} \
    --notification-configuration '{
        "QueueConfigurations": [
            {
                "QueueArn": "'$QUEUE_ARN'",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {"Name": "prefix", "Value": "csv/"},
                            {"Name": "suffix", "Value": ".csv"}
                        ]
                    }
                }
            },
            {
                "QueueArn": "'$QUEUE_ARN'",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {"Name": "prefix", "Value": "json/"},
                            {"Name": "suffix", "Value": ".json"}
                        ]
                    }
                }
            },
            {
                "QueueArn": "'$QUEUE_ARN'",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {"Name": "prefix", "Value": "images/"}
                        ]
                    }
                }
            }
        ]
    }'
```

---

## Error Handling

### Error Handling Strategy

```
+------------------+
|   S3 Upload      |
+--------+---------+
         |
         v
+--------+---------+
|   SQS Queue      | <-- Visibility Timeout: 15 min
+--------+---------+     Message Retention: 4 days
         |
         v
+--------+---------+
|   Lambda         |
|   Processor      |
+--------+---------+
    |    |    |
    |    |    +---> Success: Archive file, publish to success topic
    |    |
    |    +--------> Transient Error: Message returns to queue
    |               (retry after visibility timeout)
    |
    +-------------> Persistent Error: After 3 retries
                    Message moves to DLQ
                    Alert sent via SNS
```

### Retry Configuration

```python
# Lambda retry configuration (in SAM template)
# - Automatic retry on transient errors
# - SQS visibility timeout allows for retries
# - After max receive count, message goes to DLQ

# Error categories:
# 1. Transient (retry): Network errors, throttling, temporary service unavailability
# 2. Permanent (DLQ): Invalid data, malformed files, business logic errors
```

---

## Monitoring Setup

### CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
    --dashboard-name ${PROJECT_NAME}-dashboard \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "title": "Files Processed",
                    "metrics": [
                        ["DataPipeline", "FilesProcessed", {"stat": "Sum"}],
                        [".", "FilesSuccessful", {"stat": "Sum"}],
                        [".", "FilesFailed", {"stat": "Sum"}]
                    ],
                    "period": 60
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "title": "SQS Messages",
                    "metrics": [
                        ["AWS/SQS", "NumberOfMessagesReceived", "QueueName", "'${PROJECT_NAME}'-input-queue"],
                        [".", "NumberOfMessagesDeleted", ".", "."],
                        [".", "ApproximateNumberOfMessagesVisible", ".", "."]
                    ],
                    "period": 60
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6, "width": 12, "height": 6,
                "properties": {
                    "title": "Lambda Performance",
                    "metrics": [
                        ["AWS/Lambda", "Duration", "FunctionName", "'${PROJECT_NAME}'-processor", {"stat": "Average"}],
                        [".", ".", ".", ".", {"stat": "p99"}]
                    ],
                    "period": 60
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 6, "width": 12, "height": 6,
                "properties": {
                    "title": "DLQ Messages",
                    "metrics": [
                        ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "'${PROJECT_NAME}'-dlq"]
                    ],
                    "period": 60
                }
            }
        ]
    }'
```

### CloudWatch Alarms

```bash
# DLQ has messages alarm
aws cloudwatch put-metric-alarm \
    --alarm-name ${PROJECT_NAME}-dlq-has-messages \
    --alarm-description "Messages in DLQ indicate processing failures" \
    --metric-name ApproximateNumberOfMessagesVisible \
    --namespace AWS/SQS \
    --dimensions Name=QueueName,Value=${PROJECT_NAME}-dlq \
    --statistic Sum \
    --period 60 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --alarm-actions $ALERT_TOPIC_ARN

# High latency alarm
aws cloudwatch put-metric-alarm \
    --alarm-name ${PROJECT_NAME}-high-latency \
    --alarm-description "Lambda processing taking too long" \
    --metric-name Duration \
    --namespace AWS/Lambda \
    --dimensions Name=FunctionName,Value=${PROJECT_NAME}-processor \
    --statistic Average \
    --period 300 \
    --evaluation-periods 3 \
    --threshold 60000 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $ALERT_TOPIC_ARN

# Processing queue backlog alarm
aws cloudwatch put-metric-alarm \
    --alarm-name ${PROJECT_NAME}-queue-backlog \
    --alarm-description "Processing queue has backlog" \
    --metric-name ApproximateNumberOfMessagesVisible \
    --namespace AWS/SQS \
    --dimensions Name=QueueName,Value=${PROJECT_NAME}-input-queue \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 3 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $ALERT_TOPIC_ARN
```

---

## Complete CloudFormation Template

### template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: 'Event-Driven Data Pipeline with S3, SQS, Lambda, and DynamoDB'

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

  AlertEmail:
    Type: String
    Description: Email for pipeline alerts
    Default: ''

Conditions:
  HasAlertEmail: !Not [!Equals [!Ref AlertEmail, '']]

Globals:
  Function:
    Runtime: python3.11
    Timeout: 900
    MemorySize: 1024
    Tracing: Active
    Environment:
      Variables:
        LOG_LEVEL: INFO
        POWERTOOLS_SERVICE_NAME: data-pipeline
        POWERTOOLS_METRICS_NAMESPACE: DataPipeline

Resources:
  # ==================== S3 BUCKETS ====================
  InputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-input-${AWS::AccountId}
      VersioningConfiguration:
        Status: Enabled
      NotificationConfiguration:
        QueueConfigurations:
          - Event: s3:ObjectCreated:*
            Queue: !GetAtt InputQueue.Arn
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  OutputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-output-${AWS::AccountId}
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  ArchiveBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-archive-${AWS::AccountId}
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: MoveToGlacier
            Status: Enabled
            Transitions:
              - StorageClass: GLACIER
                TransitionInDays: 30
            ExpirationInDays: 365
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # ==================== DYNAMODB ====================
  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${AWS::StackName}-data
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true

  # ==================== SQS QUEUES ====================
  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub ${AWS::StackName}-dlq
      MessageRetentionPeriod: 1209600  # 14 days
      VisibilityTimeout: 300

  InputQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub ${AWS::StackName}-input-queue
      VisibilityTimeout: 900  # 15 minutes (6x Lambda timeout)
      MessageRetentionPeriod: 345600  # 4 days
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
        maxReceiveCount: 3

  InputQueuePolicy:
    Type: AWS::SQS::QueuePolicy
    Properties:
      Queues:
        - !Ref InputQueue
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: s3.amazonaws.com
            Action: sqs:SendMessage
            Resource: !GetAtt InputQueue.Arn
            Condition:
              ArnLike:
                aws:SourceArn: !Sub arn:aws:s3:::${AWS::StackName}-input-${AWS::AccountId}

  # ==================== SNS TOPICS ====================
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-alerts

  AlertEmailSubscription:
    Type: AWS::SNS::Subscription
    Condition: HasAlertEmail
    Properties:
      TopicArn: !Ref AlertTopic
      Protocol: email
      Endpoint: !Ref AlertEmail

  SuccessTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-success

  # ==================== LAMBDA FUNCTIONS ====================
  ProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-processor
      Handler: processor.main.handler
      CodeUri: src/
      Environment:
        Variables:
          OUTPUT_BUCKET: !Ref OutputBucket
          ARCHIVE_BUCKET: !Ref ArchiveBucket
          DYNAMODB_TABLE: !Ref DataTable
          SUCCESS_TOPIC_ARN: !Ref SuccessTopic
      Policies:
        - S3CrudPolicy:
            BucketName: !Ref InputBucket
        - S3CrudPolicy:
            BucketName: !Ref OutputBucket
        - S3CrudPolicy:
            BucketName: !Ref ArchiveBucket
        - DynamoDBCrudPolicy:
            TableName: !Ref DataTable
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt SuccessTopic.TopicName
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt InputQueue.Arn
            BatchSize: 10
            MaximumBatchingWindowInSeconds: 30

  NotifierFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-notifier
      Handler: notifier.handler.handler
      CodeUri: src/
      Timeout: 60
      MemorySize: 256
      Environment:
        Variables:
          ALERT_TOPIC_ARN: !Ref AlertTopic
      Policies:
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt AlertTopic.TopicName
      Events:
        DLQEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt DeadLetterQueue.Arn
            BatchSize: 10

  # ==================== CLOUDWATCH ALARMS ====================
  DLQAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-dlq-has-messages
      AlarmDescription: Messages in DLQ indicate processing failures
      MetricName: ApproximateNumberOfMessagesVisible
      Namespace: AWS/SQS
      Dimensions:
        - Name: QueueName
          Value: !GetAtt DeadLetterQueue.QueueName
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      AlarmActions:
        - !Ref AlertTopic

  ProcessorErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-processor-errors
      AlarmDescription: Lambda processor errors
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref ProcessorFunction
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

  QueueBacklogAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-queue-backlog
      AlarmDescription: Processing queue has significant backlog
      MetricName: ApproximateNumberOfMessagesVisible
      Namespace: AWS/SQS
      Dimensions:
        - Name: QueueName
          Value: !GetAtt InputQueue.QueueName
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 3
      Threshold: 100
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

Outputs:
  InputBucketName:
    Description: Input S3 bucket for uploading files
    Value: !Ref InputBucket
    Export:
      Name: !Sub ${AWS::StackName}-InputBucket

  OutputBucketName:
    Description: Output S3 bucket for processed files
    Value: !Ref OutputBucket
    Export:
      Name: !Sub ${AWS::StackName}-OutputBucket

  QueueUrl:
    Description: SQS Queue URL
    Value: !Ref InputQueue
    Export:
      Name: !Sub ${AWS::StackName}-QueueUrl

  DLQUrl:
    Description: Dead Letter Queue URL
    Value: !Ref DeadLetterQueue
    Export:
      Name: !Sub ${AWS::StackName}-DLQUrl

  AlertTopicArn:
    Description: SNS Alert Topic ARN
    Value: !Ref AlertTopic
    Export:
      Name: !Sub ${AWS::StackName}-AlertTopic

  TableName:
    Description: DynamoDB Table Name
    Value: !Ref DataTable
    Export:
      Name: !Sub ${AWS::StackName}-TableName

  UploadCommand:
    Description: Command to upload a file
    Value: !Sub aws s3 cp yourfile.csv s3://${InputBucket}/csv/
```

---

## Deployment Scripts

### deploy.sh

```bash
#!/bin/bash
set -euo pipefail

STACK_NAME="${1:-data-pipeline}"
ALERT_EMAIL="${2:-}"

echo "Building SAM application..."
sam build

echo "Deploying stack: $STACK_NAME"
sam deploy \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Stage=dev \
        AlertEmail="$ALERT_EMAIL" \
    --capabilities CAPABILITY_IAM \
    --resolve-s3 \
    --no-confirm-changeset

# Get outputs
echo ""
echo "Deployment complete! Stack outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs' \
    --output table
```

---

## Testing

### Test with Sample Files

```bash
# Get bucket names
INPUT_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name data-pipeline \
    --query 'Stacks[0].Outputs[?OutputKey==`InputBucketName`].OutputValue' \
    --output text)

# Create sample CSV
cat > sample.csv << 'EOF'
id,name,price,quantity,category
1,Widget A,29.99,100,electronics
2,Widget B,49.99,50,electronics
3,Gadget C,19.99,200,home
EOF

# Upload CSV
aws s3 cp sample.csv s3://${INPUT_BUCKET}/csv/sample.csv

# Create sample JSON
cat > sample.json << 'EOF'
[
    {"user_id": "user123", "type": "purchase", "amount": 99.99, "timestamp": "2026-01-03T10:00:00Z"},
    {"user_id": "user456", "type": "view", "product": "widget-a", "timestamp": "2026-01-03T10:05:00Z"}
]
EOF

# Upload JSON
aws s3 cp sample.json s3://${INPUT_BUCKET}/json/sample.json

# Check processing results
OUTPUT_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name data-pipeline \
    --query 'Stacks[0].Outputs[?OutputKey==`OutputBucketName`].OutputValue' \
    --output text)

# Wait and check output
sleep 30
aws s3 ls s3://${OUTPUT_BUCKET}/processed/ --recursive
```

### Monitor Processing

```bash
# Watch SQS queue
watch -n 5 "aws sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names ApproximateNumberOfMessages"

# View Lambda logs
aws logs tail /aws/lambda/data-pipeline-processor --follow

# Check DLQ for failures
aws sqs receive-message \
    --queue-url $DLQ_URL \
    --max-number-of-messages 10
```

---

## Cost Analysis

### Monthly Cost Estimates

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | 100K invocations (1GB, 30s avg) | $5.00 |
| S3 Storage | 10GB input + 10GB output | $0.46 |
| S3 Requests | 200K requests | $1.00 |
| SQS | 500K messages | $0.20 |
| DynamoDB | 1M writes, 5M reads | $1.50 |
| SNS | 1K notifications | $0.01 |
| CloudWatch | Logs + metrics | $3.00 |
| **Total** | | **~$11/month** |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Files not processing | S3 notification not configured | Check bucket notification configuration |
| Lambda timeout | Large files | Increase timeout, add progress tracking |
| Messages in DLQ | Processing errors | Check CloudWatch Logs for errors |
| Permission denied | IAM role missing | Verify Lambda execution role policies |
| Empty output | Validation failures | Check error reports in output bucket |

### Debug Commands

```bash
# Check S3 event notification
aws s3api get-bucket-notification-configuration \
    --bucket $INPUT_BUCKET

# View queue messages
aws sqs receive-message \
    --queue-url $QUEUE_URL \
    --max-number-of-messages 10 \
    --visibility-timeout 0

# Check Lambda logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/data-pipeline-processor \
    --filter-pattern "ERROR"

# View DynamoDB items
aws dynamodb scan \
    --table-name data-pipeline-data \
    --limit 10
```

---

## Cleanup

```bash
# Empty all buckets first
for bucket in input output archive; do
    aws s3 rm s3://data-pipeline-${bucket}-${ACCOUNT_ID} --recursive
done

# Delete stack
sam delete --stack-name data-pipeline
```

---

**Congratulations!** You have built a production-ready event-driven data pipeline with comprehensive error handling and monitoring.

[Back to Project Overview](./README.md) | [Next: Complete Infrastructure Project](../05-complete-infrastructure/implementation.md)
