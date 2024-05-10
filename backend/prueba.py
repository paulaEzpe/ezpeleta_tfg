from gensim.models import Word2Vec
from gensim.test.utils import datapath
from gensim import utils
from nltk.tokenize import word_tokenize
import nltk
import os
nltk.download('punkt')


class MyCorpus:
    """An iterator that yields tokens (lists of str) from
       all files in a directory: the corpus"""
    def init(self, dir_path):
        self.dir_path = dir_path

    def iter(self):
        for file in os.listdir(self.dir_path):
            corpus_path = datapath(os.path.join(self.dir_path, file))
            for line in open(corpus_path, encoding="utf8"):
                line = line.lower()
                #yield utils.simple_preprocess(line)
                yield word_tokenize(line,language='spanish')

    
sentences = MyCorpus('/content/quijote/corpus')

model = Word2Vec(sentences=sentences,
                    vector_size=50,
                    window=5,
                    hs=0, #0=negative sampling
                    sg=1, #1=skip-gram
                    shrink_windows=True, #draw window size from uniform [1,window]
                    negative=10,
                    ns_exponent=0.75,
                    min_count=3,
                    workers=1,
                    seed=1,
                    epochs=10)

