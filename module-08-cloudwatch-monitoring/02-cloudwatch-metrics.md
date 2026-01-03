# CloudWatch Metrics Deep Dive

## Introduction

CloudWatch Metrics are the fundamental building blocks of AWS monitoring. This section covers everything you need to know about working with metrics, from understanding their structure to publishing custom metrics.

---

## Metric Anatomy

### Core Components

Every CloudWatch metric consists of these elements:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CloudWatch Metric                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Namespace:    AWS/EC2                                          │
│  Metric Name:  CPUUtilization                                   │
│  Dimensions:   InstanceId = i-1234567890abcdef0                 │
│                                                                  │
│  Data Points:                                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Timestamp          │ Value  │ Unit    │ Statistics        │ │
│  ├────────────────────┼────────┼─────────┼───────────────────┤ │
│  │ 2024-01-15 10:00   │ 45.5   │ Percent │ Avg, Min, Max, Sum│ │
│  │ 2024-01-15 10:05   │ 52.3   │ Percent │ Avg, Min, Max, Sum│ │
│  │ 2024-01-15 10:10   │ 48.7   │ Percent │ Avg, Min, Max, Sum│ │
│  └────────────────────┴────────┴─────────┴───────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Namespace

Namespaces are containers for CloudWatch metrics that isolate different sets of metrics.

**AWS Service Namespaces**:
| Namespace | Service | Example Metrics |
|-----------|---------|-----------------|
| AWS/EC2 | EC2 Instances | CPUUtilization, NetworkIn, DiskReadBytes |
| AWS/EBS | EBS Volumes | VolumeReadOps, VolumeWriteOps, VolumeTotalReadTime |
| AWS/RDS | RDS Databases | DatabaseConnections, ReadLatency, FreeStorageSpace |
| AWS/Lambda | Lambda Functions | Invocations, Duration, Errors, Throttles |
| AWS/ELB | Classic Load Balancer | RequestCount, Latency, HTTPCode_Backend_2XX |
| AWS/ApplicationELB | ALB | RequestCount, TargetResponseTime, HTTPCode_Target_2XX |
| AWS/DynamoDB | DynamoDB | ConsumedReadCapacityUnits, ThrottledRequests |
| AWS/S3 | S3 Buckets | BucketSizeBytes, NumberOfObjects |
| AWS/SQS | SQS Queues | NumberOfMessagesSent, ApproximateNumberOfMessagesVisible |
| AWS/SNS | SNS Topics | NumberOfMessagesPublished, NumberOfNotificationsFailed |
| AWS/ApiGateway | API Gateway | Count, Latency, 4XXError, 5XXError |

**Custom Namespace Guidelines**:
```
# Good examples
MyCompany/PaymentService
Production/WebApp
DevOps/Infrastructure

# Naming rules
- Cannot start with "AWS/"
- Valid characters: alphanumeric, ".", "-", "_", "/", "#", ":"
- Maximum 256 characters
```

---

## Dimensions

Dimensions are name/value pairs that uniquely identify a metric.

### Understanding Dimensions

```
Namespace: AWS/EC2
Metric: CPUUtilization

With Dimensions:
┌──────────────────────────────────────────────────────────────┐
│ Dimension Combination              │ What it represents      │
├────────────────────────────────────┼─────────────────────────┤
│ InstanceId=i-abc123                │ Specific instance       │
│ InstanceType=t3.micro              │ All t3.micro instances  │
│ AutoScalingGroupName=MyASG         │ All instances in ASG    │
│ ImageId=ami-12345                  │ All instances from AMI  │
│ (no dimensions)                    │ Aggregate across all    │
└────────────────────────────────────┴─────────────────────────┘
```

### Common Dimensions by Service

**EC2**:
| Dimension | Description |
|-----------|-------------|
| InstanceId | Specific EC2 instance |
| InstanceType | All instances of this type |
| AutoScalingGroupName | Instances in Auto Scaling group |
| ImageId | Instances launched from AMI |

**Lambda**:
| Dimension | Description |
|-----------|-------------|
| FunctionName | Specific Lambda function |
| Resource | Function version or alias |
| ExecutedVersion | Specific version number |

**RDS**:
| Dimension | Description |
|-----------|-------------|
| DBInstanceIdentifier | Specific RDS instance |
| DBClusterIdentifier | Aurora cluster |
| DatabaseClass | All instances of class |
| EngineName | All instances of engine type |

