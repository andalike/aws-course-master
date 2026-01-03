"""
AWS Lambda Hello World Example - Python

This is a basic Lambda function that demonstrates:
- Event handling
- Context usage
- Logging
- Response formatting

Use Case: Getting started with Lambda, understanding the basics
"""

import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main Lambda handler function.

    Args:
        event (dict): The event data passed to the function.
                      Could be from API Gateway, S3, SNS, etc.
        context (LambdaContext): Runtime information about the function.

    Returns:
        dict: Response object (formatted for API Gateway if used as API endpoint)
    """

    # Log the incoming event
    logger.info(f"Received event: {json.dumps(event)}")

    # Log context information
    logger.info(f"Function name: {context.function_name}")
    logger.info(f"Request ID: {context.aws_request_id}")
    logger.info(f"Remaining time: {context.get_remaining_time_in_millis()}ms")

    # Extract name from event (supports both direct invocation and API Gateway)
    name = "World"

    # Check for direct invocation with 'name' in event
    if "name" in event:
        name = event["name"]

    # Check for API Gateway proxy integration
    elif "queryStringParameters" in event and event["queryStringParameters"]:
        name = event["queryStringParameters"].get("name", "World")

    # Check for API Gateway body (POST request)
    elif "body" in event and event["body"]:
        try:
            body = json.loads(event["body"])
            name = body.get("name", "World")
        except json.JSONDecodeError:
            logger.warning("Could not parse request body as JSON")

    # Build the response message
    message = f"Hello, {name}! Welcome to AWS Lambda."

    # Log the response
    logger.info(f"Returning message: {message}")

    # Return response formatted for API Gateway
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Enable CORS
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
        },
        "body": json.dumps({
            "message": message,
            "input_event": event,
            "function_info": {
                "function_name": context.function_name,
                "memory_limit_mb": context.memory_limit_in_mb,
                "request_id": context.aws_request_id,
                "log_group": context.log_group_name,
                "log_stream": context.log_stream_name
            }
        })
    }

    return response


# For local testing
if __name__ == "__main__":
    # Mock event and context for local testing
    class MockContext:
        function_name = "hello-world-python"
        aws_request_id = "test-request-id-12345"
        memory_limit_in_mb = 128
        log_group_name = "/aws/lambda/hello-world-python"
        log_stream_name = "2024/01/15/[$LATEST]abc123"

        def get_remaining_time_in_millis(self):
            return 30000

    # Test event
    test_event = {
        "name": "Developer"
    }

    # Test API Gateway event
    api_gateway_event = {
        "queryStringParameters": {
            "name": "API Tester"
        }
    }

    print("=== Testing Direct Invocation ===")
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(json.loads(result["body"]), indent=2))

    print("\n=== Testing API Gateway Event ===")
    result = lambda_handler(api_gateway_event, MockContext())
    print(json.dumps(json.loads(result["body"]), indent=2))
