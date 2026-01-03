# Module 04: Amazon S3 (Simple Storage Service)

## Module Overview

Amazon Simple Storage Service (Amazon S3) is an object storage service offering industry-leading scalability, data availability, security, and performance. This module provides comprehensive coverage of S3, from fundamental concepts to advanced features and real-world implementation patterns.

S3 stores data as objects within buckets. An object consists of a file and optionally any metadata that describes that file. With S3, you can store and retrieve any amount of data at any time, from anywhere on the web.

---

## Learning Objectives

By the end of this module, you will be able to:

1. **Understand S3 Architecture** - Explain buckets, objects, keys, and the S3 namespace
2. **Choose Storage Classes** - Select appropriate storage classes based on access patterns and cost requirements
3. **Implement Security** - Configure bucket policies, ACLs, encryption, and access controls
4. **Manage Object Lifecycle** - Set up versioning and lifecycle policies for automated data management
5. **Host Static Websites** - Deploy static websites with custom domains and error handling
6. **Configure Replication** - Implement Cross-Region and Same-Region Replication strategies
7. **Optimize Performance** - Use multipart uploads, transfer acceleration, and prefix optimization
8. **Build Event-Driven Architectures** - Trigger Lambda, SNS, and SQS from S3 events
9. **Generate Presigned URLs** - Create secure, time-limited access to private objects
10. **Apply Best Practices** - Implement production-ready S3 architectures

---

## S3 Use Cases

### Primary Use Cases

| Use Case | Description | Example |
|----------|-------------|---------|
| **Backup & Restore** | Durable storage for backup data | Database backups, system snapshots |
| **Archive** | Long-term data retention | Compliance records, historical data |
| **Data Lakes** | Centralized repository for analytics | Big data analytics, ML training data |
| **Static Website Hosting** | Host static web content | Marketing sites, documentation |
| **Content Distribution** | Origin for CloudFront CDN | Media streaming, software distribution |
| **Hybrid Cloud Storage** | Extend on-premises storage | AWS Storage Gateway integration |
| **Disaster Recovery** | Cross-region data replication | Business continuity planning |
| **Application Data** | Store application assets | User uploads, generated reports |

### Industry-Specific Applications

```
Healthcare:        Medical imaging storage (HIPAA compliant)
Financial:         Transaction logs, regulatory archives
Media:             Video transcoding workflows
Gaming:            Game assets, player data
IoT:               Sensor data collection and analysis
E-commerce:        Product images, inventory data
```

---

## Module Structure

| File | Topic | Duration |
|------|-------|----------|
| [01-s3-fundamentals.md](./01-s3-fundamentals.md) | Buckets, Objects, Keys, Consistency Model | 45 min |
| [02-storage-classes.md](./02-storage-classes.md) | Storage Classes & Cost Optimization | 60 min |
| [03-bucket-policies.md](./03-bucket-policies.md) | Policies, ACLs, Block Public Access | 45 min |
| [04-versioning-and-lifecycle.md](./04-versioning-and-lifecycle.md) | Versioning & Lifecycle Management | 45 min |
| [05-s3-security.md](./05-s3-security.md) | Encryption & Security Best Practices | 60 min |
| [06-static-website-hosting.md](./06-static-website-hosting.md) | Static Website Hosting Guide | 45 min |
| [07-s3-replication.md](./07-s3-replication.md) | Cross-Region & Same-Region Replication | 45 min |
| [08-s3-performance.md](./08-s3-performance.md) | Performance Optimization | 45 min |
| [09-s3-event-notifications.md](./09-s3-event-notifications.md) | Event-Driven Architecture | 45 min |
| [10-presigned-urls.md](./10-presigned-urls.md) | Presigned URLs & Secure Sharing | 30 min |
| [11-hands-on-labs.md](./11-hands-on-labs.md) | 8 Practical Labs | 3-4 hours |
| [quiz.md](./quiz.md) | Module Assessment (20 Questions) | 30 min |

**Total Estimated Time: 10-12 hours**

---

## Prerequisites

Before starting this module, you should have:

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI installed and configured
- [ ] Basic understanding of:
  - HTTP/HTTPS protocols
  - JSON syntax (for policies)
  - Command line operations
- [ ] (Optional) Python 3.x or Node.js for SDK examples

---

## Key S3 Concepts Quick Reference

