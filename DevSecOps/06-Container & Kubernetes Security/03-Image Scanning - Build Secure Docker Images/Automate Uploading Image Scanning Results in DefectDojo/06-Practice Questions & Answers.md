---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why using a vulnerability management tool like DefectDojo is beneficial compared to working with raw job logs.**

The primary benefit of using a vulnerability management tool like DefectDojo over raw job logs is the improved organization and visibility of security findings. Raw logs can be cumbersome to navigate, requiring manual zooming and scrolling to find specific issues. In contrast, DefectDojo consolidates findings from multiple sources into a single interface, making it easier to review and manage vulnerabilities. Additionally, DefectDojo offers features such as automatic duplicate detection, which helps in reducing the noise and focusing on unique issues. This streamlined approach ensures that security teams can efficiently prioritize and address critical vulnerabilities.

**Q2. How would you configure Trivy to export its scan results in JSON format and save them as an artifact?**

To configure Trivy to export its scan results in JSON format and save them as an artifact, you can use the following command:

```bash
trivy image --format=json --output=trivy.json <image_name>
```

This command sets the output format to JSON and saves the results to `trivy.json`. To ensure the file is saved as an artifact, you can add the following steps in your CI/CD pipeline:

```yaml
stages:
  - build
  - test
  - upload_reports

test:
  stage: test
  script:
    - trivy image --format=json --output=trivy.json <image_name>

upload_reports:
  stage: upload_reports
  dependencies:
    - test
  script:
    - # Upload trivy.json to DefectDojo
    - echo "Uploading trivy.json to DefectDojo"
  artifacts:
    paths:
      - trivy.json
```

This configuration ensures that the `trivy.json` file is saved as an artifact and can be uploaded to DefectDojo.

**Q3. What changes would you make to a Python script to automatically upload Trivy scan results to DefectDojo?**

To modify a Python script to automatically upload Trivy scan results to DefectDojo, you would need to include logic to handle the upload process. Below is an example of how you might structure the Python script:

```python
import requests
import json

def upload_trivy_results(file_path, api_token, engagement_id):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    headers = {
        'Authorization': f'Token {api_token}',
        'Content-Type': 'application/json'
    }
    
    url = f'https://your-defectdojo-instance/api/v2/import-scan/'
    payload = {
        'scan_type': 'Trivy Scan',
        'engagement': engagement_id,
        'file': ('trivy.json', json.dumps(data), 'application/json')
    }

    response = requests.post(url, headers=headers, files=payload)
    return response.status_code, response.text

# Example usage
api_token = 'your_api_token_here'
engagement_id = 19
file_path = 'trivy.json'

status_code, response_text = upload_trivy_results(file_path, api_token, engagement_id)
print(f'Status Code: {status_code}')
print(f'Response Text: {response_text}')
```

This script reads the Trivy scan results from a JSON file, constructs a POST request to the DefectDojo API, and uploads the scan results. Ensure to replace `your_defectdojo_instance`, `your_api_token_here`, and `engagement_id` with actual values.

**Q4. Why is it important to follow security best practices when creating Docker images?**

Following security best practices when creating Docker images is crucial for several reasons:

1. **Reduced Attack Surface**: By adhering to best practices, you minimize the potential entry points for attackers, thereby reducing the attack surface. For example, avoiding the installation of unnecessary packages and services reduces the number of vulnerabilities that could be exploited.

2. **Improved Security Posture**: Best practices such as using non-root users, securing sensitive information, and keeping software up-to-date help in maintaining a strong security posture. This reduces the risk of common vulnerabilities being exploited.

3. **Consistency and Compliance**: Following established best practices ensures consistency across different environments and aligns with compliance requirements. This is particularly important in regulated industries where adherence to security standards is mandatory.

4. **Efficient Resource Management**: Best practices often lead to more efficient use of resources. For instance, using multi-stage builds can reduce the size of the final Docker image, leading to faster deployment and lower storage costs.

Recent real-world examples, such as the exploitation of vulnerabilities in Docker images used in cloud environments (CVE-2021-21366), highlight the importance of following security best practices. By doing so, organizations can mitigate risks and protect their applications and infrastructure from potential threats.

**Q5. How does DefectDojo handle duplicate vulnerabilities found by different scanning tools?**

DefectDojo handles duplicate vulnerabilities found by different scanning tools through its automatic deduplication feature. When multiple scanning tools identify the same vulnerability, DefectDojo consolidates these findings into a single record, preventing redundancy and ensuring that each issue is addressed only once. This feature is particularly useful in environments where multiple scanning tools are used, as it streamlines the vulnerability management process.

For example, if both Trivy and another scanning tool like Clair identify the same vulnerability in a Docker image, DefectDojo will consolidate these findings into a single entry. This consolidation is based on various attributes such as the CVE ID, CWE ID, and other metadata associated with the vulnerability.

By handling duplicates automatically, DefectDojo helps security teams focus on addressing unique vulnerabilities rather than dealing with redundant entries, thus improving efficiency and effectiveness in managing security risks.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Automate Uploading Image Scanning Results in DefectDojo/05-Image Scanning and Reporting in DevSecOps|Image Scanning and Reporting in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Automate Uploading Image Scanning Results in DefectDojo/00-Overview|Overview]]
