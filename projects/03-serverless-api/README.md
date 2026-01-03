# Project 3: Build a Serverless REST API

## Project Overview

Build a fully serverless REST API using AWS Lambda, API Gateway, and DynamoDB. This project demonstrates the power of serverless architecture for building scalable, cost-effective applications.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SERVERLESS API ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│     Client Apps                                                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐                                                     │
│  │ Web  │ │Mobile│ │ CLI  │                                                     │
│  └──┬───┘ └──┬───┘ └──┬───┘                                                     │
│     │        │        │                                                          │
│     └────────┼────────┘                                                          │
│              │                                                                   │
│              ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        API GATEWAY                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  /items                                                          │    │   │
│  │  │  ├── GET    → List all items                                     │    │   │
│  │  │  ├── POST   → Create item                                        │    │   │
│  │  │  │                                                               │    │   │
│  │  │  /items/{id}                                                     │    │   │
│  │  │  ├── GET    → Get single item                                    │    │   │
│  │  │  ├── PUT    → Update item                                        │    │   │
│  │  │  └── DELETE → Delete item                                        │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│              ┌────────────────────┼────────────────────┐                       │
│              │                    │                    │                       │
│              ▼                    ▼                    ▼                       │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐            │
│  │  Lambda Function  │ │  Lambda Function  │ │  Lambda Function  │            │
│  │  (Create/Update)  │ │     (Read)        │ │    (Delete)       │            │
│  └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘            │
│            │                     │                     │                       │
│            └─────────────────────┼─────────────────────┘                       │
│                                  │                                              │
│                                  ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          DYNAMODB                                        │   │
│  │  ┌────────────────────────────────────────────────────────────────┐     │   │
│  │  │  Table: Items                                                   │     │   │
│  │  │  Partition Key: id (String)                                     │     │   │
│  │  │  Attributes: name, description, price, createdAt, updatedAt     │     │   │
│  │  └────────────────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Learning Objectives

By completing this project, you will:

- [ ] Create Lambda functions in Python
- [ ] Configure API Gateway REST API
- [ ] Design DynamoDB tables
- [ ] Implement CRUD operations
- [ ] Set up proper IAM permissions
- [ ] Use SAM for deployment
- [ ] Implement error handling and validation
- [ ] Add API authentication with API keys

---

## Prerequisites

- Completed Modules 1-7 of this course
- AWS Account with Free Tier
- Python 3.9+ installed locally
- AWS SAM CLI installed

---

## Estimated Time

| Phase | Time |
|-------|------|
| Project Setup | 15 minutes |
| Lambda Functions | 45 minutes |
| DynamoDB Table | 15 minutes |
| API Gateway | 30 minutes |
| Testing | 30 minutes |
| **Total** | **~2.5 hours** |

---

## Step 1: Project Setup

### Initialize SAM Project

```bash
# Create project directory
mkdir serverless-api
cd serverless-api

# Create directory structure
mkdir -p src/{handlers,utils}
touch src/__init__.py src/handlers/__init__.py src/utils/__init__.py
```

