# Lesson 07: Nested Stacks

## Introduction

As your CloudFormation templates grow in complexity, managing them becomes challenging. Nested stacks provide a way to break down large templates into smaller, reusable components. This lesson covers nested stack architecture, when to use them, and how to implement them effectively.

---

## What Are Nested Stacks?

Nested stacks are CloudFormation stacks created as part of other stacks. You create a nested stack within another stack by using the `AWS::CloudFormation::Stack` resource.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Nested Stack Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌─────────────────────┐                      │
│                    │    Root Stack       │                      │
│                    │   (Parent Stack)    │                      │
│                    └──────────┬──────────┘                      │
│                               │                                  │
│           ┌───────────────────┼───────────────────┐             │
│           │                   │                   │             │
│           ▼                   ▼                   ▼             │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐    │
│   │ Network Stack │   │ Security Stack│   │ App Stack     │    │
│   │  (VPC, Subnet)│   │ (SG, IAM)     │   │ (EC2, ALB)    │    │
│   └───────────────┘   └───────────────┘   └───────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Concepts

| Term | Description |
|------|-------------|
| **Root Stack** | The top-level stack that contains nested stacks |
| **Parent Stack** | A stack that contains nested stacks |
| **Nested Stack** | A stack created within another stack |
| **Child Stack** | Another term for nested stack |

---

## When to Use Nested Stacks

### Use Cases

```
┌─────────────────────────────────────────────────────────────────┐
│                   When to Use Nested Stacks                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. TEMPLATE SIZE LIMITS                                        │
│     └── Template exceeds 51KB body or 1MB S3 limit              │
│                                                                  │
│  2. REUSABLE COMPONENTS                                         │
│     └── VPC, security groups used across multiple stacks        │
│                                                                  │
│  3. SEPARATION OF CONCERNS                                      │
│     └── Different teams manage different components             │
│                                                                  │
│  4. LIFECYCLE MANAGEMENT                                        │
│     └── Components updated independently                        │
│                                                                  │
│  5. RESOURCE LIMITS                                             │
│     └── Approaching 500 resources per stack limit               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Nested Stacks vs Cross-Stack References

| Feature | Nested Stacks | Cross-Stack References |
|---------|--------------|------------------------|
| **Lifecycle** | Managed together | Independent |
| **Reusability** | Template reuse | Output value sharing |
| **Updates** | Parent controls | Independent updates |
| **Deletion** | Delete parent = delete all | Must remove dependencies first |
| **Use Case** | Component isolation | Shared infrastructure |

---

## Creating Nested Stacks

### Basic Syntax

```yaml
Resources:
  NestedStackResource:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/template.yaml
      Parameters:
        ParameterKey1: ParameterValue1
        ParameterKey2: ParameterValue2
      TimeoutInMinutes: 60
      Tags:
        - Key: Environment
          Value: Production
