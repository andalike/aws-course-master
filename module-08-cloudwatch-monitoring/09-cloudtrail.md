# AWS CloudTrail

## Introduction

AWS CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It records API calls made to AWS services, providing a complete history of AWS API activity in your account. CloudTrail is essential for security analysis, resource change tracking, and compliance auditing.

---

## CloudTrail Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS CloudTrail Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           API Activity Sources                          ││
│  │                                                                          ││
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 ││
│  │   │AWS Console   │  │  AWS CLI     │  │   AWS SDK    │                 ││
│  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 ││
│  │          │                  │                  │                         ││
│  │          └──────────────────┼──────────────────┘                         ││
│  │                             ▼                                            ││
│  │                    ┌─────────────────┐                                   ││
│  │                    │   AWS APIs      │                                   ││
│  │                    └────────┬────────┘                                   ││
│  └─────────────────────────────┼────────────────────────────────────────────┘│
│                                │                                             │
│                                ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           CloudTrail                                     ││
│  │                                                                          ││
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 ││
│  │   │  Management  │  │    Data      │  │   Insights   │                 ││
│  │   │   Events     │  │   Events     │  │   Events     │                 ││
│  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 ││
│  │          │                  │                  │                         ││
│  │          └──────────────────┼──────────────────┘                         ││
│  │                             ▼                                            ││
│  │                    ┌─────────────────┐                                   ││
│  │                    │     Trail       │                                   ││
│  │                    └────────┬────────┘                                   ││
│  └─────────────────────────────┼────────────────────────────────────────────┘│
│                                │                                             │
│            ┌───────────────────┼───────────────────┐                        │
│            ▼                   ▼                   ▼                        │
│     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │
│     │     S3       │   │  CloudWatch  │   │    SNS       │                 │
│     │   Bucket     │   │    Logs      │   │   Topics     │                 │
│     └──────────────┘   └──────────────┘   └──────────────┘                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### What CloudTrail Records

Every API call recorded includes:

| Field | Description |
|-------|-------------|
| Event time | When the API call was made |
| User identity | Who made the call (IAM user, role, service) |
| Event source | Which AWS service received the request |
| Event name | The API action performed |
| AWS region | Where the call was processed |
| Source IP | IP address of the caller |
| Request parameters | Input parameters for the API call |
| Response elements | Output of the API call |

### Sample CloudTrail Event

```json
{
    "eventVersion": "1.08",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAEXAMPLEUSERID",
        "arn": "arn:aws:iam::123456789012:user/alice",
        "accountId": "123456789012",
        "accessKeyId": "AKIAEXAMPLEKEYID",
        "userName": "alice",
        "sessionContext": {
            "sessionIssuer": {},
            "webIdFederationData": {},
            "attributes": {
                "creationDate": "2024-01-15T10:00:00Z",
                "mfaAuthenticated": "true"
            }
        }
    },
    "eventTime": "2024-01-15T10:30:45Z",
    "eventSource": "ec2.amazonaws.com",
    "eventName": "StopInstances",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "203.0.113.50",
    "userAgent": "aws-cli/2.13.0 Python/3.11.4",
    "requestParameters": {
        "instancesSet": {
            "items": [
                {
                    "instanceId": "i-1234567890abcdef0"
                }
            ]
        }
    },
    "responseElements": {
        "instancesSet": {
            "items": [
                {
                    "instanceId": "i-1234567890abcdef0",
                    "currentState": {
                        "code": 64,
                        "name": "stopping"
                    },
                    "previousState": {
                        "code": 16,
                        "name": "running"
                    }
                }
            ]
        }
    },
    "requestID": "abc123-def456-ghi789",
    "eventID": "12345678-1234-1234-1234-123456789012",
    "readOnly": false,
    "eventType": "AwsApiCall",
    "managementEvent": true,
    "recipientAccountId": "123456789012",
    "eventCategory": "Management"
}
```

---

## Event Types

### Management Events (Control Plane)

Management events provide visibility into operations performed on resources in your AWS account.

