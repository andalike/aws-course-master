# IAM Module Quiz

## Instructions

This quiz contains 30 questions covering all IAM topics from this module. Test your understanding of IAM concepts, policies, roles, and best practices.

**Question Types:**
- Multiple Choice (select one answer)
- True/False
- Scenario-Based (apply knowledge to real situations)

**Recommended Time:** 45 minutes

**Passing Score:** 80% (24 out of 30 questions)

---

## Section 1: IAM Fundamentals (Questions 1-8)

### Question 1
**What is the primary difference between authentication and authorization in AWS IAM?**

A) Authentication determines what you can do; authorization verifies who you are
B) Authentication verifies who you are; authorization determines what you can do
C) Authentication and authorization are the same thing
D) Authentication is for users; authorization is for roles

---

### Question 2
**Which of the following statements about IAM is TRUE?**

A) IAM is a regional service, and you must configure it in each region
B) IAM is a global service, and configurations apply across all regions
C) IAM is only available in the US regions
D) IAM requires additional setup fees based on the number of users

---

### Question 3
**True or False: IAM groups can contain other IAM groups (nested groups).**

A) True
B) False

---

### Question 4
**An IAM user can belong to a maximum of how many groups?**

A) 5 groups
B) 10 groups
C) 15 groups
D) Unlimited groups

---

### Question 5
**Which entity should you use when an EC2 instance needs to access S3?**

A) IAM User with access keys stored on the instance
B) IAM Group with S3 permissions
C) IAM Role with a trust policy for ec2.amazonaws.com
D) Root account credentials

---

### Question 6
**What is an ARN (Amazon Resource Name)?**

A) A password used to authenticate to AWS
B) A unique identifier for AWS resources
C) A type of IAM policy
D) An encryption key

---

### Question 7
**True or False: When you create a new IAM user, they have no permissions by default.**

A) True
B) False

---

### Question 8
**Which of the following is NOT a type of IAM credential?**

A) Console password
B) Access keys
C) SSH keys for EC2
D) MFA virtual device

---

## Section 2: IAM Policies (Questions 9-16)

### Question 9
**In an IAM policy, what does the "Principal" element specify?**

A) The actions that are allowed or denied
B) The resources the policy applies to
C) The entity (user, role, service) that is allowed or denied access
D) The conditions under which the policy applies

---

