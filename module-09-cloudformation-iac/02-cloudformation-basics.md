# Lesson 02: CloudFormation Basics

## Introduction

AWS CloudFormation is a service that helps you model and set up your AWS resources so that you can spend less time managing those resources and more time focusing on your applications. This lesson covers the foundational concepts you need to work effectively with CloudFormation.

---

## What is AWS CloudFormation?

AWS CloudFormation is an Infrastructure as Code (IaC) service that allows you to:

- **Define** your AWS infrastructure in text files (templates)
- **Provision** resources automatically and consistently
- **Manage** resource dependencies
- **Update** infrastructure safely with change sets
- **Delete** all resources cleanly

```
┌─────────────────────────────────────────────────────────────────┐
│                    CloudFormation Overview                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    Template (YAML/JSON)                                         │
│          │                                                       │
│          ▼                                                       │
│    ┌──────────────────────────────────────┐                     │
│    │         AWS CloudFormation           │                     │
│    │    (Orchestration & Provisioning)    │                     │
│    └──────────────────────────────────────┘                     │
│          │                                                       │
│          ▼                                                       │
│    ┌──────────────────────────────────────┐                     │
│    │              Stack                    │                     │
│    │  ┌────────┐ ┌────────┐ ┌────────┐   │                     │
│    │  │  VPC   │ │  EC2   │ │  RDS   │   │                     │
│    │  └────────┘ └────────┘ └────────┘   │                     │
│    │  ┌────────┐ ┌────────┐ ┌────────┐   │                     │
│    │  │  S3    │ │ Lambda │ │  IAM   │   │                     │
│    │  └────────┘ └────────┘ └────────┘   │                     │
│    └──────────────────────────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### 1. Templates

A **template** is a JSON or YAML file that describes the AWS resources you want to create.

**YAML Template Example:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Simple S3 bucket template

Resources:
  MyS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-example-bucket-12345
      VersioningConfiguration:
        Status: Enabled
      Tags:
        - Key: Environment
          Value: Development

Outputs:
  BucketName:
    Description: Name of the bucket
    Value: !Ref MyS3Bucket
  BucketArn:
    Description: ARN of the bucket
    Value: !GetAtt MyS3Bucket.Arn
```

**JSON Template Example:**
```json
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "Simple S3 bucket template",
  "Resources": {
    "MyS3Bucket": {
      "Type": "AWS::S3::Bucket",
      "Properties": {
        "BucketName": "my-example-bucket-12345",
        "VersioningConfiguration": {
          "Status": "Enabled"
        }
      }
    }
  }
}
```

#### YAML vs JSON

