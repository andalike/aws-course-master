# AWS Cloud Practitioner to Solutions Architect Course

## From Zero to Mid-Level AWS Professional

Welcome to the most comprehensive, hands-on AWS course designed to take you from absolute beginner to a mid-level AWS professional. This course is completely self-sufficient - no prior cloud experience required!

---

## Course Overview

| Attribute | Details |
|-----------|---------|
| **Duration** | Self-paced (recommended 8-12 weeks) |
| **Level** | Beginner to Intermediate |
| **Prerequisites** | Basic computer literacy, command line familiarity helpful |
| **Hands-on Labs** | 70+ practical exercises |
| **Quizzes** | 200+ assessment questions |
| **Projects** | 5 real-world projects |

---

## Learning Path

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AWS LEARNING PATH                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FOUNDATION (Weeks 1-2)                                                     │
│  ┌──────────────┐    ┌──────────────┐                                       │
│  │  Module 1    │───▶│  Module 2    │                                       │
│  │ Fundamentals │    │    IAM       │                                       │
│  └──────────────┘    └──────────────┘                                       │
│                                                                              │
│  CORE SERVICES (Weeks 3-5)                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  Module 3    │───▶│  Module 4    │───▶│  Module 5    │                   │
│  │    EC2       │    │     S3       │    │    VPC       │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
│  DATA & SERVERLESS (Weeks 6-8)                                              │
│  ┌──────────────┐    ┌──────────────┐                                       │
│  │  Module 6    │───▶│  Module 7    │                                       │
│  │   RDS/DB     │    │   Lambda     │                                       │
│  └──────────────┘    └──────────────┘                                       │
│                                                                              │
│  OPERATIONS & SECURITY (Weeks 9-12)                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  Module 8    │───▶│  Module 9    │───▶│  Module 10   │                   │
│  │ CloudWatch   │    │ CloudForm.   │    │  Security    │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Modules

### Foundation

| Module | Title | Topics | Labs |
|--------|-------|--------|------|
| [Module 1](./module-01-fundamentals/) | AWS Fundamentals | Cloud computing, AWS Console, CLI setup | 3 |
| [Module 2](./module-02-iam/) | Identity & Access Management | Users, Groups, Roles, Policies | 5 |

### Core Services

| Module | Title | Topics | Labs |
|--------|-------|--------|------|
| [Module 3](./module-03-ec2/) | Elastic Compute Cloud | Instances, AMIs, Auto Scaling, ELB | 7 |
| [Module 4](./module-04-s3/) | Simple Storage Service | Buckets, Storage Classes, Static Hosting | 8 |
| [Module 5](./module-05-vpc-networking/) | VPC & Networking | Subnets, Route 53, CloudFront | 8 |

### Data & Serverless

| Module | Title | Topics | Labs |
|--------|-------|--------|------|
| [Module 6](./module-06-rds-databases/) | Databases | RDS, DynamoDB, ElastiCache | 7 |
| [Module 7](./module-07-lambda-serverless/) | Serverless | Lambda, API Gateway, Step Functions | 10 |

### Operations & Security

| Module | Title | Topics | Labs |
|--------|-------|--------|------|
| [Module 8](./module-08-cloudwatch-monitoring/) | Monitoring | CloudWatch, X-Ray, CloudTrail | 8 |
| [Module 9](./module-09-cloudformation-iac/) | Infrastructure as Code | CloudFormation, CDK | 8 |
| [Module 10](./module-10-security-cost-optimization/) | Security & Cost | GuardDuty, WAF, Cost Optimization | 8 |

---

## Capstone Projects

After completing the modules, test your skills with these real-world projects:

| Project | Description | Services Used |
|---------|-------------|---------------|
| [Project 1](./projects/01-static-website/) | Host a Static Website | S3, CloudFront, Route 53 |
| [Project 2](./projects/02-web-application/) | Deploy a Web Application | EC2, RDS, ALB, Auto Scaling |
| [Project 3](./projects/03-serverless-api/) | Build a Serverless API | Lambda, API Gateway, DynamoDB |
| [Project 4](./projects/04-data-pipeline/) | Create a Data Pipeline | S3, Lambda, SNS, SQS |
| [Project 5](./projects/05-complete-infrastructure/) | Complete Infrastructure | VPC, EC2, RDS, CloudFormation |

