# 07 - VPC Endpoints

## What are VPC Endpoints?

VPC Endpoints allow you to privately connect your VPC to supported AWS services without requiring an Internet Gateway, NAT device, VPN connection, or AWS Direct Connect.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC ENDPOINT CONCEPT                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   WITHOUT VPC ENDPOINT:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Private Subnet                                                    │   │
│   │   ┌─────────┐    ┌───────────┐    ┌─────┐    ┌─────────────────┐   │   │
│   │   │   EC2   │───►│  NAT GW   │───►│ IGW │───►│    Internet     │   │   │
│   │   └─────────┘    └───────────┘    └─────┘    └────────┬────────┘   │   │
│   │                                                        │            │   │
│   │                                                        ▼            │   │
│   │                                                ┌───────────────┐   │   │
│   │                                                │      S3       │   │   │
│   │                                                └───────────────┘   │   │
│   │                                                                      │   │
│   │   Problems: Data transfer costs, exposure to internet, latency      │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   WITH VPC ENDPOINT:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Private Subnet                                                    │   │
│   │   ┌─────────┐    ┌───────────────────┐    ┌───────────────┐        │   │
│   │   │   EC2   │───►│   VPC Endpoint    │───►│      S3       │        │   │
│   │   └─────────┘    │   (vpce-xxxxx)    │    └───────────────┘        │   │
│   │                  └───────────────────┘                              │   │
│   │                                                                      │   │
│   │   Benefits: No internet, private, lower cost, lower latency         │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Types of VPC Endpoints

| Type | Services | How It Works | Cost |
|------|----------|--------------|------|
| **Gateway Endpoint** | S3, DynamoDB | Route table entry | Free |
| **Interface Endpoint** | 100+ services | ENI with private IP | ~$0.01/hour + data |
| **Gateway Load Balancer Endpoint** | Appliances | For security appliances | Per endpoint + data |

## Gateway Endpoints

Gateway Endpoints are FREE and used for S3 and DynamoDB.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GATEWAY ENDPOINT ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                     │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                    Private Subnet                            │   │   │
│   │   │                                                              │   │   │
│   │   │   ┌─────────┐    Route Table:                               │   │   │
│   │   │   │   EC2   │    ┌──────────────────────────────────────┐   │   │   │
│   │   │   │         │    │ 10.0.0.0/16    → local               │   │   │   │
│   │   │   └────┬────┘    │ 0.0.0.0/0      → nat-xxxxx           │   │   │   │
│   │   │        │         │ pl-xxxxxxxx    → vpce-xxxxx ◄── NEW! │   │   │   │
│   │   │        │         └──────────────────────────────────────┘   │   │   │
│   │   │        │                                                     │   │   │
│   │   └────────┼─────────────────────────────────────────────────────┘   │   │
│   │            │                                                          │   │
│   │            │         ┌──────────────────────────────────────────┐    │   │
│   │            │         │          GATEWAY ENDPOINT                 │    │   │
│   │            └────────►│                                          │    │   │
│   │                      │  Target: com.amazonaws.us-east-1.s3      │    │   │
│   │                      │  Prefix List: pl-xxxxxxxx                │    │   │
│   │                      │  (Contains S3 IP ranges)                 │    │   │
│   │                      │                                          │    │   │
│   │                      └─────────────────────┬────────────────────┘    │   │
│   │                                            │                          │   │
│   └────────────────────────────────────────────┼──────────────────────────┘   │
│                                                │                              │
│                                    ┌───────────▼───────────┐                 │
│                                    │         S3            │                 │
│                                    │   (AWS Backbone)      │                 │
│                                    └───────────────────────┘                 │
│                                                                              │
│   Key Points:                                                               │
│   • Route added automatically to specified route tables                     │
│   • Uses prefix list (pl-xxxx) for S3 IP ranges                            │
│   • Traffic stays on AWS backbone (never touches internet)                  │
│   • FREE - no hourly charge or data processing fees                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Gateway Endpoint Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

## Interface Endpoints (PrivateLink)

