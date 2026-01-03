# Identity Federation

## Introduction

Identity federation allows you to use identities from external identity providers (IdPs) to access AWS resources. Instead of creating IAM users for every person, you can leverage existing corporate directories or social identity providers.

---

## Why Federation?

### The Problem with IAM Users at Scale

```
+------------------------------------------------------------------+
|                  THE SCALING PROBLEM                              |
+------------------------------------------------------------------+
|                                                                   |
|  Company with 5,000 employees:                                   |
|                                                                   |
|  WITHOUT FEDERATION:                                              |
|  +----------------------------------------------------------+    |
|  |  Create 5,000 IAM users                                   |    |
|  |  Manage 5,000 passwords                                   |    |
|  |  Handle 5,000 MFA devices                                 |    |
|  |  Process 500+ onboarding/offboarding per year             |    |
|  |  Sync with corporate directory manually                   |    |
|  |  Users have another set of credentials to remember        |    |
|  +----------------------------------------------------------+    |
|                                                                   |
|  WITH FEDERATION:                                                 |
|  +----------------------------------------------------------+    |
|  |  Use existing corporate directory (AD, Okta, etc.)        |    |
|  |  Single set of credentials for users                      |    |
|  |  Automatic provisioning/deprovisioning                    |    |
|  |  Centralized access control                               |    |
|  |  Existing MFA/security policies apply                     |    |
|  +----------------------------------------------------------+    |
|                                                                   |
+------------------------------------------------------------------+
```

### Benefits of Federation

| Benefit | Description |
|---------|-------------|
| Single Sign-On | Users log in once to access multiple systems |
| Centralized Management | Manage access from your identity provider |
| Reduced Credentials | No additional passwords for users |
| Better Security | Leverage existing MFA and security controls |
| Compliance | Easier auditing and access reviews |
| Scalability | Handle thousands of users efficiently |

---

## Federation Types

```
+------------------------------------------------------------------+
|                    FEDERATION OPTIONS                             |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------------+     +------------------------+        |
|  |   ENTERPRISE (SAML)   |     |   CONSUMER (WEB ID)    |        |
|  +------------------------+     +------------------------+        |
|  |                        |     |                        |        |
|  | Corporate Identities   |     | Social Identities      |        |
|  |                        |     |                        |        |
|  | - Active Directory     |     | - Google               |        |
|  | - Okta                 |     | - Facebook             |        |
|  | - Azure AD             |     | - Amazon               |        |
|  | - PingFederate         |     | - Apple                |        |
|  | - OneLogin             |     | - Any OIDC provider    |        |
|  |                        |     |                        |        |
|  | Use Case:              |     | Use Case:              |        |
|  | Employees, contractors |     | Mobile apps, web apps  |        |
|  |                        |     | customer access        |        |
|  +------------------------+     +------------------------+        |
|                                                                   |
|  +------------------------+                                       |
|  | AWS IAM IDENTITY CENTER|                                       |
|  | (Recommended)          |                                       |
|  +------------------------+                                       |
|  |                        |                                       |
|  | - Built-in user store  |                                       |
|  | - Or connect to AD     |                                       |
|  | - Multi-account access |                                       |
|  | - Permission sets      |                                       |
|  |                        |                                       |
|  +------------------------+                                       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## SAML 2.0 Federation

### How SAML Works

```
+------------------------------------------------------------------+
|                    SAML 2.0 FEDERATION FLOW                       |
+------------------------------------------------------------------+
|                                                                   |
|  +--------+    +------------+    +-----------+    +-----------+   |
|  |  User  |    |  Identity  |    |   AWS     |    |   AWS     |   |
|  |        |    |  Provider  |    |   IAM     |    | Resources |   |
|  +---+----+    +-----+------+    +-----+-----+    +-----+-----+   |
|      |              |                  |                |         |
|      | 1. Access    |                  |                |         |
|      |    AWS       |                  |                |         |
|      +------------->|                  |                |         |
|      |              |                  |                |         |
|      |<-------------+                  |                |         |
|      | 2. Redirect  |                  |                |         |
|      |    to IdP    |                  |                |         |
|      |              |                  |                |         |
|      +------------->|                  |                |         |
|      | 3. Login at  |                  |                |         |
|      |    IdP       |                  |                |         |
|      |              |                  |                |         |
|      |<-------------+                  |                |         |
|      | 4. SAML      |                  |                |         |
|      |    Assertion |                  |                |         |
|      |              |                  |                |         |
|      +------------------------------------->|           |         |
|      | 5. AssumeRoleWithSAML                |           |         |
|      |              |                       |           |         |
|      |<-------------------------------------+           |         |
|      | 6. Temporary Credentials             |           |         |
|      |              |                       |           |         |
|      +------------------------------------------------->|         |
|      | 7. Access AWS Resources                          |         |
|      |              |                       |           |         |
|                                                                   |
+------------------------------------------------------------------+
```

### Setting Up SAML Federation

#### Step 1: Create SAML Provider in AWS

```bash
# Download metadata from your IdP first
# Then create the SAML provider
aws iam create-saml-provider \
    --saml-metadata-document file://idp-metadata.xml \
    --name CompanyIdP
