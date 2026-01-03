# 08 - Amazon DynamoDB

## What is DynamoDB?

Amazon DynamoDB is a fully managed NoSQL database service that provides fast and predictable performance with seamless scalability. It's designed for applications that require consistent, single-digit millisecond latency at any scale.

```
+--------------------------------------------------------------------------------+
|                           DYNAMODB KEY BENEFITS                                 |
|                                                                                 |
|  +---------------------+  +---------------------+  +---------------------+      |
|  |    PERFORMANCE      |  |    SCALABILITY      |  |    AVAILABILITY     |      |
|  |                     |  |                     |  |                     |      |
|  |  Single-digit ms    |  |  Unlimited items    |  |  99.999% SLA        |      |
|  |  latency            |  |                     |  |  (Global Tables)    |      |
|  |                     |  |  Automatic scaling  |  |                     |      |
|  |  Millions of        |  |                     |  |  Multi-AZ           |      |
|  |  requests/second    |  |  Petabyte scale     |  |  replication        |      |
|  +---------------------+  +---------------------+  +---------------------+      |
|                                                                                 |
|  +---------------------+  +---------------------+  +---------------------+      |
|  |    SERVERLESS       |  |    SECURITY         |  |    INTEGRATION      |      |
|  |                     |  |                     |  |                     |      |
|  |  No servers to      |  |  Encryption at      |  |  AWS Lambda         |      |
|  |  manage             |  |  rest and transit   |  |  triggers           |      |
|  |                     |  |                     |  |                     |      |
|  |  Pay per request    |  |  IAM integration    |  |  EventBridge        |      |
|  |  or provisioned     |  |  Fine-grained       |  |  CloudWatch         |      |
|  +---------------------+  +---------------------+  +---------------------+      |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## NoSQL vs SQL Concepts

### Comparison

| Concept | Relational (SQL) | DynamoDB (NoSQL) |
|---------|------------------|------------------|
| Structure | Tables with fixed schema | Tables with flexible schema |
| Data Unit | Row | Item |
| Data Element | Column | Attribute |
| Primary Key | Primary key (single or composite) | Partition key or Partition + Sort key |
| Relationships | Foreign keys, JOINs | Denormalization, single-table design |
| Schema | Fixed, defined upfront | Flexible, schemaless |
| Scaling | Vertical (scale up) | Horizontal (scale out) |
| Transactions | ACID by default | ACID available (TransactWriteItems) |
| Query Language | SQL | PartiQL, SDK, API |

### When to Choose DynamoDB

```
+---------------------------+------------------------------------------+
|       USE DYNAMODB        |          USE RELATIONAL DB               |
+---------------------------+------------------------------------------+
| - High-scale applications | - Complex JOINs and relationships        |
| - Serverless backends     | - Ad-hoc queries                         |
| - Gaming leaderboards     | - OLAP workloads                         |
| - Session stores          | - Strong consistency everywhere          |
| - Shopping carts          | - Existing SQL expertise                 |
| - IoT data ingestion      | - Complex transactions                   |
| - Real-time bidding       | - Reporting and analytics                |
| - Content management      | - Legacy application support             |
+---------------------------+------------------------------------------+
```

## DynamoDB Core Concepts

### Tables, Items, and Attributes

```
+--------------------------------------------------------------------------------+
|                              DYNAMODB TABLE                                     |
|  Table Name: Users                                                             |
+--------------------------------------------------------------------------------+
|                                                                                 |
|  +--------------------------------------------------------------------------+  |
|  |                            ITEM 1                                         |  |
|  |  +------------+  +-------------+  +------------------+  +-------------+  |  |
|  |  | UserID     |  | Name        |  | Email            |  | Age         |  |  |
|  |  | (PK)       |  |             |  |                  |  |             |  |  |
|  |  | "U001"     |  | "John Doe"  |  | "john@email.com" |  | 30          |  |  |
|  |  +------------+  +-------------+  +------------------+  +-------------+  |  |
|  +--------------------------------------------------------------------------+  |
|                                                                                 |
|  +--------------------------------------------------------------------------+  |
|  |                            ITEM 2                                         |  |
|  |  +------------+  +-------------+  +------------------+  +-------------+  |  |
|  |  | UserID     |  | Name        |  | Email            |  | Phone       |  |  |
|  |  | (PK)       |  |             |  |                  |  | (optional)  |  |  |
|  |  | "U002"     |  | "Jane Doe"  |  | "jane@email.com" |  | "555-1234"  |  |  |
|  |  +------------+  +-------------+  +------------------+  +-------------+  |  |
|  +--------------------------------------------------------------------------+  |
|                                                                                 |
|  Note: Each item can have different attributes (schemaless)                    |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Attribute Data Types

