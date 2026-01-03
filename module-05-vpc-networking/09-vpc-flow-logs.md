# 09 - VPC Flow Logs

## What are VPC Flow Logs?

VPC Flow Logs capture information about IP traffic going to and from network interfaces in your VPC. Flow logs help you monitor and troubleshoot connectivity issues, understand traffic patterns, and detect security threats.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VPC FLOW LOGS CONCEPT                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                              INTERNET                                            │
│                                  │                                               │
│                                  ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                              VPC                                          │  │
│   │                                                                           │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│   │   │                         Subnet                                   │    │  │
│   │   │                                                                  │    │  │
│   │   │   ┌─────────────┐         ┌─────────────┐         ┌──────────┐  │    │  │
│   │   │   │    EC2      │ ◄─────► │    EC2      │ ◄─────► │   RDS    │  │    │  │
│   │   │   │  (ENI-1)    │         │  (ENI-2)    │         │  (ENI-3) │  │    │  │
│   │   │   └──────┬──────┘         └──────┬──────┘         └─────┬────┘  │    │  │
│   │   │          │                       │                      │       │    │  │
│   │   │          │    FLOW LOGS CAPTURE  │                      │       │    │  │
│   │   │          ▼                       ▼                      ▼       │    │  │
│   │   │   ┌──────────────────────────────────────────────────────────┐  │    │  │
│   │   │   │                    FLOW LOG DATA                         │  │    │  │
│   │   │   │                                                          │  │    │  │
│   │   │   │  Source IP, Dest IP, Source Port, Dest Port, Protocol   │  │    │  │
│   │   │   │  Packets, Bytes, Start Time, End Time, Action, Status   │  │    │  │
│   │   │   │                                                          │  │    │  │
│   │   │   └──────────────────────────────────────────────────────────┘  │    │  │
│   │   │                              │                                   │    │  │
│   │   └──────────────────────────────┼───────────────────────────────────┘    │  │
│   │                                  │                                        │  │
│   └──────────────────────────────────┼────────────────────────────────────────┘  │
│                                      │                                           │
│                    ┌─────────────────┼─────────────────┐                        │
│                    │                 │                 │                        │
│                    ▼                 ▼                 ▼                        │
│            ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                 │
│            │ CloudWatch  │   │     S3      │   │   Kinesis   │                 │
│            │    Logs     │   │   Bucket    │   │  Firehose   │                 │
│            └─────────────┘   └─────────────┘   └─────────────┘                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Flow Log Levels

You can create flow logs at three levels:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FLOW LOG LEVELS                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. VPC LEVEL (Captures ALL traffic in VPC)                                    │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                         │   │
│   │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                   │   │
│   │   │  Subnet A   │   │  Subnet B   │   │  Subnet C   │                   │   │
│   │   │ ┌───┐ ┌───┐ │   │ ┌───┐ ┌───┐ │   │ ┌───┐ ┌───┐ │                   │   │
│   │   │ │EC2│ │EC2│ │   │ │EC2│ │RDS│ │   │ │EC2│ │ELB│ │                   │   │
│   │   │ └───┘ └───┘ │   │ └───┘ └───┘ │   │ └───┘ └───┘ │                   │   │
│   │   └─────────────┘   └─────────────┘   └─────────────┘                   │   │
│   │                                                                          │   │
│   │   FLOW LOG: Captures ALL ENI traffic in entire VPC                      │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   2. SUBNET LEVEL (Captures traffic for specific subnet)                        │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                         │   │
│   │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                   │   │
│   │   │  Subnet A   │   │  Subnet B   │   │  Subnet C   │                   │   │
│   │   │ ┌───┐ ┌───┐ │   │ ┌───┐ ┌───┐ │   │             │                   │   │
│   │   │ │EC2│ │EC2│ │   │ │EC2│ │RDS│ │   │   (no log)  │                   │   │
│   │   │ └───┘ └───┘ │   │ └───┘ └───┘ │   │             │                   │   │
│   │   │  FLOW LOG ◄─┘   └──► FLOW LOG │   └─────────────┘                   │   │
│   │   └─────────────┘   └─────────────┘                                     │   │
│   │                                                                          │   │
│   │   Separate flow logs for Subnet A and Subnet B only                     │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   3. ENI LEVEL (Captures traffic for specific network interface)                │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                         │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │                         Subnet                                   │   │   │
│   │   │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │   │   │
│   │   │   │    EC2      │   │    EC2      │   │    RDS      │           │   │   │
│   │   │   │   ENI-1     │   │   ENI-2     │   │   ENI-3     │           │   │   │
│   │   │   │  FLOW LOG ◄─┘   │  (no log)   │   │  (no log)   │           │   │   │
│   │   │   └─────────────┘   └─────────────┘   └─────────────┘           │   │   │
│   │   │                                                                  │   │   │
│   │   └──────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   │   Flow log for only ENI-1 (specific EC2 instance)                       │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Flow Log Record Format

