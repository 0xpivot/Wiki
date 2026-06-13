---
tags: [tools, recon, network, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.11 crt.sh Certificate Transparency Query"
---

# crt.sh Certificate Transparency Query

## Introduction to Certificate Transparency (CT)

Certificate Transparency (CT) is an open framework designed to log, audit, and monitor the issuance of TLS/SSL certificates. By requiring Certificate Authorities (CAs) to publicly log every certificate they issue, CT aims to prevent the spoofing of domains and the issuance of rogue certificates. The public nature of these logs, however, introduces a potent vector for passive reconnaissance. 

When a CA issues a certificate for a domain (e.g., `dev.internal.example.com`), that subdomain becomes a matter of public record forever, regardless of whether it actually resolves in DNS or is hosted internally. Threat actors and penetration testers leverage this mechanism to unearth forgotten subdomains, development environments, and hidden organizational assets without sending a single packet to the target's infrastructure.

`crt.sh` is a web interface and database maintained by Sectigo that aggregates and indexes logs from various CT log servers worldwide. It provides a searchable PostgreSQL database and a REST-like API to query domains, organizations, and certificate fingerprints.

## Why Use crt.sh for Reconnaissance?

1. **Absolute Stealth**: Querying CT logs via crt.sh is completely passive. The target organization has no visibility into the fact that you are enumerating their subdomains.
2. **Historical Data**: CT logs are append-only cryptographic ledgers. Certificates issued years ago are still visible, often revealing legacy infrastructure.
3. **Internal Subdomain Leakage**: Organizations frequently issue certificates for internal networks using public CAs (e.g., Let's Encrypt) to avoid deploying internal PKI. These internal hostnames (e.g., `jira.corp.local.target.com`) become publicly listed.
4. **Wildcard Expansion**: While wildcard certificates (e.g., `*.target.com`) hide specific subdomains, you can often find other specific certificates that were issued alongside or before the wildcard certificate was adopted.

## Architecture and Query Flow

The following ASCII diagram illustrates how CT logs are populated and how security practitioners extract data using `crt.sh`.

```text
+----------------+      Issuance       +------------------+
|   Target Org   | ------------------> | Certificate Auth |
| (example.com)  |                     |  (e.g., Sectigo) |
+----------------+                     +------------------+
                                                |
                                                | Logs Cert
                                                v
+----------------+       Aggregates    +------------------+
|    crt.sh      | <------------------ |  CT Log Servers  |
|  (PostgreSQL)  |                     | (Google, Apple)  |
+----------------+                     +------------------+
        ^
        | Queries (Web / API / SQL)
        |
+----------------+
| Pentesters /   |
| Bug Hunters    |
+----------------+
```

## Interfacing with crt.sh

There are three primary ways to interact with `crt.sh`:
1. **Web Interface**: Simple, human-readable, but difficult to automate at scale.
2. **JSON API**: Outputing results in JSON format by appending `&output=json` to the URL.
3. **Direct PostgreSQL Access**: Direct SQL queries to `crt.sh`'s open database, allowing for highly complex filtering and extraction.

### Method 1: The Web Interface
Navigating to `https://crt.sh/?q=example.com` returns an HTML table containing the issuer, certificate identity, and timestamps. Advanced searches can be performed using wildcards like `%.example.com`.

### Method 2: The JSON API (Ideal for Scripting)
For automation pipelines, returning the data in JSON format is preferred.
```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```
**Breakdown of the command:**
- `curl -s`: Fetches the data silently.
- `?q=%25.example.com`: The URL-encoded equivalent of `%.example.com`, searching for all subdomains.
- `&output=json`: Directs crt.sh to format the response as a JSON array.
- `jq -r '.[].name_value'`: Parses the JSON array and extracts the `name_value` field, which contains the domain names.
- `sed 's/\*\.//g'`: Removes wildcard characters (`*.`) from the beginning of domain names, as they are not actionable for direct resolution.
- `sort -u`: Sorts the output alphabetically and removes duplicate entries.

### Method 3: Direct PostgreSQL Queries
`crt.sh` provides public, read-only access to its PostgreSQL database. This is the most powerful method but requires a PostgreSQL client (`psql`).

**Connection String:**
```bash
psql -h crt.sh -p 5432 -U guest -d certwatch
```

**Example Query: Extracting unique subdomains for a domain:**
```sql
SELECT ci.NAME_VALUE
FROM certificate_and_identities ci
WHERE plainto_tsquery('certwatch', 'example.com') @@ identities(ci.CERTIFICATE)
  AND ci.NAME_VALUE LIKE '%.example.com'
  AND ci.NAME_TYPE = 'dNSName'
GROUP BY ci.NAME_VALUE;
```
This SQL query is often much faster than the API for very large domains because it leverages database indexes directly and offloads the sorting/grouping to the database engine.

## Advanced Usage and Considerations

### Handling Rate Limits and Timeouts
Because `crt.sh` is a free, publicly available service heavily used by the security community, it frequently experiences timeouts and `502 Bad Gateway` errors. 

**Mitigation Strategies:**
1. **Implement Retry Logic**: Wrap your `curl` commands in a bash loop that retries upon failure.
2. **Use Alternative CT Monitors**: If `crt.sh` is down, fallback to other services like `certspotter` or `censys`.
3. **Use the Database**: Often, the web application interface crashes under load, but the underlying PostgreSQL database (`psql`) remains responsive.

### Bash Script: Robust crt.sh Subdomain Extractor
The following script demonstrates a robust way to query `crt.sh` with retry mechanisms and wildcard sanitization.

```bash
#!/bin/bash
# crt_enum.sh - Robustly enumerate subdomains from crt.sh

TARGET=$1
if [ -z "$TARGET" ]; then
    echo "Usage: $0 <domain.com>"
    exit 1
fi

MAX_RETRIES=5
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "[*] Querying crt.sh for $TARGET (Attempt $((RETRY_COUNT+1)))"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" "https://crt.sh/?q=%25.$TARGET&output=json")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" -eq 200 ] && [ -n "$BODY" ] && [ "$BODY" != "[]" ]; then
        echo "$BODY" | jq -r '.[].name_value' | sed 's/\*\.//g' | tr '\n' ',' | tr ',' '\n' | sort -u
        SUCCESS=true
        break
    elif [ "$HTTP_CODE" -eq 502 ] || [ "$HTTP_CODE" -eq 503 ]; then
        echo "[-] Server overloaded ($HTTP_CODE). Retrying in 5 seconds..."
        sleep 5
    else
        echo "[-] Unexpected error or no data. HTTP Code: $HTTP_CODE"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$SUCCESS" = false ]; then
    echo "[-] Failed to retrieve data from crt.sh after $MAX_RETRIES attempts."
fi
```

### Parsing Subject Alternative Names (SANs)
A single certificate can be valid for multiple domains, listed under the Subject Alternative Name (SAN) extension. When querying `crt.sh`, it will often return certificates that include your target domain alongside many others. This is particularly useful for finding acquisitions or related domains owned by the same entity.

## Real-World Impact and Findings
During external penetration tests, querying `crt.sh` frequently reveals:
- **Dev/Staging environments**: `api-v2-staging.target.com`, `test-db.target.com`. These environments often lack the strict authentication or WAF protections present in production.
- **VPN / SSO Portals**: `vpn.target.com`, `sso-dev.target.com`.
- **Third-Party Integrations**: Subdomains pointing to SaaS providers (e.g., `target.zendesk.com`), which can be probed for Subdomain Takeover vulnerabilities.

## Limitations of Certificate Transparency
- **Historical Noise**: CT logs cannot tell you if a domain is *currently* active. A certificate from 2017 might point to a domain that was decommissioned years ago. Extensive DNS resolution (`dnsx` or `shuffledns`) is required to filter out inactive hosts.
- **Wildcard Masking**: If a company exclusively issues wildcard certificates (`*.example.com`), CT logs will not reveal any individual subdomains beneath that tier.
- **Intranet CAs**: Certificates issued by internal, private CAs (like Microsoft Active Directory Certificate Services) are not logged to public CT logs unless they cross-sign with a public root.

## Chaining Opportunities
- **Resolution Verification**: Pipe the output of `crt.sh` into `dnsx` or `puredns` to verify which subdomains actually resolve to live IP addresses.
- **Subdomain Takeover**: Pass unresolved subdomains to `nuclei` to check for dangling CNAME records.
- **Port Scanning**: Feed resolved IP addresses into `naabu` or `masscan` to discover open ports on forgotten infrastructure.
- **HTTP Probing**: Feed resolved domains to `httpx` to capture screenshots and web technology fingerprints.

## Related Notes
- [[02 - Passive Subdomain Enumeration]]
- [[12 - dnsx DNS Bulk Resolution and Probing]]
- [[15 - httpx HTTP Probing at Scale]]
- [[06 - Subdomain Takeovers]]
