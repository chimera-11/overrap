# Usage:
#     rd_eval_batch.py <folder-path>

import os
import sys
import rd_eval
import strutils

folder_path = sys.argv[1]

file_list = []
for _, _, files in os.walk(folder_path):
    for filename in files:
            if filename.endswith('.txt'):
                file_list.append(filename)

rd_list = []
r = rd_eval.RhymeDensityEval()

os.chdir(folder_path)
for filename in file_list:
    with open(filename, 'r', encoding='utf8') as lyrics_file:
        lines = lyrics_file.readlines()
    lines_sanitized = []
    for line in lines:
        line = strutils.normalize(line)
        if len(line) > 0:
            lines_sanitized.append(line)
    if len(lines_sanitized) <= 1:
        rd_list.append((filename, 0))
        continue
    count = 0.0
    rd_cumul = 0.0
    for i in range(len(lines_sanitized) - 1):
        line1 = lines_sanitized[i]
        line2 = lines_sanitized[i + 1]
        rd_cumul += r.eval_between(line1, line2)
        count += 1.0
    rd_list.append((filename, rd_cumul / count))

with open('rd_eval_result.csv', 'w', encoding='utf8') as eval_result:
    eval_result.write('filename, rd\n')
    for (filename, rd) in rd_list:
        eval_result.write('%s, %f\n' % (filename, rd))
