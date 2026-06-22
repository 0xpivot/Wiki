---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Common Pitfalls and Detection

### Common Pitfalls

1. **Manual Enumeration**: Manually enumerating each character of the password can be time-consuming and error-prone.
2. **Incorrect Time Threshold**: Choosing an incorrect time threshold can lead to false positives or negatives.
3. **Network Latency**: Network latency can affect the accuracy of time-based attacks.

### Detection

Detecting Blind SQL Injection can be challenging because the attacker does not directly see the results of their injected SQL code. However, there are several methods to detect such attacks:

1. **Logging and Monitoring**: Implement logging and monitoring of database queries to detect unusual patterns.
2. **Anomaly Detection**: Use anomaly detection tools to identify unexpected behavior in the application.
3. **Web Application Firewalls (WAF)**: Deploy WAFs to detect and block suspicious SQL queries.

### Real-World Example: CVE-2022-22965

CVE-2022-22965 is a real-world example of a SQL Injection vulnerability in the Drupal CMS. The vulnerability allowed attackers to inject malicious SQL code into the search functionality, leading to unauthorized access to sensitive data.

#### Exploit Details

The vulnerability was present in the `search.module` file of the CMS. The search functionality did not properly sanitize user input, allowing attackers to inject SQL code.

#### Impact

Attackers could use this vulnerability to extract sensitive data from the database, such as user credentials and content details.

---
<!-- nav -->
[[04-Blind SQL Injection|Blind SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/00-Overview|Overview]] | [[06-How to Prevent  Defend Against SQL Injection|How to Prevent  Defend Against SQL Injection]]
