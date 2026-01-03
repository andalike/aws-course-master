# Amazon EventBridge

## Introduction

Amazon EventBridge is a serverless event bus service that makes it easy to connect applications using data from your own applications, integrated SaaS applications, and AWS services. It enables event-driven architectures by routing events to targets like Lambda, Step Functions, SQS, and more.

## EventBridge Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENTBRIDGE ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Event Sources                Event Bus                Targets   │
│                                                                  │
│  ┌──────────┐              ┌────────────┐         ┌──────────┐ │
│  │   AWS    │──────────────▶│            │────────▶│  Lambda  │ │
│  │ Services │              │            │         └──────────┘ │
│  └──────────┘              │            │         ┌──────────┐ │
│  ┌──────────┐              │   Event    │────────▶│   Step   │ │
│  │   SaaS   │──────────────▶│    Bus    │         │Functions │ │
│  │   Apps   │              │            │         └──────────┘ │
│  └──────────┘              │  ┌──────┐  │         ┌──────────┐ │
│  ┌──────────┐              │  │Rules │  │────────▶│   SQS    │ │
│  │  Custom  │──────────────▶│  └──────┘  │         └──────────┘ │
│  │   Apps   │              │            │         ┌──────────┐ │
│  └──────────┘              │            │────────▶│   SNS    │ │
│                            └────────────┘         └──────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Description |
|-----------|-------------|
| **Event Bus** | Pipeline that receives events |
| **Events** | JSON objects describing state changes |
| **Rules** | Match incoming events and route to targets |
| **Targets** | AWS services that process events |
| **Scheduler** | Invoke targets on a schedule |
| **Pipes** | Point-to-point integrations |
| **Schema Registry** | Store and manage event schemas |

## Event Buses

### Types of Event Buses

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT BUS TYPES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  DEFAULT EVENT BUS                                           ││
│  │  • Automatically created in each region                      ││
│  │  • Receives events from AWS services                         ││
│  │  • Free to use (pay for custom events only)                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  CUSTOM EVENT BUS                                            ││
│  │  • Created for your applications                             ││
│  │  • Isolation between applications/environments               ││
│  │  • Can be shared across accounts                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  PARTNER EVENT BUS                                           ││
│  │  • Receives events from SaaS partners                        ││
│  │  • Zendesk, Datadog, Auth0, etc.                            ││
│  │  • Must be linked to partner source                          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Creating Custom Event Bus

```bash
# Create custom event bus
aws events create-event-bus \
    --name my-application-bus

# Create with resource policy
aws events create-event-bus \
    --name shared-bus \
    --event-bus-policy '{
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AllowCrossAccountPut",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "events:PutEvents",
            "Resource": "arn:aws:events:us-east-1:987654321098:event-bus/shared-bus"
        }]
    }'

# List event buses
aws events list-event-buses

# Delete event bus
aws events delete-event-bus --name my-application-bus
```

## Events

### Event Structure

```json
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "detail-type": "Order Placed",
  "source": "com.mycompany.orders",
  "account": "123456789012",
  "time": "2024-01-15T12:00:00Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:dynamodb:us-east-1:123456789012:table/orders"
  ],
  "detail": {
    "orderId": "ORD-001",
    "customerId": "CUST-123",
    "items": [
      {"productId": "PROD-1", "quantity": 2, "price": 29.99},
      {"productId": "PROD-2", "quantity": 1, "price": 49.99}
    ],
    "total": 109.97,
    "status": "pending"
  }
}
```

### Sending Events

```python
# Python - Send custom events
import boto3
import json
from datetime import datetime

eventbridge = boto3.client('events')

def send_order_event(order):
    """Send order placed event to EventBridge"""
    response = eventbridge.put_events(
        Entries=[
            {
                'Source': 'com.mycompany.orders',
                'DetailType': 'Order Placed',
                'Detail': json.dumps({
                    'orderId': order['id'],
                    'customerId': order['customer_id'],
                    'items': order['items'],
                    'total': order['total'],
                    'status': 'pending',
                    'timestamp': datetime.utcnow().isoformat()
                }),
                'EventBusName': 'orders-bus'  # Or 'default'
            }
        ]
    )

    # Check for failures
    if response['FailedEntryCount'] > 0:
        for entry in response['Entries']:
            if 'ErrorCode' in entry:
                print(f"Error: {entry['ErrorCode']} - {entry['ErrorMessage']}")

    return response


# Send multiple events (batch)
def send_batch_events(events):
    """Send up to 10 events in a batch"""
    entries = []
    for event in events:
        entries.append({
            'Source': event['source'],
            'DetailType': event['detail_type'],
            'Detail': json.dumps(event['detail']),
            'EventBusName': 'orders-bus'
        })

    # EventBridge allows max 10 events per PutEvents call
    response = eventbridge.put_events(Entries=entries)
    return response
```

