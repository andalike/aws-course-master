# AWS X-Ray

## Introduction

AWS X-Ray is a distributed tracing service that helps developers analyze and debug distributed applications. It provides an end-to-end view of requests as they travel through your application, showing a map of your application's underlying components and helping identify performance bottlenecks and errors.

---

## X-Ray Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS X-Ray Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Client Request                                                              │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   API Gateway   │───►│   Lambda        │───►│   DynamoDB      │         │
│  │   (Segment)     │    │   (Segment)     │    │   (Subsegment)  │         │
│  └────────┬────────┘    └────────┬────────┘    └─────────────────┘         │
│           │                      │                                          │
│           │             ┌────────┴────────┐                                 │
│           │             │   S3            │                                 │
│           │             │   (Subsegment)  │                                 │
│           │             └─────────────────┘                                 │
│           │                                                                  │
│           └──────────────────────┬───────────────────────────────────►      │
│                                  │                                          │
│                                  ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         X-Ray Service                                │   │
│  │                                                                      │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│  │   │   Traces    │  │  Service    │  │  Analytics  │               │   │
│  │   │             │  │  Map        │  │             │               │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘               │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### Traces

A trace is the complete journey of a request through your application.

```
Trace ID: 1-67891234-abcdef012345678901234567

┌──────────────────────────────────────────────────────────────────────────────┐
│                              Complete Trace                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Timeline: 0ms ────────────────────────────────────────────────────► 250ms   │
│                                                                               │
│  ├── API Gateway ──────────────────────────────────────────────────────┤     │
│  │   (0ms - 250ms, 250ms total)                                        │     │
│  │                                                                      │     │
│  │   ├── Lambda Function ─────────────────────────────────────────┤   │     │
│  │   │   (5ms - 240ms, 235ms total)                               │   │     │
│  │   │                                                            │   │     │
│  │   │   ├── DynamoDB Query ──────┤ (10ms - 50ms, 40ms)          │   │     │
│  │   │   │                                                        │   │     │
│  │   │   ├── S3 GetObject ────────────────┤ (60ms - 150ms, 90ms) │   │     │
│  │   │   │                                                        │   │     │
│  │   │   ├── External API ───────────────────────────┤ (160-220ms)│   │     │
│  │   │   │                                                        │   │     │
│  │                                                                      │     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Segments

Segments represent work done by a service for a request.

```json
{
    "name": "my-lambda-function",
    "id": "abcd1234ef567890",
    "trace_id": "1-67891234-abcdef012345678901234567",
    "start_time": 1705312200.000,
    "end_time": 1705312200.250,
    "in_progress": false,
    "http": {
        "request": {
            "method": "GET",
            "url": "https://api.example.com/users/123"
        },
        "response": {
            "status": 200
        }
    },
    "aws": {
        "function_arn": "arn:aws:lambda:us-east-1:123456789012:function:my-function"
    }
}
```

### Subsegments

Subsegments provide more granular timing data within a segment.

```json
{
    "name": "DynamoDB",
    "id": "subseg1234567890",
    "start_time": 1705312200.010,
    "end_time": 1705312200.050,
    "namespace": "aws",
    "aws": {
        "operation": "Query",
        "table_name": "Users",
        "request_id": "abc123"
    }
}
```

### Annotations

Annotations are key-value pairs indexed for filtering traces.

```json
{
    "annotations": {
        "customer_id": "cust-123",
        "order_type": "express",
        "environment": "production"
    }
}
```

### Metadata

Metadata is additional data not indexed for search.

```json
{
    "metadata": {
        "request_details": {
            "user_agent": "Mozilla/5.0...",
            "request_body_size": 1024,
            "headers": {...}
        }
    }
}
```

---

## Service Map

The service map provides a visual representation of your application's architecture.

```
                              Service Map
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                              ┌─────────────┐                                │
│                              │   Client    │                                │
│                              └──────┬──────┘                                │
│                                     │                                        │
│                                     ▼                                        │
│                              ┌─────────────┐                                │
│                              │ API Gateway │                                │
│                              │   ● 99.5%   │◄── Response Time: 45ms avg    │
│                              └──────┬──────┘    Requests: 10,000/min        │
│                                     │                                        │
│                         ┌───────────┼───────────┐                           │
│                         │           │           │                           │
│                         ▼           ▼           ▼                           │
│                  ┌───────────┐ ┌───────────┐ ┌───────────┐                  │
│                  │ Lambda A  │ │ Lambda B  │ │ Lambda C  │                  │
│                  │  ● 99.9%  │ │  ● 98.5%  │ │  ● 100%   │                  │
│                  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                  │
│                        │             │             │                        │
│              ┌─────────┴─────────────┴─────────────┘                        │
│              │         │                                                    │
│              ▼         ▼                                                    │
│        ┌───────────┐ ┌───────────┐                                          │
│        │ DynamoDB  │ │    S3     │                                          │
│        │  ● 100%   │ │  ● 100%   │                                          │
│        └───────────┘ └───────────┘                                          │
│                                                                              │
│  Legend:  ● Success Rate   ─── Request Flow   Red: Errors                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Enabling X-Ray