| Feature | YAML | JSON |
|---------|------|------|
| Readability | High | Medium |
| Comments | Supported (#) | Not supported |
| Verbosity | Less verbose | More verbose |
| Learning Curve | Easy | Easy |
| AWS Recommendation | Preferred | Supported |

**YAML Features:**
```yaml
# This is a comment (YAML only!)
Resources:
  # Multi-line strings
  MyResource:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: |
          def handler(event, context):
              return {
                  'statusCode': 200,
                  'body': 'Hello World!'
              }
```

### 2. Stacks

A **stack** is a collection of AWS resources that you manage as a single unit.

```
Template ──► CloudFormation ──► Stack
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                Resource 1   Resource 2   Resource 3
                (VPC)        (Subnet)     (EC2)
```

**Stack Characteristics:**
- All resources in a stack are created, updated, and deleted together
- Resources are managed through the stack lifecycle
- Stack names must be unique within a region
- Stacks can output values for other stacks to use

**Creating a Stack:**
```bash
# Using AWS CLI
aws cloudformation create-stack \
    --stack-name my-first-stack \
    --template-body file://template.yaml \
    --parameters ParameterKey=Environment,ParameterValue=dev

# Using AWS Console
# CloudFormation → Create stack → Upload template
```

### 3. Stack Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      Stack Lifecycle                             │
└─────────────────────────────────────────────────────────────────┘

    CREATE                  UPDATE                  DELETE
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│CREATE_IN_    │        │UPDATE_IN_    │        │DELETE_IN_    │
│PROGRESS      │        │PROGRESS      │        │PROGRESS      │
└──────────────┘        └──────────────┘        └──────────────┘
       │                       │                       │
   ┌───┴───┐               ┌───┴───┐               ┌───┴───┐
   ▼       ▼               ▼       ▼               ▼       ▼
┌──────┐ ┌──────┐    ┌──────┐ ┌──────────┐   ┌──────┐  (Stack
│CREATE│ │CREATE│    │UPDATE│ │UPDATE_   │   │DELETE│  Removed)
│COMPL-│ │FAILED│    │COMPL-│ │ROLLBACK_ │   │COMPL-│
│ETE   │ │      │    │ETE   │ │COMPLETE  │   │ETE   │
└──────┘ └──────┘    └──────┘ └──────────┘   └──────┘
             │                      │
             ▼                      ▼
       ┌──────────┐          ┌──────────┐
       │ROLLBACK_ │          │Previous  │
       │COMPLETE  │          │State     │
       └──────────┘          └──────────┘
```

**Stack States:**

| State | Description |
|-------|-------------|
| `CREATE_IN_PROGRESS` | Stack creation started |
| `CREATE_COMPLETE` | All resources created successfully |
| `CREATE_FAILED` | One or more resources failed to create |
| `ROLLBACK_IN_PROGRESS` | Rolling back failed creation |
| `ROLLBACK_COMPLETE` | Rollback completed |
| `UPDATE_IN_PROGRESS` | Stack update started |
| `UPDATE_COMPLETE` | Update successful |
| `UPDATE_ROLLBACK_IN_PROGRESS` | Rolling back failed update |
| `UPDATE_ROLLBACK_COMPLETE` | Update rollback completed |
| `DELETE_IN_PROGRESS` | Stack deletion started |
| `DELETE_COMPLETE` | Stack deleted |
| `DELETE_FAILED` | Deletion failed (manual intervention needed) |

---

## Change Sets

**Change sets** allow you to preview changes to your stack before applying them.

### Why Use Change Sets?

```
Without Change Sets:                 With Change Sets:

Template Change                      Template Change
      │                                   │
      ▼                                   ▼
┌──────────────┐                   ┌──────────────┐
│ Direct Update│                   │ Create       │
│ (Risky!)     │                   │ Change Set   │
└──────────────┘                   └──────────────┘
      │                                   │
      ▼                                   ▼
┌──────────────┐                   ┌──────────────┐
│ Resources    │                   │ Review       │
│ Modified     │                   │ Changes      │
│ (Unknown     │                   │ (Safe!)      │
│ Impact)      │                   └──────────────┘
└──────────────┘                          │
                                          ▼
                                   ┌──────────────┐
                                   │ Execute or   │
                                   │ Reject       │
                                   └──────────────┘
```

### Change Set Workflow

```bash
# Step 1: Create a change set
aws cloudformation create-change-set \
    --stack-name my-stack \
    --template-body file://updated-template.yaml \
    --change-set-name my-changes \
    --description "Update instance type and add tags"

# Step 2: Describe the change set (review changes)
aws cloudformation describe-change-set \
    --stack-name my-stack \
    --change-set-name my-changes

# Step 3: Execute the change set (apply changes)
aws cloudformation execute-change-set \
    --stack-name my-stack \
    --change-set-name my-changes

# OR: Delete the change set (reject changes)
aws cloudformation delete-change-set \
    --stack-name my-stack \
    --change-set-name my-changes
```

### Understanding Change Set Output

```json
{
  "Changes": [
    {
      "Type": "Resource",
      "ResourceChange": {
        "Action": "Modify",
        "LogicalResourceId": "WebServer",
        "PhysicalResourceId": "i-1234567890abcdef0",
        "ResourceType": "AWS::EC2::Instance",
        "Replacement": "True",
        "Details": [
          {
            "Target": {
              "Attribute": "Properties",
              "Name": "InstanceType"
            },
            "Evaluation": "Static",
            "ChangeSource": "DirectModification"
          }
        ]
      }
    }
  ]
}
```

**Change Actions:**

| Action | Description | Impact |
|--------|-------------|--------|
| **Add** | New resource created | None (new resource) |
| **Modify** | Resource updated | Depends on replacement |
| **Remove** | Resource deleted | Data loss possible |

**Replacement Values:**

| Value | Meaning |
|-------|---------|
| `True` | Resource will be replaced (deleted and recreated) |
| `False` | Resource updated in-place |
| `Conditional` | Depends on other factors |

---

## Drift Detection

**Drift** occurs when actual resource configurations differ from the expected CloudFormation template configurations.

### How Drift Happens

```
┌─────────────────────────────────────────────────────────────────┐
│                    Causes of Configuration Drift                 │
└─────────────────────────────────────────────────────────────────┘

1. Manual Console Changes
   CloudFormation: InstanceType = t3.micro
   Console Change: InstanceType = t3.large  ← DRIFT!

2. CLI/SDK Modifications
   aws ec2 modify-instance-attribute ...   ← DRIFT!

3. Other Automation Tools
   Ansible, Chef, Puppet changes           ← DRIFT!

4. Emergency Fixes
   "Quick fix" in production               ← DRIFT!
```

### Detecting Drift

```bash
# Step 1: Initiate drift detection
aws cloudformation detect-stack-drift \
    --stack-name my-stack

# Returns: StackDriftDetectionId

# Step 2: Check detection status
aws cloudformation describe-stack-drift-detection-status \
    --stack-drift-detection-id <detection-id>

# Step 3: View drift results
aws cloudformation describe-stack-resource-drifts \
    --stack-name my-stack
```

### Drift Status Values

| Stack Drift Status | Meaning |
|-------------------|---------|
| `IN_SYNC` | All resources match template |
| `DRIFTED` | One or more resources have drifted |
| `NOT_CHECKED` | Drift detection not run |
| `UNKNOWN` | Drift status undetermined |

| Resource Drift Status | Meaning |
|----------------------|---------|
| `IN_SYNC` | Resource matches template |
| `MODIFIED` | Resource properties changed |
| `DELETED` | Resource deleted outside CloudFormation |
| `NOT_CHECKED` | Resource not checked for drift |

### Example Drift Output

```json
{
  "StackResourceDrifts": [
    {
      "LogicalResourceId": "WebServerInstance",
      "PhysicalResourceId": "i-0123456789abcdef",
      "ResourceType": "AWS::EC2::Instance",
      "StackResourceDriftStatus": "MODIFIED",
      "PropertyDifferences": [
        {
          "PropertyPath": "/InstanceType",
          "ExpectedValue": "t3.micro",
          "ActualValue": "t3.large",
          "DifferenceType": "NOT_EQUAL"
        }
      ]
    }
  ]
}
```

### Remediating Drift

```
Option 1: Update the Stack (align actual → template)
┌──────────────┐        ┌──────────────┐
│   Actual     │  ───►  │  Match       │
│  t3.large    │        │  Template    │
└──────────────┘        │  t3.micro    │
                        └──────────────┘

Option 2: Update the Template (align template → actual)
┌──────────────┐        ┌──────────────┐
│   Template   │  ───►  │  Match       │
│   t3.micro   │        │  Actual      │
└──────────────┘        │  t3.large    │
                        └──────────────┘

Option 3: Import Resources (complex scenarios)
```

---

## Template Validation

Before deploying, validate your templates:

### AWS CLI Validation

```bash
# Validate template syntax
aws cloudformation validate-template \
    --template-body file://template.yaml

# Output on success:
{
    "Parameters": [...],
    "Description": "...",
    "Capabilities": [...],
    "CapabilitiesReason": "..."
}

# Output on error:
An error occurred (ValidationError) when calling ValidateTemplate:
Template format error: [Specific error message]
```

### Common Validation Errors

```yaml
# Error 1: Invalid resource type
Resources:
  MyInstance:
    Type: AWS::EC2::Instanc  # Typo!

# Error 2: Missing required property
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    # Missing Properties section when required

# Error 3: Invalid reference
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      SubnetId: !Ref NonExistentSubnet  # Reference doesn't exist

# Error 4: Circular dependency
Resources:
  ResourceA:
    DependsOn: ResourceB
  ResourceB:
    DependsOn: ResourceA  # Circular!
```

### Using cfn-lint

```bash
# Install cfn-lint
pip install cfn-lint

# Run linter
cfn-lint template.yaml

# Output example:
W3010 Don't hardcode us-east-1 in the template
E3012 Property Resources/MyBucket/Properties/InvalidProperty not found
```

---

## Working with Stacks - CLI Commands

### Create Stack

```bash
# Basic creation
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-body file://template.yaml

# With parameters
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-body file://template.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=production \
        ParameterKey=InstanceType,ParameterValue=t3.large

# With IAM capabilities (required for IAM resources)
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-body file://template.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

# From S3 (for large templates)
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-url https://s3.amazonaws.com/bucket/template.yaml

# With tags
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-body file://template.yaml \
    --tags Key=Environment,Value=Production Key=Owner,Value=TeamA
```

### Monitor Stack Events

```bash
# Watch stack events
aws cloudformation describe-stack-events \
    --stack-name my-stack \
    --query 'StackEvents[*].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId,ResourceStatusReason]' \
    --output table

# Wait for stack creation
aws cloudformation wait stack-create-complete \
    --stack-name my-stack
```

### Update Stack

```bash
# Direct update (not recommended for production)
aws cloudformation update-stack \
    --stack-name my-stack \
    --template-body file://updated-template.yaml

# Recommended: Use change sets
aws cloudformation create-change-set \
    --stack-name my-stack \
    --template-body file://updated-template.yaml \
    --change-set-name update-v2
```

### Delete Stack

```bash
# Delete stack and all resources
aws cloudformation delete-stack \
    --stack-name my-stack

# Wait for deletion
aws cloudformation wait stack-delete-complete \
    --stack-name my-stack

# Force delete (retain certain resources)
aws cloudformation delete-stack \
    --stack-name my-stack \
    --retain-resources LogicalResourceId1 LogicalResourceId2
```

### List and Describe Stacks

```bash
# List all stacks
aws cloudformation list-stacks \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Describe specific stack
aws cloudformation describe-stacks \
    --stack-name my-stack

# Get stack outputs
aws cloudformation describe-stacks \
    --stack-name my-stack \
    --query 'Stacks[0].Outputs'

# List stack resources
aws cloudformation list-stack-resources \
    --stack-name my-stack
```

---

## Template Storage Options

### Local File (Small Templates)

```bash
# For templates up to 51,200 bytes
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-body file://template.yaml
```

### S3 Bucket (Large Templates)

```bash
# Upload template to S3
aws s3 cp template.yaml s3://my-bucket/templates/

# Reference from S3 (up to 1 MB)
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-url https://s3.amazonaws.com/my-bucket/templates/template.yaml
```

### Template Size Limits

| Method | Maximum Size |
|--------|-------------|
| `--template-body` (inline) | 51,200 bytes |
| `--template-url` (S3) | 1 MB (1,048,576 bytes) |

---

## AWS Console Workflow

### Creating a Stack via Console

```
Step 1: Navigate to CloudFormation
CloudFormation Console → Stacks → Create stack

Step 2: Specify Template
├── Option A: Template is ready
│   ├── Upload a template file
│   └── Amazon S3 URL
└── Option B: Use a sample template

Step 3: Specify Stack Details
├── Stack name: my-stack
└── Parameters: Fill in required values

Step 4: Configure Stack Options
├── Tags: Key-Value pairs
├── Permissions: IAM role
├── Stack failure options:
│   ├── Roll back all stack resources
│   └── Preserve successfully provisioned resources
└── Advanced options:
    ├── Stack policy
    ├── Rollback configuration
    ├── Notification options
    └── Termination protection

Step 5: Review and Create
├── Review all settings
└── Acknowledge IAM capabilities (if required)
```

---

## Practical Example: Complete Workflow

Let's walk through creating a simple VPC stack:

### Step 1: Create Template

```yaml
# simple-vpc.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Simple VPC with one public subnet

Parameters:
  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: CIDR block for VPC

  SubnetCidr:
    Type: String
    Default: 10.0.1.0/24
    Description: CIDR block for subnet

  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-vpc'
        - Key: Environment
          Value: !Ref Environment

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Ref SubnetCidr
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-public-subnet'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-igw'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-public-rt'

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  SubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${AWS::StackName}-SubnetId'
```

### Step 2: Validate Template

```bash
aws cloudformation validate-template \
    --template-body file://simple-vpc.yaml
```

### Step 3: Create Stack

```bash
aws cloudformation create-stack \
    --stack-name dev-vpc-stack \
    --template-body file://simple-vpc.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=dev \
        ParameterKey=VPCCidr,ParameterValue=10.0.0.0/16
```

### Step 4: Monitor Progress

```bash
# Watch stack events
watch -n 5 'aws cloudformation describe-stack-events \
    --stack-name dev-vpc-stack \
    --query "StackEvents[0:5].[Timestamp,ResourceStatus,LogicalResourceId]" \
    --output table'
```

### Step 5: Get Outputs

```bash
aws cloudformation describe-stacks \
    --stack-name dev-vpc-stack \
    --query 'Stacks[0].Outputs'
```

---

## Summary

### Key Takeaways

1. **Templates** are YAML/JSON files describing AWS resources
2. **Stacks** are collections of resources managed as a unit
3. **Change Sets** preview changes before applying them
4. **Drift Detection** identifies manual configuration changes
5. **Validation** catches errors before deployment

### Best Practices

- Always use change sets for production updates
- Run drift detection regularly
- Validate templates before deployment
- Use meaningful stack names and tags
- Store templates in version control

### Common Commands Cheat Sheet

```bash
# Validate
aws cloudformation validate-template --template-body file://t.yaml

# Create
aws cloudformation create-stack --stack-name X --template-body file://t.yaml

# Update with change set
aws cloudformation create-change-set --stack-name X --change-set-name C
aws cloudformation execute-change-set --stack-name X --change-set-name C

# Drift detection
aws cloudformation detect-stack-drift --stack-name X

# Delete
aws cloudformation delete-stack --stack-name X
```

---

## Knowledge Check

1. What is the difference between a template and a stack?
2. Why should you use change sets instead of direct updates?
3. What causes configuration drift?
4. What happens when stack creation fails?
5. What are the size limits for CloudFormation templates?

---

**Next:** [03 - Template Anatomy](./03-template-anatomy.md)

**Previous:** [01 - IaC Fundamentals](./01-iac-fundamentals.md)
