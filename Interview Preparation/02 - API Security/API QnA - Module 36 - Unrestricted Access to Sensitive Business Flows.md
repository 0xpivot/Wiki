---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 36"
---

# Threat Hunting & Offensive Engineering: Unrestricted Access to Sensitive Business Flows

## Custom ASCII Diagram

```text
      [ Threat Actor ]                             [ Web Infrastructure ]
             |                                              |
             | 1. Discovers Sensitive Business Flow         |
             |    (e.g., Ticket Booking, Checkout)          |
             |--------------------------------------------->|
             |                                              |
             | 2. Identifies Lack of Controls               |
             |    (No Rate Limits, No Captcha)              |
             |<---------------------------------------------|
             |                                              |
             | 3. Deploys Automated Bot Swarm               |
             |    (Headless Browsers, Proxies)              |
     +-------+-------+                              +-------+-------+
     |               |                              |               |
[ Proxy 1 ]     [ Proxy 2 ]                    [ WAF / LB ]    [ App Server ]
     |               |                              |               |
     |   Request A   |                              |               |
     |-------------->|                              |               |
     |               |   Request B                  |               |
     |               |----------------------------->|               |
     |                                              |   Logic Hit   |
     |                                              |-------------->|
     |                                              |               |
     |<=============================================================|
             4. Resource Exhaustion / Scalping / Fraud
```

## Formal Technical Questions

### Q1: How do you differentiate between traditional volumetric attacks and logic-based abuse targeting sensitive business flows during a threat hunting exercise?
**Answer:**
Traditional volumetric attacks (like DDoS) focus on network or application resource exhaustion by flooding the infrastructure with massive amounts of junk traffic (e.g., SYN floods, HTTP GET floods). The primary indicator of compromise (IoC) is sheer volume originating from known bad IPs or botnets, often lacking valid session states or contextual request patterns.

Logic-based abuse, conversely, targets specific, resource-intensive, or financially significant workflows (e.g., checkout processes, account creation, password resets) using "low and slow" or highly distributed but contextually valid requests. 
Threat hunters must look for:
1. **High completion rates of specific funnels**: A high ratio of completed checkouts to initial page visits.
2. **Session anomaly**: Multiple distinct accounts created from the same device fingerprint despite IP rotation.
3. **Execution speed**: Time between workflow steps (e.g., adding to cart and checking out) that is impossible for a human, indicating headless automation.
4. **Endpoint skew**: Disproportionate traffic hitting a single sensitive endpoint compared to general application navigation.

### Q2: Explain the concept of "Business Logic Race Conditions" and how they manifest in sensitive flows.
**Answer:**
A business logic race condition occurs when an application fails to handle concurrent requests to a sensitive flow in a thread-safe manner. This allows an attacker to exploit the time-window (Time-of-Check to Time-of-Use, or TOCTOU) between when the application validates a condition and when it executes the associated action.

For example, in a financial transfer flow, the application checks if the user has a $100 balance. If an attacker sends 50 concurrent requests to transfer $100, the "check" might succeed for all 50 threads before the "use" (deducting the balance) completes on the first thread. 
Technical indicators include:
- Identical timestamps (down to the millisecond) for multiple state-changing requests.
- Single-session concurrency spikes.
- Database constraint violations or anomalous application state (e.g., negative balances).

### Q3: What role does fingerprinting play in detecting automated abuse, and how do attackers bypass it?
**Answer:**
Device and TLS fingerprinting (like JA3/JA4) are critical for identifying automated clients. A browser naturally has a specific TLS handshake signature, HTTP/2 pseudo-header order, and JavaScript execution environment. Threat hunters use these to differentiate a real Chrome browser from a Python `requests` script or an automated Selenium instance.

Attackers bypass these mechanisms by:
1. **TLS Impersonation**: Using tools like `uTLS` in Golang or custom forks of curl that perfectly mimic legitimate browser handshakes.
2. **Headless Browser Evasion**: Modifying Puppeteer/Selenium to strip `webdriver=true` flags, forging Canvas/WebGL fingerprints, and injecting fake mouse movements.
3. **Residential Proxies**: Routing traffic through botnets of compromised IoT devices or legitimate users' machines to bypass IP reputation checks.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement against an e-commerce platform. The client claims their "limited edition sneaker drop" is secure against scalping bots because they implemented a strict 1-request-per-second IP rate limit. How do you bypass this to scalp inventory?
**Answer:**
Relying solely on IP-based rate limiting is a fundamental flaw when defending sensitive business flows against modern adversaries. To bypass this and scalp the inventory, I would execute the following strategy:

1. **Distributed Infrastructure**: I would utilize a massive pool of residential rotating proxies. Since the limit is 1 req/sec per IP, having a pool of 10,000 IPs allows for 10,000 requests per second globally.
2. **Pre-Computation and Pre-Generation**: I would script the creation of thousands of accounts and active session tokens days before the drop. This avoids hitting any rate limits on the authentication endpoints during the actual event.
3. **Flow Optimization**: Instead of rendering the web page, I would analyze the exact HTTP requests required to add an item to the cart and complete the checkout. I would build a multi-threaded Golang tool that issues only the necessary POST requests.
4. **Bypassing CAPTCHA**: If a CAPTCHA is triggered, I would integrate a third-party CAPTCHA solving service (like 2Captcha or Anti-Captcha) into the script, or utilize CAPTCHA tokens pre-solved by human click-farms just moments before the drop.
5. **Concurrency**: I would synchronize all my distributed nodes via NTP to fire the "checkout" POST requests at the exact millisecond the drop goes live, overwhelming the backend logic and securing the inventory before legitimate users even load the page.

