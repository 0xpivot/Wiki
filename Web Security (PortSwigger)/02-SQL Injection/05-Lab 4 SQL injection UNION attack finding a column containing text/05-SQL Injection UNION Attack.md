---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection UNION Attack

A UNION-based SQL Injection attack is a technique used to retrieve data from different tables within the same database. This type of attack is particularly useful when the attacker wants to extract data from tables that are not directly accessible through the application's normal functionality.

### What is a UNION Attack?

A UNION attack combines the results of two or more SELECT statements into a single result set. The attacker can use this to retrieve data from other tables in the database, even if those tables are not directly referenced in the original query.

### Why Use a UNION Attack?

The UNION attack is particularly effective when the attacker knows the structure of the database but cannot directly access the desired data. By combining the results of multiple SELECT statements, the attacker can extract data from different tables and present it in a single result set.

### How Does a UNION Attack Work?

Consider a scenario where an attacker wants to retrieve data from a table named `employees`. The original query might look like this:

```sql
SELECT id, name, email FROM users WHERE id = 1;
```

The attacker can inject a UNION statement to combine the results of this query with another SELECT statement:

```sql
SELECT id, name, email FROM users WHERE id = 1 UNION SELECT id, name, email FROM employees;
```

This combined query will return the results of both SELECT statements, allowing the attacker to retrieve data from the `employees` table.

### Real-World Example: CVE-2019-11510

In 2019, a vulnerability was discovered in the WordPress plugin WP Travel Engine, which allowed attackers to perform a UNION-based SQL Injection attack. This vulnerability (CVE-2019-11510) enabled attackers to retrieve sensitive data from the database, including user credentials and payment information.

### Prevention and Defense

To prevent UNION-based SQL Injection attacks, developers should:

1. **Use Parameterized Queries:** Ensure that all user input is treated as data rather than executable code.
2. **Limit Database Permissions:** Restrict the permissions of the database user to only the necessary actions.
3. **Validate Input:** Implement strict input validation to ensure that user input does not contain malicious SQL code.

### Secure Coding Practices

Here is an example of a vulnerable and a secure version of a UNION-based query:

**Vulnerable Code:**

```python
# Vulnerable code
id = request.form['id']
query = f"SELECT id, name, email FROM users WHERE id = {id} UNION SELECT id, name, email FROM employees;"
cursor.execute(query)
```

**Secure Code:**

```python
# Secure code
id = request.form['id']
query = "SELECT id, name, email FROM users WHERE id = %s UNION SELECT id, name, email FROM employees;"
cursor.execute(query, (id,))
```

In the secure version, the `%s` placeholder ensures that the input is treated as data, preventing SQL Injection.

---
<!-- nav -->
[[04-SQL Injection UNION Attack Finding a Column Containing Text|SQL Injection UNION Attack Finding a Column Containing Text]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/00-Overview|Overview]] | [[06-Understanding SQL Injection and UNION Attacks|Understanding SQL Injection and UNION Attacks]]
