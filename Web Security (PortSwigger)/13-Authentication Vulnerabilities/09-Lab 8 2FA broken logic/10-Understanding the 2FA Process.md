---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Understanding the 2FA Process

Before diving into the exploitation, it's essential to understand how the 2FA process typically works.

### Typical 2FA Workflow

1. **User Authentication**: The user provides their username and password.
2. **2FA Request**: Upon successful initial authentication, the system sends a 2FA request to the user's registered device (e.g., mobile phone).
3. **2FA Verification**: The user receives a one-time password (OTP) via SMS, email, or an authenticator app. They enter this OTP into the system.
4. **Access Granted**: If the OTP is valid, the user gains access to the system.

### Common Flaws in 2FA Logic

Despite the added security provided by 2FA, several flaws can render it ineffective:

1. **Timing Attacks**: If the system does not properly handle timing between the initial authentication and the 2FA request, attackers can exploit this delay.
2. **Logic Errors**: Flaws in the logic that governs the 2FA process can allow attackers to bypass the second factor.
3. **Implementation Weaknesses**: Poorly implemented 2FA systems may have vulnerabilities that can be exploited.

### Real-World Example: CVE-2021-3129

CVE-2021-3129 is a real-world example of a 2FA vulnerability. In this case, a flaw in the 2FA implementation of a popular cryptocurrency exchange allowed attackers to bypass 2FA and steal funds. The vulnerability was due to a logic error in the 2FA process, which allowed attackers to reset the 2FA token without proper validation.

---
<!-- nav -->
[[09-Understanding Two-Factor Authentication (2FA)|Understanding Two-Factor Authentication (2FA)]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/00-Overview|Overview]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/11-Conclusion|Conclusion]]
