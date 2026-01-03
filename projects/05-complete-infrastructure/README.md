# Project 5: Complete Infrastructure with CloudFormation

## Project Overview

Deploy a complete, production-ready infrastructure using CloudFormation that combines all the skills learned throughout this course. This capstone project ties together VPC, EC2, RDS, S3, Lambda, and monitoring.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE INFRASTRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                              VPC (10.0.0.0/16)                                 │  │
│  │                                                                                │  │
│  │    Internet          ┌─────────────────────────────────────────────────┐      │  │
│  │        │             │              Application Load Balancer           │      │  │
│  │        ▼             └───────────────────────┬─────────────────────────┘      │  │
│  │  ┌──────────┐                                │                                 │  │
│  │  │   IGW    │                                │                                 │  │
│  │  └────┬─────┘                                │                                 │  │
│  │       │              ┌───────────────────────┼───────────────────────┐        │  │
│  │       │              │                       │                       │        │  │
│  │       ▼              ▼                       ▼                       ▼        │  │
│  │  ┌─────────────┐ ┌─────────────┐      ┌─────────────┐ ┌─────────────┐        │  │
│  │  │   Public    │ │   Public    │      │   Private   │ │   Private   │        │  │
│  │  │  Subnet A   │ │  Subnet B   │      │  Subnet A   │ │  Subnet B   │        │  │
│  │  │ 10.0.1.0/24 │ │ 10.0.2.0/24 │      │ 10.0.3.0/24 │ │ 10.0.4.0/24 │        │  │
│  │  │             │ │             │      │             │ │             │        │  │
│  │  │ ┌─────────┐ │ │ ┌─────────┐ │      │ ┌─────────┐ │ │ ┌─────────┐ │        │  │
│  │  │ │   NAT   │ │ │ │   NAT   │ │      │ │   EC2   │ │ │ │   EC2   │ │        │  │
│  │  │ │ Gateway │ │ │ │ Gateway │ │      │ │  (ASG)  │ │ │ │  (ASG)  │ │        │  │
│  │  │ └─────────┘ │ │ └─────────┘ │      │ └─────────┘ │ │ └─────────┘ │        │  │
│  │  └─────────────┘ └─────────────┘      └──────┬──────┘ └──────┬──────┘        │  │
│  │                                              │               │                │  │
│  │                                              └───────┬───────┘                │  │
│  │                                                      │                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Database Subnets (Private)                           │ │  │
│  │  │  ┌─────────────────┐               ┌─────────────────┐                  │ │  │
│  │  │  │ 10.0.5.0/24     │               │ 10.0.6.0/24     │                  │ │  │
│  │  │  │                 │               │                 │                  │ │  │
│  │  │  │  ┌───────────┐  │◄──Multi-AZ───►│  ┌───────────┐  │                  │ │  │
│  │  │  │  │    RDS    │  │   Replication │  │    RDS    │  │                  │ │  │
│  │  │  │  │ (Primary) │  │               │  │ (Standby) │  │                  │ │  │
│  │  │  │  └───────────┘  │               │  └───────────┘  │                  │ │  │
│  │  │  └─────────────────┘               └─────────────────┘                  │ │  │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │                           ADDITIONAL SERVICES                                    ││
│  │                                                                                  ││
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    ││
│  │  │      S3       │  │   Lambda      │  │  CloudWatch   │  │     SNS       │    ││
│  │  │   (Static     │  │  (Scheduled   │  │   (Logs,      │  │  (Alerts)     │    ││
│  │  │   Assets)     │  │   Jobs)       │  │   Alarms)     │  │               │    ││
│  │  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘    ││
│  │                                                                                  ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## CloudFormation Templates

This project uses nested stacks for modularity:

```
infrastructure/
├── main.yaml           # Parent stack
├── vpc.yaml            # VPC, subnets, NAT
├── security.yaml       # Security groups, IAM
├── database.yaml       # RDS, secrets
├── compute.yaml        # EC2, ASG, ALB
├── storage.yaml        # S3 buckets
├── serverless.yaml     # Lambda functions
└── monitoring.yaml     # CloudWatch, SNS
```

