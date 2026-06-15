---
tags: [windows, privesc, services, pentesting, red-team]
difficulty: intermediate
module: "43 - Windows Privilege Escalation"
topic: "43.42 Service Trigger Abuse"
---

# Service Trigger Abuse

## Introduction
Windows services can be configured to start not only "Automatic" or "Manual", but also on **triggers** — events such as a device arrival, an IP address becoming available, a named-pipe connection, an ETW event, a domain join, or a custom firewall-port event. **Service trigger abuse** is the technique of *firing these triggers as a low-privileged user to start (or restart) a SYSTEM service on demand*. This matters because many privilege-escalation primitives require a privileged service to **launch at a controlled moment** — e.g. so it loads a planted DLL, re-reads a modified binary, or connects to an attacker's named pipe for impersonation. Triggers give an unprivileged user that control even when they lack `SC_MANAGER`/`SERVICE_START` rights on the service directly.

## Background: Trigger-Started Services
A service's start triggers are queried with:
```cmd
sc qtriggerinfo <ServiceName>
```
Common trigger types and how an unprivileged user can fire them:

```text
+---------------------------------------------------------------+
|                 SERVICE START TRIGGER TYPES                   |
+---------------------------------------------------------------+
| NETWORK ENDPOINT (RPC/named pipe) | connect to the pipe/EP    |
| FIREWALL PORT EVENT               | open/close the port       |
| IP ADDRESS AVAILABILITY           | bring up/down an address  |
| ETW PROVIDER / CUSTOM EVENT       | emit the event            |
| DEVICE INTERFACE ARRIVAL          | plug/emulate device       |
| DOMAIN JOIN / GROUP POLICY        | (less attacker-controlled)|
+---------------------------------------------------------------+
```
The most useful for local attackers are **named-pipe / RPC endpoint** triggers and **firewall-port** triggers, both of which a normal user can cause without admin rights.

## Why Starting a Service Helps Escalate
Starting a SYSTEM service at a chosen time is the missing link in several chains:

```text
   You modified the service binary / a DLL it loads, but the
   service is already running (won't reload), and you can't
   `sc stop`/`sc start` it (no rights).
        |
        v
   Fire its START TRIGGER  ->  SCM starts a fresh instance as SYSTEM
        |
        v
   New process loads your planted binary/DLL  ->  SYSTEM code exec
```
It is also the trigger half of **named-pipe impersonation** (see [[28 - Named Pipe Impersonation]]): you create a pipe the service connects to, fire the trigger so the SYSTEM service connects, then impersonate it.

## Exploitation Workflow
1. **Enumerate trigger-started services** and their triggers:
   ```cmd
   for /f "tokens=2" %s in ('sc query state^= all ^| findstr SERVICE_NAME') do @sc qtriggerinfo %s 2>nul | findstr /i "START TRIGGER"
   ```
2. **Identify a SYSTEM service whose start helps you** — one whose binary/DLL you can tamper with ([[05 - Modifiable Service Binaries]], [[03 - Unquoted Service Paths]], [[04 - Weak Service Permissions]]) or one you want to coerce onto a named pipe.
3. **Fire the trigger** appropriate to its type:
   - **Named pipe / RPC endpoint:** connect to the endpoint that triggers it.
   - **Firewall port:** add/trigger the port event (e.g. open the port) — doable as a normal user for certain configurations.
   - **ETW/custom event:** emit the event the trigger watches.
4. **Service starts as SYSTEM** and executes your tampered code or connects to your pipe.

## Why It Matters in an Engagement
Defenders often assume that without `SERVICE_START` rights a low-priv user cannot influence service lifecycle. Triggers break that assumption: they are an *intended* mechanism to start services in response to environmental events, and several of those events are attacker-inducible. This turns "I can modify the service binary but it's already running" into a clean SYSTEM escalation.

## Detection and Mitigation
- **Audit trigger configurations** (`sc qtriggerinfo`) on SYSTEM services; remove unnecessary attacker-inducible triggers (named-pipe/port triggers on sensitive services).
- Fix the *underlying* weakness — a service you can start as SYSTEM is only dangerous if its binary/DLL/path is also tamperable; harden those ([[05 - Modifiable Service Binaries]], [[03 - Unquoted Service Paths]]).
- Monitor for unexpected service starts correlated with low-priv user activity, and for named-pipe creation preceding a SYSTEM service connect.

## Chaining Opportunities
- Trigger → [[28 - Named Pipe Impersonation]] (coerce SYSTEM onto your pipe).
- Trigger → reload of a modified binary ([[05 - Modifiable Service Binaries]]) or hijacked DLL ([[06 - DLL Hijacking]]).
- Useful after [[41 - Abusing SeManageVolumePrivilege]] plants a DLL that needs the service to restart.

## Related Notes
- [[28 - Named Pipe Impersonation]]
- [[05 - Modifiable Service Binaries]]
- [[04 - Weak Service Permissions]]
- [[03 - Unquoted Service Paths]]
- [[13 - Scheduled Task Hijacking]]
