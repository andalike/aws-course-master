# AWS Step Functions

## Introduction

AWS Step Functions is a serverless orchestration service that lets you combine AWS Lambda functions and other AWS services to build business-critical applications. It provides a visual workflow to coordinate the components of distributed applications and microservices.

## Step Functions Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    STEP FUNCTIONS OVERVIEW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input ──▶ State Machine ──▶ Output                              │
│                 │                                                │
│                 ▼                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │           STATE MACHINE DEFINITION (ASL)                     ││
│  │                                                              ││
│  │  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐      ││
│  │  │Start │──▶│Task 1│──▶│Choice│──▶│Task 2│──▶│ End  │      ││
│  │  └──────┘   └──────┘   └──┬───┘   └──────┘   └──────┘      ││
│  │                           │                                  ││
│  │                           ▼                                  ││
│  │                      ┌──────┐                                ││
│  │                      │Task 3│                                ││
│  │                      └──────┘                                ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Types

### Standard Workflows

- **Duration**: Up to 1 year
- **Execution**: Exactly-once execution
- **History**: Full execution history
- **Pricing**: Per state transition
- **Use cases**: Long-running, durable workflows

### Express Workflows

- **Duration**: Up to 5 minutes
- **Execution**: At-least-once (async) or at-most-once (sync)
- **History**: CloudWatch Logs only
- **Pricing**: Per execution duration
- **Use cases**: High-volume, short-duration workflows

| Feature | Standard | Express |
|---------|----------|---------|
| Max duration | 1 year | 5 minutes |
| Execution model | Exactly-once | At-least/At-most once |
| State transitions | 25,000 per execution | Unlimited |
| Execution history | 90 days | CloudWatch Logs |
| Pricing | Per transition | Per duration/memory |

## State Types

### Task State

Executes work using Lambda, AWS services, or activities.

```json
{
  "ProcessOrder": {
    "Type": "Task",
    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process-order",
    "InputPath": "$.order",
    "ResultPath": "$.result",
    "OutputPath": "$",
    "Next": "NotifyCustomer",
    "Retry": [
      {
        "ErrorEquals": ["Lambda.ServiceException"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }
    ],
    "Catch": [
      {
        "ErrorEquals": ["States.ALL"],
        "Next": "HandleError"
      }
    ]
  }
}
```

### Choice State

Branches execution based on conditions.

```json
{
  "CheckOrderAmount": {
    "Type": "Choice",
    "Choices": [
      {
        "Variable": "$.amount",
        "NumericGreaterThan": 1000,
        "Next": "RequireApproval"
      },
      {
        "Variable": "$.amount",
        "NumericGreaterThan": 100,
        "Next": "StandardProcessing"
      }
    ],
    "Default": "ExpressProcessing"
  }
}
```

#### Choice Operators

| Operator | Description |
|----------|-------------|
| `StringEquals` | Exact string match |
| `StringLessThan` | String comparison |
| `StringMatches` | Pattern matching with wildcards |
| `NumericEquals` | Exact number match |
| `NumericGreaterThan` | Number comparison |
| `BooleanEquals` | Boolean comparison |
| `TimestampEquals` | Timestamp comparison |
| `IsPresent` | Check if variable exists |
| `IsNull` | Check if null |
| `And`, `Or`, `Not` | Logical operators |

### Parallel State

Executes branches concurrently.

```json
{
  "ProcessInParallel": {
    "Type": "Parallel",
    "Branches": [
      {
        "StartAt": "SendEmail",
        "States": {
          "SendEmail": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:send-email",
            "End": true
          }
        }
      },
      {
        "StartAt": "SendSMS",
        "States": {
          "SendSMS": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:send-sms",
            "End": true
          }
        }
      },
      {
        "StartAt": "UpdateDatabase",
        "States": {
          "UpdateDatabase": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:update-db",
            "End": true
          }
        }
      }
    ],
    "Next": "CombineResults"
  }
}
```

### Map State

Iterates over an array and processes each item.

```json
{
  "ProcessItems": {
    "Type": "Map",
    "ItemsPath": "$.items",
    "MaxConcurrency": 10,
    "ItemProcessor": {
      "ProcessorConfig": {
        "Mode": "INLINE"
      },
      "StartAt": "ProcessItem",
      "States": {
        "ProcessItem": {
          "Type": "Task",
          "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process-item",
          "End": true
        }
      }
    },
    "ResultPath": "$.processedItems",
    "Next": "Complete"
  }
}
```

### Wait State

Delays execution for a specified time.

```json
{
  "WaitForApproval": {
    "Type": "Wait",
    "Seconds": 3600,
    "Next": "CheckApproval"
  }
}
```

