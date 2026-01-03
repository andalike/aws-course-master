# S3 Event Notifications: Event-Driven Architecture

## Table of Contents
1. [Introduction to S3 Events](#introduction-to-s3-events)
2. [S3 Event Types](#s3-event-types)
3. [Event Destinations](#event-destinations)
4. [Event Filtering](#event-filtering)
5. [Integration with Lambda](#integration-with-lambda)
6. [Integration with SQS](#integration-with-sqs)
7. [Integration with SNS](#integration-with-sns)
8. [Integration with EventBridge](#integration-with-eventbridge)
9. [Hands-On: Lambda on Upload](#hands-on-lambda-on-upload)
10. [Best Practices](#best-practices)

---

## Introduction to S3 Events

S3 Event Notifications enable event-driven architectures by automatically sending notifications when specific events occur in your buckets.

### Event-Driven Architecture Overview

```
                         S3 Bucket
                            |
                            | Events
                            v
            +-------------------------------+
            |     Event Notification        |
            +-------------------------------+
                    /    |    \    \
                   /     |     \    \
                  v      v      v    v
            +------+ +-----+ +-----+ +------------+
            |Lambda| | SQS | | SNS | |EventBridge |
            +------+ +-----+ +-----+ +------------+
                |       |       |          |
                v       v       v          v
            Process   Queue   Fan-out   Route to
            Images   Messages  Alerts   35+ Services
```

### Why Use S3 Events?

| Use Case | Description | Destination |
|----------|-------------|-------------|
| **Image Processing** | Generate thumbnails on upload | Lambda |
| **ETL Pipelines** | Process data files | Lambda/SQS |
| **Notifications** | Alert on new uploads | SNS |
| **Logging** | Track object changes | EventBridge |
| **Backup Triggers** | Initiate workflows | SQS |
| **Content Moderation** | Scan uploaded files | Lambda |

---

## S3 Event Types

### Available Event Types

```
+-----------------------------------------------+
|              S3 Event Types                   |
+-----------------------------------------------+
| Object Created Events:                        |
|   s3:ObjectCreated:*                         |
|   s3:ObjectCreated:Put                       |
|   s3:ObjectCreated:Post                      |
|   s3:ObjectCreated:Copy                      |
|   s3:ObjectCreated:CompleteMultipartUpload   |
+-----------------------------------------------+
| Object Removed Events:                        |
|   s3:ObjectRemoved:*                         |
|   s3:ObjectRemoved:Delete                    |
|   s3:ObjectRemoved:DeleteMarkerCreated       |
+-----------------------------------------------+
| Object Restore Events (Glacier):              |
|   s3:ObjectRestore:*                         |
|   s3:ObjectRestore:Post                      |
|   s3:ObjectRestore:Completed                 |
+-----------------------------------------------+
| Replication Events:                           |
|   s3:Replication:*                           |
|   s3:Replication:OperationFailedReplication  |
|   s3:Replication:OperationNotTracked         |
|   s3:Replication:OperationMissedThreshold    |
|   s3:Replication:OperationReplicatedAfterThreshold |
+-----------------------------------------------+
| Object Lifecycle Events:                      |
|   s3:LifecycleExpiration:*                   |
|   s3:LifecycleExpiration:Delete              |
|   s3:LifecycleExpiration:DeleteMarkerCreated |
|   s3:LifecycleTransition                     |
+-----------------------------------------------+
| Intelligent-Tiering Events:                   |
|   s3:IntelligentTiering                      |
+-----------------------------------------------+
| Object Tagging Events:                        |
|   s3:ObjectTagging:*                         |
|   s3:ObjectTagging:Put                       |
|   s3:ObjectTagging:Delete                    |
+-----------------------------------------------+
| Object ACL Events:                            |
|   s3:ObjectAcl:Put                           |
+-----------------------------------------------+
```

### Event Message Structure

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2024-01-15T12:30:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "MyNotificationConfig",
        "bucket": {
          "name": "my-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::my-bucket"
        },
        "object": {
          "key": "images/photo.jpg",
          "size": 1024000,
          "eTag": "0123456789abcdef0123456789abcdef",
          "versionId": "096fKKXTRTtl3on89fVO.nfljtsv6qko",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}
```

### Event Fields Explained

| Field | Description | Example |
|-------|-------------|---------|
| `eventName` | Type of event | `ObjectCreated:Put` |
| `eventTime` | When event occurred | ISO 8601 timestamp |
| `bucket.name` | Source bucket | `my-bucket` |
| `object.key` | Object key (URL-encoded) | `images%2Fphoto.jpg` |
| `object.size` | Object size in bytes | `1024000` |
| `object.eTag` | Object ETag | MD5 hash |
| `object.versionId` | Version ID (if versioned) | `096fKKX...` |

---

## Event Destinations

### Comparison of Destinations

```
+---------------+------------------+------------------+------------------+
|   Feature     |     Lambda       |       SQS        |       SNS        |
+---------------+------------------+------------------+------------------+
| Invocation    | Synchronous      | Async (poll)     | Async (push)     |
| Retry         | 2 retries        | Configurable     | 3 retries        |
| Scaling       | Automatic        | Consumer-based   | Push to all subs |
| Use Case      | Processing       | Decoupling       | Fan-out          |
| Latency       | Lowest           | Medium           | Low              |
| Cost          | Per invocation   | Per message      | Per notification |
+---------------+------------------+------------------+------------------+

+---------------+------------------+
|   Feature     |   EventBridge    |
+---------------+------------------+
| Invocation    | Async (route)    |
| Retry         | Configurable     |
| Scaling       | Automatic        |
| Use Case      | Complex routing  |
| Latency       | Low              |
| Cost          | Per event        |
+---------------+------------------+
```

### Architecture Patterns

```
Pattern 1: Direct Lambda Processing
+----------+     +--------+     +-----------+
| S3 Event | --> | Lambda | --> | DynamoDB  |
+----------+     +--------+     +-----------+

Pattern 2: Queue-Based Processing
+----------+     +-----+     +--------+     +-----------+
| S3 Event | --> | SQS | --> | Lambda | --> | RDS       |
+----------+     +-----+     +--------+     +-----------+

Pattern 3: Fan-Out with SNS
+----------+     +-----+     +--------+
| S3 Event | --> | SNS | --> | Lambda |
+----------+     +-----+     +--------+
                    |        +--------+
                    +------> | SQS    |
                    |        +--------+
                    |        +--------+
                    +------> | Email  |
                             +--------+

Pattern 4: EventBridge Routing
+----------+     +-------------+     +---------------+
| S3 Event | --> | EventBridge | --> | Step Functions|
+----------+     +-------------+     +---------------+
                       |             +---------------+
                       +-----------> | Lambda        |
                       |             +---------------+
                       +-----------> | SNS           |
                                     +---------------+
```

---

## Event Filtering

### Filter Configuration

S3 supports filtering events based on object key prefix and suffix:

```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "ProcessImages",
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessImages",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "images/"
            },
            {
              "Name": "suffix",
              "Value": ".jpg"
            }
          ]
        }
      }
    }
  ]
}
```

### Filter Examples

```
Filter Configuration Examples:

1. JPEG images in images folder:
   Prefix: "images/"
   Suffix: ".jpg"
   Matches: images/photo.jpg, images/2024/vacation.jpg
   Ignores: documents/photo.jpg, images/photo.png

2. All PDFs in any folder:
   Prefix: (none)
   Suffix: ".pdf"
   Matches: documents/report.pdf, invoices/2024/bill.pdf

3. All files in uploads folder:
   Prefix: "uploads/"
   Suffix: (none)
   Matches: uploads/file.txt, uploads/image.png

4. Log files:
   Prefix: "logs/"
   Suffix: ".log"
   Matches: logs/app.log, logs/2024/01/access.log
```

### Multiple Notification Configurations

```
Single Bucket, Multiple Handlers:
+----------------------------------------+
|              S3 Bucket                 |
+----------------------------------------+
| uploads/images/*.jpg  --> Lambda A     |
| uploads/images/*.png  --> Lambda A     |
| uploads/documents/*.pdf --> Lambda B   |
| uploads/videos/*.mp4  --> SQS Queue    |
| logs/*.log           --> EventBridge   |
+----------------------------------------+

Note: Prefixes must not overlap for the same event type!
```

---

## Integration with Lambda

### Lambda Permission Setup

Before S3 can invoke Lambda, you must grant permission:

```bash
# Add permission for S3 to invoke Lambda
aws lambda add-permission \
    --function-name ProcessImages \
    --principal s3.amazonaws.com \
    --statement-id S3InvokeLambda \
    --action "lambda:InvokeFunction" \
    --source-arn arn:aws:s3:::my-bucket \
    --source-account 123456789012
```

### Lambda Function Example

```python
import boto3
import urllib.parse
import json

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Process S3 event notifications."""

    for record in event['Records']:
        # Get bucket and key from event
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        event_name = record['eventName']

        print(f"Event: {event_name}")
        print(f"Bucket: {bucket}")
        print(f"Key: {key}")

        # Get object metadata
        response = s3_client.head_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        size = response['ContentLength']

        print(f"Content-Type: {content_type}")
        print(f"Size: {size} bytes")

        # Process based on event type
        if event_name.startswith('ObjectCreated'):
            process_new_object(bucket, key)
        elif event_name.startswith('ObjectRemoved'):
            handle_deleted_object(bucket, key)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {len(event["Records"])} events')
    }

def process_new_object(bucket, key):
    """Handle newly created objects."""
    print(f"Processing new object: s3://{bucket}/{key}")
    # Add your processing logic here

def handle_deleted_object(bucket, key):
    """Handle deleted objects."""
    print(f"Object deleted: s3://{bucket}/{key}")
    # Add cleanup logic here
```

### Image Thumbnail Generator

```python
import boto3
from PIL import Image
import io
import urllib.parse

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Generate thumbnails for uploaded images."""

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        # Skip if already a thumbnail
        if key.startswith('thumbnails/'):
            continue

        # Download image
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_content = response['Body'].read()

        # Open and resize image
        image = Image.open(io.BytesIO(image_content))
        image.thumbnail((200, 200))

        # Save to bytes
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=85)
        buffer.seek(0)

        # Upload thumbnail
        thumbnail_key = f"thumbnails/{key}"
        s3_client.put_object(
            Bucket=bucket,
            Key=thumbnail_key,
            Body=buffer,
            ContentType='image/jpeg'
        )

        print(f"Created thumbnail: {thumbnail_key}")

    return {'statusCode': 200}
```

---

## Integration with SQS

### Why Use SQS with S3?

```
Direct Lambda:
+--------+     +--------+
| S3     | --> | Lambda |  Risk: Lambda throttling
+--------+     +--------+       under high load

With SQS Buffer:
+--------+     +-----+     +--------+
| S3     | --> | SQS | --> | Lambda |  Benefit: Controlled
+--------+     +-----+     +--------+           processing rate
                  |
              Messages buffered,
              processed at your pace
```

### SQS Queue Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ToSendMessage",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:123456789012:s3-events-queue",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:::my-bucket"
        },
        "StringEquals": {
          "aws:SourceAccount": "123456789012"
        }
      }
    }
  ]
}
```

### Configure S3 to SQS

```bash
# Create SQS queue
aws sqs create-queue --queue-name s3-events-queue

# Get queue ARN
QUEUE_ARN=$(aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/s3-events-queue \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

# Apply queue policy (allowing S3)
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/s3-events-queue \
    --attributes file://queue-policy.json

# Configure S3 notification
cat > notification-config.json << EOF
{
    "QueueConfigurations": [
        {
            "Id": "S3ToSQS",
            "QueueArn": "${QUEUE_ARN}",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "uploads/"}
                    ]
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-notification-configuration \
    --bucket my-bucket \
    --notification-configuration file://notification-config.json
```

### SQS Consumer Lambda

```python
import boto3
import json
import urllib.parse

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Process S3 events from SQS."""

    for sqs_record in event['Records']:
        # Parse S3 event from SQS message body
        s3_event = json.loads(sqs_record['body'])

        for s3_record in s3_event.get('Records', []):
            bucket = s3_record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(s3_record['s3']['object']['key'])

            print(f"Processing: s3://{bucket}/{key}")

            # Your processing logic here
            process_file(bucket, key)

    return {'statusCode': 200}

def process_file(bucket, key):
    """Process the uploaded file."""
    # Get object
    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read()

    # Process content
    print(f"File size: {len(content)} bytes")
```

---

## Integration with SNS

### Fan-Out Pattern

```
SNS enables fan-out: One event, multiple consumers

             +----------+     +----------------+
             |  Lambda  | <-- | Image Processor|
             +----------+     +----------------+
                  ^
                  |
+--------+     +-----+     +----------+     +----------------+
| S3     | --> | SNS | --> | SQS      | <-- | Async Worker   |
+--------+     +-----+     +----------+     +----------------+
                  |
                  |
                  v
             +----------+     +----------------+
             |  Email   | <-- | Notification   |
             +----------+     +----------------+
```

### SNS Topic Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ToPublish",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:123456789012:s3-events-topic",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:::my-bucket"
        }
      }
    }
  ]
}
```

### Configure S3 to SNS

```bash
# Create SNS topic
aws sns create-topic --name s3-events-topic

# Apply topic policy
aws sns set-topic-attributes \
    --topic-arn arn:aws:sns:us-east-1:123456789012:s3-events-topic \
    --attribute-name Policy \
    --attribute-value file://topic-policy.json

# Subscribe Lambda to SNS
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789012:s3-events-topic \
    --protocol lambda \
    --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:ProcessImages

# Subscribe SQS to SNS
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789012:s3-events-topic \
    --protocol sqs \
    --notification-endpoint arn:aws:sqs:us-east-1:123456789012:backup-queue

# Subscribe email to SNS
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789012:s3-events-topic \
    --protocol email \
    --notification-endpoint admin@example.com

# Configure S3 notification
cat > sns-notification.json << 'EOF'
{
    "TopicConfigurations": [
        {
            "Id": "S3ToSNS",
            "TopicArn": "arn:aws:sns:us-east-1:123456789012:s3-events-topic",
            "Events": ["s3:ObjectCreated:*"]
        }
    ]
}
EOF

aws s3api put-bucket-notification-configuration \
    --bucket my-bucket \
    --notification-configuration file://sns-notification.json
```

---

## Integration with EventBridge

### Why EventBridge?

```
EventBridge Advantages:
+--------------------------------------------------+
| - Route to 35+ AWS services                      |
| - Advanced filtering with content-based rules   |
| - Archive and replay events                      |
| - Schema registry for event discovery           |
| - Cross-account event routing                    |
+--------------------------------------------------+
```

### Enable EventBridge for S3

```bash
# Enable EventBridge notifications for bucket
aws s3api put-bucket-notification-configuration \
    --bucket my-bucket \
    --notification-configuration '{
        "EventBridgeConfiguration": {}
    }'
```

### EventBridge Rule for S3 Events

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["my-bucket"]
    },
    "object": {
      "key": [{
        "prefix": "uploads/"
      }]
    }
  }
}
```

### Create EventBridge Rule

```bash
# Create rule for S3 object created events
aws events put-rule \
    --name S3ObjectCreated \
    --event-pattern '{
        "source": ["aws.s3"],
        "detail-type": ["Object Created"],
        "detail": {
            "bucket": {
                "name": ["my-bucket"]
            }
        }
    }'

# Add Lambda target
aws events put-targets \
    --rule S3ObjectCreated \
    --targets '[{
        "Id": "ProcessFunction",
        "Arn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessS3Events"
    }]'

# Add Step Functions target
aws events put-targets \
    --rule S3ObjectCreated \
    --targets '[{
        "Id": "WorkflowStateMachine",
        "Arn": "arn:aws:states:us-east-1:123456789012:stateMachine:ProcessWorkflow",
        "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeRole"
    }]'
```

### EventBridge Event Format

```json
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "detail-type": "Object Created",
  "source": "aws.s3",
  "account": "123456789012",
  "time": "2024-01-15T12:30:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:s3:::my-bucket"
  ],
  "detail": {
    "version": "0",
    "bucket": {
      "name": "my-bucket"
    },
    "object": {
      "key": "uploads/document.pdf",
      "size": 1048576,
      "etag": "d41d8cd98f00b204e9800998ecf8427e",
      "version-id": "096fKKXTRTtl3on89fVO.nfljtsv6qko",
      "sequencer": "0061234567890ABC"
    },
    "request-id": "C3D13FE58DE4C810",
    "requester": "123456789012",
    "source-ip-address": "127.0.0.1",
    "reason": "PutObject"
  }
}
```

---

## Hands-On: Lambda on Upload

### Complete Lab: Image Processing Pipeline

This lab creates an image processing pipeline that:
1. Triggers on image upload
2. Generates thumbnail
3. Extracts metadata
4. Stores metadata in DynamoDB
5. Sends notification

#### Architecture

```
+--------+     +---------+     +----------+
| Upload | --> | Lambda  | --> | Thumbnail|
| Image  |     |Processor|     | (S3)     |
+--------+     +---------+     +----------+
                    |
                    +--------> +----------+
                               | DynamoDB |
                               | Metadata |
                               +----------+
                    |
                    +--------> +----------+
                               | SNS      |
                               | Notify   |
                               +----------+
```

#### Step 1: Create IAM Role

```bash
# Create trust policy
cat > lambda-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create role
aws iam create-role \
    --role-name ImageProcessorRole \
    --assume-role-policy-document file://lambda-trust-policy.json

# Create permission policy
cat > lambda-permissions.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::image-bucket-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/ImageMetadata"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": "arn:aws:sns:*:*:image-processed"
        }
    ]
}
EOF

# Attach policy
aws iam put-role-policy \
    --role-name ImageProcessorRole \
    --policy-name ImageProcessorPolicy \
    --policy-document file://lambda-permissions.json
```

#### Step 2: Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name ImageMetadata \
    --attribute-definitions \
        AttributeName=ImageId,AttributeType=S \
    --key-schema \
        AttributeName=ImageId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

#### Step 3: Create SNS Topic

```bash
aws sns create-topic --name image-processed
```

#### Step 4: Create Lambda Function

```python
# lambda_function.py
import boto3
import urllib.parse
import json
import uuid
from datetime import datetime
from PIL import Image
import io

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

THUMBNAIL_SIZE = (200, 200)
METADATA_TABLE = 'ImageMetadata'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:image-processed'

def lambda_handler(event, context):
    """Main handler for S3 image upload events."""

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        # Skip thumbnails to avoid infinite loop
        if key.startswith('thumbnails/'):
            continue

        try:
            # Process image
            result = process_image(bucket, key)

            # Store metadata
            store_metadata(result)

            # Send notification
            send_notification(result)

            print(f"Successfully processed: {key}")

        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            raise

    return {'statusCode': 200, 'body': 'Processing complete'}

def process_image(bucket, key):
    """Download, create thumbnail, and extract metadata."""

    # Download original image
    response = s3_client.get_object(Bucket=bucket, Key=key)
    image_content = response['Body'].read()

    # Open with PIL
    image = Image.open(io.BytesIO(image_content))

    # Extract metadata
    metadata = {
        'image_id': str(uuid.uuid4()),
        'original_key': key,
        'bucket': bucket,
        'format': image.format,
        'mode': image.mode,
        'width': image.width,
        'height': image.height,
        'size_bytes': len(image_content),
        'processed_at': datetime.utcnow().isoformat()
    }

    # Create thumbnail
    thumbnail = image.copy()
    thumbnail.thumbnail(THUMBNAIL_SIZE)

    # Save thumbnail to bytes
    buffer = io.BytesIO()
    thumbnail.save(buffer, 'JPEG', quality=85)
    buffer.seek(0)

    # Upload thumbnail
    thumbnail_key = f"thumbnails/{key.rsplit('.', 1)[0]}_thumb.jpg"
    s3_client.put_object(
        Bucket=bucket,
        Key=thumbnail_key,
        Body=buffer,
        ContentType='image/jpeg'
    )

    metadata['thumbnail_key'] = thumbnail_key

    return metadata

def store_metadata(metadata):
    """Store image metadata in DynamoDB."""
    table = dynamodb.Table(METADATA_TABLE)
    table.put_item(Item={
        'ImageId': metadata['image_id'],
        'OriginalKey': metadata['original_key'],
        'Bucket': metadata['bucket'],
        'Format': metadata['format'],
        'Width': metadata['width'],
        'Height': metadata['height'],
        'SizeBytes': metadata['size_bytes'],
        'ThumbnailKey': metadata['thumbnail_key'],
        'ProcessedAt': metadata['processed_at']
    })

def send_notification(metadata):
    """Send SNS notification about processed image."""
    message = {
        'event': 'image_processed',
        'image_id': metadata['image_id'],
        'original_key': metadata['original_key'],
        'thumbnail_key': metadata['thumbnail_key'],
        'dimensions': f"{metadata['width']}x{metadata['height']}",
        'processed_at': metadata['processed_at']
    }

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message),
        Subject='Image Processed Successfully'
    )
```

#### Step 5: Package and Deploy Lambda

```bash
# Create deployment package with dependencies
mkdir lambda-package
cd lambda-package
pip install Pillow -t .
cp ../lambda_function.py .
zip -r ../function.zip .
cd ..

# Create Lambda function
aws lambda create-function \
    --function-name ImageProcessor \
    --runtime python3.11 \
    --role arn:aws:iam::123456789012:role/ImageProcessorRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 60 \
    --memory-size 512
```

#### Step 6: Create S3 Bucket and Configure Notification

```bash
# Create bucket
BUCKET_NAME="image-bucket-$(date +%s)"
aws s3api create-bucket --bucket $BUCKET_NAME --region us-east-1

# Add Lambda permission for S3
aws lambda add-permission \
    --function-name ImageProcessor \
    --principal s3.amazonaws.com \
    --statement-id S3InvokeFunction \
    --action "lambda:InvokeFunction" \
    --source-arn arn:aws:s3:::$BUCKET_NAME \
    --source-account 123456789012

# Configure S3 notification
cat > notification.json << EOF
{
    "LambdaFunctionConfigurations": [
        {
            "Id": "ImageUploadTrigger",
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:ImageProcessor",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "uploads/"},
                        {"Name": "suffix", "Value": ".jpg"}
                    ]
                }
            }
        },
        {
            "Id": "ImageUploadTriggerPNG",
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:ImageProcessor",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "uploads/"},
                        {"Name": "suffix", "Value": ".png"}
                    ]
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-notification-configuration \
    --bucket $BUCKET_NAME \
    --notification-configuration file://notification.json
```

#### Step 7: Test the Pipeline

```bash
# Upload a test image
aws s3 cp test-image.jpg s3://$BUCKET_NAME/uploads/test-image.jpg

# Check Lambda logs
aws logs tail /aws/lambda/ImageProcessor --follow

# Verify thumbnail was created
aws s3 ls s3://$BUCKET_NAME/thumbnails/

# Check DynamoDB for metadata
aws dynamodb scan --table-name ImageMetadata
```

#### Step 8: Cleanup

```bash
# Delete S3 objects and bucket
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3api delete-bucket --bucket $BUCKET_NAME

# Delete Lambda function
aws lambda delete-function --function-name ImageProcessor

# Delete DynamoDB table
aws dynamodb delete-table --table-name ImageMetadata

# Delete SNS topic
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:123456789012:image-processed

# Delete IAM role and policy
aws iam delete-role-policy --role-name ImageProcessorRole --policy-name ImageProcessorPolicy
aws iam delete-role --role-name ImageProcessorRole
```

---

## Best Practices

### Event Notification Best Practices

```
+----------------------------------------------------------+
|            S3 Event Notification Best Practices           |
+----------------------------------------------------------+

1. PREVENT INFINITE LOOPS
   - Never write to the same prefix that triggers events
   - Use separate input/output prefixes
   - Filter by suffix to process only specific file types

   BAD:  Trigger on "images/", write to "images/"
   GOOD: Trigger on "uploads/", write to "processed/"

2. HANDLE DUPLICATES
   - S3 events are delivered at least once
   - Implement idempotent processing
   - Use DynamoDB for deduplication

3. USE APPROPRIATE DESTINATION
   - Lambda: Real-time processing, low volume
   - SQS: High volume, controlled processing rate
   - SNS: Fan-out to multiple consumers
   - EventBridge: Complex routing, cross-account

4. IMPLEMENT ERROR HANDLING
   - Configure DLQ for failed processing
   - Use exponential backoff for retries
   - Log failures for debugging

5. MONITOR AND ALERT
   - Set up CloudWatch alarms
   - Monitor Lambda errors and duration
   - Track SQS queue depth

6. SECURITY
   - Use least privilege IAM roles
   - Validate event sources
   - Sanitize object keys (URL-encoded)
+----------------------------------------------------------+
```

### Avoiding Infinite Loops

```
WRONG Configuration (Infinite Loop):
+--------+     +--------+     +--------+
| Upload | --> | Lambda | --> | Write  |
| images/|     |Process |     | images/| --> Triggers Lambda again!
+--------+     +--------+     +--------+

CORRECT Configuration:
+--------+     +--------+     +--------+
| Upload | --> | Lambda | --> | Write  |
| input/ |     |Process |     | output/| --> No trigger
+--------+     +--------+     +--------+
```

### Idempotent Processing

```python
import boto3
import hashlib

dynamodb = boto3.resource('dynamodb')
processed_table = dynamodb.Table('ProcessedEvents')

def lambda_handler(event, context):
    for record in event['Records']:
        # Create unique event ID
        event_id = hashlib.sha256(
            f"{record['s3']['bucket']['name']}"
            f"{record['s3']['object']['key']}"
            f"{record['s3']['object']['sequencer']}"
            .encode()
        ).hexdigest()

        # Check if already processed
        try:
            processed_table.put_item(
                Item={
                    'EventId': event_id,
                    'ProcessedAt': datetime.utcnow().isoformat()
                },
                ConditionExpression='attribute_not_exists(EventId)'
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Event {event_id} already processed, skipping")
            continue

        # Process the event
        process_record(record)
```

---

## Summary

### Key Takeaways

| Topic | Key Points |
|-------|------------|
| **Event Types** | ObjectCreated, ObjectRemoved, Restore, Replication, Lifecycle |
| **Destinations** | Lambda, SQS, SNS, EventBridge |
| **Filtering** | Prefix and suffix based filtering |
| **Lambda** | Direct invocation, requires permission |
| **SQS** | Buffering, controlled processing rate |
| **SNS** | Fan-out to multiple subscribers |
| **EventBridge** | Advanced routing, cross-account |

### Decision Tree

```
Choosing Event Destination:

Need real-time processing?
    |
    +-- Yes --> Need fan-out?
    |               |
    |           +---+---+
    |           |       |
    |          Yes      No --> Lambda (direct)
    |           |
    |          SNS --> Multiple subscribers
    |
    +-- No --> Need controlled rate?
                    |
                +---+---+
                |       |
               Yes      No
                |       |
               SQS     EventBridge (complex routing)
```

---

## Next Steps

1. Complete the image processing hands-on lab
2. Practice with different event types
3. Implement error handling and DLQs
4. Set up monitoring and alerting
5. Proceed to the comprehensive S3 lab

---

## Additional Resources

- [S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)
- [Lambda with S3](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html)
- [EventBridge with S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventBridge.html)
- [SQS as Event Destination](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ways-to-add-notification-config-to-bucket.html)
