import math 
from decimal import Decimal
import typing as tp

class MathExpressionEvaluator:
    
    @staticmethod
    def is_operator(character: str, operator_precedence: dict) -> bool:
        """
        Check if the given character is an operator.
        The operator_precedence is used to check the operator precedence
        """
        return character in operator_precedence

    @staticmethod
    def precedence(character: str, operator_precedence: dict) -> int:
        """
        Get the precedence of the operator
        """
        return operator_precedence[character]

    @staticmethod
    def is_function(character: str, function_precedence: dict) -> bool:
        """
        Check if the given character is a function
        The function_precedence is used to check the function precedence
        """
        return character in function_precedence

    @staticmethod
    def is_float(character):
        """
        Check if the given character is a float number
        """
        try:
            float(character)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_int(character: str) -> bool:
        """
        Check if the given character is an integer
        """
        try:
            int(character)
            return True
        except ValueError:
            return False
       
    @staticmethod
    def is_left_associative(character: str, left_associative_operators: list) -> bool:
        """
        Check if the given operator is left associative
        """
        return character in left_associative_operators
        
    @staticmethod
    def perform_operation(operand1, operand2, operator):
        """
        Perform a mathematical operation between two operands using the given operator
        """
        operand1 = Decimal(operand1)
        operand2 = Decimal(operand2)
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
        
        return 'Invalid operand!'

    @staticmethod
    def perform_function(function, operand):
        """
        Perform a mathematical function operation based the given operator
        """
        operand = Decimal(operand)
        if function == 'sin':
            return math.sin(operand)
        elif function == 'cos':
            return math.cos(operand)
        elif function == 'tan':
            return math.tan(operand)
        elif function == 'log':
            return math.log10(operand)
    
        return 'Invalid function!'

    def evaluate_expression(
        self,
        characters: tp.List[str],
        operators: dict,
        functions: dict,
        left_associative_operators: tp.List[str]
    ) -> tp.List[tp.Union[str, int]]:
        
        # Initialize two empty lists, one for output and one for operators
        output_queue = []
        operator_stack = []

        while characters:
            character = characters.pop(0)
            if self.is_int(character):
                output_queue.append(character)
            elif self.is_float(character):
                output_queue.append(character)
            elif self.is_function(character, functions):
                operator_stack.append(character)
            elif self.is_operator(character, operators):
                # While the operator stack is not empty and the last element is an operator
                # with greater precedence or has the same precedence but is left associative
                while (
                    operator_stack and
                    self.is_operator(operator_stack[-1], operators) and
                    (
                        self.precedence(operator_stack[-1], operators) > self.precedence(character, operators) or
                        (self.precedence(operator_stack[-1], operators) == self.precedence(
                            character, operators) and self.is_left_associative(character, left_associative_operators))
                    )
                ):
                    # Pop elements from the operator stack and append to output queue
                    output_queue.append(operator_stack.pop())
                # Append the current operator to the operator stack
                operator_stack.append(character)
            elif character == '(':
                operator_stack.append(character)
            elif character == ')':
                # While the operator stack is not empty and the last element is not "("
                while operator_stack and operator_stack[-1] != '(':
                    # Pop elements from the operator stack and append to output queue
                    output_queue.append(operator_stack.pop())
                # If the last element of operator stack is "(", pop it
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                # Check if the last element of operator stack is a function, 
                # if so pop it and append to the output queue
                if operator_stack and self.is_function(operator_stack[-1], functions):
                    output_queue.append(operator_stack.pop())

        # While the operator stack is not empty, pop elements and append to output queue
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
        for character in evaluated_expression:
            if self.is_int(character):
                stack.append(int(character))
            elif self.is_float(character):
                stack.append(float(character))
            elif self.is_operator(character, operators):
                operator = character
                # Pop the last two elements from the stack as operands
                operand2 = stack.pop()
                operand1 = stack.pop()
                operation_result = self.perform_operation(
                    operand1, operand2, operator)
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
