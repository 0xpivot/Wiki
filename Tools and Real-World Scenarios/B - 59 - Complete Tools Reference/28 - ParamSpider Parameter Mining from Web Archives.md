---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.28 ParamSpider Parameter Mining"
---

# ParamSpider: Passive Parameter Mining from Web Archives

## 1. Introduction and Core Concepts
Unlike Arjun or x8, which actively send payloads to a target server to discover hidden parameters, ParamSpider is a purely passive reconnaissance tool. It operates by querying vast internet archives—specifically the Wayback Machine (Internet Archive), Common Crawl, and AlienVault's Open Threat Exchange (OTX)—to retrieve historical URLs associated with a target domain.

Because web applications evolve, developers frequently deprecate endpoints or parameters but fail to remove the backend code handling them. ParamSpider extracts URLs containing query string parameters (`?id=1`, `?page=about`) from years of historical data. This approach generates zero traffic to the target infrastructure, making it completely invisible to Web Application Firewalls (WAFs) and Intrusion Detection Systems (IDS).

## 2. How the Tool Works (Internal Mechanics)
ParamSpider essentially acts as an API wrapper and filtering engine for major web archive datasets. It queries these datasets for a specific domain, retrieves all known URLs, and then applies a series of regex-based filters. It explicitly filters out "junk" extensions (like `.jpg`, `.png`, `.css`, `.js`) unless they contain parameters, and normalizes the output. 

A unique feature of ParamSpider is its ability to automatically insert a placeholder payload (like `FUZZ`) into the parameter values, instantly preparing the output for tools like Ffuf, SQLMap, or Nuclei.

### ASCII Diagram: ParamSpider Architecture

```text
[ Target Domain: target.com ]
          |
          v
+---------------------------------------------------+
| ParamSpider Core Engine                           |
|                                                   |
|  +----------------+ +---------------+ +--------+  |
|  | Wayback Machine| | Common Crawl  | | OTX    |  |
|  | API Query      | | API Query     | | API    |  |
|  +----------------+ +---------------+ +--------+  |
+---------------------------------------------------+
          |
          v
[ Raw URL Dataset: 50,000 URLs ]
          |
          v
+---------------------------------------------------+
| Filtering & Normalization Layer                   |
| 1. Discard static assets (.jpg, .woff, etc.)      |
| 2. Extract URLs containing '?' or '&'             |
| 3. Deduplicate exact parameter signatures         |
| 4. Replace values with customizable payload       |
+---------------------------------------------------+
          |
          v
[ Final Output: https://target.com/page?id=FUZZ ]
```

## 3. Installation & Setup
ParamSpider is written in Python 3 and is exceptionally easy to set up. It requires minimal external dependencies.

```bash
# Clone the repository
git clone https://github.com/devanshbatham/ParamSpider
cd ParamSpider

# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 paramspider.py --help
```

*Note: It is highly recommended to run ParamSpider on a VPS or a machine with a fast internet connection, as querying the Wayback Machine for large domains (like `yahoo.com`) can return gigabytes of raw JSON data.*

## 4. Basic Usage & Common Flags
The most fundamental operation is passing a single domain to ParamSpider.

```bash
# Basic domain scan
python3 paramspider.py -d example.com

# Scan a specific subdomain only
python3 paramspider.py -s test.example.com
```

### Core CLI Flags:
- `-d, --domain`: Target domain name.
- `-s, --sub`: Target subdomain (strict match).
- `-l, --level`: Depth of subdomain scanning.
- `-e, --exclude`: Comma-separated list of extensions to exclude (Default: jpg, jpeg, png, etc.).
- `-o, --output`: Name of the output file.
- `-p, --placeholder`: String to replace parameter values (Default: `FUZZ`).
- `-q, --quiet`: Suppress banner and standard output, printing only URLs.

## 5. Advanced Configuration & Tuning

### 5.1 Custom Placeholders for Chaining
By default, ParamSpider replaces values with `FUZZ`. This is perfect for `ffuf`. However, if you intend to feed the list directly into a vulnerability scanner like SQLMap, you might want to leave the original values intact or use a different placeholder.

```bash
# Keep original values
python3 paramspider.py -d example.com -p ""

# Prepare for custom XSS payload testing
python3 paramspider.py -d example.com -p "';alert(1)//"
```

### 5.2 Handling Massive Domains
When scanning mega-corporations (e.g., `tesla.com` or `microsoft.com`), the default exclusions might not be enough. You might encounter thousands of `.pdf` or `.docx` files that happen to have parameters (e.g., `download.php?file=manual.pdf`). You can heavily customize exclusions to keep the dataset clean.

