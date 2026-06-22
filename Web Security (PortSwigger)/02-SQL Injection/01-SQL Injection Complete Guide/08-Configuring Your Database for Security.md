---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Configuring Your Database for Security

### Least Privilege Principle

The principle of least privilege is a fundamental security concept that ensures that an application or user has only the minimum permissions necessary to perform their tasks. This reduces the potential damage that can be caused by an attacker who gains access to the system.

#### What is Least Privilege?

Least privilege means that an application or user should have only the permissions required to accomplish their specific tasks. For example, a web application that reads and writes to a database should not have permissions to delete tables or modify system settings.

#### Why is Least Privilege Important?

Implementing least privilege helps mitigate the impact of a successful attack. If an attacker gains access to a system with limited privileges, they will have fewer options for causing harm. This principle is particularly important in the context of SQL injection attacks, where an attacker might attempt to escalate their privileges to gain more control over the database.

#### How Does Least Privilege Work?

To implement least privilege, you should:

1. **Create a dedicated database user** for the application with minimal permissions.
2. **Grant only the necessary permissions** to this user. For example, if the application only needs to read from certain tables, grant only `SELECT` permissions.
3. **Regularly review and audit** the permissions to ensure they remain appropriate.

#### Example Configuration

Here’s an example of creating a database user with minimal permissions in MySQL:

```sql
CREATE USER 'webapp_user'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE ON mydatabase.mytable TO 'webapp_user'@'localhost';
```

In this example, `webapp_user` is granted only `SELECT`, `INSERT`, and `UPDATE` permissions on `mydatabase.mytable`.

### Removing Default Functionality

Default functionality often includes unnecessary features or configurations that can introduce vulnerabilities. Removing or disabling these features can help reduce the attack surface.

#### What is Default Functionality?

Default functionality refers to the pre-configured settings and features that come with a database out-of-the-box. These may include sample databases, default users, and other features that are not necessary for the application.

#### Why Remove Default Functionality?

Removing default functionality helps eliminate potential entry points for attackers. For example, default users with weak passwords can be easily exploited.

#### How to Remove Default Functionality

1. **Remove sample databases**: Sample databases often contain sensitive information that can be used to craft attacks.
2. **Disable default users**: Default users typically have weak passwords and should be disabled or removed.
3. **Review and disable unnecessary features**: Disable any features that are not required for the application.

#### Example Configuration

Here’s an example of removing a default user in MySQL:

```sql
DROP USER 'root'@'localhost';
```

This command removes the default `root` user from the database.

### Applying Vendor-Security Patches

Vendor-issued security patches are critical updates that address known vulnerabilities in the database software. Applying these patches promptly is essential to maintaining the security of the database.

#### What are Vendor-Security Patches?

Vendor-security patches are updates released by the database software provider to fix known vulnerabilities. These patches often include fixes for security issues such as SQL injection vulnerabilities.

#### Why Apply Vendor-Security Patches?

Applying vendor-security patches promptly helps protect the database against known vulnerabilities. Delaying the application of these patches increases the risk of exploitation.

#### How to Apply Vendor-Security Patches

1. **Monitor for updates**: Regularly check for updates from the database vendor.
2. **Test patches**: Test the patches in a non-production environment before applying them to production.
3. **Apply patches**: Once tested, apply the patches to the production environment.

#### Recent Real-World Examples

One notable example is the SQL injection vulnerability in Microsoft SQL Server (CVE-2019-0845). This vulnerability allowed attackers to execute arbitrary code on the server. Applying the vendor-provided patch was crucial to mitigating this risk.

### Whitelist Input Validation

Whitelist input validation is an additional layer of defense that complements parameterized queries. It ensures that only valid input values are accepted, reducing the risk of SQL injection attacks.

#### What is Whitelist Input Validation?

Whitelist input validation involves defining a set of valid input values and rejecting any input that does not match this set. This approach ensures that only expected and safe inputs are processed.

#### Why Use Whitelist Input Validation?

While parameterized queries are effective at preventing SQL injection, they do not address all input validation issues. Whitelist input validation provides an additional layer of protection by ensuring that only valid inputs are accepted.

#### How to Implement Whitelist Input Validation

1. **Define valid input patterns**: Define regular expressions or other patterns that represent valid input values.
2. **Validate input against patterns**: Validate user input against these patterns before processing it.
3. **Reject invalid input**: Reject any input that does not match the defined patterns.

