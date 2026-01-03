# SNS for Alert Notifications

## Introduction

Amazon Simple Notification Service (SNS) is a fully managed pub/sub messaging service that enables you to decouple microservices, distributed systems, and serverless applications. In the context of monitoring, SNS serves as the primary mechanism for delivering CloudWatch alarm notifications to various endpoints including email, SMS, Lambda functions, and more.

---

## SNS Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Amazon SNS Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                          Publishers                                      ││
│  │                                                                          ││
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 ││
│  │   │  CloudWatch  │  │  EventBridge │  │ Applications │                 ││
│  │   │   Alarms     │  │              │  │              │                 ││
│  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 ││
│  │          │                  │                  │                         ││
│  │          └──────────────────┼──────────────────┘                         ││
│  │                             │                                            ││
│  └─────────────────────────────┼────────────────────────────────────────────┘│
│                                │                                             │
│                                ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           SNS Topic                                      ││
│  │                                                                          ││
│  │   Topic ARN: arn:aws:sns:us-east-1:123456789012:alerts                 ││
│  │                                                                          ││
│  │   ┌───────────────────────────────────────────────────────────────────┐ ││
│  │   │                    Message Filtering                               │ ││
│  │   │    (Route messages to specific subscribers based on attributes)   │ ││
│  │   └───────────────────────────────────────────────────────────────────┘ ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                │                                             │
│     ┌──────────────┬──────────┼──────────┬──────────────┬──────────────┐   │
│     ▼              ▼          ▼          ▼              ▼              ▼   │
│ ┌────────┐   ┌────────┐  ┌────────┐  ┌────────┐   ┌────────┐   ┌────────┐ │
│ │ Email  │   │  SMS   │  │ Lambda │  │  SQS   │   │ HTTP/S │   │ Mobile │ │
│ │        │   │        │  │        │  │ Queue  │   │Endpoint│   │  Push  │ │
│ └────────┘   └────────┘  └────────┘  └────────┘   └────────┘   └────────┘ │
│                                                                             │
│                          Subscriptions (Endpoints)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### Topics

A topic is a logical access point and communication channel.

```bash
# Create an SNS topic
aws sns create-topic --name cloudwatch-alerts

# Output:
# {
#     "TopicArn": "arn:aws:sns:us-east-1:123456789012:cloudwatch-alerts"
# }

# List topics
aws sns list-topics

# Get topic attributes
aws sns get-topic-attributes \
    --topic-arn arn:aws:sns:us-east-1:123456789012:cloudwatch-alerts
```

### Subscriptions

Subscriptions define endpoints that receive messages from a topic.

| Protocol | Description | Use Case |
|----------|-------------|----------|
| Email | Email notifications | Human recipients |
| Email-JSON | Email with JSON payload | Technical recipients |
| SMS | Text messages | Critical alerts |
| HTTP/HTTPS | Webhook endpoints | Custom integrations |
| Lambda | AWS Lambda functions | Automated responses |
| SQS | Amazon SQS queues | Buffered processing |
| Application | Mobile push notifications | Mobile apps |
| Firehose | Kinesis Data Firehose | Log aggregation |

### Message Structure

```json
{
    "Type": "Notification",
    "MessageId": "12345678-1234-1234-1234-123456789012",
    "TopicArn": "arn:aws:sns:us-east-1:123456789012:cloudwatch-alerts",
    "Subject": "ALARM: HighCPUAlarm has triggered",
    "Message": "{\"AlarmName\":\"HighCPUAlarm\",\"AlarmDescription\":\"CPU too high\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed\",\"StateChangeTime\":\"2024-01-15T10:30:00.000+0000\"}",
    "Timestamp": "2024-01-15T10:30:05.123Z",
    "SignatureVersion": "1",
    "Signature": "...",
    "SigningCertURL": "https://sns.us-east-1.amazonaws.com/...",
    "UnsubscribeURL": "https://sns.us-east-1.amazonaws.com/..."
}
```

---

## Setting Up SNS Topics for Monitoring

