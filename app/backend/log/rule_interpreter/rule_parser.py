import ply.yacc as yacc
from ply import lex
from app.backend.log.constants import THIS_TOK, PARALLEL_TOK, SERIES_TOK
from app.backend.log.models.enum_types import DistributionType, EqualityType, ActionType
from app.backend.log.models.process_model import ProcessModel
from app.backend.log.models.rule_model import RuleModel
from app.backend.log.rule_interpreter.rule_error import RuleError
from app.backend.log.rule_interpreter.rule_lexer import RuleLexer


# below suppresses spelling/punctuation warnings in my IDE.
# noinspection GrazieInspection
class RuleParser:
    def __init__(self, rule_lexer: RuleLexer, process_model: ProcessModel):
        self.__process_model: ProcessModel = process_model
        self.__rules_as_text: str = ""
        self.__container: dict = {'if_event_name': '', 'attribute_dict': {}, 'event_list': []}
        self.__rules: list[RuleModel] = []
        self.__dist_type: DistributionType = DistributionType.FIXED
        self.__dist_params: tuple = ()
        self.reserved: dict = rule_lexer.reserved
        self.tokens: list[str] = rule_lexer.tokens
        self.lexer: lex.Lexer = rule_lexer.lexer
        self.parser: yacc.LRParser = yacc.yacc(module=self)

    def parse(self, rules_as_text: str) -> [RuleModel]:
        self.__rules_as_text: str = rules_as_text
        self.parser.parse(lexer=self.lexer)
        return self.__rules

    # --- Beginning of Production Rules --- #

    def p_rules(self, rules) -> None:
        """rules : rules rule semicolon
                 | empty"""
        pass

    def p_rule(self, rule_toks) -> None:
        """rule : if identifier expr then action
                | if rt_expr then action"""
        if not self.__container['use_running_total']:
            self.__container['if_event_name'] = rule_toks[2]
        rule: RuleModel = RuleModel(
            rule_number=len(self.__rules) + 1,
            if_event_name=self.__container['if_event_name'],
            attribute_name=self.__container['attribute_name'],
            equality_type=self.__container['equality_type'],
            attribute_value=self.__container['attribute_value'],
            action_type=self.__container['action_type'],
            then_event_name=self.__container['then_event_name'],
            inserted_event_attributes_dict=self.__container['attribute_dict'],
            use_accumulative_total=self.__container['use_accumulative_total'],
            use_running_total=self.__container['use_running_total'],
            event_list=self.__container['event_list']
        )
        if rule in self.__rules:
            raise RuleError(f"Rule {rule.rule_number}: \"{rule.get_as_str()}\" has already been defined.")
        rule.validate_rule(process_model=self.__process_model)
        self.__rules.append(rule)
        self.__reset_container()

    def p_expr(self, expr_toks) -> None:
        """expr : this_tok identifier equality value
                | accumulative_tok identifier equality value"""
        self.__container['use_running_total'] = False
        if expr_toks[1] == THIS_TOK:
            self.__container['use_accumulative_total'] = False
        else:
            self.__container['use_accumulative_total'] = True
        self.__container['attribute_name'] = expr_toks[2]
        self.__container['equality_type'] = EqualityType(expr_toks[3])
        self.__container['attribute_value'] = float(expr_toks[4])

    def p_rt_expr(self, rt_expr_toks) -> None:
        """rt_expr : running_total_tok identifier equality value"""
        self.__container['use_running_total'] = True
        self.__container['use_accumulative_total'] = True  # Doesn't matter
        self.__container['attribute_name'] = rt_expr_toks[2]
        self.__container['equality_type'] = EqualityType(rt_expr_toks[3])
        self.__container['attribute_value'] = float(rt_expr_toks[4])

    def p_action(self, action_toks) -> None:
        """action : skip identifier
                  | insert identifier lb_tok attributes rb_tok
                  | insert identifier
                  | parallel_list
                  | series_list"""
        if action_toks[1] == "skip":
            self.__container['action_type'] = ActionType.SKIP
            self.__container['then_event_name'] = action_toks[2]
        elif action_toks[1] == "insert":
            self.__container['action_type'] = ActionType.INSERT
            self.__container['then_event_name'] = action_toks[2]
        else:
            self.__container['then_event_name'] = ""

    def p_attributes(self, tokens) -> None:
        """attributes : attributes this_tok identifier value
                      | attributes this_tok identifier distribution
                      | this_tok identifier value
                      | this_tok identifier distribution"""
        last_tok: str = ""
        for tok in tokens:
            if tok is None:
                continue
            if tok == THIS_TOK:
                continue
            if not self.is_float(tok):
                key: str = f'{THIS_TOK}{tok}'
                self.__container['attribute_dict'][key] = {'dist_type': self.__dist_type, 'params': self.__dist_params}
                last_tok = tok
            else:
                key: str = f'{THIS_TOK}{last_tok}'
                self.__dist_type = DistributionType.FIXED
                self.__dist_params = (float(tok),)
                self.__container['attribute_dict'][key] = {'dist_type': self.__dist_type, 'params': self.__dist_params}

    def p_distribution(self, tokens):
        """distribution : normal_tok lb_tok value value rb_tok
                         | uniform_tok lb_tok value value value rb_tok"""
        if tokens[1] == "?N":
            self.__dist_params = (float(tokens[3]), float(tokens[4]))
            self.__dist_type: DistributionType = DistributionType.NORMAL
        elif tokens[1] == "?U":
            self.__dist_params = (float(tokens[3]), float(tokens[4]), float(tokens[5]))
            self.__dist_type = DistributionType.UNIFORM
        else:
            raise RuleError("Unimplemented DistributionType in p_distribution(self, tokens).")

    def p_parallel_list(self, tokens):
        """parallel_list : parallel_item
                         | parallel_item parallel_next"""
        self.__container['action_type'] = ActionType.TO_PARALLEL

    def p_parallel_item(self, tokens):
        """parallel_item : identifier parallel_tok identifier"""
        self.__container['event_list'] = []
        self.__container['event_list'].append(tokens[1])
        self.__container['event_list'].append(tokens[3])

    def p_parallel_next(self, tokens):
        """parallel_next : parallel_tok identifier
                         | parallel_next parallel_tok identifier"""
        for tok in tokens:
            if tok is None:
                continue
            if tok == PARALLEL_TOK:
                continue
            self.__container['event_list'].append(tok)

    def p_series_list(self, tokens):
        """series_list : series_item
                       | series_item series_next"""
        self.__container['action_type'] = ActionType.TO_SERIES

    def p_series_item(self, tokens):
        """series_item : identifier series_tok identifier"""
        self.__container['event_list'] = []
        self.__container['event_list'].append(tokens[1])
        self.__container['event_list'].append(tokens[3])

    def p_series_next(self, tokens):
        """series_next : series_tok identifier
                       | series_next series_tok identifier"""
        for tok in tokens:
            if tok is None:
                continue
            if tok == SERIES_TOK:
                continue
            self.__container['event_list'].append(tok)

    def p_empty(self, empty_tok) -> None:
        """empty :"""
        pass

    # --- End of Production Rules --- #

    def __reset_container(self) -> None:
        for key in self.__container.keys():
            self.__container[key] = None
        self.__container: dict = {'if_event_name': '', 'attribute_dict': {}, 'event_list': []}

    def find_column(self, token) -> int:
        line_start = self.__rules_as_text.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    def p_error(self, t) -> None:
        rule_num: int = len(self.__rules)
        lines: [str] = self.__rules_as_text.split('\n')  # Can assume newlines split all rules
        try:
            error_line: str = lines[rule_num - 1]
        except IndexError:  # However, just _in_ case we'll catch like this.
            error_line: str = lines[-1]
        parsing_error: str = "Parsing error:\n"
        parsing_error += f"--> Input line: \"{error_line}\".\n"
        if hasattr(t, 'value'):
            parsing_error += f"--> Rule {rule_num}: unexpected token \"{t.value}\" with type \"{t.type}\".\n"
            if t.type == "if":
                parsing_error += f"--> Rule {rule_num}: is maybe missing a \";\"?\n"
            parsing_error += f"--> Position: line={t.lineno}, index={self.find_column(t)}.\n"
        else:
            parsing_error += f"--> Rule {rule_num}: is maybe missing a \";\"?\n"
        raise RuleError(parsing_error)

    @staticmethod
    def is_float(string: str):
        try:
            float(string)
            return True
        except ValueError:
            return False