```json
{
  "WaitUntilTimestamp": {
    "Type": "Wait",
    "TimestampPath": "$.scheduledTime",
    "Next": "Execute"
  }
}
```

### Pass State

Passes input to output, optionally transforming data.

```json
{
  "SetDefaults": {
    "Type": "Pass",
    "Result": {
      "status": "pending",
      "retryCount": 0
    },
    "ResultPath": "$.defaults",
    "Next": "ProcessOrder"
  }
}
```

### Succeed and Fail States

```json
{
  "Success": {
    "Type": "Succeed"
  },
  "OrderFailed": {
    "Type": "Fail",
    "Error": "OrderProcessingFailed",
    "Cause": "The order could not be processed"
  }
}
```

## Complete State Machine Example

### Order Processing Workflow

```json
{
  "Comment": "Order Processing State Machine",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:validate-order",
      "Next": "CheckInventory",
      "Catch": [
        {
          "ErrorEquals": ["ValidationError"],
          "Next": "OrderValidationFailed"
        }
      ]
    },
    "CheckInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:check-inventory",
      "Next": "IsInStock"
    },
    "IsInStock": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.inventory.available",
          "BooleanEquals": true,
          "Next": "CheckOrderAmount"
        }
      ],
      "Default": "OutOfStock"
    },
    "CheckOrderAmount": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.order.amount",
          "NumericGreaterThan": 1000,
          "Next": "RequireApproval"
        }
      ],
      "Default": "ProcessPayment"
    },
    "RequireApproval": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
      "Parameters": {
        "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123456789012/approval-queue",
        "MessageBody": {
          "orderId.$": "$.order.id",
          "amount.$": "$.order.amount",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "Next": "CheckApproval",
      "TimeoutSeconds": 86400
    },
    "CheckApproval": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.approved",
          "BooleanEquals": true,
          "Next": "ProcessPayment"
        }
      ],
      "Default": "OrderRejected"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process-payment",
      "Next": "NotifyAndShip",
      "Retry": [
        {
          "ErrorEquals": ["PaymentServiceError"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["PaymentFailed"],
          "Next": "PaymentFailed"
        }
      ]
    },
    "NotifyAndShip": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "SendConfirmation",
          "States": {
            "SendConfirmation": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789012:function:send-confirmation",
              "End": true
            }
          }
        },
        {
          "StartAt": "InitiateShipment",
          "States": {
            "InitiateShipment": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789012:function:initiate-shipment",
              "End": true
            }
          }
        },
        {
          "StartAt": "UpdateAnalytics",
          "States": {
            "UpdateAnalytics": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789012:function:update-analytics",
              "End": true
            }
          }
        }
      ],
      "Next": "OrderComplete"
    },
    "OrderComplete": {
      "Type": "Succeed"
    },
    "OutOfStock": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:notify-out-of-stock",
      "Next": "OrderFailed"
    },
    "OrderValidationFailed": {
      "Type": "Fail",
      "Error": "ValidationError",
      "Cause": "Order validation failed"
    },
    "OrderRejected": {
      "Type": "Fail",
      "Error": "OrderRejected",
      "Cause": "Order was rejected during approval"
    },
    "PaymentFailed": {
      "Type": "Fail",
      "Error": "PaymentFailed",
      "Cause": "Payment processing failed"
    },
    "OrderFailed": {
      "Type": "Fail",
      "Error": "OrderFailed",
      "Cause": "Order processing failed"
    }
  }
}
```

## Error Handling

### Retry Configuration

```json
{
  "ProcessOrder": {
    "Type": "Task",
    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process",
    "Retry": [
      {
        "ErrorEquals": ["States.Timeout"],
        "IntervalSeconds": 3,
        "MaxAttempts": 2,
        "BackoffRate": 1.5
      },
      {
        "ErrorEquals": ["Lambda.ServiceException", "Lambda.TooManyRequestsException"],
        "IntervalSeconds": 1,
        "MaxAttempts": 5,
        "BackoffRate": 2.0
      },
      {
        "ErrorEquals": ["States.ALL"],
        "IntervalSeconds": 5,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }
    ],
    "Next": "Complete"
  }
}
```

### Error Types

| Error | Description |
|-------|-------------|
| `States.ALL` | Matches all errors |
| `States.Timeout` | Task timed out |
| `States.TaskFailed` | Task returned failure |
| `States.Permissions` | Insufficient permissions |
| `States.ResultPathMatchFailure` | ResultPath couldn't be applied |
| `States.DataLimitExceeded` | Output exceeded 256KB |
| `Lambda.ServiceException` | Lambda service error |
| `Lambda.TooManyRequestsException` | Lambda throttled |

