# -*- coding: utf-8 -*-
# @Name     : data.py
# @Date     : 2023/5/1 21:08
# @Auth     : Yu Dahai
# @Email    : yudahai@pku.edu.cn
# @Desc     :

from functools import partial

import torch
import nltk
from nltk.corpus import sentiwordnet as swn
from nltk.tag import pos_tag
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from config import nltk_path

nltk.data.path.append(nltk_path)


# Make MyDataset
class MyDataset(Dataset):
    def __init__(self, sentences, labels, method_name, model_name):
        self.sentences = sentences
        self.labels = labels
        self.method_name = method_name
        self.model_name = model_name
        dataset = list()
        index = 0
        for data in sentences:
            tokens = data.split(' ')
            labels_id = labels[index]
            index += 1
            dataset.append((tokens, labels_id))
        self._dataset = dataset

    def __getitem__(self, index):
        return self._dataset[index]

    def __len__(self):
        return len(self.sentences)


# Generate attention weights from token
def token_to_weight(tokens):
    nltk_to_sentiwordnet = {"NN": "n", "VB": "v", "JJ": "a", "RB": "r", }
    res = []
    for i in tokens:
        sentiment = []
        tags = pos_tag(i)
        for word, pos in tags:
            swn_pos = nltk_to_sentiwordnet.get(pos[:2], None)
            synsets = list(swn.senti_synsets(word.lower(), pos=swn_pos))
            if len(synsets) != 0:
                word_ = synsets[0]
                sentiment.append(word_.pos_score() + word_.neg_score() + 1)
            else:
                sentiment.append(1)
        assert len(sentiment) == len(i)
        res.append(sentiment)

    assert len(tokens) == len(res)
    return torch.tensor(res)


# Make tokens for every batch
def my_collate(batch, tokenizer):
    tokens, label_ids = map(list, zip(*batch))

    text_ids = tokenizer(tokens,
                         padding=True,
                         truncation=True,
                         max_length=320,
                         is_split_into_words=True,
                         add_special_tokens=True,
                         return_tensors='pt')

    tokens_ = [tokenizer.convert_ids_to_tokens(i) for i in text_ids['input_ids']]
    before_shape = token_to_weight(tokens_)
    # print(before_shape.size())
    attention_weights = before_shape.reshape(before_shape.size()[0], 1, before_shape.size()[1], 1)

    return text_ids, torch.tensor(label_ids), attention_weights


# Read corpus
def read_corpus(path):
    sentences, labels = [], []
    with open(path, "r", encoding="utf8") as f:
        file = f.read().split("\n")
        file = [i.split("\t") for i in file]
        for i in file:
            if len(i) == 2:
                sentences.append(i[1])
                labels.append(int(i[0]))
        return sentences, labels


# Load dataset
def load_dataset(path, tokenizer, train_batch_size, test_batch_size, model_name, method_name, workers, ratio):
    sentences, labels = read_corpus(path)
    len1 = int(len(sentences) * ratio)

    # split train_set and test_set
    tr_sen, te_sen, tr_lab, te_lab = train_test_split(sentences[:len1], labels[:len1], train_size=0.8)
    # Dataset
    train_set = MyDataset(tr_sen, tr_lab, method_name, model_name)
    test_set = MyDataset(te_sen, te_lab, method_name, model_name)
    # DataLoader
    collate_fn = partial(my_collate, tokenizer=tokenizer)

    train_loader = DataLoader(train_set, batch_size=train_batch_size, shuffle=True, num_workers=workers,
                              collate_fn=collate_fn, pin_memory=True)

    test_loader = DataLoader(test_set, batch_size=test_batch_size, shuffle=True, num_workers=workers,
                             collate_fn=collate_fn, pin_memory=True)

    return train_loader, test_loader
