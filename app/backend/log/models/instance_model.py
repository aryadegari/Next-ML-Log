import xml.etree.ElementTree as et
import random
import pytz
from datetime import datetime, timedelta
from app.backend.log.constants import NUM_OF_DECIMALS, THIS_TOK, ACCUMULATIVE_TOK
from app.backend.log.models.enum_types import ActionType, DistributionType


class InstanceModel:
    def __init__(self, instance_id: int, attributes: [str], rule_titles: [str], event_and_id_mapping: dict[str, int]):
        self.instance_id: int = instance_id
        self.event_and_attribute_mapping: dict[str, dict] = {}
        self.__applied_rules_mapping: dict[str, int] = {rule: 0 for rule in rule_titles}
        self.__event_and_id_mapping: dict[str, int] = event_and_id_mapping
        self.__path_taken: [str] = []
        self.__event_and_prev_path_taken: dict[str, [str]] = {}
        self.__all_attributes: [str] = attributes
        self.__init_event_and_attribute_mapping()

    def __init_event_and_attribute_mapping(self) -> None:
        all_event_names: [str] = self.__event_and_id_mapping.keys()
        for event_name in all_event_names:
            self.event_and_attribute_mapping[event_name] = {}
            self.__event_and_prev_path_taken[event_name] = []
            for attribute_name in self.__all_attributes:
                self.event_and_attribute_mapping[event_name][f"{THIS_TOK}{attribute_name}"] = 0.0
                self.event_and_attribute_mapping[event_name][f"{ACCUMULATIVE_TOK}{attribute_name}"] = 0.0

    @property
    def flattened_mapping(self) -> dict:
        flattened_mapping: dict = {"trace_id": self.instance_id}
        for event, event_dict in self.event_and_attribute_mapping.items():
            for attribute, attribute_val in self.event_and_attribute_mapping[event].items():
                flattened_mapping[f"{event}{attribute}"] = attribute_val
        flattened_mapping.update(self.__applied_rules_mapping)
        flattened_mapping["_Path"] = ",".join(self.__path_taken)
        return flattened_mapping

    def update_using_mxml_entry(self, event_type: str, event_name: str, timestamp: str, data: et.Element) -> None:
        if "EVENT" in event_name:
            if "START" in event_name:
                self.__update_mapping("_Start", event_type, timestamp, data)
            elif "END" in event_name:
                self.__update_mapping("_End", event_type, timestamp, data)
            else:
                raise ValueError("Error: There is an event with the name 'EVENT' in it!")
        else:
            self.__update_mapping(event_name=event_name, event_type=event_type, timestamp=timestamp, data=data)

    def __update_mapping(self, event_name: str, event_type: str, timestamp: str, data: et.Element) -> None:
        if event_type == "start":
            self.__path_taken.append(event_name)
            self.__event_and_prev_path_taken[event_name] = self.__path_taken.copy()
            self.event_and_attribute_mapping[event_name][f"{THIS_TOK}start_time"] = timestamp
            self.event_and_attribute_mapping[event_name][f"{THIS_TOK}occurred"] = 1
            return
        if event_type == "complete":
            self.event_and_attribute_mapping[event_name][f"{THIS_TOK}end_time"] = timestamp
            self.__update_events_attributes_used(event_name, data)
            return
        raise ValueError(f"Unknown event_type \'{event_type}\' in \'instance_model.__update_mapping().\'")

    def __update_events_attributes_used(self, event: str, data: et.Element) -> None:
        for attribute in self.__all_attributes:
            if attribute == "occurred":  # Ignore
                continue
            if attribute == "duration":  # Is a unique calculation
                start = datetime.fromisoformat(self.event_and_attribute_mapping[event][f"{THIS_TOK}start_time"])
                end = datetime.fromisoformat(self.event_and_attribute_mapping[event][f"{THIS_TOK}end_time"])
                duration: float = (end - start).total_seconds()
                self.event_and_attribute_mapping[event][f"{THIS_TOK}duration"] = duration
            else:  # Generic attribute
                attribute_amount: float = 0.0
                attribute_element: et.Element = data.find(f'Attribute[@name="{attribute}"]')
                if attribute_element is not None:
                    attribute_amount = float(attribute_element.text)
                attribute_amount = round(attribute_amount, NUM_OF_DECIMALS)
                self.event_and_attribute_mapping[event][f"{THIS_TOK}{attribute}"] = attribute_amount
        self.__update_running_totals(event)

    def __update_running_totals(self, event: str) -> None:
        if self.event_and_attribute_mapping[event][f"{THIS_TOK}occurred"] == 0:
            return  # This event has been skipped
        for attribute in self.__all_attributes:
            total_attribute: float = 0.0
            if event not in self.__event_and_prev_path_taken:  # This event didn't happen
                continue
            for prev_event in self.__event_and_prev_path_taken[event]:
                total_attribute += self.event_and_attribute_mapping[prev_event][f"{THIS_TOK}{attribute}"]
            self.event_and_attribute_mapping[event][f"{ACCUMULATIVE_TOK}{attribute}"] = total_attribute

    def update_according_to_rule(self, rule_summary: dict) -> None:
        if rule_summary['use_running_total']:
            rule_summary['if_event_name'] = self.__find_event_that_triggered_running_total(rule_summary)
        # Check if the "if_event" even happened; otherwise this is redundant
        if rule_summary['if_event_name'] not in self.__path_taken:
            return
        match rule_summary['action_type']:
            case ActionType.SKIP:
                self.__apply_skip_rule(rule_summary)
            case ActionType.INSERT:
                self.__apply_insert_rule(rule_summary)
            case ActionType.TO_PARALLEL:
                self.__apply_to_parallel_rule(rule_summary)
            case ActionType.TO_SERIES:
                self.__apply_to_series_rule(rule_summary)
            case _:
                raise ValueError("Unknown rule action type in instance_model.update_according_to_rule()")
        self.__update_order_path_taken()
        for event in self.event_and_attribute_mapping.keys():
            self.__update_running_totals(event)  # Update all running totals

    def __find_event_that_triggered_running_total(self, rule_summary: dict) -> str:
        for event, attribute_dict in self.event_and_attribute_mapping.items():
            running_total_value: float = attribute_dict[f"{ACCUMULATIVE_TOK}{rule_summary['attribute_name']}"]
            if rule_summary['equality_type'].compare(running_total_value, rule_summary['attribute_value']):
                return event

    def __apply_skip_rule(self, rule_summary: dict) -> None:
        skipped_event: str = rule_summary['then_event_name']
        if self.event_and_attribute_mapping[skipped_event][f"{THIS_TOK}occurred"] == 0:
            return  # This event wasn't going to happen anyway.
        if not self.__is_parallel_event(skipped_event):
            # Shift timestamps
            skipped_event_duration: float = self.event_and_attribute_mapping[skipped_event][f'{THIS_TOK}duration']
            index_of_skipped_event: int = self.__path_taken.index(skipped_event)
            events_after_skipped_event: [str] = self.__path_taken[index_of_skipped_event + 1:]
            for event in events_after_skipped_event:
                self.__shift_event_timestamp(event_name=event, time_shift_as_secs=-skipped_event_duration)
        else:
            self.__apply_skip_shifting_on_parallel_event(skipped_event)
        # Clean up
        for attribute in self.event_and_attribute_mapping[skipped_event].keys():
            self.event_and_attribute_mapping[skipped_event][attribute] = 0
        self.__remove_skipped_event_from_paths(skipped_event=skipped_event)
        self.__applied_rules_mapping[rule_summary['rule_name']] = 1

    def __apply_skip_shifting_on_parallel_event(self, skipped_event: str) -> None:
        # Was skipped_event the last to end in the group with id
        group_id: int = self.__event_and_id_mapping[skipped_event]
        events_in_groups: [str] = [e for e, g_id in self.__event_and_id_mapping.items() if g_id == group_id]
        last_event_in_group: str = self.__get_last_event_to_happen(events_in_groups)
        is_skipped_event_last_in_group: bool = skipped_event == last_event_in_group
        if not is_skipped_event_last_in_group:
            return  # We don't need to shift proceeding events
        # Find the (second) last event in group - this is now the "real" ending time of the parallel group
        events_in_groups.remove(skipped_event)
        last_event_in_group = self.__get_last_event_to_happen(events_in_groups)
        skipped_event_end_time: str = self.event_and_attribute_mapping[skipped_event][f"{THIS_TOK}end_time"]
        skipped_event_end_dt: datetime = datetime.fromisoformat(skipped_event_end_time)
        last_event_end_time: str = self.event_and_attribute_mapping[last_event_in_group][f"{THIS_TOK}end_time"]
        last_event_end_dt: datetime = datetime.fromisoformat(last_event_end_time)
        time_shift: float = (skipped_event_end_dt - last_event_end_dt).total_seconds()
        # Actually shift proceeding events
        events_in_groups.append(skipped_event)
        last_index: int = -1
        for event in reversed(self.__path_taken):
            if event in events_in_groups:
                last_index = self.__path_taken.index(event)
                break
        events_after_skipped_event: [str] = self.__path_taken[last_index + 1:]
        for event in events_after_skipped_event:
            self.__shift_event_timestamp(event_name=event, time_shift_as_secs=-time_shift)

    def __apply_insert_shifting_on_parallel_event(self, inserted_event: str) -> None:
        # Was skipped_event the last to end in the group with id
        group_id: int = self.__event_and_id_mapping[inserted_event]
        events_in_groups: [str] = [e for e, g_id in self.__event_and_id_mapping.items() if g_id == group_id]
        second_last_event_in_group: str = self.__get_last_event_to_happen(events_in_groups)
        is_inserted_event_last_in_group: bool = inserted_event == second_last_event_in_group
        if not is_inserted_event_last_in_group:
            print(f"No shift: {self.instance_id}.")
            return  # We don't need to shift proceeding events
        # Inserted event now is the last event in parallel group
        # Find the (second) last event in group
        events_in_groups.remove(inserted_event)
        second_last_event_in_group = self.__get_last_event_to_happen(events_in_groups)
        second_last_event_end_time = self.event_and_attribute_mapping[second_last_event_in_group][f"{THIS_TOK}end_time"]
        second_last_event_end_dt: datetime = datetime.fromisoformat(second_last_event_end_time)
        inserted_event_end_time = self.event_and_attribute_mapping[inserted_event][f"{THIS_TOK}end_time"]
        inserted_event_end_dt: datetime = datetime.fromisoformat(inserted_event_end_time)
        time_shift: float = (inserted_event_end_dt - second_last_event_end_dt).total_seconds()
        print(f"Shift: {self.instance_id}, by {time_shift}.")
        # Actually shift proceeding events
        events_in_groups.append(inserted_event)
        last_index: int = -1
        for event in reversed(self.__path_taken):
            if event in events_in_groups:
                last_index = self.__path_taken.index(event)
                break
        events_after_skipped_event: [str] = self.__path_taken[last_index + 1:]
        for event in events_after_skipped_event:
            self.__shift_event_timestamp(event_name=event, time_shift_as_secs=time_shift)

    def __get_last_event_to_happen(self, events_in_groups: [str]) -> str:
        last_event: str = ""
        last_end_dt: datetime = datetime.min.replace(tzinfo=pytz.UTC)
        for event in events_in_groups:
            event_end_time: str = self.event_and_attribute_mapping[event][f"{THIS_TOK}end_time"]
            event_end_dt: datetime = datetime.fromisoformat(event_end_time)
            if event_end_dt > last_end_dt:
                last_end_dt = event_end_dt
                last_event = event
        return last_event

    def __remove_skipped_event_from_paths(self, skipped_event: str) -> None:
        for event, path_taken in self.__event_and_prev_path_taken.items():
            if skipped_event in path_taken:
                path_taken.remove(skipped_event)
        self.__path_taken.remove(skipped_event)

    def __apply_insert_rule(self, rule_summary: dict) -> None:
        # Add inserted event to the path + events_and_attribute_mapping
        inserted_event: str = rule_summary['then_event_name']
        at_event: str = rule_summary['if_event_name']
        self.event_and_attribute_mapping[inserted_event] = {}
        # Init attribute values
        for attribute in self.__all_attributes:
            self.event_and_attribute_mapping[inserted_event][f"{THIS_TOK}{attribute}"] = 0
            self.event_and_attribute_mapping[inserted_event][f"{ACCUMULATIVE_TOK}{attribute}"] = 0
        if at_event not in self.__event_and_prev_path_taken['_End']:
            return  # This event was skipped by a previous rule lol
        # Fill in attribute values as defined by rules
        for attribute_name, distribution_details in rule_summary['inserted_event_attributes_dict'].items():
            value: float = self.__generate_value_from_distribution(distribution_details)
            self.event_and_attribute_mapping[inserted_event][attribute_name] = value
        # Add timestamps - just assume happens *right* after "at_event"
        start_time_as_str: str = self.event_and_attribute_mapping[at_event][f'{THIS_TOK}end_time']
        inserted_event_duration: float = self.event_and_attribute_mapping[inserted_event][f'{THIS_TOK}duration']
        end_time_dt: datetime = datetime.fromisoformat(start_time_as_str) + timedelta(seconds=inserted_event_duration)
        end_time_as_str: str = end_time_dt.isoformat()
        self.event_and_attribute_mapping[inserted_event][f'{THIS_TOK}start_time'] = start_time_as_str
        self.event_and_attribute_mapping[inserted_event][f'{THIS_TOK}end_time'] = end_time_as_str
        # Create inserted_event and mapping dict, then make inserted_event#occured = 1 and other attributes == 0
        self.__event_and_id_mapping[inserted_event] = self.__event_and_id_mapping[at_event]
        self.__add_inserted_event_into_paths(inserted_event=inserted_event, at_event=at_event)
        self.event_and_attribute_mapping[inserted_event][f"{THIS_TOK}occurred"] = 1
        if not self.__is_parallel_event(at_event):
            # Shift timestamps
            index_of_inserted_event: int = self.__path_taken.index(inserted_event)
            events_after_inserted_event: [str] = self.__path_taken[index_of_inserted_event + 1:]
            for event in events_after_inserted_event:
                self.__shift_event_timestamp(event_name=event, time_shift_as_secs=inserted_event_duration)
        else:
            self.__apply_insert_shifting_on_parallel_event(inserted_event)
        self.__applied_rules_mapping[rule_summary['rule_name']] = 1

    def __apply_to_parallel_rule(self, rule_summary: dict) -> None:
        events_to_parallel_or_to_series: [str] = rule_summary['event_list']
        time_shift: float = 0.0
        for prev_idx, event_name in enumerate(events_to_parallel_or_to_series[1:]):  # Don't shift the first event
            prev_event: str = events_to_parallel_or_to_series[prev_idx]
            time_shift += self.event_and_attribute_mapping[prev_event][f"{THIS_TOK}duration"]
            self.__shift_event_timestamp(event_name, -time_shift)  # Shift to the left, i.e. *negative* shift
        # Now update all the remaining events
        last_event_name: str = events_to_parallel_or_to_series[-1]
        index_of_last_event: int = self.__path_taken.index(last_event_name)
        events_after_last_event: [str] = self.__path_taken[index_of_last_event + 1:]
        for event_name in events_after_last_event:
            self.__shift_event_timestamp(event_name, -time_shift)  # Shift to the left, i.e. *negative* shift
        self.__applied_rules_mapping[rule_summary['rule_name']] = 1

    def __apply_to_series_rule(self, rule_summary: dict) -> None:
        events_to_parallel_or_to_series: [str] = rule_summary['event_list']
        time_shift: float = 0.0
        for prev_idx, event_name in enumerate(events_to_parallel_or_to_series[1:]):  # Don't shift the first event
            event_timestamp_as_str: str = self.event_and_attribute_mapping[event_name][f"{THIS_TOK}start_time"]
            prev_event: str = events_to_parallel_or_to_series[prev_idx]
            prev_event_timestamp_as_str: str = self.event_and_attribute_mapping[prev_event][f"{THIS_TOK}end_time"]
            event_start_dt: datetime = datetime.fromisoformat(event_timestamp_as_str)
            prev_event_end_dt: datetime = datetime.fromisoformat(prev_event_timestamp_as_str)
            if event_start_dt < prev_event_end_dt:
                time_shift += (prev_event_end_dt - event_start_dt).total_seconds()
            else:  # Keep waiting time
                time_shift += self.event_and_attribute_mapping[prev_event][f"{THIS_TOK}duration"]
            self.__shift_event_timestamp(event_name, time_shift)  # Shift to the right, i.e. *positive* shift
        # Now update all the remaining events
        index_of_last_event: int = -1
        for event in events_to_parallel_or_to_series:
            index_of_event: int = self.__path_taken.index(event)
            if index_of_event > index_of_last_event:
                index_of_last_event = index_of_event
        events_after_last_event: [str] = self.__path_taken[index_of_last_event + 1:]
        for event_name in events_after_last_event:
            self.__shift_event_timestamp(event_name, time_shift)  # Shift to the right, i.e. *positive* shift)
        self.__applied_rules_mapping[rule_summary['rule_name']] = 1

    def __update_order_path_taken(self) -> None:
        events_that_happened: [str] = self.__path_taken.copy()  # Not in order
        event_start_dt_dict: dict[str, str] = {}
        for event in events_that_happened:
            start_time_as_str: str = self.event_and_attribute_mapping[event][f'{THIS_TOK}start_time']
            start_time_dt: datetime = datetime.fromisoformat(start_time_as_str)
            event_start_dt_dict[event] = start_time_dt
        self.__path_taken = sorted(event_start_dt_dict, key=event_start_dt_dict.get)

    # Note: Waiting time is preserved!
    def __shift_event_timestamp(self, event_name: str, time_shift_as_secs: float) -> None:
        start_time_as_str: str = self.event_and_attribute_mapping[event_name][f"{THIS_TOK}start_time"]
        start_dt: datetime = datetime.fromisoformat(start_time_as_str)
        new_start_dt: datetime = start_dt + timedelta(seconds=time_shift_as_secs)
        new_start_time_as_str: str = new_start_dt.isoformat()
        self.event_and_attribute_mapping[event_name][f"{THIS_TOK}start_time"] = new_start_time_as_str
        end_time_as_str: str = self.event_and_attribute_mapping[event_name][f"{THIS_TOK}end_time"]
        end_dt: datetime = datetime.fromisoformat(end_time_as_str)
        new_end_dt: datetime = end_dt + timedelta(seconds=time_shift_as_secs)
        new_end_time_as_str: str = new_end_dt.isoformat()
        self.event_and_attribute_mapping[event_name][f"{THIS_TOK}end_time"] = new_end_time_as_str

    def __add_inserted_event_into_paths(self, inserted_event: str, at_event: str) -> None:
        index = self.__event_and_prev_path_taken['_End'].index(at_event)
        for event, path_taken in self.__event_and_prev_path_taken.items():
            if not path_taken:
                continue
            if at_event not in path_taken:
                continue
            if event == at_event:
                continue
            self.__event_and_prev_path_taken[event].insert(index + 1, inserted_event)
        self.__event_and_prev_path_taken[inserted_event] = self.__event_and_prev_path_taken[at_event].copy()
        self.__event_and_prev_path_taken[inserted_event].append(inserted_event)
        index_of_at_event: int = self.__path_taken.index(at_event)
        self.__path_taken.insert(index_of_at_event + 1, inserted_event)

    def __is_parallel_event(self, skipped_event: str) -> bool:
        if self.__event_and_id_mapping[skipped_event] > 0:
            return True
        return False

    @staticmethod
    def __generate_value_from_distribution(distribution_details: dict) -> float:
        params_tuple: tuple = distribution_details['params']
        match distribution_details['dist_type']:
            case DistributionType.FIXED:
                return params_tuple[0]
            case DistributionType.NORMAL:
                return random.gauss(mu=params_tuple[0], sigma=params_tuple[1])
            case DistributionType.UNIFORM:
                min_value, max_value, step_size = params_tuple
                num_steps = int((max_value - min_value) / step_size)
                step_index = random.randint(0, num_steps)
                return min_value + step_index * step_size
            case _:
                raise ValueError("Unimplemented DistributionType in __generate_value_from_distribution()")

    def __str__(self) -> str:
        s: str = f"{self.instance_id=},\n"
        s += f"{self.event_and_attribute_mapping=},\n{self.__event_and_prev_path_taken=}\n"
        s += f"{self.__path_taken=}.\n"
        s += f"{self.__applied_rules_mapping=}."
        return s