```

### Required Properties

| Property | Description | Required |
|----------|-------------|----------|
| `TemplateURL` | S3 URL of the nested template | Yes |
| `Parameters` | Input parameters for nested stack | No |
| `TimeoutInMinutes` | Stack creation timeout | No |
| `NotificationARNs` | SNS topic ARNs for notifications | No |
| `Tags` | Tags to apply to nested stack | No |

---

## Hands-On Example: Three-Tier Application

Let's create a three-tier application using nested stacks.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Three-Tier Application                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  root-stack.yaml                                                │
│  ├── network-stack.yaml (VPC, Subnets, Internet Gateway)       │
│  ├── security-stack.yaml (Security Groups, IAM Roles)          │
│  ├── database-stack.yaml (RDS Instance)                         │
│  └── application-stack.yaml (EC2, ALB, Auto Scaling)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Network Stack (network-stack.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Network Stack - VPC, Subnets, and Internet Gateway'

Parameters:
  EnvironmentName:
    Type: String
    Default: dev
    Description: Environment name prefix

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: VPC CIDR block

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-vpc'

  # Internet Gateway
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

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [0, !Cidr [!Ref VPCCidr, 6, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-subnet-1'

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [1, !Cidr [!Ref VPCCidr, 6, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-subnet-2'

  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Select [2, !Cidr [!Ref VPCCidr, 6, 8]]
      MapPublicIpOnLaunch: false
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-subnet-1'

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Select [3, !Cidr [!Ref VPCCidr, 6, 8]]
      MapPublicIpOnLaunch: false
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-subnet-2'

  # Public Route Table
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

  # NAT Gateway (for private subnets)
  NatGatewayEIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-nat-eip'

  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGatewayEIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-nat-gw'

  # Private Route Table
  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-rt'

  DefaultPrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !Ref PrivateRouteTable

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

  PrivateSubnet1Id:
    Description: Private Subnet 1 ID
    Value: !Ref PrivateSubnet1

  PrivateSubnet2Id:
    Description: Private Subnet 2 ID
    Value: !Ref PrivateSubnet2

  VPCCidrBlock:
    Description: VPC CIDR Block
    Value: !Ref VPCCidr
```

### Step 2: Security Stack (security-stack.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Security Stack - Security Groups and IAM Roles'

Parameters:
  EnvironmentName:
    Type: String
    Description: Environment name prefix

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  VPCCidr:
    Type: String
    Description: VPC CIDR block

Resources:
  # ALB Security Group
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Application Load Balancer
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-alb-sg'

  # Web Server Security Group
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for web servers
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          SourceSecurityGroupId: !Ref ALBSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-web-sg'

  # Database Security Group
  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for database
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-db-sg'

  # EC2 Instance Role
  EC2InstanceRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${EnvironmentName}-ec2-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-ec2-role'

  # Instance Profile
  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub '${EnvironmentName}-ec2-instance-profile'
      Roles:
        - !Ref EC2InstanceRole

Outputs:
  ALBSecurityGroupId:
    Description: ALB Security Group ID
    Value: !Ref ALBSecurityGroup

  WebServerSecurityGroupId:
    Description: Web Server Security Group ID
    Value: !Ref WebServerSecurityGroup

  DatabaseSecurityGroupId:
    Description: Database Security Group ID
    Value: !Ref DatabaseSecurityGroup

  EC2InstanceProfileArn:
    Description: EC2 Instance Profile ARN
    Value: !GetAtt EC2InstanceProfile.Arn

  EC2InstanceProfileName:
    Description: EC2 Instance Profile Name
    Value: !Ref EC2InstanceProfile
```

### Step 3: Database Stack (database-stack.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Database Stack - RDS MySQL Instance'

Parameters:
  EnvironmentName:
    Type: String
    Description: Environment name prefix

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private Subnet 1 ID

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private Subnet 2 ID

  DatabaseSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: Database Security Group ID

  DBInstanceClass:
    Type: String
    Default: db.t3.micro
    AllowedValues:
      - db.t3.micro
      - db.t3.small
      - db.t3.medium
    Description: Database instance class

  DBName:
    Type: String
    Default: myappdb
    Description: Database name

  DBUsername:
    Type: String
    Default: admin
    NoEcho: true
    Description: Database admin username

  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database admin password

Resources:
  # DB Subnet Group
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-db-subnet-group'

  # RDS Instance
  DBInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub '${EnvironmentName}-mysql'
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
      MultiAZ: false
      PubliclyAccessible: false
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroupId
      BackupRetentionPeriod: 7
      DeleteAutomatedBackups: false
      DeletionProtection: false
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-mysql'

Outputs:
  DBInstanceEndpoint:
    Description: Database endpoint
    Value: !GetAtt DBInstance.Endpoint.Address

  DBInstancePort:
    Description: Database port
    Value: !GetAtt DBInstance.Endpoint.Port

  DBInstanceIdentifier:
    Description: Database instance identifier
    Value: !Ref DBInstance
```

