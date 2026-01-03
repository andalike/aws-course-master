# 03 - Creating Your AWS Account

## Section Overview

| Attribute | Details |
|-----------|---------|
| **Estimated Time** | 20 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | Email address, phone number, credit/debit card |
| **Type** | Hands-on |

---

## Learning Objectives

After completing this section, you will be able to:

- Create a new AWS account from scratch
- Set up Multi-Factor Authentication (MFA) for security
- Configure billing alerts to avoid surprise charges
- Understand AWS account structure and root user concepts

---

## What You'll Need

Before starting, ensure you have:

| Requirement | Purpose |
|-------------|---------|
| **Valid email address** | Account login and notifications |
| **Phone number** | Identity verification |
| **Credit/debit card** | Account verification (minimal/no charge) |
| **Personal/business name** | Account registration |

> **Warning: Credit Card Requirement**
>
> AWS requires a credit/debit card for verification. You will see a temporary $1 authorization charge that is immediately reversed. If you stay within Free Tier limits, you will NOT be charged.

---

## Step 1: Navigate to AWS Signup Page

**Action:** Open your web browser and go to:

```
https://aws.amazon.com/free
```

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  AWS Free Tier Landing Page                                     │
│                                                                 │
│  [AWS Logo]                              [Sign In] [Create...] │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   Build on AWS with Free Tier                          │   │
│  │                                                         │   │
│  │   Gain free, hands-on experience with                  │   │
│  │   AWS platform, products, and services                 │   │
│  │                                                         │   │
│  │   [Create a Free Account]  ← CLICK THIS                │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Click the **"Create a Free Account"** button.

---

## Step 2: Enter Email and Account Name

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Sign up for AWS                                                │
│                                                                 │
│  Root user email address                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ your.email@example.com                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  AWS account name                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ My Learning Account                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Verify email address]                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Fill in the fields:**

| Field | What to Enter |
|-------|---------------|
| **Root user email address** | Your personal or work email |
| **AWS account name** | A descriptive name (e.g., "MyLearning", "DevAccount") |

> **Pro Tip: Email Best Practices**
>
> - Use an email you check regularly (you'll receive important notifications)
> - For organizations, consider using a distribution list or shared email
> - Avoid using temporary email services

Click **"Verify email address"** to continue.

---

## Step 3: Verify Your Email

AWS will send a verification code to your email.

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Verify your email address                                      │
│                                                                 │
│  We sent a verification code to your.email@example.com          │
│                                                                 │
│  Verification code                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 123456                                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Verify]                                                       │
│                                                                 │
│  Didn't receive the code? [Resend code]                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

1. Check your email inbox (and spam folder if needed)
2. Find the email from AWS
3. Copy the 6-digit verification code
4. Enter it in the field
5. Click **"Verify"**

---

## Step 4: Create Root User Password

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Create your password                                           │
│                                                                 │
│  Root user password                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ••••••••••••••••                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Confirm root user password                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ••••••••••••••••                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Password requirements:                                         │
│  ✓ Minimum 8 characters                                        │
│  ✓ Include uppercase letters                                   │
│  ✓ Include lowercase letters                                   │
│  ✓ Include numbers                                             │
│  ✓ Include non-alphanumeric characters                         │
│                                                                 │
│  [Continue]                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **Warning: Root User Security is CRITICAL**
>
> The root user has **UNLIMITED** access to your AWS account. A compromised root user password can lead to:
> - Thousands of dollars in unauthorized charges
> - Data theft or destruction
> - Account takeover
>
> **NEVER share your root user credentials!**

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 lowercase letter (a-z)
- At least 1 number (0-9)
- At least 1 special character (!@#$%^&*)

> **Pro Tip: Password Manager**
>
> Use a password manager (like 1Password, Bitwarden, or LastPass) to generate and store a strong, unique password for your AWS account.

---

## Step 5: Contact Information

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Contact Information                                            │
│                                                                 │
│  How do you plan to use AWS?                                    │
│  ○ Business - for work, school, or organization                │
│  ● Personal - for your own projects  ← SELECT FOR LEARNING     │
│                                                                 │
│  Full name                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ John Doe                                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Phone number                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ +1 555-123-4567                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Country or Region                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ United States                                        ▼   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Address, City, State, Postal Code fields...                   │
│                                                                 │
│  [Continue]                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| Field | What to Enter |
|-------|---------------|
| **Account type** | Personal (for learning) |
| **Full name** | Your legal name |
| **Phone number** | Your phone number with country code |
| **Country/Region** | Your country |
| **Address** | Your billing address |

---

## Step 6: Payment Information

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Billing Information                                            │
│                                                                 │
│  Credit or Debit card number                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4111 1111 1111 1111                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Expiration date                    CVV/CVC                     │
│  ┌─────────────────────────┐       ┌───────────────────────┐   │
│  │ 12/2025                 │       │ 123                    │   │
│  └─────────────────────────┘       └───────────────────────┘   │
│                                                                 │
│  Cardholder's name                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ John Doe                                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Billing address: ○ Use contact address ● Use a new address   │
│                                                                 │
│  [Verify and Continue]                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **Note: About the Verification Charge**
>
> AWS will place a temporary $1 USD (or equivalent) hold on your card to verify it's valid. This is NOT a charge and will be released within 3-5 days. Some banks may show this as a pending transaction.

---

## Step 7: Identity Verification

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Confirm your identity                                          │
│                                                                 │
│  How should we send you the verification code?                  │
│  ○ Text message (SMS)                                          │
│  ● Voice call                                                   │
│                                                                 │
│  Country or region code                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ United States (+1)                                   ▼   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Phone number                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 555-123-4567                                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Security check (CAPTCHA)                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [CAPTCHA IMAGE]                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Type characters here                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Send SMS] or [Call me now]                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