```

#### Step 2: Create IAM Role for Federation

```bash
# Trust policy for SAML provider
cat > saml-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::123456789012:saml-provider/CompanyIdP"
            },
            "Action": "sts:AssumeRoleWithSAML",
            "Condition": {
                "StringEquals": {
                    "SAML:aud": "https://signin.aws.amazon.com/saml"
                }
            }
        }
    ]
}
EOF

# Create the role
aws iam create-role \
    --role-name SAML-Admin-Role \
    --assume-role-policy-document file://saml-trust-policy.json

# Attach permissions
aws iam attach-role-policy \
    --role-name SAML-Admin-Role \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

#### Step 3: Configure Your IdP

Configure your identity provider to:
1. Trust AWS as a service provider
2. Send SAML assertions to: `https://signin.aws.amazon.com/saml`
3. Include required attributes:
   - `https://aws.amazon.com/SAML/Attributes/Role`
   - `https://aws.amazon.com/SAML/Attributes/RoleSessionName`

### SAML Attribute Mapping

```
+------------------------------------------------------------------+
|                    SAML ATTRIBUTES                                |
+------------------------------------------------------------------+
|                                                                   |
|  Required Attributes:                                            |
|  +---------------------------------------------------------------+
|  | Attribute                                    | Value          |
|  +----------------------------------------------+----------------+
|  | https://aws.amazon.com/SAML/Attributes/Role  | arn:aws:iam::  |
|  |                                              | ACCOUNT:role/  |
|  |                                              | ROLE,arn:aws:  |
|  |                                              | iam::ACCOUNT:  |
|  |                                              | saml-provider/ |
|  |                                              | PROVIDER       |
|  +----------------------------------------------+----------------+
|  | https://aws.amazon.com/SAML/Attributes/      | user@company   |
|  | RoleSessionName                              | .com           |
|  +----------------------------------------------+----------------+
|                                                                   |
|  Optional Attributes:                                            |
|  +----------------------------------------------+----------------+
|  | https://aws.amazon.com/SAML/Attributes/      | 3600 (seconds) |
|  | SessionDuration                              |                |
|  +----------------------------------------------+----------------+
|  | https://aws.amazon.com/SAML/Attributes/      | tag values     |
|  | PrincipalTag:*                               |                |
|  +----------------------------------------------+----------------+
|                                                                   |
+------------------------------------------------------------------+
```

---

## Web Identity Federation

### Overview

Web Identity Federation allows users authenticated by a web identity provider (Google, Facebook, Amazon) to access AWS resources.

```
+------------------------------------------------------------------+
|                WEB IDENTITY FEDERATION FLOW                       |
+------------------------------------------------------------------+
|                                                                   |
|  +--------+    +------------+    +-----------+    +-----------+   |
|  |  User  |    |   Social   |    |   AWS     |    |   AWS     |   |
|  | (App)  |    |    IdP     |    |   STS     |    | Resources |   |
|  +---+----+    +-----+------+    +-----+-----+    +-----+-----+   |
|      |              |                  |                |         |
|      +------------->|                  |                |         |
|      | 1. Login     |                  |                |         |
|      |              |                  |                |         |
|      |<-------------+                  |                |         |
|      | 2. ID Token  |                  |                |         |
|      |              |                  |                |         |
|      +------------------------------>  |                |         |
|      | 3. AssumeRoleWithWebIdentity    |                |         |
|      |    (with ID Token)              |                |         |
|      |              |                  |                |         |
|      |<------------------------------  |                |         |
|      | 4. Temp AWS Credentials         |                |         |
|      |              |                  |                |         |
|      +------------------------------------------------->|         |
|      | 5. Access AWS Resources                          |         |
|                                                                   |
+------------------------------------------------------------------+
```

