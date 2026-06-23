---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. Unlike many other types of vulnerabilities that target the server directly, XSS exploits the trust relationship between a user and a web application. In essence, an attacker injects malicious scripts into web pages viewed by other users. These scripts can perform actions such as stealing sensitive data, performing unauthorized actions on behalf of the victim, or even redirecting the user to malicious sites.

### What is Cross-Site Scripting?

Cross-Site Scripting occurs when an application includes untrusted data in a web page without proper validation or escaping. This allows an attacker to inject malicious scripts into the page, which are then executed by the victim's browser. There are three main types of XSS:

1. **Reflected XSS**: The injected script comes from the current HTTP request and is echoed back immediately.
2. **Stored XSS**: The injected script is permanently stored on the server and served to victims over time.
3. **DOM-based XSS**: The vulnerability exists within the client-side JavaScript code rather than the server-side code.

### Why Does XSS Matter?

XSS attacks can lead to severe consequences, including:

- **Data Theft**: An attacker can steal cookies, session tokens, and other sensitive information.
- **Account Takeover**: By stealing session tokens, an attacker can impersonate the victim and perform actions on their behalf.
- **Phishing Attacks**: Malicious scripts can redirect users to phishing sites or display fake login forms.
- **Defacement**: An attacker can alter the appearance of a website to spread misinformation or propaganda.

### How Does XSS Work?

To understand XSS, let's break down the process step-by-step:

1. **Injection Point**: The attacker identifies a place in the application where user input is accepted and reflected back to the user.
2. **Malicious Input**: The attacker crafts a malicious script and injects it into the application.
3. **Reflection**: The application reflects the malicious script back to the user's browser.
4. **Execution**: The user's browser executes the malicious script, leading to the desired outcome for the attacker.

### Example: Language Preference Vulnerability

Let's consider a banking application that allows users to choose their preferred language. The application uses a URL parameter to set the language preference. For instance:

```
https://bank.example.com/setLanguage?lang=EN
```

Here, `lang` is the parameter that accepts the language code. However, if the application does not properly validate or escape the input, an attacker can inject malicious scripts.

#### Vulnerable Code Example

```python
def set_language(request):
    lang = request.GET.get('lang', 'EN')
    response = render(request, 'index.html', {'lang': lang})
    return response
```

In this example, the `lang` parameter is directly inserted into the HTML response without any validation or escaping.

#### Exploitation

An attacker can craft a URL like:

```
https://bank.example.com/setLanguage?lang=<script>alert('XSS')</script>
```

When a user visits this URL, the `<script>` tag is reflected back in the HTML response and executed by the browser, triggering an alert box.

### Real-World Examples

Recent real-world examples of XSS vulnerabilities include:

- **CVE-2021-21972**: A stored XSS vulnerability in WordPress plugins allowed attackers to inject malicious scripts into comments.
- **CVE-2022-22965**: A reflected XSS vulnerability in Microsoft Exchange Server allowed attackers to execute arbitrary scripts in the context of the victim's browser.

### Detection and Prevention

#### How to Detect XSS

To detect XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.

Additionally, manual testing techniques such as:

- **Fuzzing**: Sending various inputs to the application to see if they are reflected back.
- **Code Review**: Checking the application code for proper input validation and output encoding.

#### How to Prevent XSS

To prevent XSS, follow these best practices:

1. **Input Validation**: Ensure that user inputs are validated against a strict set of rules.
2. **Output Encoding**: Encode user inputs before inserting them into HTML responses.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.

##### Secure Coding Example

```python
from django.utils.safestring import mark_safe

def set_language(request):
    lang = request.GET.get('lang', 'EN')
    lang = mark_safe(lang)  # Ensures the input is safe before rendering
    response = render(request, 'index.html', {'lang': lang})
    return response
```

In this example, `mark_safe` ensures that the `lang` parameter is properly encoded before being inserted into the HTML response.

### Content Security Policy (CSP)

Content Security Policy (CSP) is a security mechanism that helps prevent XSS attacks by specifying which sources of content are allowed to be executed in a web page.

#### Example CSP Header

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
```

This CSP header specifies that scripts can only be loaded from the same origin (`'self'`) or from `https://trustedscripts.example.com`.

### Hands-On Labs

For hands-on practice with XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive challenges to learn and test XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

### Conclusion

Cross-Site Scripting is a critical vulnerability that can have severe consequences for both users and organizations. By understanding the mechanics of XSS, identifying injection points, and implementing robust prevention measures, developers can significantly reduce the risk of such attacks. Always ensure that user inputs are properly validated and encoded, and consider using Content Security Policy to further enhance security.

---

This detailed explanation covers the core concepts of Cross-Site Scripting, provides real-world examples, and offers practical guidance on detection and prevention. The next section will delve deeper into specific types of XSS and advanced mitigation techniques.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[02-What is Cross-Site Scripting (XSS)|What is Cross-Site Scripting (XSS)]]
