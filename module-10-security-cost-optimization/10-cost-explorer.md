# AWS Cost Explorer and Cost Optimization

## Introduction

AWS Cost Explorer is a powerful tool for visualizing, understanding, and managing your AWS costs and usage over time. Combined with AWS Budgets, Cost and Usage Reports, and optimization tools, it forms a comprehensive cost management suite.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS Cost Management Overview                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                      Cost Management Tools                           │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌────────────┐  │
│   │ Cost Explorer │  │    Budgets    │  │   Cost &      │  │ Savings    │  │
│   │               │  │               │  │   Usage       │  │ Plans      │  │
│   │ • Visualize   │  │ • Set limits  │  │   Reports     │  │            │  │
│   │ • Analyze     │  │ • Alerts      │  │               │  │ • Commit   │  │
│   │ • Forecast    │  │ • Actions     │  │ • Detailed    │  │ • Save up  │  │
│   │ • Filter      │  │               │  │ • S3 export   │  │   to 72%   │  │
│   └───────────────┘  └───────────────┘  └───────────────┘  └────────────┘  │
│          │                  │                  │                  │        │
│          └──────────────────┴──────────────────┴──────────────────┘        │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    Cost Optimization Actions                         │  │
│   │                                                                      │  │
│   │  • Rightsizing Recommendations      • Reserved Instances             │  │
│   │  • Savings Plans                    • Spot Instances                 │  │
│   │  • Idle Resource Cleanup            • Storage Optimization           │  │
│   │  • Data Transfer Optimization       • Compute Optimizer              │  │
│   │                                                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## AWS Cost Explorer

### Enabling Cost Explorer

```bash
# Cost Explorer must be enabled from the console first
# Navigate to: AWS Billing > Cost Explorer > Enable Cost Explorer

# After enabling (takes up to 24 hours for data to appear)
# You can use the CLI to query costs

# Get cost and usage for last 30 days
aws ce get-cost-and-usage \
    --time-period Start=$(date -d "30 days ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics "BlendedCost" "UnblendedCost" "UsageQuantity"

# Get cost by service
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE
```

### Cost Explorer Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Cost Explorer Dashboard                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Time Range: Last 6 Months              Granularity: Monthly                │
│                                                                             │
│  Cost Trend                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  $50K ┤                                              ╭──────╮       │   │
│  │       │                                        ╭────╯      │       │   │
│  │  $40K ┤                              ╭────────╯            │       │   │
│  │       │                        ╭────╯                      │       │   │
│  │  $30K ┤              ╭────────╯                            ╰───    │   │
│  │       │        ╭────╯                                              │   │
│  │  $20K ┤───────╯                                                    │   │
│  │       │                                                            │   │
│  │  $10K ┤                                                            │   │
│  │       ├──────┬──────┬──────┬──────┬──────┬──────                  │   │
│  │         Aug    Sep    Oct    Nov    Dec    Jan                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Cost by Service (Top 5)                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  EC2                    ████████████████████████████████  45%  $22.5K│   │
│  │  RDS                    ██████████████████                 25%  $12.5K│   │
│  │  S3                     ████████████                       15%  $7.5K│   │
│  │  Lambda                 ██████                             8%   $4K   │   │
│  │  CloudFront             ████                               5%   $2.5K│   │
│  │  Other                  ██                                 2%   $1K   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Cost by Account                        Cost by Region                      │
│  ┌──────────────────────────────┐      ┌──────────────────────────────┐    │
│  │  Production    $35K  (70%)   │      │  us-east-1     $30K  (60%)   │    │
│  │  Development   $10K  (20%)   │      │  eu-west-1     $15K  (30%)   │    │
│  │  Staging       $5K   (10%)   │      │  ap-south-1    $5K   (10%)   │    │
│  └──────────────────────────────┘      └──────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Filtering and Grouping

```bash
# Filter by specific service
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity DAILY \
    --metrics "BlendedCost" \
    --filter '{
        "Dimensions": {
            "Key": "SERVICE",
            "Values": ["Amazon Elastic Compute Cloud - Compute"]
        }
    }'

# Group by linked account and service
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --group-by Type=DIMENSION,Key=LINKED_ACCOUNT Type=DIMENSION,Key=SERVICE

# Filter by tags
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --filter '{
        "Tags": {
            "Key": "Environment",
            "Values": ["Production"]
        }
    }'

# Multiple filters with AND logic
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" \
    --filter '{
        "And": [
            {
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": ["Amazon Elastic Compute Cloud - Compute"]
                }
            },
            {
                "Tags": {
                    "Key": "Environment",
                    "Values": ["Production"]
                }
            }
        ]
    }'
```

