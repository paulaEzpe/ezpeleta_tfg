# -*- coding: utf-8 -*-
# @Name     : model.py
# @Date     : 2023/5/1 21:08
# @Auth     : Yu Dahai
# @Email    : yudahai@pku.edu.cn
# @Desc     :

import math

import torch
import torch.nn.functional as F
from torch import nn


class FNN(nn.Module):
    def __init__(self, base_model, num_classes):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes

        self.linear = nn.Linear(base_model.config.hidden_size, num_classes)
        self.dropout = nn.Dropout(0.5)
        self.softmax = nn.Softmax(dim=1)
        for param in base_model.parameters():
            param.requires_grad = True

    def forward(self, inputs):
        raw_outputs = self.base_model(**inputs)
        cls_feats = raw_outputs.last_hidden_state[:, 0, :]
        predicts = self.softmax(self.linear(self.dropout(cls_feats)))
        return predicts



class GRU(nn.Module):
    def __init__(self, base_model, num_classes, input_size):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        self.input_size = input_size
        self.Gru = nn.GRU(input_size=self.input_size,
                          hidden_size=320,
                          num_layers=1,
                          batch_first=True)
        self.fc = nn.Sequential(nn.Dropout(0.5),
                                nn.Linear(320, 80),
                                nn.Linear(80, 20),
                                nn.Linear(20, self.num_classes),
                                nn.Softmax(dim=1))
        for param in base_model.parameters():
            param.requires_grad = True

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        tokens = raw_outputs.last_hidden_state

        gru_output, _ = self.Gru(tokens)
        outputs = gru_output[:, -1, :]
        outputs = self.fc(outputs)
        return outputs


class LSTM(nn.Module):
    def __init__(self, base_model, num_classes, input_size):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        self.input_size = input_size
        self.Lstm = nn.LSTM(input_size=self.input_size,
                            hidden_size=320,
                            num_layers=1,
                            batch_first=True)
        self.fc = nn.Sequential(nn.Dropout(0.5),
                                nn.Linear(320, 80),
                                nn.Linear(80, 20),
                                nn.Linear(20, self.num_classes),
                                nn.Softmax(dim=1))
        for param in base_model.parameters():
            param.requires_grad = True

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        tokens = raw_outputs.last_hidden_state
        lstm_output, _ = self.Lstm(tokens)
        outputs = lstm_output[:, -1, :]
        outputs = self.fc(outputs)
        return outputs


class BiLSTM(nn.Module):
    def __init__(self, base_model, num_classes, input_size):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        self.input_size = input_size
        # Open the bidirectional
        self.BiLstm = nn.LSTM(input_size=self.input_size,
                              hidden_size=320,
                              num_layers=1,
                              batch_first=True,
                              bidirectional=True)
        self.fc = nn.Sequential(nn.Dropout(0.5),
                                nn.Linear(320 * 2, 80),
                                nn.Linear(80, 20),
                                nn.Linear(20, self.num_classes),
                                nn.Softmax(dim=1))
        for param in base_model.parameters():
            param.requires_grad = True

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        cls_feats = raw_outputs.last_hidden_state
        outputs, _ = self.BiLstm(cls_feats)
        outputs = outputs[:, -1, :]
        outputs = self.fc(outputs)
        return outputs


class RNN(nn.Module):
    def __init__(self, base_model, num_classes, input_size):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        self.input_size = input_size
        self.Rnn = nn.RNN(input_size=self.input_size,
                          hidden_size=320,
                          num_layers=1,
                          batch_first=True)
        self.fc = nn.Sequential(nn.Dropout(0.5),
                                nn.Linear(320, 80),
                                nn.Linear(80, 20),
                                nn.Linear(20, self.num_classes),
                                nn.Softmax(dim=1))
        for param in base_model.parameters():
            param.requires_grad = True

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        cls_feats = raw_outputs.last_hidden_state
        outputs, _ = self.Rnn(cls_feats)
        outputs = outputs[:, -1, :]
        outputs = self.fc(outputs)
        return outputs


class TextCNN(nn.Module):
    def __init__(self, base_model, num_classes):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        for param in base_model.parameters():
            param.requires_grad = True

        # Define the hyperparameters
        self.filter_sizes = [2, 3, 4]
        self.num_filters = 2
        self.encode_layer = 12

        # TextCNN
        self.convs = nn.ModuleList(
            [nn.Conv2d(in_channels=1, out_channels=self.num_filters,
                       kernel_size=(K, self.base_model.config.hidden_size)) for K in self.filter_sizes]
        )
        self.block = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(self.num_filters * len(self.filter_sizes), self.num_classes),
            nn.Softmax(dim=1)
        )

    def conv_pool(self, tokens, conv):
        tokens = conv(tokens)
        tokens = F.relu(tokens)
        tokens = tokens.squeeze(3)
        tokens = F.max_pool1d(tokens, tokens.size(2))
        out = tokens.squeeze(2)
        return out

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        tokens = raw_outputs.last_hidden_state.unsqueeze(1)
        out = torch.cat([self.conv_pool(tokens, conv) for conv in self.convs],
                        1)
        predicts = self.block(out)
        return predicts


class Attention(nn.Module):
    def __init__(self, base_model, num_classes):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        hidden_size = self.base_model.config.hidden_size
        for param in base_model.parameters():
            param.requires_grad = True
        # Self-Attention
        self.key_layer = nn.Linear(hidden_size, hidden_size)
        self.query_layer = nn.Linear(hidden_size, hidden_size)
        self.value_layer = nn.Linear(hidden_size, hidden_size)

        self._norm_fact = 1 / math.sqrt(hidden_size)

        self.block = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(768, 128),
            nn.Linear(128, 16),
            nn.Linear(16, num_classes),
            nn.Softmax(dim=1)
        )

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        tokens = raw_outputs.last_hidden_state

        K = self.key_layer(tokens)
        Q = self.query_layer(tokens)
        V = self.value_layer(tokens)

        attention = nn.Softmax(dim=-1)((torch.bmm(Q, K.permute(0, 2, 1))) * self._norm_fact)
        attention_output = torch.bmm(attention, V)
        attention_output = torch.mean(attention_output, dim=1)
        predicts = self.block(attention_output)

        return predicts