### SAM Template (template.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Serverless REST API with Lambda and DynamoDB

Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
    MemorySize: 256
    Environment:
      Variables:
        TABLE_NAME: !Ref ItemsTable
        LOG_LEVEL: INFO
    Tracing: Active

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  # DynamoDB Table
  ItemsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub items-${Environment}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Lambda Functions
  CreateItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub create-item-${Environment}
      Handler: src/handlers/create.handler
      CodeUri: .
      Description: Create a new item
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
      Events:
        CreateItem:
          Type: Api
          Properties:
            RestApiId: !Ref ItemsApi
            Path: /items
            Method: POST

  GetItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub get-item-${Environment}
      Handler: src/handlers/get.handler
      CodeUri: .
      Description: Get a single item by ID
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref ItemsTable
      Events:
        GetItem:
          Type: Api
          Properties:
            RestApiId: !Ref ItemsApi
            Path: /items/{id}
            Method: GET

  ListItemsFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub list-items-${Environment}
      Handler: src/handlers/list.handler
      CodeUri: .
      Description: List all items
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref ItemsTable
      Events:
        ListItems:
          Type: Api
          Properties:
            RestApiId: !Ref ItemsApi
            Path: /items
            Method: GET

  UpdateItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub update-item-${Environment}
      Handler: src/handlers/update.handler
      CodeUri: .
      Description: Update an existing item
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
      Events:
        UpdateItem:
          Type: Api
          Properties:
            RestApiId: !Ref ItemsApi
            Path: /items/{id}
            Method: PUT

  DeleteItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub delete-item-${Environment}
      Handler: src/handlers/delete.handler
      CodeUri: .
      Description: Delete an item
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
      Events:
        DeleteItem:
          Type: Api
          Properties:
            RestApiId: !Ref ItemsApi
            Path: /items/{id}
            Method: DELETE

  # API Gateway
  ItemsApi:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub items-api-${Environment}
      StageName: !Ref Environment
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key'"
        AllowOrigin: "'*'"
      Auth:
        ApiKeyRequired: false  # Set to true to require API key

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub https://${ItemsApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}

  TableName:
    Description: DynamoDB table name
    Value: !Ref ItemsTable
```

---

## Step 2: Create Lambda Functions

### Utility Module (src/utils/response.py)

```python
import json
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def build_response(status_code: int, body: dict = None, message: str = None):
    """Build a standardized API response."""
    response_body = {}

    if body is not None:
        response_body = body
    elif message is not None:
        response_body = {"message": message}

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(response_body, cls=DecimalEncoder)
    }


def success(body: dict = None, message: str = None):
    """Return a 200 success response."""
    return build_response(200, body, message)


def created(body: dict):
    """Return a 201 created response."""
    return build_response(201, body)


def bad_request(message: str = "Bad Request"):
    """Return a 400 bad request response."""
    return build_response(400, message=message)


def not_found(message: str = "Resource not found"):
    """Return a 404 not found response."""
    return build_response(404, message=message)


def internal_error(message: str = "Internal server error"):
    """Return a 500 internal server error response."""
    return build_response(500, message=message)
```

### DynamoDB Helper (src/utils/dynamodb.py)

```python
import os
import boto3
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'items-dev')
table = dynamodb.Table(table_name)


def get_item(item_id: str) -> dict:
    """Get a single item by ID."""
    response = table.get_item(Key={'id': item_id})
    return response.get('Item')


def list_items(limit: int = 100) -> list:
    """List all items with optional limit."""
    response = table.scan(Limit=limit)
    return response.get('Items', [])


def create_item(item: dict) -> dict:
    """Create a new item."""
    table.put_item(Item=item)
    return item


