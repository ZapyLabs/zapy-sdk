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
    is_placeholder = lambda node: isinstance(node, ast.Expr) and \
        isinstance(node.value, ast.Name) and \
        node.value.id == "__placeholder"

    for node in ast.walk(parsed_ast):
        if is_placeholder(node):
            custom_ast = ast.parse(custom_code)
            new_node = custom_ast
            node.value = new_node

    unparsed = ast.unparse(parsed_ast)
    exec(unparsed)

    try:
        func = locals()['__exec_wrapper']
        new_locals = await func(_globals)
    except BaseException as e:
        annotate_traceback(e, unparsed, location='exec_async')
        raise

    _globals.update(new_locals)


def sync_exec(custom_code: str, _globals: dict):
    try:
        return exec(custom_code, _globals)
    except BaseException as e:
        annotate_traceback(e, custom_code, location='sync_exec')
        raise

def sync_eval(custom_code: str, _globals: dict):
    try:
        return eval(custom_code, _globals)
    except BaseException as e:
        annotate_traceback(e, custom_code, location='sync_eval')
        raise