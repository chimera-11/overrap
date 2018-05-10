
import hangul
import numpy as np

class RhymeDensityEval:
    def create_empty_matrix(self):
        num_vowels = hangul.num_vowels()
        table = []
        for _ in range(0, num_vowels):
            table.append([0] * num_vowels)
        return table
    def set_table(self, table):
        self._table = self.create_empty_matrix()
        for i in range(0, hangul.num_vowels()):
            for j in range(0, hangul.num_vowels()):
                self._table[i][j] = table[i][j]
    def vowel_simil(self, v1, v2):
        if v1 == -1 or v2 == -1:
            return 0
        return self._table[v1][v2]
    # goal: 1> 라임도가 클수록 값이 커야 한다.
    #       2> 라임도가 비슷하면 값이 비슷해야 한다.
    def eval(self, line1, line2):
        # 1. translate to pronunciation form (TODO)
        # 2. measure rhyme
        #    note that there can be multiple evaluation criteria
        #    like vowel rhyme, consonant rhyme, character rhyme, etc
        total_score = 0
        total_score += self.eval_vowel_rhyme(line1, line2)
        return total_score
    def eval_vowel_rhyme(self, line1, line2):
        if len(line1) < 3 or len(line2) < 3:
            return 0    # too short for processing
        total_score = 0
        # 0. 전처리 작업
        # 공백으로 연결된 것은 추가하되, 그렇지 않은 것은 제거
        vowels1 = hangul.convert_to_vowel_indices_nofail(line1.replace(' ', ''))
        vowels2 = hangul.convert_to_vowel_indices_nofail(line2.replace(' ', ''))
        # 1. 말단 모음 유사성 비교
        score1 = self.vowel_simil(vowels1[-3], vowels2[-3])
        score2 = self.vowel_simil(vowels1[-2], vowels2[-2])
        score3 = self.vowel_simil(vowels1[-1], vowels2[-1])
        score_endvowel = 0
        if score3 >= 1:
            score_endvowel += score3
            if score2 >= 1:
                score_endvowel += score2 / 1.3
                if score1 >= 1:
                    score_endvowel += score1 / 1.6
        print('score_endvowel = %f' % score_endvowel)
        total_score += score_endvowel
        # 2. 유사 모음군 추출 (길이 2)
        # 유사도에 따라 graph를 구축하여 connected component별로 점수를 매기는 방식
        vertices = []
        next_index = 0
        concat = vowels1 + vowels2
        for i in range(0, len(concat) - 1):
            c1 = concat[i]
            c2 = concat[i + 1]
            if c1 == -1 or c2 == -1:
                continue
            vertices.append([i, c1, c2])
            next_index += 1
        V = len(vertices)
        adj = np.zeros([V, V])
        for i, j in np.ndindex(V, V):
            ii = vertices[i][0]
            jj = vertices[j][0]
            if np.abs(ii - jj) <= 2:
                continue # overlapping or adjacent vowel group
            sim_first = self.vowel_simil(vertices[i][1], vertices[j][1])
            sim_second = self.vowel_simil(vertices[i][2], vertices[j][2])
            if sim_first > 0 and sim_second > 0:
                adj[i][j] = sim_first + sim_second
        visited = np.zeros(V)  # 0=unvisited, 1=visiting, 2=visited
        def dfs(i):
            if visited[i] != 0:
                return 0, 0
            print('enter %d %s %s' % (i, hangul.joongseongs[vertices[i][1]], hangul.joongseongs[vertices[i][2]]))
            visited[i] = 1
            weight_sum = 0
            node_count = 1
            for j in range(0, V):
                if adj[i][j] != 0 and visited[j] == 0:
                    _w, _n = dfs(j)
                    weight_sum += _w
                    node_count += _n
                weight_sum += adj[i][j]
            visited[i] = 2
            print('leave %d %s %s' % (i, hangul.joongseongs[vertices[i][1]], hangul.joongseongs[vertices[i][2]]))
            print('  with weight_sum = %d, node_count = %d' % (weight_sum, node_count))
            return weight_sum, node_count
        score_graph = 0
        for i in range(0, V):
            weight_sum, node_count = dfs(i)
            if node_count > 1:
                score_graph += weight_sum + node_count
        print('score_graph = %f' % score_graph)
        total_score += score_graph
        # 3. 긴 라임 추출 (TODO)
        return total_score

table = [[3,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,3,0,2,0,2,0,2,0,0,1,0,0,0,0,2,0,0,0,0,0],
[0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,3,0,2,0,2,0,0,2,0,0,0,0,2,0,0,0,0,0],
[0,0,0,0,3,0,2,0,0,0,0,0,0,0,2,0,0,0,0,0,0],
[0,0,0,0,0,3,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,3,0,0,1,0,0,0,0,1,0,0,0,0,0],
[0,0,0,0,0,0,0,0,3,0,0,0,2,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,3,2,0,0,0,2,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,2,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,2,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,2,2],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,2],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3]]

for i, j in np.ndindex(21, 21):
    if i > j:
        table[i][j] = table[j][i]

r = RhymeDensityEval()
r.set_table(table)
while True:
    s1 = input()
    s2 = input()
    v = r.eval(s1, s2)
    print(v)
#r.eval('너와 나의 연결고리', '808 베이스 소리')