**Examples:**
- Creating or deleting S3 buckets
- Starting or stopping EC2 instances
- Creating IAM users or roles
- Attaching policies
- Configuring security groups

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Management Events                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Write Events (modify resources)           Read Events (describe/list)     │
│   ┌─────────────────────────────────┐      ┌────────────────────────────┐   │
│   │ CreateBucket                    │      │ DescribeInstances          │   │
│   │ DeleteBucket                    │      │ ListBuckets                │   │
│   │ PutBucketPolicy                 │      │ GetBucketPolicy            │   │
│   │ RunInstances                    │      │ DescribeSecurityGroups     │   │
│   │ TerminateInstances              │      │ ListUsers                  │   │
│   │ CreateUser                      │      │ GetUser                    │   │
│   │ AttachRolePolicy                │      │ ListRoles                  │   │
│   └─────────────────────────────────┘      └────────────────────────────┘   │
│                                                                              │
│   Logging: Enabled by default              Logging: Optional (high volume)  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Events (Data Plane)

Data events provide visibility into resource operations performed on or within a resource.

**Supported Resources:**
- S3 object-level operations (GetObject, PutObject, DeleteObject)
- Lambda function invocations
- DynamoDB item-level operations
- S3 Object Lambda access points
- EBS direct APIs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Events                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   S3 Data Events                            Lambda Data Events               │
│   ┌─────────────────────────────────┐      ┌────────────────────────────┐   │
│   │ s3:GetObject                    │      │ lambda:Invoke              │   │
│   │ s3:PutObject                    │      │                            │   │
│   │ s3:DeleteObject                 │      │ Records each function      │   │
│   │ s3:GetObjectAcl                 │      │ invocation with request    │   │
│   │ s3:PutObjectAcl                 │      │ and response details       │   │
│   └─────────────────────────────────┘      └────────────────────────────┘   │
│                                                                              │
│   DynamoDB Data Events                      Note: Data events are           │
│   ┌─────────────────────────────────┐      high-volume and incur           │
│   │ dynamodb:GetItem                │      additional costs. Enable        │
│   │ dynamodb:PutItem                │      selectively for critical        │
│   │ dynamodb:DeleteItem             │      resources only.                 │
│   │ dynamodb:UpdateItem             │                                      │
│   │ dynamodb:Query                  │                                      │
│   │ dynamodb:Scan                   │                                      │
│   └─────────────────────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Insights Events

CloudTrail Insights analyzes management events for unusual activity patterns.

**Detects:**
- Unusual API call rates
- Unusual error rates
- Anomalous user behavior

```json
{
    "eventVersion": "1.08",
    "eventTime": "2024-01-15T10:30:00Z",
    "eventSource": "cloudtrail.amazonaws.com",
    "eventName": "CloudTrailInsightsEvent",
    "insightDetails": {
        "state": "Start",
        "eventSource": "ec2.amazonaws.com",
        "eventName": "RunInstances",
        "insightType": "ApiCallRateInsight",
        "insightContext": {
            "statistics": {
                "baseline": {
                    "average": 5.0
                },
                "insight": {
                    "average": 150.0
                }
            }
        }
    }
}
```

---

## Trail Configuration

### Trail Types

| Trail Type | Scope | Use Case |
|------------|-------|----------|
| Single-region | One AWS region | Development, testing |
| Multi-region | All AWS regions | Production, compliance |
| Organization | All accounts in org | Enterprise governance |

### Creating a Trail

#### Using AWS Console

1. Navigate to CloudTrail console
2. Click "Create trail"
3. Configure trail settings:
   - Trail name
   - Storage location (S3 bucket)
   - Log file encryption (optional)
   - Log file validation
4. Choose events to log
5. Review and create

#### Using AWS CLI

```bash
# Create a multi-region trail
aws cloudtrail create-trail \
    --name my-production-trail \
    --s3-bucket-name my-cloudtrail-logs-bucket \
    --is-multi-region-trail \
    --enable-log-file-validation \
    --include-global-service-events \
    --kms-key-id alias/cloudtrail-key

# Start logging
aws cloudtrail start-logging --name my-production-trail

# Enable Insights
aws cloudtrail put-insight-selectors \
    --trail-name my-production-trail \
    --insight-selectors '[{"InsightType": "ApiCallRateInsight"}, {"InsightType": "ApiErrorRateInsight"}]'
```

#### Using CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: CloudTrail Configuration

Parameters:
  TrailName:
    Type: String
    Default: organization-trail

