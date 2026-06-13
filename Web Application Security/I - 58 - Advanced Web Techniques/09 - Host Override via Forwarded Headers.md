---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.09 Host Override via Forwarded Headers"
---

# Host Override via Forwarded Headers

## 1. Introduction to Host Overrides
Host Override via Forwarded Headers is a vulnerability class where an attacker manipulates HTTP headers—specifically those designed to carry information across reverse proxies—to deceive the backend application about the original request's Host, IP address, or protocol scheme.

In modern microservice and cloud architectures, requests typically pass through Load Balancers, Content Delivery Networks (CDNs), and Reverse Proxies before reaching the application server. These intermediaries often alter the original request, masking the client's original IP and the requested Host. To preserve this context for the backend, intermediaries inject "Forwarded" headers (e.g., `X-Forwarded-For`, `X-Forwarded-Host`).
If the backend application blindly trusts these headers without proper validation or configuration, attackers can inject arbitrary values, leading to a wide array of exploits including Web Cache Poisoning, Password Reset Poisoning, Authentication Bypass, and Server-Side Request Forgery (SSRF).

## 2. The Mechanics of Forwarded Headers
The HTTP `Host` header is mandatory in HTTP/1.1 and specifies the domain name the client is attempting to access. However, proxies might rewrite this header. To inform the backend of the original Host, headers like `X-Forwarded-Host` (XFH) are used.
Similarly, `X-Forwarded-Proto` (XFP) indicates the original protocol (HTTP or HTTPS), and `X-Forwarded-For` (XFF) contains the client's IP. The newer, standardized header is `Forwarded` (RFC 7239), which encapsulates all these in one.

When a framework (like Spring, Django, or Express) is configured to trust proxies, it will look for these headers and automatically overwrite the internal request variables.
If `X-Forwarded-Host: attacker.com` is present, the application behaves as if the `Host` was `attacker.com`.

## 3. ASCII Architecture Diagram
```text
[ Attacker ]
     |
     | GET /password-reset HTTP/1.1
     | Host: target.com
     | X-Forwarded-Host: attacker.com
     v
[ Reverse Proxy / WAF ]
     | (Does not strip the injected header, forwards it to backend)
     v
[ Backend Application ]
     | 
     | Application logic:
     | url = Request.Host + "/reset?token=" + user.token
     | 
     | Because it trusts X-Forwarded-Host, Request.Host resolves to "attacker.com"
     | url = "https://attacker.com/reset?token=12345abcd"
     | Sends email to victim with this malicious link.
     v
[ Victim receives email & clicks link -> Token leaked to Attacker ]
```

## 4. Vulnerability Mechanics in Detail

### 4.1 Blind Trust in Proxies
Many web frameworks have a setting to "trust proxy" (e.g., `app.set('trust proxy', true)` in Express.js). When enabled globally, the application trusts Forwarded headers from *any* IP, not just the legitimate internal load balancer. An attacker on the internet can simply inject these headers into their initial request.

### 4.2 Header Variations and Fallbacks
Applications might check a waterfall of headers to determine the host. Attackers fuzz various headers to find which one the application respects:
- `X-Forwarded-Host`
- `X-Forwarded-Server`
- `X-Host`
- `Forwarded: host="attacker.com"`
- `X-Original-URL`
- `Client-IP`

### 4.3 Caching Discrepancies (Unkeyed Inputs)
If an application uses the `X-Forwarded-Host` header to generate absolute URLs dynamically in the HTML response, but the CDN or Cache layer does *not* include `X-Forwarded-Host` in the "cache key", a severe Web Cache Poisoning vulnerability arises.
The attacker requests `/index.html` with `X-Forwarded-Host: evil.com`. The application generates the page with `<script src="https://evil.com/app.js"></script>`. The CDN caches this poisoned response. All subsequent legitimate users visiting the site receive the malicious script.

## 5. Exploitation Scenarios