| Category | Type | Description | Example |
|----------|------|-------------|---------|
| **Scalar** | String (S) | UTF-8 text | `"Hello World"` |
| | Number (N) | Numeric | `123`, `3.14` |
| | Binary (B) | Binary data | Base64 encoded |
| | Boolean (BOOL) | True/False | `true`, `false` |
| | Null (NULL) | Null value | `null` |
| **Document** | List (L) | Ordered collection | `["a", "b", "c"]` |
| | Map (M) | Nested attributes | `{"name": "John", "age": 30}` |
| **Set** | String Set (SS) | Set of strings | `["a", "b", "c"]` |
| | Number Set (NS) | Set of numbers | `[1, 2, 3]` |
| | Binary Set (BS) | Set of binaries | Binary values |

## Primary Keys

### Simple Primary Key (Partition Key Only)

```
+--------------------------------------------------------------------------------+
|                         SIMPLE PRIMARY KEY                                      |
|                                                                                 |
|  Table: Products                                                                |
|  Partition Key: ProductID                                                       |
|                                                                                 |
|  +-------------------+------------------+------------------+------------------+ |
|  | ProductID (PK)    | Name             | Price            | Category         | |
|  +-------------------+------------------+------------------+------------------+ |
|  | PROD-001          | Widget A         | 19.99            | Electronics      | |
|  | PROD-002          | Widget B         | 29.99            | Electronics      | |
|  | PROD-003          | Gadget X         | 49.99            | Gadgets          | |
|  +-------------------+------------------+------------------+------------------+ |
|                                                                                 |
|  - Each item must have a UNIQUE partition key                                  |
|  - Direct access via GetItem using partition key                               |
|  - Data distributed across partitions based on hash of PK                      |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Composite Primary Key (Partition Key + Sort Key)

```
+--------------------------------------------------------------------------------+
|                        COMPOSITE PRIMARY KEY                                    |
|                                                                                 |
|  Table: Orders                                                                  |
|  Partition Key: CustomerID                                                      |
|  Sort Key: OrderDate                                                            |
|                                                                                 |
|  +---------------+-----------------+------------------+------------------------+ |
|  | CustomerID    | OrderDate       | OrderID          | Total                  | |
|  | (PK)          | (SK)            |                  |                        | |
|  +---------------+-----------------+------------------+------------------------+ |
|  | C001          | 2024-01-15      | ORD-001          | 150.00                 | |
|  | C001          | 2024-02-20      | ORD-005          | 75.50                  | |
|  | C001          | 2024-03-10      | ORD-012          | 200.00                 | |
|  | C002          | 2024-01-20      | ORD-002          | 50.00                  | |
|  | C002          | 2024-02-25      | ORD-008          | 125.00                 | |
|  +---------------+-----------------+------------------+------------------------+ |
|                                                                                 |
|  - Same partition key can have multiple items (different sort keys)            |
|  - Items within a partition are stored sorted by sort key                      |
|  - Enables range queries: "All orders for C001 in January"                     |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Partition Key Design Best Practices

