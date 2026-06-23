---
course: API Security
topic: User Enumeration
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what user enumeration is and how it can be exploited.**

User enumeration is a security vulnerability that allows attackers to determine whether a specific username exists within a system by analyzing the responses from the application. This can be exploited by systematically testing usernames and observing the error messages or behavior changes to confirm the existence of certain accounts. Once identified, these usernames can be targeted for further attacks such as brute-force password guessing.

**Q2. How can an attacker use the login endpoint to perform user enumeration?**

An attacker can exploit the login endpoint by submitting various usernames and observing the responses. If the application provides distinct error messages for incorrect passwords versus non-existent usernames, the attacker can infer which usernames are valid. For instance, if submitting a known good username with an incorrect password results in a "password does not match" message, but submitting a non-existent username results in a "username not found" message, the attacker can use this to enumerate valid usernames.

**Q3. Describe how an attacker might use the `create user` endpoint to perform user enumeration.**

The `create user` endpoint can be used to check if a username already exists by attempting to create a new user with a given username. If the endpoint returns an error indicating that the username is already taken, the attacker knows that the username exists. Conversely, if the endpoint successfully creates a new user, the attacker knows that the username was not previously in use. By systematically testing usernames, the attacker can build a list of existing usernames.

**Q4. How can an attacker use the `get user` endpoint to perform user enumeration?**

The `get user` endpoint can be used to check if a specific user exists by making a request with a given username. If the endpoint returns user details, the attacker knows the username exists. If the endpoint returns an error indicating that the user does not exist, the attacker can conclude that the username is not in use. By testing multiple usernames, the attacker can identify which usernames are valid.

**Q5. What measures can be implemented to prevent user enumeration vulnerabilities?**

To prevent user enumeration, developers should ensure that error messages do not reveal specific information about the existence of usernames or passwords. Instead, a generic error message such as "Invalid username or password" should be returned regardless of whether the username or password was incorrect. Additionally, implementing rate limiting and account lockout mechanisms can help mitigate the risk of brute-force attacks. Using CAPTCHAs for repeated failed login attempts can also deter automated attacks.

**Q6. Provide an example of a recent real-world breach related to user enumeration and explain how it occurred.**

In 2021, a vulnerability in the login mechanism of a popular social media platform allowed attackers to perform user enumeration. The platform's login endpoint returned different error messages for incorrect passwords and non-existent usernames. Attackers could submit a large number of username guesses and observe the error messages to determine which usernames were valid. Once valid usernames were identified, attackers could use brute-force techniques to guess passwords, leading to unauthorized access to user accounts. This vulnerability was exploited in a series of breaches that compromised numerous user accounts.

---
<!-- nav -->
[[03-User Enumeration in APIs|User Enumeration in APIs]] | [[API Security/18-User Enumeration/02-User Demonstration Demonstration/00-Overview|Overview]]
