# Lesson 08: CloudFormation StackSets

## Introduction

AWS CloudFormation StackSets extends CloudFormation's capability by enabling you to create, update, or delete stacks across multiple accounts and AWS Regions with a single operation. This lesson covers StackSets architecture, permission models, deployment strategies, and hands-on implementation.

---

## What Are StackSets?

StackSets allow you to provision a common set of AWS resources across multiple accounts and regions from a single CloudFormation template.

```
┌─────────────────────────────────────────────────────────────────┐
│                    StackSets Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    Administrator Account                         │
│                    ┌─────────────────┐                          │
│                    │    StackSet     │                          │
│                    │   (Template +   │                          │
│                    │   Configuration)│                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│           ┌─────────────────┼─────────────────┐                 │
│           │                 │                 │                 │
│           ▼                 ▼                 ▼                 │
│   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐        │
│   │ Target Account│ │ Target Account│ │ Target Account│        │
│   │     A         │ │     B         │ │     C         │        │
│   │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │        │
│   │ │Stack      │ │ │ │Stack      │ │ │ │Stack      │ │        │
│   │ │Instance 1 │ │ │ │Instance 2 │ │ │ │Instance 3 │ │        │
│   │ │(us-east-1)│ │ │ │(us-west-2)│ │ │ │(eu-west-1)│ │        │
│   │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │        │
│   └───────────────┘ └───────────────┘ └───────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Terminology

| Term | Description |
|------|-------------|
| **StackSet** | Container for stack instances across accounts/regions |
| **Stack Instance** | Reference to a stack in a target account and region |
| **Administrator Account** | Account where you create and manage the StackSet |
| **Target Account** | Account where stack instances are deployed |
| **Operation** | Create, update, or delete action on stack instances |

---

## StackSets Use Cases

```
┌─────────────────────────────────────────────────────────────────┐
│                    StackSets Use Cases                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. GOVERNANCE AND COMPLIANCE                                   │
│     ├── AWS Config rules across all accounts                    │
│     ├── CloudTrail logging configuration                        │
│     ├── Security Hub enablement                                 │
│     └── GuardDuty deployment                                    │
│                                                                  │
│  2. SECURITY BASELINE                                           │
│     ├── IAM password policies                                   │
│     ├── Security group baselines                                │
│     ├── VPC flow logs                                           │
│     └── KMS key policies                                        │
│                                                                  │
│  3. INFRASTRUCTURE STANDARDS                                    │
│     ├── VPC design patterns                                     │
│     ├── Networking components                                   │
│     ├── Backup policies                                         │
│     └── Monitoring and alerting                                 │
│                                                                  │
│  4. MULTI-REGION DEPLOYMENTS                                    │
│     ├── Global applications                                     │
│     ├── Disaster recovery                                       │
│     └── Content delivery                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Permission Models

StackSets supports two permission models for deployment:

### 1. Self-Managed Permissions

You manually create the required IAM roles in both administrator and target accounts.

```
┌─────────────────────────────────────────────────────────────────┐
│                Self-Managed Permissions                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Administrator Account                 Target Account            │
│  ┌─────────────────────┐              ┌────────────────────┐    │
│  │ AWSCloudFormation-  │    Assumes   │ AWSCloudFormation- │    │
│  │ StackSetAdministra- │ ──────────►  │ StackSetExecution- │    │
│  │ tionRole            │              │ Role               │    │
│  └─────────────────────┘              └────────────────────┘    │
│                                                                  │
│  • Create roles manually                                        │
│  • Works with any AWS accounts                                  │
│  • More control over permissions                                │
│  • Requires more setup                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Creating Self-Managed Roles

**Administrator Account Role:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'StackSet Administration Role'

Resources:
  AdministrationRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: AWSCloudFormationStackSetAdministrationRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: cloudformation.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: AssumeExecutionRole
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: sts:AssumeRole
                Resource: 'arn:aws:iam::*:role/AWSCloudFormationStackSetExecutionRole'
```

**Target Account Role:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'StackSet Execution Role'

Parameters:
  AdministratorAccountId:
    Type: String
    Description: AWS Account ID of the administrator account

