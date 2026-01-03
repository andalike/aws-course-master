# Creating Lambda Functions

## Introduction

There are multiple ways to create and deploy Lambda functions. This section covers three primary approaches: the AWS Console, AWS CLI, and AWS SAM (Serverless Application Model). Each method has its use cases, from quick prototypes to production-grade deployments.

## Deployment Methods Overview

```
┌─────────────────────────────────────────────────────────────────┐
│               LAMBDA DEPLOYMENT OPTIONS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐    │
│  │   CONSOLE   │   │    CLI      │   │        SAM          │    │
│  │             │   │             │   │                     │    │
│  │ • Quick     │   │ • Scripts   │   │ • IaC deployments   │    │
│  │   testing   │   │ • Automation│   │ • CI/CD pipelines   │    │
│  │ • Learning  │   │ • CI/CD     │   │ • Complex apps      │    │
│  │ • Prototypes│   │ • Updates   │   │ • Multi-resource    │    │
│  └─────────────┘   └─────────────┘   └─────────────────────┘    │
│                                                                  │
│  Other Options:                                                  │
│  • CloudFormation  • CDK  • Terraform  • Serverless Framework   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Supported Runtimes

Lambda supports multiple programming languages through runtimes.

### Native Runtimes

| Runtime | Identifier | Status |
|---------|------------|--------|
| Python 3.12 | python3.12 | Current |
| Python 3.11 | python3.11 | Current |
| Python 3.10 | python3.10 | Current |
| Python 3.9 | python3.9 | Current |
| Node.js 20.x | nodejs20.x | Current |
| Node.js 18.x | nodejs18.x | Current |
| Java 21 | java21 | Current |
| Java 17 | java17 | Current |
| Java 11 | java11 | Current |
| .NET 8 | dotnet8 | Current |
| .NET 6 | dotnet6 | Current |
| Ruby 3.3 | ruby3.3 | Current |
| Go | provided.al2023 | Custom Runtime |
| Rust | provided.al2023 | Custom Runtime |

### Container Images

Lambda also supports container images up to 10 GB, allowing you to package your function and dependencies in a Docker container.

## Handler Format

The handler is the method in your code that processes events.

### Python Handler

```python
# File: lambda_function.py

def handler(event, context):
    """
    Lambda handler function

    Args:
        event (dict): Event data from trigger
        context (LambdaContext): Runtime information

    Returns:
        dict: Response object
    """
    name = event.get('name', 'World')

    return {
        'statusCode': 200,
        'body': f'Hello, {name}!'
    }
```

**Handler format**: `filename.function_name`
- File: `lambda_function.py`
- Function: `handler`
- Handler setting: `lambda_function.handler`

### Node.js Handler

```javascript
// File: index.js

// CommonJS format
exports.handler = async (event, context) => {
    const name = event.name || 'World';

    return {
        statusCode: 200,
        body: `Hello, ${name}!`
    };
};
```

```javascript
// File: index.mjs

// ES Module format
export const handler = async (event, context) => {
    const name = event.name || 'World';

    return {
        statusCode: 200,
        body: `Hello, ${name}!`
    };
};
```

**Handler format**: `filename.function_name`
- File: `index.js`
- Function: `handler`
- Handler setting: `index.handler`

### Java Handler

```java
// File: Handler.java

package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import java.util.Map;

public class Handler implements RequestHandler<Map<String, String>, String> {

    @Override
    public String handleRequest(Map<String, String> event, Context context) {
        String name = event.getOrDefault("name", "World");
        return "Hello, " + name + "!";
    }
}
```

**Handler format**: `package.Class::method`
- Handler setting: `example.Handler::handleRequest`

### Go Handler

```go
// File: main.go

package main

import (
    "context"
    "fmt"
    "github.com/aws/aws-lambda-go/lambda"
)

type Event struct {
    Name string `json:"name"`
}

type Response struct {
    StatusCode int    `json:"statusCode"`
    Body       string `json:"body"`
}

func handler(ctx context.Context, event Event) (Response, error) {
    name := event.Name
    if name == "" {
        name = "World"
    }

    return Response{
        StatusCode: 200,
        Body:       fmt.Sprintf("Hello, %s!", name),
    }, nil
}

func main() {
    lambda.Start(handler)
}
```

## Method 1: AWS Console

### Step-by-Step: Create Function via Console

#### Step 1: Navigate to Lambda

1. Sign in to AWS Console
2. Search for "Lambda" in the services menu
3. Click "Create function"

#### Step 2: Choose Creation Method

```
┌─────────────────────────────────────────────────────────────────┐
│                    CREATE FUNCTION                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ○ Author from scratch      ← Start with blank function         │
│  ○ Use a blueprint          ← Pre-built templates               │
│  ○ Container image          ← Docker container                  │
│  ○ Browse serverless app    ← AWS Serverless App Repository     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Step 3: Configure Basic Settings

```
Function name:  my-hello-function
Runtime:        Python 3.12
Architecture:   x86_64 / arm64

Permissions:
  ○ Create a new role with basic Lambda permissions
  ○ Use an existing role
  ○ Create a new role from AWS policy templates
```

