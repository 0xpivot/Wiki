---
course: API Security
topic: Server Side Request Forgery
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how an attacker could exploit server-side DNS lookups through HTTP headers.**

An attacker can exploit server-side DNS lookups by injecting malicious data into specific HTTP headers that the server uses to perform DNS queries. One common method involves using the `X-Forwarded-For` header, which is often used to pass along the original client IP address when requests are routed through proxies. By setting this header to an arbitrary domain controlled by the attacker, the server may perform a DNS lookup for that domain, potentially revealing sensitive information or allowing further exploitation.

For example, an attacker might set the `X-Forwarded-For` header to a domain such as `attacker.com`, which resolves to an IP address controlled by the attacker. If the server performs a DNS lookup for this domain, the attacker can monitor the DNS traffic to gain insights into the internal workings of the application or even inject additional malicious content.

**Q2. How can an attacker use the `host` parameter to trigger a server-side DNS lookup?**

The `host` parameter is another potential entry point for triggering a server-side DNS lookup. This parameter is typically used to specify the hostname of the server being accessed, and the server may perform a DNS lookup to resolve this hostname to an IP address. An attacker can exploit this behavior by setting the `host` parameter to an arbitrary domain under their control.

For instance, an attacker could modify a request to include a `host` parameter set to `malicious-domain.com`. When the server processes this request, it may attempt to resolve `malicious-domain.com` via a DNS lookup. The attacker can then monitor the DNS traffic to determine whether the server has performed the lookup, indicating a successful exploitation attempt.

**Q3. Describe how to configure a collaborator server to detect server-side DNS lookups.**

To configure a collaborator server to detect server-side DNS lookups, follow these steps:

1. **Set Up the Collaborator Server**: Use a tool like Burp Suite's Collaborator Client to set up a collaborator server. This server will listen for incoming connections and record details about the requests it receives.

2. **Generate a Collaborator Domain**: Use the collaborator server to generate a unique domain name that will be used in the attack. This domain will resolve to an IP address controlled by the collaborator server.

3. **Inject the Collaborator Domain**: Inject the collaborator domain into the HTTP headers or parameters of the target application. Common headers to inject include `X-Forwarded-For` or the `Host` parameter.

4. **Monitor the Collaborator Server**: Once the request is sent, monitor the collaborator server to see if it receives a DNS lookup request for the injected domain. If it does, this indicates that the server performed a DNS lookup for the specified domain.

Here is an example of how to inject the collaborator domain into an HTTP request:

```http
POST /api/products HTTP/1.1
Host: target-app.com
X-Forwarded-For: collaborator-domain.com
Content-Type: application/json

{
  "product": {
    "name": "Test Product",
    "price": 100
  }
}
```

By monitoring the collaborator server, you can confirm whether the server performed a DNS lookup for `collaborator-domain.com`.

**Q4. What recent real-world examples demonstrate the risks of server-side DNS lookups?**

Recent real-world examples highlight the risks associated with server-side DNS lookups. One notable case is the widespread exploitation of the Log4j vulnerability (CVE-2021-44228), where attackers could inject malicious payloads into logging statements that would cause the application to perform DNS lookups to attacker-controlled domains. This allowed attackers to exfiltrate sensitive information and execute remote code.

Another example is the exploitation of misconfigured web servers and applications that improperly handle the `Host` header. In some cases, attackers have been able to inject malicious domains into the `Host` header, causing the server to perform DNS lookups to attacker-controlled domains. This can lead to information disclosure, denial of service, or further exploitation.

These examples underscore the importance of properly validating and sanitizing input from HTTP headers and parameters to prevent unintended DNS lookups and other security issues.

**Q5. How can developers mitigate the risk of server-side DNS lookups being exploited?**

Developers can mitigate the risk of server-side DNS lookups being exploited by implementing the following best practices:

1. **Validate Input**: Ensure that all input from HTTP headers and parameters is validated and sanitized. Specifically, validate the `Host` header and any custom headers like `X-Forwarded-For` to ensure they contain valid and expected values.

2. **Use Whitelisting**: Implement whitelisting for the `Host` header and other relevant headers to restrict them to known good values. This prevents attackers from injecting arbitrary domains.

3. **Limit DNS Resolution**: Restrict the ability of the application to perform DNS lookups for arbitrary domains. Consider using a DNS resolver that enforces strict policies or limits the number of DNS queries.

4. **Monitor DNS Traffic**: Monitor DNS traffic for unusual patterns or requests to suspicious domains. This can help detect and respond to potential exploitation attempts.

5. **Regular Audits**: Regularly audit the application’s handling of HTTP headers and parameters to identify and fix any vulnerabilities related to DNS lookups.

By following these practices, developers can significantly reduce the risk of server-side DNS lookups being exploited and improve the overall security of their applications.

---
<!-- nav -->
[[API Security/14-Server Side Request Forgery/04-External Service Intercation DNS/01-Introduction to Server-Side Request Forgery (SSRF)|Introduction to Server-Side Request Forgery (SSRF)]] | [[API Security/14-Server Side Request Forgery/04-External Service Intercation DNS/00-Overview|Overview]]