Resources:
  ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: AWSCloudFormationStackSetExecutionRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${AdministratorAccountId}:role/AWSCloudFormationStackSetAdministrationRole'
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AdministratorAccess
      # For production, use more restrictive permissions:
      # Policies:
      #   - PolicyName: StackSetExecutionPolicy
      #     PolicyDocument:
      #       Version: '2012-10-17'
      #       Statement:
      #         - Effect: Allow
      #           Action:
      #             - cloudformation:*
      #             - s3:*
      #             - ec2:*
      #           Resource: '*'
```

### 2. Service-Managed Permissions

AWS Organizations automatically creates the required IAM roles.

```
┌─────────────────────────────────────────────────────────────────┐
│               Service-Managed Permissions                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AWS Organizations                                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  Management Account (Administrator)                      │    │
│  │  ├── Delegated Admin Account (optional)                 │    │
│  │  │                                                       │    │
│  │  └── Organization / OU                                   │    │
│  │      ├── Account A ─► Auto-created execution role       │    │
│  │      ├── Account B ─► Auto-created execution role       │    │
│  │      └── Account C ─► Auto-created execution role       │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  • Requires AWS Organizations                                   │
│  • Automatic role creation                                      │
│  • Deploy to OUs                                                │
│  • Automatic deployment to new accounts                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Permission Model Comparison

| Feature | Self-Managed | Service-Managed |
|---------|-------------|-----------------|
| AWS Organizations Required | No | Yes |
| Role Creation | Manual | Automatic |
| Target by Account ID | Yes | Yes |
| Target by OU | No | Yes |
| Auto-deploy to new accounts | No | Yes |
| Custom role names | Yes | No |
| Granular permissions | Easier | More complex |

---

## Deployment Targets

### Self-Managed: Account Lists

```bash
# Deploy to specific accounts
aws cloudformation create-stack-instances \
  --stack-set-name my-stackset \
  --accounts 111111111111 222222222222 333333333333 \
  --regions us-east-1 us-west-2 eu-west-1
```

### Service-Managed: Organizational Units

```bash
# Deploy to organizational units
aws cloudformation create-stack-instances \
  --stack-set-name my-stackset \
  --deployment-targets OrganizationalUnitIds=ou-xxxx-yyyyyyyy \
  --regions us-east-1 us-west-2

# Deploy to entire organization
aws cloudformation create-stack-instances \
  --stack-set-name my-stackset \
  --deployment-targets OrganizationalUnitIds=r-xxxx \
  --regions us-east-1
```

### Deployment Target Options

```yaml
# Service-managed deployment targets
DeploymentTargets:
  # Option 1: Deploy to specific OUs
  OrganizationalUnitIds:
    - ou-xxxx-aaaaaaaa
    - ou-xxxx-bbbbbbbb

  # Option 2: Deploy to accounts (even with service-managed)
  Accounts:
    - '111111111111'
    - '222222222222'

  # Option 3: Account filter
  AccountFilterType: INTERSECTION | DIFFERENCE | UNION
  Accounts:
    - '111111111111'
```

---

## Operation Preferences

Control how StackSets deploys stack instances:

```yaml
OperationPreferences:
  # Maximum concurrent operations
  MaxConcurrentCount: 10
  # OR percentage
  MaxConcurrentPercentage: 25

  # Failure tolerance
  FailureToleranceCount: 5
  # OR percentage
  FailureTolerancePercentage: 10

  # Region order (sequential by default)
  RegionOrder:
    - us-east-1
    - us-west-2
    - eu-west-1

  # Concurrency mode
  RegionConcurrencyType: SEQUENTIAL | PARALLEL
```

### Operation Preferences Explained

