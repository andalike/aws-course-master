# 04 - EC2 Storage Options

## Overview

EC2 instances can use several types of storage, each optimized for different use cases. Understanding these options is crucial for designing performant, cost-effective, and reliable architectures.

```
┌─────────────────────────────────────────────────────────────────┐
│                    EC2 Storage Options                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   EBS Volumes   │  │ Instance Store  │  │   EFS / FSx     │  │
│  │   (Persistent)  │  │  (Ephemeral)    │  │  (Shared/NFS)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    S3 (Object Storage)                   │    │
│  │                 (Via API, not block storage)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Amazon EBS (Elastic Block Store)

### What is EBS?

Amazon Elastic Block Store provides persistent block-level storage volumes for EC2 instances. EBS volumes are:
- Network-attached storage (not physically attached)
- Persist independently from instance lifecycle
- Can be attached/detached from instances
- Automatically replicated within an Availability Zone

### EBS Volume Types

#### General Purpose SSD (gp2 and gp3)

**gp3 (Latest Generation - Recommended)**

| Specification | gp3 |
|--------------|-----|
| Volume Size | 1 GB - 16 TB |
| Baseline IOPS | 3,000 IOPS (included) |
| Max IOPS | 16,000 IOPS |
| Baseline Throughput | 125 MB/s (included) |
| Max Throughput | 1,000 MB/s |
| Price (us-east-1) | $0.08/GB-month |
| Additional IOPS | $0.005/IOPS-month (above 3,000) |
| Additional Throughput | $0.04/MB/s-month (above 125) |

**gp2 (Previous Generation)**

| Specification | gp2 |
|--------------|-----|
| Volume Size | 1 GB - 16 TB |
| IOPS | 3 IOPS/GB (baseline), burst to 3,000 |
| Max IOPS | 16,000 IOPS |
| Throughput | Up to 250 MB/s |
| Price (us-east-1) | $0.10/GB-month |

**gp3 vs gp2 Comparison**

```
gp3 Advantages:
┌────────────────────────────────────────────────────────────┐
│  • 20% cheaper baseline price ($0.08 vs $0.10/GB)          │
│  • Predictable 3,000 IOPS regardless of size               │
│  • IOPS and throughput can be provisioned independently    │
│  • No burst credits to manage                               │
└────────────────────────────────────────────────────────────┘
```

#### Provisioned IOPS SSD (io1 and io2)

For I/O-intensive workloads requiring sustained IOPS performance.

**io2 Block Express (Highest Performance)**

| Specification | io2 Block Express |
|--------------|-------------------|
| Volume Size | 4 GB - 64 TB |
| Max IOPS | 256,000 IOPS |
| Max Throughput | 4,000 MB/s |
| IOPS:GB Ratio | 1,000:1 |
| Durability | 99.999% |
| Price | $0.125/GB-month + $0.065/IOPS-month |

**io2 Standard**

| Specification | io2 |
|--------------|-----|
| Volume Size | 4 GB - 16 TB |
| Max IOPS | 64,000 IOPS |
| Max Throughput | 1,000 MB/s |
| IOPS:GB Ratio | 500:1 |
| Durability | 99.999% |
| Price | $0.125/GB-month + $0.065/IOPS-month |

**io1 (Previous Generation)**

| Specification | io1 |
|--------------|-----|
| Volume Size | 4 GB - 16 TB |
| Max IOPS | 64,000 IOPS |
| IOPS:GB Ratio | 50:1 |
| Durability | 99.9% |
| Price | $0.125/GB-month + $0.065/IOPS-month |

#### Throughput Optimized HDD (st1)

For frequently accessed, throughput-intensive workloads.

| Specification | st1 |
|--------------|-----|
| Volume Size | 125 GB - 16 TB |
| Max Throughput | 500 MB/s |
| Max IOPS | 500 IOPS |
| Baseline Throughput | 40 MB/s per TB |
| Price | $0.045/GB-month |
| Use Cases | Big data, log processing, data warehouses |

#### Cold HDD (sc1)

For infrequently accessed data.

| Specification | sc1 |
|--------------|-----|
| Volume Size | 125 GB - 16 TB |
| Max Throughput | 250 MB/s |
| Max IOPS | 250 IOPS |
| Baseline Throughput | 12 MB/s per TB |
| Price | $0.015/GB-month |
| Use Cases | Cold data, archives, infrequent access |

### EBS Volume Type Comparison

| Type | IOPS (Max) | Throughput (Max) | Price/GB | Best For |
|------|------------|------------------|----------|----------|
| gp3 | 16,000 | 1,000 MB/s | $0.08 | General workloads |
| gp2 | 16,000 | 250 MB/s | $0.10 | Legacy workloads |
| io2 | 64,000 | 1,000 MB/s | $0.125+ | Critical databases |
| io2 BE | 256,000 | 4,000 MB/s | $0.125+ | Extreme performance |
| st1 | 500 | 500 MB/s | $0.045 | Big data, streaming |
| sc1 | 250 | 250 MB/s | $0.015 | Cold storage |

### EBS CLI Commands

```bash
# Create a gp3 volume
aws ec2 create-volume \
    --volume-type gp3 \
    --size 100 \
    --iops 3000 \
    --throughput 125 \
    --availability-zone us-east-1a \
    --encrypted \
    --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=my-data-volume}]'

