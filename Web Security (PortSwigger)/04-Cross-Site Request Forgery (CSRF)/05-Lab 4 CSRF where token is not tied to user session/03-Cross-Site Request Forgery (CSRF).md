---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Cross-Site Request Forgery (CSRF)

### Introduction to CSRF

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. This can lead to unauthorized transactions, such as changing email addresses, transferring funds, or posting content. The key aspect of a CSRF attack is that it leverages the trust that a web application places in the user's browser session.

### Scenario: Change Email Functionality

In this scenario, we will focus on a web application that allows users to change their email addresses. The attacker's goal is to trick the victim into clicking a link that changes the victim's email address to one controlled by the attacker. Once the attacker controls the email address, they can reset the victim's password and fully compromise the account.

#### Why is Changing the Email Address Relevant?

Changing the email address is particularly dangerous because many websites use email addresses for password resets and other critical actions. By controlling the email address, an attacker can:

- Reset the victim's password.
- Gain access to sensitive information sent via email.
- Potentially lock out the legitimate user from their account.

### Prerequisites for a Successful CSRF Attack

For a CSRF attack to be successful, several conditions must be met:

1. **Action Relevance**: The action being performed must be significant enough to cause harm. In this case, changing the email address is a relevant action.
2. **Cookie-Based Session Handling**: The web application must rely solely on cookies for session management.
3. **Predictable Request Parameters**: The attacker must know all the parameters required to make the request successful.

#### Action Relevance

The action of changing the email address is relevant because it can be used to gain further access to the victim's account. If an attacker can change the email address to one they control, they can use it to reset the password and take full control of the account.

#### Cookie-Based Session Handling

Cookie-based session handling means that the web application uses cookies to maintain the user's session. Typically, this involves a session cookie that contains a unique identifier for the user's session. In this scenario, the session management is handled using a single cookie named `session`.

```plaintext
Set-Cookie: session=unique_session_id; Path=/; HttpOnly
```

The `HttpOnly` flag ensures that the cookie cannot be accessed via JavaScript, which helps mitigate some types of attacks but does not protect against CSRF.

#### Predictable Request Parameters

For a CSRF attack to work, the attacker must know all the parameters required to make the request successful. In this case, the attacker knows the `email` parameter, which is the new email address they want to set. However, there is a second request parameter that is unpredictable.

### Real-World Example: CVE-2021-3116

A real-world example of a CSRF vulnerability is CVE-2021-3116, which affected the WordPress REST API. This vulnerability allowed attackers to perform unauthorized actions, such as deleting posts, by tricking authenticated users into clicking malicious links.

#### How the Vulnerability Worked

WordPress uses cookies for session management, and the REST API endpoints were vulnerable to CSRF attacks because they did not properly validate the origin of the requests. An attacker could craft a URL that, when clicked by an authenticated user, would perform actions like deleting posts.

#### Impact

The impact of this vulnerability was significant because it allowed attackers to manipulate content on WordPress sites, potentially leading to data loss or unauthorized modifications.

### CSRF Attack Mechanics

To understand how a CSRF attack works, let's break down the steps involved:

1. **Identify the Target Action**: Determine the action that the attacker wants to perform, such as changing the email address.
2. **Craft the Malicious Request**: Create a request that includes all the necessary parameters to perform the target action.
3. **Trick the Victim**: Get the victim to click on a link or submit a form that triggers the malicious request.

#### Identifying the Target Action

In this scenario, the target action is changing the email address. The attacker needs to know the endpoint and the parameters required to perform this action.

#### Crafting the Malicious Request

The attacker crafts a request that includes the `email` parameter and any other predictable parameters. For example:

```http
POST /change-email HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded

email=new_email@example.com&csrf_token=known_value
```

Note that the `csrf_token` parameter is known to the attacker, making it predictable.

#### Tricking the Victim

The attacker tricks the victim into clicking a link or submitting a form that triggers the malicious request. This can be done through various methods, such as:

- Embedding the link in an email or social media post.
- Using a malicious website that automatically submits the form when visited.

### Detection and Prevention