```javascript
// Node.js - Send custom events
const { EventBridgeClient, PutEventsCommand } = require('@aws-sdk/client-eventbridge');

const client = new EventBridgeClient({ region: 'us-east-1' });

async function sendOrderEvent(order) {
    const command = new PutEventsCommand({
        Entries: [
            {
                Source: 'com.mycompany.orders',
                DetailType: 'Order Placed',
                Detail: JSON.stringify({
                    orderId: order.id,
                    customerId: order.customerId,
                    items: order.items,
                    total: order.total,
                    status: 'pending',
                    timestamp: new Date().toISOString()
                }),
                EventBusName: 'orders-bus'
            }
        ]
    });

    const response = await client.send(command);
    return response;
}
```

### CLI - Send Events

```bash
# Send single event
aws events put-events --entries '[
    {
        "Source": "com.mycompany.orders",
        "DetailType": "Order Placed",
        "Detail": "{\"orderId\": \"ORD-001\", \"total\": 99.99}",
        "EventBusName": "default"
    }
]'

# Send from file
aws events put-events --entries file://events.json
```

## Event Rules

### Creating Rules

```bash
# Create rule with event pattern
aws events put-rule \
    --name order-processing-rule \
    --event-bus-name orders-bus \
    --event-pattern '{
        "source": ["com.mycompany.orders"],
        "detail-type": ["Order Placed"]
    }' \
    --state ENABLED \
    --description "Route order events to processing"

# Create scheduled rule
aws events put-rule \
    --name daily-report-rule \
    --schedule-expression "cron(0 9 * * ? *)" \
    --state ENABLED \
    --description "Generate daily report at 9 AM UTC"

# Add target to rule
aws events put-targets \
    --rule order-processing-rule \
    --event-bus-name orders-bus \
    --targets '[
        {
            "Id": "process-order-lambda",
            "Arn": "arn:aws:lambda:us-east-1:123456789012:function:process-order"
        }
    ]'
```

### Event Patterns

#### Simple Pattern Matching

```json
// Match all EC2 instance state changes
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"]
}
```

#### Match Specific Values

```json
// Match only stopped instances
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped", "terminated"]
  }
}
```

#### Prefix Matching

```json
// Match sources starting with "com.mycompany"
{
  "source": [{"prefix": "com.mycompany"}]
}
```

#### Numeric Matching

```json
// Match orders over $100
{
  "source": ["com.mycompany.orders"],
  "detail": {
    "total": [{"numeric": [">", 100]}]
  }
}

// Match range
{
  "detail": {
    "quantity": [{"numeric": [">=", 1, "<=", 100]}]
  }
}
```

#### Exists Pattern

```json
// Match events where priority exists
{
  "detail": {
    "priority": [{"exists": true}]
  }
}

// Match events where discount does NOT exist
{
  "detail": {
    "discount": [{"exists": false}]
  }
}
```

#### Anything-But Pattern

```json
// Match any status except "completed"
{
  "detail": {
    "status": [{"anything-but": ["completed"]}]
  }
}
```

#### Complex Pattern

```json
{
  "source": ["com.mycompany.orders"],
  "detail-type": ["Order Placed"],
  "detail": {
    "total": [{"numeric": [">=", 100]}],
    "status": ["pending", "processing"],
    "customer": {
      "type": ["premium", "enterprise"]
    },
    "priority": [{"exists": true}],
    "country": [{"anything-but": ["blocked-country"]}]
  }
}
```

