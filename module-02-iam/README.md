# Module 02: AWS Identity and Access Management (IAM)

## Module Overview

Welcome to the AWS IAM module - arguably the most critical service you will learn in your AWS journey. IAM is the foundation of security in AWS, controlling who can access what resources and under what conditions.

```
+------------------------------------------------------------------+
|                        AWS ACCOUNT                                |
|  +------------------------------------------------------------+  |
|  |                         IAM                                 |  |
|  |                                                             |  |
|  |   +----------+    +----------+    +----------+              |  |
|  |   |  USERS   |    |  GROUPS  |    |  ROLES   |              |  |
|  |   +----+-----+    +----+-----+    +----+-----+              |  |
|  |        |              |              |                      |  |
|  |        v              v              v                      |  |
|  |   +------------------------------------------------+        |  |
|  |   |              POLICIES (Permissions)             |        |  |
|  |   +------------------------------------------------+        |  |
|  |                          |                                  |  |
|  +--------------------------|----------------------------------+  |
|                             v                                     |
|   +----------------------------------------------------------+   |
|   |                    AWS RESOURCES                          |   |
|   |  (S3, EC2, RDS, Lambda, DynamoDB, etc.)                  |   |
|   +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

---

## Why IAM is Critical

### The Security Foundation

IAM is not just another AWS service - it is THE service that determines:

1. **Authentication**: Proving WHO you are
2. **Authorization**: Determining WHAT you can do
3. **Accountability**: Tracking WHAT you did

### Real-World Consequences of IAM Misconfigurations

| Incident | Cause | Impact |
|----------|-------|--------|
| Capital One Breach (2019) | Misconfigured WAF + overly permissive IAM role | 100M+ customer records exposed |
| Tesla Kubernetes Hack (2018) | Exposed credentials, no MFA | Cryptomining on Tesla infrastructure |
| Code Spaces (2014) | Compromised root credentials | Complete business destruction |

### IAM by the Numbers

- **Free**: IAM is one of the few AWS services with no cost
- **Global**: IAM is not region-specific
- **Foundational**: Every AWS API call requires IAM authentication

---

## Learning Objectives

By the end of this module, you will be able to:

### Understanding (Knowledge)
- [ ] Explain the difference between authentication and authorization
- [ ] Describe the relationship between users, groups, roles, and policies
- [ ] Identify when to use IAM users vs IAM roles
- [ ] Understand the principle of least privilege

### Application (Skills)
- [ ] Create and manage IAM users and groups
- [ ] Write custom IAM policies in JSON format
- [ ] Configure IAM roles for AWS services
- [ ] Enable and enforce Multi-Factor Authentication (MFA)
- [ ] Use the AWS CLI for IAM operations

### Analysis (Security)
- [ ] Audit IAM configurations for security issues
- [ ] Use IAM Access Analyzer to identify resource sharing
- [ ] Implement IAM best practices in real-world scenarios
- [ ] Design secure cross-account access patterns

---

## Module Contents

| File | Topic | Duration |
|------|-------|----------|
| [01-iam-fundamentals.md](./01-iam-fundamentals.md) | Core IAM concepts with real-world analogies | 30 min |
| [02-iam-policies-deep-dive.md](./02-iam-policies-deep-dive.md) | JSON policy structure and policy types | 45 min |
| [03-iam-users-groups.md](./03-iam-users-groups.md) | Managing users, groups, and credentials | 30 min |
| [04-iam-roles.md](./04-iam-roles.md) | Understanding and using IAM roles | 45 min |
| [05-iam-best-practices.md](./05-iam-best-practices.md) | Security best practices and compliance | 30 min |
| [06-identity-federation.md](./06-identity-federation.md) | External identity integration | 30 min |
| [07-iam-access-analyzer.md](./07-iam-access-analyzer.md) | IAM Access Analyzer for security auditing | 30 min |
| [08-hands-on-lab.md](./08-hands-on-lab.md) | Comprehensive practical exercises | 120 min |
| [quiz.md](./quiz.md) | Knowledge assessment (30 questions) | 45 min |

**Total Estimated Time: 6-7 hours**

---

## Prerequisites

Before starting this module, ensure you have:

1. **AWS Account**: A personal AWS account (free tier eligible)
2. **Root Account Security**: Root account secured with MFA
3. **AWS CLI**: Installed and configured (optional but recommended)
4. **Basic JSON Knowledge**: Understanding of JSON syntax

### Verifying AWS CLI Installation

```bash
# Check AWS CLI version
aws --version

