
import hangul
import numpy as np
from itertools import chain

default_table = [[3,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
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
        default_table[i][j] = default_table[j][i]

def huber_loss(x):
    x = max(5, x)
    x = float(x) / 10
    if x < 1:
        return x * x + 1
    else:
        return 2 * x

class RhymeDensityEval:
    def __init__(self):
        self.set_table(default_table)
    def create_empty_matrix(self):
        num_vowels = hangul.num_vowels()
        default_table = []
        for _ in range(0, num_vowels):
            default_table.append([0] * num_vowels)
        return default_table
    def set_table(self, table):
        self._table = self.create_empty_matrix()
        for i in range(0, hangul.num_vowels()):
            for j in range(0, hangul.num_vowels()):
                self._table[i][j] = table[i][j]
    def vowel_simil(self, v1, v2):
        if v1 == -1 or v2 == -1:
            return 0
        return self._table[v1][v2]
    def eval(self, line, verbose=False):
        line = line.replace(' ', '')
        if len(line) == 0:
            return 0
        vowels = hangul.convert_to_vowel_indices_nofail(line)
        V, vertices, adj = self.build_graph(line, vowels)
        total_score = self.eval_graph(V, vertices, adj, verbose=verbose) / len(line)
        return total_score
    # goal: 1> 라임도가 클수록 값이 커야 한다.
    #       2> 라임도가 비슷하면 값이 비슷해야 한다.
    def eval_between(self, line1, line2, verbose=False):
        # 1. translate to pronunciation form (TODO)
        # 2. measure rhyme
        #    note that there can be multiple evaluation criteria
        #    like vowel rhyme, consonant rhyme, character rhyme, etc
        total_score = 0
        total_score += self.eval_between_line_endings(line1, line2, verbose=verbose)
        total_score += self.eval_between_vowel_rhyme(line1, line2, verbose=verbose)
        return total_score
    def eval_between_line_endings(self, line1, line2, verbose=False):
        line1 = line1.replace(' ', '')
        line2 = line2.replace(' ', '')
        if len(line1) < 3 or len(line2) < 3:
            return 0    # too short for processing
        # 0. 전처리 작업
        # 공백으로 연결된 것은 추가하되, 그렇지 않은 것은 제거
        vowels1 = hangul.convert_to_vowel_indices_nofail(line1)
        vowels2 = hangul.convert_to_vowel_indices_nofail(line2)
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
        score_endvowel /= 120
        if verbose:
            print('score_endvowel = %f' % score_endvowel)
        return score_endvowel
    # graph_onechar: True이면 1모음 단위 매칭, False이면 2모음 단위 매칭
    def eval_between_vowel_rhyme(self, phrase1, phrase2, verbose=False, graph_onechar=False):
        total_score = 0
        phrase1 = phrase1.replace(' ', '')
        phrase2 = phrase2.replace(' ', '')
        if len(phrase1) == 0 or len(phrase2) == 0:
            return 0    # too short for processing
        # 0. 전처리 작업
        # 공백으로 연결된 것은 추가하되, 그렇지 않은 것은 제거
        vowels1 = hangul.convert_to_vowel_indices_nofail(phrase1)
        vowels2 = hangul.convert_to_vowel_indices_nofail(phrase2)
        # 2. 유사 모음군 추출 (길이 2)
        # 유사도에 따라 graph를 구축하여 connected component별로 점수를 매기는 방식
        if graph_onechar:
            V, vertices, adj = self.build_graph_between_charlevel(phrase1, phrase2, vowels1, vowels2)
        else:
            V, vertices, adj = self.build_graph_between(phrase1, phrase2, vowels1, vowels2)
        #V, vertices, adj = self.build_graph(vowels1 + vowels2)
        len_penalty = huber_loss(len(vowels1)) * huber_loss(len(vowels1))
        score_graph = self.eval_graph(V, vertices, adj, verbose=verbose) / len_penalty
        if verbose:
            print('score_graph = %f' % score_graph)
        total_score += score_graph
        # 3. 긴 라임 추출 (TODO)
        return total_score
    def build_graph(self, line, vowels):
        vertices = []
        next_index = 0
        for i in range(0, len(vowels) - 1):
            c1 = vowels[i]
            c2 = vowels[i + 1]
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
                edge_weight = sim_first + sim_second
                if line[ii:ii+2] == line[jj:jj+2]: # penalize mere repetition
                    edge_weight /= 4
                adj[i][j] = edge_weight
        return V, vertices, adj
    def build_graph_between_charlevel(self, line1, line2, vowels1, vowels2):
        vertices = []
        concat = vowels1 + vowels2
        for i in range(len(concat)):
            vertices.append([i, concat[i]])
        V = len(vertices)
        adj = np.zeros([V, V])
        for i in range(0, len(vowels1)):
            for j in range(len(vowels1), V):
                sim = self.vowel_simil(vertices[i][1], vertices[j][1])
                if sim > 0:
                    edge_weight = sim
                    adj[i][j] = adj[j][i] = edge_weight
        return V, vertices, adj
    def build_graph_between(self, line1, line2, vowels1, vowels2):
        vertices = []
        next_index = 0
        line = line1 + line2
        concat = vowels1 + vowels2
        v2_first_index = len(concat) - 1
        for i in chain(range(0, len(line1)-1), range(len(line1), len(concat)-1)):
            c1 = concat[i]
            c2 = concat[i + 1]
            if c1 == -1 or c2 == -1:
                continue
            if i >= len(vowels1):
                v2_first_index = min(v2_first_index, next_index)
            vertices.append([i, c1, c2])
            next_index += 1
        V = len(vertices)
        adj = np.zeros([V, V])
        for i in range(0, v2_first_index):
            for j in range(v2_first_index, V):
                ii = vertices[i][0]
                jj = vertices[j][0]
                sim_first = self.vowel_simil(vertices[i][1], vertices[j][1])
                sim_second = self.vowel_simil(vertices[i][2], vertices[j][2])
                if sim_first > 0 and sim_second > 0:
                    edge_weight = sim_first + sim_second
                    if line[ii:ii+2] == line[jj:jj+2]: # penalize mere repetition
                        edge_weight /= 4
                    adj[i][j] = adj[j][i] = edge_weight
        return V, vertices, adj
    def eval_graph(self, V, vertices, adj, verbose=False):
        visited = np.zeros(V)  # 0=unvisited, 1=visiting, 2=visited
        def dfs(i):
            if visited[i] != 0:
                return 0, 0
            if verbose and len(vertices[i]) >= 3:
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
            if verbose and len(vertices[i]) >= 3:
                print('leave %d %s %s' % (i, hangul.joongseongs[vertices[i][1]], hangul.joongseongs[vertices[i][2]]))
                print('  with weight_sum = %.3f, node_count = %d' % (weight_sum, node_count))
            return weight_sum, node_count
        score_graph = 0
        for i in range(0, V):
            weight_sum, node_count = dfs(i)
            if node_count > 1:
                score_graph += np.power(weight_sum, 0.7) + node_count
        return score_graph

if __name__  == '__main__':
    r = RhymeDensityEval()
    while True:
        s1 = input()
        s2 = input()
        v = r.eval_between(s1, s2, verbose=True)
        print(v)
    #r.eval('너와 나의 연결고리', '808 베이스 소리')