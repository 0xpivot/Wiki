---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why a brute force attack on a 2FA system is possible in this scenario.**

The brute force attack is possible due to the lack of effective lockout mechanisms after multiple failed attempts. Although the application logs out the user after two incorrect attempts, this does not prevent an attacker from automating the process of logging in and attempting two more codes repeatedly. Additionally, the 2FA code is a four-digit number, making it feasible to brute force within a reasonable timeframe.

**Q2. How would you configure Burp Suite to perform a brute force attack on a 2FA code?**

To configure Burp Suite for a brute force attack on a 2FA code:

1. **Set Up Macro**: 
   - Go to `Settings` > `Sessions`.
   - Click `Add` and set the scope to include all URLs.
   - Add a macro that includes the sequence of requests needed to log in and generate a new 2FA token.
   
2. **Configure Intruder**:
   - Send the POST request with the 2FA code to the Intruder tab.
   - Set the payload type to Integer and configure the range from 0000 to 9999.
   - Ensure the `Resource Pool` settings limit the number of concurrent requests to 1 to avoid being logged out due to incorrect attempts.
   - Start the attack and monitor for a successful 302 redirect indicating a valid 2FA code.

**Q3. Why is it important to use a macro in Burp Suite for this attack?**

Using a macro in Burp Suite is crucial because it automates the process of logging in and generating a new 2FA token after each failed attempt. Without a macro, the attacker would be locked out after two incorrect attempts, as the application resets the 2FA code. The macro ensures that the attacker can continuously attempt new codes without being blocked.

**Q4. How would you modify the brute force attack script to handle a scenario where the 2FA code is six digits instead of four?**

To modify the brute force attack script for a six-digit 2FA code:

1. **Adjust Payload Range**:
   - Change the payload range from 0000 to 9999 to 000000 to 999999.
   - Update the minimum and maximum lengths in the payload configuration to 6 digits.

2. **Increase Request Count**:
   - Increase the number of requests from 10,000 to 1,000,000 to cover all possible six-digit combinations.

3. **Optimize Resource Pool Settings**:
   - Ensure the resource pool settings still limit the number of concurrent requests to 1 to avoid being logged out.

**Q5. Discuss recent real-world examples where a similar brute force attack on 2FA was exploited.**

One notable example is the breach of Twitter in July 2020, where hackers used social engineering to gain access to internal tools and then used brute force attacks to bypass 2FA. In this case, the attackers managed to compromise high-profile accounts such as Barack Obama, Elon Musk, and Jeff Bezos. The lack of robust 2FA mechanisms and the ability to brute force temporary access tokens allowed the attackers to gain unauthorized access.

Another example is the breach of GitHub in November 2020, where attackers used a combination of phishing and brute force attacks to bypass 2FA and gain access to user accounts. The attackers targeted users who had reused their passwords across multiple services, allowing them to leverage stolen credentials to bypass 2FA.

In both cases, the attacks highlight the importance of implementing strong 2FA mechanisms and ensuring that users do not reuse passwords across different services.

---
<!-- nav -->
[[06-Detection and Prevention of Brute Force Attacks|Detection and Prevention of Brute Force Attacks]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/15-Lab 14 2FA bypass using a brute force attack/00-Overview|Overview]]
