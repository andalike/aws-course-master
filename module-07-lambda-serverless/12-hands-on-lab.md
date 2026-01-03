# Hands-On Lab: Complete Serverless Application

## Lab Overview

In this comprehensive lab, you will build a complete serverless e-commerce order processing system using AWS Lambda, API Gateway, DynamoDB, Step Functions, S3, EventBridge, and SAM.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SERVERLESS ORDER PROCESSING SYSTEM                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐     ┌───────────┐     ┌─────────────────────────────────┐ │
│  │ Client  │────▶│    API    │────▶│         Lambda Functions        │ │
│  │  (Web)  │     │  Gateway  │     │  ┌─────────┐  ┌─────────────┐  │ │
│  └─────────┘     └───────────┘     │  │ Create  │  │    Get      │  │ │
│                                     │  │  Order  │  │   Orders    │  │ │
│                                     │  └────┬────┘  └─────────────┘  │ │
│                                     └───────┼────────────────────────┘ │
│                                             │                           │
│                                             ▼                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        EventBridge                               │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │   │
│  │  │ Order Rule  │   │ Payment Rule│   │Shipping Rule│           │   │
│  │  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │   │
│  └─────────┼─────────────────┼─────────────────┼───────────────────┘   │
│            │                 │                 │                        │
│            ▼                 ▼                 ▼                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Step Functions                              │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐         │   │
│  │  │Validate │──▶│ Payment │──▶│ Fulfill │──▶│ Notify  │         │   │
│  │  │  Order  │   │ Process │   │  Order  │   │Customer │         │   │
│  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│            │                                                            │
│            ▼                                                            │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐  │
│  │    DynamoDB     │     │       S3        │     │       SNS       │  │
│  │    (Orders)     │     │   (Receipts)    │     │ (Notifications) │  │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS CLI installed and configured
- SAM CLI installed
- Docker installed (for local testing)
- Python 3.12 or Node.js 20.x
- Basic understanding of Lambda, API Gateway, DynamoDB

## Lab Duration

**Estimated Time**: 2-3 hours

---

## Part 1: Project Setup

### Step 1.1: Create Project Structure

```bash
# Create project directory
mkdir serverless-order-system
cd serverless-order-system

# Create directory structure
mkdir -p src/{orders,payments,notifications,shared}
mkdir -p statemachine
mkdir -p events
mkdir -p tests

# Create files
touch template.yaml
touch samconfig.toml
touch README.md
```

### Step 1.2: Initialize SAM Application

```bash
# Initialize with SAM (or create manually)
sam init --runtime python3.12 --name serverless-order-system --app-template hello-world

# Or start fresh
cat > template.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Serverless Order Processing System

Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256
    Tracing: Active
    Environment:
      Variables:
        LOG_LEVEL: INFO
        POWERTOOLS_SERVICE_NAME: order-system

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  # Resources will be added in subsequent steps
  PlaceholderFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      CodeUri: src/orders/

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
EOF
```

---

## Part 2: Create Lambda Functions (Console Method)

### Step 2.1: Create Order Function via Console

1. **Navigate to Lambda Console**: https://console.aws.amazon.com/lambda

2. **Create Function**:
   - Click "Create function"
   - Select "Author from scratch"
   - Function name: `order-create-function`
   - Runtime: Python 3.12
   - Architecture: x86_64
   - Click "Create function"

3. **Add Code**:
```python
import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders')

def handler(event, context):
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))

        # Create order
        order = {
            'orderId': str(uuid.uuid4()),
            'customerId': body.get('customerId'),
            'items': body.get('items', []),
            'total': body.get('total', 0),
            'status': 'pending',
            'createdAt': datetime.utcnow().isoformat()
        }

        # Save to DynamoDB
        table.put_item(Item=order)

        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'order': order})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

4. **Configure Environment Variables**:
   - Add `ORDERS_TABLE` = `orders`

5. **Create IAM Policy**:
   - Go to Configuration > Permissions
   - Click on the role
   - Add inline policy for DynamoDB access

---

## Part 3: Create Lambda Functions (CLI Method)

### Step 3.1: Create Shared Utilities Layer

```bash
# Create layer directory
mkdir -p layers/shared/python

