# Module 4: Comprehensive S3 Hands-On Lab

## Lab Overview

This comprehensive lab covers all major S3 features through practical exercises. You will build a complete S3 infrastructure including buckets, static website hosting, versioning, lifecycle policies, replication, event notifications, and batch operations.

**Duration:** 2-3 hours
**Cost Estimate:** < $5 (mostly free tier eligible)
**Prerequisites:**
- AWS CLI configured with appropriate credentials
- Basic command line knowledge
- Text editor

---

## Table of Contents

1. [Lab Setup](#lab-1-lab-setup)
2. [Create Buckets with Various Configurations](#lab-2-create-buckets-with-various-configurations)
3. [Static Website with Custom Domain](#lab-3-static-website-with-custom-domain)
4. [Versioning and Lifecycle Policies](#lab-4-versioning-and-lifecycle-policies)
5. [Cross-Region Replication](#lab-5-cross-region-replication)
6. [Event Notifications](#lab-6-event-notifications)
7. [S3 Batch Operations](#lab-7-s3-batch-operations)
8. [Cleanup](#lab-8-cleanup)

---

## Lab 1: Lab Setup

### Objectives
- Set up environment variables
- Verify AWS CLI configuration
- Create base resources

### Step 1.1: Configure Environment Variables

```bash
# Set unique suffix for bucket names (must be globally unique)
export SUFFIX=$(date +%s)
export AWS_REGION="us-east-1"
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Define bucket names
export MAIN_BUCKET="s3-lab-main-${SUFFIX}"
export WEBSITE_BUCKET="s3-lab-website-${SUFFIX}"
export LOGS_BUCKET="s3-lab-logs-${SUFFIX}"
export REPLICA_BUCKET="s3-lab-replica-${SUFFIX}"
export DEST_REGION="eu-west-1"

# Verify configuration
echo "Account ID: ${ACCOUNT_ID}"
echo "Main Bucket: ${MAIN_BUCKET}"
echo "Website Bucket: ${WEBSITE_BUCKET}"
echo "Logs Bucket: ${LOGS_BUCKET}"
echo "Replica Bucket: ${REPLICA_BUCKET}"
```

### Step 1.2: Verify AWS CLI

```bash
# Check AWS CLI version
aws --version

# Verify credentials
aws sts get-caller-identity

# Check default region
aws configure get region
```

### Step 1.3: Create Working Directory

```bash
# Create lab directory
mkdir -p ~/s3-lab/{website,data,scripts}
cd ~/s3-lab

# Create test files
echo "Hello from S3 Lab!" > data/hello.txt
echo "Test file 1" > data/file1.txt
echo "Test file 2" > data/file2.txt
dd if=/dev/urandom of=data/large-file.bin bs=1M count=10 2>/dev/null

echo "Lab directory created: ~/s3-lab"
ls -la data/
```

---

## Lab 2: Create Buckets with Various Configurations

### Objectives
- Create buckets with different configurations
- Apply encryption settings
- Configure access logging
- Set up Block Public Access

### Step 2.1: Create Main Bucket with Default Encryption

```bash
# Create main bucket
aws s3api create-bucket \
    --bucket ${MAIN_BUCKET} \
    --region ${AWS_REGION}

# Enable default encryption (SSE-S3)
aws s3api put-bucket-encryption \
    --bucket ${MAIN_BUCKET} \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                },
                "BucketKeyEnabled": true
            }
        ]
    }'

# Verify encryption
aws s3api get-bucket-encryption --bucket ${MAIN_BUCKET}

echo "Main bucket created with SSE-S3 encryption"
```

### Step 2.2: Create Logs Bucket

```bash
# Create logs bucket
aws s3api create-bucket \
    --bucket ${LOGS_BUCKET} \
    --region ${AWS_REGION}

# Grant S3 logging service write access
aws s3api put-bucket-acl \
    --bucket ${LOGS_BUCKET} \
    --grant-write URI=http://acs.amazonaws.com/groups/s3/LogDelivery \
    --grant-read-acp URI=http://acs.amazonaws.com/groups/s3/LogDelivery

# Alternative: Use bucket policy for logging (recommended approach)
cat > /tmp/logs-bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3ServerAccessLogsPolicy",
            "Effect": "Allow",
            "Principal": {
                "Service": "logging.s3.amazonaws.com"
            },
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::${LOGS_BUCKET}/*",
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:s3:::${MAIN_BUCKET}"
                },
                "StringEquals": {
                    "aws:SourceAccount": "${ACCOUNT_ID}"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${LOGS_BUCKET} \
    --policy file:///tmp/logs-bucket-policy.json

echo "Logs bucket created and configured"
```

### Step 2.3: Enable Access Logging on Main Bucket

```bash
# Configure access logging
aws s3api put-bucket-logging \
    --bucket ${MAIN_BUCKET} \
    --bucket-logging-status '{
        "LoggingEnabled": {
            "TargetBucket": "'${LOGS_BUCKET}'",
            "TargetPrefix": "access-logs/"
        }
    }'

# Verify logging configuration
aws s3api get-bucket-logging --bucket ${MAIN_BUCKET}

echo "Access logging enabled on main bucket"
```

### Step 2.4: Configure Block Public Access

```bash
# Ensure Block Public Access is enabled
aws s3api put-public-access-block \
    --bucket ${MAIN_BUCKET} \
    --public-access-block-configuration '{
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }'

# Verify settings
aws s3api get-public-access-block --bucket ${MAIN_BUCKET}

echo "Block Public Access configured"
```

### Step 2.5: Add Bucket Tags

```bash
# Add tags to main bucket
aws s3api put-bucket-tagging \
    --bucket ${MAIN_BUCKET} \
    --tagging '{
        "TagSet": [
            {"Key": "Environment", "Value": "Lab"},
            {"Key": "Project", "Value": "S3-Training"},
            {"Key": "Owner", "Value": "DevTeam"}
        ]
    }'

# Verify tags
aws s3api get-bucket-tagging --bucket ${MAIN_BUCKET}

echo "Tags added to bucket"
```

### Step 2.6: Upload Test Objects

```bash
# Upload files to main bucket
aws s3 cp data/hello.txt s3://${MAIN_BUCKET}/documents/
aws s3 cp data/file1.txt s3://${MAIN_BUCKET}/documents/
aws s3 cp data/file2.txt s3://${MAIN_BUCKET}/documents/
aws s3 cp data/large-file.bin s3://${MAIN_BUCKET}/data/

# List uploaded objects
aws s3 ls s3://${MAIN_BUCKET}/ --recursive

# Verify encryption on uploaded object
aws s3api head-object \
    --bucket ${MAIN_BUCKET} \
    --key documents/hello.txt \
    --query 'ServerSideEncryption'

echo "Test files uploaded"
```

### Checkpoint 2
```
Verify:
[ ] Main bucket exists with encryption
[ ] Logs bucket exists with proper policy
[ ] Access logging is enabled
[ ] Block Public Access is configured
[ ] Tags are applied
[ ] Test files are uploaded
```

---

## Lab 3: Static Website with Custom Domain

### Objectives
- Create a static website bucket
- Configure website hosting
- Upload website content
- Test the website endpoint

### Step 3.1: Create Website Bucket

```bash
# Create website bucket
aws s3api create-bucket \
    --bucket ${WEBSITE_BUCKET} \
    --region ${AWS_REGION}

# Disable Block Public Access for website
aws s3api put-public-access-block \
    --bucket ${WEBSITE_BUCKET} \
    --public-access-block-configuration '{
        "BlockPublicAcls": false,
        "IgnorePublicAcls": false,
        "BlockPublicPolicy": false,
        "RestrictPublicBuckets": false
    }'

echo "Website bucket created"
```

### Step 3.2: Configure Website Hosting

```bash
# Enable static website hosting
aws s3api put-bucket-website \
    --bucket ${WEBSITE_BUCKET} \
    --website-configuration '{
        "IndexDocument": {"Suffix": "index.html"},
        "ErrorDocument": {"Key": "error.html"}
    }'

# Verify website configuration
aws s3api get-bucket-website --bucket ${WEBSITE_BUCKET}

echo "Static website hosting enabled"
```

### Step 3.3: Add Public Access Bucket Policy

```bash
# Create bucket policy for public read access
cat > /tmp/website-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${WEBSITE_BUCKET}/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${WEBSITE_BUCKET} \
    --policy file:///tmp/website-policy.json

echo "Public access policy applied"
```

### Step 3.4: Create Website Content

```bash
# Create index.html
cat > website/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3 Static Website Lab</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
        }
        ul {
            line-height: 2;
        }
        .aws-badge {
            background: #ff9900;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to S3 Static Website Lab!</h1>

        <div class="info-box">
            <strong>Congratulations!</strong> You've successfully deployed a static website on Amazon S3.
        </div>

        <h2>What You've Accomplished:</h2>
        <ul>
            <li>Created an S3 bucket for website hosting</li>
            <li>Configured static website hosting settings</li>
            <li>Applied a bucket policy for public access</li>
            <li>Uploaded HTML content</li>
        </ul>

        <h2>S3 Website Features:</h2>
        <ul>
            <li>Highly available and durable storage</li>
            <li>Automatic scaling for traffic</li>
            <li>Low cost hosting solution</li>
            <li>Easy integration with CloudFront CDN</li>
        </ul>

        <div class="aws-badge">Powered by Amazon S3</div>

        <p style="margin-top: 30px; color: #666;">
            <a href="about.html">About</a> |
            <a href="contact.html">Contact</a>
        </p>
    </div>
</body>
</html>
EOF

# Create error.html
cat > website/error.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - Page Not Found</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f5f5f5;
        }
        .error-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            max-width: 500px;
            margin: 0 auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #e74c3c; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <p><a href="index.html">Return to Homepage</a></p>
    </div>
</body>
</html>
EOF

# Create about.html
cat > website/about.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>About - S3 Lab</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #667eea; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <h1>About This Lab</h1>
    <p>This is part of the AWS S3 training module.</p>
    <p><a href="index.html">Back to Home</a></p>
</body>
</html>
EOF

echo "Website content created"
```

### Step 3.5: Upload Website Content

```bash
# Upload all website files
aws s3 sync website/ s3://${WEBSITE_BUCKET}/ \
    --content-type "text/html"

# List uploaded files
aws s3 ls s3://${WEBSITE_BUCKET}/

echo "Website content uploaded"
```

### Step 3.6: Test the Website

```bash
# Get website endpoint
WEBSITE_URL="http://${WEBSITE_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
echo "Website URL: ${WEBSITE_URL}"

# Test with curl
curl -s ${WEBSITE_URL} | head -20

# Test error page
curl -s ${WEBSITE_URL}/nonexistent-page.html | head -10

echo ""
echo "Open in browser: ${WEBSITE_URL}"
```

### Checkpoint 3
```
Verify:
[ ] Website bucket created
[ ] Static hosting enabled
[ ] Public policy applied
[ ] Website accessible via browser
[ ] Error page works correctly
```

---

## Lab 4: Versioning and Lifecycle Policies

### Objectives
- Enable versioning
- Create multiple object versions
- Configure lifecycle policies
- Test version management

### Step 4.1: Enable Versioning

```bash
# Enable versioning on main bucket
aws s3api put-bucket-versioning \
    --bucket ${MAIN_BUCKET} \
    --versioning-configuration Status=Enabled

# Verify versioning
aws s3api get-bucket-versioning --bucket ${MAIN_BUCKET}

echo "Versioning enabled"
```

### Step 4.2: Create Object Versions

```bash
# Create initial version
echo "Version 1 - Initial content" > data/versioned-file.txt
aws s3 cp data/versioned-file.txt s3://${MAIN_BUCKET}/versioned/

# Create version 2
echo "Version 2 - Updated content" > data/versioned-file.txt
aws s3 cp data/versioned-file.txt s3://${MAIN_BUCKET}/versioned/

# Create version 3
echo "Version 3 - Final content" > data/versioned-file.txt
aws s3 cp data/versioned-file.txt s3://${MAIN_BUCKET}/versioned/

# List all versions
aws s3api list-object-versions \
    --bucket ${MAIN_BUCKET} \
    --prefix versioned/ \
    --query 'Versions[*].[Key,VersionId,LastModified,Size]' \
    --output table

echo "Multiple versions created"
```

### Step 4.3: Retrieve Specific Version

```bash
# Get version IDs
VERSIONS=$(aws s3api list-object-versions \
    --bucket ${MAIN_BUCKET} \
    --prefix versioned/versioned-file.txt \
    --query 'Versions[*].VersionId' \
    --output text)

echo "Version IDs: ${VERSIONS}"

# Get the oldest version (last in list)
OLDEST_VERSION=$(echo ${VERSIONS} | awk '{print $NF}')
echo "Retrieving oldest version: ${OLDEST_VERSION}"

aws s3api get-object \
    --bucket ${MAIN_BUCKET} \
    --key versioned/versioned-file.txt \
    --version-id ${OLDEST_VERSION} \
    /tmp/old-version.txt

cat /tmp/old-version.txt
```

### Step 4.4: Test Delete and Recovery

```bash
# Delete the object (creates delete marker)
aws s3 rm s3://${MAIN_BUCKET}/versioned/versioned-file.txt

# Verify delete marker
aws s3api list-object-versions \
    --bucket ${MAIN_BUCKET} \
    --prefix versioned/versioned-file.txt \
    --query 'DeleteMarkers' \
    --output table

# Object appears deleted
aws s3 ls s3://${MAIN_BUCKET}/versioned/

# Recover by deleting the delete marker
DELETE_MARKER=$(aws s3api list-object-versions \
    --bucket ${MAIN_BUCKET} \
    --prefix versioned/versioned-file.txt \
    --query 'DeleteMarkers[0].VersionId' \
    --output text)

aws s3api delete-object \
    --bucket ${MAIN_BUCKET} \
    --key versioned/versioned-file.txt \
    --version-id ${DELETE_MARKER}

# Verify recovery
aws s3 ls s3://${MAIN_BUCKET}/versioned/
aws s3 cp s3://${MAIN_BUCKET}/versioned/versioned-file.txt -

echo "Object recovered from delete!"
```

### Step 4.5: Configure Lifecycle Policy

```bash
# Create comprehensive lifecycle policy
cat > /tmp/lifecycle-policy.json << 'EOF'
{
    "Rules": [
        {
            "ID": "TransitionToIA",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "data/"
            },
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "STANDARD_IA"
                },
                {
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }
            ]
        },
        {
            "ID": "ExpireOldVersions",
            "Status": "Enabled",
            "Filter": {
                "Prefix": ""
            },
            "NoncurrentVersionTransitions": [
                {
                    "NoncurrentDays": 30,
                    "StorageClass": "STANDARD_IA"
                }
            ],
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 90
            }
        },
        {
            "ID": "CleanupIncompleteUploads",
            "Status": "Enabled",
            "Filter": {
                "Prefix": ""
            },
            "AbortIncompleteMultipartUpload": {
                "DaysAfterInitiation": 7
            }
        },
        {
            "ID": "ExpireDeleteMarkers",
            "Status": "Enabled",
            "Filter": {
                "Prefix": ""
            },
            "Expiration": {
                "ExpiredObjectDeleteMarker": true
            }
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket ${MAIN_BUCKET} \
    --lifecycle-configuration file:///tmp/lifecycle-policy.json

# Verify lifecycle configuration
aws s3api get-bucket-lifecycle-configuration --bucket ${MAIN_BUCKET}

echo "Lifecycle policy configured"
```

### Step 4.6: Visualize Lifecycle

```
Lifecycle Policy Visualization:

Data Files (data/* prefix):
+-------------+     +-------------+     +-------------+
|  Standard   | --> | Standard-IA | --> |   Glacier   |
|  (Day 0-30) |     | (Day 30-90) |     | (Day 90+)   |
+-------------+     +-------------+     +-------------+

Non-current Versions:
+-------------+     +-------------+     +-------------+
|  Standard   | --> | Standard-IA | --> |   Deleted   |
|  (Day 0-30) |     | (Day 30-90) |     | (Day 90+)   |
+-------------+     +-------------+     +-------------+

Incomplete Multipart Uploads:
+-------------------+     +-------------+
| Incomplete Upload | --> |   Aborted   |
| (Day 0-7)         |     | (Day 7+)    |
+-------------------+     +-------------+
```

### Checkpoint 4
```
Verify:
[ ] Versioning enabled
[ ] Multiple versions created
[ ] Can retrieve specific versions
[ ] Delete and recovery works
[ ] Lifecycle policy applied
```

---

## Lab 5: Cross-Region Replication

### Objectives
- Create destination bucket in another region
- Configure IAM role for replication
- Enable cross-region replication
- Verify replication works

### Step 5.1: Create Destination Bucket

```bash
# Create replica bucket in different region
aws s3api create-bucket \
    --bucket ${REPLICA_BUCKET} \
    --region ${DEST_REGION} \
    --create-bucket-configuration LocationConstraint=${DEST_REGION}

# Enable versioning (required for replication)
aws s3api put-bucket-versioning \
    --bucket ${REPLICA_BUCKET} \
    --versioning-configuration Status=Enabled \
    --region ${DEST_REGION}

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket ${REPLICA_BUCKET} \
    --region ${DEST_REGION} \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

echo "Replica bucket created in ${DEST_REGION}"
```

### Step 5.2: Create IAM Role for Replication

```bash
# Create trust policy
cat > /tmp/replication-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the role
aws iam create-role \
    --role-name S3ReplicationRole-${SUFFIX} \
    --assume-role-policy-document file:///tmp/replication-trust-policy.json

# Create permission policy
cat > /tmp/replication-permissions.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::${MAIN_BUCKET}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObjectVersionForReplication",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectVersionTagging"
            ],
            "Resource": "arn:aws:s3:::${MAIN_BUCKET}/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ReplicateTags"
            ],
            "Resource": "arn:aws:s3:::${REPLICA_BUCKET}/*"
        }
    ]
}
EOF

# Attach policy to role
aws iam put-role-policy \
    --role-name S3ReplicationRole-${SUFFIX} \
    --policy-name S3ReplicationPolicy \
    --policy-document file:///tmp/replication-permissions.json

echo "Replication IAM role created"

# Wait for role propagation
sleep 10
```

### Step 5.3: Configure Replication Rule

```bash
# Create replication configuration
cat > /tmp/replication-config.json << EOF
{
    "Role": "arn:aws:iam::${ACCOUNT_ID}:role/S3ReplicationRole-${SUFFIX}",
    "Rules": [
        {
            "ID": "ReplicateToEU",
            "Priority": 1,
            "Status": "Enabled",
            "Filter": {
                "Prefix": "replicated/"
            },
            "Destination": {
                "Bucket": "arn:aws:s3:::${REPLICA_BUCKET}",
                "StorageClass": "STANDARD"
            },
            "DeleteMarkerReplication": {
                "Status": "Enabled"
            }
        }
    ]
}
EOF

# Apply replication configuration
aws s3api put-bucket-replication \
    --bucket ${MAIN_BUCKET} \
    --replication-configuration file:///tmp/replication-config.json

# Verify configuration
aws s3api get-bucket-replication --bucket ${MAIN_BUCKET}

echo "Replication configured"
```

### Step 5.4: Test Replication

```bash
# Upload test files to replicated prefix
echo "This file will be replicated to EU" > data/replication-test.txt
aws s3 cp data/replication-test.txt s3://${MAIN_BUCKET}/replicated/

echo "File uploaded. Waiting for replication..."
sleep 30

# Check source bucket
echo "Source bucket (${AWS_REGION}):"
aws s3 ls s3://${MAIN_BUCKET}/replicated/

# Check destination bucket
echo "Destination bucket (${DEST_REGION}):"
aws s3 ls s3://${REPLICA_BUCKET}/replicated/ --region ${DEST_REGION}

# Check replication status
aws s3api head-object \
    --bucket ${MAIN_BUCKET} \
    --key replicated/replication-test.txt \
    --query 'ReplicationStatus'
```

### Step 5.5: Verify Replication Metrics

```bash
# Upload more files to see replication in action
for i in {1..5}; do
    echo "Replication test file ${i}" > data/test-${i}.txt
    aws s3 cp data/test-${i}.txt s3://${MAIN_BUCKET}/replicated/
done

sleep 60

# Check all files replicated
echo "Checking replicated files in destination..."
aws s3 ls s3://${REPLICA_BUCKET}/replicated/ --region ${DEST_REGION}
```

### Replication Architecture Diagram

```
Cross-Region Replication Setup:

     us-east-1                              eu-west-1
+------------------+                   +------------------+
|  Main Bucket     |                   |  Replica Bucket  |
|  ${MAIN_BUCKET}  |                   |  ${REPLICA_BUCKET}|
+------------------+                   +------------------+
| replicated/*     | ----------------> | replicated/*     |
|   - test-1.txt   |   Async Copy     |   - test-1.txt   |
|   - test-2.txt   |                  |   - test-2.txt   |
+------------------+                   +------------------+
         |
         v
 +----------------+
 | IAM Role       |
 | (Permissions)  |
 +----------------+
```

### Checkpoint 5
```
Verify:
[ ] Destination bucket created with versioning
[ ] IAM role created with proper permissions
[ ] Replication rule configured
[ ] Files replicated successfully
[ ] Replication status shows "COMPLETED"
```

---

## Lab 6: Event Notifications

### Objectives
- Create Lambda function for processing
- Configure S3 event notifications
- Test event-driven processing

### Step 6.1: Create Lambda Execution Role

```bash
# Create Lambda execution role
cat > /tmp/lambda-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name S3EventLambdaRole-${SUFFIX} \
    --assume-role-policy-document file:///tmp/lambda-trust-policy.json

# Create permission policy
cat > /tmp/lambda-permissions.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:HeadObject"
            ],
            "Resource": "arn:aws:s3:::${MAIN_BUCKET}/*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name S3EventLambdaRole-${SUFFIX} \
    --policy-name S3EventLambdaPolicy \
    --policy-document file:///tmp/lambda-permissions.json

echo "Lambda execution role created"
sleep 10
```

### Step 6.2: Create Lambda Function

```bash
# Create Lambda function code
cat > scripts/lambda_function.py << 'EOF'
import json
import urllib.parse
import boto3
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Process S3 event notifications."""

    print(f"Received event: {json.dumps(event, indent=2)}")

    processed_count = 0

    for record in event.get('Records', []):
        # Extract event details
        event_name = record['eventName']
        event_time = record['eventTime']
        bucket_name = record['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        object_size = record['s3']['object'].get('size', 0)

        print(f"Event: {event_name}")
        print(f"Time: {event_time}")
        print(f"Bucket: {bucket_name}")
        print(f"Key: {object_key}")
        print(f"Size: {object_size} bytes")

        # Get object metadata for created events
        if event_name.startswith('ObjectCreated'):
            try:
                response = s3_client.head_object(
                    Bucket=bucket_name,
                    Key=object_key
                )
                content_type = response.get('ContentType', 'unknown')
                print(f"Content-Type: {content_type}")
            except Exception as e:
                print(f"Error getting metadata: {str(e)}")

        processed_count += 1

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {processed_count} events',
            'timestamp': datetime.utcnow().isoformat()
        })
    }
EOF

# Create deployment package
cd scripts
zip lambda_function.zip lambda_function.py
cd ..

# Create Lambda function
aws lambda create-function \
    --function-name S3EventProcessor-${SUFFIX} \
    --runtime python3.11 \
    --role arn:aws:iam::${ACCOUNT_ID}:role/S3EventLambdaRole-${SUFFIX} \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://scripts/lambda_function.zip \
    --timeout 30 \
    --memory-size 128

echo "Lambda function created"
```

### Step 6.3: Add Lambda Permission for S3

```bash
# Allow S3 to invoke Lambda
aws lambda add-permission \
    --function-name S3EventProcessor-${SUFFIX} \
    --principal s3.amazonaws.com \
    --statement-id S3InvokeLambda-${SUFFIX} \
    --action "lambda:InvokeFunction" \
    --source-arn arn:aws:s3:::${MAIN_BUCKET} \
    --source-account ${ACCOUNT_ID}

echo "Lambda permission added"
```

### Step 6.4: Configure S3 Event Notification

```bash
# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name S3EventProcessor-${SUFFIX} \
    --query 'Configuration.FunctionArn' \
    --output text)

# Create notification configuration
cat > /tmp/notification-config.json << EOF
{
    "LambdaFunctionConfigurations": [
        {
            "Id": "ProcessUploads",
            "LambdaFunctionArn": "${LAMBDA_ARN}",
            "Events": ["s3:ObjectCreated:*"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "events/"}
                    ]
                }
            }
        }
    ]
}
EOF

# Apply notification configuration
aws s3api put-bucket-notification-configuration \
    --bucket ${MAIN_BUCKET} \
    --notification-configuration file:///tmp/notification-config.json

# Verify configuration
aws s3api get-bucket-notification-configuration --bucket ${MAIN_BUCKET}

echo "Event notification configured"
```

### Step 6.5: Test Event Notifications

```bash
# Upload files to trigger events
echo "Test event file 1" > data/event-test-1.txt
echo "Test event file 2" > data/event-test-2.txt

aws s3 cp data/event-test-1.txt s3://${MAIN_BUCKET}/events/
aws s3 cp data/event-test-2.txt s3://${MAIN_BUCKET}/events/

echo "Files uploaded. Checking Lambda logs..."
sleep 10

# View Lambda logs
aws logs tail /aws/lambda/S3EventProcessor-${SUFFIX} --since 5m
```

### Step 6.6: View Event Processing Results

```bash
# Get recent log events
aws logs filter-log-events \
    --log-group-name /aws/lambda/S3EventProcessor-${SUFFIX} \
    --start-time $(($(date +%s) - 300))000 \
    --query 'events[*].message' \
    --output text
```

### Event Flow Diagram

```
Event Notification Flow:

+------------------+     +-----------------+     +------------------+
|  Upload to       | --> | S3 Event        | --> | Lambda Function  |
|  events/ prefix  |     | Notification    |     | Processing       |
+------------------+     +-----------------+     +------------------+
                                                         |
                                                         v
                                               +------------------+
                                               | CloudWatch Logs  |
                                               +------------------+
```

### Checkpoint 6
```
Verify:
[ ] Lambda role created
[ ] Lambda function deployed
[ ] S3 can invoke Lambda
[ ] Event notification configured
[ ] Uploads trigger Lambda
[ ] Logs show event processing
```

---

## Lab 7: S3 Batch Operations

### Objectives
- Create inventory configuration
- Set up batch operations
- Execute batch job to tag objects

### Step 7.1: Create Inventory Configuration

```bash
# Create inventory destination prefix
aws s3api put-object \
    --bucket ${MAIN_BUCKET} \
    --key inventory/.placeholder \
    --body /dev/null

# Configure inventory (runs weekly, results available next day)
aws s3api put-bucket-inventory-configuration \
    --bucket ${MAIN_BUCKET} \
    --id "FullInventory" \
    --inventory-configuration '{
        "Id": "FullInventory",
        "IsEnabled": true,
        "Destination": {
            "S3BucketDestination": {
                "Bucket": "arn:aws:s3:::'${MAIN_BUCKET}'",
                "Format": "CSV",
                "Prefix": "inventory"
            }
        },
        "Schedule": {
            "Frequency": "Weekly"
        },
        "IncludedObjectVersions": "Current",
        "OptionalFields": ["Size", "LastModifiedDate", "StorageClass", "ETag"]
    }'

echo "Inventory configuration created (results available in ~24-48 hours)"
```

### Step 7.2: Create IAM Role for Batch Operations

```bash
# Create batch operations trust policy
cat > /tmp/batch-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "batchoperations.s3.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role \
    --role-name S3BatchOperationsRole-${SUFFIX} \
    --assume-role-policy-document file:///tmp/batch-trust-policy.json

# Create permission policy
cat > /tmp/batch-permissions.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObjectTagging",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:GetObjectTagging",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::${MAIN_BUCKET}",
                "arn:aws:s3:::${MAIN_BUCKET}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::${MAIN_BUCKET}/batch-reports/*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name S3BatchOperationsRole-${SUFFIX} \
    --policy-name S3BatchOperationsPolicy \
    --policy-document file:///tmp/batch-permissions.json

echo "Batch operations IAM role created"
sleep 10
```

### Step 7.3: Create Manifest File

```bash
# Create a simple manifest file listing objects to process
# Format: bucket,key

cat > data/manifest.csv << EOF
${MAIN_BUCKET},documents/hello.txt
${MAIN_BUCKET},documents/file1.txt
${MAIN_BUCKET},documents/file2.txt
EOF

# Upload manifest
aws s3 cp data/manifest.csv s3://${MAIN_BUCKET}/batch-jobs/

echo "Manifest file uploaded"
```

### Step 7.4: Create Batch Job

```bash
# Create batch job to add tags to objects
BATCH_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/S3BatchOperationsRole-${SUFFIX}"

aws s3control create-job \
    --account-id ${ACCOUNT_ID} \
    --confirmation-required \
    --operation '{
        "S3PutObjectTagging": {
            "TagSet": [
                {"Key": "ProcessedBy", "Value": "BatchOperation"},
                {"Key": "BatchDate", "Value": "'$(date +%Y-%m-%d)'"}
            ]
        }
    }' \
    --manifest '{
        "Spec": {
            "Format": "S3BatchOperations_CSV_20180820",
            "Fields": ["Bucket", "Key"]
        },
        "Location": {
            "ObjectArn": "arn:aws:s3:::'${MAIN_BUCKET}'/batch-jobs/manifest.csv",
            "ETag": "'$(aws s3api head-object --bucket ${MAIN_BUCKET} --key batch-jobs/manifest.csv --query ETag --output text)'"
        }
    }' \
    --report '{
        "Bucket": "arn:aws:s3:::'${MAIN_BUCKET}'",
        "Prefix": "batch-reports",
        "Format": "Report_CSV_20180820",
        "Enabled": true,
        "ReportScope": "AllTasks"
    }' \
    --priority 10 \
    --role-arn ${BATCH_ROLE_ARN} \
    --region ${AWS_REGION}

echo "Batch job created (requires confirmation)"
```

### Step 7.5: List and Confirm Batch Job

```bash
# List batch jobs
aws s3control list-jobs \
    --account-id ${ACCOUNT_ID} \
    --job-statuses Suspended \
    --output table

# Get job ID
JOB_ID=$(aws s3control list-jobs \
    --account-id ${ACCOUNT_ID} \
    --job-statuses Suspended \
    --query 'Jobs[0].JobId' \
    --output text)

echo "Job ID: ${JOB_ID}"

# Confirm and run the job
if [ "${JOB_ID}" != "None" ]; then
    aws s3control update-job-status \
        --account-id ${ACCOUNT_ID} \
        --job-id ${JOB_ID} \
        --requested-job-status Ready
    echo "Job confirmed and started"
fi
```

### Step 7.6: Monitor Batch Job

```bash
# Check job status
if [ "${JOB_ID}" != "None" ]; then
    aws s3control describe-job \
        --account-id ${ACCOUNT_ID} \
        --job-id ${JOB_ID} \
        --query 'Job.{Status:Status,ProgressSummary:ProgressSummary}' \
        --output table
fi

# Wait and verify tags were applied
sleep 30

# Check tags on processed objects
aws s3api get-object-tagging \
    --bucket ${MAIN_BUCKET} \
    --key documents/hello.txt

echo "Batch operation complete"
```

### Checkpoint 7
```
Verify:
[ ] Inventory configuration created
[ ] Batch operations role created
[ ] Manifest file uploaded
[ ] Batch job created
[ ] Job confirmed and executed
[ ] Tags applied to objects
```

---

## Lab 8: Cleanup

### Important: Complete cleanup to avoid ongoing charges

### Step 8.1: Delete Event Notification

```bash
# Remove event notification
aws s3api put-bucket-notification-configuration \
    --bucket ${MAIN_BUCKET} \
    --notification-configuration '{}'

echo "Event notifications removed"
```

### Step 8.2: Delete Lambda Function

```bash
# Delete Lambda function
aws lambda delete-function \
    --function-name S3EventProcessor-${SUFFIX}

# Delete Lambda log group
aws logs delete-log-group \
    --log-group-name /aws/lambda/S3EventProcessor-${SUFFIX} 2>/dev/null || true

echo "Lambda function deleted"
```

### Step 8.3: Delete Replication Configuration

```bash
# Delete replication configuration
aws s3api delete-bucket-replication --bucket ${MAIN_BUCKET}

echo "Replication configuration deleted"
```

### Step 8.4: Empty and Delete Buckets

```bash
# Function to empty versioned bucket
empty_versioned_bucket() {
    local bucket=$1
    local region=${2:-us-east-1}

    echo "Emptying bucket: ${bucket}"

    # Delete all object versions
    aws s3api list-object-versions \
        --bucket ${bucket} \
        --region ${region} \
        --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
        --output json > /tmp/versions.json

    if [ -s /tmp/versions.json ] && [ "$(cat /tmp/versions.json)" != '{"Objects": null}' ]; then
        aws s3api delete-objects \
            --bucket ${bucket} \
            --region ${region} \
            --delete file:///tmp/versions.json 2>/dev/null || true
    fi

    # Delete all delete markers
    aws s3api list-object-versions \
        --bucket ${bucket} \
        --region ${region} \
        --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
        --output json > /tmp/markers.json

    if [ -s /tmp/markers.json ] && [ "$(cat /tmp/markers.json)" != '{"Objects": null}' ]; then
        aws s3api delete-objects \
            --bucket ${bucket} \
            --region ${region} \
            --delete file:///tmp/markers.json 2>/dev/null || true
    fi
}

# Empty main bucket
empty_versioned_bucket ${MAIN_BUCKET}

# Empty and delete replica bucket
empty_versioned_bucket ${REPLICA_BUCKET} ${DEST_REGION}
aws s3api delete-bucket --bucket ${REPLICA_BUCKET} --region ${DEST_REGION}
echo "Replica bucket deleted"

# Delete main bucket
aws s3api delete-bucket --bucket ${MAIN_BUCKET}
echo "Main bucket deleted"

# Empty and delete logs bucket
aws s3 rm s3://${LOGS_BUCKET}/ --recursive
aws s3api delete-bucket --bucket ${LOGS_BUCKET}
echo "Logs bucket deleted"

# Empty and delete website bucket
aws s3 rm s3://${WEBSITE_BUCKET}/ --recursive
aws s3api delete-bucket --bucket ${WEBSITE_BUCKET}
echo "Website bucket deleted"
```

### Step 8.5: Delete IAM Roles

```bash
# Delete replication role
aws iam delete-role-policy \
    --role-name S3ReplicationRole-${SUFFIX} \
    --policy-name S3ReplicationPolicy
aws iam delete-role --role-name S3ReplicationRole-${SUFFIX}

# Delete Lambda role
aws iam delete-role-policy \
    --role-name S3EventLambdaRole-${SUFFIX} \
    --policy-name S3EventLambdaPolicy
aws iam delete-role --role-name S3EventLambdaRole-${SUFFIX}

# Delete batch operations role
aws iam delete-role-policy \
    --role-name S3BatchOperationsRole-${SUFFIX} \
    --policy-name S3BatchOperationsPolicy
aws iam delete-role --role-name S3BatchOperationsRole-${SUFFIX}

echo "IAM roles deleted"
```

### Step 8.6: Clean Local Files

```bash
# Remove lab directory
cd ~
rm -rf ~/s3-lab
rm -f /tmp/versions.json /tmp/markers.json
rm -f /tmp/*.json

echo "Local cleanup complete"
```

### Step 8.7: Verify Cleanup

```bash
# Verify buckets are deleted
echo "Checking for remaining buckets..."
aws s3 ls 2>/dev/null | grep -E "${SUFFIX}" || echo "No lab buckets found"

# Verify roles are deleted
echo "Checking for remaining IAM roles..."
aws iam list-roles --query "Roles[?contains(RoleName, '${SUFFIX}')]" --output text || echo "No lab roles found"

echo "Cleanup verification complete!"
```

### Cleanup Checklist
```
Final Verification:
[ ] Event notifications removed
[ ] Lambda function deleted
[ ] Lambda log group deleted
[ ] Replication configuration removed
[ ] All buckets emptied and deleted
  [ ] Main bucket
  [ ] Replica bucket
  [ ] Logs bucket
  [ ] Website bucket
[ ] All IAM roles deleted
  [ ] Replication role
  [ ] Lambda role
  [ ] Batch operations role
[ ] Local files cleaned up
```

---

## Lab Summary

### What You Learned

| Lab | Skills Acquired |
|-----|----------------|
| **Setup** | Environment configuration, AWS CLI |
| **Buckets** | Encryption, logging, Block Public Access, tagging |
| **Website** | Static hosting, bucket policies, public access |
| **Versioning** | Version management, lifecycle policies |
| **Replication** | CRR setup, IAM roles, replication rules |
| **Events** | Lambda integration, event notifications |
| **Batch** | Inventory, batch operations, manifest files |
| **Cleanup** | Resource deletion, versioned bucket cleanup |

### Key Takeaways

1. **Security First:** Always enable encryption and Block Public Access by default
2. **Versioning:** Essential for data protection and recovery
3. **Lifecycle Policies:** Automate cost optimization with transitions and expirations
4. **Replication:** Requires versioning and proper IAM configuration
5. **Event-Driven:** S3 events enable powerful serverless architectures
6. **Batch Operations:** Efficient for large-scale object management

### Next Steps

1. Review the quiz to test your knowledge
2. Explore advanced topics like S3 Object Lambda
3. Practice with real-world scenarios
4. Consider AWS certification preparation

---

## Troubleshooting Guide

### Common Issues

| Issue | Solution |
|-------|----------|
| Bucket name already exists | Add unique suffix (timestamp) |
| Access denied on bucket | Check IAM permissions and bucket policy |
| Replication not working | Verify versioning enabled on both buckets |
| Lambda not triggering | Check Lambda permission and event configuration |
| Cannot delete bucket | Empty all versions and delete markers first |

### Useful Commands

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket BUCKET_NAME

# Check bucket ACL
aws s3api get-bucket-acl --bucket BUCKET_NAME

# List all versions
aws s3api list-object-versions --bucket BUCKET_NAME

# Force delete all versions
aws s3 rb s3://BUCKET_NAME --force  # Doesn't work for versioned buckets

# Check S3 service quotas
aws service-quotas get-service-quota \
    --service-code s3 \
    --quota-code L-DC2B2D3D
```

---

## Additional Resources

- [S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)
- [S3 CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [S3 FAQ](https://aws.amazon.com/s3/faqs/)
