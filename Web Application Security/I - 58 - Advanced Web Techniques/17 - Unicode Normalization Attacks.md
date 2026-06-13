---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.17 Unicode Normalization Attacks"
---

# Unicode Normalization Attacks

## Introduction to Unicode Normalization

Unicode Normalization Attacks represent a sophisticated class of vulnerabilities that exploit the discrepancies between how different systems process, normalize, and interpret Unicode text. As modern applications strive to support global character sets, they rely on Unicode, which contains over 140,000 characters. 

The complexity of Unicode stems from the fact that a single visual character (a grapheme) can often be represented by multiple different sequences of codepoints. For example, the character `é` can be represented as a single precomposed character (U+00E9) or as a combination of two characters: the base letter `e` (U+0065) followed by a combining acute accent (U+0301). 

To ensure consistency in string comparison, searching, and storage, applications use **Unicode Normalization**. Normalization converts text into a standard, canonical form. However, if a security mechanism (like a Web Application Firewall, XSS filter, or authorization check) is performed *before* normalization, and the backend application performs normalization *after*, an attacker can slip malicious payloads past the filters using visually dissimilar but logically equivalent characters.

## The Four Forms of Unicode Normalization

The Unicode Consortium defines four standard normalization forms. Understanding these is critical to executing and mitigating normalization attacks.

1. **NFC (Normalization Form Canonical Composition):** 
   Combines characters into their shortest precomposed form. (e.g., `e` + `´` becomes `é`).
2. **NFD (Normalization Form Canonical Decomposition):** 
   Breaks down precomposed characters into their base characters and combining marks. (e.g., `é` becomes `e` + `´`).
3. **NFKC (Normalization Form Compatibility Composition):** 
   Like NFC, but applies *compatibility* decomposition first. This converts formatting variants (like superscript `²`, full-width `Ａ`, or ligatures like `ﬁ`) into their standard equivalents (`2`, `A`, `fi`), and then composes them.
4. **NFKD (Normalization Form Compatibility Decomposition):** 
   Like NFD, but applies *compatibility* decomposition.

**The Security Implication:** Forms NFKC and NFKD are particularly dangerous because they map visually distinct "compatibility" characters into standard ASCII equivalents. If a WAF blocks `<script>`, an attacker might send `＜ｓｃｒｉｐｔ＞` (Full-width characters). The WAF allows it, but if the backend uses NFKC/NFKD, it converts it back to `<script>`, resulting in XSS.

## ASCII Architecture Diagram: The Filter Bypass Mechanism

```text
+-------------------------------------------------------------+
|                     ATTACKER PAYLOAD                        |
|   Payload: ＜ｓｃｒｉｐｔ＞ (Full-width Unicode)            |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                     WAF / SECURITY FILTER                   |
|                                                             |
|  Rule: BLOCK IF contains "<script>"                         |
|  Check: "＜ｓｃｒｉｐｔ＞" != "<script>"                    |
|  Result: PASS / ALLOWED                                     |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                     BACKEND APPLICATION                     |
|                                                             |
|  Step 1: Receive "＜ｓｃｒｉｐｔ＞"                         |
|  Step 2: Normalize string to NFKC                           |
|  Result: normalized_payload = "<script>"                    |
|                                                             |
|  Step 3: Render to page or execute in DB query              |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                     VICTIM / BROWSER                        |
|                                                             |
|  Executes: <script> ... malicious code ...                  |
|  Impact: SYSTEM COMPROMISED / XSS TRIGGERED                 |
+-------------------------------------------------------------+
```

## Attack Scenarios and Vectors

