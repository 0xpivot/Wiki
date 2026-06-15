---
tags: [windows, privesc, ntlm, relay, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.44 Local NTLM Reflection and Relay"
---

# Local NTLM Reflection and Relay

## Introduction
NTLM relay is usually thought of as a *network* attack, but several techniques **relay or reflect NTLM authentication locally on a single host** to escalate from a low-privileged user to SYSTEM. The general idea: **coerce a privileged local component (or the SYSTEM account itself) into authenticating with NTLM to a listener the attacker controls, then relay that authentication to a local privileged service** (SMB, RPC/`ncacn_np`, LDAP-to-local, or DCOM activation) to act with the coerced identity. This family includes the "Potato"-adjacent local-auth-coercion attacks and local SMB reflection. It complements the Potato techniques already covered ([[10 - JuicyPotato RoguePotato PrintSpoofer]], [[11 - Hot Potato Sweet Potato Ghost Potato]]).

## Core Concept: Coerce → Relay Locally
```text
+---------------------------------------------------------------+
|              LOCAL NTLM REFLECTION / RELAY                    |
+---------------------------------------------------------------+
|  1. Attacker (low-priv, often with SeImpersonate) starts a    |
|     local listener (SMB / RPC named pipe / HTTP)              |
|        |                                                       |
|  2. COERCE a SYSTEM-context component to authenticate to it   |
|     - DCOM/RPC activation tricks (Potato-style)               |
|     - the SYSTEM account / a service performing NTLM          |
|        |                                                       |
|  3. RELAY that NTLM auth to a local privileged endpoint       |
|     - local SMB (\\127.0.0.1) -> file write / service install |
|     - local RPC/SCM, LDAP, DCOM -> privileged action          |
|        |                                                       |
|  4. Action executes as the relayed (SYSTEM/admin) identity    |
+---------------------------------------------------------------+
```
Historically, **reflecting** NTLM straight back to the *same* host (SMB→SMB) was the original attack; Microsoft mitigated naive SMB→SMB reflection (MS08-068, and later CVE-2019-1384/"Ghost Potato" reintroduced variants). Modern local relay shifts the **target protocol** (e.g. authenticate over RPC/named pipe, relay to a *different* local service such as AD CS web enrollment, LDAP, or SMB on a different binding) to dodge same-protocol reflection protections.

## Notable Variants
- **Local SMB reflection (classic):** coerce SYSTEM to authenticate over SMB and reflect to local SMB to write files / create a service as SYSTEM. Largely mitigated for same-protocol, but resurfaces via bugs.
- **`local-ntlm-reflection-via-smb-arbitrary-port`:** trick the SMB authentication to occur against an attacker-chosen port/binding so it can be relayed where reflection guards don't apply.
- **RemotePotato0-style cross-protocol:** coerce a DCOM/RPC NTLM authentication and relay it cross-protocol (e.g. to LDAP) — on a domain-joined host this can target the local machine's privileged actions.
- **Potato lineage** (`RoguePotato`, `PrintSpoofer`, `JuicyPotato`): closely related local coercion+impersonation primitives leveraging `SeImpersonatePrivilege` — see [[10 - JuicyPotato RoguePotato PrintSpoofer]].

## Preconditions and Enumeration
- Frequently relies on **`SeImpersonatePrivilege`** (held by service accounts: IIS `AppPool`, MSSQL, many service identities) — check `whoami /priv`. With it, coerced SYSTEM auth can be turned into a SYSTEM token.
- Domain membership widens cross-protocol targets (LDAP, AD CS).
- Patch level matters: each reflection guard (SMB signing, EPA/Channel Binding, same-protocol reflection blocks) closes specific variants.

```cmd
whoami /priv                  :: SeImpersonatePrivilege present?
:: check SMB signing / mitigations posture
reg query "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v RequireSecuritySignature
```

## Exploitation Outline
1. Confirm `SeImpersonatePrivilege` (or another coercion primitive).
2. Stand up the local listener (rogue SMB/RPC/OXID resolver, per the chosen tool).
3. Coerce SYSTEM/service NTLM auth (DCOM activation, spooler/`MS-RPRN`, `MS-EFSR`/PetitPotam-style locally, etc.).
4. Relay to a privileged local endpoint that yields code execution (service creation, file write to a privileged path, AD CS cert for the machine account → DCSync/ticket).
5. Execute as SYSTEM.

## Why It Matters in an Engagement
Service accounts with `SeImpersonatePrivilege` (web/db servers) are extremely common footholds. Local NTLM reflection/relay is the canonical "service account → SYSTEM" jump, and the cross-protocol variants keep working as same-protocol reflection gets patched. Understanding it explains why `SeImpersonatePrivilege` is treated as nearly SYSTEM-equivalent.

## Detection and Mitigation
- **Enable SMB signing** and **LDAP signing + channel binding (EPA)** to block relay to those services; enforce same-protocol reflection protections (keep patched).
- Restrict `SeImpersonatePrivilege` to trusted accounts; isolate web/db service accounts.
- Disable the Print Spooler / coercion vectors where unused; deploy RPC filters.
- Monitor for loopback NTLM auth, unexpected local service creation, and DCOM activation by service accounts.

## Chaining Opportunities
- Same precondition (`SeImpersonate`) as the Potato family — [[10 - JuicyPotato RoguePotato PrintSpoofer]], [[11 - Hot Potato Sweet Potato Ghost Potato]].
- Relayed machine-account auth → AD CS / [[20 - Pass the Hash on Local Admin]] and lateral movement.

## Related Notes
- [[10 - JuicyPotato RoguePotato PrintSpoofer]]
- [[11 - Hot Potato Sweet Potato Ghost Potato]]
- [[09 - Token Impersonation]]
- [[28 - Named Pipe Impersonation]]
