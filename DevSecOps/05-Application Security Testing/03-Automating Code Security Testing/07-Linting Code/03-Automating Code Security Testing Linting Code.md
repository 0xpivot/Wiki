---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Automating Code Security Testing: Linting Code

### Introduction to Linting

Linting is an automated process used to analyze source code for programming errors, bugs, stylistic errors, and suspicious constructs. The primary goal of linting is to improve code quality and maintainability by identifying potential issues before they become problematic. Linters can be run at various stages of the development lifecycle, including the pre-commit phase and the build phase.

#### Pre-Commit Phase

In the pre-commit phase, linting is performed locally on the developer’s machine before the code is committed to the local repository. This ensures that the code adheres to coding standards and best practices before it is even checked into the version control system. By catching issues early, developers can address them immediately, reducing the likelihood of introducing bugs into the codebase.

**Example:**

Consider a scenario where a developer is working on a Python project. Before committing the changes, the developer runs a linter like `flake8` to check for common coding errors and style violations.

```python
# Example Python code with linting issues
def calculate_sum(a, b):
    return a + b

print(calculate_sum(1, 2))
```

Running `flake8` on this code might produce the following output:

```bash
$ flake8 my_script.py
my_script.py:1:1: E302 expected 2 blank lines, found 1
my_script.py:1:1: W391 blank line at end of file
```

This output indicates that the code does not adhere to the recommended number of blank lines between functions and that there is an extra blank line at the end of the file. Addressing these issues ensures that the code is clean and follows established conventions.

#### Build Phase

During the build phase, the build server pulls the code from a Git repository and performs linting on it. This ensures that the code meets the required standards before it is built and deployed. The build server can automatically run linters as part of the continuous integration (CI) pipeline, providing feedback to the developers about any issues found.

**Example:**

Consider a CI pipeline using Jenkins. The pipeline includes a step to run a linter like `Hadolint` on Dockerfiles. Here is an example of a Jenkinsfile that includes this step:

```groovy
pipeline {
    agent any
    stages {
        stage('Lint') {
            steps {
                sh 'hadolint Dockerfile'
            }
        }
        stage('Build') {
            steps {
                sh 'docker build -t my_image .'
            }
        }
    }
}
```

In this example, the `Lint` stage runs `hadolint` on the `Dockerfile`. If any issues are found, the build fails, and the developer is notified to address the issues.

### Linters for Different Languages and Tools

Linters are available for various programming languages and tools. Some popular linters include:

- **Python:** `flake8`, `pylint`
- **JavaScript:** `eslint`, `jshint`
- **Java:** `checkstyle`, `spotbugs`
- **Docker:** `Hadolint`

Each linter has its own set of rules and configurations that can be customized to meet specific project requirements.

#### Hadolint for Dockerfiles

`Hadolint` is a linter specifically designed for Dockerfiles. It checks for common issues such as unnecessary layers, redundant commands, and security vulnerabilities. Running `Hadolint` on a Dockerfile helps ensure that the Docker image is optimized and secure.

**Example:**

Consider the following Dockerfile:

```Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    wget

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
```

Running `Hadolint` on this Dockerfile might produce the following output:

```bash
$ hadolint Dockerfile
DL3008 warning: [line 3] Use `RUN apt-get update && apt-get install -y <your-package> && rm -rf /var/lib/apt/lists/*` to avoid unnecessary layers
DL4006 warning: [line 3] Avoid installing packages inside a container
```

This output indicates that the `apt-get` commands should be combined to avoid unnecessary layers and that installing packages inside the container is generally discouraged. Addressing these issues ensures that the Dockerfile is optimized and secure.

### How to Prevent / Defend

To effectively use linting as part of a DevSecOps pipeline, it is essential to implement the following best practices:

#### Detection

- **Automate linting:** Integrate linters into the CI/CD pipeline to automatically run them on every commit and build.
- **Customize rules:** Configure linters to enforce project-specific coding standards and security policies.
- **Regular updates:** Keep linters up to date to ensure they catch the latest issues and vulnerabilities.

#### Prevention

- **Educate developers:** Provide training and documentation to help developers understand the importance of linting and how to use linters effectively.
- **Enforce linting:** Make linting a mandatory part of the development process, ensuring that code cannot be committed or built unless it passes linting checks.
- **Review linting reports:** Regularly review linting reports to identify and address recurring issues and patterns.

#### Secure Coding Fixes

Here is an example of a vulnerable Dockerfile and its secure version:

**Vulnerable Dockerfile:**

```Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    wget

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
```

**Secure Dockerfile:**

```Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    wget && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "app.py"]
```

In the secure version, the `apt-get` commands are combined to avoid unnecessary layers, and the `rm -rf /var/lib/apt/lists/*` command is added to remove temporary files after installation.

### Real-World Examples

Linting has been instrumental in identifying and preventing security vulnerabilities in real-world scenarios. For example, in the case of the Log4j vulnerability (CVE-2021-44228), linters could have helped identify insecure logging practices and configurations.

**Example:**

Consider a Java application that uses Log4j for logging. A linter like `spotbugs` could have identified insecure logging configurations and alerted the developers to the potential risks.

```java
// Vulnerable Java code
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MyApp {
    private static final Logger logger = LogManager.getLogger(MyApp.class);

    public void logMessage(String message) {
        logger.info(message);
    }
}
```

Running `spotbugs` on this code might produce the following output:

```bash
$ spotbugs -textui -effort:max -outputformat xml -output spotbugs.xml MyApp.java
SpotBugs found 1 issue(s)
```

The output indicates that the code contains a potential security vulnerability related to insecure logging. Addressing this issue ensures that the application is secure and compliant with best practices.

### Hands-On Labs

To gain practical experience with linting, consider the following hands-on labs:

- **PortSwigger Web Security Academy:** Offers interactive labs to practice web application security testing, including linting.
- **OWASP Juice Shop:** Provides a vulnerable web application to practice security testing and linting.
- **DVWA (Damn Vulnerable Web Application):** Allows users to practice security testing on a deliberately vulnerable web application.
- **WebGoat:** Offers a series of lessons to learn about web application security, including linting.

These labs provide a comprehensive learning experience and help reinforce the concepts covered in this chapter.

### Conclusion

Linting is a crucial component of DevSecOps, helping to ensure that code is clean, maintainable, and secure. By integrating linters into the development process, developers can catch and address issues early, reducing the likelihood of introducing bugs and vulnerabilities. Using linters effectively requires a combination of automation, customization, and education, ensuring that code adheres to best practices and security policies.

---
<!-- nav -->
[[02-Introduction to Linting Code|Introduction to Linting Code]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/09-Linting Code/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/09-Linting Code/04-Practice Questions & Answers|Practice Questions & Answers]]
