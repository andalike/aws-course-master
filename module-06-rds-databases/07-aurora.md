# 07 - Amazon Aurora

## What is Aurora?

Amazon Aurora is a MySQL and PostgreSQL-compatible relational database built for the cloud. It combines the performance and availability of commercial databases with the simplicity and cost-effectiveness of open-source databases.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           AURORA KEY BENEFITS                                   │
│                                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐    │
│  │    PERFORMANCE      │  │    AVAILABILITY     │  │      COST           │    │
│  │                     │  │                     │  │                     │    │
│  │  5x MySQL           │  │  99.99% SLA         │  │  1/10th cost of     │    │
│  │  3x PostgreSQL      │  │  6-way replication  │  │  commercial DBs     │    │
│  │                     │  │  < 30s failover     │  │                     │    │
│  │  Up to 128 TB       │  │  15 read replicas   │  │  Pay per use        │    │
│  │  storage            │  │  Global Database    │  │  (Serverless)       │    │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘    │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Aurora Architecture

### Storage Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          AURORA STORAGE LAYER                                   │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                    SHARED DISTRIBUTED STORAGE                              │ │
│  │                                                                            │ │
│  │   ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │   │                  PROTECTION GROUPS (10 GB each)                      │ │ │
│  │   │                                                                      │ │ │
│  │   │  Each protection group has 6 copies across 3 AZs                    │ │ │
│  │   │                                                                      │ │ │
│  │   │   AZ-A          AZ-B          AZ-C                                  │ │ │
│  │   │  ┌─────┐       ┌─────┐       ┌─────┐                                │ │ │
│  │   │  │Copy1│       │Copy3│       │Copy5│                                │ │ │
│  │   │  └─────┘       └─────┘       └─────┘                                │ │ │
│  │   │  ┌─────┐       ┌─────┐       ┌─────┐                                │ │ │
│  │   │  │Copy2│       │Copy4│       │Copy6│                                │ │ │
│  │   │  └─────┘       └─────┘       └─────┘                                │ │ │
│  │   │                                                                      │ │ │
│  │   │  Writes: Need 4 of 6 copies (quorum)                                │ │ │
│  │   │  Reads:  Need 3 of 6 copies (quorum)                                │ │ │
│  │   │                                                                      │ │ │
│  │   └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                            │ │
│  │   SELF-HEALING STORAGE                                                    │ │
│  │   ├── Automatic detection of failures                                     │ │
│  │   ├── Automatic repair of corrupt data                                   │ │
│  │   ├── Continuous background scanning                                      │ │
│  │   └── No impact on database operations during repair                     │ │
│  │                                                                            │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  STORAGE FEATURES:                                                             │
│  ├── Auto-scales from 10 GB to 128 TB                                         │
│  ├── No need to provision storage in advance                                  │
│  ├── Only pay for storage used                                                │
│  ├── Storage independent of compute                                           │
│  └── Instantaneous crash recovery                                             │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Cluster Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           AURORA CLUSTER                                        │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                         COMPUTE LAYER                                      │ │
│  │                                                                            │ │
│  │     ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │     │                   WRITER ENDPOINT                                │   │ │
│  │     │              (Connects to Primary Instance)                      │   │ │
│  │     └─────────────────────────┬───────────────────────────────────────┘   │ │
│  │                               │                                            │ │
│  │                               ▼                                            │ │
│  │     ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │     │              PRIMARY INSTANCE (Writer)                           │   │ │
│  │     │                    db.r6g.xlarge                                 │   │ │
│  │     │                                                                  │   │ │
│  │     │  - Only instance that can write                                 │   │ │
│  │     │  - Also handles reads                                           │   │ │
│  │     └─────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                            │ │
│  │     ┌─────────────────────────────────────────────────────────────────┐   │ │
│  │     │                   READER ENDPOINT                                │   │ │
│  │     │           (Load-balanced across replicas)                        │   │ │
│  │     └───────────────────────────┬─────────────────────────────────────┘   │ │
│  │                 ┌───────────────┼───────────────┐                         │ │
│  │                 │               │               │                         │ │
│  │                 ▼               ▼               ▼                         │ │
│  │     ┌───────────────┐  ┌───────────────┐  ┌───────────────┐              │ │
│  │     │   REPLICA 1   │  │   REPLICA 2   │  │   REPLICA 3   │              │ │
│  │     │ db.r6g.large  │  │ db.r6g.large  │  │ db.r6g.xlarge │              │ │
│  │     │               │  │               │  │               │              │ │
│  │     │ - Read-only   │  │ - Read-only   │  │ - Read-only   │              │ │
│  │     │ - Failover    │  │ - Failover    │  │ - Failover    │              │ │
│  │     │   target      │  │   target      │  │   target      │              │ │
│  │     └───────────────┘  └───────────────┘  └───────────────┘              │ │
│  │                                                                            │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                               │   │   │                                        │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                         STORAGE LAYER                                      │ │
│  │         (Shared across all instances - 6-way replication)                 │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Aurora vs RDS Comparison

