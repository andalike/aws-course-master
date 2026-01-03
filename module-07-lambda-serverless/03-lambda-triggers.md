# Lambda Triggers and Event Sources

## Introduction

Lambda functions don't run in isolation - they're triggered by events from various AWS services. Understanding these triggers is essential for building event-driven architectures. This section covers the major event sources and how to configure them.

## Trigger Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAMBDA TRIGGER TYPES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SYNCHRONOUS              ASYNCHRONOUS          POLL-BASED       │
│  (Request-Response)       (Fire & Forget)       (Event Source    │
│                                                  Mapping)         │
│  ┌─────────────┐         ┌─────────────┐      ┌─────────────┐   │
│  │ API Gateway │         │     S3      │      │     SQS     │   │
│  │     ALB     │         │    SNS      │      │   Kinesis   │   │
│  │   Cognito   │         │ EventBridge │      │  DynamoDB   │   │
│  │    Alexa    │         │  CloudWatch │      │   Streams   │   │
│  │ Step Funct. │         │    Logs     │      │   Kafka     │   │
│  │   AppSync   │         │   CodeCommit│      │    MQ       │   │
│  └─────────────┘         └─────────────┘      └─────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## API Gateway Trigger

API Gateway is the most common trigger for building REST APIs with Lambda.

### Architecture

```
┌──────────┐    ┌─────────────┐    ┌──────────┐    ┌───────────┐
│  Client  │───▶│ API Gateway │───▶│  Lambda  │───▶│ DynamoDB  │
│          │◀───│             │◀───│          │    │           │
└──────────┘    └─────────────┘    └──────────┘    └───────────┘
```

### Event Structure

```json
{
  "resource": "/users/{userId}",
  "path": "/users/123",
  "httpMethod": "GET",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "queryStringParameters": {
    "include": "orders"
  },
  "pathParameters": {
    "userId": "123"
  },
  "body": null,
  "isBase64Encoded": false,
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "abc123",
    "stage": "prod",
    "requestId": "request-id-123",
    "identity": {
      "sourceIp": "192.168.1.1",
      "userAgent": "Mozilla/5.0..."
    }
  }
}
```

### Handler Example (Python)

```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Handle API Gateway requests"""
    logger.info(f"Request: {event['httpMethod']} {event['path']}")

    http_method = event['httpMethod']
    path = event['path']

    # Route requests
    if path.startswith('/users'):
        if http_method == 'GET':
            return get_user(event)
        elif http_method == 'POST':
            return create_user(event)
        elif http_method == 'PUT':
            return update_user(event)
        elif http_method == 'DELETE':
            return delete_user(event)

    return response(404, {'error': 'Not found'})


def get_user(event):
    user_id = event['pathParameters'].get('userId')

    # Fetch user from database
    user = {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com'
    }

    return response(200, user)


def create_user(event):
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return response(400, {'error': 'Invalid JSON'})

    # Create user in database
    user = {
        'id': 'new-user-id',
        'name': body.get('name'),
        'email': body.get('email')
    }

    return response(201, user)


def update_user(event):
    user_id = event['pathParameters'].get('userId')
    body = json.loads(event.get('body', '{}'))

    # Update user
    return response(200, {'id': user_id, 'updated': True})


def delete_user(event):
    user_id = event['pathParameters'].get('userId')

    # Delete user
    return response(204, None)


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body) if body else ''
    }
```

### CLI Configuration

```bash
# Create REST API
aws apigateway create-rest-api \
    --name "users-api" \
    --description "Users API"

# Add permission for API Gateway to invoke Lambda
aws lambda add-permission \
    --function-name my-function \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:123456789012:abc123/*"
```

## S3 Trigger

S3 events trigger Lambda functions when objects are created, modified, or deleted.

### Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│  Upload  │───▶│    S3    │───▶│  Lambda  │───▶│ Processed │
│  File    │    │  Bucket  │    │(Process) │    │  Storage  │
└──────────┘    └──────────┘    └──────────┘    └───────────┘
```

### Event Types

| Event | Description |
|-------|-------------|
| `s3:ObjectCreated:*` | All object creation events |
| `s3:ObjectCreated:Put` | Object PUT |
| `s3:ObjectCreated:Post` | Object POST |
| `s3:ObjectCreated:Copy` | Object COPY |
| `s3:ObjectRemoved:*` | All deletion events |
| `s3:ObjectRemoved:Delete` | Object DELETE |
| `s3:ObjectRestore:*` | Glacier restore events |

### Event Structure

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2024-01-15T12:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "192.168.1.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123",
        "x-amz-id-2": "EXAMPLE123/abc"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "upload-notification",
        "bucket": {
          "name": "my-bucket",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::my-bucket"
        },
        "object": {
          "key": "uploads/image.jpg",
          "size": 1024,
          "eTag": "abc123def456",
          "sequencer": "0A1B2C3D4E5F"
        }
      }
    }
  ]
}
```

### Handler Example (Node.js)

```javascript
const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const sharp = require('sharp');

const s3 = new S3Client({ region: process.env.AWS_REGION });

exports.handler = async (event) => {
    console.log('Processing S3 event:', JSON.stringify(event, null, 2));

    const results = [];

    for (const record of event.Records) {
        const bucket = record.s3.bucket.name;
        const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, ' '));

        console.log(`Processing: s3://${bucket}/${key}`);

        try {
            // Get the uploaded image
            const getCommand = new GetObjectCommand({
                Bucket: bucket,
                Key: key
            });
            const response = await s3.send(getCommand);

            // Convert stream to buffer
            const chunks = [];
            for await (const chunk of response.Body) {
                chunks.push(chunk);
            }
            const imageBuffer = Buffer.concat(chunks);

            // Create thumbnail
            const thumbnail = await sharp(imageBuffer)
                .resize(200, 200, { fit: 'cover' })
                .jpeg({ quality: 80 })
                .toBuffer();

            // Save thumbnail
            const thumbnailKey = key.replace('uploads/', 'thumbnails/');
            const putCommand = new PutObjectCommand({
                Bucket: bucket,
                Key: thumbnailKey,
                Body: thumbnail,
                ContentType: 'image/jpeg'
            });
            await s3.send(putCommand);

            results.push({
                original: key,
                thumbnail: thumbnailKey,
                status: 'success'
            });

        } catch (error) {
            console.error(`Error processing ${key}:`, error);
            results.push({
                original: key,
                status: 'error',
                error: error.message
            });
        }
    }

    return {
        processed: results.length,
        results: results
    };
};
```

### CLI Configuration

```bash
# Add permission for S3 to invoke Lambda
aws lambda add-permission \
    --function-name image-processor \
    --statement-id s3-invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-bucket \
    --source-account 123456789012

# Configure S3 notification
aws s3api put-bucket-notification-configuration \
    --bucket my-bucket \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [
            {
                "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:image-processor",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {"Name": "prefix", "Value": "uploads/"},
                            {"Name": "suffix", "Value": ".jpg"}
                        ]
                    }
                }
            }
        ]
    }'
```

## DynamoDB Streams Trigger

DynamoDB Streams capture item-level changes in a DynamoDB table.

### Architecture

```
┌───────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐
│ DynamoDB  │───▶│  Streams  │───▶│  Lambda  │───▶│   SNS/    │
│   Table   │    │           │    │          │    │ Analytics │
└───────────┘    └───────────┘    └──────────┘    └───────────┘
```

### Stream Views

| View Type | Contains |
|-----------|----------|
| KEYS_ONLY | Only key attributes |
| NEW_IMAGE | Complete item after modification |
| OLD_IMAGE | Complete item before modification |
| NEW_AND_OLD_IMAGES | Both before and after images |

### Event Structure

```json
{
  "Records": [
    {
      "eventID": "1",
      "eventVersion": "1.0",
      "dynamodb": {
        "Keys": {
          "userId": {
            "S": "user-123"
          }
        },
        "NewImage": {
          "userId": { "S": "user-123" },
          "email": { "S": "new@example.com" },
          "name": { "S": "John Updated" }
        },
        "OldImage": {
          "userId": { "S": "user-123" },
          "email": { "S": "old@example.com" },
          "name": { "S": "John" }
        },
        "StreamViewType": "NEW_AND_OLD_IMAGES",
        "SequenceNumber": "111",
        "SizeBytes": 26
      },
      "awsRegion": "us-east-1",
      "eventName": "MODIFY",
      "eventSourceARN": "arn:aws:dynamodb:us-east-1:123456789012:table/users/stream/2024-01-15T00:00:00.000",
      "eventSource": "aws:dynamodb"
    }
  ]
}
```

### Handler Example (Python)

```python
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789012:user-updates'


