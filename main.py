from rap_word2vec import RapWord2Vec
from char_gen_base import CharGenBase
from char_gen_ngram import CharGenNgram
from char_gen_rnn import CharGenRNN

def remove_word_type_suffix(word):
    return word.rsplit('/', 1)[0]

rw2v = RapWord2Vec()
#chargen = CharGenRNN('crawl_hiphop')
chargen = CharGenNgram('corpus2\output_decomp_100000.txt', 10)

a, b = rw2v.generate_words(' ', ' ')
a = remove_word_type_suffix(a)
b = remove_word_type_suffix(b)
print(a + ", " + b)
out_str = ''
out_str += a + chargen.generate(a, 5)
out_str += b + chargen.generate(b, 5)
print(out_str)