### Creating Topics with CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: SNS Topics for Monitoring Alerts

Parameters:
  EmailAddress:
    Type: String
    Description: Email address for notifications
  PhoneNumber:
    Type: String
    Description: Phone number for SMS alerts (E.164 format)
    Default: ''

Conditions:
  HasPhoneNumber: !Not [!Equals [!Ref PhoneNumber, '']]

Resources:
  # Critical Alerts Topic (high priority)
  CriticalAlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: critical-alerts
      DisplayName: Critical System Alerts
      KmsMasterKeyId: alias/aws/sns
      Tags:
        - Key: Environment
          Value: Production
        - Key: Severity
          Value: Critical

  # Warning Alerts Topic
  WarningAlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: warning-alerts
      DisplayName: Warning Alerts
      Tags:
        - Key: Environment
          Value: Production
        - Key: Severity
          Value: Warning

  # Info Alerts Topic
  InfoAlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: info-alerts
      DisplayName: Informational Alerts
      Tags:
        - Key: Environment
          Value: Production
        - Key: Severity
          Value: Info

  # Email Subscription for Critical Alerts
  CriticalEmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref CriticalAlertsTopic
      Protocol: email
      Endpoint: !Ref EmailAddress

  # SMS Subscription for Critical Alerts
  CriticalSMSSubscription:
    Type: AWS::SNS::Subscription
    Condition: HasPhoneNumber
    Properties:
      TopicArn: !Ref CriticalAlertsTopic
      Protocol: sms
      Endpoint: !Ref PhoneNumber

  # Email Subscription for Warning Alerts
  WarningEmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref WarningAlertsTopic
      Protocol: email
      Endpoint: !Ref EmailAddress

  # Email Subscription for Info Alerts
  InfoEmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref InfoAlertsTopic
      Protocol: email
      Endpoint: !Ref EmailAddress

Outputs:
  CriticalAlertsTopicArn:
    Description: ARN of Critical Alerts SNS Topic
    Value: !Ref CriticalAlertsTopic
    Export:
      Name: CriticalAlertsTopicArn

  WarningAlertsTopicArn:
    Description: ARN of Warning Alerts SNS Topic
    Value: !Ref WarningAlertsTopic
    Export:
      Name: WarningAlertsTopicArn

  InfoAlertsTopicArn:
    Description: ARN of Info Alerts SNS Topic
    Value: !Ref InfoAlertsTopic
    Export:
      Name: InfoAlertsTopicArn
```

### Creating Subscriptions via CLI

```bash
# Create topic
TOPIC_ARN=$(aws sns create-topic --name cloudwatch-alerts --query TopicArn --output text)

# Email subscription
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol email \
    --notification-endpoint alerts@example.com

# Email-JSON subscription (for technical recipients)
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol email-json \
    --notification-endpoint devops@example.com

# SMS subscription
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol sms \
    --notification-endpoint +15555551234

# HTTPS webhook subscription
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol https \
    --notification-endpoint https://api.example.com/webhooks/aws-alerts

# Lambda subscription
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol lambda \
    --notification-endpoint arn:aws:lambda:us-east-1:123456789012:function:alert-handler

# SQS subscription
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol sqs \
    --notification-endpoint arn:aws:sqs:us-east-1:123456789012:alert-queue

# List subscriptions
aws sns list-subscriptions-by-topic --topic-arn $TOPIC_ARN
```

---

## Integrating with CloudWatch Alarms

### Creating Alarms with SNS Actions

```bash
# Create alarm that sends to SNS on ALARM state
aws cloudwatch put-metric-alarm \
    --alarm-name HighCPUUtilization \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:critical-alerts \
    --ok-actions arn:aws:sns:us-east-1:123456789012:info-alerts \
    --insufficient-data-actions arn:aws:sns:us-east-1:123456789012:warning-alerts \
    --treat-missing-data missing
