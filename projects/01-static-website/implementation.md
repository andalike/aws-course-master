# Static Website on AWS - Complete Implementation Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Complete Implementation](#complete-implementation)
4. [CloudFormation Template](#cloudformation-template)
5. [CLI Deployment Scripts](#cli-deployment-scripts)
6. [Website Source Code](#website-source-code)
7. [Custom Domain Setup](#custom-domain-setup)
8. [SSL/TLS Certificate Configuration](#ssltls-certificate-configuration)
9. [Testing and Validation](#testing-and-validation)
10. [Cost Analysis](#cost-analysis)
11. [Troubleshooting Guide](#troubleshooting-guide)

---

## Architecture Overview

```
                                    STATIC WEBSITE ARCHITECTURE
    ===============================================================================================

    +---------+         +------------+         +---------------+         +-----------------+
    |         |   DNS   |            |  HTTPS  |               |   S3    |                 |
    |  Users  +-------->+  Route 53  +-------->+  CloudFront   +-------->+   S3 Bucket     |
    |         |         |            |         |  Distribution |   OAC   | (Static Files)  |
    +---------+         +-----+------+         +-------+-------+         +-----------------+
                              |                        |
                              |                        |
                        +-----v------+          +------v------+
                        |   ACM      |          |  CloudFront |
                        | SSL Cert   |          |  Functions  |
                        | (us-east-1)|          |  (Optional) |
                        +------------+          +-------------+

    FLOW:
    1. User requests www.example.com
    2. Route 53 resolves to CloudFront distribution
    3. CloudFront checks edge cache
    4. If cache miss, CloudFront fetches from S3 via OAC
    5. Response served with SSL/TLS encryption

    COMPONENTS:
    +------------------+------------------------------------------+
    | S3 Bucket        | Stores static files (HTML, CSS, JS, etc) |
    | CloudFront       | CDN with 400+ edge locations globally    |
    | Route 53         | DNS management with alias records        |
    | ACM              | Free SSL/TLS certificates                |
    | OAC              | Secure S3 access from CloudFront only    |
    +------------------+------------------------------------------+
```

---

## Prerequisites

### Required Tools

```bash
# Check AWS CLI version (v2 recommended)
aws --version

# Configure AWS credentials
aws configure

# Required permissions:
# - s3:*
# - cloudfront:*
# - route53:*
# - acm:*
```

### Required Information

| Item | Example | Notes |
|------|---------|-------|
| AWS Account | 123456789012 | Free tier eligible |
| Region | us-east-1 | ACM must be us-east-1 for CloudFront |
| Domain (optional) | example.com | Registered via Route 53 or external |
| Unique bucket name | mysite-abc123 | Globally unique |

---

## Complete Implementation

### Phase 1: S3 Bucket Setup

#### Step 1.1: Create S3 Bucket

```bash
# Set your unique bucket name
export BUCKET_NAME="mywebsite-$(date +%s)"
export AWS_REGION="us-east-1"

# Create bucket
aws s3api create-bucket \
    --bucket ${BUCKET_NAME} \
    --region ${AWS_REGION}

# For regions other than us-east-1, add location constraint:
# aws s3api create-bucket \
#     --bucket ${BUCKET_NAME} \
#     --region eu-west-1 \
#     --create-bucket-configuration LocationConstraint=eu-west-1
```

#### Step 1.2: Enable Static Website Hosting

```bash
# Enable static website hosting
aws s3 website s3://${BUCKET_NAME}/ \
    --index-document index.html \
    --error-document error.html

# Verify configuration
aws s3api get-bucket-website --bucket ${BUCKET_NAME}
```

#### Step 1.3: Block Public Access (We'll use CloudFront OAC)

```bash
# Block all public access - CloudFront will access via OAC
aws s3api put-public-access-block \
    --bucket ${BUCKET_NAME} \
    --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

### Phase 2: CloudFront Distribution

#### Step 2.1: Create Origin Access Control (OAC)

```bash
# Create OAC for secure S3 access
aws cloudfront create-origin-access-control \
    --origin-access-control-config '{
        "Name": "'${BUCKET_NAME}'-oac",
        "Description": "OAC for static website S3 bucket",
        "SigningProtocol": "sigv4",
        "SigningBehavior": "always",
        "OriginAccessControlOriginType": "s3"
    }' > oac-output.json

# Extract OAC ID
export OAC_ID=$(cat oac-output.json | jq -r '.OriginAccessControl.Id')
echo "OAC ID: ${OAC_ID}"
```

#### Step 2.2: Create CloudFront Distribution

```bash
# Create distribution configuration
cat > cloudfront-config.json << 'CFCONFIG'
{
    "CallerReference": "static-website-TIMESTAMP",
    "Comment": "Static Website Distribution",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-BUCKET_NAME",
                "DomainName": "BUCKET_NAME.s3.us-east-1.amazonaws.com",
                "OriginAccessControlId": "OAC_ID",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "Compress": true,
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "OriginRequestPolicyId": "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/error.html",
                "ResponseCode": "404",
                "ErrorCachingMinTTL": 300
            },
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/error.html",
                "ResponseCode": "404",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "PriceClass": "PriceClass_100",
    "Enabled": true,
    "HttpVersion": "http2and3"
}
CFCONFIG

# Replace placeholders
sed -i '' "s/TIMESTAMP/$(date +%s)/g" cloudfront-config.json
sed -i '' "s/BUCKET_NAME/${BUCKET_NAME}/g" cloudfront-config.json
sed -i '' "s/OAC_ID/${OAC_ID}/g" cloudfront-config.json

# Create distribution
aws cloudfront create-distribution \
    --distribution-config file://cloudfront-config.json > cf-output.json

# Extract distribution details
export CF_DOMAIN=$(cat cf-output.json | jq -r '.Distribution.DomainName')
export CF_ID=$(cat cf-output.json | jq -r '.Distribution.Id')
export CF_ARN=$(cat cf-output.json | jq -r '.Distribution.ARN')

echo "CloudFront Domain: ${CF_DOMAIN}"
echo "CloudFront ID: ${CF_ID}"
```

#### Step 2.3: Update S3 Bucket Policy for CloudFront

```bash
# Create bucket policy allowing CloudFront access
cat > bucket-policy.json << POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudfront.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": "${CF_ARN}"
                }
            }
        }
    ]
}
POLICY

# Apply bucket policy
aws s3api put-bucket-policy \
    --bucket ${BUCKET_NAME} \
    --policy file://bucket-policy.json
```

### Phase 3: Upload Website Files

```bash
# Upload with appropriate content types
aws s3 sync ./website s3://${BUCKET_NAME}/ \
    --delete \
    --cache-control "max-age=31536000" \
    --exclude "*.html"

aws s3 sync ./website s3://${BUCKET_NAME}/ \
    --delete \
    --cache-control "max-age=0, no-cache, no-store, must-revalidate" \
    --include "*.html"

# Verify upload
aws s3 ls s3://${BUCKET_NAME}/ --recursive --human-readable
```

---

## CloudFormation Template

Save as `static-website-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete Static Website Infrastructure with S3, CloudFront, Route 53, and ACM'

Parameters:
  DomainName:
    Type: String
    Description: 'Domain name for the website (e.g., example.com)'
    Default: ''

  SubDomain:
    Type: String
    Description: 'Subdomain for the website (e.g., www)'
    Default: 'www'

  CreateDNSRecords:
    Type: String
    Description: 'Create Route 53 DNS records'
    AllowedValues: ['true', 'false']
    Default: 'false'

  HostedZoneId:
    Type: String
    Description: 'Route 53 Hosted Zone ID (required if CreateDNSRecords is true)'
    Default: ''

Conditions:
  HasDomain: !Not [!Equals [!Ref DomainName, '']]
  CreateDNS: !And
    - !Equals [!Ref CreateDNSRecords, 'true']
    - !Condition HasDomain

Resources:
  # S3 Bucket for Static Content
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-website-${AWS::AccountId}'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: false
        IgnorePublicAcls: true
        RestrictPublicBuckets: false
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldVersions
            Status: Enabled
            NoncurrentVersionExpiration:
              NoncurrentDays: 30
      Tags:
        - Key: Purpose
          Value: StaticWebsite

  # S3 Bucket for CloudFront Logs
  LogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-logs-${AWS::AccountId}'
      OwnershipControls:
        Rules:
          - ObjectOwnership: BucketOwnerPreferred
      LifecycleConfiguration:
        Rules:
          - Id: DeleteOldLogs
            Status: Enabled
            ExpirationInDays: 90

  # Origin Access Control for CloudFront
  CloudFrontOAC:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: !Sub '${AWS::StackName}-oac'
        Description: 'Origin Access Control for S3'
        SigningProtocol: sigv4
        SigningBehavior: always
        OriginAccessControlOriginType: s3

  # Bucket Policy allowing CloudFront access
  WebsiteBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref WebsiteBucket
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Sid: AllowCloudFrontServicePrincipal
            Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: s3:GetObject
            Resource: !Sub '${WebsiteBucket.Arn}/*'
            Condition:
              StringEquals:
                'AWS:SourceArn': !Sub 'arn:aws:cloudfront::${AWS::AccountId}:distribution/${CloudFrontDistribution}'

  # SSL Certificate (only if domain is specified)
  SSLCertificate:
    Type: AWS::CertificateManager::Certificate
    Condition: HasDomain
    Properties:
      DomainName: !If
        - HasDomain
        - !Sub '${SubDomain}.${DomainName}'
        - !Ref 'AWS::NoValue'
      SubjectAlternativeNames:
        - !If [HasDomain, !Ref DomainName, !Ref 'AWS::NoValue']
      ValidationMethod: DNS
      DomainValidationOptions:
        - DomainName: !Sub '${SubDomain}.${DomainName}'
          HostedZoneId: !If [CreateDNS, !Ref HostedZoneId, !Ref 'AWS::NoValue']

  # CloudFront Cache Policy
  CachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Sub '${AWS::StackName}-cache-policy'
        DefaultTTL: 86400
        MaxTTL: 31536000
        MinTTL: 0
        ParametersInCacheKeyAndForwardedToOrigin:
          CookiesConfig:
            CookieBehavior: none
          HeadersConfig:
            HeaderBehavior: none
          QueryStringsConfig:
            QueryStringBehavior: none
          EnableAcceptEncodingGzip: true
          EnableAcceptEncodingBrotli: true

  # CloudFront Response Headers Policy
  ResponseHeadersPolicy:
    Type: AWS::CloudFront::ResponseHeadersPolicy
    Properties:
      ResponseHeadersPolicyConfig:
        Name: !Sub '${AWS::StackName}-security-headers'
        SecurityHeadersConfig:
          StrictTransportSecurity:
            AccessControlMaxAgeSec: 31536000
            IncludeSubdomains: true
            Override: true
            Preload: true
          ContentSecurityPolicy:
            ContentSecurityPolicy: "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com"
            Override: true
          XContentTypeOptions:
            Override: true
          XFrameOptions:
            FrameOption: DENY
            Override: true
          XSSProtection:
            ModeBlock: true
            Override: true
            Protection: true
          ReferrerPolicy:
            ReferrerPolicy: strict-origin-when-cross-origin
            Override: true

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Comment: !Sub 'Static Website - ${AWS::StackName}'
        DefaultRootObject: index.html
        Enabled: true
        HttpVersion: http2and3
        IPV6Enabled: true
        PriceClass: PriceClass_100

        Aliases: !If
          - HasDomain
          - - !Sub '${SubDomain}.${DomainName}'
            - !Ref DomainName
          - !Ref 'AWS::NoValue'

        ViewerCertificate: !If
          - HasDomain
          - AcmCertificateArn: !Ref SSLCertificate
            MinimumProtocolVersion: TLSv1.2_2021
            SslSupportMethod: sni-only
          - CloudFrontDefaultCertificate: true

        Origins:
          - Id: S3Origin
            DomainName: !GetAtt WebsiteBucket.RegionalDomainName
            OriginAccessControlId: !Ref CloudFrontOAC
            S3OriginConfig:
              OriginAccessIdentity: ''

        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
            - OPTIONS
          CachedMethods:
            - GET
            - HEAD
          Compress: true
          CachePolicyId: !Ref CachePolicy
          ResponseHeadersPolicyId: !Ref ResponseHeadersPolicy

        CustomErrorResponses:
          - ErrorCode: 403
            ResponseCode: 404
            ResponsePagePath: /error.html
            ErrorCachingMinTTL: 300
          - ErrorCode: 404
            ResponseCode: 404
            ResponsePagePath: /error.html
            ErrorCachingMinTTL: 300

        Logging:
          Bucket: !GetAtt LogsBucket.DomainName
          IncludeCookies: false
          Prefix: 'cdn-logs/'

  # Route 53 DNS Records
  DNSRecordWWW:
    Type: AWS::Route53::RecordSet
    Condition: CreateDNS
    Properties:
      HostedZoneId: !Ref HostedZoneId
      Name: !Sub '${SubDomain}.${DomainName}'
      Type: A
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        HostedZoneId: Z2FDTNDATAQYW2  # CloudFront hosted zone ID

  DNSRecordApex:
    Type: AWS::Route53::RecordSet
    Condition: CreateDNS
    Properties:
      HostedZoneId: !Ref HostedZoneId
      Name: !Ref DomainName
      Type: A
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        HostedZoneId: Z2FDTNDATAQYW2

Outputs:
  WebsiteBucketName:
    Description: 'Name of the S3 bucket'
    Value: !Ref WebsiteBucket
    Export:
      Name: !Sub '${AWS::StackName}-BucketName'

  WebsiteBucketArn:
    Description: 'ARN of the S3 bucket'
    Value: !GetAtt WebsiteBucket.Arn
    Export:
      Name: !Sub '${AWS::StackName}-BucketArn'

  CloudFrontDistributionId:
    Description: 'CloudFront Distribution ID'
    Value: !Ref CloudFrontDistribution
    Export:
      Name: !Sub '${AWS::StackName}-DistributionId'

  CloudFrontDomainName:
    Description: 'CloudFront Distribution Domain Name'
    Value: !GetAtt CloudFrontDistribution.DomainName
    Export:
      Name: !Sub '${AWS::StackName}-CloudFrontDomain'

  WebsiteURL:
    Description: 'Website URL'
    Value: !If
      - HasDomain
      - !Sub 'https://${SubDomain}.${DomainName}'
      - !Sub 'https://${CloudFrontDistribution.DomainName}'

  UploadCommand:
    Description: 'Command to upload website files'
    Value: !Sub 'aws s3 sync ./website s3://${WebsiteBucket}/ --delete'

  InvalidationCommand:
    Description: 'Command to invalidate CloudFront cache'
    Value: !Sub 'aws cloudfront create-invalidation --distribution-id ${CloudFrontDistribution} --paths "/*"'
```

### Deploy CloudFormation Stack

```bash
# Deploy without custom domain
aws cloudformation create-stack \
    --stack-name static-website \
    --template-body file://static-website-stack.yaml \
    --capabilities CAPABILITY_IAM

# Deploy with custom domain
aws cloudformation create-stack \
    --stack-name static-website \
    --template-body file://static-website-stack.yaml \
    --parameters \
        ParameterKey=DomainName,ParameterValue=example.com \
        ParameterKey=SubDomain,ParameterValue=www \
        ParameterKey=CreateDNSRecords,ParameterValue=true \
        ParameterKey=HostedZoneId,ParameterValue=Z1234567890ABC \
    --capabilities CAPABILITY_IAM

# Monitor stack creation
aws cloudformation describe-stacks \
    --stack-name static-website \
    --query 'Stacks[0].StackStatus'

# Get outputs
aws cloudformation describe-stacks \
    --stack-name static-website \
    --query 'Stacks[0].Outputs'
```

---

## CLI Deployment Scripts

### deploy.sh - Complete Deployment Script

```bash
#!/bin/bash
set -euo pipefail

# Configuration
PROJECT_NAME="${1:-my-static-website}"
DOMAIN_NAME="${2:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"
WEBSITE_DIR="${3:-./website}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi

    if [[ ! -d "$WEBSITE_DIR" ]]; then
        log_error "Website directory not found: $WEBSITE_DIR"
        exit 1
    fi

    log_info "Prerequisites validated successfully"
}

