---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Building Artifacts with Maven and Gradle

### Introduction to Build Tools

In the world of software development, especially in Java-based applications, build tools play a crucial role in automating the process of compiling source code, managing dependencies, and packaging the final artifact. Two of the most popular build tools for Java projects are Apache Maven and Gradle. Both tools provide a structured way to manage the build process, but they differ in their approach and features.

#### What is a Build Tool?

A build tool is a software utility that automates the creation of executable applications from source code. This automation includes tasks such as compiling source code, running tests, generating documentation, and packaging the final product. The primary goal of a build tool is to streamline the development process, reduce human error, and ensure consistency across different environments.

#### Why Use Build Tools?

Using build tools offers several advantages:

1. **Consistency**: Build tools ensure that the same steps are followed every time the project is built, leading to consistent results.
2. **Automation**: They automate repetitive tasks, saving developers time and reducing the likelihood of errors.
3. **Dependency Management**: Build tools handle dependency resolution, ensuring that all required libraries are included in the build.
4. **Reproducibility**: By defining the build process in a script, it becomes easier to reproduce the build environment on different machines.

### Maven Overview

Apache Maven is a widely used build tool for Java projects. It follows a convention-over-configuration philosophy, meaning that it assumes certain conventions about the project structure and naming, allowing developers to focus more on coding rather than configuring the build process.

#### Maven Project Structure

A typical Maven project follows a standard directory structure:

```plaintext
my-project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   └── resources/
│   └── test/
│       ├── java/
│       └── resources/
├── pom.xml
└── target/
```

- `src/main/java`: Contains the main source code.
- `src/main/resources`: Contains resources like configuration files.
- `src/test/java`: Contains test source code.
- `src/test/resources`: Contains test resources.
- `pom.xml`: The project object model file, which contains metadata and configuration for the project.
- `target/`: Directory where the compiled classes and artifacts are stored.

#### Maven Lifecycle

Maven operates based on a lifecycle model, which consists of phases and goals. Each phase represents a stage in the build process, and goals are the specific tasks executed during these phases.

The default lifecycle includes phases such as:

- `validate`: Check that the project is correct and all necessary information is available.
- `compile`: Compile the source code of the project.
- `test`: Test the compiled source code using a suitable unit testing framework.
- `package`: Take the compiled code and package it in its distributable format, such as a JAR.
- `install`: Install the package into the local repository, for use as a dependency in other projects locally.
- `deploy`: Copy the final package to the remote repository for sharing with other developers and projects.

#### Maven Configuration

The `pom.xml` file is the central configuration file for Maven projects. It defines the project metadata, dependencies, plugins, and build settings. Here is an example of a simple `pom.xml`:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://m.mvn.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0-SNAPSHOT</version>
    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.12</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

This `pom.xml` defines the project group ID, artifact ID, version, and a dependency on JUnit for testing.

### Gradle Overview

Gradle is another powerful build tool for Java projects. Unlike Maven, which relies heavily on conventions, Gradle provides a more flexible and customizable approach through its domain-specific language (DSL).

#### Gradle Project Structure

A typical Gradle project structure looks similar to Maven:

```plaintext
my-project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   └── resources/
│   └── test/
│       ├── java/
│       └── resources/
├── build.gradle
└── build/
```

- `src/main/java`: Contains the main source code.
- `src/main/resources`: Contains resources like configuration files.
- `src/test/java`: Contains test source code.
- `src/test/resources`: Contains test resources.
- `build.gradle`: The build script that defines the build logic.
- `build/`: Directory where the compiled classes and artifacts are stored.

#### Gradle Build Script

The `build.gradle` file is the central configuration file for Gradle projects. It defines the build logic using Groovy or Kotlin DSL. Here is an example of a simple `build.gradle`:

```groovy
plugins {
    id 'java'
}

repositories {
    mavenCentral()
}

dependencies {
    testImplementation 'junit:junit:4.12'
}
```

This `build.gradle` applies the `java` plugin, specifies the Maven Central repository, and adds a dependency on JUnit for testing.

### Building Artifacts with Maven and Gradle

#### Maven Build Process

To build a Maven project, you typically run the following command:

```bash
mvn clean install
```

This command performs the following steps:

1. **Clean**: Removes the `target` directory to ensure a fresh build.
2. **Compile**: Compiles the source code.
3. **Test**: Runs the tests.
4. **Package**: Packages the compiled code into a JAR file.
5. **Install**: Installs the JAR file into the local Maven repository.

