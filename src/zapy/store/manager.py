import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Literal, Self, cast

import wrapt

max_recursions = 100


@dataclass
class StorageLog:
    type: Literal["set", "get"]
    instance: "Proxy"
    name: str

    @property
    def name_chain(self) -> Iterable[str]:
        count = 0
        name_stack = [self.name]
        instance: "Proxy" | None = self.instance
        while instance is not None:
            if instance._self_field_name:
                name_stack.append(instance._self_field_name)
            instance = instance._self_parent
            count += 1
            if count > max_recursions:
                raise RecursionError
        return reversed(name_stack)

    def __repr__(self) -> str:
        return f'{self.type}: {".".join(self.name_chain)}'


@dataclass
class Logger:
    modifier: str
    tags: list[str] | None = field(default_factory=list)
    _subscribers: list[Callable] = field(default_factory=list)

    def log(self, action_type: Literal["set", "get"], instance: "Proxy", name: str) -> None:
        log = StorageLog(action_type, instance, name)
        for sub in self._subscribers:
            sub(log)

    def on_log(self, something: Callable) -> None:
        self._subscribers.append(something)


class DictStorage(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore


class Proxy(wrapt.ObjectProxy):

    def __init__(self, value: Any, logger: Logger, parent: Self | None = None, field_name: str | None = None) -> None:
        super().__init__(value)
        self._self_logger = logger
        self._self_parent = parent
        self._self_field_name = field_name

    def __setattr__(self, name: str, value: Any) -> Any:
        if not name.startswith("_self_"):
            logger = self._self_logger
            logger.log("set", self, name)
        return super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Self:
        val = super().__getattr__(name)
        if isinstance(val, Proxy) or name.startswith("_self_"):
            return cast(Proxy, val)
        logger = self._self_logger
        logger.log("get", self, name)
        return Proxy(val, logger, self, name)

    def __setitem__(self, key: str, value: Any) -> Any:
        logger = self._self_logger
        logger.log("set", self, key)
        return super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Self:
        val = super().__getitem__(key)
        if isinstance(val, Proxy):
            return val
        logger = self._self_logger
        logger.log("get", self, key)
        return Proxy(val, logger, self, key)


class Store(DictStorage):

    def create_usage(self, modifier: str, tags: list[str] | None = None) -> "Store":
        logger = Logger(modifier, tags=tags)

        def catch_log(log: StorageLog) -> None:
            logging.debug(f"{logger.modifier} {logger.tags} {log}")

        logger.on_log(catch_log)
        return Proxy(self, logger)