### Creating Web Identity Role

```bash
# Trust policy for web identity
cat > web-identity-trust.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "accounts.google.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "accounts.google.com:aud": "your-google-app-client-id"
                }
            }
        }
    ]
}
EOF

# Create role
aws iam create-role \
    --role-name WebIdentityRole \
    --assume-role-policy-document file://web-identity-trust.json

# Attach limited permissions
aws iam attach-role-policy \
    --role-name WebIdentityRole \
    --policy-arn arn:aws:iam::123456789012:policy/MobileAppAccess
```

### Using AssumeRoleWithWebIdentity

```bash
# Called from your application with the ID token
aws sts assume-role-with-web-identity \
    --role-arn arn:aws:iam::123456789012:role/WebIdentityRole \
    --role-session-name app-user-session \
    --web-identity-token eyJhbGc... \
    --duration-seconds 3600
```

---

## Amazon Cognito

### Why Cognito Instead of Direct Web Identity

```
+------------------------------------------------------------------+
|                  COGNITO BENEFITS                                 |
+------------------------------------------------------------------+
|                                                                   |
|  Direct Web Identity:                                            |
|  - Must handle each IdP separately                               |
|  - Complex token management                                       |
|  - No user data storage                                          |
|  - Limited to web identity providers                             |
|                                                                   |
|  Amazon Cognito:                                                 |
|  + Unified API for all identity providers                        |
|  + Handles token refresh automatically                           |
|  + User pools for user data storage                              |
|  + Supports unauthenticated (guest) access                       |
|  + Built-in security features                                    |
|  + Works with SAML and OIDC                                      |
|                                                                   |
+------------------------------------------------------------------+
```

### Cognito Architecture

```
+------------------------------------------------------------------+
|                  COGNITO COMPONENTS                               |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+         +------------------+                |
|  |   USER POOLS     |         | IDENTITY POOLS   |                |
|  +------------------+         +------------------+                |
|  |                  |         |                  |                |
|  | User Directory   |         | AWS Credentials  |                |
|  | - Sign up/in     |         | - Map identities |                |
|  | - User profiles  |         |   to IAM roles   |                |
|  | - MFA            |   --->  | - Auth users     |                |
|  | - Password rules |         | - Unauth users   |                |
|  | - Social sign-in |         | - Fine-grained   |                |
|  |                  |         |   access control |                |
|  +------------------+         +------------------+                |
|          |                            |                           |
|          v                            v                           |
|  +------------------+         +------------------+                |
|  |  JWT Tokens      |         |  AWS Temp Creds  |                |
|  |  - ID Token      |         |  - Access Key    |                |
|  |  - Access Token  |         |  - Secret Key    |                |
|  |  - Refresh Token |         |  - Session Token |                |
|  +------------------+         +------------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

### Setting Up Cognito Identity Pool

```bash
# Create identity pool
aws cognito-identity create-identity-pool \
    --identity-pool-name MyAppPool \
    --allow-unauthenticated-identities \
    --cognito-identity-providers \
        ProviderName=cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXXX,ClientId=YYYYYY

# Set up roles for the identity pool
aws cognito-identity set-identity-pool-roles \
    --identity-pool-id us-east-1:xxxxx-xxxx-xxxx-xxxx \
    --roles authenticated=arn:aws:iam::123456789012:role/Cognito_Auth_Role,unauthenticated=arn:aws:iam::123456789012:role/Cognito_Unauth_Role
```

### Cognito Trust Policies

```json
// For authenticated role
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "cognito-identity.amazonaws.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "cognito-identity.amazonaws.com:aud": "us-east-1:xxxxx-xxxx-xxxx"
                },
                "ForAnyValue:StringLike": {
                    "cognito-identity.amazonaws.com:amr": "authenticated"
                }
            }
        }
    ]
}

