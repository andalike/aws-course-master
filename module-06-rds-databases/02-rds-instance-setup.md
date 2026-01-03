# 02 - RDS Instance Setup

## Creating RDS Instances

This section covers the complete process of creating and configuring RDS instances, including instance classes, storage options, and network configuration.

## DB Instance Classes

RDS offers various instance classes optimized for different workloads:

### Instance Class Families

```
┌────────────────────────────────────────────────────────────────────┐
│                    RDS INSTANCE CLASSES                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STANDARD (db.m*)           MEMORY OPTIMIZED (db.r*)               │
│  ├── db.m7g (Graviton3)     ├── db.r7g (Graviton3)                │
│  ├── db.m6g (Graviton2)     ├── db.r6g (Graviton2)                │
│  ├── db.m6i (Intel)         ├── db.r6i (Intel)                    │
│  ├── db.m5 (Intel)          ├── db.r5 (Intel)                     │
│  └── db.m4 (Intel)          ├── db.x2g (Graviton2)                │
│                              └── db.x1e (Intel)                    │
│                                                                     │
│  BURSTABLE (db.t*)          MEMORY OPTIMIZED (db.z*)              │
│  ├── db.t4g (Graviton2)     └── db.z1d (Intel + NVMe)             │
│  ├── db.t3 (Intel)                                                 │
│  └── db.t2 (Intel)                                                 │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Instance Class Details

| Class | vCPU Range | Memory Range | Network | Use Case |
|-------|------------|--------------|---------|----------|
| **db.t4g** | 2-8 | 1-32 GiB | Up to 5 Gbps | Dev/Test, small workloads |
| **db.t3** | 2-8 | 1-32 GiB | Up to 5 Gbps | Variable workloads |
| **db.m6g** | 2-64 | 8-256 GiB | Up to 25 Gbps | General purpose production |
| **db.m7g** | 2-64 | 8-256 GiB | Up to 30 Gbps | Latest generation, best value |
| **db.r6g** | 2-64 | 16-512 GiB | Up to 25 Gbps | Memory-intensive workloads |
| **db.r7g** | 2-64 | 16-512 GiB | Up to 30 Gbps | Latest memory-optimized |
| **db.x2g** | 4-64 | 64-1024 GiB | Up to 25 Gbps | In-memory databases |

### Burstable Instance CPU Credits

Burstable instances (db.t*) use CPU credits:

```
┌────────────────────────────────────────────────────────────────────┐
│                    CPU CREDIT SYSTEM                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │  Baseline    │     │    Credit    │     │    Burst     │       │
│  │  Performance │────▶│    Balance   │────▶│  Performance │       │
│  │   (20-40%)   │     │  (Accrues)   │     │    (100%)    │       │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│                                                                     │
│  Instance Type    Baseline    Credits/Hour    Max Credits          │
│  ───────────────────────────────────────────────────────           │
│  db.t3.micro      10%         6               144                  │
│  db.t3.small      20%         12              288                  │
│  db.t3.medium     20%         24              576                  │
│  db.t3.large      30%         36              864                  │
│  db.t3.xlarge     40%         96              2304                 │
│  db.t3.2xlarge    40%         192             4608                 │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

**Unlimited Mode:** For t3/t4g instances, you can enable unlimited mode to burst beyond credit balance (charged per vCPU-hour).

### Instance Class Pricing Comparison (us-east-1, MySQL, Single-AZ)

| Instance | vCPU | Memory | On-Demand/hr | Monthly | Reserved 1yr |
|----------|------|--------|--------------|---------|--------------|
| db.t3.micro | 2 | 1 GiB | $0.017 | $12 | $8 |
| db.t3.small | 2 | 2 GiB | $0.034 | $25 | $16 |
| db.t3.medium | 2 | 4 GiB | $0.068 | $50 | $32 |
| db.m6g.large | 2 | 8 GiB | $0.154 | $112 | $70 |
| db.m6g.xlarge | 4 | 16 GiB | $0.308 | $225 | $140 |
| db.r6g.large | 2 | 16 GiB | $0.210 | $153 | $96 |
| db.r6g.xlarge | 4 | 32 GiB | $0.420 | $307 | $192 |

## Storage Types

RDS offers four storage types with different performance characteristics:

### Storage Type Comparison

