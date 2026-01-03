# 10 - Database Migration with AWS DMS

## Overview

AWS Database Migration Service (DMS) helps you migrate databases to AWS quickly and securely. The source database remains fully operational during the migration, minimizing downtime for applications.

```
+--------------------------------------------------------------------------------+
|                         DATABASE MIGRATION SERVICE                              |
|                                                                                 |
|  +------------------------+        +------------------+        +--------------+|
|  |   SOURCE DATABASE      |        |   REPLICATION    |        |   TARGET     ||
|  |                        |  --->  |   INSTANCE       |  --->  |   DATABASE   ||
|  |  - On-premises         |        |                  |        |              ||
|  |  - EC2                 |        |  - Full Load     |        |  - RDS       ||
|  |  - RDS                 |        |  - CDC           |        |  - Aurora    ||
|  |  - Other cloud         |        |  - Full + CDC    |        |  - DynamoDB  ||
|  +------------------------+        +------------------+        +--------------+|
|                                                                                 |
|  SUPPORTED SOURCES:                  SUPPORTED TARGETS:                        |
|  +---------------------------+       +---------------------------+             |
|  | - Oracle                  |       | - Amazon RDS              |             |
|  | - SQL Server              |       | - Amazon Aurora           |             |
|  | - MySQL                   |       | - Amazon Redshift         |             |
|  | - PostgreSQL              |       | - Amazon DynamoDB         |             |
|  | - MariaDB                 |       | - Amazon S3               |             |
|  | - MongoDB                 |       | - Amazon OpenSearch       |             |
|  | - SAP ASE                 |       | - Amazon Neptune          |             |
|  | - IBM Db2                 |       | - Amazon DocumentDB       |             |
|  | - Amazon S3               |       | - Apache Kafka            |             |
|  +---------------------------+       +---------------------------+             |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Migration Types

### Homogeneous Migration

Same database engine on source and target (e.g., MySQL to MySQL, Oracle to Oracle).

```
+--------------------------------------------------------------------------------+
|                      HOMOGENEOUS MIGRATION                                      |
|                                                                                 |
|   SOURCE                                                    TARGET             |
|   +----------------+                                    +----------------+      |
|   |   MySQL 5.7    |  ================================> |   MySQL 8.0    |      |
|   |  (On-premises) |         AWS DMS                    |   (RDS)        |      |
|   +----------------+                                    +----------------+      |
|                                                                                 |
|   - Schema automatically compatible                                             |
|   - No schema conversion needed                                                 |
|   - Simpler migration process                                                  |
|   - Version upgrades possible                                                   |
|                                                                                 |
|   EXAMPLES:                                                                     |
|   - MySQL to RDS MySQL                                                         |
|   - PostgreSQL to Aurora PostgreSQL                                            |
|   - Oracle to RDS Oracle                                                       |
|   - SQL Server to RDS SQL Server                                               |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Heterogeneous Migration

Different database engines on source and target (e.g., Oracle to PostgreSQL).

