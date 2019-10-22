import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import pickle
import warnings

# converts a string to a set of words
def make_set(x):
	# return set(str(x).split())
    return str(x).split()

# split string, put in set, and then convert again to string
def split_join(x):
    x = set(x.split())
    return ' '.join(x)

class QuerySuggest:

    def __init__(self):

        # load data and do some processing on it
        self.df = None
        self.__get_data()
        self.__process_data()

        # pre-calculate some values
        self.frequencies = None
        self.max_session_length = None
        self.__calc_frequencies()
        self.__get_max_time()

        # query-specific values
        self.query = None
        self.query_freq = None
        self.query_sessions = None
        self.sessions = None
        self.candidates = None

    def __get_data(self):

        print('loading data...')

        pkl_path = Path('./qs_data.pkl')
        if pkl_path.is_file():
            print('loading data from pickle file...')
            pkl_file = open(pkl_path, 'rb') # must read as binary
            self.df = pickle.load(pkl_file)
            # self.df = self.df.sort_values(by=['session_id', 'q_time'])
            pkl_file.close()
        else:

            print('loading data from query logs...')

            all_files = [
                './ql/Clean-Data-01.txt',
                './ql/Clean-Data-02.txt',
                './ql/Clean-Data-03.txt',
                './ql/Clean-Data-04.txt',
                './ql/Clean-Data-05.txt'
            ]

            self.df = pd.concat((pd.read_csv(f, sep='\t') for f in all_files))
            # convert QueryTime string to POSIX timestamp
            self.df['QueryTime'] = pd.to_datetime(self.df['QueryTime'])
            self.df['q_time'] = self.df['QueryTime'].map(lambda x: x.timestamp())
            # convert query strings to a list of words
            self.df['q_split'] = self.df['Query'].map(lambda x: make_set(x))
            # get lengths of queries
            self.df['q_length'] = self.df['q_split'].map(lambda x: len(x))
            # get session IDs, based on when a different user starts making a search in the query log
			session_ID = []
			cur_session = 0
			prev_ID = 0
			for item in self.df['AnonID']:
				if item != prev_ID:
					cur_session += 1
					prev_ID = item
				session_ID.append(cur_session)
    
			self.df['session_id'] = session_ID
            # self.__process_data()

            print('saving data to pickle file...')
            pkl_file = open(pkl_path, 'wb') # must write as binary
            pickle.dump(self.df, pkl_file)
            pkl_file.close()

    def __process_data(self):
        print('processing loaded data...')
        # # convert QueryTime string to POSIX timestamp
        # self.df['QueryTime'] = pd.to_datetime(self.df['QueryTime'])
        # self.df['q_time'] = self.df['QueryTime'].map(lambda x: x.timestamp())
        # # convert query strings to sets of words
        # self.df['q_split'] = self.df['Query'].map(lambda x: make_set(x))
        # # get lengths of queries
        # self.df['q_length'] = self.df['q_split'].map(lambda x: len(x))
        # convert set back to string
        self.df['q_split_join'] = self.df['q_split'].map(lambda x: ' '.join(x))

    # gets candidate queries and the sessions where those candidate queries occur
    def __get_sessions(self):
        # print('getting candidates...')
        # find indeces where the user's query is part of a query in the query log, and apply to dataframe
        # df_criterion = self.df['q_split'].map(lambda x: self.query.issubset(x) and len(x) == (len(self.query)+1))
        df_criterion = self.df['q_split'].map(lambda x: len(x) == (len(self.query)+1) and self.query == x[:len(self.query)])
        qdf = self.df[df_criterion]
        # set searches in same session as the query, and candidate queries
        self.sessions = self.df[self.df['session_id'].isin(qdf['session_id'].values)]
        self.candidates = qdf

    """
    Freq(CQ)
    frequency of CQ in QL / max freq of any query in QL
    """
    def __calc_frequencies(self):

        print('getting query freqencies...')

        pkl_path = Path('./qs_freq.pkl')
        if pkl_path.is_file():
            print('loading frequencies from pickle file...')
            pkl_file = open(pkl_path, 'rb') # must read as binary
            self.frequencies = pickle.load(pkl_file)
            pkl_file.close()
        else:

            print('calculating frequencies from data...')
            # df_gb = self.df.groupby(['Query'])
            # df_freq = pd.DataFrame(df_gb.count()['q_length'])
            df_freq = pd.DataFrame(self.df.groupby(['Query'])['q_length'].count())

            # TODO: do log?
            max_freq = df_freq['q_length'].sort_values(ascending=False)[0]
            df_freq['freq'] = df_freq['q_length'].map(lambda x: x/max_freq)
            self.frequencies = df_freq['freq']

            print('saving frequencies to pickle file...')
            pkl_file = open(pkl_path, 'wb') # must write as binary
            pickle.dump(self.frequencies, pkl_file)
            pkl_file.close()

    def __freq(self, CQ):
        return self.frequencies.loc[CQ]

    """
    Mod(CQ,q')
    num sessions q' is modified to CQ / num sessions q' appears in QL
    """
    # gets the indeces of the query in the sessions
    def __get_qsessions(self):
        s_criterion = self.sessions['q_split'].map(lambda x: x == self.query)
        q_sessions = self.sessions[s_criterion]
        self.query_sessions = q_sessions

    def __get_query_freq(self):
        q_gb = self.df[['Query', 'session_id']].groupby(['Query']).nunique()
        self.query_freq = q_gb.count()[0]

    def __mod(self, CQ):
    
        # split candidate string, put in set, and then convert to string
        CQ = split_join(CQ)

        q_index = self.query_sessions.index
        
        # num sessions q' is modified to CQ
        mod_count = 0
        for i in q_index:
            # if sessions['q_split'].loc[i+1]  == CQ:
            if self.sessions['q_split_join'].loc[i+1]  == CQ:
                mod_count += 1

        # num sessions q' appears in QL
        # s_gb = q_sessions[['Query', 'session_id']].groupby(['Query']).nunique()
        # s_gb = df[['Query', 'session_id']].groupby(['Query']).nunique()
        # q_count = s_gb.count()[0]
        # q_count = self.query_freq

        return mod_count / self.query_freq

    """
    Time(CQ,q')
    min diff between times of q' and CQ in sessions / length of longest session in QL
    """
    # get length of longest session in QL
    def __get_max_time(self):

        print('getting time of longest session in the query log...')

        pkl_path = Path('./qs_max_time.pkl')
        if pkl_path.is_file():
            print('loading max time from pickle file...')
            pkl_file = open(pkl_path, 'rb') # must read as binary
            self.max_session_length = pickle.load(pkl_file)
            pkl_file.close()
        else:

            print('calculating max time from data...')
            session_lengths = self.df.groupby('session_id')['q_time'].agg(np.ptp)
            self.max_session_length = session_lengths.sort_values(ascending=False).iloc[0]

            print('saving max time to pickle file...')
            pkl_file = open(pkl_path, 'wb') # must write as binary
            pickle.dump(self.max_session_length, pkl_file)
            pkl_file.close()

    def __time(self, CQ):

        CQ = split_join(CQ)
        q_index = self.query_sessions.index
        min_time = 0 # in seconds

        for i in q_index:
            if self.sessions['q_split_join'].loc[i+1]  == CQ:
                time_range = self.sessions['q_time'].loc[i+1] - self.sessions['q_time'].loc[i]
                if time_range < min_time or min_time == 0:
                    min_time = time_range

        return min_time

    """
    Score(CQ,q')
    (Freq(CQ) + Mod(CQ,q') + Time(CQ,q')) / (1 - Min{Freq(CQ,q'), Mod(CQ,q'), Time(CQ,q'))
    """
    def __score(self, CQ):
        fr = self.__freq(CQ)
        mo = self.__mod(CQ)
        ti = self.__time(CQ)
        return (fr + mo + ti) / (1 - min(fr, mo, ti))

    """
    Get top query suggestions
    """
    def __get_top_5(self):
        
        # print('getting top query suggestions...')

        pd.options.mode.chained_assignment = None # suppress warning
        self.candidates['score'] = self.candidates['Query'].map(lambda x: self.__score(x))
        self.candidates = self.candidates.sort_values(by='score', ascending=False)
        # drop query suggestions that are duplicates (just different arrangement of words)
        top_5 = self.candidates.drop_duplicates(subset='Query')
        
        if len(top_5) >= 5:
            top_5 = top_5[:5]

        return list(top_5['Query'].values)

    """
    Only method publicly visible. Gets the top 5 query suggestions for a partial query.
    """
    def get_suggestions(self, query):

        query = query.split(' ')
        self.query = query
        self.__get_sessions()
        # pre-calculate some values for the query
        self.__get_query_freq()
        self.__get_qsessions()

        return self.__get_top_5()

def main():
	# query = ['make', 'money']
    query = 'make money'
    query_suggest = QuerySuggest()
    suggestions = query_suggest.get_suggestions(query)
    print(suggestions)

if __name__== "__main__":
    main()
