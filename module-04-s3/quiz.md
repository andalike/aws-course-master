# Module 4: Amazon S3 - Comprehensive Quiz

## Introduction

This quiz contains 30 questions covering all aspects of Amazon S3, including storage classes, security, replication, performance, and event notifications. Each question includes a detailed explanation to reinforce your learning.

**Difficulty Levels:**
- [BEGINNER] - Fundamental concepts
- [INTERMEDIATE] - Applied knowledge
- [ADVANCED] - Complex scenarios and best practices

---

## Section 1: S3 Storage Classes and Pricing

### Question 1 [BEGINNER]
**Which S3 storage class offers the lowest storage cost per GB?**

A) S3 Standard
B) S3 Intelligent-Tiering
C) S3 Glacier Deep Archive
D) S3 One Zone-IA

<details>
<summary>View Answer</summary>

**Correct Answer: C) S3 Glacier Deep Archive**

**Explanation:** S3 Glacier Deep Archive is the lowest-cost storage class in Amazon S3, designed for long-term retention of data that is accessed rarely (once or twice per year). It costs approximately $0.00099/GB/month in us-east-1, compared to:
- S3 Standard: ~$0.023/GB/month
- S3 Intelligent-Tiering: ~$0.023/GB/month (Frequent Access tier)
- S3 One Zone-IA: ~$0.01/GB/month

The trade-off is retrieval time, which can be up to 12 hours for standard retrieval.
</details>

---

### Question 2 [INTERMEDIATE]
**A company stores 100TB of data that is accessed unpredictably. Some months the data is accessed frequently, other months not at all. Which storage class would be most cost-effective?**

A) S3 Standard
B) S3 Intelligent-Tiering
C) S3 One Zone-IA
D) S3 Standard-IA

<details>
<summary>View Answer</summary>

**Correct Answer: B) S3 Intelligent-Tiering**

**Explanation:** S3 Intelligent-Tiering is designed for data with unknown or changing access patterns. It automatically moves objects between tiers based on access patterns:
- Frequent Access tier (objects accessed)
- Infrequent Access tier (objects not accessed for 30 days)
- Archive Instant Access tier (objects not accessed for 90 days)
- Optional: Archive Access tier (90-730 days)
- Optional: Deep Archive Access tier (180-730 days)

There's no retrieval fee, only a small monitoring and automation fee (~$0.0025 per 1,000 objects). This is ideal for unpredictable access patterns where manual lifecycle policies would be impractical.
</details>

---

### Question 3 [ADVANCED]
**You need to store 50TB of compliance data for 7 years. The data must be retrievable within 12 hours if needed. Calculate the approximate annual storage cost difference between S3 Standard and S3 Glacier Deep Archive in us-east-1.**

A) ~$7,000/year difference
B) ~$12,500/year difference
C) ~$500/year difference
D) ~$2,000/year difference

<details>
<summary>View Answer</summary>

**Correct Answer: B) ~$12,500/year difference**

**Explanation:** Let's calculate:

**S3 Standard:**
- 50TB = 50,000 GB
- $0.023/GB/month × 50,000 GB × 12 months = $13,800/year

**S3 Glacier Deep Archive:**
- $0.00099/GB/month × 50,000 GB × 12 months = $594/year

**Difference:** $13,800 - $594 = ~$13,206/year (approximately $12,500)

This demonstrates the massive cost savings possible with proper storage class selection for archival data. The 12-hour retrieval requirement is met by Glacier Deep Archive's standard retrieval option.
</details>

---

### Question 4 [INTERMEDIATE]
**What is the minimum storage duration charge for S3 Standard-IA?**

A) No minimum
B) 30 days
C) 90 days
D) 180 days

<details>
<summary>View Answer</summary>

**Correct Answer: B) 30 days**

**Explanation:** S3 Standard-IA has a minimum storage duration of 30 days. If you delete an object before 30 days, you're still charged for 30 days of storage.

Minimum durations by storage class:
- S3 Standard: No minimum
- S3 Intelligent-Tiering: 30 days
- S3 Standard-IA: 30 days
- S3 One Zone-IA: 30 days
- S3 Glacier Instant Retrieval: 90 days
- S3 Glacier Flexible Retrieval: 90 days
- S3 Glacier Deep Archive: 180 days

This is important for cost optimization - don't use IA classes for temporary files!
</details>

---

### Question 5 [BEGINNER]
**Which S3 storage class does NOT provide 99.999999999% (11 9's) durability?**

A) S3 Standard
B) S3 One Zone-IA
C) S3 Glacier
D) All classes provide 11 9's durability

<details>
<summary>View Answer</summary>

**Correct Answer: B) S3 One Zone-IA**

**Explanation:** S3 One Zone-IA stores data in only one Availability Zone, which makes it vulnerable to AZ-level failures. While it still provides 99.999999999% durability against device failures, the data would be lost if the entire AZ is destroyed (e.g., natural disaster).

All other storage classes replicate data across at least 3 AZs, providing protection against AZ-level failures. Use S3 One Zone-IA only for:
- Easily reproducible data
- Secondary backup copies
- Data with a primary copy stored elsewhere
</details>

---

## Section 2: Bucket Policies, ACLs, and IAM Policies

### Question 6 [INTERMEDIATE]
**A bucket policy denies access to everyone except a specific IAM role. An IAM user with full S3 permissions tries to access objects in the bucket. What happens?**

A) Access is granted (IAM policy wins)
B) Access is denied (explicit deny wins)
C) Access depends on the object ACL
D) Access is granted if the user assumes the allowed role

