# Module 08 Quiz: CloudWatch and Monitoring

## Instructions

- Total Questions: 30
- Time Limit: 45 minutes
- Passing Score: 80% (24/30)
- Question Types: Multiple Choice, Multiple Select, Scenario-Based

---

## Section 1: CloudWatch Metrics and Dimensions

### Question 1

What is the maximum number of dimensions allowed per metric in CloudWatch?

A) 10
B) 20
C) 30
D) 40

<details>
<summary>Answer</summary>

**C) 30**

Explanation: CloudWatch allows up to 30 dimensions per metric. Dimensions are name/value pairs that uniquely identify a metric. Common examples include InstanceId for EC2, FunctionName for Lambda, and QueueName for SQS.
</details>

---

### Question 2

Which of the following are valid CloudWatch metric statistics? (Select THREE)

A) Average
B) Median
C) Sum
D) p99
E) Mode

<details>
<summary>Answer</summary>

**A) Average, C) Sum, D) p99**

Explanation: CloudWatch supports Average, Sum, Minimum, Maximum, SampleCount, and percentile statistics (p0.0 to p100, like p99, p95, p50). Median and Mode are not directly supported - you would use p50 for median.
</details>

---

### Question 3

A DevOps engineer needs to monitor memory utilization on EC2 instances. Which statement is correct?

A) Memory metrics are automatically published by EC2 to CloudWatch
B) Memory metrics require the CloudWatch Agent or custom metric publishing
C) Memory metrics are only available with Enhanced Monitoring
D) Memory utilization cannot be monitored in CloudWatch

<details>
<summary>Answer</summary>

**B) Memory metrics require the CloudWatch Agent or custom metric publishing**

Explanation: EC2 basic monitoring only includes CPU, disk, network, and status check metrics. Memory and disk space utilization require the CloudWatch Agent or custom metrics. Enhanced Monitoring is an RDS feature, not EC2.
</details>

---

### Question 4

What is the default metric resolution for AWS services publishing to CloudWatch?

A) 10 seconds
B) 30 seconds
C) 1 minute
D) 5 minutes

<details>
<summary>Answer</summary>

**D) 5 minutes** (for most services like EC2 basic monitoring)

Explanation: Most AWS services publish metrics at 5-minute intervals by default. Detailed monitoring (1-minute) is available for some services. High-resolution metrics (down to 1 second) are available for custom metrics.
</details>

---

### Question 5

You want to calculate the total number of requests across all your Lambda functions using CloudWatch metric math. Which expression would you use?

A) `SUM(METRICS("Invocations"))`
B) `SUM(SEARCH('{AWS/Lambda,FunctionName} MetricName="Invocations"', 'Sum'))`
C) `AGGREGATE(Lambda.Invocations)`
D) `TOTAL(AWS/Lambda/Invocations)`

<details>
<summary>Answer</summary>

**B) `SUM(SEARCH('{AWS/Lambda,FunctionName} MetricName="Invocations"', 'Sum'))`**

Explanation: The SEARCH function finds all metrics matching the pattern, and SUM aggregates them. This metric math expression searches for all Lambda Invocations metrics and sums them together.
</details>

---

## Section 2: CloudWatch Alarms

### Question 6

What are the three possible states of a CloudWatch alarm?

A) OK, WARNING, CRITICAL
B) OK, ALARM, INSUFFICIENT_DATA
C) HEALTHY, UNHEALTHY, PENDING
D) NORMAL, ALERT, UNKNOWN

<details>
<summary>Answer</summary>

**B) OK, ALARM, INSUFFICIENT_DATA**

Explanation: CloudWatch alarms have exactly three states: OK (metric is within threshold), ALARM (metric has breached threshold), and INSUFFICIENT_DATA (not enough data points to determine state).
</details>

---

### Question 7

An alarm is configured with:
- Period: 300 seconds
- Evaluation Periods: 3
- Datapoints to Alarm: 2

How many consecutive 5-minute periods must have breaching data points for the alarm to trigger?

