# AWS WAF and Shield - Web Application Protection

## Introduction

AWS WAF (Web Application Firewall) and AWS Shield work together to protect your web applications from common exploits, bots, and DDoS attacks. This section covers how to implement comprehensive web application protection.

---

## AWS WAF Overview

### What WAF Protects Against

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WAF PROTECTION CAPABILITIES                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  OWASP TOP 10                           BOTS & SCRAPERS                 │
│  ├── SQL Injection                      ├── Bad bots                    │
│  ├── Cross-Site Scripting (XSS)         ├── Scrapers                    │
│  ├── Local File Inclusion               ├── Credential stuffing         │
│  ├── Remote Code Execution              └── Content theft               │
│  ├── Cross-Site Request Forgery                                         │
│  └── Broken Authentication              RATE-BASED ATTACKS              │
│                                         ├── Brute force                 │
│  APPLICATION LAYER ATTACKS              ├── DDoS                        │
│  ├── HTTP floods                        ├── API abuse                   │
│  ├── Malicious payloads                 └── Resource exhaustion         │
│  └── Protocol abuse                                                     │
│                                                                          │
│  GEO-BASED RESTRICTIONS                 IP REPUTATION                   │
│  ├── Block countries                    ├── Tor exit nodes              │
│  ├── Allow only specific regions        ├── Known attackers             │
│  └── Custom geo rules                   └── Anonymous proxies           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### WAF Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WAF ARCHITECTURE                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Internet                                                               │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        WEB ACL                                    │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  Rule 1: AWS Managed - Core Rule Set ──────► Block/Count         │   │
│  │     │                                                            │   │
│  │     ▼                                                            │   │
│  │  Rule 2: AWS Managed - SQL Injection ──────► Block               │   │
│  │     │                                                            │   │
│  │     ▼                                                            │   │
│  │  Rule 3: Rate-based (2000/5min) ───────────► Block               │   │
│  │     │                                                            │   │
│  │     ▼                                                            │   │
│  │  Rule 4: Geo-block (Block Russia, China) ──► Block               │   │
│  │     │                                                            │   │
│  │     ▼                                                            │   │
│  │  Rule 5: Custom IP Blocklist ──────────────► Block               │   │
│  │     │                                                            │   │
│  │     ▼                                                            │   │
│  │  Default Action ───────────────────────────► Allow               │   │
│  │                                                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│     │                                                                   │
│     ▼                                                                   │
│  Protected Resources                                                    │
│  ├── CloudFront Distributions                                          │
│  ├── Application Load Balancers                                        │
│  ├── API Gateway REST APIs                                             │
│  ├── AppSync GraphQL APIs                                              │
│  └── Cognito User Pools                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## WAF Rules and Rule Groups

### Rule Types

| Rule Type | Description | Use Case |
|-----------|-------------|----------|
| **Regular Rule** | Inspect requests based on conditions | IP blocking, geo-blocking |
| **Rate-based Rule** | Track request rate from IPs | Brute force protection |
| **Rule Group** | Collection of rules | Reusable rule sets |
| **Managed Rule Group** | AWS or vendor maintained | OWASP, Bot protection |

### Rule Actions

```
┌─────────────┬────────────────────────────────────────────────────────┐
│  Action     │  Description                                           │
├─────────────┼────────────────────────────────────────────────────────┤
│  ALLOW      │  Allow the request (terminates evaluation)             │
│  BLOCK      │  Block the request (terminates evaluation)             │
│  COUNT      │  Count but continue evaluating                         │
│  CAPTCHA    │  Present CAPTCHA challenge                             │
│  Challenge  │  Present silent challenge (JavaScript)                 │
└─────────────┴────────────────────────────────────────────────────────┘
```

---

## AWS Managed Rule Groups

