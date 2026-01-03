# CloudWatch Logs

## Introduction

CloudWatch Logs enables you to centralize logs from all your systems, applications, and AWS services in a single, highly scalable service. You can easily view, search, and analyze logs, create alarms, and stream logs to other services.

---

## Log Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CloudWatch Logs Architecture                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Log Sources                       CloudWatch Logs                           │
│  ┌─────────────┐                  ┌────────────────────────────────────────┐│
│  │   EC2       │──┐               │                                        ││
│  │ (CW Agent)  │  │               │  Log Group: /var/log/messages          ││
│  └─────────────┘  │               │  ┌────────────────────────────────┐   ││
│                   │               │  │  Log Stream: i-abc123          │   ││
│  ┌─────────────┐  │               │  │  ┌──────────────────────────┐  │   ││
│  │   Lambda    │──┼──────────────►│  │  │ Log Event (timestamp)   │  │   ││
│  │             │  │               │  │  │ Log Event (timestamp)   │  │   ││
│  └─────────────┘  │               │  │  │ Log Event (timestamp)   │  │   ││
│                   │               │  │  └──────────────────────────┘  │   ││
│  ┌─────────────┐  │               │  └────────────────────────────────┘   ││
│  │   ECS/EKS   │──┤               │  ┌────────────────────────────────┐   ││
│  │             │  │               │  │  Log Stream: i-def456          │   ││
│  └─────────────┘  │               │  │  ┌──────────────────────────┐  │   ││
│                   │               │  │  │ Log Event (timestamp)   │  │   ││
│  ┌─────────────┐  │               │  │  └──────────────────────────┘  │   ││
│  │ API Gateway │──┤               │  └────────────────────────────────┘   ││
│  │             │  │               │                                        ││
│  └─────────────┘  │               └────────────────────────────────────────┘│
│                   │                                                          │
│  ┌─────────────┐  │               ┌────────────────────────────────────────┐│
│  │    RDS      │──┤               │  Log Group: /aws/lambda/my-function    ││
│  │   (Logs)    │  │               │  ┌────────────────────────────────┐   ││
│  └─────────────┘  │               │  │  Log Stream: 2024/01/15/[$LATEST]│   ││
│                   │               │  └────────────────────────────────┘   ││
│  ┌─────────────┐  │               └────────────────────────────────────────┘│
│  │ CloudTrail  │──┘                                                          │
│  │             │                                                             │
│  └─────────────┘                                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### Log Groups

A log group is a collection of log streams that share the same retention, monitoring, and access control settings.

**Naming Conventions**:
```
# AWS Services (automatic)
/aws/lambda/function-name
/aws/rds/instance/database-id/log-type
/aws/apigateway/api-id/stage
/aws/codebuild/project-name
/aws/ecs/container-name

# Custom Applications (recommended)
/application/app-name/environment
/var/log/log-file-name
/custom/team-name/service-name
```

### Log Streams

A log stream is a sequence of log events that share the same source.

**Common Stream Naming**:
```
# EC2 Instances
i-1234567890abcdef0

# Lambda Functions
2024/01/15/[$LATEST]abc123def456

# ECS Containers
ecs/container-name/task-id

# Custom
hostname/process-id
environment/instance-id
```

### Log Events

Individual log entries with a timestamp and message.

```json
{
  "timestamp": 1705312200000,
  "message": "2024-01-15T10:30:00.000Z INFO Processing request id=abc123 user=john"
}
```

---

## Creating and Managing Log Groups

### AWS CLI

```bash
# Create log group
aws logs create-log-group \
    --log-group-name /application/my-app/production

# Create with KMS encryption
aws logs create-log-group \
    --log-group-name /application/my-app/production \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abcd1234-ab12-cd34-ef56-abcdef123456

# Set retention policy
aws logs put-retention-policy \
    --log-group-name /application/my-app/production \
    --retention-in-days 30

# Add tags
aws logs tag-log-group \
    --log-group-name /application/my-app/production \
    --tags Environment=Production,Team=Backend,CostCenter=12345

# List log groups
aws logs describe-log-groups \
    --log-group-name-prefix /application/

# Delete log group
aws logs delete-log-group \
    --log-group-name /application/my-app/staging
```

### CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudWatch Log Groups

Resources:
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /application/my-app/production
      RetentionInDays: 30
      KmsKeyId: !GetAtt LogEncryptionKey.Arn
      Tags:
        - Key: Environment
          Value: Production
        - Key: Team
          Value: Backend

  LogEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: Key for CloudWatch Logs encryption
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow CloudWatch Logs
            Effect: Allow
            Principal:
              Service: !Sub 'logs.${AWS::Region}.amazonaws.com'
            Action:
              - kms:Encrypt*
              - kms:Decrypt*
              - kms:ReEncrypt*
              - kms:GenerateDataKey*
              - kms:Describe*
            Resource: '*'
            Condition:
              ArnLike:
                kms:EncryptionContext:aws:logs:arn: !Sub 'arn:aws:logs:${AWS::Region}:${AWS::AccountId}:*'
```

---

## Retention Policies

### Available Retention Periods

| Days | Use Case |
|------|----------|
| 1 | Development/testing |
| 3 | Short-term debugging |
| 5 | Sprint-level debugging |
| 7 | Weekly review cycle |
| 14 | Two-week retention |
| 30 | Monthly retention |
| 60 | Bi-monthly retention |
| 90 | Quarterly retention |
| 120 | Four months |
| 150 | Five months |
| 180 | Six months |
| 365 | Annual retention |
| 400 | Extended annual |
| 545 | 18 months |
| 731 | Two years |
| 1096 | Three years |
| 1827 | Five years |
| 2192 | Six years |
| 2557 | Seven years |
| 2922 | Eight years |
| 3288 | Nine years |
| 3653 | Ten years |
| Never Expire | Indefinite retention |

### Setting Retention

```bash
# Set retention to 30 days
aws logs put-retention-policy \
    --log-group-name /application/my-app/production \
    --retention-in-days 30

# Remove retention (never expire)
aws logs delete-retention-policy \
    --log-group-name /application/my-app/production
```

### Cost Considerations

```
Storage Pricing (approximate):
- Ingestion: $0.50 per GB
- Storage: $0.03 per GB per month
- Analysis (Logs Insights): $0.005 per GB scanned

Example Monthly Cost:
- 100 GB ingested/month: $50 ingestion
- 100 GB stored (30-day retention): $3 storage
- 50 GB analyzed: $0.25 analysis
- Total: ~$53.25/month
```

---

## Sending Logs to CloudWatch

### From Lambda Functions

Lambda automatically sends logs to CloudWatch. Configure in the function:

```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Processing event")
    logger.debug("Event details: %s", event)

    try:
        # Process event
        result = process_event(event)
        logger.info("Successfully processed: %s", result)
        return result
    except Exception as e:
        logger.error("Error processing event: %s", str(e))
        raise
```

### From EC2 (Using CloudWatch Agent)

See [07-cloudwatch-agent.md](07-cloudwatch-agent.md) for detailed configuration.

### From Applications (SDK)

```python
import boto3
import time

logs = boto3.client('logs')

log_group = '/application/my-app/production'
log_stream = f'host-{socket.gethostname()}'

# Create log stream if not exists
try:
    logs.create_log_stream(
        logGroupName=log_group,
        logStreamName=log_stream
    )
except logs.exceptions.ResourceAlreadyExistsException:
    pass

# Send log events
logs.put_log_events(
    logGroupName=log_group,
    logStreamName=log_stream,
    logEvents=[
        {
            'timestamp': int(time.time() * 1000),
            'message': 'Application started successfully'
        },
        {
            'timestamp': int(time.time() * 1000),
            'message': 'Connected to database'
        }
    ]
)
```

### From Docker Containers

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    image: my-app:latest
    logging:
      driver: awslogs
      options:
        awslogs-group: /ecs/my-app
        awslogs-region: us-east-1
        awslogs-stream-prefix: web
```

