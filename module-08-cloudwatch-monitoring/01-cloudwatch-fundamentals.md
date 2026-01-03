# CloudWatch Fundamentals

## Introduction to Amazon CloudWatch

Amazon CloudWatch is AWS's comprehensive monitoring and observability service that provides data and actionable insights to monitor applications, respond to system-wide performance changes, and optimize resource utilization. It serves as the central nervous system for AWS operational health.

---

## CloudWatch Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Amazon CloudWatch                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Metrics    │  │    Logs      │  │   Alarms     │  │  Dashboards  │    │
│  │              │  │              │  │              │  │              │    │
│  │ - Standard   │  │ - Log Groups │  │ - Static     │  │ - Widgets    │    │
│  │ - Custom     │  │ - Log Stream │  │ - Anomaly    │  │ - Automatic  │    │
│  │ - Math       │  │ - Insights   │  │ - Composite  │  │ - Cross-Acct │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Events     │  │  ServiceLens │  │  Contributor │  │   Synthetics │    │
│  │ (EventBridge)│  │              │  │   Insights   │  │              │    │
│  │              │  │ - X-Ray      │  │              │  │ - Canaries   │    │
│  │ - Rules      │  │ - Service Map│  │ - Top-N      │  │ - Blueprints │    │
│  │ - Targets    │  │ - Traces     │  │ - Time Series│  │ - Schedules  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
     ┌──────┴──────┐        ┌───────┴───────┐       ┌──────┴──────┐
     │  AWS Services│        │  Applications │       │  On-Premises│
     │             │        │               │       │             │
     │ EC2, Lambda │        │ Custom Apps   │       │ Servers     │
     │ RDS, ELB    │        │ Containers    │       │ VMs         │
     │ S3, DynamoDB│        │ Microservices │       │ Databases   │
     └─────────────┘        └───────────────┘       └─────────────┘
```

---

## Core Components

### 1. Metrics

Metrics are time-ordered sets of data points published to CloudWatch. They represent a variable to monitor over time.

**Key Concepts**:
- **Namespace**: Container for CloudWatch metrics (e.g., AWS/EC2)
- **Metric Name**: Unique identifier within a namespace
- **Dimension**: Name/value pair for metric filtering
- **Timestamp**: Time when data was recorded
- **Value**: The actual measurement
- **Unit**: The unit of measure (Bytes, Seconds, Count, etc.)

**Example Metric Data Point**:
```json
{
  "Namespace": "AWS/EC2",
  "MetricName": "CPUUtilization",
  "Dimensions": [
    {
      "Name": "InstanceId",
      "Value": "i-1234567890abcdef0"
    }
  ],
  "Timestamp": "2024-01-15T10:30:00Z",
  "Value": 45.5,
  "Unit": "Percent"
}
```

### 2. Logs

CloudWatch Logs enables you to centralize logs from all your systems, applications, and AWS services.

**Key Concepts**:
- **Log Groups**: Collection of log streams sharing retention and access settings
- **Log Streams**: Sequence of log events from the same source
- **Log Events**: Individual log entries with timestamp and message
- **Retention**: How long logs are stored (1 day to 10 years, or indefinitely)

**Log Hierarchy**:
```
CloudWatch Logs
└── Log Group: /aws/lambda/my-function
    ├── Log Stream: 2024/01/15/[$LATEST]abc123
    │   ├── Log Event: START RequestId...
    │   ├── Log Event: Processing request...
    │   └── Log Event: END RequestId...
    └── Log Stream: 2024/01/15/[$LATEST]def456
        ├── Log Event: START RequestId...
        └── Log Event: END RequestId...