```
+--------------------------------------------------------------------------------+
|                     HETEROGENEOUS MIGRATION                                     |
|                                                                                 |
|   SOURCE                        SCT                         TARGET             |
|   +-------------+           +--------+                  +----------------+      |
|   |   Oracle    | --SCHEMA->|  AWS   |--CONVERTED----->| PostgreSQL     |      |
|   | (On-prem)   |           |  SCT   |   SCHEMA        | (Aurora)       |      |
|   +-------------+           +--------+                  +----------------+      |
|         |                                                      ^                |
|         |                   +--------+                         |                |
|         +-------DATA------->|  AWS   |--------DATA------------+                |
|                             |  DMS   |                                          |
|                             +--------+                                          |
|                                                                                 |
|   REQUIRES:                                                                     |
|   1. AWS Schema Conversion Tool (SCT) - converts schema                        |
|   2. AWS DMS - migrates data                                                   |
|   3. Manual adjustments for incompatible code                                  |
|                                                                                 |
|   EXAMPLES:                                                                     |
|   - Oracle to Aurora PostgreSQL                                                |
|   - SQL Server to MySQL                                                        |
|   - Oracle to DynamoDB                                                         |
|   - MongoDB to DocumentDB                                                      |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## AWS Schema Conversion Tool (SCT)

### SCT Overview

```
+--------------------------------------------------------------------------------+
|                    SCHEMA CONVERSION TOOL (SCT)                                 |
|                                                                                 |
|   +------------------------------------------------------------------+         |
|   |                      SCT WORKFLOW                                 |         |
|   |                                                                   |         |
|   |  1. CONNECT TO SOURCE                                            |         |
|   |     Connect to source database, analyze schema                   |         |
|   |                        |                                          |         |
|   |                        v                                          |         |
|   |  2. ASSESSMENT REPORT                                            |         |
|   |     Generate migration assessment                                 |         |
|   |     - Conversion complexity                                       |         |
|   |     - Manual conversion items                                     |         |
|   |     - Action items                                                |         |
|   |                        |                                          |         |
|   |                        v                                          |         |
|   |  3. CONVERT SCHEMA                                               |         |
|   |     - Tables, views, indexes                                      |         |
|   |     - Stored procedures, functions                                |         |
|   |     - Triggers, constraints                                       |         |
|   |                        |                                          |         |
|   |                        v                                          |         |
|   |  4. APPLY TO TARGET                                              |         |
|   |     Apply converted DDL to target database                        |         |
|   |                                                                   |         |
|   +------------------------------------------------------------------+         |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### SCT Assessment Report

```
+--------------------------------------------------------------------------------+
|                     ASSESSMENT REPORT EXAMPLE                                   |
|                                                                                 |
|   Source: Oracle 19c                                                           |
|   Target: Amazon Aurora PostgreSQL 15                                          |
|                                                                                 |
|   SUMMARY:                                                                      |
|   +----------------------------------+                                          |
|   | Object Type    | Total | Issues |                                          |
|   +----------------------------------+                                          |
|   | Tables         |   150 |      5 |                                          |
|   | Views          |    45 |      8 |                                          |
|   | Indexes        |   200 |      0 |                                          |
|   | Procedures     |    80 |     25 |                                          |
|   | Functions      |    35 |     12 |                                          |
|   | Triggers       |    20 |      6 |                                          |
|   | Packages       |    15 |     15 |  <-- All packages need manual work      |
|   +----------------------------------+                                          |
|                                                                                 |
|   CONVERSION COMPLEXITY:                                                        |
|   +------------------------------------------+                                  |
|   | Complexity       | Count | Effort       |                                  |
|   +------------------------------------------+                                  |
|   | Simple (Auto)    |   450 | 0 hours      |                                  |
|   | Medium           |    35 | 40 hours     |                                  |
|   | Complex          |    20 | 80 hours     |                                  |
|   | Very Complex     |    10 | 100+ hours   |                                  |
|   +------------------------------------------+                                  |
|                                                                                 |
|   ESTIMATED EFFORT: ~220 developer hours                                       |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Common Schema Conversion Challenges

| Source | Target | Common Issues |
|--------|--------|---------------|
| Oracle | PostgreSQL | PL/SQL to PL/pgSQL, Sequences, DECODE to CASE |
| Oracle | MySQL | Packages (not supported), Autonomous transactions |
| SQL Server | PostgreSQL | T-SQL to PL/pgSQL, IDENTITY to SERIAL |
| SQL Server | MySQL | CTEs, Window functions (older MySQL versions) |
| Oracle | DynamoDB | Relational to NoSQL model redesign |

## AWS DMS Components

### Replication Instance

```
+--------------------------------------------------------------------------------+
|                      REPLICATION INSTANCE                                       |
|                                                                                 |
|   +------------------------------------------------------------------+         |
|   |                                                                   |         |
|   |   REPLICATION INSTANCE                                           |         |
|   |   +------------------+     +------------------+                  |         |
|   |   |   Source         |     |   Target         |                  |         |
|   |   |   Connection     |     |   Connection     |                  |         |
|   |   +--------+---------+     +--------+---------+                  |         |
|   |            |                        |                            |         |
|   |            v                        v                            |         |
|   |   +----------------------------------------+                     |         |
|   |   |         REPLICATION TASKS              |                     |         |
|   |   |                                        |                     |         |
|   |   |  Task 1: Full Load + CDC (Schema A)   |                     |         |
|   |   |  Task 2: CDC Only (Schema B)          |                     |         |
|   |   |  Task 3: Full Load (Schema C)         |                     |         |
|   |   +----------------------------------------+                     |         |
|   |                                                                   |         |
|   +------------------------------------------------------------------+         |
|                                                                                 |
|   SIZING CONSIDERATIONS:                                                        |
|   +------------------------------------------------------------------+         |
|   | Data Volume          | Recommended Instance      | Multi-AZ     |         |
|   +------------------------------------------------------------------+         |
|   | < 20 GB              | dms.t3.medium             | Optional     |         |
|   | 20 - 100 GB          | dms.r5.large              | Recommended  |         |
|   | 100 GB - 1 TB        | dms.r5.xlarge             | Recommended  |         |
|   | > 1 TB               | dms.r5.2xlarge or larger  | Required     |         |
|   +------------------------------------------------------------------+         |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Endpoints

