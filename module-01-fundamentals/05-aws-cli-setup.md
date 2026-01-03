# 05 - AWS CLI Setup

## Section Overview

| Attribute | Details |
|-----------|---------|
| **Estimated Time** | 30 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | AWS account created, basic terminal/command prompt knowledge |
| **Type** | Hands-on |

---

## Learning Objectives

After completing this section, you will be able to:

- Install AWS CLI version 2 on Windows, macOS, or Linux
- Configure AWS CLI with access credentials
- Run basic AWS CLI commands
- Understand AWS CLI profiles for multiple accounts
- Troubleshoot common CLI issues

---

## What is the AWS CLI?

The **AWS Command Line Interface (CLI)** is a unified tool to manage your AWS services from the command line. With just one tool, you can control multiple AWS services and automate them through scripts.

> **Real-World Analogy**
>
> If the AWS Console is like driving a car with a dashboard and steering wheel, the AWS CLI is like being a race car mechanic who can tune every part of the engine directly. It's more powerful but requires more knowledge.

### Console vs CLI Comparison

| Aspect | AWS Console | AWS CLI |
|--------|-------------|---------|
| **Interface** | Graphical (web browser) | Text (terminal) |
| **Learning Curve** | Lower | Higher |
| **Speed** | Slower (clicking) | Faster (typing) |
| **Automation** | Limited | Excellent |
| **Scripting** | Not possible | Fully scriptable |
| **Bulk Operations** | Tedious | Easy |
| **Documentation** | Visual hints | Must know commands |

---

## AWS CLI Version 2 Features

We'll be installing **AWS CLI version 2**, which includes:

- Improved installers
- AWS SSO support
- Interactive features
- Auto-completion
- Wizards for complex commands
- Better pagination handling

---

## Installation by Operating System

Choose your operating system below:

---

## Windows Installation

### Method 1: MSI Installer (Recommended)

**Step 1: Download the installer**

```
https://awscli.amazonaws.com/AWSCLIV2.msi
```

**Step 2: Run the installer**

1. Locate the downloaded `AWSCLIV2.msi` file
2. Double-click to run the installer
3. Follow the installation wizard:

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  AWS Command Line Interface v2 Setup                            │
│                                                                 │
│  Welcome to the AWS CLI version 2 Setup Wizard                 │
│                                                                 │
│  This will install AWS CLI version 2 on your computer.         │
│                                                                 │
│  Click Next to continue, or Cancel to exit Setup.              │
│                                                                 │
│                                          [Next >]  [Cancel]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

4. Accept the license agreement
5. Choose installation location (default is fine)
6. Click **Install**
7. Click **Finish** when complete

**Step 3: Verify installation**

Open a **new** Command Prompt or PowerShell window and run:

```cmd
aws --version
```

**Expected output:**
```
aws-cli/2.15.0 Python/3.11.6 Windows/10 exe/AMD64 prompt/off
```

> **Warning: Restart Terminal**
>
> If `aws --version` doesn't work, close your terminal completely and open a new one. The PATH environment variable updates require a new terminal session.

### Method 2: Using Chocolatey

If you have Chocolatey package manager installed:

```powershell
choco install awscli
```

### Method 3: Using winget

If you have Windows Package Manager (winget):

```powershell
winget install Amazon.AWSCLI
```

---

## macOS Installation

### Method 1: PKG Installer (Recommended)

**Step 1: Download the installer**

For all Macs (Intel and Apple Silicon):

```bash
# Download the PKG file
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
```

**Step 2: Run the installer**

```bash
# Run the installer
sudo installer -pkg AWSCLIV2.pkg -target /
```

Or double-click the downloaded `.pkg` file and follow the wizard.

**Step 3: Verify installation**

```bash
aws --version
```

**Expected output:**
```
aws-cli/2.15.0 Python/3.11.6 Darwin/23.0.0 exe/x86_64 prompt/off
```

### Method 2: Using Homebrew (Popular Alternative)