```
┌─────────────────────────────────────────────────────────────────┐
│                Operation Preferences                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MAX CONCURRENT                                                 │
│  ├── Count: Deploy to N accounts/regions simultaneously        │
│  └── Percentage: Deploy to N% of accounts simultaneously       │
│                                                                  │
│  FAILURE TOLERANCE                                              │
│  ├── Count: Allow N failures before stopping                   │
│  └── Percentage: Allow N% failures before stopping             │
│                                                                  │
│  REGION ORDER                                                   │
│  ├── Specify order of region deployment                         │
│  └── Useful for phased rollouts                                 │
│                                                                  │
│  REGION CONCURRENCY                                             │
│  ├── SEQUENTIAL: One region at a time                          │
│  └── PARALLEL: All regions simultaneously                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Creating a StackSet

### Using AWS Console

1. Navigate to CloudFormation > StackSets
2. Click "Create StackSet"
3. Choose template source
4. Select permission model
5. Specify deployment targets
6. Configure operation preferences
7. Review and create

### Using AWS CLI

#### Step 1: Create the StackSet

```bash
# Self-managed permissions
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://security-baseline.yaml \
  --description "Security baseline configuration" \
  --capabilities CAPABILITY_NAMED_IAM \
  --permission-model SELF_MANAGED \
  --administration-role-arn arn:aws:iam::123456789012:role/AWSCloudFormationStackSetAdministrationRole \
  --execution-role-name AWSCloudFormationStackSetExecutionRole

# Service-managed permissions
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://security-baseline.yaml \
  --description "Security baseline configuration" \
  --capabilities CAPABILITY_NAMED_IAM \
  --permission-model SERVICE_MANAGED \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false
```

#### Step 2: Create Stack Instances

```bash
# Self-managed: Deploy to accounts
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 222222222222 \
  --regions us-east-1 us-west-2 \
  --operation-preferences MaxConcurrentPercentage=50,FailureTolerancePercentage=10

# Service-managed: Deploy to OUs
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --deployment-targets OrganizationalUnitIds=ou-xxxx-yyyyyyyy \
  --regions us-east-1 us-west-2 \
  --operation-preferences RegionConcurrencyType=PARALLEL
```

---

## Hands-On Example: Security Baseline StackSet

### The Template (security-baseline.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Security Baseline - Deployed via StackSet'

Parameters:
  EnableCloudTrail:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable CloudTrail logging

  S3BucketPrefix:
    Type: String
    Default: 'security-logs'
    Description: Prefix for S3 bucket name

Conditions:
  CreateCloudTrail: !Equals [!Ref EnableCloudTrail, 'true']

Resources:
  # S3 Bucket for Logs
  SecurityLogsBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      BucketName: !Sub '${S3BucketPrefix}-${AWS::AccountId}-${AWS::Region}'
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: TransitionToGlacier
            Status: Enabled
            Transitions:
              - TransitionInDays: 90
                StorageClass: GLACIER
            ExpirationInDays: 365
      Tags:
        - Key: Purpose
          Value: SecurityLogs
        - Key: ManagedBy
          Value: StackSet

  # S3 Bucket Policy for CloudTrail
  SecurityLogsBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Condition: CreateCloudTrail
    Properties:
      Bucket: !Ref SecurityLogsBucket
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: AWSCloudTrailAclCheck
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: s3:GetBucketAcl
            Resource: !GetAtt SecurityLogsBucket.Arn
          - Sid: AWSCloudTrailWrite
            Effect: Allow
            Principal:
              Service: cloudtrail.amazonaws.com
            Action: s3:PutObject
            Resource: !Sub '${SecurityLogsBucket.Arn}/AWSLogs/${AWS::AccountId}/*'
            Condition:
              StringEquals:
                s3:x-amz-acl: bucket-owner-full-control

  # CloudTrail
  SecurityTrail:
    Type: AWS::CloudTrail::Trail
    Condition: CreateCloudTrail
    DependsOn: SecurityLogsBucketPolicy
    Properties:
      TrailName: !Sub 'security-trail-${AWS::AccountId}'
      S3BucketName: !Ref SecurityLogsBucket
      IsLogging: true
      IsMultiRegionTrail: true
      IncludeGlobalServiceEvents: true
      EnableLogFileValidation: true
      Tags:
        - Key: Purpose
          Value: SecurityAudit
        - Key: ManagedBy
          Value: StackSet

  # Config Recorder Role
  ConfigRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub 'config-role-${AWS::Region}'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: config.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWS_ConfigRole
      Policies:
        - PolicyName: ConfigS3Access
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:PutObjectAcl
                Resource: !Sub '${SecurityLogsBucket.Arn}/config/*'
              - Effect: Allow
                Action:
                  - s3:GetBucketAcl
                Resource: !GetAtt SecurityLogsBucket.Arn

  # Config Recorder
  ConfigRecorder:
    Type: AWS::Config::ConfigurationRecorder
    Properties:
      Name: default
      RoleARN: !GetAtt ConfigRole.Arn
      RecordingGroup:
        AllSupported: true
        IncludeGlobalResourceTypes: true

  # Config Delivery Channel
  ConfigDeliveryChannel:
    Type: AWS::Config::DeliveryChannel
    Properties:
      Name: default
      S3BucketName: !Ref SecurityLogsBucket
      S3KeyPrefix: config
      ConfigSnapshotDeliveryProperties:
        DeliveryFrequency: TwentyFour_Hours

  # Password Policy (IAM)
  # Note: This uses a custom resource or needs to be done separately

  # Security Group for Reference
  BaselineSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Baseline security group - no ingress by default
      VpcId: !Ref AWS::NoValue  # Will use default VPC
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: Allow HTTPS outbound
      Tags:
        - Key: Name
          Value: baseline-security-group
        - Key: ManagedBy
          Value: StackSet

Outputs:
  SecurityLogsBucketName:
    Description: Security logs S3 bucket name
    Value: !Ref SecurityLogsBucket

  SecurityLogsBucketArn:
    Description: Security logs S3 bucket ARN
    Value: !GetAtt SecurityLogsBucket.Arn

  CloudTrailArn:
    Description: CloudTrail ARN
    Condition: CreateCloudTrail
    Value: !GetAtt SecurityTrail.Arn

  ConfigRecorderName:
    Description: Config Recorder name
    Value: !Ref ConfigRecorder
```

