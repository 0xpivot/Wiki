---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Social Engineering Attacks

### What is Social Engineering?

Social engineering is a non-technical method used by attackers to manipulate individuals into divulging confidential information or performing actions that benefit the attacker. This type of attack exploits human psychology rather than technical vulnerabilities. Social engineering attacks are often successful because they rely on the trust and goodwill of the victim, making them particularly insidious.

### Why Social Engineering Works

Social engineering works because humans are inherently trusting and cooperative. Attackers exploit this trust by posing as someone the victim knows or trusts, such as an IT specialist, a colleague, or even a customer service representative. The goal is to convince the victim to reveal sensitive information or perform actions that compromise security.

### How Social Engineering Works

Social engineering attacks typically follow a series of steps:

1. **Research**: The attacker gathers information about the target organization and its employees. This can be done through social media, public records, or other sources.
2. **Engagement**: The attacker establishes contact with the target, often via email, phone, or in-person interactions. They may pose as a trusted individual or entity.
3. **Exploitation**: Once trust is established, the attacker manipulates the target into revealing sensitive information or performing actions that benefit the attacker.

### Real-World Example: Twitter Hack

In July 2020, Twitter suffered a significant social engineering attack. Hackers posed as the company's IT department specialists and contacted several remote workers. They asked for their work account credentials, which the employees willingly provided. Using these credentials, the attackers gained access to Twitter's administrator tools.

#### Administrator Access

Administrator access to Twitter means having the ability to manage and control various aspects of the platform, including user accounts. With this level of access, the attackers could:

- Reset Twitter accounts for several dozen famous Twitter users and public figures.
- Stage fake Bitcoin giveaways from these accounts.

The attack was notable for its simplicity. No fancy hacking tools were required; the attackers simply needed a few employee credentials that were voluntarily handed over.

### Real-World Example: Yahoo Breach

In 2013, Yahoo experienced a massive data breach due to a social engineering attack. A hacker conducted a phishing campaign specifically targeted at Yahoo's employees. By gaining access to Yahoo's user database and account management tools, the hacker obtained over 500 million user accounts and their personal information, including emails, passwords, phone numbers, and dates of birth.

#### Impact of the Breach

The day after the attack, Yahoo's stock price dropped significantly. Additionally, Yahoo had to pay over $100 million in legal expenses, penalties, and security measures to remediate the damage caused by the breach.

### Common Social Engineering Tactics

1. **Phishing**: Sending fraudulent emails or messages that appear to come from a legitimate source, often asking for sensitive information.
2. **Pretexting**: Creating a fabricated scenario to trick the victim into providing sensitive information.
3. **Baiting**: Offering something enticing to the victim in exchange for sensitive information.
4. **Quid Pro Quo**: Offering something in return for sensitive information, often under the guise of a reward or compensation.

### How to Prevent / Defend Against Social Engineering Attacks

#### Detection

1. **Employee Training**: Regularly train employees on recognizing and responding to social engineering attempts.
2. **Security Awareness Programs**: Implement programs that educate employees about the risks and signs of social engineering attacks.
3. **Monitoring Tools**: Use monitoring tools to detect unusual activity or patterns that may indicate a social engineering attack.

#### Prevention

1. **Multi-Factor Authentication (MFA)**: Require multi-factor authentication for accessing sensitive systems and data.
2. **Strong Password Policies**: Enforce strong password policies and regular password changes.
3. **Access Controls**: Limit access to sensitive systems and data to only those who require it for their job functions.

#### Secure Coding Fixes

**Vulnerable Code Example**

```python
def authenticate_user(username, password):
    if username == "admin" and password == "password":
        return True
    else:
        return False
```

**Secure Code Example**

```python
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    stored_hash = get_stored_hash_for_username(username)
    input_hash = hash_password(password)
    if stored_hash == input_hash:
        return True
    else:
        return False
```

#### Configuration Hardening

**Example Nginx Configuration**

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

**Explanation**

- `auth_basic`: Enables HTTP Basic Authentication.
- `auth_basic_user_file`: Specifies the path to the file containing the usernames and hashed passwords.

### Practice Labs

For hands-on experience with social engineering attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on social engineering and phishing.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various types of attacks, including social engineering.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for testing and learning purposes.

By understanding the principles and mechanisms behind social engineering attacks, organizations can better protect themselves against these threats. Regular training, strong security policies, and robust technical controls are essential for mitigating the risks associated with social engineering.

---
<!-- nav -->
[[11-Session ID and Token Revocation|Session ID and Token Revocation]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[13-Social Engineering Attacks|Social Engineering Attacks]]
