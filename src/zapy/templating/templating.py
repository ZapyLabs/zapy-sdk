import ast

from jinja2 import Environment, StrictUndefined

from .eval import sync_eval


# internal use only

def evaluate(value, variables: dict | None = None):
    if variables is None:
        variables = dict()
    if _is_python(value):
        expression = _extract_expression(value)
        return sync_eval(expression, variables)
    else:
        return render(value, variables)

def render(source, variables: dict):
    def raise_helper(msg):
        raise Exception(msg)
    jinja = Environment(undefined=StrictUndefined)
    jinja.globals['raise'] = raise_helper
    template = jinja.from_string(source)
    rendered_template = template.render(**variables)
    return rendered_template

def _extract_expression(value):
    return value.removeprefix('{{').removesuffix('}}').strip()

def _is_python(value: str):
    if not (value.startswith('{{') and value.endswith('}}')):
        return False
    expression = _extract_expression(value)
    if '{{' not in expression:
        return True
    try:
        ast.parse(expression)
        return True
    except SyntaxError:
        return False
