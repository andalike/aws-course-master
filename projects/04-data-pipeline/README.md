# Project 4: Create an Event-Driven Data Pipeline

## Project Overview

Build an event-driven data pipeline that processes files uploaded to S3, transforms the data using Lambda, and sends notifications via SNS/SQS. This project demonstrates modern data processing patterns on AWS.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       EVENT-DRIVEN DATA PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────┐                                                                │
│  │   Users     │                                                                │
│  │  Upload     │                                                                │
│  │   Files     │                                                                │
│  └──────┬──────┘                                                                │
│         │                                                                        │
│         ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      S3 BUCKET (Input)                                   │   │
│  │  s3://data-pipeline-input-xxx/                                           │   │
│  │  ├── raw/                                                                │   │
│  │  │   └── data.csv  ←── Upload triggers event                            │   │
│  │  └── processed/                                                          │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│                                   │ S3 Event Notification                       │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         SQS QUEUE                                        │   │
│  │  (Decouples S3 from Lambda, provides retry capability)                   │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│                                   │ Triggers Lambda                             │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     LAMBDA FUNCTION                                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐     │   │
│  │  │ 1. Read file from S3                                            │     │   │
│  │  │ 2. Parse CSV data                                               │     │   │
│  │  │ 3. Transform/validate data                                      │     │   │
│  │  │ 4. Write processed data to output bucket                        │     │   │
│  │  │ 5. Store metadata in DynamoDB                                   │     │   │
│  │  │ 6. Publish notification to SNS                                  │     │   │
│  │  └────────────────────────────────────────────────────────────────┘     │   │
│  └───────┬────────────────────────┬─────────────────────────┬──────────────┘   │
│          │                        │                         │                   │
│          ▼                        ▼                         ▼                   │
│  ┌───────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐   │
│  │  S3 (Output)  │    │    DynamoDB     │    │         SNS Topic           │   │
│  │   processed/  │    │   (Metadata)    │    │                             │   │
│  │  - JSON files │    │ - file_id       │    │   ┌─────────┐ ┌─────────┐  │   │
│  │  - Reports    │    │ - record_count  │    │   │  Email  │ │ Lambda  │  │   │
│  └───────────────┘    │ - status        │    │   │         │ │         │  │   │
│                       │ - timestamp     │    │   └─────────┘ └─────────┘  │   │
│                       └─────────────────┘    └─────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     DEAD LETTER QUEUE                                    │   │
│  │  (Captures failed processing for analysis and retry)                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Learning Objectives

By completing this project, you will:

- [ ] Configure S3 event notifications
- [ ] Set up SQS queues with dead letter queues
- [ ] Create Lambda functions triggered by SQS
- [ ] Process CSV data with Python
- [ ] Store metadata in DynamoDB
- [ ] Send notifications via SNS
- [ ] Implement error handling and retries
- [ ] Monitor pipeline with CloudWatch

---

## Prerequisites

- Completed Modules 1-8 of this course
- AWS Account with Free Tier
- Python 3.9+ installed
- AWS SAM CLI installed

---

## Step 1: SAM Template

### template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Event-Driven Data Pipeline

Parameters:
  Environment:
    Type: String
    Default: dev
  NotificationEmail:
    Type: String
    Description: Email for pipeline notifications

