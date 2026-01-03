# Amazon API Gateway

## Introduction

Amazon API Gateway is a fully managed service for creating, publishing, maintaining, monitoring, and securing APIs at any scale. It handles all the tasks involved in accepting and processing up to hundreds of thousands of concurrent API calls.

## API Gateway Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY TYPES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │    REST API     │  │    HTTP API     │  │  WebSocket API  │  │
│  │                 │  │                 │  │                 │  │
│  │ • Full features │  │ • Low latency   │  │ • Real-time     │  │
│  │ • API keys      │  │ • Lower cost    │  │ • Two-way comm  │  │
│  │ • Usage plans   │  │ • OIDC/OAuth2   │  │ • Chat/Gaming   │  │
│  │ • Caching       │  │ • Simpler       │  │ • Notifications │  │
│  │ • Transformations│ │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Comparison

| Feature | REST API | HTTP API | WebSocket API |
|---------|----------|----------|---------------|
| Cost | Higher | 70% cheaper | Per message |
| Latency | Higher | Lower | Real-time |
| Caching | Yes | No | No |
| API Keys | Yes | No | No |
| Usage Plans | Yes | No | No |
| Request Validation | Yes | No | No |
| WAF Integration | Yes | No | No |
| Private Endpoints | Yes | Yes | No |
| Lambda Integration | Proxy/Non-proxy | Proxy only | Custom |
| JWT Authorization | Custom | Built-in | Custom |

## REST API

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      REST API ARCHITECTURE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Client Request                                                   │
│       │                                                           │
│       ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     API GATEWAY                              │ │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │ │
│  │  │  Method   │─▶│  Request  │─▶│Integration│─▶│ Lambda/  │  │ │
│  │  │  Request  │  │  Mapping  │  │  Request  │  │  Backend │  │ │
│  │  └───────────┘  └───────────┘  └───────────┘  └──────────┘  │ │
│  │       │              │              │              │         │ │
│  │       ▼              ▼              ▼              ▼         │ │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │ │
│  │  │  Method   │◀─│  Response │◀─│Integration│◀─│ Backend  │  │ │
│  │  │  Response │  │  Mapping  │  │  Response │  │ Response │  │ │
│  │  └───────────┘  └───────────┘  └───────────┘  └──────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│       │                                                           │
│       ▼                                                           │
│  Client Response                                                  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Creating REST API

```bash
# Create REST API
aws apigateway create-rest-api \
    --name "users-api" \
    --description "Users REST API" \
    --endpoint-configuration types=REGIONAL

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[?path==`/`].id' \
    --output text)

# Create /users resource
aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part users

# Create GET method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE

# Set up Lambda integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:get-users/invocations"
```

### Lambda Proxy Integration

With proxy integration, API Gateway sends the entire request to Lambda and expects a specific response format.

**Request format sent to Lambda:**

```json
{
  "resource": "/users/{userId}",
  "path": "/users/123",
  "httpMethod": "GET",
  "headers": {
    "Content-Type": "application/json"
  },
  "queryStringParameters": {
    "include": "orders"
  },
  "pathParameters": {
    "userId": "123"
  },
  "body": null,
  "isBase64Encoded": false,
  "requestContext": {
    "accountId": "123456789012",
    "stage": "prod",
    "requestId": "abc-123"
  }
}
```

**Required response format from Lambda:**

```python
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'userId': '123',
            'name': 'John Doe'
        }),
        'isBase64Encoded': False
    }
```

### SAM Template for REST API

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  UsersApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: users-api
      StageName: prod
      Description: Users REST API
      EndpointConfiguration:
        Type: REGIONAL
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"

  GetUsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.12
      CodeUri: src/
      Events:
        GetUsers:
          Type: Api
          Properties:
            RestApiId: !Ref UsersApi
            Path: /users
            Method: GET
        GetUser:
          Type: Api
          Properties:
            RestApiId: !Ref UsersApi
            Path: /users/{userId}
            Method: GET

  CreateUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: create.handler
      Runtime: python3.12
      CodeUri: src/
      Events:
        CreateUser:
          Type: Api
          Properties:
            RestApiId: !Ref UsersApi
            Path: /users
            Method: POST

Outputs:
  ApiEndpoint:
    Value: !Sub "https://${UsersApi}.execute-api.${AWS::Region}.amazonaws.com/prod"
