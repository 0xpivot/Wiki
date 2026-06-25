---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Cryptographic Failure and Hard-Coded Credentials

### Cryptographic Failure

Cryptographic failure refers to the improper implementation or usage of cryptographic algorithms and protocols, leading to vulnerabilities that can be exploited by attackers. This includes issues such as weak encryption, improper key management, and the use of deprecated or insecure cryptographic methods.

#### What is Cryptographic Failure?

Cryptographic failure occurs when cryptographic mechanisms are not used correctly or are implemented in a way that undermines their intended security properties. This can happen due to several reasons:

- **Weak Encryption**: Using weak encryption algorithms or modes that do not provide adequate protection against modern attacks.
- **Improper Key Management**: Poor handling of cryptographic keys, including storing them in insecure locations or using them for too long.
- **Deprecated Algorithms**: Using cryptographic algorithms that have been deprecated or are known to be insecure.

#### Why Does Cryptographic Failure Matter?

Cryptographic failure can lead to severe security breaches, including unauthorized access to sensitive data, data theft, and manipulation. For instance, if an application uses weak encryption, an attacker might be able to decrypt sensitive data, such as passwords or financial information, leading to significant financial and reputational damage.

#### How Does Cryptographic Failure Work Under the Hood?

When cryptographic mechanisms are not implemented correctly, they can be bypassed or exploited. For example, if an application uses a weak encryption algorithm, an attacker might be able to brute-force the encryption or use known vulnerabilities to decrypt the data.

Consider the following scenario:

```plaintext
An application uses a weak encryption algorithm, such as DES (Data Encryption Standard), which is now considered insecure due to its short key length (56 bits).

Attacker:
1. Identifies the use of DES in the application.
2. Uses a brute-force attack to try all possible 56-bit keys.
3. Decrypts the sensitive data.

Result:
Sensitive data, such as passwords or financial information, is exposed to the attacker.
```

#### Real-World Example: CVE-2019-11815

CVE-2019-11815 is a vulnerability in the OpenSSL library where the `RAND_bytes` function could return predictable output if called with a non-zero length argument. This could lead to weak encryption keys being generated, making it easier for attackers to guess or brute-force the keys.

```plaintext
Vulnerable Code:
```c
#include <openssl/rand.h>

unsigned char key[16];
RAND_bytes(key, sizeof(key));
```

Secure Code:
```c
#include <openssl/rand.h>
#include <openssl/err.h>

unsigned char key[16];
if (!RAND_bytes(key, sizeof(key))) {
    // Handle error
    ERR_print_errors_fp(stderr);
}
```

In the secure version, we check the return value of `RAND_bytes` to ensure that the call was successful. If it fails, we handle the error appropriately.

#### How to Prevent / Defend Against Cryptographic Failure

To prevent cryptographic failure, follow these best practices:

- **Use Strong Encryption**: Always use strong encryption algorithms and modes, such as AES (Advanced Encryption Standard) with a key size of at least 128 bits.
- **Proper Key Management**: Store cryptographic keys securely, such as in hardware security modules (HSMs) or encrypted key stores. Rotate keys regularly.
- **Avoid Deprecated Algorithms**: Do not use deprecated or insecure cryptographic algorithms. Stay updated with the latest security advisories and recommendations.

### Hard-Coded Credentials

Hard-coded credentials refer to the practice of embedding usernames, passwords, or other sensitive authentication information directly within the source code of an application. This is a serious security issue because it exposes sensitive information to anyone who has access to the source code.

#### What Are Hard-Coded Credentials?

Hard-coded credentials are sensitive authentication details, such as usernames and passwords, that are embedded directly within the source code of an application. This practice is highly discouraged because it makes it easy for attackers to obtain sensitive information by simply reading the source code.

#### Why Do Hard-Coded Credentials Matter?

Hard-coded credentials pose a significant security risk because they can be easily extracted by attackers. Once an attacker has access to the source code, they can extract the hard-coded credentials and use them to gain unauthorized access to systems or services.

#### How Do Hard-Coded Credentials Work Under the Hood?

When hard-coded credentials are used, they are stored in plain text within the source code. This means that anyone who has access to the source code can read the credentials directly. For example, consider the following code snippet:

```plaintext
Vulnerable Code:
```python
import requests

url = "https://api.example.com"
username = "admin"
password = "password123"

response = requests.get(url, auth=(username, password))
```

In this example, the username and password are hard-coded directly within the source code. An attacker who gains access to the source code can easily extract these credentials and use them to authenticate to the API.

#### Real-World Example: Equifax Breach (2017)

