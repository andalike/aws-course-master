# Serverless REST API - Complete Implementation Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [API Design](#api-design)
4. [DynamoDB Setup](#dynamodb-setup)
5. [Lambda Functions](#lambda-functions)
6. [API Gateway Configuration](#api-gateway-configuration)
7. [Cognito Authentication](#cognito-authentication)
8. [SAM Template](#sam-template)
9. [Testing Instructions](#testing-instructions)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Cost Analysis](#cost-analysis)
12. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
                         SERVERLESS API ARCHITECTURE
    ==================================================================================

                                   INTERNET
                                       |
                                       v
                          +------------------------+
                          |       Route 53         |
                          |    api.example.com     |
                          +------------------------+
                                       |
                                       v
                          +------------------------+
                          |    API Gateway         |
                          |  (REST API / HTTP API) |
                          +----------+-------------+
                                     |
                    +----------------+----------------+
                    |                |                |
                    v                v                v
            +-----------+    +-----------+    +-----------+
            |  Cognito  |    |  Lambda   |    |    WAF    |
            | User Pool |    | Authorizer|    | (Optional)|
            +-----------+    +-----------+    +-----------+
                                     |
                    +----------------+----------------+
                    |                |                |
                    v                v                v
            +-----------+    +-----------+    +-----------+
            |  Lambda   |    |  Lambda   |    |  Lambda   |
            | (Create)  |    |  (Read)   |    | (Update)  |
            +-----------+    +-----------+    +-----------+
                    |                |                |
                    +----------------+----------------+
                                     |
                                     v
                          +------------------------+
                          |       DynamoDB         |
                          |    (Items Table)       |
                          +------------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
            +-----------+                    +-----------+
            | CloudWatch|                    |   X-Ray   |
            |   Logs    |                    |  Tracing  |
            +-----------+                    +-----------+

    FLOW:
    1. Client authenticates with Cognito
    2. Client sends request to API Gateway with JWT token
    3. API Gateway validates token with Lambda Authorizer
    4. Request routed to appropriate Lambda function
    5. Lambda processes request and interacts with DynamoDB
    6. Response returned to client

    COMPONENTS:
    +------------------+--------------------------------------------+
    | API Gateway      | RESTful API endpoints with throttling      |
    | Lambda           | Serverless compute for business logic      |
    | DynamoDB         | NoSQL database with on-demand scaling      |
    | Cognito          | User authentication and authorization      |
    | CloudWatch       | Logging and monitoring                     |
    | X-Ray            | Distributed tracing                        |
    +------------------+--------------------------------------------+
```

---

## Prerequisites

### Required Tools

```bash
# AWS CLI v2
aws --version

# AWS SAM CLI
sam --version

# Python 3.9+
python3 --version

# Node.js (for testing)
node --version

# Verify AWS credentials
aws sts get-caller-identity
```

### Environment Setup

```bash
# Set environment variables
export AWS_REGION="us-east-1"
export PROJECT_NAME="serverless-api"
export STAGE="dev"

# Create project directory
mkdir -p ${PROJECT_NAME}
cd ${PROJECT_NAME}
```

---

## API Design

### RESTful Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /items | Create new item | Yes |
| GET | /items | List all items | Yes |
| GET | /items/{id} | Get single item | Yes |
| PUT | /items/{id} | Update item | Yes |
| DELETE | /items/{id} | Delete item | Yes |
| GET | /health | Health check | No |

### Request/Response Format

```json
// POST /items - Create Item
// Request
{
    "name": "Sample Item",
    "description": "Item description",
    "price": 29.99,
    "category": "electronics"
}

// Response (201 Created)
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Sample Item",
    "description": "Item description",
    "price": 29.99,
    "category": "electronics",
    "createdAt": "2026-01-03T12:00:00Z",
    "updatedAt": "2026-01-03T12:00:00Z"
}

// Error Response
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Name is required",
        "details": [...]
    }
}
```

---

## DynamoDB Setup

### Create DynamoDB Table

```bash
# Create table with on-demand capacity
aws dynamodb create-table \
    --table-name ${PROJECT_NAME}-items \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
        AttributeName=GSI1PK,AttributeType=S \
        AttributeName=GSI1SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --global-secondary-indexes \
        '[
            {
                "IndexName": "GSI1",
                "KeySchema": [
                    {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                    {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"}
            }
        ]' \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Project,Value=${PROJECT_NAME}

# Wait for table to be active
aws dynamodb wait table-exists --table-name ${PROJECT_NAME}-items
```

### DynamoDB Data Model

```
Table: serverless-api-items

Primary Key:
  PK (Partition Key): ITEM#<item-id>
  SK (Sort Key): METADATA

GSI1:
  GSI1PK: CATEGORY#<category>
  GSI1SK: <created-at>#<item-id>

Attributes:
  - id: String (UUID)
  - name: String
  - description: String
  - price: Number
  - category: String
  - userId: String
  - createdAt: String (ISO 8601)
  - updatedAt: String (ISO 8601)
```

---

## Lambda Functions

### Project Structure

```
serverless-api/
├── src/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── create_item.py
│   │   ├── get_item.py
│   │   ├── list_items.py
│   │   ├── update_item.py
│   │   ├── delete_item.py
│   │   └── health.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── dynamodb.py
│   │   ├── response.py
│   │   └── validators.py
│   └── __init__.py
├── tests/
│   ├── unit/
│   │   └── test_handlers.py
│   └── integration/
│       └── test_api.py
├── template.yaml
├── requirements.txt
└── samconfig.toml
```

### src/utils/dynamodb.py

```python
"""
DynamoDB utility functions for CRUD operations
"""
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime
import uuid
from typing import Dict, List, Optional, Any

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'serverless-api-items')
table = dynamodb.Table(table_name)


def generate_id() -> str:
    """Generate a unique UUID"""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current ISO 8601 timestamp"""
    return datetime.utcnow().isoformat() + 'Z'


def create_item(item_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Create a new item in DynamoDB

    Args:
        item_data: Item attributes
        user_id: ID of the user creating the item

    Returns:
        Created item with generated fields
    """
    item_id = generate_id()
    timestamp = get_timestamp()

    item = {
        'PK': f'ITEM#{item_id}',
        'SK': 'METADATA',
        'id': item_id,
        'name': item_data['name'],
        'description': item_data.get('description', ''),
        'price': item_data.get('price', 0),
        'category': item_data.get('category', 'general'),
        'userId': user_id,
        'createdAt': timestamp,
        'updatedAt': timestamp,
        'GSI1PK': f"CATEGORY#{item_data.get('category', 'general')}",
        'GSI1SK': f"{timestamp}#{item_id}"
    }

    table.put_item(Item=item)

    return {
        'id': item_id,
        'name': item['name'],
        'description': item['description'],
        'price': item['price'],
        'category': item['category'],
        'createdAt': timestamp,
        'updatedAt': timestamp
    }


def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single item by ID

    Args:
        item_id: The item's unique identifier

    Returns:
        Item data or None if not found
    """
    try:
        response = table.get_item(
            Key={
                'PK': f'ITEM#{item_id}',
                'SK': 'METADATA'
            }
        )

        item = response.get('Item')
        if not item:
            return None

        return {
            'id': item['id'],
            'name': item['name'],
            'description': item['description'],
            'price': float(item['price']),
            'category': item['category'],
            'createdAt': item['createdAt'],
            'updatedAt': item['updatedAt']
        }
    except ClientError as e:
        raise Exception(f"Error getting item: {e.response['Error']['Message']}")


def list_items(
    category: Optional[str] = None,
    limit: int = 20,
    last_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    List items with optional filtering and pagination

    Args:
        category: Filter by category
        limit: Maximum number of items to return
        last_key: Last evaluated key for pagination

    Returns:
        Dict with items and pagination info
    """
    try:
        scan_kwargs = {
            'Limit': limit,
            'FilterExpression': Attr('SK').eq('METADATA')
        }

        if category:
            # Use GSI for category queries
            scan_kwargs = {
                'IndexName': 'GSI1',
                'KeyConditionExpression': Key('GSI1PK').eq(f'CATEGORY#{category}'),
                'Limit': limit,
                'ScanIndexForward': False  # Newest first
            }

            if last_key:
                scan_kwargs['ExclusiveStartKey'] = {'GSI1SK': last_key}

            response = table.query(**scan_kwargs)
        else:
            if last_key:
                scan_kwargs['ExclusiveStartKey'] = {'PK': last_key, 'SK': 'METADATA'}

            response = table.scan(**scan_kwargs)

        items = [
            {
                'id': item['id'],
                'name': item['name'],
                'description': item['description'],
                'price': float(item['price']),
                'category': item['category'],
                'createdAt': item['createdAt'],
                'updatedAt': item['updatedAt']
            }
            for item in response.get('Items', [])
        ]

        result = {'items': items}

        if 'LastEvaluatedKey' in response:
            result['nextToken'] = response['LastEvaluatedKey'].get('GSI1SK') or response['LastEvaluatedKey'].get('PK')

        return result

    except ClientError as e:
        raise Exception(f"Error listing items: {e.response['Error']['Message']}")


def update_item(item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing item

    Args:
        item_id: The item's unique identifier
        updates: Fields to update

    Returns:
        Updated item or None if not found
    """
    # Build update expression
    update_parts = []
    expression_names = {}
    expression_values = {':updatedAt': get_timestamp()}

    for key, value in updates.items():
        if key in ['name', 'description', 'price', 'category']:
            update_parts.append(f'#{key} = :{key}')
            expression_names[f'#{key}'] = key
            expression_values[f':{key}'] = value

    update_parts.append('#updatedAt = :updatedAt')
    expression_names['#updatedAt'] = 'updatedAt'

    # Update GSI keys if category changes
    if 'category' in updates:
        update_parts.append('GSI1PK = :gsi1pk')
        expression_values[':gsi1pk'] = f"CATEGORY#{updates['category']}"

    try:
        response = table.update_item(
            Key={
                'PK': f'ITEM#{item_id}',
                'SK': 'METADATA'
            },
            UpdateExpression='SET ' + ', '.join(update_parts),
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW',
            ConditionExpression='attribute_exists(PK)'
        )

        item = response['Attributes']
        return {
            'id': item['id'],
            'name': item['name'],
            'description': item['description'],
            'price': float(item['price']),
            'category': item['category'],
            'createdAt': item['createdAt'],
            'updatedAt': item['updatedAt']
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return None
        raise Exception(f"Error updating item: {e.response['Error']['Message']}")


def delete_item(item_id: str) -> bool:
    """
    Delete an item by ID

    Args:
        item_id: The item's unique identifier

    Returns:
        True if deleted, False if not found
    """
    try:
        table.delete_item(
            Key={
                'PK': f'ITEM#{item_id}',
                'SK': 'METADATA'
            },
            ConditionExpression='attribute_exists(PK)'
        )
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        raise Exception(f"Error deleting item: {e.response['Error']['Message']}")
```

### src/utils/response.py

```python
"""
API response utilities
"""
import json
from typing import Any, Dict, Optional


def create_response(
    status_code: int,
    body: Any = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create a standardized API Gateway response

    Args:
        status_code: HTTP status code
        body: Response body (will be JSON serialized)
        headers: Additional headers

    Returns:
        API Gateway compatible response dict
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Api-Key',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

    if headers:
        default_headers.update(headers)

    response = {
        'statusCode': status_code,
        'headers': default_headers
    }

    if body is not None:
        response['body'] = json.dumps(body, default=str)

    return response


def success(data: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """Create a success response"""
    return create_response(status_code, data)


def created(data: Any) -> Dict[str, Any]:
    """Create a 201 Created response"""
    return create_response(201, data)


def no_content() -> Dict[str, Any]:
    """Create a 204 No Content response"""
    return create_response(204)


def bad_request(message: str, details: Any = None) -> Dict[str, Any]:
    """Create a 400 Bad Request response"""
    body = {
        'error': {
            'code': 'BAD_REQUEST',
            'message': message
        }
    }
    if details:
        body['error']['details'] = details
    return create_response(400, body)


def unauthorized(message: str = 'Unauthorized') -> Dict[str, Any]:
    """Create a 401 Unauthorized response"""
    return create_response(401, {
        'error': {
            'code': 'UNAUTHORIZED',
            'message': message
        }
    })


def forbidden(message: str = 'Forbidden') -> Dict[str, Any]:
    """Create a 403 Forbidden response"""
    return create_response(403, {
        'error': {
            'code': 'FORBIDDEN',
            'message': message
        }
    })


def not_found(resource: str = 'Resource') -> Dict[str, Any]:
    """Create a 404 Not Found response"""
    return create_response(404, {
        'error': {
            'code': 'NOT_FOUND',
            'message': f'{resource} not found'
        }
    })


def internal_error(message: str = 'Internal server error') -> Dict[str, Any]:
    """Create a 500 Internal Server Error response"""
    return create_response(500, {
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': message
        }
    })
```

### src/utils/validators.py

```python
"""
Input validation utilities
"""
from typing import Any, Dict, List, Optional, Tuple


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, details: List[str] = None):
        self.message = message
        self.details = details or []
        super().__init__(self.message)


def validate_item_input(data: Dict[str, Any], is_update: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate item input data

    Args:
        data: Input data to validate
        is_update: Whether this is an update operation

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Required fields for creation
    if not is_update:
        if not data.get('name'):
            errors.append('name is required')
        elif len(data['name']) < 1 or len(data['name']) > 200:
            errors.append('name must be between 1 and 200 characters')

    # Optional field validations
    if 'name' in data and is_update:
        if len(data['name']) < 1 or len(data['name']) > 200:
            errors.append('name must be between 1 and 200 characters')

    if 'description' in data:
        if len(data['description']) > 2000:
            errors.append('description must not exceed 2000 characters')

    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                errors.append('price must be non-negative')
            if price > 1000000:
                errors.append('price must not exceed 1,000,000')
        except (ValueError, TypeError):
            errors.append('price must be a valid number')

    if 'category' in data:
        valid_categories = ['electronics', 'clothing', 'books', 'home', 'general']
        if data['category'] not in valid_categories:
            errors.append(f'category must be one of: {", ".join(valid_categories)}')

    return len(errors) == 0, errors


def parse_query_params(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate query parameters

    Args:
        event: Lambda event object

    Returns:
        Parsed query parameters
    """
    params = event.get('queryStringParameters') or {}

    result = {}

    # Parse limit
    if 'limit' in params:
        try:
            limit = int(params['limit'])
            result['limit'] = min(max(1, limit), 100)  # Between 1 and 100
        except ValueError:
            result['limit'] = 20
    else:
        result['limit'] = 20

    # Parse category
    if 'category' in params:
        result['category'] = params['category']

    # Parse pagination token
    if 'nextToken' in params:
        result['nextToken'] = params['nextToken']

    return result
```

### src/handlers/create_item.py

```python
"""
Lambda handler for creating items
"""
import json
import os
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from utils.dynamodb import create_item
from utils.response import created, bad_request, internal_error
from utils.validators import validate_item_input

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """
    Create a new item

    POST /items

    Request body:
    {
        "name": "Item name",
        "description": "Description",
        "price": 29.99,
        "category": "electronics"
    }
    """
    logger.info("Creating new item")

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return bad_request('Invalid JSON in request body')

    # Validate input
    is_valid, errors = validate_item_input(body)
    if not is_valid:
        return bad_request('Validation failed', errors)

    # Get user ID from authorizer context
    user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', 'anonymous')

    try:
        # Create item
        item = create_item(body, user_id)
        logger.info(f"Item created: {item['id']}")
        return created(item)

    except Exception as e:
        logger.exception("Error creating item")
        return internal_error(str(e))
```

### src/handlers/get_item.py

```python
"""
Lambda handler for getting a single item
"""
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from utils.dynamodb import get_item
from utils.response import success, not_found, bad_request, internal_error

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """
    Get a single item by ID

    GET /items/{id}
    """
    # Get item ID from path parameters
    item_id = event.get('pathParameters', {}).get('id')

    if not item_id:
        return bad_request('Item ID is required')

    logger.info(f"Getting item: {item_id}")

    try:
        item = get_item(item_id)

        if not item:
            return not_found('Item')

        return success(item)

    except Exception as e:
        logger.exception("Error getting item")
        return internal_error(str(e))
```

### src/handlers/list_items.py

```python
"""
Lambda handler for listing items
"""
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from utils.dynamodb import list_items
from utils.response import success, internal_error
from utils.validators import parse_query_params

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """
    List all items with optional filtering and pagination

    GET /items
    GET /items?category=electronics
    GET /items?limit=10&nextToken=xxx
    """
    params = parse_query_params(event)
    logger.info(f"Listing items with params: {params}")

    try:
        result = list_items(
            category=params.get('category'),
            limit=params.get('limit', 20),
            last_key=params.get('nextToken')
        )

        return success(result)

    except Exception as e:
        logger.exception("Error listing items")
        return internal_error(str(e))
```

### src/handlers/update_item.py

```python
"""
Lambda handler for updating items
"""
import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from utils.dynamodb import update_item
from utils.response import success, not_found, bad_request, internal_error
from utils.validators import validate_item_input

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """
    Update an existing item

    PUT /items/{id}

    Request body:
    {
        "name": "Updated name",
        "description": "Updated description",
        "price": 39.99
    }
    """
    # Get item ID from path parameters
    item_id = event.get('pathParameters', {}).get('id')

    if not item_id:
        return bad_request('Item ID is required')

    logger.info(f"Updating item: {item_id}")

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return bad_request('Invalid JSON in request body')

    if not body:
        return bad_request('No update fields provided')

    # Validate input
    is_valid, errors = validate_item_input(body, is_update=True)
    if not is_valid:
        return bad_request('Validation failed', errors)

    try:
        item = update_item(item_id, body)

        if not item:
            return not_found('Item')

        logger.info(f"Item updated: {item_id}")
        return success(item)

    except Exception as e:
        logger.exception("Error updating item")
        return internal_error(str(e))
```

### src/handlers/delete_item.py

```python
"""
Lambda handler for deleting items
"""
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from utils.dynamodb import delete_item
from utils.response import no_content, not_found, bad_request, internal_error

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """
    Delete an item by ID

    DELETE /items/{id}
    """
    # Get item ID from path parameters
    item_id = event.get('pathParameters', {}).get('id')

    if not item_id:
        return bad_request('Item ID is required')

    logger.info(f"Deleting item: {item_id}")

    try:
        deleted = delete_item(item_id)

        if not deleted:
            return not_found('Item')

        logger.info(f"Item deleted: {item_id}")
        return no_content()

    except Exception as e:
        logger.exception("Error deleting item")
        return internal_error(str(e))
```

### src/handlers/health.py

```python
"""
Lambda handler for health checks
"""
import os
from datetime import datetime


def handler(event: dict, context) -> dict:
    """
    Health check endpoint

    GET /health
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"status": "healthy", "timestamp": "' + datetime.utcnow().isoformat() + 'Z"}'
    }
```

### requirements.txt

```
boto3>=1.26.0
aws-lambda-powertools>=2.0.0
```

---

## API Gateway Configuration

### Create REST API (CLI)

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name ${PROJECT_NAME}-api \
    --description "Serverless Items API" \
    --endpoint-configuration types=REGIONAL \
    --query 'id' \
    --output text)

echo "API ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[?path==`/`].id' \
    --output text)

# Create /items resource
ITEMS_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part items \
    --query 'id' \
    --output text)

# Create /items/{id} resource
ITEM_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ITEMS_ID \
    --path-part '{id}' \
    --query 'id' \
    --output text)

# Create /health resource
HEALTH_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part health \
    --query 'id' \
    --output text)
```

---

## Cognito Authentication

### Create User Pool

```bash
# Create User Pool
USER_POOL_ID=$(aws cognito-idp create-user-pool \
    --pool-name ${PROJECT_NAME}-users \
    --auto-verified-attributes email \
    --username-attributes email \
    --password-policy \
        MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false \
    --schema \
        Name=email,Required=true,Mutable=true \
        Name=name,Required=true,Mutable=true \
    --query 'UserPool.Id' \
    --output text)

echo "User Pool ID: $USER_POOL_ID"

# Create App Client
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
    --user-pool-id $USER_POOL_ID \
    --client-name ${PROJECT_NAME}-client \
    --no-generate-secret \
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH ALLOW_USER_SRP_AUTH \
    --supported-identity-providers COGNITO \
    --query 'UserPoolClient.ClientId' \
    --output text)

echo "Client ID: $CLIENT_ID"

# Create a test user
aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username testuser@example.com \
    --user-attributes Name=email,Value=testuser@example.com Name=name,Value="Test User" \
    --temporary-password "TempPass123"

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username testuser@example.com \
    --password "Password123" \
    --permanent
```

---

## SAM Template

### template.yaml

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: 'Serverless REST API with DynamoDB and Cognito'

Globals:
  Function:
    Runtime: python3.11
    Timeout: 30
    MemorySize: 256
    Tracing: Active
    Environment:
      Variables:
        TABLE_NAME: !Ref ItemsTable
        LOG_LEVEL: INFO
        POWERTOOLS_SERVICE_NAME: serverless-api
        POWERTOOLS_METRICS_NAMESPACE: ServerlessAPI

  Api:
    TracingEnabled: true
    Cors:
      AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
      AllowHeaders: "'Content-Type,Authorization,X-Api-Key'"
      AllowOrigin: "'*'"

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  # ==================== DynamoDB ====================
  ItemsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${AWS::StackName}-items
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true
      Tags:
        - Key: Environment
          Value: !Ref Stage

  # ==================== Cognito ====================
  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub ${AWS::StackName}-users
      AutoVerifiedAttributes:
        - email
      UsernameAttributes:
        - email
      Policies:
        PasswordPolicy:
          MinimumLength: 8
          RequireUppercase: true
          RequireLowercase: true
          RequireNumbers: true
          RequireSymbols: false
      Schema:
        - Name: email
          Required: true
          Mutable: true
        - Name: name
          Required: true
          Mutable: true

  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: !Sub ${AWS::StackName}-client
      UserPoolId: !Ref UserPool
      GenerateSecret: false
      ExplicitAuthFlows:
        - ALLOW_USER_PASSWORD_AUTH
        - ALLOW_REFRESH_TOKEN_AUTH
        - ALLOW_USER_SRP_AUTH

  # ==================== API Gateway ====================
  ApiGateway:
    Type: AWS::Serverless::Api
    Properties:
      Name: !Sub ${AWS::StackName}-api
      StageName: !Ref Stage
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
        AddDefaultAuthorizerToCorsPreflight: false
      MethodSettings:
        - ResourcePath: '/*'
          HttpMethod: '*'
          ThrottlingBurstLimit: 100
          ThrottlingRateLimit: 50
          LoggingLevel: INFO
          DataTraceEnabled: true
          MetricsEnabled: true

  # ==================== Lambda Functions ====================
  CreateItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-create-item
      Handler: handlers.create_item.handler
      CodeUri: src/
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
      Events:
        CreateItem:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /items
            Method: POST

  GetItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-get-item
      Handler: handlers.get_item.handler
      CodeUri: src/
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref ItemsTable
      Events:
        GetItem:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /items/{id}
            Method: GET

  ListItemsFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-list-items
      Handler: handlers.list_items.handler
      CodeUri: src/
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref ItemsTable
      Events:
        ListItems:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /items
            Method: GET

  UpdateItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-update-item
      Handler: handlers.update_item.handler
      CodeUri: src/
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
      Events:
        UpdateItem:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /items/{id}
            Method: PUT

  DeleteItemFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-delete-item
      Handler: handlers.delete_item.handler
      CodeUri: src/
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
      Events:
        DeleteItem:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /items/{id}
            Method: DELETE

  HealthFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${AWS::StackName}-health
      Handler: handlers.health.handler
      CodeUri: src/
      Events:
        Health:
          Type: Api
          Properties:
            RestApiId: !Ref ApiGateway
            Path: /health
            Method: GET
            Auth:
              Authorizer: NONE

  # ==================== CloudWatch Dashboard ====================
  Dashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: !Sub ${AWS::StackName}-dashboard
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "x": 0, "y": 0, "width": 12, "height": 6,
              "properties": {
                "title": "API Requests",
                "metrics": [
                  ["AWS/ApiGateway", "Count", "ApiName", "${ApiGateway}", {"stat": "Sum"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 12, "y": 0, "width": 12, "height": 6,
              "properties": {
                "title": "API Latency",
                "metrics": [
                  ["AWS/ApiGateway", "Latency", "ApiName", "${ApiGateway}", {"stat": "Average"}],
                  ["...", {"stat": "p99"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 0, "y": 6, "width": 12, "height": 6,
              "properties": {
                "title": "Lambda Invocations",
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "${CreateItemFunction}", {"stat": "Sum"}],
                  ["...", "${GetItemFunction}", {"stat": "Sum"}],
                  ["...", "${ListItemsFunction}", {"stat": "Sum"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 12, "y": 6, "width": 12, "height": 6,
              "properties": {
                "title": "Lambda Errors",
                "metrics": [
                  ["AWS/Lambda", "Errors", "FunctionName", "${CreateItemFunction}", {"stat": "Sum"}],
                  ["...", "${GetItemFunction}", {"stat": "Sum"}],
                  ["...", "${ListItemsFunction}", {"stat": "Sum"}]
                ],
                "period": 60
              }
            },
            {
              "type": "metric",
              "x": 0, "y": 12, "width": 12, "height": 6,
              "properties": {
                "title": "DynamoDB Consumed Capacity",
                "metrics": [
                  ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "${ItemsTable}", {"stat": "Sum"}],
                  [".", "ConsumedWriteCapacityUnits", ".", ".", {"stat": "Sum"}]
                ],
                "period": 60
              }
            }
          ]
        }

  # ==================== Alarms ====================
  ApiErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-api-errors
      AlarmDescription: API Gateway 5XX errors
      MetricName: 5XXError
      Namespace: AWS/ApiGateway
      Dimensions:
        - Name: ApiName
          Value: !Ref ApiGateway
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 5
      Threshold: 10
      ComparisonOperator: GreaterThanThreshold

  LambdaErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub ${AWS::StackName}-lambda-errors
      AlarmDescription: Lambda function errors
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref CreateItemFunction
      Statistic: Sum
      Period: 60
      EvaluationPeriods: 3
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${Stage}
    Export:
      Name: !Sub ${AWS::StackName}-ApiEndpoint

  UserPoolId:
    Description: Cognito User Pool ID
    Value: !Ref UserPool
    Export:
      Name: !Sub ${AWS::StackName}-UserPoolId

  UserPoolClientId:
    Description: Cognito User Pool Client ID
    Value: !Ref UserPoolClient
    Export:
      Name: !Sub ${AWS::StackName}-UserPoolClientId

  TableName:
    Description: DynamoDB Table Name
    Value: !Ref ItemsTable
    Export:
      Name: !Sub ${AWS::StackName}-TableName
```

### samconfig.toml

```toml
version = 0.1

[default.deploy.parameters]
stack_name = "serverless-api"
resolve_s3 = true
s3_prefix = "serverless-api"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
parameter_overrides = "Stage=dev"

[dev.deploy.parameters]
stack_name = "serverless-api-dev"
parameter_overrides = "Stage=dev"

[prod.deploy.parameters]
stack_name = "serverless-api-prod"
parameter_overrides = "Stage=prod"
```

### Deploy with SAM

```bash
# Build the application
sam build

# Deploy (guided for first time)
sam deploy --guided

# Deploy to specific environment
sam deploy --config-env dev

# Local testing
sam local start-api

# Invoke single function locally
sam local invoke CreateItemFunction -e events/create-item.json
```

---

## Testing Instructions

### Test Authentication

```bash
# Get auth token
USER_POOL_ID="us-east-1_xxxxxxxx"
CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxx"
USERNAME="testuser@example.com"
PASSWORD="Password123"

# Authenticate and get token
TOKEN=$(aws cognito-idp initiate-auth \
    --client-id $CLIENT_ID \
    --auth-flow USER_PASSWORD_AUTH \
    --auth-parameters USERNAME=$USERNAME,PASSWORD=$PASSWORD \
    --query 'AuthenticationResult.IdToken' \
    --output text)

echo "Token: ${TOKEN:0:50}..."
```

### Test API Endpoints

```bash
# Set API endpoint
API_URL="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev"

# Health check (no auth required)
curl -X GET "${API_URL}/health"

# Create item
curl -X POST "${API_URL}/items" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test Item",
        "description": "A test item",
        "price": 29.99,
        "category": "electronics"
    }'

# List items
curl -X GET "${API_URL}/items" \
    -H "Authorization: Bearer $TOKEN"

# Get single item
curl -X GET "${API_URL}/items/{item-id}" \
    -H "Authorization: Bearer $TOKEN"

# Update item
curl -X PUT "${API_URL}/items/{item-id}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Updated Item",
        "price": 39.99
    }'

# Delete item
curl -X DELETE "${API_URL}/items/{item-id}" \
    -H "Authorization: Bearer $TOKEN"
```

### Unit Tests (tests/unit/test_handlers.py)

```python
"""
Unit tests for Lambda handlers
"""
import json
import pytest
from unittest.mock import patch, MagicMock

# Import handlers
import sys
sys.path.insert(0, 'src')

from handlers.create_item import handler as create_handler
from handlers.get_item import handler as get_handler
from handlers.list_items import handler as list_handler


@pytest.fixture
def api_gateway_event():
    """Base API Gateway event"""
    return {
        'httpMethod': 'POST',
        'path': '/items',
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123'
        },
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'user-123'
                }
            }
        },
        'body': None,
        'pathParameters': None,
        'queryStringParameters': None
    }


class TestCreateItem:
    """Tests for create item handler"""

    @patch('handlers.create_item.create_item')
    def test_create_item_success(self, mock_create, api_gateway_event):
        """Test successful item creation"""
        mock_create.return_value = {
            'id': 'item-123',
            'name': 'Test Item',
            'description': 'Test',
            'price': 29.99,
            'category': 'electronics',
            'createdAt': '2026-01-01T00:00:00Z',
            'updatedAt': '2026-01-01T00:00:00Z'
        }

        api_gateway_event['body'] = json.dumps({
            'name': 'Test Item',
            'description': 'Test',
            'price': 29.99,
            'category': 'electronics'
        })

        response = create_handler(api_gateway_event, None)

        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['name'] == 'Test Item'

    def test_create_item_missing_name(self, api_gateway_event):
        """Test validation error for missing name"""
        api_gateway_event['body'] = json.dumps({
            'description': 'Test'
        })

        response = create_handler(api_gateway_event, None)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'name is required' in body['error']['details']

    def test_create_item_invalid_json(self, api_gateway_event):
        """Test error for invalid JSON"""
        api_gateway_event['body'] = 'not valid json'

        response = create_handler(api_gateway_event, None)

        assert response['statusCode'] == 400


class TestGetItem:
    """Tests for get item handler"""

    @patch('handlers.get_item.get_item')
    def test_get_item_success(self, mock_get, api_gateway_event):
        """Test successful item retrieval"""
        mock_get.return_value = {
            'id': 'item-123',
            'name': 'Test Item'
        }

        api_gateway_event['pathParameters'] = {'id': 'item-123'}

        response = get_handler(api_gateway_event, None)

        assert response['statusCode'] == 200

    @patch('handlers.get_item.get_item')
    def test_get_item_not_found(self, mock_get, api_gateway_event):
        """Test item not found"""
        mock_get.return_value = None

        api_gateway_event['pathParameters'] = {'id': 'nonexistent'}

        response = get_handler(api_gateway_event, None)

        assert response['statusCode'] == 404


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Monitoring and Logging

### CloudWatch Logs Insights Queries

```
# Find all errors in the last hour
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

# Analyze cold starts
fields @timestamp, @message, @duration
| filter @message like /INIT_START/
| stats count() as coldStarts by bin(5m)

# Average duration by function
fields @timestamp, @duration
| filter @type = "REPORT"
| stats avg(@duration) as avgDuration by @log
```

### X-Ray Tracing

```python
# Enable X-Ray tracing in handler
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

@xray_recorder.capture('create_item')
def create_item_logic(data):
    # Your logic here
    pass
```

---

## Cost Analysis

### Monthly Cost Breakdown (Estimates)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | 1M invocations (256MB, 200ms avg) | $0.42 |
| API Gateway | 1M requests | $3.50 |
| DynamoDB | 1M reads + 500K writes | $1.50 |
| CloudWatch Logs | 5GB | $2.50 |
| Cognito | 1,000 MAUs | Free |
| **Total** | | **~$8/month** |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired token | Refresh token or re-authenticate |
| 403 Forbidden | Missing permissions | Check IAM role and resource policies |
| 502 Bad Gateway | Lambda error | Check CloudWatch Logs |
| Timeout | Lambda cold start or slow DB | Increase timeout, use provisioned concurrency |
| ValidationError | Invalid input | Check request body format |

### Debug Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/serverless-api-create-item --follow

# Test Lambda locally
sam local invoke CreateItemFunction \
    -e events/create-item.json \
    --env-vars env.json

# Check API Gateway configuration
aws apigateway get-rest-api --rest-api-id $API_ID

# View DynamoDB table
aws dynamodb scan --table-name serverless-api-items --limit 10
```

---

## Cleanup

```bash
# Delete SAM stack
sam delete --stack-name serverless-api

# Or delete via CloudFormation
aws cloudformation delete-stack --stack-name serverless-api
aws cloudformation wait stack-delete-complete --stack-name serverless-api
```

---

**Congratulations!** You have deployed a production-ready serverless REST API with authentication, validation, and monitoring.

[Back to Project Overview](./README.md) | [Next: Data Pipeline Project](../04-data-pipeline/implementation.md)
