# Module 9: Hands-on Lab - Complete CloudFormation and IaC Workshop

## Introduction

This comprehensive hands-on lab covers all aspects of AWS CloudFormation and Infrastructure as Code. You will create, update, and manage CloudFormation stacks using both the AWS Console and CLI, work with nested stacks, implement cross-stack references, and deploy infrastructure using AWS CDK.

---

## Prerequisites

Before starting this lab, ensure you have:

- [ ] AWS account with administrative access
- [ ] AWS CLI configured (`aws configure`)
- [ ] Text editor (VS Code recommended)
- [ ] Node.js installed (for CDK)
- [ ] Python 3.9+ installed
- [ ] Basic understanding of YAML

```bash
# Verify prerequisites
aws --version
node --version
python3 --version

# Install CDK CLI
npm install -g aws-cdk
cdk --version

# Install cfn-lint
pip install cfn-lint
```

---

## Lab Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       Lab Structure                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Lab 1: Basic Stack Operations (Console + CLI)                  │
│  Lab 2: Parameters, Mappings, and Conditions                   │
│  Lab 3: Change Sets and Stack Updates                           │
│  Lab 4: Nested Stacks                                           │
│  Lab 5: Cross-Stack References                                  │
│  Lab 6: AWS CDK Deployment                                      │
│  Lab 7: Drift Detection and Remediation                        │
│  Lab 8: Complete Cleanup                                        │
│                                                                  │
│  Estimated Total Time: 3-4 hours                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Lab 1: Basic Stack Operations

### Objective
Learn to create, describe, and delete CloudFormation stacks using both the AWS Console and CLI.

### Duration: 30 minutes

---

### Part A: Create Stack via AWS Console

#### Step 1: Create Template File

Create a file named `lab1-basic-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 1 - Basic CloudFormation Stack'

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: 'Environment Configuration'
        Parameters:
          - EnvironmentName
          - BucketSuffix

Parameters:
  EnvironmentName:
    Type: String
    Default: lab
    Description: Environment name for tagging

  BucketSuffix:
    Type: String
    Default: data
    Description: Suffix for S3 bucket name

Resources:
  # S3 Bucket
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${EnvironmentName}-${BucketSuffix}-${AWS::AccountId}-${AWS::Region}'
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Purpose
          Value: Lab1

  # CloudWatch Log Group
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/lab/${EnvironmentName}/application'
      RetentionInDays: 7
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

  # SNS Topic
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub '${EnvironmentName}-notifications'
      DisplayName: Lab Notifications
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

Outputs:
  BucketName:
    Description: S3 Bucket Name
    Value: !Ref DataBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'

  BucketArn:
    Description: S3 Bucket ARN
    Value: !GetAtt DataBucket.Arn
    Export:
      Name: !Sub '${AWS::StackName}-BucketArn'

  LogGroupName:
    Description: CloudWatch Log Group Name
    Value: !Ref ApplicationLogGroup

  TopicArn:
    Description: SNS Topic ARN
    Value: !Ref NotificationTopic
    Export:
      Name: !Sub '${AWS::StackName}-TopicArn'
```

#### Step 2: Deploy via Console

1. Navigate to **CloudFormation** in AWS Console
2. Click **Create stack** > **With new resources (standard)**
3. Choose **Upload a template file**
4. Upload `lab1-basic-stack.yaml`
5. Click **Next**
6. Enter Stack name: `lab1-basic-stack`
7. Review parameters and click **Next**
8. Configure stack options (add tags if desired)
9. Review and click **Submit**
10. Monitor the stack creation in the **Events** tab

#### Step 3: Explore Stack Resources

1. Click on the stack name
2. Navigate to **Resources** tab - view created resources
3. Navigate to **Outputs** tab - view exported values
4. Navigate to **Template** tab - view original template
5. Navigate to **Parameters** tab - view input parameters

---

### Part B: Create Stack via CLI

#### Step 1: Create Template File

Create a file named `lab1-cli-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 1 - CLI Created Stack'

Parameters:
  EnvironmentName:
    Type: String
    Default: lab-cli
    Description: Environment name

Resources:
  DemoQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub '${EnvironmentName}-demo-queue'
      VisibilityTimeoutSeconds: 60
      MessageRetentionPeriod: 86400
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub '${EnvironmentName}-dlq'
      MessageRetentionPeriod: 1209600
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

Outputs:
  QueueUrl:
    Description: SQS Queue URL
    Value: !Ref DemoQueue

  QueueArn:
    Description: SQS Queue ARN
    Value: !GetAtt DemoQueue.Arn

  DLQUrl:
    Description: Dead Letter Queue URL
    Value: !Ref DeadLetterQueue
```

#### Step 2: Validate Template

```bash
# Validate template syntax
aws cloudformation validate-template \
  --template-body file://lab1-cli-stack.yaml

# Use cfn-lint for additional checks
cfn-lint lab1-cli-stack.yaml
```

#### Step 3: Create Stack

```bash
# Create stack
aws cloudformation create-stack \
  --stack-name lab1-cli-stack \
  --template-body file://lab1-cli-stack.yaml \
  --parameters ParameterKey=EnvironmentName,ParameterValue=lab-cli \
  --tags Key=Purpose,Value=Lab1 Key=CreatedBy,Value=CLI

# Wait for stack creation
aws cloudformation wait stack-create-complete \
  --stack-name lab1-cli-stack

echo "Stack creation complete!"
```

