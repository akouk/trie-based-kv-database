import math
import typing as tp

class MathExpressionEvaluator:
    
    @staticmethod
    def is_operator(character: str, operator_precedence: dict) -> bool:
        return character in operator_precedence

    @staticmethod
    def precedence(character: str, operator_precedence: dict) -> int:
        return operator_precedence[character]

    @staticmethod
    def is_function(character: str, function_precedence: dict) -> bool:
        return character in function_precedence

    @staticmethod
    def is_number(character: str) -> bool:
        if character.isnumeric():
            return True
        return False

    @staticmethod
    def is_left_associative(character: str, left_associative_operators: list) -> bool:
        return character in left_associative_operators

    @staticmethod
    def perform_operation(operand1: float, operand2: float, operator: str) -> float:
        if operator == '+':
            return operand1 + operand2
        elif operator == '-':
            return operand1 - operand2
        elif operator == '*':
            return operand1 * operand2
        elif operator == '/':
            return operand1 / operand2
        elif operator == '^':
            return operand1 ** operand2
        else:
            return 'Invalid operand!'

    @staticmethod
    def perform_function(function: str, operand: float) -> float:
        if function == 'sin':
            return math.sin(operand)
        elif function == 'cos':
            return math.cos(operand)
        elif function == 'tan':
            return math.tan(operand)
        elif function == 'log':
            return math.log10(operand)
        else:
            return 'Invalid function!'

    def evaluate_expression(
        self,
        characters: tp.List[str],
        operators: dict,
        functions: dict,
        left_associative_operators: tp.List[str]
    ) -> tp.List[tp.Union[str, int]]:

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

    def compute_expression(
        self,
        evaluated_expression: tp.List[str],
        operators: dict,
        functions: dict
    ) -> tp.Union[float, str]:
        
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
