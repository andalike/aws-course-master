# AWS Config

## Introduction

AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources. It continuously monitors and records your AWS resource configurations and allows you to automate the evaluation of recorded configurations against desired configurations. This is essential for security compliance, resource management, and troubleshooting.

---

## AWS Config Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS Config Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         AWS Resources                                    ││
│  │                                                                          ││
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              ││
│  │   │   EC2    │  │    S3    │  │   IAM    │  │   RDS    │  ...         ││
│  │   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              ││
│  │        │             │             │             │                      ││
│  └────────┼─────────────┼─────────────┼─────────────┼──────────────────────┘│
│           │             │             │             │                       │
│           └─────────────┴─────────────┴─────────────┘                       │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           AWS Config                                     ││
│  │                                                                          ││
│  │   ┌──────────────────┐      ┌──────────────────┐                       ││
│  │   │  Configuration   │      │   Config Rules   │                       ││
│  │   │    Recorder      │      │                  │                       ││
│  │   │                  │      │ ┌──────────────┐ │                       ││
│  │   │ Records changes  │─────►│ │  Managed     │ │                       ││
│  │   │ to resources     │      │ │  Rules       │ │                       ││
│  │   └──────────────────┘      │ └──────────────┘ │                       ││
│  │                              │ ┌──────────────┐ │                       ││
│  │   ┌──────────────────┐      │ │  Custom      │ │                       ││
│  │   │  Configuration   │      │ │  Rules       │ │                       ││
│  │   │    History       │      │ └──────────────┘ │                       ││
│  │   └──────────────────┘      └────────┬─────────┘                       ││
│  │                                      │                                  ││
│  │                                      ▼                                  ││
│  │                          ┌──────────────────┐                           ││
│  │                          │   Compliance     │                           ││
│  │                          │   Dashboard      │                           ││
│  │                          └──────────────────┘                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│            ┌───────────────────────┼───────────────────────┐               │
│            ▼                       ▼                       ▼               │
│     ┌──────────────┐       ┌──────────────┐       ┌──────────────┐        │
│     │     S3       │       │     SNS      │       │   Systems    │        │
│     │ (History)    │       │  (Alerts)    │       │   Manager    │        │
│     └──────────────┘       └──────────────┘       │ (Remediation)│        │
│                                                    └──────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### Configuration Items

A configuration item (CI) represents a point-in-time view of the attributes of a supported AWS resource.

```json
{
    "version": "1.3",
    "accountId": "123456789012",
    "configurationItemCaptureTime": "2024-01-15T10:30:00.000Z",
    "configurationItemStatus": "ResourceDiscovered",
    "configurationStateId": "1705315800000",
    "configurationItemMD5Hash": "abc123...",
    "arn": "arn:aws:s3:::my-bucket",
    "resourceType": "AWS::S3::Bucket",
    "resourceId": "my-bucket",
    "resourceName": "my-bucket",
    "awsRegion": "us-east-1",
    "availabilityZone": "Regional",
    "resourceCreationTime": "2024-01-01T00:00:00.000Z",
    "tags": {
        "Environment": "Production",
        "Team": "DevOps"
    },
    "relatedEvents": [],
    "relationships": [
        {
            "resourceType": "AWS::IAM::User",
            "resourceId": "AIDAEXAMPLE",
            "relationshipName": "Is attached to User"
        }
    ],
    "configuration": {
        "name": "my-bucket",
        "owner": {
            "displayName": "owner",
            "id": "abc123..."
        },
        "creationDate": "2024-01-01T00:00:00.000Z",
        "versioningConfiguration": {
            "status": "Enabled"
        },
        "serverSideEncryptionConfiguration": {
            "rules": [
                {
                    "applyServerSideEncryptionByDefault": {
                        "sseAlgorithm": "AES256"
                    }
                }
            ]
        }
    },
    "supplementaryConfiguration": {
        "BucketPolicy": "...",
        "BucketAcl": "...",
        "BucketLogging": "...",
        "PublicAccessBlockConfiguration": "..."
    }
}
```

