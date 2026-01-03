# Module 03: EC2 Comprehensive Quiz

## Instructions

- Total Questions: 30
- Time Limit: 45 minutes (suggested)
- Passing Score: 80% (24 correct answers)
- Question Types: Multiple Choice, Multiple Select, Scenario-Based

---

## Section 1: EC2 Fundamentals and Instance Types (Questions 1-6)

### Question 1

**Which EC2 instance family would you choose for a high-performance computing (HPC) workload that requires the highest compute performance?**

A) T3 - General Purpose
B) R6i - Memory Optimized
C) C7g - Compute Optimized
D) M6i - General Purpose

<details>
<summary>Show Answer</summary>

**Correct Answer: C) C7g - Compute Optimized**

**Explanation:**
- **C (Compute Optimized)** instances are designed for compute-intensive workloads that benefit from high-performance processors
- HPC workloads like batch processing, scientific modeling, and gaming servers require high CPU performance
- T3 instances are burstable and not suitable for sustained high-performance workloads
- R6i is optimized for memory, not compute
- M6i is general purpose, providing balanced compute, memory, and networking

**Key Point:** Instance family selection is based on the workload characteristics - compute, memory, storage, or accelerated computing needs.
</details>

---

### Question 2

**A company runs a development environment that experiences variable CPU usage throughout the day. Most of the time, CPU usage is low, but occasionally spikes to 100% for short periods. Which instance type is MOST cost-effective?**

A) C6i.large
B) T3.large
C) M6i.large
D) R6i.large

<details>
<summary>Show Answer</summary>

**Correct Answer: B) T3.large**

**Explanation:**
- **T3 instances** are burstable performance instances that provide a baseline level of CPU performance with the ability to burst above the baseline
- They accumulate CPU credits during idle periods and use them during burst periods
- This is perfect for variable workloads with occasional spikes
- C6i is compute-optimized (expensive for variable loads)
- M6i is general purpose (fixed performance, more expensive)
- R6i is memory-optimized (wrong use case)

**Cost Savings:** T3 instances can be up to 10% cheaper than M6i while providing burst capability for development workloads.
</details>

---

### Question 3

**What does the "xlarge" in instance type "m6i.xlarge" represent?**

A) The instance generation
B) The processor type
C) The instance size (vCPUs and memory)
D) The networking capability

<details>
<summary>Show Answer</summary>

**Correct Answer: C) The instance size (vCPUs and memory)**

**Explanation:**
Instance type naming convention: `[family][generation][attributes].[size]`

- **m** = Instance family (General Purpose)
- **6** = Generation (6th generation)
- **i** = Attribute (Intel processor)
- **xlarge** = Size (4 vCPUs, 16 GiB memory)

Size progression: nano < micro < small < medium < large < xlarge < 2xlarge < 4xlarge < 8xlarge < 12xlarge < 16xlarge < 24xlarge < metal

</details>

---

### Question 4 (Multiple Select)

**Which of the following statements about EC2 instance states are TRUE? (Select THREE)**

A) A stopped instance does not incur compute charges but does incur EBS charges
B) Instance store volumes persist data when an instance is stopped
C) A terminated instance cannot be restarted
D) Public IP addresses are retained when an instance is stopped and started
E) Private IP addresses are retained when an instance is stopped and started
F) A stopped instance can be resized to a different instance type

<details>
<summary>Show Answer</summary>

**Correct Answers: A, C, E, F**

**Explanation:**
- **A) TRUE** - Stopped instances don't incur EC2 charges, but attached EBS volumes continue to incur storage charges
- **B) FALSE** - Instance store volumes are ephemeral; data is LOST when instance stops
- **C) TRUE** - Terminated instances are permanently deleted and cannot be recovered
- **D) FALSE** - Public IP addresses are released when stopped; use Elastic IP for persistence
- **E) TRUE** - Private IP addresses are retained across stop/start cycles
- **F) TRUE** - You can change instance type only when the instance is stopped

**Key Insight:** Understanding instance states is crucial for cost management and data persistence planning.
</details>

---

### Question 5

**What is the maximum ratio of EBS-optimized throughput to instance network bandwidth for EBS-optimized instances?**

