# Amazon Inspector

## Introduction

Amazon Inspector is an automated vulnerability management service that continually scans AWS workloads for software vulnerabilities and unintended network exposure. It automatically discovers and scans EC2 instances, container images in Amazon ECR, and Lambda functions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Amazon Inspector Overview                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Workloads                    Inspector                    Outputs         │
│                                                                             │
│   ┌─────────────┐        ┌──────────────────┐        ┌─────────────────┐   │
│   │     EC2     │        │                  │        │    Findings     │   │
│   │  Instances  │───────▶│                  │───────▶│                 │   │
│   └─────────────┘        │                  │        │ • Severity      │   │
│                          │   Vulnerability  │        │ • CVE Details   │   │
│   ┌─────────────┐        │      Scan        │        │ • Remediation   │   │
│   │  ECR Images │───────▶│                  │        │                 │   │
│   │ (Containers)│        │ • CVE Database   │        └─────────────────┘   │
│   └─────────────┘        │ • Network Rules  │               │              │
│                          │ • Code Analysis  │               ▼              │
│   ┌─────────────┐        │                  │        ┌─────────────────┐   │
│   │   Lambda    │───────▶│                  │───────▶│  Security Hub   │   │
│   │  Functions  │        │                  │        │  Integration    │   │
│   └─────────────┘        └──────────────────┘        └─────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## What is Amazon Inspector?

### Key Features

| Feature | Description |
|---------|-------------|
| **Continuous Scanning** | Automatically scans workloads when changes are detected |
| **CVE Detection** | Identifies known vulnerabilities from CVE database |
| **Network Reachability** | Analyzes network paths to identify exposure |
| **Code Scanning** | Scans Lambda functions for code vulnerabilities |
| **Risk Scoring** | Provides contextual risk scores using CVSS |
| **Integration** | Works with Security Hub, EventBridge, and S3 |
| **Multi-Account** | Centralized management via AWS Organizations |

### Inspector Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Amazon Inspector Architecture                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     Management Account                               │  │
│   │                                                                      │  │
│   │   ┌────────────────────────────────────────────────────────────┐    │  │
│   │   │            Inspector Delegated Administrator               │    │  │
│   │   │                                                            │    │  │
│   │   │  • Centralized Dashboard                                   │    │  │
│   │   │  • Cross-Account Findings                                  │    │  │
│   │   │  • Aggregated Metrics                                      │    │  │
│   │   │  • Suppression Rules                                       │    │  │
│   │   └────────────────────────────────────────────────────────────┘    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                 │
│              ▼                     ▼                     ▼                 │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐         │
│   │  Member Acct 1  │   │  Member Acct 2  │   │  Member Acct N  │         │
│   │                 │   │                 │   │                 │         │
│   │ ┌─────────────┐ │   │ ┌─────────────┐ │   │ ┌─────────────┐ │         │
│   │ │  EC2 Scan   │ │   │ │  EC2 Scan   │ │   │ │  EC2 Scan   │ │         │
│   │ │  Agent/SSM  │ │   │ │  Agent/SSM  │ │   │ │  Agent/SSM  │ │         │
│   │ └─────────────┘ │   │ └─────────────┘ │   │ └─────────────┘ │         │
│   │ ┌─────────────┐ │   │ ┌─────────────┐ │   │ ┌─────────────┐ │         │
│   │ │  ECR Scan   │ │   │ │  ECR Scan   │ │   │ │  ECR Scan   │ │         │
│   │ │  (Agentless)│ │   │ │  (Agentless)│ │   │ │  (Agentless)│ │         │
│   │ └─────────────┘ │   │ └─────────────┘ │   │ └─────────────┘ │         │
│   │ ┌─────────────┐ │   │ ┌─────────────┐ │   │ ┌─────────────┐ │         │
│   │ │ Lambda Scan │ │   │ │ Lambda Scan │ │   │ │ Lambda Scan │ │         │
│   │ │  (Code)     │ │   │ │  (Code)     │ │   │ │  (Code)     │ │         │
│   │ └─────────────┘ │   │ └─────────────┘ │   │ └─────────────┘ │         │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Scan Types and Coverage