```

## HTTP API

HTTP APIs are optimized for building APIs that proxy to Lambda functions or HTTP backends.

### Creating HTTP API

```bash
# Create HTTP API
aws apigatewayv2 create-api \
    --name "users-http-api" \
    --protocol-type HTTP \
    --cors-configuration '{
        "AllowOrigins": ["*"],
        "AllowMethods": ["GET", "POST", "PUT", "DELETE"],
        "AllowHeaders": ["Content-Type", "Authorization"]
    }'

# Create Lambda integration
aws apigatewayv2 create-integration \
    --api-id $API_ID \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:us-east-1:123456789012:function:my-function" \
    --payload-format-version "2.0"

# Create route
aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key "GET /users" \
    --target "integrations/$INTEGRATION_ID"

# Create stage
aws apigatewayv2 create-stage \
    --api-id $API_ID \
    --stage-name prod \
    --auto-deploy
```

### HTTP API Event Format (v2.0)

```json
{
  "version": "2.0",
  "routeKey": "GET /users/{userId}",
  "rawPath": "/users/123",
  "rawQueryString": "include=orders",
  "headers": {
    "content-type": "application/json"
  },
  "queryStringParameters": {
    "include": "orders"
  },
  "pathParameters": {
    "userId": "123"
  },
  "requestContext": {
    "accountId": "123456789012",
    "apiId": "abc123",
    "domainName": "abc123.execute-api.us-east-1.amazonaws.com",
    "http": {
      "method": "GET",
      "path": "/users/123",
      "protocol": "HTTP/1.1",
      "sourceIp": "192.168.1.1",
      "userAgent": "Mozilla/5.0"
    },
    "requestId": "request-id-123",
    "stage": "prod",
    "time": "15/Jan/2024:12:00:00 +0000"
  },
  "body": null,
  "isBase64Encoded": false
}
```

### SAM Template for HTTP API

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  HttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: prod
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
          - "*"

  UsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.12
      CodeUri: src/
      Events:
        GetUsers:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /users
            Method: GET
        GetUser:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /users/{userId}
            Method: GET
        CreateUser:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Path: /users
            Method: POST
```

## WebSocket API

WebSocket APIs enable two-way, real-time communication between clients and servers.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEBSOCKET API FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│     Client                 API Gateway              Lambda       │
│       │                         │                      │         │
│       │──$connect──────────────▶│─────────────────────▶│         │
│       │                         │                      │         │
│       │◀───Connection ID────────│◀─────────────────────│         │
│       │                         │   Store connection   │         │
│       │                         │                      │         │
│       │──Send Message──────────▶│─────────────────────▶│         │
│       │                         │                      │         │
│       │                         │◀────Process──────────│         │
│       │                         │                      │         │
│       │◀──Push Message──────────│◀─────────────────────│         │
│       │                         │                      │         │
│       │──$disconnect───────────▶│─────────────────────▶│         │
│       │                         │   Remove connection  │         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Routes

| Route | Description |
|-------|-------------|
| `$connect` | Called when client connects |
| `$disconnect` | Called when client disconnects |
| `$default` | Fallback for unmatched routes |
| Custom routes | Your defined message routes |

### Creating WebSocket API

```bash
# Create WebSocket API
aws apigatewayv2 create-api \
    --name "chat-api" \
    --protocol-type WEBSOCKET \
    --route-selection-expression '$request.body.action'

# Create $connect route integration
aws apigatewayv2 create-integration \
    --api-id $API_ID \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:us-east-1:123456789012:function:connect-handler"

aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key '$connect' \
    --target "integrations/$INTEGRATION_ID"
```

### WebSocket Handler Example

