# CloudWatch Alarms

## Introduction

CloudWatch Alarms watch metrics and perform automated actions when thresholds are breached. They are essential for proactive monitoring and automated incident response.

---

## Alarm Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CloudWatch Alarm                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Metric    │───►│   Alarm      │───►│   Actions    │                   │
│  │   Data      │    │   Evaluation │    │              │                   │
│  └─────────────┘    └──────────────┘    └──────────────┘                   │
│                            │                    │                           │
│                            ▼                    ▼                           │
│                     ┌──────────────┐    ┌──────────────────────────┐       │
│                     │    States    │    │ - SNS Notification       │       │
│                     │              │    │ - EC2 Action             │       │
│                     │ ┌──────────┐ │    │ - Auto Scaling Action    │       │
│                     │ │    OK    │ │    │ - Systems Manager Action │       │
│                     │ └──────────┘ │    │ - Lambda Action          │       │
│                     │ ┌──────────┐ │    └──────────────────────────┘       │
│                     │ │  ALARM   │ │                                        │
│                     │ └──────────┘ │                                        │
│                     │ ┌──────────┐ │                                        │
│                     │ │INSUFF_   │ │                                        │
│                     │ │DATA      │ │                                        │
│                     │ └──────────┘ │                                        │
│                     └──────────────┘                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Alarm States

### State Definitions

| State | Description | Typical Action |
|-------|-------------|----------------|
| **OK** | Metric is within the defined threshold | No action needed |
| **ALARM** | Metric has breached the threshold | Trigger notifications/actions |
| **INSUFFICIENT_DATA** | Not enough data to determine state | May need investigation |

### State Transitions

```
                    ┌─────────────────────┐
                    │                     │
                    ▼                     │
            ┌──────────────┐              │
   ┌───────►│     OK       │◄────────┐    │
   │        └──────────────┘         │    │
   │               │                 │    │
   │  Below        │ Breaches        │    │
   │  Threshold    │ Threshold       │    │
   │               ▼                 │    │
   │        ┌──────────────┐         │    │
   │        │    ALARM     │         │    │
   │        └──────────────┘         │    │
   │               │                 │    │
   │               │ No Data         │    │
   │               ▼                 │    │
   │        ┌──────────────┐         │    │
   └────────│ INSUFFICIENT │─────────┘    │
            │    DATA      │──────────────┘
            └──────────────┘
                    │
                    │ Startup
                    ▲
                    │
            [ Alarm Created ]
```

---

## Alarm Types

### 1. Static Threshold Alarms

Traditional alarms with fixed threshold values.

```bash
# Create a static threshold alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "HighCPU-WebServer" \
    --alarm-description "Alarm when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts \
    --ok-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### 2. Anomaly Detection Alarms

Machine learning-based alarms that adapt to metric patterns.

```bash
# Create an anomaly detection alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "AnomalousLatency-API" \
    --alarm-description "Alarm when latency is anomalous" \
    --metrics '[
        {
            "Id": "m1",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/ApplicationELB",
                    "MetricName": "TargetResponseTime",
                    "Dimensions": [
                        {"Name": "LoadBalancer", "Value": "app/my-alb/1234567890"}
                    ]
                },
                "Period": 300,
                "Stat": "Average"
            },
            "ReturnData": true
        },
        {
            "Id": "ad1",
            "Expression": "ANOMALY_DETECTION_BAND(m1, 2)",
            "Label": "LatencyAnomaly",
            "ReturnData": true
        }
    ]' \
    --threshold-metric-id ad1 \
    --comparison-operator LessThanLowerOrGreaterThanUpperThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### 3. Composite Alarms

Alarms that combine multiple alarms using boolean logic.

```bash
# Create child alarms first
aws cloudwatch put-metric-alarm \
    --alarm-name "HighCPU" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 2

aws cloudwatch put-metric-alarm \
    --alarm-name "HighMemory" \
    --metric-name mem_used_percent \
    --namespace CWAgent \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 2

# Create composite alarm
aws cloudwatch put-composite-alarm \
    --alarm-name "CriticalServerHealth" \
    --alarm-rule "ALARM(HighCPU) AND ALARM(HighMemory)" \
    --alarm-description "Both CPU and Memory are high" \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:critical-alerts \
    --ok-actions arn:aws:sns:us-east-1:123456789012:alerts
```

