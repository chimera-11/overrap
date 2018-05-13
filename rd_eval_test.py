import rd_eval
import os
import sys

data_src_path = sys.argv[1]
r = rd_eval.RhymeDensityEval()

file_list = []
for _, _, files in os.walk(data_src_path):
    for filename in files:
            if filename.endswith('.txt'):
                file_list.append(filename)

prev_cwd = os.getcwd()
os.chdir(data_src_path)
with open('rhyme_summary_duet.csv', 'w', encoding='utf-8-sig') as csvout:
    for filename in file_list:
        with open(filename, 'r', encoding='utf8') as lyrics_file:
            lines = lyrics_file.readlines()
        if len(lines) == 0:
            continue
        rhyme_score = 0
        for i in range(0, len(lines) - 1):
            line1 = lines[i][:-1]
            line2 = lines[i+1][:-1]
            rhyme_score = r.eval_between(line1, line2)
            csvout.write('%.3f, %s, %s\n' % (rhyme_score, line1, line2))
        #for line in lines:
            #line = line.replace('\n', '')
            #rhyme_score += r.eval(line) / len(lines)
            #csvout.write('%.3f, %s\n' % (rhyme_score, line))
        #csvout.write('%.3f, %s\n' % (rhyme_score, filename))

os.chdir(prev_cwd)