# Create an io2 volume
aws ec2 create-volume \
    --volume-type io2 \
    --size 100 \
    --iops 10000 \
    --availability-zone us-east-1a \
    --encrypted

# List volumes
aws ec2 describe-volumes \
    --query 'Volumes[*].[VolumeId,Size,VolumeType,State]' \
    --output table

# Attach volume to instance
aws ec2 attach-volume \
    --volume-id vol-0123456789abcdef0 \
    --instance-id i-1234567890abcdef0 \
    --device /dev/sdf

# Detach volume
aws ec2 detach-volume \
    --volume-id vol-0123456789abcdef0

# Modify volume (resize or change type)
aws ec2 modify-volume \
    --volume-id vol-0123456789abcdef0 \
    --size 200 \
    --volume-type gp3 \
    --iops 4000

# Delete volume
aws ec2 delete-volume \
    --volume-id vol-0123456789abcdef0
```

### Mounting EBS Volumes (Linux)

```bash
# List block devices
lsblk

# Check if volume has a filesystem
sudo file -s /dev/xvdf

# Create filesystem (if new volume - shows "data")
sudo mkfs -t xfs /dev/xvdf

# Create mount point
sudo mkdir /data

# Mount the volume
sudo mount /dev/xvdf /data

# Verify mount
df -h /data

# Make mount persistent (add to /etc/fstab)
# Get UUID
sudo blkid /dev/xvdf

# Add to /etc/fstab
echo "UUID=your-uuid-here /data xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab

# Test fstab entry
sudo umount /data
sudo mount -a
```

### Resizing EBS Volumes

```bash
# Step 1: Modify volume in AWS
aws ec2 modify-volume \
    --volume-id vol-0123456789abcdef0 \
    --size 200

# Step 2: Wait for modification to complete
aws ec2 describe-volumes-modifications \
    --volume-ids vol-0123456789abcdef0

# Step 3: Extend the partition (on the instance)
sudo growpart /dev/xvda 1

# Step 4: Extend the filesystem
# For XFS:
sudo xfs_growfs /data

# For ext4:
sudo resize2fs /dev/xvda1
```

---

## EBS Snapshots

### What are Snapshots?

EBS snapshots are point-in-time copies of EBS volumes stored in S3. They are:
- Incremental (only changed blocks are stored)
- Region-specific but can be copied across regions
- Can be used to create new volumes or AMIs
- Encrypted snapshots remain encrypted

### Snapshot Operations

```bash
# Create snapshot
aws ec2 create-snapshot \
    --volume-id vol-0123456789abcdef0 \
    --description "Daily backup $(date +%Y-%m-%d)" \
    --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=daily-backup}]'

# Create snapshot with multi-volume consistency
aws ec2 create-snapshots \
    --instance-specification InstanceId=i-1234567890abcdef0 \
    --description "Multi-volume snapshot" \
    --copy-tags-from-source volume

# List snapshots
aws ec2 describe-snapshots \
    --owner-ids self \
    --query 'Snapshots[*].[SnapshotId,VolumeId,StartTime,State]' \
    --output table

# Copy snapshot to another region
aws ec2 copy-snapshot \
    --source-region us-east-1 \
    --source-snapshot-id snap-0123456789abcdef0 \
    --destination-region us-west-2 \
    --description "DR copy"

