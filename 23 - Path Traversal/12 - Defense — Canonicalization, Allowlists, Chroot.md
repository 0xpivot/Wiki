---
tags: [vapt, path-traversal, defense, advanced]
difficulty: advanced
module: "23 - Path Traversal and LFI/RFI"
topic: "23.12 Defense — Canonicalization, Allowlists, Chroot"
---

# 23.12 — Defense: Canonicalization, Allowlists, Chroot

## What is it?
Defending against Path Traversal and File Inclusion requires a defense-in-depth approach. Because attackers constantly invent new encoding techniques (`%252e%252e%252f`, null bytes, non-standard OS pathing), relying on blocklists (e.g., `replace('../', '')`) is guaranteed to fail.

The gold standard for defense involves three concepts:
1. **Allowlists (Indirect References):** Never pass user input to the filesystem. Use a database or an array map to link a safe, numeric ID to a real file.
2. **Canonicalization (Path Resolution):** If you *must* use user-supplied names, resolve the absolute path completely (resolving all symlinks and `../` sequences) *before* you validate it.
3. **Chroot Jails / OS Sandboxing:** Strip the web application of its ability to see the rest of the filesystem entirely using OS-level isolation.

Think of it like securing a vault. You don't let the customer walk into the back room and look for "Box 42" (because they might sneak into the Manager's office). You have them give you a claim ticket (Allowlist). You verify the ticket matches a specific box (Canonicalization). Finally, the clerk fetching the box operates in a sealed room with no doors leading to the Manager's office (Chroot).

## ASCII Diagram
```text
[User Request] ──> GET /download?file=../../etc/passwd

[Defense Level 1: Indirect Reference (BEST)]
    Is `../../etc/passwd` an integer ID? NO. -> Reject.
    (If it was `?file=5`, it maps to `/var/www/safe/report.pdf`)

[Defense Level 2: Canonicalization (GOOD)]
    Combine: "/var/www/uploads/" + "../../etc/passwd"
    Resolve to Canonical Path: "/etc/passwd"
    Does Canonical Path start with "/var/www/uploads/"? NO. -> Reject.

[Defense Level 3: OS Isolation / Chroot (FALLBACK)]
    App tries to read /etc/passwd.
    Because the App is in a Docker container or Chroot Jail,
    its "Root" (/) is actually /var/www/jail/.
    There is no /etc/passwd inside the jail! -> File Not Found.
```

## Core Defense 1: Indirect Object References (Allowlists)
The absolute best way to prevent path traversal is to simply not use filesystem paths in your parameters.

**PHP Example:**
```php
$file_id = $_GET['id'];

// Hardcoded map (or query from a database)
$files = [
    '1' => '/var/www/html/downloads/q1_report.pdf',
    '2' => '/var/www/html/downloads/q2_report.pdf'
];

if (array_key_exists($file_id, $files)) {
    // 100% safe, user cannot manipulate the actual path
    readfile($files[$file_id]);
} else {
    http_response_code(404);
    echo "File not found.";
}
```

## Core Defense 2: Canonicalization (Strict Path Validation)
If your application allows users to upload files and then download them by name, you cannot use a hardcoded map. In this case, you must mathematically resolve the path to ensure it hasn't escaped the intended directory.

"Canonicalization" means converting a path with dots, symlinks, and encodings into its absolute, true, final state. 

**Rules:**
1. Prepend the base directory to the user input.
2. Call the OS's canonicalization function (e.g., `realpath()` in PHP, `path.resolve()` in Node, `os.path.abspath()` in Python).
3. Verify that the resulting absolute path strictly begins with the expected base directory.

**Java Example:**
```java
import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;

public class SecureDownloader {
    public File getFile(String userInput) throws Exception {
        // Define the secure base path
        Path basePath = Paths.get("/var/www/html/safe_uploads/").normalize();
        
        // Resolve the user input against the base path
        Path targetPath = basePath.resolve(userInput).normalize();
        
        // Strict prefix check!
        if (!targetPath.startsWith(basePath)) {
            throw new SecurityException("Path traversal attempt blocked!");
        }
        
        return targetPath.toFile();
    }
}
```

## Core Defense 3: OS Sandboxing (Chroot / Docker / SELinux)
Assume your application code has a bug and allows Path Traversal. You can still protect the server by restricting the application process at the operating system level.

- **Chroot:** Changes the root directory for the current running process and its children. A web server chrooted into `/var/www/jail/` literally cannot comprehend paths outside of that folder. If an attacker asks for `../../../../etc/passwd`, the server goes up to `/var/www/jail/`, hits the artificial root, and stops.
- **Containers (Docker):** Runs the application in an isolated filesystem. If an attacker traverses to `/etc/passwd`, they get the container's stripped-down password file, not the host server's.
- **SELinux / AppArmor:** Mandatory Access Control (MAC) systems that can be configured to explicitly deny the `www-data` process the ability to read `/etc/passwd`, `/proc/self/environ`, or `/var/log/apache2/`, regardless of file permissions.

**Systemd Configuration (Sandboxing a Service):**
```ini
[Service]
ExecStart=/usr/bin/my_webapp
# Prevent the application from seeing the host's /home, /root, and /run directories
ProtectHome=yes
ProtectSystem=strict
# Only allow read/write access to this specific folder
ReadWritePaths=/var/www/html/uploads/
```

## Summary Checklist for Path Traversal Defense
- [ ] Have you replaced user-controlled filenames with indirect IDs wherever possible?
- [ ] If using user-controlled filenames, are you resolving the path using a built-in canonicalization function (e.g., `realpath`)?
- [ ] Are you strictly comparing the canonicalized path against the intended base directory?
- [ ] Are you actively avoiding regex blocklists (`str_replace('../', '')`)?
- [ ] Is `allow_url_include` set to `Off` in your PHP configuration to prevent RFI?
- [ ] Is the application running in a restricted OS environment (Docker, Chroot, or AppArmor) with minimal read permissions?

## Related Notes
- [[01 - What is Path Traversal?]]
- [[05 - Local File Inclusion (LFI)]]
- [[10 - Remote File Inclusion (RFI)]]
