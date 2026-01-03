# 11 - Hands-On Database Lab

## Lab Overview

In this comprehensive lab, you will set up a complete database infrastructure on AWS, including RDS MySQL, DynamoDB, and ElastiCache Redis. You will learn to connect applications, perform CRUD operations, and implement best practices.

```
+--------------------------------------------------------------------------------+
|                           LAB ARCHITECTURE                                      |
|                                                                                 |
|  +------------------------------------------------------------------+          |
|  |                          VPC (10.0.0.0/16)                        |          |
|  |                                                                   |          |
|  |   Public Subnet (10.0.1.0/24)           Private Subnet (10.0.2.0/24)        |
|  |   +-------------------------+           +-------------------------+          |
|  |   |                         |           |                         |          |
|  |   |   +----------------+    |           |   +----------------+    |          |
|  |   |   |   Bastion/     |    |           |   |   RDS MySQL    |    |          |
|  |   |   |   App Server   |    |---------->|   |   (Multi-AZ)   |    |          |
|  |   |   +----------------+    |           |   +----------------+    |          |
|  |   |                         |           |                         |          |
|  |   +-------------------------+           |   +----------------+    |          |
|  |                                          |   |   ElastiCache  |    |          |
|  |                                          |   |   (Redis)      |    |          |
|  |                                          |   +----------------+    |          |
|  |                                          |                         |          |
|  |                                          +-------------------------+          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
|  +------------------------------------------------------------------+          |
|  |                       DynamoDB (Serverless)                       |          |
|  +------------------------------------------------------------------+          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

**Estimated Time:** 3-4 hours

**Cost Estimate:** ~$5-10 (if cleaned up promptly)

**Prerequisites:**
- AWS Account with admin access
- AWS CLI configured
- Basic SQL knowledge
- Python 3.8+ installed locally

---

## Lab 1: Launch RDS MySQL Instance

### Step 1.1: Create VPC Infrastructure

```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=database-lab-vpc}]' \
    --query 'Vpc.VpcId' \
    --output text)

echo "VPC ID: $VPC_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=database-lab-igw}]' \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

aws ec2 attach-internet-gateway \
    --vpc-id $VPC_ID \
    --internet-gateway-id $IGW_ID

# Create Public Subnet (AZ-a)
PUBLIC_SUBNET_A=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=database-lab-public-a}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Create Private Subnets (for RDS - need 2 AZs)
PRIVATE_SUBNET_A=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone us-east-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=database-lab-private-a}]' \
    --query 'Subnet.SubnetId' \
    --output text)

PRIVATE_SUBNET_B=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone us-east-1b \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=database-lab-private-b}]' \
    --query 'Subnet.SubnetId' \
    --output text)

# Create and configure route tables
PUBLIC_RT=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=database-lab-public-rt}]' \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --route-table-id $PUBLIC_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

aws ec2 associate-route-table \
    --route-table-id $PUBLIC_RT \
    --subnet-id $PUBLIC_SUBNET_A

echo "Public Subnet: $PUBLIC_SUBNET_A"
echo "Private Subnet A: $PRIVATE_SUBNET_A"
echo "Private Subnet B: $PRIVATE_SUBNET_B"
```

### Step 1.2: Create Security Groups

```bash
# Security group for EC2 (Bastion/App Server)
EC2_SG=$(aws ec2 create-security-group \
    --group-name database-lab-ec2-sg \
    --description "Security group for EC2 instances" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow SSH from your IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-id $EC2_SG \
    --protocol tcp \
    --port 22 \
    --cidr ${MY_IP}/32

# Security group for RDS
RDS_SG=$(aws ec2 create-security-group \
    --group-name database-lab-rds-sg \
    --description "Security group for RDS" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow MySQL from EC2 security group
aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG \
    --protocol tcp \
    --port 3306 \
    --source-group $EC2_SG

# Security group for ElastiCache
CACHE_SG=$(aws ec2 create-security-group \
    --group-name database-lab-cache-sg \
    --description "Security group for ElastiCache" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)

# Allow Redis from EC2 security group
aws ec2 authorize-security-group-ingress \
    --group-id $CACHE_SG \
    --protocol tcp \
    --port 6379 \
    --source-group $EC2_SG

echo "EC2 Security Group: $EC2_SG"
echo "RDS Security Group: $RDS_SG"
echo "Cache Security Group: $CACHE_SG"
```

### Step 1.3: Create RDS Subnet Group

```bash
aws rds create-db-subnet-group \
    --db-subnet-group-name database-lab-subnet-group \
    --db-subnet-group-description "Subnet group for database lab" \
    --subnet-ids $PRIVATE_SUBNET_A $PRIVATE_SUBNET_B
```

### Step 1.4: Create RDS MySQL Instance

```bash
# Create RDS MySQL instance
aws rds create-db-instance \
    --db-instance-identifier database-lab-mysql \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --engine-version 8.0 \
    --master-username admin \
    --master-user-password 'LabPassword123!' \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids $RDS_SG \
    --db-subnet-group-name database-lab-subnet-group \
    --backup-retention-period 7 \
    --no-publicly-accessible \
    --no-multi-az \
    --db-name labdb \
    --tags Key=Environment,Value=Lab

echo "RDS instance creation initiated. This will take 5-10 minutes..."

# Wait for instance to be available
aws rds wait db-instance-available \
    --db-instance-identifier database-lab-mysql

# Get endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier database-lab-mysql \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"
```

### Step 1.5: Launch EC2 Instance (Bastion)

```bash
# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ssm get-parameters \
    --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
    --query 'Parameters[0].Value' \
    --output text)

# Create key pair
aws ec2 create-key-pair \
    --key-name database-lab-key \
    --query 'KeyMaterial' \
    --output text > database-lab-key.pem

chmod 400 database-lab-key.pem

# Launch EC2 instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t3.micro \
    --key-name database-lab-key \
    --subnet-id $PUBLIC_SUBNET_A \
    --security-group-ids $EC2_SG \
    --associate-public-ip-address \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=database-lab-bastion}]' \
    --user-data '#!/bin/bash
