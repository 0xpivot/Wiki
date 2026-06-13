---
tags: [tools, web-testing, utility, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.44 noSQLmap NoSQL Injection Tool"
---

# 59.44 noSQLmap NoSQL Injection Tool

## 1. Introduction and Core Capabilities

`noSQLmap` is an open-source, automated penetration testing tool designed to audit for and exploit NoSQL database vulnerabilities, specifically focusing on NoSQL injection. While traditional tools like `sqlmap` dominate the relational database landscape, the rise of NoSQL databases (like MongoDB, CouchDB, and Redis) necessitates specialized tooling.

NoSQL databases do not use standard SQL syntax. Instead, they rely on JSON, BSON, or object-oriented queries. Consequently, injection attacks do not involve escaping quotes and adding `UNION SELECT` statements; they involve manipulating the structure of JSON objects or injecting operator logic (e.g., `$gt`, `$ne`, `$where`) directly into the backend query structure.

### 1.1 Why noSQLmap?

Identifying NoSQL injection manually can be tedious, requiring careful crafting of JSON payloads, URL-encoding considerations, and boolean inference logic. `noSQLmap` automates the discovery of these flaws, offering automated payload injection, data extraction, and even direct code execution capabilities depending on the database configuration.

### 1.2 Primary Features

*   **Automated Injection Detection**: Scans endpoints for operator injection and boolean-based NoSQL vulnerabilities.
*   **Data Exfiltration**: Automates the extraction of database names, collections, and documents via blind injection techniques.
*   **Network-Level Attacks**: Capable of directly attacking exposed NoSQL management ports if no authentication is required.
*   **Framework Support**: Optimized for modern stacks (Node.js, Express, MongoDB, AngularJS).

## 2. Architectural Overview & Attack Flow

The ASCII diagram below illustrates how `noSQLmap` interacts with a vulnerable Node.js/MongoDB application, transforming a malicious input into a compromised database query.

```text
+-------------------+                          +----------------------+
|                   |   [1] Malicious Payload  |                      |
| Attacker Machine  | -----------------------> |  Target Application  |
| (noSQLmap)        |  (e.g., {"$gt": ""} )    |  (Node.js / Express) |
+-------------------+                          +----------------------+
          |                                               |
          |                                               v
          |                             +-----------------------------------+
          |                             | API Endpoint / Data Access Layer  |
          |                             |                                   |
          v                             |  [2] Driver Query Translation     |
+-------------------+                   |  +-----------------------------+  |
| Attack Vector     |                   |  | db.collection.find({        |  |
| Selection         |                   |  |   username: {"$gt": ""}     |  |
| - Operator Inject |                   |  | })                          |  |
| - Boolean Inject  |                   |  +-----------------------------+  |
| - Timing Attack   |                   |                 |                 |
+-------------------+                   |                 v                 |
          |                             |  [3] MongoDB Database             |
          |                             |  +-----------------------------+  |
          |                             |  | Evaluates to TRUE for all   |  |
          |                             |  | Returns entire user set     |  |
          +-----------------------------+  +-----------------------------+  |
                                                          |
                                                          | [4] Exfiltrated Data
                                                          v
                                        <-----------------------------------+
```

## 3. Installation and Setup

`noSQLmap` is built on Python and relies on specific database drivers to interface with target NoSQL architectures.

### 3.1 Installation Process

```bash
# Clone the repository
git clone https://github.com/codingo/NoSQLMap.git
cd NoSQLMap

# Install Python requirements
python setup.py install

# Launch the interactive menu
python nosqlmap.py
```

## 4. Deep Dive: NoSQL Injection Mechanics

To effectively use `noSQLmap`, it is crucial to understand the distinct nature of NoSQL injection.

### 4.1 Operator Injection

MongoDB and similar databases use query operators prefixed with a dollar sign (`$`). Common operators include `$eq` (equals), `$gt` (greater than), and `$ne` (not equal). If a web framework automatically parses incoming JSON or URL-encoded arrays into backend objects, an attacker can submit an operator instead of a string.

*Expected Input:* `username=admin`  --> Query: `{username: "admin"}`
*Malicious Input:* `username[$ne]=x` --> Query: `{username: {"$ne": "x"}}`
*Result:* Returns all documents where the username is *not* 'x' (essentially bypassing authentication).

### 4.2 JavaScript Injection (The `$where` clause)

MongoDB historically allowed the execution of server-side JavaScript within queries using the `$where` operator. If user input is concatenated into a `$where` clause, an attacker can execute arbitrary JavaScript logic, manipulate data, or introduce sleep commands for timing attacks.

*Query:* `db.users.find({ $where: "this.username == '" + userInput + "'" })`
*Payload:* `a'; sleep(5000); var dummy='`
*Result:* Delays the server response, proving injection and allowing for blind data extraction.

## 5. Using noSQLmap (Menu-Driven Interface)

Unlike traditional CLI tools, `noSQLmap` is primarily operated via an interactive menu.

### 5.1 Main Menu Operations

When you launch `nosqlmap.py`, you are presented with options to configure the target:
1.  **Set options**: Configure the target IP, port, URI path, HTTP method, and headers.
2.  **NoSQL DB Access Attacks**: Direct attacks against unauthenticated database ports (e.g., port 27017).
3.  **NoSQL Web App attacks**: Exploiting web-facing endpoints via HTTP requests.

### 5.2 Configuring a Web App Attack

1.  Select `1` to configure options.
2.  Set `Target Host/IP` to the target domain.
3.  Set `Web App Path` to the vulnerable endpoint (e.g., `/api/login`).
4.  Set `HTTP Request Method` (GET/POST).
5.  If POST, define the `POST Data`. Use a placeholder like `*` to tell `noSQLmap` exactly where to inject the payloads.
6.  Return to the main menu and select `3` (Web App attacks), then choose automated injection testing.

## 6. Advanced Attack Methodologies

### 6.1 Blind NoSQL Injection (Boolean Inference)

If the application does not return database errors or data directly, `noSQLmap` relies on boolean inference. By asking the database true/false questions, it reconstructs data character by character.

*Payload Example:* `username[$regex]=^a.*`
If the server responds normally (or a login succeeds), the tool knows the target username starts with 'a'. `noSQLmap` automates this regex-based character guessing to exfiltrate entire collections.

### 6.2 Exploiting PHP Arrays in MongoDB

PHP applications interacting with MongoDB are particularly vulnerable. In PHP, `?user[username]=admin` is parsed into an associative array `['user' => ['username' => 'admin']]`. If passed directly to the MongoDB driver, attackers can inject arrays containing operators (`?user[$ne]=null`), bypassing input validation entirely.

## 7. Troubleshooting and Limitations

*   **Modern Driver Protections**: Many modern NoSQL drivers (like newer versions of Mongoose for Node.js) have built-in protections against operator injection by strictly defining schema types. If a field is defined as a `String`, attempting to pass an object (`{"$gt": ""}`) will result in a cast error, halting the injection.
*   **Limited Database Support**: While `noSQLmap` is excellent for MongoDB, its support for CouchDB, Redis, and Cassandra is less robust and may require manual intervention.
*   **False Positives**: Timing-based injections can result in false positives over high-latency networks. Increase the threshold and verify manually using a tool like Burp Suite.

## 8. Defensive Mitigation and Remediation

1.  **Type Validation (Schemas)**: Enforce strict schemas. If an API expects a string, validate that the incoming data type is explicitly a string, not an object or array. Libraries like `Mongoose` do this natively if configured correctly.
2.  **Input Sanitization**: Use libraries to sanitize inputs and strip out key characters like `$` or `.` from user-supplied data before passing it to database queries.
    *   Node.js example: Use `mongo-sanitize`.
3.  **Disable Server-Side JavaScript**: In MongoDB, disable the execution of server-side JavaScript entirely if it is not absolutely necessary. Set `javascriptEnabled: false` in the `mongod.conf` file to neutralize `$where` attacks.
4.  **Use Parameterized-style APIs**: Use framework-provided APIs that inherently separate data from query structure, preventing logic injection.

## 9. Chaining Opportunities

*   **[[12 - Broken Authentication]]**: Bypassing login forms using operator injection (`$ne`).
*   **[[01 - Insecure Direct Object References (IDOR)]]**: Modifying MongoDB ObjectIDs directly to access cross-tenant data.
*   **[[16 - Remote Code Execution (RCE)]]**: Exploiting legacy `$where` clauses or unauthenticated database instances to execute OS-level commands.

## 10. Related Notes

*   [[21 - NoSQL Injection Deep Dive]]
*   [[10 - SQL Injection vs NoSQL Injection]]
*   [[46 - sqlmap Reference]]
*   [[99 - Penetration Testing Cheatsheet]]
