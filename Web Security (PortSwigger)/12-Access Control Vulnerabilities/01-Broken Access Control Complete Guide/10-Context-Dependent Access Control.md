---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Context-Dependent Access Control

### Introduction

Context-dependent access control is a critical aspect of web security that ensures users can only perform actions within the correct sequence and state of the application. This type of access control is particularly important in applications that involve multi-step processes, such as user deletion or online transactions. By enforcing proper sequencing and state management, context-dependent access control helps prevent unauthorized actions and maintains the integrity of the application.

### What is Context-Dependent Access Control?

Context-dependent access control is a mechanism that restricts access to certain functionalities based on the current state of the application or the user's interaction with it. This type of access control is essential in scenarios where actions must be performed in a specific order to ensure security and correctness.

#### Example: Multi-Step User Deletion Process

Consider a scenario where a user wants to delete another user account. The process typically involves the following steps:

1. **Initiate Deletion Request**: The user clicks on a "Delete" button, which sends a request to the backend server.
2. **Confirmation Step**: The server responds with a confirmation prompt, asking the user to verify their intention to delete the account.
3. **Finalize Deletion**: Upon confirmation, the user clicks on a "Yes" button, which triggers a final request to the server to delete the account.

In this example, context-dependent access control ensures that the user cannot proceed to the final deletion step without first confirming their intention. This prevents accidental deletions and ensures that the deletion process is properly sequenced.

### Why is Context-Dependent Access Control Important?

Context-dependent access control is crucial for several reasons:

1. **Prevents Unauthorized Actions**: By enforcing proper sequencing, context-dependent access control prevents users from performing actions out of order, which could lead to unintended consequences.
2. **Maintains Application Integrity**: Ensures that the application remains in a consistent state by preventing users from bypassing necessary steps.
3. **Enhances Security**: Helps protect against malicious actions by ensuring that users follow the intended workflow.

### How Does Context-Dependent Access Control Work?

Context-dependent access control works by maintaining the state of the application and verifying that each action is performed in the correct sequence. This is typically achieved through server-side logic that tracks the state of the user's interaction and enforces rules based on that state.

#### Example: State Management in User Deletion

Let's consider the multi-step user deletion process again. Here’s how the state management might work:

1. **Initial Request**: When the user clicks the "Delete" button, the server receives a request and sets the state to `INITIAL_REQUEST`.
2. **Confirmation Prompt**: The server responds with a confirmation prompt and sets the state to `CONFIRMATION_REQUESTED`.
3. **Final Deletion**: When the user confirms the deletion, the server checks the state. If the state is `CONFIRMATION_REQUESTED`, the server proceeds with the deletion and sets the state to `DELETION_COMPLETED`.

This state management ensures that the user cannot skip the confirmation step and directly delete the account.

### Real-World Examples

#### Retail Website Scenario

Consider a retail website where users can add items to their shopping cart and proceed to checkout. Once the order is confirmed and payment is made, the shopping cart should be locked to prevent further modifications. However, if there are access control vulnerabilities, users might be able to modify the cart even after the order is confirmed.

##### Vulnerability Scenario

Suppose a user buys an item for $1, confirms the order, and makes the payment. Due to a vulnerability, the user can still modify the shopping cart and add high-value items worth $100,000. This would result in significant financial loss for the retailer.

##### Real-World Breach Example

A similar issue was observed in a real-world breach involving a retail website. In this case, attackers exploited a vulnerability in the access control mechanism, allowing them to modify orders after they were confirmed. This resulted in significant financial losses for the retailer.

### Implementation Details

To implement context-dependent access control effectively, developers need to manage the state of the application and enforce rules based on that state. This can be achieved using various techniques, including session management, tokens, and server-side validation.

#### Example Code: Multi-Step User Deletion

Here’s an example implementation of a multi-step user deletion process using Python and Flask:

