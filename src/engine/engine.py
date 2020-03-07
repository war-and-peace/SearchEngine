class SearchEngine(object):
    def __init__(self):
        self.collection = get_collection()
        self.prefix_tree = get_prefix_tree(self.collection)
        self.inverted_prefix_tree = get_inverted_prefix_tree(self.collection)
        self.rotated_prefix_tree = get_rotated_prefix_tree(self.collection)
        self.rii = regular_inverted_index(self.collection)
        self.stop_words = set(stopwords.words('english'))
        self.words = list(self.rii.keys())

    def search(self, query):
        flag = True
        answer = set()
        resulting_query = []
        for token in remove_stop_word(tokenize(normalizeQuery(query))):
            if len(token) < 1:
                continue

            if self.prefix_tree.find(token):
                answer = answer.union(self.rii[token]) if flag else answer.intersection(self.rii[token])
                resulting_query.append(token)
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
                    print('adding word', word)
                    partial_answer = partial_answer.union(self.rii[word])
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
                        partial_answer = partial_answer.union(self.rii[word])
                        query_part.append(word)
                answer = answer.union(partial_answer) if flag else answer.intersection(partial_answer)
                resulting_query.append(query_part)
                flag = False
        return answer, resulting_query

if __name__ == '__main__':
    engine = SearchEngine()