import pandas as pd
from datetime import datetime
import re


class FileParser:
    def __init__(self, file_path: str):
        self.file_path: str = file_path

    def parse_csv(self, use_dyllan_csv: bool) -> tuple[pd.DataFrame, pd.Series]:
        if use_dyllan_csv:
            return self.parse_specific_csv()
        else:
            return self.parse_general_csv()

    def parse_general_csv(self) -> tuple[pd.DataFrame, pd.Series]:
        print("-----------------------General CSV---------------------------")
        data = pd.read_csv(self.file_path)
        labels = data.iloc[:, -1]
        features = data.iloc[:, : -1]
        print("FINAL DATAFRAMES")
        print(features)
        print(features.keys())
        print(labels)
        print("-----------------------\General CSV---------------------------")
        return (features, labels)

    def parse_specific_csv(self) -> tuple[pd.DataFrame, pd.Series]:
        print("-----------------------Specific CSV---------------------------")
        data = pd.read_csv(self.file_path)
        data = data.drop(['trace_id'], axis=1)
        labels = data["_Label"]  # .iloc[:,-1]
        # Identify the first rules column index
        symbol_columns = []
        for column in data.columns:
            if re.search(r"<=|<|>=|>|!=|==", column):
                symbol_columns.append(column)
        rules = data[symbol_columns]
        # Drop the extracted columns from the original dataframe and drop last column too
        features = data.drop(rules, axis=1).iloc[:, : -1]
        strings_to_drop = ["#start_time", "#end_time", "@occurred", "_Path"]
        # Get the columns to drop
        columns_to_drop = [col for col in features.columns if any(
            string in col for string in strings_to_drop)]
        features = features.drop(columns=columns_to_drop)
        # get all events affected by the rules so that you avoid 1 : 1 mappings
        # CONSTRAINTS: RULES CAN NOT HAVE _ INSIDE THE NAME eg SK_IP
        affected_events = []
        columns_to_drop = []
        for i in range(len(rules.columns)):
            index = rules.columns[i].rindex("then")
            result_string = rules.columns[i][index + len("then") + 1:].strip()
            start_index = result_string.find("(")
            end_index = result_string.rfind(")")
            if start_index != -1 and end_index != -1:
                result_string = result_string[:start_index] + \
                    result_string[end_index + 1:]
            result_string = result_string[:-1]
            if "+" in result_string:
                result_strings = result_string.split("+")
                for string in result_strings:
                    print(f"EVENT DROPPED: {string}")
                    affected_events.append(string)
            elif "-" in result_string:
                result_strings = result_string.split("-")
                for string in result_strings:
                    print(f"EVENT DROPPED: {string}")
                    affected_events.append(string)
            else:
                if result_string[-1] == "_":
                    result_string = result_string[:-1]
                result_string = result_string.split("_", 1)
                result_string = result_string[-1]
                print(f"EVENT DROPPED: {result_string}")
                affected_events.append(result_string)
        for affected_event in affected_events:
            for feature_header in features.columns:
                if feature_header.startswith(affected_event + "@") or feature_header.startswith(affected_event + "#"):
                    columns_to_drop.append(feature_header)
        features = features.drop(columns=columns_to_drop)
        print("FINAL DATAFRAMES")
        print(features)
        print(features.keys())
        print(labels)
        print("-----------------------\Specific CSV---------------------------")
        print(
            f'If you are using Random Forest use {2 ** len(rules.columns) - 1} for max_leaf_nodes')
        return (features, labels)

    def get_timestamps(self, value):
        if 'T' in str(value):
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
            value = value.timestamp()
            return value
        else:
            return value