A) 2 out of 2 periods
B) 2 out of 3 periods
C) 3 out of 3 periods
D) 3 out of 5 periods

<details>
<summary>Answer</summary>

**B) 2 out of 3 periods**

Explanation: The alarm evaluates 3 consecutive periods (Evaluation Periods = 3), and triggers if 2 or more of those periods are breaching (Datapoints to Alarm = 2). This "M out of N" configuration helps reduce false alarms from transient spikes.
</details>

---

### Question 8

Which alarm type uses machine learning to automatically adjust thresholds based on historical patterns?

A) Static Threshold Alarm
B) Composite Alarm
C) Anomaly Detection Alarm
D) Metric Math Alarm

<details>
<summary>Answer</summary>

**C) Anomaly Detection Alarm**

Explanation: Anomaly Detection Alarms use machine learning to analyze metric history and create a band of expected values. The alarm triggers when the metric goes outside this dynamic threshold band.
</details>

---

### Question 9

What is the purpose of a Composite Alarm?

A) To monitor multiple AWS regions simultaneously
B) To combine multiple alarms using boolean logic
C) To create alarms with multiple thresholds
D) To aggregate alarms from multiple accounts

<details>
<summary>Answer</summary>

**B) To combine multiple alarms using boolean logic**

Explanation: Composite Alarms allow you to combine multiple child alarms using AND, OR, and NOT operators. They reduce alarm noise by triggering only when specific combinations of conditions are met.
</details>

---

### Question 10

Which actions can be triggered directly by a CloudWatch Alarm? (Select THREE)

A) Send notification to SNS topic
B) Execute a Lambda function directly
C) Stop/Terminate an EC2 instance
D) Trigger Auto Scaling policy
E) Create a CloudFormation stack

<details>
<summary>Answer</summary>

**A) Send notification to SNS topic, C) Stop/Terminate an EC2 instance, D) Trigger Auto Scaling policy**

Explanation: CloudWatch Alarms can directly: 1) Send to SNS, 2) Perform EC2 actions (stop, terminate, reboot, recover), and 3) Trigger Auto Scaling policies. Lambda functions are triggered indirectly via SNS subscription, not directly from the alarm.
</details>

---

## Section 3: CloudWatch Logs and Insights

### Question 11

What is the correct hierarchy in CloudWatch Logs?

A) Log Event > Log Stream > Log Group
B) Log Group > Log Event > Log Stream
C) Log Group > Log Stream > Log Event
D) Log Stream > Log Group > Log Event

<details>
<summary>Answer</summary>

**C) Log Group > Log Stream > Log Event**

Explanation: Log Groups contain Log Streams, which contain Log Events. A Log Group typically represents an application or service, Log Streams represent individual sources (like EC2 instances), and Log Events are individual log entries.
</details>

---

### Question 12

Which CloudWatch Logs Insights query finds all ERROR messages in the last hour?

A) `SELECT * FROM logs WHERE message LIKE '%ERROR%'`
B) `fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc`
C) `SEARCH logs FOR "ERROR" ORDER BY timestamp DESC`
D) `query logs where @message contains "ERROR"`

<details>
<summary>Answer</summary>

**B) `fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc`**

Explanation: CloudWatch Logs Insights uses its own query syntax with commands like `fields`, `filter`, `stats`, `sort`, and `limit`. The pipe (|) character chains commands together.
</details>

---

### Question 13

A Lambda function is experiencing cold starts. Which Logs Insights query identifies cold start occurrences?

A) `filter @message like /COLD/`
B) `filter @type = "REPORT" | parse @message "Init Duration: * ms" as initDuration | filter ispresent(initDuration)`
C) `stats count(*) by coldStart = true`
D) `filter @message like /START/ and @message like /INIT/`

<details>
<summary>Answer</summary>

**B) `filter @type = "REPORT" | parse @message "Init Duration: * ms" as initDuration | filter ispresent(initDuration)`**

