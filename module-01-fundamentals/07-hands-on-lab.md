# 07 - Hands-on Lab: Your First AWS Experience

## Lab Overview

| Attribute | Details |
|-----------|---------|
| **Estimated Time** | 45 minutes |
| **Difficulty** | Beginner |
| **Cost** | Free (within Free Tier) |
| **Prerequisites** | AWS account, AWS CLI installed and configured |
| **Type** | Hands-on Lab |

---

## Lab Objectives

In this lab, you will:

1. Create AWS Budgets to monitor spending
2. Explore the AWS Console and find key information
3. Create your first S3 bucket using the Console
4. Perform operations using AWS CLI
5. Clean up resources

---

## What You'll Learn

By completing this lab, you will gain practical experience with:

- Setting up cost controls from day one
- Navigating the AWS Console efficiently
- Understanding AWS resource naming
- Basic S3 operations (Console and CLI)
- AWS CLI fundamentals
- Resource cleanup best practices

---

## Lab Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            YOUR AWS ACCOUNT                                  │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │                 │  │                 │  │                             │ │
│  │  AWS Budgets    │  │   S3 Bucket     │  │     CloudShell / CLI        │ │
│  │                 │  │                 │  │                             │ │
│  │  - Zero Budget  │  │  - my-first-    │  │  - List resources           │ │
│  │  - $5 Budget    │  │    bucket-xxx   │  │  - Upload file              │ │
│  │  - Alerts       │  │                 │  │  - Explore commands         │ │
│  │                 │  │                 │  │                             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Setting Up Budget Alerts

**Time: 15 minutes**

Setting up budgets is the FIRST thing you should do with any new AWS account. Let's create multiple budgets for peace of mind.

### Step 1.1: Access AWS Budgets

1. Sign in to the AWS Console
2. Search for **"Budgets"** in the search bar
3. Click on **"AWS Budgets"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AWS Budgets                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Overview                                                                   │
│                                                                             │
│  You haven't created any budgets yet.                                       │
│                                                                             │
│  [Create budget]                                                            │
│                                                                             │
│  What is AWS Budgets?                                                       │
│  AWS Budgets gives you the ability to set custom budgets that alert         │
│  you when your costs or usage exceed your budgeted amount.                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 1.2: Create a Zero Spend Budget

This budget alerts you the moment you incur ANY charge.

1. Click **"Create budget"**
2. Select **"Use a template (simplified)"**
3. Select **"Zero spend budget"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Create budget                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Choose budget type                                                         │
│  ● Use a template (simplified)                                             │
│  ○ Customize (advanced)                                                    │
│                                                                             │
│  Templates                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ● Zero spend budget                                                 │   │
│  │   Alerts when your spending exceeds $0.01 (after Free Tier)        │   │
│  │                                                                     │   │
│  │ ○ Monthly cost budget                                              │   │
│  │   Alerts at customizable threshold                                 │   │
│  │                                                                     │   │
│  │ ○ Daily savings plans coverage budget                              │   │
│  │ ○ Daily reservation utilization budget                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Budget name: My Zero-Spend Budget                                          │
│  Email recipients: your.email@example.com                                   │
│                                                                             │
│  [Create budget]                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

4. Enter a budget name: **"My Zero-Spend Budget"**
5. Enter your email address for notifications
6. Click **"Create budget"**

> **Checkpoint 1**
>
> You should now see your Zero Spend Budget in the list!

### Step 1.3: Create a Monthly Cost Budget

Let's create another budget with a specific dollar threshold.

1. Click **"Create budget"** again
2. Select **"Use a template (simplified)"**
3. Select **"Monthly cost budget"**
4. Enter budget name: **"Monthly $5 Budget"**
5. Enter budgeted amount: **5.00**
6. Enter your email for notifications
7. Click **"Create budget"**

### Step 1.4: Verify Your Budgets

You should now have two budgets:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AWS Budgets                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Budget name            │ Budget type    │ Budget amount │ Current spend   │
│  ───────────────────────┼────────────────┼───────────────┼─────────────────│
│  My Zero-Spend Budget   │ Cost budget    │ $0.01         │ $0.00           │
│  Monthly $5 Budget      │ Cost budget    │ $5.00         │ $0.00           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **Checkpoint 2**
>
> You now have protection against unexpected charges!

---

## Part 2: Console Exploration Challenge

**Time: 10 minutes**

Let's explore the console and find some key information about your account.

### Challenge 1: Find Your Account ID

**Task:** Find your 12-digit AWS Account ID

**Steps:**
1. Click on your account name in the top-right corner
2. Your Account ID is displayed in the dropdown

**Record your answer:**
```
My AWS Account ID: _________________________
```

### Challenge 2: Find the Current Region

**Task:** Identify your current region

**Steps:**
1. Look at the region selector in the top-right
2. Note both the region name AND region code

**Record your answer:**
```
Region Name: _________________________
Region Code: _________________________
```

### Challenge 3: Find IAM Dashboard

**Task:** Navigate to IAM and find how many users exist

