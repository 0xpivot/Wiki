---
course: API Security
topic: Information Disclosure
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is the primary goal when attempting to identify information disclosure vulnerabilities in an API?**

The primary goal is to detect any instances where sensitive information is inadvertently exposed through API responses. This could include stack trace errors, sensitive data such as passwords, or system details that should not be publicly accessible. The aim is to ensure that the API does not leak any confidential information that could be exploited by attackers.

**Q2. How can you exploit a debug endpoint to reveal sensitive information?**

To exploit a debug endpoint, you can attempt to trigger an error condition that might expose internal system details or configuration settings. For example, sending malformed input or invalid parameters to the endpoint might cause an exception to be thrown, which could result in a stack trace being returned. This stack trace often contains detailed information about the application's internal workings, including file paths, function calls, and even sensitive configuration data.

**Q3. Explain how a non-existent user request can lead to information disclosure.**

When a non-existent user is requested from an API, the server might respond with an error message that includes sensitive information. For instance, if a POST request to `/api/v2/users` with a non-existent username and password is made, the server might return a response containing the password in plain text. This is a clear case of information disclosure because the password, which is supposed to be kept secret, is revealed in the response. This can be exploited to gain unauthorized access to user accounts.

**Q4. Describe a scenario where an unexpected token error reveals sensitive information.**

An unexpected token error typically occurs when the server encounters syntax it cannot parse correctly. If the server returns a detailed error message, it might include the exact location within the code where the error occurred, along with file paths and other internal details. For example, if a semicolon is added to a search query parameter, it might cause an unexpected token error, revealing the path to the file where the error occurred. This type of information can be used to map out the server's directory structure and potentially discover additional vulnerabilities.

**Q5. What types of sensitive system information might be disclosed through an API endpoint?**

Sensitive system information that might be disclosed through an API endpoint includes:

- User local binary versions and models
- HTTP architecture details
- Platform release versions
- Environment details (e.g., database connection strings, API keys)
- Configuration settings

For example, an endpoint like `/api/info` might return details about the MongoDB environment, including version numbers and possibly even connection strings. This information can be used by attackers to craft targeted attacks against the system.

**Q6. How can information disclosure vulnerabilities impact an organization's security posture?**

Information disclosure vulnerabilities can significantly impact an organization's security posture by exposing sensitive data that can be used to launch further attacks. For instance, leaked passwords can be used to gain unauthorized access to systems, while exposed configuration details can provide attackers with insights into the system's architecture, facilitating more sophisticated attacks. Additionally, such vulnerabilities can undermine trust in the organization and lead to compliance issues if sensitive data is improperly handled.

**Q7. Provide a recent real-world example of an information disclosure vulnerability and explain its impact.**

One recent example is the CVE-2021-21972, which affected the WordPress REST API. This vulnerability allowed attackers to retrieve sensitive information, including usernames and email addresses, by making specific requests to the API. The impact was significant because it exposed personal data, leading to potential privacy violations and enabling further attacks such as phishing. This highlights the importance of securing APIs to prevent such disclosures and protect user data.

---
<!-- nav -->
[[API Security/16-Information Disclosure/03-Information Disclosure Demonstration/02-Information Disclosure in APIs|Information Disclosure in APIs]] | [[API Security/16-Information Disclosure/03-Information Disclosure Demonstration/00-Overview|Overview]]