### Configuration Recorder

Records configuration changes for supported resources.

```bash
# Start the configuration recorder
aws configservice start-configuration-recorder \
    --configuration-recorder-name default

# Check recorder status
aws configservice describe-configuration-recorder-status
```

### Delivery Channel

Specifies where Config sends configuration history and snapshots.

```bash
# Create delivery channel
aws configservice put-delivery-channel --delivery-channel '{
    "name": "default",
    "s3BucketName": "my-config-bucket",
    "s3KeyPrefix": "config",
    "snsTopicARN": "arn:aws:sns:us-east-1:123456789012:config-notifications",
    "configSnapshotDeliveryProperties": {
        "deliveryFrequency": "TwentyFour_Hours"
    }
}'
```

---

## Config Rules

### Managed Rules

AWS provides over 300 managed rules for common compliance checks.

#### Popular Managed Rules

| Rule | Description |
|------|-------------|
| `s3-bucket-public-read-prohibited` | Checks that S3 buckets don't allow public read |
| `s3-bucket-server-side-encryption-enabled` | Checks S3 bucket encryption |
| `ec2-instance-no-public-ip` | Checks EC2 instances don't have public IPs |
| `rds-instance-public-access-check` | Checks RDS instances aren't publicly accessible |
| `iam-password-policy` | Checks IAM password policy requirements |
| `iam-root-access-key-check` | Checks root account has no access keys |
| `cloudtrail-enabled` | Checks CloudTrail is enabled |
| `encrypted-volumes` | Checks EBS volumes are encrypted |
| `vpc-flow-logs-enabled` | Checks VPC flow logs are enabled |
| `required-tags` | Checks resources have required tags |

### Creating Managed Rules

#### Using AWS CLI

```bash
# S3 bucket encryption rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "s3-bucket-encryption-check",
    "Description": "Checks that S3 buckets have encryption enabled",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
    },
    "Scope": {
        "ComplianceResourceTypes": ["AWS::S3::Bucket"]
    }
}'

# EC2 instances must use specific AMIs
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "approved-amis-check",
    "Description": "Checks that EC2 instances use approved AMIs",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "APPROVED_AMIS_BY_ID"
    },
    "InputParameters": "{\"amiIds\":\"ami-12345678,ami-87654321\"}",
    "Scope": {
        "ComplianceResourceTypes": ["AWS::EC2::Instance"]
    }
}'

# Required tags rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "required-tags-check",
    "Description": "Checks that resources have required tags",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "REQUIRED_TAGS"
    },
    "InputParameters": "{\"tag1Key\":\"Environment\",\"tag2Key\":\"Owner\",\"tag3Key\":\"CostCenter\"}",
    "Scope": {
        "ComplianceResourceTypes": [
            "AWS::EC2::Instance",
            "AWS::S3::Bucket",
            "AWS::RDS::DBInstance"
        ]
    }
}'
```

#### Using CloudFormation

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: AWS Config Rules

