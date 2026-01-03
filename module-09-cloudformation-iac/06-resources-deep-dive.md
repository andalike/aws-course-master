# Lesson 06: Resources Deep Dive

## Introduction

The Resources section is the heart of every CloudFormation template. It defines the AWS resources to create and their configurations. This lesson provides an in-depth exploration of resource definitions, properties, attributes, and advanced features like DependsOn, DeletionPolicy, and UpdatePolicy.

---

## Resource Structure

Every resource follows this structure:

```yaml
Resources:
  LogicalResourceId:                    # Unique identifier
    Type: AWS::Service::Resource        # Resource type
    Properties:                         # Resource configuration
      PropertyName: PropertyValue

    # Optional attributes
    Condition: ConditionName            # Conditional creation
    DependsOn:                          # Explicit dependencies
      - OtherResource
    DeletionPolicy: Retain              # Deletion behavior
    UpdatePolicy:                       # Update behavior
      Key: Value
    UpdateReplacePolicy: Retain         # Replacement behavior
    CreationPolicy:                     # Wait for signals
      ResourceSignal:
        Count: 1
        Timeout: PT15M
    Metadata:                           # Resource metadata
      Key: Value
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    Resource Anatomy                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LogicalResourceId (MyWebServer)                                │
│  ├── Type: AWS::EC2::Instance                                   │
│  ├── Properties:                                                │
│  │   ├── InstanceType: t3.micro                                │
│  │   ├── ImageId: ami-12345678                                 │
│  │   └── Tags: [...]                                           │
│  ├── DeletionPolicy: Retain                                    │
│  ├── DependsOn: [Database]                                     │
│  └── Metadata:                                                  │
│      └── AWS::CloudFormation::Init: {...}                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Resource Types

### Resource Type Format

```
AWS::ServiceName::ResourceType

Examples:
AWS::EC2::Instance
AWS::S3::Bucket
AWS::Lambda::Function
AWS::RDS::DBInstance
AWS::IAM::Role
AWS::CloudFormation::Stack
```

### Common Resource Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    Common Resource Types                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Compute                    Storage                              │
│  ├── AWS::EC2::Instance     ├── AWS::S3::Bucket                 │
│  ├── AWS::Lambda::Function  ├── AWS::EBS::Volume                │
│  ├── AWS::ECS::Service      └── AWS::EFS::FileSystem            │
│  └── AWS::AutoScaling::                                         │
│      AutoScalingGroup                                           │
│                                                                  │
│  Network                    Database                             │
│  ├── AWS::EC2::VPC          ├── AWS::RDS::DBInstance            │
│  ├── AWS::EC2::Subnet       ├── AWS::DynamoDB::Table            │
│  ├── AWS::EC2::SecurityGroup└── AWS::ElastiCache::              │
│  └── AWS::ElasticLoadBalancingV2::LoadBalancer  CacheCluster    │
│                                                                  │
│  Security                   Messaging                            │
│  ├── AWS::IAM::Role         ├── AWS::SQS::Queue                 │
│  ├── AWS::IAM::Policy       ├── AWS::SNS::Topic                 │
│  └── AWS::KMS::Key          └── AWS::Events::Rule               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Resource Properties

### Required vs Optional Properties

Each resource type has specific properties:

```yaml
Resources:
  # EC2 Instance - ImageId is required, others optional
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-12345678          # Required
      InstanceType: t3.micro         # Optional (has default)
      KeyName: my-key                # Optional
      SubnetId: !Ref MySubnet        # Optional but recommended

  # S3 Bucket - No required properties
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-unique-bucket   # Optional (auto-generated if omitted)

  # Lambda Function - Multiple required properties
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function      # Optional
      Runtime: python3.9             # Required
      Handler: index.handler         # Required
      Role: !GetAtt LambdaRole.Arn   # Required
      Code:                          # Required
        ZipFile: |
          def handler(event, context):
              return "Hello"
