import textwrap
import unittest

from zapy.requests.converter import RequestConverter
from zapy.requests.models import KeyValueItem, ZapyRequest
from zapy.requests.requester import ZapyRequestContext
from zapy.store import use_store
from zapy.store.manager import Store


class TestCaseReq(unittest.TestCase):

    def test_trailing_spaces(self):
        zapy_request = ZapyRequest(
            endpoint="http://test",
            method="GET",
            variables=[
                KeyValueItem(key="var1", value="Hello ", active=True),
            ],
            params=[
                KeyValueItem(key="param1 ", value='{{var1 + "World"}}', active=True),
            ],
        )
        ctx = ZapyRequestContext(store=use_store(), logger=print)
        requester = RequestConverter(zapy_request, ctx)
        request_context = requester.build_httpx_args()

        self.assertDictEqual({"param1": ["Hello World"]}, request_context["params"])

    def test_python_variables(self):
        zapy_request = ZapyRequest(
            endpoint="http://test/",
            method="GET",
            variables=[
                KeyValueItem(key="var1", value='{{ Decimal("0.1") }}', active=True),
            ],
            headers=[
                KeyValueItem(key="X-test", value='{{ Decimal("5") }}', active=True),
                KeyValueItem(key="Content-TYPE", value="{{ ctx.auto() }}", active=True),
            ],
            params=[
                KeyValueItem(key="param1", value='{{var1 + Decimal("0.2")}}', active=True),
            ],
            script=[
                "from decimal import Decimal",
            ],
            body_type="text/plain",
            body=[
                "{{ var1 }}",
            ],
        )
        ctx = ZapyRequestContext(store=use_store(), logger=print)
        requester = RequestConverter(zapy_request, ctx)
        request_context = requester.build_httpx_args()

        self.assertDictEqual({"X-test": "5", "Content-TYPE": "text/plain"}, request_context["headers"])
        self.assertEqual({"param1": ["0.3"]}, request_context["params"])
        self.assertEqual("0.1", request_context["content"])

    def test_jinja_render(self):
        zapy_request = ZapyRequest(
            endpoint="http://test/{{var1}}/{{var2 | upper}}",
            method="GET",
            variables=[
                KeyValueItem(key="var1", value='{#jinja#}{{ "val1" | upper }}', active=True),
                KeyValueItem(key="var2", value="val2", active=True),
                KeyValueItem(key="var3", value="{{[1, 2, 0.3]}}", active=True),
            ],
            params=[
                KeyValueItem(key="param1", value="val: {{var1}}", active=True),
                KeyValueItem(key="param2", value="{{var2 | upper}}", active=True),
                KeyValueItem(key="param3", value="{{ var1 }} {{ var2 }}", active=True),
            ],
            headers=[
                KeyValueItem(key="X-test", value='{#jinja#}{{ "val1" | upper }}', active=True),
                KeyValueItem(key="Content-TYPE", value="{{ ctx.auto() }}", active=True),
            ],
            body_type="text/plain",
            body=[
                "{% for element in var3 -%}",
                "{{element + 4}}",
                "{% endfor %}",
            ],
        )
        ctx = ZapyRequestContext(store=use_store(), logger=print)
        requester = RequestConverter(zapy_request, ctx)
        request_context = requester.build_httpx_args()

        self.assertEqual("http://test/VAL1/VAL2", request_context["url"])
        self.assertDictEqual(
            {
                "param1": ["val: VAL1"],
                "param2": ["VAL2"],
                "param3": ["VAL1 val2"],
            },
            request_context["params"],
        )
        self.assertDictEqual({"X-test": "VAL1", "Content-TYPE": "text/plain"}, request_context["headers"])
        self.assertEqual(
            textwrap.dedent(
                """\
            5
            6
            4.3
            """
            ),
            request_context["content"],
        )

    def test_store(self):
        from decimal import Decimal

        zapy_request = ZapyRequest(
            endpoint="http://test/{{ctx.store.path1}}",
            method="GET",
            params=[
                KeyValueItem(key="param1", value="{{ctx.store.var1 + ctx.store.var2}}", active=True),
            ],
            script=[
                "from decimal import Decimal",
                'ctx.store.var2 = Decimal("0.2")',
            ],
        )
        store = Store()
        store.path1 = "abc"
        store["var1"] = Decimal("0.1")

        ctx = ZapyRequestContext(store=store, logger=print)
        requester = RequestConverter(zapy_request, ctx)
        request_context = requester.build_httpx_args()

        self.assertEqual("http://test/abc", request_context["url"])
        self.assertEqual({"param1": ["0.3"]}, request_context["params"])
        self.assertEqual(Decimal("0.2"), store.var2)
