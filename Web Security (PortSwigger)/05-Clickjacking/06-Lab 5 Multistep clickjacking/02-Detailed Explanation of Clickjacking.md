---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Detailed Explanation of Clickjacking

### What is Clickjacking?

Clickjacking, also known as UI Redress Attack, is a malicious technique used by attackers to trick users into clicking on hidden buttons or links. This can lead to unauthorized actions being performed on behalf of the user, such as changing settings, deleting accounts, or making purchases. The attacker achieves this by overlaying a transparent or opaque layer over the legitimate website, which the user interacts with unknowingly.

### Why Does Clickjacking Matter?

Clickjacking is significant because it can lead to serious security breaches. Users may inadvertently perform actions that they did not intend to, leading to data loss, financial damage, or other negative consequences. For example, a user might think they are clicking on a benign button, but they are actually clicking on a hidden iframe that deletes their account or changes their email address.

### How Does Clickjacking Work?

To understand clickjacking, let's break down the process:

1. **Embedding the Target Website**: The attacker embeds the target website within an iframe on their malicious site.
2. **Overlaying Transparent Layers**: The attacker uses CSS to overlay transparent layers on top of the iframe, making it difficult for the user to see the actual content.
3. **User Interaction**: When the user clicks on what they believe to be a benign button or link, they are actually interacting with the hidden iframe.

### Example Scenario

Consider a scenario where a user wants to update their email address on a legitimate website. The attacker can create a malicious page that embeds the legitimate website within an iframe and overlays a transparent layer on top of it. When the user clicks on the "Update Email" button, they are actually clicking on the hidden iframe, which performs the action on the legitimate website.

### Real-World Examples

Recent real-world examples of clickjacking attacks include:

- **CVE-2019-1133**: A clickjacking vulnerability was discovered in the Microsoft Office suite, allowing attackers to trick users into granting administrative privileges.
- **CVE-2020-13777**: A clickjacking vulnerability was found in the Cisco Webex Meetings client, enabling attackers to execute arbitrary commands on the victim's machine.

### Prevention and Detection

To prevent clickjacking attacks, websites should implement security measures such as the X-Frame-Options header, Content Security Policy (CSP), and secure coding practices.

#### X-Frame-Options Header

The X-Frame-Options header is used to indicate whether or not a browser should be allowed to render a page in a frame or iframe. There are three possible values:

- `DENY`: The page cannot be displayed in a frame.
- `SAMEORIGIN`: The page can only be displayed in a frame on the same origin as the page itself.
- `ALLOW-FROM uri`: The page can only be displayed in a frame on the specified origin.

```http
HTTP/1.1 200 OK
Content-Type: text/html
X-Frame-Options: SAMEORIGIN
```

#### Content Security Policy (CSP)

