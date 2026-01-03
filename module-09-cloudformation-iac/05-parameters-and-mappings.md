# Lesson 05: Parameters and Mappings

## Introduction

Parameters and Mappings are essential for creating reusable, flexible CloudFormation templates. Parameters allow runtime customization, while Mappings provide static lookup tables for region-specific or environment-specific values. This lesson covers both in depth.

---

## Parameters Overview

Parameters enable you to input custom values when creating or updating a stack, making templates reusable across different environments and use cases.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Parameter Flow                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Template                   Stack Creation                       │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ Parameters:     │       │ Parameter Values:│                  │
│  │  - Environment  │  ───► │  - prod          │                  │
│  │  - InstanceType │       │  - t3.large      │                  │
│  │  - VPCCidr      │       │  - 10.0.0.0/16   │                  │
│  └─────────────────┘       └─────────────────┘                  │
│                                   │                              │
│                                   ▼                              │
│                           ┌─────────────────┐                   │
│                           │ Resources use    │                   │
│                           │ !Ref Parameter   │                   │
│                           └─────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Parameter Types

### String Type

The most common parameter type for text values.

```yaml
Parameters:
  # Basic string
  Environment:
    Type: String
    Default: dev
    Description: Deployment environment

  # String with allowed values
  EnvironmentRestricted:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Deployment environment (restricted)

  # String with pattern validation
  ProjectName:
    Type: String
    MinLength: 3
    MaxLength: 20
    AllowedPattern: '^[a-zA-Z][a-zA-Z0-9-]*$'
    ConstraintDescription: Must start with letter, contain only alphanumeric and hyphens
    Description: Project name for resource naming

  # String for sensitive data
  DatabasePassword:
    Type: String
    NoEcho: true
    MinLength: 8
    MaxLength: 41
    AllowedPattern: '^[a-zA-Z0-9!@#$%^&*()_+=-]*$'
    ConstraintDescription: Must be 8-41 characters, alphanumeric and special chars
    Description: Master password for database
```

### Number Type

For numeric values with optional constraints.

```yaml
Parameters:
  # Basic number
  InstanceCount:
    Type: Number
    Default: 2
    Description: Number of instances to launch

  # Number with constraints
  DesiredCapacity:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 100
    Description: Desired number of instances in ASG

  # Port number
  WebServerPort:
    Type: Number
    Default: 80
    AllowedValues:
      - 80
      - 443
      - 8080
      - 8443
    Description: Port for web server

  # Storage size
  AllocatedStorage:
    Type: Number
    Default: 20
    MinValue: 20
    MaxValue: 1000
    Description: RDS allocated storage in GB
```

### List Types

For multiple values.

```yaml
Parameters:
  # List of strings
  AvailabilityZones:
    Type: List<String>
    Default: 'us-east-1a,us-east-1b'
    Description: List of Availability Zones

  # Comma-delimited list
  SubnetCidrs:
    Type: CommaDelimitedList
    Default: '10.0.1.0/24,10.0.2.0/24,10.0.3.0/24'
    Description: CIDR blocks for subnets
```

Using list parameters:

```yaml
Resources:
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # Select first item from list
      CidrBlock: !Select [0, !Ref SubnetCidrs]
      AvailabilityZone: !Select [0, !Ref AvailabilityZones]

  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [1, !Ref SubnetCidrs]
      AvailabilityZone: !Select [1, !Ref AvailabilityZones]
```

---

## AWS-Specific Parameter Types

AWS provides special parameter types that integrate with AWS resources.

### EC2 Parameter Types

```yaml
Parameters:
  # VPC ID (shows VPC dropdown in console)
  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: Select a VPC

  # Subnet ID
  SubnetId:
    Type: AWS::EC2::Subnet::Id
    Description: Select a subnet

  # List of Subnet IDs
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Select multiple subnets

  # Security Group ID
  SecurityGroupId:
    Type: AWS::EC2::SecurityGroup::Id
    Description: Select a security group

  # List of Security Groups
  SecurityGroupIds:
    Type: List<AWS::EC2::SecurityGroup::Id>
    Description: Select security groups

  # Key Pair Name
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Select an EC2 key pair

  # AMI ID
  ImageId:
    Type: AWS::EC2::Image::Id
    Description: Enter AMI ID
    Default: ami-12345678

  # Availability Zone
  AvailabilityZone:
    Type: AWS::EC2::AvailabilityZone::Name
    Description: Select an Availability Zone
```

### SSM Parameter Store Types

