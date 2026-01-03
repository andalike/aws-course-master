"""
AWS Lambda API Handler Example - Python

This Lambda function demonstrates:
- RESTful API handling with API Gateway
- CRUD operations with DynamoDB
- Request validation
- Error handling
- Environment variables

Use Case: Building serverless REST APIs
"""

import json
import os
import logging
import uuid
from datetime import datetime
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME", "items")
table = dynamodb.Table(TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal types from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def create_response(status_code, body, headers=None):
    """Create a standardized API Gateway response."""
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    if headers:
        default_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body, cls=DecimalEncoder) if body else ""
    }


def validate_item(item):
    """Validate item data."""
    required_fields = ["name"]
    errors = []

    for field in required_fields:
        if field not in item or not item[field]:
            errors.append(f"Missing required field: {field}")

    if "price" in item:
        try:
            price = float(item["price"])
            if price < 0:
                errors.append("Price cannot be negative")
        except (TypeError, ValueError):
            errors.append("Price must be a number")

    return errors


def get_all_items():
    """Get all items from DynamoDB."""
    try:
        response = table.scan()
        items = response.get("Items", [])

        # Handle pagination for large datasets
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        logger.info(f"Retrieved {len(items)} items")
        return create_response(200, {"items": items, "count": len(items)})

    except ClientError as e:
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        return create_response(500, {"error": "Failed to retrieve items"})


def get_item(item_id):
    """Get a single item by ID."""
    try:
        response = table.get_item(Key={"id": item_id})
        item = response.get("Item")

        if not item:
            return create_response(404, {"error": f"Item {item_id} not found"})

        logger.info(f"Retrieved item: {item_id}")
        return create_response(200, item)

    except ClientError as e:
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        return create_response(500, {"error": "Failed to retrieve item"})


def create_item(body):
    """Create a new item."""
    try:
        item_data = json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})

    # Validate item
    errors = validate_item(item_data)
    if errors:
        return create_response(400, {"errors": errors})

    # Create item with generated ID and timestamps
    item = {
        "id": str(uuid.uuid4()),
        "name": item_data["name"],
        "description": item_data.get("description", ""),
        "price": Decimal(str(item_data.get("price", 0))),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        table.put_item(Item=item)
        logger.info(f"Created item: {item['id']}")
        return create_response(201, item)

    except ClientError as e:
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        return create_response(500, {"error": "Failed to create item"})


def update_item(item_id, body):
    """Update an existing item."""
    try:
        item_data = json.loads(body) if isinstance(body, str) else body
    except json.JSONDecodeError:
        return create_response(400, {"error": "Invalid JSON in request body"})

    # Build update expression dynamically
    update_parts = []
    expression_values = {}
    expression_names = {}

    if "name" in item_data:
        update_parts.append("#n = :name")
        expression_values[":name"] = item_data["name"]
        expression_names["#n"] = "name"

    if "description" in item_data:
        update_parts.append("description = :description")
        expression_values[":description"] = item_data["description"]

    if "price" in item_data:
        update_parts.append("price = :price")
        expression_values[":price"] = Decimal(str(item_data["price"]))

    # Always update the updated_at timestamp
    update_parts.append("updated_at = :updated_at")
    expression_values[":updated_at"] = datetime.utcnow().isoformat()

    if not update_parts:
        return create_response(400, {"error": "No fields to update"})

    try:
        response = table.update_item(
            Key={"id": item_id},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names if expression_names else None,
            ReturnValues="ALL_NEW",
            ConditionExpression="attribute_exists(id)"
        )

        logger.info(f"Updated item: {item_id}")
        return create_response(200, response.get("Attributes"))

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return create_response(404, {"error": f"Item {item_id} not found"})
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        return create_response(500, {"error": "Failed to update item"})


def delete_item(item_id):
    """Delete an item by ID."""
    try:
        table.delete_item(
            Key={"id": item_id},
            ConditionExpression="attribute_exists(id)"
        )
        logger.info(f"Deleted item: {item_id}")
        return create_response(204, None)

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return create_response(404, {"error": f"Item {item_id} not found"})
        logger.error(f"DynamoDB error: {e.response['Error']['Message']}")
        return create_response(500, {"error": "Failed to delete item"})


def lambda_handler(event, context):
    """
    Main Lambda handler for API Gateway requests.

    Supports the following endpoints:
    - GET /items - Get all items
    - GET /items/{id} - Get a single item
    - POST /items - Create a new item
    - PUT /items/{id} - Update an item
    - DELETE /items/{id} - Delete an item
    """

    logger.info(f"Received event: {json.dumps(event)}")

    # Handle OPTIONS for CORS preflight
    http_method = event.get("httpMethod", event.get("requestContext", {}).get("http", {}).get("method", ""))
    if http_method == "OPTIONS":
        return create_response(200, {"message": "OK"})

    # Get path and path parameters
    path = event.get("path", event.get("rawPath", "/"))
    path_parameters = event.get("pathParameters") or {}
    item_id = path_parameters.get("id")

    # Route request to appropriate handler
    try:
        if http_method == "GET":
            if item_id:
                return get_item(item_id)
            return get_all_items()

        elif http_method == "POST":
            body = event.get("body", "{}")
            return create_item(body)

        elif http_method == "PUT":
            if not item_id:
                return create_response(400, {"error": "Item ID required for update"})
            body = event.get("body", "{}")
            return update_item(item_id, body)

        elif http_method == "DELETE":
            if not item_id:
                return create_response(400, {"error": "Item ID required for delete"})
            return delete_item(item_id)

        else:
            return create_response(405, {"error": f"Method {http_method} not allowed"})

    except Exception as e:
        logger.exception("Unexpected error")
        return create_response(500, {"error": "Internal server error"})


# For local testing
if __name__ == "__main__":
    import sys

    class MockContext:
        function_name = "api-handler-python"
        aws_request_id = "test-request-id"
        memory_limit_in_mb = 128

    # Test events
    test_events = {
        "get_all": {
            "httpMethod": "GET",
            "path": "/items"
        },
        "get_one": {
            "httpMethod": "GET",
            "path": "/items/123",
            "pathParameters": {"id": "123"}
        },
        "create": {
            "httpMethod": "POST",
            "path": "/items",
            "body": json.dumps({
                "name": "Test Item",
                "description": "A test item",
                "price": 29.99
            })
        },
        "update": {
            "httpMethod": "PUT",
            "path": "/items/123",
            "pathParameters": {"id": "123"},
            "body": json.dumps({
                "name": "Updated Item",
                "price": 39.99
            })
        },
        "delete": {
            "httpMethod": "DELETE",
            "path": "/items/123",
            "pathParameters": {"id": "123"}
        }
    }

    print("API Handler Test (requires DynamoDB table)")
    print("Set TABLE_NAME environment variable before running")
    print(f"Current TABLE_NAME: {TABLE_NAME}")
    print("\nTest events available:", list(test_events.keys()))
