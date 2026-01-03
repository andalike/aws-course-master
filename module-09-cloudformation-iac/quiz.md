# Module 9: CloudFormation and Infrastructure as Code - Quiz

## Instructions

- **Total Questions**: 30
- **Time Limit**: 45 minutes (suggested)
- **Passing Score**: 80% (24 correct answers)
- **Format**: Multiple choice and multiple select

Answer each question to the best of your ability. Answers and explanations are provided at the end.

---

## Section 1: CloudFormation Fundamentals (Questions 1-6)

### Question 1

What is the only required section in a CloudFormation template?

A) Parameters
B) Resources
C) Outputs
D) Mappings

---

### Question 2

Which CloudFormation template format is recommended for readability?

A) XML
B) JSON
C) YAML
D) Both JSON and YAML are equally recommended

---

### Question 3

What is the maximum size of a CloudFormation template body when passed directly to the API?

A) 1 MB
B) 51,200 bytes
C) 460,800 bytes
D) 100 KB

---

### Question 4

What happens by default when a CloudFormation stack creation fails?

A) The stack remains in a failed state with all resources
B) All successfully created resources are retained
C) All resources are automatically rolled back and deleted
D) Only the failed resource is deleted

---

### Question 5

Which AWS CLI command creates a new CloudFormation stack?

A) `aws cloudformation deploy`
B) `aws cloudformation create-stack`
C) `aws cloudformation new-stack`
D) Both A and B

---

### Question 6

What is the purpose of the `AWSTemplateFormatVersion` field?

A) To specify which AWS CLI version to use
B) To identify the capabilities of the template
C) To specify the minimum AWS SDK version
D) To enable certain CloudFormation features

---

## Section 2: Template Structure (Questions 7-12)

### Question 7

Which section allows you to pass values into your template at stack creation time?

A) Mappings
B) Conditions
C) Parameters
D) Metadata

---

### Question 8

What is the maximum number of parameters allowed in a single CloudFormation template?

A) 60
B) 100
C) 200
D) 500

---

### Question 9

Which parameter type would you use to allow users to select an existing EC2 key pair?

A) `String`
B) `AWS::EC2::KeyPair`
C) `AWS::EC2::KeyPair::KeyName`
D) `AWS::SSM::Parameter::Value<String>`

---

### Question 10

What is the purpose of the Mappings section?

A) To create key-value lookups based on runtime values
B) To define conditional logic
C) To create static key-value lookups based on known values
D) To map parameters to resources

---

### Question 11

Which statement about CloudFormation Conditions is TRUE?

A) Conditions can reference other conditions
B) Conditions can only be used with the Fn::If function
C) Conditions are evaluated at stack update time only
D) Conditions cannot reference parameters

---

### Question 12

What is the maximum number of outputs per CloudFormation template?

A) 60
B) 100
C) 200
D) 500

---

## Section 3: Intrinsic Functions (Questions 13-18)

### Question 13

Which intrinsic function returns the value of a resource or parameter?

A) `Fn::GetAtt`
B) `Fn::Sub`
C) `Ref`
D) `Fn::ImportValue`

---

### Question 14

What does `!GetAtt MyEC2Instance.PublicIp` return?

A) The Instance ID
B) The public IP address of the instance
C) The private IP address of the instance
D) The Availability Zone of the instance

---

### Question 15

Which function would you use to perform variable substitution in a string?

A) `Fn::Join`
B) `Fn::Sub`
C) `Fn::Replace`
D) `Fn::Format`

---

### Question 16

What is the correct syntax for `Fn::If`?

A) `!If [ConditionName, TrueValue]`
B) `!If [ConditionName, TrueValue, FalseValue]`
C) `!If {Condition: ConditionName, Then: TrueValue, Else: FalseValue}`
D) `!If ConditionName ? TrueValue : FalseValue`

---

### Question 17

Which function retrieves an exported value from another stack?

A) `Fn::GetAtt`
B) `Ref`
C) `Fn::ImportValue`
D) `Fn::CrossStackRef`

