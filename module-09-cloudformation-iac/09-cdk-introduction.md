# Lesson 09: AWS CDK Introduction

## Introduction

AWS Cloud Development Kit (CDK) is an open-source software development framework to define cloud infrastructure in code and provision it through AWS CloudFormation. Unlike traditional CloudFormation templates written in YAML or JSON, CDK allows you to use familiar programming languages like TypeScript, Python, Java, C#, and Go.

---

## What is AWS CDK?

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS CDK Overview                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Your Code (TypeScript/Python/Java/C#/Go)                       │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────┐                    │
│  │              CDK CLI                     │                    │
│  │         (cdk synth)                      │                    │
│  └─────────────────────────────────────────┘                    │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────┐                    │
│  │       CloudFormation Template            │                    │
│  │            (JSON/YAML)                   │                    │
│  └─────────────────────────────────────────┘                    │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────┐                    │
│  │         AWS CloudFormation               │                    │
│  │     (Deploy AWS Resources)               │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Familiar Languages** | Use TypeScript, Python, Java, C#, or Go |
| **IDE Support** | Auto-completion, type checking, inline docs |
| **Abstraction Layers** | High-level constructs reduce boilerplate |
| **Reusability** | Share constructs as npm/pip packages |
| **Testing** | Unit test your infrastructure |
| **Loops & Conditions** | Use native programming constructs |

---

## CDK vs CloudFormation

```
┌─────────────────────────────────────────────────────────────────┐
│                 CDK vs CloudFormation                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Feature              CloudFormation       CDK                   │
│  ─────────────────────────────────────────────────────────────  │
│  Language             YAML/JSON            Programming langs    │
│  IDE Support          Limited              Full                 │
│  Type Safety          No                   Yes                  │
│  Abstraction          Low-level            Multi-level          │
│  Learning Curve       Declarative syntax   Familiar language    │
│  Testing              TaskCat              Standard frameworks  │
│  Modularity           Nested stacks        Constructs/libs      │
│  State Management     CloudFormation       CloudFormation       │
│  Deployment           Direct               Via CloudFormation   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Code Comparison

**CloudFormation (YAML):**
```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-app-bucket
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
```

**CDK (TypeScript):**
```typescript
const bucket = new s3.Bucket(this, 'MyBucket', {
  bucketName: 'my-app-bucket',
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
});
```

**CDK (Python):**
```python
bucket = s3.Bucket(
    self, "MyBucket",
    bucket_name="my-app-bucket",
    versioned=True,
    encryption=s3.BucketEncryption.S3_MANAGED,
    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
)
```

---

## CDK Concepts

### The CDK App Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                     CDK App Structure                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  App (cdk.App)                                                   │
│  └── Stack 1 (cdk.Stack)                                        │
│      ├── Construct A                                            │
│      │   └── Child Constructs                                   │
│      ├── Construct B                                            │
│      └── Construct C                                            │
│  └── Stack 2 (cdk.Stack)                                        │
│      ├── Construct D                                            │
│      └── Construct E                                            │
│                                                                  │
│  Each stack becomes a CloudFormation stack                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Constructs - The Building Blocks

Constructs are the basic building blocks of CDK apps. They represent AWS resources or higher-level components.

```
┌─────────────────────────────────────────────────────────────────┐
│                   Construct Levels                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  L1 (CFN Resources) - Lowest Level                              │
│  ├── Direct mapping to CloudFormation                           │
│  ├── Prefixed with "Cfn" (e.g., CfnBucket)                     │
│  ├── All properties must be specified                           │
│  └── No defaults or convenience methods                         │
│                                                                  │
│  L2 (Curated Constructs) - Middle Level                         │
│  ├── AWS-curated with sensible defaults                         │
│  ├── Higher-level APIs                                          │
│  ├── Convenience methods (grantRead, addToPolicy)              │
│  └── Most commonly used                                         │
│                                                                  │
│  L3 (Patterns) - Highest Level                                  │
│  ├── Opinionated architectures                                  │
│  ├── Multiple resources combined                                │
│  ├── Common patterns (LambdaRestApi)                           │
│  └── Maximum convenience                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Construct Level Examples

**L1 Construct (Low-level):**
```typescript
// Direct CloudFormation mapping - must specify everything
const cfnBucket = new s3.CfnBucket(this, 'MyCfnBucket', {
  bucketName: 'my-bucket',
  versioningConfiguration: {
    status: 'Enabled'
  },
  bucketEncryption: {
    serverSideEncryptionConfiguration: [{
      serverSideEncryptionByDefault: {
        sseAlgorithm: 'AES256'
      }
    }]
  }
});
```

**L2 Construct (High-level):**
```typescript
// Sensible defaults, convenience methods
const bucket = new s3.Bucket(this, 'MyBucket', {
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
});

// Convenience method to grant access
bucket.grantRead(myLambdaFunction);
```

**L3 Construct (Pattern):**
```typescript
// Complete pattern with multiple resources
const api = new apigateway.LambdaRestApi(this, 'MyApi', {
  handler: myLambdaFunction,
  // Automatically creates:
  // - API Gateway REST API
  // - Lambda integration
  // - IAM permissions
  // - CloudWatch logs
});
```

---

## Getting Started with CDK

### Prerequisites

```bash
# Install Node.js (required for CDK CLI)
# https://nodejs.org/

# Install AWS CDK CLI globally
npm install -g aws-cdk

# Verify installation
cdk --version
```

### CDK CLI Commands

| Command | Description |
|---------|-------------|
| `cdk init` | Create a new CDK project |
| `cdk synth` | Synthesize CloudFormation template |
| `cdk diff` | Compare deployed stack with local changes |
| `cdk deploy` | Deploy stack(s) to AWS |
| `cdk destroy` | Delete stack(s) from AWS |
| `cdk bootstrap` | Prepare AWS environment for CDK |
| `cdk list` | List all stacks in the app |
| `cdk doctor` | Check for potential problems |

---

## Hands-On: TypeScript CDK Project

### Step 1: Initialize Project

```bash
# Create project directory
mkdir my-cdk-app
cd my-cdk-app

# Initialize TypeScript CDK project
cdk init app --language typescript

# Project structure created:
# my-cdk-app/
# ├── bin/
# │   └── my-cdk-app.ts      # App entry point
# ├── lib/
# │   └── my-cdk-app-stack.ts # Main stack definition
# ├── test/
# │   └── my-cdk-app.test.ts  # Test files
# ├── cdk.json                 # CDK configuration
# ├── package.json             # Node dependencies
# └── tsconfig.json            # TypeScript config
```

### Step 2: Bootstrap Your AWS Environment

```bash
# Bootstrap CDK in your AWS account/region
# This creates S3 bucket and IAM roles for CDK
cdk bootstrap aws://ACCOUNT-NUMBER/REGION

# Example
cdk bootstrap aws://123456789012/us-east-1

# Or use default profile
cdk bootstrap
```

### Step 3: Create a Simple Stack

**lib/my-cdk-app-stack.ts:**
```typescript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class MyCdkAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const table = new dynamodb.Table(this, 'ItemsTable', {
      partitionKey: {
        name: 'id',
        type: dynamodb.AttributeType.STRING
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For dev only
    });

    // S3 Bucket
    const bucket = new s3.Bucket(this, 'DataBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true, // For dev only
    });

    // Lambda Function
    const handler = new lambda.Function(this, 'ApiHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'index.handler',
      environment: {
        TABLE_NAME: table.tableName,
        BUCKET_NAME: bucket.bucketName,
      },
    });

    // Grant permissions (CDK handles IAM automatically)
    table.grantReadWriteData(handler);
    bucket.grantReadWrite(handler);

    // API Gateway
    const api = new apigateway.RestApi(this, 'ItemsApi', {
      restApiName: 'Items Service',
      description: 'This service serves items.',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
      },
    });

    // API Resources
    const items = api.root.addResource('items');
    items.addMethod('GET', new apigateway.LambdaIntegration(handler));
    items.addMethod('POST', new apigateway.LambdaIntegration(handler));

    const item = items.addResource('{id}');
    item.addMethod('GET', new apigateway.LambdaIntegration(handler));
    item.addMethod('DELETE', new apigateway.LambdaIntegration(handler));

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'API Gateway URL',
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: table.tableName,
      description: 'DynamoDB Table Name',
    });

    new cdk.CfnOutput(this, 'BucketName', {
      value: bucket.bucketName,
      description: 'S3 Bucket Name',
    });
  }
}
```

### Step 4: Create Lambda Handler

**lambda/index.ts:**
```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  PutCommand,
  GetCommand,
  ScanCommand,
  DeleteCommand
} from '@aws-sdk/lib-dynamodb';

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);
const tableName = process.env.TABLE_NAME!;

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  console.log('Event:', JSON.stringify(event, null, 2));

  try {
    const method = event.httpMethod;
    const path = event.path;
    const id = event.pathParameters?.id;

    if (method === 'GET' && path === '/items') {
      // List all items
      const result = await docClient.send(new ScanCommand({
        TableName: tableName,
      }));
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result.Items),
      };
    }

    if (method === 'GET' && id) {
      // Get single item
      const result = await docClient.send(new GetCommand({
        TableName: tableName,
        Key: { id },
      }));
      return {
        statusCode: result.Item ? 200 : 404,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result.Item || { message: 'Item not found' }),
      };
    }

    if (method === 'POST') {
      // Create item
      const body = JSON.parse(event.body || '{}');
      const item = {
        id: body.id || Date.now().toString(),
        ...body,
        createdAt: new Date().toISOString(),
      };
      await docClient.send(new PutCommand({
        TableName: tableName,
        Item: item,
      }));
      return {
        statusCode: 201,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      };
    }

    if (method === 'DELETE' && id) {
      // Delete item
      await docClient.send(new DeleteCommand({
        TableName: tableName,
        Key: { id },
      }));
      return {
        statusCode: 204,
        body: '',
      };
    }

    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Invalid request' }),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Internal server error' }),
    };
  }
};
```

### Step 5: Deploy

```bash
# Synthesize CloudFormation template
cdk synth

# View changes before deploying
cdk diff

# Deploy to AWS
cdk deploy

# Deploy with auto-approve
cdk deploy --require-approval never
```

---

## Hands-On: Python CDK Project

### Step 1: Initialize Project

```bash
# Create project directory
mkdir my-python-cdk-app
cd my-python-cdk-app

# Initialize Python CDK project
cdk init app --language python

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create a Stack

**my_python_cdk_app/my_python_cdk_app_stack.py:**
```python
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)
from constructs import Construct


class MyPythonCdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Table
        table = dynamodb.Table(
            self, "ItemsTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,  # Dev only
        )

        # S3 Bucket
        bucket = s3.Bucket(
            self, "DataBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,  # Dev only
        )

        # SQS Queue for async processing
        queue = sqs.Queue(
            self, "ProcessingQueue",
            visibility_timeout=Duration.seconds(300),
            retention_period=Duration.days(14),
        )

        # SNS Topic for notifications
        topic = sns.Topic(
            self, "NotificationTopic",
            display_name="Item Notifications"
        )

        # Lambda Function
        handler = lambda_.Function(
            self, "ApiHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda"),
            handler="index.handler",
            environment={
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": bucket.bucket_name,
                "QUEUE_URL": queue.queue_url,
                "TOPIC_ARN": topic.topic_arn,
            },
            timeout=Duration.seconds(30),
        )

        # Grant permissions
        table.grant_read_write_data(handler)
        bucket.grant_read_write(handler)
        queue.grant_send_messages(handler)
        topic.grant_publish(handler)

        # API Gateway
        api = apigateway.RestApi(
            self, "ItemsApi",
            rest_api_name="Items Service",
            description="This service serves items.",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            ),
        )

        # API Resources and Methods
        items = api.root.add_resource("items")
        items.add_method("GET", apigateway.LambdaIntegration(handler))
        items.add_method("POST", apigateway.LambdaIntegration(handler))

        item = items.add_resource("{id}")
        item.add_method("GET", apigateway.LambdaIntegration(handler))
        item.add_method("PUT", apigateway.LambdaIntegration(handler))
        item.add_method("DELETE", apigateway.LambdaIntegration(handler))

        # Outputs
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway URL"
        )

        CfnOutput(
            self, "TableName",
            value=table.table_name,
            description="DynamoDB Table Name"
        )

        CfnOutput(
            self, "BucketName",
            value=bucket.bucket_name,
            description="S3 Bucket Name"
        )
