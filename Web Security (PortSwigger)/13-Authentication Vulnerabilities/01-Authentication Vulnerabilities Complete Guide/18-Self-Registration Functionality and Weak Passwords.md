---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Self-Registration Functionality and Weak Passwords

### Background Theory

Self-registration functionality is a common feature in web applications, allowing users to create their own accounts. This feature can be exploited if the application does not enforce strong password policies. Weak passwords are easily guessable and can lead to unauthorized access to user accounts. 

### Identifying Weak Passwords

To identify weak passwords, one can attempt to register accounts with various types of weak passwords:

1. **Very Short Passwords**: These are typically less than 8 characters long and can be easily guessed.
2. **Blank Passwords**: An empty password field can be accepted by some applications.
3. **Common Dictionary Words**: These are simple words found in dictionaries, such as "password", "123456", etc.
4. **Password Same as Username**: This is a common mistake where the password is set to the same value as the username.

#### Example Code for Registration

Here is an example of how a registration form might look in HTML:

```html
<form action="/register" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required>
    
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required>
    
    <button type="submit">Register</button>
</form>
```

And the corresponding server-side validation in Python using Flask:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # Check for weak passwords
    if len(password) < 8 or password == '' or password.isalpha() or password == username:
        return "Weak password detected. Please choose a stronger password."
    
    # Proceed with registration logic
    # ...
    
    return "Registration successful."

if __name__ == '__main__':
    app.run(debug=True)
```

### Reporting Weak Passwords

If you identify that the application allows weak passwords, it should be reported as a finding in your penetration test report. This is crucial because weak passwords can be easily exploited by attackers.

### Change Password Functionality

Sometimes, developers enforce strong password policies during the initial account creation but forget to apply the same rules when users change their passwords. This can lead to vulnerabilities.

#### Example Code for Change Password

Here is an example of how a change password form might look in HTML:

```html
<form action="/change_password" method="POST">
    <label for="current_password">Current Password:</label>
    <input type="password" id="current_password" name="current_password" required>
    
    <label for="new_password">New Password:</label>
    <input type="password" id="new_password" name="new_password" required>
    
    <button type="submit">Change Password</button>
</form>
```

And the corresponding server-side validation in Python using Flask:

```python
@app.route('/change_password', methods=['POST'])
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    
    # Check for weak passwords
    if len(new_password) < 8 or new_password == '' or new_password.isalpha() or new_password == current_password:
        return "Weak password detected. Please choose a stronger password."
    
    # Proceed with password change logic
    # ...
    
    return "Password changed successfully."
```

### How to Prevent / Defend Against Weak Passwords

#### Secure Coding Practices

Ensure that both the registration and change password functionalities enforce strong password policies. Here is an example of a secure password policy:

```python
import re

def is_strong_password(password):
    if len(password) < 8:
        return False
    if re.search(r'\d', password) is None:
        return False
    if re.search(r'[A-Z]', password) is None:
        return False
    if re.search(r'[a-z]', password) is None:
        return False
    return True
```

#### Detection

Use automated tools like `ZAP` (Zed Attack Proxy) or `Burp Suite` to test for weak password enforcement. These tools can automatically detect and report weak password policies.

#### Prevention

1. **Enforce Strong Password Policies**: Ensure that passwords meet certain criteria, such as minimum length, inclusion of numbers, uppercase letters, lowercase letters, and special characters.
2. **Educate Users**: Provide guidance to users on creating strong passwords.
3. **Regular Audits**: Regularly audit the application to ensure that password policies are consistently enforced.

### Recent Real-World Examples

#### CVE-2021-31166

In 2021, a vulnerability was discovered in a popular web application where users could register with weak passwords. This allowed attackers to gain unauthorized access to user accounts. The application did not enforce strong password policies, leading to widespread exploitation.

### Improper Restriction of Authentication Attempts

### Background Theory

Improper restriction of authentication attempts refers to the lack of mechanisms to prevent brute-force attacks. Brute-force attacks involve systematically trying different combinations of usernames and passwords until the correct one is found.

### Identifying Lack of Lockout Mechanism

To test for the presence of a lockout mechanism, manually submit several bad login attempts to accounts that you control. If after 10 failed login attempts, you do not get locked out, then chances are there is no lockout mechanism.

#### Example Code for Login Form

Here is an example of how a login form might look in HTML:

```html
<form action="/login" method="POST">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required>
    
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required>
    
    <button type="submit">Login</button>
</form>
```

And the corresponding server-side validation in Python using Flask:

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Check credentials
    if username == 'admin' and password == 'admin':
        return "Login successful."
    else:
        return "Invalid credentials."
```

### How to Prevent / Defend Against Improper Restriction of Authentication Attempts

#### Secure Coding Practices

Implement a lockout mechanism that temporarily locks an account after a certain number of failed login attempts. Here is an example of how to implement a simple lockout mechanism in Python:

```python
from flask import session

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Increment failed login attempts
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0
    session['failed_attempts'] += 1
    
    # Check credentials
    if username == 'admin' and password == 'admin':
        session['failed_attempts'] = 0
        return "Login successful."
    else:
        if session['failed_attempts'] >= 10:
            return "Account locked due to too many failed attempts."
        else:
            return "Invalid credentials."
```

#### Detection

Use automated tools like `ZAP` or `Burp Suite` to test for the presence of a lockout mechanism. These tools can simulate multiple failed login attempts and report whether the account gets locked out.

#### Prevention

1. **Implement Lockout Mechanisms**: Ensure that accounts are locked out after a certain number of failed login attempts.
2. **Monitor Failed Login Attempts**: Monitor the number of failed login attempts and take appropriate action if the threshold is exceeded.
3. **Educate Users**: Inform users about the importance of strong passwords and the risks associated with weak passwords.

### Recent Real-World Examples

#### CVE-2_2021-44228

In 2021, a vulnerability was discovered in a web application where the application did not have a lockout mechanism. This allowed attackers to perform brute-force attacks and gain unauthorized access to user accounts. The application did not enforce any restrictions on the number of failed login attempts, leading to widespread exploitation.

### Conclusion

Authentication vulnerabilities are a significant threat to web applications. Ensuring strong password policies and implementing proper lockout mechanisms are crucial steps in securing authentication processes. By following secure coding practices and regularly auditing the application, you can significantly reduce the risk of authentication-related vulnerabilities.

### Practice Labs

For hands-on practice with authentication vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on authentication vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat**: An interactive training application designed to teach web security.

These labs provide practical experience in identifying and mitigating authentication vulnerabilities.

---
<!-- nav -->
[[17-Real-Time Password Strength Feedback|Real-Time Password Strength Feedback]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[19-Storing Passwords Securely|Storing Passwords Securely]]