### Default Format (Version 2)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DEFAULT FLOW LOG FORMAT                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   version account-id interface-id srcaddr dstaddr srcport dstport              │
│   protocol packets bytes start end action log-status                           │
│                                                                                  │
│   Example Record:                                                               │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ 2 123456789012 eni-1234567890abcdef0 172.31.16.139 172.31.16.21         │   │
│   │ 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK                      │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Field Breakdown:                                                              │
│   ┌───────────────────┬──────────────────────────────────────────────────────┐  │
│   │ Field             │ Value                                                │  │
│   ├───────────────────┼──────────────────────────────────────────────────────┤  │
│   │ version           │ 2                                                    │  │
│   │ account-id        │ 123456789012                                         │  │
│   │ interface-id      │ eni-1234567890abcdef0                                │  │
│   │ srcaddr           │ 172.31.16.139 (source IP)                            │  │
│   │ dstaddr           │ 172.31.16.21 (destination IP)                        │  │
│   │ srcport           │ 20641 (source port)                                  │  │
│   │ dstport           │ 22 (destination port - SSH)                          │  │
│   │ protocol          │ 6 (TCP)                                              │  │
│   │ packets           │ 20                                                   │  │
│   │ bytes             │ 4249                                                 │  │
│   │ start             │ 1418530010 (Unix timestamp)                          │  │
│   │ end               │ 1418530070 (Unix timestamp)                          │  │
│   │ action            │ ACCEPT                                               │  │
│   │ log-status        │ OK                                                   │  │
│   └───────────────────┴──────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Protocol Numbers Reference

| Protocol Number | Protocol Name |
|-----------------|---------------|
| 1 | ICMP |
| 6 | TCP |
| 17 | UDP |
| 47 | GRE |
| 50 | ESP (IPsec) |
| 51 | AH (IPsec) |

### Action Values

| Action | Description |
|--------|-------------|
| ACCEPT | Traffic was allowed by security groups/NACLs |
| REJECT | Traffic was blocked by security groups/NACLs |

### Log-Status Values

| Status | Description |
|--------|-------------|
| OK | Data logged normally |
| NODATA | No network traffic during aggregation interval |
| SKIPDATA | Some records skipped (capacity limit) |

### Custom Format (Additional Fields)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CUSTOM FLOW LOG FIELDS                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   Available Custom Fields (select what you need):                               │
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │ Field                  │ Description                                     │  │
│   ├──────────────────────────────────────────────────────────────────────────┤  │
│   │ ${vpc-id}              │ VPC ID                                          │  │
│   │ ${subnet-id}           │ Subnet ID                                       │  │
│   │ ${instance-id}         │ EC2 instance ID                                 │  │
│   │ ${tcp-flags}           │ TCP flags (SYN, ACK, FIN, etc.)                 │  │
│   │ ${type}                │ Traffic type (IPv4, IPv6)                       │  │
│   │ ${pkt-srcaddr}         │ Packet source address                           │  │
│   │ ${pkt-dstaddr}         │ Packet destination address                      │  │
│   │ ${region}              │ AWS region                                      │  │
│   │ ${az-id}               │ Availability Zone ID                            │  │
│   │ ${sublocation-type}    │ Sublocation type                                │  │
│   │ ${sublocation-id}      │ Sublocation ID                                  │  │
│   │ ${pkt-src-aws-service} │ Source AWS service                              │  │
│   │ ${pkt-dst-aws-service} │ Destination AWS service                         │  │
│   │ ${flow-direction}      │ ingress or egress                               │  │
│   │ ${traffic-path}        │ Path traffic took (e.g., via TGW, VPG)         │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   Example Custom Format:                                                        │
│   ${version} ${vpc-id} ${subnet-id} ${instance-id} ${srcaddr} ${dstaddr}       │
│   ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${action}              │
│   ${tcp-flags} ${flow-direction}                                               │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Publishing Flow Logs

