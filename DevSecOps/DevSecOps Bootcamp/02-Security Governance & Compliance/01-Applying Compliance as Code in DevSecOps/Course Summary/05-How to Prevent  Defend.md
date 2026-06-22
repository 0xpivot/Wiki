---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## How to Prevent / Defend

### Detection

Regularly run security scans and audits to detect vulnerabilities and compliance issues. Use tools like SAST, SCA, and vulnerability scanners to identify potential security weaknesses.

### Prevention

Integrate security controls into the build and testing phases to ensure that the final artifact is secure and compliant. Use tools like Azure Policy, AWS Config, and Cloud Custodian to enforce compliance policies.

### Secure Coding Fixes

Show the vulnerable pattern and the corrected secure version side by side.

#### Vulnerable Pattern

```python
import os
import subprocess

def execute_command(command):
    subprocess.run(command, shell=True)
```

#### Secure Pattern

```python
import os
import subprocess

def execute_command(command):
    subprocess.run(command.split(), check=True)
```

### Configuration Hardening

Ensure that all configurations are hardened and follow best practices. Use tools like AWS Config and Cloud Custodian to enforce configuration policies.

### Mitigations

Implement additional mitigations to further reduce the risk of security issues. For example, use network segmentation and access controls to limit the impact of a potential breach.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/04-Example from Wild Brain Coffee|Example from Wild Brain Coffee]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/06-Mapping Security Controls from Specification to Code|Mapping Security Controls from Specification to Code]]
