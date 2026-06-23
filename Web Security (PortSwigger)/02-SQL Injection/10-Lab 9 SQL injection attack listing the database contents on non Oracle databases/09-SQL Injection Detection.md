---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Detection

### Intrusion Detection Systems (IDS)

Intrusion Detection Systems (IDS) monitor network traffic and system logs to detect potential security threats, including SQL Injection attempts.

#### Example

Consider the following Snort rule:

```snort
alert tcp any any -> any 80 (msg:"Potential SQL Injection"; content:"union"; content:"select"; sid:1000001;)
```

This rule detects potential SQL Injection attempts by looking for the keywords "union" and "select" in HTTP traffic.

### Database Activity Monitoring

Database Activity Monitoring (DAM) tools monitor database activity to detect potential security threats, including SQL Injection attempts.

#### Example

Consider the following SQL Server Audit:

```sql
CREATE SERVER AUDIT [SQLInjectionAudit]
TO FILE (FILEPATH = 'C:\AuditLogs')
WITH (ON_FAILURE = CONTINUE);

CREATE DATABASE AUDIT SPECIFICATION [SQLInjectionSpec]
FOR SERVER AUDIT [SQLInjectionAudit]
ADD (FAILED_LOGIN_GROUP),
ADD (SUCCESSFUL_LOGIN_GROUP),
ADD (FAILED_SQL_DATA_ACCESS_GROUP),
ADD (SUCCESSFUL_SQL_DATA_ACCESS_GROUP);

ALTER SERVER AUDIT [SQLInjectionAudit] WITH (STATE = ON);
```

This audit monitors failed and successful login attempts, as well as failed and successful SQL data access attempts, to detect potential SQL Injection attempts.

### Real-World Example: MongoDB SQL Injection Vulnerability

In 2019, a critical SQL Injection vulnerability was discovered in MongoDB, affecting versions 3.6.0 to 3.6.11. The vulnerability allowed attackers to inject SQL code through the aggregation framework, potentially leading to data theft or manipulation.

#### Vulnerable Code

```javascript
db.collection.aggregate([
    { $match: { field: req.query.field } }
]);
```

#### Fixed Code

```javascript
db.collection.aggregate([
    { $match: { field: { $eq: req.query.field } } }
]);
```

This code uses the `$eq` operator to ensure the input is treated as data rather than executable code, preventing SQL Injection.

---
<!-- nav -->
[[08-SQL Injection Attack Listing Database Contents on Non-Oracle Databases|SQL Injection Attack Listing Database Contents on Non-Oracle Databases]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[10-SQL Injection Prevention|SQL Injection Prevention]]