Resources:
  # S3 Bucket for CloudTrail Logs
  CloudTrailBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      BucketName: !Sub '${AWS::AccountId}-cloudtrail-logs'
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: 'aws:kms'
              KMSMasterKeyID: !Ref CloudTrailKey
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: ArchiveOldLogs
            Status: Enabled
            Transitions:
              - StorageClass: GLACIER
                TransitionInDays: 90
            ExpirationInDays: 365

  # Bucket Policy for CloudTrail
  CloudTrailBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref CloudTrailBucket
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: AWSCloudTrailAclCheck
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: s3:GetBucketAcl
            Resource: !GetAtt CloudTrailBucket.Arn
          - Sid: AWSCloudTrailWrite
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: s3:PutObject
            Resource: !Sub '${CloudTrailBucket.Arn}/*'
            Condition:
              StringEquals:
                's3:x-amz-acl': 'bucket-owner-full-control'

  # KMS Key for CloudTrail Encryption
  CloudTrailKey:
    Type: AWS::KMS::Key
    Properties:
      Description: KMS key for CloudTrail log encryption
      EnableKeyRotation: true
      KeyPolicy:
        Version: '2012-10-17'
        Statement:
          - Sid: Enable IAM User Permissions
            Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
            Action: 'kms:*'
            Resource: '*'
          - Sid: Allow CloudTrail to encrypt logs
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action:
              - 'kms:GenerateDataKey*'
              - 'kms:DescribeKey'
            Resource: '*'
          - Sid: Allow CloudTrail to describe key
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: 'kms:DescribeKey'
            Resource: '*'

  # CloudWatch Log Group for CloudTrail
  CloudTrailLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/cloudtrail/${TrailName}'
      RetentionInDays: 90

  # IAM Role for CloudTrail to CloudWatch Logs
  CloudTrailCloudWatchRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${TrailName}-cloudwatch-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: 'sts:AssumeRole'
      Policies:
        - PolicyName: CloudTrailCloudWatchPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'logs:CreateLogStream'
                  - 'logs:PutLogEvents'
                Resource: !GetAtt CloudTrailLogGroup.Arn

  # CloudTrail Trail
  CloudTrail:
    Type: AWS::CloudTrail::Trail
    DependsOn:
      - CloudTrailBucketPolicy
    Properties:
      TrailName: !Ref TrailName
      S3BucketName: !Ref CloudTrailBucket
      IsMultiRegionTrail: true
      IncludeGlobalServiceEvents: true
      EnableLogFileValidation: true
      IsLogging: true
      KMSKeyId: !Ref CloudTrailKey
      CloudWatchLogsLogGroupArn: !GetAtt CloudTrailLogGroup.Arn
      CloudWatchLogsRoleArn: !GetAtt CloudTrailCloudWatchRole.Arn
      EventSelectors:
        - ReadWriteType: All
          IncludeManagementEvents: true
          DataResources:
            - Type: AWS::S3::Object
              Values:
                - 'arn:aws:s3:::my-sensitive-bucket/'
            - Type: AWS::Lambda::Function
              Values:
                - 'arn:aws:lambda'
      InsightSelectors:
        - InsightType: ApiCallRateInsight
        - InsightType: ApiErrorRateInsight

Outputs:
  TrailArn:
    Value: !GetAtt CloudTrail.Arn
    Description: CloudTrail ARN
  BucketName:
    Value: !Ref CloudTrailBucket
    Description: S3 Bucket for CloudTrail logs
  LogGroupName:
    Value: !Ref CloudTrailLogGroup
    Description: CloudWatch Log Group for CloudTrail
```

---

## Log File Integrity Validation

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Log File Integrity Validation                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Hour 1                    Hour 2                    Hour 3                 │
│  ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐    │
│  │ Log File 1       │     │ Log File 3       │     │ Log File 5       │    │
│  │ Log File 2       │     │ Log File 4       │     │ Log File 6       │    │
│  │                  │     │                  │     │                  │    │
│  │ Hash: abc123...  │     │ Hash: def456...  │     │ Hash: ghi789...  │    │
│  │ Hash: xyz789...  │     │ Hash: uvw012...  │     │ Hash: jkl345...  │    │
│  └────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘    │
│           │                        │                        │               │
│           └────────────────────────┼────────────────────────┘               │
│                                    │                                        │
│                                    ▼                                        │
│                           ┌────────────────┐                                │
│                           │  Digest File   │                                │
│                           │                │                                │
│                           │ Contains:      │                                │
│                           │ - Log hashes   │                                │
│                           │ - Previous     │                                │
│                           │   digest hash  │                                │
│                           │ - Signature    │                                │
│                           └────────────────┘                                │
│                                                                              │
│  Digest files are delivered hourly and contain:                             │
│  - SHA-256 hashes of each log file delivered in that hour                  │
│  - Hash of the previous digest file (chain)                                │
│  - Digital signature for tamper detection                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Validating Log Integrity

```bash
# Validate log files using AWS CLI
aws cloudtrail validate-logs \
    --trail-arn arn:aws:cloudtrail:us-east-1:123456789012:trail/my-trail \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-15T23:59:59Z

