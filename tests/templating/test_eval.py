from zapy.templating import templating


def test_templating():
    a = templating.evaluate('{{var1}}', {
        'var1': 123
    })
    assert a == 123
