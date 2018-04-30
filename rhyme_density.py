import hangul
import numpy as np

# a, b: 각 모음의 출현 빈도수
def similarity_score(a, b):
    #a = min(a, 3)
    #b = min(b, 3)
    return a * b

# 모음 20가지에 대해 라임 유사도 분석 실시
# 반환값: 20 x 20 upper triangular matrix
def analyze(input_str):
    vowel_count = len(hangul.joongseongs)
    rhyme_counts = np.zeros(vowel_count)
    for c in input_str:
        if not hangul.is_hangul_char(c):
            continue
        vowel = hangul.decompose_hangul(c)[1]
        index = hangul.joongseongs.index(vowel)
        rhyme_counts[index] += 1
    counts = np.zeros((vowel_count, vowel_count))
    for i in range(vowel_count):
        for j in range(i, vowel_count):
            counts[i][j] = similarity_score(rhyme_counts[i], rhyme_counts[j])
    total_count = vowel_count * (vowel_count + 1) / 2
    totals = np.ones((vowel_count, vowel_count)) * total_count
    return counts, totals

def analyze_file(filename):
    with open(filename, 'r', encoding='utf8') as myfile:
        data = myfile.readlines()

    vowel_count = len(hangul.joongseongs)
    counts = np.zeros((vowel_count, vowel_count))
    totals = np.zeros((vowel_count, vowel_count))
    for i in range(0, len(data)-1):
        counts_cur, totals_cur = analyze(data[i] + ' ' + data[i+1])
        counts += counts_cur
        totals += totals_cur
        if i % 200 == 0 or i == len(data)-1:
            print('Processed %dth line' % int(i))
    mat = counts / totals
    return mat

file_rhyme = 'corpus2\\rhyme_match.txt'
file_random = 'corpus2\\output_100000.txt'
mat_rhyme = analyze_file(file_rhyme)
mat_random = analyze_file(file_random)
odds = np.log(mat_rhyme / (mat_random + 0.000000000000001))

print(odds)