### EC2 Instance Scanning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EC2 Instance Scanning                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Scanning Methods:                                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │  Agent-Based (SSM Agent)              Agentless Scanning            │  │
│   │  ─────────────────────────            ──────────────────            │  │
│   │                                                                     │  │
│   │  ┌──────────────┐                    ┌──────────────┐               │  │
│   │  │  EC2         │                    │  EC2         │               │  │
│   │  │  Instance    │                    │  Instance    │               │  │
│   │  │  ┌────────┐  │                    │              │               │  │
│   │  │  │  SSM   │  │                    │  (No Agent)  │               │  │
│   │  │  │ Agent  │  │                    │              │               │  │
│   │  │  └────────┘  │                    └──────────────┘               │  │
│   │  └──────┬───────┘                           │                       │  │
│   │         │                                   │                       │  │
│   │         ▼                                   ▼                       │  │
│   │  • Package inventory                 • EBS Volume scan              │  │
│   │  • OS configuration                  • Snapshot-based               │  │
│   │  • Deep inspection                   • No instance access           │  │
│   │  • Network paths                     • Limited to packages          │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   What Gets Scanned:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Operating system packages (yum, apt, rpm, dpkg)                  │  │
│   │  • Programming language packages (Python, Java, Node.js, .NET)      │  │
│   │  • Network configuration and reachability                           │  │
│   │  • EC2 instance metadata                                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Supported Operating Systems:                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Amazon Linux, Amazon Linux 2, Amazon Linux 2023                  │  │
│   │  • Ubuntu 16.04, 18.04, 20.04, 22.04                                │  │
│   │  • Debian 9, 10, 11                                                 │  │
│   │  • RHEL 7, 8, 9                                                     │  │
│   │  • CentOS 7, 8                                                      │  │
│   │  • SUSE Linux Enterprise Server 12, 15                              │  │
│   │  • Windows Server 2012, 2016, 2019, 2022                            │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ECR Container Image Scanning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ECR Container Image Scanning                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────┐         ┌───────────────┐         ┌───────────────┐    │
│   │   Developer   │         │      ECR      │         │   Inspector   │    │
│   │               │         │   Registry    │         │               │    │
│   │  docker push  │────────▶│               │────────▶│  Scan Image   │    │
│   │               │         │ ┌───────────┐ │         │               │    │
│   └───────────────┘         │ │   Image   │ │         │ ┌───────────┐ │    │
│                             │ │  Layers   │ │         │ │   OS      │ │    │
│                             │ └───────────┘ │         │ │  Packages │ │    │
│                             └───────────────┘         │ ├───────────┤ │    │
│                                                       │ │   Lang    │ │    │
│   Scan Triggers:                                      │ │  Packages │ │    │
│   • On push to repository                             │ └───────────┘ │    │
│   • Scheduled rescans                                 │               │    │
│   • Manual trigger                                    └───────────────┘    │
│                                                              │              │
│                                                              ▼              │
│                                                       ┌───────────────┐    │
│   Scan Coverage:                                      │   Findings    │    │
│   ─────────────────────────────────────               │               │    │
│   • Base image vulnerabilities                        │ • CVE-2023-XX │    │
│   • OS package vulnerabilities                        │ • CVE-2023-YY │    │
│   • Application dependencies                          │ • ...         │    │
│   • Language-specific packages                        └───────────────┘    │
│     - Python (pip)                                                          │
│     - Node.js (npm)                                                         │
│     - Java (Maven, Gradle)                                                  │
│     - Go modules                                                            │
│     - Ruby gems                                                             │
│     - .NET NuGet                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Lambda Function Scanning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Lambda Function Scanning                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        Lambda Scan Types                             │  │
│   ├─────────────────────────────┬───────────────────────────────────────┤  │
│   │   Package Vulnerabilities   │   Code Vulnerabilities (Preview)      │  │
│   │                             │                                       │  │
│   │   • Dependencies scan       │   • Static code analysis              │  │
│   │   • Third-party libraries   │   • Security best practices           │  │
│   │   • CVE detection           │   • Injection vulnerabilities         │  │
│   │   • Automatic on deploy     │   • Hardcoded secrets detection       │  │
│   │                             │   • Insecure configurations           │  │
│   └─────────────────────────────┴───────────────────────────────────────┘  │
│                                                                             │
│   Supported Runtimes:                                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │  Python     │  Node.js    │   Java      │   Go        │  .NET      │  │
│   │  3.7-3.12   │  14.x-20.x  │   8, 11, 17 │   1.x       │  Core 3.1  │  │
│   │             │             │   21        │             │  6, 7, 8   │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Code Vulnerability Detection (Examples):                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │  • SQL Injection                      CWE-89                        │  │
│   │  • Command Injection                  CWE-78                        │  │
│   │  • Cross-Site Scripting (XSS)         CWE-79                        │  │
│   │  • Path Traversal                     CWE-22                        │  │
│   │  • Hardcoded Credentials              CWE-798                       │  │
│   │  • Insecure Deserialization           CWE-502                       │  │
│   │  • Server-Side Request Forgery        CWE-918                       │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Findings and Severity

