# Lesson 04: CloudFormation Intrinsic Functions

## Introduction

Intrinsic functions are built-in CloudFormation functions that help you manage your stacks. They enable dynamic value assignment, conditional logic, and reference resolution at runtime. This lesson covers all the essential intrinsic functions you need to master.

---

## Overview of Intrinsic Functions

```
┌─────────────────────────────────────────────────────────────────┐
│              CloudFormation Intrinsic Functions                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Reference Functions        String Functions                     │
│  ├── Ref                    ├── Fn::Sub                         │
│  ├── Fn::GetAtt             ├── Fn::Join                        │
│  └── Fn::ImportValue        ├── Fn::Split                       │
│                             └── Fn::Base64                       │
│                                                                  │
│  Conditional Functions      List Functions                       │
│  ├── Fn::If                 ├── Fn::Select                      │
│  ├── Fn::Equals             ├── Fn::GetAZs                      │
│  ├── Fn::And                └── Fn::Cidr                        │
│  ├── Fn::Or                                                      │
│  └── Fn::Not                                                     │
│                                                                  │
│  Lookup Functions           Transform Functions                  │
│  ├── Fn::FindInMap          └── Fn::Transform                   │
│  └── Fn::Length                                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### YAML Syntax

Functions can be written in two ways:

```yaml
# Full function syntax
Fn::Ref: MyResource
Fn::GetAtt: [MyResource, Arn]

# Short form (recommended)
!Ref MyResource
!GetAtt MyResource.Arn
```

---

## Ref Function

Returns the value of a parameter or the physical ID of a resource.

### Syntax

```yaml
# Full syntax
Fn::Ref: LogicalName

# Short syntax (recommended)
!Ref LogicalName
```

### Reference Parameters

```yaml
Parameters:
  InstanceType:
    Type: String
    Default: t3.micro

  Environment:
    Type: String
    Default: dev

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # Reference parameter value
      InstanceType: !Ref InstanceType
      Tags:
        - Key: Environment
          Value: !Ref Environment
```

### Reference Resources

```yaml
Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      # !Ref returns the VPC ID
      VpcId: !Ref MyVPC
      CidrBlock: 10.0.1.0/24

  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: My security group
      # !Ref returns the VPC ID
      VpcId: !Ref MyVPC

  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # !Ref returns the Subnet ID
      SubnetId: !Ref MySubnet
      SecurityGroupIds:
        # !Ref returns the Security Group ID
        - !Ref MySecurityGroup
```

### What Ref Returns for Common Resources

| Resource Type | Ref Returns |
|--------------|-------------|
| `AWS::EC2::VPC` | VPC ID |
| `AWS::EC2::Subnet` | Subnet ID |
| `AWS::EC2::Instance` | Instance ID |
| `AWS::EC2::SecurityGroup` | Security Group ID |
| `AWS::S3::Bucket` | Bucket Name |
| `AWS::IAM::Role` | Role Name |
| `AWS::Lambda::Function` | Function Name |
| `AWS::RDS::DBInstance` | DB Instance ID |
| `AWS::CloudFormation::Stack` | Stack ID |

---

## Fn::GetAtt

Returns an attribute value from a resource.

### Syntax

```yaml
# Full syntax
Fn::GetAtt:
  - LogicalResourceName
  - AttributeName

# Alternative full syntax
Fn::GetAtt: [LogicalResourceName, AttributeName]

# Short syntax (recommended)
!GetAtt LogicalResourceName.AttributeName
```

### Common Examples

```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: ami-12345678

  MyBucket:
    Type: AWS::S3::Bucket

  MyDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: mysql
      MasterUsername: admin
      MasterUserPassword: mypassword

  MyLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: python3.9
      Handler: index.handler
      Role: !GetAtt MyRole.Arn
      Code:
        ZipFile: |
          def handler(event, context):
              return "Hello"

  MyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole

