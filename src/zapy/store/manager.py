from dataclasses import dataclass, field
from typing import Literal, Callable
import wrapt


@dataclass
class StorageLog:
    type: Literal['set', 'get']
    instance: 'Proxy'
    name: str

    @property
    def name_chain(self):
        count = 0
        name_stack = [self.name]
        instance = self.instance
        while instance is not None:
            if instance._self_field_name:
                name_stack.append(instance._self_field_name)
            instance = instance._self_parent
            count += 1
            if count > 100:
                raise RecursionError
        return reversed(name_stack)

    def __repr__(self) -> str:
        return f'{self.type}: {".".join(self.name_chain)}'


@dataclass
class Logger:
    modifier: str
    tags: list | None = field(default_factory=list)
    _subscribers: list[Callable] = field(default_factory=list)

    def log(self, type, instance, name):
        log = StorageLog(type, instance, name)
        for sub in self._subscribers:
            sub(log)

    def on_log(self, something: Callable):
        self._subscribers.append(something)


class DictStorage(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Proxy(wrapt.ObjectProxy):

    def __init__(self, value, logger: Logger, parent=None, field_name=None):
        super().__init__(value)
        self._self_logger = logger
        self._self_parent = parent
        self._self_field_name = field_name

    def __setattr__(self, name, value):
        if not name.startswith('_self_'):
            logger = self._self_logger
            logger.log('set', self, name)
        return super().__setattr__(name, value)

    def __getattr__(self, name: str):
        val = super().__getattr__(name)
        if isinstance(val, Proxy) or name.startswith('_self_'):
            return val
        logger = self._self_logger
        logger.log('get', self, name)
        return Proxy(val, logger, self, name)

    def __setitem__(self, key, value):
        logger = self._self_logger
        logger.log('set', self, key)
        return super().__setitem__(key, value)

    def __getitem__(self, key):
        val = super().__getitem__(key)
        if isinstance(val, Proxy):
            return val
        logger = self._self_logger
        logger.log('get', self, key)
        return Proxy(val, logger, self, key)


class Store(DictStorage):

    def create_usage(self, modifier, tags=None) -> 'Store':
        logger = Logger(modifier, tags=tags)
        def catch_log(log: StorageLog):
            print(logger.modifier, logger.tags, log)
        logger.on_log(catch_log)
        return Proxy(self, logger)

