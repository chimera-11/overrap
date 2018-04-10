from char_gen_base import CharGenBase
from ngram import Ngram
import hangul_decomp

class CharGenNgram(CharGenBase):
    def __init__(self, input_file, order):
        self.ngram = Ngram()
        self.ngram.train_char_lm(input_file, order)
    def generate(self, input_str, out_len):
        return self.ngram.generate_text(self.ngram.order, list(hangul_decomp.process_data(input_str)), out_len)