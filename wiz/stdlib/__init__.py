import importlib
import inspect
import pkgutil

STDLIB = {}

for _, module_name, _ in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")

    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module.__name__:
            STDLIB[module_name] = cls
            break