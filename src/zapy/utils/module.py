import importlib.util
import sys
import types
from pathlib import Path
from threading import Lock
from typing import Any

from zapy.templating.eval import exec_async


def load_module(module_path: str | Path) -> Any:
    module_path = Path(module_path)

    if module_path.is_dir():
        return load_module_dir(module_path)
    elif module_path.suffix == ".ipynb":
        err_msg = "use load_ipynb to load ipynb"
        raise ValueError(err_msg)
    else:
        return load_module_python(module_path)


def load_module_dir(module_path: str | Path) -> Any:
    module_path = Path(module_path)
    module_str = str(module_path)
    with Lock():
        sys.path.append(module_str)
        try:
            return load_module_python(module_path / "__init__.py")
        finally:
            sys.path.remove(module_str)


def load_module_python(module_path: str | Path) -> Any:
    module_path = Path(module_path)
    module_spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if module_spec is None or module_spec.loader is None:
        err_msg = "module spec is none"
        raise ValueError(err_msg)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    return module


async def load_ipynb(module_path: str | Path, variables: dict[str, Any] | None = None) -> Any:
    """from https://jupyter-notebook.readthedocs.io/en/latest/examples/Notebook/Importing%20Notebooks.html"""
    from IPython import get_ipython
    from IPython.core.interactiveshell import InteractiveShell
    from nbformat import read

    module_path = Path(module_path)
    shell = InteractiveShell.instance()
    fullname = module_path.stem

    variables = variables or {}

    # load the notebook object
    with open(module_path, encoding="utf-8") as f:
        nb = read(f, 4)

    # create the module and add it to sys.modules if name in sys.modules:
    #    return sys.modules[name]
    mod = types.ModuleType(fullname)
    mod.__file__ = str(module_path)
    mod.__dict__["get_ipython"] = get_ipython
    # apply parameters
    for k, v in variables.items():
        mod.__dict__[k] = v

    # extra work to ensure that magics that would affect the user_ns
    # actually affect the notebook module's ns
    save_user_ns = shell.user_ns
    shell.user_ns = mod.__dict__

    try:
        for cell in nb.cells:
            if cell.cell_type == "code":
                # transform the input to executable Python
                code = shell.input_transformer_manager.transform_cell(cell.source)
                # run the code in themodule
                await exec_async(code, mod.__dict__)
    finally:
        shell.user_ns = save_user_ns
    return mod