Interface Endpoints create an ENI in your subnet with a private IP address.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERFACE ENDPOINT ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                     │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │                    Private Subnet AZ-1a                      │   │   │
│   │   │                                                              │   │   │
│   │   │   ┌─────────┐         ┌───────────────────────────────┐     │   │   │
│   │   │   │   EC2   │         │     Interface Endpoint        │     │   │   │
│   │   │   │         │────────►│                               │     │   │   │
│   │   │   └─────────┘         │   ENI: 10.0.1.50              │     │   │   │
│   │   │                       │   DNS: vpce-xxx.ec2.region... │     │   │   │
│   │   │                       │   SG: sg-endpoint             │     │   │   │
│   │   │                       └───────────────┬───────────────┘     │   │   │
│   │   │                                       │                      │   │   │
│   │   └───────────────────────────────────────┼──────────────────────┘   │   │
│   │                                           │                          │   │
│   │   ┌───────────────────────────────────────┼──────────────────────┐   │   │
│   │   │                    Private Subnet AZ-1b                      │   │   │
│   │   │                                       │                      │   │   │
│   │   │   ┌─────────┐         ┌───────────────▼───────────────┐     │   │   │
│   │   │   │   EC2   │         │     Interface Endpoint        │     │   │   │
│   │   │   │         │────────►│                               │     │   │   │
│   │   │   └─────────┘         │   ENI: 10.0.2.50              │     │   │   │
│   │   │                       │   (HA across AZs)              │     │   │   │
│   │   │                       └───────────────┬───────────────┘     │   │   │
│   │   │                                       │                      │   │   │
│   │   └───────────────────────────────────────┼──────────────────────┘   │   │
│   │                                           │                          │   │
│   └───────────────────────────────────────────┼──────────────────────────┘   │
│                                               │                              │
│                                   ┌───────────▼───────────┐                 │
│                                   │     AWS Service       │                 │
│                                   │  (EC2, SNS, SQS...)   │                 │
│                                   └───────────────────────┘                 │
│                                                                              │
│   Key Points:                                                               │
│   • Creates ENI in each selected subnet                                     │
│   • Has private IP address                                                  │
│   • Supports Security Groups                                                │
│   • Per-hour charge + data processing                                       │
│   • Private DNS optional (replace public DNS)                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Private DNS for Interface Endpoints

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRIVATE DNS RESOLUTION                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   WITHOUT Private DNS:                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Application Code:                                                  │   │
│   │   endpoint_url = "vpce-abc123.ec2.us-east-1.vpce.amazonaws.com"    │   │
│   │   (Must change code to use endpoint-specific URL)                   │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   WITH Private DNS (Recommended):                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                      │   │
│   │   Application Code:                                                  │   │
│   │   endpoint_url = "ec2.us-east-1.amazonaws.com"                      │   │
│   │   (Standard AWS SDK/CLI - no code changes!)                         │   │
│   │                                                                      │   │
│   │   DNS Resolution (inside VPC):                                      │   │
│   │   ec2.us-east-1.amazonaws.com → 10.0.1.50 (endpoint ENI)           │   │
│   │                                                                      │   │
│   │   DNS Resolution (outside VPC):                                     │   │
│   │   ec2.us-east-1.amazonaws.com → 54.x.x.x (public IP)               │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Requirements for Private DNS:                                             │
│   • enableDnsHostnames = true                                               │
│   • enableDnsSupport = true                                                 │
│   • Route 53 Resolver processes queries                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Common Interface Endpoint Services

| Category | Services |
|----------|----------|
| **Compute** | EC2, ECS, EKS, Lambda |
| **Storage** | EBS, EFS, S3 (Interface) |
| **Database** | RDS, DynamoDB, ElastiCache |
| **Messaging** | SQS, SNS, EventBridge |
| **Security** | KMS, Secrets Manager, SSM |
| **Monitoring** | CloudWatch, X-Ray |
| **Management** | CloudFormation, Config |