### Step 4: Application Stack (application-stack.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Application Stack - EC2 Auto Scaling and ALB'

Parameters:
  EnvironmentName:
    Type: String
    Description: Environment name prefix

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PublicSubnet1Id:
    Type: AWS::EC2::Subnet::Id
    Description: Public Subnet 1 ID

  PublicSubnet2Id:
    Type: AWS::EC2::Subnet::Id
    Description: Public Subnet 2 ID

  PrivateSubnet1Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private Subnet 1 ID

  PrivateSubnet2Id:
    Type: AWS::EC2::Subnet::Id
    Description: Private Subnet 2 ID

  ALBSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: ALB Security Group ID

  WebServerSecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: Web Server Security Group ID

  EC2InstanceProfileName:
    Type: String
    Description: EC2 Instance Profile Name

  InstanceType:
    Type: String
    Default: t3.micro
    Description: EC2 instance type

  DBEndpoint:
    Type: String
    Description: Database endpoint

  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64

Resources:
  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${EnvironmentName}-alb'
      Type: application
      Scheme: internet-facing
      SecurityGroups:
        - !Ref ALBSecurityGroupId
      Subnets:
        - !Ref PublicSubnet1Id
        - !Ref PublicSubnet2Id
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-alb'

  # Target Group
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${EnvironmentName}-tg'
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPCId
      HealthCheckEnabled: true
      HealthCheckPath: /
      HealthCheckProtocol: HTTP
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 5
      TargetType: instance
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-tg'

  # ALB Listener
  ALBListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup

  # Launch Template
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub '${EnvironmentName}-launch-template'
      LaunchTemplateData:
        ImageId: !Ref LatestAmiId
        InstanceType: !Ref InstanceType
        IamInstanceProfile:
          Name: !Ref EC2InstanceProfileName
        SecurityGroupIds:
          - !Ref WebServerSecurityGroupId
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            yum install -y httpd
            systemctl start httpd
            systemctl enable httpd

            # Create a simple web page
            cat <<EOF > /var/www/html/index.html
            <!DOCTYPE html>
            <html>
            <head>
                <title>${EnvironmentName} Application</title>
            </head>
            <body>
                <h1>Welcome to ${EnvironmentName} Environment</h1>
                <p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>
                <p>Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)</p>
                <p>Database Endpoint: ${DBEndpoint}</p>
            </body>
            </html>
            EOF
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub '${EnvironmentName}-web-server'

  # Auto Scaling Group
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub '${EnvironmentName}-asg'
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 2
      MaxSize: 4
      DesiredCapacity: 2
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1Id
        - !Ref PrivateSubnet2Id
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-asg'
          PropagateAtLaunch: false

  # Scaling Policy - Scale Up
  ScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70

Outputs:
  ALBDNSName:
    Description: Application Load Balancer DNS Name
    Value: !GetAtt ApplicationLoadBalancer.DNSName

  ALBFullName:
    Description: Application Load Balancer Full Name
    Value: !GetAtt ApplicationLoadBalancer.LoadBalancerFullName

  AutoScalingGroupName:
    Description: Auto Scaling Group Name
    Value: !Ref AutoScalingGroup