# Create volume from snapshot
aws ec2 create-volume \
    --snapshot-id snap-0123456789abcdef0 \
    --availability-zone us-east-1a \
    --volume-type gp3

# Share snapshot with another account
aws ec2 modify-snapshot-attribute \
    --snapshot-id snap-0123456789abcdef0 \
    --attribute createVolumePermission \
    --operation-type add \
    --user-ids 123456789012

# Delete snapshot
aws ec2 delete-snapshot \
    --snapshot-id snap-0123456789abcdef0
```

### Snapshot Lifecycle Management

```bash
# Create lifecycle policy using Data Lifecycle Manager
aws dlm create-lifecycle-policy \
    --description "Daily EBS snapshots" \
    --state ENABLED \
    --execution-role-arn arn:aws:iam::123456789012:role/AWSDataLifecycleManagerDefaultRole \
    --policy-details '{
        "PolicyType": "EBS_SNAPSHOT_MANAGEMENT",
        "ResourceTypes": ["VOLUME"],
        "TargetTags": [{"Key": "Backup", "Value": "true"}],
        "Schedules": [{
            "Name": "DailySnapshots",
            "CreateRule": {
                "Interval": 24,
                "IntervalUnit": "HOURS",
                "Times": ["03:00"]
            },
            "RetainRule": {
                "Count": 7
            },
            "CopyTags": true
        }]
    }'
```

### Fast Snapshot Restore (FSR)

```bash
# Enable Fast Snapshot Restore
aws ec2 enable-fast-snapshot-restores \
    --availability-zones us-east-1a us-east-1b \
    --source-snapshot-ids snap-0123456789abcdef0

# Check FSR status
aws ec2 describe-fast-snapshot-restores \
    --filters "Name=snapshot-id,Values=snap-0123456789abcdef0"

# Disable FSR
aws ec2 disable-fast-snapshot-restores \
    --availability-zones us-east-1a \
    --source-snapshot-ids snap-0123456789abcdef0
```

---

## EBS Encryption

### Encryption Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    EBS Encryption Flow                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   EC2 Instance                                                   │
│       │                                                          │
│       │ Data encrypted/decrypted                                │
│       │ transparently                                           │
│       ▼                                                          │
│   ┌─────────────────┐                                           │
│   │   EBS Volume    │◀────── AWS KMS Key                        │
│   │   (Encrypted)   │                                           │
│   └─────────────────┘                                           │
│       │                                                          │
│       │ Snapshots inherit                                       │
│       │ encryption                                              │
│       ▼                                                          │
│   ┌─────────────────┐                                           │
│   │   Snapshot      │                                           │
│   │   (Encrypted)   │                                           │
│   └─────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Encryption Benefits

| Benefit | Description |
|---------|-------------|
| Data at Rest | Volume data encrypted on disk |
| Data in Transit | Encrypted between instance and volume |
| Snapshots | Automatically encrypted |
| Compliance | Meets regulatory requirements |
| No Performance Impact | Hardware-accelerated encryption |

### Encryption Commands

```bash
# Enable encryption by default for account
aws ec2 enable-ebs-encryption-by-default

# Get default KMS key for EBS
aws ec2 get-ebs-default-kms-key-id

# Set custom default KMS key
aws ec2 modify-ebs-default-kms-key-id \
    --kms-key-id alias/my-ebs-key

# Create encrypted volume with specific key
aws ec2 create-volume \
    --volume-type gp3 \
    --size 100 \
    --encrypted \
    --kms-key-id alias/my-ebs-key \
    --availability-zone us-east-1a

# Encrypt an unencrypted volume (via snapshot)
# 1. Create snapshot of unencrypted volume
aws ec2 create-snapshot \
    --volume-id vol-unencrypted

# 2. Copy snapshot with encryption
aws ec2 copy-snapshot \
    --source-region us-east-1 \
    --source-snapshot-id snap-unencrypted \
    --encrypted \
    --kms-key-id alias/my-key

# 3. Create new encrypted volume from snapshot
aws ec2 create-volume \
    --snapshot-id snap-encrypted \
    --availability-zone us-east-1a
