import unittest
from unittest import mock
import httpx

from zapy.test import AssertTestResultMixin
from zapy.utils import module
from pathlib import Path


class TestScript(unittest.IsolatedAsyncioTestCase, AssertTestResultMixin):

    @mock.patch.object(
        httpx.AsyncClient, 'send',
        return_value = httpx.Response(200, json={'id': 'test-id'})
    )
    async def test_chain_success(self, mock_request):
        chain = await module.load_ipynb('tests/assets/chain.ipynb')
        self.assertEqual({'id': 'test-id'}, chain.out_response)

    @mock.patch.object(
        httpx.AsyncClient, 'send',
        return_value = httpx.Response(200, json={'id': 'test-id'})
    )
    async def test_chain_error(self, mock_request):
        with self.assertRaises(AssertionError) as ex:
            chain = await module.load_ipynb('tests/assets/chain_asserterror.ipynb')

        self.assertIn("AssertionError: 'FOO' != 'will raise an error'", str(ex.exception))

    @mock.patch.object(
        httpx.AsyncClient, 'send',
        return_value = httpx.Response(200, json={'id': 'test-id'})
    )
    async def test_chain_success_import(self, mock_request):
        rel_path = Path('tests/assets')
        chain = await module.load_ipynb(rel_path / 'chain_import.ipynb', variables={
            'rel_path': rel_path
        })
