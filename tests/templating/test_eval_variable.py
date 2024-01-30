from zapy.templating import templating


def test_variable_with_int():
    actual = templating.evaluate("{{var1}}", {"var1": 123})
    assert actual == 123


def test_variable_with_spaces():
    actual = templating.evaluate("{{var1}} ", {"var1": 123})
    assert actual == "123 "


def test_variable_with_pipe():
    actual = templating.evaluate(
        "{{var1 | var2}}",
        {
            "var1": {1, 2},
            "var2": {1, 3},
        },
    )
    assert actual == {1, 2, 3}
