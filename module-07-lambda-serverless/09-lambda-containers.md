# Lambda Container Images

## Introduction

AWS Lambda supports deploying functions as container images up to 10 GB in size. This allows you to use familiar container tools, workflows, and dependencies while benefiting from Lambda's serverless execution model.

## Why Container Images for Lambda?

```
┌─────────────────────────────────────────────────────────────────┐
│               LAMBDA DEPLOYMENT OPTIONS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│     ZIP Package                    Container Image               │
│  ┌─────────────────┐           ┌─────────────────┐              │
│  │                 │           │                 │              │
│  │  function.zip   │           │   image:latest  │              │
│  │  ┌───────────┐  │           │  ┌───────────┐  │              │
│  │  │ handler.py│  │           │  │ Dockerfile│  │              │
│  │  │  utils.py │  │           │  │ handler.py│  │              │
│  │  │requirements│  │           │  │ libraries │  │              │
│  │  └───────────┘  │           │  │ OS pkgs   │  │              │
│  │                 │           │  │ custom    │  │              │
│  │   Max: 250 MB   │           │  └───────────┘  │              │
│  │   (unzipped)    │           │   Max: 10 GB    │              │
│  │                 │           │                 │              │
│  └─────────────────┘           └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Benefits of Container Images

| Benefit | Description |
|---------|-------------|
| **Larger Package Size** | Up to 10 GB (vs 250 MB for zip) |
| **Familiar Tooling** | Use Docker, CI/CD pipelines |
| **Custom Dependencies** | Include any libraries, binaries, OS packages |
| **Consistent Testing** | Same container runs locally and in Lambda |
| **ML Frameworks** | Large ML libraries (TensorFlow, PyTorch) |
| **Custom Runtimes** | Build any runtime environment |
| **Existing Workflows** | Integrate with container registries |

### When to Use Container Images

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION GUIDE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Use ZIP Package when:          Use Container Image when:       │
│  ├─ Package < 250 MB            ├─ Package > 250 MB             │
│  ├─ Standard runtime            ├─ Custom runtime needed        │
│  ├─ Few dependencies            ├─ ML/AI frameworks             │
│  ├─ Quick deployments           ├─ System dependencies          │
│  └─ Simpler CI/CD               ├─ Existing Docker workflow     │
│                                 └─ Consistent dev/prod env      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Lambda Container Requirements

### Required Interface

Lambda container images must implement the Lambda Runtime API:

```
┌─────────────────────────────────────────────────────────────────┐
│                LAMBDA CONTAINER INTERFACE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Lambda Execution Environment                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │  ┌──────────────┐     ┌──────────────┐     ┌────────────┐  ││
│  │  │   Lambda     │────▶│  Runtime     │────▶│   Your     │  ││
│  │  │   Service    │◀────│  Interface   │◀────│   Code     │  ││
│  │  │              │     │  Client      │     │            │  ││
│  │  └──────────────┘     └──────────────┘     └────────────┘  ││
│  │                                                              ││
│  │  Runtime API Endpoints:                                      ││
│  │  • GET /runtime/invocation/next     (Get next event)        ││
│  │  • POST /runtime/invocation/{id}/response (Send response)   ││
│  │  • POST /runtime/invocation/{id}/error    (Report error)    ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Image Requirements

| Requirement | Details |
|-------------|---------|
| Registry | Amazon ECR (same region as function) |
| Image Size | Maximum 10 GB |
| OS | Linux-based container |
| Architecture | x86_64 or arm64 |
| Entry Point | Must implement Runtime API |
| Read-Only | Container runs read-only (except /tmp) |

## AWS Base Images

AWS provides optimized base images for common runtimes:

### Available Base Images

