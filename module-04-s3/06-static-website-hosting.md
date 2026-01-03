# 06 - Static Website Hosting

## Introduction

Amazon S3 can host static websites, serving HTML, CSS, JavaScript, images, and other static content directly to web browsers. This is a cost-effective solution for hosting websites that don't require server-side processing.

---

## Static Website Hosting Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      S3 STATIC WEBSITE HOSTING                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  What S3 Can Host (Static):         What S3 Cannot Host (Dynamic):         │
│  ─────────────────────────           ─────────────────────────────          │
│  ✓ HTML pages                        ✗ Server-side scripts (PHP, Python)   │
│  ✓ CSS stylesheets                   ✗ Database connections                │
│  ✓ JavaScript (client-side)          ✗ Session management                  │
│  ✓ Images (PNG, JPG, SVG)            ✗ Real-time data processing           │
│  ✓ Videos and audio                                                        │
│  ✓ PDF and documents                 Can use with:                         │
│  ✓ Single Page Apps (React, Vue)     • API Gateway + Lambda for APIs       │
│  ✓ Web fonts                         • Cognito for authentication          │
│                                      • CloudFront for CDN                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Options

### Option 1: Basic S3 Website Hosting

```
┌─────────┐                ┌─────────────────┐
│  Users  │───── HTTP ────▶│   S3 Bucket     │
│         │                │  (Website)      │
└─────────┘                └─────────────────┘

URL: http://bucket-name.s3-website-region.amazonaws.com

Limitations:
• HTTP only (no HTTPS)
• No custom domain without Route 53
• No edge caching
```

### Option 2: S3 + CloudFront (Recommended)

```
┌─────────┐    ┌────────────┐    ┌─────────────┐
│  Users  │───▶│ CloudFront │───▶│  S3 Bucket  │
│         │    │    CDN     │    │  (Origin)   │
└─────────┘    └────────────┘    └─────────────┘
                     │
              ┌──────┴──────┐
              │  Route 53   │
              │ (DNS/HTTPS) │
              └─────────────┘

Benefits:
• HTTPS support
• Custom domain
• Global edge caching
• DDoS protection
• Better performance
```

### Option 3: Full Stack Serverless

```
┌─────────┐    ┌────────────┐    ┌─────────────┐
│  Users  │───▶│ CloudFront │───▶│  S3 Bucket  │
└─────────┘    └─────┬──────┘    │  (Static)   │
                     │           └─────────────┘
                     │
              ┌──────┴──────┐    ┌─────────────┐    ┌──────────┐
              │ API Gateway │───▶│   Lambda    │───▶│ DynamoDB │
              └─────────────┘    │ (Functions) │    └──────────┘
                                 └─────────────┘
```

---

## Enabling Static Website Hosting

### Step 1: Create and Configure Bucket

```bash
# Create bucket (name should match your domain for custom domains)
aws s3 mb s3://www.example.com --region us-east-1

# Enable static website hosting
aws s3 website s3://www.example.com \
    --index-document index.html \
    --error-document error.html
```

### Step 2: Configure Bucket for Public Access

```bash
# Disable Block Public Access (for website hosting)
aws s3api put-public-access-block \
    --bucket www.example.com \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Add bucket policy for public read
cat > bucket-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::www.example.com/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket www.example.com \
    --policy file://bucket-policy.json
```

### Step 3: Upload Website Content

```bash
# Upload all files
aws s3 sync ./website-folder s3://www.example.com/

# Upload with correct content types
aws s3 cp index.html s3://www.example.com/ --content-type "text/html"
aws s3 cp styles.css s3://www.example.com/ --content-type "text/css"
aws s3 cp script.js s3://www.example.com/ --content-type "application/javascript"

# Sync with automatic content type detection
aws s3 sync ./website-folder s3://www.example.com/ \
    --content-type "text/html" --exclude "*" --include "*.html"
```

### Python (Boto3)