### Cost Forecasting

```bash
# Get cost forecast
aws ce get-cost-forecast \
    --time-period Start=$(date +%Y-%m-%d),End=$(date -d "+30 days" +%Y-%m-%d) \
    --metric BLENDED_COST \
    --granularity MONTHLY

# Forecast with prediction interval
aws ce get-cost-forecast \
    --time-period Start=$(date +%Y-%m-%d),End=$(date -d "+90 days" +%Y-%m-%d) \
    --metric BLENDED_COST \
    --granularity MONTHLY \
    --prediction-interval-level 80
```

## AWS Cost and Usage Reports (CUR)

### Setting Up CUR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Cost and Usage Report Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                                                       │
│   │   AWS Billing   │                                                       │
│   │                 │                                                       │
│   │ • Usage data    │────────────────┐                                     │
│   │ • Cost data     │                │                                     │
│   │ • Resource IDs  │                │                                     │
│   └─────────────────┘                │                                     │
│                                      ▼                                     │
│                           ┌─────────────────┐                              │
│                           │   S3 Bucket     │                              │
│                           │                 │                              │
│                           │ • CSV/Parquet   │                              │
│                           │ • Updated daily │                              │
│                           │ • Compressed    │                              │
│                           └────────┬────────┘                              │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                 │
│              ▼                     ▼                     ▼                 │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐         │
│   │     Athena      │   │   QuickSight    │   │    Redshift     │         │
│   │                 │   │                 │   │                 │         │
│   │ • SQL queries   │   │ • Dashboards    │   │ • Data warehouse│         │
│   │ • Ad-hoc        │   │ • Visualize     │   │ • Complex       │         │
│   │   analysis      │   │ • Share         │   │   analysis      │         │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Create CUR via Console

1. Navigate to **Billing Dashboard** > **Cost & Usage Reports**
2. Click **Create report**
3. Configure report settings:
   - Report name
   - Include resource IDs
   - Split cost allocation data
   - Time granularity (Hourly, Daily, Monthly)
   - Report versioning
4. Configure S3 delivery:
   - S3 bucket (with appropriate policy)
   - Report path prefix
   - Compression (GZIP or Parquet)
5. Enable report data integration:
   - Amazon Athena
   - Amazon Redshift
   - Amazon QuickSight

### CUR S3 Bucket Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "billingreports.amazonaws.com"
            },
            "Action": [
                "s3:GetBucketAcl",
                "s3:GetBucketPolicy"
            ],
            "Resource": "arn:aws:s3:::your-cur-bucket",
            "Condition": {
                "StringEquals": {
                    "aws:SourceArn": "arn:aws:cur:us-east-1:123456789012:definition/*",
                    "aws:SourceAccount": "123456789012"
                }
            }
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "billingreports.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::your-cur-bucket/*",
            "Condition": {
                "StringEquals": {
                    "aws:SourceArn": "arn:aws:cur:us-east-1:123456789012:definition/*",
                    "aws:SourceAccount": "123456789012"
                }
            }
        }
    ]
}
```

### Querying CUR with Athena

```sql
-- Create Athena table for CUR (auto-generated by AWS)
-- Sample queries:

-- Total cost by service for current month
SELECT
    line_item_product_code AS service,
    ROUND(SUM(line_item_unblended_cost), 2) AS total_cost
FROM your_cur_database.your_cur_table
WHERE year = '2024' AND month = '01'
GROUP BY line_item_product_code
ORDER BY total_cost DESC
LIMIT 10;

-- Daily spend trend
SELECT
    line_item_usage_start_date AS date,
    ROUND(SUM(line_item_unblended_cost), 2) AS daily_cost
FROM your_cur_database.your_cur_table
WHERE year = '2024' AND month = '01'
GROUP BY line_item_usage_start_date
ORDER BY date;

-- EC2 cost by instance type
SELECT
    product_instance_type,
    ROUND(SUM(line_item_unblended_cost), 2) AS cost,
    SUM(line_item_usage_amount) AS hours
FROM your_cur_database.your_cur_table
WHERE line_item_product_code = 'AmazonEC2'
    AND product_instance_type IS NOT NULL
    AND year = '2024' AND month = '01'
