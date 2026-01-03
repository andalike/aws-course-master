# 04 - AWS Console Tour

## Section Overview

| Attribute | Details |
|-----------|---------|
| **Estimated Time** | 25 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | AWS account created |
| **Type** | Hands-on |

---

## Learning Objectives

After completing this section, you will be able to:

- Navigate the AWS Management Console efficiently
- Use the search function to find services quickly
- Pin frequently used services for easy access
- Change regions and understand region-specific resources
- Access AWS CloudShell for quick CLI access
- Find and use AWS documentation and support

---

## What is the AWS Management Console?

The **AWS Management Console** is a web-based interface for accessing and managing AWS services. Think of it as your command center for everything AWS.

> **Real-World Analogy**
>
> The AWS Console is like a car dashboard - it gives you visibility and control over everything happening in your AWS environment, with different displays and controls for different functions.

**Access the Console:**
```
https://console.aws.amazon.com
```

---

## Console Overview

When you first log in, you'll see the main console dashboard:

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [AWS Logo]  Services ▼  Search [____________________] 🔔  Region ▼  User ▼ │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AWS Console Home                                                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Recently visited services                                          │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │   │
│  │  │  EC2   │ │   S3   │ │  RDS   │ │ Lambda │ │  IAM   │            │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  AWS Health                                     Cost & Usage         │   │
│  │  ✓ No issues                                   $0.00 this month     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Explore AWS                                                        │   │
│  │  • Build a solution                                                  │   │
│  │  • Learn to build                                                    │   │
│  │  • Explore services                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Navigation Bar Components

The top navigation bar is your primary tool for navigating AWS:

### 1. AWS Logo (Home Button)

Click the **AWS logo** (orange arrow/smile) to return to the console home from anywhere.

### 2. Services Menu

Click **"Services"** to see all AWS services organized by category:

**Screenshot Description:**
```
┌──────────────────────────────────────────────────────────────┐
│  All services                                                │
│                                                              │
│  Recently visited          │  All services by category      │
│  ├─ EC2                    │                                │
│  ├─ S3                     │  Compute                       │
│  └─ IAM                    │  ├─ EC2                        │
│                            │  ├─ Lambda                     │
│  Favorites ☆               │  ├─ Elastic Beanstalk          │
│  [Drag services here]      │  └─ ...                        │
│                            │                                │
│                            │  Storage                       │
│                            │  ├─ S3                         │
│                            │  ├─ EBS                        │
│                            │  └─ EFS                        │
│                            │                                │
│                            │  Database                      │
│                            │  ├─ RDS                        │
│                            │  ├─ DynamoDB                   │
│                            │  └─ ElastiCache                │
│                            │                                │
└──────────────────────────────────────────────────────────────┘
```

### 3. Search Bar (The Most Important Feature!)

The search bar is your **fastest way** to find any service, feature, or documentation.

**Keyboard Shortcut:** Press `Alt + S` (Windows/Linux) or `Option + S` (Mac)

**What you can search for:**

| Search Type | Example | Result |
|-------------|---------|--------|
| Service name | "EC2" | Opens EC2 service |
| Feature | "security groups" | Goes directly to feature |
| Documentation | "S3 pricing" | Shows relevant docs |
| Actions | "create bucket" | Direct link to action |
| Blog posts | "serverless best practices" | AWS blog articles |