```python
import boto3
import json
import mimetypes
import os

s3_client = boto3.client('s3')

def create_website_bucket(bucket_name, region='us-east-1'):
    """Create and configure an S3 bucket for static website hosting."""

    # Create bucket
    if region == 'us-east-1':
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    # Disable Block Public Access
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )

    # Enable website hosting
    s3_client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'error.html'}
        }
    )

    # Add public read policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(policy)
    )

    website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
    return website_url


def upload_website(bucket_name, source_dir):
    """Upload a website directory to S3 with correct content types."""

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, source_dir)
            s3_key = relative_path.replace('\\', '/')  # Windows compatibility

            # Determine content type
            content_type, _ = mimetypes.guess_type(file)
            if content_type is None:
                content_type = 'application/octet-stream'

            # Upload file
            s3_client.upload_file(
                local_path,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            print(f"Uploaded: {s3_key}")


# Usage
bucket = 'my-website-bucket-unique-name'
url = create_website_bucket(bucket)
print(f"Website URL: {url}")

upload_website(bucket, './my-website-folder')
```

---

## Website Endpoint Formats

```
Website Endpoint Formats by Region:
────────────────────────────────────────────────────────────────────────────

Dash format (older regions):
http://bucket-name.s3-website-region.amazonaws.com
Examples:
• http://my-site.s3-website-us-east-1.amazonaws.com
• http://my-site.s3-website-eu-west-1.amazonaws.com

Dot format (newer regions):
http://bucket-name.s3-website.region.amazonaws.com
Examples:
• http://my-site.s3-website.us-east-2.amazonaws.com
• http://my-site.s3-website.ap-south-1.amazonaws.com

REST API Endpoint (NOT for website hosting):
https://bucket-name.s3.region.amazonaws.com
This returns XML for directory listing, not index.html!
```

---

## Index and Error Documents

### Index Document

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My S3 Website</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Welcome to My Website</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about.html">About</a>
            <a href="/contact.html">Contact</a>
        </nav>
    </header>
    <main>
        <p>This website is hosted on Amazon S3!</p>
    </main>
    <script src="script.js"></script>
</body>
</html>
```

### Error Document

```html
<!-- error.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .error-container {
            text-align: center;
            padding: 40px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #e74c3c; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">Return to Home</a>
    </div>
</body>
</html>
```

### Custom Error Pages per Error Code

```bash
# Configure routing rules for custom error handling
aws s3api put-bucket-website \
    --bucket www.example.com \
    --website-configuration '{
        "IndexDocument": {"Suffix": "index.html"},
        "ErrorDocument": {"Key": "error.html"},
        "RoutingRules": [
            {
                "Condition": {
                    "HttpErrorCodeReturnedEquals": "404"
                },
                "Redirect": {
                    "ReplaceKeyWith": "404.html"
                }
            },
            {
                "Condition": {
                    "HttpErrorCodeReturnedEquals": "403"
                },
                "Redirect": {
                    "ReplaceKeyWith": "403.html"
                }
            }
        ]
    }'
```

---

## Routing Rules and Redirects

### Redirect All Requests

```bash
# Redirect all requests to another domain
aws s3api put-bucket-website \
    --bucket old-domain.com \
    --website-configuration '{
        "RedirectAllRequestsTo": {
            "HostName": "new-domain.com",
            "Protocol": "https"
        }
    }'
```

### Conditional Redirects

```json
{
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "error.html"},
    "RoutingRules": [
        {
            "Condition": {
                "KeyPrefixEquals": "docs/"
            },
            "Redirect": {
                "ReplaceKeyPrefixWith": "documents/"
            }
        },
        {
            "Condition": {
                "KeyPrefixEquals": "images/"
            },
            "Redirect": {
                "HostName": "cdn.example.com",
                "Protocol": "https"
            }
        },
        {
            "Condition": {
                "HttpErrorCodeReturnedEquals": "404",
                "KeyPrefixEquals": "blog/"
            },
            "Redirect": {
                "ReplaceKeyWith": "blog/not-found.html"
            }
        }
    ]
}
```

```python
import boto3

