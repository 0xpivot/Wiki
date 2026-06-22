#!/bin/bash
set -e

commit_file() {
  local file="$1"
  echo "Adding and committing: $file"
  git add "$file"
  for i in {1..10}; do
    if git commit -m "Enhance $(basename "$file")"; then
       echo "Committed $file successfully."
       return 0
    else
       echo "Git lock detected, retrying in 2 seconds..."
       sleep 2
    fi
  done
  echo "Failed to commit $file"
  return 1
}

commit_file "Command and Control Operations/I - 94 - Command and Control Foundations and Architectures/16 - Havoc C2 Framework.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/29 - POP3 (Ports 110-995) Pentesting.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/30 - IMAP (Ports 143-993) Pentesting.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/33 - ident (Port 113) Pentesting.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/34 - Echo (Port 7) Pentesting.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/37 - rlogin (Port 513) Pentesting.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/38 - rsh (Port 514) Pentesting.md"
commit_file "Network Security/A - 81 - Network Service Pentesting/78 - distcc (Port 3632) Pentesting.md"
