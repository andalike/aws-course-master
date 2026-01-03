# Module 06 - RDS and Databases Quiz

## Overview

This comprehensive quiz covers all topics in Module 06, including RDS fundamentals, Aurora, DynamoDB, ElastiCache, and database migration. Test your knowledge with 30 questions ranging from basic concepts to advanced scenarios.

**Time Estimate:** 45 minutes
**Passing Score:** 80% (24/30)

---

## Section 1: RDS Fundamentals (Questions 1-6)

### Question 1
Which of the following database engines are supported by Amazon RDS? (Select THREE)

A. MySQL
B. MongoDB
C. PostgreSQL
D. Cassandra
E. Oracle
F. Redis

<details>
<summary>Click for Answer</summary>

**Answer: A, C, E**

**Explanation:** Amazon RDS supports six relational database engines:
- MySQL
- PostgreSQL
- MariaDB
- Oracle
- Microsoft SQL Server
- Amazon Aurora (MySQL/PostgreSQL compatible)

MongoDB, Cassandra, and Redis are not relational databases. MongoDB workloads can use Amazon DocumentDB, Cassandra workloads can use Amazon Keyspaces, and Redis is available through Amazon ElastiCache.
</details>

---

### Question 2
What is the primary advantage of using Amazon RDS over running a database on EC2?

A. RDS provides SSH access to the database server
B. RDS is always less expensive than EC2-hosted databases
C. RDS handles operational tasks like patching, backups, and failover
D. RDS supports more database engines than EC2

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** The primary advantage of RDS is that AWS manages operational tasks including:
- Hardware provisioning
- Database setup and patching
- Automated backups
- High availability (Multi-AZ)
- Automatic failover
- Monitoring and metrics

RDS does NOT provide SSH access (you cannot access the underlying OS). While RDS can be cost-effective, it's not always cheaper than EC2. EC2 can run any database software, so it actually supports more engines than RDS.
</details>

---

### Question 3
Which RDS instance class family is best suited for memory-intensive database workloads?

A. T3 (Burstable)
B. M6g (Standard)
C. R6g (Memory Optimized)
D. C6g (Compute Optimized)

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** RDS instance class families:
- **R classes (r6g, r6i, r5)**: Memory Optimized - High memory-to-CPU ratio, ideal for memory-intensive database workloads
- **M classes (m6g, m6i, m5)**: Standard - Balanced compute, memory, and networking
- **T classes (t3, t4g)**: Burstable - Variable workloads, cost-effective for dev/test
- **C classes**: Not available for RDS (Compute Optimized is for CPU-intensive workloads)

For memory-intensive workloads like large databases, analytics, or caching layers, use R-class instances.
</details>

---

### Question 4
What is the maximum storage size for an Amazon RDS instance using gp3 storage?

A. 16 TB
B. 32 TB
C. 64 TB
D. 128 TB

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** Amazon RDS storage limits:
- **gp2/gp3 (General Purpose SSD)**: Up to 64 TB (except SQL Server: 16 TB)
- **io1/io2 (Provisioned IOPS SSD)**: Up to 64 TB (except SQL Server: 16 TB)
- **Aurora**: Up to 128 TB (auto-scaling)
- **Magnetic**: Up to 3 TB (legacy, not recommended)

Note: SQL Server has a lower maximum of 16 TB due to engine limitations.
</details>

---

### Question 5
A company wants to modify database engine parameters without affecting other RDS instances. What should they use?

A. DB Option Group
B. DB Parameter Group
C. DB Subnet Group
D. DB Security Group

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** RDS configuration groups:
- **DB Parameter Group**: Contains engine configuration parameters (e.g., max_connections, innodb_buffer_pool_size). Create a custom parameter group to modify settings without affecting other instances.
- **DB Option Group**: Enables additional database features (e.g., Oracle APEX, SQL Server native backup)
- **DB Subnet Group**: Defines which VPC subnets can be used for the database
- **Security Group**: Controls network access (not an RDS-specific concept)

To change engine parameters, create a custom DB Parameter Group and associate it with your instance.
</details>

---

### Question 6
Which storage type should you choose for an RDS instance that requires consistent, high IOPS performance?