Outputs:
  # EC2 Instance attributes
  InstancePublicIP:
    Value: !GetAtt MyInstance.PublicIp

  InstancePrivateIP:
    Value: !GetAtt MyInstance.PrivateIp

  InstanceAZ:
    Value: !GetAtt MyInstance.AvailabilityZone

  # S3 Bucket attributes
  BucketArn:
    Value: !GetAtt MyBucket.Arn

  BucketDomainName:
    Value: !GetAtt MyBucket.DomainName

  BucketRegionalDomainName:
    Value: !GetAtt MyBucket.RegionalDomainName

  # RDS attributes
  DatabaseEndpoint:
    Value: !GetAtt MyDatabase.Endpoint.Address

  DatabasePort:
    Value: !GetAtt MyDatabase.Endpoint.Port

  # Lambda attributes
  LambdaArn:
    Value: !GetAtt MyLambda.Arn

  # IAM Role attributes
  RoleArn:
    Value: !GetAtt MyRole.Arn
```

### Common GetAtt Attributes by Resource Type

**AWS::EC2::Instance:**
```yaml
!GetAtt Instance.AvailabilityZone
!GetAtt Instance.PrivateDnsName
!GetAtt Instance.PublicDnsName
!GetAtt Instance.PrivateIp
!GetAtt Instance.PublicIp
```

**AWS::S3::Bucket:**
```yaml
!GetAtt Bucket.Arn
!GetAtt Bucket.DomainName
!GetAtt Bucket.RegionalDomainName
!GetAtt Bucket.WebsiteURL
```

**AWS::RDS::DBInstance:**
```yaml
!GetAtt Database.Endpoint.Address
!GetAtt Database.Endpoint.Port
!GetAtt Database.Endpoint.HostedZoneId
```

**AWS::Lambda::Function:**
```yaml
!GetAtt Function.Arn
!GetAtt Function.SnapStartResponse.ApplyOn
!GetAtt Function.SnapStartResponse.OptimizationStatus
```

**AWS::Elastic LoadBalancingV2::LoadBalancer:**
```yaml
!GetAtt ALB.DNSName
!GetAtt ALB.CanonicalHostedZoneID
!GetAtt ALB.LoadBalancerFullName
!GetAtt ALB.SecurityGroups
```

---

## Fn::Sub

Substitutes variables in a string with their values.

### Basic Syntax

```yaml
# Simple substitution
!Sub 'Hello ${Variable}'

# With mapping
!Sub
  - 'String with ${Var1} and ${Var2}'
  - Var1: Value1
    Var2: Value2
```

### Using with Parameters and Resources

```yaml
Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      # Substitute parameter
      BucketName: !Sub 'my-bucket-${Environment}'

  MyRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${Environment}-app-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
```

### Using Pseudo Parameters

```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      # Use AWS pseudo parameters
      BucketName: !Sub 'app-${AWS::AccountId}-${AWS::Region}'

Outputs:
  BucketARN:
    # Construct ARN using pseudo parameters
    Value: !Sub 'arn:aws:s3:::${MyBucket}'

  StackURL:
    Value: !Sub 'https://${AWS::Region}.console.aws.amazon.com/cloudformation/home?region=${AWS::Region}#/stacks/stackinfo?stackId=${AWS::StackId}'
```

### Multi-Line Strings with Sub

```yaml
Resources:
  MyLambda:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          import boto3

          BUCKET_NAME = '${MyBucket}'
          REGION = '${AWS::Region}'
          ACCOUNT = '${AWS::AccountId}'

          def handler(event, context):
              print(f"Processing in {REGION}")
              return {"bucket": BUCKET_NAME}
```

### Variable Mapping

```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Base64:
          !Sub
            - |
              #!/bin/bash
              echo "Environment: ${Env}"
              echo "Database: ${DBHost}:${DBPort}"
              echo "S3 Bucket: ${BucketName}"
            - Env: !Ref Environment
              DBHost: !GetAtt Database.Endpoint.Address
              DBPort: !GetAtt Database.Endpoint.Port
              BucketName: !Ref MyBucket