### Core Rule Groups

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AWS MANAGED RULE GROUPS                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  BASELINE RULE GROUPS                                                   │
│  ├── AWSManagedRulesCommonRuleSet                                       │
│  │   └── OWASP Top 10 protections                                       │
│  ├── AWSManagedRulesAdminProtectionRuleSet                              │
│  │   └── Admin page protection                                          │
│  └── AWSManagedRulesKnownBadInputsRuleSet                               │
│      └── Known malicious patterns                                       │
│                                                                          │
│  USE-CASE SPECIFIC                                                      │
│  ├── AWSManagedRulesSQLiRuleSet                                         │
│  │   └── SQL injection protection                                       │
│  ├── AWSManagedRulesLinuxRuleSet                                        │
│  │   └── Linux-specific exploits                                        │
│  ├── AWSManagedRulesUnixRuleSet                                         │
│  │   └── Unix-specific exploits                                         │
│  ├── AWSManagedRulesWindowsRuleSet                                      │
│  │   └── Windows-specific exploits                                      │
│  ├── AWSManagedRulesPHPRuleSet                                          │
│  │   └── PHP-specific exploits                                          │
│  └── AWSManagedRulesWordPressRuleSet                                    │
│      └── WordPress-specific exploits                                    │
│                                                                          │
│  IP REPUTATION                                                          │
│  ├── AWSManagedRulesAmazonIpReputationList                              │
│  │   └── Known malicious IPs                                            │
│  └── AWSManagedRulesAnonymousIpList                                     │
│      └── Tor nodes, VPNs, proxies                                       │
│                                                                          │
│  BOT CONTROL                                                            │
│  ├── AWSManagedRulesBotControlRuleSet                                   │
│  │   └── Bot detection and management                                   │
│  └── ATP (Account Takeover Prevention)                                  │
│      └── Credential stuffing protection                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Managed Rule Pricing

| Rule Group | WCU Cost | Notes |
|------------|----------|-------|
| Common Rule Set | 700 | Essential for all deployments |
| SQL Injection | 200 | Add for database applications |
| Known Bad Inputs | 200 | Recommended |
| IP Reputation | 25 | Low cost, high value |
| Bot Control | 50 | Additional per-request fee |

---

## Creating a Web ACL

### Via Console

1. Navigate to WAF & Shield console
2. Click "Create web ACL"
3. Define scope (Regional or CloudFront)
4. Add rules and rule groups
5. Set default action
6. Associate with resources

### Via CLI

```bash
# Create a Web ACL
aws wafv2 create-web-acl \
  --name "ProductionWebACL" \
  --scope REGIONAL \
  --default-action Allow={} \
  --description "Production web application firewall" \
  --rules '[
    {
      "Name": "AWS-AWSManagedRulesCommonRuleSet",
      "Priority": 0,
      "Statement": {
        "ManagedRuleGroupStatement": {
          "VendorName": "AWS",
          "Name": "AWSManagedRulesCommonRuleSet"
        }
      },
      "OverrideAction": {"None": {}},
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "AWS-AWSManagedRulesCommonRuleSet"
      }
    },
    {
      "Name": "RateLimitRule",
      "Priority": 1,
      "Statement": {
        "RateBasedStatement": {
          "Limit": 2000,
          "AggregateKeyType": "IP"
        }
      },
      "Action": {"Block": {}},
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "RateLimitRule"
      }
    }
  ]' \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=ProductionWebACL
```

### Via CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: WAF Web ACL for production

Parameters:
  ALBArn:
    Type: String
    Description: ARN of the Application Load Balancer

Resources:
  ProductionWebACL:
    Type: AWS::WAFv2::WebACL
    Properties:
      Name: ProductionWebACL
      Scope: REGIONAL
      Description: Production web application firewall
      DefaultAction:
        Allow: {}
      VisibilityConfig:
        SampledRequestsEnabled: true
        CloudWatchMetricsEnabled: true
        MetricName: ProductionWebACL
      Rules:
        # AWS Managed Common Rule Set
        - Name: AWS-AWSManagedRulesCommonRuleSet
          Priority: 0
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesCommonRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: CommonRuleSet

        # AWS Managed SQL Injection Rule Set
        - Name: AWS-AWSManagedRulesSQLiRuleSet
          Priority: 1
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesSQLiRuleSet
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: SQLiRuleSet

        # AWS IP Reputation List
        - Name: AWS-AWSManagedRulesAmazonIpReputationList
          Priority: 2
          Statement:
            ManagedRuleGroupStatement:
              VendorName: AWS
              Name: AWSManagedRulesAmazonIpReputationList
          OverrideAction:
            None: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: IPReputationList

        # Rate Limiting
        - Name: RateLimitRule
          Priority: 3
          Statement:
            RateBasedStatement:
              Limit: 2000
              AggregateKeyType: IP
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: RateLimitRule

        # Geo Blocking
        - Name: GeoBlockRule
          Priority: 4
          Statement:
            GeoMatchStatement:
              CountryCodes:
                - RU
                - CN
                - KP
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: GeoBlockRule

  WebACLAssociation:
    Type: AWS::WAFv2::WebACLAssociation
    Properties:
      ResourceArn: !Ref ALBArn
      WebACLArn: !GetAtt ProductionWebACL.Arn

