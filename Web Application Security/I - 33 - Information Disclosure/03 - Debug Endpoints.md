---
tags: [vapt, information-disclosure, reconnaissance, spring-boot, actuator, intermediate]
difficulty: intermediate
module: "33 - Information Disclosure"
topic: "33.03 Debug Endpoints (/debug, /actuator, /console)"
---
# Debug Endpoints (/debug, /actuator, /console)

## Introduction

Debug endpoints are specialized administrative interfaces built directly into modern web frameworks and applications. Their purpose is to provide developers, system administrators, and DevOps engineers with real-time insight into the application's internal state, configuration, performance metrics, and environment variables. 

While these endpoints are incredibly powerful tools for health checking and remote debugging in a secure development environment, they represent a catastrophic Information Disclosure and Remote Code Execution (RCE) risk when exposed to the public internet or untrusted internal networks. An exposed debug endpoint is essentially a "backdoor" created by the developers themselves, bypassing standard authentication and authorization controls.

Unlike verbose error messages or stack traces (which require an attacker to trigger an error via malformed input), debug endpoints proactively serve highly sensitive operational data on a silver platter, merely by the attacker navigating to the correct URL path.

## Common Debug Endpoints

Different technology stacks have their own ubiquitous debugging interfaces. Recognizing these patterns is essential for rapid reconnaissance:
- **Spring Boot (Java):** The `Spring Boot Actuator` (`/actuator`, `/actuator/env`, `/actuator/heapdump`, `/actuator/routes`).
- **Werkzeug/Flask (Python):** The interactive web-based debugger console (`/console`).
- **Django (Python):** The Django Debug Toolbar, which appends extensive SQL and template data to normal responses.
- **Laravel (PHP):** Laravel Telescope or the Ignition error page.
- **Node.js:** Exposed Inspector endpoints (typically on port 9229) or custom `/debug` routes.
- **Next.js / React:** Source maps mapping transpiled code to original React component source code, or exposed `__NEXT_DATA__` state JSON.

## ASCII Diagram: Spring Boot Actuator Exposure

```text
+---------------------+                             +-----------------------------------+
|      Attacker       |                             |       Spring Boot Application     |
|                     |                             |                                   |
|  1. Discovers Path  |                             |  +-----------------------------+  |
|  GET /actuator/env  +---------------------------->|  |       Actuator Module       |  |
+---------------------+                             |  |  (Unauthenticated Access)   |  |
           ^                                        |  +-------------+---------------+  |
           |                                        |                |                  |
           |                                        |                v                  |
           |                                        |  +-----------------------------+  |
           |                                        |  |     Environment Context     |  |
           |                                        |  |   Reads OS Vars, app.props  |  |
           |                                        |  +-------------+---------------+  |
           | 2. Server responds with full JSON      |                |                  |
           |    containing OS variables, AWS        |                |                  |
           |    keys, DB passwords, etc.            |                |                  |
           |                                        |                v                  |
           |  {                                     |  +-----------------------------+  |
           |    "name": "systemProperties",         |  |       Response Formatter    |  |
           |    "properties": {                     |  |  (Serializes state to JSON) |  |
           |      "AWS_SECRET_ACCESS_KEY": {        |  +-----------------------------+  |
           |        "value": "AKIAIOSFODNN7EXAMPLE" |                                   |
           |      }                                 |                                   |
           |    }                                   |                                   |
           |  }                                     |                                   |
           +----------------------------------------+-----------------------------------+
```

## Deep Dive: Spring Boot Actuator

Spring Boot Actuator is an industry-standard library used to monitor and manage Spring applications. By default, older versions of Spring Boot (1.x) exposed all Actuator endpoints without authentication. Modern versions (2.x/3.x) secure most endpoints by default, but developers frequently misconfigure them (e.g., using `management.endpoints.web.exposure.include=*` in their `application.properties` or `application.yml`) for convenience during deployment.

Critical Actuator Endpoints:
- `/actuator/env`: Returns all environment variables, system properties, and configuration values. This is the holy grail for attackers, as it almost always leaks database credentials, third-party API keys, and cloud provider secrets (like AWS IAM keys).
- `/actuator/heapdump`: Generates and downloads a complete Java memory heap dump (often in `.hprof` format). Attackers can download this massive file and use tools like Eclipse MAT (Memory Analyzer Tool), `jhat`, or OQL (Object Query Language) to extract plain-text session tokens, passwords, and sensitive user data directly from the JVM's live memory.
- `/actuator/threaddump`: Returns a thread dump, revealing active operations, blocking conditions, and potentially sensitive execution states.
- `/actuator/httptrace` / `/actuator/httpexchanges`: Shows HTTP trace information. By default, it stores the last 100 HTTP request/response exchanges, which frequently includes active `Cookie` headers, `Authorization` Bearer tokens, and sensitive POST bodies from other legitimate users interacting with the application.
- `/actuator/mappings`: Lists all active application routes, acting as an instant, perfectly accurate roadmap for the application's REST API.

## Deep Dive: Werkzeug Interactive Console (Python)

Flask and Django applications utilizing the Werkzeug WSGI utility library feature a highly dangerous interactive debugger. If an application crashes while in debug mode, it presents a traceback. What makes Werkzeug uniquely critical is that clicking on a line of code in the traceback opens an interactive Python shell directly in the browser. This allows the user to execute arbitrary Python code directly within the context of the running server.