### Question 10
**Given the following policy, what access does it provide?**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        },
        {
            "Effect": "Deny",
            "Action": "s3:DeleteBucket",
            "Resource": "*"
        }
    ]
}
```

A) Full S3 access including DeleteBucket
B) No S3 access at all
C) Full S3 access except DeleteBucket
D) Only DeleteBucket access

---

### Question 11
**What is the correct order of policy evaluation in AWS?**

A) Explicit Allow > Explicit Deny > Implicit Deny
B) Explicit Deny > Explicit Allow > Implicit Deny
C) Implicit Deny > Explicit Allow > Explicit Deny
D) Explicit Allow > Implicit Deny > Explicit Deny

---

### Question 12
**Which policy type CANNOT be modified after creation?**

A) Customer Managed Policies
B) Inline Policies
C) AWS Managed Policies
D) Service Control Policies

---

### Question 13
**What is the maximum size of a customer managed policy?**

A) 2 KB
B) 6 KB
C) 10 KB
D) Unlimited

---

### Question 14
**True or False: In a policy condition, multiple values for the same condition key are evaluated with OR logic.**

A) True
B) False

---

### Question 15
**Which condition key would you use to require MFA for an action?**

A) aws:RequireMFA
B) aws:MultiFactorAuthPresent
C) aws:MFARequired
D) iam:MFAAuthenticated

---

### Question 16
**In the following resource ARN, what does the empty field represent?**
```
arn:aws:s3:::my-bucket
```

A) The ARN is invalid
B) Region - S3 is a global service
C) Account ID - S3 bucket names are globally unique
D) Both B and C

---

## Section 3: IAM Roles (Questions 17-22)

### Question 17
**What is a Trust Policy in an IAM Role?**

A) A policy that defines what actions the role can perform
B) A policy that defines who or what can assume the role
C) A policy that encrypts role credentials
D) A policy attached to users who want to use the role

---

### Question 18
**When assuming a role, what type of credentials are provided?**

A) Permanent access keys
B) Console password
C) Temporary security credentials
D) SSH key pair

---

### Question 19
**What is an Instance Profile?**

A) A configuration file on an EC2 instance
B) A container for an IAM role that allows EC2 to assume it
C) A type of security group
D) A logging mechanism for EC2

---

### Question 20
**What is the purpose of an External ID in cross-account role assumption?**

A) To encrypt the role credentials
B) To prevent the "confused deputy" problem
C) To identify the AWS region
D) To set the session duration

---

### Question 21
**Which STS API call is used to assume a role from a SAML identity provider?**

A) AssumeRole
B) AssumeRoleWithWebIdentity
C) AssumeRoleWithSAML
D) GetFederationToken

---

### Question 22
**True or False: Service-linked roles can have their permissions modified by customers.**

A) True
B) False

---

## Section 4: Security Best Practices (Questions 23-27)

### Question 23
**According to AWS best practices, when should you use the root account?**

A) For daily administrative tasks
B) When you need full access to all services
C) Only for specific tasks that require root (like changing account settings)
D) When MFA is not available

---

### Question 24
**What is the recommended maximum age for access keys before rotation?**

A) 30 days
B) 60 days
C) 90 days
D) 365 days

---

### Question 25
**Which of the following is the BEST practice for assigning permissions to users?**

A) Attach policies directly to each user
B) Use inline policies for each user
C) Create groups with appropriate policies and add users to groups
D) Give all users AdministratorAccess and trust them

---

### Question 26
**What is a Permission Boundary?**

A) A network boundary that restricts access
B) A managed policy that sets the maximum permissions an identity can have
C) The border between two AWS accounts
D) A limit on the number of policies you can attach

---

### Question 27
**True or False: You should enable MFA for all human IAM users, especially those with console access.**

A) True
B) False

---

## Section 5: Scenario-Based Questions (Questions 28-30)

### Question 28
**Scenario:** Your company has 500 developers across 10 teams. Each team needs different levels of access to AWS resources. What is the BEST approach?

A) Create 500 IAM users with inline policies customized for each developer
B) Create IAM groups for each team, attach appropriate policies to groups, and add developers to their team groups
C) Give all developers AdministratorAccess and monitor with CloudTrail
D) Create one shared IAM user per team

---

### Question 29
**Scenario:** A Lambda function needs to read from a DynamoDB table and write to an S3 bucket. How should you configure access?

A) Create an IAM user with access keys and hardcode them in the Lambda function
B) Create an IAM role with appropriate permissions and assign it as the Lambda execution role
C) Attach policies directly to the Lambda function
D) Use the root account credentials in environment variables

---

### Question 30
**Scenario:** You discover that an S3 bucket in your account is publicly accessible. IAM Access Analyzer has flagged this as a finding. What is the correct sequence of actions?

A) Immediately delete the bucket
B) Archive the finding since it's probably intentional
C) Investigate the finding, determine if access is intentional, remediate if not, then document or archive
D) Ignore the finding - Access Analyzer has too many false positives

---

## Answer Key

Scroll down for answers with detailed explanations.

.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.

---

# Answers and Explanations

## Section 1: IAM Fundamentals

### Answer 1: B
**Authentication verifies who you are; authorization determines what you can do**

- **Authentication** = "Who are you?" (login process, credentials)
- **Authorization** = "What can you do?" (permissions, policies)

This is a fundamental security concept. AWS IAM handles both: authentication through passwords/access keys/MFA, and authorization through policies.

---

### Answer 2: B
**IAM is a global service, and configurations apply across all regions**

IAM is one of the few AWS services that is truly global:
- Users, groups, roles, and policies are available in all regions
- No need to replicate IAM configurations
- IAM is also free - no charges for users, groups, or policies

---

### Answer 3: B
**False**

IAM groups CANNOT contain other groups. Groups can only contain users. This is a common exam trick question.

```
ALLOWED:
Group --> User
Group --> User
Group --> User

