---
course: DevSecOps
topic: Understanding DevSecOps Concepts
tags: [devsecops]
---

## Understanding DevSecOps Concepts

### Introduction to DevSecOps

DevSecOps is a methodology that integrates security practices into the DevOps lifecycle. This approach ensures that security is not an afterthought but is embedded throughout the development, testing, and deployment processes. The DevSecOps Manifesto, inspired by the Agile Manifesto, outlines key principles that guide the integration of security into the DevOps culture.

### The DevSecOps Manifesto

The DevSecOps Manifesto consists of nine items that emphasize the importance of integrating security into the DevOps workflow. Each item is structured similarly to the Agile Manifesto, with a preferred value on the left and a less desirable value on the right. Let's delve into each of these items in detail.

#### 1. Leaning In Over Always Saying No

**What:**
Leaning in refers to actively participating in the development process and contributing to solutions rather than simply rejecting ideas due to security concerns.

**Why:**
Security practitioners often face the stereotype of being the "no-sayers." By leaning in, security professionals can become integral members of the development team, helping to create secure solutions rather than blocking progress.

**How:**
To lean in, security professionals should:
- Engage in regular communication with developers.
- Provide constructive feedback and alternative solutions.
- Participate in code reviews and design discussions.

**Real-World Example:**
In the Equifax breach (CVE-2017-5638), security teams were initially hesitant to approve certain changes. However, had they leaned in and collaborated more closely with the development team, they might have identified vulnerabilities earlier and prevented the breach.

**How to Prevent / Defend:**
- **Detection:** Regularly review logs and monitor for suspicious activities.
- **Prevention:** Implement automated security checks in the CI/CD pipeline.
- **Secure Coding Fix:**
  ```python
  # Vulnerable Code
  def login(user, password):
      if user == 'admin' and password == 'password':
          return True
      else:
          return False

  # Secure Code
  def login(user, password):
      if user == 'admin' and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
          return True
      else:
          return False
  ```

#### 2. Data and Security Signs Over Fear, Uncertainty, and Doubt (FUD)

**What:**
Data-driven decision-making is preferred over making decisions based on fear, uncertainty, and doubt.

**Why:**
Using data to substantiate actions and remediation plans is more effective than relying on emotional responses. Data provides a clear, objective basis for decision-making.

**How:**
To leverage data effectively:
- Collect and analyze security metrics.
- Use data to identify trends and patterns.
- Make informed decisions based on evidence.

**Real-World Example:**
In the Capital One breach (CVE-2019-11510), the lack of proper data analysis led to the exposure of sensitive customer information. Had the organization relied more on data-driven insights, they might have detected the vulnerability earlier.

**How to Prevent / Defend:**
- **Detection:** Implement continuous monitoring tools like SIEM.
- **Prevention:** Use data analytics to identify anomalies.
- **Secure Coding Fix:**
  ```python
  # Vulnerable Code
  def get_user_data(user_id):
      return db.execute(f"SELECT * FROM users WHERE id = {user_id}")

  # Secure Code
  def get_user_data(user_id):
      return db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
  ```

#### 3. Open Contribution and Collaboration Over Security-Only Requirements

**What:**
Open contribution and collaboration involve transparency and a holistic view of the project, rather than focusing solely on security requirements.

**Why:**
Transparency fosters trust and encourages collaboration among team members. A holistic view ensures that all aspects of the project are considered, not just security.

**How:**
To promote open contribution and collaboration:
- Encourage cross-functional teams.
- Share security knowledge and best practices.
- Foster a culture of openness and inclusivity.

**Real-World Example:**
In the SolarWinds supply chain attack (CVE-2020-1014), the lack of open collaboration between vendors and customers contributed to the widespread impact. Had there been more transparency and collaboration, the attack might have been detected earlier.

**How to Prevent / Defend:**
- **Detection:** Implement supply chain security measures.
- **Prevention:** Conduct regular security audits and assessments.
- **Secure Coding Fix:**
  ```python
  # Vulnerable Code
  def download_file(url):
      response = requests.get(url)
      with open('file.txt', 'wb') as f:
          f.write(response.content)

  # Secure Code
  def download_file(url):
      response = requests.get(url, verify=True)
      with open('file.txt', 'wb') as f:
          f.write(response.content)
  ```

#### 4. Consumable Security Services with APIs Over Mandated Security Controls and Paperwork

**What:**
Consumable security services with APIs are preferred over mandated security controls and paperwork.

**Why:**
APIs enable seamless integration of security services into the development process, reducing the need for manual intervention and paperwork.

**How:**
To implement consumable security services:
- Use APIs to automate security checks.
- Integrate security services into the CI/CD pipeline.
- Ensure that security services are easily accessible and usable.

**Real-World Example:**
In the Uber breach (CVE-2016-10001), the lack of automated security checks and reliance on manual processes contributed to the exposure of sensitive data. Had Uber implemented consumable security services with APIs, they might have detected the vulnerability earlier.

**How to Prevent / Defend:**
- **Detection:** Implement automated security scanning tools.
- **Prevention:** Use APIs to integrate security services into the CI/CD pipeline.
- **Secure Coding Fix:**
  ```python
  # Vulnerable Code
  def upload_file(file):
      with open('uploaded_file.txt', 'wb') as f:
          f.write(file.read())

  # Secure Code
  def upload_file(file):
      with open('uploaded_file.txt', 'wb') as f:
          f.write(file.read())
      scan_file('uploaded_file.txt')
  ```

### Conclusion

The DevSecOps Manifesto emphasizes the importance of integrating security into the DevOps workflow. By leaning in, using data-driven decision-making, promoting open collaboration, and leveraging consumable security services with APIs, organizations can create a more secure and efficient development process. Real-world examples and secure coding practices further illustrate the practical application of these principles.

### Practice Labs

For hands-on experience with DevSecOps concepts, consider the following labs:
- **PortSwigger Web Security Academy**: Focuses on web application security and includes various challenges and labs.
- **OWASP Juice Shop**: An intentionally insecure web application for practicing security testing and ethical hacking.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for security testing purposes.
- **WebGoat**: An interactive, gamified training application for learning web security.

These labs provide practical experience in applying DevSecOps principles and techniques.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/The DevSecOps Manifesto/01-Introduction to DevSecOps Concepts|Introduction to DevSecOps Concepts]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/The DevSecOps Manifesto/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/The DevSecOps Manifesto/03-247 Proactive Security Monitoring Over Reacting After Being Informed of an Incident|247 Proactive Security Monitoring Over Reacting After Being Informed of an Incident]]
