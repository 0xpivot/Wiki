---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Storing Passwords Securely

### Introduction to Password Storage

Password storage is one of the most critical aspects of web security. When passwords are stored securely, it significantly reduces the risk of unauthorized access to user accounts. However, many systems still store passwords in plain text, which is highly insecure. In this section, we will explore why storing passwords in plain text is dangerous, how to properly hash passwords, and how to implement a secure password reset mechanism.

### Plain Text Password Storage

#### What is Plain Text Password Storage?

Plain text password storage means that passwords are stored in an unencrypted form within the database. This means that anyone with access to the database can read the passwords directly.

#### Why is Plain Text Password Storage Insecure?

Storing passwords in plain text is extremely insecure because:

- **Data Breaches**: If the database is compromised, attackers can easily read all the passwords.
- **Insider Threats**: Employees or contractors with access to the database can view and misuse the passwords.
- **Compliance Issues**: Many regulations require passwords to be stored securely. Storing passwords in plain text can lead to legal issues and fines.

#### Real-World Example: LinkedIn Data Breach (CVE-2012-0830)

In 2012, LinkedIn suffered a massive data breach where 6.5 million hashed passwords were stolen. However, the passwords were initially stored in plain text, and the breach occurred after they were hashed. This incident highlights the importance of proper password storage practices.

### Hashing Passwords

#### What is Hashing?

Hashing is a process that converts a password into a fixed-length string of characters using a mathematical algorithm. The resulting string is called a hash. Hashing is a one-way function, meaning that it is computationally infeasible to reverse-engineer the original password from the hash.

#### Why Use Hashing?

Using hashing provides several benefits:

- **Security**: Hashes cannot be reversed to obtain the original password.
- **Consistency**: The same input always produces the same output.
- **Speed**: Hashing is fast, making it suitable for real-time applications.

#### Common Hashing Algorithms

Some commonly used hashing algorithms include:

- **MD5**: Although widely used, MD5 is considered weak due to collision vulnerabilities.
- **SHA-256**: A more secure alternative to MD5, providing better resistance against attacks.
- **bcrypt**: A slow hashing algorithm designed specifically for password hashing, making it resistant to brute-force attacks.

#### How to Implement Hashing

To implement hashing, you can use libraries such as `bcrypt` in Python. Here’s an example of how to hash a password using `bcrypt`:

```python
import bcrypt

# Generate a salt
salt = bcrypt.gensalt()

# Hash the password
password = b"mysecretpassword"
hashed_password = bcrypt.hashpw(password, salt)

print(hashed_password)
```

### Salted Hashing

#### What is Salted Hashing?

Salted hashing adds a unique value (the salt) to the password before hashing. This ensures that even identical passwords produce different hashes, making rainbow table attacks much harder.

#### How to Implement Salted Hashing

Here’s an example of how to implement salted hashing using `bcrypt`:

```python
import bcrypt

# Generate a salt
salt = bcrypt.gensalt()

# Hash the password with the salt
password = b"mysecretpassword"
hashed_password = bcrypt.hashpw(password, salt)

print(hashed_password)
```

### Password Reset Mechanism

#### What is a Password Reset Mechanism?

A password reset mechanism allows users to regain access to their account if they forget their password. This is typically done via email or SMS verification.

#### Why is a Password Reset Mechanism Important?

A password reset mechanism is important because:

- **User Convenience**: Users can recover their accounts without needing to contact support.
- **Security**: It provides a secure method for users to regain access to their accounts.

#### How to Implement a Password Reset Mechanism

To implement a password reset mechanism, follow these steps:

1. **Generate a Unique Token**: Create a unique token for the reset link.
2. **Send the Token**: Send the token to the user via email or SMS.
3. **Validate the Token**: When the user clicks the link, validate the token.
4. **Reset the Password**: Allow the user to set a new password.

Here’s an example implementation using Flask:

```python
from flask import Flask, request, redirect, url_for
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Serializer for generating and validating tokens
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form['email']
    token = ts.dumps(email, salt='recover-key')
    reset_link = url_for('confirm_reset', token=token, _external=True)
    # Send the reset link to the user via email
    return redirect(reset_link)

@app.route('/confirm-reset/<token>', methods=['GET', 'POST'])
def confirm_reset(token):
    try:
        email = ts.loads(token, salt='recover-key', max_age=3600)
    except:
        return "The link is invalid or has expired."
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        # Update the password in the database
        return "Password successfully reset!"
    
    return "Please enter your new password."

if __name__ == '__main__':
    app.run(debug=True)
```

### Testing for Plain Text Password Storage

#### How to Test for Plain Text Password Storage

There are several ways to test whether passwords are stored in plain text:

1. **Remote Code Execution**: If you have remote code execution on the server, you can access the database directly and check the password storage format.
2. **Technical Interviews**: Conduct technical interviews with developers to review how passwords are stored in the backend database.

#### Example of Remote Code Execution

If you have remote code execution on the server, you can access the database and check the password storage format. Here’s an example using SQL:

```sql
SELECT * FROM users;
```

This will show you the password field in the database. If the passwords are stored in plain text, you will see them directly.

### Automated Tools for Testing Authentication Vulnerabilities

#### What are Web Application Vulnerability Scanners?

Web application vulnerability scanners are automated tools that crawl your web application and look for vulnerabilities. They can identify various types of authentication flaws, including plain text password storage.

#### Popular Web Application Vulnerability Scanners

Some popular web application vulnerability scanners include:

- **OWASP ZAP**
- **Burp Suite**
- **Nexpose**

These tools can help you identify and mitigate authentication vulnerabilities in your web application.

### Hands-On Labs for Exploiting Authentication Vulnerabilities

To gain hands-on experience in exploiting authentication vulnerabilities, you can use the following labs:

- **PortSwigger Web Security Academy**
- **OWASP Juice Shop**
- **DVWA (Damn Vulnerable Web Application)**
- **WebGoat**

These labs provide a safe environment to practice and learn about various authentication vulnerabilities.

### How to Prevent / Defend Against Plain Text Password Storage

#### Detection

To detect plain text password storage, you can:

- **Review Database Schema**: Check the schema of the database to ensure passwords are not stored in plain text.
- **Use Vulnerability Scanners**: Use automated tools to scan for vulnerabilities.

#### Prevention

To prevent plain text password storage, you should:

- **Hash Passwords**: Always hash passwords using a strong hashing algorithm like `bcrypt`.
- **Use Salts**: Use salts to ensure that even identical passwords produce different hashes.
- **Implement Secure Password Reset Mechanisms**: Provide a secure method for users to reset their passwords.

#### Secure Coding Fixes

Here’s an example of a vulnerable code and its secure counterpart:

**Vulnerable Code:**

```python
import sqlite3

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
```

**Secure Code:**

```python
import sqlite3
import bcrypt

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
```

### Conclusion

Proper password storage is crucial for maintaining the security of web applications. By hashing passwords and implementing secure password reset mechanisms, you can significantly reduce the risk of unauthorized access. Additionally, using automated tools and hands-on labs can help you identify and mitigate authentication vulnerabilities effectively.

By following the best practices outlined in this guide, you can ensure that your web application is secure and protected against common authentication vulnerabilities.

---
<!-- nav -->
[[18-Self-Registration Functionality and Weak Passwords|Self-Registration Functionality and Weak Passwords]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[20-Unencrypted HTTP Traffic and Authentication Vulnerabilities|Unencrypted HTTP Traffic and Authentication Vulnerabilities]]