Resources:
  # S3 Bucket Public Read Prohibited
  S3BucketPublicReadProhibitedRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-public-read-prohibited
      Description: Checks that S3 buckets do not allow public read access
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_READ_PROHIBITED
      Scope:
        ComplianceResourceTypes:
          - AWS::S3::Bucket

  # S3 Bucket Encryption
  S3BucketEncryptionRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-server-side-encryption-enabled
      Description: Checks that S3 buckets have encryption enabled
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED
      Scope:
        ComplianceResourceTypes:
          - AWS::S3::Bucket

  # RDS Encryption
  RDSEncryptionRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: rds-storage-encrypted
      Description: Checks that RDS instances have storage encryption enabled
      Source:
        Owner: AWS
        SourceIdentifier: RDS_STORAGE_ENCRYPTED
      Scope:
        ComplianceResourceTypes:
          - AWS::RDS::DBInstance

  # EC2 EBS Encryption
  EBSEncryptionRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: encrypted-volumes
      Description: Checks that EBS volumes are encrypted
      Source:
        Owner: AWS
        SourceIdentifier: ENCRYPTED_VOLUMES
      Scope:
        ComplianceResourceTypes:
          - AWS::EC2::Volume

  # CloudTrail Enabled
  CloudTrailEnabledRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: cloudtrail-enabled
      Description: Checks that CloudTrail is enabled
      Source:
        Owner: AWS
        SourceIdentifier: CLOUD_TRAIL_ENABLED
      MaximumExecutionFrequency: TwentyFour_Hours

  # IAM Password Policy
  IAMPasswordPolicyRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: iam-password-policy
      Description: Checks IAM password policy requirements
      Source:
        Owner: AWS
        SourceIdentifier: IAM_PASSWORD_POLICY
      InputParameters:
        RequireUppercaseCharacters: 'true'
        RequireLowercaseCharacters: 'true'
        RequireSymbols: 'true'
        RequireNumbers: 'true'
        MinimumPasswordLength: '14'
        PasswordReusePrevention: '24'
        MaxPasswordAge: '90'
      MaximumExecutionFrequency: TwentyFour_Hours

  # VPC Flow Logs
  VPCFlowLogsRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: vpc-flow-logs-enabled
      Description: Checks that VPC flow logs are enabled
      Source:
        Owner: AWS
        SourceIdentifier: VPC_FLOW_LOGS_ENABLED
      Scope:
        ComplianceResourceTypes:
          - AWS::EC2::VPC
```

### Custom Rules

Custom rules use AWS Lambda functions for evaluation logic.

#### Lambda-Based Custom Rule

```python
# custom_rule_lambda.py
import json
import boto3

config = boto3.client('config')

def evaluate_compliance(configuration_item):
    """
    Custom rule: Check if EC2 instance has required security group
    """
    if configuration_item['resourceType'] != 'AWS::EC2::Instance':
        return 'NOT_APPLICABLE'

    # Get security groups from configuration
    security_groups = configuration_item.get('configuration', {}).get('securityGroups', [])
    required_sg = 'sg-required-security-group'

    # Check if required security group is attached
    sg_ids = [sg.get('groupId') for sg in security_groups]

    if required_sg in sg_ids:
        return 'COMPLIANT'
    else:
        return 'NON_COMPLIANT'

def lambda_handler(event, context):
    """
    Main handler for Config rule evaluation
    """
    # Get the invoking event
    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event.get('configurationItem')

    # Handle oversized configuration items
    if invoking_event.get('messageType') == 'OversizedConfigurationItemChangeNotification':
        configuration_item = get_configuration_item(
            invoking_event['configurationItemSummary']['resourceType'],
            invoking_event['configurationItemSummary']['resourceId']
        )

    # Evaluate compliance
    compliance_type = evaluate_compliance(configuration_item)

    # Report evaluation result
    evaluation = {
        'ComplianceResourceType': configuration_item['resourceType'],
        'ComplianceResourceId': configuration_item['resourceId'],
        'ComplianceType': compliance_type,
        'Annotation': f'Security group check: {compliance_type}',
        'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
    }

    config.put_evaluations(
        Evaluations=[evaluation],
        ResultToken=event['resultToken']
    )

    return {
        'statusCode': 200,
        'body': json.dumps(evaluation)
    }

def get_configuration_item(resource_type, resource_id):
    """
    Get configuration item for oversized items
    """
    result = config.get_resource_config_history(
        resourceType=resource_type,
        resourceId=resource_id,
        limit=1
    )
    return result['configurationItems'][0]
