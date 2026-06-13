---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.18 Certificates and Certificate Authorities"
---

# 01.18 — Certificates and Certificate Authorities

## What is it?

An **SSL/TLS certificate** is a digital document that proves a server is who it claims to be. A **Certificate Authority (CA)** is a trusted organization that vouches for certificates by digitally signing them.

**Analogy:** A certificate is like a passport. The CA is the government that issues it. When your browser connects to a server, it's like a border agent checking whether the passport is valid and issued by a trusted government.

---

## How Certificate Trust Works

```
TRUST CHAIN:
                    ┌─────────────────────────────┐
                    │  Root CA Certificate         │
                    │  (DigiCert Global Root)      │ ← Built into OS/browser
                    │  Self-signed, trusted by all │
                    └──────────────┬──────────────┘
                                   │ signs
                    ┌──────────────▼──────────────┐
                    │  Intermediate CA Certificate │
                    │  (DigiCert TLS RSA SHA256)   │ ← Issued by Root CA
                    └──────────────┬──────────────┘
                                   │ signs
                    ┌──────────────▼──────────────┐
                    │  End-Entity Certificate      │
                    │  CN=target.com               │ ← Issued by Intermediate CA
                    │  Valid: 2024-01-01 to 2025   │
                    └─────────────────────────────┘

VERIFICATION PROCESS:
1. Browser connects to target.com
2. Server sends its certificate + intermediate CA cert
3. Browser builds chain: End-Entity → Intermediate → Root CA
4. Browser checks Root CA is in its trusted store
5. Browser verifies each signature in the chain
6. Browser checks cert is not expired
7. Browser checks CN/SAN matches the hostname (target.com)
8. Connection is trusted ✓
```

---

## What's Inside a Certificate

```bash
openssl x509 -in cert.pem -noout -text
# Key fields:

Version: 3
Serial Number: 04:e6:2e:93:af:5c:c3...     # Unique ID
Signature Algorithm: sha256WithRSAEncryption

Issuer: C=US, O=DigiCert, CN=DigiCert RSA CA G1   ← who issued it
Subject: C=US, O=Target Corp, CN=target.com        ← who it's for

Validity:
  Not Before: Jan 1 00:00:00 2024 GMT
  Not After:  Jan 1 23:59:59 2025 GMT   ← expiry

Subject Alternative Names (SANs):         ← ALL valid hostnames!
  DNS:target.com
  DNS:www.target.com
  DNS:api.target.com
  DNS:internal.target.com                 ← ← ← Hidden subdomain!

Public Key: RSA 2048 bit (or ECDSA P-256)

X509v3 Basic Constraints: CA:FALSE        ← not a CA cert
X509v3 Key Usage: Digital Signature, Key Encipherment
X509v3 CRL Distribution Points: http://crl.digicert.com/...
X509v3 Authority Information Access:
  OCSP: http://ocsp.digicert.com         ← revocation check
```

---

## Types of Certificates

```
DOMAIN VALIDATION (DV):
  Proves: You control the domain
  Verification: DNS TXT record or HTTP file
  Issued by: Let's Encrypt (free!), ZeroSSL
  Browser shows: Lock icon + domain name
  Time: Minutes

ORGANIZATION VALIDATION (OV):
  Proves: Organization identity verified
  Verification: Company documents + domain control
  Issued by: DigiCert, Comodo, Sectigo
  Browser shows: Lock icon + org name in some browsers
  Time: Days

EXTENDED VALIDATION (EV):
  Proves: Extensive org verification + jurisdiction
  Verification: Legal documents, physical verification
  Issued by: DigiCert, Entrust
  Browser shows: Was green bar (now just lock, most browsers dropped EV UI)
  Time: Weeks

WILDCARD CERTIFICATE:
  CN=*.target.com
  Covers: www.target.com, api.target.com, anything.target.com
  Does NOT cover: deep.sub.target.com (only one level!)

MULTI-DOMAIN (SAN):
  Covers multiple specific domains via SAN entries
  CN=target.com, SAN: target.com, otherdomain.com, api.target.com
```

---

## Security Context — Certificates in VAPT

### 1. Certificate Transparency — Subdomain Discovery

All certificates issued by CAs are logged in public **Certificate Transparency (CT) logs**. This is mandatory. This means you can find EVERY subdomain ever issued a certificate.