def update_item(item_id: str, updates: dict) -> dict:
    """Update an existing item."""
    # Build update expression
    update_expression = "SET "
    expression_values = {}
    expression_names = {}

    for key, value in updates.items():
        if key != 'id':  # Don't update the primary key
            update_expression += f"#{key} = :{key}, "
            expression_values[f":{key}"] = value
            expression_names[f"#{key}"] = key

    # Remove trailing comma and space
    update_expression = update_expression.rstrip(', ')

    response = table.update_item(
        Key={'id': item_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ExpressionAttributeNames=expression_names,
        ReturnValues="ALL_NEW"
    )

    return response.get('Attributes')


def delete_item(item_id: str) -> bool:
    """Delete an item by ID."""
    table.delete_item(Key={'id': item_id})
    return True
```

### Create Handler (src/handlers/create.py)

```python
import json
import uuid
from datetime import datetime
import logging

from src.utils.response import created, bad_request, internal_error
from src.utils.dynamodb import create_item

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_item(data: dict) -> tuple:
    """Validate item data. Returns (is_valid, error_message)."""
    required_fields = ['name']

    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"

    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                return False, "Price cannot be negative"
        except (ValueError, TypeError):
            return False, "Price must be a valid number"

    return True, None


def handler(event, context):
    """Create a new item."""
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))

        # Validate input
        is_valid, error_message = validate_item(body)
        if not is_valid:
            return bad_request(error_message)

        # Create item with generated ID and timestamps
        timestamp = datetime.utcnow().isoformat()
        item = {
            'id': str(uuid.uuid4()),
            'name': body['name'],
            'description': body.get('description', ''),
            'price': float(body.get('price', 0)),
            'category': body.get('category', 'uncategorized'),
            'createdAt': timestamp,
            'updatedAt': timestamp
        }

        # Save to DynamoDB
        created_item = create_item(item)

        logger.info(f"Created item: {created_item['id']}")

        return created({
            "message": "Item created successfully",
            "item": created_item
        })

    except json.JSONDecodeError:
        return bad_request("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        return internal_error(str(e))
```

### Get Handler (src/handlers/get.py)

```python
import json
import logging

from src.utils.response import success, not_found, bad_request, internal_error
from src.utils.dynamodb import get_item

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Get a single item by ID."""
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Get item ID from path parameters
        path_params = event.get('pathParameters', {}) or {}
        item_id = path_params.get('id')

        if not item_id:
            return bad_request("Item ID is required")

        # Fetch from DynamoDB
        item = get_item(item_id)

        if not item:
            return not_found(f"Item with ID '{item_id}' not found")

        return success({"item": item})

    except Exception as e:
        logger.error(f"Error getting item: {str(e)}")
        return internal_error(str(e))
```

### List Handler (src/handlers/list.py)

```python
import json
import logging

from src.utils.response import success, internal_error
from src.utils.dynamodb import list_items

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """List all items."""
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Get optional query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        limit = int(query_params.get('limit', 100))

        # Ensure limit is reasonable
        limit = min(max(1, limit), 1000)

        # Fetch items from DynamoDB
        items = list_items(limit=limit)

        return success({
            "items": items,
            "count": len(items)
        })

    except Exception as e:
        logger.error(f"Error listing items: {str(e)}")
        return internal_error(str(e))
```

### Update Handler (src/handlers/update.py)

```python
import json
from datetime import datetime
import logging

from src.utils.response import success, not_found, bad_request, internal_error
from src.utils.dynamodb import get_item, update_item

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Update an existing item."""
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Get item ID from path parameters
        path_params = event.get('pathParameters', {}) or {}
        item_id = path_params.get('id')

        if not item_id:
            return bad_request("Item ID is required")

        # Check if item exists
        existing_item = get_item(item_id)
        if not existing_item:
            return not_found(f"Item with ID '{item_id}' not found")

        # Parse request body
        body = json.loads(event.get('body', '{}'))

        if not body:
            return bad_request("Request body cannot be empty")

        # Prepare updates
        allowed_fields = ['name', 'description', 'price', 'category']
        updates = {}

        for field in allowed_fields:
            if field in body:
                if field == 'price':
                    updates[field] = float(body[field])
                else:
                    updates[field] = body[field]

        if not updates:
            return bad_request("No valid fields to update")

        # Add updated timestamp
        updates['updatedAt'] = datetime.utcnow().isoformat()

        # Update in DynamoDB
        updated_item = update_item(item_id, updates)

        logger.info(f"Updated item: {item_id}")

        return success({
            "message": "Item updated successfully",
            "item": updated_item
        })

    except json.JSONDecodeError:
        return bad_request("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        return internal_error(str(e))
```

### Delete Handler (src/handlers/delete.py)

```python
import json
import logging

from src.utils.response import success, not_found, bad_request, internal_error
from src.utils.dynamodb import get_item, delete_item

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Delete an item by ID."""
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Get item ID from path parameters
        path_params = event.get('pathParameters', {}) or {}
        item_id = path_params.get('id')

        if not item_id:
            return bad_request("Item ID is required")

        # Check if item exists
        existing_item = get_item(item_id)
        if not existing_item:
            return not_found(f"Item with ID '{item_id}' not found")

        # Delete from DynamoDB
        delete_item(item_id)

        logger.info(f"Deleted item: {item_id}")

        return success({
            "message": f"Item '{item_id}' deleted successfully"
        })

    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        return internal_error(str(e))
```

---

## Step 3: Deploy with SAM

```bash
# Build the application
sam build

# Deploy (first time - guided)
sam deploy --guided

# For subsequent deploys
sam deploy

# View deployed resources
aws cloudformation describe-stacks \
    --stack-name serverless-api \
    --query 'Stacks[0].Outputs'
```

---

## Step 4: Test the API

### Using cURL

```bash
# Set your API endpoint
API_URL="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev"

# Create an item
curl -X POST $API_URL/items \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Laptop",
        "description": "High-performance laptop",
        "price": 999.99,
        "category": "electronics"
    }'

# List all items
curl $API_URL/items

# Get a specific item (replace with actual ID)
curl $API_URL/items/your-item-id

# Update an item
curl -X PUT $API_URL/items/your-item-id \
    -H "Content-Type: application/json" \
    -d '{
        "price": 899.99,
        "description": "Updated description"
    }'

# Delete an item
curl -X DELETE $API_URL/items/your-item-id
```

### Using Python

```python
import requests
import json

API_URL = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev"

# Create item
response = requests.post(
    f"{API_URL}/items",
    json={
        "name": "Headphones",
        "description": "Wireless noise-canceling headphones",
        "price": 299.99,
        "category": "electronics"
    }
)
print("Create:", response.json())

# List items
response = requests.get(f"{API_URL}/items")
print("List:", response.json())

# Get item
item_id = response.json()['items'][0]['id']
response = requests.get(f"{API_URL}/items/{item_id}")
print("Get:", response.json())

# Update item
response = requests.put(
    f"{API_URL}/items/{item_id}",
    json={"price": 249.99}
)
print("Update:", response.json())

# Delete item
response = requests.delete(f"{API_URL}/items/{item_id}")
print("Delete:", response.json())
```

---

## Step 5: Local Testing with SAM

```bash
# Start local API
sam local start-api

# In another terminal, test locally
curl http://localhost:3000/items

# Invoke function directly
sam local invoke CreateItemFunction \
    --event events/create-event.json
```

### Sample Event (events/create-event.json)

```json
{
    "body": "{\"name\": \"Test Item\", \"price\": 19.99}",
    "resource": "/items",
    "path": "/items",
    "httpMethod": "POST",
    "headers": {
        "Content-Type": "application/json"
    }
}
```

---

## Cost Breakdown

| Service | Monthly Cost (Estimate) |
|---------|------------------------|
| Lambda (1M requests) | Free Tier |
| API Gateway (1M requests) | ~$3.50 |
| DynamoDB (on-demand) | Free Tier |
| **Total** | **~$3.50/month** |

---

## Cleanup

```bash
# Delete the SAM stack
sam delete --stack-name serverless-api

# Or using CloudFormation
aws cloudformation delete-stack --stack-name serverless-api
```

---

## Verification Checklist

- [ ] SAM template validates successfully
- [ ] All Lambda functions deploy correctly
- [ ] API Gateway endpoints respond
- [ ] DynamoDB table created
- [ ] Create item works
- [ ] List items works
- [ ] Get single item works
- [ ] Update item works
- [ ] Delete item works
- [ ] Error handling works correctly

---

## Stretch Goals

1. **Add authentication** - Implement Cognito user pools
2. **Add pagination** - Use DynamoDB pagination tokens
3. **Add search** - Implement DynamoDB GSI for querying
4. **Add caching** - Use API Gateway caching or DAX
5. **Add CI/CD** - Deploy with GitHub Actions

---

**Congratulations!** You've built a production-ready serverless API!

[← Back to Projects](../) | [Previous: Web Application](../02-web-application/) | [Next: Data Pipeline →](../04-data-pipeline/)
