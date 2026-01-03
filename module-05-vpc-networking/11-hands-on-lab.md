# 11 - Hands-On VPC Networking Lab

## Lab Overview

In this comprehensive lab, you will build a production-ready VPC architecture from scratch. This lab covers all major VPC components and provides hands-on experience with real-world networking scenarios.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        LAB ARCHITECTURE OVERVIEW                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                              INTERNET                                            │
│                                  │                                               │
│                    ┌─────────────▼─────────────┐                                │
│                    │     Internet Gateway       │                                │
│                    └─────────────┬─────────────┘                                │
│                                  │                                               │
│   ┌──────────────────────────────┴───────────────────────────────────────────┐  │
│   │                      VPC-A (Production): 10.0.0.0/16                      │  │
│   │                                                                           │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│   │   │                    Public Subnet: 10.0.1.0/24                    │    │  │
│   │   │   ┌─────────────┐        ┌─────────────┐       ┌─────────────┐  │    │  │
│   │   │   │   Bastion   │        │     ALB     │       │ NAT Gateway │  │    │  │
│   │   │   │    Host     │        │             │       │             │  │    │  │
│   │   │   └─────────────┘        └─────────────┘       └──────┬──────┘  │    │  │
│   │   │                                                        │         │    │  │
│   │   └────────────────────────────────────────────────────────┼─────────┘    │  │
│   │                                                            │              │  │
│   │   ┌────────────────────────────────────────────────────────┼─────────┐    │  │
│   │   │                    Private Subnet: 10.0.2.0/24         │         │    │  │
│   │   │   ┌─────────────┐        ┌─────────────┐              │         │    │  │
│   │   │   │   App EC2   │        │   App EC2   │◄─────────────┘         │    │  │
│   │   │   │   Server    │        │   Server    │                        │    │  │
│   │   │   └──────┬──────┘        └──────┬──────┘                        │    │  │
│   │   │          │                      │                               │    │  │
│   │   └──────────┼──────────────────────┼───────────────────────────────┘    │  │
│   │              │                      │                                    │  │
│   │   ┌──────────▼──────────────────────▼───────────────────────────────┐    │  │
│   │   │                    Data Subnet: 10.0.3.0/24                      │    │  │
│   │   │   ┌─────────────┐        ┌─────────────┐                        │    │  │
│   │   │   │  RDS MySQL  │        │ ElastiCache │                        │    │  │
│   │   │   │  Primary    │        │   Redis     │                        │    │  │
│   │   │   └─────────────┘        └─────────────┘                        │    │  │
│   │   └─────────────────────────────────────────────────────────────────┘    │  │
│   │                                                                           │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│   │   │ VPC Endpoint: S3 Gateway                                         │    │  │
│   │   └─────────────────────────────────────────────────────────────────┘    │  │
│   │                                                                           │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                  │                                               │
│                                  │ VPC Peering                                   │
│                                  │                                               │
│   ┌──────────────────────────────▼───────────────────────────────────────────┐  │
│   │                      VPC-B (Development): 10.1.0.0/16                     │  │
│   │                                                                           │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│   │   │                    Private Subnet: 10.1.1.0/24                   │    │  │
│   │   │   ┌─────────────┐        ┌─────────────┐                        │    │  │
│   │   │   │   Dev EC2   │        │   Dev EC2   │                        │    │  │
│   │   │   │   Server    │        │   Server    │                        │    │  │
│   │   │   └─────────────┘        └─────────────┘                        │    │  │
│   │   └─────────────────────────────────────────────────────────────────┘    │  │
│   │                                                                           │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- AWS Account with administrator access
- AWS CLI configured with appropriate credentials
- Basic understanding of networking concepts
- SSH key pair created in your AWS region

## Lab Duration

**Estimated Time:** 2-3 hours

---

## Part 1: Create the Production VPC

### Step 1.1: Create VPC

```bash
# Create VPC
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=Production-VPC}]' \
    --instance-tenancy default

# Save the VPC ID
VPC_PROD_ID=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=Production-VPC" \
    --query 'Vpcs[0].VpcId' --output text)

echo "Production VPC ID: $VPC_PROD_ID"

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_PROD_ID \
    --enable-dns-hostnames '{"Value":true}'

# Enable DNS support
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_PROD_ID \
    --enable-dns-support '{"Value":true}'
```

### Step 1.2: Create Internet Gateway

```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
    --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=Production-IGW}]'

# Get IGW ID
IGW_ID=$(aws ec2 describe-internet-gateways \
    --filters "Name=tag:Name,Values=Production-IGW" \
    --query 'InternetGateways[0].InternetGatewayId' --output text)

echo "Internet Gateway ID: $IGW_ID"

# Attach IGW to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_PROD_ID
```

### Step 1.3: Create Subnets

