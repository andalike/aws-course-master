# Lesson 01: Infrastructure as Code Fundamentals

## Introduction

Infrastructure as Code (IaC) is the practice of managing and provisioning computing infrastructure through machine-readable configuration files rather than physical hardware configuration or interactive configuration tools. This lesson explores the foundational concepts that make IaC essential for modern cloud operations.

---

## Why Infrastructure as Code?

### The Evolution of Infrastructure Management

```
Era 1: Physical Servers (1990s-2000s)
├── Manual rack and stack
├── Weeks to provision
├── Hardware procurement
└── Limited scalability

Era 2: Virtualization (2000s-2010s)
├── VMs on hypervisors
├── Days to provision
├── Still manual configuration
└── Better resource utilization

Era 3: Cloud Computing (2010s)
├── On-demand resources
├── Minutes to provision
├── Console-based management
└── Scripting for automation

Era 4: Infrastructure as Code (2010s-Present)
├── Declarative definitions
├── Seconds to provision
├── Version-controlled infrastructure
└── Full automation and repeatability
```

### Problems with Manual Infrastructure Management

#### 1. Configuration Drift
```
Day 1: All servers configured identically
   │
   ├── Server A: Manual patch applied
   ├── Server B: Config change for testing
   └── Server C: Hotfix for production issue
   │
Day 30: All servers are different (DRIFT!)
```

**Real-world Example:**
```
Production Incident:
- Application worked in staging but failed in production
- Root cause: Production server had different library version
- Time to diagnose: 4 hours
- Cost: $50,000 in lost revenue
- Could have been prevented with IaC
```

#### 2. The "Snowflake Server" Problem

Each server becomes unique like a snowflake - irreplaceable and impossible to recreate:

| Characteristic | Snowflake Server | IaC-Managed Server |
|----------------|------------------|---------------------|
| Documentation | Tribal knowledge | Code is documentation |
| Reproducibility | Nearly impossible | 100% reproducible |
| Recovery Time | Hours to days | Minutes |
| Consistency | None guaranteed | Guaranteed |
| Audit Trail | Manual logs | Git history |

#### 3. Slow Provisioning

```
Traditional Approach:
┌─────────────────┐
│ Request Server  │ ──► 2 days
├─────────────────┤
│ Procurement     │ ──► 1 week (if hardware)
├─────────────────┤
│ OS Installation │ ──► 1 day
├─────────────────┤
│ Configuration   │ ──► 2 days
├─────────────────┤
│ Security Review │ ──► 3 days
├─────────────────┤
│ Testing         │ ──► 2 days
└─────────────────┘
Total: 2-3 weeks

IaC Approach:
┌─────────────────┐
│ Deploy Template │ ──► 15 minutes
└─────────────────┘
```

---

## Core Principles of IaC

### 1. Idempotency

Running the same code multiple times produces the same result:

```yaml
# Running this template 1 time or 100 times
# produces exactly the same infrastructure
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-idempotent-bucket

# First run: Creates bucket
# Second run: No changes (bucket exists)
# Third run: No changes (bucket exists)
```

### 2. Version Control

Infrastructure changes are tracked like application code:

```bash
# Track all infrastructure changes
git log --oneline templates/

a1b2c3d Add production VPC
e4f5g6h Update security groups
i7j8k9l Add RDS instance
m0n1o2p Fix CIDR overlap issue
```

### 3. Reproducibility

Same input always produces same output:

```
Template + Parameters = Consistent Infrastructure

├── Template: vpc-template.yaml
├── Parameters:
│   ├── Environment: production
│   ├── VPCCidr: 10.0.0.0/16
│   └── Region: us-east-1
│
└── Result: Identical VPC every time
```

### 4. Self-Documenting

The code describes the infrastructure:

```yaml
# This IS the documentation
Resources:
  # Web server auto scaling group with 2-10 instances
  WebServerASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: 2          # Always at least 2 instances
      MaxSize: 10         # Scale up to 10 instances
      DesiredCapacity: 2  # Start with 2 instances
      # ... more configuration
```

---

## Declarative vs Imperative IaC

### Understanding the Difference

```
IMPERATIVE (How to do it):
"Create a VPC. Then create a subnet.
Then create an internet gateway.
Then attach the gateway to the VPC.
Then create a route table..."

DECLARATIVE (What to achieve):
"I want a VPC with a public subnet
and internet access."
```

### Imperative Approach

**Definition:** You specify the exact steps to achieve the desired state.

**Example (Bash Script):**
```bash
#!/bin/bash
# Imperative: Step-by-step instructions

# Step 1: Create VPC
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
echo "Created VPC: $VPC_ID"

# Step 2: Create Subnet
SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --query 'Subnet.SubnetId' --output text)
echo "Created Subnet: $SUBNET_ID"

# Step 3: Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
echo "Created IGW: $IGW_ID"

# Step 4: Attach IGW to VPC
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

# Step 5: Create Route Table
RTB_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)

# Step 6: Create Route
aws ec2 create-route --route-table-id $RTB_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

# Step 7: Associate Route Table with Subnet
aws ec2 associate-route-table --route-table-id $RTB_ID --subnet-id $SUBNET_ID
```