```

### Escaping Dollar Signs

```yaml
# To include a literal ${, use ${!
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          #!/bin/bash
          # This ${variable} will be substituted
          BUCKET="${MyBucket}"

          # This ${!variable} will remain as ${variable}
          echo "Literal: ${!PATH}"
```

---

## Fn::Join

Joins values with a delimiter.

### Syntax

```yaml
!Join
  - 'delimiter'
  - - Value1
    - Value2
    - Value3
```

### Examples

```yaml
Resources:
  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: !Join
        - ' '
        - - 'Security group for'
          - !Ref Environment
          - 'environment'

Outputs:
  # Join subnet IDs with comma
  SubnetIds:
    Value: !Join
      - ','
      - - !Ref PublicSubnet1
        - !Ref PublicSubnet2
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  # Create a connection string
  DatabaseConnectionString:
    Value: !Join
      - ''
      - - 'mysql://'
        - !Ref DBUsername
        - ':'
        - !Ref DBPassword
        - '@'
        - !GetAtt Database.Endpoint.Address
        - ':'
        - !GetAtt Database.Endpoint.Port
        - '/'
        - !Ref DBName

  # Alternative using Fn::Sub (preferred for URLs)
  DatabaseConnectionStringSub:
    Value: !Sub 'mysql://${DBUsername}:${DBPassword}@${Database.Endpoint.Address}:${Database.Endpoint.Port}/${DBName}'
```

### Join vs Sub

```yaml
# Using Join (more verbose)
Value: !Join
  - ''
  - - 'arn:aws:s3:::'
    - !Ref MyBucket
    - '/*'

# Using Sub (cleaner)
Value: !Sub 'arn:aws:s3:::${MyBucket}/*'
```

---

## Fn::Split

Splits a string into a list of values.

### Syntax

```yaml
!Split ['delimiter', 'string']
```

### Examples

```yaml
Parameters:
  SubnetCidrs:
    Type: String
    Default: '10.0.1.0/24,10.0.2.0/24,10.0.3.0/24'

Resources:
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # Split and select first CIDR
      CidrBlock: !Select [0, !Split [',', !Ref SubnetCidrs]]

  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # Split and select second CIDR
      CidrBlock: !Select [1, !Split [',', !Ref SubnetCidrs]]

Outputs:
  # Get domain from ARN
  BucketDomain:
    Value: !Select
      - 2
      - !Split
        - '/'
        - !GetAtt MyBucket.WebsiteURL
```

---

## Fn::Select

Selects a single element from a list.

### Syntax

```yaml
!Select [index, list]
```

### Examples

```yaml
Parameters:
  AvailabilityZones:
    Type: List<AWS::EC2::AvailabilityZone::Name>
    Default: 'us-east-1a,us-east-1b,us-east-1c'

Resources:
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      # Select first AZ
      AvailabilityZone: !Select [0, !Ref AvailabilityZones]

  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      # Select second AZ
      AvailabilityZone: !Select [1, !Ref AvailabilityZones]

  # Using with GetAZs
  Subnet3:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.3.0/24
      # Select first AZ from current region
      AvailabilityZone: !Select
        - 0
        - !GetAZs ''
```

---

## Fn::GetAZs

Returns an array of Availability Zones for a region.

### Syntax

```yaml
# Get AZs for current region
!GetAZs ''

# Get AZs for specific region
!GetAZs 'us-east-1'

