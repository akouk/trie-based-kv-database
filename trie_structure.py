import re
import numbers
import typing as tp
import MathExpressionEvaluator


class TrieNode:
    def __init__(self) -> None:
        self.children = {}  # a dictionary mapping characters to child nodes
        self.value = None  # the value stored at this node (if any)
        self.is_leaf = False # a boolean attribute that indicates whether the current node is a leaf node in the trie or not
        self.is_deleted = False  # a flag indicating whether the node has been deleted

    def remove_if_unused(self) -> None:
        if self.is_deleted:  # remove the node that is marked as deleted
            del self


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()  # create the root node of the trie
        self.variables = {}  # dictionary to store variable names and their values
        self.operators = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        self.functions = {'sin': 1, 'cos': 1, 'tan': 1, 'log': 1}
        self.left_associative_operators = ['+', '-', '*', '/']
        self.computed_value = None

    def put(self, key: str, value: str) -> None:
        current_root = self.root  # start at the root of the trie
        # follow the path of the key in the trie, creating new nodes as needed
        for char in key:
            if char not in current_root.children:
                current_root.children[char] = TrieNode()
            current_root = current_root.children[char]

        current_root.is_leaf = True
        current_root.value = value  # store the value at the final node

    def get(self, key: str) -> str:
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        for char in key:
            if char not in current_root.children:
                # the key does not exist in the trie
                return None
            current_root = current_root.children[char]
            # print(f'current_root = {current_root.children}')

        if current_root.value == "null":
            return []

        if current_root.is_leaf:
            if not current_root.is_deleted:
                return current_root.value
            else:
                return f'Key: {key} deleted successfully!'
        else:
            return "null"

    def delete(self, key: str) -> str:
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        path: tp.List[TrieNode] = []
        for char in key:
            if char not in current_root.children:
                # the key is not in the trie
                return None
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
        keys = keypath.split('.')

        high_level_key = keys[0]
        value_of_high_level_key = self.get(high_level_key)

        def search_dictionary(dic, keys):
            for key in keys[1:]:
                print(f'key: {key}')
                if key in dic:
                    dic = dic[key]
                else:
                    return None

            if isinstance(dic, dict):
                search_dictionary(dic, keys)

            return dic

        if value_of_high_level_key == None:
            print(f'{high_level_key} -> []')
            # keypath_value == None
        else:
            if isinstance(value_of_high_level_key, dict):
                keypath_value = search_dictionary(
                    value_of_high_level_key, keys)
                # print(f'keypath_value: {keypath_value}')
                # print(f'{keypath} -> ' + print_key_value(keypath_value))

        return keypath_value

    def compute(self, advanced_formula):

        # Extract the formula and keypath
        computation, variable_keypath = advanced_formula.split('WHERE')

        computation_formula = re.search(r'COMPUTE (.*)', computation)
        if not computation_formula:
            return 'Invalid computation formula'

        variables = self.variables
        if 'AND' in variable_keypath:
            variable_values = variable_keypath.split('AND')
            for variable_value in variable_values:

                match_value_formula = re.search(
                    r'(\w+) = QUERY (.*)', variable_value)
                if not match_value_formula:
                    return 'Invalid value formula'

                variable_name = match_value_formula.group(1).strip()
                variable_value_keypath = match_value_formula.group(2).strip()
                variable_value = self.query(variable_value_keypath)

                if isinstance(variable_value, numbers.Number):
                    variables[variable_name] = variable_value
                else:
                    return 'Keypath s value is not a number'
        else:
            match_value_formula = re.search(
                r'(\w+) = QUERY (.*)', variable_keypath)
            if not match_value_formula:
                return 'Invalid value formula'

            variable_name = match_value_formula.group(1).strip()
            variable_value_keypath = match_value_formula.group(2).strip()
            variable_value = self.query(variable_value_keypath)

            if isinstance(variable_value, numbers.Number):
                variables[variable_name] = variable_value
            else:
                return 'Keypath s is not a number'

        # Replace the variables with their values in the formula
        for variable, value in variables.items():
            computation = computation.replace(variable, str(value))

        operators_and_variables = re.findall('\d+|[+-/*^()]|sin|cos|tan|log10', computation)
        if not operators_and_variables:
            return 'Invalid characters in the expression'

        math_expression_evaluator = MathExpressionEvaluator()
        operators = self.operators
        functions = self.functions
        left_associative_operators = self.left_associative_operators

        evaluated_expression = math_expression_evaluator.evaluate_expression(
            operators_and_variables,
            operators,
            functions,
            left_associative_operators
        )
        computed_result = math_expression_evaluator.compute_expression(
            evaluated_expression,
            operators,
            functions
        )
        return(computed_result)
