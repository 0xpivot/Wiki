---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.11 Nuclei"
---

# 41.11 Nuclei: Template-Based Fast Vulnerability Scanner

## Introduction

`Nuclei` is a modern, fast, and highly customizable vulnerability scanner developed by ProjectDiscovery. Unlike traditional scanners (like Nessus or Nikto) that rely on built-in, hardcoded checks, Nuclei uses a template-based system. This means that every vulnerability check, misconfiguration test, or fingerprinting routine is defined in simple, human-readable YAML files.

Because of this template-driven architecture, Nuclei has become the industry standard for Bug Bounty hunters, DevSecOps pipelines, and modern penetration testers. It allows security researchers to rapidly write and distribute checks for new CVEs (Common Vulnerabilities and Exposures) often within hours of their public disclosure.

### Why Nuclei?
- **Speed**: Written in Go, it is incredibly fast and designed to scan massive lists of URLs or IP addresses asynchronously.
- **Customization**: Templates are just YAML. Anyone can write a custom template for an internal application or a newly discovered 0-day.
- **Community**: The open-source `nuclei-templates` repository contains thousands of high-quality, peer-reviewed checks covering everything from basic misconfigurations to complex Remote Code Execution (RCE) chains.
- **Integration**: Designed to seamlessly plug into CI/CD pipelines and integrate with other tools via JSON output.

## Architecture and Execution Flow

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |   nuclei Engine   |
|   nuclei-templates| ----> |   YAML Parser         | ----> |   (Go Routines)   |
|   (GitHub Repo)   |       |   & Validator         |       |                   |
|                   |       |                       |       |                   |
+-------------------+       +-----------------------+       +---------+---------+
                                                                      |
                                                                      | Concurrent Requests
                                                                      v
                                                            +-------------------+
                                                            |                   |
                                                            | Target Host(s)    |
                                                            | (HTTP, DNS, TCP)  |
                                                            |                   |
                                                            +-------------------+
```

When Nuclei runs, it first parses the specified YAML templates. It supports various protocols including HTTP, DNS, TCP, and even headless browser interactions. It then maps these templates to the target list and executes the requests concurrently. Finally, it uses powerful matchers and extractors (using regex, DSL, or JSON queries) on the responses to determine if a vulnerability exists.

## Core Concepts

1. **Templates**: YAML files defining the request to be sent and the criteria for a successful match.
2. **Matchers**: The logic that defines a vulnerability. E.g., matching a specific string in the HTTP body AND a status code of 200.
3. **Extractors**: Logic used to pull out specific data from a response (like extracting an AWS access key found in an exposed `.env` file).
4. **Workflows**: Chaining multiple templates together. For example, a workflow might first fingerprint a server as running WordPress, and only *then* run the hundreds of specific WordPress plugin vulnerability templates, saving immense amounts of time.

## Installation and Setup

Nuclei is written in Go. The easiest way to install it is via the official Go toolchain or downloading the precompiled binary.
```bash
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
```
After installation, you must download the official templates:
```bash
nuclei -update-templates
```
This clones the `projectdiscovery/nuclei-templates` repository to your `~/nuclei-templates/` directory.

## Detailed Usage and Methodology

### Basic Scanning
To scan a single URL with all default templates:
```bash
nuclei -u https://example.com
```
To scan a list of targets (the most common use case):
```bash
nuclei -l targets.txt
```

### Selecting Specific Templates
Running *all* templates against a target can be noisy and slow. It is often better to run specific categories.
- **By Tag**: Run templates tagged with specific keywords.
  ```bash
  nuclei -u https://example.com -tags cve,rce,lfi
  ```
- **By Severity**: Run only high and critical severity templates.
  ```bash
  nuclei -u https://example.com -severity high,critical
  ```
- **By Author or Directory**: Run templates from a specific folder.
  ```bash
  nuclei -u https://example.com -t cves/2023/
  ```

### Writing a Custom Template
The true power of Nuclei is writing your own checks. Below is a simple example of a template looking for an exposed `.git/config` file.

```yaml
id: exposed-git-config
info:
  name: Exposed .git/config file
  author: YourName
  severity: medium
  description: The .git/config file was discovered, potentially exposing repository details.
  tags: exposure,config,git
requests:
  - method: GET
    path:
      - "{{BaseURL}}/.git/config"
    matchers-condition: and
    matchers:
      - type: word
        words:
          - "core"
          - "repositoryformatversion"
        condition: and
      - type: status
        status:
          - 200
```
Save this as `git-check.yaml` and run it:
```bash
nuclei -u https://example.com -t git-check.yaml
```

### Rate Limiting and Performance Tuning
When scanning large networks, you must manage your request rate to avoid dropping packets or getting blocked.
- `-c`: Number of concurrent templates to execute.
- `-bs`: Number of concurrent hosts to scan in bulk.
- `-rl`: Maximum number of requests per second.

```bash
nuclei -l massive_list.txt -c 50 -rl 150
```

### Using Workflows
Workflows optimize scanning by executing checks conditionally.
```bash
nuclei -u https://example.com -w workflows/wordpress-workflow.yaml
```

## Advanced Features

### Headless Browser Support
Some vulnerabilities (like DOM-based XSS) require a real browser to execute JavaScript. Nuclei templates can interact with headless Chrome to perform these checks.
```bash
nuclei -u https://example.com -t headless/ -headless
```

### CI/CD Integration
Nuclei is frequently used in DevSecOps. It can output results in JSON format (`-json`) which can be parsed by vulnerability management dashboards or used to break a build if a critical vulnerability is found.
```bash
nuclei -l targets.txt -t cves/ -severity critical -json -o results.json
```

## Security and Ethical Considerations
- Nuclei is an active exploitation tool. While many checks are non-destructive (e.g., checking version numbers), some templates explicitly attempt to exploit RCE or SQLi to confirm the vulnerability.
- Always ensure you have authorization to scan the targets.
- Review community templates before running them on sensitive environments, as they may cause unexpected behavior.

## Chaining Opportunities
- Use `subfinder` or `amass` to gather a massive list of subdomains, pipe the live hosts into `httpx`, and finally pipe those URLs into Nuclei for automated vulnerability scanning at scale.
- Take endpoints discovered by [[08 - Feroxbuster]] and feed them into Nuclei to check for known misconfigurations on those specific paths.
- If Nuclei discovers a specific outdated service (e.g., vulnerable Tomcat server), use [[12 - Metasploit Framework]] to gain a shell.

## Related Notes
- [[08 - Feroxbuster]]
- [[01 - Burp Suite]]
- [[12 - Metasploit Framework]]
