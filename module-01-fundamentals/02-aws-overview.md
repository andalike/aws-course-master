# 02 - AWS Overview

## Section Overview

| Attribute | Details |
|-----------|---------|
| **Estimated Time** | 30 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | Understanding of cloud computing basics |

---

## Learning Objectives

After completing this section, you will be able to:

- Describe the history and evolution of AWS
- Explain AWS global infrastructure components
- Differentiate between Regions, Availability Zones, and Edge Locations
- Compare AWS with other major cloud providers
- Understand key AWS services categories

---

## The Story of AWS

### How It All Began

Amazon Web Services wasn't planned as a separate business—it evolved from Amazon's internal needs.

### Timeline of Key Events

| Year | Milestone |
|------|-----------|
| **2002** | Amazon.com launches web services, allowing developers to incorporate Amazon features into their websites |
| **2003** | Chris Pinkham and Benjamin Black propose idea of selling Amazon's infrastructure as a service |
| **2004** | SQS (Simple Queue Service) launches publicly—the first AWS service |
| **2006** | **AWS officially launches** with S3 (storage) and EC2 (compute) |
| **2007** | Over 180,000 developers sign up for AWS |
| **2008** | Elastic Block Store (EBS) and CloudFront CDN launch |
| **2009** | Amazon RDS (managed databases) launches |
| **2010** | Amazon.com retail operations move to AWS |
| **2011** | AWS GovCloud for US government workloads |
| **2012** | AWS re:Invent conference begins |
| **2013** | AWS certifications program launches |
| **2014** | AWS Lambda introduces serverless computing |
| **2015** | AWS revenue exceeds $7 billion |
| **2016** | AWS revenue exceeds $12 billion |
| **2018** | AWS revenue exceeds $25 billion |
| **2020** | AWS revenue exceeds $45 billion |
| **2021** | AWS revenue exceeds $62 billion |
| **2023** | AWS revenue exceeds $90 billion |

> **Fun Fact**
>
> Amazon's original internal infrastructure was so inefficient that engineers estimated they spent 70% of their time on "undifferentiated heavy lifting" (infrastructure) rather than innovation. This frustration led to AWS!

---

## Why AWS Dominates the Cloud Market

### Market Share Comparison (2024)

```
AWS         ████████████████████████████████  32%
Azure       ██████████████████████            23%
Google Cloud████████████                      10%
Others      ███████████████████████████████   35%
```

### AWS by the Numbers

| Metric | Value |
|--------|-------|
| **Global Market Share** | ~32% |
| **Number of Services** | 200+ |
| **Number of Regions** | 33+ |
| **Availability Zones** | 100+ |
| **Edge Locations** | 450+ |
| **Countries with Regions** | 26+ |
| **Active Customers** | Millions |
| **Annual Revenue** | $90+ billion |

---

## AWS Global Infrastructure

Understanding AWS's global infrastructure is **critical** for designing reliable, high-performance applications.

> **Real-World Analogy: The Postal System**
>
> - **Regions** = Countries (e.g., USA, UK, Japan)
> - **Availability Zones** = Major cities within each country
> - **Edge Locations** = Local post offices in your neighborhood

---

### Regions

A **Region** is a physical location around the world where AWS clusters data centers.

**Key Characteristics:**
- Completely independent and isolated from other Regions
- Contains at least 2 (usually 3 or more) Availability Zones
- Services and pricing can vary by Region
- Data is NOT replicated between Regions unless you explicitly configure it

**Current AWS Regions:**

| Region Code | Region Name | Availability Zones |
|-------------|-------------|-------------------|
| us-east-1 | N. Virginia | 6 |
| us-east-2 | Ohio | 3 |
| us-west-1 | N. California | 3 |
| us-west-2 | Oregon | 4 |
| ca-central-1 | Canada (Central) | 3 |
| eu-west-1 | Ireland | 3 |
| eu-west-2 | London | 3 |
| eu-west-3 | Paris | 3 |
| eu-central-1 | Frankfurt | 3 |
| eu-north-1 | Stockholm | 3 |
| ap-southeast-1 | Singapore | 3 |
| ap-southeast-2 | Sydney | 3 |
| ap-northeast-1 | Tokyo | 4 |
| ap-northeast-2 | Seoul | 4 |
| ap-northeast-3 | Osaka | 3 |
| ap-south-1 | Mumbai | 3 |
| sa-east-1 | São Paulo | 3 |

*Note: This list is not exhaustive. AWS regularly adds new Regions.*

**How to Choose a Region:**

| Factor | Consideration |
|--------|---------------|
| **Latency** | Choose closest Region to your users |
| **Compliance** | Data residency laws may require specific Regions |
| **Service Availability** | Not all services are available in all Regions |
| **Pricing** | Prices vary by Region (us-east-1 is often cheapest) |
| **Disaster Recovery** | Consider secondary Region for DR |

> **Pro Tip: Default to us-east-1**
>
> For learning and testing, `us-east-1` (N. Virginia) is recommended because:
> - Most services launch here first
> - Typically has the lowest prices
> - Largest service catalog
> - Most AWS documentation examples use this Region

