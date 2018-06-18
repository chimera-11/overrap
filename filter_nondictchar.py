# ---------------------------------------------
#   filter_nondictchar.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module excludes lyrics files which contain
#     non-dictionary (alphanumeric) characters.
#     When discard threshold value (between 0 and 1) is specified,
#     a text file is only copied to the destination directory
#     if it has non-dictionary characters fewer than the threshold.
# Usage:
#     python filter_nondictchar.py <src-dir> <dst-dir>
#     python filter_nondictchar.py <src-dir> <dst-dir> <discard-threshold>

import os
import sys

src_dir = sys.argv[1]
dst_dir = sys.argv[2]

orig_dir = os.getcwd()
src_dir = os.path.join(orig_dir, src_dir)
dst_dir = os.path.join(orig_dir, dst_dir)
if len(sys.argv) >= 4:
    threshold = float(sys.argv[3])
    if threshold < 0 or threshold > 1:
        raise EnvironmentError('threshold should be between 0 and 1')
else:
    threshold = -1 # indicates it is off

def isEnglishAlpha(c):
    c = ord(c)
    return (c >= ord('A') and c <= ord('Z')) or (c >= ord('a') and c <= ord('z'))
def hasAlphanumeric(inputString):
    return any((char.isdigit() or isEnglishAlpha(char)) for char in inputString)
def fractionAlphanumeric(inputString):
    if len(inputString) == 0:
        return 0.0
    an_set = [x for x in inputString if x.isdigit() or isEnglishAlpha(x)]
    return len(an_set) * 1.0 / len(inputString)

for _, _, files in os.walk(src_dir):
    for filename in files:
        if filename.endswith('.txt'):
            filepath = os.path.join(src_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as srcf:
                data = str(srcf.read())
                if threshold == -1:
                    retain = not hasAlphanumeric(data) and len(data) >= 5
                else:
                    retain = fractionAlphanumeric(data) <= threshold and len(data) >= 5
                if retain:
                    dstpath = os.path.join(dst_dir, filename)
                    data = data.replace('  ', ' ').replace(' \n', '\n').replace('\n ', '\n').replace('\n\n', '\n').strip() + '\n'
                    with open(dstpath, 'w', encoding='utf-8') as dstf:
                        dstf.write(data)
