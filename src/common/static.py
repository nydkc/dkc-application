import os


def get_static_dir():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "static"))