s3_client = boto3.client('s3')

# Set up routing rules
s3_client.put_bucket_website(
    Bucket='www.example.com',
    WebsiteConfiguration={
        'IndexDocument': {'Suffix': 'index.html'},
        'ErrorDocument': {'Key': 'error.html'},
        'RoutingRules': [
            {
                'Condition': {
                    'KeyPrefixEquals': 'old-path/'
                },
                'Redirect': {
                    'ReplaceKeyPrefixWith': 'new-path/',
                    'HttpRedirectCode': '301'
                }
            }
        ]
    }
)
```

---

## Custom Domains with Route 53

### Setup Steps

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   CUSTOM DOMAIN SETUP (HTTP Only)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Requirements:                                                              │
│  1. Bucket name must match domain name exactly                              │
│     - Domain: www.example.com                                               │
│     - Bucket: www.example.com                                               │
│                                                                             │
│  2. Configure Route 53 alias record                                         │
│     - Record name: www.example.com                                          │
│     - Record type: A (Alias)                                                │
│     - Target: S3 website endpoint                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Creating Route 53 Alias Record

```bash
# Get hosted zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones-by-name \
    --dns-name "example.com" \
    --query "HostedZones[0].Id" \
    --output text | sed 's/\/hostedzone\///')

# Create alias record
aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "www.example.com",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": "Z3AQBSTGFYJSTF",
                        "DNSName": "s3-website-us-east-1.amazonaws.com",
                        "EvaluateTargetHealth": false
                    }
                }
            }
        ]
    }'
```

### S3 Website Endpoint Hosted Zone IDs

```
Region                  Hosted Zone ID      Website Endpoint
─────────────────────────────────────────────────────────────────────────────
us-east-1               Z3AQBSTGFYJSTF      s3-website-us-east-1.amazonaws.com
us-east-2               Z2O1EMRO9K5GLX      s3-website.us-east-2.amazonaws.com
us-west-1               Z2F56UZL2M1ACD      s3-website-us-west-1.amazonaws.com
us-west-2               Z3BJ6K6RIION7M      s3-website-us-west-2.amazonaws.com
eu-west-1               Z1BKCTXD74EZPE      s3-website-eu-west-1.amazonaws.com
eu-central-1            Z21DNDUVLTQW6Q      s3-website.eu-central-1.amazonaws.com
ap-southeast-1          Z3O0J2DXBE1FTB      s3-website-ap-southeast-1.amazonaws.com
ap-northeast-1          Z2M4EHUR26P7ZW      s3-website-ap-northeast-1.amazonaws.com
```

---

## HTTPS with CloudFront

### Complete CloudFront + S3 Setup

```bash
# Step 1: Create S3 bucket (no public access needed with OAC)
aws s3 mb s3://www.example.com-origin

# Step 2: Upload website content
aws s3 sync ./website s3://www.example.com-origin/

# Step 3: Create Origin Access Control
OAC_ID=$(aws cloudfront create-origin-access-control \
    --origin-access-control-config '{
        "Name": "S3-OAC",
        "Description": "OAC for S3 website",
        "SigningProtocol": "sigv4",
        "SigningBehavior": "always",
        "OriginAccessControlOriginType": "s3"
    }' \
    --query 'OriginAccessControl.Id' \
    --output text)

# Step 4: Request SSL certificate (must be in us-east-1 for CloudFront)
CERT_ARN=$(aws acm request-certificate \
    --region us-east-1 \
    --domain-name "example.com" \
    --subject-alternative-names "www.example.com" \
    --validation-method DNS \
    --query 'CertificateArn' \
    --output text)

