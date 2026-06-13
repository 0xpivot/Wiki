---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.30 Nuclei Writing Custom Templates"
---

# Nuclei: Advanced Usage and Writing Custom Templates

## 1. Introduction and Core Concepts
Nuclei, developed by ProjectDiscovery, is the preeminent modern vulnerability scanner. Unlike legacy scanners such as Nikto or Nessus, which rely on hardcoded plugins or proprietary scripting languages, Nuclei is driven entirely by YAML-based templates. This "Infrastructure as Code" approach to vulnerability scanning allows the security community to rapidly write, share, and execute checks for the newest CVEs within hours of public disclosure.

Nuclei is incredibly fast, utilizing Go's robust concurrency model. It doesn't just scan HTTP; it supports DNS, TCP, SSH, SSL, and even custom protocol interactions. However, the true power of Nuclei lies not in running the default community templates, but in the ability to write custom templates tailored to specific organizational logic, proprietary software, or newly discovered 0-day vulnerabilities.

## 2. How the Tool Works (Internal Mechanics)
Nuclei operates as a highly optimized template execution engine. When fed a target (URL, IP, or CIDR) and a template, it compiles the YAML definition into a series of highly efficient network requests. 

It handles connection pooling, rate limiting, and HTTP pipelining natively. Once a request is sent, the response is piped through "Matchers" and "Extractors" defined in the YAML. Matchers (using Regex, String comparison, or Status Codes) determine if the vulnerability exists. Extractors pull specific data out of the response (like an AWS key or database password) to display in the output.

### ASCII Diagram: Nuclei Execution Architecture

```text
[ YAML Template ]       [ Target List (URLs/IPs) ]
        |                          |
        v                          v
+---------------------------------------------------+
| Nuclei Core Engine (Golang)                       |
|                                                   |
| 1. Request Engine                                 |
|    - HTTP / TCP / DNS Client                      |
|    - Handles Retries, Timeouts, Rate Limits       |
|                                                   |
| 2. Execution Logic                                |
|    - Replaces variables (e.g., {{BaseURL}})       |
|    - Injects Payloads                             |
|                                                   |
| 3. Evaluation Engine                              |
|    - Applies Matchers (Regex, Words, Status)      |
|    - Applies Extractors (Capturing Groups)        |
+---------------------------------------------------+
        |                          |
   [ Match = False ]          [ Match = True ]
        |                          |
   (Discarded)                (Logged / Alerted)
                                   |
                                   v
                       [ JSON / Markdown / CLI Output ]
```

## 3. Basic Usage & CLI Refresher
Before writing templates, you must understand how to execute them.

```bash
# Update the core engine and templates
nuclei -update
nuclei -ut

# Run default templates against a single URL
nuclei -u https://example.com

# Run specific template categories (e.g., CVEs and Exposed Panels)
nuclei -l urls.txt -t cves/ -t exposed-panels/

# Run with custom rate limits to avoid WAF blocking
nuclei -l urls.txt -rl 50 -c 10
```

## 4. The Anatomy of a Nuclei Template
A custom template is a simple YAML file divided into three main blocks:
1. **Metadata (`id`, `info`)**: Describes the vulnerability, author, severity, and tags.
2. **Requests (`http`, `network`, `dns`)**: Defines the actual payload, headers, method, and endpoint.
3. **Matchers / Extractors (`matchers`, `extractors`)**: Defines what the vulnerable response looks like.

### 4.1 Basic HTTP Template Example
Let's write a template to detect an exposed `.env` file containing AWS credentials.

```yaml
id: exposed-env-aws

info:
  name: Exposed .env File with AWS Keys
  author: YourName
  severity: high
  description: Searches for an exposed .env file containing AWS_ACCESS_KEY_ID.
  tags: exposure,config,aws

http:
  - method: GET
    path:
      - "{{BaseURL}}/.env"
      - "{{BaseURL}}/api/.env"

    matchers-condition: and
    matchers:
      - type: word
        words:
          - "AWS_ACCESS_KEY_ID="
          - "AWS_SECRET_ACCESS_KEY="
        condition: or

      - type: status
        status:
          - 200
```
**Explanation:** 
- `{{BaseURL}}` is a built-in Nuclei variable. If you pass `https://target.com`, it tests `https://target.com/.env` and `https://target.com/api/.env`.
- `matchers-condition: and` means *both* the word matcher AND the status matcher must be true for the template to fire.