Resources:
  # S3 Buckets
  InputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub data-pipeline-input-${AWS::AccountId}-${Environment}
      NotificationConfiguration:
        QueueConfigurations:
          - Event: s3:ObjectCreated:*
            Queue: !GetAtt ProcessingQueue.Arn
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: raw/
                  - Name: suffix
                    Value: .csv

  OutputBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub data-pipeline-output-${AWS::AccountId}-${Environment}

  # SQS Queues
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub data-processing-queue-${Environment}
      VisibilityTimeout: 300
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
        maxReceiveCount: 3

  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub data-processing-dlq-${Environment}
      MessageRetentionPeriod: 1209600  # 14 days

  # Queue Policy for S3
  ProcessingQueuePolicy:
    Type: AWS::SQS::QueuePolicy
    Properties:
      Queues:
        - !Ref ProcessingQueue
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: s3.amazonaws.com
            Action: sqs:SendMessage
            Resource: !GetAtt ProcessingQueue.Arn
            Condition:
              ArnLike:
                aws:SourceArn: !Sub arn:aws:s3:::data-pipeline-input-${AWS::AccountId}-${Environment}

  # DynamoDB Table
  MetadataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub pipeline-metadata-${Environment}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: file_id
          AttributeType: S
        - AttributeName: processed_at
          AttributeType: S
      KeySchema:
        - AttributeName: file_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: processed-at-index
          KeySchema:
            - AttributeName: processed_at
              KeyType: HASH
          Projection:
            ProjectionType: ALL

  # SNS Topic
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub pipeline-notifications-${Environment}

  EmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      Protocol: email
      TopicArn: !Ref NotificationTopic
      Endpoint: !Ref NotificationEmail

  # Lambda Function
  ProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub data-processor-${Environment}
      Handler: handler.process_file
      Runtime: python3.9
      Timeout: 300
      MemorySize: 512
      CodeUri: src/
      Environment:
        Variables:
          OUTPUT_BUCKET: !Ref OutputBucket
          METADATA_TABLE: !Ref MetadataTable
          SNS_TOPIC_ARN: !Ref NotificationTopic
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref InputBucket
        - S3CrudPolicy:
            BucketName: !Ref OutputBucket
        - DynamoDBCrudPolicy:
            TableName: !Ref MetadataTable
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt NotificationTopic.TopicName
        - SQSPollerPolicy:
            QueueName: !GetAtt ProcessingQueue.QueueName
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt ProcessingQueue.Arn
            BatchSize: 1

  # CloudWatch Alarms
  DLQAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub pipeline-dlq-alarm-${Environment}
      AlarmDescription: Alert when messages appear in DLQ
      MetricName: ApproximateNumberOfMessagesVisible
      Namespace: AWS/SQS
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 1
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      Dimensions:
        - Name: QueueName
          Value: !GetAtt DeadLetterQueue.QueueName
      AlarmActions:
        - !Ref NotificationTopic

Outputs:
  InputBucketName:
    Value: !Ref InputBucket
  OutputBucketName:
    Value: !Ref OutputBucket
  ProcessingQueueUrl:
    Value: !Ref ProcessingQueue
  NotificationTopicArn:
    Value: !Ref NotificationTopic
```

---

## Step 2: Lambda Function

### src/handler.py

```python
import os
import json
import csv
import uuid
import boto3
from datetime import datetime
from io import StringIO
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Environment variables
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET')
METADATA_TABLE = os.environ.get('METADATA_TABLE')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')


def process_file(event, context):
    """Process CSV files from S3 via SQS trigger."""
    logger.info(f"Received event: {json.dumps(event)}")

    for record in event['Records']:
        try:
            # Parse SQS message containing S3 event
            message_body = json.loads(record['body'])

            # Handle S3 test events
            if 'Event' in message_body and message_body['Event'] == 's3:TestEvent':
                logger.info("Received S3 test event, skipping...")
                continue

            # Get S3 object info
            s3_event = message_body['Records'][0]
            bucket = s3_event['s3']['bucket']['name']
            key = s3_event['s3']['object']['key']

            logger.info(f"Processing file: s3://{bucket}/{key}")

            # Process the file
            result = process_csv(bucket, key)

            # Store metadata
            store_metadata(result)

            # Send notification
            send_notification(result)

            logger.info(f"Successfully processed: {key}")

        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            raise  # Re-raise to trigger DLQ after retries


def process_csv(bucket: str, key: str) -> dict:
    """Read and process CSV file from S3."""
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # Download file from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')

    # Parse CSV
    reader = csv.DictReader(StringIO(content))
    rows = list(reader)

    logger.info(f"Parsed {len(rows)} rows from CSV")

    # Transform data
    processed_data = transform_data(rows)

    # Save processed data to output bucket
    output_key = f"processed/{file_id}.json"
    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=output_key,
        Body=json.dumps(processed_data, indent=2),
        ContentType='application/json'
    )

    # Generate summary report
    summary = generate_summary(rows, processed_data)
    summary_key = f"reports/{file_id}_summary.json"
    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=summary_key,
        Body=json.dumps(summary, indent=2),
        ContentType='application/json'
    )

    return {
        'file_id': file_id,
        'source_bucket': bucket,
        'source_key': key,
        'output_bucket': OUTPUT_BUCKET,
        'output_key': output_key,
        'summary_key': summary_key,
        'record_count': len(rows),
        'processed_count': len(processed_data['records']),
        'error_count': len(processed_data.get('errors', [])),
        'processed_at': timestamp,
        'status': 'success'
    }


