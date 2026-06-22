---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## White Box Testing Perspective

White box testing involves testing the application with access to its internal workings. The goal is to identify vulnerabilities such as clickjacking by analyzing the code and configurations.

### Steps to Identify Clickjacking Vulnerabilities

1. **Identify Technologies**: Determine the technologies used by the application, such as frameworks, libraries, and servers.
2. **Review Configurations**: Check the configurations of the application, including headers and policies.
3. **Analyze Code**: Review the code for any potential vulnerabilities, such as missing or incorrect headers.

#### Example Analysis

Here’s an example of reviewing the configuration of an application:

```json
{
    "server": {
        "name": "Apache",
        "version": "2.4.41"
    },
    "headers": {
        "X-Frame-Options": "SAMEORIGIN",
        "Content-Security-Policy": "frame-ancestors 'self'"
    }
}
```

In this example, the application is configured with both `X-Frame-Options` and `Content-Security-Policy` headers set to restrict framing to the same origin.

### How to Prevent / Defend

To defend against clickjacking during white box testing:

1. **Implement Headers**: Ensure the `X-Frame-Options` and `Content-Security-Policy` headers are correctly configured.
2. **Regular Audits**: Conduct regular security audits to identify and mitigate vulnerabilities.
3. **Code Reviews**: Perform regular code reviews to ensure the application is free from vulnerabilities.

---
<!-- nav -->
[[16-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[18-X-Frame-Options Header|X-Frame-Options Header]]
