---
course: DevSecOps
topic: Getting Started with the DevSecOps Bootcamp
tags: [devsecops]
---

## Security Essentials for DevSecOps

### Introduction to Security Basics

Security is a critical aspect of modern software development, especially in the context of DevSecOps. DevSecOps integrates security practices into the software development lifecycle, ensuring that applications are secure from the initial design phase through deployment and maintenance. This chapter serves as an essential foundation for anyone starting their journey into DevSecOps, regardless of their prior security experience.

#### Importance of Security Basics

Understanding the fundamentals of security is crucial because it provides a solid base upon which more advanced security concepts can be built. Without a strong grasp of basic security principles, developers may overlook critical vulnerabilities that could be exploited by attackers. This chapter aims to fill any knowledge gaps and ensure that all participants have a comprehensive understanding of the core security concepts necessary for effective DevSecOps.

### Open Source Security Foundation (OSF) Top 10 Categories

The Open Source Security Foundation (OSF) is a non-profit organization dedicated to improving the security of open-source software. One of their key contributions is the OSF Top 10 list, which identifies the most critical security risks faced by web applications. These categories serve as a guideline for application security and are widely recognized in the industry.

#### Detailed Explanation of Each Category

1. **Injection**
   - **What:** Injection flaws occur when untrusted data is sent as part of a command or query. The attacker’s hostile data can trick the interpreter into executing unintended commands or accessing unauthorized data.
   - **Why:** Injection attacks are among the most dangerous because they can lead to complete system compromise. Common types include SQL injection, command injection, and LDAP injection.
   - **How:** Attackers inject malicious data into input fields, which are then processed by the application. For example, in SQL injection, an attacker might insert a SQL command into a form field to manipulate the database.
   - **Real-World Example:** CVE-2019-11510 was a SQL injection vulnerability in WordPress plugins that allowed attackers to execute arbitrary SQL commands.
   - **How to Prevent / Defend:**
     - **Detection:** Use static and dynamic analysis tools to identify potential injection points.
     - **Prevention:** Use parameterized queries and prepared statements.
     - **Secure Coding Fix:**
       ```sql
       -- Vulnerable Code
       $query = "SELECT * FROM users WHERE username = '" . $_GET['username'] . "'";

       -- Secure Code
       $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username');
       $stmt->execute(['username' => $_GET['username']]);
       ```

2. **Broken Authentication**
   - **What:** Broken authentication occurs when authentication mechanisms are implemented incorrectly, allowing attackers to compromise passwords, keys, or session tokens, or to exploit other implementation flaws to assume other users’ identities.
   - **Why:** Weak authentication mechanisms can lead to unauthorized access to sensitive data and systems.
   - **How:** Attackers can exploit weak password policies, insecure session management, or flawed multi-factor authentication implementations.
   - **Real-World Example:** The Equifax breach in 2017 was partly due to broken authentication, where attackers exploited a vulnerability in Apache Struts to gain access to sensitive data.
   - **How to Prevent / Defend:**
     - **Detection:** Regularly audit authentication mechanisms using penetration testing and vulnerability scanners.
     - **Prevention:** Implement strong password policies, use multi-factor authentication, and secure session management.
     - **Secure Coding Fix:**
       ```python
       # Vulnerable Code
       if user_password == stored_password:
           session['authenticated'] = True

       # Secure Code
       if bcrypt.checkpw(user_password.encode('utf-8'), stored_password):
           session['authenticated'] = True
       ```

3. **Sensitive Data Exposure**
   - **What:** Sensitive data exposure occurs when sensitive data is not properly protected, leading to unauthorized access or disclosure.
   - **Why:** Exposed sensitive data can be used for identity theft, financial fraud, and other malicious activities.
   - **How:** Attackers can exploit weak encryption, lack of proper access controls, or misconfigured storage to access sensitive data.
   - **Real-World Example:** The Capital One breach in 2019 exposed sensitive data due to misconfigured cloud storage settings.
   - **How to Prevent / Defend:**
     - **Detection:** Use data loss prevention (DLP) tools to monitor and control sensitive data.
     - **Prevention:** Encrypt sensitive data both in transit and at rest, implement strict access controls, and regularly audit data storage configurations.
     - **Secure Coding Fix:**
       ```python
       # Vulnerable Code
       data = {'credit_card': '1234567890123456'}
       return jsonify(data)

       # Secure Code
       data = {'credit_card': encrypt('1234567890123456')}
       return jsonify(data)
       ```

