import sys
import hangul

with open(sys.argv[1], 'r', encoding='utf8') as myfile:
    data = myfile.read()

data_len = len(data)
i = 0
processed_data = []
while i < data_len:
    if i <= data_len - 3 and hangul.is_leading_hangul(data[i]):
        composed, composed_char = hangul.try_compose(data[i], data[i+1], data[i+2])
        if composed:
            processed_data.append(composed_char)
            i += 3
            continue
    processed_data .append(data[i])
    i += 1

with open(sys.argv[2], 'w', encoding='utf8') as myfile:
    myfile.write(''.join(processed_data))