---

## Main Stack (main.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Complete Infrastructure - Parent Stack

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

  ProjectName:
    Type: String
    Default: complete-infra

  DBUsername:
    Type: String
    Default: admin

  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8

  NotificationEmail:
    Type: String

  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair

Resources:
  # VPC Stack
  VPCStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub https://${ArtifactsBucket}.s3.amazonaws.com/vpc.yaml
      Parameters:
        Environment: !Ref Environment
        ProjectName: !Ref ProjectName
        VPCCidr: 10.0.0.0/16

  # Security Stack
  SecurityStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: VPCStack
    Properties:
      TemplateURL: !Sub https://${ArtifactsBucket}.s3.amazonaws.com/security.yaml
      Parameters:
        Environment: !Ref Environment
        VPCId: !GetAtt VPCStack.Outputs.VPCId

  # Database Stack
  DatabaseStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: SecurityStack
    Properties:
      TemplateURL: !Sub https://${ArtifactsBucket}.s3.amazonaws.com/database.yaml
      Parameters:
        Environment: !Ref Environment
        ProjectName: !Ref ProjectName
        DBSubnet1: !GetAtt VPCStack.Outputs.DBSubnet1
        DBSubnet2: !GetAtt VPCStack.Outputs.DBSubnet2
        DBSecurityGroup: !GetAtt SecurityStack.Outputs.DBSecurityGroup
        DBUsername: !Ref DBUsername
        DBPassword: !Ref DBPassword

  # Compute Stack
  ComputeStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: DatabaseStack
    Properties:
      TemplateURL: !Sub https://${ArtifactsBucket}.s3.amazonaws.com/compute.yaml
      Parameters:
        Environment: !Ref Environment
        VPCId: !GetAtt VPCStack.Outputs.VPCId
        PublicSubnet1: !GetAtt VPCStack.Outputs.PublicSubnet1
        PublicSubnet2: !GetAtt VPCStack.Outputs.PublicSubnet2
        PrivateSubnet1: !GetAtt VPCStack.Outputs.PrivateSubnet1
        PrivateSubnet2: !GetAtt VPCStack.Outputs.PrivateSubnet2
        ALBSecurityGroup: !GetAtt SecurityStack.Outputs.ALBSecurityGroup
        EC2SecurityGroup: !GetAtt SecurityStack.Outputs.EC2SecurityGroup
        EC2InstanceProfile: !GetAtt SecurityStack.Outputs.EC2InstanceProfile
        DBEndpoint: !GetAtt DatabaseStack.Outputs.DBEndpoint
        KeyPairName: !Ref KeyPairName

  # Monitoring Stack
  MonitoringStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: ComputeStack
    Properties:
      TemplateURL: !Sub https://${ArtifactsBucket}.s3.amazonaws.com/monitoring.yaml
      Parameters:
        Environment: !Ref Environment
        AutoScalingGroupName: !GetAtt ComputeStack.Outputs.AutoScalingGroupName
        ALBFullName: !GetAtt ComputeStack.Outputs.ALBFullName
        TargetGroupFullName: !GetAtt ComputeStack.Outputs.TargetGroupFullName
        DBInstanceId: !GetAtt DatabaseStack.Outputs.DBInstanceId
        NotificationEmail: !Ref NotificationEmail

  # Artifacts Bucket
  ArtifactsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub ${ProjectName}-artifacts-${AWS::AccountId}

Outputs:
  VPCId:
    Value: !GetAtt VPCStack.Outputs.VPCId
    Export:
      Name: !Sub ${ProjectName}-VPCId

  ALBDNSName:
    Value: !GetAtt ComputeStack.Outputs.ALBDNSName
    Export:
      Name: !Sub ${ProjectName}-ALBDNSName

  DBEndpoint:
    Value: !GetAtt DatabaseStack.Outputs.DBEndpoint
    Export:
      Name: !Sub ${ProjectName}-DBEndpoint