**Screenshot Description:**
```
┌───────────────────────────────────────────────────────────────────────┐
│  🔍 ec2                                                               │
├───────────────────────────────────────────────────────────────────────┤
│  Services                                                             │
│  ├─ EC2 - Virtual Servers in the Cloud                               │
│  └─ EC2 Image Builder                                                 │
│                                                                       │
│  Features                                                             │
│  ├─ EC2 > Instances                                                  │
│  ├─ EC2 > Security Groups                                            │
│  ├─ EC2 > Key Pairs                                                  │
│  └─ EC2 > AMIs                                                       │
│                                                                       │
│  Documentation                                                        │
│  ├─ Amazon EC2 User Guide                                            │
│  └─ EC2 API Reference                                                │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

> **Pro Tip: Search is Your Friend**
>
> Instead of clicking through menus, just type what you want in the search bar. It's faster and you'll discover features you didn't know existed!

### 4. Notifications Bell

Click the **bell icon** 🔔 to see:
- Service health notifications
- Scheduled maintenance
- Important account alerts

### 5. Region Selector

**Critical concept!** The region selector shows your current AWS region.

**Screenshot Description:**
```
┌─────────────────────────────────────┐
│  Region ▼                          │
├─────────────────────────────────────┤
│  Recently visited                   │
│  ├─ US East (N. Virginia) us-east-1│
│  └─ US West (Oregon) us-west-2     │
│                                     │
│  All regions                        │
│  ├─ US East (N. Virginia) us-east-1│
│  ├─ US East (Ohio) us-east-2       │
│  ├─ US West (N. California)us-west-1│
│  ├─ US West (Oregon) us-west-2     │
│  ├─ Asia Pacific (Mumbai) ap-south-1│
│  ├─ Asia Pacific (Tokyo) ap-north..│
│  └─ Europe (Ireland) eu-west-1     │
│                                     │
└─────────────────────────────────────┘
```

> **Warning: Region-Specific Resources**
>
> Most AWS resources exist only in the region where you create them! If you create an EC2 instance in us-east-1 and then switch to eu-west-1, you won't see that instance. Always check your region if resources seem "missing"!

**Global vs Regional Services:**

| Global Services | Regional Services |
|-----------------|-------------------|
| IAM (Users, Roles) | EC2 (Instances) |
| Route 53 (DNS) | S3 (Buckets are global, but have a region) |
| CloudFront (CDN) | RDS (Databases) |
| AWS Organizations | Lambda (Functions) |
| Billing | VPC (Networks) |

### 6. Account Menu

Click your **account name/ID** for account options:

**Screenshot Description:**
```
┌───────────────────────────────────┐
│  Account: 123456789012           │
│  user: root                       │
├───────────────────────────────────┤
│  Account                          │
│  Organization                     │
│  Service Quotas                   │
│  Billing Dashboard                │
│  Security credentials             │
│  Settings                         │
│  ─────────────────────────────── │
│  Switch role                      │
│  ─────────────────────────────── │
│  Sign out                         │
└───────────────────────────────────┘
```

---

## Pinning Favorite Services

You can pin frequently used services for quick access.

### Method 1: From the Services Menu

1. Click **"Services"** in the navigation bar
2. Hover over a service name
3. Click the **star icon** ☆ next to it
4. The service is now in your **"Favorites"** section

### Method 2: Drag and Drop

1. Click **"Services"** in the navigation bar
2. Drag any service to the **"Favorites"** section

**Screenshot Description:**
```
┌───────────────────────────────────────────────────────────────────┐
│  Services ▼                                                       │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Favorites (drag services here)                                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │
│  │ ★ EC2  │ │ ★ S3   │ │ ★ IAM  │ │★Lambda │ │ ★ RDS  │          │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘          │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Recommended Services to Pin (Beginners)

| Service | Why Pin It |
|---------|------------|
| **EC2** | Core compute service - you'll use it often |
| **S3** | Core storage service - frequently accessed |
| **IAM** | Security management - essential for access control |
| **CloudWatch** | Monitoring - check logs and metrics |
| **VPC** | Networking - understanding networks is fundamental |
| **Lambda** | Serverless - increasingly important |
| **RDS** | Databases - common in most applications |

---

## Understanding the Console Layout

Each AWS service has a similar layout pattern:

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [AWS Logo]  Services ▼  Search [____________________] 🔔  Region ▼  User ▼ │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────┬─────────────────────────────────────────────────────┐   │
│  │               │                                                     │   │
│  │  LEFT MENU    │              MAIN CONTENT AREA                      │   │
│  │               │                                                     │   │
│  │  Dashboard    │   ┌─────────────────────────────────────────────┐   │   │
│  │  Instances    │   │                                             │   │   │
│  │  Security Grp │   │   Dashboard / List of resources             │   │   │
│  │  Key Pairs    │   │                                             │   │   │
│  │  AMIs         │   │   [Create] [Actions ▼] [Refresh]            │   │   │
│  │  Volumes      │   │                                             │   │   │
│  │  Snapshots    │   │   ┌─────────────────────────────────────┐   │   │   │
│  │  ───────────  │   │   │ Resource 1     │ Status │ Type     │   │   │   │
│  │  NETWORK      │   │   │ Resource 2     │ Status │ Type     │   │   │   │
│  │  VPCs         │   │   │ Resource 3     │ Status │ Type     │   │   │   │
│  │  Subnets      │   │   └─────────────────────────────────────┘   │   │   │
│  │  ───────────  │   │                                             │   │   │
│  │  LOAD BAL.    │   └─────────────────────────────────────────────┘   │   │
│  │               │                                                     │   │
│  └───────────────┴─────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Common Console Elements

