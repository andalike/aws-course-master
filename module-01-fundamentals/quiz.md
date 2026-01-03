# Module 01 Quiz: AWS Fundamentals

## Quiz Overview

| Attribute | Details |
|-----------|---------|
| **Number of Questions** | 15 |
| **Estimated Time** | 20 minutes |
| **Passing Score** | 80% (12/15 correct) |
| **Attempts** | Unlimited |

---

## Instructions

1. Read each question carefully
2. Select the best answer(s)
3. Check your answers at the end
4. Review explanations for any questions you missed

---

## Questions

### Question 1: Cloud Computing Basics

**Which of the following BEST describes cloud computing?**

A) Storing all data on local hard drives for security

B) The delivery of computing services over the internet on a pay-as-you-go basis

C) Running applications only on company-owned physical servers

D) Using USB drives to transfer data between computers

---

### Question 2: Service Models

**A company wants to deploy their application without managing the underlying servers, operating systems, or runtime environments. Which cloud service model should they use?**

A) Infrastructure as a Service (IaaS)

B) Platform as a Service (PaaS)

C) Software as a Service (SaaS)

D) Hardware as a Service (HaaS)

---

### Question 3: AWS Global Infrastructure

**Which AWS component is designed to achieve fault isolation and consists of one or more discrete data centers?**

A) Region

B) Availability Zone

C) Edge Location

D) Local Zone

---

### Question 4: Regions and Availability Zones

**An AWS Region typically contains:**

A) Exactly one Availability Zone

B) At least two Availability Zones

C) Exactly three Availability Zones

D) Only Edge Locations, no Availability Zones

---

### Question 5: Edge Locations

**What is the primary purpose of AWS Edge Locations?**

A) Running EC2 instances

B) Hosting RDS databases

C) Caching content closer to users for lower latency

D) Storing S3 buckets

---

### Question 6: Account Security

**Which security feature should you IMMEDIATELY enable after creating an AWS account to protect the root user?**

A) AWS Shield

B) Multi-Factor Authentication (MFA)

C) AWS WAF

D) Security Groups

---

### Question 7: Root User Best Practices

**Which of the following is a recommended best practice for the AWS root user?**

A) Use the root user for all daily operations

B) Create access keys for the root user for CLI access

C) Share root credentials with your team for collaboration

D) Enable MFA and avoid using root for everyday tasks

---

### Question 8: AWS CLI

**After installing AWS CLI, which command is used to configure credentials?**

A) `aws setup`

B) `aws configure`

C) `aws credentials`

D) `aws login`

---

### Question 9: Free Tier Types

**Which AWS Free Tier type never expires and provides free usage within limits regardless of how long you've had your account?**

A) 12 Months Free

B) Trial Free Tier

C) Always Free

D) Premium Free Tier

---

### Question 10: EC2 Free Tier

**A developer has been running ONE t2.micro Linux instance 24/7 for 30 days. They then launch a SECOND t2.micro instance that runs 24/7. What will happen to their Free Tier EC2 usage?**

A) Nothing, each instance has its own 750-hour limit

B) They will exceed the 750-hour monthly limit and be charged for overage

C) AWS automatically stops the second instance to prevent charges

D) The Free Tier automatically doubles to accommodate both instances

---

### Question 11: AWS Console Navigation

**What is the FASTEST way to find a specific AWS service in the AWS Management Console?**

A) Click through the Services menu alphabetically

B) Use the search bar in the navigation header

C) Open each service category until you find it

D) Use the AWS CLI instead

---

### Question 12: CloudShell

**Which of the following statements about AWS CloudShell is TRUE?**

A) CloudShell requires you to install the AWS CLI separately

B) CloudShell provides a browser-based shell with pre-installed AWS CLI

C) CloudShell can only run PowerShell commands

D) CloudShell requires additional charges beyond Free Tier

---

### Question 13: Region Selection Factors

**When choosing an AWS Region for your application, which of the following is NOT a relevant consideration?**

A) Latency to end users

B) Data residency and compliance requirements

C) Service availability in the region

D) The color of the AWS Console theme

---

### Question 14: S3 Bucket Naming

**Which of the following is a valid S3 bucket name?**

A) My_First_Bucket

B) my-first-bucket-2024

C) MyFirstBucket

D) 192.168.1.1

---

### Question 15: AWS Account ID

**How many digits are in an AWS Account ID?**

A) 8 digits

B) 10 digits

C) 12 digits

D) 16 digits

---

## Answer Key

Scroll down to see the answers...

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

## Answers and Explanations

### Question 1: Answer - B

**The delivery of computing services over the internet on a pay-as-you-go basis**

**Explanation:** Cloud computing is defined as the on-demand delivery of IT resources over the internet with pay-as-you-go pricing. Instead of buying, owning, and maintaining physical data centers and servers, you can access technology services from a cloud provider.

---

### Question 2: Answer - B

**Platform as a Service (PaaS)**

**Explanation:**
- **IaaS:** You manage OS, runtime, and application (e.g., EC2)
- **PaaS:** Provider manages OS and runtime; you manage application and data (e.g., Elastic Beanstalk, Lambda)
- **SaaS:** Provider manages everything; you just use the software (e.g., Gmail, Salesforce)

---

### Question 3: Answer - B

**Availability Zone**