A) EBS bandwidth is always equal to network bandwidth
B) EBS bandwidth is separate and dedicated
C) EBS bandwidth shares the network bandwidth
D) EBS bandwidth is limited to 50% of network bandwidth

<details>
<summary>Show Answer</summary>

**Correct Answer: B) EBS bandwidth is separate and dedicated**

**Explanation:**
- **EBS-optimized instances** provide dedicated bandwidth for EBS I/O, separate from network traffic
- This prevents network traffic from impacting storage performance and vice versa
- Most current-generation instances are EBS-optimized by default
- The dedicated EBS bandwidth varies by instance type (e.g., m6i.large has 10 Gbps EBS bandwidth)

**Best Practice:** Always use EBS-optimized instances for production workloads to ensure consistent storage performance.
</details>

---

### Question 6

**A web application requires instances that can handle 10 Gbps network bandwidth and provide enhanced networking capabilities. Which feature should you verify is enabled?**

A) EBS optimization
B) Elastic Network Adapter (ENA)
C) Instance store
D) Placement groups

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Elastic Network Adapter (ENA)**

**Explanation:**
- **ENA (Elastic Network Adapter)** provides enhanced networking capabilities with higher bandwidth and lower latency
- ENA supports up to 100 Gbps on supported instance types
- It's required for instances that need high network performance
- EBS optimization is for storage, not network
- Instance store is for local storage
- Placement groups help with latency but don't provide networking capability by themselves

**Note:** Most current-generation instances support ENA by default. Verify ENA driver installation for older AMIs.
</details>

---

## Section 2: Pricing Models (Questions 7-12)

### Question 7

**A company runs a critical production database that must run 24/7 for the next 3 years. The database requires a specific instance type (r6i.2xlarge). Which pricing model offers the MOST cost savings?**

A) On-Demand Instances
B) Spot Instances
C) Reserved Instances (3-year, All Upfront)
D) Savings Plans (3-year, Compute)

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Reserved Instances (3-year, All Upfront)**

**Explanation:**
- **Reserved Instances** with 3-year term and All Upfront payment provides up to **72% discount** compared to On-Demand
- For a specific instance type that must run continuously, Reserved Instances offer the best savings
- Savings Plans offer flexibility but slightly less discount for committed instance types
- Spot Instances can be interrupted, unsuitable for databases
- On-Demand is the most expensive option

**Pricing Comparison (approximate for r6i.2xlarge):**
| Option | Discount |
|--------|----------|
| On-Demand | 0% |
| 1-year RI (All Upfront) | ~40% |
| 3-year RI (All Upfront) | ~72% |
| Compute Savings Plan | ~66% |
</details>

---

### Question 8

**Which EC2 pricing option allows you to bid on unused EC2 capacity and can provide up to 90% discount but may be interrupted?**

A) Reserved Instances
B) Spot Instances
C) Scheduled Reserved Instances
D) Dedicated Hosts

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Spot Instances**

**Explanation:**
- **Spot Instances** allow you to use spare EC2 capacity at up to 90% discount
- AWS can reclaim Spot Instances with a 2-minute warning when capacity is needed
- Best for: batch processing, CI/CD, data analysis, stateless web servers
- NOT suitable for: databases, critical applications, instances that can't handle interruption

**Interruption Handling Options:**
1. Hibernate (saves memory state)
2. Stop (loses in-memory data)
3. Terminate (default)
</details>

---

### Question 9 (Multiple Select)

**A startup needs flexibility to change instance types and regions over time while still saving costs. Which options would you recommend? (Select TWO)**

A) Standard Reserved Instances
B) Convertible Reserved Instances
C) Compute Savings Plans
D) EC2 Instance Savings Plans
E) Spot Instances

<details>
<summary>Show Answer</summary>

**Correct Answers: B, C**

**Explanation:**
- **B) Convertible Reserved Instances** - Can be exchanged for different instance types, OS, or tenancy (but not regions)
- **C) Compute Savings Plans** - Most flexible; applies to any instance family, size, OS, tenancy, or region

