import os
import pprint

ALL_ML_FILE_PATH = "auto_ml.txt"


class Model:
    def __init__(self):
        self.all_models_dict: dict = self.create_models_dictionary()

    @staticmethod
    def create_models_dictionary():
        models_dictionary = {
            "Random Forest": {
                "n_estimators": "int, default=100",
                "criterion": "{“gini”, “entropy”, “log_loss”}, default=”gini”",
                "max_depth": "int, default=None",
                "min_samples_split": "int or float, default=2",
                "min_samples_leaf": "int or float, default=1",
                "min_weight_fraction_leaf": "float, default=0.0",
                "max_features": "{“sqrt”, “log2”, None}, int or float, default=”sqrt”",
                "max_leaf_nodes": "int, default=None",
                "min_impurity_decrease": "float, default=0.0",
                "bootstrap": "bool, default=True",
                "oob_score": "bool, default=False",
                "n_jobs": "int, default=None",
                "random_state": "int, RandomState instance or None, default=None",
                "verbose": "int, default=0",
                "warm_start": "bool, default=False",
                "class_weight": "{“balanced”, “balanced_subsample”},\n dict or list of dicts, default=None",
                "ccp_alpha": "non-negative float, default=0.0",
                "max_samples": "int or float, default=None"
            },

            "Decision Tree": {
                "criterion": "{“gini”, “entropy”, “log_loss”}, default=”gini”",
                "splitter": "{“best”, “random”}, default=”best”",
                "max_depth": "int, default=None",
                "min_samples_split": "int or float, default=2",
                "min_samples_leaf": "int or float, default=1",
                "min_weight_fraction_leaf": "float, default=0.0",
                "max_features": "int, float or {“auto”, “sqrt”, “log2”}, default=None",
                "random_state": "int, RandomState instance or None, default=None",
                "max_leaf_nodes": "int, default=None",
                "min_impurity_decrease": "float, default=0.0",
                "class_weight": "dict, list of dict or “balanced”, default=None",
                "ccp_alpha": "non-negative float, default=0.0"
            },

            "Generalized LVQ": {
                "distance_type": "{“squared-euclidean”, “euclidean”}, default=”squared-euclidean”",
                "distance_params": "dict, optional, default=None",
                "activation_type": "{“identity”, “sigmoid”, “soft+”, “swish”}, default=”sigmoid”",
                "activation_params": "dict, default=None",
                "discriminant_type": "“relative-distance”",
                "discriminant_params": "dict, default=None",
                "solver_type": "{“sgd”, “wgd”, “adam”, “lbfgs”, “bfgs”}",
                "solver_params": "dict, default=None",
                "prototype_init": "“class-conditional-mean” or \n ndarray, default=”class-conditional-mean”",
                "prototype_n_per_class": "int or np.ndarray, optional, default=1",
                "random_state": "int, RandomState instance, default=None",
                "force_all_finite": "{True, “allow-nan”}, default=True"
            },

            "K-Nearest Neighbors": {
                "n_neighbors": "int, default=5",
                "weights": "{“uniform”, “distance”}, callable or None, default=”uniform”",
                "algorithm": "{“auto”, “ball_tree”, “kd_tree”, “brute”}, default=”auto”",
                "leaf_size": "int, default=30",
                "p": "int, default=2",
                "metric": "str or callable, default=”minkowski”",
                "metric_params": "dict, default=None",
                "n_jobs": "int, default=None"
            }
        }
        return models_dictionary

    @staticmethod
    def get_all_ml_file_path():
        absolute_path = os.path.abspath(ALL_ML_FILE_PATH)
        return absolute_path

    def fill_auto_ml_file(self):
        absolute_path = os.path.abspath(ALL_ML_FILE_PATH)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
        with open(absolute_path, 'w') as file:
            data = pprint.pformat(self.all_models_dict)
            file.write(data)