## Gateway vs Interface Endpoint Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GATEWAY vs INTERFACE ENDPOINTS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────┬────────────────────┬────────────────────────┐  │
│   │      Feature           │  Gateway Endpoint  │  Interface Endpoint    │  │
│   ├────────────────────────┼────────────────────┼────────────────────────┤  │
│   │ Services supported     │ S3, DynamoDB       │ 100+ services          │  │
│   │ Cost                   │ FREE               │ ~$0.01/hr + data       │  │
│   │ Implementation         │ Route table entry  │ ENI in subnet          │  │
│   │ Security Group         │ No                 │ Yes                    │  │
│   │ Endpoint Policy        │ Yes                │ Yes                    │  │
│   │ Access from on-prem    │ No                 │ Yes (via VPN/DX)       │  │
│   │ Cross-region           │ No                 │ No                     │  │
│   │ Private DNS            │ N/A                │ Yes (optional)         │  │
│   │ High Availability      │ AWS managed        │ Deploy in multi-AZ     │  │
│   └────────────────────────┴────────────────────┴────────────────────────┘  │
│                                                                              │
│   Note: S3 has BOTH Gateway (free) and Interface (paid) endpoints          │
│   Use Interface for S3 when you need on-premises access via VPN/DX         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## AWS PrivateLink

PrivateLink allows you to expose your own services to other VPCs or accounts.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AWS PRIVATELINK ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SERVICE PROVIDER VPC                    SERVICE CONSUMER VPC              │
│   (Account A)                             (Account B)                       │
│                                                                              │
│   ┌─────────────────────────────┐        ┌─────────────────────────────┐   │
│   │                             │        │                             │   │
│   │   ┌───────────────────┐     │        │     ┌───────────────────┐   │   │
│   │   │  Your Application │     │        │     │  Client App       │   │   │
│   │   │  (EC2/Container)  │     │        │     │                   │   │   │
│   │   └─────────┬─────────┘     │        │     └─────────┬─────────┘   │   │
│   │             │               │        │               │             │   │
│   │   ┌─────────▼─────────┐     │        │     ┌─────────▼─────────┐   │   │
│   │   │   Network Load    │     │        │     │ Interface Endpoint │   │   │
│   │   │   Balancer (NLB)  │     │        │     │  (vpce-xxxxx)      │   │   │
│   │   └─────────┬─────────┘     │        │     └─────────┬─────────┘   │   │
│   │             │               │        │               │             │   │
│   │   ┌─────────▼─────────┐     │        │               │             │   │
│   │   │ VPC Endpoint      │◄────┼────────┼───────────────┘             │   │
│   │   │ Service           │     │        │                             │   │
│   │   │ (vpce-svc-xxx)    │     │        │                             │   │
│   │   └───────────────────┘     │        │                             │   │
│   │                             │        │                             │   │
│   └─────────────────────────────┘        └─────────────────────────────┘   │
│                                                                              │
│   Flow:                                                                     │
│   1. Provider creates NLB + VPC Endpoint Service                            │
│   2. Consumer creates Interface Endpoint to the service                     │
│   3. Traffic flows over AWS backbone (private)                              │
│                                                                              │
│   Use Cases:                                                                │
│   • SaaS applications                                                       │
│   • Internal shared services                                                │
│   • Selling access to your application                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## VPC Endpoint Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC ENDPOINT BEST PRACTICES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. Use Gateway Endpoints for S3 and DynamoDB (FREE!)                      │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   • Reduces NAT Gateway data processing costs                       │   │
│   │   • Faster access (AWS backbone)                                    │   │
│   │   • More secure (no internet exposure)                              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   2. Deploy Interface Endpoints in Multiple AZs                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   • High availability                                               │   │
│   │   • Lower cross-AZ data transfer                                    │   │
│   │   • Failover support                                                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   3. Use Endpoint Policies                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   • Restrict access to specific resources                           │   │
│   │   • Implement least privilege                                       │   │
│   │   • Add additional security layer                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   4. Enable Private DNS                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   • No application code changes                                     │   │
│   │   • Standard AWS SDK works                                          │   │
│   │   • Transparent to developers                                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   5. Apply Security Groups to Interface Endpoints                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   • Control which resources can access the endpoint                 │   │
│   │   • Restrict by source IP or security group                         │   │
│   │   • Log access with VPC Flow Logs                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Cost Optimization with VPC Endpoints

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COST SAVINGS CALCULATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Scenario: 10 TB/month S3 traffic from private subnets                    │
│                                                                              │
│   WITHOUT Gateway Endpoint:                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   NAT Gateway Hourly:     $0.045 × 730 hrs = $32.85                 │   │
│   │   NAT Gateway Data:       $0.045 × 10,240 GB = $460.80              │   │
│   │   ──────────────────────────────────────────────────                │   │
│   │   Total:                  $493.65/month                              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   WITH Gateway Endpoint:                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   Gateway Endpoint:       $0.00 (FREE!)                             │   │
│   │   Data Transfer:          $0.00 (within region)                     │   │
│   │   ──────────────────────────────────────────────────                │   │
│   │   Total:                  $0.00/month                                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   SAVINGS: $493.65/month = $5,924/year                                     │
│                                                                              │
│   ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│   Interface Endpoint Cost Consideration:                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   Hourly: $0.01/hr × 730 hrs × 3 AZs = $21.90/month                │   │
│   │   Data:   $0.01/GB × data processed                                 │   │
│   │                                                                      │   │
│   │   Worth it if:                                                      │   │
│   │   • Security requirements (no internet exposure)                    │   │
│   │   • Need on-premises access via VPN/DX                              │   │
│   │   • Compliance requirements                                          │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Creating VPC Endpoints with AWS CLI