```

### CloudFormation with Alarms and SNS

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudWatch Alarms with SNS Notifications

Parameters:
  InstanceId:
    Type: AWS::EC2::Instance::Id
    Description: EC2 Instance ID to monitor

Resources:
  # SNS Topic
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: ec2-monitoring-alerts

  # High CPU Alarm
  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub 'HighCPU-${InstanceId}'
      AlarmDescription: CPU utilization exceeded 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      AlarmActions:
        - !Ref AlertTopic
      OKActions:
        - !Ref AlertTopic
      TreatMissingData: breaching

  # High Memory Alarm (requires CloudWatch Agent)
  HighMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub 'HighMemory-${InstanceId}'
      AlarmDescription: Memory utilization exceeded 85%
      MetricName: mem_used_percent
      Namespace: CWAgent
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 85
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      AlarmActions:
        - !Ref AlertTopic

  # Disk Space Alarm
  LowDiskSpaceAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub 'LowDiskSpace-${InstanceId}'
      AlarmDescription: Disk space below 20%
      MetricName: disk_used_percent
      Namespace: CWAgent
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
        - Name: path
          Value: /
        - Name: fstype
          Value: ext4
      AlarmActions:
        - !Ref AlertTopic

  # Status Check Alarm
  StatusCheckAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub 'StatusCheck-${InstanceId}'
      AlarmDescription: EC2 status check failed
      MetricName: StatusCheckFailed
      Namespace: AWS/EC2
      Statistic: Maximum
      Period: 60
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId
      AlarmActions:
        - !Ref AlertTopic
```

---

## SNS Message Filtering

Message filtering allows subscribers to receive only the messages they're interested in.

### Filter Policy Examples

```json
// Severity-based filtering
{
    "severity": ["CRITICAL", "HIGH"]
}

// Environment filtering
{
    "environment": ["production"]
}

// Combined filtering with prefix match
{
    "severity": ["CRITICAL"],
    "environment": [{"prefix": "prod"}],
    "service": [{"anything-but": "test-service"}]
}

// Numeric filtering
{
    "error_count": [{"numeric": [">", 100]}]
}

// Exists filtering
{
    "customer_id": [{"exists": true}]
}
```

### Setting Up Filtered Subscriptions

```bash
# Create subscription with filter policy
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-1:123456789012:alerts \
    --protocol email \
    --notification-endpoint critical-team@example.com \
    --attributes '{
        "FilterPolicy": "{\"severity\": [\"CRITICAL\"]}"
    }'

# Update existing subscription filter
aws sns set-subscription-attributes \
    --subscription-arn arn:aws:sns:us-east-1:123456789012:alerts:12345678-1234-1234-1234-123456789012 \
    --attribute-name FilterPolicy \
    --attribute-value '{"severity": ["CRITICAL", "HIGH"]}'
```

### Publishing Messages with Attributes

```bash
# Publish message with attributes for filtering
aws sns publish \
    --topic-arn arn:aws:sns:us-east-1:123456789012:alerts \
    --message "Critical database connection failure" \
    --message-attributes '{
        "severity": {
            "DataType": "String",
            "StringValue": "CRITICAL"
        },
        "environment": {
            "DataType": "String",
            "StringValue": "production"
        },
        "service": {
            "DataType": "String",
            "StringValue": "database"
        }
    }'
```

### CloudFormation with Filter Policies

```yaml
Resources:
  AlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: unified-alerts

  # Critical alerts - goes to on-call team via SMS
  CriticalSMSSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref AlertsTopic
      Protocol: sms
      Endpoint: !Ref OnCallPhoneNumber
      FilterPolicy:
        severity:
          - CRITICAL

  # Critical and high - goes to DevOps email
  DevOpsEmailSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref AlertsTopic
      Protocol: email
      Endpoint: devops@example.com
      FilterPolicy:
        severity:
          - CRITICAL
          - HIGH
        environment:
          - production

  # All alerts - goes to logging system
  LoggingSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref AlertsTopic
      Protocol: lambda
      Endpoint: !GetAtt AlertLoggerFunction.Arn
      # No filter policy = receives all messages
```

---