#### Example Implementation

Here’s an example of implementing whitelist input validation in Python:

```python
import re

def validate_input(input_value):
    # Define a regex pattern for valid input
    pattern = r'^[a-zA-Z0-9]+$'
    
    # Validate input against the pattern
    if re.match(pattern, input_value):
        return True
    else:
        return False

# Example usage
input_value = "validInput123"
if validate_input(input_value):
    print("Input is valid")
else:
    print("Input is invalid")
```

In this example, the `validate_input` function checks if the input matches the defined pattern. If the input is valid, it proceeds; otherwise, it rejects the input.

### SQL Injection Attack Chain

A typical SQL injection attack chain involves several steps, including reconnaissance, exploitation, and post-exploitation activities. Understanding this chain helps in developing effective defenses.

#### Reconnaissance

Reconnaissance involves gathering information about the target system. Attackers may use tools like SQLMap to identify vulnerable parameters and extract database schema information.

#### Exploitation

Exploitation involves injecting malicious SQL code into the application. This can lead to unauthorized access to the database, data exfiltration, or even full system compromise.

#### Post-Exploitation

Post-exploitation activities may include escalating privileges, moving laterally within the network, or deploying malware.

### Real-World Example: CVE-2019-0845

CVE-2019-0845 is a SQL injection vulnerability in Microsoft SQL Server. This vulnerability allowed attackers to execute arbitrary code on the server, leading to potential data theft or system compromise.

#### Vulnerable Code

Here’s an example of vulnerable code that could be exploited:

```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password';
```

If `$username` and `$password` are not properly sanitized, an attacker could inject malicious SQL code.

#### Exploit Example

An attacker could inject the following payload:

```sql
$username = 'admin\' -- ';
$password = 'anything';
```

This would result in the following SQL query:

```sql
SELECT * FROM users WHERE username = 'admin' -- ' AND password = 'anything';
```

The `--` comment character effectively disables the rest of the query, allowing the attacker to bypass authentication.

#### Secure Code

To prevent this vulnerability, use parameterized queries:

```sql
SELECT * FROM users WHERE username = ? AND password = ?;
```

In this example, the `?` placeholders are replaced with actual values, preventing SQL injection.

### How to Prevent / Defend Against SQL Injection

#### Detection

Detecting SQL injection attempts involves monitoring logs and network traffic for suspicious activity. Tools like intrusion detection systems (IDS) can help identify potential attacks.

#### Prevention

Preventing SQL injection involves implementing the following measures:

1. **Use parameterized queries**: Ensure that all database interactions use parameterized queries.
2. **Whitelist input validation**: Validate user input against predefined patterns.
3. **Least privilege principle**: Grant only the necessary permissions to the application.
4. **Apply vendor-security patches**: Keep the database software up-to-date with the latest security patches.

#### Secure Coding Practices

Secure coding practices involve writing code that is resistant to SQL injection attacks. This includes:

1. **Using ORM frameworks**: Object-relational mapping (ORM) frameworks automatically handle parameterization.
2. **Sanitizing user input**: Sanitize user input to remove potentially harmful characters.
3. **Logging and monitoring**: Log and monitor database interactions to detect potential attacks.

#### Example of Secure Code

Here’s an example of secure code using parameterized queries in Python:

```python
import sqlite3

def get_user(username, password):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # Use parameterized query
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    
    user = cursor.fetchone()
    conn.close()
    
    return user
```

In this example, the `execute` method uses parameterized queries to prevent SQL injection.

### Hands-On Labs

For hands-on practice with SQL injection, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice SQL injection techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security attacks, including SQL injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These resources provide practical experience in identifying and defending against SQL injection attacks.

### Conclusion

SQL injection is a serious threat to web applications that interact with databases. By implementing the principles of least privilege, removing default functionality, applying vendor-security patches, and using whitelist input validation, you can significantly reduce the risk of SQL injection attacks. Additionally, understanding the attack chain and practicing secure coding techniques can further enhance the security of your applications.

By following these guidelines and utilizing the recommended resources, you can develop robust defenses against SQL injection and ensure the security of your web applications.

---
<!-- nav -->
[[07-Boolean-Based SQL Injection|Boolean-Based SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[09-Enabling Logging for Detection and Analysis|Enabling Logging for Detection and Analysis]]