```

### Step 3: Create Lambda Handler

**lambda/index.py:**
```python
import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sqs = boto3.client('sqs')
sns = boto3.client('sns')

table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket_name = os.environ['BUCKET_NAME']
queue_url = os.environ['QUEUE_URL']
topic_arn = os.environ['TOPIC_ARN']


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)


def handler(event, context):
    print(f"Event: {json.dumps(event)}")

    try:
        method = event['httpMethod']
        path = event['path']
        path_params = event.get('pathParameters') or {}
        item_id = path_params.get('id')

        if method == 'GET' and path == '/items':
            # List all items
            response = table.scan()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(response.get('Items', []), cls=DecimalEncoder)
            }

        if method == 'GET' and item_id:
            # Get single item
            response = table.get_item(Key={'id': item_id})
            item = response.get('Item')
            if item:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(item, cls=DecimalEncoder)
                }
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Item not found'})
            }

        if method == 'POST':
            # Create item
            body = json.loads(event.get('body') or '{}')
            item = {
                'id': body.get('id', str(int(datetime.now().timestamp() * 1000))),
                **body,
                'createdAt': datetime.now().isoformat()
            }
            table.put_item(Item=item)

            # Send notification
            sns.publish(
                TopicArn=topic_arn,
                Message=f"New item created: {item['id']}",
                Subject="Item Created"
            )

            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(item, cls=DecimalEncoder)
            }

        if method == 'PUT' and item_id:
            # Update item
            body = json.loads(event.get('body') or '{}')
            item = {
                'id': item_id,
                **body,
                'updatedAt': datetime.now().isoformat()
            }
            table.put_item(Item=item)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(item, cls=DecimalEncoder)
            }

        if method == 'DELETE' and item_id:
            # Delete item
            table.delete_item(Key={'id': item_id})
            return {
                'statusCode': 204,
                'body': ''
            }

        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Invalid request'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Internal server error'})
        }
