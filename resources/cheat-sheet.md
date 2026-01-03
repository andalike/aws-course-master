# AWS CLI Cheat Sheet

A comprehensive reference for commonly used AWS CLI commands organized by service.

---

## Table of Contents

1. [AWS CLI Configuration](#aws-cli-configuration)
2. [IAM Commands](#iam-commands)
3. [EC2 Commands](#ec2-commands)
4. [S3 Commands](#s3-commands)
5. [VPC Commands](#vpc-commands)
6. [RDS Commands](#rds-commands)
7. [Lambda Commands](#lambda-commands)
8. [CloudWatch Commands](#cloudwatch-commands)
9. [CloudFormation Commands](#cloudformation-commands)

---

## AWS CLI Configuration

```bash
# Configure default profile
aws configure

# Configure named profile
aws configure --profile production

# List all profiles
aws configure list-profiles

# Set default region
aws configure set region us-east-1

# Set default output format
aws configure set output json

# Get caller identity (who am I)
aws sts get-caller-identity

# Assume a role
aws sts assume-role \
    --role-arn arn:aws:iam::123456789012:role/RoleName \
    --role-session-name session-name
```

---

## IAM Commands

### Users

```bash
# List users
aws iam list-users

# Create user
aws iam create-user --user-name john

# Delete user
aws iam delete-user --user-name john

# Get user details
aws iam get-user --user-name john

# Add user to group
aws iam add-user-to-group --user-name john --group-name developers

# Create access keys
aws iam create-access-key --user-name john

# List access keys
aws iam list-access-keys --user-name john

# Delete access key
aws iam delete-access-key --user-name john --access-key-id AKIAXXXXXXXX
```

### Groups

```bash
# List groups
aws iam list-groups

# Create group
aws iam create-group --group-name developers

# Delete group
aws iam delete-group --group-name developers

# List group members
aws iam get-group --group-name developers
```

### Roles

```bash
# List roles
aws iam list-roles

# Create role
aws iam create-role \
    --role-name MyRole \
    --assume-role-policy-document file://trust-policy.json

# Attach policy to role
aws iam attach-role-policy \
    --role-name MyRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# List attached policies
aws iam list-attached-role-policies --role-name MyRole
```

### Policies

```bash
# List policies
aws iam list-policies --scope Local

# Create policy
aws iam create-policy \
    --policy-name MyPolicy \
    --policy-document file://policy.json

# Get policy document
aws iam get-policy-version \
    --policy-arn arn:aws:iam::123456789012:policy/MyPolicy \
    --version-id v1
```

---

## EC2 Commands

### Instances

```bash
# List all instances
aws ec2 describe-instances

# List running instances
aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].{ID:InstanceId,Type:InstanceType,State:State.Name,IP:PublicIpAddress}'

# Launch instance
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --instance-type t2.micro \
    --key-name MyKeyPair \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --count 1

# Start instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0

# Stop instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Terminate instance
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

# Reboot instance
aws ec2 reboot-instances --instance-ids i-1234567890abcdef0
```

### AMIs

```bash
# List AMIs
aws ec2 describe-images --owners self

# Create AMI from instance
aws ec2 create-image \
    --instance-id i-1234567890abcdef0 \
    --name "My-AMI" \
    --description "My custom AMI"

# Delete AMI
aws ec2 deregister-image --image-id ami-12345678
```

### Security Groups

```bash
# List security groups
aws ec2 describe-security-groups

# Create security group
aws ec2 create-security-group \
    --group-name my-sg \
    --description "My security group" \
    --vpc-id vpc-12345678

# Add inbound rule
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Remove inbound rule
aws ec2 revoke-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Delete security group
aws ec2 delete-security-group --group-id sg-12345678
```

### Key Pairs

```bash
# List key pairs
aws ec2 describe-key-pairs

# Create key pair
aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem

# Delete key pair
aws ec2 delete-key-pair --key-name MyKeyPair
```

### EBS Volumes

```bash
# List volumes
aws ec2 describe-volumes

# Create volume
aws ec2 create-volume \
    --size 100 \
    --volume-type gp3 \
    --availability-zone us-east-1a

# Attach volume
aws ec2 attach-volume \
    --volume-id vol-12345678 \
    --instance-id i-1234567890abcdef0 \
    --device /dev/sdf

# Create snapshot
aws ec2 create-snapshot \
    --volume-id vol-12345678 \
    --description "My snapshot"
```

---

## S3 Commands

### Buckets

```bash
# List buckets
aws s3 ls

# Create bucket
aws s3 mb s3://my-bucket-name

# Delete bucket
aws s3 rb s3://my-bucket-name

# Delete bucket with contents
aws s3 rb s3://my-bucket-name --force
```

### Objects

```bash
# List objects
aws s3 ls s3://my-bucket/

# List objects recursively
aws s3 ls s3://my-bucket/ --recursive

# Upload file
aws s3 cp file.txt s3://my-bucket/

# Download file
aws s3 cp s3://my-bucket/file.txt ./

# Sync directory
aws s3 sync ./local-folder s3://my-bucket/folder/

# Delete object
aws s3 rm s3://my-bucket/file.txt

# Delete all objects in bucket
aws s3 rm s3://my-bucket/ --recursive

# Copy between buckets
aws s3 cp s3://bucket1/file.txt s3://bucket2/file.txt

# Move object
aws s3 mv s3://my-bucket/old-name.txt s3://my-bucket/new-name.txt
```

### Advanced S3 Commands

```bash
# Enable versioning
aws s3api put-bucket-versioning \
    --bucket my-bucket \
    --versioning-configuration Status=Enabled

# Get bucket policy
aws s3api get-bucket-policy --bucket my-bucket

# Put bucket policy
aws s3api put-bucket-policy \
    --bucket my-bucket \
    --policy file://policy.json

# Generate presigned URL
aws s3 presign s3://my-bucket/file.txt --expires-in 3600

# Set object public
aws s3api put-object-acl \
    --bucket my-bucket \
    --key file.txt \
    --acl public-read
```

---

## VPC Commands

### VPCs

```bash
# List VPCs
aws ec2 describe-vpcs

# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Delete VPC
aws ec2 delete-vpc --vpc-id vpc-12345678

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id vpc-12345678 \
    --enable-dns-hostnames
```

### Subnets

```bash
# List subnets
aws ec2 describe-subnets

# Create subnet
aws ec2 create-subnet \
    --vpc-id vpc-12345678 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone us-east-1a

# Delete subnet
aws ec2 delete-subnet --subnet-id subnet-12345678
```

### Internet Gateway

```bash
# Create IGW
aws ec2 create-internet-gateway

# Attach IGW to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id igw-12345678 \
    --vpc-id vpc-12345678

# Detach IGW
aws ec2 detach-internet-gateway \
    --internet-gateway-id igw-12345678 \
    --vpc-id vpc-12345678
```

### Route Tables

```bash
# List route tables
aws ec2 describe-route-tables

# Create route table
aws ec2 create-route-table --vpc-id vpc-12345678

# Create route
aws ec2 create-route \
    --route-table-id rtb-12345678 \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-12345678

# Associate with subnet
aws ec2 associate-route-table \
    --route-table-id rtb-12345678 \
    --subnet-id subnet-12345678
```

---

## RDS Commands

```bash
# List DB instances
aws rds describe-db-instances

# Create DB instance
aws rds create-db-instance \
    --db-instance-identifier mydb \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --master-user-password password123 \
    --allocated-storage 20

# Start DB instance
aws rds start-db-instance --db-instance-identifier mydb

# Stop DB instance
aws rds stop-db-instance --db-instance-identifier mydb

# Delete DB instance
aws rds delete-db-instance \
    --db-instance-identifier mydb \
    --skip-final-snapshot

# Create snapshot
aws rds create-db-snapshot \
    --db-instance-identifier mydb \
    --db-snapshot-identifier my-snapshot

# List snapshots
aws rds describe-db-snapshots

# Modify instance
aws rds modify-db-instance \
    --db-instance-identifier mydb \
    --db-instance-class db.t3.small \
    --apply-immediately
```

---

## Lambda Commands

```bash
# List functions
aws lambda list-functions

# Create function
aws lambda create-function \
    --function-name my-function \
    --runtime python3.9 \
    --role arn:aws:iam::123456789012:role/lambda-role \
    --handler lambda_function.handler \
    --zip-file fileb://function.zip

# Invoke function
aws lambda invoke \
    --function-name my-function \
    --payload '{"key": "value"}' \
    output.json

# Update function code
aws lambda update-function-code \
    --function-name my-function \
    --zip-file fileb://function.zip

# Update function configuration
aws lambda update-function-configuration \
    --function-name my-function \
    --memory-size 512 \
    --timeout 30

# Delete function
aws lambda delete-function --function-name my-function

# Get function logs
aws logs tail /aws/lambda/my-function --follow
```

---

## CloudWatch Commands

### Metrics

```bash
# List metrics
aws cloudwatch list-metrics --namespace AWS/EC2

# Get metric statistics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average

# Put custom metric
aws cloudwatch put-metric-data \
    --namespace MyApp \
    --metric-name PageViews \
    --value 100
```

### Alarms

```bash
# List alarms
aws cloudwatch describe-alarms

# Create alarm
aws cloudwatch put-metric-alarm \
    --alarm-name cpu-high \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:my-topic \
    --dimensions Name=InstanceId,Value=i-1234567890abcdef0

# Delete alarm
aws cloudwatch delete-alarms --alarm-names cpu-high
```

### Logs

```bash
# List log groups
aws logs describe-log-groups

# List log streams
aws logs describe-log-streams --log-group-name /aws/lambda/my-function

# Get log events
aws logs get-log-events \
    --log-group-name /aws/lambda/my-function \
    --log-stream-name stream-name

# Create log group
aws logs create-log-group --log-group-name my-log-group

# Set retention
aws logs put-retention-policy \
    --log-group-name my-log-group \
    --retention-in-days 30

# Delete log group
aws logs delete-log-group --log-group-name my-log-group
```

---

## CloudFormation Commands

```bash
# List stacks
aws cloudformation list-stacks

# Create stack
aws cloudformation create-stack \
    --stack-name my-stack \
    --template-body file://template.yaml \
    --parameters ParameterKey=Env,ParameterValue=dev \
    --capabilities CAPABILITY_IAM

# Update stack
aws cloudformation update-stack \
    --stack-name my-stack \
    --template-body file://template.yaml

# Delete stack
aws cloudformation delete-stack --stack-name my-stack

# Describe stack
aws cloudformation describe-stacks --stack-name my-stack

# List stack events
aws cloudformation describe-stack-events --stack-name my-stack

# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Create change set
aws cloudformation create-change-set \
    --stack-name my-stack \
    --change-set-name my-changes \
    --template-body file://template.yaml

# Execute change set
aws cloudformation execute-change-set \
    --stack-name my-stack \
    --change-set-name my-changes
```

---

## Pro Tips

### Output Formatting

```bash
# JSON output
aws ec2 describe-instances --output json

# Table output
aws ec2 describe-instances --output table

# Text output
aws ec2 describe-instances --output text

# JMESPath queries
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId'
```

### Environment Variables

```bash
# Set credentials
export AWS_ACCESS_KEY_ID=AKIAXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXX
export AWS_DEFAULT_REGION=us-east-1

# Use profile
export AWS_PROFILE=production
```

### Pagination

```bash
# Get all results (handles pagination)
aws s3api list-objects-v2 --bucket my-bucket --no-paginate

# Get specific page
aws s3api list-objects-v2 --bucket my-bucket --max-items 100 --starting-token TOKEN
```

---

*Keep this cheat sheet handy for quick reference!*
