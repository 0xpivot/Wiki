---
tags: [cryptography, encryption, cbc, padding-oracle, intermediate]
difficulty: intermediate
module: "32 - Cryptography Vulnerabilities"
topic: "32.05 CBC Padding Oracle Attack"
---

# CBC Padding Oracle Attack

## 1. Introduction to CBC Mode and Padding

Cipher Block Chaining (CBC) is a mode of operation for block ciphers that provides confidentiality. To encrypt a message in CBC mode, the plaintext is divided into fixed-size blocks (e.g., 16 bytes for AES). Each block of plaintext is XORed with the previous ciphertext block before being encrypted. For the very first block, an Initialization Vector (IV) is used instead of a previous ciphertext block.

### PKCS#7 Padding
Block ciphers require the total plaintext length to be an exact multiple of the block size. To satisfy this requirement, padding is appended to the end of the plaintext before encryption. The most common padding scheme is PKCS#7.

In PKCS#7, the value of each added byte is equal to the number of bytes added.
- If 1 byte is needed, the padding is `\x01`.
- If 2 bytes are needed, the padding is `\x02\x02`.
- If 3 bytes are needed, the padding is `\x03\x03\x03`.
- If the plaintext is already a multiple of the block size, an entire new block of padding is added (e.g., 16 bytes of `\x10`).

When a system decrypts the ciphertext, it verifies the padding at the end of the recovered plaintext. If the padding is incorrect (e.g., ending in `\x03\x04\x03`), the decryption function typically throws a cryptographic exception or error.

---

## 2. Visualizing CBC Decryption

To understand the padding oracle attack, one must intimately understand the math of CBC decryption.

### ASCII Diagram: CBC Decryption Process

```text
    [Ciphertext Block 1 (C1)]         [Ciphertext Block 2 (C2)]
               |                                 |
               v                                 v
         +-----------+                     +-----------+
         | Block     |                     | Block     |
 Key --->| Cipher    |             Key --->| Cipher    |
         | Decrypt   |                     | Decrypt   |
         +-----------+                     +-----------+
               |                                 |
               | (Intermediate State, I1)        | (Intermediate State, I2)
               v                                 v
  IV ------> (XOR)                     +-----> (XOR)
               |                       |         |
               v                       |         v
       [Plaintext Block 1]             |  [Plaintext Block 2]
                                       |
    (C1 is used to XOR against I2) ----+
```

### The Mathematical Relationship
Focusing on Block 2, the decryption equation is:
`Plaintext_2 = Decrypt(Ciphertext_2) ⊕ Ciphertext_1`

Let `Decrypt(Ciphertext_2)` be called the **Intermediate State ($I_2$)**. The intermediate state is the value produced by the AES decryption algorithm *before* the XOR operation is applied.
Therefore:
`Plaintext_2 = I_2 ⊕ Ciphertext_1`

An attacker cannot see $I_2$ or $Plaintext_2$, but the attacker **controls** $Ciphertext_1$ and $Ciphertext_2$.

---

## 3. The Vulnerability: The Padding Oracle

A "Padding Oracle" is a side-channel vulnerability where a system leaks information about whether the padding of a decrypted ciphertext is valid or invalid. This leakage can occur through various channels:
- **Explicit Error Messages:** The application returns "Invalid Padding Exception".
- **HTTP Status Codes:** The server returns a 500 Internal Server Error for bad padding, but a 200 OK or 302 Found for valid padding.
- **Timing Differences:** The application takes slightly longer to process valid padding compared to invalid padding.

The attacker uses this oracle to ask a simple yes/no question: *"If I modify the ciphertext this way, does the resulting plaintext have valid PKCS#7 padding?"*

---

## 4. Attack Mechanics: Decrypting the Ciphertext

The goal of the attacker is to decrypt a captured ciphertext without knowing the encryption key. They do this by iteratively guessing the Intermediate State ($I_2$) byte by byte.

### Step 1: Modifying the Previous Ciphertext Block
Suppose the attacker wants to discover the last byte of `Plaintext_2`. They know that:
`P_2[15] = I_2[15] ⊕ C_1[15]`

To manipulate `P_2[15]`, the attacker modifies `C_1[15]`. They send the modified pair `(C_1', C_2)` to the oracle.
The oracle decrypts `C_2` to `I_2` (which remains unchanged because `C_2` is untouched), and then XORs it with the attacker's modified `C_1'`:
`P_2'[15] = I_2[15] ⊕ C_1'[15]`

### Step 2: Forcing Valid Padding
The attacker's objective is to modify `C_1'[15]` until the oracle indicates that the padding is valid. If the padding is valid, the most likely scenario is that the last byte of the tampered plaintext (`P_2'[15]`) happens to be `\x01` (a valid 1-byte padding).

The attacker loops through all 256 possible values for `C_1'[15]`. When the oracle returns "Valid Padding", the attacker knows a mathematical truth:
`P_2'[15] = \x01`

