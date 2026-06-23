---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain why insufficient logging and monitoring are critical vulnerabilities in API security.**

Insufficient logging and monitoring allow attackers to operate undetected, making it difficult to identify and respond to security incidents in a timely manner. Without proper logging, organizations cannot track suspicious activities or understand the extent of an attack. Monitoring helps in detecting unusual patterns and alerting security teams to take action. In the absence of these practices, attackers have ample time to exploit vulnerabilities and cause significant damage.

**Q2. Describe how the 7-Eleven Japan 7Pay mobile payment app vulnerability could have been mitigated through better logging and monitoring practices.**

The 7Pay app allowed attackers to reset passwords by specifying any email address, leading to unauthorized access to 900 user accounts. Better logging and monitoring practices could have included:

- **Logging:** Detailed logs should have recorded every password reset request, including the email address used. This would help in identifying patterns of abuse.
- **Monitoring:** Automated monitoring systems could have alerted administrators to an unusual number of password reset requests, especially if they were directed to non-registered email addresses.
- **Rate Limiting:** Implementing rate limits on password reset requests could have slowed down attackers and flagged repeated attempts.

**Q3. How can insufficient logging and monitoring lead to data breaches involving administrative APIs?**

Insufficient logging and monitoring can lead to data breaches involving administrative APIs in several ways:

- **Leaked Access Keys:** If administrative API access keys are leaked, and there is no logging, the organization will not be able to trace the actions taken by the malicious actor.
- **Delayed Response:** Without continuous monitoring, the organization might not detect the leak until long after it has occurred, allowing attackers ample time to access sensitive data.
- **Lack of Audit Trails:** Without proper logging, there is no way to determine what actions were performed using the compromised credentials, making it difficult to assess the full extent of the breach.

**Q4. What steps can be taken to ensure that logging and monitoring are effective in preventing API security issues?**

To ensure effective logging and monitoring for API security, consider the following steps:

- **Detailed Logging:** Ensure logs capture all necessary details, such as timestamps, user IDs, IP addresses, and API endpoints accessed.
- **Continuous Monitoring:** Use automated tools to continuously monitor logs for unusual activity and set up alerts for suspicious behavior.
- **Integrate with SIEM Systems:** Integrate logs with Security Information and Event Management (SIEM) systems to correlate events across multiple sources and provide a comprehensive view of security posture.
- **Regular Audits:** Conduct regular audits of logs to identify and address potential security gaps.
- **Secure Log Integrity:** Protect logs against tampering by ensuring they are stored securely and have mechanisms to verify their integrity.

**Q5. How would you exploit a vulnerable API that lacks proper logging and monitoring?**

To exploit a vulnerable API lacking proper logging and monitoring, follow these steps:

1. **Identify Vulnerabilities:** Look for weaknesses in the API, such as missing authentication checks, weak rate limiting, or unprotected endpoints.
2. **Test Exploitation:** Use automated scripts to repeatedly call the vulnerable API endpoints, attempting to bypass security controls.
3. **Avoid Detection:** Since there is no proper logging or monitoring, avoid leaving obvious traces by using obfuscated requests and varying IP addresses.
4. **Exploit Privileges:** Once access is gained, use administrative privileges to perform unauthorized actions, such as data exfiltration or service disruption.
5. **Cover Tracks:** Remove any traces of the exploitation attempt by deleting logs or modifying them to avoid detection.

**Q6. Provide a recent real-world example of insufficient logging and monitoring leading to a security breach.**

A notable example is the Capital One data breach in 2019 (CVE-2019-11270). The attacker exploited a misconfigured web application firewall to gain unauthorized access to customer data. Due to insufficient logging and monitoring, the breach went unnoticed for an extended period, allowing the attacker to access sensitive information of over 100 million customers. Proper logging and monitoring could have detected the unusual traffic patterns and alerted the security team sooner, potentially mitigating the impact of the breach.

---
<!-- nav -->
[[04-Insufficient Logging and Monitoring|Insufficient Logging and Monitoring]] | [[API Security/05-OWASP API TOP 10/02-API10 Insufficient Logging Monitoring/00-Overview|Overview]]
