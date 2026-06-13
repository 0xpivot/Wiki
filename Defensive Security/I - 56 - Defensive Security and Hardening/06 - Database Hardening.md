---
tags: [defense, hardening, security, vapt]
difficulty: intermediate
module: "56 - Defensive Security and Hardening"
topic: "56.06 Database Hardening"
---

# 56.06 Database Hardening

## Introduction
Database Hardening is the process of securing a database to reduce its vulnerability surface and protect the critical data it houses from unauthorized access, modification, or destruction. It goes beyond simple access control, extending into the realms of operating system configuration, network-level security, encryption (both in transit and at rest), auditing, and regular patching. Given that databases are the crown jewels of most modern architectures, securing them is paramount. A compromised web application might lead to a defacement; a compromised database leads to catastrophic data breaches, severe regulatory fines, and irreparable reputational damage.

## The Threat Landscape
Before diving into hardening, we must understand the diverse and evolving threats we are defending against. 
- **SQL Injection (SQLi):** Attackers exploit poorly sanitized input to execute malicious SQL statements. While primarily an application flaw, a hardened database restricts the blast radius of a successful SQLi.
- **Unauthorized Access/Privilege Escalation:** Weak default configurations or compromised credentials allow attackers to access databases, often escalating privileges to DBA (Database Administrator).
- **Data Exfiltration:** Extraction of sensitive information by exploiting network configurations or lack of encryption.
- **Denial of Service (DoS):** Exhausting database resources (CPU, Memory, connections) to render services unavailable.
- **Unpatched Vulnerabilities:** Exploiting known CVEs in database software to gain remote code execution or bypass authentication.
- **Insider Threats:** Malicious or negligent employees with excessive privileges extracting or destroying data.

## Architecture and Security Controls

Below is an ASCII diagram illustrating a hardened database architecture.

```text
+---------------------------------------------------------------------------------------+
|                                    Enterprise Network                                 |
|                                                                                       |
|   +-------------------+       +-----------------------+       +-------------------+   |
|   |    Web Server     |       |   Application Server  |       |   Bastion Host    |   |
|   | (DMZ, Web Facing) | ----> |   (Internal VLAN)     | <---- | (Admin Access)    |   |
|   +-------------------+       +-----------+-----------+       +-------------------+   |
|                                           |                                           |
|                                           | Port 3306/5432 (TLS only)                 |
|                                           v                                           |
|   +-------------------------------------------------------------------------------+   |
|   |                        Strict Firewall / WAF / DB Proxy                       |   |
|   +---------------------------------------+---------------------------------------+   |
|                                           |                                           |
|                                           v                                           |
|   +-------------------------------------------------------------------------------+   |
|   |                        Database Subnet (Isolated VLAN)                        |   |
|   |                                                                               |   |
|   |   +-----------------------------------------------------------------------+   |   |
|   |   |                      Database Management System (DBMS)                |   |   |
|   |   |                                                                       |   |   |
|   |   |  +--------------------+  +--------------------+  +-----------------+  |   |   |
|   |   |  |   Authentication   |  |   Authorization    |  |  Encryption Engine|  |   |   |
|   |   |  | (IAM, AD, MFA)     |  | (RBAC, Least Priv) |  | (TDE, TLS 1.3)    |  |   |   |
|   |   |  +--------------------+  +--------------------+  +-----------------+  |   |   |
|   |   |                                                                       |   |   |
|   |   |  +-----------------------------------------------------------------+  |   |   |
|   |   |  |                         Audit & Logging                         |  |   |   |
|   |   |  |                   (Syslog, Guardium, Splunk)                    |  |   |   |
|   |   |  +-----------------------------------------------------------------+  |   |   |
|   |   +-----------------------------------+-----------------------------------+   |   |
|   |                                       |                                       |   |
|   |   +-----------------------------------+-----------------------------------+   |   |
|   |   |                            Encrypted Storage                          |   |   |
|   |   |                           (SAN / Local Disk)                          |   |   |
|   |   +-----------------------------------------------------------------------+   |   |
|   +-------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------+
```