# Step 5: Create CloudFront distribution
aws cloudfront create-distribution \
    --distribution-config '{
        "CallerReference": "my-website-'$(date +%s)'",
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "S3Origin",
                    "DomainName": "www.example.com-origin.s3.us-east-1.amazonaws.com",
                    "S3OriginConfig": {
                        "OriginAccessIdentity": ""
                    },
                    "OriginAccessControlId": "'$OAC_ID'"
                }
            ]
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "S3Origin",
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            },
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            },
            "ForwardedValues": {
                "QueryString": false,
                "Cookies": {"Forward": "none"}
            },
            "MinTTL": 0,
            "DefaultTTL": 86400,
            "MaxTTL": 31536000,
            "Compress": true
        },
        "DefaultRootObject": "index.html",
        "Enabled": true,
        "Aliases": {
            "Quantity": 2,
            "Items": ["example.com", "www.example.com"]
        },
        "ViewerCertificate": {
            "ACMCertificateArn": "'$CERT_ARN'",
            "SSLSupportMethod": "sni-only",
            "MinimumProtocolVersion": "TLSv1.2_2021"
        },
        "CustomErrorResponses": {
            "Quantity": 1,
            "Items": [
                {
                    "ErrorCode": 404,
                    "ResponsePagePath": "/error.html",
                    "ResponseCode": "404",
                    "ErrorCachingMinTTL": 300
                }
            ]
        }
    }'
```

### Python: Complete Setup Script

```python
import boto3
import json
import time

def setup_cloudfront_website(domain_name, bucket_name, region='us-east-1'):
    """Set up a complete S3 + CloudFront static website with HTTPS."""

    s3_client = boto3.client('s3', region_name=region)
    cf_client = boto3.client('cloudfront')
    acm_client = boto3.client('acm', region_name='us-east-1')  # ACM must be us-east-1

    # 1. Create S3 bucket (private - CloudFront will access via OAC)
    print(f"Creating bucket: {bucket_name}")
    if region == 'us-east-1':
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

    # 2. Block all public access (CloudFront uses OAC)
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )

    # 3. Create Origin Access Control
    print("Creating Origin Access Control...")
    oac_response = cf_client.create_origin_access_control(
        OriginAccessControlConfig={
            'Name': f'{bucket_name}-oac',
            'Description': f'OAC for {bucket_name}',
            'SigningProtocol': 'sigv4',
            'SigningBehavior': 'always',
            'OriginAccessControlOriginType': 's3'
        }
    )
    oac_id = oac_response['OriginAccessControl']['Id']

    # 4. Request ACM certificate
    print(f"Requesting SSL certificate for {domain_name}...")
    cert_response = acm_client.request_certificate(
        DomainName=domain_name,
        SubjectAlternativeNames=[f'www.{domain_name}'],
        ValidationMethod='DNS'
    )
    cert_arn = cert_response['CertificateArn']
    print(f"Certificate ARN: {cert_arn}")
    print("Please add DNS validation records and wait for certificate to be issued.")

    # 5. Create CloudFront distribution
    caller_reference = f'{bucket_name}-{int(time.time())}'
    s3_domain = f'{bucket_name}.s3.{region}.amazonaws.com'

    print("Creating CloudFront distribution...")
    dist_config = {
        'CallerReference': caller_reference,
        'Origins': {
            'Quantity': 1,
            'Items': [{
                'Id': 'S3Origin',
                'DomainName': s3_domain,
                'S3OriginConfig': {'OriginAccessIdentity': ''},
                'OriginAccessControlId': oac_id
            }]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3Origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']}
            },
            'Compress': True,
            'CachePolicyId': '658327ea-f89d-4fab-a63d-7e88639e58f6',  # CachingOptimized
        },
        'DefaultRootObject': 'index.html',
        'Enabled': True,
        'Comment': f'Distribution for {domain_name}'
    }

    dist_response = cf_client.create_distribution(DistributionConfig=dist_config)
    dist_id = dist_response['Distribution']['Id']
    cf_domain = dist_response['Distribution']['DomainName']

    # 6. Add bucket policy for CloudFront
    account_id = boto3.client('sts').get_caller_identity()['Account']
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {"Service": "cloudfront.amazonaws.com"},
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{account_id}:distribution/{dist_id}"
                }
            }
        }]
    }

    s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))

    print("\n=== Setup Complete ===")
    print(f"S3 Bucket: {bucket_name}")
    print(f"CloudFront Domain: https://{cf_domain}")
    print(f"Distribution ID: {dist_id}")
    print(f"\nNext steps:")
    print(f"1. Validate ACM certificate (add DNS records)")
    print(f"2. Upload website content to S3 bucket")
    print(f"3. Update CloudFront to use certificate and custom domain")
    print(f"4. Create Route 53 alias record pointing to CloudFront")

    return {
        'bucket': bucket_name,
        'distribution_id': dist_id,
        'cloudfront_domain': cf_domain,
        'certificate_arn': cert_arn
    }

