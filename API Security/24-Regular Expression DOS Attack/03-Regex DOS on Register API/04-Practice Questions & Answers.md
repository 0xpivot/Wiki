---
course: API Security
topic: Regular Expression DOS Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is a Regex DOS attack and how does it work?**

A Regex DOS (Denial of Service) attack exploits the way regular expressions (regex) are processed by software. When a regex pattern is complex or poorly designed, it can cause the software to spend excessive amounts of time trying to match the pattern against a given input. This can lead to a significant slowdown or even crash the system. In the context of a Register API, if the username or password fields use regex for validation, an attacker can craft inputs that trigger catastrophic backtracking, causing the regex engine to consume a lot of CPU time and potentially making the service unavailable.

**Q2. Explain how a Regex DOS attack can be exploited using a Register API.**

To exploit a Regex DOS attack on a Register API, an attacker needs to identify the regex patterns used for validating usernames or passwords. The attacker crafts a malicious input that causes the regex engine to perform extensive backtracking, leading to high CPU usage and potentially crashing the service. For example, if the regex pattern is `^[a-zA-Z]+[0-9]*$`, an attacker might submit a very long string with many characters that force the regex engine to backtrack repeatedly, such as `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1`. This can cause the regex engine to take a long time to process the input, effectively performing a DOS attack.

**Q3. How can you configure a Register API to mitigate the risk of a Regex DOS attack?**

To mitigate the risk of a Regex DOS attack on a Register API, several strategies can be employed:

1. **Optimize Regex Patterns**: Ensure that regex patterns are optimized and avoid patterns that can lead to catastrophic backtracking. Use non-capturing groups and atomic groups where possible.
   
2. **Time Limits**: Implement timeouts for regex operations to prevent them from running indefinitely. For example, set a maximum time limit for matching a regex pattern.

3. **Rate Limiting**: Apply rate limiting to the API endpoints to prevent a single client from sending too many requests in a short period.

4. **Input Validation**: Validate input lengths and types before applying regex patterns. For example, reject overly long usernames or passwords.

5. **Use Safe Libraries**: Utilize regex libraries that are designed to handle large inputs efficiently and prevent backtracking attacks.

**Q4. How can you detect a Regex DOS attack in progress on a Register API?**

Detecting a Regex DOS attack involves monitoring the system's performance and identifying unusual behavior. Here are some steps to detect such an attack:

1. **Monitor CPU Usage**: High CPU usage, especially when processing user inputs, could indicate a Regex DOS attack.
   
2. **Log Analysis**: Analyze logs for patterns of repeated requests with suspiciously long or complex inputs.

3. **Performance Metrics**: Monitor performance metrics such as response times and error rates. A sudden increase in response times or errors could suggest an ongoing attack.

4. **Real-Time Alerts**: Set up alerts for abnormal activity, such as a surge in incoming requests or unexpected spikes in resource usage.

**Q5. How would you exploit a Regex DOS vulnerability in a Register API using Burp Suite?**

To exploit a Regex DOS vulnerability using Burp Suite, follow these steps:

1. **Capture the Request**: Use Burp Suite to intercept the HTTP request sent to the Register API when a user attempts to register.
   
2. **Send to Intruder**: Right-click the captured request and select "Send to Intruder". This will open the Intruder tab with the request pre-populated.

3. **Configure Payloads**: In the Intruder tab, configure the payload positions and add a payload list containing long strings designed to trigger catastrophic backtracking. For example, use a payload like `a{1000}` which generates a string of 1000 'a' characters.

4. **Start Attack**: Start the attack and monitor the responses. The server should slow down or crash if the regex pattern is vulnerable to the crafted input.

5. **Analyze Results**: Check the server's response times and logs to confirm whether the attack was successful and caused a denial of service.

**Q6. Provide a recent real-world example of a Regex DOS attack and explain how it occurred.**

One notable example of a Regex DOS attack is the incident involving the popular web framework Express.js in 2018 (CVE-2018-1287). The vulnerability was in the `express` middleware, which used a regex pattern to parse URLs. An attacker could craft a URL with a specific pattern that caused the regex engine to perform extensive backtracking, leading to a significant slowdown or crash of the server.

For instance, the regex pattern `^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?` was vulnerable to a Regex DOS attack. An attacker could submit a URL like `http://a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z/`, which would cause the regex engine to perform excessive backtracking and consume a lot of CPU resources.

This vulnerability affected many web applications built with Express.js and highlighted the importance of optimizing regex patterns and implementing safeguards against Regex DOS attacks.

---
<!-- nav -->
[[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/03-Regular Expression Denial of Service (ReDoS)|Regular Expression Denial of Service (ReDoS)]] | [[API Security/24-Regular Expression DOS Attack/03-Regex DOS on Register API/00-Overview|Overview]]
