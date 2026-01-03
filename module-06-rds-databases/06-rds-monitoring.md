# 06 - RDS Monitoring

## Monitoring Overview

Amazon RDS provides multiple monitoring tools to help you understand database performance and health:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        RDS MONITORING ECOSYSTEM                                 │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        CLOUDWATCH METRICS                                │   │
│  │                                                                          │   │
│  │  Standard Metrics (1-minute granularity)                                 │   │
│  │  ├── CPU, Memory, Storage                                               │   │
│  │  ├── Network I/O                                                        │   │
│  │  ├── Database Connections                                               │   │
│  │  ├── IOPS (Read/Write)                                                  │   │
│  │  └── Latency                                                            │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                       ENHANCED MONITORING                                │   │
│  │                                                                          │   │
│  │  OS-Level Metrics (1-60 second granularity)                             │   │
│  │  ├── Process list                                                       │   │
│  │  ├── Memory breakdown                                                   │   │
│  │  ├── File system metrics                                                │   │
│  │  └── CPU utilization per process                                        │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      PERFORMANCE INSIGHTS                                │   │
│  │                                                                          │   │
│  │  Database Performance Analysis                                           │   │
│  │  ├── Database load visualization                                        │   │
│  │  ├── Top SQL queries                                                    │   │
│  │  ├── Wait event analysis                                                │   │
│  │  └── Historical performance data                                        │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                       DATABASE LOGS                                      │   │
│  │                                                                          │   │
│  │  ├── Error logs                                                         │   │
│  │  ├── Slow query logs                                                    │   │
│  │  ├── General logs                                                       │   │
│  │  └── Audit logs                                                         │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## CloudWatch Metrics

### Key RDS Metrics

| Metric | Description | Unit | Alert Threshold |
|--------|-------------|------|-----------------|
| **CPUUtilization** | CPU usage percentage | Percent | > 80% |
| **DatabaseConnections** | Active connections | Count | > 90% of max |
| **FreeableMemory** | Available RAM | Bytes | < 10% of total |
| **FreeStorageSpace** | Available storage | Bytes | < 10% or < 10 GB |
| **ReadIOPS** | Read I/O operations/sec | Count/Second | Varies |
| **WriteIOPS** | Write I/O operations/sec | Count/Second | Varies |
| **ReadLatency** | Read operation latency | Seconds | > 0.020 (20ms) |
| **WriteLatency** | Write operation latency | Seconds | > 0.020 (20ms) |
| **DiskQueueDepth** | I/O waiting in queue | Count | > 1 sustained |
| **NetworkReceiveThroughput** | Incoming network bytes | Bytes/Second | Varies |
| **NetworkTransmitThroughput** | Outgoing network bytes | Bytes/Second | Varies |
| **SwapUsage** | Swap memory used | Bytes | > 0 |
| **BurstBalance** | gp2 burst credits remaining | Percent | < 20% |
| **ReplicaLag** | Replication delay | Seconds | > 60 |

### CloudWatch Alarms

```bash
# Create CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name rds-mydb-high-cpu \
    --alarm-description "RDS CPU utilization over 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=mydb \
    --evaluation-periods 3 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts \
    --ok-actions arn:aws:sns:us-east-1:123456789012:alerts

# Create low storage alarm
aws cloudwatch put-metric-alarm \
    --alarm-name rds-mydb-low-storage \
    --alarm-description "RDS storage below 10GB" \
    --metric-name FreeStorageSpace \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 10737418240 \
    --comparison-operator LessThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=mydb \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts

# Create replica lag alarm
aws cloudwatch put-metric-alarm \
    --alarm-name rds-replica-lag-high \
    --alarm-description "Replica lag exceeds 60 seconds" \
    --metric-name ReplicaLag \
    --namespace AWS/RDS \
    --statistic Average \
    --period 60 \
    --threshold 60 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=mydb-replica \
    --evaluation-periods 5 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### CloudWatch Dashboard

```json
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "RDS CPU Utilization",
                "metrics": [
                    ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "mydb"]
                ],
                "period": 60,
                "stat": "Average",
                "region": "us-east-1"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "Database Connections",
                "metrics": [
                    ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "mydb"]
                ],
                "period": 60,
                "stat": "Average",
                "region": "us-east-1"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "IOPS",
                "metrics": [
                    ["AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", "mydb"],
                    [".", "WriteIOPS", ".", "."]
                ],
                "period": 60,
                "stat": "Average",
                "region": "us-east-1"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "title": "Latency",
                "metrics": [
                    ["AWS/RDS", "ReadLatency", "DBInstanceIdentifier", "mydb"],
                    [".", "WriteLatency", ".", "."]
                ],
                "period": 60,
                "stat": "Average",
                "region": "us-east-1"
            }
        }
    ]
}
```

## Enhanced Monitoring

### Enabling Enhanced Monitoring

```bash
# Create IAM role for Enhanced Monitoring
aws iam create-role \
    --role-name rds-enhanced-monitoring-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "monitoring.rds.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach policy