The Equifax breach in 2017 was partially attributed to the use of hard-coded credentials. Attackers were able to exploit a vulnerability in Apache Struts and gain access to the system. Once inside, they were able to find hard-coded credentials that allowed them to escalate their privileges and access sensitive data.

```plaintext
Vulnerable Code:
```java
public class DatabaseConnection {
    private static final String USERNAME = "admin";
    private static final String PASSWORD = "hardcodedpassword";

    public void connect() {
        // Connect to the database using the hard-coded credentials
    }
}
```

Secure Code:
```java
public class DatabaseConnection {
    private static final String USERNAME = System.getenv("DB_USERNAME");
    private static final String PASSWORD = System.getenv("DB_PASSWORD");

    public void connect() {
        // Connect to the database using environment variables
    }
}
```

In the secure version, the credentials are stored in environment variables rather than hard-coded within the source code. This makes it much harder for attackers to obtain the credentials.

#### How to Prevent / Defend Against Hard-Coded Credentials

To prevent the use of hard-coded credentials, follow these best practices:

- **Use Environment Variables**: Store sensitive credentials in environment variables rather than hard-coding them within the source code.
- **Configuration Files**: Use configuration files to store sensitive information, but ensure that these files are properly secured and not included in version control.
- **Secret Management Tools**: Use secret management tools, such as HashiCorp Vault or AWS Secrets Manager, to securely store and manage sensitive credentials.

### Using Insecure Protocols

Using insecure protocols, such as HTTP, can expose sensitive data during transmission. This is a critical security issue because it allows attackers to intercept and read data as it travels between the client and server.

#### What Are Insecure Protocols?

Insecure protocols are communication protocols that do not provide adequate security measures to protect data during transmission. The most common example of an insecure protocol is HTTP (HyperText Transfer Protocol), which transmits data in plain text and does not provide any form of encryption.

#### Why Do Insecure Protocols Matter?

Insecure protocols pose a significant security risk because they allow attackers to intercept and read sensitive data as it travels between the client and server. This can lead to data theft, manipulation, and other forms of unauthorized access.

#### How Do Insecure Protocols Work Under the Hood?

When data is transmitted using an insecure protocol, it is sent in plain text over the network. This means that anyone who has access to the network can intercept and read the data. For example, consider the following HTTP request:

```plaintext
HTTP Request:
```http
GET /api/data HTTP/1.1
Host: example.com
```

HTTP Response:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "credit_card_number": "1234-5678-9012-3456",
  "password": "mysecretpassword"
}
```

In this example, the sensitive data, including a credit card number and password, is transmitted in plain text. An attacker who intercepts this traffic can easily read and use the sensitive information.

#### Real-World Example: Heartbleed Bug (CVE-2014-0160)

The Heartbleed bug (CVE-2014-0160) was a serious vulnerability in the OpenSSL library that allowed attackers to steal sensitive information, such as passwords and private keys, from servers using TLS (Transport Layer Security). This vulnerability was particularly dangerous because it affected the encryption layer, allowing attackers to bypass the security provided by HTTPS.

```plaintext
Vulnerable Configuration:
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
    }
}
```

Secure Configuration:
```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    location / {
        proxy_pass https://backend;
    }
}
```

In the secure configuration, the server listens on port 443 (HTTPS) and uses SSL/TLS to encrypt the data. This ensures that the data is protected during transmission.

#### How to Prevent / Defend Against Insecure Protocols

To prevent the use of insecure protocols, follow these best practices:

- **Use Secure Protocols**: Always use secure protocols, such as HTTPS (HTTP over TLS), to encrypt data during transmission.
- **Enable HSTS**: Enable HTTP Strict Transport Security (HSTS) to ensure that browsers always use HTTPS when communicating with your server.
- **Disable Insecure Ciphers**: Disable insecure ciphers and protocols, such as SSLv3 and TLS 1.0, to prevent downgrade attacks.

### Summary

Cryptographic failure, hard-coded credentials, and the use of insecure protocols are serious security issues that can lead to significant data breaches and unauthorized access. To prevent these issues, it is essential to use strong encryption, proper key management, avoid hard-coding credentials, and use secure protocols for data transmission.

### Practice Labs

For hands-on experience with these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including topics related to cryptographic failures and insecure protocols.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including issues related to cryptographic failures and insecure protocols.

By following these best practices and engaging in hands-on practice, you can significantly improve the security of your applications and protect sensitive data from unauthorized access.

---
<!-- nav -->
[[12-Cloud Platform Misconfigurations|Cloud Platform Misconfigurations]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 1/00-Overview|Overview]] | [[14-Cryptographic Failures|Cryptographic Failures]]
