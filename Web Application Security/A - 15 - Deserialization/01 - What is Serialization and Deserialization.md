---
tags: [vapt, deserialization, beginner]
difficulty: beginner
module: "15 - Deserialization"
topic: "15.01 What is Serialization and Deserialization?"
portswigger_labs: ["Modifying serialized objects", "Modifying serialized data types"]
---

# 15.01 — What is Serialization and Deserialization?

## Core Concepts

```
SERIALIZATION:
  Converting an object (in memory) to a format that can be:
  - Stored (database, file, cache)
  - Transmitted (HTTP request, cookie, API)
  
  Object → bytes/string → storage/network

DESERIALIZATION:
  The reverse: bytes/string → Object (in memory)
  
  The vulnerability: when user-controlled data is deserialized
  without validation, the attacker controls what object is created!
  
EXAMPLE (Java):
  User userObj = new User("alice", "admin");
  byte[] serialized = serialize(userObj);
  → serialized = "rO0ABXNy..." (base64 of Java serialized bytes)
  
  // Later:
  User user = (User) deserialize(serialized);  ← DANGEROUS if serialized = attacker input!
```

---

## Why Deserialization Is Dangerous

```
WHEN DESERIALIZING AN OBJECT:
  The runtime recreates the full object with all its methods.
  
  MAGIC METHODS get called automatically during deserialization:
  Java:   readObject(), readResolve(), finalize()
  PHP:    __wakeup(), __destruct(), __toString()
  Python: __reduce__(), __setstate__()
  .NET:   IDeserializationCallback.OnDeserialization()
  Ruby:   marshal_load()
  
  IF A "GADGET CLASS" EXISTS IN THE APPLICATION:
  A class whose magic methods do something dangerous when called
  (execute code, read files, make HTTP requests, etc.)
  → Deserializing an object of that class = code execution!
  
  GADGET CHAINS: Multiple classes whose magic methods call each other
  Eventually reaching a dangerous operation like Runtime.exec()!
```

---

## Where Deserialized Data Appears

```
COMMON LOCATIONS:
  ✓ Cookies (serialized session objects)
  ✓ Hidden form fields (ViewState in .NET)
  ✓ HTTP headers (X-Java-Serialized-Object)
  ✓ Request body (binary or base64 blob)
  ✓ Database (stored then later deserialized)
  ✓ Cache (Redis, Memcached storing serialized objects)
  ✓ Message queues (RabbitMQ, Kafka with serialized payloads)
  ✓ RPC calls (Java RMI, .NET Remoting)
  ✓ File uploads (serialized objects as upload format)
  ✓ API responses (reflected back in subsequent requests)

IDENTIFYING SERIALIZED DATA:
  Java:     base64 starts with rO0AB (raw: ac ed 00 05)
  PHP:      O:4:"User":2:{s:4:"name";s:5:"Alice";}
  Python:   binary pickle (starts with 0x80 0x04 or 0x80 0x02)
  .NET:     ViewState (base64) or binary starting with FF 01
  Ruby:     Binary marshal format (starting with 04 08)
  JSON:     {"@type": "...Class..."}  ← Fastjson/Jackson type confusion
```

---

## Impact of Deserialization Vulnerabilities

```
SEVERITY: Critical (often leads to RCE)

WHAT ATTACKERS CAN DO:
  ✓ Remote Code Execution (most common goal)
  ✓ Privilege escalation (change role/admin field in serialized object)
  ✓ Authentication bypass (modify user/isLoggedIn in session cookie)
  ✓ Data theft (read files via gadget chains)
  ✓ DoS (deserialization bombs — hash collision attacks)

REAL WORLD CVEs:
  Apache Commons Collections (Java) — gadget chain → RCE
  Apache Struts 2 — Java deserialization RCE
  WebLogic RCE (CVE-2020-14882) — Java deserialization
  .NET BinaryFormatter — many RCE CVEs
  PHP Joomla — PHP object injection RCE
```

---

## Simple Deserialization Attack (PHP — Privilege Escalation)

```php
// VULNERABLE PHP SESSION:
// Server stores session as serialized PHP object in cookie

// Server-side code:
$user = new User();
$user->name = $_POST['username'];
$user->role = 'user';
setcookie('session', base64_encode(serialize($user)));

// When request comes in:
$user = unserialize(base64_decode($_COOKIE['session']));
if ($user->role === 'admin') { showAdminPanel(); }

// ATTACK:
// Normal session cookie contains:
// O:4:"User":2:{s:4:"name";s:5:"Alice";s:4:"role";s:4:"user";}
// base64: Tzo0OiJVc2VyIjoyOntzOjQ6Im5hbWUiO3M6NToiQWxpY2UiO3M6NDoicm9sZSI7czo0OiJ1c2VyIjt9

// MODIFIED by attacker:
// O:4:"User":2:{s:4:"name";s:5:"Alice";s:4:"role";s:5:"admin";}
//                                                  ↑ changed!
// base64 encode → set as cookie → server deserializes → user.role = "admin"!
// → Admin panel accessible!
```

---

## ASCII Diagram: Deserialization Attack Flow

```
ATTACKER                APP SERVER                OS/FILESYSTEM
   │                        │                          │
   │  Send modified          │                          │
   │  serialized cookie      │                          │
   │  or body                │                          │
   │────────────────────────→│                          │
   │                         │  deserialize()           │
   │                         │  ↓                       │
   │                         │  readObject() called     │
   │                         │  ↓                       │
   │                         │  Gadget chain executes   │
   │                         │  Runtime.exec("id")      │
   │                         │─────────────────────────→
   │                         │                          │
   │                         │  "uid=33(www-data)..."   │
   │                         │←─────────────────────────
   │  Response includes      │                          │
   │  command output!        │                          │
   │←────────────────────────│                          │
```

---

## Related Notes
- [[02 - Java Deserialization ysoserial]] — Java-specific exploitation
- [[03 - PHP Object Injection]] — PHP magic methods
- [[04 - Python Pickle Deserialization]] — Python pickle
- [[05 - .NET Deserialization]] — .NET BinaryFormatter/ViewState
- [[11 - Magic Methods Abuse]] — understanding gadget chains
- [[12 - Defense Avoid Untrusted Deserialization]] — how to fix
