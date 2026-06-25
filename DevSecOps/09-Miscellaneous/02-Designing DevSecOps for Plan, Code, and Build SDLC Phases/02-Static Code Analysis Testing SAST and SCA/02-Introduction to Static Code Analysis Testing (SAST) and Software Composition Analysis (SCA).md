---
course: DevSecOps
topic: Designing DevSecOps for Plan, Code, and Build SDLC Phases
tags: [devsecops]
---

## Introduction to Static Code Analysis Testing (SAST) and Software Composition Analysis (SCA)

In the realm of DevSecOps, ensuring the security of software throughout its lifecycle is paramount. Two critical tools that play a significant role in this process are Static Application Security Testing (SAST) and Software Composition Analysis (SCA). Both are essential components of the Plan, Code, and Build phases of the Software Development Life Cycle (SDLC).

### Understanding SAST

**What is SAST?**

Static Application Security Testing (SAST), also known as Static Analysis Security Testing, is a method of analyzing source code to identify potential security vulnerabilities. Unlike dynamic testing methods, which require the code to be executed, SAST operates on the source code itself, allowing it to detect issues before the code is even compiled or run.

**Why is SAST Important?**

SAST is crucial because it helps identify security flaws early in the development process. By catching these issues during the coding phase, developers can address them before the code is deployed, reducing the risk of vulnerabilities being exploited in production environments. This proactive approach is more cost-effective and efficient than trying to fix security issues after deployment.

**How Does SAST Work?**

SAST tools work by parsing the source code and applying a set of rules or heuristics to identify patterns that may indicate security vulnerabilities. These rules are typically based on known security issues and coding practices that are prone to introducing vulnerabilities. The process involves:

1. **Parsing the Source Code:** The tool reads the source code and creates an abstract syntax tree (AST) to understand the structure of the code.
2. **Applying Rules:** The tool applies a set of predefined rules to the AST to identify potential security issues.
3. **Reporting Findings:** The tool generates a report detailing the identified vulnerabilities, including their severity and potential impact.

#### Example of SAST in Action

Consider a simple C program that uses `strcpy` without proper bounds checking:

```c
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[10];
    strcpy(buffer, "This is a very long string");
    printf("%s\n", buffer);
    return 0;
}
```

A SAST tool would flag this code as potentially vulnerable due to the use of `strcpy`, which does not perform bounds checking. The tool might generate a report similar to the following:

```
[Vulnerability] Buffer Overflow
File: example.c
Line: 6
Description: The function 'strcpy' is used without proper bounds checking, leading to a potential buffer overflow.
Severity: High
```

### Understanding SCA

**What is SCA?**

Software Composition Analysis (SCA), also known as Software Composition Analysis, is a process that identifies open-source components used in a software project and checks these components against known vulnerabilities. Open-source components are widely used in modern software development, and SCA helps ensure that these components are secure.

**Why is SCA Important?**

SCA is important because most software today includes open-source components, and these components can introduce vulnerabilities if they are not properly vetted. By identifying and addressing these vulnerabilities early in the development process, SCA helps reduce the risk of security issues in the final product.

**How Does SCA Work?**

SCA tools work by scanning the software project to identify open-source components and then comparing these components against publicly available vulnerability databases. The process involves:

1. **Identifying Components:** The tool scans the project to identify all open-source components used.
2. **Comparing Against Databases:** The tool compares the identified components against vulnerability databases such as the National Vulnerability Database (NVD) or the Common Vulnerabilities and Exposures (CVE) list.
3. **Reporting Findings:** The tool generates a report detailing any vulnerabilities found in the open-source components.

#### Example of SCA in Action

Consider a Node.js project that uses the `lodash` library:

```json
{
  "name": "example-project",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "^4.17.21"
  }
}
```

An SCA tool would scan the `package.json` file and identify the `lodash` dependency. It would then check this dependency against vulnerability databases and generate a report similar to the following:

```
[Vulnerability] CVE-2021-21345
Component: lodash
Version: 4.17.21
Description: The lodash library contains a vulnerability that allows remote code execution.
Severity: Critical
```

### Differences Between SAST and SCA

While both SAST and SCA are important tools in the DevSecOps toolkit, they serve different purposes:

- **SAST** focuses on analyzing the source code of the application itself to identify security vulnerabilities.
- **SCA** focuses on analyzing the open-source components used in the application to identify vulnerabilities in those components.

### Recent Real-World Examples

#### SAST Example: Heartbleed Bug (CVE-2014-0160)

The Heartbleed bug was a serious vulnerability in the OpenSSL cryptographic software library. This vulnerability allowed attackers to read sensitive information from the memory of systems using OpenSSL, including private keys, passwords, and other sensitive data.

A SAST tool could have detected this issue by identifying the use of unsafe memory operations in the OpenSSL code. For example, the following C code snippet from OpenSSL contained the vulnerability:

```c
static int
tls1_process_heartbeat(SSL *s)
{
    unsigned short hbtype;
    unsigned int payload;

    /* Read type */
   hbtype = *p++;
    n--;
    /* Read length */
    payload = p[0] << 8 | p[1];
    p += 2;
    n -= 2;
    /* Read payload */
    if (1 + 2 + payload + 16 > n)
        return 0; /* Silently discard per RFC 6520 sec. 4 */
    /* Sequence number */
    for (i = 0; i < 8; i++)
        s->s3->handshake_buffer[i] = *p++;
    /* Payload */
    for (i = 0; i < payload; i++)
        s->s3->handshake_buffer[8 + i] = *p++;
    /* Padding */
    for (i = 0; i < 16 - payload % 16; i++)
        s->s3->handshake_buffer[8 + payload + i] = *p++;
    /* Random padding */
    for (i = 0; i < 16 - payload % 16; i++)
        s->s3->handshake_buffer[8 + payload + i] = rand();
    /* Sequence number */
    for (i = 0; i < 8; i++)
        s->s3->handshake_buffer[8 + payload + 16 - i] = *p++;
    /* Send response */
    if (hbtype == TLS1_HB_REQUEST)
    {
        unsigned char *p = s->wbuf;
        /* Create the response */
        *p++ = TLS1_HB_RESPONSE;
        *p++ = payload >> 8;
        *p++ = payload & 255;
        memcpy(p, s->s3->handshake_buffer, payload);
        p += payload;
        /* Add random padding */
        for (i = 0; i < 16 - payload % 16; i++)
            *p++ = rand();
        /* Send the response */
        if (!ssl_write(s))
            return -1;
    }
    return 1;
}
```

A SAST tool would flag the use of `memcpy` without proper bounds checking, indicating a potential buffer overflow vulnerability.

#### SCA Example: Log4j Vulnerability (CVE-2021-44228)

The Log4j vulnerability, also known as Log4Shell, was a critical vulnerability in the Apache Log4j logging framework. This vulnerability allowed attackers to execute arbitrary code on affected systems, leading to widespread exploitation.

An SCA tool would have identified the use of the vulnerable Log4j version and flagged it as a critical vulnerability. For example, consider a Java project that uses Log4j:

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.logging.log4j</groupId>
        <artifactId>log4j-core</artifactId>
        <version>2.14.1</version>
    </dependency>
</dependencies>
```

An SCA tool would scan the `pom.xml` file and identify the `log4j-core` dependency. It would then compare this dependency against vulnerability databases and generate a report similar to the following:

```
[Vulnerability] CVE-2021-44228
Component: log4j-core
Version: 2.14.1
Description: The Log4j library contains a vulnerability that allows remote code execution.
Severity: Critical
```

### How to Prevent / Defend

#### SAST Prevention and Defense

To prevent and defend against vulnerabilities detected by SAST, follow these steps:

1. **Code Review:** Conduct regular code reviews to ensure that security best practices are followed.
2. **Secure Coding Practices:** Implement secure coding practices, such as input validation, proper error handling, and avoiding unsafe functions.
3. **Regular Scans:** Run SAST tools regularly to catch new vulnerabilities as they are introduced.
4. **Fix Identified Issues:** Address any vulnerabilities identified by SAST tools promptly.

#### Example of Secure Code Fix

Consider the earlier example of the `strcpy` vulnerability. The secure version of the code would use `strncpy` with proper bounds checking:

```c
#include <stdio.h>
#include <string.h>

int main() {
    char buffer[10];
    strncpy(buffer, "This is a very long string", sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    printf("%s\n", buffer);
    return 0;
}
```

#### SCA Prevention and Defense

To prevent and defend against vulnerabilities detected by SCA, follow these steps:

1. **Dependency Management:** Use a dependency management tool to keep track of all open-source components used in the project.
2. **Regular Scans:** Run SCA tools regularly to catch new vulnerabilities in open-source components.
3. **Update Dependencies:** Keep all dependencies up to date to ensure that they are patched against known vulnerabilities.
4. **Use Trusted Sources:** Use trusted sources for open-source components, such as official repositories and reputable package managers.

#### Example of Secure Dependency Management

Consider the earlier example of the `lodash` dependency. The secure version of the `package.json` file would use a version that is not vulnerable:

```json
{
  "name": "example-project",
  "version": "1.0.0",
  "dependencies": {
    "lodash": "^4.17.22"
  }
}
```

### Conclusion

Both SAST and SCA are essential tools in the DevSecOps toolkit. SAST helps identify security vulnerabilities in the source code of the application itself, while SCA helps identify vulnerabilities in open-source components used in the application. By using these tools effectively, developers can ensure that their software is secure throughout its lifecycle.

### Practice Labs

For hands-on experience with SAST and SCA, consider the following practice labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on various web security topics, including SAST.
- **OWASP Juice Shop:** A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **CloudGoat:** A series of labs designed to teach cloud security concepts using AWS.
- **Pacu:** A collection of penetration testing modules for AWS.

These labs provide practical experience with SAST and SCA tools and help reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[01-Introduction to Static Code Analysis (SAST)|Introduction to Static Code Analysis (SAST)]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/02-Static Code Analysis Testing SAST and SCA/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/02-Static Code Analysis Testing SAST and SCA/03-Practice Questions & Answers|Practice Questions & Answers]]
