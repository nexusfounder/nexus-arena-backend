import os
import re

app_dir = 'app'
sql_issues = []

for root, _, files in os.walk(app_dir):
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            with open(fpath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            for idx, line in enumerate(lines):
                # Search for cursor.execute or conn.execute with formatted strings
                if re.search(r'execute\s*\(\s*f["\']', line) or re.search(r'execute\s*\([^,)]*\+', line) or re.search(r'execute\s*\(.*%\s*\(', line):
                    sql_issues.append((fpath, idx + 1, line.strip()))

print(f"Found {len(sql_issues)} potential SQL injection locations:")
for path, line_no, content in sql_issues:
    print(f"{path}:{line_no} -> {content}")
