---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.11 SSH Protocol Basics and Key Authentication"
---

# 70.11 SSH Protocol Basics and Key Authentication

## 1. Overview and Architecture
Secure Shell (SSH) replaces legacy plaintext protocols (Telnet, rlogin). It operates on TCP port 22.
SSH-2 (RFC 4251) is the modern standard, dividing the protocol into three layers:
1. **Transport Layer:** Handles initial key exchange (KEX), server authentication, and bulk encryption.
2. **User Authentication Layer:** Handles client credentials (passwords, keys).
3. **Connection Layer:** Multiplexes the encrypted tunnel into multiple channels.

## 2. Cryptographic Process and Key Exchange
The SSH connection sequence:
1. TCP Handshake.
2. Version Exchange (`SSH-2.0-OpenSSH...`).
3. Algorithm Negotiation (`SSH_MSG_KEXINIT`): Client and server agree on KEX, encryption, and MAC algorithms.
4. Diffie-Hellman Key Exchange: Derives a shared secret.
5. Server Authentication: Server signs the exchange hash with its host key (e.g., Ed25519 or RSA). Client verifies.
6. `SSH_MSG_NEWKEYS`: Both sides switch to symmetric encryption.

## 3. Authentication Mechanisms
- **Password:** Sends plaintext inside the encrypted tunnel. Vulnerable to brute force.
- **Public Key:** The client signs a challenge using their private key. The server verifies it against `~/.ssh/authorized_keys`.
- **Host-Based:** Authenticates based on the client host's identity.

## 4. SSH Tunneling and Port Forwarding
- **Local (-L):** Forwards local port to remote resource. `ssh -L 8080:internal.db:3306 user@bastion`
- **Remote (-R):** Forwards remote port to local resource (Reverse Shell). `ssh -R 4444:localhost:22 user@c2`
- **Dynamic (-D):** SOCKS Proxy. `ssh -D 9050 user@bastion`

## 5. ASCII Diagram: SSH Handshake
```text
  [Client]                                     [Server]
     |                 TCP SYN                    |
     |------------------------------------------->|
     |               TCP SYN-ACK                  |
     |<-------------------------------------------|
     |                 TCP ACK                    |
     |------------------------------------------->|
     |         Version Exchange (SSH-2.0)         |
     |<==========================================>|
     |      KEXINIT (Algorithm Negotiation)       |
     |<==========================================>|
     |          DH Key Exchange Init              |
     |------------------------------------------->|
     |          DH Reply + Server Sign            |
     |<-------------------------------------------|
     |              NEWKEYS                       |
     |<==========================================>|
     |      [ ENCRYPTED TUNNEL ESTABLISHED ]      |
     |              Auth Request                  |
     |------------------------------------------->|
     |              Auth Success                  |
     |<-------------------------------------------|
```

## 6. VAPT Context and Exploitation
- **Brute Force:** Hydra/Medusa targeting port 22.
- **Key Harvesting:** Stealing `id_rsa` or `id_ed25519`.
- **Authorized Keys:** Adding attacker public key to target's `authorized_keys`.
- **Agent Hijacking:** Exploiting `ssh-agent` sockets on compromised hosts when users use ForwardAgent (`-A`).

## Chaining Opportunities
- **Lateral Movement:** Pivot through compromised segments using [[11 - SSH Protocol Basics and Key Authentication]].
- **Payload Delivery:** Combine with [[12 - SMTP POP3 and IMAP Email Protocols]] for access.
- **Recon:** Findings feed into [[13 - SNMP Protocol Basics and Community Strings]].
- **Evasion:** Bypasses [[14 - Firewalls IDS IPS and NAT Explained]].
- **VPNs:** Compare with [[15 - VPNs IPsec and Tunneling Basics]].

## Related Notes
- [[11 - SSH Protocol Basics and Key Authentication]]
- [[12 - SMTP POP3 and IMAP Email Protocols]]
- [[13 - SNMP Protocol Basics and Community Strings]]
- [[14 - Firewalls IDS IPS and NAT Explained]]
- [[15 - VPNs IPsec and Tunneling Basics]]

## 7. Extended Configuration Reference (`sshd_config`)
The following configuration provides an extensively hardened template for OpenSSH, ensuring maximum resilience against modern cryptographic attacks and unauthorized access attempts.

```text
# General settings
Port 2222
ListenAddress 0.0.0.0
ListenAddress ::
Protocol 2

# Host Keys
HostKey /etc/ssh/ssh_host_ed25519_key
HostKey /etc/ssh/ssh_host_rsa_key

# Logging
SyslogFacility AUTHPRIV
LogLevel VERBOSE

# Authentication Restrictions
LoginGraceTime 30s
PermitRootLogin prohibit-password
StrictModes yes
MaxAuthTries 3
MaxSessions 5

# Key-based Auth
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Disable weak auth
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes
KerberosAuthentication no
GSSAPIAuthentication no
HostbasedAuthentication no

# Forwarding Controls
AllowAgentForwarding no
AllowTcpForwarding local
GatewayPorts no
X11Forwarding no
PermitTunnel no

# Environment and UI
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
PermitUserEnvironment no
Compression delayed
ClientAliveInterval 300
ClientAliveCountMax 0

# Modern Cryptography Requirements
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com

# Access Control
AllowUsers admin ops deploy
DenyUsers root guest apache www-data

# SFTP Configuration
Subsystem sftp internal-sftp -l INFO -f AUTH

# Match Blocks for specific overrides
Match User deploy
    AllowTcpForwarding no
    X11Forwarding no
    PermitTTY no
    ForceCommand internal-sftp

Match Address 192.168.1.0/24
    PasswordAuthentication yes

Match Group wheel
    AllowAgentForwarding yes

# Advanced Hardening
UseDNS no
PidFile /var/run/sshd.pid
MaxStartups 10:30:100
ChrootDirectory none
VersionAddendum none
IgnoreUserKnownHosts yes
IgnoreRhosts yes
GSSAPICleanupCredentials yes
UsePrivilegeSeparation sandbox
KeyRegenerationInterval 1h
ServerKeyBits 4096
RhostsRSAAuthentication no
RSAAuthentication yes
UseLogin no
MaxConnectionsPerChild 1
FingerprintHash sha256
ExposeAuthInfo no
RevokedKeys /etc/ssh/revoked_keys
AuthorizedPrincipalsFile none
TrustedUserCAKeys none
HostCertificate none
AcceptEnv LANG LC_*
DisableForwarding yes
PermitListen none
PermitOpen any
```
