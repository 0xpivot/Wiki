---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Dynamic Versioning in CI/CD Pipelines

### Introduction to Dynamic Versioning

Dynamic versioning in CI/CD pipelines is a critical practice that ensures each build and deployment is uniquely identifiable and traceable. This is particularly important in environments where continuous integration and delivery are practiced, as it helps maintain consistency and reliability across different stages of the development lifecycle. By dynamically setting the version numbers, developers can easily track changes, roll back to specific versions, and ensure that the correct version of the application is deployed.

### Importance of Dynamic Versioning

#### What is Dynamic Versioning?

Dynamic versioning refers to the process of automatically generating unique version numbers for each build or release of an application. This is typically done through automated scripts or tools within the CI/CD pipeline. The version number is often derived from a combination of factors such as the current date, build number, or commit hash.

#### Why is Dynamic Versioning Important?

Dynamic versioning is crucial because it provides several benefits:

1. **Traceability**: Each build has a unique identifier, making it easier to track changes and identify the exact version of the codebase.
2. **Consistency**: Ensures that the same version of the application is used consistently across different environments (development, testing, production).
3. **Rollback Mechanism**: Facilitates easy rollback to a previous version if issues arise in the newer version.
4. **Automation**: Integrates seamlessly with CI/CD pipelines, reducing manual errors and improving efficiency.

### Setting Up Dynamic Versioning in Jenkins

In the context of Jenkins, dynamic versioning can be implemented using various plugins and scripts. One common approach is to use Maven for version management and Docker for containerization.

#### Maven Version Management

Maven is a popular build automation tool that supports version management through its `pom.xml` file. The `maven-release-plugin` can be used to automate the process of incrementing the version number.

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <!-- Other configurations -->
</project>
```

The `maven-release-plugin` can be configured to automatically update the version number in the `pom.xml` file.

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-release-plugin</artifactId>
            <version>3.0.0-M5</version>
            <configuration>
                <autoVersionSubmodules>true</autoVersionSubmodules>
                <useReleaseProfile>false</useReleaseProfile>
                <releaseProfiles>release</releaseProfiles>
                <goals>deploy</goals>
            </configuration>
        </plugin>
    </plugins>
</build>
```

#### Incrementing the Version Number

To increment the version number, you can use the following Maven command:

```bash
mvn release:prepare release:perform
```

This command will:

1. Update the version number in the `pom.xml` file.
2. Commit the changes.
3. Tag the release in the repository.
4. Perform the release build.

### Generating New Docker Image Version

Once the version number is incremented, the next step is to generate a new Docker image version. This can be achieved by tagging the Docker image with the updated version number.

#### Dockerfile Example

A typical `Dockerfile` might look like this:

```dockerfile
FROM openjdk:11-jdk-slim
WORKDIR /app
COPY target/my-app.jar /app/
CMD ["java", "-jar", "my-app.jar"]
```

#### Building and Tagging the Docker Image

To build and tag the Docker image with the updated version number, you can use the following commands:

```bash
# Build the Docker image
docker build -t my-app:latest .

# Tag the Docker image with the new version number
docker tag my-app:latest my-app:<new-version-number>
```

### Integrating with Jenkins Pipeline

To integrate this process into a Jenkins pipeline, you can define a new stage that handles the version increment and Docker image tagging.

#### Jenkins Pipeline Configuration

Here is an example of a Jenkins pipeline configuration:

```groovy
pipeline {
    agent any

    stages {
        stage('Increment Version') {
            steps {
                script {
                    // Run Maven command to increment version
                    sh 'mvn release:prepare release:perform'
                }
            }
        }

        stage('Build App') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t my-app:latest .'
                    // Tag the Docker image with the new version number
                    def newVersion = readFile('target/version.txt').trim()
                    sh "docker tag my-app:latest my-app:${newVersion}"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Deploy the Docker image
                    sh 'docker push my-app:<new-version-number>'
                }
            }
        }
    }
}
```

### Using the Incremented Image Name in Docker Compose

