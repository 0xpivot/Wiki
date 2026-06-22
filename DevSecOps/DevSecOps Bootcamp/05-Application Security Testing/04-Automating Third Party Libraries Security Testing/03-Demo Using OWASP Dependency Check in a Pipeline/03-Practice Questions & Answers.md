---
course: DevSecOps
topic: Automating Third Party Libraries Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of integrating OWASP Dependency Check into a CI/CD pipeline.**

Integrating OWASP Dependency Check into a CI/CD pipeline helps ensure that the software dependencies used in a project are free from known vulnerabilities. This is crucial for maintaining the security posture of the application throughout its development lifecycle. By automating the process, teams can catch and address security issues early, reducing the risk of deploying vulnerable components.

**Q2. How would you configure a Jenkins pipeline to run OWASP Dependency Check using a Docker image?**

To configure a Jenkins pipeline to run OWASP Dependency Check using a Docker image, you need to add a new stage in your Jenkinsfile. Here’s an example:

```groovy
pipeline {
    agent { docker 'owasp/dependency-check' }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Dependency Check') {
            steps {
                script {
                    def reportDir = "${WORKSPACE}/reports"
                    sh """
                        mkdir -p ${reportDir}
                        dependency-check --project "JuShop" --scan . --out ${reportDir} --format "HTML"
                    """
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*.html', allowEmptyArchive: true
        }
    }
}
```

This configuration uses the `owasp/dependency-check` Docker image to run the dependency check on the project. The report is saved to a `reports` directory, ensuring that the original source remains untouched.

**Q3. Why is it important to map a separate directory for reports when using a Docker image for OWASP Dependency Check?**

Mapping a separate directory for reports when using a Docker image for OWASP Dependency Check is important because it ensures that the original source code remains read-only. This practice enhances security by preventing the Docker container from modifying the source code directly. Additionally, it allows for better organization and separation of concerns between the source code and the generated reports.

**Q4. How does OWASP Dependency Check determine whether a build should fail based on vulnerabilities?**

OWASP Dependency Check can be configured to fail the build if it detects vulnerabilities with a certain CVSS score threshold. For example, in the Jenkinsfile snippet provided, the build fails if any vulnerability has a CVSS score of 6 or higher. This is achieved by setting appropriate parameters in the `dependency-check` command, such as `--failOnCVSS 6`.

**Q5. What recent real-world examples highlight the importance of using tools like OWASP Dependency Check in a CI/CD pipeline?**

One notable example is the Log4j vulnerability (CVE-2021-44228), which affected numerous applications globally. Many organizations were caught off guard due to the widespread use of the Log4j library in their applications. Integrating tools like OWASP Dependency Check into CI/CD pipelines could have helped identify and mitigate such vulnerabilities earlier. By continuously scanning dependencies, teams can stay informed about potential risks and take proactive measures to secure their applications.

**Q6. How would you modify the Jenkins pipeline to schedule OWASP Dependency Check runs asynchronously rather than on every code commit?**

To schedule OWASP Dependency Check runs asynchronously, you can create a separate Jenkins job that runs periodically (e.g., daily). Here’s an example of how you might set this up:

1. Create a new Jenkins job for the asynchronous scan.
2. Configure the job to run on a schedule (e.g., daily).
3. Use the same Jenkinsfile configuration as before but ensure it only triggers this new job.

Here’s an example of the Jenkinsfile for the asynchronous job:

```groovy
pipeline {
    agent { docker 'owasp/dependency-check' }
    triggers {
        cron('H H(0-23) * * *') // Runs once per day at a random hour
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://gitlab.com/your-repo/JuShop.git'
            }
        }
        stage('Dependency Check') {
            steps {
                script {
                    def reportDir = "${WORKSPACE}/reports"
                    sh """
                        mkdir -p ${reportDir}
                        dependency-check --project "JuShop" --scan . --out ${reportDir} --format "HTML"
                    """
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*.html', allowEmptyArchive: true
        }
    }
}
```

By scheduling the job to run asynchronously, you can still benefit from regular security checks without impacting the speed of frequent code commits.

---
<!-- nav -->
[[02-Automating Third-Party Libraries Security Testing Using OWASP Dependency Check in a Pipeline|Automating Third-Party Libraries Security Testing Using OWASP Dependency Check in a Pipeline]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/04-Automating Third Party Libraries Security Testing/03-Demo Using OWASP Dependency Check in a Pipeline/00-Overview|Overview]]
