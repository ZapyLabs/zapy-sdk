from unittest.mock import patch

import pytest

from zapy.utils import module as module_util


@pytest.mark.asyncio
async def test_load_python():
    actual = await module_util.load_python("tests/assets/setup/setup_store.py")
    assert actual.store["test_1"] == "setup_store"


@pytest.mark.asyncio
async def test_load_python_spec_none():
    with (
        patch("importlib.util.spec_from_file_location") as mock_loader,
        pytest.raises(ValueError, match="module spec is none"),
    ):
        mock_loader.return_value = None
        _ = await module_util.load_python("tests/assets/setup/setup_store.py")


@pytest.mark.asyncio
async def test_load_ipynb():
    actual = await module_util.load_ipynb(
        "tests/assets/chains/notebook.ipynb", variables={"passed_value": "test_load_ipynb"}
    )
    assert actual.a == 8
    assert actual.b == "test value b"
    assert actual.c == "hello test_load_ipynb"
