---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Techniques

### Union-Based SQL Injection

Union-based SQL Injection involves using the `UNION` operator to combine the results of two or more SELECT statements. This technique is often used to retrieve data from other tables in the database.

#### Example

Consider the following SQL query:

```sql
SELECT username, password FROM users WHERE id = 1;
```

An attacker could inject a `UNION` statement to retrieve data from another table:

```sql
SELECT username, password FROM users WHERE id = 1 UNION SELECT table_name, column_name FROM information_schema.columns;
```

This query would return both the original data and additional data from the `information_schema.columns` table.

### Error-Based SQL Injection

Error-based SQL Injection involves exploiting the error messages returned by the database to infer information about the database structure and data.

#### Example

Consider the following SQL query:

```sql
SELECT * FROM users WHERE id = 1;
```

An attacker could inject a query that causes an error, revealing information about the database:

```sql
SELECT * FROM users WHERE id = 1 AND 1/(SELECT COUNT(*) FROM information_schema.tables) = 1;
```

If the database contains tables, this query will cause a division by zero error, revealing the number of tables in the database.

### Blind SQL Injection

Blind SQL Injection involves inferring information about the database without receiving direct feedback from the application. This technique is often used when the application does not return error messages or other useful information.

#### Example

Consider the following SQL query:

```sql
SELECT * FROM users WHERE id = 1;
```

An attacker could inject a query that causes a delay, revealing information about the database:

```sql
SELECT * FROM users WHERE id = 1 AND IF(SUBSTRING(@@version,1,1)='5', SLEEP(5), 0);
```

This query will cause a delay if the database version starts with '5', allowing the attacker to infer the version number.

---
<!-- nav -->
[[10-SQL Injection Prevention|SQL Injection Prevention]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[12-SQL Injection Tools|SQL Injection Tools]]
