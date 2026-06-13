---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.11 Compression Side-Channel BREACH TIME"
---
# Compression Side-Channel Attacks: BREACH & TIME

## Introduction to Compression Side-Channels

Compression side-channels leverage the behavior of compression algorithms (like DEFLATE, used in gzip/Brotli) when applied to data that contains both attacker-controlled input and secret data. Since compression algorithms reduce the size of repeating strings, an attacker can infer the presence of a specific string (the secret) by observing the compressed size of the ciphertext.

When cryptography and compression are combined, compression happens before encryption. The size of the encrypted ciphertext is directly proportional to the size of the compressed plaintext. This creates a side-channel leak: the length of the ciphertext reveals information about the redundancy in the plaintext.

## The Foundation: CRIME

CRIME (Compression Ratio Info-leak Made Easy) was introduced in 2012 by Juliano Rizzo and Thai Duong. It targeted TLS/SSL compression and SPDY compression.

### How CRIME Works
In a CRIME attack, the attacker observes the size of the encrypted TLS payloads. The attacker injects data into the victim's request (e.g., via JavaScript submitting cross-domain requests). 

If the attacker guesses a byte of the victim's secret (like a session cookie), the compression algorithm finds a longer match between the attacker's injected string and the actual secret. This longer match results in a smaller compressed payload, which translates to a smaller encrypted ciphertext. 

By systematically guessing byte by byte, the attacker can recover the full secret.

### Mitigation of CRIME
CRIME was mitigated by disabling TLS-level compression and SPDY header compression. However, this did not solve the root issue; it only removed the mechanism at the transport layer. HTTP-level compression (e.g., compressing the HTTP response body) remained prevalent and vulnerable.

## BREACH: Browser Reconnaissance and Exfiltration via Adaptive Compression of Hypertext

BREACH is a more advanced compression side-channel attack introduced in 2013 by Angelo Prado, Neal Harris, and Yoel Gluck. Unlike CRIME, which targets TLS compression, BREACH targets HTTP response body compression (gzip/Brotli).

### Prerequisites for BREACH

For a web application to be vulnerable to BREACH, it must meet the following three conditions:
1. **HTTP-level Compression**: The server must use HTTP compression (e.g., gzip or DEFLATE) for its responses.
2. **User-input Reflection**: The application must reflect user input in the HTTP response body.
3. **Secrets in the Body**: A secret (e.g., a CSRF token, session identifier, or sensitive PII) must be present in the response body.

### Anatomy of a BREACH Attack

The attacker tricks the victim into visiting a malicious site. The site contains JavaScript that repeatedly issues requests to the vulnerable target application on behalf of the victim.

1. **Setup**: The attacker knows the context of the secret. For example, a CSRF token might be preceded by `csrf_token=`.
2. **Injection**: The attacker's script sends a request with an injected payload: `csrf_token=a`.
3. **Reflection & Compression**: The server receives the request, processes it, and returns an HTTP response containing both the injected payload (`csrf_token=a`) and the actual secret (e.g., `csrf_token=x7y8`).
4. **Observation**: The attacker observes the size of the encrypted response over the network.
5. **Iteration**: The attacker changes the payload to `csrf_token=b`, `csrf_token=c`, etc. When the attacker guesses the correct first character (e.g., `csrf_token=x`), the string `csrf_token=x` appears twice in the response (once in the reflection, once in the secret).
6. **Compression Ratio**: Because DEFLATE compresses repeated strings using back-references (LZ77), the response containing the correct guess will compress better than responses with incorrect guesses. The encrypted packet size will be smaller.
7. **Byte-by-Byte Exfiltration**: The attacker locks in the correct character and proceeds to the next: `csrf_token=x1`, `csrf_token=x2`, etc., until the entire secret is recovered.

### Visualizing the BREACH Attack Flow

```text
+---------------------+                            +-------------------------+
| Attacker Controlled |                            | Vulnerable Web Server   |
| Website (JS Code)   |                            | (HTTPS, gzip enabled)   |
+---------------------+                            +-------------------------+
          |                                                     |
          | 1. JS forces Victim Browser to request              |
          |    https://target.com/?search=csrf_token%3Da        |
          |---------------------------------------------------->|
          |                                                     |
          |                                                     | 2. Server reflects input and
          |                                                     |    includes real CSRF token.
          |                                                     |    Response body:
          |                                                     |    "...csrf_token=a...
          |                                                     |     ...csrf_token=x7y8..."
          |                                                     |
          | 3. Encrypted HTTP Response (Size: 1042 bytes)       | 
          |<----------------------------------------------------|
          |                                                     |
          | 4. JS forces request:                               |
          |    https://target.com/?search=csrf_token%3Dx        |
          |---------------------------------------------------->|
          |                                                     |
          |                                                     | 5. Response body:
          |                                                     |    "...csrf_token=x...
          |                                                     |     ...csrf_token=x7y8..."
          |                                                     |    (LZ77 compresses the repeat)
          |                                                     |
          | 6. Encrypted HTTP Response (Size: 1038 bytes)       | 
          |<----------------------------------------------------| 
          |    Smaller size detected! First byte is 'x'.        |
          |                                                     |
          v                                                     v
```

