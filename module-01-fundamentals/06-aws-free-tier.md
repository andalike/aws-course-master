# 06 - AWS Free Tier Guide

## Section Overview

| Attribute | Details |
|-----------|---------|
| **Estimated Time** | 20 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | AWS account created |
| **Type** | Theory |

---

## Learning Objectives

After completing this section, you will be able to:

- Understand the three types of AWS Free Tier offers
- Identify which services are free and their limits
- Monitor your Free Tier usage
- Avoid unexpected charges
- Know what happens when you exceed Free Tier limits

---

## What is AWS Free Tier?

AWS Free Tier provides free access to explore and try out AWS services. It's designed for:

- Learning and experimentation
- Building proof of concepts
- Small applications and websites
- Training and certification prep

> **Real-World Analogy**
>
> Think of AWS Free Tier like a gym's free trial membership. You get access to the equipment (services) for free up to certain limits. If you use the sauna too long (exceed limits), you'll be charged for the extra time.

---

## Three Types of Free Tier Offers

### 1. Always Free

Services that are **always free** regardless of how long you've had your account.

| Service | Free Limit | Example Use |
|---------|------------|-------------|
| **AWS Lambda** | 1 million requests/month | Serverless functions |
| **Amazon DynamoDB** | 25 GB storage | NoSQL database |
| **Amazon CloudWatch** | 10 custom metrics, 10 alarms | Monitoring |
| **Amazon SNS** | 1 million publishes | Push notifications |
| **Amazon SQS** | 1 million requests | Message queuing |
| **AWS CodeBuild** | 100 build minutes/month | CI/CD |
| **Amazon Cognito** | 50,000 MAUs | User authentication |
| **AWS Step Functions** | 4,000 state transitions | Workflow orchestration |

> **Pro Tip: Always Free for Learning**
>
> Focus on Always Free services when learning. Lambda, DynamoDB, and CloudWatch together can power many learning projects at no cost.

---

### 2. 12 Months Free

Services that are free for **12 months from your AWS account creation date**.

| Service | Free Limit | Notes |
|---------|------------|-------|
| **Amazon EC2** | 750 hours/month (t2.micro or t3.micro) | Linux and Windows |
| **Amazon S3** | 5 GB standard storage | Plus 20,000 GET, 2,000 PUT |
| **Amazon RDS** | 750 hours/month (db.t2.micro or db.t3.micro) | 20 GB storage |
| **Amazon ElastiCache** | 750 hours/month (cache.t2.micro or cache.t3.micro) | Redis/Memcached |
| **Amazon EBS** | 30 GB of storage | General Purpose (SSD) or Magnetic |
| **Elastic Load Balancing** | 750 hours/month | Classic and Application Load Balancer |
| **Amazon CloudFront** | 1 TB data transfer out | CDN |
| **Amazon API Gateway** | 1 million API calls/month | REST APIs |

```
Account Creation: January 15, 2024
                        │
                        ▼
     ┌──────────────────────────────────────────────────────────┐
     │                                                          │
     │              12 MONTHS FREE TIER PERIOD                  │
     │                                                          │
     │  Jan 2024 ────────────────────────────────> Jan 2025    │
     │                                                          │
     │  EC2, S3, RDS, etc. available for free within limits    │
     │                                                          │
     └──────────────────────────────────────────────────────────┘
                                                      │
                                                      ▼
                                          12-month free tier ends
                                          Standard pricing applies
```

> **Warning: 12-Month Clock Starts at Account Creation**
>
> The 12-month clock starts when you create your account, NOT when you first use a service. If you create an account in January but don't use EC2 until June, you've already used 5 months of your free period!

---

### 3. Short-Term Free Trials

Services that offer a **one-time free trial** for a specific period.

| Service | Free Trial | Trial Period |
|---------|------------|--------------|
| **Amazon SageMaker** | 250 hours/month (ml.t3.medium) | First 2 months |
| **Amazon Redshift** | 750 hours/month (dc2.large) | First 2 months |
| **Amazon Inspector** | 90-day free trial | 90 days |
| **Amazon Lightsail** | 750 hours/month (smallest instance) | First 3 months |
| **Amazon QuickSight** | 30-day free trial | 30 days |
| **AWS Database Migration Service** | 750 hours (dms.t2.micro) | First 6 months |

---

## Detailed Free Tier Breakdown

### Amazon EC2 (12 Months Free)

**What's Included:**
- 750 hours per month of t2.micro (or t3.micro in regions where t2.micro is unavailable)
- Both Linux and Windows instances
- Free hours split between all instances

**Hour Calculation:**
```
750 hours ÷ 24 hours/day = 31.25 days

This means:
- 1 instance running 24/7 = 720 hours (within limit)
- 2 instances running 24/7 = 1,440 hours (690 hours OVER limit!)
```

