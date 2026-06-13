---
tags: [tools, recon, vapt, assetfinder, tomnomnom]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.03 Assetfinder Lightweight Subdomain Discovery"
---

# Assetfinder: Lightweight Subdomain Discovery

Assetfinder, created by the highly respected security researcher Tomnomnom, is a testament to the Unix philosophy: *do one thing, and do it well.* Where tools like Amass are monolithic beasts capable of graph theory analysis and Subfinder is a highly configurable framework requiring API key management, Assetfinder is designed to be purely frictionless.

It is a lightweight, compiled Go binary that requires absolutely zero configuration, zero API keys, and executes in seconds. For quick recon, CI/CD pipeline integration, or on-the-fly terminal hacking, Assetfinder is indispensable.

## Core Philosophy and Architecture

Assetfinder is purposefully minimal. It queries a curated, hardcoded list of highly reliable, public, and free OSINT sources. It does not attempt to brute-force DNS, it does not do permutations, and it does not maintain a database.

```ascii
+-----------------------------------------------------------------------------+
|                            ASSETFINDER ARCHITECTURE                         |
+-----------------------------------------------------------------------------+
|                                                                             |
|                       +----------------------+                              |
|                       |  Target Domain       |                              |
|                       |  (e.g., tesla.com)   |                              |
|                       +----------+-----------+                              |
|                                  |                                          |
|            +---------------------+-----------------------+                  |
|            |                     |                       |                  |
|   +--------v--------+   +--------v---------+   +---------v--------+         |
|   |   crt.sh        |   |   Certspotter    |   |   Hackertarget   |         |
|   | (Certificates)  |   | (Certificates)   |   | (Passive DNS)    |         |
|   +--------+--------+   +--------+---------+   +---------+--------+         |
|            |                     |                       |                  |
|            +---------------------+-----------------------+                  |
|                                  |                                          |
|            +---------------------+-----------------------+                  |
|            |                     |                       |                  |
|   +--------v--------+   +--------v---------+   +---------v--------+         |
|   |   Threatcrowd   |   |   Wayback Mach   |   |   FindSubDomains |         |
|   | (Threat Intel)  |   | (Archival)       |   |   (Scraping)     |         |
|   +--------+--------+   +--------+---------+   +---------+--------+         |
|            |                     |                       |                  |
|            +---------------------+-----------------------+                  |
|                                  |                                          |
|                       +----------v-----------+                              |
|                       |   Deduplication      |                              |
|                       |   (In-Memory)        |                              |
|                       +----------+-----------+                              |
|                                  |                                          |
|                       +----------v-----------+                              |
|                       |   Standard Output    |                              |
|                       |   (stdout)           |                              |
|                       +----------------------+                              |
|                                                                             |
+-----------------------------------------------------------------------------+
```

Because it uses `goroutines` to query all these sources simultaneously, execution time is bound only by the network latency of the slowest source (typically under 5-10 seconds total).

## Installation and Setup

Like most of Tomnomnom's tools, Assetfinder is written in Go. You can compile it directly from source if you have Go installed:

```bash
go install github.com/tomnomnom/assetfinder@latest
```
Make sure your `~/go/bin` directory is in your `$PATH`.

## Core Usage and Flags

Assetfinder is so minimal that it barely has flags. You provide the domain, and it provides the assets.

### Basic Discovery
```bash
assetfinder example.com
```
By default, this command will output any domain associated with `example.com`. This includes subdomains (`dev.example.com`), but it *also* includes related domains that might share the same root name (e.g., `example.org`, `example-corp.com`) if it finds them in certificate Subject Alternative Names (SANs).

### Subdomains-Only Flag (`-subs-only`)
In strict bug bounty scopes, you are often only authorized to test `*.example.com`. To ensure Assetfinder does not output out-of-scope related domains, use the `-subs-only` flag.

```bash
assetfinder -subs-only example.com
```
*This is the most common and safest way to run Assetfinder during a formal engagement.*