```

### Step 4: Deploy

```bash
# Synthesize
cdk synth

# View diff
cdk diff

# Deploy
cdk deploy
```

---

## Advanced CDK Concepts

### Using Aspects for Cross-Cutting Concerns

```typescript
import * as cdk from 'aws-cdk-lib';
import { IAspect, Tags } from 'aws-cdk-lib';
import { IConstruct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';

// Aspect to ensure all S3 buckets have versioning
class BucketVersioningChecker implements IAspect {
  public visit(node: IConstruct): void {
    if (node instanceof s3.CfnBucket) {
      if (!node.versioningConfiguration) {
        cdk.Annotations.of(node).addWarning('Bucket versioning is not enabled');
      }
    }
  }
}

// Aspect to add tags to all resources
class TaggingAspect implements IAspect {
  constructor(private readonly tags: { [key: string]: string }) {}

  public visit(node: IConstruct): void {
    if (cdk.TagManager.isTaggable(node)) {
      for (const [key, value] of Object.entries(this.tags)) {
        Tags.of(node).add(key, value);
      }
    }
  }
}

// Apply aspects to stack
const app = new cdk.App();
const stack = new MyStack(app, 'MyStack');

cdk.Aspects.of(stack).add(new BucketVersioningChecker());
cdk.Aspects.of(stack).add(new TaggingAspect({
  Environment: 'Production',
  Team: 'Platform'
}));
```

### Custom Constructs

```typescript
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import { Construct } from 'constructs';

// Custom L3 construct for a secure database
export interface SecureDatabaseProps {
  vpc: ec2.IVpc;
  databaseName: string;
  instanceType?: ec2.InstanceType;
}

export class SecureDatabase extends Construct {
  public readonly cluster: rds.DatabaseCluster;
  public readonly secret: rds.DatabaseSecret;

  constructor(scope: Construct, id: string, props: SecureDatabaseProps) {
    super(scope, id);

    // Create secret for credentials
    this.secret = new rds.DatabaseSecret(this, 'Secret', {
      username: 'admin',
    });

    // Create Aurora cluster
    this.cluster = new rds.DatabaseCluster(this, 'Cluster', {
      engine: rds.DatabaseClusterEngine.auroraMysql({
        version: rds.AuroraMysqlEngineVersion.VER_3_04_0,
      }),
      credentials: rds.Credentials.fromSecret(this.secret),
      defaultDatabaseName: props.databaseName,
      vpc: props.vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      writer: rds.ClusterInstance.provisioned('Writer', {
        instanceType: props.instanceType || ec2.InstanceType.of(
          ec2.InstanceClass.T3,
          ec2.InstanceSize.MEDIUM
        ),
      }),
      readers: [
        rds.ClusterInstance.provisioned('Reader', {
          instanceType: props.instanceType || ec2.InstanceType.of(
            ec2.InstanceClass.T3,
            ec2.InstanceSize.MEDIUM
          ),
        }),
      ],
      storageEncrypted: true,
      deletionProtection: true,
      backup: {
        retention: cdk.Duration.days(30),
      },
    });
  }
}

// Usage
const database = new SecureDatabase(this, 'Database', {
  vpc: myVpc,
  databaseName: 'myapp',
});
```

### Environment-Specific Configuration

```typescript
import * as cdk from 'aws-cdk-lib';

// Define environment configuration
interface EnvironmentConfig {
  instanceType: string;
  minCapacity: number;
  maxCapacity: number;
  enableDeletionProtection: boolean;
}

const environments: { [key: string]: EnvironmentConfig } = {
  dev: {
    instanceType: 't3.micro',
    minCapacity: 1,
    maxCapacity: 2,
    enableDeletionProtection: false,
  },
  staging: {
    instanceType: 't3.small',
    minCapacity: 2,
    maxCapacity: 4,
    enableDeletionProtection: true,
  },
  prod: {
    instanceType: 't3.medium',
    minCapacity: 4,
    maxCapacity: 10,
    enableDeletionProtection: true,
  },
};

// Use in stack
const envName = app.node.tryGetContext('env') || 'dev';
const config = environments[envName];

// Deploy with context
// cdk deploy --context env=prod
```

### Cross-Stack References

```typescript
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

// VPC Stack
class VpcStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
    });
  }
}