```

### Step 5: Root Stack (root-stack.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Root Stack - Three-Tier Application with Nested Stacks'

Parameters:
  EnvironmentName:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Environment name

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: VPC CIDR block

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
    Description: EC2 instance type

  DBInstanceClass:
    Type: String
    Default: db.t3.micro
    AllowedValues:
      - db.t3.micro
      - db.t3.small
      - db.t3.medium
    Description: Database instance class

  DBUsername:
    Type: String
    Default: admin
    NoEcho: true
    Description: Database admin username

  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database admin password

  TemplatesBucket:
    Type: String
    Description: S3 bucket containing nested stack templates

Resources:
  # Network Stack
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/nested-stacks/network-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VPCCidr: !Ref VPCCidr
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-network-stack'

  # Security Stack
  SecurityStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/nested-stacks/security-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
        VPCCidr: !Ref VPCCidr
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-security-stack'

  # Database Stack
  DatabaseStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: SecurityStack
    Properties:
      TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/nested-stacks/database-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        PrivateSubnet1Id: !GetAtt NetworkStack.Outputs.PrivateSubnet1Id
        PrivateSubnet2Id: !GetAtt NetworkStack.Outputs.PrivateSubnet2Id
        DatabaseSecurityGroupId: !GetAtt SecurityStack.Outputs.DatabaseSecurityGroupId
        DBInstanceClass: !Ref DBInstanceClass
        DBUsername: !Ref DBUsername
        DBPassword: !Ref DBPassword
      TimeoutInMinutes: 30
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-database-stack'

  # Application Stack
  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: DatabaseStack
    Properties:
      TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/nested-stacks/application-stack.yaml'
      Parameters:
        EnvironmentName: !Ref EnvironmentName
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
        PublicSubnet1Id: !GetAtt NetworkStack.Outputs.PublicSubnet1Id
        PublicSubnet2Id: !GetAtt NetworkStack.Outputs.PublicSubnet2Id
        PrivateSubnet1Id: !GetAtt NetworkStack.Outputs.PrivateSubnet1Id
        PrivateSubnet2Id: !GetAtt NetworkStack.Outputs.PrivateSubnet2Id
        ALBSecurityGroupId: !GetAtt SecurityStack.Outputs.ALBSecurityGroupId
        WebServerSecurityGroupId: !GetAtt SecurityStack.Outputs.WebServerSecurityGroupId
        EC2InstanceProfileName: !GetAtt SecurityStack.Outputs.EC2InstanceProfileName
        InstanceType: !Ref InstanceType
        DBEndpoint: !GetAtt DatabaseStack.Outputs.DBInstanceEndpoint
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-application-stack'

Outputs:
  VPCId:
    Description: VPC ID
    Value: !GetAtt NetworkStack.Outputs.VPCId

  ApplicationURL:
    Description: Application URL
    Value: !Sub 'http://${ApplicationStack.Outputs.ALBDNSName}'

  DatabaseEndpoint:
    Description: Database Endpoint
    Value: !GetAtt DatabaseStack.Outputs.DBInstanceEndpoint
```

---

## Passing Parameters and Outputs

### Passing Parameters to Nested Stacks

```yaml
# In parent stack
Resources:
  NestedStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/template.yaml
      Parameters:
        # Pass parent parameter directly
        Environment: !Ref EnvironmentName

        # Pass hardcoded value
        InstanceType: t3.micro

        # Pass output from another nested stack
        VPCId: !GetAtt NetworkStack.Outputs.VPCId

        # Pass computed value
        BucketName: !Sub '${AWS::StackName}-data-bucket'
```

### Accessing Nested Stack Outputs

```yaml
# In parent stack
Outputs:
  # Get output from nested stack
  ApplicationURL:
    Description: Application URL
    Value: !GetAtt ApplicationStack.Outputs.ALBDNSName

  # Use in another resource
  MyResource:
    Type: AWS::SomeService::Resource
    Properties:
      TargetArn: !GetAtt NestedStack.Outputs.ResourceArn
```

### Syntax for Nested Stack Outputs

```
!GetAtt NestedStackLogicalId.Outputs.OutputKey
```

---

## Exporting Values for Cross-Stack References

Besides nested stacks, you can share values between independent stacks using exports.

### Exporting Values

```yaml
# In VPC stack (vpc-stack.yaml)
Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  PublicSubnet1:
    Description: Public Subnet 1
    Value: !Ref PublicSubnet1
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnet1'
```

### Importing Values

