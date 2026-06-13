---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.54 X-AspNet-Version / X-AspNetMvc-Version — Framework Disclosure"
---

# 03.54 — X-AspNet-Version / X-AspNetMvc-Version

## What is it?

`X-AspNet-Version` and `X-AspNetMvc-Version` are response headers automatically added by ASP.NET and ASP.NET MVC frameworks respectively. They disclose the exact .NET framework and MVC version running the application — enabling targeted CVE exploitation.

---

## Header Values

```
X-AspNet-Version: 4.0.30319           → ASP.NET Framework version
X-AspNetMvc-Version: 5.2.7.0          → MVC version
X-Powered-By: ASP.NET                 → broad disclosure

COMBINED FINGERPRINT:
  Server: Microsoft-IIS/10.0
  X-Powered-By: ASP.NET
  X-AspNet-Version: 4.0.30319
  X-AspNetMvc-Version: 5.2.7.0
  
  → Windows Server 2016+, IIS 10, .NET 4.x, MVC 5.2.7
```

---

## Attack: Version-Targeted Exploits

```
ASP.NET 4.0.30319 → .NET 4.0 RTM
  → Check: MS10-070 (.NET padding oracle → CVE-2010-3332!)
  → ASPXAUTH cookie decryption → admin takeover!

PADDING ORACLE ATTACK (.NET):
  Tool: padbuster
  Target: __VIEWSTATE or ASPXAUTH cookie
  padbuster https://target.com/page __VIEWSTATE 8 --encoding 0

OLD MVC VERSION:
  X-AspNetMvc-Version: 2.0 → very old → likely many vulns
  → Unvalidated redirects, CSRF gaps in old versions
```

---

## ViewState Disclosure

```
ASP.NET apps use __VIEWSTATE — base64-encoded state in forms.
If MAC validation is disabled:
  → ViewState is not signed → attacker can forge arbitrary values!
  → Deserialization vulnerabilities!

X-AspNet-Version combined with exposed ViewState:
  → Use YSoSerial.NET to generate gadget chains!

Tools:
  ysoserial.exe -p ViewState -g ActivitySurrogateSelector
  Burp Extension: "ViewState Editor"
```

---

## Testing

```bash
# Check ASP.NET headers:
curl -sI https://target.com | grep -iE "x-aspnet|x-powered-by: asp"

# Check for __VIEWSTATE in forms:
curl -s https://target.com/login | grep "__VIEWSTATE"

# Padding oracle test (carefully):
padbuster https://target.com/default.aspx <ENCRYPTEDVALUE> 8 -encoding 0

# .NET version to release mapping:
# 4.0.30319 = .NET Framework 4.0 (2010) - VERY OLD!
# 4.7.3062  = .NET Framework 4.7.2
# 6.0       = .NET 6 (ASP.NET Core)
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| X-AspNet-Version disclosed | Remove in web.config |
| X-AspNetMvc-Version disclosed | FilterConfig or web.config |

**web.config removal:**
```xml
<system.web>
  <httpRuntime enableVersionHeader="false" />
</system.web>

<system.webServer>
  <httpProtocol>
    <customHeaders>
      <remove name="X-Powered-By" />
      <remove name="X-AspNet-Version" />
      <remove name="X-AspNetMvc-Version" />
    </customHeaders>
  </httpProtocol>
</system.webServer>
```

---

## Related Notes
- [[52 - X-Powered-By]] — framework fingerprinting
- [[53 - Server]] — server version disclosure
- [[Module 17 - Recon]] — full fingerprinting guide
- [[Module 09 - Deserialization]] — .NET deserialization
