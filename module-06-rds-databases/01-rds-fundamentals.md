# 01 - RDS Fundamentals

## What is Amazon RDS?

Amazon Relational Database Service (RDS) is a managed service that makes it easy to set up, operate, and scale relational databases in the cloud. RDS handles routine database tasks such as provisioning, patching, backup, recovery, failure detection, and repair.

## Managed vs Self-Managed Databases

### Self-Managed (EC2-Based) Database

When you run a database on EC2, YOU are responsible for:

```
+------------------------------------------------------------------+
|                    YOUR RESPONSIBILITIES                          |
+------------------------------------------------------------------+
| - EC2 instance management (sizing, purchasing options)           |
| - Operating system installation and patching                      |
| - Database software installation and configuration               |
| - Database patching and upgrades                                  |
| - Backup implementation and management                            |
| - High availability setup (clustering, replication)              |
| - Disaster recovery planning and testing                          |
| - Security hardening                                              |
| - Performance tuning and optimization                             |
| - Scaling (vertical and horizontal)                               |
| - Monitoring and alerting setup                                   |
+------------------------------------------------------------------+
```

### AWS Managed (RDS) Database

With RDS, AWS handles most operational tasks:

```
+------------------------------------------------------------------+
|                    AWS RESPONSIBILITIES                           |
+------------------------------------------------------------------+
| - Hardware provisioning                                           |
| - Database setup                                                  |
| - Patching (OS and database engine)                              |
| - Automated backups                                               |
| - High availability (Multi-AZ)                                    |
| - Automatic failover                                              |
| - Read replica management                                         |
| - Monitoring (CloudWatch integration)                             |
| - Storage management and scaling                                  |
+------------------------------------------------------------------+

+------------------------------------------------------------------+
|                   YOUR RESPONSIBILITIES                           |
+------------------------------------------------------------------+
| - Schema design and optimization                                  |
| - Query optimization                                              |
| - Application-level settings                                      |
| - Data management                                                 |
| - Access control and security policies                            |
| - Parameter group configuration                                   |
| - Choosing instance type and storage                              |
+------------------------------------------------------------------+
```

## Supported Database Engines

Amazon RDS supports six database engines, each with specific versions and features:

### 1. MySQL

```
Engine: MySQL
Versions: 5.7, 8.0
License: GPL (Open Source)
Use Cases: Web applications, e-commerce, content management

Key Features:
- InnoDB storage engine (default)
- Full-text search
- JSON support
- Spatial data support
- Replication support
```

**Connection String Example:**
```python
# Python (mysql-connector-python)
import mysql.connector

connection = mysql.connector.connect(
    host='mydb.123456789012.us-east-1.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='your-password',
    database='myapp'
)

# JDBC (Java)
# jdbc:mysql://mydb.123456789012.us-east-1.rds.amazonaws.com:3306/myapp

# Connection String (Generic)
# mysql://admin:password@mydb.123456789012.us-east-1.rds.amazonaws.com:3306/myapp
```

### 2. PostgreSQL

```
Engine: PostgreSQL
Versions: 12, 13, 14, 15, 16
License: PostgreSQL License (Open Source)
Use Cases: Complex queries, geospatial, analytics, data warehousing

Key Features:
- Advanced data types (JSON, arrays, hstore)
- Full-text search
- PostGIS extension for geospatial
- Parallel query execution
- Materialized views
- Table partitioning
```

**Connection String Example:**
```python
# Python (psycopg2)
import psycopg2

connection = psycopg2.connect(
    host='mydb.123456789012.us-east-1.rds.amazonaws.com',
    port=5432,
    user='postgres',
    password='your-password',
    database='myapp'
)

# JDBC (Java)
# jdbc:postgresql://mydb.123456789012.us-east-1.rds.amazonaws.com:5432/myapp

# Connection String (Generic)
# postgresql://postgres:password@mydb.123456789012.us-east-1.rds.amazonaws.com:5432/myapp
```

### 3. MariaDB

