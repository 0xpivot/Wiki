---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Detection and Prevention

Detecting and preventing clickjacking attacks requires a combination of technical measures and best practices. By understanding the mechanisms behind clickjacking, organizations can implement effective countermeasures to protect their web applications.

### Detection Techniques

1. **Automated Scanning Tools**: Utilize automated scanning tools such as Burp Suite, OWASP ZAP, and Acunetix to identify potential clickjacking vulnerabilities. These tools can help detect overlays and hidden elements that may be used in clickjacking attacks.

2. **Manual Testing**: Conduct manual testing to verify the presence of clickjacking vulnerabilities. This involves inspecting the HTML and CSS of web pages to identify any suspicious overlays or hidden elements.

3. **User Education**: Educate users about the risks of clickjacking and encourage them to be cautious when interacting with web applications. Users should be wary of unexpected pop-ups or overlays and should verify the authenticity of links and buttons before clicking.

### Prevention Techniques

1. **X-Frame-Options Header**: Implement the `X-Frame-Options` HTTP header to prevent web pages from being loaded within frames. This header can be set to `DENY` or `SAMEORIGIN` to restrict framing to the same origin.

    ```http
    HTTP/1.1 200 OK
    Content-Type: text/html
    X-Frame-Options: SAMEORIGIN
    ```

2. **Content Security Policy (CSP)**: Use Content Security Policy (CSP) to define a whitelist of trusted sources for resources such as scripts, stylesheets, and images. CSP can help prevent clickjacking by restricting the loading of external resources.

    ```http
    HTTP/1.1 200 OK
    Content-Type: text/html
    Content-Security-Policy: frame-ancestors 'self'
    ```

3. **JavaScript Mitigation**: Implement JavaScript-based mitigation techniques to detect and prevent clickjacking attacks. For example, you can use JavaScript to check the position of elements and ensure they are not being overlaid by malicious content.

    ```javascript
    // Check if the element is being overlaid
    function checkOverlay(element) {
      const rect = element.getBoundingClientRect();
      const overlayElements = document.querySelectorAll('*[style*="position"]');
      for (const overlay of overlayElements) {
        const overlayRect = overlay.getBoundingClientRect();
        if (rect.left <= overlayRect.right && rect.right >= overlayRect.left &&
            rect.top <= overlayRect.bottom && rect.bottom >= overlayRect.top) {
          console.log('Potential clickjacking overlay detected');
          return true;
        }
      }
      return false;
    }

    const button = document.getElementById('realButton');
    if (checkOverlay(button)) {
      // Handle potential clickjacking
    }
    ```

4. **Secure Coding Practices**: Follow secure coding practices to minimize the risk of clickjacking vulnerabilities. This includes validating user input, sanitizing output, and ensuring that sensitive actions require explicit confirmation.

### Secure Code Fix

Here is an example of how to implement the `X-Frame-Options` header and Content Security Policy (CSP) to prevent clickjacking:

#### Vulnerable Code

```python
# Flask app without X-Frame-Options and CSP
from flask import Flask, make_response

app = Flask(__name__)

@app.route('/')
def index():
    response = make_response('<h1>Welcome to the website</h1>')
    return response

if __name__ == '__main__':
    app.run()
```

#### Fixed Code

```python
# Flask app with X-Frame-Options and CSP
from flask import Flask, make_response

app = Flask(__name__)

@app.route('/')
def index():
    response = make_response('<h1>Welcome to the website</h1>')
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    return response

if __name__ == '__main__':
    app.run()
```

By implementing these headers, the web application becomes more resistant to clickjacking attacks.

### Configuration Hardening

Configuration hardening involves securing the environment in which the web application runs. This includes securing the server, network, and other infrastructure components.

1. **Server Configuration**: Ensure that the server is configured securely. Disable unnecessary services, update software regularly, and apply security patches promptly.

2. **Network Configuration**: Configure the network to restrict access to the web application. Use firewalls, intrusion detection systems (IDS), and intrusion prevention systems (IPS) to monitor and control traffic.

3. **Application Configuration**: Configure the web application to enforce security policies. This includes setting appropriate permissions, enabling logging and monitoring, and configuring error handling to prevent information leakage.

### Real-World Example: CVE-2010-0188

In 2010, a clickjacking vulnerability was discovered in Adobe Reader and Acrobat. The vulnerability allowed attackers to trick users into installing malicious software by overlaying a download button with a seemingly benign link.

#### Vulnerable Code

```html
<!-- Attacker's HTML -->
<div style="position:absolute; left:0; top:0; width:100%; height:100%; z-index:1000; opacity:0;">
  <a href="malicious-software.exe">Download</a>
</div>

<!-- Victim's HTML -->
<a href="legitimate-software.exe">Click Me</a>
```

#### Fixed Code

To prevent this vulnerability, Adobe implemented the `X-Frame-Options` header and Content Security Policy (CSP).

```http
HTTP/1.1 200 OK
Content-Type: text/html
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'self'
```

By implementing these headers, Adobe ensured that the web page could not be framed by malicious content, thus preventing clickjacking attacks.

### Real-World Example: CVE-2010-3337

In 2010, a clickjacking vulnerability was discovered in Microsoft Office. The vulnerability allowed attackers to trick users into opening malicious files by overlaying a file open dialog with a seemingly benign link.

#### Vulnerable Code

```html
<!-- Attacker's HTML -->
<div style="position:absolute; left:0; top:0; width:100%; height:100%; z-index:1000; opacity:0;">
  <a href="malicious-file.doc">Open File</a>
</div>

<!-- Victim's HTML -->
<a href="legitimate-file.doc">Click Me</a>
```

#### Fixed Code

To prevent this vulnerability, Microsoft implemented the `X-Frame-Options` header and Content Security Policy (CSP).

```http
HTTP/1.1 200 OK
Content-Type: text/html
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'self'
```

By implementing these headers, Microsoft ensured that the web page could not be framed by malicious content, thus preventing clickjacking attacks.

---
<!-- nav -->
[[08-Content-Security-Policy (CSP) Header|Content-Security-Policy (CSP) Header]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[10-Finding Clickjacking Vulnerabilities|Finding Clickjacking Vulnerabilities]]
