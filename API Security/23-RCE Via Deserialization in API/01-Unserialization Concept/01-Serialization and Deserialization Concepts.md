---
course: API Security
topic: RCE Via Deserialization in API
tags: [api-security]
---

## Serialization and Deserialization Concepts

### Introduction to Serialization and Deserialization

Serialization and deserialization are fundamental concepts in computer science, particularly in the context of APIs and network communication. These processes involve converting complex data structures into a format that can be easily stored or transmitted over a network, and then reconstructing those data structures from their serialized form.

#### What is Serialization?

Serialization is the process of converting an object or data structure into a format that can be stored or transmitted. This format is often a byte stream or a string representation. The primary goal of serialization is to enable the storage of objects in a persistent medium such as a file or database, or to transmit them over a network.

For example, consider a simple Java object:

```java
public class User {
    private String name;
    private int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // Getters and Setters
}
```

When this `User` object is serialized, it might look something like this:

```json
{
    "name": "John Doe",
    "age": 30
}
```

This JSON representation can be easily stored in a file or sent over a network.

#### What is Deserialization?

Deserialization is the reverse process of serialization. It involves taking a serialized format (such as a byte stream or a string) and reconstructing the original object or data structure from it. This is crucial for restoring the state of an object after it has been stored or transmitted.

Continuing with our `User` example, deserialization would take the JSON string and convert it back into a `User` object:

```java
User user = new User("John Doe", 30);
```

### Why Serialization and Deserialization Matter

Serialization and deserialization are essential for several reasons:

1. **Data Persistence**: They allow objects to be saved to a file or database and later restored.
2. **Network Communication**: They enable the transmission of complex data structures over a network.
3. **Interoperability**: Different systems can exchange data using standardized formats like JSON or XML.

### How Serialization and Deserialization Work Under the Hood

#### Serialization Process

The serialization process typically involves the following steps:

1. **Object Traversal**: The system traverses the object graph, identifying all objects and their relationships.
2. **Data Conversion**: Each object is converted into a suitable format, such as JSON or XML.
3. **Output**: The serialized data is written to a file, database, or transmitted over a network.

For example, in Python, the `pickle` module can serialize an object:

```python
import pickle

class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User("John Doe", 30)
serialized_user = pickle.dumps(user)
print(serialized_user)
```

#### Deserialization Process

The deserialization process involves the following steps:

1. **Input**: The serialized data is read from a file, database, or received over a network.
2. **Data Parsing**: The serialized data is parsed to extract the necessary information.
3. **Object Reconstruction**: The original object is reconstructed based on the parsed data.

Continuing with the Python example:

```python
deserialized_user = pickle.loads(serialized_user)
print(deserialized_user.name, deserialized_user.age)
```

### Common Formats for Serialization

Several formats are commonly used for serialization:

1. **JSON (JavaScript Object Notation)**: A lightweight data interchange format that is easy for humans to read and write, and easy for machines to parse and generate.
2. **XML (Extensible Markup Language)**: A markup language that defines a set of rules for encoding documents in a format that is both human-readable and machine-readable.
3. **YAML (YAML Ain't Markup Language)**: A human-friendly data serialization standard for all programming languages.
4. **Binary Formats**: Such as Protocol Buffers and MessagePack, which are more compact and efficient than text-based formats.

### Real-World Examples of Serialization and Deserialization

Serialization and deserialization are widely used in various applications. Here are some real-world examples:

1. **Web Services**: Many web services use JSON or XML to serialize and deserialize data exchanged between client and server.
2. **Databases**: Data is often serialized before being stored in a database and deserialized when retrieved.
3. **APIs**: APIs frequently use JSON or XML to serialize and deserialize data.

### Pitfalls and Risks

While serialization and deserialization are powerful tools, they also introduce risks, particularly in the context of API security.

#### Risks Associated with Deserialization

One of the most significant risks associated with deserialization is Remote Code Execution (RCE). This occurs when an attacker crafts a malicious serialized object that, when deserialized, executes arbitrary code on the server.

##### Real-World Example: CVE-2015-4852

CVE-2015-4852 is a critical vulnerability in Apache Struts 2 that allows remote code execution through deserialization. An attacker could send a specially crafted serialized object to the server, which, upon deserialization, would execute arbitrary commands.

Here is a simplified example of how this might work:

```java
// Malicious serialized object
String maliciousSerializedObject = "...";

// Deserialization
ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(maliciousSerializedObject.getBytes()));
ois.readObject(); // Executes arbitrary code
```

### How to Prevent / Defend Against Deserialization Attacks

To prevent deserialization attacks, several strategies can be employed:

#### Secure Coding Practices

1. **Validate Input**: Ensure that all input is validated and sanitized before deserialization.
2. **Use Safe Libraries**: Use libraries that have built-in protections against deserialization attacks.
3. **Whitelist Classes**: Only allow deserialization of trusted classes.

#### Configuration Hardening

1. **Disable Unnecessary Features**: Disable features that are not required, such as unnecessary serialization mechanisms.
2. **Enable Security Features**: Enable security features provided by frameworks and libraries.

#### Detection and Monitoring

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual deserialization activities.
2. **Intrusion Detection Systems (IDS)**: Use IDS to detect and alert on potential deserialization attacks.

#### Secure Code Examples

Here is an example of how to securely handle deserialization in Java:

```java
import java.io.*;

public class SafeDeserializer {
    public static Object safeDeserialize(byte[] data) throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data))) {
            ois.setObjectInputFilter(ObjectInputFilter.Config.createFilter("com.example.MyClass"));
            return ois.readObject();
        }
    }
}

// Usage
byte[] data = ...; // Serialized data
try {
    Object obj = SafeDeserializer.safeDeserialize(data);
} catch (IOException | ClassNotFoundException e) {
    e.printStackTrace();
}
```

### Conclusion

Serialization and deserialization are fundamental processes in computer science, enabling data persistence and network communication. However, they also introduce risks, particularly in the context of API security. By understanding these processes and implementing secure coding practices, configuration hardening, and detection mechanisms, developers can mitigate the risks associated with deserialization attacks.

### Practice Labs

For hands-on practice with API security and deserialization attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on deserialization vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for learning about various security issues, including deserialization.
- **DVWA (Damn Vulnerable Web Application)**: Contains exercises on deserialization vulnerabilities.

These labs will help you gain practical experience in identifying and preventing deserialization attacks.

---
<!-- nav -->
[[API Security/23-RCE Via Deserialization in API/01-Unserialization Concept/00-Overview|Overview]] | [[02-Unserialization Concept|Unserialization Concept]]