## 5. Advanced Template Creation

### 5.1 Using Extractors
Extractors don't just say "vulnerable"; they pull the sensitive data out of the response and print it to the terminal.

```yaml
    extractors:
      - type: regex
        name: aws-key
        regex:
          - "AKIA[0-9A-Z]{16}"
```
If the `.env` file is found, Nuclei will extract the regex match and display the actual AWS key in the output.

### 5.2 Dynamic Workflows and Payloads
Sometimes you need to test multiple parameters or use external wordlists inside a template. You can define `payloads`.

```yaml
http:
  - method: POST
    path:
      - "{{BaseURL}}/login"
    body: '{"username":"{{username}}", "password":"{{password}}"}'
    headers:
      Content-Type: application/json
    
    payloads:
      username:
        - admin
        - root
      password:
        - admin123
        - password
    attack: clusterbomb
```
This acts like Burp Suite Intruder. The `clusterbomb` attack type tests all combinations of username and password.

### 5.3 Multi-Step Requests (Chaining)
For complex vulnerabilities (like blind SSRF or authenticated exploits), you need to send a request, extract a token, and use that token in the next request.

```yaml
http:
  - raw:
      - |
        POST /api/login HTTP/1.1
        Host: {{Hostname}}
        Content-Type: application/json

        {"user":"admin","pass":"admin"}
      
      - |
        GET /api/admin/dashboard HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{auth_token}}

    extractors:
      - type: json
        part: body
        name: auth_token
        internal: true # Internal means don't print this, just save it as a variable
        json:
          - '.token'
```

## 6. Real-world Scenarios for Custom Templates
### 6.1 Internal Application Scanning
If your organization deploys a custom microservice that has a known vulnerability (e.g., an unauthenticated debug endpoint at `/internal/v1/metrics`), the public Nuclei templates will not catch it. You must write a custom template:
1. Define the path `{{BaseURL}}/internal/v1/metrics`.
2. Define a matcher looking for specific proprietary JSON output.
3. Integrate this custom template into your CI/CD pipeline using the Nuclei GitHub Action.

### 6.2 Zero-Day Hunting
When a new vulnerability drops (e.g., Log4j or a new Confluence RCE), proof-of-concept (PoC) code is usually published on Twitter or GitHub. Security engineers can rapidly translate a Python PoC into a YAML Nuclei template in minutes, allowing them to scan thousands of corporate assets immediately, long before commercial scanners like Nessus release an official plugin.

## 7. Interaction with OAST (ProjectDiscovery Interactsh)
Nuclei natively integrates with `interactsh` to detect out-of-band (OOB) vulnerabilities like Blind SSRF or Blind RCE.

```yaml
http:
  - method: GET
    path:
      - "{{BaseURL}}/webhook?url=http://{{interactsh-url}}"

    matchers:
      - type: word
        part: interactsh_protocol # Listens on the OAST server
        words:
          - "http"
          - "dns"
```
If the target server makes an HTTP or DNS request to the generated `interactsh` URL, Nuclei flags it as vulnerable.

## 8. Chaining Opportunities
Nuclei is frequently the final step in an automated reconnaissance pipeline.

1. **Subfinder** -> Find all subdomains.
2. **Httpx** -> Filter for active web servers and grab technologies.
3. **Nuclei** -> Run specific templates based on the technology detected by httpx.

```bash
subfinder -d example.com | httpx -silent | nuclei -t cves/
```

## 9. Common Pitfalls and Limitations
- **Syntax Errors**: YAML is strictly indented. A single space error will break the template. Always test templates locally with `nuclei -t mytemplate.yaml -u http://localhost -debug` before mass scanning.
- **Stateful Applications**: Nuclei is stateless by design. Handling complex state (e.g., a 5-step checkout process with CSRF tokens at each step) is very difficult in YAML and is better suited for a custom Python script.

## 10. Related Notes
- [[29 - Nikto Full Config and Output Interpretation]] - The legacy predecessor to Nuclei.
- [[10 - API10 — Unsafe Consumption of APIs]] - Custom Nuclei templates are perfect for detecting misconfigured 3rd party API integrations.
- [[07 - API7 — Security Misconfiguration]] - Exposed files and admin panels are easily caught by Nuclei.