Retrieve values from SSM Parameter Store at stack creation time.

```yaml
Parameters:
  # Get latest Amazon Linux 2 AMI
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
    Description: Latest Amazon Linux 2 AMI

  # Get specific SSM parameter
  DatabaseHost:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /myapp/production/database/host
    Description: Database hostname from Parameter Store

  # List from SSM
  SubnetIdsFromSSM:
    Type: AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>
    Default: /myapp/production/subnet-ids
    Description: Subnet IDs from Parameter Store

  # SecureString (decrypted at deployment)
  SecretValue:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /myapp/production/api-key
    NoEcho: true
    Description: API key from Parameter Store
```

### AWS-Specific Types Reference

| Type | Description | Console Display |
|------|-------------|-----------------|
| `AWS::EC2::VPC::Id` | VPC ID | VPC dropdown |
| `AWS::EC2::Subnet::Id` | Subnet ID | Subnet dropdown |
| `AWS::EC2::SecurityGroup::Id` | Security Group ID | SG dropdown |
| `AWS::EC2::KeyPair::KeyName` | Key pair name | Key pair dropdown |
| `AWS::EC2::Image::Id` | AMI ID | Text input |
| `AWS::EC2::AvailabilityZone::Name` | AZ name | AZ dropdown |
| `AWS::EC2::Instance::Id` | Instance ID | Text input |
| `AWS::EC2::Volume::Id` | EBS Volume ID | Text input |
| `AWS::Route53::HostedZone::Id` | Hosted Zone ID | Text input |
| `AWS::SSM::Parameter::Value<Type>` | SSM Parameter | Text input |

---

## Parameter Properties

### Complete Parameter Reference

```yaml
Parameters:
  MyParameter:
    # Required
    Type: String                          # Parameter type

    # Optional properties
    Default: 'default-value'              # Default value
    Description: 'Parameter description'  # Shown in console

    # String constraints
    AllowedPattern: '^[a-z]+$'           # Regex pattern
    MinLength: 1                          # Minimum length
    MaxLength: 100                        # Maximum length

    # Number constraints
    MinValue: 0                           # Minimum value
    MaxValue: 100                         # Maximum value

    # Value restrictions
    AllowedValues:                        # Allowed values list
      - value1
      - value2

    # Error message
    ConstraintDescription: 'Error message for invalid input'

    # Security
    NoEcho: true                          # Hide in console/logs
```

### NoEcho for Sensitive Data

```yaml
Parameters:
  # Password - hidden in console and events
  MasterPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    MaxLength: 41
    AllowedPattern: '^[a-zA-Z0-9]*$'
    ConstraintDescription: Must be alphanumeric
    Description: Database master password (will not be displayed)

  # API Key
  APIKey:
    Type: String
    NoEcho: true
    Description: External API key

  # Secret token
  SecretToken:
    Type: String
    NoEcho: true
    AllowedPattern: '^[A-Za-z0-9+/=]+$'
    Description: Secret authentication token
```

---

## Parameter Best Practices

### 1. Use Descriptive Names and Descriptions

```yaml
Parameters:
  # Good: Clear, descriptive
  WebServerInstanceType:
    Type: String
    Default: t3.micro
    Description: EC2 instance type for web servers (e.g., t3.micro, t3.small)

  # Bad: Vague
  Type:
    Type: String
    Description: type
```

### 2. Provide Sensible Defaults

```yaml
Parameters:
  Environment:
    Type: String
    Default: dev  # Safe default for development
    AllowedValues:
      - dev
      - staging
      - prod

  InstanceType:
    Type: String
    Default: t3.micro  # Cost-effective default
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large
```

### 3. Use AllowedValues for Known Options

```yaml
Parameters:
  DatabaseEngine:
    Type: String
    Default: mysql
    AllowedValues:
      - mysql
      - postgres
      - mariadb
      - oracle-se2
    Description: RDS database engine

  SSLCertificateType:
    Type: String
    Default: 'none'
    AllowedValues:
      - none
      - acm
      - iam
    Description: Type of SSL certificate
```

### 4. Use Patterns for Complex Validation

```yaml
Parameters:
  # Email validation
  NotificationEmail:
    Type: String
    AllowedPattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    ConstraintDescription: Must be a valid email address
    Description: Email for notifications

  # CIDR validation
  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(1[6-9]|2[0-8]))$'
    ConstraintDescription: Must be a valid CIDR block (e.g., 10.0.0.0/16)

  # Domain name validation
  DomainName:
    Type: String
    AllowedPattern: '^([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    ConstraintDescription: Must be a valid domain name
    Description: Domain name for the application
```

