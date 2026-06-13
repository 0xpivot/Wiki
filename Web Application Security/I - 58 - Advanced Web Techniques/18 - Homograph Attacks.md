---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.18 Homograph Attacks"
---

# Homograph Attacks

## Introduction to Homograph Attacks

A homograph attack (also known as a homoglyph attack) is a deception technique where an attacker uses characters that look alike visually (homographs) to spoof a legitimate domain name, file name, or user identifier. The goal is to trick a victim or a system into trusting a malicious entity because it appears completely identical to a trusted one.

The attack heavily relies on the vastness of the Unicode standard. With over 140,000 characters covering dozens of different alphabets (Latin, Cyrillic, Greek, Hebrew, etc.), many characters from different scripts are visually indistinguishable. For example, the Latin lowercase `a` (U+0061) is visually identical in most fonts to the Cyrillic small letter `а` (U+0430). While a human cannot tell the difference, a computer treats them as two completely separate strings.

In the context of Web Application Penetration Testing (VAPT), homograph attacks are primarily associated with Internationalized Domain Names (IDNs), but they also critically impact software supply chains (e.g., malicious npm or PyPI packages), account registration systems, and internal file upload mechanisms.

## Internationalized Domain Names (IDN) and Punycode

Historically, the Domain Name System (DNS) only supported ASCII characters. To allow global users to register domains in their native languages (like Arabic, Chinese, or Russian), the IETF introduced Internationalized Domain Names in Applications (IDNA). 

Because the underlying DNS infrastructure could not be entirely rewritten to support raw Unicode, a translation mechanism called **Punycode** was invented. Punycode takes a Unicode string and converts it into an ASCII-Compatible Encoding (ACE) string. All Punycode domains begin with the prefix `xn--`.

For example, the domain `münchen.de` is converted via Punycode to `xn--mnchen-3ya.de` before a DNS lookup is performed.

### The Attack Vector
An attacker registers a domain that uses Cyrillic characters to visually spoof a popular domain.
- Legitimate: `apple.com` (Latin 'a') -> Punycode: `apple.com`
- Malicious: `аррle.com` (Cyrillic 'а', 'р', 'р') -> Punycode: `xn--le-2tac9c.com`

When the victim clicks a link to the malicious domain, their browser might render the raw Unicode `аррle.com` in the URL bar instead of the underlying `xn--le-2tac9c.com`. The victim believes they are on the real Apple website and enters their credentials.

## ASCII Architecture Diagram: IDN Spoofing Flow

```text
+-------------------------------------------------------------+
|                     ATTACKER REGISTRATION                   |
|                                                             |
|  1. Selects Target:     citi.com                            |
|  2. Swaps 'i' (U+0069) with Cyrillic 'і' (U+0456)           |
|  3. Creates Homograph:  cіtі.com                            |
|  4. Punycode Gen:       xn--ct-oja5c.com                    |
|  5. Registers 'xn--ct-oja5c.com' with Registrar             |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                     PHISHING CAMPAIGN                       |
|                                                             |
|  Email Sent to Victim: "Please login at https://cіtі.com"   |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                     VICTIM BROWSER                          |
|                                                             |
|  1. User clicks link: https://cіtі.com                      |
|  2. Browser IDNA Engine intercepts the Unicode URL          |
|  3. Converts Unicode to Punycode -> xn--ct-oja5c.com        |
|  4. DNS Query sent for xn--ct-oja5c.com                     |
|  5. Attacker Server IP returned                             |
|                                                             |
|  URL Bar Display Logic (Varies by Browser):                 |
|  [🔒 https://cіtі.com      ] <-- Dangerous (Trust assumed)  |
|  [🔒 https://xn--ct...     ] <-- Safe (Deception revealed)  |
+-------------------------------------------------------------+
```

## Browser Defenses and The IDN Display Algorithm

Because IDN homograph attacks represent such a severe threat to the integrity of the web, browser vendors have implemented complex heuristics to determine when to display the raw Unicode in the URL bar, and when to display the ugly `xn--` Punycode format as a warning.

1. **Google Chrome & Mozilla Firefox:** 
   Modern browsers use a mechanism called the IDN Display Algorithm. They check if all characters in the domain belong to a single script (e.g., all Cyrillic or all Latin). Mixing scripts (e.g., a Cyrillic 'a' inside a mostly Latin 'pple.com') is highly suspicious and usually forces the browser to display the Punycode (`xn--`).
   
2. **Whole-Script Confusables:**
   The most dangerous attacks occur when an attacker can create a domain using characters entirely from ONE foreign script that visually resembles a Latin domain. For instance, the domain `epic.com` can be spoofed using purely Cyrillic characters: `е` (U+0435), `р` (U+0440), `і` (U+0456), `с` (U+0441). Because it uses a single script, some browser heuristics might consider it "safe" and display the Unicode form, leading to a perfect visual clone in the address bar.