## Core Principles of Database Hardening

### 1. Physical and OS-Level Security
The foundation of database security begins below the DBMS itself. If the OS is compromised, the database is compromised.
- **OS Hardening:** The underlying server must be hardened. Disable unnecessary services (FTP, Telnet), use SELinux or AppArmor to enforce mandatory access controls, and enforce strict file permissions on database directories.
- **Dedicated Servers:** Databases should reside on dedicated servers (or isolated VMs/containers) to prevent compromise via adjacent vulnerable applications. Never run a web server and a database on the same OS instance.
- **File System Permissions:** Restrict access to database binaries, configuration files (e.g., `my.cnf`, `postgresql.conf`), and data files to the specific user account running the database service (e.g., `postgres` or `mysql`).

### 2. Network Isolation
Databases must never be directly exposed to the internet.
- **VLANs and Subnets:** Place the database in a dedicated, non-routable private subnet.
- **Firewall Rules:** Implement strict egress and ingress rules. The database should only accept connections from explicitly authorized application servers and administrative bastion hosts. Use an allowlist approach.
- **Change Default Ports:** While security through obscurity is not a primary defense, changing default ports (e.g., moving away from 3306 for MySQL or 1433 for MS SQL) can reduce automated scanning noise and worm propagation.
- **Database Firewalls (DAM):** Consider Database Activity Monitoring firewalls that can inspect SQL queries over the wire and block malicious payloads before they hit the database engine.

### 3. Authentication and Access Control
- **Remove Default Accounts:** Ensure default accounts like `sa` (SQL Server), `root` (MySQL), or `postgres` are either disabled, renamed, or protected with extremely complex, vaulted passwords.
- **Principle of Least Privilege:** Applications should connect using service accounts with strictly limited permissions. If an app only needs to `SELECT` and `INSERT`, do not grant it `UPDATE`, `DELETE`, or `DROP` privileges. Never grant `FILE` or administrative privileges to an application user.
- **Role-Based Access Control (RBAC):** Group permissions into roles and assign roles to users. This simplifies management and ensures consistency.
- **Multi-Factor Authentication (MFA):** Require MFA for administrative access to the database, often implemented via IAM integration, Active Directory, or PAM (Privileged Access Management) solutions.

### 4. Encryption
Data must be protected both in transit and at rest to defend against physical theft or network sniffing.
- **In Transit:** Enforce TLS (version 1.2 or 1.3) for all database connections. Reject unencrypted connections entirely. Configure the application to strictly verify the database's SSL certificate to prevent Man-in-the-Middle (MitM) attacks.
- **At Rest:** Use Transparent Data Encryption (TDE) to encrypt the data files on the disk. For extremely sensitive fields (like PII, credit cards), implement application-level encryption or column-level encryption so that even the DBA cannot read the plaintext data without the application keys.
- **Key Management:** Store encryption keys in a secure Key Management Service (KMS) or Hardware Security Module (HSM), strictly separated from the database itself.

### 5. Auditing and Monitoring
You cannot secure what you do not monitor. Detection is just as critical as prevention.
- **Enable Auditing:** Log failed login attempts, schema changes (DDL), permission changes (DCL), and potentially sensitive data access (DML).
- **Centralized Logging:** Forward all database logs to a centralized SIEM (Security Information and Event Management) system in real-time. Do not leave logs solely on the database server where an attacker could wipe them to cover their tracks.
- **Query Analysis:** Implement tools that analyze query patterns to detect anomalies, such as sudden bulk data extraction (e.g., `SELECT * FROM users`) indicating a potential data breach or malicious insider activity.

### 6. Patching and Updates
- **Vulnerability Management:** Regularly scan the database infrastructure for known vulnerabilities using automated tools.
- **Patch Management:** Establish a rigorous patching schedule. Subscribe to vendor security advisories and apply critical patches immediately. Apply patches in a staging environment first to ensure they do not break application functionality.