### Catch Configuration

```json
{
  "ProcessOrder": {
    "Type": "Task",
    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process",
    "Catch": [
      {
        "ErrorEquals": ["ValidationError"],
        "ResultPath": "$.error",
        "Next": "HandleValidationError"
      },
      {
        "ErrorEquals": ["States.Timeout"],
        "ResultPath": "$.error",
        "Next": "HandleTimeout"
      },
      {
        "ErrorEquals": ["States.ALL"],
        "ResultPath": "$.error",
        "Next": "HandleGenericError"
      }
    ],
    "Next": "Complete"
  }
}
```

## Input/Output Processing

### Path Expressions

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT/OUTPUT FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  State Input                                                     │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐                                                │
│  │ InputPath   │  Select subset of input                        │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Parameters  │  Add/transform data                            │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │    Task     │  Execute task                                  │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ResultSelector│ Transform task result                         │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ ResultPath  │  Merge result with input                       │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ OutputPath  │  Select final output                           │
│  └──────┬──────┘                                                │
│         ▼                                                        │
│  State Output                                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Example

```json
{
  "ProcessOrder": {
    "Type": "Task",
    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:process",
    "InputPath": "$.order",
    "Parameters": {
      "orderId.$": "$.id",
      "items.$": "$.items",
      "metadata": {
        "processedAt.$": "$$.State.EnteredTime",
        "executionId.$": "$$.Execution.Id"
      }
    },
    "ResultSelector": {
      "status.$": "$.status",
      "trackingNumber.$": "$.tracking.number"
    },
    "ResultPath": "$.orderResult",
    "OutputPath": "$",
    "Next": "Complete"
  }
}
```

### Context Object ($$)

```json
{
  "Execution": {
    "Id": "arn:aws:states:us-east-1:123456789012:execution:StateMachine:execution-id",
    "Input": { },
    "Name": "execution-name",
    "RoleArn": "arn:aws:iam::123456789012:role/...",
    "StartTime": "2024-01-15T12:00:00Z"
  },
  "State": {
    "EnteredTime": "2024-01-15T12:00:05Z",
    "Name": "ProcessOrder",
    "RetryCount": 0
  },
  "StateMachine": {
    "Id": "arn:aws:states:us-east-1:123456789012:stateMachine:StateMachine",
    "Name": "StateMachine"
  },
  "Task": {
    "Token": "task-token-123"
  }
}
```

## Service Integrations

### Direct Lambda Integration

```json
{
  "InvokeLambda": {
    "Type": "Task",
    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
    "Next": "Complete"
  }
}
```

### Optimized Lambda Integration

```json
{
  "InvokeLambda": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "arn:aws:lambda:us-east-1:123456789012:function:my-function",
      "Payload.$": "$"
    },
    "Next": "Complete"
  }
}
```

### DynamoDB Integration

```json
{
  "PutItem": {
    "Type": "Task",
    "Resource": "arn:aws:states:::dynamodb:putItem",
    "Parameters": {
      "TableName": "Orders",
      "Item": {
        "orderId": { "S.$": "$.orderId" },
        "status": { "S": "processing" },
        "createdAt": { "S.$": "$$.State.EnteredTime" }
      }
    },
    "Next": "Complete"
  }
}
```

### SNS Integration

```json
{
  "PublishNotification": {
    "Type": "Task",
    "Resource": "arn:aws:states:::sns:publish",
    "Parameters": {
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:notifications",
      "Message": {
        "orderId.$": "$.orderId",
        "status": "completed"
      },
      "Subject": "Order Completed"
    },
    "Next": "Complete"
  }
}
```

### SQS Integration

```json
{
  "SendToQueue": {
    "Type": "Task",
    "Resource": "arn:aws:states:::sqs:sendMessage",
    "Parameters": {
      "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123456789012/orders",
      "MessageBody.$": "States.JsonToString($)"
    },
    "Next": "Complete"
  }
}
```

### Callback Pattern (Wait for Task Token)

```json
{
  "WaitForCallback": {
    "Type": "Task",
    "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
    "Parameters": {
      "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123456789012/callback-queue",
      "MessageBody": {
        "input.$": "$",
        "taskToken.$": "$$.Task.Token"
      }
    },
    "TimeoutSeconds": 3600,
    "Next": "ProcessResult"
  }
}
```

**Callback handler:**

