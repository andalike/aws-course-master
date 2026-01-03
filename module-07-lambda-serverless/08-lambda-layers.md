# Lambda Layers

## Introduction

Lambda Layers are a distribution mechanism for libraries, custom runtimes, and other function dependencies. They allow you to manage code shared across multiple functions, reducing deployment package size and promoting code reuse.

## What are Lambda Layers?

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAMBDA LAYERS ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    LAMBDA FUNCTION                          ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │              Your Function Code                      │   ││
│  │  │                handler.py                            │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  │                          │                                  ││
│  │                          ▼                                  ││
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐               ││
│  │  │  Layer 1  │  │  Layer 2  │  │  Layer 3  │   (Up to 5)   ││
│  │  │ (Utils)   │  │ (SDK)     │  │ (Runtime) │               ││
│  │  └───────────┘  └───────────┘  └───────────┘               ││
│  │         │              │              │                     ││
│  │         └──────────────┼──────────────┘                     ││
│  │                        ▼                                    ││
│  │              ┌─────────────────┐                            ││
│  │              │   /opt/         │  Layers extracted here     ││
│  │              │   ├── python/   │                            ││
│  │              │   ├── nodejs/   │                            ││
│  │              │   └── bin/      │                            ││
│  │              └─────────────────┘                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Characteristics

| Feature | Description |
|---------|-------------|
| Maximum Layers | 5 per function |
| Maximum Size | 250 MB unzipped (all layers + function) |
| Extraction Path | `/opt` directory |
| Versioning | Immutable versions, version numbers |
| Sharing | Can share across accounts and make public |
| Runtimes | Runtime-specific paths for libraries |

## Benefits of Using Layers

### 1. Code Reuse
```
┌──────────────────────────────────────────────────────────────┐
│                    WITHOUT LAYERS                             │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Function A│  │Function B│  │Function C│  │Function D│     │
│  │ + boto3  │  │ + boto3  │  │ + boto3  │  │ + boto3  │     │
│  │ + pandas │  │ + pandas │  │ + pandas │  │ + pandas │     │
│  │ + numpy  │  │ + numpy  │  │ + numpy  │  │ + numpy  │     │
│  │ = 50 MB  │  │ = 50 MB  │  │ = 50 MB  │  │ = 50 MB  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                               │
│                    Total: 200 MB                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    WITH LAYERS                                │
│                                                               │
│              ┌────────────────────────────┐                  │
│              │    Shared Dependencies     │                  │
│              │    Layer (50 MB once)      │                  │
│              └────────────────────────────┘                  │
│                          │                                    │
│         ┌────────────────┼────────────────┐                  │
│         │                │                │                   │
│         ▼                ▼                ▼                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Function A│  │Function B│  │Function C│  │Function D│     │
│  │  1 MB    │  │  1 MB    │  │  1 MB    │  │  1 MB    │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                               │
│                    Total: 54 MB                               │
└──────────────────────────────────────────────────────────────┘
```

### 2. Faster Deployments
- Smaller function packages deploy faster
- Only update layers when dependencies change
- Function code updates are quick

### 3. Separation of Concerns
- Dependencies managed separately from business logic
- Different teams can manage layers
- Version control for dependencies

## Layer Structure

### Python Layer Structure

```
python-layer.zip
├── python/
│   ├── lib/
│   │   └── python3.12/
│   │       └── site-packages/
│   │           ├── requests/
│   │           ├── pandas/
│   │           └── numpy/
│   └── (alternative flat structure)
│       ├── requests/
│       └── pandas/
```

### Node.js Layer Structure

```
nodejs-layer.zip
├── nodejs/
│   └── node_modules/
│       ├── axios/
│       ├── lodash/
│       └── uuid/
```

### Binary/Executable Layer Structure

```
custom-layer.zip
├── bin/
│   └── my-binary
├── lib/
│   └── libcustom.so
└── python/
    └── my_module.py
```

## Creating Lambda Layers

### Method 1: Creating a Python Layer (CLI)

#### Step 1: Create Layer Directory Structure

