---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to IaC and GitOps for DevSecOps

Infrastructure as Code (IaC) and GitOps are fundamental practices in modern DevSecOps environments. IaC involves managing and provisioning infrastructure through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. GitOps, on the other hand, extends IaC by using Git as a single source of truth for all infrastructure and application configurations. This approach ensures that all changes are version-controlled, auditable, and reproducible.

### Background Theory

#### Infrastructure as Code (IaC)

IaC allows teams to manage their infrastructure using declarative configuration files. These files describe the desired state of the infrastructure, which can be applied consistently across different environments. Popular IaC tools include Terraform, Ansible, and CloudFormation.

**Why IaC Matters:**
- **Consistency:** Ensures that environments are configured identically, reducing human error.
- **Reproducibility:** Allows teams to recreate environments from scratch using the same configuration files.
- **Version Control:** Configuration files can be stored in version control systems like Git, enabling tracking of changes and rollbacks.

#### GitOps

GitOps leverages Git as the single source of truth for infrastructure and application configurations. It involves continuous integration and delivery (CI/CD) pipelines that automatically deploy changes from the Git repository to the live environment. This approach ensures that the live environment always matches the desired state defined in the Git repository.

**Why GitOps Matters:**
- **Auditing and Compliance:** All changes are tracked in Git, making it easier to audit and comply with regulatory requirements.
- **Automated Rollouts:** Changes can be automatically deployed, reducing the risk of human error.
- **Collaboration:** Teams can collaborate on infrastructure changes using familiar Git workflows.

### Integrating Automated Security Scans with IaC

One critical aspect of DevSecOps is integrating automated security scans into the CI/CD pipeline. This ensures that infrastructure configurations are checked for security vulnerabilities before being deployed. In this section, we will focus on integrating TFSEC, a static analysis tool for Terraform configurations, into a GitOps workflow.

#### Setting Up TFSEC

TFSEC is a static analysis tool designed to find security issues in Terraform configurations. It can be integrated into a CI/CD pipeline to automatically scan Terraform code for potential security vulnerabilities.

**Step-by-Step Integration:**

1. **Install TFSEC:**
   ```bash
   go install github.com/aquasecurity/tfsec/cmd/tfsec@latest
   ```

2. **Configure TFSEC in Your Pipeline:**
   - Set the format to JSON.
   - Specify the output file for the scan results.
   - Save the scan results as an artifact.

Here is an example of how to configure TFSEC in a GitLab CI/CD pipeline:

```yaml
stages:
  - validate
  - build
  - test
  - deploy

validate_infrastructure:
  stage: validate
  script:
    - tfsec --format json --out tfsec.json
  artifacts:
    paths:
      - tfsec.json
    expire_in: 1 week
```

In this configuration:
- `tfsec --format json --out tfsec.json` runs TFSEC and outputs the results in JSON format to `tfsec.json`.
- The `artifacts` section specifies that the `tfsec.json` file should be saved as an artifact, even if the job fails.

#### Handling Artifacts

Artifacts are files that are produced during the execution of a pipeline job and are stored for future reference. In the context of TFSEC, the scan results are saved as an artifact to ensure they are available for review and further processing.

**Handling Artifacts in Case of Job Failure:**

To ensure that artifacts are saved even when the job fails, you can configure the `when` keyword in your pipeline:

```yaml
validate_infrastructure:
  stage: validate
  script:
    - tfsec --format json --out tfsec.json
  artifacts:
    paths:
      - tfsec.json
    expire_in: 1 week
  when: always
```

The `when: always` directive ensures that the artifact is saved regardless of the job's outcome.

#### Committing and Pushing Changes

Once the pipeline configuration is updated, you need to commit and push the changes to trigger the pipeline:

```bash
git add .gitlab-ci.yml
git commit -m "Add TFSEC security scan to CI/CD pipeline"
git push origin main
```

### Viewing TFSEC Results

After the pipeline runs, you can view the TFSEC results by downloading the artifact:

1. Navigate to the pipeline in your CI/CD platform.
2. Click on the job that generated the artifact.
3. Download the `tfsec.json` file.

Here is an example of what the `tfsec.json` file might look like:

```json
{
  "results": [
    {
      "description": "AWS S3 bucket is publicly accessible",
      "severity": "HIGH",
      "location": {
        "file": "main.tf",
        "start_line": 10,
        "end_line": 15
      }
    },
    {
      "description": "EC2 instance is using default SSH key",
      "severity": "MEDIUM",
      "location": {
        "file": "ec2.tf",
        "start_line": 20,
        "end_line": 25
      }
    }
  ]
}
```

### Visualizing TFSEC Results

To visualize the TFSEC results, you can upload the `tfsec.json` file to a tool like DefectDojo, which provides a dashboard for reviewing security findings.

#### Example of Uploading to DefectDojo

1. Log in to DefectDojo.
2. Navigate to the "Engagements" section.
3. Create a new engagement and upload the `tfsec.json` file.

DefectDojo will parse the JSON file and display the findings in a user-friendly interface.

### Handling Deployment

If the TFSEC scan does not identify any critical issues, you can proceed with the deployment. In the given scenario, since no changes were made to the Terraform script, Terraform will check the state and confirm that everything is up to date.

#### Example of Terraform Apply

```bash
terraform init
terraform plan
terraform apply
```

The output will indicate that no resources were created or modified:

```
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

### How to Prevent / Defend

#### Secure Coding Practices

To prevent security vulnerabilities in Terraform configurations, follow these secure coding practices:

1. **Use Least Privilege Principle:** Ensure that IAM roles and policies grant only the necessary permissions.
2. **Avoid Hardcoding Secrets:** Use environment variables or secrets management tools like HashiCorp Vault.
3. **Regularly Update Dependencies:** Keep Terraform modules and plugins up to date to benefit from security patches.

#### Example of Vulnerable vs. Secure Code

**Vulnerable Code:**
```hcl
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket"
  acl    = "public-read"
}
```

**Secure Code:**
```hcl
resource "aws_s3_bucket" "private_bucket" {
  bucket = "my-private-bucket"
  acl    = "private"
}
```

#### Configuration Hardening

Hardening configurations involves setting up security controls to mitigate risks. For example, you can configure AWS S3 buckets to block public access:

```hcl
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-20225:** A vulnerability in AWS S3 bucket policies allowed unauthorized access to sensitive data.
- **Equifax Data Breach (2017):** Poorly configured AWS S3 buckets contributed to the exposure of sensitive personal information.

These examples highlight the importance of regularly scanning and securing infrastructure configurations.

### Practice Labs

For hands-on practice with integrating TFSEC into a GitOps workflow, consider the following labs:

- **PortSwigger Web Security Academy:** Offers exercises on securing web applications and infrastructure.
- **OWASP Juice Shop:** Provides a vulnerable web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application):** Another resource for practicing web application security.

### Conclusion

Integrating automated security scans like TFSEC into a GitOps workflow is crucial for maintaining secure infrastructure. By following secure coding practices, regularly updating dependencies, and hardening configurations, you can significantly reduce the risk of security vulnerabilities. Regularly reviewing and acting on scan results ensures that your infrastructure remains secure throughout its lifecycle.

---
<!-- nav -->
[[03-Introduction to IaC and GitOps for DevSecOps Part 2|Introduction to IaC and GitOps for DevSecOps Part 2]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Add Automated Security Scan to TF Infrastructure Code/00-Overview|Overview]] | [[05-Introduction to IaC and GitOps for DevSecOps|Introduction to IaC and GitOps for DevSecOps]]