# Usage
# result = setup_cloudfront_website('example.com', 'example-website-bucket')
```

---

## Single Page Application (SPA) Hosting

### React/Vue/Angular Configuration

For SPAs, you need to handle client-side routing by redirecting all requests to index.html.

```bash
# CloudFront custom error response for SPA
aws cloudfront update-distribution \
    --id DISTRIBUTION_ID \
    --distribution-config '{
        ...
        "CustomErrorResponses": {
            "Quantity": 2,
            "Items": [
                {
                    "ErrorCode": 403,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 0
                },
                {
                    "ErrorCode": 404,
                    "ResponsePagePath": "/index.html",
                    "ResponseCode": "200",
                    "ErrorCachingMinTTL": 0
                }
            ]
        }
        ...
    }'
```

### SPA Deployment Script

```bash
#!/bin/bash
# deploy-spa.sh

BUCKET_NAME="my-spa-bucket"
DISTRIBUTION_ID="E1234567890ABC"
BUILD_DIR="./build"  # or ./dist for Vue

# Build the application
npm run build

# Sync to S3
aws s3 sync $BUILD_DIR s3://$BUCKET_NAME \
    --delete \
    --cache-control "max-age=31536000" \
    --exclude "index.html" \
    --exclude "service-worker.js"

# Upload index.html with no-cache
aws s3 cp $BUILD_DIR/index.html s3://$BUCKET_NAME/index.html \
    --cache-control "no-cache, no-store, must-revalidate"

# Upload service worker with no-cache
if [ -f "$BUILD_DIR/service-worker.js" ]; then
    aws s3 cp $BUILD_DIR/service-worker.js s3://$BUCKET_NAME/service-worker.js \
        --cache-control "no-cache, no-store, must-revalidate"
fi

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*"

echo "Deployment complete!"
```

---

## Performance Optimization

### Cache Control Headers

```python
import boto3
import mimetypes

s3_client = boto3.client('s3')

def upload_with_cache_control(bucket, source_dir):
    """Upload files with appropriate cache control headers."""

    cache_settings = {
        # Long cache for static assets (1 year)
        '.js': 'public, max-age=31536000',
        '.css': 'public, max-age=31536000',
        '.woff': 'public, max-age=31536000',
        '.woff2': 'public, max-age=31536000',
        '.png': 'public, max-age=31536000',
        '.jpg': 'public, max-age=31536000',
        '.svg': 'public, max-age=31536000',

        # No cache for HTML (ensures fresh content)
        '.html': 'no-cache, no-store, must-revalidate',

        # Short cache for JSON/XML
        '.json': 'public, max-age=3600',
        '.xml': 'public, max-age=3600',
    }

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_path, source_dir)

            # Get file extension and cache control
            ext = os.path.splitext(file)[1].lower()
            cache_control = cache_settings.get(ext, 'public, max-age=86400')

            # Get content type
            content_type, _ = mimetypes.guess_type(file)

            extra_args = {
                'CacheControl': cache_control
            }
            if content_type:
                extra_args['ContentType'] = content_type

            s3_client.upload_file(
                local_path, bucket, s3_key,
                ExtraArgs=extra_args
            )
