---
course: DevSecOps
topic: Differentiating the Pros and Cons of Automated Security Testing
tags: [devsecops]
---

## Repeatable Security Testing

### What is Repeatable Security Testing?

Repeatable security testing ensures that the same test, given the same inputs, produces the same results every time it is run. This consistency is critical for maintaining reliable security assessments.

### Why Does Repeatability Matter?

Repeatability is essential because it allows for consistent and predictable security outcomes. Without repeatable testing, security assessments could yield different results each time, making it difficult to trust the results and manage security effectively.

### How Does Repeatability Work?

Repeatable security testing relies on deterministic processes and tools that produce consistent outputs. Automated security testing tools are designed to execute the same tests in the same way each time, ensuring that the results are reliable.

#### Example: Repeatable Security Testing with OWASP ZAP

OWASP ZAP (Zed Attack Proxy) is a widely used open-source security testing tool. Here’s how it can be configured for repeatable testing:

```bash
# Command to run OWASP ZAP in headless mode
zap-baseline.py -t http://target.example.com -r report.html
```

This command runs OWASP ZAP in headless mode against a specified target and generates a report. The same command can be run repeatedly to ensure consistent testing results.

### Real-World Example: Repeatable Security Testing in CI/CD Pipelines

Many organizations integrate OWASP ZAP into their CI/CD pipelines to ensure that security testing is performed consistently. For example, a company might run OWASP ZAP as part of the deployment process to verify that no new vulnerabilities have been introduced.

### Pitfalls of Repeatability

While repeatability is beneficial, it can also lead to complacency. If security testing is too rigid and does not adapt to changing threats, it may miss new types of vulnerabilities.

### How to Prevent / Defend

To maintain effective repeatable security testing, it is important to regularly update the testing tools and rules to reflect the latest security threats. Additionally, incorporating dynamic security testing alongside static testing can help identify new vulnerabilities.

```bash
# Example of updating OWASP ZAP rules
zap-cli --apikey <api_key> core.setOption api.key <new_api_key>
zap-cli --apikey <api_key> spider.scan <target_url>
```

These commands update the API key and perform a spider scan using OWASP ZAP, ensuring that the testing remains up-to-date.

---
<!-- nav -->
[[17-Immediate Feedback for Developers|Immediate Feedback for Developers]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/05-Differentiating the Pros and Cons of Automated Security Testing/The Pros and Cons of Automated Security Testing/00-Overview|Overview]] | [[19-Scalability of Automated Security Testing|Scalability of Automated Security Testing]]
