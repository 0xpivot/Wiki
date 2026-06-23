---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Versioning in Build Tools

### Background Theory

Versioning is a fundamental aspect of software development, particularly in the context of build tools such as Maven, Gradle, and npm. It allows developers to track changes, manage dependencies, and ensure that the correct versions of libraries and modules are used in their applications. The versioning scheme typically follows a format that includes major, minor, and patch numbers, sometimes with additional suffixes.

#### Major, Minor, Patch, and Suffix

The versioning scheme can be broken down into four main components:

1. **Major Version**: Represents significant changes, such as breaking API changes or major architectural shifts.
2. **Minor Version**: Indicates new features or enhancements that are backward-compatible.
3. **Patch Version**: Represents bug fixes or minor improvements that do not affect compatibility.
4. **Suffix**: Often used to denote pre-release stages (alpha, beta, rc) or special builds (SNAPSHOT).

For example, a version number `2.3.1-SNAPSHOT` indicates:
- Major version: 2
- Minor version: 3
- Patch version: 1
- Suffix: SNAPSHOT (indicating an in-progress build)

### Different Versioning Schemas

While the four-part schema (major.minor.patch.suffix) is widely used, there are variations:

1. **Two-Part Schema**: Some projects might use only major and minor versions (e.g., `1.2`).
2. **Three-Part Schema**: Others might use major, minor, and patch (e.g., `1.2.3`).

The choice of versioning schema depends on the project's needs and the conventions followed by the development team.

### Decision-Making Process

When deciding which version to increment, consider the nature of the changes:

- **Major Changes**: Increment the major version if the changes break backward compatibility.
- **Minor Changes**: Increment the minor version if new features are added but backward compatibility is maintained.
- **Patch Changes**: Increment the patch version for bug fixes and minor improvements.

### Manual vs. Automated Versioning

#### Manual Versioning

Manually updating the version in files like `pom.xml`, `package.json`, or `build.gradle` is possible but error-prone and time-consuming. For example, in a `pom.xml` file:

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.2.3-SNAPSHOT</version>
    <!-- Other configurations -->
</project>
```

Similarly, in a `package.json` file:

```json
{
  "name": "my-app",
  "version": "1.2.3",
  "dependencies": {
    "express": "^4.17.1"
  }
}
```

#### Automated Versioning

Automated versioning is more efficient and reduces human error. Tools like Maven, Gradle, and npm provide mechanisms to automatically update versions during the build process.

### Automating Versioning in CI/CD Pipelines

In a Continuous Integration/Continuous Deployment (CI/CD) pipeline, versioning should be automated to ensure consistency and reliability. For instance, Jenkins can be configured to automatically increment the version upon each build.

#### Example with Jenkins

Consider a Jenkins pipeline script that increments the version:

```groovy
pipeline {
    agent any
    environment {
        VERSION = readFile('version.txt').trim()
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean install'
                script {
                    def versionParts = VERSION.tokenize('.')
                    def major = versionParts[0] as int
                    def minor = versionParts[1] as int
                    def patch = versionParts[2] as int
                    // Increment patch version
                    patch++
                    VERSION = "${major}.${minor}.${patch}"
                    writeFile file: 'version.txt', text: "${VERSION}\n"
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'mvn deploy'
            }
        }
    }
}
```

This script reads the current version from `version.txt`, increments the patch version, and writes the updated version back to the file.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the Log4j vulnerability (CVE-2021-44228), which affected many applications using the Log4j library. Proper version management could have helped mitigate the impact by ensuring that applications were using the latest, patched versions of the library.

#### Secure Coding Practices

To prevent vulnerabilities, ensure that all dependencies are up-to-date and follow secure coding practices. For example, in a `pom.xml` file, specify the exact version of a dependency:

```xml
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.17.1</version>
</dependency>
```

### How to Prevent / Defend

#### Detection

Regularly scan your project dependencies for known vulnerabilities using tools like OWASP Dependency Check or Sonatype Nexus Lifecycle.

#### Prevention

1. **Use Version Ranges Wisely**: Avoid using open-ended version ranges (e.g., `^1.2.3`) unless necessary.
2. **Automate Version Updates**: Use tools like Dependabot or Renovate to automatically update dependencies.
3. **Secure Coding Practices**: Follow secure coding guidelines and regularly review dependencies.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of a `package.json` file:

**Vulnerable Version:**

```json
{
  "name": "my-app",
  "version": "1.2.3",
  "dependencies": {
    "express": "^4.17.1"
  }
}
```

**Secure Version:**

```json
{
  "name": "my-app",
  "version": "1.2.3",
  "dependencies": {
    "express": "4.17.1"
  }
}
```

### Hands-On Labs

For practical experience with versioning and CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers versioning and dependency management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning security concepts.

These labs provide a comprehensive understanding of versioning and its importance in modern software development.

### Conclusion

Understanding and implementing proper versioning is crucial for maintaining the integrity and security of software applications. By automating versioning in CI/CD pipelines, developers can ensure consistent and reliable builds, reducing the risk of vulnerabilities and errors.

---
<!-- nav -->
[[10-Semantic Versioning|Semantic Versioning]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/22-Increasing Application Version in Build Tools/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/22-Increasing Application Version in Build Tools/12-Practice Questions & Answers|Practice Questions & Answers]]
