---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.35 tplmap Template Injection Tester"
---

# 59.35 tplmap Template Injection Tester

## 1. Introduction and Legacy Context
Before the rise of modern, actively maintained tools like SSTImap, `tplmap` was the foundational standard for automating Server-Side Template Injection (SSTI) detection and exploitation. Written in Python, it serves as the ideological predecessor to SSTImap. 

While SSTImap is generally more maintained and supports newer frameworks and Node.js engines, `tplmap` remains a strictly critical tool in the VAPT arsenal. It possesses highly specialized payloads for older, esoteric, or highly specific versions of template engines that newer tools sometimes overlook or have deprecated. Understanding `tplmap` is essential for dealing with legacy enterprise infrastructure, which makes up a massive portion of real-world assessment targets.

## 2. Core Architecture and Exploitation Flow

Tplmap operates by injecting context-breaking characters and mathematical evaluations, interpreting the resulting stack traces, and parsing rendering errors to fingerprint the engine accurately.

```ascii
+-----------------------------------------------------------------------------------+
|                                 Tplmap Core Engine                                |
|                                                                                   |
|  +-----------------+    +-------------------------+    +-----------------------+  |
|  | Request Builder | -> | Code Injection Engine   | -> | Output Parsing & WAF  |  |
|  | (GET/POST/Hdr)  |    | (Math Eval & Context)   |    | Heuristics            |  |
|  +-----------------+    +-------------------------+    +-----------------------+  |
|                                     |                              |              |
|                                     v                              v              |
|                         +-------------------------+    +-----------------------+  |
|                         | Sandbox Escape Engine   | <- | Execution Context     |  |
|                         | (MRO, Reflection, Glob) |    | Fingerprinting        |  |
|                         +-------------------------+    +-----------------------+  |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                            Reverse Shell / OS Commmand                            |
+-----------------------------------------------------------------------------------+
```

## 3. Templating Engines Deep Dive and Specific Quirks
`tplmap` shines in its support for specific framework quirks from older versions.
*   **Python**: It handles Jinja2, Mako, and Tornado efficiently. Its MRO (Method Resolution Order) traversal for Python sandbox escapes is legendary and forms the fundamental basis of many modern SSTI payload generators.
*   **PHP**: Smarty and Twig. It leverages specialized PHP callbacks (like `call_user_func` bypasses) to achieve arbitrary execution, often utilizing PHP magic methods.
*   **Java**: Velocity and FreeMarker. Tplmap exploits Java's powerful reflection API, breaking out of the confined template context to execute arbitrary `java.lang.Runtime.getRuntime().exec()` calls.
*   **Ruby**: ERB payloads focus on utilizing standard Ruby module inclusions and dynamic evaluation.

## 4. Python MRO and Sandbox Escapes Deep Dive
Tplmap's approach to Python SSTI is highly educational. When evaluating Jinja2, it attempts to traverse the object hierarchy to break out of the sandbox. It starts with an empty string `""`, accesses its class `__class__`, navigates to the base object `__mro__[1]`, and then lists all subclasses `__subclasses__()`. 

From there, tplmap automatically scans the hundreds of loaded subclasses in memory to find ones that can execute commands (like `subprocess.Popen` or modules that import `os`). It automates this complex, tedious process entirely.

## 5. Execution Contexts and Exfiltration Mechanisms
The primary goal of Tplmap, once SSTI is detected, is to transition from simple template evaluation to arbitrary OS-level execution.

*   `--os-cmd`: Execute a single shell command.
    *   *Example*: `./tplmap.py -u "http://target.com/page?name=John" --os-cmd "cat /etc/passwd"`
*   `--os-shell`: Launch a pseudo-interactive shell. Tplmap simulates a shell by repeatedly sending payloads containing your commands.
*   `--upload`: Upload local files to the remote server.
*   `--download`: Exfiltrate remote files to your local machine.

## 6. Detailed Flag Reference
The flag structure is heavily inspired by `sqlmap`, making it intuitive for experienced penetration testers.

### Target Selection
*   `-u URL`, `--url=URL`: Direct URL targeting.
*   `-req REQUEST_FILE`: Parse a standard HTTP request file (e.g., exported from Burp Suite).
*   `-d DATA`: Specify POST data.
*   `-H HEADERS`: Append custom headers.
*   `-c COOKIES`: Provide session cookies.

### Injection Control
*   `--engine ENGINE`: Force Tplmap to use payloads for a specific engine (e.g., `--engine jinja2`). This bypasses the noisy fingerprinting phase, avoids triggering WAFs unnecessarily, and significantly reduces execution time.
*   `--level LEVEL`: Determines the aggressiveness and complexity of the payloads. Levels 1-5 dictate whether the tool uses basic math evaluations or complex, multi-stage sandbox escape vectors.
*   `-e ENGINE`: A convenient alias for forcing the engine.

### Advanced Evaluation
*   `--tpl-shell`: Instead of an OS shell, this drops you into a "template shell," allowing you to execute arbitrary template code directly on the server. This is incredibly useful for deep internal enumeration if OS-level execution is blocked by strict EDR/AppArmor policies, but the template engine can still access local objects, database connectors, or environment variables.

## 7. Case Studies (WAF Bypass in Legacy Apps)
In older enterprise applications, WAFs frequently block the exact string `java.lang.Runtime`. `tplmap` allows for deep customization of the payload generation process. 

By dropping into a `--tpl-shell`, an attacker can manually craft obfuscated reflection calls. For instance, in Velocity, if `.getClass()` is heavily filtered, an attacker might manually traverse the object graph using `.class.classLoader` to eventually instantiate a runtime object, bypassing the rudimentary regex rules of older IPS appliances.

Furthermore, `tplmap`'s Python MRO payloads are extremely versatile. If a target WAF blocks the `subprocess` module, the payloads can pivot automatically to utilize the `os` module or even the `builtins` module to execute `eval()` or `exec()`.

## 8. Blind Exploitation Capabilities
While not as sophisticated as modern tools in asynchronous blind evaluation, `tplmap` supports basic blind SSTI. It relies heavily on the application throwing specific template parsing errors (which requires stack traces to be enabled and visible) or observing significant time delays when injecting complex processing loops within the template payload.

## 9. Chaining Opportunities
*   **Burp Suite to Tplmap**: Save the raw HTTP request from Burp's Repeater module. If a parameter seems to reflect dynamically rendered content, pass the file directly to `tplmap` using `-req`.
*   **Tplmap to Persistence**: Use the `--upload` flag to place a resilient web shell or an SSH key in `/root/.ssh/authorized_keys` (if the application runs as root), establishing a persistent foothold outside the template injection vulnerability.
*   **Environment Variable Harvesting**: Use the `--tpl-shell` to dump `self.__dict__` or access the `env` object directly via the template engine, extracting database credentials or cloud API tokens without ever dropping to a monitored OS shell.

## 10. Related Notes
*   [[17 - Server-Side Template Injection (SSTI)]]
*   [[34 - SSTImap SSTI Scanner and Exploiter]]
*   [[55 - Python MRO and Sandbox Escapes]]
*   [[56 - Java Reflection Attacks]]
