---
course: API Security
topic: RCE Via Deserialization in API
tags: [api-security]
---

## Unserialization Concept

### Introduction to Serialization and Deserialization

Serialization and deserialization are fundamental concepts in computer programming that involve converting an object's state into a byte stream and reconstructing the object from that byte stream, respectively. These processes are essential for various operations such as saving the state of an object to a database, sending objects over a network, or storing them in a file.

**Serialization**: This is the process of converting an object's state into a byte stream. The byte stream can then be stored in a file or sent over a network to another system. Serialization is often used in distributed systems, where objects need to be transferred between different parts of the system.

**Deserialization**: This is the reverse process of serialization, where the byte stream is converted back into an object. The object is reconstructed using the data contained in the byte stream. Deserialization is crucial for restoring the state of an object that was previously serialized.

### Vulnerabilities Arising from Deserialization

Vulnerabilities arise when developers write code that accepts serialized data from users and attempts to deserialize it. This can lead to various security issues, including:

- **Remote Code Execution (RCE)**: This is one of the most severe vulnerabilities that can occur due to deserialization. An attacker can craft malicious serialized data that, when deserialized, executes arbitrary code on the server.
- **Data Tampering**: An attacker can modify the serialized data to alter the state of the object being deserialized.
- **Information Disclosure**: Sensitive information can be exposed if the serialized data contains confidential details.

### Language-Specific Deserialization Vulnerabilities

Different programming languages have their own mechanisms for serialization and deserialization, which can introduce specific vulnerabilities.

#### Java Serialization

Java uses the `Serializable` interface for serialization. When an object implements this interface, it can be serialized and deserialized. However, if the deserialization process is not properly controlled, it can lead to RCE attacks.

**Example**: In 2015, a critical vulnerability (CVE-2015-4852) was discovered in Apache Struts, which allowed attackers to execute arbitrary commands by exploiting the deserialization of Java objects.

```java
// Vulnerable Java code
import java.io.*;
import java.util.*;

public class DeserializationExample {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream("serializedObject.ser"));
        Object obj = ois.readObject(); // Deserialization happens here
        System.out.println(obj);
    }
}
```

**Secure Code Fix**:
```java
// Secure Java code
import java.io.*;
import java.util.*;

public class DeserializationExample {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("serializedObject.ser"))) {
            ois.readObject(); // Ensure proper validation and sanitization
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
```

#### Python Pickle Module

Python uses the `pickle` module for serialization and deserialization. The `pickle.load()` function is used to deserialize data. However, if this function is used to deserialize data from untrusted sources, it can lead to RCE attacks.

**Example**: In 2015, a vulnerability (CVE-2015-8614) was found in the `pickle` module, which allowed attackers to execute arbitrary code by crafting malicious pickled data.

```python
# Vulnerable Python code
import pickle

def deserialize_data(data):
    return pickle.loads(data)

data = b"cos\nsystem\n(S'echo Attacked'\ntR."
deserialized_data = deserialize_data(data)
print(deserialized_data)
```

**Secure Code Fix**:
```python
# Secure Python code
import pickle

def deserialize_data(data):
    try:
        unpickler = pickle.Unpickler(io.BytesIO(data))
        unpickler.find_global = lambda module, name: None  # Disable global imports
        return unpickler.load()
    except Exception as e:
        print(f"Error: {e}")

data = b"cos\nsystem\n(S'echo Attacked'\ntR."
deserialized_data = deserialize_data(data)
print(deserialized_data)
```

### Remote Code Execution via Deserialization

Remote Code Execution (RCE) is one of the most dangerous types of vulnerabilities that can arise from deserialization. An attacker can craft malicious serialized data that, when deserialized, executes arbitrary code on the server.

#### Scenario: API with Upload Feature

Consider an application with an API that has an upload feature. The API accepts input from users in any format, including binary documents. The application uses the `YAML.load` function to deserialize the uploaded data.

**Example**: In 2017, a vulnerability (CVE-2017-17438) was discovered in the `pyyaml` library, which allowed attackers to execute arbitrary code by crafting malicious YAML data.

```yaml
# Malicious YAML data
!!python/object/apply:os.system ["echo Attacked"]
```

**Full HTTP Request and Response**:

```http
POST /upload HTTP/1.1
Host: example.com
Content-Type: application/octet-stream
Content-Length: 42

!!python/object/apply:os.system ["echo Attacked"]
```

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: text/plain
Content-Length: 11

File uploaded successfully
```

### How to Prevent / Defend Against Deserialization Attacks

To prevent deserialization attacks, follow these best practices:

1. **Validate Input**: Always validate and sanitize user input before deserializing it.
2. **Use Safe Deserialization Libraries**: Use libraries that provide safe deserialization mechanisms, such as `serde` in Rust or `json` in Python.
3. **Disable Global Imports**: Disable global imports in deserialization functions to prevent the execution of arbitrary code.
4. **Use Sandboxing**: Run deserialization processes in a sandboxed environment to limit the damage caused by an attack.
5. **Monitor and Log**: Monitor deserialization processes and log any suspicious activity.

**Detection**:
- Use intrusion detection systems (IDS) to monitor for signs of deserialization attacks.
- Implement logging and monitoring to detect unusual patterns in deserialization activities.

**Prevention**:
- Validate and sanitize user input before deserializing it.
- Use safe deserialization libraries and disable global imports.
- Run deserialization processes in a sandboxed environment.

**Secure Coding Practices**:
- Always validate and sanitize user input before deserializing it.
- Use safe deserialization libraries and disable global imports.
- Run deserialization processes in a sandboxed environment.

### Real-World Examples and Breaches

#### Apache Struts (CVE-2015-4852)

In 2015, a critical vulnerability (CVE-2015-4852) was discovered in Apache Struts, which allowed attackers to execute arbitrary commands by exploiting the deserialization of Java objects. This vulnerability led to several high-profile breaches, including the Equifax breach in 2017.

#### pyyaml (CVE-2017-17438)

In 2017, a vulnerability (CVE-2017-17438) was discovered in the `pyyaml` library, which allowed attackers to execute arbitrary code by crafting malicious YAML data. This vulnerability affected several applications that used the `pyyaml` library for deserialization.

### Hands-On Labs

For hands-on practice with deserialization vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on deserialization vulnerabilities and how to exploit them.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes deserialization vulnerabilities for educational purposes.
- **DVWA (Damn Vulnerable Web Application)**: Includes deserialization vulnerabilities that can be exploited to learn about the risks and mitigation strategies.

By thoroughly understanding the concepts of serialization and deserialization, and implementing robust security measures, developers can significantly reduce the risk of deserialization-based attacks.

---
<!-- nav -->
[[01-Serialization and Deserialization Concepts|Serialization and Deserialization Concepts]] | [[API Security/23-RCE Via Deserialization in API/01-Unserialization Concept/00-Overview|Overview]] | [[03-Understanding Deserialization Vulnerabilities in APIs|Understanding Deserialization Vulnerabilities in APIs]]
