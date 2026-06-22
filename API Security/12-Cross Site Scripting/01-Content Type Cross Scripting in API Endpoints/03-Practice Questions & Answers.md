---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of Content Type Cross-Site Scripting (XSS) in API endpoints.**

Content Type Cross-Site Scripting (XSS) occurs when an API endpoint returns different content types based on certain conditions, leading to unexpected behavior. For example, an API might return JSON data under normal circumstances but switch to plain text or HTML when a specific condition is met, such as a username already existing. If the response in plain text or HTML contains unencoded special characters, it can lead to XSS attacks where malicious scripts are injected into the response and executed by the client browser.

**Q2. How does the Content Type Cross-Site Scripting vulnerability manifest in the login API described in the lecture?**

In the lecture, the login API behaves differently based on whether a username already exists. If the username is unique, the API returns a JSON response indicating successful creation. However, if the username already exists, the API switches to returning a plain text response. This plain text response includes the username and a message stating that the username already exists. If the username contains unencoded HTML characters, it could lead to an XSS attack. For example, if the username is `<script>alert('XSS')</script>`, the response will include this script, which can execute in the client’s browser.

**Q3. How would you exploit a Content Type Cross-Site Scripting vulnerability in an API endpoint?**

To exploit a Content Type Cross-Site Scripting vulnerability, follow these steps:

1. Identify an API endpoint that changes its content type based on input, such as switching from JSON to plain text.
2. Craft a payload that includes malicious JavaScript code wrapped in HTML tags. For example, `<script>alert('XSS')</script>`.
3. Submit the payload through the vulnerable API endpoint.
4. Observe if the response contains the unencoded HTML tags and executes the script in the client’s browser.

Here’s an example using `curl` to submit a payload:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "<script>alert(\"XSS\")</script>"}' http://example.com/api/register
```

If the API returns the payload in plain text without encoding the HTML tags, the script will execute in the client’s browser.

**Q4. What recent real-world examples or CVEs highlight the risks of Content Type Cross-Site Scripting vulnerabilities in APIs?**

One notable example is the CVE-2021-30149, which affected the Jenkins Continuous Integration server. This vulnerability allowed attackers to inject arbitrary JavaScript code via a specially crafted HTTP request to the `/loginError` endpoint. The server returned the error message in plain text format, which included the attacker’s payload. This led to a Cross-Site Scripting (XSS) attack, allowing the attacker to execute arbitrary JavaScript in the context of the victim’s browser session.

Another example is CVE-2020-14882, which affected the Atlassian Jira software. An attacker could inject malicious JavaScript into the response by manipulating the content type of the API response, leading to an XSS attack.

**Q5. How can developers prevent Content Type Cross-Site Scripting vulnerabilities in their API endpoints?**

To prevent Content Type Cross-Site Scripting vulnerabilities, developers should follow these best practices:

1. **Consistent Content Types:** Ensure that API responses consistently use the same content type, such as `application/json`. Avoid switching to plain text or HTML unless absolutely necessary.
2. **Output Encoding:** Always encode output data to prevent injection of malicious scripts. Use appropriate encoding methods based on the context (e.g., HTML entity encoding for HTML contexts).
3. **Content Security Policies (CSP):** Implement Content Security Policies to restrict the sources from which scripts can be loaded, reducing the risk of XSS attacks.
4. **Input Validation:** Validate and sanitize all inputs to ensure they do not contain potentially harmful characters or patterns.
5. **Security Testing:** Regularly perform security testing, including automated scanning and manual penetration testing, to identify and mitigate vulnerabilities.

By adhering to these practices, developers can significantly reduce the risk of Content Type Cross-Site Scripting vulnerabilities in their API endpoints.

---
<!-- nav -->
[[02-Content Type Cross-Site Scripting in API Endpoints|Content Type Cross-Site Scripting in API Endpoints]] | [[API Security/12-Cross Site Scripting/01-Content Type Cross Scripting in API Endpoints/00-Overview|Overview]]