GROUP BY product_instance_type
ORDER BY cost DESC;

-- Cost by cost allocation tag
SELECT
    resource_tags_user_environment AS environment,
    ROUND(SUM(line_item_unblended_cost), 2) AS cost
FROM your_cur_database.your_cur_table
WHERE year = '2024' AND month = '01'
    AND resource_tags_user_environment IS NOT NULL
GROUP BY resource_tags_user_environment
ORDER BY cost DESC;

-- Unused Reserved Instance coverage
SELECT
    reservation_reservation_arn,
    reservation_start_time,
    reservation_end_time,
    ROUND(SUM(reservation_unused_normalized_unit_quantity), 2) AS unused_units,
    ROUND(SUM(reservation_unused_amortized_upfront_fee_for_billing_period), 2) AS unused_cost
FROM your_cur_database.your_cur_table
WHERE reservation_reservation_arn IS NOT NULL
    AND year = '2024' AND month = '01'
GROUP BY 1, 2, 3
HAVING SUM(reservation_unused_normalized_unit_quantity) > 0
ORDER BY unused_cost DESC;

-- Savings Plans utilization
SELECT
    savings_plan_savings_plan_arn,
    ROUND(AVG(savings_plan_used_commitment), 4) AS avg_utilization,
    ROUND(SUM(savings_plan_savings_plan_effective_cost), 2) AS effective_cost,
    ROUND(SUM(savings_plan_total_commitment_to_date), 2) AS total_commitment
FROM your_cur_database.your_cur_table
WHERE savings_plan_savings_plan_arn IS NOT NULL
    AND year = '2024' AND month = '01'
GROUP BY savings_plan_savings_plan_arn;
```

## AWS Budgets

### Budget Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS Budget Types                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Cost Budget                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Monitor spending against a fixed amount                          │   │
│  │  • Track actual vs. budgeted costs                                  │   │
│  │  • Set thresholds for alerts (e.g., 80%, 100%, 120%)                │   │
│  │  • Filter by service, account, tag, etc.                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Usage Budget                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Monitor usage in specific units (hours, GB, requests)            │   │
│  │  • Track EC2 hours, S3 storage, Lambda invocations                  │   │
│  │  • Useful for capacity planning                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Reservation Budget                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Track Reserved Instance utilization                              │   │
│  │  • Monitor RI coverage across resources                             │   │
│  │  • Alert when RIs are underutilized                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Savings Plans Budget                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Track Savings Plans utilization                                  │   │
│  │  • Monitor coverage across compute resources                        │   │
│  │  • Ensure maximum savings                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Creating Budgets

```bash
# Create a monthly cost budget
aws budgets create-budget \
    --account-id 123456789012 \
    --budget '{
        "BudgetName": "Monthly-AWS-Budget",
        "BudgetLimit": {
            "Amount": "5000",
            "Unit": "USD"
        },
        "BudgetType": "COST",
        "TimeUnit": "MONTHLY",
        "CostFilters": {},
        "CostTypes": {
            "IncludeTax": true,
            "IncludeSubscription": true,
            "UseBlended": false,
            "IncludeRefund": false,
            "IncludeCredit": false,
            "IncludeUpfront": true,
            "IncludeRecurring": true,
            "IncludeOtherSubscription": true,
            "IncludeSupport": true,
            "IncludeDiscount": true,
            "UseAmortized": false
        }
    }' \
    --notifications-with-subscribers '[
        {
            "Notification": {
                "NotificationType": "ACTUAL",
                "ComparisonOperator": "GREATER_THAN",
                "Threshold": 80,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "SubscriptionType": "EMAIL",
                    "Address": "finance@example.com"
                }
            ]
        },
        {
            "Notification": {
                "NotificationType": "ACTUAL",
                "ComparisonOperator": "GREATER_THAN",
                "Threshold": 100,
                "ThresholdType": "PERCENTAGE"
            },
            "Subscribers": [
                {
                    "SubscriptionType": "EMAIL",
                    "Address": "finance@example.com"
                },
                {
                    "SubscriptionType": "SNS",
                    "Address": "arn:aws:sns:us-east-1:123456789012:budget-alerts"
                }
            ]
        }
    ]'