### Publishing to CloudWatch Logs

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FLOW LOGS TO CLOUDWATCH                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                         │   │
│   │   ┌─────────┐   ┌─────────┐   ┌─────────┐                               │   │
│   │   │  ENI-1  │   │  ENI-2  │   │  ENI-3  │                               │   │
│   │   └────┬────┘   └────┬────┘   └────┬────┘                               │   │
│   │        │             │             │                                     │   │
│   │        └─────────────┼─────────────┘                                     │   │
│   │                      │                                                   │   │
│   │               Flow Log                                                   │   │
│   │                      │                                                   │   │
│   └──────────────────────┼───────────────────────────────────────────────────┘   │
│                          │                                                       │
│                          ▼                                                       │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                    CloudWatch Logs                                        │  │
│   │                                                                           │  │
│   │   Log Group: /aws/vpc/flow-logs                                          │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│   │   │                                                                  │    │  │
│   │   │   Log Stream: eni-1234567890abcdef0-accept                      │    │  │
│   │   │   Log Stream: eni-1234567890abcdef0-reject                      │    │  │
│   │   │   Log Stream: eni-0987654321fedcba0-accept                      │    │  │
│   │   │                                                                  │    │  │
│   │   └─────────────────────────────────────────────────────────────────┘    │  │
│   │                                                                           │  │
│   │   Benefits:                                                              │  │
│   │   • Real-time querying with CloudWatch Logs Insights                    │  │
│   │   • Metric filters for alerts                                           │  │
│   │   • Integration with CloudWatch Alarms                                  │  │
│   │   • Log retention policies                                              │  │
│   │                                                                           │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   Required IAM Role Trust Policy:                                               │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │ {                                                                         │  │
│   │   "Version": "2012-10-17",                                               │  │
│   │   "Statement": [                                                          │  │
│   │     {                                                                     │  │
│   │       "Effect": "Allow",                                                 │  │
│   │       "Principal": {"Service": "vpc-flow-logs.amazonaws.com"},           │  │
│   │       "Action": "sts:AssumeRole"                                         │  │
│   │     }                                                                     │  │
│   │   ]                                                                       │  │
│   │ }                                                                         │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   Required IAM Role Permissions:                                                │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │ {                                                                         │  │
│   │   "Version": "2012-10-17",                                               │  │
│   │   "Statement": [                                                          │  │
│   │     {                                                                     │  │
│   │       "Effect": "Allow",                                                 │  │
│   │       "Action": [                                                         │  │
│   │         "logs:CreateLogGroup",                                           │  │
│   │         "logs:CreateLogStream",                                          │  │
│   │         "logs:PutLogEvents",                                             │  │
│   │         "logs:DescribeLogGroups",                                        │  │
│   │         "logs:DescribeLogStreams"                                        │  │
│   │       ],                                                                  │  │
│   │       "Resource": "*"                                                     │  │
│   │     }                                                                     │  │
│   │   ]                                                                       │  │
│   │ }                                                                         │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Publishing to S3

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FLOW LOGS TO S3                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              VPC                                         │   │
│   │        Flow Log                                                          │   │
│   └────────────────────────────────────────────────────────────────────────┬─┘   │
│                                                                             │     │
│                                                                             ▼     │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                           S3 Bucket                                       │  │
│   │                                                                           │  │
│   │   Folder Structure:                                                      │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│   │   │                                                                  │    │  │
│   │   │   s3://my-flow-logs-bucket/                                     │    │  │
│   │   │   └── AWSLogs/                                                  │    │  │
│   │   │       └── 123456789012/                    (Account ID)         │    │  │
│   │   │           └── vpcflowlogs/                                      │    │  │
│   │   │               └── us-east-1/               (Region)             │    │  │
│   │   │                   └── 2024/                (Year)               │    │  │
│   │   │                       └── 01/              (Month)              │    │  │
│   │   │                           └── 15/          (Day)                │    │  │
│   │   │                               └── eni-xxx.log.gz               │    │  │
│   │   │                                                                  │    │  │
│   │   └─────────────────────────────────────────────────────────────────┘    │  │
│   │                                                                           │  │
│   │   File Formats:                                                          │  │
│   │   • Plain text (default)                                                 │  │
│   │   • Parquet (for Athena queries)                                        │  │
│   │                                                                           │  │
│   │   Benefits:                                                              │  │
│   │   • Cost-effective for long-term storage                                │  │
│   │   • Query with Athena                                                   │  │
│   │   • Lifecycle policies for retention                                    │  │
│   │   • Cross-account delivery supported                                    │  │
│   │                                                                           │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│   Required S3 Bucket Policy:                                                    │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │ {                                                                         │  │
│   │   "Version": "2012-10-17",                                               │  │
│   │   "Statement": [                                                          │  │
│   │     {                                                                     │  │
│   │       "Sid": "AWSLogDeliveryAclCheck",                                   │  │
│   │       "Effect": "Allow",                                                 │  │
│   │       "Principal": {"Service": "delivery.logs.amazonaws.com"},           │  │
│   │       "Action": "s3:GetBucketAcl",                                       │  │
│   │       "Resource": "arn:aws:s3:::my-flow-logs-bucket"                     │  │
│   │     },                                                                    │  │
│   │     {                                                                     │  │
│   │       "Sid": "AWSLogDeliveryWrite",                                      │  │
│   │       "Effect": "Allow",                                                 │  │
│   │       "Principal": {"Service": "delivery.logs.amazonaws.com"},           │  │
│   │       "Action": "s3:PutObject",                                          │  │
│   │       "Resource": "arn:aws:s3:::my-flow-logs-bucket/AWSLogs/*",          │  │
│   │       "Condition": {                                                      │  │
│   │         "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}   │  │
│   │       }                                                                   │  │
│   │     }                                                                     │  │
│   │   ]                                                                       │  │
│   │ }                                                                         │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Creating Flow Logs