```
┌────────────────────────────────────────────────────────────────────┐
│                     RDS STORAGE TYPES                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   General       │  │   Provisioned   │  │   Magnetic      │    │
│  │   Purpose SSD   │  │   IOPS SSD      │  │   (Legacy)      │    │
│  │   (gp2/gp3)     │  │   (io1/io2)     │  │                 │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                     │
│     Balanced            High Performance      Previous Gen         │
│     Cost-Effective      I/O Intensive         Backward Compat      │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### General Purpose SSD (gp2)

| Attribute | Value |
|-----------|-------|
| Size Range | 20 GiB - 64 TiB |
| Baseline IOPS | 3 IOPS/GiB (min 100) |
| Max IOPS | 16,000 |
| Burst IOPS | 3,000 (volumes < 1 TiB) |
| Throughput | 250 MiB/s max |
| Latency | Single-digit milliseconds |
| Cost | ~$0.115/GiB/month |

**IOPS Calculation for gp2:**
```
IOPS = Volume Size (GiB) × 3

Examples:
- 20 GiB  → 100 IOPS (minimum)
- 100 GiB → 300 IOPS
- 500 GiB → 1,500 IOPS
- 5,334 GiB → 16,000 IOPS (maximum)
```

### General Purpose SSD (gp3)

| Attribute | Value |
|-----------|-------|
| Size Range | 20 GiB - 64 TiB |
| Baseline IOPS | 3,000 (independent of size) |
| Max IOPS | 16,000 (provisionable) |
| Baseline Throughput | 125 MiB/s |
| Max Throughput | 1,000 MiB/s (provisionable) |
| Latency | Single-digit milliseconds |
| Cost | ~$0.08/GiB/month + IOPS/throughput |

**gp3 Pricing:**
```
Storage: $0.08/GiB/month
IOPS: $0.005/provisioned IOPS/month (above 3,000)
Throughput: $0.04/provisioned MiB/s/month (above 125 MiB/s)
```

### Provisioned IOPS SSD (io1/io2)

| Attribute | io1 | io2 |
|-----------|-----|-----|
| Size Range | 100 GiB - 64 TiB | 100 GiB - 64 TiB |
| IOPS Range | 1,000 - 64,000 | 1,000 - 64,000 |
| Max IOPS/GiB | 50:1 | 500:1 |
| Durability | 99.8% - 99.9% | 99.999% |
| Latency | Sub-millisecond | Sub-millisecond |

**io1 Pricing:**
```
Storage: $0.125/GiB/month
IOPS: $0.065/provisioned IOPS/month

Example (1 TiB + 10,000 IOPS):
Storage: 1024 × $0.125 = $128/month
IOPS: 10000 × $0.065 = $650/month
Total: $778/month
```

### Storage Type Decision Matrix

| Requirement | Recommended Storage |
|-------------|---------------------|
| Development/Testing | gp2 or gp3 (small) |
| General Production | gp3 |
| Variable Workloads | gp2 (burst capable) |
| High IOPS (>16,000) | io1/io2 |
| Consistent Low Latency | io1/io2 |
| Cost-Sensitive | gp3 |
| Legacy/Archive | Magnetic |

## Creating an RDS Instance

### Method 1: AWS Console

1. **Navigate to RDS Console**
   - Open AWS Console > RDS
   - Click "Create database"

2. **Choose Creation Method**
   - Standard Create (full configuration)
   - Easy Create (default settings)

3. **Engine Selection**
   ```
   Engine Options:
   ├── Aurora (MySQL/PostgreSQL)
   ├── MySQL
   ├── MariaDB
   ├── PostgreSQL
   ├── Oracle
   └── SQL Server
   ```

4. **Template Selection**
   - Production
   - Dev/Test
   - Free Tier (db.t3.micro/db.t2.micro)

5. **Configure Settings**
   - DB Instance Identifier
   - Master Username
   - Master Password

### Method 2: AWS CLI

```bash
# Create a MySQL RDS Instance
aws rds create-db-instance \
    --db-instance-identifier mydb-mysql \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --engine-version 8.0 \
    --master-username admin \
    --master-user-password "YourSecurePassword123!" \
    --allocated-storage 100 \
    --storage-type gp3 \
    --iops 3000 \
    --storage-throughput 125 \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name my-subnet-group \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "Mon:04:00-Mon:05:00" \
    --multi-az \
    --publicly-accessible false \
    --storage-encrypted \
    --kms-key-id alias/aws/rds \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --enable-cloudwatch-logs-exports '["error","slowquery","general"]' \
    --deletion-protection \
    --tags Key=Environment,Value=Production Key=Application,Value=MyApp