**Problems with Imperative:**
- Must handle errors at each step
- Must handle resource already exists scenarios
- Order matters
- No automatic rollback
- Complex dependency management

### Declarative Approach

**Definition:** You specify the desired end state, and the tool figures out how to achieve it.

**Example (CloudFormation):**
```yaml
# Declarative: Describe desired state
AWSTemplateFormatVersion: '2010-09-09'
Description: VPC with public subnet

Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: MyVPC

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref MyVPC
      InternetGatewayId: !Ref InternetGateway

  RouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref MyVPC

  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref RouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref RouteTable
```

### Comparison Table

| Aspect | Imperative | Declarative |
|--------|-----------|-------------|
| **Focus** | How to do it | What to achieve |
| **Error Handling** | Manual at each step | Automatic rollback |
| **Idempotency** | Must implement | Built-in |
| **State Management** | Manual tracking | Automatic |
| **Learning Curve** | Lower initially | Higher initially |
| **Maintainability** | Harder over time | Easier over time |
| **Example Tools** | Bash, Ansible | CloudFormation, Terraform |

---

## AWS IaC Options

AWS provides multiple tools for Infrastructure as Code:

### 1. AWS CloudFormation

**The Native AWS IaC Service**

```yaml
# CloudFormation Template (YAML)
AWSTemplateFormatVersion: '2010-09-09'
Description: S3 Bucket with versioning

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      VersioningConfiguration:
        Status: Enabled
```

**Characteristics:**
- Native AWS service (no additional cost)
- Supports all AWS services
- YAML or JSON format
- Automatic rollback on failure
- Drift detection
- StackSets for multi-account/region

**Best For:**
- AWS-only environments
- Teams preferring native services
- Tight AWS service integration

### 2. AWS Cloud Development Kit (CDK)

**Infrastructure in Programming Languages**

```typescript
// CDK in TypeScript
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';

export class MyStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string) {
    super(scope, id);

    new s3.Bucket(this, 'MyBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
  }
}
```

```python
# CDK in Python
from aws_cdk import Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct

class MyStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        s3.Bucket(self, "MyBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )
```

**Characteristics:**
- Write infrastructure in TypeScript, Python, Java, C#, Go
- Generates CloudFormation under the hood
- High-level abstractions (Constructs)
- IDE support (autocomplete, type checking)
- Reusable patterns

**Best For:**
- Developer-heavy teams
- Complex logic in infrastructure
- Reusable infrastructure libraries

### 3. AWS Serverless Application Model (SAM)

**Simplified Serverless IaC**

```yaml
# SAM Template
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Simple Lambda API

Resources:
  HelloFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      Events:
        Api:
          Type: Api
          Properties:
            Path: /hello
            Method: GET
```

**Characteristics:**
- Extension of CloudFormation
- Simplified syntax for serverless
- Local testing with SAM CLI
- Built-in best practices

**Best For:**
- Serverless applications
- Lambda, API Gateway, DynamoDB
- Rapid serverless development

### 4. Terraform (HashiCorp)

**Multi-Cloud IaC**

```hcl
# Terraform Configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-terraform-bucket"
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.my_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

**Characteristics:**
- Multi-cloud support (AWS, Azure, GCP, etc.)
- HCL (HashiCorp Configuration Language)
- State file management
- Large provider ecosystem
- Open source (with enterprise version)

**Best For:**
- Multi-cloud environments
- Existing Terraform expertise
- Non-AWS resources

### Comparison Matrix

```
                    ┌─────────────────────────────────────────────────────┐
                    │              AWS IaC Tools Comparison               │
                    ├──────────────┬──────────┬──────────┬───────────────┤
                    │CloudFormation│   CDK    │   SAM    │   Terraform   │
┌───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ Language          │ YAML/JSON    │ TS/Py/   │ YAML     │ HCL           │
│                   │              │ Java/C#  │          │               │
├───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ Learning Curve    │ Medium       │ Medium   │ Low      │ Medium        │
├───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ AWS Integration   │ Native       │ Native   │ Native   │ Provider      │
├───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ Multi-Cloud       │ No           │ No       │ No       │ Yes           │
├───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ State Management  │ AWS Managed  │ AWS      │ AWS      │ Self-Managed  │
├───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ Drift Detection   │ Yes          │ Yes      │ Yes      │ Yes           │
├───────────────────┼──────────────┼──────────┼──────────┼───────────────┤
│ Cost              │ Free         │ Free     │ Free     │ Free/Paid     │
└───────────────────┴──────────────┴──────────┴──────────┴───────────────┘
```

---

## IaC Workflow

### Standard IaC Development Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      IaC Development Workflow                    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │  Write  │          │  Test   │          │ Review  │
   │ Template│   ───►   │  Local  │   ───►   │  Code   │
   └─────────┘          └─────────┘          └─────────┘
                              │
                              ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │ Deploy  │          │  Test   │          │ Promote │
   │  to Dev │   ───►   │   Dev   │   ───►   │ Staging │
   └─────────┘          └─────────┘          └─────────┘
                              │
                              ▼
                        ┌─────────┐
                        │ Deploy  │
                        │  Prod   │
                        └─────────┘
```

