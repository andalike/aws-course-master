# AWS SAM (Serverless Application Model)

## Introduction

AWS SAM is an open-source framework for building serverless applications on AWS. It provides shorthand syntax to define Lambda functions, APIs, databases, and event source mappings using YAML or JSON templates.

## What is AWS SAM?

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS SAM OVERVIEW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    SAM TEMPLATE                              ││
│  │                   (template.yaml)                            ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │ • Simplified resource definitions                    │   ││
│  │  │ • Built-in best practices                           │   ││
│  │  │ • Local testing capabilities                        │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  └──────────────────────────┬──────────────────────────────────┘│
│                             │                                    │
│                             ▼  Transform                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                CloudFormation Template                       ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │ • Lambda Functions                                   │   ││
│  │  │ • API Gateway                                        │   ││
│  │  │ • IAM Roles/Policies                                │   ││
│  │  │ • DynamoDB Tables                                    │   ││
│  │  │ • Event Sources                                      │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Simplified Syntax** | Fewer lines than raw CloudFormation |
| **Local Testing** | Test functions and APIs locally |
| **Built-in Policies** | Predefined IAM policy templates |
| **Accelerated Sync** | Fast development iteration |
| **CI/CD Integration** | Works with CodePipeline, GitHub Actions |
| **Debugging** | Step-through debugging with IDEs |

## Installing SAM CLI

### macOS

```bash
# Using Homebrew
brew install aws-sam-cli

# Verify installation
sam --version
```

### Linux

```bash
# Download installer
curl -L https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip -o sam-cli.zip

# Unzip and install
unzip sam-cli.zip -d sam-installation
sudo ./sam-installation/install

# Verify
sam --version
```

### Windows

```powershell
# Using MSI installer (download from AWS)
# Or using Chocolatey
choco install aws-sam-cli

# Verify
sam --version
```

### Docker Requirement

```bash
# SAM CLI requires Docker for local testing
docker --version

# If not installed, install Docker Desktop or:
# Linux: sudo apt-get install docker.io
```

## SAM Template Structure

### Basic Template

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: My Serverless Application

# Global settings for all functions
Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256
    Environment:
      Variables:
        LOG_LEVEL: INFO

# Parameters (optional)
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

# Conditions (optional)
Conditions:
  IsProd: !Equals [!Ref Environment, prod]

# Resources (required)
Resources:
  # Lambda Function
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      CodeUri: src/
      Description: My Lambda function
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: GET

# Outputs (optional)
Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

### SAM Resource Types

| SAM Resource | Description |
|--------------|-------------|
| `AWS::Serverless::Function` | Lambda function |
| `AWS::Serverless::Api` | API Gateway REST API |
| `AWS::Serverless::HttpApi` | API Gateway HTTP API |
| `AWS::Serverless::SimpleTable` | DynamoDB table |
| `AWS::Serverless::LayerVersion` | Lambda layer |
| `AWS::Serverless::Application` | Nested application |
| `AWS::Serverless::StateMachine` | Step Functions |

## Defining Lambda Functions

### Basic Function

```yaml
Resources:
  HelloFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: hello-function
      Handler: app.handler
      Runtime: python3.12
      CodeUri: src/hello/
      Description: Says hello
      MemorySize: 256
      Timeout: 30
```

### Function with API Event

```yaml
Resources:
  UsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: users.handler
      Runtime: nodejs20.x
      CodeUri: src/users/
      Events:
        GetUsers:
          Type: Api
          Properties:
            Path: /users
            Method: GET
        GetUser:
          Type: Api
          Properties:
            Path: /users/{userId}
            Method: GET
        CreateUser:
          Type: Api
          Properties:
            Path: /users
            Method: POST
```

### Function with Multiple Event Sources

