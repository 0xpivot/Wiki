---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Background Knowledge on Access Control Vulnerabilities

Access control vulnerabilities occur when an application fails to properly restrict access to certain resources or functionalities based on user permissions. One common form of access control vulnerability arises from the improper handling of HTTP headers, particularly non-standard ones such as `X-Original-URL`. This header can be used to manipulate the perceived URL of a request, potentially bypassing access controls that rely on URL-based restrictions.

### What is `X-Original-URL`?

The `X-Original-URL` header is a non-standard HTTP header that can be used to specify the original URL of a request. This header is often used in reverse proxy scenarios where the proxy server modifies the URL before forwarding the request to the backend server. However, if the backend server incorrectly trusts this header, it can lead to security vulnerabilities.

#### Why Does `X-Original-URL` Matter?

In many web applications, access control mechanisms are implemented based on the URL of the request. For example, an application might restrict access to an administrative panel by checking the URL and denying access if the user is not authorized. If the application allows the `X-Original-URL` header to override the actual URL, an attacker can potentially bypass these restrictions.

### How Does `X-Original-URL` Work Under the Hood?

When a request is made to a web server, the server parses the HTTP headers and uses them to determine how to handle the request. In the case of the `X-Original-URL` header, the server might use the value of this header to determine the resource to serve, instead of the actual URL in the request line.

#### Example Scenario

Consider a web application that restricts access to an administrative panel (`/admin`) to users with specific privileges. If the application checks the URL to enforce this restriction but also allows the `X-Original-URL` header to override the URL, an attacker can craft a request that bypasses the restriction.

```http
GET /nonexistent_directory/3243 HTTP/1.1
Host: example.com
X-Original-URL: /admin
```

In this example, the attacker sends a request to a non-existent directory but sets the `X-Original-URL` header to `/admin`. If the server trusts this header, it will treat the request as if it were directed to the administrative panel, potentially allowing unauthorized access.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities related to improper handling of HTTP headers include:

- **CVE-2021-21972**: A vulnerability in Apache Struts allowed attackers to bypass access controls by manipulating the `X-Original-URL` header. This vulnerability was exploited in several high-profile attacks.
- **CVE-2022-22965**: A similar issue was found in a popular web framework, where the framework incorrectly trusted the `X-Original-URL` header, leading to unauthorized access to sensitive resources.

These examples highlight the importance of proper handling of HTTP headers and the potential risks associated with trusting non-standard headers.

---
<!-- nav -->
[[02-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/04-Common Pitfalls and Mistakes|Common Pitfalls and Mistakes]]
