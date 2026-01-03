# CloudWatch Agent

## Introduction

The CloudWatch Agent is a unified agent that collects both system-level metrics and logs from EC2 instances and on-premises servers. It enables you to collect metrics that are not available by default, such as memory utilization and disk space, and stream application logs to CloudWatch Logs.

---

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EC2 Instance / On-Premises Server                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        CloudWatch Agent                               │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │                                                                       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │  Metrics        │  │  Logs           │  │  StatsD/        │      │   │
│  │  │  Collector      │  │  Collector      │  │  collectd       │      │   │
│  │  │                 │  │                 │  │                 │      │   │
│  │  │  - CPU          │  │  - Syslog       │  │  - Custom       │      │   │
│  │  │  - Memory       │  │  - Application  │  │    metrics      │      │   │
│  │  │  - Disk         │  │  - Windows      │  │                 │      │   │
│  │  │  - Network      │  │    Events       │  │                 │      │   │
│  │  │  - Processes    │  │                 │  │                 │      │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │   │
│  │           │                    │                    │               │   │
│  │           └────────────────────┼────────────────────┘               │   │
│  │                                │                                     │   │
│  │                    ┌───────────▼───────────┐                        │   │
│  │                    │    Configuration      │                        │   │
│  │                    │    (JSON file or      │                        │   │
│  │                    │     SSM Parameter)    │                        │   │
│  │                    └───────────┬───────────┘                        │   │
│  │                                │                                     │   │
│  └────────────────────────────────┼─────────────────────────────────────┘   │
│                                   │                                          │
└───────────────────────────────────┼──────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │        Amazon CloudWatch       │
                    │                                │
                    │  ┌──────────┐  ┌──────────┐   │
                    │  │ Metrics  │  │  Logs    │   │
                    │  └──────────┘  └──────────┘   │
                    │                                │
                    └───────────────────────────────┘
```

---

## Why Use CloudWatch Agent?

### Default EC2 Metrics (Without Agent)

| Metric | Available |
|--------|-----------|
| CPUUtilization | Yes |
| NetworkIn/Out | Yes |
| DiskReadBytes/WriteBytes | Yes |
| StatusCheckFailed | Yes |
| **Memory Utilization** | **No** |
| **Disk Space Used** | **No** |
| **Swap Usage** | **No** |
| **Process Count** | **No** |

### Additional Metrics (With Agent)

| Metric | Enabled By Agent |
|--------|------------------|
| mem_used_percent | Yes |
| disk_used_percent | Yes |
| swap_used_percent | Yes |
| processes | Yes |
| netstat | Yes |
| Custom application metrics | Yes |

---

## Installation

### Amazon Linux 2 / RHEL / CentOS

```bash
# Download agent
sudo yum install -y amazon-cloudwatch-agent

# Or using SSM
sudo yum install -y https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
```

### Ubuntu / Debian

```bash
# Download and install
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Windows

```powershell
# Download MSI installer
Invoke-WebRequest -Uri https://s3.amazonaws.com/amazoncloudwatch-agent/windows/amd64/latest/amazon-cloudwatch-agent.msi -OutFile amazon-cloudwatch-agent.msi

# Install
msiexec /i amazon-cloudwatch-agent.msi
```

### Using Systems Manager

```bash
# Install via SSM Run Command
aws ssm send-command \
    --document-name "AWS-ConfigureAWSPackage" \
    --targets "Key=instanceids,Values=i-1234567890abcdef0" \
    --parameters '{"action":["Install"],"name":["AmazonCloudWatchAgent"]}'
```

---

## IAM Requirements

### EC2 Instance Role Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudwatch:PutMetricData",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams",
                "logs:DescribeLogGroups",
                "ec2:DescribeVolumes",
                "ec2:DescribeTags",
                "ssm:GetParameter"
            ],
            "Resource": "*"
        }
    ]
}
```

### CloudFormation IAM Role

```yaml
Resources:
  CloudWatchAgentRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: CloudWatchAgentServerRole
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

  CloudWatchAgentInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref CloudWatchAgentRole
