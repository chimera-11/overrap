import hangul
import sys
import os

wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']
def _is_in_wordset(test_str):
    for c in list(test_str):
        if not c in wordset:
            return False
    return True

indir = sys.argv[1]
outdir = sys.argv[2]

prev_dir = os.getcwd()
for _, _, files in os.walk(indir):
    for filename in files:
        os.chdir(indir)
        with open(filename, 'r', encoding='utf8') as myfile:
            data = myfile.read()
        if _is_in_wordset(data):
            os.chdir(outdir)
            with open(filename, 'w', encoding='utf8') as outfile:
                outfile.write(data)

os.chdir(prev_dir)