**Explanation:** An Availability Zone (AZ) is one or more discrete data centers with redundant power, networking, and connectivity in an AWS Region. AZs are designed to be isolated from failures in other AZs while being connected via high-speed, low-latency networks.

---

### Question 4: Answer - B

**At least two Availability Zones**

**Explanation:** Every AWS Region has a minimum of two Availability Zones (most have three or more) to provide redundancy and fault tolerance. This allows customers to design highly available applications that can survive the failure of a single AZ.

---

### Question 5: Answer - C

**Caching content closer to users for lower latency**

**Explanation:** Edge Locations are endpoints for AWS services like CloudFront and Route 53. They cache copies of content closer to end users, reducing latency. There are more Edge Locations (450+) than Regions, providing broad geographic coverage for content delivery.

---

### Question 6: Answer - B

**Multi-Factor Authentication (MFA)**

**Explanation:** MFA adds an extra layer of security beyond just a password. Even if someone obtains your password, they cannot access your account without the MFA device. This is especially critical for the root user, which has unrestricted access to the entire account.

---

### Question 7: Answer - D

**Enable MFA and avoid using root for everyday tasks**

**Explanation:** The root user has unrestricted access and cannot be limited by IAM policies. Best practices include:
- Enable MFA immediately
- Do NOT create access keys for root
- Do NOT use root for daily operations
- Create IAM users with appropriate permissions for everyday tasks

---

### Question 8: Answer - B

**`aws configure`**

**Explanation:** The `aws configure` command is used to set up your AWS CLI credentials and default settings, including Access Key ID, Secret Access Key, default region, and output format. Credentials are stored in `~/.aws/credentials`.

---

### Question 9: Answer - C

**Always Free**

**Explanation:** AWS Free Tier has three types:
- **Always Free:** Never expires (e.g., Lambda 1M requests/month)
- **12 Months Free:** Free for 12 months from account creation (e.g., EC2 t2.micro)
- **Trials:** Short-term free trials for specific services

---

### Question 10: Answer - B

**They will exceed the 750-hour monthly limit and be charged for overage**

**Explanation:** The 750 hours of EC2 Free Tier is a TOTAL across all t2.micro instances, not per instance. Running two t2.micro instances 24/7 for 30 days = 1,440 hours, which exceeds the 750-hour limit by 690 hours. These extra hours will be charged.

---

### Question 11: Answer - B

**Use the search bar in the navigation header**

**Explanation:** The unified search bar is the fastest way to find services, features, documentation, and even specific actions. Keyboard shortcut: `Alt+S` (Windows/Linux) or `Option+S` (Mac).

---

### Question 12: Answer - B

**CloudShell provides a browser-based shell with pre-installed AWS CLI**

**Explanation:** AWS CloudShell is a browser-based shell with:
- Pre-installed AWS CLI (already configured with your session credentials)
- 1 GB of persistent storage
- Common development tools (Python, Node.js, git)
- No additional charge (included with your AWS account)

---

### Question 13: Answer - D

**The color of the AWS Console theme**

**Explanation:** When choosing a Region, consider:
- **Latency:** Closer regions = lower latency
- **Compliance:** Data residency laws (GDPR, etc.)
- **Service availability:** Not all services are in all regions
- **Pricing:** Prices vary by region

Console theme color is a personal preference and has no impact on application performance or compliance.

---

### Question 14: Answer - B

**my-first-bucket-2024**

**Explanation:** S3 bucket naming rules:
- 3-63 characters
- Only lowercase letters, numbers, and hyphens
- Must start with a letter or number
- Cannot be formatted as an IP address
- Must be globally unique across all AWS accounts

Option A uses underscores (invalid), Option C uses uppercase (invalid), Option D looks like an IP address (invalid).

---

### Question 15: Answer - C

**12 digits**

**Explanation:** AWS Account IDs are always 12-digit numbers (e.g., 123456789012). They uniquely identify your AWS account and are used for cross-account access, support cases, and IAM login URLs.

---

## Score Interpretation

| Score | Result |
|-------|--------|
| 15/15 | Excellent! You're ready for the next module! |
| 12-14/15 | Great job! Review the questions you missed. |
| 9-11/15 | Good effort. Consider re-reading the sections you struggled with. |
| Below 9/15 | Review the module content before moving on. |

---

## Passing Score

You need **12 out of 15 (80%)** to pass this quiz.

---

## Next Steps

If you passed:
- Congratulations! You've completed Module 01: AWS Fundamentals!
- Move on to Module 02: Identity and Access Management (IAM)

If you need more practice:
- Review the sections corresponding to questions you missed
- Redo the hands-on lab
- Try explaining concepts out loud to reinforce learning

---

## Summary of Key Concepts to Remember

| Concept | Key Points |
|---------|------------|
| **Cloud Computing** | On-demand resources, pay-as-you-go |
| **IaaS vs PaaS vs SaaS** | More control = more management responsibility |
| **Regions** | Geographic areas with 2+ AZs |
| **Availability Zones** | Isolated data centers for fault tolerance |
| **Edge Locations** | Content caching endpoints |
| **Root User** | Full access, use sparingly, enable MFA |
| **AWS CLI** | Command-line management tool |
| **Free Tier** | Always Free, 12-Month Free, Trials |

---

## Congratulations!

You've completed Module 01: AWS Fundamentals!

---

[<-- Previous: Hands-on Lab](07-hands-on-lab.md) | [Back to Module Overview](README.md)
