# Project 1: Host a Static Website on AWS

## Project Overview

Build and deploy a professional static website using AWS S3, CloudFront, and Route 53. This project teaches you how to host content globally with high availability and low latency.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STATIC WEBSITE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     Users                                                                    │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────┐     ┌───────────────┐     ┌──────────────┐                    │
│  │  Route   │────▶│   CloudFront  │────▶│     S3       │                    │
│  │   53     │     │     (CDN)     │     │   Bucket     │                    │
│  │  (DNS)   │     │               │     │  (Origin)    │                    │
│  └──────────┘     │  Edge Locations│     │              │                    │
│                   │  - US East    │     │ index.html   │                    │
│                   │  - EU West    │     │ styles.css   │                    │
│                   │  - AP South   │     │ scripts.js   │                    │
│                   │  - ...        │     │ images/      │                    │
│                   └───────────────┘     └──────────────┘                    │
│                          │                                                   │
│                          ▼                                                   │
│                   ┌───────────────┐                                          │
│                   │     ACM       │                                          │
│                   │ (SSL/TLS Cert)│                                          │
│                   └───────────────┘                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Learning Objectives

By completing this project, you will:

- [ ] Create and configure an S3 bucket for static website hosting
- [ ] Set up proper bucket policies for public access
- [ ] Create a CloudFront distribution for global content delivery
- [ ] Configure a custom domain with Route 53
- [ ] Set up SSL/TLS certificate with AWS Certificate Manager
- [ ] Implement cache invalidation strategies

---

## Prerequisites

- Completed Module 1-4 of this course
- AWS Account with Free Tier access
- A domain name (optional, but recommended)
- Basic HTML/CSS knowledge

---

## Estimated Time

| Phase | Time |
|-------|------|
| S3 Setup | 30 minutes |
| CloudFront Configuration | 45 minutes |
| Route 53 & SSL | 30 minutes |
| Testing & Optimization | 30 minutes |
| **Total** | **~2.5 hours** |

---

## Step 1: Create the Website Files

First, let's create a simple but professional-looking website.

### Create Project Structure

```bash
mkdir -p my-website/{css,js,images}
cd my-website
```

### index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My AWS Hosted Website</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header class="hero">
        <nav class="navbar">
            <div class="logo">AWS Website</div>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
        <div class="hero-content">
            <h1>Welcome to My AWS-Hosted Website</h1>
            <p>This website is hosted on Amazon S3, delivered via CloudFront CDN</p>
            <a href="#services" class="cta-button">Learn More</a>
        </div>
    </header>

    <main>
        <section id="about" class="section">
            <h2>About This Project</h2>
            <div class="cards">
                <div class="card">
                    <h3>S3 Storage</h3>
                    <p>Static files stored securely in Amazon S3 with high durability (99.999999999%)</p>
                </div>
                <div class="card">
                    <h3>CloudFront CDN</h3>
                    <p>Content delivered from edge locations worldwide for minimal latency</p>
                </div>
                <div class="card">
                    <h3>Route 53 DNS</h3>
                    <p>Custom domain with highly available DNS routing</p>
                </div>
            </div>
        </section>

        <section id="services" class="section alt-bg">
            <h2>AWS Services Used</h2>
            <ul class="services-list">
                <li>Amazon S3 - Static file hosting</li>
                <li>Amazon CloudFront - Content Delivery Network</li>
                <li>Amazon Route 53 - DNS Management</li>
                <li>AWS Certificate Manager - SSL/TLS Certificates</li>
            </ul>
        </section>

        <section id="contact" class="section">
            <h2>Get In Touch</h2>
            <form id="contact-form">
                <input type="text" placeholder="Your Name" required>
                <input type="email" placeholder="Your Email" required>
                <textarea placeholder="Your Message" required></textarea>
                <button type="submit">Send Message</button>
            </form>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 AWS Training Project. Hosted on AWS.</p>
    </footer>

    <script src="js/main.js"></script>
</body>
</html>
```

### css/styles.css

```css
/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}