**Why not others:**
- **A) Standard RIs** - Cannot change instance family or region
- **D) EC2 Instance Savings Plans** - Locked to specific instance family in a region
- **E) Spot Instances** - Can be interrupted, not suitable for all workloads

**Flexibility Ranking:**
1. Compute Savings Plans (most flexible)
2. Convertible RIs (moderately flexible)
3. EC2 Instance Savings Plans (region-locked)
4. Standard RIs (least flexible)
</details>

---

### Question 10

**A company has regulatory requirements that prohibit sharing physical hardware with other AWS customers. Which pricing option must they use?**

A) Reserved Instances
B) Spot Instances
C) Dedicated Instances
D) On-Demand Instances

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Dedicated Instances**

**Explanation:**
- **Dedicated Instances** run on hardware dedicated to a single customer
- They provide physical isolation at the host level
- Available options for dedicated hardware:
  - **Dedicated Instances** - Per-instance pricing, hardware dedicated to your account
  - **Dedicated Hosts** - Pay for entire physical host, visibility into sockets/cores

**Use Cases:**
- Compliance requirements (HIPAA, PCI-DSS)
- Licensing that requires dedicated hardware
- Security requirements for physical isolation

**Note:** Dedicated Instances can be combined with Reserved Instance pricing for cost savings.
</details>

---

### Question 11

**Which statement about Spot Instance pricing is CORRECT?**

A) Spot price is fixed and never changes
B) You set a maximum price, and if the Spot price exceeds it, your instance is terminated
C) Spot Instances always cost exactly 90% less than On-Demand
D) Spot Instances cannot be used with Auto Scaling groups

<details>
<summary>Show Answer</summary>

**Correct Answer: B) You set a maximum price, and if the Spot price exceeds it, your instance is terminated**

**Explanation:**
- Spot price varies based on supply and demand
- You can set a maximum price (up to On-Demand price)
- If Spot price exceeds your max, instance is interrupted with 2-minute warning
- Current Spot pricing model is simpler - instances run until capacity is needed

**Incorrect statements:**
- A) Spot price fluctuates based on availability
- C) Discount varies (can be 50-90% depending on instance type and AZ)
- D) Spot Instances work excellently with Auto Scaling for cost optimization
</details>

---

### Question 12

**A media company runs batch video encoding jobs that can be interrupted and restarted. The jobs typically take 2-4 hours. Which combination provides the BEST cost optimization?**

A) On-Demand Instances only
B) Reserved Instances only
C) Spot Instances with checkpointing
D) Dedicated Hosts

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Spot Instances with checkpointing**

**Explanation:**
- **Spot Instances** provide up to 90% savings, perfect for interruptible workloads
- **Checkpointing** saves job progress periodically, allowing restart from last checkpoint if interrupted
- Video encoding is typically:
  - Compute-intensive
  - Parallelizable
  - Can handle interruption with proper design

**Best Practices for Spot with Batch Jobs:**
1. Save state/checkpoints regularly
2. Use multiple Spot pools (instance types/AZs)
3. Mix with On-Demand for baseline capacity
4. Use Spot Fleet or Auto Scaling with mixed instances
</details>

---

## Section 3: AMIs and Storage (Questions 13-18)

### Question 13

**Which statement about Amazon Machine Images (AMIs) is TRUE?**

A) AMIs are global and can be used in any region without copying
B) AMIs can only be created from running instances
C) AMI backing storage can be either EBS or Instance Store
D) AMIs cannot be shared between AWS accounts

<details>
<summary>Show Answer</summary>

**Correct Answer: C) AMI backing storage can be either EBS or Instance Store**

**Explanation:**
- **EBS-backed AMIs** - Root device is an EBS volume created from a snapshot
- **Instance Store-backed AMIs** - Root device is stored in S3

**Incorrect statements:**
- A) AMIs are regional; must be copied to use in other regions
- B) AMIs can be created from running or stopped instances (use --no-reboot option)
- D) AMIs can be shared publicly or with specific accounts

**EBS vs Instance Store AMIs:**
| Feature | EBS-backed | Instance Store |
|---------|------------|----------------|
| Stop/Start | Yes | No |
| Root Size | Up to 64 TiB | Up to 10 GB |
| Boot Time | < 1 minute | 3-5 minutes |
| Data Persistence | Yes | No |
</details>

