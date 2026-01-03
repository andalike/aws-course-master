# CloudWatch Dashboards

## Introduction

CloudWatch Dashboards provide customizable home pages in the CloudWatch console that you can use to monitor your resources in a single view. You can create dashboards that display metrics, alarms, logs, and text to provide comprehensive operational visibility.

---

## Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CloudWatch Dashboard                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Dashboard: Production-Overview                    [Actions ▼] [Share]   ││
│  │ Time Range: [Last 3 hours ▼]  Auto-refresh: [1 min ▼]                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────┐  ┌─────────────────────────┐                  │
│  │    Line Chart           │  │    Stacked Area         │                  │
│  │    CPU Utilization      │  │    Request Count        │                  │
│  │    ┌─────────────────┐  │  │    ┌─────────────────┐  │                  │
│  │    │  /\    /\       │  │  │    │ ████████████   │  │                  │
│  │    │ /  \  /  \      │  │  │    │ ████████       │  │                  │
│  │    │/    \/    \     │  │  │    │ ████           │  │                  │
│  │    └─────────────────┘  │  │    └─────────────────┘  │                  │
│  └─────────────────────────┘  └─────────────────────────┘                  │
│                                                                              │
│  ┌─────────────────────────┐  ┌─────────────────────────┐                  │
│  │    Number Widget        │  │    Alarm Status         │                  │
│  │                         │  │                         │                  │
│  │    Active Users         │  │    ● HighCPU     OK     │                  │
│  │       1,234             │  │    ● LowStorage  ALARM  │                  │
│  │                         │  │    ● ErrorRate   OK     │                  │
│  └─────────────────────────┘  └─────────────────────────┘                  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │    Logs Insights Widget                                                  ││
│  │    Recent Errors                                                         ││
│  │    ┌─────────────────────────────────────────────────────────────────┐  ││
│  │    │ 10:30:45  ERROR: Connection timeout                             │  ││
│  │    │ 10:28:32  ERROR: Invalid request                                │  ││
│  │    └─────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Widget Types

### 1. Line Chart

Best for showing metric trends over time.

```json
{
    "type": "metric",
    "width": 12,
    "height": 6,
    "properties": {
        "metrics": [
            ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"]
        ],
        "title": "EC2 CPU Utilization",
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "view": "timeSeries"
    }
}
```

### 2. Stacked Area Chart

Shows composition of total over time.

```json
{
    "type": "metric",
    "width": 12,
    "height": 6,
    "properties": {
        "metrics": [
            ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", "app/my-alb/1234567890"],
            [".", "HTTPCode_Target_4XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
        ],
        "title": "HTTP Response Codes",
        "period": 60,
        "stat": "Sum",
        "region": "us-east-1",
        "view": "timeSeries",
        "stacked": true
    }
}
```

### 3. Number Widget

Displays single metric value.

```json
{
    "type": "metric",
    "width": 6,
    "height": 3,
    "properties": {
        "metrics": [
            ["AWS/Lambda", "Invocations", "FunctionName", "my-function"]
        ],
        "title": "Lambda Invocations",
        "period": 3600,
        "stat": "Sum",
        "region": "us-east-1",
        "view": "singleValue"
    }
}
```

### 4. Gauge Widget

Shows current value against a range.

```json
{
    "type": "metric",
    "width": 6,
    "height": 6,
    "properties": {
        "metrics": [
            ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"]
        ],
        "title": "CPU Usage",
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "view": "gauge",
        "yAxis": {
            "left": {
                "min": 0,
                "max": 100
            }
        },
        "annotations": {
            "horizontal": [
                {
                    "color": "#ff0000",
                    "value": 80,
                    "label": "Critical"
                },
                {
                    "color": "#ff9900",
                    "value": 60,
                    "label": "Warning"
                }
            ]
        }
    }
}
```

### 5. Bar Chart

Compare values across categories.