```

#### Creating Custom Rule

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Custom AWS Config Rule

Resources:
  # Lambda Function for Custom Rule
  CustomRuleFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: config-custom-rule-security-group
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt CustomRuleLambdaRole.Arn
      Timeout: 60
      Code:
        ZipFile: |
          import json
          import boto3

          config = boto3.client('config')

          def evaluate_compliance(configuration_item, rule_parameters):
              if configuration_item['resourceType'] != 'AWS::EC2::Instance':
                  return 'NOT_APPLICABLE'

              required_sg = rule_parameters.get('requiredSecurityGroup', '')
              security_groups = configuration_item.get('configuration', {}).get('securityGroups', [])
              sg_ids = [sg.get('groupId') for sg in security_groups]

              if required_sg in sg_ids:
                  return 'COMPLIANT'
              return 'NON_COMPLIANT'

          def lambda_handler(event, context):
              invoking_event = json.loads(event['invokingEvent'])
              rule_parameters = json.loads(event.get('ruleParameters', '{}'))
              configuration_item = invoking_event.get('configurationItem', {})

              compliance_type = evaluate_compliance(configuration_item, rule_parameters)

              config.put_evaluations(
                  Evaluations=[{
                      'ComplianceResourceType': configuration_item['resourceType'],
                      'ComplianceResourceId': configuration_item['resourceId'],
                      'ComplianceType': compliance_type,
                      'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
                  }],
                  ResultToken=event['resultToken']
              )

              return {'statusCode': 200}

  # IAM Role for Lambda
  CustomRuleLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: config-custom-rule-lambda-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: ConfigPutEvaluations
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - config:PutEvaluations
                  - config:GetResourceConfigHistory
                Resource: '*'

  # Lambda Permission for Config
  CustomRuleLambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref CustomRuleFunction
      Action: lambda:InvokeFunction
      Principal: config.amazonaws.com
      SourceAccount: !Ref AWS::AccountId

  # Custom Config Rule
  CustomSecurityGroupRule:
    Type: AWS::Config::ConfigRule
    DependsOn: CustomRuleLambdaPermission
    Properties:
      ConfigRuleName: ec2-required-security-group
      Description: Checks that EC2 instances have required security group attached
      Source:
        Owner: CUSTOM_LAMBDA
        SourceIdentifier: !GetAtt CustomRuleFunction.Arn
        SourceDetails:
          - EventSource: aws.config
            MessageType: ConfigurationItemChangeNotification
      InputParameters:
        requiredSecurityGroup: sg-12345678
      Scope:
        ComplianceResourceTypes:
          - AWS::EC2::Instance
```

---

## Conformance Packs

Conformance packs are collections of Config rules and remediation actions that work together for a compliance framework.

### Available Sample Conformance Packs

| Pack | Description |
|------|-------------|
| Operational Best Practices for AWS Identity and Access Management | IAM security best practices |
| Operational Best Practices for Amazon S3 | S3 security configuration |
| Operational Best Practices for PCI DSS | Payment Card Industry compliance |
| Operational Best Practices for HIPAA Security | Healthcare compliance |
| Operational Best Practices for CIS AWS Foundations Benchmark | CIS controls |

### Creating Conformance Pack

```yaml
# conformance-pack.yaml
ConformancePackName: security-best-practices
Description: Security best practices conformance pack

Parameters:
  S3BucketName:
    Type: String
    Description: S3 bucket for remediation documents

Resources:
  # S3 Bucket Encryption
  S3BucketEncryption:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-server-side-encryption-enabled
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED

  # S3 Public Access
  S3PublicAccessBlocked:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-public-read-prohibited
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_READ_PROHIBITED

  # EBS Encryption
  EBSEncrypted:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: encrypted-volumes
      Source:
        Owner: AWS
        SourceIdentifier: ENCRYPTED_VOLUMES

  # RDS Encryption
  RDSEncrypted:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: rds-storage-encrypted
      Source:
        Owner: AWS
        SourceIdentifier: RDS_STORAGE_ENCRYPTED

  # CloudTrail Enabled
  CloudTrailEnabled:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: cloudtrail-enabled
      Source:
        Owner: AWS
        SourceIdentifier: CLOUD_TRAIL_ENABLED
      MaximumExecutionFrequency: TwentyFour_Hours

  # VPC Flow Logs
  VPCFlowLogs:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: vpc-flow-logs-enabled
      Source:
        Owner: AWS
        SourceIdentifier: VPC_FLOW_LOGS_ENABLED

  # IAM Password Policy
  IAMPasswordPolicy:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: iam-password-policy
      Source:
        Owner: AWS
        SourceIdentifier: IAM_PASSWORD_POLICY
      InputParameters:
        RequireUppercaseCharacters: 'true'
        RequireLowercaseCharacters: 'true'
        RequireSymbols: 'true'
        RequireNumbers: 'true'
        MinimumPasswordLength: '14'
      MaximumExecutionFrequency: TwentyFour_Hours
```