<details>
<summary>View Answer</summary>

**Correct Answer: B) Access is denied (explicit deny wins)**

**Explanation:** In AWS, an explicit DENY always overrides any ALLOW. The policy evaluation logic is:
1. By default, all requests are implicitly denied
2. An explicit ALLOW overrides the implicit deny
3. An explicit DENY overrides any ALLOW

Even though the IAM user has full S3 permissions, the bucket policy's explicit deny takes precedence. This is a fundamental security principle in AWS - "deny by default, explicit deny wins."

```
+-------------------+
|   Decision Flow   |
+-------------------+
         |
    Explicit Deny? ----YES----> DENY
         |
         NO
         |
    Explicit Allow? ----NO----> DENY (implicit)
         |
        YES
         |
       ALLOW
```
</details>

---

### Question 7 [ADVANCED]
**Which of the following can a bucket policy do that an IAM policy cannot?**

A) Grant cross-account access
B) Restrict access based on IP address
C) Grant public access to objects
D) All of the above

<details>
<summary>View Answer</summary>

**Correct Answer: D) All of the above**

**Explanation:** Bucket policies are resource-based policies attached to S3 buckets and can:

1. **Grant cross-account access:** Bucket policies can grant access to principals in other AWS accounts, while IAM policies can only grant permissions to principals in the same account.

2. **Restrict by IP address:** Bucket policies can use conditions like `aws:SourceIp` to restrict access based on IP addresses. IAM policies can also do this, but bucket policies are more commonly used for this purpose.

3. **Grant public access:** Bucket policies can specify `"Principal": "*"` to grant access to anonymous users. IAM policies are attached to identities, so they cannot grant public access directly.

```json
{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::example-bucket/*",
    "Condition": {
        "IpAddress": {
            "aws:SourceIp": "203.0.113.0/24"
        }
    }
}
```
</details>

---

### Question 8 [BEGINNER]
**What is the recommended best practice for S3 object ACLs in new applications?**

A) Use ACLs for fine-grained access control
B) Disable ACLs and use bucket policies instead
C) Combine ACLs with bucket policies for layered security
D) Use ACLs only for cross-account access

<details>
<summary>View Answer</summary>

**Correct Answer: B) Disable ACLs and use bucket policies instead**

**Explanation:** AWS recommends disabling ACLs for most use cases. As of April 2023, new buckets have ACLs disabled by default with the "Bucket owner enforced" setting.

Reasons to disable ACLs:
- Simplifies permission management (single place to manage access)
- Reduces complexity and potential security misconfigurations
- Bucket policies provide more flexibility with conditions
- All objects are owned by the bucket owner

Enable "Bucket owner enforced" with:
```bash
aws s3api put-bucket-ownership-controls \
    --bucket my-bucket \
    --ownership-controls Rules=[{ObjectOwnership=BucketOwnerEnforced}]
```
</details>

---

### Question 9 [INTERMEDIATE]
**An S3 bucket has Block Public Access settings enabled at the account level but disabled at the bucket level. What is the effective public access setting?**

A) Public access is allowed (bucket setting wins)
B) Public access is blocked (account setting wins)
C) It depends on the bucket policy
D) It causes a conflict error

<details>
<summary>View Answer</summary>

**Correct Answer: B) Public access is blocked (account setting wins)**

**Explanation:** S3 Block Public Access works at multiple levels, and the most restrictive setting wins:

1. **Account level:** Applies to all buckets in the account
2. **Bucket level:** Applies to a specific bucket

If Block Public Access is enabled at the account level, it overrides any bucket-level settings. This is a safety mechanism to prevent accidental public exposure.

```
+---------------------------+
|    Account Level: ON      |  <-- Takes precedence
+---------------------------+
            |
+---------------------------+
|    Bucket Level: OFF      |  <-- Ignored
+---------------------------+
            |
      Result: BLOCKED
```

Always enable Block Public Access at the account level for security, then selectively disable at the bucket level only when absolutely necessary.
</details>

---

### Question 10 [ADVANCED]
**You have a bucket policy that allows s3:GetObject for a specific IAM role. The role's IAM policy has no S3 permissions. Can the role access objects?**

A) No, both policies must allow access
B) Yes, resource-based policies can grant access independently
C) No, IAM policies must explicitly allow the action
D) It depends on the bucket's ACL settings

<details>
<summary>View Answer</summary>

**Correct Answer: B) Yes, resource-based policies can grant access independently**

**Explanation:** For same-account access, either the identity-based policy (IAM) OR the resource-based policy (bucket policy) can grant access. This is different from cross-account access, where both must allow.

**Same-account access:**
- IAM policy allows OR bucket policy allows = Access granted

**Cross-account access:**
- IAM policy allows AND bucket policy allows = Access granted

This is why bucket policies can be powerful for granting access without modifying IAM policies. However, for cross-account scenarios, both sides must explicitly allow the access.
</details>

---

## Section 3: Versioning and Lifecycle Policies

### Question 11 [BEGINNER]
**What happens when you delete an object in a versioning-enabled bucket?**

A) The object is permanently deleted
B) All versions of the object are deleted
C) A delete marker is placed on the object
D) The latest version is moved to Glacier

<details>
<summary>View Answer</summary>

**Correct Answer: C) A delete marker is placed on the object**

**Explanation:** When versioning is enabled, deleting an object doesn't actually remove it. Instead, S3 creates a "delete marker" which becomes the current version. The previous versions remain intact and recoverable.