### Deployment Steps

```bash
# Step 1: Create the StackSet
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://security-baseline.yaml \
  --description "Security baseline for all accounts" \
  --parameters \
    ParameterKey=EnableCloudTrail,ParameterValue=true \
    ParameterKey=S3BucketPrefix,ParameterValue=org-security-logs \
  --capabilities CAPABILITY_NAMED_IAM \
  --permission-model SELF_MANAGED \
  --administration-role-arn arn:aws:iam::123456789012:role/AWSCloudFormationStackSetAdministrationRole \
  --execution-role-name AWSCloudFormationStackSetExecutionRole

# Step 2: Add stack instances
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 222222222222 333333333333 \
  --regions us-east-1 us-west-2 eu-west-1 \
  --operation-preferences \
    MaxConcurrentCount=2,FailureToleranceCount=1,RegionConcurrencyType=SEQUENTIAL

# Step 3: Check operation status
aws cloudformation describe-stack-set-operation \
  --stack-set-name security-baseline \
  --operation-id <operation-id>

# Step 4: List stack instances
aws cloudformation list-stack-instances \
  --stack-set-name security-baseline
```

---

## Managing StackSets

### Update StackSet

```bash
# Update template for all instances
aws cloudformation update-stack-set \
  --stack-set-name security-baseline \
  --template-body file://security-baseline-v2.yaml \
  --capabilities CAPABILITY_NAMED_IAM

# Update with operation preferences
aws cloudformation update-stack-set \
  --stack-set-name security-baseline \
  --use-previous-template \
  --parameters ParameterKey=EnableCloudTrail,ParameterValue=false \
  --operation-preferences MaxConcurrentPercentage=25
```

### Add Stack Instances

```bash
# Add new accounts
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 444444444444 \
  --regions us-east-1 us-west-2

# Add new regions to existing accounts
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 222222222222 \
  --regions ap-southeast-1
```

### Delete Stack Instances

```bash
# Delete specific instances
aws cloudformation delete-stack-instances \
  --stack-set-name security-baseline \
  --accounts 333333333333 \
  --regions eu-west-1 \
  --no-retain-stacks

# Retain stacks after removal (orphan)
aws cloudformation delete-stack-instances \
  --stack-set-name security-baseline \
  --accounts 333333333333 \
  --regions eu-west-1 \
  --retain-stacks
```

### Delete StackSet

