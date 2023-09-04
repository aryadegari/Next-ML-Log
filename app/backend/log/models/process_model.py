from typing import Union
import xml.etree.ElementTree as et
from app.backend.log.constants import NAMESPACE, IGNORED_ATTRIBUTES, HARDCODED_ATTRIBUTES
from app.backend.log.models.enum_types import EventType
from app.backend.log.models.event_model import EventModel


class ProcessModel:
    def __init__(self):
        self.attributes: [str] = []
        self.mxml_file_path: str = ""
        self.bpmn_file_path: str = ""
        self.events: list[EventModel] = []

    @property
    def unique_event_names(self) -> set:
        return set([event.name for event in self.events if "Gateway" not in event.name])

    @property
    def event_and_gw_id_mapping(self) -> dict[str, int]:
        event_names: [str] = self.unique_event_names
        mapping: dict[str, str] = {}
        for event_name in event_names:
            _, event = self.find_event_with_name(event_name)
            mapping[event_name] = event.parallel_or_xor_id
        return mapping

    def update_model(self, bpmn_file_path: str, mxml_file_path: str) -> None:
        self.bpmn_file_path = bpmn_file_path
        self.mxml_file_path = mxml_file_path
        self.events = []
        self.__extract_attributes_from_mxml_file(mxml_file_path)
        self.__parse_bpmn_file(bpmn_file_path)
        # print("(Backend) --> Done updating model!")

    def __extract_attributes_from_mxml_file(self, mxml_file_path: str) -> None:
        all_attributes_set: set = set(HARDCODED_ATTRIBUTES)
        tree = et.parse(mxml_file_path)
        root = tree.getroot().find("Process")
        # for _ in root.findall('ProcessInstance'):  # Will make program slower, but guarantees we read all attributes
        for attribute in root.iter('Attribute'):
            attribute_name = attribute.attrib['name']
            all_attributes_set.add(attribute_name)
        self.attributes = [attribute for attribute in list(all_attributes_set) if attribute not in IGNORED_ATTRIBUTES]

    def __parse_bpmn_file(self, bpmn_file_url: str) -> None:
        tree = et.parse(bpmn_file_url)
        root = tree.getroot()
        task_elements = root.findall('.//bpmn:startEvent', NAMESPACE)
        task_elements += root.findall('.//bpmn:task', NAMESPACE)
        task_elements += root.findall('.//bpmn:endEvent', NAMESPACE)
        exclusive_gateway_elements = root.findall('.//bpmn:exclusiveGateway', NAMESPACE)
        parallel_gateway_elements = root.findall('.//bpmn:parallelGateway', NAMESPACE)
        event_elements = task_elements + exclusive_gateway_elements + parallel_gateway_elements
        for event_element in event_elements:
            self.__append_event(event_element)
        self.__extract_sequence_flows()
        self.__extract_parallel_ids()

    def __append_event(self, event_element: et.Element) -> None:
        event_name, event_type = self.__unwrap_event_name_and_type(event_element)
        event_incoming_elements: [et.Element] = event_element.findall('.//bpmn:incoming', NAMESPACE)
        incoming_flow_ids = [incoming_element.text for incoming_element in event_incoming_elements]
        event_outgoing_elements: [et.Element] = event_element.findall('.//bpmn:outgoing', NAMESPACE)
        outgoing_flow_ids = [outgoing_element.text for outgoing_element in event_outgoing_elements]
        event = EventModel(
            name=event_name,
            event_type=event_type,
            incoming_ids=incoming_flow_ids,
            outgoing_ids=outgoing_flow_ids,
            # Below will be found later
            all_reachable_events=[],
            parallel_or_xor_id=0
        )
        self.events.append(event)

    @staticmethod
    def __unwrap_event_name_and_type(event_element: et.Element) -> tuple[str, EventType]:
        tag: str = event_element.tag.split('}')[-1]
        match tag:
            case "startEvent":
                return "_Start", EventType.START
            case "endEvent":
                return "_End", EventType.END
            case "task":
                return event_element.get('name'), EventType.TASK
            case "exclusiveGateway":
                return event_element.get('id'), EventType.EXCLUSIVE_OR
            case "parallelGateway":
                return event_element.get('id'), EventType.PARALLEL
            case _:
                raise ValueError("Error: Unable to unwrap event_name and type from et.Element.")

    def __extract_sequence_flows(self) -> None:
        outgoing_flows_dict = {}  # Maps event name to outgoing flow IDs
        for event in self.events:
            for outgoing_flow_id in event.outgoing_ids:
                outgoing_flows_dict.setdefault(event.name, []).append(outgoing_flow_id)
        # Traverse the sequence of reachable events for each event
        for event in self.events:
            reachable_events = set()
            self.__traverse(event.name, outgoing_flows_dict, self.unique_event_names, reachable_events, set())
            event.all_reachable_events = list(reachable_events)

    # Quite ugly, also not sure if there is a more efficient to do this? Don't think it matters (for now)
    def __traverse(self, event_name, outgoing_flows_dict, event_names_set, reachable_events, memo_set) -> None:
        if event_name in memo_set:
            return
        memo_set.add(event_name)
        if event_name not in outgoing_flows_dict:
            return
        outgoing_flow_ids = outgoing_flows_dict[event_name]
        for flow_id in outgoing_flow_ids:
            for event in self.events:
                if flow_id in event.incoming_ids:
                    reachable_events.add(event.name)
                    self.__traverse(event.name, outgoing_flows_dict, event_names_set, reachable_events, memo_set)

    # -1: A normal "in series" event, <=-2: unique "group_id" of XOR events, >=0: unique "group_id" of parallel events
    def __extract_parallel_ids(self) -> None:
        parallel_id_counter: id = 1
        parallel_gateway_flow_ids: [tuple[int, [str]]] = []
        xor_id_counter: id = -1
        xor_gateway_flow_ids: [tuple[int, [str]]] = []
        for event in self.events:
            if event.event_type == EventType.PARALLEL:
                parallel_gateway_flow_ids.append((parallel_id_counter, event.outgoing_ids))
                parallel_id_counter += 1
            elif event.event_type == EventType.EXCLUSIVE_OR:
                xor_gateway_flow_ids.append((xor_id_counter, event.outgoing_ids))
                xor_id_counter -= 1
        for event in self.events:
            if event.event_type != EventType.TASK:
                continue
            for parallel_id, outgoing_flow_ids in parallel_gateway_flow_ids:
                if len(event.incoming_ids) != 1:
                    continue
                if event.incoming_ids[0] in outgoing_flow_ids:
                    event.parallel_or_xor_id = parallel_id
            for xor_id, outgoing_flow_ids in xor_gateway_flow_ids:
                if len(event.incoming_ids) != 1:
                    continue
                if event.incoming_ids[0] in outgoing_flow_ids:
                    event.parallel_or_xor_id = xor_id

    def find_event_with_name(self, name: str) -> tuple[bool, Union[EventModel, None]]:
        for event in self.events:
            if event.name == name:
                return True, event
        return False, None

    def get_parallel_or_xor_id_for_event(self, event_name: str) -> int:
        for event in self.events:
            if event_name == event.name:
                return event.parallel_or_xor_id

    def get_num_of_events_in_parallel_or_xor_group(self, group_id: int) -> int:
        counter: int = 0
        for event in self.events:
            if event.parallel_or_xor_id == group_id:
                counter += 1
        return counter