### 5. Organize with Metadata Interface

```yaml
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Network Configuration"
        Parameters:
          - VPCCidr
          - PublicSubnet1Cidr
          - PublicSubnet2Cidr
          - PrivateSubnet1Cidr
          - PrivateSubnet2Cidr

      - Label:
          default: "Compute Configuration"
        Parameters:
          - InstanceType
          - KeyPairName
          - DesiredCapacity

      - Label:
          default: "Database Configuration"
        Parameters:
          - DBInstanceClass
          - DBName
          - DBUsername
          - DBPassword

      - Label:
          default: "Security"
        Parameters:
          - AllowedSSHCidr
          - EnableSSL

    ParameterLabels:
      VPCCidr:
        default: "VPC CIDR Block"
      InstanceType:
        default: "Web Server Instance Type"
      DBPassword:
        default: "Database Master Password"
```

---

## Mappings Overview

Mappings are fixed lookup tables defined in your template. They're useful for values that vary by region, environment, or other keys.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Mapping Structure                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Mappings:                                                       │
│    MapName:              # First level - Map name                │
│      TopLevelKey:        # Second level - Primary key            │
│        SecondLevelKey:   # Third level - Attribute               │
│          Value                                                   │
│                                                                  │
│  Example:                                                        │
│    RegionAMI:                                                    │
│      us-east-1:                                                  │
│        HVM64: ami-12345678                                       │
│        HVM32: ami-87654321                                       │
│      us-west-2:                                                  │
│        HVM64: ami-abcdefgh                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Mapping Use Cases

### 1. Region-Based AMI Mapping

```yaml
Mappings:
  RegionAMI:
    us-east-1:
      HVM64: ami-0123456789abcdef0
      HVM32: ami-0123456789abcdef1
    us-east-2:
      HVM64: ami-0234567890abcdef0
      HVM32: ami-0234567890abcdef1
    us-west-1:
      HVM64: ami-0345678901abcdef0
      HVM32: ami-0345678901abcdef1
    us-west-2:
      HVM64: ami-0456789012abcdef0
      HVM32: ami-0456789012abcdef1
    eu-west-1:
      HVM64: ami-0567890123abcdef0
      HVM32: ami-0567890123abcdef1
    eu-central-1:
      HVM64: ami-0678901234abcdef0
      HVM32: ami-0678901234abcdef1
    ap-northeast-1:
      HVM64: ami-0789012345abcdef0
      HVM32: ami-0789012345abcdef1
    ap-southeast-1:
      HVM64: ami-0890123456abcdef0
      HVM32: ami-0890123456abcdef1

Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap
        - RegionAMI
        - !Ref 'AWS::Region'
        - HVM64
      InstanceType: t3.micro
```

### 2. Environment-Based Configuration

```yaml
Mappings:
  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      MinSize: '1'
      MaxSize: '2'
      DesiredCapacity: '1'
      DBInstanceClass: db.t3.micro
      DBAllocatedStorage: '20'
      MultiAZ: 'false'

    staging:
      InstanceType: t3.small
      MinSize: '2'
      MaxSize: '4'
      DesiredCapacity: '2'
      DBInstanceClass: db.t3.small
      DBAllocatedStorage: '50'
      MultiAZ: 'false'

    prod:
      InstanceType: t3.large
      MinSize: '2'
      MaxSize: '10'
      DesiredCapacity: '4'
      DBInstanceClass: db.r5.large
      DBAllocatedStorage: '100'
      MultiAZ: 'true'

Resources:
  WebServerASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: !FindInMap [EnvironmentConfig, !Ref Environment, MinSize]
      MaxSize: !FindInMap [EnvironmentConfig, !Ref Environment, MaxSize]
      DesiredCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, DesiredCapacity]

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: !FindInMap [EnvironmentConfig, !Ref Environment, DBInstanceClass]
      AllocatedStorage: !FindInMap [EnvironmentConfig, !Ref Environment, DBAllocatedStorage]
      MultiAZ: !FindInMap [EnvironmentConfig, !Ref Environment, MultiAZ]
```

### 3. Region-Specific S3 Endpoints