```

### Method 3: AWS CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'RDS MySQL Instance'

Parameters:
  DBInstanceClass:
    Type: String
    Default: db.t3.medium
    AllowedValues:
      - db.t3.micro
      - db.t3.small
      - db.t3.medium
      - db.m6g.large
      - db.r6g.large
    Description: Instance class for RDS

  DBName:
    Type: String
    Default: myappdb
    MinLength: 1
    MaxLength: 64

  MasterUsername:
    Type: String
    Default: admin
    NoEcho: true

  MasterPassword:
    Type: String
    NoEcho: true
    MinLength: 8

Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-subnet-group

  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref AppSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${AWS::StackName}-rds-sg

  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Family: mysql8.0
      Description: Custom parameter group
      Parameters:
        max_connections: '200'
        innodb_buffer_pool_size: '{DBInstanceClassMemory*3/4}'
        slow_query_log: '1'
        long_query_time: '2'

  RDSInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub ${AWS::StackName}-mysql
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0'
      DBName: !Ref DBName
      MasterUsername: !Ref MasterUsername
      MasterUserPassword: !Ref MasterPassword
      AllocatedStorage: 100
      StorageType: gp3
      Iops: 3000
      StorageThroughput: 125
      MultiAZ: true
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      BackupRetentionPeriod: 7
      PreferredBackupWindow: '03:00-04:00'
      PreferredMaintenanceWindow: 'Mon:04:00-Mon:05:00'
      StorageEncrypted: true
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 7
      EnableCloudwatchLogsExports:
        - error
        - slowquery
      DeletionProtection: true
      Tags:
        - Key: Environment
          Value: Production

Outputs:
  RDSEndpoint:
    Description: RDS Endpoint
    Value: !GetAtt RDSInstance.Endpoint.Address
    Export:
      Name: !Sub ${AWS::StackName}-RDSEndpoint

  RDSPort:
    Description: RDS Port
    Value: !GetAtt RDSInstance.Endpoint.Port
    Export:
      Name: !Sub ${AWS::StackName}-RDSPort
```

### Method 4: Terraform

```hcl
# Provider configuration
provider "aws" {
  region = "us-east-1"
}

# Variables
variable "db_password" {
  type        = string
  sensitive   = true
  description = "Master password for RDS"
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "Main DB Subnet Group"
  }
}

# Security Group
resource "aws_security_group" "rds" {
  name        = "rds-mysql-sg"
  description = "Security group for RDS MySQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "RDS MySQL SG"
  }
}

# Parameter Group
resource "aws_db_parameter_group" "mysql8" {
  name   = "mysql8-custom"
  family = "mysql8.0"

  parameter {
    name  = "max_connections"
    value = "200"
  }

  parameter {
    name  = "slow_query_log"
    value = "1"
  }

  parameter {
    name  = "long_query_time"
    value = "2"
  }

  tags = {
    Name = "MySQL 8.0 Custom Parameters"
  }
}

# RDS Instance
resource "aws_db_instance" "mysql" {
  identifier     = "myapp-mysql-production"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.medium"

  # Storage
  allocated_storage     = 100
  max_allocated_storage = 500  # Enable storage autoscaling
  storage_type          = "gp3"
  iops                  = 3000
  storage_throughput    = 125
  storage_encrypted     = true

  # Credentials
  db_name  = "myappdb"
  username = "admin"
  password = var.db_password

  # Network
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = true

  # Configuration
  parameter_group_name = aws_db_parameter_group.mysql8.name

  # Backup
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"
  copy_tags_to_snapshot   = true
  skip_final_snapshot     = false
  final_snapshot_identifier = "myapp-mysql-final-snapshot"

  # Monitoring
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  enabled_cloudwatch_logs_exports       = ["error", "slowquery"]

  # Protection
  deletion_protection = true

  tags = {
    Name        = "MyApp MySQL Production"
    Environment = "Production"
  }
}

# Outputs
output "rds_endpoint" {
  value = aws_db_instance.mysql.endpoint
}

output "rds_port" {
  value = aws_db_instance.mysql.port
}
```

## DB Parameter Groups

Parameter groups contain engine-specific configuration settings.

### Common MySQL Parameters