---

### Question 14

**A DevOps engineer created a custom AMI and needs to make it available in another region for disaster recovery. What is the correct approach?**

A) AMIs are automatically replicated to all regions
B) Use `aws ec2 copy-image` to copy the AMI to the target region
C) Share the AMI with the target region
D) Create a snapshot and restore it in the target region

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Use `aws ec2 copy-image` to copy the AMI to the target region**

**Explanation:**

```bash
# Copy AMI to another region
aws ec2 copy-image \
    --source-region us-east-1 \
    --source-image-id ami-0123456789abcdef0 \
    --name "My-AMI-DR-Copy" \
    --region us-west-2
```

**Key Points:**
- AMIs are regional resources
- Copying includes all associated EBS snapshots
- Copied AMI gets a new AMI ID in the target region
- Can copy AMIs across accounts and regions
- Encryption can be added during copy

**Use Cases for Cross-Region AMI Copy:**
- Disaster recovery
- Multi-region deployment
- Migration to different regions
</details>

---

### Question 15

**Which EBS volume type provides the highest IOPS performance for a transactional database?**

A) gp2 (General Purpose SSD)
B) gp3 (General Purpose SSD)
C) io2 Block Express
D) st1 (Throughput Optimized HDD)

<details>
<summary>Show Answer</summary>

**Correct Answer: C) io2 Block Express**

**Explanation:**

| Volume Type | Max IOPS | Max Throughput | Use Case |
|-------------|----------|----------------|----------|
| gp2 | 16,000 | 250 MiB/s | General purpose |
| gp3 | 16,000 | 1,000 MiB/s | General purpose |
| io1 | 64,000 | 1,000 MiB/s | Critical databases |
| **io2** | 64,000 | 1,000 MiB/s | Critical databases |
| **io2 Block Express** | **256,000** | **4,000 MiB/s** | **Highest performance** |
| st1 | 500 | 500 MiB/s | Big data, warehouses |
| sc1 | 250 | 250 MiB/s | Cold storage |

**io2 Block Express** is designed for the most demanding I/O-intensive applications like SAP HANA, Oracle, and SQL Server.
</details>

---

### Question 16

**What happens to data on an instance store volume when the EC2 instance is stopped?**

A) Data is persisted and available when the instance starts
B) Data is automatically backed up to S3
C) Data is lost
D) Data is moved to an EBS volume

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Data is lost**

**Explanation:**
Instance store volumes are **ephemeral** storage:
- Data persists only while instance is **running**
- Data is **lost** when instance is stopped, terminated, or fails
- Data **survives** instance reboot (not stop)

**When to use Instance Store:**
- Buffer, cache, temporary data
- Data replicated across multiple instances
- High-performance temporary storage (NVMe SSDs)

**When to use EBS:**
- Persistent data
- Database storage
- Boot volumes
- Any data that must survive instance stop/termination
</details>

---

### Question 17 (Multiple Select)

**Which statements about EBS snapshots are TRUE? (Select THREE)**

A) Snapshots are stored in Amazon S3
B) Snapshots are incremental, storing only changed blocks
C) You cannot create a volume from a snapshot in a different region
D) Deleting a snapshot removes only the data not needed by other snapshots
E) Snapshots must be created from stopped instances
F) Encrypted snapshots can only be shared within the same AWS account

<details>
<summary>Show Answer</summary>

**Correct Answers: A, B, D**

**Explanation:**
- **A) TRUE** - Snapshots are stored redundantly in S3 (managed by AWS)
- **B) TRUE** - Only changed blocks since last snapshot are stored (saves space and cost)
- **C) FALSE** - Snapshots can be copied to other regions and volumes created there
- **D) TRUE** - Deleting a snapshot removes only unique data; shared blocks remain
- **E) FALSE** - Snapshots can be created from running instances (may have inconsistent state)
- **F) FALSE** - Encrypted snapshots can be shared if using a custom CMK