```yaml
# In application stack (app-stack.yaml)
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      SubnetId: !ImportValue 'vpc-stack-PublicSubnet1'
      # Or with Fn::ImportValue
      SubnetId:
        Fn::ImportValue: 'vpc-stack-PublicSubnet1'
```

### Export vs Nested Stack Outputs

```
┌─────────────────────────────────────────────────────────────────┐
│              Export vs Nested Stack Outputs                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Cross-Stack Export (ImportValue)                               │
│  ├── Independent stack lifecycle                                │
│  ├── Must delete dependent stacks first                         │
│  ├── Better for shared infrastructure                           │
│  └── Cannot update exported value while in use                  │
│                                                                  │
│  Nested Stack Outputs (GetAtt)                                  │
│  ├── Managed together as one unit                              │
│  ├── Parent controls all nested stacks                          │
│  ├── Better for application components                          │
│  └── Values resolved at deployment time                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deploying Nested Stacks

### Step 1: Upload Templates to S3

```bash
# Create S3 bucket for templates
aws s3 mb s3://my-cfn-templates-bucket

# Upload all templates
aws s3 cp network-stack.yaml s3://my-cfn-templates-bucket/nested-stacks/
aws s3 cp security-stack.yaml s3://my-cfn-templates-bucket/nested-stacks/
aws s3 cp database-stack.yaml s3://my-cfn-templates-bucket/nested-stacks/
aws s3 cp application-stack.yaml s3://my-cfn-templates-bucket/nested-stacks/
aws s3 cp root-stack.yaml s3://my-cfn-templates-bucket/
```

### Step 2: Deploy Root Stack

```bash
# Deploy the root stack
aws cloudformation create-stack \
  --stack-name three-tier-app \
  --template-url https://my-cfn-templates-bucket.s3.amazonaws.com/root-stack.yaml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=dev \
    ParameterKey=TemplatesBucket,ParameterValue=my-cfn-templates-bucket \
    ParameterKey=DBPassword,ParameterValue=MySecurePassword123! \
  --capabilities CAPABILITY_NAMED_IAM

# Monitor stack creation
aws cloudformation describe-stacks --stack-name three-tier-app

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name three-tier-app
```

### Step 3: View Nested Stack Status

```bash
# List all nested stacks
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE \
  --query "StackSummaries[?ParentId!=null]"

# Describe specific nested stack
aws cloudformation describe-stacks \
  --stack-name "three-tier-app-NetworkStack-XXXX"
```

---

## Updating Nested Stacks

### Update Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nested Stack Update Process                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Update nested template in S3                                │
│     aws s3 cp updated-template.yaml s3://bucket/                │
│                                                                  │
│  2. Update root stack (triggers nested stack updates)           │
│     aws cloudformation update-stack --stack-name root-stack     │
│                                                                  │
│  3. CloudFormation determines which nested stacks changed       │
│                                                                  │
│  4. Only changed nested stacks are updated                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Using Change Sets with Nested Stacks

```bash
# Create change set
aws cloudformation create-change-set \
  --stack-name three-tier-app \
  --change-set-name update-instance-type \
  --template-url https://my-cfn-templates-bucket.s3.amazonaws.com/root-stack.yaml \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=t3.small \
    ParameterKey=EnvironmentName,UsePreviousValue=true \
    ParameterKey=TemplatesBucket,UsePreviousValue=true \
    ParameterKey=DBPassword,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM \
  --include-nested-stacks

# Review change set (includes nested stack changes)
aws cloudformation describe-change-set \
  --stack-name three-tier-app \
  --change-set-name update-instance-type

# Execute change set
aws cloudformation execute-change-set \
  --stack-name three-tier-app \
  --change-set-name update-instance-type
```

---

## Best Practices

### 1. Template Organization

```
project/
├── templates/
│   ├── root-stack.yaml
│   └── nested/
│       ├── network/
│       │   └── vpc.yaml
│       ├── security/
│       │   ├── security-groups.yaml
│       │   └── iam-roles.yaml
│       ├── database/
│       │   └── rds.yaml
│       └── application/
│           ├── ec2.yaml
│           └── alb.yaml
├── parameters/
│   ├── dev.json
│   ├── staging.json
│   └── prod.json
└── scripts/
    ├── deploy.sh
    └── upload-templates.sh