```

### Property Value Types

```yaml
Resources:
  ExampleResource:
    Type: AWS::Example::Resource
    Properties:
      # String
      StringProperty: "value"

      # Number
      NumberProperty: 100

      # Boolean
      BooleanProperty: true

      # List (Array)
      ListProperty:
        - item1
        - item2
        - item3

      # Map (Object)
      MapProperty:
        Key1: Value1
        Key2: Value2

      # Reference
      ReferenceProperty: !Ref OtherResource

      # GetAtt
      AttributeProperty: !GetAtt OtherResource.Arn

      # Nested Structure
      NestedProperty:
        SubProperty1: value1
        SubProperty2:
          - nested1
          - nested2
```

---

## Common Resource Examples

### VPC Resources

```yaml
Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      InstanceTenancy: default
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-VPC'

  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-IGW'

  # Attach Internet Gateway
  GatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-PublicSubnet'

  # Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-PublicRT'

  # Route to Internet
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: GatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  # Associate Route Table
  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable
```

### EC2 Instance with Security Group

```yaml
Resources:
  # Security Group
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web server
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: !Ref SSHLocation
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-WebSG'

  # EC2 Instance
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !Ref AMI
      KeyName: !Ref KeyName
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      IamInstanceProfile: !Ref InstanceProfile
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: 20
            VolumeType: gp3
            Encrypted: true
            DeleteOnTermination: true
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from ${AWS::StackName}</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-WebServer'
```

### RDS Database

```yaml
Resources:
  # DB Subnet Group
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-DBSubnetGroup'

  # DB Security Group
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref WebServerSecurityGroup

  # RDS Instance
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${AWS::StackName}-db'
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      DBName: !Ref DBName
      AllocatedStorage: 20
      MaxAllocatedStorage: 100
      StorageType: gp2
      StorageEncrypted: true
      MultiAZ: !If [IsProduction, true, false]
      PubliclyAccessible: false
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      BackupRetentionPeriod: !If [IsProduction, 7, 1]
      DeletionProtection: !If [IsProduction, true, false]
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-Database'
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
```

### Lambda Function with Role

```yaml
Resources:
  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${AWS::StackName}-LambdaRole'
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
        - PolicyName: S3Access
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                Resource: !Sub '${DataBucket.Arn}/*'

  # Lambda Function
  ProcessingFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${AWS::StackName}-Processor'
      Runtime: python3.9
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Timeout: 30
      MemorySize: 256
      Environment:
        Variables:
          BUCKET_NAME: !Ref DataBucket
          ENVIRONMENT: !Ref Environment
      Code:
        ZipFile: |
          import json
          import boto3
          import os

          def handler(event, context):
              bucket = os.environ['BUCKET_NAME']
              env = os.environ['ENVIRONMENT']

              return {
                  'statusCode': 200,
                  'body': json.dumps({
                      'message': f'Processing in {env}',
                      'bucket': bucket
                  })
              }
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

---

## DependsOn

Explicitly specify that a resource depends on another resource.

### When to Use DependsOn

```yaml
# CloudFormation automatically handles most dependencies
# DependsOn is needed when:
# 1. Dependencies aren't expressed through Ref/GetAtt
# 2. Order matters for reasons CloudFormation can't detect

Resources:
  # Example 1: Route depends on Gateway Attachment
  # (Not expressed through Ref/GetAtt)
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: GatewayAttachment  # Explicit dependency required
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  # Example 2: Lambda needs VPC endpoints first
  LambdaFunction:
    Type: AWS::Lambda::Function
    DependsOn:
      - S3VPCEndpoint
      - DynamoDBVPCEndpoint
    Properties:
      FunctionName: my-function
      # ...

  # Example 3: RDS needs NAT Gateway for downloads
  Database:
    Type: AWS::RDS::DBInstance
    DependsOn: NATGateway
    Properties:
      # ...
```

### DependsOn vs Implicit Dependencies

```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  # IMPLICIT dependency - CloudFormation knows Subnet needs VPC
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC  # Creates implicit dependency
      CidrBlock: 10.0.1.0/24

  IGW:
    Type: AWS::EC2::InternetGateway

  # EXPLICIT dependency needed - no Ref/GetAtt to VPC
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref IGW

  # EXPLICIT dependency - Route needs attachment complete
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway  # Must wait for attachment
    Properties:
      RouteTableId: !Ref RouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref IGW
```