#### Step 4: Describe Stack

```bash
# Get stack status
aws cloudformation describe-stacks \
  --stack-name lab1-cli-stack \
  --query 'Stacks[0].StackStatus'

# List stack resources
aws cloudformation list-stack-resources \
  --stack-name lab1-cli-stack

# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name lab1-cli-stack \
  --query 'Stacks[0].Outputs'

# View stack events
aws cloudformation describe-stack-events \
  --stack-name lab1-cli-stack \
  --query 'StackEvents[0:5]'
```

### Lab 1 Checkpoint

You should now have:
- [ ] Stack `lab1-basic-stack` created via Console
- [ ] Stack `lab1-cli-stack` created via CLI
- [ ] Understanding of stack resources, outputs, and events

---

## Lab 2: Parameters, Mappings, and Conditions

### Objective
Learn to use parameters, mappings, and conditions to create flexible, reusable templates.

### Duration: 45 minutes

---

### Step 1: Create Advanced Template

Create a file named `lab2-advanced-template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 2 - Parameters, Mappings, and Conditions'

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: 'Environment Configuration'
        Parameters:
          - EnvironmentType
      - Label:
          default: 'Application Configuration'
        Parameters:
          - EnableMonitoring
          - LogRetentionDays
    ParameterLabels:
      EnvironmentType:
        default: 'What environment is this?'
      EnableMonitoring:
        default: 'Enable CloudWatch monitoring?'

Parameters:
  EnvironmentType:
    Type: String
    Default: development
    AllowedValues:
      - development
      - staging
      - production
    Description: Select the environment type

  EnableMonitoring:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable CloudWatch monitoring

  LogRetentionDays:
    Type: Number
    Default: 7
    AllowedValues:
      - 1
      - 7
      - 14
      - 30
      - 90
      - 365
    Description: CloudWatch log retention period

Mappings:
  EnvironmentConfig:
    development:
      InstanceType: t3.micro
      MinSize: 1
      MaxSize: 2
      EnableDeletionProtection: false
      BackupRetention: 1
    staging:
      InstanceType: t3.small
      MinSize: 2
      MaxSize: 4
      EnableDeletionProtection: false
      BackupRetention: 7
    production:
      InstanceType: t3.medium
      MinSize: 3
      MaxSize: 6
      EnableDeletionProtection: true
      BackupRetention: 30

  RegionAMI:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    us-west-2:
      AMI: ami-0892d3c7ee96c0bf7
    eu-west-1:
      AMI: ami-0d5d9d301c853a04a

Conditions:
  IsProduction: !Equals [!Ref EnvironmentType, 'production']
  IsNotProduction: !Not [!Equals [!Ref EnvironmentType, 'production']]
  EnableMonitoringCondition: !Equals [!Ref EnableMonitoring, 'true']
  CreateProductionResources: !And
    - !Condition IsProduction
    - !Condition EnableMonitoringCondition

Resources:
  # S3 Bucket - Different configuration per environment
  ApplicationBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: !If [IsProduction, Retain, Delete]
    Properties:
      BucketName: !Sub 'lab2-app-${EnvironmentType}-${AWS::AccountId}'
      VersioningConfiguration:
        Status: !If [IsProduction, Enabled, Suspended]
      LifecycleConfiguration:
        Rules:
          - Id: TransitionRule
            Status: Enabled
            Transitions:
              - TransitionInDays: !FindInMap [EnvironmentConfig, !Ref EnvironmentType, BackupRetention]
                StorageClass: STANDARD_IA
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentType
        - Key: Monitoring
          Value: !Ref EnableMonitoring

  # CloudWatch Log Group
  ApplicationLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/lab2/${EnvironmentType}/application'
      RetentionInDays: !Ref LogRetentionDays

  # CloudWatch Dashboard - Only in Production with Monitoring Enabled
  MonitoringDashboard:
    Type: AWS::CloudWatch::Dashboard
    Condition: CreateProductionResources
    Properties:
      DashboardName: !Sub 'Lab2-${EnvironmentType}-Dashboard'
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "text",
              "x": 0,
              "y": 0,
              "width": 24,
              "height": 1,
              "properties": {
                "markdown": "# Lab 2 Dashboard - ${EnvironmentType}"
              }
            },
            {
              "type": "metric",
              "x": 0,
              "y": 1,
              "width": 12,
              "height": 6,
              "properties": {
                "title": "S3 Bucket Size",
                "region": "${AWS::Region}",
                "metrics": [
                  ["AWS/S3", "BucketSizeBytes", "BucketName", "${ApplicationBucket}", "StorageType", "StandardStorage"]
                ],
                "period": 86400,
                "stat": "Average"
              }
            }
          ]
        }

  # Alarm - Only with Monitoring Enabled
  BucketSizeAlarm:
    Type: AWS::CloudWatch::Alarm
    Condition: EnableMonitoringCondition
    Properties:
      AlarmName: !Sub 'Lab2-${EnvironmentType}-BucketSize'
      AlarmDescription: Alarm when bucket size exceeds threshold
      MetricName: BucketSizeBytes
      Namespace: AWS/S3
      Statistic: Average
      Period: 86400
      EvaluationPeriods: 1
      Threshold: 1073741824  # 1 GB
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: BucketName
          Value: !Ref ApplicationBucket
        - Name: StorageType
          Value: StandardStorage

  # DynamoDB Table - Production only
  ProductionTable:
    Type: AWS::DynamoDB::Table
    Condition: IsProduction
    DeletionPolicy: Retain
    Properties:
      TableName: !Sub 'lab2-production-table'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentType

Outputs:
  BucketName:
    Description: Application S3 Bucket Name
    Value: !Ref ApplicationBucket

  BucketVersioningStatus:
    Description: Bucket Versioning Status
    Value: !If [IsProduction, 'Enabled', 'Suspended']

  EnvironmentSettings:
    Description: Environment Configuration Summary
    Value: !Sub
      - 'Instance Type: ${InstanceType}, Min: ${MinSize}, Max: ${MaxSize}'
      - InstanceType: !FindInMap [EnvironmentConfig, !Ref EnvironmentType, InstanceType]
        MinSize: !FindInMap [EnvironmentConfig, !Ref EnvironmentType, MinSize]
        MaxSize: !FindInMap [EnvironmentConfig, !Ref EnvironmentType, MaxSize]

  DashboardName:
    Description: CloudWatch Dashboard Name
    Condition: CreateProductionResources
    Value: !Ref MonitoringDashboard

  ProductionTableName:
    Description: DynamoDB Table Name (Production Only)
    Condition: IsProduction
    Value: !Ref ProductionTable
```