# Create S3 bucket
create_s3_bucket() {
    local bucket_name="${PROJECT_NAME}-$(aws sts get-caller-identity --query Account --output text)"

    log_info "Creating S3 bucket: $bucket_name"

    if aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
        log_warn "Bucket already exists"
    else
        aws s3api create-bucket \
            --bucket "$bucket_name" \
            --region "$AWS_REGION" \
            ${AWS_REGION:+$([ "$AWS_REGION" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=$AWS_REGION")}
    fi

    # Enable website hosting
    aws s3 website "s3://$bucket_name/" \
        --index-document index.html \
        --error-document error.html

    echo "$bucket_name"
}

# Create CloudFront OAC
create_oac() {
    local oac_name="${PROJECT_NAME}-oac"

    log_info "Creating Origin Access Control..."

    # Check if OAC exists
    local existing_oac=$(aws cloudfront list-origin-access-controls \
        --query "OriginAccessControlList.Items[?Name=='$oac_name'].Id" \
        --output text)

    if [[ -n "$existing_oac" ]]; then
        log_warn "OAC already exists: $existing_oac"
        echo "$existing_oac"
        return
    fi

    local oac_result=$(aws cloudfront create-origin-access-control \
        --origin-access-control-config '{
            "Name": "'"$oac_name"'",
            "Description": "OAC for '"$PROJECT_NAME"'",
            "SigningProtocol": "sigv4",
            "SigningBehavior": "always",
            "OriginAccessControlOriginType": "s3"
        }')

    echo "$oac_result" | jq -r '.OriginAccessControl.Id'
}

# Create CloudFront distribution
create_distribution() {
    local bucket_name="$1"
    local oac_id="$2"

    log_info "Creating CloudFront distribution..."

    local config=$(cat <<EOF
{
    "CallerReference": "${PROJECT_NAME}-$(date +%s)",
    "Comment": "Distribution for ${PROJECT_NAME}",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [{
            "Id": "S3-${bucket_name}",
            "DomainName": "${bucket_name}.s3.${AWS_REGION}.amazonaws.com",
            "OriginAccessControlId": "${oac_id}",
            "S3OriginConfig": {"OriginAccessIdentity": ""}
        }]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${bucket_name}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}
        },
        "Compress": true,
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6"
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [{
            "ErrorCode": 404,
            "ResponsePagePath": "/error.html",
            "ResponseCode": "404",
            "ErrorCachingMinTTL": 300
        }]
    },
    "PriceClass": "PriceClass_100",
    "Enabled": true,
    "HttpVersion": "http2and3"
}
EOF
)

    local result=$(aws cloudfront create-distribution \
        --distribution-config "$config")

    local dist_id=$(echo "$result" | jq -r '.Distribution.Id')
    local dist_domain=$(echo "$result" | jq -r '.Distribution.DomainName')
    local dist_arn=$(echo "$result" | jq -r '.Distribution.ARN')

    echo "$dist_id|$dist_domain|$dist_arn"
}