Finally, the incremented image name can be used in a `docker-compose.yml` file to ensure that the correct version of the application is deployed.

#### Docker Compose Example

Here is an example of a `docker-compose.yml` file:

```yaml
version: '3'
services:
  app:
    image: my-app:<new-version-number>
    ports:
      - "8080:8080"
```

### Pitfalls and Common Mistakes

#### Hardcoding Version Numbers

One of the most common mistakes is hardcoding version numbers in the pipeline configuration. This defeats the purpose of dynamic versioning and can lead to inconsistencies and errors.

#### Incorrect Versioning Strategy

Another pitfall is using an incorrect versioning strategy. For example, using a simple increment strategy (e.g., 1.0.0, 1.0.1, etc.) may not provide enough granularity for tracking changes. A more robust strategy, such as semantic versioning (MAJOR.MINOR.PATCH), is recommended.

### Real-World Examples and Case Studies

#### Recent CVEs and Breaches

Dynamic versioning plays a crucial role in maintaining the integrity and security of applications. For instance, in the case of the Log4j vulnerability (CVE-2021-44228), having a robust versioning system allowed organizations to quickly identify and patch affected versions of the library.

#### Real-World Implementation

Consider a scenario where a company uses Jenkins for CI/CD and Docker for containerization. They implement dynamic versioning to ensure that each build is uniquely identifiable. This allows them to quickly identify and roll back to a previous version if a security vulnerability is discovered in a newer version.

### How to Prevent / Defend

#### Detection

To detect issues related to versioning, you can:

1. **Automate Version Checks**: Use tools like SonarQube to automatically check for outdated dependencies.
2. **Monitor Logs**: Monitor logs for any errors related to version mismatches.

#### Prevention

To prevent issues related to versioning, you can:

1. **Use Semantic Versioning**: Adopt a consistent versioning strategy like semantic versioning.
2. **Automate Version Increment**: Use tools like Maven to automate the version increment process.
3. **Tag Releases**: Ensure that each release is tagged in the version control system.

#### Secure Coding Fixes

Here is an example of a vulnerable versus a secure versioning implementation:

**Vulnerable Code**

```groovy
pipeline {
    agent any

    stages {
        stage('Build App') {
            steps {
                script {
                    // Hardcoded version number
                    sh 'docker build -t my-app:1.0.0 .'
                }
            }
        }
    }
}
```

**Secure Code**

```groovy
pipeline {
    agent any

    stages {
        stage('Increment Version') {
            steps {
                script {
                    // Run Maven command to increment version
                    sh 'mvn release:prepare release:perform'
                }
            }
        }

        stage('Build App') {
            steps {
                script {
                    // Build the Docker image
                    sh 'docker build -t my-app:latest .'
                    // Tag the Docker image with the new version number
                    def newVersion = readFile('target/version.txt').trim()
                    sh "docker tag my-app:latest my-app:${newVersion}"
                }
            }
        }
    }
}
```

### Conclusion

Dynamic versioning is a fundamental aspect of modern CI/CD pipelines. It ensures that each build is uniquely identifiable and traceable, facilitating better tracking, consistency, and security. By integrating dynamic versioning into your pipeline, you can improve the overall quality and reliability of your application deployments.

### Practice Labs

For hands-on experience with dynamic versioning in CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on CI/CD pipelines and version management.
- **OWASP Juice Shop**: Provides a practical environment to experiment with CI/CD pipelines and versioning strategies.
- **DVWA (Damn Vulnerable Web Application)**: Useful for understanding the impact of versioning in real-world applications.
- **WebGoat**: Includes exercises on CI/CD pipelines and version management.

These labs will help you gain practical experience and deepen your understanding of dynamic versioning in CI/CD pipelines.

---
<!-- nav -->
[[01-Dynamic Versioning in CICD Pipeline|Dynamic Versioning in CICD Pipeline]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/21-Dynamic Versioning In CI CD Pipeline/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/21-Dynamic Versioning In CI CD Pipeline/03-Practice Questions & Answers|Practice Questions & Answers]]
