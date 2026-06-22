---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Real-World Examples

### CVE-2021-21972: Docker API SSRF

In 2021, a vulnerability was discovered in the Docker API that allowed SSRF attacks. Attackers could exploit this vulnerability to access internal resources and perform unauthorized actions.

```http
POST /v1.41/containers/create HTTP/1.1
Host: docker.example.com
Content-Type: application/json

{
  "Image": "alpine",
  "Cmd": ["sh", "-c", "curl http://internal-resource.example.com"]
}
```

### CVE-2022-22965: Spring Framework SSRF

Another notable example is the SSRF vulnerability in the Spring Framework, which allowed attackers to access internal resources through the `RestTemplate` class.

```java
// Vulnerable code
RestTemplate restTemplate = new RestTemplate();
String url = "http://internal-resource.example.com";
restTemplate.getForObject(url, String.class);
```

### Secure Code Fixes

To prevent SSRF attacks, developers should validate and sanitize all input parameters that are used to construct URLs. Additionally, they should restrict the domains that the server can access.

```java
// Secure code
RestTemplate restTemplate = new RestTemplate();
String url = "http://example.com";
if (isValidUrl(url)) {
    restTemplate.getForObject(url, String.class);
}

boolean isValidUrl(String url) {
    // Implement validation logic
    return true;
}
```

---
<!-- nav -->
[[13-Preventing and Mitigating SSRF Attacks|Preventing and Mitigating SSRF Attacks]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[15-Sanitization and Validation of Client-Supplied Input Data|Sanitization and Validation of Client-Supplied Input Data]]