# Update S3 bucket policy
update_bucket_policy() {
    local bucket_name="$1"
    local distribution_arn="$2"

    log_info "Updating S3 bucket policy..."

    local policy=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "AllowCloudFrontServicePrincipal",
        "Effect": "Allow",
        "Principal": {"Service": "cloudfront.amazonaws.com"},
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::${bucket_name}/*",
        "Condition": {
            "StringEquals": {"AWS:SourceArn": "${distribution_arn}"}
        }
    }]
}
EOF
)

    aws s3api put-bucket-policy \
        --bucket "$bucket_name" \
        --policy "$policy"
}

# Upload website files
upload_website() {
    local bucket_name="$1"

    log_info "Uploading website files to S3..."

    # Upload non-HTML files with long cache
    aws s3 sync "$WEBSITE_DIR" "s3://$bucket_name/" \
        --exclude "*.html" \
        --cache-control "max-age=31536000,public" \
        --delete

    # Upload HTML files with no cache
    aws s3 sync "$WEBSITE_DIR" "s3://$bucket_name/" \
        --exclude "*" \
        --include "*.html" \
        --cache-control "max-age=0,no-cache,no-store,must-revalidate" \
        --delete

    log_info "Website files uploaded successfully"
}

# Main deployment
main() {
    log_info "Starting deployment for: $PROJECT_NAME"

    validate_prerequisites

    local bucket_name=$(create_s3_bucket)
    log_info "Bucket created: $bucket_name"

    local oac_id=$(create_oac)
    log_info "OAC created: $oac_id"

    local dist_info=$(create_distribution "$bucket_name" "$oac_id")
    local dist_id=$(echo "$dist_info" | cut -d'|' -f1)
    local dist_domain=$(echo "$dist_info" | cut -d'|' -f2)
    local dist_arn=$(echo "$dist_info" | cut -d'|' -f3)

    log_info "Distribution created: $dist_id"

    update_bucket_policy "$bucket_name" "$dist_arn"

    upload_website "$bucket_name"

    echo ""
    echo "=============================================="
    echo "Deployment Complete!"
    echo "=============================================="
    echo "Bucket Name:         $bucket_name"
    echo "Distribution ID:     $dist_id"
    echo "CloudFront Domain:   https://$dist_domain"
    echo ""
    echo "Note: CloudFront distribution takes 5-15 minutes to deploy globally."
    echo ""
    echo "To invalidate cache:"
    echo "  aws cloudfront create-invalidation --distribution-id $dist_id --paths '/*'"
}

main
```

### invalidate.sh - Cache Invalidation Script

```bash
#!/bin/bash
set -euo pipefail

DISTRIBUTION_ID="${1:-}"
PATHS="${2:-/*}"

if [[ -z "$DISTRIBUTION_ID" ]]; then
    echo "Usage: $0 <distribution-id> [paths]"
    echo "Example: $0 E1234567890ABC '/index.html' '/css/*'"
    exit 1
fi

echo "Creating cache invalidation..."
result=$(aws cloudfront create-invalidation \
    --distribution-id "$DISTRIBUTION_ID" \
    --paths "$PATHS")

invalidation_id=$(echo "$result" | jq -r '.Invalidation.Id')
echo "Invalidation created: $invalidation_id"

echo "Waiting for invalidation to complete..."
aws cloudfront wait invalidation-completed \
    --distribution-id "$DISTRIBUTION_ID" \
    --id "$invalidation_id"

echo "Cache invalidation completed!"
```

### cleanup.sh - Resource Cleanup Script

```bash
#!/bin/bash
set -euo pipefail

PROJECT_NAME="${1:-}"

if [[ -z "$PROJECT_NAME" ]]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

echo "WARNING: This will delete all resources for $PROJECT_NAME"
read -p "Are you sure? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo "Aborted"
    exit 0
fi

BUCKET_NAME="${PROJECT_NAME}-$(aws sts get-caller-identity --query Account --output text)"

# Get distribution ID
DIST_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='Distribution for ${PROJECT_NAME}'].Id" \
    --output text)

if [[ -n "$DIST_ID" ]]; then
    echo "Disabling CloudFront distribution: $DIST_ID"

    # Get current config
    config=$(aws cloudfront get-distribution-config --id "$DIST_ID")
    etag=$(echo "$config" | jq -r '.ETag')

    # Disable distribution
    disabled_config=$(echo "$config" | jq '.DistributionConfig.Enabled = false' | jq '.DistributionConfig')
    aws cloudfront update-distribution \
        --id "$DIST_ID" \
        --if-match "$etag" \
        --distribution-config "$disabled_config" > /dev/null

    echo "Waiting for distribution to be disabled (this may take several minutes)..."
    aws cloudfront wait distribution-deployed --id "$DIST_ID"

    # Get new ETag and delete
    new_etag=$(aws cloudfront get-distribution --id "$DIST_ID" --query 'ETag' --output text)
    aws cloudfront delete-distribution --id "$DIST_ID" --if-match "$new_etag"
    echo "Distribution deleted"
fi

# Empty and delete S3 bucket
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "Emptying S3 bucket: $BUCKET_NAME"
    aws s3 rm "s3://$BUCKET_NAME" --recursive

    echo "Deleting S3 bucket"
    aws s3 rb "s3://$BUCKET_NAME"
fi

# Delete OAC
OAC_ID=$(aws cloudfront list-origin-access-controls \
    --query "OriginAccessControlList.Items[?Name=='${PROJECT_NAME}-oac'].Id" \
    --output text)

if [[ -n "$OAC_ID" ]]; then
    echo "Deleting OAC: $OAC_ID"
    etag=$(aws cloudfront get-origin-access-control --id "$OAC_ID" --query 'ETag' --output text)
    aws cloudfront delete-origin-access-control --id "$OAC_ID" --if-match "$etag"
fi

echo "Cleanup complete!"
```

---

## Website Source Code

### Complete Website Structure

```
website/
├── index.html
├── error.html
├── about.html
├── contact.html
├── css/
│   ├── styles.css
│   └── responsive.css
├── js/
│   ├── main.js
│   └── animations.js
├── images/
│   ├── logo.svg
│   └── hero-bg.jpg
└── favicon.ico
```

### index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Professional static website hosted on AWS S3 with CloudFront CDN">
    <meta name="robots" content="index, follow">
    <title>AWS Hosted Website | Fast & Secure</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/styles.css">
    <link rel="stylesheet" href="/css/responsive.css">
</head>
<body>
    <header class="header">
        <nav class="navbar container">
            <a href="/" class="logo">
                <span class="logo-text">AWS<span class="accent">Site</span></span>
            </a>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link active">Home</a></li>
                <li><a href="/about.html" class="nav-link">About</a></li>
                <li><a href="/#services" class="nav-link">Services</a></li>
                <li><a href="/contact.html" class="nav-link">Contact</a></li>
            </ul>
            <button class="mobile-menu-btn" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </nav>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <div class="hero-content">
                    <h1 class="hero-title">
                        Lightning Fast <br>
                        <span class="gradient-text">Global Delivery</span>
                    </h1>
                    <p class="hero-description">
                        This website is hosted on Amazon S3 and delivered worldwide
                        through CloudFront's 400+ edge locations. Experience sub-50ms
                        latency from anywhere in the world.
                    </p>
                    <div class="hero-buttons">
                        <a href="#services" class="btn btn-primary">Explore Services</a>
                        <a href="#architecture" class="btn btn-secondary">View Architecture</a>
                    </div>
                    <div class="hero-stats">
                        <div class="stat">
                            <span class="stat-value">99.99%</span>
                            <span class="stat-label">Uptime</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">&lt;50ms</span>
                            <span class="stat-label">Latency</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">400+</span>
                            <span class="stat-label">Edge Locations</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="services" class="services">
            <div class="container">
                <h2 class="section-title">AWS Services Powering This Site</h2>
                <p class="section-subtitle">
                    Production-grade infrastructure using AWS best practices
                </p>
                <div class="services-grid">
                    <div class="service-card">
                        <div class="service-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                                <polyline points="22,6 12,13 2,6"/>
                            </svg>
                        </div>
                        <h3>Amazon S3</h3>
                        <p>Highly durable object storage with 11 9's durability. Stores all static assets including HTML, CSS, JavaScript, and images.</p>
                        <ul class="service-features">
                            <li>99.999999999% durability</li>
                            <li>Automatic encryption</li>
                            <li>Versioning enabled</li>
                        </ul>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <line x1="2" y1="12" x2="22" y2="12"/>
                                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                            </svg>
                        </div>
                        <h3>CloudFront CDN</h3>
                        <p>Global content delivery network with edge caching for minimal latency worldwide. HTTP/3 and IPv6 enabled.</p>
                        <ul class="service-features">
                            <li>400+ edge locations</li>
                            <li>Brotli compression</li>
                            <li>HTTP/2 & HTTP/3</li>
                        </ul>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                            </svg>
                        </div>
                        <h3>AWS Certificate Manager</h3>
                        <p>Free SSL/TLS certificates with automatic renewal. Ensures all traffic is encrypted end-to-end.</p>
                        <ul class="service-features">
                            <li>Free certificates</li>
                            <li>Auto-renewal</li>
                            <li>TLS 1.3 support</li>
                        </ul>
                    </div>
                    <div class="service-card">
                        <div class="service-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                <circle cx="12" cy="10" r="3"/>
                            </svg>
                        </div>
                        <h3>Route 53</h3>
                        <p>Highly available and scalable DNS web service. Provides domain registration and routing.</p>
                        <ul class="service-features">
                            <li>100% SLA uptime</li>
                            <li>Latency-based routing</li>
                            <li>Health checks</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <section id="architecture" class="architecture">
            <div class="container">
                <h2 class="section-title">Architecture Overview</h2>
                <div class="architecture-diagram">
                    <pre class="diagram-ascii">
     Users (Global)
          |
          v
    +-----------+
    | Route 53  |  DNS Resolution
    +-----------+
          |
          v
    +-----------+        +------------+
    | CloudFront| -----> | ACM        |
    | (CDN)     |        | SSL Cert   |
    +-----------+        +------------+
          |
          | Origin Access Control
          v
    +-----------+
    | S3 Bucket |  Static Assets
    +-----------+
                    </pre>
                </div>
                <div class="architecture-details">
                    <div class="arch-step">
                        <span class="step-number">1</span>
                        <div class="step-content">
                            <h4>DNS Resolution</h4>
                            <p>Route 53 resolves domain to CloudFront distribution with ultra-low latency.</p>
                        </div>
                    </div>
                    <div class="arch-step">
                        <span class="step-number">2</span>
                        <div class="step-content">
                            <h4>Edge Caching</h4>
                            <p>CloudFront serves cached content from the nearest edge location.</p>
                        </div>
                    </div>
                    <div class="arch-step">
                        <span class="step-number">3</span>
                        <div class="step-content">
                            <h4>Origin Fetch</h4>
                            <p>On cache miss, CloudFront securely fetches from S3 using OAC.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="cta-section">
            <div class="container">
                <h2>Ready to Build Your Own?</h2>
                <p>Follow our step-by-step guide to deploy your static website on AWS</p>
                <a href="/contact.html" class="btn btn-primary btn-large">Get Started</a>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    <span class="logo-text">AWS<span class="accent">Site</span></span>
                    <p>Demonstrating AWS best practices for static website hosting.</p>
                </div>
                <div class="footer-links">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/about.html">About</a></li>
                        <li><a href="/contact.html">Contact</a></li>
                    </ul>
                </div>
                <div class="footer-links">
                    <h4>Resources</h4>
                    <ul>
                        <li><a href="https://aws.amazon.com/s3/">Amazon S3</a></li>
                        <li><a href="https://aws.amazon.com/cloudfront/">CloudFront</a></li>
                        <li><a href="https://aws.amazon.com/route53/">Route 53</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 AWS Training Project. Built with AWS.</p>
            </div>
        </div>
    </footer>

    <script src="/js/main.js"></script>
    <script src="/js/animations.js"></script>
</body>
</html>
```

### css/styles.css

```css
/* ============================================
   AWS Static Website - Main Stylesheet
   ============================================ */

/* CSS Custom Properties */
:root {
    /* Colors */
    --color-primary: #FF9900;
    --color-primary-dark: #EC7211;
    --color-secondary: #232F3E;
    --color-secondary-light: #37475A;
    --color-accent: #146EB4;
    --color-success: #1D8102;
    --color-error: #D13212;

    /* Neutrals */
    --color-white: #FFFFFF;
    --color-gray-50: #FAFAFA;
    --color-gray-100: #F5F5F5;
    --color-gray-200: #EEEEEE;
    --color-gray-300: #E0E0E0;
    --color-gray-400: #BDBDBD;
    --color-gray-500: #9E9E9E;
    --color-gray-600: #757575;
    --color-gray-700: #616161;
    --color-gray-800: #424242;
    --color-gray-900: #212121;

    /* Typography */
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    --font-size-4xl: 2.25rem;
    --font-size-5xl: 3rem;

    /* Spacing */
    --spacing-1: 0.25rem;
    --spacing-2: 0.5rem;
    --spacing-3: 0.75rem;
    --spacing-4: 1rem;
    --spacing-5: 1.25rem;
    --spacing-6: 1.5rem;
    --spacing-8: 2rem;
    --spacing-10: 2.5rem;
    --spacing-12: 3rem;
    --spacing-16: 4rem;
    --spacing-20: 5rem;

    /* Borders */
    --border-radius-sm: 0.25rem;
    --border-radius-md: 0.5rem;
    --border-radius-lg: 1rem;
    --border-radius-full: 9999px;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-base: 300ms ease;
    --transition-slow: 500ms ease;

    /* Z-index */
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal: 1050;
}

/* Reset & Base */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
    -webkit-text-size-adjust: 100%;
}

