import re
import json

class Node:
    def __init__(self, type_, left=None, right=None, value=None):
        self.type = type_  # 'operator' or 'operand'
        self.left = left
        self.right = right
        self.value = value  # For operands: ('age', '>', 30)

    def __repr__(self):
        if self.type == 'operator':
            return f"({self.left} {self.value} {self.right})"
        else:
            return f"{self.value[0]} {self.value[1]} {self.value[2]}"

def tokenize(rule_string):
   
    token_specification = [
        ('NUMBER',   r'\b\d+(\.\d*)?\b'),  # Integer or decimal number
        ('STRING',   r"'[^']*'"),          # String enclosed in single quotes
        ('ID',       r'\b\w+\b'),          # Identifiers
        ('OP',       r'<=|>=|!=|=|<|>'),   # Operators
        ('AND',      r'\bAND\b'),          # AND operator
        ('OR',       r'\bOR\b'),           # OR operator
        ('LPAREN',   r'\('),               # Left Parenthesis
        ('RPAREN',   r'\)'),               # Right Parenthesis
        ('SKIP',     r'[ \t]+'),           # Skip spaces and tabs
        ('MISMATCH', r'.'),                # Any other character
    ]
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(token_regex).match
    line = rule_string
    pos = 0
    tokens = []
    match = get_token(line)
    while match is not None:
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'NUMBER':
            tokens.append(('NUMBER', float(value) if '.' in value else int(value)))
        elif kind == 'STRING':
            tokens.append(('STRING', value.strip("'")))
        elif kind == 'ID':
            if value == 'AND' or value == 'OR':
                tokens.append((value, value))
            else:
                tokens.append(('ID', value))
        elif kind == 'OP':
            tokens.append(('OP', value))
        elif kind == 'LPAREN':
            tokens.append(('LPAREN', value))
        elif kind == 'RPAREN':
            tokens.append(('RPAREN', value))
        elif kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {value!r} at position {pos}')
        pos = match.end()
        match = get_token(line, pos)
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        node = self.expression()
        if self.pos < len(self.tokens):
            raise RuntimeError('Unexpected token at the end')
        return node

    def match(self, expected_types):
        if self.pos < len(self.tokens):
            token_type, value = self.tokens[self.pos]
            if token_type in expected_types:
                self.pos += 1
                return token_type, value
        return None, None

    def expression(self):
        node = self.term()
        while True:
            token_type, value = self.match(['OR'])
            if token_type:
                right = self.term()
                node = Node('operator', left=node, right=right, value='OR')
            else:
                break
        return node

    def term(self):
        node = self.factor()
        while True:
            token_type, value = self.match(['AND'])
            if token_type:
                right = self.factor()
                node = Node('operator', left=node, right=right, value='AND')
            else:
                break
        return node

    def factor(self):
        token_type, value = self.match(['LPAREN'])
        if token_type:
            node = self.expression()
            if not self.match(['RPAREN']):
                raise RuntimeError('Expected )')
            return node
        else:
            return self.comparison()

    def comparison(self):
        token_type, left_value = self.match(['ID'])
        if not token_type:
            raise RuntimeError('Expected identifier')
        token_type, op_value = self.match(['OP'])
        if not token_type:
            raise RuntimeError('Expected operator')
        token_type, right_value = self.match(['NUMBER', 'STRING', 'ID'])
        if not token_type:
            raise RuntimeError('Expected number or string')
        return Node('operand', value=(left_value, op_value, right_value))

def create_rule(rule_string):
    tokens = tokenize(rule_string)
    parser = Parser(tokens)
    ast = parser.parse()
    return ast

def combine_rules(rule_strings):
    asts = [create_rule(rule_str) for rule_str in rule_strings]
    if not asts:
        return None
    combined_ast = asts[0]
    for ast in asts[1:]:
        combined_ast = Node('operator', left=combined_ast, right=ast, value='OR')
    return combined_ast

def evaluate_rule(ast, data):
    if ast.type == 'operator':
        left_val = evaluate_rule(ast.left, data)
        right_val = evaluate_rule(ast.right, data)
        if ast.value == 'AND':
            return left_val and right_val
        elif ast.value == 'OR':
            return left_val or right_val
    elif ast.type == 'operand':
        attr, op, value = ast.value
        if attr not in data:
            raise RuntimeError(f'Attribute {attr} not in data')
        data_value = data[attr]
        if op == '=':
            return data_value == value
        elif op == '!=':
            return data_value != value
        elif op == '>':
            return data_value > value
        elif op == '<':
            return data_value < value
        elif op == '>=':
            return data_value >= value
        elif op == '<=':
            return data_value <= value
        else:
            raise RuntimeError(f'Unknown operator {op}')
    else:
        raise RuntimeError(f'Unknown node type {ast.type}')


if __name__ == '__main__':
    # Sample Rules
    rule1 = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
    rule2 = "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)"


    ast1 = create_rule(rule1)
    print("AST for rule1:")
    print(ast1)

    ast2 = create_rule(rule2)
    print("\nAST for rule2:")
    print(ast2)

    
    combined_ast = combine_rules([rule1, rule2])
    print("\nCombined AST:")
    print(combined_ast)

    
    data1 = {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}
    data2 = {"age": 22, "department": "Marketing", "salary": 30000, "experience": 2}
    data3 = {"age": 40, "department": "Marketing", "salary": 25000, "experience": 6}
    data4 = {"age": 28, "department": "HR", "salary": 40000, "experience": 4}

   
    print("\nEvaluating data1:")
    result1 = evaluate_rule(combined_ast, data1)
    print(f"Result: {result1}")

    print("\nEvaluating data2:")
    result2 = evaluate_rule(combined_ast, data2)
    print(f"Result: {result2}")

    print("\nEvaluating data3:")
    result3 = evaluate_rule(combined_ast, data3)
    print(f"Result: {result3}")

    print("\nEvaluating data4:")
    result4 = evaluate_rule(combined_ast, data4)
    print(f"Result: {result4}")