### Using AWS CLI

```bash
# Create Flow Log to CloudWatch Logs
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flow-logs \
    --deliver-logs-permission-arn arn:aws:iam::123456789012:role/flowlogsRole \
    --tag-specifications 'ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=my-vpc-flow-log}]'

# Create Flow Log to S3
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type s3 \
    --log-destination arn:aws:s3:::my-flow-logs-bucket \
    --log-format '${version} ${vpc-id} ${subnet-id} ${instance-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status}' \
    --max-aggregation-interval 60

# Create Flow Log for specific ENI
aws ec2 create-flow-logs \
    --resource-type NetworkInterface \
    --resource-ids eni-0123456789abcdef0 \
    --traffic-type REJECT \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flow-logs/rejected

# Create Flow Log with Parquet format (for S3)
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0123456789abcdef0 \
    --traffic-type ALL \
    --log-destination-type s3 \
    --log-destination arn:aws:s3:::my-flow-logs-bucket \
    --destination-options FileFormat=parquet,HiveCompatiblePartitions=true,PerHourPartition=true
```

### Using Terraform

```hcl
# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "flow_log" {
  name              = "/aws/vpc/flow-logs"
  retention_in_days = 30
}

# IAM Role for Flow Logs
resource "aws_iam_role" "flow_log" {
  name = "vpc-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "flow_log" {
  name = "vpc-flow-log-policy"
  role = aws_iam_role.flow_log.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# VPC Flow Log
resource "aws_flow_log" "main" {
  vpc_id                   = aws_vpc.main.id
  traffic_type             = "ALL"
  log_destination_type     = "cloud-watch-logs"
  log_destination          = aws_cloudwatch_log_group.flow_log.arn
  iam_role_arn             = aws_iam_role.flow_log.arn
  max_aggregation_interval = 60

  tags = {
    Name = "vpc-flow-log"
  }
}
```

## Analyzing Flow Logs

