class Interpreter:
    def __init__(self):
        self.stack = []
        self.env = {}       # Variable environment
        self.functions = {} # Function definitions

    def eval_node(self, node):
        if isinstance(node, list):
            cmd = node[0]
            if cmd == 'infix':
                value = self.eval_infix(node[1:])
                self.stack.append(value)
            elif cmd == '.s':
                print(self.stack)
            elif cmd == 'puts':
                if len(node) > 1:
                    value = self.eval_node(node[1])
                    print(value)
                elif self.stack:
                    print(self.stack.pop())
                else:
                    print()
            elif cmd == 'fn':
                name = node[1]
                body = node[2]
                self.functions[name] = body
            elif cmd == 'block':
                for stmt in node[1:]:
                    self.eval_node(stmt)
            elif cmd == 'dup':
                if self.stack:
                    self.stack.append(self.stack[-1])
                else:
                    # Instead of raising an exception, handle gracefully by adding a placeholder value
                    self.stack.append(0)
            elif cmd == 'when':
                condition = node[1]
                block = node[2]
                cond_value = self.eval_node(condition)
                if cond_value:
                    self.eval_node(block)
            else:
                # Function call
                fn_name = cmd
                args = node[1:]
                # Push arguments onto the stack
                for arg in args:
                    self.stack.append(self.eval_node(arg))
                result = self.call_function(fn_name)
                return result
        else:
            # Handle literals and variables
            if isinstance(node, str):
                if node.startswith('"') and node.endswith('"'):
                    return bytes(node[1:-1], "utf-8").decode("unicode_escape")
                elif node in self.env:
                    return self.env[node]
                elif node == '$':
                    if self.stack:
                        return self.stack.pop()
                    else:
                        raise Exception("Stack is empty, cannot pop value for '$'")
                else:
                    try:
                        return float(node)
                    except ValueError:
                        raise Exception(f"Unknown variable or value: {node}")
            else:
                return node

    def eval_infix(self, expr):
        # Handle assignments
        if '=' in expr:
            index = expr.index('=')
            var_name = expr[index - 1]
            value_expr = expr[index + 1:]
            value = self.eval_infix(value_expr)
            self.env[var_name] = value
            return value
        else:
            # Evaluate expressions
            tokens = [self.eval_node(token) if isinstance(token, list) else token for token in expr]
            stack = []
            operators = {'+', '-', '*', '/', '>', '<', '=='}

            for token in tokens:
                if token in operators:
                    stack.append(token)
                else:
                    if token == '$':
                        if self.stack:
                            value = self.stack.pop()
                        else:
                            raise Exception("Stack is empty, cannot use '$'")
                    elif isinstance(token, str) and token in self.env:
                        value = self.env[token]
                    else:
                        try:
                            value = float(token)
                        except ValueError:
                            raise Exception(f"Unknown variable or value: {token}")
                    while stack and stack[-1] in operators:
                        op = stack.pop()
                        if len(stack) == 0:
                            stack.append(value)
                            break
                        operand = stack.pop()
                        if op == '+':
                            value = operand + value
                        elif op == '-':
                            value = operand - value
                        elif op == '*':
                            value = operand * value
                        elif op == '/':
                            value = operand / value
                        elif op == '>':
                            value = 1.0 if operand > value else 0.0
                        elif op == '<':
                            value = 1.0 if operand < value else 0.0
                        elif op == '==':
                            value = 1.0 if operand == value else 0.0
                    stack.append(value)
            return stack[0] if stack else 0

    def call_function(self, fn_name):
        if fn_name in self.functions:
            body = self.functions[fn_name]
            # Use a local stack and environment for the function
            saved_stack = self.stack
            saved_env = self.env
            self.stack = saved_stack[:]  # Make a copy of the current stack
            self.env = saved_env.copy()  # Make a copy of the current environment
            self.eval_node(body)
            result = self.stack.pop() if self.stack else None
            self.stack = saved_stack
            self.env = saved_env
            return result
        else:
            raise Exception(f"Unknown function '{fn_name}'")

# The provided AST
ast = [
    ['infix', '1', '+', '2', '+', '3.1'],
    ['.s'],
    ['puts'],
    ['infix', 'a', '=', '5'],
    ['puts', 'a'],
    ['fn', 'double', [
        'block',
        ['dup'],
        ['infix', '$', '+', '$'],
    ]],
    ['puts', '"before"'],
    ['puts', ['double', '10']],
    ['puts', '"after"'],
    ['when', ['infix', 'a', '>', '1'], [
        'block',
        ['puts', '"big"'],
    ]],
    ['puts', '"end"'],
]

# Create an interpreter instance and execute the AST
interpreter = Interpreter()
for stmt in ast:
    interpreter.eval_node(stmt)