| Element | Description |
|---------|-------------|
| **Left Navigation** | Service-specific menu for features and resources |
| **Breadcrumbs** | Shows your location in the console hierarchy |
| **Action Buttons** | Create, Delete, Modify resources |
| **Resource Lists** | Tables showing your resources with status |
| **Filters** | Narrow down resource lists |
| **Info Panels** | Detailed information about selected resources |

---

## AWS CloudShell

**CloudShell** is a browser-based shell that gives you instant CLI access to AWS without installing anything!

### Accessing CloudShell

Click the **CloudShell icon** in the navigation bar (looks like a terminal prompt `>_`)

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [AWS Logo]  Services ▼  Search [____]  [>_] ← CloudShell  🔔  Region  User │
└─────────────────────────────────────────────────────────────────────────────┘
```

Or search for "CloudShell" in the search bar.

### CloudShell Features

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AWS CloudShell                                                    [X]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [user@ip-10-0-0-1 ~]$ _                                                    │
│                                                                             │
│  Welcome to AWS CloudShell                                                  │
│  - AWS CLI is pre-installed and configured                                  │
│  - 1 GB of persistent storage in $HOME                                     │
│  - Common tools: Python, Node.js, git, etc.                                │
│                                                                             │
│  [user@ip-10-0-0-1 ~]$ aws --version                                       │
│  aws-cli/2.13.0 Python/3.11.4 Linux/5.10.0-1234 exe/x86_64.amzn.2023      │
│                                                                             │
│  [user@ip-10-0-0-1 ~]$ aws s3 ls                                           │
│  2024-01-15 10:30:00 my-bucket-1                                           │
│  2024-01-16 14:22:00 my-bucket-2                                           │
│                                                                             │
│  [user@ip-10-0-0-1 ~]$ _                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Feature | Description |
|---------|-------------|
| **Pre-installed AWS CLI** | No need to install or configure |
| **Pre-authenticated** | Uses your console session credentials |
| **1 GB Storage** | Persistent home directory |
| **Common Tools** | Python, Node.js, git, make, pip, etc. |
| **File Upload/Download** | Transfer files to/from CloudShell |
| **Free** | No additional charges |

### Try These CloudShell Commands

```bash
# Check AWS CLI version
aws --version

# See your identity
aws sts get-caller-identity

# List S3 buckets (probably empty for new accounts)
aws s3 ls

# List EC2 instances (probably empty for new accounts)
aws ec2 describe-instances