aws iam attach-role-policy \
    --role-name rds-enhanced-monitoring-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole

# Enable Enhanced Monitoring (1-second granularity)
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --monitoring-interval 1 \
    --monitoring-role-arn arn:aws:iam::123456789012:role/rds-enhanced-monitoring-role \
    --apply-immediately
```

### Enhanced Monitoring Metrics

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      ENHANCED MONITORING METRICS                                │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  CPU METRICS                                                             │   │
│  │  ├── guest: CPU used by guest programs                                  │   │
│  │  ├── idle: CPU idle                                                     │   │
│  │  ├── irq: CPU used by software interrupts                               │   │
│  │  ├── nice: CPU used by low-priority processes                           │   │
│  │  ├── steal: CPU stolen by hypervisor                                    │   │
│  │  ├── system: CPU used by kernel                                         │   │
│  │  ├── total: Total CPU usage                                             │   │
│  │  ├── user: CPU used by user processes                                   │   │
│  │  └── wait: CPU waiting for I/O                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  MEMORY METRICS                                                          │   │
│  │  ├── active: Memory recently used                                       │   │
│  │  ├── buffers: Memory for buffering I/O                                  │   │
│  │  ├── cached: Memory for caching file system                             │   │
│  │  ├── dirty: Memory waiting for write                                    │   │
│  │  ├── free: Free memory                                                  │   │
│  │  ├── hugePagesFree: Free huge pages                                     │   │
│  │  ├── hugePagesTotal: Total huge pages                                   │   │
│  │  ├── inactive: Memory not recently used                                 │   │
│  │  ├── mapped: Memory-mapped files                                        │   │
│  │  ├── pageTables: Memory for page tables                                 │   │
│  │  ├── slab: Kernel data structures                                       │   │
│  │  ├── total: Total memory                                                │   │
│  │  └── writeback: Memory being written back                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  DISK I/O METRICS                                                        │   │
│  │  ├── avgQueueLen: Average queue length                                  │   │
│  │  ├── avgReqSz: Average request size                                     │   │
│  │  ├── await: Average time for I/O requests                               │   │
│  │  ├── readIOsPS: Read operations per second                              │   │
│  │  ├── readKb: KB read per second                                         │   │
│  │  ├── readKbPS: KB/second read                                           │   │
│  │  ├── rrqmPS: Merged read requests per second                            │   │
│  │  ├── tps: Transactions per second                                       │   │
│  │  ├── util: Disk utilization percentage                                  │   │
│  │  ├── writeIOsPS: Write operations per second                            │   │
│  │  ├── writeKb: KB written per second                                     │   │
│  │  ├── writeKbPS: KB/second written                                       │   │
│  │  └── wrqmPS: Merged write requests per second                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PROCESS LIST                                                            │   │
│  │  ├── vss: Virtual memory size                                           │   │
│  │  ├── rss: Resident set size (physical memory)                           │   │
│  │  ├── memoryUsedPc: Memory usage percentage                              │   │
│  │  ├── cpuUsedPc: CPU usage percentage                                    │   │
│  │  └── name: Process name                                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Monitoring Intervals and Costs

| Interval | Data Points/Hour | Cost Impact |
|----------|------------------|-------------|
| 1 second | 3,600 | Highest |
| 5 seconds | 720 | High |
| 10 seconds | 360 | Medium |
| 15 seconds | 240 | Medium |
| 30 seconds | 120 | Low |
| 60 seconds | 60 | Lowest |

## Performance Insights

### Overview

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        PERFORMANCE INSIGHTS                                     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  DATABASE LOAD CHART                                                     │   │
│  │                                                                          │   │
│  │     AAS (Average Active Sessions)                                        │   │
│  │      ▲                                                                   │   │
│  │   8  │  ████                                                             │   │
│  │   7  │  ████░░                                                           │   │
│  │   6  │  ████░░░░                                                         │   │
│  │   5  │  ████░░░░████                                                     │   │
│  │   4  │  ████░░░░████████      Max vCPU = 4                               │   │
│  │   3  │  ████░░░░████████ ─────────────────────────────────              │   │
│  │   2  │  ████░░░░████████░░░░████                                         │   │
│  │   1  │  ████░░░░████████░░░░████░░░░                                     │   │
│  │   0  └──────────────────────────────────────────────────────────────▶   │   │
│  │          Time                                                            │   │
│  │                                                                          │   │
│  │  Legend:  ████ CPU    ░░░░ I/O Wait    ░░░░ Lock Wait                   │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  TOP SQL                                                                 │   │
│  │                                                                          │   │
│  │  SQL ID        | Digest                     | DB Load | Wait Events     │   │
│  │  ──────────────┼────────────────────────────┼─────────┼────────────────  │   │
│  │  ab12cd34ef56  | SELECT * FROM orders...    | 2.3 AAS | CPU: 1.5        │   │
│  │  12ab34cd56ef  | UPDATE inventory SET...    | 1.8 AAS | IO: 1.2         │   │
│  │  cd56ef78ab12  | INSERT INTO logs...        | 0.9 AAS | Lock: 0.5       │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  TOP WAIT EVENTS                                                         │   │
│  │                                                                          │   │
│  │  Event                        | DB Load | Description                    │   │
│  │  ────────────────────────────┼─────────┼──────────────────────────────  │   │
│  │  CPU                          | 3.2 AAS | Query processing               │   │
│  │  IO:DataFileRead              | 1.5 AAS | Reading data pages             │   │
│  │  LWLock:BufferContent         | 0.8 AAS | Buffer contention              │   │
│  │  Lock:transactionid           | 0.5 AAS | Transaction lock wait          │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Enable Performance Insights

```bash
# Enable on new instance
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    # ... other options