```
+------------------+     +------------------+     +------------------+
|     BUCKET       |     |     OBJECT       |     |      KEY         |
+------------------+     +------------------+     +------------------+
| - Globally unique|     | - File + metadata|     | - Full path name |
| - Region-specific|     | - Max 5TB size   |     | - Unique in      |
| - Flat namespace |     | - Immutable      |     |   bucket         |
+------------------+     +------------------+     +------------------+

URL Format: https://bucket-name.s3.region.amazonaws.com/key-name
Example:    https://my-app.s3.us-east-1.amazonaws.com/images/logo.png
```

---

## S3 Architecture Patterns

### Pattern 1: Static Website with CDN

```
┌─────────┐    ┌────────────┐    ┌─────────────┐    ┌────────┐
│  Users  │───▶│ CloudFront │───▶│  S3 Bucket  │    │Route 53│
└─────────┘    │    CDN     │    │  (Origin)   │◀───│  DNS   │
               └────────────┘    └─────────────┘    └────────┘
```

### Pattern 2: Data Lake Architecture

```
┌──────────────┐    ┌─────────────┐    ┌───────────────┐
│ Data Sources │───▶│  S3 Raw     │───▶│   S3 Curated  │
│ (IoT, Apps)  │    │  (Landing)  │    │   (Processed) │
└──────────────┘    └─────────────┘    └───────┬───────┘
                                               │
                    ┌──────────────────────────┼──────────────┐
                    ▼                          ▼              ▼
              ┌──────────┐            ┌─────────────┐  ┌───────────┐
              │  Athena  │            │   Redshift  │  │ SageMaker │
              │ (Query)  │            │  Spectrum   │  │   (ML)    │
              └──────────┘            └─────────────┘  └───────────┘
```

### Pattern 3: Event-Driven Processing

```
┌─────────┐    ┌─────────────┐    ┌────────────┐    ┌─────────────┐
│ Upload  │───▶│  S3 Bucket  │───▶│   Lambda   │───▶│  DynamoDB   │
└─────────┘    │  (Trigger)  │    │ (Process)  │    │  (Store)    │
               └─────────────┘    └────────────┘    └─────────────┘
                      │
                      ▼
               ┌─────────────┐
               │     SNS     │
               │  (Notify)   │
               └─────────────┘
```

---

## Cost Optimization Tips

1. **Right-size Storage Classes**: Use S3 Intelligent-Tiering for unpredictable access patterns
2. **Implement Lifecycle Policies**: Automatically transition to cheaper storage classes
3. **Enable S3 Analytics**: Identify opportunities to move data to less expensive tiers
4. **Use S3 Inventory**: Audit and report on replication and encryption status
5. **Clean Up Incomplete Multipart Uploads**: Configure lifecycle rules to abort them
6. **Monitor with Cost Explorer**: Track S3 costs by bucket and storage class

---

## AWS CLI Quick Start

```bash
# Configure AWS CLI
aws configure

# Create a bucket
aws s3 mb s3://my-bucket-name --region us-east-1

# Upload a file
aws s3 cp myfile.txt s3://my-bucket-name/

# List bucket contents
aws s3 ls s3://my-bucket-name/

# Sync a directory
aws s3 sync ./local-folder s3://my-bucket-name/remote-folder

# Download a file
aws s3 cp s3://my-bucket-name/myfile.txt ./

# Remove a bucket (must be empty)
aws s3 rb s3://my-bucket-name
```

---

## Additional Resources

### AWS Documentation
- [Amazon S3 User Guide](https://docs.aws.amazon.com/s3/index.html)
- [S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)

### AWS SDKs
- [Boto3 (Python)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [AWS SDK for JavaScript](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-s3/)

### Best Practices
- [S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [S3 Performance Guidelines](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)

---

## Certification Relevance

This module covers topics essential for:

| Certification | Relevance |
|---------------|-----------|
| AWS Certified Cloud Practitioner | High |
| AWS Certified Solutions Architect - Associate | Very High |
| AWS Certified Solutions Architect - Professional | Very High |
| AWS Certified Developer - Associate | High |
| AWS Certified SysOps Administrator - Associate | Very High |
| AWS Certified Security - Specialty | High |

---

**Next Step**: Begin with [01-s3-fundamentals.md](./01-s3-fundamentals.md) to understand S3's core concepts.