---

### Question 18

What does the `Fn::GetAZs` function return when passed an empty string?

A) All Availability Zones in all regions
B) The Availability Zones in the current region
C) An error because empty string is invalid
D) The default Availability Zone only

---

## Section 4: Stack Operations (Questions 19-22)

### Question 19

What is the primary purpose of a Change Set?

A) To create a backup of the current stack
B) To preview changes before executing them
C) To automatically detect drift
D) To rollback failed updates

---

### Question 20

Which DeletionPolicy value ensures a resource is not deleted when the stack is deleted?

A) `Snapshot`
B) `Delete`
C) `Retain`
D) `Protect`

---

### Question 21

What is Stack Drift Detection used for?

A) To track changes in template files
B) To identify differences between expected and actual resource configurations
C) To monitor stack creation progress
D) To detect unauthorized access to stacks

---

### Question 22

Which of the following resources support the `Snapshot` DeletionPolicy? (Select TWO)

A) AWS::EC2::Instance
B) AWS::RDS::DBInstance
C) AWS::S3::Bucket
D) AWS::EC2::Volume
E) AWS::Lambda::Function

---

## Section 5: Nested Stacks (Questions 23-25)

### Question 23

What is the resource type for creating a nested stack?

A) `AWS::CloudFormation::NestedStack`
B) `AWS::CloudFormation::Stack`
C) `AWS::Stack::Nested`
D) `AWS::CFN::Stack`

---

### Question 24

Which property is REQUIRED when creating a nested stack resource?

A) Parameters
B) TemplateURL
C) TimeoutInMinutes
D) NotificationARNs

---

### Question 25

How do you pass outputs from a nested stack to the parent stack?

A) Using `Fn::ImportValue`
B) Using `!GetAtt NestedStackLogicalId.Outputs.OutputKey`
C) Using `!Ref NestedStackLogicalId.OutputKey`
D) Outputs are automatically available in the parent stack

---

## Section 6: StackSets (Questions 26-27)

### Question 26

What is the primary use case for CloudFormation StackSets?

A) To create stacks faster
B) To deploy stacks across multiple accounts and regions
C) To create nested stack structures
D) To automate stack updates

---

### Question 27

Which permission model allows StackSets to automatically create the necessary IAM roles?

A) Self-managed permissions
B) Service-managed permissions
C) Cross-account permissions
D) Delegated permissions

---

## Section 7: AWS CDK (Questions 28-30)

### Question 28

What is AWS CDK?

A) A graphical interface for creating CloudFormation templates
B) A framework for defining cloud infrastructure in programming languages
C) A replacement for CloudFormation
D) An AWS service for deploying containers

---

### Question 29

Which CDK construct level provides the highest level of abstraction with pre-configured defaults?

A) L1 (CFN Resources)
B) L2 (Curated Constructs)
C) L3 (Patterns)
D) L4 (Solutions)

---

### Question 30

What command synthesizes a CDK app into a CloudFormation template?

A) `cdk compile`
B) `cdk build`
C) `cdk synth`
D) `cdk generate`

---

## Answers and Explanations

### Answer 1: B) Resources

**Explanation**: The Resources section is the only required section in a CloudFormation template. It defines the AWS resources that CloudFormation will create. All other sections (Parameters, Mappings, Conditions, Outputs, etc.) are optional.

---

### Answer 2: C) YAML

**Explanation**: While both JSON and YAML are supported, YAML is recommended for readability because it supports comments, has cleaner syntax, and is less verbose. Most AWS documentation examples now use YAML format.

---

### Answer 3: B) 51,200 bytes

**Explanation**: When passing the template body directly in the API call, the maximum size is 51,200 bytes (approximately 50 KB). For larger templates, you must upload them to S3 first (max 460,800 bytes or ~450 KB).

---

### Answer 4: C) All resources are automatically rolled back and deleted