1. Choose verification method (SMS or Voice call)
2. Enter your phone number
3. Complete the CAPTCHA
4. Click **"Send SMS"** or **"Call me now"**
5. Enter the verification code you receive

---

## Step 8: Select Support Plan

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Select a support plan                                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ● Basic Support - Free                                   │   │
│  │   Customer Service & Communities - 24x7 access           │   │
│  │   AWS Trusted Advisor - 7 core checks                    │   │
│  │   AWS Personal Health Dashboard                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ○ Developer - $29/month                                  │   │
│  │   Business hours email support                           │   │
│  │   1 primary contact, unlimited cases                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ○ Business - $100/month (minimum)                        │   │
│  │   24x7 phone, email, chat support                        │   │
│  │   Unlimited contacts, unlimited cases                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Complete sign up]                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Support Plan Comparison

| Feature | Basic (Free) | Developer ($29/mo) | Business ($100+/mo) |
|---------|--------------|-------------------|---------------------|
| **Cost** | Free | $29/month | Greater of $100 or 3-10% of usage |
| **Tech Support** | None | Business hours email | 24/7 phone, email, chat |
| **Response Time** | N/A | 12-24 hours | 1 hour for urgent |
| **Trusted Advisor** | 7 checks | 7 checks | All checks |
| **Best For** | Learning | Development | Production |

> **Pro Tip: Start with Basic**
>
> For learning purposes, **Basic Support (Free)** is sufficient. You can upgrade anytime if needed.

Select **"Basic Support - Free"** and click **"Complete sign up"**.

---

## Congratulations! Account Created!

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    ✓ Congratulations!                           │
│                                                                 │
│  Your AWS account is ready                                      │
│                                                                 │
│  Account ID: 123456789012                                       │
│                                                                 │
│  [Go to the AWS Management Console]                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **Note: Save Your Account ID**
>
> Your 12-digit AWS Account ID is important. Save it somewhere safe. You'll need it for:
> - IAM user login URLs
> - Cross-account access
> - Support cases

---

## Step 9: Enable Multi-Factor Authentication (MFA)

**MFA is ESSENTIAL for account security.** Do not skip this step!

### What is MFA?

MFA adds a second layer of security beyond your password. Even if someone steals your password, they can't access your account without the MFA device.

### Setting Up Virtual MFA

1. Sign in to the AWS Console at `https://console.aws.amazon.com`
2. Click on your account name (top right)
3. Click **"Security credentials"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  AWS Console                                        John Doe ▼  │
│                                                     ┌─────────┐ │
│                                                     │Account  │ │
│                                                     │Security │ │
│                                                     │credent..│ │
│                                                     │Sign out │ │
│                                                     └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

4. Scroll to **"Multi-factor authentication (MFA)"**
5. Click **"Assign MFA device"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Assign MFA device                                              │
│                                                                 │
│  Device name                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ my-root-mfa                                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Select MFA device type:                                        │
│  ● Authenticator app (Virtual MFA device)                      │
│  ○ Security key                                                │
│  ○ Hardware TOTP token                                         │
│                                                                 │
│  [Next]                                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

6. Enter a device name (e.g., "my-root-mfa")
7. Select **"Authenticator app"**
8. Click **"Next"**

### Recommended Authenticator Apps

| App | Platform | Cost |
|-----|----------|------|
| **Google Authenticator** | iOS, Android | Free |
| **Microsoft Authenticator** | iOS, Android | Free |
| **Authy** | iOS, Android, Desktop | Free |
| **1Password** | iOS, Android, Desktop | Paid |

9. Open your authenticator app
10. Scan the QR code shown by AWS

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Set up device                                                  │
│                                                                 │
│  1. Open your authenticator app                                 │
│  2. Scan the QR code                                           │
│                                                                 │
│     ┌───────────────────┐                                      │
│     │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │                                      │
│     │  ▓             ▓  │  ← Scan this with your app           │
│     │  ▓  QR CODE    ▓  │                                      │
│     │  ▓             ▓  │                                      │
│     │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │                                      │
│     └───────────────────┘                                      │
│                                                                 │
│  Or enter this code manually: ABCD EFGH IJKL MNOP              │
│                                                                 │
│  Enter two consecutive MFA codes:                               │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ 123456          │  │ 789012          │                      │
│  └─────────────────┘  └─────────────────┘                      │
│   MFA code 1           MFA code 2                               │
│                                                                 │
│  [Add MFA]                                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

