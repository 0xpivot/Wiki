---
tags: [cryptography, tls, crime, compression, advanced]
difficulty: advanced
module: "32 - Cryptography Vulnerabilities"
topic: "32.13 CRIME Attack (compression of cookies over TLS)"
---

# CRIME Attack (Compression Ratio Info-leak Made Easy)

## Introduction

The Compression Ratio Info-leak Made Easy (CRIME) attack is a severe cryptographic vulnerability discovered by security researchers Juliano Rizzo and Thai Duong in 2012. It targets the confidentiality of data transmitted over secure connections (such as HTTPS/TLS or SPDY) by exploiting the way data compression algorithms interact with encryption. Unlike traditional cryptographic attacks that target the underlying mathematical properties of the encryption algorithms themselves (e.g., breaking RSA or exploiting weak cipher suites), CRIME operates at a different layer of abstraction. It abuses the deterministic nature of lossless data compression (specifically DEFLATE) and how it reveals the presence of repeated data patterns through the length of the resulting ciphertext. 

The primary target of a CRIME attack is usually session identifiers, specifically HTTP cookies used for authentication. By injecting attacker-controlled plaintext into the encrypted stream and observing the size of the compressed ciphertext, an attacker can systematically brute-force the contents of secret data, character by character. This represents a classic side-channel attack where the "leak" is not timing or power consumption, but rather the length of the data packet on the wire.

## The Core Vulnerability Mechanism

### Compression Basics: DEFLATE and LZ77
To understand CRIME, one must first understand how compression algorithms like DEFLATE work. DEFLATE relies on a combination of LZ77 compression and Huffman coding. The LZ77 algorithm looks for repeated sequences of characters within a sliding window of the data. When it finds a repeated sequence, instead of storing the characters again, it stores a back-reference (a pointer and a length) to the previous occurrence.

For example, consider the string:
`secret_cookie=super_secret_cookie`

Without compression, this string takes up 35 bytes. However, LZ77 recognizes that the string `secret_cookie` is repeated. It can compress the second occurrence:
`secret_cookie=super_<go back 20 characters, copy 13 characters>`

This back-reference takes up significantly less space than the original text, resulting in a compressed payload that is much smaller than the original.

### Encryption Does Not Hide Length
Encryption algorithms (like AES) are designed to hide the *contents* of a message, making it indistinguishable from random noise to anyone without the key. However, standard encryption algorithms do *not* hide the *length* of the message. If you input 100 bytes of plaintext into AES-CTR, the resulting ciphertext will be 100 bytes long. Even block ciphers with padding (like AES-CBC) only round the length up to the nearest block size (e.g., 16 bytes), which still provides a highly accurate indication of the original plaintext length.

### The Fatal Intersection: Compression + Encryption + Attacker Input
The vulnerability arises when three conditions are met simultaneously:
1. The protocol compresses data *before* encrypting it (which is standard practice, as encrypted data looks like random noise and cannot be compressed).
2. The attacker can observe the length of the encrypted packets sent over the network.
3. The attacker can force the victim to encrypt data that contains both the attacker's chosen input and the victim's secret data (e.g., a session cookie) within the *same* compressed context.

## Attack Flow and Exploitation

The CRIME attack operates by forcing the victim's browser to send requests to the target website where the victim is authenticated. The attacker constructs these requests to include arbitrary, attacker-controlled strings within the HTTP headers or URL, which are compressed alongside the victim's secret HTTP cookies.

### Step-by-Step Brute-forcing

Let's assume the victim's browser has a secret cookie: `Cookie: session=ABCDE12345`
The attacker wants to steal this cookie to hijack the session.

1. **Initial Setup**: The attacker intercepts the victim's network traffic (MitM) and lures the victim to an attacker-controlled website, or injects malicious JavaScript into an insecure HTTP connection.
2. **First Guess**: The malicious JavaScript forces the browser to make a cross-origin request to the secure target site, appending a guess to the URL path or an injected header.
   The attacker injects the guess `session=A`. The raw HTTP request looks roughly like this:
   ```http
   GET /?guess=session=A HTTP/1.1
   Host: secure-bank.com
   Cookie: session=ABCDE12345
   ```
3. **Compression Efficiency**: The DEFLATE algorithm processes this request. It sees `session=A` in the URL and `session=A` (the first part of `session=ABCDE12345`) in the Cookie header. Because these strings match, LZ77 replaces the second occurrence with a short pointer. This results in a highly efficient compression. The final payload size might be, for example, 150 bytes.
4. **Incorrect Guess**: Next, the attacker guesses `session=X`.
   ```http
   GET /?guess=session=X HTTP/1.1
   Host: secure-bank.com
   Cookie: session=ABCDE12345
   ```
   DEFLATE processes this. It sees `session=X` in the URL and `session=A` in the Cookie header. The `session=` part matches and compresses, but the `X` does not match the `A`. Therefore, the `X` must be stored literally, which is less efficient. The final payload size might be 151 bytes.