### 1. Bypassing WAFs and XSS Filters
As illustrated in the diagram, attackers can use compatibility characters to bypass string matching filters. 
For instance, the Kelven symbol `K` (U+212A) normalizes to the ASCII character `K` (U+004B). 
If an application filters the keyword `COOKIE`, an attacker could inject `CKOOKIE` (using the Kelven symbol). The filter sees a harmless string and allows it. Later, a backend normalization process (like Python's `unicodedata.normalize('NFKC', string)`) converts it to `COOKIE`, executing the attack.

### 2. SQL Injection (SQLi) via Normalization
Consider a backend that escapes single quotes (`'`) to prevent SQL injection. 
If an attacker sends a modifier letter apostrophe `ʼ` (U+02BC) or a full-width apostrophe `＇` (U+FF07), the escaping function might ignore it because it's technically not a standard ASCII single quote `\x27`.
However, if the database driver or the database itself (like certain configurations of MySQL or MS SQL) automatically normalizes the input before parsing the SQL query, that compatibility quote becomes a standard quote, breaking out of the string literal and achieving SQL injection.

### 3. Account Takeover and User Impersonation
Normalization vulnerabilities are infamous in account registration and login flows.
Imagine a system where the username `admin` exists. 
An attacker registers the username `admｉn` (using the full-width `ｉ` U+FF49). 
- The system checks if `admｉn` exists in the database. It does not.
- The registration succeeds.
- Later, the user logs in. The system might perform NFKC normalization on the username *during the password reset flow* or *internal authorization checks*, reducing `admｉn` to `admin`.
- The attacker now has the ability to reset the password for the real `admin` account or access resources meant only for the `admin` user. This exact vulnerability impacted platforms like Spotify and GitHub in the past.

### 4. Directory Traversal Bypass
If a system blocks `../` to prevent directory traversal, an attacker can use `．．／` (Full-width dot and slash). If the file system routing logic normalizes the path using NFKC before fetching the file, the attacker successfully bypasses the restriction and accesses sensitive files like `/etc/passwd`.

## Code Analysis: Vulnerable Python Implementation

Let's look at a concrete example of how this occurs in a Python web application using Flask.

```python
import unicodedata
from flask import Flask, request, abort

app = Flask(__name__)

# Mock database
users = {"admin": "super_secret_hash"}

def check_username_availability(username):
    # Vulnerability 1: Security check BEFORE normalization
    if username.lower() == "admin":
         return False
    return True

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    
    if not check_username_availability(username):
        abort(403, "Username taken.")
        
    # Vulnerability 2: Normalization applied AFTER the check
    normalized_username = unicodedata.normalize('NFKC', username)
    
    # Save to DB (Attacker overwrites real admin)
    users[normalized_username] = request.form['password']
    return "Registered successfully."
```

In this code, if an attacker sends `admin` with a full-width `a` (`ａdmin`), `check_username_availability` returns `True` because `ａdmin` != `admin`. 
Then, `unicodedata.normalize('NFKC', username)` converts `ａdmin` into `admin`. 
The application then overwrites the real admin's password in the `users` dictionary.

## Advanced Mitigation Strategies

Securing an application against Unicode Normalization attacks requires architectural discipline and understanding the order of operations in data processing.

1. **Normalize First, Validate Second:**
   This is the golden rule. Any user input MUST be normalized *before* any security checks, validations, sanitizations, or routing decisions are made. 
   ```python
   # Correct Approach
   username = request.form['username']
   normalized_username = unicodedata.normalize('NFKC', username)
   
   if not check_username_availability(normalized_username):
       abort(403)
   ```

2. **Consistent Normalization Forms:**
   Ensure that every component in your tech stack (Frontend, WAF, Backend Application, Database, and Search Engine) uses the exact same Unicode normalization form (preferably NFC for general text storage). Discrepancies between components create gaps for attackers to exploit.

3. **Database Collation Awareness:**
   Understand your database's collation settings. Some collations (like `utf8_general_ci` in MySQL) treat different Unicode characters as equivalent during comparisons even without explicit normalization by the application. Ensure your application's uniqueness checks align with how the database evaluates uniqueness.

4. **Restrict Allowed Character Sets:**
   For fields like usernames, email addresses, or identifiers, do not allow arbitrary Unicode characters unless strictly necessary. Restrict input to `[A-Za-z0-9_-]` where possible. If internationalization is required, use strict allow-lists for supported Unicode ranges and reject compatibility blocks.

## Chaining Opportunities

- **[[03 - Cross-Site Scripting (XSS)]]**: Bypassing XSS WAF rules using full-width characters.
- **[[06 - SQL Injection (SQLi)]]**: Escaping string enclosures by passing compatibility quotation marks.
- **[[18 - Homograph Attacks]]**: Homograph attacks also rely on Unicode confusions, but target human perception rather than backend normalization logic.
- **[[11 - Business Logic Vulnerabilities]]**: Exploiting username registration flows to achieve account takeover.

## Related Notes

- [[02 - Input Validation and Sanitization]]
- [[24 - Proxy and WAF Evasion]]
- [[13 - Authentication Bypasses]]
- [[52 - Advanced Cryptography and Hashing]]

---
*End of Document*
