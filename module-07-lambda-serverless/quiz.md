# Module 7: Lambda & Serverless - Quiz

## Overview

This comprehensive quiz covers all topics from Module 7, including Lambda fundamentals, API Gateway, Step Functions, and serverless architecture concepts. Test your knowledge with 30 questions ranging from basic to advanced.

---

## Section 1: Lambda Fundamentals (Questions 1-8)

### Question 1: Lambda Pricing Model

What are the two main components of AWS Lambda pricing?

A) CPU usage and storage
B) Number of requests and compute duration (GB-seconds)
C) Network bandwidth and memory allocation
D) Instance hours and data transfer

<details>
<summary>Answer</summary>

**B) Number of requests and compute duration (GB-seconds)**

**Explanation:** AWS Lambda pricing consists of:
1. **Requests**: $0.20 per 1 million requests (first 1 million free per month)
2. **Duration**: $0.0000166667 per GB-second (first 400,000 GB-seconds free per month)

GB-seconds is calculated as: `Memory allocated (GB) x Execution time (seconds)`

Example: A function with 512 MB memory running for 1 second = 0.5 GB-seconds
</details>

---

### Question 2: Lambda Memory Configuration

What is the relationship between Lambda memory and CPU allocation?

A) Memory and CPU are configured independently
B) CPU allocation increases proportionally with memory
C) CPU is always the same regardless of memory
D) CPU allocation decreases as memory increases

<details>
<summary>Answer</summary>

**B) CPU allocation increases proportionally with memory**

**Explanation:** In AWS Lambda, you only directly configure memory (128 MB to 10,240 MB). CPU power is allocated proportionally:
- At 1,769 MB, you get the equivalent of one full vCPU
- At 3,538 MB, you get two vCPUs
- At 10,240 MB, you get six vCPUs

This means increasing memory also increases compute power, which can improve performance for CPU-bound workloads.
</details>

---

### Question 3: Lambda Timeout

What is the maximum timeout you can configure for an AWS Lambda function?

A) 5 minutes
B) 10 minutes
C) 15 minutes
D) 30 minutes

<details>
<summary>Answer</summary>

**C) 15 minutes**

**Explanation:** The maximum timeout for a Lambda function is 15 minutes (900 seconds). The minimum is 1 second. If your workload requires more than 15 minutes, consider:
- Breaking it into smaller functions orchestrated by Step Functions
- Using AWS Fargate or EC2 for longer-running processes
- Processing data in chunks with SQS
</details>

---

### Question 4: Cold Starts

Which factor has the LEAST impact on Lambda cold start duration?

A) Runtime selection (Java vs Python)
B) Memory allocation
C) Function timeout setting
D) Deployment package size

<details>
<summary>Answer</summary>

**C) Function timeout setting**

**Explanation:** Function timeout does NOT affect cold start duration. Factors that DO impact cold starts:
- **Runtime**: Java/.NET have longer cold starts (500ms-5s) vs Python/Node.js (100-300ms)
- **Memory**: Higher memory = faster initialization
- **Package size**: Larger packages take longer to download and decompress
- **VPC configuration**: Adds ~1 second for ENI attachment
- **Initialization code**: More dependencies = longer init time

Timeout only affects how long the function can run, not how quickly it starts.
</details>

---

### Question 5: Provisioned Concurrency

What problem does Provisioned Concurrency solve?

A) Reduces Lambda function costs
B) Eliminates cold starts for specified capacity
C) Increases the maximum concurrent executions
D) Allows functions to run longer than 15 minutes

<details>
<summary>Answer</summary>

**B) Eliminates cold starts for specified capacity**

**Explanation:** Provisioned Concurrency keeps a specified number of execution environments initialized and ready to respond immediately. Key points:
- You specify how many pre-initialized environments to maintain
- Requests up to that number experience no cold start latency
- You pay for the provisioned capacity whether it's used or not
- Best for latency-sensitive applications with predictable traffic

Note: Provisioned Concurrency has additional cost beyond regular Lambda pricing.
</details>

---

### Question 6: Lambda Invocation Types

