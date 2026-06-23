---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Running the Jenkins Pipeline

Once the Jenkinsfile is configured, the pipeline can be triggered to run.

### Triggering the Pipeline

1. **Create a New Job**: In Jenkins, create a new job and specify the Jenkinsfile location.
2. **Run the Job**: Trigger the job to start the pipeline execution.

### Monitoring the Pipeline Execution

During the execution of the pipeline, you can monitor the progress through the Jenkins UI.

### Analyzing Dependencies with Dependency Track

While the pipeline is running, you can also check the Dependency Track dashboard to see the analysis results.

1. **Access Dependency Track Dashboard**: Open the Dependency Track dashboard in a web browser.
2. **Check Projects**: Navigate to the projects section to view the analysis results for the `Tools Image Project`.
3. **View Components**: Click on the project to view the detected components and their associated vulnerabilities.

### Example Analysis Results

In the provided scenario, the Dependency Track server did not find any vulnerabilities in the third-party libraries being used. This indicates that the dependencies are secure.

### Verifying the Results in Jenkins

After the pipeline completes, you can verify the results in Jenkins.

1. **Refresh Jenkins Page**: Refresh the Jenkins page to see the updated build status.
2. **View Dashboard**: Check the right-hand side of the Jenkins page to see the dashboard indicating the successful verification of the software build materials.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Plugins/05-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Plugins/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/Demo Integrating Automated Security Testing into a Jenkins Pipeline Using Plugins/07-Setting Up Jenkins and Dependency Track|Setting Up Jenkins and Dependency Track]]
