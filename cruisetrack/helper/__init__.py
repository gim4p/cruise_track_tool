import pickle


def pickle_dict(element_dict: dict, file_path: str):
    with open(file_path, "wb") as f:
        pickle.dump(element_dict, f)