```bash
# Get Available AZs
AZ1=$(aws ec2 describe-availability-zones \
    --query 'AvailabilityZones[0].ZoneName' --output text)
AZ2=$(aws ec2 describe-availability-zones \
    --query 'AvailabilityZones[1].ZoneName' --output text)

echo "Using AZs: $AZ1 and $AZ2"

# Create Public Subnet in AZ1
aws ec2 create-subnet \
    --vpc-id $VPC_PROD_ID \
    --cidr-block 10.0.1.0/24 \
    --availability-zone $AZ1 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Production-Public-Subnet-1}]'

PUBLIC_SUBNET_1=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Production-Public-Subnet-1" \
    --query 'Subnets[0].SubnetId' --output text)

# Create Public Subnet in AZ2
aws ec2 create-subnet \
    --vpc-id $VPC_PROD_ID \
    --cidr-block 10.0.4.0/24 \
    --availability-zone $AZ2 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Production-Public-Subnet-2}]'

PUBLIC_SUBNET_2=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Production-Public-Subnet-2" \
    --query 'Subnets[0].SubnetId' --output text)

# Create Private Subnet (App Tier) in AZ1
aws ec2 create-subnet \
    --vpc-id $VPC_PROD_ID \
    --cidr-block 10.0.2.0/24 \
    --availability-zone $AZ1 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Production-Private-App-Subnet-1}]'

PRIVATE_APP_SUBNET_1=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Production-Private-App-Subnet-1" \
    --query 'Subnets[0].SubnetId' --output text)

# Create Private Subnet (App Tier) in AZ2
aws ec2 create-subnet \
    --vpc-id $VPC_PROD_ID \
    --cidr-block 10.0.5.0/24 \
    --availability-zone $AZ2 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Production-Private-App-Subnet-2}]'

PRIVATE_APP_SUBNET_2=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Production-Private-App-Subnet-2" \
    --query 'Subnets[0].SubnetId' --output text)

# Create Private Subnet (Data Tier) in AZ1
aws ec2 create-subnet \
    --vpc-id $VPC_PROD_ID \
    --cidr-block 10.0.3.0/24 \
    --availability-zone $AZ1 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Production-Private-Data-Subnet-1}]'

DATA_SUBNET_1=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Production-Private-Data-Subnet-1" \
    --query 'Subnets[0].SubnetId' --output text)

# Create Private Subnet (Data Tier) in AZ2
aws ec2 create-subnet \
    --vpc-id $VPC_PROD_ID \
    --cidr-block 10.0.6.0/24 \
    --availability-zone $AZ2 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Production-Private-Data-Subnet-2}]'

DATA_SUBNET_2=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Production-Private-Data-Subnet-2" \
    --query 'Subnets[0].SubnetId' --output text)

# Enable auto-assign public IP for public subnets
aws ec2 modify-subnet-attribute \
    --subnet-id $PUBLIC_SUBNET_1 \
    --map-public-ip-on-launch

aws ec2 modify-subnet-attribute \
    --subnet-id $PUBLIC_SUBNET_2 \
    --map-public-ip-on-launch

echo "Subnets created:"
echo "Public Subnet 1: $PUBLIC_SUBNET_1"
echo "Public Subnet 2: $PUBLIC_SUBNET_2"
echo "Private App Subnet 1: $PRIVATE_APP_SUBNET_1"
echo "Private App Subnet 2: $PRIVATE_APP_SUBNET_2"
echo "Data Subnet 1: $DATA_SUBNET_1"
echo "Data Subnet 2: $DATA_SUBNET_2"
```

### Subnet Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION VPC SUBNET LAYOUT                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   VPC: 10.0.0.0/16 (65,536 IPs)                                                │
│                                                                                  │
│   ┌───────────────────────────────────┬───────────────────────────────────┐     │
│   │       Availability Zone 1         │       Availability Zone 2         │     │
│   │                                   │                                   │     │
│   │  ┌─────────────────────────────┐  │  ┌─────────────────────────────┐  │     │
│   │  │ PUBLIC SUBNET               │  │  │ PUBLIC SUBNET               │  │     │
│   │  │ 10.0.1.0/24 (251 IPs)       │  │  │ 10.0.4.0/24 (251 IPs)       │  │     │
│   │  │                             │  │  │                             │  │     │
│   │  │ • Bastion Host              │  │  │ • ALB                       │  │     │
│   │  │ • NAT Gateway               │  │  │ • NAT Gateway (optional)    │  │     │
│   │  │ • ALB                       │  │  │                             │  │     │
│   │  └─────────────────────────────┘  │  └─────────────────────────────┘  │     │
│   │                                   │                                   │     │
│   │  ┌─────────────────────────────┐  │  ┌─────────────────────────────┐  │     │
│   │  │ PRIVATE SUBNET (App)        │  │  │ PRIVATE SUBNET (App)        │  │     │
│   │  │ 10.0.2.0/24 (251 IPs)       │  │  │ 10.0.5.0/24 (251 IPs)       │  │     │
│   │  │                             │  │  │                             │  │     │
│   │  │ • Application Servers       │  │  │ • Application Servers       │  │     │
│   │  │ • Container Hosts           │  │  │ • Container Hosts           │  │     │
│   │  └─────────────────────────────┘  │  └─────────────────────────────┘  │     │
│   │                                   │                                   │     │
│   │  ┌─────────────────────────────┐  │  ┌─────────────────────────────┐  │     │
│   │  │ PRIVATE SUBNET (Data)       │  │  │ PRIVATE SUBNET (Data)       │  │     │
│   │  │ 10.0.3.0/24 (251 IPs)       │  │  │ 10.0.6.0/24 (251 IPs)       │  │     │
│   │  │                             │  │  │                             │  │     │
│   │  │ • RDS Primary               │  │  │ • RDS Standby               │  │     │
│   │  │ • ElastiCache               │  │  │ • ElastiCache Replica       │  │     │
│   │  └─────────────────────────────┘  │  └─────────────────────────────┘  │     │
│   │                                   │                                   │     │
│   └───────────────────────────────────┴───────────────────────────────────┘     │
│                                                                                  │
│   IP Allocation Summary:                                                        │
│   • Public: 502 IPs (10.0.1.0/24 + 10.0.4.0/24)                                │
│   • App: 502 IPs (10.0.2.0/24 + 10.0.5.0/24)                                   │
│   • Data: 502 IPs (10.0.3.0/24 + 10.0.6.0/24)                                  │
│   • Reserved: 10.0.7.0/24 - 10.0.255.0/24 (future use)                         │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Set Up NAT Gateway

### Step 2.1: Create Elastic IP for NAT Gateway