If you have Homebrew installed:

```bash
# Install AWS CLI
brew install awscli

# Verify installation
aws --version
```

> **Pro Tip: Homebrew Updates**
>
> With Homebrew, you can easily update AWS CLI later:
> ```bash
> brew upgrade awscli
> ```

---

## Linux Installation

### For x86 (64-bit) Systems

**Step 1: Download and unzip the installer**

```bash
# Download the installer
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip
unzip awscliv2.zip
```

**Step 2: Run the installer**

```bash
# Install (requires sudo)
sudo ./aws/install
```

**Step 3: Verify installation**

```bash
aws --version
```

**Expected output:**
```
aws-cli/2.15.0 Python/3.11.6 Linux/5.15.0-1051-aws exe/x86_64.ubuntu.22 prompt/off
```

### For ARM (64-bit) Systems

```bash
# Download ARM version
curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"

# Unzip and install
unzip awscliv2.zip
sudo ./aws/install
```

### Clean Up Installation Files

```bash
rm -rf aws awscliv2.zip
```

---

## Installation Verification Checklist

Run these commands to verify your installation:

```bash
# Check AWS CLI version
aws --version

# Check where AWS CLI is installed
which aws

# Check all installed components
aws --version --debug 2>&1 | head -20
```

---

## Configuring AWS CLI Credentials

Now that AWS CLI is installed, you need to configure it with credentials to access your AWS account.

### Step 1: Create Access Keys

> **Warning: Root User Access Keys**
>
> You should NEVER create access keys for the root user. Instead, create an IAM user with appropriate permissions. For now, we'll show the process, but you should use IAM users in practice.

**For learning purposes (create IAM user later for production):**

1. Go to AWS Console → Search for **"IAM"**
2. Click **"Users"** in the left menu
3. Click **"Create user"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Create user                                                    │
│                                                                 │
│  Step 1: Specify user details                                   │
│                                                                 │
│  User name                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ cli-admin                                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ☑ Provide user access to the AWS Management Console           │
│                                                                 │
│  [Next]                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

4. Enter a user name (e.g., `cli-admin`)
5. Click **"Next"**
6. Select **"Attach policies directly"**
7. Search for and select **"AdministratorAccess"** (for learning only!)
8. Click **"Next"** and then **"Create user"**

**Now create access keys:**

1. Click on the user you just created
2. Click the **"Security credentials"** tab
3. Scroll to **"Access keys"**
4. Click **"Create access key"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Create access key                                              │
│                                                                 │
│  Access key best practices & alternatives                       │
│                                                                 │
│  Use case                                                       │
│  ● Command Line Interface (CLI)                                │
│  ○ Local code                                                   │
│  ○ Application running on AWS compute service                   │
│  ○ Third-party service                                          │
│  ○ Application running outside AWS                              │
│                                                                 │
│  ☑ I understand the above recommendation...                    │
│                                                                 │
│  [Next]                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

5. Select **"Command Line Interface (CLI)"**
6. Check the confirmation box
7. Click **"Next"**
8. (Optional) Add a description tag
9. Click **"Create access key"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Retrieve access keys                                           │
│                                                                 │
│  Access key                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ AKIAIOSFODNN7EXAMPLE                              [Copy] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Secret access key                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY         [Show] │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ⚠️ This is the only time you can view the secret access key   │
│                                                                 │
│  [Download .csv file]                                           │
│                                                                 │
│  [Done]                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **Warning: Save Your Secret Access Key NOW**
>
> The **Secret Access Key** is only shown ONCE! If you lose it, you'll need to create new access keys. Download the CSV or copy both keys to a secure location.

### Step 2: Configure AWS CLI

Open your terminal and run:

```bash
aws configure
```

You'll be prompted for four pieces of information:

