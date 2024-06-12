# -*- coding: utf-8 -*-
# @Name     : main.py
# @Date     : 2023/5/1 21:08
# @Auth     : Yu Dahai
# @Email    : yudahai@pku.edu.cn
# @Desc     :

import json
import os

import torch
import torch.nn as nn
from torchmetrics.classification import MulticlassF1Score
from tqdm import tqdm
from transformers import logging, AutoTokenizer, AutoModel

from config import logger, bert_path, roberta_path, scibert_path, device, backend, corpus_path, train_batch_size, \
    test_batch_size, workers, corpus_ratio, lr, weight_decay, num_epoch, num_classes, input_size, output_process_path, \
    model_names, method_names
from data import load_dataset
from model import FNN, GRU, BiLSTM, LSTM, RNN, TextCNN, CNN_RNN, \
    Attention, CNN_RNN_Attention
from sentibert import SentiBert


class Train:
    def __init__(self, model_name="bert", method_name="sentibert"):
        self.logger = logger
        self.micro_f1 = MulticlassF1Score( num_classes=num_classes, average="micro").to(device)
        self.macro_f1 = MulticlassF1Score( num_classes=num_classes, average="macro").to(device)

        self.model_name = model_name
        self.method_name = method_name
        self.model = None
        self.tokenizer = None
        self.DATA = None
        self.DATA_tk = None
        self.history = dict()

    def _make_model(self, model_name, method_name):
        """
        construct model
        :param model_name: pre-trained model
        :param method_name: method
        :return:
        """
        self.model_name = model_name
        self.method_name = method_name
        # self.logger.info(f"> creating model {model_name}")

        # Create model
        if model_name == "bert":
            self.tokenizer = AutoTokenizer.from_pretrained(bert_path, add_prefix_space=True)
            base_model = AutoModel.from_pretrained(bert_path)
        elif model_name == "roberta":
            self.tokenizer = AutoTokenizer.from_pretrained(roberta_path, add_prefix_space=True)
            base_model = AutoModel.from_pretrained(roberta_path)
        elif model_name == "scibert":
            self.tokenizer = AutoTokenizer.from_pretrained(scibert_path, add_prefix_space=True)
            base_model = AutoModel.from_pretrained(scibert_path)
        else:
            raise ValueError("unknown model")

        # Operate the method
        if method_name == "fnn":
            self.model = FNN(base_model, num_classes)
        elif method_name == "gru":
            self.model = GRU(base_model, num_classes, input_size)
        elif method_name == "lstm":
            self.model = LSTM(base_model, num_classes, input_size)
        elif method_name == "bilstm":
            self.model = BiLSTM(base_model, num_classes, input_size)
        elif method_name == "rnn":
            self.model = RNN(base_model, num_classes, input_size)
        elif method_name == "textcnn":
            self.model = TextCNN(base_model, num_classes)
        elif method_name == "attention":
            self.model = Attention(base_model, num_classes)
        elif method_name == "lstm+textcnn":
            self.model = CNN_RNN(base_model, num_classes)
        elif method_name == "lstm_textcnn_attention":
            self.model = CNN_RNN_Attention(base_model, num_classes)
        elif method_name == "sentibert":
            self.model = SentiBert(base_model, num_classes)
        else:
            raise ValueError("unknown method")

        self.model.to(device)
        self._print_args()

    def _print_args(self):
        """
        print arguments
        :return:
        """
        # self.logger.info("> training arguments:")
        for arg in ["device", "train_batch_size", "test_batch_size", "self.model_name",
                    "self.method_name", "corpus_ratio", "num_epoch"]:
            self.logger.info(f">>> {arg}: {eval(arg)}")

    def _train(self, dataloader, criterion, optimizer):
        train_loss, n_correct, n_train, n = 0, 0, 0, 0
        micro_f1, macro_f1 = 0, 0

        self.model.train()

        for inputs, targets, attention_weights in tqdm(dataloader, disable=backend, ascii=">="):
            inputs = {k: v.to(device) for k, v in inputs.items()}
            inputs["attention_weights"] = attention_weights.to(device)
            targets = targets.to(device)
            predicts = self.model(inputs)
            loss = criterion(predicts, targets)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * targets.size(0)
            n_correct += (torch.argmax(predicts, dim=1) == targets).sum().item()
            n_train += targets.size(0)

            n += 1
            micro_f1 += self.micro_f1(predicts, targets)
            macro_f1 += self.macro_f1(predicts, targets)

        # Guardar el modelo
        torch.save(self.model.state_dict(), "pesos_modelo.pt")

        return train_loss / n_train, n_correct / n_train, micro_f1 / n, macro_f1 / n


    def _test(self, dataloader, criterion):
        test_loss, n_correct, n_test, n = 0, 0, 0, 0
        micro_f1, macro_f1 = 0, 0
        # Turn on the eval mode
        self.model.eval()
        with torch.no_grad():
            for inputs, targets, attention_weights in tqdm(dataloader, disable=backend, ascii=">="):
                inputs = {k: v.to(device) for k, v in inputs.items()}
                inputs["attention_weights"] = attention_weights.to(device)
                targets = targets.to(device)
                predicts = self.model(inputs)
                loss = criterion(predicts, targets)

                test_loss += loss.item() * targets.size(0)
                n_correct += (torch.argmax(predicts, dim=1) == targets).sum().item()
                n_test += targets.size(0)

                n += 1
                micro_f1 += self.micro_f1(predicts, targets)
                macro_f1 += self.macro_f1(predicts, targets)

        return test_loss / n_test, n_correct / n_test, micro_f1 / n, macro_f1 / n

    def save_history(self, data_dict=None):
        """
        save history of every batch
        :param data_dict:
        :return:
        """
        name = f"{self.model_name}_{self.method_name}"
        self.history[name] = data_dict

        if not os.path.exists(output_process_path):
            os.mkdir(output_process_path)

        with open(f"{output_process_path}/{name}.json", "w+", encoding="UTF-8") as f:
            json.dump(data_dict, f)

    def _get_data(self):
        """
        get data before training
        :return:
        """
        if not self.DATA or (self.DATA_tk != self.model_name):
            self.DATA = load_dataset(
                path=corpus_path, tokenizer=self.tokenizer, train_batch_size=train_batch_size, ratio=corpus_ratio,
                test_batch_size=test_batch_size, model_name=self.model_name, method_name=self.method_name,
                workers=workers)
            self.DATA_tk = self.model_name
        return self.DATA

    def _run(self):
        """
        run the process
        :return:
        """
        train_dataloader, test_dataloader = self._get_data()

        _params = filter(lambda x: x.requires_grad, self.model.parameters())
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(_params, lr=lr, weight_decay=weight_decay)

        process_data = {
            "train_loss": [], "train_acc": [], "train_micro_f1": [], "train_macro_f1": [],
            "test_loss": [], "test_acc": [], "test_micro_f1": [], "test_macro_f1": [],
        }

        best_loss, best_acc = 0, 0
        for epoch in range(num_epoch):
            tr_loss, tr_acc, tr_f1_micro, tr_f1_macro = self._train(train_dataloader, criterion, optimizer)

            test_loss, test_acc, test_f1_micro, test_f1_macro = self._test(test_dataloader, criterion)

            process_data["train_loss"].append(tr_loss)
            process_data["train_acc"].append(tr_acc)
            process_data["train_micro_f1"].append(float(tr_f1_micro))
            process_data["train_macro_f1"].append(float(tr_f1_macro))

            process_data["test_loss"].append(test_loss)
            process_data["test_acc"].append(test_acc)
            process_data["test_micro_f1"].append(float(test_f1_micro))
            process_data["test_macro_f1"].append(float(test_f1_macro))

            if test_acc > best_acc or (test_acc == best_acc and test_loss < best_loss):
                best_acc, best_loss = test_acc, test_loss

            self.logger.info("{}/{} - {:.2f}%".format(epoch + 1, num_epoch, 100 * (epoch + 1) / num_epoch))
            self.logger.info("[train] loss: {:.4f}, acc: {:.2f}, micro f1: {:.2f},"
                             " macro f1: {:.2f}".format(tr_loss, tr_acc * 100, tr_f1_micro, tr_f1_macro))
            self.logger.info("[test] loss: {:.4f}, acc: {:.2f}, micro f1: {:.2f},"
                             " macro f1: {:.2f}".format(test_loss, test_acc * 100, test_f1_micro, test_f1_macro))

        self.logger.info("best loss: {:.4f}, best acc: {:.2f}".format(best_loss, best_acc * 100))
        self.logger.info("\n\n")
        self.save_history(process_data)

    def loop(self):
        """
        train every model+method
        :return:
        """
        for model in model_names:
            for method in method_names:
                self._make_model(model, method)
                self._run()

        with open(f"{output_process_path}/history.json", "w+", encoding="UTF-8") as f:
            json.dump(self.history, f)


if __name__ == "__main__":
    logging.set_verbosity_error()
    train = Train(model_name="bert", method_name="fnn")
    train.loop()
