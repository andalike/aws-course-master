# 05 - RDS Backup and Restore

## Backup Overview

Amazon RDS provides multiple backup mechanisms to protect your data:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          RDS BACKUP OPTIONS                                     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     AUTOMATED BACKUPS                                    │   │
│  │                                                                          │   │
│  │  ┌─────────────────────┐     ┌─────────────────────────────────────┐    │   │
│  │  │   Daily Snapshots   │     │   Transaction Logs (5-minute)       │    │   │
│  │  │   (Backup Window)   │     │   (Continuous backup)               │    │   │
│  │  └─────────────────────┘     └─────────────────────────────────────┘    │   │
│  │                                                                          │   │
│  │  Features:                                                               │   │
│  │  ├── Automatic, no manual intervention required                         │   │
│  │  ├── Retention: 0-35 days (0 = disabled)                               │   │
│  │  ├── Point-in-time recovery (PITR) supported                           │   │
│  │  ├── Stored in S3 (managed by AWS)                                     │   │
│  │  └── Deleted when RDS instance is deleted (unless snapshot taken)      │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     MANUAL SNAPSHOTS                                     │   │
│  │                                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │   User-initiated at any time                                    │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                          │   │
│  │  Features:                                                               │   │
│  │  ├── Manual trigger (CLI, Console, API)                                 │   │
│  │  ├── No retention limit (persist until deleted)                         │   │
│  │  ├── Can be shared with other AWS accounts                              │   │
│  │  ├── Can be copied to other regions                                     │   │
│  │  └── Persist after RDS instance deletion                                │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Automated Backups

### How Automated Backups Work

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      AUTOMATED BACKUP TIMELINE                                  │
│                                                                                 │
│  Day 1        Day 2        Day 3        Day 4        Day 5                     │
│    │            │            │            │            │                        │
│    ▼            ▼            ▼            ▼            ▼                        │
│  ┌────┐      ┌────┐      ┌────┐      ┌────┐      ┌────┐                        │
│  │ S1 │      │ S2 │      │ S3 │      │ S4 │      │ S5 │  Daily Snapshots      │
│  └────┘      └────┘      └────┘      └────┘      └────┘                        │
│    │            │            │            │            │                        │
│    └────────────┴────────────┴────────────┴────────────┘                        │
│                              │                                                   │
│                              │                                                   │
│    ┌──────────────────────────────────────────────────┐                        │
│    │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ Transaction Logs       │
│    │                                                   │ (Every 5 minutes)      │
│    └──────────────────────────────────────────────────┘                        │
│                                                                                 │
│                              │                                                   │
│                              ▼                                                   │
│                    Point-in-Time Recovery                                       │
│                    (Any second within retention period)                         │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Configuring Automated Backups

```bash
# Enable automated backups (7-day retention)
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --apply-immediately

# Disable automated backups (NOT recommended)
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --backup-retention-period 0 \
    --apply-immediately
```

### Backup Window Best Practices

| Consideration | Recommendation |
|---------------|----------------|
| Time Zone | Use UTC for consistency |
| Low Traffic Period | Schedule during lowest activity |
| Duration | Allow 30-60 minutes minimum |
| Multi-AZ | Backups from standby (less impact) |
| I/O Impact | May experience brief I/O suspension |

**Backup Window Format:** `hh:mm-hh:mm` (UTC)

Example: `03:00-04:00` = 3 AM to 4 AM UTC

### Automated Backup Storage

```
Backup Storage = Allocated Storage × (1 + Additional for logs)

Example:
- Allocated Storage: 100 GB
- Backup Retention: 7 days
- Storage for 7 daily snapshots: ~100 GB (incremental)
- Transaction logs: Variable (depends on write activity)
```

**Free Backup Storage:** Equal to your allocated storage (up to 100% of provisioned storage)

## Manual Snapshots

### Creating Manual Snapshots

```bash
# Create a manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier mydb \
    --db-snapshot-identifier mydb-snapshot-2024-01-15

# Create snapshot with tags
aws rds create-db-snapshot \
    --db-instance-identifier mydb \
    --db-snapshot-identifier mydb-before-migration \
    --tags Key=Purpose,Value=Pre-Migration Key=CreatedBy,Value=Admin
```

### Snapshot States

| State | Description |
|-------|-------------|
| creating | Snapshot is being created |
| available | Snapshot is ready for use |
| copying | Snapshot is being copied |
| deleting | Snapshot is being deleted |

### List Snapshots