/* Navigation */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 5%;
    position: fixed;
    width: 100%;
    top: 0;
    background: rgba(0, 0, 0, 0.8);
    z-index: 1000;
}

.logo {
    color: #ff9900;
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-links a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;
}

.nav-links a:hover {
    color: #ff9900;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #232f3e 0%, #1a252f 100%);
    color: white;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.hero-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2rem;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.cta-button {
    background: #ff9900;
    color: #232f3e;
    padding: 1rem 2rem;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
    transition: transform 0.3s, box-shadow 0.3s;
}

.cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 153, 0, 0.4);
}

/* Sections */
.section {
    padding: 5rem 10%;
}

.section h2 {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: #232f3e;
}

.alt-bg {
    background: #f5f5f5;
}

/* Cards */
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

.card:hover {
    transform: translateY(-5px);
}

.card h3 {
    color: #ff9900;
    margin-bottom: 1rem;
}

/* Services List */
.services-list {
    max-width: 600px;
    margin: 0 auto;
    list-style: none;
}

.services-list li {
    padding: 1rem;
    margin-bottom: 0.5rem;
    background: white;
    border-left: 4px solid #ff9900;
    border-radius: 0 5px 5px 0;
}

/* Contact Form */
#contact-form {
    max-width: 500px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

#contact-form input,
#contact-form textarea {
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
}

#contact-form textarea {
    min-height: 150px;
    resize: vertical;
}

#contact-form button {
    background: #ff9900;
    color: white;
    padding: 1rem;
    border: none;
    border-radius: 5px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s;
}

#contact-form button:hover {
    background: #e88a00;
}

/* Footer */
footer {
    background: #232f3e;
    color: white;
    text-align: center;
    padding: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }

    .nav-links {
        display: none;
    }

    .section {
        padding: 3rem 5%;
    }
}
```

### js/main.js

```javascript
// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar background change on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(35, 47, 62, 0.95)';
    } else {
        navbar.style.background = 'rgba(0, 0, 0, 0.8)';
    }
});

// Form submission handler
document.getElementById('contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your message! (This is a static site demo)');
    this.reset();
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.card, .services-list li').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
});

console.log('Website loaded successfully!');
console.log('Hosted on AWS S3 with CloudFront CDN');
```

### error.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #232f3e;
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .container {
            text-align: center;
        }
        h1 {
            font-size: 6rem;
            color: #ff9900;
            margin: 0;
        }
        p {
            font-size: 1.5rem;
            margin: 1rem 0;
        }
        a {
            color: #ff9900;
            text-decoration: none;
            padding: 1rem 2rem;
            border: 2px solid #ff9900;
            display: inline-block;
            margin-top: 1rem;
            transition: all 0.3s;
        }
        a:hover {
            background: #ff9900;
            color: #232f3e;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <p>Oops! The page you're looking for doesn't exist.</p>
        <a href="/">Return Home</a>
    </div>
</body>
</html>
```

---

## Step 2: Create S3 Bucket for Hosting

### Using AWS Console