# Or using Ref
!GetAZs !Ref 'AWS::Region'
```

### Examples

```yaml
Resources:
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.10.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.11.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
```

---

## Fn::Cidr

Returns an array of CIDR address blocks.

### Syntax

```yaml
!Cidr [ipBlock, count, cidrBits]
```

- `ipBlock`: The CIDR address block to partition
- `count`: Number of CIDR blocks to generate
- `cidrBits`: Number of subnet bits for each CIDR block

### Examples

```yaml
Parameters:
  VPCCidr:
    Type: String
    Default: 10.0.0.0/16

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr

  # Generate 4 /24 subnets from /16 VPC
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # First /24 subnet: 10.0.0.0/24
      CidrBlock: !Select [0, !Cidr [!Ref VPCCidr, 4, 8]]

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # Second /24 subnet: 10.0.1.0/24
      CidrBlock: !Select [1, !Cidr [!Ref VPCCidr, 4, 8]]

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # Third /24 subnet: 10.0.2.0/24
      CidrBlock: !Select [2, !Cidr [!Ref VPCCidr, 4, 8]]

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      # Fourth /24 subnet: 10.0.3.0/24
      CidrBlock: !Select [3, !Cidr [!Ref VPCCidr, 4, 8]]
```

### CIDR Bits Calculation

| VPC CIDR | cidrBits | Resulting Subnet Size |
|----------|----------|----------------------|
| /16 | 8 | /24 (256 addresses) |
| /16 | 4 | /20 (4096 addresses) |
| /20 | 4 | /24 (256 addresses) |
| /24 | 4 | /28 (16 addresses) |

---

## Fn::If

Returns one value if a condition is true and another if false.

### Syntax

```yaml
!If [ConditionName, ValueIfTrue, ValueIfFalse]
```

### Examples

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']
  CreateDevResources: !Equals [!Ref Environment, 'dev']

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # Conditional instance type
      InstanceType: !If
        - IsProduction
        - t3.large
        - t3.micro

      # Conditional tags
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-webserver'
        # Add criticality tag only in production
        - !If
          - IsProduction
          - Key: Criticality
            Value: High
          - !Ref AWS::NoValue  # Don't add tag

  # Conditional MultiAZ
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: !If
        - IsProduction
        - db.r5.large
        - db.t3.micro
      MultiAZ: !If
        - IsProduction
        - true
        - false
      AllocatedStorage: !If
        - IsProduction
        - 100
        - 20

Outputs:
  DatabaseEndpoint:
    Value: !GetAtt Database.Endpoint.Address

  EnvironmentType:
    Value: !If
      - IsProduction
      - 'This is a Production Environment'
      - 'This is a Non-Production Environment'
```

### Using AWS::NoValue

```yaml
# Remove a property entirely when condition is false
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      # Only add KeyName if HasKeyName condition is true
      KeyName: !If
        - HasKeyName
        - !Ref KeyName
        - !Ref AWS::NoValue  # Property won't exist
```

---

## Fn::Equals

Compares two values for equality (used in Conditions).

### Syntax

```yaml
!Equals [value1, value2]
```

### Examples

```yaml
Conditions:
  # Compare with string
  IsProduction: !Equals [!Ref Environment, 'prod']

  # Compare with number
  SingleInstance: !Equals [!Ref InstanceCount, 1]

  # Compare with pseudo parameter
  IsUsEast1: !Equals [!Ref 'AWS::Region', 'us-east-1']

  # Compare two parameters
  SameAccount: !Equals [!Ref SourceAccount, !Ref 'AWS::AccountId']
```

---

## Fn::And

Returns true if ALL conditions are true.

### Syntax

```yaml
!And
  - Condition1
  - Condition2
  - Condition3  # 2-10 conditions
```

### Examples

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']
  IsUsRegion: !Or
    - !Equals [!Ref 'AWS::Region', 'us-east-1']
    - !Equals [!Ref 'AWS::Region', 'us-west-2']

  # Both conditions must be true
  CreateProdUsResources: !And
    - !Condition IsProduction
    - !Condition IsUsRegion

  # Combine multiple checks
  EnableHighAvailability: !And
    - !Condition IsProduction
    - !Equals [!Ref EnableHA, 'true']
    - !Not [!Equals [!Ref InstanceCount, 1]]