| Feature | Aurora | RDS MySQL/PostgreSQL |
|---------|--------|----------------------|
| **Performance** | 5x MySQL, 3x PostgreSQL | Baseline |
| **Max Storage** | 128 TB | 64 TB |
| **Storage Scaling** | Automatic | Manual |
| **Replication** | 6 copies, 3 AZs | 2 copies (Multi-AZ) |
| **Read Replicas** | 15 | 5 |
| **Failover Time** | < 30 seconds | 60-120 seconds |
| **Replica Lag** | < 100ms typically | Seconds to minutes |
| **Backtrack** | Yes | No |
| **Serverless Option** | Yes (v2) | No |
| **Global Database** | Yes | No (cross-region replica) |
| **Parallel Query** | Yes | No |

## Aurora Endpoints

### Endpoint Types

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           AURORA ENDPOINTS                                      │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  CLUSTER ENDPOINT (Writer)                                              │   │
│  │                                                                          │   │
│  │  mydb-cluster.cluster-abc123.us-east-1.rds.amazonaws.com                │   │
│  │                                                                          │   │
│  │  - Always points to the current primary instance                        │   │
│  │  - Use for write operations and consistent reads                        │   │
│  │  - Automatically updates during failover                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  READER ENDPOINT                                                         │   │
│  │                                                                          │   │
│  │  mydb-cluster.cluster-ro-abc123.us-east-1.rds.amazonaws.com             │   │
│  │                                                                          │   │
│  │  - Load balances across all read replicas                               │   │
│  │  - Connection-level load balancing (not query-level)                    │   │
│  │  - Falls back to writer if no replicas exist                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  INSTANCE ENDPOINTS                                                      │   │
│  │                                                                          │   │
│  │  mydb-instance-1.abc123.us-east-1.rds.amazonaws.com                     │   │
│  │  mydb-instance-2.abc123.us-east-1.rds.amazonaws.com                     │   │
│  │                                                                          │   │
│  │  - Direct connection to specific instance                               │   │
│  │  - Use for troubleshooting or specific routing                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  CUSTOM ENDPOINTS                                                        │   │
│  │                                                                          │   │
│  │  analytics.cluster-custom-abc123.us-east-1.rds.amazonaws.com            │   │
│  │                                                                          │   │
│  │  - User-defined group of instances                                       │   │
│  │  - Route specific workloads (analytics, reporting)                      │   │
│  │  - Can include any combination of instances                             │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Connection String Examples

```python
# Writer Endpoint (for writes and consistent reads)
writer_config = {
    'host': 'mydb-cluster.cluster-abc123.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'password',
    'database': 'myapp'
}

# Reader Endpoint (for read operations)
reader_config = {
    'host': 'mydb-cluster.cluster-ro-abc123.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'readonly',
    'password': 'password',
    'database': 'myapp'
}

# Custom Endpoint (for analytics)
analytics_config = {
    'host': 'analytics.cluster-custom-abc123.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'analytics_user',
    'password': 'password',
    'database': 'myapp'
}
```

## Aurora Serverless v2

