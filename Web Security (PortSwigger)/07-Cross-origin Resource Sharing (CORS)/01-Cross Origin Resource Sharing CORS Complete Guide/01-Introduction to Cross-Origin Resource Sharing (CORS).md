---
course: Web Security
topic: Cross-origin Resource Sharing (CORS)
tags: [web-security]
---

## Introduction to Cross-Origin Resource Sharing (CORS)

Cross-Origin Resource Sharing (CORS) is a mechanism that allows web applications to make requests to resources hosted on different domains than the one serving the web page. This is necessary because of the Same-Origin Policy, which restricts how a document or script loaded from one origin can interact with a resource from another origin. CORS provides a way to relax these restrictions in a controlled manner, enabling cross-origin requests while maintaining security.

### What is CORS?

CORS is a security feature implemented by web browsers to ensure that web pages cannot make unauthorized requests to resources on other domains. It works by adding specific HTTP headers to the requests and responses, allowing servers to specify which origins are allowed to access their resources.

#### Same-Origin Policy

The Same-Origin Policy is a critical security measure enforced by web browsers. It states that a web page can only make requests to the same domain, protocol, and port as the web page itself. For example, a web page served from `https://example.com` can only make requests to `https://example.com`, but not to `https://another-example.com`.

#### Why CORS Matters

Without CORS, web developers would be severely limited in creating dynamic web applications that rely on data from external sources. For instance, a weather app might need to fetch data from a third-party weather service. CORS enables this interaction by allowing the server to explicitly permit such cross-origin requests.

### Types of CORS Vulnerabilities

There are several types of CORS vulnerabilities that can occur due to misconfigurations:

1. **Permissive CORS Headers**: When a server sets overly permissive CORS headers, allowing any origin to make requests.
2. **Insecure Wildcard Origins**: Using wildcard origins (`*`) without proper validation.
3. **Exposed Endpoints**: Exposing sensitive endpoints that should not be accessible via CORS.
4. **Preflight Requests**: Misconfigured handling of preflight requests (`OPTIONS` method).

### Commonality of CORS Vulnerabilities

CORS vulnerabilities are relatively common, especially in web applications that handle sensitive data. According to recent studies and reports, many popular websites and APIs have been found to have misconfigured CORS settings, leading to potential security risks.

### Real-World Examples

Several high-profile breaches and vulnerabilities have been attributed to CORS misconfigurations:

- **CVE-2021-21974**: A vulnerability in the Microsoft Azure API Management service allowed attackers to bypass CORS restrictions and access sensitive data.
- **CVE-2020-14182**: A CORS misconfiguration in the Zoom API allowed unauthorized access to user data.

These examples highlight the importance of properly configuring CORS to prevent unauthorized access and data exposure.

---
<!-- nav -->
[[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/00-Overview|Overview]] | [[02-Same Origin Policy Overview|Same Origin Policy Overview]]
