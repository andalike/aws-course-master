# Hands-On Lab: Complete Monitoring Solution

## Lab Overview

In this comprehensive lab, you will build a complete monitoring solution for a sample application using all the AWS monitoring services covered in this module. By the end of this lab, you will have hands-on experience with CloudWatch metrics, alarms, dashboards, logs, X-Ray tracing, CloudTrail, AWS Config, and SNS notifications.

**Duration**: 2-3 hours
**Prerequisites**: AWS account with administrator access, AWS CLI configured

---

## Lab Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Complete Monitoring Lab Architecture                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Sample Application                            │   │
│  │                                                                       │   │
│  │   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      │   │
│  │   │ API Gateway  │─────►│   Lambda     │─────►│  DynamoDB    │      │   │
│  │   │              │      │ (X-Ray)      │      │              │      │   │
│  │   └──────────────┘      └──────────────┘      └──────────────┘      │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Monitoring Stack                              │   │
│  │                                                                       │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │   │  CloudWatch  │  │  CloudWatch  │  │   X-Ray      │              │   │
│  │   │   Metrics    │  │    Logs      │  │   Traces     │              │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │                                                                       │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │   │  CloudWatch  │  │  CloudTrail  │  │  AWS Config  │              │   │
│  │   │   Alarms     │  │              │  │              │              │   │
│  │   └──────┬───────┘  └──────────────┘  └──────────────┘              │   │
│  │          │                                                            │   │
│  │          ▼                                                            │   │
│  │   ┌──────────────┐                                                    │   │
│  │   │     SNS      │─────► Email/Slack/Lambda                          │   │
│  │   └──────────────┘                                                    │   │
│  │                                                                       │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐│   │
│  │   │                    CloudWatch Dashboard                          ││   │
│  │   │  [Metrics] [Logs] [Alarms] [Traces] [Custom Widgets]            ││   │
│  │   └─────────────────────────────────────────────────────────────────┘│   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Setup and Prerequisites

### 1.1 Set Environment Variables

```bash
# Set your AWS region
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export LAB_NAME="monitoring-lab"

echo "Region: $AWS_REGION"
echo "Account: $ACCOUNT_ID"
echo "Lab Name: $LAB_NAME"
```

### 1.2 Create S3 Buckets

```bash
# Bucket for Lambda code
aws s3 mb s3://$LAB_NAME-lambda-$ACCOUNT_ID --region $AWS_REGION

# Bucket for CloudTrail logs
aws s3 mb s3://$LAB_NAME-cloudtrail-$ACCOUNT_ID --region $AWS_REGION

# Bucket for Config logs
aws s3 mb s3://$LAB_NAME-config-$ACCOUNT_ID --region $AWS_REGION

echo "Buckets created successfully"
```

### 1.3 Create IAM Roles

```bash
# Create Lambda execution role
cat > /tmp/lambda-trust-policy.json << 'EOF'
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

aws iam create-role \
    --role-name $LAB_NAME-lambda-role \
    --assume-role-policy-document file:///tmp/lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
    --role-name $LAB_NAME-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --role-name $LAB_NAME-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess

aws iam attach-role-policy \
    --role-name $LAB_NAME-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

echo "IAM roles created successfully"

# Wait for role to propagate
sleep 10
```

---

## Part 2: Create Sample Application

### 2.1 Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name $LAB_NAME-orders \
    --attribute-definitions \
        AttributeName=order_id,AttributeType=S \
    --key-schema \
        AttributeName=order_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Lab,Value=$LAB_NAME

echo "DynamoDB table created"

# Wait for table to be active
aws dynamodb wait table-exists --table-name $LAB_NAME-orders
```

### 2.2 Create Lambda Function

```bash
# Create Lambda function code
cat > /tmp/lambda_function.py << 'EOF'
import json
import boto3
import os
import uuid
import random
import time
from datetime import datetime
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch AWS SDK for X-Ray
patch_all()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'monitoring-lab-orders'))