---

## Comparison Operators

| Operator | Description | Use Case |
|----------|-------------|----------|
| GreaterThanThreshold | > threshold | CPU, memory, latency |
| GreaterThanOrEqualToThreshold | >= threshold | Error counts |
| LessThanThreshold | < threshold | Available storage |
| LessThanOrEqualToThreshold | <= threshold | Connection pool |
| LessThanLowerOrGreaterThanUpperThreshold | Outside band | Anomaly detection |
| LessThanLowerThreshold | < lower band | Anomaly (low) |
| GreaterThanUpperThreshold | > upper band | Anomaly (high) |

---

## Evaluation Periods and Datapoints

### Understanding Evaluation

```
Alarm Configuration:
- Period: 60 seconds
- Evaluation Periods: 3
- Datapoints to Alarm: 2

Timeline:
┌─────────────────────────────────────────────────────────────────┐
│  Period 1    │  Period 2    │  Period 3    │  Result          │
├──────────────┼──────────────┼──────────────┼──────────────────┤
│  75% (OK)    │  85% (BREACH)│  82% (BREACH)│  ALARM (2 of 3)  │
│  85% (BREACH)│  75% (OK)    │  82% (BREACH)│  OK (1 of 3)     │
│  85% (BREACH)│  88% (BREACH)│  82% (BREACH)│  ALARM (3 of 3)  │
└──────────────┴──────────────┴──────────────┴──────────────────┘
```

### Configuration Options

```bash
# M out of N evaluation
# Alarm if 2 out of 3 evaluation periods breach threshold
aws cloudwatch put-metric-alarm \
    --alarm-name "HighCPU" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 60 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 3 \
    --datapoints-to-alarm 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

---

## Missing Data Treatment

How alarms behave when data points are missing:

| Treatment | Behavior |
|-----------|----------|
| **missing** | Maintains current state |
| **notBreaching** | Treats missing data as within threshold |
| **breaching** | Treats missing data as breaching threshold |
| **ignore** | Ignores missing data points in evaluation |

```bash
# Set missing data treatment
aws cloudwatch put-metric-alarm \
    --alarm-name "HighCPU" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 3 \
    --treat-missing-data notBreaching \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### When to Use Each Treatment

| Scenario | Recommended Treatment |
|----------|----------------------|
| Stopped instance monitoring | notBreaching |
| Critical health check | breaching |
| Sporadic metrics | ignore |
| Continuous stream expected | missing |

---

## Alarm Actions

### Supported Actions

| Action Type | Description |
|-------------|-------------|
| SNS | Send notifications to SNS topic |
| EC2 | Stop, terminate, reboot, or recover instance |
| Auto Scaling | Scale out or scale in |
| Systems Manager | Run automation or incident management |
| Lambda | Trigger Lambda function (via SNS) |

### EC2 Actions

```bash
# Auto-recover instance alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "AutoRecover-Instance" \
    --alarm-description "Recover instance on status check failure" \
    --metric-name StatusCheckFailed_System \
    --namespace AWS/EC2 \
    --statistic Maximum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:automate:us-east-1:ec2:recover

# Stop instance when idle
aws cloudwatch put-metric-alarm \
    --alarm-name "StopIdleInstance" \
    --alarm-description "Stop instance when CPU is idle" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 3600 \
    --threshold 5 \
    --comparison-operator LessThanThreshold \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --evaluation-periods 4 \
    --alarm-actions arn:aws:automate:us-east-1:ec2:stop
```

### Auto Scaling Actions

