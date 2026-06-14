import re
with open('./Methodology and Standards/I - 42 - VAPT Reporting/05 - Severity Ratings.md', 'r', encoding='utf-8') as f:
    content = f.read()
    blocks = re.findall(r'```(?:text|ascii)?\n(.*?)```', content, re.DOTALL)
    for b in blocks:
        print("BLOCK START")
        print(b)
        print("BLOCK END")