#### Step 4: Write Code

In the inline code editor:

```python
import json

def lambda_handler(event, context):
    # Parse incoming request
    body = event.get('body')
    if body:
        body = json.loads(body)
        name = body.get('name', 'World')
    else:
        name = event.get('name', 'World')

    # Create response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': f'Hello, {name}!',
            'input': event
        })
    }

    return response
```

#### Step 5: Configure Test Event

```json
{
  "name": "AWS Lambda"
}
```

#### Step 6: Test the Function

Click "Test" to execute the function and view results.

## Method 2: AWS CLI

### Prerequisites

```bash
# Verify AWS CLI is installed
aws --version

# Configure credentials
aws configure

# Verify Lambda access
aws lambda list-functions
```

### Create Execution Role

First, create an IAM role for the Lambda function.

#### Step 1: Create Trust Policy

```bash
# Create trust-policy.json
cat > trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
```

#### Step 2: Create Role

```bash
# Create the execution role
aws iam create-role \
    --role-name lambda-execution-role \
    --assume-role-policy-document file://trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name lambda-execution-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Create Function with CLI

#### Step 1: Create Function Code

```bash
# Create Python function
cat > lambda_function.py << 'EOF'
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    name = event.get('name', 'World')

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': f'Hello, {name}!',
            'requestId': context.aws_request_id
        })
    }
EOF
```

#### Step 2: Create Deployment Package

```bash
# Create ZIP file
zip function.zip lambda_function.py
```

#### Step 3: Create Lambda Function

```bash
# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create function
aws lambda create-function \
    --function-name my-cli-function \
    --runtime python3.12 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/lambda-execution-role \
    --handler lambda_function.handler \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --memory-size 256
```

#### Step 4: Invoke Function

```bash
# Invoke synchronously
aws lambda invoke \
    --function-name my-cli-function \
    --payload '{"name": "CLI User"}' \
    --cli-binary-format raw-in-base64-out \
    response.json

# View response
cat response.json
```

### Update Function Code

```bash
# Make changes to lambda_function.py
# Then update the deployment package
zip function.zip lambda_function.py

# Update the function
aws lambda update-function-code \
    --function-name my-cli-function \
    --zip-file fileb://function.zip
```

### Update Function Configuration

```bash
# Update memory and timeout
aws lambda update-function-configuration \
    --function-name my-cli-function \
    --memory-size 512 \
    --timeout 60

# Add environment variables
aws lambda update-function-configuration \
    --function-name my-cli-function \
    --environment "Variables={LOG_LEVEL=DEBUG,TABLE_NAME=my-table}"
```

## Method 3: AWS SAM

AWS SAM (Serverless Application Model) is an open-source framework for building serverless applications.

### Install SAM CLI

```bash
# macOS (using Homebrew)
brew install aws-sam-cli

# Verify installation
sam --version
```

### SAM Project Structure

```
my-sam-app/
├── template.yaml          # SAM template
├── samconfig.toml         # SAM configuration
├── src/
│   ├── handlers/
│   │   ├── hello.py
│   │   └── goodbye.py
│   └── requirements.txt
├── tests/
│   └── test_handler.py
└── events/
    └── event.json
```

### Create SAM Project

```bash
# Initialize new project
sam init

# Choose options:
# 1. AWS Quick Start Templates
# 2. Hello World Example
# 3. Python 3.12
# 4. Zip package type
```

### SAM Template (template.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: My SAM Application

# Global settings for all functions
Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: python3.12
    Architectures:
      - x86_64
    Environment:
      Variables:
        LOG_LEVEL: INFO

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  # Lambda Function
  HelloFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub hello-function-${Environment}
      Description: Hello World function
      CodeUri: src/
      Handler: handlers/hello.handler
      Environment:
        Variables:
          ENVIRONMENT: !Ref Environment
      Events:
        HelloApi:
          Type: Api
          Properties:
            Path: /hello
            Method: get
        HelloApiPost:
          Type: Api
          Properties:
            Path: /hello
            Method: post
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref UsersTable

  # DynamoDB Table
  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub users-${Environment}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: userId
          AttributeType: S
      KeySchema:
        - AttributeName: userId
          KeyType: HASH

Outputs:
  HelloApi:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/hello/"

  HelloFunction:
    Description: Hello Function ARN
    Value: !GetAtt HelloFunction.Arn
```

### SAM Function Code

```python
# src/handlers/hello.py

import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize outside handler for connection reuse
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'users')
table = dynamodb.Table(table_name) if table_name else None


def handler(event, context):
    """
    Hello World Lambda handler

    Parameters
    ----------
    event: dict
        API Gateway Lambda Proxy Input Format
    context: object
        Lambda Context runtime methods and attributes

    Returns
    -------
    dict
        API Gateway Lambda Proxy Output Format
    """
    logger.info(f"Event: {json.dumps(event)}")

    # Handle different HTTP methods
    http_method = event.get('httpMethod', 'GET')

    if http_method == 'GET':
        return handle_get(event)
    elif http_method == 'POST':
        return handle_post(event)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }


def handle_get(event):
    """Handle GET requests"""
    query_params = event.get('queryStringParameters') or {}
    name = query_params.get('name', 'World')

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': f'Hello, {name}!',
            'environment': os.environ.get('ENVIRONMENT', 'unknown')
        })
    }


def handle_post(event):
    """Handle POST requests"""
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }

    name = body.get('name', 'World')

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': f'Hello, {name}!',
            'received': body
        })
    }
```