```bash
# Scale out alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ScaleOut-WebApp" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 70 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=AutoScalingGroupName,Value=my-asg \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:autoscaling:us-east-1:123456789012:scalingPolicy:abc123:autoScalingGroupName/my-asg:policyName/scale-out

# Scale in alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "ScaleIn-WebApp" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 30 \
    --comparison-operator LessThanThreshold \
    --dimensions Name=AutoScalingGroupName,Value=my-asg \
    --evaluation-periods 5 \
    --alarm-actions arn:aws:autoscaling:us-east-1:123456789012:scalingPolicy:def456:autoScalingGroupName/my-asg:policyName/scale-in
```

---

## Composite Alarms

### Alarm Rule Syntax

```
# Operators
AND  - All conditions must be true
OR   - Any condition must be true
NOT  - Inverse of condition
()   - Grouping

# Functions
ALARM(alarm-name)   - True if alarm is in ALARM state
OK(alarm-name)      - True if alarm is in OK state
INSUFFICIENT_DATA(alarm-name) - True if in INSUFFICIENT_DATA state
```

### Complex Composite Alarm Examples

```bash
# Example 1: AND condition
aws cloudwatch put-composite-alarm \
    --alarm-name "CriticalDatabase" \
    --alarm-rule "ALARM(HighCPU-RDS) AND ALARM(HighConnections-RDS)"

# Example 2: OR condition
aws cloudwatch put-composite-alarm \
    --alarm-name "AnyServerIssue" \
    --alarm-rule "ALARM(HighCPU-Web1) OR ALARM(HighCPU-Web2) OR ALARM(HighCPU-Web3)"

# Example 3: Complex logic
aws cloudwatch put-composite-alarm \
    --alarm-name "ApplicationHealth" \
    --alarm-rule "(ALARM(HighErrorRate) OR ALARM(HighLatency)) AND NOT ALARM(MaintenanceMode)"

# Example 4: Nested conditions
aws cloudwatch put-composite-alarm \
    --alarm-name "InfrastructureCritical" \
    --alarm-rule "(ALARM(WebTier-Critical) AND ALARM(AppTier-Critical)) OR ALARM(DatabaseTier-Critical)"
```

### Composite Alarm for Alert Suppression

```bash
# Suppress alerts during maintenance
aws cloudwatch put-metric-alarm \
    --alarm-name "MaintenanceWindow" \
    --metric-name MaintenanceMode \
    --namespace Custom/Operations \
    --statistic Maximum \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1

# Composite alarm that respects maintenance
aws cloudwatch put-composite-alarm \
    --alarm-name "ProductionAlert" \
    --alarm-rule "ALARM(HighErrorRate) AND NOT ALARM(MaintenanceWindow)" \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:production-alerts
```

---

## Anomaly Detection

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Anomaly Detection Process                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Historical Data    ML Model Training     Expected Band     Current Value   │
│  ┌────────────┐    ┌────────────────┐    ┌─────────────┐   ┌────────────┐  │
│  │ 2 weeks of │───►│ Pattern        │───►│ Upper Bound │   │            │  │
│  │ metric     │    │ Recognition    │    │ ─────────── │   │  90% ●     │  │
│  │ history    │    │                │    │ Expected    │   │            │  │
│  │            │    │ Daily/Weekly   │    │ ─────────── │   │            │  │
│  │            │    │ Seasonality    │    │ Lower Bound │   │            │  │
│  └────────────┘    └────────────────┘    └─────────────┘   └────────────┘  │
│                                                                    │        │
│                                                                    │        │
│                                                       ┌────────────▼──────┐ │
│                                                       │ Is 90% within    │ │
│                                                       │ expected band?   │ │
│                                                       └────────────┬─────┘ │
│                                                                    │        │
│                                           ┌─────────┐      ┌──────▼──────┐ │
│                                           │   YES   │      │     NO      │ │
│                                           │   OK    │      │   ALARM     │ │
│                                           └─────────┘      └─────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuring Anomaly Detection