### Deploying Conformance Pack

```bash
# Deploy conformance pack
aws configservice put-conformance-pack \
    --conformance-pack-name security-best-practices \
    --template-body file://conformance-pack.yaml \
    --delivery-s3-bucket my-config-bucket

# Check conformance pack status
aws configservice describe-conformance-pack-status \
    --conformance-pack-names security-best-practices

# Get compliance summary
aws configservice get-conformance-pack-compliance-summary \
    --conformance-pack-names security-best-practices
```

---

## Remediation Actions

### Automatic Remediation

Configure automatic fixes for non-compliant resources using Systems Manager Automation documents.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Config Rule with Auto Remediation

Resources:
  # Config Rule
  S3BucketEncryptionRule:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-encryption-required
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED
      Scope:
        ComplianceResourceTypes:
          - AWS::S3::Bucket

  # Remediation Configuration
  S3EncryptionRemediation:
    Type: AWS::Config::RemediationConfiguration
    Properties:
      ConfigRuleName: !Ref S3BucketEncryptionRule
      TargetType: SSM_DOCUMENT
      TargetId: AWS-EnableS3BucketEncryption
      TargetVersion: '1'
      Parameters:
        BucketName:
          ResourceValue:
            Value: RESOURCE_ID
        SSEAlgorithm:
          StaticValue:
            Values:
              - AES256
        AutomationAssumeRole:
          StaticValue:
            Values:
              - !GetAtt RemediationRole.Arn
      Automatic: true
      MaximumAutomaticAttempts: 5
      RetryAttemptSeconds: 60

  # IAM Role for Remediation
  RemediationRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: config-remediation-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ssm.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: S3EncryptionRemediation
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:PutEncryptionConfiguration
                  - s3:GetEncryptionConfiguration
                Resource: '*'
```

### Manual Remediation with CLI

```bash
# Enable remediation for a rule
aws configservice put-remediation-configurations --remediation-configurations '[
    {
        "ConfigRuleName": "s3-bucket-encryption-required",
        "TargetType": "SSM_DOCUMENT",
        "TargetId": "AWS-EnableS3BucketEncryption",
        "TargetVersion": "1",
        "Parameters": {
            "BucketName": {
                "ResourceValue": {
                    "Value": "RESOURCE_ID"
                }
            },
            "SSEAlgorithm": {
                "StaticValue": {
                    "Values": ["AES256"]
                }
            },
            "AutomationAssumeRole": {
                "StaticValue": {
                    "Values": ["arn:aws:iam::123456789012:role/config-remediation-role"]
                }
            }
        },
        "Automatic": true,
        "MaximumAutomaticAttempts": 5,
        "RetryAttemptSeconds": 60
    }
]'

# Start manual remediation for specific resource
aws configservice start-remediation-execution \
    --config-rule-name s3-bucket-encryption-required \
    --resource-keys resourceType=AWS::S3::Bucket,resourceId=my-non-compliant-bucket
