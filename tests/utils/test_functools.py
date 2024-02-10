import pytest

from zapy.utils import functools as zapy_tools


@pytest.mark.asyncio
async def test_function_no_args():
    actual = await zapy_tools.empty_function()
    assert actual is None


@pytest.mark.asyncio
@pytest.mark.parametrize("test_input", ["a", 1, None, ["a", "b"]])
async def test_function_single(test_input):
    actual = await zapy_tools.empty_function(test_input)
    assert actual == test_input


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_input",
    [
        ("a", 1),
        (None, 1, "a"),
        ({}, 1, 2),
        (["a", "b"], ""),
    ],
)
async def test_function_multiple(test_input):
    actual = await zapy_tools.empty_function(*test_input)
    assert actual == test_input


def example(a, b: int, c: str):
    return f"{a} {b} {c}"


def test_call_with_signature():
    actual = zapy_tools.call_with_signature(example, 1, 2, "3", kwargs={})
    assert actual == "1 2 3"
    actual = zapy_tools.call_with_signature(
        example,
        23,
        kwargs={
            str: "25",
            int: 27,
        },
    )
    assert actual == "23 27 25"


def test_call_with_missing_signature():
    with pytest.raises(ValueError, match="Missing type of <class 'int'> for argument 'b' on method 'example'"):
        _ = zapy_tools.call_with_signature(
            example,
            23,
            kwargs={
                str: "25",
                dict: {"a": 3},
            },
        )


def test_call_with_empty_signature():
    def example_empty_signature(a, b: int, c):
        return f"{a} {b} {c}"

    with pytest.raises(ValueError, match="Undefined type for 'c' argument on method 'example_empty_signature'"):
        _ = zapy_tools.call_with_signature(
            example_empty_signature,
            23,
            "3",
            kwargs={
                dict: {"a": 3},
            },
        )
