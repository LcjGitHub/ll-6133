with open('d:/lcj/0613/ll-6133/backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

count = 0
cut_index = None
for i, line in enumerate(lines):
    if '@app.get("/api/batches/export")' in line:
        count += 1
        if count == 2:
            cut_index = i
            break

if cut_index:
    start_idx = cut_index
    while start_idx > 0 and lines[start_idx - 1].strip() == '':
        start_idx -= 1

    new_lines = lines[:start_idx]
    with open('d:/lcj/0613/ll-6133/backend/main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f'Deleted from line {start_idx + 1} to end')
    print(f'Original lines: {len(lines)}, New lines: {len(new_lines)}')
else:
    print('No duplicate found')