```
Engine: MariaDB
Versions: 10.4, 10.5, 10.6, 10.11
License: GPL (Open Source)
Use Cases: MySQL alternative, high-performance OLTP

Key Features:
- MySQL compatible (fork of MySQL)
- Aria storage engine
- Thread pool
- Parallel replication
- Query optimizer improvements
```

**Connection String Example:**
```python
# Python (mariadb connector)
import mariadb

connection = mariadb.connect(
    host='mydb.123456789012.us-east-1.rds.amazonaws.com',
    port=3306,
    user='admin',
    password='your-password',
    database='myapp'
)

# JDBC (Java)
# jdbc:mariadb://mydb.123456789012.us-east-1.rds.amazonaws.com:3306/myapp
```

### 4. Oracle

```
Engine: Oracle Database
Versions: 19c, 21c
License: BYOL (Bring Your Own License) or License Included
Use Cases: Enterprise applications, ERP, complex transactions

Key Features:
- Enterprise Edition features (with licensing)
- RAC support (not on RDS, use RAC on EC2)
- Advanced security
- Data Guard (partially via Multi-AZ)
- Partitioning (Enterprise Edition)
```

**Connection String Example:**
```python
# Python (cx_Oracle)
import cx_Oracle

dsn = cx_Oracle.makedsn(
    'mydb.123456789012.us-east-1.rds.amazonaws.com',
    1521,
    service_name='ORCL'
)
connection = cx_Oracle.connect(user='admin', password='your-password', dsn=dsn)

# JDBC (Java)
# jdbc:oracle:thin:@mydb.123456789012.us-east-1.rds.amazonaws.com:1521/ORCL

# TNS Connection String
# (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=mydb.123456789012.us-east-1.rds.amazonaws.com)(PORT=1521))(CONNECT_DATA=(SID=ORCL)))
```

### 5. SQL Server

```
Engine: Microsoft SQL Server
Versions: 2017, 2019, 2022
Editions: Express, Web, Standard, Enterprise
License: License Included or BYOL
Use Cases: .NET applications, enterprise systems, BI

Key Features:
- Native Windows integration
- T-SQL
- SQL Server Agent (limited in RDS)
- Always On (via Multi-AZ)
- Full-text search
```

**Connection String Example:**
```python
# Python (pyodbc)
import pyodbc

connection = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=mydb.123456789012.us-east-1.rds.amazonaws.com,1433;'
    'DATABASE=myapp;'
    'UID=admin;'
    'PWD=your-password'
)

# JDBC (Java)
# jdbc:sqlserver://mydb.123456789012.us-east-1.rds.amazonaws.com:1433;databaseName=myapp

# .NET Connection String
# Server=mydb.123456789012.us-east-1.rds.amazonaws.com,1433;Database=myapp;User Id=admin;Password=your-password;
```

### 6. Amazon Aurora (MySQL/PostgreSQL Compatible)

```
Engine: Aurora MySQL or Aurora PostgreSQL
Compatibility: MySQL 5.7/8.0, PostgreSQL 12-16
License: AWS Proprietary
Use Cases: Cloud-native, high-performance, enterprise applications

Key Features:
- 5x throughput of MySQL
- 3x throughput of PostgreSQL
- Distributed, fault-tolerant storage
- Auto-scaling replicas
- Serverless option
- Global Database
```

## Engine Comparison Matrix

| Feature | MySQL | PostgreSQL | MariaDB | Oracle | SQL Server | Aurora |
|---------|-------|------------|---------|--------|------------|--------|
| **License Cost** | Free | Free | Free | $$$$ | $$$ | $ |
| **Max Storage** | 64 TB | 64 TB | 64 TB | 64 TB | 16 TB | 128 TB |
| **Read Replicas** | 15 | 15 | 15 | 5 | 5 | 15 |
| **Multi-AZ** | Yes | Yes | Yes | Yes | Yes | Built-in |
| **Encryption** | Yes | Yes | Yes | Yes | Yes | Yes |
| **IAM Auth** | Yes | Yes | Yes | No | No | Yes |
| **Performance Insights** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Blue/Green Deployments** | Yes | Yes | Yes | No | No | Yes |

