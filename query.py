import pandas as pd
import pickle as pkl
import numpy as np
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from IPython.display import display
import operator
import re
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import color

def process(content, ps, stop_words, tokenizer):
    #df = row.to_frame()
    # split documents with tokenizer
    processed = tokenizer.tokenize(content)
    # remove punctuation
    #processed = [token for token in processed if token != ',' and token != '.']
    # remove capitalization
    processed = [token.lower() for token in processed]
    # remove stopwords
    processed = [token for token in processed if token not in stop_words]
    # lemmatize/stem terms
    return [ps.stem(token) for token in processed]

def getSnippetFromContent(content, query):
    tf = TfidfVectorizer()
    sentences = sent_tokenize(content)
    tfidf_matrix = tf.fit_transform(sentences)
    features = tf.get_feature_names()
    token_2_index_little = dict(zip(features, range(len(features))))
    query_docs = (tfidf_matrix.T)[[token_2_index_little[token] for token in query.split(' ') if token in token_2_index_little],:].todense()
    for i in range(len(query_docs)):
        query_docs[i] = np.where(query_docs[i]==0, -1000, query_docs[i])
    query_docs_sum = np.sum(query_docs, axis=0)
    docSent_score = list(zip(range(len(query_docs_sum.tolist()[0])), query_docs_sum.tolist()[0]))
    docSent_score.sort(key=operator.itemgetter(1), reverse=True)
    docSent_score_selected = docSent_score[0:2]
    sentence_indices = [i[0] for i in docSent_score_selected]
    snippet = '... '.join([sentences[i] for i in sentence_indices])
    #print('\033[1m' + 'Hello World! ' + '\033[0m' + 'asdfasdf')
    return snippet

def getTop5(query, ps, stop_words, tokenizer, docs_content, token_2_index, tf_idf_test):
    #query_proc
    query_proc = process(query, ps, stop_words, tokenizer)
    #[token_2_index[token] for token in query_proc]
    query_all_docs = (tf_idf_test.T)[[token_2_index[token] for token in query_proc],:].todense()
    #query_all_docs.shape
    #type(query_all_docs[0])
    #query_all_docs
    for i in range(len(query_all_docs)):
        query_all_docs[i] = np.where(query_all_docs[i]==0, -1000, query_all_docs[i])
    #query_all_docs
    query_all_docs_sum = np.sum(query_all_docs, axis=0)
    #len(query_all_docs_sum.tolist()[0])
    docId_score = list(zip(range(len(query_all_docs_sum.tolist()[0])), query_all_docs_sum.tolist()[0]))
    docId_score.sort(key=operator.itemgetter(1), reverse=True)
    docId_score_selected = docId_score[0:5]
    top5 = docId_score_selected
    top5_docs = docs_content.iloc[[i[0] for i in top5]]
    top5_docs['score'] = [i[1] for i in top5]
    top5_docs['query'] = [query for i in range(len(top5_docs))]
    top5_docs['snippet'] = [getSnippetFromContent(row['content'], query) for index, row in top5_docs.iterrows()]
    return top5_docs