```bash
# Create source endpoint (Oracle on-premises)
aws dms create-endpoint \
    --endpoint-identifier oracle-source \
    --endpoint-type source \
    --engine-name oracle \
    --username admin \
    --password 'SecurePassword123!' \
    --server-name oracle.example.com \
    --port 1521 \
    --database-name ORCL \
    --extra-connection-attributes "useLogminerReader=N;useBfile=Y"

# Create target endpoint (Aurora PostgreSQL)
aws dms create-endpoint \
    --endpoint-identifier aurora-target \
    --endpoint-type target \
    --engine-name aurora-postgresql \
    --username postgres \
    --password 'SecurePassword123!' \
    --server-name myaurora.cluster-abc123.us-east-1.rds.amazonaws.com \
    --port 5432 \
    --database-name myapp

# Test endpoint connections
aws dms test-connection \
    --replication-instance-arn arn:aws:dms:us-east-1:123456789012:rep:EXAMPLE \
    --endpoint-arn arn:aws:dms:us-east-1:123456789012:endpoint:EXAMPLE
```

### Replication Tasks

```
+--------------------------------------------------------------------------------+
|                      REPLICATION TASK TYPES                                     |
|                                                                                 |
|   1. FULL LOAD ONLY                                                            |
|      +--------+     +--------+     +--------+                                  |
|      | Source | --> |  DMS   | --> | Target |                                  |
|      | Tables |     | (Copy) |     | Tables |                                  |
|      +--------+     +--------+     +--------+                                  |
|      - One-time migration                                                       |
|      - Source must be quiesced or accept some inconsistency                    |
|      - Fastest for static data                                                  |
|                                                                                 |
|   2. CDC ONLY (Change Data Capture)                                            |
|      +--------+     +--------+     +--------+                                  |
|      | Source | --> |  DMS   | --> | Target |                                  |
|      | Changes|     | (CDC)  |     | Applied|                                  |
|      +--------+     +--------+     +--------+                                  |
|      - Ongoing replication                                                      |
|      - Assumes initial load done separately                                     |
|      - Near real-time synchronization                                           |
|                                                                                 |
|   3. FULL LOAD + CDC (Recommended)                                             |
|      +--------+     +--------+     +--------+                                  |
|      | Source | --> |  DMS   | --> | Target |                                  |
|      |Full+CDC|     |(Both)  |     | Sync'd |                                  |
|      +--------+     +--------+     +--------+                                  |
|      - Full load first, then CDC for ongoing changes                           |
|      - Minimal downtime migration                                               |
|      - Most common choice for production migrations                             |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Migration Strategies

### Big Bang Migration

```
+--------------------------------------------------------------------------------+
|                      BIG BANG MIGRATION                                         |
|                                                                                 |
|   Timeline:                                                                     |
|   +------------------------------------------------------------+               |
|   |          |                    |                   |        |               |
|   | Prepare  |   Full Migration   |    Validation     | Switch |               |
|   |          |     (Downtime)     |                   |        |               |
|   +------------------------------------------------------------+               |
|                                                                                 |
|   CHARACTERISTICS:                                                              |
|   - Single migration event                                                      |
|   - Longer downtime window required                                            |
|   - Simpler to plan and execute                                                |
|   - All-or-nothing approach                                                    |
|   - Best for: Smaller databases, scheduled maintenance windows                 |
|                                                                                 |
|   PROCESS:                                                                      |
|   1. Stop application                                                           |
|   2. Perform full data migration                                               |
|   3. Validate data                                                              |
|   4. Update connection strings                                                  |
|   5. Start application                                                          |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Phased Migration with CDC

