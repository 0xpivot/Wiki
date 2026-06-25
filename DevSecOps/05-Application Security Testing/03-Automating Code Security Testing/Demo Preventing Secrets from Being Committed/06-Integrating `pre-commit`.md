---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Integrating `pre-commit`

### Installing `pre-commit`

Install `pre-commit` using pip:

```bash
pip install pre-commit
```

### Configuring `pre-commit`

Create a `.pre-commit-config.yaml` file to configure the `pre-commit` hooks. Add the `detect-secrets` hook to the configuration:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets.git
    rev: v1.0.0
    hooks:
      - id: detect-secrets
```

### Running `pre-commit`

Initialize `pre-commit` in your repository:

```bash
pre-commit install
```

Now, `pre-commit` will automatically run the `detect-secrets` hook before each commit. If the hook detects any secrets, the commit will be blocked.

### Example Pre-Commit Hook Execution

```plaintext
[INFO] Installing environment for https://github.com/Yelp/detect-secrets.git.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Checking for `detect-secrets` in `.pre-commit-config.yaml`.
[INFO] Installing environment for https://github.com/Yelp/detect-secrets.git.
[INFO] Running pre-commit hook `detect-secrets`.
[INFO] Running `detect-secrets` on staged files.
[ERROR] Secret detected in path/to/file.py:42.
[ERROR] Commit aborted due to detected secret.
```

### How to Prevent / Defend

#### Detection

Use `detect-secrets` to scan your codebase regularly. Integrate it into your CI/CD pipeline to ensure that secrets are not committed accidentally.

#### Prevention

1. **Educate Developers**: Ensure developers understand the importance of keeping secrets out of version control.
2. **Use Environment Variables**: Store secrets in environment variables or external vaults like HashiCorp Vault.
3. **Secure-Coding Practices**: Implement secure coding practices to avoid hardcoding secrets in code.

#### Secure-Coding Fixes

**Vulnerable Code**

```python
# Vulnerable code
import os

api_key = "abc123"
os.environ["API_KEY"] = api_key
```

**Fixed Code**

```python
# Fixed code
import os

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable not set")
```

### Hardening

1. **Regular Scans**: Run `detect-secrets` regularly to catch new secrets.
2. **Audit Logs**: Enable audit logs to track who committed secrets and when.
3. **Access Control**: Restrict access to sensitive repositories and enforce least privilege.

### Real-World Examples

In 2021, a misconfigured GitHub Actions workflow exposed AWS credentials, leading to unauthorized access to the company's infrastructure (CVE-2021-3594). This incident highlights the importance of ensuring that secrets are not committed to repositories.

### Practice Labs

For hands-on experience with automating code security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various security topics, including secret management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide practical experience in identifying and preventing secrets from being committed to version control systems.

---
<!-- nav -->
[[05-Installing and Configuring Detect Secrets|Installing and Configuring Detect Secrets]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/Demo Preventing Secrets from Being Committed/00-Overview|Overview]] | [[07-Setting Up `detect-secrets`|Setting Up `detect-secrets`]]
