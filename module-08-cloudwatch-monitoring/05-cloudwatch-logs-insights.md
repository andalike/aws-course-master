# CloudWatch Logs Insights

## Introduction

CloudWatch Logs Insights is an interactive, pay-per-query service for analyzing log data. It uses a purpose-built query language to search and analyze logs at scale, providing visualizations and the ability to save queries for reuse.

---

## Query Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CloudWatch Logs Insights Query                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Log Groups: [/aws/lambda/my-function ▼] [+ Add log groups]              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Time Range: [Last 1 hour ▼]  Custom: [From] [To]                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Query:                                                                   ││
│  │ ┌─────────────────────────────────────────────────────────────────────┐ ││
│  │ │ fields @timestamp, @message                                         │ ││
│  │ │ | filter @message like /ERROR/                                      │ ││
│  │ │ | sort @timestamp desc                                              │ ││
│  │ │ | limit 100                                                         │ ││
│  │ └─────────────────────────────────────────────────────────────────────┘ ││
│  │                                                                          ││
│  │ [Run query]  [Save]  [Actions ▼]                                        ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Results (1,234 records matched):                                        ││
│  │ ┌─────────────┬─────────────────────────────────────────────────────┐  ││
│  │ │ @timestamp  │ @message                                             │  ││
│  │ ├─────────────┼─────────────────────────────────────────────────────┤  ││
│  │ │ 10:30:45    │ ERROR: Connection timeout to database               │  ││
│  │ │ 10:30:42    │ ERROR: Failed to process request id=abc123          │  ││
│  │ │ 10:30:38    │ ERROR: Invalid input parameter                      │  ││
│  │ └─────────────┴─────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Query Syntax Overview

### Query Structure

```sql
-- Basic structure
fields field1, field2, field3
| filter condition
| stats aggregation by groupField
| sort field order
| limit count
```

### Available Commands

| Command | Purpose |
|---------|---------|
| `fields` | Select specific fields to display |
| `filter` | Filter log events by condition |
| `stats` | Calculate aggregate statistics |
| `sort` | Order results |
| `limit` | Limit number of results |
| `parse` | Extract data using patterns |
| `display` | Modify visualization |

---

## Automatically Discovered Fields

CloudWatch Logs Insights automatically discovers fields in your logs:

### System Fields

| Field | Description |
|-------|-------------|
| `@timestamp` | Event timestamp |
| `@message` | Raw log message |
| `@logStream` | Log stream name |
| `@log` | Log group identifier |
| `@ingestionTime` | When log was ingested |

### JSON Fields

For JSON-formatted logs, fields are automatically extracted:

```json
{"level": "INFO", "message": "Request processed", "userId": "123", "responseTime": 250}
```

Discovered fields: `level`, `message`, `userId`, `responseTime`

---

## Field Selection

### Basic Field Selection

```sql
-- Select specific fields
fields @timestamp, @message

-- Select JSON fields
fields @timestamp, level, message, userId

-- Select with alias
fields @timestamp as time, level as logLevel, message as msg

-- Select all fields
fields *
```

---

## Filtering

### Comparison Operators

```sql
-- Equals
filter level = "ERROR"

-- Not equals
filter level != "DEBUG"

-- Greater/Less than
filter responseTime > 1000
filter statusCode >= 400

-- Contains (string)
filter @message like /ERROR/

-- Not contains
filter @message not like /DEBUG/

-- Regular expression
filter @message like /user-\d+/

-- Case insensitive
filter @message like /(?i)error/

-- In list
filter level in ["ERROR", "WARN", "CRITICAL"]

-- Exists
filter ispresent(userId)

-- Not exists
filter not ispresent(errorCode)
```

### Logical Operators

```sql
-- AND
filter level = "ERROR" and responseTime > 1000

-- OR
filter level = "ERROR" or level = "CRITICAL"

-- NOT
filter not (level = "DEBUG")

-- Complex conditions
filter (level = "ERROR" or level = "WARN") and responseTime > 500
```

---

## Parse Command

### Pattern Matching

