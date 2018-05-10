import sys
import os.path

# rhyme_extract.py
# run as:
#     python rhyme_extract.py <input_file>
# for example:
#     python rhyme_extract.py crawl_1.txt

if len(sys.argv) < 2:
    raise Exception('Supply input file path')
input_file_path = sys.argv[1]
output_file_path = input_file_path + '.rhyme'

# save and restore the file pointer
def checkpoint_save(input_file_path, val):
    ckpt_file_path = input_file_path + '.ckpt'
    with open(ckpt_file_path, 'w', encoding='utf8') as fckpt:
        fckpt.write('%d' % int(val))
def checkpoint_restore(input_file_path):
    ckpt_file_path = input_file_path + '.ckpt'
    if not os.path.isfile(ckpt_file_path):
        return 0
    with open(ckpt_file_path, 'r', encoding='utf8') as fckpt:
        try:
            return int(fckpt.read())
        except:
            return 0
    

with open(input_file_path, 'r', encoding='utf8') as fin:
    with open(output_file_path, 'a', encoding='utf8') as fout:
        ptr = checkpoint_restore(input_file_path)
        if ptr > 0:
            print('restoring to file position %d' % ptr)
            fin.seek(ptr)
        line = fin.readline()
        prev_line = ''
        prev_choice = 'x'
        while line:
            line = line.replace('\r', '').replace('\n', '')
            print('[%s]' % line)
            while True:
                if prev_choice == 'x':
                    choice = input('save=1, skip=0, suspend=s: ')
                else:
                    choice = input('save=1, skip=0, twoline=2, suspend=s: ')
                if choice == '1':
                    fout.write(line + '\r\n')
                    print('saved')
                    prev_choice = choice
                    break
                elif choice == '0':
                    print('skipped')
                    prev_choice = choice
                    break
                elif prev_choice != 'x' and choice == '2':
                    fout.write(prev_line + ' ' + line + '\r\n')
                    print('twoline saved')
                    prev_choice = choice
                    break
                elif choice == 's':
                    checkpoint_save(input_file_path, ptr)
                    print('suspended at file position %d' % ptr)
                    exit()
            ptr = fin.tell()
            prev_line = line
            line = fin.readline()
