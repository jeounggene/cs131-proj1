from intbase import *
from brewparse import parse_program


class Interpreter(InterpreterBase):
    global var

    def __init__(self, console_output=True, inp=None, trace_output=False, ):
        super().__init__(console_output, inp)  # call InterpreterBase's constructor

    def run(self, program):
        global var

        parsed_program = parse_program(program)
        var = {}

        # check if main exists
        if len(parsed_program.dict['functions']) > 1 or len(parsed_program.dict['functions']) <= 0 or parsed_program.dict['functions'][0].dict['name'] != 'main':
            super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
        main_func_node = parsed_program.dict['functions'][0]
        self.run_func(main_func_node)

    def run_func(self, func_node):
        for statement_node in func_node.dict['statements']:
            self.run_statement(statement_node)

    def run_statement(self, statement_node):
        if self.is_assignment(statement_node):
            self.do_assignment(statement_node)
        elif self.is_func_call(statement_node):
            if self.is_print_call(statement_node):
                self.do_print_call(statement_node)
            elif self.is_inputi_call(statement_node):
                self.do_inputi_call(statement_node)
            else:
                super().error(
                    ErrorType.NAME_ERROR,
                    "Undefined behavior",
                )

    def do_assignment(self, statement_node):
        global var
        # target_var_name = get_target_variable_name(statement_node)
        target_var_name = statement_node.dict['name']
        # source_node = get_expression_node(statement_node)
        source_node = statement_node.dict['expression']
        resulting_value = self.evaluate_expression(source_node)
        # this.variable_name_to_value[target_var_name] = resulting_value
        var[target_var_name] = resulting_value

    def evaluate_expression(self, expression_node):
        if self.is_value_node(expression_node):
            return self.get_value(expression_node)
        elif self.is_variable_node(expression_node):
            return self.get_value_of_variable(expression_node)
        elif self.is_binary_operator(expression_node):
            return self.evaluate_binary_operator(expression_node)
        elif self.is_func_call(expression_node):
            return self.do_inputi_call(expression_node)

    def evaluate_binary_operator(self, expression_node):  # ONLY INTS
        fir = expression_node.dict['op1']
        sec = expression_node.dict['op2']

        fir_expression = self.evaluate_expression(fir)
        sec_expression = self.evaluate_expression(sec)

        if self.is_value_string(fir_expression) or self.is_value_string(sec_expression):
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

        if expression_node.elem_type == '+':
            return fir_expression + sec_expression
        elif expression_node.elem_type == '-':
            return fir_expression - sec_expression

        else:  # TODO: Check if right kind of error
            super().error(
                ErrorType.NAME_ERROR,
                "Undefined behavior",
            )

    def do_print_call(self, expression_node):
        if expression_node.dict['name'] == 'print':
            a = ""
            # if len(expression_node.dict['args']) > 1:
            for arg in expression_node.dict['args']:
                a += str(self.evaluate_expression(arg))
            super().output(a)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                "Undefined behavior",
            )

    def do_inputi_call(self, expression_node):
        if expression_node.dict['name'] == 'inputi':
            if len(expression_node.dict['args']) == 0:
                user_input = super().get_input()
                return int(user_input)

            elif len(expression_node.dict['args']) == 1:
                super().output(self.evaluate_expression(
                    expression_node.dict['args'][0]))
                user_input = super().get_input()
                return int(user_input)

            if len(expression_node.dict['args']) > 1:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"No inputi() function found that takes > 1 parameter",
                )
        else:
            super().error(
                ErrorType.NAME_ERROR,
                "Undefined behavior",
            )

    # Getter functions
    def get_value(self, expression_node):
        return expression_node.dict['val']

    def get_value_of_variable(self, variable_node):
        if var.get(variable_node.dict['name']) is not None:
            return var[variable_node.dict['name']]
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {variable_node.dict['name']} has not been defined",
            )

    # 'is' (boolean) functions
    def is_assignment(self, statement_node):
        return statement_node.elem_type == '='

    def is_func_call(self, statement_node):
        return statement_node.elem_type == 'fcall'

    def is_print_call(self, expression_node):
        return expression_node.dict['name'] == 'print'

    def is_inputi_call(self, expression_node):
        return expression_node.dict['name'] == 'inputi'

    def is_value_int(self, value_node):
        return value_node.elem_type == 'int'

    def is_value_string(self, value_node):
        return isinstance(value_node, str)

    def is_value_node(self, value_node):
        return value_node.elem_type == 'int' or value_node.elem_type == 'string'

    def is_value_same_type(self, value_node1, value_node2):
        if self.is_value_int(value_node1) and self.is_value_int(value_node2):
            return True
        elif self.is_value_string(value_node1) and self.is_value_string(value_node2):
            return True
        return False

    def is_variable_node(self, variable_node):
        return variable_node.elem_type == 'var'

    def is_binary_operator(self, expression_node):
        return expression_node.elem_type == '+' or expression_node.elem_type == '-'