```bash
# Allocate Elastic IP
aws ec2 allocate-address \
    --domain vpc \
    --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=NAT-Gateway-EIP}]'

NAT_EIP_ALLOC=$(aws ec2 describe-addresses \
    --filters "Name=tag:Name,Values=NAT-Gateway-EIP" \
    --query 'Addresses[0].AllocationId' --output text)

echo "Elastic IP Allocation ID: $NAT_EIP_ALLOC"
```

### Step 2.2: Create NAT Gateway

```bash
# Create NAT Gateway in Public Subnet 1
aws ec2 create-nat-gateway \
    --subnet-id $PUBLIC_SUBNET_1 \
    --allocation-id $NAT_EIP_ALLOC \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=Production-NAT-Gateway}]'

# Wait for NAT Gateway to become available (takes 1-2 minutes)
echo "Waiting for NAT Gateway to become available..."
aws ec2 wait nat-gateway-available \
    --filter "Name=tag:Name,Values=Production-NAT-Gateway"

NAT_GW_ID=$(aws ec2 describe-nat-gateways \
    --filter "Name=tag:Name,Values=Production-NAT-Gateway" \
    --query 'NatGateways[0].NatGatewayId' --output text)

echo "NAT Gateway ID: $NAT_GW_ID"
```

### Step 2.3: Create Route Tables

```bash
# Create Public Route Table
aws ec2 create-route-table \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Production-Public-RT}]'

PUBLIC_RT=$(aws ec2 describe-route-tables \
    --filters "Name=tag:Name,Values=Production-Public-RT" \
    --query 'RouteTables[0].RouteTableId' --output text)

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $PUBLIC_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

# Associate Public Subnets with Public Route Table
aws ec2 associate-route-table \
    --subnet-id $PUBLIC_SUBNET_1 \
    --route-table-id $PUBLIC_RT

aws ec2 associate-route-table \
    --subnet-id $PUBLIC_SUBNET_2 \
    --route-table-id $PUBLIC_RT

# Create Private Route Table
aws ec2 create-route-table \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Production-Private-RT}]'

PRIVATE_RT=$(aws ec2 describe-route-tables \
    --filters "Name=tag:Name,Values=Production-Private-RT" \
    --query 'RouteTables[0].RouteTableId' --output text)

# Add route to NAT Gateway
aws ec2 create-route \
    --route-table-id $PRIVATE_RT \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id $NAT_GW_ID

# Associate Private Subnets with Private Route Table
aws ec2 associate-route-table \
    --subnet-id $PRIVATE_APP_SUBNET_1 \
    --route-table-id $PRIVATE_RT

aws ec2 associate-route-table \
    --subnet-id $PRIVATE_APP_SUBNET_2 \
    --route-table-id $PRIVATE_RT

aws ec2 associate-route-table \
    --subnet-id $DATA_SUBNET_1 \
    --route-table-id $PRIVATE_RT

aws ec2 associate-route-table \
    --subnet-id $DATA_SUBNET_2 \
    --route-table-id $PRIVATE_RT

echo "Route Tables created and associated"
echo "Public RT: $PUBLIC_RT"
echo "Private RT: $PRIVATE_RT"
```

### Route Table Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ROUTE TABLE CONFIGURATION                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   PUBLIC ROUTE TABLE (Production-Public-RT)                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ Destination         │ Target              │ Status                      │   │
│   ├─────────────────────────────────────────────────────────────────────────┤   │
│   │ 10.0.0.0/16         │ local               │ Active (VPC local traffic) │   │
│   │ 0.0.0.0/0           │ igw-xxxxx           │ Active (Internet access)   │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Associated Subnets:                                                           │
│   • Production-Public-Subnet-1 (10.0.1.0/24)                                   │
│   • Production-Public-Subnet-2 (10.0.4.0/24)                                   │
│                                                                                  │
│   ─────────────────────────────────────────────────────────────────────────     │
│                                                                                  │
│   PRIVATE ROUTE TABLE (Production-Private-RT)                                   │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │ Destination         │ Target              │ Status                      │   │
│   ├─────────────────────────────────────────────────────────────────────────┤   │
│   │ 10.0.0.0/16         │ local               │ Active (VPC local traffic) │   │
│   │ 0.0.0.0/0           │ nat-xxxxx           │ Active (Outbound via NAT)  │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Associated Subnets:                                                           │
│   • Production-Private-App-Subnet-1 (10.0.2.0/24)                              │
│   • Production-Private-App-Subnet-2 (10.0.5.0/24)                              │
│   • Production-Private-Data-Subnet-1 (10.0.3.0/24)                             │
│   • Production-Private-Data-Subnet-2 (10.0.6.0/24)                             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: Configure Security Groups

### Step 3.1: Create Security Groups