## Lambda Integration for Alert Processing

### Alert Handler Lambda Function

```python
# alert_handler.py
import json
import boto3
import os
from datetime import datetime

# Initialize clients
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

def lambda_handler(event, context):
    """
    Process SNS notifications from CloudWatch Alarms
    """
    for record in event['Records']:
        # Parse SNS message
        sns_message = record['Sns']
        message_id = sns_message['MessageId']
        subject = sns_message.get('Subject', 'No Subject')
        timestamp = sns_message['Timestamp']

        # Parse CloudWatch alarm message
        try:
            alarm_data = json.loads(sns_message['Message'])
        except json.JSONDecodeError:
            alarm_data = {'RawMessage': sns_message['Message']}

        # Log the alert
        print(f"Processing alert: {message_id}")
        print(f"Subject: {subject}")
        print(f"Alarm Data: {json.dumps(alarm_data, indent=2)}")

        # Extract alarm details
        alarm_name = alarm_data.get('AlarmName', 'Unknown')
        new_state = alarm_data.get('NewStateValue', 'Unknown')
        reason = alarm_data.get('NewStateReason', 'No reason provided')
        region = alarm_data.get('Region', 'Unknown')

        # Store in DynamoDB for tracking
        store_alert(message_id, alarm_name, new_state, reason, timestamp)

        # Route based on severity
        if is_critical_alarm(alarm_name, new_state):
            send_critical_notification(alarm_data)

        # Create incident if needed
        if new_state == 'ALARM':
            create_incident(alarm_data)

    return {
        'statusCode': 200,
        'body': json.dumps('Alerts processed successfully')
    }

def is_critical_alarm(alarm_name, state):
    """Check if alarm is critical based on naming convention"""
    critical_keywords = ['critical', 'prod', 'production', 'database', 'payment']
    return state == 'ALARM' and any(kw in alarm_name.lower() for kw in critical_keywords)

def store_alert(message_id, alarm_name, state, reason, timestamp):
    """Store alert in DynamoDB for tracking"""
    table_name = os.environ.get('ALERTS_TABLE', 'monitoring-alerts')
    try:
        table = dynamodb.Table(table_name)
        table.put_item(Item={
            'message_id': message_id,
            'alarm_name': alarm_name,
            'state': state,
            'reason': reason,
            'timestamp': timestamp,
            'processed_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        print(f"Error storing alert: {e}")

def send_critical_notification(alarm_data):
    """Send enhanced notification for critical alerts"""
    alarm_name = alarm_data.get('AlarmName', 'Unknown Alarm')
    reason = alarm_data.get('NewStateReason', 'No reason provided')
    region = alarm_data.get('Region', 'Unknown')

    # Send formatted email via SES
    try:
        ses.send_email(
            Source=os.environ.get('FROM_EMAIL', 'alerts@example.com'),
            Destination={
                'ToAddresses': [os.environ.get('CRITICAL_EMAIL', 'oncall@example.com')]
            },
            Message={
                'Subject': {
                    'Data': f'CRITICAL ALERT: {alarm_name}'
                },
                'Body': {
                    'Html': {
                        'Data': f'''
                        <h1 style="color: red;">Critical Alert</h1>
                        <p><strong>Alarm:</strong> {alarm_name}</p>
                        <p><strong>Region:</strong> {region}</p>
                        <p><strong>Reason:</strong> {reason}</p>
                        <p><strong>Time:</strong> {datetime.utcnow().isoformat()}</p>
                        <hr>
                        <p>Please investigate immediately.</p>
                        '''
                    }
                }
            }
        )
    except Exception as e:
        print(f"Error sending critical notification: {e}")

def create_incident(alarm_data):
    """Create incident ticket (integrate with PagerDuty, Jira, etc.)"""
    # Placeholder for incident management integration
    print(f"Creating incident for: {alarm_data.get('AlarmName')}")
    # Integration code would go here
```

### Lambda Function CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Alert Handler Lambda Function