```
Before Delete:        After Delete:
+-------------+       +---------------+
| Version 3   | ----> | Delete Marker | (current)
+-------------+       +---------------+
| Version 2   |       | Version 3     |
+-------------+       +---------------+
| Version 1   |       | Version 2     |
+-------------+       +---------------+
                      | Version 1     |
                      +---------------+
```

To permanently delete, you must delete each version by specifying the version ID, or delete the delete marker to restore the object.
</details>

---

### Question 12 [INTERMEDIATE]
**A lifecycle policy transitions objects to S3 Glacier Flexible Retrieval after 90 days. What happens to existing object versions when versioning is enabled?**

A) All versions are transitioned
B) Only the current version is transitioned
C) Lifecycle rules don't apply to versioned objects
D) It depends on the lifecycle rule configuration

<details>
<summary>View Answer</summary>

**Correct Answer: D) It depends on the lifecycle rule configuration**

**Explanation:** Lifecycle policies can be configured separately for current and non-current versions:

```xml
<LifecycleConfiguration>
  <Rule>
    <!-- For current versions -->
    <Transition>
      <Days>90</Days>
      <StorageClass>GLACIER</StorageClass>
    </Transition>

    <!-- For non-current versions -->
    <NoncurrentVersionTransition>
      <NoncurrentDays>30</NoncurrentDays>
      <StorageClass>GLACIER</StorageClass>
    </NoncurrentVersionTransition>

    <!-- Delete old non-current versions -->
    <NoncurrentVersionExpiration>
      <NoncurrentDays>365</NoncurrentDays>
    </NoncurrentVersionExpiration>
  </Rule>
</LifecycleConfiguration>
```

You can configure different rules for:
- Current versions (Transition)
- Non-current versions (NoncurrentVersionTransition)
- Delete markers (ExpiredObjectDeleteMarker)
</details>

---

### Question 13 [ADVANCED]
**You want to minimize storage costs for a versioned bucket. Which lifecycle configuration is most efficient?**

A) Transition all versions to Glacier after 30 days
B) Delete all non-current versions immediately
C) Transition non-current versions to IA after 30 days, then delete after 90 days
D) Move current versions to Intelligent-Tiering, delete non-current after 1 day

<details>
<summary>View Answer</summary>

**Correct Answer: C) Transition non-current versions to IA after 30 days, then delete after 90 days**

**Explanation:** The optimal strategy depends on recovery needs, but option C provides a balance:

```
Cost-Optimized Lifecycle Strategy:
+------------------+     +------------------+     +------------------+
|  Current Version | --> | Non-current (IA) | --> |     Deleted      |
|    (Standard)    |     |  (After 30 days) |     | (After 90 days)  |
+------------------+     +------------------+     +------------------+

Why this works:
1. Current version stays in Standard for fast access
2. Non-current versions move to cheaper IA storage
3. Old versions auto-delete to prevent unbounded growth
```

Option A: 30-day minimum storage for IA makes immediate Glacier transition wasteful
Option B: No version protection defeats the purpose of versioning
Option D: 1-day retention provides almost no recovery window

Always consider the 30-day minimum storage duration for IA classes!
</details>

---

### Question 14 [INTERMEDIATE]
**Can you disable versioning once it's been enabled on a bucket?**

A) Yes, versioning can be disabled completely
B) No, versioning can only be suspended, not disabled
C) Yes, but all versions will be deleted
D) No, you must delete and recreate the bucket

<details>
<summary>View Answer</summary>

**Correct Answer: B) No, versioning can only be suspended, not disabled**

**Explanation:** Once versioning is enabled on a bucket, it cannot be completely disabled. It can only be suspended:

**Versioning States:**
1. **Unversioned** (default) - Versioning never enabled
2. **Enabled** - All objects get version IDs
3. **Suspended** - New objects get null version ID, existing versions preserved

```
+--------------+     +----------+     +-----------+
| Unversioned  | --> | Enabled  | --> | Suspended |
+--------------+     +----------+     +-----------+
       ^                  ^                 |
       |                  +-----------------+
       |                  (can re-enable)
       +-- Cannot return to unversioned
```

When suspended:
- Existing versions remain accessible
- New uploads get null version ID
- Overwrites replace the null version
</details>

---

### Question 15 [BEGINNER]
**What is the minimum object size that can be transitioned to S3 Standard-IA using lifecycle policies?**

A) No minimum
B) 64 KB
C) 128 KB
D) 256 KB

<details>
<summary>View Answer</summary>

**Correct Answer: C) 128 KB**

**Explanation:** S3 Standard-IA has a minimum object size of 128 KB for billing purposes. Objects smaller than 128 KB are charged as if they were 128 KB.

For lifecycle transitions:
- Objects smaller than 128 KB are not transitioned to IA classes
- This is because the overhead and minimum charges would make it more expensive

**Cost-effective transitions:**
| Storage Class | Minimum Recommended Size |
|--------------|-------------------------|
| Standard-IA | 128 KB |
| One Zone-IA | 128 KB |
| Glacier Instant Retrieval | 128 KB |
| Glacier Flexible | No minimum |
| Glacier Deep Archive | No minimum |

For small files, consider aggregating them into larger archives before transitioning.
</details>

---

## Section 4: Cross-Region and Same-Region Replication

### Question 16 [BEGINNER]
**Which of the following is a prerequisite for S3 Cross-Region Replication?**

A) Both buckets must be in the same account
B) Versioning must be enabled on both source and destination buckets
C) The buckets must have the same storage class
D) Both buckets must have the same name prefix

<details>
<summary>View Answer</summary>

**Correct Answer: B) Versioning must be enabled on both source and destination buckets**