def lambda_handler(event, context):
    """
    Sample order processing Lambda function with X-Ray tracing
    """
    # Add annotation for filtering
    xray_recorder.put_annotation('environment', 'lab')

    # Parse request
    if 'body' in event:
        try:
            body = json.loads(event.get('body', '{}'))
        except:
            body = {}
    else:
        body = event

    action = body.get('action', 'create')
    order_id = body.get('order_id', str(uuid.uuid4()))

    # Add annotation
    xray_recorder.put_annotation('action', action)
    xray_recorder.put_annotation('order_id', order_id)

    try:
        if action == 'create':
            result = create_order(order_id, body)
        elif action == 'get':
            result = get_order(order_id)
        elif action == 'simulate_error':
            result = simulate_error()
        elif action == 'simulate_slow':
            result = simulate_slow_request()
        else:
            result = {'error': 'Unknown action'}

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        xray_recorder.current_segment().add_exception(e)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def create_order(order_id, body):
    """Create a new order"""
    with xray_recorder.in_subsegment('create_order') as subsegment:
        order = {
            'order_id': order_id,
            'customer_id': body.get('customer_id', f'customer-{random.randint(1000, 9999)}'),
            'product': body.get('product', 'Sample Product'),
            'quantity': body.get('quantity', random.randint(1, 10)),
            'price': body.get('price', round(random.uniform(10, 500), 2)),
            'status': 'created',
            'created_at': datetime.utcnow().isoformat()
        }

        subsegment.put_metadata('order', order)

        # Simulate some processing time
        time.sleep(random.uniform(0.05, 0.2))

        table.put_item(Item=order)
        print(f"INFO: Order created: {order_id}")

        return {'message': 'Order created', 'order': order}

def get_order(order_id):
    """Get an existing order"""
    with xray_recorder.in_subsegment('get_order') as subsegment:
        subsegment.put_annotation('order_id', order_id)

        response = table.get_item(Key={'order_id': order_id})
        order = response.get('Item')

        if order:
            print(f"INFO: Order retrieved: {order_id}")
            return {'order': order}
        else:
            print(f"WARN: Order not found: {order_id}")
            return {'error': 'Order not found'}

def simulate_error():
    """Simulate an error for testing"""
    print("ERROR: Simulated error occurred")
    raise Exception("This is a simulated error for testing monitoring")

def simulate_slow_request():
    """Simulate a slow request"""
    with xray_recorder.in_subsegment('slow_operation') as subsegment:
        delay = random.uniform(2, 5)
        subsegment.put_annotation('delay_seconds', delay)
        print(f"WARN: Simulating slow request with {delay:.2f}s delay")
        time.sleep(delay)
        return {'message': f'Slow request completed after {delay:.2f} seconds'}
EOF

# Create deployment package
cd /tmp
pip install aws-xray-sdk -t .
zip -r lambda_package.zip lambda_function.py aws_xray_sdk* wrapt* future* jsonpickle*

# Upload to S3
aws s3 cp lambda_package.zip s3://$LAB_NAME-lambda-$ACCOUNT_ID/

# Create Lambda function
aws lambda create-function \
    --function-name $LAB_NAME-order-processor \
    --runtime python3.9 \
    --handler lambda_function.lambda_handler \
    --role arn:aws:iam::$ACCOUNT_ID:role/$LAB_NAME-lambda-role \
    --code S3Bucket=$LAB_NAME-lambda-$ACCOUNT_ID,S3Key=lambda_package.zip \
    --timeout 30 \
    --memory-size 256 \
    --tracing-config Mode=Active \
    --environment Variables="{TABLE_NAME=$LAB_NAME-orders}" \
    --tags Lab=$LAB_NAME

echo "Lambda function created"

cd -
```

### 2.3 Create API Gateway

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name "$LAB_NAME-api" \
    --description "Monitoring Lab API" \
    --endpoint-configuration types=REGIONAL \
    --query 'id' \
    --output text)

echo "API ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[0].id' \
    --output text)

# Create /orders resource
RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part orders \
    --query 'id' \
    --output text)

# Create POST method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE

# Create Lambda integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$AWS_REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$AWS_REGION:$ACCOUNT_ID:function:$LAB_NAME-order-processor/invocations"

# Add Lambda permission
aws lambda add-permission \
    --function-name $LAB_NAME-order-processor \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$AWS_REGION:$ACCOUNT_ID:$API_ID/*/POST/orders"

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --stage-description "Production Stage" \
    --description "Initial deployment"

# Enable X-Ray tracing
aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --patch-operations op=replace,path=/tracingEnabled,value=true

API_URL="https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/prod/orders"
echo "API URL: $API_URL"
```

---

## Part 3: Custom CloudWatch Metrics

### 3.1 Create Custom Metric Publisher