```json
{
    "type": "metric",
    "width": 12,
    "height": 6,
    "properties": {
        "metrics": [
            ["AWS/Lambda", "Invocations", "FunctionName", "function-1"],
            [".", ".", ".", "function-2"],
            [".", ".", ".", "function-3"]
        ],
        "title": "Lambda Invocations by Function",
        "period": 3600,
        "stat": "Sum",
        "region": "us-east-1",
        "view": "bar"
    }
}
```

### 6. Pie Chart

Show proportional distribution.

```json
{
    "type": "metric",
    "width": 6,
    "height": 6,
    "properties": {
        "metrics": [
            ["AWS/Lambda", "Errors", "FunctionName", "function-1"],
            [".", ".", ".", "function-2"],
            [".", ".", ".", "function-3"]
        ],
        "title": "Error Distribution",
        "period": 3600,
        "stat": "Sum",
        "region": "us-east-1",
        "view": "pie"
    }
}
```

### 7. Text Widget

Add documentation and context.

```json
{
    "type": "text",
    "width": 24,
    "height": 2,
    "properties": {
        "markdown": "# Production Dashboard\n\nThis dashboard shows key metrics for the production environment.\n\n**Contacts**: ops@example.com | **Runbook**: [Link](https://wiki.example.com/runbook)"
    }
}
```

### 8. Alarm Status Widget

Show multiple alarm states.

```json
{
    "type": "alarm",
    "width": 6,
    "height": 4,
    "properties": {
        "title": "Critical Alarms",
        "alarms": [
            "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighCPU",
            "arn:aws:cloudwatch:us-east-1:123456789012:alarm:LowStorage",
            "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighErrors"
        ]
    }
}
```

### 9. Logs Insights Widget

Display log query results.

```json
{
    "type": "log",
    "width": 24,
    "height": 6,
    "properties": {
        "title": "Recent Errors",
        "query": "SOURCE '/aws/lambda/my-function'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20",
        "region": "us-east-1",
        "view": "table"
    }
}
```

### 10. Explorer Widget

Dynamic service-based metrics.

```json
{
    "type": "explorer",
    "width": 24,
    "height": 12,
    "properties": {
        "metrics": [
            {
                "metricName": "CPUUtilization",
                "resourceType": "AWS::EC2::Instance",
                "stat": "Average"
            }
        ],
        "aggregateBy": {
            "key": "InstanceType",
            "func": "AVG"
        },
        "labels": [
            {
                "key": "Name",
                "value": "Web-*"
            }
        ],
        "widgetOptions": {
            "legend": {
                "position": "bottom"
            },
            "view": "timeSeries"
        },
        "period": 300
    }
}
```

---

## Creating Dashboards

### AWS Console

1. Navigate to CloudWatch > Dashboards
2. Click "Create dashboard"
3. Enter dashboard name
4. Add widgets by clicking "Add widget"
5. Configure widget type and metrics
6. Arrange widgets by dragging
7. Save dashboard

### AWS CLI

```bash
# Create dashboard
aws cloudwatch put-dashboard \
    --dashboard-name "Production-Overview" \
    --dashboard-body file://dashboard.json

# Get dashboard
aws cloudwatch get-dashboard \
    --dashboard-name "Production-Overview"

# List dashboards
aws cloudwatch list-dashboards

# Delete dashboard
aws cloudwatch delete-dashboards \
    --dashboard-names "Production-Overview"
```

### Complete Dashboard JSON

