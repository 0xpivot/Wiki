---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Understanding SQL Injection in API Endpoints

SQL Injection (SQLi) is a type of security vulnerability that allows an attacker to manipulate database queries by injecting malicious SQL code through input fields. This can lead to unauthorized access to sensitive data, data corruption, or even complete control of the database. In the context of API endpoints, SQLi can occur when user inputs are improperly sanitized and directly included in SQL queries.

### What is SQL Injection?

SQL Injection occurs when an attacker manipulates a SQL query by inserting or "injecting" additional SQL code into the input fields of a web application. This can happen in various parts of the application, such as login forms, search boxes, or any other input field that interacts with the database.

#### Why Does SQL Injection Matter?

SQL Injection is a critical security issue because it can lead to severe consequences:

- **Data Exposure**: Attackers can extract sensitive information like passwords, personal details, and financial data.
- **Data Manipulation**: Attackers can modify or delete data within the database.
- **Privilege Escalation**: In some cases, attackers can gain administrative privileges and take full control of the database.

### How Does SQL Injection Work?

To understand SQL Injection, let's consider a simple example. Suppose we have an API endpoint that accepts a username and password and checks them against a database:

```python
def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = execute_query(query)
    return result
```

If an attacker provides the following input:

- `username`: `admin' --`
- `password`: `anything`

The resulting SQL query would be:

```sql
SELECT * FROM users WHERE username='admin' --' AND password='anything'
```

Here, the `--` is a comment in SQL, which effectively ignores the rest of the query. As a result, the query becomes:

```sql
SELECT * FROM users WHERE username='admin'
```

This allows the attacker to bypass authentication and log in as the admin user.

### Real-World Examples of SQL Injection

SQL Injection vulnerabilities have been exploited in numerous high-profile breaches. Here are a couple of recent examples:

- **CVE-2021-3129**: A SQL Injection vulnerability was found in the WordPress plugin "WP eCommerce". An attacker could inject malicious SQL code through the search functionality, leading to unauthorized access to the database.
- **CVE-2020-14882**: A SQL Injection vulnerability was discovered in the Joomla CMS. Attackers could exploit this vulnerability to execute arbitrary SQL commands, potentially gaining administrative access to the site.

### Finding SQL Injection Vulnerabilities in API Endpoints

To find SQL Injection vulnerabilities in API endpoints, you need to test the input fields for improper sanitization. Here’s a step-by-step guide:

1. **Identify Input Fields**: Determine which API endpoints accept user input.
2. **Test with Malicious Inputs**: Provide inputs that include SQL syntax, such as single quotes (`'`) or semicolons (`;`).
3. **Analyze Responses**: Look for signs of SQL errors or unexpected behavior in the API responses.

#### Example: Testing an API Endpoint

Consider an API endpoint `/api/users/login` that accepts a `username` and `password`. You can test this endpoint using tools like `curl` or Postman.

**Vulnerable Code Example:**

```python
@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = execute_query(query)
    
    if result:
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "failure", "message": "Invalid credentials"})
```

**Testing with `curl`:**

```sh
curl -X POST http://localhost:5000/api/users/login -H "Content-Type: application/json" -d '{"username": "admin\' --", "password": "anything"}'
```

**Expected Response:**

```json
{
  "status": "success",
  "message": "Login successful"
}
```

If the response indicates a successful login, it suggests that the endpoint is vulnerable to SQL Injection.

### How to Prevent / Defend Against SQL Injection

Preventing SQL Injection requires a combination of proper coding practices, input validation, and the use of secure coding techniques.

#### Secure Coding Practices

1. **Use Prepared Statements**: Prepared statements ensure that user inputs are treated as data rather than executable code.
2. **Parameterized Queries**: Parameterized queries separate the SQL logic from the user inputs, preventing SQL Injection.

**Secure Code Example:**

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username, password=password).first()
    
    if user:
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "failure", "message": "Invalid credentials"})

if __name__ == '__main__':
    app.run(debug=True)
```

#### Input Validation

Validate all user inputs to ensure they meet expected formats and constraints. Use regular expressions or built-in validation libraries to enforce these rules.

**Example: Input Validation with Regular Expressions:**

```python
import re

def validate_username(username):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username format")

def validate_password(password):
    if not re.match(r'^.{8,}$', password):
        raise ValueError("Password must be at least 8 characters long")
```

#### Detection and Monitoring

Regularly scan your applications for SQL Injection vulnerabilities using automated tools like SQLMap, Burp Suite, or OWASP ZAP. Monitor your logs for suspicious activities that might indicate an SQL Injection attempt.

### Practice Labs for SQL Injection

To practice detecting and preventing SQL Injection, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about SQL Injection and other web security vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

By thoroughly understanding SQL Injection and implementing secure coding practices, you can protect your APIs from this critical vulnerability.

---
<!-- nav -->
[[API Security/11-SQL Injection/01-Admin Token Bypassing SQL Injection/02-SQL Injection Overview|SQL Injection Overview]] | [[API Security/11-SQL Injection/01-Admin Token Bypassing SQL Injection/00-Overview|Overview]] | [[API Security/11-SQL Injection/01-Admin Token Bypassing SQL Injection/04-Practice Questions & Answers|Practice Questions & Answers]]
