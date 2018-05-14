# ---------------------------------------------
#   rnn_lyrics_gen_180514.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module generates word pairs by using
#     both word2vec and rhyme density.
# Notes:
#     The suffix '180514' indicates the major revision date.

import gensim
import random
import rd_eval
import mathutils
import numpy as np

def load_word2vec_model(path):
    model = gensim.models.word2vec.Word2Vec()
    return model.wv.load(path)
# expects list of (id, score) pairs with zero-based ids
# the one with the highest score will be ranked highest (=1)
def score_to_rankings(pairs):
    rank_sorted = []
    for id, _ in sorted(pairs, key=lambda x: x[1], reverse=True):
        rank_sorted.append(id)
    rankings = np.zeros(len(rank_sorted))
    for i in range(len(rank_sorted)):
        rankings[rank_sorted[i]] = i
    return rankings

class RapWord2Vec180514:
    def __init__(self, scope=30):
        self.scope = scope
        self.model = load_word2vec_model('model_word2vec\\model_phrase\\model_phrase_token')
        self.rd_evaler = rd_eval.RhymeDensityEval()
        self.vocab = []
        for x in self.model.wv.vocab:
            self.vocab.append(x)
    # utility functions
    def is_vocab(self, word, model):
        return word in self.vocab
    def random_vocab(self):
        return random.choice(self.vocab)
    # external interface functions
    def sample_pair(self):
        w1 = self.random_vocab()
        # bake up candidates
        w2_cands = [x[0] for x in self.model.most_similar(w1)]
        meaning_scores = []
        rhyme_scores = []
        # score the candidates
        for i in range(len(w2_cands)):
            w2_cand = w2_cands[i]
            meaning_scores.append(self.model.similarity(w1, w2_cand))
            rhyme_scores.append((i, self.rd_evaler.eval_between_vowel_rhyme(
                w1, w2_cand,
                graph_onechar=True)))
        # evaluate single-dimension score by combining the two
        # note that meaning score is used as-is, while rhyme score is
        # converted to rankings
        # * we negate ranking here because better ones rank lower
        score_sum = np.array(meaning_scores) + (-1) * score_to_rankings(rhyme_scores)
        # compute softmax probability within limited window
        final_cand_len = min(1 + self.scope // 4, 5)
        final_cand_list = []
        for i in range(len(score_sum)):
            final_cand_list.append((i, score_sum[i]))
        final_cand_list = sorted(final_cand_list, key=lambda x: x[1], reverse=True)
        final_cand_weights = [x[1] for x in final_cand_list[0:final_cand_len]]
        prob = mathutils.softmax(final_cand_weights)
        # return the one by sampling
        best_id_indirect = np.random.choice(range(final_cand_len), p=prob)
        best_id = final_cand_list[best_id_indirect][0]
        return w1, w2_cands[best_id]