**Explanation**: By default, CloudFormation uses "rollback on failure" behavior. When stack creation fails, all resources that were successfully created are deleted to return to the previous state. This can be disabled using `--disable-rollback` or `--on-failure DO_NOTHING`.

---

### Answer 5: D) Both A and B

**Explanation**: Both commands can create stacks. `aws cloudformation create-stack` is the traditional command, while `aws cloudformation deploy` is a higher-level command that can create or update stacks and handles change sets automatically.

---

### Answer 6: B) To identify the capabilities of the template

**Explanation**: `AWSTemplateFormatVersion` identifies the capabilities of the template. The only valid value is `2010-09-09`. It's optional but recommended for clarity. It doesn't affect functionality as there's only one version.

---

### Answer 7: C) Parameters

**Explanation**: Parameters enable you to input custom values to your template each time you create or update a stack. They make templates reusable by allowing runtime customization without modifying the template itself.

---

### Answer 8: C) 200

**Explanation**: CloudFormation templates can have a maximum of 200 parameters. If you need more inputs, consider using nested stacks, AWS Systems Manager Parameter Store, or consolidating related values.

---

### Answer 9: C) AWS::EC2::KeyPair::KeyName

**Explanation**: `AWS::EC2::KeyPair::KeyName` is an AWS-specific parameter type that validates the key pair exists in the account and region. It also provides a dropdown list in the AWS Console for user convenience.

---

### Answer 10: C) To create static key-value lookups based on known values

**Explanation**: Mappings provide static key-value lookups based on known values (like region-specific AMI IDs). Unlike parameters, mappings are defined at template creation time and cannot be modified during stack operations.

---

### Answer 11: A) Conditions can reference other conditions

**Explanation**: Conditions can reference other conditions using condition functions like `Fn::And`, `Fn::Or`, and `Fn::Not`. They can also reference parameters and mappings. Conditions are evaluated at stack creation and update time.

---

### Answer 12: C) 200

**Explanation**: CloudFormation templates can have a maximum of 200 outputs. Outputs can be used to return information about resources, export values for cross-stack references, or display information in the console.

---

### Answer 13: C) Ref

**Explanation**: The `Ref` function returns the value of a parameter or the physical ID of a resource (like an EC2 instance ID or S3 bucket name). `Fn::GetAtt` returns specific attributes of resources.

---

### Answer 14: B) The public IP address of the instance

**Explanation**: `!GetAtt MyEC2Instance.PublicIp` returns the public IP address attribute of the EC2 instance. Each resource type has specific attributes that can be retrieved using `GetAtt`. Common EC2 attributes include AvailabilityZone, PrivateDnsName, PublicDnsName, and PrivateIp.

---

### Answer 15: B) Fn::Sub

**Explanation**: `Fn::Sub` (substitute) performs variable substitution in strings. It can substitute references (${AWS::StackName}) and can use a mapping of variables. `Fn::Join` concatenates values with a delimiter but doesn't perform substitution.

---

### Answer 16: B) !If [ConditionName, TrueValue, FalseValue]

**Explanation**: `Fn::If` takes three parameters: the condition name, the value if true, and the value if false. Both the true and false values are required. You can use `AWS::NoValue` as a pseudo parameter to not set a value.

---

### Answer 17: C) Fn::ImportValue

**Explanation**: `Fn::ImportValue` retrieves an exported output value from another stack. The exporting stack must define an Export in its Outputs section. This enables cross-stack references.

---

### Answer 18: B) The Availability Zones in the current region

**Explanation**: When `Fn::GetAZs` is passed an empty string (`!GetAZs ''` or `!GetAZs ""`), it returns all Availability Zones in the current region where the stack is being created. You can also pass a specific region name.

---

### Answer 19: B) To preview changes before executing them

**Explanation**: Change Sets allow you to preview how proposed changes will impact your running resources before implementing them. This helps identify potentially disruptive changes (like resource replacements) before they occur.

---

### Answer 20: C) Retain

