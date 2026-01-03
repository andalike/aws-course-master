# 04 - RDS Security

## Security Overview

Amazon RDS security follows a defense-in-depth approach with multiple layers:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          RDS SECURITY LAYERS                                    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: NETWORK SECURITY                                              │   │
│  │  ├── VPC Isolation                                                       │   │
│  │  ├── Private Subnets                                                     │   │
│  │  ├── Security Groups                                                     │   │
│  │  ├── Network ACLs                                                        │   │
│  │  └── VPC Endpoints (Interface)                                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 2: ACCESS CONTROL                                                │   │
│  │  ├── IAM Policies (Management Plane)                                    │   │
│  │  ├── IAM Database Authentication                                        │   │
│  │  ├── Database Users/Roles (Data Plane)                                  │   │
│  │  └── RDS Proxy (Connection Management)                                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 3: DATA PROTECTION                                               │   │
│  │  ├── Encryption at Rest (KMS)                                           │   │
│  │  ├── Encryption in Transit (SSL/TLS)                                    │   │
│  │  └── Encrypted Snapshots/Backups                                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 4: AUDITING & COMPLIANCE                                         │   │
│  │  ├── Database Activity Streams                                          │   │
│  │  ├── CloudTrail (API Logging)                                           │   │
│  │  ├── Database Logs (Error, Slow Query, General)                         │   │
│  │  └── AWS Config Rules                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## VPC Placement

### Private Subnet Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                    VPC                                          │
│                            (10.0.0.0/16)                                       │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      AVAILABILITY ZONE A                                 │   │
│  │                                                                          │   │
│  │  ┌───────────────────────┐    ┌───────────────────────┐                 │   │
│  │  │   PUBLIC SUBNET       │    │   PRIVATE SUBNET      │                 │   │
│  │  │   (10.0.1.0/24)       │    │   (10.0.10.0/24)      │                 │   │
│  │  │                       │    │                       │                 │   │
│  │  │  ┌─────────────────┐  │    │  ┌─────────────────┐  │                 │   │
│  │  │  │  NAT Gateway    │  │    │  │  RDS Primary    │  │                 │   │
│  │  │  └─────────────────┘  │    │  └─────────────────┘  │                 │   │
│  │  │                       │    │                       │                 │   │
│  │  │  ┌─────────────────┐  │    │                       │                 │   │
│  │  │  │  ALB            │  │    │                       │                 │   │
│  │  │  └─────────────────┘  │    │                       │                 │   │
│  │  │         │             │    │                       │                 │   │
│  │  └─────────┼─────────────┘    └───────────────────────┘                 │   │
│  │            │                                                             │   │
│  └────────────┼─────────────────────────────────────────────────────────────┘   │
│               │                                                                  │
│  ┌────────────┼─────────────────────────────────────────────────────────────┐   │
│  │            │            AVAILABILITY ZONE B                               │   │
│  │            ▼                                                              │   │
│  │  ┌───────────────────────┐    ┌───────────────────────┐                  │   │
│  │  │   PUBLIC SUBNET       │    │   PRIVATE SUBNET      │                  │   │
│  │  │   (10.0.2.0/24)       │    │   (10.0.20.0/24)      │                  │   │
│  │  │                       │    │                       │                  │   │
│  │  │  ┌─────────────────┐  │    │  ┌─────────────────┐  │                  │   │
│  │  │  │  EC2 (App)      │  │    │  │  RDS Standby    │  │                  │   │
│  │  │  └─────────────────┘  │    │  └─────────────────┘  │                  │   │
│  │  │                       │    │                       │                  │   │
│  │  └───────────────────────┘    └───────────────────────┘                  │   │
│  │                                                                           │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │  DB SUBNET GROUP                                                         │    │
│  │  ├── Subnet: 10.0.10.0/24 (AZ-A)                                        │    │
│  │  └── Subnet: 10.0.20.0/24 (AZ-B)                                        │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Creating DB Subnet Group

```bash
# Create DB subnet group via CLI
aws rds create-db-subnet-group \
    --db-subnet-group-name my-db-subnet-group \
    --db-subnet-group-description "Private subnets for RDS" \
    --subnet-ids subnet-abc123 subnet-def456

# Terraform
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet-group"
  subnet_ids = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]

  tags = {
    Name = "Main DB Subnet Group"
  }
}
```

## Security Groups