```json
{
    "widgets": [
        {
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "# Production Environment Dashboard"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 1,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["AWS/EC2", "CPUUtilization", "InstanceId", "i-web1", {"label": "Web Server 1"}],
                    [".", ".", ".", "i-web2", {"label": "Web Server 2"}]
                ],
                "title": "EC2 CPU Utilization",
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "view": "timeSeries",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "max": 100
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 1,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/my-alb/1234567890"]
                ],
                "title": "ALB Request Count",
                "period": 60,
                "stat": "Sum",
                "region": "us-east-1",
                "view": "timeSeries"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 7,
            "width": 6,
            "height": 4,
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Invocations", "FunctionName", "api-handler"]
                ],
                "title": "Lambda Invocations",
                "period": 3600,
                "stat": "Sum",
                "region": "us-east-1",
                "view": "singleValue"
            }
        },
        {
            "type": "metric",
            "x": 6,
            "y": 7,
            "width": 6,
            "height": 4,
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Duration", "FunctionName", "api-handler"]
                ],
                "title": "Lambda Duration (p99)",
                "period": 300,
                "stat": "p99",
                "region": "us-east-1",
                "view": "singleValue"
            }
        },
        {
            "type": "alarm",
            "x": 12,
            "y": 7,
            "width": 12,
            "height": 4,
            "properties": {
                "title": "Alarm Status",
                "alarms": [
                    "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighCPU-Web",
                    "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighErrors-API",
                    "arn:aws:cloudwatch:us-east-1:123456789012:alarm:LowStorage-RDS"
                ]
            }
        },
        {
            "type": "log",
            "x": 0,
            "y": 11,
            "width": 24,
            "height": 6,
            "properties": {
                "title": "Recent Application Errors",
                "query": "SOURCE '/aws/lambda/api-handler'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 10",
                "region": "us-east-1",
                "view": "table"
            }
        }
    ]
}
```

---

## CloudFormation Dashboard

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudWatch Dashboard

Parameters:
  Environment:
    Type: String
    Default: Production
  InstanceId:
    Type: AWS::EC2::Instance::Id
  FunctionName:
    Type: String

Resources:
  OperationalDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub ${Environment}-Dashboard
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 1,
              "properties": {
                "markdown": "# ${Environment} Environment Dashboard\n\nMonitoring key infrastructure metrics"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 1,
              "width": 12,
              "height": 6,
              "properties": {
                "metrics": [
                  ["AWS/EC2", "CPUUtilization", "InstanceId", "${InstanceId}"]
                ],
                "title": "EC2 CPU Utilization",
                "period": 300,
                "stat": "Average",
                "region": "${AWS::Region}",
                "view": "timeSeries",
                "yAxis": {
                  "left": {
                    "min": 0,
                    "max": 100
                  }
                }
              }
            },
            {
              "type": "metric",
              "x": 12,
              "y": 1,
              "width": 12,
              "height": 6,
              "properties": {
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "${FunctionName}"],
                  [".", "Errors", ".", "."]
                ],
                "title": "Lambda Metrics",
                "period": 300,
                "stat": "Sum",
                "region": "${AWS::Region}",
                "view": "timeSeries"
              }
            }
          ]
        }
```

---

## Automatic Dashboards

AWS provides pre-built dashboards for services.

### Accessing Automatic Dashboards

1. Navigate to CloudWatch
2. Click "Dashboards" in the left menu
3. Select "Automatic dashboards"
4. Choose a service (EC2, Lambda, ECS, etc.)

### Available Automatic Dashboards

| Service | Metrics Included |
|---------|-----------------|
| EC2 | CPU, Network, Disk, Status Checks |
| Lambda | Invocations, Duration, Errors, Throttles |
| RDS | CPU, Connections, Storage, Latency |
| ECS | CPU, Memory, Task Count |
| API Gateway | Requests, Latency, Errors |
| DynamoDB | Read/Write Capacity, Throttling |

---

## Cross-Account Dashboards

### Enable Cross-Account Sharing

```bash
# In monitoring account, enable cross-account
aws cloudwatch put-dashboard \
    --dashboard-name "MultiAccount-Dashboard" \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/EC2", "CPUUtilization", "InstanceId", "i-prod1", {"accountId": "111111111111"}],
                        ["...", "i-staging1", {"accountId": "222222222222"}]
                    ],
                    "title": "Cross-Account CPU",
                    "region": "us-east-1"
                }
            }
        ]
    }'