```yaml
Mappings:
  RegionS3Website:
    us-east-1:
      Suffix: s3-website-us-east-1.amazonaws.com
    us-west-2:
      Suffix: s3-website-us-west-2.amazonaws.com
    eu-west-1:
      Suffix: s3-website-eu-west-1.amazonaws.com

Outputs:
  WebsiteURL:
    Value: !Sub
      - 'http://${BucketName}.${S3Suffix}'
      - BucketName: !Ref WebsiteBucket
        S3Suffix: !FindInMap [RegionS3Website, !Ref 'AWS::Region', Suffix]
```

### 4. Instance Type to Architecture Mapping

```yaml
Mappings:
  InstanceTypeArch:
    t3.micro:
      Arch: HVM64
    t3.small:
      Arch: HVM64
    t3.medium:
      Arch: HVM64
    m5.large:
      Arch: HVM64
    a1.medium:
      Arch: ARM64
    a1.large:
      Arch: ARM64
    t4g.micro:
      Arch: ARM64
    t4g.small:
      Arch: ARM64

  RegionArchAMI:
    us-east-1:
      HVM64: ami-0123456789abcdef0
      ARM64: ami-0fedcba9876543210
    us-west-2:
      HVM64: ami-0234567890abcdef0
      ARM64: ami-0edcba98765432100

Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      # Two-step mapping: InstanceType -> Arch -> AMI
      ImageId: !FindInMap
        - RegionArchAMI
        - !Ref 'AWS::Region'
        - !FindInMap
          - InstanceTypeArch
          - !Ref InstanceType
          - Arch
```

### 5. CIDR Block Mapping

```yaml
Mappings:
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
    DatabaseSubnet1:
      CIDR: 10.0.20.0/24
    DatabaseSubnet2:
      CIDR: 10.0.21.0/24

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !FindInMap [SubnetCIDR, VPC, CIDR]

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !FindInMap [SubnetCIDR, PublicSubnet1, CIDR]
```

---

## Combining Parameters and Mappings

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Combined Parameters and Mappings Example

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large

Mappings:
  # Map instance types to architectures
  InstanceTypeArch:
    t3.micro:
      Arch: HVM64
    t3.small:
      Arch: HVM64
    t3.medium:
      Arch: HVM64
    t3.large:
      Arch: HVM64

  # Map region + architecture to AMI
  RegionAMI:
    us-east-1:
      HVM64: ami-0123456789abcdef0
    us-west-2:
      HVM64: ami-0456789012abcdef3

  # Map environment to configuration
  EnvironmentConfig:
    dev:
      InstanceCount: '1'
      VolumeSize: '20'
    staging:
      InstanceCount: '2'
      VolumeSize: '50'
    prod:
      InstanceCount: '3'
      VolumeSize: '100'

Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      # Use parameter directly
      InstanceType: !Ref InstanceType

      # Chain mappings: InstanceType -> Arch -> Region AMI
      ImageId: !FindInMap
        - RegionAMI
        - !Ref 'AWS::Region'
        - !FindInMap
          - InstanceTypeArch
          - !Ref InstanceType
          - Arch

      # Use environment mapping
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: !FindInMap
              - EnvironmentConfig
              - !Ref Environment
              - VolumeSize

      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: InstanceType
          Value: !Ref InstanceType