```python
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/delete_user', methods=['POST'])
def initiate_deletion():
    user_id = request.form['user_id']
    session['deletion_state'] = 'INITIAL_REQUEST'
    session['user_id'] = user_id
    return "Deletion initiated. Please confirm."

@app.route('/confirm_deletion', methods=['POST'])
def confirm_deletion():
    if session.get('deletion_state') == 'INITIAL_REQUEST':
        session['deletion_state'] = 'CONFIRMATION_REQUESTED'
        return "Deletion confirmed. Finalize deletion."
    else:
        return "Invalid state transition."

@app.route('/finalize_deletion', methods=['POST'])
def finalize_deletion():
    if session.get('deletion_state') == 'CONFIRMATION_REQUESTED':
        user_id = session.get('user_id')
        # Perform deletion logic here
        return f"User {user_id} deleted successfully."
    else:
        return "Invalid state transition."

if __name__ == '__main__':
    app.run(debug=True)
```

### Pitfalls and Common Mistakes

Developers often make several common mistakes when implementing context-dependent access control:

1. **Insufficient State Management**: Failing to properly track and manage the state of the application can lead to vulnerabilities.
2. **Client-Side Validation Only**: Relying solely on client-side validation can be easily bypassed by attackers.
3. **Inconsistent State Transitions**: Allowing inconsistent state transitions can lead to unauthorized actions.

### How to Prevent / Defend

#### Detection

To detect context-dependent access control vulnerabilities, organizations can use automated tools and manual testing:

1. **Automated Tools**: Tools like Burp Suite, OWASP ZAP, and others can help identify potential vulnerabilities.
2. **Manual Testing**: Conduct thorough manual testing to simulate different scenarios and check for improper state transitions.

#### Prevention

To prevent context-dependent access control vulnerabilities, follow these best practices:

1. **Server-Side Validation**: Always validate state transitions on the server side to ensure proper sequencing.
2. **Use Tokens**: Utilize tokens to manage state and prevent tampering.
3. **Audit Logs**: Maintain audit logs to track user actions and detect anomalies.

#### Secure Coding Fixes

Here’s an example of a vulnerable code and its secure counterpart:

**Vulnerable Code:**

```python
@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    # Directly delete the user without any state management
    # Perform deletion logic here
    return f"User {user_id} deleted successfully."
```

**Secure Code:**

```python
@app.route('/delete_user', methods=['POST'])
def initiate_deletion():
    user_id = request.form['user_id']
    session['deletion_state'] = 'INITIAL_REQUEST'
    session['user_id'] = user_id
    return "Deletion initiated. Please confirm."

@app.route('/confirm_deletion', methods=['POST'])
def confirm_deletion():
    if session.get('deletion_state') == 'INITIAL_REQUEST':
        session['deletion_state'] = 'CONFIRMATION_REQUESTED'
        return "Deletion confirmed. Finalize deletion."
    else:
        return "Invalid state transition."

@app.route('/finalize_deletion', methods=['POST'])
def finalize_deletion():
    if session.get('deletion_state') == 'CONFIRMATION_REQUESTED':
        user_id = session.get('user_id')
        # Perform deletion logic here
        return f"User {user_id} deleted successfully."
    else:
        return "Invalid state transition."
```

### Configuration Hardening

To harden the configuration and prevent context-dependent access control vulnerabilities, consider the following:

1. **Session Management**: Ensure proper session management to prevent session hijacking.
2. **Token-Based Authentication**: Use token-based authentication mechanisms to manage state securely.
3. **Regular Audits**: Conduct regular audits to ensure compliance with security policies.

### Conclusion

Context-dependent access control is a vital component of web security that ensures proper sequencing and state management in multi-step processes. By understanding the principles and implementing best practices, developers can prevent unauthorized actions and maintain the integrity of their applications.

### Practice Labs

For hands-on practice with context-dependent access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on access control vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security concepts, including access control.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing and security assessments.

By engaging with these labs, you can gain practical experience in identifying and mitigating context-dependent access control vulnerabilities.

---
<!-- nav -->
[[09-Confidentiality, Integrity, and Availability|Confidentiality, Integrity, and Availability]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[11-Denied by Default Design|Denied by Default Design]]
