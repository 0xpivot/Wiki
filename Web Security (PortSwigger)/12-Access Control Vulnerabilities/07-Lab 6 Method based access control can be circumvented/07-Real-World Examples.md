---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Real-World Examples

### Recent CVEs and Breaches

Several real-world examples illustrate the impact of method-based access control vulnerabilities:

- **CVE-2021-21972**: A vulnerability in the WordPress REST API allowed attackers to modify posts and pages using a `POST` request instead of the expected `PUT` request.
- **CVE-2020-14882**: A vulnerability in the Atlassian Jira REST API allowed unauthorized users to create new issues using a `POST` request instead of the expected `PUT` request.

These examples highlight the importance of properly validating HTTP methods and ensuring that access control mechanisms are robust.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/06-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/08-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]]
