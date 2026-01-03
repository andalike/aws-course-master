# Lesson 03: CloudFormation Template Anatomy

## Introduction

A CloudFormation template is a JSON or YAML formatted text file that describes your AWS infrastructure. Understanding the structure and purpose of each section is essential for creating effective templates. This lesson provides an in-depth exploration of every template section.

---

## Template Structure Overview

```yaml
AWSTemplateFormatVersion: '2010-09-09'  # Required (recommended)

Description: >                            # Optional but recommended
  Template description here

Metadata:                                  # Optional
  # Additional information about template

Parameters:                                # Optional
  # Input values at runtime

Rules:                                     # Optional
  # Validate parameters

Mappings:                                  # Optional
  # Static lookup tables

Conditions:                                # Optional
  # Conditional logic

Transform:                                 # Optional
  # Macros to process template

Resources:                                 # REQUIRED
  # AWS resources to create

Outputs:                                   # Optional
  # Values to export
```

### Visual Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                  CloudFormation Template                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ AWSTemplateFormatVersion: '2010-09-09'                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Description: Multi-tier web application                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Metadata:        │ Parameters:      │ Mappings:          │  │
│  │ - AWS::CF::Init  │ - Environment    │ - RegionAMI        │  │
│  │ - Interface      │ - InstanceType   │ - InstanceSize     │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Conditions:                                                │  │
│  │ - IsProduction: !Equals [!Ref Environment, 'prod']        │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Resources:  (REQUIRED)                                     │  │
│  │ - VPC, Subnets, EC2, RDS, S3, Lambda, etc.                │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Outputs:                                                   │  │
│  │ - VPCId, LoadBalancerDNS, DatabaseEndpoint                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Section 1: AWSTemplateFormatVersion

The template format version identifies the capabilities of the template.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
```

### Key Points

- **Current Value**: `2010-09-09` (only valid value as of 2024)
- **Status**: Optional but strongly recommended
- **Purpose**: Ensures template is parsed correctly
- **Note**: Always include this for forward compatibility

```yaml
# Recommended practice
AWSTemplateFormatVersion: '2010-09-09'
Description: My template

# Also valid but not recommended
Description: My template without version
Resources:
  # ...
```

---

## Section 2: Description

A text string that describes the template's purpose.

```yaml
Description: >
  This template creates a highly available web application
  infrastructure with an Application Load Balancer, Auto Scaling
  Group, and RDS MySQL database in a Multi-AZ configuration.
```

### Key Points

- **Maximum Length**: 1024 bytes
- **Status**: Optional but highly recommended
- **Visibility**: Shown in AWS Console
- **Use**: Document purpose, author, version

### Best Practices

```yaml
# Good: Detailed and informative
Description: |
  Template: production-webapp-v2.3
  Author: DevOps Team
  Purpose: Deploy production web application with:
    - VPC with public/private subnets
    - Auto Scaling Group (2-10 instances)
    - Application Load Balancer
    - RDS MySQL Multi-AZ
  Last Updated: 2024-01-15

# Avoid: Vague descriptions
Description: My template  # Not helpful
```

---

## Section 3: Metadata

Additional information about the template.

### AWS::CloudFormation::Interface

Controls how parameters appear in the AWS Console:

```yaml
Metadata:
  AWS::CloudFormation::Interface:
    # Group parameters logically
    ParameterGroups:
      - Label:
          default: "Network Configuration"
        Parameters:
          - VPCCidr
          - PublicSubnetCidr
          - PrivateSubnetCidr

      - Label:
          default: "EC2 Configuration"
        Parameters:
          - InstanceType
          - KeyName
          - AMIId

      - Label:
          default: "Database Configuration"
        Parameters:
          - DBInstanceClass
          - DBName
          - DBUsername
          - DBPassword

    # Provide friendly labels for parameters
    ParameterLabels:
      VPCCidr:
        default: "VPC CIDR Block"
      InstanceType:
        default: "EC2 Instance Type"
      DBPassword:
        default: "Database Master Password"
```

### AWS::CloudFormation::Init

Configuration data for cfn-init (covered in detail in Lesson 09):

```yaml
Metadata:
  AWS::CloudFormation::Init:
    configSets:
      default:
        - install
        - configure
    install:
      packages:
        yum:
          httpd: []
          php: []
      files:
        /var/www/html/index.html:
          content: |
            <h1>Hello World</h1>
          mode: '000644'
          owner: apache
          group: apache
    configure:
      services:
        sysvinit:
          httpd:
            enabled: true
            ensureRunning: true