A Lambda function is triggered by an S3 bucket when a new object is uploaded. What invocation type is this?

A) Synchronous
B) Asynchronous
C) Poll-based (Event Source Mapping)
D) Direct invocation

<details>
<summary>Answer</summary>

**B) Asynchronous**

**Explanation:** S3 events invoke Lambda asynchronously:
- S3 sends the event to Lambda and receives an immediate acknowledgment
- Lambda queues the event and processes it when ready
- Built-in retry: 2 automatic retries on failure
- Can configure DLQ or destinations for failed events

**Asynchronous sources include:** S3, SNS, EventBridge, CloudWatch Logs, CodeCommit
**Synchronous sources include:** API Gateway, ALB, Cognito, Lambda Function URLs
**Poll-based sources include:** SQS, Kinesis, DynamoDB Streams, Kafka
</details>

---

### Question 7: Lambda Layers

What is the maximum number of layers a single Lambda function can use?

A) 3 layers
B) 5 layers
C) 10 layers
D) Unlimited

<details>
<summary>Answer</summary>

**B) 5 layers**

**Explanation:** Lambda functions can have a maximum of 5 layers attached. Important layer limits:
- **Maximum 5 layers** per function
- **Total unzipped size** (function + all layers) cannot exceed 250 MB
- Layer versions are immutable once published
- Layers are extracted to `/opt` directory at runtime

Best practices for layers:
- Use for shared libraries and dependencies
- Keep frequently changing code in the function, not layers
- Version layers for controlled updates
</details>

---

### Question 8: Lambda Resource Limits

Which of the following is NOT a valid AWS Lambda limit?

A) 50 MB deployment package (zipped)
B) 10 GB container image size
C) 512 MB /tmp storage minimum
D) 20,000 concurrent executions default

<details>
<summary>Answer</summary>

**D) 20,000 concurrent executions default**

**Explanation:** The default concurrent execution limit is 1,000 per region, not 20,000. Correct limits:
- **Deployment package (zipped)**: 50 MB
- **Deployment package (unzipped)**: 250 MB
- **Container image**: 10 GB
- **/tmp storage**: 512 MB to 10,240 MB
- **Default concurrent executions**: 1,000 per region (can request increase)
- **Request payload (sync)**: 6 MB
- **Request payload (async)**: 256 KB
</details>

---

## Section 2: Lambda Triggers and Destinations (Questions 9-13)

### Question 9: Event Source Mapping

Which service requires Lambda to poll for messages using Event Source Mapping?

A) S3
B) API Gateway
C) SQS
D) SNS

<details>
<summary>Answer</summary>

**C) SQS**

**Explanation:** Event Source Mapping (poll-based invocation) is used for streaming and queue services where Lambda needs to actively poll for records:
- **Amazon SQS** (Standard and FIFO)
- **Amazon Kinesis Data Streams**
- **Amazon DynamoDB Streams**
- **Amazon MQ**
- **Amazon MSK (Kafka)**
- **Self-managed Apache Kafka**

S3 and SNS use asynchronous invocation (they push events to Lambda).
API Gateway uses synchronous invocation (waits for response).
</details>

---

### Question 10: SQS Batch Processing

When processing SQS messages with Lambda, a batch of 10 messages is received. If processing fails for only 2 messages, what happens by default?

A) Only the 2 failed messages are retried
B) All 10 messages are returned to the queue and retried
C) The 2 failed messages are sent to the DLQ
D) Lambda automatically retries only the failed messages

<details>
<summary>Answer</summary>

**B) All 10 messages are returned to the queue and retried**

**Explanation:** By default, if any message in a batch fails, the entire batch is considered failed. All messages become visible again after the visibility timeout.

To handle partial failures, enable **Report Batch Item Failures**:
```python
def handler(event, context):
    failed_items = []
    for record in event['Records']:
        try:
            process(record)
        except Exception:
            failed_items.append({
                'itemIdentifier': record['messageId']
            })
    return {'batchItemFailures': failed_items}
```

With this enabled, only failed messages are retried.
</details>

---

### Question 11: Lambda Destinations

Which invocation type supports Lambda Destinations?

