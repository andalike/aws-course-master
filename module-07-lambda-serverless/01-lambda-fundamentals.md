# Lambda Fundamentals

## Introduction to AWS Lambda

AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers. You pay only for the compute time you consume - there's no charge when your code isn't running. Lambda automatically scales your application by running code in response to each trigger, from a few requests per day to thousands per second.

## What is AWS Lambda?

### Definition

AWS Lambda is an **event-driven, serverless computing platform** provided by AWS. It executes your code only when needed and scales automatically, from a few requests per day to thousands per second.

### Key Characteristics

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS LAMBDA OVERVIEW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐     │
│   │   EVENT     │ ───▶ │   LAMBDA    │ ───▶ │   OUTPUT    │     │
│   │   SOURCE    │      │   FUNCTION  │      │   (Result)  │     │
│   └─────────────┘      └─────────────┘      └─────────────┘     │
│                              │                                   │
│                              ▼                                   │
│                     ┌─────────────────┐                         │
│                     │  EXECUTION ENV  │                         │
│                     │  • Runtime      │                         │
│                     │  • Memory       │                         │
│                     │  • Timeout      │                         │
│                     │  • Permissions  │                         │
│                     └─────────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Event-Driven Architecture

### Understanding Events

An event is a JSON-formatted document that contains data for a Lambda function to process. Each event source has its own event structure.

### Event Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    EVENT-DRIVEN ARCHITECTURE                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│    EVENT SOURCES              LAMBDA                 TARGETS      │
│                                                                   │
│    ┌──────────┐                                                   │
│    │   S3     │──┐                                                │
│    └──────────┘  │                                                │
│    ┌──────────┐  │         ┌────────────┐        ┌──────────┐    │
│    │   API    │──┼────────▶│   Lambda   │───────▶│ DynamoDB │    │
│    │ Gateway  │  │         │  Function  │        └──────────┘    │
│    └──────────┘  │         └────────────┘        ┌──────────┐    │
│    ┌──────────┐  │              │                │   SNS    │    │
│    │   SQS    │──┤              │                └──────────┘    │
│    └──────────┘  │              │                ┌──────────┐    │
│    ┌──────────┐  │              └───────────────▶│   S3     │    │
│    │  Kinesis │──┘                               └──────────┘    │
│    └──────────┘                                                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Sample Events

#### S3 Event
```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2024-01-15T12:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "bucket": {
          "name": "my-bucket",
          "arn": "arn:aws:s3:::my-bucket"
        },
        "object": {
          "key": "uploads/image.jpg",
          "size": 1024,
          "eTag": "abc123"
        }
      }
    }
  ]
}
```

#### API Gateway Event
```json
{
  "resource": "/users/{id}",
  "path": "/users/123",
  "httpMethod": "GET",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token123"
  },
  "queryStringParameters": {
    "filter": "active"
  },
  "pathParameters": {
    "id": "123"
  },
  "body": null,
  "requestContext": {
    "accountId": "123456789012",
    "stage": "prod",
    "requestId": "abc-123"
  }
}
```

#### SQS Event
```json
{
  "Records": [
    {
      "messageId": "msg-001",
      "receiptHandle": "handle123",
      "body": "{\"orderId\": \"ORD-001\", \"amount\": 99.99}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "1642329600000"
      },
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:my-queue"
    }
  ]
}
```

## Lambda Invocation Types

Lambda supports three invocation models, each suited for different use cases.

### 1. Synchronous Invocation

The caller waits for the function to process the event and return a response.

```
┌──────────┐     Request      ┌──────────┐
│  Client  │─────────────────▶│  Lambda  │
│          │◀─────────────────│          │
└──────────┘     Response     └──────────┘
         Caller waits for response
```

**Characteristics:**
- Caller waits for response
- Errors returned directly to caller
- No automatic retry

**Services using synchronous invocation:**
- Amazon API Gateway
- Amazon Cognito
- Application Load Balancer
- Lambda Function URLs
- Amazon Alexa

**Example: Synchronous call with AWS CLI**
```bash
aws lambda invoke \
    --function-name my-function \
    --payload '{"key": "value"}' \
    --cli-binary-format raw-in-base64-out \
    response.json
```

### 2. Asynchronous Invocation

