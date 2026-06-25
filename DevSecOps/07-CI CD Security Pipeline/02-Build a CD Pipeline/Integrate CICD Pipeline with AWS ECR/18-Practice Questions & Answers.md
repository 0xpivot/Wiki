---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why using AWS CLI to retrieve ECR login credentials is considered more secure compared to hardcoding passwords.**

The use of AWS CLI to retrieve ECR login credentials is considered more secure because it avoids the need to store static passwords in code or environment variables. Instead, the AWS CLI retrieves a temporary access token that is valid for only one hour. This means that even if someone manages to steal the token, it will expire within an hour, rendering it useless. Additionally, the dynamic retrieval of credentials ensures that there is no static data to be compromised, reducing the risk of unauthorized access.

**Q2. How would you configure the AWS CLI in a CICD pipeline to authenticate with ECR and push Docker images?**

To configure the AWS CLI in a CICD pipeline to authenticate with ECR and push Docker images, follow these steps:

1. **Install AWS CLI**: Ensure that the AWS CLI is installed in the Docker image used by the pipeline. This can be done by adding installation commands to the pipeline script. For example:
    ```sh
    apk add --no-cache python3 py3-pip
    pip3 install awscli
    ```

2. **Set Environment Variables**: Set the necessary environment variables for AWS access key, secret key, and default region. These can be defined in the pipeline configuration:
    ```sh
    export AWS_ACCESS_KEY_ID=<your-access-key>
    export AWS_SECRET_ACCESS_KEY=<your-secret-key>
    export AWS_DEFAULT_REGION=<your-region>
    ```

3. **Authenticate with ECR**: Use the `aws ecr get-login-password` command to authenticate with ECR:
    ```sh
    aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
    ```

4. **Build and Push Docker Image**: Build the Docker image and push it to the ECR repository. Use dynamic tags such as the commit SHA for uniqueness and a `latest` tag for convenience:
    ```sh
    docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:$CI_COMMIT_SHA .
    docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:$CI_COMMIT_SHA $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:$CI_COMMIT_SHA
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:latest
    ```

By following these steps, you ensure that the pipeline securely interacts with ECR and maintains best practices for handling credentials.

**Q3. What are the benefits of using dynamic tags (e.g., commit SHA) for Docker images in a CICD pipeline?**

Using dynamic tags for Docker images in a CICD pipeline offers several benefits:

1. **Uniqueness**: Each build generates a unique tag based on the commit SHA, ensuring that each image is uniquely identifiable and traceable. This helps in maintaining a clear history of builds and deployments.

2. **Consistency**: Dynamic tags help maintain consistency between the source code and the deployed image. Since the tag is derived from the commit SHA, it directly links the image to the specific version of the codebase.

3. **Rollback Capability**: With unique tags, it becomes easier to roll back to a previous version of the application if a newer version introduces issues. Simply redeploying the image with the old tag can revert the application to a known stable state.

4. **Automation**: Dynamic tagging integrates seamlessly with automated pipelines. The pipeline can automatically generate the tag based on the current commit, eliminating the need for manual intervention.

5. **Security**: Using dynamic tags reduces the risk associated with static tags. Static tags might be reused, leading to potential confusion or security risks if an older image is mistakenly deployed under a new tag.

For example, if a pipeline uses the commit SHA as a tag, it ensures that each build corresponds to a specific version of the code, facilitating easier debugging and maintenance.

**Q4. How can you ensure that the pipeline does not fail due to expired tokens or security checks?**

To ensure that the pipeline does not fail due to expired tokens or security checks, you can implement the following strategies:

1. **Comment Out Failing Jobs**: Temporarily comment out jobs that may cause failures due to expired tokens or security checks. For example, if a job relies on a DefectDojo API token that expires frequently, you can comment it out:
    ```yaml
    # - script:
    #     - defectdojo-api --token $DEFECTDOJO_API_TOKEN ...
    ```

2. **Configure Allow Failure**: Configure jobs to allow failures without stopping the pipeline. This can be done by setting the `allow_failure` flag in the pipeline configuration:
    ```yaml
    - script:
        - defectdojo-api --token $DEFECTDOJO_API_TOKEN ...
      allow_failure: true
    ```

3. **Automate Token Renewal**: Implement automation to renew tokens periodically. This can be achieved by setting up a cron job or a scheduled task that regenerates the token before it expires.

4. **Use Short-Lived Tokens**: Utilize short-lived tokens that are automatically refreshed. For example, AWS IAM roles can be configured to provide temporary credentials that are valid for a short duration and automatically renewed.

By implementing these strategies, you can ensure that the pipeline remains robust and continues to function even when certain components temporarily fail.

**Q5. Describe how to set up a CICD pipeline to build and push Docker images to AWS ECR, including the necessary steps and commands.**

To set up a CICD pipeline to build and push Docker images to AWS ECR, follow these steps:

1. **Install AWS CLI**: Ensure the AWS CLI is installed in the Docker image used by the pipeline. Add the installation commands to the pipeline script:
    ```sh
    apk add --no-cache python3 py3-pip
    pip3 install awscli
    ```

2. **Set Environment Variables**: Define the necessary environment variables for AWS access key, secret key, and default region:
    ```sh
    export AWS_ACCESS_KEY_ID=<your-access-key>
    export AWS_SECRET_ACCESS_KEY=<your-secret-key>
    export AWS_DEFAULT_REGION=<your-region>
    export AWS_ACCOUNT_ID=<your-account-id>
    ```

3. **Authenticate with ECR**: Use the `aws ecr get-login-password` command to authenticate with ECR:
    ```sh
    aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
    ```

4. **Build and Tag Docker Image**: Build the Docker image and tag it with a unique identifier (e.g., commit SHA) and a `latest` tag:
    ```sh
    docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:$CI_COMMIT_SHA .
    docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:$CI_COMMIT_SHA $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:latest
    ```

5. **Push Docker Image**: Push the tagged images to the ECR repository:
    ```sh
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:$CI_COMMIT_SHA
    docker push $AWS_ACCOUNT_ ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/juice-shop:latest
    ```

6. **Commit Changes**: Commit the changes to the pipeline configuration to ensure that the pipeline runs smoothly.

By following these steps, you can set up a robust CICD pipeline that securely builds and pushes Docker images to AWS ECR, ensuring that the images are uniquely tagged and easily traceable.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/20-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Integrate CICD Pipeline with AWS ECR/00-Overview|Overview]]
