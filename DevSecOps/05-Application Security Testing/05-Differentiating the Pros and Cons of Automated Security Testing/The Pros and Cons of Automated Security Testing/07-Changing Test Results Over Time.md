---
course: DevSecOps
topic: Differentiating the Pros and Cons of Automated Security Testing
tags: [devsecops]
---

## Changing Test Results Over Time

### What Does Changing Test Results Mean?

Changing test results refer to the phenomenon where the results of security tests can vary over time, even if the code or build process remains unchanged. This occurs because security threats and vulnerabilities evolve over time, and what was secure yesterday may not be secure today.

### Why Do Test Results Change Over Time?

Test results change over time because security threats and vulnerabilities are constantly evolving. New vulnerabilities are discovered regularly, and existing vulnerabilities may be exploited in new ways. As a result, what was considered secure in the past may no longer be secure today.

### How Do Test Results Change Over Time?

Test results change over time due to several factors:

1. **New Vulnerabilities**: New vulnerabilities are discovered regularly, and these can affect previously secure components.
2. **Exploit Techniques**: Exploit techniques evolve, and what was once considered a low-risk vulnerability may become a high-risk vulnerability.
3. **Threat Landscape**: The threat landscape is constantly changing, and new threats can emerge that were not previously considered.

#### Example: Changing Test Results with OWASP ZAP

Consider a web application that was initially tested using OWASP ZAP and found to be secure. Over time, new vulnerabilities are discovered, and the same application is retested using OWASP ZAP. The results may differ from the initial test due to the discovery of new vulnerabilities.

```bash
# Initial test
zap-baseline.py -t http://target.example.com -r report_initial.html

# Re-test after a period
zap-baseline.py -t http://target.example.com -r report_retest.html
```

In this example, the initial test and re-test may produce different results due to the discovery of new vulnerabilities.

### Real-World Example: Changing Test Results in Continuous Integration

Consider a CI/CD pipeline that performs regular security testing using tools like OWASP ZAP. Over time, the results of these tests may change due to the discovery of new vulnerabilities, even if the codebase remains unchanged.

### Pitfalls of Changing Test Results

While changing test results are inevitable, they can also lead to confusion and uncertainty. Developers may struggle to understand why test results have changed and how to address the new vulnerabilities.

### How to Prevent / Defend

To manage changing test results effectively, it is important to stay up-to-date with the latest security threats and vulnerabilities. This includes regularly updating security testing tools and rules to reflect the latest threats.

```bash
# Example of updating OWASP ZAP rules
zap-cli --apikey <api_key> core.setOption api.key <new_api_key>
zap-cli --apikey <api_key> spider.scan <target_url>
```

By keeping the testing tools and rules up-to-date, organizations can ensure that they are testing against the latest threats.

---
<!-- nav -->
[[13-Blocking Builds on Security Failures|Blocking Builds on Security Failures]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/05-Differentiating the Pros and Cons of Automated Security Testing/The Pros and Cons of Automated Security Testing/00-Overview|Overview]] | [[15-Differentiating the Pros and Cons of Automated Security Testing|Differentiating the Pros and Cons of Automated Security Testing]]