body {
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    line-height: 1.6;
    color: var(--color-gray-800);
    background-color: var(--color-white);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Container */
.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-6);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.2;
    color: var(--color-secondary);
}

h1 { font-size: var(--font-size-5xl); }
h2 { font-size: var(--font-size-4xl); }
h3 { font-size: var(--font-size-2xl); }
h4 { font-size: var(--font-size-xl); }

p {
    margin-bottom: var(--spacing-4);
}

a {
    color: var(--color-accent);
    text-decoration: none;
    transition: color var(--transition-fast);
}

a:hover {
    color: var(--color-primary);
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-3) var(--spacing-6);
    font-size: var(--font-size-base);
    font-weight: 500;
    border-radius: var(--border-radius-md);
    border: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    text-decoration: none;
}

.btn-primary {
    background-color: var(--color-primary);
    color: var(--color-secondary);
}

.btn-primary:hover {
    background-color: var(--color-primary-dark);
    color: var(--color-secondary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-secondary {
    background-color: transparent;
    color: var(--color-white);
    border-color: var(--color-white);
}

.btn-secondary:hover {
    background-color: var(--color-white);
    color: var(--color-secondary);
}

.btn-large {
    padding: var(--spacing-4) var(--spacing-8);
    font-size: var(--font-size-lg);
}

/* Header & Navigation */
.header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background-color: rgba(35, 47, 62, 0.95);
    backdrop-filter: blur(10px);
    z-index: var(--z-fixed);
    transition: background-color var(--transition-base);
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 70px;
}

.logo {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--color-white);
    text-decoration: none;
}