#### How to Detect CSRF Attacks

Detecting CSRF attacks can be challenging because they often do not leave obvious traces. However, there are several indicators that can help identify potential CSRF activity:

- **Unexpected Actions**: Users reporting unexpected changes to their accounts, such as email address changes or password resets.
- **Anomalous Requests**: Monitoring logs for unusual patterns of requests, especially those that involve sensitive actions.
- **User Behavior Analysis**: Analyzing user behavior to detect deviations from normal patterns, such as frequent changes to account settings.

#### How to Prevent CSRF Attacks

Preventing CSRF attacks requires implementing robust security measures. Here are some effective strategies:

1. **Use CSRF Tokens**: Generate and validate unique tokens for each request. These tokens should be unpredictable and tied to the user's session.
2. **Validate Origin Headers**: Ensure that requests originate from trusted sources by validating the `Origin` or `Referer` headers.
3. **Implement SameSite Cookies**: Use the `SameSite` attribute to restrict cookies to first-party contexts, preventing them from being sent in cross-site requests.
4. **Educate Users**: Inform users about the risks of clicking suspicious links and encourage them to verify the authenticity of requests.

#### Secure Coding Practices

Here is an example of how to implement CSRF protection in a web application:

**Vulnerable Code**

```python
@app.route('/change-email', methods=['POST'])
def change_email():
    email = request.form['email']
    # Update the user's email address
    return "Email changed successfully"
```

**Secure Code**

```python
from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/change-email', methods=['POST'])
def change_email():
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    
    if request.form.get('csrf_token') != session['csrf_token']:
        return "Invalid CSRF token", 403
    
    email = request.form['email']
    # Update the user's email address
    return "Email changed successfully"

def generate_csrf_token():
    import secrets
    return secrets.token_hex(16)
```

### Network Topology and Request Flow

To visualize the attack flow, consider the following network topology and request sequence:

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant WebApp
    participant Server

    User->>WebApp: GET /login
    WebApp-->>User: Set-Cookie: session=unique_session_id
    User->>WebApp: POST /login
    WebApp-->>User: Set-Cookie: session=unique_session_id; Path=/; HttpOnly
    User->>WebApp: GET /
    WebApp-->>User: HTML page with CSRF link
    Attacker->>User: Click on CSRF link
    User->>WebApp: POST /change-email
    WebApp-->>Server: Update email address
    Server-->>WebApp: Confirmation
    WebApp-->>User: Email changed successfully
```

### Common Pitfalls and Mitigations

#### Common Pitfalls

- **Ignoring CSRF Protection**: Not implementing CSRF protection mechanisms can leave the application vulnerable to attacks.
- **Using Predictable Tokens**: Using tokens that can be easily guessed or predicted can undermine the effectiveness of CSRF protection.
- **Not Validating Origin Headers**: Failing to validate the origin of requests can allow attackers to bypass CSRF protections.

#### Mitigations

- **Regular Security Audits**: Conduct regular security audits to identify and fix vulnerabilities.
- **Keep Software Updated**: Ensure that all software components are up-to-date with the latest security patches.
- **Educate Developers**: Train developers on secure coding practices and the importance of implementing CSRF protections.

### Practice Labs

For hands-on practice with CSRF attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on CSRF attacks and defenses.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various security attacks, including CSRF.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including CSRF, for educational purposes.

By thoroughly understanding the mechanics of CSRF attacks and implementing robust security measures, you can significantly reduce the risk of such attacks compromising your web applications.

### Conclusion

Cross-Site Request Forgery (CSRF) is a serious threat to web applications. By understanding the mechanics of CSRF attacks, identifying relevant actions, and implementing strong security measures, you can protect your applications from these types of attacks. Regular security audits, keeping software updated, and educating developers are essential steps in maintaining a secure web environment.

---
<!-- nav -->
[[02-CSRF Tokens and Their Implementation|CSRF Tokens and Their Implementation]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/05-Lab 4 CSRF where token is not tied to user session/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/05-Lab 4 CSRF where token is not tied to user session/04-Hands-On Labs|Hands-On Labs]]