### CloudWatch Logs Insights Queries

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CLOUDWATCH LOGS INSIGHTS QUERIES                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. Find rejected traffic:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ fields @timestamp, srcAddr, dstAddr, dstPort, action                    │   │
│   │ | filter action = "REJECT"                                              │   │
│   │ | sort @timestamp desc                                                  │   │
│   │ | limit 100                                                             │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   2. Top 10 talkers by bytes:                                                   │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ stats sum(bytes) as totalBytes by srcAddr                               │   │
│   │ | sort totalBytes desc                                                  │   │
│   │ | limit 10                                                              │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   3. Traffic by destination port:                                               │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ stats count(*) as requestCount by dstPort                               │   │
│   │ | sort requestCount desc                                                │   │
│   │ | limit 10                                                              │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   4. SSH attempts (port 22):                                                    │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ fields @timestamp, srcAddr, dstAddr, action                             │   │
│   │ | filter dstPort = 22                                                   │   │
│   │ | stats count(*) as attempts by srcAddr, action                         │   │
│   │ | sort attempts desc                                                    │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   5. Traffic between specific IPs:                                              │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ fields @timestamp, srcAddr, dstAddr, srcPort, dstPort, action           │   │
│   │ | filter srcAddr = "10.0.1.50" and dstAddr = "10.0.2.100"              │   │
│   │ | sort @timestamp desc                                                  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   6. Rejected traffic by hour:                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ filter action = "REJECT"                                                │   │
│   │ | stats count(*) as rejectedCount by bin(1h)                            │   │
│   │ | sort bin asc                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   7. Potential port scanning (many ports from same source):                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ stats count(distinct(dstPort)) as portCount by srcAddr                  │   │
│   │ | filter portCount > 100                                                │   │
│   │ | sort portCount desc                                                   │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Athena Queries (for S3)

```sql
-- Create table for flow logs
CREATE EXTERNAL TABLE IF NOT EXISTS vpc_flow_logs (
  version int,
  account_id string,
  interface_id string,
  srcaddr string,
  dstaddr string,
  srcport int,
  dstport int,
  protocol bigint,
  packets bigint,
  bytes bigint,
  start_time bigint,
  end_time bigint,
  action string,
  log_status string
)
PARTITIONED BY (
  `date` date
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ' '
LOCATION 's3://my-flow-logs-bucket/AWSLogs/123456789012/vpcflowlogs/us-east-1/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Load partitions
MSCK REPAIR TABLE vpc_flow_logs;

-- Query: Find all rejected traffic
SELECT srcaddr, dstaddr, dstport, protocol, packets, bytes
FROM vpc_flow_logs
WHERE action = 'REJECT'
  AND date = DATE '2024-01-15'
ORDER BY bytes DESC
LIMIT 100;

-- Query: Top source IPs by data transfer
SELECT srcaddr,
       SUM(bytes) as total_bytes,
       SUM(packets) as total_packets,
       COUNT(*) as flow_count
FROM vpc_flow_logs
WHERE date >= DATE '2024-01-01'
GROUP BY srcaddr
ORDER BY total_bytes DESC
LIMIT 20;

-- Query: Traffic analysis by hour
SELECT date_trunc('hour', from_unixtime(start_time)) as hour,
       action,
       COUNT(*) as flow_count,
       SUM(bytes) as total_bytes
FROM vpc_flow_logs
WHERE date = DATE '2024-01-15'
GROUP BY date_trunc('hour', from_unixtime(start_time)), action
ORDER BY hour;
```

## Troubleshooting with Flow Logs

