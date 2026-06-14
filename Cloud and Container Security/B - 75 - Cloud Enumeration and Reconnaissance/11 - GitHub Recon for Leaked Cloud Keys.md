---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.11 GitHub Recon for Leaked Cloud Keys"
---

# 75.11 GitHub Recon for Leaked Cloud Keys

## Introduction to Source Code Reconnaissance

In the modern era of cloud-native development, infrastructure as code (IaC), serverless deployments, and automated CI/CD pipelines require heavy reliance on programmatic access keys. Developers, under tight deadlines, often hardcode these access keys, tokens, and credentials directly into configuration files, scripts, or application source code. When these repositories are pushed to version control systems like GitHub, GitLab, or Bitbucket—whether inadvertently made public or leaked via compromised developer endpoints—the hardcoded secrets become accessible to malicious actors.

GitHub recon is a fundamental phase in cloud enumeration. It involves systematically searching through public (and sometimes private, if access is obtained) repositories, gists, and organization profiles to identify leaked cloud credentials. These credentials typically take the form of AWS Identity and Access Management (IAM) access keys, Google Cloud Platform (GCP) service account JSON files, Azure Service Principal secrets, or third-party API tokens. 

The impact of leaked cloud keys cannot be overstated. A single exposed AWS `AKIA...` key with administrative privileges can lead to total cloud environment compromise within minutes. Automated bots actively scrape GitHub for these specific key patterns, meaning that a leaked key is often weaponized by opportunistic attackers or cryptominers before the developer even realizes the mistake. Therefore, understanding how to actively enumerate, identify, and validate leaked keys is an essential skill for any cloud security professional or penetration tester.

## The Mechanics of Git History and Secret Leakage

To effectively hunt for secrets, one must understand how Git tracks changes. Git is a distributed version control system that maintains a complete history of every modification made to the codebase. This fundamental design means that simply removing a hardcoded secret and pushing a new commit does not remediate the leak. 

### Commits and the `.git` Directory
When a developer commits a file containing a secret, that exact state of the file is snapshot and stored as a blob object within the `.git/objects` directory. Even if a subsequent commit deletes the secret, the original blob remains in the repository's history. Anyone who clones the repository receives the entire `.git` directory and can easily browse past commits, branches, and tags.

### Pull Requests and Orphaned Commits
Pull requests (PRs) introduce another vector. A developer might open a PR containing a secret, realize the error, and force-push a corrected commit to their branch. While the branch is updated, GitHub often caches the original commit, which can still be accessed via the PR's comment history or specific commit hash. These "orphaned" commits are a goldmine for attackers who systematically scrape PR histories.

### Gists and Personal Repositories
Developers often use GitHub Gists to share code snippets, configuration files, or debugging logs. These snippets frequently contain environment variables or connection strings with embedded credentials. Furthermore, developers might clone corporate code to their personal, public repositories to work from home, inadvertently exposing proprietary code and associated secrets to the public internet.

## GitHub Dorking Techniques

GitHub's native search functionality, while heavily filtered to prevent mass scraping, is an incredibly powerful tool for manual reconnaissance. By leveraging specific search operators (dorks), penetration testers can pinpoint files likely to contain secrets.

### Basic Search Operators
- `filename:` Filters results by the name of the file (e.g., `filename:.env`, `filename:credentials`).
- `extension:` Filters by file type (e.g., `extension:pem`, `extension:json`).
- `user:` or `org:` Restricts the search to a specific user or organization profile.
- `path:` Searches within a specific directory path.

### Highly Effective GitHub Dorks for Cloud Secrets

1. **AWS IAM Keys:**
   AWS access keys historically start with `AKIA` (for long-term credentials) or `ASIA` (for short-term STS credentials).
   `"AKIA" extension:env`
   `"aws_access_key_id" extension:json`
   `"aws_secret_access_key" org:target-company`

2. **GCP Service Accounts:**
   GCP credentials are often stored in JSON format, detailing the project ID, private key, and client email.
   `"type": "service_account" extension:json`
   `"private_key": "-----BEGIN PRIVATE KEY-----" "project_id"`

3. **Azure Service Principals:**
   Azure uses tenant IDs, client IDs, and client secrets.
   `"client_secret" "tenant_id" extension:json`
   `"AZURE_CLIENT_SECRET" extension:env`

4. **Terraform State Files:**
   Terraform state files (`.tfstate`) contain a comprehensive map of the deployed cloud infrastructure, frequently including plaintext passwords, API keys, and database connection strings.
   `filename:terraform.tfstate "password"`
   `extension:tfstate "aws_access_key"`

## Automated Tooling: GitLeaks and TruffleHog

Manual dorking is tedious and scales poorly. Modern reconnaissance relies on automated tools designed to parse Git history and apply complex regular expressions and entropy checks to identify secrets.

