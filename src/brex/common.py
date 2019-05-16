import importlib
import os

def import_python_file(filepath):
    filepath = filepath[:-3] # strip .py
    filepath = filepath.replace(os.sep, '.')
    return importlib.import_module(filepath)