Explanation: Lambda REPORT lines only include "Init Duration" when a cold start occurs. By filtering for REPORT type logs and checking if Init Duration is present, you identify cold starts.
</details>

---

### Question 14

You need to extract the user ID from log messages formatted as "Processing request for user: USER123". Which Logs Insights command would you use?

A) `extract @message "user: *" as userId`
B) `parse @message "Processing request for user: *" as userId`
C) `regex @message /user: (\w+)/ as userId`
D) `split @message "user: " as userId`

<details>
<summary>Answer</summary>

**B) `parse @message "Processing request for user: *" as userId`**

Explanation: The `parse` command extracts values from log messages using patterns. The asterisk (*) acts as a wildcard that captures the value into the specified variable.
</details>

---

### Question 15

What is the purpose of a Metric Filter in CloudWatch Logs?

A) To remove unwanted log entries
B) To route logs to specific destinations
C) To extract metric values from log data
D) To compress log files for storage

<details>
<summary>Answer</summary>

**C) To extract metric values from log data**

Explanation: Metric Filters scan incoming log data for specific patterns and create CloudWatch metrics from the matches. For example, you can count ERROR occurrences or extract numeric values from log messages.
</details>

---

## Section 4: AWS X-Ray

### Question 16

What is the primary purpose of AWS X-Ray?

A) To monitor CloudWatch metrics across regions
B) To provide distributed tracing for applications
C) To aggregate logs from multiple services
D) To detect security anomalies

<details>
<summary>Answer</summary>

**B) To provide distributed tracing for applications**

Explanation: AWS X-Ray helps developers analyze and debug distributed applications by providing end-to-end request tracing. It shows how requests flow through your application and identifies performance bottlenecks.
</details>

---

### Question 17

What is the difference between X-Ray annotations and metadata?

A) Annotations are encrypted, metadata is not
B) Annotations are indexed for search, metadata is not
C) Annotations are for errors only, metadata is for all data
D) There is no difference

<details>
<summary>Answer</summary>

**B) Annotations are indexed for search, metadata is not**

Explanation: Annotations are key-value pairs that are indexed and can be used to filter traces (e.g., find all traces for customer_id="123"). Metadata stores additional information but is not indexed for searching.
</details>

---

### Question 18

In X-Ray, what is a segment?

A) A portion of the service map
B) Work done by a service for a request
C) A collection of related traces
D) A time bucket for aggregation

<details>
<summary>Answer</summary>

**B) Work done by a service for a request**

Explanation: A segment represents the work done by a single service or component for a request. Subsegments provide finer granularity within a segment, typically for downstream calls to other services or databases.
</details>

---

### Question 19

What controls the percentage of requests that X-Ray traces?

A) Trace filters
B) Segment rules
C) Sampling rules
D) Quota limits

<details>
<summary>Answer</summary>

**C) Sampling rules**

Explanation: Sampling rules control what percentage of requests are traced. They include a reservoir size (fixed number of requests per second) and a fixed rate (percentage of additional requests to trace).
</details>

---

## Section 5: CloudTrail

### Question 20

What is the difference between CloudTrail Management Events and Data Events?

A) Management events are free, data events are paid
B) Management events track API calls to AWS services, data events track operations on resources within services
C) Management events are real-time, data events are batched
D) Management events are for console access, data events are for CLI access

<details>
<summary>Answer</summary>

**B) Management events track API calls to AWS services, data events track operations on resources within services**

Explanation: Management events capture control plane operations (CreateBucket, StartInstances, CreateUser). Data events capture data plane operations (S3 GetObject/PutObject, Lambda Invoke). Data events generate high volume and cost more.
</details>

---

### Question 21

How can you verify that CloudTrail log files have not been tampered with?

A) Enable encryption with KMS
B) Enable Log File Integrity Validation
C) Use CloudTrail Insights
D) Enable multi-region logging

<details>
<summary>Answer</summary>

**B) Enable Log File Integrity Validation**