```bash
# Create directory structure
mkdir -p python-layer/python/lib/python3.12/site-packages

# Install dependencies
pip install requests pandas -t python-layer/python/lib/python3.12/site-packages/

# Create zip file
cd python-layer
zip -r ../python-dependencies-layer.zip python/
cd ..
```

#### Step 2: Publish the Layer

```bash
# Publish layer
aws lambda publish-layer-version \
    --layer-name python-dependencies \
    --description "Python dependencies: requests, pandas" \
    --zip-file fileb://python-dependencies-layer.zip \
    --compatible-runtimes python3.11 python3.12 \
    --compatible-architectures x86_64 arm64

# Response includes LayerVersionArn
# arn:aws:lambda:us-east-1:123456789012:layer:python-dependencies:1
```

### Method 2: Creating a Node.js Layer

#### Step 1: Create Layer Directory Structure

```bash
# Create directory structure
mkdir -p nodejs-layer/nodejs

# Initialize and install dependencies
cd nodejs-layer/nodejs
npm init -y
npm install axios lodash uuid

# Create zip file
cd ..
zip -r ../nodejs-dependencies-layer.zip nodejs/
cd ..
```

#### Step 2: Publish the Layer

```bash
aws lambda publish-layer-version \
    --layer-name nodejs-dependencies \
    --description "Node.js dependencies: axios, lodash, uuid" \
    --zip-file fileb://nodejs-dependencies-layer.zip \
    --compatible-runtimes nodejs18.x nodejs20.x \
    --compatible-architectures x86_64 arm64
```

### Method 3: Creating a Layer with Docker (Cross-Platform)

For dependencies with compiled components, use Docker to ensure compatibility:

```bash
# Python layer with compiled dependencies
docker run -v "$PWD":/var/task \
    public.ecr.aws/sam/build-python3.12:latest \
    pip install numpy pandas -t python/lib/python3.12/site-packages/

# Zip the layer
zip -r python-data-layer.zip python/

# Publish
aws lambda publish-layer-version \
    --layer-name python-data-processing \
    --zip-file fileb://python-data-layer.zip \
    --compatible-runtimes python3.12
```

### Method 4: Creating a Custom Runtime Layer

```bash
# Create custom runtime layer structure
mkdir -p custom-runtime/bin

# Create bootstrap file (required for custom runtimes)
cat > custom-runtime/bin/bootstrap << 'EOF'
#!/bin/bash
set -euo pipefail

# Handler format: file.method
HANDLER_FILE=$(echo "$_HANDLER" | cut -d. -f1)
HANDLER_METHOD=$(echo "$_HANDLER" | cut -d. -f2)

# Processing loop
while true; do
    # Get next invocation
    HEADERS="$(mktemp)"
    EVENT_DATA=$(curl -sS -LD "$HEADERS" \
        "http://${AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/next")

    REQUEST_ID=$(grep -Fi Lambda-Runtime-Aws-Request-Id "$HEADERS" | tr -d '[:space:]' | cut -d: -f2)

    # Execute handler
    RESPONSE=$(source "$HANDLER_FILE" && $HANDLER_METHOD "$EVENT_DATA")

    # Send response
    curl -sS -X POST \
        "http://${AWS_LAMBDA_RUNTIME_API}/2018-06-01/runtime/invocation/$REQUEST_ID/response" \
        -d "$RESPONSE"
done
EOF

chmod +x custom-runtime/bin/bootstrap

# Create zip
cd custom-runtime
zip -r ../custom-runtime-layer.zip .
cd ..

# Publish
aws lambda publish-layer-version \
    --layer-name custom-bash-runtime \
    --zip-file fileb://custom-runtime-layer.zip \
    --compatible-runtimes provided.al2023
```

## Using Layers in Functions

### CLI - Attach Layer to Function

```bash
# Update function to use layer
aws lambda update-function-configuration \
    --function-name my-function \
    --layers \
        arn:aws:lambda:us-east-1:123456789012:layer:python-dependencies:1 \
        arn:aws:lambda:us-east-1:123456789012:layer:custom-utils:3

# List function layers
aws lambda get-function-configuration \
    --function-name my-function \
    --query 'Layers'
```