### SAM Template - Rules and Targets

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  # Custom Event Bus
  OrdersBus:
    Type: AWS::Events::EventBus
    Properties:
      Name: orders-bus

  # Rule for high-value orders
  HighValueOrderRule:
    Type: AWS::Events::Rule
    Properties:
      Name: high-value-orders
      EventBusName: !Ref OrdersBus
      EventPattern:
        source:
          - com.mycompany.orders
        detail-type:
          - Order Placed
        detail:
          total:
            - numeric:
                - '>='
                - 1000
      State: ENABLED
      Targets:
        - Id: ProcessHighValueOrder
          Arn: !GetAtt ProcessHighValueOrderFunction.Arn
        - Id: NotifyManager
          Arn: !Ref HighValueOrderTopic

  # Lambda permission for EventBridge
  ProcessHighValueOrderPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ProcessHighValueOrderFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt HighValueOrderRule.Arn

  # Lambda function
  ProcessHighValueOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: high_value.handler
      Runtime: python3.12
      CodeUri: src/

  # SNS Topic
  HighValueOrderTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: high-value-orders

  # SNS Topic Policy for EventBridge
  HighValueOrderTopicPolicy:
    Type: AWS::SNS::TopicPolicy
    Properties:
      Topics:
        - !Ref HighValueOrderTopic
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sns:Publish
            Resource: !Ref HighValueOrderTopic
```

## EventBridge Scheduler

### Creating Schedules

```bash
# Create one-time schedule
aws scheduler create-schedule \
    --name process-report \
    --schedule-expression "at(2024-12-31T23:59:00)" \
    --schedule-expression-timezone "America/New_York" \
    --flexible-time-window '{"Mode": "OFF"}' \
    --target '{
        "Arn": "arn:aws:lambda:us-east-1:123456789012:function:generate-report",
        "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role"
    }'

# Create recurring schedule
aws scheduler create-schedule \
    --name daily-cleanup \
    --schedule-expression "rate(1 day)" \
    --flexible-time-window '{"Mode": "FLEXIBLE", "MaximumWindowInMinutes": 15}' \
    --target '{
        "Arn": "arn:aws:lambda:us-east-1:123456789012:function:cleanup",
        "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role"
    }'

# Create cron schedule
aws scheduler create-schedule \
    --name weekly-report \
    --schedule-expression "cron(0 9 ? * MON *)" \
    --schedule-expression-timezone "UTC" \
    --flexible-time-window '{"Mode": "OFF"}' \
    --target '{
        "Arn": "arn:aws:lambda:us-east-1:123456789012:function:weekly-report",
        "RoleArn": "arn:aws:iam::123456789012:role/scheduler-role",
        "Input": "{\"reportType\": \"weekly\"}"
    }'
```

### Schedule Expressions

| Type | Expression | Description |
|------|------------|-------------|
| Rate | `rate(1 hour)` | Every hour |
| Rate | `rate(5 minutes)` | Every 5 minutes |
| Rate | `rate(1 day)` | Once per day |
| Cron | `cron(0 9 * * ? *)` | Daily at 9 AM UTC |
| Cron | `cron(0 12 ? * MON-FRI *)` | Weekdays at noon |
| Cron | `cron(0/15 * * * ? *)` | Every 15 minutes |
| One-time | `at(2024-12-31T23:59:00)` | Specific date/time |

### Cron Expression Format

```
cron(minutes hours day-of-month month day-of-week year)

Fields:
- Minutes: 0-59
- Hours: 0-23
- Day-of-month: 1-31 or ?
- Month: 1-12 or JAN-DEC
- Day-of-week: 1-7 or SUN-SAT or ?
- Year: 1970-2199 or *