**Explanation:** Versioning is a mandatory prerequisite for S3 replication. Both source and destination buckets must have versioning enabled.

**Replication Prerequisites:**
1. Versioning enabled on both buckets
2. IAM role with appropriate permissions
3. For CRR: Buckets in different regions
4. For cross-account: Bucket policy on destination

```
+-------------------+        +-------------------+
| Source Bucket     |        | Destination Bucket|
| (Versioning: ON)  | -----> | (Versioning: ON)  |
| Region: us-east-1 |        | Region: eu-west-1 |
+-------------------+        +-------------------+
```

Note: Buckets can be in different accounts, have different names, and use different storage classes.
</details>

---

### Question 17 [INTERMEDIATE]
**Which objects are replicated by default when you enable replication on an existing bucket?**

A) All existing and new objects
B) Only new objects uploaded after replication is enabled
C) Only objects matching the replication rule prefix
D) All objects except those in Glacier

<details>
<summary>View Answer</summary>

**Correct Answer: B) Only new objects uploaded after replication is enabled**

**Explanation:** By default, S3 replication only applies to new objects uploaded after the replication rule is enabled. Existing objects are NOT replicated automatically.

To replicate existing objects, you have two options:

1. **S3 Batch Replication:** AWS-managed solution to replicate existing objects
```bash
aws s3control create-job \
    --account-id 123456789012 \
    --operation '{"S3ReplicateObject":{}}' \
    --manifest-generator ...
```

2. **Copy objects manually:** Use `aws s3 cp` to copy existing objects (they'll be treated as new uploads)

```
Timeline:
        Replication Enabled
              |
    +---------+---------+
    |                   |
Existing Objects    New Objects
(NOT replicated)    (Replicated)
    |                   |
Use Batch Replication   Automatic
```
</details>

---

### Question 18 [ADVANCED]
**You have bidirectional replication set up between two buckets. What prevents replication loops?**

A) Replication automatically stops after one hop
B) Replica objects have a special flag that prevents re-replication
C) You must manually configure loop prevention
D) Bidirectional replication is not supported

<details>
<summary>View Answer</summary>

**Correct Answer: B) Replica objects have a special flag that prevents re-replication**

**Explanation:** S3 uses replica modification sync to handle bidirectional replication. Objects created by replication are marked and won't be re-replicated, preventing infinite loops.

```
+------------------+                    +------------------+
|   Bucket A       |                    |   Bucket B       |
|   (us-east-1)    |                    |   (eu-west-1)    |
+------------------+                    +------------------+
        |                                       |
        | Upload object.txt                     |
        v                                       |
  [Object created] -----------------------> [Replica created]
        |                                       |
        |  (Marked as replica -                 |
        |   won't replicate back)               |
        |                                       |
        |                         Upload other.txt
        |                                       v
  [Replica created] <------------------- [Object created]
```

Enable replica modification sync:
```json
{
  "ReplicaModifications": {
    "Status": "Enabled"
  }
}
```
</details>

---

### Question 19 [INTERMEDIATE]
**What is S3 Replication Time Control (RTC)?**

A) A feature to schedule replication at specific times
B) An SLA guaranteeing 99.99% of objects replicate within 15 minutes
C) A way to throttle replication bandwidth
D) A feature to pause and resume replication

<details>
<summary>View Answer</summary>

**Correct Answer: B) An SLA guaranteeing 99.99% of objects replicate within 15 minutes**

**Explanation:** S3 Replication Time Control (RTC) provides a predictable replication time SLA:
- 99.99% of objects replicated within 15 minutes
- Includes replication metrics and notifications
- Additional cost on top of standard replication

```
+-------------------+
| Standard Replication |
| - Best effort      |
| - Usually minutes  |
| - No SLA           |
+-------------------+
         vs
+-------------------+
| With RTC          |
| - 15 min SLA      |
| - 99.99% of objects|
| - CloudWatch metrics|
| - SNS notifications|
+-------------------+
```

RTC is ideal for:
- Compliance requirements with defined RPO
- Critical data requiring predictable replication
- Disaster recovery scenarios

Enable RTC in replication rules with `ReplicationTimeValue` set to 15 minutes.
</details>

---

### Question 20 [ADVANCED]
**You need to replicate objects to a bucket in another AWS account. What configurations are required on the destination bucket?**

A) Only enable versioning
B) Add a bucket policy granting the source account's replication role permissions
C) Create an IAM role in the destination account
D) Both A and B

<details>
<summary>View Answer</summary>

**Correct Answer: D) Both A and B**

**Explanation:** For cross-account replication, the destination bucket requires:

1. **Versioning enabled** (mandatory for all replication)
2. **Bucket policy** granting the source account's IAM role permission to replicate