A) Synchronous invocation only
B) Asynchronous invocation only
C) Both synchronous and asynchronous
D) Neither - Destinations work with all invocation types

<details>
<summary>Answer</summary>

**B) Asynchronous invocation only**

**Explanation:** Lambda Destinations are available only for asynchronous invocations. You can configure destinations for:
- **On Success**: SNS, SQS, Lambda, or EventBridge
- **On Failure**: SNS, SQS, Lambda, or EventBridge

Destinations are preferred over Dead Letter Queues (DLQ) because:
- They support both success and failure scenarios
- They include function execution context
- They support more target types (EventBridge, Lambda)

DLQs only capture failures and only support SNS or SQS.
</details>

---

### Question 12: Kinesis Stream Processing

When processing Kinesis streams, how does Lambda handle failed records?

A) Skips the failed record and continues
B) Blocks the shard until the record succeeds or expires
C) Sends failed records to a DLQ immediately
D) Retries the entire batch indefinitely

<details>
<summary>Answer</summary>

**B) Blocks the shard until the record succeeds or expires**

**Explanation:** Lambda processes Kinesis records in order per shard. When a record fails:
1. Lambda retries the entire batch
2. Processing of subsequent records in that shard is blocked
3. Continues until success, record expiration, or max retries

To prevent blocking, configure:
- **Bisect batch on function error**: Splits batch to isolate bad record
- **Maximum retry attempts**: Limits retries (default unlimited)
- **Maximum record age**: Skips records older than threshold
- **On-failure destination**: Sends failed records to SQS/SNS

These settings prevent a single bad record from blocking the entire shard indefinitely.
</details>

---

### Question 13: DynamoDB Streams

You want to trigger a Lambda function whenever a specific item attribute changes in DynamoDB. What should you configure?

A) DynamoDB Streams with KEYS_ONLY view
B) DynamoDB Streams with NEW_IMAGE view
C) DynamoDB Streams with NEW_AND_OLD_IMAGES view
D) Direct DynamoDB to Lambda integration

<details>
<summary>Answer</summary>

**C) DynamoDB Streams with NEW_AND_OLD_IMAGES view**

**Explanation:** To detect attribute changes, you need both the old and new values:

| Stream View Type | Description |
|-----------------|-------------|
| KEYS_ONLY | Only partition/sort keys |
| NEW_IMAGE | New item state after modification |
| OLD_IMAGE | Old item state before modification |
| NEW_AND_OLD_IMAGES | Both old and new states |

With NEW_AND_OLD_IMAGES, you can compare:
```python
def handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            old = record['dynamodb']['OldImage']
            new = record['dynamodb']['NewImage']
            if old['status'] != new['status']:
                # Status changed - process
                pass
```
</details>

---

## Section 3: API Gateway (Questions 14-19)

### Question 14: API Gateway Types

Which API Gateway type is approximately 70% cheaper than REST API and is recommended for simple Lambda proxy integrations?

A) WebSocket API
B) HTTP API
C) REST API with caching disabled
D) Private REST API

<details>
<summary>Answer</summary>

**B) HTTP API**

**Explanation:** HTTP API is designed for simple use cases and offers:
- **~70% lower cost** than REST API
- **Lower latency** (single-digit milliseconds)
- **Simpler configuration**
- **Built-in JWT/OIDC authorization**
- **Native CORS support**

However, HTTP API lacks some REST API features:
- API caching
- Request/response transformation
- API keys and usage plans
- Request validation
- WAF integration

Choose HTTP API for cost-effective Lambda proxies; REST API for full feature set.
</details>

---

### Question 15: Lambda Proxy Integration Response

When using Lambda proxy integration with API Gateway REST API, what format must the Lambda function return?

A) Any JSON object
B) Raw string or binary data
C) Object with statusCode, headers, and body
D) Object with only body field

<details>
<summary>Answer</summary>

**C) Object with statusCode, headers, and body**

**Explanation:** Lambda proxy integration requires a specific response format:

```python
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'message': 'Success'}),
        'isBase64Encoded': False  # Optional
    }
```