```bash
# Create Gateway Endpoint for S3
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345678 \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids rtb-private1 rtb-private2 \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=S3-Endpoint}]'

# Create Interface Endpoint for EC2
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345678 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.ec2 \
    --subnet-ids subnet-1a subnet-1b \
    --security-group-ids sg-12345678 \
    --private-dns-enabled

# Create Interface Endpoint for Secrets Manager
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345678 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.secretsmanager \
    --subnet-ids subnet-1a subnet-1b \
    --security-group-ids sg-12345678 \
    --private-dns-enabled

# List available endpoint services
aws ec2 describe-vpc-endpoint-services \
    --query 'ServiceNames[?contains(@, `us-east-1`)]'
```

## Troubleshooting VPC Endpoints

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VPC ENDPOINT TROUBLESHOOTING                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   "Cannot connect to AWS service via endpoint"                              │
│          │                                                                   │
│          ▼                                                                   │
│   ┌──────────────────────────────────┐                                      │
│   │ Check endpoint status            │                                      │
│   │ (Must be "available")            │                                      │
│   └──────────────┬───────────────────┘                                      │
│                  │                                                           │
│        ┌─────────┴─────────┐                                                │
│   Gateway?             Interface?                                           │
│        │                   │                                                │
│        ▼                   ▼                                                │
│   ┌─────────────────┐  ┌─────────────────────────────┐                     │
│   │Check route table│  │Check Security Group on      │                     │
│   │for prefix list  │  │endpoint (allow HTTPS/443)   │                     │
│   │entry            │  │                             │                     │
│   └────────┬────────┘  └──────────────┬──────────────┘                     │
│            │                          │                                     │
│   Missing? │ Present?           ┌─────┴─────┐                              │
│       │    │                Blocked?    Allowed?                            │
│       ▼    ▼                    │            │                              │
│   Add route│              Add rule      ┌────▼────────────────┐            │
│   table    │              for 443       │Check Private DNS    │            │
│            │                            │enabled?             │            │
│            ▼                            └─────────┬───────────┘            │
│   ┌─────────────────┐                             │                         │
│   │Check endpoint   │                   ┌─────────┴─────────┐              │
│   │policy allows    │              Disabled?           Enabled?             │
│   │your actions     │                   │                   │               │
│   └─────────────────┘                   ▼                   ▼               │
│                                   Enable or use     Check VPC DNS          │
│                                   vpce-xxx URL      settings                │
│                                                                              │
│   Additional Checks:                                                        │
│   • DNS resolution (nslookup service.region.amazonaws.com)                 │
│   • VPC Flow Logs for rejected traffic                                     │
│   • Endpoint policy permissions                                             │
│   • IAM permissions for the service                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Gateway Endpoints are FREE** - Use for S3 and DynamoDB
2. **Interface Endpoints cost money** - But provide more flexibility
3. **Private DNS simplifies usage** - No code changes needed
4. **Security Groups on Interface Endpoints** - Additional access control
5. **Endpoint Policies** - Restrict what can be accessed
6. **Multi-AZ deployment** - For high availability of Interface Endpoints

---

**Next:** [08-vpn-direct-connect.md](08-vpn-direct-connect.md) - Hybrid connectivity options
