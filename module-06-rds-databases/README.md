# Module 06: AWS Databases - RDS, Aurora, DynamoDB, and ElastiCache

## Module Overview

This comprehensive module covers AWS database services, focusing on relational databases (RDS, Aurora), NoSQL databases (DynamoDB), and in-memory caching solutions (ElastiCache). You will learn how to design, deploy, secure, and optimize database solutions on AWS.

## Why AWS Managed Databases?

AWS offers fully managed database services that handle the heavy lifting of database administration, including:
- Hardware provisioning and setup
- Patching and software updates
- Backups and point-in-time recovery
- High availability and failover
- Monitoring and metrics
- Scaling (vertical and horizontal)

## Database Options on AWS

| Service | Type | Use Case | Key Features |
|---------|------|----------|--------------|
| **Amazon RDS** | Relational | Traditional applications, OLTP | Multi-AZ, Read Replicas, 6 engines |
| **Amazon Aurora** | Relational | High-performance, cloud-native | 5x MySQL, 3x PostgreSQL performance |
| **Amazon DynamoDB** | NoSQL (Key-Value/Document) | Serverless, high-scale apps | Single-digit ms latency, unlimited scale |
| **Amazon ElastiCache** | In-Memory Cache | Session stores, real-time analytics | Redis or Memcached, sub-ms latency |
| **Amazon Neptune** | Graph | Social networks, fraud detection | SPARQL, Gremlin support |
| **Amazon DocumentDB** | Document | MongoDB workloads | MongoDB compatible |
| **Amazon Keyspaces** | Wide Column | Cassandra workloads | Cassandra compatible |
| **Amazon Timestream** | Time Series | IoT, DevOps metrics | Built-in time series functions |
| **Amazon QLDB** | Ledger | Audit trails, supply chain | Immutable, cryptographically verifiable |
| **Amazon MemoryDB** | In-Memory | Redis-compatible, durable | Ultra-fast with durability |

## Database Selection Decision Matrix

```
START
  |
  v
Is your data relational? ----YES----> Do you need cloud-native performance?
  |                                      |
  NO                                   YES --> Aurora
  |                                      |
  v                                    NO --> RDS
Do you need flexible schema?
  |
YES --> DynamoDB (key-value/document)
  |
  NO
  |
  v
Is it graph data? --------YES--------> Neptune
  |
  NO
  |
  v
Is it time-series data? --YES--------> Timestream
  |
  NO
  |
  v
Need caching layer? ------YES--------> ElastiCache (Redis/Memcached)
  |
  NO
  |
  v
Need audit/ledger? -------YES--------> QLDB
```

## Learning Objectives

By the end of this module, you will be able to:

### RDS and Aurora
- [ ] Explain the differences between self-managed and AWS-managed databases
- [ ] Create and configure RDS instances with appropriate instance classes and storage
- [ ] Implement Multi-AZ deployments for high availability
- [ ] Configure read replicas for read scaling and disaster recovery
- [ ] Apply security best practices including encryption and network isolation
- [ ] Set up automated backups and perform point-in-time recovery
- [ ] Monitor database performance using CloudWatch and Performance Insights
- [ ] Understand Aurora architecture and its advantages over standard RDS

### DynamoDB
- [ ] Design DynamoDB tables with appropriate partition and sort keys
- [ ] Choose between provisioned and on-demand capacity modes
- [ ] Create and use Global Secondary Indexes (GSI) and Local Secondary Indexes (LSI)
- [ ] Implement DynamoDB Streams for event-driven architectures
- [ ] Use DynamoDB transactions for ACID compliance
- [ ] Configure DAX for microsecond read latency

### ElastiCache
- [ ] Choose between Redis and Memcached for your use case
- [ ] Implement caching strategies (lazy loading, write-through)
- [ ] Configure ElastiCache clusters for high availability

### Database Migration
- [ ] Plan and execute database migrations using AWS DMS
- [ ] Use Schema Conversion Tool for heterogeneous migrations
- [ ] Understand different migration strategies (one-time, CDC)

## Module Structure

| File | Topic | Duration |
|------|-------|----------|
| 01-rds-fundamentals.md | RDS Overview and Engine Options | 45 min |
| 02-rds-instance-setup.md | Creating and Configuring RDS | 60 min |
| 03-rds-high-availability.md | Multi-AZ and Read Replicas | 45 min |
| 04-rds-security.md | Security Best Practices | 45 min |
| 05-rds-backup-restore.md | Backup and Recovery | 30 min |
| 06-rds-monitoring.md | Monitoring and Performance | 45 min |
| 07-aurora.md | Amazon Aurora Deep Dive | 60 min |
| 08-dynamodb.md | DynamoDB Fundamentals | 60 min |
| 09-dynamodb-advanced.md | Advanced DynamoDB Features | 60 min |
| 10-elasticache.md | ElastiCache Redis and Memcached | 45 min |
| 11-database-migration.md | AWS DMS and Migration | 45 min |
| 12-hands-on-labs.md | Practical Labs (7 exercises) | 180 min |
| quiz.md | Assessment (25 questions) | 30 min |

**Total Estimated Time: 12+ hours**

## Prerequisites

Before starting this module, you should have:
- Completed Module 01-05 (Core AWS Services)
- Basic understanding of SQL and database concepts
- Familiarity with VPCs and security groups
- AWS account with appropriate permissions
- AWS CLI configured on your local machine

## Cost Considerations

This module involves creating database instances that incur costs. Estimated costs for hands-on labs:

| Resource | Approximate Cost |
|----------|------------------|
| RDS db.t3.micro (Free Tier eligible) | $0.00 - $12/month |
| Aurora Serverless v2 (0.5 ACU) | ~$0.06/hour |
| DynamoDB (On-Demand, light usage) | < $1/month |
| ElastiCache cache.t3.micro | ~$0.017/hour |
| DMS replication instance | ~$0.018/hour |

**Tip:** Always delete resources after completing labs to avoid ongoing charges.

## Key AWS Services Covered

- Amazon RDS (Relational Database Service)
- Amazon Aurora
- Amazon DynamoDB
- Amazon ElastiCache
- AWS Database Migration Service (DMS)
- AWS Schema Conversion Tool (SCT)
- RDS Proxy
- DynamoDB Accelerator (DAX)

## Additional Resources

- [AWS Database Services Overview](https://aws.amazon.com/products/databases/)
- [Amazon RDS User Guide](https://docs.aws.amazon.com/rds/)
- [Amazon Aurora User Guide](https://docs.aws.amazon.com/aurora/)
- [Amazon DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [Amazon ElastiCache User Guide](https://docs.aws.amazon.com/elasticache/)
- [AWS Database Blog](https://aws.amazon.com/blogs/database/)
- [AWS re:Invent Database Sessions](https://www.youtube.com/results?search_query=aws+reinvent+databases)

---

**Next:** [01 - RDS Fundamentals](./01-rds-fundamentals.md)
