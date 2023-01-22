import re
import numbers
import typing as tp
from MathExpressionEvaluator import MathExpressionEvaluator

class TrieNode:
    def __init__(self) -> None:
        self.children = {} # a dictionary mapping characters to child nodes
        self.value = None # the value stored at this node (if any)
        self.is_leaf = False # a boolean attribute that indicates whether the currnet node is a leaf node in the trie or not
        self.is_deleted = False # a flag indicating whether the node has been deleted

    def remove_if_unused(self) -> None:
        # remove the node if it has no children and is marked as deleted
        if self.is_deleted and not self.children:
            del self

class Trie:

    
    def __init__(self) -> None:
        self.root = TrieNode() # create the root node of the trie
        self.variables = {} # dictionary to store variable names and their values
        self.operators = {'+':1, '-':1, '*':2, '/':2, '^':3}
        self.functions = {'sin':1, 'cos':1, 'tan':1, 'log':1}
        self.left_associative_operators = ['+', '-', '*', '/']
        self.computed_value = None
        self.operators_and_variables = []

    def put(self, key: str, value:str) -> None:
        current_root = self.root # start at the root of the trie
        # follow the path of the key in the trie, creating new nodes as needed
        for char in key:
            if char not in current_root.children:
                current_root.children[char] = TrieNode()
            current_root = current_root.children[char]
        
        current_root.is_leaf = True
        current_root.value = value #store the value at the final node

   
    def get(self, key: str) -> str:
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        for char in key:
            if char not in current_root.children:
                # the key does not exist in the trie
                return None
            current_root = current_root.children[char]

        if current_root.is_leaf:
            if not current_root.is_deleted:
                return current_root.value
            else:
                return f'Key: {key} has been deleted!'
        else:
            return None
        
        


    def delete(self, key:str) -> str:
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        path: tp.List[TrieNode] = []
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

    def query(self, keypath: str) -> str:
        # split the keypath into individual keys
        keys = keypath.split(".")

        high_level_key = keys[0]
        value_of_high_level_key = self.get(high_level_key)

        keypath_value = self.computed_value

        def search_dictionary( dic: dict, keys: list):
            for key in keys[1:]:
                if key in dic:
                    dic = dic[key]
                else:
                    return None

            if isinstance(dic, dict):
                search_dictionary(dic, keys)
            
            return dic

        if isinstance(value_of_high_level_key, dict):
            keypath_value = search_dictionary(value_of_high_level_key, keys)
            
        return keypath_value

    def compute(self, formula):
        # Extract the formula and keypath
        computation, variable_keypath = formula.split("where")

        computation_formula = re.search(r"compute (.*)", computation)
        if not computation_formula:
            return "Invalid computation formula"
        
        variables = self.variables
        if "and" in variable_keypath:
            variable_values = variable_keypath.split("and")
            for variable_value in variable_values:

                match_value_formula = re.search(r"(\w+) = query (.*)", variable_value)          
                if not match_value_formula:
                    return "Invalid value formula"

                variable_name = match_value_formula.group(1).strip()
                variable_value_keypath = match_value_formula.group(2).strip()
                variable_value = self.query(variable_value_keypath)
                
                if isinstance(variable_value, numbers.Number):
                    variables[variable_name] = variable_value

        else:
            match_value_formula = re.search(r"(\w+) = query (.*)", variable_keypath)          
            if not match_value_formula:
                return "Invalid value formula"
            
            variable_name = match_value_formula.group(1).strip()
            variable_value_keypath = match_value_formula.group(2).strip()
            variable_value = self.query(variable_value_keypath)

            if isinstance(variable_value, numbers.Number):
                variables[variable_name] = variable_value
            else:
                return "Variable is not a number"  

        operators = self.operators
        functions = self.functions
        left_associative_operators = self.left_associative_operators
        expression_evaluator = MathExpressionEvaluator()
        operators_functions_and_variables = self.operators_and_variables

        # Replace the variables with their values in the formula
        for variable, value in variables.items():
            computation = computation.replace(variable, str(value))
        
        print(f"computation: {computation}")

        variables = re.findall("(\d+(?:\.\d+)?)", computation)
        operators_functions_and_variables.extend(variables)

        operators_and_functions = re.findall("[+-/*^()]|sin|cos|tan|log10", computation)
        operators_functions_and_variables.extend(operators_and_functions)

        dot = "."
        if dot in operators_functions_and_variables:
            operators_functions_and_variables.remove(dot)

        evaluated_expression = expression_evaluator.evaluate_expression(
            operators_functions_and_variables, 
            operators, 
            functions, 
            left_associative_operators
        )
        computed_result = expression_evaluator.compute_expression(
            evaluated_expression, 
            operators, 
            functions
        )
        
        return(computed_result)