Required fields:
- **statusCode**: HTTP status code (integer)
- **body**: Response body (must be string, use json.dumps for objects)

Optional fields:
- **headers**: Response headers
- **isBase64Encoded**: True if body is base64 encoded
- **multiValueHeaders**: Headers with multiple values
</details>

---

### Question 16: API Gateway Throttling

API Gateway throttling limits are configured at multiple levels. What is the correct hierarchy from highest to lowest priority?

A) Account > API > Stage > Method
B) Method > Stage > API > Account
C) Stage > Method > API > Account
D) API > Account > Stage > Method

<details>
<summary>Answer</summary>

**A) Account > API > Stage > Method**

**Explanation:** Throttling limits cascade from account level down:

```
Account Level (10,000 RPS default)
    └── Usage Plan Level
        └── API/Stage Level
            └── Method Level (most specific)
```

The most restrictive limit at any level applies. For example:
- Account: 10,000 RPS
- Usage Plan: 1,000 RPS for specific API key
- Stage: 500 RPS
- Method GET /users: 100 RPS

A request to GET /users would be limited to 100 RPS (method level, most restrictive applicable limit).
</details>

---

### Question 17: API Gateway Caching

Which API Gateway type supports response caching?

A) HTTP API only
B) REST API only
C) WebSocket API only
D) Both HTTP API and REST API

<details>
<summary>Answer</summary>

**B) REST API only**

**Explanation:** Response caching is only available in REST API:

| Feature | REST API | HTTP API | WebSocket |
|---------|----------|----------|-----------|
| Caching | Yes | No | No |
| Cache sizes | 0.5-237 GB | N/A | N/A |
| TTL | 0-3600 seconds | N/A | N/A |
| Per-method config | Yes | N/A | N/A |

Caching configuration:
- Enable at stage level
- Configure TTL per method
- Define cache key parameters (query strings, headers)
- Cache encryption available
- Invalidation via headers or console
</details>

---

### Question 18: WebSocket API

In a WebSocket API, what route handles messages that don't match any defined custom routes?

A) $connect
B) $disconnect
C) $default
D) $fallback

<details>
<summary>Answer</summary>

**C) $default**

**Explanation:** WebSocket API has three special routes:

| Route | Purpose |
|-------|---------|
| `$connect` | Client establishes connection |
| `$disconnect` | Client disconnects (or times out) |
| `$default` | Fallback for unmatched message routes |

Custom routes are matched based on `routeSelectionExpression`, typically `$request.body.action`:

```json
// Message with action="sendMessage" routes to "sendMessage" route
{"action": "sendMessage", "data": "Hello"}

// Message with unknown/missing action routes to $default
{"data": "Hello"}
```

$default is optional but recommended for handling unexpected messages gracefully.
</details>

---

### Question 19: Lambda Authorizer

What can a Lambda authorizer return to allow API Gateway to cache authorization decisions?

A) A boolean value
B) An IAM policy document with a principal ID
C) A JWT token
D) An HTTP status code

<details>
<summary>Answer</summary>

**B) An IAM policy document with a principal ID**

**Explanation:** Lambda authorizers must return a policy document:

```python
def authorizer(event, context):
    # Validate token...
    return {
        'principalId': 'user123',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': 'Allow',  # or 'Deny'
                'Resource': event['methodArn']
            }]
        },
        'context': {  # Optional - passed to backend
            'userId': 'user123',
            'email': 'user@example.com'
        }
    }
```

Caching:
- Configure TTL (0-3600 seconds)
- Cache key: Authorization token (token authorizer) or request parameters (request authorizer)
- Reduces Lambda invocations and latency
</details>

---

## Section 4: Step Functions (Questions 20-24)

### Question 20: Workflow Types

A high-volume data processing pipeline needs to process 100,000 events per second with workflows completing in under 30 seconds. Which Step Functions workflow type should you use?

A) Standard workflow with high concurrency
B) Express workflow (synchronous)
C) Express workflow (asynchronous)
D) Standard workflow is the only option

<details>
<summary>Answer</summary>

**C) Express workflow (asynchronous)**

**Explanation:** Express workflows are designed for high-volume, short-duration workloads:

| Feature | Standard | Express |
|---------|----------|---------|
| Max duration | 1 year | 5 minutes |
| Execution rate | 2,000/sec | 100,000/sec |
| State transitions | 25,000/execution | Unlimited |
| Execution semantics | Exactly-once | At-least-once (async) |
| Pricing | Per transition | Per execution/duration |

For 100,000 events/sec completing in 30 seconds, Express (async) is ideal:
- Handles high throughput
- At-least-once is acceptable for most data processing
- Cost-effective for short durations
</details>

---

### Question 21: Map State

What is the purpose of the Map state in Step Functions?

A) Transform the structure of input data
B) Create a visual map of the state machine
C) Iterate over an array and process each item
D) Route to different states based on conditions

<details>
<summary>Answer</summary>

**C) Iterate over an array and process each item**

**Explanation:** The Map state iterates over an array and runs a set of steps for each element:

```json
{
  "ProcessItems": {
    "Type": "Map",
    "ItemsPath": "$.orders",
    "MaxConcurrency": 10,
    "ItemProcessor": {
      "StartAt": "ProcessOrder",
      "States": {
        "ProcessOrder": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:...:function:process",
          "End": true
        }
      }
    },
    "Next": "Complete"
  }
}
```

Key features:
- **ItemsPath**: JSONPath to array
- **MaxConcurrency**: Parallel processing limit (0 = unlimited)
- **ItemProcessor**: Steps to run for each item
- Results are collected into an array
</details>

---

### Question 22: Error Handling

In Step Functions, what is the correct order of error handling evaluation?

A) Catch, then Retry
B) Retry, then Catch
C) Catch and Retry are evaluated simultaneously
D) Only one can be configured per state

<details>
<summary>Answer</summary>

**B) Retry, then Catch**

**Explanation:** Error handling order:
1. **Retry**: Attempt retries based on configuration
2. **Catch**: If retries exhausted or error not in Retry, evaluate Catch

```json
{
  "ProcessOrder": {
    "Type": "Task",
    "Resource": "...",
    "Retry": [
      {
        "ErrorEquals": ["ServiceException"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }
    ],
    "Catch": [
      {
        "ErrorEquals": ["States.ALL"],
        "ResultPath": "$.error",
        "Next": "HandleError"
      }
    ]
  }
}
```

Flow: Error occurs -> Check Retry rules -> Retry if matched -> After max retries or unmatched -> Check Catch rules -> Transition to error handler
</details>

---

### Question 23: Service Integrations

Which Step Functions service integration pattern waits for an external process to call back with a task token?

A) Request-Response
B) Run a Job (.sync)
C) Wait for Callback (.waitForTaskToken)
D) Optimized Integration

<details>
<summary>Answer</summary>

**C) Wait for Callback (.waitForTaskToken)**

**Explanation:** Three integration patterns:

1. **Request-Response** (default): Call service and continue
   ```json
   "Resource": "arn:aws:states:::sqs:sendMessage"
   ```

2. **Run a Job (.sync)**: Wait for job to complete
   ```json
   "Resource": "arn:aws:states:::glue:startJobRun.sync"
   ```

3. **Wait for Callback (.waitForTaskToken)**: Pause until callback
   ```json
   "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
   "Parameters": {
     "MessageBody": {
       "taskToken.$": "$$.Task.Token"
     }
   }
   ```

Use `.waitForTaskToken` for human approvals, external systems, or async processes that need to signal completion.
</details>

---

### Question 24: Input/Output Processing

In the following order, how does Step Functions process input and output?

A) InputPath -> Parameters -> Task -> ResultSelector -> ResultPath -> OutputPath
B) Parameters -> InputPath -> Task -> ResultPath -> ResultSelector -> OutputPath
C) InputPath -> Task -> Parameters -> ResultPath -> OutputPath
D) Parameters -> Task -> ResultSelector -> InputPath -> OutputPath

<details>
<summary>Answer</summary>

**A) InputPath -> Parameters -> Task -> ResultSelector -> ResultPath -> OutputPath**

**Explanation:** The input/output processing flow:

