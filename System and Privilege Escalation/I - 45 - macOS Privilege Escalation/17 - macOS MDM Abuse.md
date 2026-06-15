---
tags: [macos, mdm, red-team, post-exploitation, pentesting]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.17 macOS MDM Abuse"
---

# macOS MDM Abuse

## Introduction
**MDM (Mobile Device Management)** is how organizations centrally manage Macs: enroll devices, push **configuration profiles**, install software, enforce policy, and run commands. An MDM server effectively has **root-equivalent, fleet-wide control** over every enrolled Mac. This makes MDM both a high-value target (compromise the server → own every endpoint) and a useful post-exploitation lever (abuse enrollment to push privileged payloads). MDM ties into Apple's **DEP/ABM (Device Enrollment Program / Apple Business Manager)** for zero-touch enrollment, which introduces its own trust-and-spoofing issues.

## How MDM Trust Works
```text
+---------------------------------------------------------------+
|                  MDM / DEP ENROLLMENT CHAIN                   |
+---------------------------------------------------------------+
|  Apple (ABM/DEP)                                              |
|     | device serial mapped to an organization's MDM server   |
|     v                                                         |
|  Mac at first boot (or `profiles`) asks Apple "who manages me?"|
|     | Apple returns the org's MDM enrollment URL             |
|     v                                                         |
|  Device enrolls -> MDM can push profiles, apps, commands      |
|     | profiles can: install root CAs, configure Wi-Fi/VPN,    |
|     |   set restrictions, install pkgs, run MDM commands       |
|     v                                                         |
|  MDM = root-equivalent over the device                        |
+---------------------------------------------------------------+
```
Check enrollment locally:
```bash
profiles status -type enrollment      # is it DEP/MDM enrolled?
profiles show -type enrollment
profiles list                         # installed configuration profiles
system_profiler SPConfigurationProfileDataType
```

## Abuse Scenarios
### 1. Compromise the MDM server → fleet RCE
If you breach the organization's MDM (Jamf, Mosyle, Kandji, Intune, etc.) — via web vuln, leaked admin creds, or API token — you can push a **configuration profile** or **package** to every device that runs as root. This is the macOS equivalent of owning a Windows domain's deployment system. Hunt for MDM admin consoles, API tokens in CI/secrets, and SSO access during an engagement.

### 2. DEP/enrollment spoofing (serial-number abuse)
DEP maps a **device serial number** to an org's MDM. Knowing a victim org's enrollment endpoint and a **valid serial**, a researcher can register a rogue device into the org's MDM (the "enrolling devices in other organisations" technique), receiving the org's profiles — which may include **Wi-Fi/VPN credentials, root CA certs, and internal config** pushed automatically. Conversely, an attacker who learns the MDM URL can sometimes harvest enrollment data.
```bash
# Serial is low-entropy and discoverable
system_profiler SPHardwareDataType | grep Serial
ioreg -l | grep IOPlatformSerialNumber
```

### 3. Malicious profile installation (local)
With admin/root on a host, install a **configuration profile** that weakens posture or persists:
```bash
profiles install -path evil.mobileconfig   # (older syntax; modern macOS requires UI/MDM)
```
A profile can install a **trusted root CA** (enabling TLS interception), preconfigure proxies, add restrictions, or set up managed login items — durable, "legitimate-looking" persistence (ties to [[13 - macOS Auto-Start Locations and Persistence]]). Modern macOS increasingly requires user/MDM approval for profile installation, limiting purely-local installs.

### 4. Pushed root CA → traffic interception
A profile-delivered root CA lets the controller MITM the device's TLS. Compromising MDM to push such a CA fleet-wide is a powerful interception primitive.

## Post-Compromise Value
```text
   Own one Mac      -> loot its MDM enrollment data, server URL, tokens
   Own MDM server   -> push root pkg/profile to ALL enrolled Macs
   Spoof enrollment -> pull org's pushed creds/CAs onto a rogue device
   Push root CA     -> intercept fleet TLS
```

## Why It Matters
MDM concentrates fleet-wide root authority into one web application and one trust chain. For red teams it is often the **highest-leverage target** in a Mac-heavy environment — far more efficient than per-host escalation. For defenders, MDM compromise is a worst-case incident.

## Defensive Notes
- Lock down the MDM console: SSO + MFA, least-privilege admin roles, rotate API tokens, monitor profile/command pushes.
- Treat enrollment URLs and serial lists as sensitive; use ABM/DEP with strict device assignment and monitor for unexpected enrollments.
- Restrict who can install configuration profiles; alert on new root CAs and unexpected profiles (`profiles list`).
- Review pushed profiles for embedded credentials; prefer per-device, short-lived secrets over static ones in profiles.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[13 - macOS Auto-Start Locations and Persistence]]
- [[15 - macOS Sensitive Locations and Credential Theft]]
- [[04 - TCC Transparency Consent and Control]]
