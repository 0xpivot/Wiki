---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Pipeline Configuration with Groovy Scripts

In the realm of continuous integration and continuous delivery (CI/CD), Jenkins has emerged as one of the most popular tools for automating the software development lifecycle. One of the key features of Jenkins is its ability to define and manage pipelines using Groovy scripts. These scripts provide a powerful and flexible way to automate the build, test, and deployment processes. In this chapter, we will delve deep into the world of creating pipelines using Groovy scripts in Jenkins, covering everything from basic concepts to advanced techniques and security considerations.

### What is a Jenkins Pipeline?

A Jenkins Pipeline is a way to model your continuous integration and continuous delivery process. It allows you to define a series of steps that are executed in a specific order, often referred to as a "pipeline." Each step in the pipeline can perform various tasks such as building the code, running tests, deploying the application, and more. The pipeline is defined using a Groovy script, which provides a declarative or scripted approach to defining the workflow.

### Why Use Groovy Scripts for Pipelines?

Groovy is a versatile programming language that is well-suited for scripting and automation tasks. It is tightly integrated with Jenkins, making it an ideal choice for defining pipelines. Here are some reasons why Groovy scripts are preferred for Jenkins pipelines:

1. **Flexibility**: Groovy provides a high degree of flexibility, allowing you to define complex workflows with ease.
2. **Readability**: Groovy scripts are easy to read and understand, making them accessible to developers and operations teams alike.
3. **Integration**: Groovy integrates seamlessly with Jenkins, providing access to a wide range of plugins and features.
4. **Extensibility**: Groovy scripts can be extended with custom functions and libraries, enabling you to tailor the pipeline to your specific needs.

### Basic Syntax of a Groovy Script

Before diving into the details of creating pipelines, let's first understand the basic syntax of a Groovy script. A simple Groovy script might look like this:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
```

This script defines a pipeline with three stages: Build, Test, and Deploy. Each stage contains a set of steps that are executed sequentially. The `agent` directive specifies the environment in which the pipeline runs, and `any` indicates that the pipeline can run on any available agent.

### Pipeline Script Options in Jenkins

When configuring a pipeline in Jenkins, you have several options for specifying the pipeline script:

1. **Pipeline script**: You can write the pipeline script directly in the Jenkins UI.
2. **Pipeline script from SCM**: You can store the pipeline script in a version control system (SCM) and reference it in Jenkins.
3. **Pipeline script from a file**: You can specify a file path where the pipeline script is stored.

For this chapter, we will focus on writing the pipeline script directly in the Jenkins UI.

### Sample Pipeline Scripts

Jenkins provides several sample pipeline scripts to help you get started. Let's explore two of these samples: "Hello World" and "GitHub Maven."

#### Hello World Pipeline

The "Hello World" pipeline is a simple example that demonstrates the basic structure of a pipeline script. Here is what the script looks like:

```groovy
pipeline {
    agent any
    stages {
        stage('Hello') {
            steps {
                echo 'Hello, World!'
            }
        }
    }
}
```

This script defines a single stage called "Hello" that simply prints "Hello, World!" to the console.

#### GitHub Maven Pipeline

The "GitHub Maven" pipeline is a more complex example that demonstrates how to integrate with a GitHub repository and build a Maven project. Here is what the script looks like:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/example/maven-project.git'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

This script defines two stages: "Checkout" and "Build." The "Checkout" stage clones the specified GitHub repository, and the "Build" stage runs the Maven `clean package` command to build the project.

### Groovy Sandbox

One important aspect of using Groovy scripts in Jenkins is the Groovy sandbox. The sandbox is a security feature that restricts the execution of certain Groovy functions to prevent potential security risks. When the Groovy sandbox is enabled, only a limited set of functions are allowed to be executed without requiring approval from a Jenkins administrator.

#### Enabling the Groovy Sandbox

To enable the Groovy sandbox, you need to check the "Groovy sandbox" checkbox in the Jenkins UI when configuring the pipeline. This ensures that the script can only use the whitelisted functions, which are considered safe.

#### Whitelisted Functions

The whitelisted functions are those that are deemed safe and non-risky when executed on Jenkins. These functions typically include basic operations such as printing messages, reading files, and executing shell commands. Here are some examples of whitelisted functions:

- `echo`: Prints a message to the console.
- `sh`: Executes a shell command.
- `readFile`: Reads the contents of a file.

#### Custom Functions and Libraries

If you need to use custom functions or libraries that are not whitelisted, you will need to obtain approval from a Jenkins administrator. Once approved, you can use these functions in your pipeline script. However, it is important to exercise caution when using custom functions, as they may introduce security risks.

### How to Prevent / Defend Against Security Risks

While the Groovy sandbox helps mitigate security risks, it is essential to follow best practices to ensure the security of your Jenkins pipelines. Here are some key strategies to consider:

#### Secure Coding Practices

1. **Use the Groovy Sandbox**: Always enable the Groovy sandbox to restrict the execution of potentially risky functions.
2. **Whitelist Functions**: Only use functions that are whitelisted and deemed safe.
3. **Avoid Hardcoding Credentials**: Do not hardcode sensitive information such as passwords or API keys in your pipeline scripts. Instead, use Jenkins credentials management to securely store and manage sensitive data.
4. **Validate Inputs**: Ensure that any input to your pipeline is properly validated to prevent injection attacks.

#### Detection and Prevention

1. **Regular Audits**: Regularly audit your pipeline scripts to identify and address any security vulnerabilities.
2. **Security Plugins**: Utilize Jenkins security plugins such as the "Script Security Plugin" to enforce additional security measures.
3. **Least Privilege Principle**: Run your pipeline agents with the least privilege necessary to minimize the potential impact of a security breach.

#### Secure Code Examples

Here is an example of a vulnerable pipeline script that hardcodes a password:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sh 'ssh user@server -p 12345'
            }
        }
    }
}
```