class CNN_RNN(nn.Module):
    def __init__(self, base_model, num_classes):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        for param in base_model.parameters():
            param.requires_grad = (True)

        # Define the hyperparameters
        self.filter_sizes = [3, 4, 5]
        self.num_filters = 100

        # TextCNN
        self.convs = nn.ModuleList(
            [nn.Conv2d(in_channels=1, out_channels=self.num_filters,
                       kernel_size=(K, self.base_model.config.hidden_size)) for K in self.filter_sizes]
        )

        # LSTM
        self.lstm = nn.LSTM(input_size=self.base_model.config.hidden_size,
                            hidden_size=512,
                            num_layers=1,
                            batch_first=True)

        self.block = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(812, 128),
            nn.Linear(128, 16),
            nn.Linear(16, num_classes),
            nn.Softmax(dim=1)
        )

    def conv_pool(self, tokens, conv):
        # x -> [batch,1,text_length,768]
        tokens = conv(tokens)  # shape [batch_size, out_channels, x.shape[2] - conv.kernel_size[0] + 1, 1]
        tokens = F.relu(tokens)
        tokens = tokens.squeeze(3)  # shape [batch_size, out_channels, x.shape[2] - conv.kernel_size[0] + 1]
        tokens = F.max_pool1d(tokens, tokens.size(2))  # shape[batch, out_channels, 1]
        out = tokens.squeeze(2)  # shape[batch, out_channels]
        return out

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        cnn_tokens = raw_outputs.last_hidden_state.unsqueeze(1)  # shape [batch_size, 1, max_len, hidden_size]
        cnn_out = torch.cat([self.conv_pool(cnn_tokens, conv) for conv in self.convs],
                            1)  # shape  [batch_size, self.num_filters * len(self.filter_sizes]
        rnn_tokens = raw_outputs.last_hidden_state
        rnn_outputs, _ = self.lstm(rnn_tokens)
        rnn_out = rnn_outputs[:, -1, :]
        # cnn_out --> [batch,300]
        # rnn_out --> [batch,512]
        out = torch.cat((cnn_out, rnn_out), 1)
        predicts = self.block(out)
        return predicts


class CNN_RNN_Attention(nn.Module):
    def __init__(self, base_model, num_classes):
        super().__init__()
        self.base_model = base_model
        self.num_classes = num_classes
        for param in base_model.parameters():
            param.requires_grad = (True)

        # Define the hyperparameters
        self.filter_sizes = [3, 4, 5]
        self.num_filters = 100

        # TextCNN
        self.convs = nn.ModuleList(
            [nn.Conv2d(in_channels=1, out_channels=self.num_filters,
                       kernel_size=(K, self.base_model.config.hidden_size)) for K in self.filter_sizes]
        )

        # LSTM
        self.lstm = nn.LSTM(input_size=self.base_model.config.hidden_size,
                            hidden_size=512,
                            num_layers=1,
                            batch_first=True)
        # Self-Attention
        self.key_layer = nn.Linear(self.base_model.config.hidden_size, self.base_model.config.hidden_size)
        self.query_layer = nn.Linear(self.base_model.config.hidden_size, self.base_model.config.hidden_size)
        self.value_layer = nn.Linear(self.base_model.config.hidden_size, self.base_model.config.hidden_size)
        self._norm_fact = 1 / math.sqrt(self.base_model.config.hidden_size)

        self.block = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(812, 128),
            nn.Linear(128, 16),
            nn.Linear(16, num_classes),
            nn.Softmax(dim=1)
        )

    def conv_pool(self, tokens, conv):
        # x -> [batch,1,text_length,768]
        tokens = conv(tokens)  # shape [batch_size, out_channels, x.shape[2] - conv.kernel_size[0] + 1, 1]
        tokens = F.relu(tokens)
        tokens = tokens.squeeze(3)  # shape [batch_size, out_channels, x.shape[2] - conv.kernel_size[0] + 1]
        tokens = F.max_pool1d(tokens, tokens.size(2))  # shape[batch, out_channels, 1]
        out = tokens.squeeze(2)  # shape[batch, out_channels]
        return out

    def forward(self, inputs):
        del inputs['attention_weights']
        raw_outputs = self.base_model(**inputs)
        tokens = raw_outputs.last_hidden_state
        # Self-Attention
        K = self.key_layer(tokens)
        Q = self.query_layer(tokens)
        V = self.value_layer(tokens)
        attention = nn.Softmax(dim=-1)((torch.bmm(Q, K.permute(0, 2, 1))) * self._norm_fact)
        attention_output = torch.bmm(attention, V)

        # TextCNN
        cnn_tokens = attention_output.unsqueeze(1)  # shape [batch_size, 1, max_len, hidden_size]
        cnn_out = torch.cat([self.conv_pool(cnn_tokens, conv) for conv in self.convs],
                            1)  # shape  [batch_size, self.num_filters * len(self.filter_sizes]

        rnn_tokens = tokens
        rnn_outputs, _ = self.lstm(rnn_tokens)
        rnn_out = rnn_outputs[:, -1, :]
        # cnn_out --> [batch,300]
        # rnn_out --> [batch,512]
        out = torch.cat((cnn_out, rnn_out), 1)
        predicts = self.block(out)
        return predicts