4. **XML External Entities (XXE)**
   - **What:** XML External Entities (XXE) occur when an application processes XML input without validating it, allowing attackers to exploit the XML parser to read local files, execute remote code, or cause denial of service.
   - **Why:** XXE attacks can lead to data exfiltration, remote code execution, and denial of service.
   - **How:** Attackers can inject malicious XML entities into input fields, which are then processed by the application.
   - **Real-World Example:** The Equifax breach in 2017 also involved an XXE vulnerability in Apache Struts.
   - **How to Prevent / Defend:**
     - **Detection:** Use static and dynamic analysis tools to identify potential XXE vulnerabilities.
     - **Prevention:** Disable external entity processing in XML parsers, validate XML input, and use secure XML libraries.
     - **Secure Coding Fix:**
       ```xml
       <!-- Vulnerable Code -->
       <root>
         <!ENTITY xxe SYSTEM "file:///etc/passwd">
         <data>&xxe;</data>
       </root>

       <!-- Secure Code -->
       <root>
         <data>Safe data</data>
       </root>
       ```

5. **Broken Access Control**
   - **What:** Broken access control occurs when an application fails to enforce proper access restrictions, allowing unauthorized users to access sensitive functionality or data.
   - **Why:** Weak access control can lead to unauthorized access to sensitive data and systems.
   - **How:** Attackers can exploit weak role-based access control (RBAC) implementations, lack of proper authorization checks, or misconfigured permissions.
   - **Real-World Example:** The Uber breach in 2016 was partly due to broken access control, where attackers gained access to sensitive data due to misconfigured permissions.
   - **How to Prevent / Defend:**
     - **Detection:** Regularly audit access control mechanisms using penetration testing and vulnerability scanners.
     - **Prevention:** Implement strong RBAC, use least privilege principles, and regularly review and update access control configurations.
     - **Secure Coding Fix:**
       ```python
       # Vulnerable Code
       if user_role == 'admin':
           return render_template('admin.html')

       # Secure Code
       if current_user.is_admin():
           return render_template('admin.html')
       ```

6. **Security Misconfiguration**
   - **What:** Security misconfiguration occurs when an application or environment is not properly configured, leaving it vulnerable to attacks.
   - **Why:** Misconfigured environments can be easily exploited by attackers to gain unauthorized access or perform malicious activities.
   - **How:** Attackers can exploit default credentials, misconfigured firewalls, or insecure default settings to gain access to sensitive data and systems.
   - **Real-World Example:** The Capital One breach in 2019 was partly due to security misconfiguration, where misconfigured cloud storage settings allowed unauthorized access.
   - **How to Prevent / Defend:**
     - **Detection:** Regularly audit security configurations using vulnerability scanners and penetration testing.
     - **Prevention:** Follow secure configuration guidelines, disable unnecessary services, and regularly review and update security configurations.
     - **Secure Coding Fix:**
       ```bash
       # Vulnerable Configuration
       sudo apt-get install apache2
       sudo systemctl enable apache2

       # Secure Configuration
       sudo apt-get install apache2
       sudo systemctl enable apache2
       sudo ufw allow 'Apache Full'
       ```

7. **Cross-Site Scripting (XSS)**
   - **What:** Cross-Site Scripting (XSS) occurs when an application includes untrusted data in a web page without proper validation or escaping, allowing attackers to inject malicious scripts into the page.
   - **Why:** XSS attacks can lead to data theft, session hijacking, and other malicious activities.
   - **How:** Attackers can inject malicious scripts into input fields, which are then executed by the browser.
   - **Real-World Example:** The Facebook XSS bug in 2019 allowed attackers to inject malicious scripts into user profiles.
   - **How to Prevent / Defend:**
     - **Detection:** Use static and dynamic analysis tools to identify potential XSS vulnerabilities.
     - **Prevention:** Validate and escape user input, use Content Security Policy (CSP), and implement secure coding practices.
     - **Secure Coding Fix:**
       ```html
       <!-- Vulnerable Code -->
       <div>{{ user_input }}</div>

       <!-- Secure Code -->
       <div>{{ escape(user_input) }}</div>
       ```

8. **Insecure Deserialization**
   - **What:** Insecure deserialization occurs when an application deserializes untrusted data without proper validation, allowing attackers to execute arbitrary code or perform other malicious activities.
   - **Why:** Insecure deserialization can lead to remote code execution, data theft, and other malicious activities.
   - **How:** Attackers can inject malicious serialized objects into input fields, which are then deserialized by the application.
   - **Real-World Example:** The Apache Struts vulnerability in 2017 allowed attackers to execute arbitrary code due to insecure deserialization.
   - **How to Prevent / Defend:**
     - **Detection:** Use static and dynamic analysis tools to identify potential insecure deserialization vulnerabilities.
     - **Prevention:** Validate and sanitize serialized data, use secure serialization libraries, and implement secure coding practices.
     - **Secure Coding Fix:**
       ```java
       // Vulnerable Code
       ObjectInputStream ois = new ObjectInputStream(new FileInputStream("data.ser"));
       Object obj = ois.readObject();

       // Secure Code
       ObjectInputStream ois = new ObjectInputStream(new FileInputStream("data.ser")) {
           @Override
           protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
               if (!desc.getName().startsWith("com.example")) {
                   throw new InvalidClassException("Unauthorized deserialization attempt", desc.getName());
               }
               return super.resolveClass(desc);
           }
       };
       Object obj = ois.readObject();
       ```