```

### Custom Metadata

You can add any custom metadata:

```yaml
Metadata:
  # Custom metadata for documentation
  TemplateVersion: '2.3.1'
  Author: 'DevOps Team'
  License: 'MIT'
  Repository: 'https://github.com/company/infrastructure'

  # Custom metadata for tools
  cfn-lint:
    config:
      ignore_checks:
        - W3011
```

---

## Section 4: Parameters

Input values that customize your template at runtime.

### Basic Parameter Structure

```yaml
Parameters:
  ParameterName:
    Type: String                    # Required
    Default: 'default-value'        # Optional
    Description: 'Parameter desc'   # Optional but recommended
    AllowedValues:                  # Optional
      - value1
      - value2
    AllowedPattern: '^[a-zA-Z].*'   # Optional (regex)
    ConstraintDescription: '...'    # Optional
    MaxLength: 50                   # Optional (for String)
    MinLength: 1                    # Optional (for String)
    MaxValue: 100                   # Optional (for Number)
    MinValue: 1                     # Optional (for Number)
    NoEcho: true                    # Optional (hide in console)
```

### Parameter Types

```yaml
Parameters:
  # String type
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

  # Number type
  InstanceCount:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 10

  # List of strings
  AvailabilityZones:
    Type: List<String>
    Default: 'us-east-1a,us-east-1b'

  # Comma-delimited list
  SubnetCidrs:
    Type: CommaDelimitedList
    Default: '10.0.1.0/24,10.0.2.0/24'

  # AWS-specific parameter types
  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: Select existing VPC

  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Select subnets

  SecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: Select security group

  KeyPair:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Select key pair

  AMI:
    Type: AWS::EC2::Image::Id
    Default: ami-12345678

  # SSM Parameter Store integration
  LatestAMI:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
```

### AWS-Specific Parameter Types

| Type | Description |
|------|-------------|
| `AWS::EC2::VPC::Id` | VPC ID |
| `AWS::EC2::Subnet::Id` | Subnet ID |
| `AWS::EC2::SecurityGroup::Id` | Security Group ID |
| `AWS::EC2::KeyPair::KeyName` | EC2 Key Pair name |
| `AWS::EC2::Image::Id` | AMI ID |
| `AWS::EC2::AvailabilityZone::Name` | AZ name |
| `AWS::SSM::Parameter::Value<Type>` | SSM Parameter Store value |

### Complete Parameter Example

```yaml
Parameters:
  # Environment selection with validation
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Deployment environment
    ConstraintDescription: Must be dev, staging, or prod

  # Instance type with conditional sizing
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large
      - m5.large
      - m5.xlarge
    Description: EC2 instance type

  # Database password with no echo
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    MaxLength: 41
    AllowedPattern: '^[a-zA-Z0-9]*$'
    ConstraintDescription: Must contain only alphanumeric characters
    Description: Database master password

  # CIDR validation with pattern
  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(1[6-9]|2[0-8]))$'
    ConstraintDescription: Must be a valid CIDR block (e.g., 10.0.0.0/16)
    Description: CIDR block for VPC
```

---

## Section 5: Rules

Validate parameter combinations before stack creation/update.

```yaml
Rules:
  # Validate production has larger instances
  ProductionInstanceTypeRule:
    RuleCondition: !Equals [!Ref Environment, 'prod']
    Assertions:
      - Assert: !Contains
          - - t3.large
            - m5.large
            - m5.xlarge
            - c5.large
          - !Ref InstanceType
        AssertDescription: Production environment requires t3.large or larger

  # Validate Multi-AZ for production database
  ProductionMultiAZRule:
    RuleCondition: !Equals [!Ref Environment, 'prod']
    Assertions:
      - Assert: !Equals [!Ref DBMultiAZ, 'true']
        AssertDescription: Production databases must be Multi-AZ

  # Validate subnet selections are in same VPC
  SubnetVPCRule:
    Assertions:
      - Assert: !Not [!Equals [!Ref VPCId, '']]
        AssertDescription: A VPC must be selected