Destination bucket policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReplication",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::SOURCE-ACCOUNT:role/replication-role"
      },
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete",
        "s3:ReplicateTags"
      ],
      "Resource": "arn:aws:s3:::destination-bucket/*"
    }
  ]
}
```

```
Source Account (111111111111)      Destination Account (222222222222)
+-------------------+              +-------------------+
| Source Bucket     |              | Dest Bucket       |
|                   |   Replicate  |                   |
| Replication Role -+------------->| Bucket Policy     |
|                   |              | (allows role)     |
+-------------------+              +-------------------+
```
</details>

---

## Section 5: S3 Security Features

### Question 21 [BEGINNER]
**Which encryption option has AWS manage the encryption keys entirely?**

A) SSE-C
B) SSE-S3
C) SSE-KMS
D) Client-side encryption

<details>
<summary>View Answer</summary>

**Correct Answer: B) SSE-S3**

**Explanation:** SSE-S3 (Server-Side Encryption with S3-Managed Keys) is fully managed by AWS:
- AWS creates, manages, and rotates the keys
- No additional configuration or key management needed
- Uses AES-256 encryption

```
Encryption Options:
+----------+------------------+----------------------+
| Option   | Key Management   | Your Control         |
+----------+------------------+----------------------+
| SSE-S3   | Fully AWS        | None (simplest)      |
| SSE-KMS  | AWS KMS          | Key policies, audit  |
| SSE-C    | Customer         | Full (most complex)  |
| Client   | Customer         | Full (encrypt before)|
+----------+------------------+----------------------+
```

SSE-KMS uses AWS KMS but gives you control over key policies and audit trails.
SSE-C requires you to provide encryption keys with each request.
</details>

---

### Question 22 [INTERMEDIATE]
**You want to enforce that all objects uploaded to a bucket are encrypted with SSE-KMS. How do you achieve this?**

A) Enable default encryption on the bucket
B) Create a bucket policy denying uploads without encryption headers
C) Enable S3 Object Lock
D) Use VPC endpoints only

<details>
<summary>View Answer</summary>

**Correct Answer: B) Create a bucket policy denying uploads without encryption headers**

**Explanation:** While default encryption ensures objects are encrypted, a bucket policy is needed to ENFORCE that clients explicitly use SSE-KMS:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    },
    {
      "Sid": "DenyNoEncryptionHeader",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    }
  ]
}
```

Default encryption (option A) applies encryption to objects without headers, but doesn't deny incorrectly encrypted uploads.
</details>

---

### Question 23 [ADVANCED]
**What is the difference between S3 Object Lock Governance mode and Compliance mode?**

A) Governance mode is cheaper
B) Compliance mode allows root user to delete, Governance does not
C) Governance mode can be overridden by users with special permissions, Compliance cannot
D) There is no difference, they are aliases

<details>
<summary>View Answer</summary>

**Correct Answer: C) Governance mode can be overridden by users with special permissions, Compliance cannot**

**Explanation:** S3 Object Lock provides WORM (Write Once Read Many) protection in two modes:

**Governance Mode:**
- Users with `s3:BypassGovernanceRetention` permission can override
- Useful for testing or when exceptions may be needed
- Protects against accidental deletion

**Compliance Mode:**
- NOBODY can override, including root user or AWS
- Cannot be shortened or removed until retention expires
- Required for strict regulatory compliance (SEC 17a-4, FINRA, etc.)

```
+------------------+     +------------------+
|  Governance Mode |     |  Compliance Mode |
+------------------+     +------------------+
| Can be overridden|     | Cannot override  |
| by special perms |     | under ANY        |
|                  |     | circumstances    |
| Good for:        |     | Good for:        |
| - Testing        |     | - Regulatory     |
| - Soft protection|     | - Legal holds    |
+------------------+     +------------------+
```

Choose Compliance mode carefully - once set, the retention period cannot be shortened!
</details>

---

### Question 24 [INTERMEDIATE]
**Which S3 feature allows you to grant temporary access to an object without changing bucket policies?**

A) S3 Access Points
B) Pre-signed URLs
C) S3 Object Lambda
D) Cross-origin resource sharing (CORS)

<details>
<summary>View Answer</summary>

**Correct Answer: B) Pre-signed URLs**

**Explanation:** Pre-signed URLs allow temporary access to private S3 objects without modifying permissions:

```python
import boto3
from datetime import timedelta

s3_client = boto3.client('s3')

# Generate a pre-signed URL valid for 1 hour
url = s3_client.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'private/file.pdf'},
    ExpiresIn=3600  # seconds
)
```

**Pre-signed URL Characteristics:**
- Contains signature derived from creator's credentials
- Expires after specified time (max 7 days with IAM user credentials)
- Anyone with URL can access the object until expiration
- No bucket policy or ACL changes needed

```
+-------------+                    +-------------+
| Your App    | -- Generate URL -> | S3 Object   |
+-------------+                    +-------------+
      |                                   ^
      | Share URL                         |
      v                                   |
+-------------+                           |
| End User    | -- Access with URL -------+
+-------------+   (temporary, signed)
```
</details>

---

### Question 25 [BEGINNER]
**What does S3 Access Points provide?**

A) Faster data transfer speeds
B) Named network endpoints with dedicated access policies
C) Direct VPC connectivity to S3
D) SSL/TLS certificates for custom domains

<details>
<summary>View Answer</summary>

**Correct Answer: B) Named network endpoints with dedicated access policies**

**Explanation:** S3 Access Points simplify managing access to shared datasets by providing:
- Unique hostnames for each access point
- Dedicated access policies per access point
- Can be restricted to specific VPCs
- Simplifies managing complex bucket policies

```
                    +-------------------+
                    |    S3 Bucket      |
                    | (shared dataset)  |
                    +-------------------+
                           / | \
                          /  |  \
              +-----------+ +|+ +------------+
              |           | | | |            |
        +-----+-----+ +---+-+--+ +-----+-----+
        |Access Point| |Access | |Access Point|
        | for Team A | |Point B| | for VPC    |
        | (Read-Only)| |(R/W)  | | (Restricted)|
        +-----------+ +--------+ +------------+
              |            |           |
           Team A       Team B      VPC Apps
```

Benefits:
- Each team gets their own endpoint and policy
- No need for complex bucket policies with multiple statements
- VPC-restricted access points for network isolation
- Easier to audit and manage
</details>