Here is an example of the full Maven build process:

```bash
$ mvn clean install
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------< com.example:my-project >------------------------
[INFO] Building my-project 1.0-SNAPSHOT
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- maven-clean-plugin:3.1.0:clean (default-clean) @ my-project ---
[INFO] Deleting /path/to/my-project/target
[INFO] 
[INFO] --- maven-resources-plugin:3.2.0:resources (default-resources) @ my-project ---
[INFO] Using 'UTF-8' encoding to copy filtered resources.
[INFO] Copying 0 resource
[INFO] 
[INFO] --- maven-compiler-plugin:3.8.1:compile (default-compile) @ my-project ---
[INFO] Changes detected - recompiling the module!
[INFO] Compiling 1 source file to /path/to/my-project/target/classes
[INFO] 
[INFO] --- maven-resources-plugin:3.2.0:testResources (default-testResources) @ my-project ---
[INFO] Using 'UTF-8' encoding to copy filtered resources.
[INFO] Copying 0 resource
[INFO] 
[INFO] --- maven-compiler-plugin:3.8.1:testCompile (default-testCompile) @ my-project ---
[INFO] Changes detected - recompiling the module!
[INFO] Compiling 1 source file to /path/to/my-project/target/test-classes
[INFO] 
[INFO] --- maven-surefire-plugin:2.22.2:test (default-test) @ my-project ---
[INFO] 
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.example.MyProjectTest
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.01 s - in com.example.MyProjectTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] 
[INFO] --- maven-jar-plugin:3.2.0:jar (default-jar) @ my-project ---
[INFO] Building jar: /path/to/my-project/target/my-project-1.0-SNAPSHOT.jar
[INFO] 
[INFO] --- maven-install-plugin:2.5.2:install (default-install) @ my-project ---
[INFO] Installing /path/to/my-project/target/my-project-1.0-SNAPSHOT.jar to /path/to/.m2/repository/com/example/my-project/1.0-SNAPSHOT/my-project-1.0-SNAPSHOT.jar
[INFO] Installing /path/to/my-project/pom.xml to /path/to/.m2/repository/com/example/my-project/1.0-SNAPSHOT/my-project-1.0-SNAPSHOT.pom
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.567 s
[INFO] Finished at: 2023-10-01T12:00:00Z
[INFO] ------------------------------------------------------------------------
```

#### Gradle Build Process

To build a Gradle project, you typically run the following command:

```bash
gradle build
```

This command performs the following steps:

1. **Compile**: Compiles the source code.
2. **Test**: Runs the tests.
3. **Jar**: Packages the compiled code into a JAR file.

Here is an example of the full Gradle build process:

```bash
$ gradle build
Starting a Gradle Daemon (subsequent builds will be faster)

> Task :compileJava
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.

> Task :processResources NO-SOURCE
> Task :classes

> Task :compileTestJava
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.

> Task :processTestResources NO-SOURCE
> Task :testClasses

> Task :test
Gradle Test Executor 1 started executing tests.
Vintage test suite: com.example.MyProjectTest
Vintage test: com.example.MyProjectTest.testMethod PASSED

Gradle Test Executor 1 finished executing tests.

BUILD SUCCESSFUL in 2s
2 actionable tasks: 2 executed
```

### Dependency Management

Both Maven and Gradle provide robust mechanisms for managing dependencies. Dependencies are declared in the `pom.xml` for Maven and in the `build.gradle` for Gradle.

#### Maven Dependencies

Dependencies in Maven are declared within the `<dependencies>` section of the `pom.xml`:

```xml
<dependencies>
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.12</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

#### Gradle Dependencies

Dependencies in Gradle are declared within the `dependencies` block of the `build.gradle`:

```groovy
dependencies {
    testImplementation 'junit:junit:4.12'
}
```

### Packaging Artifacts

Both Maven and Gradle can package the compiled code into various formats, such as JAR, WAR, or EAR files.

#### Maven Packaging

Maven uses the `maven-jar-plugin` to package the compiled code into a JAR file. The default packaging type is `jar`, but it can be changed to `war` or `ear` by setting the `<packaging>` element in the `pom.xml`.

```xml
<packaging>jar</packaging>
```

#### Gradle Packaging

Gradle uses the `application` plugin to create a runnable JAR file. The `jar` task is used to package the compiled code into a JAR file.

```groovy
apply plugin: 'java'
apply plugin: 'application'

