---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## How to Prevent / Defend Against Password Reset Poisoning

### Detection

To detect such attacks, monitor HTTP requests for unusual `Host` header values. Tools like IDS/IPS systems can be configured to alert on suspicious activity.

### Prevention

1. **Validate the `Host` Header**:
   - Ensure the `Host` header matches a list of trusted hosts.
   - Reject requests with invalid or unexpected `Host` headers.

2. **Sanitize User Input**:
   - Properly escape and validate user input to prevent HTML injection.

3. **Secure Coding Practices**:
   - Use secure coding practices to prevent vulnerabilities in the first place.

### Secure Code Example

Here’s an example of secure code that validates the `Host` header and sanitizes user input:

```java
public void handleRequest(HttpServletRequest request) {
    String host = request.getHeader("Host");
    if (!isValidHost(host)) {
        throw new IllegalArgumentException("Invalid Host header");
    }

    String email = request.getParameter("email");
    if (!isSafeInput(email)) {
        throw new IllegalArgumentException("Unsafe email input");
    }

    // Process the request using the sanitized inputs
}

private boolean isValidHost(String host) {
    List<String> trustedHosts = Arrays.asList("trusted-host1.com", "trusted-host2.com");
    return trustedHosts.contains(host);
}

private boolean isSafeInput(String input) {
    // Implement input validation logic
    return true;
}
```

### Configuration Hardening

1. **Web Server Configuration**:
   - Configure web servers to reject requests with invalid `Host` headers.
   - Use tools like mod_security to enforce strict validation rules.

2. **Application Configuration**:
   - Configure applications to validate and sanitize user input.
   - Use frameworks and libraries that provide built-in security features.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a vulnerability in Microsoft Exchange Server that allows attackers to manipulate the `Host` header to gain unauthorized access. This vulnerability was exploited by attackers to compromise numerous Exchange servers.

#### Vulnerable Configuration

Here’s an example of a vulnerable configuration in an Exchange server:

```xml
<webConfig>
    <system.webServer>
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="30000000" />
            </requestFiltering>
        </security>
    </system.webServer>
</webConfig>
```

#### Secure Configuration

To prevent such vulnerabilities, configure the server to validate the `Host` header and limit the size of requests:

```xml
<webConfig>
    <system.webServer>
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="30000000" />
            </requestFiltering>
        </安全>
    </system.webServer>
    <system.web>
        <httpRuntime requestValidationMode="2.0" />
    </system.web>
</webConfig>
```

### Hands-On Practice

To practice these concepts, you can use the following labs:

- **PortSwigger Web Security Academy**: Lab 7 "Password Reset Poisoning via Dangling Markup"
- **OWASP Juice Shop**: Various labs related to HTTP header manipulation
- **DVWA**: Labs related to XSS and other web vulnerabilities

By thoroughly understanding and practicing these concepts, you can effectively defend against HTTP Host Header attacks and ensure the security of web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/08-Lab 7 Password reset poisoning via dangling markup/01-Introduction to HTTP Host Header Attacks|Introduction to HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/08-Lab 7 Password reset poisoning via dangling markup/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/08-Lab 7 Password reset poisoning via dangling markup/03-Understanding HTTP Host Header Attacks|Understanding HTTP Host Header Attacks]]
