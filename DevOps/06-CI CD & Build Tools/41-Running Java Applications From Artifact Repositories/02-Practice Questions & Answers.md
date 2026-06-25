---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the command to execute a Java application packaged as a JAR file?**

The command to execute a Java application packaged as a JAR file is `java -jar <name-of-the-jar-file>.jar`. This command tells the Java runtime environment to launch the application contained within the specified JAR file.

**Q2. How would you start a Java application from an artifact repository on a fresh server with Java installed?**

To start a Java application from an artifact repository on a fresh server with Java installed, follow these steps:

1. Download the JAR file from the artifact repository.
2. Ensure Java is installed on the server.
3. Use the command `java -jar <path-to-downloaded-jar-file>.jar` to start the application.

For example, if the JAR file is named `app.jar`, the command would be `java -jar app.jar`.

**Q3. Explain how to execute a Maven-built Java application from its target directory.**

A Maven-built Java application typically has its compiled classes and resources packaged into a JAR file located in the `target` directory of the project. To execute such an application, you would use the following command:

```bash
java -jar target/<artifact-name>-<version>.jar
```

For instance, if the artifact name is `my-app` and the version is `1.0.0`, the command would look like this:

```bash
java -jar target/my-app-1.0.0.jar
```

This command will start the application using the JAR file found in the `target` directory.

**Q4. Why is it important to ensure Java is installed before attempting to run a JAR file on a new server?**

It is crucial to ensure Java is installed before running a JAR file on a new server because the JAR file contains bytecode that needs to be executed by the Java Virtual Machine (JVM). If Java is not installed, the server will lack the necessary runtime environment to interpret and execute the bytecode, resulting in errors or failure to start the application.

**Q5. How does the process of running a Java application from an artifact repository compare to running it directly from source code?**

Running a Java application from an artifact repository involves downloading a pre-packaged JAR file and executing it with the `java -jar` command. This process is straightforward and requires minimal setup once the artifact is downloaded.

In contrast, running an application directly from source code involves compiling the source files into bytecode and then executing the compiled classes. This process might require additional steps such as setting up build tools (like Maven or Gradle), managing dependencies, and configuring the classpath.

Using an artifact repository simplifies deployment and ensures consistency across different environments since the exact same artifact is used everywhere.

---
<!-- nav -->
[[01-Introduction to Artifact Repositories and Java Application Deployment|Introduction to Artifact Repositories and Java Application Deployment]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/41-Running Java Applications From Artifact Repositories/00-Overview|Overview]]