### Lambda Functions

```yaml
# SAM Template
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: my-traced-function
      Handler: index.handler
      Runtime: python3.9
      Tracing: Active  # Enable X-Ray
      Policies:
        - AWSXRayDaemonWriteAccess
```

### API Gateway

```yaml
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      TracingEnabled: true  # Enable X-Ray
```

### EC2 / ECS

Install X-Ray Daemon:

```bash
# Install X-Ray Daemon on EC2
curl https://s3.us-east-1.amazonaws.com/aws-xray-assets.us-east-1/xray-daemon/aws-xray-daemon-3.x.rpm -o xray-daemon.rpm
sudo yum install -y xray-daemon.rpm
sudo systemctl start xray
```

### ECS Task Definition

```json
{
    "containerDefinitions": [
        {
            "name": "xray-daemon",
            "image": "amazon/aws-xray-daemon",
            "cpu": 32,
            "memoryReservation": 256,
            "portMappings": [
                {
                    "containerPort": 2000,
                    "protocol": "udp"
                }
            ]
        },
        {
            "name": "my-app",
            "image": "my-app:latest",
            "environment": [
                {
                    "name": "AWS_XRAY_DAEMON_ADDRESS",
                    "value": "xray-daemon:2000"
                }
            ]
        }
    ]
}
```

---

## Instrumenting Applications

### Python

```python
# Install: pip install aws-xray-sdk

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import boto3

# Patch all supported libraries
patch_all()

# Or patch specific libraries
# from aws_xray_sdk.core import patch
# patch(['boto3', 'requests'])

# Configure X-Ray
xray_recorder.configure(
    sampling=True,
    context_missing='LOG_ERROR',
    plugins=('EC2Plugin', 'ECSPlugin')
)

# Manual segment
@xray_recorder.capture('my_function')
def my_function():
    # Your code here
    pass

# Manual subsegment
def process_data(data):
    subsegment = xray_recorder.begin_subsegment('process_data')
    try:
        # Process data
        result = transform(data)
        subsegment.put_metadata('result_size', len(result))
        return result
    except Exception as e:
        subsegment.add_exception(e)
        raise
    finally:
        xray_recorder.end_subsegment()

# Add annotations
def handle_request(user_id, order_type):
    segment = xray_recorder.current_segment()
    segment.put_annotation('user_id', user_id)
    segment.put_annotation('order_type', order_type)

# Add metadata
def log_request_details(request):
    segment = xray_recorder.current_segment()
    segment.put_metadata('request', {
        'headers': dict(request.headers),
        'body_size': len(request.body)
    }, 'http')
```

### Node.js