---

## Section 6: Performance Optimization

### Question 26 [INTERMEDIATE]
**What is the recommended approach for uploading a 5GB file to S3?**

A) Standard single PUT request
B) Multipart upload
C) S3 Transfer Acceleration
D) AWS Snowball

<details>
<summary>View Answer</summary>

**Correct Answer: B) Multipart upload**

**Explanation:** Multipart upload is recommended for files larger than 100MB and required for files larger than 5GB:

**Multipart Upload Benefits:**
- Parallel uploads for improved throughput
- Pause and resume capability
- Failed part retry without starting over
- Begin upload before knowing total size

```
5GB File
+-------+-------+-------+-------+-------+
| Part 1| Part 2| Part 3| Part 4| Part 5|  (100MB each)
+-------+-------+-------+-------+-------+
    |       |       |       |       |
    v       v       v       v       v
         Parallel Upload Streams
                    |
                    v
              [S3 Combines]
                    |
                    v
            Complete Object
```

**CLI Example:**
```bash
# AWS CLI automatically uses multipart for large files
aws s3 cp large-file.zip s3://my-bucket/ \
    --expected-size 5368709120

# Or configure multipart threshold
aws configure set default.s3.multipart_threshold 64MB
```

Single PUT is limited to 5GB. Transfer Acceleration speeds up transfers but still requires multipart for large files.
</details>

---

### Question 27 [ADVANCED]
**How does S3 prefix design affect performance, and what is the current request rate limit per prefix?**

A) 3,500 PUT/POST/DELETE and 5,500 GET/HEAD per second per prefix
B) 100 requests per second regardless of prefix
C) No limits with proper prefix design
D) 1,000 requests per second per bucket

<details>
<summary>View Answer</summary>

**Correct Answer: A) 3,500 PUT/POST/DELETE and 5,500 GET/HEAD per second per prefix**

**Explanation:** S3 provides high request rates per prefix:
- 3,500 PUT/COPY/POST/DELETE requests per second
- 5,500 GET/HEAD requests per second

**Key Point:** These limits are per PREFIX, not per bucket. You can achieve virtually unlimited throughput by using multiple prefixes.

```
Prefix Design for High Throughput:
+----------------------+
| Bad: All in one prefix|
| /data/file1.txt      |  Limited to ~5,500 GET/s
| /data/file2.txt      |
| /data/file3.txt      |
+----------------------+

+----------------------+
| Good: Distributed    |
| /2024/01/file1.txt   |  Each prefix gets full throughput
| /2024/02/file2.txt   |
| /2024/03/file3.txt   |
+----------------------+

+----------------------+
| Better: Hash prefix  |
| /a1b2/data/file1.txt |  Automatically distributed
| /c3d4/data/file2.txt |
| /e5f6/data/file3.txt |
+----------------------+
```

Modern S3 automatically partitions based on key name, but intentional prefix design can optimize specific access patterns.
</details>

---

### Question 28 [INTERMEDIATE]
**What is S3 Select used for?**

A) Selecting which storage class to use
B) Retrieving a subset of data from an object using SQL
C) Selecting objects for batch operations
D) Choosing replication destinations

<details>
<summary>View Answer</summary>

**Correct Answer: B) Retrieving a subset of data from an object using SQL**

**Explanation:** S3 Select allows you to retrieve specific data from objects using SQL queries, reducing data transfer and processing time:

```sql
-- Instead of downloading entire 1GB CSV file
SELECT s.name, s.age
FROM s3object s
WHERE s.age > 25
```

**Supported Formats:**
- CSV
- JSON
- Apache Parquet

**Benefits:**
```
Traditional Approach:
+------------+     Download     +-----------+    Process    +--------+
| S3 Object  | --> 1GB -------> | Your App  | --> Filter -> | 10 MB  |
| (1 GB)     |                  | (Process) |               | Result |
+------------+                  +-----------+               +--------+

With S3 Select:
+------------+     Filter at S3    +--------+
| S3 Object  | --> 10 MB --------> | Result |
| (1 GB)     |    (SQL query)      |        |
+------------+                     +--------+

Savings: ~99% less data transfer!
```

```python
import boto3

s3 = boto3.client('s3')
response = s3.select_object_content(
    Bucket='my-bucket',
    Key='data.csv',
    ExpressionType='SQL',
    Expression="SELECT * FROM s3object s WHERE s.status = 'active'",
    InputSerialization={'CSV': {'FileHeaderInfo': 'USE'}},
    OutputSerialization={'CSV': {}}
)
```
</details>

---

### Question 29 [BEGINNER]
**What is S3 Transfer Acceleration?**

A) Compresses data before upload
B) Uses CloudFront edge locations for faster uploads
C) Increases S3 request rate limits
D) Parallelizes single object downloads

<details>
<summary>View Answer</summary>

**Correct Answer: B) Uses CloudFront edge locations for faster uploads**

**Explanation:** S3 Transfer Acceleration uses CloudFront's globally distributed edge locations to accelerate uploads:

```
Without Transfer Acceleration:
+--------+                                      +-----------+
| Client | -------- Long distance -----------> | S3 Bucket |
| (Tokyo)|         (High latency)              | (Virginia)|
+--------+                                      +-----------+

With Transfer Acceleration:
+--------+     +----------------+               +-----------+
| Client | --> | CloudFront     | -- AWS --> | S3 Bucket |
| (Tokyo)|     | Edge (Tokyo)   |  Backbone    | (Virginia)|
+--------+     +----------------+               +-----------+
              (Low latency)     (Optimized network)
```