Outputs:
  WebACLArn:
    Value: !GetAtt ProductionWebACL.Arn
```

### Via Terraform

```hcl
resource "aws_wafv2_web_acl" "production" {
  name        = "production-web-acl"
  description = "Production web application firewall"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # AWS Managed Common Rule Set
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 0

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"

        # Exclude specific rules if needed
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SizeRestrictions_BODY"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "CommonRuleSet"
      sampled_requests_enabled  = true
    }
  }

  # Rate Limiting
  rule {
    name     = "RateLimitRule"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "RateLimitRule"
      sampled_requests_enabled  = true
    }
  }

  # Custom IP Blocklist
  rule {
    name     = "IPBlocklist"
    priority = 2

    action {
      block {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.blocklist.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name               = "IPBlocklist"
      sampled_requests_enabled  = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name               = "ProductionWebACL"
    sampled_requests_enabled  = true
  }

  tags = {
    Environment = "Production"
  }
}

# IP Set for blocklist
resource "aws_wafv2_ip_set" "blocklist" {
  name               = "ip-blocklist"
  description        = "Blocked IP addresses"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = ["192.0.2.0/24", "198.51.100.0/24"]
}

# Associate with ALB
resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.application.arn
  web_acl_arn  = aws_wafv2_web_acl.production.arn
}
```

---

## Custom Rules

### IP-Based Rules

```bash
# Create an IP set
aws wafv2 create-ip-set \
  --name "BlockedIPs" \
  --scope REGIONAL \
  --ip-address-version IPV4 \
  --addresses "192.0.2.0/24" "198.51.100.0/24"
```

### Rate-Based Rules

```yaml
# CloudFormation rate-based rule
RateLimitLoginRule:
  Name: RateLimitLogin
  Priority: 5
  Statement:
    RateBasedStatement:
      Limit: 100
      AggregateKeyType: IP
      ScopeDownStatement:
        ByteMatchStatement:
          SearchString: /api/login
          FieldToMatch:
            UriPath: {}
          TextTransformations:
            - Priority: 0
              Type: LOWERCASE
          PositionalConstraint: STARTS_WITH
  Action:
    Block: {}
  VisibilityConfig:
    SampledRequestsEnabled: true
    CloudWatchMetricsEnabled: true
    MetricName: RateLimitLogin
```

### Regex Pattern Rules

```yaml
# Block specific patterns
BlockBadUserAgents:
  Name: BlockBadUserAgents
  Priority: 6
  Statement:
    RegexPatternSetReferenceStatement:
      Arn: !GetAtt BadUserAgentPatterns.Arn
      FieldToMatch:
        SingleHeader:
          Name: user-agent
      TextTransformations:
        - Priority: 0
          Type: LOWERCASE
  Action:
    Block: {}
```

### Geographic Rules

```yaml
# Allow only specific countries
AllowOnlyUSandEU:
  Name: AllowOnlyUSandEU
  Priority: 7
  Statement:
    NotStatement:
      Statement:
        GeoMatchStatement:
          CountryCodes:
            - US
            - GB
            - DE
            - FR
            - IT
            - ES
  Action:
    Block: {}