# Create budget for specific service
aws budgets create-budget \
    --account-id 123456789012 \
    --budget '{
        "BudgetName": "EC2-Monthly-Budget",
        "BudgetLimit": {
            "Amount": "2000",
            "Unit": "USD"
        },
        "BudgetType": "COST",
        "TimeUnit": "MONTHLY",
        "CostFilters": {
            "Service": ["Amazon Elastic Compute Cloud - Compute"]
        }
    }'

# Create budget for specific tag
aws budgets create-budget \
    --account-id 123456789012 \
    --budget '{
        "BudgetName": "Production-Environment-Budget",
        "BudgetLimit": {
            "Amount": "10000",
            "Unit": "USD"
        },
        "BudgetType": "COST",
        "TimeUnit": "MONTHLY",
        "CostFilters": {
            "TagKeyValue": ["user:Environment$Production"]
        }
    }'
```

### Budget Actions

```bash
# Create budget with automatic actions
aws budgets create-budget-action \
    --account-id 123456789012 \
    --budget-name "Production-Budget" \
    --notification-type ACTUAL \
    --action-type APPLY_IAM_POLICY \
    --action-threshold '{
        "ActionThresholdValue": 100,
        "ActionThresholdType": "PERCENTAGE"
    }' \
    --definition '{
        "IamActionDefinition": {
            "PolicyArn": "arn:aws:iam::123456789012:policy/DenyEC2LaunchPolicy",
            "Roles": ["DeveloperRole"],
            "Groups": ["Developers"]
        }
    }' \
    --execution-role-arn "arn:aws:iam::123456789012:role/BudgetActionRole" \
    --approval-model AUTOMATIC \
    --subscribers '[
        {
            "SubscriptionType": "EMAIL",
            "Address": "admin@example.com"
        }
    ]'
```

### CloudFormation Budget Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS Budgets Configuration'

Parameters:
  MonthlyBudgetAmount:
    Type: Number
    Default: 5000
    Description: 'Monthly budget limit in USD'

  AlertEmail:
    Type: String
    Description: 'Email for budget alerts'

Resources:
  # Monthly Cost Budget
  MonthlyCostBudget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetName: 'Monthly-Cost-Budget'
        BudgetLimit:
          Amount: !Ref MonthlyBudgetAmount
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostTypes:
          IncludeTax: true
          IncludeSubscription: true
          UseBlended: false
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 50
            ThresholdType: PERCENTAGE
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref AlertEmail
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 80
            ThresholdType: PERCENTAGE
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref AlertEmail
            - SubscriptionType: SNS
              Address: !Ref BudgetAlertTopic
        - Notification:
            NotificationType: FORECASTED
            ComparisonOperator: GREATER_THAN
            Threshold: 100
            ThresholdType: PERCENTAGE
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref AlertEmail

  # EC2 Specific Budget
  EC2Budget:
    Type: AWS::Budgets::Budget
    Properties:
      Budget:
        BudgetName: 'EC2-Monthly-Budget'
        BudgetLimit:
          Amount: 2000
          Unit: USD
        TimeUnit: MONTHLY
        BudgetType: COST
        CostFilters:
          Service:
            - Amazon Elastic Compute Cloud - Compute
      NotificationsWithSubscribers:
        - Notification:
            NotificationType: ACTUAL
            ComparisonOperator: GREATER_THAN
            Threshold: 90
            ThresholdType: PERCENTAGE
          Subscribers:
            - SubscriptionType: EMAIL
              Address: !Ref AlertEmail

  # SNS Topic for Alerts
  BudgetAlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: budget-alerts
      KmsMasterKeyId: alias/aws/sns

  BudgetAlertSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref BudgetAlertTopic
      Protocol: email
      Endpoint: !Ref AlertEmail

Outputs:
  BudgetName:
    Description: 'Budget Name'
    Value: !Ref MonthlyCostBudget

  SNSTopicArn:
    Description: 'SNS Topic for alerts'
    Value: !Ref BudgetAlertTopic
```

## Rightsizing Recommendations

