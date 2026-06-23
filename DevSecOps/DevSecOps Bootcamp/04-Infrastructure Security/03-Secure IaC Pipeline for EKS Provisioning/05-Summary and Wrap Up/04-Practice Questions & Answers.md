---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how the pipeline ensures secure access management for the EKS cluster.**

The pipeline ensures secure access management for the EKS cluster by avoiding the use of static credentials. Instead, it uses temporary credentials that are generated on-demand for each job execution. These credentials are automatically revoked once the job is completed, ensuring that there are no lingering active credentials that could be misused. Additionally, access to the cluster is restricted such that no human or system user can directly access the cluster without assuming a specific AWS role, further enhancing security.

**Q2. How would you implement a cleanup job in the pipeline to avoid unnecessary costs?**

To implement a cleanup job in the pipeline to avoid unnecessary costs, you would follow these steps:

1. Add a new job in the pipeline configuration specifically designated for cleanup.
2. Ensure this cleanup job runs after the deployment stage.
3. In the cleanup job, execute `terraform destroy` to remove all the resources created during the pipeline execution.
4. Optionally, configure the cleanup job to require a manual trigger to ensure it is only executed when intended.

Here’s an example snippet of how you might configure this in a GitLab CI/CD pipeline:

```yaml
stages:
  - build
  - deploy
  - cleanup

build_job:
  stage: build
  script:
    - echo "Building the application"

deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application"
    - terraform apply -auto-approve

cleanup_job:
  stage: cleanup
  when: manual
  script:
    - echo "Cleaning up resources"
    - terraform destroy -auto-approve
```

This setup ensures that the cleanup job is only executed manually, preventing accidental resource deletion.

**Q3. Why is it important to clean up resources after completing a demo or learning exercise?**

It is crucial to clean up resources after completing a demo or learning exercise to avoid unnecessary costs. Cloud services like AWS charge for the resources that are provisioned and running, even if they are not actively being used. By cleaning up these resources, you prevent charges for resources that are no longer needed. This practice also helps maintain good cloud hygiene and ensures that your account remains organized and free of unused resources.

**Q4. What are the potential risks of using static credentials in a pipeline?**

Using static credentials in a pipeline poses several significant risks:

1. **Exposure Risk**: Static credentials can be exposed through various means, such as insecure storage, accidental commits to version control systems, or unauthorized access to the repository.
2. **Longevity Risk**: Once static credentials are compromised, they remain vulnerable until they are explicitly changed. This can lead to prolonged exposure to security threats.
3. **Auditability Risk**: With static credentials, it is difficult to track who accessed the system and when, making it challenging to perform effective audits and trace unauthorized activities.
4. **Compliance Risk**: Many compliance standards mandate the use of dynamic and temporary credentials to reduce the attack surface and improve security posture.

By using temporary credentials that are valid only for the duration of a job, these risks are mitigated, providing a more secure environment.

**Q5. How does the use of temporary credentials enhance security in the pipeline?**

The use of temporary credentials enhances security in the pipeline in several ways:

1. **Reduced Exposure Time**: Temporary credentials are valid only for the duration of a job execution, reducing the window of opportunity for misuse.
2. **No Lingering Access**: Once a job completes, the temporary credentials are invalidated, ensuring that there are no lingering access points that could be exploited.
3. **Improved Auditability**: Since the credentials are tied to specific job executions, it becomes easier to audit and trace access patterns, helping to identify any unauthorized activities.
4. **Dynamic Security Posture**: The dynamic nature of temporary credentials aligns well with modern security practices, which emphasize minimizing the attack surface and reducing the risk of credential theft.

By implementing temporary credentials, the pipeline significantly reduces the risk of unauthorized access and enhances overall security.

---
<!-- nav -->
[[03-Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning|Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/05-Summary and Wrap Up/00-Overview|Overview]]