```

### 2. Use Consistent Naming

```yaml
# Good - Consistent naming convention
NetworkStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/${EnvironmentName}/network.yaml'

SecurityStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/${EnvironmentName}/security.yaml'
```

### 3. Handle Dependencies Properly

```yaml
Resources:
  # Explicit dependency
  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn:
      - NetworkStack
      - SecurityStack
      - DatabaseStack
    Properties:
      TemplateURL: !Sub 'https://${TemplatesBucket}.s3.amazonaws.com/app.yaml'
```

### 4. Pass Only Required Parameters

```yaml
# Good - Pass only what's needed
ApplicationStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    Parameters:
      VPCId: !GetAtt NetworkStack.Outputs.VPCId
      SubnetId: !GetAtt NetworkStack.Outputs.PrivateSubnetId

# Avoid - Passing too many parameters
ApplicationStack:
  Type: AWS::CloudFormation::Stack
  Properties:
    Parameters:
      VPCId: !GetAtt NetworkStack.Outputs.VPCId
      VPCCidr: !GetAtt NetworkStack.Outputs.VPCCidr  # Might not be needed
      IGWId: !GetAtt NetworkStack.Outputs.IGWId      # Might not be needed
```

### 5. Version Your Templates

```yaml
# Include version in template description
Description: 'Network Stack v1.2.0 - VPC and Subnets'

# Or use metadata
Metadata:
  Version: '1.2.0'
  LastModified: '2024-01-15'
```

---

## Common Errors and Solutions

### Error 1: Template URL Access Denied

```
Error: Access Denied (Service: Amazon S3)
```

**Solution**: Ensure proper S3 bucket permissions

```yaml
# S3 bucket policy for CloudFormation access
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudformation.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-templates-bucket/*"
    }
  ]
}
```

### Error 2: Circular Dependency

```
Error: Circular dependency between resources
```

**Solution**: Break circular dependencies

```yaml
# Instead of direct circular reference
# Use exports and imports for loosely coupled stacks
Outputs:
  ResourceArn:
    Value: !GetAtt MyResource.Arn
    Export:
      Name: !Sub '${AWS::StackName}-ResourceArn'
```

### Error 3: Output Not Found

```
Error: Output 'VPCId' not found in stack 'NetworkStack'
```

**Solution**: Verify output exists in nested template

```yaml
# In nested template - Ensure output exists
Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
```

### Error 4: Nested Stack Update Failed

```
Error: Nested stack update failed
```

**Solution**: Check nested stack events

```bash
# Get nested stack events
aws cloudformation describe-stack-events \
  --stack-name "parent-stack-NestedStack-XXXXX"
```

---

## Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nested Stacks Summary                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Key Concepts:                                                   │
│  ├── Nested stacks are stacks within stacks                     │
│  ├── Created using AWS::CloudFormation::Stack                   │
│  ├── Templates must be stored in S3                             │
│  └── Managed together as a unit                                 │
│                                                                  │
│  Benefits:                                                       │
│  ├── Overcome template size limits                              │
│  ├── Enable template reuse                                      │
│  ├── Separate concerns                                          │
│  └── Simplify complex deployments                               │
│                                                                  │
│  Best Practices:                                                 │
│  ├── Organize templates logically                               │
│  ├── Use consistent naming                                      │
│  ├── Handle dependencies explicitly                             │
│  ├── Pass only required parameters                              │
│  └── Version your templates                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Practice**: Deploy the three-tier application example
2. **Explore**: Cross-stack references with exports
3. **Learn**: StackSets for multi-account deployment

---

**Next:** [Lesson 08 - StackSets](./08-stacksets.md)
