# ---------------------------------------------
#   rd_join.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module rranges multiple lines so that.
#     adjacent lines are maximally rhyme-paired
# Usage:
#     python rd_join.py <input_file_name>
# Notes:
#     as we use TSP-based rhyme selection (=> brute force),
#     the maximum number of lines that can be configured
#     is limited to 15 lines.

import numpy as np
import sys

import rd_eval

VMAX = 20

# read the file
is_interactive = '--interactive' in sys.argv
if is_interactive:
    lines = []
    while len(lines) < VMAX:
        line = input('Press "q" to start arrangement; otherwise type next line\r\n')
        if line == 'q':
            break
        if len(line) > 0:
            lines.append(line)
else:
    filename = sys.argv[1]
    with open(filename, mode='r', encoding='utf-8-sig') as fp:
        lines = str(fp.read()).split('\n')
        lines = list(filter(None, lines))

# ensure the number of lines is within our range
V = len(lines)
if V == 0:
    if is_interactive:
        raise RuntimeError('No valid lines entered; quitting')
    else:
        raise RuntimeError('Input file %s does not have valid lines' % filename)
if V > VMAX:
    print('Input file exceeds the maximum number of lines supported; truncating to %d lines' % VMAX)
    lines = lines[0:VMAX]

# construct the rhyme density graph
V = len(lines)
adj = np.zeros([V, V])
r = rd_eval.RhymeDensityEval()
for i, j in np.ndindex(np.shape(adj)):
    if i == j:
        continue
    adj[i][j] = r.eval_between(lines[i], lines[j])

# solve TSP
valid = np.zeros([V, 1 << V])
DP = np.zeros([V, 1 << V]) # DP[node][unvisited] = node에서 시작하여 unvisited의 node들을 모두 방문할 때의 최대 경로 길이
def solve_TSP(node, unvisited):
    if unvisited == 0:
        return 0
    if valid[node][unvisited] == 1:
        return DP[node][unvisited]
    dist_max = 0
    for v in range(0, V):
        bitmask = 1 << v
        if (unvisited & bitmask) != 0:
            dist_max = max(dist_max, adj[node][v] + solve_TSP(v, unvisited & ~bitmask))
    DP[node][unvisited] = dist_max
    valid[node][unvisited] = 1
    return dist_max
def starting_bitmask(starting_node):
    v = starting_node
    return ((1 << V) - 1) & ~(1 << v)

best = [0, 0]
for v in range(0, V):
    dist_max = solve_TSP(v, starting_bitmask(v))
    if dist_max > best[1]:
        best = [v, dist_max]

# backtrack
starting_node = best[0]
best_seq = [starting_node]
unvisited = starting_bitmask(starting_node) 
while len(best_seq) < V:
    prev_node = best_seq[-1]
    best = [0, 0]
    for v in range(0, V):
        bitmask = 1 << v
        if (unvisited & bitmask) != 0:
            dist = adj[prev_node][v] + DP[v][unvisited & ~bitmask]
            if dist > best[1]:
                best = [v, dist]
    next_node = best[0]
    best_seq.append(next_node)
    unvisited &= ~(1 << next_node)

# print the result
ordered_lines = []
for i in range(0, V):
    seq_index = best_seq[i]
    ordered_lines.append(lines[seq_index])
for line in ordered_lines:
    print(line)
