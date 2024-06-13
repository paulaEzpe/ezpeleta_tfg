# -*- coding: utf-8 -*-
# @Name     : config.py
# @Date     : 2023/5/1 21:05
# @Auth     : Yu Dahai
# @Email    : yudahai@pku.edu.cn
# @Desc     :

import logging
import os
import sys
from datetime import datetime

import torch

# featurize dataset download e5ab6077-7bd1-4720-9d3f-643387086572
# pip install nltk transformers torchmetrics
"""Path"""
corpus_ratio = 1
output_process_path = "output"
nltk_path = "/home/featurize/data/nltk_data"

# corpus_path = "D:/COURSE/dissertation/visualization/dissertation/data/corpus2.txt"
# bert_path = "D:/COURSE/dissertation/bert/model/bert-base"
# roberta_path = "D:/COURSE/dissertation/bert/model/roberta-base"
# scibert_path = "D:/COURSE/dissertation/bert/model/scibert"

corpus_path = "corpus.txt"
bert_path = "/home/featurize/data/bert-base"
roberta_path = "/home/featurize/data/roberta-base"
scibert_path = "allenai/scibert_scivocab_uncased"

"""Base"""
num_classes = 3  # Positive, Negative and Neutral
input_size = 768  # default input size

# model_names = ["bert", "roberta", "scibert"]
model_names = ["scibert"]

# method_names = ["fnn"]
method_names = ["sentibert"]

"""Optimization"""
train_batch_size = 32
test_batch_size = 64
num_epoch = 50
lr = 5e-6  # learning rate
weight_decay = 0.01

"""Environment"""
device = "cuda" if torch.cuda.is_available() else "cpu"
backend = False
workers = 0

"""logger"""
log_path = f"logs"
log_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
os.mkdir(log_path) if not os.path.exists(log_path) else None
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(f"{log_path}/{log_name}"))