### TruffleHog
TruffleHog is a premier secret-scanning tool that goes beyond simple regex matching. It natively integrates with various cloud providers and SaaS platforms to actively *verify* the identified secrets. 
When TruffleHog finds an AWS key, it can attempt to authenticate against the AWS STS `GetCallerIdentity` endpoint to determine if the key is active and what IAM entity it belongs to.

**Execution Example:**
```bash
trufflehog github --org=target-company --only-verified
```
This command instructs TruffleHog to scan all repositories belonging to `target-company` and only output secrets that are actively valid, drastically reducing false positives.

### GitLeaks
GitLeaks is a fast, Go-based secret scanner that excels in CI/CD pipeline integration and rapid repository auditing. It uses a comprehensive configuration file (`gitleaks.toml`) filled with highly tuned regular expressions for hundreds of distinct secret types.

**Execution Example:**
```bash
gitleaks detect --source /path/to/cloned/repo --report-path findings.json --verbose
```
GitLeaks iterates through every commit in the repository's history, analyzing file additions and modifications against its rule set. The resulting JSON report provides the commit hash, author, date, file path, and the specific matched secret, enabling testers to quickly locate the leaked credential.

## Advanced Attack Architecture Diagram

```mermaid
graph TD
    subgraph The Credential Leakage Lifecycle
        A[Developer] -- 1. Hardcodes AWS_SECRET_ACCESS_KEY in .env file --> B[Local Git Repo]
        B -- 2. Commits and Pushes to GitHub --> C[GitHub Repository]
        C -- 3. Public or Compromised --> D[Attacker Recon Node <br/> - TruffleHog <br/> - GitLeaks <br/> - GitHub Dorks]
        D -- 5. Attacker Extracts Active Keys e.g., AKIA... --> E[Target Cloud Environment <br/> - AWS IAM <br/> - S3 Buckets <br/> - EC2 Instances <br/> - RDS Databases]
        D -- 6. Authentication --> E
        E -- 7. Data Exfiltration & Privilege Escalation --> D
    end
```

## Exploiting the Recovered Keys

Once a valid cloud key is recovered from GitHub, the next phase is validation and enumeration using the cloud provider's CLI or specialized enumeration tools.

### AWS Credential Validation
For AWS, the recovered `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` should be configured in the local environment:
```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-east-1
```
The first command executed should always be `aws sts get-caller-identity`. This critical command returns the Account ID, User ARN, and User ID without logging an explicit "Access Denied" error if the key lacks broader permissions.

```json
{
    "UserId": "AIDAJQABLZS4A3QDU576Q",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/dev-ci-cd-bot"
}
```

If the key belongs to a highly privileged user, the attacker can proceed to enumerate S3 buckets (`aws s3 ls`), EC2 instances (`aws ec2 describe-instances`), or escalate privileges by modifying IAM policies.

## Defensive Strategies and Remediation

Addressing leaked secrets requires a multi-layered approach focusing on prevention, detection, and rapid response.

1. **Pre-Commit Hooks:** Tools like `git-secrets` or `talisman` can be installed locally on developers' machines. These hooks run regex checks against the code *before* the commit is finalized, preventing the secret from ever entering the local Git history.
2. **GitHub Advanced Security:** Enabling secret scanning on GitHub repositories allows GitHub to automatically detect leaked keys and notify the organization. For certain partners (like AWS), GitHub will automatically forward the leaked key to the provider, who will instantly revoke it or apply a quarantine policy.
3. **Key Rotation and Least Privilege:** The impact of a leaked key is directly proportional to its permissions. Following the principle of least privilege ensures that a leaked CI/CD token can only access the specific S3 bucket it needs, rather than full administrative control. Furthermore, implementing mandatory 90-day key rotation limits the useful lifespan of an undetected leak.
4. **History Rewriting:** If a secret is leaked, simply deleting the file is insufficient. The repository's history must be rewritten using tools like `git filter-repo` or `BFG Repo-Cleaner` to completely purge the blob objects from the `.git` directory. The compromised keys MUST be immediately revoked in the cloud provider's console; rewriting history does not invalidate the active credentials.

## Chaining Opportunities
- Leaked credentials provide initial access that can be heavily utilized in [[12 - Using CloudBrute and Pacu for Discovery]].
- Once initial access is achieved, a comprehensive audit tool can be run against the environment as detailed in [[13 - Using ScoutSuite for Cloud Security Auditing]].
- The enumerated IAM privileges might allow for modifying network configurations, leading directly to [[14 - Identifying Misconfigured Cloud Networking Security Groups]].

## Related Notes
- [[01 - Introduction to Cloud Security Concepts]]
- [[05 - AWS IAM Architecture and Misconfigurations]]
- [[22 - Source Code Analysis and Static Application Security Testing]]