```

---

## Section 6: Mappings

Static lookup tables for conditional values.

```yaml
Mappings:
  # Region to AMI mapping
  RegionAMI:
    us-east-1:
      HVM64: ami-0123456789abcdef0
      HVM32: ami-0123456789abcdef1
    us-west-2:
      HVM64: ami-0fedcba9876543210
      HVM32: ami-0fedcba9876543211
    eu-west-1:
      HVM64: ami-0abcdef1234567890
      HVM32: ami-0abcdef1234567891

  # Environment-based instance sizing
  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      MinSize: 1
      MaxSize: 2
      DBInstanceClass: db.t3.micro
    staging:
      InstanceType: t3.small
      MinSize: 2
      MaxSize: 4
      DBInstanceClass: db.t3.small
    prod:
      InstanceType: t3.large
      MinSize: 2
      MaxSize: 10
      DBInstanceClass: db.r5.large

  # CIDR block mappings
  SubnetCIDR:
    VPC:
      CIDR: 10.0.0.0/16
    PublicSubnet1:
      CIDR: 10.0.1.0/24
    PublicSubnet2:
      CIDR: 10.0.2.0/24
    PrivateSubnet1:
      CIDR: 10.0.10.0/24
    PrivateSubnet2:
      CIDR: 10.0.11.0/24
```

### Using Mappings

```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # Look up AMI based on region
      ImageId: !FindInMap
        - RegionAMI
        - !Ref 'AWS::Region'
        - HVM64

      # Look up instance type based on environment
      InstanceType: !FindInMap
        - EnvironmentConfig
        - !Ref Environment
        - InstanceType
```

---

## Section 7: Conditions

Define conditions for resource creation or property values.

```yaml
Conditions:
  # Simple equality check
  IsProduction: !Equals [!Ref Environment, 'prod']

  # Not condition
  IsNotProduction: !Not [!Equals [!Ref Environment, 'prod']]

  # And condition
  CreateProdResources: !And
    - !Equals [!Ref Environment, 'prod']
    - !Equals [!Ref CreateOptional, 'true']

  # Or condition
  CreateInProdOrStaging: !Or
    - !Equals [!Ref Environment, 'prod']
    - !Equals [!Ref Environment, 'staging']

  # Nested conditions
  LargeProductionDeployment: !And
    - !Condition IsProduction
    - !Equals [!Ref DeploymentSize, 'large']

  # Check if parameter has value
  HasKeyName: !Not [!Equals [!Ref KeyName, '']]
```

### Condition Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `Fn::Equals` | Compare two values | `!Equals [!Ref Env, 'prod']` |
| `Fn::If` | Conditional value | `!If [Cond, ValueIfTrue, ValueIfFalse]` |
| `Fn::Not` | Negate condition | `!Not [!Condition IsProduction]` |
| `Fn::And` | All conditions true | `!And [Cond1, Cond2]` |
| `Fn::Or` | Any condition true | `!Or [Cond1, Cond2]` |

### Using Conditions

```yaml
Resources:
  # Conditionally create resource
  ProductionDatabase:
    Type: AWS::RDS::DBInstance
    Condition: IsProduction  # Only created if IsProduction is true
    Properties:
      DBInstanceClass: db.r5.large
      MultiAZ: true

  # Conditional property values
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !If
        - IsProduction
        - t3.large
        - t3.micro

      # Conditional tags
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - !If
          - IsProduction
          - Key: CriticalityLevel
            Value: High
          - !Ref AWS::NoValue  # Don't add tag if not production

Outputs:
  # Conditional outputs
  ProductionDBEndpoint:
    Condition: IsProduction
    Description: Production database endpoint
    Value: !GetAtt ProductionDatabase.Endpoint.Address
```

---

## Section 8: Transform

Macros that process your template.

### AWS::Include Transform

Include template snippets from S3:

```yaml
Transform:
  - AWS::Include

Resources:
  Fn::Transform:
    Name: AWS::Include
    Parameters:
      Location: s3://my-bucket/snippets/common-resources.yaml
```

### AWS::Serverless Transform

Enable SAM (Serverless Application Model) syntax:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Serverless application

Resources:
  # SAM simplified syntax
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      CodeUri: ./src
      Events:
        Api:
          Type: Api
          Properties:
            Path: /hello
            Method: GET
```

### Multiple Transforms

```yaml
Transform:
  - AWS::Serverless-2016-10-31
  - AWS::CodeDeployBlueGreen
```

---

## Section 9: Resources (REQUIRED)

The only required section - defines AWS resources to create.

### Resource Structure

