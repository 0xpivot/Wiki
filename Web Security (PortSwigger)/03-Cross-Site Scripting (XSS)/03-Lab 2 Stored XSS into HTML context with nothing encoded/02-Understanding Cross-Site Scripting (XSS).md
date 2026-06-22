---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. This can lead to various attacks such as stealing cookies, session tokens, and other sensitive information. XSS vulnerabilities occur when a web application takes untrusted data and includes it in the output without proper validation or escaping.

### What is XSS?

XSS vulnerabilities can be categorized into three main types:

1. **Stored XSS**: The malicious script is permanently stored on the target servers, such as in a database, comment field, visitor log, etc. Each time a victim visits the page containing the malicious script, their browser will execute the script.
   
2. **Reflected XSS**: The malicious script comes from the current HTTP request. Reflected XSS vulnerabilities are exploited by tricking a user into clicking a malicious link, visiting a malicious site, or otherwise sending a crafted request to the server.
   
3. **DOM-based XSS**: The vulnerability arises from client-side code that, when manipulated, can alter the DOM and execute arbitrary JavaScript.

In this chapter, we will focus on **Stored XSS** into an HTML context where nothing is encoded.

### Why Does XSS Matter?

XSS vulnerabilities can have severe consequences:

- **Data Theft**: Attackers can steal sensitive data like session cookies, authentication tokens, and personal information.
- **Account Takeover**: By stealing session cookies, attackers can impersonate legitimate users.
- **Defacement**: Attackers can modify the appearance of a website to display inappropriate content.
- **Phishing**: Attackers can redirect users to fake login pages to steal credentials.

### How Does XSS Work?

To understand how XSS works, let's consider a simple example. Suppose a web application has a feature where users can post comments on a blog. The application stores these comments in a database and displays them on the blog page.

#### Example Scenario

Consider the following HTML structure for displaying comments:

```html
<div id="comments">
  <!-- Comments are inserted here -->
</div>
```

Suppose a user posts the following comment:

```html
<script>alert('XSS');</script>
```

If the web application does not properly sanitize or escape this input, the comment will be displayed as:

```html
<div id="comments">
  <script>alert('XSS');</script>
</div>
```

When another user views the blog page, their browser will execute the `<script>` tag, triggering the `alert` function and displaying a popup with the message "XSS".

### Real-World Examples

Recent real-world examples of XSS vulnerabilities include:

- **CVE-2021-21972**: A stored XSS vulnerability was found in the WordPress plugin "WP GDPR Compliance". An attacker could inject malicious scripts into the plugin settings, which would then be executed by other users.
  
- **CVE-2022-22965**: A reflected XSS vulnerability was discovered in the popular web framework Django. An attacker could craft a URL with malicious scripts, which would be executed when the URL is visited.

### Complete Example

Let's walk through a complete example of a stored XSS vulnerability in a web application.

#### Vulnerable Code

Consider the following Python Flask application that allows users to post comments:

```python
from flask import Flask, request, render_template_string

app = Flask(__name__)

comments = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        comment = request.form['comment']
        comments.append(comment)
    
    return render_template_string('''
        <h1>Comments</h1>
        <form method="post">
            <textarea name="comment"></textarea>
            <input type="submit" value="Post Comment">
        </form>
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
    ''', comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
```

#### Exploitation

An attacker can post the following comment:

```html
<script>alert('XSS');</script>
```

The application will store this comment and display it on the page:

```html
<ul>
    <li><script>alert('XSS');</script></li>
</ul>
```

When another user views the page, their browser will execute the `<script>` tag, triggering the `alert` function.

### How to Prevent / Defend Against XSS

Preventing XSS vulnerabilities requires a combination of input validation, output encoding, and secure coding practices.

#### Input Validation

Validate all user inputs to ensure they meet the expected format. For example, if a comment should only contain alphanumeric characters and spaces, validate the input accordingly.

#### Output Encoding

Encode all user inputs before rendering them in the HTML context. This ensures that any potentially harmful scripts are treated as plain text rather than executable code.

##### Example of Secure Code

Here is the corrected version of the Flask application using output encoding:

```python
from flask import Flask, request, render_template_string
import html

app = Flask(__name__)

comments = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        comment = request.form['comment']
        comments.append(html.escape(comment))
    
    return render_template_string('''
        <h1>Comments</h1>
        <form method="post">
            <textarea name="comment"></textarea>
            <input type="submit" value="Post Comment">
        </form>
        <ul>
            {% for comment in comments %}
                <li>{{ comment }}</li>
            {% endfor %}
        </ul>
    ''', comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
```

In this corrected version, the `html.escape` function is used to encode the user input before storing it in the `comments` list. This ensures that any potentially harmful scripts are treated as plain text.

#### Detection

Detecting XSS vulnerabilities can be done through automated tools and manual testing.

- **Automated Tools**: Use tools like Burp Suite, OWASP ZAP, and Acunetix to scan for XSS vulnerabilities.
  
- **Manual Testing**: Test the application by injecting various payloads and observing the behavior. Common payloads include `<script>alert('XSS');</script>` and `<img src=x onerror=alert('XSS')>`.

#### Hardening

Hardening the application against XSS vulnerabilities involves several steps:

- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts. For example:

  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self'
  ```

- **HTTP Headers**: Set the `X-XSS-Protection` header to enable browser-based XSS protection:

  ```http
  X-XSS-Protection: 1; mode=block
  ```

- **Secure Coding Practices**: Follow secure coding practices such as input validation, output encoding, and least privilege principles.

### Practice Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and practice XSS exploitation.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application to teach web application security lessons.

These labs provide a safe environment to practice identifying and exploiting XSS vulnerabilities.

### Conclusion

Understanding and preventing XSS vulnerabilities is crucial for securing web applications. By validating inputs, encoding outputs, and following secure coding practices, developers can significantly reduce the risk of XSS attacks. Regularly testing and hardening applications can help ensure they remain secure against these types of vulnerabilities.

By mastering the concepts and techniques covered in this chapter, you will be well-equipped to identify, exploit, and defend against XSS vulnerabilities in real-world web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/03-Practice Questions & Answers|Practice Questions & Answers]]