```

---

## Multi-Region Template Design

### Complete Multi-Region Example

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Multi-region deployment template

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

  InstanceType:
    Type: String
    Default: t3.micro

Mappings:
  # Region-specific AMIs
  RegionAMI:
    us-east-1:
      AMZNLINUX2: ami-0c02fb55956c7d316
      UBUNTU20: ami-042e8287309f5df03
    us-west-2:
      AMZNLINUX2: ami-0892d3c7ee96c0bf7
      UBUNTU20: ami-0ca5c3bd5a268e7db
    eu-west-1:
      AMZNLINUX2: ami-0d71ea30463e0ff8d
      UBUNTU20: ami-0e66f5495b4efdd0f
    ap-northeast-1:
      AMZNLINUX2: ami-0f27d081df46f326c
      UBUNTU20: ami-0ee88be43f0fda84c

  # Region-specific settings
  RegionSettings:
    us-east-1:
      S3Endpoint: s3.amazonaws.com
      ELBAccountId: '127311923021'
      AZCount: '6'
    us-west-2:
      S3Endpoint: s3-us-west-2.amazonaws.com
      ELBAccountId: '797873946194'
      AZCount: '4'
    eu-west-1:
      S3Endpoint: s3-eu-west-1.amazonaws.com
      ELBAccountId: '156460612806'
      AZCount: '3'
    ap-northeast-1:
      S3Endpoint: s3-ap-northeast-1.amazonaws.com
      ELBAccountId: '582318560864'
      AZCount: '3'

  # Environment configurations
  EnvironmentSettings:
    dev:
      InstanceType: t3.micro
      VolumeSize: 20
      Encrypted: 'false'
    staging:
      InstanceType: t3.small
      VolumeSize: 50
      Encrypted: 'true'
    prod:
      InstanceType: t3.large
      VolumeSize: 100
      Encrypted: 'true'

Resources:
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      # Region-aware AMI selection
      ImageId: !FindInMap [RegionAMI, !Ref 'AWS::Region', AMZNLINUX2]

      # Environment-aware sizing (with parameter override option)
      InstanceType: !If
        - UseDefaultInstanceType
        - !FindInMap [EnvironmentSettings, !Ref Environment, InstanceType]
        - !Ref InstanceType

      # Environment-aware storage
      BlockDeviceMappings:
        - DeviceName: /dev/xvda
          Ebs:
            VolumeSize: !FindInMap [EnvironmentSettings, !Ref Environment, VolumeSize]
            Encrypted: !FindInMap [EnvironmentSettings, !Ref Environment, Encrypted]

      Tags:
        - Key: Name
          Value: !Sub '${Environment}-webserver-${AWS::Region}'

Conditions:
  UseDefaultInstanceType: !Equals [!Ref InstanceType, 't3.micro']

Outputs:
  RegionInfo:
    Description: Current region information
    Value: !Sub |
      Region: ${AWS::Region}
      S3 Endpoint: ${RegionSettings.${AWS::Region}.S3Endpoint}
      AZ Count: ${RegionSettings.${AWS::Region}.AZCount}
```

---

## Rules for Parameter Validation

Rules provide more complex parameter validation than constraints alone.

```yaml
Rules:
  # Ensure production uses larger instances
  ProductionInstanceRule:
    RuleCondition: !Equals [!Ref Environment, 'prod']
    Assertions:
      - Assert: !Contains
          - - t3.large
            - t3.xlarge
            - m5.large
            - m5.xlarge
          - !Ref InstanceType
        AssertDescription: Production requires t3.large or larger instances

  # Ensure Multi-AZ for production databases
  ProductionDatabaseRule:
    RuleCondition: !Equals [!Ref Environment, 'prod']
    Assertions:
      - Assert: !Equals [!Ref MultiAZDatabase, 'true']
        AssertDescription: Production databases must be Multi-AZ

  # Ensure encryption for non-dev environments
  EncryptionRule:
    RuleCondition: !Not [!Equals [!Ref Environment, 'dev']]
    Assertions:
      - Assert: !Equals [!Ref EnableEncryption, 'true']
        AssertDescription: Encryption must be enabled for staging and production

  # Subnet and VPC must be specified together
  NetworkConfigRule:
    Assertions:
      - Assert: !Or
          - !And
            - !Not [!Equals [!Ref VPCId, '']]
            - !Not [!Equals [!Ref SubnetId, '']]
          - !And
            - !Equals [!Ref VPCId, '']
            - !Equals [!Ref SubnetId, '']
        AssertDescription: VPC and Subnet must both be specified or both be empty
```

---

## Complete Template Example

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: |
  Production-ready template with comprehensive
  parameters and mappings for multi-environment deployment

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: "Environment Settings"
        Parameters:
          - Environment
          - ProjectName

      - Label:
          default: "Network Configuration"
        Parameters:
          - VPCCidr
          - CreateNewVPC

      - Label:
          default: "Compute Configuration"
        Parameters:
          - InstanceType
          - KeyPairName
          - OperatingSystem

      - Label:
          default: "Database Configuration"
        Parameters:
          - DBInstanceClass
          - DBName
          - DBUsername
          - DBPassword
          - MultiAZDatabase

    ParameterLabels:
      Environment:
        default: "Deployment Environment"
      ProjectName:
        default: "Project Name"
      VPCCidr:
        default: "VPC CIDR Block"
      InstanceType:
        default: "EC2 Instance Type"
      DBPassword:
        default: "Database Master Password (min 8 chars)"

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: Target deployment environment

  ProjectName:
    Type: String
    Default: myapp
    MinLength: 3
    MaxLength: 20
    AllowedPattern: '^[a-z][a-z0-9-]*$'
    Description: Project name (lowercase, alphanumeric, hyphens)

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(1[6-9]|2[0-8]))$'
    Description: CIDR block for the VPC

  CreateNewVPC:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Create a new VPC or use existing

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

  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access

  OperatingSystem:
    Type: String
    Default: AmazonLinux2
    AllowedValues:
      - AmazonLinux2
      - Ubuntu20
    Description: Operating system for EC2 instances

  DBInstanceClass:
    Type: String
    Default: db.t3.micro
    AllowedValues:
      - db.t3.micro
      - db.t3.small
      - db.t3.medium
      - db.r5.large
    Description: RDS instance class

  DBName:
    Type: String
    Default: myappdb
    MinLength: 4
    MaxLength: 64
    AllowedPattern: '^[a-zA-Z][a-zA-Z0-9]*$'
    Description: Database name

  DBUsername:
    Type: String
    Default: admin
    MinLength: 4
    MaxLength: 16
    AllowedPattern: '^[a-zA-Z][a-zA-Z0-9]*$'
    Description: Database master username

  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    MaxLength: 41
    AllowedPattern: '^[a-zA-Z0-9!@#$%^&*()_+=]*$'
    Description: Database master password

  MultiAZDatabase:
    Type: String
    Default: 'false'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable Multi-AZ for RDS