```
+--------------------------------------------------------------------------------+
|                   PHASED MIGRATION WITH CDC                                     |
|                                                                                 |
|   Timeline:                                                                     |
|   +------------------------------------------------------------+               |
|   |                                                    |  Brief |               |
|   |  Full Load  |    CDC Replication    |  Validation  | Switch |               |
|   |   (Hours)   |       (Days/Weeks)    |              |  (<5m) |               |
|   +------------------------------------------------------------+               |
|           ^            Source Active              ^                            |
|           |                                       |                            |
|           |                                       |                            |
|       Start DMS                              Stop CDC,                         |
|                                              cutover                           |
|                                                                                 |
|   PROCESS:                                                                      |
|   1. Start full load (source remains active)                                   |
|   2. CDC captures changes during full load                                     |
|   3. Apply cached changes after full load                                      |
|   4. Continue CDC replication (source active)                                  |
|   5. Validate data consistency                                                 |
|   6. Brief cutover window                                                       |
|     - Stop applications                                                         |
|     - Wait for CDC to catch up                                                 |
|     - Switch connection strings                                                |
|     - Start applications                                                        |
|                                                                                 |
|   DOWNTIME: Minimal (minutes)                                                  |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Parallel/Blue-Green Migration

```
+--------------------------------------------------------------------------------+
|                   BLUE-GREEN MIGRATION                                          |
|                                                                                 |
|   +------------------------------------------------------------------+         |
|   |  BLUE (Current Production)        GREEN (New)                    |         |
|   |                                                                   |         |
|   |  +-----------------+              +-----------------+            |         |
|   |  |   Application   |              |   Application   |            |         |
|   |  |   (Blue)        |              |   (Green)       |            |         |
|   |  +--------+--------+              +--------+--------+            |         |
|   |           |                                |                     |         |
|   |           v                                v                     |         |
|   |  +--------+--------+              +--------+--------+            |         |
|   |  |   Source DB     |  -----CDC--> |   Target DB     |            |         |
|   |  |   (Oracle)      |              |   (Aurora PG)   |            |         |
|   |  +-----------------+              +-----------------+            |         |
|   |                                                                   |         |
|   +------------------------------------------------------------------+         |
|                                                                                 |
|   STAGES:                                                                       |
|   1. Set up target (Green) environment                                         |
|   2. DMS full load + CDC replication                                           |
|   3. Test Green with synthetic traffic                                         |
|   4. Gradually shift traffic (canary, 10%, 50%, 100%)                         |
|   5. Monitor for issues                                                         |
|   6. Rollback capability until cutover complete                                |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Hands-On: DMS Migration

### Step 1: Set Up Replication Instance

```bash
# Create replication subnet group
aws dms create-replication-subnet-group \
    --replication-subnet-group-identifier my-dms-subnet \
    --replication-subnet-group-description "DMS subnet group" \
    --subnet-ids subnet-abc123 subnet-def456

# Create replication instance
aws dms create-replication-instance \
    --replication-instance-identifier my-dms-instance \
    --replication-instance-class dms.r5.large \
    --allocated-storage 100 \
    --vpc-security-group-ids sg-12345678 \
    --replication-subnet-group-identifier my-dms-subnet \
    --multi-az \
    --engine-version 3.5.1 \
    --publicly-accessible false

# Wait for instance to be available
aws dms wait replication-instance-available \
    --filters Name=replication-instance-id,Values=my-dms-instance
```

### Step 2: Create Endpoints