11. Enter **two consecutive** MFA codes from your app
    - Wait for the first code, enter it
    - Wait for the code to change, enter the second code
12. Click **"Add MFA"**

> **Warning: Backup Your MFA**
>
> If you lose your MFA device, you could be locked out of your account!
> - Save the secret key/QR code in a secure location
> - Consider setting up MFA on multiple devices
> - AWS can help recover access, but it's a lengthy process

---

## Step 10: Set Up Billing Alerts

**This step prevents surprise charges!**

### Enable Billing Alerts

1. Go to **Billing Dashboard**: Click account name → **"Billing Dashboard"**
2. In the left menu, click **"Billing preferences"**
3. Enable these settings:

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Billing preferences                                            │
│                                                                 │
│  Alert preferences                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ☑ Receive AWS Free Tier alerts                          │   │
│  │   Email: your.email@example.com                          │   │
│  │                                                         │   │
│  │ ☑ Receive CloudWatch billing alerts                     │   │
│  │   (Required to create billing alarms)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Invoice delivery preferences                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ☑ Receive PDF invoice by email                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Save preferences]                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

4. Check ALL boxes:
   - Receive AWS Free Tier alerts
   - Receive CloudWatch billing alerts
   - Receive PDF invoice by email
5. Click **"Save preferences"**

### Create a Billing Alarm

1. Go to **CloudWatch**: Search "CloudWatch" in the search bar
2. Make sure you're in the **us-east-1** region (billing metrics only exist here)
3. Click **"Alarms"** → **"All alarms"** → **"Create alarm"**

**Screenshot Description:**
```
┌─────────────────────────────────────────────────────────────────┐
│  CloudWatch > Alarms > Create alarm                             │
│                                                                 │
│  Step 1: Specify metric and conditions                          │
│                                                                 │
│  [Select metric]                                                │
│                                                                 │
│  Browse:                                                        │
│  Billing → Total Estimated Charge → USD                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

4. Click **"Select metric"**
5. Navigate: **Billing** → **Total Estimated Charge** → **USD**
6. Check the box for **EstimatedCharges** where Currency = USD
7. Click **"Select metric"**

**Configure the threshold:**

```
Threshold type: Static
Whenever EstimatedCharges is: Greater than
Threshold: 5 (or whatever amount you're comfortable with)
```

8. Click **"Next"**
9. Create or select an SNS topic for notifications
10. Enter your email address for notifications
11. Click **"Create alarm"**

> **Pro Tip: Multiple Alarms**
>
> Create multiple alarms at different thresholds:
> - $1 - First notification
> - $5 - Warning
> - $10 - Urgent attention needed

---

## Understanding the Root User

| Aspect | Details |
|--------|---------|
| **What is it?** | The original account identity with complete access |
| **Email** | The email used to create the account |
| **Permissions** | FULL access to everything - cannot be restricted |
| **When to use** | Rarely - only for specific root-only tasks |

### Root User Best Practices

| Do | Don't |
|----|-------|
| Enable MFA immediately | Share credentials with anyone |
| Create IAM users for daily work | Use root for everyday tasks |
| Set up billing alerts | Log in as root regularly |
| Store credentials securely | Use root access keys |

### Tasks That REQUIRE Root User

- Changing account settings (name, email, password)
- Changing support plan
- Closing the AWS account
- Restoring IAM user permissions
- Creating CloudFront key pairs
- Viewing certain tax invoices

---

## Quick Security Checklist

Before moving on, verify you've completed these critical security steps:

- [ ] Account created successfully
- [ ] Root user has a strong, unique password
- [ ] MFA enabled on root user
- [ ] Billing alerts configured
- [ ] Free Tier alerts enabled
- [ ] Account ID saved securely

---

## Key Takeaways

| Concept | Remember This |
|---------|---------------|
| **Root User** | Most powerful account - use sparingly |
| **MFA** | Required for security - enable immediately |
| **Billing Alerts** | Prevents surprise charges |
| **Support Plan** | Start with Basic (Free) |
| **Account ID** | 12-digit number - save it |

---

## Troubleshooting Common Issues

### Can't Receive Verification Email

- Check spam/junk folder
- Add `@amazon.com` and `@aws.amazon.com` to your safe senders
- Wait a few minutes and try resending
- Try a different email address

### Card Declined

- Ensure card details are correct
- Check card is not expired
- Some prepaid cards may not work
- Contact your bank (they may block the authorization)

### MFA Issues

- Ensure your device's time is synchronized
- Try manual code entry instead of QR scan
- Use a different authenticator app

---

## What's Next?

Now that your account is created and secured, let's explore the AWS Console in **[04 - AWS Console Tour](04-aws-console-tour.md)**.

---

[<-- Previous: AWS Overview](02-aws-overview.md) | [Next: AWS Console Tour -->](04-aws-console-tour.md)
