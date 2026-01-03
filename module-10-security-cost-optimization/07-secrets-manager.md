# AWS Secrets Manager

## Introduction

AWS Secrets Manager is a fully managed service that helps you protect access to your applications, services, and IT resources without the upfront cost and complexity of deploying and maintaining secrets management infrastructure.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AWS Secrets Manager Overview                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌───────────────────────┐    ┌─────────────────────┐   │
│  │ Application │───▶│   Secrets Manager     │───▶│   KMS Encryption    │   │
│  │             │    │                       │    │                     │   │
│  │ • Lambda    │    │ • API Credentials     │    │ • Customer CMK      │   │
│  │ • EC2       │    │ • Database Passwords  │    │ • AWS Managed Key   │   │
│  │ • ECS       │    │ • OAuth Tokens        │    │                     │   │
│  │ • EKS       │    │ • SSH Keys            │    └─────────────────────┘   │
│  └─────────────┘    │ • Certificates        │                              │
│                     └───────────────────────┘                              │
│                               │                                            │
│                               ▼                                            │
│                     ┌───────────────────────┐                              │
│                     │  Automatic Rotation   │                              │
│                     │                       │                              │
│                     │ • Lambda Functions    │                              │
│                     │ • RDS Integration     │                              │
│                     │ • Custom Rotation     │                              │
│                     └───────────────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## What is Secrets Manager?

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Secret Storage** | Securely store and manage secrets (credentials, API keys, tokens) |
| **Automatic Rotation** | Built-in rotation for RDS, DocumentDB, Redshift; custom rotation via Lambda |
| **Fine-grained Access Control** | IAM policies and resource-based policies for access management |
| **Encryption** | All secrets encrypted at rest using KMS |
| **Versioning** | Automatic version tracking for secrets |
| **Cross-Region Replication** | Replicate secrets across multiple AWS regions |
| **Audit** | CloudTrail integration for auditing secret access |

### Secrets Manager Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Secrets Manager Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Application Layer                                                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                       │
│   │ Lambda  │  │   EC2   │  │   ECS   │  │   EKS   │                       │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                       │
│        │            │            │            │                             │
│        └────────────┴─────┬──────┴────────────┘                            │
│                           │                                                 │
│                           ▼                                                 │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │                    Secrets Manager API                               │ │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │ │
│   │  │ GetSecret   │  │ CreateSecret│  │RotateSecret │  │ PutSecret  │  │ │
│   │  │ Value       │  │             │  │             │  │ Value      │  │ │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                           │                                                 │
│                           ▼                                                 │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │                    Secret Storage Layer                              │ │
│   │                                                                      │ │
│   │  ┌────────────────────┐    ┌────────────────────────────────────┐   │ │
│   │  │   Secret Data      │    │           KMS Integration          │   │ │
│   │  │                    │    │                                    │   │ │
│   │  │ • Encrypted Value  │◀──▶│ • Envelope Encryption             │   │ │
│   │  │ • Metadata         │    │ • Customer Managed Keys           │   │ │
│   │  │ • Version IDs      │    │ • Automatic Key Rotation          │   │ │
│   │  └────────────────────┘    └────────────────────────────────────┘   │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   Rotation Layer                                                            │
│   ┌──────────────────────────────────────────────────────────────────────┐ │
│   │              Lambda Rotation Function                                │ │
│   │  ┌──────────────────────────────────────────────────────────────┐   │ │
│   │  │  Step 1: Create Secret  →  Step 2: Set Secret                │   │ │
│   │  │           ↑                           ↓                       │   │ │
│   │  │  Step 4: Finish Secret  ←  Step 3: Test Secret               │   │ │
│   │  └──────────────────────────────────────────────────────────────┘   │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Storing and Retrieving Secrets

### Creating Secrets via Console

1. Navigate to AWS Secrets Manager console
2. Click "Store a new secret"
3. Choose secret type:
   - Credentials for Amazon RDS database
   - Credentials for other database
   - Other type of secret (API keys, tokens, etc.)
4. Enter secret key/value pairs
5. Select encryption key (default or custom CMK)
6. Name your secret and add description
7. Configure automatic rotation (optional)
8. Review and store