| Runtime | Image URI |
|---------|-----------|
| Python 3.12 | `public.ecr.aws/lambda/python:3.12` |
| Python 3.11 | `public.ecr.aws/lambda/python:3.11` |
| Node.js 20 | `public.ecr.aws/lambda/nodejs:20` |
| Node.js 18 | `public.ecr.aws/lambda/nodejs:18` |
| Java 21 | `public.ecr.aws/lambda/java:21` |
| Java 17 | `public.ecr.aws/lambda/java:17` |
| .NET 8 | `public.ecr.aws/lambda/dotnet:8` |
| Go | `public.ecr.aws/lambda/go:1` |
| Ruby 3.2 | `public.ecr.aws/lambda/ruby:3.2` |
| Custom | `public.ecr.aws/lambda/provided:al2023` |

## Creating Container Images

### Python Container Image

#### Basic Dockerfile

```dockerfile
# Dockerfile for Python Lambda
FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the handler
CMD ["app.handler"]
```

#### Python Handler Code

```python
# app.py
import json
import boto3

# Initialize outside handler (reused in warm starts)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')


def handler(event, context):
    """
    Lambda handler function

    Args:
        event: Event data
        context: Lambda context

    Returns:
        Response object
    """
    try:
        # Process event
        body = event.get('body')
        if body and isinstance(body, str):
            body = json.loads(body)

        # Your business logic here
        result = process_data(body)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_data(data):
    """Process the incoming data"""
    return {
        'message': 'Success',
        'processed': data
    }
```

#### Requirements File

```text
# requirements.txt
boto3>=1.26.0
requests>=2.28.0
pandas>=2.0.0
numpy>=1.24.0
```

### Node.js Container Image

#### Dockerfile

```dockerfile
# Dockerfile for Node.js Lambda
FROM public.ecr.aws/lambda/nodejs:20

# Copy package files
COPY package*.json ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN npm ci --omit=dev

# Copy function code
COPY *.js ${LAMBDA_TASK_ROOT}

# Set the handler
CMD ["index.handler"]
```

#### Node.js Handler

```javascript
// index.js
const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event, context) => {
    console.log('Event:', JSON.stringify(event, null, 2));

    try {
        // Parse body if string
        let body = event.body;
        if (typeof body === 'string') {
            body = JSON.parse(body);
        }

        // Process request
        const result = await processRequest(body);

        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(result)
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message })
        };
    }
};

async function processRequest(data) {
    // Your business logic
    return {
        message: 'Success',
        data: data
    };
}
```

### Multi-Stage Build (Optimized)

```dockerfile
# Multi-stage build for smaller image size
FROM public.ecr.aws/lambda/python:3.12 AS builder

# Install build dependencies
RUN yum install -y gcc python3-devel

# Install Python dependencies
COPY requirements.txt .
RUN pip install --target /asset requirements.txt

# Production stage
FROM public.ecr.aws/lambda/python:3.12

# Copy installed dependencies
COPY --from=builder /asset ${LAMBDA_TASK_ROOT}

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]
```

### Custom Runtime Image

For languages not natively supported, use a custom runtime:

```dockerfile
# Custom runtime with provided.al2023
FROM public.ecr.aws/lambda/provided:al2023

# Install your runtime (example: Rust)
RUN yum install -y gcc

# Copy your compiled binary
COPY bootstrap ${LAMBDA_RUNTIME_DIR}

# Make bootstrap executable
RUN chmod +x ${LAMBDA_RUNTIME_DIR}/bootstrap

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy function code
COPY function.sh ${LAMBDA_TASK_ROOT}

CMD ["function.handler"]
```

#### Custom Bootstrap Script

```bash
#!/bin/bash
# bootstrap - Custom runtime entry point
set -euo pipefail

# Handler format: file.method
HANDLER="${_HANDLER}"

# Processing loop
while true; do
    # Get next invocation
    HEADERS="$(mktemp)"
    EVENT_DATA=$(curl -sS -LD "$HEADERS" \
        "http://${AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/next")

    # Extract request ID
    REQUEST_ID=$(grep -Fi Lambda-Runtime-Aws-Request-Id "$HEADERS" | \
        tr -d '[:space:]' | cut -d: -f2)

    # Execute handler and capture response
    RESPONSE=$(./function.sh "$EVENT_DATA")

    # Send response
    curl -sS -X POST \
        "http://${AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/$REQUEST_ID/response" \
        -d "$RESPONSE"
done
```

