---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the advantages of using an external script for security testing in a Jenkins pipeline over using a plugin.**

The primary advantage of using an external script for security testing in a Jenkins pipeline is the flexibility and control it provides. External scripts can be customized more easily to meet specific needs and can be tested independently outside of the CI/CD environment. This allows developers to verify the script's functionality before integrating it into the pipeline. Additionally, external scripts can be version-controlled alongside the application code, ensuring consistency and traceability. Plugins, while convenient, may lack the customization options and might not be as readily adaptable to changing requirements.

**Q2. How would you configure a Jenkins pipeline to execute an external script for security testing?**

To configure a Jenkins pipeline to execute an external script for security testing, follow these steps:

1. Create the external script, such as `linter.sh`, and place it in the repository.
2. Ensure the script has execute permissions (`chmod +x linter.sh`).
3. Modify the Jenkinsfile to include a stage that executes the external script using the `sh` step. For example:
   ```groovy
   pipeline {
       agent any
       stages {
           stage('Security Test') {
               steps {
                   sh './test/linter.sh'
               }
           }
       }
   }
   ```
4. Commit the changes to the repository and push them to trigger the Jenkins pipeline.

**Q3. What is the role of Docker in the context of running security tests via an external script in Jenkins?**

Docker plays a crucial role in providing a consistent and isolated environment for running security tests. By using a Docker container, the external script can run in a standardized environment that mirrors production conditions, ensuring that the tests are reliable and repeatable. This isolation helps prevent issues caused by differences in local development environments or server configurations. For instance, the Docker container might contain a specific version of a linter tool that is used to check the codebase for security vulnerabilities.

**Q4. Why is it important to have the external script executable and located within the repository?**

It is important to have the external script executable and located within the repository for several reasons:

1. **Version Control**: Keeping the script in the repository ensures that it is version-controlled along with the rest of the codebase. This allows tracking changes and maintaining a history of the script.
2. **Consistency**: Having the script in the repository ensures that all team members and the CI/CD system use the same version of the script, reducing inconsistencies.
3. **Execution Permissions**: Making the script executable (`chmod +x`) ensures that it can be run directly from the command line or within the Jenkins pipeline without additional steps.
4. **Ease of Use**: Locating the script within the repository simplifies the process of referencing and executing the script in the Jenkinsfile, making the pipeline setup straightforward and maintainable.

**Q5. How does the Jenkins pipeline detect and build the new branch after pushing the changes?**

Jenkins detects and builds the new branch automatically through its polling mechanism or webhook configuration. When changes are pushed to the repository, Jenkins can be configured to either periodically poll the repository for updates or receive notifications via webhooks. Once Jenkins detects the new branch, it triggers a build according to the defined pipeline in the Jenkinsfile. This process ensures that the pipeline runs the necessary stages, including the execution of the external security script, whenever changes are made to the branch.

**Q6. Discuss a recent real-world example where integrating automated security testing into a CI/CD pipeline helped identify a vulnerability.**

A notable example is the identification of the Log4j vulnerability (CVE-2021-44228). Many organizations integrated automated security testing tools into their CI/CD pipelines to scan for known vulnerabilities, including those related to Log4j. These tools, often part of the pipeline, flagged instances where vulnerable versions of Log4j were being used. This early detection allowed teams to quickly address the issue, mitigate risks, and prevent potential breaches. The integration of such automated security tests into the pipeline ensured that security was a continuous part of the development process, rather than an afterthought.

---
<!-- nav -->
[[03-Using External Scripts for Automated Security Testing|Using External Scripts for Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/06-Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Scripts/00-Overview|Overview]]
