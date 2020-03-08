from bs4 import BeautifulSoup
import re
import codecs
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from os import path
import json


# Helper functions: normalization, lemmatization

def normalize(text):
    """
    Converts text to lower string and removes numbers, punctuations,
    and other non-alphabetic characters, but leaving space and '*'
    """

    text = text.lower()
    return re.sub('( +)|(_+)', ' ', re.sub('[0-9]', '', ' '.join(re.findall("([\w]*)", text))))


def normalize_query(text):
    text = text.lower()
    return re.sub('( +)|(_+)', ' ', re.sub('[0-9]', '', ' '.join(re.findall("([\w\*]*)", text))))


def tokenize(text):
    """
    Breaks the text down into tokens
    """

    return word_tokenize(text)


def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(x) for x in tokens]


def remove_stop_word(tokens):
    stop_words = set(stopwords.words('english'))
    filtered = []
    for token in tokens:
        if token not in stop_words:
            filtered.append(token)
    return filtered


def get_collection(dataset_path, collection_path):
    collection = {}
    ids = []
    info = {}
    for i in range(1):
        file_path = path.join(dataset_path, f'reut2-{str(i).zfill(3)}.sgm')
        with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            doc = f.read()
        soup = BeautifulSoup(doc)
        reuters = soup.find_all('reuters')
        for x in reuters:
            id = x['newid']
            title = str(x.find('title'))[7:-8]
            body = str(x.find('body'))[6:-9]
            ids.append(id)
            info[id] = title
            collection[id] = [title, body]
    with open(collection_path, 'w') as fout:
        json.dump(collection, fout)

    return ids, info


def regular_inverted_index(collection_path, index_path):
    inverted_index = {}
    collection = {}
    with open(collection_path) as file:
        collection = json.load(file)

    for key in collection:
    # for key, doc in collection:
        id = int(key)
        for word in lemmatize(tokenize(normalize(collection[key][1]))):
            if word in inverted_index:
                inverted_index[word].add(id)
            else:
                inverted_index[word] = {id}
        for word in lemmatize(tokenize(normalize(collection[key][0]))):
            if word in inverted_index:
                inverted_index[word].add(id)
            else:
                inverted_index[word] = {id}
    words = []
    for key, value in inverted_index.items():
        words.append(key)
        with open(path.join(index_path, key), 'w') as file:
            json.dump(list(value), file)
    return words
    # return inverted_index


def soundex(token):
    mapping = {'a': 0, 'e': 0, 'i': 0, 'o': 0, 'u': 0, 'h': 0, 'w': 0, 'y': 0,
               'b': 1, 'f': 1, 'p': 1, 'v': 1,
               'c': 2, 'g': 2, 'j': 2, 'k': 2, 'q': 2, 's': 2, 'x': 2, 'z': 2,
               'd': 3, 't': 3,
               'l': 4,
               'm': 5, 'n': 5,
               'r': 6}
    if len(token) < 1:
        raise ValueError
    first = str(token[0])
    s = token[1:]
    s = ''.join(str(mapping[x]) for x in s)
    for i in range(10):
        s = re.sub(f'({i}{i}+)', f'{i}', s)
    s = re.sub('(0+)', '', s)
    ans = first + s + '000'
    return ans[:4]


def soundex_inverted_index(collection):
    inverted_index = {}
    for index in range(len(collection)):
        for word in tokenize(normalize(collection[index])):
            w = soundex(word)
            if w in inverted_index:
                inverted_index[w].add(index)
            else:
                inverted_index[w] = {index}
    return inverted_index


def edit_distance(str1, str2, m, n):
    if m == 0:
        return n
    if n == 0:
        return m

    if str1[m - 1] == str2[n - 1]:
        return edit_distance(str1, str2, m - 1, n - 1)

    return 1 + min(edit_distance(str1, str2, m, n - 1), edit_distance(str1, str2, m - 1, n),
                   edit_distance(str1, str2, m - 1, n - 1))


def levenshtein(a, b):
    return edit_distance(a, b, len(a), len(b))

def parse_config(config_path):
    with open(config_path) as json_file:
        return json.load(json_file)

def isValidConfig(config):
    if (config['dataset'] is None) or (config['collection'] is None) or (config['index'] is None):
        return False
    else:
        return True