### Security Group Configuration

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY GROUP RULES                                    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  APPLICATION SECURITY GROUP (sg-app-12345)                              │   │
│  │                                                                          │   │
│  │  Inbound:                                                                │   │
│  │  ├── Port 443 (HTTPS) from 0.0.0.0/0                                    │   │
│  │  └── Port 22 (SSH) from Bastion SG                                      │   │
│  │                                                                          │   │
│  │  Outbound:                                                               │   │
│  │  └── All traffic to 0.0.0.0/0                                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                              │                                                  │
│                              │ Allows connection                               │
│                              ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  RDS SECURITY GROUP (sg-rds-67890)                                      │   │
│  │                                                                          │   │
│  │  Inbound:                                                                │   │
│  │  ├── Port 3306 (MySQL) from sg-app-12345                                │   │
│  │  ├── Port 3306 (MySQL) from sg-lambda-11111                             │   │
│  │  └── Port 3306 (MySQL) from 10.0.0.0/16 (VPC CIDR)                      │   │
│  │                                                                          │   │
│  │  Outbound:                                                               │   │
│  │  └── (No outbound rules needed for RDS)                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Security Group Examples

```bash
# Create RDS security group (CLI)
aws ec2 create-security-group \
    --group-name rds-mysql-sg \
    --description "Security group for RDS MySQL" \
    --vpc-id vpc-12345678

# Add inbound rule for application servers
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-67890 \
    --protocol tcp \
    --port 3306 \
    --source-group sg-app-12345

# Add inbound rule for specific CIDR
aws ec2 authorize-security-group-ingress \
    --group-id sg-rds-67890 \
    --protocol tcp \
    --port 3306 \
    --cidr 10.0.0.0/16
```

### Terraform Security Group

```hcl
resource "aws_security_group" "rds" {
  name        = "rds-mysql-sg"
  description = "Security group for RDS MySQL"
  vpc_id      = aws_vpc.main.id

  # MySQL from application servers
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "MySQL from application servers"
  }

  # MySQL from Lambda functions
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda.id]
    description     = "MySQL from Lambda"
  }

  # No egress rules needed for RDS
  # RDS doesn't initiate outbound connections

  tags = {
    Name = "RDS MySQL Security Group"
  }
}
```

### Database Port Reference

| Database Engine | Default Port |
|-----------------|--------------|
| MySQL | 3306 |
| PostgreSQL | 5432 |
| MariaDB | 3306 |
| Oracle | 1521 |
| SQL Server | 1433 |
| Aurora MySQL | 3306 |
| Aurora PostgreSQL | 5432 |

## Encryption at Rest

### KMS Encryption

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        ENCRYPTION AT REST                                       │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         AWS KMS                                          │   │
│  │  ┌────────────────┐                                                     │   │
│  │  │ Customer       │  CMK (Customer Master Key)                          │   │
│  │  │ Master Key     │  ├── AWS Managed: aws/rds (default)                 │   │
│  │  └───────┬────────┘  └── Customer Managed: Custom key                   │   │
│  │          │                                                               │   │
│  │          │ Generates                                                     │   │
│  │          ▼                                                               │   │
│  │  ┌────────────────┐                                                     │   │
│  │  │ Data Key       │  Unique per RDS instance                            │   │
│  │  └───────┬────────┘                                                     │   │
│  │          │                                                               │   │
│  └──────────┼──────────────────────────────────────────────────────────────┘   │
│             │ Encrypts                                                          │
│             ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         RDS ENCRYPTED STORAGE                            │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ EBS Volume   │  │ Snapshots    │  │ Read Replicas│                   │   │
│  │  │ (Encrypted)  │  │ (Encrypted)  │  │ (Encrypted)  │                   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                   │   │
│  │                                                                          │   │
│  │  Also encrypted:                                                         │   │
│  │  ├── Automated backups                                                   │   │
│  │  ├── Transaction logs                                                    │   │
│  │  └── S3 backup copies                                                    │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Enabling Encryption

```bash
# Create encrypted RDS instance
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --storage-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012 \
    # ... other options

# Create encrypted snapshot from unencrypted instance
# Step 1: Create snapshot
aws rds create-db-snapshot \
    --db-instance-identifier mydb-unencrypted \
    --db-snapshot-identifier mydb-snapshot

# Step 2: Copy snapshot with encryption
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier mydb-snapshot \
    --target-db-snapshot-identifier mydb-snapshot-encrypted \
    --kms-key-id alias/aws/rds

# Step 3: Restore from encrypted snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-encrypted \
    --db-snapshot-identifier mydb-snapshot-encrypted
```

### Encryption Limitations