## Pricing Comparison (us-east-1, db.r6g.large, Single-AZ)

| Engine | On-Demand (/hour) | Monthly Estimate | License |
|--------|-------------------|------------------|---------|
| MySQL | $0.178 | ~$130 | Included |
| PostgreSQL | $0.178 | ~$130 | Included |
| MariaDB | $0.178 | ~$130 | Included |
| Oracle SE2 (LI) | $0.484 | ~$353 | Included |
| Oracle SE2 (BYOL) | $0.178 | ~$130 | Customer |
| SQL Server SE (LI) | $0.690 | ~$503 | Included |
| SQL Server SE (BYOL) | $0.178 | ~$130 | Customer |
| Aurora MySQL | $0.210 | ~$153 | Included |
| Aurora PostgreSQL | $0.210 | ~$153 | Included |

**Note:** Prices are approximate and may vary. Always check current AWS pricing.

## When to Use Each Engine

### Choose MySQL When:
- Building web applications (LAMP stack)
- You need wide ecosystem support
- Simple replication is sufficient
- Budget is a concern
- Your team has MySQL expertise

### Choose PostgreSQL When:
- You need advanced data types (JSON, arrays, geospatial)
- Complex queries are common
- You need strong ACID compliance
- PostGIS for geospatial applications
- Data warehousing with complex analytics

### Choose MariaDB When:
- Migrating from MySQL
- You want MySQL compatibility with improvements
- Open-source commitment is important
- You need thread pool for connection handling

### Choose Oracle When:
- Running Oracle-based enterprise applications
- You have existing Oracle licenses (BYOL)
- PL/SQL stored procedures are required
- Enterprise features are needed
- Regulatory compliance requires Oracle

### Choose SQL Server When:
- Running .NET applications
- Microsoft ecosystem integration needed
- Migrating from on-premises SQL Server
- You have existing SQL Server licenses
- BI and reporting with SSRS/SSIS

### Choose Aurora When:
- Cloud-native development
- High performance requirements
- Need automatic scaling
- MySQL/PostgreSQL compatible
- Enterprise-grade availability

## RDS Architecture Overview

```
                              ┌─────────────────────────────┐
                              │         Region              │
                              │  ┌──────────────────────┐   │
                              │  │   Availability Zone 1 │   │
┌──────────────┐              │  │  ┌────────────────┐  │   │
│              │   ┌──────────┼──┼──│  Primary RDS   │  │   │
│  Application ├───│ Endpoint │  │  │   Instance     │  │   │
│    Server    │   └──────────┼──┼──│                │  │   │
│              │              │  │  │  ┌──────────┐  │  │   │
└──────────────┘              │  │  │  │  EBS     │  │  │   │
                              │  │  │  │ Storage  │  │  │   │
                              │  │  │  └──────────┘  │  │   │
                              │  │  └────────────────┘  │   │
                              │  │                      │   │
                              │  └──────────────────────┘   │
                              │                             │
                              │  ┌──────────────────────┐   │
                              │  │   Availability Zone 2 │   │
                              │  │  ┌────────────────┐  │   │
                              │  │  │  Standby RDS   │  │   │
     Synchronous              │  │  │  (Multi-AZ)    │◄─┼───┼── Sync
     Replication              │  │  │                │  │   │   Replication
                              │  │  │  ┌──────────┐  │  │   │
                              │  │  │  │  EBS     │  │  │   │
                              │  │  │  │ Storage  │  │  │   │
                              │  │  │  └──────────┘  │  │   │
                              │  │  └────────────────┘  │   │
                              │  └──────────────────────┘   │
                              │                             │
                              │      ┌───────────────┐      │
                              │      │  Automated    │      │
                              │      │   Backups     │      │
                              │      │     (S3)      │      │
                              │      └───────────────┘      │
                              └─────────────────────────────┘
```

