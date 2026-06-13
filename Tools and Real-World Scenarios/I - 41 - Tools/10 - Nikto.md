---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.10 Nikto"
---

# 41.10 Nikto: Comprehensive Web Server Scanner

## Introduction

`Nikto` is a legendary, open-source (GPL) web server scanner which performs comprehensive tests against web servers for multiple items, including over 6700 potentially dangerous files/programs, checks for outdated versions of over 1250 servers, and version specific problems on over 270 servers. 

While it is one of the oldest tools in the web application penetration testing arsenal, it remains relevant due to its extensive database of known misconfigurations, default files, and legacy vulnerabilities that modern, heavily JavaScript-focused scanners often overlook. It is a noisy, aggressive scanner, making it highly effective for internal testing but easy to spot by defensive teams.

### Why Nikto?
- **Speed and Simplicity**: Requires minimal configuration. Point and shoot.
- **Vast Database**: Contains signatures for thousands of known vulnerabilities, outdated software, and default administrative interfaces.
- **Server Misconfigurations**: Excellent at identifying missing security headers, improper directory indexing, and HTTP server fingerprinting.
- **Plugin Architecture**: Easily extensible via plugins.

## Architecture and Execution Flow

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Target Server   | <---- |      Nikto Engine     | <---- | Configuration &   |
|   (HTTP/HTTPS)    | ----> |  (Perl Script)        | ----> | Plugin Database   |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +-------------------+
         |                              |
         |  HTTP Responses              |
         |  (Headers, Body, Status)     | Evaluates signatures
         |                              v
         |                  +-----------------------+
         +----------------> | Reporting Module      |
                            | (Text, HTML, CSV)     |
                            +-----------------------+
```

Nikto operates by executing a series of predefined tests (plugins) against a target URL or IP address. It begins by mapping the basic characteristics of the server (identifying the HTTP daemon, checking for SSL/TLS support) and then systematically requests paths, files, and queries looking for specific string matches or status codes that indicate a vulnerability or misconfiguration.

## Core Concepts

1. **Plugins**: Nikto's logic is modular. Plugins handle different classes of vulnerabilities (e.g., XSS, SQLi, file inclusion, default credentials).
2. **Evasion**: Contains basic IDS/IPS evasion techniques to alter the request signature (e.g., URL encoding, directory traversal padding).
3. **Tuning**: The ability to restrict Nikto to only run specific classes of tests to save time and reduce noise.
4. **False Positives**: Nikto is prone to false positives, especially against servers that return 200 OK for 404 Not Found pages (custom error pages). It requires manual verification of findings.

## Installation and Setup

Nikto is written in Perl and is natively included in Kali Linux.
To install manually on a Debian-based system:
```bash
sudo apt update
sudo apt install nikto
```
Or via Git:
```bash
git clone https://github.com/sullo/nikto.git
cd nikto/program
perl nikto.pl -h
```

## Detailed Usage and Methodology

### Basic Scanning
The most basic execution requires only the `-h` (host) flag. Nikto will automatically detect if it needs to use HTTP or HTTPS (though specifying is safer).
```bash
nikto -h http://example.com
```
Or for an IP address:
```bash
nikto -h 192.168.1.100
```

### Specifying Ports
If the web server is running on a non-standard port, use the `-p` flag:
```bash
nikto -h 192.168.1.100 -p 8080,8443
```

### SSL/TLS Testing
When testing HTTPS endpoints, you can force SSL usage, which is sometimes required if Nikto fails to detect it automatically.
```bash
nikto -h https://example.com -ssl
```

### Tuning the Scan (Reducing Noise)
By default, Nikto runs all tests. This can take a long time and generate massive logs on the target. You can tune the scan using the `-Tuning` flag followed by a number or letter representing a class of tests:
- `1`: Interesting File / Seen in logs
- `2`: Misconfiguration / Default File
- `3`: Information Disclosure
- `4`: Injection (XSS/Script/HTML)
- `8`: Command Execution / Remote Shell
- `9`: SQL Injection

To run only tests for Information Disclosure and Injection:
```bash
nikto -h http://example.com -Tuning 34
```
To run everything *except* Denial of Service tests (highly recommended):
```bash
nikto -h http://example.com -Tuning x 6
```
*(Wait, 'x' means reversed tuning. Standard is `-Tuning x 6` to exclude DOS).*

### Bypassing IDS/WAF
Nikto offers several evasion techniques via the `-evasion` flag:
- `1`: Random URI encoding (non-UTF8)
- `2`: Directory self-reference (`/./`)
- `3`: Premature URL ending
- `4`: Prepend long random string
- `8`: Use Windows directory separator (`\`)

```bash
nikto -h http://example.com -evasion 128
```

### Authentication
If the target requires Basic Authentication, you can pass credentials:
```bash
nikto -h http://example.com -id "username:password"
```

## Output and Reporting

For integration into larger pentesting workflows or client reports, saving the output is crucial. Nikto supports various formats including HTML, CSV, and XML.
```bash
nikto -h http://example.com -o nikto_report.html -Format htm
```
Or to save as CSV for spreadsheet parsing:
```bash
nikto -h http://example.com -o nikto_report.csv -Format csv
```

## Proxy Integration
Routing Nikto through Burp Suite is an excellent way to capture exactly what payloads Nikto is sending, allowing for detailed manual analysis of any interesting responses.
```bash
nikto -h http://example.com -useproxy http://127.0.0.1:8080
```

## Security and Ethical Considerations
- **Extremely Noisy**: Nikto makes thousands of requests rapidly. It will trigger almost any modern IDS/IPS/WAF.
- **Log Flooding**: It can fill up server logs quickly, which might cause operational issues on legacy systems.
- **False Positives**: Always verify Nikto's findings. A response indicating a vulnerable file might just be a server catching the request and serving a generic 200 OK page.

## Chaining Opportunities
- Initial reconnaissance with Nikto can reveal outdated server versions, which can then be researched for CVEs and exploited via [[12 - Metasploit Framework]].
- Discovered endpoints or default credentials should be manually verified using [[01 - Burp Suite]].
- If Nikto finds potential SQL injection vectors, feed those specific endpoints to [[09 - sqlmap]] for in-depth exploitation.

## Related Notes
- [[08 - Feroxbuster]]
- [[09 - sqlmap]]
- [[11 - Nuclei]]
- [[12 - Metasploit Framework]]