```

---

## AWS Shield

### Shield Standard vs Advanced

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHIELD COMPARISON                                     │
├────────────────────────────────┬────────────────────────────────────────┤
│      SHIELD STANDARD           │         SHIELD ADVANCED                │
├────────────────────────────────┼────────────────────────────────────────┤
│                                │                                        │
│  Cost: FREE                    │  Cost: $3,000/month                    │
│                                │  + Data Transfer Out fees              │
│                                │                                        │
├────────────────────────────────┼────────────────────────────────────────┤
│                                │                                        │
│  Protection Level:             │  Protection Level:                     │
│  ● Layer 3/4 attacks           │  ● Layer 3/4/7 attacks                 │
│  ● SYN/UDP floods              │  ● Application layer attacks           │
│  ● Reflection attacks          │  ● Sophisticated attacks               │
│                                │                                        │
├────────────────────────────────┼────────────────────────────────────────┤
│                                │                                        │
│  Protected Resources:          │  Protected Resources:                  │
│  ● CloudFront                  │  ● All Standard resources              │
│  ● Route 53                    │  ● EC2 instances                       │
│  ● Global Accelerator          │  ● Elastic IPs                         │
│                                │  ● ELB (ALB/NLB/CLB)                   │
│                                │                                        │
├────────────────────────────────┼────────────────────────────────────────┤
│                                │                                        │
│  Features:                     │  Features:                             │
│  ● Automatic                   │  ● 24/7 DDoS Response Team (DRT)       │
│  ● Always on                   │  ● Real-time attack visibility         │
│  ● No SLA                      │  ● Health-based detection              │
│                                │  ● Cost protection (scaling credits)   │
│                                │  ● WAF included (for protected res)    │
│                                │  ● Firewall Manager included           │
│                                │  ● 99.99% SLA                          │
│                                │                                        │
└────────────────────────────────┴────────────────────────────────────────┘
```

### Shield Advanced Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SHIELD ADVANCED ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                         Internet                                        │
│                            │                                            │
│                            ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    AWS EDGE LOCATIONS                             │   │
│  │  ┌──────────────────────────────────────────────────────────┐    │   │
│  │  │            Shield Standard (Always On)                    │    │   │
│  │  │            Layer 3/4 Protection                          │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  │  ┌──────────────────────────────────────────────────────────┐    │   │
│  │  │            Shield Advanced                                │    │   │
│  │  │            ● Enhanced detection                          │    │   │
│  │  │            ● DDoS Response Team                          │    │   │
│  │  │            ● Real-time metrics                           │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                            │                                            │
│                            ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    AWS REGION                                     │   │
│  │  ┌──────────────────────────────────────────────────────────┐    │   │
│  │  │            WAF (Included with Shield Advanced)            │    │   │
│  │  │            Layer 7 Protection                             │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  │                            │                                      │   │
│  │                            ▼                                      │   │
│  │  ┌──────────────────────────────────────────────────────────┐    │   │
│  │  │            Protected Resources                            │    │   │
│  │  │            ALB, EC2, Elastic IP                          │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Enabling Shield Advanced

```bash
# Subscribe to Shield Advanced
aws shield create-subscription

# List protected resources
aws shield list-protections

# Add protection for a resource
aws shield create-protection \
  --name "ProductionALB" \
  --resource-arn "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/abc123"

# Associate a health check
aws shield associate-health-check \
  --protection-id "abc123" \
  --health-check-arn "arn:aws:route53:::healthcheck/xyz789"
```

### Shield Advanced with CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Shield Advanced Protection

Resources:
  # Shield Advanced subscription (done once per account)
  # Note: This is typically done via Console or CLI

  # Protection for ALB
  ALBProtection:
    Type: AWS::Shield::Protection
    Properties:
      Name: ProductionALBProtection
      ResourceArn: !Ref ApplicationLoadBalancer
      Tags:
        - Key: Environment
          Value: Production

  # Protection for CloudFront
  CloudFrontProtection:
    Type: AWS::Shield::Protection
    Properties:
      Name: ProductionCFProtection
      ResourceArn: !GetAtt CloudFrontDistribution.Arn

  # Protection Group
  CriticalResourcesGroup:
    Type: AWS::Shield::ProtectionGroup
    Properties:
      ProtectionGroupId: critical-resources
      Aggregation: MAX
      Pattern: ARBITRARY
      Members:
        - !Ref ApplicationLoadBalancer
        - !GetAtt CloudFrontDistribution.Arn