```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

| Prompt | What to Enter |
|--------|---------------|
| **Access Key ID** | Your access key ID (starts with AKIA) |
| **Secret Access Key** | Your secret access key |
| **Default region** | Your preferred region (e.g., `us-east-1`) |
| **Output format** | `json` (recommended), `text`, or `table` |

### Where Are Credentials Stored?

AWS CLI stores credentials in these files:

**Windows:**
```
C:\Users\USERNAME\.aws\credentials
C:\Users\USERNAME\.aws\config
```

**macOS/Linux:**
```
~/.aws/credentials
~/.aws/config
```

**credentials file content:**
```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**config file content:**
```ini
[default]
region = us-east-1
output = json
```

> **Warning: Protect Your Credentials**
>
> Never share your credentials files. Never commit them to git. Never paste them in public forums. If exposed, immediately delete the access keys from IAM and create new ones.

---

## Basic AWS CLI Commands

Let's test your configuration with some basic commands:

### 1. Verify Your Identity

```bash
aws sts get-caller-identity
```

**Expected output:**
```json
{
    "UserId": "AIDAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/cli-admin"
}
```

### 2. List S3 Buckets

```bash
aws s3 ls
```

**Expected output (empty for new accounts):**
```
(no output if you have no buckets)
```

### 3. List EC2 Instances

```bash
aws ec2 describe-instances
```

**Expected output (empty for new accounts):**
```json
{
    "Reservations": []
}
```

### 4. List IAM Users

```bash
aws iam list-users
```

**Expected output:**
```json
{
    "Users": [
        {
            "UserName": "cli-admin",
            "UserId": "AIDAIOSFODNN7EXAMPLE",
            "Arn": "arn:aws:iam::123456789012:user/cli-admin",
            "CreateDate": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 5. Get AWS Account ID

```bash
aws sts get-caller-identity --query Account --output text
```

**Expected output:**
```
123456789012
```

---

## Understanding CLI Output Formats

AWS CLI supports multiple output formats:

### JSON (Default)

```bash
aws iam list-users --output json
```

```json
{
    "Users": [
        {
            "UserName": "cli-admin",
            "UserId": "AIDAIOSFODNN7EXAMPLE"
        }
    ]
}
```

### Table

```bash
aws iam list-users --output table
```

```
---------------------------------------------
|               ListUsers                   |
+-------------------------------------------+
||                Users                    ||
|+--------------+--------------------------+|
||   UserName   |         UserId           ||
|+--------------+--------------------------+|
||  cli-admin   |  AIDAIOSFODNN7EXAMPLE    ||
|+--------------+--------------------------+|
```

### Text

```bash
aws iam list-users --output text
```

```
USERS   cli-admin   AIDAIOSFODNN7EXAMPLE
```

---

## AWS CLI Profiles

Profiles allow you to manage multiple AWS accounts or roles.

### Creating Additional Profiles

```bash
# Create a profile named "development"
aws configure --profile development
```

Enter credentials for the development account when prompted.

### Using Profiles

```bash
# Use a specific profile
aws s3 ls --profile development

# Set default profile for session
export AWS_PROFILE=development  # Linux/macOS
set AWS_PROFILE=development     # Windows CMD
$env:AWS_PROFILE="development"  # Windows PowerShell
```

### Viewing Your Profiles

```bash
# List all profiles
aws configure list-profiles

# View current profile configuration
aws configure list
```

**profiles in credentials file:**
```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[development]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

---

## CLI Query and Filtering

The `--query` parameter lets you filter JSON output using JMESPath syntax.

### Examples

```bash
# Get just the user names
aws iam list-users --query 'Users[*].UserName'

# Get specific fields
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'

# Filter by condition
aws ec2 describe-instances --query 'Reservations[*].Instances[?State.Name==`running`]'
```

---

## AWS CLI Auto-Completion

Enable auto-completion for faster command entry.

### macOS/Linux (Bash)

Add to your `~/.bashrc` or `~/.bash_profile`:

```bash
complete -C '/usr/local/bin/aws_completer' aws
```

Then reload:

```bash
source ~/.bashrc
```

### macOS/Linux (Zsh)