// Application Stack
interface AppStackProps extends cdk.StackProps {
  vpc: ec2.IVpc;
}

class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppStackProps) {
    super(scope, id, props);

    // Use VPC from VpcStack
    new ec2.Instance(this, 'Instance', {
      vpc: props.vpc,
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T3,
        ec2.InstanceSize.MICRO
      ),
      machineImage: ec2.MachineImage.latestAmazonLinux2023(),
    });
  }
}

// App
const app = new cdk.App();
const vpcStack = new VpcStack(app, 'VpcStack');
const appStack = new AppStack(app, 'AppStack', {
  vpc: vpcStack.vpc,
});

// AppStack depends on VpcStack
appStack.addDependency(vpcStack);
```

---

## Testing CDK Applications

### Unit Testing (TypeScript with Jest)

```typescript
import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { MyCdkAppStack } from '../lib/my-cdk-app-stack';

describe('MyCdkAppStack', () => {
  const app = new cdk.App();
  const stack = new MyCdkAppStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('DynamoDB Table Created', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      BillingMode: 'PAY_PER_REQUEST',
      KeySchema: [
        {
          AttributeName: 'id',
          KeyType: 'HASH',
        },
      ],
    });
  });

  test('S3 Bucket Created with Versioning', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      VersioningConfiguration: {
        Status: 'Enabled',
      },
    });
  });

  test('Lambda Function Has Required Environment Variables', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Environment: {
        Variables: Match.objectLike({
          TABLE_NAME: Match.anyValue(),
          BUCKET_NAME: Match.anyValue(),
        }),
      },
    });
  });

  test('API Gateway Created', () => {
    template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
  });

  test('Lambda Has DynamoDB Permissions', () => {
    template.hasResourceProperties('AWS::IAM::Policy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: Match.arrayWith([
              'dynamodb:BatchGetItem',
              'dynamodb:GetRecords',
              'dynamodb:GetItem',
              'dynamodb:Query',
              'dynamodb:Scan',
            ]),
          }),
        ]),
      },
    });
  });
});
```

### Running Tests

```bash
# Install dependencies
npm install --save-dev jest @types/jest ts-jest

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