### Overview

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        AURORA SERVERLESS V2                                     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    CAPACITY AUTO-SCALING                                 │   │
│  │                                                                          │   │
│  │     Capacity (ACUs)                                                      │   │
│  │      ▲                                                                   │   │
│  │  128 │                        ┌───────┐                                  │   │
│  │      │                        │       │         Max ACUs                 │   │
│  │   64 │                   ┌────┘       └────┐                             │   │
│  │      │              ┌────┘                 └────┐                        │   │
│  │   32 │         ┌────┘                          └────┐                    │   │
│  │      │    ┌────┘                                    └────┐               │   │
│  │    8 │────┘                                              └────           │   │
│  │      │                                                        Min ACUs   │   │
│  │  0.5 │────────────────────────────────────────────────────────          │   │
│  │      └────────────────────────────────────────────────────────────▶      │   │
│  │                              Time                                        │   │
│  │                                                                          │   │
│  │  1 ACU = 2 GB memory + proportional CPU and networking                  │   │
│  │                                                                          │   │
│  │  Features:                                                               │   │
│  │  ├── Scales in 0.5 ACU increments                                       │   │
│  │  ├── Scales in seconds (not minutes)                                    │   │
│  │  ├── Can scale to zero (v1 only)                                        │   │
│  │  ├── Mixed with provisioned instances in same cluster                   │   │
│  │  └── Same storage layer as provisioned Aurora                           │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Serverless v2 Configuration

```bash
# Create Aurora Serverless v2 cluster
aws rds create-db-cluster \
    --db-cluster-identifier my-serverless-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 \
    --master-username admin \
    --master-user-password YourPassword123! \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name my-subnet-group

# Add Serverless v2 instance
aws rds create-db-instance \
    --db-instance-identifier my-serverless-instance \
    --db-instance-class db.serverless \
    --engine aurora-mysql \
    --db-cluster-identifier my-serverless-cluster
```

### Serverless v2 Pricing (us-east-1)

| Component | Aurora MySQL | Aurora PostgreSQL |
|-----------|--------------|-------------------|
| **ACU-hour** | $0.12 | $0.12 |
| **Storage** | $0.10/GB-month | $0.10/GB-month |
| **I/O** | $0.20/million requests | $0.20/million requests |

**Cost Example:**
```
Scenario: Average 4 ACUs for 8 hours/day, 30 days
- Compute: 4 ACUs × 8 hours × 30 days × $0.12 = $115.20/month
- Storage: 50 GB × $0.10 = $5/month
- I/O: 10 million requests × $0.20 = $2/month
Total: ~$122/month
```

### Serverless v2 vs Provisioned

| Aspect | Serverless v2 | Provisioned |
|--------|---------------|-------------|
| **Best For** | Variable workloads | Predictable workloads |
| **Scaling** | Automatic, seconds | Manual or Auto Scaling |
| **Minimum Cost** | 0.5 ACU × hours | Full instance cost |
| **Predictable Cost** | Variable | Fixed |
| **Features** | All Aurora features | All Aurora features |
| **Multi-AZ** | Yes | Yes |

## Aurora Global Database

### Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        AURORA GLOBAL DATABASE                                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     PRIMARY REGION (us-east-1)                           │   │
│  │                                                                          │   │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │   │
│  │  │                    PRIMARY CLUSTER                                 │  │   │
│  │  │                                                                    │  │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                            │  │   │
│  │  │  │ Writer  │  │ Reader  │  │ Reader  │                            │  │   │
│  │  │  │         │  │   #1    │  │   #2    │                            │  │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘                            │  │   │
│  │  │                                                                    │  │   │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │   │
│  │  │  │              PRIMARY STORAGE (6 copies, 3 AZs)               │  │  │   │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │   │
│  │  │                                │                                   │  │   │
│  │  └────────────────────────────────┼───────────────────────────────────┘  │   │
│  │                                   │                                       │   │
│  └───────────────────────────────────┼───────────────────────────────────────┘   │
│                                      │                                           │
│                    Storage-level replication (< 1 second lag)                   │
│                                      │                                           │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐   │
│  │                     SECONDARY REGION (eu-west-1)                          │   │
│  │                                   │                                        │   │
│  │  ┌────────────────────────────────┼───────────────────────────────────┐   │   │
│  │  │                    SECONDARY CLUSTER                                │   │   │
│  │  │                                ▼                                    │   │   │
│  │  │  ┌─────────────────────────────────────────────────────────────┐   │   │   │
│  │  │  │            SECONDARY STORAGE (6 copies, 3 AZs)               │   │   │   │
│  │  │  └─────────────────────────────────────────────────────────────┘   │   │   │
│  │  │                                                                     │   │   │
│  │  │  ┌─────────┐  ┌─────────┐                                          │   │   │
│  │  │  │ Reader  │  │ Reader  │    (Read-only until promoted)           │   │   │
│  │  │  │   #1    │  │   #2    │                                          │   │   │
│  │  │  └─────────┘  └─────────┘                                          │   │   │
│  │  │                                                                     │   │   │
│  │  └─────────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                            │   │
│  └────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                   │
│  GLOBAL DATABASE FEATURES:                                                       │
│  ├── Up to 5 secondary regions                                                  │
│  ├── Sub-second replication lag (typically < 1 second)                          │
│  ├── RTO < 1 minute for region failover                                         │
│  ├── Write forwarding (secondary can forward writes to primary)                 │
│  └── Managed RPO/RTO monitoring                                                 │
│                                                                                   │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Create Global Database