### Common Connectivity Issues

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        TROUBLESHOOTING SCENARIOS                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SCENARIO 1: Instance cannot reach internet                                    │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Check flow logs for traffic to internet destinations:                 │   │
│   │                                                                          │   │
│   │   srcaddr=10.0.1.50, dstaddr=8.8.8.8, action=REJECT                     │   │
│   │       │                                                                  │   │
│   │       └── REJECT means Security Group or NACL blocking                  │   │
│   │                                                                          │   │
│   │   srcaddr=10.0.1.50, dstaddr=8.8.8.8, action=ACCEPT                     │   │
│   │       │                                                                  │   │
│   │       └── ACCEPT but no response? Check:                                │   │
│   │           • Route table (missing route to IGW/NAT)                       │   │
│   │           • NAT Gateway issue                                            │   │
│   │           • Target not responding                                        │   │
│   │                                                                          │   │
│   │   NO LOGS FOUND for 10.0.1.50?                                          │   │
│   │       │                                                                  │   │
│   │       └── Check:                                                        │   │
│   │           • Flow log is active and attached                             │   │
│   │           • Instance ENI correct                                        │   │
│   │           • Application actually sending traffic                        │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   SCENARIO 2: Cannot SSH to instance                                           │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   Your IP: 203.0.113.50                                                 │   │
│   │   Instance: 10.0.1.100                                                  │   │
│   │                                                                          │   │
│   │   Check for inbound traffic:                                            │   │
│   │   srcaddr=203.0.113.50, dstaddr=10.0.1.100, dstport=22                  │   │
│   │                                                                          │   │
│   │   Flow Log Analysis:                                                    │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │ If action=REJECT:                                               │   │   │
│   │   │   • Security Group doesn't allow your IP on port 22            │   │   │
│   │   │   • NACL blocking inbound port 22                              │   │   │
│   │   │   • NACL blocking outbound ephemeral ports                     │   │   │
│   │   │                                                                  │   │   │
│   │   │ If action=ACCEPT but no connection:                            │   │   │
│   │   │   • Check for return traffic (outbound)                        │   │   │
│   │   │   • Instance might have local firewall (iptables)             │   │   │
│   │   │   • SSH service might not be running                           │   │   │
│   │   │                                                                  │   │   │
│   │   │ If NO LOGS:                                                     │   │   │
│   │   │   • Traffic never reached instance                             │   │   │
│   │   │   • Check route tables, IGW attachment                         │   │   │
│   │   │   • Check your local firewall                                  │   │   │
│   │   └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   SCENARIO 3: Application cannot connect to RDS                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   App Server: 10.0.1.50                                                 │   │
│   │   RDS: 10.0.2.100:3306                                                  │   │
│   │                                                                          │   │
│   │   Check outbound from app server:                                       │   │
│   │   srcaddr=10.0.1.50, dstaddr=10.0.2.100, dstport=3306                   │   │
│   │                                                                          │   │
│   │   Check inbound at RDS:                                                 │   │
│   │   srcaddr=10.0.1.50, dstaddr=10.0.2.100, dstport=3306                   │   │
│   │                                                                          │   │
│   │   Common Issues:                                                        │   │
│   │   ┌──────────────────────────────────────────────────────────────────┐  │   │
│   │   │ • RDS Security Group doesn't allow app server's SG              │  │   │
│   │   │ • Different subnets with restrictive NACLs                      │  │   │
│   │   │ • App trying wrong port                                         │  │   │
│   │   │ • RDS in different VPC (need peering/TGW)                       │  │   │
│   │   └──────────────────────────────────────────────────────────────────┘  │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Troubleshooting Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FLOW LOG TROUBLESHOOTING FLOWCHART                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   START: Connectivity Issue Reported                                            │
│            │                                                                     │
│            ▼                                                                     │
│   ┌─────────────────────────┐                                                   │
│   │ Check Flow Logs for     │                                                   │
│   │ relevant traffic        │                                                   │
│   └───────────┬─────────────┘                                                   │
│               │                                                                  │
│               ▼                                                                  │
│   ┌─────────────────────────┐    No logs     ┌──────────────────────────────┐   │
│   │ Flow logs exist?        │───────────────►│ Check:                       │   │
│   └───────────┬─────────────┘                │ • Flow log enabled?          │   │
│               │ Yes                           │ • Correct resource attached? │   │
│               ▼                               │ • Traffic type filter?       │   │
│   ┌─────────────────────────┐                │ • Aggregation interval?      │   │
│   │ What is action field?   │                └──────────────────────────────┘   │
│   └───────────┬─────────────┘                                                   │
│               │                                                                  │
│       ┌───────┴───────┐                                                         │
│       │               │                                                         │
│       ▼               ▼                                                         │
│   REJECT          ACCEPT                                                        │
│       │               │                                                         │
│       ▼               ▼                                                         │
│   ┌───────────┐   ┌───────────────────────────────────────────────────────┐    │
│   │ Check:    │   │ Traffic allowed but still not working?               │    │
│   │           │   │                                                       │    │
│   │ 1. SG     │   │ Check:                                               │    │
│   │    rules  │   │ 1. Response traffic (other direction)               │    │
│   │           │   │ 2. Routing (correct route table?)                   │    │
│   │ 2. NACL   │   │ 3. Target service running?                          │    │
│   │    rules  │   │ 4. Target firewall (iptables, Windows FW)           │    │
│   │           │   │ 5. Application configuration                        │    │
│   │ 3. Check  │   │ 6. DNS resolution                                   │    │
│   │    both   │   │ 7. MTU issues (packet fragmentation)                │    │
│   │    inbound│   │                                                       │    │
│   │    and    │   └───────────────────────────────────────────────────────┘    │
│   │    outbound    │                                                            │
│   └───────────┘                                                                 │
│                                                                                  │
│   REMEMBER:                                                                     │
│   • NACL is STATELESS - check BOTH inbound AND outbound rules                  │
│   • Security Group is STATEFUL - return traffic auto-allowed                   │
│   • Flow logs show what was allowed/rejected at network level                  │
│   • ACCEPT doesn't mean application-level success                              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Creating CloudWatch Alarms

