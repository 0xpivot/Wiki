---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Black Box Testing Perspective

Black box testing involves testing the application without access to its internal workings. The goal is to identify vulnerabilities such as clickjacking by simulating real-world attacks.

### Steps to Identify Clickjacking Vulnerabilities

1. **Identify Actionable Items**: Look for pages with actionable items, such as login forms or buttons that trigger sensitive actions.
2. **Create Proof-of-Concept**: Develop a proof-of-concept that demonstrates how an attacker could trick a user into performing an unintended action.

#### Example Proof-of-Concept

Here’s an example of a proof-of-concept for a clickjacking attack:

```html
<!-- Malicious Website -->
<!DOCTYPE html>
<html>
<head>
    <title>Malicious Website</title>
</head>
<body>
    <iframe src="https://example.com/login" style="position:absolute; left:-9999px; top:-9999px;"></iframe>
    <button onclick="document.querySelector('iframe').contentWindow.location.reload();">Claim Your Prize!</button>
</body>
</html>
```

In this example, the malicious website uses an invisible iframe to load the login page of a target site. When the user clicks on the "Claim Your Prize!" button, it reloads the iframe, triggering the login action.

### How to Prevent / Defend

To defend against clickjacking during black box testing:

1. **Implement Headers**: Ensure the `X-Frame-Options` and `Content-Security-Policy` headers are correctly configured.
2. **Regular Audits**: Conduct regular security audits to identify and mitigate vulnerabilities.
3. **Educate Users**: Educate users about the risks of clicking on suspicious links or buttons.

---
<!-- nav -->
[[03-What is Clickjacking|What is Clickjacking]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[05-Clickjacking An In-Depth Analysis|Clickjacking An In-Depth Analysis]]