### The Werkzeug PIN Bypass
To secure this shell from opportunistic attackers, Werkzeug requires a numerical PIN (which is printed to the server's standard output `stdout` on startup). However, if an attacker has a Local File Inclusion (LFI) vulnerability or another way to read arbitrary files on the filesystem, they can calculate the PIN themselves.

The PIN generation algorithm relies on predictable environment data:
1. The username running the application (e.g., discovering it by reading `/etc/passwd` or `/proc/self/environ`).
2. The exact path to the `app.py` or the `flask` executable module.
3. The MAC address of the active network interface (readable via `/sys/class/net/eth0/address` and mathematically converted to a decimal representation).
4. The unique machine ID (readable via `/etc/machine-id` or `/proc/sys/kernel/random/boot_id`).

By gathering these 4 pieces of predictable information via an LFI, an attacker can run a local python script to reverse-engineer the PIN generator, unlock the interactive console, and gain instant, unauthenticated Remote Code Execution (RCE) via commands like `os.popen('id').read()`.

## Impact of Exposed Debug Endpoints

The exposure of debug endpoints is rarely just a simple Information Disclosure issue; it almost always escalates to total system compromise.
- **Immediate Credential Theft:** Extracting AWS keys from an `/env` endpoint allows attackers to pivot from the web application tier to the entire AWS cloud infrastructure, potentially launching ransomware attacks against S3 buckets.
- **Remote Code Execution (RCE):** 
  - The Werkzeug console allows direct, native execution of OS commands.
  - Spring Boot Actuator can be leveraged directly for RCE in multiple ways. For example, if the `spring-cloud-starter` dependency is present, an attacker can modify the environment variables via a `POST` request to `/actuator/env` to point `spring.cloud.bootstrap.location` to a malicious YAML file hosted on an attacker-controlled server. They then call `/actuator/refresh`, forcing the server to fetch and execute the malicious YAML, triggering a Spring Cloud SnakeYAML RCE.

## Discovery Methodologies

Since these endpoints reside on highly standardized paths, discovery is easily automated and scaled.

### 1. Directory Brute-Forcing
Using tools like `ffuf`, `dirb`, `dirsearch`, or `Gobuster` with specialized wordlists focused on debug and administrative paths.
- **Wordlists:** SecLists contains excellent, highly-curated wordlists specifically for Spring Boot (e.g., `spring-boot.txt`) and generic debug paths.
- **Key paths to fuzz:** `/actuator`, `/actuator/env`, `/debug/vars`, `/console`, `/__profiler`, `/_profiler/phpinfo`, `/.env`.

### 2. Environment and Header Analysis
- Passively analyzing HTTP response headers. If a server returns `X-Powered-By: Express`, an attacker might explicitly look for Node inspector ports. If it returns `X-Application-Context`, it strongly hints at a Spring Boot application.
- Using browser extensions or CLI tools like Wappalyzer to proactively identify the framework, which instantly dictates which specific debug endpoints to test.

### 3. Google Dorking
Publicly accessible debug endpoints are, shockingly, often indexed by search engines.
- `inurl:"/actuator/env"`
- `intitle:"Werkzeug Debugger"`
- `inurl:"/actuator/heapdump"`

## Mitigation and Best Practices

### 1. Never Expose Debug Endpoints to the Public
Debug and management endpoints must be structurally segregated from the public internet.
- Configure Web Application Firewalls (WAF) or Reverse Proxies (Nginx, HAProxy, AWS ALB) to strictly block any external requests to `/actuator/*`, `/debug/*`, or `/console/*`. These requests should return a `403 Forbidden` or `404 Not Found` before ever reaching the application.

### 2. Disable Debug Mode in Production
- Ensure environment variables are strictly enforced across deployments: `FLASK_ENV=production`, `NODE_ENV=production`.
- In Spring Boot, avoid using wildcard inclusion like `management.endpoints.web.exposure.include=*`. Only expose explicitly needed endpoints (like `/health` or `/info`), and even then, secure them carefully.

### 3. Implement Strict Authentication
If management endpoints must be accessible (e.g., for internal monitoring tools like Prometheus or Datadog), they must be protected by strong, dedicated authentication.
- In Spring Boot, integrate Spring Security to require HTTP Basic Auth or OAuth2 tokens specifically for the `/actuator` path family.
- Restrict access at the network level using IP whitelisting (e.g., only allowing the internal VPC subnet `10.0.0.0/8` or a specific bastion host to access the management endpoints).

## Chaining Opportunities

- **[[02 - Local File Inclusion (LFI)]]:** LFI is absolutely required to read the host parameters necessary to bypass the Werkzeug Console PIN, upgrading a read-only LFI to full RCE.
- **[[12 - Server-Side Request Forgery (SSRF)]]:** If external access to `/actuator` is blocked by a WAF or reverse proxy, an attacker can use an SSRF vulnerability elsewhere in the application to make the server request its own internal `http://localhost:8080/actuator/env` endpoint, entirely bypassing external network controls.
- **[[32 - Cloud Security Vulnerabilities]]:** Keys and tokens extracted from debug endpoints are the primary vector for attacking the underlying cloud infrastructure (AWS/GCP/Azure) via lateral movement.

## Related Notes
- [[01 - Verbose Error Messages]]
- [[02 - Stack Traces in Responses]]
- [[14 - Remote Code Execution (RCE)]]
