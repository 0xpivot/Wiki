---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why maintaining logs is crucial for investigating cyber attacks.**

Logs are essential in cyber investigations because they provide a detailed record of activities and events within a system. They serve as the "crime scene" for digital forensics, allowing investigators to reconstruct the sequence of actions taken by attackers. Without logs, there is no evidence to trace the steps of an intruder, making it nearly impossible to prosecute malicious actors. Logs must be protected from deletion and tampering to ensure their integrity and admissibility in legal proceedings.

**Q2. How can you prevent attackers from deleting or tampering with logs?**

To prevent attackers from deleting or tampering with logs, you should implement several security measures:

1. **Make logs read-only:** Ensure that once logs are written, they cannot be modified or deleted.
2. **Backup logs:** Regularly back up logs to multiple locations, including offsite storage, to ensure redundancy.
3. **Limit access:** Restrict access to logs to only authorized personnel using strong authentication mechanisms.
4. **Use secure logging solutions:** Employ logging solutions that support encryption and integrity checks to prevent tampering.

**Q3. List and explain three common sources of Indicators of Compromise (IOCs).**

Three common sources of Indicators of Compromise (IOCs) are:

1. **Malware Signatures:** Anti-malware software uses known patterns or signatures of malicious files to detect and block threats. These signatures can be used to identify potential infections.
   
   ```plaintext
   Example: A file with a signature matching a known virus.
   ```

2. **File Hashes:** Cryptographic hashes of files can be compared against known malicious hashes. This method is more reliable than using file names and sizes since renaming a file does not change its hash.

   ```plaintext
   Example: A file with a hash value that matches a known malicious file hash.
   ```

3. **Network Traffic:** Monitoring network traffic can reveal connections to known malicious IP addresses or domains. This includes tracking URLs visited and detecting unusual outbound traffic patterns.

   ```plaintext
   Example: A connection to a known malicious IP address or domain.
   ```

**Q4. Describe how ransomware can be detected through IOCs.**

Ransomware can be detected through various IOCs, including:

1. **File Extensions:** Ransomware often renames files with unique extensions associated with specific strains of ransomware.
   
   ```plaintext
   Example: Files renamed with extensions like .crypt or .xyz.
   ```

2. **Bulk File Renames:** A large number of files being renamed in a short period can indicate a ransomware attack.

   ```plaintext
   Example: Multiple files renamed within minutes.
   ```

3. **Ransom Notes:** The appearance of ransom notes on infected machines is a clear sign of ransomware.

   ```plaintext
   Example: A message demanding payment in exchange for decrypting files.
   ```

4. **User Reports:** Users may report issues such as slow computer performance or inability to access files, which can be indicative of ransomware.

   ```plaintext
   Example: User reports that files are inaccessible or renamed.
   ```

**Q5. How can security tools like network behavior analysis tools help in identifying IOCs?**

Network behavior analysis tools can help in identifying IOCs by monitoring and analyzing network traffic for unusual patterns or behaviors. These tools can detect anomalies such as:

1. **Unusual Outbound Traffic:** Sudden spikes in data leaving the network to known malicious IP addresses or domains.
   
   ```plaintext
   Example: Large amounts of data being sent to a known C2 server.
   ```

2. **Suspicious DNS Requests:** Requests to resolve domain names associated with known malicious activity.
   
   ```plaintext
   Example: DNS requests for domains known to host malware.
   ```

3. **Unexpected Protocol Usage:** Use of protocols or ports that are not typically seen in normal network operations.
   
   ```plaintext
   Example: Unusual use of SMB or HTTP protocols.
   ```

By identifying these behaviors, security teams can quickly respond to potential threats and mitigate damage.

**Q6. Why is it important to treat logs as evidence in the context of cyber investigations?**

Treating logs as evidence is critical because they provide a factual record of events that can be used to establish what happened during a cyber attack. Logs can help in:

1. **Reconstructing the Attack:** Understanding the sequence of events and the methods used by the attacker.
2. **Identifying the Attacker:** Tracing the origin of the attack and potentially linking it to known malicious actors.
3. **Legal Proceedings:** Providing concrete evidence that can be presented in court to support prosecution efforts.

Ensuring the integrity and preservation of logs is essential for effective forensic analysis and successful legal action against cyber criminals.

---
<!-- nav -->
[[03-Understanding Logs as the Cyber Crime Scene|Understanding Logs as the Cyber Crime Scene]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/05-Indicators of Compromise IOC/00-Overview|Overview]]
