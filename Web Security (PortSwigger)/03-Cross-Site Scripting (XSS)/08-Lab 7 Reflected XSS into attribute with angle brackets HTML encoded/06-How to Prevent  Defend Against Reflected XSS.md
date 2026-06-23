---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against Reflected XSS

### Detection

Detecting Reflected XSS vulnerabilities involves both automated and manual testing methods:

1. **Automated Tools**: Use tools like Burp Suite, OWASP ZAP, and Acunetix to scan for XSS vulnerabilities.
2. **Manual Testing**: Perform manual tests by injecting various payloads into input fields and observing the server's response.

### Prevention

Preventing Reflected XSS involves several best practices:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and lengths.
2. **Output Encoding**: Encode all user inputs before reflecting them back to the user. Use libraries like OWASP Java Encoder or Microsoft AntiXSS Library.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources from which scripts can be loaded.

### Secure Coding Practices

#### Vulnerable Code Example

```java
public class SearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String query = request.getParameter("q");
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        out.println("<h1>Search Results for: " + query + "</h1>");
        out.println("<input type='text' value='" + query + "'>");
    }
}
```

#### Secure Code Example

```java
import org.owasp.encoder.Encode;

public class SearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String query = request.getParameter("q");
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        out.println("<h1>Search Results for: " + Encode.forHtml(query) + "</h1>");
        out.println("<input type='text' value='" + Encode.forHtmlAttribute(query) + "'>");
    }
}
```

### Configuration Hardening

#### Content Security Policy (CSP)

Implement CSP to further mitigate XSS risks:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
```

### Additional Defenses

1. **HTTPOnly Cookies**: Set the `HttpOnly` flag on cookies to prevent access via JavaScript.
2. **Subresource Integrity (SRI)**: Use SRI to ensure that external scripts are not tampered with.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/05-Hands-On Practice|Hands-On Practice]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[07-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]]
