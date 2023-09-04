import pandas as pd
import xml.etree.ElementTree as et
from pandas import DataFrame
from app.backend.log.constants import THIS_TOK, ACCUMULATIVE_TOK
from app.backend.log.models.instance_model import InstanceModel
from app.backend.log.models.process_model import ProcessModel
from app.backend.log.models.rule_model import RuleModel


class LogsModel:
    def __init__(self, process_model: ProcessModel, rule_models: list[RuleModel]):
        self.__process_model: ProcessModel = process_model
        self.__rule_models: list[RuleModel] = rule_models
        self.__rule_titles: [str] = [rule.get_as_str(use_underscores=True) for rule in rule_models]
        self.__instances: list[InstanceModel] = []
        self.__df_headers: [str] = []
        self.__original_df: DataFrame = pd.DataFrame()
        self.__adapted_df: DataFrame = pd.DataFrame()
        self.__post_init(process_model.mxml_file_path)

    def __post_init(self, mxml_file_path: str) -> None:
        self.__create_instances_from_mxml_file(mxml_file_path)
        self.__create_original_df()
        self.__apply_rules_and_update_instances()
        self.__create_adapted_df()
        self.__create_labels()

    def __create_instances_from_mxml_file(self, mxml_file_path: str) -> None:
        attributes: str = self.__process_model.attributes
        tree = et.parse(mxml_file_path)
        root = tree.getroot().find("Process")
        self.__instances = []
        for instance in root.findall('ProcessInstance'):
            instance_id: int = int(instance.get('id'))
            instance_model: InstanceModel = InstanceModel(
                instance_id=instance_id,
                attributes=attributes,
                rule_titles=self.__rule_titles,
                event_and_id_mapping=self.__process_model.event_and_gw_id_mapping
            )
            for entry in instance.findall('AuditTrailEntry'):
                event_type = entry.find('EventType').text
                if event_type not in ["start", "complete"]:
                    continue
                instance_model.update_using_mxml_entry(
                    event_name=entry.find('WorkflowModelElement').text,
                    event_type=event_type,
                    timestamp=entry.find('Timestamp').text,
                    data=entry.find('Data')
                )
            self.__instances.append(instance_model)

    def __create_original_df(self) -> None:
        # Add trace_id, event and attribute columns
        self.__df_headers = ["trace_id"]
        instance: InstanceModel = self.__instances[0]
        for name in sorted(instance.event_and_attribute_mapping.keys()):
            for attribute in sorted(instance.event_and_attribute_mapping[name].keys()):
                self.__df_headers.append(f"{name}{attribute}")
        set_of_inserted_events: set = set()
        for rule in self.__rule_models:
            set_of_inserted_events.update(rule.inserted_events)
        inserted_events_and_attributes: [str] = []
        for inserted_event in list(set_of_inserted_events):
            if inserted_event == "":
                continue
            inserted_events_and_attributes.append(f"{inserted_event}{THIS_TOK}start_time")
            inserted_events_and_attributes.append(f"{inserted_event}{THIS_TOK}end_time")
            for attribute in self.__process_model.attributes:
                inserted_events_and_attributes.append(f"{inserted_event}{THIS_TOK}{attribute}")
                inserted_events_and_attributes.append(f"{inserted_event}{ACCUMULATIVE_TOK}{attribute}")
        self.__df_headers.extend(inserted_events_and_attributes)
        self.__df_headers.extend(self.__rule_titles)
        self.__df_headers.append("_Path")
        # Store original data into df
        all_rows = []  # https://stackoverflow.com/questions/75956209/dataframe-object-has-no-attribute-append
        for instance in self.__instances:
            all_rows.append(instance.flattened_mapping)
        # Create df(s) and set the rule columns to 0.
        self.__sort_df_headers_ordering()
        self.__original_df = pd.DataFrame(all_rows, columns=self.__df_headers).fillna(0)
        dropped_columns = self.__rule_titles + ["_Label"]
        self.__original_df = self.__original_df.drop(columns=dropped_columns)

    def __create_adapted_df(self) -> None:
        all_rows = []  # https://stackoverflow.com/questions/75956209/dataframe-object-has-no-attribute-append
        for instance in self.__instances:
            all_rows.append(instance.flattened_mapping)
        # Create df(s) and set the rule columns to 0.
        self.__adapted_df = pd.DataFrame(all_rows, columns=self.__df_headers).fillna(0)

    # Note: Even though we *assume* rules don't overlap; rules will be applied in sequential order!
    # Thus, if rules do overlap, we should still (in theory) have the desired results.
    def __apply_rules_and_update_instances(self) -> None:
        for rule in self.__rule_models:
            for instance in self.__instances:
                if rule.is_true_on_instance(instance):
                    instance.update_according_to_rule(rule.get_rule_summary(use_underscores=True))

    def __create_labels(self) -> None:
        for index, row in self.__adapted_df.iterrows():
            binary_as_str: str = ''.join(str(round(row[column])) for column in self.__rule_titles)
            if binary_as_str != "":
                self.__adapted_df.at[index, '_Label'] = int(binary_as_str, 2)
            # Else there were no rules, ie; <rules> = <empty>

    def __sort_df_headers_ordering(self) -> None:
        # Format ordering of columns
        ordered_columns: [str] = []
        begin_columns: [str] = []
        for column in sorted(self.__df_headers):
            if column in self.__rule_titles:
                continue
            if column == "trace_id" or column == "_Label":
                continue
            if column.startswith("_Start"):
                begin_columns.append(column)
            else:
                ordered_columns.append(column)
        ordered_columns = ["trace_id"] + begin_columns + ordered_columns + self.__rule_titles + ["_Label"]
        self.__df_headers = ordered_columns

    def simple_error_check(self) -> tuple[bool, [str]]:
        events_in_instance: [str] = self.__instances[0].event_and_attribute_mapping.keys()
        unvisited_events: [str] = []
        for event_name in events_in_instance:
            event_visited: bool = False
            for instance in self.__instances:
                if instance.event_and_attribute_mapping[event_name][f"{THIS_TOK}occurred"]:
                    event_visited = True
                    break
            if not event_visited:
                unvisited_events.append(event_name)
        if unvisited_events:
            return False, unvisited_events
        return True, []

    def save_to_csv(self, output_file_path: str, save_original: bool = False) -> None:
        if save_original:
            self.__original_df.to_csv(f"{output_file_path[:-4]}_original.csv", index=False)
        self.__adapted_df.to_csv(output_file_path, index=False)
