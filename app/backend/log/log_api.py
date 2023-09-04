from app.backend.log.models.logs_model import LogsModel
from app.backend.log.models.process_model import ProcessModel
from app.backend.log.models.rule_model import RuleModel
from app.backend.log.rule_interpreter.rule_error import RuleError
from app.backend.log.rule_interpreter.rule_lexer import RuleLexer
from app.backend.log.rule_interpreter.rule_parser import RuleParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.backend.controller import Controller


class LogApi:
    def __init__(self, controller):
        self.__controller: Controller = controller
        self.__rules_as_text: str = ""
        self.__process_model: ProcessModel = ProcessModel()

    def uploaded_new_bpmn_file(self, bpmn_file_url: str) -> None:
        bpmn_file_url = self.__controller.get_os_specific_path(bpmn_file_url)
        self.__process_model.bpmn_file_url = bpmn_file_url
        with open(bpmn_file_url, 'r') as bpmn_file:
            bpmn_data: str = bpmn_file.read()
        with open(r'app/frontend/log/html/view_bpm_template.html', 'r') as template_html_file:
            html_data: str = template_html_file.read()
            html_data = html_data.replace("var bpmnXML = ``;", f"var bpmnXML = `{bpmn_data}`;")
        with open(r'app/frontend/log/html/view_bpm.html', 'w') as current_html_file:
            current_html_file.write(html_data)

    def read_loaded_rules(self, rules_file_path: str) -> str:
        rules_file_path = self.__controller.get_os_specific_path(rules_file_path)
        with open(rules_file_path) as f:
            lines_as_list: [str] = f.readlines()
            lines: str = ''.join(lines_as_list)
        return lines

    def save_rules(self, rules: str, output_rule_file_path: str) -> None:
        output_rule_file_path = self.__controller.get_os_specific_path(output_rule_file_path)
        with open(output_rule_file_path, 'w+') as f:
            f.write(rules)

    def update_process_model(self, bpmn_file_path: str, mxml_file_path: str) -> None:
        bpmn_file_path = self.__controller.get_os_specific_path(bpmn_file_path)
        mxml_file_path = self.__controller.get_os_specific_path(mxml_file_path)
        success: bool = True
        unknown_event: str = ""
        unvisited_events: [str] = []
        try:
            self.__process_model.update_model(bpmn_file_path, mxml_file_path)
            logs_model: LogsModel = LogsModel(self.__process_model, [])
            success, unvisited_events = logs_model.simple_error_check()
        except KeyError as e:
            unknown_event: str = str(e)
            success = False
        finally:
            if success:
                resp = "Success"
            else:
                bpmn_file: str = bpmn_file_path.split('/')[-1]
                mxml_file: str = mxml_file_path.split('/')[-1]
                resp = f"Possibly mismatching files: '{bpmn_file}' + '{mxml_file}'\n\n"
                if unknown_event:
                    resp += f"The event \"{unknown_event}\" occurs in the logs, but not the bpmn!"
                else:
                    resp += f"The event(s) \"{unvisited_events}\" are unvisited, but exist in the bpmn!"
            self.__controller.updated_log_model_signal.emit(resp)

    def parse_rules(self, rules_as_text: str) -> str:
        try:
            self.__rules_as_text = rules_as_text
            rule_lexer: RuleLexer = RuleLexer()
            rule_lexer.input(rules_as_text)  # Will throw a (RuleError) Exception if failed
            parser = RuleParser(rule_lexer, self.__process_model)
            parser.parse(rules_as_text)  # Will throw a (RuleError) Exception if failed
            return "Accepted!"
        except RuleError as e:
            return str(e)

    def get_attributes_and_event_names(self) -> str:
        response: str = "Attributes:\n"
        response += "-->" + ','.join(sorted(self.__process_model.attributes))
        response += "\nEvents:\n"
        response += "-->" + ','.join(sorted(self.__process_model.unique_event_names))
        return response

    def generate_log_files(self, output_file_path: str, save_original: bool) -> None:
        output_file_path = self.__controller.get_os_specific_path(output_file_path)
        print(f"(Backend) --> Started: log_api.generate_logs({output_file_path=}, {save_original=})")
        rule_lexer: RuleLexer = RuleLexer()
        rule_lexer.input(self.__rules_as_text)
        parser: RuleParser = RuleParser(rule_lexer, self.__process_model)
        rule_models: [RuleModel] = parser.parse(self.__rules_as_text)
        logs_model: LogsModel = LogsModel(self.__process_model, rule_models)
        logs_model.save_to_csv(output_file_path=output_file_path, save_original=save_original)
        self.__controller.generated_log_file_signal.emit("Done")
        print(f"(Backend) --> Finished: Adapted logs saved to: {output_file_path}")