Explanation: Log File Integrity Validation creates a digest file with hashes of log files. You can use the AWS CLI to validate that log files haven't been modified or deleted since CloudTrail delivered them.
</details>

---

### Question 22

A security team needs real-time alerts when the root user signs in. What should they configure?

A) CloudTrail with CloudWatch Logs integration and a metric filter
B) CloudTrail Insights
C) AWS Config rule
D) GuardDuty finding

<details>
<summary>Answer</summary>

**A) CloudTrail with CloudWatch Logs integration and a metric filter**

Explanation: By sending CloudTrail logs to CloudWatch Logs, you can create metric filters to detect specific events (like ConsoleLogin by root user) and trigger CloudWatch Alarms for real-time notification.
</details>

---

## Section 6: EventBridge (CloudWatch Events)

### Question 23

Which statement best describes Amazon EventBridge?

A) A log aggregation service
B) A serverless event bus for routing events
C) A metric visualization tool
D) A tracing service for microservices

<details>
<summary>Answer</summary>

**B) A serverless event bus for routing events**

Explanation: EventBridge (formerly CloudWatch Events) is a serverless event bus that receives events from AWS services, SaaS applications, and custom applications, then routes them to targets based on rules.
</details>

---

### Question 24

Which EventBridge feature allows you to capture events that failed to be delivered to a target?

A) Event replay
B) Dead-letter queue
C) Event archive
D) Retry policy

<details>
<summary>Answer</summary>

**B) Dead-letter queue**

Explanation: Dead-letter queues (SQS) capture events that could not be successfully delivered to a target after all retry attempts. This enables you to investigate and reprocess failed events.
</details>

---

### Question 25

An EventBridge rule needs to trigger a Lambda function every 5 minutes. Which schedule expression is correct?

A) `rate(5 minutes)`
B) `cron(*/5 * * * *)`
C) `interval(5m)`
D) `schedule(every 5 minutes)`

<details>
<summary>Answer</summary>

**A) `rate(5 minutes)`**

Explanation: EventBridge supports rate expressions (`rate(5 minutes)`) and cron expressions (`cron(0/5 * * * ? *)`). The rate expression is simpler for fixed intervals. Note: cron uses 6 fields in EventBridge.
</details>

---

## Section 7: AWS Config

### Question 26

What is the primary purpose of AWS Config?

A) To optimize AWS resource costs
B) To track resource configuration changes and compliance
C) To monitor application performance
D) To encrypt data at rest

<details>
<summary>Answer</summary>

**B) To track resource configuration changes and compliance**

Explanation: AWS Config records configuration changes to AWS resources over time, evaluates resources against rules for compliance, and provides a configuration history for troubleshooting and auditing.
</details>

---

### Question 27

Which AWS Config feature groups multiple rules that work together for a compliance framework?

A) Config aggregators
B) Conformance packs
C) Rule bundles
D) Compliance groups

<details>
<summary>Answer</summary>

**B) Conformance packs**

Explanation: Conformance packs are collections of Config rules and remediation actions that you can deploy as a single entity. They're useful for implementing compliance frameworks like PCI-DSS, HIPAA, or custom standards.
</details>

---

### Question 28

An AWS Config rule detects an S3 bucket without encryption. What feature automatically enables encryption?

A) Auto-correction
B) Remediation action
C) Compliance fix
D) Config enforcement

<details>
<summary>Answer</summary>

**B) Remediation action**

Explanation: Remediation actions use Systems Manager Automation documents to automatically fix non-compliant resources. You can configure manual or automatic remediation for each Config rule.
</details>

---

## Section 8: SNS and Alerting

### Question 29

Which SNS subscription protocols are supported for CloudWatch Alarm notifications? (Select THREE)

A) Email
B) SMS
C) HTTP/HTTPS
D) FTP
E) Lambda

<details>
<summary>Answer</summary>

**A) Email, B) SMS, C) HTTP/HTTPS, E) Lambda**