**ELB/ALB**:
| Dimension | Description |
|-----------|-------------|
| LoadBalancer | Specific load balancer |
| TargetGroup | Specific target group |
| AvailabilityZone | Load balancer in specific AZ |

### Dimension Limits

- Maximum **30 dimensions** per metric
- Dimension name: maximum **255 characters**
- Dimension value: maximum **1024 characters**

---

## Statistics

Statistics are aggregations of metric data over specified periods.

### Available Statistics

| Statistic | Description | Use Case |
|-----------|-------------|----------|
| **Average** | Mean of all values | CPU utilization, latency |
| **Sum** | Total of all values | Request count, bytes transferred |
| **Minimum** | Lowest value | Response time floor |
| **Maximum** | Highest value | Peak usage, spikes |
| **SampleCount** | Number of data points | Request frequency |
| **pNN.NN** | Percentile (p50, p99, etc.) | Latency distribution |

### Percentiles

Percentiles show the distribution of your data:

```
Response Times for 1000 requests:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│ p50 (50th percentile) = 100ms                                 │
│   └── 50% of requests completed in 100ms or less             │
│                                                                │
│ p90 (90th percentile) = 250ms                                 │
│   └── 90% of requests completed in 250ms or less             │
│                                                                │
│ p95 (95th percentile) = 400ms                                 │
│   └── 95% of requests completed in 400ms or less             │
│                                                                │
│ p99 (99th percentile) = 800ms                                 │
│   └── 99% of requests completed in 800ms or less             │
│                                                                │
│ p99.9 (99.9th percentile) = 1500ms                           │
│   └── 99.9% of requests completed in 1500ms or less          │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Choosing the Right Statistic

| Metric Type | Recommended Statistic |
|-------------|----------------------|
| CPU/Memory Utilization | Average |
| Request Count | Sum |
| Latency | p50, p90, p99 |
| Error Count | Sum |
| Queue Depth | Maximum |
| Connection Count | Maximum |
| Disk I/O | Average, Sum |

---

## Periods

Periods define the time interval for metric aggregation.

### Standard vs. High-Resolution Metrics

| Type | Minimum Period | Default Period | Storage Duration |
|------|---------------|----------------|------------------|
| Standard | 1 minute | 5 minutes (EC2) | See retention |
| High-Resolution | 1 second | N/A | See retention |

### Metric Retention

CloudWatch automatically aggregates data at different resolutions:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Metric Data Retention                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1-second metrics  ──────►  3 hours                             │
│  (high-resolution)                                               │
│                                                                  │
│  60-second metrics ──────►  15 days                             │
│  (1-minute)                                                      │
│                                                                  │
│  5-minute metrics  ──────►  63 days                             │
│  (300 seconds)                                                   │
│                                                                  │
│  1-hour metrics    ──────►  455 days (15 months)                │
│  (3600 seconds)                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Period Selection

```bash
# 1-minute granularity (last 15 days)
aws cloudwatch get-metric-statistics \
    --period 60 \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)

# 5-minute granularity (last 63 days)
aws cloudwatch get-metric-statistics \
    --period 300 \
    --start-time $(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)