def handler(event, context):
    """Process DynamoDB Stream records"""
    logger.info(f"Processing {len(event['Records'])} records")

    for record in event['Records']:
        event_name = record['eventName']
        logger.info(f"Event: {event_name}")

        if event_name == 'INSERT':
            handle_insert(record)
        elif event_name == 'MODIFY':
            handle_modify(record)
        elif event_name == 'REMOVE':
            handle_remove(record)

    return {
        'statusCode': 200,
        'processed': len(event['Records'])
    }


def handle_insert(record):
    """Handle new item creation"""
    new_item = deserialize_dynamodb(record['dynamodb']['NewImage'])
    logger.info(f"New user created: {new_item['userId']}")

    # Send welcome notification
    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject='New User Registration',
        Message=json.dumps({
            'event': 'user_created',
            'userId': new_item['userId'],
            'email': new_item.get('email')
        })
    )


def handle_modify(record):
    """Handle item modification"""
    old_item = deserialize_dynamodb(record['dynamodb']['OldImage'])
    new_item = deserialize_dynamodb(record['dynamodb']['NewImage'])

    # Detect email change
    if old_item.get('email') != new_item.get('email'):
        logger.info(f"Email changed for user {new_item['userId']}")
        # Send email change notification
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='Email Updated',
            Message=json.dumps({
                'event': 'email_changed',
                'userId': new_item['userId'],
                'oldEmail': old_item.get('email'),
                'newEmail': new_item.get('email')
            })
        )


def handle_remove(record):
    """Handle item deletion"""
    old_item = deserialize_dynamodb(record['dynamodb']['OldImage'])
    logger.info(f"User deleted: {old_item['userId']}")


def deserialize_dynamodb(item):
    """Convert DynamoDB format to Python dict"""
    result = {}
    for key, value in item.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = int(value['N']) if '.' not in value['N'] else float(value['N'])
        elif 'BOOL' in value:
            result[key] = value['BOOL']
        elif 'L' in value:
            result[key] = [deserialize_dynamodb({'v': v})['v'] for v in value['L']]
        elif 'M' in value:
            result[key] = deserialize_dynamodb(value['M'])
    return result
```

### CLI Configuration

```bash
# Enable DynamoDB Streams
aws dynamodb update-table \
    --table-name users \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# Get stream ARN
STREAM_ARN=$(aws dynamodb describe-table \
    --table-name users \
    --query 'Table.LatestStreamArn' \
    --output text)

# Create event source mapping
aws lambda create-event-source-mapping \
    --function-name stream-processor \
    --event-source-arn $STREAM_ARN \
    --starting-position LATEST \
    --batch-size 100
```

## SNS Trigger

SNS (Simple Notification Service) triggers Lambda when messages are published to topics.

### Architecture

```
                              ┌──────────┐
                          ┌──▶│ Lambda 1 │
┌──────────┐   ┌──────┐   │   └──────────┘
│ Publisher│──▶│  SNS │───┤   ┌──────────┐
└──────────┘   │ Topic│   ├──▶│ Lambda 2 │
               └──────┘   │   └──────────┘
                          │   ┌──────────┐
                          └──▶│   SQS    │
                              └──────────┘