# Output shows validation results
# Validating log files for trail arn:aws:cloudtrail:us-east-1:123456789012:trail/my-trail between 2024-01-01T00:00:00Z and 2024-01-15T23:59:59Z

# Results:
# Log files validated: 720
# Log files invalid: 0
# Digest files validated: 360
# Digest files invalid: 0
```

### Sample Digest File

```json
{
    "digestStartTime": "2024-01-15T10:00:00Z",
    "digestEndTime": "2024-01-15T11:00:00Z",
    "digestS3Bucket": "my-cloudtrail-logs-bucket",
    "digestS3Object": "AWSLogs/123456789012/CloudTrail-Digest/us-east-1/2024/01/15/123456789012_CloudTrail-Digest_us-east-1_my-trail_us-east-1_20240115T110000Z.json.gz",
    "previousDigestS3Bucket": "my-cloudtrail-logs-bucket",
    "previousDigestS3Object": "AWSLogs/123456789012/CloudTrail-Digest/...",
    "previousDigestHashValue": "abcdef123456...",
    "previousDigestHashAlgorithm": "SHA-256",
    "previousDigestSignature": "...",
    "logFiles": [
        {
            "s3Bucket": "my-cloudtrail-logs-bucket",
            "s3Object": "AWSLogs/123456789012/CloudTrail/us-east-1/2024/01/15/...",
            "hashValue": "1234567890abcdef...",
            "hashAlgorithm": "SHA-256"
        }
    ]
}
```

---

## Integration with CloudWatch Logs

### Benefits of Integration

1. **Real-time monitoring**: Query and alert on API activity in near real-time
2. **Metric filters**: Create custom metrics from CloudTrail events
3. **Logs Insights**: Analyze API patterns and anomalies
4. **Retention**: Independent retention from S3

### Setting Up CloudWatch Integration

```bash
# Create log group
aws logs create-log-group \
    --log-group-name /aws/cloudtrail/my-trail

# Create IAM role for CloudTrail
aws iam create-role \
    --role-name CloudTrailCloudWatchLogsRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach policy
aws iam put-role-policy \
    --role-name CloudTrailCloudWatchLogsRole \
    --policy-name CloudTrailCloudWatchLogsPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/cloudtrail/my-trail:*"
        }]
    }'

# Update trail
aws cloudtrail update-trail \
    --name my-trail \
    --cloud-watch-logs-log-group-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/cloudtrail/my-trail \
    --cloud-watch-logs-role-arn arn:aws:iam::123456789012:role/CloudTrailCloudWatchLogsRole
```

### Metric Filters for Security Monitoring

```bash
# Create metric filter for root user activity
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail/my-trail \
    --filter-name RootUserActivity \
    --filter-pattern '{ $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" }' \
    --metric-transformations \
        metricName=RootUserActivityCount,metricNamespace=CloudTrailMetrics,metricValue=1

# Create metric filter for unauthorized API calls
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail/my-trail \
    --filter-name UnauthorizedAPICalls \
    --filter-pattern '{ ($.errorCode = "*UnauthorizedAccess*") || ($.errorCode = "AccessDenied*") }' \
    --metric-transformations \
        metricName=UnauthorizedAPICallsCount,metricNamespace=CloudTrailMetrics,metricValue=1

# Create metric filter for console login without MFA
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail/my-trail \
    --filter-name ConsoleLoginWithoutMFA \
    --filter-pattern '{ ($.eventName = "ConsoleLogin") && ($.additionalEventData.MFAUsed != "Yes") }' \
    --metric-transformations \
        metricName=ConsoleLoginWithoutMFACount,metricNamespace=CloudTrailMetrics,metricValue=1