### Understanding Rightsizing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Rightsizing Recommendations                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  What is Rightsizing?                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Rightsizing = Matching instance size to actual workload needs      │   │
│  │                                                                     │   │
│  │  Current Instance: m5.2xlarge ($0.384/hr)                           │   │
│  │  ┌───────────────────────────────────────────────────────────┐     │   │
│  │  │  CPU Utilization: ████░░░░░░░░░░░░░░░░  20%               │     │   │
│  │  │  Memory Usage:    ██████░░░░░░░░░░░░░░  30%               │     │   │
│  │  │  Network I/O:     ███░░░░░░░░░░░░░░░░░  15%               │     │   │
│  │  └───────────────────────────────────────────────────────────┘     │   │
│  │                                                                     │   │
│  │  Recommendation: m5.large ($0.096/hr)                               │   │
│  │  ┌───────────────────────────────────────────────────────────┐     │   │
│  │  │  Estimated CPU:   ████████████████░░░░  80%               │     │   │
│  │  │  Estimated Mem:   ████████████████████  100%              │     │   │
│  │  │  Monthly Savings: $207.36 (75% reduction)                 │     │   │
│  │  └───────────────────────────────────────────────────────────┘     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Recommendation Types:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Downsize: Move to smaller instance type                          │   │
│  │  • Upgrade: Move to newer generation (better price/performance)     │   │
│  │  • Terminate: Idle instances with no activity                       │   │
│  │  • Change family: Move to specialized family (compute, memory)      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Getting Rightsizing Recommendations

```bash
# Get rightsizing recommendations
aws ce get-rightsizing-recommendation \
    --service "AmazonEC2" \
    --configuration '{
        "RecommendationTarget": "SAME_INSTANCE_FAMILY",
        "BenefitsConsidered": true
    }'

# Get recommendations across instance families
aws ce get-rightsizing-recommendation \
    --service "AmazonEC2" \
    --configuration '{
        "RecommendationTarget": "CROSS_INSTANCE_FAMILY",
        "BenefitsConsidered": true
    }'
```

### AWS Compute Optimizer

```bash
# Enable Compute Optimizer
aws compute-optimizer update-enrollment-status \
    --status Active \
    --include-member-accounts

# Get EC2 instance recommendations
aws compute-optimizer get-ec2-instance-recommendations \
    --instance-arns "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"

# Get Auto Scaling group recommendations
aws compute-optimizer get-auto-scaling-group-recommendations

# Get EBS volume recommendations
aws compute-optimizer get-ebs-volume-recommendations

# Get Lambda function recommendations
aws compute-optimizer get-lambda-function-recommendations

# Export recommendations to S3
aws compute-optimizer export-ec2-instance-recommendations \
    --s3-destination-config '{
        "bucket": "compute-optimizer-exports",
        "keyPrefix": "ec2-recommendations/"
    }'
```

## Reserved Instances and Savings Plans

### Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              Reserved Instances vs Savings Plans                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Reserved Instances                    Savings Plans                        │
│  ─────────────────────                 ──────────────                       │
│                                                                             │
│  Commitment:                           Commitment:                          │
│  • Specific instance type              • $/hour commitment                  │
│  • Specific region/AZ                  • Flexible usage                     │
│  • 1 or 3 year term                    • 1 or 3 year term                   │
│                                                                             │
│  Flexibility:                          Flexibility:                         │
│  ┌─────────────────────────┐          ┌─────────────────────────┐          │
│  │ Standard RI:            │          │ Compute Savings Plan:   │          │
│  │ • Cannot change         │          │ • Any EC2 instance      │          │
│  │   instance family       │          │ • Any region            │          │
│  │ • Modify size within    │          │ • Fargate               │          │
│  │   same family           │          │ • Lambda                │          │
│  │                         │          │                         │          │
│  │ Convertible RI:         │          │ EC2 Instance Plan:      │          │
│  │ • Can change instance   │          │ • Specific instance     │          │
│  │   family                │          │   family                │          │
│  │ • Lower discount        │          │ • Specific region       │          │
│  │                         │          │ • Higher discount       │          │
│  └─────────────────────────┘          └─────────────────────────┘          │
│                                                                             │
│  Discount Comparison (3-year, all upfront):                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Option                  │  Discount  │  Flexibility              │   │
│  │  ────────────────────────┼────────────┼───────────────────────────│   │
│  │  Standard RI             │  Up to 72% │  Lowest                   │   │
│  │  Convertible RI          │  Up to 66% │  Medium                   │   │
│  │  EC2 Instance SP         │  Up to 72% │  Medium-High              │   │
│  │  Compute SP              │  Up to 66% │  Highest                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Savings Plans Recommendations