```

### Event Structure

```json
{
  "Records": [
    {
      "EventVersion": "1.0",
      "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:topic:12345678-1234-1234-1234-123456789012",
      "EventSource": "aws:sns",
      "Sns": {
        "SignatureVersion": "1",
        "Timestamp": "2024-01-15T12:00:00.000Z",
        "Signature": "EXAMPLE...",
        "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/...",
        "MessageId": "msg-12345",
        "Message": "{\"orderId\": \"ORD-001\", \"amount\": 99.99}",
        "MessageAttributes": {
          "eventType": {
            "Type": "String",
            "Value": "ORDER_PLACED"
          }
        },
        "Type": "Notification",
        "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/...",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:orders",
        "Subject": "New Order"
      }
    }
  ]
}
```

### Handler Example (Python)

```python
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Process SNS notifications"""
    logger.info(f"Received {len(event['Records'])} SNS messages")

    for record in event['Records']:
        sns_message = record['Sns']

        # Parse message
        message_body = json.loads(sns_message['Message'])
        subject = sns_message.get('Subject', 'No Subject')
        message_id = sns_message['MessageId']

        # Get message attributes
        attributes = sns_message.get('MessageAttributes', {})
        event_type = attributes.get('eventType', {}).get('Value', 'UNKNOWN')

        logger.info(f"Processing message {message_id}: {subject}")
        logger.info(f"Event type: {event_type}")
        logger.info(f"Message body: {message_body}")

        # Process based on event type
        if event_type == 'ORDER_PLACED':
            process_order(message_body)
        elif event_type == 'ORDER_CANCELLED':
            cancel_order(message_body)

    return {'processed': len(event['Records'])}


def process_order(order):
    """Process new order"""
    logger.info(f"Processing order: {order['orderId']}")
    # Business logic here


def cancel_order(order):
    """Cancel order"""
    logger.info(f"Cancelling order: {order['orderId']}")
    # Business logic here
```

### CLI Configuration

```bash
# Create SNS topic
aws sns create-topic --name orders

# Add Lambda permission
aws lambda add-permission \
    --function-name order-processor \
    --statement-id sns-invoke \
    --action lambda:InvokeFunction \
    --principal sns.amazonaws.com \
    --source-arn arn:aws:sns:us-east-1:123456789012:orders

# Subscribe Lambda to topic
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789012:orders \
    --protocol lambda \
    --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:order-processor
```

## SQS Trigger

SQS (Simple Queue Service) triggers Lambda to process messages from queues.

### Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Producer │───▶│   SQS    │───▶│  Lambda  │───▶│ Database  │
└──────────┘    │  Queue   │    │          │    └───────────┘
                └──────────┘    └──────────┘
                     │                │
                     ▼                ▼
                ┌──────────┐    ┌──────────┐
                │   DLQ    │◀───│ (Failed) │
                └──────────┘    └──────────┘
```

### Event Structure

```json
{
  "Records": [
    {
      "messageId": "msg-001",
      "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3...",
      "body": "{\"orderId\": \"ORD-001\", \"items\": [{\"sku\": \"ITEM-1\", \"qty\": 2}]}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1642329600000",
        "SenderId": "123456789012",
        "ApproximateFirstReceiveTimestamp": "1642329601000"
      },
      "messageAttributes": {
        "priority": {
          "stringValue": "high",
          "dataType": "String"
        }
      },
      "md5OfBody": "abc123...",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:orders-queue",
      "awsRegion": "us-east-1"
    }
  ]
}
```

### Handler Example (Python)

```python
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders')


def handler(event, context):
    """Process SQS messages with partial batch response"""
    logger.info(f"Processing {len(event['Records'])} messages")

    batch_item_failures = []

    for record in event['Records']:
        try:
            process_message(record)
        except Exception as e:
            logger.error(f"Error processing message {record['messageId']}: {e}")
            # Report this message as failed
            batch_item_failures.append({
                'itemIdentifier': record['messageId']
            })

    # Return failed messages for retry
    return {
        'batchItemFailures': batch_item_failures
    }


def process_message(record):
    """Process individual SQS message"""
    message_id = record['messageId']
    body = json.loads(record['body'])

    logger.info(f"Processing order: {body['orderId']}")

    # Get message attributes
    attributes = record.get('messageAttributes', {})
    priority = attributes.get('priority', {}).get('stringValue', 'normal')

    # Store in DynamoDB
    table.put_item(Item={
        'orderId': body['orderId'],
        'items': body['items'],
        'status': 'processing',
        'priority': priority,
        'messageId': message_id
    })

    logger.info(f"Order {body['orderId']} stored successfully")
```

### CLI Configuration

```bash
# Create SQS queue
aws sqs create-queue --queue-name orders-queue

# Create DLQ
aws sqs create-queue --queue-name orders-queue-dlq

# Configure DLQ policy
aws sqs set-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/orders-queue \
    --attributes '{
        "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:123456789012:orders-queue-dlq\",\"maxReceiveCount\":\"3\"}"
    }'

# Create event source mapping
aws lambda create-event-source-mapping \
    --function-name order-processor \
    --event-source-arn arn:aws:sqs:us-east-1:123456789012:orders-queue \
    --batch-size 10 \
    --function-response-types ReportBatchItemFailures
```

## CloudWatch Events / EventBridge Trigger

CloudWatch Events and EventBridge trigger Lambda on schedule or in response to AWS events.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENTBRIDGE PATTERNS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Scheduled:                                                      │
│  ┌──────────┐    ┌─────────────┐    ┌──────────┐                │
│  │  Cron    │───▶│ EventBridge │───▶│  Lambda  │                │
│  │  Rule    │    │             │    │          │                │
│  └──────────┘    └─────────────┘    └──────────┘                │
│                                                                  │
│  Event-Based:                                                    │
│  ┌──────────┐    ┌─────────────┐    ┌──────────┐                │
│  │   EC2    │───▶│ EventBridge │───▶│  Lambda  │                │
│  │ State    │    │   Pattern   │    │(Respond) │                │
│  │ Change   │    │   Matching  │    │          │                │
│  └──────────┘    └─────────────┘    └──────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Scheduled Event Structure

```json
{
  "version": "0",
  "id": "event-id-123",
  "detail-type": "Scheduled Event",
  "source": "aws.events",
  "account": "123456789012",
  "time": "2024-01-15T12:00:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:events:us-east-1:123456789012:rule/my-scheduled-rule"
  ],
  "detail": {}
}
```

### EC2 State Change Event

```json
{
  "version": "0",
  "id": "event-id-456",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "2024-01-15T12:00:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"
  ],
  "detail": {
    "instance-id": "i-1234567890abcdef0",
    "state": "stopped"
  }
}
```

### Handler Example (Python)

```python
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client('ec2')
sns = boto3.client('sns')


def handler(event, context):
    """Handle EventBridge events"""
    logger.info(f"Event: {json.dumps(event)}")

    detail_type = event.get('detail-type')

    if detail_type == 'Scheduled Event':
        return handle_scheduled_event(event)
    elif detail_type == 'EC2 Instance State-change Notification':
        return handle_ec2_state_change(event)
    else:
        logger.warning(f"Unknown event type: {detail_type}")
        return {'handled': False}


def handle_scheduled_event(event):
    """Handle scheduled events (cron jobs)"""
    logger.info("Running scheduled task")

    # Example: Clean up old snapshots
    snapshots = ec2.describe_snapshots(
        OwnerIds=['self'],
        Filters=[
            {'Name': 'tag:AutoCleanup', 'Values': ['true']}
        ]
    )

    deleted = 0
    for snapshot in snapshots['Snapshots']:
        # Delete snapshots older than 30 days
        # (simplified - add actual date logic)
        ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
        deleted += 1
        logger.info(f"Deleted snapshot: {snapshot['SnapshotId']}")

    return {'deleted_snapshots': deleted}


def handle_ec2_state_change(event):
    """Handle EC2 instance state changes"""
    instance_id = event['detail']['instance-id']
    state = event['detail']['state']

    logger.info(f"Instance {instance_id} changed to {state}")

    if state == 'stopped':
        # Send notification
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:alerts',
            Subject='EC2 Instance Stopped',
            Message=f'Instance {instance_id} has stopped'
        )

    return {'instance': instance_id, 'state': state}
```

### CLI Configuration

```bash
# Create scheduled rule (every 5 minutes)
aws events put-rule \
    --name scheduled-cleanup \
    --schedule-expression "rate(5 minutes)"

# Create rule for EC2 state changes
aws events put-rule \
    --name ec2-state-changes \
    --event-pattern '{
        "source": ["aws.ec2"],
        "detail-type": ["EC2 Instance State-change Notification"],
        "detail": {
            "state": ["stopped", "terminated"]
        }
    }'

# Add Lambda permission
aws lambda add-permission \
    --function-name event-handler \
    --statement-id eventbridge-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:123456789012:rule/scheduled-cleanup

# Add target
aws events put-targets \
    --rule scheduled-cleanup \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789012:function:event-handler"
```

## Kinesis Trigger

Kinesis Data Streams trigger Lambda for real-time data processing.

### Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Producers│───▶│ Kinesis  │───▶│  Lambda  │───▶│   S3/     │
│          │    │  Stream  │    │          │    │ DynamoDB  │
└──────────┘    └──────────┘    └──────────┘    └───────────┘
```

### Event Structure

```json
{
  "Records": [
    {
      "kinesis": {
        "kinesisSchemaVersion": "1.0",
        "partitionKey": "user-123",
        "sequenceNumber": "49590338...",
        "data": "eyJ1c2VySWQiOiAidXNlci0xMjMiLCAiYWN0aW9uIjogImNsaWNrIn0=",
        "approximateArrivalTimestamp": 1642329600.123
      },
      "eventSource": "aws:kinesis",
      "eventVersion": "1.0",
      "eventID": "shardId-000000000000:49590338...",
      "eventName": "aws:kinesis:record",
      "invokeIdentityArn": "arn:aws:iam::123456789012:role/lambda-role",
      "awsRegion": "us-east-1",
      "eventSourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/my-stream"
    }
  ]
}
```

### Handler Example (Python)

```python
import json
import base64
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Process Kinesis stream records"""
    logger.info(f"Processing {len(event['Records'])} Kinesis records")

    processed = 0
    failed = 0

    for record in event['Records']:
        try:
            # Decode base64 data
            payload = base64.b64decode(record['kinesis']['data'])
            data = json.loads(payload)

            # Get metadata
            partition_key = record['kinesis']['partitionKey']
            sequence_number = record['kinesis']['sequenceNumber']
            arrival_time = record['kinesis']['approximateArrivalTimestamp']

            logger.info(f"Record: {data}")

            # Process the record
            process_record(data, partition_key)
            processed += 1

        except Exception as e:
            logger.error(f"Error processing record: {e}")
            failed += 1

    logger.info(f"Processed: {processed}, Failed: {failed}")

    return {
        'processed': processed,
        'failed': failed
    }


