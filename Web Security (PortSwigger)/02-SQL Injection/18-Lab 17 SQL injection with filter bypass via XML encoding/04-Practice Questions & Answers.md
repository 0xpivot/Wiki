---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of using the Hack Verter extension in the context of this lab?**

The Hack Verter extension is used to obfuscate SQL injection payloads to bypass web application firewalls (WAFs). In this lab, the WAF blocks obvious SQL injection attempts. By encoding the payload using Hack Verter, the payload becomes less recognizable to the WAF, allowing the attacker to execute the SQL injection without triggering the WAF.

**Q2. How does XML encoding help in bypassing a WAF in SQL injection attacks?**

XML encoding helps in bypassing a WAF by altering the format of the SQL injection payload. Instead of using plain text characters, XML encoding uses character references (e.g., `&amp;` for `&`, `&#x3C;` for `<`). This makes the payload less recognizable to the WAF, as it may not have rules to detect these encoded characters as part of a SQL injection attempt. This technique is particularly effective when the WAF is configured to block specific patterns or keywords commonly associated with SQL injection.

**Q3. Explain how you would determine the number of columns in a SQL injection vulnerable query.**

To determine the number of columns in a SQL injection vulnerable query, you can use a `UNION SELECT` statement with a series of `NULL` values. Start with one `NULL` value and incrementally increase the number of `NULL` values until the query returns a valid result. For example:

```sql
1 UNION SELECT NULL -- Check for one column
1 UNION SELECT NULL, NULL -- Check for two columns
```

If the query with one `NULL` value returns a valid result, it indicates that the original query has one column. If the query with two `NULL` values returns a valid result, it indicates that the original query has two columns, and so on.

**Q4. How would you exploit a SQL injection vulnerability to retrieve the admin's credentials from a user's table?**

To exploit a SQL injection vulnerability to retrieve the admin's credentials, follow these steps:

1. Identify the vulnerable input field.
2. Use a `UNION SELECT` statement to retrieve data from the user's table.
3. Determine the number of columns in the original query.
4. Concatenate the username and password fields to fit into the number of columns determined.
5. Encode the payload to bypass any WAFs using tools like Hack Verter.

Example payload:

```sql
1 UNION SELECT username || '||' || password FROM users WHERE username = 'admin'
```

This payload concatenates the username and password fields with a separator (`||`) and retrieves the admin's credentials.

**Q5. Discuss recent real-world examples where SQL injection vulnerabilities were exploited.**

One notable recent example is the Capital One data breach in 2019, where a misconfigured firewall allowed an attacker to exploit a SQL injection vulnerability. The attacker was able to access sensitive information, including names, addresses, credit scores, and social security numbers of approximately 100 million customers and potential customers.

Another example is the 2020 breach of the UK-based company TalkTalk, where a SQL injection vulnerability led to the theft of customer data, including names, phone numbers, email addresses, and bank details. This breach affected over 156,000 customers and resulted in significant financial losses and reputational damage.

In both cases, the vulnerabilities were due to poor coding practices and inadequate security measures, highlighting the importance of proper input validation and the use of secure coding techniques to prevent such attacks.

---
<!-- nav -->
[[03-Techniques to Bypass Web Application Firewalls|Techniques to Bypass Web Application Firewalls]] | [[Web Security (PortSwigger)/02-SQL Injection/18-Lab 17 SQL injection with filter bypass via XML encoding/00-Overview|Overview]]