Examples:
- cron(0 9 * * ? *)           Every day at 9:00 AM
- cron(0 18 ? * MON-FRI *)    Weekdays at 6:00 PM
- cron(0/10 * * * ? *)        Every 10 minutes
- cron(0 0 1 * ? *)           First day of month at midnight
- cron(0 8 ? * 2#1 *)         First Monday of month at 8 AM
```

### SAM Template - Scheduler

```yaml
Resources:
  # Scheduler Schedule
  DailyReportSchedule:
    Type: AWS::Scheduler::Schedule
    Properties:
      Name: daily-report
      Description: Generate daily report at 9 AM
      ScheduleExpression: cron(0 9 * * ? *)
      ScheduleExpressionTimezone: America/New_York
      FlexibleTimeWindow:
        Mode: FLEXIBLE
        MaximumWindowInMinutes: 15
      Target:
        Arn: !GetAtt ReportFunction.Arn
        RoleArn: !GetAtt SchedulerRole.Arn
        Input: '{"reportType": "daily"}'
        RetryPolicy:
          MaximumEventAgeInSeconds: 3600
          MaximumRetryAttempts: 3

  # Scheduler Role
  SchedulerRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: scheduler.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: InvokeLambda
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: lambda:InvokeFunction
                Resource: !GetAtt ReportFunction.Arn

  ReportFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: report.handler
      Runtime: python3.12
      CodeUri: src/
```

## Event Targets

### Available Targets

| Target | Use Case |
|--------|----------|
| Lambda | Function invocation |
| Step Functions | Start workflow |
| SQS | Queue message |
| SNS | Publish notification |
| Kinesis | Stream data |
| API Gateway | HTTP endpoint |
| ECS Task | Run container |
| CodePipeline | Start pipeline |
| CodeBuild | Start build |
| EventBridge Bus | Cross-account/region |

### Input Transformation

```bash
# Transform input before sending to target
aws events put-targets \
    --rule order-rule \
    --targets '[
        {
            "Id": "transform-example",
            "Arn": "arn:aws:lambda:us-east-1:123456789012:function:process",
            "InputTransformer": {
                "InputPathsMap": {
                    "orderId": "$.detail.orderId",
                    "customer": "$.detail.customerId",
                    "total": "$.detail.total"
                },
                "InputTemplate": "{\"order\": \"<orderId>\", \"customer\": \"<customer>\", \"amount\": <total>}"
            }
        }
    ]'
```

### Multiple Targets

```yaml
Resources:
  OrderProcessingRule:
    Type: AWS::Events::Rule
    Properties:
      EventBusName: !Ref OrdersBus
      EventPattern:
        source:
          - com.mycompany.orders
        detail-type:
          - Order Placed
      Targets:
        # Target 1: Lambda for processing
        - Id: ProcessOrder
          Arn: !GetAtt ProcessOrderFunction.Arn

        # Target 2: SQS for async processing
        - Id: QueueOrder
          Arn: !GetAtt OrdersQueue.Arn

        # Target 3: Step Functions for workflow
        - Id: StartOrderWorkflow
          Arn: !Ref OrderWorkflow
          RoleArn: !GetAtt EventBridgeRole.Arn

        # Target 4: SNS for notifications
        - Id: NotifyOrder
          Arn: !Ref OrderNotificationTopic

        # Target 5: API Gateway for webhook
        - Id: WebhookTarget
          Arn: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${WebhookApi}/prod/POST/orders"
          HttpParameters:
            HeaderParameters:
              Content-Type: application/json
```

## Hands-On Examples

### Example 1: Order Processing System

```
┌─────────────────────────────────────────────────────────────────┐
│              ORDER PROCESSING EVENT FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐     ┌────────────┐     ┌────────────────────────┐│
│  │  Order   │────▶│ EventBridge │────▶│ Rules                  ││
│  │  Service │     │    Bus      │     │                        ││
│  └──────────┘     └────────────┘     │ 1. All Orders          ││
│                                       │    └▶ Lambda (Log)     ││
│                                       │                        ││
│                                       │ 2. High Value ($1000+) ││
│                                       │    └▶ SNS (Alert)      ││
│                                       │    └▶ Step Functions   ││
│                                       │                        ││
│                                       │ 3. Priority Orders     ││
│                                       │    └▶ SQS (Fast Lane)  ││
│                                       └────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