---

### Availability Zones (AZs)

An **Availability Zone** is one or more discrete data centers with redundant power, networking, and connectivity in a Region.

**Key Characteristics:**
- Physically separated by a meaningful distance (many kilometers)
- Connected via high-speed, low-latency private links
- Designed to be isolated from failures in other AZs
- Named as Region + letter (e.g., us-east-1a, us-east-1b)

```
                    AWS Region: us-east-1 (N. Virginia)
    ┌──────────────────────────────────────────────────────────────┐
    │                                                              │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
    │  │    AZ-1a    │  │    AZ-1b    │  │    AZ-1c    │   ...    │
    │  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌───────┐  │          │
    │  │  │  DC   │  │  │  │  DC   │  │  │  │  DC   │  │          │
    │  │  │       │  │  │  │       │  │  │  │       │  │          │
    │  │  └───────┘  │  │  └───────┘  │  │  └───────┘  │          │
    │  │  ┌───────┐  │  │  ┌───────┐  │  │  ┌───────┐  │          │
    │  │  │  DC   │  │  │  │  DC   │  │  │  │  DC   │  │          │
    │  │  └───────┘  │  │  └───────┘  │  │  └───────┘  │          │
    │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
    │         │                │                │                  │
    │         └────────────────┼────────────────┘                  │
    │              High-speed, low-latency links                   │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
```

> **Warning: AZ Names are Account-Specific**
>
> The AZ `us-east-1a` in YOUR account might be a different physical data center than `us-east-1a` in ANOTHER account. AWS randomizes this mapping to distribute load evenly.

**Why Use Multiple AZs?**

| Scenario | Single AZ | Multiple AZs |
|----------|-----------|--------------|
| Power outage | Application DOWN | Application UP |
| Network failure | Application DOWN | Application UP |
| Natural disaster | Application DOWN | Application UP |
| Hardware failure | Possible downtime | Automatic failover |

> **Pro Tip: Design for Failure**
>
> Always deploy production workloads across at least 2 Availability Zones. AWS services like ELB and RDS make multi-AZ deployment easy.

---

### Edge Locations

**Edge Locations** are data centers designed to deliver content to end users with lower latency.

**Key Characteristics:**
- More numerous than Regions (450+ locations)
- Used primarily for caching content closer to users
- Smaller than AZs, optimized for content delivery
- Located in major cities worldwide

**Services Using Edge Locations:**

| Service | Purpose |
|---------|---------|
| **CloudFront** | Content Delivery Network (CDN) |
| **Route 53** | DNS service |
| **AWS WAF** | Web Application Firewall |
| **AWS Shield** | DDoS protection |
| **Lambda@Edge** | Run code at edge locations |

```
         User in Sydney
              │
              ▼
    ┌──────────────────┐
    │  Edge Location   │  ← Cached content served quickly
    │    (Sydney)      │
    └────────┬─────────┘
             │ (Cache miss? Fetch from origin)
             ▼
    ┌──────────────────┐
    │   Origin Server  │
    │  (ap-southeast-2)│
    └──────────────────┘
```

---

### Regional Edge Caches

These are larger caches between Edge Locations and your origin servers:

```
User → Edge Location → Regional Edge Cache → Origin (S3/EC2)
```

They keep content cached longer for less frequently accessed content.

---

### Local Zones

**Local Zones** are AWS infrastructure deployments that place compute, storage, and other services closer to large population centers.

**Use Cases:**
- Ultra-low latency applications (gaming, video streaming)
- Real-time applications
- Media content creation

**Example Local Zones:**
- Los Angeles
- Boston
- Houston
- Miami

---

### AWS Wavelength

**Wavelength** zones embed AWS compute and storage at the edge of 5G networks.

**Use Cases:**
- Mobile gaming
- Live video streaming
- AR/VR applications
- Connected vehicles

---

### AWS Outposts

**Outposts** brings AWS infrastructure and services to your on-premises data center.

**Use Cases:**
- Low-latency requirements
- Local data processing
- Data residency requirements
- Hybrid deployments

---

## Infrastructure Summary Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS GLOBAL INFRASTRUCTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REGIONS (33+)                                                          │
│  └── Complete, isolated deployments of AWS services                     │
│       │                                                                 │
│       ├── AVAILABILITY ZONES (100+)                                     │
│       │   └── One or more data centers per AZ                          │
│       │       └── Redundant power, networking, connectivity             │
│       │                                                                 │
│       └── LOCAL ZONES                                                   │
│           └── Extensions of Regions to metro areas                      │
│                                                                         │
│  EDGE LOCATIONS (450+)                                                  │
│  └── Content caching (CloudFront, Route 53)                            │
│       │                                                                 │
│       └── REGIONAL EDGE CACHES                                          │
│           └── Larger caches between edge and origin                     │
│                                                                         │
│  WAVELENGTH ZONES                                                       │
│  └── AWS at 5G network edge                                            │
│                                                                         │
│  OUTPOSTS                                                               │
│  └── AWS in your data center                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## AWS vs Competitors

