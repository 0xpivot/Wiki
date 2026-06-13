---
tags: [vapt, deserialization, defense, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.12 Defense — Avoid Untrusted Deserialization, Use Safe Formats"
---

# 15.12 — Defense: Avoid Untrusted Deserialization

## The Core Problem

```
FUNDAMENTAL RULE:
  Never deserialize data from an untrusted source using native
  serialization formats (Java ObjectInputStream, PHP unserialize,
  Python pickle, .NET BinaryFormatter, etc.)
  
  No amount of input validation, filtering, or "safe deserialization"
  fully protects against gadget chains in loaded libraries.
  
THE ONLY SAFE SOLUTIONS:
  1. Don't deserialize untrusted data at all
  2. Use a safe data format that cannot instantiate objects (JSON, XML with schema)
  3. Deserialize in a strict sandbox with no useful classes available
  4. Use signed/encrypted cookies (verify before deserializing)
```

---

## Java Defenses

```java
// OPTION 1: DON'T USE ObjectInputStream FOR USER DATA AT ALL!
// Use Jackson, Gson, or similar for data exchange.

// OPTION 2: JAVA DESERIALIZATION FILTER (Java 9+ — JEP 290):
// Set a process-wide filter:
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "maxdepth=5;maxarray=100;maxrefs=50;" +
    "com.example.SafeClass;" +  // only allow specific classes!
    "!*"                         // block everything else
);
ObjectInputFilter.Config.setSerialFilter(filter);

// PER-STREAM FILTER:
ObjectInputStream ois = new ObjectInputStream(inputStream);
ois.setObjectInputFilter(info -> {
    Class<?> clazz = info.serialClass();
    if (clazz == null) return ObjectInputFilter.Status.UNDECIDED;
    if (ALLOWED_CLASSES.contains(clazz.getName())) {
        return ObjectInputFilter.Status.ALLOWED;
    }
    return ObjectInputFilter.Status.REJECTED;  // block everything else
});

// OPTION 3: NOTSO SERIALKILLER / SERIAL WHITELIST AGENT:
// Java agent that blocks deserialization of dangerous classes
// https://github.com/kantega/notsoserial

// OPTION 4: REMOVE DANGEROUS LIBRARIES:
// Remove Commons Collections, Spring, Groovy from classpath
// if not needed → no gadget chains available!
// (Not always practical, but reduces attack surface)
```

---

## PHP Defenses

```php
// OPTION 1: NEVER PASS USER INPUT TO unserialize()!
// This is a hard rule — no exceptions.

// BAD:
$user = unserialize($_COOKIE['user']);  // ← NEVER DO THIS!
$data = unserialize(base64_decode($_POST['data']));  // ← NEVER!

// OPTION 2: USE JSON INSTEAD:
$user = json_decode($_COOKIE['user'], true);  // returns array, not object!
// → json_decode with assoc=true returns arrays → no magic methods!

// OPTION 3: IF YOU MUST DESERIALIZE, SIGN THE DATA:
function serialize_signed($data, $secret) {
    $serialized = serialize($data);
    $sig = hash_hmac('sha256', $serialized, $secret);
    return base64_encode($sig . '|' . $serialized);
}

function unserialize_signed($input, $secret) {
    $decoded = base64_decode($input);
    [$sig, $serialized] = explode('|', $decoded, 2);
    $expected = hash_hmac('sha256', $serialized, $secret);
    if (!hash_equals($expected, $sig)) {
        throw new Exception("Signature mismatch!");
    }
    return unserialize($serialized);  // only after signature verification!
}

// OPTION 4: PHP 7+ ALLOWED CLASSES:
// Limit which classes can be deserialized:
$obj = unserialize($data, ['allowed_classes' => ['SafeClass']]);
// → Only SafeClass can be created; others become __PHP_Incomplete_Class

// OPTION 5: FIND AND FIX DANGEROUS MAGIC METHODS IN CODEBASE:
// Audit all classes for __destruct(), __wakeup(), __toString() 
// that do anything with file system, exec, or network
```

---

## Python Defenses

```python
# OPTION 1: NEVER USE pickle FOR UNTRUSTED DATA!
# Use JSON, msgpack, or similar safe formats.

# BAD:
import pickle
data = pickle.loads(user_input)  # ← NEVER!

# OPTION 2: USE JSON INSTEAD:
import json
data = json.loads(user_input)  # safe — no code execution!

# OPTION 3: IF PICKLE NECESSARY, SIGN IT:
import pickle, hmac, hashlib, base64

SECRET = b'server-secret-key'

def serialize(obj):
    serialized = pickle.dumps(obj)
    sig = hmac.new(SECRET, serialized, hashlib.sha256).digest()
    return base64.b64encode(sig + serialized)

def deserialize(data):
    raw = base64.b64decode(data)
    sig, payload = raw[:32], raw[32:]
    expected = hmac.new(SECRET, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Signature mismatch!")
    return pickle.loads(payload)

# OPTION 4: USE RestrictedUnpickler:
class SafeUnpickler(pickle.Unpickler):
    SAFE_GLOBALS = {'builtins': {'int', 'str', 'float', 'list', 'dict', 'tuple'}}
    
    def find_class(self, module, name):
        if module in self.SAFE_GLOBALS and name in self.SAFE_GLOBALS[module]:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Forbidden: {module}.{name}")

# OPTION 5: FIX YAML:
import yaml
data = yaml.safe_load(user_input)  # safe_load disables !! tags!
# NEVER: yaml.load(user_input)  ← dangerous
# NEVER: yaml.load(user_input, Loader=yaml.Loader)  ← dangerous
```

---

## .NET Defenses

```csharp
// OPTION 1: DON'T USE BinaryFormatter! (Deprecated in .NET 5+)
// Microsoft officially marks it as "always insecure"

// BAD:
BinaryFormatter bf = new BinaryFormatter();
object obj = bf.Deserialize(stream);  // ← ALWAYS DANGEROUS!

// GOOD ALTERNATIVES:
// Use System.Text.Json or Newtonsoft.Json for data exchange
// Use DataContractSerializer with known types list
// Use XmlSerializer (safer, but still audit it)

// OPTION 2: JSON.NET — DISABLE TypeNameHandling:
var settings = new JsonSerializerSettings {
    TypeNameHandling = TypeNameHandling.None  // ← Safe! (default)
};
var obj = JsonConvert.DeserializeObject<MyClass>(json, settings);

// OPTION 3: VIEWSTATE — ALWAYS ENABLE MAC:
// In web.config:
<system.web>
  <machineKey validationKey="AutoGenerate,IsolateApps" 
              validation="HMACSHA256" />
  <pages enableViewStateMac="true" viewStateEncryptionMode="Always" />
</system.web>
// → ViewState tampering impossible without the server's machineKey

// OPTION 4: NET NATIVE AOT (new in .NET 7+):
// BinaryFormatter completely removed — use new apps as .NET 7+
```

---

## Ruby Defenses

```ruby
# OPTION 1: DON'T EXPOSE Marshal.load TO USER INPUT!
# Use JSON instead for data exchange.

require 'json'
data = JSON.parse(user_input)  # safe!

# OPTION 2: SIGN COOKIES (Rails does this by default):
# Rails uses HMAC-signed cookies — never disable this!
# config/initializers/secret_key_base.rb must have strong key
# Never commit secret_key_base to version control!

# OPTION 3: YAML — USE safe_load:
require 'yaml'
data = YAML.safe_load(user_input)  # disables class instantiation!
# NEVER: YAML.load(user_input)  ← allows arbitrary Ruby objects!
```

---

## Node.js Defenses

```javascript
// OPTION 1: DON'T USE node-serialize PACKAGE!
// It's been removed from active maintenance; use JSON instead.

// OPTION 2: USE JSON.parse (safe):
const data = JSON.parse(userInput);  // returns plain objects, no functions!

// OPTION 3: AVOID eval() ON USER DATA:
// BAD:
const obj = eval('(' + userInput + ')');  // ← NEVER!

// OPTION 4: PROTOTYPE POLLUTION (related):
// Use Object.create(null) for untrusted data maps
// Validate __proto__, constructor, prototype in user JSON
const safe = JSON.parse(input, (key, value) => {
    if (key === '__proto__' || key === 'constructor') return undefined;
    return value;
});
```

---

## Safe Replacement Formats

```
NATIVE SERIALIZATION → SAFE REPLACEMENT:
  Java ObjectInputStream  → Jackson JSON / Protobuf / Thrift
  PHP unserialize         → json_decode (returns array!)
  Python pickle           → json / msgpack / protobuf
  .NET BinaryFormatter    → System.Text.Json / DataContractSerializer (with types)
  Ruby Marshal            → JSON.parse
  Node node-serialize     → JSON.parse
  
WHY JSON IS SAFER:
  JSON only represents primitives, arrays, and objects (key-value)
  Cannot represent code/functions
  Cannot specify which class to instantiate
  Cannot trigger magic methods on deserialization
  
EXCEPTIONS (even JSON can be unsafe):
  Jackson with DefaultTyping enabled → type confusion attacks!
  JSON.NET with TypeNameHandling → type confusion attacks!
  → Disable type annotations even in JSON libraries!
```

---

## Quick Audit Checklist

```
✓ Grep for: unserialize, pickle.loads, Marshal.load, BinaryFormatter
✓ Check: Are any of these called with user-controlled input?
✓ Check: Are YAML files/strings from users parsed with safe_load?
✓ Check: Is Jackson DefaultTyping disabled?
✓ Check: Is JSON.NET TypeNameHandling = None?
✓ Check: Are cookies signed/verified before deserialization?
✓ Check: Is Java serialization filter configured (Java 9+)?
✓ Check: Is PHP unserialize using allowed_classes?
✓ Test: Can you modify a serialized cookie and it gets accepted?
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[02 - Java Deserialization ysoserial]] — what this defense prevents
- [[03 - PHP Object Injection]] — PHP magic methods
- [[04 - Python Pickle Deserialization]] — pickle RCE
- [[05 - .NET Deserialization]] — BinaryFormatter + ViewState
- [[11 - Magic Methods Abuse]] — why native deser is dangerous