# Enable on existing instance
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --apply-immediately
```

### Performance Insights API

```bash
# Get database load
aws pi get-resource-metrics \
    --service-type RDS \
    --identifier db-ABCDEFGHIJKLMNOPQRSTUVWXYZ \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period-in-seconds 60 \
    --metric-queries '[{
        "Metric": "db.load.avg",
        "GroupBy": {
            "Group": "db.wait_event"
        }
    }]'

# Get top SQL
aws pi describe-dimension-keys \
    --service-type RDS \
    --identifier db-ABCDEFGHIJKLMNOPQRSTUVWXYZ \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --metric "db.load.avg" \
    --group-by '{"Group": "db.sql"}'
```

### Key Performance Insights Metrics

| Metric | Description |
|--------|-------------|
| **db.load.avg** | Average active sessions |
| **db.SQL.avg** | Database load by SQL statement |
| **db.Wait.avg** | Database load by wait event |
| **db.User.avg** | Database load by user |
| **db.Host.avg** | Database load by host |

### Wait Event Categories

| Category | Example Events | Indicates |
|----------|----------------|-----------|
| **CPU** | CPU | Query processing overhead |
| **IO** | IO:DataFileRead, IO:DataFileWrite | Storage I/O |
| **Lock** | Lock:transactionid, Lock:tuple | Concurrency issues |
| **LWLock** | LWLock:BufferContent | Internal locking |
| **IPC** | IPC:MultixactOffsetBuffer | Inter-process communication |

## Database Logs

### Available Log Types

| Engine | Log Types |
|--------|-----------|
| MySQL | error, general, slowquery, audit |
| PostgreSQL | postgresql |
| MariaDB | error, general, slowquery, audit |
| Oracle | alert, audit, listener, trace |
| SQL Server | agent, error |

### Enable Log Publishing to CloudWatch

```bash
# Enable log exports
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --cloudwatch-logs-export-configuration '{
        "EnableLogTypes": ["error", "slowquery", "general"]
    }' \
    --apply-immediately
```

### Configure Slow Query Log (MySQL)

```sql
-- Parameter group settings
slow_query_log = 1
long_query_time = 2
log_queries_not_using_indexes = 1
log_slow_admin_statements = 1
min_examined_row_limit = 1000
```

```bash
# View slow query log
aws rds download-db-log-file-portion \
    --db-instance-identifier mydb \
    --log-file-name slowquery/mysql-slowquery.log \
    --output text

