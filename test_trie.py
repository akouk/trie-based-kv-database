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
        print(keys)
        print(keys[0])

        # start at the root of the trie
        current_root = self.root
        # current_value = current_root.value
        
        high_level_key = keys[0]
        value_of_high_level_key = self.get(high_level_key)

        def search_dictionary(dic, keys):
            if len(keys) == 0:
                return dic
            key = keys.pop(0)
            if type(dic) == dict:
                for key in keys[1:]:
                    print(f"key: {key}")
                    if key in dic:
                        print(f"key: {key} found!")
                        print(f"value of key: {key} is {dic[key]}")
                        return search_dictionary(dic[key], keys)
                    else:
                        print(f"The key: {key} not found in the keypath! Please provide a valid keypath.")
                        return None
            # return None
        # follow the path of the keys in the trie

        keypath_value = search_dictionary(value_of_high_level_key, keys)
        return keypath_value

def main():
    data = {"ageqRfZ": 
                {"level": 
                    {"person2": 
                        {"age": 86, "name": "PzOQ", "person1": "Anqr", "person2": "Gt9U"
                        }
                    }, "person1": 
                        {"level": 
                            {"profession": "5Ik8", "street": "W4Pg", "person1": "p589"
                            }, 
                        "profession": 
                                {"name": "f4bH", "person3": "xmkw"
                            }
                        }
                }
            }

    data2 = {"height8BrR": {"age": {"person1": {"age": 3}, "person3": {"person1": "tyXB", "person2": "QOJf"}, "profession": {"person2": "OHdc"}}, "height": {"profession": {"person3": "64u5", "level": 22}, "name": {"street": "aXl0"}, "level": {"level": 68, "street": "SPUo"}}}}

    # trie = Trie()
    # for key, value in data.items():
    #     trie.put(key, value)

    # for key, value in data2.items():
    #     trie.put(key, value)
    
    # trie.delete("height8BrR")
    
    # # print(trie.get("height8BrR"))
    # print(trie.query("ageqRfZ.level.person2.age"))

    trie = Trie()
    for key, value in data.items():
        trie.put(key, value)
    print(trie.query('ageqRfZ.level.person2.age'))

    # trie.add_to_trie(trie, "", data)
    # print(trie.query('ageqRfZ.level.person2.age'))


def pretty_print(obj: dict) -> str:

    def handle_value(v):
        if isinstance(v, dict):
            return f'[ {pretty_print(v)} ]'

        elif isinstance(v, list):
            return f'[ {" | ".join(f"“{str(element)}”" for element in v)} ]'

        elif isinstance(v, (int, float)):
            return str(v)

        elif v is None:
            return 'null'

        else:
            return f'“{str(v)}”'

    return f' | '.join([F'“{k}” -> {handle_value(v)}' for k, v in obj.items()])



if __name__ == '__main__':
    main()
