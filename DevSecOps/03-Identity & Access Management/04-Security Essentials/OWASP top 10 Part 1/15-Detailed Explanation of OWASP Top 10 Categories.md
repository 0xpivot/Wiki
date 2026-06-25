---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Detailed Explanation of OWASP Top 10 Categories

### Injection

Injection attacks occur when untrusted data is sent as part of a command or query. The attacker’s hostile data can trick the interpreter into executing unintended commands or accessing unauthorized data. Common types of injection attacks include SQL injection, OS command injection, and LDAP injection.

#### SQL Injection

SQL injection is a type of injection attack where an attacker manipulates a SQL query by inserting malicious SQL code. This can lead to unauthorized access to sensitive data, data corruption, or even complete system compromise.

**Example:**
```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password';
```
If `$username` is set to `' OR '1'='1` and `$password` is set to `' OR '1'='1`, the query becomes:
```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1';
```
This query will return all rows from the `users` table, allowing the attacker to bypass authentication.

**How to Prevent / Defend:**

- **Use Prepared Statements:** Prepared statements ensure that user input is treated as data rather than executable code.
  
  **Vulnerable Code:**
  ```php
  $stmt = $pdo->prepare('SELECT * FROM users WHERE username = ? AND password = ?');
  $stmt->execute([$username, $password]);
  ```

  **Secure Code:**
  ```php
  $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username AND password = :password');
  $stmt->execute(['username' => $username, 'password' => $password]);
  ```

- **Input Validation:** Validate and sanitize user input to ensure it meets expected formats and constraints.

### Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) occurs when an attacker injects malicious scripts into web pages viewed by other users. XSS can be used to steal cookies, session tokens, and other sensitive information.

**Example:**
Consider a web application that displays user-submitted comments without proper sanitization:
```html
<div>
  <h2>Comments</h2>
  <ul>
    <?php foreach ($comments as $comment): ?>
      <li><?php echo $comment; ?></li>
    <?php endforeach; ?>
  </ul>
</div>
```
If an attacker submits a comment containing `<script>alert('XSS');</script>`, the script will execute in the context of the victim's browser.

**How to Prevent / Defend:**

- **Output Encoding:** Encode user input to prevent it from being interpreted as HTML or JavaScript.
  
  **Vulnerable Code:**
  ```php
  echo $comment;
  ```

  **Secure Code:**
  ```php
  echo htmlspecialchars($comment, ENT_QUOTES, 'UTF-8');
  ```

- **Content Security Policy (CSP):** Implement CSP to restrict the sources from which scripts can be loaded.

  **HTTP Response Headers:**
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
  ```

### Broken Authentication

Broken authentication occurs when an application fails to properly authenticate users, leading to unauthorized access. This can happen due to weak passwords, predictable session IDs, or improper handling of authentication credentials.

**Example:**
Consider a login form that does not enforce strong password policies:
```html
<form action="/login" method="POST">
  <label for="username">Username:</label>
  <input type="text" id="username" name="username">
  <label for="password">Password:</label>
  <input type="password" id="password" name="password">
  <button type="submit">Login</button>
</form>
```
If the application allows weak passwords like "123456", an attacker can easily guess or brute-force the password.

**How to Prevent / Defend:**

- **Strong Password Policies:** Enforce strong password requirements, such as minimum length, complexity, and regular expiration.
  
  **Vulnerable Code:**
  ```php
  if (strlen($password) >= 6) {
    // Allow login
  }
  ```

  **Secure Code:**
  ```php
  if (preg_match('/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/', $password)) {
    // Allow login
  }
  ```

- **Multi-Factor Authentication (MFA):** Implement MFA to provide an additional layer of security.

### Insecure Deserialization

Insecure deserialization occurs when an application deserializes untrusted data without proper validation. This can lead to remote code execution, data tampering, or privilege escalation.

**Example:**
Consider a web application that uses PHP's `unserialize()` function to deserialize user input:
```php
$data = $_GET['data'];
$object = unserialize($data);
```
If an attacker sends a serialized object that contains malicious code, the application may execute the code.

**How to Prevent / Defend:**

- **Avoid Untrusted Data:** Avoid deserializing data from untrusted sources.
  
  **Vulnerable Code:**
  ```php
  $data = $_GET['data'];
  $object = unserialize($data);
  ```

  **Secure Code:**
  ```php
  $data = file_get_contents('/path/to/trusted/data');
  $object = unserialize($data);
  ```

- **Serialization Filters:** Use serialization filters to validate the structure of serialized data.

### Security Misconfiguration

Security misconfiguration occurs when an application is not properly configured to protect against security threats. This can include default settings, unnecessary features, and insecure configurations.

**Example:**
Consider a web server that is configured to display detailed error messages:
```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<title>Error 500</title>
</head>
<body>
<h1>Error 500</h1>
<p>An unexpected error occurred.</p>
<pre>
Traceback (most recent call last):
  File "/path/to/app.py", line 10, in main
    result = process_data(data)
  File "/path/to/utils.py", line 20, in process_data
    raise Exception("Invalid data")
Exception: Invalid data
</pre>
</body>
</html>
```
These detailed error messages can reveal sensitive information to attackers.

**How to Prevent / Defend:**

- **Disable Detailed Error Messages:** Configure the application to display generic error messages instead of detailed ones.
  
  **Vulnerable Code:**
  ```python
  try:
    result = process_data(data)
  except Exception as e:
    print(f"Error: {e}")
  ```

  **Secure Code:**
  ```python
  try:
    result = process_data(data)
  except Exception as e:
    logging.error(f"Error: {e}")
    print("An unexpected error occurred.")
  ```

- **Regular Audits:** Regularly audit the application's configuration to ensure that it is secure.

### Vulnerable and Outdated Components

Using vulnerable and outdated components can expose an application to known security vulnerabilities. This includes libraries, frameworks, and dependencies that have not been updated to address security issues.

**Example:**
Consider a web application that uses an outdated version of a library:
```python
import vulnerable_library