| Action | Possible? |
|--------|-----------|
| Encrypt new instance | Yes |
| Encrypt existing instance | No (must restore from encrypted snapshot) |
| Create encrypted replica from unencrypted source | No |
| Create unencrypted replica from encrypted source | No |
| Copy encrypted snapshot to another region | Yes (with target region KMS key) |
| Share encrypted snapshot | Yes (with shared KMS key) |

## Encryption in Transit (SSL/TLS)

### SSL/TLS Configuration

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        ENCRYPTION IN TRANSIT                                    │
│                                                                                 │
│   ┌─────────────┐         TLS 1.2/1.3         ┌─────────────────────────────┐  │
│   │ Application │ ◄══════════════════════════▶│        RDS Instance         │  │
│   │   Server    │                              │                             │  │
│   └─────────────┘                              │  ┌───────────────────────┐  │  │
│                                                │  │ AWS RDS CA Certificate│  │  │
│   SSL Connection Requirements:                 │  │                       │  │  │
│   1. Download RDS CA certificate               │  │ rds-ca-2019-root      │  │  │
│   2. Configure client to use certificate       │  │ rds-ca-rsa2048-g1     │  │  │
│   3. Enable SSL in connection string           │  │ rds-ca-rsa4096-g1     │  │  │
│                                                │  │ rds-ca-ecc384-g1      │  │  │
│                                                │  └───────────────────────┘  │  │
│                                                │                             │  │
│                                                └─────────────────────────────┘  │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Download RDS CA Certificate

```bash
# Download global bundle (all regions)
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem

# Download region-specific bundle
wget https://truststore.pki.rds.amazonaws.com/us-east-1/us-east-1-bundle.pem

# Download specific CA certificate
wget https://truststore.pki.rds.amazonaws.com/us-east-1/us-east-1-bundle.pem
```

### SSL Connection Examples

**MySQL:**
```python
import mysql.connector

connection = mysql.connector.connect(
    host='mydb.abc123.us-east-1.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='password',
    database='myapp',
    ssl_ca='/path/to/global-bundle.pem',
    ssl_verify_cert=True
)

# Or using connection string
# mysql://admin:password@mydb.abc123.us-east-1.rds.amazonaws.com:3306/myapp?ssl-ca=/path/to/global-bundle.pem&ssl-mode=VERIFY_IDENTITY
```

**PostgreSQL:**
```python
import psycopg2

connection = psycopg2.connect(
    host='mydb.abc123.us-east-1.rds.amazonaws.com',
    port=5432,
    user='postgres',
    password='password',
    database='myapp',
    sslmode='verify-full',
    sslrootcert='/path/to/global-bundle.pem'
)

# Connection string
# postgresql://postgres:password@mydb.abc123.us-east-1.rds.amazonaws.com:5432/myapp?sslmode=verify-full&sslrootcert=/path/to/global-bundle.pem
```

**JDBC (Java):**
```java
// MySQL
String url = "jdbc:mysql://mydb.abc123.us-east-1.rds.amazonaws.com:3306/myapp" +
    "?useSSL=true" +
    "&requireSSL=true" +
    "&verifyServerCertificate=true" +
    "&trustCertificateKeyStoreUrl=file:/path/to/truststore.jks" +
    "&trustCertificateKeyStorePassword=changeit";

// PostgreSQL
String url = "jdbc:postgresql://mydb.abc123.us-east-1.rds.amazonaws.com:5432/myapp" +
    "?ssl=true" +
    "&sslmode=verify-full" +
    "&sslrootcert=/path/to/global-bundle.pem";
```

### Enforce SSL Connections

```sql
-- MySQL: Require SSL for specific user
ALTER USER 'myuser'@'%' REQUIRE SSL;

-- MySQL: Require SSL for all new connections (parameter group)
-- Set parameter: require_secure_transport = 1

-- PostgreSQL: Require SSL in pg_hba.conf (via parameter group)
-- rds.force_ssl = 1

-- SQL Server: Force encryption (option group)
-- Enable FORCE_SSL option
```

## IAM Database Authentication

### How It Works

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        IAM DATABASE AUTHENTICATION                              │
│                                                                                 │
│  ┌─────────────────┐                                                           │
│  │   Application   │                                                           │
│  │    (EC2/Lambda) │                                                           │
│  └────────┬────────┘                                                           │
│           │                                                                     │
│           │ 1. Request token with IAM credentials                              │
│           ▼                                                                     │
│  ┌─────────────────┐                                                           │
│  │   AWS STS       │                                                           │
│  │                 │  2. Returns authentication token (15 min validity)        │
│  └────────┬────────┘                                                           │
│           │                                                                     │
│           │ 3. Connect using token as password                                 │
│           ▼                                                                     │
│  ┌─────────────────┐                                                           │
│  │   RDS Instance  │                                                           │
│  │                 │  4. Validates token with IAM                              │
│  │   ┌──────────┐  │                                                           │
│  │   │ IAM Auth │  │  5. Connection established                                │
│  │   │ enabled  │  │                                                           │
│  │   └──────────┘  │                                                           │
│  └─────────────────┘                                                           │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Enable IAM Authentication

