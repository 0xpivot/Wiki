---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the GitOps pipeline described in the lecture.**

The GitOps pipeline described in the lecture serves to automate the process of updating the Kustomization file with new image tags after a successful CI pipeline run. This ensures that the latest version of the microservice images is deployed to the Kubernetes cluster. The pipeline uses tools like `yq` for YAML file manipulation and Git for version control operations, ensuring that the changes are committed and pushed back to the repository in a secure manner.

**Q2. How does the pipeline ensure that it doesn’t trigger an infinite loop of commits and builds?**

To prevent an infinite loop of commits and builds, the pipeline includes a `CI_SKIP` parameter in the `git push` command. This parameter tells GitLab to skip triggering a new pipeline when the current pipeline commits changes back to the repository. By doing this, the pipeline avoids re-triggering itself repeatedly, which could lead to an infinite loop.

**Q3. Describe the steps involved in updating the Kustomization file with the new image tag using `yq`.**

The steps involved in updating the Kustomization file with the new image tag using `yq` include:

1. Checking out the main branch of the repository.
2. Using `yq` to locate the specific microservice in the Kustomization file.
3. Updating the image tag for that microservice with the new tag value.
4. Committing the changes to the repository.
5. Pushing the changes back to the repository.

Here is an example of the `yq` command used to update the image tag:

```bash
yq e '.images[] | select(.name == env.MICROSERVICE_NAME).newTag = env.NEW_IMAGE_TAG' overlays/dev/kustomization.yaml -i
```

This command finds the microservice with the specified name (`env.MICROSERVICE_NAME`) and updates its `newTag` field with the new image tag (`env.NEW_IMAGE_TAG`).

**Q4. Why is it important to use a personal access token for authentication in the GitOps pipeline?**

Using a personal access token for authentication in the GitOps pipeline is important for several reasons:

1. **Security**: Personal access tokens provide a secure way to authenticate API requests without exposing your username and password. They can be restricted to specific scopes and permissions, reducing the risk of unauthorized access.
   
2. **Least Privilege Access**: A personal access token can be configured with minimal permissions required for the pipeline to function. This adheres to the principle of least privilege, ensuring that the pipeline has only the necessary access to perform its tasks.

3. **Granularity**: Personal access tokens can be created specifically for the pipeline, allowing for granular control over which repositories or resources the token can access. This is particularly useful in environments where multiple pipelines and repositories exist.

**Q5. How does the pipeline determine which microservice and new image tag to update in the Kustomization file?**

The pipeline determines which microservice and new image tag to update in the Kustomization file by receiving these details as environment variables from the preceding CI pipeline. Specifically, the CI pipeline that builds and tests the microservice code passes the `MICROSERVICE_NAME` and `NEW_IMAGE_TAG` as environment variables to the GitOps pipeline. These variables are then used in the `yq` command to update the appropriate fields in the Kustomization file.

**Q6. What are the security implications of using a personal access token for the GitOps pipeline?**

The security implications of using a personal access token for the GitOps pipeline include:

1. **Exposure Risk**: If the personal access token is exposed, it could potentially be used by unauthorized parties to access the repository and make changes. Therefore, it is crucial to keep the token secure and limit its exposure.

2. **Access Control**: The personal access token should be configured with the minimum necessary permissions to perform the required actions. This reduces the potential damage if the token is compromised.

3. **Token Revocation**: In the event of a suspected compromise, the personal access token can be revoked immediately, preventing further unauthorized access.

Recent real-world examples such as the GitHub data breach in 2021 highlight the importance of securing access tokens and limiting their scope to minimize potential damage.

---
<!-- nav -->
[[29-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]]