```bash
# List all snapshots for an instance
aws rds describe-db-snapshots \
    --db-instance-identifier mydb \
    --query 'DBSnapshots[*].[DBSnapshotIdentifier,Status,SnapshotCreateTime,AllocatedStorage]' \
    --output table

# List automated snapshots
aws rds describe-db-snapshots \
    --db-instance-identifier mydb \
    --snapshot-type automated

# List manual snapshots
aws rds describe-db-snapshots \
    --db-instance-identifier mydb \
    --snapshot-type manual
```

### Delete Snapshots

```bash
# Delete a snapshot
aws rds delete-db-snapshot \
    --db-snapshot-identifier mydb-old-snapshot

# Delete multiple snapshots (use with caution)
aws rds describe-db-snapshots \
    --db-instance-identifier mydb \
    --snapshot-type manual \
    --query 'DBSnapshots[?SnapshotCreateTime<`2024-01-01`].DBSnapshotIdentifier' \
    --output text | xargs -n1 aws rds delete-db-snapshot --db-snapshot-identifier
```

## Point-in-Time Recovery (PITR)

### How PITR Works

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      POINT-IN-TIME RECOVERY                                     │
│                                                                                 │
│   Retention Period: 7 days                                                      │
│                                                                                 │
│   ├──────────────────────────────────────────────────────────────────────────┤ │
│   Day 1      Day 2      Day 3      Day 4      Day 5      Day 6      Day 7    │ │
│   │          │          │          │          │          │          │        │ │
│   ▼          ▼          ▼          ▼          ▼          ▼          ▼        │ │
│   S1 ─────── S2 ─────── S3 ─────── S4 ─────── S5 ─────── S6 ─────── S7      │ │
│   │          │          │          │          │          │          │        │ │
│   │          │          │    ▲     │          │          │          │        │ │
│   │          │          │    │     │          │          │          │        │ │
│   └──────────┴──────────┴────┼─────┴──────────┴──────────┴──────────┘        │ │
│                              │                                                │ │
│                     Restore Point                                             │ │
│                   (Any second here)                                           │ │
│                                                                               │ │
│   PITR Process:                                                               │ │
│   1. Find most recent snapshot before restore point                          │ │
│   2. Restore snapshot to new instance                                        │ │
│   3. Apply transaction logs up to restore point                              │ │
│   4. New instance available with data at exact restore point                 │ │
│                                                                               │ │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Perform Point-in-Time Recovery

```bash
# Find latest restorable time
aws rds describe-db-instances \
    --db-instance-identifier mydb \
    --query 'DBInstances[0].[LatestRestorableTime,EarliestRestorableTime]' \
    --output table

# Restore to specific point in time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mydb \
    --target-db-instance-identifier mydb-restored \
    --restore-time "2024-01-15T10:30:00Z" \
    --db-instance-class db.t3.medium \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name my-subnet-group

# Restore to latest restorable time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier mydb \
    --target-db-instance-identifier mydb-restored-latest \
    --use-latest-restorable-time \
    --db-instance-class db.t3.medium
```

### PITR Limitations

| Limitation | Description |
|------------|-------------|
| New Instance | Creates new instance (cannot overwrite existing) |
| Time Range | Within backup retention period only |
| Granularity | Up to 5 minutes behind current time |
| Configuration | Some settings not restored (security groups, parameter groups) |
| Read Replicas | Not automatically recreated |

## Restore from Snapshot

### Restore Process

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                         SNAPSHOT RESTORE PROCESS                                │
│                                                                                 │
│  ┌───────────────┐                                                             │
│  │   Snapshot    │                                                             │
│  │  (Available)  │                                                             │
│  └───────┬───────┘                                                             │
│          │                                                                      │
│          │  1. Initiate restore                                                │
│          ▼                                                                      │
│  ┌───────────────┐                                                             │
│  │  New RDS      │                                                             │
│  │  Instance     │  2. Instance created with 'creating' status                 │
│  │  (Creating)   │                                                             │
│  └───────┬───────┘                                                             │
│          │                                                                      │
│          │  3. Data restored from snapshot                                     │
│          ▼                                                                      │
│  ┌───────────────┐                                                             │
│  │  New RDS      │                                                             │
│  │  Instance     │  4. Instance available                                      │
│  │  (Available)  │                                                             │
│  └───────┬───────┘                                                             │
│          │                                                                      │
│          │  5. Update application connection strings                           │
│          ▼                                                                      │
│  ┌───────────────┐                                                             │
│  │  Application  │                                                             │
│  │  (Connected)  │  6. Verify data and application functionality              │
│  └───────────────┘                                                             │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Restore Commands

