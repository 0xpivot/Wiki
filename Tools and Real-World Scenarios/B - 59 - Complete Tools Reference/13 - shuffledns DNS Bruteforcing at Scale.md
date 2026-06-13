---
tags: [tools, recon, network, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.13 shuffledns DNS Bruteforcing at Scale"
---

# shuffledns DNS Bruteforcing at Scale

## Introduction to shuffledns

`shuffledns` is an advanced, high-performance wrapper around `MassDNS`, developed by ProjectDiscovery. Written in Go, it is designed specifically for large-scale DNS brute-forcing and mass resolution. While tools like `dnsx` are excellent for general-purpose DNS probing and resolution, `shuffledns` excels when you need to resolve massive wordlists (e.g., 100 million+ lines) against a target domain rapidly.

The primary limitation of standard DNS brute-forcing tools is that they execute queries sequentially or rely on the host OS's networking stack, which severely limits throughput. `MassDNS` solves this by implementing a custom DNS stub resolver in C, capable of millions of packets per second. However, `MassDNS` lacks built-in intelligent wildcard filtering and outputs data in a format that requires heavy parsing.

`shuffledns` bridges this gap. It leverages the raw speed of `MassDNS` engine while adding intelligent wildcard handling, native Go concurrency, and clean integration into modern bug bounty pipelines.

## Why Use shuffledns?

1. **Extreme Performance**: Capable of resolving millions of subdomains in minutes by utilizing `MassDNS` under the hood.
2. **Intelligent Wildcard Handling**: It implements an advanced algorithm to detect wildcard domains and filter out false positives accurately without slowing down the brute-force process.
3. **Smart Resolver Distribution**: It actively shuffles the resolver list for each query, ensuring that rate limits and temporary bans from public DNS servers are avoided.
4. **Pipeline Ready**: Designed to read from standard input (`stdin`) and write clean results to standard output (`stdout`), making it perfect for chaining with other ProjectDiscovery tools.

## Architecture and Execution Pipeline

The following ASCII diagram illustrates the workflow of `shuffledns` and how it orchestrates `MassDNS`.

```text
+-------------------+       +-----------------------------------+
|  Wordlist (.txt)  |       |            shuffledns             |
| (Millions of lines| ----> |                                   |
+-------------------+       |  +-----------------------------+  |
                            |  | 1. Wildcard Baseline Setup  |  |
+-------------------+       |  | (Query random non-existent  |  |
|  Target Domain    | ----> |  |  hosts to map wildcards)    |  |
+-------------------+       |  +-----------------------------+  |
                            |                 |                 |
+-------------------+       |  +-----------------------------+  |
|  Resolver List    | ----> |  | 2. Payload Generation       |  |
| (Thousands of IPs)|       |  | (Append domain to wordlist) |  |
+-------------------+       |  +-----------------------------+  |
                            |                 |                 |
                            |  +-----------------------------+  |
                            |  | 3. MassDNS Invocation       |  |
                            |  | (Execute binary with inputs)|  |
                            |  +-----------------------------+  |
                            |                 |                 |
                            |  +-----------------------------+  |
                            |  | 4. Results Sanitization     |  |
                            |  | (Filter against Wildcards)  |  |
                            |  +-----------------------------+  |
                            +-----------------------------------+
                                              |
                                              v
                            +-----------------------------------+
                            |  Valid, Live Subdomains (stdout)  |
                            +-----------------------------------+
```

## Core Features and Usage

### Prerequisites
Because `shuffledns` is a wrapper, you **must** have the `massdns` binary installed and available in your system's PATH.
```bash
git clone https://github.com/blechschmidt/massdns.git
cd massdns
make
sudo cp bin/massdns /usr/local/bin/
```

### 1. Active Subdomain Bruteforcing
The core use case for `shuffledns` is actively guessing subdomains using a large wordlist.
```bash
shuffledns -d example.com -w subdomains-top1million-110000.txt -r resolvers.txt -o live_subs.txt
```
- `-d`: The target domain you are brute-forcing.
- `-w`: The wordlist containing potential subdomain prefixes (e.g., `dev`, `staging`, `api`).
- `-r`: A list of public DNS resolvers to use for the queries. This is critical for performance and avoiding rate limits.
- `-o`: Output file for the valid subdomains found.

### 2. Mass DNS Resolution (List Verification)
Instead of brute-forcing, you can use `shuffledns` to rapidly verify a massive list of pre-generated or passively gathered subdomains.
```bash
shuffledns -list raw_subdomains.txt -r resolvers.txt -o resolved_subs.txt
```
- `-list`: A file containing a list of full subdomains to resolve (e.g., `dev.example.com`, `test.example.com`).

### 3. Wildcard Filtering
Wildcard DNS records (`*.example.com`) are the bane of brute-forcing. If unhandled, every entry in your 100-million wordlist will return a successful resolution, creating 100 million false positives.

`shuffledns` handles this elegantly out of the box. Before brute-forcing, it generates several random, non-existent subdomains (e.g., `asdfqwer123.example.com`) and queries them. If they resolve, it records the IP addresses returned. During the actual brute-force, any discovered subdomain that resolves to one of those baseline IPs is flagged as a wildcard and filtered out automatically.

You can strictly enforce wildcard filtering by using the `-strict-wildcard` flag, which increases the thoroughness of the baseline checks.

## Advanced Configuration and Tuning

### Building a Robust Resolver List
The performance of `shuffledns` and `MassDNS` is entirely dependent on the quality of your resolver list. Using a small list or default ISP resolvers will result in throttling and dropped queries.

You should maintain a large list of trusted public resolvers (e.g., Google, Cloudflare, Quad9, OpenDNS, Level3). Tools like `puredns` or `dnsvalidator` are often used to generate and sanitize these lists.
```bash
wget https://raw.githubusercontent.com/trickest/resolvers/main/resolvers-trusted.txt -O resolvers.txt
```

### Tuning massdns Parameters
You can pass custom arguments directly to the underlying `MassDNS` engine. This allows you to fine-tune the raw query speed. ProjectDiscovery integrated massdns into `shuffledns` in a way where tuning the thread count and rate limit is done via `shuffledns` flags.

**Concurrency Tuning:**
- `-t`: Number of threads to utilize (default is 5000). For large wordlists and good bandwidth, you can push this higher.
- `-m`: Path to the massdns binary, if it is not in your system's PATH.

Example of high-concurrency execution:
```bash
shuffledns -d target.com -w huge_wordlist.txt -r resolvers.txt -t 10000 -o results.txt
```

### Dealing with Evasion and WAFs
Since DNS operates over UDP port 53 and queries are sent to public resolvers, the target organization rarely sees your actual IP address during a brute-force attack. They only see queries coming from Google (8.8.8.8) or Cloudflare (1.1.1.1). This makes DNS brute-forcing with `shuffledns` extremely stealthy from the target's perspective, though you are making heavy noise across the public DNS infrastructure.

## Real-World Workflow Example

A comprehensive active enumeration strategy:
1. **Passive Recon**: Gather known subdomains using `subfinder` and `crt.sh`.
2. **Permutation/Alteration**: Feed the passive list into `altdns` or `gotator` to generate a list of likely permutations (e.g., `api-dev.target.com`, `api-prod.target.com`).
3. **Mass Resolution**: Feed this massive list of permutations into `shuffledns` for rapid verification.

```bash
# 1. Generate permutations (assuming 'altdns_words.txt' contains alteration words)
gotator -sub passive_subs.txt -perm altdns_words.txt -depth 1 > permutations.txt

# 2. Rapidly resolve millions of permutations and filter wildcards
shuffledns -list permutations.txt -d example.com -r resolvers.txt -strict-wildcard -o final_active_subs.txt
```

## Chaining Opportunities
- **Wordlist Generation**: Use the output of `shuffledns` as seed data to generate further wordlists using `regulator` or `gotator`.
- **Port Discovery**: Pass the validated subdomains into `naabu` to find open services.
- **Web Technology Fingerprinting**: Pipe the output into `httpx` to analyze the web applications running on the discovered subdomains.

## Related Notes
- [[12 - dnsx DNS Bulk Resolution and Probing]]
- [[14 - puredns Fast DNS Resolver]]
- [[02 - Passive Subdomain Enumeration]]
- [[05 - DNS Brute-forcing & Permutations]]