```
+--------------------------------------------------------------------------------+
|                    PARTITION KEY SELECTION                                      |
|                                                                                 |
|  GOOD PARTITION KEYS:                    BAD PARTITION KEYS:                   |
|  +----------------------------------+    +----------------------------------+  |
|  | - UserID (high cardinality)      |    | - Status ("Active"/"Inactive")  |  |
|  | - OrderID (unique)               |    | - Gender ("M"/"F")              |  |
|  | - DeviceID (many devices)        |    | - Country (few values)          |  |
|  | - SessionID (unique per session) |    | - Date only (leads to hot      |  |
|  +----------------------------------+    |   partitions on current date)   |  |
|                                          +----------------------------------+  |
|                                                                                 |
|  KEY PRINCIPLES:                                                                |
|  1. High cardinality - Many unique values                                      |
|  2. Uniform distribution - Even access pattern                                 |
|  3. Avoid hot partitions - No single key gets most traffic                    |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Secondary Indexes

### Global Secondary Index (GSI)

```
+--------------------------------------------------------------------------------+
|                      GLOBAL SECONDARY INDEX (GSI)                               |
|                                                                                 |
|  BASE TABLE: Orders                         GSI: Orders-by-Status              |
|  PK: OrderID                                PK: Status                          |
|                                             SK: OrderDate                       |
|                                                                                 |
|  +-------------+----------+--------+        +----------+-------------+--------+ |
|  | OrderID(PK) | Status   | Date   |        | Status   | OrderDate   | OrderID| |
|  +-------------+----------+--------+   -->  +----------+-------------+--------+ |
|  | ORD-001     | Pending  | Jan-15 |        | Pending  | Jan-15      | ORD-001| |
|  | ORD-002     | Shipped  | Jan-16 |        | Pending  | Feb-01      | ORD-003| |
|  | ORD-003     | Pending  | Feb-01 |        | Shipped  | Jan-16      | ORD-002| |
|  | ORD-004     | Delivered| Feb-10 |        | Delivered| Feb-10      | ORD-004| |
|  +-------------+----------+--------+        +----------+-------------+--------+ |
|                                                                                 |
|  GSI CHARACTERISTICS:                                                           |
|  +------------------------------------------------------------------+          |
|  | - Different partition key and/or sort key from base table        |          |
|  | - Can be created on existing tables                              |          |
|  | - Has its own provisioned throughput (separate from base table)  |          |
|  | - Eventually consistent reads only                               |          |
|  | - Maximum 20 GSIs per table                                      |          |
|  | - Can project all, some, or only key attributes                 |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Local Secondary Index (LSI)

```
+--------------------------------------------------------------------------------+
|                      LOCAL SECONDARY INDEX (LSI)                                |
|                                                                                 |
|  BASE TABLE: Orders                         LSI: Orders-by-Amount              |
|  PK: CustomerID                             PK: CustomerID (same)              |
|  SK: OrderDate                              SK: TotalAmount                    |
|                                                                                 |
|  +------------+----------+---------+        +------------+---------+----------+ |
|  | CustomerID | OrderDate| Amount  |        | CustomerID | Amount  | OrderDate| |
|  | (PK)       | (SK)     |         |   -->  | (PK)       | (SK)    |          | |
|  +------------+----------+---------+        +------------+---------+----------+ |
|  | C001       | Jan-15   | 150.00  |        | C001       | 75.50   | Feb-20   | |
|  | C001       | Feb-20   | 75.50   |        | C001       | 150.00  | Jan-15   | |
|  | C001       | Mar-10   | 200.00  |        | C001       | 200.00  | Mar-10   | |
|  +------------+----------+---------+        +------------+---------+----------+ |
|                                                                                 |
|  LSI CHARACTERISTICS:                                                           |
|  +------------------------------------------------------------------+          |
|  | - Same partition key as base table, different sort key           |          |
|  | - MUST be created at table creation time (cannot add later)     |          |
|  | - Shares provisioned throughput with base table                  |          |
|  | - Supports strongly consistent reads                             |          |
|  | - Maximum 5 LSIs per table                                       |          |
|  | - 10 GB limit per partition key value                           |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### GSI vs LSI Comparison

| Feature | Global Secondary Index (GSI) | Local Secondary Index (LSI) |
|---------|------------------------------|------------------------------|
| Partition Key | Any attribute | Same as base table |
| Sort Key | Any attribute | Different from base table |
| Creation Time | Any time | Table creation only |
| Throughput | Separate from base table | Shared with base table |
| Consistency | Eventually consistent only | Strongly consistent available |
| Maximum per Table | 20 | 5 |
| Size Limit | None | 10 GB per partition key |
| Projected Attributes | All, Keys Only, or Specific | All, Keys Only, or Specific |

## Capacity Modes

### On-Demand Capacity Mode

```
+--------------------------------------------------------------------------------+
|                         ON-DEMAND CAPACITY MODE                                 |
|                                                                                 |
|     Request Rate                                                                |
|           ^                                                                     |
|           |                    +---------+                                      |
|     10000 |                   /|         |\                                     |
|           |                  / |         | \                                    |
|      5000 |       +--------+  |         |  +--------+                          |
|           |      /         |  |         |          \                           |
|      1000 |-----+          +--+         +----------+------                     |
|           |                                                                     |
|           +---------------------------------------------------------> Time     |
|                                                                                 |
|  CHARACTERISTICS:                                                               |
|  +------------------------------------------------------------------+          |
|  | - Pay per request (read/write)                                   |          |
|  | - Automatic scaling to handle any traffic                        |          |
|  | - No capacity planning required                                  |          |
|  | - Best for unpredictable or spiky workloads                      |          |
|  | - Instantly handles sudden traffic spikes                        |          |
|  | - New tables start with on-demand by default                     |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  PRICING (Example - US East 1):                                                |
|  - Read Request Unit (RRU): $0.25 per million                                  |
|  - Write Request Unit (WRU): $1.25 per million                                 |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Provisioned Capacity Mode