# Create metric filter for IAM policy changes
aws logs put-metric-filter \
    --log-group-name /aws/cloudtrail/my-trail \
    --filter-name IAMPolicyChanges \
    --filter-pattern '{ ($.eventName = DeleteGroupPolicy) || ($.eventName = DeleteRolePolicy) || ($.eventName = DeleteUserPolicy) || ($.eventName = PutGroupPolicy) || ($.eventName = PutRolePolicy) || ($.eventName = PutUserPolicy) || ($.eventName = CreatePolicy) || ($.eventName = DeletePolicy) || ($.eventName = CreatePolicyVersion) || ($.eventName = DeletePolicyVersion) || ($.eventName = AttachRolePolicy) || ($.eventName = DetachRolePolicy) || ($.eventName = AttachUserPolicy) || ($.eventName = DetachUserPolicy) || ($.eventName = AttachGroupPolicy) || ($.eventName = DetachGroupPolicy) }' \
    --metric-transformations \
        metricName=IAMPolicyChangesCount,metricNamespace=CloudTrailMetrics,metricValue=1
```

### CloudWatch Alarms for CloudTrail Events

```bash
# Alarm for root user activity
aws cloudwatch put-metric-alarm \
    --alarm-name RootUserActivityAlarm \
    --alarm-description "Alert when root user is used" \
    --metric-name RootUserActivityCount \
    --namespace CloudTrailMetrics \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:security-alerts

# Alarm for unauthorized API calls
aws cloudwatch put-metric-alarm \
    --alarm-name UnauthorizedAPICallsAlarm \
    --alarm-description "Alert on unauthorized API call attempts" \
    --metric-name UnauthorizedAPICallsCount \
    --namespace CloudTrailMetrics \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:security-alerts
```

---

## Querying CloudTrail with Logs Insights

### Common Queries

```sql
-- Find all API calls by a specific user
fields @timestamp, eventName, eventSource, sourceIPAddress
| filter userIdentity.userName = "alice"
| sort @timestamp desc
| limit 100

-- Find failed API calls
fields @timestamp, eventName, errorCode, errorMessage, userIdentity.arn
| filter ispresent(errorCode)
| sort @timestamp desc
| limit 100

-- Root user activity
fields @timestamp, eventName, eventSource, sourceIPAddress, userAgent
| filter userIdentity.type = "Root"
| sort @timestamp desc

-- Console logins
fields @timestamp, userIdentity.arn, sourceIPAddress, responseElements.ConsoleLogin
| filter eventName = "ConsoleLogin"
| sort @timestamp desc
| limit 50

-- Security group changes
fields @timestamp, eventName, userIdentity.arn, requestParameters.groupId
| filter eventSource = "ec2.amazonaws.com"
    and (eventName = "AuthorizeSecurityGroupIngress"
         or eventName = "AuthorizeSecurityGroupEgress"
         or eventName = "RevokeSecurityGroupIngress"
         or eventName = "RevokeSecurityGroupEgress")
| sort @timestamp desc

-- S3 bucket policy changes
fields @timestamp, eventName, userIdentity.arn, requestParameters.bucketName
| filter eventSource = "s3.amazonaws.com"
    and (eventName = "PutBucketPolicy"
         or eventName = "DeleteBucketPolicy"
         or eventName = "PutBucketAcl")
| sort @timestamp desc

-- Count API calls by service
stats count(*) as apiCalls by eventSource
| sort apiCalls desc
| limit 20

-- API call patterns over time
stats count(*) as calls by bin(1h)
| sort @timestamp asc

-- Top API callers
stats count(*) as calls by userIdentity.arn
| sort calls desc
| limit 10

-- API calls from specific IP range
fields @timestamp, eventName, userIdentity.arn
| filter isIpInSubnet(sourceIPAddress, "10.0.0.0/8")
| sort @timestamp desc
| limit 100
```

---

## CloudTrail Insights

### Enabling Insights

```bash
# Enable Insights on existing trail
aws cloudtrail put-insight-selectors \
    --trail-name my-trail \
    --insight-selectors '[
        {"InsightType": "ApiCallRateInsight"},
        {"InsightType": "ApiErrorRateInsight"}
    ]'

# Check Insights status
aws cloudtrail get-insight-selectors --trail-name my-trail
```

### Insight Types

| Type | Description | Use Case |
|------|-------------|----------|
| ApiCallRateInsight | Unusual API call volume | Detect automation issues, attacks |
| ApiErrorRateInsight | Unusual error rates | Identify permission problems, service issues |

### Viewing Insights

```bash
# List recent insights
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=CloudTrailInsightsEvent \
    --max-results 20
```

---

## Organization Trails

### Benefits

- Single trail for all accounts
- Centralized log storage
- Consistent configuration
- Simplified compliance

### Creating Organization Trail

```bash
# Must be run from management account
aws cloudtrail create-trail \
    --name organization-trail \
    --s3-bucket-name org-cloudtrail-logs \
    --is-organization-trail \
    --is-multi-region-trail \
    --enable-log-file-validation
