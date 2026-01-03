# Lambda Permissions and Security

## Introduction

Lambda functions require proper permissions configuration to securely access AWS resources and be invoked by other services. This section covers execution roles, resource-based policies, and cross-account patterns.

## Permission Model Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                LAMBDA PERMISSION MODEL                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WHO CAN INVOKE LAMBDA?          WHAT CAN LAMBDA ACCESS?        │
│  (Resource-Based Policy)          (Execution Role)               │
│                                                                  │
│  ┌─────────────┐                 ┌─────────────┐                │
│  │ API Gateway │                 │   Lambda    │                │
│  │     S3      │───────▶┌────┐──▶│  Function   │                │
│  │    SNS      │        │FUNC│   └──────┬──────┘                │
│  │   Events    │───────▶│TION│          │                       │
│  └─────────────┘        └────┘          ▼                       │
│                                  ┌─────────────┐                │
│                                  │ Execution   │                │
│                                  │    Role     │                │
│                                  └──────┬──────┘                │
│                                         │                       │
│                                         ▼                       │
│                                  ┌─────────────┐                │
│                                  │ DynamoDB    │                │
│                                  │     S3      │                │
│                                  │    SQS      │                │
│                                  │   Secrets   │                │
│                                  └─────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Execution Role

The execution role grants Lambda permission to access AWS services and resources.

### Trust Policy

Every Lambda execution role needs a trust policy allowing Lambda to assume it:

```json
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
```

### Creating an Execution Role

```bash
# Create trust policy file
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

# Create the role
aws iam create-role \
    --role-name my-lambda-role \
    --assume-role-policy-document file://trust-policy.json

# Attach basic execution policy (CloudWatch Logs)
aws iam attach-role-policy \
    --role-name my-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### AWS Managed Policies for Lambda

| Policy | Description |
|--------|-------------|
| `AWSLambdaBasicExecutionRole` | CloudWatch Logs permissions |
| `AWSLambdaVPCAccessExecutionRole` | VPC + CloudWatch Logs |
| `AWSLambdaDynamoDBExecutionRole` | DynamoDB Streams + Logs |
| `AWSLambdaKinesisExecutionRole` | Kinesis Streams + Logs |
| `AWSLambdaSQSQueueExecutionRole` | SQS + Logs |

### Custom Permission Policies

#### DynamoDB Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DynamoDBTableAccess",
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:123456789012:table/users",
                "arn:aws:dynamodb:us-east-1:123456789012:table/users/index/*"
            ]
        }
    ]
}
```

#### S3 Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3ReadAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        },
        {
            "Sid": "S3WriteAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::my-bucket/output/*"
        }
    ]
}
```

#### Secrets Manager Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SecretsAccess",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/*"
            ]
        },
        {
            "Sid": "KMSDecrypt",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "arn:aws:kms:us-east-1:123456789012:key/abc-123",
            "Condition": {
                "StringEquals": {
                    "kms:ViaService": "secretsmanager.us-east-1.amazonaws.com"
                }
            }
        }
    ]
}
```

#### SNS/SQS Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SNSPublish",
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:us-east-1:123456789012:notifications"
        },
        {
            "Sid": "SQSSend",
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:GetQueueUrl"
            ],
            "Resource": "arn:aws:sqs:us-east-1:123456789012:orders-queue"
        }
    ]
}
```

### SAM Template with Policies

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.12
      CodeUri: src/

      # Option 1: Use SAM policy templates
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
        - S3ReadPolicy:
            BucketName: !Ref DataBucket
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt NotificationTopic.TopicName
        - SQSSendMessagePolicy:
            QueueName: !GetAtt OrderQueue.QueueName

  MyFunctionWithCustomRole:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.12
      CodeUri: src/

      # Option 2: Use custom role
      Role: !GetAtt CustomLambdaRole.Arn

  CustomLambdaRole:
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
      Policies:
        - PolicyName: CustomAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:*
                Resource: !GetAtt UsersTable.Arn
```

### SAM Policy Templates

SAM provides convenient policy templates:

| Template | Description |
|----------|-------------|
| `DynamoDBCrudPolicy` | CRUD operations on table |
| `DynamoDBReadPolicy` | Read-only table access |
| `S3ReadPolicy` | Read from S3 bucket |
| `S3WritePolicy` | Write to S3 bucket |
| `S3CrudPolicy` | Full S3 bucket access |
| `SNSPublishMessagePolicy` | Publish to SNS topic |
| `SQSSendMessagePolicy` | Send to SQS queue |
| `SQSPollerPolicy` | Receive from SQS queue |
| `KMSDecryptPolicy` | KMS decrypt |
| `SecretsManagerGetSecretValuePolicy` | Get secrets |
| `StepFunctionsExecutionPolicy` | Start Step Functions |
| `LambdaInvokePolicy` | Invoke other Lambda |

