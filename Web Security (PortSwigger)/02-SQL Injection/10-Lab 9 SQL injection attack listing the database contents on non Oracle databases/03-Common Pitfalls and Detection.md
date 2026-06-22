---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Common Pitfalls and Detection

### Common Pitfalls

When exploiting SQL Injection vulnerabilities, there are several common pitfalls to avoid:

1. **Incorrect Number of Columns**: Ensure that the number of columns in the injected query matches the number of columns in the original query.
2. **Data Type Mismatch**: Ensure that the data types of the columns in the injected query match the data types of the columns in the original query.
3. **Error Handling**: Some applications may have error handling mechanisms that prevent the injection from working. Test different payloads to bypass these mechanisms.

### Detection

Detecting SQL Injection vulnerabilities requires a combination of static and dynamic analysis techniques.

#### Static Analysis

Static analysis tools can scan the source code of the application to identify potential SQL Injection vulnerabilities. These tools look for patterns that indicate the use of user input in SQL queries without proper sanitization.

#### Dynamic Analysis

Dynamic analysis involves testing the application with various SQL Injection payloads to see if the application is vulnerable. Tools like Burp Suite and SQLMap can automate this process.

### Real-World Example: CVE-2-2021-22205

CVE-2021-22205 is a real-world example of a SQL Injection vulnerability that affected the WPForms plugin for WordPress. The vulnerability was detected through static analysis of the plugin's source code, which revealed the use of user input in SQL queries without proper sanitization.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/02-SQL Injection Overview|SQL Injection Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[04-Constructing the UNION Query|Constructing the UNION Query]]
