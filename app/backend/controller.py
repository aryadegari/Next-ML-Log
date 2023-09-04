import sys
import platform
import json
from threading import Thread
from typing import Callable
from PySide6 import QtCore
from PySide6.QtCore import QObject, Slot, Signal, QRunnable, QThreadPool
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6 import QtGui
from app.backend.log.log_api import LogApi
from app.backend.ml.ml_api import MLApi



class Worker(QRunnable):
    def __init__(self, target: Callable, args: tuple):
        super().__init__()
        self.__target: Callable = target
        self.__args: tuple = args

    def run(self):
        self.__target(*self.__args)
        print("Thread complete")


class Controller(QObject):
    # Log API signals
    generated_log_file_signal: Signal = Signal(str)
    updated_log_model_signal: Signal = Signal(str)

    # ML API signals
    models_signal: Signal = Signal(str, arguments=["models_list"])
    training_finished_signal: Signal = Signal(str)
    training_statistics_signal: Signal = Signal(str)
    pretrained_model_signal: Signal = Signal(str)
    pretrained_model_test_result_signal: Signal = Signal(str, str)
    invalid_features_to_plot_signal: Signal = Signal(list)
    plot_open_signal: Signal = Signal()
    plot_closed_signal: Signal = Signal()
    def __init__(self):
        QObject.__init__(self)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        self.__threads: list[Thread] = []
        self.__is_using_windows: bool = True
        self.__app = QApplication(sys.argv)
        self.__engine = QQmlApplicationEngine()
        self.__log_api: LogApi = LogApi(self)
        self.__ml_api: MLApi = MLApi(self)
        self.__threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.__threadpool.maxThreadCount())
        self.__setup_app()

    # General setting up
    def __setup_app(self) -> None:
        QtGui.QImageReader.setAllocationLimit(0)
        self.__app.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.RoundPreferFloor)
        self.__app.setWindowIcon(QIcon(r"app/frontend/assets/icon.png"))
        if platform.system() == "Windows":
            import ctypes  # This library is only for Windows.
            my_app_id = 'next_log_v1.0'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        else:
            self.__is_using_windows = False
        
        self.__app.setOrganizationName("RuG")
        self.__app.setOrganizationDomain("RuG")
        self.__engine.rootContext().setContextProperty("backend", self)
        qml_file = r"app/frontend/main.qml"
        self.__engine.setInitialProperties({
            "all_ml_models": json.dumps(self.__ml_api.model.all_models_dict),
            "application_root_path": r""
        })
        self.__engine.load(qml_file)

    def start(self) -> None:
        if not self.__engine.rootObjects():
            sys.exit(-1)
        self.__app.exec()
        for thread in self.__threads:
            thread.join()

    # def __new_threaded_api_call(self, target: Callable, args: tuple) -> None:
    #     worker = Worker(target=target, args=args)
    #     self.__threadpool.start(worker)

    def new_threaded_api_call(self, target: Callable, args: tuple) -> None:
        worker = Worker(target=target, args=args)
        self.__threadpool.start(worker)

    def get_os_specific_path(self, file_path: str) -> str:
        file_path = file_path.replace("file:///", "")
        if self.__is_using_windows:
            return file_path
        return "/" + file_path  # Might be specific to Mac, might break on Linux.

    # Shared API calls
    @Slot(bool)
    def changed_theme(self, changed_to_light_theme: bool) -> None:
        # Update current bpm rendering
        with open(r'app/frontend/log/html/view_bpm.html', 'r') as current_html_file:
            current_html_data: str = current_html_file.read()
            if changed_to_light_theme:
                current_html_data = current_html_data.replace('dark_theme.css', 'light_theme.css')
            else:
                current_html_data = current_html_data.replace('light_theme.css', 'dark_theme.css')
        with open(r'app/frontend/log/html/view_bpm.html', 'w') as current_html_file:
            current_html_file.write(current_html_data)

        # Update template bpm
        with open(r'app/frontend/log/html/view_bpm_template.html', 'r') as template_html_file:
            template_html_data: str = template_html_file.read()
            if changed_to_light_theme:
                template_html_data = template_html_data.replace('dark_theme.css', 'light_theme.css')
            else:
                template_html_data = template_html_data.replace('light_theme.css', 'dark_theme.css')
        with open(r'app/frontend/log/html/view_bpm_template.html', 'w') as template_html_file:
            template_html_file.write(template_html_data)

    # --- Log API calls  --- #
    @Slot(str)
    def uploaded_new_bpmn_file(self, bpmn_file_url: str) -> None:
        self.__log_api.uploaded_new_bpmn_file(bpmn_file_url)

    @Slot(str, result=str)
    def read_loaded_rules(self, rules_file_path: str) -> str:
        return self.__log_api.read_loaded_rules(rules_file_path)

    @Slot(str, str)
    def save_rules(self, rules: str, output_rule_file_path: str) -> None:
        self.__log_api.save_rules(rules, output_rule_file_path)

    @Slot(str, str)
    def update_process_model_with_mxml_and_bpmn_files(self, bpmn_file_path: str, mxml_file_path: str) -> None:
        self.new_threaded_api_call(target=self.__log_api.update_process_model, args=(bpmn_file_path, mxml_file_path))

    @Slot(str, result=str)
    def parse_rules(self, rules_as_text: str) -> str:
        return self.__log_api.parse_rules(rules_as_text)

    @Slot(result=str)
    def get_attributes_and_event_names(self) -> str:
        return self.__log_api.get_attributes_and_event_names()

    @Slot(str, bool)
    def generate_log_files(self, output_file_path: str, save_original: bool) -> None:
        self.new_threaded_api_call(target=self.__log_api.generate_log_files, args=(output_file_path, save_original))

    # --- ML.log API calls --- #
    @Slot(str)
    def uploaded_new_file(self, file_url: str) -> None:
        self.__ml_api.uploaded_new_file(file_url)

    @Slot(str, str)
    def uploaded_pretrained_model(self, file_url: str, background_color: str) -> None:
        self.__ml_api.uploaded_pretrained_model(file_url, background_color)

    @Slot(str)
    def uploaded_validation_data(self, file_url: str) -> None:
        self.__ml_api.uploaded_validation_data(file_url)


    @Slot(str, str, bool, list)
    def get_data_from_view_and_train(self, model_dictionary_str: str, image_bg_color: str, use_nextlog: bool, features_to_plot: list) -> None:
        self.new_threaded_api_call(
            target=self.__ml_api.get_data_from_view_and_train,
            args=(model_dictionary_str, image_bg_color, use_nextlog, features_to_plot)
        )

    @Slot()
    def export_images(self):
        self.__ml_api.trainer.export_plots(self.__ml_api.trainer.active_model, self)

    @Slot(bool)
    def test_pretrained_model_on_validation_data(self, is_next_log_csv: bool) -> None:
        self.__ml_api.test_pretrained_model_on_validation_data(is_next_log_csv)

    @Slot(str)
    def save_model(self, save_path: str) -> None:
        self.__ml_api.save_model(save_path)

    @Slot(str)
    def save_model_image(self, save_path: str) -> None:
        self.__ml_api.save_model_image(save_path)

    @Slot()
    def next_image(self) -> None:
        self.__ml_api.next_image()

    @Slot()
    def previous_image(self) -> None:
        self.__ml_api.previous_image()

    @Slot(int, str, bool)
    def perform_auto_ml(self, train_split, image_bg_color, use_nextlog_csv) -> None:
        self.new_threaded_api_call(
            target=self.__ml_api.perform_auto_ml,
            args=(train_split, image_bg_color, use_nextlog_csv)
        )