---

## How to Use This Course

### For Self-Study

1. **Start with Module 1** - Don't skip the fundamentals!
2. **Complete all hands-on labs** - Reading isn't enough
3. **Take the quizzes** - Test your understanding
4. **Build the projects** - Apply what you've learned
5. **Review and repeat** - Reinforce your knowledge

### For Instructors

This course can be delivered as:
- 8-week bootcamp (5-6 hours/week)
- 12-week part-time course (3-4 hours/week)
- Self-paced with checkpoints

---

## Prerequisites Setup

Before starting, ensure you have:

### 1. AWS Account (Free Tier)
```bash
# Sign up at: https://aws.amazon.com/free/
# Set up MFA immediately after creating account
```

### 2. AWS CLI Installed
```bash
# macOS
brew install awscli

# Windows
choco install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

### 3. Code Editor
- Recommended: VS Code with AWS Toolkit extension

### 4. Terminal/Shell
- macOS/Linux: Built-in terminal
- Windows: PowerShell or WSL2 (recommended)

---

## Cost Considerations

This course is designed to use AWS Free Tier wherever possible.

| Service | Free Tier Limit |
|---------|----------------|
| EC2 | 750 hours/month t2.micro |
| S3 | 5 GB storage |
| RDS | 750 hours/month db.t2.micro |
| Lambda | 1M requests/month |
| DynamoDB | 25 GB storage |

**Estimated cost if you exceed Free Tier**: $5-20/month

> **Warning**: Always clean up resources after labs to avoid unexpected charges!

---

## Learning Objectives

By completing this course, you will be able to:

### Foundation Skills
- [ ] Understand cloud computing concepts and AWS global infrastructure
- [ ] Navigate the AWS Console and use AWS CLI effectively
- [ ] Implement secure IAM policies following best practices

### Compute & Storage
- [ ] Launch and manage EC2 instances with Auto Scaling
- [ ] Configure load balancers for high availability
- [ ] Use S3 for various storage scenarios
- [ ] Design VPCs with proper network segmentation

### Data & Applications
- [ ] Deploy and manage RDS databases
- [ ] Build serverless applications with Lambda
- [ ] Create APIs with API Gateway

### Operations
- [ ] Monitor applications with CloudWatch
- [ ] Implement infrastructure as code with CloudFormation
- [ ] Apply security best practices and optimize costs

---

## Certification Path

This course prepares you for:

```
┌────────────────────────────────────────────────────────────────┐
│                    CERTIFICATION PATH                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  This Course Covers:                                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  AWS Cloud Practitioner (CLF-C02)         ✓ COVERED     │  │
│  │  - 100% of exam objectives                               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  AWS Solutions Architect Associate (SAA-C03)  ✓ COVERED │  │
│  │  - ~80% of exam objectives                               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                    │
│                           ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Additional Study Recommended for:                       │  │
│  │  - AWS Developer Associate                               │  │
│  │  - AWS SysOps Administrator                              │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Support & Community

- **Issues**: Open a GitHub issue for questions or problems
- **Discussions**: Use GitHub Discussions for community help
- **Updates**: Star and watch this repo for updates

---

## Contributors

This course was created by a team of AWS experts:

| Role | Expertise |
|------|-----------|
| Module Authors (10) | AWS Certified Solutions Architects |
| Technical Reviewers (2) | Senior AWS Engineers |
| Course Manager | AWS Training Lead |

---

## License

This course is provided under MIT License. Feel free to use for personal learning or teaching.

---

## Quick Start

Ready to begin? Start here:

```bash
# Clone this repository
git clone https://github.com/yourusername/aws-course.git

# Navigate to Module 1
cd aws-course/module-01-fundamentals

# Open the README and start learning!
```

**[Start Module 1: AWS Fundamentals →](./module-01-fundamentals/)**

---

*Last Updated: January 2026*