```bash
# Get Savings Plans recommendations
aws ce get-savings-plans-purchase-recommendation \
    --savings-plans-type COMPUTE_SP \
    --term-in-years THREE_YEARS \
    --payment-option NO_UPFRONT \
    --lookback-period-in-days SIXTY_DAYS

# Get recommendations for EC2 Instance Savings Plans
aws ce get-savings-plans-purchase-recommendation \
    --savings-plans-type EC2_INSTANCE_SP \
    --term-in-years ONE_YEAR \
    --payment-option ALL_UPFRONT \
    --lookback-period-in-days THIRTY_DAYS

# Check Savings Plans utilization
aws ce get-savings-plans-utilization \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY

# Check Savings Plans coverage
aws ce get-savings-plans-coverage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY
```

### Reserved Instance Recommendations

```bash
# Get RI recommendations
aws ce get-reservation-purchase-recommendation \
    --service "Amazon Elastic Compute Cloud - Compute" \
    --term-in-years THREE_YEARS \
    --payment-option ALL_UPFRONT \
    --lookback-period-in-days SIXTY_DAYS

# Check RI utilization
aws ce get-reservation-utilization \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY

# Check RI coverage
aws ce get-reservation-coverage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --group-by Type=DIMENSION,Key=SERVICE
```

## Cost Optimization Strategies

### Cost Optimization Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Cost Optimization Framework                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Visibility & Governance                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Enable Cost Explorer and detailed billing                        │   │
│  │  • Implement cost allocation tags                                   │   │
│  │  • Set up AWS Organizations with consolidated billing               │   │
│  │  • Create budgets and alerts                                        │   │
│  │  • Use AWS Cost Anomaly Detection                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. Right Size Resources                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Use Compute Optimizer recommendations                            │   │
│  │  • Implement Auto Scaling                                           │   │
│  │  • Review underutilized resources                                   │   │
│  │  • Choose appropriate storage classes                               │   │
│  │  • Optimize database instance sizes                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. Increase Elasticity                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Shut down non-production after hours                             │   │
│  │  • Use Auto Scaling for variable workloads                          │   │
│  │  • Implement Lambda for intermittent processing                     │   │
│  │  • Use Spot Instances for fault-tolerant workloads                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. Choose Right Pricing Model                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Workload Type          │  Recommended Pricing                      │   │
│  │  ─────────────────────────────────────────────────────              │   │
│  │  Steady-state           │  Reserved Instances / Savings Plans       │   │
│  │  Variable               │  On-Demand + Auto Scaling                 │   │
│  │  Fault-tolerant batch   │  Spot Instances                           │   │
│  │  Short-term projects    │  On-Demand                                │   │
│  │  Dev/Test               │  Spot + Scheduled shutdown                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  5. Optimize Data Transfer                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Use VPC endpoints for AWS service access                         │   │
│  │  • Implement CloudFront for content delivery                        │   │
│  │  • Choose same-AZ for high-throughput workloads                     │   │
│  │  • Use S3 Transfer Acceleration when needed                         │   │
│  │  • Compress data before transfer                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  6. Optimize Storage                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Use S3 Intelligent-Tiering                                       │   │
│  │  • Implement S3 Lifecycle policies                                  │   │
│  │  • Delete unused EBS volumes and snapshots                          │   │
│  │  • Use gp3 instead of gp2 for EBS                                   │   │
│  │  • Archive infrequently accessed data to Glacier                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Quick Wins Script

