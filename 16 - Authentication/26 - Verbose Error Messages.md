---
tags: [vapt, authentication, information-disclosure, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.26 Verbose Error Messages"
---

# 16.26 — Verbose Error Messages

## What Is Information Leakage via Error Messages?

```
PROBLEM:
  Error messages reveal more information than necessary to an attacker
  
  EXAMPLES:
  "Invalid password"  ← tells attacker the USERNAME is valid!
  "mysql_fetch_array(): supplied argument is not a valid MySQL result" ← exposes tech stack!
  "ORA-00933: SQL command not properly ended" ← Oracle SQL error!
  "at line 42 of /var/www/html/app/models/User.php" ← exposes file path!
  "No account with email bob@example.com" ← confirms user doesn't exist!
```

---

## Types of Information Leakage

### Login Error Differentiation

```
WEAK (reveals information):
  "Your username is incorrect"          → confirms username wrong
  "Incorrect password"                  → confirms username EXISTS
  "No account found for this email"     → confirms email NOT in DB
  "We sent a reset email to alice@x.com" → confirms email EXISTS
  
STRONG (reveals nothing):
  "Incorrect username or password"      → same for all failures
  "If that email exists, we'll send a reset link" → same always
```

### Stack Traces and Technical Errors

```
BAD (production error):
  Error: SQLSTATE[42000]: Syntax error or access violation:
  1064 You have an error in your SQL syntax;
  check the manual that corresponds to your MySQL server version
  for the right syntax to use near 'admin'' at line 1
  
  → Confirms SQLi injection point!
  → Reveals: MySQL database engine
  
BAD (PHP warning):
  Warning: file_get_contents(/etc/config/passwords.json): 
  failed to open stream: Permission denied in /var/www/html/auth.php on line 45
  
  → Reveals: file path, OS, technology stack
  
GOOD (production):
  "An error occurred. Please try again later."
  + Log the full error server-side for developers
```

### Version Disclosure

```
HTTP SERVER HEADERS:
  Server: Apache/2.4.29 (Ubuntu)
  X-Powered-By: PHP/7.1.3
  X-AspNet-Version: 4.0.30319
  
  → Reveals: exact versions → check CVE databases for vulnerabilities!
  
FRAMEWORK VERSION IN HTML:
  <!-- Powered by WordPress 5.8.1 -->
  <!-- Bootstrap v3.3.7 -->
  <!-- jQuery v1.7.2 (vulnerable!) -->
  
CMS LOGIN PAGE:
  Drupal admin login form → identifies CMS = Drupal
  WordPress /wp-login.php → always WordPress!
```

---

## Testing

```bash
# CHECK SERVER HEADERS:
curl -I https://target.com/login
# Look for: Server, X-Powered-By, X-AspNet-Version

# CHECK ERROR PAGE CONTENT:
curl https://target.com/invalid-path-12345
# Does it show stack trace? File paths? Framework errors?

# TRIGGER SQL ERRORS:
# In any form field, try: '
# Check if raw SQL error appears

# CHECK LOGIN DIFFERENTIATION:
curl -X POST https://target.com/login -d "username=definitelynotauser12345&password=test"
curl -X POST https://target.com/login -d "username=admin&password=wrongpassword"
# Compare response text — different messages?

# CHECK FORGOT PASSWORD:
curl -X POST https://target.com/forgot-password -d "email=notauser99999@notexist.com"
curl -X POST https://target.com/forgot-password -d "email=known_user@example.com"
# Same response? (Good!) Different? (Leaks!)
```

---

## Severity Reference

```
HIGH:
  - SQL error revealing database queries (SQLi possible)
  - Stack trace with file paths (path traversal hints)
  - Server internal IP/hostname in errors
  - Debug endpoints accessible (/debug, /trace, /actuator/env)
  
MEDIUM:
  - Username enumeration via error message
  - Database type revealed (MySQL, Oracle, PostgreSQL)
  - Framework/version revealed (PHP 7.1, Spring Boot 2.1)
  
LOW / INFORMATIONAL:
  - Server header reveals version (Apache/2.4.29)
  - X-Powered-By header
  - WordPress/Drupal detected from login page
  - Autocomplete issues
```

---

## Fix

```
DEFENSES:
  ✓ Generic error messages to users:
    "Invalid username or password" (never differentiate!)
    "An error occurred. Please try again."
    
  ✓ Log full details server-side (for developers), not in HTTP response:
    Python: logger.exception("Auth failed") — not response.write(traceback)
    
  ✓ Remove/suppress HTTP headers:
    Nginx: server_tokens off;
    Apache: ServerTokens Prod; ServerSignature Off
    PHP: expose_php = Off (in php.ini)
    .NET: removeServerHeader="true" in web.config
    
  ✓ Custom error pages (don't use default framework error pages):
    404, 403, 500 → custom pages with no technical details
    
  ✓ Debug mode OFF in production:
    Django: DEBUG = False
    Flask: debug=False (and not on by default!)
    PHP: display_errors = Off
    Spring Boot: application.properties: server.error.include-stacktrace=never
    
  ✓ Remove version comments from HTML
```

---

## Related Notes
- [[01 - Username Enumeration]] — error-based username enumeration
- [[25 - Autocomplete on Sensitive Fields]] — another low-severity finding
- [[Module 06 - SQL Injection]] — SQL errors = SQLi confirmation
