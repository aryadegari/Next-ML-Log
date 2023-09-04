from dataclasses import dataclass
from typing import Union
from app.backend.log.constants import THIS_TOK, ACCUMULATIVE_TOK, RUNNING_TOTAL_TOK, PARALLEL_TOK, SERIES_TOK
from app.backend.log.models.enum_types import EqualityType, DistributionType, ActionType
from app.backend.log.models.instance_model import InstanceModel
from app.backend.log.models.process_model import ProcessModel
from app.backend.log.rule_interpreter.rule_error import RuleError


@dataclass
class RuleModel:
    rule_number: int
    if_event_name: str
    attribute_name: str
    equality_type: EqualityType
    attribute_value: float
    action_type: ActionType
    then_event_name: str
    inserted_event_attributes_dict: dict[str, dict[str, Union[DistributionType, tuple]]]
    use_accumulative_total: bool
    use_running_total: bool
    event_list: list[str]

    @property
    def inserted_events(self) -> [str]:
        if self.action_type == ActionType.SKIP:
            return []
        return [self.then_event_name]

    def get_as_str(self, use_underscores: bool = False) -> str:
        if self.use_running_total:
            pretty: str = f'if {RUNNING_TOTAL_TOK}{self.attribute_name} {self.equality_type.value} '
        else:
            separator: str = ACCUMULATIVE_TOK if self.use_accumulative_total else THIS_TOK
            pretty: str = f'if {self.if_event_name}{separator}{self.attribute_name} {self.equality_type.value} '
        if (self.action_type == ActionType.SKIP) or (self.action_type == ActionType.INSERT):
            pretty += f'{self.attribute_value} then {self.action_type.value} {self.then_event_name}'
            if self.inserted_event_attributes_dict:
                pretty += " ( "
                for attribute, dist_dict in self.inserted_event_attributes_dict.items():
                    if dist_dict['dist_type'] == DistributionType.FIXED:
                        params: str = str(dist_dict['params'][0])
                        pretty += f"{attribute} {params} "
                    else:
                        params: str = "(" + " ".join([str(element) for element in dist_dict['params']]) + ") "
                        dist_type: str = "?N" if dist_dict['dist_type'] == DistributionType.NORMAL else "?U"
                        pretty += f"{attribute} {dist_type} {params}"
                pretty += ")"
        else:
            if self.action_type == ActionType.TO_PARALLEL:
                event_list_as_str: str = PARALLEL_TOK.join(self.event_list)
            else:
                event_list_as_str: str = SERIES_TOK.join(self.event_list)
            pretty += f'{self.attribute_value} then {event_list_as_str}'
        pretty += ";"
        if not use_underscores:
            return pretty
        pretty = f"{self.rule_number}_" + pretty
        return pretty.replace(" ", "_")

    def get_rule_summary(self, use_underscores: bool = False) -> dict:
        summary: dict = vars(self)
        summary['rule_name'] = self.get_as_str(use_underscores)
        return summary

    def is_true_on_instance(self, i: InstanceModel) -> bool:
        if self.use_running_total:
            # For example; rule == "if !duration > 10 then skip C"
            for event, attribute_dict in i.event_and_attribute_mapping.items():
                running_total_value: float = attribute_dict[f'{ACCUMULATIVE_TOK}{self.attribute_name}']
                if self.equality_type.compare(running_total_value, self.attribute_value):
                    return True
            return False
        # For example; rule == "if B@duration > 10 then skip C"
        separator: str = ACCUMULATIVE_TOK if self.use_accumulative_total else THIS_TOK  # separator = "@"
        attribute_val: float = i.event_and_attribute_mapping[self.if_event_name][f"{separator}{self.attribute_name}"]
        # attribute_val = i.event_and_attribute_mapping["B"]["@duration"] -- which is "unique" per instance
        return self.equality_type.compare(attribute_val, self.attribute_value)  # return if attribute_val > 10

    def validate_rule(self, process_model: ProcessModel) -> None:
        event_names: [str] = list(process_model.unique_event_names)
        is_valid: bool = True
        error: str = "Rule definition error(s):\n"
        error += f"--> Rule #{self.rule_number}: \"{self.get_as_str()}\".\n"
        if not self.use_running_total:
            if self.if_event_name not in event_names:  # Check if 'if_event_name' exists
                error += f"--> Undefined event \"{self.if_event_name}\".\n"
                is_valid = False
        if self.attribute_name not in process_model.attributes:
            error += f"--> Undefined attribute \"{self.attribute_name}\".\n"
            is_valid = False
        match self.action_type:
            case ActionType.SKIP:
                self.__validate_skip_rule(process_model, error, is_valid)
            case ActionType.INSERT:
                self.__validate_insert_rule(process_model, error, is_valid)
            case ActionType.TO_SERIES:
                self.__validate_to_series_rule(process_model, error, is_valid)
            case ActionType.TO_PARALLEL:
                self.__validate_to_parallel_rule(process_model, error, is_valid)
            case _:
                raise RuleError(f'{error}--> Unknown rule type {self.action_type} in rule_model.validate_rule()!')

    def __validate_to_series_rule(self, process_model: ProcessModel, error: str, is_valid: bool) -> None:
        event_names: [str] = list(process_model.unique_event_names)
        for event in self.event_list:
            if event not in event_names:
                error += f"--> Undefined TO_SERIES event \"{event}\".\n"
                is_valid = False
        start_event: str = self.event_list[0]
        group_id: int = process_model.get_parallel_or_xor_id_for_event(start_event)
        for event in self.event_list:
            parallel_id: int = process_model.get_parallel_or_xor_id_for_event(event)
            if parallel_id <= 0:
                error += f"--> The TO_SERIES event \"{event}\" is not in parallel (ie, is in series/xor/undefined).\n"
                is_valid = False
            elif parallel_id != group_id:
                error += f"--> The TO_SERIES event \"{event}\" is not in same parallel 'group' as \"{start_event}\".\n"
                is_valid = False
        if group_id > 0:
            num_of_events_in_parallel_group: int = process_model.get_num_of_events_in_parallel_or_xor_group(group_id)
            num_of_given_events: int = len(self.event_list)
            if num_of_given_events != num_of_events_in_parallel_group:
                error += f"--> There are {num_of_given_events} events in your TO_SERIES list, but there should be "
                error += f"{num_of_events_in_parallel_group}.\n"
                is_valid = False
        if len(self.event_list) != (len((set(self.event_list)))):
            error += f"--> There are duplicates in your TO_SERIES list.\n"
            is_valid = False
        if not self.use_running_total:
            found, if_event = process_model.find_event_with_name(self.if_event_name)
            for event in self.event_list:
                if event not in if_event.all_reachable_events:
                    error += f"--> The event {event} in your TO_SERIES list is not reachable from "
                    error += f"{self.if_event_name}.\n"
                    is_valid = False
        if not is_valid:
            raise RuleError(error)

    def __validate_to_parallel_rule(self, process_model: ProcessModel, error: str, is_valid: bool) -> None:
        event_names: [str] = list(process_model.unique_event_names)
        for event in self.event_list:
            if event not in event_names:
                error += f"--> Undefined TO_PARALLEL event \"{event}\".\n"
                is_valid = False
            parallel_xor_id: int = process_model.get_parallel_or_xor_id_for_event(event)
            if parallel_xor_id != 0:  # Means this event is nested in a parallel or xor group.
                error += f"--> The TO_PARALLEL event \"{event}\" is not in series (ie, is in parallel/xor/undefined).\n"
                is_valid = False
        if not self.use_running_total:
            found, if_event = process_model.find_event_with_name(self.if_event_name)
            for event in self.event_list:
                if (event not in if_event.all_reachable_events) and (event != if_event.name):
                    error += f"--> The event {event} in your TO_PARALLEL list is not reachable from "
                    error += f"{self.if_event_name}.\n"
                    is_valid = False
        # Test if each event is *directly* after one another
        for i, this_event_name in enumerate(self.event_list):
            found, this_event = process_model.find_event_with_name(this_event_name)
            if i == len(self.event_list) - 1:
                break
            found, next_event = process_model.find_event_with_name(self.event_list[i + 1])
            if found:
                if this_event.outgoing_ids[0] != next_event.incoming_ids[0]:
                    error += f"--> The event {next_event.name} in your TO_PARALLEL list is not *directly* after "
                    error += f"{this_event.name}.\n"
                    is_valid = False
        if not is_valid:
            raise RuleError(error)

    def __validate_skip_rule(self, process_model: ProcessModel, error: str, is_valid: bool) -> None:
        event_names: [str] = list(process_model.unique_event_names)
        if self.then_event_name not in event_names:
            error += f"--> Undefined SKIP event \"{self.then_event_name}\".\n"
            is_valid = False
        if not self.use_running_total:
            if not self.__is_skipped_event_actually_reachable(process_model):
                error += f"--> The SKIPPED event \"{self.then_event_name}\" "
                error += f"is not reachable from \"{self.if_event_name}\".\n"
                is_valid = False
        if not is_valid:
            raise RuleError(error)

    def __validate_insert_rule(self, process_model: ProcessModel, error: str, is_valid: bool) -> None:
        event_names: [str] = list(process_model.unique_event_names)
        if self.then_event_name in event_names:
            error += f"--> The INSERTED event \"{self.then_event_name}\" is already a part of the process model.\n"
            is_valid = False
        if self.inserted_event_attributes_dict != {}:
            for attribute_name, dist_dict in self.inserted_event_attributes_dict.items():
                attribute_name = attribute_name[1:]  # Remove '#' prefix
                if attribute_name not in process_model.attributes:
                    error += f"--> Undefined attribute \"{attribute_name}\" "
                    error += f"for INSERTED event \"{self.then_event_name}\".\n"
                    is_valid = False
                if dist_dict['dist_type'] == DistributionType.NORMAL:
                    mu, sigma = dist_dict['params']
                    if sigma <= 0:
                        error += f"--> Inserted attribute \"{attribute_name}\" with Normal Distribution cannot have "
                        error += f"a sigma \"{sigma}\" <= 0.\n"
                        is_valid = False
                elif dist_dict['dist_type'] == DistributionType.UNIFORM:
                    min_value, max_value, step_size = dist_dict['params']
                    if max_value <= min_value:
                        error += f"--> Inserted attribute \"{attribute_name}\" with Uniform Distribution cannot have "
                        error += f"a max_value \"{max_value}\" that's smaller or equal to min_value \"{min_value}\".\n"
                        is_valid = False
                    if step_size <= 0:
                        error += f"--> Inserted attribute \"{attribute_name}\" with Uniform Distribution cannot have "
                        error += f"a step_size \"{step_size}\" that's <= 0.\n"
                        is_valid = False
        if not is_valid:
            raise RuleError(error)

    def __is_skipped_event_actually_reachable(self, process_model: ProcessModel) -> bool:
        found, event = process_model.find_event_with_name(self.if_event_name)
        if not found:
            return False
        if self.then_event_name in event.all_reachable_events:
            return True
        return False

    def __eq__(self, other) -> bool:
        return self.get_as_str() == other.get_as_str()