### Q2: As a Threat Hunter, you notice a massive spike in failed login attempts. However, the attempts are distributed across thousands of IPs, and each IP only makes one request. How do you detect and block this Credential Stuffing campaign?
**Answer:**
This is a classic "low and slow" distributed credential stuffing attack designed to evade basic volumetric and IP-based rate limits. 

**Detection Strategy:**
1. **Analyze Authentication Ratios**: Instead of looking at requests per IP, I would query the SIEM for the global ratio of failed vs. successful logins across the entire application. A sudden drop from a 90% success rate to a 5% success rate indicates a stuffing attack.
2. **Credential Clustering**: I would group the login attempts by the targeted usernames/emails. Attackers often run through alphabetical lists or specific breach dumps. Seeing sequential alphabetical usernames being targeted across disparate IPs is a strong signal.
3. **Header Anomaly Detection**: Even with rotating IPs, attackers often use the same scripting tool. I would hunt for anomalies in `User-Agent` strings, `Accept-Language` patterns, or specific HTTP header ordering that deviates from our baseline legitimate traffic.
4. **JA3 Hash Matching**: If we capture TLS fingerprints, I would look for a dominant JA3 hash among the failed login requests, correlating the distributed IPs back to a single underlying tool (e.g., OpenBullet or a custom Python script).

**Response:**
Immediate blocking by IP is ineffective. I would implement adaptive responses:
- Trigger step-up authentication (MFA/CAPTCHA) for any login attempt matching the suspicious JA3 hash or header profile.
- Temporarily lock accounts targeted by the attack and force a password reset.

## Deep-Dive Defensive Questions

### Q1: Develop a Splunk SPL query to detect potential Business Logic abuse on a checkout endpoint that evades basic volumetric thresholds.
**Answer:**
We want to find sessions that complete the checkout flow abnormally fast, bypassing human interaction times, or sessions that hit the checkout endpoint without hitting prerequisite pages (like adding an item to the cart).

```splunk
index=web_logs sourcetype=access_combined 
| transaction session_id maxspan=30m
| search eventcount > 1 AND uri_path="/checkout/complete"
| eval time_to_checkout = duration
| eval bypassed_cart = if(match(_raw, "/cart/add"), 0, 1)
| stats count, avg(time_to_checkout) as avg_time, max(bypassed_cart) as skipped_cart by session_id, src_ip, user_agent
| where avg_time < 2 OR skipped_cart == 1
| table session_id, src_ip, user_agent, avg_time, skipped_cart
| sort avg_time ascending
```
This query uses the `transaction` command to group events by `session_id`. It then flags any session that completed the checkout in under 2 seconds (impossible for a human to enter details) OR successfully hit the `/checkout/complete` endpoint without ever hitting `/cart/add`.

### Q2: How does implementing "Workflow State Enforcement" mitigate unrestricted access to sensitive flows?
**Answer:**
Workflow State Enforcement (or State Machine Enforcement) ensures that an entity interacting with the application strictly follows the intended sequence of steps required to complete a business flow.

In many applications, state is managed entirely client-side, allowing an attacker to intercept a request and jump straight to step 5 (e.g., `POST /transfer_funds`) without completing steps 1-4. 

Defensively, the server must track the user's progress through the state machine. When a request for step 5 is received, the server checks its internal state store (e.g., Redis session data) to verify that the user successfully completed step 4 with valid inputs. If the state is invalid or missing, the request is dropped, and an alert is generated. This effectively neutralizes direct-endpoint abuse, forced browsing, and many automated bot flows that attempt to bypass time-consuming intermediate steps.

## Real-World Attack Scenario

**The Targeted Account Takeover via Verification Abuse**

In a recent engagement against a financial technology platform, the target application allowed users to link external bank accounts. The business flow involved sending two micro-deposits to the external account, which the user had to verify by entering the exact amounts.

**The Flaw:**
The verification endpoint (`/api/v1/verify_micro_deposits`) had no rate limiting, no CAPTCHA, and did not lock the account after multiple failed attempts. It simply returned `{"status": "failed"}` or `{"status": "success"}`.

**The Attack:**
1. The attacker initiated the linking process to a victim's known account number.
2. The application sent the micro-deposits (between $0.01 and $0.99) to the victim.
3. The attacker used a highly concurrent script to brute-force the verification endpoint. Since there are only 9,801 possible combinations (99 * 99), the attacker bypassed the need to actually view the victim's bank statement.
4. Using a cluster of 10 proxies, the attacker fired 1,000 requests per second. The entire brute-force process took less than 10 seconds.
5. Upon hitting the correct combination, the external account was successfully linked to the attacker's profile, granting them unrestricted access to drain funds from the victim.

This scenario highlights how unrestricted access to a sensitive business flow (verification) completely compromised the integrity of the financial system, despite no traditional "injection" vulnerabilities being present.

## Chaining Opportunities

- **Business Logic Abuse + Parameter Tampering:** Manipulating item prices during an automated checkout flow.
- **Unrestricted Access + Information Disclosure:** Brute-forcing user enumeration endpoints at high speed to build target lists for credential stuffing.
- **Race Conditions + Unrestricted Flows:** Exploiting multi-threading vulnerabilities during concurrent sensitive actions to multiply coupon applications or duplicate transactions.
- **Bot Automation + 2FA Bypass:** Rapidly exhausting 2FA token generation until a predictable seed sequence is found or an SMS gateway is bankrupted.

## Related Notes
- [[05 - Threat Hunting Credential Stuffing]]
- [[12 - Advanced Defensive Splunk SPL]]
- [[22 - Red Teaming E-Commerce Platforms]]
- [[45 - Exploiting Race Conditions in Web Apps]]