```
+--------------------------------------------------------------------------------+
|                        PROVISIONED CAPACITY MODE                                |
|                                                                                 |
|     Capacity                                                                    |
|           ^                                                                     |
|           |       Provisioned: 5000 RCU                                        |
|     5000  |--------------------------------------------                        |
|           |        ^                                                            |
|           |        | Auto-scaling adjusts                                       |
|           |        |                                                            |
|     3000  |        +-- Actual usage varies                                     |
|           |                                                                     |
|     1000  |                                                                     |
|           +---------------------------------------------------------> Time     |
|                                                                                 |
|  CAPACITY UNITS:                                                                |
|  +------------------------------------------------------------------+          |
|  | Read Capacity Unit (RCU):                                        |          |
|  | - 1 RCU = 1 strongly consistent read/sec for item up to 4 KB    |          |
|  | - 1 RCU = 2 eventually consistent reads/sec for item up to 4 KB |          |
|  |                                                                   |          |
|  | Write Capacity Unit (WCU):                                       |          |
|  | - 1 WCU = 1 write/sec for item up to 1 KB                        |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  AUTO-SCALING:                                                                  |
|  - Set target utilization (e.g., 70%)                                          |
|  - Define minimum and maximum capacity                                          |
|  - DynamoDB adjusts capacity automatically                                      |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Capacity Calculation Examples

```python
# Example: Calculate required capacity

# READS
# Item size: 8 KB, 100 strongly consistent reads/second
# RCUs needed = (8 KB / 4 KB) * 100 = 200 RCUs

# Item size: 8 KB, 100 eventually consistent reads/second
# RCUs needed = (8 KB / 4 KB) * 100 / 2 = 100 RCUs

# WRITES
# Item size: 3 KB, 50 writes/second
# WCUs needed = ceil(3 / 1) * 50 = 150 WCUs