Explanation: SNS supports multiple protocols: Email, Email-JSON, SMS, HTTP/HTTPS, Lambda, SQS, and platform applications (mobile push). FTP is not a supported protocol.
</details>

---

### Question 30

What is the purpose of SNS message filtering?

A) To remove sensitive data from messages
B) To route messages to specific subscribers based on attributes
C) To compress messages for faster delivery
D) To encrypt messages in transit

<details>
<summary>Answer</summary>

**B) To route messages to specific subscribers based on attributes**

Explanation: SNS message filtering allows subscribers to receive only messages that match a filter policy based on message attributes. This reduces unnecessary message processing and costs.
</details>

---

## Scenario-Based Questions

### Question 31 (Bonus)

A company runs a three-tier web application (web servers, application servers, database) on AWS. They need to:
- Monitor custom business metrics (orders per minute)
- Alert when error rate exceeds 5%
- Trace requests end-to-end
- Track all configuration changes
- Store logs for 90 days

Which combination of services should they use?

A) CloudWatch Metrics, CloudWatch Alarms, X-Ray, CloudTrail, CloudWatch Logs
B) CloudWatch Metrics, CloudWatch Alarms, X-Ray, AWS Config, CloudWatch Logs
C) CloudWatch Metrics, SNS, X-Ray, AWS Config, S3
D) CloudWatch Dashboards, CloudWatch Events, VPC Flow Logs, AWS Config, S3

<details>
<summary>Answer</summary>

**B) CloudWatch Metrics, CloudWatch Alarms, X-Ray, AWS Config, CloudWatch Logs**

Explanation:
- CloudWatch Metrics: Custom business metrics
- CloudWatch Alarms: Error rate alerting
- X-Ray: End-to-end request tracing
- AWS Config: Configuration change tracking
- CloudWatch Logs: 90-day log retention

CloudTrail tracks API calls, not configuration state. SNS alone doesn't provide alerting logic.
</details>

---

### Question 32 (Bonus)

A Lambda function processing SQS messages is timing out intermittently. Which combination of tools would best help diagnose the issue?

A) CloudWatch Metrics only
B) CloudWatch Logs only
C) X-Ray traces and CloudWatch Logs Insights
D) AWS Config and CloudTrail

<details>
<summary>Answer</summary>

**C) X-Ray traces and CloudWatch Logs Insights**

Explanation: X-Ray traces show where time is being spent in each request (downstream calls, initialization). CloudWatch Logs Insights can analyze Lambda logs to find patterns in timeouts, cold starts, and error messages. This combination provides both tracing and log analysis capabilities.
</details>

---

## Scoring Guide

| Score | Grade | Status |
|-------|-------|--------|
| 28-32 | A | Excellent - Ready for production monitoring |
| 24-27 | B | Good - Review specific areas |
| 20-23 | C | Fair - Additional study recommended |
| Below 20 | D | Needs Improvement - Review module content |

---

## Key Concepts Summary

### CloudWatch Metrics
- Namespaces organize metrics by service
- Dimensions uniquely identify metrics
- Standard resolution: 1-minute minimum
- High resolution: 1-second minimum

### CloudWatch Alarms
- Three states: OK, ALARM, INSUFFICIENT_DATA
- Static, Anomaly Detection, and Composite types
- Actions: SNS, EC2, Auto Scaling

### CloudWatch Logs
- Log Groups > Log Streams > Log Events
- Metric Filters extract metrics from logs
- Logs Insights for querying and analysis

### X-Ray
- Traces > Segments > Subsegments
- Annotations (indexed) vs Metadata (not indexed)
- Sampling rules control trace volume

### CloudTrail
- Management events: Control plane operations
- Data events: Data plane operations (high volume)
- Log file integrity validation

### AWS Config
- Resource configuration tracking
- Managed and custom rules
- Conformance packs for compliance frameworks
- Automatic remediation

### EventBridge
- Serverless event bus
- Rules with patterns or schedules
- Multiple targets per rule

---

*Module 08 Quiz - AWS Solutions Architect Training Course*