```bash
# Create script to publish custom metrics
cat > /tmp/publish_metrics.sh << 'EOF'
#!/bin/bash

NAMESPACE="MonitoringLab"
REGION=${AWS_REGION:-us-east-1}

# Publish order count metric
aws cloudwatch put-metric-data \
    --namespace $NAMESPACE \
    --metric-name OrderCount \
    --value $((RANDOM % 100 + 1)) \
    --unit Count \
    --dimensions Environment=Production,Service=OrderProcessor \
    --region $REGION

# Publish order value metric
aws cloudwatch put-metric-data \
    --namespace $NAMESPACE \
    --metric-name OrderValue \
    --value $((RANDOM % 1000 + 50)) \
    --unit None \
    --dimensions Environment=Production,Service=OrderProcessor \
    --region $REGION

# Publish processing time metric
aws cloudwatch put-metric-data \
    --namespace $NAMESPACE \
    --metric-name ProcessingTime \
    --value $((RANDOM % 500 + 100)) \
    --unit Milliseconds \
    --dimensions Environment=Production,Service=OrderProcessor \
    --region $REGION

# Publish error count (occasionally)
if [ $((RANDOM % 10)) -eq 0 ]; then
    aws cloudwatch put-metric-data \
        --namespace $NAMESPACE \
        --metric-name ErrorCount \
        --value $((RANDOM % 5 + 1)) \
        --unit Count \
        --dimensions Environment=Production,Service=OrderProcessor \
        --region $REGION
fi

echo "Custom metrics published at $(date)"
EOF

chmod +x /tmp/publish_metrics.sh

# Publish some initial metrics
for i in {1..10}; do
    /tmp/publish_metrics.sh
    sleep 2
done

echo "Custom metrics published successfully"
```

### 3.2 Create Metric Math Expressions

```bash
# Create a composite metric using metric math via dashboard
# (We'll add this to the dashboard in Part 6)
echo "Metric math will be configured in the dashboard"
```

---

## Part 4: Set Up CloudWatch Alarms with SNS

### 4.1 Create SNS Topic

```bash
# Create SNS topic
TOPIC_ARN=$(aws sns create-topic \
    --name $LAB_NAME-alerts \
    --query 'TopicArn' \
    --output text)

echo "Topic ARN: $TOPIC_ARN"

# Create email subscription (replace with your email)
# aws sns subscribe \
#     --topic-arn $TOPIC_ARN \
#     --protocol email \
#     --notification-endpoint your-email@example.com

# Create a test subscription that confirms automatically (for lab purposes)
# For production, use email subscription and confirm it
```

### 4.2 Create CloudWatch Alarms

```bash
# Lambda Error Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "$LAB_NAME-lambda-errors" \
    --alarm-description "Lambda function errors detected" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --dimensions Name=FunctionName,Value=$LAB_NAME-order-processor \
    --alarm-actions $TOPIC_ARN \
    --ok-actions $TOPIC_ARN \
    --treat-missing-data notBreaching

# Lambda Duration Alarm (slow requests)
aws cloudwatch put-metric-alarm \
    --alarm-name "$LAB_NAME-lambda-duration" \
    --alarm-description "Lambda function taking too long" \
    --metric-name Duration \
    --namespace AWS/Lambda \
    --statistic Average \
    --period 300 \
    --threshold 3000 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=FunctionName,Value=$LAB_NAME-order-processor \
    --alarm-actions $TOPIC_ARN \
    --treat-missing-data notBreaching

# Lambda Throttles Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "$LAB_NAME-lambda-throttles" \
    --alarm-description "Lambda function being throttled" \
    --metric-name Throttles \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --dimensions Name=FunctionName,Value=$LAB_NAME-order-processor \
    --alarm-actions $TOPIC_ARN \
    --treat-missing-data notBreaching

# DynamoDB Read Capacity Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "$LAB_NAME-dynamodb-reads" \
    --alarm-description "DynamoDB consumed read capacity high" \
    --metric-name ConsumedReadCapacityUnits \
    --namespace AWS/DynamoDB \
    --statistic Sum \
    --period 300 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=TableName,Value=$LAB_NAME-orders \
    --alarm-actions $TOPIC_ARN \
    --treat-missing-data notBreaching

# API Gateway 5XX Errors
aws cloudwatch put-metric-alarm \
    --alarm-name "$LAB_NAME-api-5xx-errors" \
    --alarm-description "API Gateway 5XX errors detected" \
    --metric-name 5XXError \
    --namespace AWS/ApiGateway \
    --statistic Sum \
    --period 60 \
    --threshold 5 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --dimensions Name=ApiName,Value=$LAB_NAME-api \
    --alarm-actions $TOPIC_ARN \
    --treat-missing-data notBreaching

# Custom Metric Alarm - Error Count
aws cloudwatch put-metric-alarm \
    --alarm-name "$LAB_NAME-custom-errors" \
    --alarm-description "Custom error count too high" \
    --metric-name ErrorCount \
    --namespace MonitoringLab \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=Environment,Value=Production Name=Service,Value=OrderProcessor \
    --alarm-actions $TOPIC_ARN \
    --treat-missing-data notBreaching

echo "CloudWatch alarms created"

# List alarms
aws cloudwatch describe-alarms \
    --alarm-name-prefix $LAB_NAME \
    --query 'MetricAlarms[*].[AlarmName,StateValue]' \
    --output table
```