```bash
# Create primary cluster
aws rds create-db-cluster \
    --db-cluster-identifier primary-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --global-cluster-identifier my-global-cluster \
    --master-username admin \
    --master-user-password YourPassword123! \
    --region us-east-1

# Add primary instance
aws rds create-db-instance \
    --db-instance-identifier primary-instance \
    --db-cluster-identifier primary-cluster \
    --db-instance-class db.r6g.large \
    --engine aurora-mysql \
    --region us-east-1

# Create global cluster
aws rds create-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --source-db-cluster-identifier arn:aws:rds:us-east-1:123456789012:cluster:primary-cluster

# Add secondary cluster
aws rds create-db-cluster \
    --db-cluster-identifier secondary-cluster \
    --engine aurora-mysql \
    --engine-version 8.0.mysql_aurora.3.04.0 \
    --global-cluster-identifier my-global-cluster \
    --region eu-west-1

# Add secondary instance
aws rds create-db-instance \
    --db-instance-identifier secondary-instance \
    --db-cluster-identifier secondary-cluster \
    --db-instance-class db.r6g.large \
    --engine aurora-mysql \
    --region eu-west-1
```

### Global Database Failover

```bash
# Planned failover (switchover)
# 1. Stop application writes
# 2. Wait for replication to catch up
# 3. Detach secondary cluster
aws rds remove-from-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --db-cluster-identifier arn:aws:rds:eu-west-1:123456789012:cluster:secondary-cluster

# Secondary cluster becomes standalone and writable

# Unplanned failover
aws rds failover-global-cluster \
    --global-cluster-identifier my-global-cluster \
    --target-db-cluster-identifier arn:aws:rds:eu-west-1:123456789012:cluster:secondary-cluster
```

## Aurora Parallel Query

### How It Works

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          PARALLEL QUERY                                         │
│                                                                                 │
│  TRADITIONAL QUERY (without Parallel Query):                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │   Storage → Read all data → Buffer Pool → Process Query → Return Results │ │
│  │             (I/O bound)      (Memory)      (CPU bound)                    │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  WITH PARALLEL QUERY:                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                           │ │
│  │   Storage Layer                                                           │ │
│  │   ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │ │
│  │   │  │ Storage  │  │ Storage  │  │ Storage  │  │ Storage  │            │ │ │
│  │   │  │ Node 1   │  │ Node 2   │  │ Node 3   │  │ Node 4   │            │ │ │
│  │   │  │          │  │          │  │          │  │          │            │ │ │
│  │   │  │ Filter   │  │ Filter   │  │ Filter   │  │ Filter   │            │ │ │
│  │   │  │ Aggregate│  │ Aggregate│  │ Aggregate│  │ Aggregate│            │ │ │
│  │   │  │ Project  │  │ Project  │  │ Project  │  │ Project  │            │ │ │
│  │   │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │ │ │
│  │   │       │             │             │             │                   │ │ │
│  │   │       └──────────┬──┴──────┬──────┴─────────────┘                   │ │ │
│  │   │                  │         │                                        │ │ │
│  │   │                  ▼         ▼                                        │ │ │
│  │   │            (Only matching, aggregated data returned)               │ │ │
│  │   └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                            │                                              │ │
│  │                            ▼                                              │ │
│  │   Compute Layer     (Final aggregation, minimal data)                    │ │
│  │   ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │   │                    Aurora Instance                                   │ │ │
│  │   │              (Only processes pre-filtered data)                      │ │ │
│  │   └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  BENEFITS:                                                                     │
│  ├── Query processing pushed to storage layer                                 │
│  ├── Reduces data transferred between storage and compute                     │
│  ├── Ideal for analytical queries on large tables                            │
│  ├── Works on rarely accessed (cold) data                                    │
│  └── No impact on buffer pool (hot data stays cached)                        │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Enable Parallel Query