```

### CloudFormation for Organization Trail

```yaml
Resources:
  OrganizationTrail:
    Type: AWS::CloudTrail::Trail
    Properties:
      TrailName: organization-trail
      S3BucketName: !Ref OrgTrailBucket
      IsOrganizationTrail: true
      IsMultiRegionTrail: true
      IncludeGlobalServiceEvents: true
      EnableLogFileValidation: true
      IsLogging: true
```

---

## Best Practices

### Security

1. **Enable in all regions**: Attackers may operate in regions you don't normally use
2. **Enable log file validation**: Detect tampering with log files
3. **Encrypt log files**: Use KMS for encryption at rest
4. **Restrict access**: Use IAM policies to control who can modify trails
5. **Enable MFA delete**: Protect S3 bucket with MFA delete

### Operations

1. **Send to CloudWatch Logs**: Enable real-time monitoring
2. **Create metric filters**: Alert on critical events
3. **Set appropriate retention**: Balance cost and compliance needs
4. **Use lifecycle policies**: Transition old logs to cheaper storage

### Cost Optimization

1. **Exclude read-only events**: If not needed for compliance
2. **Be selective with data events**: They generate high volume
3. **Use lifecycle policies**: Archive to Glacier for long-term storage

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No logs in S3 | Bucket policy incorrect | Verify CloudTrail has write access |
| Logs delayed | Normal behavior | Logs are delivered within 15 minutes |
| Missing events | Wrong event type | Check management vs data events |
| Validation fails | Files modified | Investigate potential tampering |

### Debugging Commands

```bash
# Check trail status
aws cloudtrail get-trail-status --name my-trail

# Verify trail configuration
aws cloudtrail describe-trails --trail-name-list my-trail

# Check recent events
aws cloudtrail lookup-events --max-results 10

# Validate log files
aws cloudtrail validate-logs \
    --trail-arn arn:aws:cloudtrail:us-east-1:123456789012:trail/my-trail \
    --start-time $(date -d '24 hours ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds)
```

---

## Pricing

| Component | Cost |
|-----------|------|
| Management events (first copy) | Free |
| Management events (additional copies) | $2.00 per 100,000 events |
| Data events | $0.10 per 100,000 events |
| Insights events | $0.35 per 100,000 events analyzed |
| S3 storage | Standard S3 pricing |

---

## Hands-On: Setting Up CloudTrail

### Step 1: Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://my-account-cloudtrail-logs-$(aws sts get-caller-identity --query Account --output text)

# Create bucket policy
cat > /tmp/bucket-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::my-account-cloudtrail-logs-ACCOUNT_ID"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::my-account-cloudtrail-logs-ACCOUNT_ID/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
EOF

# Apply policy (replace ACCOUNT_ID)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
sed -i "s/ACCOUNT_ID/$ACCOUNT_ID/g" /tmp/bucket-policy.json
aws s3api put-bucket-policy --bucket my-account-cloudtrail-logs-$ACCOUNT_ID --policy file:///tmp/bucket-policy.json
```

### Step 2: Create Trail

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws cloudtrail create-trail \
    --name production-trail \
    --s3-bucket-name my-account-cloudtrail-logs-$ACCOUNT_ID \
    --is-multi-region-trail \
    --enable-log-file-validation \
    --include-global-service-events

# Start logging
aws cloudtrail start-logging --name production-trail
```

### Step 3: Verify Configuration

```bash
# Check status
aws cloudtrail get-trail-status --name production-trail

# Generate test event
aws sts get-caller-identity

# Wait a few minutes, then check for logs
aws s3 ls s3://my-account-cloudtrail-logs-$ACCOUNT_ID/AWSLogs/ --recursive | head -20
```

### Step 4: Cleanup

```bash
# Stop logging
aws cloudtrail stop-logging --name production-trail

# Delete trail
aws cloudtrail delete-trail --name production-trail

# Empty and delete bucket
aws s3 rm s3://my-account-cloudtrail-logs-$ACCOUNT_ID --recursive
aws s3 rb s3://my-account-cloudtrail-logs-$ACCOUNT_ID
```

---

## Next Steps

Continue to the next sections:
- [10-aws-config.md](10-aws-config.md) - Configuration compliance
- [11-sns-notifications.md](11-sns-notifications.md) - Alert notifications
- [12-hands-on-lab.md](12-hands-on-lab.md) - Complete monitoring lab