```yaml
Resources:
  ProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: processor.handler
      Runtime: python3.12
      CodeUri: src/processor/
      Events:
        # API Gateway trigger
        ApiEvent:
          Type: Api
          Properties:
            Path: /process
            Method: POST

        # S3 trigger
        S3Event:
          Type: S3
          Properties:
            Bucket: !Ref DataBucket
            Events: s3:ObjectCreated:*
            Filter:
              S3Key:
                Rules:
                  - Name: prefix
                    Value: uploads/

        # SQS trigger
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt ProcessingQueue.Arn
            BatchSize: 10

        # Schedule trigger
        ScheduleEvent:
          Type: Schedule
          Properties:
            Schedule: rate(1 hour)
            Description: Hourly processing
```

### Function with DynamoDB Stream

```yaml
Resources:
  StreamProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: stream.handler
      Runtime: python3.12
      CodeUri: src/stream/
      Events:
        DynamoDBStream:
          Type: DynamoDB
          Properties:
            Stream: !GetAtt UsersTable.StreamArn
            StartingPosition: LATEST
            BatchSize: 100
            MaximumBatchingWindowInSeconds: 10
            FilterCriteria:
              Filters:
                - Pattern: '{"eventName": ["INSERT", "MODIFY"]}'
      Policies:
        - DynamoDBStreamReadPolicy:
            TableName: !Ref UsersTable
```

## Defining APIs

### REST API (API Gateway)

```yaml
Resources:
  RestApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: users-rest-api
      StageName: prod
      Description: Users REST API
      EndpointConfiguration:
        Type: REGIONAL
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
      GatewayResponses:
        UNAUTHORIZED:
          StatusCode: 401
          ResponseTemplates:
            application/json: '{"message": "Unauthorized"}'

  UsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: users.handler
      Runtime: python3.12
      CodeUri: src/
      Events:
        GetUsers:
          Type: Api
          Properties:
            RestApiId: !Ref RestApi
            Path: /users
            Method: GET
            Auth:
              Authorizer: CognitoAuthorizer
```

### HTTP API (Lower Cost)

```yaml
Resources:
  HttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: prod
      Description: Users HTTP API
      CorsConfiguration:
        AllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
        AllowHeaders:
          - Content-Type
          - Authorization
        AllowOrigins:
          - https://example.com
      Auth:
        DefaultAuthorizer: JWTAuthorizer
        Authorizers:
          JWTAuthorizer:
            AuthorizationScopes:
              - read:users
            IdentitySource: $request.header.Authorization
            JwtConfiguration:
              issuer: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxx
              audience:
                - client-id

  UsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: users.handler
      Runtime: python3.12
      CodeUri: src/
      Events:
        GetUsers:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /users
            Method: GET
```

## Built-in Policies

### Common Policy Templates

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      Runtime: python3.12
      CodeUri: src/
      Policies:
        # DynamoDB policies
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
        - DynamoDBReadPolicy:
            TableName: !Ref ConfigTable
        - DynamoDBStreamReadPolicy:
            TableName: !Ref EventsTable

        # S3 policies
        - S3ReadPolicy:
            BucketName: !Ref DataBucket
        - S3WritePolicy:
            BucketName: !Ref OutputBucket
        - S3CrudPolicy:
            BucketName: !Ref StorageBucket

        # SQS policies
        - SQSPollerPolicy:
            QueueName: !GetAtt InputQueue.QueueName
        - SQSSendMessagePolicy:
            QueueName: !GetAtt OutputQueue.QueueName

        # SNS policies
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt NotificationTopic.TopicName

        # Secrets Manager
        - AWSSecretsManagerGetSecretValuePolicy:
            SecretArn: !Ref DatabaseSecret

        # Step Functions
        - StepFunctionsExecutionPolicy:
            StateMachineName: !GetAtt OrderWorkflow.Name

        # Lambda invocation
        - LambdaInvokePolicy:
            FunctionName: !Ref HelperFunction
```

### Custom IAM Policy

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      Runtime: python3.12
      CodeUri: src/
      Policies:
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - ec2:DescribeInstances
                - ec2:StartInstances
                - ec2:StopInstances
              Resource: '*'
              Condition:
                StringEquals:
                  'ec2:ResourceTag/Environment': !Ref Environment
```

## SAM CLI Commands

### sam init - Initialize Project

