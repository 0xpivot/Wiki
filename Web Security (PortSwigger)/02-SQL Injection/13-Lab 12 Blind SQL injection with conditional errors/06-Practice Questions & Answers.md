---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the difference between union-based SQL injection and blind SQL injection with conditional errors.**

Blind SQL injection with conditional errors differs significantly from union-based SQL injection. Union-based SQL injection involves manipulating the UNION operator to combine the results of multiple SELECT statements, often to retrieve data from different tables. In contrast, blind SQL injection with conditional errors does not return any data directly; instead, it relies on the application's behavior when an error occurs. By injecting SQL code that causes an error, attackers can infer information about the database structure and content based on whether the application returns an error message or not.

**Q2. How would you exploit a blind SQL injection vulnerability with conditional errors to determine the length of a password?**

To exploit a blind SQL injection vulnerability with conditional errors to determine the length of a password, follow these steps:

1. Identify the vulnerable parameter (e.g., a tracking cookie).
2. Inject SQL code that causes an error if the password length meets a specific condition. For example, `SELECT CASE WHEN LENGTH(password) > 1 THEN 1/0 ELSE '' END FROM users WHERE username = 'admin'`.
3. Observe the application's response. If the application returns an error, the condition is true. If it does not return an error, the condition is false.
4. Iterate through possible lengths, increasing the number until the application no longer returns an error. This indicates the exact length of the password.

For example, if the application returns an error for `LENGTH(password) > 1` but not for `LENGTH(password) > 2`, the password length is 2.

**Q3. How would you use Burp Suite Intruder to automate the process of extracting a password character by character in a blind SQL injection scenario?**

To automate the extraction of a password character by character using Burp Suite Intruder:

1. Set up the vulnerable request in Burp Suite Repeater.
2. Use the SQL payload that causes an error if the character matches, e.g., `SELECT CASE WHEN SUBSTR(password, 1, 1) = 'A' THEN 1/0 ELSE '' END FROM users WHERE username = 'admin'`.
3. In Burp Suite Intruder, set the payload position for the character being tested.
4. Configure the payload list to include all possible characters (e.g., alphanumeric, special characters).
5. Run the Intruder attack and observe the responses. When an error is returned, the corresponding character is part of the password.
6. Repeat the process for each character position until the entire password is extracted.

**Q4. Why is it important to understand the order of execution in SQL queries when exploiting blind SQL injection with conditional errors?**

Understanding the order of execution in SQL queries is crucial when exploiting blind SQL injection with conditional errors because it affects how the injected SQL code interacts with the database. The order of execution typically follows:

1. FROM clause (table selection)
2. WHERE clause (filtering rows)
3. SELECT clause (column selection)

By manipulating the WHERE clause with conditions that depend on the existence of specific data (e.g., a user), attackers can control whether the SELECT clause is executed. This allows them to infer information based on whether the query causes an error or not. For example, if the WHERE clause filters out all rows, the SELECT clause will not execute, leading to no error. Conversely, if the WHERE clause matches a row, the SELECT clause will execute, potentially causing an error.

**Q5. What recent real-world examples or CVEs demonstrate the exploitation of blind SQL injection with conditional errors?**

One notable example is the exploitation of blind SQL injection vulnerabilities in various web applications, such as CMS platforms and web frameworks. For instance, CVE-2021-3129 describes a blind SQL injection vulnerability in WordPress plugins that allowed attackers to extract sensitive data from the database by manipulating input parameters. The vulnerability was exploited by sending specially crafted requests that caused conditional errors, revealing information about the database structure and content.

Another example is CVE-2020-13775, which affected Joomla! versions prior to 3.9.19. This vulnerability allowed attackers to exploit a blind SQL injection flaw in the search functionality, leading to unauthorized data retrieval. By injecting malicious SQL code that caused conditional errors, attackers could infer the presence of specific data within the database.

These examples highlight the importance of securing web applications against SQL injection attacks, particularly blind SQL injection with conditional errors, which can be challenging to detect and mitigate.

---
<!-- nav -->
[[05-Understanding the Attack Scenario|Understanding the Attack Scenario]] | [[Web Security (PortSwigger)/02-SQL Injection/13-Lab 12 Blind SQL injection with conditional errors/00-Overview|Overview]]