```bash
# Create metric filter for rejected traffic
aws logs put-metric-filter \
    --log-group-name "/aws/vpc/flow-logs" \
    --filter-name "RejectedTraffic" \
    --filter-pattern "[version, account, eni, source, dest, srcport, destport, proto, packets, bytes, windowstart, windowend, action=\"REJECT\", flowlogstatus]" \
    --metric-transformations \
        metricName=RejectedPacketCount,metricNamespace=VPCFlowLogs,metricValue=1

# Create alarm for high rejected traffic
aws cloudwatch put-metric-alarm \
    --alarm-name "HighRejectedTraffic" \
    --alarm-description "Alert when rejected traffic exceeds threshold" \
    --metric-name RejectedPacketCount \
    --namespace VPCFlowLogs \
    --statistic Sum \
    --period 300 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:security-alerts
```

## Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FLOW LOG BEST PRACTICES                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   1. COVERAGE                                                                   │
│      • Enable flow logs at VPC level for complete visibility                   │
│      • Use ENI-level logs for specific troubleshooting                         │
│      • Log ALL traffic types (ACCEPT, REJECT)                                  │
│                                                                                  │
│   2. STORAGE                                                                    │
│      • Use S3 for long-term storage (cheaper)                                  │
│      • Use CloudWatch Logs for real-time analysis                              │
│      • Consider Parquet format for Athena queries                              │
│      • Implement lifecycle policies (e.g., move to Glacier after 90 days)      │
│                                                                                  │
│   3. PERFORMANCE                                                                │
│      • Set appropriate aggregation interval (60s for detailed, 600s for cost)  │
│      • Use custom log format to capture only needed fields                     │
│      • Partition logs for efficient querying                                   │
│                                                                                  │
│   4. SECURITY MONITORING                                                        │
│      • Create alarms for unusual traffic patterns                              │
│      • Monitor for port scanning (many ports from one source)                  │
│      • Alert on rejected SSH/RDP attempts                                      │
│      • Watch for data exfiltration (unusual outbound traffic)                  │
│                                                                                  │
│   5. COST MANAGEMENT                                                            │
│      • Flow logs incur data ingestion costs                                    │
│      • Consider sampling in high-traffic environments                          │
│      • Set log retention policies                                              │
│      • Monitor CloudWatch and S3 costs                                         │
│                                                                                  │
│   6. COMPLIANCE                                                                 │
│      • Enable for compliance requirements (PCI-DSS, HIPAA)                     │
│      • Retain logs per regulatory requirements                                 │
│      • Enable encryption for S3 logs                                           │
│      • Use cross-account logging for centralization                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Pricing

| Component | Cost |
|-----------|------|
| Data ingestion to CloudWatch | $0.50 per GB |
| Data storage in CloudWatch | $0.03 per GB/month |
| Data ingestion to S3 | $0.00 (free) |
| S3 storage | Standard S3 pricing |
| CloudWatch Logs Insights queries | $0.005 per GB scanned |
| Athena queries | $5.00 per TB scanned |

## Key Takeaways

1. **Flow Logs** capture IP traffic metadata (not packet contents)
2. Available at **VPC**, **Subnet**, or **ENI** level
3. Publish to **CloudWatch Logs** or **S3**
4. **Not real-time** - aggregation interval of 60s to 600s
5. Essential for **security monitoring** and **troubleshooting**
6. Use **CloudWatch Logs Insights** for real-time analysis
7. Use **Athena** for historical analysis of S3 logs
8. Remember: **ACCEPT** means network allowed, not application success

---

**Next:** [10-hybrid-connectivity.md](10-hybrid-connectivity.md) - Learn about connecting on-premises networks to AWS