// For unauthenticated role
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "cognito-identity.amazonaws.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "cognito-identity.amazonaws.com:aud": "us-east-1:xxxxx-xxxx-xxxx"
                },
                "ForAnyValue:StringLike": {
                    "cognito-identity.amazonaws.com:amr": "unauthenticated"
                }
            }
        }
    ]
}
```

---

## AWS IAM Identity Center (AWS SSO)

### Overview

AWS IAM Identity Center (formerly AWS Single Sign-On) is the recommended way to manage human access to AWS accounts in an organization.

```
+------------------------------------------------------------------+
|               IAM IDENTITY CENTER ARCHITECTURE                    |
+------------------------------------------------------------------+
|                                                                   |
|  +------------------+                                             |
|  | Identity Source  |                                             |
|  +------------------+                                             |
|  | - Built-in store |                                             |
|  | - Active Directory|                                            |
|  | - External IdP   |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|           v                                                       |
|  +------------------+                                             |
|  | IAM Identity     |                                             |
|  | Center           |                                             |
|  +------------------+                                             |
|  | - Users & Groups |                                             |
|  | - Permission Sets|                                             |
|  | - AWS Account    |                                             |
|  |   Assignments    |                                             |
|  +--------+---------+                                             |
|           |                                                       |
|     +-----+-----+-----+-----+                                     |
|     |     |     |     |     |                                     |
|     v     v     v     v     v                                     |
|  +-----+-----+-----+-----+-----+                                  |
|  |Acct1|Acct2|Acct3|Acct4|Acct5|  AWS Accounts                   |
|  +-----+-----+-----+-----+-----+                                  |
|                                                                   |
+------------------------------------------------------------------+
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Identity Source** | Where users are defined (built-in, AD, or external IdP) |
| **Permission Set** | Collection of policies that define access level |
| **Account Assignment** | Links users/groups to accounts with permission sets |
| **Access Portal** | Web portal where users select accounts and roles |

### Setting Up IAM Identity Center

```bash
# Enable IAM Identity Center (in Organizations management account)
# This is typically done via console

# Create a permission set
aws sso-admin create-permission-set \
    --instance-arn arn:aws:sso:::instance/ssoins-xxx \
    --name "DeveloperAccess" \
    --description "Access for developers" \
    --session-duration PT8H

# Attach managed policy to permission set
aws sso-admin attach-managed-policy-to-permission-set \
    --instance-arn arn:aws:sso:::instance/ssoins-xxx \
    --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
    --managed-policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Create account assignment
aws sso-admin create-account-assignment \
    --instance-arn arn:aws:sso:::instance/ssoins-xxx \
    --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
    --principal-id "group-id" \
    --principal-type GROUP \
    --target-id "123456789012" \
    --target-type AWS_ACCOUNT
```