```

---

## VPC Stack (vpc.yaml)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: VPC Infrastructure

Parameters:
  Environment:
    Type: String
  ProjectName:
    Type: String
  VPCCidr:
    Type: String
    Default: 10.0.0.0/16

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-vpc-${Environment}

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-igw-${Environment}

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      InternetGatewayId: !Ref InternetGateway
      VpcId: !Ref VPC

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-1-${Environment}

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-2-${Environment}

  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.3.0/24
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-1-${Environment}

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.4.0/24
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-2-${Environment}

  # Database Subnets
  DBSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.5.0/24
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-db-1-${Environment}

  DBSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.6.0/24
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-db-2-${Environment}

  # NAT Gateways
  NatGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc

  NatGateway2EIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-nat-1-${Environment}

  NatGateway2:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway2EIP.AllocationId
      SubnetId: !Ref PublicSubnet2
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-nat-2-${Environment}

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-public-rt-${Environment}

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet1

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet2

  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-rt-1-${Environment}

  PrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet1

  DBSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref DBSubnet1

  PrivateRouteTable2:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-private-rt-2-${Environment}

  PrivateRoute2:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable2
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway2

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable2
      SubnetId: !Ref PrivateSubnet2

  DBSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable2
      SubnetId: !Ref DBSubnet2

Outputs:
  VPCId:
    Value: !Ref VPC
  PublicSubnet1:
    Value: !Ref PublicSubnet1
  PublicSubnet2:
    Value: !Ref PublicSubnet2
  PrivateSubnet1:
    Value: !Ref PrivateSubnet1
  PrivateSubnet2:
    Value: !Ref PrivateSubnet2
  DBSubnet1:
    Value: !Ref DBSubnet1
  DBSubnet2:
    Value: !Ref DBSubnet2
```

---

## Deployment Commands

```bash
# Validate templates
aws cloudformation validate-template --template-body file://main.yaml

# Create S3 bucket for templates
aws s3 mb s3://your-cfn-templates-bucket

# Upload nested templates
aws s3 sync ./infrastructure s3://your-cfn-templates-bucket/

# Deploy the stack
aws cloudformation create-stack \
    --stack-name complete-infrastructure \
    --template-body file://main.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=dev \
        ParameterKey=DBUsername,ParameterValue=admin \
        ParameterKey=DBPassword,ParameterValue=YourSecurePassword123! \
        ParameterKey=NotificationEmail,ParameterValue=your@email.com \
        ParameterKey=KeyPairName,ParameterValue=your-key-pair \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

# Monitor progress
aws cloudformation describe-stack-events \
    --stack-name complete-infrastructure \
    --query 'StackEvents[*].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId]' \
    --output table
```

---

## Verification Checklist

- [ ] VPC with 6 subnets across 2 AZs
- [ ] Internet Gateway attached
- [ ] NAT Gateways in public subnets
- [ ] Route tables configured correctly
- [ ] Security groups with proper rules
- [ ] RDS Multi-AZ deployed
- [ ] Auto Scaling Group with 2+ instances
- [ ] ALB distributing traffic
- [ ] CloudWatch alarms configured
- [ ] SNS notifications working

---

## Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| NAT Gateways (2) | ~$65 |
| RDS db.t3.micro Multi-AZ | ~$25 |
| EC2 t2.micro (2) | Free Tier / ~$17 |
| ALB | ~$22 |
| CloudWatch | ~$3 |
| **Total** | **~$130/month** |

---

## Cleanup

```bash
# Delete the stack (will delete all nested stacks)
aws cloudformation delete-stack --stack-name complete-infrastructure

# Monitor deletion
aws cloudformation describe-stacks \
    --stack-name complete-infrastructure
```

---

**Congratulations!** You've completed the AWS Course Capstone Project!

[← Back to Projects](../) | [Back to Course Home](../../)
