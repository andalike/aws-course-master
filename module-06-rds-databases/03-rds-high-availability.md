# 03 - RDS High Availability

## Overview

Amazon RDS provides multiple features for high availability and disaster recovery:

1. **Multi-AZ Deployments** - Automatic failover within a region
2. **Read Replicas** - Read scaling and cross-region disaster recovery
3. **Cross-Region Replicas** - Geographic redundancy

## Multi-AZ Deployments

### How Multi-AZ Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS REGION                                      │
│                                                                              │
│  ┌────────────────────────────┐     ┌────────────────────────────┐         │
│  │     Availability Zone A     │     │     Availability Zone B     │         │
│  │                             │     │                             │         │
│  │  ┌───────────────────────┐ │     │ ┌───────────────────────┐  │         │
│  │  │    PRIMARY INSTANCE   │ │     │ │   STANDBY INSTANCE    │  │         │
│  │  │                       │ │     │ │                       │  │         │
│  │  │  ┌─────────────────┐  │ │     │ │ ┌─────────────────┐   │  │         │
│  │  │  │   DB Engine     │  │ │     │ │ │   DB Engine     │   │  │         │
│  │  │  └─────────────────┘  │ │     │ │ └─────────────────┘   │  │         │
│  │  │                       │ │     │ │                       │  │         │
│  │  │  ┌─────────────────┐  │ │     │ │ ┌─────────────────┐   │  │         │
│  │  │  │   EBS Storage   │  │ │═════│═│ │   EBS Storage   │   │  │         │
│  │  │  └─────────────────┘  │ │Sync │ │ └─────────────────┘   │  │         │
│  │  │                       │ │Repl │ │                       │  │         │
│  │  └───────────────────────┘ │     │ └───────────────────────┘  │         │
│  │                             │     │                             │         │
│  └────────────────────────────┘     └────────────────────────────┘         │
│                                                                              │
│                          ┌──────────────┐                                   │
│                          │  DNS Endpoint │                                   │
│                          │  (Automatic   │                                   │
│                          │   Failover)   │                                   │
│                          └──────────────┘                                   │
│                                 ▲                                            │
│                                 │                                            │
└─────────────────────────────────┼────────────────────────────────────────────┘
                                  │
                           ┌──────┴──────┐
                           │ Application │
                           └─────────────┘
```

### Key Characteristics

| Feature | Multi-AZ |
|---------|----------|
| **Purpose** | High availability and durability |
| **Replication** | Synchronous |
| **Failover** | Automatic (60-120 seconds) |
| **Endpoint** | Single DNS endpoint |
| **Standby Access** | No read/write access |
| **Region** | Same region, different AZ |
| **Cost** | ~2x single instance |

### Multi-AZ Failover Process

```
Normal Operation:
┌─────────────────────────────────────────┐
│                                         │
│   App ──► DNS ──► Primary (Active)      │
│                     │                   │
│                     │ Sync Replication  │
│                     ▼                   │
│              Standby (Passive)          │
│                                         │
└─────────────────────────────────────────┘

Failover Triggered:
┌─────────────────────────────────────────┐
│                                         │
│   1. Primary failure detected           │
│   2. DNS TTL expires (~60 seconds)      │
│   3. Standby promoted to Primary        │
│   4. DNS points to new Primary          │
│                                         │
│   App ──► DNS ──► New Primary           │
│              (Former Standby)           │
│                                         │
└─────────────────────────────────────────┘
```

### Failover Triggers

| Event | Automatic Failover? |
|-------|---------------------|
| Primary AZ failure | Yes |
| Primary instance failure | Yes |
| Primary storage failure | Yes |
| Network connectivity loss | Yes |
| Instance scaling (modify) | Yes |
| OS patching | Yes |
| Database engine patching | Yes |
| Manual failover (reboot with failover) | Yes |

### Enabling Multi-AZ

```bash
# Create new instance with Multi-AZ
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --multi-az \
    # ... other options

# Convert existing instance to Multi-AZ
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --multi-az \
    --apply-immediately

# Manual failover (reboot with failover)
aws rds reboot-db-instance \
    --db-instance-identifier mydb \
    --force-failover
