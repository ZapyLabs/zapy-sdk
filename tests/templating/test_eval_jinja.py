import pytest

from zapy.templating import templating


def test_templating_variable_not_defined_throws_nameerror():
    with pytest.raises(NameError):
        _ = templating.evaluate(
            "{{ var_1 }}",
            {
                "var_2": 1,
            },
        )


def test_jinja_pipe():
    actual = templating.evaluate("{#jinja#}{{var1 | upper}}", {"var1": "hello"})
    assert actual == "HELLO"


def test_jinja_variable():
    actual = templating.evaluate("{% set x = 42 %}{{x}}")
    assert actual == "42"


def test_python_string_interpolation():
    actual = templating.evaluate(
        'hello {{var1}}{{"".join(var2)}}',
        {
            "var1": "w",
            "var2": ["o", "r", "l", "d"],
        },
    )
    assert actual == "hello world"


def test_python_string_interpolation_with_objects():
    actual = templating.evaluate(
        "{{var1}}{{(var2)}}",
        {
            "var1": 1,
            "var2": ["o", "r", "l", "d"],
        },
    )
    assert actual == "1['o', 'r', 'l', 'd']"


def test_python_spaces():
    actual = templating.evaluate(
        " s {{  var_1 }}{{  (var_2  ) }}",
        {
            "var_1": 1,
            "var_2": 2,
        },
    )
    assert actual == " s 12"