---

## Metric Filters

Metric filters extract metric observations from log events and publish them to CloudWatch Metrics.

### Creating Metric Filters

```bash
# Count ERROR occurrences
aws logs put-metric-filter \
    --log-group-name /application/my-app/production \
    --filter-name ErrorCount \
    --filter-pattern "ERROR" \
    --metric-transformations \
        metricName=ErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0

# Extract numeric value
aws logs put-metric-filter \
    --log-group-name /application/my-app/production \
    --filter-name ResponseTime \
    --filter-pattern '[timestamp, requestId, level, msg, responseTime]' \
    --metric-transformations \
        metricName=ResponseTime,metricNamespace=MyApp,metricValue='$responseTime',unit=Milliseconds

# JSON log filter
aws logs put-metric-filter \
    --log-group-name /application/my-app/production \
    --filter-name OrderValue \
    --filter-pattern '{ $.eventType = "ORDER_PLACED" }' \
    --metric-transformations \
        metricName=OrderValue,metricNamespace=MyApp,metricValue='$.orderValue',unit=None
```

### Filter Pattern Syntax

#### Simple Text Matching

```
# Match exact text
ERROR

# Match any of these terms
?ERROR ?WARN ?CRITICAL

# Exclude term
-DEBUG

# Multiple terms (AND)
ERROR database connection

# Case sensitive by default
```

#### Space-Delimited Log Format

```
# Log format: timestamp requestId level message responseTime
# Example: 2024-01-15T10:30:00 abc123 INFO "Request completed" 250

# Extract all fields
[timestamp, requestId, level, message, responseTime]

# Filter on specific field
[timestamp, requestId, level = ERROR, ...]

# Numeric comparison
[..., responseTime > 1000]

# String matching
[..., level = "ERROR", ...]

# Wildcard
[timestamp, requestId, level, ...]
```

#### JSON Log Format

```json
{"timestamp": "2024-01-15T10:30:00", "level": "ERROR", "message": "Connection failed", "responseTime": 250}
```

```bash
# Match any ERROR level
{ $.level = "ERROR" }

# Numeric comparison
{ $.responseTime > 1000 }

# String contains
{ $.message = "*connection*" }

# Multiple conditions (AND)
{ $.level = "ERROR" && $.responseTime > 500 }

# OR condition
{ $.level = "ERROR" || $.level = "CRITICAL" }

# Nested JSON
{ $.request.userId = "user123" }

# Check field exists
{ $.errorCode EXISTS }

# Check field not exists
{ $.errorCode NOT EXISTS }

# IS NULL check
{ $.value IS NULL }

# NOT NULL check
{ $.value NOT NULL }
```

### CloudFormation Metric Filter

```yaml
Resources:
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterName: ErrorFilter
      FilterPattern: '{ $.level = "ERROR" }'
      MetricTransformations:
        - MetricName: ApplicationErrors
          MetricNamespace: MyApp/Logs
          MetricValue: '1'
          DefaultValue: 0
          Unit: Count
          Dimensions:
            - Key: Environment
              Value: Production

  LatencyMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterName: LatencyFilter
      FilterPattern: '{ $.responseTime >= 0 }'
      MetricTransformations:
        - MetricName: ResponseTime
          MetricNamespace: MyApp/Logs
          MetricValue: '$.responseTime'
          Unit: Milliseconds
```

### Create Alarm from Metric Filter

```yaml
Resources:
  ErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighErrorRate
      AlarmDescription: Error rate exceeds threshold
      MetricName: ApplicationErrors
      Namespace: MyApp/Logs
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic
```

---

## Subscription Filters

Subscription filters stream log data to other AWS services in real-time.

### Supported Destinations

