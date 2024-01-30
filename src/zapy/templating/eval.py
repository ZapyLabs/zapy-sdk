import ast

from .traceback import annotate_traceback

_python_code = """
async def __exec_wrapper(_globs):
    globals().update(**_globs)
    __placeholder
    return locals()
"""


async def exec_async(custom_code: str, _globals: dict):
    parsed_ast = ast.parse(_python_code)

    def is_placeholder(node):
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Name) and node.value.id == "__placeholder"

    for node in ast.walk(parsed_ast):
        if is_placeholder(node):
            custom_ast = ast.parse(custom_code)
            new_node = custom_ast
            node.value = new_node

    unparsed = ast.unparse(parsed_ast)
    exec(unparsed)  # noqa S102

    try:
        func = locals()["__exec_wrapper"]
        new_locals = await func(_globals)
    except BaseException as e:
        annotate_traceback(e, unparsed, location="exec_async")
        raise

    _globals.update(new_locals)


def exec_sync(custom_code: str, _globals: dict):
    try:
        return exec(custom_code, _globals)  # noqa S102
    except BaseException as e:
        annotate_traceback(e, custom_code, location="exec_sync")
        raise


def eval_sync(custom_code: str, _globals: dict):
    try:
        return eval(custom_code, _globals)  # noqa S307
    except BaseException as e:
        annotate_traceback(e, custom_code, location="eval_sync")
        raise
