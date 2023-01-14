import re
import numbers
import math

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
        self.variables = {} # dictionary to store variable names and their values
        self.operators = {'+':1, '-':1, '*':2, '/':2, '^':3} # dictionary to store operator precedence
        self.functions = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'log': math.log} # dictionary to store trigonometric and logarithmic functions

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

        high_level_key = keys[0]
        value_of_high_level_key = self.get(high_level_key)

        keypath_value = None
        def search_dictionary( dic, keys):
            for key in keys[1:]:
                # print(f"key: {key}")
                if key in dic:
                    dic = dic[key]
                else:
                    return None

            if isinstance(dic, dict):
                search_dictionary(dic, keys)
            
            return dic


        if value_of_high_level_key == None:
            print(f"{high_level_key} -> []")
            # keypath_value == None
        else:
            if isinstance(value_of_high_level_key, dict):
                keypath_value = search_dictionary(value_of_high_level_key, keys)
                # print(f"keypath_value: {keypath_value}")
                # print(f"{keypath} -> " + print_key_value(keypath_value))
            
        return keypath_value

    def compute(self, formula_with_keypath):


        match_simple_formula = re.search(r"COMPUTE (.*) WHERE (\w+) = QUERY (.*)", formula_with_keypath)
        if match_simple_formula:
            computation = match_simple_formula.group(1)
            variable_name = match_simple_formula.group(2)
            keypath = match_simple_formula.group(3)
            variable_value = self.query(keypath)

            def perform_operation(operand1, operand2, operator):
                if operator == "+":
                    return operand1 + operand2
                elif operator == "-":
                    return operand1 - operand2
                elif operator == "*":
                    return operand1 * operand2
                elif operator == "/":
                    return operand1 / operand2
                elif operator == "^":
                    return operand1 ** operand2

            if isinstance(variable_value, numbers.Number):
                computation = computation.replace(variable_name, str(variable_value))
                operators_and_variables = re.findall("\d+|[+\-*/^()]", computation)
                print(f"operators_and_variables: {operators_and_variables}")
                # Perform the computation using the list of numbers and mathematical operators
                # ...
                operand1 = int(operators_and_variables[0])
                operand2 = int(operators_and_variables[2])
                operator = operators_and_variables[1]
                result = perform_operation(operand1, operand2, operator)
            else:
                return "Variable is not a number"
        else:
            return "Invalid formula"


        # # Extract the formula and keypath
        # formula, keypath = formula_with_keypath.split("WHERE")
        # print(f"formula:{formula}, keypath:{keypath}")
        # # Extract the variable name
        # variable_name = keypath.split("=")[0].strip()
        # print(f"variable_name: {variable_name}")
        # # Get the value of the keypath
        # variable_value = self.query(keypath.split("QUERY")[1].strip())
        # print(f"variable_value: {variable_value}")

        # def perform_operation(operand1, operand2, operator):
        #     if operator == "+":
        #         return operand1 + operand2
        #     elif operator == "-":
        #         return operand1 - operand2
        #     elif operator == "*":
        #         return operand1 * operand2
        #     elif operator == "/":
        #         return operand1 / operand2
        #     elif operator == "^":
        #         return operand1 ** operand2

        # if variable_value != None:
        # # Replace the variable name with its value in the formula
        #     formula = formula.replace(variable_name, str(variable_value))
        #     print(f"formula: {formula}")
        #     # Use regular expression to find all the numbers and mathematical operators in the formula
        #     operators_and_variables = re.findall("\d+|[+\-*/^()]", formula)
        #     print(f"operators_and_variables: {operators_and_variables}")
        #     # Perform the computation using the list of numbers and mathematical operators
        #     # ...
        #     operand1 = int(operators_and_variables[0])
        #     operand2 = int(operators_and_variables[2])
        #     operator = operators_and_variables[1]
        #     result = perform_operation(operand1, operand2, operator)
        # else: 
        #     return "Invalid keypath"
        # Compute the formula
        # result = evaluate_formula(formula)
        # result = eval(operators_and_variables[0] + operators_and_variables[1] + operators_and_variables[2])
        return result

 

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
    print(trie.query('ageqRfZ.level.person2.person1'))

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