To secure this script, you should use Jenkins credentials management to store the password securely:

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-credentials-id', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]) {
                    sh 'ssh $USER@server -p $PASSWORD'
                }
            }
        }
    }
}
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of securing Jenkins pipelines. For example, the CVE-2018-19535 vulnerability in the Jenkins Script Security Plugin allowed attackers to bypass the sandbox and execute arbitrary code. To prevent such vulnerabilities, it is crucial to keep Jenkins and its plugins up to date and to follow secure coding practices.

### Complete Example: Full Pipeline with Request/Response/Result

Let's walk through a complete example of a Jenkins pipeline that integrates with a GitHub repository and deploys the application to a server. We will also include the full HTTP request and response for clarity.

#### Pipeline Script

```groovy
pipeline {
    agent any
    environment {
        GIT_URL = 'https://github.com/example/maven-project.git'
        SSH_USER = 'deploy-user'
        SSH_PASSWORD = credentials('ssh-password')
    }
    stages {
        stage('Checkout') {
            steps {
                git url: env.GIT_URL, branch: 'main'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'ssh-credentials', usernameVariable: 'SSH_USER', passwordVariable: 'SSH_PASSWORD')]) {
                    sh 'scp target/myapp.jar ${SSH_USER}@server:/opt/app/'
                }
            }
        }
    }
}
```

#### HTTP Request and Response

When the pipeline executes the `git` command, it sends an HTTP request to the GitHub repository. Here is an example of the full HTTP request and response:

**HTTP Request**

```http
GET /repos/example/maven-project/git/refs/heads/main HTTP/1.1
Host: api.github.com
Authorization: Bearer <your-access-token>
User-Agent: Jenkins
Accept: application/vnd.github.v3+json
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 123
Connection: keep-alive
Server: GitHub.com

{
  "ref": "refs/heads/main",
  "url": "https://api.github.com/repos/example/maven-project/git/refs/heads/main",
  "object": {
    "sha": "abc123def456ghi789jkl012mno345pqr678stu901vwxyza2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 123
Connection: keep-alive
Server: GitHub.com

{
  "ref": "refs/heads/main",
  "url": "https://api.github.com/repos/example/maven-project/git/refs/heads/main",
  "object": {
    "sha": "abc111def222ghi333jkl444mno555pqr666stu777vwxy888za999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m777n888o999p000q111r222s333t444u555v666w777x888y999z000a111b222c333d444e555f666g777h888i999j000k111l222m333n444o555p666q777r888s999t000u111v222w333x444y555z666a777b888c999d000e111f222g333h444i555j666k777l888m999n000o111p222q333r444s555t666u777v888w999x000y111z222a333b444c555d666e777f888g999h000i111j222k333l444m555n666o777p888q999r000s111t222u333v444w555x666y777z888a999b000c111d222e333f444g555h666i777j888k999l000m111n222o333p444q555r666s777t888u999v000w111x222y333z444a555b666c777d888e999f000g111h222i333j444k555l666m77

---
<!-- nav -->
[[04-Introduction to Jenkins Pipeline and Groovy Scripts|Introduction to Jenkins Pipeline and Groovy Scripts]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/16-Creating Pipelines Using Groovy Scripts/00-Overview|Overview]] | [[06-Introduction to Pipeline Creation Using Groovy Scripts|Introduction to Pipeline Creation Using Groovy Scripts]]