### SAM Template - Using Layers

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.12
    Layers:
      - !Ref SharedDependenciesLayer

Resources:
  # Define the layer
  SharedDependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: shared-dependencies
      Description: Shared Python dependencies
      ContentUri: layers/dependencies/
      CompatibleRuntimes:
        - python3.11
        - python3.12
      CompatibleArchitectures:
        - x86_64
        - arm64
      RetentionPolicy: Retain
    Metadata:
      BuildMethod: python3.12

  # Function using the layer
  ProcessDataFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      CodeUri: src/process-data/
      # Inherits layer from Globals

  # Function with additional layer
  AnalyticsFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      CodeUri: src/analytics/
      Layers:
        - !Ref SharedDependenciesLayer
        - !Ref DataScienceLayer

  # Layer with external dependencies
  DataScienceLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: data-science
      ContentUri: layers/data-science/
      CompatibleRuntimes:
        - python3.12
    Metadata:
      BuildMethod: python3.12
```

### CloudFormation - Using Layers

```yaml
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: python3.12
      Handler: index.handler
      Code:
        S3Bucket: my-bucket
        S3Key: function.zip
      Layers:
        - arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1
        - !Ref MyCustomLayer
      Role: !GetAtt LambdaRole.Arn

  MyCustomLayer:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: my-custom-layer
      Description: Custom utilities layer
      Content:
        S3Bucket: my-bucket
        S3Key: my-layer.zip
      CompatibleRuntimes:
        - python3.12
      CompatibleArchitectures:
        - x86_64
```

### Python Function Using Layer

```python
# Function code - imports from layer are available
import json
import requests  # From layer
import pandas as pd  # From layer
from shared_utils import format_response  # From layer

def handler(event, context):
    # Use library from layer
    response = requests.get('https://api.example.com/data')

    # Process with pandas
    df = pd.DataFrame(response.json())

    return format_response(200, df.to_dict())
```

### Node.js Function Using Layer

```javascript
// Function code - modules from layer are available
const axios = require('axios');  // From layer
const _ = require('lodash');     // From layer
const { v4: uuidv4 } = require('uuid');  // From layer

exports.handler = async (event) => {
    const response = await axios.get('https://api.example.com/data');

    const processedData = _.map(response.data, item => ({
        ...item,
        id: uuidv4()
    }));

    return {
        statusCode: 200,
        body: JSON.stringify(processedData)
    };
};
```

## Layer Versioning

### Understanding Version Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER VERSIONING                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer: python-dependencies                                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Version 1   │  │  Version 2   │  │  Version 3   │          │
│  │  requests    │  │  requests    │  │  requests    │          │
│  │  2.28.0      │  │  2.29.0      │  │  2.31.0      │          │
│  │  pandas      │  │  pandas      │  │  pandas      │          │
│  │  1.5.0       │  │  2.0.0       │  │  2.1.0       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                                    │                   │
│         │                                    │                   │
│  Function A                           Function B                 │
│  (uses v1)                           (uses v3)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Publishing New Versions

```bash
# Each publish creates a new version number
aws lambda publish-layer-version \
    --layer-name python-dependencies \
    --zip-file fileb://python-dependencies-v2.zip \
    --compatible-runtimes python3.12

# Returns: arn:aws:lambda:us-east-1:123456789012:layer:python-dependencies:2
```

### Managing Layer Versions

```bash
# List layer versions
aws lambda list-layer-versions \
    --layer-name python-dependencies

# Get specific version
aws lambda get-layer-version \
    --layer-name python-dependencies \
    --version-number 2

# Delete old version
aws lambda delete-layer-version \
    --layer-name python-dependencies \
    --version-number 1
```

### Version Update Strategy

```bash
#!/bin/bash
# Script: update-layer-for-functions.sh