## Building and Pushing Images

### Build Locally

```bash
# Build the image
docker build -t my-lambda-function:latest .

# Test locally (using Lambda Runtime Interface Emulator)
docker run -p 9000:8080 my-lambda-function:latest

# Invoke locally
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d '{"key": "value"}'
```

### Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
    --repository-name my-lambda-function \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

# Get repository URI
REPO_URI=$(aws ecr describe-repositories \
    --repository-names my-lambda-function \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "Repository URI: $REPO_URI"
```

### Push to ECR

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag image for ECR
docker tag my-lambda-function:latest $REPO_URI:latest
docker tag my-lambda-function:latest $REPO_URI:v1.0.0

# Push to ECR
docker push $REPO_URI:latest
docker push $REPO_URI:v1.0.0
```

### Complete Build Script

```bash
#!/bin/bash
# build-and-push.sh

set -e

# Configuration
FUNCTION_NAME="my-lambda-function"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${FUNCTION_NAME}"
VERSION=$(git describe --tags --always 2>/dev/null || echo "latest")

echo "Building ${FUNCTION_NAME}:${VERSION}"

# Build image
docker build --platform linux/amd64 -t ${FUNCTION_NAME}:${VERSION} .

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Create repository if it doesn't exist
aws ecr describe-repositories --repository-names ${FUNCTION_NAME} 2>/dev/null || \
    aws ecr create-repository --repository-name ${FUNCTION_NAME}

# Tag and push
docker tag ${FUNCTION_NAME}:${VERSION} ${REPO_URI}:${VERSION}
docker tag ${FUNCTION_NAME}:${VERSION} ${REPO_URI}:latest

docker push ${REPO_URI}:${VERSION}
docker push ${REPO_URI}:latest

echo "Pushed: ${REPO_URI}:${VERSION}"
echo "Pushed: ${REPO_URI}:latest"
```

## Deploying Container Functions

### Deploy with CLI

```bash
# Create function from container image
aws lambda create-function \
    --function-name my-container-function \
    --package-type Image \
    --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/my-function:latest \
    --role arn:aws:iam::123456789012:role/lambda-execution-role \
    --timeout 30 \
    --memory-size 512 \
    --architectures x86_64

# Update function code to new image
aws lambda update-function-code \
    --function-name my-container-function \
    --image-uri 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-function:v2.0.0
```

### Deploy with SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ContainerFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      ImageUri: !Sub ${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/my-function:latest
      MemorySize: 512
      Timeout: 30
      Architectures:
        - x86_64
      Environment:
        Variables:
          TABLE_NAME: !Ref DataTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref DataTable
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /process
            Method: POST
    Metadata:
      DockerTag: latest
      DockerContext: ./src
      Dockerfile: Dockerfile

  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: data-table
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH

Outputs:
  ApiEndpoint:
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/process"
```

### Build with SAM

```bash
# Build container image
sam build

# Deploy (includes image push)
sam deploy --guided

# Or deploy with specific image
sam deploy \
    --image-repository 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-function \
    --stack-name my-container-stack
```

### Deploy with CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'

Parameters:
  ImageUri:
    Type: String
    Description: ECR image URI

Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: container-function
      PackageType: Image
      Code:
        ImageUri: !Ref ImageUri
      Role: !GetAtt LambdaRole.Arn
      Timeout: 30
      MemorySize: 512
      Architectures:
        - x86_64

  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

## Local Testing

### Using Lambda Runtime Interface Emulator (RIE)

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL TESTING WITH RIE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐    HTTP POST    ┌─────────────────────────┐ │
│  │     curl      │───────────────▶│    Docker Container     │ │
│  │  (test client)│                 │  ┌─────────────────────┐│ │
│  └───────────────┘                 │  │        RIE          ││ │
│         │                          │  │   (Port 8080)       ││ │
│         │                          │  └─────────┬───────────┘│ │
│         │                          │            │             │ │
│         ▼                          │            ▼             │ │
│  localhost:9000                    │  ┌─────────────────────┐│ │
│  /2015-03-31/functions/            │  │   Your Handler      ││ │
│  function/invocations              │  │    (app.handler)    ││ │
│                                    │  └─────────────────────┘│ │
│                                    └─────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### AWS Base Images (Include RIE)

```bash
# Run container locally (RIE is included)
docker run -p 9000:8080 my-lambda-function:latest

# Invoke function
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d '{"httpMethod": "POST", "body": "{\"name\": \"test\"}"}'
```

### Custom Images (Add RIE)

```dockerfile
# Add RIE to custom image
FROM public.ecr.aws/lambda/provided:al2023

# Install RIE for local testing
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/local/bin/aws-lambda-rie
RUN chmod +x /usr/local/bin/aws-lambda-rie

# Copy your code
COPY bootstrap ${LAMBDA_RUNTIME_DIR}
COPY function.sh ${LAMBDA_TASK_ROOT}

# Entrypoint script to use RIE locally
COPY entry.sh /
RUN chmod +x /entry.sh

ENTRYPOINT ["/entry.sh"]
CMD ["function.handler"]
```

```bash
#!/bin/bash
# entry.sh
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    # Running locally - use RIE
    exec /usr/local/bin/aws-lambda-rie /var/runtime/bootstrap "$@"
else
    # Running in Lambda - use actual runtime
    exec /var/runtime/bootstrap "$@"
fi
```

### SAM Local Testing

```bash
# Test with SAM CLI
sam local invoke ContainerFunction \
    --event events/test-event.json

# Start local API
sam local start-api

# Invoke API
curl -XPOST http://localhost:3000/process \
    -H "Content-Type: application/json" \
    -d '{"name": "test"}'
```

## Comparison: ZIP vs Container

### Deployment Package Comparison

| Feature | ZIP Package | Container Image |
|---------|-------------|-----------------|
| **Maximum Size** | 250 MB (unzipped) | 10 GB |
| **Deployment** | S3 or direct upload | ECR push |
| **Build Tool** | zip, SAM | Docker |
| **Local Testing** | SAM CLI | Docker + RIE |
| **Cold Start** | Generally faster | May be slower for large images |
| **Custom Runtime** | Layers | Dockerfile |
| **Dependencies** | pip/npm install | Any package manager |
| **OS Packages** | Limited | Full control |

### Performance Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE COMPARISON                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Cold Start Latency:                                             │
│                                                                  │
│  ZIP (small):     ████░░░░░░  ~200ms                            │
│  ZIP (250MB):     ████████░░  ~800ms                            │
│  Container (1GB): █████████░  ~1s                               │
│  Container (5GB): ██████████  ~3-5s                             │
│                                                                  │
│  Note: Cold start varies by:                                     │
│  • Image size                                                    │
│  • Runtime (Java > Python)                                      │
│  • Memory allocation                                             │
│  • VPC configuration                                             │
│                                                                  │
│  Mitigation:                                                     │
│  • Use Provisioned Concurrency                                   │
│  • Optimize image size (multi-stage builds)                     │
│  • Increase memory allocation                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### When to Choose Each

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELECTION MATRIX                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Choose ZIP when:                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ✓ Package size < 250 MB                                     ││
│  │ ✓ Standard runtime (Python, Node.js, etc.)                  ││
│  │ ✓ No special OS dependencies                                ││
│  │ ✓ Fastest cold starts needed                                ││
│  │ ✓ Simpler deployment pipeline                               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Choose Container when:                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ✓ Package size > 250 MB                                     ││
│  │ ✓ ML frameworks (TensorFlow, PyTorch, etc.)                 ││
│  │ ✓ Custom/compiled dependencies                              ││
│  │ ✓ Existing Docker workflow                                  ││
│  │ ✓ Custom runtime needed                                     ││
│  │ ✓ Team expertise in containers                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Best Practices

### 1. Image Optimization

```dockerfile
# Use multi-stage builds
FROM public.ecr.aws/lambda/python:3.12 AS builder
COPY requirements.txt .
RUN pip install --target /packages -r requirements.txt

FROM public.ecr.aws/lambda/python:3.12
COPY --from=builder /packages ${LAMBDA_TASK_ROOT}
COPY app.py ${LAMBDA_TASK_ROOT}
CMD ["app.handler"]
```

### 2. Layer Caching

```dockerfile
# Order commands to maximize cache hits
FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies first (change rarely)
RUN yum install -y libpq-devel

# Copy and install Python deps (change sometimes)
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy code last (changes frequently)
COPY *.py ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]
```

### 3. Security Scanning

```bash
# Enable ECR scanning
aws ecr put-image-scanning-configuration \
    --repository-name my-function \
    --image-scanning-configuration scanOnPush=true

