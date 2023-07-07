file = open("dataset.txt", "r", encoding="utf8")
out = open('freq.txt', 'w', encoding='utf8')
for line in file:
    temp_line = line.replace('\n', '')
    temp_line += ',1\n'
    out.write(temp_line)
out.close()
file.close()