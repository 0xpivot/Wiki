---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Setting Up `detect-secrets`

### Installation

First, install `detect-secrets` using pip:

```bash
pip install detect-secrets
```

### Configuration File

Create a `.secrets.baseline.json` file to store the scan results and settings used for the scan. This file can be added to your repository to ensure consistency across different environments.

#### Example `.secrets.baseline.json`

```json
{
    "plugins": {
        "HighEntropyString": {
            "blacklist": [],
            "whitelist": []
        },
        "Base64HighEntropyString": {
            "blacklist": [],
            "whitelist": []
        },
        "HexHighEntropyString": {
            "blacklist": [],
            "whitelist": []
        }
    },
    "baseline": [
        {
            "filename": "path/to/file.py",
            "line_number": 42,
            "type": "HighEntropyString",
            "hash": "sha256:abc123..."
        }
    ]
}
```

### Running the Scan

Run the `detect-secrets` scan to generate the baseline:

```bash
detect-secrets scan --baseline .secrets.baseline.json
```

This command will scan the codebase and update the `.secrets.baseline.json` file with the detected secrets.

### Auditing the Baseline

The next step is to audit the baseline to determine which detected items are actual secrets and which are false positives. Use the following command to start the audit process:

```bash
detect-secrets audit .secrets.baseline.json
```

This command will prompt you to review each detected item one by one. You can mark items as false positives or confirm them as actual secrets.

### Example Audit Process

```plaintext
Reviewing secret at path/to/file.py:42
Type: HighEntropyString
Hash: sha256:abc111...

Is this a false positive? [y/N]: N
```

By marking items as false positives, you can refine the baseline to exclude non-sensitive information.

---
<!-- nav -->
[[06-Integrating `pre-commit`|Integrating `pre-commit`]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/Demo Preventing Secrets from Being Committed/00-Overview|Overview]] | [[08-Conclusion Part 1|Conclusion Part 1]]