### 4.3 Create Composite Alarm

```bash
# Create composite alarm
aws cloudwatch put-composite-alarm \
    --alarm-name "$LAB_NAME-critical-composite" \
    --alarm-description "Critical: Multiple issues detected" \
    --alarm-rule "ALARM(\"$LAB_NAME-lambda-errors\") AND ALARM(\"$LAB_NAME-api-5xx-errors\")" \
    --alarm-actions $TOPIC_ARN \
    --ok-actions $TOPIC_ARN

echo "Composite alarm created"
```

---

## Part 5: Enable CloudTrail Logging

### 5.1 Configure S3 Bucket Policy

```bash
# Create bucket policy for CloudTrail
cat > /tmp/cloudtrail-bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::$LAB_NAME-cloudtrail-$ACCOUNT_ID"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::$LAB_NAME-cloudtrail-$ACCOUNT_ID/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $LAB_NAME-cloudtrail-$ACCOUNT_ID \
    --policy file:///tmp/cloudtrail-bucket-policy.json
```

### 5.2 Create CloudTrail

```bash
# Create CloudWatch Log Group for CloudTrail
aws logs create-log-group --log-group-name /aws/cloudtrail/$LAB_NAME

# Create IAM role for CloudTrail to CloudWatch Logs
cat > /tmp/cloudtrail-cwl-trust.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name $LAB_NAME-cloudtrail-cwl-role \
    --assume-role-policy-document file:///tmp/cloudtrail-cwl-trust.json

# Create and attach policy
cat > /tmp/cloudtrail-cwl-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:$AWS_REGION:$ACCOUNT_ID:log-group:/aws/cloudtrail/$LAB_NAME:*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name $LAB_NAME-cloudtrail-cwl-role \
    --policy-name CloudTrailCloudWatchPolicy \
    --policy-document file:///tmp/cloudtrail-cwl-policy.json

# Wait for role to propagate
sleep 10

# Create CloudTrail
aws cloudtrail create-trail \
    --name $LAB_NAME-trail \
    --s3-bucket-name $LAB_NAME-cloudtrail-$ACCOUNT_ID \
    --include-global-service-events \
    --is-multi-region-trail \
    --enable-log-file-validation \
    --cloud-watch-logs-log-group-arn arn:aws:logs:$AWS_REGION:$ACCOUNT_ID:log-group:/aws/cloudtrail/$LAB_NAME \
    --cloud-watch-logs-role-arn arn:aws:iam::$ACCOUNT_ID:role/$LAB_NAME-cloudtrail-cwl-role

# Start logging
aws cloudtrail start-logging --name $LAB_NAME-trail

echo "CloudTrail created and started"
```

### 5.3 Create CloudTrail Metric Filter

```bash
# Create metric filter for root user activity
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail/$LAB_NAME \
    --filter-name "$LAB_NAME-root-activity" \
    --filter-pattern '{ $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS }' \
    --metric-transformations \
        metricName=RootUserActivity,metricNamespace=CloudTrailMetrics,metricValue=1

# Create metric filter for unauthorized API calls
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail/$LAB_NAME \
    --filter-name "$LAB_NAME-unauthorized-calls" \
    --filter-pattern '{ ($.errorCode = "*UnauthorizedAccess*") || ($.errorCode = "AccessDenied*") }' \
    --metric-transformations \
        metricName=UnauthorizedAPICalls,metricNamespace=CloudTrailMetrics,metricValue=1

echo "CloudTrail metric filters created"
```

---

## Part 6: Set Up X-Ray Tracing

### 6.1 View X-Ray Service Map

```bash
# Generate some test traffic for X-Ray
echo "Generating test traffic for X-Ray..."

for i in {1..20}; do
    # Create order
    curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d '{"action": "create", "product": "Test Product '$i'", "quantity": '$i'}' > /dev/null

    # Get order (some will fail as order_id is random)
    curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d '{"action": "get", "order_id": "test-order-'$i'"}' > /dev/null

    sleep 1
done

echo "Test traffic generated. View X-Ray in console:"
echo "https://$AWS_REGION.console.aws.amazon.com/xray/home?region=$AWS_REGION#/service-map"
```

