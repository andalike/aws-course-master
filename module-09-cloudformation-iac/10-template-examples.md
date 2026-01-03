# Lesson 10: Production CloudFormation Templates

## Introduction

This lesson provides production-ready CloudFormation templates for common AWS architectures. Each template includes best practices for security, reliability, and maintainability. Use these as starting points for your own infrastructure.

---

## Template 1: Production VPC with Public and Private Subnets

This template creates a highly available VPC architecture with:
- VPC with configurable CIDR
- Public and private subnets across multiple AZs
- NAT Gateways for private subnet internet access
- VPC Flow Logs for network monitoring
- Network ACLs for additional security

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Production VPC - Multi-AZ with Public and Private Subnets'

Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: 'VPC Configuration'
        Parameters:
          - EnvironmentName
          - VPCCidr
          - EnableVPCFlowLogs
      - Label:
          default: 'Subnet Configuration'
        Parameters:
          - PublicSubnet1Cidr
          - PublicSubnet2Cidr
          - PublicSubnet3Cidr
          - PrivateSubnet1Cidr
          - PrivateSubnet2Cidr
          - PrivateSubnet3Cidr

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    AllowedValues:
      - development
      - staging
      - production
    Description: Environment name for tagging

  VPCCidr:
    Type: String
    Default: 10.0.0.0/16
    AllowedPattern: ^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$
    Description: VPC CIDR block (e.g., 10.0.0.0/16)

  PublicSubnet1Cidr:
    Type: String
    Default: 10.0.1.0/24
    Description: CIDR for Public Subnet 1

  PublicSubnet2Cidr:
    Type: String
    Default: 10.0.2.0/24
    Description: CIDR for Public Subnet 2

  PublicSubnet3Cidr:
    Type: String
    Default: 10.0.3.0/24
    Description: CIDR for Public Subnet 3

  PrivateSubnet1Cidr:
    Type: String
    Default: 10.0.11.0/24
    Description: CIDR for Private Subnet 1

  PrivateSubnet2Cidr:
    Type: String
    Default: 10.0.12.0/24
    Description: CIDR for Private Subnet 2

  PrivateSubnet3Cidr:
    Type: String
    Default: 10.0.13.0/24
    Description: CIDR for Private Subnet 3

  EnableVPCFlowLogs:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable VPC Flow Logs

Conditions:
  CreateFlowLogs: !Equals [!Ref EnableVPCFlowLogs, 'true']
  IsProduction: !Equals [!Ref EnvironmentName, 'production']