```bash
# Source endpoint (MySQL on EC2)
aws dms create-endpoint \
    --endpoint-identifier mysql-source \
    --endpoint-type source \
    --engine-name mysql \
    --username admin \
    --password 'SourcePassword123!' \
    --server-name 10.0.1.50 \
    --port 3306 \
    --database-name myapp

# Target endpoint (RDS MySQL)
aws dms create-endpoint \
    --endpoint-identifier rds-target \
    --endpoint-type target \
    --engine-name mysql \
    --username admin \
    --password 'TargetPassword123!' \
    --server-name mydb.abc123.us-east-1.rds.amazonaws.com \
    --port 3306 \
    --database-name myapp

# Test connections
REPL_ARN=$(aws dms describe-replication-instances \
    --filters Name=replication-instance-id,Values=my-dms-instance \
    --query 'ReplicationInstances[0].ReplicationInstanceArn' \
    --output text)

SOURCE_ARN=$(aws dms describe-endpoints \
    --filters Name=endpoint-id,Values=mysql-source \
    --query 'Endpoints[0].EndpointArn' \
    --output text)

TARGET_ARN=$(aws dms describe-endpoints \
    --filters Name=endpoint-id,Values=rds-target \
    --query 'Endpoints[0].EndpointArn' \
    --output text)

aws dms test-connection \
    --replication-instance-arn $REPL_ARN \
    --endpoint-arn $SOURCE_ARN

aws dms test-connection \
    --replication-instance-arn $REPL_ARN \
    --endpoint-arn $TARGET_ARN
```

### Step 3: Create Table Mappings

```json
{
    "rules": [
        {
            "rule-type": "selection",
            "rule-id": "1",
            "rule-name": "include-all-tables",
            "object-locator": {
                "schema-name": "myapp",
                "table-name": "%"
            },
            "rule-action": "include"
        },
        {
            "rule-type": "selection",
            "rule-id": "2",
            "rule-name": "exclude-logs",
            "object-locator": {
                "schema-name": "myapp",
                "table-name": "audit_logs"
            },
            "rule-action": "exclude"
        },
        {
            "rule-type": "transformation",
            "rule-id": "3",
            "rule-name": "rename-schema",
            "rule-target": "schema",
            "object-locator": {
                "schema-name": "myapp"
            },
            "rule-action": "rename",
            "value": "production"
        },
        {
            "rule-type": "transformation",
            "rule-id": "4",
            "rule-name": "convert-to-lowercase",
            "rule-target": "table",
            "object-locator": {
                "schema-name": "%",
                "table-name": "%"
            },
            "rule-action": "convert-lowercase"
        }
    ]
}
```

### Step 4: Create and Start Replication Task

```bash
# Create task with table mappings
aws dms create-replication-task \
    --replication-task-identifier my-migration-task \
    --source-endpoint-arn $SOURCE_ARN \
    --target-endpoint-arn $TARGET_ARN \
    --replication-instance-arn $REPL_ARN \
    --migration-type full-load-and-cdc \
    --table-mappings file://table-mappings.json \
    --replication-task-settings '{
        "TargetMetadata": {
            "SupportLobs": true,
            "FullLobMode": false,
            "LobChunkSize": 64,
            "LimitedSizeLobMode": true,
            "LobMaxSize": 32
        },
        "FullLoadSettings": {
            "TargetTablePrepMode": "DROP_AND_CREATE",
            "CreatePkAfterFullLoad": false,
            "StopTaskCachedChangesApplied": false,
            "StopTaskCachedChangesNotApplied": false
        },
        "Logging": {
            "EnableLogging": true,
            "LogComponents": [
                {"Id": "SOURCE_UNLOAD", "Severity": "LOGGER_SEVERITY_DEFAULT"},
                {"Id": "TARGET_LOAD", "Severity": "LOGGER_SEVERITY_DEFAULT"},
                {"Id": "SOURCE_CAPTURE", "Severity": "LOGGER_SEVERITY_DEFAULT"},
                {"Id": "TARGET_APPLY", "Severity": "LOGGER_SEVERITY_DEFAULT"}
            ]
        }
    }'

# Start the task
aws dms start-replication-task \
    --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:EXAMPLE \
    --start-replication-task-type start-replication
```

### Step 5: Monitor Migration