**Steps:**
1. Search for "IAM" in the search bar
2. Go to IAM Dashboard
3. Look at the "IAM Resources" section

**Record your answer:**
```
Number of Users: _________________________
Number of Groups: _________________________
Number of Policies: _________________________
```

### Challenge 4: Find Your Free Tier Usage

**Task:** Check your Free Tier usage status

**Steps:**
1. Go to Billing Dashboard
2. Click "Free Tier" in the left menu
3. Note any services you're using

**Record your answer:**
```
Services with usage: _________________________
```

---

## Part 3: Create Your First S3 Bucket

**Time: 10 minutes**

S3 (Simple Storage Service) is one of AWS's most fundamental services. Let's create your first bucket!

### Step 3.1: Navigate to S3

1. Search for **"S3"** in the search bar
2. Click on **"S3"**

### Step 3.2: Create a Bucket

1. Click **"Create bucket"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Create bucket                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  General configuration                                                      │
│                                                                             │
│  Bucket name                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ my-first-bucket-12345-uniqueid                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ⚠️ Bucket names must be globally unique across all AWS accounts           │
│                                                                             │
│  AWS Region                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ US East (N. Virginia) us-east-1                                 ▼   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

2. Enter a bucket name:
   - Must be globally unique (across ALL AWS accounts)
   - Use lowercase letters, numbers, and hyphens only
   - Example: `my-first-bucket-[your-name]-[random-numbers]`
   - Like: `my-first-bucket-john-2024-01-15`

3. Select your region (keep default or choose closest to you)

4. Leave all other settings as default for now:
   - Block all public access: **Enabled** (default)
   - Bucket versioning: **Disabled** (default)
   - Encryption: **SSE-S3** (default)

5. Scroll down and click **"Create bucket"**

> **Warning: Bucket Name Rules**
>
> - 3-63 characters long
> - Only lowercase letters, numbers, and hyphens
> - Must start with letter or number
> - Cannot look like an IP address (192.168.1.1)
> - Must be GLOBALLY unique (no one else can have the same name)

### Step 3.3: Upload a File

1. Click on your bucket name to open it
2. Click **"Upload"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Upload                                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │              Drag and drop files and folders here                  │   │
│  │                                                                     │   │
│  │                    or click [Add files]                            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [Add files]  [Add folder]                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

3. Create a simple text file on your computer:
   - Create a file named `hello.txt`
   - Content: `Hello, AWS! This is my first file in S3.`

4. Click **"Add files"** and select your `hello.txt`
5. Click **"Upload"**
6. Click **"Close"** when upload is complete

> **Checkpoint 3**
>
> You've successfully created an S3 bucket and uploaded a file!

### Step 3.4: View Your File

1. Click on `hello.txt` in your bucket
2. Click **"Open"** to view the file (opens in new tab)

**Note:** This works because you're the bucket owner. The file is not publicly accessible.

---

## Part 4: AWS CLI Exploration

**Time: 15 minutes**

Now let's accomplish similar tasks using the command line.

### Step 4.1: Open Your Terminal

Open your terminal (macOS/Linux) or Command Prompt/PowerShell (Windows).

**Alternative:** Use CloudShell in the AWS Console (click the `>_` icon in the navigation bar).

### Step 4.2: Verify Your Identity

```bash
aws sts get-caller-identity
```

**Expected output:**
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/cli-admin"
}
```

**Record your output:**
```
Account ID: _________________________
User ARN: _________________________
```

### Step 4.3: List Your S3 Buckets

```bash
aws s3 ls
```

**Expected output:**
```
2024-01-15 10:30:00 my-first-bucket-john-2024-01-15
```

### Step 4.4: List Objects in Your Bucket

Replace `your-bucket-name` with your actual bucket name:

```bash
aws s3 ls s3://your-bucket-name/
```

**Expected output:**
```
2024-01-15 10:35:00         42 hello.txt
```

### Step 4.5: Create Another File and Upload via CLI

Create a new file locally:

**macOS/Linux:**
```bash
echo "This file was uploaded via AWS CLI!" > cli-test.txt
```

**Windows (PowerShell):**
```powershell
"This file was uploaded via AWS CLI!" | Out-File cli-test.txt -Encoding ASCII
```

**Windows (CMD):**
```cmd
echo This file was uploaded via AWS CLI! > cli-test.txt
```

Upload to S3:

```bash
aws s3 cp cli-test.txt s3://your-bucket-name/cli-test.txt
```

**Expected output:**
```
upload: ./cli-test.txt to s3://your-bucket-name/cli-test.txt
```

### Step 4.6: List Objects Again

```bash
aws s3 ls s3://your-bucket-name/
```

**Expected output:**
```
2024-01-15 10:35:00         42 hello.txt
2024-01-15 10:40:00         38 cli-test.txt
```

> **Checkpoint 4**
>
> You've successfully used AWS CLI to interact with S3!

### Step 4.7: Download a File via CLI

```bash
aws s3 cp s3://your-bucket-name/hello.txt ./downloaded-hello.txt
```

**Expected output:**
```
download: s3://your-bucket-name/hello.txt to ./downloaded-hello.txt
```

### Step 4.8: Explore More CLI Commands

Try these additional commands:

```bash
# Get information about your S3 bucket
aws s3api get-bucket-location --bucket your-bucket-name

