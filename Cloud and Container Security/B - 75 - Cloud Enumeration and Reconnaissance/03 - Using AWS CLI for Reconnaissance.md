---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.03 Using AWS CLI for Reconnaissance"
---

# Using AWS CLI for Reconnaissance

## 1. Introduction to AWS CLI in VAPT

The AWS Command Line Interface (CLI) is the most fundamental tool for interacting with Amazon Web Services. For a penetration tester, gaining access to AWS credentials (an Access Key ID and Secret Access Key) is equivalent to obtaining a shell on a traditional server. Once credentials are in hand, the AWS CLI becomes the primary weapon for enumerating the cloud environment, discovering privileges, and identifying lateral movement opportunities.

The reconnaissance phase using the AWS CLI focuses on answering three critical questions:
1. **Who am I?** (What identity do these credentials belong to?)
2. **What can I do?** (What IAM permissions are attached to this identity?)
3. **What is out there?** (What resources exist in the AWS account?)

## 2. Architecture and Attack Flow

```mermaid
sequenceDiagram
    participant Attacker as Attacker / VAPT Professional
    participant CLI as AWS CLI Configuration (~/.aws/credentials)
    participant API as AWS Cloud API / IAM (Target Account)

    Attacker->>CLI: 1. Obtain leaked credentials (GitHub, SSRF, S3 leak)
    Attacker->>CLI: 2. Configure AWS CLI profile
    Attacker->>API: 3. aws sts get-caller-identity
    API-->>Attacker: 4. Return Account ID, User ARN
    Attacker->>API: 5. aws iam list-user-policies
    Attacker->>API: 6. Enumerate EC2, S3, RDS
```

## 3. The "How": Detailed Methodology

### Step 1: Configuration
When you find AWS credentials, you configure them locally using `aws configure`.

```bash
$ aws configure --profile target
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```
This creates entries in `~/.aws/credentials` and `~/.aws/config`.

### Step 2: "Who Am I?"
The very first command you should run is `sts get-caller-identity`. This is the AWS equivalent of `whoami`.

```bash
$ aws sts get-caller-identity --profile target
```

Example Output:
```json
{
    "UserId": "AIDAJQABLZS4A3QDU576Q",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/dev-john"
}
```
From this output, we know the target account ID (`123456789012`) and that we are operating as an IAM User named `dev-john`.

### Step 3: "What Can I Do?"
AWS permissions are notoriously difficult to enumerate perfectly because you cannot always query your own permissions unless you have specific IAM read access.

If you have `iam:ListAttachedUserPolicies` and `iam:ListUserPolicies`:
```bash
# List inline policies
$ aws iam list-user-policies --user-name dev-john --profile target

# List attached managed policies
$ aws iam list-attached-user-policies --user-name dev-john --profile target
```

Example Output for Attached Policies:
```json
{
    "AttachedPolicies": [
        {
            "PolicyName": "AmazonEC2ReadOnlyAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
        },
        {
            "PolicyName": "CustomS3AdminPolicy",
            "PolicyArn": "arn:aws:iam::123456789012:policy/CustomS3AdminPolicy"
        }
    ]
}
```

### Step 4: "What Is Out There?" (Resource Enumeration)

#### Enumerating S3 Buckets
```bash
$ aws s3 ls --profile target
2023-01-01 12:00:00 prod-database-backups-123
2023-01-02 12:00:00 dev-assets-bucket
```

#### Enumerating EC2 Instances
To find running servers, their IP addresses, and the IAM Roles attached to them.
```bash
$ aws ec2 describe-instances --region us-east-1 --profile target
```
*Tip: Always check multiple regions! Resources can be deployed in any of the 20+ AWS regions.*

#### Enumerating Lambda Functions
Lambda functions often contain hardcoded credentials or vulnerable code.
```bash
$ aws lambda list-functions --region us-east-1 --profile target
```

## 4. Deep Dive: Extracting EC2 User Data

EC2 instances often have "User Data" scripts that run when the instance boots. These scripts frequently contain hardcoded passwords, database credentials, or API keys.

```bash
# 1. Get the instance ID
$ aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId' --output text

# 2. Get the user data for that instance
$ aws ec2 describe-instance-attribute --instance-id i-0abcd1234efgh5678 --attribute userData

# 3. Decode the base64 output
$ echo "YmFzaCBzY3JpcHQgaGVyZQ==" | base64 -d
```

## 5. Tools of the Trade (Automated CLI Wrappers)

Manually running AWS CLI commands is tedious. Pentesters use automated frameworks that wrap the CLI to rapidly enumerate environments:
- **Pacu**: The AWS exploitation framework. Features modules for enumeration, privilege escalation, and exfiltration.
- **ScoutSuite**: An open-source multi-cloud security-auditing tool that generates HTML reports of the environment.
- **Cloudsplaining**: An IAM security assessment tool that identifies violations of least privilege.

## 6. Case Studies / Examples

**Case Study: The SSRF to IAM Role Pivot**
An attacker finds an SSRF vulnerability on an EC2 instance. They query `http://169.254.169.254/latest/meta-data/iam/security-credentials/web-role` and retrieve temporary AWS credentials. The attacker configures these locally in the AWS CLI, runs `aws sts get-caller-identity`, confirms they are operating as `web-role`, and uses `aws s3 ls` to find and download a database backup bucket the role had access to.

## 7. Mitigation and Defense

### Least Privilege IAM Policies
Ensure users and roles only have the exact permissions necessary for their function. Never attach `AdministratorAccess` unless strictly required.

### Credential Rotation and Scope
Use temporary, short-lived credentials via AWS STS instead of static IAM User Access Keys.

### CloudTrail Monitoring
Enable AWS CloudTrail across all regions to log every API call made via the AWS CLI. Set up alerts for anomalous enumeration activities (e.g., a user suddenly calling `DescribeInstances` across 15 different regions).

## 8. Chaining Opportunities
- **[[01 - OSINT for Cloud Assets Domain to Cloud IP]]**: Mapping external assets back to internal AWS resources.
- **[[02 - Discovering Exposed Cloud Storage S3 Scanner]]**: Validating open buckets found during CLI enumeration.
- **IAM Privilege Escalation**: Using the CLI to identify and exploit misconfigured IAM policies (e.g., `iam:PassRole` combined with `ec2:RunInstances`).

## 9. Related Notes
- [[01 - OSINT for Cloud Assets Domain to Cloud IP]]
- [[02 - Discovering Exposed Cloud Storage S3 Scanner]]
- [[04 - Using Azure CLI and AzureHound for Recon]]
- [[05 - Using GCP CLI gcloud for Reconnaissance]]