### Multiple Dependencies

```yaml
Resources:
  MyResource:
    Type: AWS::SomeService::Resource
    DependsOn:
      - Dependency1
      - Dependency2
      - Dependency3
    Properties:
      # ...
```

---

## DeletionPolicy

Controls what happens to a resource when it's deleted from the stack.

### DeletionPolicy Options

```yaml
Resources:
  # Delete - Default behavior, resource is deleted
  TemporaryResource:
    Type: AWS::S3::Bucket
    DeletionPolicy: Delete
    Properties:
      BucketName: temporary-bucket

  # Retain - Resource is kept, removed from stack management
  ImportantBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      BucketName: important-data-bucket

  # Snapshot - Create snapshot before deletion (RDS, EBS, etc.)
  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: production-db
      # ...

  # RetainExceptOnCreate - New in 2023
  # Retain on update/delete, but delete on create failure
  NewResource:
    Type: AWS::S3::Bucket
    DeletionPolicy: RetainExceptOnCreate
```

### DeletionPolicy Reference

| Value | Behavior | Use Case |
|-------|----------|----------|
| `Delete` | Resource deleted | Temporary resources |
| `Retain` | Resource kept | Production data |
| `Snapshot` | Snapshot created | Databases, volumes |
| `RetainExceptOnCreate` | Retain unless create fails | Safe deployments |

### Production Example

```yaml
Resources:
  # Production S3 bucket - retain data
  ProductionDataBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      BucketName: !Sub 'prod-data-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled

  # Production RDS - create snapshot
  ProductionDatabase:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      DBInstanceIdentifier: prod-database
      DeletionProtection: true
      # ...

  # Production EBS volume - snapshot
  DataVolume:
    Type: AWS::EC2::Volume
    DeletionPolicy: Snapshot
    Properties:
      AvailabilityZone: !GetAtt EC2Instance.AvailabilityZone
      Size: 100
      Encrypted: true

  # CloudWatch Log Group - retain logs
  ApplicationLogs:
    Type: AWS::Logs::LogGroup
    DeletionPolicy: Retain
    Properties:
      LogGroupName: !Sub '/aws/${AWS::StackName}/application'
      RetentionInDays: 365
```

---

## UpdatePolicy

Controls how resources are updated, particularly for Auto Scaling Groups.

### AutoScalingRollingUpdate

```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    UpdatePolicy:
      AutoScalingRollingUpdate:
        # Minimum instances in service during update
        MinInstancesInService: 1

        # Maximum instances updated at once
        MaxBatchSize: 1

        # Pause time between batches
        PauseTime: PT5M

        # Wait for signals before proceeding
        WaitOnResourceSignals: true

        # Suspend processes during update
        SuspendProcesses:
          - HealthCheck
          - ReplaceUnhealthy
          - AZRebalance
          - AlarmNotification
          - ScheduledActions
    Properties:
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 4
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

### AutoScalingReplacingUpdate

```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    UpdatePolicy:
      AutoScalingReplacingUpdate:
        # Replace entire ASG
        WillReplace: true
    Properties:
      # ...
```

### AutoScalingScheduledAction

```yaml
Resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    UpdatePolicy:
      AutoScalingScheduledAction:
        # Ignore scheduled action differences during update
        IgnoreDifferences: true
    Properties:
      # ...
```

### Complete ASG Example

```yaml
Resources:
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub '${AWS::StackName}-LaunchTemplate'
      LaunchTemplateData:
        ImageId: !Ref AMI
        InstanceType: !Ref InstanceType
        KeyName: !Ref KeyName
        SecurityGroupIds:
          - !Ref WebServerSG
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            yum install -y httpd
            systemctl start httpd
            systemctl enable httpd

            # Signal CloudFormation
            /opt/aws/bin/cfn-signal -e $? \
              --stack ${AWS::StackName} \
              --resource AutoScalingGroup \
              --region ${AWS::Region}

  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    CreationPolicy:
      ResourceSignal:
        Count: !Ref DesiredCapacity
        Timeout: PT15M
    UpdatePolicy:
      AutoScalingRollingUpdate:
        MinInstancesInService: !Ref MinSize
        MaxBatchSize: 1
        PauseTime: PT10M
        WaitOnResourceSignals: true
        SuspendProcesses:
          - HealthCheck
          - ReplaceUnhealthy
    Properties:
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: !Ref MinSize
      MaxSize: !Ref MaxSize
      DesiredCapacity: !Ref DesiredCapacity
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-ASG-Instance'
          PropagateAtLaunch: true