# List all EC2 instances (probably empty)
aws ec2 describe-instances --output table

# List available AWS regions
aws ec2 describe-regions --output table

# Check how many availability zones in your region
aws ec2 describe-availability-zones --output table

# Get your default VPC information
aws ec2 describe-vpcs --output table
```

---

## Part 5: Cleanup

**Time: 5 minutes**

It's essential to clean up resources after learning exercises. Let's delete the S3 bucket.

### Step 5.1: Delete Files from Bucket (CLI Method)

You cannot delete a bucket with objects in it. First, empty the bucket:

```bash
# Delete all objects in the bucket
aws s3 rm s3://your-bucket-name --recursive
```

**Expected output:**
```
delete: s3://your-bucket-name/hello.txt
delete: s3://your-bucket-name/cli-test.txt
```

### Step 5.2: Delete the Bucket (CLI Method)

```bash
aws s3 rb s3://your-bucket-name
```

**Expected output:**
```
remove_bucket: your-bucket-name
```

### Step 5.3: Verify Deletion

```bash
aws s3 ls
```

Your bucket should no longer appear in the list.

### Alternative: Console Cleanup Method

If you prefer to use the console:

1. Go to S3 in the console
2. Select your bucket (checkbox)
3. Click **"Empty"** first (required before deletion)
4. Type "permanently delete" to confirm
5. Select your bucket again
6. Click **"Delete"**
7. Type the bucket name to confirm

### Step 5.4: Clean Up Local Files

```bash
# Remove local test files
rm cli-test.txt downloaded-hello.txt hello.txt
```

> **Checkpoint 5**
>
> All resources cleaned up!

---

## Lab Summary

### What You Accomplished

| Task | Status |
|------|--------|
| Created Zero Spend Budget | Completed |
| Created Monthly $5 Budget | Completed |
| Found Account ID | Completed |
| Explored IAM Dashboard | Completed |
| Created S3 Bucket | Completed |
| Uploaded File via Console | Completed |
| Uploaded File via CLI | Completed |
| Downloaded File via CLI | Completed |
| Cleaned Up Resources | Completed |

### Commands You Learned

| Command | Purpose |
|---------|---------|
| `aws sts get-caller-identity` | Verify your identity |
| `aws s3 ls` | List S3 buckets |
| `aws s3 ls s3://bucket-name/` | List objects in bucket |
| `aws s3 cp file s3://bucket-name/` | Upload file to S3 |
| `aws s3 cp s3://bucket-name/file ./` | Download file from S3 |
| `aws s3 rm s3://bucket-name --recursive` | Delete all objects |
| `aws s3 rb s3://bucket-name` | Delete bucket |
| `aws ec2 describe-regions` | List AWS regions |
| `aws ec2 describe-availability-zones` | List AZs |

---

## Bonus Challenges

If you have extra time, try these:

### Challenge 1: Create a Bucket with Versioning

```bash
# Create bucket
aws s3api create-bucket --bucket my-versioned-bucket-yourname --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning --bucket my-versioned-bucket-yourname \
    --versioning-configuration Status=Enabled
```

### Challenge 2: Set Up a Lifecycle Rule

Research and try:
```bash
aws s3api put-bucket-lifecycle-configuration --bucket your-bucket-name \
    --lifecycle-configuration file://lifecycle.json
```

### Challenge 3: Explore CloudWatch

```bash
# List any CloudWatch alarms
aws cloudwatch describe-alarms

# Get metrics available
aws cloudwatch list-metrics --namespace "AWS/S3" --output table
```

---

## Troubleshooting

### Issue: "An error occurred (BucketAlreadyExists)"

**Cause:** Bucket name is already taken globally

**Solution:** Choose a more unique name with random numbers

### Issue: "The bucket you tried to delete is not empty"

**Cause:** Bucket has objects

**Solution:** Run `aws s3 rm s3://bucket --recursive` first

### Issue: "Access Denied"

**Cause:** Insufficient permissions

**Solution:**
1. Verify you're using the correct profile
2. Check IAM permissions
3. Run `aws sts get-caller-identity` to verify identity

---

## Key Takeaways

| Lesson | Application |
|--------|-------------|
| **Budget First** | Always set up budgets before using AWS |
| **CLI is Powerful** | Same actions, different interface |
| **Unique Naming** | S3 bucket names are globally unique |
| **Always Clean Up** | Delete resources when done learning |
| **Verify Identity** | Use `get-caller-identity` when debugging |

---

## What's Next?

Congratulations on completing your first hands-on lab! Now test your knowledge with the **[Module Quiz](quiz.md)**.

---

[<-- Previous: AWS Free Tier Guide](06-aws-free-tier.md) | [Next: Module Quiz -->](quiz.md)