LAYER_NAME="python-dependencies"
NEW_VERSION="3"
NEW_LAYER_ARN="arn:aws:lambda:us-east-1:123456789012:layer:$LAYER_NAME:$NEW_VERSION"

# List functions using this layer
FUNCTIONS=$(aws lambda list-functions \
    --query 'Functions[?contains(Layers[].Arn, `'$LAYER_NAME'`)].FunctionName' \
    --output text)

# Update each function to new layer version
for FUNC in $FUNCTIONS; do
    echo "Updating $FUNC to layer version $NEW_VERSION"

    # Get current layers
    CURRENT_LAYERS=$(aws lambda get-function-configuration \
        --function-name $FUNC \
        --query 'Layers[].Arn' \
        --output text)

    # Replace old layer version with new
    UPDATED_LAYERS=$(echo $CURRENT_LAYERS | sed "s|$LAYER_NAME:[0-9]*|$LAYER_NAME:$NEW_VERSION|g")

    # Update function
    aws lambda update-function-configuration \
        --function-name $FUNC \
        --layers $UPDATED_LAYERS
done
```

## Sharing Layers

### Share with Specific AWS Accounts

```bash
# Add permission for another account
aws lambda add-layer-version-permission \
    --layer-name python-dependencies \
    --version-number 1 \
    --statement-id account-123 \
    --principal 123456789012 \
    --action lambda:GetLayerVersion

# Share with an organization
aws lambda add-layer-version-permission \
    --layer-name python-dependencies \
    --version-number 1 \
    --statement-id org-sharing \
    --principal "*" \
    --action lambda:GetLayerVersion \
    --organization-id o-1234567890
```

### Make Layer Public

```bash
# Make layer publicly accessible
aws lambda add-layer-version-permission \
    --layer-name python-dependencies \
    --version-number 1 \
    --statement-id public \
    --principal "*" \
    --action lambda:GetLayerVersion
```

### View and Remove Permissions

```bash
# View layer policy
aws lambda get-layer-version-policy \
    --layer-name python-dependencies \
    --version-number 1

# Remove permission
aws lambda remove-layer-version-permission \
    --layer-name python-dependencies \
    --version-number 1 \
    --statement-id account-123
