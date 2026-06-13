---
tags: [vapt, methodology, web-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - Web"
topic: "Master Guide - Web VAPT 01"
---

# Web VAPT 01 - Recon and Attack Surface Mapping Methodology

## 🗣️ Interview Strategy: How to Explain Reconnaissance
When asked about your reconnaissance methodology in a senior or expert VAPT interview, **do not just list tools**. Amateurs list tools; experts explain the *funnel methodology* and *data correlation*.

**Your Script:**
> *"I approach reconnaissance as a funnel. I start wide with Horizontal Recon to map the organization's total asset footprint—acquisitions, ASNs, and reverse WHOIS. Then I move to Vertical Recon on specific domains, using a hybrid of passive data sources and active brute-forcing, augmented with permutation lists. I don't just dump subdomains; I resolve them, fingerprint the tech stack, parse JavaScript for hidden endpoints, and actively hunt for cloud misconfigurations. The goal isn't just to find subdomains; it's to find the forgotten 'dev' or 'staging' server that lacks the WAF rules of the production environment."*

---

## 🛠️ Step 1: Horizontal Reconnaissance (The Wide Net)
Horizontal recon maps out the target organization's entire digital footprint, including subsidiaries, acquisitions, and related brands.

### 1.1 ASN Enumeration and CIDR Mapping
Find the IP space owned by the target.
*   **Tools:** `amass`, `bgp.he.net`, `whois`, `metabigor`
*   **Command:**
    ```bash
    # Using Amass to find ASNs and related netblocks
    amass intel -org "Target Company"
    
    # Resolving ASN to CIDR ranges
    whois -h whois.radb.net -- '-i origin AS12345' | grep -Eo "([0-9.]+){4}/[0-9]+"
    ```
*   **Interview Talking Point:** "I always map the ASN first. If I only focus on the main domain, I'll miss legacy infrastructure hosted on their own IP space."

### 1.2 Reverse WHOIS & Acquisitions
Find other domains registered by the same entity.
*   **Tools:** `whoxy`, `crunchbase` (for acquisitions)
*   **Command:**
    ```bash
    # DOMAIN is target.com
    # Extract registrant email, then reverse lookup
    amass intel -d target.com -whois
    ```

---

## 🛠️ Step 2: Vertical Reconnaissance (Subdomain Enumeration)
This is where you dig deep into a specific domain to find all subdomains. 

### 2.1 Passive Enumeration
Gathering subdomains without touching the target's infrastructure.
*   **Sources:** Certificate Transparency (crt.sh), VirusTotal, Shodan, Censys, WayBackMachine.
*   **Tools:** `subfinder`, `amass`, `assetfinder`, `github-subdomains`
*   **Command Flow:**
    ```bash
    subfinder -d target.com -all -recursive -o passive_subs.txt
    amass enum -passive -d target.com -o amass_passive.txt
    cat passive_subs.txt amass_passive.txt | sort -u > all_passive_subs.txt
    ```

### 2.2 Active Enumeration (Brute-Forcing & DNS Resolution)
Resolving passive results and brute-forcing new ones using custom wordlists.
*   **Tools:** `puredns`, `shuffledns`, `massdns`
*   **Command Flow:**
    ```bash
    # Brute-force using a massive wordlist
    puredns bruteforce SecLists/Discovery/DNS/dns-Jhaddix.txt target.com -r resolvers.txt -w active_subs.txt
    
    # Resolve all gathered passive subdomains
    puredns resolve all_passive_subs.txt -r resolvers.txt -w resolved_subs.txt
    ```

### 2.3 Permutations and Alterations
Generating new subdomain guesses based on the ones you already found (e.g., `dev-app` -> `staging-app`).
*   **Tools:** `dnsx`, `altdns`, `gotator`
*   **Command Flow:**
    ```bash
    gotator -sub resolved_subs.txt -perm permutations_list.txt -depth 1 -mindup -md | dnsx -r resolvers.txt -o final_subs.txt
    ```
*   **Interview Talking Point:** "Permutations are where I find the best bugs. A company might secure `api.target.com`, but completely forget about `api-v2-dev.target.com` which I generate using `gotator`."

---

## 🛠️ Step 3: Infrastructure Discovery & Port Scanning
Now that we have live subdomains, we need to see what's running on them.

### 3.1 Fast Port Scanning
*   **Tools:** `naabu`, `masscan`, `nmap`
*   **Command Flow:**
    ```bash
    # Use Naabu for fast, reliable port scanning of all subdomains
    naabu -l final_subs.txt -p - -c 50 -nmap-cli 'nmap -sV -sC -oA nmap_scan'
    ```

### 3.2 WAF Detection
*   **Tools:** `wafw00f`, `nuclei`
*   **Command:**
    ```bash
    wafw00f -i live_hosts.txt
    ```

---

## 🛠️ Step 4: Visual Recon & Technology Fingerprinting
Taking screenshots of all web services and identifying the technology stack.

### 4.1 Visual Recon
*   **Tools:** `httpx`, `aquatone`, `eyewitness`
*   **Command Flow:**
    ```bash
    # Probe for live HTTP/HTTPS servers and snapshot
    cat final_subs.txt | httpx -ports 80,443,8080,8443 -threads 200 -screenshot -title -tech-detect -status-code -o httpx_live.txt
    ```

### 4.2 Technology Fingerprinting
*   **Tools:** `wappalyzer`, `whatweb`, `retire.js`
*   **Interview Talking Point:** "I use `httpx` with `-tech-detect` to find outdated frameworks. If I see a specific version of Apache Struts or an old Spring Boot instance, I immediately pivot to CVE hunting."

---

## 🛠️ Step 5: Content, Directory, & Parameter Discovery
Finding hidden endpoints, directories, and parameters.

### 5.1 Directory Brute-Forcing
*   **Tools:** `ffuf`, `feroxbuster`, `dirsearch`
*   **Command Flow:**
    ```bash
    feroxbuster -u https://api.target.com -w SecLists/Discovery/Web-Content/raft-large-directories.txt -t 50 -d 2 -o ferox_results.txt
    ```
*   **Pro-Tip:** Always brute-force with extensions specific to the tech stack (e.g., `.php`, `.jsp`, `.aspx`, `.json`).

### 5.2 JavaScript Parsing & Endpoint Extraction
*   **Tools:** `linkfinder`, `xnLinkFinder`, `subjs`
*   **Command:**
    ```bash
    echo "https://target.com" | subjs | xargs -I % python3 linkfinder.py -i % -o cli
    ```

### 5.3 Hidden Parameter Discovery
*   **Tools:** `arjun`, `x8`
*   **Command:**
    ```bash
    arjun -u https://target.com/endpoint -w custom_params.txt -m GET,POST
    ```
*   **Interview Talking Point:** "When I hit a 403 Forbidden on an endpoint, I use Arjun or x8 to brute-force parameters. Finding hidden `?admin=true` or `?debug=1` parameters often completely bypasses authorization controls."

---

## 🛠️ Step 6: Cloud Recon & Secrets Gathering
Many modern applications rely on cloud storage and Git repositories.

### 6.1 S3 Bucket Enumeration
*   **Tools:** `cloud_enum`, `s3scanner`
*   **Command:**
    ```bash
    cloud_enum -k target -m cloud_enum_results.txt
    ```

### 6.2 GitHub Recon
*   **Tools:** `trufflehog`, `gitleaks`, `gitrob`
*   **Interview Talking Point:** "I automate GitHub dorking using the company's domain and internal product names to look for leaked developer credentials, AWS keys, or hardcoded API tokens."

---

## 📊 ASCII Diagram: The Reconnaissance Funnel

```text
    [ ASNs, CIDRs, Reverse WHOIS ]   <-- Horizontal Recon (Broad)
      \                        /
       \  [ Passive Subs ]    /      <-- crt.sh, Shodan, WayBack
        \                    /
         \ [ Active Subs ]  /        <-- Brute-force, Permutations (puredns, gotator)
          \                /
           \  [ httpx ]   /          <-- Live Hosts, Tech Stack, Screenshots
            \            /
             \[ ffuf ]  /            <-- Endpoints, Directories, APIs
              \        /
               \      /              <-- Parameter Discovery (Arjun), JS Parsing
                \    /
                 \  /
               [ VULN ]              <-- High-Value Target Surface
```

---

## 💥 Real-World Attack Scenario: From Recon to Full Account Takeover (ATO)

**Scenario Context:**
During an engagement for a fintech client, the primary domain `app.fintech.com` was heavily fortified behind Cloudflare and an aggressive WAF.

**The Attack Execution:**
1.  **Permutation Recon:** Executed `gotator` on their known subdomains. Discovered `stg-api-internal.fintech.com`.
2.  **DNS Resolution:** The staging API resolved to an AWS Elastic IP outside of the Cloudflare WAF protection.
3.  **Directory Brute-forcing:** Ran `feroxbuster` against the staging API and discovered an undocumented `/v1/swagger.json` file.
4.  **Parameter Discovery:** Parsed the Swagger file and found a forgotten `/v1/users/updateEmail` endpoint that did not require the current password or CSRF tokens.
5.  **Exploitation:** Crafted a POST request to the staging endpoint, changing the admin's email address to the attacker's email, enabling a password reset on the production environment (since staging and prod shared the same backend database).
6.  **Impact:** Full Account Takeover of the Administrator account.

**Interview Lesson:** "This scenario highlights why WAFs are not a silver bullet and why exhaustive permutation and directory discovery are critical. The vulnerability wasn't a zero-day; it was an orphaned endpoint on a forgotten subdomain."

---

## 🔗 Chaining Opportunities

1.  **Exposed `.git` Directory (Recon) -> Source Code Download -> Static Analysis -> RCE:** Finding a `/.git/` folder via `ffuf` allows you to dump the repository using `git-dumper`. Analyzing the source code can reveal hardcoded secret keys or RCE vulnerabilities.
2.  **Subdomain Takeover (Recon) -> Cookie Stealing (Session Hijacking):** Finding a dangling CNAME pointing to an unclaimed S3 bucket allows for Subdomain Takeover. If the main application issues cookies with `.target.com` (wildcard scope), the attacker can steal authentication cookies from users visiting the taken-over subdomain.
3.  **JS Source Map (Recon) -> API Key Leakage -> SSRF / Data Exfiltration:** Extracting `.js.map` files using recon tools allows reconstruction of unminified frontend code, often revealing hidden AWS Cognito credentials or third-party API keys.

---

## 📚 Related Notes
*   [[Web VAPT 02 - Exploiting Authentication and Session Management]]
*   [[Web VAPT 03 - Deep Dive into Injection Exploits SQLi XXE Command]]
*   [[Infrastructure VAPT 01 - External Network Penetration Testing]]
*   [[Cloud Security 01 - AWS Misconfigurations and IAM Privilege Escalation]]