```
State Input
    |
    v
InputPath     -> Select subset of input
    |
    v
Parameters    -> Construct task input, add values
    |
    v
Task          -> Execute the task
    |
    v
ResultSelector -> Transform task result
    |
    v
ResultPath    -> Merge result with original input
    |
    v
OutputPath    -> Select subset for output
    |
    v
State Output
```

Example:
- InputPath: `$.order` - Extract order from input
- Parameters: Add metadata, format for API
- ResultSelector: Extract specific fields from result
- ResultPath: `$.orderResult` - Store result in original input
- OutputPath: `$` - Pass entire merged object
</details>

---

## Section 5: Advanced Concepts (Questions 25-30)

### Question 25: Lambda Execution Context Reuse

Which of the following persists between invocations in a warm Lambda execution environment?

A) Variables declared inside the handler function
B) Global variables and objects initialized outside the handler
C) The event object from the previous invocation
D) Local file system in /tmp directory only

<details>
<summary>Answer</summary>

**B) Global variables and objects initialized outside the handler**

**Explanation:** In warm starts, the execution environment is reused:

**Persists (reused):**
- Global variables and imports
- Objects instantiated outside handler
- Database connections
- SDK clients
- Files in /tmp

**Does NOT persist:**
- Variables inside handler (recreated each invocation)
- Event/context objects (new each invocation)

Best practice - initialize outside handler:
```python
import boto3

# Persists between invocations (INIT phase)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

def handler(event, context):
    # Runs every invocation
    return table.get_item(Key={'id': event['id']})
```
</details>

---

### Question 26: VPC Configuration

What additional latency component is introduced when a Lambda function is configured with VPC access?

A) DNS resolution time
B) Elastic Network Interface (ENI) attachment
C) Security group evaluation
D) NAT Gateway processing

<details>
<summary>Answer</summary>

**B) Elastic Network Interface (ENI) attachment**

**Explanation:** VPC-enabled Lambda functions historically had significant cold start overhead due to ENI creation. AWS improved this with Hyperplane ENIs:

**Before (legacy):**
- ENI created per execution environment
- Added 10-30 seconds to cold start

**After (current - Hyperplane):**
- ENIs pre-provisioned and shared
- Adds ~1 second to cold start
- ENI attachment still required but much faster

VPC configuration requirements:
- Subnet IDs (private recommended)
- Security group IDs
- Lambda execution role needs `ec2:CreateNetworkInterface` etc.

For internet access from VPC Lambda, need NAT Gateway in public subnet.
</details>

---

### Question 27: Reserved Concurrency

What happens when you set Reserved Concurrency to 0 for a Lambda function?

A) The function runs with unlimited concurrency
B) The function is throttled (cannot be invoked)
C) The function uses the account's unreserved concurrency
D) An error is thrown and the configuration fails

<details>
<summary>Answer</summary>

**B) The function is throttled (cannot be invoked)**

**Explanation:** Reserved Concurrency has two purposes:

1. **Guarantee capacity**: Reserve concurrent executions for the function
2. **Throttle function**: Set to 0 to prevent invocations

```bash
# Throttle function (set to 0)
aws lambda put-function-concurrency \
    --function-name my-function \
    --reserved-concurrent-executions 0

# Reserve 100 concurrent executions
aws lambda put-function-concurrency \
    --function-name my-function \
    --reserved-concurrent-executions 100
```

Use cases for setting to 0:
- Temporarily disable function during maintenance
- Prevent costs during development
- Stop runaway functions

Note: Reserved concurrency is taken from account pool (1000 default).
</details>

---

### Question 28: Lambda Container Images

What is the maximum size for a Lambda container image?

A) 250 MB
B) 1 GB
C) 10 GB
D) 50 GB

<details>
<summary>Answer</summary>

**C) 10 GB**

**Explanation:** Lambda container images support:
- **Maximum size**: 10 GB
- **Base images**: AWS-provided or custom
- **Registry**: Amazon ECR (Elastic Container Registry)
- **Architecture**: x86_64 or arm64