### Step 2: Deploy for Development

```bash
# Deploy for development environment
aws cloudformation create-stack \
  --stack-name lab2-development \
  --template-body file://lab2-advanced-template.yaml \
  --parameters \
    ParameterKey=EnvironmentType,ParameterValue=development \
    ParameterKey=EnableMonitoring,ParameterValue=true \
    ParameterKey=LogRetentionDays,ParameterValue=7

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name lab2-development

# View outputs
aws cloudformation describe-stacks \
  --stack-name lab2-development \
  --query 'Stacks[0].Outputs'
```

### Step 3: Deploy for Production

```bash
# Deploy for production environment
aws cloudformation create-stack \
  --stack-name lab2-production \
  --template-body file://lab2-advanced-template.yaml \
  --parameters \
    ParameterKey=EnvironmentType,ParameterValue=production \
    ParameterKey=EnableMonitoring,ParameterValue=true \
    ParameterKey=LogRetentionDays,ParameterValue=30

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name lab2-production

# View outputs - note the additional outputs
aws cloudformation describe-stacks \
  --stack-name lab2-production \
  --query 'Stacks[0].Outputs'
```

### Step 4: Compare Resources

```bash
# Compare resources between environments
echo "Development Resources:"
aws cloudformation list-stack-resources \
  --stack-name lab2-development \
  --query 'StackResourceSummaries[].{Type:ResourceType,ID:LogicalResourceId}'

echo -e "\nProduction Resources:"
aws cloudformation list-stack-resources \
  --stack-name lab2-production \
  --query 'StackResourceSummaries[].{Type:ResourceType,ID:LogicalResourceId}'
```

### Lab 2 Checkpoint

You should now have:
- [ ] Understanding of mappings for environment-specific values
- [ ] Conditions controlling resource creation
- [ ] Different outputs based on conditions

---

## Lab 3: Change Sets and Stack Updates

### Objective
Learn to safely update stacks using change sets.

### Duration: 30 minutes

---

### Step 1: Create Initial Stack

Create a file named `lab3-changeset.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 3 - Change Sets Demo v1.0'

Parameters:
  BucketPrefix:
    Type: String
    Default: lab3
    Description: Prefix for bucket name

  EnableVersioning:
    Type: String
    Default: 'false'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable S3 versioning

Conditions:
  VersioningEnabled: !Equals [!Ref EnableVersioning, 'true']

Resources:
  DemoBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketPrefix}-demo-${AWS::AccountId}'
      VersioningConfiguration:
        Status: !If [VersioningEnabled, Enabled, Suspended]
      Tags:
        - Key: Version
          Value: '1.0'

Outputs:
  BucketName:
    Description: Bucket Name
    Value: !Ref DemoBucket

  BucketArn:
    Description: Bucket ARN
    Value: !GetAtt DemoBucket.Arn
```

```bash
# Create initial stack
aws cloudformation create-stack \
  --stack-name lab3-changeset \
  --template-body file://lab3-changeset.yaml \
  --parameters ParameterKey=EnableVersioning,ParameterValue=false

aws cloudformation wait stack-create-complete --stack-name lab3-changeset
```

### Step 2: Create Change Set for Non-Breaking Change

```bash
# Create change set to enable versioning (non-breaking)
aws cloudformation create-change-set \
  --stack-name lab3-changeset \
  --change-set-name enable-versioning \
  --template-body file://lab3-changeset.yaml \
  --parameters ParameterKey=EnableVersioning,ParameterValue=true

# Wait for change set to be created
aws cloudformation wait change-set-create-complete \
  --stack-name lab3-changeset \
  --change-set-name enable-versioning

# Describe change set
aws cloudformation describe-change-set \
  --stack-name lab3-changeset \
  --change-set-name enable-versioning

# View changes in detail
aws cloudformation describe-change-set \
  --stack-name lab3-changeset \
  --change-set-name enable-versioning \
  --query 'Changes'
```