```

---

## Fn::Or

Returns true if ANY condition is true.

### Syntax

```yaml
!Or
  - Condition1
  - Condition2
  - Condition3  # 2-10 conditions
```

### Examples

```yaml
Conditions:
  # True if either prod or staging
  IsHigherEnvironment: !Or
    - !Equals [!Ref Environment, 'prod']
    - !Equals [!Ref Environment, 'staging']

  # True if in any US region
  IsUSRegion: !Or
    - !Equals [!Ref 'AWS::Region', 'us-east-1']
    - !Equals [!Ref 'AWS::Region', 'us-east-2']
    - !Equals [!Ref 'AWS::Region', 'us-west-1']
    - !Equals [!Ref 'AWS::Region', 'us-west-2']
```

---

## Fn::Not

Negates a condition.

### Syntax

```yaml
!Not [Condition]
```

### Examples

```yaml
Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']

  # Negate condition
  IsNotProduction: !Not [!Condition IsProduction]

  # Alternative syntax
  IsDevelopment: !Not [!Equals [!Ref Environment, 'prod']]

  # Check if parameter is empty
  HasBucketName: !Not [!Equals [!Ref BucketName, '']]
```

---

## Fn::FindInMap

Returns value from a mapping table.

### Syntax

```yaml
!FindInMap [MapName, TopLevelKey, SecondLevelKey]
```

### Examples

```yaml
Mappings:
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

  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      MinSize: '1'
      MaxSize: '2'
    staging:
      InstanceType: t3.small
      MinSize: '2'
      MaxSize: '4'
    prod:
      InstanceType: t3.large
      MinSize: '2'
      MaxSize: '10'

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      # Find AMI based on current region
      ImageId: !FindInMap
        - RegionAMI
        - !Ref 'AWS::Region'
        - HVM64

      # Find instance type based on environment parameter
      InstanceType: !FindInMap
        - EnvironmentConfig
        - !Ref Environment
        - InstanceType

  MyASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: !FindInMap
        - EnvironmentConfig
        - !Ref Environment
        - MinSize
      MaxSize: !FindInMap
        - EnvironmentConfig
        - !Ref Environment
        - MaxSize
```

---

## Fn::ImportValue

Imports a value exported from another stack.

### Syntax

```yaml
!ImportValue ExportedValueName

# With Sub for dynamic names
!ImportValue !Sub '${StackPrefix}-VPCId'
```

### Example: Cross-Stack References

**Stack A (Network Stack) - Exports values:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Network Stack

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: network-stack-vpc-id  # Export name

  PublicSubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet
    Export:
      Name: network-stack-public-subnet
```

**Stack B (Application Stack) - Imports values:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Application Stack

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      # Import subnet from network stack
      SubnetId: !ImportValue network-stack-public-subnet

  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: App security group
      # Import VPC from network stack
      VpcId: !ImportValue network-stack-vpc-id
```

### Dynamic Import Names

```yaml
Parameters:
  NetworkStackName:
    Type: String
    Default: production-network

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      SubnetId: !ImportValue
        Fn::Sub: '${NetworkStackName}-PublicSubnetId'
```

---

## Fn::Base64

Encodes a string to Base64.

### Syntax

```yaml
!Base64 string
```

### Example: EC2 User Data

```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: !Ref AMI
      # User data must be Base64 encoded
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "Hello World" > /var/www/html/index.html

  # Combining Base64 with Sub
  MyInstanceWithSub:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: !Ref AMI
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          echo "Environment: ${Environment}" > /var/www/html/index.html
          echo "Region: ${AWS::Region}" >> /var/www/html/index.html
```

---

## Fn::Length

Returns the number of elements in an array.

### Syntax

```yaml
!Length list
```

### Example

```yaml
Parameters:
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Select subnets

Conditions:
  # Check if multiple subnets selected
  MultipleSubnets: !Not [!Equals [!Length !Ref SubnetIds, 1]]

Resources:
  LoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Condition: MultipleSubnets
    Properties:
      Subnets: !Ref SubnetIds
