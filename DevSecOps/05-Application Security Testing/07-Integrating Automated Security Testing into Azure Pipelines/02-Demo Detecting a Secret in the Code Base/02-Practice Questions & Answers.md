---
course: DevSecOps
topic: Integrating Automated Security Testing into Azure Pipelines
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why it's important to detect secrets in the codebase during automated security testing.**

Detecting secrets in the codebase is crucial because it helps prevent sensitive information such as API keys, passwords, and private keys from being accidentally committed to version control systems. If these secrets are exposed, they can be exploited by malicious actors to gain unauthorized access to systems, leading to data breaches and other security incidents. Automated security testing ensures that developers are alerted when they attempt to commit such sensitive information, thereby maintaining the security of the codebase and the systems it interacts with.

**Q2. How would you configure an Azure pipeline to detect secrets in the codebase?**

To configure an Azure pipeline to detect secrets in the codebase, you can use tools like `detect-secrets` or similar security scanning tools. Here’s a basic example of how to set up a pipeline step using `detect-secrets`:

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- script: |
    pip install detect-secrets
    detect-secrets scan --baseline .secrets.baseline
  displayName: 'Run Secrets Detection'
```

This YAML snippet sets up a pipeline that installs `detect-secrets`, scans the codebase for secrets, and compares the findings against a baseline file. The baseline file contains known secrets that are allowed in the codebase, so new secrets not in the baseline will cause the pipeline to fail.

**Q3. What would happen if you tried to commit a file with secrets to a repository that has an automated security test configured to detect secrets?**

If you try to commit a file with secrets to a repository that has an automated security test configured to detect secrets, the commit would likely trigger the security test. If the test detects any secrets that are not part of the established baseline, the commit would fail, and the pipeline would notify you of the issue. For example, in the scenario described in the lecture, committing a file named `users.yml` containing a username and password caused the pipeline stage to fail because the secrets were detected and did not match the baseline.

**Q4. Why is it necessary to update the baseline when adding new secrets to the codebase?**

Updating the baseline is necessary when adding new secrets to the codebase because the baseline serves as a record of approved secrets that are allowed to exist within the codebase. If you add a new secret without updating the baseline, the automated security test will flag it as a new, unapproved secret and fail the build. By updating the baseline, you inform the security test that the new secret is authorized, allowing the build to proceed successfully.

**Q5. Can you provide a recent real-world example where failing to detect secrets in the codebase led to a security breach?**

A notable example is the incident involving the cryptocurrency exchange Binance in 2020. Hackers gained access to Binance's systems by exploiting a leaked API key that was stored in the codebase. The API key was used to access Binance's internal systems, leading to unauthorized transactions and potential financial losses. This incident underscores the importance of ensuring that sensitive information is not inadvertently committed to version control systems and that automated security tests are in place to detect such issues before they can be exploited.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/03-Demo Detecting a Secret in the Code Base/01-Integrating Automated Security Testing into Azure Pipelines|Integrating Automated Security Testing into Azure Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/07-Integrating Automated Security Testing into Azure Pipelines/03-Demo Detecting a Secret in the Code Base/00-Overview|Overview]]