### 6.2 Create X-Ray Group

```bash
# Create X-Ray group for filtering
aws xray create-group \
    --group-name "$LAB_NAME-production" \
    --filter-expression 'annotation.environment = "lab"'

# Create X-Ray sampling rule
aws xray create-sampling-rule --cli-input-json '{
    "SamplingRule": {
        "RuleName": "'$LAB_NAME'-rule",
        "Priority": 100,
        "FixedRate": 0.5,
        "ReservoirSize": 10,
        "ServiceName": "*",
        "ServiceType": "*",
        "Host": "*",
        "HTTPMethod": "*",
        "URLPath": "/prod/orders",
        "Version": 1
    }
}'

echo "X-Ray group and sampling rule created"
```

---

## Part 7: Analyze Logs with Logs Insights

### 7.1 Sample Logs Insights Queries

```bash
# Create Lambda log group (if not exists)
LOG_GROUP="/aws/lambda/$LAB_NAME-order-processor"

# Generate some logs first
for i in {1..10}; do
    curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d '{"action": "create", "product": "Product '$i'"}' > /dev/null
    sleep 1
done

# Run Logs Insights query - Error analysis
QUERY_ID=$(aws logs start-query \
    --log-group-name $LOG_GROUP \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'fields @timestamp, @message
        | filter @message like /ERROR/
        | sort @timestamp desc
        | limit 20' \
    --query 'queryId' \
    --output text)

echo "Query started: $QUERY_ID"
sleep 5

aws logs get-query-results --query-id $QUERY_ID

echo ""
echo "Run more queries in CloudWatch console:"
echo "https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:logs-insights"
```

### 7.2 Lambda Performance Analysis Query

```bash
# Lambda cold start analysis
QUERY_ID=$(aws logs start-query \
    --log-group-name $LOG_GROUP \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'filter @type = "REPORT"
        | parse @message "Duration: * ms" as duration
        | parse @message "Init Duration: * ms" as initDuration
        | stats count(*) as invocations,
                count(initDuration) as coldStarts,
                avg(duration) as avgDuration,
                max(duration) as maxDuration,
                avg(initDuration) as avgColdStartDuration
        by bin(5m)' \
    --query 'queryId' \
    --output text)

echo "Query started: $QUERY_ID"
sleep 5

aws logs get-query-results --query-id $QUERY_ID
```

---

## Part 8: Create AWS Config Rules

### 8.1 Enable AWS Config

```bash
# Create bucket policy for Config
cat > /tmp/config-bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSConfigBucketPermissionsCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::$LAB_NAME-config-$ACCOUNT_ID"
        },
        {
            "Sid": "AWSConfigBucketDelivery",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::$LAB_NAME-config-$ACCOUNT_ID/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $LAB_NAME-config-$ACCOUNT_ID \
    --policy file:///tmp/config-bucket-policy.json

# Create IAM role for Config
cat > /tmp/config-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name $LAB_NAME-config-role \
    --assume-role-policy-document file:///tmp/config-trust-policy.json

aws iam attach-role-policy \
    --role-name $LAB_NAME-config-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWS_ConfigRole

# Wait for role
sleep 10

# Create configuration recorder
aws configservice put-configuration-recorder --configuration-recorder '{
    "name": "default",
    "roleARN": "arn:aws:iam::'$ACCOUNT_ID':role/'$LAB_NAME'-config-role",
    "recordingGroup": {
        "allSupported": true,
        "includeGlobalResourceTypes": true
    }
}'

# Create delivery channel
aws configservice put-delivery-channel --delivery-channel '{
    "name": "default",
    "s3BucketName": "'$LAB_NAME'-config-'$ACCOUNT_ID'"
}'

# Start recording
aws configservice start-configuration-recorder --configuration-recorder-name default

echo "AWS Config enabled"
```

### 8.2 Create Config Rules