NOT ALLOWED:
Group --> Group --> User
```

---

### Answer 4: B
**10 groups**

An IAM user can be a member of a maximum of 10 groups. This is a hard limit set by AWS.

---

### Answer 5: C
**IAM Role with a trust policy for ec2.amazonaws.com**

Using IAM roles for EC2 instances is the best practice because:
- No credentials stored on the instance
- Automatic credential rotation
- Credentials obtained via Instance Metadata Service
- No risk of credential leakage in code

Never store access keys on EC2 instances.

---

### Answer 6: B
**A unique identifier for AWS resources**

ARN = Amazon Resource Name. Format:
```
arn:partition:service:region:account-id:resource
```

Examples:
- `arn:aws:s3:::my-bucket`
- `arn:aws:iam::123456789012:user/john`
- `arn:aws:ec2:us-east-1:123456789012:instance/i-12345`

---

### Answer 7: A
**True**

New IAM users have NO permissions by default (implicit deny). You must explicitly grant permissions through:
- Group membership (recommended)
- Attached managed policies
- Inline policies

This follows the principle of least privilege.

---

### Answer 8: C
**SSH keys for EC2**

SSH keys for EC2 are not IAM credentials - they are EC2 key pairs used for SSH access to instances.

IAM credentials include:
- Console password (for AWS Console)
- Access keys (for CLI/SDK/API)
- MFA devices (for additional authentication)
- Signing certificates (for specific services)

---

## Section 2: IAM Policies

### Answer 9: C
**The entity (user, role, service) that is allowed or denied access**

The Principal element specifies WHO the policy applies to. It's used in:
- Resource-based policies (S3 bucket policies, role trust policies)
- NOT in identity-based policies (the identity IS the principal)

Example:
```json
"Principal": {
    "AWS": "arn:aws:iam::123456789012:user/john"
}
```

---

### Answer 10: C
**Full S3 access except DeleteBucket**

This is the key rule: **Explicit Deny ALWAYS wins**.

- First statement: Allow all S3 actions
- Second statement: Explicitly deny DeleteBucket
- Result: All S3 actions except DeleteBucket are allowed

---

### Answer 11: B
**Explicit Deny > Explicit Allow > Implicit Deny**

The evaluation order is:
1. By default, everything is denied (implicit deny)
2. If there's an explicit Allow, access is granted
3. BUT if there's any explicit Deny, access is denied regardless of any Allows

Remember: **Deny always wins!**

---

### Answer 12: C
**AWS Managed Policies**

AWS Managed Policies are created and maintained by AWS. You cannot modify them, but you can:
- Attach/detach them from identities
- View their permissions
- AWS updates them automatically when new features are added

---

### Answer 13: B
**6 KB**

Policy size limits:
- Inline policy: 2 KB per user, 5 KB per group, 10 KB per role
- Customer managed policy: 6 KB
- If you exceed limits, split into multiple policies

---

### Answer 14: A
**True**

Condition logic:
- Multiple values for the SAME key = OR (any match)
- Multiple DIFFERENT keys = AND (all must match)

```json
"Condition": {
    "IpAddress": {
        "aws:SourceIp": ["10.0.0.0/8", "192.168.0.0/16"]  // OR
    },
    "Bool": {
        "aws:SecureTransport": "true"  // AND with above
    }
}
```

---

### Answer 15: B
**aws:MultiFactorAuthPresent**

This condition key checks if MFA was used during authentication:
```json
"Condition": {
    "Bool": {
        "aws:MultiFactorAuthPresent": "true"
    }
}
```

Use `BoolIfExists` for more robust checking.

---

### Answer 16: D
**Both B and C**

S3 bucket ARNs have empty region and account-id fields because:
- S3 is a global service (no region)
- Bucket names are globally unique (account not needed)

Format: `arn:aws:s3:::bucket-name`

---

## Section 3: IAM Roles

### Answer 17: B
**A policy that defines who or what can assume the role**

A role has two types of policies:
1. **Trust Policy** (AssumeRolePolicyDocument): WHO can assume the role
2. **Permission Policies**: WHAT the role can do once assumed

```json
// Trust Policy Example
{
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
}
```

---

### Answer 18: C
**Temporary security credentials**

When you assume a role, STS provides:
- AccessKeyId
- SecretAccessKey
- SessionToken
- Expiration time

These are temporary (1 hour by default, configurable 1-12 hours) and automatically rotated.

---

### Answer 19: B
**A container for an IAM role that allows EC2 to assume it**

EC2 instances cannot directly assume roles. They need an Instance Profile:

```
EC2 Instance --> Instance Profile --> IAM Role --> Permissions
```

When you attach a role to EC2 via console, AWS automatically creates the instance profile.

---

### Answer 20: B
**To prevent the "confused deputy" problem**

The External ID is a shared secret between you and the third party:
- Prevents malicious actors from using another customer's role ARN
- Should be unique per customer/partner
- Required in the trust policy condition

---

### Answer 21: C
**AssumeRoleWithSAML**

STS API calls for role assumption:
- `AssumeRole`: For IAM users/roles
- `AssumeRoleWithSAML`: For SAML federation (enterprise SSO)
- `AssumeRoleWithWebIdentity`: For web identity providers (Google, Facebook)
- `GetFederationToken`: For custom federation

---

### Answer 22: B
**False**

Service-linked roles:
- Created and managed by AWS services
- Have predefined permissions that cannot be modified
- Named pattern: `AWSServiceRoleFor<ServiceName>`
- Can only be deleted after the service no longer needs them

---

## Section 4: Security Best Practices

### Answer 23: C
**Only for specific tasks that require root**

Root account should ONLY be used for:
- Changing account settings (email, password)
- Closing the AWS account
- Changing support plans
- Restoring IAM access if locked out
- Viewing certain billing reports

Enable MFA on root immediately and do NOT create access keys for root.

---

### Answer 24: C
**90 days**

AWS recommends rotating access keys every 90 days:
- Reduces exposure window if keys are compromised
- Can be enforced via AWS Config rules
- Rotation process: Create new key, update apps, deactivate old key, delete old key

---

### Answer 25: C
**Create groups with appropriate policies and add users to groups**

Best practice for permissions:
1. Create groups by job function (Developers, Admins, Auditors)
2. Attach policies to groups
3. Add users to appropriate groups
4. Users inherit group permissions

Benefits: Easier management, consistent permissions, simpler auditing.

---

### Answer 26: B
**A managed policy that sets the maximum permissions an identity can have**

Permission Boundaries:
- Set the maximum permissions possible
- Effective permissions = Identity Policy INTERSECTION Boundary
- Used for delegation (give admins ability to create users with limits)

Even if you attach AdministratorAccess, the boundary limits actual permissions.

---

### Answer 27: A
**True**

MFA should be enabled for ALL human users, especially:
- Console users
- Users with admin access
- Users who can access sensitive data
- Root account (critical!)

Consider requiring MFA for sensitive API actions via policy conditions.

---

## Section 5: Scenario-Based Questions

### Answer 28: B
**Create IAM groups for each team, attach appropriate policies to groups, and add developers to their team groups**

This is the standard best practice:
- Groups by team/function
- Policies attached to groups
- Users inherit permissions from group membership
- Easy to update: change group policy, all members affected

Options A (500 inline policies) and D (shared users) are security anti-patterns.

---

### Answer 29: B
**Create an IAM role with appropriate permissions and assign it as the Lambda execution role**

For AWS services like Lambda:
- Always use IAM roles
- Never use access keys in code or environment variables
- Role provides automatic credential rotation
- Least privilege: only DynamoDB read + S3 write permissions

---

### Answer 30: C
**Investigate the finding, determine if access is intentional, remediate if not, then document or archive**

Proper Access Analyzer workflow:
1. **Investigate**: Review the finding details
2. **Determine intent**: Is this access supposed to exist?
3. **If unintentional**: Remediate by updating the policy
4. **If intentional**: Document why and archive the finding
5. **Monitor**: Set up alerts for new findings

Never ignore findings or delete resources without investigation.

---

## Scoring Guide

| Score | Rating | Recommendation |
|-------|--------|----------------|
| 27-30 | Excellent | Ready for advanced topics |
| 24-26 | Good | Review missed concepts |
| 20-23 | Fair | Revisit the module content |
| Below 20 | Needs Improvement | Re-read all lessons and complete labs again |

---

## Topics to Review by Question

If you missed questions in specific areas, review these lessons:

| Questions | Topic | Lesson |
|-----------|-------|--------|
| 1-8 | IAM Fundamentals | 01-iam-fundamentals.md |
| 9-16 | IAM Policies | 02-iam-policies-deep-dive.md |
| 17-22 | IAM Roles | 04-iam-roles.md |
| 23-27 | Best Practices | 05-iam-best-practices.md |
| 28-30 | Scenario Application | All lessons + 08-hands-on-lab.md |

---

## Next Steps

Congratulations on completing the IAM module!

**If you scored 80% or higher:**
- Proceed to the next module
- Consider getting AWS Certified (IAM is heavily tested)

**If you scored below 80%:**
- Review the lessons for topics you missed
- Redo the hands-on lab
- Retake the quiz in a few days

---

*Quiz Version: 1.0*
*Last Updated: January 2025*