```python
import boto3
import json

sfn = boto3.client('stepfunctions')

def callback_handler(event, context):
    # Process the message
    for record in event['Records']:
        body = json.loads(record['body'])
        task_token = body['taskToken']
        input_data = body['input']

        try:
            # Do processing
            result = process_task(input_data)

            # Send success callback
            sfn.send_task_success(
                taskToken=task_token,
                output=json.dumps(result)
            )
        except Exception as e:
            # Send failure callback
            sfn.send_task_failure(
                taskToken=task_token,
                error='ProcessingError',
                cause=str(e)
            )
```

## SAM Template for Step Functions

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  OrderStateMachine:
    Type: AWS::Serverless::StateMachine
    Properties:
      Name: order-processing
      Type: STANDARD
      DefinitionUri: statemachine/order-processing.asl.json
      DefinitionSubstitutions:
        ValidateOrderFunctionArn: !GetAtt ValidateOrderFunction.Arn
        ProcessPaymentFunctionArn: !GetAtt ProcessPaymentFunction.Arn
        NotifyFunctionArn: !GetAtt NotifyFunction.Arn
      Policies:
        - LambdaInvokePolicy:
            FunctionName: !Ref ValidateOrderFunction
        - LambdaInvokePolicy:
            FunctionName: !Ref ProcessPaymentFunction
        - LambdaInvokePolicy:
            FunctionName: !Ref NotifyFunction
        - DynamoDBWritePolicy:
            TableName: !Ref OrdersTable

  ValidateOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: validate.handler
      Runtime: python3.12
      CodeUri: src/

  ProcessPaymentFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: payment.handler
      Runtime: python3.12
      CodeUri: src/

  NotifyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: notify.handler
      Runtime: python3.12
      CodeUri: src/

  OrdersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: orders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH
```

### State Machine Definition with Substitutions

```json
{
  "Comment": "Order Processing",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "${ValidateOrderFunctionArn}",
      "Next": "ProcessPayment"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "${ProcessPaymentFunctionArn}",
      "Next": "Notify"
    },
    "Notify": {
      "Type": "Task",
      "Resource": "${NotifyFunctionArn}",
      "End": true
    }
  }
}
```

## CLI Operations

```bash
# Create state machine
aws stepfunctions create-state-machine \
    --name "order-processing" \
    --definition file://definition.json \
    --role-arn arn:aws:iam::123456789012:role/StepFunctionsRole \
    --type STANDARD

# Start execution
aws stepfunctions start-execution \
    --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:order-processing \
    --input '{"orderId": "ORD-001", "amount": 99.99}'

# Describe execution
aws stepfunctions describe-execution \
    --execution-arn arn:aws:states:us-east-1:123456789012:execution:order-processing:exec-123

# Get execution history
aws stepfunctions get-execution-history \
    --execution-arn arn:aws:states:us-east-1:123456789012:execution:order-processing:exec-123

# List executions
aws stepfunctions list-executions \
    --state-machine-arn arn:aws:states:us-east-1:123456789012:stateMachine:order-processing \
    --status-filter RUNNING
```

## Best Practices

### 1. Use Service Integrations

```json
// Prefer this (optimized integration)
{
  "Resource": "arn:aws:states:::dynamodb:putItem",
  "Parameters": { ... }
}

// Over this (Lambda wrapper)
{
  "Resource": "arn:aws:lambda:...:function:dynamodb-wrapper"
}
```

### 2. Handle Errors Appropriately

```json
{
  "Retry": [
    {
      "ErrorEquals": ["States.Timeout", "Lambda.TooManyRequestsException"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2.0
    }
  ],
  "Catch": [
    {
      "ErrorEquals": ["States.ALL"],
      "ResultPath": "$.error",
      "Next": "ErrorHandler"
    }
  ]
}
```

### 3. Use Express Workflows for High Volume

For workflows that:
- Complete in under 5 minutes
- Don't require exactly-once semantics
- Need high throughput

### 4. Keep State Data Small

- Maximum 256 KB per state input/output
- Use S3 for large payloads and pass references

## Summary

### Key Takeaways

1. **State machine orchestration**: Visual workflow coordination
2. **Multiple state types**: Task, Choice, Parallel, Map, Wait, Pass
3. **Built-in error handling**: Retry and Catch configurations
4. **Service integrations**: Direct integration with 200+ AWS services
5. **Two workflow types**: Standard for durability, Express for speed

### When to Use Step Functions

| Use Case | Step Functions Fit |
|----------|-------------------|
| Multi-step workflows | Excellent |
| Human approval processes | Excellent |
| Error handling/retry | Excellent |
| Long-running processes | Excellent |
| Simple Lambda chains | Consider EventBridge |
| Real-time processing | Consider Kinesis |

### Next Steps

Continue to [08-sam-framework.md](./08-sam-framework.md) to learn about deploying serverless applications with AWS SAM.