def process_record(data, partition_key):
    """Process individual Kinesis record"""
    user_id = data.get('userId')
    action = data.get('action')

    logger.info(f"User {user_id} performed action: {action}")

    # Business logic here
    # - Store in DynamoDB
    # - Send to analytics
    # - Trigger alerts
```

### CLI Configuration

```bash
# Create Kinesis stream
aws kinesis create-stream \
    --stream-name my-stream \
    --shard-count 1

# Create event source mapping
aws lambda create-event-source-mapping \
    --function-name stream-processor \
    --event-source-arn arn:aws:kinesis:us-east-1:123456789012:stream/my-stream \
    --starting-position LATEST \
    --batch-size 100 \
    --maximum-batching-window-in-seconds 5
```

## Event Source Mapping Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `BatchSize` | Records per invocation | 10-10,000 |
| `MaximumBatchingWindowInSeconds` | Wait time to gather records | 0-300 |
| `StartingPosition` | Where to start reading | LATEST/TRIM_HORIZON |
| `ParallelizationFactor` | Concurrent batches per shard | 1-10 |
| `MaximumRetryAttempts` | Retry failed batches | 0-10,000 |
| `BisectBatchOnFunctionError` | Split batch on error | true/false |

### Managing Event Source Mappings

```bash
# List mappings
aws lambda list-event-source-mappings \
    --function-name my-function

# Update mapping
aws lambda update-event-source-mapping \
    --uuid abc-123-def \
    --batch-size 100 \
    --maximum-batching-window-in-seconds 10

# Disable mapping
aws lambda update-event-source-mapping \
    --uuid abc-123-def \
    --enabled false

# Delete mapping
aws lambda delete-event-source-mapping \
    --uuid abc-123-def
```

## Summary

### Key Takeaways

1. **Multiple trigger types**: Synchronous, asynchronous, and poll-based
2. **Event structure varies**: Each service has unique event format
3. **Proper error handling**: Return failures for batch retry with SQS/Kinesis
4. **Permissions matter**: Lambda needs both execution role and resource-based policies

### Trigger Selection Guide

| Use Case | Trigger |
|----------|---------|
| REST/HTTP API | API Gateway |
| File processing | S3 |
| Database changes | DynamoDB Streams |
| Decoupled processing | SQS |
| Fan-out notifications | SNS |
| Scheduled tasks | EventBridge |
| Real-time streaming | Kinesis |

### Next Steps

Continue to [04-lambda-configuration.md](./04-lambda-configuration.md) to learn about configuring Lambda functions including memory, timeout, environment variables, and layers.