# View error log
aws rds download-db-log-file-portion \
    --db-instance-identifier mydb \
    --log-file-name error/mysql-error.log \
    --output text
```

### Query CloudWatch Logs

```bash
# Search slow query logs
aws logs filter-log-events \
    --log-group-name /aws/rds/instance/mydb/slowquery \
    --start-time $(date -d '1 hour ago' +%s000) \
    --filter-pattern "Query_time"

# Search for specific error
aws logs filter-log-events \
    --log-group-name /aws/rds/instance/mydb/error \
    --filter-pattern "ERROR"
```

### Log Insights Queries

```sql
-- Find slowest queries
fields @timestamp, @message
| filter @message like /Query_time/
| parse @message "Query_time: * Lock_time: * Rows_sent: * Rows_examined: *" as query_time, lock_time, rows_sent, rows_examined
| sort query_time desc
| limit 20

-- Count queries by hour
fields @timestamp
| stats count(*) as query_count by bin(1h)
| sort @timestamp desc

-- Find connection errors
fields @timestamp, @message
| filter @message like /connect|connection/i
| filter @message like /error|failed|refused/i
| sort @timestamp desc
| limit 50
```

## Monitoring Queries

### MySQL Monitoring Queries

```sql
-- Current connections
SHOW PROCESSLIST;

-- Connection summary
SELECT
    user,
    host,
    db,
    command,
    time,
    state,
    info
FROM information_schema.processlist
WHERE command != 'Sleep'
ORDER BY time DESC;

-- InnoDB status
SHOW ENGINE INNODB STATUS\G

-- Table lock waits
SELECT
    r.trx_id AS waiting_trx_id,
    r.trx_mysql_thread_id AS waiting_thread,
    r.trx_query AS waiting_query,
    b.trx_id AS blocking_trx_id,
    b.trx_mysql_thread_id AS blocking_thread,
    b.trx_query AS blocking_query
FROM information_schema.innodb_lock_waits w
JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id
JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;

-- Query performance
SELECT
    digest_text,
    count_star AS executions,
    avg_timer_wait/1000000000000 AS avg_latency_sec,
    sum_rows_examined/count_star AS avg_rows_examined
FROM performance_schema.events_statements_summary_by_digest
ORDER BY avg_timer_wait DESC
LIMIT 10;
```

### PostgreSQL Monitoring Queries

```sql
-- Active connections
SELECT
    pid,
    usename,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- Connection summary
SELECT
    state,
    count(*)
FROM pg_stat_activity
GROUP BY state;

-- Long-running queries
SELECT
    pid,
    now() - query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;

-- Table statistics
SELECT
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Blocking queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

## Monitoring Best Practices

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPUUtilization | > 70% | > 85% | Scale up or optimize queries |
| FreeableMemory | < 25% | < 10% | Scale up instance |
| FreeStorageSpace | < 20% | < 10% | Enable autoscaling or increase |
| DatabaseConnections | > 80% max | > 90% max | Connection pooling |
| ReadLatency | > 10ms | > 20ms | Check IOPS, storage type |
| WriteLatency | > 10ms | > 20ms | Check IOPS, storage type |
| ReplicaLag | > 30s | > 60s | Check replica performance |
| SwapUsage | > 0 | > 100MB | Scale up instance |
| DiskQueueDepth | > 1 avg | > 5 avg | Increase IOPS |

### Monitoring Checklist

```
DAILY MONITORING
□ Check CPU utilization trends
□ Review database connections
□ Check storage space
□ Review slow query logs
□ Check replica lag (if applicable)

WEEKLY MONITORING
□ Analyze Performance Insights data
□ Review top SQL queries
□ Check for index optimization opportunities
□ Review error logs
□ Validate backup completion

MONTHLY MONITORING
□ Capacity planning review
□ Performance trend analysis
□ Cost optimization review
□ Security audit review
□ Test backup restoration
```

## Summary

- **CloudWatch Metrics** provide standard database metrics with 1-minute granularity
- **Enhanced Monitoring** provides OS-level metrics with up to 1-second granularity
- **Performance Insights** visualizes database load and identifies bottlenecks
- **Database Logs** can be exported to CloudWatch for analysis
- Set up appropriate alarms for proactive monitoring
- Use CloudWatch Logs Insights for log analysis

---

**Next:** [07 - Aurora](./07-aurora.md)

**Previous:** [05 - RDS Backup and Restore](./05-rds-backup-restore.md)
