---
tags: [linux, privesc, selinux, mac, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.37 SELinux Enumeration and Bypass"
---

# SELinux Enumeration and Bypass

## Introduction
**SELinux (Security-Enhanced Linux)** is a Mandatory Access Control (MAC) framework layered on top of standard Unix DAC permissions, default on RHEL/CentOS/Fedora and available elsewhere. Where DAC asks "does this *user* own/have permission?", SELinux asks "does this *security context* (domain) have a policy rule allowing this action on this object's type?". For an attacker this matters in two directions: SELinux can **block an otherwise-successful privesc** (e.g. you got root but a confined domain stops you), and **misconfigured/permissive SELinux** removes a layer defenders assumed was protecting them. Understanding contexts and modes is essential when operating on hardened RHEL-family hosts.

## Core Concepts
Every process and file has a **security context**: `user:role:type:level`, e.g. `system_u:system_r:httpd_t:s0`. Policy rules (type enforcement) say which **domains** (process types, `*_t`) may access which **types** (object labels). A web server running as `httpd_t` can only touch files labelled for it — even as root — unless policy allows it.

```text
+---------------------------------------------------------------+
|                 DAC vs MAC (SELinux)                         |
+---------------------------------------------------------------+
|  Operation must pass BOTH:                                    |
|    1. DAC  (uid/gid/mode/ACL)  -- traditional Unix            |
|    2. MAC  (SELinux type-enforcement policy)                  |
|                                                               |
|  => even ROOT in a confined domain (e.g. httpd_t) is limited  |
|     to what policy permits.                                   |
+---------------------------------------------------------------+
```

## Enumeration
```bash
getenforce                 # Enforcing / Permissive / Disabled
sestatus                   # full status, policy name, mode
id -Z                      # your process's SELinux context
ps -eZ                     # contexts of running processes
ls -Z /path                # file/object labels
getsebool -a               # tunable booleans (many loosen policy)
semanage boolean -l 2>/dev/null
ausearch -m avc -ts recent # recent AVC denials (what SELinux blocked)
sesearch --allow 2>/dev/null  # query allow rules (policy analysis)
```
**Key checks:**
- `getenforce` → **Permissive** or **Disabled** means SELinux logs but does **not block** — effectively off for the attacker.
- Dangerous **booleans** enabled (e.g. `httpd_can_network_connect`, `httpd_execmem`, `allow_execstack`) widen what a confined service can do.
- Your domain: if you landed as an *unconfined* domain (`unconfined_t`), SELinux barely restricts you.

## Bypass / Weakness Patterns
### 1. Permissive mode / disabled
The simplest "bypass" — SELinux isn't enforcing. Confirm with `getenforce`; if Permissive, proceed as on a non-SELinux box (denials are only logged).

### 2. Unconfined domains
Many interactive logins run as `unconfined_t`, which has near-DAC-only restrictions. If your shell is unconfined, standard privesc techniques work; SELinux mainly confines *services* (`httpd_t`, `mysqld_t`), so a service foothold is more constrained than a user shell.

### 3. Permissive domains
`semanage permissive -l` shows individual domains set permissive even while the system is Enforcing — those domains are unprotected.

### 4. Dangerous booleans
Enabled tunables can permit memory execution, network connections, or file access that policy would otherwise deny — turning a confined service compromise into a fuller one. Enumerate with `getsebool -a`.

### 5. Transition to a less-confined domain
If policy allows your domain to execute a binary that transitions to a more privileged/unconfined domain (a `type_transition` rule), invoking it escalates your effective domain. Analyze with `sesearch`.

### 6. Disable it (with root)
If you reach root and SELinux blocks your next step, root can often **set permissive at runtime**:
```bash
setenforce 0          # requires root + not locked by policy/booleans
# persistent: edit /etc/selinux/config (SELINUX=disabled) + reboot
```
Note: a well-configured policy can deny even root the ability to `setenforce 0` (via `secure_mode_policyload`), so this isn't guaranteed.

## Why It Matters in an Engagement
On RHEL-family targets, SELinux frequently explains *why a known privesc failed* — your exploit ran but the confined domain blocked the payoff. Recognising the mode/domain tells you whether to pivot (find an unconfined path, abuse a boolean, escape via a transition) or whether the box is effectively unprotected (Permissive/Disabled — a finding in itself).

## Detection and Mitigation
- Keep SELinux **Enforcing** with the **targeted** (or stricter) policy; alert on `setenforce 0` and config changes.
- Audit booleans — disable unnecessary loosening tunables; avoid permissive domains in production.
- Run services in **confined** domains; review `ausearch -m avc` denials rather than relabeling/permissive-ing problems away.
- Lock policy reload/`setenforce` against root where feasible.

## Chaining Opportunities
- SELinux confinement is what makes container/runtime escapes ([[36 - Container Runtime PrivEsc containerd runc]]) and service abuse harder; bypassing it unlocks those.
- Pairs with kernel exploits ([[23 - Kernel Exploits]]) — kernel-level code execution sidesteps MAC entirely.

## Related Notes
- [[36 - Container Runtime PrivEsc containerd runc]]
- [[23 - Kernel Exploits]]
- [[01 - Linux PrivEsc Methodology Overview]]
- [[35 - Defense File Permission Hardening]]