```

---

## UpdateReplacePolicy

Controls what happens when a resource is replaced during an update.

```yaml
Resources:
  # Keep old resource when replaced
  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot  # Create snapshot when replaced
    Properties:
      DBInstanceIdentifier: my-database
      # ...

  # Retain old S3 bucket when replaced
  DataBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain  # Keep old bucket when replaced
    Properties:
      BucketName: my-data-bucket
```

### When Resources Get Replaced

Some property changes require replacement:

```yaml
# Example: Changing these properties requires replacement
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # Changes that DON'T require replacement:
      InstanceType: t3.small  # Modifiable (with restart)
      Tags: [...]             # Modifiable

      # Changes that DO require replacement:
      AvailabilityZone: us-east-1a  # Requires replacement
      SubnetId: subnet-123          # Requires replacement
```

---

## CreationPolicy

Wait for signals from resources before marking as complete.

```yaml
Resources:
  # EC2 Instance with CreationPolicy
  WebServer:
    Type: AWS::EC2::Instance
    CreationPolicy:
      ResourceSignal:
        Count: 1           # Number of signals to wait for
        Timeout: PT15M     # Wait up to 15 minutes
    Properties:
      ImageId: !Ref AMI
      InstanceType: t3.micro
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd

          # Start web server
          systemctl start httpd
          systemctl enable httpd

          # Signal success to CloudFormation
          /opt/aws/bin/cfn-signal -e $? \
            --stack ${AWS::StackName} \
            --resource WebServer \
            --region ${AWS::Region}

  # Auto Scaling Group with CreationPolicy
  ASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    CreationPolicy:
      ResourceSignal:
        Count: 2           # Wait for 2 instances
        Timeout: PT15M
    Properties:
      MinSize: 2
      MaxSize: 4
      DesiredCapacity: 2
      # ...
```

### Signal Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CreationPolicy Signal Flow                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CloudFormation                    EC2 Instance                  │
│       │                                 │                        │
│       │ 1. Create Instance              │                        │
│       ├────────────────────────────────►│                        │
│       │                                 │                        │
│       │ 2. Wait for signals             │ 3. Instance boots     │
│       │    (Timeout: PT15M)             │    and configures     │
│       │                                 │                        │
│       │                                 │ 4. cfn-signal         │
│       │◄────────────────────────────────┤    sends result       │
│       │                                 │                        │
│       │ 5. Mark as CREATE_COMPLETE      │                        │
│       │    or FAILED                    │                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Resource Metadata

Add metadata to resources for various purposes.

### AWS::CloudFormation::Init

Configuration for cfn-init helper script:

```yaml
Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Metadata:
      AWS::CloudFormation::Init:
        configSets:
          default:
            - install
            - configure
            - start

        install:
          packages:
            yum:
              httpd: []
              php: []
              mysql: []

        configure:
          files:
            /var/www/html/index.html:
              content: |
                <html>
                  <body>
                    <h1>Hello World</h1>
                  </body>
                </html>
              mode: '000644'
              owner: apache
              group: apache

        start:
          services:
            sysvinit:
              httpd:
                enabled: true
                ensureRunning: true
    Properties:
      # ...
```

### Custom Metadata

```yaml
Resources:
  Database:
    Type: AWS::RDS::DBInstance
    Metadata:
      # Documentation
      Description: Production MySQL database
      Owner: database-team@company.com
      LastReviewed: '2024-01-15'

      # Tool-specific metadata
      cfn-lint:
        config:
          ignore_checks:
            - W3011
    Properties:
      # ...