## Key RDS Concepts

### 1. DB Instance
The basic building block of RDS. A DB instance is an isolated database environment running in the cloud.

### 2. DB Instance Class
Determines compute and memory capacity:
- **Standard (m classes)**: Balanced compute, memory, networking
- **Memory Optimized (r, x classes)**: High memory-to-CPU ratio
- **Burstable (t classes)**: Variable workloads, cost-effective

### 3. DB Instance Storage
- **General Purpose SSD (gp2/gp3)**: Cost-effective, balanced performance
- **Provisioned IOPS SSD (io1/io2)**: High-performance, I/O-intensive
- **Magnetic**: Legacy, previous-generation

### 4. DB Parameter Groups
Collection of engine configuration parameters:
```sql
-- Example MySQL parameters
max_connections = 150
innodb_buffer_pool_size = 8589934592  -- 8GB
slow_query_log = 1
long_query_time = 2
```

### 5. DB Option Groups
Enable and configure additional features:
- Oracle: APEX, OEM, Timezone
- SQL Server: Native backup/restore
- MySQL: memcached plugin

### 6. DB Subnet Groups
Define which subnets and AZs can be used:
```
DB Subnet Group: my-db-subnet-group
├── Subnet: subnet-abc123 (us-east-1a) - 10.0.1.0/24
├── Subnet: subnet-def456 (us-east-1b) - 10.0.2.0/24
└── Subnet: subnet-ghi789 (us-east-1c) - 10.0.3.0/24
```

## RDS Endpoints

| Endpoint Type | Description | Use Case |
|---------------|-------------|----------|
| **Instance Endpoint** | Direct connection to specific instance | Troubleshooting, specific instance access |
| **Cluster Endpoint** | Connects to primary (Aurora) | Write operations |
| **Reader Endpoint** | Load-balanced read replicas (Aurora) | Read operations |
| **Custom Endpoint** | User-defined group of instances (Aurora) | Analytics, specific workloads |

**Endpoint Format:**
```
<db-instance-identifier>.<random-id>.<region>.rds.amazonaws.com

Example:
mydb.abc123xyz.us-east-1.rds.amazonaws.com
```

## Limitations and Restrictions

### What You CAN'T Do with RDS:
- SSH into the database server
- Install custom software on the server
- Access the underlying file system
- Use operating system commands
- Configure network settings directly
- Access certain system tables and procedures

### What You CAN Do:
- Create/modify/delete databases
- Create/manage users and permissions
- Execute SQL queries and stored procedures
- Configure parameter groups
- Set up replication
- Manage backups
- Use supported extensions

## AWS CLI Commands

### List Available Engine Versions
```bash
# List MySQL versions
aws rds describe-db-engine-versions \
    --engine mysql \
    --query 'DBEngineVersions[*].[EngineVersion,Status]' \
    --output table

# List PostgreSQL versions
aws rds describe-db-engine-versions \
    --engine postgres \
    --query 'DBEngineVersions[*].[EngineVersion,Status]' \
    --output table
```

### List Available Instance Classes
```bash
aws rds describe-orderable-db-instance-options \
    --engine mysql \
    --engine-version 8.0 \
    --query 'OrderableDBInstanceOptions[*].DBInstanceClass' \
    --output text | tr '\t' '\n' | sort -u
```

### Describe RDS Instances
```bash
aws rds describe-db-instances \
    --query 'DBInstances[*].[DBInstanceIdentifier,Engine,DBInstanceClass,DBInstanceStatus]' \
    --output table
```

## Summary

- RDS is AWS's managed relational database service
- Supports 6 engines: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, and Aurora
- AWS handles operational tasks; you focus on schema and application
- Choose engine based on licensing, features, expertise, and ecosystem
- Aurora provides cloud-native performance with MySQL/PostgreSQL compatibility
- Pricing varies by engine, instance class, and licensing model

---

**Next:** [02 - RDS Instance Setup](./02-rds-instance-setup.md)

**Previous:** [README](./README.md)