```

---

## Configuration

### Configuration Wizard

```bash
# Run the configuration wizard
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

The wizard asks about:
- Operating system
- Metrics to collect
- Log files to stream
- SSM parameter storage

### Configuration File Location

| OS | Path |
|----|------|
| Linux | /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json |
| Windows | C:\ProgramData\Amazon\AmazonCloudWatchAgent\amazon-cloudwatch-agent.json |

### Complete Configuration Example

```json
{
    "agent": {
        "metrics_collection_interval": 60,
        "run_as_user": "cwagent",
        "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
    },
    "metrics": {
        "namespace": "CWAgent",
        "metrics_collected": {
            "cpu": {
                "resources": ["*"],
                "measurement": [
                    "cpu_usage_idle",
                    "cpu_usage_user",
                    "cpu_usage_system"
                ],
                "totalcpu": true,
                "metrics_collection_interval": 60
            },
            "mem": {
                "measurement": [
                    "mem_used_percent",
                    "mem_available_percent",
                    "mem_used",
                    "mem_cached",
                    "mem_total"
                ],
                "metrics_collection_interval": 60
            },
            "disk": {
                "resources": ["/", "/data"],
                "measurement": [
                    "disk_used_percent",
                    "disk_free",
                    "disk_used",
                    "disk_total"
                ],
                "ignore_file_system_types": ["sysfs", "devtmpfs", "tmpfs"],
                "metrics_collection_interval": 60
            },
            "diskio": {
                "resources": ["*"],
                "measurement": [
                    "diskio_reads",
                    "diskio_writes",
                    "diskio_read_bytes",
                    "diskio_write_bytes"
                ],
                "metrics_collection_interval": 60
            },
            "net": {
                "resources": ["eth0"],
                "measurement": [
                    "net_bytes_recv",
                    "net_bytes_sent",
                    "net_packets_recv",
                    "net_packets_sent"
                ],
                "metrics_collection_interval": 60
            },
            "netstat": {
                "measurement": [
                    "netstat_tcp_established",
                    "netstat_tcp_time_wait"
                ],
                "metrics_collection_interval": 60
            },
            "processes": {
                "measurement": [
                    "processes_running",
                    "processes_sleeping",
                    "processes_zombies"
                ],
                "metrics_collection_interval": 60
            },
            "swap": {
                "measurement": [
                    "swap_used_percent",
                    "swap_used",
                    "swap_free"
                ],
                "metrics_collection_interval": 60
            }
        },
        "append_dimensions": {
            "InstanceId": "${aws:InstanceId}",
            "InstanceType": "${aws:InstanceType}",
            "AutoScalingGroupName": "${aws:AutoScalingGroupName}"
        },
        "aggregation_dimensions": [
            ["InstanceId"],
            ["AutoScalingGroupName"]
        ]
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "/ec2/var/log/messages",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": 30,
                        "timestamp_format": "%b %d %H:%M:%S"
                    },
                    {
                        "file_path": "/var/log/secure",
                        "log_group_name": "/ec2/var/log/secure",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": 90,
                        "timestamp_format": "%b %d %H:%M:%S"
                    },
                    {
                        "file_path": "/var/log/httpd/access_log",
                        "log_group_name": "/ec2/apache/access",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/httpd/error_log",
                        "log_group_name": "/ec2/apache/error",
                        "log_stream_name": "{instance_id}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/application/*.log",
                        "log_group_name": "/application/logs",
                        "log_stream_name": "{instance_id}/{file_name}",
                        "retention_in_days": 14,
                        "multi_line_start_pattern": "{timestamp_format}"
                    }
                ]
            }
        },
        "log_stream_name": "{instance_id}"
    }
}
```

---

## Metrics Configuration

### Available Metrics

#### CPU Metrics
```json
{
    "cpu": {
        "resources": ["*"],
        "measurement": [
            "cpu_usage_idle",
            "cpu_usage_user",
            "cpu_usage_system",
            "cpu_usage_iowait",
            "cpu_usage_steal",
            "cpu_usage_guest",
            "cpu_usage_nice",
            "cpu_usage_irq",
            "cpu_usage_softirq"
        ],
        "totalcpu": true
    }
}
```