Parameters:
  CriticalEmailAddress:
    Type: String
    Description: Email for critical alerts
  FromEmailAddress:
    Type: String
    Description: Sender email address

Resources:
  # DynamoDB table for alert tracking
  AlertsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: monitoring-alerts
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: message_id
          AttributeType: S
        - AttributeName: timestamp
          AttributeType: S
      KeySchema:
        - AttributeName: message_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: timestamp-index
          KeySchema:
            - AttributeName: timestamp
              KeyType: HASH
          Projection:
            ProjectionType: ALL
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # Lambda execution role
  AlertHandlerRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: alert-handler-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: AlertHandlerPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                  - dynamodb:GetItem
                  - dynamodb:Query
                Resource:
                  - !GetAtt AlertsTable.Arn
                  - !Sub '${AlertsTable.Arn}/index/*'
              - Effect: Allow
                Action:
                  - ses:SendEmail
                Resource: '*'

  # Alert handler Lambda function
  AlertHandlerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: alert-handler
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt AlertHandlerRole.Arn
      Timeout: 60
      MemorySize: 256
      Environment:
        Variables:
          ALERTS_TABLE: !Ref AlertsTable
          CRITICAL_EMAIL: !Ref CriticalEmailAddress
          FROM_EMAIL: !Ref FromEmailAddress
      Code:
        ZipFile: |
          import json
          import boto3
          import os
          from datetime import datetime

          dynamodb = boto3.resource('dynamodb')

          def lambda_handler(event, context):
              for record in event['Records']:
                  sns_message = record['Sns']
                  message_id = sns_message['MessageId']
                  subject = sns_message.get('Subject', 'No Subject')

                  try:
                      alarm_data = json.loads(sns_message['Message'])
                  except:
                      alarm_data = {'RawMessage': sns_message['Message']}

                  print(f"Processing: {message_id}")
                  print(f"Alarm: {json.dumps(alarm_data, indent=2)}")

                  # Store alert
                  table = dynamodb.Table(os.environ['ALERTS_TABLE'])
                  table.put_item(Item={
                      'message_id': message_id,
                      'alarm_name': alarm_data.get('AlarmName', 'Unknown'),
                      'state': alarm_data.get('NewStateValue', 'Unknown'),
                      'timestamp': sns_message['Timestamp'],
                      'processed_at': datetime.utcnow().isoformat()
                  })

              return {'statusCode': 200}

  # SNS permission for Lambda
  AlertHandlerPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref AlertHandlerFunction
      Action: lambda:InvokeFunction
      Principal: sns.amazonaws.com
      SourceArn: !Ref AlertsTopic

  # SNS Topic
  AlertsTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: monitoring-alerts

  # Lambda subscription
  LambdaSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref AlertsTopic
      Protocol: lambda
      Endpoint: !GetAtt AlertHandlerFunction.Arn

Outputs:
  TopicArn:
    Value: !Ref AlertsTopic
  FunctionArn:
    Value: !GetAtt AlertHandlerFunction.Arn
```

---

## Slack and PagerDuty Integration

### Slack Integration via Lambda

```python
# slack_notifier.py
import json
import urllib3
import os

http = urllib3.PoolManager()

def lambda_handler(event, context):
    """
    Send CloudWatch alarm notifications to Slack
    """
    webhook_url = os.environ['SLACK_WEBHOOK_URL']

    for record in event['Records']:
        sns_message = record['Sns']

        try:
            alarm_data = json.loads(sns_message['Message'])
        except json.JSONDecodeError:
            alarm_data = {'Message': sns_message['Message']}

        # Build Slack message
        slack_message = format_slack_message(alarm_data)

        # Send to Slack
        response = http.request(
            'POST',
            webhook_url,
            body=json.dumps(slack_message),
            headers={'Content-Type': 'application/json'}
        )

        print(f"Slack response: {response.status}")

    return {'statusCode': 200}