```python
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table('websocket-connections')


def connect_handler(event, context):
    """Handle new WebSocket connection"""
    connection_id = event['requestContext']['connectionId']

    # Store connection
    connections_table.put_item(Item={
        'connectionId': connection_id,
        'timestamp': int(time.time())
    })

    logger.info(f"Connected: {connection_id}")

    return {'statusCode': 200}


def disconnect_handler(event, context):
    """Handle WebSocket disconnection"""
    connection_id = event['requestContext']['connectionId']

    # Remove connection
    connections_table.delete_item(Key={
        'connectionId': connection_id
    })

    logger.info(f"Disconnected: {connection_id}")

    return {'statusCode': 200}


def message_handler(event, context):
    """Handle incoming messages"""
    connection_id = event['requestContext']['connectionId']
    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']

    # Parse message
    body = json.loads(event.get('body', '{}'))
    action = body.get('action')
    message = body.get('message')

    logger.info(f"Message from {connection_id}: {message}")

    # Broadcast to all connections
    endpoint_url = f"https://{domain}/{stage}"
    api_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)

    # Get all connections
    connections = connections_table.scan()['Items']

    for connection in connections:
        target_id = connection['connectionId']
        try:
            api_client.post_to_connection(
                ConnectionId=target_id,
                Data=json.dumps({
                    'from': connection_id,
                    'message': message
                }).encode()
            )
        except api_client.exceptions.GoneException:
            # Connection no longer exists
            connections_table.delete_item(Key={'connectionId': target_id})

    return {'statusCode': 200}
```

### SAM Template for WebSocket API

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  WebSocketApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: chat-websocket-api
      ProtocolType: WEBSOCKET
      RouteSelectionExpression: '$request.body.action'

  ConnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: $connect
      Target: !Sub integrations/${ConnectIntegration}

  ConnectIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref WebSocketApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ConnectFunction.Arn}/invocations

  ConnectFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: websocket.connect_handler
      Runtime: python3.12
      CodeUri: src/
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ConnectionsTable

  ConnectionsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: websocket-connections
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: connectionId
          AttributeType: S
      KeySchema:
        - AttributeName: connectionId
          KeyType: HASH
```

## Stages and Deployments

### Stage Variables

```bash
# Create stage with variables
aws apigateway create-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --deployment-id $DEPLOYMENT_ID \
    --variables '{
        "lambdaAlias": "prod",
        "tableName": "users-prod"
    }'

# Update stage variables
aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --patch-operations op=replace,path=/variables/lambdaAlias,value=v2
```

### Using Stage Variables in Lambda Integration

```
arn:aws:lambda:us-east-1:123456789012:function:my-function:${stageVariables.lambdaAlias}
```

### Deployment

```bash
# Create deployment
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --description "Version 1.0"
```

## Authentication and Authorization

### API Keys and Usage Plans

```bash
# Create API key
aws apigateway create-api-key \
    --name "customer-key" \
    --enabled

# Create usage plan
aws apigateway create-usage-plan \
    --name "basic-plan" \
    --throttle burstLimit=100,rateLimit=50 \
    --quota limit=1000,period=MONTH \
    --api-stages apiId=$API_ID,stage=prod

# Associate API key with usage plan
aws apigateway create-usage-plan-key \
    --usage-plan-id $PLAN_ID \
    --key-id $KEY_ID \
    --key-type API_KEY
```

### Lambda Authorizer

```python
# Lambda authorizer for REST API
def authorizer(event, context):
    """Custom Lambda authorizer"""
    token = event.get('authorizationToken', '')
    method_arn = event['methodArn']

    # Validate token
    if validate_token(token):
        principal_id = extract_user_id(token)
        return generate_policy(principal_id, 'Allow', method_arn)
    else:
        return generate_policy('user', 'Deny', method_arn)


def generate_policy(principal_id, effect, resource):
    """Generate IAM policy"""
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        },
        'context': {
            'userId': principal_id,
            'scope': 'read:users'
        }
    }


def validate_token(token):
    """Validate JWT token"""
    import jwt
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.InvalidTokenError:
        return False


def extract_user_id(token):
    """Extract user ID from token"""
    import jwt
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return payload.get('sub')
```

### Cognito Authorizer

```yaml
# SAM template with Cognito authorizer
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn

  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: my-user-pool
      AutoVerifiedAttributes:
        - email
```

### JWT Authorizer (HTTP API)

```yaml
Resources:
  HttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
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
```

## Throttling and Quotas

### Throttling Settings

```
┌─────────────────────────────────────────────────────────────────┐
│                    THROTTLING HIERARCHY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Account Level (10,000 RPS default)                              │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Usage Plan (e.g., 1,000 RPS)                                ││
│  │     │                                                       ││
│  │     ▼                                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ API/Stage (e.g., 500 RPS)                               │ ││
│  │ │     │                                                   │ ││
│  │ │     ▼                                                   │ ││
│  │ │ ┌─────────────────────────────────────────────────────┐ │ ││
│  │ │ │ Method (e.g., GET /users: 100 RPS)                  │ │ ││
│  │ │ └─────────────────────────────────────────────────────┘ │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Configure Throttling