| Destination | Use Case |
|-------------|----------|
| Kinesis Data Streams | Real-time processing, multiple consumers |
| Kinesis Data Firehose | Streaming to S3, Elasticsearch, Splunk |
| Lambda | Custom processing, transformation |
| CloudWatch Logs (Cross-Account) | Centralized logging |

### Lambda Subscription

```bash
# Grant CloudWatch Logs permission to invoke Lambda
aws lambda add-permission \
    --function-name log-processor \
    --statement-id cloudwatch-logs \
    --principal logs.amazonaws.com \
    --action lambda:InvokeFunction \
    --source-arn arn:aws:logs:us-east-1:123456789012:log-group:/application/my-app:*

# Create subscription filter
aws logs put-subscription-filter \
    --log-group-name /application/my-app/production \
    --filter-name error-processor \
    --filter-pattern "ERROR" \
    --destination-arn arn:aws:lambda:us-east-1:123456789012:function:log-processor
```

### Lambda Function to Process Logs

```python
import json
import base64
import gzip
import boto3

def lambda_handler(event, context):
    # Decode and decompress log data
    payload = base64.b64decode(event['awslogs']['data'])
    log_data = json.loads(gzip.decompress(payload))

    log_group = log_data['logGroup']
    log_stream = log_data['logStream']

    for log_event in log_data['logEvents']:
        timestamp = log_event['timestamp']
        message = log_event['message']

        # Process the log event
        print(f"Processing: {message}")

        # Example: Send to external system
        # send_to_external_system(log_group, log_stream, message)

    return {'statusCode': 200}
```

### Kinesis Data Firehose Subscription

```bash
# Create subscription to Firehose
aws logs put-subscription-filter \
    --log-group-name /application/my-app/production \
    --filter-name firehose-stream \
    --filter-pattern "" \
    --destination-arn arn:aws:firehose:us-east-1:123456789012:deliverystream/log-delivery \
    --role-arn arn:aws:iam::123456789012:role/CWLtoFirehoseRole
```

### Cross-Account Log Streaming

```bash
# In destination account: Create destination
aws logs put-destination \
    --destination-name SharedLogDestination \
    --target-arn arn:aws:kinesis:us-east-1:DESTINATION_ACCOUNT:stream/shared-logs \
    --role-arn arn:aws:iam::DESTINATION_ACCOUNT:role/CWLtoKinesisRole

# Set destination policy
aws logs put-destination-policy \
    --destination-name SharedLogDestination \
    --access-policy '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "AWS": "SOURCE_ACCOUNT_ID"
            },
            "Action": "logs:PutSubscriptionFilter",
            "Resource": "arn:aws:logs:us-east-1:DESTINATION_ACCOUNT:destination:SharedLogDestination"
        }]
    }'

# In source account: Create subscription
aws logs put-subscription-filter \
    --log-group-name /application/my-app/production \
    --filter-name cross-account \
    --filter-pattern "" \
    --destination-arn arn:aws:logs:us-east-1:DESTINATION_ACCOUNT:destination:SharedLogDestination
```

---

## Exporting Logs

### Export to S3

```bash
# Create export task
aws logs create-export-task \
    --log-group-name /application/my-app/production \
    --from 1704067200000 \
    --to 1704153600000 \
    --destination my-logs-bucket \
    --destination-prefix exports/my-app/

# Check export status
aws logs describe-export-tasks \
    --task-id abc123-def456-ghi789
```

### S3 Bucket Policy for Export

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "logs.us-east-1.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::my-logs-bucket"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "logs.us-east-1.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-logs-bucket/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
```

---

## Live Tail

Live Tail provides real-time streaming of log events for debugging.

### Using AWS Console

1. Navigate to CloudWatch Logs
2. Select log group
3. Click "Live Tail" button
4. Optionally add filter patterns
5. View real-time log stream

### Using AWS CLI

```bash
# Start live tail session
aws logs start-live-tail \
    --log-group-identifiers arn:aws:logs:us-east-1:123456789012:log-group:/application/my-app \
    --log-stream-names stream-1 stream-2 \
    --log-event-filter-pattern "ERROR"
