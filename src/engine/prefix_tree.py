from functions import *


# Prefix tree

class Node(object):
    def __init__(self):
        self.children = [None] * 27
        self.isEnd = False


class PrefixTree(object):
    def __init__(self):
        self.root = Node()

    def insert(self, word):

        current = self.root
        for i in range(len(word)):
            pos = self.get_index(word[i])
            if pos < 0 or pos > 26:
                return
            if not current.children[pos]:
                current.children[pos] = Node()
            current = current.children[pos]

        current.isEnd = True

    def find(self, word):

        current = self.root

        for i in range(len(word)):
            pos = self.get_index(word[i])
            if pos < 0 or pos > 26:
                return False
            if not current.children[pos]:
                return False
            current = current.children[pos]

        return current is not None and current.isEnd

    def get_index(self, c):
        return 26 if c == '$' else ord(c) - ord('a')

    def clean_word(self, word):
        index = word.find('$')
        if index == -1:
            return word
        if index == 0:
            return word[1:]
        elif index == len(word) - 1:
            return word[:len(word) - 1]
        else:
            return word[index + 1:] + word[:index]

    def get_all_ending_with(self, start_pos, suffix):
        answer = []
        for i in range(27):
            if start_pos.children[i] is not None:
                symbol = '$' if i == 26 else chr(ord('a') + i)

                if start_pos.children[i].isEnd:
                    answer.append(self.clean_word(suffix + symbol))

                for x in self.get_all_ending_with(start_pos.children[i], suffix + symbol):
                    answer.append(x)
        return answer

    def get_starting_with(self, prefix):
        current = self.root

        for i in range(len(prefix)):
            index = self.get_index(prefix[i])
            if not current.children[index]:
                return []
            current = current.children[index]
        answer = []

        if current.isEnd:
            answer.append(self.clean_word(prefix))

        for suffix in self.get_all_ending_with(current, ''):
            answer.append(self.clean_word(prefix + suffix))

        return answer


# Prefix tree:
def get_prefix_tree(dictionary):
    prefix_tree = PrefixTree()

    for word in dictionary:
            prefix_tree.insert(word)
    return prefix_tree


# Inverted Prefix Tree
def get_inverted_prefix_tree(dictionary):
    inv_prefix_tree = PrefixTree()
    for word in dictionary:
    # for index in range(len(collection)):
    #     for word in tokenize(normalize(collection[index])):
            inv_prefix_tree.insert(word[::-1])
    return inv_prefix_tree


# Prefix tree of rotated tokens
def get_rotated_prefix_tree(dictionary):
    rotated_prefix_tree = PrefixTree()
    for word in dictionary:
    # for index in range(len(collection)):
    #     for word in tokenize(normalize(collection[index])):
        w = word + '$'
        for i in range(len(w)):
            rotated_prefix_tree.insert(w)
            w = w[1:] + w[:1]
    return rotated_prefix_tree
