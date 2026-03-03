import numpy as np

def preprocess_tabular(data: dict):
    return np.array([
        data["age"],
        data["smoker"],
        data["asthma"],
        data["genetics"]
    ], dtype="float32")
