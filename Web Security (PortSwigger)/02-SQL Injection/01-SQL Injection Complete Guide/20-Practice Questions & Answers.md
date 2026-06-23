---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a SQL injection vulnerability is and provide an example of how it can be exploited.**

SQL injection is a type of security vulnerability that allows an attacker to interfere with the SQL queries that an application makes to its backend database. By inserting malicious SQL code into input fields, an attacker can manipulate the database to perform unintended actions.

For example, consider a login form where the SQL query checks if the entered username and password match a record in the database:

```sql
SELECT * FROM users WHERE username = 'admin' AND password = 'password';
```

An attacker can insert a single quote and a comment symbol (`--`) to terminate the SQL statement prematurely:

```sql
SELECT * FROM users WHERE username = 'admin' -- ' AND password = 'password';
```

This modified query effectively ignores the password condition, allowing the attacker to log in as `admin` without knowing the password.

**Q2. Describe the different types of SQL injection vulnerabilities and provide an example of each.**

There are three main types of SQL injection vulnerabilities:

1. **In-band SQL Injection**: The attacker uses the same communication channel to both launch the attack and gather the results.
   - **Example**: An attacker inputs a single quote in a search field, causing the application to return an error message that reveals the database version.

2. **Blind SQL Injection**: The attacker cannot see the results directly but can infer them by observing changes in the application's behavior.
   - **Example**: An attacker uses a time-based payload to determine if a condition is true or false. If the response time is significantly longer, the condition is true.

3. **Out-of-band SQL Injection**: The attacker triggers an out-of-band network connection to a system they control.
   - **Example**: An attacker exploits a DNS lookup feature in the database to confirm the existence of a SQL injection vulnerability by checking if a DNS request is made to a domain they control.

**Q3. How can SQL injection vulnerabilities be found during a black box and white box testing process?**

- **Black Box Testing**: 
  - **Map the Application**: Identify all input vectors and understand the application's logic.
  - **Fuzz the Application**: Input SQL-specific characters (e.g., single quotes, double quotes, `--`, `/* */) and observe the application's response.
  - **Check for Errors**: Look for SQL syntax errors that reveal the structure of the queries.
  - **Test for Blind SQL Injection**: Use Boolean conditions and time delays to determine if the application is vulnerable.
  - **Out-of-band Testing**: Trigger network interactions to a controlled server to check for out-of-band SQL injection.

- **White Box Testing**:
  - **Enable Logging**: Turn on web server and database logging to capture detailed information about SQL queries.
  - **Review Source Code**: Search for SQL query implementations and check for proper parameterization.
  - **Code Review**: Analyze the code for insecure functions and improper handling of user input.

**Q4. How can SQL injection vulnerabilities be exploited to gain unauthorized access or manipulate data?**

Exploitation methods vary based on the type of SQL injection vulnerability:

- **In-band SQL Injection**: Combine the results of two queries using the `UNION` operator to retrieve sensitive data.
- **Blind SQL Injection**: Use Boolean conditions or time delays to extract data piece by piece.
- **Out-of-band SQL Injection**: Trigger network interactions to exfiltrate data or confirm the presence of vulnerabilities.

For example, an attacker might use a `UNION` query to combine the results of a legitimate query with a query that retrieves usernames and passwords:

```sql
SELECT * FROM products WHERE id = 1 UNION SELECT username, password FROM users;
```

**Q5. Provide recent real-world examples of SQL injection vulnerabilities and explain how they were exploited.**

One notable example is the SQL injection vulnerability in the popular CMS platform WordPress (CVE-2019-9978). This vulnerability allowed attackers to execute arbitrary SQL commands by manipulating the `post_name` parameter in the REST API.

Another example is the SQL injection vulnerability in the Joomla CMS (CVE-2019-9661), which allowed attackers to execute SQL commands by manipulating the `id` parameter in the `com_content` component.

Both vulnerabilities were exploited by attackers to gain unauthorized access to databases and potentially steal sensitive data or take control of the affected websites.

**Q6. What are the recommended methods to prevent SQL injection vulnerabilities?**

The primary defense against SQL injection is the use of prepared statements or parameterized queries. These methods ensure that user input is treated as data rather than executable code.

- **Prepared Statements**: Define the structure of the query with placeholders for user input and then bind the actual values separately.
  
  ```java
  String sql = "SELECT * FROM users WHERE username = ?";
  PreparedStatement stmt = conn.prepareStatement(sql);
  stmt.setString(1, userInput);
  ResultSet rs = stmt.executeQuery();
  ```

- **Stored Procedures**: While not foolproof, stored procedures can help mitigate SQL injection by encapsulating complex logic in the database.

- **Input Validation**: Validate and sanitize user input to ensure it conforms to expected formats and lengths.

- **Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks, reducing the potential damage from a successful SQL injection attack.

**Q7. How can automated tools be used to detect and exploit SQL injection vulnerabilities?**

Automated tools like SQLmap can be used to detect and exploit SQL injection vulnerabilities:

- **Detection**: SQLmap can automatically identify SQL injection points by injecting various payloads and analyzing the application's responses.
- **Exploitation**: Once a vulnerability is detected, SQLmap can be used to extract data, dump the database schema, or even gain a shell on the server.

Other tools like web application vulnerability scanners (e.g., Nessus, Acunetix) can also be used to scan for SQL injection vulnerabilities, though they may not exploit them fully.

**Q8. What are the implications of SQL injection vulnerabilities in terms of confidentiality, integrity, and availability?**

- **Confidentiality**: SQL injection can be used to access sensitive data, such as usernames and passwords, leading to unauthorized disclosure.
- **Integrity**: Attackers can modify data in the database, altering records or inserting false data.
- **Availability**: SQL injection can disrupt services by causing denial of service conditions or by corrupting data, rendering the application unusable.

For example, an attacker might use SQL injection to reset a user's password by altering the email address in the database, thereby denying the legitimate user access to their account.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/19-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]]
