---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## How to Prevent / Defend Against XSS

### Input Validation and Output Encoding

To prevent XSS attacks, it is crucial to validate user input and encode output properly. This ensures that malicious scripts cannot be injected into web pages.

#### Secure Coding Practices

1. **Input Validation**: Validate all user inputs to ensure they conform to expected formats. Use regular expressions or predefined patterns to filter out invalid characters.
   
2. **Output Encoding**: Encode all user inputs before rendering them in the browser. Use libraries like `OWASP Java Encoder` or `Microsoft Anti-XSS Library` to automatically encode output.

#### Example of Secure Code

```java
import org.owasp.encoder.Encode;

public class SearchServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String query = request.getParameter("query");
        String encodedQuery = Encode.forHtml(query);
        
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        out.println("<!DOCTYPE html>");
        out.println("<html>");
        out.println("<head><title>Search Results</title></head>");
        out.println("<body>");
        out.println("<script>");
        out.println("var query = \"" + encodedQuery + "\";");
        out.println("</script>");
        out.println("</body>");
        out.println("</html>");
    }
}
```

### Configuration Hardening

Ensure that your web server and application frameworks are configured securely to mitigate XSS risks.

#### Example of Secure Configuration

1. **Content Security Policy (CSP)**: Implement CSP to restrict the sources from which scripts can be loaded. This helps prevent the execution of malicious scripts.

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-source.com;
```

2. **HTTP Headers**: Set appropriate HTTP headers to enhance security.

```http
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### Detection and Monitoring

Regularly monitor your web application for signs of XSS attacks. Use tools like Burp Suite, ZAP, or automated scanners to identify potential vulnerabilities.

#### Example of Detection

Use Burp Suite to intercept and analyze requests and responses. Look for patterns where user input is reflected without proper encoding.

### Hands-On Labs

To practice and reinforce your understanding of XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various types of XSS vulnerabilities.
- **OWASP Juice Shop**: An intentionally vulnerable web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application with numerous security vulnerabilities for educational purposes.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/03-Exploiting the Vulnerability|Exploiting the Vulnerability]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/05-How to Prevent  Defend|How to Prevent  Defend]]
