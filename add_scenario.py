import sys

def add_scenario(filepath):
    scenario = sys.stdin.read()
    with open(filepath, 'r') as f:
        content = f.read()

    # Find injection point
    insert_point = content.find('## Chaining Opportunities')
    if insert_point == -1:
        insert_point = content.find('## Related Notes')
    if insert_point == -1:
        insert_point = len(content)

    new_content = content[:insert_point] + "\n## Real-World Attack Scenario\n" + scenario.strip() + "\n\n" + content[insert_point:]

    with open(filepath, 'w') as f:
        f.write(new_content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 add_scenario.py <filepath> < scenario.txt")
        sys.exit(1)
    add_scenario(sys.argv[1])