```

### Multi-AZ Pricing Impact

| Engine | Single-AZ | Multi-AZ | Price Increase |
|--------|-----------|----------|----------------|
| MySQL (db.r6g.large) | $0.210/hr | $0.420/hr | 2x |
| PostgreSQL (db.r6g.large) | $0.210/hr | $0.420/hr | 2x |
| Oracle SE2-LI (db.r6g.large) | $0.484/hr | $0.968/hr | 2x |
| SQL Server SE-LI (db.r6g.large) | $0.580/hr | $1.160/hr | 2x |

**Note:** Multi-AZ doubles compute costs but also doubles storage costs.

## Read Replicas

### How Read Replicas Work

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│  ┌─────────────────────┐                                                      │
│  │   WRITE TRAFFIC     │                                                      │
│  │   (Primary Only)    │                                                      │
│  └──────────┬──────────┘                                                      │
│             │                                                                  │
│             ▼                                                                  │
│  ┌─────────────────────┐        Async Replication                             │
│  │                     │ ─────────────────────────────┐                       │
│  │   PRIMARY INSTANCE  │ ─────────────────────┐       │                       │
│  │                     │ ──────────┐          │       │                       │
│  └─────────────────────┘           │          │       │                       │
│                                    ▼          ▼       ▼                       │
│                           ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│                           │ Read     │ │ Read     │ │ Read     │             │
│                           │ Replica 1│ │ Replica 2│ │ Replica 3│             │
│                           └────┬─────┘ └────┬─────┘ └────┬─────┘             │
│                                │            │            │                    │
│                                └────────────┴────────────┘                    │
│                                             │                                  │
│                                             ▼                                  │
│                              ┌──────────────────────────┐                     │
│                              │      READ TRAFFIC        │                     │
│                              │   (Load Balanced)        │                     │
│                              └──────────────────────────┘                     │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Read Replica Characteristics

| Feature | Read Replica |
|---------|--------------|
| **Purpose** | Read scaling, reporting, disaster recovery |
| **Replication** | Asynchronous |
| **Read Access** | Yes |
| **Write Access** | No (until promoted) |
| **Endpoint** | Separate endpoint per replica |
| **Max Replicas** | 5 (MySQL, MariaDB, PostgreSQL, Oracle), 5 (SQL Server) |
| **Cross-Region** | Yes (except SQL Server) |
| **Promotion** | Can be promoted to standalone |

### Read Replica vs Multi-AZ

| Aspect | Multi-AZ | Read Replica |
|--------|----------|--------------|
| **Purpose** | High availability | Read scaling |
| **Replication** | Synchronous | Asynchronous |
| **Failover** | Automatic | Manual (promotion) |
| **Read Traffic** | No | Yes |
| **Latency** | None (same region) | Replica lag possible |
| **Cross-Region** | No | Yes |
| **Separate Endpoint** | No | Yes |
| **Can be Multi-AZ** | N/A | Yes |

### Creating Read Replicas

```bash
# Create read replica in same region
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-1 \
    --source-db-instance-identifier mydb \
    --db-instance-class db.r6g.large

# Create cross-region read replica
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-eu \
    --source-db-instance-identifier arn:aws:rds:us-east-1:123456789012:db:mydb \
    --source-region us-east-1 \
    --region eu-west-1 \
    --db-instance-class db.r6g.large \
    --kms-key-id arn:aws:kms:eu-west-1:123456789012:key/12345678-1234-1234-1234-123456789012

# Create replica with different storage
aws rds create-db-instance-read-replica \
    --db-instance-identifier mydb-replica-analytics \
    --source-db-instance-identifier mydb \
    --db-instance-class db.r6g.2xlarge \
    --storage-type io1 \
    --iops 10000
```

### Promoting a Read Replica

When you promote a read replica, it becomes a standalone database instance:

```bash
# Promote read replica
aws rds promote-read-replica \
    --db-instance-identifier mydb-replica-1

# Promote with backup settings
aws rds promote-read-replica \
    --db-instance-identifier mydb-replica-1 \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"
```

**Promotion Use Cases:**
- Disaster recovery (cross-region failover)
- Database sharding (split database)
- Database refresh for testing
- Migration strategy

### Read Replica Chains (MySQL/MariaDB)

MySQL and MariaDB support cascading replicas:

```
┌──────────────┐
│   Primary    │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Replica 1   │────▶│  Replica 1a  │ (Replica of Replica)
└──────────────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Replica 2   │────▶│  Replica 2a  │
└──────────────┘     └──────────────┘

Maximum Chain Depth: 4 levels
```

### Replica Lag Monitoring

```sql
-- MySQL: Check replica lag
SHOW SLAVE STATUS\G

-- Key metrics:
-- Seconds_Behind_Master: Lag in seconds
-- Slave_IO_Running: Should be "Yes"
-- Slave_SQL_Running: Should be "Yes"

