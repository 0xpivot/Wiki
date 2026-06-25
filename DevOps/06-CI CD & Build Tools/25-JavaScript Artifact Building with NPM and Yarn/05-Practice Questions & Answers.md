---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the role of NPM and Yarn in JavaScript development, and how do they differ from build tools like Maven and Gradle?**

NPM (Node Package Manager) and Yarn are package managers used in JavaScript development. Their primary role is to manage dependencies specified in the `package.json` file, similar to how Maven and Gradle manage dependencies in Java projects. However, NPM and Yarn are not build tools; they do not compile, transpile, or bundle the code. Build tools like Webpack, Babel, or Rollup are used for these tasks in JavaScript projects.

**Q2. How do you create a JavaScript artifact (zip or tar file) using NPM or Yarn, and what does it typically include?**

To create a JavaScript artifact using NPM, you can use the `npm pack` command. This command creates a tarball (tar file) containing the application code and metadata but not the dependencies. The artifact typically includes the application code, `package.json`, and any other files specified in the configuration. By default, dependencies are not included in the artifact, so they must be installed separately on the target server.

```bash
npm pack
```

This command generates a tarball named `<project-name>-<version>.tgz`.

**Q3. Explain the process of managing dependencies for a React application using NPM or Yarn.**

For a React application, dependencies are managed using `package.json`. When you run `npm install` or `yarn install`, NPM or Yarn downloads the dependencies listed in `package.json` and stores them in the `node_modules` directory. This includes both the React framework and any other libraries required by the application.

To install dependencies:

```bash
npm install
# or
yarn install
```

These commands ensure that all necessary libraries are available for the application to run correctly.

**Q4. How does Webpack contribute to the build process of a React application, and what are the typical steps involved?**

Webpack is a build tool that compiles, transpiles, and bundles the source code of a React application. The typical steps involved in using Webpack include:

1. **Configuration**: Define the entry point, output path, and loaders in the `webpack.config.js` file.
2. **Transpilation**: Convert modern JavaScript code to a version compatible with older browsers.
3. **Bundling**: Combine multiple source files into a single bundle.
4. **Minification**: Reduce the size of the final bundle to improve performance.

Example `webpack.config.js`:

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

To build the application:

```bash
npm run build
```

This command runs Webpack, which processes the source code according to the configuration and outputs the bundled and optimized code.

**Q5. Describe the differences between packaging a Node.js backend and a React frontend, and explain why these differences exist.**

The main differences between packaging a Node.js backend and a React frontend lie in the nature of the code and the requirements for deployment:

- **Node.js Backend**: The backend code is typically written in modern JavaScript and does not require transpilation. Dependencies are managed via `package.json`, and the artifact often includes only the application code and metadata. Dependencies are installed separately on the server using `npm install`.
  
- **React Frontend**: The frontend code requires transpilation to ensure compatibility with older browsers. Additionally, the code needs to be minified and bundled to optimize performance. Tools like Webpack handle these tasks. The artifact includes the compiled and minified code, ready for deployment to a web server.

These differences exist because the backend runs on a server where modern JavaScript is supported, while the frontend runs in a browser that may not support the latest JavaScript features. Therefore, the frontend requires additional processing steps to ensure compatibility and performance.

**Q6. What are the advantages and disadvantages of having separate `package.json` files for the frontend and backend in a full-stack JavaScript application?**

Advantages:
- **Modular Dependency Management**: Separate `package.json` files allow for independent management of dependencies specific to the frontend and backend, reducing conflicts and ensuring that each part of the application has the necessary dependencies.
- **Clarity and Maintainability**: Keeping dependencies separate can make the project structure clearer and easier to maintain, especially in larger teams.

Disadvantages:
- **Complexity**: Managing multiple `package.json` files can introduce complexity, particularly when dealing with shared dependencies or when coordinating updates across the frontend and backend.
- **Potential Duplication**: There might be duplication of effort in managing dependencies, especially if certain libraries are used in both the frontend and backend.

**Q7. How would you configure Webpack to handle both the frontend and backend code in a full-stack JavaScript application?**

To configure Webpack to handle both the frontend and backend code, you can set up multiple configurations or use a single configuration with conditional logic. Here’s an example of a single configuration that handles both:

```javascript
const path = require('path');
const { merge } = require('webpack-merge');

const commonConfig = {
  entry: {
    frontend: './src/frontend/index.js',
    backend: './src/backend/index.js'
  },
  output: {
    filename: '[name].bundle.js',
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

const frontendConfig = {
  entry: './src/frontend/index.js',
  output: {
    filename: 'frontend.bundle.js',
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

const backendConfig = {
  entry: './src/backend/index.js',
  output: {
    filename: 'backend.bundle.js',
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

module.exports = (env, argv) => {
  if (argv.mode === 'development') {
    return merge(commonConfig, frontendConfig);
  } else if (argv.mode === 'production') {
    return merge(commonConfig, backendConfig);
  }
};
```

In this configuration, Webpack can handle both frontend and backend code based on the mode (`development` or `production`). This allows for flexibility and ensures that the appropriate code is processed and bundled correctly.

---
<!-- nav -->
[[04-Packaging Applications with WAR Files|Packaging Applications with WAR Files]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/25-JavaScript Artifact Building with NPM and Yarn/00-Overview|Overview]]