Resources:
  #=====================================
  # VPC
  #=====================================
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VPCCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      InstanceTenancy: default
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-vpc'
        - Key: Environment
          Value: !Ref EnvironmentName

  #=====================================
  # Internet Gateway
  #=====================================
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-igw'
        - Key: Environment
          Value: !Ref EnvironmentName

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  #=====================================
  # Public Subnets
  #=====================================
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Ref PublicSubnet1Cidr
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-subnet-1'
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Type
          Value: Public

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Ref PublicSubnet2Cidr
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-subnet-2'
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Type
          Value: Public

  PublicSubnet3:
    Type: AWS::EC2::Subnet
    Condition: IsProduction
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [2, !GetAZs '']
      CidrBlock: !Ref PublicSubnet3Cidr
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-subnet-3'
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Type
          Value: Public

  #=====================================
  # Private Subnets
  #=====================================
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: !Ref PrivateSubnet1Cidr
      MapPublicIpOnLaunch: false
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-subnet-1'
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Type
          Value: Private

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: !Ref PrivateSubnet2Cidr
      MapPublicIpOnLaunch: false
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-subnet-2'
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Type
          Value: Private

  PrivateSubnet3:
    Type: AWS::EC2::Subnet
    Condition: IsProduction
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [2, !GetAZs '']
      CidrBlock: !Ref PrivateSubnet3Cidr
      MapPublicIpOnLaunch: false
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-subnet-3'
        - Key: Environment
          Value: !Ref EnvironmentName
        - Key: Type
          Value: Private

  #=====================================
  # NAT Gateways
  #=====================================
  NatGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-nat-eip-1'

  NatGateway2EIP:
    Type: AWS::EC2::EIP
    Condition: IsProduction
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-nat-eip-2'

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-nat-gw-1'

  NatGateway2:
    Type: AWS::EC2::NatGateway
    Condition: IsProduction
    Properties:
      AllocationId: !GetAtt NatGateway2EIP.AllocationId
      SubnetId: !Ref PublicSubnet2
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-nat-gw-2'

  #=====================================
  # Public Route Table
  #=====================================
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-public-rt'

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref PublicRouteTable

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref PublicRouteTable

  PublicSubnet3RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Condition: IsProduction
    Properties:
      SubnetId: !Ref PublicSubnet3
      RouteTableId: !Ref PublicRouteTable

  #=====================================
  # Private Route Tables
  #=====================================
  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-rt-1'

  DefaultPrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet1
      RouteTableId: !Ref PrivateRouteTable1

  PrivateRouteTable2:
    Type: AWS::EC2::RouteTable
    Condition: IsProduction
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-private-rt-2'

  DefaultPrivateRoute2:
    Type: AWS::EC2::Route
    Condition: IsProduction
    Properties:
      RouteTableId: !Ref PrivateRouteTable2
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway2

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet2
      RouteTableId: !If [IsProduction, !Ref PrivateRouteTable2, !Ref PrivateRouteTable1]

  PrivateSubnet3RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Condition: IsProduction
    Properties:
      SubnetId: !Ref PrivateSubnet3
      RouteTableId: !Ref PrivateRouteTable1

  #=====================================
  # VPC Flow Logs
  #=====================================
  FlowLogsLogGroup:
    Type: AWS::Logs::LogGroup
    Condition: CreateFlowLogs
    Properties:
      LogGroupName: !Sub '/aws/vpc/${EnvironmentName}-flow-logs'
      RetentionInDays: 30

  FlowLogsRole:
    Type: AWS::IAM::Role
    Condition: CreateFlowLogs
    Properties:
      RoleName: !Sub '${EnvironmentName}-vpc-flow-logs-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: vpc-flow-logs.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: FlowLogsPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                  - logs:DescribeLogGroups
                  - logs:DescribeLogStreams
                Resource: !GetAtt FlowLogsLogGroup.Arn

  VPCFlowLog:
    Type: AWS::EC2::FlowLog
    Condition: CreateFlowLogs
    Properties:
      ResourceId: !Ref VPC
      ResourceType: VPC
      TrafficType: ALL
      LogDestinationType: cloud-watch-logs
      LogGroupName: !Ref FlowLogsLogGroup
      DeliverLogsPermissionArn: !GetAtt FlowLogsRole.Arn
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-vpc-flow-log'

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VPCId'

  VPCCidr:
    Description: VPC CIDR
    Value: !Ref VPCCidr
    Export:
      Name: !Sub '${AWS::StackName}-VPCCidr'

  PublicSubnet1Id:
    Description: Public Subnet 1 ID
    Value: !Ref PublicSubnet1
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnet1Id'

  PublicSubnet2Id:
    Description: Public Subnet 2 ID
    Value: !Ref PublicSubnet2
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnet2Id'

  PublicSubnet3Id:
    Description: Public Subnet 3 ID
    Condition: IsProduction
    Value: !Ref PublicSubnet3
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnet3Id'

  PrivateSubnet1Id:
    Description: Private Subnet 1 ID
    Value: !Ref PrivateSubnet1
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnet1Id'

  PrivateSubnet2Id:
    Description: Private Subnet 2 ID
    Value: !Ref PrivateSubnet2
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnet2Id'

  PrivateSubnet3Id:
    Description: Private Subnet 3 ID
    Condition: IsProduction
    Value: !Ref PrivateSubnet3
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnet3Id'

  PublicSubnetIds:
    Description: Public Subnet IDs (comma-separated)
    Value: !If
      - IsProduction
      - !Join [',', [!Ref PublicSubnet1, !Ref PublicSubnet2, !Ref PublicSubnet3]]
      - !Join [',', [!Ref PublicSubnet1, !Ref PublicSubnet2]]
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnetIds'

  PrivateSubnetIds:
    Description: Private Subnet IDs (comma-separated)
    Value: !If
      - IsProduction
      - !Join [',', [!Ref PrivateSubnet1, !Ref PrivateSubnet2, !Ref PrivateSubnet3]]
      - !Join [',', [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
    Export:
      Name: !Sub '${AWS::StackName}-PrivateSubnetIds'
```

---

## Template 2: EC2 with Auto Scaling and ALB

This template creates:
- Application Load Balancer with HTTPS support
- Auto Scaling Group with health checks
- Launch Template with latest Amazon Linux 2023
- CloudWatch alarms for scaling

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 Auto Scaling with Application Load Balancer'

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    Description: Environment name

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PublicSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Public subnet IDs for ALB

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Private subnet IDs for EC2 instances

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t3.micro
      - t3.small
      - t3.medium
      - t3.large
      - m5.large
      - m5.xlarge
    Description: EC2 instance type

  MinSize:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 10
    Description: Minimum number of instances

  MaxSize:
    Type: Number
    Default: 6
    MinValue: 2
    MaxValue: 20
    Description: Maximum number of instances

  DesiredCapacity:
    Type: Number
    Default: 2
    MinValue: 1
    MaxValue: 10
    Description: Desired number of instances

  TargetCPUUtilization:
    Type: Number
    Default: 70
    MinValue: 20
    MaxValue: 90
    Description: Target CPU utilization for scaling

  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64
    Description: Latest Amazon Linux 2023 AMI

  SSLCertificateArn:
    Type: String
    Default: ''
    Description: ARN of SSL certificate (optional)

Conditions:
  HasSSLCertificate: !Not [!Equals [!Ref SSLCertificateArn, '']]

Resources:
  #=====================================
  # Security Groups
  #=====================================
  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for ALB
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: HTTP from anywhere
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
          Description: HTTPS from anywhere
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-alb-sg'

  EC2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2 instances
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref ALBSecurityGroup
          Description: HTTP from ALB
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-ec2-sg'

  #=====================================
  # IAM Role for EC2
  #=====================================
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${EnvironmentName}-ec2-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-ec2-role'

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      InstanceProfileName: !Sub '${EnvironmentName}-ec2-instance-profile'
      Roles:
        - !Ref EC2Role

  #=====================================
  # Application Load Balancer
  #=====================================
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${EnvironmentName}-alb'
      Type: application
      Scheme: internet-facing
      SecurityGroups:
        - !Ref ALBSecurityGroup
      Subnets: !Ref PublicSubnetIds
      LoadBalancerAttributes:
        - Key: idle_timeout.timeout_seconds
          Value: '60'
        - Key: deletion_protection.enabled
          Value: 'false'
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-alb'

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${EnvironmentName}-tg'
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPCId
      TargetType: instance
      HealthCheckEnabled: true
      HealthCheckPath: /health
      HealthCheckProtocol: HTTP
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 5
      Matcher:
        HttpCode: 200-299
      TargetGroupAttributes:
        - Key: deregistration_delay.timeout_seconds
          Value: '30'
        - Key: stickiness.enabled
          Value: 'false'
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-tg'

  HTTPListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - !If
          - HasSSLCertificate
          - Type: redirect
            RedirectConfig:
              Protocol: HTTPS
              Port: '443'
              StatusCode: HTTP_301
          - Type: forward
            TargetGroupArn: !Ref TargetGroup

  HTTPSListener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Condition: HasSSLCertificate
    Properties:
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 443
      Protocol: HTTPS
      Certificates:
        - CertificateArn: !Ref SSLCertificateArn
      SslPolicy: ELBSecurityPolicy-TLS13-1-2-2021-06
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup

  #=====================================
  # Launch Template
  #=====================================
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub '${EnvironmentName}-launch-template'
      LaunchTemplateData:
        ImageId: !Ref LatestAmiId
        InstanceType: !Ref InstanceType
        IamInstanceProfile:
          Arn: !GetAtt EC2InstanceProfile.Arn
        SecurityGroupIds:
          - !Ref EC2SecurityGroup
        Monitoring:
          Enabled: true
        MetadataOptions:
          HttpEndpoint: enabled
          HttpTokens: required  # IMDSv2 required
          HttpPutResponseHopLimit: 1
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            set -ex

            # Update system
            dnf update -y

            # Install required packages
            dnf install -y httpd stress-ng

            # Configure Apache
            systemctl start httpd
            systemctl enable httpd

            # Create health check endpoint
            echo "OK" > /var/www/html/health

            # Create main page
            INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
            AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)

            cat <<EOF > /var/www/html/index.html
            <!DOCTYPE html>
            <html>
            <head>
                <title>${EnvironmentName} Application</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .info { background: #f4f4f4; padding: 20px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Welcome to ${EnvironmentName}</h1>
                <div class="info">
                    <p><strong>Instance ID:</strong> $INSTANCE_ID</p>
                    <p><strong>Availability Zone:</strong> $AZ</p>
                    <p><strong>Timestamp:</strong> $(date)</p>
                </div>
            </body>
            </html>
            EOF

            # Install CloudWatch agent
            dnf install -y amazon-cloudwatch-agent
            /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
              -a fetch-config -m ec2 -s

        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub '${EnvironmentName}-instance'
              - Key: Environment
                Value: !Ref EnvironmentName

  #=====================================
  # Auto Scaling Group
  #=====================================
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub '${EnvironmentName}-asg'
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: !Ref MinSize
      MaxSize: !Ref MaxSize
      DesiredCapacity: !Ref DesiredCapacity
      VPCZoneIdentifier: !Ref PrivateSubnetIds
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      TerminationPolicies:
        - OldestInstance
      MetricsCollection:
        - Granularity: 1Minute
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-asg'
          PropagateAtLaunch: false
    UpdatePolicy:
      AutoScalingRollingUpdate:
        MinInstancesInService: 1
        MaxBatchSize: 1
        PauseTime: PT5M
        WaitOnResourceSignals: false

  #=====================================
  # Scaling Policies
  #=====================================
  CPUTargetTrackingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: !Ref TargetCPUUtilization
        DisableScaleIn: false

  RequestCountTargetTrackingPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref AutoScalingGroup
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ALBRequestCountPerTarget
          ResourceLabel: !Sub '${ApplicationLoadBalancer.LoadBalancerFullName}/${TargetGroup.TargetGroupFullName}'
        TargetValue: 1000
        DisableScaleIn: false

  #=====================================
  # CloudWatch Alarms
  #=====================================
  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${EnvironmentName}-high-cpu'
      AlarmDescription: Alarm when CPU exceeds 80%
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup

  UnhealthyHostsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${EnvironmentName}-unhealthy-hosts'
      AlarmDescription: Alarm when there are unhealthy hosts
      MetricName: UnHealthyHostCount
      Namespace: AWS/ApplicationELB
      Statistic: Average
      Period: 60
      EvaluationPeriods: 2
      Threshold: 1
      ComparisonOperator: GreaterThanOrEqualToThreshold
      Dimensions:
        - Name: LoadBalancer
          Value: !GetAtt ApplicationLoadBalancer.LoadBalancerFullName
        - Name: TargetGroup
          Value: !GetAtt TargetGroup.TargetGroupFullName

Outputs:
  LoadBalancerDNS:
    Description: ALB DNS Name
    Value: !GetAtt ApplicationLoadBalancer.DNSName
    Export:
      Name: !Sub '${AWS::StackName}-ALBDNSName'

  LoadBalancerURL:
    Description: ALB URL
    Value: !Sub 'http://${ApplicationLoadBalancer.DNSName}'

  AutoScalingGroupName:
    Description: Auto Scaling Group Name
    Value: !Ref AutoScalingGroup
    Export:
      Name: !Sub '${AWS::StackName}-ASGName'

  TargetGroupArn:
    Description: Target Group ARN
    Value: !Ref TargetGroup
    Export:
      Name: !Sub '${AWS::StackName}-TargetGroupArn'
```

---

## Template 3: Serverless API with Lambda and API Gateway

This template creates:
- Lambda function with VPC access
- API Gateway REST API
- DynamoDB table
- IAM roles with least privilege

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Serverless API - Lambda, API Gateway, DynamoDB'

Transform: AWS::Serverless-2016-10-31

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    Description: Environment name

  FunctionMemory:
    Type: Number
    Default: 256
    AllowedValues:
      - 128
      - 256
      - 512
      - 1024
      - 2048
    Description: Lambda function memory in MB

  FunctionTimeout:
    Type: Number
    Default: 30
    MinValue: 1
    MaxValue: 900
    Description: Lambda function timeout in seconds

  LogRetentionDays:
    Type: Number
    Default: 30
    AllowedValues:
      - 1
      - 7
      - 14
      - 30
      - 60
      - 90
      - 365
    Description: CloudWatch log retention period

Globals:
  Function:
    Timeout: !Ref FunctionTimeout
    MemorySize: !Ref FunctionMemory
    Runtime: python3.11
    Architectures:
      - arm64
    Tracing: Active
    Environment:
      Variables:
        TABLE_NAME: !Ref ItemsTable
        POWERTOOLS_SERVICE_NAME: !Ref EnvironmentName
        LOG_LEVEL: INFO

Resources:
  #=====================================
  # DynamoDB Table
  #=====================================
  ItemsTable:
    Type: AWS::DynamoDB::Table
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      TableName: !Sub '${EnvironmentName}-items'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
        - AttributeName: gsi1pk
          AttributeType: S
        - AttributeName: gsi1sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: gsi1pk
              KeyType: HASH
            - AttributeName: gsi1sk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

  #=====================================
  # Lambda Execution Role
  #=====================================
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${EnvironmentName}-lambda-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        - arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
      Policies:
        - PolicyName: DynamoDBAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource:
                  - !GetAtt ItemsTable.Arn
                  - !Sub '${ItemsTable.Arn}/index/*'

  #=====================================
  # Lambda Function
  #=====================================
  ApiFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${EnvironmentName}-api-handler'
      Runtime: python3.11
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      MemorySize: !Ref FunctionMemory
      Timeout: !Ref FunctionTimeout
      Architectures:
        - arm64
      TracingConfig:
        Mode: Active
      Environment:
        Variables:
          TABLE_NAME: !Ref ItemsTable
          ENVIRONMENT: !Ref EnvironmentName
      Code:
        ZipFile: |
          import json
          import os
          import boto3
          from decimal import Decimal
          from datetime import datetime
          import logging

          logger = logging.getLogger()
          logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

          dynamodb = boto3.resource('dynamodb')
          table = dynamodb.Table(os.environ['TABLE_NAME'])

          class DecimalEncoder(json.JSONEncoder):
              def default(self, obj):
                  if isinstance(obj, Decimal):
                      return str(obj)
                  return super().default(obj)

          def response(status_code, body):
              return {
                  'statusCode': status_code,
                  'headers': {
                      'Content-Type': 'application/json',
                      'Access-Control-Allow-Origin': '*',
                      'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                      'Access-Control-Allow-Headers': 'Content-Type,Authorization'
                  },
                  'body': json.dumps(body, cls=DecimalEncoder)
              }

          def handler(event, context):
              logger.info(f"Event: {json.dumps(event)}")

              try:
                  method = event.get('httpMethod', '')
                  path = event.get('path', '')
                  path_params = event.get('pathParameters') or {}
                  item_id = path_params.get('id')

                  if method == 'GET' and path == '/items':
                      result = table.scan()
                      return response(200, {'items': result.get('Items', [])})

                  if method == 'GET' and item_id:
                      result = table.get_item(Key={'pk': f'ITEM#{item_id}', 'sk': 'METADATA'})
                      item = result.get('Item')
                      if not item:
                          return response(404, {'error': 'Item not found'})
                      return response(200, item)

                  if method == 'POST':
                      body = json.loads(event.get('body') or '{}')
                      item_id = body.get('id', context.aws_request_id)
                      item = {
                          'pk': f'ITEM#{item_id}',
                          'sk': 'METADATA',
                          'id': item_id,
                          'data': body.get('data', {}),
                          'createdAt': datetime.utcnow().isoformat(),
                          'updatedAt': datetime.utcnow().isoformat()
                      }
                      table.put_item(Item=item)
                      return response(201, item)

                  if method == 'PUT' and item_id:
                      body = json.loads(event.get('body') or '{}')
                      table.update_item(
                          Key={'pk': f'ITEM#{item_id}', 'sk': 'METADATA'},
                          UpdateExpression='SET #data = :data, updatedAt = :updatedAt',
                          ExpressionAttributeNames={'#data': 'data'},
                          ExpressionAttributeValues={
                              ':data': body.get('data', {}),
                              ':updatedAt': datetime.utcnow().isoformat()
                          }
                      )
                      return response(200, {'message': 'Updated successfully'})

                  if method == 'DELETE' and item_id:
                      table.delete_item(Key={'pk': f'ITEM#{item_id}', 'sk': 'METADATA'})
                      return response(204, {})

                  return response(400, {'error': 'Invalid request'})

              except Exception as e:
                  logger.error(f"Error: {str(e)}")
                  return response(500, {'error': 'Internal server error'})
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

  # Lambda Log Group
  ApiFunctionLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub '/aws/lambda/${ApiFunction}'
      RetentionInDays: !Ref LogRetentionDays

  #=====================================
  # API Gateway
  #=====================================
  ApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub '${EnvironmentName}-api'
      Description: Serverless API
      EndpointConfiguration:
        Types:
          - REGIONAL
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

  # /items resource
  ItemsResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGateway
      ParentId: !GetAtt ApiGateway.RootResourceId
      PathPart: items

  # /items/{id} resource
  ItemResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGateway
      ParentId: !Ref ItemsResource
      PathPart: '{id}'

  # GET /items
  GetItemsMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ItemsResource
      HttpMethod: GET
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations'

  # POST /items
  PostItemsMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ItemsResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations'

  # GET /items/{id}
  GetItemMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ItemResource
      HttpMethod: GET
      AuthorizationType: NONE
      RequestParameters:
        method.request.path.id: true
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations'

  # PUT /items/{id}
  PutItemMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ItemResource
      HttpMethod: PUT
      AuthorizationType: NONE
      RequestParameters:
        method.request.path.id: true
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations'

  # DELETE /items/{id}
  DeleteItemMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ItemResource
      HttpMethod: DELETE
      AuthorizationType: NONE
      RequestParameters:
        method.request.path.id: true
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ApiFunction.Arn}/invocations'

  # CORS for /items
  ItemsOptionsMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ItemsResource
      HttpMethod: OPTIONS
      AuthorizationType: NONE
      Integration:
        Type: MOCK
        IntegrationResponses:
          - StatusCode: 200
            ResponseParameters:
              method.response.header.Access-Control-Allow-Headers: "'Content-Type,Authorization'"
              method.response.header.Access-Control-Allow-Methods: "'GET,POST,OPTIONS'"
              method.response.header.Access-Control-Allow-Origin: "'*'"
            ResponseTemplates:
              application/json: ''
        RequestTemplates:
          application/json: '{"statusCode": 200}'
      MethodResponses:
        - StatusCode: 200
          ResponseParameters:
            method.response.header.Access-Control-Allow-Headers: true
            method.response.header.Access-Control-Allow-Methods: true
            method.response.header.Access-Control-Allow-Origin: true

  # Lambda Permission for API Gateway
  ApiGatewayLambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ApiFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub 'arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ApiGateway}/*'

  # API Deployment
  ApiDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn:
      - GetItemsMethod
      - PostItemsMethod
      - GetItemMethod
      - PutItemMethod
      - DeleteItemMethod
      - ItemsOptionsMethod
    Properties:
      RestApiId: !Ref ApiGateway

  # API Stage
  ApiStage:
    Type: AWS::ApiGateway::Stage
    Properties:
      RestApiId: !Ref ApiGateway
      DeploymentId: !Ref ApiDeployment
      StageName: !Ref EnvironmentName
      TracingEnabled: true
      MethodSettings:
        - ResourcePath: '/*'
          HttpMethod: '*'
          LoggingLevel: INFO
          DataTraceEnabled: true
          MetricsEnabled: true
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub 'https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/${EnvironmentName}'
    Export:
      Name: !Sub '${AWS::StackName}-ApiEndpoint'

  FunctionName:
    Description: Lambda function name
    Value: !Ref ApiFunction
    Export:
      Name: !Sub '${AWS::StackName}-FunctionName'

  FunctionArn:
    Description: Lambda function ARN
    Value: !GetAtt ApiFunction.Arn
    Export:
      Name: !Sub '${AWS::StackName}-FunctionArn'

  TableName:
    Description: DynamoDB table name
    Value: !Ref ItemsTable
    Export:
      Name: !Sub '${AWS::StackName}-TableName'

  TableArn:
    Description: DynamoDB table ARN
    Value: !GetAtt ItemsTable.Arn
    Export:
      Name: !Sub '${AWS::StackName}-TableArn'
```

---

## Template 4: RDS MySQL with Multi-AZ

This template creates:
- RDS MySQL instance with Multi-AZ
- Parameter group for tuning
- Secrets Manager for credentials
- CloudWatch alarms

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'RDS MySQL with Multi-AZ and Secrets Manager'

Parameters:
  EnvironmentName:
    Type: String
    Default: production
    Description: Environment name

  VPCId:
    Type: AWS::EC2::VPC::Id
    Description: VPC ID

  PrivateSubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Private subnet IDs for RDS

  DBInstanceClass:
    Type: String
    Default: db.t3.medium
    AllowedValues:
      - db.t3.micro
      - db.t3.small
      - db.t3.medium
      - db.t3.large
      - db.r5.large
      - db.r5.xlarge
    Description: Database instance class

  DBAllocatedStorage:
    Type: Number
    Default: 100
    MinValue: 20
    MaxValue: 1000
    Description: Allocated storage in GB

  DBMaxAllocatedStorage:
    Type: Number
    Default: 500
    MinValue: 100
    MaxValue: 16384
    Description: Maximum storage autoscaling limit in GB

  DBName:
    Type: String
    Default: appdb
    AllowedPattern: '[a-zA-Z][a-zA-Z0-9]*'
    MinLength: 1
    MaxLength: 64
    Description: Database name

  DBMasterUsername:
    Type: String
    Default: admin
    AllowedPattern: '[a-zA-Z][a-zA-Z0-9]*'
    MinLength: 1
    MaxLength: 16
    Description: Database master username

  MultiAZ:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: Enable Multi-AZ deployment

  BackupRetentionPeriod:
    Type: Number
    Default: 7
    MinValue: 1
    MaxValue: 35
    Description: Backup retention period in days

  AllowedCIDR:
    Type: String
    Default: 10.0.0.0/16
    Description: CIDR block allowed to access database

Conditions:
  IsMultiAZ: !Equals [!Ref MultiAZ, 'true']

Resources:
  #=====================================
  # Secrets Manager Secret
  #=====================================
  DBSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '${EnvironmentName}/rds/mysql/credentials'
      Description: RDS database credentials
      GenerateSecretString:
        SecretStringTemplate: !Sub '{"username": "${DBMasterUsername}"}'
        GenerateStringKey: password
        PasswordLength: 32
        ExcludeCharacters: '"@/\'
      Tags:
        - Key: Environment
          Value: !Ref EnvironmentName

  #=====================================
  # Security Group
  #=====================================
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for RDS
      VpcId: !Ref VPCId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          CidrIp: !Ref AllowedCIDR
          Description: MySQL access from VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-rds-sg'

  #=====================================
  # DB Subnet Group
  #=====================================
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for RDS
      SubnetIds: !Ref PrivateSubnetIds
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-db-subnet-group'

  #=====================================
  # DB Parameter Group
  #=====================================
  DBParameterGroup:
    Type: AWS::RDS::DBParameterGroup
    Properties:
      Description: Custom parameter group for MySQL
      Family: mysql8.0
      Parameters:
        character_set_server: utf8mb4
        collation_server: utf8mb4_unicode_ci
        max_connections: '1000'
        slow_query_log: '1'
        long_query_time: '2'
        log_output: FILE
        general_log: '0'
        innodb_buffer_pool_size: '{DBInstanceClassMemory*3/4}'
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-db-params'

  #=====================================
  # RDS Instance
  #=====================================
  DBInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    UpdateReplacePolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub '${EnvironmentName}-mysql'
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: !Sub '{{resolve:secretsmanager:${DBSecret}:SecretString:username}}'
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DBSecret}:SecretString:password}}'
      DBName: !Ref DBName
      AllocatedStorage: !Ref DBAllocatedStorage
      MaxAllocatedStorage: !Ref DBMaxAllocatedStorage
      StorageType: gp3
      StorageEncrypted: true
      MultiAZ: !If [IsMultiAZ, true, false]
      PubliclyAccessible: false
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBParameterGroupName: !Ref DBParameterGroup
      BackupRetentionPeriod: !Ref BackupRetentionPeriod
      PreferredBackupWindow: '03:00-04:00'
      PreferredMaintenanceWindow: 'sun:04:00-sun:05:00'
      AutoMinorVersionUpgrade: true
      CopyTagsToSnapshot: true
      DeletionProtection: true
      EnablePerformanceInsights: true
      PerformanceInsightsRetentionPeriod: 7
      MonitoringInterval: 60
      MonitoringRoleArn: !GetAtt EnhancedMonitoringRole.Arn
      EnableCloudwatchLogsExports:
        - error
        - slowquery
        - general
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-mysql'
        - Key: Environment
          Value: !Ref EnvironmentName

  #=====================================
  # Enhanced Monitoring Role
  #=====================================
  EnhancedMonitoringRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub '${EnvironmentName}-rds-monitoring-role'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: monitoring.rds.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole

  #=====================================
  # Secret Attachment
  #=====================================
  SecretRDSAttachment:
    Type: AWS::SecretsManager::SecretTargetAttachment
    Properties:
      SecretId: !Ref DBSecret
      TargetId: !Ref DBInstance
      TargetType: AWS::RDS::DBInstance

  #=====================================
  # CloudWatch Alarms
  #=====================================
  HighCPUAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${EnvironmentName}-rds-high-cpu'
      AlarmDescription: RDS CPU utilization is high
      MetricName: CPUUtilization
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 80
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstance

  LowFreeStorageAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${EnvironmentName}-rds-low-storage'
      AlarmDescription: RDS free storage is low
      MetricName: FreeStorageSpace
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 10737418240  # 10 GB in bytes
      ComparisonOperator: LessThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstance

  HighDatabaseConnectionsAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${EnvironmentName}-rds-high-connections'
      AlarmDescription: RDS database connections are high
      MetricName: DatabaseConnections
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 800
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstance

  ReadLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: !Sub '${EnvironmentName}-rds-read-latency'
      AlarmDescription: RDS read latency is high
      MetricName: ReadLatency
      Namespace: AWS/RDS
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 0.05  # 50ms
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: DBInstanceIdentifier
          Value: !Ref DBInstance

Outputs:
  DBEndpoint:
    Description: Database endpoint
    Value: !GetAtt DBInstance.Endpoint.Address
    Export:
      Name: !Sub '${AWS::StackName}-DBEndpoint'

  DBPort:
    Description: Database port
    Value: !GetAtt DBInstance.Endpoint.Port
    Export:
      Name: !Sub '${AWS::StackName}-DBPort'

  DBSecretArn:
    Description: Database credentials secret ARN
    Value: !Ref DBSecret
    Export:
      Name: !Sub '${AWS::StackName}-DBSecretArn'

  DBInstanceIdentifier:
    Description: Database instance identifier
    Value: !Ref DBInstance
    Export:
      Name: !Sub '${AWS::StackName}-DBInstanceIdentifier'

  DBSecurityGroupId:
    Description: Database security group ID
    Value: !Ref DBSecurityGroup
    Export:
      Name: !Sub '${AWS::StackName}-DBSecurityGroupId'

  ConnectionString:
    Description: Connection string (use with Secrets Manager)
    Value: !Sub 'mysql://${DBMasterUsername}:PASSWORD@${DBInstance.Endpoint.Address}:${DBInstance.Endpoint.Port}/${DBName}'
```

---

## Template Best Practices Summary

```
┌─────────────────────────────────────────────────────────────────┐
│              CloudFormation Best Practices                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TEMPLATE STRUCTURE                                             │
│  ├── Use Metadata for console organization                     │
│  ├── Group related parameters                                   │
│  ├── Add descriptions to all parameters                         │
│  └── Use conditions for environment-specific resources          │
│                                                                  │
│  SECURITY                                                       │
│  ├── Use Secrets Manager for credentials                        │
│  ├── Enable encryption at rest                                  │
│  ├── Use VPC endpoints where possible                           │
│  ├── Implement least privilege IAM                              │
│  └── Enable logging and monitoring                              │
│                                                                  │
│  RELIABILITY                                                    │
│  ├── Use Multi-AZ for databases                                 │
│  ├── Configure proper health checks                             │
│  ├── Set appropriate timeouts                                   │
│  ├── Use DeletionPolicy: Retain for stateful resources         │
│  └── Enable automated backups                                   │
│                                                                  │
│  MAINTAINABILITY                                                │
│  ├── Use consistent naming conventions                          │
│  ├── Tag all resources                                          │
│  ├── Export commonly referenced values                          │
│  ├── Use SSM Parameter Store for AMI IDs                        │
│  └── Document with comments                                     │
│                                                                  │
│  COST OPTIMIZATION                                              │
│  ├── Use parameters for instance sizes                          │
│  ├── Implement auto scaling                                     │
│  ├── Use conditions to reduce non-prod resources               │
│  └── Enable storage autoscaling                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Commands

```bash
# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Create stack
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --tags Key=Environment,Value=production

# Update stack
aws cloudformation update-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM

# Create change set
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name update-v2 \
  --template-body file://template.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM

# Execute change set
aws cloudformation execute-change-set \
  --stack-name my-stack \
  --change-set-name update-v2
```

---

## Next Steps

1. **Customize**: Modify templates for your specific requirements
2. **Test**: Deploy in development environment first
3. **Practice**: Complete the hands-on lab

---

**Next:** [Lesson 11 - Hands-on Lab](./11-hands-on-lab.md)