```bash
# Lambda function timeout rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "'$LAB_NAME'-lambda-timeout-check",
    "Description": "Check Lambda function timeout is less than 30 seconds",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "LAMBDA_FUNCTION_SETTINGS_CHECK"
    },
    "InputParameters": "{\"timeout\":\"30\"}",
    "Scope": {
        "ComplianceResourceTypes": ["AWS::Lambda::Function"]
    }
}'

# DynamoDB encryption rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "'$LAB_NAME'-dynamodb-encryption",
    "Description": "Check DynamoDB tables are encrypted",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "DYNAMODB_TABLE_ENCRYPTED_KMS"
    },
    "Scope": {
        "ComplianceResourceTypes": ["AWS::DynamoDB::Table"]
    }
}'

# Lambda X-Ray tracing rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "'$LAB_NAME'-lambda-xray-enabled",
    "Description": "Check Lambda functions have X-Ray tracing enabled",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "LAMBDA_XRAY_TRACING_ENABLED"
    },
    "Scope": {
        "ComplianceResourceTypes": ["AWS::Lambda::Function"]
    }
}'

echo "Config rules created"

# Run rule evaluation
aws configservice start-config-rules-evaluation \
    --config-rule-names $LAB_NAME-lambda-timeout-check $LAB_NAME-dynamodb-encryption $LAB_NAME-lambda-xray-enabled

echo "Config rules evaluation started"
```

---

## Part 9: Create CloudWatch Dashboard

### 9.1 Create Comprehensive Dashboard

```bash
cat > /tmp/dashboard.json << EOF
{
    "widgets": [
        {
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "# Monitoring Lab Dashboard\n**Application Health Overview**"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 1,
            "width": 8,
            "height": 6,
            "properties": {
                "title": "Lambda Invocations",
                "metrics": [
                    ["AWS/Lambda", "Invocations", "FunctionName", "$LAB_NAME-order-processor", {"stat": "Sum", "period": 60}]
                ],
                "view": "timeSeries",
                "region": "$AWS_REGION"
            }
        },
        {
            "type": "metric",
            "x": 8,
            "y": 1,
            "width": 8,
            "height": 6,
            "properties": {
                "title": "Lambda Duration",
                "metrics": [
                    ["AWS/Lambda", "Duration", "FunctionName", "$LAB_NAME-order-processor", {"stat": "Average", "period": 60}],
                    ["...", {"stat": "p99", "period": 60}]
                ],
                "view": "timeSeries",
                "region": "$AWS_REGION"
            }
        },
        {
            "type": "metric",
            "x": 16,
            "y": 1,
            "width": 8,
            "height": 6,
            "properties": {
                "title": "Lambda Errors",
                "metrics": [
                    ["AWS/Lambda", "Errors", "FunctionName", "$LAB_NAME-order-processor", {"stat": "Sum", "period": 60, "color": "#d62728"}]
                ],
                "view": "timeSeries",
                "region": "$AWS_REGION"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 7,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "DynamoDB Operations",
                "metrics": [
                    ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "$LAB_NAME-orders", {"stat": "Sum", "period": 60}],
                    [".", "ConsumedWriteCapacityUnits", ".", ".", {"stat": "Sum", "period": 60}]
                ],
                "view": "timeSeries",
                "region": "$AWS_REGION"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 7,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "Custom Metrics",
                "metrics": [
                    ["MonitoringLab", "OrderCount", "Environment", "Production", "Service", "OrderProcessor", {"stat": "Sum", "period": 60}],
                    [".", "OrderValue", ".", ".", ".", ".", {"stat": "Average", "period": 60}]
                ],
                "view": "timeSeries",
                "region": "$AWS_REGION"
            }
        },
        {
            "type": "alarm",
            "x": 0,
            "y": 13,
            "width": 12,
            "height": 4,
            "properties": {
                "title": "Alarm Status",
                "alarms": [
                    "arn:aws:cloudwatch:$AWS_REGION:$ACCOUNT_ID:alarm:$LAB_NAME-lambda-errors",
                    "arn:aws:cloudwatch:$AWS_REGION:$ACCOUNT_ID:alarm:$LAB_NAME-lambda-duration",
                    "arn:aws:cloudwatch:$AWS_REGION:$ACCOUNT_ID:alarm:$LAB_NAME-api-5xx-errors"
                ]
            }
        },
        {
            "type": "log",
            "x": 12,
            "y": 13,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "Lambda Error Logs",
                "query": "SOURCE '/aws/lambda/$LAB_NAME-order-processor' | fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20",
                "region": "$AWS_REGION",
                "view": "table"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 17,
            "width": 24,
            "height": 1,
            "properties": {
                "title": "Metric Math: Error Rate (%)",
                "metrics": [
                    [{"expression": "errors/invocations*100", "label": "Error Rate %", "id": "e1"}],
                    ["AWS/Lambda", "Errors", "FunctionName", "$LAB_NAME-order-processor", {"stat": "Sum", "period": 300, "id": "errors", "visible": false}],
                    [".", "Invocations", ".", ".", {"stat": "Sum", "period": 300, "id": "invocations", "visible": false}]
                ],
                "view": "singleValue",
                "region": "$AWS_REGION"
            }
        }
    ]
}
EOF

# Create dashboard
aws cloudwatch put-dashboard \
    --dashboard-name "$LAB_NAME-dashboard" \
    --dashboard-body file:///tmp/dashboard.json

echo "Dashboard created"
echo "View dashboard: https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=$LAB_NAME-dashboard"
```