```

---

## Log Insights

CloudWatch Logs Insights provides interactive querying. See [05-cloudwatch-logs-insights.md](05-cloudwatch-logs-insights.md) for detailed query syntax.

### Quick Query Examples

```sql
-- Find all errors in last hour
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Count errors by type
fields @message
| filter @message like /ERROR/
| parse @message "ERROR: *" as errorType
| stats count(*) by errorType

-- Latency percentiles
fields @timestamp, responseTime
| filter responseTime > 0
| stats avg(responseTime), percentile(responseTime, 95), max(responseTime) by bin(5m)
```

---

## CloudFormation Complete Example

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Complete CloudWatch Logs Setup

Parameters:
  Environment:
    Type: String
    Default: production
  RetentionDays:
    Type: Number
    Default: 30

Resources:
  # Log Group
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub /application/my-app/${Environment}
      RetentionInDays: !Ref RetentionDays
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Metric Filter - Error Count
  ErrorMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterName: ErrorCount
      FilterPattern: '{ $.level = "ERROR" }'
      MetricTransformations:
        - MetricName: ErrorCount
          MetricNamespace: !Sub MyApp/${Environment}
          MetricValue: '1'
          DefaultValue: 0

  # Metric Filter - Latency
  LatencyMetricFilter:
    Type: AWS::Logs::MetricFilter
    Properties:
      LogGroupName: !Ref ApplicationLogGroup
      FilterName: Latency
      FilterPattern: '{ $.responseTime >= 0 }'
      MetricTransformations:
        - MetricName: ResponseTime
          MetricNamespace: !Sub MyApp/${Environment}
          MetricValue: '$.responseTime'
          Unit: Milliseconds

  # Error Alarm
  ErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${Environment}-HighErrorRate
      MetricName: ErrorCount
      Namespace: !Sub MyApp/${Environment}
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic

  # SNS Topic
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${Environment}-log-alerts

Outputs:
  LogGroupName:
    Value: !Ref ApplicationLogGroup
  LogGroupArn:
    Value: !GetAtt ApplicationLogGroup.Arn
```

---

## Best Practices

### Log Formatting

```python
# Use structured JSON logging
import json
import logging
import sys

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Configure logger
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Log Levels

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed debugging information |
| INFO | General operational information |
| WARN | Warning conditions |
| ERROR | Error conditions |
| CRITICAL | Critical errors requiring immediate attention |

### Cost Optimization

1. **Set appropriate retention** - Don't keep logs longer than needed
2. **Use sampling** for high-volume logs
3. **Archive to S3** for long-term storage
4. **Use log levels** - Don't log DEBUG in production
5. **Compress before sending** when using SDK

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Logs not appearing | Check IAM permissions, verify log group exists |
| High ingestion costs | Reduce log verbosity, increase sampling |
| Slow queries | Use specific time ranges, add filters |
| Missing logs | Check CloudWatch Agent status, verify configuration |

### Debugging Commands

```bash
# Check log group exists
aws logs describe-log-groups \
    --log-group-name-prefix /application/my-app

# View recent log streams
aws logs describe-log-streams \
    --log-group-name /application/my-app/production \
    --order-by LastEventTime \
    --descending

# Get recent log events
aws logs get-log-events \
    --log-group-name /application/my-app/production \
    --log-stream-name stream-name \
    --limit 100

# Filter logs
aws logs filter-log-events \
    --log-group-name /application/my-app/production \
    --filter-pattern "ERROR" \
    --start-time $(date -d '1 hour ago' +%s)000
```

---

## Next Steps

Continue to the next sections:
- [05-cloudwatch-logs-insights.md](05-cloudwatch-logs-insights.md) - Advanced log querying
- [06-cloudwatch-dashboards.md](06-cloudwatch-dashboards.md) - Visualize logs and metrics