yum update -y
yum install -y mysql python3 python3-pip
pip3 install boto3 pymysql redis' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "EC2 Instance ID: $INSTANCE_ID"

# Wait for instance and get public IP
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

EC2_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "EC2 Public IP: $EC2_IP"
echo "SSH Command: ssh -i database-lab-key.pem ec2-user@$EC2_IP"
```

---

## Lab 2: Set Up Multi-AZ and Read Replica

### Step 2.1: Enable Multi-AZ

```bash
# Modify RDS instance to enable Multi-AZ
aws rds modify-db-instance \
    --db-instance-identifier database-lab-mysql \
    --multi-az \
    --apply-immediately

echo "Enabling Multi-AZ. This will take 10-15 minutes..."

# Wait for modification to complete
aws rds wait db-instance-available \
    --db-instance-identifier database-lab-mysql

# Verify Multi-AZ is enabled
aws rds describe-db-instances \
    --db-instance-identifier database-lab-mysql \
    --query 'DBInstances[0].{MultiAZ:MultiAZ,SecondaryAZ:SecondaryAvailabilityZone}'
```

### Step 2.2: Create Read Replica

```bash
# Create Read Replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier database-lab-mysql-replica \
    --source-db-instance-identifier database-lab-mysql \
    --db-instance-class db.t3.micro \
    --availability-zone us-east-1b \
    --no-publicly-accessible

echo "Creating Read Replica. This will take 5-10 minutes..."

# Wait for replica to be available
aws rds wait db-instance-available \
    --db-instance-identifier database-lab-mysql-replica

# Get replica endpoint
REPLICA_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier database-lab-mysql-replica \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo "Read Replica Endpoint: $REPLICA_ENDPOINT"
```

### Step 2.3: Test Replication

```bash
# SSH into EC2 instance
ssh -i database-lab-key.pem ec2-user@$EC2_IP

# Connect to primary and create test data
mysql -h $RDS_ENDPOINT -u admin -p'LabPassword123!' labdb << 'EOF'
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, price) VALUES
    ('Widget A', 19.99),
    ('Widget B', 29.99),
    ('Gadget X', 49.99);

SELECT * FROM products;
EOF

# Connect to replica and verify data
mysql -h $REPLICA_ENDPOINT -u admin -p'LabPassword123!' labdb -e "SELECT * FROM products;"
```

---

## Lab 3: Connect Application to RDS

### Step 3.1: Python Application

Create `app.py` on the EC2 instance:

```python
#!/usr/bin/env python3
"""
RDS MySQL Application Example
"""

import pymysql
import os
from datetime import datetime