```bash
# Restore from snapshot (basic)
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-restored \
    --db-snapshot-identifier mydb-snapshot-2024-01-15

# Restore with specific configuration
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-restored \
    --db-snapshot-identifier mydb-snapshot-2024-01-15 \
    --db-instance-class db.r6g.large \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name my-subnet-group \
    --publicly-accessible false \
    --multi-az \
    --storage-type gp3 \
    --iops 3000

# Restore encrypted snapshot with different KMS key
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier mydb-restored \
    --db-snapshot-identifier mydb-snapshot-encrypted \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/new-key-id
```

### What's Restored vs Not Restored

| Restored | Not Restored (Must Configure) |
|----------|-------------------------------|
| Data and schema | Security groups |
| Engine and version | Parameter group (uses default) |
| Storage size | Option group (uses default) |
| Encryption status | DB subnet group |
| Master credentials | Multi-AZ setting |
| | Read replicas |
| | IAM roles |
| | CloudWatch alarms |

## Cross-Region Snapshot Copies

### Copy Snapshots Between Regions

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                     CROSS-REGION SNAPSHOT COPY                                  │
│                                                                                 │
│  ┌─────────────────────────────┐          ┌─────────────────────────────┐     │
│  │        US-EAST-1            │          │        EU-WEST-1            │     │
│  │                             │          │                             │     │
│  │  ┌───────────────────────┐  │          │  ┌───────────────────────┐  │     │
│  │  │      RDS Instance     │  │          │  │   Snapshot Copy       │  │     │
│  │  │                       │  │          │  │   (For DR)            │  │     │
│  │  └───────────┬───────────┘  │          │  └───────────────────────┘  │     │
│  │              │              │          │            ▲                │     │
│  │              ▼              │          │            │                │     │
│  │  ┌───────────────────────┐  │   Copy   │            │                │     │
│  │  │   Manual Snapshot     │──┼──────────┼────────────┘                │     │
│  │  │   (Source)            │  │ (Async)  │                             │     │
│  │  └───────────────────────┘  │          │  Uses separate KMS key     │     │
│  │                             │          │  in target region          │     │
│  └─────────────────────────────┘          └─────────────────────────────┘     │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Copy Snapshot Commands

```bash
# Copy snapshot to another region
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:mydb-snapshot \
    --target-db-snapshot-identifier mydb-snapshot-eu-copy \
    --source-region us-east-1 \
    --region eu-west-1 \
    --kms-key-id arn:aws:kms:eu-west-1:123456789012:key/target-region-key

# Copy with tags
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-1:123456789012:snapshot:mydb-snapshot \
    --target-db-snapshot-identifier mydb-snapshot-dr \
    --region eu-west-1 \
    --copy-tags \
    --tags Key=Purpose,Value=DisasterRecovery
```

### Automated Cross-Region Backup

Use AWS Backup for automated cross-region copies:

```json
{
  "Rules": [
    {
      "RuleName": "DailyBackupWithCrossRegionCopy",
      "TargetBackupVaultName": "Default",
      "ScheduleExpression": "cron(0 5 ? * * *)",
      "StartWindowMinutes": 60,
      "CompletionWindowMinutes": 120,
      "Lifecycle": {
        "DeleteAfterDays": 35
      },
      "CopyActions": [
        {
          "DestinationBackupVaultArn": "arn:aws:backup:eu-west-1:123456789012:backup-vault:DR-Vault",
          "Lifecycle": {
            "DeleteAfterDays": 35
          }
        }
      ]
    }
  ]
}
```

## Sharing Snapshots

### Share with Other AWS Accounts

```bash
# Share snapshot with another account
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier mydb-snapshot \
    --attribute-name restore \
    --values-to-add 987654321098

# Share with multiple accounts
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier mydb-snapshot \
    --attribute-name restore \
    --values-to-add 111111111111 222222222222

# Make snapshot public (NOT recommended for production)
aws rds modify-db-snapshot-attribute \
    --db-snapshot-identifier mydb-snapshot \
    --attribute-name restore \
    --values-to-add all

# View sharing settings
aws rds describe-db-snapshot-attributes \
    --db-snapshot-identifier mydb-snapshot
```

### Sharing Encrypted Snapshots

