---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## MacOS Tool Setup for Development Environment

### Introduction to MacOS Development Environment

In the context of setting up a development environment on macOS, we often encounter situations where specific versions of tools or libraries are required. One such scenario involves managing different versions of the Java Development Kit (JDK). In this section, we will delve into the process of setting up a specific version of OpenJDK on macOS, specifically version 15, and integrating it into an Integrated Development Environment (IDE) like IntelliJ IDEA.

### Understanding Symbolic Links

A symbolic link, also known as a symlink, is a special type of file that points to another file or directory. Symbolic links are commonly used to create shortcuts or aliases to files or directories in Unix-based systems like macOS. They are particularly useful when you need to access a file or directory from multiple locations without duplicating the actual data.

#### Why Use Symbolic Links?

Symbolic links are beneficial because they allow you to:

1. **Access Files from Multiple Locations**: You can create a shortcut to a file or directory in another location, making it easier to access.
2. **Manage Different Versions of Software**: You can use symlinks to switch between different versions of a software package without having to reinstall it.
3. **Save Disk Space**: Instead of duplicating large files or directories, you can use symlinks to reference them from multiple locations.

#### How Symbolic Links Work

When you create a symbolic link, you are essentially creating a pointer to another file or directory. The operating system uses this pointer to resolve the actual file or directory when you interact with the symlink. Here’s a simple example of creating a symbolic link:

```bash
ln -s /path/to/target /path/to/symlink
```

In this command:
- `ln` is the command used to create links.
- `-s` specifies that you want to create a symbolic link.
- `/path/to/target` is the path to the actual file or directory.
- `/path/to/symlink` is the path where you want to create the symbolic link.

### Installing OpenJDK on macOS

To install OpenJDK on macOS, you can use a package manager like Homebrew. Homebrew is a popular package manager for macOS that simplifies the installation of various software packages.

#### Installing Homebrew

If you haven’t already installed Homebrew, you can do so by running the following command in your terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Once Homebrew is installed, you can use it to install OpenJDK. Run the following command to install OpenJDK:

```bash
brew install openjdk@15
```

This command installs OpenJDK version 15 on your system.

### Creating a Symbolic Link for OpenJDK

After installing OpenJDK, you may need to create a symbolic link to ensure that your IDE can find the correct version of the JDK. Let’s assume that OpenJDK version 15 is installed in `/usr/local/opt/openjdk@15`.

#### Creating the Symlink

To create a symbolic link, you can use the `ln` command as follows:

```bash
sudo ln -s /usr/local/opt/openjdk@15/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/
```

This command creates a symbolic link in the `/Library/Java/JavaVirtualMachines/` directory, pointing to the OpenJDK version 15 installation.

### Configuring IntelliJ IDEA

Now that OpenJDK version 15 is installed and a symbolic link is created, you can configure IntelliJ IDEA to use this version of the JDK.

#### Setting Up the JDK in IntelliJ IDEA

1. **Open IntelliJ IDEA**.
2. **Go to Preferences**: On macOS, you can access preferences by selecting `IntelliJ IDEA` > `Preferences`.
3. **Navigate to Project Structure**: In the preferences window, navigate to `Project: <Your Project>` > `Project Structure`.
4. **Add JDK**: Click on the `SDKs` tab and then click on the `+` button to add a new SDK. Select `JDK` and browse to the location where the symbolic link was created (e.g., `/Library/Java/JavaVirtualMachines/openjdk.jdk`).

#### Verifying the Configuration

After configuring IntelliJ IDEA to use the correct JDK, you can verify the setup by checking the project settings:

1. **Go to Project Structure**: Navigate to `Project: <Your Project>` > `Project Structure`.
2. **Check SDK Settings**: Ensure that the correct JDK version (15) is selected for your project.

### Running the Application

With the JDK correctly configured, you can now run your application within IntelliJ IDEA.

#### Running the Application

1. **Open the Main Class**: Locate the main class of your application in the project explorer.
2. **Run the Application**: Right-click on the main class and select `Run '<Main Class>'`. IntelliJ IDEA will compile and run the application using the specified JDK version.

#### Example Output

When the application runs successfully, you should see output similar to the following in the console:

```plaintext
Started application.
```

This indicates that the project is successfully set up with the correct JDK version, and the application is running as expected.

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Incorrect JDK Version

**Problem**: Using the wrong version of the JDK can lead to compatibility issues and runtime errors.

**Prevention**:
- Always verify the JDK version being used by your IDE.
- Use symbolic links to manage different versions of the JDK.

#### Pitfall 2: Missing Dependencies

**Problem**: Missing dependencies can cause compilation errors and runtime exceptions.

**Prevention**:
- Ensure that all required dependencies are included in your project.
- Use build tools like Maven or Gradle to manage dependencies.

#### Pitfall 3: Incorrect Configuration

**Problem**: Incorrect configuration of the IDE can result in the wrong JDK being used.

**Prevention**:
- Double-check the project settings to ensure the correct JDK is selected.
- Verify the symbolic link creation and usage.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-2155

CVE-2021-2155 is a vulnerability in the Java Runtime Environment (JRE) that affects older versions of the JDK. This vulnerability could allow an attacker to execute arbitrary code on a victim's machine.

**Impact**: Using outdated versions of the JDK can expose your application to security risks.

**Mitigation**:
- Keep your JDK up to date.
- Use symbolic links to manage different versions of the JDK.

### Conclusion

Setting up a development environment on macOS involves managing different versions of tools and libraries, such as the JDK. By using symbolic links and properly configuring your IDE, you can ensure that your development environment is set up correctly and securely. This chapter has covered the steps to install OpenJDK, create symbolic links, and configure IntelliJ IDEA to use the correct JDK version. Additionally, we have discussed common pitfalls and provided real-world examples to illustrate the importance of proper setup and management.

### Practice Labs

For hands-on practice with setting up a development environment on macOS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in setting up and securing development environments, which is crucial for mastering DevOps practices.

---
<!-- nav -->
[[07-Introduction to MacOS Tool Setup for Development Environment|Introduction to MacOS Tool Setup for Development Environment]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/15-MacOS Tool Setup for Development Environment/00-Overview|Overview]] | [[09-Setting Up a Development Environment on macOS for Node.js Projects|Setting Up a Development Environment on macOS for Node.js Projects]]
