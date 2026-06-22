---
course: API Security
topic: Hidden API Functionality Exposure
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is a dictionary attack in the context of API security?**

A dictionary attack in API security involves systematically attempting to log in or access resources by using a predefined list of common usernames and passwords. This approach leverages a dictionary file containing potential credentials to identify valid combinations through repeated login attempts. The goal is to find a valid username and password pair that grants unauthorized access to the system.

**Q2. How can you detect if an API endpoint is vulnerable to a dictionary attack?**

To detect if an API endpoint is vulnerable to a dictionary attacks, you can perform the following steps:

1. **Capture API Requests**: Use tools like Burp Suite to capture requests made to the API.
2. **Identify Endpoints**: Look for endpoints that handle authentication, such as login or user management.
3. **Inject Payloads**: Use Burp Suite's Intruder feature to inject payloads from a dictionary file into these endpoints.
4. **Analyze Responses**: Monitor the responses for successful login attempts or unexpected behavior, such as redirects or specific HTTP status codes (e.g., 200 OK).

For example, if you observe multiple 200 OK responses or redirects to a login page, it could indicate that the endpoint is vulnerable to a dictionary attack.

**Q3. Explain how to configure Burp Suite to perform a dictionary attack on an API endpoint.**

To configure Burp Suite to perform a dictionary attack on an API endpoint, follow these steps:

1. **Capture the Request**: Use Burp Suite’s Proxy to intercept and capture the HTTP request to the API endpoint.
2. **Send to Intruder**: Right-click the captured request and select “Send to Intruder”.
3. **Set Target**: In the Intruder tab, set the target URL and identify the parameters where you want to inject payloads.
4. **Configure Payloads**: Go to the Payloads tab and choose the payload type. For a dictionary attack, select “File” and specify the path to your dictionary file.
5. **Start Attack**: Click the “Start Attack” button to begin the attack. Burp Suite will send requests with different payloads from the dictionary file to the API endpoint.
6. **Analyze Results**: Review the results in the Intruder tab to identify any successful login attempts or unusual responses.

**Q4. What are some recent real-world examples of breaches involving dictionary attacks on API endpoints?**

One notable example is the breach of the Capital One data in 2019 (CVE-2019-11279). The attacker used a combination of techniques, including dictionary attacks, to gain unauthorized access to the company's AWS S3 buckets. The attacker exploited a misconfigured web application firewall rule, which allowed them to perform a dictionary attack to discover sensitive information.

Another example is the breach of the Equifax credit reporting agency in 2017. Although primarily attributed to exploiting a vulnerability in Apache Struts, dictionary attacks were used to gain further access and escalate privileges within the network.

**Q5. How can organizations protect their API endpoints against dictionary attacks?**

Organizations can protect their API endpoints against dictionary attacks by implementing the following measures:

1. **Rate Limiting**: Implement rate limiting on login attempts to prevent rapid successive login attempts.
2. **Account Lockout Policies**: Enforce account lockout policies after a certain number of failed login attempts.
3. **Captcha**: Use CAPTCHA mechanisms to prevent automated login attempts.
4. **Strong Authentication Mechanisms**: Encourage the use of strong, unique passwords and consider multi-factor authentication (MFA).
5. **Monitoring and Logging**: Regularly monitor and log access attempts to detect and respond to suspicious activity.
6. **Security Testing**: Conduct regular security testing, including penetration testing, to identify and mitigate vulnerabilities.

By combining these strategies, organizations can significantly reduce the risk of dictionary attacks compromising their API endpoints.

---
<!-- nav -->
[[API Security/25-Hidden API Functionality Exposure/01-Dictionary Attack at API Endpoint/01-Introduction to Hidden API Functionality Exposure|Introduction to Hidden API Functionality Exposure]] | [[API Security/25-Hidden API Functionality Exposure/01-Dictionary Attack at API Endpoint/00-Overview|Overview]]