```

### CloudFront Cache Optimization

```json
{
    "DefaultCacheBehavior": {
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "Compress": true,
        "ViewerProtocolPolicy": "redirect-to-https"
    },
    "CacheBehaviors": {
        "Quantity": 2,
        "Items": [
            {
                "PathPattern": "/static/*",
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
                "TTL": {
                    "DefaultTTL": 31536000,
                    "MaxTTL": 31536000,
                    "MinTTL": 31536000
                }
            },
            {
                "PathPattern": "/api/*",
                "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                "TTL": {
                    "DefaultTTL": 0,
                    "MaxTTL": 0,
                    "MinTTL": 0
                }
            }
        ]
    }
}
```

---

## Cost Estimation

```
S3 STATIC WEBSITE HOSTING COSTS
────────────────────────────────────────────────────────────────────────────

S3 Storage:
• First 50 TB: $0.023/GB/month

S3 Requests:
• PUT/COPY/POST: $0.005 per 1,000 requests
• GET/SELECT: $0.0004 per 1,000 requests

S3 Data Transfer:
• First 100 GB/month: Free (to internet)
• Up to 10 TB/month: $0.09/GB

CloudFront (if used):
• First 10 TB/month: $0.085/GB
• HTTP/HTTPS Requests: $0.0075-$0.01 per 10,000

EXAMPLE CALCULATION:
Small website (1 GB storage, 100,000 pageviews/month, 5 MB average):

S3 Only:
• Storage: 1 GB x $0.023 = $0.023
• GET requests: 100,000 x $0.0004/1000 = $0.04
• Transfer: 500 GB x $0.09 = $45.00
• Total: ~$45/month

With CloudFront:
• S3 Storage: $0.023
• S3 Transfer to CloudFront: Free
• CloudFront Transfer: 500 GB x $0.085 = $42.50
• CloudFront Requests: 100,000 x $0.01/10000 = $0.10
• Total: ~$42.63/month (plus better performance!)
```

---

## Troubleshooting

### Common Issues

```
ISSUE: 403 Forbidden Error
─────────────────────────────────────────────────────────────────────────────
Causes:
• Block Public Access is enabled
• Bucket policy doesn't allow public read
• Object ACL is private (if using ACLs)

Fix:
1. Disable Block Public Access settings
2. Add public read bucket policy
3. Verify object permissions

ISSUE: 404 Not Found for Routes
─────────────────────────────────────────────────────────────────────────────
Causes:
• SPA routes not handled
• Missing index.html in subdirectory

Fix:
1. For SPAs: Configure CloudFront custom error responses
2. For static sites: Ensure index.html exists in each directory

ISSUE: Website shows XML instead of HTML
─────────────────────────────────────────────────────────────────────────────
Causes:
• Using REST API endpoint instead of website endpoint

Fix:
• Use: bucket.s3-website-region.amazonaws.com
• Not: bucket.s3.region.amazonaws.com

ISSUE: HTTPS not working
─────────────────────────────────────────────────────────────────────────────
Causes:
• S3 website endpoints only support HTTP
• No CloudFront distribution configured

Fix:
• Set up CloudFront with ACM certificate
• S3 website hosting does not support HTTPS directly
```

---

## Summary

| Feature | S3 Only | S3 + CloudFront |
|---------|---------|-----------------|
| **HTTPS** | Not supported | Full support |
| **Custom Domain** | Limited | Full support |
| **Performance** | Single region | Global CDN |
| **Cost** | Lower for low traffic | Better for high traffic |
| **Cache Control** | Limited | Advanced |
| **Security** | Public bucket | Private bucket + OAC |

---

## Next Steps

Continue to [07-s3-replication.md](./07-s3-replication.md) to learn about Cross-Region and Same-Region Replication.
