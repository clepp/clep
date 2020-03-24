# -*- coding: utf-8 -*-

"""This module contains all the constants used in CLEPP package."""

import os
from scipy.stats import uniform, loguniform
from skopt.space import Real, Categorical

MODULE_NAME = 'clepp'
DEFAULT_CLEPP_DIR = os.path.join(os.path.expanduser('~'), '.clepp')
CLEPP_DIR = os.environ.get('CLEPP_DIRECTORY', DEFAULT_CLEPP_DIR)

METRIC_TO_LABEL = {
    'f1_weighted': '$F_1$ Weighted',
    'f1': '$F_1$',
    'f1_micro': '$F_1$ Micro',
    'f1_macro': '$F_1$ Macro',
    'recall': 'Recall',
    'precision': 'Precision',
    'jaccard': 'Jaccard Score',
    'roc_auc': 'ROC-AUC',
    'accuracy': 'Accuracy',
    'balanced_accuracy': 'Balanced Accuracy',
    'average_precision': 'Average Precision',
}


def get_data_dir() -> str:
    """Ensure the appropriate clepp data directory exists for the given module, then returns the file path."""
    os.makedirs(CLEPP_DIR, exist_ok=True)
    return CLEPP_DIR


def get_param_grid(model_name):
    if model_name == 'logistic_regression':
        c_values = [0.01, 0.1, 0.25, 0.5, 0.8, 0.9, 1, 10]
        param_grid = dict(C=c_values)

    elif model_name == 'elastic_net':
        l1_ratios = [.1, .5, .7, .9, .95, .99, 1]
        c_values = [0.01, 0.1, 0.25, 0.5, 0.8, 0.9, 1, 10]
        param_grid = dict(l1_ratio=l1_ratios, C=c_values)

    elif model_name == 'svm':
        c_values = [0.1, 1, 10, 100, 1000]
        kernel = ['linear', 'poly', 'rbf']
        param_grid = dict(C=c_values, kernel=kernel)

    elif model_name == 'random_forest':
        n_estimators = [100, 200, 500, 700]
        max_features = ["auto", "log2"]
        param_grid = dict(n_estimators=n_estimators, max_features=max_features)

    elif model_name == 'gradient_boost':
        param_grid = {
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.5, 0.6, 0.7, 0.8],
            'max_depth': [6, 7, 8],
            'min_child_weight': [1]
        }

    else:
        raise ValueError(
            f'The entered model "{model_name}", was not found. Please check that you have chosen a valid model.'
        )

    return param_grid


def get_param_dist(model_name):
    if model_name == 'logistic_regression':
        param_dist = dict(C=loguniform(1e-6, 1e+6))

    elif model_name == 'elastic_net':
        param_dist = dict(l1_ratio=uniform(0, 1), C=loguniform(1e-6, 1e+6))

    elif model_name == 'svm':
        kernel = ['linear', 'poly', 'rbf']
        param_dist = dict(C=loguniform(1e-6, 1e+6), kernel=kernel)

    elif model_name == 'random_forest':
        max_features = ["auto", "log2"]
        param_dist = dict(n_estimators=uniform(100, 1000), max_features=max_features)

    elif model_name == 'gradient_boost':
        param_dist = dict(
            learning_rate=uniform(0, 1),
            subsample=uniform(0.1, 0.9),
            max_depth=uniform(0, 10),
            min_child_weight=uniform(0, 25)
        )

    else:
        raise ValueError(
            f'The entered model "{model_name}", was not found. Please check that you have chosen a valid model.'
        )

    return param_dist


def get_param_space(model_name):
    if model_name == 'logistic_regression':
        param_space = dict(C=Real(1e-6, 1e+6, prior='log-uniform'))

    elif model_name == 'elastic_net':
        param_space = dict(l1_ratio=Real(0, 1), C=Real(1e-6, 1e+6, prior='log-uniform'))

    elif model_name == 'svm':
        kernel = ['linear', 'poly', 'rbf']
        param_space = dict(C=Real(1e-6, 1e+6, prior='log-uniform'), kernel=Categorical(kernel))

    elif model_name == 'random_forest':
        max_features = ["auto", "log2"]
        param_space = dict(n_estimators=Real(100, 1000), max_features=Categorical(max_features))

    elif model_name == 'gradient_boost':
        param_space = dict(
            learning_rate=Real(0, 1),
            subsample=Real(0.1, 1.0),
            max_depth=Real(0, 10),
            min_child_weight=Real(0, 25)
        )

    else:
        raise ValueError(
            f'The entered model "{model_name}", was not found. Please check that you have chosen a valid model.'
        )

    return param_space