# Item size: 0.5 KB, 50 writes/second
# WCUs needed = ceil(0.5 / 1) * 50 = 50 WCUs (minimum 1 KB)
```

### Capacity Mode Comparison

| Aspect | On-Demand | Provisioned |
|--------|-----------|-------------|
| Best For | Unpredictable workloads | Predictable workloads |
| Pricing | Per request | Per hour (capacity) |
| Scaling | Instant, automatic | Auto-scaling (with delay) |
| Cost | Higher per request | Lower for steady traffic |
| Throttling Risk | Very low | Possible if under-provisioned |
| Reserved Capacity | Not available | Available (additional savings) |
| Burst Capacity | Unlimited | Limited burst pool |

## DynamoDB Streams

### Stream Architecture

```
+--------------------------------------------------------------------------------+
|                           DYNAMODB STREAMS                                      |
|                                                                                 |
|  +-------------+     +-----------------+     +------------------+               |
|  |  DynamoDB   |     |   DynamoDB      |     |   Consumers      |               |
|  |   Table     | --> |   Stream        | --> |                  |               |
|  |             |     |                 |     |  - Lambda        |               |
|  +-------------+     +-----------------+     |  - Kinesis       |               |
|                                              |  - Custom app    |               |
|                                              +------------------+               |
|                                                                                 |
|  STREAM RECORDS:                                                                |
|  +------------------------------------------------------------------+          |
|  |                                                                   |          |
|  |  {                                                                |          |
|  |    "eventID": "abc123",                                          |          |
|  |    "eventName": "INSERT" | "MODIFY" | "REMOVE",                  |          |
|  |    "eventSource": "aws:dynamodb",                                |          |
|  |    "dynamodb": {                                                 |          |
|  |      "Keys": { "UserID": { "S": "U001" } },                     |          |
|  |      "NewImage": { ... },    // Item after change                |          |
|  |      "OldImage": { ... },    // Item before change               |          |
|  |      "StreamViewType": "NEW_AND_OLD_IMAGES"                      |          |
|  |    }                                                              |          |
|  |  }                                                                |          |
|  |                                                                   |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Stream View Types

| View Type | Keys | New Image | Old Image | Use Case |
|-----------|------|-----------|-----------|----------|
| KEYS_ONLY | Yes | No | No | Minimal data, trigger only |
| NEW_IMAGE | Yes | Yes | No | Current state processing |
| OLD_IMAGE | Yes | No | Yes | Audit, before-state needed |
| NEW_AND_OLD_IMAGES | Yes | Yes | Yes | Full change history, CDC |

### Lambda Trigger Example

```python
import json

def lambda_handler(event, context):
    for record in event['Records']:
        # Get event type
        event_name = record['eventName']  # INSERT, MODIFY, or REMOVE

        # Get the key
        keys = record['dynamodb']['Keys']
        user_id = keys['UserID']['S']

        if event_name == 'INSERT':
            new_item = record['dynamodb']['NewImage']
            print(f"New user created: {user_id}")
            # Send welcome email, create related records, etc.

        elif event_name == 'MODIFY':
            old_item = record['dynamodb']['OldImage']
            new_item = record['dynamodb']['NewImage']
            print(f"User updated: {user_id}")
            # Compare changes, update caches, etc.

        elif event_name == 'REMOVE':
            old_item = record['dynamodb']['OldImage']
            print(f"User deleted: {user_id}")
            # Clean up related data, archive, etc.

    return {'statusCode': 200}
```

## Hands-On Examples

### Create a DynamoDB Table (AWS CLI)

```bash
# Create table with composite primary key
aws dynamodb create-table \
    --table-name Orders \
    --attribute-definitions \
        AttributeName=CustomerID,AttributeType=S \
        AttributeName=OrderDate,AttributeType=S \
        AttributeName=Status,AttributeType=S \
    --key-schema \
        AttributeName=CustomerID,KeyType=HASH \
        AttributeName=OrderDate,KeyType=RANGE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"StatusIndex\",
                \"KeySchema\": [
                    {\"AttributeName\": \"Status\", \"KeyType\": \"HASH\"},
                    {\"AttributeName\": \"OrderDate\", \"KeyType\": \"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\": \"ALL\"}
            }
        ]" \
    --billing-mode PAY_PER_REQUEST

# Check table status
aws dynamodb describe-table --table-name Orders \
    --query 'Table.TableStatus'
```

### CRUD Operations (Python - boto3)