#### Memory Metrics
```json
{
    "mem": {
        "measurement": [
            "mem_used_percent",
            "mem_available_percent",
            "mem_used",
            "mem_available",
            "mem_cached",
            "mem_buffered",
            "mem_total",
            "mem_free"
        ]
    }
}
```

#### Disk Metrics
```json
{
    "disk": {
        "resources": ["/", "/home", "/data"],
        "measurement": [
            "disk_used_percent",
            "disk_free",
            "disk_used",
            "disk_total",
            "disk_inodes_free",
            "disk_inodes_used",
            "disk_inodes_total"
        ],
        "ignore_file_system_types": [
            "sysfs", "devtmpfs", "tmpfs", "overlay"
        ]
    }
}
```

#### Network Metrics
```json
{
    "net": {
        "resources": ["eth0", "eth1"],
        "measurement": [
            "net_bytes_recv",
            "net_bytes_sent",
            "net_packets_recv",
            "net_packets_sent",
            "net_err_in",
            "net_err_out",
            "net_drop_in",
            "net_drop_out"
        ]
    }
}
```

### Custom Namespace

```json
{
    "metrics": {
        "namespace": "MyApplication/EC2",
        "metrics_collected": {
            "cpu": {},
            "mem": {}
        }
    }
}
```

### High-Resolution Metrics

```json
{
    "metrics": {
        "metrics_collected": {
            "cpu": {
                "metrics_collection_interval": 10
            }
        }
    }
}
```

---

## Logs Configuration

### Basic Log Collection

```json
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "messages",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    }
}
```

### Multi-line Log Events

```json
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/application/app.log",
                        "log_group_name": "application",
                        "log_stream_name": "{instance_id}",
                        "multi_line_start_pattern": "^\\d{4}-\\d{2}-\\d{2}",
                        "timestamp_format": "%Y-%m-%d %H:%M:%S"
                    }
                ]
            }
        }
    }
}
```

### Windows Event Logs

```json
{
    "logs": {
        "logs_collected": {
            "windows_events": {
                "collect_list": [
                    {
                        "event_name": "System",
                        "event_levels": ["CRITICAL", "ERROR", "WARNING"],
                        "log_group_name": "WindowsEvents/System",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "event_name": "Application",
                        "event_levels": ["CRITICAL", "ERROR"],
                        "log_group_name": "WindowsEvents/Application",
                        "log_stream_name": "{instance_id}"
                    },
                    {
                        "event_name": "Security",
                        "event_levels": ["CRITICAL", "ERROR", "WARNING", "INFORMATION"],
                        "log_group_name": "WindowsEvents/Security",
                        "log_stream_name": "{instance_id}"
                    }
                ]
            }
        }
    }
}
```

---

## StatsD and collectd Integration

### StatsD Configuration

```json
{
    "metrics": {
        "metrics_collected": {
            "statsd": {
                "service_address": ":8125",
                "metrics_collection_interval": 60,
                "metrics_aggregation_interval": 60
            }
        }
    }
}
```

### Send StatsD Metrics

```python
import statsd

# Create StatsD client
client = statsd.StatsClient('localhost', 8125)

# Counter
client.incr('myapp.requests')

# Gauge
client.gauge('myapp.queue_size', 100)

# Timer
with client.timer('myapp.processing_time'):
    process_request()
```

### collectd Configuration

```json
{
    "metrics": {
        "metrics_collected": {
            "collectd": {
                "service_address": "udp://127.0.0.1:25826",
                "metrics_aggregation_interval": 60
            }
        }
    }
}
```

---

## Managing the Agent

### Starting and Stopping

```bash
# Linux - Start agent with configuration file
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Start with SSM Parameter
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c ssm:AmazonCloudWatch-linux

# Stop agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop

# Check status
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status
```

### Windows Commands