Content Security Policy (CSP) is a security feature that helps to detect and mitigate certain types of attacks, including clickjacking. CSP allows you to specify which sources of content are permitted to load in your web pages.

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'self'
```

### Secure Coding Practices

Secure coding practices involve ensuring that user interactions are properly validated and authenticated. For example, when updating an email address, the system should require the user to re-enter their password or provide a one-time verification code.

#### Vulnerable Code Example

```python
# Vulnerable code example
@app.route('/update_email', methods=['POST'])
def update_email():
    new_email = request.form['new_email']
    user_id = session['user_id']
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return redirect('/')
```

#### Secure Code Example

```python
# Secure code example
@app.route('/update_email', methods=['POST'])
def update_email():
    new_email = request.form['new_email']
    user_id = session['user_id']
    password = request.form['password']
    
    # Verify the user's password
    stored_password_hash = db.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    if not check_password_hash(stored_password_hash, password):
        return "Invalid password", 401
    
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return redirect('/')
```

### Lab Exercises

To practice and understand clickjacking, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security vulnerabilities, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Clickjacking is a serious security threat that can lead to unauthorized actions being performed on behalf of the user. By understanding how clickjacking works and implementing proper security measures, you can protect your web applications from such attacks.

### Detailed Explanation of Clickjacking

### What is Clickjacking?

Clickjacking, also known as UI Redress Attack, is a malicious technique used by attackers to trick users into clicking on hidden buttons or links. This can lead to unauthorized actions being performed on behalf of the user, such as changing settings, deleting accounts, or making purchases. The attacker achieves this by overlaying a transparent or opaque layer over the legitimate website, which the user interacts with unknowingly.

### Why Does Clickjacking Matter?

Clickjacking is significant because it can lead to serious security breaches. Users may inadvertently perform actions that they did not intend to, leading to data loss, financial damage, or other negative consequences. For example, a user might think they are clicking on a benign button, but they are actually clicking on a hidden iframe that deletes their account or changes their email address.

### How Does Clickjacking Work?

To understand clickjacking, let's break down the process:

1. **Embedding the Target Website**: The attacker embeds the target website within an iframe on their malicious site.
2. **Overlaying Transparent Layers**: The attacker uses CSS to overlay transparent layers on top of the iframe, making it difficult for the user to see the actual content.
3. **User Interaction**: When the user clicks on what they believe to be a benign button or link, they are actually interacting with the hidden iframe.

### Example Scenario

Consider a scenario where a user wants to update their email address on a legitimate website. The attacker can create a malicious page that embeds the legitimate website within an iframe and overlays a transparent layer on top of it. When the user clicks on the "Update Email" button, they are actually clicking on the hidden iframe, which performs the action on the legitimate website.

### Real-World Examples

Recent real-world examples of clickjacking attacks include:

- **CVE-2019-1133**: A clickjacking vulnerability was discovered in the Microsoft Office suite, allowing attackers to trick users into granting administrative privileges.
- **CVE-2020-13777**: A clickjacking vulnerability was found in the Cisco Webex Meetings client, enabling attackers to execute arbitrary commands on the victim's machine.

### Prevention and Detection

To prevent clickjacking attacks, websites should implement security measures such as the X-Frame-Options header, Content Security Policy (CSP), and secure coding practices.

#### X-Frame-Options Header

The X-Frame-Options header is used to indicate whether or not a browser should be allowed to render a page in a frame or iframe. There are three possible values:

- `DENY`: The page cannot be displayed in a frame.
- `SAMEORIGIN`: The page can only be displayed in a frame on the same origin as the page itself.
- `ALLOW-FROM uri`: The page can only be displayed in a frame on the specified origin.

```http
HTTP/1.1 200 OK
Content-Type: text/html
X-Frame-Options: SAMEORIGIN
```

#### Content Security Policy (CSP)

Content Security Policy (CSP) is a security feature that helps to detect and mitigate certain types of attacks, including clickjacking. CSP allows you to specify which sources of content are permitted to load in your web pages.

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'self'
```

### Secure Coding Practices

Secure coding practices involve ensuring that user interactions are properly validated and authenticated. For example, when updating an email address, the system should require the user to re-enter their password or provide a one-time verification code.

#### Vulnerable Code Example

```python
# Vulnerable code example
@app.route('/update_email', methods=['POST'])
def update_email():
    new_email = request.form['new_email']
    user_id = session['user_id']
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return redirect('/')
```

#### Secure Code Example

```python
# Secure code example
@app.route('/update_email', methods=['POST'])
def update_email():
    new_email = request.form['new_email']
    user_id = session['user_id']
    password = request.form['password']
    
    # Verify the user's password
    stored_password_hash = db.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    if not check_password_hash(stored_password_hash, password):
        return "Invalid password", 401
    
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return redirect('/')
```

### Lab Exercises

To practice and understand clickjacking, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security vulnerabilities, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Clickjacking is a serious security threat that can lead to unauthorized actions being performed on behalf of the user. By understanding how clickjacking works and implementing proper security measures, you can protect your web applications from such attacks.

### Detailed Explanation of Clickjacking

### What is Clickjacking?

