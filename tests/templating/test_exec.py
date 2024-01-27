import pytest

from zapy.templating import eval


def test_exec_variable_declaration():
    global_vars = dict()
    eval.exec_sync(
        """
a = 3
b = '''
   multiline
   text
'''
c = [1]
    """,
        global_vars,
    )
    assert global_vars["a"] == 3
    assert (
        global_vars["b"]
        == """
   multiline
   text
"""
    )
    assert global_vars["c"] == [1]


def test_exec_throws_error():
    with pytest.raises(ValueError) as exc_info:
        global_vars = dict()
        eval.exec_sync(
            """
raise ValueError("From exec")
        """,
            global_vars,
        )
    assert str(exc_info.value) == "From exec"


@pytest.mark.asyncio
async def test_exec_async():
    global_vars = dict()
    await eval.exec_async(
        """
async def my_async_function():
    return 3
a = await my_async_function()
""",
        global_vars,
    )
    assert global_vars["a"] == 3


@pytest.mark.asyncio
async def test_exec_async_error():
    with pytest.raises(ValueError) as exc_info:
        global_vars = dict()
        await eval.exec_async(
            """
async def my_async_function():
    raise ValueError("From exec")
a = await my_async_function()
""",
            global_vars,
        )
    assert str(exc_info.value) == "From exec"
