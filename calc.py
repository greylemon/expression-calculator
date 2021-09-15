import sys

ERROR_FUNCTION_MISSING_BRACKETS = \
    'Function expression must be contained in opening and closing brackets'
ERROR_FUNCTION_MISSING_PARAM = \
    'Function expression must contain both operation and arguments'
ERROR_FUNCTION_INVALID_OPERATION = \
    'Function expression operation must be defined'
ERROR_FUNCTION_INVALID_INPUTS = \
    'Function expression inputs must be valid'
ERROR_FUNCTION_INVALID_ARGUMENTS_COUNT = \
    'Function expression arguments count does not match the operations config'


class Error(Exception):
    pass


class ExpressionError(Error):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


# Base calculator functions

def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def exponent(base, power):
    return base ** power


# Calculator functions that can accept arbitrary arguments

def generic_tail_recursion(function, args, acc):
    '''
    Generic tail recursion function with a higher ordered function

    function: (a, b) => number
    args: number[]
    acc: number
    '''

    if len(args) == 0:
        return acc
    return generic_tail_recursion(function, args[1:], function(acc,
                                                               args[0]))


def tail_add(args, acc=0):
    return generic_tail_recursion(add, args, acc)


def tail_multiply(args, acc=1):
    return generic_tail_recursion(multiply, args, acc)


def tail_exponent(args):
    return generic_tail_recursion(exponent, args[1:], args[0])


# Operations config

# Contains the functions used for the calculator, along with config such as
# argument counts

# Structure of operations: {
#   [Operation]: {
#     arguments_count: number | "any"
#     function: (args: number[]) => integer
#   }
# }
operations = {
    'add': {'arguments_count': "any", 'function': tail_add},
    'multiply': {'arguments_count': "any", 'function': tail_multiply},
    'exponent': {'arguments_count': 2, 'function': tail_exponent}}


def is_brackets_valid(expression):
    '''
    Checks if expression has the correct structure of 
    opening and enclosing brackets
    '''
    opening_brackets = 0
    for i in range(len(expression)):
        char = expression[i]

        if char == '(':
            opening_brackets += 1
        elif char == ')':
            if opening_brackets <= 0:
                return False
            opening_brackets -= 1

    if opening_brackets > 0:
        return False
    return True


def find_end_of_expression(expression, start_index):
    '''
    returns the end index of an expression
    '''
    end_index = start_index + 1
    if expression[start_index] != '(':
        while end_index < len(expression) and expression[end_index] \
                != ' ' and expression[end_index] != ')':
            if not expression[end_index].isnumeric():
                raise ExpressionError(expression,
                                      ERROR_FUNCTION_INVALID_INPUTS)
            end_index += 1
        return end_index

    open_brackets_count = 1
    while open_brackets_count:
        if expression[end_index] == '(':
            open_brackets_count += 1
        elif expression[end_index] == ')':
            open_brackets_count -= 1

        end_index += 1

    return end_index


def calculator(expression):
    '''
    Problem: https://gist.github.com/rraval/2ef5e2ff228e022653db2055fc12ea9d

    Evaluates the expression with the following grammar:

    ---------------------------------------------------------------------------
    DIGIT = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";

    EXPR = INTEGER | ADD | MULTIPLY;

    INTEGER = DIGIT, { DIGIT };

    ADD = "(", "a", "d", "d", " ", EXPR, " ", EXPR, ")";

    MULTIPLY = "(", "m", "u", "l", "t", "i", "p", "l", "y", " ", EXPR, " ", EXPR, ")";

    ---------------------------------------------------------------------------

    Doc tests 

    ~~ Multiplication ~~
    >>> calculator("(multiply 1 1)")
    1
    >>> calculator("(multiply 0 (multiply 3 4))")
    0
    >>> calculator("(multiply 2 (multiply 3 4))")
    24
    >>> calculator("(multiply 3 (multiply (multiply 3 3) 3))")
    81

    ~~ Addition ~~
    >>> calculator("(add 1 1)")
    2
    >>> calculator("(add 0 (add 3 4))")
    7
    >>> calculator("(add 3 (add (add 3 3) 3))")
    12

    ~~ Exponent ~~
    >>> calculator("(exponent 2 1)")
    2
    >>> calculator("(exponent 2 2)")
    4
    >>> calculator("(exponent 2 3)")
    8
    '''
    # Check for proper bracketing
    # Could be moved in outer function for single check

    if not is_brackets_valid(expression):
        raise ExpressionError(expression,
                              ERROR_FUNCTION_MISSING_BRACKETS)

    if expression.isnumeric():
        return int(expression)
    else:
        # Case where expression is of the form (FUNC EXPR EXPR)
        # Check for opening and closing brackets

        if len(expression) < 2 or expression[0] != '(' \
                or expression[-1] != ')':
            raise ExpressionError(expression,
                                  ERROR_FUNCTION_MISSING_BRACKETS)

        # Content inside bracket

        inner_content = expression[1:-1]
        parsed_function_expression = inner_content.split(' ', 1)

        # Validate operation and arguments

        if len(parsed_function_expression) != 2:
            raise ExpressionError(expression,
                                  ERROR_FUNCTION_MISSING_PARAM)

        (operation, arguments) = parsed_function_expression

        if operation not in operations:
            raise ExpressionError(expression,
                                  ERROR_FUNCTION_INVALID_OPERATION)

        arguments_count = operations[operation]['arguments_count']
        operation_function = operations[operation]['function']

        # Allow arguments to be variable based on the operations mapping

        evaluated_arguments = []
        start_index = len(operation) + 2

        # check if arguments count is set to any or fixed number in operations config, then handle each cases

        # For unlimited arguments:  while start_index < len(expression):
        # For fixed arguments:      for i in range(arguments_count):

        i = 0
        is_arguments_unlimited = arguments_count == 'any'

        while is_arguments_unlimited and start_index < len(expression) \
                or not is_arguments_unlimited and i < arguments_count:
            end_index = find_end_of_expression(expression, start_index)
            argument_expression = expression[start_index:end_index]
            evaluated_expression = calculator(argument_expression)
            evaluated_arguments.append(evaluated_expression)

            start_index = end_index + 1
            i += 1

        # Check if the arguments count in the expression exceeds the one 
        # present in the operations config
        if not is_arguments_unlimited and start_index < len(expression):
            raise ExpressionError(expression,
                                  ERROR_FUNCTION_INVALID_ARGUMENTS_COUNT)

        return operation_function(evaluated_arguments)


if __name__ == '__main__':
    expr = sys.argv[1]
    print(calculator(expr))

    # import doctest
    # doctest.testmod()