| Scenario | Hours Used | Status |
|----------|------------|--------|
| 1 instance, 24/7 for 30 days | 720 hours | SAFE |
| 2 instances, 24/7 for 15 days | 720 hours | SAFE |
| 3 instances, 24/7 for 10 days | 720 hours | SAFE |
| 2 instances, 24/7 for 30 days | 1,440 hours | OVER BY 690 HOURS |

> **Warning: Instance Types Matter**
>
> ONLY t2.micro and t3.micro are free. If you accidentally select t2.small or any other instance type, you WILL be charged!

---

### Amazon S3 (12 Months Free)

**What's Included:**
- 5 GB of Standard Storage
- 20,000 GET Requests
- 2,000 PUT Requests
- 100 GB of Data Transfer Out (to internet)

**What's NOT Free:**
- Storage classes other than Standard (Glacier, etc.)
- S3 Transfer Acceleration
- Cross-region replication data transfer

---

### Amazon RDS (12 Months Free)

**What's Included:**
- 750 hours per month of db.t2.micro or db.t3.micro
- 20 GB of General Purpose (SSD) storage
- 20 GB of storage for automated backups
- Supports: MySQL, PostgreSQL, MariaDB, Oracle BYOL, SQL Server Express

> **Warning: Multi-AZ is NOT Free**
>
> If you enable Multi-AZ deployment for RDS, you will be charged. Always use Single-AZ for learning.

---

### AWS Lambda (Always Free)

**What's Included:**
- 1 million free requests per month
- 400,000 GB-seconds of compute time per month

**Calculation Example:**
```
400,000 GB-seconds with 128 MB function:
= 400,000 × (1024/128)
= 3,200,000 seconds
= 888 hours of execution time

That's A LOT of free Lambda usage!
```

---

## Monitoring Free Tier Usage

### Method 1: Free Tier Usage Dashboard

1. Go to **Billing Dashboard**
2. Click **"Free Tier"** in the left menu

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AWS Free Tier Usage                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Your free tier status (Forecasted for month)                               │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ Service              │ Usage      │ Limit       │ % Used    │ Status  │ │
│  ├──────────────────────┼────────────┼─────────────┼───────────┼─────────┤ │
│  │ EC2 - Linux          │ 234 hrs    │ 750 hrs     │ 31%       │ ✓ OK    │ │
│  │ S3 - Storage         │ 1.2 GB     │ 5 GB        │ 24%       │ ✓ OK    │ │
│  │ RDS - Hours          │ 450 hrs    │ 750 hrs     │ 60%       │ ⚠️ Watch │ │
│  │ Lambda - Requests    │ 125,000    │ 1,000,000   │ 12.5%     │ ✓ OK    │ │
│  │ CloudWatch - Alarms  │ 3          │ 10          │ 30%       │ ✓ OK    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ⚠️ 1 service is approaching free tier limit                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Method 2: Free Tier Usage Alerts (Email)

Set up in Billing Preferences (covered in account creation):

1. Go to **Billing Dashboard** → **Billing Preferences**
2. Enable **"Receive AWS Free Tier alerts"**
3. Alerts sent at 85% of limit

### Method 3: AWS Budgets

Create a $0 budget to get alerts before any charges:

1. Go to **Billing** → **Budgets**
2. Click **"Create budget"**
3. Select **"Zero spend budget"**
4. Enter email for notifications

### Method 4: AWS CLI

```bash
# Get current month costs
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost"
```

---

## Common Causes of Unexpected Charges

### 1. Wrong Instance Type

| Mistake | Solution |
|---------|----------|
| Selected t2.small instead of t2.micro | Always double-check instance type before launching |
| Chose t2.large for "better performance" | Stick with t2.micro for learning |

### 2. Running Too Many Instances

```
❌ WRONG: 3 EC2 instances running 24/7 = 2,160 hours
✓ RIGHT: 1 EC2 instance running 24/7 = 720 hours
```

### 3. Forgot to Stop/Terminate Resources

| Resource | What Happens If Forgotten |
|----------|--------------------------|
| EC2 Instance | Billed per hour |
| RDS Database | Billed per hour (even if not used) |
| NAT Gateway | Billed per hour + data processed |
| Elastic IP | Billed if NOT attached to running instance |
| EBS Volumes | Billed for storage (even if not attached) |

> **Warning: Stop vs Terminate**
>
> - **Stop**: Instance is paused but EBS volume continues to incur storage charges
> - **Terminate**: Instance is deleted and (by default) EBS volume is deleted
>
> For learning, TERMINATE instances when done unless you need to keep the data.

### 4. Data Transfer Charges