```

### Common SSM Automation Documents for Remediation

| Document | Purpose |
|----------|---------|
| AWS-EnableS3BucketEncryption | Enable S3 bucket encryption |
| AWS-DisableS3BucketPublicReadWrite | Block S3 public access |
| AWS-EnableEbsEncryptionByDefault | Enable EBS encryption |
| AWS-EnableCloudTrail | Enable CloudTrail |
| AWS-EnableVPCFlowLogs | Enable VPC Flow Logs |
| AWS-StopEC2Instance | Stop EC2 instance |
| AWS-TerminateEC2Instance | Terminate EC2 instance |

---

## Config Aggregators

Aggregate compliance data from multiple accounts and regions.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Config Aggregator for Organization

Resources:
  ConfigAggregator:
    Type: AWS::Config::ConfigurationAggregator
    Properties:
      ConfigurationAggregatorName: organization-aggregator
      OrganizationAggregationSource:
        RoleArn: !GetAtt AggregatorRole.Arn
        AllAwsRegions: true

  AggregatorRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: config-aggregator-role
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: config.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSConfigRoleForOrganizations
```

### Querying Aggregated Data

```bash
# Get aggregate compliance by config rule
aws configservice get-aggregate-config-rule-compliance-summary \
    --configuration-aggregator-name organization-aggregator

# Get non-compliant resources across accounts
aws configservice get-aggregate-compliance-details-by-config-rule \
    --configuration-aggregator-name organization-aggregator \
    --config-rule-name s3-bucket-encryption-required \
    --compliance-type NON_COMPLIANT
```

---

## Advanced Queries

AWS Config supports SQL-like queries for resource inventory.

### Query Examples

```sql
-- Find all S3 buckets without encryption
SELECT
    resourceId,
    resourceName,
    configuration.serverSideEncryptionConfiguration
WHERE
    resourceType = 'AWS::S3::Bucket'
    AND configuration.serverSideEncryptionConfiguration IS NULL

-- Find EC2 instances by instance type
SELECT
    resourceId,
    configuration.instanceType,
    configuration.placement.availabilityZone
WHERE
    resourceType = 'AWS::EC2::Instance'
    AND configuration.instanceType LIKE 't2.%'

-- Find resources without required tags
SELECT
    resourceType,
    resourceId,
    tags
WHERE
    resourceType IN ('AWS::EC2::Instance', 'AWS::S3::Bucket')
    AND tags.Environment IS NULL

-- Find public security groups
SELECT
    resourceId,
    resourceName,
    configuration.ipPermissions
WHERE
    resourceType = 'AWS::EC2::SecurityGroup'
    AND configuration.ipPermissions.ipRanges LIKE '%0.0.0.0/0%'

-- Count resources by type
SELECT
    resourceType,
    COUNT(*)
WHERE
    resourceType LIKE 'AWS::EC2::%'
GROUP BY
    resourceType
```

### Running Queries

```bash
# Run a query
aws configservice select-resource-config \
    --expression "SELECT resourceId, resourceType WHERE resourceType = 'AWS::S3::Bucket'"

# Save query for reuse
aws configservice put-stored-query \
    --stored-query '{
        "QueryName": "unencrypted-s3-buckets",
        "Description": "Find S3 buckets without encryption",
        "Expression": "SELECT resourceId, resourceName WHERE resourceType = '\''AWS::S3::Bucket'\'' AND configuration.serverSideEncryptionConfiguration IS NULL"
    }'

# Run stored query
aws configservice get-stored-query --query-name unencrypted-s3-buckets
```

---

## Hands-On: Setting Up AWS Config

### Step 1: Enable Config

