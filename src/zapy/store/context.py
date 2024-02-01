from typing import cast

from zapy.utils import SingletonMeta

from .manager import DictStorage, Store


class Stores(DictStorage, metaclass=SingletonMeta):  # type: ignore
    def __init__(self) -> None:
        self.default = Store()


def use_store(name: str = "default") -> Store:
    store = Stores()[name]
    return cast(Store, store)
