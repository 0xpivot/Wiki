---
course: DevSecOps
topic: Debunking DevSecOps Myths
tags: [devsecops]
---

## Debunking DevSecOps Myths

### Myth 1: The Security Team Still Needs to Do All Security Checks

One of the most pervasive myths in the realm of DevSecOps is the belief that the security team must conduct all security checks. This notion often stems from traditional software development practices where security was treated as an afterthought, and the security team would review the code post-development. However, this approach introduces significant delays and inefficiencies into the agile development process.

#### Why This Myth Is Misleading

By relying solely on the security team to perform all security checks, you introduce several issues:

1. **Delays**: Handing off code to the security team for review can significantly delay the release cycle. In an agile environment, speed and agility are paramount, and any delay can disrupt the continuous delivery pipeline.
   
2. **Inefficiency**: Manual reviews by the security team can be time-consuming and prone to human error. Automated checks integrated into the development process can be more consistent and accurate.

3. **Lack of Ownership**: Developers may feel less responsible for security if they believe the security team will catch any issues. This can lead to a lack of ownership and accountability among developers.

#### How to Codify Security Checks

To address these issues, the security team should work closely with developers to codify their security checks. This means creating automated tests and checks that can be integrated into the continuous integration/continuous deployment (CI/CD) pipeline.

##### Example: Static Application Security Testing (SAST)

Static Application Security Testing (SAST) tools can be integrated into the CI/CD pipeline to automatically scan code for vulnerabilities. Here’s an example using SonarQube, a popular SAST tool:

```yaml
# Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
    }
}
```

In this example, the `Jenkinsfile` includes a stage for SonarQube analysis, which runs automatically whenever code is pushed to the repository.

#### Benefits of Automating Security Checks

1. **Consistency**: Automated checks ensure that security standards are consistently applied across the entire codebase.
   
2. **Speed**: Automated checks can run much faster than manual reviews, reducing the time to identify and fix issues.

3. **Integration**: By integrating security checks into the CI/CD pipeline, developers receive immediate feedback on potential security issues, allowing them to address problems early in the development cycle.

### Myth 2: We Don’t Have Enough Resources to Do DevSecOps

Another common myth is that organizations lack the necessary resources to implement DevSecOps. This often leads to the belief that purchasing a tool will solve the problem. While tools are essential, they are not a substitute for a cultural shift towards DevSecOps.

#### Why This Myth Is Misleading

1. **Culture Over Tools**: DevSecOps is fundamentally about fostering a culture where security is everyone's responsibility. Simply buying a tool does not change the underlying culture and mindset of the organization.

2. **Tool Limitations**: While tools can automate certain aspects of security, they cannot replace the need for skilled personnel who understand both development and security principles.

3. **Implementation Challenges**: Implementing DevSecOps requires a holistic approach that includes training, process changes, and organizational alignment. A tool alone cannot achieve this.

#### Building a DevSecOps Culture

To effectively implement DevSecOps, organizations need to focus on building a culture that prioritizes security throughout the development lifecycle. This involves several key steps:

1. **Training and Awareness**: Educate developers and other stakeholders about the importance of security and provide them with the skills needed to integrate security into their daily tasks.

2. **Process Integration**: Integrate security practices into existing development processes. This might involve modifying workflows, implementing new tools, and establishing clear guidelines for security practices.

3. **Collaboration**: Encourage collaboration between development, operations, and security teams. This can be achieved through regular meetings, shared goals, and cross-functional training.

##### Example: Training Programs

Organizations can implement training programs to educate developers about security best practices. For instance, a company might offer courses on secure coding practices, such as those provided by the Open Web Application Security Project (OWASP).

```markdown
# Secure Coding Training Program

---
<!-- nav -->
[[01-Course Outline|Course Outline]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/03-Debunking DevSecOps Myths/02-More DevSecOps Myths/00-Overview|Overview]] | [[03-Learning Objectives|Learning Objectives]]