Mappings:
  RegionAMI:
    us-east-1:
      AmazonLinux2: ami-0c02fb55956c7d316
      Ubuntu20: ami-042e8287309f5df03
    us-west-2:
      AmazonLinux2: ami-0892d3c7ee96c0bf7
      Ubuntu20: ami-0ca5c3bd5a268e7db
    eu-west-1:
      AmazonLinux2: ami-0d71ea30463e0ff8d
      Ubuntu20: ami-0e66f5495b4efdd0f

  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      MinSize: '1'
      MaxSize: '2'
      DBInstanceClass: db.t3.micro
      MultiAZ: 'false'
    staging:
      InstanceType: t3.small
      MinSize: '2'
      MaxSize: '4'
      DBInstanceClass: db.t3.small
      MultiAZ: 'false'
    prod:
      InstanceType: t3.large
      MinSize: '2'
      MaxSize: '10'
      DBInstanceClass: db.r5.large
      MultiAZ: 'true'

Rules:
  ProductionValidation:
    RuleCondition: !Equals [!Ref Environment, 'prod']
    Assertions:
      - Assert: !Contains
          - - t3.large
            - m5.large
            - m5.xlarge
          - !Ref InstanceType
        AssertDescription: Production requires t3.large or larger
      - Assert: !Equals [!Ref MultiAZDatabase, 'true']
        AssertDescription: Production requires Multi-AZ database

Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']
  CreateVPC: !Equals [!Ref CreateNewVPC, 'true']
  UseMultiAZ: !Or
    - !Condition IsProduction
    - !Equals [!Ref MultiAZDatabase, 'true']

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Condition: CreateVPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-vpc'
        - Key: Environment
          Value: !Ref Environment

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap
        - RegionAMI
        - !Ref 'AWS::Region'
        - !Ref OperatingSystem
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyPairName
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-webserver'

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0'
      DBName: !Ref DBName
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: '20'
      MultiAZ: !If [UseMultiAZ, true, false]
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-${Environment}-database'

Outputs:
  Environment:
    Description: Deployment environment
    Value: !Ref Environment

  VPCId:
    Condition: CreateVPC
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  WebServerIP:
    Description: Web server public IP
    Value: !GetAtt WebServer.PublicIp

  DatabaseEndpoint:
    Description: RDS endpoint
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub '${AWS::StackName}-DBEndpoint'
```

---

## Summary

### Key Takeaways

1. **Parameters** provide runtime customization
2. **Mappings** provide static lookup tables
3. Use **AWS-specific types** for better console integration
4. Use **SSM Parameter Store types** for dynamic values
5. **Rules** validate parameter combinations
6. **Metadata Interface** improves console UX
7. Combine parameters and mappings for flexible templates

### When to Use Each

| Feature | Use Case |
|---------|----------|
| **Parameters** | User-provided values at runtime |
| **Mappings** | Static, pre-defined lookup tables |
| **SSM Parameters** | Dynamic, centrally managed values |
| **Rules** | Complex parameter validation |

---

## Knowledge Check

1. What is the difference between Parameters and Mappings?
2. How do you hide a parameter value in the console and logs?
3. What AWS-specific parameter types are available for EC2?
4. How do you retrieve the latest AMI automatically?
5. When would you use Rules over ConstraintDescription?

---

**Next:** [06 - Resources Deep Dive](./06-resources-deep-dive.md)

**Previous:** [04 - Intrinsic Functions](./04-intrinsic-functions.md)
