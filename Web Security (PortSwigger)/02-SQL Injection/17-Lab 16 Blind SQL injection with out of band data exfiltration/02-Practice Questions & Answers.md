---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of using an out-of-band data exfiltration technique in a blind SQL injection attack?**

Out-of-band data exfiltration is used in blind SQL injection attacks to bypass the limitations of traditional SQL injection techniques where the attacker cannot directly observe the results of their queries. By causing the database to interact with an external system (like a DNS server), the attacker can indirectly retrieve information from the database. This method is particularly useful when the application's responses do not provide any direct feedback about the success or failure of the SQL injection attempts.

**Q2. How would you exploit a blind SQL injection vulnerability to extract the password of the administrator user from the `users` table?**

To exploit a blind SQL injection vulnerability to extract the password of the administrator user from the `users` table, you would follow these steps:

1. Identify the vulnerable parameter, typically a tracking cookie in this case.
2. Craft a payload that triggers an out-of-band interaction with an external domain, such as a DNS lookup.
3. Use a tool like Burp Suite's Collaborator to monitor for interactions with the external domain.
4. Construct a SQL query that selects the password from the `users` table where the username equals 'administrator'.
5. Encode the payload appropriately and inject it into the vulnerable parameter.
6. Monitor the Collaborator server for DNS lookups that include the extracted password.
7. Use the extracted password to log in as the administrator user.

Here’s an example payload:

```sql
SELECT password FROM users WHERE username='administrator' AND RLIKE(password, CONCAT('^(?=.*', (SELECT CAST(CAST(COLLABORATOR_DOMAIN AS CHAR) AS BINARY)), '.*)$'))
```

Replace `COLLABORATOR_DOMAIN` with the actual domain provided by Burp Collaborator.

**Q3. Why is it important to use Burp Collaborator's default public server in this lab exercise?**

It is important to use Burp Collaborator's default public server in this lab exercise because the lab environment is configured with a firewall that blocks interactions with arbitrary external systems. This restriction is in place to prevent the lab from being used to attack third parties. Using Burp Collaborator ensures that the out-of-band interactions are within the controlled environment of the lab, allowing you to successfully exfiltrate data without violating the lab's security policies.

**Q4. Explain how recent real-world examples, such as CVE-2021-44228 (Log4Shell), relate to the concept of out-of-band data exfiltration.**

CVE-2021-44228, also known as Log4Shell, is a critical vulnerability in the Apache Log4j library that allows attackers to execute arbitrary code on affected servers. One of the ways this vulnerability can be exploited is through out-of-band data exfiltration. Attackers can craft malicious input that causes the logging mechanism to make network requests to external domains, effectively leaking sensitive information from the compromised system.

For instance, an attacker could inject a payload that causes the application to perform a DNS lookup to a domain they control. When the DNS request is made, the attacker can capture the leaked data, such as passwords or other sensitive information. This technique is similar to the out-of-band SQL injection method discussed in the lab, where the database is induced to communicate with an external domain to exfiltrate data.

**Q5. How would you configure Firefox to send requests through Burp Suite for this lab exercise?**

To configure Firefox to send requests through Burp Suite for this lab exercise, follow these steps:

1. Open Firefox and install the FoxyProxy extension.
2. Open Burp Suite and ensure the proxy is running.
3. In FoxyProxy settings, add a new proxy configuration and set the host to `localhost` and the port to the port number where Burp Suite's proxy is listening (usually 8080).
4. Enable the proxy for all sites or specify the particular site (e.g., the lab's URL).
5. Test the setup by navigating to the lab's URL in Firefox and verifying that the requests appear in Burp Suite's proxy tab.

By configuring Firefox to route traffic through Burp Suite, you can intercept and modify HTTP requests, which is essential for performing the blind SQL injection attack described in the lab.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/17-Lab 16 Blind SQL injection with out of band data exfiltration/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/17-Lab 16 Blind SQL injection with out of band data exfiltration/00-Overview|Overview]]