.logo .accent {
    color: var(--color-primary);
}

.nav-menu {
    display: flex;
    gap: var(--spacing-8);
    list-style: none;
}

.nav-link {
    color: var(--color-gray-300);
    font-weight: 500;
    transition: color var(--transition-fast);
}

.nav-link:hover,
.nav-link.active {
    color: var(--color-primary);
}

.mobile-menu-btn {
    display: none;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: none;
    cursor: pointer;
    padding: var(--spacing-2);
}

.mobile-menu-btn span {
    display: block;
    width: 25px;
    height: 2px;
    background-color: var(--color-white);
    transition: all var(--transition-fast);
}

/* Hero Section */
.hero {
    min-height: 100vh;
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, var(--color-secondary) 0%, #1a252f 50%, #0d1117 100%);
    padding-top: 70px;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 70%, rgba(255, 153, 0, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 70% 30%, rgba(20, 110, 180, 0.1) 0%, transparent 50%);
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 800px;
}

.hero-title {
    font-size: clamp(2.5rem, 5vw, 4rem);
    color: var(--color-white);
    margin-bottom: var(--spacing-6);
}

.gradient-text {
    background: linear-gradient(135deg, var(--color-primary) 0%, #FFD700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-description {
    font-size: var(--font-size-xl);
    color: var(--color-gray-400);
    margin-bottom: var(--spacing-8);
    max-width: 600px;
}

.hero-buttons {
    display: flex;
    gap: var(--spacing-4);
    margin-bottom: var(--spacing-12);
}

.hero-stats {
    display: flex;
    gap: var(--spacing-12);
}

.stat {
    display: flex;
    flex-direction: column;
}

.stat-value {
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--color-primary);
}

.stat-label {
    font-size: var(--font-size-sm);
    color: var(--color-gray-500);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Sections */
.section-title {
    text-align: center;
    margin-bottom: var(--spacing-4);
}

.section-subtitle {
    text-align: center;
    color: var(--color-gray-600);
    max-width: 600px;
    margin: 0 auto var(--spacing-12);
}

/* Services Section */
.services {
    padding: var(--spacing-20) 0;
    background-color: var(--color-gray-50);
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-8);
}