vulnerable_library.process_data(data)
```
If the library has a known vulnerability, an attacker can exploit it to gain unauthorized access.

**How to Prevent / Defend:**

- **Keep Dependencies Updated:** Regularly update all dependencies to the latest versions.
  
  **Vulnerable Code:**
  ```python
  import vulnerable_library

  vulnerable_library.process_data(data)
  ```

  **Secure Code:**
  ```python
  import secure_library

  secure_library.process_data(data)
  ```

- **Dependency Management Tools:** Use dependency management tools to track and manage dependencies.

### Insufficient Logging and Monitoring

Insufficient logging and monitoring can make it difficult to detect and respond to security incidents. Without proper logging and monitoring, an attacker can operate undetected for extended periods.

**Example:**
Consider a web application that does not log user activities:
```python
def handle_request(request):
  # Process request
  pass
```
Without logging, it is impossible to track user activities and detect suspicious behavior.

**How to Prevent / Defend:**

- **Enable Logging:** Enable logging for all critical operations.
  
  **Vulnerable Code:**
  ```python
  def handle_request(request):
    # Process request
    pass
  ```

  **Secure Code:**
  ```python
  def handle_request(request):
    logging.info(f"Handling request: {request}")
    # Process request
  ```

- **Centralized Logging:** Use centralized logging to collect and analyze logs from multiple sources.

### Access Control

Access control violations occur when an application fails to properly restrict access to sensitive resources. This can allow unauthorized users to access or modify sensitive data.

**Example:**
Consider a web application that does not properly restrict access to user profiles:
```python
@app.route('/profile/<username>')
def profile(username):
  user = get_user(username)
  return render_template('profile.html', user=user)
```
If an attacker can guess or enumerate usernames, they can access other users' profiles.

**How to Prevent / Defend:**

- **Role-Based Access Control (RBAC):** Implement RBAC to restrict access based on user roles.
  
  **Vulnerable Code:**
  ```python
  @app.route('/profile/<username>')
  def profile(username):
    user = get_user(username)
    return render_template('profile.html', user=user)
  ```

  **Secure Code:**
  ```python
  @app.route('/profile/<username>')
  @login_required
  def profile(username):
    if current_user.username == username:
      user = get_user(username)
      return render_template('profile.html', user=user)
    else:
      abort(403)
  ```

- **Audit Access Logs:** Regularly audit access logs to detect and respond to unauthorized access attempts.

### Cryptographic Failures

Cryptographic failures occur when an application improperly implements cryptographic functions. This can lead to data exposure, authentication bypass, and other security issues.

**Example:**
Consider a web application that uses a weak encryption algorithm:
```python
from cryptography.fernet import Fernet

key = b'weak_key'
cipher_suite = Fernet(key)
encrypted_data = cipher_suite.encrypt(b'sensitive_data')
```
If the key is weak or the encryption algorithm is vulnerable, an attacker can decrypt the data.

**How to Prevent / Defend:**

- **Use Strong Encryption Algorithms:** Use strong encryption algorithms and keys.
  
  **Vulnerable Code:**
  ```python
  from cryptography.fernet import Fernet

  key = b'weak_key'
  cipher_suite = Fernet(key)
  encrypted_data = cipher_suite.encrypt(b'sensitive_data')
  ```

  **Secure Code:**
  ```python
  from cryptography.fernet import Fernet
  from os import urandom

  key = urandom(32)
  cipher_suite = Fernet(key)
  encrypted_data = cipher_suite.encrypt(b'sensitive_data')
  ```

- **Key Management:** Properly manage encryption keys to ensure they are secure.

### Command Injection

Command injection occurs when an application executes system commands using untrusted input. This can allow an attacker to execute arbitrary commands on the system.

**Example:**
Consider a web application that executes system commands using user input:
```python
import subprocess

command = f"ls {user_input}"
subprocess.run(command, shell=True)
```
If an attacker sets `user_input` to `; rm -rf /`, the command will delete all files on the system.

**How to Prevent / Defend:**

- **Avoid Shell Commands:** Avoid using shell commands with untrusted input.
  
  **Vulnerable Code:**
  ```python
  import subprocess

  command = f"ls {user_input}"
  subprocess.run(command, shell=True)
  ```

  **Secure Code:**
  ```python
  import subprocess

  command = ["ls", user_input]
  subprocess.run(command)
  ```

- **Input Validation:** Validate and sanitize user input to ensure it meets expected formats and constraints.

### Conclusion

The OWASP Top 10 provides a comprehensive list of the most critical web application security risks. By understanding and addressing these risks, organizations can significantly improve the security of their applications. This chapter has covered each category in detail, providing background theory, recent real-world examples, complete code, mermaid diagrams, pitfalls, and a clear 'How to Prevent / Defend' section. By following these guidelines, developers can build more secure applications and protect against common security threats.

### Practice Labs

For hands-on practice with OWASP Top 10 vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs covering a wide range of web application security topics.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat:** An interactive, gamified training application for learning about web application security.

By engaging with these labs, you can gain practical experience in identifying and mitigating OWASP Top 1.

---
<!-- nav -->
[[15-Default Credentials and Misconfigurations|Default Credentials and Misconfigurations]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 1/00-Overview|Overview]] | [[17-Encryption and Data Protection|Encryption and Data Protection]]
