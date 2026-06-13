---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.08 Feroxbuster"
---

# 41.08 Feroxbuster: Next-Generation Recursive Content Discovery

## Introduction

Content discovery is an essential part of the reconnaissance and enumeration phase of any web application penetration test or bug bounty engagement. The goal is to uncover hidden files, directories, API endpoints, and administrative panels that are not linked or intended to be publicly accessible.

`Feroxbuster` is a fast, simple, recursive content discovery tool written in Rust. It takes the concepts introduced by legacy tools like `DirBuster` and `GoBuster` and supercharges them with modern programming techniques, delivering unparalleled speed and functionality.

### Why Feroxbuster?
- **Speed**: Being written in Rust, it utilizes multithreading and async I/O efficiently, maxing out network connections and reducing enumeration time.
- **Recursion**: Uniquely handles recursion dynamically, identifying new directories and instantly spawning new threads to explore them based on the configuration.
- **Smart Filtering**: Capable of dynamically filtering out wildcard responses and custom error pages (e.g., auto-tuning), saving analysts from analyzing massive false positive files.
- **Portability**: Compiled as a single static binary, making it easy to deploy to jump boxes.

## Architecture and Execution Flow

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Target Server   | <---- | Feroxbuster Engine    | <---- |    Wordlist(s)    |
|   (HTTP/HTTPS)    | ----> | (Rust Async Workers)  | ----> | (SecLists, etc.)  |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +-------------------+
         |                              |
         |  HTTP 200 OK (New Dir)       | Spawns Recursive Thread
         |                              v
         |                  +-----------------------+
         +----------------> | Recursive Engine      |
                            | Depth N+1             |
                            +-----------------------+
```

When Feroxbuster initializes, it loads the specified wordlists into memory or streams them, creating an initial set of tasks. The connection pool manages multiple simultaneous requests. If a request yields a successful directory response (e.g., a 301 Redirect or 200 OK for a directory), Feroxbuster checks its recursion depth rules and automatically spawns a new task to brute-force the newly discovered path.

## Core Concepts and Terminology

1. **Recursion Depth**: The number of directories deep the tool will automatically travel. A depth of 1 means it will only scan the base URL. A depth of 2 means it will scan the base URL, and any directories found within it.
2. **Auto-Calibration**: Servers often return 200 OK for non-existent pages (soft 404s) to provide a helpful user interface. Feroxbuster can auto-calibrate to detect the signature (size, words, lines) of these custom error pages and filter them from the output.
3. **Extensions**: Identifying files often requires appending extensions (e.g., `.php`, `.bak`, `.txt`) to wordlist entries.
4. **Rate Limiting**: Controlling the number of requests per second to prevent overloading the target server or triggering WAF/IPS blocks.

## Installation and Configuration

### Installing on Linux

Feroxbuster can be easily installed via curl:
```bash
curl -sL https://raw.githubusercontent.com/epi052/feroxbuster/main/install-nix.sh | bash
mv feroxbuster /usr/local/bin/
```
Alternatively, via Cargo (Rust package manager):
```bash
cargo install feroxbuster
```

### Configuration File (`ferox-config.toml`)
Feroxbuster supports a configuration file to set global defaults. This is highly recommended for standardizing your testing environment.

```toml
# ferox-config.toml
wordlist = "/opt/SecLists/Discovery/Web-Content/raft-large-directories.txt"
threads = 50
timeout = 10
status_codes = [200, 204, 301, 302, 307, 308, 401, 403, 405]
filter_status = [404]
save_state = true
```

## Detailed Usage and Methodology

### Basic Enumeration
The simplest invocation requires only a target URL.
```bash
feroxbuster -u https://example.com/
```
If no wordlist is provided, Feroxbuster will look for a default wordlist (usually `dirb/common.txt` or similar depending on OS). It is always recommended to specify a robust wordlist:
```bash
feroxbuster -u https://example.com/ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

