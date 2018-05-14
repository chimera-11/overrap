from rap_word2vec import RapWord2Vec
from char_gen_base import CharGenBase
from char_gen_ngram import CharGenNgram
from char_gen_rnn import CharGenRNN
from char_gen_rnn_yangseo import CharGenRNNYangseo
import hangul_comp
import random

def remove_word_type_suffix(word):
    return word.rsplit('/', 1)[0]

rw2v = RapWord2Vec()
#chargen = CharGenRNN('crawl_hiphop')
#chargen = CharGenRNN('D:\\Dev\\School\\tmp')
#chargen = CharGenRNN('D:\\Dev\\School\\crawl_dance')
#chargen = CharGenNgram('corpus2\\output_decomp_100000.txt', 5)
#chargen = CharGenNgram('corpus2\\output_decomp_403340.txt', 6)
chargen = CharGenRNNYangseo()

def run(a, b):
    a = remove_word_type_suffix(a)
    b = remove_word_type_suffix(b)
    out_str = ''
    out_str += a + chargen.generate(a, random.randrange(5, 7))
    out_str += ' ' + b + chargen.generate(out_str + ' ' + b, 5 + random.randrange(-1, 2))
    out_str = out_str.replace('\n', ' ').replace('  ', ' ')
    out_str = hangul_comp.process_data(out_str)
    return out_str

cmd = ''

a = ''
b = ''
while True:
    if cmd == 'q':
        break
    if cmd == 'i':
        a = input('')
        b = input('')
    elif cmd == 'r':
        pass
    else:
        a, b = rw2v.generate_words(' ', ' ')
    tries = 0
    while tries < 5:
        try:
            out_str = run(a, b)
            break
        except Exception as e:
            print(e)
            tries += 1
    if tries < 5:
        print("keywords: " + a + ", " + b)
        print("generated: " + out_str)
    else:
        print("an error occurred; please tolerate for now")
    cmd = input("q=exit; i=gen from input pairs; r=replay; otherwise generate again: ")