```bash
# Enable IAM authentication on RDS instance
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --enable-iam-database-authentication \
    --apply-immediately
```

### Create Database User for IAM

```sql
-- MySQL: Create user for IAM authentication
CREATE USER 'iam_user'@'%' IDENTIFIED WITH AWSAuthenticationPlugin AS 'RDS';
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'iam_user'@'%';

-- PostgreSQL: Create user for IAM authentication
CREATE USER iam_user;
GRANT rds_iam TO iam_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO iam_user;
```

### IAM Policy for Database Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rds-db:connect"
            ],
            "Resource": [
                "arn:aws:rds-db:us-east-1:123456789012:dbuser:db-ABCDEFGHIJKL/iam_user"
            ]
        }
    ]
}
```

### Connect Using IAM Authentication

**Python (MySQL):**
```python
import boto3
import mysql.connector

# Generate authentication token
rds_client = boto3.client('rds', region_name='us-east-1')

token = rds_client.generate_db_auth_token(
    DBHostname='mydb.abc123.us-east-1.rds.amazonaws.com',
    Port=3306,
    DBUsername='iam_user',
    Region='us-east-1'
)

# Connect using token as password
connection = mysql.connector.connect(
    host='mydb.abc123.us-east-1.rds.amazonaws.com',
    port=3306,
    user='iam_user',
    password=token,
    database='myapp',
    ssl_ca='/path/to/global-bundle.pem'
)
```

**Python (PostgreSQL):**
```python
import boto3
import psycopg2

# Generate authentication token
rds_client = boto3.client('rds', region_name='us-east-1')

token = rds_client.generate_db_auth_token(
    DBHostname='mydb.abc123.us-east-1.rds.amazonaws.com',
    Port=5432,
    DBUsername='iam_user',
    Region='us-east-1'
)

# Connect using token as password
connection = psycopg2.connect(
    host='mydb.abc123.us-east-1.rds.amazonaws.com',
    port=5432,
    user='iam_user',
    password=token,
    database='myapp',
    sslmode='verify-full',
    sslrootcert='/path/to/global-bundle.pem'
)
```

### IAM Authentication Limitations

| Engine | Supported | Max Connections/sec |
|--------|-----------|---------------------|
| MySQL | Yes | 256 |
| PostgreSQL | Yes | 256 |
| MariaDB | Yes | 256 |
| Aurora MySQL | Yes | 256 |
| Aurora PostgreSQL | Yes | 256 |
| Oracle | No | N/A |
| SQL Server | No | N/A |

## RDS Proxy

### Overview

RDS Proxy provides connection pooling and improved security for database connections.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           RDS PROXY ARCHITECTURE                                │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                         APPLICATION LAYER                                  │ │
│  │                                                                            │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │ │
│  │  │ Lambda  │  │ Lambda  │  │  EC2    │  │  ECS    │  │  EKS    │         │ │
│  │  │ Func 1  │  │ Func 2  │  │ Server  │  │ Service │  │  Pod    │         │ │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘         │ │
│  │       │            │            │            │            │               │ │
│  └───────┼────────────┼────────────┼────────────┼────────────┼───────────────┘ │
│          │            │            │            │            │                  │
│          └────────────┴────────────┴────────────┴────────────┘                  │
│                                    │                                            │
│                        Many short-lived connections                             │
│                                    ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                           RDS PROXY                                        │ │
│  │                                                                            │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    CONNECTION POOL                                  │  │ │
│  │  │                                                                     │  │ │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │  │ │
│  │  │  │ C1  │ │ C2  │ │ C3  │ │ C4  │ │ C5  │ │ C6  │ │ C7  │ │ C8  │  │  │ │
│  │  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘  │  │ │
│  │  │                                                                     │  │ │
│  │  └─────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                            │ │
│  │  Features:                                                                 │ │
│  │  ├── Connection pooling and sharing                                       │ │
│  │  ├── IAM/Secrets Manager authentication                                   │ │
│  │  ├── Automatic failover handling                                          │ │
│  │  └── Reduced database resource consumption                                │ │
│  │                                                                            │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                            │
│                       Few long-lived connections                               │
│                                    ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                         RDS INSTANCE                                       │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐   │ │
│  │  │                    DATABASE CONNECTIONS                             │   │ │
│  │  │         (Much fewer connections than without proxy)                 │   │ │
│  │  └────────────────────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Creating RDS Proxy

```bash
# Create RDS Proxy
aws rds create-db-proxy \
    --db-proxy-name my-proxy \
    --engine-family MYSQL \
    --auth '[{
        "AuthScheme": "SECRETS",
        "SecretArn": "arn:aws:secretsmanager:us-east-1:123456789012:secret:mydb-credentials",
        "IAMAuth": "REQUIRED"
    }]' \
    --role-arn arn:aws:iam::123456789012:role/RDSProxyRole \
    --vpc-subnet-ids subnet-abc123 subnet-def456 \
    --vpc-security-group-ids sg-proxy-12345 \
    --require-tls