1. Navigate to **S3** in AWS Console
2. Click **Create bucket**
3. Configure:
   - Bucket name: `my-website-[unique-id]` (must be globally unique)
   - Region: Choose closest to your users
   - Uncheck "Block all public access" (we'll secure via CloudFront)
   - Acknowledge the warning
4. Click **Create bucket**

### Using AWS CLI

```bash
# Create the bucket
aws s3 mb s3://my-website-unique-12345 --region us-east-1

# Enable static website hosting
aws s3 website s3://my-website-unique-12345 \
    --index-document index.html \
    --error-document error.html

# Upload files
aws s3 sync ./my-website s3://my-website-unique-12345 \
    --exclude ".git/*"

# Verify upload
aws s3 ls s3://my-website-unique-12345 --recursive
```

### Set Bucket Policy

Create a file named `bucket-policy.json`:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-website-unique-12345/*"
        }
    ]
}
```

Apply the policy:

```bash
aws s3api put-bucket-policy \
    --bucket my-website-unique-12345 \
    --policy file://bucket-policy.json
```

---

## Step 3: Create CloudFront Distribution

### Using AWS Console

1. Navigate to **CloudFront**
2. Click **Create Distribution**
3. Configure:
   - **Origin Domain**: Select your S3 bucket
   - **Origin Access**: Create new OAC (Origin Access Control)
   - **Viewer Protocol Policy**: Redirect HTTP to HTTPS
   - **Cache Policy**: CachingOptimized
   - **Default Root Object**: index.html
4. Click **Create Distribution**

### Using AWS CLI

```bash
# Create Origin Access Control
aws cloudfront create-origin-access-control \
    --origin-access-control-config '{
        "Name": "my-website-oac",
        "Description": "OAC for static website",
        "SigningProtocol": "sigv4",
        "SigningBehavior": "always",
        "OriginAccessControlOriginType": "s3"
    }'

# Create distribution config file
cat > distribution-config.json << 'EOF'
{
    "CallerReference": "my-website-2026",
    "Comment": "Static website distribution",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3Origin",
                "DomainName": "my-website-unique-12345.s3.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": ""
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3Origin",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
        },
        "CachedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {"Forward": "none"}
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/error.html",
                "ResponseCode": "404",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "Enabled": true
}
EOF

# Create distribution
aws cloudfront create-distribution \
    --distribution-config file://distribution-config.json
```

---

## Step 4: Configure Custom Domain (Optional)

### Request SSL Certificate

```bash
# Request certificate (must be in us-east-1 for CloudFront)
aws acm request-certificate \
    --domain-name www.yourdomain.com \
    --validation-method DNS \
    --region us-east-1
```

### Create Route 53 Hosted Zone

```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name yourdomain.com \
    --caller-reference $(date +%s)

# Create alias record pointing to CloudFront
# (Use the CloudFront distribution domain name)
```

---

## Step 5: Cache Invalidation

When you update content, invalidate the cache:

```bash
# Invalidate all files
aws cloudfront create-invalidation \
    --distribution-id EXAMPLEDIST \
    --paths "/*"

# Invalidate specific files
aws cloudfront create-invalidation \
    --distribution-id EXAMPLEDIST \
    --paths "/index.html" "/css/styles.css"
```

---

## Cost Breakdown

| Service | Monthly Cost (Estimate) |
|---------|------------------------|
| S3 Storage (1GB) | ~$0.023 |
| S3 Requests | ~$0.004 |
| CloudFront (10GB transfer) | ~$0.85 |
| Route 53 Hosted Zone | $0.50 |
| **Total** | **~$1.40/month** |

---

## Cleanup

To avoid charges, delete resources in this order:

```bash
# 1. Delete CloudFront distribution (disable first)
aws cloudfront get-distribution-config --id DIST_ID
# Update to set Enabled: false
aws cloudfront update-distribution --id DIST_ID --if-match ETAG --distribution-config file://disabled.json
# Wait for deployment, then delete
aws cloudfront delete-distribution --id DIST_ID --if-match ETAG

# 2. Empty and delete S3 bucket
aws s3 rm s3://my-website-unique-12345 --recursive
aws s3 rb s3://my-website-unique-12345

# 3. Delete Route 53 hosted zone (if created)
aws route53 delete-hosted-zone --id ZONE_ID
```

---

## Verification Checklist

- [ ] Website loads via CloudFront URL
- [ ] HTTPS is working
- [ ] All pages load correctly
- [ ] Images and assets are served
- [ ] Error page displays for 404
- [ ] Custom domain works (if configured)

---

## Stretch Goals

1. **Add contact form backend** - Use Lambda + API Gateway + SES
2. **Implement CI/CD** - Auto-deploy on GitHub push using CodePipeline
3. **Add analytics** - Integrate CloudFront logs with Athena
4. **Improve performance** - Add CloudFront functions for URL rewrites

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Access Denied | Check bucket policy and OAC configuration |
| SSL Certificate pending | Validate DNS records in ACM |
| Old content showing | Create cache invalidation |
| 403 on refresh | Configure custom error response |

---

**Congratulations!** You've deployed a production-ready static website on AWS!

[← Back to Projects](../) | [Next Project: Web Application →](../02-web-application/)
