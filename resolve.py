import os

filepath = r"c:\Users\Asus\Desktop\AETRIX 2026'\frontend\src\components\MapView.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_head = False
for line in lines:
    if line.startswith('<<<<<<< HEAD'):
        in_head = True
    elif line.startswith('======='):
        in_head = False
    elif line.startswith('>>>>>>>'):
        pass
    else:
        if not in_head:
            new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