```bash
# Create S3 bucket for Config
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 mb s3://config-bucket-$ACCOUNT_ID

# Create bucket policy
cat > /tmp/config-bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSConfigBucketPermissionsCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::config-bucket-$ACCOUNT_ID"
        },
        {
            "Sid": "AWSConfigBucketDelivery",
            "Effect": "Allow",
            "Principal": {
                "Service": "config.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::config-bucket-$ACCOUNT_ID/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket config-bucket-$ACCOUNT_ID --policy file:///tmp/config-bucket-policy.json

# Create IAM role for Config
aws iam create-role \
    --role-name ConfigRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "config.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

aws iam attach-role-policy \
    --role-name ConfigRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWS_ConfigRole

# Create configuration recorder
aws configservice put-configuration-recorder --configuration-recorder '{
    "name": "default",
    "roleARN": "arn:aws:iam::'$ACCOUNT_ID':role/ConfigRole",
    "recordingGroup": {
        "allSupported": true,
        "includeGlobalResourceTypes": true
    }
}'

# Create delivery channel
aws configservice put-delivery-channel --delivery-channel '{
    "name": "default",
    "s3BucketName": "config-bucket-'$ACCOUNT_ID'"
}'

# Start recording
aws configservice start-configuration-recorder --configuration-recorder-name default
```

### Step 2: Create Config Rules

```bash
# S3 encryption rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "s3-bucket-encryption",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
    }
}'

# S3 public access rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "s3-public-read-prohibited",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED"
    }
}'

# EBS encryption rule
aws configservice put-config-rule --config-rule '{
    "ConfigRuleName": "ebs-encryption",
    "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "ENCRYPTED_VOLUMES"
    }
}'
```

### Step 3: Check Compliance

```bash
# Get compliance summary
aws configservice get-compliance-summary-by-config-rule

# Get non-compliant resources
aws configservice get-compliance-details-by-config-rule \
    --config-rule-name s3-bucket-encryption \
    --compliance-types NON_COMPLIANT

# Get resource configuration history
aws configservice get-resource-config-history \
    --resource-type AWS::S3::Bucket \
    --resource-id my-bucket \
    --limit 5
```

### Step 4: Cleanup

```bash
# Stop recording
aws configservice stop-configuration-recorder --configuration-recorder-name default

# Delete rules
aws configservice delete-config-rule --config-rule-name s3-bucket-encryption
aws configservice delete-config-rule --config-rule-name s3-public-read-prohibited
aws configservice delete-config-rule --config-rule-name ebs-encryption

# Delete delivery channel
aws configservice delete-delivery-channel --delivery-channel-name default

# Delete configuration recorder
aws configservice delete-configuration-recorder --configuration-recorder-name default

# Delete S3 bucket
aws s3 rm s3://config-bucket-$ACCOUNT_ID --recursive
aws s3 rb s3://config-bucket-$ACCOUNT_ID

# Delete IAM role
aws iam detach-role-policy --role-name ConfigRole --policy-arn arn:aws:iam::aws:policy/service-role/AWS_ConfigRole
aws iam delete-role --role-name ConfigRole
```

---

## Best Practices

### Configuration

1. **Enable in all regions**: Resources can be created in any region
2. **Include global resources**: Only enable in one region to avoid duplicates
3. **Use lifecycle policies**: Archive old configuration history to Glacier

### Rules

1. **Start with managed rules**: Use AWS-managed rules before building custom
2. **Prioritize critical resources**: Focus on security-sensitive resources first
3. **Test rules in non-production**: Validate rule behavior before production deployment

### Remediation

1. **Start with manual remediation**: Understand the fix before automating
2. **Use least privilege**: Give remediation roles minimum required permissions
3. **Monitor remediation actions**: Track success/failure rates

### Cost Optimization

1. **Use recording filters**: Only record resources you need to monitor
2. **Limit custom rules**: Each rule evaluation has a cost
3. **Archive old data**: Use S3 lifecycle policies

---

## Pricing

| Component | Cost |
|-----------|------|
| Configuration items recorded | $0.003 per item |
| Config rule evaluations | $0.001 per evaluation |
| Conformance pack evaluations | $0.0012 per evaluation per rule |
| Advanced queries | $0.01 per query |

---

## Next Steps

Continue to the next sections:
- [11-sns-notifications.md](11-sns-notifications.md) - Alert notifications
- [12-hands-on-lab.md](12-hands-on-lab.md) - Complete monitoring lab
