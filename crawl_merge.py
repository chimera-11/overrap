import glob

lines = []
for filename in glob.glob('test*.txt'):
    with open(filename, 'r', encoding='utf8') as myfile:
        line = myfile.readline()
        while line:
            line = line.strip()
            if not str.isdigit(line) and len(line) > 0:
                lines.append(line)
            #input('current line:' + line)
            line = myfile.readline()

with open("output.txt", 'w', encoding='utf8') as myfile:
    myfile.writelines('\n'.join(lines))

# 한글유니코드값 = 0xAC00 + ( (초성순서 * 21) + 중성순서 ) * 28 + 종성순서