## Resource-Based Policies

Resource-based policies control which services and accounts can invoke the Lambda function.

### Viewing Resource Policy

```bash
aws lambda get-policy --function-name my-function
```

### Adding Permissions

#### API Gateway Permission

```bash
aws lambda add-permission \
    --function-name my-function \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:123456789012:abc123/*/*/*"
```

#### S3 Permission

```bash
aws lambda add-permission \
    --function-name my-function \
    --statement-id s3-invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-bucket \
    --source-account 123456789012
```

#### SNS Permission

```bash
aws lambda add-permission \
    --function-name my-function \
    --statement-id sns-invoke \
    --action lambda:InvokeFunction \
    --principal sns.amazonaws.com \
    --source-arn arn:aws:sns:us-east-1:123456789012:my-topic
```

#### CloudWatch Events / EventBridge Permission

```bash
aws lambda add-permission \
    --function-name my-function \
    --statement-id events-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:123456789012:rule/my-rule
```

#### Cross-Account Permission

```bash
aws lambda add-permission \
    --function-name my-function \
    --statement-id cross-account-invoke \
    --action lambda:InvokeFunction \
    --principal 999888777666 \
    --source-arn arn:aws:events:us-east-1:999888777666:rule/their-rule
```

### Removing Permissions

```bash
aws lambda remove-permission \
    --function-name my-function \
    --statement-id apigateway-invoke
```

### Resource Policy Example

```json
{
    "Version": "2012-10-17",
    "Id": "default",
    "Statement": [
        {
            "Sid": "apigateway-invoke",
            "Effect": "Allow",
            "Principal": {
                "Service": "apigateway.amazonaws.com"
            },
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
            "Condition": {
                "ArnLike": {
                    "AWS:SourceArn": "arn:aws:execute-api:us-east-1:123456789012:abc123/*/*/*"
                }
            }
        },
        {
            "Sid": "s3-invoke",
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceAccount": "123456789012"
                },
                "ArnLike": {
                    "AWS:SourceArn": "arn:aws:s3:::my-bucket"
                }
            }
        }
    ]
}
```

## Cross-Account Invocation

### Pattern 1: Resource-Based Policy (Push Model)

Account B's Lambda can be invoked by Account A's service.

```
┌─────────────────────────────────────────────────────────────────┐
│                   CROSS-ACCOUNT INVOCATION                       │
│                      (Push Model)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Account A (Caller)              Account B (Lambda Owner)        │
│  ┌─────────────────┐            ┌─────────────────┐             │
│  │                 │            │                 │             │
│  │  EventBridge    │───────────▶│    Lambda       │             │
│  │     Rule        │            │   Function      │             │
│  │                 │            │                 │             │
│  └─────────────────┘            └─────────────────┘             │
│                                         │                        │
│                                         ▼                        │
│                                  Resource-Based Policy           │
│                                  (Allows Account A)              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**In Account B (Lambda owner):**

```bash
# Allow Account A to invoke
aws lambda add-permission \
    --function-name my-function \
    --statement-id allow-account-a \
    --action lambda:InvokeFunction \
    --principal 111122223333  # Account A's ID
```

**In Account A (Caller):**

```bash
# Invoke the function in Account B
aws lambda invoke \
    --function-name arn:aws:lambda:us-east-1:999888777666:function:my-function \
    --payload '{"key": "value"}' \
    response.json
```

### Pattern 2: AssumeRole (Pull Model)

Account A assumes a role in Account B to invoke Lambda.

```
┌─────────────────────────────────────────────────────────────────┐
│                   CROSS-ACCOUNT INVOCATION                       │
│                      (Pull Model)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Account A                       Account B                       │
│  ┌─────────────────┐            ┌─────────────────┐             │
│  │                 │            │                 │             │
│  │    Lambda       │──AssumeRole─▶│  IAM Role     │             │
│  │   Function      │            │                 │             │
│  │                 │            └────────┬────────┘             │
│  └─────────────────┘                     │                       │
│                                          ▼                       │
│                                  ┌─────────────────┐             │
│                                  │    Lambda       │             │
│                                  │   Function      │             │
│                                  └─────────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**In Account B (Create role for Account A):**

