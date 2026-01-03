# Lambda Configuration

## Introduction

Proper configuration of Lambda functions is crucial for performance, cost optimization, and security. This section covers memory settings, timeout configuration, environment variables, Lambda layers, and VPC connectivity.

## Configuration Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 LAMBDA CONFIGURATION OPTIONS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   COMPUTE       │  │  ENVIRONMENT    │  │   NETWORKING    │  │
│  │                 │  │                 │  │                 │  │
│  │  • Memory       │  │  • Variables    │  │  • VPC          │  │
│  │  • Timeout      │  │  • Secrets      │  │  • Subnets      │  │
│  │  • Architecture │  │  • Encryption   │  │  • Security     │  │
│  │  • Ephemeral    │  │                 │  │    Groups       │  │
│  │    Storage      │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   CODE          │  │  MONITORING     │  │   CONCURRENCY   │  │
│  │                 │  │                 │  │                 │  │
│  │  • Layers       │  │  • CloudWatch   │  │  • Reserved     │  │
│  │  • Handler      │  │  • X-Ray        │  │  • Provisioned  │  │
│  │  • Runtime      │  │  • Tracing      │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Memory Configuration

### Memory and CPU Relationship

Lambda allocates CPU power proportionally to memory. More memory = more CPU = faster execution.

```
┌─────────────────────────────────────────────────────────────────┐
│              MEMORY TO CPU RELATIONSHIP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Memory    │  vCPUs  │  Best For                                │
│  ──────────┼─────────┼──────────────────────────────────────    │
│  128 MB    │  ~0.08  │  Simple operations, basic webhooks       │
│  256 MB    │  ~0.15  │  API handlers, small data processing     │
│  512 MB    │  ~0.30  │  Medium complexity, SDK operations       │
│  1024 MB   │  ~0.60  │  Data processing, image manipulation     │
│  1769 MB   │  1.00   │  Full vCPU, compute-intensive           │
│  3538 MB   │  2.00   │  Multi-threaded, large processing       │
│  10240 MB  │  6.00   │  Heavy computation, ML inference        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Memory Limits

| Setting | Value |
|---------|-------|
| Minimum | 128 MB |
| Maximum | 10,240 MB |
| Increment | 1 MB |
| Default | 128 MB |

### Configuring Memory

```bash
# Set memory via CLI
aws lambda update-function-configuration \
    --function-name my-function \
    --memory-size 1024
```

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    MemorySize: 1024
```

### Memory Optimization Strategy

```python
import time
import boto3
import json

def handler(event, context):
    """Function to test memory/performance relationship"""
    start = time.time()

    # Perform computation
    result = compute_intensive_task()

    duration = (time.time() - start) * 1000

    return {
        'statusCode': 200,
        'body': json.dumps({
            'duration_ms': duration,
            'memory_allocated': context.memory_limit_in_mb,
            'memory_used': get_memory_used()
        })
    }

def compute_intensive_task():
    """Simulate CPU-intensive work"""
    result = 0
    for i in range(1000000):
        result += i * i
    return result

def get_memory_used():
    """Get actual memory usage"""
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # MB
```

### Power Tuning

Use AWS Lambda Power Tuning to find optimal memory:

```bash
# Deploy power tuning tool
sam deploy \
    --template-file https://raw.githubusercontent.com/alexcasalboni/aws-lambda-power-tuning/master/template.yml \
    --stack-name lambda-power-tuning \
    --capabilities CAPABILITY_IAM

# Run tuning
aws stepfunctions start-execution \
    --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:powerTuningStateMachine \
    --input '{
        "lambdaARN": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
        "powerValues": [128, 256, 512, 1024, 1536, 2048, 3008],
        "num": 10,
        "payload": "{}"
    }'
```

## Timeout Configuration

### Timeout Limits

| Setting | Value |
|---------|-------|
| Minimum | 1 second |
| Maximum | 15 minutes (900 seconds) |
| Default | 3 seconds |

### Configuring Timeout

