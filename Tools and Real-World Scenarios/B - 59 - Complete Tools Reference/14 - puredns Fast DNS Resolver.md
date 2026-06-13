---
tags: [tools, recon, network, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.14 puredns Fast DNS Resolver"
---

# puredns Fast DNS Resolver

## Introduction to puredns

`puredns` is a wildly fast, reliable, and highly tuned DNS brute-forcing and mass-resolution tool developed by d3mondev. Similar to `shuffledns`, it acts as a modern Go-based wrapper around the incredibly powerful `MassDNS` engine. 

While both `shuffledns` and `puredns` aim to solve the same problem—executing millions of DNS queries as fast as possible—`puredns` differentiates itself through its **meticulous focus on accuracy, resolver sanitization, and complex wildcard filtering.** 

Public DNS resolvers (the lists of thousands of IP addresses you feed into these tools) are notoriously unreliable. Many are "poisoned" (intentionally returning false IP addresses for advertising or censorship), many drop packets under load, and others simply timeout. `puredns` solves this by aggressively sanitizing your resolver list *before* beginning the actual brute-force attack, ensuring that the results you get are mathematically accurate and entirely free of false positives.

## Why Use puredns over Others?

1. **Resolver Sanitization**: `puredns` tests thousands of public resolvers against known good and bad domains, silently dropping the "poisoned" or slow ones. This ensures high-fidelity results.
2. **Multi-Stage Wildcard Filtering**: It uses a highly complex algorithm to detect wildcards, going beyond simple A-record baseline checks. It accounts for wildcard CNAMEs and complex routing behaviors.
3. **Speed**: By sanitizing the resolver list, the `MassDNS` engine wastes zero time waiting on dead servers, resulting in significantly faster overall execution times compared to raw `MassDNS` usage.
4. **Accuracy Verification**: After `MassDNS` completes the brute-force, `puredns` takes the raw output and performs a secondary validation pass using known-good, highly trusted resolvers (like Google or Cloudflare) to guarantee the domain actually exists.

## Architecture and Execution Pipeline

The following ASCII diagram illustrates the multi-stage pipeline that `puredns` uses to guarantee accuracy at scale.

```text
+-------------------+       +---------------------------------------+
| Raw Public        |       |               puredns                 |
| Resolver List     | ----> |                                       |
+-------------------+       |  +---------------------------------+  |
                            |  | STAGE 1: Resolver Sanitization  |  |
                            |  | (Test resolvers against known   |  |
                            |  |  good/bad domains. Drop bad IPs)|  |
                            |  +---------------------------------+  |
                                                |
+-------------------+                           v (Clean Resolvers)
|  Wordlist /       |                   +---------------+           |
|  Permutations     | ----------------> |  STAGE 2:     |           |
+-------------------+                   |  Bruteforce   |           |
                                        |  (MassDNS)    |           |
+-------------------+                   +---------------+           |
|  Target Domain    | ---------------->         |                   |
+-------------------+                           v (Raw Results)     |
                                       +-----------------+          |
                                       | STAGE 3:        |          |
                                       | Wildcard Filter |          |
                                       | (Algorithmic)   |          |
                                       +-----------------+          |
                                                |                   |
                                                v (Filtered Results)|
                                       +-----------------+          |
                                       | STAGE 4:        |          |
                                       | Validation Pass |          |
                                       | (Verify via     |          |
                                       | trusted DNS)    |          |
                                       +-----------------+          |
                                                |                   |
                                                v                   |
                                +-------------------------------+   |
                                | Final Accurate Subdomains     |   |
                                +-------------------------------+   |
```

## Core Features and Usage

### Prerequisites
Like `shuffledns`, `puredns` requires the `massdns` binary to be present in your system's PATH.

### 1. Active Subdomain Bruteforcing
The syntax for brute-forcing is straightforward. `puredns` requires a list of public resolvers to function correctly.
```bash
puredns bruteforce wordlist.txt example.com -r public-resolvers.txt -w output.txt
```
- `bruteforce`: The mode of operation.
- `wordlist.txt`: The dictionary of subdomain prefixes.
- `example.com`: The target root domain.
- `-r`: A list of public, untested resolvers. `puredns` will sanitize this list automatically before starting.
- `-w`: Write the valid subdomains to this file.

### 2. Mass Resolution (Resolving existing lists)
If you already possess a list of millions of subdomains (e.g., from passive enumeration or permutation generation), you can verify which ones are active.
```bash
puredns resolve subdomains_list.txt -r public-resolvers.txt -w active_subdomains.txt
```
This mode is extremely efficient. It will sanitize the resolvers, blast the list through `MassDNS`, filter for wildcards, and validate the results.

### 3. Dedicated Resolver Sanitization
While `puredns` sanitizes resolvers automatically during execution, you can run a dedicated command to clean a massive list of resolvers and save the good ones for use in other tools (like `dnsx` or `shuffledns`).
```bash
wget https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt
puredns public -r resolvers.txt -w clean_resolvers.txt
```
This command will test every IP in `resolvers.txt`. The resulting `clean_resolvers.txt` will be highly reliable and fast.

## Advanced Configuration and Tuning

### Bypassing Validation for Speed
By default, `puredns` performs a final validation pass on all discovered subdomains using trusted resolvers (8.8.8.8, 1.1.1.1). If you are scanning millions of domains and do not care about a small percentage of false positives, you can disable this validation to save time.
```bash
puredns resolve raw_subs.txt -r resolvers.txt --skip-validation -w fast_results.txt
```

### Rate Limiting and Concurrency
You can dictate how hard `puredns` pushes the network.
- `-l`: Rate limit in queries per second (e.g., `-l 10000`). This is crucial if running from a VPS with bandwidth caps or strict provider policies (like DigitalOcean).
- `--wildcard-batch`: Adjusts how many wildcards are processed in a single batch, useful for domains with massive, complex wildcard structures.

Example of a safe, rate-limited run:
```bash
puredns bruteforce dict.txt target.com -r resolvers.txt -l 5000 -w safe_results.txt
```

### Handling Complex Wildcards
Some targets utilize multi-level wildcards (e.g., `*.dev.target.com` and `*.staging.target.com`). `puredns` uses a highly sophisticated filtering algorithm to isolate these. It maps out the logical structure of the target's DNS zone and dynamically generates baselines for each level of the subdomain tree. This is where `puredns` dramatically outshines almost all other tools.

## Real-World Workflow Example

A professional asset discovery workflow utilizing the strengths of `puredns`:

1. **Gather Public Resolvers**: Download a fresh list of global DNS resolvers.
2. **Gather Passive Data**: Run `amass`, `subfinder`, and `crt.sh`.
3. **Generate Permutations**: Use `gotator` to create a massive list of potential subdomains based on the passive data.
4. **Resolve and Sanitize**: Feed the multi-million line permutation list into `puredns`.

```bash
# Combine passive sources
cat subfinder.txt crt.txt | sort -u > passive.txt

# Generate permutations (assuming 10 million+ lines generated)
gotator -sub passive.txt -perm permutations.txt -depth 1 -mindup 2 > massive_list.txt

# Resolve accurately with puredns
puredns resolve massive_list.txt -r global_resolvers.txt -w final_live_assets.txt
```

## Chaining Opportunities
- **Resolver Generation**: Use `puredns public` to generate a master list of clean resolvers, and feed that file to `dnsx` or `nuclei`.
- **Continuous Monitoring**: Integrate `puredns resolve` into cron jobs to monitor when passively gathered subdomains come online or go offline over time.
- **Web Probing**: Pass the validated, highly accurate output list directly to `httpx`.

## Related Notes
- [[13 - shuffledns DNS Bruteforcing at Scale]]
- [[12 - dnsx DNS Bulk Resolution and Probing]]
- [[05 - DNS Brute-forcing & Permutations]]
- [[15 - httpx HTTP Probing at Scale]]
