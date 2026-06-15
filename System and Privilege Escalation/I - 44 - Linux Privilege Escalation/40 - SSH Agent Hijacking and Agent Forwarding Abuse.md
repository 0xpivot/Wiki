---
tags: [linux, privesc, ssh, lateral-movement, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.40 SSH Agent Hijacking and Agent Forwarding Abuse"
---

# SSH Agent Hijacking and Agent Forwarding Abuse

## Introduction
The **SSH agent** (`ssh-agent`) holds a user's decrypted private keys in memory so they don't have to retype a passphrase for every connection. **Agent forwarding** (`ssh -A` / `ForwardAgent yes`) extends this: when you SSH into a remote host with forwarding on, that host can use your *local* agent to authenticate onward — convenient for hopping through bastions, but a serious security hazard. If an attacker controls (or gains root on) a host where someone has forwarded their agent, they can **hijack the agent socket** and authenticate as that user to anywhere their keys are accepted — without ever seeing the private key. This is primarily a **lateral-movement / credential-abuse** technique but is a classic finding during Linux post-exploitation.

## How Agent Forwarding Exposes You
```text
+---------------------------------------------------------------+
|              SSH AGENT FORWARDING RISK                       |
+---------------------------------------------------------------+
|  Workstation (keys in ssh-agent)                              |
|     |  ssh -A user@jump                                       |
|     v                                                         |
|  Jump host:  $SSH_AUTH_SOCK -> a forwarded socket back to     |
|              the workstation's agent                          |
|     |                                                         |
|  Attacker who is ROOT (or the same uid) on the jump host can  |
|  read $SSH_AUTH_SOCK and ASK the agent to sign challenges     |
|     v                                                         |
|  -> authenticates as the victim to ANY host accepting the     |
|     forwarded keys, WITHOUT the private key material          |
+---------------------------------------------------------------+
```
The agent never reveals the key; it only *signs*. But signing is all SSH auth needs, so socket access == the ability to log in as the victim.

## Finding and Hijacking an Agent Socket
```bash
# Look for live agent sockets (forwarded or local)
ls -la /tmp/ssh-*/agent.* 2>/dev/null
find /tmp -type s -name 'agent.*' 2>/dev/null
env | grep SSH_AUTH_SOCK
# As root, find other users' agent sockets and their owners
lsof 2>/dev/null | grep agent
```
To hijack, point your SSH client at the victim's socket and list/use the keys:
```bash
export SSH_AUTH_SOCK=/tmp/ssh-XXXX/agent.1234   # victim's socket
ssh-add -l                       # list keys the agent holds (fingerprints)
ssh victim@internal-target       # authenticate AS the victim, no key needed
```
As **root** you can access any user's agent socket (file perms are user-owned, but root overrides DAC). As the **same uid**, you can access that user's own socket directly.

## Related SSH Key Vectors
- **Plaintext / reused private keys** on disk (`~/.ssh/id_*`) — covered in [[17 - SSH Private Key Reuse]]; agent hijacking is the "no key on disk needed" cousin.
- **`known_hosts` and config** reveal onward targets and usernames for pivoting.
- **`authorized_keys` tampering** (if writable) is persistence, not hijacking.

## Why It Matters in an Engagement
On a compromised bastion/jump host, agent hijacking is often the **fastest lateral-movement** primitive: administrators routinely forward agents through jump boxes, so root on the jump box silently grants their access to the entire fleet those keys reach — frequently including privileged accounts. It leaves little trace (legitimate-looking SSH auth) and never exposes the key for rotation detection.

## Detection and Mitigation
- **Do not use `ForwardAgent`/`-A` to untrusted hosts.** Prefer **`ProxyJump` (`-J`)**, which tunnels the connection without exposing the agent on the intermediate host.
- Use **`ssh-add -c`** (confirmation) and **`-t` lifetimes** so each signing requires interaction / keys expire.
- On servers, set `AllowAgentForwarding no` where not required; segment bastions.
- Monitor for `SSH_AUTH_SOCK` access by other uids/root and for unexpected onward SSH from jump hosts.

## Chaining Opportunities
- Root on a jump host ([[23 - Kernel Exploits]], any privesc here) → harvest forwarded agents → lateral movement.
- Combine with [[17 - SSH Private Key Reuse]] and [[16 - Password in Config Files History Env Vars]] for broader credential capture.

## Related Notes
- [[17 - SSH Private Key Reuse]]
- [[16 - Password in Config Files History Env Vars]]
- [[30 - Tmux Screen Session Hijacking]]
- [[01 - Linux PrivEsc Methodology Overview]]
