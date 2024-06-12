# -*- coding: utf-8 -*-
# @Name     : sentibert.py
# @Date     : 2023/5/1 21:08
# @Auth     : Yu Dahai
# @Email    : yudahai@pku.edu.cn
# @Desc     :

import copy
import math
from typing import Optional, Tuple

import torch
from torch import nn
from transformers.models.bert.modeling_bert import BertPooler, BertEncoder, BertLayer, BertAttention, \
    BertSelfAttention, BertModel


class BertEncoderCustom(BertEncoder):
    def __init__(self, config):
        super().__init__(config)
        self.layer = nn.ModuleList([BertLayerCustom(config) for _ in range(config.num_hidden_layers)])


class BertLayerCustom(BertLayer):
    def __init__(self, config):
        super().__init__(config)
        self.attention = BertAttentionCustom(config)


class BertAttentionCustom(BertAttention):
    def __init__(self, config, position_embedding_type=None):
        super().__init__(config, )
        self.self = BertSelfAttentionCustom(config, position_embedding_type=position_embedding_type)

    def forward(
            self,
            hidden_states: tuple,
            attention_mask: Optional[torch.FloatTensor] = None,
            head_mask: Optional[torch.FloatTensor] = None,
            encoder_hidden_states: Optional[torch.FloatTensor] = None,
            encoder_attention_mask: Optional[torch.FloatTensor] = None,
            past_key_value: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
            output_attentions: Optional[bool] = False,
    ) -> Tuple[torch.Tensor]:
        self_outputs = self.self(
            hidden_states,
            attention_mask,
            head_mask,
            encoder_hidden_states,
            encoder_attention_mask,
            past_key_value,
            output_attentions,
        )
        hidden_states, _ = hidden_states
        attention_output = self.output(self_outputs[0], hidden_states)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs


class BertSelfAttentionCustom(BertSelfAttention):
    def forward(self, hidden_states,
                attention_mask: Optional[torch.FloatTensor] = None,
                head_mask: Optional[torch.FloatTensor] = None,
                encoder_hidden_states: Optional[torch.FloatTensor] = None,
                encoder_attention_mask: Optional[torch.FloatTensor] = None,
                past_key_value: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
                output_attentions: Optional[bool] = False) -> Tuple[torch.Tensor]:

        hidden_states, attention_weights = hidden_states
        # print(type(hidden_states))

        mixed_query_layer = self.query(hidden_states)
        is_cross_attention = encoder_hidden_states is not None
        if is_cross_attention and past_key_value is not None:
            key_layer = past_key_value[0]
            value_layer = past_key_value[1]
            attention_mask = encoder_attention_mask
        elif is_cross_attention:
            key_layer = self.transpose_for_scores(self.key(encoder_hidden_states))
            value_layer = self.transpose_for_scores(self.value(encoder_hidden_states))
            attention_mask = encoder_attention_mask
        elif past_key_value is not None:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))
            key_layer = torch.cat([past_key_value[0], key_layer], dim=2)
            value_layer = torch.cat([past_key_value[1], value_layer], dim=2)
        else:
            key_layer = self.transpose_for_scores(self.key(hidden_states))
            value_layer = self.transpose_for_scores(self.value(hidden_states))

        query_layer = self.transpose_for_scores(mixed_query_layer)

        if self.is_decoder:
            past_key_value = (key_layer, value_layer)

        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        if self.position_embedding_type == "relative_key" or self.position_embedding_type == "relative_key_query":
            seq_length = hidden_states.size()[1]
            position_ids_l = torch.arange(seq_length, dtype=torch.long, device=hidden_states.device).view(-1, 1)
            position_ids_r = torch.arange(seq_length, dtype=torch.long, device=hidden_states.device).view(1, -1)
            distance = position_ids_l - position_ids_r
            positional_embedding = self.distance_embedding(distance + self.max_position_embeddings - 1)
            positional_embedding = positional_embedding.to(dtype=query_layer.dtype)  # fp16 compatibility
            if self.position_embedding_type == "relative_key":
                relative_position_scores = torch.einsum("bhld,lrd->bhlr", query_layer, positional_embedding)
                attention_scores = attention_scores + relative_position_scores
            elif self.position_embedding_type == "relative_key_query":
                relative_position_scores_query = torch.einsum("bhld,lrd->bhlr", query_layer, positional_embedding)
                relative_position_scores_key = torch.einsum("bhrd,lrd->bhlr", key_layer, positional_embedding)
                attention_scores = attention_scores + relative_position_scores_query + relative_position_scores_key

        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        if attention_mask is not None:
            attention_scores = attention_scores + attention_mask

        # modify attention_scores
        attention_scores = self.modify_attention_scores(attention_scores)

        attention_probs = nn.functional.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        if head_mask is not None:
            attention_probs = attention_probs * head_mask
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(new_context_layer_shape)
        outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        if self.is_decoder:
            outputs = outputs + (past_key_value,)
        return outputs

    @staticmethod
    def modify_attention_scores(attention_scores):
        return attention_scores


class SentiBert(nn.Module):
    def __init__(self, base_model, num_classes):
        super().__init__()

        self.base_model = base_model
        for param in self.base_model.parameters():
            param.requires_grad = True

        config_old = self.base_model.config
        config_new = copy.copy(config_old)
        config_new.num_hidden_layers = 1
        config_new.num_attention_heads = 1

        self.custom = BertEncoderCustom(config_new)
        self.pooler = BertPooler(config_new)
        self.dropout = nn.Dropout(config_new.hidden_dropout_prob)
        self.classifier = nn.Linear(config_new.hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, inputs):
        attention_weights = inputs["attention_weights"]
        del inputs["attention_weights"]
        outputs = self.base_model(**inputs)
        last_hidden_states = outputs[0]

        new_output = self.custom((last_hidden_states, attention_weights))[0]

        pooled_output = self.dropout(self.pooler(new_output))
        cls = self.softmax(self.classifier(pooled_output))
        return cls


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    bert_path = "D:/COURSE/dissertation/bert/model/bert-base"
    bert = BertModel.from_pretrained(bert_path).to(device=device)

    b = SentiBert(bert, 3)
    print(b)