A. gp2 (General Purpose SSD)
B. gp3 (General Purpose SSD)
C. io1 (Provisioned IOPS SSD)
D. Standard (Magnetic)

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** RDS storage types comparison:
- **io1/io2 (Provisioned IOPS)**: Consistent, high-performance I/O. You specify exact IOPS (up to 256,000). Best for I/O-intensive workloads requiring predictable performance.
- **gp3**: Good baseline performance (3,000 IOPS), can provision up to 16,000 IOPS. Cost-effective for most workloads.
- **gp2**: IOPS scales with storage size (3 IOPS per GB). Burst capability but not consistent for sustained high IOPS.
- **Magnetic**: Legacy, lowest cost, lowest performance.

For consistent, high IOPS requirements, Provisioned IOPS (io1/io2) is the correct choice.
</details>

---

## Section 2: Multi-AZ and Read Replicas (Questions 7-12)

### Question 7
What type of replication is used for RDS Multi-AZ deployments?

A. Asynchronous replication
B. Synchronous replication
C. Semi-synchronous replication
D. Logical replication

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:**
- **Multi-AZ uses synchronous replication**: Every write to the primary is immediately replicated to the standby before the transaction is acknowledged. This ensures zero data loss (RPO = 0).
- **Read Replicas use asynchronous replication**: Writes are sent to replicas after being committed on the primary. There may be replica lag (seconds to minutes).

Multi-AZ is designed for high availability with automatic failover. The synchronous replication ensures the standby is always up-to-date.
</details>

---

### Question 8
During an RDS Multi-AZ failover, what happens to the database endpoint?

A. A new endpoint is created for the standby instance
B. The DNS endpoint automatically points to the new primary
C. You must manually update your application connection strings
D. The endpoint becomes unavailable until you create a new standby

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** Multi-AZ failover process:
1. AWS detects the primary instance failure
2. The standby is automatically promoted to primary
3. The DNS record (endpoint) is updated to point to the new primary
4. Application connections using the same endpoint are redirected
5. Failover typically completes in 60-120 seconds

No application changes are needed because the endpoint remains the same. Applications should implement connection retry logic to handle the brief interruption.
</details>

---

### Question 9
Which of the following scenarios will trigger an automatic Multi-AZ failover? (Select TWO)

A. A read replica fails
B. The primary AZ experiences an infrastructure failure
C. You manually reboot the primary with the "force failover" option
D. A user drops a table accidentally
E. The database runs out of storage space

<details>
<summary>Click for Answer</summary>

**Answer: B, C**

**Explanation:** Automatic Multi-AZ failover triggers:
- Primary instance failure
- Primary AZ failure (infrastructure failure)
- Loss of network connectivity to primary
- Primary storage failure
- Instance scaling operations
- OS/database engine patching
- Manual reboot with force failover option