```bash
# Interactive mode
sam init

# Quick start with template
sam init --runtime python3.12 --name my-app --app-template hello-world

# From Git repository
sam init --location https://github.com/aws-samples/cookiecutter-aws-sam-python

# List available templates
sam init --help
```

### sam build - Build Application

```bash
# Build all functions
sam build

# Build specific function
sam build MyFunction

# Build with Docker (for compiled languages)
sam build --use-container

# Build with specific Docker image
sam build --use-container --build-image amazon/aws-sam-cli-build-image-python3.12

# Build in parallel
sam build --parallel

# Clean build
sam build --cached
```

### sam local - Local Testing

```bash
# Invoke function locally
sam local invoke MyFunction --event events/event.json

# Invoke with environment variables
sam local invoke MyFunction --env-vars env.json

# Start local API
sam local start-api

# Start API on specific port
sam local start-api --port 8080

# Start local Lambda endpoint
sam local start-lambda

# Generate sample event
sam local generate-event s3 put --bucket my-bucket --key test.json

# Debug mode (Node.js)
sam local invoke --debug-port 5858 MyFunction

# Debug mode (Python)
sam local invoke --debug-port 5678 MyFunction
```

### sam deploy - Deploy Application

```bash
# Guided deployment (first time)
sam deploy --guided

# Deploy with existing config
sam deploy

# Deploy with specific parameters
sam deploy \
    --stack-name my-stack \
    --s3-bucket my-deployment-bucket \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides Environment=prod

# Deploy without confirmation
sam deploy --no-confirm-changeset

# Deploy to specific region
sam deploy --region us-west-2
```

### sam sync - Fast Development

```bash
# Sync code changes (no CloudFormation update)
sam sync --watch

# Sync specific resources
sam sync --code

# Sync with stack name
sam sync --stack-name my-stack --watch
```

### sam logs - View Logs

```bash
# Tail logs
sam logs --name MyFunction --tail

# Filter logs
sam logs --name MyFunction --filter "ERROR"

# Logs from specific time
sam logs --name MyFunction --start-time '5 minutes ago'

# Include X-Ray traces
sam logs --name MyFunction --include-traces
```

### sam validate - Validate Template

```bash
# Validate SAM template
sam validate

# Validate with lint
sam validate --lint
```

## Complete Application Example

### Project Structure

```
my-serverless-app/
├── template.yaml           # SAM template
├── samconfig.toml         # SAM configuration
├── events/                 # Test events
│   ├── api-event.json
│   └── s3-event.json
├── src/
│   ├── users/             # Users function
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── orders/            # Orders function
│   │   ├── app.py
│   │   └── requirements.txt
│   └── shared/            # Shared code (layer)
│       └── python/
│           └── utils.py
├── tests/                  # Unit tests
│   ├── test_users.py
│   └── test_orders.py
└── README.md
```

### Complete template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Complete Serverless Application

# Global Configuration
Globals:
  Function:
    Runtime: python3.12
    Timeout: 30
    MemorySize: 256
    Tracing: Active
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment
        LOG_LEVEL: !If [IsProd, INFO, DEBUG]
    Layers:
      - !Ref SharedUtilsLayer

# Parameters
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

