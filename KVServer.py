from trie_structure import Trie

class KVServer:
    def __init__(self):
        self.root = Trie()

    def put_request(self, key, value):
        self.root.put(key, value)  # insert the key-value pair into the trie

    def get_request(self, key):
        # retrieve the value associated with the key from the trie
        return self.root.get(key)

    def delete_request(self, key):
        # delete the key and its associated value from the trie
        self.root.delete(key)

    def query_request(self, keypath):
        # retrieve the value or subkey associated with the keypath from the trie
        return self.root.query(keypath)

    def compute_request(self, formula):
        # Parse the formula and retrieve any required values from the key-value store
        # compute formula using values from the trie
        return self.root.compute(formula)
