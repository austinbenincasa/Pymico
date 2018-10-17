import inspect
import sys
import core.plugins as plugins
import core.controllers as controllers
from core.exceptions.util_exceptions import LoaderException


class LoaderUtil:

    @staticmethod
    def load_plugin(plugin):
        for name, obj in inspect.getmembers(plugins):
            if inspect.isclass(obj) and name == plugin:
                return obj
        raise LoaderException(f"plugin {plugin} not found")

    @staticmethod
    def load_controller(controller):
        for name, obj in inspect.getmembers(controllers):
            if inspect.isclass(obj) and name == controller:
                return obj
        raise LoaderException(f"controller {controller} not found")