### Detailed Steps

```bash
# Step 1: Write Template
vim templates/my-infrastructure.yaml

# Step 2: Validate Template
aws cloudformation validate-template \
    --template-body file://templates/my-infrastructure.yaml

# Step 3: Lint Template
cfn-lint templates/my-infrastructure.yaml

# Step 4: Create Change Set (Preview)
aws cloudformation create-change-set \
    --stack-name my-stack \
    --template-body file://templates/my-infrastructure.yaml \
    --change-set-name my-changes

# Step 5: Review Changes
aws cloudformation describe-change-set \
    --stack-name my-stack \
    --change-set-name my-changes

# Step 6: Execute Change Set
aws cloudformation execute-change-set \
    --stack-name my-stack \
    --change-set-name my-changes

# Step 7: Monitor Deployment
aws cloudformation describe-stack-events \
    --stack-name my-stack

# Step 8: Verify Resources
aws cloudformation describe-stacks \
    --stack-name my-stack
```

---

## IaC Best Practices

### 1. Version Control Everything

```bash
# Initialize Git repository for templates
git init infrastructure/

# Create .gitignore
cat > .gitignore << EOF
*.bak
.aws-sam/
cdk.out/
.terraform/
*.tfstate
*.tfstate.backup
EOF

# Commit templates
git add templates/
git commit -m "Add initial CloudFormation templates"
```

### 2. Use Consistent Naming Conventions

```yaml
# Good: Consistent naming
Resources:
  ProductionVPC:
    Type: AWS::EC2::VPC
  ProductionPublicSubnet1:
    Type: AWS::EC2::Subnet
  ProductionPrivateSubnet1:
    Type: AWS::EC2::Subnet
  ProductionWebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
```

### 3. Parameterize Everything

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
  InstanceType:
    Type: String
    Default: t3.micro
  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
```

### 4. Tag All Resources

```yaml
Resources:
  MyResource:
    Type: AWS::EC2::Instance
    Properties:
      Tags:
        - Key: Environment
          Value: !Ref Environment
        - Key: Project
          Value: !Ref ProjectName
        - Key: Owner
          Value: !Ref OwnerEmail
        - Key: CostCenter
          Value: !Ref CostCenter
```

### 5. Implement Least Privilege

```yaml
# Good: Specific permissions
Resources:
  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      Policies:
        - PolicyName: S3ReadOnly
          PolicyDocument:
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !GetAtt MyBucket.Arn
                  - !Sub '${MyBucket.Arn}/*'
```

---

## Common IaC Anti-Patterns

### 1. Hardcoding Values

```yaml
# BAD: Hardcoded values
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.large  # Should be a parameter
      ImageId: ami-12345678   # Should use SSM parameter

# GOOD: Parameterized
Parameters:
  InstanceType:
    Type: String
    Default: t3.micro
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !Ref LatestAmiId
```

### 2. Monolithic Templates

```yaml
# BAD: 5000+ line template with everything
# - VPC, Subnets, EC2, RDS, Lambda, S3, etc. all in one file

# GOOD: Nested stacks
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.../network.yaml

  ComputeStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.../compute.yaml
      Parameters:
        VPCId: !GetAtt NetworkStack.Outputs.VPCId
```

### 3. No Change Management

```bash
# BAD: Direct updates
aws cloudformation update-stack --stack-name prod-stack ...

# GOOD: Use change sets
aws cloudformation create-change-set \
    --stack-name prod-stack \
    --change-set-name review-changes \
    --template-body file://template.yaml

# Review the changes before applying
aws cloudformation describe-change-set \
    --stack-name prod-stack \
    --change-set-name review-changes
```

---

## Summary

### Key Takeaways

1. **IaC is Essential** - Modern cloud infrastructure demands automation and reproducibility

2. **Declarative is Preferred** - Focus on what you want, not how to get there

3. **CloudFormation is Native** - No additional cost, tight AWS integration

4. **Choose the Right Tool** - CloudFormation for AWS-only, Terraform for multi-cloud, CDK for developers

5. **Version Control** - Treat infrastructure code like application code

6. **Test Before Deploy** - Use change sets and dev environments

### Decision Framework

```
Need multi-cloud?
├── Yes ──► Terraform
└── No
    ├── Need programming languages?
    │   ├── Yes ──► CDK
    │   └── No
    │       ├── Building serverless?
    │       │   ├── Yes ──► SAM
    │       │   └── No ──► CloudFormation
    │       └── Need simple YAML/JSON?
    │           └── Yes ──► CloudFormation
```

---

## Knowledge Check

1. What is the main difference between declarative and imperative IaC?
2. Name three benefits of Infrastructure as Code
3. When would you choose Terraform over CloudFormation?
4. What is idempotency and why is it important?
5. What is configuration drift?

---

## Next Steps

In the next lesson, we'll dive deep into CloudFormation basics, covering:
- Templates and stacks
- Stack lifecycle
- Change sets
- Drift detection

---

**Next:** [02 - CloudFormation Basics](./02-cloudformation-basics.md)

**Previous:** [README](./README.md)