### SAM Commands

```bash
# Validate template
sam validate

# Build the application
sam build

# Local testing
sam local invoke HelloFunction --event events/event.json

# Local API testing
sam local start-api

# Deploy with guided prompts (first time)
sam deploy --guided

# Deploy subsequent times
sam deploy

# View logs
sam logs --name HelloFunction --tail

# Delete the stack
sam delete
```

### SAM Configuration (samconfig.toml)

```toml
version = 0.1

[default]
[default.global.parameters]
stack_name = "my-sam-app"
region = "us-east-1"

[default.build.parameters]
cached = true
parallel = true

[default.deploy.parameters]
capabilities = "CAPABILITY_IAM"
confirm_changeset = true
resolve_s3 = true

[default.local_invoke.parameters]
env_vars = "env.json"

[dev]
[dev.deploy.parameters]
stack_name = "my-sam-app-dev"
parameter_overrides = "Environment=dev"

[prod]
[prod.deploy.parameters]
stack_name = "my-sam-app-prod"
parameter_overrides = "Environment=prod"
confirm_changeset = true
```

## Deployment Packages

### Simple Package (No Dependencies)

```bash
# Single file
zip function.zip lambda_function.py

# Multiple files
zip -r function.zip lambda_function.py utils.py config.py
```

### Package with Dependencies (Python)

```bash
# Create project structure
mkdir my-function
cd my-function

# Create requirements.txt
cat > requirements.txt << 'EOF'
requests==2.31.0
boto3==1.34.0
EOF

# Create function
cat > lambda_function.py << 'EOF'
import requests
import boto3

def handler(event, context):
    return {"statusCode": 200}
EOF

# Install dependencies to package directory
pip install -r requirements.txt -t package/

# Create deployment package
cd package
zip -r ../deployment.zip .
cd ..
zip deployment.zip lambda_function.py
```

### Package with Dependencies (Node.js)

```bash
# Create project
mkdir my-function
cd my-function
npm init -y

# Install dependencies
npm install axios uuid

# Create handler
cat > index.js << 'EOF'
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

exports.handler = async (event) => {
    const id = uuidv4();
    return { statusCode: 200, body: JSON.stringify({ id }) };
};
EOF

# Create deployment package
zip -r function.zip index.js node_modules/
```

### Using Container Images

```dockerfile
# Dockerfile
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the handler
CMD [ "lambda_function.handler" ]
```

```bash
# Build image
docker build -t my-lambda-image .

# Tag for ECR
docker tag my-lambda-image:latest \
    123456789012.dkr.ecr.us-east-1.amazonaws.com/my-lambda-image:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-lambda-image:latest

# Create function from container
aws lambda create-function \
    --function-name my-container-function \
    --package-type Image \
    --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/my-lambda-image:latest \
    --role arn:aws:iam::123456789012:role/lambda-execution-role
```

## Versioning and Aliases

### Publishing Versions

```bash
# Publish a version
aws lambda publish-version \
    --function-name my-function \
    --description "Version 1.0"

# List versions
aws lambda list-versions-by-function \
    --function-name my-function
```

### Creating Aliases

```bash
# Create alias pointing to version
aws lambda create-alias \
    --function-name my-function \
    --name prod \
    --function-version 1

# Create alias for latest
aws lambda create-alias \
    --function-name my-function \
    --name dev \
    --function-version '$LATEST'

# Update alias to new version
aws lambda update-alias \
    --function-name my-function \
    --name prod \
    --function-version 2
```

### Traffic Shifting with Aliases

```bash
# Split traffic between versions
aws lambda update-alias \
    --function-name my-function \
    --name prod \
    --function-version 2 \
    --routing-config AdditionalVersionWeights={"1"=0.3}

# 70% traffic to version 2, 30% to version 1
```

## Comparison: Console vs CLI vs SAM

| Aspect | Console | CLI | SAM |
|--------|---------|-----|-----|
| **Best For** | Learning, quick tests | Automation, scripting | Production deployments |
| **IaC Support** | No | Partial | Yes |
| **Local Testing** | No | Limited | Yes |
| **CI/CD Integration** | Manual | Good | Excellent |
| **Multi-Resource** | Manual | Scripted | Template-based |
| **Version Control** | No | Possible | Yes |
| **Reproducibility** | Low | Medium | High |

## Summary

### Key Takeaways

1. **Multiple deployment options**: Console for learning, CLI for automation, SAM for production
2. **Handler format varies by runtime**: Understand your language's handler convention
3. **Deployment packages**: Zip files for simple cases, containers for complex dependencies
4. **SAM simplifies serverless**: Templates, local testing, and integrated deployment

### Next Steps

Continue to [03-lambda-triggers.md](./03-lambda-triggers.md) to learn about the various event sources that can trigger Lambda functions.
