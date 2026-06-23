---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Front-End and Back-End Development with JavaScript

In modern web development, JavaScript plays a pivotal role both on the client-side (front-end) and server-side (back-end). This chapter delves into the intricacies of building and managing JavaScript artifacts using tools like npm and yarn, focusing on a project structure that utilizes React for the front-end and Node.js for the back-end.

### Project Structure Overview

A typical project structure might look like this:

```
my-project/
├── frontend/
│   ├── package.json
│   └── src/
│       └── App.js
└── backend/
    ├── package.json
    └── server.js
```

Each part of the project (front-end and back-end) is contained within its own directory and has its own `package.json` file. This separation allows for independent management of dependencies and build processes.

#### Dependencies Management

Dependencies are managed via `package.json`. Here’s an example of a `package.json` for the front-end:

```json
{
  "name": "frontend",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "dependencies": {
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "react-scripts": "4.0.3"
  }
}
```

And for the back-end:

```json
{
  "name": "backend",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.17.1"
  }
}
```

### Transpilation and Compression in Front-End Development

One of the key challenges in front-end development is ensuring that the latest JavaScript features are compatible with all browsers. This is achieved through transpilation and compression.

#### Transpilation

Transpilation converts modern JavaScript code into a version that older browsers can understand. Tools like Babel are commonly used for this purpose.

##### Example with Babel

Here’s a simple example of using Babel to transpile ES6+ code:

1. **Install Babel**:
   ```bash
   npm install --save-dev @babel/core @babel/cli @babel/preset-env
   ```

2. **Create `.babelrc`**:
   ```json
   {
     "presets": ["@babel/preset-env"]
   }
   ```

3. **Transpile Code**:
   ```bash
   npx babel src --out-dir dist
   ```

This will convert the code in `src` to a more compatible format and place it in the `dist` directory.

#### Compression

Compression reduces the size of the final output, making it faster to download and load in the browser. Tools like UglifyJS or Terser are often used for this purpose.

##### Example with Terser

1. **Install Terser**:
   ```bash
   npm install --save-dev terser
   ```

2. **Compress Code**:
   ```bash
   npx terser src/main.js -o dist/main.min.js
   ```

This will minify the `main.js` file and save it as `main.min.js`.

### Build Tools for Front-End Development

Several tools are available for automating the build process, including transpilation and compression. Some of the most popular ones are Webpack, Gulp, and Grunt.

#### Webpack

Webpack is a powerful module bundler that can handle various types of assets and perform complex transformations.

##### Example Configuration

1. **Install Webpack**:
   ```bash
   npm install --save-dev webpack webpack-cli
   ```

2. **Create `webpack.config.js`**:
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

3. **Build Project**:
   ```bash
   npx webpack
   ```

This configuration sets up Webpack to take the entry point at `src/index.js`, transpile it using Babel, and output the result to `dist/bundle.js`.

### Real-World Examples and Security Considerations

#### Recent CVEs and Breaches

One notable example is the `CVE-2021-21366`, which affected Webpack. This vulnerability allowed attackers to execute arbitrary code during the build process. To mitigate such risks, it is crucial to keep all tools and dependencies up-to-date and to follow secure coding practices.

#### Secure Coding Practices

1. **Keep Dependencies Updated**: Regularly update dependencies to patch known vulnerabilities.
2. **Use Secure Configurations**: Ensure that configurations like Webpack’s `resolve.alias` are set securely to prevent malicious code injection.
3. **Validate Inputs**: Always validate and sanitize inputs to prevent injection attacks.

### How to Prevent / Defend

#### Detection

Regularly scan your project for vulnerabilities using tools like `npm audit` or `yarn audit`.

```bash
npm audit
```

#### Prevention

1. **Update Dependencies**:
   ```bash
   npm update
   ```

2. **Secure Configurations**:
   ```javascript
   module.exports = {
     resolve: {
       alias: {
         '@': path.resolve(__dirname, 'src')
       }
     }
   };
   ```

3. **Sanitize Inputs**:
   ```javascript
   const express = require('express');
   const app = express();

   app.use(express.urlencoded({ extended: true }));
   app.use((req, res, next) => {
     req.body = sanitize(req.body);
     next();
   });

   function sanitize(input) {
     // Sanitize input logic here
   }

   app.post('/submit', (req, res) => {
     console.log(req.body);
     res.send('Received');
   });
   ```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on web security, including front-end and back-end vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular tool for learning about web application security.

These labs provide real-world scenarios to practice and reinforce the concepts covered in this chapter.

### Conclusion

Building and managing JavaScript artifacts requires a deep understanding of transpilation, compression, and build tools. By following best practices and using secure configurations, developers can ensure their applications are robust and secure.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/25-JavaScript Artifact Building with NPM and Yarn/00-Overview|Overview]] | [[02-Introduction to JavaScript Artifact Building with NPM and Yarn|Introduction to JavaScript Artifact Building with NPM and Yarn]]