.service-card {
    background-color: var(--color-white);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-8);
    box-shadow: var(--shadow-md);
    transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.service-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-xl);
}

.service-icon {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    border-radius: var(--border-radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--spacing-4);
}

.service-icon svg {
    width: 24px;
    height: 24px;
    stroke: var(--color-white);
}

.service-card h3 {
    margin-bottom: var(--spacing-3);
}

.service-card p {
    color: var(--color-gray-600);
    margin-bottom: var(--spacing-4);
}

.service-features {
    list-style: none;
}

.service-features li {
    padding: var(--spacing-2) 0;
    color: var(--color-gray-700);
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
}

.service-features li::before {
    content: '✓';
    color: var(--color-success);
    font-weight: bold;
}

/* Architecture Section */
.architecture {
    padding: var(--spacing-20) 0;
}

.architecture-diagram {
    background-color: var(--color-secondary);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-8);
    margin-bottom: var(--spacing-12);
    overflow-x: auto;
}

.diagram-ascii {
    color: var(--color-primary);
    font-family: 'Courier New', monospace;
    font-size: var(--font-size-sm);
    line-height: 1.4;
    text-align: center;
    white-space: pre;
}

.architecture-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-6);
}

.arch-step {
    display: flex;
    gap: var(--spacing-4);
    align-items: flex-start;
}

.step-number {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    background-color: var(--color-primary);
    color: var(--color-secondary);
    border-radius: var(--border-radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.step-content h4 {
    margin-bottom: var(--spacing-2);
}

.step-content p {
    color: var(--color-gray-600);
    margin-bottom: 0;
}

/* CTA Section */
.cta-section {
    padding: var(--spacing-20) 0;
    background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-secondary-light) 100%);
    text-align: center;
}

.cta-section h2 {
    color: var(--color-white);
    margin-bottom: var(--spacing-4);
}

.cta-section p {
    color: var(--color-gray-400);
    margin-bottom: var(--spacing-8);
}

/* Footer */
.footer {
    background-color: var(--color-gray-900);
    color: var(--color-gray-400);
    padding: var(--spacing-16) 0 var(--spacing-8);
}

.footer-content {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: var(--spacing-12);
    margin-bottom: var(--spacing-12);
}

.footer-brand .logo-text {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--color-white);
}

.footer-brand p {
    margin-top: var(--spacing-4);
    color: var(--color-gray-500);
}

.footer-links h4 {
    color: var(--color-white);
    margin-bottom: var(--spacing-4);
}

.footer-links ul {
    list-style: none;
}

.footer-links li {
    margin-bottom: var(--spacing-2);
}

.footer-links a {
    color: var(--color-gray-500);
    transition: color var(--transition-fast);
}

.footer-links a:hover {
    color: var(--color-primary);
}

.footer-bottom {
    border-top: 1px solid var(--color-gray-800);
    padding-top: var(--spacing-8);
    text-align: center;
}

.footer-bottom p {
    margin-bottom: 0;
    color: var(--color-gray-600);
}
```

### css/responsive.css

```css
/* ============================================
   Responsive Styles
   ============================================ */

/* Tablets and smaller desktops */
@media (max-width: 1024px) {
    .hero-stats {
        gap: var(--spacing-8);
    }

    .footer-content {
        grid-template-columns: 1fr 1fr;
        gap: var(--spacing-8);
    }

    .footer-brand {
        grid-column: 1 / -1;
    }
}

/* Tablets */
@media (max-width: 768px) {
    .nav-menu {
        display: none;
        position: absolute;
        top: 70px;
        left: 0;
        right: 0;
        flex-direction: column;
        background-color: var(--color-secondary);
        padding: var(--spacing-6);
        gap: var(--spacing-4);
    }

    .nav-menu.active {
        display: flex;
    }

    .mobile-menu-btn {
        display: flex;
    }

    .mobile-menu-btn.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }

    .mobile-menu-btn.active span:nth-child(2) {
        opacity: 0;
    }

    .mobile-menu-btn.active span:nth-child(3) {
        transform: rotate(-45deg) translate(5px, -5px);
    }

    .hero-content {
        text-align: center;
    }

    .hero-description {
        margin-left: auto;
        margin-right: auto;
    }

    .hero-buttons {
        justify-content: center;
        flex-wrap: wrap;
    }

    .hero-stats {
        justify-content: center;
        flex-wrap: wrap;
        gap: var(--spacing-6);
    }

    .stat {
        align-items: center;
    }

    .services-grid {
        grid-template-columns: 1fr;
    }

    .diagram-ascii {
        font-size: var(--font-size-xs);
    }

    .footer-content {
        grid-template-columns: 1fr;
        text-align: center;
    }
}

/* Mobile phones */
@media (max-width: 480px) {
    :root {
        --font-size-5xl: 2.25rem;
        --font-size-4xl: 1.875rem;
        --font-size-3xl: 1.5rem;
    }

    .container {
        padding: 0 var(--spacing-4);
    }

    .hero {
        padding-top: 80px;
    }

    .hero-buttons {
        flex-direction: column;
        width: 100%;
    }

    .btn {
        width: 100%;
    }

    .service-card {
        padding: var(--spacing-6);
    }

    .cta-section {
        padding: var(--spacing-12) 0;
    }
}

/* Print styles */
@media print {
    .header,
    .mobile-menu-btn,
    .hero-buttons,
    .cta-section {
        display: none;
    }

    .hero {
        min-height: auto;
        padding: var(--spacing-8) 0;
        background: none;
        color: var(--color-gray-900);
    }

    .hero-title,
    .gradient-text {
        color: var(--color-gray-900);
        -webkit-text-fill-color: initial;
    }

    .hero-description {
        color: var(--color-gray-700);
    }

    .services {
        background: none;
    }

    .service-card {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid var(--color-gray-300);
    }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }

    html {
        scroll-behavior: auto;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --color-gray-50: #1a1a1a;
        --color-gray-100: #2d2d2d;
        --color-white: #0d0d0d;
    }

    body {
        background-color: #0d0d0d;
        color: var(--color-gray-300);
    }

    .service-card {
        background-color: #1a1a1a;
    }
}
```

### js/main.js

```javascript
/**
 * AWS Static Website - Main JavaScript
 * Handles navigation, smooth scrolling, and user interactions
 */

'use strict';

// DOM Elements
const header = document.querySelector('.header');
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navMenu = document.querySelector('.nav-menu');
const navLinks = document.querySelectorAll('.nav-link');

// Mobile menu toggle
function toggleMobileMenu() {
    mobileMenuBtn.classList.toggle('active');
    navMenu.classList.toggle('active');
    document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
}

// Close mobile menu when clicking a link
function closeMobileMenu() {
    mobileMenuBtn.classList.remove('active');
    navMenu.classList.remove('active');
    document.body.style.overflow = '';
}

// Header scroll effect
function handleScroll() {
    if (window.scrollY > 100) {
        header.style.backgroundColor = 'rgba(35, 47, 62, 0.98)';
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.3)';
    } else {
        header.style.backgroundColor = 'rgba(35, 47, 62, 0.95)';
        header.style.boxShadow = 'none';
    }
}

// Active navigation link based on scroll position
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const scrollPosition = window.scrollY + 100;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');

        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}` ||
                    link.getAttribute('href') === `/#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}