Since `P_2'[15] = I_2[15] ⊕ C_1'[15]`, the attacker can substitute the known values:
`\x01 = I_2[15] ⊕ C_1'[15]`

By rearranging the XOR equation, the attacker extracts the hidden Intermediate State byte:
`I_2[15] = \x01 ⊕ C_1'[15]`

### Step 3: Recovering the Original Plaintext
Now that the attacker knows `I_2[15]`, they can recover the original, genuine plaintext byte by XORing it with the original, unmodified `C_1[15]` that they captured from the network:
`Original_P_2[15] = I_2[15] ⊕ Original_C_1[15]`

### Step 4: Iterating to the Next Byte
To find the second-to-last byte (`I_2[14]`), the attacker needs to force the padding to end in `\x02\x02`.
They already know `I_2[15]`. To force the last byte of the tampered plaintext to be `\x02`, they calculate a specific `C_1'[15]`:
`C_1'[15] = I_2[15] ⊕ \x02`

Now, they loop through all 256 values for `C_1'[14]` until the oracle says "Valid Padding". When it does, they know that `P_2'[14] = \x02`.
They calculate:
`I_2[14] = \x02 ⊕ C_1'[14]`
And recover the original plaintext:
`Original_P_2[14] = I_2[14] ⊕ Original_C_1[14]`

This process is repeated right-to-left until the entire block is decrypted. The attacker then moves to the previous block, using `C_0` (or the IV) to manipulate `C_1`.

---

## 5. Padding Oracle Encryption (CBC-MAC Forgery)

The Padding Oracle attack doesn't just allow decryption; it also allows an attacker to **encrypt** arbitrary data without knowing the key.

If an attacker knows the Intermediate State of a specific ciphertext block, they can forge a new previous block to force the plaintext to decrypt to whatever they want.
`Desired_Plaintext = I_2 ⊕ C_1'`
`C_1' = I_2 ⊕ Desired_Plaintext`

By chaining this backward block by block, an attacker can craft a completely synthetic ciphertext (and IV) that will successfully decrypt into a malicious payload (e.g., `role=admin`) on the server. This is often an extremely critical escalation.

---

## 6. Practical Example / Exploit Flow

Imagine a cookie: `Auth=IV + C_1 + C_2`
The server responds with `500 Internal Error` if padding is wrong, and `200 OK` (or `403 Forbidden` if auth fails, but padding is correct). The difference between 500 and 403 is the oracle.

1. Attacker sends `IV + Random_Block + C_2`.
2. Attacker modifies the last byte of `Random_Block` from `0x00` to `0xff`.
3. At `0x3a`, the server returns `403 Forbidden` instead of `500 Error`.
4. Attacker concludes `I_2[15] = 0x3a ⊕ 0x01 = 0x3b`.
5. Original Plaintext byte = `0x3b ⊕ Original_C_1[15]`.
6. Repeat for all bytes across the block.

---

## 7. Defense and Mitigation

Mitigating Padding Oracle attacks requires breaking the oracle feedback loop or adopting modern cryptographic standards.

1. **Encrypt-then-MAC:** The most robust defense for CBC mode is to apply a Message Authentication Code (MAC), such as HMAC, over the *ciphertext* and the IV. During decryption, the server must first verify the MAC. If the MAC is invalid, the ciphertext is dropped immediately, *before* decryption and padding validation occur. This prevents the attacker from tampering with the ciphertext to query the oracle.
2. **Authenticated Encryption with Associated Data (AEAD):** Transition away from CBC mode entirely. Modern protocols use AEAD modes like AES-GCM or ChaCha20-Poly1305. These modes inherently combine encryption and integrity verification, making them immune to padding oracle attacks as they do not use PKCS#7 padding and reject tampered ciphertexts outright.
3. **Constant-Time Responses (Weak Defense):** Attempting to mask the oracle by returning generic error messages and using constant-time comparison algorithms is notoriously difficult to implement flawlessly and is generally discouraged in favor of AEAD.

---

## 8. Chaining Opportunities

- **Session Hijacking:** Decrypting CBC-encrypted session cookies can reveal internal IDs, timestamps, and usernames, which can be forged to impersonate other users.
- **Server-Side Request Forgery (SSRF) / Deserialization:** If the decrypted payload is fed into a vulnerable deserializer or XML parser, the ability to forge arbitrary encrypted payloads via the oracle leads directly to Remote Code Execution (RCE) or SSRF.
- **[[06 - Predictable IVs and Nonces]]:** Combines closely with CBC implementation flaws where IVs are mishandled, further compromising the confidentiality of the system.

---

## 9. Related Notes

- [[01 - Introduction to Cryptographic Concepts]]
- [[02 - Block Ciphers and Stream Ciphers]]
- [[04 - ECB Mode Encryption - Block Boundary Manipulation]]
- [[10 - Cryptographic Oracles and Blind Exploitation]]
