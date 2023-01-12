import NEW.BaseServer as BaseServer

class TrieNode:
    def __init__(self):
        self.children = {} # a dictionary mapping characters to child nodes
        self.value = None # the value stored at this node (if any)
        self.is_leaf = False # a boolean attribute that indicates whether the currnet node is a leaf node in the trie or not
        self.is_deleted = False # a flag indicating whether the node has been deleted

    def remove_if_unused(self):
        # remove the node if it has no children and is marked as deleted
        if self.is_deleted and not self.children:
            del self

class Trie:
    def __init__(self):
        self.root = TrieNode() # create the root node of the trie

    def put(self, key, value):
        current_root = self.root # start at the root of the trie
        # follow the path of the key in the trie, creating new nodes as needed
        for char in key:
            # print(f"char: {char}")
            if char not in current_root.children:
                # print("chzr not in current_root.children")
                current_root.children[char] = TrieNode()
            current_root = current_root.children[char]
        
        current_root.is_leaf = True
        current_root.value = value #store the value at the final node
    
    
    def get(self, key):
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        for char in key:
            # print(f"for char: {char} in key: {key}")
            if char not in current_root.children:
                # print(f"char not in {current_root.children}")
                # the key does not exist in the trie
                return None
            current_root = current_root.children[char]
            # print(f"current_root = {current_root.childern}")
        
        if current_root.is_leaf:
            if not current_root.is_deleted:
                return current_root.value
            else:
                return "Deleted"
        else:
            return None

    def remove_if_unused(self):
        # remove the node if it has no children, is marked as deleted and is a leaf node
        if self.is_deleted and not self.children:
            del self

    def delete(self, key):
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        path = []
        for char in key:
            if char not in current_root.children:
                # the key is not in the trie
                return
            path.append(current_root)
            current_root = current_root.children[char]

        # mark the note at the end of the path as deleted
        current_root.is_deleted = True
        path.append(current_root)
        # remove all nodes that are no longer being used
        for node in path:
            node.remove_if_unused()
    
    def query(self, keypath):
        # split the keypath into individual keys
        keys = keypath.split(".")

        # start at the root of the trie
        current_root = self.root

        # follow the path of the keys in the trie
        for key in keys:
            if key not in current_root.children:
                # the key is not in the trie
                return None
            current_root = current_root.children[key]

        # return the value or the subkey at the end of the path (if any)
        if current_root.value is not None:
            return current_root.value
        else:
            return current_root.children

    def compute(self, formula, variables):
        # define a dictionary of operator functions
        operators = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y,
            "^": lambda x, y: x **y
        }

        result = variables[formula[0]] # initialize the result to the first value in the formula

        # loop through the formula, applying the appropriate operator function to the result and the next value
        for i in range(1, len(formula), 2):
            op = formula[i]
            val = variables[formula[i+1]]
            result = operators[op](result, val)

        return result


class KVServer(BaseServer.BaseServer):
    def __init__(self, port, ip_address):
        super().__init__(port=port, host=ip_address)
        self.ip_address = ip_address
        self.port = port
        self.root = Trie()

    def put_request(self, key, value):
        self.root.put(key, value) # insert the key-value pair into the trie

    def get_request(self, key):
        return self.root.get(key) # retrieve the value associated with the key from the trie

    def delete_request(self, key):
        self.root.delete(key) # delete the key and its associated value from the trie

    def query_request(self, keypath):
        return self.root.query(keypath) # retrieve the value or subkey associated with the keypath from the trie
            
    def compute_request(self, formula, variables):
        # Parse the formula and retrieve any required values from the key-value store
        return self.root.compute(formula, variables) # compute formula using values from the trie
