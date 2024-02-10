import unittest
from unittest import mock

import httpx

from zapy.requests import RenderLocationError, send_request
from zapy.requests.models import KeyValueItem, RequestMetadata, ZapyRequest
from zapy.store.manager import Store
from zapy.test import AssertTestResultMixin, assert_test_result_dict


class TestScript(unittest.IsolatedAsyncioTestCase, AssertTestResultMixin):

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200))
    async def test_print(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            script=[
                'print("test_print", "hello")',
            ],
        )

        mock_print = mock.MagicMock()

        await zapy_request.send(logger=mock_print)

        mock_print.assert_called_with("test_print", "hello")

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200))
    async def test_pre_request_hook(self, mock_request):
        from decimal import Decimal

        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            params=[
                KeyValueItem(key="param1", value="{{ 0.3 }}", active=True),
            ],
            script=[
                "from decimal import Decimal",
                'ctx.store.var2 = Decimal("0.2")',
                "@ctx.hooks.pre_request",
                "async def on_pre_request(request_args):",
                '    ctx.store.pre_req = "Test pre script"',
                "    ctx.store.request_args = request_args",
                '    request_args["params"]["X-custom"] = ["hello world"]',
                '    print("pre_request")',
            ],
        )

        store = Store()
        mock_print = mock.MagicMock()

        await zapy_request.send(store=store, logger=mock_print)

        self.assertEqual(Decimal("0.2"), store.var2)
        self.assertEqual("Test pre script", store.pre_req)
        self.assertEqual(dict, type(store.request_args))
        mock_print.assert_called_with("pre_request")
        (req,) = mock_request.call_args.args
        self.assertEqual("http://test/?param1=0.3&X-custom=hello%20world", req.url)

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200))
    async def test_pre_request_hook_error(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            params=[
                KeyValueItem(key="param1", value="{{ 0.3 }}", active=True),
            ],
            script=[
                "@ctx.hooks.pre_request",
                "async def on_pre_request(request_args):",
                '    raise ValueError("MockError")',
            ],
        )

        store = Store()
        mock_print = mock.MagicMock()

        with self.assertRaises(RenderLocationError) as context:
            await zapy_request.send(store=store, logger=mock_print)
        self.assertEqual("Error on pre_request", str(context.exception))

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200))
    async def test_post_request_hook_error(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            params=[
                KeyValueItem(key="param1", value="{{ 0.3 }}", active=True),
            ],
            script=[
                "@ctx.hooks.post_request",
                "async def on_post_request(request_args):",
                '    raise ValueError("MockError")',
            ],
        )

        store = Store()
        mock_print = mock.MagicMock()

        with self.assertRaises(RenderLocationError) as context:
            await zapy_request.send(store=store, logger=mock_print)
        self.assertEqual("Error on post_request", str(context.exception))

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200, json={"id": "test-id"}))
    async def test_post_request_hook(self, _):
        from decimal import Decimal

        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            params=[
                KeyValueItem(key="param1", value="{{ 0.3 }}", active=True),
            ],
            script=[
                "from decimal import Decimal",
                'ctx.store.var2 = Decimal("0.2")',
                "@ctx.hooks.post_request",
                "async def on_post_request(response):",
                '    ctx.store.post_req = "Test post script"',
                "    print(response)",
            ],
        )

        store = Store()
        mock_print = mock.MagicMock()

        await zapy_request.send(store=store, logger=mock_print)

        self.assertEqual(Decimal("0.2"), store.var2)
        self.assertEqual("Test post script", store.post_req)
        (response,) = mock_print.call_args.args
        self.assertEqual(httpx.Response, type(response))
        self.assertEqual({"id": "test-id"}, response.json())

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200))
    async def test_request_hook_order(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            script=[
                "import unittest",
                'print("script 1")',
                "@ctx.hooks.pre_request",
                "async def on_pre_request(request_args):",
                '    print("pre_request")',
                "@ctx.hooks.post_request",
                "async def on_post_request(response):",
                '    print("post_request")',
                "@ctx.hooks.test",
                "class TestStringMethods(unittest.TestCase):",
                "    def test_upper(self):",
                '        print("test")',
                '        self.assertEqual("foo".upper(), "FOO")',
                'print("script 2")',
            ],
        )

        mock_print = mock.MagicMock()

        await zapy_request.send(logger=mock_print)

        mock_print.assert_has_calls(
            [
                mock.call("script 1"),
                mock.call("script 2"),
                mock.call("pre_request"),
                mock.call("post_request"),
                mock.call("test"),
            ]
        )

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200, json={"id": "test-id"}))
    async def test_test_hook_fails(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            script=[
                "import unittest",
                "@ctx.hooks.test",
                "class TestStringMethods(unittest.TestCase):",
                "    def test_response(self):",
                '        self.assertEqual({"id": "test-id2"}, self.response.json())',
            ],
        )

        mock_print = mock.MagicMock()
        with self.assertRaises(AssertionError):
            await zapy_request.send(logger=mock_print)

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200, json={"id": "test-id"}))
    async def test_test_hook_passes(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            script=[
                "import unittest",
                "@ctx.hooks.test",
                "class TestStringMethods(unittest.TestCase):",
                "    def test_response(self):",
                '        self.assertEqual({"id": "test-id"}, self.response.json())',
            ],
        )

        mock_print = mock.MagicMock()
        response_wrapper = await send_request(zapy_request, logger=mock_print)

        self.assert_zapy_test_results(response_wrapper.test_result)
        assert_test_result_dict(response_wrapper.test_result)

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200, json={"id": "test-id"}))
    async def test_hook_calls_deprecated(self, _):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            script=[
                "import unittest",
                "@ctx.hooks.test",
                "class TestStringMethods(unittest.TestCase):",
                "    def test_response(self):",
                '        self.assertEqual({"id": "test-id"}, self.response.json())',
            ],
        )

        mock_print = mock.MagicMock()
        response_wrapper = await send_request(zapy_request, logger=mock_print)

        with mock.patch("warnings.warn") as mock_warn:
            self.assertZapyTestResults(response_wrapper.test_result)
            mock_warn.assert_called_once_with(
                "Call to deprecated function assertZapyTestResults. Replace it with assert_zapy_test_results.",
                stacklevel=2,
            )

    @mock.patch.object(httpx.AsyncClient, "send", return_value=httpx.Response(200))
    async def test_hook_with_metadata(self, _):
        zapy_request = ZapyRequest(
            metadata=RequestMetadata(tags=["meta_tag_1"]),
            endpoint="http://test/",
            method="GET",
            script=[
                "from zapy.base import Metadata",
                "@ctx.hooks.pre_request",
                "async def on_pre_request(request_args, metadata: Metadata):",
                "    ctx.store.metadata = metadata",
            ],
        )

        store = Store()
        await zapy_request.send(store=store)

        self.assertEqual(["meta_tag_1"], store.metadata.tags)
        self.assertEqual(RequestMetadata, type(store.metadata))