Lambda queues the event for processing and returns immediately.

```
┌──────────┐     Request      ┌───────────┐      ┌──────────┐
│  Client  │─────────────────▶│  Lambda   │─────▶│  Lambda  │
│          │◀──────────────── │  Queue    │      │ Function │
└──────────┘  Immediate ACK   └───────────┘      └──────────┘
                                   │
                                   ▼
                            (Retry on failure)
```

**Characteristics:**
- Caller receives immediate acknowledgment
- Built-in retry (2 retries by default)
- Can configure Dead Letter Queue (DLQ)
- Can configure destinations for success/failure

**Services using asynchronous invocation:**
- Amazon S3
- Amazon SNS
- Amazon EventBridge
- Amazon CloudWatch Logs
- AWS CodeCommit

**Example: Asynchronous call with AWS CLI**
```bash
aws lambda invoke \
    --function-name my-function \
    --invocation-type Event \
    --payload '{"key": "value"}' \
    --cli-binary-format raw-in-base64-out \
    response.json
```

**Configuring retry behavior:**
```bash
aws lambda put-function-event-invoke-config \
    --function-name my-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600
```

### 3. Poll-Based Invocation (Event Source Mapping)

Lambda polls the source and invokes the function with batches of records.

```
┌───────────┐                  ┌────────────┐      ┌──────────┐
│   SQS/    │◀─────────────────│   Lambda   │─────▶│  Lambda  │
│  Kinesis/ │   Lambda Polls   │   Poller   │      │ Function │
│  DynamoDB │─────────────────▶│            │      │ (Batch)  │
└───────────┘                  └────────────┘      └──────────┘
```

**Characteristics:**
- Lambda service polls the stream/queue
- Invokes function with batches of records
- Manages checkpointing and retry
- Scales based on source throughput

**Services using poll-based invocation:**
- Amazon SQS
- Amazon Kinesis Data Streams
- Amazon DynamoDB Streams
- Amazon MQ
- Amazon MSK (Kafka)

**Creating an event source mapping:**
```bash
aws lambda create-event-source-mapping \
    --function-name my-function \
    --event-source-arn arn:aws:sqs:us-east-1:123456789012:my-queue \
    --batch-size 10
```

### Invocation Types Comparison

| Aspect | Synchronous | Asynchronous | Poll-Based |
|--------|-------------|--------------|------------|
| Response | Waits for response | Immediate ACK | N/A |
| Retry | Caller handles | 2 automatic retries | Depends on source |
| Error Handling | Return to caller | DLQ/Destinations | DLQ/Source retry |
| Use Case | API calls | Event processing | Stream processing |
| Scaling | Caller controls | Lambda controls | Source-based |

## Cold Starts and Execution Environment

### Understanding the Execution Environment

When Lambda executes a function for the first time (or after scaling), it creates a new execution environment.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAMBDA EXECUTION ENVIRONMENT                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    INITIALIZATION                          │  │
│  │  1. Download code                                         │  │
│  │  2. Create execution environment                          │  │
│  │  3. Initialize runtime                                    │  │
│  │  4. Run initialization code (outside handler)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    INVOCATION                              │  │
│  │  1. Invoke handler function                               │  │
│  │  2. Process event                                         │  │
│  │  3. Return response                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    ENVIRONMENT REUSE                       │  │
│  │  • Environment may be reused for subsequent invocations   │  │
│  │  • Variables persist between invocations                  │  │
│  │  • Connections can be reused                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cold Start vs Warm Start

#### Cold Start

A cold start occurs when Lambda needs to create a new execution environment:

```
┌──────────────────────────────────────────────────────────────────┐
│                         COLD START                                │
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │Download │─▶│ Create  │─▶│  Init   │─▶│  Init   │─▶│ Invoke │ │
│  │  Code   │  │  Env    │  │ Runtime │  │  Code   │  │Handler │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └────────┘ │
│                                                                   │
│  ◀──────────── Cold Start Duration ─────────────▶│◀── Exec ──▶│ │
│     (100ms - several seconds)                        (billed)    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Cold start happens when:**
- First invocation of a function
- Lambda scales out to handle increased load
- Function hasn't been invoked for a while
- After a code update or configuration change

#### Warm Start

A warm start reuses an existing execution environment:

```
┌──────────────────────────────────────────────────────────────────┐
│                         WARM START                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────┐  ┌────────┐ │
│  │      Existing Execution Environment              │  │ Invoke │ │
│  │      (Already initialized)                       │─▶│Handler │ │
│  └─────────────────────────────────────────────────┘  └────────┘ │
│                                                                   │
│                                                      │◀── Exec ──▶│
│                                                         (billed)  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Cold Start Factors

