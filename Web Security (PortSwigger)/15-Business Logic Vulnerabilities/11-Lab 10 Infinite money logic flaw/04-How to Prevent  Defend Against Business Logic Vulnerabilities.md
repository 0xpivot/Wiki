---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against Business Logic Vulnerabilities

### Detection

Detecting business logic vulnerabilities requires thorough testing and analysis of the application’s business rules and processes. Automated tools and manual testing can help identify potential issues.

#### Automated Tools

- **Static Application Security Testing (SAST)**: Tools like SonarQube and Fortify can analyze the codebase for potential business logic flaws.
- **Dynamic Application Security Testing (DAST)**: Tools like Burp Suite and OWASP ZAP can simulate attacks and identify vulnerabilities during runtime.

#### Manual Testing

- **Penetration Testing**: Engage security experts to manually test the application and identify business logic vulnerabilities.
- **Code Reviews**: Regularly review the codebase to ensure that business rules are properly enforced.

### Prevention

Preventing business logic vulnerabilities involves implementing robust validation and enforcement mechanisms.

#### Secure Coding Practices

- **Input Validation**: Ensure that all inputs are validated against expected formats and ranges.
- **Access Control**: Implement proper access control mechanisms to restrict unauthorized actions.
- **Rate Limiting**: Limit the frequency of certain actions to prevent abuse.

#### Example: Secure Code Implementation

Here’s an example of how to implement secure coding practices to prevent an infinite money logic flaw:

```python
def transfer_funds(from_account_id, to_account_id, amount):
    from_account = get_account(from_account_id)
    to_account = get_account(to_account_id)
    
    if from_account.balance < amount:
        raise ValueError("Insufficient balance")
    
    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer funds to the same account")
    
    from_account.balance -= amount
    to_account.balance += amount
    
    save_accounts(from_account, to_account)
```

### Comparison: Vulnerable vs. Secure Code

#### Vulnerable Code

```python
def transfer_funds(from_account_id, to_account_id, amount):
    from_account = get_account(from_account_id)
    to_account = get_account(to_account_id)
    
    from_account.balance -= amount
    to_account.balance += amount
    
    save_accounts(from_account, to_account)
```

#### Secure Code

```python
def transfer_funds(from_account_id, to_account_id, amount):
    from_account = get_account(from_account_id)
    to_account = get_account(to_account_id)
    
    if from_account.balance < amount:
        raise ValueError("Insufficient balance")
    
    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer funds to the same account")
    
    from_account.balance -= amount
    to_account.balance += amount
    
    save_accounts(from_account, to_account)
```

### Configuration Hardening

Hardening the application’s configuration can further mitigate business logic vulnerabilities.

#### Example: Rate Limiting Configuration

```json
{
    "rate_limiting": {
        "transfer_funds": {
            "max_requests_per_minute": 10,
            "max_requests_per_hour": 100
        }
    }
}
```

### Conclusion

Business logic vulnerabilities are a critical concern for web applications. By understanding the nature of these vulnerabilities, detecting them through thorough testing, and implementing secure coding practices, you can significantly reduce the risk of exploitation. Always ensure that your application’s business rules are properly enforced to maintain the integrity and security of your system.

### Practice Labs

For hands-on practice with business logic vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security vulnerabilities, including business logic flaws.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning and testing security concepts.

These labs provide practical experience in identifying and mitigating business logic vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/00-Overview|Overview]] | [[05-Main Method Implementation|Main Method Implementation]]
