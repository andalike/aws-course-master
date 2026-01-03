# S3 Event Processor Lambda - Node.js

A Lambda function that processes files uploaded to S3.

## Overview

This function demonstrates:
- S3 event trigger handling
- File downloading and processing
- Metadata extraction
- DynamoDB integration for storing metadata
- Error handling for batch processing

## Files

- `index.js` - Main Lambda function code
- `package.json` - Node.js dependencies

## Prerequisites

### S3 Bucket

Create an S3 bucket for uploads:

```bash
aws s3 mb s3://my-file-uploads-bucket
```

### DynamoDB Table

Create a table for file metadata:

```bash
aws dynamodb create-table \
    --table-name file-metadata \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### IAM Role

Required permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:HeadObject"
            ],
            "Resource": "arn:aws:s3:::my-file-uploads-bucket/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/file-metadata"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

## Deployment

### Package and Deploy

```bash
# Install dependencies
npm install

# Create deployment package
zip -r function.zip index.js node_modules package.json

# Create Lambda function
aws lambda create-function \
    --function-name s3-processor-nodejs \
    --runtime nodejs20.x \
    --handler index.handler \
    --zip-file fileb://function.zip \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-s3-role \
    --environment Variables="{METADATA_TABLE=file-metadata,PROCESSED_PREFIX=processed/}" \
    --timeout 30 \
    --memory-size 256

# Add S3 trigger permission
aws lambda add-permission \
    --function-name s3-processor-nodejs \
    --statement-id s3-trigger \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-file-uploads-bucket \
    --source-account YOUR_ACCOUNT_ID

# Configure S3 bucket notification
aws s3api put-bucket-notification-configuration \
    --bucket my-file-uploads-bucket \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [
            {
                "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT:function:s3-processor-nodejs",
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
    }'
```

## S3 Event Structure

When a file is uploaded to S3, the event looks like:

```json
{
    "Records": [
        {
            "eventSource": "aws:s3",
            "eventName": "ObjectCreated:Put",
            "eventTime": "2024-01-15T10:30:00.000Z",
            "s3": {
                "bucket": {
                    "name": "my-file-uploads-bucket"
                },
                "object": {
                    "key": "uploads/document.pdf",
                    "size": 102400
                }
            }
        }
    ]
}
```

## Supported File Types

| Content Type | Processing |
|-------------|------------|
| image/* | Metadata extraction (dimensions, format) |
| text/* | Line/word/character count |
| application/json | JSON validation |
| Other | Metadata only |

## Testing

### Upload a file to trigger processing

```bash
# Upload a test file
aws s3 cp test.json s3://my-file-uploads-bucket/uploads/test.json

# Check CloudWatch logs
aws logs tail /aws/lambda/s3-processor-nodejs --follow

# Verify metadata in DynamoDB
aws dynamodb get-item \
    --table-name file-metadata \
    --key '{"id": {"S": "uploads/test.json"}}'
```

### Direct Lambda invocation

```bash
aws lambda invoke \
    --function-name s3-processor-nodejs \
    --payload '{
        "Records": [{
            "eventSource": "aws:s3",
            "eventName": "ObjectCreated:Put",
            "eventTime": "2024-01-15T10:00:00.000Z",
            "s3": {
                "bucket": {"name": "my-file-uploads-bucket"},
                "object": {"key": "uploads/test.json", "size": 1024}
            }
        }]
    }' \
    --cli-binary-format raw-in-base64-out \
    response.json
```

## Architecture

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│    S3        │────>│   Lambda Function   │────>│  DynamoDB    │
│  (Upload)    │     │  (s3-processor)     │     │  (Metadata)  │
└──────────────┘     └─────────────────────┘     └──────────────┘
                              │
                              v
                     ┌──────────────┐
                     │     S3       │
                     │ (Processed)  │
                     └──────────────┘
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| METADATA_TABLE | DynamoDB table name | file-metadata |
| PROCESSED_PREFIX | Prefix for processed files | processed/ |

## Cleanup

```bash
# Delete Lambda function
aws lambda delete-function --function-name s3-processor-nodejs

# Empty and delete S3 bucket
aws s3 rm s3://my-file-uploads-bucket --recursive
aws s3 rb s3://my-file-uploads-bucket

# Delete DynamoDB table
aws dynamodb delete-table --table-name file-metadata
```

## Extending the Function

### Add Image Thumbnail Generation

```javascript
const sharp = require('sharp');

async function generateThumbnail(buffer) {
    return sharp(buffer)
        .resize(200, 200, { fit: 'inside' })
        .jpeg({ quality: 80 })
        .toBuffer();
}
```

### Add SNS Notification

```javascript
const { SNSClient, PublishCommand } = require('@aws-sdk/client-sns');
const sns = new SNSClient({});

async function notifyProcessingComplete(fileInfo) {
    await sns.send(new PublishCommand({
        TopicArn: process.env.NOTIFICATION_TOPIC,
        Message: JSON.stringify(fileInfo),
        Subject: 'File Processing Complete'
    }));
}
```