---

## Part 10: Test the Monitoring Setup

### 10.1 Generate Normal Traffic

```bash
echo "Generating normal traffic..."

for i in {1..30}; do
    curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d '{"action": "create", "product": "Product '$i'", "quantity": '$((RANDOM % 10 + 1))'}' > /dev/null

    echo "Created order $i"
    sleep 2
done
```

### 10.2 Generate Error Traffic

```bash
echo "Generating error traffic..."

for i in {1..5}; do
    curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d '{"action": "simulate_error"}'

    echo "Error request $i"
    sleep 2
done
```

### 10.3 Generate Slow Traffic

```bash
echo "Generating slow traffic..."

for i in {1..3}; do
    echo "Starting slow request $i..."
    curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d '{"action": "simulate_slow"}'
    echo "Completed slow request $i"
done
```

### 10.4 View Results

```bash
echo ""
echo "=========================================="
echo "   Monitoring Lab - Quick Links"
echo "=========================================="
echo ""
echo "Dashboard:"
echo "  https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=$LAB_NAME-dashboard"
echo ""
echo "Alarms:"
echo "  https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#alarmsV2:?~(alarmNamePrefix~'$LAB_NAME)"
echo ""
echo "X-Ray Service Map:"
echo "  https://$AWS_REGION.console.aws.amazon.com/xray/home?region=$AWS_REGION#/service-map"
echo ""
echo "Logs Insights:"
echo "  https://$AWS_REGION.console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:logs-insights"
echo ""
echo "CloudTrail:"
echo "  https://$AWS_REGION.console.aws.amazon.com/cloudtrail/home?region=$AWS_REGION"
echo ""
echo "Config:"
echo "  https://$AWS_REGION.console.aws.amazon.com/config/home?region=$AWS_REGION"
echo ""
echo "API Endpoint: $API_URL"
echo ""
```

---

## Part 11: Troubleshooting Scenarios

### Scenario 1: High Latency Investigation

```bash
# Query for slow Lambda invocations
aws logs start-query \
    --log-group-name /aws/lambda/$LAB_NAME-order-processor \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'filter @type = "REPORT"
        | parse @message "Duration: * ms" as duration
        | filter duration > 2000
        | sort duration desc
        | limit 10'
```

### Scenario 2: Error Pattern Analysis

```bash
# Find error patterns
aws logs start-query \
    --log-group-name /aws/lambda/$LAB_NAME-order-processor \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'filter @message like /ERROR/
        | parse @message "ERROR: *" as errorMessage
        | stats count(*) as count by errorMessage
        | sort count desc'
```

### Scenario 3: Check Alarm States

```bash
# Check all alarm states
aws cloudwatch describe-alarms \
    --alarm-name-prefix $LAB_NAME \
    --query 'MetricAlarms[*].[AlarmName,StateValue,StateReason]' \
    --output table
```

---

## Part 12: Cleanup

**IMPORTANT**: Run this section to avoid ongoing charges.