### Finding Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Inspector Finding Example                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Finding ID: arn:aws:inspector2:us-east-1:123456789012:finding/abc123       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Title: CVE-2023-44487 - HTTP/2 Rapid Reset Attack                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Severity: CRITICAL (CVSS 7.5)                                      │   │
│  │  Status: ACTIVE                                                     │   │
│  │  Type: PACKAGE_VULNERABILITY                                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  Affected Resource:                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Type: AWS_EC2_INSTANCE                                     │   │   │
│  │  │  ID: i-0abc123def456789                                     │   │   │
│  │  │  Region: us-east-1                                          │   │   │
│  │  │  Tags: Environment=Production, Team=Backend                 │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  Vulnerable Package:                                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Package: nginx                                             │   │   │
│  │  │  Installed Version: 1.18.0                                  │   │   │
│  │  │  Fixed Version: 1.25.3                                      │   │   │
│  │  │  Package Manager: YUM                                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  Remediation:                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Update nginx to version 1.25.3 or later.                   │   │   │
│  │  │                                                             │   │   │
│  │  │  sudo yum update nginx                                      │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  References:                                                        │   │
│  │  • https://nvd.nist.gov/vuln/detail/CVE-2023-44487               │   │
│  │  • https://nginx.org/en/security_advisories.html                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Severity Levels

| Severity | CVSS Score | Description | Response Time |
|----------|------------|-------------|---------------|
| **Critical** | 9.0 - 10.0 | Immediate exploitation risk | 24-48 hours |
| **High** | 7.0 - 8.9 | Significant vulnerability | 1 week |
| **Medium** | 4.0 - 6.9 | Moderate risk | 2 weeks |
| **Low** | 0.1 - 3.9 | Minor vulnerability | 1 month |
| **Informational** | 0 | Best practice recommendations | As scheduled |

### Inspector Score

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Inspector Score Calculation                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Inspector Score = Base CVSS Score + Environmental Adjustments             │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     Score Components                                 │  │
│   ├─────────────────────────────────────────────────────────────────────┤  │
│   │                                                                     │  │
│   │  Base Score (CVSS v3.1)                                             │  │
│   │  ├── Attack Vector (Network, Adjacent, Local, Physical)            │  │
│   │  ├── Attack Complexity (Low, High)                                 │  │
│   │  ├── Privileges Required (None, Low, High)                         │  │
│   │  ├── User Interaction (None, Required)                             │  │
│   │  └── Impact (Confidentiality, Integrity, Availability)             │  │
│   │                                                                     │  │
│   │  Environmental Adjustments                                          │  │
│   │  ├── Network Reachability (Public Internet exposure?)              │  │
│   │  ├── Exploit Availability (Known exploits in the wild?)            │  │
│   │  └── Asset Criticality (Is this a production system?)              │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Example:                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  CVE-2023-XXXX                                                      │  │
│   │  Base CVSS: 7.5 (High)                                              │  │
│   │  + Network accessible from internet: +1.0                           │  │
│   │  + Known exploit available: +0.5                                    │  │
│   │  ─────────────────────────────────                                  │  │
│   │  Inspector Score: 9.0 (Critical)                                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Enabling and Configuring Inspector

### Enable Inspector via Console