### The Big Three Cloud Providers

| Feature | AWS | Azure | Google Cloud |
|---------|-----|-------|--------------|
| **Market Share** | ~32% | ~23% | ~10% |
| **Launch Year** | 2006 | 2010 | 2008 |
| **Number of Services** | 200+ | 200+ | 100+ |
| **Regions** | 33+ | 60+ | 35+ |
| **Strength** | Breadth & depth | Enterprise/Hybrid | Data/ML |
| **Primary Users** | Startups, Enterprise | Enterprise, Microsoft shops | Data companies |

### Service Name Comparison

| Service Type | AWS | Azure | Google Cloud |
|--------------|-----|-------|--------------|
| **Virtual Servers** | EC2 | Virtual Machines | Compute Engine |
| **Serverless Functions** | Lambda | Functions | Cloud Functions |
| **Object Storage** | S3 | Blob Storage | Cloud Storage |
| **Relational DB** | RDS | SQL Database | Cloud SQL |
| **NoSQL DB** | DynamoDB | Cosmos DB | Firestore/Bigtable |
| **Container Orchestration** | EKS | AKS | GKE |
| **CDN** | CloudFront | Azure CDN | Cloud CDN |
| **DNS** | Route 53 | Azure DNS | Cloud DNS |
| **IAM** | IAM | Azure AD | Cloud IAM |

### When to Choose AWS

**Choose AWS if you:**
- Need the broadest range of services
- Want the most mature cloud platform
- Are a startup (AWS has excellent startup programs)
- Need specific services only AWS offers
- Want the largest talent pool to hire from

**Choose Azure if you:**
- Are a Microsoft shop (Windows, Office 365, .NET)
- Need hybrid cloud capabilities
- Want to leverage existing Microsoft enterprise agreements

**Choose Google Cloud if you:**
- Are focused on data analytics and machine learning
- Use Kubernetes extensively (Google created it)
- Need BigQuery for data warehousing
- Are already using Google Workspace

---

## AWS Service Categories

AWS offers 200+ services. Here are the main categories:

### Core Service Categories

| Category | Description | Key Services |
|----------|-------------|--------------|
| **Compute** | Processing power | EC2, Lambda, ECS, EKS |
| **Storage** | Data storage | S3, EBS, EFS, Glacier |
| **Database** | Managed databases | RDS, DynamoDB, ElastiCache |
| **Networking** | Network infrastructure | VPC, Route 53, CloudFront |
| **Security** | Identity & security | IAM, KMS, WAF, Shield |
| **Management** | Operations tools | CloudWatch, CloudFormation |

### Additional Categories

| Category | Key Services |
|----------|--------------|
| **Analytics** | Athena, EMR, Kinesis, QuickSight |
| **Machine Learning** | SageMaker, Rekognition, Comprehend |
| **Developer Tools** | CodeCommit, CodeBuild, CodePipeline |
| **Application Integration** | SQS, SNS, EventBridge, Step Functions |
| **IoT** | IoT Core, IoT Greengrass |
| **Migration** | DMS, Snow Family, Application Migration |

> **Pro Tip: Start with the Core Five**
>
> As a beginner, focus on mastering these five foundational services first:
> 1. **EC2** - Virtual servers
> 2. **S3** - Object storage
> 3. **VPC** - Networking
> 4. **IAM** - Security & access
> 5. **RDS** - Managed databases

---

## AWS Well-Architected Framework

AWS provides a framework for building secure, high-performing, resilient, and efficient infrastructure. It has **six pillars**:

| Pillar | Focus |
|--------|-------|
| **Operational Excellence** | Running and monitoring systems |
| **Security** | Protecting information and systems |
| **Reliability** | Recovery from failures |
| **Performance Efficiency** | Using resources efficiently |
| **Cost Optimization** | Avoiding unnecessary costs |
| **Sustainability** | Minimizing environmental impact |

---

## Key Takeaways

| Concept | Remember This |
|---------|---------------|
| **Region** | Geographic area with multiple AZs |
| **Availability Zone** | One or more data centers in a Region |
| **Edge Location** | CDN endpoint for caching content |
| **Multi-AZ** | Deploy across AZs for high availability |
| **Service Categories** | Compute, Storage, Database, Networking, Security |
| **AWS Strength** | Breadth of services, market maturity |

---

## Self-Check Questions

Before moving on, make sure you can answer these questions:

1. What year did AWS officially launch with EC2 and S3?
2. What is the difference between a Region and an Availability Zone?
3. Why would you deploy an application across multiple AZs?
4. What are Edge Locations used for?
5. Name three factors to consider when choosing an AWS Region.

---

## What's Next?

Now that you understand AWS and its global infrastructure, let's create your own AWS account in **[03 - Creating Your AWS Account](03-creating-aws-account.md)**.

---

[<-- Previous: What is Cloud Computing](01-what-is-cloud-computing.md) | [Next: Creating Your AWS Account -->](03-creating-aws-account.md)