```bash
# Create anomaly detection model
aws cloudwatch put-anomaly-detector \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --stat Average \
    --configuration '{
        "ExcludedTimeRanges": [
            {
                "StartTime": "2024-01-15T00:00:00Z",
                "EndTime": "2024-01-15T06:00:00Z"
            }
        ]
    }'

# Create alarm using anomaly detection
aws cloudwatch put-metric-alarm \
    --alarm-name "AnomalyCPU" \
    --alarm-description "CPU anomaly detection alarm" \
    --metrics '[
        {
            "Id": "m1",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/EC2",
                    "MetricName": "CPUUtilization",
                    "Dimensions": [
                        {"Name": "InstanceId", "Value": "i-1234567890abcdef0"}
                    ]
                },
                "Period": 300,
                "Stat": "Average"
            },
            "ReturnData": true
        },
        {
            "Id": "ad1",
            "Expression": "ANOMALY_DETECTION_BAND(m1, 2)",
            "Label": "CPUAnomaly",
            "ReturnData": true
        }
    ]' \
    --threshold-metric-id ad1 \
    --comparison-operator LessThanLowerOrGreaterThanUpperThreshold \
    --evaluation-periods 3 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### Band Width Adjustment

```
ANOMALY_DETECTION_BAND(metric, width)

Width Examples:
- 1 = Tight band (more sensitive, more alarms)
- 2 = Standard band (balanced)
- 3 = Wide band (less sensitive, fewer alarms)
- 5 = Very wide band (only major anomalies)
```

---

## CloudFormation Templates

### Basic Alarm

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudWatch Alarm Examples

Parameters:
  InstanceId:
    Type: AWS::EC2::Instance::Id
  AlertEmail:
    Type: String

Resources:
  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: cloudwatch-alerts
      Subscription:
        - Protocol: email
          Endpoint: !Ref AlertEmail

  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighCPU
      AlarmDescription: CPU utilization exceeds 80%
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
      TreatMissingData: notBreaching
```

### Composite Alarm with Child Alarms

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Composite Alarm Setup

Resources:
  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighCPU-Child
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

  HighMemoryAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: HighMemory-Child
      MetricName: mem_used_percent
      Namespace: CWAgent
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: InstanceId
          Value: !Ref InstanceId

  CriticalHealthAlarm:
    Type: AWS::CloudWatch::CompositeAlarm
    Properties:
      AlarmName: CriticalServerHealth
      AlarmDescription: Both CPU and Memory are critically high
      AlarmRule: !Sub "ALARM(${HighCPUAlarm}) AND ALARM(${HighMemoryAlarm})"
      AlarmActions:
        - !Ref CriticalAlertTopic
```

### Anomaly Detection Alarm

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Anomaly Detection Alarm

Resources:
  LatencyAnomalyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: LatencyAnomaly
      AlarmDescription: API latency is anomalous
      Metrics:
        - Id: m1
          MetricStat:
            Metric:
              Namespace: AWS/ApplicationELB
              MetricName: TargetResponseTime
              Dimensions:
                - Name: LoadBalancer
                  Value: !Ref LoadBalancerFullName
            Period: 300
            Stat: Average
          ReturnData: true
        - Id: ad1
          Expression: "ANOMALY_DETECTION_BAND(m1, 2)"
          Label: LatencyAnomaly
          ReturnData: true
      ThresholdMetricId: ad1
      ComparisonOperator: LessThanLowerOrGreaterThanUpperThreshold
      EvaluationPeriods: 3
      AlarmActions:
        - !Ref AlertTopic
```

---

## Common Alarm Patterns

### EC2 Instance Monitoring

```yaml
Resources:
  # CPU Alarm
  CPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${InstanceId}-HighCPU"
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

  # Status Check Alarm
  StatusCheckAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${InstanceId}-StatusCheck"
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
        - !Sub "arn:aws:automate:${AWS::Region}:ec2:recover"
```

### Lambda Function Monitoring