```yaml
Resources:
  LogicalResourceId:           # Unique identifier within template
    Type: AWS::Service::Resource   # Resource type
    Properties:                    # Resource configuration
      PropertyName: PropertyValue

    # Optional attributes
    Condition: ConditionName       # Conditional creation
    DependsOn:                     # Explicit dependencies
      - OtherResource
    DeletionPolicy: Retain         # Behavior on deletion
    UpdatePolicy:                  # Behavior on update
      AutoScalingRollingUpdate:
        MinInstancesInService: 1
    UpdateReplacePolicy: Retain    # Behavior on replacement
    CreationPolicy:                # Wait for signals
      ResourceSignal:
        Count: 1
        Timeout: PT15M
    Metadata:                      # Resource-specific metadata
      Key: Value
```

### Common Resource Types

```yaml
Resources:
  # VPC Resources
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true

  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: 10.0.1.0/24

  # EC2 Resources
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: !Ref AMI
      SubnetId: !Ref MySubnet
      SecurityGroupIds:
        - !Ref MySecurityGroup

  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Web server security group
      VpcId: !Ref MyVPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  # S3 Resources
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'my-bucket-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled

  # IAM Resources
  MyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

  # RDS Resources
  MyDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20

  # Lambda Resources
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: python3.9
      Handler: index.handler
      Role: !GetAtt MyRole.Arn
      Code:
        ZipFile: |
          def handler(event, context):
              return {'statusCode': 200, 'body': 'Hello'}
```

### Resource Reference

Find all resource types in the [AWS Resource and Property Types Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html).

---

## Section 10: Outputs

Values to export from the stack.

### Output Structure

```yaml
Outputs:
  OutputLogicalId:
    Description: Description of output    # Optional but recommended
    Value: !Ref SomeResource              # Required
    Condition: SomeCondition              # Optional
    Export:                               # Optional (for cross-stack)
      Name: ExportedName
```

### Complete Outputs Example

```yaml
Outputs:
  # Simple reference output
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  # GetAtt output
  DatabaseEndpoint:
    Description: RDS endpoint address
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub '${AWS::StackName}-DBEndpoint'

  # Constructed URL output
  WebsiteURL:
    Description: URL of the load balancer
    Value: !Sub 'http://${LoadBalancer.DNSName}'

  # Conditional output
  ProductionDBEndpoint:
    Condition: IsProduction
    Description: Production database endpoint
    Value: !GetAtt ProductionDB.Endpoint.Address

  # Multiple values using Join
  SubnetIds:
    Description: List of subnet IDs
    Value: !Join
      - ','
      - - !Ref PublicSubnet1
        - !Ref PublicSubnet2
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
    Export:
      Name: !Sub '${AWS::StackName}-SubnetIds'

  # Security group for other stacks
  WebServerSecurityGroup:
    Description: Security group for web servers
    Value: !Ref WebServerSG
    Export:
      Name: !Sub '${AWS::StackName}-WebServerSG'
```

### Cross-Stack References

**Stack A (Exports):**
```yaml
Outputs:
  VPCId:
    Value: !Ref VPC
    Export:
      Name: shared-vpc-id  # This name is used by other stacks
```

**Stack B (Imports):**
```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # Import value from Stack A
      SubnetId: !ImportValue shared-subnet-id
```

---

## Pseudo Parameters

Built-in parameters available in every template:

```yaml
Resources:
  MyResource:
    Type: AWS::S3::Bucket
    Properties:
      # AWS::AccountId - Current account ID
      BucketName: !Sub 'bucket-${AWS::AccountId}'

      Tags:
        # AWS::Region - Current region
        - Key: Region
          Value: !Ref 'AWS::Region'

        # AWS::StackName - Name of the stack
        - Key: Stack
          Value: !Ref 'AWS::StackName'

        # AWS::StackId - Stack ID
        - Key: StackId
          Value: !Ref 'AWS::StackId'

Outputs:
  # AWS::URLSuffix - Domain suffix (amazonaws.com)
  S3URL:
    Value: !Sub 'https://${MyBucket}.s3.${AWS::URLSuffix}'

  # AWS::NotificationARNs - List of SNS topic ARNs
  NotificationTopics:
    Value: !Join [',', !Ref 'AWS::NotificationARNs']

  # AWS::NoValue - Remove property (use in conditions)
  ConditionalOutput:
    Value: !If [SomeCondition, 'value', !Ref 'AWS::NoValue']
```