```bash
# Stage-level throttling
aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/throttling/rateLimit,value=1000 \
        op=replace,path=/throttling/burstLimit,value=2000

# Method-level throttling
aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --patch-operations \
        'op=replace,path=/~1users/GET/throttling/rateLimit,value=100'
```

## Caching (REST API)

### Enable Caching

```bash
# Enable caching for stage
aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --patch-operations \
        op=replace,path=/cacheClusterEnabled,value=true \
        op=replace,path=/cacheClusterSize,value=0.5

# Configure method caching
aws apigateway update-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --patch-operations \
        op=replace,path=/cachingEnabled,value=true \
        op=replace,path=/cacheDataEncrypted,value=true \
        op=replace,path=/cacheTtlInSeconds,value=300
```

### Cache Key Parameters

```yaml
# SAM template with cache key
GetUsersFunction:
  Type: AWS::Serverless::Function
  Properties:
    Events:
      GetUsers:
        Type: Api
        Properties:
          Path: /users
          Method: GET
          RestApiId: !Ref MyApi
          RequestParameters:
            - method.request.querystring.filter:
                Required: true
                Caching: true
```

## CORS Configuration

### REST API CORS

```bash
# Add OPTIONS method for CORS
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE

# Set up mock integration
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}'

# Configure response headers
aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{
        "method.response.header.Access-Control-Allow-Headers": "'\''Content-Type,Authorization'\''",
        "method.response.header.Access-Control-Allow-Methods": "'\''GET,POST,PUT,DELETE,OPTIONS'\''",
        "method.response.header.Access-Control-Allow-Origin": "'\''*'\''"
    }'
```

### HTTP API CORS

```yaml
# SAM template
HttpApi:
  Type: AWS::Serverless::HttpApi
  Properties:
    CorsConfiguration:
      AllowMethods:
        - GET
        - POST
        - PUT
        - DELETE
        - OPTIONS
      AllowHeaders:
        - Content-Type
        - Authorization
        - X-Requested-With
      AllowOrigins:
        - https://example.com
        - https://app.example.com
      AllowCredentials: true
      MaxAge: 86400
```

## Request/Response Transformation (REST API)

### Request Mapping Template

```velocity
## Transform incoming request
#set($inputRoot = $input.path('$'))
{
    "userId": "$input.params('userId')",
    "queryParams": {
        #foreach($param in $input.params().querystring.keySet())
        "$param": "$input.params().querystring.get($param)"
        #if($foreach.hasNext),#end
        #end
    },
    "headers": {
        "authorization": "$input.params('Authorization')",
        "contentType": "$input.params('Content-Type')"
    },
    "body": $input.json('$')
}
```

### Response Mapping Template

```velocity
## Transform response
#set($inputRoot = $input.path('$'))
{
    "data": $input.json('$.items'),
    "metadata": {
        "count": $input.json('$.count'),
        "page": $input.json('$.page')
    },
    "links": {
        "self": "$context.domainName$context.path"
    }
}
```

## Summary

### API Gateway Selection Guide

| Use Case | Recommended |
|----------|-------------|
| Full-featured REST API | REST API |
| Simple Lambda proxy | HTTP API |
| Cost optimization | HTTP API |
| Real-time communication | WebSocket API |
| Complex transformations | REST API |
| JWT/OIDC auth | HTTP API |
| API keys/Usage plans | REST API |
| Response caching | REST API |

### Best Practices

1. **Use HTTP API for simple Lambda proxies** (70% cost savings)
2. **Enable caching for GET endpoints** (REST API)
3. **Implement proper CORS configuration**
4. **Use custom domain names for production**
5. **Set appropriate throttling limits**
6. **Use Lambda authorizers for custom auth**
7. **Monitor with CloudWatch and X-Ray**

### Next Steps

Continue to [07-step-functions.md](./07-step-functions.md) to learn about orchestrating serverless workflows with AWS Step Functions.