### Working with Extensions
To find specific file types, use the `-x` flag. This appends the extensions to every word in the wordlist.
```bash
feroxbuster -u https://example.com/ -x php,bak,txt,zip,tar.gz
```
*Tip: Always look for `.bak` or `.old` files, as developers frequently leave these behind during maintenance, potentially exposing source code or configuration secrets.*

### Managing Recursion
Recursion is Feroxbuster's superpower. By default, recursion is enabled.
- `--depth 2`: Limits the recursion to 2 levels deep.
- `--extract-links` (`-e`): Parses HTML responses to extract links and adds them to the scan queue. This turns Feroxbuster into a hybrid spider/brute-forcer.
- `--no-recursion` (`-n`): Disables recursion entirely, useful for a quick surface scan.

```bash
feroxbuster -u https://example.com/ -e --depth 3
```

### Filtering and Tuning
Web application firewalls and edge networks (like Cloudflare) often introduce anomalies. Filtering is crucial to maintain signal-to-noise ratio.
- **Filter by Status Code**: `-S 403,401` or `--filter-status`
- **Filter by Size**: `-S 0` (ignores empty responses)
- **Filter by Word/Line Count**: `-W` and `-N` flags.
- **Auto-tune**: `--auto-tune` automatically attempts to filter out wildcard responses.

```bash
feroxbuster -u https://example.com/ --auto-tune -S 403,404,500
```

### Authentication and Headers
When testing authenticated areas of an application or APIs requiring specific headers (like `Authorization: Bearer ...`), Feroxbuster allows custom headers.
```bash
feroxbuster -u https://api.example.com/v1/ -H "Authorization: Bearer eyJhbG..." -H "X-Custom-Header: Testing"
```

### Resuming Scans
Feroxbuster automatically saves its state if it is interrupted (Ctrl+C). This is incredibly valuable during long-running engagements or over unstable VPN connections.
To resume:
```bash
feroxbuster --resume-from ferox-https_example_com-1620000000.state
```

## Advanced Techniques

### Integrating with Burp Suite
To capture all discovered endpoints within your proxy for further active testing, route Feroxbuster's traffic through Burp Suite.
```bash
feroxbuster -u https://example.com/ --proxy http://127.0.0.1:8080 -k
```
*Note: The `-k` flag disables TLS certificate validation, which is necessary when proxying HTTPS traffic through Burp.*

### Bypassing WAFs via Rate Limiting and Randomization
If a WAF is blocking your requests due to high volume or predictable User-Agents, adjust the tool's behavior:
- `--rate-limit`: Limit requests per second.
- `--random-agent`: Use a random User-Agent for each request.
- `--time-limit`: Set a maximum runtime.

```bash
feroxbuster -u https://example.com/ --rate-limit 10 --random-agent --depth 1
```

### Analyzing the Output
Feroxbuster can output results in various formats (JSON, CSV). JSON output is highly recommended for integration with other automation pipelines.
```bash
feroxbuster -u https://example.com/ --json -o results.json
```
You can then pipe this JSON into `jq` for parsing and extraction of just the URLs for tools like `nuclei` or `ffuf`.

## Operational Security and Considerations
- Always ensure you have explicit permission to run automated discovery tools against a target.
- Monitor your connection state. If your VPN drops, Feroxbuster might start scanning your local ISP or fail open depending on routing.
- High thread counts against fragile infrastructure can cause Denial of Service (DoS) conditions. Always start slow and scale up.

## Chaining Opportunities
- Take discovered URLs and pass them to [[11 - Nuclei]] for vulnerability scanning.
- Discovered login pages can be targeted using [[13 - Hydra]] or [[01 - Burp Suite]] Intruder.
- Uncovered API endpoints can be fuzzed using `ffuf` or tested for broken authorization.
- Directories with directory listing enabled can be downloaded recursively via `wget`.

## Related Notes
- [[09 - sqlmap]]
- [[10 - Nikto]]
- [[11 - Nuclei]]
- [[12 - Metasploit Framework]]