```bash
# Set timeout via CLI
aws lambda update-function-configuration \
    --function-name my-function \
    --timeout 60
```

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Timeout: 60
```

### Handling Timeouts

```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Handle timeout gracefully"""

    # Check remaining time
    remaining_time = context.get_remaining_time_in_millis()
    logger.info(f"Time remaining: {remaining_time}ms")

    # Process items with timeout awareness
    items = event.get('items', [])
    processed = []

    for item in items:
        # Check if enough time remains
        if context.get_remaining_time_in_millis() < 5000:  # 5 seconds buffer
            logger.warning("Running low on time, stopping processing")
            break

        result = process_item(item)
        processed.append(result)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': len(processed),
            'total': len(items),
            'completed': len(processed) == len(items)
        })
    }


def process_item(item):
    """Process single item"""
    # Simulate work
    import time
    time.sleep(0.5)
    return {'id': item['id'], 'status': 'processed'}
```

### Timeout Recommendations

| Use Case | Recommended Timeout |
|----------|-------------------|
| API Handlers | 3-10 seconds |
| S3 Processing | 30-60 seconds |
| ETL Jobs | 5-15 minutes |
| Warm-up Events | 5-10 seconds |
| SQS Processing | Match visibility timeout |

## Environment Variables

### Use Cases

- Configuration values
- Feature flags
- Connection strings
- API endpoints
- Non-sensitive settings

### Configuring Environment Variables

```bash
# Set environment variables via CLI
aws lambda update-function-configuration \
    --function-name my-function \
    --environment "Variables={
        LOG_LEVEL=INFO,
        TABLE_NAME=users,
        API_ENDPOINT=https://api.example.com,
        FEATURE_FLAG_NEW_UI=true
    }"
```

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Environment:
      Variables:
        LOG_LEVEL: INFO
        TABLE_NAME: !Ref UsersTable
        API_ENDPOINT: !Sub "https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com"
```

### Accessing Environment Variables

```python
import os
import logging

# Set up logging based on environment
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger = logging.getLogger()
logger.setLevel(getattr(logging, log_level))

# Get configuration
TABLE_NAME = os.environ['TABLE_NAME']
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'https://default.api.com')
FEATURE_NEW_UI = os.environ.get('FEATURE_FLAG_NEW_UI', 'false').lower() == 'true'


def handler(event, context):
    logger.info(f"Using table: {TABLE_NAME}")

    if FEATURE_NEW_UI:
        return new_ui_handler(event)
    else:
        return legacy_handler(event)
```

```javascript
// Node.js
const LOG_LEVEL = process.env.LOG_LEVEL || 'INFO';
const TABLE_NAME = process.env.TABLE_NAME;
const API_ENDPOINT = process.env.API_ENDPOINT || 'https://default.api.com';

exports.handler = async (event) => {
    console.log(`Using table: ${TABLE_NAME}`);

    // Use configuration
    return { statusCode: 200 };
};
```

### Environment Variable Limits

| Limit | Value |
|-------|-------|
| Total size | 4 KB |
| Key format | Letters, numbers, underscores |
| Reserved prefixes | AWS_, _X_AMZN_, _HANDLER, etc. |

### Reserved Environment Variables

Lambda automatically sets these variables:

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | Current region |
| `AWS_EXECUTION_ENV` | Runtime identifier |
| `AWS_LAMBDA_FUNCTION_NAME` | Function name |
| `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` | Configured memory |
| `AWS_LAMBDA_FUNCTION_VERSION` | Function version |
| `AWS_LAMBDA_LOG_GROUP_NAME` | CloudWatch log group |
| `AWS_LAMBDA_LOG_STREAM_NAME` | CloudWatch log stream |
| `_HANDLER` | Handler location |

### Encrypting Environment Variables

```bash
# Create KMS key
aws kms create-key --description "Lambda environment encryption"

# Configure Lambda to use KMS key
aws lambda update-function-configuration \
    --function-name my-function \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abc-123

# Store encrypted value
aws lambda update-function-configuration \
    --function-name my-function \
    --environment "Variables={
        DATABASE_PASSWORD=encrypted-value
    }"
```

### Using Secrets Manager

For sensitive data, use Secrets Manager instead of environment variables:

```python
import json
import boto3
from botocore.exceptions import ClientError

# Cache secrets client
secrets_client = boto3.client('secretsmanager')
cached_secrets = {}


def get_secret(secret_name):
    """Get secret from Secrets Manager with caching"""
    if secret_name in cached_secrets:
        return cached_secrets[secret_name]

    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        cached_secrets[secret_name] = secret
        return secret
    except ClientError as e:
        raise e


def handler(event, context):
    # Get database credentials
    db_secret = get_secret('prod/database/credentials')

    # Use credentials
    connection = connect_to_database(
        host=db_secret['host'],
        username=db_secret['username'],
        password=db_secret['password']
    )

    return {'statusCode': 200}
```

## Lambda Layers

### What are Layers?

Layers are ZIP archives containing libraries, custom runtimes, or other dependencies that can be shared across functions.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAMBDA LAYERS                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    FUNCTION CODE                         │    │
│  │                    (Your business logic)                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              ▲                                   │
│                              │                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Layer 1   │  │   Layer 2   │  │   Layer 3   │              │
│  │  (boto3)    │  │  (requests) │  │  (shared)   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                              ▲                                   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    LAMBDA RUNTIME                        │    │
│  │                    (Python, Node.js, etc.)               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Benefits

- **Code reuse**: Share code across multiple functions
- **Smaller packages**: Reduce function deployment size
- **Separate updates**: Update dependencies independently
- **Team collaboration**: Central libraries managed by teams

### Creating a Python Layer

```bash
# Create layer directory structure
mkdir -p layer/python

# Install dependencies
pip install requests boto3 -t layer/python/

# Create layer ZIP
cd layer
zip -r ../my-layer.zip .
cd ..

# Publish layer
aws lambda publish-layer-version \
    --layer-name my-shared-libs \
    --description "Shared Python libraries" \
    --zip-file fileb://my-layer.zip \
    --compatible-runtimes python3.11 python3.12 \
    --compatible-architectures x86_64 arm64
```

### Creating a Node.js Layer

```bash
# Create layer directory structure
mkdir -p layer/nodejs

# Initialize and install dependencies
cd layer/nodejs
npm init -y
npm install axios uuid lodash
cd ../..

# Create layer ZIP
cd layer
zip -r ../nodejs-layer.zip .
cd ..

# Publish layer
aws lambda publish-layer-version \
    --layer-name nodejs-shared-libs \
    --description "Shared Node.js libraries" \
    --zip-file fileb://nodejs-layer.zip \
    --compatible-runtimes nodejs18.x nodejs20.x
```

### Attaching Layers to Functions

```bash
# Attach layer to function
aws lambda update-function-configuration \
    --function-name my-function \
    --layers \
        arn:aws:lambda:us-east-1:123456789012:layer:my-shared-libs:1 \
        arn:aws:lambda:us-east-1:123456789012:layer:utilities:2
```

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Layers:
      - !Ref SharedLibsLayer
      - arn:aws:lambda:us-east-1:123456789012:layer:utilities:2

SharedLibsLayer:
  Type: AWS::Serverless::LayerVersion
  Properties:
    LayerName: shared-libs
    Description: Shared Python libraries
    ContentUri: layers/shared-libs/
    CompatibleRuntimes:
      - python3.11
      - python3.12
    RetentionPolicy: Retain
```

### Layer Directory Structure

```
# Python Layer
layer.zip
└── python/
    ├── requests/
    ├── boto3/
    └── my_shared_module/
        ├── __init__.py
        └── utils.py

# Node.js Layer
layer.zip
└── nodejs/
    └── node_modules/
        ├── axios/
        ├── uuid/
        └── lodash/
```

### Using Layers in Code

```python
# Python - imports work normally
import requests
from my_shared_module import utils

def handler(event, context):
    response = requests.get('https://api.example.com')
    result = utils.process_data(response.json())
    return {'statusCode': 200, 'body': result}
```

```javascript
// Node.js - require from node_modules
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

exports.handler = async (event) => {
    const id = uuidv4();
    const response = await axios.get('https://api.example.com');
    return { statusCode: 200, body: JSON.stringify({ id }) };
};
```

### Layer Limits

| Limit | Value |
|-------|-------|
| Layers per function | 5 |
| Total unzipped size | 250 MB (function + all layers) |
| Layer package size | 50 MB (zipped) |
| Layer versions | Unlimited |

### AWS Managed Layers

AWS provides managed layers for common use cases:

```bash
# AWS SDK PowerTools for Python
arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:51

# AWS Parameters and Secrets Lambda Extension
arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11
```

## VPC Configuration

### When to Use VPC

| Scenario | VPC Required |
|----------|--------------|
| Access RDS/ElastiCache | Yes |
| Access EC2 instances | Yes |
| Access on-premises resources | Yes |
| Access DynamoDB/S3 | No (via endpoints) |
| Public API calls | No (need NAT) |

### VPC Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VPC                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │     Private Subnet A    │  │     Private Subnet B        │   │
│  │                         │  │                             │   │
│  │  ┌─────────┐           │  │  ┌─────────┐                │   │
│  │  │ Lambda  │           │  │  │   RDS   │                │   │
│  │  │   ENI   │───────────┼──┼─▶│         │                │   │
│  │  └─────────┘           │  │  └─────────┘                │   │
│  │       │                 │  │                             │   │
│  └───────┼─────────────────┘  └─────────────────────────────┘   │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │        NAT Gateway      │  │     VPC Endpoint (S3)       │   │
│  │  (For internet access)  │  │  (For S3/DynamoDB access)   │   │
│  └─────────────────────────┘  └─────────────────────────────┘   │
│          │                              │                        │
└──────────┼──────────────────────────────┼───────────────────────┘
           │                              │
           ▼                              ▼
    ┌──────────────┐              ┌──────────────┐
    │   Internet   │              │      S3      │
    └──────────────┘              └──────────────┘
```

### Configuring VPC Access

```bash
# Configure VPC
aws lambda update-function-configuration \
    --function-name my-function \
    --vpc-config "SubnetIds=subnet-abc123,subnet-def456,SecurityGroupIds=sg-xyz789"
```

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    VpcConfig:
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
```

### Security Group Configuration

```yaml
# Lambda Security Group
LambdaSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Security group for Lambda function
    VpcId: !Ref VPC
    SecurityGroupEgress:
      - IpProtocol: tcp
        FromPort: 5432
        ToPort: 5432
        DestinationSecurityGroupId: !Ref DatabaseSecurityGroup
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0  # For HTTPS outbound

# Database Security Group
DatabaseSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Security group for RDS
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 5432
        ToPort: 5432
        SourceSecurityGroupId: !Ref LambdaSecurityGroup
```

### VPC Endpoints for AWS Services

```yaml
# S3 VPC Endpoint (Gateway)
S3Endpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub com.amazonaws.${AWS::Region}.s3
    VpcId: !Ref VPC
    RouteTableIds:
      - !Ref PrivateRouteTable
    VpcEndpointType: Gateway

# DynamoDB VPC Endpoint (Gateway)
DynamoDBEndpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub com.amazonaws.${AWS::Region}.dynamodb
    VpcId: !Ref VPC
    RouteTableIds:
      - !Ref PrivateRouteTable
    VpcEndpointType: Gateway

# Secrets Manager VPC Endpoint (Interface)
SecretsManagerEndpoint:
  Type: AWS::EC2::VPCEndpoint
  Properties:
    ServiceName: !Sub com.amazonaws.${AWS::Region}.secretsmanager
    VpcId: !Ref VPC
    SubnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2
    SecurityGroupIds:
      - !Ref EndpointSecurityGroup
    VpcEndpointType: Interface
    PrivateDnsEnabled: true
```

### NAT Gateway for Internet Access

```yaml
# NAT Gateway
NATGateway:
  Type: AWS::EC2::NatGateway
  Properties:
    AllocationId: !GetAtt EIP.AllocationId
    SubnetId: !Ref PublicSubnet

EIP:
  Type: AWS::EC2::EIP
  Properties:
    Domain: vpc

# Private Route Table
PrivateRouteTable:
  Type: AWS::EC2::RouteTable
  Properties:
    VpcId: !Ref VPC

PrivateRoute:
  Type: AWS::EC2::Route
  Properties:
    RouteTableId: !Ref PrivateRouteTable
    DestinationCidrBlock: 0.0.0.0/0
    NatGatewayId: !Ref NATGateway
```

### VPC Cold Start Considerations

VPC-connected functions have additional cold start latency due to ENI (Elastic Network Interface) creation.

**Mitigation strategies:**
1. Use Provisioned Concurrency
2. Keep functions warm
3. Use VPC endpoints instead of NAT for AWS services
4. Use arm64 architecture (faster ENI attachment)

## Ephemeral Storage (/tmp)

### Storage Limits

| Setting | Value |
|---------|-------|
| Minimum | 512 MB |
| Maximum | 10,240 MB (10 GB) |
| Default | 512 MB |

### Configuring Storage

```bash
# Set ephemeral storage
aws lambda update-function-configuration \
    --function-name my-function \
    --ephemeral-storage Size=1024
```

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    EphemeralStorage:
      Size: 1024
```

### Using /tmp Storage

```python
import os
import json

def handler(event, context):
    # Write to /tmp
    temp_file = '/tmp/data.json'

    with open(temp_file, 'w') as f:
        json.dump(event, f)

    # Read from /tmp
    with open(temp_file, 'r') as f:
        data = json.load(f)

    # Check available space
    statvfs = os.statvfs('/tmp')
    available_mb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'available_storage_mb': available_mb,
            'data': data
        })
    }
```

**Important notes about /tmp:**
- Contents persist between invocations in the same execution environment
- Contents are NOT shared between concurrent executions
- Clean up files to avoid storage exhaustion

## Summary

### Configuration Checklist

- [ ] Memory sized appropriately for workload
- [ ] Timeout allows completion with buffer
- [ ] Environment variables for configuration
- [ ] Secrets in Secrets Manager (not env vars)
- [ ] Layers for shared dependencies
- [ ] VPC only when needed for private resources
- [ ] VPC endpoints to avoid NAT costs
- [ ] Ephemeral storage sized for temp files

### Configuration Best Practices

1. **Memory**: Start at 256MB and tune based on actual usage
2. **Timeout**: Set to 2x expected duration with max 15 min
3. **Environment**: Use for config, not secrets
4. **Layers**: Share common dependencies across functions
5. **VPC**: Only use when accessing VPC resources

### Next Steps

Continue to [05-lambda-permissions.md](./05-lambda-permissions.md) to learn about IAM roles, resource-based policies, and cross-account access patterns.