# Conditions
Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  # ============= API =============
  RestApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub ${AWS::StackName}-api
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization,X-Request-ID'"
        AllowOrigin: "'*'"
      TracingEnabled: true
      MethodSettings:
        - ResourcePath: /*
          HttpMethod: '*'
          LoggingLevel: !If [IsProd, ERROR, INFO]
          DataTraceEnabled: !If [IsProd, false, true]

  # ============= Lambda Layers =============
  SharedUtilsLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub ${AWS::StackName}-shared-utils
      Description: Shared utilities
      ContentUri: src/shared/
      CompatibleRuntimes:
        - python3.12
    Metadata:
      BuildMethod: python3.12

  # ============= Users Functions =============
  GetUsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-get-users
      Handler: app.get_users
      CodeUri: src/users/
      Description: Get all users
      Environment:
        Variables:
          USERS_TABLE: !Ref UsersTable
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref UsersTable
      Events:
        GetUsers:
          Type: Api
          Properties:
            RestApiId: !Ref RestApi
            Path: /users
            Method: GET

  GetUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-get-user
      Handler: app.get_user
      CodeUri: src/users/
      Description: Get single user
      Environment:
        Variables:
          USERS_TABLE: !Ref UsersTable
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref UsersTable
      Events:
        GetUser:
          Type: Api
          Properties:
            RestApiId: !Ref RestApi
            Path: /users/{userId}
            Method: GET

  CreateUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-create-user
      Handler: app.create_user
      CodeUri: src/users/
      Description: Create new user
      Environment:
        Variables:
          USERS_TABLE: !Ref UsersTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
      Events:
        CreateUser:
          Type: Api
          Properties:
            RestApiId: !Ref RestApi
            Path: /users
            Method: POST

  # ============= Orders Functions =============
  ProcessOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-process-order
      Handler: app.process_order
      CodeUri: src/orders/
      Description: Process new orders from SQS
      Environment:
        Variables:
          ORDERS_TABLE: !Ref OrdersTable
          NOTIFICATION_TOPIC: !Ref NotificationTopic
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt NotificationTopic.TopicName
      Events:
        SQSEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt OrdersQueue.Arn
            BatchSize: 10
            FunctionResponseTypes:
              - ReportBatchItemFailures

  # ============= DynamoDB Tables =============
  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${AWS::StackName}-users
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: userId
          AttributeType: S
        - AttributeName: email
          AttributeType: S
      KeySchema:
        - AttributeName: userId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: email-index
          KeySchema:
            - AttributeName: email
              KeyType: HASH
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: !If [IsProd, true, false]

  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${AWS::StackName}-orders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
        - AttributeName: userId
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: user-orders-index
          KeySchema:
            - AttributeName: userId
              KeyType: HASH
          Projection:
            ProjectionType: ALL

  # ============= SQS Queues =============
  OrdersQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub ${AWS::StackName}-orders-queue
      VisibilityTimeout: 180
      MessageRetentionPeriod: 1209600  # 14 days
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt OrdersDLQ.Arn
        maxReceiveCount: 3

  OrdersDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub ${AWS::StackName}-orders-dlq
      MessageRetentionPeriod: 1209600

  # ============= SNS Topics =============
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub ${AWS::StackName}-notifications
      DisplayName: Order Notifications

  # ============= S3 Buckets =============
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${AWS::StackName}-data-${AWS::AccountId}
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

# Outputs
Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${RestApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}/"
    Export:
      Name: !Sub ${AWS::StackName}-ApiEndpoint

  UsersTableName:
    Description: Users DynamoDB table name
    Value: !Ref UsersTable
    Export:
      Name: !Sub ${AWS::StackName}-UsersTable

  OrdersQueueUrl:
    Description: Orders SQS queue URL
    Value: !Ref OrdersQueue
    Export:
      Name: !Sub ${AWS::StackName}-OrdersQueue

  DataBucketName:
    Description: Data S3 bucket name
    Value: !Ref DataBucket
    Export:
      Name: !Sub ${AWS::StackName}-DataBucket
```

### Users Handler (src/users/app.py)

```python
import json
import os
import boto3
from utils import create_response, parse_body, validate_required

# Initialize outside handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USERS_TABLE'])


def get_users(event, context):
    """Get all users"""
    try:
        response = table.scan()
        users = response.get('Items', [])

        return create_response(200, {
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        return create_response(500, {'error': str(e)})


def get_user(event, context):
    """Get single user by ID"""
    try:
        user_id = event['pathParameters']['userId']

        response = table.get_item(Key={'userId': user_id})
        user = response.get('Item')

        if not user:
            return create_response(404, {'error': 'User not found'})

        return create_response(200, {'user': user})
    except Exception as e:
        return create_response(500, {'error': str(e)})


def create_user(event, context):
    """Create new user"""
    try:
        body = parse_body(event)
        validate_required(body, ['email', 'name'])

        import uuid
        user = {
            'userId': str(uuid.uuid4()),
            'email': body['email'],
            'name': body['name'],
            'status': 'active'
        }

        table.put_item(Item=user)

        return create_response(201, {'user': user})
    except ValueError as e:
        return create_response(400, {'error': str(e)})
    except Exception as e:
        return create_response(500, {'error': str(e)})
```

### SAM Configuration (samconfig.toml)

```toml
# samconfig.toml
version = 0.1

[default]
[default.global]
[default.global.parameters]
stack_name = "my-serverless-app"

[default.build]
[default.build.parameters]
cached = true
parallel = true

[default.validate]
[default.validate.parameters]
lint = true

[default.deploy]
[default.deploy.parameters]
capabilities = "CAPABILITY_IAM CAPABILITY_NAMED_IAM"
confirm_changeset = true
resolve_s3 = true
s3_prefix = "my-serverless-app"
region = "us-east-1"
parameter_overrides = "Environment=dev"

[default.sync]
[default.sync.parameters]
watch = true

[default.local_start_api]
[default.local_start_api.parameters]
warm_containers = "EAGER"

# Environment-specific configurations
[prod]
[prod.deploy]
[prod.deploy.parameters]
stack_name = "my-serverless-app-prod"
s3_prefix = "my-serverless-app-prod"
parameter_overrides = "Environment=prod"
confirm_changeset = false
```

## Local Testing

### Sample Events

```json
// events/api-event.json
{
  "resource": "/users/{userId}",
  "path": "/users/123",
  "httpMethod": "GET",
  "headers": {
    "Content-Type": "application/json"
  },
  "pathParameters": {
    "userId": "123"
  },
  "queryStringParameters": null,
  "body": null,
  "requestContext": {
    "stage": "dev",
    "requestId": "test-request-id"
  }
}
```

### Testing Commands

```bash
# Invoke function
sam local invoke GetUserFunction --event events/api-event.json

# Start local API
sam local start-api

# Test with curl
curl http://localhost:3000/users
curl http://localhost:3000/users/123
curl -X POST http://localhost:3000/users \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "name": "Test User"}'
```

### Environment Variables

```json
// env.json
{
  "GetUsersFunction": {
    "USERS_TABLE": "local-users-table",
    "LOG_LEVEL": "DEBUG"
  },
  "CreateUserFunction": {
    "USERS_TABLE": "local-users-table"
  }
}
```

```bash
sam local invoke --env-vars env.json GetUsersFunction
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy SAM Application

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pytest boto3 moto

      - name: Run tests
        run: pytest tests/ -v

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Setup SAM CLI
        uses: aws-actions/setup-sam@v2

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: SAM Build
        run: sam build

      - name: SAM Deploy
        run: |
          sam deploy \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset \
            --stack-name my-app-prod \
            --parameter-overrides Environment=prod
```

### AWS CodePipeline

```yaml
# buildspec.yml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.12

  build:
    commands:
      - pip install pytest
      - pytest tests/ -v
      - sam build

  post_build:
    commands:
      - sam package --output-template-file packaged.yaml --s3-bucket $S3_BUCKET

artifacts:
  files:
    - packaged.yaml
```

## Summary

### Key SAM CLI Commands

| Command | Purpose |
|---------|---------|
| `sam init` | Initialize new project |
| `sam build` | Build application |
| `sam local invoke` | Test function locally |
| `sam local start-api` | Start local API |
| `sam deploy` | Deploy to AWS |
| `sam sync` | Fast sync for development |
| `sam logs` | View function logs |
| `sam validate` | Validate template |

### SAM Best Practices

1. **Use Globals** for shared function configuration
2. **Use Parameters** for environment-specific values
3. **Use Built-in Policies** instead of inline policies
4. **Use Layers** for shared dependencies
5. **Enable Tracing** with X-Ray
6. **Use samconfig.toml** for deployment configuration

### Next Steps

Continue to [11-eventbridge.md](./11-eventbridge.md) to learn about building event-driven architectures with Amazon EventBridge.