```

### 3. Alarms

Alarms watch metrics and perform actions when thresholds are breached.

**Alarm States**:
| State | Description |
|-------|-------------|
| OK | Metric is within threshold |
| ALARM | Metric has breached threshold |
| INSUFFICIENT_DATA | Not enough data to determine state |

**Alarm Types**:
- **Static Threshold**: Fixed value comparison
- **Anomaly Detection**: Machine learning-based dynamic thresholds
- **Composite**: Logical combination of multiple alarms

### 4. Dashboards

Dashboards are customizable home pages for monitoring resources.

**Features**:
- Multiple widget types (line, stacked area, number, text, logs)
- Cross-account and cross-region support
- Automatic dashboards for AWS services
- Shareable via AWS Organizations

---

## CloudWatch vs. Other AWS Monitoring Services

| Service | Purpose | Key Difference |
|---------|---------|----------------|
| **CloudWatch** | Metrics, logs, alarms | Central monitoring hub |
| **X-Ray** | Distributed tracing | Request path analysis |
| **CloudTrail** | API logging | Who did what and when |
| **AWS Config** | Configuration history | What changed and compliance |
| **EventBridge** | Event routing | React to events |
| **Systems Manager** | Operational management | Take action on resources |

---

## How AWS Services Publish to CloudWatch

### Automatic Metrics (Free Tier)

Most AWS services automatically publish metrics to CloudWatch:

| Service | Default Metrics | Default Period |
|---------|----------------|----------------|
| EC2 | CPU, Network, Disk | 5 minutes |
| ELB | Request count, Latency | 1 minute |
| RDS | CPU, Connections, Storage | 1 minute |
| Lambda | Invocations, Duration, Errors | 1 minute |
| S3 | Bucket size, Object count | Daily |
| DynamoDB | Read/Write capacity | 1 minute |

### Detailed Monitoring (Paid)

Enable detailed monitoring for higher resolution:

| Service | Standard | Detailed |
|---------|----------|----------|
| EC2 | 5 minutes | 1 minute |
| Auto Scaling | 5 minutes | 1 minute |

---

## CloudWatch Pricing Model

### Free Tier (Monthly)

| Component | Free Allowance |
|-----------|----------------|
| Metrics | 10 custom metrics |
| Alarms | 10 alarms |
| Dashboards | 3 dashboards (50 metrics each) |
| Logs Data | 5 GB ingested |
| Logs Storage | 5 GB archived |
| API Requests | 1,000,000 requests |

### Paid Pricing (Key Components)

| Component | Cost (approximate) |
|-----------|-------------------|
| Custom Metrics | $0.30/metric/month |
| Dashboard | $3.00/dashboard/month |
| Alarms (standard) | $0.10/alarm/month |
| Alarms (high-res) | $0.30/alarm/month |
| Logs Ingestion | $0.50/GB |
| Logs Storage | $0.03/GB/month |
| Logs Insights | $0.005/GB scanned |

---

## Accessing CloudWatch

### AWS Console

Navigate to CloudWatch in the AWS Console for visual access to all features.

### AWS CLI

```bash
# List all metrics
aws cloudwatch list-metrics

# Get metric statistics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --start-time 2024-01-15T00:00:00Z \
    --end-time 2024-01-15T23:59:59Z \
    --period 300 \
    --statistics Average

# Put custom metric
aws cloudwatch put-metric-data \
    --namespace MyApplication \
    --metric-name RequestCount \
    --value 100 \
    --unit Count

# Describe alarms
aws cloudwatch describe-alarms

# Get log events
aws logs get-log-events \
    --log-group-name /aws/lambda/my-function \
    --log-stream-name "2024/01/15/[\$LATEST]abc123"
```

### AWS SDK (Python/Boto3)

```python
import boto3
from datetime import datetime, timedelta

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# Get CPU utilization
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-1234567890abcdef0'
        }
    ],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,
    Statistics=['Average', 'Maximum']
)

# Print results
for datapoint in response['Datapoints']:
    print(f"Time: {datapoint['Timestamp']}, "
          f"Average: {datapoint['Average']:.2f}%, "
          f"Maximum: {datapoint['Maximum']:.2f}%")
