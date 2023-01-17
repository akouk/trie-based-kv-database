import re
import numbers
import math

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
            # print(f"current_root = {current_root.childern}")
        
        if current_root.is_leaf:
            if not current_root.is_deleted:
                return current_root.value
            else:
                return "Deleted"
        else:
            return None


    def delete(self, key:str) -> str:
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
            node.self.remove_if_unused()

    def query(self, keypath: str) -> str:
        # split the keypath into individual keys
        keys = keypath.split(".")

        high_level_key = keys[0]
        value_of_high_level_key = self.get(high_level_key)

        keypath_value = self.computed_value

        def search_dictionary( dic: dict, keys: list):
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
            
        return keypath_value

    def compute(self, advanced_formula):
        # Extract the formula and keypath
        computation, variable_keypath = advanced_formula.split("WHERE")

        computation_formula = re.search(r"COMPUTE (.*)", computation)
        if not computation_formula:
            return "Invalid computation formula"
        
        variables = self.variables
        if "AND" in variable_keypath:
            variable_values = variable_keypath.split("AND")
            for variable_value in variable_values:

                match_value_formula = re.search(r"(\w+) = QUERY (.*)", variable_value)          
                if not match_value_formula:
                    return "Invalid value formula"

                variable_name = match_value_formula.group(1).strip()
                variable_value_keypath = match_value_formula.group(2).strip()
                variable_value = self.query(variable_value_keypath)
                
                if isinstance(variable_value, numbers.Number):
                    variables[variable_name] = variable_value
                else:
                    return "Variable is not a number"
        else:
            match_value_formula = re.search(r"(\w+) = QUERY (.*)", variable_keypath)          
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

        # Replace the variables with their values in the formula
        for variable, value in variables.items():
            computation = computation.replace(variable, str(value))
        
        operators_and_variables = re.findall("\d+|[+-/*^()]|sin|cos|tan|log10", computation)
        if not operators_and_variables:
            return "Invalid operators"

        evaluated_expression = self.evaluate_expression(operators_and_variables, operators, functions, left_associative_operators)
        computed_result = self.compute_expression(evaluated_expression, operators, functions)
        return(computed_result)
    
    @staticmethod
    def is_operator(character, operator_precedence):
        return character in operator_precedence

    @staticmethod
    def precedence(character, operator_precedence):
        return operator_precedence[character]

    @staticmethod
    def is_function(character, function_precedence):
        return character in function_precedence

    @staticmethod
    def is_number(character):
        if character.isnumeric():
            return True

    @staticmethod
    def is_left_associative(character, left_associative_operators):
        return character in left_associative_operators
        
    @staticmethod
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
        else:
            return "Invalid operand!"

    @staticmethod
    def perform_function(function, operand):
        if function == "sin":
            return math.sin(operand)
        elif function == "cos":
            return math.cos(operand)
        elif function == "tan":
            return math.tan(operand)
        elif function == "log":
            return math.log10(operand)
        else:
            return "Invalid function"

    
    def evaluate_expression(self,
        characters,
        operators,
        functions,
        left_associative_operators
    ):

        output_queue = []
        operator_stack = []
        while characters:
            character = characters.pop(0)
            if self.is_number(character):
                output_queue.append(character)
            elif self.is_function(character, functions):
                operator_stack.append(character)
            elif self.is_operator(character, operators):
                while (
                    operator_stack and
                    self.is_operator(operator_stack[-1], operators) and
                    (
                        self.precedence(operator_stack[-1], operators) > self.precedence(character, operators) or
                        (self.precedence(operator_stack[-1], operators) == self.precedence(character, operators) and self.is_left_associative(character, left_associative_operators))
                    )
                ):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(character)
            elif character == "(":
                operator_stack.append(character)
            elif character == ")":
                while operator_stack and operator_stack[-1] != "(":
                    output_queue.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == "(":
                    operator_stack.pop()
                if operator_stack and self.is_function(operator_stack[-1], functions):
                    output_queue.append(operator_stack.pop())

        while operator_stack:
            output_queue.append(operator_stack.pop())

        return output_queue   

    def compute_expression(self,
        evaluated_expression,
        operators,
        functions
    ):
        
        # Use a stack to handle operator precedence
        stack = []
        print(f"result: {evaluated_expression}")
        for character in evaluated_expression:
            if self.is_number(character):
                stack.append(float(character))
            elif self.is_operator(character, operators):
                operator = character
                # Pop the last two elements from the stack as operands
                operand2 = stack.pop()
                operand1 = stack.pop()
                operation_result = self.perform_operation(operand1, operand2, operator)
                # Perform the operation and push the result back to the stack
                stack.append(operation_result)

            elif self.is_function(character, functions):
                function = character
                operand = stack.pop()
                # Perform the function and push the result back to the stack
                function_result = self.perform_function(function, operand)
                stack.append(function_result)

        # The final result is the last element in the stack
        return stack.pop()


def main():
    data = {"ageqRfZ": 
                {"level": 
                    {"person2": 
                        {"age": 86, "name": "PzOQ", "person1": "Anqr", "person2": "Gt9U", "height": 2
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


    trie = Trie()
    for key, value in data.items():
        trie.put(key, value)
    print(trie.query('ageqRfZ.level.person2.age'))
    print(trie.compute("COMPUTE x/2 WHERE x = QUERY ageqRfZ.level.person2.age"))
    print(trie.compute("COMPUTE 2/(x+3*(y+z)) WHERE x = QUERY ageqRfZ.level.person2.age AND y = QUERY ageqRfZ.level.person2.height AND z = QUERY ageqRfZ.level.person2.age"))
    print(trie.compute("COMPUTE cos(x)-tan(2*y+3) WHERE x = QUERY ageqRfZ.level.person2.age AND y = QUERY ageqRfZ.level.person2.height AND z = QUERY ageqRfZ.level.person2.age"))

    # trie.add_to_trie(trie, "", data)
    # print(trie.query('ageqRfZ.level.person2.age'))


def print_key_value(v) -> str:

    def handle_value(v):
        if isinstance(v, dict):
            return f'[ {print_key_value(v)} ]'

        elif isinstance(v, list):
            return f'[ {" | ".join(f"“{str(element)}”" for element in v)} ]'

        elif isinstance(v, (int, float)):
            return str(v)

        elif v is None:
            return 'null'

        else:
            return f'“{str(v)}”'

    return f' | '.join([F'“{k}” -> {handle_value(v)}' for k, v in v])



if __name__ == '__main__':
    main()
