# CloudFormation Templates

This directory contains CloudFormation templates demonstrating various AWS architecture patterns.

## Templates Overview

| Template | Description | Key Services |
|----------|-------------|--------------|
| `vpc-basic.yaml` | VPC with public/private subnets | VPC, Subnets, NAT Gateway |
| `ec2-webserver.yaml` | Auto-scaling web servers | EC2, ALB, Auto Scaling |
| `s3-static-website.yaml` | Static website hosting | S3, CloudFront |
| `serverless-api.yaml` | Serverless REST API | Lambda, API Gateway, DynamoDB |

## Quick Start

### Deploy VPC

```bash
aws cloudformation create-stack \
    --stack-name my-vpc \
    --template-body file://vpc-basic.yaml \
    --parameters ParameterKey=EnvironmentName,ParameterValue=dev

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name my-vpc
```

### Deploy EC2 Web Server

```bash
# First, create a key pair
aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
chmod 400 my-key.pem

# Get VPC and subnet info
VPC_ID=$(aws cloudformation describe-stacks --stack-name my-vpc \
    --query 'Stacks[0].Outputs[?OutputKey==`VpcId`].OutputValue' --output text)

SUBNET_IDS=$(aws cloudformation describe-stacks --stack-name my-vpc \
    --query 'Stacks[0].Outputs[?OutputKey==`PublicSubnetIds`].OutputValue' --output text)

# Deploy web server stack
aws cloudformation create-stack \
    --stack-name my-webserver \
    --template-body file://ec2-webserver.yaml \
    --parameters \
        ParameterKey=VpcId,ParameterValue=$VPC_ID \
        ParameterKey=PublicSubnetIds,ParameterValue=\"$SUBNET_IDS\" \
        ParameterKey=KeyName,ParameterValue=my-key \
    --capabilities CAPABILITY_IAM
```

### Deploy S3 Static Website

```bash
# Generate unique bucket name
BUCKET_NAME="my-website-$(date +%s)"

aws cloudformation create-stack \
    --stack-name my-website \
    --template-body file://s3-static-website.yaml \
    --parameters ParameterKey=BucketName,ParameterValue=$BUCKET_NAME

# Wait and get outputs
aws cloudformation wait stack-create-complete --stack-name my-website

# Upload website content
aws s3 sync ./my-website-files s3://$BUCKET_NAME
```

### Deploy Serverless API (SAM)

```bash
# Using SAM CLI
sam build --template serverless-api.yaml
sam deploy --guided

# Or using CloudFormation (requires packaging first)
aws cloudformation package \
    --template-file serverless-api.yaml \
    --s3-bucket my-deployment-bucket \
    --output-template-file packaged.yaml

aws cloudformation deploy \
    --template-file packaged.yaml \
    --stack-name my-serverless-api \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
```

## Template Details

### vpc-basic.yaml

Creates a production-ready VPC architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                          VPC (10.0.0.0/16)                  │
├─────────────────────────────┬───────────────────────────────┤
│       Availability Zone A    │       Availability Zone B     │
├─────────────────────────────┼───────────────────────────────┤
│  Public Subnet (10.0.1.0/24) │  Public Subnet (10.0.2.0/24)  │
│  - Internet Gateway Route    │  - Internet Gateway Route     │
├─────────────────────────────┼───────────────────────────────┤
│ Private Subnet (10.0.10.0/24)│ Private Subnet (10.0.20.0/24) │
│  - NAT Gateway Route         │  - NAT Gateway Route          │
└─────────────────────────────┴───────────────────────────────┘
```

**Parameters:**
- `EnvironmentName`: Environment prefix (dev/staging/prod)
- `VpcCIDR`: VPC CIDR block
- `EnableNATGateway`: Enable/disable NAT Gateway

### ec2-webserver.yaml

Deploys a highly available web application:

```
                    ┌─────────────────┐
                    │  Internet       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Application    │
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
    ┌───────▼───────┐                 ┌───────▼───────┐
    │   EC2 (AZ-A)  │                 │   EC2 (AZ-B)  │
    │   Auto Scaling│                 │   Auto Scaling│
    └───────────────┘                 └───────────────┘
```

**Features:**
- Application Load Balancer
- Auto Scaling Group (1-10 instances)
- Launch Template with user data
- Target tracking scaling policy
- Security groups configured

### s3-static-website.yaml

Creates a secure static website with CDN:

```
    ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
    │   User      │────▶│  CloudFront  │────▶│  S3 Bucket  │
    └─────────────┘     │  (CDN)       │     │  (Origin)   │
                        └──────────────┘     └─────────────┘
```

**Features:**
- S3 bucket with versioning
- CloudFront distribution with HTTPS
- Origin Access Control (OAC)
- Caching and compression
- Custom error pages

### serverless-api.yaml (SAM)

Complete serverless CRUD API:

```
    ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
    │   Client    │────▶│  API Gateway │────▶│   Lambda    │
    └─────────────┘     └──────────────┘     │  Functions  │
                                              └──────┬──────┘
                                                     │
                                              ┌──────▼──────┐
                                              │  DynamoDB   │
                                              │   Table     │
                                              └─────────────┘
```

**API Endpoints:**
- `POST /items` - Create item
- `GET /items` - List items
- `GET /items/{id}` - Get item
- `DELETE /items/{id}` - Delete item

## Best Practices Demonstrated

### 1. Security
- Private subnets for sensitive resources
- Security groups with minimal permissions
- S3 bucket policies with OAC
- Encryption at rest (S3, DynamoDB)

### 2. High Availability
- Multi-AZ deployments
- Auto Scaling with health checks
- Load balancer health monitoring

### 3. Cost Optimization
- Conditional resource creation
- Pay-per-request DynamoDB
- Appropriate instance types

### 4. Operational Excellence
- CloudWatch alarms
- X-Ray tracing
- Structured logging
- Resource tagging

## Cleanup

Delete stacks in reverse order:

```bash
# Delete application stacks first
aws cloudformation delete-stack --stack-name my-serverless-api
aws cloudformation delete-stack --stack-name my-website
aws cloudformation delete-stack --stack-name my-webserver

# Wait for deletions
aws cloudformation wait stack-delete-complete --stack-name my-serverless-api
aws cloudformation wait stack-delete-complete --stack-name my-website
aws cloudformation wait stack-delete-complete --stack-name my-webserver

# Delete VPC last (no dependencies)
aws cloudformation delete-stack --stack-name my-vpc
```

## Troubleshooting

### Common Issues

**Stack creation failed:**
```bash
# Check events for error details
aws cloudformation describe-stack-events --stack-name my-stack \
    --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

**Nested stack issues:**
```bash
# List all nested stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE \
    --query 'StackSummaries[?ParentId!=`null`]'
```

**Cannot delete stack:**
```bash
# Check for dependencies
aws cloudformation describe-stack-resources --stack-name my-stack

# Force delete with retained resources (use carefully)
aws cloudformation delete-stack --stack-name my-stack --retain-resources ResourceId
```

## Additional Resources

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [CloudFormation Template Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)
