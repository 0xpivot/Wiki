---
course: Web Security
topic: Lab Environment Setup
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What are the essential tools needed for the web security labs and how are they installed?**

The essential tools include:
1. **Burp Suite Community Edition**: Comes pre-installed in Kali Linux.
2. **Burp Suite Professional Edition**: Requires a purchase and installation via a provided link.
3. **Visual Studio**: Used for Python scripts and requires installation via a provided link.
4. **Foxy Proxy Proxy Extension**: Only required for older versions of Burp Suite; otherwise, not necessary.

Installation instructions for each tool are detailed in the document linked in the video description. For example, Burp Suite Community Edition can be accessed directly from the Kali Linux applications menu, while Visual Studio needs to be manually installed using the provided link.

**Q2. How can you access Burp Suite Community Edition in Kali Linux?**

To access Burp Suite Community Edition in Kali Linux:
1. Click on the applications icon.
2. Type "Burp Suite Community Edition".
3. Select "Temporary Project", and click "Next".
4. Keep the default settings and click "Start Burp".

Once started, you can click on the "Proxy" tab and then "Open Browser" to use the built-in proxy that automatically sends requests to Burp Suite.

**Q3. Why is Burp Suite Professional Edition not mandatory for the course, and what are its additional features?**

Burp Suite Professional Edition is not mandatory because only a small portion of the videos require its use, specifically for functionalities like Collaborator and Intruder. These features are more advanced and are typically used in real-world engagements where employers provide the professional version. If you do not have the funds to purchase it, you can still learn by watching the videos and understanding how to use these features, even if you cannot apply them practically.

**Q4. What is the purpose of the Foxy Proxy Proxy extension, and why is it not recommended for recent versions of Burp Suite?**

The Foxy Proxy Proxy extension is used to configure a browser to send requests to Burp Suite. This was necessary in older versions of Burp Suite, which did not have a built-in browser. However, newer versions of Burp Suite include a built-in browser, making the Foxy Proxy Proxy extension unnecessary. Therefore, it is not recommended unless you are using an outdated version of Burp Suite.

**Q5. Explain the process of intercepting requests using Burp Suite's built-in proxy.**

To intercept requests using Burp Suite's built-in proxy:
1. Start Burp Suite and navigate to the "Proxy" tab.
2. Click "Open Browser" to launch the built-in browser.
3. Browse to a website (e.g., Google).
4. Go to the "HTTP History" tab to see all intercepted requests.

This process allows you to monitor and analyze network traffic between your browser and the target server.

**Q6. What is the Portswigger Web Security Academy, and how do you access it?**

Portswigger Web Security Academy is a free online web security training platform created by Portswigger, the same organization that develops Burp Suite. To access it:
1. Register an account using the provided link.
2. Complete the registration process via email instructions.
3. Log in and access the academy.

This platform provides various labs and exercises for practicing web security techniques covered in the course.

**Q7. How can you configure your browser to work with Burp Suite if you are using an older version without a built-in proxy?**

If you are using an older version of Burp Suite without a built-in proxy, you need to configure your browser to send requests through Burp Suite:
1. Install the Foxy Proxy Proxy extension in Firefox.
2. Configure the extension to route traffic through Burp Suite.
3. Set up the SSL certificate in your browser to trust Burp Suite.
4. Ensure that your browser is configured to use Burp Suite as a proxy.

These steps ensure that your browser sends all HTTP and HTTPS traffic through Burp Suite for interception and analysis.

---
<!-- nav -->
[[03-Session 1 Initial Reconnaissance|Session 1 Initial Reconnaissance]] | [[Web Security (PortSwigger)/01-Lab Environment Setup/01-Lab Environment Setup/00-Overview|Overview]]