### Permission Set with Custom Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowDeveloperServices",
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "s3:*",
                "lambda:*",
                "dynamodb:*",
                "rds:*",
                "logs:*",
                "cloudwatch:*"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": [
                        "us-east-1",
                        "us-west-2"
                    ]
                }
            }
        },
        {
            "Sid": "DenyIAMChanges",
            "Effect": "Deny",
            "Action": [
                "iam:CreateUser",
                "iam:DeleteUser",
                "iam:CreateAccessKey",
                "iam:DeleteAccessKey"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Federation Decision Tree

```
                            START
                              |
                              v
                    +-------------------+
                    | Who needs access? |
                    +--------+----------+
                             |
        +--------------------+--------------------+
        |                    |                    |
   Employees            Mobile/Web           Partner/
   (Corporate)          App Users            Vendor
        |                    |                    |
        v                    v                    v
+---------------+    +---------------+    +---------------+
| How many AWS  |    | Do you need   |    | How many      |
| accounts?     |    | user profiles?|    | partners?     |
+-------+-------+    +-------+-------+    +-------+-------+
        |                    |                    |
   +----+----+          +----+----+          +----+----+
   |         |          |         |          |         |
Single    Multiple     YES       NO        Few       Many
   |         |          |         |          |         |
   v         v          v         v          v         v
+------+ +--------+ +-------+ +-------+ +-------+ +-------+
| SAML | | IAM    | | Cognito| | Direct | | Cross | | SAML  |
| with | | Identity| | User   | | Web ID | | Account| | for   |
| IAM  | | Center | | Pools  | | or     | | Roles | | each  |
+------+ | (SSO)  | +-------+ | Cognito| +-------+ +-------+
         +--------+           | Identity|
                              | Pools   |
                              +-------+
```

---

## Federation Comparison

| Feature | SAML | Web Identity | Cognito | IAM Identity Center |
|---------|------|--------------|---------|---------------------|
| **Best For** | Enterprise SSO | Consumer apps | Mobile/Web apps | Multi-account |
| **IdP Types** | Corporate | Social | Both | Both |
| **AWS Account** | Single/Multi | Single | Single | Multi (Org) |
| **User Directory** | External | External | Built-in + External | Built-in + External |
| **Setup Complexity** | Medium | Low | Medium | Low |
| **Token Management** | Manual | Manual | Automatic | Automatic |

---

## Security Considerations

### Federation Security Best Practices

```
+------------------------------------------------------------------+
|           FEDERATION SECURITY CHECKLIST                           |
+------------------------------------------------------------------+

[ ] Use HTTPS for all IdP communications
[ ] Validate SAML assertions thoroughly
[ ] Use short session durations (1-4 hours)
[ ] Implement proper token storage in applications
[ ] Rotate federation metadata regularly
[ ] Monitor federation logs in CloudTrail
[ ] Use condition keys in trust policies
[ ] Implement attribute-based access control (ABAC)
[ ] Regularly audit federated access
[ ] Have break-glass IAM users for emergencies

+------------------------------------------------------------------+
```

### CloudTrail Events for Federation

```bash
# Key events to monitor:
# - AssumeRoleWithSAML
# - AssumeRoleWithWebIdentity
# - GetFederationToken

# Search for federation events
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRoleWithSAML \
    --start-time $(date -d '24 hours ago' --iso-8601=seconds)
```

---

## Common Mistakes

### Mistake 1: Not Setting Session Duration

```json
// PROBLEM: Default session too long or too short

// SOLUTION: Set appropriate session duration
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::123456789012:saml-provider/IdP"
            },
            "Action": "sts:AssumeRoleWithSAML",
            "Condition": {
                "StringEquals": {
                    "SAML:aud": "https://signin.aws.amazon.com/saml"
                }
            }
        }
    ]
}

// Also set in SAML attributes:
// SessionDuration: 14400 (4 hours)
```

### Mistake 2: Overly Broad Trust Policies

```json
// PROBLEM: Any SAML assertion accepted
{
    "Principal": {
        "Federated": "arn:aws:iam::123456789012:saml-provider/IdP"
    },
    "Action": "sts:AssumeRoleWithSAML"
    // No conditions!
}

// SOLUTION: Add conditions
{
    "Principal": {
        "Federated": "arn:aws:iam::123456789012:saml-provider/IdP"
    },
    "Action": "sts:AssumeRoleWithSAML",
    "Condition": {
        "StringEquals": {
            "SAML:aud": "https://signin.aws.amazon.com/saml",
            "SAML:sub_type": "persistent"
        },
        "StringLike": {
            "SAML:sub": "*@company.com"
        }
    }
}
```

### Mistake 3: Not Monitoring Federation

```bash
# Create CloudWatch alarm for unusual federation activity
aws cloudwatch put-metric-alarm \
    --alarm-name UnusualFederationActivity \
    --metric-name FederationLoginCount \
    --namespace Custom/Federation \
    --statistic Sum \
    --period 3600 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

---

## Summary

| Federation Type | Use When |
|-----------------|----------|
| **SAML 2.0** | Enterprise SSO with corporate IdP |
| **Web Identity** | Simple social login for apps |
| **Cognito** | Full-featured mobile/web app auth |
| **IAM Identity Center** | Multi-account access for organization |

---

## Next Steps

Continue to [07-hands-on-labs.md](./07-hands-on-labs.md) to practice IAM concepts with hands-on exercises.
