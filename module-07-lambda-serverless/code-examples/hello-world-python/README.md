# Hello World Lambda - Python

A basic AWS Lambda function demonstrating fundamental Lambda concepts.

## Overview

This function demonstrates:
- Event and context handling
- CloudWatch logging
- API Gateway integration
- CORS headers for web applications
- Local testing patterns

## Files

- `lambda_function.py` - Main Lambda function code

## Deployment

### Using AWS CLI

```bash
# Zip the function
zip function.zip lambda_function.py

# Create the function
aws lambda create-function \
    --function-name hello-world-python \
    --runtime python3.12 \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role

# Update existing function
aws lambda update-function-code \
    --function-name hello-world-python \
    --zip-file fileb://function.zip
```

### Using AWS Console

1. Navigate to Lambda in AWS Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Enter function name: `hello-world-python`
5. Select Runtime: Python 3.12
6. Create or select an execution role
7. Copy the code from `lambda_function.py` into the editor
8. Click "Deploy"

## Testing

### Direct Invocation

```bash
aws lambda invoke \
    --function-name hello-world-python \
    --payload '{"name": "Developer"}' \
    --cli-binary-format raw-in-base64-out \
    response.json

cat response.json
```

### With API Gateway

```bash
curl "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/hello?name=Developer"
```

### Local Testing

```bash
python lambda_function.py
```

## Event Formats

### Direct Invocation
```json
{
    "name": "Developer"
}
```

### API Gateway (Query String)
```json
{
    "queryStringParameters": {
        "name": "Developer"
    }
}
```

### API Gateway (POST Body)
```json
{
    "body": "{\"name\": \"Developer\"}"
}
```

## Response Format

```json
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": "{\"message\": \"Hello, Developer!\"}"
}
```

## IAM Role Requirements

Minimum permissions (AWSLambdaBasicExecutionRole):
```json
{
    "Version": "2012-10-17",
    "Statement": [
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

## Cleanup

```bash
aws lambda delete-function --function-name hello-world-python
```
