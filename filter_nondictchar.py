# ---------------------------------------------
#   filter_nondictchar.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module excludes lyrics files which contain
#     non-dictionary (alphanumeric) characters.
# Usage:
#     python filter_nondictchar.py <src-dir> <dst-dir>

import os
import sys

src_dir = sys.argv[1]
dst_dir = sys.argv[2]

orig_dir = os.getcwd()
src_dir = os.path.join(orig_dir, src_dir)
dst_dir = os.path.join(orig_dir, dst_dir)

def isEnglishAlpha(c):
    c = ord(c)
    return (c >= ord('A') and c <= ord('Z')) or (c >= ord('a') and c <= ord('z'))
def hasAlphanumeric(inputString):
    return any((char.isdigit() or isEnglishAlpha(char)) for char in inputString)

for _, _, files in os.walk(src_dir):
    for filename in files:
        if filename.endswith('.txt'):
            filepath = os.path.join(src_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as srcf:
                data = str(srcf.read())
                if not hasAlphanumeric(data) and len(data) >= 5:
                    dstpath = os.path.join(dst_dir, filename)
                    data = data.replace('  ', ' ').replace(' \n', '\n').replace('\n ', '\n').replace('\n\n', '\n').strip() + '\n'
                    with open(dstpath, 'w', encoding='utf-8') as dstf:
                        dstf.write(data)