**When to Use:**
- Uploading from geographically distant locations
- Consistent fast uploads needed worldwide
- Large files over long distances

**Endpoint:**
```
Normal: mybucket.s3.us-east-1.amazonaws.com
Accelerated: mybucket.s3-accelerate.amazonaws.com
```

Use the [Speed Comparison Tool](http://s3-accelerate-speedtest.s3-accelerate.amazonaws.com) to test if acceleration helps your use case.
</details>

---

### Question 30 [ADVANCED]
**You need to retrieve only the first 1MB of a 1GB video file stored in S3. What is the most efficient approach?**

A) Download the full file and truncate locally
B) Use S3 Select with LIMIT clause
C) Use byte-range fetch with Range header
D) Create a separate object with just the first 1MB

<details>
<summary>View Answer</summary>

**Correct Answer: C) Use byte-range fetch with Range header**

**Explanation:** Byte-range fetches allow you to retrieve specific portions of an object using the HTTP Range header:

```bash
# Retrieve first 1MB of file
aws s3api get-object \
    --bucket my-bucket \
    --key large-video.mp4 \
    --range bytes=0-1048575 \
    output.partial

# Or with curl
curl -H "Range: bytes=0-1048575" \
    "https://my-bucket.s3.amazonaws.com/large-video.mp4" \
    -o first-1mb.mp4
```

**Use Cases:**
1. **Video streaming:** Retrieve chunks as needed
2. **Large file headers:** Read metadata without downloading
3. **Parallel downloads:** Split large files across multiple requests
4. **Resume failed downloads:** Continue from last successful byte

```
+-------------------------------------------+
|            1GB Video File                 |
+-------------------------------------------+
| Byte 0-1MB | Byte 1MB-2MB | ... | ...     |
+-------------------------------------------+
      |
      | Range: bytes=0-1048575
      v
+------------+
| First 1MB  |  Only this portion transferred
+------------+
```

S3 Select (option B) is for querying CSV/JSON/Parquet data, not binary files.
</details>

---

## Section 7: Event Notifications

### Question 31 [BEGINNER]
**Which AWS services can receive S3 event notifications natively?**

A) Lambda, SQS, and SNS only
B) Lambda, SQS, SNS, and EventBridge
C) Any AWS service through EventBridge
D) Only Lambda functions

<details>
<summary>View Answer</summary>

**Correct Answer: B) Lambda, SQS, SNS, and EventBridge**

**Explanation:** S3 can send event notifications to four destinations:

```
                    +-------------------+
                    |    S3 Bucket      |
                    | (Event Source)    |
                    +-------------------+
                           |
        +------------------+------------------+
        |         |               |          |
        v         v               v          v
    +-------+ +-------+      +-------+  +-----------+
    |Lambda | | SQS   |      | SNS   |  |EventBridge|
    +-------+ +-------+      +-------+  +-----------+
                                              |
                                    +---------+---------+
                                    |    |    |    |   |
                                    v    v    v    v   v
                                 (Route to 35+ AWS services)
```

**Direct Destinations:**
1. **Lambda:** Serverless function execution
2. **SQS:** Queue for decoupled processing
3. **SNS:** Fan-out to multiple subscribers

**EventBridge:**
- Route to 35+ AWS services
- Advanced filtering rules
- Archive and replay events
- More flexible event routing
</details>

---

### Question 32 [INTERMEDIATE]
**You want to trigger a Lambda function only when JPEG files are uploaded to the "images/" prefix. How do you configure this?**

A) Configure the Lambda function to filter events
B) Use S3 event notification with prefix and suffix filters
C) Use S3 Select to identify JPEG files
D) Configure S3 Intelligent-Tiering

<details>
<summary>View Answer</summary>

**Correct Answer: B) Use S3 event notification with prefix and suffix filters**

**Explanation:** S3 event notifications support prefix and suffix filtering:

```json
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessImages",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "images/"
            },
            {
              "Name": "suffix",
              "Value": ".jpg"
            }
          ]
        }
      }
    }
  ]
}
```

```
S3 Upload Events:
+------------------------+     +-----------------+
| images/photo.jpg      | --> | Lambda Invoked  | (Matches prefix AND suffix)
+------------------------+     +-----------------+

+------------------------+     +-----------------+
| images/photo.png      | --> | Ignored         | (Suffix doesn't match)
+------------------------+     +-----------------+

+------------------------+     +-----------------+
| documents/photo.jpg   | --> | Ignored         | (Prefix doesn't match)
+------------------------+     +-----------------+
```

Note: You can have multiple notification configurations with different filters on the same bucket.
</details>

---

### Question 33 [ADVANCED]
**What permissions are required to configure S3 event notifications to Lambda?**

A) Only S3 permissions on the bucket
B) Only Lambda permissions to invoke the function
C) Lambda resource-based policy allowing S3 to invoke, plus S3 permissions to configure notifications
D) IAM role attached to S3 bucket

<details>
<summary>View Answer</summary>

**Correct Answer: C) Lambda resource-based policy allowing S3 to invoke, plus S3 permissions to configure notifications**

**Explanation:** Two permissions are needed:

1. **Lambda resource-based policy** allowing S3 to invoke the function:
```bash
aws lambda add-permission \
    --function-name ProcessImages \
    --principal s3.amazonaws.com \
    --statement-id S3Invoke \
    --action "lambda:InvokeFunction" \
    --source-arn arn:aws:s3:::my-bucket \
    --source-account 123456789012
```