### 5.1 Password Reset Poisoning
This is a classic exploit. The application generates a password reset link to be sent via email. If it uses the injected `X-Forwarded-Host` to build the domain portion of the URL, the victim receives an email containing a link to the attacker's server (with the valid reset token). When the victim clicks it, the attacker intercepts the token and compromises the account.

### 5.2 Web Cache Poisoning
As described above, manipulating unkeyed forwarded headers allows attackers to inject malicious absolute URLs or manipulate routing directives, caching the poisoned response to execute Stored DOM XSS or redirect users globally.

### 5.3 Bypassing Access Controls
Some applications restrict administrative endpoints based on the `Host` header or the originating IP.
- **IP Spoofing:** Injecting `X-Forwarded-For: 127.0.0.1` might bypass restrictions on `/admin` if the application logic trusts this header for ACL checks.
- **Protocol Spoofing:** Injecting `X-Forwarded-Proto: https` might bypass requirements that secure actions only occur over HTTPS, circumventing security controls on a plaintext connection.

### 5.4 Server-Side Request Forgery (SSRF) and Routing Attacks
In certain architectures, internal reverse proxies route traffic based on the `Host` header. By manipulating `X-Forwarded-Host`, an attacker might cause an internal load balancer to route the request to an unintended internal microservice, effectively achieving SSRF.

## 6. Step-by-Step Exploitation

### Step 1: Identification
Use a proxy like Burp Suite. Intercept a normal request. Add `X-Forwarded-Host: burpcollaborator.net`. Observe the response.
- If the application reflects `burpcollaborator.net` in absolute URLs (like `<link>`, `<script>`, or `meta` tags), it is vulnerable.
- If an email is triggered (e.g., password reset), check if the link in the email points to the collaborator payload.

### Step 2: Cache Poisoning Verification
If reflection occurs, check if the response is cached (look for headers like `X-Cache: HIT`). Make the request without the injected header to see if the poisoned response persists.

### Step 3: IP and Protocol Fuzzing
Test `X-Forwarded-For: 127.0.0.1` on 403 Forbidden endpoints to check for internal access bypass.

## 7. Advanced Obfuscation
Sometimes WAFs block `X-Forwarded-Host`. Attackers can use:
- Case variations: `x-fOrWaRdEd-HoSt`
- White space injection: `X-Forwarded-Host : attacker.com`
- Using the standard RFC 7239 header: `Forwarded: for=192.0.2.60;proto=http;by=203.0.113.43;host=attacker.com`

## 8. Mitigation and Defense

### 8.1 Strict Proxy Trust Configuration
Configure backend web frameworks to trust Forwarded headers *only* when the direct connecting IP address matches a known, trusted internal proxy or load balancer.
Example in Django:
```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Must only be used if a secure proxy is directly in front of Django!
```

### 8.2 Strip External Headers
The outermost edge device (CDN or edge Load Balancer) must actively strip or overwrite any `X-Forwarded-*` or `Forwarded` headers present in incoming internet requests before routing them internally.

### 8.3 Absolute URL Generation
Avoid using dynamic Host headers for critical functions like password reset links. Instead, define a static base URL in the application's configuration file and use that for generating absolute links.

### 8.4 Cache Key Configuration
If the application dynamically alters content based on specific headers, ensure those headers are explicitly included in the cache key configuration of the CDN or caching proxy.

## 9. Summary
Forwarded headers provide necessary context in proxy-heavy environments, but their improper handling creates massive security holes. Treating all HTTP headers as untrusted input and enforcing strict proxy topologies are key to mitigating these attacks.

## Chaining Opportunities
- **[[15 - Web Cache Poisoning]]**: Forwarded headers are the primary vector for finding unkeyed cache parameters.
- **[[02 - Server-Side Request Forgery SSRF]]**: Internal routing manipulation.
- **[[10 - HTTP Request Smuggling]]**: Bypassing edge protections to deliver manipulated headers directly to the backend.

## Related Notes
- [[08 - Origin Header Spoofing]]
- [[03 - HTTP Header Injection]]
- [[12 - Business Logic Vulnerabilities]]
