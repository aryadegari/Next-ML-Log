from app.backend.ml.models.model import Model
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklvq import GLVQ
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.tree import export_graphviz
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pprint
import json
import ast
import pydot
import matplotlib
# this has to be BEFORE import pyplot in order to run on MAC
matplotlib.use("QtAgg")
# from subprocess import call #use this if you want to save img with better quality (see comment below)


IMAGE_PATH = r"app/frontend/assets/active_image.png"
ACTIVE_PICKLED_IMAGE_PATH = r"app/frontend/assets/active_pickled_image.png"


class Trainer:
    def __init__(self, model_dictionary=None, x=None, y=None, background_color="white", feature_names_to_plot=[]):
        if model_dictionary is None:
            model_dictionary = {}
        self.model_dictionary: dict = model_dictionary
        self.all_models_dictionary: dict = Model().all_models_dict
        self.active_model = None
        self.X = x
        self.y = y
        self.image_background_color = background_color
        self.active_image_index = 0
        self.max_image_index = None
        self.feature_names_to_plot = feature_names_to_plot
        self.scaler = None

    def get_model(self):
        return self.active_model

    def split_dataset(self, X, y, test_size=20):
        return train_test_split(X, y, test_size=test_size, random_state=101)

    def start_train_print_info(self, second_part=False):
        if not second_part:
            print(
                f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Start Train {self.model_dictionary['model']} ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~ Data Shape ~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("X_train: ", self.X_train.shape)
            print("X_test: ", self.X_test.shape)
            print("y_train: ", self.y_train.shape)
            print("y_test: ", self.y_test.shape)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~ Params ~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Params before dropping default and empty: ")
            pprint.pprint(self.model_dictionary["parameters"])
            print("\n")
        else:
            print("Params after dropping default and empty (these values are the input params for the training that the user chose): ")
            pprint.pprint(self.model_dictionary["parameters"])
            print("\n")

    def train(self):
        self.X_train, self.X_test, self.y_train, self.y_test = self.split_dataset(
            self.X, self.y, test_size=(100 - self.model_dictionary["train_split"]) / 100)
        self.start_train_print_info()
        match self.model_dictionary["model"]:
            case "Random Forest":
                self.drop_default_and_empty_values(self.model_dictionary["parameters"],
                                                   self.all_models_dictionary["Random Forest"])
                self.start_train_print_info(second_part=True)
                self.train_random_forest()
            case "Decision Tree":
                self.drop_default_and_empty_values(self.model_dictionary["parameters"],
                                                   self.all_models_dictionary["Decision Tree"])
                self.start_train_print_info(second_part=True)
                self.train_decision_tree()
            case "Generalized LVQ":
                self.drop_default_and_empty_values(self.model_dictionary["parameters"],
                                                   self.all_models_dictionary["Generalized LVQ"])
                self.start_train_print_info(second_part=True)
                self.train_generalized_lvq()

            case "K-Nearest Neighbors":
                self.drop_default_and_empty_values(self.model_dictionary["parameters"],
                                                   self.all_models_dictionary["K-Nearest Neighbors"])
                self.start_train_print_info(second_part=True)
                self.train_knn()
            case _:
                print(f"Unknown model {self.model_dictionary['model']}")

    def train_random_forest(self):
        grid_search = self.find_best_params(
            RandomForestClassifier(), self.X_train)
        random_forest_model = RandomForestClassifier(
            **grid_search.best_params_)
        random_forest_model.fit(self.X_train, self.y_train)
        self.print_training_results(
            random_forest_model, self.X_train, self.X_test)
        self.active_model = random_forest_model
        self.max_image_index = self.active_model.get_params()["n_estimators"]

    def train_decision_tree(self):
        grid_search = self.find_best_params(
            DecisionTreeClassifier(), self.X_train)
        decision_tree_model = DecisionTreeClassifier(
            **grid_search.best_params_)
        decision_tree_model.fit(self.X_train, self.y_train)
        self.print_training_results(
            decision_tree_model, self.X_train, self.X_test)
        self.active_model = decision_tree_model

    def train_knn(self):
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(self.X_train)
        X_test = self.scaler.transform(self.X_test)
        grid_search = self.find_best_params(KNeighborsClassifier(), X_train)
        knn_model = KNeighborsClassifier(**grid_search.best_params_)
        knn_model.fit(X_train, self.y_train)
        self.print_training_results(knn_model, X_train, X_test)
        self.active_model = knn_model

    def train_generalized_lvq(self):
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(self.X_train)
        X_test = self.scaler.transform(self.X_test)
        grid_search = self.find_best_params(GLVQ(), X_train)
        # GrlvqModel(**grid_search.best_params_)
        glvq_model = GLVQ(**grid_search.best_params_)
        glvq_model.fit(X_train, self.y_train)
        self.print_training_results(glvq_model, X_train, X_test)
        self.active_model = glvq_model

    def get_most_important_features(self):
        if self.feature_names_to_plot == []:
            # Change this to whatever feature selector you want/need
            gradboost_clf = GradientBoostingClassifier()
            gradboost_model = gradboost_clf.fit(self.X_train, self.y_train)
            gradboost_model_fit = gradboost_model.predict(self.X_test)
            print('Accuracy of the Gradient Boosting model is:', '',
                  accuracy_score(self.y_test, gradboost_model_fit).round(3))
            imp_features = gradboost_model.feature_importances_
            for i in imp_features:
                print(i.round(3))
            df_imp_features = pd.DataFrame({"features": self.X_train.columns}).join(
                pd.DataFrame({"weights": imp_features}))
            df_imp_features = df_imp_features.sort_values(
                by=['weights'], ascending=False)
            return list(df_imp_features['features'][:3])
        return self.feature_names_to_plot

    def find_best_params(self, model, X_train):
        params = self.convert_from_string_in_dictionary(
            self.model_dictionary["parameters"])
        grid_search = GridSearchCV(
            model, param_grid=params, scoring='f1_weighted', cv=5)
        grid_search.fit(X_train, self.y_train)
        print("Best hyperparameters: ", grid_search.best_params_)
        return grid_search

    def export_plots(self, model, controller):
        match self.model_dictionary["model"]:
            case "Generalized LVQ":
                self.get_lvq_images(model=model)
            case "K-Nearest Neighbors":
                self.get_lvq_images(model=model)
            case "Random Forest":
                self.export_tree_graphs(self.active_model)
            case "Decision Tree":
                self.export_tree_graphs(self.active_model)
            case _:
                print(f"Model {self.model_dictionary['model']} not known")
        controller.plot_closed_signal.emit()

    def get_lvq_images(self, model=None):
        self.most_important_features_names = self.get_most_important_features()
        if len(self.most_important_features_names) > 3:
            self.max_image_index = 7
        else:
            self.max_image_index = 2 ** len(
                self.most_important_features_names) - 1
        X = np.concatenate((self.X_train, self.X_test))
        X = self.scaler.transform(X)
        predicted_labels = model.predict(X)
        X = self.scaler.inverse_transform(X)
        self.features_to_plot = pd.DataFrame(X)
        self.features_to_plot.columns = self.X.columns
        print("FEATURES TO PLOT (before dropping columns): \n",
              self.features_to_plot)
        self.features_to_plot = self.features_to_plot[self.most_important_features_names].copy(
        )
        self.features_to_plot.insert(
            len(self.features_to_plot.columns), "Label", predicted_labels)
        print("FEATURES TO PLOT (before after dropping columns): \n",
              self.features_to_plot)
        # REMOVE OUTLIERS HERE IF NEEDED
        condition = self.features_to_plot > 10000
        self.features_to_plot = self.features_to_plot[~condition]
        self.plot_images()

    def plot_images(self, popup=False):
        match self.max_image_index:
            case 1:  # plotting 1 feature (A : A)
                match self.active_image_index:
                    case 0:
                        self.plot_single_plot(0, 0)
            case 3:  # plotting 2 features (A : A, B : B, A : B)
                match self.active_image_index:
                    case 0:
                        self.plot_single_plot(0, 0)

                    case 1:
                        self.plot_single_plot(1, 1)

                    case 2:
                        self.plot_single_plot(0, 1)

            # plotting 3 featires (A : A, B : B, C : C, A : B, A : C, B : C, A : B : C)
            case 7:
                match self.active_image_index:
                    case 0:
                        self.plot_single_plot(0, 0)

                    case 1:
                        self.plot_single_plot(1, 1)

                    case 2:
                        self.plot_single_plot(2, 2)

                    case 3:
                        self.plot_single_plot(0, 1)

                    case 4:
                        self.plot_single_plot(0, 2)

                    case 5:
                        self.plot_single_plot(1, 2)

                    case 6:
                        plt.close('all')
                        fig = plt.figure(facecolor=self.image_background_color)
                        ax = fig.add_subplot(
                            projection='3d', facecolor=self.image_background_color)
                        ax.scatter3D(self.features_to_plot.iloc[:, 0], self.features_to_plot.iloc[:, 1],
                                     self.features_to_plot.iloc[:, 2], c=self.features_to_plot.iloc[:, -1])
                        ax.set_xlabel(self.features_to_plot.columns[0])
                        ax.set_ylabel(self.features_to_plot.columns[1])
                        ax.set_zlabel(self.features_to_plot.columns[2])
                        self.graph = fig
                        plt.savefig(IMAGE_PATH)
                        plt.ion()
                        plt.show()
                        plt.ioff()

    def plot_single_plot(self, feature_1, feature_2):
        plt.close('all')
        fig = plt.figure(facecolor=self.image_background_color)
        plt.scatter(self.features_to_plot.iloc[:, feature_1], self.features_to_plot.iloc[:, feature_2],
                    c=self.features_to_plot.iloc[:, -1])
        plt.xlabel(self.features_to_plot.columns[feature_1])
        plt.ylabel(self.features_to_plot.columns[feature_2])
        plt.savefig(IMAGE_PATH)
        plt.close()
        self.graph = fig

    def export_tree_graphs(self, model):
        match self.model_dictionary["model"]:
            case "Random Forest":
                estimator = model.estimators_[self.active_image_index]
                self.make_active_tree_png(estimator)
            case "Decision Tree":
                self.make_active_tree_png(model)
            case _:
                print(f"Unknown model {self.model_dictionary['model']}")

    def make_active_tree_png(self, estimator):
        class_names = [str(x) for x in self.y.unique()]
        export_graphviz(estimator, out_file='tree.dot',
                        feature_names=self.X.columns,
                        class_names=class_names,
                        rounded=True, proportion=False,
                        precision=2, filled=True)
        # Convert .dot to .png and export
        # call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600']) #better quality but hard to load and sometimes too big for GUI
        (self.graph,) = pydot.graph_from_dot_file('tree.dot')
        self.graph.set_bgcolor(self.image_background_color)
        # add this to the save image button
        self.graph.write_png(IMAGE_PATH)

    def save_image(self, path):
        if self.model_dictionary["model"] in ["Generalized LVQ", "K-Nearest Neighbors"]:
            self.graph.savefig(path)
        else:
            self.graph.set_bgcolor("white")
            self.graph.write_png(path)

    def create_pickle_active_image(self, graph):
        if isinstance(graph, pydot.Dot):
            graph = pydot.graph_from_dot_data(str(graph))[0]
            graph.set_bgcolor(self.image_background_color)
            graph.write_png(ACTIVE_PICKLED_IMAGE_PATH)
        elif isinstance(graph, matplotlib.figure.Figure):
            graph.savefig(ACTIVE_PICKLED_IMAGE_PATH)

    def convert_from_string_in_dictionary(self, dictionary):
        for key, value in dictionary.items():
            v = json.loads(value)
            if (type(v) != list):
                value = [v]
                dictionary[key] = value
            else:
                dictionary[key] = v
        return dictionary

    def drop_default_and_empty_values(self, model_dictionary, all_models_dictionary):
        for key in all_models_dictionary:
            if model_dictionary[key] == '':
                del model_dictionary[key]
            elif model_dictionary[key] == all_models_dictionary[key]:
                del model_dictionary[key]

    def get_statistics(self):
        X_test = self.X_test
        X_train = self.X_train
        model_name = self.model_dictionary["model"]
        if model_name in ["Generalized LVQ", "K-Nearest Neighbors"]:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
        labels_prediction = self.active_model.predict(X_test)
        f1 = f1_score(self.y_test, labels_prediction, average='weighted')
        precision = precision_score(
            self.y_test, labels_prediction, average='weighted')
        recall = recall_score(
            self.y_test, labels_prediction, average='weighted')
        return {
            "model_name": model_name,
            "training_accuracy": self.active_model.score(X_train, self.y_train),
            "testing_accuracy": self.active_model.score(X_test, self.y_test),
            "parameters": self.active_model.get_params(),
            "train_size": self.model_dictionary["train_split"],
            "f1": f1,
            "precision": precision,
            "recall": recall
        }

    def print_training_results(self, model, X_train, X_test):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~ Train Results ~~~~~~~~~~~~~~~~~~~~~~~")
        predicted_labels = model.predict(X_test)
        print(f'Train Accuracy - : {model.score(X_train, self.y_train):.3f}')
        print(f'Test Accuracy - : {model.score(X_test, self.y_test):.3f}')
        print(classification_report(self.y_test, predicted_labels))

    def scale_features(self, X, use_fit_transform=True):
        scaler = StandardScaler()
        if use_fit_transform:
            X = scaler.fit_transform(X)
        else:
            X = scaler.transform(X)
        return X

    def perform_auto_ml(self, train_split):
        # Read content from all_ml_dictionary
        with open(Model().get_all_ml_file_path(), 'r') as file:
            all_ml_dictionary = file.read()
            all_ml_dictionary = ast.literal_eval(all_ml_dictionary)
        self.model_dictionary["train_split"] = train_split
        best_metric = -1
        best_model_name = ""
        best_model_parameters = {}
        for model, parameters in all_ml_dictionary.items():  # go through whole dictionary and do training
            self.model_dictionary["model"] = model
            self.model_dictionary["parameters"] = parameters
            self.train()
            if self.get_statistics()["f1"] > best_metric:
                print(
                    "~~~~~~~~~~~~~~~~~~~~~~ NEW BEST MODEL ~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print(model)
                print(self.get_statistics()["f1"])
                best_metric = self.get_statistics()["f1"]
                best_model_name = model
                best_model_parameters = self.active_model.get_params()
        for parameter, value in best_model_parameters.items():
            best_model_parameters[parameter] = json.dumps(value)
        self.model_dictionary["model"] = best_model_name
        self.model_dictionary["parameters"] = best_model_parameters
        self.train()