```yaml
# template.yaml - Order Processing System
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  # Event Bus
  OrdersEventBus:
    Type: AWS::Events::EventBus
    Properties:
      Name: orders-event-bus

  # Rule 1: Log all orders
  LogAllOrdersRule:
    Type: AWS::Events::Rule
    Properties:
      Name: log-all-orders
      EventBusName: !Ref OrdersEventBus
      EventPattern:
        source:
          - com.mycompany.orders
        detail-type:
          - Order Placed
          - Order Updated
          - Order Cancelled
      Targets:
        - Id: LogOrders
          Arn: !GetAtt OrderLogFunction.Arn

  # Rule 2: High value orders
  HighValueOrderRule:
    Type: AWS::Events::Rule
    Properties:
      Name: high-value-orders
      EventBusName: !Ref OrdersEventBus
      EventPattern:
        source:
          - com.mycompany.orders
        detail-type:
          - Order Placed
        detail:
          total:
            - numeric:
                - '>='
                - 1000
      Targets:
        - Id: AlertManager
          Arn: !Ref HighValueAlertTopic
        - Id: StartApprovalWorkflow
          Arn: !Ref OrderApprovalWorkflow
          RoleArn: !GetAtt EventBridgeRole.Arn

  # Rule 3: Priority orders
  PriorityOrderRule:
    Type: AWS::Events::Rule
    Properties:
      Name: priority-orders
      EventBusName: !Ref OrdersEventBus
      EventPattern:
        source:
          - com.mycompany.orders
        detail-type:
          - Order Placed
        detail:
          priority:
            - express
            - same-day
      Targets:
        - Id: FastLaneQueue
          Arn: !GetAtt PriorityOrderQueue.Arn

  # Lambda Functions
  OrderLogFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: log_orders.handler
      Runtime: python3.12
      CodeUri: src/
      Environment:
        Variables:
          LOG_TABLE: !Ref OrderLogsTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrderLogsTable

  OrderLogFunctionPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref OrderLogFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt LogAllOrdersRule.Arn

  # Send orders function
  SendOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: send_order.handler
      Runtime: python3.12
      CodeUri: src/
      Environment:
        Variables:
          EVENT_BUS_NAME: !Ref OrdersEventBus
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action: events:PutEvents
              Resource: !GetAtt OrdersEventBus.Arn
      Events:
        CreateOrder:
          Type: Api
          Properties:
            Path: /orders
            Method: POST

  # DynamoDB Table
  OrderLogsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: order-logs
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
        - AttributeName: timestamp
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH
        - AttributeName: timestamp
          KeyType: RANGE

  # SQS Queue
  PriorityOrderQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: priority-orders

  PriorityOrderQueuePolicy:
    Type: AWS::SQS::QueuePolicy
    Properties:
      Queues:
        - !Ref PriorityOrderQueue
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sqs:SendMessage
            Resource: !GetAtt PriorityOrderQueue.Arn

  # SNS Topic
  HighValueAlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: high-value-orders-alert

  HighValueAlertTopicPolicy:
    Type: AWS::SNS::TopicPolicy
    Properties:
      Topics:
        - !Ref HighValueAlertTopic
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sns:Publish
            Resource: !Ref HighValueAlertTopic

  # Step Functions
  OrderApprovalWorkflow:
    Type: AWS::Serverless::StateMachine
    Properties:
      Type: STANDARD
      DefinitionUri: statemachine/approval.asl.json
      Policies:
        - LambdaInvokePolicy:
            FunctionName: !Ref ApprovalFunction

  # EventBridge Role
  EventBridgeRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: StartStepFunctions
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: states:StartExecution
                Resource: !Ref OrderApprovalWorkflow
```

### Example 2: Cross-Account Event Routing

```yaml
# Source Account - Send events to another account
Resources:
  CrossAccountRule:
    Type: AWS::Events::Rule
    Properties:
      EventPattern:
        source:
          - com.mycompany.app
      Targets:
        - Id: TargetAccount
          Arn: !Sub "arn:aws:events:${AWS::Region}:TARGET_ACCOUNT_ID:event-bus/shared-bus"
          RoleArn: !GetAtt CrossAccountRole.Arn

  CrossAccountRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: PutEventsPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: events:PutEvents
                Resource: !Sub "arn:aws:events:${AWS::Region}:TARGET_ACCOUNT_ID:event-bus/shared-bus"
```

```yaml
# Target Account - Receive events from another account
Resources:
  SharedEventBus:
    Type: AWS::Events::EventBus
    Properties:
      Name: shared-bus

  SharedEventBusPolicy:
    Type: AWS::Events::EventBusPolicy
    Properties:
      EventBusName: !Ref SharedEventBus
      StatementId: AllowSourceAccount
      Statement:
        Effect: Allow
        Principal:
          AWS: !Sub "arn:aws:iam::SOURCE_ACCOUNT_ID:root"
        Action: events:PutEvents
        Resource: !GetAtt SharedEventBus.Arn
```

### Example 3: Scheduled Data Pipeline

