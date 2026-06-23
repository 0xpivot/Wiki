---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the username enumeration vulnerability demonstrated in the lab?**

The purpose of the username enumeration vulnerability demonstrated in the lab is to allow attackers to identify valid usernames on the application by analyzing subtle differences in the responses from the server. This can be exploited to gain unauthorized access by brute-forcing the password of a known valid username.

**Q2. How did the lab demonstrate the presence of a valid username through subtle differences in responses?**

In the lab, the presence of a valid username was demonstrated through a subtle difference in the error message returned by the server. Specifically, when the username was invalid, the error message included a period (".") at the end, while for a valid username with an incorrect password, the period was omitted. This allowed the attacker to distinguish between valid and invalid usernames by searching for the absence of the period in the error message.

**Q3. Explain how Burp Suite's Intruder tool was used to identify a valid username in the lab.**

Burp Suite's Intruder tool was used to automate the process of identifying a valid username. First, a request containing a test username and password was sent to the Intruder. The username parameter was then set as the payload position, and a list of candidate usernames was pasted into the payloads section. By sending these requests, the Intruder tool compared the responses and identified the one where the error message lacked the period, indicating a valid username.

**Q4. How was the password brute-forced once a valid username was discovered?**

Once a valid username was discovered, the password was brute-forced using Burp Suite's Intruder tool. The valid username was kept constant, and the password field was set as the payload position. A list of candidate passwords was then pasted into the payloads section. The Intruder tool sent requests with each password in the list until a successful login was detected, indicated by a 302 redirect to the account page.

**Q5. Why is scripting this exploit in Python not recommended according to the lab?**

Scripting this exploit in Python is not recommended because the initial phase of identifying a valid username involves analyzing subtle differences in responses, which requires human judgment. Automated scripts may miss nuances that a human can detect, leading to potential errors in identifying valid usernames. Therefore, manual analysis is preferred for this part of the exploit.

**Q6. Describe a recent real-world example of a username enumeration vulnerability and its impact.**

A recent real-world example of a username enumeration vulnerability occurred in the breach of the social media platform MySpace in 2016. Attackers were able to identify valid usernames by observing different error messages for existing versus non-existing users. Once valid usernames were identified, they could be targeted with phishing attacks or password brute-forcing attempts. This vulnerability led to the exposure of sensitive user information and potential account compromises.

---
<!-- nav -->
[[02-Authentication Vulnerabilities Username Enumeration via Subtly Different Responses|Authentication Vulnerabilities Username Enumeration via Subtly Different Responses]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/05-Lab 4 Username enumeration via subtly different responses/00-Overview|Overview]]