Clickjacking, also known as UI Redress Attack, is a malicious technique used by attackers to trick users into clicking on hidden buttons or links. This can lead to unauthorized actions being performed on behalf of the user, such as changing settings, deleting accounts, or making purchases. The attacker achieves this by overlaying a transparent or opaque layer over the legitimate website, which the user interacts with unknowingly.

### Why Does Clickjacking Matter?

Clickjacking is significant because it can lead to serious security breaches. Users may inadvertently perform actions that they did not intend to, leading to data loss, financial damage, or other negative consequences. For example, a user might think they are clicking on a benign button, but they are actually clicking on a hidden iframe that deletes their account or changes their email address.

### How Does Clickjacking Work?

To understand clickjacking, let's break down the process:

1. **Embedding the Target Website**: The attacker embeds the target website within an iframe on their malicious site.
2. **Overlaying Transparent Layers**: The attacker uses CSS to overlay transparent layers on top of the iframe, making it difficult for the user to see the actual content.
3. **User Interaction**: When the user clicks on what they believe to be a benign button or link, they are actually interacting with the hidden iframe.

### Example Scenario

Consider a scenario where a user wants to update their email address on a legitimate website. The attacker can create a malicious page that embeds the legitimate website within an iframe and overlays a transparent layer on top of it. When the user clicks on the "Update Email" button, they are actually clicking on the hidden iframe, which performs the action on the legitimate website.

### Real-World Examples

Recent real-world examples of clickjacking attacks include:

- **CVE-2019-1133**: A clickjacking vulnerability was discovered in the Microsoft Office suite, allowing attackers to trick users into granting administrative privileges.
- **CVE-2020-13777**: A clickjacking vulnerability was found in the Cisco Webex Meetings client, enabling attackers to execute arbitrary commands on the victim's machine.

### Prevention and Detection

To prevent clickjacking attacks, websites should implement security measures such as the X-Frame-Options header, Content Security Policy (CSP), and secure coding practices.

#### X-Frame-Options Header

The X-Frame-Options header is used to indicate whether or not a browser should be allowed to render a page in a frame or iframe. There are three possible values:

- `DENY`: The page cannot be displayed in a frame.
- `SAMEORIGIN`: The page can only be displayed in a frame on the same origin as the page itself.
- `ALLOW-FROM uri`: The page can only be displayed in a frame on the specified origin.

```http
HTTP/1.1 200 OK
Content-Type: text/html
X-Frame-Options: SAMEORIGIN
```

#### Content Security Policy (CSP)

Content Security Policy (CSP) is a security feature that helps to detect and mitigate certain types of attacks, including clickjacking. CSP allows you to specify which sources of content are permitted to load in your web pages.

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: frame-ancestors 'self'
```

### Secure Coding Practices

Secure coding practices involve ensuring that user interactions are properly validated and authenticated. For example, when updating an email address, the system should require the user to re-enter their password or provide a one-time verification code.

#### Vulnerable Code Example

```python
# Vulnerable code example
@app.route('/update_email', methods=['POST'])
def update_email():
    new_email = request.form['new_email']
    user_id = session['user_id']
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return redirect('/')
```

#### Secure Code Example

```python
# Secure code example
@app.route('/update_email', methods=['POST'])
def update_email():
    new_email = request.form['new_email']
    user_id = session['user_id']
    password = request.form['password']
    
    # Verify the user's password
    stored_password_hash = db.execute("SELECT password FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    if not check_password_hash(stored_password_hash, password):
        return "Invalid password", 401
    
    db.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    return redirect('/')
```

### Lab Exercises

To practice and understand clickjacking, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security vulnerabilities, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Clickjacking is a serious security threat that can lead to unauthorized actions being performed on behalf of the user. By understanding how clickjacking works and implementing proper security measures, you can protect your web applications from such attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/06-Lab 5 Multistep clickjacking/01-Introduction to Clickjacking|Introduction to Clickjacking]] | [[Web Security (PortSwigger)/05-Clickjacking/06-Lab 5 Multistep clickjacking/00-Overview|Overview]] | [[03-Setting Up a Clickjacking Exploit|Setting Up a Clickjacking Exploit]]
