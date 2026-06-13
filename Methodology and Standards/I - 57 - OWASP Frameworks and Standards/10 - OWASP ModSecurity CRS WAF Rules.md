---
tags: [owasp, standards, framework, vapt]
difficulty: intermediate
module: "57 - OWASP Frameworks and Standards"
topic: "57.10 OWASP ModSecurity CRS WAF Rules"
---

# OWASP ModSecurity Core Rule Set (CRS)

## 1. Introduction to ModSecurity and CRS
**ModSecurity** is an open-source, cross-platform Web Application Firewall (WAF) engine. By itself, ModSecurity does not protect an application; it is simply an engine that processes HTTP traffic and executes rules.

The **OWASP Core Rule Set (CRS)** is a set of generic attack detection rules designed specifically for use with ModSecurity. The CRS aims to protect web applications from a wide range of attacks, including the OWASP Top 10, with a minimum of false alerts.

### Key Benefits:
*   Provides a robust, drop-in defense mechanism against known vulnerability categories.
*   Highly tunable to balance security stringency with false-positive rates.
*   Operates transparently at the reverse proxy or web server layer (e.g., Apache, Nginx, IIS).

---

## 2. ModSecurity CRS Architecture and Flow

The WAF engine processes requests in distinct phases. The ASCII diagram below illustrates the life cycle of an HTTP transaction through ModSecurity phases.

```text
+-----------------------------------------------------------------------------------+
|                        HTTP Transaction Lifecycle in ModSecurity                  |
|                                                                                   |
|  [ Client Request ]                                                               |
|          |                                                                        |
|          v                                                                        |
|  +--------------------+                                                           |
|  | PHASE 1            | --> Parses URI, Query Strings, HTTP Headers.              |
|  | (Request Headers)  |     (Checks for malicious User-Agents, Protocol issues)   |
|  +--------------------+                                                           |
|          |                                                                        |
|          v                                                                        |
|  +--------------------+                                                           |
|  | PHASE 2            | --> Parses Request Body (POST/PUT data, JSON, XML).       |
|  | (Request Body)     |     (Checks for SQLi, XSS, RCE payloads in payload)       |
|  +--------------------+                                                           |
|          |                                                                        |
|          | (If not blocked, passed to Backend Application)                        |
|          v                                                                        |
|  [ Backend Application ]                                                          |
|          |                                                                        |
|          v                                                                        |
|  +--------------------+                                                           |
|  | PHASE 3            | --> Parses HTTP Response Headers from backend.            |
|  | (Response Headers) |     (Checks for missing secure headers, status codes)     |
|  +--------------------+                                                           |
|          |                                                                        |
|          v                                                                        |
|  +--------------------+                                                           |
|  | PHASE 4            | --> Parses Response Body (HTML, API responses).           |
|  | (Response Body)    |     (Checks for Data Leakage, Stack Traces, SSNs)         |
|  +--------------------+                                                           |
|          |                                                                        |
|          v                                                                        |
|  [ Phase 5: Logging ] ----> Request logged to audit logs regardless of action.    |
|          |                                                                        |
|          v                                                                        |
|   [ Client Response ]                                                             |
+-----------------------------------------------------------------------------------+
```

---

## 3. Anomaly Scoring Mode

Historically, WAFs operated in a traditional mode: if a rule matched, the WAF immediately blocked the request. This led to high false positive rates and broken applications.

The OWASP CRS utilizes **Anomaly Scoring Mode**.
1.  As a request passes through the phases, matched rules do not block the request immediately.
2.  Instead, each matched rule adds points to a cumulative **Anomaly Score**.
    *   Critical anomaly: +5 points
    *   Error anomaly: +4 points
    *   Warning anomaly: +3 points
    *   Notice anomaly: +2 points
3.  At the end of Phase 2 (for requests) or Phase 4 (for responses), the total score is compared to an **Inbound/Outbound Threshold**.
4.  If the cumulative score exceeds the threshold (e.g., limit is 5), the request is blocked and an HTTP 403 Forbidden is returned.

This approach significantly reduces false positives by requiring multiple indicators of compromise or highly confident signatures before blocking.

---

## 4. Paranoia Levels (PL)

The CRS is divided into four Paranoia Levels. Administrators choose a PL based on the risk profile of the application.