# Register target
aws rds register-db-proxy-targets \
    --db-proxy-name my-proxy \
    --db-instance-identifiers mydb
```

### RDS Proxy Terraform

```hcl
# Secrets Manager secret for database credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name = "mydb-credentials"
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = "admin"
    password = var.db_password
  })
}

# IAM role for RDS Proxy
resource "aws_iam_role" "rds_proxy" {
  name = "rds-proxy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "rds.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "rds_proxy" {
  name = "rds-proxy-policy"
  role = aws_iam_role.rds_proxy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [
        "secretsmanager:GetSecretValue"
      ]
      Effect   = "Allow"
      Resource = aws_secretsmanager_secret.db_credentials.arn
    }]
  })
}

# RDS Proxy
resource "aws_db_proxy" "main" {
  name                   = "my-db-proxy"
  debug_logging          = false
  engine_family          = "MYSQL"
  idle_client_timeout    = 1800
  require_tls            = true
  role_arn               = aws_iam_role.rds_proxy.arn
  vpc_security_group_ids = [aws_security_group.rds_proxy.id]
  vpc_subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  auth {
    auth_scheme               = "SECRETS"
    iam_auth                  = "REQUIRED"
    secret_arn                = aws_secretsmanager_secret.db_credentials.arn
  }

  tags = {
    Name = "My DB Proxy"
  }
}

# Target group
resource "aws_db_proxy_default_target_group" "main" {
  db_proxy_name = aws_db_proxy.main.name

  connection_pool_config {
    connection_borrow_timeout    = 120
    max_connections_percent      = 100
    max_idle_connections_percent = 50
  }
}

# Target
resource "aws_db_proxy_target" "main" {
  db_instance_identifier = aws_db_instance.mysql.id
  db_proxy_name          = aws_db_proxy.main.name
  target_group_name      = aws_db_proxy_default_target_group.main.name
}

# Output proxy endpoint
output "proxy_endpoint" {
  value = aws_db_proxy.main.endpoint
}
```

## Security Best Practices

### Checklist

| Category | Best Practice | Priority |
|----------|---------------|----------|
| **Network** | Place RDS in private subnets | Critical |
| **Network** | Use security groups (not public access) | Critical |
| **Network** | Disable public accessibility | Critical |
| **Encryption** | Enable encryption at rest | Critical |
| **Encryption** | Enforce SSL/TLS connections | Critical |
| **Access** | Use IAM authentication where possible | High |
| **Access** | Rotate database credentials regularly | High |
| **Access** | Use Secrets Manager for credentials | High |
| **Access** | Implement least privilege access | High |
| **Monitoring** | Enable database activity logging | High |
| **Monitoring** | Enable CloudTrail for API logging | High |
| **Updates** | Enable auto minor version upgrade | Medium |
| **Updates** | Plan major version upgrades | Medium |
| **Backup** | Enable automated backups | Critical |
| **Backup** | Encrypt backups | Critical |

### AWS Config Rules for RDS

```yaml
# Example AWS Config rules for RDS
ConfigRules:
  - rds-instance-public-access-check
  - rds-storage-encrypted
  - rds-instance-deletion-protection-enabled
  - rds-multi-az-support
  - rds-in-backup-plan
  - rds-logging-enabled
  - rds-snapshot-encrypted
```

## Summary

- Place RDS in private subnets with proper security groups
- Enable encryption at rest (KMS) and in transit (SSL/TLS)
- Use IAM authentication for supported engines
- Implement RDS Proxy for connection pooling and enhanced security
- Follow the principle of least privilege for database access
- Enable logging and monitoring for audit and compliance

---

**Next:** [05 - RDS Backup and Restore](./05-rds-backup-restore.md)

**Previous:** [03 - RDS High Availability](./03-rds-high-availability.md)
