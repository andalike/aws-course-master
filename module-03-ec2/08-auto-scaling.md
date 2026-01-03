# Auto Scaling Deep Dive

## Table of Contents

1. [Introduction to Auto Scaling](#introduction-to-auto-scaling)
2. [Auto Scaling Components](#auto-scaling-components)
3. [Launch Templates vs Launch Configurations](#launch-templates-vs-launch-configurations)
4. [Auto Scaling Groups (ASG)](#auto-scaling-groups-asg)
5. [Scaling Policies](#scaling-policies)
6. [Lifecycle Hooks](#lifecycle-hooks)
7. [Instance Refresh](#instance-refresh)
8. [Warm Pools](#warm-pools)
9. [Hands-On CLI Examples](#hands-on-cli-examples)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Introduction to Auto Scaling

### What is Auto Scaling?

Amazon EC2 Auto Scaling helps you maintain application availability and allows you to automatically add or remove EC2 instances according to conditions you define. It ensures you have the right number of instances available to handle the load for your application.

### Key Benefits

```
+------------------------------------------------------------------+
|                    AUTO SCALING BENEFITS                          |
+------------------------------------------------------------------+
|                                                                   |
|  [Availability]     Maintain a consistent number of instances     |
|        |            even if one fails                             |
|        v                                                          |
|  [Scalability]      Automatically scale out during demand peaks   |
|        |            and scale in during off-peak times            |
|        v                                                          |
|  [Cost Savings]     Only pay for the instances you need,          |
|        |            when you need them                            |
|        v                                                          |
|  [Flexibility]      Use multiple instance types and purchase      |
|                     options (On-Demand, Spot, Reserved)           |
|                                                                   |
+------------------------------------------------------------------+
```

### Auto Scaling vs Manual Scaling

| Aspect | Manual Scaling | Auto Scaling |
|--------|----------------|--------------|
| Response Time | Hours (human intervention) | Minutes (automatic) |
| Cost Efficiency | Over/under provisioned | Right-sized |
| Availability | Prone to human error | Self-healing |
| Operational Load | High | Low |
| Scalability | Limited by team capacity | Unlimited |

---

## Auto Scaling Components

### Architecture Overview

```
                    ┌──────────────────────────────────────────┐
                    │           Auto Scaling Group             │
                    │                                          │
                    │    ┌─────────────────────────────────┐   │
                    │    │      Launch Template            │   │
                    │    │  (AMI, Instance Type, SG, etc.) │   │
                    │    └─────────────────────────────────┘   │
                    │                    │                     │
                    │                    ▼                     │
                    │    ┌────────┐ ┌────────┐ ┌────────┐     │
                    │    │  EC2   │ │  EC2   │ │  EC2   │     │
                    │    │ i-aaa  │ │ i-bbb  │ │ i-ccc  │     │
                    │    └────────┘ └────────┘ └────────┘     │
                    │                                          │
                    └──────────────────────────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────────┐
                    │            Scaling Policies               │
                    │                                          │
                    │  • Target Tracking (CPU at 50%)          │
                    │  • Step Scaling (add 2 if CPU > 80%)     │
                    │  • Simple Scaling (add 1 if alarm)       │
                    │  • Scheduled Scaling (9AM workdays)      │
                    │  • Predictive Scaling (ML-based)         │
                    │                                          │
                    └──────────────────────────────────────────┘
```

### Core Components

| Component | Purpose |
|-----------|---------|
| **Launch Template/Configuration** | Defines what to launch (AMI, instance type, security groups, etc.) |
| **Auto Scaling Group (ASG)** | Manages the collection of instances as a logical group |
| **Scaling Policies** | Defines when and how to scale |
| **Lifecycle Hooks** | Custom actions during launch/terminate |
| **Health Checks** | Determines instance health status |

---

## Launch Templates vs Launch Configurations

### Comparison Table

| Feature | Launch Template | Launch Configuration |
|---------|-----------------|----------------------|
| **Versioning** | Yes | No |
| **Multiple Instance Types** | Yes | No |
| **Spot + On-Demand Mix** | Yes | No |
| **T2/T3 Unlimited** | Yes | No |
| **Dedicated Hosts** | Yes | No |
| **Capacity Reservations** | Yes | No |
| **AWS Recommendation** | Preferred | Legacy (deprecated) |

> **Important**: AWS recommends using Launch Templates instead of Launch Configurations. Launch Configurations are being deprecated.

### Launch Template Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                      LAUNCH TEMPLATE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  AMI ID         │    │  Instance Type  │                    │
│  │  ami-0abc123... │    │  t3.medium      │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  Key Pair       │    │  Security Groups│                    │
│  │  my-key         │    │  sg-123, sg-456 │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  User Data      │    │  IAM Role       │                    │
│  │  #!/bin/bash... │    │  EC2Role        │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │  Block Device Mappings                  │                   │
│  │  /dev/xvda: 20GB gp3                    │                   │
│  │  /dev/xvdb: 100GB gp3                   │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  Version: 3 (Latest)                                           │
│  Default Version: 2                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Creating a Launch Template (CLI)

```bash
# Create a launch template
aws ec2 create-launch-template \
    --launch-template-name my-web-server-template \
    --version-description "Initial version" \
    --launch-template-data '{
        "ImageId": "ami-0abcdef1234567890",
        "InstanceType": "t3.medium",
        "KeyName": "my-key-pair",
        "SecurityGroupIds": ["sg-0123456789abcdef0"],
        "UserData": "IyEvYmluL2Jhc2gKeXVtIHVwZGF0ZSAteQp5dW0gaW5zdGFsbCAteSBodHRwZApzeXN0ZW1jdGwgc3RhcnQgaHR0cGQKc3lzdGVtY3RsIGVuYWJsZSBodHRwZA==",
        "IamInstanceProfile": {
            "Name": "EC2-Instance-Profile"
        },
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "VolumeSize": 20,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": true,
                    "Encrypted": true
                }
            }
        ],
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "Web-Server"
                    },
                    {
                        "Key": "Environment",
                        "Value": "Production"
                    }
                ]
            }
        ],
        "Monitoring": {
            "Enabled": true
        }
    }'
```

### Creating a New Version

```bash
# Create a new version with updated instance type
aws ec2 create-launch-template-version \
    --launch-template-name my-web-server-template \
    --version-description "Upgraded to t3.large" \
    --source-version 1 \
    --launch-template-data '{
        "InstanceType": "t3.large"
    }'
```

### Set Default Version

```bash
# Set version 2 as default
aws ec2 modify-launch-template \
    --launch-template-name my-web-server-template \
    --default-version 2
```

---

## Auto Scaling Groups (ASG)

### ASG Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTO SCALING GROUP SETTINGS                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Capacity Settings:                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   Min: 2      Desired: 4      Max: 10                  │   │
│  │    │             │              │                       │   │
│  │    └─────────────┼──────────────┘                       │   │
│  │         ◄────────┴────────►                             │   │
│  │    [Floor]    [Target]    [Ceiling]                     │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Availability Zones:                                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                        │
│  │ us-e-1a │  │ us-e-1b │  │ us-e-1c │                        │
│  └─────────┘  └─────────┘  └─────────┘                        │
│                                                                 │
│  Health Check Type:  EC2  |  ELB                               │
│  Health Check Grace Period: 300 seconds                        │
│                                                                 │
│  Termination Policy:  Default | OldestInstance | NewestInstance│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Capacity Types

| Capacity | Description |
|----------|-------------|
| **Minimum** | Lowest number of instances ASG maintains (never goes below) |
| **Desired** | Target number of instances ASG tries to maintain |
| **Maximum** | Highest number of instances ASG can scale to |

### Creating an Auto Scaling Group (CLI)

```bash
# Create Auto Scaling Group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name my-web-asg \
    --launch-template "LaunchTemplateName=my-web-server-template,Version=\$Latest" \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 4 \
    --vpc-zone-identifier "subnet-111111,subnet-222222,subnet-333333" \
    --health-check-type ELB \
    --health-check-grace-period 300 \
    --target-group-arns "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/1234567890123456" \
    --tags "Key=Name,Value=Web-Server,PropagateAtLaunch=true" \
           "Key=Environment,Value=Production,PropagateAtLaunch=true"
```

### Mixed Instances Policy

Use multiple instance types with On-Demand and Spot instances:

```bash
# Create ASG with mixed instances
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name my-mixed-asg \
    --mixed-instances-policy '{
        "LaunchTemplate": {
            "LaunchTemplateSpecification": {
                "LaunchTemplateName": "my-web-server-template",
                "Version": "$Latest"
            },
            "Overrides": [
                {"InstanceType": "t3.medium"},
                {"InstanceType": "t3.large"},
                {"InstanceType": "t3a.medium"},
                {"InstanceType": "t3a.large"},
                {"InstanceType": "m5.large"}
            ]
        },
        "InstancesDistribution": {
            "OnDemandBaseCapacity": 2,
            "OnDemandPercentageAboveBaseCapacity": 25,
            "SpotAllocationStrategy": "price-capacity-optimized",
            "SpotInstancePools": 4
        }
    }' \
    --min-size 4 \
    --max-size 20 \
    --vpc-zone-identifier "subnet-111111,subnet-222222"
```

### Instance Distribution Explained

```
┌─────────────────────────────────────────────────────────────────┐
│                 MIXED INSTANCES DISTRIBUTION                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OnDemandBaseCapacity: 2                                        │
│  OnDemandPercentageAboveBaseCapacity: 25%                       │
│                                                                 │
│  Example with Desired Capacity = 10:                            │
│                                                                 │
│  Total: 10 instances                                            │
│  ├── On-Demand Base: 2 (guaranteed)                            │
│  ├── Remaining: 8                                               │
│  │   ├── On-Demand (25%): 2                                    │
│  │   └── Spot (75%): 6                                         │
│  │                                                              │
│  Result: 4 On-Demand + 6 Spot                                  │
│                                                                 │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐...   │
│  │ OD │ │ OD │ │ OD │ │ OD │ │Spot│ │Spot│ │Spot│ │Spot│      │
│  │Base│ │Base│ │ 25%│ │ 25%│ │    │ │    │ │    │ │    │      │
│  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Termination Policies

When scaling in, ASG uses termination policies to determine which instances to terminate:

| Policy | Description |
|--------|-------------|
| **Default** | Balance AZs first, then use launch configuration age |
| **OldestInstance** | Terminate the oldest instance |
| **NewestInstance** | Terminate the newest instance |
| **OldestLaunchConfiguration** | Terminate instances with oldest launch config |
| **OldestLaunchTemplate** | Terminate instances with oldest launch template |
| **ClosestToNextInstanceHour** | Terminate instance closest to billing hour |
| **AllocationStrategy** | For Spot, align with allocation strategy |

```bash
# Update termination policy
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name my-web-asg \
    --termination-policies "OldestLaunchTemplate" "OldestInstance"
```

---

## Scaling Policies

### Types of Scaling Policies

```
┌─────────────────────────────────────────────────────────────────┐
│                      SCALING POLICIES                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. TARGET TRACKING SCALING                                     │
│     "Keep CPU at 50%"                                           │
│     [Simplest, AWS manages alarms]                              │
│                                                                 │
│  2. STEP SCALING                                                │
│     "If CPU > 70%, add 2. If CPU > 90%, add 4"                 │
│     [Graduated response to metrics]                             │
│                                                                 │
│  3. SIMPLE SCALING                                              │
│     "If alarm triggers, add 1"                                  │
│     [Basic, waits for cooldown]                                 │
│                                                                 │
│  4. SCHEDULED SCALING                                           │
│     "At 9AM, set capacity to 10"                               │
│     [Time-based, predictable patterns]                          │
│                                                                 │
│  5. PREDICTIVE SCALING                                          │
│     "ML predicts traffic spike at 2PM tomorrow"                │
│     [Machine learning based]                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Target Tracking Scaling

The simplest and most recommended policy type. You set a target value, and Auto Scaling creates and manages CloudWatch alarms.

```bash
# Create target tracking policy for CPU
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name my-web-asg \
    --policy-name cpu-target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0,
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60,
        "DisableScaleIn": false
    }'
```

**Predefined Metrics:**
- `ASGAverageCPUUtilization` - Average CPU across all instances
- `ASGAverageNetworkIn` - Average network bytes received
- `ASGAverageNetworkOut` - Average network bytes sent
- `ALBRequestCountPerTarget` - Requests per target from ALB

```bash
# Target tracking with ALB request count
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name my-web-asg \
    --policy-name alb-request-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ALBRequestCountPerTarget",
            "ResourceLabel": "app/my-alb/1234567890123456/targetgroup/my-tg/1234567890123456"
        },
        "TargetValue": 1000.0
    }'
```

### 2. Step Scaling

Provides graduated scaling based on alarm breach size:

```
┌─────────────────────────────────────────────────────────────────┐
│                      STEP SCALING EXAMPLE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CPU Utilization:                                               │
│                                                                 │
│  0%──────30%──────50%──────70%──────85%──────100%              │
│           │        │        │        │                          │
│           │        │        │        └─► Add 4 instances        │
│           │        │        └──────────► Add 2 instances        │
│           │        └───────────────────► No action              │
│           └────────────────────────────► Remove 1 instance      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```bash
# Create CloudWatch alarm first
aws cloudwatch put-metric-alarm \
    --alarm-name cpu-high-alarm \
    --alarm-description "CPU utilization high" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 60 \
    --threshold 50 \
    --comparison-operator GreaterThanThreshold \
    --dimensions "Name=AutoScalingGroupName,Value=my-web-asg" \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:autoscaling:us-east-1:123456789012:scalingPolicy:12345678-1234-1234-1234-123456789012:autoScalingGroupName/my-web-asg:policyName/step-scale-out

# Create step scaling policy
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name my-web-asg \
    --policy-name step-scale-out \
    --policy-type StepScaling \
    --adjustment-type ChangeInCapacity \
    --step-adjustments '[
        {
            "MetricIntervalLowerBound": 0,
            "MetricIntervalUpperBound": 20,
            "ScalingAdjustment": 2
        },
        {
            "MetricIntervalLowerBound": 20,
            "MetricIntervalUpperBound": 35,
            "ScalingAdjustment": 4
        },
        {
            "MetricIntervalLowerBound": 35,
            "ScalingAdjustment": 6
        }
    ]' \
    --metric-aggregation-type Average
```

### 3. Simple Scaling

Basic scaling with cooldown period:

```bash
# Scale out policy
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name my-web-asg \
    --policy-name simple-scale-out \
    --scaling-adjustment 2 \
    --adjustment-type ChangeInCapacity \
    --cooldown 300

# Scale in policy
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name my-web-asg \
    --policy-name simple-scale-in \
    --scaling-adjustment -1 \
    --adjustment-type ChangeInCapacity \
    --cooldown 300
```

### Adjustment Types

| Type | Description | Example |
|------|-------------|---------|
| **ChangeInCapacity** | Add/remove specific number | +2 instances |
| **ExactCapacity** | Set to specific number | Set to 10 instances |
| **PercentChangeInCapacity** | Percentage change | +50% capacity |

### 4. Scheduled Scaling

For predictable load patterns:

```bash
# Scale up for business hours
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name my-web-asg \
    --scheduled-action-name scale-up-morning \
    --recurrence "0 9 * * MON-FRI" \
    --min-size 4 \
    --max-size 20 \
    --desired-capacity 10 \
    --time-zone "America/New_York"

# Scale down after business hours
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name my-web-asg \
    --scheduled-action-name scale-down-evening \
    --recurrence "0 18 * * MON-FRI" \
    --min-size 2 \
    --max-size 10 \
    --desired-capacity 2 \
    --time-zone "America/New_York"

# One-time scheduled action
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name my-web-asg \
    --scheduled-action-name black-friday-scale \
    --start-time "2025-11-28T00:00:00Z" \
    --end-time "2025-11-29T23:59:59Z" \
    --min-size 20 \
    --max-size 100 \
    --desired-capacity 50
```

### 5. Predictive Scaling

Uses machine learning to predict future traffic:

```bash
# Enable predictive scaling
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name my-web-asg \
    --policy-name predictive-scaling-policy \
    --policy-type PredictiveScaling \
    --predictive-scaling-configuration '{
        "MetricSpecifications": [
            {
                "TargetValue": 50,
                "PredefinedMetricPairSpecification": {
                    "PredefinedMetricType": "ASGCPUUtilization"
                }
            }
        ],
        "Mode": "ForecastAndScale",
        "SchedulingBufferTime": 300,
        "MaxCapacityBreachBehavior": "IncreaseMaxCapacity",
        "MaxCapacityBuffer": 10
    }'
```

---

## Lifecycle Hooks

### What are Lifecycle Hooks?

Lifecycle hooks allow you to perform custom actions as Auto Scaling launches or terminates instances.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTANCE LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SCALE OUT (Launch):                                            │
│                                                                 │
│  ┌─────────┐    ┌───────────────────┐    ┌─────────────┐       │
│  │ Pending │───►│ Pending:Wait      │───►│ Pending:    │       │
│  │         │    │ (Hook Active)     │    │ Proceed     │       │
│  └─────────┘    └───────────────────┘    └─────────────┘       │
│                          │                      │               │
│                    [Custom Action]              │               │
│                    - Pull code                  │               │
│                    - Register DNS               ▼               │
│                    - Configure app       ┌─────────────┐       │
│                                          │   InService │       │
│                                          └─────────────┘       │
│                                                                 │
│  SCALE IN (Terminate):                                          │
│                                                                 │
│  ┌───────────┐    ┌───────────────────┐    ┌─────────────┐     │
│  │ InService │───►│ Terminating:Wait  │───►│ Terminating:│     │
│  │           │    │ (Hook Active)     │    │ Proceed     │     │
│  └───────────┘    └───────────────────┘    └─────────────┘     │
│                          │                      │               │
│                    [Custom Action]              │               │
│                    - Deregister DNS             ▼               │
│                    - Send logs             ┌─────────────┐     │
│                    - Drain connections     │ Terminated  │     │
│                                            └─────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Creating Lifecycle Hooks

```bash
# Launch lifecycle hook
aws autoscaling put-lifecycle-hook \
    --auto-scaling-group-name my-web-asg \
    --lifecycle-hook-name launch-hook \
    --lifecycle-transition autoscaling:EC2_INSTANCE_LAUNCHING \
    --heartbeat-timeout 300 \
    --default-result CONTINUE \
    --notification-target-arn arn:aws:sns:us-east-1:123456789012:asg-notifications \
    --role-arn arn:aws:iam::123456789012:role/AutoScalingNotificationRole

# Terminate lifecycle hook
aws autoscaling put-lifecycle-hook \
    --auto-scaling-group-name my-web-asg \
    --lifecycle-hook-name terminate-hook \
    --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
    --heartbeat-timeout 600 \
    --default-result ABANDON \
    --notification-target-arn arn:aws:sqs:us-east-1:123456789012:asg-terminate-queue \
    --role-arn arn:aws:iam::123456789012:role/AutoScalingNotificationRole
```

### Hook Parameters

| Parameter | Description |
|-----------|-------------|
| **heartbeat-timeout** | Time (seconds) to wait for action completion (max 7200) |
| **default-result** | CONTINUE (proceed) or ABANDON (cancel) if timeout |
| **notification-target-arn** | SNS topic, SQS queue, or EventBridge |

### Completing Lifecycle Actions

```bash
# Complete lifecycle action (from Lambda or EC2 User Data)
aws autoscaling complete-lifecycle-action \
    --lifecycle-hook-name launch-hook \
    --auto-scaling-group-name my-web-asg \
    --lifecycle-action-result CONTINUE \
    --instance-id i-1234567890abcdef0

# Or abandon the action (will terminate instance on launch hook)
aws autoscaling complete-lifecycle-action \
    --lifecycle-hook-name launch-hook \
    --auto-scaling-group-name my-web-asg \
    --lifecycle-action-result ABANDON \
    --instance-id i-1234567890abcdef0
```

### Extending Heartbeat Timeout

```bash
# If you need more time, extend the heartbeat
aws autoscaling record-lifecycle-action-heartbeat \
    --lifecycle-hook-name launch-hook \
    --auto-scaling-group-name my-web-asg \
    --instance-id i-1234567890abcdef0
```

---

## Instance Refresh

### What is Instance Refresh?

Instance Refresh allows you to update instances in an Auto Scaling group in a rolling fashion without downtime.

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTANCE REFRESH PROCESS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Start with 4 instances (Old AMI)                       │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │Old-1│ │Old-2│ │Old-3│ │Old-4│                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│                                                                 │
│  Step 2: Launch new instance, terminate old (Min Healthy: 50%)  │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │New-1│ │Old-2│ │Old-3│ │Old-4│                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│                                                                 │
│  Step 3: Continue rolling replacement                           │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │New-1│ │New-2│ │Old-3│ │Old-4│                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│                                                                 │
│  Step 4: Complete                                               │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                               │
│  │New-1│ │New-2│ │New-3│ │New-4│                               │
│  └─────┘ └─────┘ └─────┘ └─────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Starting Instance Refresh

```bash
# Start instance refresh
aws autoscaling start-instance-refresh \
    --auto-scaling-group-name my-web-asg \
    --preferences '{
        "MinHealthyPercentage": 50,
        "InstanceWarmup": 300,
        "SkipMatching": true,
        "CheckpointPercentages": [25, 50, 75, 100],
        "CheckpointDelay": 3600
    }' \
    --desired-configuration '{
        "LaunchTemplate": {
            "LaunchTemplateName": "my-web-server-template",
            "Version": "$Latest"
        }
    }'
```

### Monitoring Instance Refresh

```bash
# Describe instance refresh status
aws autoscaling describe-instance-refreshes \
    --auto-scaling-group-name my-web-asg

# Cancel instance refresh
aws autoscaling cancel-instance-refresh \
    --auto-scaling-group-name my-web-asg
```

---

## Warm Pools

### What are Warm Pools?

Warm pools maintain a pool of pre-initialized instances that can be quickly added to an ASG, reducing scale-out time.

```
┌─────────────────────────────────────────────────────────────────┐
│                        WARM POOL                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Auto Scaling Group (In Service)    Warm Pool (Stopped/Running) │
│  ┌───────────────────────────────┐  ┌────────────────────────┐  │
│  │  ┌─────┐ ┌─────┐ ┌─────┐     │  │  ┌─────┐ ┌─────┐      │  │
│  │  │ i-1 │ │ i-2 │ │ i-3 │     │  │  │ i-4 │ │ i-5 │      │  │
│  │  │ Run │ │ Run │ │ Run │     │  │  │Stop │ │Stop │      │  │
│  │  └─────┘ └─────┘ └─────┘     │  │  └─────┘ └─────┘      │  │
│  │  Desired: 3                   │  │  Pool Size: 2         │  │
│  └───────────────────────────────┘  └────────────────────────┘  │
│                                                                 │
│  Scale-Out Event: Move from Warm Pool to ASG (seconds vs mins) │
│                                                                 │
│  Without Warm Pool: ~3-5 minutes (launch + initialize)         │
│  With Warm Pool:    ~30 seconds (just start instance)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Creating a Warm Pool

```bash
# Create warm pool
aws autoscaling put-warm-pool \
    --auto-scaling-group-name my-web-asg \
    --pool-state Stopped \
    --min-size 2 \
    --max-group-prepared-capacity 6 \
    --instance-reuse-policy '{
        "ReuseOnScaleIn": true
    }'
```

### Warm Pool States

| State | Description | Cost |
|-------|-------------|------|
| **Stopped** | Instances are stopped (only EBS charges) | Lowest |
| **Running** | Instances are running (full charges) | Highest |
| **Hibernated** | Instances are hibernated (EBS + RAM snapshot) | Medium |

---

## Hands-On CLI Examples

### Complete Auto Scaling Setup

```bash
#!/bin/bash

# Variables
REGION="us-east-1"
AMI_ID="ami-0abcdef1234567890"  # Replace with your AMI
VPC_ID="vpc-12345678"
SUBNET_IDS="subnet-111111,subnet-222222"
KEY_NAME="my-key-pair"

# Step 1: Create Security Group
echo "Creating Security Group..."
SG_ID=$(aws ec2 create-security-group \
    --group-name web-server-sg \
    --description "Web server security group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

echo "Security Group created: $SG_ID"

# Step 2: Create Launch Template
echo "Creating Launch Template..."
USER_DATA=$(cat << 'EOF' | base64
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
echo "<h1>Hello from $INSTANCE_ID</h1>" > /var/www/html/index.html
EOF
)

aws ec2 create-launch-template \
    --launch-template-name web-server-template \
    --version-description "v1" \
    --launch-template-data "{
        \"ImageId\": \"$AMI_ID\",
        \"InstanceType\": \"t3.micro\",
        \"KeyName\": \"$KEY_NAME\",
        \"SecurityGroupIds\": [\"$SG_ID\"],
        \"UserData\": \"$USER_DATA\",
        \"Monitoring\": {\"Enabled\": true},
        \"TagSpecifications\": [{
            \"ResourceType\": \"instance\",
            \"Tags\": [{\"Key\": \"Name\", \"Value\": \"Web-Server\"}]
        }]
    }"

echo "Launch Template created"

# Step 3: Create Auto Scaling Group
echo "Creating Auto Scaling Group..."
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name web-asg \
    --launch-template "LaunchTemplateName=web-server-template,Version=\$Latest" \
    --min-size 2 \
    --max-size 6 \
    --desired-capacity 2 \
    --vpc-zone-identifier "$SUBNET_IDS" \
    --health-check-type EC2 \
    --health-check-grace-period 300 \
    --tags "Key=Name,Value=Web-Server,PropagateAtLaunch=true"

echo "Auto Scaling Group created"

# Step 4: Create Target Tracking Policy
echo "Creating Scaling Policy..."
aws autoscaling put-scaling-policy \
    --auto-scaling-group-name web-asg \
    --policy-name cpu-target-tracking \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0
    }'

echo "Scaling Policy created"

# Step 5: Create Scheduled Scaling
echo "Creating Scheduled Actions..."
aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name web-asg \
    --scheduled-action-name scale-up-morning \
    --recurrence "0 9 * * MON-FRI" \
    --desired-capacity 4

aws autoscaling put-scheduled-update-group-action \
    --auto-scaling-group-name web-asg \
    --scheduled-action-name scale-down-evening \
    --recurrence "0 18 * * MON-FRI" \
    --desired-capacity 2

echo "Scheduled Actions created"

echo "Setup complete!"
```

### Monitoring Commands

```bash
# Describe Auto Scaling Group
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names web-asg \
    --query 'AutoScalingGroups[0].{
        Name:AutoScalingGroupName,
        Min:MinSize,
        Max:MaxSize,
        Desired:DesiredCapacity,
        Instances:Instances[*].InstanceId
    }'

# Describe scaling activities
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name web-asg \
    --max-items 10

# Describe scaling policies
aws autoscaling describe-policies \
    --auto-scaling-group-name web-asg

# View scheduled actions
aws autoscaling describe-scheduled-actions \
    --auto-scaling-group-name web-asg
```

### Manual Scaling

```bash
# Set desired capacity manually
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name web-asg \
    --desired-capacity 4

# Update min/max capacity
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name web-asg \
    --min-size 2 \
    --max-size 10
```

### Cleanup Script

```bash
#!/bin/bash

# Delete Auto Scaling Group
echo "Deleting Auto Scaling Group..."
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name web-asg \
    --min-size 0 \
    --max-size 0 \
    --desired-capacity 0

# Wait for instances to terminate
echo "Waiting for instances to terminate..."
aws autoscaling wait group-not-exists --auto-scaling-group-name web-asg || true

aws autoscaling delete-auto-scaling-group \
    --auto-scaling-group-name web-asg \
    --force-delete

# Delete Launch Template
echo "Deleting Launch Template..."
aws ec2 delete-launch-template \
    --launch-template-name web-server-template

# Delete Security Group (wait for instances to terminate)
sleep 60
echo "Deleting Security Group..."
aws ec2 delete-security-group --group-id $SG_ID

echo "Cleanup complete!"
```

---

## Best Practices

### 1. Capacity Planning

```
+------------------------------------------------------------------+
|                  CAPACITY PLANNING CHECKLIST                     |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Set minimum capacity >= 2 for high availability             |
|  [ ] Spread instances across multiple AZs                        |
|  [ ] Use multiple instance types in mixed instances policy       |
|  [ ] Set health check grace period long enough for boot          |
|  [ ] Configure appropriate cooldown periods                      |
|                                                                   |
+------------------------------------------------------------------+
```

### 2. Scaling Strategy Recommendations

| Scenario | Recommended Policy |
|----------|-------------------|
| Steady traffic with occasional spikes | Target Tracking |
| Gradual traffic increases | Step Scaling |
| Predictable daily patterns | Scheduled + Target Tracking |
| ML workloads, batch processing | Predictive Scaling |
| Unknown traffic patterns | Start with Target Tracking |

### 3. Cost Optimization

- Use mixed instances policy with Spot instances
- Implement proper scale-in policies
- Use warm pools for faster scaling instead of over-provisioning
- Set up billing alerts for unexpected scaling

### 4. Monitoring and Alerting

```bash
# Create CloudWatch alarm for ASG
aws cloudwatch put-metric-alarm \
    --alarm-name asg-high-cpu \
    --alarm-description "ASG average CPU is high" \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions "Name=AutoScalingGroupName,Value=web-asg" \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Instances not launching | Insufficient capacity | Use multiple instance types, check AZ availability |
| Instances marked unhealthy | Application not ready | Increase health check grace period |
| Scaling not happening | Policy not triggered | Check CloudWatch metrics and alarms |
| Instances terminating immediately | User data failure | Check instance logs, verify AMI |
| Stuck in Pending:Wait | Lifecycle hook timeout | Complete lifecycle action or increase timeout |

### Debugging Commands

```bash
# Check instance health status
aws autoscaling describe-auto-scaling-instances \
    --query 'AutoScalingInstances[?AutoScalingGroupName==`web-asg`].{
        InstanceId:InstanceId,
        HealthStatus:HealthStatus,
        LifecycleState:LifecycleState
    }'

# Check recent scaling activities
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name web-asg \
    --max-items 5 \
    --query 'Activities[*].{
        Activity:Description,
        Status:StatusCode,
        Cause:Cause
    }'

# View launch template validation
aws ec2 describe-launch-template-versions \
    --launch-template-name web-server-template \
    --query 'LaunchTemplateVersions[*].{
        Version:VersionNumber,
        Description:VersionDescription,
        Default:DefaultVersion
    }'
```

### Instance Failed to Launch Checklist

1. Check launch template AMI exists in the region
2. Verify instance type is available in selected AZs
3. Confirm security group exists and is in correct VPC
4. Check IAM instance profile permissions
5. Verify subnet has available IP addresses
6. Check service quotas/limits

---

## Summary

### Key Takeaways

1. **Launch Templates** are preferred over Launch Configurations
2. **Target Tracking** is the simplest and most effective scaling policy
3. **Mixed Instances Policy** provides cost savings and availability
4. **Lifecycle Hooks** enable custom automation during scaling events
5. **Warm Pools** reduce scale-out time significantly
6. **Instance Refresh** enables rolling updates without downtime

### Next Steps

- Practice creating ASGs with different scaling policies
- Experiment with lifecycle hooks and automation
- Move on to [09-load-balancing.md](./09-load-balancing.md) to learn about ELB integration

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Estimated Reading Time**: 60 minutes