For encrypted snapshots, you must also share the KMS key:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Allow use of the key for decryption",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::987654321098:root"
            },
            "Action": [
                "kms:Decrypt",
                "kms:DescribeKey",
                "kms:CreateGrant"
            ],
            "Resource": "*"
        }
    ]
}
```

## Export Snapshots to S3

### Export Process

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      SNAPSHOT EXPORT TO S3                                      │
│                                                                                 │
│  ┌───────────────┐                                                             │
│  │   Snapshot    │                                                             │
│  │               │                                                             │
│  └───────┬───────┘                                                             │
│          │                                                                      │
│          │  Export Task                                                        │
│          ▼                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                              S3 BUCKET                                    │ │
│  │                                                                           │ │
│  │  export-task-id/                                                         │ │
│  │  ├── database-name/                                                      │ │
│  │  │   ├── table1/                                                         │ │
│  │  │   │   ├── part-00000.parquet                                         │ │
│  │  │   │   ├── part-00001.parquet                                         │ │
│  │  │   │   └── ...                                                        │ │
│  │  │   ├── table2/                                                         │ │
│  │  │   │   └── ...                                                        │ │
│  │  │   └── _export_info                                                   │ │
│  │  └── export_info/                                                        │ │
│  │      └── export_manifest.json                                            │ │
│  │                                                                           │ │
│  │  Format: Apache Parquet (compressed, columnar)                           │ │
│  │  Use with: Athena, Redshift, Spark, etc.                                 │ │
│  │                                                                           │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Export Commands

```bash
# Start export task
aws rds start-export-task \
    --export-task-identifier mydb-export-task \
    --source-arn arn:aws:rds:us-east-1:123456789012:snapshot:mydb-snapshot \
    --s3-bucket-name my-export-bucket \
    --s3-prefix exports/rds/ \
    --iam-role-arn arn:aws:iam::123456789012:role/RDSExportRole \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/export-key

# Export specific tables
aws rds start-export-task \
    --export-task-identifier mydb-partial-export \
    --source-arn arn:aws:rds:us-east-1:123456789012:snapshot:mydb-snapshot \
    --s3-bucket-name my-export-bucket \
    --iam-role-arn arn:aws:iam::123456789012:role/RDSExportRole \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/export-key \
    --export-only "mydb.users" "mydb.orders"

# Check export status
aws rds describe-export-tasks \
    --export-task-identifier mydb-export-task
```

### IAM Role for Export

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject*",
                "s3:GetBucketLocation",
                "s3:GetObject*",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-export-bucket",
                "arn:aws:s3:::my-export-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "arn:aws:kms:us-east-1:123456789012:key/export-key"
        }
    ]
}
```

## Backup Best Practices

### Backup Strategy

| Requirement | Solution |
|-------------|----------|
| Daily recovery point | Automated backups (7+ day retention) |
| Long-term retention | Manual snapshots (monthly/yearly) |
| Disaster recovery | Cross-region snapshot copies |
| Compliance/Audit | AWS Backup with vault lock |
| Data analytics | Export to S3 (Parquet format) |

### Recovery Time Estimates

| Scenario | Estimated Recovery Time |
|----------|-------------------------|
| Point-in-time recovery (100 GB) | 30-60 minutes |
| Snapshot restore (100 GB) | 20-40 minutes |
| Snapshot restore (1 TB) | 2-4 hours |
| Cross-region restore | Add 30-60 minutes for copy |

### Backup Testing Checklist

```
BACKUP TESTING PROCEDURE

□ Monthly Snapshot Restore Test
  1. Select recent snapshot
  2. Restore to test instance
  3. Verify data integrity
  4. Run application tests
  5. Document results
  6. Delete test instance

□ Quarterly PITR Test
  1. Note specific timestamp
  2. Perform PITR to that time
  3. Verify data matches expectations
  4. Document restore time
  5. Delete test instance

□ Annual DR Test
  1. Copy snapshot to DR region
  2. Restore in DR region
  3. Test full application stack
  4. Document RTO achieved
  5. Update DR runbook
```

## Summary

- **Automated backups** provide daily snapshots and transaction logs (0-35 day retention)
- **Manual snapshots** persist until deleted and can be shared
- **PITR** enables recovery to any second within retention period
- **Cross-region copies** support disaster recovery requirements
- **Export to S3** enables analytics on database data
- Test your backup and restore procedures regularly

---

**Next:** [06 - RDS Monitoring](./06-rds-monitoring.md)

**Previous:** [04 - RDS Security](./04-rds-security.md)