```python
# src/daily_pipeline.py
import boto3
import json
from datetime import datetime, timedelta

eventbridge = boto3.client('events')
s3 = boto3.client('s3')

def handler(event, context):
    """Scheduled data pipeline triggered by EventBridge"""

    # Get date from event or use yesterday
    report_date = event.get('date', (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))

    print(f"Processing data for date: {report_date}")

    # Step 1: Extract data
    raw_data = extract_data(report_date)

    # Step 2: Transform data
    processed_data = transform_data(raw_data)

    # Step 3: Load to S3
    output_key = f"reports/{report_date}/summary.json"
    s3.put_object(
        Bucket='data-pipeline-output',
        Key=output_key,
        Body=json.dumps(processed_data)
    )

    # Step 4: Publish completion event
    eventbridge.put_events(
        Entries=[{
            'Source': 'com.mycompany.pipeline',
            'DetailType': 'Pipeline Completed',
            'Detail': json.dumps({
                'date': report_date,
                'outputLocation': f"s3://data-pipeline-output/{output_key}",
                'recordCount': len(processed_data.get('records', [])),
                'status': 'success'
            }),
            'EventBusName': 'default'
        }]
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'date': report_date,
            'status': 'completed'
        })
    }


def extract_data(date):
    # Extract logic
    return {'date': date, 'records': []}


def transform_data(data):
    # Transform logic
    return data
```

```yaml
# Schedule configuration
Resources:
  DailyPipelineSchedule:
    Type: AWS::Scheduler::Schedule
    Properties:
      Name: daily-data-pipeline
      ScheduleExpression: cron(0 2 * * ? *)  # 2 AM daily
      ScheduleExpressionTimezone: UTC
      FlexibleTimeWindow:
        Mode: OFF
      Target:
        Arn: !GetAtt PipelineFunction.Arn
        RoleArn: !GetAtt SchedulerRole.Arn
        Input: '{"type": "scheduled"}'
```

## Best Practices

### 1. Event Design

```json
// Good: Descriptive detail-type and structured detail
{
  "source": "com.mycompany.orders",
  "detail-type": "Order Placed",
  "detail": {
    "orderId": "ORD-001",
    "version": "1.0",
    "metadata": {
      "correlationId": "abc-123",
      "timestamp": "2024-01-15T12:00:00Z"
    },
    "data": {
      "customerId": "CUST-001",
      "items": [],
      "total": 99.99
    }
  }
}

// Avoid: Generic detail-type, unstructured detail
{
  "source": "app",
  "detail-type": "event",
  "detail": {
    "message": "Order ORD-001 placed for $99.99"
  }
}
```

### 2. Use Schema Registry

```bash
# Create schema
aws schemas create-schema \
    --registry-name my-registry \
    --schema-name com.mycompany.orders.OrderPlaced \
    --type OpenApi3 \
    --content file://schema.json

# Discover schemas from events
aws schemas create-discoverer \
    --source-arn arn:aws:events:us-east-1:123456789012:event-bus/orders-bus
```

### 3. Dead Letter Queues

```yaml
Resources:
  OrderRule:
    Type: AWS::Events::Rule
    Properties:
      EventPattern:
        source:
          - com.mycompany.orders
      Targets:
        - Id: ProcessOrder
          Arn: !GetAtt ProcessOrderFunction.Arn
          DeadLetterConfig:
            Arn: !GetAtt RuleDLQ.Arn
          RetryPolicy:
            MaximumEventAgeInSeconds: 3600
            MaximumRetryAttempts: 3

  RuleDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: eventbridge-dlq
```

### 4. Monitoring

```yaml
# CloudWatch Alarms for EventBridge
Resources:
  FailedInvocationsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: EventBridge-FailedInvocations
      MetricName: FailedInvocations
      Namespace: AWS/Events
      Dimensions:
        - Name: RuleName
          Value: !Ref OrderRule
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 1
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref AlertTopic
```

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| Event Bus | Pipeline receiving events |
| Events | JSON state change notifications |
| Rules | Pattern matching and routing |
| Targets | Destinations for matched events |
| Scheduler | Time-based invocations |

### Common Patterns

1. **Fan-out**: One event triggers multiple targets
2. **Event routing**: Different events to different targets
3. **Cross-account**: Share events between accounts
4. **Scheduling**: Time-based triggers
5. **Dead letter**: Handle failed deliveries

### Next Steps

Continue to [12-hands-on-lab.md](./12-hands-on-lab.md) to build a complete serverless application using all the concepts learned in this module.
