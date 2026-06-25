---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Introduction to Jenkins and Dependency Track Integration

### What is Jenkins?

Jenkins is an open-source automation server that provides continuous integration and continuous delivery (CI/CD) services. It allows developers to build, test, and deploy their applications automatically. Jenkins supports a wide range of plugins that extend its functionality, including plugins for integrating with various tools and services.

### What is Dependency Track?

Dependency Track is a software composition analysis (SCA) tool that helps organizations manage the security risks associated with third-party dependencies used in their software projects. It integrates with various package managers and repositories to provide detailed information about the components used in a project, including known vulnerabilities and licenses.

### Why Integrate Jenkins with Dependency Track?

Integrating Jenkins with Dependency Track allows you to automate the process of analyzing your project's dependencies for security vulnerabilities and license compliance issues. This integration ensures that your CI/CD pipeline includes a step to check the security and legal status of your dependencies, helping you to identify and mitigate potential risks early in the development cycle.

### How Does the Integration Work?

The integration between Jenkins and Dependency Track is achieved through a Jenkins plugin. This plugin communicates with the Dependency Track server using an API key to fetch and analyze the dependencies of your project. By configuring the plugin correctly, you can ensure that your Jenkins pipeline includes steps to interact with Dependency Track.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Installing Jenkins Plugins/02-Introduction to Jenkins and Automated Security Testing|Introduction to Jenkins and Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Installing Jenkins Plugins/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Installing Jenkins Plugins/04-Introduction to Jenkins and Integrating Automated Security Testing|Introduction to Jenkins and Integrating Automated Security Testing]]
