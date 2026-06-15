---
tags: [macos, privesc, sandbox, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.08 App Sandbox Escapes"
---

# App Sandbox Escapes

## Introduction
The **macOS App Sandbox** (built on the kernel's **Sandbox / Seatbelt** framework, `sandboxd` and the TrustedBSD MAC layer) confines an application to a least-privilege profile: which files it can read/write, which Mach services and network endpoints it can reach, whether it can spawn children, and so on. Every Mac App Store app is sandboxed, as are many Apple apps and browser renderer processes. If your code lands inside a sandboxed process — a browser renderer, a Mac App Store app, an Office app — you are *not* free even as that user: you must **escape the sandbox** before most local techniques apply.

## How the Sandbox Works
A sandboxed process declares its needs as **entitlements** (`com.apple.security.app-sandbox = true` plus capability entitlements like `com.apple.security.network.client` or `com.apple.security.files.user-selected.read-write`). At launch these expand into a compiled **sandbox profile** (a Scheme-like `.sb` policy) that the kernel enforces on every syscall.

```text
+---------------------------------------------------------------+
|                    SANDBOX ENFORCEMENT                        |
+---------------------------------------------------------------+
|  Process makes syscall (open, mach_msg, connect, fork...)     |
|        | TrustedBSD MAC hook                                  |
|        v                                                       |
|  Sandbox kext evaluates compiled profile                      |
|        | allowed?  -> proceed                                  |
|        | denied?   -> errno / kill (logged by sandboxd)        |
+---------------------------------------------------------------+
| Container: ~/Library/Containers/<bundleid>/Data  (its world)  |
+---------------------------------------------------------------+
```
Inspect a process's container and profile:
```bash
ls ~/Library/Containers/<bundle.id>/Data
sandbox-exec -f profile.sb /bin/zsh     # run something under a profile (testing)
codesign -d --entitlements - /path/App  # confirm app-sandbox + capabilities
log stream --predicate 'sender == "Sandbox"'   # watch denials
```

## Escape Technique Classes
Sandbox escapes are about reaching something **outside the profile**, usually by talking to a *less-constrained broker*:

### 1. Abusing reachable XPC / Mach services
The profile lists Mach services the app may contact (e.g. for opening files via a powerbox, printing, etc.). If any reachable service is a **privileged broker** with a logic flaw, the sandboxed app can ask it to perform an out-of-sandbox action. This is the dominant escape pattern — see [[11 - XPC and Mach IPC Abuse]]. Many browser/renderer escapes are exactly "renderer → privileged GPU/launch service → host."

### 2. Powerbox / open-save path confusion
Sandboxed apps get user-granted file access via the **powerbox** (the system open/save dialog issues a scoped grant). Bugs in how those grants are scoped, persisted (security-scoped bookmarks), or symlink-resolved have let apps reach files the user never picked.

### 3. Misconfigured / over-broad profiles
Some apps ship weak profiles: `com.apple.security.temporary-exception.*` entitlements, broad file globs, or `(allow file-read* (subpath "/"))`. A weak profile is effectively a self-inflicted escape. Audit third-party app entitlements for `temporary-exception` keys.

### 4. Inherited handles / shared resources
If the sandboxed process inherits an open file descriptor, a writable shared-memory region, or a Mach port from a less-restricted parent, it can leverage that pre-existing handle outside its profile.

### 5. Symlink / path-resolution tricks inside writable areas
The container is writable; planting symlinks or abusing race conditions during operations a broker performs *on the app's behalf* can redirect a privileged write outside the container.

```text
   Sandboxed renderer (cannot touch host FS)
        |  allowed to mach_msg() the GPU/launch broker
        v
   Broker process (NOT sandboxed, or less so)
        |  logic bug: performs action with attacker-controlled args
        v
   Effect outside the sandbox  ==  ESCAPE
```

## After the Escape
Escaping the sandbox returns you to "ordinary user" — you have *not* gained root or defeated TCC. The natural follow-on chain is:
sandbox escape → user-level code exec → local privesc to root ([[11 - XPC and Mach IPC Abuse]], classic Unix vectors) → SIP/TCC bypass for data/persistence. Browser exploit chains typically read: renderer RCE → sandbox escape → local EoP → (optional) kernel.

## Why It Matters
Whenever your foothold is a browser, Mac App Store app, or document handler, the sandbox is the first wall. Knowing it is profile-driven tells you to **enumerate the reachable Mach services and the profile's exceptions** — that's where the escape lives.

## Defensive Notes
- Sandbox apps with the **tightest** profile; avoid `temporary-exception` entitlements.
- Privileged XPC brokers reachable from sandboxes must rigorously validate the peer (code-signing requirement) and all arguments — they are the prime escape target.
- Monitor `Sandbox` denial logs for probing; investigate apps making unusual Mach-service requests.

## Related Notes
- [[01 - macOS PrivEsc Methodology Overview]]
- [[11 - XPC and Mach IPC Abuse]]
- [[06 - Code Signing and Entitlements]]
- [[04 - TCC Transparency Consent and Control]]