# Create shared utilities
cat > layers/shared/python/utils.py << 'EOF'
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from functools import wraps

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def json_dumps(obj):
    """JSON serialize with Decimal support"""
    return json.dumps(obj, cls=DecimalEncoder)


def create_response(status_code, body, headers=None):
    """Create standardized API response"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    if headers:
        default_headers.update(headers)

    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json_dumps(body) if isinstance(body, dict) else body
    }


def parse_body(event):
    """Parse JSON body from event"""
    body = event.get('body', '{}')
    if isinstance(body, str):
        return json.loads(body)
    return body


def get_path_param(event, name):
    """Get path parameter"""
    params = event.get('pathParameters') or {}
    return params.get(name)


def lambda_handler(func):
    """Decorator for Lambda handlers with logging and error handling"""
    @wraps(func)
    def wrapper(event, context):
        logger.info(f"Event: {json.dumps(event)}")
        try:
            result = func(event, context)
            logger.info(f"Response: {result['statusCode']}")
            return result
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return create_response(400, {'error': str(e)})
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return create_response(500, {'error': 'Internal server error'})
    return wrapper


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).isoformat()
EOF

# Package layer
cd layers/shared
zip -r ../../shared-layer.zip python/
cd ../..
```

### Step 3.2: Create Orders Functions

```bash
# Create orders handler
cat > src/orders/app.py << 'EOF'
import os
import uuid
import boto3
from utils import (
    lambda_handler, create_response, parse_body,
    get_path_param, get_timestamp
)

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ.get('ORDERS_TABLE', 'orders'))

# Initialize EventBridge
eventbridge = boto3.client('events')
EVENT_BUS = os.environ.get('EVENT_BUS', 'default')


@lambda_handler
def create_order(event, context):
    """Create a new order"""
    body = parse_body(event)

    # Validate required fields
    required = ['customerId', 'items']
    missing = [f for f in required if f not in body]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Calculate total
    total = sum(item.get('price', 0) * item.get('quantity', 1)
                for item in body['items'])

    # Create order
    order = {
        'orderId': str(uuid.uuid4()),
        'customerId': body['customerId'],
        'items': body['items'],
        'total': total,
        'status': 'pending',
        'createdAt': get_timestamp(),
        'updatedAt': get_timestamp()
    }

    # Save to DynamoDB
    orders_table.put_item(Item=order)

    # Publish event
    eventbridge.put_events(
        Entries=[{
            'Source': 'com.orders.service',
            'DetailType': 'Order Created',
            'Detail': json.dumps(order),
            'EventBusName': EVENT_BUS
        }]
    )

    return create_response(201, {
        'message': 'Order created successfully',
        'order': order
    })


@lambda_handler
def get_order(event, context):
    """Get order by ID"""
    order_id = get_path_param(event, 'orderId')
    if not order_id:
        raise ValueError("Order ID is required")

    response = orders_table.get_item(Key={'orderId': order_id})
    order = response.get('Item')

    if not order:
        return create_response(404, {'error': 'Order not found'})

    return create_response(200, {'order': order})


@lambda_handler
def list_orders(event, context):
    """List all orders"""
    # Get query parameters
    params = event.get('queryStringParameters') or {}
    customer_id = params.get('customerId')

    if customer_id:
        # Query by customer using GSI
        response = orders_table.query(
            IndexName='customer-index',
            KeyConditionExpression='customerId = :cid',
            ExpressionAttributeValues={':cid': customer_id}
        )
    else:
        # Scan all (use with caution in production)
        response = orders_table.scan(Limit=100)

    orders = response.get('Items', [])
    return create_response(200, {
        'orders': orders,
        'count': len(orders)
    })


@lambda_handler
def update_order_status(event, context):
    """Update order status"""
    order_id = get_path_param(event, 'orderId')
    body = parse_body(event)

    if not order_id:
        raise ValueError("Order ID is required")
    if 'status' not in body:
        raise ValueError("Status is required")

    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if body['status'] not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

    response = orders_table.update_item(
        Key={'orderId': order_id},
        UpdateExpression='SET #status = :status, updatedAt = :updated',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': body['status'],
            ':updated': get_timestamp()
        },
        ReturnValues='ALL_NEW'
    )

    order = response.get('Attributes')

    # Publish status change event
    eventbridge.put_events(
        Entries=[{
            'Source': 'com.orders.service',
            'DetailType': 'Order Status Changed',
            'Detail': json.dumps({
                'orderId': order_id,
                'status': body['status'],
                'order': order
            }),
            'EventBusName': EVENT_BUS
        }]
    )

    return create_response(200, {
        'message': 'Order status updated',
        'order': order
    })


# Add json import at top
import json
EOF

# Create requirements.txt
cat > src/orders/requirements.txt << 'EOF'
boto3>=1.26.0
EOF
```

### Step 3.3: Create Payment Function

```bash
cat > src/payments/app.py << 'EOF'
import os
import json
import boto3
from utils import lambda_handler, create_response, get_timestamp

dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ.get('ORDERS_TABLE', 'orders'))


@lambda_handler
def process_payment(event, context):
    """Process payment for order - called by Step Functions"""
    order = event.get('order', event)
    order_id = order.get('orderId')
    amount = order.get('total', 0)

    # Simulate payment processing
    # In production, integrate with payment gateway
    import random
    success = random.random() > 0.1  # 90% success rate

    if not success:
        raise Exception("Payment processing failed")

    # Update order status
    orders_table.update_item(
        Key={'orderId': order_id},
        UpdateExpression='SET #status = :status, paymentStatus = :ps, updatedAt = :updated',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':status': 'paid',
            ':ps': 'completed',
            ':updated': get_timestamp()
        }
    )

    return {
        'orderId': order_id,
        'paymentStatus': 'completed',
        'amount': amount,
        'transactionId': f"TXN-{order_id[:8].upper()}"
    }
EOF
```

### Step 3.4: Create Notification Function

```bash
cat > src/notifications/app.py << 'EOF'
import os
import json
import boto3
from utils import lambda_handler, get_timestamp

sns = boto3.client('sns')
NOTIFICATION_TOPIC = os.environ.get('NOTIFICATION_TOPIC', '')


@lambda_handler
def send_notification(event, context):
    """Send order notification"""
    order = event.get('order', event)
    order_id = order.get('orderId')
    status = order.get('status', 'unknown')

    # Determine notification message
    messages = {
        'pending': 'Your order has been received and is being processed.',
        'paid': 'Payment confirmed for your order.',
        'shipped': 'Your order has been shipped!',
        'delivered': 'Your order has been delivered.',
        'cancelled': 'Your order has been cancelled.'
    }

    message = messages.get(status, f'Order status updated to: {status}')

    notification = {
        'orderId': order_id,
        'status': status,
        'message': message,
        'timestamp': get_timestamp()
    }

    # Publish to SNS if topic configured
    if NOTIFICATION_TOPIC:
        sns.publish(
            TopicArn=NOTIFICATION_TOPIC,
            Subject=f"Order {order_id} - {status.title()}",
            Message=json.dumps(notification)
        )

    return notification


@lambda_handler
def process_order_event(event, context):
    """Process EventBridge order events"""
    detail = event.get('detail', {})
    detail_type = event.get('detail-type', '')

    print(f"Received event: {detail_type}")
    print(f"Detail: {json.dumps(detail)}")

    if detail_type == 'Order Created':
        # Send welcome notification
        return send_notification({'order': detail}, context)

    elif detail_type == 'Order Status Changed':
        # Send status update
        return send_notification({'order': detail.get('order', detail)}, context)

    return {'status': 'processed'}
EOF
```

---

## Part 4: Set Up API Gateway REST API

### Step 4.1: Update SAM Template with Complete Resources

```yaml
# template.yaml - Complete version
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Serverless Order Processing System

Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256
    Tracing: Active
    Layers:
      - !Ref SharedUtilsLayer
    Environment:
      Variables:
        LOG_LEVEL: INFO
        ORDERS_TABLE: !Ref OrdersTable
        EVENT_BUS: !Ref OrderEventBus
        NOTIFICATION_TOPIC: !Ref NotificationTopic

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Resources:
  # ============= API Gateway =============
  OrdersApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub ${AWS::StackName}-api
      StageName: !Ref Environment
      Description: Orders REST API
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
      TracingEnabled: true

  # ============= Lambda Layer =============
  SharedUtilsLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub ${AWS::StackName}-shared-utils
      Description: Shared utilities
      ContentUri: layers/shared/
      CompatibleRuntimes:
        - python3.12
    Metadata:
      BuildMethod: python3.12

  # ============= Orders Functions =============
  CreateOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-create-order
      Handler: app.create_order
      CodeUri: src/orders/
      Description: Create new order
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - EventBridgePutEventsPolicy:
            EventBusName: !Ref OrderEventBus
      Events:
        CreateOrder:
          Type: Api
          Properties:
            RestApiId: !Ref OrdersApi
            Path: /orders
            Method: POST

  GetOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-get-order
      Handler: app.get_order
      CodeUri: src/orders/
      Description: Get order by ID
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref OrdersTable
      Events:
        GetOrder:
          Type: Api
          Properties:
            RestApiId: !Ref OrdersApi
            Path: /orders/{orderId}
            Method: GET

  ListOrdersFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-list-orders
      Handler: app.list_orders
      CodeUri: src/orders/
      Description: List all orders
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref OrdersTable
      Events:
        ListOrders:
          Type: Api
          Properties:
            RestApiId: !Ref OrdersApi
            Path: /orders
            Method: GET

  UpdateOrderStatusFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-update-status
      Handler: app.update_order_status
      CodeUri: src/orders/
      Description: Update order status
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - EventBridgePutEventsPolicy:
            EventBusName: !Ref OrderEventBus
      Events:
        UpdateStatus:
          Type: Api
          Properties:
            RestApiId: !Ref OrdersApi
            Path: /orders/{orderId}/status
            Method: PUT

  # ============= Payment Function =============
  ProcessPaymentFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-process-payment
      Handler: app.process_payment
      CodeUri: src/payments/
      Description: Process order payment
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable

  # ============= Notification Function =============
  SendNotificationFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-send-notification
      Handler: app.send_notification
      CodeUri: src/notifications/
      Policies:
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt NotificationTopic.TopicName

  ProcessOrderEventFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-process-event
      Handler: app.process_order_event
      CodeUri: src/notifications/
      Policies:
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt NotificationTopic.TopicName
      Events:
        OrderCreated:
          Type: EventBridgeRule
          Properties:
            EventBusName: !Ref OrderEventBus
            Pattern:
              source:
                - com.orders.service
              detail-type:
                - Order Created
        OrderStatusChanged:
          Type: EventBridgeRule
          Properties:
            EventBusName: !Ref OrderEventBus
            Pattern:
              source:
                - com.orders.service
              detail-type:
                - Order Status Changed

  # ============= DynamoDB =============
  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${AWS::StackName}-orders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
        - AttributeName: customerId
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: customer-index
          KeySchema:
            - AttributeName: customerId
              KeyType: HASH
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

  # ============= EventBridge =============
  OrderEventBus:
    Type: AWS::Events::EventBus
    Properties:
      Name: !Sub ${AWS::StackName}-orders

  # ============= SNS =============
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-notifications

  # ============= S3 =============
  ReceiptsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-receipts-${AWS::AccountId}
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # ============= Step Functions =============
  OrderWorkflow:
    Type: AWS::Serverless::StateMachine
    Properties:
      Name: !Sub ${AWS::StackName}-order-workflow
      DefinitionUri: statemachine/order-workflow.asl.json
      DefinitionSubstitutions:
        ProcessPaymentArn: !GetAtt ProcessPaymentFunction.Arn
        SendNotificationArn: !GetAtt SendNotificationFunction.Arn
        OrdersTableName: !Ref OrdersTable
        ReceiptsBucket: !Ref ReceiptsBucket
      Policies:
        - LambdaInvokePolicy:
            FunctionName: !Ref ProcessPaymentFunction
        - LambdaInvokePolicy:
            FunctionName: !Ref SendNotificationFunction
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - S3CrudPolicy:
            BucketName: !Ref ReceiptsBucket

  # Rule to trigger workflow on high-value orders
  HighValueOrderRule:
    Type: AWS::Events::Rule
    Properties:
      Name: !Sub ${AWS::StackName}-high-value-orders
      EventBusName: !Ref OrderEventBus
      EventPattern:
        source:
          - com.orders.service
        detail-type:
          - Order Created
        detail:
          total:
            - numeric:
                - '>='
                - 100
      Targets:
        - Id: StartWorkflow
          Arn: !Ref OrderWorkflow
          RoleArn: !GetAtt EventBridgeWorkflowRole.Arn
          InputTransformer:
            InputPathsMap:
              order: "$.detail"
            InputTemplate: '{"order": <order>}'

  EventBridgeWorkflowRole:
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
        - PolicyName: StartExecution
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: states:StartExecution
                Resource: !Ref OrderWorkflow

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${OrdersApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/"

  OrdersTableName:
    Description: DynamoDB Orders table
    Value: !Ref OrdersTable

  EventBusName:
    Description: EventBridge bus name
    Value: !Ref OrderEventBus

  WorkflowArn:
    Description: Step Functions workflow ARN
    Value: !Ref OrderWorkflow

  ReceiptsBucketName:
    Description: S3 receipts bucket
    Value: !Ref ReceiptsBucket
```

---

## Part 5: Implement CRUD with DynamoDB

### Step 5.1: Test DynamoDB Operations

```bash
# Create table directly (for testing before SAM deploy)
aws dynamodb create-table \
    --table-name orders-test \
    --attribute-definitions \
        AttributeName=orderId,AttributeType=S \
        AttributeName=customerId,AttributeType=S \
    --key-schema \
        AttributeName=orderId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes \
        'IndexName=customer-index,KeySchema=[{AttributeName=customerId,KeyType=HASH}],Projection={ProjectionType=ALL}'

# Put item
aws dynamodb put-item \
    --table-name orders-test \
    --item '{
        "orderId": {"S": "ORD-001"},
        "customerId": {"S": "CUST-001"},
        "items": {"L": [{"M": {"productId": {"S": "PROD-1"}, "quantity": {"N": "2"}, "price": {"N": "29.99"}}}]},
        "total": {"N": "59.98"},
        "status": {"S": "pending"},
        "createdAt": {"S": "2024-01-15T12:00:00Z"}
    }'

# Get item
aws dynamodb get-item \
    --table-name orders-test \
    --key '{"orderId": {"S": "ORD-001"}}'

# Query by customer
aws dynamodb query \
    --table-name orders-test \
    --index-name customer-index \
    --key-condition-expression "customerId = :cid" \
    --expression-attribute-values '{":cid": {"S": "CUST-001"}}'

# Update status
aws dynamodb update-item \
    --table-name orders-test \
    --key '{"orderId": {"S": "ORD-001"}}' \
    --update-expression "SET #status = :status" \
    --expression-attribute-names '{"#status": "status"}' \
    --expression-attribute-values '{":status": {"S": "processing"}}'

# Clean up test table
aws dynamodb delete-table --table-name orders-test
```

---

## Part 6: Create Step Functions Workflow

### Step 6.1: Create State Machine Definition

```bash
cat > statemachine/order-workflow.asl.json << 'EOF'
{
  "Comment": "Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Pass",
      "Comment": "Validate order data",
      "Next": "CheckOrderTotal"
    },
    "CheckOrderTotal": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.order.total",
          "NumericGreaterThanEquals": 1000,
          "Next": "RequireApproval"
        }
      ],
      "Default": "ProcessPayment"
    },
    "RequireApproval": {
      "Type": "Wait",
      "Comment": "Wait for manual approval (simulated)",
      "Seconds": 5,
      "Next": "ProcessPayment"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "${ProcessPaymentArn}",
      "Parameters": {
        "order.$": "$.order"
      },
      "ResultPath": "$.paymentResult",
      "Next": "UpdateOrderStatus",
      "Retry": [
        {
          "ErrorEquals": ["States.TaskFailed"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "ResultPath": "$.error",
          "Next": "PaymentFailed"
        }
      ]
    },
    "UpdateOrderStatus": {
      "Type": "Task",
      "Resource": "arn:aws:states:::dynamodb:updateItem",
      "Parameters": {
        "TableName": "${OrdersTableName}",
        "Key": {
          "orderId": {
            "S.$": "$.order.orderId"
          }
        },
        "UpdateExpression": "SET #status = :status, paymentInfo = :payment",
        "ExpressionAttributeNames": {
          "#status": "status"
        },
        "ExpressionAttributeValues": {
          ":status": {"S": "paid"},
          ":payment": {"S.$": "States.JsonToString($.paymentResult)"}
        }
      },
      "ResultPath": "$.updateResult",
      "Next": "GenerateReceipt"
    },
    "GenerateReceipt": {
      "Type": "Task",
      "Resource": "arn:aws:states:::aws-sdk:s3:putObject",
      "Parameters": {
        "Bucket": "${ReceiptsBucket}",
        "Key.$": "States.Format('receipts/{}/receipt.json', $.order.orderId)",
        "Body.$": "States.JsonToString($.order)",
        "ContentType": "application/json"
      },
      "ResultPath": "$.receiptResult",
      "Next": "NotifyCustomer"
    },
    "NotifyCustomer": {
      "Type": "Task",
      "Resource": "${SendNotificationArn}",
      "Parameters": {
        "order.$": "$.order",
        "paymentResult.$": "$.paymentResult"
      },
      "ResultPath": "$.notificationResult",
      "Next": "OrderComplete"
    },
    "OrderComplete": {
      "Type": "Succeed"
    },
    "PaymentFailed": {
      "Type": "Task",
      "Resource": "arn:aws:states:::dynamodb:updateItem",
      "Parameters": {
        "TableName": "${OrdersTableName}",
        "Key": {
          "orderId": {
            "S.$": "$.order.orderId"
          }
        },
        "UpdateExpression": "SET #status = :status, errorInfo = :error",
        "ExpressionAttributeNames": {
          "#status": "status"
        },
        "ExpressionAttributeValues": {
          ":status": {"S": "payment_failed"},
          ":error": {"S.$": "States.JsonToString($.error)"}
        }
      },
      "ResultPath": "$.failureUpdate",
      "Next": "NotifyPaymentFailure"
    },
    "NotifyPaymentFailure": {
      "Type": "Task",
      "Resource": "${SendNotificationArn}",
      "Parameters": {
        "order.$": "$.order",
        "error.$": "$.error",
        "message": "Payment processing failed"
      },
      "End": true
    }
  }
}
EOF
```

---

## Part 7: Event-Driven Processing with S3

### Step 7.1: Create S3 Event Handler

```bash
cat > src/orders/s3_handler.py << 'EOF'
import os
import json
import boto3
from urllib.parse import unquote_plus
from utils import lambda_handler

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
orders_table = dynamodb.Table(os.environ.get('ORDERS_TABLE', 'orders'))


@lambda_handler
def process_upload(event, context):
    """Process files uploaded to S3"""
    results = []

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        print(f"Processing: s3://{bucket}/{key}")

        # Get the object
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        # Parse based on file type
        if key.endswith('.json'):
            data = json.loads(content)
            result = process_json_upload(data, key)
        elif key.endswith('.csv'):
            result = process_csv_upload(content, key)
        else:
            result = {'status': 'skipped', 'reason': 'unsupported file type'}

        results.append({
            'key': key,
            'result': result
        })

    return {'processed': results}


def process_json_upload(data, key):
    """Process JSON file containing orders"""
    if 'orders' in data:
        # Batch import
        count = 0
        for order in data['orders']:
            orders_table.put_item(Item=order)
            count += 1
        return {'status': 'imported', 'count': count}
    elif 'orderId' in data:
        # Single order
        orders_table.put_item(Item=data)
        return {'status': 'imported', 'orderId': data['orderId']}
    return {'status': 'skipped', 'reason': 'unknown format'}


def process_csv_upload(content, key):
    """Process CSV file containing orders"""
    import csv
    from io import StringIO

    reader = csv.DictReader(StringIO(content))
    count = 0

    for row in reader:
        order = {
            'orderId': row.get('order_id'),
            'customerId': row.get('customer_id'),
            'total': float(row.get('total', 0)),
            'status': row.get('status', 'pending')
        }
        orders_table.put_item(Item=order)
        count += 1

    return {'status': 'imported', 'count': count}
EOF
```

### Step 7.2: Add S3 Trigger to Template

Add this to the Resources section:

```yaml
  # S3 Upload Handler
  ProcessUploadFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-process-upload
      Handler: s3_handler.process_upload
      CodeUri: src/orders/
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref UploadsBucket
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
      Events:
        S3Upload:
          Type: S3
          Properties:
            Bucket: !Ref UploadsBucket
            Events: s3:ObjectCreated:*
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: uploads/

  UploadsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-uploads-${AWS::AccountId}
```

---

## Part 8: Deploy with SAM

### Step 8.1: Create SAM Configuration

```bash
cat > samconfig.toml << 'EOF'
version = 0.1

[default]
[default.build]
[default.build.parameters]
cached = true
parallel = true

[default.deploy]
[default.deploy.parameters]
stack_name = "serverless-order-system"
resolve_s3 = true
s3_prefix = "serverless-order-system"
region = "us-east-1"
capabilities = "CAPABILITY_IAM CAPABILITY_NAMED_IAM"
confirm_changeset = true
parameter_overrides = "Environment=dev"

[default.sync]
[default.sync.parameters]
watch = true

[default.local_invoke]
[default.local_invoke.parameters]
env_vars = "env.json"
EOF
```

### Step 8.2: Build and Deploy

```bash
# Validate template
sam validate --lint

# Build the application
sam build

# Deploy (guided for first time)
sam deploy --guided

# Or deploy with existing config
sam deploy
```

### Step 8.3: Test the Deployment

```bash
# Get API endpoint from outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name serverless-order-system \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

echo "API Endpoint: $API_ENDPOINT"

# Create an order
curl -X POST "$API_ENDPOINT/orders" \
    -H "Content-Type: application/json" \
    -d '{
        "customerId": "CUST-001",
        "items": [
            {"productId": "PROD-1", "name": "Widget", "quantity": 2, "price": 29.99},
            {"productId": "PROD-2", "name": "Gadget", "quantity": 1, "price": 49.99}
        ]
    }'

# List orders
curl "$API_ENDPOINT/orders"

# Get specific order (replace ORDER_ID)
curl "$API_ENDPOINT/orders/ORDER_ID"

# Update order status
curl -X PUT "$API_ENDPOINT/orders/ORDER_ID/status" \
    -H "Content-Type: application/json" \
    -d '{"status": "processing"}'
```

---

## Part 9: Local Testing

### Step 9.1: Create Test Events

```bash
cat > events/create-order.json << 'EOF'
{
  "resource": "/orders",
  "path": "/orders",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"customerId\": \"CUST-TEST\", \"items\": [{\"productId\": \"PROD-1\", \"quantity\": 2, \"price\": 29.99}]}"
}
EOF

cat > events/get-order.json << 'EOF'
{
  "resource": "/orders/{orderId}",
  "path": "/orders/test-order-123",
  "httpMethod": "GET",
  "pathParameters": {
    "orderId": "test-order-123"
  }
}
EOF
```

### Step 9.2: Local Testing Commands

```bash
# Start local API
sam local start-api --port 3000

# In another terminal, test endpoints
curl http://localhost:3000/orders

# Invoke function directly
sam local invoke CreateOrderFunction --event events/create-order.json

# Start local Lambda endpoint
sam local start-lambda
```

### Step 9.3: Local DynamoDB

```bash
# Start DynamoDB Local with Docker
docker run -p 8000:8000 amazon/dynamodb-local

# Create table in local DynamoDB
aws dynamodb create-table \
    --endpoint-url http://localhost:8000 \
    --table-name orders \
    --attribute-definitions AttributeName=orderId,AttributeType=S \
    --key-schema AttributeName=orderId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# Create env.json for local testing
cat > env.json << 'EOF'
{
  "CreateOrderFunction": {
    "ORDERS_TABLE": "orders",
    "AWS_SAM_LOCAL": "true"
  }
}
EOF
```

---

## Part 10: Complete Cleanup

### Step 10.1: Delete All Resources

```bash
#!/bin/bash
# cleanup.sh - Complete cleanup script

STACK_NAME="serverless-order-system"

echo "Starting cleanup of $STACK_NAME..."

# Get bucket names before deletion
RECEIPTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ReceiptsBucketName`].OutputValue' \
    --output text 2>/dev/null)

UPLOADS_BUCKET="${STACK_NAME}-uploads-$(aws sts get-caller-identity --query Account --output text)"

# Empty S3 buckets (required before deletion)
for BUCKET in $RECEIPTS_BUCKET $UPLOADS_BUCKET; do
    if [ -n "$BUCKET" ]; then
        echo "Emptying bucket: $BUCKET"
        aws s3 rm s3://$BUCKET --recursive 2>/dev/null || true

        # Delete versioned objects
        aws s3api list-object-versions \
            --bucket $BUCKET \
            --query 'Versions[].{Key:Key,VersionId:VersionId}' \
            --output text 2>/dev/null | while read KEY VERSION; do
            if [ -n "$KEY" ]; then
                aws s3api delete-object \
                    --bucket $BUCKET \
                    --key "$KEY" \
                    --version-id "$VERSION" 2>/dev/null || true
            fi
        done

        # Delete markers
        aws s3api list-object-versions \
            --bucket $BUCKET \
            --query 'DeleteMarkers[].{Key:Key,VersionId:VersionId}' \
            --output text 2>/dev/null | while read KEY VERSION; do
            if [ -n "$KEY" ]; then
                aws s3api delete-object \
                    --bucket $BUCKET \
                    --key "$KEY" \
                    --version-id "$VERSION" 2>/dev/null || true
            fi
        done
    fi
done

# Delete CloudFormation stack
echo "Deleting CloudFormation stack..."
aws cloudformation delete-stack --stack-name $STACK_NAME

# Wait for deletion
echo "Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME

echo "Cleanup complete!"

# Verify deletion
aws cloudformation describe-stacks --stack-name $STACK_NAME 2>&1 | grep -q "does not exist" && \
    echo "Stack successfully deleted" || echo "Warning: Stack may still exist"
```

### Step 10.2: CLI Cleanup Commands

```bash
# Delete stack
sam delete --stack-name serverless-order-system

# Or manually:
# 1. Empty S3 buckets
aws s3 rm s3://serverless-order-system-receipts-ACCOUNT_ID --recursive
aws s3 rm s3://serverless-order-system-uploads-ACCOUNT_ID --recursive

# 2. Delete stack
aws cloudformation delete-stack --stack-name serverless-order-system

# 3. Wait for completion
aws cloudformation wait stack-delete-complete --stack-name serverless-order-system

# 4. Verify
aws cloudformation describe-stacks --stack-name serverless-order-system
```

---

## Lab Summary

### What You Built

| Component | Purpose |
|-----------|---------|
| API Gateway REST API | HTTP endpoints for orders |
| Lambda Functions (6) | Business logic handlers |
| Lambda Layer | Shared utilities |
| DynamoDB Table | Order data storage |
| Step Functions | Order processing workflow |
| EventBridge | Event routing |
| SNS Topic | Notifications |
| S3 Buckets | File storage |

### Key Learnings

1. **Lambda Functions**: Creating handlers with proper error handling
2. **API Gateway**: REST API with CORS and routing
3. **DynamoDB**: CRUD operations with GSI
4. **Step Functions**: Complex workflow orchestration
5. **EventBridge**: Event-driven architecture
6. **SAM**: Infrastructure as code deployment
7. **Local Testing**: SAM CLI for development

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Final Architecture                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Client ──▶ API Gateway ──▶ Lambda Functions ──▶ DynamoDB          │
│                  │                  │                                │
│                  │                  ▼                                │
│                  │           EventBridge                             │
│                  │                  │                                │
│                  │         ┌───────┴───────┐                        │
│                  │         ▼               ▼                         │
│                  │   Step Functions    Notifications                 │
│                  │         │               │                         │
│                  │    ┌────┴────┐         ▼                         │
│                  │    ▼         ▼        SNS                        │
│                  │ DynamoDB    S3                                    │
│                  │                                                   │
│                  └──▶ S3 (Uploads) ──▶ Lambda ──▶ DynamoDB          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Next Steps

1. Add authentication with Cognito
2. Implement caching with ElastiCache
3. Add monitoring with CloudWatch dashboards
4. Implement CI/CD with CodePipeline
5. Add API versioning
6. Implement rate limiting

---

## Additional Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Step Functions Developer Guide](https://docs.aws.amazon.com/step-functions/)
- [EventBridge User Guide](https://docs.aws.amazon.com/eventbridge/)