| Factor | Impact on Cold Start |
|--------|---------------------|
| **Runtime** | Java/C# > Python/Node.js |
| **Package Size** | Larger = Longer |
| **Memory** | More memory = Faster initialization |
| **VPC** | VPC adds ~1 second |
| **Dependencies** | More dependencies = Longer |
| **Initialization Code** | Complex init = Longer |

### Cold Start Duration by Runtime

| Runtime | Typical Cold Start |
|---------|-------------------|
| Python | 100-300ms |
| Node.js | 100-300ms |
| Go | 50-100ms |
| Java | 500ms-5s |
| .NET | 500ms-3s |

### Mitigating Cold Starts

#### 1. Provisioned Concurrency

Keep a specified number of execution environments initialized and ready.

```bash
aws lambda put-provisioned-concurrency-config \
    --function-name my-function \
    --qualifier prod \
    --provisioned-concurrent-executions 10
```

#### 2. Keep Functions Warm

Use CloudWatch Events to invoke functions periodically:

```yaml
# SAM template
WarmingRule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: rate(5 minutes)
    Targets:
      - Arn: !GetAtt MyFunction.Arn
        Id: WarmingTarget
        Input: '{"warm": true}'
```

#### 3. Optimize Package Size

```python
# Before: Large package with unused dependencies
# requirements.txt
boto3
pandas
numpy
scikit-learn

# After: Minimal dependencies
# requirements.txt
boto3  # Already included in Lambda runtime
```

#### 4. Initialize Outside Handler

```python
import boto3
import json

# Initialize OUTSIDE handler - reused in warm starts
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

def handler(event, context):
    # Handler code - runs every invocation
    response = table.get_item(Key={'id': event['id']})
    return response['Item']
```

## Lambda Execution Lifecycle

### Phase 1: Init

```python
import boto3
import os

# INIT PHASE - Runs once per execution environment
# - Import modules
# - Initialize SDK clients
# - Read environment variables
# - Establish database connections

# These are executed during INIT
db_client = boto3.client('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
connection = None  # Placeholder for DB connection

def get_connection():
    global connection
    if connection is None:
        connection = create_database_connection()
    return connection
```

### Phase 2: Invoke

```python
def handler(event, context):
    """
    INVOKE PHASE - Runs for each invocation

    Args:
        event: Event data (dict)
        context: Runtime information (LambdaContext)

    Returns:
        Response data
    """
    # Get reused connection from INIT phase
    conn = get_connection()

    # Process the event
    result = process_event(event, conn)

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### Phase 3: Shutdown

```python
# SHUTDOWN PHASE - Lambda may send SIGTERM
# - Clean up resources
# - Flush logs/metrics
# - Close connections gracefully

import signal

def shutdown_handler(signum, frame):
    """Handle graceful shutdown"""
    print("Received shutdown signal, cleaning up...")
    if connection:
        connection.close()

signal.signal(signal.SIGTERM, shutdown_handler)
```

## Lambda Context Object

The context object provides runtime information about the invocation and environment.

### Python Context

```python
def handler(event, context):
    # Function name
    print(f"Function: {context.function_name}")

    # Memory allocated
    print(f"Memory: {context.memory_limit_in_mb} MB")

    # Request ID (unique per invocation)
    print(f"Request ID: {context.aws_request_id}")

    # Time remaining before timeout
    remaining_ms = context.get_remaining_time_in_millis()
    print(f"Time remaining: {remaining_ms} ms")

    # Log group and stream
    print(f"Log Group: {context.log_group_name}")
    print(f"Log Stream: {context.log_stream_name}")

    # Function ARN
    print(f"ARN: {context.invoked_function_arn}")
