---
tags: [c2, red-team, initial-access, evasion, vapt]
difficulty: intermediate
module: "101 - Red Team Initial Access and Payload Delivery"
topic: "101.02 HTML Smuggling"
---

# HTML Smuggling

## Introduction
**HTML smuggling** is a payload-delivery technique that **assembles a malicious file inside the victim's browser** rather than transmitting it over the network as a recognizable file. Instead of emailing an `.exe` (blocked) or linking to a `.zip` (scanned by the proxy), the attacker sends a benign-looking HTML page; JavaScript inside that page reconstructs the payload from embedded data and triggers a download locally. Because the payload never crosses the network in its true form, **perimeter controls (web proxies, mail gateways, IDS) see only HTML/JS and a TLS stream** — there is nothing for them to inspect or block. It became a staple of real-world intrusion sets (used by major malware families) and remains highly effective for getting a file onto disk.

## How It Works
```text
+---------------------------------------------------------------+
|                    HTML SMUGGLING FLOW                       |
+---------------------------------------------------------------+
|  Attacker page contains:                                      |
|    - payload bytes encoded as a JS string (base64) OR a Blob  |
|        |                                                       |
|  Victim opens the HTML (email attachment / link)              |
|        |  JS decodes bytes -> Blob -> object URL              |
|        v                                                       |
|  JS creates <a download="invoice.iso"> and clicks() it        |
|        |  browser writes the file to Downloads LOCALLY        |
|        v                                                       |
|  No real file ever traversed the proxy/mail gateway           |
+---------------------------------------------------------------+
```
The two browser features abused are the **`Blob` / data URL** APIs (construct binary data client-side) and the **`download` anchor attribute** (programmatically save it).

## Minimal Example
```html
<html><body><script>
  // payload base64 (e.g. an ISO/ZIP containing an LNK + payload)
  var b64 = "TVqQAAMAAAAEAAAA...";          // smuggled bytes
  var bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  var blob = new Blob([bytes], {type: "application/octet-stream"});
  var url  = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url; a.download = "Invoice_2026.iso";
  document.body.appendChild(a); a.click();   // file lands in Downloads
</script></body></html>
```
The encoded payload can be split/obfuscated, fetched in pieces, or password-gated to defeat static detection.

## Evading Mark-of-the-Web (MotW)
Files downloaded from the internet normally get **MotW** (`Zone.Identifier`), which makes Office open in Protected View and SmartScreen scrutinize executables. A key reason smugglers wrap payloads in **container formats** (ISO, IMG, VHD, sometimes 7z/ZIP):
- When a user **mounts an ISO/VHD**, the files *inside* historically did **not** inherit MotW → an LNK/EXE inside runs without the usual warnings.
- Microsoft has progressively closed these MotW-propagation gaps, so operators rotate container types. The container also helps smuggling deliver a multi-file lure (decoy doc + hidden payload + LNK).

## Typical Payload Chains
```text
   HTML smuggle -> .ISO/.IMG  -> contains LNK -> LNK runs:
        - download cradle ([[05 ...]])  OR
        - LOLBin (rundll32/mshta) executing embedded script  OR
        - a renamed binary / DLL sideload
   HTML smuggle -> .ZIP (password)  -> maldoc ([[04 ...]]) / script
```

## Why It Matters
HTML smuggling neutralizes the network layer of defense by construction — content filtering, attachment stripping, and proxy AV never see the real payload. It is one of the most reliable ways to put a file on the endpoint in 2020s tradecraft, which is why detection has shifted to the **endpoint** (what happens after the file lands).

## Defensive Notes
- **Endpoint focus**: detection must be EDR/host-side (LNK execution, ISO/VHD mounts spawning processes, script interpreters from Downloads) — the network won't catch it.
- **Block/limit risky containers**: prevent automatic mounting of ISO/IMG/VHD for normal users; flag mounting of downloaded images.
- **Browser/mail policy**: strip or sandbox HTML attachments; warn on JS-initiated downloads; enforce MotW propagation (keep OS patched).
- **Attack Surface Reduction** rules: block executable content from email/Downloads; restrict LOLBins (mshta, rundll32) launching from user dirs.

## Related Notes
- [[01 - Phishing Tradecraft and Pretexting]]
- [[04 - Malicious Office Documents and Macros]]
- [[05 - Windows Download and Execute Cradles]]
- [[05 - Gatekeeper and Quarantine Bypass]]
