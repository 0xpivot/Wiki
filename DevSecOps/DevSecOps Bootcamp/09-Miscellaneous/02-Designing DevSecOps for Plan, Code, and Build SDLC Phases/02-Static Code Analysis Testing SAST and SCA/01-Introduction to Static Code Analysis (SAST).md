---
course: DevSecOps
topic: Designing DevSecOps for Plan, Code, and Build SDLC Phases
tags: [devsecops]
---

## Introduction to Static Code Analysis (SAST)

Static Code Analysis (SAST) is a critical component of the DevSecOps methodology, particularly during the planning, coding, and building phases of the Software Development Life Cycle (SDLC). SAST tools analyze source code without executing it, identifying potential security vulnerabilities and coding errors. This analysis helps developers catch issues early in the development process, reducing the overall cost of remediation and improving the security posture of the application.

### What is SAST?

SAST stands for Static Application Security Testing. It is a type of security testing that analyzes the source code of an application to identify security vulnerabilities and coding errors. Unlike Dynamic Application Security Testing (DAST), which requires the application to be running, SAST operates on the static source code itself.

#### Why Use SAST?

The primary reasons for using SAST include:

1. **Early Detection**: Identifying security issues early in the development cycle allows for quicker and less expensive fixes.
2. **Comprehensive Coverage**: SAST can analyze the entire codebase, including parts that may not be easily reachable through dynamic testing.
3. **Automation**: SAST can be integrated into continuous integration (CI) pipelines, providing automated feedback on code quality and security.
4. **Reduced False Negatives**: By analyzing the source code directly, SAST can provide more accurate results compared to DAST, which might miss certain vulnerabilities due to incomplete test coverage.

### How Does SAST Work?

SAST tools operate by parsing the source code and applying various rules and heuristics to identify potential security issues. These rules are typically based on known vulnerabilities, coding standards, and security best practices. The process involves several steps:

1. **Parsing**: The tool reads and parses the source code, creating an abstract syntax tree (AST) that represents the structure of the code.
2. **Analysis**: The AST is analyzed against a set of predefined rules and heuristics to identify potential security issues.
3. **Reporting**: The tool generates a report detailing the identified issues, including their severity, location in the code, and suggested remediations.

#### Example of SAST in Action

Consider a simple Python function that takes user input and writes it to a file:

```python
def write_to_file(user_input):
    with open('output.txt', 'w') as f:
        f.write(user_input)
```

A SAST tool might flag this function for potential security risks, such as:

- **Path Traversal**: The `user_input` could contain a path traversal attack (e.g., `../../../../etc/passwd`).
- **File Injection**: The `user_input` could contain malicious content that could be executed when the file is read.

### False Positives in SAST

One of the challenges with SAST is the presence of false positives. False positives occur when the tool incorrectly identifies a piece of code as containing a security issue when it does not. This can happen due to the limited context available to the scanner, which only has access to the raw source code.

#### Causes of False Positives

1. **Limited Context**: SAST tools lack the runtime context that DAST tools have. They cannot determine the actual execution paths or the values of variables at runtime.
2. **Complex Code Structures**: Modern applications often have complex code structures, making it difficult for SAST tools to accurately determine the flow of data and control.
3. **Configuration Issues**: Incorrectly configured SAST tools can lead to false positives. For example, overly strict rules or misconfigured rule sets can result in many false alarms.

#### Managing False Positives

To manage false positives effectively, consider the following strategies:

1. **Tuning Rules**: Customize the rulesets to better match the specific requirements and context of your application.
2. **Code Reviews**: Conduct manual code reviews to verify the findings of the SAST tool.
3. **Integration with CI/CD**: Integrate SAST into your CI/CD pipeline to automatically run scans and review results.
4. **Training and Awareness**: Educate developers about the importance of SAST and how to interpret its results.

### Real-World Examples of SAST

Recent vulnerabilities and breaches highlight the importance of SAST in identifying and mitigating security issues early in the development process.

#### Example 1: Heartbleed Bug (CVE-2014-0160)

The Heartbleed bug was a serious vulnerability in the OpenSSL cryptographic software library. A SAST tool could have potentially identified this issue by analyzing the code for improper handling of memory buffers.

```c
static int
tls1_process_heartbeat(SSL *s)
{
    unsigned char *p = s->rlayer.rrec.data;
    unsigned short hbtype;
    unsigned int payload;

    /* Read the message type */
    hbtype = *p++;
    /* Read the payload length */
    n2s(p, payload);
    if (payload == 0) {
        /* Nothing follows. */
    } else if (payload > 18 || payload < 1) {
        /* Silently discard inappropriate messages */
        return -1;
    }
    /* Read the payload */
    p += payload;
    /* Read the padding */
    p += 18 - payload;
    /* Read the padding length */
    n2s(p, payload);
    if (payload > 18 || payload < 1) {
        /* Silently discard inappropriate messages */
        return -1;
    }
    /* Read the padding */
    p += payload;
    /* Read the heartbeat message */
    if (hbtype == TLS1_HB_REQUEST) {
        unsigned char *buffer, *bp;
        int r;

        /* Create the response message */
        buffer = OPENSSL_malloc(1 + 2 + payload + 16); // Extra random bytes
        bp = buffer;

        /* Enter response type, length and copy payload */
        *bp++ = TLS1_HB_RESPONSE;
        s2n(payload, bp);
        memcpy(bp, p - payload, payload);
        bp += payload;
        /* Add some random stuff at the end */
        RAND_bytes(bp, 16);

        /* Send the response */
        r = ssl_write(s, buffer, bp - buffer);
        OPENSSL_free(buffer);
        if (r <=  0)
            return r;
    }

    return 1;
}
```