## Specific DBMS Hardening Examples

### PostgreSQL
- Edit `pg_hba.conf` to strictly define which hosts can connect, and require strong authentication methods like `scram-sha-256`. Do not use `trust` or `password` (which sends plaintext).
- Disable listening on all interfaces if not needed: set `listen_addresses = 'localhost'` or a specific internal IP.
- Use the `pgAudit` extension for detailed session and object audit logging.
- Regularly monitor `pg_stat_statements` for query profiling and anomaly detection.

### MySQL / MariaDB
- Run `mysql_secure_installation` immediately post-install to remove anonymous users, disable remote root login, and drop the test database.
- Set `local_infile = 0` to prevent attackers from reading local files if they find a SQL injection vulnerability.
- Ensure `skip-symbolic-links` is enabled to prevent file-level symlink attacks that could overwrite system files.
- Use the `audit_log` plugin for comprehensive tracking.

### NoSQL Considerations (MongoDB / Redis)
- **MongoDB:** Enable authorization (`security.authorization: enabled` in `mongod.conf`), which is disabled by default. Bind to localhost or specific internal IPs only. Implement RBAC.
- **Redis:** Never expose Redis to the internet. Require a strong `requirepass` configuration. Disable dangerous commands using `rename-command CONFIG ""` and `rename-command FLUSHALL ""`.

## Cloud Database Considerations (RDS, Aurora, Cloud SQL)
- Rely on cloud provider security groups instead of OS-level firewalls.
- Enable automated KMS integration for at-rest encryption.
- Force IAM authentication instead of static database passwords where supported.
- Disable public accessibility flags (e.g., AWS RDS `Publicly Accessible: No`).

## Common Pitfalls
- **Hardcoded Credentials:** Storing database credentials directly in source code instead of using environment variables or a secrets manager like HashiCorp Vault.
- **Overprivileged Accounts:** Using the same administrative account for application connections and database management.
- **Ignoring Backups:** Failing to secure backup files. A stolen backup is as damaging as a live database breach. Backups must be encrypted, access-restricted, and ideally stored in immutable, air-gapped storage.
- **Neglecting Staging Environments:** Often, production is locked down, but staging or dev environments containing production data clones are left vulnerable and exposed. Always sanitize or generate synthetic data for lower environments.

## Step-by-Step Hardening Checklist
1. Identify and inventory all database assets, including shadow IT instances.
2. Conduct a vulnerability assessment of the OS and DBMS.
3. Review and refine network access controls (firewalls, security groups, VPCs).
4. Enforce TLS for all client-server connections.
5. Review user accounts; remove defaults, enforce strong passwords, rotate keys.
6. Implement strict RBAC and the Principle of Least Privilege.
7. Configure at-rest encryption (TDE, full disk encryption).
8. Enable and centralize audit logging to a SIEM.
9. Verify backup integrity, encryption, and secure storage.
10. Establish an ongoing patch management and configuration drift monitoring process.

## Chaining Opportunities
- Database vulnerabilities are often chained with **[[04 - Web Application Firewalls]]** bypasses. If an attacker bypasses the WAF, a hardened database ensures the exploit payload (like SQLi) is confined by least privilege and lacks permissions to execute OS commands (e.g., via `xp_cmdshell`).
- Poorly hardened databases can be pivoting points to compromise the rest of the network, linking directly to **[[08 - Network Segmentation and VLANs]]**.
- Can be chained with **[[03 - Principle of Least Privilege]]** for granular service account controls and zero-trust verification.

## Related Notes
- [[01 - Security Baselines]]
- [[02 - Defense in Depth]]
- [[07 - Firewall Rules Allowlist vs Denylist]]
- [[09 - Zero Trust Architecture]]
- [[05 - SIEM and Log Aggregation]]