```powershell
# Start agent
& "C:\Program Files\Amazon\AmazonCloudWatchAgent\amazon-cloudwatch-agent-ctl.ps1" -a fetch-config -m ec2 -s -c file:"C:\ProgramData\Amazon\AmazonCloudWatchAgent\amazon-cloudwatch-agent.json"

# Stop agent
& "C:\Program Files\Amazon\AmazonCloudWatchAgent\amazon-cloudwatch-agent-ctl.ps1" -a stop

# Check status
& "C:\Program Files\Amazon\AmazonCloudWatchAgent\amazon-cloudwatch-agent-ctl.ps1" -a status
```

---

## SSM Parameter Store

### Store Configuration

```bash
# Create SSM parameter with configuration
aws ssm put-parameter \
    --name "AmazonCloudWatch-linux" \
    --type "String" \
    --value file://cloudwatch-agent-config.json \
    --overwrite
```

### Use Configuration from SSM

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c ssm:AmazonCloudWatch-linux
```

---

## CloudFormation Deployment

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: EC2 with CloudWatch Agent

Parameters:
  InstanceType:
    Type: String
    Default: t3.micro
  KeyPair:
    Type: AWS::EC2::KeyPair::KeyName

Resources:
  CloudWatchAgentConfig:
    Type: AWS::SSM::Parameter
    Properties:
      Name: AmazonCloudWatch-config
      Type: String
      Value: |
        {
          "agent": {
            "metrics_collection_interval": 60
          },
          "metrics": {
            "namespace": "CWAgent",
            "metrics_collected": {
              "cpu": {
                "resources": ["*"],
                "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
                "totalcpu": true
              },
              "mem": {
                "measurement": ["mem_used_percent"]
              },
              "disk": {
                "resources": ["/"],
                "measurement": ["disk_used_percent"]
              }
            },
            "append_dimensions": {
              "InstanceId": "${aws:InstanceId}"
            }
          },
          "logs": {
            "logs_collected": {
              "files": {
                "collect_list": [
                  {
                    "file_path": "/var/log/messages",
                    "log_group_name": "/ec2/messages",
                    "log_stream_name": "{instance_id}"
                  }
                ]
              }
            }
          }
        }

  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      KeyName: !Ref KeyPair
      IamInstanceProfile: !Ref InstanceProfile
      ImageId: !Ref LatestAmiId
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum install -y amazon-cloudwatch-agent
          /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c ssm:AmazonCloudWatch-config

  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref CloudWatchAgentRole

  CloudWatchAgentRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
```

---

## Troubleshooting

### Log Locations

| OS | Agent Log Path |
|----|----------------|
| Linux | /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log |
| Windows | C:\ProgramData\Amazon\AmazonCloudWatchAgent\Logs\amazon-cloudwatch-agent.log |

### Common Issues

| Issue | Solution |
|-------|----------|
| Agent not starting | Check IAM role, verify configuration syntax |
| No metrics in CloudWatch | Verify namespace, check agent logs |
| Logs not appearing | Check file path, permissions, log group |
| Configuration error | Validate JSON syntax, use config wizard |

### Debugging Commands

```bash
# Check agent status
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status

# View agent logs
sudo tail -f /opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log

# Validate configuration
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a validate-config -c file:/path/to/config.json

# Test configuration
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/path/to/config.json
```

---

## Best Practices

### Configuration
1. Store configuration in SSM Parameter Store
2. Use automation for consistent deployment
3. Set appropriate collection intervals
4. Include instance dimensions for filtering

### Performance
1. Avoid collecting unnecessary metrics
2. Use appropriate collection intervals (60s for most)
3. Monitor agent resource usage
4. Use aggregation dimensions wisely

### Security
1. Use IAM roles instead of access keys
2. Encrypt logs with KMS
3. Limit log group access with IAM policies
4. Run agent as non-root user

---

## Next Steps

Continue to the next sections:
- [08-xray.md](08-xray.md) - Distributed tracing
- [12-hands-on-labs.md](12-hands-on-labs.md) - Configure agent hands-on
