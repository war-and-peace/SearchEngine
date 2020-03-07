# Helper functions: normalization, lemmatization

def normalize(text):
    # Converts text to lower string and removes numbers, punctuations, and other non-alphabetic characters, but leaving space and '*'

    text = text.lower()
    return re.sub('( +)|(_+)', ' ', re.sub('[0-9]', '', ' '.join(re.findall("([\w]*)", text))))


def normalizeQuery(text):
    text = text.lower()
    return re.sub('( +)|(_+)', ' ', re.sub('[0-9]', '', ' '.join(re.findall("([\w\*]*)", text))))


def tokenize(text):
    # Breaks the text down into tokens

    return word_tokenize(text)


def lemmatize(tokens):
    # lemmatizes

    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(x) for x in tokens]


def remove_stop_word(tokens):
    stop_words = set(stopwords.words('english'))
    filtered = []
    for token in tokens:
        if token not in stop_words:
            filtered.append(token)
    return filtered

def get_collection():
    collection = []
    for i in range(22):
        file_name = f'reuters/reut2-{str(i).zfill(3)}.sgm'
        doc = ''
        with codecs.open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
            doc = f.read()
        soup = BeautifulSoup(doc)
        body = soup.find_all('body')
        for x in body:
            collection.append(str(x)[6:-9])
    return collection

def regular_inverted_index(collection):
    inverted_index = {}
    for index in range(len(collection)):
        for word in lemmatize(tokenize(normalize(collection[index]))):
            if word in inverted_index:
                inverted_index[word].add(index)
            else:
                inverted_index[word] = set([index])
    return inverted_index


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
                inverted_index[w] = set([index])
    return inverted_index


def editDistance(str1, str2, m, n):
    if m == 0:
        return n
    if n == 0:
        return m

    if str1[m - 1] == str2[n - 1]:
        return editDistance(str1, str2, m - 1, n - 1)

    return 1 + min(editDistance(str1, str2, m, n - 1), editDistance(str1, str2, m - 1, n),
                   editDistance(str1, str2, m - 1, n - 1))


def levenshtein(a, b):
    return editDistance(a, b, len(a), len(b))