```bash
# Enable via parameter group
aws rds modify-db-cluster-parameter-group \
    --db-cluster-parameter-group-name my-aurora-params \
    --parameters "ParameterName=aurora_parallel_query,ParameterValue=ON,ApplyMethod=immediate"

# Or per session
SET aurora_pq = 1;

# Check if query uses parallel query
EXPLAIN SELECT SUM(amount) FROM large_table WHERE date > '2024-01-01';
```

## Aurora Backtrack

### Overview

Backtrack allows you to rewind the database to a previous point in time without restoring from backup.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                              BACKTRACK                                          │
│                                                                                 │
│   Database Timeline:                                                            │
│                                                                                 │
│   ├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┤          │
│   │          │          │          │    ▲     │          │          │          │
│   T-6h      T-5h       T-4h       T-3h   │    T-2h       T-1h       Now        │
│                                          │                                      │
│                               Backtrack to here                                 │
│                               (takes seconds)                                   │
│                                                                                 │
│   How it works:                                                                │
│   1. Aurora continuously logs changes                                          │
│   2. Backtrack reverses those changes                                          │
│   3. Database goes back in time (in-place, not restore)                        │
│   4. Takes seconds, not hours                                                  │
│                                                                                 │
│   Use Cases:                                                                   │
│   ├── Undo accidental DELETE or UPDATE                                         │
│   ├── Quickly recover from application bugs                                    │
│   ├── Explore data as it was at a previous time                               │
│   └── Test scenario recovery                                                   │
│                                                                                 │
│   Limitations:                                                                 │
│   ├── Aurora MySQL only                                                        │
│   ├── Maximum 72 hours of backtrack                                           │
│   ├── Cluster-wide operation (affects all instances)                          │
│   ├── Replication paused during backtrack                                      │
│   └── Cannot cross DDL operations that modify table structure                 │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Using Backtrack

```bash
# Enable backtrack (during cluster creation or modification)
aws rds modify-db-cluster \
    --db-cluster-identifier my-cluster \
    --backtrack-window 86400  # 24 hours in seconds

# Backtrack to specific time
aws rds backtrack-db-cluster \
    --db-cluster-identifier my-cluster \
    --backtrack-to "2024-01-15T10:30:00Z"

# Check backtrack status
aws rds describe-db-clusters \
    --db-cluster-identifier my-cluster \
    --query 'DBClusters[0].[EarliestBacktrackTime,BacktrackWindow]'
```

## Aurora Pricing (us-east-1)

### Instance Pricing

| Instance Class | Aurora MySQL ($/hr) | Aurora PostgreSQL ($/hr) |
|----------------|---------------------|--------------------------|
| db.t3.medium | $0.082 | $0.082 |
| db.r6g.large | $0.210 | $0.210 |
| db.r6g.xlarge | $0.420 | $0.420 |
| db.r6g.2xlarge | $0.840 | $0.840 |
| db.r6g.4xlarge | $1.680 | $1.680 |

### Storage and I/O Pricing

| Component | Price |
|-----------|-------|
| Storage | $0.10/GB-month |
| I/O | $0.20/million requests |
| Backtrack | $0.012/million change records |

### Cost Comparison Example

```
Scenario: Medium production workload

RDS MySQL Multi-AZ:
- db.r6g.large × 2 (Multi-AZ) = $0.420/hr × 730 = $306/month
- Storage: 200 GB × $0.23 = $46/month
Total: ~$352/month

Aurora MySQL:
- db.r6g.large × 1 (writer) = $0.210/hr × 730 = $153/month
- db.r6g.large × 1 (reader) = $0.210/hr × 730 = $153/month
- Storage: 200 GB × $0.10 = $20/month
- I/O: 50M requests × $0.20 = $10/month
Total: ~$336/month

Note: Aurora provides better availability and performance at similar cost
```

## Summary

- Aurora provides 5x MySQL and 3x PostgreSQL performance
- Storage automatically scales up to 128 TB with 6-way replication
- Supports up to 15 read replicas with < 100ms replica lag
- Failover typically completes in < 30 seconds
- Serverless v2 provides automatic scaling for variable workloads
- Global Database enables sub-second cross-region replication
- Parallel Query optimizes analytical queries on large datasets
- Backtrack allows instant point-in-time recovery without restore

---

**Next:** [08 - DynamoDB](./08-dynamodb.md)

**Previous:** [06 - RDS Monitoring](./06-rds-monitoring.md)
