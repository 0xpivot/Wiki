---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Installing and Configuring Detect Secrets

### What Is Detect Secrets?

`Detect Secrets` is an open-source tool designed to detect secrets in code repositories. It uses a combination of regular expressions and machine learning models to identify potential secrets. The tool supports various types of secrets, including API keys, passwords, and private keys.

### Installation

To install `Detect Secrets`, you can use `pip`, the Python package installer. Open your terminal and run the following command:

```bash
pip install detect-secrets
```

This command installs `Detect Secrets` and makes it available for use in your project.

### Running Detect Secrets

Once installed, you can run `Detect Secrets` on your codebase to detect potential secrets. Navigate to your project directory and execute the following command:

```bash
detect-secrets scan
```

This command scans the current directory and its subdirectories for potential secrets. The output will list any detected secrets along with their locations in the codebase.

### Example Output

Here is an example of the output you might see when running `Detect Secrets`:

```plaintext
[+] Found 3 secrets!
    - api_key: abcdefghijklmnopqrstuvwxyz
      Location: src/main.py:10
    - password: mysecretpassword
      Location: src/config.json:5
    - private_key: -----BEGIN RSA PRIVATE KEY-----
                    MIIEowIBAAKCAQEA...
                    -----END RSA PRIVATE KEY-----
                  Location: src/private_keys.txt:1
```

### Excluding Files and Directories

By default, `Detect Secrets` scans all files in the specified directory. However, you may want to exclude certain files or directories from the scan. You can achieve this by specifying exclusion patterns using regular expressions.

For example, to exclude the `test` and `frontend` directories, you can modify the command as follows:

```bash
detect-secrets scan --exclude-files '^test/|^frontend/'
```

This command excludes all files in the `test` and `frontend` directories from the scan.

### Saving Scan Results

You can save the results of the `Detect Secrets` scan to a file for further analysis. To do this, redirect the output to a file using the `>` operator:

```bash
detect-secrets scan > secrets_report.txt
```

This command saves the scan results to a file named `secrets_report.txt`.

### Full Example

Here is a complete example of running `Detect Secrets` on a repository and saving the results to a file:

```bash
# Clear the screen
clear

# Navigate to the repository
cd path/to/repository

# Run Detect Secrets and save the results to a file
detect-secrets scan --exclude-files '^test/|^frontend/' > secrets_report.txt
```

### Explanation of Each Step

1. **Clear the Screen**: The `clear` command clears the terminal screen for better visibility.
2. **Navigate to the Repository**: The `cd` command changes the current working directory to the repository.
3. **Run Detect Secrets**: The `detect-secrets scan` command scans the repository for potential secrets.
4. **Exclude Files**: The `--exclude-files` option specifies the files and directories to exclude from the scan.
5. **Save Results**: The `>` operator redirects the output of the command to a file named `secrets_report.txt`.

### How to Prevent / Defend Against Secret Leakage

#### Detection

To detect secret leakage, you can integrate `Detect Secrets` into your CI/CD pipeline. This ensures that every commit is scanned for potential secrets before being merged into the main branch.

#### Prevention

To prevent secret leakage, you can use `Pre-Commit` to enforce pre-commit hooks that run `Detect Secrets` before allowing commits to be pushed to the repository.

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**

```python
# src/main.py
api_key = 'abcdefghijklmnopqrstuvwxyz'
```

**Secure Code**

```python
# src/main.py
import os

api_key = os.getenv('API_KEY')
```

In the secure version, the API key is loaded from an environment variable, which is not stored in the codebase.

### Configuration Hardening

To harden your configuration, you can set up environment variables and use `.env` files to store sensitive information. Additionally, you can use tools like `dotenv` to manage environment variables.

#### Example .env File

```plaintext
# .env
API_KEY=abcdefghijklmnopqrstuvwxyz
```

#### Example dotenv Usage

```python
# src/main.py
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')
```

### Full HTTP Request and Response Example

Here is an example of a full HTTP request and response using `Detect Secrets`:

**HTTP Request**

```http
POST /api/detect-secrets HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "repository": "path/to/repository",
  "exclude_files": "^test/|^frontend/"
}
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "secrets": [
    {
      "type": "api_key",
      "value": "abcdefghijklmnopqrstuvwxyz",
      "location": "src/main.py:10"
    },
    {
      "type": "password",
      "value": "mysecretpassword",
      "location": "src/config.json:5"
    }
  ]
}
```

### Mermaid Diagrams

#### Directory Structure

```mermaid
graph TD
    A[Repository] --> B[Test]
    A --> C[Frontend]
    A --> D[Src]
    D --> E[main.py]
    D --> F[config.json]
```

#### Scan Process

```mermaid
sequenceDiagram
    participant User
    participant DetectSecrets
    participant PreCommit
    participant CI/CD

    User->>DetectSecrets: Run detect-secrets scan
    DetectSecrets->>User: Return scan results
    User->>PreCommit: Configure pre-commit hook
    PreCommit->>CI/CD: Integrate into CI/CD pipeline
    CI/CD->>User: Notify on secret detection
```

### Hands-On Labs

To practice automating code security testing, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide practical experience in detecting and preventing secret leakage in real-world scenarios.

---
<!-- nav -->
[[04-Automating Code Security Testing Preventing Secrets from Being Committed|Automating Code Security Testing Preventing Secrets from Being Committed]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/Demo Preventing Secrets from Being Committed/00-Overview|Overview]] | [[06-Integrating `pre-commit`|Integrating `pre-commit`]]