```bash
# First, delete all stack instances
aws cloudformation delete-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 222222222222 333333333333 \
  --regions us-east-1 us-west-2 eu-west-1 \
  --no-retain-stacks

# Wait for deletion
aws cloudformation describe-stack-set-operation \
  --stack-set-name security-baseline \
  --operation-id <operation-id>

# Then delete the StackSet
aws cloudformation delete-stack-set \
  --stack-set-name security-baseline
```

---

## Auto Deployment (Service-Managed)

With service-managed permissions, enable automatic deployment to new accounts:

```bash
# Enable auto-deployment
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://security-baseline.yaml \
  --permission-model SERVICE_MANAGED \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --capabilities CAPABILITY_NAMED_IAM

# Update auto-deployment settings
aws cloudformation update-stack-set \
  --stack-set-name security-baseline \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=true
```

### Auto Deployment Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│                  Auto Deployment Behavior                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Enabled=true:                                                  │
│  ├── New accounts in target OUs automatically get stacks       │
│  └── Account moves to target OU triggers deployment            │
│                                                                  │
│  RetainStacksOnAccountRemoval:                                  │
│  ├── false: Stack deleted when account leaves OU               │
│  └── true: Stack retained (orphaned) when account leaves       │
│                                                                  │
│  Example Scenario:                                              │
│  1. StackSet targets OU: "Production"                          │
│  2. New account joins "Production" OU                          │
│  3. StackSet automatically deploys to new account              │
│  4. Account moves to "Sandbox" OU                              │
│  5. Stack deleted or retained based on setting                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Drift Detection for StackSets

```bash
# Detect drift on StackSet
aws cloudformation detect-stack-set-drift \
  --stack-set-name security-baseline

# Check drift status
aws cloudformation describe-stack-set-operation \
  --stack-set-name security-baseline \
  --operation-id <drift-operation-id>

# List drift results
aws cloudformation list-stack-instance-status \
  --stack-set-name security-baseline \
  --filters Name=DRIFT_STATUS,Values=DRIFTED
```

---

## Importing Existing Stacks

You can import existing stacks into a StackSet:

```bash
# Step 1: Create StackSet with same template
aws cloudformation create-stack-set \
  --stack-set-name my-stackset \
  --template-body file://template.yaml \
  --capabilities CAPABILITY_NAMED_IAM

# Step 2: Import existing stacks
aws cloudformation import-stacks-to-stack-set \
  --stack-set-name my-stackset \
  --stack-ids \
    arn:aws:cloudformation:us-east-1:111111111111:stack/my-stack/xxx \
    arn:aws:cloudformation:us-west-2:222222222222:stack/my-stack/yyy
```

---

## Best Practices

### 1. Start Small, Scale Gradually

```bash
# Deploy to one region first
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 \
  --regions us-east-1

# Validate, then expand
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 222222222222 333333333333 \
  --regions us-east-1 us-west-2 eu-west-1
```

### 2. Use Region Order for Controlled Rollouts

```yaml
OperationPreferences:
  RegionOrder:
    - us-east-1      # Deploy here first (validation)
    - us-west-2      # Then secondary US region
    - eu-west-1      # Then EU
    - ap-southeast-1 # Finally APAC
  RegionConcurrencyType: SEQUENTIAL
```

### 3. Set Appropriate Failure Tolerance

```yaml
# Production: Low tolerance
OperationPreferences:
  FailureToleranceCount: 0
  MaxConcurrentCount: 1

# Development: Higher tolerance
OperationPreferences:
  FailureTolerancePercentage: 25
  MaxConcurrentPercentage: 50
```

### 4. Use Tags for Organization

```bash
aws cloudformation create-stack-set \
  --stack-set-name security-baseline \
  --template-body file://template.yaml \
  --tags \
    Key=Purpose,Value=Security \
    Key=Team,Value=Platform \
    Key=CostCenter,Value=IT-Security
```

### 5. Use Parameter Overrides

```bash
# Different parameters per account
aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 111111111111 \
  --regions us-east-1 \
  --parameter-overrides \
    ParameterKey=Environment,ParameterValue=production

aws cloudformation create-stack-instances \
  --stack-set-name security-baseline \
  --accounts 222222222222 \
  --regions us-east-1 \
  --parameter-overrides \
    ParameterKey=Environment,ParameterValue=development
```

