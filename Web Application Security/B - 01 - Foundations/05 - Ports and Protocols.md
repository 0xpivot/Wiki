---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.05 Ports and Protocols"
---

# 01.05 — Ports and Protocols

## What is it?

A **port** is a numbered door on a device. An **IP address** gets you to the right house; the **port** gets you to the right room.

A **protocol** is a set of rules that defines how two computers communicate — the language they speak.

```
[Your Browser]  ──→  142.250.182.46 : 443
                     └── IP address  └── Port (HTTPS)

Same IP, different port = different service:
142.250.182.46:80   → HTTP (web, unencrypted)
142.250.182.46:443  → HTTPS (web, encrypted)
```

---

## Port Ranges

```
0     – 1023    Well-known ports (standard services, needs root to bind)
1024  – 49151   Registered ports (applications)
49152 – 65535   Dynamic/Ephemeral ports (temporary, used by clients)

When your browser connects to google.com:443
  Source port: 54231 (random ephemeral port — your browser picks this)
  Dest port:   443   (HTTPS — Google listens here)
```

---

## Complete Port Reference for VAPT

### Critical Ports — Memorise These

```
PORT    PROTOCOL   SERVICE        PENTEST SIGNIFICANCE
────────────────────────────────────────────────────────────────────
21      TCP        FTP            Cleartext creds, anonymous login
22      TCP        SSH            Brute force, key auth, pivoting
23      TCP        Telnet         Cleartext everything — dead simple MITM
25      TCP        SMTP           Email relay, user enumeration (VRFY)
53      TCP/UDP    DNS            Zone transfer, DNS rebinding, tunneling
67/68   UDP        DHCP           Rogue DHCP → MITM all traffic
69      UDP        TFTP           No auth, often has config files
80      TCP        HTTP           Web attacks (full web vuln set)
88      TCP        Kerberos       Kerberoasting, AS-REP, ticket attacks
110     TCP        POP3           Email access, cleartext creds
111     TCP/UDP    RPCBind        NFS enumeration
135     TCP        MSRPC          Windows RPC, lateral movement
137-139 TCP/UDP    NetBIOS        NBNS poisoning, enumeration
143     TCP        IMAP           Email access
161/162 UDP        SNMP           Info disclosure, community strings
389     TCP/UDP    LDAP           AD enumeration, injection
443     TCP        HTTPS          Web attacks over TLS
445     TCP        SMB            EternalBlue, relay, null session
465/587 TCP        SMTPS/SMTP     Email with TLS
512-514 TCP        rsh/rexec/rlogin  Legacy remote exec, no auth
548     TCP        AFP            Apple file sharing
587     TCP        SMTP Submission  Email sending (modern)
631     TCP        IPP            Printer — often has web UI
636     TCP        LDAPS          LDAP over TLS
873     TCP        Rsync          Backup tool — often unauthenticated
902     TCP        VMware ESXi    Hypervisor management
993     TCP        IMAPS          IMAP over TLS
995     TCP        POP3S          POP3 over TLS
1080    TCP        SOCKS          Proxy, pivoting
1433    TCP        MSSQL          SQL Server, xp_cmdshell → RCE
1521    TCP        Oracle DB      Database attacks
2049    TCP/UDP    NFS            File share, root squash abuse
2181    TCP        Zookeeper      Unauthenticated access
2375    TCP        Docker API     Exposed daemon → container escape
2376    TCP        Docker TLS     Docker with TLS
3306    TCP        MySQL          Database attacks, UDF RCE
3389    TCP        RDP            Brute force, BlueKeep, session hijack
3690    TCP        SVN            Source code access
4443    TCP        HTTPS Alt      Dev servers
4444    TCP        Metasploit     Default reverse shell listener
5000    TCP        Various        Flask dev, Docker registry
5432    TCP        PostgreSQL     Database attacks
5601    TCP        Kibana         Elasticsearch frontend
5900    TCP        VNC            Screen sharing — often no auth
5985    TCP        WinRM HTTP     PowerShell remoting
5986    TCP        WinRM HTTPS    PowerShell remoting (TLS)
6379    TCP        Redis          Unauthenticated access → RCE
6443    TCP        Kubernetes API  K8s cluster — RBAC bypass
7001    TCP        WebLogic       Java deserialization CVEs
8009    TCP        AJP (Tomcat)   Ghostcat (CVE-2020-1938)
8080    TCP        HTTP Alt       App servers, proxies
8443    TCP        HTTPS Alt      App servers with TLS
8500    TCP        Consul         Service mesh — unauthenticated
8888    TCP        Jupyter        Notebooks — code execution
9000    TCP        PHP-FPM        FastCGI — RCE if exposed
9090    TCP        Prometheus     Metrics — info disclosure
9200    TCP        Elasticsearch  Open access — data exfil
9300    TCP        Elasticsearch  Cluster comms
10250   TCP        Kubelet API    Kubernetes node agent
11211   TCP/UDP    Memcached      Amplification, data dump
27017   TCP        MongoDB        Unauthenticated access
50000   TCP        SAP            SAP management console
```