### Step 3: Execute Change Set

```bash
# Execute the change set
aws cloudformation execute-change-set \
  --stack-name lab3-changeset \
  --change-set-name enable-versioning

# Wait for update to complete
aws cloudformation wait stack-update-complete --stack-name lab3-changeset

# Verify the change
aws s3api get-bucket-versioning \
  --bucket $(aws cloudformation describe-stacks --stack-name lab3-changeset --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' --output text)
```

### Step 4: Create Change Set for Resource Replacement

Update the template to change the bucket name (will cause replacement):

```yaml
# Update lab3-changeset.yaml - change the BucketName
Resources:
  DemoBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketPrefix}-demo-v2-${AWS::AccountId}'  # Changed!
      VersioningConfiguration:
        Status: !If [VersioningEnabled, Enabled, Suspended]
      Tags:
        - Key: Version
          Value: '2.0'  # Changed!
```

```bash
# Create change set for replacement
aws cloudformation create-change-set \
  --stack-name lab3-changeset \
  --change-set-name rename-bucket \
  --template-body file://lab3-changeset.yaml \
  --parameters ParameterKey=EnableVersioning,ParameterValue=true

aws cloudformation wait change-set-create-complete \
  --stack-name lab3-changeset \
  --change-set-name rename-bucket

# View the replacement warning
aws cloudformation describe-change-set \
  --stack-name lab3-changeset \
  --change-set-name rename-bucket \
  --query 'Changes[].ResourceChange.{Action:Action,Replacement:Replacement,LogicalId:LogicalResourceId}'
```

**Warning**: This change set shows `Replacement: True`. This means the existing bucket will be deleted and a new one created!

### Step 5: Delete Change Set Without Executing

```bash
# Delete the dangerous change set
aws cloudformation delete-change-set \
  --stack-name lab3-changeset \
  --change-set-name rename-bucket

echo "Change set deleted - bucket was not replaced!"
```

### Lab 3 Checkpoint

You should now understand:
- [ ] How to create change sets before applying updates
- [ ] How to review change set details
- [ ] The difference between Modify and Replace actions
- [ ] How to safely delete a change set

---

## Lab 4: Nested Stacks

### Objective
Create a multi-tier application using nested stacks.

### Duration: 45 minutes

---

### Step 1: Create Child Stack Templates

First, create an S3 bucket to store the nested templates:

```bash
# Create bucket for templates
TEMPLATE_BUCKET="lab4-templates-${RANDOM}-$(aws sts get-caller-identity --query Account --output text)"
aws s3 mb s3://${TEMPLATE_BUCKET}
echo "Template bucket: ${TEMPLATE_BUCKET}"
```

Create `lab4-network-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 4 - Nested Stack: Network Layer'

Parameters:
  EnvironmentName:
    Type: String
    Description: Environment name

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: VPC CIDR block

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-vpc'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-igw'

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [0, !Cidr [!Ref VPCCidr, 4, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-1'

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [1, !Cidr [!Ref VPCCidr, 4, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-2'

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-rt'

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC

  PublicSubnet1Id:
    Description: Public Subnet 1 ID
    Value: !Ref PublicSubnet1

  PublicSubnet2Id:
    Description: Public Subnet 2 ID
    Value: !Ref PublicSubnet2

  VPCCidrBlock:
    Description: VPC CIDR Block
    Value: !Ref VPCCidr
```

Create `lab4-security-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 4 - Nested Stack: Security Layer'

Parameters:
  EnvironmentName:
    Type: String
    Description: Environment name

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

Resources:
  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Web server security group
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP access
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS access
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-web-sg'

Outputs:
  WebSecurityGroupId:
    Description: Web Security Group ID
    Value: !Ref WebSecurityGroup
```

Create `lab4-storage-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 4 - Nested Stack: Storage Layer'

Parameters:
  EnvironmentName:
    Type: String
    Description: Environment name

Resources:
  DataBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${EnvironmentName}-data-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-data-bucket'

Outputs:
  BucketName:
    Description: Data Bucket Name
    Value: !Ref DataBucket

  BucketArn:
    Description: Data Bucket ARN
    Value: !GetAtt DataBucket.Arn
```

### Step 2: Upload Child Templates to S3

```bash
# Upload nested stack templates
aws s3 cp lab4-network-stack.yaml s3://${TEMPLATE_BUCKET}/nested/
aws s3 cp lab4-security-stack.yaml s3://${TEMPLATE_BUCKET}/nested/
aws s3 cp lab4-storage-stack.yaml s3://${TEMPLATE_BUCKET}/nested/

# Verify uploads
aws s3 ls s3://${TEMPLATE_BUCKET}/nested/
```

### Step 3: Create Root Stack