```

---

## Instance Store (Ephemeral Storage)

### What is Instance Store?

Instance store provides temporary block-level storage that is physically attached to the host computer. Unlike EBS:
- Data is lost when instance stops, terminates, or fails
- Cannot be detached or attached to another instance
- Included in instance price (no additional cost)
- Provides very high IOPS and throughput

### Instance Store Characteristics

| Characteristic | Description |
|---------------|-------------|
| Persistence | Ephemeral (data lost on stop/terminate) |
| Performance | Very high (NVMe, local disk) |
| Capacity | Fixed based on instance type |
| Cost | Included with instance |
| Encryption | Instance store encryption available |

### Instance Types with Instance Store

| Instance Type | Instance Store | Capacity | IOPS |
|--------------|----------------|----------|------|
| i3.large | 1 x 475 GB NVMe | 475 GB | 100K |
| i3.xlarge | 1 x 950 GB NVMe | 950 GB | 206K |
| i3.2xlarge | 1 x 1.9 TB NVMe | 1.9 TB | 412K |
| d2.xlarge | 3 x 2 TB HDD | 6 TB | - |
| c5d.large | 1 x 50 GB NVMe | 50 GB | - |
| m5d.large | 1 x 75 GB NVMe | 75 GB | - |

### Using Instance Store

```bash
# List instance store volumes
lsblk

# Instance store typically appears as /dev/nvme*n1 or /dev/xvd*

# Check volume (usually unformatted)
sudo file -s /dev/nvme1n1

# Format the volume
sudo mkfs -t xfs /dev/nvme1n1

# Mount
sudo mkdir /mnt/instance-store
sudo mount /dev/nvme1n1 /mnt/instance-store

# Add to fstab (optional - use nofail)
# Note: Instance store won't be available on stop/start
echo "/dev/nvme1n1 /mnt/instance-store xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab
```

### Instance Store Use Cases

| Use Case | Why Instance Store |
|----------|-------------------|
| Temporary data | Scratch space, temp files |
| Cache | In-memory cache overflow |
| Buffer | Log buffer before shipping |
| Shuffle data | Spark shuffle, MapReduce intermediate |
| CI/CD builds | Build artifacts (rebuilt anyway) |

---

## EBS vs Instance Store Comparison

| Feature | EBS | Instance Store |
|---------|-----|----------------|
| Persistence | Persistent | Ephemeral |
| Attach/Detach | Yes | No |
| Replication | Within AZ | None |
| Snapshots | Yes | No |
| Encryption | Yes (KMS) | Yes (Instance) |
| Network | Network attached | Locally attached |
| Latency | Higher | Lower |
| Cost | Pay per GB | Included |
| Max IOPS | 256K (io2 BE) | 3M+ (i3en) |
| Max Throughput | 4 GB/s | 16 GB/s |

---

## EBS Multi-Attach

### Overview

Multi-Attach enables you to attach a single Provisioned IOPS (io1/io2) volume to multiple instances in the same AZ.

### Requirements and Limitations

| Requirement | Details |
|------------|---------|
| Volume Type | io1 or io2 only |
| Same AZ | All instances must be in same AZ |
| Max Instances | 16 instances |
| Nitro Instances | Required |
| Cluster-aware FS | Required (GFS2, OCFS2) |

### Multi-Attach Commands

```bash
# Create multi-attach enabled volume
aws ec2 create-volume \
    --volume-type io2 \
    --size 100 \
    --iops 10000 \
    --multi-attach-enabled \
    --availability-zone us-east-1a

# Attach to multiple instances
aws ec2 attach-volume \
    --volume-id vol-multi-attach \
    --instance-id i-instance-1 \
    --device /dev/sdf

aws ec2 attach-volume \
    --volume-id vol-multi-attach \
    --instance-id i-instance-2 \
    --device /dev/sdf
