import sys
import hangul

def process_data(data):
    data_len = len(data)
    i = 0
    processed_data = []
    while i < data_len:
        if i <= data_len - 3 and hangul.is_choseong(data[i]):
            composed, composed_char = hangul.try_compose(data[i], data[i+1], data[i+2])
            if composed:
                processed_data.append(composed_char)
                i += 3
                continue
        processed_data .append(data[i])
        i += 1
    return ''.join(processed_data)

if __name__  == '__main__':
    with open(sys.argv[1], 'r', encoding='utf8') as myfile:
        read_data = myfile.read()

    processed_data = process_data(read_data)
    with open(sys.argv[2], 'w', encoding='utf8') as myfile:
        myfile.write(processed_data)