def transform_data(rows: list) -> dict:
    """Transform and validate CSV data."""
    processed_records = []
    errors = []

    for i, row in enumerate(rows):
        try:
            # Example transformation logic
            processed_record = {
                'id': str(uuid.uuid4()),
                'original_row': i + 1,
                'data': {}
            }

            # Process each field
            for key, value in row.items():
                # Clean field names
                clean_key = key.strip().lower().replace(' ', '_')

                # Clean and validate values
                clean_value = value.strip() if value else None

                # Type conversion for numeric fields
                if clean_key in ['amount', 'price', 'quantity', 'total']:
                    try:
                        clean_value = float(clean_value) if clean_value else 0
                    except ValueError:
                        clean_value = 0

                processed_record['data'][clean_key] = clean_value

            # Add metadata
            processed_record['processed_at'] = datetime.utcnow().isoformat()
            processed_records.append(processed_record)

        except Exception as e:
            errors.append({
                'row': i + 1,
                'error': str(e),
                'original_data': row
            })

    return {
        'records': processed_records,
        'errors': errors,
        'total_processed': len(processed_records),
        'total_errors': len(errors)
    }


def generate_summary(original_rows: list, processed_data: dict) -> dict:
    """Generate a summary report of the processing."""
    records = processed_data['records']

    # Calculate statistics
    summary = {
        'total_input_rows': len(original_rows),
        'total_processed': len(records),
        'total_errors': len(processed_data.get('errors', [])),
        'success_rate': round(len(records) / max(len(original_rows), 1) * 100, 2),
        'generated_at': datetime.utcnow().isoformat()
    }

    # Field statistics
    if records:
        field_stats = {}
        for key in records[0]['data'].keys():
            values = [r['data'].get(key) for r in records]

            # Numeric stats
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                field_stats[key] = {
                    'type': 'numeric',
                    'count': len(numeric_values),
                    'sum': sum(numeric_values),
                    'avg': round(sum(numeric_values) / len(numeric_values), 2),
                    'min': min(numeric_values),
                    'max': max(numeric_values)
                }
            else:
                # String stats
                non_null = [v for v in values if v]
                field_stats[key] = {
                    'type': 'string',
                    'count': len(non_null),
                    'unique': len(set(non_null))
                }

        summary['field_statistics'] = field_stats

    return summary


def store_metadata(result: dict) -> None:
    """Store processing metadata in DynamoDB."""
    table = dynamodb.Table(METADATA_TABLE)

    item = {
        'file_id': result['file_id'],
        'source_bucket': result['source_bucket'],
        'source_key': result['source_key'],
        'output_bucket': result['output_bucket'],
        'output_key': result['output_key'],
        'record_count': result['record_count'],
        'processed_count': result['processed_count'],
        'error_count': result['error_count'],
        'processed_at': result['processed_at'],
        'status': result['status']
    }

    table.put_item(Item=item)
    logger.info(f"Stored metadata for file_id: {result['file_id']}")


def send_notification(result: dict) -> None:
    """Send processing notification via SNS."""
    subject = f"Data Pipeline: File Processed Successfully"

    message = f"""
Data Pipeline Processing Complete
=================================

File ID: {result['file_id']}
Source: s3://{result['source_bucket']}/{result['source_key']}
Output: s3://{result['output_bucket']}/{result['output_key']}

Statistics:
- Records Processed: {result['processed_count']}
- Errors: {result['error_count']}
- Status: {result['status']}

Processed At: {result['processed_at']}
"""

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=subject,
        Message=message
    )

    logger.info("Notification sent successfully")
```

---

## Step 3: Deploy and Test

```bash
# Build and deploy
sam build
sam deploy --guided \
    --parameter-overrides NotificationEmail=your@email.com

# Get output values
INPUT_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name data-pipeline \
    --query 'Stacks[0].Outputs[?OutputKey==`InputBucketName`].OutputValue' \
    --output text)

# Create sample CSV
cat > sample-data.csv << 'EOF'
name,email,amount,date
John Doe,john@example.com,100.50,2024-01-15
Jane Smith,jane@example.com,250.00,2024-01-16
Bob Wilson,bob@example.com,75.25,2024-01-17
Alice Brown,alice@example.com,300.00,2024-01-18
EOF

# Upload to trigger pipeline
aws s3 cp sample-data.csv s3://$INPUT_BUCKET/raw/sample-data.csv

# Monitor logs
sam logs -n ProcessorFunction --tail
```

---

## Verification Checklist

- [ ] S3 event triggers SQS
- [ ] Lambda processes CSV correctly
- [ ] Processed JSON saved to output bucket
- [ ] Metadata stored in DynamoDB
- [ ] Email notification received
- [ ] DLQ alarm configured

---

**Congratulations!** You've built a production-ready data pipeline!

[← Back to Projects](../) | [Next: Complete Infrastructure →](../05-complete-infrastructure/)