```

---

## CloudFormation for EBS

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 with EBS volumes and snapshots'

Parameters:
  InstanceType:
    Type: String
    Default: t3.medium

Resources:
  # Root volume is defined in BlockDeviceMappings
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64}}'
      InstanceType: !Ref InstanceType
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: 30
            VolumeType: gp3
            Iops: 3000
            Throughput: 125
            Encrypted: true
            DeleteOnTermination: true
      Tags:
        - Key: Name
          Value: web-server

  # Additional EBS volume
  DataVolume:
    Type: AWS::EC2::Volume
    Properties:
      AvailabilityZone: !GetAtt WebServer.AvailabilityZone
      Size: 100
      VolumeType: gp3
      Iops: 3000
      Throughput: 125
      Encrypted: true
      KmsKeyId: alias/aws/ebs
      Tags:
        - Key: Name
          Value: data-volume

  # Attach volume to instance
  DataVolumeAttachment:
    Type: AWS::EC2::VolumeAttachment
    Properties:
      Device: /dev/sdf
      InstanceId: !Ref WebServer
      VolumeId: !Ref DataVolume

  # Database volume with high IOPS
  DatabaseVolume:
    Type: AWS::EC2::Volume
    Properties:
      AvailabilityZone: !GetAtt WebServer.AvailabilityZone
      Size: 200
      VolumeType: io2
      Iops: 10000
      Encrypted: true
      Tags:
        - Key: Name
          Value: database-volume

  # Lifecycle policy for snapshots
  SnapshotLifecyclePolicy:
    Type: AWS::DLM::LifecyclePolicy
    Properties:
      Description: Daily backup policy
      State: ENABLED
      ExecutionRoleArn: !GetAtt DLMRole.Arn
      PolicyDetails:
        PolicyType: EBS_SNAPSHOT_MANAGEMENT
        ResourceTypes:
          - VOLUME
        TargetTags:
          - Key: Backup
            Value: 'true'
        Schedules:
          - Name: DailySnapshots
            CreateRule:
              Interval: 24
              IntervalUnit: HOURS
              Times:
                - '03:00'
            RetainRule:
              Count: 7
            CopyTags: true

  DLMRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: dlm.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSDataLifecycleManagerServiceRole

Outputs:
  DataVolumeId:
    Description: Data volume ID
    Value: !Ref DataVolume

  DatabaseVolumeId:
    Description: Database volume ID
    Value: !Ref DatabaseVolume
```

---

## Cost Optimization

### EBS Cost Comparison (100 GB, us-east-1)

| Volume Type | Monthly Cost | Use Case |
|------------|--------------|----------|
| gp3 (3000 IOPS) | $8.00 | General purpose |
| gp2 | $10.00 | Legacy |
| io2 (10000 IOPS) | $77.50 | High-performance DB |
| st1 | $4.50 | Sequential reads |
| sc1 | $1.50 | Archive |

### Cost Optimization Tips

1. **Use gp3 over gp2** - 20% cheaper with better base performance
2. **Right-size volumes** - Monitor and resize based on actual usage
3. **Delete unused volumes** - Check for unattached volumes
4. **Use appropriate type** - Don't use io2 for low-IOPS workloads
5. **Snapshot cleanup** - Delete old snapshots
6. **Use S3 for cold data** - Move infrequently accessed data to S3

```bash
# Find unattached volumes
aws ec2 describe-volumes \
    --filters "Name=status,Values=available" \
    --query 'Volumes[*].[VolumeId,Size,CreateTime]' \
    --output table

# Find old snapshots
aws ec2 describe-snapshots \
    --owner-ids self \
    --query 'Snapshots[?StartTime<=`2024-01-01`].[SnapshotId,VolumeId,StartTime]' \
    --output table
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Volume stuck attaching | Instance/volume mismatch | Check AZ, instance type |
| Poor performance | Wrong volume type | Upgrade to gp3 or io2 |
| Volume full | No space | Resize volume |
| Snapshot slow | Large volume | Use FSR or wait |
| Cannot delete volume | Still attached | Detach first |
| Encryption error | KMS key issue | Check key permissions |

### Performance Monitoring

```bash
# CloudWatch metrics for EBS
aws cloudwatch get-metric-statistics \
    --namespace AWS/EBS \
    --metric-name VolumeReadOps \
    --dimensions Name=VolumeId,Value=vol-0123456789abcdef0 \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 300 \
    --statistics Sum

# On instance - check I/O stats
iostat -x 1 5

# Check for I/O wait
top  # Look at wa% (wait percentage)
```

---

## Key Takeaways

1. **gp3 is the new default** - Use gp3 for most workloads
2. **io2 for critical databases** - When you need guaranteed IOPS
3. **Instance store is ephemeral** - Never store important data
4. **Snapshots are incremental** - Cost-effective for backups
5. **Encrypt everything** - Enable default encryption
6. **Monitor IOPS usage** - Right-size based on actual needs
7. **EBS volumes are AZ-specific** - Plan for multi-AZ deployments

---

## Next Steps

Continue to [05-security-groups.md](./05-security-groups.md) to learn about securing EC2 instances with security groups.