```python
import boto3
from decimal import Decimal
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

# CREATE - Put Item
def create_order(customer_id, order_date, order_id, total, status='Pending'):
    response = table.put_item(
        Item={
            'CustomerID': customer_id,
            'OrderDate': order_date,
            'OrderID': order_id,
            'Total': Decimal(str(total)),
            'Status': status,
            'Items': [
                {'ProductID': 'PROD-001', 'Quantity': 2},
                {'ProductID': 'PROD-002', 'Quantity': 1}
            ]
        }
    )
    return response

# READ - Get Item
def get_order(customer_id, order_date):
    response = table.get_item(
        Key={
            'CustomerID': customer_id,
            'OrderDate': order_date
        }
    )
    return response.get('Item')

# READ - Query (all orders for a customer)
def get_customer_orders(customer_id, start_date=None):
    if start_date:
        response = table.query(
            KeyConditionExpression='CustomerID = :cid AND OrderDate >= :date',
            ExpressionAttributeValues={
                ':cid': customer_id,
                ':date': start_date
            }
        )
    else:
        response = table.query(
            KeyConditionExpression='CustomerID = :cid',
            ExpressionAttributeValues={
                ':cid': customer_id
            }
        )
    return response['Items']

# READ - Query using GSI
def get_orders_by_status(status):
    response = table.query(
        IndexName='StatusIndex',
        KeyConditionExpression='#status = :status',
        ExpressionAttributeNames={
            '#status': 'Status'  # Status is a reserved word
        },
        ExpressionAttributeValues={
            ':status': status
        }
    )
    return response['Items']

# UPDATE - Update Item
def update_order_status(customer_id, order_date, new_status):
    response = table.update_item(
        Key={
            'CustomerID': customer_id,
            'OrderDate': order_date
        },
        UpdateExpression='SET #status = :status, UpdatedAt = :updated',
        ExpressionAttributeNames={
            '#status': 'Status'
        },
        ExpressionAttributeValues={
            ':status': new_status,
            ':updated': datetime.now().isoformat()
        },
        ReturnValues='UPDATED_NEW'
    )
    return response['Attributes']

# DELETE - Delete Item
def delete_order(customer_id, order_date):
    response = table.delete_item(
        Key={
            'CustomerID': customer_id,
            'OrderDate': order_date
        },
        ReturnValues='ALL_OLD'
    )
    return response.get('Attributes')

# SCAN - Scan entire table (use sparingly!)
def scan_all_orders():
    response = table.scan()
    items = response['Items']

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response['Items'])

    return items

# Example usage
if __name__ == '__main__':
    # Create an order
    create_order('C001', '2024-03-15', 'ORD-123', 199.99)

    # Get the order
    order = get_order('C001', '2024-03-15')
    print(f"Order: {order}")

    # Get all orders for customer
    orders = get_customer_orders('C001')
    print(f"Customer orders: {orders}")

    # Update status
    update_order_status('C001', '2024-03-15', 'Shipped')

    # Query by status using GSI
    pending_orders = get_orders_by_status('Pending')
    print(f"Pending orders: {pending_orders}")
```

### Batch Operations

```python
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Products')

# Batch Write (up to 25 items)
def batch_write_products(products):
    with table.batch_writer() as batch:
        for product in products:
            batch.put_item(Item={
                'ProductID': product['id'],
                'Name': product['name'],
                'Price': Decimal(str(product['price'])),
                'Category': product['category']
            })

# Batch Get (up to 100 items)
def batch_get_products(product_ids):
    response = dynamodb.batch_get_item(
        RequestItems={
            'Products': {
                'Keys': [{'ProductID': pid} for pid in product_ids]
            }
        }
    )
    return response['Responses']['Products']

# Example
products = [
    {'id': 'PROD-001', 'name': 'Widget A', 'price': 19.99, 'category': 'Widgets'},
    {'id': 'PROD-002', 'name': 'Widget B', 'price': 29.99, 'category': 'Widgets'},
    {'id': 'PROD-003', 'name': 'Gadget X', 'price': 49.99, 'category': 'Gadgets'}
]
batch_write_products(products)
```

### Transactions