# Check current identity
aws sts get-caller-identity
```

---

## Key Terminology

| Term | Definition |
|------|------------|
| **Principal** | An entity that can make requests (user, role, service) |
| **Authentication** | Verifying the identity of a principal |
| **Authorization** | Determining what actions a principal can perform |
| **Policy** | A JSON document defining permissions |
| **ARN** | Amazon Resource Name - unique identifier for AWS resources |
| **MFA** | Multi-Factor Authentication |
| **Credential** | Secret information used for authentication (password, access key) |

---

## The IAM Mental Model

Think of IAM like a corporate security system:

```
REAL WORLD                          AWS IAM
-----------                         -------
Employee Badge          -->         IAM User/Role
Department              -->         IAM Group
Key Card Access Levels  -->         IAM Policy
Building/Rooms          -->         AWS Resources
Security Guard          -->         IAM Service
Visitor Pass            -->         Temporary Credentials
```

---

## Common Mistakes to Avoid

Before diving into the content, be aware of these common pitfalls:

1. **Using Root Account for Daily Tasks**
   - Never use root for regular operations
   - Create an IAM admin user immediately

2. **Overly Permissive Policies**
   - Avoid `"Action": "*"` and `"Resource": "*"`
   - Start restrictive, add permissions as needed

3. **Sharing Access Keys**
   - Each user should have their own credentials
   - Never commit access keys to code repositories

4. **Not Enabling MFA**
   - Enable MFA for all human users
   - Require MFA for sensitive operations

5. **Ignoring Unused Credentials**
   - Regularly audit and rotate credentials
   - Remove access for departed employees immediately

---

## How to Use This Module

### Recommended Approach

1. **Read sequentially**: Files are numbered for a reason
2. **Practice immediately**: Don't wait to try the labs
3. **Take notes**: Write down concepts in your own words
4. **Ask "why"**: Understanding the reasoning helps retention

### Learning Checkpoints

After each file, you should be able to answer:
- What did I learn?
- Why is this important?
- How would I use this in practice?

---

## Quick Reference Card

### IAM Entity Comparison

```
+-------------+------------------+------------------+------------------+
|             |      USER        |      GROUP       |      ROLE        |
+-------------+------------------+------------------+------------------+
| Identity    | Specific person  | Collection of    | Assumable by     |
|             | or application   | users            | anyone/anything  |
+-------------+------------------+------------------+------------------+
| Credentials | Password +       | None (inherits   | Temporary via    |
|             | Access Keys      | from users)      | STS              |
+-------------+------------------+------------------+------------------+
| Use Case    | Human users,     | Organize users   | Services, cross- |
|             | service accounts | by function      | account, federat.|
+-------------+------------------+------------------+------------------+
| Policies    | Attached         | Attached (users  | Attached         |
|             | directly         | inherit)         | directly         |
+-------------+------------------+------------------+------------------+
```

### Essential AWS CLI Commands

```bash
# Users
aws iam create-user --user-name <username>
aws iam list-users

# Groups
aws iam create-group --group-name <groupname>
aws iam add-user-to-group --user-name <user> --group-name <group>

# Policies
aws iam create-policy --policy-name <name> --policy-document file://policy.json
aws iam attach-user-policy --user-name <user> --policy-arn <arn>

# Roles
aws iam create-role --role-name <name> --assume-role-policy-document file://trust.json
aws sts assume-role --role-arn <arn> --role-session-name <session>
```

---

## Additional Resources

### AWS Documentation
- [IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)

### Tools
- [AWS Policy Simulator](https://policysim.aws.amazon.com/)
- [IAM Policy Generator](https://awspolicygen.s3.amazonaws.com/policygen.html)
- [AWS CloudFormation IAM Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html)

---

## Ready to Begin?

Start with [01-iam-fundamentals.md](./01-iam-fundamentals.md) to learn the core concepts of IAM.

Remember: **Security is not optional. It's foundational.**

---

*Module Version: 1.0*
*Last Updated: January 2025*
*Author: AWS Training Team*