# Configuration
DB_CONFIG = {
    'host': os.environ.get('RDS_HOST', 'your-rds-endpoint'),
    'user': 'admin',
    'password': 'LabPassword123!',
    'database': 'labdb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

class ProductRepository:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Establish database connection"""
        self.connection = pymysql.connect(**DB_CONFIG)

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def create_table(self):
        """Create products table if not exists"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    quantity INT DEFAULT 0,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
        self.connection.commit()

    def create(self, name, description, price, quantity, category):
        """Create a new product"""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products (name, description, price, quantity, category)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, description, price, quantity, category)
            )
        self.connection.commit()
        return cursor.lastrowid

    def read(self, product_id):
        """Read a product by ID"""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM products WHERE id = %s",
                (product_id,)
            )
            return cursor.fetchone()

    def read_all(self):
        """Read all products"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
            return cursor.fetchall()

    def update(self, product_id, **kwargs):
        """Update a product"""
        fields = ', '.join([f"{k} = %s" for k in kwargs.keys()])
        values = list(kwargs.values()) + [product_id]

        with self.connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE products SET {fields} WHERE id = %s",
                values
            )
        self.connection.commit()
        return cursor.rowcount

    def delete(self, product_id):
        """Delete a product"""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )
        self.connection.commit()
        return cursor.rowcount

    def search_by_category(self, category):
        """Search products by category"""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM products WHERE category = %s",
                (category,)
            )
            return cursor.fetchall()

def main():
    repo = ProductRepository()

    try:
        # Connect to database
        print("Connecting to RDS MySQL...")
        repo.connect()
        print("Connected successfully!\n")

        # Create table
        print("Creating products table...")
        repo.create_table()
        print("Table created/verified.\n")

        # CREATE - Insert products
        print("Inserting products...")
        products = [
            ("Laptop Pro", "High-performance laptop", 1299.99, 10, "Electronics"),
            ("Wireless Mouse", "Ergonomic wireless mouse", 29.99, 50, "Electronics"),
            ("Desk Chair", "Comfortable office chair", 249.99, 15, "Furniture"),
            ("USB-C Hub", "Multi-port USB-C hub", 49.99, 30, "Electronics"),
            ("Standing Desk", "Adjustable standing desk", 599.99, 5, "Furniture"),
        ]

        for name, desc, price, qty, cat in products:
            product_id = repo.create(name, desc, price, qty, cat)
            print(f"  Created: {name} (ID: {product_id})")

        print()

        # READ - Get all products
        print("All products:")
        all_products = repo.read_all()
        for p in all_products:
            print(f"  [{p['id']}] {p['name']}: ${p['price']} ({p['quantity']} in stock)")

        print()

        # READ - Get single product
        product = repo.read(1)
        if product:
            print(f"Product 1: {product['name']}")
            print(f"  Description: {product['description']}")
            print(f"  Price: ${product['price']}")
            print(f"  Category: {product['category']}")

        print()

        # UPDATE - Modify a product
        print("Updating product 1 price...")
        repo.update(1, price=1199.99, quantity=8)
        updated_product = repo.read(1)
        print(f"  New price: ${updated_product['price']}")
        print(f"  New quantity: {updated_product['quantity']}")

        print()

        # SEARCH - Find by category
        print("Electronics products:")
        electronics = repo.search_by_category("Electronics")
        for p in electronics:
            print(f"  - {p['name']}: ${p['price']}")

        print()

        # DELETE - Remove a product
        print("Deleting product 5...")
        deleted = repo.delete(5)
        print(f"  Deleted {deleted} product(s)")

        print()

        # Final count
        final_products = repo.read_all()
        print(f"Total products remaining: {len(final_products)}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        repo.disconnect()
        print("\nDisconnected from database.")

if __name__ == '__main__':
    main()
```

### Step 3.2: Run the Application

```bash
# Set environment variable for RDS endpoint
export RDS_HOST="database-lab-mysql.abc123.us-east-1.rds.amazonaws.com"

# Run the application
python3 app.py
```

---

## Lab 4: Create DynamoDB Table

### Step 4.1: Create Table with GSI

```bash
# Create DynamoDB table
aws dynamodb create-table \
    --table-name database-lab-orders \
    --attribute-definitions \
        AttributeName=customer_id,AttributeType=S \
        AttributeName=order_date,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=customer_id,KeyType=HASH \
        AttributeName=order_date,KeyType=RANGE \
    --global-secondary-indexes \
        '[
            {
                "IndexName": "status-index",
                "KeySchema": [
                    {"AttributeName": "status", "KeyType": "HASH"},
                    {"AttributeName": "order_date", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"}
            }
        ]' \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=Lab

# Wait for table to be active
aws dynamodb wait table-exists --table-name database-lab-orders

echo "DynamoDB table created successfully!"
```

### Step 4.2: DynamoDB Python Application

Create `dynamodb_app.py`:

```python
#!/usr/bin/env python3
"""
DynamoDB Application Example
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from datetime import datetime, timedelta
import json
import uuid

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('database-lab-orders')