## Non-DNS Attack Vectors

Homograph attacks are not limited to domain names. During a VAPT engagement, you should look for the following alternative attack surfaces:

### 1. Software Supply Chain (Typosquatting via Homographs)
Attackers frequently upload malicious packages to package managers like NPM, PyPI, or RubyGems. While traditional typosquatting uses visual mistakes (e.g., `reqeusts` instead of `requests`), advanced attackers use Unicode homographs. If a developer copies and pastes an installation command from a compromised blog or a malicious StackOverflow answer, they might accidentally install the homograph package.

Example malicious install command:
`pip install rеquests` (Where the 'е' is Cyrillic U+0435).

### 2. File Uploads and Path Confusion
If an application allows file uploads and checks the extension against a blacklist (e.g., blocking `.php`), an attacker might upload `shell.pһp` (where 'һ' is the Cyrillic U+04BB). If the web server configuration uses a different character encoding or normalizes the path incorrectly, it might execute the file as a PHP script, bypassing the initial upload filter.

### 3. Account Takeover via Username Spoofing
Similar to Unicode Normalization attacks, homographs can be used in registration systems. 
If an attacker registers `admin` but with a Cyrillic `a`, the system might see it as a distinct, valid username. The attacker can then use this account to impersonate administrators on forums, internal ticketing systems, or Slack workspaces, tricking other users into divulging sensitive information or granting permissions.

## Code Example: Generating Homograph Payloads in Python

To demonstrate the concept, here is a Python script an attacker (or a penetration tester) might use to generate possible homograph permutations for a target string.

```python
import itertools

# Mapping of Latin characters to their Cyrillic/Greek homographs
HOMOGLYPH_MAP = {
    'a': ['а', 'ɑ'], # Cyrillic 'a', Latin Alpha
    'c': ['с', 'ϲ'], # Cyrillic 'c', Greek Lunate Sigma
    'e': ['е', 'ҽ'], # Cyrillic 'e', Cyrillic 'e' with descender
    'o': ['о', 'ο'], # Cyrillic 'o', Greek Omicron
    'p': ['р', 'ρ'], # Cyrillic 'p', Greek Rho
    'x': ['х', 'χ'], # Cyrillic 'x', Greek Chi
    'y': ['у', 'γ'], # Cyrillic 'y', Greek Gamma
}

def generate_homographs(target_word):
    # Create a list of possible characters for each position
    options = []
    for char in target_word.lower():
        if char in HOMOGLYPH_MAP:
            options.append([char] + HOMOGLYPH_MAP[char])
        else:
            options.append([char])
            
    # Generate all combinations using Cartesian product
    permutations = list(itertools.product(*options))
    
    results = []
    for p in permutations:
        word = ''.join(p)
        if word != target_word:
            results.append(word)
            
    return results

# Example Usage
target = "apple"
spoofs = generate_homographs(target)
for spoof in spoofs[:5]:
    # Encode to IDNA/Punycode to see the DNS registration requirement
    punycode = spoof.encode('idna').decode('ascii')
    print(f"Unicode: {spoof}  ->  Punycode: {punycode}")
```

## Remediation and Mitigation Strategies

1. **Punycode Enforcement:** 
   Security teams should configure internal proxies, email gateways, and firewalls to flag or block incoming domains that start with `xn--` if they do not belong to a known, whitelisted international entity.
   
2. **Homograph Detection in CI/CD:**
   Implement static analysis tools in the CI/CD pipeline to scan source code and package dependencies for non-standard Unicode characters in package names and imports. Tools like `flake8-homographs` for Python can prevent developers from merging compromised code.

3. **Strict Validation for User Input:**
   For usernames, email addresses, and filenames, restrict the allowed character set to purely ASCII (`^[A-Za-z0-9_-]+$`) unless the application specifically requires internationalization. If internationalization is required, disallow mixing scripts within a single word (e.g., reject a username containing both Latin and Cyrillic).

4. **Brand Protection Services:**
   Organizations should proactively register common homograph variants of their primary domains or employ brand protection services that monitor ICANN databases for new Punycode domain registrations matching their brand.

## Chaining Opportunities

- **[[01 - Phishing and Social Engineering]]**: Homographs are the ultimate enabler for highly convincing spear-phishing campaigns.
- **[[17 - Unicode Normalization Attacks]]**: Exploiting how backend systems misinterpret the homograph after it bypasses frontend filters.
- **[[22 - Supply Chain Attacks]]**: Injecting homograph dependencies into a company's internal software registry.

## Related Notes

- [[12 - HTTP Protocol Fundamentals]]
- [[53 - Active Directory Spoofing Techniques]]
- [[02 - Input Validation and Sanitization]]

---
*End of Document*
