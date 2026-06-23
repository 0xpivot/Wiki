---
course: API Security
topic: Server Side Request Forgery
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is Server Side Request Forgery (SSRF), and how does it work?**

SSRF is a vulnerability that allows an attacker to induce a server into making unintended requests to an external or internal service. This typically happens when an application takes user input and uses it to make requests to other services without proper validation. For example, if an API accepts a URL from a user and fetches content from that URL, an attacker could provide a URL pointing to an internal service, leading to unauthorized access or information leakage.

**Q2. How can SSRF be exploited to perform port scanning on an internal network?**

An attacker can exploit SSRF to perform port scanning by crafting requests to the server to scan specific ports on internal network addresses. For instance, if the server is vulnerable to SSRF and can make HTTP requests, an attacker might provide a URL like `http://192.168.1.10:8080/`, where `192.168.1.10` is an internal IP address and `8080` is the port to be scanned. The server’s response to this request can indicate whether the port is open or closed, allowing the attacker to map out the internal network.

**Q3. Explain how SSRF can be used to access applications running on an intranet or local network.**

If an application is vulnerable to SSRF and can make requests to internal IP addresses, an attacker can use this vulnerability to access applications running on the intranet or local network. By providing a crafted URL that points to an internal IP address and port, the attacker can make the server interact with these internal applications. This can lead to unauthorized access to sensitive data or control over internal services.

**Q4. How can SSRF be leveraged to read local files from the underlying operating system?**

SSRF can be used to read local files if the vulnerable application supports file protocols like `file://`. An attacker can craft a request to read a local file by providing a URL like `file:///etc/passwd` (for Linux systems). If the server processes this request, it will return the contents of `/etc/passwd`, which contains user account information. This can lead to significant information leakage and potential compromise of the system.

**Q5. What are some recent real-world examples of SSRF vulnerabilities, and how were they exploited?**

One notable example is the SSRF vulnerability in Docker Hub (CVE-2020-7827). This vulnerability allowed attackers to manipulate the `X-Docker-Token` header to trigger requests to arbitrary URLs, including internal network addresses. Attackers could use this to perform port scanning, access internal services, and potentially read sensitive files from the underlying operating system. Another example is the SSRF vulnerability in GitHub Actions (CVE-2021-22205), which allowed attackers to manipulate environment variables to make requests to internal services, leading to unauthorized access and data exfiltration.

**Q6. How can developers prevent SSRF vulnerabilities in their applications?**

To prevent SSRF vulnerabilities, developers should:

1. **Validate and sanitize user inputs**: Ensure that any user-provided URLs or IP addresses are validated against a whitelist of allowed domains or IP ranges.
2. **Use secure libraries and frameworks**: Leverage well-tested libraries and frameworks that handle URL parsing and request validation securely.
3. **Restrict network access**: Configure the application to restrict outbound network requests to trusted domains and IP addresses.
4. **Implement rate limiting and monitoring**: Monitor and limit the number of requests made by the application to detect and mitigate abuse.
5. **Regularly update and patch dependencies**: Keep all dependencies up-to-date to avoid known vulnerabilities.

By following these best practices, developers can significantly reduce the risk of SSRF vulnerabilities in their applications.

---
<!-- nav -->
[[API Security/14-Server Side Request Forgery/01-Background Concept Minimal Refer Hunter 20 Section/02-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]] | [[API Security/14-Server Side Request Forgery/01-Background Concept Minimal Refer Hunter 20 Section/00-Overview|Overview]]
