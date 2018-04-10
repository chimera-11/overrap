import hangul
import numpy as np

# a, b: 각 모음의 출현 빈도수
def similarity_score(a, b):
    a = min(a, 3)
    b = min(b, 3)
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
    mat = np.zeros((vowel_count, vowel_count))
    for i in range(vowel_count):
        for j in range(i, vowel_count):
            mat[i][j] = similarity_score(rhyme_counts[i], rhyme_counts[j])
    return mat

#filename = 'corpus2\\rhyme_match.txt'
filename = 'corpus2\\output_100000.txt'
with open(filename, 'r', encoding='utf8') as myfile:
    data = myfile.readlines()

vowel_count = len(hangul.joongseongs)
mat = np.zeros((vowel_count, vowel_count))
for i in range(0, len(data)-1):
    mat += analyze(data[i] + ' ' + data[i+1])
    if i % 100 == 0:
        print('Processed %dth line' % int(i))

print(mat)