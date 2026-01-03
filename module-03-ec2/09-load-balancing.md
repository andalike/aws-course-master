# Elastic Load Balancing (ELB) Complete Guide

## Table of Contents

1. [Introduction to Load Balancing](#introduction-to-load-balancing)
2. [ELB Types Comparison](#elb-types-comparison)
3. [Application Load Balancer (ALB)](#application-load-balancer-alb)
4. [Network Load Balancer (NLB)](#network-load-balancer-nlb)
5. [Gateway Load Balancer (GWLB)](#gateway-load-balancer-gwlb)
6. [Classic Load Balancer (CLB)](#classic-load-balancer-clb)
7. [Target Groups](#target-groups)
8. [Health Checks](#health-checks)
9. [SSL/TLS Termination](#ssltls-termination)
10. [Advanced Features](#advanced-features)
11. [Hands-On Setup](#hands-on-setup)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Introduction to Load Balancing

### What is Load Balancing?

Load balancing distributes incoming application traffic across multiple targets (EC2 instances, containers, IP addresses) to ensure high availability, fault tolerance, and scalability.

### Why Use Load Balancing?

```
+------------------------------------------------------------------+
|                 WITHOUT LOAD BALANCER                            |
+------------------------------------------------------------------+
|                                                                   |
|   Users ────────────────────► Single Server                       |
|     │                              │                              |
|     │                              │                              |
|     └── All traffic to one server ─┘                              |
|                                                                   |
|   Problems:                                                       |
|   - Single point of failure                                       |
|   - Cannot scale horizontally                                     |
|   - No automatic failover                                         |
|   - Uneven load distribution                                      |
|                                                                   |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                  WITH LOAD BALANCER                               |
+------------------------------------------------------------------+
|                                                                   |
|                    ┌─────────────────┐                            |
|                    │  Load Balancer  │                            |
|                    │                 │                            |
|   Users ──────────►│   ALB / NLB    │                            |
|                    │                 │                            |
|                    └────────┬────────┘                            |
|                             │                                     |
|              ┌──────────────┼──────────────┐                      |
|              ▼              ▼              ▼                      |
|         ┌────────┐    ┌────────┐    ┌────────┐                   |
|         │Server 1│    │Server 2│    │Server 3│                   |
|         │  (AZ-a)│    │  (AZ-b)│    │  (AZ-c)│                   |
|         └────────┘    └────────┘    └────────┘                   |
|                                                                   |
|   Benefits:                                                       |
|   - High availability across AZs                                  |
|   - Automatic scaling                                             |
|   - Health checks and failover                                    |
|   - Even load distribution                                        |
|                                                                   |
+------------------------------------------------------------------+
```

### Key Concepts

| Term | Definition |
|------|------------|
| **Listener** | Process that checks for connection requests using protocol/port |
| **Target** | Destination for traffic (EC2, IP, Lambda, ALB) |
| **Target Group** | Logical grouping of targets |
| **Health Check** | Determines if targets are healthy |
| **Rule** | Routing logic based on conditions |
| **AZ** | Availability Zone for high availability |

---

## ELB Types Comparison

### Quick Comparison Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ELASTIC LOAD BALANCER TYPES                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │     ALB     │  │     NLB     │  │    GWLB    │  │     CLB     │   │
│  │ Application │  │   Network   │  │   Gateway   │  │   Classic   │   │
│  │   Layer 7   │  │   Layer 4   │  │  Layer 3/4  │  │  Layer 4/7  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│        │                │                │                │            │
│        ▼                ▼                ▼                ▼            │
│  HTTP/HTTPS       TCP/UDP/TLS     Security           Legacy           │
│  WebSocket        Ultra-low       Appliances         Apps             │
│  gRPC             latency         Firewalls                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Detailed Feature Comparison

| Feature | ALB | NLB | GWLB | CLB |
|---------|-----|-----|------|-----|
| **OSI Layer** | 7 (Application) | 4 (Transport) | 3 (Network) | 4 & 7 |
| **Protocols** | HTTP, HTTPS, gRPC, WebSocket | TCP, UDP, TLS | IP | HTTP, HTTPS, TCP, SSL |
| **Performance** | Good | Ultra-high | High | Good |
| **Static IP** | No (use Global Accelerator) | Yes | No | No |
| **Elastic IP** | No | Yes | No | No |
| **PrivateLink** | Yes (consumer) | Yes (producer & consumer) | Yes | No |
| **Path-based Routing** | Yes | No | No | No |
| **Host-based Routing** | Yes | No | No | No |
| **Lambda Targets** | Yes | No | No | No |
| **IP Targets** | Yes | Yes | Yes | No |
| **Container Support** | Yes (dynamic ports) | Yes | Yes | Limited |
| **Source IP Preservation** | X-Forwarded-For | Yes | Yes | X-Forwarded-For |
| **WebSocket** | Yes | Yes | N/A | No |
| **Slow Start** | Yes | No | No | No |
| **Cross-Zone LB** | Free, default on | Paid, default off | N/A | Free |
| **Sticky Sessions** | Yes | Yes (per target group) | N/A | Yes |
| **Connection Draining** | Yes | Yes | Yes | Yes |

### When to Use Each Type

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DECISION TREE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Is it a security/firewall appliance?                                  │
│       │                                                                 │
│       ├── YES ──► GATEWAY LOAD BALANCER                                │
│       │                                                                 │
│       └── NO                                                           │
│            │                                                            │
│            ▼                                                            │
│  Do you need path/host routing or HTTP features?                       │
│       │                                                                 │
│       ├── YES ──► APPLICATION LOAD BALANCER                            │
│       │                                                                 │
│       └── NO                                                           │
│            │                                                            │
│            ▼                                                            │
│  Do you need ultra-low latency or static/Elastic IP?                   │
│       │                                                                 │
│       ├── YES ──► NETWORK LOAD BALANCER                                │
│       │                                                                 │
│       └── NO                                                           │
│            │                                                            │
│            ▼                                                            │
│  Is it a legacy application requiring CLB?                             │
│       │                                                                 │
│       ├── YES ──► CLASSIC LOAD BALANCER (migrate to ALB/NLB)           │
│       │                                                                 │
│       └── NO ──► Use ALB (most common choice)                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Application Load Balancer (ALB)

### Overview

ALB operates at Layer 7 (Application Layer) and is ideal for HTTP/HTTPS traffic. It provides advanced routing capabilities and is the most feature-rich load balancer.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LOAD BALANCER                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                         ┌─────────────────┐                            │
│   Internet ────────────►│      ALB        │                            │
│                         │                 │                            │
│                         │ ┌─────────────┐ │                            │
│                         │ │  Listener   │ │                            │
│                         │ │ HTTPS:443   │ │                            │
│                         │ └──────┬──────┘ │                            │
│                         │        │        │                            │
│                         │ ┌──────▼──────┐ │                            │
│                         │ │   Rules     │ │                            │
│                         │ └──────┬──────┘ │                            │
│                         └────────┼────────┘                            │
│                                  │                                      │
│       ┌──────────────────────────┼──────────────────────────┐          │
│       │                          │                          │          │
│       ▼                          ▼                          ▼          │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐    │
│  │Target Group │          │Target Group │          │Target Group │    │
│  │   /api/*    │          │  /web/*     │          │  default    │    │
│  │             │          │             │          │             │    │
│  │ ┌───┐ ┌───┐│          │ ┌───┐ ┌───┐│          │ ┌───┐ ┌───┐│    │
│  │ │EC2│ │EC2││          │ │EC2│ │EC2││          │ │EC2│ │EC2││    │
│  │ └───┘ └───┘│          │ └───┘ └───┘│          │ └───┘ └───┘│    │
│  └─────────────┘          └─────────────┘          └─────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### ALB Features

#### 1. Path-Based Routing

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATH-BASED ROUTING                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Request: https://example.com/api/users                        │
│                    │                                            │
│                    ▼                                            │
│  ┌─────────────────────────────┐                               │
│  │         ALB Rules           │                               │
│  ├─────────────────────────────┤                               │
│  │ IF path = /api/*            │───► API Target Group          │
│  │ IF path = /static/*         │───► Static Content Group      │
│  │ IF path = /admin/*          │───► Admin Target Group        │
│  │ ELSE (default)              │───► Web Target Group          │
│  └─────────────────────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. Host-Based Routing

```
┌─────────────────────────────────────────────────────────────────┐
│                    HOST-BASED ROUTING                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Single ALB serves multiple domains:                           │
│                                                                 │
│  api.example.com    ───► API Target Group                      │
│  www.example.com    ───► Web Target Group                      │
│  admin.example.com  ───► Admin Target Group                    │
│  *.example.com      ───► Default Target Group                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3. Query String and Header Routing

```
┌─────────────────────────────────────────────────────────────────┐
│               QUERY STRING / HEADER ROUTING                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Query String Examples:                                         │
│  /products?platform=mobile  ───► Mobile Backend                │
│  /products?platform=desktop ───► Desktop Backend               │
│                                                                 │
│  Header Examples:                                               │
│  X-Custom-Header: premium   ───► Premium Service Tier          │
│  X-Custom-Header: standard  ───► Standard Service Tier         │
│  User-Agent: *Mobile*       ───► Mobile Optimized Backend      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Creating ALB with CLI

```bash
# Step 1: Create Application Load Balancer
aws elbv2 create-load-balancer \
    --name my-application-lb \
    --type application \
    --subnets subnet-11111111 subnet-22222222 subnet-33333333 \
    --security-groups sg-0123456789abcdef0 \
    --scheme internet-facing \
    --ip-address-type ipv4 \
    --tags Key=Environment,Value=Production

# Get ALB ARN from output
ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-application-lb/1234567890123456"

# Step 2: Create Target Group
aws elbv2 create-target-group \
    --name my-web-targets \
    --protocol HTTP \
    --port 80 \
    --vpc-id vpc-12345678 \
    --target-type instance \
    --health-check-enabled \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --matcher "HttpCode=200-299"

TG_ARN="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-web-targets/1234567890123456"

# Step 3: Register Targets
aws elbv2 register-targets \
    --target-group-arn $TG_ARN \
    --targets Id=i-1234567890abcdef0 Id=i-0987654321fedcba0

# Step 4: Create HTTPS Listener with Certificate
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTPS \
    --port 443 \
    --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
    --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

LISTENER_ARN="arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/my-application-lb/1234567890123456/1234567890123456"

# Step 5: Create HTTP Listener (redirect to HTTPS)
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions "Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}"
```

### Adding Routing Rules

```bash
# Path-based routing rule
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 10 \
    --conditions Field=path-pattern,Values='/api/*' \
    --actions Type=forward,TargetGroupArn=$API_TG_ARN

# Host-based routing rule
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 20 \
    --conditions Field=host-header,Values='api.example.com' \
    --actions Type=forward,TargetGroupArn=$API_TG_ARN

# Combined path and host routing
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 30 \
    --conditions '[
        {"Field": "host-header", "Values": ["admin.example.com"]},
        {"Field": "path-pattern", "Values": ["/dashboard/*"]}
    ]' \
    --actions Type=forward,TargetGroupArn=$ADMIN_TG_ARN

# Header-based routing
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 40 \
    --conditions '[
        {"Field": "http-header", "HttpHeaderConfig": {"HttpHeaderName": "X-Custom-Header", "Values": ["premium"]}}
    ]' \
    --actions Type=forward,TargetGroupArn=$PREMIUM_TG_ARN

# Query string routing
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 50 \
    --conditions '[
        {"Field": "query-string", "QueryStringConfig": {"Values": [{"Key": "version", "Value": "v2"}]}}
    ]' \
    --actions Type=forward,TargetGroupArn=$V2_TG_ARN

# Fixed response (maintenance page)
aws elbv2 create-rule \
    --listener-arn $LISTENER_ARN \
    --priority 60 \
    --conditions Field=path-pattern,Values='/maintenance' \
    --actions "Type=fixed-response,FixedResponseConfig={ContentType=text/html,StatusCode=503,MessageBody='<h1>Under Maintenance</h1>'}"
```

### Weighted Target Groups (Blue-Green/Canary)

```bash
# Forward to multiple target groups with weights
aws elbv2 modify-rule \
    --rule-arn $RULE_ARN \
    --actions '[
        {
            "Type": "forward",
            "ForwardConfig": {
                "TargetGroups": [
                    {
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:...:targetgroup/blue/...",
                        "Weight": 90
                    },
                    {
                        "TargetGroupArn": "arn:aws:elasticloadbalancing:...:targetgroup/green/...",
                        "Weight": 10
                    }
                ],
                "TargetGroupStickinessConfig": {
                    "Enabled": true,
                    "DurationSeconds": 3600
                }
            }
        }
    ]'
```

---

## Network Load Balancer (NLB)

### Overview

NLB operates at Layer 4 (Transport Layer) and provides ultra-low latency and high throughput. It's ideal for TCP, UDP, and TLS traffic.

### Key Features

```
┌─────────────────────────────────────────────────────────────────┐
│                  NETWORK LOAD BALANCER FEATURES                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Performance:                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Millions of requests per second                        │   │
│  │ - Ultra-low latency (~100 microseconds)                  │   │
│  │ - Handles volatile workloads                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Static IP / Elastic IP:                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - One static IP per AZ                                   │   │
│  │ - Can assign Elastic IPs                                 │   │
│  │ - Ideal for whitelisting                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Source IP Preservation:                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Client IP visible to targets (no X-Forwarded-For)     │   │
│  │ - Essential for IP-based security                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Connection Handling:                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Long-lived connections (gaming, IoT)                   │   │
│  │ - UDP support (DNS, VoIP)                                │   │
│  │ - TLS termination at NLB                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Creating NLB with CLI

```bash
# Create NLB with Elastic IPs
aws elbv2 create-load-balancer \
    --name my-network-lb \
    --type network \
    --subnet-mappings "SubnetId=subnet-11111111,AllocationId=eipalloc-12345678" \
                      "SubnetId=subnet-22222222,AllocationId=eipalloc-87654321" \
    --scheme internet-facing

# Create TCP Target Group
aws elbv2 create-target-group \
    --name my-tcp-targets \
    --protocol TCP \
    --port 80 \
    --vpc-id vpc-12345678 \
    --target-type instance \
    --health-check-enabled \
    --health-check-protocol TCP \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 3 \
    --unhealthy-threshold-count 3

# Create TLS Target Group (pass-through)
aws elbv2 create-target-group \
    --name my-tls-targets \
    --protocol TLS \
    --port 443 \
    --vpc-id vpc-12345678 \
    --target-type instance

# Create UDP Target Group (for DNS, gaming)
aws elbv2 create-target-group \
    --name my-udp-targets \
    --protocol UDP \
    --port 53 \
    --vpc-id vpc-12345678 \
    --target-type instance \
    --health-check-enabled \
    --health-check-protocol TCP \
    --health-check-port 80

# Create TCP Listener
aws elbv2 create-listener \
    --load-balancer-arn $NLB_ARN \
    --protocol TCP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TCP_TG_ARN

# Create TLS Listener (NLB terminates TLS)
aws elbv2 create-listener \
    --load-balancer-arn $NLB_ARN \
    --protocol TLS \
    --port 443 \
    --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
    --certificates CertificateArn=$CERT_ARN \
    --default-actions Type=forward,TargetGroupArn=$TLS_TG_ARN
```

### NLB with AWS PrivateLink

```bash
# Create NLB for VPC Endpoint Service
aws elbv2 create-load-balancer \
    --name privatelink-nlb \
    --type network \
    --subnets subnet-11111111 subnet-22222222 \
    --scheme internal

# Create VPC Endpoint Service
aws ec2 create-vpc-endpoint-service-configuration \
    --network-load-balancer-arns $NLB_ARN \
    --acceptance-required
```

---

## Gateway Load Balancer (GWLB)

### Overview

GWLB is designed for deploying, scaling, and managing third-party virtual network appliances (firewalls, intrusion detection systems, etc.).

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GATEWAY LOAD BALANCER                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Service Consumer VPC              Security VPC                         │
│  ┌─────────────────────┐          ┌─────────────────────────────────┐  │
│  │                     │          │                                 │  │
│  │  ┌───────────┐      │          │    ┌─────────────────────┐     │  │
│  │  │Application│      │          │    │    Gateway Load     │     │  │
│  │  │  Server   │      │          │    │      Balancer       │     │  │
│  │  └─────┬─────┘      │          │    └──────────┬──────────┘     │  │
│  │        │            │          │               │                │  │
│  │        ▼            │          │    ┌──────────┼──────────┐     │  │
│  │  ┌───────────┐      │          │    │          │          │     │  │
│  │  │   GWLB    │◄─────┼──────────┼────┤    ┌─────▼─────┐    │     │  │
│  │  │ Endpoint  │      │          │    │    │ Firewall  │    │     │  │
│  │  └───────────┘      │          │    │    │ Appliance │    │     │  │
│  │        ▲            │          │    │    └───────────┘    │     │  │
│  │        │            │          │    │                     │     │  │
│  │  ┌─────┴─────┐      │          │    │    ┌───────────┐    │     │  │
│  │  │  Internet │      │          │    │    │ Firewall  │    │     │  │
│  │  │  Gateway  │      │          │    │    │ Appliance │    │     │  │
│  │  └───────────┘      │          │    │    └───────────┘    │     │  │
│  │                     │          │    └─────────────────────┘     │  │
│  └─────────────────────┘          └─────────────────────────────────┘  │
│                                                                         │
│  Traffic Flow:                                                          │
│  1. Traffic enters via IGW                                              │
│  2. Routed to GWLB endpoint                                            │
│  3. GWLB sends to appliance (GENEVE encapsulation)                     │
│  4. Appliance inspects and returns to GWLB                             │
│  5. Traffic continues to application                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Creating GWLB

```bash
# Create Gateway Load Balancer
aws elbv2 create-load-balancer \
    --name my-gwlb \
    --type gateway \
    --subnets subnet-11111111 subnet-22222222

# Create Target Group for appliances
aws elbv2 create-target-group \
    --name my-appliance-targets \
    --protocol GENEVE \
    --port 6081 \
    --vpc-id vpc-12345678 \
    --target-type instance \
    --health-check-port 80 \
    --health-check-protocol HTTP \
    --health-check-path /health

# Register appliance instances
aws elbv2 register-targets \
    --target-group-arn $GWLB_TG_ARN \
    --targets Id=i-firewall1 Id=i-firewall2

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn $GWLB_ARN \
    --default-actions Type=forward,TargetGroupArn=$GWLB_TG_ARN

# Create VPC Endpoint Service
aws ec2 create-vpc-endpoint-service-configuration \
    --gateway-load-balancer-arns $GWLB_ARN \
    --no-acceptance-required

# Create GWLB Endpoint in consumer VPC
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-consumer \
    --service-name com.amazonaws.vpce.us-east-1.vpce-svc-xxxxx \
    --vpc-endpoint-type GatewayLoadBalancer \
    --subnet-ids subnet-consumer
```

---

## Classic Load Balancer (CLB)

### Overview

CLB is the legacy load balancer that operates at both Layer 4 and Layer 7. AWS recommends migrating to ALB or NLB.

> **Warning**: Classic Load Balancer is legacy. New applications should use ALB or NLB.

### Migration Path

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLB MIGRATION PATH                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Classic Load Balancer                                          │
│         │                                                       │
│         ├── HTTP/HTTPS traffic ───► Application Load Balancer   │
│         │                                                       │
│         └── TCP/SSL traffic ──────► Network Load Balancer       │
│                                                                 │
│  AWS provides migration wizard in console                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Creating CLB (for reference)

```bash
# Create Classic Load Balancer
aws elb create-load-balancer \
    --load-balancer-name my-classic-lb \
    --listeners "Protocol=HTTP,LoadBalancerPort=80,InstanceProtocol=HTTP,InstancePort=80" \
    --subnets subnet-11111111 subnet-22222222 \
    --security-groups sg-12345678

# Configure health check
aws elb configure-health-check \
    --load-balancer-name my-classic-lb \
    --health-check "Target=HTTP:80/health,Interval=30,UnhealthyThreshold=2,HealthyThreshold=2,Timeout=5"

# Register instances
aws elb register-instances-with-load-balancer \
    --load-balancer-name my-classic-lb \
    --instances i-1234567890abcdef0 i-0987654321fedcba0
```

---

## Target Groups

### Target Types

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TARGET TYPES                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. INSTANCE                                                            │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ - Traffic routed using instance ID                          │    │
│     │ - Primary ENI IP is used                                    │    │
│     │ - Port can be overridden per target                         │    │
│     │ - Works with: ALB, NLB, GWLB                                │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  2. IP                                                                  │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ - Traffic routed to IP address                              │    │
│     │ - Can be private IP in VPC or public IP (NLB)              │    │
│     │ - Enables routing to on-premises servers                    │    │
│     │ - Works with: ALB, NLB, GWLB                                │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  3. LAMBDA                                                              │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ - Traffic routed to Lambda function                         │    │
│     │ - ALB invokes function with HTTP request as event          │    │
│     │ - Response must follow specific format                      │    │
│     │ - Works with: ALB only                                      │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  4. ALB                                                                 │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │ - NLB can target an ALB                                     │    │
│     │ - Combines NLB static IP with ALB routing features          │    │
│     │ - Works with: NLB only                                      │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Target Group Attributes

```bash
# Enable slow start (ALB only)
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=slow_start.duration_seconds,Value=120

# Enable stickiness
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=stickiness.enabled,Value=true \
                 Key=stickiness.type,Value=lb_cookie \
                 Key=stickiness.lb_cookie.duration_seconds,Value=86400

# Configure deregistration delay (connection draining)
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=deregistration_delay.timeout_seconds,Value=30

# Enable cross-zone load balancing (NLB)
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=load_balancing.cross_zone.enabled,Value=true
```

### Lambda Target Group

```bash
# Create Lambda target group
aws elbv2 create-target-group \
    --name my-lambda-tg \
    --target-type lambda

# Register Lambda function
aws elbv2 register-targets \
    --target-group-arn $LAMBDA_TG_ARN \
    --targets Id=arn:aws:lambda:us-east-1:123456789012:function:my-function

# Grant ALB permission to invoke Lambda
aws lambda add-permission \
    --function-name my-function \
    --statement-id elb-invoke \
    --principal elasticloadbalancing.amazonaws.com \
    --action lambda:InvokeFunction \
    --source-arn $LAMBDA_TG_ARN
```

---

## Health Checks

### Health Check Configuration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HEALTH CHECK FLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Load Balancer                                                          │
│       │                                                                 │
│       │  GET /health HTTP/1.1                                          │
│       │  (every IntervalSeconds)                                       │
│       │                                                                 │
│       ▼                                                                 │
│  ┌─────────┐                                                           │
│  │ Target  │                                                           │
│  └────┬────┘                                                           │
│       │                                                                 │
│       │  HTTP 200 OK                                                   │
│       │  (within TimeoutSeconds)                                       │
│       │                                                                 │
│       ▼                                                                 │
│                                                                         │
│  Healthy after:     HealthyThresholdCount consecutive successes        │
│  Unhealthy after:   UnhealthyThresholdCount consecutive failures       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Health Check Parameters

| Parameter | ALB | NLB | Description |
|-----------|-----|-----|-------------|
| **Protocol** | HTTP, HTTPS | TCP, HTTP, HTTPS | Protocol for health check |
| **Port** | traffic-port or 1-65535 | traffic-port or 1-65535 | Port to check |
| **Path** | Required for HTTP(S) | Optional for HTTP(S) | URL path |
| **Interval** | 5-300 seconds | 10 or 30 seconds | Time between checks |
| **Timeout** | 2-120 seconds | 6 or 10 seconds | Wait time for response |
| **Healthy Threshold** | 2-10 | 2-10 | Successes for healthy |
| **Unhealthy Threshold** | 2-10 | 2-10 | Failures for unhealthy |
| **Success Codes** | 200-499 | N/A (TCP) | HTTP codes for success |

### Configuring Health Checks

```bash
# Modify health check settings
aws elbv2 modify-target-group \
    --target-group-arn $TG_ARN \
    --health-check-protocol HTTP \
    --health-check-port traffic-port \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 10 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --matcher "HttpCode=200-299"

# Check target health
aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN
```

### Health Check Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│                 HEALTH CHECK BEST PRACTICES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Create a dedicated health endpoint                          │
│     /health or /healthz                                         │
│                                                                 │
│  2. Check critical dependencies                                 │
│     - Database connection                                       │
│     - Cache connection                                          │
│     - External service connectivity                             │
│                                                                 │
│  3. Return appropriate status codes                             │
│     200 = healthy                                               │
│     503 = unhealthy (graceful)                                 │
│                                                                 │
│  4. Keep health checks lightweight                              │
│     - Fast response (< 1 second)                               │
│     - Minimal resource usage                                    │
│                                                                 │
│  5. Consider startup time                                       │
│     - Initial delay before checks                               │
│     - Grace period for new instances                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Example Health Check Endpoint (Python/Flask)

```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

@app.route('/health')
def health_check():
    health = {
        'status': 'healthy',
        'checks': {}
    }

    # Check database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        health['checks']['database'] = 'ok'
    except Exception as e:
        health['checks']['database'] = 'failed'
        health['status'] = 'unhealthy'

    # Check cache
    try:
        r = redis.Redis(host=REDIS_HOST)
        r.ping()
        health['checks']['cache'] = 'ok'
    except Exception as e:
        health['checks']['cache'] = 'failed'
        health['status'] = 'unhealthy'

    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code
```

---

## SSL/TLS Termination

### TLS Options

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     TLS TERMINATION OPTIONS                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Option 1: TLS Termination at Load Balancer                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Client ──HTTPS──► ALB/NLB ──HTTP──► Target                    │   │
│  │                      │                                          │   │
│  │                   [Decrypt]                                     │   │
│  │                                                                 │   │
│  │  Pros: Simplified cert management, offload CPU from targets    │   │
│  │  Cons: Traffic unencrypted within VPC                          │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Option 2: TLS Pass-through (NLB only)                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Client ──TLS──► NLB ──TLS──► Target                           │   │
│  │                    │                                            │   │
│  │                [Pass-through]                                   │   │
│  │                                                                 │   │
│  │  Pros: End-to-end encryption                                   │   │
│  │  Cons: Certificate management on targets                        │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Option 3: Re-encryption (ALB)                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Client ──HTTPS──► ALB ──HTTPS──► Target                       │   │
│  │                      │                                          │   │
│  │                  [Decrypt]                                      │   │
│  │                  [Re-encrypt]                                   │   │
│  │                                                                 │   │
│  │  Pros: End-to-end encryption with ALB features                 │   │
│  │  Cons: Additional CPU overhead                                  │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Certificate Management

```bash
# Request certificate from ACM
aws acm request-certificate \
    --domain-name example.com \
    --subject-alternative-names "*.example.com" \
    --validation-method DNS

# List certificates
aws acm list-certificates

# Add additional certificate to listener (SNI)
aws elbv2 add-listener-certificates \
    --listener-arn $LISTENER_ARN \
    --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/additional-cert
```

### Security Policies

| Policy Name | Use Case | Protocols |
|-------------|----------|-----------|
| **ELBSecurityPolicy-TLS13-1-2-2021-06** | Recommended default | TLS 1.2, 1.3 |
| **ELBSecurityPolicy-FS-1-2-Res-2020-10** | Forward secrecy | TLS 1.2 |
| **ELBSecurityPolicy-TLS-1-2-2017-01** | Legacy compatibility | TLS 1.2 |
| **ELBSecurityPolicy-2016-08** | Maximum compatibility | TLS 1.0, 1.1, 1.2 |

```bash
# Update listener security policy
aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06
```

### Mutual TLS (mTLS) with ALB

```bash
# Create trust store
aws elbv2 create-trust-store \
    --name my-trust-store \
    --ca-certificates-bundle-s3-bucket my-bucket \
    --ca-certificates-bundle-s3-key ca-bundle.pem

# Modify listener to require client certificates
aws elbv2 modify-listener \
    --listener-arn $LISTENER_ARN \
    --mutual-authentication Mode=verify,TrustStoreArn=arn:aws:elasticloadbalancing:...:truststore/my-trust-store/...
```

---

## Advanced Features

### Connection Draining (Deregistration Delay)

```bash
# Set deregistration delay
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=deregistration_delay.timeout_seconds,Value=120
```

### Slow Start Mode (ALB)

Gradually increases traffic to new targets:

```bash
# Enable slow start (120 seconds)
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=slow_start.duration_seconds,Value=120
```

### Sticky Sessions

```bash
# Application-based stickiness (custom cookie)
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=stickiness.enabled,Value=true \
                 Key=stickiness.type,Value=app_cookie \
                 Key=stickiness.app_cookie.cookie_name,Value=MYCOOKIE \
                 Key=stickiness.app_cookie.duration_seconds,Value=86400

# Load balancer generated cookie
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=stickiness.enabled,Value=true \
                 Key=stickiness.type,Value=lb_cookie \
                 Key=stickiness.lb_cookie.duration_seconds,Value=86400
```

### Access Logs

```bash
# Enable access logs for ALB
aws elbv2 modify-load-balancer-attributes \
    --load-balancer-arn $ALB_ARN \
    --attributes Key=access_logs.s3.enabled,Value=true \
                 Key=access_logs.s3.bucket,Value=my-alb-logs-bucket \
                 Key=access_logs.s3.prefix,Value=my-alb

# S3 bucket policy required
cat << 'EOF' > bucket-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::127311923021:root"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-alb-logs-bucket/my-alb/AWSLogs/123456789012/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket my-alb-logs-bucket \
    --policy file://bucket-policy.json
```

### Cross-Zone Load Balancing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  CROSS-ZONE LOAD BALANCING                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  WITHOUT Cross-Zone (traffic stays in AZ):                             │
│                                                                         │
│       AZ-a (50%)              AZ-b (50%)                               │
│    ┌────────────────┐     ┌────────────────┐                           │
│    │                │     │                │                           │
│    │  ┌───┐  ┌───┐ │     │  ┌───┐  ┌───┐  │                           │
│    │  │25%│  │25%│ │     │  │25%│  │25%│  │                           │
│    │  └───┘  └───┘ │     │  └───┘  └───┘  │                           │
│    │  2 instances  │     │  2 instances   │                           │
│    └────────────────┘     └────────────────┘                           │
│                                                                         │
│  WITH Cross-Zone (traffic distributed evenly):                         │
│                                                                         │
│       AZ-a                    AZ-b                                     │
│    ┌────────────────┐     ┌────────────────┐                           │
│    │                │     │                │                           │
│    │  ┌───┐  ┌───┐ │     │  ┌───┐  ┌───┐  │                           │
│    │  │25%│  │25%│ │     │  │25%│  │25%│  │                           │
│    │  └───┘  └───┘ │     │  └───┘  └───┘  │                           │
│    │  2 instances  │     │  2 instances   │                           │
│    └────────────────┘     └────────────────┘                           │
│                                                                         │
│  ALB: Enabled by default, free                                         │
│  NLB: Disabled by default, charges apply                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```bash
# Enable cross-zone for NLB target group
aws elbv2 modify-target-group-attributes \
    --target-group-arn $TG_ARN \
    --attributes Key=load_balancing.cross_zone.enabled,Value=true
```

---

## Hands-On Setup

### Complete ALB Setup Script

```bash
#!/bin/bash
set -e

# Configuration
REGION="us-east-1"
VPC_ID="vpc-12345678"
SUBNET_1="subnet-11111111"  # AZ-a
SUBNET_2="subnet-22222222"  # AZ-b
AMI_ID="ami-0abcdef1234567890"
KEY_NAME="my-key-pair"
DOMAIN="example.com"

echo "Step 1: Creating Security Groups..."

# ALB Security Group
ALB_SG=$(aws ec2 create-security-group \
    --group-name alb-sg \
    --description "ALB Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp --port 443 --cidr 0.0.0.0/0

# Instance Security Group
INSTANCE_SG=$(aws ec2 create-security-group \
    --group-name instance-sg \
    --description "Instance Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
    --group-id $INSTANCE_SG \
    --protocol tcp --port 80 \
    --source-group $ALB_SG

echo "ALB SG: $ALB_SG"
echo "Instance SG: $INSTANCE_SG"

echo "Step 2: Launching EC2 Instances..."

USER_DATA=$(cat << 'EOF' | base64
#!/bin/bash
yum update -y
yum install -y httpd
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
echo "<h1>Hello from $INSTANCE_ID in $AZ</h1>" > /var/www/html/index.html
echo "OK" > /var/www/html/health
systemctl start httpd
systemctl enable httpd
EOF
)

# Launch instance in AZ-a
INSTANCE_1=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name $KEY_NAME \
    --security-group-ids $INSTANCE_SG \
    --subnet-id $SUBNET_1 \
    --user-data $USER_DATA \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=web-server-1}]" \
    --query 'Instances[0].InstanceId' --output text)

# Launch instance in AZ-b
INSTANCE_2=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name $KEY_NAME \
    --security-group-ids $INSTANCE_SG \
    --subnet-id $SUBNET_2 \
    --user-data $USER_DATA \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=web-server-2}]" \
    --query 'Instances[0].InstanceId' --output text)

echo "Instance 1: $INSTANCE_1"
echo "Instance 2: $INSTANCE_2"

echo "Waiting for instances to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_1 $INSTANCE_2

echo "Step 3: Creating Application Load Balancer..."

ALB_ARN=$(aws elbv2 create-load-balancer \
    --name my-web-alb \
    --type application \
    --subnets $SUBNET_1 $SUBNET_2 \
    --security-groups $ALB_SG \
    --scheme internet-facing \
    --query 'LoadBalancers[0].LoadBalancerArn' --output text)

ALB_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $ALB_ARN \
    --query 'LoadBalancers[0].DNSName' --output text)

echo "ALB ARN: $ALB_ARN"
echo "ALB DNS: $ALB_DNS"

echo "Step 4: Creating Target Group..."

TG_ARN=$(aws elbv2 create-target-group \
    --name my-web-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --target-type instance \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --query 'TargetGroups[0].TargetGroupArn' --output text)

echo "Target Group ARN: $TG_ARN"

echo "Step 5: Registering Targets..."

aws elbv2 register-targets \
    --target-group-arn $TG_ARN \
    --targets Id=$INSTANCE_1 Id=$INSTANCE_2

echo "Step 6: Creating Listener..."

# HTTP Listener (for testing, use HTTPS in production)
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

echo "Step 7: Waiting for targets to be healthy..."

sleep 60  # Wait for health checks

aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo "ALB DNS: http://$ALB_DNS"
echo ""
echo "Test with: curl http://$ALB_DNS"
echo ""
```

### Adding HTTPS Listener

```bash
# Request ACM certificate (must validate)
CERT_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN \
    --subject-alternative-names "*.$DOMAIN" \
    --validation-method DNS \
    --query 'CertificateArn' --output text)

# After validation, create HTTPS listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTPS \
    --port 443 \
    --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
    --certificates CertificateArn=$CERT_ARN \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Modify HTTP listener to redirect to HTTPS
HTTP_LISTENER_ARN=$(aws elbv2 describe-listeners \
    --load-balancer-arn $ALB_ARN \
    --query "Listeners[?Port==\`80\`].ListenerArn" --output text)

aws elbv2 modify-listener \
    --listener-arn $HTTP_LISTENER_ARN \
    --default-actions "Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}"
```

### Cleanup Script

```bash
#!/bin/bash
set -e

echo "Cleaning up resources..."

# Delete listeners
for LISTENER_ARN in $(aws elbv2 describe-listeners \
    --load-balancer-arn $ALB_ARN \
    --query 'Listeners[*].ListenerArn' --output text); do
    aws elbv2 delete-listener --listener-arn $LISTENER_ARN
done

# Delete target group
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete load balancer
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN

# Wait for ALB deletion
echo "Waiting for ALB to be deleted..."
sleep 60

# Terminate instances
aws ec2 terminate-instances --instance-ids $INSTANCE_1 $INSTANCE_2
aws ec2 wait instance-terminated --instance-ids $INSTANCE_1 $INSTANCE_2

# Delete security groups
aws ec2 delete-security-group --group-id $INSTANCE_SG
aws ec2 delete-security-group --group-id $ALB_SG

echo "Cleanup complete!"
```

---

## Best Practices

### 1. High Availability

```
+------------------------------------------------------------------+
|                  HIGH AVAILABILITY CHECKLIST                      |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Deploy ALB/NLB across multiple AZs (minimum 2)              |
|  [ ] Register targets in multiple AZs                             |
|  [ ] Enable cross-zone load balancing                             |
|  [ ] Configure appropriate health check settings                  |
|  [ ] Use Auto Scaling with the load balancer                      |
|                                                                   |
+------------------------------------------------------------------+
```

### 2. Security

```
+------------------------------------------------------------------+
|                     SECURITY CHECKLIST                            |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Use HTTPS with TLS 1.2 or higher                            |
|  [ ] Configure security groups (least privilege)                  |
|  [ ] Enable access logs for auditing                              |
|  [ ] Use AWS WAF with ALB for web protection                     |
|  [ ] Implement proper certificate management                      |
|  [ ] Consider mTLS for high-security applications                 |
|                                                                   |
+------------------------------------------------------------------+
```

### 3. Performance

```
+------------------------------------------------------------------+
|                   PERFORMANCE CHECKLIST                           |
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Choose the right load balancer type for your use case       |
|  [ ] Enable connection keepalive                                  |
|  [ ] Configure appropriate idle timeout                           |
|  [ ] Use slow start for new targets                               |
|  [ ] Monitor latency metrics                                      |
|  [ ] Consider NLB for ultra-low latency requirements              |
|                                                                   |
+------------------------------------------------------------------+
```

### 4. Cost Optimization

- Use ALB for multiple applications (share with host-based routing)
- Clean up unused load balancers and target groups
- Monitor LCU usage for ALB pricing
- Use NLB only when needed (static IP, extreme performance)

---

## Troubleshooting

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 502 Bad Gateway | Targets not responding | Check target health, security groups |
| 503 Service Unavailable | No healthy targets | Verify health checks, target status |
| 504 Gateway Timeout | Target taking too long | Increase timeout, check target performance |
| Connection Refused | Security group rules | Verify SG allows traffic from LB |
| Health checks failing | Wrong path/port | Verify health check configuration |
| Uneven distribution | Sticky sessions enabled | Review stickiness settings |

### Debugging Commands

```bash
# Check load balancer status
aws elbv2 describe-load-balancers \
    --names my-web-alb \
    --query 'LoadBalancers[0].State'

# Check target health
aws elbv2 describe-target-health \
    --target-group-arn $TG_ARN

# Check listener rules
aws elbv2 describe-rules \
    --listener-arn $LISTENER_ARN

# View access logs (if enabled)
aws s3 ls s3://my-alb-logs-bucket/my-alb/AWSLogs/

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ApplicationELB \
    --metric-name HealthyHostCount \
    --dimensions Name=TargetGroup,Value=targetgroup/my-web-tg/1234567890123456 \
                 Name=LoadBalancer,Value=app/my-web-alb/1234567890123456 \
    --start-time 2025-01-01T00:00:00Z \
    --end-time 2025-01-01T01:00:00Z \
    --period 300 \
    --statistics Average
```

### Health Check Troubleshooting

```bash
# Test health check from EC2 instance
curl -v http://localhost/health

# Check if instance can receive traffic from ALB
# On the target instance:
ss -tlnp | grep 80

# Check security group rules
aws ec2 describe-security-groups \
    --group-ids $INSTANCE_SG \
    --query 'SecurityGroups[0].IpPermissions'
```

---

## Summary

### Key Takeaways

1. **ALB** is the most feature-rich, ideal for HTTP/HTTPS applications
2. **NLB** provides ultra-low latency and static IPs for TCP/UDP traffic
3. **GWLB** is designed for security appliances and firewalls
4. **CLB** is legacy - migrate to ALB or NLB
5. **Target Groups** provide flexible routing to various target types
6. **Health Checks** are critical for availability
7. **SSL/TLS** termination simplifies certificate management

### Next Steps

- Practice creating load balancers with different configurations
- Experiment with routing rules and target groups
- Move on to [10-hands-on-lab.md](./10-hands-on-lab.md) for comprehensive labs

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Estimated Reading Time**: 60 minutes