```

---

## DDoS Protection Strategies

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DDoS DEFENSE LAYERS                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Layer 1: Edge Protection                                               │
│  ├── CloudFront (absorb traffic at edge)                               │
│  ├── Route 53 (DNS-level protection)                                   │
│  └── Global Accelerator (anycast routing)                              │
│                                                                          │
│  Layer 2: Shield Protection                                             │
│  ├── Shield Standard (automatic L3/L4)                                 │
│  └── Shield Advanced (enhanced, L3/L4/L7)                              │
│                                                                          │
│  Layer 3: WAF Protection                                                │
│  ├── Rate limiting                                                      │
│  ├── Bot control                                                        │
│  └── Application-specific rules                                        │
│                                                                          │
│  Layer 4: Application Protection                                        │
│  ├── Auto Scaling (absorb traffic spikes)                              │
│  ├── Elastic Load Balancing (distribute load)                          │
│  └── Application-level validation                                       │
│                                                                          │
│  Layer 5: Origin Protection                                             │
│  ├── Security groups (restrict access)                                 │
│  ├── VPC design (private subnets)                                      │
│  └── Origin cloaking (hide real IPs)                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture for DDoS Resilience

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DDoS-RESILIENT ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Users ──► Route 53 ──► CloudFront ──► WAF ──► ALB ──► EC2 (ASG)       │
│              │              │            │        │         │           │
│              ▼              ▼            ▼        ▼         ▼           │
│           Shield        Shield      Rate      Security  Private        │
│           Standard      Standard    Limit     Groups    Subnets        │
│           (DNS)         (Edge)      Rules                               │
│                                                                          │
│  Benefits:                                                              │
│  ├── Traffic absorbed at CloudFront edge (225+ locations)              │
│  ├── Malicious requests blocked at WAF                                 │
│  ├── Legitimate traffic load-balanced                                  │
│  ├── Auto Scaling handles spikes                                       │
│  └── Origin protected in private subnets                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## WAF Logging and Monitoring

### Enable Logging

```bash
# Create S3 bucket for logs
aws s3 mb s3://aws-waf-logs-123456789012-us-east-1

# Set bucket policy
aws s3api put-bucket-policy \
  --bucket aws-waf-logs-123456789012-us-east-1 \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AWSLogDeliveryWrite",
        "Effect": "Allow",
        "Principal": {"Service": "delivery.logs.amazonaws.com"},
        "Action": "s3:PutObject",
        "Resource": "arn:aws:s3:::aws-waf-logs-123456789012-us-east-1/AWSLogs/*"
      }
    ]
  }'

# Enable logging
aws wafv2 put-logging-configuration \
  --logging-configuration '{
    "ResourceArn": "arn:aws:wafv2:us-east-1:123456789012:regional/webacl/ProductionWebACL/abc123",
    "LogDestinationConfigs": [
      "arn:aws:s3:::aws-waf-logs-123456789012-us-east-1"
    ],
    "RedactedFields": [
      {"SingleHeader": {"Name": "authorization"}}
    ]
  }'
```

### CloudWatch Metrics

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WAF CLOUDWATCH METRICS                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AllowedRequests ──────────► Count of requests allowed                  │
│  BlockedRequests ──────────► Count of requests blocked                  │
│  CountedRequests ──────────► Count of requests counted                  │
│  PassedRequests ───────────► Requests passing through rules             │
│                                                                          │
│  Per-Rule Metrics:                                                      │
│  ├── {RuleName}_AllowedRequests                                        │
│  ├── {RuleName}_BlockedRequests                                        │
│  └── {RuleName}_CountedRequests                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### CloudWatch Dashboard

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "title": "WAF Request Summary",
        "metrics": [
          ["AWS/WAFV2", "AllowedRequests", "WebACL", "ProductionWebACL", "Region", "us-east-1"],
          ["AWS/WAFV2", "BlockedRequests", "WebACL", "ProductionWebACL", "Region", "us-east-1"]
        ],
        "period": 300,
        "stat": "Sum"
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "Block Rate",
        "metrics": [
          [{
            "expression": "m2/(m1+m2)*100",
            "label": "Block Rate %"
          }],
          ["AWS/WAFV2", "AllowedRequests", "WebACL", "ProductionWebACL", {"id": "m1", "visible": false}],
          ["AWS/WAFV2", "BlockedRequests", "WebACL", "ProductionWebACL", {"id": "m2", "visible": false}]
        ],
        "period": 300
      }
    }
  ]
}
```

### CloudWatch Alarms

```yaml
# High block rate alarm
HighBlockRateAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: WAF-HighBlockRate
    MetricName: BlockedRequests
    Namespace: AWS/WAFV2
    Dimensions:
      - Name: WebACL
        Value: ProductionWebACL
      - Name: Region
        Value: us-east-1
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 1000
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SecurityAlarmTopic
```