### Pseudo Parameters Reference

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `AWS::AccountId` | AWS account ID | `123456789012` |
| `AWS::Region` | Current region | `us-east-1` |
| `AWS::StackName` | Stack name | `my-stack` |
| `AWS::StackId` | Stack ARN | `arn:aws:cloudformation:...` |
| `AWS::URLSuffix` | Domain suffix | `amazonaws.com` |
| `AWS::Partition` | AWS partition | `aws`, `aws-cn`, `aws-us-gov` |
| `AWS::NotificationARNs` | SNS topic ARNs | List of ARNs |
| `AWS::NoValue` | Remove property | N/A |

---

## Complete Template Example

Here's a complete template demonstrating all sections:

```yaml
AWSTemplateFormatVersion: '2010-09-09'

Description: |
  Complete CloudFormation Template Example
  Demonstrates all template sections
  Version: 1.0.0

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: Environment Configuration
        Parameters:
          - Environment
          - ProjectName
      - Label:
          default: Network Configuration
        Parameters:
          - VPCCidr
      - Label:
          default: Instance Configuration
        Parameters:
          - InstanceType
          - KeyName
    ParameterLabels:
      Environment:
        default: Deployment Environment
      VPCCidr:
        default: VPC CIDR Block

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Deployment environment

  ProjectName:
    Type: String
    Default: myproject
    Description: Project name for resource naming

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(1[6-9]|2[0-8]))$'
    Description: CIDR block for VPC

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
    Description: EC2 instance type

  KeyName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 key pair name

Rules:
  ProductionInstanceSize:
    RuleCondition: !Equals [!Ref Environment, 'prod']
    Assertions:
      - Assert: !Not [!Equals [!Ref InstanceType, 't3.micro']]
        AssertDescription: Production requires t3.small or larger

Mappings:
  RegionAMI:
    us-east-1:
      AMI: ami-0123456789abcdef0
    us-west-2:
      AMI: ami-0fedcba9876543210

  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
    staging:
      InstanceType: t3.small
    prod:
      InstanceType: t3.medium

Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']
  CreateDevResources: !Equals [!Ref Environment, 'dev']

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-vpc'
        - Key: Environment
          Value: !Ref Environment

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Cidr [!Ref VPCCidr, 4, 8]]
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-public-subnet'

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !If
        - IsProduction
        - !FindInMap [EnvironmentConfig, prod, InstanceType]
        - !Ref InstanceType
      ImageId: !FindInMap
        - RegionAMI
        - !Ref 'AWS::Region'
        - AMI
      KeyName: !Ref KeyName
      SubnetId: !Ref PublicSubnet
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-webserver'

  # Only created in dev environment
  DevBucket:
    Type: AWS::S3::Bucket
    Condition: CreateDevResources
    Properties:
      BucketName: !Sub '${ProjectName}-dev-${AWS::AccountId}'

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  WebServerPublicIP:
    Description: Web server public IP
    Value: !GetAtt WebServer.PublicIp

  DevBucketName:
    Condition: CreateDevResources
    Description: Development bucket name
    Value: !Ref DevBucket
```

---

## Summary

### Section Summary Table

| Section | Required | Purpose |
|---------|----------|---------|
| AWSTemplateFormatVersion | No* | Template version |
| Description | No | Template documentation |
| Metadata | No | Additional template info |
| Parameters | No | Runtime input values |
| Rules | No | Parameter validation |
| Mappings | No | Static lookup tables |
| Conditions | No | Conditional logic |
| Transform | No | Macro processing |
| **Resources** | **Yes** | AWS resources to create |
| Outputs | No | Export values |

*Recommended to include

### Best Practices

1. Always include `AWSTemplateFormatVersion` and `Description`
2. Use `Metadata::AWS::CloudFormation::Interface` for better console UX
3. Parameterize everything that might change
4. Use Mappings for static, region-specific values
5. Use Conditions to avoid duplicate templates
6. Export Outputs for cross-stack references
7. Add meaningful descriptions to all Parameters and Outputs

---

## Knowledge Check

1. Which template section is required?
2. What is the purpose of the Metadata section?
3. How do you make a parameter value hidden in the console?
4. What is the difference between Parameters and Mappings?
5. How do you conditionally create a resource?

---

**Next:** [04 - Intrinsic Functions](./04-intrinsic-functions.md)

**Previous:** [02 - CloudFormation Basics](./02-cloudformation-basics.md)
