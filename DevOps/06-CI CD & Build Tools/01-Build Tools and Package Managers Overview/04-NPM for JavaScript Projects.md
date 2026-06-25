---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## NPM for JavaScript Projects

### What is NPM?

NPM (Node Package Manager) is the default package manager for Node.js. It allows developers to easily manage and install JavaScript packages. NPM uses a `package.json` file to declare the project’s dependencies and scripts.

#### Key Features of NPM

- **Package management**: NPM manages the installation, upgrade, and removal of JavaScript packages.
- **Scripts**: NPM allows developers to define custom scripts in the `package.json` file.
- **Registry**: NPM uses a public registry to host and distribute packages.
- **Dependency resolution**: NPM resolves transitive dependencies and ensures that the correct versions are used.

### Setting Up an NPM Project

To set up an NPM project, you need to create a `package.json` file in the root directory of your project. This file contains the project metadata and configurations.

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

#### Explanation of the `package.json` File

- **name**: The name of the project.
- **version**: The version of the project.
- **main**: The entry point of the project.
- **scripts**: Custom scripts defined for the project.
- **dependencies**: Lists the dependencies required by the project.

### Installing Dependencies with NPM

To install dependencies for an NPM project, you can run the following command:

```bash
npm install
```

This command reads the `package.json` file and installs the specified dependencies in the `node_modules` directory.

### Running Scripts with NPM

NPM allows developers to define custom scripts in the `package.json` file. These scripts can be executed using the `npm run` command.

#### Example of Running a Script

```bash
npm run start
```

This command executes the `start` script defined in the `package.json` file.

### How to Prevent / Defend

#### Detection

To detect outdated or vulnerable dependencies, you can use tools like npm audit or Snyk. These tools scan your project’s dependencies and provide reports on known vulnerabilities.

#### Prevention

To prevent security issues related to dependencies, follow these best practices:

- **Regularly update dependencies**: Keep your dependencies up-to-date to avoid known vulnerabilities.
- **Use dependency checkers**: Integrate dependency checkers into your CI/CD pipeline to automatically detect and alert on insecure dependencies.
- **Secure coding practices**: Follow secure coding guidelines to minimize the risk of introducing vulnerabilities.

### Secure Code Example

#### Vulnerable Code

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

#### Secure Code

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "audit": "npm audit"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

### Real-World Examples

#### CVE-2021-21315

CVE-2021-21315 is a vulnerability in the `lodash` package, which is widely used in JavaScript applications. This vulnerability allows attackers to execute arbitrary code by manipulating the input to certain functions.

#### Prevention

To prevent such vulnerabilities, you should regularly update your dependencies and use tools like npm audit to detect and fix known vulnerabilities.

### Practice Labs

For hands-on practice with build tools and package managers, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs covering web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

By completing these labs, you can gain practical experience with build tools and package managers in a controlled environment.

### Conclusion

In this module, we have explored the role of build tools and package managers in the software development process. We have compared and contrasted Gradle and Maven for Java projects, and NPM for JavaScript projects. By understanding how to build and package applications, as well as how to manage dependencies effectively, you can improve the productivity and security of your development workflow.

---
<!-- nav -->
[[03-Maven for Java Projects|Maven for Java Projects]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/01-Build Tools and Package Managers Overview/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/01-Build Tools and Package Managers Overview/05-Practice Questions & Answers|Practice Questions & Answers]]