## Why use Assetfinder over Amass/Subfinder?

Given that Amass and Subfinder find more subdomains, why use Assetfinder?

1. **Frictionless Portability:** If you drop onto a compromised Linux jumpbox during a Red Team engagement, you can download the Assetfinder binary via `curl` and run it instantly. No dependencies, no `config.ini` to set up, no API keys to migrate.
2. **Speed in Micro-Workflows:** When investigating a single obscure domain dynamically in the terminal, waiting 5 minutes for Amass to spin up its graph engine is overkill. Assetfinder gives you the immediate 80% result in 3 seconds.
3. **Piping Purity:** Assetfinder outputs *only* the domain names. It doesn't output banners, version numbers, or status updates. It acts identically to a standard Unix utility (like `cat` or `grep`), making it perfect for shell scripting.

## Scripting and Bash Pipelining

Assetfinder’s true power unlocks when combined with other Unix utilities and recon tools.

### 1. The Immediate Live-Host Pipeline
Find subdomains and immediately probe them for HTTP services using `httprobe` (another Tomnomnom tool).
```bash
assetfinder -subs-only example.com | httprobe
```
*Result: A clean list of `http://` and `https://` URLs that are actively responding.*

### 2. Filtering In-Scope Targets with `grep`
If your scope is strictly `*.dev.example.com`, you can filter the output on the fly.
```bash
assetfinder -subs-only example.com | grep '\.dev\.example\.com$'
```

### 3. Building a Bash Micro-Recon Wrapper
You can create a quick bash alias or function in your `.bashrc` or `.zshrc` to automate initial domain profiling.

```bash
# Add this to your ~/.bashrc
quickrecon() {
    mkdir -p $1_recon
    echo "[+] Running Assetfinder on $1"
    assetfinder -subs-only $1 > $1_recon/domains.txt
    echo "[+] Resolving live hosts"
    cat $1_recon/domains.txt | fping -c 1 -q 2> /dev/null | awk '{print $1}' > $1_recon/live_domains.txt
    echo "[+] Probing for HTTP servers"
    cat $1_recon/live_domains.txt | httpx -silent > $1_recon/web_servers.txt
    echo "[+] Recon complete for $1. Results in $1_recon/"
}
```
Now, simply typing `quickrecon tesla.com` will perform an end-to-end passive recon and active probing pipeline in seconds.

## Limitations and Edge Cases

- **Blind Spots:** Because Assetfinder relies purely on a small list of free APIs, it will miss subdomains that exist solely in closed datasets (like Shodan's premium tiers) or internal network brute-forcing.
- **Defunct Endpoints:** Passive scraping pulls historical data. A subdomain found in a 2-year-old certificate via `crt.sh` might point to an IP address that the company no longer owns, leading to potential subdomain takeover scenarios, or simply wasted time during active probing. Always resolve the results.
- **Rate Limiting Resilience:** While Assetfinder doesn't need API keys, the public services it hits (like `crt.sh`) are frequently overloaded or rate-limit aggressive IPs. If `crt.sh` is down, Assetfinder will simply skip it and return fewer results, often without producing a loud error.

## Chaining Opportunities

- **Assetfinder -> httprobe -> meg**: A classic Tomnomnom pipeline. Find subdomains, probe for HTTP, and use `meg` to fetch the root path `/` of every host concurrently to search for interesting titles or exposed `.git` directories.
- **Assetfinder -> fff (Fairly Fast Fetcher)**: Use `fff` to rapidly request headers from all discovered subdomains to build a local cache for offline inspection.
- **Assetfinder -> gau (GetAllUrls)**: Pass the discovered domains to `gau` to fetch every known URL for those subdomains from the Wayback Machine.

## Related Notes
- [[01 - Amass Full Config and Usage]]
- [[02 - Subfinder Config Sources API Keys]]
- [[04 - theHarvester Full Usage Guide]]
- [[05 - Recon-ng Modular OSINT Framework]]
- [[06 - DNS Resolution and Brute Forcing]]