# Check current region
aws configure get region
```

> **Pro Tip: CloudShell for Quick Tasks**
>
> Use CloudShell when you need to quickly run a CLI command without switching to your terminal. It's perfect for one-off commands and testing.

### CloudShell Limitations

| Limitation | Details |
|------------|---------|
| **Session timeout** | Inactive sessions close after 20 minutes |
| **Region-specific** | CloudShell runs in a specific region |
| **1 GB storage** | Files outside $HOME are not persistent |
| **No GUI** | Terminal only, no graphical applications |
| **Concurrent sessions** | Limited number of concurrent sessions |

---

## Console Settings and Preferences

### Accessing Settings

Click your **account name** → **Settings**

### Useful Settings

| Setting | Recommendation |
|---------|----------------|
| **Language** | Set your preferred language |
| **Default region** | Set your most-used region |
| **Visual mode** | Choose between light and dark themes |
| **New Console** | Opt-in to new console experiences |

### Dark Mode

AWS Console supports dark mode:

1. Click the **gear icon** ⚙️ in the bottom left of the console
2. Select **"Dark"** under Visual mode

---

## Finding Help and Documentation

### In-Console Help

Most services have a **"Learn more"** or **"Info"** link:

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  EC2 > Instances                                      [?] Help  │
│                                                                 │
│  ℹ️ Need help? Check out:                                       │
│  • Getting started guide                                        │
│  • EC2 documentation                                            │
│  • AWS re:Post community                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Documentation Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| **AWS Docs** | docs.aws.amazon.com | Official documentation |
| **AWS Blog** | aws.amazon.com/blogs | News and tutorials |
| **re:Post** | repost.aws | Community Q&A |
| **Workshops** | workshops.aws | Hands-on tutorials |
| **Skill Builder** | skillbuilder.aws | Free training courses |

---

## Resource Groups and Tag Editor

### What are Resource Groups?

Resource Groups help you organize and manage AWS resources based on tags or CloudFormation stacks.

### Accessing Resource Groups

1. Search for **"Resource Groups"** in the search bar
2. Or click **"Services"** → **"Management & Governance"** → **"Resource Groups & Tag Editor"**

### Use Cases

| Use Case | Example |
|----------|---------|
| **By Environment** | Group all "Production" tagged resources |
| **By Project** | Group all resources for "Project X" |
| **By Cost Center** | Group resources by department |
| **By Application** | Group all components of an application |

---

## Billing and Cost Management

### Accessing Billing Dashboard

1. Click your **account name** → **"Billing Dashboard"**
2. Or search for **"Billing"** in the search bar

### Key Billing Pages

| Page | What It Shows |
|------|---------------|
| **Dashboard** | Overview of current month costs |
| **Bills** | Detailed bills by service |
| **Cost Explorer** | Analyze costs over time |
| **Budgets** | Create and track budgets |
| **Free Tier** | Track Free Tier usage |

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Billing and Cost Management Dashboard                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Month-to-date costs                    Forecasted month-end costs          │
│  ┌──────────────────────┐              ┌──────────────────────┐            │
│  │                      │              │                      │            │
│  │       $0.00          │              │       $0.00          │            │
│  │                      │              │                      │            │
│  └──────────────────────┘              └──────────────────────┘            │
│                                                                             │
│  Top services by cost                                                       │
│  ───────────────────────────────────────────────────────────────           │
│  No charges this month!                                                     │
│                                                                             │
│  Free Tier usage                                                            │
│  ───────────────────────────────────────────────────────────────           │
│  [View Free Tier usage details]                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **Pro Tip: Check Billing Weekly**
>
> Make it a habit to check your billing dashboard at least weekly. This helps you catch any unexpected charges early before they grow.

---

## Console Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt + S` (Win/Linux) / `Option + S` (Mac) | Focus search bar |
| `Esc` | Close dialog/modal |
| `Enter` | Confirm action in dialogs |
| `Tab` | Navigate between elements |

---

## Hands-On Exercise: Console Exploration

Spend 10-15 minutes exploring the console:

### Task 1: Pin Services
1. Open the Services menu
2. Pin these services to favorites: EC2, S3, IAM, CloudWatch, Lambda

### Task 2: Change Regions
1. Note your current region
2. Switch to a different region (e.g., eu-west-1)
3. Switch back to your original region

### Task 3: Open CloudShell
1. Click the CloudShell icon
2. Wait for it to initialize
3. Run: `aws sts get-caller-identity`
4. Run: `aws s3 ls`

### Task 4: Explore Services
1. Go to EC2 Dashboard (even though you have no instances)
2. Go to S3 Console
3. Go to IAM Console
4. Go to CloudWatch Console

### Task 5: Check Billing
1. Go to Billing Dashboard
2. Check your Free Tier usage
3. Verify your billing alerts are configured

---

## Key Takeaways

| Concept | Remember This |
|---------|---------------|
| **Search Bar** | Fastest way to find anything - use it! |
| **Region** | Always verify your region - resources are region-specific |
| **Favorites** | Pin frequently used services for quick access |
| **CloudShell** | Instant CLI access, no setup required |
| **Billing Dashboard** | Check regularly to avoid surprises |

---

## Common Mistakes to Avoid

> **Warning: Region Mistakes**
>
> The #1 beginner mistake is creating resources in the wrong region or not finding resources because you're in the wrong region. ALWAYS check the region selector!

> **Warning: Not Using Search**
>
> Clicking through menus is slow. The search bar can take you directly to features, documentation, and even specific actions. Learn to use it!

> **Warning: Ignoring Billing**
>
> Even with Free Tier, you can accidentally incur charges. Check your billing dashboard regularly!

---

## What's Next?

Now that you're comfortable navigating the console, let's set up the AWS CLI on your local machine in **[05 - AWS CLI Setup](05-aws-cli-setup.md)**.

---

[<-- Previous: Creating Your AWS Account](03-creating-aws-account.md) | [Next: AWS CLI Setup -->](05-aws-cli-setup.md)