```json
// Trust policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111122223333:role/AccountALambdaRole"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

```json
// Permission policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:us-east-1:999888777666:function:my-function"
        }
    ]
}
```

**In Account A (Lambda code):**

```python
import boto3
import json

def handler(event, context):
    # Assume role in Account B
    sts = boto3.client('sts')

    assumed_role = sts.assume_role(
        RoleArn='arn:aws:iam::999888777666:role/CrossAccountLambdaRole',
        RoleSessionName='cross-account-session'
    )

    credentials = assumed_role['Credentials']

    # Create Lambda client with assumed credentials
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    # Invoke function in Account B
    response = lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:999888777666:function:my-function',
        InvocationType='RequestResponse',
        Payload=json.dumps({'key': 'value'})
    )

    return json.loads(response['Payload'].read())
```

## Least Privilege Best Practices

### 1. Scope Resources Specifically

```json
// Bad - Too broad
{
    "Effect": "Allow",
    "Action": "dynamodb:*",
    "Resource": "*"
}

// Good - Specific table and actions
{
    "Effect": "Allow",
    "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
    ],
    "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/users"
}
```

### 2. Use Conditions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "StringEquals": {
                    "s3:ExistingObjectTag/environment": "production"
                }
            }
        }
    ]
}
```

### 3. Separate Roles per Function

```yaml
# Each function gets its own role
OrderFunction:
  Type: AWS::Serverless::Function
  Properties:
    Policies:
      - DynamoDBCrudPolicy:
          TableName: !Ref OrdersTable

PaymentFunction:
  Type: AWS::Serverless::Function
  Properties:
    Policies:
      - DynamoDBReadPolicy:
          TableName: !Ref PaymentsTable
      - SNSPublishMessagePolicy:
          TopicName: !GetAtt PaymentTopic.TopicName
```

### 4. Use IAM Access Analyzer

```bash
# Analyze function policy
aws accessanalyzer start-policy-generation \
    --policy-generation-details '{
        "principalArn": "arn:aws:iam::123456789012:role/my-lambda-role"
    }'
```

## Function URLs Authentication

Lambda Function URLs can be configured with different authentication modes.

### IAM Authentication

```bash
# Create function URL with IAM auth
aws lambda create-function-url-config \
    --function-name my-function \
    --auth-type AWS_IAM \
    --cors '{
        "AllowOrigins": ["https://example.com"],
        "AllowMethods": ["GET", "POST"],
        "AllowHeaders": ["Content-Type"]
    }'
```

### No Authentication (Public)

```bash
# Create function URL without auth
aws lambda create-function-url-config \
    --function-name my-function \
    --auth-type NONE

# Grant public access
aws lambda add-permission \
    --function-name my-function \
    --statement-id function-url-public \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE
```

### Calling Function URL with IAM Auth

```python
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

def call_lambda_url(url, payload):
    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name

    # Create request
    request = AWSRequest(
        method='POST',
        url=url,
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'}
    )

    # Sign request
    SigV4Auth(credentials, 'lambda', region).add_auth(request)

    # Send request
    response = requests.post(
        url,
        data=request.data,
        headers=dict(request.headers)
    )

    return response.json()
```

## Security Best Practices Summary

### Execution Role

1. **Use least privilege**: Only grant necessary permissions
2. **Use SAM policy templates**: Pre-built, scoped policies
3. **Separate roles per function**: Isolate permissions
4. **Use conditions**: Add additional constraints
5. **Regular audits**: Review and remove unused permissions

### Resource-Based Policies

1. **Always use source conditions**: Prevent confused deputy
2. **Scope to specific resources**: Not `*`
3. **Use source account**: For S3, SNS triggers
4. **Review regularly**: Remove old permissions

### General Security

1. **Encrypt environment variables**: Use KMS for sensitive data
2. **Use Secrets Manager**: For credentials and API keys
3. **Enable VPC**: For private resource access
4. **Enable X-Ray**: For security tracing
5. **Use AWS Config**: Monitor compliance

## Summary

### Key Takeaways

1. **Two permission types**: Execution role (what Lambda can do) and resource-based policy (who can invoke Lambda)
2. **Least privilege**: Always scope permissions to minimum required
3. **Cross-account patterns**: Use resource policies or AssumeRole
4. **SAM simplifies IAM**: Use policy templates for common patterns
5. **Security conditions**: Always use source ARN/account conditions

### Next Steps

Continue to [06-api-gateway.md](./06-api-gateway.md) to learn about building APIs with API Gateway and Lambda integration.
