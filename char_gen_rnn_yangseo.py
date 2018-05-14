from char_gen_base import CharGenBase
from RNN.sample import Sampler

class CharGenRNNYangseo(CharGenBase):
    def __init__(self, model_path=None):
        if model_path is None:
            self.sampler = Sampler()
        else:
            self.sampler = Sampler(model_path=str(model_path))
    def generate(self, input_str, out_len):
        self.sampler.set_prime_text(input_str)
        return self.sampler.sample(out_len, return_prefix_prime=False)