Create `lab4-root-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 4 - Root Stack with Nested Stacks'

Parameters:
  EnvironmentName:
    Type: String
    Default: lab4
    Description: Environment name

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: VPC CIDR block

  TemplateBucket:
    Type: String
    Description: S3 bucket containing nested templates

Resources:
  # Network Stack
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/nested/lab4-network-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VPCCidr: !Ref VPCCidr
      Tags:
        - Key: StackType
          Value: Network

  # Security Stack
  SecurityStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/nested/lab4-security-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
      Tags:
        - Key: StackType
          Value: Security

  # Storage Stack
  StorageStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/nested/lab4-storage-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
      Tags:
        - Key: StackType
          Value: Storage

Outputs:
  VPCId:
    Description: VPC ID
    Value: !GetAtt NetworkStack.Outputs.VPCId

  PublicSubnets:
    Description: Public Subnet IDs
    Value: !Join
      - ','
      - - !GetAtt NetworkStack.Outputs.PublicSubnet1Id
        - !GetAtt NetworkStack.Outputs.PublicSubnet2Id

  WebSecurityGroupId:
    Description: Web Security Group ID
    Value: !GetAtt SecurityStack.Outputs.WebSecurityGroupId

  DataBucketName:
    Description: Data Bucket Name
    Value: !GetAtt StorageStack.Outputs.BucketName
```

### Step 4: Deploy Root Stack

```bash
# Deploy the root stack
aws cloudformation create-stack \
  --stack-name lab4-nested \
  --template-body file://lab4-root-stack.yaml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=lab4 \
    ParameterKey=TemplateBucket,ParameterValue=${TEMPLATE_BUCKET}

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name lab4-nested

# View all stacks
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE \
  --query 'StackSummaries[?contains(StackName, `lab4`)]'
```

### Step 5: Explore Nested Stacks

```bash
# Get root stack outputs
aws cloudformation describe-stacks \
  --stack-name lab4-nested \
  --query 'Stacks[0].Outputs'

# List nested stacks
aws cloudformation list-stack-resources \
  --stack-name lab4-nested \
  --query 'StackResourceSummaries[?ResourceType==`AWS::CloudFormation::Stack`]'
```

### Lab 4 Checkpoint

You should now have:
- [ ] Root stack with three nested stacks
- [ ] Understanding of parent-child stack relationships
- [ ] Experience passing outputs between stacks

---

## Lab 5: Cross-Stack References

### Objective
Learn to share values between independent stacks using exports and imports.

### Duration: 30 minutes

---

### Step 1: Create Exporting Stack

Create `lab5-shared-resources.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 5 - Shared Resources (Exporting Stack)'

Parameters:
  EnvironmentName:
    Type: String
    Default: lab5
    Description: Environment name

Resources:
  SharedBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${EnvironmentName}-shared-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-shared-bucket'

  SharedTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: !Sub '${EnvironmentName}-shared-topic'
      DisplayName: Lab 5 Shared Topic

  SharedQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub '${EnvironmentName}-shared-queue'

Outputs:
  SharedBucketName:
    Description: Shared S3 Bucket Name
    Value: !Ref SharedBucket
    Export:
      Name: !Sub '${AWS::StackName}-SharedBucketName'

  SharedBucketArn:
    Description: Shared S3 Bucket ARN
    Value: !GetAtt SharedBucket.Arn
    Export:
      Name: !Sub '${AWS::StackName}-SharedBucketArn'

  SharedTopicArn:
    Description: Shared SNS Topic ARN
    Value: !Ref SharedTopic
    Export:
      Name: !Sub '${AWS::StackName}-SharedTopicArn'

  SharedQueueUrl:
    Description: Shared SQS Queue URL
    Value: !Ref SharedQueue
    Export:
      Name: !Sub '${AWS::StackName}-SharedQueueUrl'

  SharedQueueArn:
    Description: Shared SQS Queue ARN
    Value: !GetAtt SharedQueue.Arn
    Export:
      Name: !Sub '${AWS::StackName}-SharedQueueArn'
```

```bash
# Deploy shared resources stack
aws cloudformation create-stack \
  --stack-name lab5-shared \
  --template-body file://lab5-shared-resources.yaml

aws cloudformation wait stack-create-complete --stack-name lab5-shared

# View exports
aws cloudformation list-exports
```

### Step 2: Create Importing Stack

