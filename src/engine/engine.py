from prefix_tree import *
from functions import *
import json
import os
import sys

class SearchEngine(object):
    def __init__(self, config):
        self.config = config
        self.collection, self.titles = get_collection(self.config['dataset'], self.config['collection'])
        self.words = regular_inverted_index(self.config['collection'], self.config['index'])
        self.auxilary_index = {}
        self.prefix_tree = get_prefix_tree(self.words)
        self.inverted_prefix_tree = get_inverted_prefix_tree(self.words)
        self.rotated_prefix_tree = get_rotated_prefix_tree(self.words)
        self.stop_words = set(stopwords.words('english'))
        self.deleted_postings = set()

    def search(self, query):
        flag = True
        answer = set()
        resulting_query = []
        for token in remove_stop_word(tokenize(normalize_query(query))):
            if len(token) < 1:
                continue

            if self.prefix_tree.find(token):
                answer = answer.union(self.get_indexes_of_token(token)) \
                    if flag else answer.intersection(self.get_indexes_of_token(token))
                resulting_query.append(token)
                flag = False
                continue

            if token in self.auxilary_index:
                answer = answer.union(self.auxilary_index[token]) \
                    if flag else answer.intersection(self.auxilary_index[token])
                flag = False
                continue

            index = token.find('*')
            if index != -1:
                possible_words = []
                if index == 0:
                    inv_possible_words = self.inverted_prefix_tree.get_starting_with((token[1:])[::-1])
                    possible_words = [None] * len(inv_possible_words)
                    for i in range(len(inv_possible_words)):
                        possible_words[i] = inv_possible_words[i][::-1]
                elif index == len(token) - 1:
                    possible_words = self.prefix_tree.get_starting_with(token[:len(token) - 1])
                else:
                    new_token = token[index + 1:] + '$' + token[:index]
                    possible_words = self.rotated_prefix_tree.get_starting_with(new_token)

                partial_answer = set()
                query_part = []
                for word in lemmatize(possible_words):
                    if word in self.stop_words:
                        continue
                    query_part.append(word)
                    # print('adding word', word)
                    partial_answer = partial_answer.union(self.get_indexes_of_token(word))
                answer = answer.union(partial_answer) if flag else answer.intersection(partial_answer)
                resulting_query.append(query_part)
            else:
                stoken = soundex(token)
                minDistance = 1000
                for word in self.words:
                    minDistance = min(minDistance, levenshtein(stoken, soundex(word)))

                partial_answer = set()
                query_part = []
                for word in self.words:
                    if levenshtein(stoken, soundex(word)) == minDistance and word not in self.stop_words:
                        partial_answer = partial_answer.union(self.get_indexes_of_token(word))
                        query_part.append(word)
                answer = answer.union(partial_answer) if flag else answer.intersection(partial_answer)
                resulting_query.append(query_part)
                flag = False
        for index in list(answer):
            if index in self.deleted_postings:
                answer.remove(index)
        return answer, resulting_query

    def get_answers(self, result):
        ans = []
        for id in result:
            ans.append([id, self.titles[str(id)]])
        return ans

    def get_document(self, id):
        with open(self.config['collection']) as file:
            collection = json.load(file)
        key = str(id)
        return None if key not in collection else collection[key]

    def get_indexes_of_token(self, token):
        file_path = os.path.join(self.config['index'], token)
        try:
            f = open(file_path, 'r')
            return json.load(f)
        except:
            return []

    def process_crawler_data(self, additions, deletions):
        for posting in deletions:
            self.deleted_postings.add(posting)

        self.update_auxilary_index(additions)
        current_size = sys.getsizeof(self.auxilary_index)
        if current_size > int(self.config['auxilary_index_threshold']):
            self.dump_auxilary_index()

    def update_auxilary_index(self, collection):
        for key in collection:
            # for key, doc in collection:
            id = int(key)
            self.titles[str(id)] = collection[key][0]
            for word in lemmatize(tokenize(normalize(collection[key][1]))):
                if word in self.auxilary_index:
                    self.auxilary_index[word].add(id)
                else:
                    self.auxilary_index[word] = {id}
            for word in lemmatize(tokenize(normalize(collection[key][0]))):
                if word in self.auxilary_index:
                    self.auxilary_index[word].add(id)
                else:
                    self.auxilary_index[word] = {id}

    def dump_auxilary_index(self):
        base_dir = self.config['index']
        for word, indexes in self.auxilary_index.items():
            file_path = os.path.join(base_dir, word)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    old_indexes = json.load(f)
                sind = set(old_indexes)
                for index in indexes:
                    sind.add(index)
                for index in self.deleted_postings:
                    if index in sind:
                        sind.remove(index)
                with open(file_path, 'w') as f:
                    json.dump(list(sind), f)
            else:
                sind = set(indexes)
                for index in self.deleted_postings:
                    if index in sind:
                        sind.remove(index)
                with open(file_path, 'w') as f:
                    json.dump(list(sind), f)
        self.auxilary_index = {}
        self.deleted_postings = set()