Add to your `~/.zshrc`:

```bash
autoload bashcompinit && bashcompinit
autoload -Uz compinit && compinit
complete -C '/usr/local/bin/aws_completer' aws
```

### Usage

Type `aws` followed by a space, then press `Tab` to see available options:

```bash
aws ec2 <Tab>
# Shows: describe-instances, run-instances, terminate-instances, etc.
```

---

## Common AWS CLI Commands Reference

### S3 Commands

| Command | Description |
|---------|-------------|
| `aws s3 ls` | List buckets |
| `aws s3 mb s3://bucket-name` | Create bucket |
| `aws s3 rb s3://bucket-name` | Remove bucket |
| `aws s3 cp file.txt s3://bucket-name/` | Upload file |
| `aws s3 sync ./local-dir s3://bucket-name/` | Sync directory |

### EC2 Commands

| Command | Description |
|---------|-------------|
| `aws ec2 describe-instances` | List instances |
| `aws ec2 start-instances --instance-ids i-xxx` | Start instance |
| `aws ec2 stop-instances --instance-ids i-xxx` | Stop instance |
| `aws ec2 describe-security-groups` | List security groups |

### IAM Commands

| Command | Description |
|---------|-------------|
| `aws iam list-users` | List users |
| `aws iam list-roles` | List roles |
| `aws iam get-user` | Get current user info |
| `aws iam list-policies` | List policies |

---

## Troubleshooting Common Issues

### Issue: "aws: command not found"

**Cause:** AWS CLI not in PATH

**Solution:**

```bash
# Find where AWS CLI is installed
which aws  # macOS/Linux
where aws  # Windows

# Add to PATH if needed
export PATH=$PATH:/usr/local/bin  # macOS/Linux
```

### Issue: "Unable to locate credentials"

**Cause:** Credentials not configured

**Solution:**

```bash
# Configure credentials
aws configure

# Or check if credentials file exists
cat ~/.aws/credentials  # macOS/Linux
type %USERPROFILE%\.aws\credentials  # Windows
```

### Issue: "Access Denied"

**Cause:** Insufficient permissions

**Solution:**
- Check IAM user/role permissions
- Verify correct profile is being used
- Ensure access keys are active

### Issue: "Region not specified"

**Cause:** No default region configured

**Solution:**

```bash
# Set default region
aws configure set region us-east-1

# Or specify region per command
aws ec2 describe-instances --region us-east-1
```

---

## Security Best Practices

| Practice | Description |
|----------|-------------|
| **Use IAM users** | Never use root account credentials |
| **Least privilege** | Grant minimum necessary permissions |
| **Rotate keys** | Regularly rotate access keys |
| **Use roles** | Prefer IAM roles over access keys |
| **Never commit** | Never commit credentials to git |
| **Environment variables** | Consider using env vars for temporary credentials |

---

## Key Takeaways

| Concept | Remember This |
|---------|---------------|
| **AWS CLI v2** | Latest version with improved features |
| **aws configure** | Command to set up credentials |
| **Profiles** | Manage multiple accounts with named profiles |
| **--query** | Filter output with JMESPath |
| **Credentials file** | `~/.aws/credentials` (protect this!) |

---

## Hands-On Practice

Try these commands on your own:

```bash
# 1. Check your identity
aws sts get-caller-identity

# 2. List available regions
aws ec2 describe-regions --output table

# 3. Get your account ID
aws sts get-caller-identity --query Account --output text

# 4. List availability zones in your region
aws ec2 describe-availability-zones --output table

# 5. Get help on any command
aws ec2 help
aws s3 help
```

---

## What's Next?

Now that you have AWS CLI set up, let's learn about the AWS Free Tier to avoid unexpected charges in **[06 - AWS Free Tier Guide](06-aws-free-tier.md)**.

---

[<-- Previous: AWS Console Tour](04-aws-console-tour.md) | [Next: AWS Free Tier Guide -->](06-aws-free-tier.md)