def format_slack_message(alarm_data):
    """Format CloudWatch alarm as Slack message"""
    alarm_name = alarm_data.get('AlarmName', 'Unknown Alarm')
    state = alarm_data.get('NewStateValue', 'Unknown')
    reason = alarm_data.get('NewStateReason', 'No reason provided')
    region = alarm_data.get('Region', 'Unknown')

    # Color based on state
    color_map = {
        'ALARM': '#FF0000',      # Red
        'OK': '#00FF00',         # Green
        'INSUFFICIENT_DATA': '#FFA500'  # Orange
    }
    color = color_map.get(state, '#808080')

    # Emoji based on state
    emoji_map = {
        'ALARM': ':rotating_light:',
        'OK': ':white_check_mark:',
        'INSUFFICIENT_DATA': ':warning:'
    }
    emoji = emoji_map.get(state, ':question:')

    return {
        'attachments': [
            {
                'color': color,
                'title': f'{emoji} CloudWatch Alarm: {alarm_name}',
                'fields': [
                    {
                        'title': 'State',
                        'value': state,
                        'short': True
                    },
                    {
                        'title': 'Region',
                        'value': region,
                        'short': True
                    },
                    {
                        'title': 'Reason',
                        'value': reason,
                        'short': False
                    }
                ],
                'footer': 'AWS CloudWatch',
                'ts': int(datetime.now().timestamp())
            }
        ]
    }
```

### PagerDuty Integration

```python
# pagerduty_notifier.py
import json
import urllib3
import os
from datetime import datetime

http = urllib3.PoolManager()

PAGERDUTY_EVENTS_API = 'https://events.pagerduty.com/v2/enqueue'

def lambda_handler(event, context):
    """
    Send CloudWatch alarm notifications to PagerDuty
    """
    routing_key = os.environ['PAGERDUTY_ROUTING_KEY']

    for record in event['Records']:
        sns_message = record['Sns']

        try:
            alarm_data = json.loads(sns_message['Message'])
        except json.JSONDecodeError:
            print(f"Failed to parse message: {sns_message['Message']}")
            continue

        # Build PagerDuty event
        pd_event = create_pagerduty_event(alarm_data, routing_key)

        # Send to PagerDuty
        response = http.request(
            'POST',
            PAGERDUTY_EVENTS_API,
            body=json.dumps(pd_event),
            headers={'Content-Type': 'application/json'}
        )

        print(f"PagerDuty response: {response.status} - {response.data.decode()}")

    return {'statusCode': 200}

def create_pagerduty_event(alarm_data, routing_key):
    """Create PagerDuty event from CloudWatch alarm"""
    alarm_name = alarm_data.get('AlarmName', 'Unknown Alarm')
    state = alarm_data.get('NewStateValue', 'Unknown')
    reason = alarm_data.get('NewStateReason', 'No reason provided')
    region = alarm_data.get('Region', 'Unknown')

    # Map CloudWatch state to PagerDuty event action
    action_map = {
        'ALARM': 'trigger',
        'OK': 'resolve',
        'INSUFFICIENT_DATA': 'trigger'
    }
    event_action = action_map.get(state, 'trigger')

    # Map to PagerDuty severity
    severity_map = {
        'ALARM': 'critical',
        'OK': 'info',
        'INSUFFICIENT_DATA': 'warning'
    }
    severity = severity_map.get(state, 'error')

    return {
        'routing_key': routing_key,
        'event_action': event_action,
        'dedup_key': f'cloudwatch-{alarm_name}',
        'payload': {
            'summary': f'CloudWatch: {alarm_name} is {state}',
            'source': f'AWS CloudWatch - {region}',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'custom_details': {
                'alarm_name': alarm_name,
                'state': state,
                'reason': reason,
                'region': region
            }
        },
        'links': [
            {
                'href': f'https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{alarm_name}',
                'text': 'View in CloudWatch'
            }
        ]
    }