```javascript
// Install: npm install aws-xray-sdk

const AWSXRay = require('aws-xray-sdk');
const AWS = AWSXRay.captureAWS(require('aws-sdk'));
const https = AWSXRay.captureHTTPs(require('https'));

// Configure X-Ray
AWSXRay.setDaemonAddress('127.0.0.1:2000');
AWSXRay.setContextMissingStrategy('LOG_ERROR');

// Capture Express
const express = require('express');
const app = express();
app.use(AWSXRay.express.openSegment('MyApp'));

app.get('/api/users/:id', async (req, res) => {
    const segment = AWSXRay.getSegment();

    // Add annotation
    segment.addAnnotation('userId', req.params.id);

    // Create subsegment
    const subsegment = segment.addNewSubsegment('fetchUser');
    try {
        const user = await fetchUser(req.params.id);
        subsegment.addMetadata('user', user);
        res.json(user);
    } catch (error) {
        subsegment.addError(error);
        res.status(500).json({ error: 'Failed to fetch user' });
    } finally {
        subsegment.close();
    }
});

app.use(AWSXRay.express.closeSegment());
```

### Java

```java
// Add dependency
// implementation 'com.amazonaws:aws-xray-recorder-sdk-core'

import com.amazonaws.xray.AWSXRay;
import com.amazonaws.xray.entities.Subsegment;

public class MyService {

    public void processRequest(String userId) {
        // Add annotation to current segment
        AWSXRay.getCurrentSegment().putAnnotation("userId", userId);

        // Create subsegment
        Subsegment subsegment = AWSXRay.beginSubsegment("processData");
        try {
            // Process data
            processData();
            subsegment.putMetadata("status", "success");
        } catch (Exception e) {
            subsegment.addException(e);
            throw e;
        } finally {
            AWSXRay.endSubsegment();
        }
    }
}
```

### Lambda Function (Python)

```python
import json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import boto3

# Patch AWS SDK calls
patch_all()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    # Add annotations
    xray_recorder.put_annotation('request_id', context.aws_request_id)

    user_id = event.get('user_id')
    xray_recorder.put_annotation('user_id', user_id)

    # Create custom subsegment
    with xray_recorder.in_subsegment('fetch-user') as subsegment:
        response = table.get_item(Key={'user_id': user_id})
        user = response.get('Item')
        subsegment.put_metadata('user_data', user)

    # Create another subsegment
    with xray_recorder.in_subsegment('process-user') as subsegment:
        result = process_user(user)
        subsegment.put_annotation('processed', True)

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def process_user(user):
    # Processing logic
    return {'status': 'processed', 'user': user}
```

---

## Sampling Rules

Sampling controls which requests are traced to reduce costs.

### Default Sampling Rule

```json
{
    "version": 2,
    "rules": [
        {
            "description": "Default rule",
            "host": "*",
            "http_method": "*",
            "url_path": "*",
            "fixed_target": 1,
            "rate": 0.05
        }
    ],
    "default": {
        "fixed_target": 1,
        "rate": 0.05
    }
}
```

### Custom Sampling Rules

```bash
# Create sampling rule via CLI
aws xray create-sampling-rule --cli-input-json '{
    "SamplingRule": {
        "RuleName": "HighPriorityAPI",
        "Priority": 100,
        "FixedRate": 0.1,
        "ReservoirSize": 10,
        "ServiceName": "*",
        "ServiceType": "*",
        "Host": "*",
        "HTTPMethod": "*",
        "URLPath": "/api/critical/*",
        "Version": 1
    }
}'
```

### Sampling Rule Parameters

| Parameter | Description |
|-----------|-------------|
| RuleName | Unique rule identifier |
| Priority | Lower number = higher priority |
| FixedRate | Percentage of requests to sample (0.0 - 1.0) |
| ReservoirSize | Fixed number of requests per second to sample |
| ServiceName | Service to match (* for all) |
| HTTPMethod | HTTP method to match |
| URLPath | URL path pattern to match |

---

## X-Ray Groups

Groups allow you to filter and organize traces.

### Create Group

```bash
aws xray create-group \
    --group-name "ProductionErrors" \
    --filter-expression 'service("api-gateway") AND fault'
```

### Filter Expressions