```sql
-- Basic parse
parse @message "user * performed * action" as userId, actionType

-- Parse with prefix/suffix
parse @message "RequestId: * Duration: * ms" as requestId, duration

-- Parse JSON manually (rarely needed)
parse @message '{"userId": "*", "action": "*"}' as userId, action
```

### Regular Expression Parse

```sql
-- Regex parse
parse @message /user=(?<userId>\w+)/

-- Multiple captures
parse @message /method=(?<method>\w+) path=(?<path>[^\s]+) status=(?<status>\d+)/

-- Extract IP address
parse @message /(?<ip>\d+\.\d+\.\d+\.\d+)/
```

### Parse Common Log Formats

```sql
-- Apache/Nginx access log
parse @message '* - - [*] "* * *" * *' as ip, timestamp, method, path, protocol, status, size

-- Application log with timestamp
parse @message '[*] [*] *' as timestamp, level, message
```

---

## Statistics

### Aggregation Functions

| Function | Description |
|----------|-------------|
| `count()` | Count of events |
| `count_distinct(field)` | Unique values |
| `sum(field)` | Total sum |
| `avg(field)` | Average value |
| `min(field)` | Minimum value |
| `max(field)` | Maximum value |
| `stddev(field)` | Standard deviation |
| `percentile(field, p)` | Percentile value |
| `earliest(field)` | First chronological value |
| `latest(field)` | Last chronological value |

### Basic Aggregations

```sql
-- Count all events
stats count(*) as totalEvents

-- Count by field
stats count(*) by level

-- Multiple aggregations
stats count(*) as total, avg(responseTime) as avgLatency, max(responseTime) as maxLatency

-- Count distinct
stats count_distinct(userId) as uniqueUsers
```

### Time-Based Aggregations

```sql
-- Count per time bucket
stats count(*) by bin(5m)

-- Stats per hour
stats avg(responseTime) as avgLatency by bin(1h)

-- Combined grouping
stats count(*) by level, bin(15m)
```

### Percentile Calculations

```sql
-- Response time percentiles
stats
    percentile(responseTime, 50) as p50,
    percentile(responseTime, 90) as p90,
    percentile(responseTime, 95) as p95,
    percentile(responseTime, 99) as p99
by bin(5m)

-- With additional context
stats
    count(*) as requests,
    avg(responseTime) as avgLatency,
    percentile(responseTime, 99) as p99Latency
by endpoint
| sort p99Latency desc
```

---

## Sorting and Limiting

### Sort

```sql
-- Sort descending
sort @timestamp desc

-- Sort ascending
sort responseTime asc

-- Multiple sort fields
sort level asc, @timestamp desc

-- Sort by aggregated value
stats count(*) as errorCount by level
| sort errorCount desc
```

### Limit

```sql
-- Limit results
limit 100

-- Top N pattern
stats count(*) as count by userId
| sort count desc
| limit 10
```

---

## String Functions

| Function | Description | Example |
|----------|-------------|---------|
| `strlen(s)` | String length | `strlen(@message)` |
| `substr(s, start, len)` | Substring | `substr(@message, 0, 50)` |
| `trim(s)` | Remove whitespace | `trim(@message)` |
| `ltrim(s)` | Left trim | `ltrim(@message)` |
| `rtrim(s)` | Right trim | `rtrim(@message)` |
| `replace(s, old, new)` | Replace text | `replace(@message, "ERROR", "ERR")` |
| `tolower(s)` | Lowercase | `tolower(level)` |
| `toupper(s)` | Uppercase | `toupper(level)` |
| `concat(s1, s2)` | Concatenate | `concat(firstName, lastName)` |

---

## Numeric Functions

| Function | Description |
|----------|-------------|
| `abs(n)` | Absolute value |
| `ceil(n)` | Round up |
| `floor(n)` | Round down |
| `sqrt(n)` | Square root |
| `log(n)` | Natural logarithm |
| `log10(n)` | Base-10 logarithm |
| `pow(base, exp)` | Power |

---

## Date/Time Functions