In this example, the SAST tool could have flagged the improper handling of the payload length, leading to a buffer overflow.

#### Example 2: Equifax Data Breach (CVE-2017-5638)

The Equifax data breach was caused by a vulnerability in Apache Struts. A SAST tool could have identified the improper handling of user input, leading to remote code execution.

```java
public class VulnerableAction extends ActionSupport {
    private String parameter;

    public void setParameter(String parameter) {
        this.parameter = parameter;
    }

    public String execute() throws Exception {
        if (parameter != null) {
            // Vulnerable code
            Runtime.getRuntime().exec(parameter);
        }
        return SUCCESS;
    }
}
```

In this example, the SAST tool could have flagged the use of `Runtime.getRuntime().exec()` with unvalidated user input, leading to remote code execution.

### Integrating SAST into the CI/CD Pipeline

Integrating SAST into the CI/CD pipeline ensures that security checks are performed automatically and consistently throughout the development process. This integration can be achieved using various tools and frameworks.

#### Example Configuration with SonarQube

SonarQube is a popular open-source platform for continuous inspection of code quality. Here’s an example of how to integrate SonarQube into a CI/CD pipeline using Jenkins:

```yaml
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarQube Scanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }
    }
}
```

In this example, the `withSonarQubeEnv` step sets up the environment variables required by SonarQube, and the `sh "${scannerHome}/bin/sonar-scanner"` command runs the SonarQube analysis.

### Open Source and Commercial SAST Tools

There are numerous SAST tools available, both open source and commercial. Some popular options include:

- **SonarQube**: An open-source platform for continuous inspection of code quality.
- **Fortify**: A commercial SAST tool by Micro Focus.
- **Veracode**: A commercial SAST tool that provides comprehensive security testing.
- **Checkmarx**: A commercial SAST tool that supports multiple programming languages.

#### NIST List of Source Code Security Analyzers

The National Institute for Standards in Technology (NIST) maintains a list of source code security analyzers, which can be found on their website. This list includes both open-source and commercial products, providing a comprehensive resource for selecting appropriate SAST tools.

### How to Prevent / Defend Against SAST Limitations

To effectively use SAST and mitigate its limitations, follow these best practices:

1. **Regular Updates**: Keep your SAST tools updated to ensure they have the latest rules and heuristics.
2. **Customization**: Customize the rulesets to better match the specific requirements and context of your application.
3. **Manual Review**: Conduct manual code reviews to verify the findings of the SAST tool.
4. **Training and Awareness**: Educate developers about the importance of SAST and how to interpret its results.
5. **Integration with CI/CD**: Integrate SAST into your CI/CD pipeline to automatically run scans and review results.

#### Secure Coding Practices

Implementing secure coding practices can help prevent many of the issues identified by SAST tools. Here are some examples:

- **Input Validation**: Always validate user input to prevent injection attacks.
- **Error Handling**: Properly handle errors to prevent information leakage.
- **Secure Configuration**: Ensure that configurations are secure and do not expose sensitive information.

#### Example of Secure Coding

Consider the previous Python function that writes user input to a file. Here is a secure version:

```python
import os

def write_to_file(user_input):
    if not os.path.isabs(user_input):
        with open('output.txt', 'w') as f:
            f.write(user_input)
    else:
        raise ValueError("Invalid user input")
```

In this secure version, the function checks if the `user_input` is an absolute path and raises an error if it is, preventing path traversal attacks.

### Conclusion

Static Code Analysis (SAST) is a crucial tool in the DevSecOps methodology, helping to identify security vulnerabilities and coding errors early in the development process. While SAST can generate false positives, integrating it into the CI/CD pipeline and following best practices can significantly improve the security of your applications. By leveraging SAST tools and implementing secure coding practices, you can reduce the overall cost of remediation and improve the security posture of your applications.

### Practice Labs

For hands-on experience with SAST, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including SAST.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is vulnerable by design.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide practical experience with SAST and other security testing techniques, helping you to master the skills needed for effective DevSecOps.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/02-Designing DevSecOps for Plan, Code, and Build SDLC Phases/02-Static Code Analysis Testing SAST and SCA/00-Overview|Overview]] | [[02-Introduction to Static Code Analysis Testing (SAST) and Software Composition Analysis (SCA)|Introduction to Static Code Analysis Testing (SAST) and Software Composition Analysis (SCA)]]
