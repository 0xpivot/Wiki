---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Clickjacking: A Comprehensive Guide

### Introduction to Clickjacking

Clickjacking, also known as UI redress attack or User Interface Redress Attack (UIRA), is a malicious technique used by attackers to trick users into clicking on hidden buttons or links. This attack exploits the way browsers handle overlapping elements on a webpage. By overlaying transparent or opaque elements over legitimate buttons, attackers can manipulate users into performing unintended actions, such as deleting an account or changing settings.

### Understanding the Basics of Clickjacking

#### What is Clickjacking?

Clickjacking is a type of phishing attack that relies on the use of HTML frames and CSS properties to hide or obscure the true nature of a link or button. The attacker creates a seemingly benign webpage that contains an invisible iframe, which overlays the target website. When a user interacts with the decoy page, they inadvertently interact with the hidden iframe, triggering the desired action on the target site.

#### Why Does Clickjacking Matter?

Clickjacking is particularly dangerous because it can bypass many traditional security measures, such as CSRF tokens and CAPTCHAs. By tricking the user into performing actions on their behalf, attackers can gain unauthorized access to sensitive information or perform malicious actions.

### How Clickjacking Works

To understand how clickjacking works, let's break down the process step-by-step:

1. **Create a Decoy Website**: The attacker creates a webpage that appears legitimate but contains hidden elements.
2. **Embed an Invisible iFrame**: The attacker embeds an iFrame that points to the target website. The iFrame is made invisible using CSS properties.
3. **Overlay Transparent Elements**: The attacker uses CSS to overlay transparent or semi-transparent elements over the iFrame, making it appear as though the user is interacting with the decoy website.
4. **Trigger Actions**: When the user clicks on the decoy elements, they are actually clicking on the hidden iFrame, triggering actions on the target website.

### Detailed Example: Basic Clickjacking with CSRF Token Protection

Let's walk through a detailed example of how a basic clickjacking attack might work, including the necessary HTML and CSS code.

#### Step 1: Create the Decoy Website

The first step is to create a decoy website that will serve as the front-end for the attack. This website will contain the hidden iFrame and the overlay elements.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decoy Website</title>
    <style>
        .hidden-iframe {
            position: relative;
            width: 1000px;
            height: 1000px;
            opacity: 0.5; /* Initially set to 0.5 for visibility */
            z-index: 2; /* Stacking order */
        }
        .overlay-button {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 10px 20px;
            background-color: #ff0000;
            color: white;
            font-size: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <iframe src="https://target-website.com" class="hidden-iframe"></iframe>
    <button class="overlay-button">Click Me</button>
</body>
</html>
```

#### Step 2: Explain the CSS Properties

- **Position**: The `position` property is set to `relative`, which allows the iFrame to be positioned relative to its normal position.
- **Width and Height**: The `width` and `height` properties are set to `1000px` to ensure the iFrame covers a large area of the screen.
- **Opacity**: The `opacity` property is initially set to `0.5` to allow the user to see the underlying iFrame during testing. In a real attack, this would be set to `0` to make the iFrame completely invisible.
- **Z-Index**: The `z-index` property is set to `2` to ensure the iFrame is stacked above other elements on the page.

#### Step 3: Overlay Transparent Elements

The `overlay-button` is positioned absolutely over the iFrame using the `top`, `left`, and `transform` properties. This ensures that when the user clicks on the button, they are actually clicking on the iFrame underneath.

### Real-World Examples of Clickjacking Attacks

Clickjacking attacks have been used in various real-world scenarios. Here are a few notable examples:

- **CVE-2010-3544**: This vulnerability affected Adobe Flash Player and allowed attackers to execute arbitrary code by tricking users into clicking on a hidden Flash object.
- **CVE-2012-1525**: This vulnerability affected Microsoft Internet Explorer and allowed attackers to bypass the Same Origin Policy by using a clickjacking attack.

### How to Prevent / Defend Against Clickjacking

#### Detection

To detect clickjacking attacks, organizations should implement monitoring and logging mechanisms to track unusual activity on their websites. This includes monitoring for unexpected changes in user behavior and detecting the presence of hidden iFrames.

#### Prevention

1. **X-Frame-Options Header**: Set the `X-Frame-Options` header to `DENY` or `SAMEORIGIN` to prevent your website from being embedded in an iFrame.
   
   ```http
   HTTP/1.1 200 OK
   Content-Type: text/html
   X-Frame-Options: DENY
   ```

2. **Content Security Policy (CSP)**: Implement a Content Security Policy that restricts the sources from which iFrames can be loaded.

   ```http
   HTTP/1.1 200 OK
   Content-Type: text/html
   Content-Security-Policy: frame-ancestors 'none'
   ```

3. **JavaScript Mitigation**: Use JavaScript to detect and prevent clickjacking attacks by checking the window's parent and top properties.

   ```javascript
   if (window.top !== window.self) {
       window.top.location = window.self.location;
   }
   ```

#### Secure Coding Practices

1. **Validate User Input**: Ensure that all user input is validated and sanitized to prevent malicious data from being injected into the website.
2. **Use HTTPS**: Always use HTTPS to encrypt data transmitted between the client and server, preventing man-in-the-middle attacks.
3. **Implement CSRF Tokens**: Use CSRF tokens to protect against cross-site request forgery attacks, which can be combined with clickjacking to perform unauthorized actions.

### Complete Example: Vulnerable vs. Secure Code

#### Vulnerable Code

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vulnerable Website</title>
</head>
<body>
    <form action="/delete-account" method="POST">
        <input type="submit" value="Delete Account">
    </form>
</body>
</html>
```

#### Secure Code

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Website</title>
    <script>
        if (window.top !== window.self) {
            window.top.location = window.self.location;
        }
    </script>
</head>
<body>
    <form action="/delete-account" method="POST">
        <input type="hidden" name="csrf_token" value="unique_token_here">
        <input type="submit" value="Delete Account">
    </form>
</body>
</html>
```

### Conclusion

Clickjacking is a sophisticated attack that can bypass many traditional security measures. By understanding the mechanics of clickjacking and implementing robust defense mechanisms, organizations can protect themselves from these types of attacks. Regularly updating security policies and staying informed about the latest vulnerabilities and mitigation techniques is crucial in maintaining a secure web environment.

### Hands-On Labs

For hands-on practice with clickjacking, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs and challenges to learn about various web security vulnerabilities, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application that simulates real-world vulnerabilities, including clickjacking.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that provides a platform to learn and test security concepts.

By engaging with these resources, you can gain practical experience in identifying and defending against clickjacking attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/02-Lab 1 Basic clickjacking with CSRF token protection/00-Overview|Overview]] | [[02-Clickjacking Overview|Clickjacking Overview]]