---

## Common Errors and Solutions

### Error 1: Insufficient Permissions

```
Error: User is not authorized to perform: cloudformation:CreateStackSet
```

**Solution**: Ensure proper IAM permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStackSet",
        "cloudformation:CreateStackInstances",
        "cloudformation:UpdateStackSet",
        "cloudformation:DeleteStackSet",
        "cloudformation:DeleteStackInstances",
        "cloudformation:DescribeStackSet",
        "cloudformation:DescribeStackSetOperation",
        "cloudformation:ListStackInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::*:role/AWSCloudFormationStackSet*"
    }
  ]
}
```

### Error 2: Execution Role Not Found

```
Error: Execution role not found in target account
```

**Solution**: Create execution role in target account

```bash
# Deploy execution role template to target account
aws cloudformation create-stack \
  --stack-name stackset-execution-role \
  --template-body file://execution-role.yaml \
  --parameters ParameterKey=AdministratorAccountId,ParameterValue=123456789012 \
  --capabilities CAPABILITY_NAMED_IAM
```

### Error 3: StackSet Operation in Progress

```
Error: StackSet operation already in progress
```

**Solution**: Wait for current operation to complete

```bash
# Check operation status
aws cloudformation list-stack-set-operations \
  --stack-set-name my-stackset

# Wait for completion
aws cloudformation wait stack-set-operation-complete \
  --stack-set-name my-stackset \
  --operation-id <operation-id>
```

### Error 4: Template Validation Error in One Account

```
Error: Template validation failed in account 222222222222
```

**Solution**: Check account-specific constraints

```bash
# Get detailed error
aws cloudformation list-stack-instance-resource-drifts \
  --stack-set-name my-stackset \
  --stack-instance-account 222222222222 \
  --stack-instance-region us-east-1
```

---

## Monitoring StackSets

### CloudWatch Events

```yaml
# EventBridge rule for StackSet operations
Resources:
  StackSetEventRule:
    Type: AWS::Events::Rule
    Properties:
      Name: stackset-operation-notifications
      EventPattern:
        source:
          - aws.cloudformation
        detail-type:
          - CloudFormation StackSet Operation Status Change
        detail:
          status:
            - FAILED
            - SUCCEEDED
      Targets:
        - Id: SNSNotification
          Arn: !Ref NotificationTopic
```

### Useful CLI Commands

```bash
# List all StackSets
aws cloudformation list-stack-sets

# Describe StackSet
aws cloudformation describe-stack-set --stack-set-name my-stackset

# List stack instances
aws cloudformation list-stack-instances --stack-set-name my-stackset

# Get operation details
aws cloudformation describe-stack-set-operation \
  --stack-set-name my-stackset \
  --operation-id <operation-id>

# List failed instances
aws cloudformation list-stack-instances \
  --stack-set-name my-stackset \
  --filters Name=DETAILED_STATUS,Values=FAILED
```

---

## Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     StackSets Summary                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Key Concepts:                                                   │
│  ├── Deploy to multiple accounts and regions                   │
│  ├── Single template, many stack instances                     │
│  ├── Centralized management                                    │
│  └── Two permission models available                           │
│                                                                  │
│  Permission Models:                                             │
│  ├── Self-Managed: Manual IAM role setup                       │
│  └── Service-Managed: AWS Organizations integration            │
│                                                                  │
│  Best Practices:                                                │
│  ├── Start small, scale gradually                              │
│  ├── Use region order for controlled rollouts                  │
│  ├── Set appropriate failure tolerance                         │
│  ├── Use tags for organization                                 │
│  └── Consider parameter overrides                              │
│                                                                  │
│  Use Cases:                                                     │
│  ├── Security baselines                                        │
│  ├── Compliance requirements                                   │
│  ├── Multi-region deployments                                  │
│  └── Organizational standards                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Practice**: Set up StackSet roles in your accounts
2. **Deploy**: Create a simple StackSet across accounts
3. **Learn**: AWS CDK for programmatic infrastructure

---

**Next:** [Lesson 09 - AWS CDK Introduction](./09-cdk-introduction.md)
