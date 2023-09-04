import os
import json
import pickle
from app.backend.ml.file_parser import FileParser
from datetime import datetime
from sklearn.metrics import f1_score, precision_score, recall_score
from app.backend.ml.models.model import Model
from app.backend.ml.models.train import Trainer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.backend.controller import Controller

ACTIVE_IMAGE_PATH = r"app/frontend/assets/active_image.png"
ACTIVE_PICKLED_IMAGE_PATH = r"app/frontend/assets/active_pickled_image.png"


class MLApi:
    def __init__(self, controller):
        self.__controller: Controller = controller
        self.__delete_active_image(ACTIVE_IMAGE_PATH)
        self.__delete_active_image(ACTIVE_PICKLED_IMAGE_PATH)
        self.trainer: Trainer = Trainer()
        self.model: Model = Model()
        self.model.fill_auto_ml_file()
        self.trained_model = None
        self.pretrained_model = None
        self.pretrained_model_url = None
        self.validation_data_url = None
        self.file_url: str = None

    def uploaded_new_file(self, file_url: str):
        file_url = self.__controller.get_os_specific_path(file_url)
        self.file_url = file_url
        print("(Backend) --> Uploaded file URL: ", file_url)

    def uploaded_pretrained_model(self, file_url: str, background_color: str):
        file_url = self.__controller.get_os_specific_path(file_url)
        self.pretrained_model_url = file_url
        with open(file_url, 'rb') as file:
            pickle_object = pickle.load(file)
            self.pretrained_model = pickle_object["model"]
        print("(Backend) --> Loaded pickle file URL: ", file_url)

        trainer = Trainer(background_color=background_color)
        trainer.create_pickle_active_image(pickle_object["image"])

        # SEND DATA TO FRONTEND
        pretrained_data_for_view = {
            "model": type(self.pretrained_model).__name__,
            "parameters": self.pretrained_model.get_params(),
            "date": pickle_object["date"],
            "train_size": pickle_object["train_size"]
        }
        self.send_pretrained_model_to_view(pretrained_data_for_view)

    def uploaded_validation_data(self, file_url: str):
        file_url = self.__controller.get_os_specific_path(file_url)
        self.validation_data_url = file_url
        print("(Backend) --> Validation data file URL: ", file_url)

    def get_data_from_view_and_train(self, model_dictionary_str: str, image_bg_color: str, use_nextlog: bool, features_to_plot: list) -> None:
        model_dictionary = json.loads(model_dictionary_str)
        parser: FileParser = FileParser(self.file_url)
        x, y = parser.parse_csv(use_nextlog)

        invalid_features = []
        for feature in features_to_plot:
            if feature not in x.columns:
                invalid_features.append(feature)
                #self.__controller.invalid_features_to_plot_signal.emit()
        if invalid_features:
            self.__controller.invalid_features_to_plot_signal.emit(invalid_features)
            return
        error = ""
        try:
            self.trainer: Trainer = Trainer(model_dictionary, x, y, image_bg_color, features_to_plot)
            self.trainer.train()
            self.trained_model = self.trainer.get_model()
            self.training_statistics = self.trainer.get_statistics()
            self.send_train_test_data_to_view()
        except ValueError as value_error:
            error = str(value_error)
            print(error)
        self.__controller.training_finished_signal.emit(error)

    def test_pretrained_model_on_validation_data(self, is_next_log_csv: bool):
        parser: FileParser = FileParser(self.validation_data_url)
        X, y = parser.parse_csv(is_next_log_csv)
        if type(self.pretrained_model).__name__ in ["GLVQ", "KNeighborsClassifier"]:
            trainer = Trainer()
            _ , X_test, _ , y_test = trainer.split_dataset(X, y, test_size=100)
            X = trainer.scale_features(X_test)
            y = y_test

        try:
            error = ""
            labels_prediction = self.pretrained_model.predict(X)
        except ValueError as value_error:
            error = str(value_error)
            self.__controller.pretrained_model_test_result_signal.emit("", error)
            return

        f1 = f1_score(y, labels_prediction, average='weighted')
        precision = precision_score(y, labels_prediction, average='weighted')
        recall = recall_score(y, labels_prediction, average='weighted')
        msg = {
            "accuracy": str(self.pretrained_model.score(X, y)),
            "f1": str(f1),
            "precision": str(precision),
            "recall": str(recall)
        }
        self.__controller.pretrained_model_test_result_signal.emit(json.dumps(msg), error)


    def get_invalid_features(self, features_to_plot):
        parser: FileParser = FileParser(self.file_url)
        x, _ = parser.parse_csv(False)
        invalid_features = []
        for feature in features_to_plot:
            if feature not in x.columns:
                invalid_features.append(feature)
        return invalid_features


    def send_train_test_data_to_view(self):
        training_statistics = json.dumps(self.training_statistics)
        self.__controller.training_statistics_signal.emit(training_statistics)


    def send_pretrained_model_to_view(self, pretrained_model):
        pretrained_model = json.dumps(pretrained_model)
        self.__controller.pretrained_model_signal.emit(pretrained_model)


    def save_model(self, save_path: str):
        save_path = self.__controller.get_os_specific_path(save_path)
        if self.trained_model is None:
            print("(Backend) --> No model to save")
        else:
            with open(save_path[1:], 'wb') as file:
                date = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                pickle.dump({
                    "date": date,
                    "model": self.trained_model,
                    "train_size": self.training_statistics["train_size"],
                    "image": self.trainer.graph,
                    "f1": self.training_statistics["f1"],
                    "precision": self.training_statistics["precision"],
                    "recall": self.training_statistics["recall"]
                }, file)


    def save_model_image(self, save_path: str):
        save_path = self.__controller.get_os_specific_path(save_path)
        self.trainer.save_image(save_path) #[1:])


    def __delete_active_image(self, file_path):
        file_path = self.__controller.get_os_specific_path(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)


    def next_image(self):
        if (self.trainer.active_image_index == self.trainer.max_image_index - 1):
            print("Last image reached. Can't go any further.")
        else:
            self.trainer.active_image_index += 1
            self.__controller.plot_open_signal.emit()
            if (self.trainer.active_image_index == self.trainer.max_image_index - 1):
                self.trainer.export_plots(self.trainer.active_model, self.__controller)
            else:
                self.__controller.new_threaded_api_call(
                    target=self.trainer.export_plots,
                    args=(self.trainer.active_model, self.__controller)
                )       


    def previous_image(self):
        if (self.trainer.active_image_index == 0):
            print("First image reached. Can't go any further.")
        else:
            self.trainer.active_image_index -= 1
            self.__controller.plot_open_signal.emit()
            if (self.trainer.active_image_index == self.trainer.max_image_index - 2):
                self.trainer.export_plots(self.trainer.active_model, self.__controller)
            else:
                self.__controller.new_threaded_api_call(
                    target=self.trainer.export_plots,
                    args=(self.trainer.active_model, self.__controller)
                )


    def perform_auto_ml(self, train_split, image_background_color, use_nextlog_csv):
        error = ""
        try:
            parser: FileParser = FileParser(self.file_url)
            x, y = parser.parse_csv(use_nextlog_csv)
            self.trainer: Trainer = Trainer(x=x, y=y, background_color=image_background_color)
            self.trainer.perform_auto_ml(train_split)
            self.trained_model = self.trainer.get_model()
            self.training_statistics = self.trainer.get_statistics()
            self.send_train_test_data_to_view()
        except ValueError as value_error:
            error = str(value_error)
            print(error)
        self.__controller.training_finished_signal.emit(error)