## TIME: Timing Info-leak Made Easy

TIME is a variant of the compression side-channel that does not rely on measuring the size of encrypted packets over the network. Instead, it measures the *time* it takes for the browser to process the response.

### How TIME works
TIME exploits the fact that the processing time of a response is related to its size. A highly compressible response results in a smaller encrypted payload, which takes less time to decrypt, parse, and render by the browser. 

By using high-resolution timers in JavaScript (like `performance.now()`), the attacker's script can measure the round-trip time or parsing time. If a particular guess results in a statistically significant drop in processing time, the attacker infers a correct guess. 

TIME is particularly dangerous because it does not require a network sniffer (like a Man-in-the-Middle position). The attacker only needs the victim to execute malicious JavaScript.

## Advanced Techniques: Block Ciphers vs Stream Ciphers

The precision of compression side-channel attacks depends on the underlying cipher.
- **Stream Ciphers (e.g., RC4, ChaCha20)**: Provide byte-level precision. A 1-byte change in plaintext length results in exactly a 1-byte change in ciphertext length.
- **Block Ciphers (e.g., AES-CBC)**: Add padding to match block sizes (e.g., 16 bytes). A 1-byte reduction in plaintext length might not change the ciphertext length if it just results in 1 additional byte of padding.

### Defeating Block Cipher Padding
To bypass the block cipher padding barrier, attackers use a technique called "boundary shifting" or "padding manipulation". The attacker slowly increases the size of their injected payload (e.g., adding junk characters) until the ciphertext size jumps to the next block boundary. 

Once the exact boundary is found, any single byte of compression savings will drop the total plaintext size just below the boundary, eliminating an entire block of padding and reducing the ciphertext size by exactly one block (16 bytes). This restores byte-level precision for the attack.

## HEIST: HTTP Encrypted Information can be Stolen Through TCP-windows

HEIST (2016) demonstrated a way to conduct BREACH/CRIME attacks purely in the browser without network sniffing. It abuses the Fetch API and TCP window behaviors.
By forcing the browser to fetch a cross-origin resource and measuring the exact time the promise resolves, an attacker can deduce the size of the response down to the exact byte. This is achieved by manipulating the TCP congestion window so that responses of a certain size trigger an extra round-trip, creating a massive, easily detectable timing difference.

## Mitigation Strategies

Mitigating BREACH and related attacks is notoriously difficult because compression is essential for web performance. 

1. **Disable HTTP Compression**: The most effective but least practical solution. Disabling gzip/Brotli destroys web application performance and bandwidth usage.
2. **Length Hiding (Padding)**: Injecting a random number of junk bytes into the HTTP response on every request. This adds noise to the ciphertext length, making it statistically harder (though not impossible) for the attacker to determine the true compression ratio.
3. **Masking Secrets (XORing)**: For secrets like CSRF tokens, the server can generate a random nonce, XOR the token with the nonce, and send both `(nonce, token ^ nonce)` to the client. The actual string representation of the token changes on every request, destroying the LZ77 back-reference capability.
4. **Separating Data and Secrets**: Host sensitive data/secrets on a different origin (e.g., `api.target.com`) that does not reflect user input, while the main application (`target.com`) handles user input but contains no secrets.
5. **SameSite Cookies**: Setting `SameSite=Lax` or `Strict` prevents the attacker's site from issuing authenticated cross-origin requests, thus preventing the reflection and secret from co-existing in the victim's session context.
6. **Rate Limiting**: BREACH requires thousands of requests per secret byte. Aggressive rate-limiting or anomalous traffic detection can identify and block the attack before the secret is fully extracted.

## Rupture Framework
Rupture is an open-source framework developed to automate compression side-channel attacks. It handles the statistical analysis, padding boundary alignment, and byte-by-byte guessing, demonstrating the real-world viability of these attacks even against noisy networks.

## Chaining Opportunities
- **Cross-Site Request Forgery (CSRF)**: BREACH is often used to steal CSRF tokens, which are then immediately used to execute a state-changing attack.
- **Session Hijacking**: If session IDs are passed in the URL or body (instead of just HttpOnly headers), BREACH can recover them.
- **XSS**: A stolen CSRF token can be used to alter application settings to inject a persistent XSS payload.

## Related Notes
- [[04 - Cross-Site Request Forgery (CSRF)]]
- [[12 - Timing Attacks Remote Timing Analysis]]
- [[38 - Cryptographic Failures]]
- [[21 - Advanced Cross-Site Scripting]]
