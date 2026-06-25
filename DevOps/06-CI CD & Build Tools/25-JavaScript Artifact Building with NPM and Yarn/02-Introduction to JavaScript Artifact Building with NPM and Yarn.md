---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to JavaScript Artifact Building with NPM and Yarn

When working with Java applications, developers often rely on build tools like Maven and Gradle to manage dependencies, compile code, and create artifacts. However, JavaScript applications operate differently. Unlike Java, which has specific artifact types such as JAR or WAR files, JavaScript artifacts can be packaged into various formats, including ZIP or TAR files. This chapter will delve into the process of building JavaScript artifacts using NPM and Yarn, two popular package managers for JavaScript.

### What Are NPM and Yarn?

NPM (Node Package Manager) and Yarn are package managers designed to handle dependencies in JavaScript projects. While they serve similar purposes, they have distinct features and workflows.

#### NPM

NPM is the default package manager for Node.js. It is widely used and has a vast ecosystem of packages available through the npm registry. NPM allows developers to manage dependencies, install packages, and run scripts defined in the `package.json` file.

#### Yarn

Yarn is another package manager that was developed to address some of the shortcomings of NPM, particularly around speed and reliability. Yarn uses a lockfile (`yarn.lock`) to ensure deterministic installations, meaning that the exact same dependencies will be installed every time.

### Dependency Management with `package.json`

Both NPM and Yarn use the `package.json` file to manage dependencies. This file contains metadata about the project and lists the dependencies required to run the application.

```json
{
  "name": "my-javascript-project",
  "version": "1.0.0",
  "description": "A sample JavaScript project",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "lodash": "^4.17.21"
  }
}
```

In this example, the `package.json` file includes:

- **name**: The name of the project.
- **version**: The version number of the project.
- **description**: A brief description of the project.
- **main**: The entry point of the application.
- **scripts**: Custom scripts that can be run using `npm run` or `yarn run`.
- **dependencies**: A list of dependencies and their versions.

### Installing Dependencies with NPM and Yarn

To install the dependencies listed in the `package.json` file, you can use either NPM or Yarn.

#### Using NPM

```bash
npm install
```

This command reads the `package.json` file and installs all the dependencies listed under the `dependencies` field.

#### Using Yarn

```bash
yarn install
```

Yarn also reads the `package.json` file but uses the `yarn.lock` file to ensure that the exact same dependencies are installed every time.

### Building JavaScript Artifacts

Unlike Java build tools, NPM and Yarn do not directly build artifacts. Instead, they manage dependencies and provide a way to run custom scripts. To build a JavaScript artifact, you typically need to use additional tools such as Webpack, Babel, or Rollup.

#### Example: Using Webpack

Webpack is a popular module bundler that can be used to build JavaScript artifacts. Here’s an example of how to set up Webpack in a project:

1. **Install Webpack and Webpack CLI**

   ```bash
   npm install --save-dev webpack webpack-cli
   ```

2. **Create a Webpack Configuration File**

   Create a `webpack.config.js` file in the root of your project:

   ```javascript
   const path = require('path');

   module.exports = {
     entry: './src/index.js',
     output: {
       filename: 'bundle.js',
       path: path.resolve(__dirname, 'dist')
     },
     mode: 'production'
   };
   ```

3. **Add a Build Script to `package.json`**

   Modify the `package.json` file to include a build script:

   ```json
   {
     "scripts": {
       "build": "webpack"
     }
   }
   ```

4. **Run the Build Command**

   ```bash
   npm run build
   ```

   This command will run Webpack and generate a `bundle.js` file in the `dist` directory.

### Packaging Artifacts

Once the JavaScript application is built, you can package it into a ZIP or TAR file. This is useful for deployment or distribution.

#### Creating a ZIP File

```bash
zip -r my-javascript-project.zip dist/
```

#### Creating a TAR File

```bash
tar -czvf my-javascript-project.tar.gz dist/
```

### Real-World Examples and Security Considerations

JavaScript applications are often targeted by various security vulnerabilities. One notable example is the `CVE-2021-21319`, which affected the `lodash` library. This vulnerability allowed attackers to execute arbitrary code by manipulating the input to certain functions.

#### Secure Coding Practices

To prevent such vulnerabilities, it is crucial to follow secure coding practices:

1. **Keep Dependencies Updated**
   Regularly update dependencies to the latest versions to mitigate known vulnerabilities.

2. **Use Dependency Auditing Tools**
   Tools like `npm audit` and `yarn audit` can help identify and fix vulnerabilities in your dependencies.

   ```bash
   npm audit
   ```

   ```bash
   yarn audit
   ```

3. **Validate Input**
   Always validate and sanitize user input to prevent injection attacks.

### How to Prevent / Defend

#### Detection

Regularly run dependency audits to detect vulnerabilities:

```bash
npm audit
```

```bash
yarn audit
```

#### Prevention

1. **Update Dependencies**
   Keep all dependencies up-to-date by regularly running:

   ```bash
   npm update
   ```

   ```bash
   yarn upgrade
   ```

2. **Secure Coding Practices**
   Follow secure coding practices to prevent common vulnerabilities.

3. **Use Secure Libraries**
   Choose libraries that have a good track record of security and regular updates.

### Conclusion

Building JavaScript artifacts involves managing dependencies with NPM or Yarn and using additional tools like Webpack to bundle the application. By following secure coding practices and regularly updating dependencies, developers can ensure the security and reliability of their JavaScript applications.

### Practice Labs

For hands-on practice with JavaScript artifact building and security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including JavaScript security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application with intentional vulnerabilities for security training.

These labs provide practical experience in building and securing JavaScript applications.

---
<!-- nav -->
[[01-Introduction to Front-End and Back-End Development with JavaScript|Introduction to Front-End and Back-End Development with JavaScript]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/25-JavaScript Artifact Building with NPM and Yarn/00-Overview|Overview]] | [[03-Introduction to Webpack and Artifact Building|Introduction to Webpack and Artifact Building]]