```python
import boto3
from decimal import Decimal

dynamodb = boto3.client('dynamodb')

def transfer_inventory(from_product, to_product, quantity):
    """Transfer inventory between products atomically"""

    response = dynamodb.transact_write_items(
        TransactItems=[
            {
                'Update': {
                    'TableName': 'Products',
                    'Key': {'ProductID': {'S': from_product}},
                    'UpdateExpression': 'SET Quantity = Quantity - :qty',
                    'ConditionExpression': 'Quantity >= :qty',
                    'ExpressionAttributeValues': {
                        ':qty': {'N': str(quantity)}
                    }
                }
            },
            {
                'Update': {
                    'TableName': 'Products',
                    'Key': {'ProductID': {'S': to_product}},
                    'UpdateExpression': 'SET Quantity = Quantity + :qty',
                    'ExpressionAttributeValues': {
                        ':qty': {'N': str(quantity)}
                    }
                }
            }
        ]
    )
    return response

def create_order_with_transaction(order, order_items):
    """Create order and update inventory atomically"""

    transact_items = [
        {
            'Put': {
                'TableName': 'Orders',
                'Item': {
                    'OrderID': {'S': order['order_id']},
                    'CustomerID': {'S': order['customer_id']},
                    'OrderDate': {'S': order['order_date']},
                    'Total': {'N': str(order['total'])}
                }
            }
        }
    ]

    # Add inventory updates for each item
    for item in order_items:
        transact_items.append({
            'Update': {
                'TableName': 'Products',
                'Key': {'ProductID': {'S': item['product_id']}},
                'UpdateExpression': 'SET Quantity = Quantity - :qty',
                'ConditionExpression': 'Quantity >= :qty',
                'ExpressionAttributeValues': {
                    ':qty': {'N': str(item['quantity'])}
                }
            }
        })

    response = dynamodb.transact_write_items(TransactItems=transact_items)
    return response
```

### PartiQL Queries

```python
import boto3

dynamodb = boto3.client('dynamodb')

# SELECT - Get items
response = dynamodb.execute_statement(
    Statement="SELECT * FROM Orders WHERE CustomerID = ?",
    Parameters=[{'S': 'C001'}]
)

# SELECT with condition
response = dynamodb.execute_statement(
    Statement="""
        SELECT OrderID, Total, Status
        FROM Orders
        WHERE CustomerID = ? AND OrderDate >= ?
    """,
    Parameters=[
        {'S': 'C001'},
        {'S': '2024-01-01'}
    ]
)

# INSERT
response = dynamodb.execute_statement(
    Statement="""
        INSERT INTO Products
        VALUE {'ProductID': ?, 'Name': ?, 'Price': ?}
    """,
    Parameters=[
        {'S': 'PROD-999'},
        {'S': 'New Product'},
        {'N': '99.99'}
    ]
)

# UPDATE
response = dynamodb.execute_statement(
    Statement="""
        UPDATE Products
        SET Price = ?
        WHERE ProductID = ?
    """,
    Parameters=[
        {'N': '79.99'},
        {'S': 'PROD-999'}
    ]
)

# DELETE
response = dynamodb.execute_statement(
    Statement="DELETE FROM Products WHERE ProductID = ?",
    Parameters=[{'S': 'PROD-999'}]
)
```

## DynamoDB Accelerator (DAX)

### DAX Architecture

```
+--------------------------------------------------------------------------------+
|                        DYNAMODB ACCELERATOR (DAX)                               |
|                                                                                 |
|  +-------------+        +-------------------+        +------------------+       |
|  | Application |  <-->  |    DAX Cluster    |  <-->  |    DynamoDB      |       |
|  +-------------+        |                   |        |      Table       |       |
|                         |  +-------------+  |        +------------------+       |
|                         |  | DAX Node 1  |  |                                   |
|                         |  +-------------+  |        CACHE HIT:                 |
|                         |  | DAX Node 2  |  |        - Microseconds latency     |
|                         |  +-------------+  |                                   |
|                         |  | DAX Node 3  |  |        CACHE MISS:                |
|                         |  +-------------+  |        - Read from DynamoDB       |
|                         +-------------------+        - Cache result in DAX      |
|                                                                                 |
|  DAX FEATURES:                                                                  |
|  +------------------------------------------------------------------+          |
|  | - In-memory cache for DynamoDB                                   |          |
|  | - Microsecond response times (up to 10x faster)                  |          |
|  | - Write-through cache                                            |          |
|  | - API-compatible with DynamoDB                                   |          |
|  | - Fully managed cluster                                          |          |
|  | - Up to 10 nodes per cluster                                     |          |
|  | - Multi-AZ for high availability                                 |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  IDEAL FOR:                                 NOT IDEAL FOR:                     |
|  - Read-heavy workloads                     - Write-heavy workloads            |
|  - Repeated reads of same items             - Strongly consistent reads        |
|  - Low-latency requirements                 - Infrequent data access           |
|  - Gaming, social, trading apps             - Sensitive/regulated data         |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### DAX Code Example

```python
import amazondax
import boto3