```bash
# Bastion Host Security Group
aws ec2 create-security-group \
    --group-name Bastion-SG \
    --description "Security group for Bastion host" \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=Bastion-SG}]'

BASTION_SG=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=Bastion-SG" \
    --query 'SecurityGroups[0].GroupId' --output text)

# Allow SSH from your IP (replace with your IP)
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-id $BASTION_SG \
    --protocol tcp \
    --port 22 \
    --cidr $MY_IP/32

# ALB Security Group
aws ec2 create-security-group \
    --group-name ALB-SG \
    --description "Security group for Application Load Balancer" \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=ALB-SG}]'

ALB_SG=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=ALB-SG" \
    --query 'SecurityGroups[0].GroupId' --output text)

# Allow HTTP and HTTPS from internet
aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id $ALB_SG \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# App Server Security Group
aws ec2 create-security-group \
    --group-name App-SG \
    --description "Security group for Application servers" \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=App-SG}]'

APP_SG=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=App-SG" \
    --query 'SecurityGroups[0].GroupId' --output text)

# Allow traffic from ALB on port 80
aws ec2 authorize-security-group-ingress \
    --group-id $APP_SG \
    --protocol tcp \
    --port 80 \
    --source-group $ALB_SG

# Allow SSH from Bastion
aws ec2 authorize-security-group-ingress \
    --group-id $APP_SG \
    --protocol tcp \
    --port 22 \
    --source-group $BASTION_SG

# Database Security Group
aws ec2 create-security-group \
    --group-name DB-SG \
    --description "Security group for Database servers" \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=DB-SG}]'

DB_SG=$(aws ec2 describe-security-groups \
    --filters "Name=tag:Name,Values=DB-SG" \
    --query 'SecurityGroups[0].GroupId' --output text)

# Allow MySQL from App servers
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG \
    --protocol tcp \
    --port 3306 \
    --source-group $APP_SG

# Allow Redis from App servers
aws ec2 authorize-security-group-ingress \
    --group-id $DB_SG \
    --protocol tcp \
    --port 6379 \
    --source-group $APP_SG

echo "Security Groups created:"
echo "Bastion SG: $BASTION_SG"
echo "ALB SG: $ALB_SG"
echo "App SG: $APP_SG"
echo "DB SG: $DB_SG"
```

### Security Group Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        SECURITY GROUP ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   INTERNET                                                                      │
│       │                                                                          │
│       │ Your IP (SSH)              HTTP/HTTPS (0.0.0.0/0)                       │
│       │                                    │                                     │
│       ▼                                    ▼                                     │
│   ┌─────────────┐                    ┌─────────────┐                            │
│   │ BASTION-SG  │                    │   ALB-SG    │                            │
│   │             │                    │             │                            │
│   │ Inbound:    │                    │ Inbound:    │                            │
│   │ • SSH:22    │                    │ • HTTP:80   │                            │
│   │   from      │                    │ • HTTPS:443 │                            │
│   │   your IP   │                    │   from      │                            │
│   │             │                    │   0.0.0.0/0 │                            │
│   └──────┬──────┘                    └──────┬──────┘                            │
│          │                                  │                                    │
│          │ SSH (port 22)                    │ HTTP (port 80)                    │
│          │                                  │                                    │
│          ▼                                  ▼                                    │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              APP-SG                                      │   │
│   │                                                                          │   │
│   │   Inbound:                                                              │   │
│   │   • SSH:22 from Bastion-SG (for management)                            │   │
│   │   • HTTP:80 from ALB-SG (for application traffic)                      │   │
│   │                                                                          │   │
│   │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                   │   │
│   │   │   App EC2   │   │   App EC2   │   │   App EC2   │                   │   │
│   │   │   Server    │   │   Server    │   │   Server    │                   │   │
│   │   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                   │   │
│   │          │                 │                 │                           │   │
│   └──────────┼─────────────────┼─────────────────┼───────────────────────────┘   │
│              │                 │                 │                               │
│              │ MySQL (3306) / Redis (6379)       │                               │
│              │                                   │                               │
│              ▼                                   ▼                               │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                               DB-SG                                      │   │
│   │                                                                          │   │
│   │   Inbound:                                                              │   │
│   │   • MySQL:3306 from App-SG                                              │   │
│   │   • Redis:6379 from App-SG                                              │   │
│   │                                                                          │   │
│   │   ┌─────────────┐                    ┌─────────────┐                    │   │
│   │   │  RDS MySQL  │                    │ ElastiCache │                    │   │
│   │   │             │                    │   Redis     │                    │   │
│   │   └─────────────┘                    └─────────────┘                    │   │
│   │                                                                          │   │
│   └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   KEY PRINCIPLE: Security Group chaining by referencing SG IDs                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 4: Launch Bastion Host

### Step 4.1: Get Latest Amazon Linux 2 AMI

```bash
# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
              "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

echo "AMI ID: $AMI_ID"
```

### Step 4.2: Create Key Pair (if you don't have one)

```bash
# Create new key pair (optional - use existing if you have one)
aws ec2 create-key-pair \
    --key-name vpc-lab-key \
    --query 'KeyMaterial' \
    --output text > vpc-lab-key.pem

chmod 400 vpc-lab-key.pem

KEY_NAME="vpc-lab-key"
```

### Step 4.3: Launch Bastion Host

```bash
# Launch Bastion EC2 Instance
aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-group-ids $BASTION_SG \
    --subnet-id $PUBLIC_SUBNET_1 \
    --associate-public-ip-address \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Bastion-Host}]'

# Wait for instance to be running
aws ec2 wait instance-running \
    --filters "Name=tag:Name,Values=Bastion-Host"

BASTION_INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=Bastion-Host" \
    --query 'Reservations[0].Instances[0].InstanceId' --output text)

BASTION_PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $BASTION_INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "Bastion Host Instance ID: $BASTION_INSTANCE_ID"
echo "Bastion Host Public IP: $BASTION_PUBLIC_IP"
echo ""
echo "Connect using: ssh -i $KEY_NAME.pem ec2-user@$BASTION_PUBLIC_IP"
```

### Step 4.4: Launch Private App Server

```bash
# Launch App Server in Private Subnet
aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-group-ids $APP_SG \
    --subnet-id $PRIVATE_APP_SUBNET_1 \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=App-Server}]' \
    --user-data '#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from App Server</h1>" > /var/www/html/index.html'

# Wait for instance
aws ec2 wait instance-running \
    --filters "Name=tag:Name,Values=App-Server"

APP_INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=App-Server" \
    --query 'Reservations[0].Instances[0].InstanceId' --output text)

APP_PRIVATE_IP=$(aws ec2 describe-instances \
    --instance-ids $APP_INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)

echo "App Server Instance ID: $APP_INSTANCE_ID"
echo "App Server Private IP: $APP_PRIVATE_IP"
```