1. Navigate to Amazon Inspector console
2. Click "Get started"
3. Select scan types to enable:
   - EC2 scanning
   - ECR scanning
   - Lambda scanning (standard and code)
4. Review and confirm activation

### Enable Inspector via CLI

```bash
# Enable Inspector for the account
aws inspector2 enable \
    --resource-types EC2 ECR LAMBDA LAMBDA_CODE

# Check Inspector status
aws inspector2 batch-get-account-status

# Get enabled resource types
aws inspector2 get-member \
    --account-id 123456789012

# Enable for specific member accounts (delegated admin)
aws inspector2 enable-delegated-admin-account \
    --delegated-admin-account-id 123456789012

# Associate member accounts
aws inspector2 associate-member \
    --account-id 987654321098
```

### Configure Scan Settings

```bash
# Update EC2 scan configuration
aws inspector2 update-ec2-deep-inspection-configuration \
    --activate-deep-inspection \
    --package-paths "/usr/local/lib" "/opt/app"

# Configure ECR scan settings
aws inspector2 update-configuration \
    --ecr-configuration '{
        "rescanDuration": "LIFETIME",
        "pullDateRescanDuration": "DAYS_180"
    }'

# Set up filter for findings
aws inspector2 create-filter \
    --name "Critical-Production" \
    --description "Critical findings in production" \
    --action "NONE" \
    --filter-criteria '{
        "severity": [{"comparison": "EQUALS", "value": "CRITICAL"}],
        "resourceTags": [{"comparison": "EQUALS", "key": "Environment", "value": "Production"}]
    }'
```

### CloudFormation Setup

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Amazon Inspector Configuration'

Resources:
  # Enable Inspector
  InspectorEnabler:
    Type: AWS::Inspector2::Enabler
    Properties:
      AccountIds:
        - !Ref AWS::AccountId
      ResourceTypes:
        - EC2
        - ECR
        - LAMBDA
        - LAMBDA_CODE

  # Create suppression rule for known false positives
  InspectorFilter:
    Type: AWS::Inspector2::Filter
    Properties:
      Name: 'Suppress-Development-Low'
      Description: 'Suppress low severity findings in development'
      FilterAction: SUPPRESS
      FilterCriteria:
        Severity:
          - Comparison: EQUALS
            Value: LOW
        ResourceTags:
          - Comparison: EQUALS
            Key: Environment
            Value: Development

  # EventBridge rule for critical findings
  CriticalFindingsRule:
    Type: AWS::Events::Rule
    Properties:
      Name: 'Inspector-Critical-Findings'
      Description: 'Alert on critical Inspector findings'
      EventPattern:
        source:
          - aws.inspector2
        detail-type:
          - Inspector2 Finding
        detail:
          severity:
            - CRITICAL
      State: ENABLED
      Targets:
        - Id: SNSTarget
          Arn: !Ref AlertTopic

  AlertTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: inspector-critical-alerts
      KmsMasterKeyId: alias/aws/sns

  AlertSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref AlertTopic
      Protocol: email
      Endpoint: security-team@example.com

Outputs:
  FilterArn:
    Description: 'Inspector Filter ARN'
    Value: !Ref InspectorFilter
```

## Integration with Security Hub

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Inspector + Security Hub Integration                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                        ┌─────────────────────────┐   │
│   │    Inspector    │                        │     Security Hub        │   │
│   │                 │                        │                         │   │
│   │  ┌───────────┐  │    Auto-forwarding    │  ┌───────────────────┐  │   │
│   │  │ EC2       │  │ ──────────────────────▶│  │ Findings          │  │   │
│   │  │ Findings  │  │                        │  │ Aggregation       │  │   │
│   │  └───────────┘  │                        │  └───────────────────┘  │   │
│   │  ┌───────────┐  │                        │           │            │   │
│   │  │ ECR       │  │                        │           ▼            │   │
│   │  │ Findings  │  │                        │  ┌───────────────────┐  │   │
│   │  └───────────┘  │                        │  │ Unified Dashboard │  │   │
│   │  ┌───────────┐  │                        │  │                   │  │   │
│   │  │ Lambda    │  │                        │  │ • All Sources     │  │   │
│   │  │ Findings  │  │                        │  │ • Compliance      │  │   │
│   │  └───────────┘  │                        │  │ • Prioritization  │  │   │
│   │                 │                        │  └───────────────────┘  │   │
│   └─────────────────┘                        │           │            │   │
│                                              │           ▼            │   │
│                                              │  ┌───────────────────┐  │   │
│                                              │  │ Automated         │  │   │
│                                              │  │ Response          │  │   │
│                                              │  │ (EventBridge)     │  │   │
│                                              │  └───────────────────┘  │   │
│                                              └─────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enable Security Hub Integration

```bash
# Security Hub integration is automatic when both services are enabled
# Verify integration status
aws securityhub describe-products \
    --query 'Products[?ProductName==`Inspector`]'