---

## CDK Best Practices

```
┌─────────────────────────────────────────────────────────────────┐
│                   CDK Best Practices                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. USE L2 CONSTRUCTS                                           │
│     └── Prefer L2 over L1 for better defaults and APIs         │
│                                                                  │
│  2. CREATE CUSTOM CONSTRUCTS                                    │
│     └── Encapsulate patterns for reuse                          │
│                                                                  │
│  3. USE ASPECTS FOR COMPLIANCE                                  │
│     └── Enforce policies across all resources                   │
│                                                                  │
│  4. SEPARATE STACKS APPROPRIATELY                               │
│     └── Group by lifecycle and ownership                        │
│                                                                  │
│  5. PARAMETERIZE WITH CONTEXT                                   │
│     └── Use cdk.json and --context for configuration           │
│                                                                  │
│  6. WRITE TESTS                                                 │
│     └── Use assertion library for infrastructure tests          │
│                                                                  │
│  7. USE REMOVAL POLICIES CAREFULLY                              │
│     └── DESTROY for dev, RETAIN/SNAPSHOT for prod              │
│                                                                  │
│  8. VERSION YOUR CDK DEPENDENCIES                               │
│     └── Pin versions in package.json                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common CDK Commands Reference

```bash
# Initialize new project
cdk init app --language typescript
cdk init app --language python

# Bootstrap environment
cdk bootstrap
cdk bootstrap aws://ACCOUNT/REGION

# Synthesize template
cdk synth
cdk synth StackName

# View differences
cdk diff
cdk diff StackName

# Deploy stacks
cdk deploy
cdk deploy StackName
cdk deploy --all
cdk deploy --require-approval never

# Destroy stacks
cdk destroy
cdk destroy StackName
cdk destroy --all

# List stacks
cdk list

# Watch for changes (hot reloading)
cdk watch

# Import existing resources
cdk import StackName

# View generated CloudFormation
cat cdk.out/StackName.template.json
```

---

## Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      CDK Summary                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  What is CDK?                                                   │
│  ├── Framework for defining infrastructure in code             │
│  ├── Supports TypeScript, Python, Java, C#, Go                │
│  └── Synthesizes to CloudFormation                             │
│                                                                  │
│  Construct Levels:                                              │
│  ├── L1: Direct CloudFormation mapping                         │
│  ├── L2: AWS-curated with defaults                             │
│  └── L3: Complete patterns                                      │
│                                                                  │
│  Key Commands:                                                  │
│  ├── cdk init: Create project                                  │
│  ├── cdk synth: Generate template                              │
│  ├── cdk deploy: Deploy stack                                  │
│  └── cdk destroy: Delete stack                                 │
│                                                                  │
│  Benefits:                                                      │
│  ├── IDE support and type safety                               │
│  ├── Reusable constructs                                        │
│  ├── Standard testing frameworks                                │
│  └── Familiar programming patterns                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Practice**: Build a CDK project in your preferred language
2. **Explore**: CDK Construct Hub for community constructs
3. **Learn**: Production templates and patterns

---

**Next:** [Lesson 10 - Template Examples](./10-template-examples.md)
