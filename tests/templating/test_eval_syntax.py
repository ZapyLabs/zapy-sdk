import pytest

from zapy.templating import templating


def test_templating_single_brackets():
    actual = templating.evaluate('{var1}')
    assert actual == '{var1}'


def test_templating_brackets_with_spaces():
    actual = templating.evaluate('{ { var } }')
    assert actual == '{ { var } }'


def test_templating_brackets_escape():
    actual = templating.evaluate('{{ "{{" }}var}}')
    assert actual == '{{var}}'


def test_templating_brackets_not_closed():
    from jinja2.exceptions import TemplateSyntaxError
    with pytest.raises(TemplateSyntaxError):
        _ = templating.evaluate('{{ var }')


def test_variable_names_with_spaces_throws_error():
    with pytest.raises(SyntaxError):
        _ = templating.evaluate('{{ var 1 }}', {
            'var 1': 1,
        })

