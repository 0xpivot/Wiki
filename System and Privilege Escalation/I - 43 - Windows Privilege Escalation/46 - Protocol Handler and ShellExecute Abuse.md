---
tags: [windows, privesc, execution, protocol-handler, pentesting, red-team]
difficulty: intermediate
module: "43 - Windows Privilege Escalation"
topic: "43.46 Protocol Handler and ShellExecute Abuse"
---

# Protocol Handler and ShellExecute Abuse

## Introduction
Windows maps **URI schemes** (`http:`, `ms-msdt:`, `search-ms:`, `ms-officecmd:`, `mailto:`, custom app schemes) to **protocol handlers** — registry-registered commands that launch when a URI of that scheme is invoked. `ShellExecute`/`ShellExecuteEx` and the Run dialog resolve these handlers. Because a single URI can cause a registered application to launch *with attacker-controlled arguments*, protocol handlers are a powerful primitive for **code execution, argument injection, and privilege/UAC abuse** — both for initial access (a link or document triggers a handler) and for local escalation (driving an auto-elevating or privileged handler). The infamous **Follina / `ms-msdt`** issue and numerous `ms-officecmd`/`search-ms` abuses are examples of this class.

## How Protocol Handlers Resolve
Handlers are registered under the registry, mapping a scheme to a command line where `%1` is the full URI:
```text
HKEY_CLASSES_ROOT\<scheme>\
   (Default) = "URL:<scheme> Protocol"
   URL Protocol = ""
   shell\open\command\(Default) = "C:\Path\App.exe" "%1"
```
When `someapp:payload-here` is invoked (from a browser, document, `.url`/`.lnk`, or `ShellExecute`), Windows launches the registered command with the URI substituted into `%1`.

```text
+---------------------------------------------------------------+
|              URI -> HANDLER -> EXECUTION                     |
+---------------------------------------------------------------+
|  user/app invokes  scheme:data                                |
|        |  ShellExecute / browser / Office link                |
|        v                                                       |
|  HKCR\scheme\shell\open\command   ->  App.exe "scheme:data"   |
|        |                                                       |
|        v                                                       |
|  App parses the URI; if it passes parts to a shell / process  |
|  unsanitized  ->  ARGUMENT INJECTION / command execution      |
+---------------------------------------------------------------+
```

## Abuse Techniques
### 1. Argument injection into the handler's target
If the handler passes URI-derived data into a process/command without sanitization, an attacker crafts a URI that injects extra arguments or switches. `ms-msdt:` (Follina) caused the Microsoft Support Diagnostic Tool to execute PowerShell from a URI. Many third-party app schemes are similarly careless with `%1`.

### 2. Privileged / auto-elevating handlers
Some handlers launch a target that **auto-elevates** or runs in a higher-privilege context. Triggering such a handler from a Medium-integrity process can perform a privileged action — a UAC-adjacent escalation that pairs with [[12 - UAC Bypass Techniques]] and [[45 - UIAccess and Admin Protection Bypass]].

### 3. Registering / hijacking a handler (local persistence + execution)
A user can register handlers under **`HKCU\Software\Classes\<scheme>`**, which take precedence for that user. Registering or overwriting a scheme that a privileged/automated process later invokes redirects that invocation to attacker code (an execution + persistence vector akin to [[15 - Registry Autorun Key Abuse]] and [[29 - COM Object Hijacking]]).

### 4. LOLBin handlers (`search-ms`, `ms-officecmd`, etc.)
Built-in schemes can be abused to reach a file share, open a remote search window that lures execution, or chain to Office components — useful for phishing-to-execution and for bypassing some launch restrictions ([[34 - LOLBins]]).

## Enumeration
```cmd
:: list registered URL schemes
reg query HKCR /f "URL Protocol" /s 2>nul | findstr /i "HKEY"
:: inspect a scheme's launch command
reg query "HKCR\<scheme>\shell\open\command"
:: per-user overrides (writable by the user)
reg query "HKCU\Software\Classes" /s 2>nul | findstr /i "URL Protocol"
```
Audit each handler's command for unsanitized `%1` usage and for targets that elevate.

## Why It Matters in an Engagement
Protocol handlers connect *data you can deliver* (a URL, a document field, a `.lnk`) to *code that runs locally with the handler app's privileges*. They underpin a steady stream of initial-access exploits (Follina-class) and provide local execution/escalation via privileged or hijackable handlers — often bypassing macro and download protections because no obvious executable is involved.

## Detection and Mitigation
- **Remove/disable risky handlers** not in use (`ms-msdt`, legacy diagnostic schemes) via registry / GPO; apply vendor patches (Follina was fixed by removing the vulnerable handler behavior).
- Developers: rigorously **validate and quote** URI input; never pass `%1` parts into a shell or as raw arguments.
- Monitor `HKCU\Software\Classes\<scheme>` modifications and unusual parent→child chains (Office/`msdt`/`searchprotocolhost` spawning shells).
- Use ASR rules / attack-surface reduction to block Office spawning child processes.

## Chaining Opportunities
- Initial access (document/link) → handler execution → local privesc via the other I-43 techniques.
- Handler hijack as persistence alongside [[15 - Registry Autorun Key Abuse]] / [[29 - COM Object Hijacking]].
- Privileged handler → [[12 - UAC Bypass Techniques]] / [[45 - UIAccess and Admin Protection Bypass]].

## Related Notes
- [[34 - LOLBins]]
- [[29 - COM Object Hijacking]]
- [[15 - Registry Autorun Key Abuse]]
- [[12 - UAC Bypass Techniques]]
- [[45 - UIAccess and Admin Protection Bypass]]