| Function | Description |
|----------|-------------|
| `datefloor(ts, period)` | Round down to period |
| `dateceil(ts, period)` | Round up to period |
| `fromMillis(ms)` | Convert milliseconds to timestamp |
| `toMillis(ts)` | Convert timestamp to milliseconds |
| `bin(period)` | Group by time bucket |

```sql
-- Time bucket examples
stats count(*) by bin(1m)   -- Per minute
stats count(*) by bin(5m)   -- Per 5 minutes
stats count(*) by bin(1h)   -- Per hour
stats count(*) by bin(1d)   -- Per day
```

---

## IP Functions

```sql
-- Check if IP is in CIDR range
filter isIpInSubnet(clientIp, "10.0.0.0/8")

-- Check private IPs
filter isIpInSubnet(srcIp, "192.168.0.0/16") or
      isIpInSubnet(srcIp, "10.0.0.0/8") or
      isIpInSubnet(srcIp, "172.16.0.0/12")
```

---

## Visualization Types

### Automatic Visualization

Based on query structure, Logs Insights suggests visualizations:

| Query Type | Visualization |
|------------|---------------|
| `stats ... by bin()` | Line chart |
| `stats ... by field` | Bar chart |
| `fields without stats` | Table |
| `stats with multiple metrics` | Multi-line chart |

### Example Visualization Queries

```sql
-- Line chart: Events over time
stats count(*) by bin(5m)

-- Stacked area: Events by level over time
stats count(*) by level, bin(5m)

-- Bar chart: Top endpoints
stats count(*) as requests by endpoint
| sort requests desc
| limit 10

-- Pie chart: Distribution by status
stats count(*) by statusCode
```

---

## Saved Queries

### Saving Queries

Queries can be saved for reuse:

1. Run your query
2. Click "Save"
3. Provide name and description
4. Choose log groups (optional)

### Query Categories

Organize saved queries by category:
- Error Investigation
- Performance Analysis
- Security Audit
- Cost Analysis
- Daily Operations

---

## Multi-Log Group Queries

### Querying Multiple Log Groups

```sql
-- Select multiple log groups in the UI
-- The query runs across all selected groups

fields @log, @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

### Cross-Account Queries

With proper cross-account access:
```sql
fields @log, @timestamp, @message
| filter @message like /CRITICAL/
| stats count(*) by @log
```

---

## Sample Queries by Use Case

### Error Analysis

```sql
-- Find all errors
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Error distribution by type
filter @message like /ERROR/
| parse @message "ERROR: *" as errorType
| stats count(*) as count by errorType
| sort count desc

-- Errors with context (surrounding logs)
fields @timestamp, @message, @logStream
| filter @message like /ERROR/ or @message like /Exception/
| sort @timestamp desc
| limit 200
```

### Performance Analysis

```sql
-- Slow requests
fields @timestamp, @message, responseTime
| filter responseTime > 1000
| sort responseTime desc
| limit 50

-- Latency percentiles over time
stats
    percentile(responseTime, 50) as p50,
    percentile(responseTime, 95) as p95,
    percentile(responseTime, 99) as p99
by bin(5m)

-- Slowest endpoints
stats
    avg(responseTime) as avgLatency,
    max(responseTime) as maxLatency,
    count(*) as requests
by endpoint
| sort avgLatency desc
| limit 10
```

### Lambda Analysis

```sql
-- Cold starts
filter @type = "REPORT"
| parse @message "Init Duration: * ms" as initDuration
| filter ispresent(initDuration)
| stats count(*) as coldStarts, avg(initDuration) as avgInitDuration by bin(1h)

-- Lambda duration analysis
filter @type = "REPORT"
| parse @message "Duration: * ms" as duration
| parse @message "Billed Duration: * ms" as billedDuration
| parse @message "Memory Size: * MB" as memorySize
| parse @message "Max Memory Used: * MB" as memoryUsed
| stats
    avg(duration) as avgDuration,
    max(duration) as maxDuration,
    avg(memoryUsed/memorySize*100) as avgMemoryUtilization
by bin(1h)