```bash
# Check task status
aws dms describe-replication-tasks \
    --filters Name=replication-task-id,Values=my-migration-task \
    --query 'ReplicationTasks[0].{Status:Status,Progress:ReplicationTaskStats}'

# Get table statistics
aws dms describe-table-statistics \
    --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:EXAMPLE \
    --query 'TableStatistics[*].{Table:TableName,Inserts:Inserts,Updates:Updates,Deletes:Deletes,FullLoadRows:FullLoadRows}'

# View CloudWatch logs
aws logs get-log-events \
    --log-group-name dms-tasks-my-migration-task \
    --log-stream-name dms-task-EXAMPLE
```

## Validation and Cutover

### Data Validation

```bash
# Create validation task
aws dms create-replication-task \
    --replication-task-identifier validation-task \
    --migration-type full-load \
    --replication-task-settings '{
        "ValidationSettings": {
            "EnableValidation": true,
            "ValidationMode": "ROW_LEVEL",
            "ThreadCount": 5,
            "TableFailureMaxCount": 10000,
            "ValidationOnly": true
        }
    }' \
    # ... other parameters

# Check validation results
aws dms describe-table-statistics \
    --replication-task-arn arn:aws:dms:us-east-1:123456789012:task:validation-task \
    --query 'TableStatistics[?ValidationState!=`Validated`]'
```

### Cutover Checklist

```
+--------------------------------------------------------------------------------+
|                      MIGRATION CUTOVER CHECKLIST                                |
|                                                                                 |
|  PRE-CUTOVER:                                                                   |
|  [ ] Full load completed successfully                                          |
|  [ ] CDC caught up (minimal replication lag)                                   |
|  [ ] Data validation passed                                                    |
|  [ ] Application tested against target                                          |
|  [ ] Rollback plan documented                                                  |
|  [ ] Stakeholders notified                                                      |
|  [ ] Maintenance window scheduled                                               |
|                                                                                 |
|  CUTOVER STEPS:                                                                 |
|  [ ] 1. Announce maintenance window                                             |
|  [ ] 2. Stop all application writes to source                                  |
|  [ ] 3. Wait for CDC to apply all pending changes                              |
|  [ ] 4. Verify replication lag = 0                                             |
|  [ ] 5. Stop DMS replication task                                              |
|  [ ] 6. Final data validation                                                  |
|  [ ] 7. Update application connection strings                                   |
|  [ ] 8. Start applications pointing to target                                  |
|  [ ] 9. Smoke test critical functionality                                       |
|  [ ] 10. Monitor for errors                                                     |
|                                                                                 |
|  POST-CUTOVER:                                                                  |
|  [ ] Monitor application performance                                            |
|  [ ] Keep source database read-only (rollback option)                          |
|  [ ] Document lessons learned                                                   |
|  [ ] Clean up DMS resources after confidence period                            |
|  [ ] Decommission source database (after retention period)                     |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Common Migration Scenarios

### Scenario 1: Oracle to Aurora PostgreSQL

```
+--------------------------------------------------------------------------------+
|              ORACLE TO AURORA POSTGRESQL MIGRATION                              |
|                                                                                 |
|   TOOLS NEEDED:                                                                 |
|   - AWS Schema Conversion Tool (SCT)                                           |
|   - AWS Database Migration Service (DMS)                                        |
|                                                                                 |
|   PROCESS:                                                                      |
|   1. Install SCT on local machine                                              |
|   2. Connect SCT to Oracle source                                              |
|   3. Generate assessment report                                                 |
|   4. Review and plan for manual conversions                                     |
|   5. Convert schema using SCT                                                   |
|   6. Apply converted schema to Aurora                                           |
|   7. Create DMS replication instance                                           |
|   8. Create source and target endpoints                                        |
|   9. Create and run migration task (full load + CDC)                           |
|  10. Validate data                                                              |
|  11. Cutover                                                                    |
|                                                                                 |
|   COMMON CHALLENGES:                                                            |
|   - PL/SQL to PL/pgSQL conversion                                              |
|   - Oracle packages (not supported in PostgreSQL)                              |
|   - Sequences and identity columns                                             |
|   - Data type differences (VARCHAR2 vs VARCHAR)                                |
|   - Oracle-specific functions                                                   |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

### Scenario 2: Self-Managed MySQL to RDS