### Creating Secrets via CLI

```bash
# Create a simple secret
aws secretsmanager create-secret \
    --name "prod/myapp/api-key" \
    --description "API key for external service" \
    --secret-string '{"api_key":"abc123xyz","api_endpoint":"https://api.example.com"}'

# Create secret with custom KMS key
aws secretsmanager create-secret \
    --name "prod/database/credentials" \
    --description "Production database credentials" \
    --kms-key-id "alias/my-secrets-key" \
    --secret-string '{"username":"admin","password":"SuperSecret123!","host":"db.example.com","port":"5432"}'

# Create secret from file
aws secretsmanager create-secret \
    --name "prod/certificates/ssl" \
    --secret-binary fileb://certificate.pem

# Create secret with tags
aws secretsmanager create-secret \
    --name "prod/app/config" \
    --secret-string '{"setting1":"value1","setting2":"value2"}' \
    --tags Key=Environment,Value=Production Key=Application,Value=MyApp
```

### Retrieving Secrets

```bash
# Get current secret value
aws secretsmanager get-secret-value \
    --secret-id "prod/myapp/api-key"

# Get specific version by stage
aws secretsmanager get-secret-value \
    --secret-id "prod/myapp/api-key" \
    --version-stage AWSPREVIOUS

# Get specific version by ID
aws secretsmanager get-secret-value \
    --secret-id "prod/myapp/api-key" \
    --version-id "a1b2c3d4-5678-90ab-cdef-EXAMPLE11111"

# List all secrets
aws secretsmanager list-secrets

# Describe a secret (metadata only)
aws secretsmanager describe-secret \
    --secret-id "prod/myapp/api-key"
```

### Retrieving Secrets in Applications

#### Python (Boto3)

```python
import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="us-east-1"):
    """
    Retrieve a secret from AWS Secrets Manager
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'DecryptionFailureException':
            raise Exception("Cannot decrypt secret using provided KMS key")
        elif error_code == 'InternalServiceErrorException':
            raise Exception("Internal server error")
        elif error_code == 'InvalidParameterException':
            raise Exception("Invalid parameter provided")
        elif error_code == 'InvalidRequestException':
            raise Exception("Invalid request")
        elif error_code == 'ResourceNotFoundException':
            raise Exception(f"Secret {secret_name} not found")
        else:
            raise e

    # Parse and return the secret
    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    else:
        # Binary secret
        return get_secret_value_response['SecretBinary']

# Usage example
if __name__ == "__main__":
    # Get database credentials
    db_creds = get_secret("prod/database/credentials")
    print(f"Database Host: {db_creds['host']}")
    print(f"Database User: {db_creds['username']}")

    # Use credentials to connect
    import psycopg2

    connection = psycopg2.connect(
        host=db_creds['host'],
        port=db_creds['port'],
        database=db_creds.get('database', 'mydb'),
        user=db_creds['username'],
        password=db_creds['password']
    )
```

#### Python with Caching

```python
import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

# Install: pip install aws-secretsmanager-caching

# Create cache configuration
cache_config = SecretCacheConfig(
    max_cache_size=1000,  # Maximum secrets to cache
    exception_retry_delay_base=1,  # Base delay for retries
    exception_retry_growth_factor=2,  # Growth factor for retry delays
    exception_retry_delay_max=3600,  # Maximum retry delay
    default_secret_refresh_interval=3600,  # Refresh interval in seconds
    default_secret_version_stage_refresh_interval=3600  # Version stage refresh
)

# Create the cache
client = boto3.client('secretsmanager')
cache = SecretCache(config=cache_config, client=client)

# Get secret (will be cached)
secret_string = cache.get_secret_string("prod/myapp/api-key")
secret_dict = json.loads(secret_string)
```

#### Node.js