# 1-hour granularity (last 455 days)
aws cloudwatch get-metric-statistics \
    --period 3600 \
    --start-time $(date -u -d '90 days ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## Custom Metrics

### When to Use Custom Metrics

Custom metrics are essential for:
- Application-specific KPIs
- Business metrics (orders, revenue)
- System metrics not captured by CloudWatch Agent
- Custom calculations and aggregations

### Publishing Custom Metrics

#### AWS CLI

```bash
# Single metric
aws cloudwatch put-metric-data \
    --namespace "MyApplication" \
    --metric-name "PageViews" \
    --value 100 \
    --unit Count

# Metric with dimensions
aws cloudwatch put-metric-data \
    --namespace "MyApplication" \
    --metric-name "RequestLatency" \
    --value 250 \
    --unit Milliseconds \
    --dimensions Page=HomePage,Region=us-east-1

# High-resolution metric (1-second)
aws cloudwatch put-metric-data \
    --namespace "MyApplication" \
    --metric-name "TransactionsPerSecond" \
    --value 1500 \
    --unit Count/Second \
    --storage-resolution 1

# Multiple metrics in one call
aws cloudwatch put-metric-data \
    --namespace "MyApplication" \
    --metric-data '[
        {
            "MetricName": "ProcessedItems",
            "Value": 100,
            "Unit": "Count"
        },
        {
            "MetricName": "ProcessingTime",
            "Value": 2.5,
            "Unit": "Seconds"
        }
    ]'

# Metric with timestamp
aws cloudwatch put-metric-data \
    --namespace "MyApplication" \
    --metric-name "BatchSize" \
    --value 500 \
    --unit Count \
    --timestamp "2024-01-15T10:30:00Z"
```

#### Python (Boto3)

```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

# Single metric
cloudwatch.put_metric_data(
    Namespace='MyApplication',
    MetricData=[
        {
            'MetricName': 'PageViews',
            'Value': 100,
            'Unit': 'Count',
            'Timestamp': datetime.utcnow()
        }
    ]
)

# Metric with dimensions
cloudwatch.put_metric_data(
    Namespace='MyApplication',
    MetricData=[
        {
            'MetricName': 'RequestLatency',
            'Dimensions': [
                {'Name': 'Page', 'Value': 'HomePage'},
                {'Name': 'Environment', 'Value': 'Production'}
            ],
            'Value': 250,
            'Unit': 'Milliseconds'
        }
    ]
)

# High-resolution metric
cloudwatch.put_metric_data(
    Namespace='MyApplication',
    MetricData=[
        {
            'MetricName': 'TPS',
            'Value': 1500,
            'Unit': 'Count/Second',
            'StorageResolution': 1  # 1-second resolution
        }
    ]
)

# Statistic set (pre-aggregated values)
cloudwatch.put_metric_data(
    Namespace='MyApplication',
    MetricData=[
        {
            'MetricName': 'RequestLatency',
            'StatisticValues': {
                'SampleCount': 100,
                'Sum': 25000,
                'Minimum': 50,
                'Maximum': 500
            },
            'Unit': 'Milliseconds'
        }
    ]
)

# Batch publish (up to 1000 data points)
metrics = []
for i in range(100):
    metrics.append({
        'MetricName': 'PageViews',
        'Dimensions': [
            {'Name': 'Page', 'Value': f'Page{i}'}
        ],
        'Value': i * 10,
        'Unit': 'Count'
    })

# Split into batches of 20 (API limit)
for i in range(0, len(metrics), 20):
    batch = metrics[i:i+20]
    cloudwatch.put_metric_data(
        Namespace='MyApplication',
        MetricData=batch
    )
```

#### Node.js

```javascript
const AWS = require('aws-sdk');
const cloudwatch = new AWS.CloudWatch();

// Single metric
const params = {
    Namespace: 'MyApplication',
    MetricData: [
        {
            MetricName: 'PageViews',
            Value: 100,
            Unit: 'Count',
            Timestamp: new Date()
        }
    ]
};

cloudwatch.putMetricData(params, (err, data) => {
    if (err) console.error(err);
    else console.log('Metric published:', data);
});

// With dimensions
const paramsWithDimensions = {
    Namespace: 'MyApplication',
    MetricData: [
        {
            MetricName: 'APILatency',
            Dimensions: [
                { Name: 'Endpoint', Value: '/api/users' },
                { Name: 'Method', Value: 'GET' }
            ],
            Value: 150,
            Unit: 'Milliseconds'
        }
    ]
};

cloudwatch.putMetricData(paramsWithDimensions).promise()
    .then(data => console.log('Success:', data))
    .catch(err => console.error('Error:', err));
```

---

## Metric Units

### Available Units

| Category | Units |
|----------|-------|
| **Count** | Count, None |
| **Time** | Seconds, Microseconds, Milliseconds |
| **Data Size** | Bytes, Kilobytes, Megabytes, Gigabytes, Terabytes |
| **Data Rate** | Bits/Second, Kilobits/Second, Megabits/Second, Gigabits/Second |
| **Throughput** | Bytes/Second, Kilobytes/Second, Megabytes/Second, Gigabytes/Second |
| **Percentage** | Percent |
| **Rate** | Count/Second |

### Unit Best Practices

```python
# Good: Consistent units
cloudwatch.put_metric_data(
    Namespace='MyApp',
    MetricData=[
        {'MetricName': 'Latency', 'Value': 250, 'Unit': 'Milliseconds'},
        {'MetricName': 'Throughput', 'Value': 1.5, 'Unit': 'Megabytes/Second'},
        {'MetricName': 'ErrorRate', 'Value': 0.5, 'Unit': 'Percent'},
        {'MetricName': 'RequestCount', 'Value': 1000, 'Unit': 'Count'}
    ]
)
```

---

## Metric Math

Metric Math allows you to perform calculations across multiple metrics.

### Basic Operations

```
# Addition
e1 = m1 + m2

# Subtraction
e1 = m1 - m2

# Multiplication
e1 = m1 * m2

# Division
e1 = m1 / m2

# Percentage
e1 = (m1 / m2) * 100
```

### Mathematical Functions

| Function | Description | Example |
|----------|-------------|---------|
| ABS(m) | Absolute value | ABS(m1 - m2) |
| AVG(m) | Average across metrics | AVG([m1, m2, m3]) |
| CEIL(m) | Round up | CEIL(m1) |
| FLOOR(m) | Round down | FLOOR(m1) |
| MAX(m) | Maximum value | MAX([m1, m2]) |
| MIN(m) | Minimum value | MIN([m1, m2]) |
| SUM(m) | Sum all values | SUM([m1, m2, m3]) |
| STDDEV(m) | Standard deviation | STDDEV(m1) |

### Time-Based Functions

| Function | Description |
|----------|-------------|
| RATE(m) | Change per second |
| DIFF(m) | Difference from previous |
| DIFF_TIME(m) | Time difference |
| RUNNING_SUM(m) | Cumulative sum |
| ANOMALY_DETECTION_BAND(m) | Anomaly detection band |

### Practical Examples

```python
# Example 1: Error Rate Calculation
# Error Rate = (Errors / Total Requests) * 100

# In CloudWatch console or API:
"""
Metrics:
  m1 = AWS/ApplicationELB HTTPCode_Target_5XX_Count
  m2 = AWS/ApplicationELB RequestCount

Expression:
  e1 = (m1 / m2) * 100
  Label: "Error Rate %"
"""

# Example 2: Memory Available
# Available Memory = Total Memory - Used Memory

"""
Metrics:
  m1 = CWAgent/mem_total
  m2 = CWAgent/mem_used

Expression:
  e1 = m1 - m2
  Label: "Available Memory"
"""

# Example 3: Average Latency Across Multiple Targets
"""
Metrics:
  m1 = AWS/ApplicationELB TargetResponseTime (TargetGroup=tg1)
  m2 = AWS/ApplicationELB TargetResponseTime (TargetGroup=tg2)
  m3 = AWS/ApplicationELB TargetResponseTime (TargetGroup=tg3)

Expression:
  e1 = AVG([m1, m2, m3])
  Label: "Average Latency"
"""

# Example 4: Requests Per Second from Request Count
"""
Metrics:
  m1 = AWS/ApplicationELB RequestCount (Period=60)

Expression:
  e1 = m1 / 60
  Label: "Requests Per Second"
"""
```

### Using Metric Math in AWS CLI

```bash
# Get metric math expression results
aws cloudwatch get-metric-data \
    --metric-data-queries '[
        {
            "Id": "errors",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/ApplicationELB",
                    "MetricName": "HTTPCode_Target_5XX_Count",
                    "Dimensions": [
                        {"Name": "LoadBalancer", "Value": "app/my-alb/1234567890"}
                    ]
                },
                "Period": 300,
                "Stat": "Sum"
            },
            "ReturnData": false
        },
        {
            "Id": "requests",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/ApplicationELB",
                    "MetricName": "RequestCount",
                    "Dimensions": [
                        {"Name": "LoadBalancer", "Value": "app/my-alb/1234567890"}
                    ]
                },
                "Period": 300,
                "Stat": "Sum"
            },
            "ReturnData": false
        },
        {
            "Id": "errorRate",
            "Expression": "(errors / requests) * 100",
            "Label": "Error Rate %",
            "ReturnData": true
        }
    ]' \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## Search Expressions

Search expressions allow you to dynamically query metrics using pattern matching.

### Syntax

```
SEARCH('expression', 'statistic', period)
```

### Examples

```bash
# Find all EC2 CPUUtilization metrics
SEARCH('Namespace="AWS/EC2" MetricName="CPUUtilization"', 'Average', 300)

# Find metrics with specific dimension value
SEARCH('{AWS/EC2,InstanceId} InstanceId="i-abc123"', 'Average', 300)

# Search across custom namespace
SEARCH('Namespace="MyApp" MetricName="Latency"', 'p99', 300)

# Search with wildcards
SEARCH('MetricName="*Error*"', 'Sum', 300)

# Multiple conditions
SEARCH('Namespace="AWS/Lambda" MetricName="Errors" FunctionName="prod-*"', 'Sum', 300)
```

---

## Metric Streams

CloudWatch Metric Streams continuously streams metrics to destinations like Kinesis Data Firehose.

### Use Cases
- Real-time analytics in Datadog, Splunk, Dynatrace
- Custom metric processing
- Long-term storage in S3

### Configuration

```yaml
# CloudFormation example
Resources:
  MetricStream:
    Type: AWS::CloudWatch::MetricStream
    Properties:
      Name: AllMetricsStream
      FirehoseArn: !GetAtt DeliveryStream.Arn
      RoleArn: !GetAtt MetricStreamRole.Arn
      OutputFormat: json
      IncludeFilters:
        - Namespace: AWS/EC2
        - Namespace: AWS/Lambda
        - Namespace: MyApplication
```

---

## Embedded Metric Format (EMF)

EMF allows you to embed custom metrics within structured log events.

### Benefits
- Single call for logs and metrics
- Automatic metric extraction
- High-cardinality support
- Lower latency than PutMetricData

### Example

```python
import json
import sys

def emit_metric(namespace, metric_name, value, dimensions, unit="Count"):
    emf_log = {
        "_aws": {
            "Timestamp": int(datetime.now().timestamp() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": namespace,
                    "Dimensions": [list(dimensions.keys())],
                    "Metrics": [
                        {
                            "Name": metric_name,
                            "Unit": unit
                        }
                    ]
                }
            ]
        },
        metric_name: value,
        **dimensions
    }
    print(json.dumps(emf_log))
    sys.stdout.flush()