# Get scan results
aws ecr describe-image-scan-findings \
    --repository-name my-function \
    --image-id imageTag=latest
```

### 4. Image Tagging Strategy

```bash
# Use semantic versioning + git SHA
VERSION="1.0.0"
GIT_SHA=$(git rev-parse --short HEAD)

docker tag my-function:latest $REPO_URI:$VERSION
docker tag my-function:latest $REPO_URI:$VERSION-$GIT_SHA
docker tag my-function:latest $REPO_URI:latest

# Immutable production deployments
aws lambda update-function-code \
    --function-name my-function \
    --image-uri $REPO_URI:$VERSION-$GIT_SHA
```

### 5. Reduce Image Size

```dockerfile
# Before: 1.2 GB
FROM public.ecr.aws/lambda/python:3.12
RUN pip install pandas numpy scipy scikit-learn tensorflow

# After: 800 MB (using slim/minimal packages)
FROM public.ecr.aws/lambda/python:3.12
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    && rm -rf /root/.cache
```

## ML/AI Use Case Example

### TensorFlow Lambda Container

```dockerfile
# Dockerfile for ML inference
FROM public.ecr.aws/lambda/python:3.12

# Install TensorFlow
RUN pip install tensorflow==2.15.0 --target "${LAMBDA_TASK_ROOT}"

