---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up a Development Environment on macOS for Node.js Projects

### Introduction

In this section, we will cover the setup of a development environment on macOS specifically tailored for Node.js projects using IntelliJ IDEA. This setup will enable you to work effectively with various build tools that are essential for a DevOps engineer. We'll delve into the necessary steps, tools, and configurations to ensure a robust and secure development environment.

### Prerequisites

Before setting up your development environment, ensure you have the following installed:

1. **macOS**: The operating system on which you will be working.
2. **Node.js**: A JavaScript runtime built on Chrome's V8 JavaScript engine.
3. **npm (Node Package Manager)**: A package manager for Node.js.
4. **IntelliJ IDEA**: An integrated development environment (IDE) for Java and other languages.

#### Installing Node.js and npm

To install Node.js and npm, follow these steps:

1. **Download Node.js**:
   - Visit the official Node.js website: [https://nodejs.org](https://nodejs.org)
   - Download the latest LTS (Long-Term Support) version for macOS.

2. **Install Node.js**:
   - Open the downloaded `.pkg` file and follow the installation instructions.

3. **Verify Installation**:
   - Open Terminal and run the following commands to check the installed versions:
     ```sh
     node -v
     npm -v
     ```

### Setting Up IntelliJ IDEA

#### Installing IntelliJ IDEA

1. **Download IntelliJ IDEA**:
   - Visit the JetBrains website: [https://www.jetbrains.com/idea/download/](https://www.jetbrains.com/idea/download/)
   - Download the Community Edition for free.

2. **Install IntelliJ IDEA**:
   - Open the downloaded `.dmg` file and drag IntelliJ IDEA to your Applications folder.

3. **Launch IntelliJ IDEA**:
   - Double-click the IntelliJ IDEA icon in your Applications folder to launch it.

#### Creating a New Node.js Project

1. **Open IntelliJ IDEA**:
   - Launch IntelliJ IDEA and select `Create New Project`.

2. **Select Node.js**:
   - In the `New Project` dialog, select `Node.js` from the list of available templates.

3. **Configure Project Settings**:
   - Specify the project name and location.
   - Ensure that the `Use Node.js` checkbox is selected.
   - Click `Next` and then `Finish`.

### Configuring Build Tools

As a DevOps engineer, you will frequently interact with various build tools. Some of the most commonly used build tools include:

- **npm scripts**
- **Yarn**
- **Webpack**
- **Gulp**

#### npm Scripts

npm scripts are defined in the `package.json` file and can be used to automate tasks such as building, testing, and deploying your application.

##### Example `package.json` with npm Scripts

```json
{
  "name": "my-node-project",
  "version": "1.0.0",
  "description": "A sample Node.js project",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "build": "webpack",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.17.1"
  },
  "devDependencies": {
    "webpack": "^5.64.0",
    "jest": "^27.4.7"
  }
}
```

##### Running npm Scripts

To run an npm script, use the following command in Terminal:

```sh
npm run <script-name>
```

For example, to start the application:

```sh
npm run start
```

#### Yarn

Yarn is an alternative package manager for Node.js that offers faster and more reliable dependency management.

##### Installing Yarn

To install Yarn, run the following command:

```sh
npm install --global yarn
```

##### Using Yarn

To initialize a new Yarn project, run:

```sh
yarn init
```

This will create a `package.json` file similar to the one created by npm.

##### Adding Dependencies with Yarn

To add dependencies, use:

```sh
yarn add <package-name>
```

For example, to add Express:

```sh
yarn add express
```

#### Webpack

Webpack is a module bundler that allows you to manage and bundle your application's modules.

##### Installing Webpack

To install Webpack, run:

```sh
npm install --save-dev webpack webpack-cli
```

##### Configuring Webpack

Create a `webpack.config.js` file in the root of your project:

```javascript
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      }
    ]
  }
};
```

##### Running Webpack

To run Webpack, add a script to your `package.json`:

```json
"scripts": {
  "build": "webpack"
}
```

Then run:

```sh
npm run build
```

#### Gulp

Gulp is a task runner that automates repetitive tasks such as minifying files, running unit tests, and optimizing images.

##### Installing Gulp

To install Gulp, run:

```sh
npm install --save-dev gulp
```

##### Configuring Gulp

Create a `gulpfile.js` in the root of your project:

```javascript
const { src, dest } = require('gulp');
const uglify = require('gulp-uglify');

function minifyJS() {
  return src('src/**/*.js')
    .pipe(uglify())
    .pipe(dest('dist'));
}

exports.default = minifyJS;
```

##### Running Gulp

To run Gulp, add a script to your `package.json`:

```json
"scripts": {
  "minify": "gulp"
}
```

Then run:

```sh
npm run minify
```

### Security Considerations

When setting up your development environment, it is crucial to consider security best practices to avoid vulnerabilities and potential breaches.

#### Common Vulnerabilities

Some common vulnerabilities in Node.js applications include:

- **CVE-2021-21315**: A vulnerability in the `http-parser` library that could lead to a denial-of-service attack.
- **CVE-2021-21316**: A vulnerability in the `http-parser` library that could allow remote code execution.

#### How to Prevent / Defend

1. **Keep Dependencies Updated**:
   - Regularly update your dependencies to the latest versions.
   - Use tools like `npm audit` or `yarn audit` to identify and fix vulnerabilities.

2. **Secure Coding Practices**:
   - Avoid using `eval()` and `new Function()` as they can execute arbitrary code.
   - Validate and sanitize user input to prevent injection attacks.

3. **Configuration Hardening**:
   - Disable unnecessary features and services.
   - Use environment variables to store sensitive information securely.

4. **Monitoring and Logging**:
   - Implement logging and monitoring to detect and respond to security incidents promptly.

#### Secure Code Example

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**:

```javascript
const http = require('http');
const fs = require('fs');

http.createServer((req, res) => {
  const filePath = req.url.slice(1);
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File not found\n');
    } else {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    }
  });
}).listen(8080);
```

**Secure Code**:

```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

http.createServer((req, res) => {
  const filePath = path.join(__dirname, req.url.slice(1));
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File not found\n');
    } else {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    }
  });
}).listen(8080);
```

### Hands-On Labs

To practice and reinforce your learning, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: A deliberately insecure Java web application maintained by OWASP for security training.

These labs provide practical experience in setting up and securing development environments, as well as working with various build tools.

### Conclusion

Setting up a development environment on macOS for Node.js projects using IntelliJ IDEA is a critical step for any DevOps engineer. By following the steps outlined in this chapter, you can ensure a robust and secure development environment. Additionally, understanding and implementing security best practices will help you avoid common vulnerabilities and protect your applications from potential breaches.

---
<!-- nav -->
[[08-MacOS Tool Setup for Development Environment|MacOS Tool Setup for Development Environment]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/15-MacOS Tool Setup for Development Environment/00-Overview|Overview]] | [[10-Setting Up a Java Gradle Project on macOS|Setting Up a Java Gradle Project on macOS]]