2. **IAM permissions** to configure S3 notifications:
```json
{
  "Effect": "Allow",
  "Action": "s3:PutBucketNotification",
  "Resource": "arn:aws:s3:::my-bucket"
}
```

```
Permission Flow:
+------------+                    +------------+
| Your IAM   | -- Configure ----> | S3 Bucket  |
| Principal  |   notifications    | Notification|
+------------+                    +------------+
                                        |
                                        | Invoke
                                        v
                                  +------------+
                                  | Lambda     |
                                  | (Needs     |
                                  |  resource  |
                                  |  policy)   |
                                  +------------+
```
</details>

---

## Section 8: Scenario-Based Questions

### Question 34 [ADVANCED]
**A company needs to store application logs with the following requirements: immediate access for 30 days, queryable access for 90 days, archived for 7 years, and deleted after. Which lifecycle configuration is optimal?**

A) S3 Standard -> Standard-IA -> Glacier -> Delete
B) S3 Standard -> Intelligent-Tiering -> Glacier Deep Archive -> Delete
C) S3 Standard (30d) -> Standard-IA (90d) -> Glacier Deep Archive (7y) -> Delete
D) S3 Intelligent-Tiering for all phases

<details>
<summary>View Answer</summary>

**Correct Answer: C) S3 Standard (30d) -> Standard-IA (90d) -> Glacier Deep Archive (7y) -> Delete**

**Explanation:** This configuration matches the requirements exactly:

```yaml
LifecycleConfiguration:
  Rules:
    - ID: "LogLifecycle"
      Status: Enabled
      Transitions:
        - Days: 30
          StorageClass: STANDARD_IA      # Queryable but less accessed
        - Days: 90
          StorageClass: DEEP_ARCHIVE     # Archived for compliance
      Expiration:
        Days: 2555                        # 7 years = ~2555 days
```

```
Timeline:
Day 0          Day 30           Day 90              Year 7
  |              |                |                   |
  v              v                v                   v
+----------+  +-----------+  +-------------+     +--------+
| Standard |->| Standard- |->| Deep Archive|---->| DELETE |
| (Active  |  | IA        |  | (Compliance |     |        |
|  access) |  | (Query)   |  |  storage)   |     |        |
+----------+  +-----------+  +-------------+     +--------+
   $0.023       $0.0125        $0.00099
  /GB/month    /GB/month      /GB/month

Cost for 1TB over lifecycle:
- First 30 days (Standard): ~$23
- Days 30-90 (IA): ~$25
- 7 years (Deep Archive): ~$82
Total: ~$130 vs ~$1,932 if kept in Standard
```
</details>

---

### Question 35 [ADVANCED]
**You discover that your S3 costs have increased significantly. Investigation shows thousands of incomplete multipart uploads. How do you address this?**

A) Delete incomplete uploads manually
B) Configure a lifecycle rule to abort incomplete multipart uploads
C) Disable multipart uploads for the bucket
D) Enable S3 Intelligent-Tiering

<details>
<summary>View Answer</summary>

**Correct Answer: B) Configure a lifecycle rule to abort incomplete multipart uploads**

**Explanation:** Incomplete multipart uploads consume storage and incur costs. Configure a lifecycle rule to automatically clean them up:

```json
{
  "Rules": [
    {
      "ID": "CleanupIncompleteMultipartUploads",
      "Status": "Enabled",
      "Filter": {},
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
```

**CLI Commands:**
```bash
# List incomplete multipart uploads
aws s3api list-multipart-uploads --bucket my-bucket

# Abort a specific upload
aws s3api abort-multipart-upload \
    --bucket my-bucket \
    --key large-file.zip \
    --upload-id UPLOAD_ID

# Configure lifecycle rule
aws s3api put-bucket-lifecycle-configuration \
    --bucket my-bucket \
    --lifecycle-configuration file://lifecycle.json
```

```
Cost Impact:
+----------------------------------+
| Incomplete Uploads               |
| - Each part stored = charges     |
| - Can accumulate significantly   |
| - Often forgotten/invisible      |
+----------------------------------+
           |
           | Lifecycle Rule
           v
+----------------------------------+
| Auto-cleanup after X days        |
| - Abort incomplete uploads       |
| - Reclaim storage costs          |
+----------------------------------+
```
</details>

---

## Scoring Guide

| Score | Level | Recommendation |
|-------|-------|----------------|
| 0-10 | Beginner | Review fundamentals before hands-on labs |
| 11-20 | Intermediate | Ready for basic S3 implementations |
| 21-28 | Advanced | Ready for complex S3 architectures |
| 29-35 | Expert | Consider AWS certification |

---

## Quick Reference: S3 Limits and Defaults

| Feature | Limit/Default |
|---------|---------------|
| Maximum object size | 5 TB |
| Single PUT limit | 5 GB |
| Multipart upload minimum | 5 MB (except last part) |
| Maximum parts per upload | 10,000 |
| Bucket name length | 3-63 characters |
| Default storage class | S3 Standard |
| Versioning states | Unversioned, Enabled, Suspended |
| Maximum lifecycle rules | 1,000 per bucket |
| Event notification destinations | Lambda, SQS, SNS, EventBridge |
| Pre-signed URL max expiry (IAM user) | 7 days |
| Request rate per prefix | 3,500 PUT + 5,500 GET/sec |

---

## Summary

This quiz covered the essential S3 concepts you need for:
- AWS Solutions Architect certification
- Real-world S3 implementations
- Cost optimization strategies
- Security best practices
- Performance tuning

Continue to the hands-on labs to practice these concepts with real AWS resources!