-- PostgreSQL: Check replica lag
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

**CloudWatch Metrics for Replica Lag:**
- `ReplicaLag` - Seconds behind primary
- `ReplicaLagMaximum` - Maximum lag in cluster

## Cross-Region Replicas

### Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ┌─────────────────────────┐          ┌─────────────────────────┐           │
│  │      US-EAST-1          │          │       EU-WEST-1         │           │
│  │                         │          │                         │           │
│  │  ┌───────────────────┐  │          │  ┌───────────────────┐  │           │
│  │  │                   │  │   Async  │  │                   │  │           │
│  │  │  PRIMARY (Multi-AZ)│══════════════▶│  CROSS-REGION     │  │           │
│  │  │                   │  │   Repl   │  │  READ REPLICA     │  │           │
│  │  └───────────────────┘  │  (SSL)   │  └───────────────────┘  │           │
│  │           │             │          │                         │           │
│  │           │ Sync        │          │  Can be promoted for   │           │
│  │           ▼             │          │  disaster recovery     │           │
│  │  ┌───────────────────┐  │          │                         │           │
│  │  │   STANDBY         │  │          │                         │           │
│  │  └───────────────────┘  │          │                         │           │
│  │                         │          │                         │           │
│  └─────────────────────────┘          └─────────────────────────┘           │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Cross-Region Replica Benefits

1. **Disaster Recovery**: Promote replica if primary region fails
2. **Lower Latency**: Serve read traffic from closer region
3. **Migration**: Use for region migration
4. **Reporting**: Offload reporting to another region

### Cross-Region Replica Costs

| Cost Component | Description |
|----------------|-------------|
| Instance Cost | Standard RDS pricing in target region |
| Storage Cost | Standard storage pricing in target region |
| Data Transfer | Cross-region data transfer charges |

**Data Transfer Pricing (approximate):**
- US to EU: $0.02/GB
- US to Asia Pacific: $0.09/GB
- Cross-region within US: $0.02/GB

### Cross-Region Disaster Recovery Runbook

```
CROSS-REGION FAILOVER PROCEDURE

1. ASSESS SITUATION
   □ Confirm primary region failure
   □ Check primary region status page
   □ Verify replica lag before failure
   □ Estimate data loss (RPO)

2. PREPARE FOR FAILOVER
   □ Notify stakeholders
   □ Stop writes to primary (if accessible)
   □ Wait for replica to catch up (if possible)

3. PROMOTE REPLICA
   aws rds promote-read-replica \
       --db-instance-identifier mydb-replica-eu \
       --backup-retention-period 7

4. UPDATE APPLICATION
   □ Update connection strings
   □ Update DNS records (if using CNAME)
   □ Verify application connectivity

5. POST-FAILOVER
   □ Enable Multi-AZ on promoted instance
   □ Create new read replicas
   □ Update monitoring/alerting
   □ Document the incident
```

## Aurora High Availability

Aurora has built-in high availability features that differ from standard RDS:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          AURORA CLUSTER                                         │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                       AURORA STORAGE LAYER                               │   │
│  │                                                                          │   │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │   │ Storage  │  │ Storage  │  │ Storage  │  │ Storage  │  │ Storage  │ │   │
│  │   │ Node 1   │  │ Node 2   │  │ Node 3   │  │ Node 4   │  │ Node 5   │ │   │
│  │   │  (AZ-A)  │  │  (AZ-B)  │  │  (AZ-C)  │  │  (AZ-A)  │  │  (AZ-B)  │ │   │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │   │
│  │                                                                          │   │
│  │   6 copies of data across 3 AZs (4/6 quorum for writes, 3/6 for reads)  │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                          ▲            ▲            ▲                           │
│                          │            │            │                           │
│              ┌───────────┘            │            └───────────┐               │
│              │                        │                        │               │
│  ┌───────────┴──────────┐  ┌─────────┴──────────┐  ┌─────────┴──────────┐    │
│  │      PRIMARY         │  │     REPLICA 1      │  │     REPLICA 2      │    │
│  │   Writer Instance    │  │   Reader Instance  │  │   Reader Instance  │    │
│  │      (AZ-A)          │  │      (AZ-B)        │  │      (AZ-C)        │    │
│  └──────────────────────┘  └────────────────────┘  └────────────────────┘    │
│              ▲                        ▲                        ▲               │
│              │                        │                        │               │
│              │             ┌──────────┴──────────┐             │               │
│              │             │   READER ENDPOINT   │             │               │
│              │             │   (Load Balanced)   │             │               │
│   ┌──────────┴──────────┐  └─────────────────────┘             │               │
│   │   CLUSTER ENDPOINT  │                                      │               │
│   │   (Writer Traffic)  │                                      │               │
│   └─────────────────────┘                                      │               │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Aurora vs RDS Multi-AZ Comparison