### Step 4.5: Test Bastion Connectivity

```bash
# SSH to Bastion (from your local machine)
ssh -i vpc-lab-key.pem ec2-user@$BASTION_PUBLIC_IP

# From Bastion, SSH to App Server (you need to copy the key to bastion first)
# Or use SSH agent forwarding: ssh -A -i vpc-lab-key.pem ec2-user@$BASTION_PUBLIC_IP
# Then: ssh ec2-user@<APP_PRIVATE_IP>
```

---

## Part 5: Create VPC Peering

### Step 5.1: Create Development VPC

```bash
# Create Development VPC
aws ec2 create-vpc \
    --cidr-block 10.1.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=Development-VPC}]'

VPC_DEV_ID=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=Development-VPC" \
    --query 'Vpcs[0].VpcId' --output text)

# Enable DNS
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_DEV_ID \
    --enable-dns-hostnames '{"Value":true}'

aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_DEV_ID \
    --enable-dns-support '{"Value":true}'

# Create Private Subnet in Dev VPC
aws ec2 create-subnet \
    --vpc-id $VPC_DEV_ID \
    --cidr-block 10.1.1.0/24 \
    --availability-zone $AZ1 \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=Dev-Private-Subnet}]'

DEV_SUBNET=$(aws ec2 describe-subnets \
    --filters "Name=tag:Name,Values=Dev-Private-Subnet" \
    --query 'Subnets[0].SubnetId' --output text)

echo "Development VPC ID: $VPC_DEV_ID"
echo "Development Subnet: $DEV_SUBNET"
```

### Step 5.2: Create VPC Peering Connection

```bash
# Create VPC Peering Connection
aws ec2 create-vpc-peering-connection \
    --vpc-id $VPC_PROD_ID \
    --peer-vpc-id $VPC_DEV_ID \
    --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=Prod-Dev-Peering}]'

PEERING_ID=$(aws ec2 describe-vpc-peering-connections \
    --filters "Name=tag:Name,Values=Prod-Dev-Peering" \
    --query 'VpcPeeringConnections[0].VpcPeeringConnectionId' --output text)

echo "Peering Connection ID: $PEERING_ID"

# Accept the peering connection (since both VPCs are in same account)
aws ec2 accept-vpc-peering-connection \
    --vpc-peering-connection-id $PEERING_ID
```

### Step 5.3: Update Route Tables for Peering

```bash
# Add route to Dev VPC in Production Private Route Table
aws ec2 create-route \
    --route-table-id $PRIVATE_RT \
    --destination-cidr-block 10.1.0.0/16 \
    --vpc-peering-connection-id $PEERING_ID

# Create Route Table for Dev VPC
aws ec2 create-route-table \
    --vpc-id $VPC_DEV_ID \
    --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=Dev-Private-RT}]'

DEV_RT=$(aws ec2 describe-route-tables \
    --filters "Name=tag:Name,Values=Dev-Private-RT" \
    --query 'RouteTables[0].RouteTableId' --output text)

# Add route to Production VPC in Dev Route Table
aws ec2 create-route \
    --route-table-id $DEV_RT \
    --destination-cidr-block 10.0.0.0/16 \
    --vpc-peering-connection-id $PEERING_ID

# Associate Dev Subnet with Dev Route Table
aws ec2 associate-route-table \
    --subnet-id $DEV_SUBNET \
    --route-table-id $DEV_RT

echo "VPC Peering routes configured"
```

### VPC Peering Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        VPC PEERING CONFIGURATION                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                    PRODUCTION VPC (10.0.0.0/16)                          │   │
│   │                                                                          │   │
│   │   Route Table (Production-Private-RT):                                  │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │ 10.0.0.0/16 → local                                             │   │   │
│   │   │ 10.1.0.0/16 → pcx-xxxxx (Peering Connection) ◄── NEW            │   │   │
│   │   │ 0.0.0.0/0   → nat-xxxxx                                         │   │   │
│   │   └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   │   ┌─────────────┐                                                       │   │
│   │   │ App Server  │                                                       │   │
│   │   │ 10.0.2.50   │                                                       │   │
│   │   └──────┬──────┘                                                       │   │
│   │          │                                                               │   │
│   └──────────┼───────────────────────────────────────────────────────────────┘   │
│              │                                                                    │
│              │         ┌────────────────────────────┐                            │
│              │         │   VPC PEERING CONNECTION   │                            │
│              └────────►│       (pcx-xxxxx)          │◄───────────┐               │
│                        │                            │            │               │
│                        │   No transitive routing    │            │               │
│                        └────────────────────────────┘            │               │
│                                                                  │               │
│   ┌──────────────────────────────────────────────────────────────┼───────────┐   │
│   │                    DEVELOPMENT VPC (10.1.0.0/16)             │           │   │
│   │                                                              │           │   │
│   │   Route Table (Dev-Private-RT):                                          │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │ 10.1.0.0/16 → local                                             │   │   │
│   │   │ 10.0.0.0/16 → pcx-xxxxx (Peering Connection) ◄── NEW            │   │   │
│   │   └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   │   ┌─────────────┐                                                       │   │
│   │   │ Dev Server  │                                                       │   │
│   │   │ 10.1.1.50   │                                                       │   │
│   │   └─────────────┘                                                       │   │
│   │                                                                          │   │
│   └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   Now 10.0.2.50 can communicate with 10.1.1.50 via peering!                    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 6: Create VPC Endpoint for S3

### Step 6.1: Create S3 Gateway Endpoint

