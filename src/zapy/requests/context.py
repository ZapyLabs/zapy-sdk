from dataclasses import dataclass, field
from typing import Callable
from types import ModuleType

from zapy.base import ZapyAuto
from zapy.store import Store, use_store

from .file_loader import load_file
from .hooks import RequestHookBlueprint


@dataclass
class ZapyRequestContext:
    
    store: Store = field(default_factory=use_store)
    hooks: RequestHookBlueprint = field(default_factory=RequestHookBlueprint)
    logger: Callable = print

    def load_file(self, path, mime=ZapyAuto):
        return load_file(path, mime)

    def auto(self):
        return ZapyAuto


def build_context_module(ctx: ZapyRequestContext) -> ModuleType:
    module_ctx = ModuleType('zapy.context')
    ctx_attrs = (name for name in dir(ctx) if not name.startswith('_'))
    for name in ctx_attrs:
        value = getattr(ctx, name)
        setattr(module_ctx, name, value)

    return module_ctx
