from rap_word2vec_180514 import RapWord2Vec180514
from char_gen_base import CharGenBase
from char_gen_ngram import CharGenNgram
from char_gen_rnn import CharGenRNN
from char_gen_rnn import CharGenRNN180514
from char_gen_rnn_yangseo import CharGenRNNYangseo
import hangul_comp
import random

# removes type suffix concatenated by text processor
# Ex> '찬란하다/Verb' --> '찬란하다'
def remove_word_type_suffix(word):
    word = str(word)
    if '/' in word:
        return word.rsplit('/', 1)[0]
    return word

class LineGen:
    def __init__(self):
        self.rw2v = RapWord2Vec180514()
        #self.chargen = CharGenRNN('crawl_hiphop')
        #self.chargen = CharGenRNN('..\\tmp')
        #self.chargen = CharGenRNN180514('..\\crawl_dance')
        self.chargen = CharGenRNN180514('crawl_dance_180514')
        #self.chargen = CharGenRNN180514('..\\crawl_balad')
        #self.chargen = CharGenRNN180514('crawl_hiphop')
        #self.chargen = CharGenNgram('..\\crawl_dance\\output_decomp.txt', 6)
        #self.chargen = CharGenNgram('corpus2\\output_decomp_100000.txt', 5)
        #self.chargen = CharGenNgram('corpus2\\output_decomp_403340.txt', 6)
        #self.chargen = CharGenRNNYangseo('RNN\\save_balad')
        #self.chargen = CharGenRNNYangseo('RNN\\save_180515')
    def generate(self, primer_text, str_len):
        out_str = primer_text + self.chargen.generate(primer_text, str_len)
        out_str = out_str.replace('\r', '').replace('\n', ' ').replace('  ', ' ')
        out_str = hangul_comp.process_data(out_str)
        return out_str
    def generate_multi(self, primer_text, str_len, count):
        pre_result = self.chargen.generate_multi(primer_text, str_len, count)
        result = []
        for line in pre_result:
            line = primer_text + line
            line = line.replace('\r', '').replace('\n', '').replace('  ', ' ')
            line = hangul_comp.process_data(line)
            result.append(line)
        return result
    def run(self, a, b):
        a = remove_word_type_suffix(a)
        b = remove_word_type_suffix(b)
        out_str = a
        out_str = self.generate(out_str, random.randrange(5, 7)) + ' ' + b
        out_str = self.generate(out_str, random.randrange(5, 7))
        return out_str
    def interactive_loop(self):
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
                a, b = self.rw2v.sample_pair()
            tries = 0
            while tries < 5:
                try:
                    out_str = self.run(a, b)
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

if __name__ == '__main__':
    lg = LineGen()
    lg.interactive_loop()