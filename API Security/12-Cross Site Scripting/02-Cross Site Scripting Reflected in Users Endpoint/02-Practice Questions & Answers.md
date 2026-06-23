---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what reflected cross-site scripting (XSS) is and how it can occur in an API endpoint.**

Reflected XSS occurs when an attacker injects malicious scripts into content that is immediately returned to the user. In the context of an API endpoint, this could happen if user input is included in the response without proper sanitization or validation. For example, if an API endpoint returns user-submitted data directly in its response, an attacker might inject a script that executes when the response is rendered in a browser.

**Q2. How can you test for reflected XSS vulnerabilities in an API endpoint that handles user data?**

To test for reflected XSS vulnerabilities, you can inject payloads that include script tags or other potentially harmful content into the API endpoint. The goal is to determine whether the API reflects the injected content back in its response. Here’s an example using a simple script payload:

```python
import requests
url = 'http://example.com/api/users'
payload = '<script>alert("XSS")</script>'
response = requests.get(url, params={'data': payload})
print(response.text)
```

If the response includes the `<script>` tag, it indicates a potential XSS vulnerability.

**Q3. What are the steps to mitigate reflected XSS vulnerabilities in an API endpoint?**

Mitigating reflected XSS involves several steps:

1. **Input Validation:** Ensure that all user inputs are validated against a strict set of rules. This can include checking for specific characters or patterns that are indicative of script injection attempts.
   
2. **Output Encoding:** Encode all user inputs before they are included in the response. This ensures that any special characters are properly escaped and cannot be interpreted as executable code.

3. **Content Security Policy (CSP):** Implement a Content Security Policy that restricts the sources from which scripts can be loaded. This helps prevent execution of unauthorized scripts even if they are injected.

4. **Sanitization:** Use a library or framework that provides sanitization functions to remove or escape potentially dangerous content from user inputs.

**Q4. How would you exploit a reflected XSS vulnerability in an API endpoint that allows GET requests but not POST requests?**

To exploit a reflected XSS vulnerability in an API endpoint that only allows GET requests, you would craft a URL that includes the malicious script payload. When a user clicks on this URL, the script will be executed in their browser. Here’s an example:

```python
import requests
url = 'http://example.com/api/users?data=<script>alert("XSS")</script>'
# Assume this URL is sent to a victim who clicks on it.
response = requests.get(url)
print(response.text)
```

The key is to ensure that the payload is properly URL-encoded so that it can be included in the query string.

**Q5. Can you provide a recent real-world example of a reflected XSS vulnerability in an API endpoint?**

One notable example is the reflected XSS vulnerability found in the GitHub API in 2019 (CVE-2019-16781). The vulnerability was present in the `GET /repos/{owner}/{repo}/commits` endpoint. An attacker could inject a script into the `sha` parameter, which would be reflected in the response and executed in the user's browser. This allowed the attacker to steal session cookies and gain unauthorized access to the user's GitHub account.

In this case, the vulnerability was mitigated by ensuring proper input validation and output encoding on the server side.

---
<!-- nav -->
[[API Security/12-Cross Site Scripting/02-Cross Site Scripting Reflected in Users Endpoint/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[API Security/12-Cross Site Scripting/02-Cross Site Scripting Reflected in Users Endpoint/00-Overview|Overview]]