```yaml
Resources:
  # Error Rate Alarm
  LambdaErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${FunctionName}-Errors"
      Metrics:
        - Id: errors
          MetricStat:
            Metric:
              Namespace: AWS/Lambda
              MetricName: Errors
              Dimensions:
                - Name: FunctionName
                  Value: !Ref FunctionName
            Period: 60
            Stat: Sum
          ReturnData: false
        - Id: invocations
          MetricStat:
            Metric:
              Namespace: AWS/Lambda
              MetricName: Invocations
              Dimensions:
                - Name: FunctionName
                  Value: !Ref FunctionName
            Period: 60
            Stat: Sum
          ReturnData: false
        - Id: errorRate
          Expression: "IF(invocations > 0, errors/invocations*100, 0)"
          Label: ErrorRate
          ReturnData: true
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      EvaluationPeriods: 3

  # Duration Alarm
  LambdaDurationAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${FunctionName}-Duration"
      MetricName: Duration
      Namespace: AWS/Lambda
      Statistic: p99
      Period: 300
      EvaluationPeriods: 3
      Threshold: 5000  # 5 seconds
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: FunctionName
          Value: !Ref FunctionName
```

### RDS Database Monitoring

```yaml
Resources:
  # CPU Alarm
  RDSCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${DBInstanceIdentifier}-HighCPU"
      MetricName: CPUUtilization
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 3
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstanceIdentifier

  # Low Storage Alarm
  RDSStorageAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${DBInstanceIdentifier}-LowStorage"
      MetricName: FreeStorageSpace
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 1
      Threshold: 5368709120  # 5 GB in bytes
      ComparisonOperator: LessThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstanceIdentifier

  # High Connections Alarm
  RDSConnectionsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub "${DBInstanceIdentifier}-HighConnections"
      MetricName: DatabaseConnections
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 100
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstanceIdentifier
```

---

## Best Practices

### Alarm Naming Convention

```
# Format: Environment-Service-Resource-Metric-Severity
Production-EC2-WebServer01-CPU-Warning
Production-RDS-MainDB-Storage-Critical
Staging-Lambda-OrderProcessor-Errors-Info

# Or simpler format
HighCPU-WebServer
LowStorage-Database
ErrorRate-API
```

### Reduce Alert Fatigue

1. **Use composite alarms** to correlate related issues
2. **Set appropriate evaluation periods** (not too sensitive)
3. **Configure M-of-N thresholds** for transient spikes
4. **Implement severity levels** (critical, warning, info)
5. **Use anomaly detection** for variable metrics

### Alarm Severity Tiers

```
Tier 1 - Critical (Page immediately):
- Service completely down
- Data loss risk
- Security breach

Tier 2 - High (Alert during business hours):
- Significant performance degradation
- Approaching resource limits
- Elevated error rates

Tier 3 - Medium (Review daily):
- Minor performance issues
- Warning thresholds
- Capacity planning alerts

Tier 4 - Low (Review weekly):
- Cost optimization opportunities
- Trend analysis
- Informational metrics
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Alarm stuck in INSUFFICIENT_DATA | No metrics published | Check metric exists, verify dimensions |
| Too many false positives | Threshold too sensitive | Increase evaluation periods or threshold |
| Alarm not triggering | Wrong comparison operator | Verify operator matches intent |
| Missing notifications | SNS not configured | Check alarm actions and SNS subscriptions |

### Debugging Commands

```bash
# Check alarm state
aws cloudwatch describe-alarms \
    --alarm-names "HighCPU-WebServer" \
    --query 'MetricAlarms[*].[AlarmName,StateValue,StateReason]'

# View alarm history
aws cloudwatch describe-alarm-history \
    --alarm-name "HighCPU-WebServer" \
    --history-item-type StateUpdate \
    --max-records 10

# Verify metric exists
aws cloudwatch list-metrics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0

# Test alarm actions manually
aws cloudwatch set-alarm-state \
    --alarm-name "HighCPU-WebServer" \
    --state-value ALARM \
    --state-reason "Testing alarm actions"
```

---

## Next Steps

Continue to the next sections:
- [04-cloudwatch-logs.md](04-cloudwatch-logs.md) - Log management
- [05-cloudwatch-logs-insights.md](05-cloudwatch-logs-insights.md) - Query logs effectively