---

## TCP vs UDP — The Two Main Protocols

```
TCP (Transmission Control Protocol) — Reliable
┌────────────────────────────────────────────────┐
│  • Connection-oriented (3-way handshake first) │
│  • Guarantees delivery (retransmits lost data) │
│  • Data arrives in order                        │
│  • Slower (overhead for reliability)            │
│  • Used for: HTTP, HTTPS, SSH, FTP, SMTP       │
└────────────────────────────────────────────────┘

UDP (User Datagram Protocol) — Fast
┌────────────────────────────────────────────────┐
│  • Connectionless (just sends, no handshake)   │
│  • No guaranteed delivery                       │
│  • No ordering                                  │
│  • Faster (no overhead)                         │
│  • Used for: DNS, DHCP, VoIP, games, video     │
└────────────────────────────────────────────────┘
```

**VAPT implication:** Nmap scans TCP by default. Add `-sU` for UDP scanning — often finds hidden services:
```bash
nmap -sU -p 53,67,68,69,161,162 target
```

---

## Hands-On: Port Commands

```bash
# See what ports are open on YOUR machine
ss -tulnp              # Linux (preferred)
netstat -tulnp         # Linux (older)
netstat -ano           # Windows

# Sample ss output:
# Netid  State   Recv-Q  Send-Q  Local Address:Port
# tcp    LISTEN  0       128     0.0.0.0:22        ← SSH listening
# tcp    LISTEN  0       80      0.0.0.0:80        ← HTTP listening
# tcp    LISTEN  0       128     127.0.0.1:3306    ← MySQL (local only)

# Connect to a port manually (test if open)
nc -zv 192.168.1.1 22       ← test if SSH is open
nc -zv 192.168.1.1 80       ← test if HTTP is open

# Scan ports with Nmap (VAPT)
nmap -p 22,80,443 target
nmap -p- target              ← all 65535 ports (slow but thorough)
nmap -p 1-1000 target
nmap --top-ports 1000 target ← most common 1000 ports
```

---

## Security Context — Ports in VAPT

### 1. Open Port = Attack Surface

Every open port is a potential entry point.

```
nmap scan result:
PORT     STATE  SERVICE
22/tcp   open   ssh       ← try default/weak passwords, key reuse
80/tcp   open   http      ← web app testing
443/tcp  open   https     ← web app testing  
3306/tcp open   mysql     ← try default root: (no password)
6379/tcp open   redis     ← try unauthenticated access
```

### 2. Unexpected Ports = Misconfiguration

```
Finding port 8500 open (Consul) → service mesh might allow
  registering malicious services

Finding port 9200 open (Elasticsearch) → run:
  curl http://target:9200/_cat/indices    ← list all databases
  curl http://target:9200/_all/_search    ← dump all data

Finding port 2375 open (Docker API) → run:
  docker -H tcp://target:2375 ps          ← list containers
  docker -H tcp://target:2375 run -v /:/host ubuntu chroot /host
  ← mount host filesystem → full system compromise
```

### 3. Port Knocking

Some systems hide services behind port knocking — knock on specific ports in sequence to open another.

```bash
# Knock on ports 1234, 5678, 9012 to open port 22
knock target 1234 5678 9012
nc -zv target 22             ← now SSH is open
```

### 4. Firewall Bypass via Allowed Ports

If firewall blocks most ports but allows 80/443:
```bash
# Run SSH on port 443 (bypass firewall)
ssh user@target -p 443

# HTTP tunneling — wrap traffic in HTTP
# Chisel, reGeorg, Neo-reGeorg over port 80/443
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Unnecessary open ports | Close with firewall — deny all, allow specific |
| Cleartext services (Telnet, FTP) | Replace with SSH, SFTP |
| Services listening on 0.0.0.0 | Bind to specific IP (127.0.0.1 if local-only) |
| Default ports → easy fingerprinting | Change SSH to non-standard port (security by obscurity — minor benefit) |
| No monitoring of open ports | Regular port scans of your own infrastructure |

---

## Related Notes
- [[01 - What is a Network]] — networking basics
- [[06 - TCP Three-Way Handshake]] — how TCP connections work
- [[21 - Port Scanning with Nmap]] — scanning ports in VAPT
- [[Module 35 - Network Protocol Attacks]] — exploiting specific services