---

## AWS Firewall Manager

### Centralized WAF Management

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FIREWALL MANAGER ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                    MANAGEMENT ACCOUNT                           │     │
│  │                    (Firewall Manager Admin)                     │     │
│  │                                                                 │     │
│  │  Security Policies:                                            │     │
│  │  ├── WAF Policy (Web ACL rules)                               │     │
│  │  ├── Shield Advanced Policy                                    │     │
│  │  ├── Security Group Policy                                     │     │
│  │  └── Network Firewall Policy                                   │     │
│  │                                                                 │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                │                                        │
│                                ▼                                        │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │                    MEMBER ACCOUNTS                              │     │
│  ├────────────────────────────────────────────────────────────────┤     │
│  │                                                                 │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │     │
│  │  │ Account A   │  │ Account B   │  │ Account C   │             │     │
│  │  │             │  │             │  │             │             │     │
│  │  │ WAF applied │  │ WAF applied │  │ WAF applied │             │     │
│  │  │ automatically│ │ automatically│ │ automatically│            │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │     │
│  │                                                                 │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Creating a Firewall Manager Policy

```bash
# Create WAF policy
aws fms put-policy \
  --policy '{
    "PolicyName": "OrgWideWAFPolicy",
    "SecurityServicePolicyData": {
      "Type": "WAFV2",
      "ManagedServiceData": "{\"type\":\"WAFV2\",\"preProcessRuleGroups\":[{\"ruleGroupArn\":null,\"overrideAction\":{\"type\":\"NONE\"},\"managedRuleGroupIdentifier\":{\"vendorName\":\"AWS\",\"managedRuleGroupName\":\"AWSManagedRulesCommonRuleSet\"},\"ruleGroupType\":\"ManagedRuleGroup\",\"excludeRules\":[]}],\"postProcessRuleGroups\":[],\"defaultAction\":{\"type\":\"ALLOW\"}}"
    },
    "ResourceType": "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "ResourceTags": [],
    "ExcludeResourceTags": false,
    "RemediationEnabled": true,
    "IncludeMap": {
      "ACCOUNT": ["*"]
    }
  }'
```

---

## Best Practices

### WAF Best Practices

1. **Start with Count mode** - Test rules before blocking
2. **Use managed rules** - Leverage AWS expertise
3. **Layer your rules** - Multiple rule groups for defense in depth
4. **Enable logging** - Essential for troubleshooting
5. **Monitor metrics** - Set up alerts for anomalies
6. **Regular reviews** - Update rules based on attack patterns

### DDoS Protection Best Practices

1. **Use CloudFront** - Absorb attacks at the edge
2. **Enable Shield Standard** - Free, always-on protection
3. **Consider Shield Advanced** - For critical applications
4. **Design for scale** - Auto Scaling, ELB
5. **Hide origins** - Don't expose EC2 IPs directly
6. **Plan for attacks** - Have runbooks ready

### Rule Priority Guidelines

```
Priority Order:
1. Allow trusted IPs (0-10)
2. Block known bad IPs (11-20)
3. Rate limiting (21-30)
4. Bot control (31-40)
5. Managed rule groups (41-100)
6. Custom application rules (101+)
```

---

## Cost Optimization

### WAF Pricing

| Component | Cost |
|-----------|------|
| Web ACL | $5/month |
| Rule | $1/month per rule |
| Requests | $0.60 per 1M requests |
| Bot Control | $10/month + $1 per 1M requests |

### Cost Optimization Tips

1. **Consolidate Web ACLs** - Share across resources
2. **Use rule groups efficiently** - Avoid duplicate rules
3. **Monitor request volume** - Right-size protection
4. **Consider scope** - Use CloudFront scope for global apps

---

## Key Takeaways

1. **WAF protects Layer 7** - Application layer attacks
2. **Shield protects Layers 3/4** - Network and transport layer
3. **Use managed rules** - AWS-maintained protection
4. **Layer your defenses** - Edge + WAF + application
5. **Enable logging** - Critical for incident response
6. **Monitor and alert** - Detect attacks early
7. **Use Firewall Manager** - For multi-account deployments

---

## Next Steps

Continue to [06-kms.md](06-kms.md) to learn about encryption key management.