# Copy model and code
COPY model/ ${LAMBDA_TASK_ROOT}/model/
COPY inference.py ${LAMBDA_TASK_ROOT}

CMD ["inference.handler"]
```

```python
# inference.py
import json
import numpy as np
import tensorflow as tf

# Load model at cold start (reused in warm invocations)
model = tf.keras.models.load_model('model')


def handler(event, context):
    """ML inference handler"""
    try:
        # Parse input
        body = json.loads(event.get('body', '{}'))
        input_data = np.array(body['data'])

        # Reshape if needed
        input_data = input_data.reshape(1, -1)

        # Run inference
        predictions = model.predict(input_data)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'predictions': predictions.tolist()
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## Summary

### Key Takeaways

1. **10 GB limit**: Container images support much larger packages than ZIP
2. **ECR required**: Images must be stored in Amazon ECR
3. **AWS base images**: Use optimized base images for best performance
4. **Local testing**: Use RIE for local development and testing
5. **Cold starts**: Larger images may have longer cold starts

### Container vs ZIP Quick Reference

| Aspect | ZIP | Container |
|--------|-----|-----------|
| Size limit | 250 MB | 10 GB |
| Build tool | zip/SAM | Docker |
| Registry | S3 | ECR |
| Runtime customization | Limited | Full |
| Cold start | Faster | Slower for large |

### Next Steps

Continue to [10-sam-framework.md](./10-sam-framework.md) to learn about building and deploying serverless applications with AWS SAM.