5. **Observation**: The attacker, monitoring the network wire, observes that the packet generated by the guess `session=A` is smaller than the packet generated by `session=X`. The attacker concludes that `A` is the correct first character of the cookie.
6. **Iteration**: The attacker appends the known character and repeats the process to guess the next character: `session=AB`, `session=AC`, `session=AD`, etc., observing the packet sizes until the entire cookie is recovered.

### ASCII Diagram of the CRIME Attack

```text
+-------------------+                                      +-------------------+
|     Attacker      |                                      |      Server       |
| (Malicious JS)    |                                      |  (TLS Enabled)    |
+---------+---------+                                      +---------+---------+
          |                                                          |
          | 1. Forces victim browser to send request                 |
          |    Path: /?guess=session=A                               |
          |--------------------------------------------------------->|
          |                                                          |
          | 2. Browser compresses headers (DEFLATE)                  |
          |    [Cookie: session=XYZ...] + [Path: /?guess=session=A]  |
          |    If guess 'A' is wrong, size = N bytes                 |
          |                                                          |
          | 3. Forces victim browser to send request                 |
          |    Path: /?guess=session=X                               |
          |--------------------------------------------------------->|
          |                                                          |
          | 4. Browser compresses headers (DEFLATE)                  |
          |    'session=X' matches part of the cookie.               |
          |    Compression is more efficient! Size = N-1 bytes       |
          |                                                          |
          | 5. Attacker observes network traffic size (Man-in-Middle)|
          |<---------------------------------------------------------|
          |    Identifies correct character by smaller payload size  |
          |                                                          |
+---------+---------+                                      +---------+---------+
```

## Advanced Considerations and Constraints

### Block Cipher Padding Issues
While the concept relies on length differences of a single byte, block ciphers like AES-CBC operate on fixed-size blocks (e.g., 16 bytes). This means that a 1-byte change in the compressed plaintext might not immediately result in a change in the ciphertext length, unless the plaintext size crosses a block boundary. Attackers bypass this by strategically adding dummy padding to the URL or headers until the compressed payload is exactly at a block boundary. Once exactly aligned, any decrease in compression efficiency will immediately push the payload into a new 16-byte block, making the difference highly visible.

### HTTP/2 and HPACK
While TLS compression was widely disabled to mitigate CRIME, the introduction of HTTP/2 brought its own header compression mechanism known as HPACK. Because HPACK operates on HTTP headers (which contain cookies), it initially raised concerns about a resurgence of CRIME-like vulnerabilities. However, HPACK was specifically designed to mitigate these side-channels by separating static and dynamic dictionaries, and by allowing sensitive headers (like cookies) to be marked as "never index," preventing them from being compressed in a way that an attacker could exploit.

### SPDY Vulnerability
Before HTTP/2, Google developed the SPDY protocol, which mandated header compression using DEFLATE. Because SPDY compressed all headers within a single DEFLATE stream, it was inherently vulnerable to the CRIME attack, leading to massive industry shifts and the eventual deprecation of SPDY in favor of the more robust HTTP/2 standards.

## Mitigation and Defense

The most effective and definitive mitigation for the CRIME attack is to **disable compression at the TLS level**. 

1. **Disable TLS Compression**: Server administrators must configure their web servers and TLS libraries (like OpenSSL) to explicitly disable TLS-level compression. Modern defaults in nearly all web servers and libraries have compression disabled by default.
2. **Browser Updates**: Modern web browsers entirely dropped support for TLS compression shortly after the CRIME vulnerability was publicized. Even if a server attempts to negotiate compression, modern clients will refuse.
3. **Application-Level Compression**: It is important to distinguish TLS compression from HTTP content compression (e.g., `Content-Encoding: gzip`). HTTP content compression only compresses the body of the HTTP response, not the headers (where the cookies live). Therefore, HTTP content compression does not inherently expose cookies to the CRIME attack, although it can expose CSRF tokens in the response body to a related attack known as BREACH.

To verify a server is not vulnerable, administrators can use tools like `nmap` or `testssl.sh`:
```bash
nmap -p 443 --script ssl-enum-ciphers <target>
# Look for "compression: NULL"
```

## Chaining Opportunities
CRIME is often a gateway to complete session takeover. Once an attacker successfully extracts the victim's session cookie, they can chain this with:
- **Account Takeover**: Replaying the stolen cookie to impersonate the victim, bypassing standard login mechanisms entirely.
- **Privilege Escalation**: If the victim is an administrator, the attacker immediately gains administrative access to the web application.
- **CSRF Bypass**: If the CSRF token is stored in a cookie, the attacker can extract it to forge state-changing requests.

## Related Notes
- [[12 - POODLE Attack]] - Another attack exploiting TLS weaknesses (specifically CBC padding in SSLv3).
- [[09 - BEAST Attack]] - An older attack targeting CBC mode initialization vectors in TLS 1.0.
- [[14 - Diffie-Hellman Weak Parameters (Logjam)]] - Another TLS downgrade attack.
- [[11 - Padding Oracle Attacks]] - Detailed mechanics of how padding interacts with cryptography, relevant to how block boundaries are calculated.
- [[16 - BREACH Attack]] - The spiritual successor to CRIME, which targets HTTP response body compression instead of TLS header compression.
