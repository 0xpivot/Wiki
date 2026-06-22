---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection and UNION Attacks

SQL Injection (SQLi) is one of the most prevalent and dangerous vulnerabilities in web applications. It occurs when an attacker manipulates input fields to execute arbitrary SQL commands against a database. This can lead to unauthorized access to sensitive data, data manipulation, or even complete compromise of the database server.

### What is SQL Injection?

SQL Injection is a code injection technique where an attacker inserts malicious SQL statements into an entry field for execution. This can happen when user inputs are not properly sanitized or validated before being used in SQL queries. The goal of an attacker is to manipulate the application's logic to gain unauthorized access to data or perform actions that should not be allowed.

#### Example of SQL Injection

Consider a simple login form where the username and password are submitted to a server. The server might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password';
```

If the `$username` variable is not properly sanitized, an attacker could enter something like `admin' OR '1'='1` as the username. This would change the SQL query to:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = '';
```

Since `'1'='1'` is always true, the query will return all rows where the username is 'admin', effectively bypassing authentication.

### UNION Operator in SQL

The `UNION` operator is used to combine the result sets of two or more `SELECT` statements. Each `SELECT` statement within the `UNION` must have the same number of columns, and corresponding columns must have similar data types. This operator is often used in SQL Injection attacks to retrieve data from different tables.

#### Syntax of UNION

The general syntax of the `UNION` operator is:

```sql
SELECT column1, column2, ...
FROM table1
UNION
SELECT column1, column2, ...
FROM table2;
```

### Rules for Using UNION

When using the `UNION` operator, there are specific rules that must be followed:

1. **Number and Order of Columns**: The number and order of columns must be the same in all queries. This ensures that the combined result set is consistent.
2. **Data Types Compatibility**: The data types of corresponding columns must be compatible. This means that the data types should either match exactly or be implicitly convertible.

### Example of UNION in SQL Injection

Let's consider a scenario where an attacker wants to extract data from the `users` table using a `UNION` attack. Suppose the original query is:

```sql
SELECT product_name, price FROM products WHERE id = $id;
```

An attacker could inject a `UNION` query to retrieve usernames and passwords from the `users` table:

```sql
SELECT product_name, price FROM products WHERE id = 1 UNION SELECT username, password FROM users;
```

This would combine the results of the two queries into a single result set.

### Determining the Number of Columns

Before performing a `UNION` attack, it is crucial to determine the number of columns returned by the original query. This can be done through trial and error or by analyzing the structure of the query.

#### Example of Determining Column Count

Suppose the original query is:

```sql
SELECT product_name, price FROM products WHERE id = $id;
```

To determine the number of columns, the attacker can inject a query with different numbers of columns until the correct number is found. For example:

```sql
SELECT product_name, price FROM products WHERE id = 1 UNION SELECT NULL, NULL;
```

If this query returns results, it indicates that the original query has two columns. If it does not work, the attacker can try with three columns:

```sql
SELECT product_name, price FROM products WHERE id = 1 UNION SELECT NULL, NULL, NULL;
```

By systematically increasing the number of columns, the attacker can determine the correct number.

### Real-World Examples of SQL Injection

#### CVE-2021-21972: WordPress REST API SQL Injection

In 2021, a critical SQL Injection vulnerability was discovered in the WordPress REST API. The vulnerability allowed attackers to inject malicious SQL code through the `filter` parameter, leading to unauthorized data retrieval or manipulation.

#### CVE-2020-14882: Apache Struts SQL Injection

Another notable example is the SQL Injection vulnerability in Apache Struts, which affected versions 2.3.x and 2.5.x. Attackers could exploit this vulnerability to execute arbitrary SQL commands, potentially leading to data theft or server compromise.

### How to Prevent SQL Injection

#### Secure Coding Practices

1. **Use Prepared Statements**: Prepared statements ensure that user inputs are treated as data rather than executable code. This prevents SQL Injection attacks.
   
   ```java
   String sql = "SELECT * FROM users WHERE username = ? AND password = ?";
   PreparedStatement pstmt = connection.prepareStatement(sql);
   pstmt.setString(1, username);
   pstmt.setString(2, password);
   ResultSet rs = pstmt.executeQuery();
   ```

2. **Input Validation**: Validate and sanitize all user inputs to ensure they meet expected formats and constraints.

   ```python
   import re
   
   def validate_input(input_str):
       if re.match(r'^[a-zA-Z0-9_]+$', input_str):
           return True
       return False
   ```

3. **Least Privilege Principle**: Ensure that database accounts used by the application have the minimum necessary privileges to perform their tasks.

#### Detection and Monitoring

1. **Web Application Firewalls (WAF)**: Deploy WAFs to monitor and filter incoming traffic for suspicious patterns indicative of SQL Injection attempts.

2. **Logging and Auditing**: Implement comprehensive logging and auditing mechanisms to track database activities and detect unusual patterns.

#### Hardening Database Configurations

1. **Disable Unnecessary Features**: Disable unnecessary features and services in the database to reduce the attack surface.

2. **Regular Updates and Patch Management**: Keep the database management system and related components up to date with the latest security patches.

### Conclusion

SQL Injection remains a significant threat to web applications. Understanding the principles behind SQL Injection and the `UNION` operator is crucial for both attackers and defenders. By adhering to secure coding practices, implementing robust detection mechanisms, and regularly updating systems, organizations can significantly mitigate the risk of SQL Injection attacks.

### Practice Labs

For hands-on experience with SQL Injection and UNION attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice various SQL Injection techniques, including UNION attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including SQL Injection, for educational purposes.

These labs provide a safe environment to learn and practice the concepts discussed in this chapter.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/00-Overview|Overview]] | [[02-Introduction to SQL Injection and Union Attacks|Introduction to SQL Injection and Union Attacks]]