Create `lab5-consumer.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 5 - Consumer Stack (Importing Stack)'

Parameters:
  EnvironmentName:
    Type: String
    Default: lab5
    Description: Environment name

  SharedStackName:
    Type: String
    Default: lab5-shared
    Description: Name of the shared resources stack

Resources:
  # Lambda execution role with access to shared resources
  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${EnvironmentName}-consumer-lambda-role'
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
        - PolicyName: SharedResourcesAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:ListBucket
                Resource:
                  - Fn::ImportValue: !Sub '${SharedStackName}-SharedBucketArn'
                  - !Sub
                    - '${BucketArn}/*'
                    - BucketArn:
                        Fn::ImportValue: !Sub '${SharedStackName}-SharedBucketArn'
              - Effect: Allow
                Action:
                  - sns:Publish
                Resource:
                  Fn::ImportValue: !Sub '${SharedStackName}-SharedTopicArn'
              - Effect: Allow
                Action:
                  - sqs:SendMessage
                  - sqs:ReceiveMessage
                  - sqs:DeleteMessage
                Resource:
                  Fn::ImportValue: !Sub '${SharedStackName}-SharedQueueArn'

  # Lambda function that uses shared resources
  ConsumerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${EnvironmentName}-consumer'
      Runtime: python3.11
      Handler: index.handler
      Role: !GetAtt LambdaRole.Arn
      Timeout: 30
      Environment:
        Variables:
          BUCKET_NAME:
            Fn::ImportValue: !Sub '${SharedStackName}-SharedBucketName'
          TOPIC_ARN:
            Fn::ImportValue: !Sub '${SharedStackName}-SharedTopicArn'
          QUEUE_URL:
            Fn::ImportValue: !Sub '${SharedStackName}-SharedQueueUrl'
      Code:
        ZipFile: |
          import os
          import json
          import boto3

          s3 = boto3.client('s3')
          sns = boto3.client('sns')
          sqs = boto3.client('sqs')

          def handler(event, context):
              bucket = os.environ['BUCKET_NAME']
              topic = os.environ['TOPIC_ARN']
              queue = os.environ['QUEUE_URL']

              # Write to S3
              s3.put_object(
                  Bucket=bucket,
                  Key=f'test/{context.aws_request_id}.json',
                  Body=json.dumps({'request_id': context.aws_request_id})
              )

              # Publish to SNS
              sns.publish(
                  TopicArn=topic,
                  Message=f'Processed request: {context.aws_request_id}'
              )

              # Send to SQS
              sqs.send_message(
                  QueueUrl=queue,
                  MessageBody=json.dumps({'request_id': context.aws_request_id})
              )

              return {
                  'statusCode': 200,
                  'body': json.dumps({
                      'message': 'Successfully used shared resources',
                      'request_id': context.aws_request_id
                  })
              }

Outputs:
  FunctionName:
    Description: Consumer Lambda Function Name
    Value: !Ref ConsumerFunction

  FunctionArn:
    Description: Consumer Lambda Function ARN
    Value: !GetAtt ConsumerFunction.Arn

  UsedBucket:
    Description: Bucket being used (imported)
    Value:
      Fn::ImportValue: !Sub '${SharedStackName}-SharedBucketName'
```

```bash
# Deploy consumer stack
aws cloudformation create-stack \
  --stack-name lab5-consumer \
  --template-body file://lab5-consumer.yaml \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation wait stack-create-complete --stack-name lab5-consumer
```

### Step 3: Verify Cross-Stack References

```bash
# List all imports for the shared stack
aws cloudformation list-imports \
  --export-name lab5-shared-SharedBucketName

# Test the consumer function
aws lambda invoke \
  --function-name lab5-consumer \
  --payload '{}' \
  response.json

cat response.json
```

### Step 4: Understand Deletion Order

```bash
# Try to delete shared stack (will fail)
aws cloudformation delete-stack --stack-name lab5-shared

# Check why it failed
aws cloudformation describe-stack-events \
  --stack-name lab5-shared \
  --query 'StackEvents[0]'

# Correct order: delete consumer first, then shared
```

### Lab 5 Checkpoint

You should now understand:
- [ ] How to export values from one stack
- [ ] How to import values in another stack
- [ ] Dependency management between stacks

---

## Lab 6: AWS CDK Deployment

### Objective
Deploy infrastructure using AWS CDK.

### Duration: 45 minutes

---

### Step 1: Initialize CDK Project

```bash
# Create project directory
mkdir lab6-cdk && cd lab6-cdk

# Initialize CDK project (TypeScript)
cdk init app --language typescript

# Install dependencies
npm install
```

### Step 2: Create CDK Stack

Replace `lib/lab6-cdk-stack.ts`:

```typescript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class Lab6CdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const table = new dynamodb.Table(this, 'ItemsTable', {
      tableName: 'lab6-items',
      partitionKey: {
        name: 'id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // S3 Bucket
    const bucket = new s3.Bucket(this, 'DataBucket', {
      bucketName: `lab6-data-${this.account}-${this.region}`,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // Lambda Function
    const handler = new lambda.Function(this, 'ApiHandler', {
      functionName: 'lab6-api-handler',
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    method = event.get('httpMethod', '')

    if method == 'GET':
        response = table.scan()
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response.get('Items', []))
        }

    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        item = {
            'id': context.aws_request_id,
            **body
        }
        table.put_item(Item=item)
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(item)
        }

    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Invalid method'})
    }
`),
      environment: {
        TABLE_NAME: table.tableName,
        BUCKET_NAME: bucket.bucketName,
      },
      timeout: cdk.Duration.seconds(30),
    });

    // Grant permissions
    table.grantReadWriteData(handler);
    bucket.grantReadWrite(handler);

    // API Gateway
    const api = new apigateway.RestApi(this, 'ItemsApi', {
      restApiName: 'Lab 6 Items API',
      description: 'API created with CDK',
      deployOptions: {
        stageName: 'prod',
      },
    });

    const items = api.root.addResource('items');
    items.addMethod('GET', new apigateway.LambdaIntegration(handler));
    items.addMethod('POST', new apigateway.LambdaIntegration(handler));

    // Outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint',
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: table.tableName,
      description: 'DynamoDB Table name',
    });

    new cdk.CfnOutput(this, 'BucketName', {
      value: bucket.bucketName,
      description: 'S3 Bucket name',
    });
  }
}
```

### Step 3: Bootstrap and Deploy

```bash
# Bootstrap CDK (first time only)
cdk bootstrap

