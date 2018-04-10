# decomposition of Hangul characters into two or three parts

import sys
import hangul

def process_data(data):
    processed_data = []
    for c in data:
        if hangul.is_hangul_char(c):
            processed_data.append(hangul.decompose_hangul(c))
        else:
            processed_data.append(c)
        #input(processed_data)
    return ''.join(processed_data)

if __name__  == '__main__':
    with open(sys.argv[1], 'r', encoding='utf8') as myfile:
        read_data = myfile.read()

    processed_data = process_data(read_data)
    with open(sys.argv[2], 'w', encoding='utf8') as myfile:
        myfile.write(processed_data)