```

---

## Fn::Transform

Apply macros to template sections.

### Syntax

```yaml
Fn::Transform:
  Name: MacroName
  Parameters:
    Key: Value
```

### Example: AWS::Include

```yaml
# Include content from S3
Resources:
  Fn::Transform:
    Name: AWS::Include
    Parameters:
      Location: s3://my-bucket/snippets/common-resources.yaml
```

---

## Complete Example: Function Chaining

Here's a complex example combining multiple intrinsic functions:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Intrinsic Functions Complete Example

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16

Mappings:
  EnvironmentConfig:
    dev:
      InstanceType: t3.micro
      MultiAZ: 'false'
    staging:
      InstanceType: t3.small
      MultiAZ: 'false'
    prod:
      InstanceType: t3.large
      MultiAZ: 'true'

Conditions:
  IsProduction: !Equals [!Ref Environment, 'prod']
  EnableMultiAZ: !Equals
    - !FindInMap [EnvironmentConfig, !Ref Environment, MultiAZ]
    - 'true'

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-vpc'

  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Cidr [!Ref VPCCidr, 4, 8]]
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-subnet-1'

  Subnet2:
    Type: AWS::EC2::Subnet
    Condition: EnableMultiAZ
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [1, !Cidr [!Ref VPCCidr, 4, 8]]
      AvailabilityZone: !Select [1, !GetAZs '']
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-subnet-2'

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !FindInMap
        - EnvironmentConfig
        - !Ref Environment
        - InstanceType
      SubnetId: !Ref Subnet1
      Tags:
        - Key: Name
          Value: !Join
            - '-'
            - - !Ref Environment
              - webserver
              - !Ref 'AWS::Region'
        - !If
          - IsProduction
          - Key: Backup
            Value: 'true'
          - !Ref AWS::NoValue
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          echo "Environment: ${Environment}"
          echo "Account: ${AWS::AccountId}"
          echo "Region: ${AWS::Region}"
          echo "VPC ID: ${VPC}"

Outputs:
  VPCId:
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  SubnetIds:
    Value: !If
      - EnableMultiAZ
      - !Join [',', [!Ref Subnet1, !Ref Subnet2]]
      - !Ref Subnet1
    Export:
      Name: !Sub '${AWS::StackName}-SubnetIds'

  WebServerInfo:
    Value: !Sub |
      Instance ID: ${WebServer}
      Private IP: ${WebServer.PrivateIp}
```

---

## Function Reference Quick Guide

| Function | Purpose | Common Use Case |
|----------|---------|-----------------|
| `!Ref` | Reference parameter/resource | Get resource ID |
| `!GetAtt` | Get resource attribute | Get ARN, IP, endpoint |
| `!Sub` | String substitution | Build names, ARNs |
| `!Join` | Join array with delimiter | Create lists |
| `!Split` | Split string to array | Parse values |
| `!Select` | Select from array | Choose AZ, subnet |
| `!GetAZs` | Get availability zones | Dynamic AZ selection |
| `!Cidr` | Generate CIDR blocks | Subnet planning |
| `!If` | Conditional value | Env-based config |
| `!Equals` | Compare values | Define conditions |
| `!And` / `!Or` / `!Not` | Logical operators | Complex conditions |
| `!FindInMap` | Lookup from mapping | Region AMIs |
| `!ImportValue` | Cross-stack reference | Share resources |
| `!Base64` | Encode to Base64 | User data |

---

## Knowledge Check

1. What is the difference between `!Ref` and `!GetAtt`?
2. When would you use `!Sub` instead of `!Join`?
3. How do you reference a value from another CloudFormation stack?
4. What does `!Ref AWS::NoValue` do?
5. How do you generate subnet CIDR blocks dynamically?

---

**Next:** [05 - Parameters and Mappings](./05-parameters-and-mappings.md)

**Previous:** [03 - Template Anatomy](./03-template-anatomy.md)
