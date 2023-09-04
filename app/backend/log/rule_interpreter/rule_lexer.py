import ply.lex as lex
from app.backend.log.constants import THIS_TOK, ACCUMULATIVE_TOK, RUNNING_TOTAL_TOK, PARALLEL_TOK, SERIES_TOK
from app.backend.log.rule_interpreter.rule_error import RuleError


class RuleLexer:
    def __init__(self):
        self.rules_as_text: str = ""
        self.reserved: dict = {'if': 'if', 'then': 'then', 'skip': 'skip', 'insert': 'insert'}
        self.tokens: [str] = [
            'identifier', 'value', 'equality', 'semicolon', 'this_tok', 'accumulative_tok', 'lb_tok', 'rb_tok',
            'running_total_tok', 'parallel_tok', 'series_tok', 'normal_tok', 'uniform_tok'
        ]
        self.tokens += list(self.reserved.values())
        self.t_value: str = r'(\-)?\d+(\.\d+)?'
        self.t_equality: str = r'<=|>=|<|>|==|!='
        self.t_semicolon: str = r'\;'
        self.t_this_tok: str = f'\\{THIS_TOK}'
        self.t_accumulative_tok: str = f'\\{ACCUMULATIVE_TOK}'
        self.t_running_total_tok: str = f'\\{RUNNING_TOTAL_TOK}'
        self.t_parallel_tok: str = f'\\{PARALLEL_TOK}'
        self.t_series_tok: str = f'\\{SERIES_TOK}'
        self.t_normal_tok: str = r'\?N'
        self.t_uniform_tok: str = r'\?U'
        self.t_lb_tok: str = r'\('
        self.t_rb_tok: str = r'\)'
        self.t_ignore: str = ' \t'
        self.t_ignore_comment = r'\/\/.*'  # Anything after '//' is ignored until a new line.
        self.lexer: lex.Lexer = lex.lex(module=self)

    def t_identifier(self, t) -> lex.LexToken:
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        t.type = self.reserved.get(t.value, 'identifier')  # Check if token is a reserved word
        return t

    @staticmethod
    def t_newline(token) -> None:
        r"""\n+"""
        token.lexer.lineno += len(token.value)

    def find_column(self, token) -> int:
        line_start = self.rules_as_text.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    def t_error(self, token) -> None:
        lines: [str] = self.rules_as_text.split('\n')
        error_line: str = lines[token.lineno - 1]
        lexer_error: str = "Lexing error:\n"
        lexer_error += f"--> Input line: \"{error_line}\".\n"
        lexer_error += f"--> Invalid character: \"{token.value[0]}\".\n"
        lexer_error += f"--> Position: line={token.lineno}, index={self.find_column(token)}.\n"
        raise RuleError(lexer_error)

    def input(self, rules_as_text: str) -> None:
        self.rules_as_text = rules_as_text
        self.lexer.input(rules_as_text)

    def token(self) -> lex.LexToken | None:
        return self.lexer.token()