**Snapshot Best Practices:**
1. Use consistent snapshots (stop I/O or use VSS for Windows)
2. Automate with Data Lifecycle Manager
3. Copy critical snapshots to another region
4. Use snapshot tags for organization
</details>

---

### Question 18

**A company needs to encrypt an existing unencrypted EBS volume. What is the correct process?**

A) Enable encryption on the existing volume
B) Create a snapshot, copy with encryption, create new encrypted volume
C) Use AWS KMS to encrypt the volume in place
D) Encryption cannot be added to existing volumes

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Create a snapshot, copy with encryption, create new encrypted volume**

**Explanation:**
You cannot directly encrypt an existing unencrypted EBS volume. The process is:

```bash
# 1. Create snapshot of unencrypted volume
aws ec2 create-snapshot --volume-id vol-xxx --description "For encryption"

# 2. Copy snapshot with encryption
aws ec2 copy-snapshot \
    --source-region us-east-1 \
    --source-snapshot-id snap-xxx \
    --encrypted \
    --kms-key-id alias/my-key \
    --description "Encrypted copy"

# 3. Create encrypted volume from encrypted snapshot
aws ec2 create-volume \
    --snapshot-id snap-encrypted \
    --availability-zone us-east-1a
```

**Key Points:**
- Encryption is set at volume creation time
- Encrypted volumes remain encrypted
- Unencrypted volumes remain unencrypted
- Use snapshot copy to change encryption state
</details>

---

## Section 4: Auto Scaling (Questions 19-23)

### Question 19

**What is the recommended method for specifying instance configuration in Auto Scaling groups?**

A) Launch Configuration
B) Launch Template
C) CloudFormation Template
D) Instance Profile

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Launch Template**

**Explanation:**
**Launch Templates** are recommended over Launch Configurations because they support:
- Versioning
- Multiple instance types in one template
- Spot and On-Demand mix
- T2/T3 Unlimited mode
- Dedicated Hosts
- Capacity Reservations
- Elastic Inference

**Launch Configurations** are legacy and being deprecated.

**Best Practice:** Always use Launch Templates for new Auto Scaling groups.
</details>

---

### Question 20

**An Auto Scaling group has the following configuration: Min=2, Desired=4, Max=6. A scaling policy adds 3 instances. How many instances will be running?**

A) 4 instances
B) 6 instances
C) 7 instances
D) 9 instances

<details>
<summary>Show Answer</summary>

**Correct Answer: B) 6 instances**

**Explanation:**
- Current: 4 instances
- Scaling action: +3 instances
- Would result in: 7 instances
- But **Max=6**, so Auto Scaling caps at 6

Auto Scaling group capacity is always bounded by Min and Max values:
- Never goes below Min
- Never goes above Max
- Desired adjusts within these bounds

```
Min (2) ◄──────── Desired (4) ──────────► Max (6)
                      │
              Scaling Action +3
                      │
                      ▼
              Would be 7, but capped at Max = 6
```
</details>

---

### Question 21

**Which scaling policy type automatically creates and manages CloudWatch alarms for you?**

A) Simple Scaling
B) Step Scaling
C) Target Tracking Scaling
D) Scheduled Scaling

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Target Tracking Scaling**

**Explanation:**
**Target Tracking Scaling:**
- You specify a target value (e.g., CPU at 50%)
- ASG automatically creates and manages alarms
- Continuously adjusts capacity to maintain target
- Simplest to configure and most commonly used

**Other policies:**
- **Simple Scaling** - You create alarms, basic response
- **Step Scaling** - You create alarms, graduated response
- **Scheduled Scaling** - Time-based, no alarms

```bash
# Target Tracking Example
aws autoscaling put-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 50.0
    }'
```
</details>

---

### Question 22

**What is the purpose of a lifecycle hook in Auto Scaling?**

A) To automatically restart failed instances
B) To perform custom actions during instance launch or termination
C) To change the instance type during scaling
D) To modify security groups dynamically

<details>
<summary>Show Answer</summary>

**Correct Answer: B) To perform custom actions during instance launch or termination**

**Explanation:**
**Lifecycle Hooks** pause instances during launch or termination to allow custom actions:

**Launch Hook Use Cases:**
- Install/configure software
- Pull code from repository
- Register with service discovery
- Run health verification

**Termination Hook Use Cases:**
- Deregister from service discovery
- Drain connections
- Upload logs to S3
- Notify external systems

```
Launch: Pending → Pending:Wait → Pending:Proceed → InService
                      ↑
              [Custom Actions]

Terminate: InService → Terminating:Wait → Terminating:Proceed → Terminated
                              ↑
                      [Custom Actions]
```
</details>

---

### Question 23

**An application experiences predictable traffic patterns with high load during business hours (9 AM - 6 PM) and low load overnight. Which scaling approach is MOST cost-effective?**

A) Target Tracking with CPU utilization
B) Scheduled Scaling combined with Target Tracking
C) Step Scaling with CloudWatch alarms
D) Manual scaling twice daily

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Scheduled Scaling combined with Target Tracking**

**Explanation:**
Combining **Scheduled Scaling** with **Target Tracking** provides:

1. **Scheduled Scaling** - Proactively adjusts capacity before predicted load
   - Scale up at 8:45 AM (before traffic increase)
   - Scale down at 6:15 PM (after traffic decrease)

2. **Target Tracking** - Handles unexpected variations
   - Maintains CPU at target during normal variations
   - Scales for unexpected spikes

```bash
# Scheduled: Scale up before business hours
aws autoscaling put-scheduled-update-group-action \
    --scheduled-action-name scale-up-morning \
    --recurrence "45 8 * * MON-FRI" \
    --desired-capacity 10

# Target Tracking: Handle variations
aws autoscaling put-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-configuration '{
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ASGAverageCPUUtilization"
        },
        "TargetValue": 60.0
    }'
```

This combination is more cost-effective than reactive-only scaling because instances are ready before load increases.
</details>

---

## Section 5: Load Balancing (Questions 24-28)

### Question 24