*   **Paranoia Level 1 (Default):** A baseline set of rules that minimizes false positives. Highly reliable, suitable for virtually all applications without extensive tuning. Detects obvious and common attacks.
*   **Paranoia Level 2:** Adds extra rules (e.g., checking for unusual characters in payloads, deeper SQLi regex). May cause some false positives depending on the application's input types.
*   **Paranoia Level 3:** Adds aggressive rules tailored for high-security applications (e.g., banking, healthcare). Enforces strict limits on special characters. Requires significant tuning and false positive management.
*   **Paranoia Level 4:** The most restrictive mode. Blocks almost anything that is not standard, alphanumeric web traffic. Extensively locks down HTTP protocol usage. Designed only for highly restricted API endpoints or critical infrastructure.

---

## 5. Configuration and Syntax

ModSecurity rules are written using a specific syntax called `SecRule`.

### 5.1 Basic SecRule Syntax
```apache
SecRule VARIABLES "OPERATOR" "ACTIONS"
```
*   **VARIABLES:** What to inspect (e.g., `ARGS`, `REQUEST_HEADERS:User-Agent`).
*   **OPERATOR:** How to inspect it (e.g., `@rx` for regex, `@pm` for parallel match).
*   **ACTIONS:** What to do if matched (e.g., `id:1001, phase:2, deny, status:403, msg:'XSS Attack Detected'`).

### 5.2 Example: CRS XSS Rule (Simplified)
```apache
SecRule ARGS|ARGS_NAMES|REQUEST_COOKIES|!REQUEST_COOKIES:/__utm/ "@rx (?i)<script[^>]*>[\s\S]*?</script>" \
    "id:941110,\
    phase:2,\
    block,\
    capture,\
    t:none,t:utf8toUnicode,t:urlDecodeUni,t:htmlEntityDecode,t:jsDecode,\
    msg:'XSS Filter - Category 1: Script Tag Vector',\
    logdata:'Matched Data: %{TX.0} found within %{MATCHED_VAR_NAME}: %{MATCHED_VAR}',\
    tag:'application-multi',\
    tag:'language-multi',\
    tag:'platform-multi',\
    tag:'attack-xss',\
    ver:'OWASP_CRS/3.3.0',\
    severity:'CRITICAL',\
    setvar:'tx.xss_score=+%{tx.critical_anomaly_score}',\
    setvar:'tx.anomaly_score_pl1=+%{tx.critical_anomaly_score}'"
```
*Note how the rule uses multiple transformation functions (`t:urlDecodeUni`, `t:htmlEntityDecode`) to normalize data before applying the regex, preventing basic encoding bypasses.*

---

## 6. Tuning and Handling False Positives

When a legitimate request is blocked by the CRS, it is considered a false positive. Administrators must write **Rule Exclusions** to tune the WAF.

### Method 1: Disabling a Rule Entirely
If rule `942100` (SQLi) is too noisy and irrelevant, disable it globally:
```apache
SecRuleRemoveById 942100
```

### Method 2: Disabling a Rule for a Specific Endpoint
Only disable rule `942100` on the `/login.php` page:
```apache
SecRule REQUEST_FILENAME "@streq /login.php" \
    "id:10001,phase:1,pass,nolog,ctl:ruleRemoveById=942100"
```

### Method 3: Disabling a Rule for a Specific Parameter
If the `bio` parameter in the profile update legitimately accepts HTML (triggering XSS rules), exclude that parameter from the XSS rule, but keep the rule active for all other parameters:
```apache
SecRule UPDATE_TARGETS "TX:941110" "id:10002,phase:1,pass,nolog,ctl:ruleRemoveTargetById=941110;ARGS:bio"
```

---

## 7. WAF Evasion and Chaining Opportunities

From an attacker's perspective, WAF evasion involves finding discrepancies between how the WAF parses a request (Phases 1/2) and how the backend application parses it.

*   **Impedance Mismatch:** If the WAF parses JSON rigidly, but the backend Node.js server parses it flexibly, an attacker might send malformed JSON that bypasses the WAF's regex but is successfully processed by the backend (e.g., using unicode escapes like `\u0027` instead of `'`).
*   **HTTP Desync (Request Smuggling):** Exploiting discrepancies in `Content-Length` and `Transfer-Encoding` headers. The WAF might see one harmless request, while the backend processes two requests, the second containing the malicious payload, entirely bypassing Phase 2 inspection.
*   **Chaining with BOLA:** WAFs are generally incapable of detecting Broken Object Level Authorization (BOLA/IDOR). Since BOLA payloads look like legitimate traffic (e.g., `GET /api/user/9999`), chaining an initial WAF bypass with a BOLA attack is highly effective.

---

## 8. Related Notes
*   [[07 - OWASP WSTG Testing Checklist]]
*   [[12 - Cross Site Scripting XSS]]
*   [[03 - Injection]]
*   [[16 - HTTP Request Smuggling]]