**Explanation**: `DeletionPolicy: Retain` preserves the resource when the stack is deleted. `Snapshot` creates a snapshot before deletion (for supported resources). `Delete` is the default behavior. `Protect` is not a valid DeletionPolicy.

---

### Answer 21: B) To identify differences between expected and actual resource configurations

**Explanation**: Drift detection identifies when the actual configuration of stack resources differs from the expected configuration defined in the template. This can happen when resources are modified outside of CloudFormation (manually or by other tools).

---

### Answer 22: B) AWS::RDS::DBInstance and D) AWS::EC2::Volume

**Explanation**: The `Snapshot` DeletionPolicy is supported by resources that can create snapshots: RDS instances (DB snapshots), EC2 volumes (EBS snapshots), Redshift clusters, Neptune clusters, and ElastiCache clusters. S3 buckets and Lambda functions don't support snapshots.

---

### Answer 23: B) AWS::CloudFormation::Stack

**Explanation**: Nested stacks are created using the `AWS::CloudFormation::Stack` resource type. Despite the naming, there is no `AWS::CloudFormation::NestedStack` type. The same resource type is used for both root and nested stacks.

---

### Answer 24: B) TemplateURL

**Explanation**: `TemplateURL` is the only required property for `AWS::CloudFormation::Stack`. It must point to a template stored in S3. Parameters, TimeoutInMinutes, and NotificationARNs are optional properties.

---

### Answer 25: B) Using !GetAtt NestedStackLogicalId.Outputs.OutputKey

**Explanation**: To access outputs from a nested stack, use `!GetAtt NestedStackLogicalId.Outputs.OutputKey`. The format is the logical ID of the nested stack resource, followed by `.Outputs.`, followed by the output key name from the nested template.

---

### Answer 26: B) To deploy stacks across multiple accounts and regions

**Explanation**: StackSets extend CloudFormation's capability by enabling you to create, update, or delete stacks across multiple accounts and regions with a single operation. This is essential for multi-account environments and organizational governance.

---

### Answer 27: B) Service-managed permissions

**Explanation**: Service-managed permissions (integrated with AWS Organizations) allow StackSets to automatically create the necessary IAM roles in target accounts. Self-managed permissions require you to manually create IAM roles in each account.

---

### Answer 28: B) A framework for defining cloud infrastructure in programming languages

**Explanation**: AWS CDK (Cloud Development Kit) is an open-source framework that allows you to define cloud infrastructure using familiar programming languages (TypeScript, Python, Java, C#, Go). CDK synthesizes your code into CloudFormation templates.

---

### Answer 29: C) L3 (Patterns)

**Explanation**: L3 constructs (Patterns) provide the highest abstraction level with pre-configured, opinionated defaults for common architectures. L1 constructs are direct CloudFormation mappings, L2 constructs provide sensible defaults for individual resources, and L4 doesn't exist in CDK terminology.

---

### Answer 30: C) cdk synth

**Explanation**: The `cdk synth` command synthesizes (converts) your CDK application code into a CloudFormation template. The output is placed in the `cdk.out` directory by default. `cdk deploy` both synthesizes and deploys the stack.

---

## Score Interpretation

| Score | Rating | Recommendation |
|-------|--------|----------------|
| 27-30 | Expert | Excellent! You're ready for advanced CloudFormation topics |
| 24-26 | Proficient | Good understanding. Review missed topics |
| 20-23 | Intermediate | Solid foundation. Review sections with errors |
| 15-19 | Developing | Need more practice. Re-read relevant lessons |
| Below 15 | Beginner | Start from the beginning of the module |

---

## Next Steps

Based on your quiz results:

1. **Review weak areas** - Go back to the relevant lessons for topics you missed
2. **Practice with hands-on labs** - Apply concepts in real CloudFormation templates
3. **Try the advanced labs** - Nested stacks, StackSets, and CDK exercises
4. **Explore real-world templates** - Study AWS Quick Starts and sample templates

---

**Continue to**: [Hands-on Lab](./11-hands-on-lab.md)
