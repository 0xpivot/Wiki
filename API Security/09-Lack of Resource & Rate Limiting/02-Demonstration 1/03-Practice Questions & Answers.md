---
course: API Security
topic: Lack of Resource & Rate Limiting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of rate limiting in API security and why it is important.**

Rate limiting is a technique used to control the number of requests that can be made to an API within a specified time frame. This is important because without rate limiting, malicious actors could flood the API with excessive requests, leading to resource exhaustion, denial of service (DoS), and potentially exposing vulnerabilities. Rate limiting helps ensure that the API remains responsive and available to legitimate users while mitigating the risk of abuse.

**Q2. How would you exploit a lack of rate limiting in an API endpoint designed to add comments?**

To exploit a lack of rate limiting in an API endpoint designed to add comments, one could use tools like Burp Suite Intruder to automate the process of sending multiple requests to the API. By generating a large number of requests (e.g., 1000 or 10,000), the attacker can overwhelm the server and potentially cause resource exhaustion. This could lead to the API becoming unresponsive or slow, affecting its ability to serve legitimate requests.

**Q3. Describe a recent real-world example of an API vulnerability related to rate limiting and explain how it was exploited.**

A notable example is the Twitter API rate-limiting bypass vulnerability (CVE-2021-29134). In this case, attackers were able to bypass rate limits by using a combination of different IP addresses and user agents to make repeated requests to the API. This allowed them to perform actions such as following and unfollowing users at an accelerated rate, which could be used for spamming or other malicious activities. The vulnerability was exploited due to insufficient rate-limiting mechanisms in place to detect and block such behavior.

**Q4. How would you configure rate limiting for an API endpoint that sends verification emails?**

To configure rate limiting for an API endpoint that sends verification emails, you could implement a mechanism that tracks the number of requests made by a particular user within a given time period. For example, you could set a limit of 5 emails per hour per user. If the limit is exceeded, the API could return an error message indicating that the user has reached their limit and must wait before attempting to send more emails. This can be implemented using middleware in your API framework or through a dedicated rate-limiting service.

**Q5. Explain how a lack of rate limiting in an API endpoint designed to delete comments could be exploited.**

Without rate limiting, an attacker could exploit an API endpoint designed to delete comments by automating the deletion process using tools like Burp Suite Intruder. By sending a large number of deletion requests (e.g., 1000 or more), the attacker could potentially disrupt the functionality of the application by deleting a significant amount of content. This could lead to data loss and affect the usability of the application for legitimate users.

**Q6. How would you detect and report a vulnerability related to the absence of rate limiting in an API?**

To detect a vulnerability related to the absence of rate limiting in an API, you could use automated tools like Burp Suite Intruder to send a high volume of requests to the API and observe the server's response. If the server continues to respond without any rate-limiting measures, it indicates a potential vulnerability. To report the vulnerability, you would typically follow the organization’s responsible disclosure policy, providing detailed information about the vulnerability, including the steps to reproduce it and the potential impact. You might also suggest implementing rate-limiting mechanisms as a mitigation strategy.

---
<!-- nav -->
[[02-Lack of Resource & Rate Limiting|Lack of Resource & Rate Limiting]] | [[API Security/09-Lack of Resource & Rate Limiting/02-Demonstration 1/00-Overview|Overview]]
