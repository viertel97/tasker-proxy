import json
import os


def get_config(file_path):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/config/", file_path), encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_value(value, row, config):
    return next(i for i in config if i[row] == value)
