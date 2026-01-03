# API Handler Lambda - Python

A RESTful API handler demonstrating CRUD operations with DynamoDB.

## Overview

This function demonstrates:
- RESTful API design with Lambda
- DynamoDB CRUD operations
- Request validation
- Error handling patterns
- API Gateway integration
- CORS configuration

## Files

- `lambda_function.py` - Main Lambda function code
- `requirements.txt` - Python dependencies

## Prerequisites

### DynamoDB Table

Create a DynamoDB table with the following configuration:

```bash
aws dynamodb create-table \
    --table-name items \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### IAM Role

The Lambda execution role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/items"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /items | Get all items |
| GET | /items/{id} | Get single item |
| POST | /items | Create new item |
| PUT | /items/{id} | Update item |
| DELETE | /items/{id} | Delete item |

## Deployment

### Package and Deploy

```bash
# Create deployment package
pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package && zip -r ../function.zip . && cd ..

# Create function
aws lambda create-function \
    --function-name api-handler-python \
    --runtime python3.12 \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-dynamodb-role \
    --environment Variables={TABLE_NAME=items}

# Create API Gateway
aws apigateway create-rest-api \
    --name "Items API" \
    --description "CRUD API for items"
```

## Request/Response Examples

### Create Item (POST /items)

Request:
```json
{
    "name": "Widget",
    "description": "A useful widget",
    "price": 29.99
}
```

Response (201):
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Widget",
    "description": "A useful widget",
    "price": 29.99,
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
}
```

### Get All Items (GET /items)

Response (200):
```json
{
    "items": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Widget",
            "price": 29.99
        }
    ],
    "count": 1
}
```

### Update Item (PUT /items/{id})

Request:
```json
{
    "price": 34.99
}
```

Response (200):
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Widget",
    "price": 34.99,
    "updated_at": "2024-01-15T11:00:00.000Z"
}
```

### Error Response

```json
{
    "error": "Item not found"
}
```

## Testing

### With AWS CLI

```bash
# Create item
aws lambda invoke \
    --function-name api-handler-python \
    --payload '{"httpMethod":"POST","path":"/items","body":"{\"name\":\"Test\",\"price\":10}"}' \
    --cli-binary-format raw-in-base64-out \
    response.json

# Get all items
aws lambda invoke \
    --function-name api-handler-python \
    --payload '{"httpMethod":"GET","path":"/items"}' \
    --cli-binary-format raw-in-base64-out \
    response.json
```

### With curl (via API Gateway)

```bash
# Create item
curl -X POST https://API_ID.execute-api.REGION.amazonaws.com/prod/items \
    -H "Content-Type: application/json" \
    -d '{"name":"Widget","price":29.99}'

# Get all items
curl https://API_ID.execute-api.REGION.amazonaws.com/prod/items

# Get single item
curl https://API_ID.execute-api.REGION.amazonaws.com/prod/items/{id}

# Update item
curl -X PUT https://API_ID.execute-api.REGION.amazonaws.com/prod/items/{id} \
    -H "Content-Type: application/json" \
    -d '{"price":39.99}'

# Delete item
curl -X DELETE https://API_ID.execute-api.REGION.amazonaws.com/prod/items/{id}
```

## Cleanup

```bash
# Delete Lambda function
aws lambda delete-function --function-name api-handler-python

# Delete DynamoDB table
aws dynamodb delete-table --table-name items

# Delete API Gateway (get ID first)
aws apigateway get-rest-apis
aws apigateway delete-rest-api --rest-api-id YOUR_API_ID
```