# Create DAX client (same API as DynamoDB)
dax_client = amazondax.AmazonDaxClient.resource(
    endpoint_url='dax://my-dax-cluster.us-east-1.amazonaws.com:8111'
)

# Use DAX client just like DynamoDB
table = dax_client.Table('Products')

# Read operations go through DAX cache
product = table.get_item(Key={'ProductID': 'PROD-001'})

# Write operations write-through to DynamoDB
table.put_item(Item={
    'ProductID': 'PROD-002',
    'Name': 'New Product',
    'Price': Decimal('29.99')
})

# Queries also benefit from DAX caching
response = table.query(
    KeyConditionExpression='Category = :cat',
    ExpressionAttributeValues={':cat': 'Electronics'}
)
```

## Global Tables

```
+--------------------------------------------------------------------------------+
|                          DYNAMODB GLOBAL TABLES                                 |
|                                                                                 |
|       US-EAST-1                         EU-WEST-1                              |
|   +----------------+                 +----------------+                         |
|   |   DynamoDB     |  <-- Async -->  |   DynamoDB     |                         |
|   |    Table       |   Replication   |    Table       |                         |
|   |   (Replica)    |                 |   (Replica)    |                         |
|   +----------------+                 +----------------+                         |
|          |                                   |                                  |
|          v                                   v                                  |
|   +----------------+                 +----------------+                         |
|   | US Application |                 | EU Application |                         |
|   +----------------+                 +----------------+                         |
|                                                                                 |
|                         AP-SOUTHEAST-1                                         |
|                      +----------------+                                         |
|                      |   DynamoDB     |                                         |
|                      |    Table       |                                         |
|                      |   (Replica)    |                                         |
|                      +----------------+                                         |
|                             |                                                   |
|                             v                                                   |
|                      +----------------+                                         |
|                      | APAC Application|                                        |
|                      +----------------+                                         |
|                                                                                 |
|  GLOBAL TABLES FEATURES:                                                        |
|  +------------------------------------------------------------------+          |
|  | - Active-active replication across regions                       |          |
|  | - Writes accepted in any region                                  |          |
|  | - Sub-second replication latency                                 |          |
|  | - Automatic conflict resolution (last writer wins)              |          |
|  | - 99.999% availability SLA                                       |          |
|  | - Supports DynamoDB Streams                                      |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Best Practices Summary

### Data Modeling

1. **Single-table design**: Store multiple entity types in one table
2. **Denormalize data**: Duplicate data to avoid JOINs
3. **Use composite sort keys**: Enable flexible queries (e.g., `STATUS#DATE#ORDER_ID`)
4. **Overload GSIs**: Use the same GSI for multiple access patterns

### Performance

1. **Distribute partition keys**: Avoid hot partitions
2. **Use sparse indexes**: Only project needed attributes
3. **Implement pagination**: Use `LastEvaluatedKey` for large result sets
4. **Prefer Query over Scan**: Scans are expensive

### Cost Optimization

1. **Right-size capacity**: Use auto-scaling or on-demand mode
2. **Use TTL for expiring data**: Automatically delete old items
3. **Project minimal attributes**: Reduce data transfer costs
4. **Consider reserved capacity**: For steady, predictable workloads

---

**Next:** [09 - ElastiCache](./09-elasticache.md)

**Previous:** [07 - Aurora](./07-aurora.md)