```bash
# Simple homogeneous migration - no SCT needed

# 1. Create RDS MySQL instance
aws rds create-db-instance \
    --db-instance-identifier mysql-target \
    --db-instance-class db.r5.large \
    --engine mysql \
    --engine-version 8.0 \
    --master-username admin \
    --master-user-password 'SecurePass123!' \
    --allocated-storage 100 \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name my-db-subnet

# 2. Export schema from source (optional - DMS can create tables)
mysqldump -h source-mysql.example.com -u admin -p \
    --no-data --routines --triggers mydb > schema.sql

# 3. Import schema to target
mysql -h mysql-target.abc123.us-east-1.rds.amazonaws.com \
    -u admin -p mydb < schema.sql

# 4. Create DMS task (full-load-and-cdc)
# ... (as shown in hands-on section above)
```

### Scenario 3: On-Premises SQL Server to Aurora PostgreSQL

```
+--------------------------------------------------------------------------------+
|          SQL SERVER TO AURORA POSTGRESQL MIGRATION                             |
|                                                                                 |
|   ARCHITECTURE:                                                                 |
|                                                                                 |
|   On-Premises                 AWS VPC                                          |
|   +-----------+             +---------------------------------+                |
|   |           |   VPN/DX    |                                 |                |
|   | SQL Server| ==========> |  DMS    -->    Aurora PostgreSQL|                |
|   |           |             |  Instance                       |                |
|   +-----------+             +---------------------------------+                |
|                                                                                 |
|   SCT CONVERSION NOTES:                                                         |
|   +------------------------------------------------------------------+         |
|   | T-SQL Feature           | PostgreSQL Equivalent                  |         |
|   +------------------------------------------------------------------+         |
|   | IDENTITY                | SERIAL / GENERATED AS IDENTITY         |         |
|   | TOP N                   | LIMIT N                                 |         |
|   | ISNULL()                | COALESCE()                              |         |
|   | GETDATE()               | CURRENT_TIMESTAMP                       |         |
|   | VARCHAR(MAX)            | TEXT                                    |         |
|   | BIT                     | BOOLEAN                                 |         |
|   | NVARCHAR                | VARCHAR                                 |         |
|   | Stored Procedures       | PL/pgSQL functions                      |         |
|   +------------------------------------------------------------------+         |
|                                                                                 |
+--------------------------------------------------------------------------------+
```

## Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Endpoint connection failed | Network/firewall | Check security groups, VPN, NACLs |
| LOB truncation | LobMaxSize too small | Increase LobMaxSize or use FullLobMode |
| Table not found | Case sensitivity | Check schema/table name case |
| CDC not working | Binary logging disabled | Enable binary logging on source |
| Slow migration | Undersized replication instance | Scale up replication instance |
| Validation failures | Data type mismatch | Review SCT conversion report |

### Monitoring Best Practices

```bash
# CloudWatch metrics to monitor
aws cloudwatch get-metric-statistics \
    --namespace AWS/DMS \
    --metric-name CDCLatencySource \
    --dimensions Name=ReplicationInstanceIdentifier,Value=my-dms-instance \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 300 \
    --statistics Average

# Key metrics:
# - CDCLatencySource: Time between when change is made and captured
# - CDCLatencyTarget: Time between capture and apply
# - FullLoadThroughputRowsSource: Rows read per second
# - FullLoadThroughputRowsTarget: Rows written per second
# - MemoryUsage: Memory used by replication instance
```

## Best Practices Summary

### Pre-Migration

1. **Assessment First**: Always run SCT assessment before planning
2. **Size Appropriately**: Choose replication instance size based on data volume
3. **Test Thoroughly**: Run full migration in test environment first
4. **Document Everything**: Connection strings, table mappings, custom code

### During Migration

1. **Monitor Continuously**: Watch CloudWatch metrics and task status
2. **Log Everything**: Enable detailed logging for troubleshooting
3. **Validate Incrementally**: Check data consistency throughout
4. **Have Rollback Plan**: Keep source database accessible

### Post-Migration

1. **Validate Data**: Run comprehensive data validation
2. **Test Application**: Full functional testing against new database
3. **Monitor Performance**: Compare performance metrics
4. **Clean Up**: Remove DMS resources after successful migration

---

**Next:** [11 - Hands-on Lab](./11-hands-on-lab.md)

**Previous:** [09 - ElastiCache](./09-elasticache.md)