```

---

## Resource Attributes Quick Reference

| Attribute | Purpose | Applies To |
|-----------|---------|------------|
| `DependsOn` | Explicit dependency | All resources |
| `DeletionPolicy` | Deletion behavior | All resources |
| `UpdateReplacePolicy` | Replacement behavior | All resources |
| `UpdatePolicy` | Update behavior | ASG, Lambda Alias |
| `CreationPolicy` | Wait for signals | EC2, ASG, WaitCondition |
| `Condition` | Conditional creation | All resources |
| `Metadata` | Additional data | All resources |

---

## Best Practices

### 1. Use Appropriate DeletionPolicy

```yaml
# Development - allow cleanup
Resources:
  DevBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Delete  # OK for dev

# Production - protect data
  ProdBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain

# Databases - always snapshot
  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
```

### 2. Minimize DependsOn Usage

```yaml
# Let CloudFormation detect dependencies through Ref/GetAtt
# Only use DependsOn when necessary

Resources:
  # BAD: Unnecessary DependsOn
  Subnet:
    Type: AWS::EC2::Subnet
    DependsOn: VPC  # Not needed - VpcId creates implicit dependency
    Properties:
      VpcId: !Ref VPC

  # GOOD: Implicit dependency
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC  # CloudFormation knows to create VPC first
```

### 3. Use CreationPolicy for Configuration Verification

```yaml
Resources:
  WebServer:
    Type: AWS::EC2::Instance
    CreationPolicy:
      ResourceSignal:
        Count: 1
        Timeout: PT10M
    Properties:
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          # Install and configure
          yum install -y httpd
          systemctl start httpd

          # Verify configuration before signaling
          if curl -s http://localhost | grep -q "Hello"; then
            /opt/aws/bin/cfn-signal -e 0 --stack ${AWS::StackName} \
              --resource WebServer --region ${AWS::Region}
          else
            /opt/aws/bin/cfn-signal -e 1 --stack ${AWS::StackName} \
              --resource WebServer --region ${AWS::Region}
          fi
```

### 4. Tag All Resources

```yaml
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      # ...
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-webserver'
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: !Ref OwnerEmail
        - Key: CostCenter
          Value: !Ref CostCenter
        - Key: ManagedBy
          Value: CloudFormation
```

---

## Complete Example

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Resources Deep Dive Example

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

  InstanceType:
    Type: String
    Default: t3.micro

Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']

Resources:
  # VPC with standard configuration
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-VPC'

  # S3 Bucket with appropriate deletion policy
  DataBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: !If [IsProduction, Retain, Delete]
    UpdateReplacePolicy: !If [IsProduction, Retain, Delete]
    Properties:
      BucketName: !Sub '${AWS::StackName}-data-${AWS::AccountId}'
      VersioningConfiguration:
        Status: !If [IsProduction, Enabled, Suspended]
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # EC2 Instance with CreationPolicy
  WebServer:
    Type: AWS::EC2::Instance
    DependsOn: GatewayAttachment
    CreationPolicy:
      ResourceSignal:
        Count: 1
        Timeout: PT10M
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !Ref LatestAmiId
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSG
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-WebServer'
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from ${Environment}</h1>" > /var/www/html/index.html

          /opt/aws/bin/cfn-signal -e $? \
            --stack ${AWS::StackName} \
            --resource WebServer \
            --region ${AWS::Region}

  # RDS with Snapshot deletion policy
  Database:
    Type: AWS::RDS::DBInstance
    Condition: IsProduction
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub '${AWS::StackName}-db'
      DBInstanceClass: db.t3.micro
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      MultiAZ: true
      DeletionProtection: true
      Tags:
        - Key: Environment
          Value: !Ref Environment

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  BucketName:
    Description: S3 Bucket Name
    Value: !Ref DataBucket

  WebServerIP:
    Description: Web Server Public IP
    Value: !GetAtt WebServer.PublicIp
```

---

## Knowledge Check

1. What is the difference between DeletionPolicy and UpdateReplacePolicy?
2. When should you use explicit DependsOn?
3. What does CreationPolicy do?
4. How does UpdatePolicy work with Auto Scaling Groups?
5. What are the three DeletionPolicy options?

---

**Next:** [07 - Nested Stacks](./07-nested-stacks.md)

**Previous:** [05 - Parameters and Mappings](./05-parameters-and-mappings.md)