```bash
# Create S3 Gateway Endpoint
aws ec2 create-vpc-endpoint \
    --vpc-id $VPC_PROD_ID \
    --service-name com.amazonaws.$(aws configure get region).s3 \
    --route-table-ids $PRIVATE_RT \
    --tag-specifications 'ResourceType=vpc-endpoint,Tags=[{Key=Name,Value=S3-Gateway-Endpoint}]'

S3_ENDPOINT=$(aws ec2 describe-vpc-endpoints \
    --filters "Name=tag:Name,Values=S3-Gateway-Endpoint" \
    --query 'VpcEndpoints[0].VpcEndpointId' --output text)

echo "S3 Gateway Endpoint ID: $S3_ENDPOINT"
```

### Step 6.2: Verify Endpoint in Route Table

```bash
# Check the route table for S3 endpoint
aws ec2 describe-route-tables \
    --route-table-ids $PRIVATE_RT \
    --query 'RouteTables[0].Routes'
```

### VPC Endpoint Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        S3 GATEWAY ENDPOINT                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   WITHOUT ENDPOINT (via NAT Gateway):                                           │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   EC2 in Private Subnet                                                 │   │
│   │   ┌─────────┐                                                           │   │
│   │   │   EC2   │ ─► NAT Gateway ─► Internet Gateway ─► Internet ─► S3     │   │
│   │   └─────────┘                                                           │   │
│   │                                                                          │   │
│   │   Problems: Data transfer costs, security exposure, latency             │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   WITH S3 GATEWAY ENDPOINT:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                          │   │
│   │   ┌───────────────────────────────────────────────────────────────┐     │   │
│   │   │                    Production VPC                              │     │   │
│   │   │                                                                │     │   │
│   │   │   Private Route Table:                                        │     │   │
│   │   │   ┌────────────────────────────────────────────────────────┐  │     │   │
│   │   │   │ 10.0.0.0/16    → local                                 │  │     │   │
│   │   │   │ pl-xxxxxxxx    → vpce-xxxxx (S3 Prefix List) ◄── NEW   │  │     │   │
│   │   │   │ 0.0.0.0/0      → nat-xxxxx                             │  │     │   │
│   │   │   └────────────────────────────────────────────────────────┘  │     │   │
│   │   │                                                                │     │   │
│   │   │   ┌─────────────┐          ┌────────────────────────────────┐ │     │   │
│   │   │   │     EC2     │ ────────►│   S3 GATEWAY ENDPOINT          │ │     │   │
│   │   │   │  (Private)  │          │   (vpce-xxxxx)                 │ │     │   │
│   │   │   └─────────────┘          │                                │ │     │   │
│   │   │                            │   Routes traffic to S3         │ │     │   │
│   │   │                            │   via AWS backbone             │ │     │   │
│   │   │                            └──────────────┬─────────────────┘ │     │   │
│   │   │                                           │                   │     │   │
│   │   └───────────────────────────────────────────┼───────────────────┘     │   │
│   │                                               │                         │   │
│   │                                               ▼                         │   │
│   │                                    ┌──────────────────┐                 │   │
│   │                                    │        S3        │                 │   │
│   │                                    │ (AWS Backbone)   │                 │   │
│   │                                    └──────────────────┘                 │   │
│   │                                                                          │   │
│   │   Benefits:                                                             │   │
│   │   • FREE (no hourly or data charges)                                   │   │
│   │   • Private (no internet exposure)                                     │   │
│   │   • Lower latency (AWS backbone)                                       │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 7: Set Up VPC Flow Logs

### Step 7.1: Create CloudWatch Log Group

```bash
# Create CloudWatch Log Group
aws logs create-log-group \
    --log-group-name /aws/vpc/flow-logs/production

# Set retention policy (30 days)
aws logs put-retention-policy \
    --log-group-name /aws/vpc/flow-logs/production \
    --retention-in-days 30
```

### Step 7.2: Create IAM Role for Flow Logs

```bash
# Create IAM Role trust policy
cat > flow-logs-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "vpc-flow-logs.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM Role
aws iam create-role \
    --role-name VPCFlowLogsRole \
    --assume-role-policy-document file://flow-logs-trust-policy.json

# Create permissions policy
cat > flow-logs-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Attach policy to role
aws iam put-role-policy \
    --role-name VPCFlowLogsRole \
    --policy-name VPCFlowLogsPolicy \
    --policy-document file://flow-logs-policy.json

# Get role ARN
FLOW_LOGS_ROLE_ARN=$(aws iam get-role \
    --role-name VPCFlowLogsRole \
    --query 'Role.Arn' --output text)

echo "Flow Logs Role ARN: $FLOW_LOGS_ROLE_ARN"

# Clean up temp files
rm flow-logs-trust-policy.json flow-logs-policy.json
```

### Step 7.3: Create VPC Flow Log

```bash
# Create Flow Log for Production VPC
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids $VPC_PROD_ID \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /aws/vpc/flow-logs/production \
    --deliver-logs-permission-arn $FLOW_LOGS_ROLE_ARN \
    --tag-specifications 'ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=Production-VPC-Flow-Log}]'

FLOW_LOG_ID=$(aws ec2 describe-flow-logs \
    --filter "Name=tag:Name,Values=Production-VPC-Flow-Log" \
    --query 'FlowLogs[0].FlowLogId' --output text)

echo "Flow Log ID: $FLOW_LOG_ID"
```

### Step 7.4: Test Flow Logs

```bash
# Generate some traffic (SSH to bastion, ping, etc.)
# Then query flow logs in CloudWatch Logs Insights:

# Example query to find rejected traffic:
# fields @timestamp, srcAddr, dstAddr, dstPort, action
# | filter action = "REJECT"
# | sort @timestamp desc
# | limit 20
```

---

## Part 8: Create Network ACL