```
# All errors
fault

# Specific service errors
service("payment-service") AND fault

# Slow requests
responsetime > 5

# Combined conditions
service("api-gateway") AND (fault OR responsetime > 3)

# Annotation-based
annotation.customer_tier = "premium"

# HTTP status codes
http.status >= 500
```

---

## X-Ray Insights

X-Ray Insights automatically detects anomalies.

### Enable Insights

```bash
aws xray update-group \
    --group-name "Production" \
    --insights-configuration '{"InsightsEnabled": true, "NotificationsEnabled": true}'
```

### Insights Detection

X-Ray Insights automatically detects:
- Response time anomalies
- Error rate spikes
- Throughput changes
- Service availability issues

---

## Querying Traces

### Using AWS Console

1. Navigate to X-Ray > Traces
2. Apply time filter
3. Use filter expressions
4. Click on traces to see details

### Using AWS CLI

```bash
# Get trace summaries
aws xray get-trace-summaries \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --filter-expression 'fault'

# Get specific trace
aws xray batch-get-traces \
    --trace-ids "1-67891234-abcdef012345678901234567"

# Get service graph
aws xray get-service-graph \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s)
```

---

## CloudFormation for X-Ray

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: X-Ray Configuration

Resources:
  # Sampling Rule
  CriticalPathSamplingRule:
    Type: AWS::XRay::SamplingRule
    Properties:
      SamplingRule:
        RuleName: CriticalPath
        Priority: 100
        FixedRate: 0.5
        ReservoirSize: 50
        ServiceName: '*'
        ServiceType: '*'
        Host: '*'
        HTTPMethod: '*'
        URLPath: '/api/checkout/*'
        Version: 1

  # X-Ray Group
  ProductionGroup:
    Type: AWS::XRay::Group
    Properties:
      GroupName: Production
      FilterExpression: 'service("api-production") { fault }'
      InsightsConfiguration:
        InsightsEnabled: true
        NotificationsEnabled: true

  # Lambda with X-Ray
  TracedFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: traced-function
      Runtime: python3.9
      Handler: index.handler
      Role: !GetAtt LambdaRole.Arn
      TracingConfig:
        Mode: Active
      Code:
        ZipFile: |
          def handler(event, context):
              return {'statusCode': 200}
```

---

## Best Practices

### Instrumentation
1. Instrument all service-to-service calls
2. Add meaningful annotations for filtering
3. Use subsegments for granular timing
4. Capture errors and exceptions

### Sampling
1. Use higher sample rates for critical paths
2. Lower sample rates for high-volume, low-priority operations
3. Use fixed reservoir for minimum coverage

### Annotations
1. Include business context (customer ID, order ID)
2. Include environment information
3. Keep annotation values short and indexable

### Performance
1. Use async segment close when possible
2. Batch metadata updates
3. Monitor X-Ray SDK overhead

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| No traces appearing | Check X-Ray daemon, verify IAM permissions |
| Missing subsegments | Verify SDK patching, check segment context |
| High latency overhead | Reduce sampling rate, optimize metadata |
| Traces not connecting | Verify trace header propagation |

### Debugging

```bash
# Check X-Ray daemon status
sudo systemctl status xray

# View daemon logs
sudo journalctl -u xray -f

# Test daemon connectivity
curl -X POST http://localhost:2000/GetTraceSummaries

# Verify IAM permissions
aws xray get-sampling-rules
```

---

## Integration with CloudWatch

### ServiceLens

CloudWatch ServiceLens provides a unified view combining:
- X-Ray traces
- CloudWatch metrics
- CloudWatch logs

### Creating ServiceLens Dashboard

1. Navigate to CloudWatch > ServiceLens
2. Select service from map
3. View correlated metrics, traces, and logs
4. Drill down into specific traces

---

## Next Steps

Continue to the next sections:
- [09-cloudtrail.md](09-cloudtrail.md) - API activity logging
- [12-hands-on-labs.md](12-hands-on-labs.md) - Implement X-Ray tracing