```javascript
const {
    SecretsManagerClient,
    GetSecretValueCommand
} = require("@aws-sdk/client-secrets-manager");

const client = new SecretsManagerClient({ region: "us-east-1" });

async function getSecret(secretName) {
    try {
        const command = new GetSecretValueCommand({
            SecretId: secretName
        });

        const response = await client.send(command);

        if ('SecretString' in response) {
            return JSON.parse(response.SecretString);
        } else {
            // Binary secret
            const buff = Buffer.from(response.SecretBinary, 'base64');
            return buff.toString('ascii');
        }
    } catch (error) {
        console.error('Error retrieving secret:', error);
        throw error;
    }
}

// Usage
(async () => {
    const dbCreds = await getSecret('prod/database/credentials');
    console.log(`Database host: ${dbCreds.host}`);
})();
```

#### Java

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueRequest;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueResponse;
import com.google.gson.Gson;
import java.util.Map;

public class SecretsManagerExample {

    public static Map<String, String> getSecret(String secretName) {
        Region region = Region.US_EAST_1;

        SecretsManagerClient client = SecretsManagerClient.builder()
            .region(region)
            .build();

        GetSecretValueRequest request = GetSecretValueRequest.builder()
            .secretId(secretName)
            .build();

        GetSecretValueResponse response = client.getSecretValue(request);

        String secret = response.secretString();
        Gson gson = new Gson();
        return gson.fromJson(secret, Map.class);
    }

    public static void main(String[] args) {
        Map<String, String> credentials = getSecret("prod/database/credentials");
        System.out.println("Database: " + credentials.get("host"));
    }
}
```

#### Lambda Function Example

```python
import json
import boto3
import os

# Initialize client outside handler for connection reuse
secrets_client = boto3.client('secretsmanager')

# Cache secrets in memory (Lambda container reuse)
_secrets_cache = {}

def get_cached_secret(secret_name):
    """Get secret with simple caching"""
    if secret_name not in _secrets_cache:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        _secrets_cache[secret_name] = json.loads(response['SecretString'])
    return _secrets_cache[secret_name]