### Step 8.1: Create Custom NACL for Private Subnets

```bash
# Create Network ACL
aws ec2 create-network-acl \
    --vpc-id $VPC_PROD_ID \
    --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=Private-Subnet-NACL}]'

PRIVATE_NACL=$(aws ec2 describe-network-acls \
    --filters "Name=tag:Name,Values=Private-Subnet-NACL" \
    --query 'NetworkAcls[0].NetworkAclId' --output text)

echo "Private NACL ID: $PRIVATE_NACL"

# Add Inbound Rules

# Rule 100: Allow HTTP from VPC
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=80,To=80 \
    --cidr-block 10.0.0.0/16 \
    --rule-action allow \
    --ingress

# Rule 110: Allow HTTPS from VPC
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 110 \
    --protocol tcp \
    --port-range From=443,To=443 \
    --cidr-block 10.0.0.0/16 \
    --rule-action allow \
    --ingress

# Rule 120: Allow SSH from Bastion Subnet
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 120 \
    --protocol tcp \
    --port-range From=22,To=22 \
    --cidr-block 10.0.1.0/24 \
    --rule-action allow \
    --ingress

# Rule 130: Allow ephemeral ports (for return traffic)
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 130 \
    --protocol tcp \
    --port-range From=1024,To=65535 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --ingress

# Add Outbound Rules

# Rule 100: Allow all outbound to VPC
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 100 \
    --protocol tcp \
    --port-range From=0,To=65535 \
    --cidr-block 10.0.0.0/16 \
    --rule-action allow \
    --egress

# Rule 110: Allow HTTPS outbound (for package updates)
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 110 \
    --protocol tcp \
    --port-range From=443,To=443 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --egress

# Rule 120: Allow ephemeral ports outbound
aws ec2 create-network-acl-entry \
    --network-acl-id $PRIVATE_NACL \
    --rule-number 120 \
    --protocol tcp \
    --port-range From=1024,To=65535 \
    --cidr-block 0.0.0.0/0 \
    --rule-action allow \
    --egress

echo "NACL rules configured"
```

---

## Part 9: Verification and Testing

### Step 9.1: Verify All Resources

```bash
echo "============================================"
echo "           RESOURCE VERIFICATION            "
echo "============================================"

echo ""
echo "=== VPCs ==="
aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=Production-VPC,Development-VPC" \
    --query 'Vpcs[*].{Name:Tags[?Key==`Name`].Value|[0],VpcId:VpcId,CIDR:CidrBlock}' \
    --output table

echo ""
echo "=== Subnets ==="
aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_PROD_ID" \
    --query 'Subnets[*].{Name:Tags[?Key==`Name`].Value|[0],SubnetId:SubnetId,CIDR:CidrBlock,AZ:AvailabilityZone}' \
    --output table

echo ""
echo "=== NAT Gateway ==="
aws ec2 describe-nat-gateways \
    --filter "Name=vpc-id,Values=$VPC_PROD_ID" \
    --query 'NatGateways[*].{Name:Tags[?Key==`Name`].Value|[0],NatGatewayId:NatGatewayId,State:State}' \
    --output table

echo ""
echo "=== VPC Peering ==="
aws ec2 describe-vpc-peering-connections \
    --query 'VpcPeeringConnections[*].{Name:Tags[?Key==`Name`].Value|[0],PeeringId:VpcPeeringConnectionId,Status:Status.Code}' \
    --output table

echo ""
echo "=== VPC Endpoints ==="
aws ec2 describe-vpc-endpoints \
    --filters "Name=vpc-id,Values=$VPC_PROD_ID" \
    --query 'VpcEndpoints[*].{Name:Tags[?Key==`Name`].Value|[0],EndpointId:VpcEndpointId,ServiceName:ServiceName}' \
    --output table

echo ""
echo "=== EC2 Instances ==="
aws ec2 describe-instances \
    --filters "Name=vpc-id,Values=$VPC_PROD_ID" "Name=instance-state-name,Values=running" \
    --query 'Reservations[*].Instances[*].{Name:Tags[?Key==`Name`].Value|[0],InstanceId:InstanceId,PrivateIP:PrivateIpAddress,PublicIP:PublicIpAddress}' \
    --output table

echo ""
echo "=== Flow Logs ==="
aws ec2 describe-flow-logs \
    --query 'FlowLogs[*].{Name:Tags[?Key==`Name`].Value|[0],FlowLogId:FlowLogId,Status:FlowLogStatus}' \
    --output table
```

### Step 9.2: Connectivity Tests

```bash
# Test 1: SSH to Bastion
echo "Test 1: Connecting to Bastion Host..."
ssh -o ConnectTimeout=10 -i vpc-lab-key.pem ec2-user@$BASTION_PUBLIC_IP "echo 'Bastion connection successful!'"

# Test 2: From Bastion, test NAT Gateway (internet access from private subnet)
echo ""
echo "Test 2: Testing NAT Gateway from App Server..."
# (Run this from Bastion after SSHing to App Server)
# curl -s https://checkip.amazonaws.com

# Test 3: S3 Endpoint Test
echo ""
echo "Test 3: S3 Endpoint test commands (run from App Server):"
echo "aws s3 ls"
```

---

## Part 10: Cleanup

**IMPORTANT: Run cleanup to avoid ongoing charges!**

### Step 10.1: Delete EC2 Instances

```bash
echo "Terminating EC2 instances..."

# Terminate App Server
aws ec2 terminate-instances --instance-ids $APP_INSTANCE_ID

# Terminate Bastion Host
aws ec2 terminate-instances --instance-ids $BASTION_INSTANCE_ID

# Wait for termination
aws ec2 wait instance-terminated --instance-ids $APP_INSTANCE_ID $BASTION_INSTANCE_ID
echo "EC2 instances terminated"
```