// Smooth scroll for anchor links
function handleAnchorClick(e) {
    const href = this.getAttribute('href');

    if (href.startsWith('#') || href.startsWith('/#')) {
        e.preventDefault();
        const targetId = href.replace('/', '').replace('#', '');
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            const headerHeight = header.offsetHeight;
            const targetPosition = targetElement.offsetTop - headerHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });

            closeMobileMenu();
        }
    }
}

// Initialize event listeners
function init() {
    // Mobile menu
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    }

    // Navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', handleAnchorClick);
    });

    // All anchor links with hash
    document.querySelectorAll('a[href^="#"], a[href^="/#"]').forEach(anchor => {
        anchor.addEventListener('click', handleAnchorClick);
    });

    // Scroll events
    window.addEventListener('scroll', () => {
        handleScroll();
        updateActiveNavLink();
    });

    // Close mobile menu on resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });

    // Initial calls
    handleScroll();
    updateActiveNavLink();
}

// Run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { toggleMobileMenu, handleScroll, updateActiveNavLink };
}
```

### js/animations.js

```javascript
/**
 * AWS Static Website - Animation Effects
 * Handles scroll-triggered animations and visual effects
 */

'use strict';

// Animation configuration
const animationConfig = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

// Elements to animate
const animatableSelectors = [
    '.service-card',
    '.arch-step',
    '.hero-stats .stat',
    '.section-title',
    '.section-subtitle'
];

// Create intersection observer for scroll animations
function createScrollObserver() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, animationConfig);

    return observer;
}

// Initialize scroll animations
function initScrollAnimations() {
    const observer = createScrollObserver();

    animatableSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach((element, index) => {
            // Set initial state
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;

            observer.observe(element);
        });
    });
}

// Add animate-in styles
function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }

        .hero-title {
            animation: fadeInUp 0.8s ease forwards;
        }

        .hero-description {
            animation: fadeInUp 0.8s ease 0.2s forwards;
            opacity: 0;
        }

        .hero-buttons {
            animation: fadeInUp 0.8s ease 0.4s forwards;
            opacity: 0;
        }

        .btn:hover {
            animation: pulse 0.3s ease;
        }
    `;
    document.head.appendChild(style);
}

// Parallax effect for hero section
function initParallax() {
    const hero = document.querySelector('.hero');

    if (!hero) return;

    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const rate = scrolled * 0.3;

        if (scrolled < window.innerHeight) {
            hero.style.backgroundPosition = `center ${rate}px`;
        }
    });
}

// Counter animation for stats
function animateCounters() {
    const statValues = document.querySelectorAll('.stat-value');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalValue = target.textContent;

                // Handle percentage values
                if (finalValue.includes('%')) {
                    animateNumber(target, 0, parseFloat(finalValue), '%', 2000);
                }
                // Handle millisecond values
                else if (finalValue.includes('ms')) {
                    animateNumber(target, 0, parseInt(finalValue), 'ms', 1500, '<');
                }
                // Handle number values
                else if (/^\d+\+?$/.test(finalValue)) {
                    const num = parseInt(finalValue);
                    animateNumber(target, 0, num, '+', 2000);
                }

                observer.unobserve(target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(stat => observer.observe(stat));
}

// Animate number from start to end
function animateNumber(element, start, end, suffix, duration, prefix = '') {
    const startTime = performance.now();
    const originalText = element.textContent;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = easeOutQuart(progress);
        const current = Math.floor(start + (end - start) * easeProgress);

        element.textContent = `${prefix}${current}${suffix}`;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = originalText;
        }
    }

    requestAnimationFrame(update);
}

// Easing function
function easeOutQuart(x) {
    return 1 - Math.pow(1 - x, 4);
}

// Typing effect for hero title
function initTypingEffect() {
    const gradientText = document.querySelector('.gradient-text');
    if (!gradientText) return;

    const text = gradientText.textContent;
    gradientText.textContent = '';
    gradientText.style.borderRight = '2px solid var(--color-primary)';

    let index = 0;

    function type() {
        if (index < text.length) {
            gradientText.textContent += text.charAt(index);
            index++;
            setTimeout(type, 100);
        } else {
            gradientText.style.borderRight = 'none';
        }
    }

    // Start typing after a delay
    setTimeout(type, 800);
}

// Initialize all animations
function init() {
    // Check for reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    addAnimationStyles();
    initScrollAnimations();
    initParallax();
    animateCounters();
    // initTypingEffect(); // Uncomment to enable typing effect
}

// Run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
```

