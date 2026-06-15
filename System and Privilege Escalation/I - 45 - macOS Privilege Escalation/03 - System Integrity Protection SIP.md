---
tags: [macos, privesc, sip, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.03 System Integrity Protection (SIP)"
---

# System Integrity Protection (SIP)

## Introduction
**System Integrity Protection (SIP)**, also called **rootless**, was introduced in OS X 10.11 (El Capitan) to constrain what the all-powerful `root` user can do. Before SIP, compromising root on macOS gave total control: an attacker could tamper with system binaries, load arbitrary kernel extensions, and persist invisibly. SIP changes that contract — even UID 0 cannot modify SIP-protected paths, attach to protected processes, or load unsigned kexts. It is enforced by the kernel itself, not by user-space permissions.

For an attacker, SIP is often the single most important fact about a host: with SIP **enabled**, root is a means to an end but not the end; with SIP **disabled** (a surprisingly common developer/lab misconfiguration), the system is wide open to durable kernel-level compromise.

## What SIP Protects
SIP enforces several distinct restrictions, each toggled by a flag in NVRAM (`csr-active-config`):

```text
+---------------------------------------------------------------+
|                    SIP PROTECTION DOMAINS                     |
+---------------------------------------------------------------+
| Filesystem protection                                         |
|   - /System, /usr (except /usr/local), /bin, /sbin, certain   |
|     apps in /Applications are read-only even to root          |
|   - Marked by the "restricted" flag (com.apple.rootless xattr |
|     or entry in /System/Library/Sandbox/rootless.conf)        |
+---------------------------------------------------------------+
| Runtime / process protection                                  |
|   - Cannot task_for_pid() or attach a debugger to protected   |
|     (Apple-signed, restricted) processes                      |
|   - Cannot inject code (DYLD_*) into protected binaries       |
+---------------------------------------------------------------+
| Kernel extension restriction                                  |
|   - Only validly-signed kexts may load (ties into AMFI)       |
+---------------------------------------------------------------+
| NVRAM protection                                              |
|   - Certain NVRAM variables cannot be modified                |
+---------------------------------------------------------------+
```

## Checking SIP Status
```bash
csrutil status
# "System Integrity Protection status: enabled."
nvram csr-active-config            # raw config bitmask (base64/hex)
ls -lO /System/Applications/Safari.app   # 'restricted' flag visible via -O
```
The `restricted` keyword in `ls -lO` output marks a SIP-protected file. The `com.apple.rootless` extended attribute also denotes protected items.

## Legitimately Toggling SIP
SIP can only be changed from **Recovery Mode** (the bitmask lives in NVRAM, which is itself protected at runtime):

```bash
# In Recovery (Cmd-R at boot), Terminal:
csrutil disable
csrutil enable --without kext      # selectively disable just kext signing
reboot
```
This requires **physical access / boot control** — it is not a remote technique. This is exactly why SIP is effective: an attacker with a remote root shell still cannot toggle it without rebooting into Recovery, which is loud and usually impossible remotely.

## Attacker Perspective: SIP Bypasses
Because SIP is so valuable to defeat, a long line of CVEs has targeted it. The recurring theme is **an Apple-entitled process being tricked into performing a privileged filesystem operation on the attacker's behalf**, since some Apple daemons hold the `com.apple.rootless.install` (or `.heritable`) entitlement that lets them write to protected locations.

Historically significant classes:
- **Shrootless (CVE-2021-30892):** `system_installer` ran post-install scripts from packages; because it was entitled to bypass SIP, an attacker-controlled post-install script inherited that power and could write to `/System` (e.g. drop a persistent file or disable other protections). Patched by sandboxing the child.
- **`com.apple.rootless.install.heritable` abuse:** any process spawned by an entitled installer daemon could inherit SIP-bypass capability if the daemon didn't drop it — recurring pattern across several CVEs.
- **Migration / `diskutil` / `fsck` style daemons:** entitled maintenance tools that accept attacker-influenceable paths.

```text
   Attacker (root, SIP on)            Apple daemon
   |  cannot write /System            |  holds com.apple.rootless.install
   |                                  |  (CAN write /System)
   |---- craft input the daemon ----->|
   |     processes (pkg script,       |
   |     symlink, path arg)           |
   |                                  |--- daemon writes to /System
   |                                  |    using its entitlement
   |<--- protected file modified -----|
   SIP effectively bypassed without touching csr-active-config
```

The practical takeaway: SIP bypasses are **logic bugs in entitled Apple components**, patched individually. On a fully-updated system they are scarce; on an out-of-date system, match `sw_vers` against known SIP-bypass CVEs.

## Why It Matters in an Engagement
- **Persistence:** without a SIP bypass, you cannot hide implants in `/System` or load a malicious kext — persistence is confined to user/Library launch items, which are far more detectable.
- **Disabling other defenses:** writing to protected locations can let you neuter TCC, AMFI configs, or planted EDR.
- **Reporting:** finding SIP **disabled** on a production endpoint is itself a high-severity finding.

## Defensive Notes
- Verify `csrutil status` reports **enabled** across the fleet via MDM compliance checks; flag any host with it disabled.
- Keep macOS patched — SIP bypasses are CVE-driven and fixed promptly by Apple.
- Monitor for unexpected modification of `/System`, `/usr`, and rootless.conf, and for kext load attempts.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[07 - AMFI and Launch Constraints]]
- [[09 - Dangerous Entitlements]]
- [[16 - macOS Installers and Package Abuse]]