Failover does NOT occur for:
- Read replica failures (replicas are independent)
- User errors (like dropping tables)
- Storage exhaustion (this causes the database to stop, but doesn't trigger failover)

For user errors, you would need to restore from a backup or use point-in-time recovery.
</details>

---

### Question 10
What is the primary purpose of RDS Read Replicas?

A. Automatic failover during primary failure
B. Horizontal scaling for read-heavy workloads
C. Geographic data isolation for compliance
D. Real-time data synchronization

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** Read Replica purposes:
- **Primary purpose**: Horizontal scaling for read-heavy workloads by offloading read traffic
- **Secondary purposes**:
  - Disaster recovery (can be promoted to standalone)
  - Reporting/analytics without impacting production
  - Cross-region read scaling

Read Replicas do NOT provide:
- Automatic failover (Multi-AZ does this)
- Synchronous replication (they use asynchronous)
- Write capability (read-only until promoted)

For automatic failover, use Multi-AZ. Read Replicas can be promoted manually if needed.
</details>

---

### Question 11
A company wants to deploy a disaster recovery solution where the replica database can be quickly promoted if the primary region fails. Which solution should they implement?

A. Multi-AZ deployment in the primary region
B. Cross-region Read Replica
C. Daily automated backups copied to another region
D. Aurora Global Database

<details>
<summary>Click for Answer</summary>

**Answer: B (or D for Aurora)**

**Explanation:** For cross-region disaster recovery:
- **Cross-region Read Replica**: Can be promoted to a standalone database if the primary region fails. RPO is minutes (due to async replication), RTO is minutes (promotion time).
- **Aurora Global Database**: Even better for Aurora - provides RPO < 1 second and RTO < 1 minute for cross-region failover.

Other options:
- Multi-AZ only provides HA within a single region
- Backup copies have higher RPO (last backup) and higher RTO (restore time)

For RDS (non-Aurora), cross-region Read Replica is the best DR solution. For Aurora, use Global Database.
</details>

---

### Question 12
How many Read Replicas can you create for an RDS MySQL instance?

A. 5
B. 10
C. 15
D. Unlimited

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** Maximum Read Replicas per RDS instance:
- MySQL: 15 replicas
- PostgreSQL: 15 replicas
- MariaDB: 15 replicas
- Oracle: 5 replicas
- SQL Server: 5 replicas
- Aurora: 15 replicas (using shared storage)

Note: Each Read Replica can also have its own Read Replicas (up to 4 levels of chaining for MySQL/MariaDB).
</details>

---

## Section 3: Aurora Architecture (Questions 13-17)

### Question 13
How does Aurora achieve its high availability and durability?

A. By storing data on a single highly reliable disk
B. By replicating data 6 times across 3 Availability Zones
C. By using Multi-AZ with synchronous replication
D. By automatically creating backups every minute

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** Aurora storage architecture:
- Data is divided into 10 GB segments called "protection groups"
- Each segment is replicated 6 times across 3 AZs (2 copies per AZ)
- Writes require a quorum of 4 out of 6 copies
- Reads require a quorum of 3 out of 6 copies
- Can tolerate loss of 2 copies without losing write availability
- Can tolerate loss of 3 copies without losing read availability
- Self-healing storage automatically detects and repairs failures

This architecture is fundamentally different from standard RDS Multi-AZ and provides superior durability.
</details>

---

### Question 14
What is the maximum storage capacity of an Aurora database cluster?

A. 16 TB
B. 64 TB
C. 128 TB
D. 256 TB

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** Aurora storage characteristics:
- **Maximum size**: 128 TB
- **Auto-scaling**: Storage automatically grows in 10 GB increments
- **No pre-provisioning**: You don't need to specify storage size upfront
- **Pay for what you use**: Billed only for storage consumed
- **Storage is shared**: All instances in the cluster access the same storage

Compare to standard RDS: 64 TB maximum with manual scaling required.
</details>

---

### Question 15
What is the typical failover time for an Aurora database?

A. 60-120 seconds
B. 30-60 seconds
C. Less than 30 seconds
D. 5-10 minutes

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** Aurora failover times:
- **With existing replica**: Less than 30 seconds (typically 10-20 seconds)
- **Without replica (recreate primary)**: Longer, as new instance must be provisioned

Aurora achieves faster failover because:
- Storage is separate from compute (no data copying needed)
- Replicas use shared storage (already have data)
- DNS propagation is optimized

Compare to standard RDS Multi-AZ: 60-120 seconds for failover.

Best practice: Always maintain at least one Aurora Replica for fast failover.
</details>

---

### Question 16
Which Aurora endpoint should an application use for write operations?

A. Reader Endpoint
B. Cluster Endpoint (Writer Endpoint)
C. Instance Endpoint
D. Custom Endpoint

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** Aurora endpoint types:
- **Cluster Endpoint (Writer)**: Points to the current primary instance. Use for all write operations and reads requiring strong consistency.
- **Reader Endpoint**: Load balances across all read replicas. Use for read operations that can tolerate eventual consistency.
- **Instance Endpoint**: Direct connection to a specific instance. Use for troubleshooting or specific routing needs.
- **Custom Endpoint**: User-defined group of instances. Use for routing specific workloads (e.g., analytics queries to larger instances).

Always use the Cluster Endpoint for writes to ensure automatic failover handling.
</details>

---

### Question 17
What is Aurora Serverless v2 best suited for?

A. Steady-state, predictable workloads
B. Variable workloads with unpredictable traffic patterns
C. Development environments only
D. Read-heavy workloads with no writes

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** Aurora Serverless v2 use cases:
- **Variable/unpredictable workloads**: Automatically scales capacity up and down
- **Infrequently used applications**: Scales to minimum when idle
- **Development and test databases**: Cost-effective for intermittent use
- **Multi-tenant applications**: Each tenant's load varies independently
- **New applications**: When you don't know capacity requirements

Aurora Serverless v2 features:
- Scales in increments of 0.5 ACUs (Aurora Capacity Units)
- Scales instantly (no warmup time)
- Can scale from 0.5 to 128 ACUs
- Supports all Aurora features (Global Database, Multi-AZ, etc.)

For steady, predictable workloads, provisioned Aurora is more cost-effective.
</details>

---

## Section 4: RDS Proxy and Security (Questions 18-20)

### Question 18
What is the primary benefit of using RDS Proxy?

A. Encrypts database traffic automatically
B. Manages database connection pooling and reduces failover time
C. Provides read scaling across multiple regions
D. Automatically backs up databases more frequently

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** RDS Proxy benefits:
- **Connection pooling**: Shares and reuses database connections, reducing connection overhead
- **Reduced failover time**: Maintains connections during failover, reducing impact from 60+ seconds to near-zero
- **Improved scalability**: Handles many application connections with fewer database connections
- **Lambda integration**: Ideal for serverless applications that create many short-lived connections
- **IAM authentication**: Enforces IAM-based authentication to the database

RDS Proxy is especially useful for:
- Applications with many short-lived connections (like Lambda)
- Applications that open/close connections frequently
- Reducing failover disruption
</details>

---

### Question 19
Which authentication methods are supported for RDS databases? (Select TWO)

A. Native database authentication (username/password)
B. IAM database authentication
C. SAML 2.0 federation
D. Active Directory (for supported engines)
E. OAuth 2.0

<details>
<summary>Click for Answer</summary>

**Answer: A, B, D**

**Explanation:** RDS authentication methods:
- **Native database authentication**: Traditional username/password stored in the database
- **IAM database authentication**: Use IAM credentials to generate authentication tokens (MySQL, PostgreSQL, MariaDB, Aurora)
- **Kerberos/Active Directory**: Supported for SQL Server, Oracle, PostgreSQL, MySQL

SAML 2.0 and OAuth 2.0 are not directly supported for RDS authentication.

IAM authentication benefits:
- Credentials managed by IAM (rotation, policies)
- No need to store passwords in application
- Authentication token valid for 15 minutes
- Network traffic encrypted with SSL
</details>

---

### Question 20
How can you encrypt an existing unencrypted RDS database?

A. Enable encryption on the existing instance
B. Create an encrypted snapshot and restore to a new encrypted instance
C. Use AWS KMS to encrypt the instance in place
D. Encryption cannot be added to existing databases

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** RDS encryption rules:
- Encryption must be enabled at instance creation time
- You cannot encrypt an existing unencrypted instance
- You cannot decrypt an encrypted instance

To encrypt an existing unencrypted database:
1. Create a snapshot of the unencrypted instance
2. Copy the snapshot and enable encryption during the copy
3. Restore the encrypted snapshot to a new RDS instance
4. Update application connection strings to the new instance
5. Delete the old unencrypted instance

Note: This requires downtime for the cutover to the new instance.
</details>

---

## Section 5: DynamoDB (Questions 21-24)

### Question 21
What type of primary key requires both a partition key and a sort key?

A. Simple primary key
B. Composite primary key
C. Secondary key
D. Global key

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** DynamoDB primary key types:
- **Simple primary key (Partition Key only)**: Single attribute that uniquely identifies each item. Example: UserID
- **Composite primary key (Partition Key + Sort Key)**: Two attributes that together uniquely identify each item. Example: UserID (partition) + OrderDate (sort)

With a composite key:
- Partition key determines the physical partition
- Sort key orders items within the partition
- Enables range queries on the sort key
- Multiple items can share the same partition key (with different sort keys)
</details>

---

### Question 22
A company needs to query a DynamoDB table by an attribute that is not the primary key. What should they create?

A. Read Replica
B. Local Secondary Index (LSI)
C. Global Secondary Index (GSI)
D. Partition key alias

<details>
<summary>Click for Answer</summary>

**Answer: C (or B depending on requirements)**

**Explanation:** DynamoDB secondary indexes:
- **Global Secondary Index (GSI)**:
  - Can use any attribute as partition key and sort key
  - Can be created at any time
  - Has its own provisioned throughput
  - Eventually consistent reads only
  - Up to 20 GSIs per table

- **Local Secondary Index (LSI)**:
  - Must use same partition key as the table
  - Uses different sort key
  - Must be created at table creation time
  - Shares throughput with the table
  - Supports strongly consistent reads
  - Up to 5 LSIs per table

For querying by a completely different attribute, use a GSI. For querying with the same partition key but different sort, use an LSI.
</details>

---

### Question 23
What capacity mode should you choose for a DynamoDB table with unpredictable traffic patterns?

A. Provisioned capacity
B. On-demand capacity
C. Reserved capacity
D. Burst capacity

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** DynamoDB capacity modes:
- **On-demand capacity**:
  - Automatically scales to handle traffic
  - Pay per request (read/write)
  - No capacity planning required
  - Best for unpredictable or spiky workloads
  - Instantly handles sudden traffic spikes

- **Provisioned capacity**:
  - You specify RCUs (Read Capacity Units) and WCUs (Write Capacity Units)
  - Auto-scaling available but has limits
  - More cost-effective for predictable workloads
  - Can use reserved capacity for additional savings

For unpredictable traffic, on-demand mode eliminates throttling risk and capacity planning overhead.
</details>

---

### Question 24
What feature allows you to capture changes to DynamoDB items in near real-time?

A. DynamoDB Accelerator (DAX)
B. DynamoDB Streams
C. DynamoDB Triggers
D. DynamoDB Replication

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** DynamoDB Streams:
- Captures item-level changes (insert, update, delete) in near real-time
- Stores changes for 24 hours
- Ordered stream of changes per partition key
- Can trigger Lambda functions for event-driven processing
- Use cases: replication, analytics, notifications, audit logs

Stream record views:
- KEYS_ONLY: Only the key attributes
- NEW_IMAGE: The entire item after the change
- OLD_IMAGE: The entire item before the change
- NEW_AND_OLD_IMAGES: Both before and after

DAX is for caching, not change capture.
</details>

---

## Section 6: ElastiCache (Questions 25-27)

### Question 25
Which ElastiCache engine supports data persistence and replication?

A. Memcached only
B. Redis only
C. Both Redis and Memcached
D. Neither Redis nor Memcached

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** ElastiCache engine comparison:

**Redis**:
- Data persistence (snapshots, AOF)
- Replication (primary-replica)
- Multi-AZ with automatic failover
- Complex data types (lists, sets, sorted sets, hashes)
- Pub/Sub messaging
- Lua scripting
- Geospatial support

**Memcached**:
- Simple key-value cache
- Multi-threaded (better for simple caching)
- No persistence
- No replication
- Horizontal scaling with sharding

Choose Redis when you need persistence, replication, complex data types, or pub/sub. Choose Memcached for simple, multi-threaded caching.
</details>

---

### Question 26
What caching strategy writes data to the cache and database simultaneously?

A. Lazy Loading
B. Write-Through
C. Write-Behind
D. Cache-Aside

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** Caching strategies:

**Write-Through**:
- Write to cache AND database together
- Data in cache is always current
- Higher write latency (two writes)
- Prevents stale data

**Lazy Loading (Cache-Aside)**:
- Read: Check cache, if miss, read from DB and update cache
- Write: Write to DB only
- Pros: Only requested data is cached
- Cons: Cache miss penalty, potential stale data

**Write-Behind (Write-Back)**:
- Write to cache immediately
- Asynchronously write to database later
- Lower write latency
- Risk of data loss if cache fails

**TTL (Time to Live)**: Combined with lazy loading to expire stale data.
</details>

---

### Question 27
An application requires sub-millisecond latency for frequently accessed data. Which AWS service is most appropriate?

A. Amazon RDS with read replicas
B. Amazon DynamoDB
C. Amazon ElastiCache
D. Amazon S3

<details>
<summary>Click for Answer</summary>

**Answer: C**

**Explanation:** Latency comparison:
- **ElastiCache (Redis/Memcached)**: Sub-millisecond (microseconds for simple operations)
- **DynamoDB**: Single-digit milliseconds
- **DynamoDB with DAX**: Microseconds (in-memory cache for DynamoDB)
- **RDS**: Milliseconds to tens of milliseconds
- **S3**: Tens to hundreds of milliseconds

For sub-millisecond latency requirements, in-memory caching with ElastiCache is the appropriate choice. It's ideal for:
- Session stores
- Real-time leaderboards
- Frequently accessed database queries
- API response caching
</details>

---

## Section 7: Database Migration (Questions 28-30)

### Question 28
What AWS service is used to migrate databases to AWS with minimal downtime?

A. AWS DataSync
B. AWS Database Migration Service (DMS)
C. AWS Snowball
D. AWS Transfer Family

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** AWS Database Migration Service (DMS):
- Migrates databases to AWS quickly and securely
- Source database remains operational during migration
- Supports homogeneous migrations (Oracle to Oracle)
- Supports heterogeneous migrations (Oracle to PostgreSQL)
- Continuous data replication (CDC) for minimal downtime
- Supports various source/target combinations

Other services:
- DataSync: File/object storage transfer
- Snowball: Large-scale data transfer
- Transfer Family: SFTP/FTPS/FTP to S3

For database migrations, DMS is the purpose-built solution.
</details>

---

### Question 29
When migrating from Oracle to PostgreSQL, which AWS tool helps convert the database schema?

A. AWS DMS
B. AWS Schema Conversion Tool (SCT)
C. AWS Glue
D. Amazon Athena

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** AWS Schema Conversion Tool (SCT):
- Converts database schemas between different database engines
- Handles stored procedures, functions, and views
- Identifies conversion issues and provides guidance
- Generates migration assessment reports
- Works with DMS for heterogeneous migrations

Migration workflow:
1. SCT converts schema (DDL, stored procedures)
2. SCT assessment report highlights manual conversion needs
3. Apply converted schema to target database
4. DMS migrates the data
5. DMS provides ongoing replication until cutover

DMS migrates data; SCT converts schema for heterogeneous migrations.
</details>

---

### Question 30
What type of replication does AWS DMS use for ongoing data synchronization during migration?

A. Synchronous replication
B. Change Data Capture (CDC)
C. Snapshot replication
D. Log shipping

<details>
<summary>Click for Answer</summary>

**Answer: B**

**Explanation:** AWS DMS replication types:
- **Full Load**: Initial bulk data migration (one-time copy)
- **Change Data Capture (CDC)**: Captures ongoing changes after full load
- **Full Load + CDC**: Combines both for minimal downtime migration

CDC captures:
- Inserts, updates, and deletes from source
- Applies changes to target in near real-time
- Uses database transaction logs (not triggers)
- Enables cutover with minimal data loss

Migration pattern:
1. Start full load migration
2. Enable CDC to capture changes during migration
3. Continue CDC until ready for cutover
4. Brief cutover window to switch applications
5. Verify data and complete migration
</details>

---

## Scoring Guide

| Score | Grade | Feedback |
|-------|-------|----------|
| 27-30 | A (90-100%) | Excellent! You have mastery of AWS database services. |
| 24-26 | B (80-86%) | Good job! You passed and understand the core concepts. |
| 21-23 | C (70-76%) | Review the areas where you struggled before proceeding. |
| 18-20 | D (60-66%) | More study needed. Review all sections and try again. |
| Below 18 | F (<60%) | Please review the module content thoroughly. |

---

## Answer Key Quick Reference

| Question | Answer | Question | Answer |
|----------|--------|----------|--------|
| 1 | A, C, E | 16 | B |
| 2 | C | 17 | B |
| 3 | C | 18 | B |
| 4 | C | 19 | A, B, D |
| 5 | B | 20 | B |
| 6 | C | 21 | B |
| 7 | B | 22 | C |
| 8 | B | 23 | B |
| 9 | B, C | 24 | B |
| 10 | B | 25 | B |
| 11 | B | 26 | B |
| 12 | C | 27 | C |
| 13 | B | 28 | B |
| 14 | C | 29 | B |
| 15 | C | 30 | B |

---

## Topics for Further Study

If you struggled with specific sections, review these resources:

- **RDS Fundamentals**: 01-rds-fundamentals.md, 02-rds-instance-setup.md
- **Multi-AZ/Read Replicas**: 03-rds-high-availability.md
- **Aurora**: 07-aurora.md
- **Security**: 04-rds-security.md
- **DynamoDB**: 08-dynamodb.md
- **ElastiCache**: 09-elasticache.md
- **Migration**: 10-database-migration.md

---

**Next:** [11 - Hands-on Lab](./11-hands-on-lab.md)

**Previous:** [10 - Database Migration](./10-database-migration.md)