# Enable Inspector findings import in Security Hub
aws securityhub enable-import-findings-for-product \
    --product-arn "arn:aws:securityhub:us-east-1::product/aws/inspector"

# View Inspector findings in Security Hub
aws securityhub get-findings \
    --filters '{
        "ProductName": [{"Value": "Inspector", "Comparison": "EQUALS"}],
        "SeverityLabel": [{"Value": "CRITICAL", "Comparison": "EQUALS"}]
    }' \
    --max-results 10
```

## Hands-on Setup

### Step 1: Enable Inspector

```bash
#!/bin/bash
# Enable Amazon Inspector

# Enable Inspector for all resource types
echo "Enabling Amazon Inspector..."
aws inspector2 enable \
    --resource-types EC2 ECR LAMBDA LAMBDA_CODE

# Wait for enablement to complete
sleep 10

# Verify status
echo "Checking Inspector status..."
aws inspector2 batch-get-account-status \
    --query 'accounts[0].state'
```

### Step 2: Configure EC2 Scanning

```bash
#!/bin/bash
# Configure EC2 instance for Inspector scanning

# 1. Ensure SSM Agent is installed and running
# Amazon Linux 2
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent

# 2. Attach IAM role with SSM permissions to EC2
# The instance needs AmazonSSMManagedInstanceCore policy

# 3. Enable deep inspection for additional package paths
aws inspector2 update-ec2-deep-inspection-configuration \
    --activate-deep-inspection \
    --package-paths "/usr/local/lib" "/opt/myapp/lib" "/home/app/node_modules"

# 4. Verify instance is being scanned
aws inspector2 list-coverage \
    --filter-criteria '{
        "resourceType": [{"comparison": "EQUALS", "value": "AWS_EC2_INSTANCE"}]
    }'
```

### Step 3: Configure ECR Scanning

```bash
#!/bin/bash
# Configure ECR scanning

# Create ECR repository with scanning enabled
aws ecr create-repository \
    --repository-name my-application \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=KMS

# Configure scan duration
aws inspector2 update-configuration \
    --ecr-configuration '{
        "rescanDuration": "DAYS_180"
    }'

# Push an image to trigger scan
docker build -t my-application:latest .
docker tag my-application:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-application:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-application:latest

# Check scan results
aws inspector2 list-findings \
    --filter-criteria '{
        "resourceType": [{"comparison": "EQUALS", "value": "AWS_ECR_CONTAINER_IMAGE"}]
    }'
```

### Step 4: Set Up Alerting

```bash
#!/bin/bash
# Set up alerting for Inspector findings

# Create SNS topic for alerts
TOPIC_ARN=$(aws sns create-topic --name inspector-alerts --query 'TopicArn' --output text)

# Subscribe email
aws sns subscribe \
    --topic-arn $TOPIC_ARN \
    --protocol email \
    --notification-endpoint security@example.com

# Create EventBridge rule for critical findings
aws events put-rule \
    --name "inspector-critical-findings" \
    --event-pattern '{
        "source": ["aws.inspector2"],
        "detail-type": ["Inspector2 Finding"],
        "detail": {
            "severity": ["CRITICAL", "HIGH"]
        }
    }' \
    --state ENABLED

# Add SNS target
aws events put-targets \
    --rule "inspector-critical-findings" \
    --targets "Id"="sns-target","Arn"="$TOPIC_ARN"
```

### Step 5: Query and Export Findings

```bash
#!/bin/bash
# Query Inspector findings