**A company needs to route traffic based on URL paths (/api/* to backend, /images/* to CDN). Which load balancer type should they use?**

A) Classic Load Balancer
B) Network Load Balancer
C) Application Load Balancer
D) Gateway Load Balancer

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Application Load Balancer**

**Explanation:**
**Application Load Balancer (ALB)** operates at Layer 7 and supports:
- **Path-based routing** (/api/*, /images/*)
- Host-based routing (api.example.com, www.example.com)
- Query string routing (?version=v2)
- Header-based routing
- HTTP/HTTPS, WebSocket, gRPC

**Other load balancers:**
- **NLB** - Layer 4, no content-based routing
- **CLB** - Legacy, limited routing options
- **GWLB** - For security appliances

```
Request: /api/users
    │
    ▼
┌─────────────────┐
│      ALB        │
│  Rule: /api/*   │───► API Target Group
│  Rule: /images/*│───► Images Target Group
│  Default        │───► Web Target Group
└─────────────────┘
```
</details>

---

### Question 25

**Which load balancer type should you use when you need static IP addresses for whitelisting by clients?**

A) Application Load Balancer
B) Network Load Balancer
C) Classic Load Balancer
D) Gateway Load Balancer

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Network Load Balancer**

**Explanation:**
**Network Load Balancer (NLB)** provides:
- **Static IP addresses** (one per AZ)
- **Elastic IP support** (assign your own IPs)
- Ideal for clients that whitelist IP addresses

**ALB alternatives for static IP:**
- Use AWS Global Accelerator (provides static IPs that route to ALB)
- Use NLB in front of ALB

**NLB Static IP Example:**
```bash
aws elbv2 create-load-balancer \
    --type network \
    --subnet-mappings "SubnetId=subnet-1,AllocationId=eipalloc-xxx" \
                      "SubnetId=subnet-2,AllocationId=eipalloc-yyy"
```
</details>

---

### Question 26 (Multiple Select)

**Which health check configurations are available for Application Load Balancer target groups? (Select THREE)**

A) HTTP health checks
B) HTTPS health checks
C) TCP health checks
D) UDP health checks
E) Custom Lambda health checks
F) gRPC health checks

<details>
<summary>Show Answer</summary>

**Correct Answers: A, B, F**

**Explanation:**
**ALB Target Group Health Checks:**
- **HTTP** - Most common, checks path for 200-299 response
- **HTTPS** - For SSL-enabled backends
- **gRPC** - For gRPC applications

**Not supported by ALB target groups:**
- **TCP** - Available for NLB, not ALB
- **UDP** - Available for NLB, not ALB
- **Lambda** - Lambda targets don't use traditional health checks

**Health Check Configuration:**
```bash
aws elbv2 modify-target-group \
    --target-group-arn $TG_ARN \
    --health-check-protocol HTTP \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --matcher "HttpCode=200-299"
```
</details>

---

### Question 27

**What is the purpose of cross-zone load balancing?**

A) Route traffic between different AWS regions
B) Distribute traffic evenly across all registered targets in all AZs
C) Balance traffic between VPCs
D) Route traffic to the closest geographic location

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Distribute traffic evenly across all registered targets in all AZs**

**Explanation:**

**Without Cross-Zone Load Balancing:**
```
           AZ-a (50%)              AZ-b (50%)
        ┌──────────────┐      ┌──────────────┐
        │  2 targets   │      │  8 targets   │
        │  (25% each)  │      │ (6.25% each) │
        └──────────────┘      └──────────────┘

        Uneven distribution per target!
```

**With Cross-Zone Load Balancing:**
```
           AZ-a                    AZ-b
        ┌──────────────┐      ┌──────────────┐
        │  2 targets   │      │  8 targets   │
        │  (10% each)  │      │ (10% each)   │
        └──────────────┘      └──────────────┘

        Even distribution across all 10 targets!
```

**Default Settings:**
- ALB: Enabled by default, free
- NLB: Disabled by default, charges for cross-AZ traffic
</details>

---

### Question 28

**A company is implementing SSL/TLS termination at the load balancer level. Which component stores the SSL certificate for ALB?**

A) IAM
B) AWS Certificate Manager (ACM)
C) Amazon S3
D) AWS Secrets Manager

<details>
<summary>Show Answer</summary>

**Correct Answer: B) AWS Certificate Manager (ACM)**

**Explanation:**
**AWS Certificate Manager (ACM)** provides:
- Free public SSL/TLS certificates
- Automatic renewal
- Integration with ALB, NLB, CloudFront, API Gateway

**Certificate Options for ELB:**
1. **ACM certificates** (recommended) - Free, auto-renewing
2. **IAM certificates** - Manual upload, for regions without ACM
3. **Third-party certificates** - Import to ACM

```bash
# Create HTTPS listener with ACM certificate
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/xxx \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN
```
</details>

---

## Section 6: Security and Architecture (Questions 29-30)

### Question 29

**A security team requires that EC2 instances in a private subnet can only receive traffic from an Application Load Balancer. How should the security group be configured?**

A) Allow all inbound traffic from 0.0.0.0/0
B) Allow inbound traffic from the ALB's public IP addresses
C) Allow inbound traffic from the ALB's security group
D) Allow inbound traffic from the VPC CIDR block

<details>
<summary>Show Answer</summary>

**Correct Answer: C) Allow inbound traffic from the ALB's security group**

**Explanation:**
**Security Group Best Practice:**
Reference the ALB security group as the source, not IP addresses.

```bash
# Instance security group rule
aws ec2 authorize-security-group-ingress \
    --group-id $INSTANCE_SG \
    --protocol tcp \
    --port 80 \
    --source-group $ALB_SG
```

**Why this is best:**
- ALB IP addresses can change
- Security group reference is dynamic
- Simplifies management
- Principle of least privilege

**Architecture:**
```
Internet → ALB (ALB-SG allows 0.0.0.0/0:443)
              │
              ▼
         Instances (Instance-SG allows ALB-SG:80)
```
</details>

---

### Question 30 (Scenario-Based)

**A company is designing a highly available web application with the following requirements:**
- Handle 100,000 concurrent users
- Survive failure of an entire Availability Zone
- Minimize costs while meeting performance needs
- Use Auto Scaling based on traffic patterns

**Which architecture BEST meets these requirements?**

A) Single large EC2 instance (x1e.32xlarge) with Elastic IP in one AZ

B) Application Load Balancer with Auto Scaling group across 2 AZs, using Reserved Instances for baseline and Spot Instances for peak capacity

C) Network Load Balancer with manually managed EC2 instances in 3 AZs

D) Multiple Classic Load Balancers, one per AZ, with On-Demand instances

<details>
<summary>Show Answer</summary>

**Correct Answer: B) Application Load Balancer with Auto Scaling group across 2 AZs, using Reserved Instances for baseline and Spot Instances for peak capacity**

**Explanation:**

| Requirement | How B Meets It |
|-------------|----------------|
| 100K concurrent users | ALB handles millions of requests; ASG scales horizontally |
| AZ failure survival | Multi-AZ deployment; if one AZ fails, others handle traffic |
| Cost minimization | Reserved for baseline (up to 72% savings), Spot for peaks (up to 90% savings) |
| Auto Scaling on traffic | ASG with target tracking automatically adjusts capacity |

**Why not others:**
- **A)** Single point of failure, no HA, no scaling
- **C)** NLB doesn't provide path-based routing; manual management doesn't scale
- **D)** CLB is legacy; multiple LBs add complexity and cost

**Recommended Architecture:**
```
                         ┌───────────────────┐
                         │        ALB        │
                         │    (Multi-AZ)     │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │        Auto Scaling         │
                    │  Min: 4 (Reserved)          │
                    │  Max: 20                    │
                    │  Mixed: Reserved + Spot     │
                    └─────────────┬───────────────┘
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
         ┌─────▼─────┐      ┌─────▼─────┐     ┌─────▼─────┐
         │   AZ-a    │      │   AZ-b    │     │   AZ-c    │
         │ EC2 (RI)  │      │ EC2 (RI)  │     │ EC2 (Spot)│
         │ EC2 (Spot)│      │ EC2 (Spot)│     │ EC2 (Spot)│
         └───────────┘      └───────────┘     └───────────┘
```
</details>

---

## Answer Key

| Question | Answer | Question | Answer |
|----------|--------|----------|--------|
| 1 | C | 16 | C |
| 2 | B | 17 | A, B, D |
| 3 | C | 18 | B |
| 4 | A, C, E, F | 19 | B |
| 5 | B | 20 | B |
| 6 | B | 21 | C |
| 7 | C | 22 | B |
| 8 | B | 23 | B |
| 9 | B, C | 24 | C |
| 10 | C | 25 | B |
| 11 | B | 26 | A, B, F |
| 12 | C | 27 | B |
| 13 | C | 28 | B |
| 14 | B | 29 | C |
| 15 | C | 30 | B |

---

## Score Interpretation

| Score | Level | Recommendation |
|-------|-------|----------------|
| 27-30 (90-100%) | Expert | Ready for advanced topics and certification |
| 24-26 (80-89%) | Proficient | Review missed topics, proceed to next module |
| 20-23 (67-79%) | Intermediate | Review relevant sections before proceeding |
| 15-19 (50-66%) | Developing | Complete hands-on labs, re-read materials |
| Below 15 (<50%) | Foundational | Review entire module, complete all exercises |

---

## Study Resources

### Topics to Review Based on Incorrect Answers

| Questions | Topic | Resource |
|-----------|-------|----------|
| 1-6 | Instance Types & Fundamentals | 01-ec2-fundamentals.md |
| 7-12 | Pricing Models | AWS Pricing Calculator |
| 13-18 | AMIs & Storage | 02-ami-and-marketplace.md, 04-storage-options.md |
| 19-23 | Auto Scaling | 08-auto-scaling.md |
| 24-28 | Load Balancing | 09-load-balancing.md |
| 29-30 | Architecture & Security | 05-security-groups.md |

### Additional Practice

1. Complete all hands-on labs in 10-hands-on-lab.md
2. Use AWS Free Tier to practice
3. Review AWS documentation for updates
4. Take AWS practice exams for certification preparation

---

**Quiz Version**: 1.0
**Last Updated**: January 2025
**Total Questions**: 30
**Estimated Time**: 45 minutes