9. **Using Components with Known Vulnerabilities**
   - **What:** Using components with known vulnerabilities occurs when an application uses outdated or vulnerable third-party components, libraries, or frameworks.
   - **Why:** Outdated components can be easily exploited by attackers to gain unauthorized access or perform malicious activities.
   - **How:** Attackers can exploit known vulnerabilities in third-party components to gain access to sensitive data and systems.
   - **Real-World Example:** The Equifax breach in 22017 was partly due to using an outdated version of Apache Struts.
   - **How to Prevent / Defend:**
     - **Detection:** Regularly audit third-party components using vulnerability scanners and dependency checkers.
     - **Prevention:** Keep third-party components up-to-date, use secure component management practices, and regularly review and update component configurations.
     - **Secure Coding Fix:**
       ```bash
       # Vulnerable Component
       sudo apt-get install struts=2.3.15.1

       # Secure Component
       sudo apt-get install struts=2.5.20
       ```

10. **Insufficient Logging & Monitoring**
    - **What:** Insufficient logging & monitoring occurs when an application does not log or monitor security events properly, making it difficult to detect and respond to security incidents.
    - **Why:** Lack of proper logging and monitoring can make it difficult to detect and respond to security incidents.
    - **How:** Attackers can exploit insufficient logging and monitoring to hide their activities and evade detection.
    - **Real-World Example:** The Target breach in 2013 was partly due to insufficient logging and monitoring, where attackers were able to hide their activities.
    - **How to Prevent / Defend:**
      - **Detection:** Regularly audit logging and monitoring configurations using vulnerability scanners and penetration testing.
      - **Prevention:** Implement proper logging and monitoring practices, use centralized logging and monitoring tools, and regularly review and update logging and monitoring configurations.
      - **Secure Coding Fix:**
        ```bash
        # Vulnerable Logging
        sudo apt-get install rsyslog

        # Secure Logging
        sudo apt-get install rsyslog
        sudo systemctl enable rsyslog
        sudo systemctl start rsyslog
        ```

### Different Security Risks at Different Levels of the Application

Security risks can occur at various levels of the application, including the application code itself, the runtime environment, and the underlying infrastructure. Understanding these different levels is crucial for implementing effective security measures.

#### Application Code Level

At the application code level, security risks include:

- **SQL Injection**: Occurs when an attacker injects malicious SQL code into input fields, which are then executed by the database.
- **Path Traversal**: Occurs when an attacker manipulates file paths to access unauthorized files or directories.
- **Cross-Site Scripting (XSS)**: Occurs when an attacker injects malicious scripts into web pages, which are then executed by the browser.
- **Client-Side Request Forgery (CSRF)**: Occurs when an attacker tricks a user into performing unintended actions on a web application.

#### Runtime Environment Level

At the runtime environment level, security risks include:

- **Insecure Deserialization**: Occurs when an application deserializes untrusted data without proper validation, allowing attackers to execute arbitrary code.
- **Broken Authentication**: Occurs when authentication mechanisms are implemented incorrectly, allowing attackers to compromise passwords, keys, or session tokens.
- **Security Misconfiguration**: Occurs when an application or environment is not properly configured, leaving it vulnerable to attacks.

#### Infrastructure Level

At the infrastructure level, security risks include:

- **Denial of Service (DoS)**: Occurs when an attacker floods a network or server with traffic, causing it to become unavailable.
- **Man-in-the-Middle (MitM)**: Occurs when an attacker intercepts and modifies communication between two parties.
- **Network Intrusion**: Occurs when an attacker gains unauthorized access to a network and performs malicious activities.

### Conclusion

This chapter has provided a comprehensive overview of the essential security concepts and risks that are critical for DevSecOps. By understanding these concepts and implementing effective security measures, developers can ensure that their applications are secure from the initial design phase through deployment and maintenance.

### Practice Labs

To further enhance your understanding and practical skills in DevSecOps, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application to practice web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is extremely vulnerable to common flaws.
- **WebGoat**: An interactive, gamified web application security training tool.

These labs provide hands-on experience with real-world security challenges and help reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[10-Introduction to Kubernetes Platform Security|Introduction to Kubernetes Platform Security]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/00-Overview|Overview]] | [[12-Understanding Fundamental Concepts in DevSecOps|Understanding Fundamental Concepts in DevSecOps]]