Comparison with zip packages:
| Feature | Zip Package | Container Image |
|---------|-------------|-----------------|
| Max size | 250 MB (unzipped) | 10 GB |
| Deployment | S3/direct upload | ECR |
| Custom runtime | Lambda Layers | Dockerfile |
| Tooling | SAM/CloudFormation | Docker |

Use containers for:
- Large dependencies (ML frameworks)
- Custom runtimes
- Existing container workflows
- Dependencies > 250 MB
</details>

---

### Question 29: EventBridge Integration

You want to invoke a Lambda function every weekday at 9 AM UTC. Which EventBridge rule pattern should you use?

A) Rate expression: rate(1 day)
B) Cron expression: cron(0 9 * * MON-FRI *)
C) Cron expression: cron(0 9 ? * MON-FRI *)
D) Event pattern matching

<details>
<summary>Answer</summary>

**C) Cron expression: cron(0 9 ? * MON-FRI *)**

**Explanation:** EventBridge cron format:
```
cron(minutes hours day-of-month month day-of-week year)
```

- `0` - minute 0
- `9` - hour 9 (UTC)
- `?` - any day of month (required when day-of-week is specified)
- `*` - every month
- `MON-FRI` - Monday through Friday
- `*` - every year

Important: When specifying day-of-week, use `?` for day-of-month (and vice versa).

Option B `cron(0 9 * * MON-FRI *)` is invalid because you cannot use `*` for both day-of-month and day-of-week.

Rate expressions (`rate(1 day)`) run every day, not weekdays only.
</details>

---

### Question 30: Serverless Best Practices

Which practice helps reduce Lambda cold starts for Java applications?

A) Increasing function timeout
B) Reducing memory allocation
C) Using GraalVM native image compilation
D) Disabling CloudWatch logging

<details>
<summary>Answer</summary>

**C) Using GraalVM native image compilation**

**Explanation:** Cold start optimization strategies for Java:

1. **GraalVM Native Image**:
   - Compiles Java to native binary ahead-of-time
   - Dramatically reduces cold start (from seconds to milliseconds)
   - Smaller deployment size
   - Trade-off: longer build time

2. **SnapStart** (AWS feature):
   - Creates snapshot of initialized function
   - Restores from snapshot on cold start
   - Significant reduction in Java cold starts

3. **Other optimizations**:
   - Minimize dependencies
   - Use tiered compilation
   - Initialize SDK clients lazily
   - Increase memory (more CPU)

What does NOT help:
- Increasing timeout (doesn't affect initialization)
- Reducing memory (makes it worse)
- Disabling logging (minimal impact)
</details>

---

## Scoring Guide

| Score | Level |
|-------|-------|
| 27-30 | Expert - Ready for Solutions Architect Professional |
| 22-26 | Proficient - Strong serverless knowledge |
| 17-21 | Intermediate - Review weak areas |
| 12-16 | Developing - More hands-on practice needed |
| 0-11 | Beginner - Review all module materials |

---

## Summary of Key Topics

### Lambda Fundamentals
- Pricing: Requests + GB-seconds
- Memory: 128 MB - 10,240 MB (proportional CPU)
- Timeout: 1 second - 15 minutes
- Layers: Maximum 5
- Package size: 250 MB unzipped, 10 GB container

### Invocation Types
- **Synchronous**: API Gateway, ALB, Lambda URLs
- **Asynchronous**: S3, SNS, EventBridge
- **Poll-based**: SQS, Kinesis, DynamoDB Streams

### Cold Start Mitigation
- Provisioned Concurrency
- Smaller package size
- Initialize outside handler
- Choose efficient runtime
- SnapStart for Java

### API Gateway
- REST API: Full features, caching, transformations
- HTTP API: Lower cost, simpler, JWT auth
- WebSocket API: Real-time bidirectional

### Step Functions
- Standard: Long-running, exactly-once
- Express: High-volume, short-duration
- States: Task, Choice, Parallel, Map, Wait, Pass
- Error handling: Retry then Catch

---

## Additional Practice

For hands-on practice, complete the labs in:
- [12-hands-on-lab.md](./12-hands-on-lab.md) - Complete serverless application lab