# Synthesize CloudFormation template
cdk synth

# View the generated template
cat cdk.out/Lab6CdkStack.template.json | jq .

# Compare with what's deployed (nothing yet)
cdk diff

# Deploy
cdk deploy --require-approval never
```

### Step 4: Test the Deployment

```bash
# Get the API endpoint
API_URL=$(aws cloudformation describe-stacks \
  --stack-name Lab6CdkStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

echo "API URL: ${API_URL}"

# Test GET
curl ${API_URL}items

# Test POST
curl -X POST ${API_URL}items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "Created via CDK"}'

# Test GET again
curl ${API_URL}items
```

### Step 5: Make a Change and Update

Modify the stack to add a new output, then:

```bash
# See the diff
cdk diff

# Deploy the change
cdk deploy
```

### Lab 6 Checkpoint

You should now have:
- [ ] CDK project created and deployed
- [ ] Understanding of CDK constructs
- [ ] Experience with CDK workflow

---

## Lab 7: Drift Detection and Remediation

### Objective
Learn to detect and remediate configuration drift.

### Duration: 30 minutes

---

### Step 1: Create Stack for Drift Testing

Create `lab7-drift-test.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Lab 7 - Drift Detection Test'

Resources:
  DriftTestBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'lab7-drift-test-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled
      Tags:
        - Key: Purpose
          Value: DriftTest
        - Key: ManagedBy
          Value: CloudFormation

  DriftTestQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: lab7-drift-test-queue
      VisibilityTimeoutSeconds: 60
      MessageRetentionPeriod: 345600

Outputs:
  BucketName:
    Value: !Ref DriftTestBucket
  QueueUrl:
    Value: !Ref DriftTestQueue
```

```bash
# Deploy stack
aws cloudformation create-stack \
  --stack-name lab7-drift \
  --template-body file://lab7-drift-test.yaml

aws cloudformation wait stack-create-complete --stack-name lab7-drift
```

### Step 2: Introduce Drift

```bash
# Get bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name lab7-drift \
  --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
  --output text)

# Introduce drift by disabling versioning (should be Enabled)
aws s3api put-bucket-versioning \
  --bucket ${BUCKET_NAME} \
  --versioning-configuration Status=Suspended

# Add a tag manually (not in template)
aws s3api put-bucket-tagging \
  --bucket ${BUCKET_NAME} \
  --tagging 'TagSet=[{Key=ManualTag,Value=AddedManually},{Key=Purpose,Value=DriftTest},{Key=ManagedBy,Value=CloudFormation}]'

# Modify SQS queue
QUEUE_URL=$(aws cloudformation describe-stacks \
  --stack-name lab7-drift \
  --query 'Stacks[0].Outputs[?OutputKey==`QueueUrl`].OutputValue' \
  --output text)

aws sqs set-queue-attributes \
  --queue-url ${QUEUE_URL} \
  --attributes VisibilityTimeout=120

echo "Drift introduced!"
```

### Step 3: Detect Drift

```bash
# Initiate drift detection
DRIFT_ID=$(aws cloudformation detect-stack-drift \
  --stack-name lab7-drift \
  --query 'StackDriftDetectionId' \
  --output text)

echo "Drift Detection ID: ${DRIFT_ID}"

# Wait for detection to complete
aws cloudformation describe-stack-drift-detection-status \
  --stack-drift-detection-id ${DRIFT_ID}

# Get drift status for stack
aws cloudformation describe-stack-resource-drifts \
  --stack-name lab7-drift

# Get detailed drift for specific resource
aws cloudformation describe-stack-resource-drifts \
  --stack-name lab7-drift \
  --stack-resource-drift-status-filters MODIFIED \
  --query 'StackResourceDrifts[].{Resource:LogicalResourceId,Status:StackResourceDriftStatus,Differences:PropertyDifferences}'
```

### Step 4: Remediate Drift

```bash
# Option 1: Update stack to match current state
# (Update template to reflect current values)

# Option 2: Fix resources to match template (recommended)
# Re-enable versioning
aws s3api put-bucket-versioning \
  --bucket ${BUCKET_NAME} \
  --versioning-configuration Status=Enabled

# Restore original tags
aws s3api put-bucket-tagging \
  --bucket ${BUCKET_NAME} \
  --tagging 'TagSet=[{Key=Purpose,Value=DriftTest},{Key=ManagedBy,Value=CloudFormation}]'

# Restore SQS attributes
aws sqs set-queue-attributes \
  --queue-url ${QUEUE_URL} \
  --attributes VisibilityTimeout=60

# Re-run drift detection
aws cloudformation detect-stack-drift --stack-name lab7-drift

# Verify drift is resolved
aws cloudformation describe-stack-resource-drifts \
  --stack-name lab7-drift