### Step 10.2: Delete VPC Flow Log

```bash
echo "Deleting Flow Log..."
aws ec2 delete-flow-logs --flow-log-ids $FLOW_LOG_ID

# Delete CloudWatch Log Group
aws logs delete-log-group --log-group-name /aws/vpc/flow-logs/production

# Delete IAM Role
aws iam delete-role-policy --role-name VPCFlowLogsRole --policy-name VPCFlowLogsPolicy
aws iam delete-role --role-name VPCFlowLogsRole
echo "Flow logs and IAM role deleted"
```

### Step 10.3: Delete VPC Endpoint

```bash
echo "Deleting VPC Endpoint..."
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids $S3_ENDPOINT
echo "VPC Endpoint deleted"
```

### Step 10.4: Delete VPC Peering

```bash
echo "Deleting VPC Peering..."
aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $PEERING_ID
echo "VPC Peering deleted"
```

### Step 10.5: Delete NAT Gateway

```bash
echo "Deleting NAT Gateway..."
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_ID

# Wait for NAT Gateway to be deleted
echo "Waiting for NAT Gateway deletion..."
sleep 60

# Release Elastic IP
aws ec2 release-address --allocation-id $NAT_EIP_ALLOC
echo "NAT Gateway and Elastic IP deleted"
```

### Step 10.6: Delete Security Groups

```bash
echo "Deleting Security Groups..."
aws ec2 delete-security-group --group-id $DB_SG
aws ec2 delete-security-group --group-id $APP_SG
aws ec2 delete-security-group --group-id $ALB_SG
aws ec2 delete-security-group --group-id $BASTION_SG
echo "Security Groups deleted"
```

### Step 10.7: Delete Subnets

```bash
echo "Deleting Subnets..."

# Production VPC Subnets
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_1
aws ec2 delete-subnet --subnet-id $PUBLIC_SUBNET_2
aws ec2 delete-subnet --subnet-id $PRIVATE_APP_SUBNET_1
aws ec2 delete-subnet --subnet-id $PRIVATE_APP_SUBNET_2
aws ec2 delete-subnet --subnet-id $DATA_SUBNET_1
aws ec2 delete-subnet --subnet-id $DATA_SUBNET_2

# Development VPC Subnet
aws ec2 delete-subnet --subnet-id $DEV_SUBNET

echo "Subnets deleted"
```

### Step 10.8: Delete Route Tables

```bash
echo "Deleting Route Tables..."

# Get and delete route table associations first
# (Main route table cannot be deleted)

# Delete custom route tables
aws ec2 delete-route-table --route-table-id $PUBLIC_RT 2>/dev/null || true
aws ec2 delete-route-table --route-table-id $PRIVATE_RT 2>/dev/null || true
aws ec2 delete-route-table --route-table-id $DEV_RT 2>/dev/null || true

echo "Route Tables deleted"
```

### Step 10.9: Delete NACL

```bash
echo "Deleting NACL..."
aws ec2 delete-network-acl --network-acl-id $PRIVATE_NACL 2>/dev/null || true
echo "NACL deleted"
```

### Step 10.10: Delete Internet Gateway

```bash
echo "Deleting Internet Gateway..."
aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_PROD_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID
echo "Internet Gateway deleted"
```

### Step 10.11: Delete VPCs

```bash
echo "Deleting VPCs..."
aws ec2 delete-vpc --vpc-id $VPC_DEV_ID
aws ec2 delete-vpc --vpc-id $VPC_PROD_ID
echo "VPCs deleted"
```

### Step 10.12: Delete Key Pair (Optional)

```bash
echo "Deleting Key Pair..."
aws ec2 delete-key-pair --key-name vpc-lab-key
rm -f vpc-lab-key.pem
echo "Key Pair deleted"
```

### Cleanup Verification

```bash
echo ""
echo "============================================"
echo "           CLEANUP VERIFICATION             "
echo "============================================"

echo ""
echo "Remaining VPCs (should be empty or only default):"
aws ec2 describe-vpcs \
    --query 'Vpcs[*].{VpcId:VpcId,Name:Tags[?Key==`Name`].Value|[0],IsDefault:IsDefault}' \
    --output table

echo ""
echo "Remaining NAT Gateways (should be empty):"
aws ec2 describe-nat-gateways \
    --filter "Name=state,Values=available" \
    --query 'NatGateways[*].NatGatewayId' \
    --output text

echo ""
echo "Remaining Elastic IPs (should be empty for this lab):"
aws ec2 describe-addresses \
    --query 'Addresses[*].{AllocationId:AllocationId,PublicIp:PublicIp}' \
    --output table

echo ""
echo "Cleanup complete!"
```

---

## Lab Summary

In this comprehensive lab, you successfully:

1. **Created a Production VPC** with proper CIDR planning
2. **Set up multi-tier subnets** (public, private app, private data)
3. **Configured NAT Gateway** for private subnet internet access
4. **Created security groups** with proper chaining
5. **Launched a bastion host** for secure access
6. **Set up VPC peering** between production and development VPCs
7. **Created S3 Gateway Endpoint** for private S3 access
8. **Enabled VPC Flow Logs** for monitoring
9. **Configured Network ACLs** for additional security

### Key Takeaways

- VPC design should follow the principle of least privilege
- Use security group chaining (referencing SG IDs) for maintainability
- NAT Gateway should be in each AZ for high availability
- VPC Flow Logs are essential for troubleshooting and security
- Gateway Endpoints for S3/DynamoDB are free - use them!
- Always clean up resources to avoid unexpected charges

---

**Congratulations on completing the VPC Networking Lab!**

Return to [Module Overview](README.md) or take the [Quiz](quiz.md)
