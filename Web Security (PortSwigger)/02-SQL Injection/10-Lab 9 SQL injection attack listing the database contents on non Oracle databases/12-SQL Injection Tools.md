---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Tools

### Burp Suite

Burp Suite is a popular web application security testing tool that includes features for detecting and exploiting SQL Injection vulnerabilities.

#### Example

Consider the following Burp Suite configuration:

- **Proxy**: Intercept and modify HTTP requests to test for SQL Injection vulnerabilities.
- **Scanner**: Automatically scan web applications for SQL Injection vulnerabilities.
- **Intruder**: Manually test for SQL Injection vulnerabilities by injecting payloads into HTTP requests.

### SQLMap

SQLMap is a powerful open-source tool for automating the process of detecting and exploiting SQL Injection vulnerabilities.

#### Example

Consider the following SQLMap command:

```bash
sqlmap -u "http://example.com/search?query=" --data="query=1" --batch --level=5 --risk=3
```

This command tests the `query` parameter for SQL Injection vulnerabilities, using a high level of detection and risk.

---
<!-- nav -->
[[11-SQL Injection Techniques|SQL Injection Techniques]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[13-Union-Based SQL Injection|Union-Based SQL Injection]]
