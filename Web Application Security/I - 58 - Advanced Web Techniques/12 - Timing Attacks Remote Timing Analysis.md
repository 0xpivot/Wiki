---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.12 Timing Attacks Remote Timing Analysis"
---
# Remote Timing Analysis and Timing Attacks

## Introduction to Timing Attacks

A timing attack is a type of side-channel attack where an attacker attempts to compromise a system by analyzing the time taken to execute cryptographic algorithms, database queries, or general business logic. By measuring these minute variations in response times, an attacker can infer sensitive information, deduce application states, or bypass security controls.

In a web context, timing attacks are typically remote, meaning the attacker relies on network requests to measure the execution time on a remote server. This introduces massive challenges due to network jitter, latency variations, and server load, making remote timing analysis a complex statistical endeavor.

## Types of Timing Vulnerabilities in Web Apps

Timing leaks occur when the execution path of a program diverges based on secret data or attacker-controlled input. Common vulnerable scenarios include:

1. **String/Password Comparisons**: Using standard equality operators (e.g., `==` or `strcmp()`) instead of constant-time functions. Standard operators fail fast; they stop comparing as soon as a mismatch is found.
2. **Cryptographic Signatures (HMAC/JWT)**: If an application verifies a digital signature byte-by-byte and returns early on failure, the verification time leaks the length of the matching prefix.
3. **Database Queries**: If a query is executed only when a certain condition is met (e.g., checking if a user exists before checking their password), the difference in response time reveals the existence of the user.
4. **API Authentication**: Different processing times for valid vs. invalid API keys, or valid usernames vs. invalid usernames.

## Anatomy of a Byte-by-Byte Timing Attack

Consider a vulnerable password check or HMAC verification:

```python
# VULNERABLE CODE
def check_hmac(user_hmac, actual_hmac):
    if len(user_hmac) != len(actual_hmac):
        return False
    for i in range(len(user_hmac)):
        if user_hmac[i] != actual_hmac[i]:
            return False # Fails fast!
    return True
```

If an attacker submits `A000`, the loop checks index 0. If it mismatches, it returns immediately (1 unit of time). 
If the attacker submits `B000`, and `B` is correct, the loop checks index 0 (match), then index 1 (mismatch). It returns (2 units of time).

By measuring the response times, the attacker can guess the HMAC byte-by-byte.

### ASCII Diagram: Remote Timing Analysis

```text
Attacker                     Network                      Server (Vulnerable String Compare)
   |                            |                                |
   | Send "A000"                |                                |
   |--------------------------->|                                |
   |                            | Compare[0] 'A' != 'S' (Fail)   |
   | Time = T1                  |<-------------------------------|
   |                            |                                |
   | Send "S000"                |                                |
   |--------------------------->|                                |
   |                            | Compare[0] 'S' == 'S' (Match)  |
   |                            | Compare[1] '0' != 'e' (Fail)   |
   | Time = T2 (T2 > T1)        |<-------------------------------|
   |                            |                                |
   | Attacker deduces first byte is 'S' due to measurable delay. |
   v                                                             v
```

## The Challenge of Remote Timing Analysis

Over a WAN or the Internet, network jitter is massive compared to the nanosecond differences of CPU instructions. 
A single string comparison mismatch might save 50 nanoseconds, while network jitter fluctuates by 50,000,000 nanoseconds (50 milliseconds).

### Overcoming Jitter: Statistical Methods

To extract signal from the noise, attackers use statistical amplification.

1. **Massive Sampling**: Sending thousands of requests for the same payload and averaging the times.
2. **Filtering Outliers**: Network spikes, garbage collection pauses on the server, and TCP retransmissions create massive outliers. Attackers typically discard the top and bottom 5-10% of response times (Trimmed Mean) or use the Median, which is highly resistant to outliers.
3. **Box Test**: Comparing the lowest percentile of response times. The fastest responses represent the theoretical minimum network transit time, which contains the least jitter.
4. **Student's t-test**: A statistical hypothesis test used to determine if there is a significant difference between the means of two groups (e.g., times for guess A vs. guess B).

## Multi-variable Timing Analysis

Sometimes applications introduce random delays to thwart timing attacks. However, if the random delay is bounded or follows a specific distribution, statistical analysis over a large enough dataset will average out the random delay, leaving only the execution time difference.

## Timeless Timing Attacks

A breakthrough in timing attacks is the "Timeless Timing Attack" (TTA), primarily exploiting HTTP/2 multiplexing.

### Concurrency over HTTP/2
In HTTP/2, multiple requests can be sent over a single TCP connection concurrently. An attacker can place two requests (Request A and Request B) into a single network packet. 
Because they are in the same packet, they experience the exact same network latency and arrive at the server simultaneously.

The server processes them concurrently. The attacker observes the order in which the responses arrive back. 
If Request A consistently returns before Request B, the attacker knows Request A required less processing time, completely independent of network latency or jitter.

This reduces the required sample size from thousands to dozens, making microsecond-level timing attacks practical over the open internet.

## Exploitation Tools
- **wfuzz / ffuf**: Custom scripts wrapped around these fuzzers to measure response times.
- **Turbo Intruder**: A Burp Suite extension by James Kettle, designed for high-speed, low-jitter HTTP attacks, perfect for timing analysis and race conditions.
- **Time-Trial**: Open-source tools specifically built for remote timing analysis using statistical correlation.

## Mitigation Strategies

### 1. Constant-Time Comparisons
Always use constant-time comparison functions for sensitive strings, hashes, tokens, and passwords.

```python
# SECURE CODE (Python)
import hmac

def check_hmac_secure(user_hmac, actual_hmac):
    return hmac.compare_digest(user_hmac, actual_hmac)
```
```php
// SECURE CODE (PHP)
hash_equals($actual_hmac, $user_hmac);
```

### 2. Hash Verification
When looking up users in a database, prevent timing leaks regarding user existence by performing a dummy password verification even if the user is not found.

```python
# SECURE LOGIN FLOW
user = db.get_user(username)
if user:
    verify_password(input_password, user.password_hash)
else:
    # Prevent user enumeration timing attack
    verify_password(input_password, DUMMY_HASH)
```

### 3. Rate Limiting and Monitoring
Strict rate limiting makes statistical timing attacks mathematically impossible to execute within a reasonable timeframe. If an attacker needs 10,000 requests per byte, a rate limit of 10 requests per minute forces the attack to take years.

### 4. Jitter / Padding Delays
Artificially padding the response time to a fixed boundary (e.g., always ensuring an authentication request takes exactly 500ms).
*Warning*: If the processing time exceeds 500ms under load, the timing leak reappears.

## Chaining Opportunities
- **Authentication Bypass**: Forging JWT signatures or session tokens by extracting HMAC keys.
- **Username Enumeration**: Chaining with brute-force to identify valid administrative accounts.
- **Data Exfiltration**: In Blind SQLi, timing attacks (using `SLEEP()`) are the primary method of extracting data when error or boolean inference is unavailable.

## Related Notes
- [[13 - Race Condition TOCTOU]]
- [[34 - JSON Web Token (JWT) Security]]
- [[02 - Blind SQL Injection]]
- [[11 - Compression Side-Channel BREACH TIME]]