def lambda_handler(event, context):
    # Get database credentials
    db_secret_name = os.environ.get('DB_SECRET_NAME', 'prod/database/credentials')

    try:
        credentials = get_cached_secret(db_secret_name)

        # Use credentials to connect to database
        # ... your database logic here ...

        return {
            'statusCode': 200,
            'body': json.dumps('Successfully connected to database')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
```

## Automatic Rotation

### Rotation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Secret Rotation Process                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    Four-Step Rotation Process                        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   Step 1: createSecret                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Generate new secret value                                         │  │
│   │  • Store with AWSPENDING staging label                               │  │
│   │  • Original secret remains AWSCURRENT                                │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│   Step 2: setSecret                                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Update credentials in target service (e.g., RDS)                  │  │
│   │  • New credentials now active on database                            │  │
│   │  • Both old and new credentials work                                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│   Step 3: testSecret                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Verify new credentials work                                       │  │
│   │  • Attempt connection with AWSPENDING secret                         │  │
│   │  • If fails, rotation stops here                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│   Step 4: finishSecret                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  • Move AWSCURRENT label to new secret                               │  │
│   │  • Move AWSPREVIOUS label to old secret                              │  │
│   │  • Applications automatically get new credentials                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Rotation Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Rotation Strategies                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Strategy 1: Single-User Rotation                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌──────────┐     ┌──────────────┐     ┌──────────────────┐        │   │
│  │  │  Secret  │────▶│   Lambda     │────▶│     Database     │        │   │
│  │  │ (1 user) │     │   Rotation   │     │                  │        │   │
│  │  └──────────┘     └──────────────┘     │ Single DB User   │        │   │
│  │                                        │ (password change)│        │   │
│  │                                        └──────────────────┘        │   │
│  │                                                                     │   │
│  │  Pros: Simple setup                                                 │   │
│  │  Cons: Brief unavailability during rotation                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Strategy 2: Alternating-Users Rotation (Recommended)                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌──────────┐     ┌──────────────┐     ┌──────────────────┐        │   │
│  │  │  Secret  │────▶│   Lambda     │────▶│     Database     │        │   │
│  │  │ (2 users)│     │   Rotation   │     │                  │        │   │
│  │  │          │     │              │     │ User A (active)  │        │   │
│  │  │ User A   │     │ Alternates   │     │ User B (standby) │        │   │
│  │  │ User B   │     │ between them │     │                  │        │   │
│  │  └──────────┘     └──────────────┘     └──────────────────┘        │   │
│  │                                                                     │   │
│  │  Pros: Zero downtime, always one valid credential                   │   │
│  │  Cons: Requires two database users                                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Enabling Rotation for RDS

```bash
# Enable rotation with AWS-managed rotation function
aws secretsmanager rotate-secret \
    --secret-id "prod/database/credentials" \
    --rotation-lambda-arn "arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSMySQLRotation" \
    --rotation-rules '{"AutomaticallyAfterDays": 30}'

# Create secret with rotation enabled (for RDS)
aws secretsmanager create-secret \
    --name "prod/rds/mysql-credentials" \
    --secret-string '{"username":"admin","password":"Initial123!","engine":"mysql","host":"mydb.cluster-xxx.us-east-1.rds.amazonaws.com","port":3306,"dbname":"myapp"}'

# Enable rotation using managed rotation
aws secretsmanager rotate-secret \
    --secret-id "prod/rds/mysql-credentials" \
    --rotation-lambda-arn "arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSMySQLSingleUserRotation" \
    --rotation-rules '{"AutomaticallyAfterDays": 7}'
```

### Custom Rotation Lambda Function

```python
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Custom rotation Lambda function template
    """
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    # Setup the client
    service_client = boto3.client('secretsmanager')

    # Get the secret metadata
    metadata = service_client.describe_secret(SecretId=arn)

    # Ensure the version is staged correctly
    versions = metadata['VersionIdsToStages']
    if token not in versions:
        logger.error(f"Secret version {token} has no stage for rotation")
        raise ValueError(f"Secret version {token} has no stage")

    if "AWSCURRENT" in versions[token]:
        logger.info(f"Secret version {token} already set as AWSCURRENT")
        return
    elif "AWSPENDING" not in versions[token]:
        logger.error(f"Secret version {token} not set as AWSPENDING")
        raise ValueError(f"Secret version {token} not AWSPENDING")

    # Route to the appropriate step
    if step == "createSecret":
        create_secret(service_client, arn, token)
    elif step == "setSecret":
        set_secret(service_client, arn, token)
    elif step == "testSecret":
        test_secret(service_client, arn, token)
    elif step == "finishSecret":
        finish_secret(service_client, arn, token)
    else:
        raise ValueError(f"Invalid step: {step}")

def create_secret(service_client, arn, token):
    """
    Create a new secret version with a new password
    """
    # Get current secret
    current_secret = service_client.get_secret_value(
        SecretId=arn,
        VersionStage="AWSCURRENT"
    )
    secret_dict = json.loads(current_secret['SecretString'])

    # Generate new password
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    new_password = ''.join(secrets.choice(alphabet) for _ in range(32))

    # Update the password in the secret
    secret_dict['password'] = new_password

    # Store the new version
    service_client.put_secret_value(
        SecretId=arn,
        ClientRequestToken=token,
        SecretString=json.dumps(secret_dict),
        VersionStages=['AWSPENDING']
    )
    logger.info(f"Created new secret version {token}")

def set_secret(service_client, arn, token):
    """
    Set the secret in the target service (e.g., database)
    """
    # Get the pending secret
    pending_secret = service_client.get_secret_value(
        SecretId=arn,
        VersionId=token,
        VersionStage="AWSPENDING"
    )
    secret_dict = json.loads(pending_secret['SecretString'])

    # Get the current secret for authentication
    current_secret = service_client.get_secret_value(
        SecretId=arn,
        VersionStage="AWSCURRENT"
    )
    current_dict = json.loads(current_secret['SecretString'])

    # Update password in target service
    # This example shows MySQL - adapt for your service
    import pymysql

    conn = pymysql.connect(
        host=current_dict['host'],
        user=current_dict['username'],
        password=current_dict['password'],
        database=current_dict.get('dbname', 'mysql')
    )

    with conn.cursor() as cursor:
        cursor.execute(
            f"ALTER USER '{secret_dict['username']}'@'%' "
            f"IDENTIFIED BY '{secret_dict['password']}'"
        )
    conn.commit()
    conn.close()

    logger.info(f"Set secret in target service")

def test_secret(service_client, arn, token):
    """
    Test that the new secret works
    """
    # Get the pending secret
    pending_secret = service_client.get_secret_value(
        SecretId=arn,
        VersionId=token,
        VersionStage="AWSPENDING"
    )
    secret_dict = json.loads(pending_secret['SecretString'])

    # Test connection with new credentials
    import pymysql

    try:
        conn = pymysql.connect(
            host=secret_dict['host'],
            user=secret_dict['username'],
            password=secret_dict['password'],
            database=secret_dict.get('dbname', 'mysql'),
            connect_timeout=5
        )
        conn.close()
        logger.info("Successfully tested new secret")
    except Exception as e:
        logger.error(f"Failed to test new secret: {str(e)}")
        raise

def finish_secret(service_client, arn, token):
    """
    Finish the rotation by moving labels
    """
    # Get current version
    metadata = service_client.describe_secret(SecretId=arn)
    current_version = None

    for version, stages in metadata['VersionIdsToStages'].items():
        if "AWSCURRENT" in stages:
            if version == token:
                logger.info(f"Version {token} already AWSCURRENT")
                return
            current_version = version
            break

    # Move AWSCURRENT label
    service_client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version
    )

    logger.info(f"Finished rotation, {token} is now AWSCURRENT")
```

### Rotation Lambda IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:DescribeSecret",
                "secretsmanager:GetSecretValue",
                "secretsmanager:PutSecretValue",
                "secretsmanager:UpdateSecretVersionStage"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetRandomPassword"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt",
                "kms:GenerateDataKey"
            ],
            "Resource": "arn:aws:kms:us-east-1:123456789012:key/your-key-id"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeNetworkInterfaces"
            ],
            "Resource": "*"
        }
    ]
}
```

## Integration with RDS

### Creating RDS Secret with Rotation

```bash
# Create the secret for RDS
aws secretsmanager create-secret \
    --name "prod/rds/postgres-master" \
    --description "Master credentials for production PostgreSQL" \
    --secret-string '{
        "username": "postgres",
        "password": "InitialPassword123!",
        "engine": "postgres",
        "host": "prod-db.cluster-xyz.us-east-1.rds.amazonaws.com",
        "port": 5432,
        "dbname": "production"
    }'

# Configure rotation using AWS managed rotation Lambda
aws secretsmanager rotate-secret \
    --secret-id "prod/rds/postgres-master" \
    --rotation-lambda-arn "arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSPostgreSQLRotation" \
    --rotation-rules '{"AutomaticallyAfterDays": 30}'
```

### CloudFormation Template for RDS with Secrets Manager

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'RDS with Secrets Manager rotation'

Parameters:
  Environment:
    Type: String
    Default: production

  DBInstanceClass:
    Type: String
    Default: db.t3.medium

Resources:
  # Generate master credentials
  DBMasterSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '${Environment}/rds/master-credentials'
      Description: 'RDS master credentials'
      GenerateSecretString:
        SecretStringTemplate: '{"username": "admin"}'
        GenerateStringKey: 'password'
        PasswordLength: 32
        ExcludePunctuation: false
        ExcludeCharacters: '"@/\'
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # RDS Instance
  DBInstance:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${Environment}-database'
      DBInstanceClass: !Ref DBInstanceClass
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: !Sub '{{resolve:secretsmanager:${DBMasterSecret}:SecretString:username}}'
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DBMasterSecret}:SecretString:password}}'
      AllocatedStorage: 100
      StorageType: gp3
      StorageEncrypted: true
      MultiAZ: true
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: 7
      DeletionProtection: true
      Tags:
        - Key: Environment
          Value: !Ref Environment

  # Attach secret to RDS instance
  DBSecretAttachment:
    Type: AWS::SecretsManager::SecretTargetAttachment
    Properties:
      SecretId: !Ref DBMasterSecret
      TargetId: !Ref DBInstance
      TargetType: AWS::RDS::DBInstance

  # Rotation schedule
  DBSecretRotation:
    Type: AWS::SecretsManager::RotationSchedule
    DependsOn: DBSecretAttachment
    Properties:
      SecretId: !Ref DBMasterSecret
      HostedRotationLambda:
        RotationType: MySQLSingleUser
        VpcSecurityGroupIds: !Ref LambdaSecurityGroup
        VpcSubnetIds: !Join [',', [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
      RotationRules:
        AutomaticallyAfterDays: 30

  # Security group for database
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: 'Security group for RDS'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref ApplicationSecurityGroup

Outputs:
  SecretArn:
    Description: 'Secret ARN for database credentials'
    Value: !Ref DBMasterSecret

  DBEndpoint:
    Description: 'Database endpoint'
    Value: !GetAtt DBInstance.Endpoint.Address
```

## Secrets Manager vs Parameter Store

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               Secrets Manager vs Systems Manager Parameter Store            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Feature              │  Secrets Manager         │  Parameter Store         │
│  ─────────────────────┼──────────────────────────┼──────────────────────────│
│  Purpose              │  Secrets (credentials,   │  Configuration data,     │
│                       │  API keys, certificates) │  parameters, secrets     │
│                       │                          │                          │
│  Automatic Rotation   │  ✓ Built-in support      │  ✗ Manual only           │
│                       │                          │                          │
│  Cross-Account Access │  ✓ Resource policies     │  ✓ Via RAM sharing       │
│                       │                          │                          │
│  Cross-Region         │  ✓ Secret replication    │  ✗ Not supported         │
│  Replication          │                          │                          │
│                       │                          │                          │
│  Versioning           │  ✓ Automatic staging     │  ✓ Basic versioning      │
│                       │  labels                  │                          │
│                       │                          │                          │
│  Encryption           │  ✓ Always encrypted      │  ✓ Optional (Secure      │
│                       │  (KMS required)          │  String uses KMS)        │
│                       │                          │                          │
│  Pricing              │  $0.40/secret/month +    │  Standard: Free          │
│                       │  $0.05/10K API calls     │  Advanced: $0.05/param   │
│                       │                          │                          │
│  Max Size             │  64 KB                   │  Standard: 4 KB          │
│                       │                          │  Advanced: 8 KB          │
│                       │                          │                          │
│  Parameter Policies   │  ✓ Resource policies     │  ✓ Advanced tier only    │
│                       │                          │                          │
│  Integration          │  RDS, DocumentDB,        │  EC2, ECS, Lambda,       │
│                       │  Redshift rotation       │  CloudFormation          │
│                       │                          │                          │
│  Hierarchy            │  Flat with naming        │  ✓ Path-based hierarchy  │
│                       │  conventions             │  (/app/prod/db/password) │
│                       │                          │                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Decision Guide

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    When to Use Which Service?                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Use Secrets Manager when:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • You need automatic credential rotation                            │   │
│  │  • Storing database credentials for RDS/Aurora/Redshift              │   │
│  │  • Managing API keys that need periodic rotation                     │   │
│  │  • Requiring cross-region secret replication                         │   │
│  │  • Secrets need fine-grained resource-based policies                 │   │
│  │  • Cost is not a primary concern                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Use Parameter Store when:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Storing configuration values (feature flags, URLs, settings)      │   │
│  │  • Cost optimization is important (Standard tier is free)            │   │
│  │  • Hierarchical parameter organization is needed                     │   │
│  │  • Storing non-sensitive configuration data                          │   │
│  │  • Integration with CloudFormation references                        │   │
│  │  • You don't need automatic rotation                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Use Both Together:                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Secrets Manager: Database credentials, API keys                   │   │
│  │  • Parameter Store: Application config, feature flags, endpoints     │   │
│  │                                                                      │   │
│  │  Example Architecture:                                               │   │
│  │  /myapp/prod/                                                        │   │
│  │    config/                                                           │   │
│  │      feature-flags (Parameter Store - String)                        │   │
│  │      api-endpoint (Parameter Store - String)                         │   │
│  │    secrets/                                                          │   │
│  │      db-password (Secrets Manager - with rotation)                   │   │
│  │      api-key (Secrets Manager - with rotation)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Best Practices

### Security Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Secrets Manager Best Practices                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Naming Conventions                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Use hierarchical naming:                                            │   │
│  │  • {environment}/{application}/{secret-type}                         │   │
│  │  • prod/myapp/database-credentials                                   │   │
│  │  • staging/payment-service/stripe-api-key                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. Encryption                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Use customer-managed KMS keys for sensitive secrets               │   │
│  │  • Separate KMS keys per environment                                 │   │
│  │  • Enable automatic KMS key rotation                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. Access Control                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Use least privilege IAM policies                                  │   │
│  │  • Implement resource-based policies for cross-account access        │   │
│  │  • Use IAM conditions to restrict access by IP, VPC, or time         │   │
│  │  • Enable MFA for sensitive operations                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. Rotation                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Enable automatic rotation for all credentials                     │   │
│  │  • Use alternating users strategy for zero downtime                  │   │
│  │  • Test rotation in staging before production                        │   │
│  │  • Set appropriate rotation intervals (30-90 days)                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  5. Monitoring and Auditing                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Enable CloudTrail for all Secrets Manager API calls               │   │
│  │  • Set up CloudWatch alarms for failed access attempts               │   │
│  │  • Monitor rotation failures                                         │   │
│  │  • Review access logs regularly                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### IAM Policy Examples

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowReadProductionSecrets",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/*",
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalTag/Environment": "production"
                }
            }
        },
        {
            "Sid": "DenyAccessFromOutsideVPC",
            "Effect": "Deny",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "*",
            "Condition": {
                "StringNotEquals": {
                    "aws:SourceVpc": "vpc-12345678"
                }
            }
        }
    ]
}
```

### Resource-Based Policy for Cross-Account Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCrossAccountAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::987654321098:role/ApplicationRole"
            },
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "secretsmanager:VersionStage": "AWSCURRENT"
                }
            }
        }
    ]
}
```

## Hands-on Examples

### Example 1: Complete Secret Lifecycle

```bash
#!/bin/bash
# Complete Secrets Manager workflow

# 1. Create a secret
aws secretsmanager create-secret \
    --name "demo/application/config" \
    --description "Demo application configuration" \
    --secret-string '{
        "database_url": "postgres://localhost:5432/mydb",
        "api_key": "demo-api-key-12345",
        "feature_flag": true
    }' \
    --tags Key=Environment,Value=Demo Key=Team,Value=DevOps

# 2. Retrieve the secret
echo "Current secret value:"
aws secretsmanager get-secret-value \
    --secret-id "demo/application/config" \
    --query 'SecretString' \
    --output text | jq .

# 3. Update the secret
aws secretsmanager put-secret-value \
    --secret-id "demo/application/config" \
    --secret-string '{
        "database_url": "postgres://prod-db:5432/mydb",
        "api_key": "new-api-key-67890",
        "feature_flag": true,
        "new_setting": "added"
    }'

# 4. Get previous version
echo "Previous secret value:"
aws secretsmanager get-secret-value \
    --secret-id "demo/application/config" \
    --version-stage AWSPREVIOUS \
    --query 'SecretString' \
    --output text | jq .

# 5. List secret versions
aws secretsmanager list-secret-version-ids \
    --secret-id "demo/application/config"

# 6. Add resource policy
aws secretsmanager put-resource-policy \
    --secret-id "demo/application/config" \
    --resource-policy '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::123456789012:role/AppRole"},
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "*"
        }]
    }'

# 7. Delete secret (with recovery window)
aws secretsmanager delete-secret \
    --secret-id "demo/application/config" \
    --recovery-window-in-days 7

# 8. Restore deleted secret (if within recovery window)
# aws secretsmanager restore-secret --secret-id "demo/application/config"
```

### Example 2: ECS Task with Secrets Manager

```yaml
# ECS Task Definition with Secrets Manager
AWSTemplateFormatVersion: '2010-09-09'
Description: 'ECS Task using Secrets Manager'

Resources:
  # Secret for database credentials
  DatabaseSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: !Sub '${AWS::StackName}/database-credentials'
      GenerateSecretString:
        SecretStringTemplate: '{"username": "appuser"}'
        GenerateStringKey: 'password'
        PasswordLength: 32
        ExcludeCharacters: '"@/\'

  # ECS Task Execution Role
  TaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
      Policies:
        - PolicyName: SecretsManagerAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - secretsmanager:GetSecretValue
                Resource: !Ref DatabaseSecret
              - Effect: Allow
                Action:
                  - kms:Decrypt
                Resource: !Sub 'arn:aws:kms:${AWS::Region}:${AWS::AccountId}:key/*'
                Condition:
                  StringEquals:
                    kms:ViaService: !Sub 'secretsmanager.${AWS::Region}.amazonaws.com'

  # ECS Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: my-application
      Cpu: '256'
      Memory: '512'
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/my-app:latest'
          Essential: true
          Secrets:
            - Name: DB_USERNAME
              ValueFrom: !Sub '${DatabaseSecret}:username::'
            - Name: DB_PASSWORD
              ValueFrom: !Sub '${DatabaseSecret}:password::'
          Environment:
            - Name: DB_HOST
              Value: !Ref DatabaseEndpoint
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: app
```

### Example 3: Lambda with Secrets Manager Layer

```python
# Lambda function using Secrets Manager caching layer
import json
import os

# Use AWS Parameters and Secrets Lambda Extension
# Extension automatically fetches and caches secrets

def lambda_handler(event, context):
    """
    Lambda function using Secrets Manager Extension

    The extension exposes secrets via localhost HTTP endpoint
    """
    import urllib.request

    secret_name = os.environ['SECRET_NAME']
    headers = {
        'X-Aws-Parameters-Secrets-Token': os.environ.get('AWS_SESSION_TOKEN', '')
    }

    # Fetch from extension cache
    secrets_extension_endpoint = (
        f"http://localhost:2773/secretsmanager/get?"
        f"secretId={secret_name}"
    )

    req = urllib.request.Request(
        secrets_extension_endpoint,
        headers=headers
    )

    with urllib.request.urlopen(req) as response:
        secret_response = json.loads(response.read().decode())
        secret_value = json.loads(secret_response['SecretString'])

    # Use the secret
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully retrieved secret',
            'username': secret_value.get('username', 'unknown')
        })
    }
```

## Monitoring and Troubleshooting

### CloudWatch Metrics

```bash
# Create CloudWatch alarm for rotation failures
aws cloudwatch put-metric-alarm \
    --alarm-name "SecretsManager-RotationFailure" \
    --alarm-description "Alert when secret rotation fails" \
    --metric-name "RotationFailed" \
    --namespace "AWS/SecretsManager" \
    --statistic Sum \
    --period 3600 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions "arn:aws:sns:us-east-1:123456789012:alerts"
```

### CloudTrail Events to Monitor

| Event Name | Description |
|------------|-------------|
| GetSecretValue | Secret value retrieved |
| CreateSecret | New secret created |
| DeleteSecret | Secret deleted |
| RotateSecret | Rotation initiated |
| PutSecretValue | Secret value updated |
| UpdateSecret | Secret metadata updated |

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Access Denied | Missing IAM permissions | Add secretsmanager:GetSecretValue permission |
| KMS Decrypt Error | Missing KMS permissions | Add kms:Decrypt permission for the secret's KMS key |
| Rotation Failed | Lambda timeout or network issues | Check Lambda VPC config and increase timeout |
| Secret Not Found | Wrong region or deleted | Verify region and check for deletion |
| Version Not Found | Invalid version stage | Use AWSCURRENT or AWSPREVIOUS |

## Summary

AWS Secrets Manager provides a comprehensive solution for managing sensitive information:

1. **Secure Storage**: All secrets encrypted with KMS
2. **Automatic Rotation**: Built-in support for RDS, custom rotation via Lambda
3. **Fine-grained Access**: IAM and resource policies for access control
4. **Versioning**: Automatic version management with staging labels
5. **Integration**: Native support for AWS services (RDS, ECS, Lambda)
6. **Auditing**: CloudTrail integration for compliance

**Key Takeaways**:
- Use Secrets Manager for credentials that need rotation
- Implement caching in applications to reduce API calls and costs
- Use resource policies for cross-account access
- Monitor rotation status with CloudWatch alarms
- Choose between Secrets Manager and Parameter Store based on requirements