```bash
python3 paramspider.py -d example.com -e pdf,docx,xlsx,csv,xml,json -o clean_params.txt
```

### 5.3 Working Through Proxies
If you are querying from an IP that the Wayback Machine has rate-limited, you can route ParamSpider traffic through a proxy.

```bash
export HTTP_PROXY="http://127.0.0.1:8080"
export HTTPS_PROXY="http://127.0.0.1:8080"
python3 paramspider.py -d example.com
```

## 6. Output Formats & Parsing
The output of ParamSpider is written to a text file in the `output/` directory by default. 

Sample Output File (`output/example.com.txt`):
```text
https://example.com/login?redirect=FUZZ
https://example.com/api/v1/user?id=FUZZ&token=FUZZ
https://blog.example.com/search?q=FUZZ
```

### 6.1 Parsing with Grep and Sed
Sometimes you only care about specific parameters that are highly indicative of vulnerabilities. For example, finding potential SSRF candidates:

```bash
grep -E 'url=|path=|redirect=|dest=|window=|next=' output/example.com.txt > ssrf_candidates.txt
```

Or extracting LFI candidates:
```bash
grep -E 'file=|page=|doc=|folder=|dir=' output/example.com.txt > lfi_candidates.txt
```

## 7. Real-world Scenarios
### 7.1 Exploiting Forgotten Endpoints
Consider a scenario where an organization migrated their API from `/v1/` to `/v2/`. The modern web app no longer references `/v1/`, so an active spider (like Burp Suite) won't find it. 

ParamSpider queries the Wayback Machine from 2018 and discovers:
`https://api.target.com/v1/admin_export?format=csv&user_id=102`

Because the `/v1/` backend was never decommissioned, you can access this hidden endpoint. Changing `user_id` to another value might instantly yield an Insecure Direct Object Reference (IDOR) or BOLA vulnerability.

### 7.2 Discovering Staging and UAT Environments
Developers often test new features on production subdomains that are temporarily public. These get crawled by indexing engines. ParamSpider frequently unearths URLs like:
`https://target.com/test_feature_xyz?debug=true`
Long after the developer removes the link from the UI, the parameter and endpoint remain perfectly viable.

## 8. Chaining Opportunities
ParamSpider is the ultimate "top-of-the-funnel" tool. It is designed explicitly to feed data into active scanners.

1. **ParamSpider** -> Gather thousands of parameterized URLs passively.
2. **httpx** -> Probe the URLs to see which ones are still returning 200 OK.
3. **Nuclei** -> Run CVE and exposure templates against the live URLs.
4. **Gf (Grep for Hackers)** -> Categorize the URLs into vulnerability classes.
5. **SQLMap / Dalfox** -> Actively exploit the categorized lists.

### Advanced Pipeline Script:
```bash
# 1. Mine parameters
python3 paramspider.py -d target.com -o raw.txt

# 2. Filter for live endpoints (removing FUZZ so httpx can test the base URL)
sed 's/FUZZ/1/g' output/raw.txt | httpx -silent -mc 200,301,302 > live_urls.txt

# 3. Categorize with Gf
cat live_urls.txt | gf sqli > sqli_targets.txt
cat live_urls.txt | gf xss > xss_targets.txt

# 4. Automate exploitation
dalfox file xss_targets.txt -b https://your-xss-blind-server.com
```

## 9. Limitations and Caveats
1. **Passive Only**: If an endpoint or parameter was created yesterday and has never been crawled by the Wayback Machine or OTX, ParamSpider will never see it.
2. **False Positives (Dead Links)**: Because it queries historical data, many of the URLs returned will result in 404 Not Found. You *must* pipe the output through `httpx` or a similar tool to verify the endpoint is still alive.
3. **Context Blindness**: ParamSpider doesn't know if a parameter requires a POST request body, specific headers, or authentication tokens. It simply returns the URL string.

## 10. Related Notes
- [[26 - arjun Parameter Discovery]] - Active parameter discovery to supplement ParamSpider's passive approach.
- [[27 - x8 Hidden Parameter Discovery]] - High-speed active parameter brute-forcing.
- [[02 - API2 — Broken User Authentication]] - Often exploited using historical administrative parameters.
- [[06 - API6 — Mass Assignment]] - Discovering parameters passively that can be actively injected into JSON objects.