```

### Node.js Context

```javascript
exports.handler = async (event, context) => {
    // Function name
    console.log(`Function: ${context.functionName}`);

    // Memory allocated
    console.log(`Memory: ${context.memoryLimitInMB} MB`);

    // Request ID
    console.log(`Request ID: ${context.awsRequestId}`);

    // Time remaining
    const remaining = context.getRemainingTimeInMillis();
    console.log(`Time remaining: ${remaining} ms`);

    // Log group and stream
    console.log(`Log Group: ${context.logGroupName}`);
    console.log(`Log Stream: ${context.logStreamName}`);

    return { statusCode: 200, body: 'Success' };
};
```

## Lambda Limits and Quotas

### Resource Limits

| Resource | Limit |
|----------|-------|
| Memory | 128 MB - 10,240 MB |
| Timeout | 1 second - 15 minutes |
| Environment Variables | 4 KB total |
| Deployment Package (zipped) | 50 MB |
| Deployment Package (unzipped) | 250 MB |
| /tmp Storage | 512 MB - 10,240 MB |
| Layers | 5 layers per function |
| Concurrent Executions | 1,000 (default, can be increased) |

### Deployment Limits

| Resource | Limit |
|----------|-------|
| Function Code (Console) | 3 MB |
| Function Code (S3) | 50 MB (zipped) |
| Container Image | 10 GB |
| Layers (total unzipped) | 250 MB |

### Invocation Limits

| Resource | Limit |
|----------|-------|
| Request/Response Payload (Sync) | 6 MB |
| Request Payload (Async) | 256 KB |
| Invocation Frequency (per region) | 10x concurrent execution limit |

## Lambda Pricing

### Pricing Components

1. **Number of Requests**
   - First 1 million requests per month: FREE
   - $0.20 per 1 million requests thereafter

2. **Duration (GB-seconds)**
   - First 400,000 GB-seconds per month: FREE
   - $0.0000166667 per GB-second thereafter

### Pricing Examples

#### Example 1: Simple API

```
Configuration:
- Memory: 256 MB (0.25 GB)
- Average duration: 200 ms
- Requests per month: 3 million

Calculation:
- GB-seconds = 3,000,000 * 0.25 * 0.2 = 150,000 GB-seconds
- Free tier covers this (400,000 free)
- Request cost = (3,000,000 - 1,000,000) * $0.20/1M = $0.40

Total Monthly Cost: $0.40
```

#### Example 2: Data Processing

```
Configuration:
- Memory: 1024 MB (1 GB)
- Average duration: 30 seconds
- Requests per month: 100,000

Calculation:
- GB-seconds = 100,000 * 1 * 30 = 3,000,000 GB-seconds
- Billable = 3,000,000 - 400,000 = 2,600,000 GB-seconds
- Duration cost = 2,600,000 * $0.0000166667 = $43.33
- Request cost = 0 (under 1M free)

Total Monthly Cost: $43.33
```

## Lambda vs Other Compute Options

### Comparison Matrix

| Feature | Lambda | EC2 | Fargate | ECS |
|---------|--------|-----|---------|-----|
| Server Management | None | Full | Container only | Container only |
| Scaling | Automatic | Manual/ASG | Automatic | Automatic |
| Billing | Per ms | Per hour | Per second | Per second |
| Max Duration | 15 min | Unlimited | Unlimited | Unlimited |
| Cold Start | Yes | No | Yes | Yes |
| State | Stateless | Stateful | Stateful | Stateful |

### When to Use Lambda

**Good fit for:**
- Event-driven processing
- APIs with variable traffic
- Scheduled tasks (cron jobs)
- File processing
- Real-time stream processing
- Microservices

**Not ideal for:**
- Long-running processes (>15 min)
- Applications requiring persistent state
- High-performance computing
- Applications needing GPU
- Legacy applications requiring specific OS

## Summary

### Key Takeaways

1. **Lambda is event-driven**: Functions are triggered by events from AWS services
2. **Three invocation types**: Synchronous, asynchronous, and poll-based
3. **Cold starts matter**: Understand and mitigate for latency-sensitive applications
4. **Pay per use**: Only charged for actual execution time
5. **Automatic scaling**: Lambda handles scaling automatically

### Next Steps

Continue to [02-creating-functions.md](./02-creating-functions.md) to learn how to create and deploy Lambda functions using the console, CLI, and SAM.
