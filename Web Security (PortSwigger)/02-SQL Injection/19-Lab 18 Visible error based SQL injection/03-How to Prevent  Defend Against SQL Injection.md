---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against SQL Injection

### Detection

Detecting SQL Injection vulnerabilities requires a combination of static and dynamic analysis techniques. Static analysis tools can scan the source code for potential SQL Injection points, while dynamic analysis tools can test the application for vulnerabilities by simulating attacks.

### Prevention

Preventing SQL Injection requires proper input validation and sanitization. Here are some best practices:

1. **Use Prepared Statements**: Prepared statements separate the SQL code from the user input, preventing attackers from injecting malicious code.
2. **Input Validation**: Validate all user input to ensure it meets expected formats and constraints.
3. **Parameterized Queries**: Use parameterized queries to safely include user input in SQL queries.
4. **Least Privilege Principle**: Ensure that the application runs with the least privileges necessary to perform its tasks.
5. **Error Handling**: Implement proper error handling to avoid revealing sensitive information through error messages.

### Secure Coding Fixes

#### Vulnerable Code

```java
String sql = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(sql);
```

#### Secure Code

```java
PreparedStatement pstmt = connection.prepareStatement("SELECT * FROM users WHERE username = ? AND password = ?");
pstmt.setString(1, username);
pstmt.setString(2, password);
ResultSet rs = pstmt.executeQuery();
```

### Configuration Hardening

Hardening the database configuration can also help prevent SQL Injection attacks. Some best practices include:

1. **Disable Unnecessary Features**: Disable unnecessary features and services in the database to reduce the attack surface.
2. **Use Strong Passwords**: Ensure that all database accounts use strong passwords and enable multi-factor authentication where possible.
3. **Limit User Permissions**: Limit user permissions to the minimum required to perform their tasks.
4. **Enable Auditing**: Enable auditing to track and monitor database activities.

### Mitigations

Mitigating SQL Injection attacks requires a combination of technical and organizational measures. Some key mitigations include:

1. **Regular Security Assessments**: Conduct regular security assessments to identify and remediate vulnerabilities.
2. **Security Training**: Provide security training to developers and other personnel to ensure they understand the risks and best practices.
3. **Incident Response Plan**: Develop and maintain an incident response plan to quickly respond to and mitigate the impact of SQL Injection attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/02-Exploiting the Vulnerability|Exploiting the Vulnerability]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/00-Overview|Overview]] | [[04-Lab Setup|Lab Setup]]