class OrderRepository:
    @staticmethod
    def create_order(customer_id, items, total):
        """Create a new order"""
        order_id = str(uuid.uuid4())
        order_date = datetime.now().isoformat()

        order = {
            'customer_id': customer_id,
            'order_date': order_date,
            'order_id': order_id,
            'items': items,
            'total': Decimal(str(total)),
            'status': 'PENDING',
            'created_at': order_date
        }

        table.put_item(Item=order)
        return order

    @staticmethod
    def get_order(customer_id, order_date):
        """Get a specific order"""
        response = table.get_item(
            Key={
                'customer_id': customer_id,
                'order_date': order_date
            }
        )
        return response.get('Item')

    @staticmethod
    def get_customer_orders(customer_id, start_date=None):
        """Get all orders for a customer"""
        if start_date:
            response = table.query(
                KeyConditionExpression=Key('customer_id').eq(customer_id) &
                                        Key('order_date').gte(start_date)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('customer_id').eq(customer_id)
            )
        return response['Items']

    @staticmethod
    def get_orders_by_status(status):
        """Get orders by status using GSI"""
        response = table.query(
            IndexName='status-index',
            KeyConditionExpression=Key('status').eq(status)
        )
        return response['Items']

    @staticmethod
    def update_status(customer_id, order_date, new_status):
        """Update order status"""
        response = table.update_item(
            Key={
                'customer_id': customer_id,
                'order_date': order_date
            },
            UpdateExpression='SET #status = :status, updated_at = :updated',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': new_status,
                ':updated': datetime.now().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        return response['Attributes']

    @staticmethod
    def delete_order(customer_id, order_date):
        """Delete an order"""
        response = table.delete_item(
            Key={
                'customer_id': customer_id,
                'order_date': order_date
            },
            ReturnValues='ALL_OLD'
        )
        return response.get('Attributes')

    @staticmethod
    def batch_write_orders(orders):
        """Batch write multiple orders"""
        with table.batch_writer() as batch:
            for order in orders:
                batch.put_item(Item=order)

def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def print_order(order):
    """Pretty print an order"""
    print(json.dumps(order, indent=2, default=decimal_default))

def main():
    print("DynamoDB Orders Demo")
    print("=" * 50)

    # CREATE - Insert orders
    print("\n1. Creating orders...")

    orders = [
        {
            'customer_id': 'CUST-001',
            'items': [
                {'product': 'Laptop Pro', 'quantity': 1, 'price': 1299.99},
                {'product': 'USB-C Hub', 'quantity': 2, 'price': 49.99}
            ],
            'total': 1399.97
        },
        {
            'customer_id': 'CUST-001',
            'items': [
                {'product': 'Wireless Mouse', 'quantity': 1, 'price': 29.99}
            ],
            'total': 29.99
        },
        {
            'customer_id': 'CUST-002',
            'items': [
                {'product': 'Standing Desk', 'quantity': 1, 'price': 599.99},
                {'product': 'Desk Chair', 'quantity': 1, 'price': 249.99}
            ],
            'total': 849.98
        }
    ]

    created_orders = []
    for order_data in orders:
        order = OrderRepository.create_order(
            order_data['customer_id'],
            order_data['items'],
            order_data['total']
        )
        created_orders.append(order)
        print(f"  Created order {order['order_id'][:8]}... for {order['customer_id']}")

    # READ - Get all orders for a customer
    print("\n2. Orders for CUST-001:")
    customer_orders = OrderRepository.get_customer_orders('CUST-001')
    for order in customer_orders:
        print(f"  - {order['order_date']}: ${order['total']} ({order['status']})")

    # READ - Get specific order
    print("\n3. Getting first order details:")
    first_order = created_orders[0]
    order = OrderRepository.get_order(first_order['customer_id'], first_order['order_date'])
    print_order(order)

    # UPDATE - Change status
    print("\n4. Updating order status to SHIPPED...")
    updated = OrderRepository.update_status(
        first_order['customer_id'],
        first_order['order_date'],
        'SHIPPED'
    )
    print(f"  New status: {updated['status']}")

    # QUERY by GSI - Get pending orders
    print("\n5. All PENDING orders:")
    pending = OrderRepository.get_orders_by_status('PENDING')
    for order in pending:
        print(f"  - {order['customer_id']}: ${order['total']}")

    # DELETE - Remove an order
    print("\n6. Deleting last order...")
    last_order = created_orders[-1]
    deleted = OrderRepository.delete_order(
        last_order['customer_id'],
        last_order['order_date']
    )
    print(f"  Deleted order {deleted['order_id'][:8]}...")

    # Scan - Count all orders
    print("\n7. Total orders in table:")
    response = table.scan(Select='COUNT')
    print(f"  {response['Count']} orders")

if __name__ == '__main__':
    main()
```

### Step 4.3: Enable DynamoDB Streams

```bash
# Enable streams
aws dynamodb update-table \
    --table-name database-lab-orders \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# Get stream ARN
STREAM_ARN=$(aws dynamodb describe-table \
    --table-name database-lab-orders \
    --query 'Table.LatestStreamArn' \
    --output text)

echo "Stream ARN: $STREAM_ARN"
```

---

## Lab 5: Set Up ElastiCache Redis

### Step 5.1: Create Cache Subnet Group

```bash
# Create ElastiCache subnet group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name database-lab-cache-subnet \
    --cache-subnet-group-description "Cache subnet group for lab" \
    --subnet-ids $PRIVATE_SUBNET_A $PRIVATE_SUBNET_B
```

### Step 5.2: Create Redis Cluster

```bash
# Create Redis replication group
aws elasticache create-replication-group \
    --replication-group-id database-lab-redis \
    --replication-group-description "Redis cluster for lab" \
    --engine redis \
    --engine-version 7.0 \
    --cache-node-type cache.t3.micro \
    --num-cache-clusters 2 \
    --cache-subnet-group-name database-lab-cache-subnet \
    --security-group-ids $CACHE_SG \
    --automatic-failover-enabled \
    --multi-az-enabled

echo "Creating Redis cluster. This will take 5-10 minutes..."

# Wait for cluster to be available
aws elasticache wait replication-group-available \
    --replication-group-id database-lab-redis

# Get endpoint
REDIS_ENDPOINT=$(aws elasticache describe-replication-groups \
    --replication-group-id database-lab-redis \
    --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
    --output text)

echo "Redis Endpoint: $REDIS_ENDPOINT"
```

### Step 5.3: Redis Cache Application

Create `cache_app.py`:

```python
#!/usr/bin/env python3
"""
ElastiCache Redis Application with Caching Patterns
"""

import redis
import pymysql
import json
import time
import os
from functools import wraps

# Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'your-redis-endpoint')
REDIS_PORT = 6379

DB_CONFIG = {
    'host': os.environ.get('RDS_HOST', 'your-rds-endpoint'),
    'user': 'admin',
    'password': 'LabPassword123!',
    'database': 'labdb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Initialize Redis client
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(**DB_CONFIG)

class CachedProductRepository:
    """Product repository with caching"""

    CACHE_TTL = 300  # 5 minutes

    @staticmethod
    def get_product(product_id):
        """Get product with lazy loading cache pattern"""
        cache_key = f"product:{product_id}"

        # Try cache first
        cached = cache.get(cache_key)
        if cached:
            print(f"  [CACHE HIT] {cache_key}")
            return json.loads(cached)

        print(f"  [CACHE MISS] {cache_key}")

        # Get from database
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                product = cursor.fetchone()

            if product:
                # Convert Decimal to float for JSON serialization
                product['price'] = float(product['price'])
                product['created_at'] = str(product['created_at'])
                product['updated_at'] = str(product['updated_at'])

                # Store in cache
                cache.setex(cache_key, CachedProductRepository.CACHE_TTL, json.dumps(product))

            return product
        finally:
            conn.close()

    @staticmethod
    def update_product(product_id, **kwargs):
        """Update product with write-through cache pattern"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                fields = ', '.join([f"{k} = %s" for k in kwargs.keys()])
                values = list(kwargs.values()) + [product_id]
                cursor.execute(f"UPDATE products SET {fields} WHERE id = %s", values)
            conn.commit()

            # Invalidate cache
            cache_key = f"product:{product_id}"
            cache.delete(cache_key)
            print(f"  [CACHE INVALIDATED] {cache_key}")

            return True
        finally:
            conn.close()

    @staticmethod
    def get_all_products():
        """Get all products with cache"""
        cache_key = "products:all"

        cached = cache.get(cache_key)
        if cached:
            print("  [CACHE HIT] products:all")
            return json.loads(cached)

        print("  [CACHE MISS] products:all")

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM products")
                products = cursor.fetchall()

            # Convert for JSON
            for p in products:
                p['price'] = float(p['price'])
                p['created_at'] = str(p['created_at'])
                p['updated_at'] = str(p['updated_at'])

            cache.setex(cache_key, CachedProductRepository.CACHE_TTL, json.dumps(products))
            return products
        finally:
            conn.close()

class SessionStore:
    """Session management with Redis"""

    SESSION_TTL = 3600  # 1 hour

    @staticmethod
    def create_session(user_id, user_data):
        """Create a new session"""
        import uuid
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"

        session_data = {
            'user_id': user_id,
            'created_at': time.time(),
            **user_data
        }

        cache.setex(session_key, SessionStore.SESSION_TTL, json.dumps(session_data))
        return session_id

    @staticmethod
    def get_session(session_id):
        """Get session data"""
        session_key = f"session:{session_id}"
        data = cache.get(session_key)
        return json.loads(data) if data else None

    @staticmethod
    def delete_session(session_id):
        """Delete session (logout)"""
        session_key = f"session:{session_id}"
        return cache.delete(session_key)

    @staticmethod
    def extend_session(session_id):
        """Extend session TTL"""
        session_key = f"session:{session_id}"
        return cache.expire(session_key, SessionStore.SESSION_TTL)

class RateLimiter:
    """Rate limiting with Redis"""

    @staticmethod
    def is_allowed(user_id, max_requests=10, window_seconds=60):
        """Check if request is allowed under rate limit"""
        key = f"ratelimit:{user_id}"

        # Get current count
        current = cache.get(key)

        if current is None:
            # First request - set counter
            cache.setex(key, window_seconds, 1)
            return True, max_requests - 1

        current = int(current)
        if current >= max_requests:
            # Rate limit exceeded
            ttl = cache.ttl(key)
            return False, ttl

        # Increment counter
        cache.incr(key)
        return True, max_requests - current - 1

class Leaderboard:
    """Gaming leaderboard with Redis sorted sets"""

    LEADERBOARD_KEY = "leaderboard:game1"

    @staticmethod
    def add_score(player_id, score):
        """Add or update player score"""
        cache.zadd(Leaderboard.LEADERBOARD_KEY, {player_id: score})

    @staticmethod
    def increment_score(player_id, points):
        """Increment player score"""
        return cache.zincrby(Leaderboard.LEADERBOARD_KEY, points, player_id)

    @staticmethod
    def get_rank(player_id):
        """Get player rank (0-indexed, highest first)"""
        rank = cache.zrevrank(Leaderboard.LEADERBOARD_KEY, player_id)
        return rank + 1 if rank is not None else None

    @staticmethod
    def get_score(player_id):
        """Get player score"""
        return cache.zscore(Leaderboard.LEADERBOARD_KEY, player_id)

    @staticmethod
    def get_top(n=10):
        """Get top N players"""
        return cache.zrevrange(Leaderboard.LEADERBOARD_KEY, 0, n-1, withscores=True)

def main():
    print("ElastiCache Redis Demo")
    print("=" * 50)

    # 1. Database Caching Demo
    print("\n1. DATABASE CACHING (Lazy Loading)")
    print("-" * 40)

    # First request - cache miss
    print("First request (cache miss expected):")
    product = CachedProductRepository.get_product(1)
    if product:
        print(f"  Product: {product['name']} - ${product['price']}")

    # Second request - cache hit
    print("\nSecond request (cache hit expected):")
    product = CachedProductRepository.get_product(1)

    # Update and invalidate
    print("\nUpdating product (cache invalidation):")
    CachedProductRepository.update_product(1, price=1149.99)

    # Next request - cache miss again
    print("\nAfter update (cache miss expected):")
    product = CachedProductRepository.get_product(1)
    if product:
        print(f"  New price: ${product['price']}")

    # 2. Session Store Demo
    print("\n\n2. SESSION STORE")
    print("-" * 40)

    # Create session
    session_id = SessionStore.create_session('user123', {
        'username': 'john_doe',
        'email': 'john@example.com',
        'role': 'admin'
    })
    print(f"Created session: {session_id[:8]}...")

    # Get session
    session = SessionStore.get_session(session_id)
    print(f"Session data: {session}")

    # Extend session
    SessionStore.extend_session(session_id)
    print("Session extended")

    # 3. Rate Limiting Demo
    print("\n\n3. RATE LIMITING")
    print("-" * 40)

    user_id = "user456"
    print(f"Rate limit: 5 requests per minute for {user_id}")

    for i in range(7):
        allowed, remaining = RateLimiter.is_allowed(user_id, max_requests=5, window_seconds=60)
        if allowed:
            print(f"  Request {i+1}: ALLOWED ({remaining} remaining)")
        else:
            print(f"  Request {i+1}: BLOCKED (retry in {remaining}s)")

    # 4. Leaderboard Demo
    print("\n\n4. GAMING LEADERBOARD")
    print("-" * 40)

    # Add scores
    players = [
        ('player1', 1500),
        ('player2', 2300),
        ('player3', 1800),
        ('player4', 2100),
        ('player5', 1950)
    ]

    print("Adding player scores...")
    for player, score in players:
        Leaderboard.add_score(player, score)

    # Get top players
    print("\nTop 5 Players:")
    top_players = Leaderboard.get_top(5)
    for i, (player, score) in enumerate(top_players, 1):
        print(f"  {i}. {player}: {int(score)} points")

    # Increment score
    print("\nplayer1 earned 1000 points!")
    new_score = Leaderboard.increment_score('player1', 1000)
    rank = Leaderboard.get_rank('player1')
    print(f"  New score: {int(new_score)}, Rank: {rank}")

    # Updated leaderboard
    print("\nUpdated Leaderboard:")
    top_players = Leaderboard.get_top(5)
    for i, (player, score) in enumerate(top_players, 1):
        print(f"  {i}. {player}: {int(score)} points")

    # 5. Cache Statistics
    print("\n\n5. CACHE STATISTICS")
    print("-" * 40)

    info = cache.info()
    print(f"Connected clients: {info['connected_clients']}")
    print(f"Used memory: {info['used_memory_human']}")
    print(f"Total keys: {cache.dbsize()}")

    # List all keys
    print("\nAll cache keys:")
    for key in cache.keys('*'):
        ttl = cache.ttl(key)
        print(f"  {key} (TTL: {ttl}s)")

if __name__ == '__main__':
    main()
```

---

## Lab 6: Performance Testing

### Step 6.1: RDS Performance Test

```python
#!/usr/bin/env python3
"""
RDS Performance Testing
"""

import pymysql
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_CONFIG = {
    'host': 'your-rds-endpoint',
    'user': 'admin',
    'password': 'LabPassword123!',
    'database': 'labdb'
}

def single_query_test():
    """Test single query latency"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    latencies = []
    for _ in range(100):
        start = time.time()
        cursor.execute("SELECT * FROM products WHERE id = 1")
        cursor.fetchone()
        latencies.append((time.time() - start) * 1000)  # ms

    cursor.close()
    conn.close()

    return latencies

def concurrent_query_test(num_threads=10, queries_per_thread=50):
    """Test concurrent query performance"""

    def worker():
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        latencies = []

        for _ in range(queries_per_thread):
            start = time.time()
            cursor.execute("SELECT * FROM products")
            cursor.fetchall()
            latencies.append((time.time() - start) * 1000)

        cursor.close()
        conn.close()
        return latencies

    all_latencies = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        for future in as_completed(futures):
            all_latencies.extend(future.result())

    total_time = time.time() - start_time
    total_queries = num_threads * queries_per_thread

    return {
        'total_queries': total_queries,
        'total_time': total_time,
        'qps': total_queries / total_time,
        'latencies': all_latencies
    }

def print_stats(name, latencies):
    """Print latency statistics"""
    print(f"\n{name}:")
    print(f"  Count: {len(latencies)}")
    print(f"  Min: {min(latencies):.2f} ms")
    print(f"  Max: {max(latencies):.2f} ms")
    print(f"  Mean: {statistics.mean(latencies):.2f} ms")
    print(f"  Median: {statistics.median(latencies):.2f} ms")
    print(f"  Std Dev: {statistics.stdev(latencies):.2f} ms")
    print(f"  p95: {sorted(latencies)[int(len(latencies)*0.95)]:.2f} ms")
    print(f"  p99: {sorted(latencies)[int(len(latencies)*0.99)]:.2f} ms")

def main():
    print("RDS Performance Test")
    print("=" * 50)

    # Single query test
    print("\n1. Single Query Latency Test (100 queries)")
    latencies = single_query_test()
    print_stats("Single Query", latencies)

    # Concurrent test
    print("\n2. Concurrent Query Test (10 threads, 50 queries each)")
    results = concurrent_query_test(10, 50)
    print(f"\n  Total queries: {results['total_queries']}")
    print(f"  Total time: {results['total_time']:.2f}s")
    print(f"  Queries/second: {results['qps']:.2f}")
    print_stats("Concurrent Queries", results['latencies'])

if __name__ == '__main__':
    main()
```

### Step 6.2: Cache vs Database Performance

```python
#!/usr/bin/env python3
"""
Compare Cache vs Database Performance
"""

import redis
import pymysql
import time
import json

REDIS_HOST = 'your-redis-endpoint'
DB_CONFIG = {
    'host': 'your-rds-endpoint',
    'user': 'admin',
    'password': 'LabPassword123!',
    'database': 'labdb'
}

def benchmark_database(iterations=1000):
    """Benchmark direct database queries"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    start = time.time()
    for _ in range(iterations):
        cursor.execute("SELECT * FROM products WHERE id = 1")
        cursor.fetchone()

    elapsed = time.time() - start
    cursor.close()
    conn.close()

    return elapsed

def benchmark_cache(iterations=1000):
    """Benchmark Redis cache"""
    r = redis.Redis(host=REDIS_HOST, decode_responses=True)

    # Prime the cache
    r.set('product:1', json.dumps({'id': 1, 'name': 'Test', 'price': 99.99}))

    start = time.time()
    for _ in range(iterations):
        data = r.get('product:1')
        json.loads(data)

    elapsed = time.time() - start
    return elapsed

def benchmark_cached_pattern(iterations=1000):
    """Benchmark cache-aside pattern"""
    r = redis.Redis(host=REDIS_HOST, decode_responses=True)
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Clear cache
    r.delete('product:cached:1')

    start = time.time()
    for _ in range(iterations):
        cached = r.get('product:cached:1')
        if cached:
            json.loads(cached)
        else:
            cursor.execute("SELECT * FROM products WHERE id = 1")
            product = cursor.fetchone()
            if product:
                product['price'] = float(product['price'])
                product['created_at'] = str(product['created_at'])
                product['updated_at'] = str(product['updated_at'])
                r.setex('product:cached:1', 300, json.dumps(product))

    elapsed = time.time() - start
    cursor.close()
    conn.close()
    return elapsed

def main():
    iterations = 1000
    print(f"Performance Comparison ({iterations} iterations)")
    print("=" * 50)

    # Database only
    print("\n1. Database Only...")
    db_time = benchmark_database(iterations)
    db_qps = iterations / db_time
    print(f"   Time: {db_time:.3f}s")
    print(f"   Queries/sec: {db_qps:.0f}")

    # Cache only
    print("\n2. Cache Only...")
    cache_time = benchmark_cache(iterations)
    cache_qps = iterations / cache_time
    print(f"   Time: {cache_time:.3f}s")
    print(f"   Queries/sec: {cache_qps:.0f}")

    # Cached pattern (mostly hits after first)
    print("\n3. Cache-Aside Pattern...")
    cached_time = benchmark_cached_pattern(iterations)
    cached_qps = iterations / cached_time
    print(f"   Time: {cached_time:.3f}s")
    print(f"   Queries/sec: {cached_qps:.0f}")

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"   Cache is {db_time/cache_time:.1f}x faster than database")
    print(f"   Cache-aside is {db_time/cached_time:.1f}x faster than database only")

if __name__ == '__main__':
    main()
```

---

## Lab 7: Cleanup

**IMPORTANT:** Complete this cleanup to avoid ongoing charges!

### Step 7.1: Delete ElastiCache

```bash
# Delete Redis replication group
aws elasticache delete-replication-group \
    --replication-group-id database-lab-redis \
    --no-final-snapshot

echo "Deleting Redis cluster..."
# This takes several minutes

# Delete cache subnet group (after cluster is deleted)
# Wait for cluster deletion first
sleep 300

aws elasticache delete-cache-subnet-group \
    --cache-subnet-group-name database-lab-cache-subnet
```

### Step 7.2: Delete DynamoDB Table

```bash
# Delete DynamoDB table
aws dynamodb delete-table --table-name database-lab-orders

echo "DynamoDB table deleted"
```

### Step 7.3: Delete RDS Instances

```bash
# Delete Read Replica first (no final snapshot needed)
aws rds delete-db-instance \
    --db-instance-identifier database-lab-mysql-replica \
    --skip-final-snapshot

echo "Deleting Read Replica..."

# Wait for replica deletion
aws rds wait db-instance-deleted \
    --db-instance-identifier database-lab-mysql-replica

# Delete primary instance
aws rds delete-db-instance \
    --db-instance-identifier database-lab-mysql \
    --skip-final-snapshot \
    --delete-automated-backups

echo "Deleting primary RDS instance..."

# Wait for primary deletion
aws rds wait db-instance-deleted \
    --db-instance-identifier database-lab-mysql

# Delete subnet group
aws rds delete-db-subnet-group \
    --db-subnet-group-name database-lab-subnet-group

echo "RDS resources deleted"
```

### Step 7.4: Delete EC2 and VPC Resources

```bash
# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID

# Delete key pair
aws ec2 delete-key-pair --key-name database-lab-key
rm -f database-lab-key.pem

# Delete security groups
aws ec2 delete-security-group --group-id $CACHE_SG
aws ec2 delete-security-group --group-id $RDS_SG
aws ec2 delete-security-group --group-id $EC2_SG

# Delete subnets
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_A
aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_A
aws ec2 delete-subnet --subnet-id $PRIVATE_SUBNET_B

# Delete route table
aws ec2 delete-route-table --route-table-id $PUBLIC_RT

# Detach and delete Internet Gateway
aws ec2 detach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID

aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID

# Delete VPC
aws ec2 delete-vpc --vpc-id $VPC_ID

echo "All VPC resources deleted"
```

### Step 7.5: Verification

```bash
# Verify all resources are deleted
echo "Verifying cleanup..."

# Check RDS
aws rds describe-db-instances \
    --query 'DBInstances[?starts_with(DBInstanceIdentifier, `database-lab`)]'

# Check DynamoDB
aws dynamodb list-tables --query 'TableNames[?contains(@, `database-lab`)]'

# Check ElastiCache
aws elasticache describe-replication-groups \
    --query 'ReplicationGroups[?starts_with(ReplicationGroupId, `database-lab`)]'

# Check VPC
aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=database-lab-vpc" \
    --query 'Vpcs[*].VpcId'

echo "Cleanup verification complete!"
```

---

## Lab Summary

### What You Learned

1. **RDS MySQL**
   - Created and configured RDS instance
   - Enabled Multi-AZ for high availability
   - Created Read Replica for read scaling
   - Connected from EC2 application

2. **DynamoDB**
   - Created table with composite primary key
   - Implemented CRUD operations
   - Used Global Secondary Index for queries
   - Enabled DynamoDB Streams

3. **ElastiCache Redis**
   - Created Redis replication group
   - Implemented caching patterns (lazy loading, write-through)
   - Built session store
   - Implemented rate limiting and leaderboard

4. **Performance**
   - Compared database vs cache performance
   - Measured query latencies
   - Observed cache benefits (10-100x faster)

### Next Steps

- [ ] Implement RDS Proxy for connection pooling
- [ ] Set up Aurora Serverless
- [ ] Create DynamoDB Global Tables
- [ ] Implement Redis Cluster mode
- [ ] Set up AWS DMS for migration
- [ ] Configure automated monitoring and alerts

---

**Next:** [Quiz](./quiz.md)

**Previous:** [10 - Database Migration](./10-database-migration.md)
