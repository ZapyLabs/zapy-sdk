from zapy.utils import SingletonMeta
from .manager import Store, DictStorage


class Stores(DictStorage, metaclass=SingletonMeta):
    def __init__(self):
        self.default = Store()


def use_store(name='default') -> Store:
    return Stores()[name]