```

---

## Best Practices

### Topic Organization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SNS Topic Organization Strategy                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Option 1: By Severity                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ critical-alerts  │  │ warning-alerts   │  │  info-alerts     │          │
│  │                  │  │                  │  │                  │          │
│  │ • SMS            │  │ • Email          │  │ • Email          │          │
│  │ • PagerDuty      │  │ • Slack          │  │ • Log archiver   │          │
│  │ • Email          │  │                  │  │                  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│  Option 2: By Service/Team                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │ frontend-alerts  │  │ backend-alerts   │  │  database-alerts │          │
│  │                  │  │                  │  │                  │          │
│  │ Frontend team    │  │ Backend team     │  │ DBA team         │          │
│  │ subscribers      │  │ subscribers      │  │ subscribers      │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│  Option 3: Combined with Message Filtering                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        unified-alerts                                    ││
│  │                                                                          ││
│  │  Subscribers with filter policies:                                       ││
│  │  • Critical team: {severity: [CRITICAL]}                                ││
│  │  • DevOps: {severity: [CRITICAL, HIGH], env: [production]}             ││
│  │  • Dev team: {env: [development]}                                       ││
│  │  • All alerts: (no filter)                                              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Security

1. **Use encryption**: Enable SSE-KMS for sensitive topics
2. **Restrict publishing**: Use IAM policies to control who can publish
3. **Verify endpoints**: Confirm HTTPS endpoints belong to you
4. **Use VPC endpoints**: For Lambda/SQS in VPCs

### Cost Optimization

1. **Consolidate topics**: Use message filtering instead of multiple topics
2. **Avoid SMS for non-critical**: SMS is expensive, use sparingly
3. **Set delivery retry policies**: Reduce retries for non-critical endpoints

---

## Hands-On: Setting Up Alert Pipeline

### Step 1: Create SNS Topics

```bash
# Create topics for different severity levels
aws sns create-topic --name critical-alerts
aws sns create-topic --name warning-alerts
aws sns create-topic --name info-alerts

# Get topic ARNs
CRITICAL_ARN=$(aws sns list-topics --query "Topics[?contains(TopicArn, 'critical-alerts')].TopicArn" --output text)
WARNING_ARN=$(aws sns list-topics --query "Topics[?contains(TopicArn, 'warning-alerts')].TopicArn" --output text)
```

### Step 2: Create Subscriptions

```bash
# Email subscription
aws sns subscribe \
    --topic-arn $CRITICAL_ARN \
    --protocol email \
    --notification-endpoint your-email@example.com

# Check your email and confirm subscription!
```

### Step 3: Create CloudWatch Alarm with SNS

```bash
# Create test alarm (using a Lambda that likely exists)
aws cloudwatch put-metric-alarm \
    --alarm-name TestAlarm \
    --alarm-description "Test alarm for SNS integration" \
    --metric-name Invocations \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions $CRITICAL_ARN

# Trigger alarm (if you have a Lambda function)
# aws lambda invoke --function-name your-function /dev/null
```

### Step 4: Test the Pipeline

```bash
# Manually publish test message
aws sns publish \
    --topic-arn $CRITICAL_ARN \
    --subject "Test Alert" \
    --message "This is a test alert from the monitoring module."
```

### Step 5: Cleanup

```bash
# Delete alarms
aws cloudwatch delete-alarms --alarm-names TestAlarm

# Delete subscriptions (get ARNs first)
aws sns list-subscriptions-by-topic --topic-arn $CRITICAL_ARN

# Delete topics
aws sns delete-topic --topic-arn $CRITICAL_ARN
aws sns delete-topic --topic-arn $WARNING_ARN
```

---

## Pricing

| Component | Cost |
|-----------|------|
| Publishes | First 1M free, then $0.50 per 1M |
| HTTP/S deliveries | First 100K free, then $0.60 per 1M |
| Email deliveries | First 1K free, then $2.00 per 100K |
| SMS deliveries | Varies by country ($0.00645 - $0.0908/message) |
| Lambda/SQS deliveries | Free (pay for Lambda/SQS execution) |
| Data transfer | Standard AWS data transfer rates |

---

## Next Steps

Continue to the next section:
- [12-hands-on-lab.md](12-hands-on-lab.md) - Complete monitoring hands-on lab