```

### CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudWatch Resources

Resources:
  # CloudWatch Alarm
  CPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighCPUUtilization
      AlarmDescription: Alarm when CPU exceeds 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: InstanceId
          Value: !Ref MyInstance
      AlarmActions:
        - !Ref AlertTopic

  # Log Group
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /application/my-app
      RetentionInDays: 30

  # Dashboard
  MonitoringDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: ApplicationDashboard
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0,
              "y": 0,
              "width": 12,
              "height": 6,
              "properties": {
                "metrics": [
                  ["AWS/EC2", "CPUUtilization", "InstanceId", "${MyInstance}"]
                ],
                "title": "EC2 CPU Utilization",
                "period": 300,
                "region": "${AWS::Region}"
              }
            }
          ]
        }
```

---

## CloudWatch Namespaces

### AWS Service Namespaces

AWS services use standardized namespace formats:

| Namespace | Service |
|-----------|---------|
| AWS/EC2 | Amazon EC2 |
| AWS/EBS | Amazon EBS |
| AWS/ELB | Classic Load Balancer |
| AWS/ApplicationELB | Application Load Balancer |
| AWS/NetworkELB | Network Load Balancer |
| AWS/RDS | Amazon RDS |
| AWS/DynamoDB | Amazon DynamoDB |
| AWS/Lambda | AWS Lambda |
| AWS/S3 | Amazon S3 |
| AWS/SNS | Amazon SNS |
| AWS/SQS | Amazon SQS |
| AWS/ApiGateway | Amazon API Gateway |
| AWS/Kinesis | Amazon Kinesis |
| AWS/CloudFront | Amazon CloudFront |

### Custom Namespaces

For custom metrics, use your own namespace:

```bash
# Best practice: Use organization/application prefix
aws cloudwatch put-metric-data \
    --namespace "MyCompany/OrderService" \
    --metric-name OrderCount \
    --value 50 \
    --unit Count
```

---

## Key CloudWatch Features Summary

### Metrics Features
- **Metric Math**: Perform calculations across metrics
- **Search Expressions**: Query metrics dynamically
- **Contributor Insights**: Identify top contributors
- **Anomaly Detection**: ML-based anomaly bands

### Logs Features
- **Logs Insights**: SQL-like query language
- **Metric Filters**: Extract metrics from logs
- **Subscription Filters**: Stream to Kinesis, Lambda, ES
- **Live Tail**: Real-time log viewing

### Alarm Features
- **Composite Alarms**: Combine multiple alarms
- **Missing Data Treatment**: Handle gaps in data
- **Actions**: EC2, Auto Scaling, SNS
- **Anomaly Detection Alarms**: Dynamic thresholds

### Dashboard Features
- **Automatic Dashboards**: Pre-built for services
- **Cross-Account**: View metrics from linked accounts
- **Text Widgets**: Add context and documentation
- **API Integration**: Programmatic updates

---

## CloudWatch Limits

| Resource | Default Limit |
|----------|---------------|
| Metrics per namespace | No limit |
| Dimensions per metric | 30 |
| Alarms per account | 5,000 |
| Dashboard widgets | 500 |
| Log groups per account | 1,000,000 |
| Log events per batch | 10,000 |
| Metric data points per call | 1,000 |

---

## Best Practices

### Naming Conventions
```
# Log Groups
/aws/service-name             # AWS services
/application/app-name/env     # Applications
/custom/team-name/service     # Custom services

# Custom Metrics Namespaces
CompanyName/ApplicationName
Environment/ServiceName
```

### Organization
- Use consistent dimension naming
- Group related metrics logically
- Tag log groups for cost allocation
- Create environment-specific dashboards

### Cost Optimization
- Set appropriate log retention
- Use standard resolution when possible
- Delete unused dashboards and alarms
- Sample high-volume custom metrics

---

## Next Steps

Continue to the next sections to dive deeper into:
- [02-cloudwatch-metrics.md](02-cloudwatch-metrics.md) - Detailed metrics configuration
- [03-cloudwatch-alarms.md](03-cloudwatch-alarms.md) - Alarm setup and best practices
- [04-cloudwatch-logs.md](04-cloudwatch-logs.md) - Log management strategies