```bash
# crt.sh — search CT logs
curl "https://crt.sh/?q=%25.target.com&output=json" 2>/dev/null | \
  python3 -c "import json,sys; [print(e['name_value']) for e in json.load(sys.stdin)]" | \
  sort -u > subdomains.txt

# Direct crt.sh web search:
# https://crt.sh/?q=%.target.com

# subfinder uses CT logs + other sources
subfinder -d target.com

# amass uses CT logs
amass enum -d target.com

# Certificate Transparency reveals:
# - All subdomains (even internal ones that got certs!)
# - Internal hostnames: internal.target.com, vpn.corp.target.com
# - Pre-production: dev.target.com, staging.target.com
# - Old certificates from years ago
```

### 2. Certificate Information as Recon

```bash
# View target's cert
echo | openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -noout -text

# Extract key info:
# Organization: "Target Corp Inc" → official company name
# Email: admin@target.com → admin contact for spear phishing
# SAN: reveals ALL hostnames on this cert
# CA: which CA they use → check CA for vulnerabilities

# Check for expired certs (common on internal/staging):
echo | openssl s_client -connect target.com:443 2>/dev/null | \
  openssl x509 -noout -dates
# If past Not After → browser shows error, but curl -k bypasses it

# Shodan cert search
shodan search "ssl.cert.subject.cn:target.com"
```

### 3. Self-Signed Certificates — Trust Issues

Self-signed certs don't have a CA signature. Browsers warn users.

```bash
# Check for self-signed cert:
echo | openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -noout -issuer -subject
# If Issuer == Subject → self-signed!

# Connect ignoring cert errors (curl -k):
curl -k https://target.com/
# WARNING: this bypasses MITM protection → only for authorized testing

# Pentest significance:
# Self-signed cert → probably internal/dev → misconfigured → attack target
```

### 4. Certificate Pinning Bypass (Mobile)

```bash
# Android apps that pin certs only accept specific cert
# Bypass with Frida:
frida -U -f com.target.app --no-pause -l ssl_bypass.js

# ssl_bypass.js (Frida script):
Java.perform(function() {
    var TrustManager = Java.registerClass({
        name: 'com.sensepost.test.TrustManager',
        implements: [javax.net.ssl.X509TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });
    // Install our no-op trust manager
    var SSLContext = javax.net.ssl.SSLContext.getInstance("TLS");
    SSLContext.init(null, [TrustManager.$new()], null);
    javax.net.ssl.HttpsURLConnection.setDefaultSSLSocketFactory(SSLContext.getSocketFactory());
});
```

### 5. OCSP Stapling and CRL — Revocation

```bash
# Check if cert is revoked
# Method 1: OCSP
openssl s_client -connect target.com:443 -status 2>/dev/null | grep -A 10 OCSP

# Method 2: CRL (Certificate Revocation List)
# Get CRL URL from cert:
openssl x509 -in cert.pem -noout -text | grep "CRL Distribution"
# http://crl.digicert.com/xxx.crl

# Download and check CRL:
curl http://crl.digicert.com/xxx.crl -o crl.der
openssl crl -in crl.der -inform DER -noout -text | grep SERIAL
# If cert serial is listed → revoked!
```

### 6. CA Misconfiguration — Wildcard Issuance

Some internal CAs are misconfigured to issue certs for any domain:

```
Internal CA → issues cert for *.target.com to attacker
Attacker uses cert → MITM internal traffic
Internal users trust the CA → no browser warning
```

---

## Hands-On: Certificate Commands

```bash
# View full cert from live server
openssl s_client -connect target.com:443 -showcerts

# Save cert to file
openssl s_client -connect target.com:443 2>/dev/null | \
  sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p' > cert.pem

# View cert file
openssl x509 -in cert.pem -noout -text

# Check cert expiry
openssl x509 -in cert.pem -noout -dates

# Generate CSR (certificate signing request)
openssl req -new -newkey rsa:2048 -keyout private.key -out request.csr -nodes

# Create CA and sign cert (for lab)
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Self-signed certificate in production | Get a proper CA-signed cert (Let's Encrypt is free) |
| Certificate expired | Automate renewal with certbot/acme.sh |
| Wildcard cert covers too much | Use specific SAN certs per service |
| Internal domains in public certs | Use internal CA for internal services |
| No HPKP / cert pinning | Implement pinning for high-value apps |
| Weak RSA key (1024 bit) | Use 2048+ RSA or ECDSA P-256 |

---

## Related Notes
- [[17 - TLS SSL How HTTPS Works]] — how certs are used in TLS
- [[Module 05 - Recon]] — CT log subdomain discovery
- [[Module 34 - Subdomain Takeover]] — expired certs + subdomain reuse
- [[Module 48 - Wireless Security]] — MITM with fake certs on WiFi