```

## Hands-On Lab: Creating a Shared Utilities Layer

### Lab Objective

Create a Python utilities layer with common functions that can be shared across multiple Lambda functions.

### Step 1: Create the Layer Code

```bash
# Create directory structure
mkdir -p shared-utils-layer/python
cd shared-utils-layer
```

### Step 2: Create Utility Module

```python
# python/shared_utils.py
"""
Shared utilities for Lambda functions
"""
import json
import logging
from datetime import datetime, timezone
from functools import wraps
import traceback

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_response(status_code, body, headers=None):
    """
    Create a standard API Gateway response

    Args:
        status_code (int): HTTP status code
        body (dict): Response body
        headers (dict): Additional headers

    Returns:
        dict: Formatted response for API Gateway
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

    if headers:
        default_headers.update(headers)

    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, default=str)
    }


def success_response(data, message="Success"):
    """Create a success response"""
    return create_response(200, {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })


def error_response(status_code, message, error_code=None):
    """Create an error response"""
    body = {
        'success': False,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    if error_code:
        body['error_code'] = error_code
    return create_response(status_code, body)


def lambda_handler(func):
    """
    Decorator for Lambda handlers with error handling and logging

    Usage:
        @lambda_handler
        def handler(event, context):
            return {'result': 'success'}
    """
    @wraps(func)
    def wrapper(event, context):
        request_id = context.aws_request_id if context else 'local'

        logger.info(f"Request {request_id}: Starting {func.__name__}")
        logger.info(f"Event: {json.dumps(event, default=str)}")

        try:
            result = func(event, context)
            logger.info(f"Request {request_id}: Completed successfully")
            return result

        except ValidationError as e:
            logger.warning(f"Request {request_id}: Validation error - {str(e)}")
            return error_response(400, str(e), 'VALIDATION_ERROR')

        except NotFoundError as e:
            logger.warning(f"Request {request_id}: Not found - {str(e)}")
            return error_response(404, str(e), 'NOT_FOUND')

        except Exception as e:
            logger.error(f"Request {request_id}: Error - {str(e)}")
            logger.error(traceback.format_exc())
            return error_response(500, 'Internal server error', 'INTERNAL_ERROR')

    return wrapper


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class NotFoundError(Exception):
    """Raised when a resource is not found"""
    pass


def validate_required_fields(data, required_fields):
    """
    Validate that required fields are present in data

    Args:
        data (dict): Input data
        required_fields (list): List of required field names

    Raises:
        ValidationError: If any required field is missing
    """
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def parse_event_body(event):
    """
    Parse the body from an API Gateway event

    Args:
        event (dict): Lambda event

    Returns:
        dict: Parsed body
    """
    body = event.get('body')
    if body is None:
        return {}

    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON in request body")

    return body


def get_path_parameter(event, param_name, required=True):
    """
    Get a path parameter from the event

    Args:
        event (dict): Lambda event
        param_name (str): Parameter name
        required (bool): Whether the parameter is required

    Returns:
        str: Parameter value or None
    """
    params = event.get('pathParameters') or {}
    value = params.get(param_name)

    if required and not value:
        raise ValidationError(f"Missing path parameter: {param_name}")

    return value


def get_query_parameter(event, param_name, default=None, param_type=str):
    """
    Get a query parameter from the event

    Args:
        event (dict): Lambda event
        param_name (str): Parameter name
        default: Default value if not present
        param_type: Type to convert to (str, int, bool)

    Returns:
        Converted parameter value or default
    """
    params = event.get('queryStringParameters') or {}
    value = params.get(param_name)

    if value is None:
        return default

    try:
        if param_type == bool:
            return value.lower() in ('true', '1', 'yes')
        return param_type(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid value for parameter: {param_name}")
```

### Step 3: Create Database Utilities

```python
# python/db_utils.py
"""
Database utilities for DynamoDB operations
"""
import boto3
from decimal import Decimal
import json
from datetime import datetime, timezone
from shared_utils import NotFoundError

# Initialize outside handler for connection reuse
_dynamodb = None


def get_dynamodb_resource():
    """Get or create DynamoDB resource"""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource('dynamodb')
    return _dynamodb


class DynamoDBTable:
    """
    Wrapper for DynamoDB table operations
    """

    def __init__(self, table_name):
        self.table_name = table_name
        self._table = None

    @property
    def table(self):
        if self._table is None:
            dynamodb = get_dynamodb_resource()
            self._table = dynamodb.Table(self.table_name)
        return self._table

    def get_item(self, key):
        """
        Get a single item by key

        Args:
            key (dict): Primary key

        Returns:
            dict: Item data

        Raises:
            NotFoundError: If item not found
        """
        response = self.table.get_item(Key=key)
        item = response.get('Item')
        if not item:
            raise NotFoundError(f"Item not found with key: {key}")
        return self._convert_decimals(item)

    def put_item(self, item, condition=None):
        """
        Put an item into the table

        Args:
            item (dict): Item to store
            condition (str): Optional condition expression
        """
        # Add timestamps
        now = datetime.now(timezone.utc).isoformat()
        item['updatedAt'] = now
        if 'createdAt' not in item:
            item['createdAt'] = now

        # Convert floats to Decimals
        item = self._convert_to_decimals(item)

        params = {'Item': item}
        if condition:
            params['ConditionExpression'] = condition

        self.table.put_item(**params)
        return self._convert_decimals(item)

    def update_item(self, key, updates):
        """
        Update an item

        Args:
            key (dict): Primary key
            updates (dict): Fields to update

        Returns:
            dict: Updated item
        """
        updates['updatedAt'] = datetime.now(timezone.utc).isoformat()
        updates = self._convert_to_decimals(updates)

        update_expr = 'SET ' + ', '.join(f'#{k} = :{k}' for k in updates.keys())
        expr_names = {f'#{k}': k for k in updates.keys()}
        expr_values = {f':{k}': v for k, v in updates.items()}

        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )

        return self._convert_decimals(response.get('Attributes', {}))

    def delete_item(self, key):
        """Delete an item"""
        self.table.delete_item(Key=key)

    def query(self, key_condition, filter_expr=None, limit=None):
        """
        Query items by partition key

        Args:
            key_condition: Key condition expression
            filter_expr: Optional filter expression
            limit: Maximum items to return

        Returns:
            list: List of items
        """
        params = {'KeyConditionExpression': key_condition}

        if filter_expr:
            params['FilterExpression'] = filter_expr
        if limit:
            params['Limit'] = limit

        response = self.table.query(**params)
        return [self._convert_decimals(item) for item in response.get('Items', [])]

    def scan(self, filter_expr=None, limit=None):
        """
        Scan table

        Args:
            filter_expr: Optional filter expression
            limit: Maximum items to return

        Returns:
            list: List of items
        """
        params = {}

        if filter_expr:
            params['FilterExpression'] = filter_expr
        if limit:
            params['Limit'] = limit

        response = self.table.scan(**params)
        return [self._convert_decimals(item) for item in response.get('Items', [])]

    @staticmethod
    def _convert_decimals(obj):
        """Convert Decimal types to int/float for JSON serialization"""
        if isinstance(obj, dict):
            return {k: DynamoDBTable._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DynamoDBTable._convert_decimals(i) for i in obj]
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return obj

    @staticmethod
    def _convert_to_decimals(obj):
        """Convert float types to Decimal for DynamoDB"""
        if isinstance(obj, dict):
            return {k: DynamoDBTable._convert_to_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DynamoDBTable._convert_to_decimals(i) for i in obj]
        elif isinstance(obj, float):
            return Decimal(str(obj))
        return obj
```

### Step 4: Package and Deploy the Layer

```bash
# Create requirements.txt for any additional dependencies
cat > python/requirements.txt << 'EOF'
# No external dependencies for this utils layer
# boto3 is included in Lambda runtime
EOF

# Zip the layer
zip -r shared-utils-layer.zip python/

# Publish the layer
aws lambda publish-layer-version \
    --layer-name shared-utils \
    --description "Shared utilities: response formatting, error handling, DynamoDB wrapper" \
    --zip-file fileb://shared-utils-layer.zip \
    --compatible-runtimes python3.11 python3.12 \
    --compatible-architectures x86_64 arm64

# Note the Layer ARN returned
```

### Step 5: Use the Layer in a Function

```python
# handler.py - A Lambda function using the layer
from shared_utils import (
    lambda_handler,
    success_response,
    parse_event_body,
    get_path_parameter,
    validate_required_fields,
    ValidationError
)
from db_utils import DynamoDBTable
import os

# Initialize table (reused in warm starts)
users_table = DynamoDBTable(os.environ['USERS_TABLE'])


@lambda_handler
def get_user(event, context):
    """Get a user by ID"""
    user_id = get_path_parameter(event, 'userId')
    user = users_table.get_item({'userId': user_id})
    return success_response(user)


@lambda_handler
def create_user(event, context):
    """Create a new user"""
    body = parse_event_body(event)
    validate_required_fields(body, ['email', 'name'])

    user = users_table.put_item({
        'userId': body.get('userId') or str(uuid.uuid4()),
        'email': body['email'],
        'name': body['name'],
        'status': 'active'
    })

    return success_response(user, "User created successfully")


@lambda_handler
def update_user(event, context):
    """Update a user"""
    user_id = get_path_parameter(event, 'userId')
    body = parse_event_body(event)

    # Validate at least one field to update
    allowed_fields = ['email', 'name', 'status']
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        raise ValidationError("No valid fields to update")

    updated_user = users_table.update_item(
        {'userId': user_id},
        updates
    )

    return success_response(updated_user, "User updated successfully")
```

### Step 6: Deploy Function with Layer (SAM)

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  SharedUtilsLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: shared-utils
      ContentUri: layers/shared-utils/
      CompatibleRuntimes:
        - python3.12
    Metadata:
      BuildMethod: python3.12

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: userId
          AttributeType: S
      KeySchema:
        - AttributeName: userId
          KeyType: HASH

  UsersApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod

  GetUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: handler.get_user
      Runtime: python3.12
      CodeUri: src/
      Layers:
        - !Ref SharedUtilsLayer
      Environment:
        Variables:
          USERS_TABLE: !Ref UsersTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
      Events:
        GetUser:
          Type: Api
          Properties:
            RestApiId: !Ref UsersApi
            Path: /users/{userId}
            Method: GET

  CreateUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: handler.create_user
      Runtime: python3.12
      CodeUri: src/
      Layers:
        - !Ref SharedUtilsLayer
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
            RestApiId: !Ref UsersApi
            Path: /users
            Method: POST
```

## AWS-Provided Layers

### Available AWS Layers

| Layer | Description | Use Case |
|-------|-------------|----------|
| AWS Parameters and Secrets | Access Parameter Store and Secrets Manager | Configuration management |
| AWS AppConfig | Feature flags and configuration | Dynamic configuration |
| AWS Lambda Insights | Enhanced monitoring | Performance monitoring |

### Using AWS Parameters and Secrets Layer

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.12
      Layers:
        # AWS Parameters and Secrets Lambda Extension
        - arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:11
      Environment:
        Variables:
          PARAMETERS_SECRETS_EXTENSION_HTTP_PORT: 2773
          SSM_PARAMETER_STORE_TTL: 300
```

## Best Practices

### 1. Layer Sizing

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER SIZE GUIDELINES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Total Size Limit: 250 MB (unzipped)                       │  │
│  │                                                            │  │
│  │ Function Code  │ Layer 1 │ Layer 2 │ Layer 3 │ ... │ ≤ 250MB │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Recommendations:                                                │
│  • Keep layers focused on specific functionality                 │
│  • Combine small related dependencies into single layer          │
│  • Split large dependency sets across multiple layers            │
│  • Consider cold start impact of large layers                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Versioning Strategy

- Use semantic versioning for layer descriptions
- Document breaking changes between versions
- Test new layer versions before updating production functions
- Maintain old versions until all functions are migrated

### 3. Organization

```bash
# Recommended layer structure
layers/
├── shared-utils/
│   └── python/
│       ├── shared_utils.py
│       ├── db_utils.py
│       └── requirements.txt
├── data-processing/
│   └── python/
│       ├── requirements.txt  # pandas, numpy
│       └── data_helpers.py
└── external-apis/
    └── python/
        ├── requirements.txt  # requests, aiohttp
        └── api_client.py
```

### 4. Testing Layers

```python
# test_layer.py
import sys
sys.path.insert(0, './python')  # Add layer path

from shared_utils import create_response, success_response, validate_required_fields, ValidationError
import pytest

def test_create_response():
    response = create_response(200, {'message': 'test'})
    assert response['statusCode'] == 200
    assert 'Content-Type' in response['headers']

def test_success_response():
    response = success_response({'id': '123'})
    body = json.loads(response['body'])
    assert body['success'] == True
    assert body['data']['id'] == '123'

def test_validate_required_fields():
    with pytest.raises(ValidationError):
        validate_required_fields({'name': 'test'}, ['name', 'email'])
```

## Summary

### Key Takeaways

1. **Layers enable code reuse**: Share dependencies across functions
2. **Maximum 5 layers**: Per function limit
3. **250 MB limit**: Total unzipped size (function + layers)
4. **Immutable versions**: Each publish creates new version
5. **Extracted to /opt**: Layers available in /opt directory

### Layer Selection Guide

| Scenario | Recommendation |
|----------|----------------|
| Shared dependencies | Create dependency layer |
| Common utilities | Create shared code layer |
| ML/Data libraries | Create specialized layer |
| Custom runtime | Create runtime layer |
| AWS SDKs | Usually not needed (included) |

### Next Steps

Continue to [09-lambda-containers.md](./09-lambda-containers.md) to learn about deploying Lambda functions as container images.