```

### Cross-Account IAM Setup

In source accounts:
```yaml
# IAM role for CloudWatch cross-account access
CloudWatchCrossAccountRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: CloudWatch-CrossAccountSharingRole
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            AWS: arn:aws:iam::MONITORING_ACCOUNT:root
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess
```

---

## Dashboard Sharing

### Share via Link

1. Open dashboard
2. Click "Actions" > "Share dashboard"
3. Enable public sharing or use SSO
4. Copy shareable link

### Dashboard Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudwatch:GetDashboard",
                "cloudwatch:ListDashboards"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Advanced Widget Configurations

### Metric Math in Dashboard

```json
{
    "type": "metric",
    "properties": {
        "metrics": [
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "app/my-alb/123", {"id": "errors", "visible": false}],
            [".", "RequestCount", ".", ".", {"id": "requests", "visible": false}],
            [{"expression": "(errors/requests)*100", "label": "Error Rate %", "id": "errorRate"}]
        ],
        "title": "Error Rate",
        "view": "timeSeries",
        "period": 60
    }
}
```

### Annotations

```json
{
    "type": "metric",
    "properties": {
        "metrics": [
            ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"]
        ],
        "annotations": {
            "horizontal": [
                {
                    "label": "Critical",
                    "value": 90,
                    "color": "#ff0000"
                },
                {
                    "label": "Warning",
                    "value": 70,
                    "color": "#ff9900"
                }
            ],
            "vertical": [
                {
                    "label": "Deployment",
                    "value": "2024-01-15T10:30:00Z",
                    "color": "#0000ff"
                }
            ]
        }
    }
}
```

### Alarm Annotations

```json
{
    "type": "metric",
    "properties": {
        "metrics": [
            ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"]
        ],
        "annotations": {
            "alarms": [
                "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighCPU"
            ]
        }
    }
}
```

### Dynamic Labels

```json
{
    "type": "metric",
    "properties": {
        "metrics": [
            ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0",
             {"label": "${PROP('Dim.InstanceId')} - ${AVG} avg, ${MAX} max"}]
        ]
    }
}
```

Available dynamic labels:
- `${LABEL}` - Default label
- `${AVG}` - Average value
- `${MIN}` - Minimum value
- `${MAX}` - Maximum value
- `${SUM}` - Sum value
- `${PROP('DimensionName')}` - Dimension value

---

## Dashboard Variables (Parameters)

Create parameterized dashboards:

```json
{
    "variables": [
        {
            "type": "property",
            "property": "InstanceId",
            "inputType": "select",
            "id": "instance",
            "label": "Instance",
            "defaultValue": "i-1234567890abcdef0",
            "visible": true,
            "search": "AWS/EC2 CPUUtilization",
            "populateFrom": "InstanceId"
        }
    ],
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/EC2", "CPUUtilization", "InstanceId", "${instance}"]
                ],
                "title": "CPU for ${instance}"
            }
        }
    ]
}
```

---

## Best Practices

### Dashboard Organization

1. **Executive Dashboard**: High-level business metrics
2. **Operations Dashboard**: Infrastructure health
3. **Application Dashboard**: Application-specific metrics
4. **Incident Dashboard**: Alarms and critical indicators

### Widget Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Row 0: Header/Title (text widget)                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Row 1-6: Key Metrics (line charts, most important)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Row 7-10: Summary Numbers (single value widgets)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Row 11-14: Alarm Status                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Row 15+: Logs and Details                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Naming Conventions

```
# Environment-based
Production-Overview
Staging-API-Metrics
Development-Lambda-Functions

# Team-based
Platform-Infrastructure
Backend-Services
Frontend-Performance

# Service-based
OrderService-Dashboard
PaymentGateway-Monitoring
UserAuthentication-Metrics
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| No data in widget | Verify metric exists, check time range |
| Widget shows error | Check metric name, dimensions, region |
| Cross-account not working | Verify IAM roles and policies |
| Dashboard not loading | Check browser console, verify permissions |

### Debugging

```bash
# Verify dashboard exists
aws cloudwatch list-dashboards

# Get dashboard definition
aws cloudwatch get-dashboard --dashboard-name "Production-Overview"

# Verify metrics exist
aws cloudwatch list-metrics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization
```

---

## Next Steps

Continue to the next sections:
- [07-cloudwatch-agent.md](07-cloudwatch-agent.md) - Collect custom metrics for dashboards
- [12-hands-on-labs.md](12-hands-on-labs.md) - Build a complete dashboard
