---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to IntelliJ and Development Environments

IntelliJ IDEA is a powerful Integrated Development Environment (IDE) developed by JetBrains. It supports various programming languages, including Java, Kotlin, Scala, Groovy, and more. IntelliJ IDEA provides a rich set of features such as code completion, refactoring, debugging, and integration with version control systems. This makes it an excellent choice for developers working on complex projects.

### IntelliJ Preferences and Project Structure

When setting up your development environment in IntelliJ IDEA, it's crucial to understand the difference between global preferences and project-specific settings.

#### Global Preferences

Global preferences apply to all projects and can be accessed via `Preferences` (on macOS) or `Settings` (on Windows/Linux). These settings include configurations for the IDE itself, such as appearance, keymaps, plugins, and other general settings.

#### Project-Specific Settings

Project-specific settings are configured within the project itself and can be found under `File > Project Structure`. These settings include configurations related to the project's structure, modules, libraries, and SDKs.

### Software Development Kit (SDK)

The Software Development Kit (SDK) is a collection of tools used to develop applications for a specific platform. In the context of Java development, the SDK typically includes the Java Runtime Environment (JRE) and the Java Development Kit (JDK).

#### Java Development Kit (JDK)

The Java Development Kit (JDK) is essential for developing Java applications. It includes the JRE, which is required to run Java programs, along with additional tools like the Java compiler (`javac`), the Java debugger (`jdb`), and other utilities.

### Configuring the JDK in IntelliJ IDEA

To configure the JDK in IntelliJ IDEA, follow these steps:

1. **Open IntelliJ IDEA** and create or open an existing project.
2. **Navigate to `File > Project Structure`**.
3. Under the `Project` tab, locate the `Project SDK` section.
4. Click on the dropdown menu and select `New...`.
5. Choose `JDK` and navigate to the location where the JDK is installed.

### Installing Java Using Homebrew

Homebrew is a popular package manager for macOS that simplifies the installation of software packages. To install Java using Homebrew, follow these steps:

1. **Open Terminal**.
2. **Install Homebrew** if you haven't already by running:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
3. **Install OpenJDK** by running:
    ```bash
    brew install --cask adoptopenjdk15
    ```

### Specifying a Specific Version of Java

In some cases, you may need to use a specific version of Java, especially if you are working on a project that requires a particular version. For example, the project might require Java 15 or earlier due to compatibility issues with newer versions.

#### Why Use Java 15?

Java 15 was released in September 2020 and includes several new features and improvements. However, some projects, particularly those using older build tools like Gradle, may not be compatible with newer versions of Java. Therefore, it's important to ensure that the correct version is installed and configured.

### Installing Java 15 Using Homebrew

To install Java 15 using Homebrew, run the following command:

```bash
brew install --cask adoptopenjdk15
```

This command installs AdoptOpenJDK 15, which is a community-driven distribution of OpenJDK.

### Verifying the Installation

After installing Java 15, you can verify the installation by checking the version of Java installed on your system. Run the following command in Terminal:

```bash
java -version
```

If the installation was successful, you should see output similar to the following:

```plaintext
openjdk version "15.0.2" 2021-01-19
OpenJDK Runtime Environment (AdoptOpenJDK)(build 15.0.2+7)
OpenJDK 64-Bit Server VM (AdoptOpenJDK)(build 15.0.2+7, mixed mode, sharing)
```

### Configuring the JDK in IntelliJ IDEA

Once Java 15 is installed, you can configure it in IntelliJ IDEA:

1. **Open IntelliJ IDEA** and create or open an existing project.
2. **Navigate to `File > Project Structure`**.
3. Under the `Project` tab, locate the `Project SDK` section.
4. Click on the dropdown menu and select `New...`.
5. Choose `JDK` and navigate to the location where Java 15 is installed.

### Common Pitfalls and How to Avoid Them

#### Incorrect JDK Configuration

One common pitfall is configuring the wrong version of the JDK in IntelliJ IDEA. This can lead to compatibility issues and runtime errors. To avoid this, always verify the version of Java installed on your system and ensure that the correct version is selected in IntelliJ IDEA.

#### Missing JDK Installation

Another common issue is forgetting to install the JDK altogether. This can result in errors when trying to compile or run Java programs. Always ensure that the JDK is installed before starting a new project.

### Real-World Examples and Recent CVEs

#### CVE-2021-2155

CVE-2021-2155 is a vulnerability in the Java Cryptography Extension (JCE) that allows an attacker to bypass certain security restrictions. This vulnerability affects Java versions prior to 15. By ensuring that you are using a version of Java that is not affected by this vulnerability, you can help protect your applications from potential attacks.

### How to Prevent / Defend

#### Detection

To detect whether your system is vulnerable to CVE-2021-2155, you can check the version of Java installed on your system. If the version is prior to 15, you should consider upgrading to a newer version.

#### Prevention

To prevent vulnerabilities like CVE-2021-2155, always ensure that you are using the latest version of Java. Additionally, keep your system and all installed software up to date with the latest security patches.

#### Secure Coding Practices

When writing Java code, follow secure coding practices to minimize the risk of introducing vulnerabilities. This includes validating user input, avoiding hardcoded passwords, and using secure libraries and frameworks.

### Complete Example

Here is a complete example of installing Java 15 using Homebrew and configuring it in IntelliJ IDEA:

#### Install Java 15 Using Homebrew

```bash
brew install --cask adoptopenjdk15
```

#### Verify the Installation

```bash
java -version
```

#### Configure the JDK in IntelliJ IDEA

1. **Open IntelliJ IDEA** and create or open an existing project.
2. **Navigate to `File > Project Structure`**.
3. Under the `Project` tab, locate the `Project SDK` section.
4. Click on the dropdown menu and select `New...`.
5. Choose `JDK` and navigate to the location where Java 15 is installed.

### Conclusion

Setting up your development environment in IntelliJ IDEA involves configuring the correct SDK and ensuring that the necessary tools are installed. By following the steps outlined in this chapter, you can set up your environment correctly and avoid common pitfalls. Additionally, by staying up to date with the latest versions of Java and following secure coding practices, you can help protect your applications from potential vulnerabilities.

### Practice Labs

For hands-on practice with setting up a development environment in IntelliJ IDEA, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in setting up and securing a development environment, which is essential for any developer.

---
<!-- nav -->
[[05-Introduction to IntelliJ IDEA for Development Environment Setup|Introduction to IntelliJ IDEA for Development Environment Setup]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/15-MacOS Tool Setup for Development Environment/00-Overview|Overview]] | [[07-Introduction to MacOS Tool Setup for Development Environment|Introduction to MacOS Tool Setup for Development Environment]]