-- Lambda errors
filter @message like /ERROR/ or @message like /Task timed out/
| stats count(*) by bin(5m)
```

### VPC Flow Logs Analysis

```sql
-- Rejected traffic
filter action = "REJECT"
| stats count(*) as rejectedCount by srcAddr, dstAddr, dstPort
| sort rejectedCount desc
| limit 20

-- Top talkers
stats sum(bytes) as totalBytes by srcAddr
| sort totalBytes desc
| limit 10

-- Traffic by protocol
stats count(*) as connections, sum(bytes) as totalBytes by protocol
| sort totalBytes desc
```

### CloudTrail Analysis

```sql
-- Failed API calls
filter errorCode like /./
| stats count(*) by eventSource, eventName, errorCode
| sort count desc

-- Root user activity
filter userIdentity.type = "Root"
| fields @timestamp, eventName, sourceIPAddress
| sort @timestamp desc

-- Console logins
filter eventName = "ConsoleLogin"
| fields @timestamp, userIdentity.arn, sourceIPAddress, responseElements.ConsoleLogin
| sort @timestamp desc
```

---

## Using AWS CLI

### Run Query

```bash
# Start query
QUERY_ID=$(aws logs start-query \
    --log-group-name /aws/lambda/my-function \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | limit 100' \
    --query 'queryId' \
    --output text)

echo "Query ID: $QUERY_ID"

# Wait for results
aws logs get-query-results --query-id $QUERY_ID
```

### Check Query Status

```bash
# Get query results (may need to poll)
aws logs get-query-results --query-id $QUERY_ID

# Status values: Scheduled, Running, Complete, Failed, Cancelled
```

### Script for Complete Query

```bash
#!/bin/bash

LOG_GROUP="/aws/lambda/my-function"
QUERY='fields @timestamp, @message | filter @message like /ERROR/ | limit 100'
START_TIME=$(date -d '1 hour ago' +%s)
END_TIME=$(date +%s)

# Start query
QUERY_ID=$(aws logs start-query \
    --log-group-name "$LOG_GROUP" \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --query-string "$QUERY" \
    --query 'queryId' \
    --output text)

echo "Started query: $QUERY_ID"

# Poll for results
while true; do
    RESULT=$(aws logs get-query-results --query-id $QUERY_ID)
    STATUS=$(echo $RESULT | jq -r '.status')

    if [ "$STATUS" = "Complete" ] || [ "$STATUS" = "Failed" ]; then
        echo "Query status: $STATUS"
        echo "$RESULT" | jq '.results'
        break
    fi

    echo "Query status: $STATUS, waiting..."
    sleep 1
done
```

---

## Pricing

| Component | Cost |
|-----------|------|
| Data scanned | $0.005 per GB |

### Cost Optimization Tips

1. **Narrow time range** - Query only necessary time periods
2. **Filter early** - Use filters before stats
3. **Select specific fields** - Don't use `fields *` unnecessarily
4. **Use saved queries** - Avoid re-scanning for same data
5. **Sample for exploration** - Use `limit` during development

---

## Limits

| Resource | Limit |
|----------|-------|
| Concurrent queries | 30 per account per region |
| Query timeout | 60 minutes |
| Results per query | 10,000 log events |
| Log groups per query | 50 |
| Query history | 24 hours |

---

## Best Practices

### Query Optimization

```sql
-- Good: Filter early
fields @timestamp, @message
| filter level = "ERROR"
| filter responseTime > 1000
| limit 100

-- Bad: Process everything then filter
fields @timestamp, @message, level, responseTime
| limit 10000
| filter level = "ERROR"
```

### Structured Logging Benefits

```sql
-- With structured (JSON) logs, queries are more precise
filter level = "ERROR" and service = "payment-api" and environment = "production"
| stats count(*) by errorType
| sort count desc

-- Compared to unstructured logs
filter @message like /ERROR/ and @message like /payment/ and @message like /production/
| parse @message "type=*" as errorType
| stats count(*) by errorType
```

---

## Next Steps

Continue to the next sections:
- [06-cloudwatch-dashboards.md](06-cloudwatch-dashboards.md) - Visualize query results
- [query-examples.md](query-examples.md) - 20 practical query examples
