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

    # def remove_if_unused(self):
    #     # remove the node if it has no children, is marked as deleted and is a leaf node
    #     if self.is_deleted and not self.children:
    #         del self

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
            node.remove_if_unused()

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

    # def compute(self, formula_with_keypath: str) -> str:


    #     match_simple_formula = re.search(r"COMPUTE (.*) WHERE (\w+) = QUERY (.*)", formula_with_keypath)
    #     if not match_simple_formula:
    #         return "Invalid formula"

    #     computation = match_simple_formula.group(1)
    #     variable_name = match_simple_formula.group(2).strip()
    #     keypath = match_simple_formula.group(3).strip()
    #     variable_value = self.query(keypath)

    #     def perform_operation(operand1, operand2, operator):
    #         if operator == "+":
    #             return operand1 + operand2
    #         elif operator == "-":
    #             return operand1 - operand2
    #         elif operator == "*":
    #             return operand1 * operand2
    #         elif operator == "/":
    #             return operand1 / operand2
    #         elif operator == "^":
    #             return operand1 ** operand2

    #     if isinstance(variable_value, numbers.Number):
    #         computation = computation.replace(variable_name, str(variable_value))
    #         operators_and_variables = re.findall("\d+|[+\-*/^()]", computation)
    #         # Perform the computation using the list of numbers and mathematical operators
    #         # ...
    #         operand1 = int(operators_and_variables[0])
    #         operand2 = int(operators_and_variables[2])
    #         operator = operators_and_variables[1]
    #         result = perform_operation(operand1, operand2, operator)
    #     else:
    #         return "Variable is not a number"            

    #     return result

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

    @staticmethod
    def evaluate_expression(
        characters,
        operators,
        functions,
        left_associative_operators
    ):
        trie = Trie()
        output_queue = []
        operator_stack = []
        while characters:
            character = characters.pop(0)
            if trie.is_number(character):
                output_queue.append(character)
            elif trie.is_function(character, functions):
                operator_stack.append(character)
            elif trie.is_operator(character, operators):
                while (
                    operator_stack and
                    trie.is_operator(operator_stack[-1], operators) and
                    (
                        trie.precedence(operator_stack[-1], operators) > trie.precedence(character, operators) or
                        (trie.precedence(operator_stack[-1], operators) == trie.precedence(character, operators) and trie.is_left_associative(character, left_associative_operators))
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
                if operator_stack and trie.is_function(operator_stack[-1], functions):
                    output_queue.append(operator_stack.pop())

        while operator_stack:
            output_queue.append(operator_stack.pop())

        return output_queue    

    @staticmethod
    def compute_expression(
        evaluated_expression,
        operators,
        functions
    ):
        trie = Trie()
        # Use a stack to handle operator precedence
        stack = []
        print(f"result: {evaluated_expression}")
        for character in evaluated_expression:
            if trie.is_number(character):
                stack.append(float(character))
            elif trie.is_operator(character, operators):
                operator = character
                # Pop the last two elements from the stack as operands
                operand2 = stack.pop()
                operand1 = stack.pop()
                operation_result = trie.perform_operation(operand1, operand2, operator)
                # Perform the operation and push the result back to the stack
                stack.append(operation_result)

            elif trie.is_function(character, functions):
                function = character
                operand = stack.pop()
                # Perform the function and push the result back to the stack
                function_result = trie.perform_function(function, operand)
                stack.append(function_result)

        # The final result is the last element in the stack
        return stack.pop()
    
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

        evaluated_expression = Trie.evaluate_expression(
            operators_and_variables,
            operators,
            functions,
            left_associative_operators
        )
        computed_result = Trie.compute_expression(
            evaluated_expression,
            operators,
            functions
        )
        return(computed_result)

        # print(result2)

        #     def evaluate_postfix(output_queue):
        #         stack = []
        #         for token in output_queue:
        #             if isinstance(token, numbers.Number):
        #                 stack.append(token)
        #             elif token in operators:
        #                 operand2 = stack.pop()
        #                 operand1 = stack.pop()
        #                 result = operators[token](operand1, operand2)
        #                 stack.append(result)
        #         return stack.pop()
            
        #     res = evaluate_postfix(output_queue)
        #     return res

        # expression = ['2', '/', '(', '86', '+', '3', '*', '(', '2', '+', '86', ')', ')']
        # result = evaluate_expression(expression)
        # print(f"rsult: {result}") # Output: 0.023255813953488372


        
        # final_res = evaluate_postfix(result)
        # print(f"final res: {final_res}")


        # def evaluate_expression2(expression):
        #     stack = []
        #     for char in expression:
        #         if char in self.operator_precedence:
        #             if char == '(':
        #                 stack.append(char)
        #             elif char == ')':
        #                 while stack[-1] != '(':
        #                     operator = stack.pop()
        #                     operand2 = stack.pop()
        #                     operand1 = stack.pop()
        #                     result = self.operator_precedence[operator](operand1, operand2)
        #                     stack.append(result)
        #                 stack.pop() # remove the open parenthesis
        #             else:
        #                 while stack and stack[-1] in self.operator_precedence:
        #                     operator = stack.pop()
        #                     operand2 = stack.pop()
        #                     operand1 = stack.pop()
        #                     result = self.operator_precedence[operator](operand1, operand2)
        #                     stack.append(result)
        #                 stack.append(char)
        #         else:
        #             stack.append(int(char))
        #     while stack:
        #         operator = stack.pop()
        #         operand2 = stack.pop()
        #         operand1 = stack.pop()
        #         result = self.operator_precedence[operator](operand1, operand2)
        #         stack.append(result)
        #     return stack.pop()

        # expression = [2, '/', '(', 86, '+', 3, '*', '(', 2, '+', 86, ')', ')']
        # result2 = evaluate_expression2(expression)

        # def evaluate_expression(operators_and_variables):
        #     stack = []
        #     for token in operators_and_variables:
        #         if token in operators:
        #             operator = operators[token]
        #             operand2 = stack.pop()
        #             operand1 = stack.pop()
        #             result = operator(operand1, operand2)
        #             stack.append(result)
        #         elif token in self.variables:
        #             stack.append(self.variables[token])
        #         else:
        #             stack.append(float(token))
        #     return stack.pop()


        # def evaluate_expression(expression):
        #     # operators = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '^': operator.pow}
        #     stack = []
        #     for char in expression:
        #         if char in operators:
        #             operand2 = stack.pop()
        #             operand1 = stack.pop()
        #             result = operators[char](operand1, operand2)
        #             stack.append(result)
        #         else:
        #             stack.append(float(char))
        #     return stack.pop()


        # for i in match_operators_and_variables:
        #     if i in variables.values():
        #         print(f"variable: {i}")
        #     elif i in operators:
        #         print(f"operator: {i}")

        # Replace trigonometric and logarithmic functions with their python equivalents
        # formula = formula.replace("sin", "math.sin")
        # formula = formula.replace("cos", "math.cos")
        # formula = formula.replace("tan", "math.tan")
        # formula = formula.replace("log", "math.log10")

        # computation =computation.split("COMPUTE")[1].strip()
        # print(computation)


        # def process_computation(characters):

        #     output_queue = []
        #     operator_stack = []

        #     for char in characters:
        #         if re.match(r"\d+", char):
        #             output_queue.append(char)
        #         elif re.match(r"[+-/*^]", char):
        #             while operator_stack and re.match(r"[+-/*^]", operator_stack[-1]):
        #                 output_queue.append(operator_stack.pop())
        #             operator_stack.append(char)
        #         elif char == "(":
        #             operator_stack.append(char)
        #         elif char == (")"):
        #             while operator_stack and operator_stack[-1] != "(":
        #                 output_queue.append(operator_stack.pop())
        #             operator_stack.pop()
        #     while operator_stack:
        #         output_queue.append(operator_stack.pop())
        #     return output_queue

        # value = process_computation(computation)
        # return value

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