| Transfer Type | Free? |
|---------------|-------|
| Data IN to AWS | Always free |
| Data OUT to internet | First 100 GB free |
| Data between regions | CHARGED |
| Data within same AZ | Free |
| Data between AZs (same region) | CHARGED |

### 5. Services Outside Free Tier

| Service | Reason for Charge |
|---------|-------------------|
| NAT Gateway | No free tier at all |
| Elastic IP (unused) | Charged when not attached |
| AWS Secrets Manager | No free tier |
| Amazon Elasticsearch | No free tier |
| Amazon EKS | No free tier for control plane |

---

## Free Tier Expiration Checklist

### Before Your 12-Month Free Tier Ends

- [ ] Review what resources you're using
- [ ] Delete any resources you no longer need
- [ ] Set up billing alerts for post-free-tier
- [ ] Consider which services are worth paying for
- [ ] Explore Always Free alternatives

### What Happens When Free Tier Ends

| Service | After 12 Months |
|---------|-----------------|
| EC2 t2.micro | ~$8-10/month (running 24/7) |
| S3 (5 GB) | ~$0.12/month |
| RDS db.t2.micro | ~$12-15/month (running 24/7) |

> **Pro Tip: Set a Calendar Reminder**
>
> Set a reminder for 11 months after account creation to review your resources before Free Tier expires.

---

## Best Practices to Avoid Charges

### 1. Clean Up After Every Session

```bash
# List all EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]' --output table

# Terminate instances (replace with your instance IDs)
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

### 2. Use Tags for Tracking

Tag all your resources with:
- `Project: learning`
- `Environment: sandbox`
- `DeleteAfter: 2024-02-01`

### 3. Enable Budget Alerts

Create multiple budgets:

| Budget | Alert Threshold | Purpose |
|--------|-----------------|---------|
| Zero Budget | $0.01 | Any charge alert |
| Low Budget | $5.00 | Early warning |
| Max Budget | $20.00 | Emergency stop |

### 4. Check Billing Dashboard Weekly

Make it a habit to check:
- Current charges
- Free Tier usage
- Cost trends

### 5. Use AWS Cost Explorer

Visualize your spending patterns and identify unexpected costs.

---

## Free Tier FAQ

### Q: Can I extend the 12-month Free Tier?

**A:** No. The 12-month period is fixed from account creation. You cannot pause, extend, or restart it.

### Q: Does creating a new account reset Free Tier?

**A:** Technically yes, but AWS Terms of Service prohibit creating multiple accounts to abuse Free Tier. This can result in account termination.

### Q: Are all regions equal for Free Tier?

**A:** Yes, Free Tier limits are per-account, not per-region. Running EC2 in us-east-1 AND eu-west-1 counts against the same 750 hours.

### Q: What if I accidentally get charged?

**A:**
1. Identify the source in Cost Explorer
2. Stop/terminate the resource immediately
3. For first-time small charges, contact AWS Support - they sometimes offer one-time credits

### Q: Is there Free Tier for Organizations?

**A:** Yes, but the 12-month Free Tier is shared across ALL accounts in the organization (not per-account).

---

## Free Tier Resources Summary Table

| Category | Service | Always Free | 12-Month Free | Trial |
|----------|---------|-------------|---------------|-------|
| Compute | EC2 | - | 750 hrs/month (t2.micro) | - |
| Compute | Lambda | 1M requests/month | - | - |
| Storage | S3 | - | 5 GB | - |
| Storage | EBS | - | 30 GB | - |
| Database | RDS | - | 750 hrs/month (db.t2.micro) | - |
| Database | DynamoDB | 25 GB | - | - |
| Networking | CloudFront | - | 1 TB transfer out | - |
| Networking | API Gateway | - | 1M calls/month | - |
| Monitoring | CloudWatch | 10 metrics, 10 alarms | - | - |
| Messaging | SNS | 1M publishes | - | - |
| Messaging | SQS | 1M requests | - | - |
| Security | Cognito | 50K MAUs | - | - |
| ML | SageMaker | - | - | 250 hrs (2 months) |

---

## Key Takeaways

| Concept | Remember This |
|---------|---------------|
| **Always Free** | Never expires, fixed monthly limits |
| **12 Months Free** | Clock starts at account creation |
| **Instance Type** | t2.micro/t3.micro ONLY for free EC2 |
| **Hours Pooled** | 750 hours across ALL instances |
| **Monitoring** | Set up billing alerts immediately |
| **Clean Up** | Terminate resources after learning sessions |

---

## What's Next?

Now that you understand Free Tier limits, let's put everything together in a hands-on lab in **[07 - Hands-on Lab](07-hands-on-lab.md)**.

---

[<-- Previous: AWS CLI Setup](05-aws-cli-setup.md) | [Next: Hands-on Lab -->](07-hands-on-lab.md)