```bash
echo "Starting cleanup..."

# Delete CloudWatch Dashboard
aws cloudwatch delete-dashboards --dashboard-names $LAB_NAME-dashboard

# Delete CloudWatch Alarms
aws cloudwatch delete-alarms --alarm-names \
    $LAB_NAME-lambda-errors \
    $LAB_NAME-lambda-duration \
    $LAB_NAME-lambda-throttles \
    $LAB_NAME-dynamodb-reads \
    $LAB_NAME-api-5xx-errors \
    $LAB_NAME-custom-errors \
    $LAB_NAME-critical-composite

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id $API_ID

# Delete Lambda function
aws lambda delete-function --function-name $LAB_NAME-order-processor

# Delete DynamoDB table
aws dynamodb delete-table --table-name $LAB_NAME-orders

# Delete X-Ray group
aws xray delete-group --group-name $LAB_NAME-production 2>/dev/null || true

# Delete X-Ray sampling rule
aws xray delete-sampling-rule --rule-name $LAB_NAME-rule 2>/dev/null || true

# Delete Config rules
aws configservice delete-config-rule --config-rule-name $LAB_NAME-lambda-timeout-check
aws configservice delete-config-rule --config-rule-name $LAB_NAME-dynamodb-encryption
aws configservice delete-config-rule --config-rule-name $LAB_NAME-lambda-xray-enabled

# Stop and delete Config recorder
aws configservice stop-configuration-recorder --configuration-recorder-name default
aws configservice delete-delivery-channel --delivery-channel-name default
aws configservice delete-configuration-recorder --configuration-recorder-name default

# Stop and delete CloudTrail
aws cloudtrail stop-logging --name $LAB_NAME-trail
aws cloudtrail delete-trail --name $LAB_NAME-trail

# Delete CloudWatch Log Groups
aws logs delete-log-group --log-group-name /aws/lambda/$LAB_NAME-order-processor 2>/dev/null || true
aws logs delete-log-group --log-group-name /aws/cloudtrail/$LAB_NAME 2>/dev/null || true

# Delete CloudWatch Metric Filters
aws logs delete-metric-filter \
    --log-group-name /aws/cloudtrail/$LAB_NAME \
    --filter-name "$LAB_NAME-root-activity" 2>/dev/null || true
aws logs delete-metric-filter \
    --log-group-name /aws/cloudtrail/$LAB_NAME \
    --filter-name "$LAB_NAME-unauthorized-calls" 2>/dev/null || true

# Delete SNS topic
aws sns delete-topic --topic-arn $TOPIC_ARN

# Delete IAM roles (detach policies first)
aws iam detach-role-policy --role-name $LAB_NAME-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null || true
aws iam detach-role-policy --role-name $LAB_NAME-lambda-role --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess 2>/dev/null || true
aws iam detach-role-policy --role-name $LAB_NAME-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess 2>/dev/null || true
aws iam delete-role --role-name $LAB_NAME-lambda-role 2>/dev/null || true

aws iam delete-role-policy --role-name $LAB_NAME-cloudtrail-cwl-role --policy-name CloudTrailCloudWatchPolicy 2>/dev/null || true
aws iam delete-role --role-name $LAB_NAME-cloudtrail-cwl-role 2>/dev/null || true

aws iam detach-role-policy --role-name $LAB_NAME-config-role --policy-arn arn:aws:iam::aws:policy/service-role/AWS_ConfigRole 2>/dev/null || true
aws iam delete-role --role-name $LAB_NAME-config-role 2>/dev/null || true

# Empty and delete S3 buckets
aws s3 rm s3://$LAB_NAME-lambda-$ACCOUNT_ID --recursive
aws s3 rb s3://$LAB_NAME-lambda-$ACCOUNT_ID

aws s3 rm s3://$LAB_NAME-cloudtrail-$ACCOUNT_ID --recursive
aws s3 rb s3://$LAB_NAME-cloudtrail-$ACCOUNT_ID

aws s3 rm s3://$LAB_NAME-config-$ACCOUNT_ID --recursive
aws s3 rb s3://$LAB_NAME-config-$ACCOUNT_ID

# Clean up temp files
rm -f /tmp/lambda_function.py /tmp/lambda_package.zip /tmp/*.json /tmp/publish_metrics.sh

echo ""
echo "=========================================="
echo "   Cleanup Complete!"
echo "=========================================="
echo ""
echo "All lab resources have been deleted."
echo "Please verify in the AWS Console that all resources are removed."
```

---

## Lab Summary

### What You Learned

1. **Custom Metrics**: Publishing custom application metrics to CloudWatch
2. **Metric Math**: Using expressions to calculate derived metrics
3. **Alarms**: Creating static and composite alarms with SNS actions
4. **X-Ray Tracing**: Instrumenting Lambda functions for distributed tracing
5. **CloudWatch Logs**: Analyzing logs with Logs Insights queries
6. **CloudTrail**: Setting up API logging with CloudWatch integration
7. **AWS Config**: Creating compliance rules for resource configuration
8. **SNS Notifications**: Building alert pipelines with multiple subscribers
9. **Dashboards**: Creating comprehensive operational dashboards

### Key Takeaways

- Monitoring is not optional - it's essential for production workloads
- Use all three pillars: metrics, logs, and traces
- Automate alerting but avoid alert fatigue
- Set up compliance rules before issues occur
- Regular cleanup prevents unnecessary costs

### Next Steps

- Explore CloudWatch Synthetics for availability monitoring
- Set up cross-account monitoring with CloudWatch
- Implement anomaly detection alarms
- Create custom CloudWatch dashboards for your applications
- Integrate with external tools (PagerDuty, Slack, etc.)

---

*Congratulations on completing the Monitoring Lab!*

*Module 08 of the AWS Solutions Architect Training Course*