```bash
#!/bin/bash
# AWS Cost Optimization Quick Wins

echo "=== AWS Cost Optimization Analysis ==="

echo -e "\n1. Finding unattached EBS volumes..."
aws ec2 describe-volumes \
    --filters Name=status,Values=available \
    --query 'Volumes[].{VolumeId:VolumeId,Size:Size,Type:VolumeType,Created:CreateTime}' \
    --output table

echo -e "\n2. Finding stopped EC2 instances..."
aws ec2 describe-instances \
    --filters Name=instance-state-name,Values=stopped \
    --query 'Reservations[].Instances[].{InstanceId:InstanceId,Type:InstanceType,Name:Tags[?Key==`Name`].Value|[0],StoppedSince:StateTransitionReason}' \
    --output table

echo -e "\n3. Finding unused Elastic IPs..."
aws ec2 describe-addresses \
    --query 'Addresses[?InstanceId==`null`].{PublicIp:PublicIp,AllocationId:AllocationId}' \
    --output table

echo -e "\n4. Finding idle load balancers..."
aws elbv2 describe-load-balancers \
    --query 'LoadBalancers[].{Name:LoadBalancerName,ARN:LoadBalancerArn}' \
    --output table

echo -e "\n5. Finding old EBS snapshots (>90 days)..."
NINETY_DAYS_AGO=$(date -d "90 days ago" +%Y-%m-%d)
aws ec2 describe-snapshots \
    --owner-ids self \
    --query "Snapshots[?StartTime<='${NINETY_DAYS_AGO}'].{SnapshotId:SnapshotId,Size:VolumeSize,StartTime:StartTime}" \
    --output table

echo -e "\n6. Checking for gp2 volumes (should upgrade to gp3)..."
aws ec2 describe-volumes \
    --filters Name=volume-type,Values=gp2 \
    --query 'Volumes[].{VolumeId:VolumeId,Size:Size,IOPS:Iops}' \
    --output table

echo -e "\n7. Finding NAT Gateways (expensive - consider alternatives)..."
aws ec2 describe-nat-gateways \
    --query 'NatGateways[?State==`available`].{NatGatewayId:NatGatewayId,SubnetId:SubnetId,VpcId:VpcId}' \
    --output table

echo -e "\n8. Checking S3 bucket sizes..."
for bucket in $(aws s3api list-buckets --query 'Buckets[].Name' --output text); do
    SIZE=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/S3 \
        --metric-name BucketSizeBytes \
        --dimensions Name=BucketName,Value=$bucket Name=StorageType,Value=StandardStorage \
        --start-time $(date -d "1 day ago" -u +%Y-%m-%dT%H:%M:%SZ) \
        --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
        --period 86400 \
        --statistics Average \
        --query 'Datapoints[0].Average' \
        --output text 2>/dev/null)

    if [ "$SIZE" != "None" ] && [ -n "$SIZE" ]; then
        SIZE_GB=$(echo "scale=2; $SIZE / 1073741824" | bc)
        echo "$bucket: ${SIZE_GB} GB"
    fi
done

echo -e "\n=== Analysis Complete ==="
```

## Hands-on Setup

### Complete Cost Management Setup

