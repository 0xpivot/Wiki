---
tags: [reporting, vapt, professional, template]
difficulty: advanced
module: "42 - VAPT Reporting"
topic: "42.14 Sample Finding SQLi"
---

# 14 - Sample Finding — SQL Injection

## Introduction

This document provides a comprehensive template and example for reporting a SQL Injection (SQLi) vulnerability within a professional VAPT report.
A well-documented finding must clearly articulate the vulnerability, its impact, the evidence of exploitation, and actionable remediation guidance.
This template ensures consistency and high quality in vulnerability reporting.

## The Anatomy of a Finding

A professional finding should contain the following distinct sections:

1.  **Title:** Clear and concise, indicating the vulnerability type and location.
2.  **Severity Rating:** Based on a standard scoring system (e.g., CVSS v3.1).
3.  **Description:** A detailed explanation of the vulnerability and how it occurs in the specific context of the application.
4.  **Impact:** The potential business and technical consequences if the vulnerability is exploited by a malicious actor.
5.  **Proof of Concept (PoC):** Step-by-step instructions and evidence demonstrating the exploitability of the issue.
6.  **Remediation:** Actionable advice on how to fix the vulnerability.
7.  **References:** Links to relevant documentation or standards.

## Sample Finding Presentation

Below is an example of how a critical SQL Injection finding should be structured.

---

### Finding #1: Boolean-Based Blind SQL Injection in User Authentication

**Severity:** Critical (CVSS: 9.8 - CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
**CWE:** CWE-89: Improper Neutralization of Special Elements used in an SQL Command
**Location:** `https://app.example.com/login.php` (Parameter: `username`)

#### Description

The testing team identified a Boolean-Based Blind SQL Injection vulnerability in the authentication mechanism of the application. The `username` parameter submitted via a POST request to `/login.php` is insecurely concatenated into a backend database query without adequate sanitization or parameterization.

Because the application does not return the direct results of the database query (hence "blind"), the vulnerability must be exploited by inferring data bit-by-bit based on the application's response to true or false conditions. Specifically, injecting a conditionally true statement results in a generic "Invalid Password" error, while a false statement results in an "Invalid Username" error, allowing an attacker to map out the entire database structure and extract data.

#### Impact

Successful exploitation of this vulnerability allows an unauthenticated, remote attacker to execute arbitrary SQL commands against the backend database.

The impact is critical and includes:
-   **Data Breach:** Complete extraction of all data within the database, including sensitive customer Personally Identifiable Information (PII), administrative credentials, and proprietary business data.
-   **Data Integrity Loss:** The ability to modify or delete data, potentially causing severe operational disruption.
-   **Authentication Bypass:** The attacker could potentially alter their own privilege level or bypass the login mechanism entirely.
-   **Potential Server Compromise:** Depending on the database configuration and privileges, SQLi can sometimes be escalated to Remote Code Execution (RCE) on the underlying operating system.

#### ASCII Diagram: Boolean Inference Logic

```text
+-------------------+       Payload: ' OR 1=1 --    +-------------------+
| Attacker          | ----------------------------> | Application       |
| Sends Payload     |                               | Processes Query   |
+-------------------+                               +---------+---------+
                                                              |
                                                              v
+-------------------+       True Condition:         +---------+---------+
| Attacker Infers   | <---------------------------- | Database Returns  |
| Data bit is '1'   |       "Invalid Password"      | Result to App     |
+-------------------+                               +-------------------+
        ^
        |
        |                   Payload: ' OR 1=2 --    +-------------------+
+-------------------+ ----------------------------> | Application       |
| Attacker          |                               | Processes Query   |
+-------------------+                               +---------+---------+
                                                              |
                                                              v
+-------------------+       False Condition:        +---------+---------+
| Attacker Infers   | <---------------------------- | Database Returns  |
| Data bit is '0'   |       "Invalid Username"      | Result to App     |
+-------------------+                               +-------------------+
```

#### Proof of Concept (PoC)

**Step 1:** The following baseline request was captured during the login process.

```http
POST /login.php HTTP/1.1
Host: app.example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=password123
```
*Response:* `HTTP/200 OK` with body containing `Invalid Password`.

**Step 2:** A payload designed to evaluate to FALSE was injected into the `username` parameter.

```http
POST /login.php HTTP/1.1
Host: app.example.com
Content-Type: application/x-www-form-urlencoded

username=admin' AND 1=2 -- &password=password123
```
*Response:* `HTTP/200 OK` with body containing `Invalid Username`. This change in response indicates the database evaluated the injected condition.

**Step 3:** To demonstrate data extraction capabilities, the team used the `sqlmap` tool to extract the current database user. The following command was executed:

```bash
sqlmap -u "https://app.example.com/login.php" --data="username=admin&password=password123" -p username --dbms=mysql --current-user --batch
```

**Step 4:** The tool successfully extracted the database user, confirming the vulnerability.

*Evidence (sqlmap output snippet):*
```text
[INFO] fetching current user
[INFO] retrieved: 'db_admin@localhost'
current user: 'db_admin@localhost'
```

*Note: Data extraction was limited to demonstrating impact; no sensitive client data was permanently stored or exfiltrated by the assessment team.*

#### Remediation

**Immediate Action (Short-Term):**
Implement Web Application Firewall (WAF) rules to detect and block common SQL injection payloads targeting the `/login.php` endpoint. This is a temporary measure and must not replace the long-term solution.

**Strategic Solution (Long-Term):**
The root cause must be addressed by eliminating the insecure string concatenation used to construct database queries.

1.  **Implement Parameterized Queries (Prepared Statements):** This is the primary defense against SQL injection. Parameterization ensures that user input is treated strictly as data, not as executable code by the database parser.

    *Example Implementation (PHP Data Objects - PDO):*
    ```php
    // Vulnerable Code (Do NOT use)
    // $query = "SELECT * FROM users WHERE username = '" . $_POST['username'] . "'";

    // Secure Code (Use Prepared Statements)
    $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username');
    $stmt->execute(['username' => $_POST['username']]);
    $user = $stmt->fetch();
    ```

2.  **Employ an Object-Relational Mapping (ORM) Framework:** If appropriate for the architecture, using a modern ORM (e.g., Hibernate, Entity Framework) can significantly reduce the risk of SQL injection, as they inherently utilize parameterized queries.

3.  **Enforce Principle of Least Privilege:** Ensure the database user account used by the application (`db_admin@localhost`) has only the minimum necessary privileges required to function. It should not have administrative access to the entire database server.

#### References
-   [OWASP Top 10 - A03:2021-Injection](https://owasp.org/Top10/A03_2021-Injection/)
-   [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

---

## Conclusion

A finding formatted in this manner leaves no room for ambiguity. It clearly defines the problem, proves it exists, explains why the client should care, and tells them exactly how to fix it.

## Chaining Opportunities

-   A SQL injection finding like this is often the linchpin in a broader [[12 - Attack Narrative]], serving as the primary mechanism for data exfiltration or initial access to backend systems.
-   Proper remediation, as detailed here, is essential to ensure the vulnerability passes the [[13 - Retesting Methodology]] phase.

## Related Notes

-   [[11 - Remediation Guidance]]
-   [[12 - Attack Narrative]]
-   [[13 - Retesting Methodology]]
-   [[15 - Sample Full Report]]