### error.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | AWS Hosted Website</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #232f3e 0%, #1a252f 50%, #0d1117 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            padding: 2rem;
        }

        .error-container {
            max-width: 500px;
        }

        .error-code {
            font-size: 8rem;
            font-weight: 700;
            color: #ff9900;
            line-height: 1;
            text-shadow: 0 4px 20px rgba(255, 153, 0, 0.3);
        }

        h1 {
            font-size: 2rem;
            margin: 1rem 0;
        }

        p {
            color: #9e9e9e;
            margin-bottom: 2rem;
            line-height: 1.6;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem 2rem;
            background-color: #ff9900;
            color: #232f3e;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn:hover {
            background-color: #ec7211;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 153, 0, 0.4);
        }

        .illustration {
            margin-bottom: 2rem;
        }

        .illustration svg {
            width: 200px;
            height: 200px;
        }

        .links {
            margin-top: 3rem;
            display: flex;
            gap: 2rem;
            justify-content: center;
        }

        .links a {
            color: #9e9e9e;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .links a:hover {
            color: #ff9900;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="illustration">
            <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="100" cy="100" r="80" stroke="#ff9900" stroke-width="4" stroke-dasharray="10 5"/>
                <path d="M60 80 L100 120 L140 80" stroke="#ff9900" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="70" cy="70" r="8" fill="#ff9900"/>
                <circle cx="130" cy="70" r="8" fill="#ff9900"/>
            </svg>
        </div>

        <div class="error-code">404</div>

        <h1>Page Not Found</h1>

        <p>
            Oops! The page you're looking for seems to have wandered off into the cloud.
            It might have been moved, deleted, or never existed in the first place.
        </p>

        <a href="/" class="btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12l9-9 9 9M5 10v10a1 1 0 001 1h3a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1h3a1 1 0 001-1V10"/>
            </svg>
            Back to Home
        </a>

        <div class="links">
            <a href="/about.html">About</a>
            <a href="/contact.html">Contact</a>
        </div>
    </div>
</body>
</html>
```

---

## Custom Domain Setup

### Step 1: Register Domain (if needed)

```bash
# Check domain availability
aws route53domains check-domain-availability \
    --domain-name example.com

# Register domain (requires manual confirmation)
aws route53domains register-domain \
    --domain-name example.com \
    --duration-in-years 1 \
    --admin-contact file://contact.json \
    --registrant-contact file://contact.json \
    --tech-contact file://contact.json \
    --auto-renew
```

### Step 2: Create Hosted Zone

```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name example.com \
    --caller-reference "$(date +%s)" \
    --hosted-zone-config Comment="Static website"

# Get hosted zone ID and name servers
aws route53 list-hosted-zones-by-name \
    --dns-name example.com \
    --query 'HostedZones[0]'
```

### Step 3: Configure DNS Records

```bash
# Create alias record for www
cat > dns-record.json << 'EOF'
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "www.example.com",
            "Type": "A",
            "AliasTarget": {
                "HostedZoneId": "Z2FDTNDATAQYW2",
                "DNSName": "d1234abcd.cloudfront.net",
                "EvaluateTargetHealth": false
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890ABC \
    --change-batch file://dns-record.json
```

---

## SSL/TLS Certificate Configuration

### Step 1: Request Certificate

```bash
# Request certificate in us-east-1 (required for CloudFront)
aws acm request-certificate \
    --domain-name example.com \
    --subject-alternative-names "*.example.com" \
    --validation-method DNS \
    --region us-east-1

# Get certificate ARN
CERT_ARN=$(aws acm list-certificates \
    --region us-east-1 \
    --query "CertificateSummaryList[?DomainName=='example.com'].CertificateArn" \
    --output text)
```

### Step 2: DNS Validation

```bash
# Get DNS validation records
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region us-east-1 \
    --query 'Certificate.DomainValidationOptions'

# Create validation records in Route 53
# (Automatic if using Route 53, otherwise add records manually)
```

### Step 3: Update CloudFront Distribution

```bash
# Get current distribution config
aws cloudfront get-distribution-config \
    --id E1234567890ABC > dist-config.json

# Extract ETag for update
ETAG=$(cat dist-config.json | jq -r '.ETag')

# Modify configuration to add aliases and certificate
# Update ViewerCertificate section with ACM certificate ARN
# Add Aliases array with domain names

aws cloudfront update-distribution \
    --id E1234567890ABC \
    --if-match $ETAG \
    --distribution-config file://updated-config.json
```

---

## Testing and Validation

### Validation Checklist

```bash
#!/bin/bash
# validation-script.sh

CLOUDFRONT_URL="https://d1234abcd.cloudfront.net"
CUSTOM_DOMAIN="https://www.example.com"

echo "=== Static Website Validation ==="

# Test HTTP to HTTPS redirect
echo -n "HTTP redirect: "
REDIRECT=$(curl -s -o /dev/null -w "%{redirect_url}" http://d1234abcd.cloudfront.net 2>/dev/null)
if [[ $REDIRECT == https* ]]; then echo "PASS"; else echo "FAIL"; fi

# Test HTTPS connection
echo -n "HTTPS connection: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $CLOUDFRONT_URL)
if [[ $HTTP_CODE == "200" ]]; then echo "PASS"; else echo "FAIL ($HTTP_CODE)"; fi

# Test index.html
echo -n "Index page: "
CONTENT=$(curl -s $CLOUDFRONT_URL | head -1)
if [[ $CONTENT == *"DOCTYPE"* ]]; then echo "PASS"; else echo "FAIL"; fi

# Test 404 page
echo -n "404 error page: "
HTTP_404=$(curl -s -o /dev/null -w "%{http_code}" "$CLOUDFRONT_URL/nonexistent")
if [[ $HTTP_404 == "404" ]]; then echo "PASS"; else echo "FAIL ($HTTP_404)"; fi

# Test SSL certificate
echo -n "SSL certificate: "
SSL_VALID=$(curl -s -o /dev/null -w "%{ssl_verify_result}" $CLOUDFRONT_URL)
if [[ $SSL_VALID == "0" ]]; then echo "PASS"; else echo "FAIL"; fi

# Test response headers
echo -n "Security headers: "
HEADERS=$(curl -sI $CLOUDFRONT_URL | grep -i "strict-transport-security")
if [[ -n $HEADERS ]]; then echo "PASS"; else echo "WARN (HSTS not set)"; fi

# Test compression
echo -n "Gzip compression: "
ENCODING=$(curl -sI -H "Accept-Encoding: gzip" $CLOUDFRONT_URL | grep -i "content-encoding")
if [[ $ENCODING == *"gzip"* ]]; then echo "PASS"; else echo "FAIL"; fi

echo "=== Validation Complete ==="
```

### Performance Testing

```bash
# Test latency from multiple regions
for region in us-east-1 eu-west-1 ap-southeast-1; do
    echo "Testing from $region..."
    aws cloudfront get-distribution \
        --id E1234567890ABC \
        --query 'Distribution.DomainName' \
        --output text
done

# Load testing with Apache Bench
ab -n 1000 -c 50 https://d1234abcd.cloudfront.net/

# Check cache hit ratio in CloudFront
aws cloudfront get-distribution \
    --id E1234567890ABC \
    --query 'Distribution.ActiveTrustedSigners'
```

---

## Cost Analysis

### Monthly Cost Breakdown

| Service | Usage | Cost (USD) |
|---------|-------|------------|
| **S3 Storage** | 100 MB | $0.00 (Free Tier) |
| **S3 Requests** | 10,000 GET/month | $0.00 (Free Tier) |
| **CloudFront Data Transfer** | 10 GB/month | $0.00 (Free Tier first 1TB) |
| **CloudFront Requests** | 100,000/month | $0.00 (Free Tier) |
| **Route 53 Hosted Zone** | 1 zone | $0.50 |
| **Route 53 Queries** | 100,000/month | $0.00 (first 1M free) |
| **ACM Certificate** | 1 certificate | $0.00 (Free) |
| **Total (Free Tier)** | | **$0.50/month** |
| **Total (After Free Tier)** | | **$1.50-$5.00/month** |

### Cost Optimization Tips

1. **Use CloudFront Price Class**: PriceClass_100 for US/EU only
2. **Enable compression**: Reduces data transfer costs
3. **Set appropriate cache TTLs**: Reduce origin requests
4. **Use S3 Intelligent-Tiering**: For infrequently accessed content
5. **Monitor with Cost Explorer**: Set up billing alerts

---

## Troubleshooting Guide

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Access Denied (403) | Bucket policy misconfigured | Verify CloudFront OAC and bucket policy |
| SSL Certificate Pending | DNS validation incomplete | Add CNAME records for validation |
| Old Content Displayed | CloudFront cache | Create invalidation: `aws cloudfront create-invalidation` |
| Slow Initial Load | Cold cache | Pre-warm cache or reduce TTL during updates |
| Custom Domain Not Working | DNS propagation | Wait 24-48 hours, check NS records |
| 504 Gateway Timeout | Origin not responding | Check S3 bucket region and CloudFront origin settings |

### Debug Commands

```bash
# Check S3 bucket configuration
aws s3api get-bucket-website --bucket $BUCKET_NAME
aws s3api get-bucket-policy --bucket $BUCKET_NAME

# Check CloudFront distribution status
aws cloudfront get-distribution --id $DIST_ID --query 'Distribution.Status'

# View CloudFront error logs
aws logs filter-log-events \
    --log-group-name /aws/cloudfront/$DIST_ID \
    --filter-pattern "ERROR"

# Test origin directly
curl -v "https://$BUCKET_NAME.s3.amazonaws.com/index.html"

# Check DNS resolution
dig www.example.com
nslookup www.example.com

# Verify SSL certificate
openssl s_client -connect www.example.com:443 -servername www.example.com
```

---

## Next Steps

After completing this project, consider:

1. **Add CI/CD Pipeline**: Automate deployments with CodePipeline
2. **Enable CloudFront Functions**: URL rewrites, A/B testing
3. **Add Analytics**: CloudFront logs + Athena analysis
4. **Implement WAF**: Web Application Firewall for security
5. **Create Contact Form Backend**: Lambda + API Gateway + SES

---

**Congratulations!** You have successfully deployed a production-ready static website on AWS with global CDN distribution, custom domain, and SSL/TLS encryption.

[Back to Project Overview](./README.md) | [Next: Web Application Project](../02-web-application/implementation.md)
