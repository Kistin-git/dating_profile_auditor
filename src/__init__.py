from importlib import import_module

__all__ = ["DatingProfileAuditor"]


def __getattr__(name):
    if name == "DatingProfileAuditor":
        return import_module("src.inference").DatingProfileAuditor
    raise AttributeError(f"module src has no attribute {name}")