```sql
-- Connection settings
max_connections = 150
wait_timeout = 28800
interactive_timeout = 28800
connect_timeout = 10

-- InnoDB settings
innodb_buffer_pool_size = {DBInstanceClassMemory*3/4}
innodb_log_file_size = 134217728
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50

-- Query cache (deprecated in MySQL 8.0)
query_cache_type = 0

-- Logging
slow_query_log = 1
long_query_time = 2
log_queries_not_using_indexes = 0
general_log = 0

-- Character set
character_set_server = utf8mb4
collation_server = utf8mb4_unicode_ci
```

### Common PostgreSQL Parameters

```sql
-- Connection settings
max_connections = 100
idle_in_transaction_session_timeout = 60000

-- Memory settings
shared_buffers = {DBInstanceClassMemory/4096}MB
effective_cache_size = {DBInstanceClassMemory*3/4096}MB
work_mem = 256MB
maintenance_work_mem = 512MB

-- WAL settings
wal_buffers = 64MB
max_wal_size = 2GB
min_wal_size = 1GB

-- Query planning
random_page_cost = 1.1
effective_io_concurrency = 200

-- Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

### Creating a Parameter Group (CLI)

```bash
# Create parameter group
aws rds create-db-parameter-group \
    --db-parameter-group-name my-mysql8-params \
    --db-parameter-group-family mysql8.0 \
    --description "Custom MySQL 8.0 parameters"

# Modify parameters
aws rds modify-db-parameter-group \
    --db-parameter-group-name my-mysql8-params \
    --parameters \
        "ParameterName=max_connections,ParameterValue=200,ApplyMethod=pending-reboot" \
        "ParameterName=slow_query_log,ParameterValue=1,ApplyMethod=immediate" \
        "ParameterName=long_query_time,ParameterValue=2,ApplyMethod=immediate"
```

## DB Option Groups

Option groups enable additional engine features.

### MySQL Options

| Option | Description |
|--------|-------------|
| MARIADB_AUDIT_PLUGIN | Audit logging |
| MEMCACHED | In-memory caching |

### SQL Server Options

| Option | Description |
|--------|-------------|
| SQLSERVER_BACKUP_RESTORE | Native backup to S3 |
| TRANSPARENT_DATA_ENCRYPTION | TDE encryption |
| SQLSERVER_AUDIT | SQL Server Audit |

### Oracle Options

| Option | Description |
|--------|-------------|
| APEX | Application Express |
| OEM | Oracle Enterprise Manager |
| S3_INTEGRATION | S3 access from Oracle |
| NATIVE_NETWORK_ENCRYPTION | Network encryption |

## Storage Auto Scaling

Enable automatic storage scaling to handle growth:

```bash
# Enable storage autoscaling (CLI)
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --max-allocated-storage 1000  # Max 1 TB

# Terraform
resource "aws_db_instance" "mysql" {
  # ...
  allocated_storage     = 100      # Initial size
  max_allocated_storage = 1000     # Max size (enables autoscaling)
}
```

**Auto Scaling Triggers:**
- Free storage < 10% of allocated storage
- Low storage condition persists for 5+ minutes
- 6+ hours since last scaling operation

## Modifying RDS Instances

### Immediate vs Scheduled Modifications

| Modification Type | Apply Immediately | During Maintenance Window |
|-------------------|-------------------|---------------------------|
| Instance class change | Downtime | Downtime |
| Storage increase | No downtime | No downtime |
| Storage type change | Possible downtime | Possible downtime |
| Engine version upgrade | Downtime | Downtime |
| Multi-AZ change | No downtime | No downtime |
| Parameter group | May require reboot | May require reboot |

### Modify Instance Example

```bash
# Scale up instance class
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --db-instance-class db.r6g.xlarge \
    --apply-immediately

# Increase storage
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --allocated-storage 500 \
    --apply-immediately

# Change storage type
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --storage-type io1 \
    --iops 10000 \
    --apply-immediately
```

## Summary

- Choose instance class based on workload: burstable for dev/test, standard for general, memory-optimized for heavy workloads
- gp3 offers better value than gp2 with independent IOPS/throughput provisioning
- Use io1/io2 for high-performance, consistent low-latency requirements
- Parameter groups customize engine behavior
- Option groups enable additional engine features
- Enable storage autoscaling to handle growth automatically

---

**Next:** [03 - RDS High Availability](./03-rds-high-availability.md)

**Previous:** [01 - RDS Fundamentals](./01-rds-fundamentals.md)