# Usage
emit_metric(
    namespace="MyApp",
    metric_name="OrderProcessed",
    value=1,
    dimensions={
        "Environment": "Production",
        "Region": "us-east-1"
    }
)
```

### Lambda with EMF

```python
from aws_embedded_metrics import metric_scope

@metric_scope
def handler(event, context, metrics):
    metrics.set_namespace("MyApp")
    metrics.set_dimensions({"Environment": "Production"})

    # These automatically become CloudWatch metrics
    metrics.put_metric("ProcessingTime", 150, "Milliseconds")
    metrics.put_metric("ItemsProcessed", 50, "Count")

    return {"statusCode": 200}
```

---

## Best Practices

### Naming Conventions
```
# Namespaces
CompanyName/ServiceName
Environment/Application

# Metric Names
RequestCount (not request_count or RequestCnt)
ProcessingTimeMs (include unit in name if helpful)
ErrorRate (clear and concise)

# Dimension Names
Environment (not env)
InstanceId (match AWS conventions)
CustomerTier (business context)
```

### Performance Optimization
- Batch PutMetricData calls (up to 20 metrics per call)
- Use statistic sets for pre-aggregated data
- Choose appropriate resolution (standard vs. high-res)
- Consider EMF for Lambda functions

### Cost Optimization
- Use standard resolution unless sub-minute is required
- Aggregate client-side before publishing
- Review unused custom metrics
- Use metric streams for third-party integration

---

## Common Metric Patterns

### Application Performance
```python
# Request latency by endpoint
put_metric('RequestLatency', latency_ms,
           dimensions={'Endpoint': endpoint, 'Method': method})

# Error rate by error type
put_metric('ErrorCount', 1,
           dimensions={'ErrorType': error_type, 'Service': service})

# Throughput
put_metric('RequestCount', batch_size,
           dimensions={'Operation': operation})
```

### Business Metrics
```python
# Order processing
put_metric('OrdersPlaced', order_count,
           dimensions={'Region': region, 'CustomerType': customer_type})

# Revenue tracking
put_metric('Revenue', amount,
           dimensions={'Product': product, 'Currency': currency})
```

### Infrastructure
```python
# Queue depth
put_metric('QueueDepth', message_count,
           dimensions={'QueueName': queue_name})

# Cache hit ratio
put_metric('CacheHitRatio', ratio * 100,
           dimensions={'CacheCluster': cluster_id})
```

---

## Next Steps

Continue to the next sections:
- [03-cloudwatch-alarms.md](03-cloudwatch-alarms.md) - Create alarms based on metrics
- [04-cloudwatch-logs.md](04-cloudwatch-logs.md) - Log management and analysis