```bash
#!/bin/bash
# Complete AWS Cost Management Setup

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
EMAIL="finance@example.com"

echo "=== Setting up AWS Cost Management ==="

# 1. Create S3 bucket for CUR
echo "1. Creating S3 bucket for Cost and Usage Reports..."
CUR_BUCKET="aws-cur-${ACCOUNT_ID}"

aws s3 mb s3://${CUR_BUCKET} --region us-east-1

# Apply bucket policy for CUR
aws s3api put-bucket-policy \
    --bucket ${CUR_BUCKET} \
    --policy "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [
            {
                \"Effect\": \"Allow\",
                \"Principal\": {
                    \"Service\": \"billingreports.amazonaws.com\"
                },
                \"Action\": [
                    \"s3:GetBucketAcl\",
                    \"s3:GetBucketPolicy\"
                ],
                \"Resource\": \"arn:aws:s3:::${CUR_BUCKET}\",
                \"Condition\": {
                    \"StringEquals\": {
                        \"aws:SourceAccount\": \"${ACCOUNT_ID}\"
                    }
                }
            },
            {
                \"Effect\": \"Allow\",
                \"Principal\": {
                    \"Service\": \"billingreports.amazonaws.com\"
                },
                \"Action\": \"s3:PutObject\",
                \"Resource\": \"arn:aws:s3:::${CUR_BUCKET}/*\",
                \"Condition\": {
                    \"StringEquals\": {
                        \"aws:SourceAccount\": \"${ACCOUNT_ID}\"
                    }
                }
            }
        ]
    }"

# 2. Create SNS topic for budget alerts
echo "2. Creating SNS topic for budget alerts..."
TOPIC_ARN=$(aws sns create-topic --name budget-alerts --query 'TopicArn' --output text)

aws sns subscribe \
    --topic-arn ${TOPIC_ARN} \
    --protocol email \
    --notification-endpoint ${EMAIL}

# 3. Create monthly cost budget
echo "3. Creating monthly cost budget..."
aws budgets create-budget \
    --account-id ${ACCOUNT_ID} \
    --budget "{
        \"BudgetName\": \"Monthly-Total-Budget\",
        \"BudgetLimit\": {
            \"Amount\": \"1000\",
            \"Unit\": \"USD\"
        },
        \"BudgetType\": \"COST\",
        \"TimeUnit\": \"MONTHLY\"
    }" \
    --notifications-with-subscribers "[
        {
            \"Notification\": {
                \"NotificationType\": \"ACTUAL\",
                \"ComparisonOperator\": \"GREATER_THAN\",
                \"Threshold\": 50,
                \"ThresholdType\": \"PERCENTAGE\"
            },
            \"Subscribers\": [
                {
                    \"SubscriptionType\": \"EMAIL\",
                    \"Address\": \"${EMAIL}\"
                }
            ]
        },
        {
            \"Notification\": {
                \"NotificationType\": \"ACTUAL\",
                \"ComparisonOperator\": \"GREATER_THAN\",
                \"Threshold\": 80,
                \"ThresholdType\": \"PERCENTAGE\"
            },
            \"Subscribers\": [
                {
                    \"SubscriptionType\": \"SNS\",
                    \"Address\": \"${TOPIC_ARN}\"
                }
            ]
        },
        {
            \"Notification\": {
                \"NotificationType\": \"FORECASTED\",
                \"ComparisonOperator\": \"GREATER_THAN\",
                \"Threshold\": 100,
                \"ThresholdType\": \"PERCENTAGE\"
            },
            \"Subscribers\": [
                {
                    \"SubscriptionType\": \"SNS\",
                    \"Address\": \"${TOPIC_ARN}\"
                }
            ]
        }
    ]"

# 4. Create EC2-specific budget
echo "4. Creating EC2-specific budget..."
aws budgets create-budget \
    --account-id ${ACCOUNT_ID} \
    --budget "{
        \"BudgetName\": \"EC2-Monthly-Budget\",
        \"BudgetLimit\": {
            \"Amount\": \"500\",
            \"Unit\": \"USD\"
        },
        \"BudgetType\": \"COST\",
        \"TimeUnit\": \"MONTHLY\",
        \"CostFilters\": {
            \"Service\": [\"Amazon Elastic Compute Cloud - Compute\"]
        }
    }" \
    --notifications-with-subscribers "[
        {
            \"Notification\": {
                \"NotificationType\": \"ACTUAL\",
                \"ComparisonOperator\": \"GREATER_THAN\",
                \"Threshold\": 90,
                \"ThresholdType\": \"PERCENTAGE\"
            },
            \"Subscribers\": [
                {
                    \"SubscriptionType\": \"EMAIL\",
                    \"Address\": \"${EMAIL}\"
                }
            ]
        }
    ]"

# 5. Enable Compute Optimizer
echo "5. Enabling Compute Optimizer..."
aws compute-optimizer update-enrollment-status --status Active || true

# 6. Create Cost Anomaly Detection monitor
echo "6. Setting up Cost Anomaly Detection..."
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "MonitorName": "AWS-Services-Monitor",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }'

MONITOR_ARN=$(aws ce get-anomaly-monitors \
    --query 'AnomalyMonitors[?MonitorName==`AWS-Services-Monitor`].MonitorArn' \
    --output text)

aws ce create-anomaly-subscription \
    --anomaly-subscription "{
        \"SubscriptionName\": \"Cost-Anomaly-Alerts\",
        \"MonitorArnList\": [\"${MONITOR_ARN}\"],
        \"Subscribers\": [
            {
                \"Type\": \"EMAIL\",
                \"Address\": \"${EMAIL}\"
            }
        ],
        \"Threshold\": 100,
        \"Frequency\": \"DAILY\"
    }"

echo -e "\n=== Cost Management Setup Complete ==="
echo "CUR Bucket: s3://${CUR_BUCKET}"
echo "SNS Topic: ${TOPIC_ARN}"
echo "Note: Enable CUR from the console: Billing > Cost & Usage Reports > Create report"
```

## Summary

AWS provides comprehensive cost management tools:

1. **Cost Explorer**: Visualize and analyze costs with filtering and forecasting
2. **Budgets**: Set spending limits with alerts and automated actions
3. **Cost and Usage Reports**: Detailed billing data for analysis
4. **Rightsizing**: Recommendations for optimal resource sizing
5. **Savings Plans & RIs**: Commitment-based discounts for predictable workloads

**Key Cost Optimization Strategies**:
- Implement tagging for cost allocation
- Use rightsizing recommendations
- Leverage Savings Plans for steady-state workloads
- Use Spot Instances for fault-tolerant workloads
- Implement Auto Scaling for elasticity
- Optimize storage with lifecycle policies
- Monitor with budgets and anomaly detection
