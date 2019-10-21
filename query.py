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

#process query the same way we processed documents
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

#compute tf-idf for every sentence in document, compare to search query to get two top sentences
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
    return snippet

#compare query to every document, get top 5 most relevent documents
def getTop5(query, ps, stop_words, tokenizer, docs_content, token_2_index, tf_idf_test):
    query_proc = process(query, ps, stop_words, tokenizer)
    if len(query_proc) == 0:
        return "please enter a more specific query :)"
    print('query_proc: ' + str(query_proc))
    query_all_docs = (tf_idf_test.T)[[token_2_index[token] for token in query_proc if token in token_2_index],:].todense()
    for i in range(len(query_all_docs)):
        query_all_docs[i] = np.where(query_all_docs[i]==0, -1000, query_all_docs[i])
    query_all_docs_sum = np.sum(query_all_docs, axis=0)
    docId_score = list(zip(range(len(query_all_docs_sum.tolist()[0])), query_all_docs_sum.tolist()[0]))
    docId_score.sort(key=operator.itemgetter(1), reverse=True)
    docId_score_selected = docId_score[0:5]
    top5 = docId_score_selected
    top5_docs = docs_content.iloc[[i[0] for i in top5]]
    top5_docs['score'] = [i[1] for i in top5]
    top5_docs['query'] = [query for i in range(len(top5_docs))]
    top5_docs['snippet'] = [getSnippetFromContent(row['content'], query) for index, row in top5_docs.iterrows()]
    return top5_docs
