'''
 Adapted and extended from 
 https://github.com/huggingface/transformers/issues/1950#issuecomment-558679189

'''
#Usando transformers y BERT

import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
#----------------------------------------------------------
def get_sentence_similarity(tokenizer,model,s1,s2):

    s1 = tokenizer.encode(s1)  
    s2 = tokenizer.encode(s2)

    #print("1 len(s1) s1",len(s1),s1) # #prints length of tokens - input_ids 8 [101, 7592...
    #print("1 len(s2) s2",len(s2),s2)
    s1 = torch.tensor(s1)
    ##print("2",s1) # #prints tensor([ 101, 7592, ...
    s1 = s1.unsqueeze(0) # add an extra dimension, why ? the model needs to be fed in batches, we give a dummy batch 1
    ##print("3",s1) # #prints tensor([[ 101, 7592, 
    s2 = torch.tensor(s2).unsqueeze(0)

    # Pass it to the model for inference
    with torch.no_grad():
        output_1 = model(s1)
        output_2 = model(s2)

    logits_s1 = output_1[0]  # The last hidden-state is the first element of the output tuple
    logits_s2 = output_2[0].detach()
    ##print("logits_s1 before detach",logits_s1) # #prints  tensor([[[-0.1162,  0.2388, ...-0.2128]]], grad_fn=<NativeLayerNormBackward0>)
    logits_s1 = logits_s1.detach() # to remove the last part we call detach

    #print("logits_s1.shape",logits_s1.shape ) # #prints ([1, <length of tokens>, 768]) - Each token is rep by a 768 row vector for the base Bert Model!
    #print("logits_s2.shape",logits_s2.shape ) # 1 the dummy batch dimension we added to the model by un-squeeze
    logits_s1 = torch.squeeze(logits_s1) #lets remove the batch dimension by squeeze
    logits_s2 = torch.squeeze(logits_s2)
    #print("logits_s1.shape",logits_s1.shape ) # #prints ([<length of tokens>, 768]) say torch.Size([8, 768])
    #print("logits_s2.shape",logits_s2.shape )
    a = logits_s1.reshape(1,logits_s1.numel()) # we lay the vector flat make it 1, **768 via reshape; numel is number of elements
    b = logits_s2.reshape(1,logits_s2.numel())
    #print("a.shape",a.shape ) # torch.Size([1, 6144])
    #print("b.shape",b.shape ) # the shape will be 1, 768* no of tokens in b sentence - need not be similar

    # we can  mean over the rows to give it better similarity - but that is giving poor output
    # a = sentence_vector_1.mean(axis=1) this is giving cosine similarity as 1
    # b = sentence_vector_2.mean(axis=1)
    #cos_sim = F.cosine_similarity(a.reshape(1,-1),b.reshape(1,-1), dim=1)

    # so we pad the tensors to be same shape
    if  a.shape[1] <  b.shape[1]:
        pad_size = (0, b.shape[1] - a.shape[1]) 
        a = torch.nn.functional.pad(a, pad_size, mode='constant', value=0)
    else:
        pad_size = (0, a.shape[1] - b.shape[1]) 
        b = torch.nn.functional.pad(b, pad_size, mode='constant', value=0)

    #print("After padding")
    #print("a.shape",a.shape ) # 1,N
    #print("b.shape",b.shape ) # 1, N


    # Calculate the cosine similarity
    cos_sim = cosine_similarity(a,b)
    ##print("got cosine similarity",cos_sim) # output [[0.80432487]]
    return cos_sim
#----------------------------------------------------------
def get():
    sys.stdout.write('--> ')
    return input()
#----------------------------------------------------------

def get_out_of_vocabulary_words_list(tokenizer, texts):
    out_of_vocab_words = []
    for text in texts:
        tokens = tokenizer.tokenize(text)
        out_of_vocab_words.extend([token for token in tokens if token not in tokenizer.vocab])
    return out_of_vocab_words


#----------------------------------------------------------


def show_results(scores):
    for i in range(len(scores)):
        s = scores[i]
        print("(%d,%d): %f"%(s[0][0],s[0][1],s[1]))
#----------------------------------------------------------



if __name__ == "__main__":
    s1 = "John loves dogs" 
    s2 = "dogs love John"

    s1 = ['In this chapter we introduce mechanisms for declaring new types and classes in Haskell. We start with three approaches to declaring types, then consider recursive types, show how to declare classes and their instances, and conclude by developing a tautology checker and an abstract machine drgfhegoh 2345746576']

    s2 = [
    'In this chapter, we explore methods for defining new types and classes in Haskell. We begin with three techniques for declaring types, followed by a discussion on recursive types. Next, we demonstrate how to declare classes and their instances. Finally, we conclude by creating a tautology checker and an abstract machine',
    'He says they are showing how to declare classes and instances',
    'They do not show how to declare classes and instances',
    'In this chapter we present mechanisms for declaring new classes',
    'It seems the authors propose the use of Haskell',
    'It seems the authors are against the use of Haskell',
    'This is bullshit'
    ]

    # Let's try the same with a better model - say for sentence embedding
    # From https://www.sbert.net/docs/pretrained_models.html
    # They have been extensively evaluated for their quality to embedded sentences 
    # (Performance Sentence Embeddings) and to embedded search queries & paragraphs 

    # better to use AutoTokenizer for other models see https://github.com/huggingface/transformers/issues/5587

    # Tokenize the text using BERT tokenizer

    # opción 1
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased") #Not good for sentence similarity

    # opción 2
    # tokenizer = BertTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
    # model = BertModel.from_pretrained("allenai/scibert_scivocab_uncased")

    # opción 3
    # tokenizer = BertTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    # model = BertModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model.eval()
    scores = dict()
    for i in range(len(s1)):
        for j in range(len(s2)):
            cos_sim = get_sentence_similarity(tokenizer,model,s1[i],s2[j])
            # print("(%d,%d): %f"%(i,j,cos_sim[0][0]))
            # print("--------------------------------")
            scores[(i,j)] = cos_sim[0][0]
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    show_results(sorted_scores)

    out_of_vocab_words_s1 = get_out_of_vocabulary_words_list(tokenizer, s1)
    # out_of_vocab_words_s2 = get_out_of_vocabulary_words_list(tokenizer, s2)
    print("Palabras fuera del vocabulario en s1:", out_of_vocab_words_s1)
    # print("Palabras fuera del vocabulario en s2:", out_of_vocab_words_s2)

    for i in range (len(s2)):
        out_of_vocab_words_s2 = get_out_of_vocabulary_words_list(tokenizer, s2[i])
        print("Palabras fuera del vocabulario en s2:", out_of_vocab_words_s2)
    