# List all critical findings
echo "Critical Findings:"
aws inspector2 list-findings \
    --filter-criteria '{
        "severity": [{"comparison": "EQUALS", "value": "CRITICAL"}],
        "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
    }' \
    --sort-criteria '{"field": "SEVERITY", "sortOrder": "DESC"}' \
    --max-results 50

# Get findings count by severity
echo "Findings Summary:"
aws inspector2 list-finding-aggregations \
    --aggregation-type SEVERITY \
    --query 'responses[].severityCounts'

# Export findings to S3
aws inspector2 create-findings-report \
    --report-format CSV \
    --s3-destination '{
        "bucketName": "my-inspector-reports",
        "keyPrefix": "findings/",
        "kmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/my-key"
    }' \
    --filter-criteria '{
        "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
    }'
```

### Step 6: Create Suppression Rules

```bash
#!/bin/bash
# Create suppression rules for false positives

# Suppress findings for development environments
aws inspector2 create-filter \
    --name "Suppress-Dev-Low-Medium" \
    --description "Suppress low and medium findings in dev" \
    --action SUPPRESS \
    --filter-criteria '{
        "severity": [
            {"comparison": "EQUALS", "value": "LOW"},
            {"comparison": "EQUALS", "value": "MEDIUM"}
        ],
        "resourceTags": [
            {"comparison": "EQUALS", "key": "Environment", "value": "development"}
        ]
    }'

# Suppress specific CVE (after verification it's not applicable)
aws inspector2 create-filter \
    --name "Suppress-CVE-2023-XXXX" \
    --description "Not applicable - compensating control in place" \
    --action SUPPRESS \
    --filter-criteria '{
        "vulnerabilityId": [{"comparison": "EQUALS", "value": "CVE-2023-XXXX"}]
    }'

# List all filters
aws inspector2 list-filters
```

## Remediation Strategies

### Automated Remediation with Systems Manager

```yaml
# CloudFormation template for automated patching
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Automated vulnerability remediation'

Resources:
  # SSM Patch Baseline
  PatchBaseline:
    Type: AWS::SSM::PatchBaseline
    Properties:
      Name: SecurityPatchBaseline
      Description: 'Patch baseline for security updates'
      OperatingSystem: AMAZON_LINUX_2
      ApprovalRules:
        PatchRules:
          - ApproveAfterDays: 0
            ComplianceLevel: CRITICAL
            PatchFilterGroup:
              PatchFilters:
                - Key: CLASSIFICATION
                  Values:
                    - Security
                - Key: SEVERITY
                  Values:
                    - Critical
                    - Important
          - ApproveAfterDays: 7
            ComplianceLevel: HIGH
            PatchFilterGroup:
              PatchFilters:
                - Key: CLASSIFICATION
                  Values:
                    - Security
                - Key: SEVERITY
                  Values:
                    - Medium

  # Maintenance Window
  MaintenanceWindow:
    Type: AWS::SSM::MaintenanceWindow
    Properties:
      Name: SecurityPatchWindow
      Schedule: cron(0 2 ? * SAT *)  # Every Saturday at 2 AM
      Duration: 4
      Cutoff: 1
      AllowUnassociatedTargets: false

  # Maintenance Window Target
  MaintenanceWindowTarget:
    Type: AWS::SSM::MaintenanceWindowTarget
    Properties:
      WindowId: !Ref MaintenanceWindow
      ResourceType: INSTANCE
      Targets:
        - Key: tag:PatchGroup
          Values:
            - Production

  # Patch Task
  PatchTask:
    Type: AWS::SSM::MaintenanceWindowTask
    Properties:
      WindowId: !Ref MaintenanceWindow
      Targets:
        - Key: WindowTargetIds
          Values:
            - !Ref MaintenanceWindowTarget
      TaskType: RUN_COMMAND
      TaskArn: AWS-RunPatchBaseline
      Priority: 1
      MaxConcurrency: '25%'
      MaxErrors: '10%'
      TaskInvocationParameters:
        MaintenanceWindowRunCommandParameters:
          Parameters:
            Operation:
              - Install
            RebootOption:
              - RebootIfNeeded

  # EventBridge rule to trigger on critical findings
  RemediationTrigger:
    Type: AWS::Events::Rule
    Properties:
      Name: 'Inspector-Auto-Remediation'
      EventPattern:
        source:
          - aws.inspector2
        detail-type:
          - Inspector2 Finding
        detail:
          severity:
            - CRITICAL
          status:
            - ACTIVE
      State: ENABLED
      Targets:
        - Id: RemediationLambda
          Arn: !GetAtt RemediationLambda.Arn

  # Lambda for automated response
  RemediationLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: inspector-auto-remediation
      Runtime: python3.11
      Handler: index.handler
      Role: !GetAtt LambdaRole.Arn
      Timeout: 300
      Code:
        ZipFile: |
          import boto3
          import json

          ssm = boto3.client('ssm')

          def handler(event, context):
              finding = event['detail']
              resource_type = finding['resources'][0]['type']

              if resource_type == 'AWS_EC2_INSTANCE':
                  instance_id = finding['resources'][0]['id'].split('/')[-1]

                  # Trigger immediate patching
                  response = ssm.send_command(
                      InstanceIds=[instance_id],
                      DocumentName='AWS-RunPatchBaseline',
                      Parameters={
                          'Operation': ['Install'],
                          'RebootOption': ['NoReboot']
                      }
                  )

                  return {
                      'statusCode': 200,
                      'body': json.dumps(f'Patching triggered for {instance_id}')
                  }

              return {
                  'statusCode': 200,
                  'body': json.dumps('No action taken')
              }

  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: SSMAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - ssm:SendCommand
                Resource: '*'