```

### Lab 7 Checkpoint

You should now understand:
- [ ] How to detect configuration drift
- [ ] How to analyze drift details
- [ ] How to remediate drift

---

## Lab 8: Complete Cleanup

### Objective
Clean up all resources created during the labs.

### Duration: 15 minutes

---

### Step 1: List All Lab Stacks

```bash
# List all lab stacks
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query 'StackSummaries[?contains(StackName, `lab`)].StackName' \
  --output table
```

### Step 2: Delete Stacks in Correct Order

```bash
# Delete dependent stacks first

# Lab 5: Consumer before Shared
aws cloudformation delete-stack --stack-name lab5-consumer
aws cloudformation wait stack-delete-complete --stack-name lab5-consumer

aws cloudformation delete-stack --stack-name lab5-shared
aws cloudformation wait stack-delete-complete --stack-name lab5-shared

# Lab 7: Drift test
aws cloudformation delete-stack --stack-name lab7-drift
aws cloudformation wait stack-delete-complete --stack-name lab7-drift

# Lab 6: CDK stack
cd lab6-cdk
cdk destroy --force
cd ..

# Lab 4: Nested stacks (root stack deletes children)
aws cloudformation delete-stack --stack-name lab4-nested
aws cloudformation wait stack-delete-complete --stack-name lab4-nested

# Empty and delete template bucket
aws s3 rm s3://${TEMPLATE_BUCKET} --recursive
aws s3 rb s3://${TEMPLATE_BUCKET}

# Lab 3: Change set
aws cloudformation delete-stack --stack-name lab3-changeset
aws cloudformation wait stack-delete-complete --stack-name lab3-changeset

# Lab 2: Production and Development
aws cloudformation delete-stack --stack-name lab2-production
aws cloudformation delete-stack --stack-name lab2-development
aws cloudformation wait stack-delete-complete --stack-name lab2-production
aws cloudformation wait stack-delete-complete --stack-name lab2-development

# Lab 1: Basic stacks
aws cloudformation delete-stack --stack-name lab1-cli-stack
aws cloudformation delete-stack --stack-name lab1-basic-stack
aws cloudformation wait stack-delete-complete --stack-name lab1-cli-stack
aws cloudformation wait stack-delete-complete --stack-name lab1-basic-stack

echo "All lab resources cleaned up!"
```

### Step 3: Verify Cleanup

```bash
# Verify no lab stacks remain
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query 'StackSummaries[?contains(StackName, `lab`)].StackName'

# Check for any failed deletions
aws cloudformation list-stacks \
  --stack-status-filter DELETE_FAILED \
  --query 'StackSummaries[?contains(StackName, `lab`)].StackName'
```

---

## Lab Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lab Completion Checklist                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [ ] Lab 1: Basic Stack Operations                              │
│      - Created stacks via Console and CLI                       │
│      - Explored stack resources and outputs                     │
│                                                                  │
│  [ ] Lab 2: Parameters, Mappings, and Conditions                │
│      - Used mappings for environment config                     │
│      - Applied conditions for resource creation                 │
│                                                                  │
│  [ ] Lab 3: Change Sets                                         │
│      - Created and reviewed change sets                         │
│      - Understood replacement vs modification                   │
│                                                                  │
│  [ ] Lab 4: Nested Stacks                                       │
│      - Created child stack templates                            │
│      - Deployed root stack with nested stacks                   │
│      - Passed outputs between stacks                            │
│                                                                  │
│  [ ] Lab 5: Cross-Stack References                              │
│      - Exported values from one stack                           │
│      - Imported values in another stack                         │
│      - Understood dependency implications                       │
│                                                                  │
│  [ ] Lab 6: AWS CDK                                             │
│      - Initialized CDK project                                  │
│      - Deployed infrastructure with CDK                         │
│      - Tested the deployed API                                  │
│                                                                  │
│  [ ] Lab 7: Drift Detection                                     │
│      - Introduced configuration drift                           │
│      - Detected and analyzed drift                              │
│      - Remediated drifted resources                             │
│                                                                  │
│  [ ] Lab 8: Cleanup                                             │
│      - Deleted all lab resources                                │
│      - Verified complete cleanup                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting Common Issues

### Stack Creation Fails

```bash
# Check events for error details
aws cloudformation describe-stack-events \
  --stack-name STACK_NAME \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

### Stack Deletion Fails

```bash
# Check for protected resources
aws cloudformation describe-stack-resources \
  --stack-name STACK_NAME \
  --query 'StackResources[?ResourceStatus==`DELETE_FAILED`]'

# Force delete with retain
aws cloudformation delete-stack \
  --stack-name STACK_NAME \
  --retain-resources ResourceLogicalId1 ResourceLogicalId2
```

### Permission Errors

```bash
# Verify IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names cloudformation:CreateStack \
  --resource-arns '*'
```

### Template Validation Errors

```bash
# Validate template
aws cloudformation validate-template \
  --template-body file://template.yaml

# Use cfn-lint for detailed validation
cfn-lint template.yaml
```

---

## Next Steps

1. **Practice**: Recreate these labs in your own environment
2. **Extend**: Add more resources to the templates
3. **Explore**: AWS Solutions Library for more complex templates
4. **Certify**: Use this knowledge for AWS certifications

---

**Congratulations!** You have completed Module 9: CloudFormation and Infrastructure as Code.

**Return to**: [Module Overview](./README.md)