mainClassName = 'com.example.MainClass'

jar {
    manifest {
        attributes 'Main-Class': mainClassName
    }
}
```

### Java Version Compatibility

One important consideration when using build tools is the compatibility between the Java version and the build tool version. As mentioned in the transcript, Gradle does not yet support the latest Java version (Java 16 at the time of recording).

#### Java Version Configuration

To configure the Java version for a project, you can specify it in the `pom.xml` for Maven and in the `build.gradle` for Gradle.

##### Maven Java Version Configuration

In Maven, you can specify the Java version using the `maven-compiler-plugin`:

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.8.1</version>
            <configuration>
                <source>1.8</source>
                <target>1.8</target>
            </configuration>
        </plugin>
    </plugins>
</build>
```

##### Gradle Java Version Configuration

In Gradle, you can specify the Java version using the `java` plugin:

```groovy
apply plugin: 'java'

sourceCompatibility = '1.8'
targetCompatibility = '1.8'
```

#### Checking Java Version in IntelliJ IDEA

To check the Java version configured for a project in IntelliJ IDEA, follow these steps:

1. Open the project in IntelliJ IDEA.
2. Go to `File` > `Project Structure`.
3. In the `Project Structure` dialog, select `Modules`.
4. Under the `Sources` tab, you can see the SDK configured for the project.

If you have a Java 16 version installed and configured for the project, you might encounter issues when trying to execute Gradle commands. To resolve this, you can either downgrade the Java version or update Gradle to a version that supports Java 16.

### Real-World Examples and CVEs

While the transcript does not mention any specific CVEs or real-world examples, it is important to understand the potential security implications of using outdated or unsupported versions of Java and build tools.

#### Example: CVE-2021-44228 (Log4Shell)

CVE-2021-44228, also known as Log4Shell, is a critical vulnerability in the Apache Log4j library. This vulnerability allows attackers to execute arbitrary code on the server by injecting malicious log messages. One of the ways this vulnerability could be exploited is through outdated or insecure dependencies managed by build tools.

To mitigate such vulnerabilities, it is essential to keep your dependencies up-to-date and use secure coding practices. Build tools like Maven and Gradle can help manage dependencies and ensure that the project uses the latest and most secure versions of libraries.

### How to Prevent / Defend

#### Detection

To detect outdated or insecure dependencies, you can use tools like:

- **OWASP Dependency-Check**: A tool that identifies project dependencies with known vulnerabilities.
- **Sonatype Nexus Lifecycle**: A service that provides detailed security and license compliance information for open-source components.

#### Prevention

To prevent issues related to Java version compatibility and dependency management, follow these best practices:

1. **Keep Dependencies Up-to-date**: Regularly update your dependencies to the latest versions.
2. **Use Secure Coding Practices**: Follow secure coding guidelines to minimize the risk of vulnerabilities.
3. **Configure Build Tools Correctly**: Ensure that the Java version and build tool configurations are correct and compatible.
4. **Automate Security Checks**: Integrate security checks into your build process using tools like OWASP Dependency-Check.

#### Secure Code Fix

Here is an example of a vulnerable and secure version of a `pom.xml` file:

**Vulnerable Version:**

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.logging.log4j</groupId>
        <artifactId>log4j-core</artifactId>
        <version>2.14.1</version>
    </dependency>
</dependencies>
```

**Secure Version:**

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.logging.log4j</groupId>
        <artifactId>log4j-core</artifactId>
        <version>2.17.1</version>
    </dependency>
</dependencies>
```

In the secure version, the `log4j-core` dependency is updated to a version that addresses the Log4Shell vulnerability.

### Conclusion

Building artifacts with Maven and Gradle is a fundamental aspect of modern Java development. Understanding the build process, dependency management, and Java version compatibility is crucial for creating robust and secure applications. By following best practices and using the right tools, you can ensure that your projects are built efficiently and securely.

### Practice Labs

For hands-on practice with Maven and Gradle, consider the following labs:

- **PortSwigger Web Security Academy**: Offers labs on web application security, including dependency management and secure coding practices.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

These labs provide practical experience in building and securing Java applications using Maven and Gradle.

---
<!-- nav -->
[[01-Introduction to Build Tools in Java|Introduction to Build Tools in Java]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/09-Building Artifacts with Maven and Gradle/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/09-Building Artifacts with Maven and Gradle/03-Practice Questions & Answers|Practice Questions & Answers]]