| Feature | RDS Multi-AZ | Aurora |
|---------|--------------|--------|
| Storage Replication | Synchronous to standby | 6-way replication across 3 AZs |
| Failover Time | 60-120 seconds | < 30 seconds |
| Standby Readable | No | Yes (replicas) |
| Max Read Replicas | 5 | 15 |
| Storage Failure Recovery | EBS-based | Self-healing storage |
| Crash Recovery | Instance-based | Parallel, faster |

## Best Practices

### High Availability Architecture

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION ARCHITECTURE                                │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         PRIMARY REGION (us-east-1)                       │   │
│  │                                                                          │   │
│  │   ┌──────────────────────────────────────────────────────────────────┐  │   │
│  │   │                     MULTI-AZ DEPLOYMENT                          │  │   │
│  │   │                                                                   │  │   │
│  │   │   ┌─────────────┐         ┌─────────────┐                        │  │   │
│  │   │   │   PRIMARY   │ ◄─Sync─▶│   STANDBY   │                        │  │   │
│  │   │   │    (AZ-A)   │         │    (AZ-B)   │                        │  │   │
│  │   │   └─────────────┘         └─────────────┘                        │  │   │
│  │   │          │                                                        │  │   │
│  │   │          │ Async                                                  │  │   │
│  │   │          ▼                                                        │  │   │
│  │   │   ┌─────────────┐  ┌─────────────┐                               │  │   │
│  │   │   │ READ REPLICA│  │ READ REPLICA│  (Multi-AZ Replicas)          │  │   │
│  │   │   │     #1      │  │     #2      │                               │  │   │
│  │   │   └─────────────┘  └─────────────┘                               │  │   │
│  │   │                                                                   │  │   │
│  │   └──────────────────────────────────────────────────────────────────┘  │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                      │
│                                          │ Async (Cross-Region)                │
│                                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        DR REGION (eu-west-1)                             │   │
│  │                                                                          │   │
│  │   ┌─────────────────────┐                                               │   │
│  │   │ CROSS-REGION REPLICA│  (Multi-AZ enabled)                           │   │
│  │   │   (Promotable)      │                                               │   │
│  │   └─────────────────────┘                                               │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Recommendations

| Requirement | Recommendation |
|-------------|----------------|
| Production Workloads | Multi-AZ enabled |
| Read-Heavy Applications | Add read replicas |
| Global Applications | Cross-region replicas |
| RPO < 5 minutes | Synchronous replication (Multi-AZ) |
| RTO < 1 minute | Consider Aurora |
| Cost-Sensitive | Single-AZ with regular backups |

### Connection String Management

```python
# Python example with read/write splitting
import mysql.connector
from mysql.connector import pooling

# Write connection pool (Primary)
write_pool = pooling.MySQLConnectionPool(
    pool_name="write_pool",
    pool_size=10,
    host="mydb.abc123.us-east-1.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="password",
    database="myapp"
)

# Read connection pool (Replicas - round-robin)
replica_hosts = [
    "mydb-replica-1.abc123.us-east-1.rds.amazonaws.com",
    "mydb-replica-2.abc123.us-east-1.rds.amazonaws.com"
]

read_pools = [
    pooling.MySQLConnectionPool(
        pool_name=f"read_pool_{i}",
        pool_size=10,
        host=host,
        port=3306,
        user="readonly",
        password="password",
        database="myapp"
    )
    for i, host in enumerate(replica_hosts)
]

# Simple round-robin for reads
import itertools
read_pool_cycle = itertools.cycle(read_pools)

def get_read_connection():
    pool = next(read_pool_cycle)
    return pool.get_connection()

def get_write_connection():
    return write_pool.get_connection()
```

## Summary

- **Multi-AZ** provides automatic failover for high availability (synchronous replication)
- **Read Replicas** enable read scaling and can be promoted for DR (asynchronous replication)
- **Cross-Region Replicas** provide geographic redundancy and disaster recovery
- Aurora offers faster failover and more replicas than standard RDS
- Use connection pooling with read/write splitting for optimal performance
- Always test your failover procedures regularly

---

**Next:** [04 - RDS Security](./04-rds-security.md)

**Previous:** [02 - RDS Instance Setup](./02-rds-instance-setup.md)