```

## Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Inspector Best Practices                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Coverage and Scanning                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Enable all scan types (EC2, ECR, Lambda)                         │   │
│  │  • Ensure SSM Agent is installed on all EC2 instances               │   │
│  │  • Enable deep inspection for custom package paths                   │   │
│  │  • Configure ECR scan-on-push for all repositories                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. Finding Management                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Prioritize findings by Inspector Score (not just CVSS)           │   │
│  │  • Create suppression rules for verified false positives            │   │
│  │  • Document justification for suppressed findings                    │   │
│  │  • Regularly review and clean up suppression rules                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. Integration and Automation                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Enable Security Hub integration for centralized view             │   │
│  │  • Set up EventBridge rules for critical findings                    │   │
│  │  • Implement automated remediation where possible                    │   │
│  │  • Export findings to S3 for compliance reporting                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. Multi-Account Management                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Use delegated administrator for Organizations                     │   │
│  │  • Standardize tag-based policies across accounts                    │   │
│  │  • Aggregate findings in central security account                    │   │
│  │  • Create account-specific and org-wide suppression rules            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  5. Remediation SLAs                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Severity    │  Production SLA  │  Development SLA                  │   │
│  │  ──────────────────────────────────────────────────                 │   │
│  │  Critical    │  24 hours        │  72 hours                         │   │
│  │  High        │  7 days          │  14 days                          │   │
│  │  Medium      │  30 days         │  60 days                          │   │
│  │  Low         │  90 days         │  Best effort                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Pricing

| Resource Type | Pricing Model |
|---------------|---------------|
| **EC2 Instances** | Per instance per month (varies by instance size) |
| **ECR Images** | Per image scanned (initial + rescan) |
| **Lambda Functions** | Per function per month |
| **Lambda Code Scanning** | Per function per month (additional) |

**Cost Optimization Tips**:
- Use suppression rules to avoid re-scanning known issues
- Tag resources to exclude non-production from certain scans
- Configure appropriate rescan durations for ECR
- Use filters to focus on actionable findings

## Summary

Amazon Inspector provides comprehensive vulnerability management:

1. **Continuous Scanning**: Automatic scanning of EC2, ECR, and Lambda
2. **Contextual Scoring**: Inspector Score considers network exposure and exploitability
3. **Integration**: Native Security Hub and EventBridge integration
4. **Multi-Account**: Centralized management via Organizations
5. **Automation**: EventBridge rules enable automated remediation

**Key Takeaways**:
- Enable Inspector for all workload types
- Prioritize remediation based on Inspector Score
- Implement automated patching for critical vulnerabilities
- Use suppression rules judiciously with documentation
- Integrate with Security Hub for unified security view
