import itertools
import sys
from collections import defaultdict
from threading import Lock

from zapy.base import ZapyAuto
from zapy.templating.eval import exec_sync
from zapy.templating.templating import evaluate, render

from .context import ZapyRequestContext, build_context_module
from .exceptions import error_location
from .file_loader import ZapyFileInfo
from .hooks import RequestHook
from .models import HttpxArguments, KeyValueItem, ZapyRequest

FORM_TYPES = [
    "application/x-www-form-urlencoded",
    "multipart/form-data",
]


class RequestConverter:

    def __init__(self, zapy_request: ZapyRequest, ctx: ZapyRequestContext):
        self.zapy_request = zapy_request
        self.ctx = ctx

        # evaluate script
        request_hooks, variables = self._load_script()
        self.request_hooks = request_hooks
        self.variables = variables

    def build_httpx_args(self) -> HttpxArguments:
        zapy_request: ZapyRequest = self.zapy_request

        # variable_declaration
        self.variables |= self._convert_variables(self.zapy_request.variables)

        httpx_args = HttpxArguments(
            method=zapy_request.method,
            url=self._convert_url(zapy_request.endpoint),
            params=self._convert_params(zapy_request.params),
            headers=self._convert_headers(zapy_request.headers, body_content_type=zapy_request.body_type),
            **self._build_httpx_args_body(zapy_request.body_type, zapy_request.body),
        )

        return httpx_args

    @error_location("body")
    def _build_httpx_args_body(self, body_type: str, body):
        files, data, content = None, None, None
        if body is None or body_type == "None":
            data = None
        elif body_type in FORM_TYPES:
            data, files = self._convert_body_data(body)
        else:
            _body_source = self.__join_code(body)
            content = self.__render(_body_source)
        return {
            "files": files,
            "data": data,
            "content": content,
        }

    @error_location("body")
    def _convert_body_data(self, data_list: list[KeyValueItem]):
        data_list: list[KeyValueItem] = filter(lambda x: x.active and x.key.strip(), data_list)
        result_dict = defaultdict(list)
        files = list()
        for param in data_list:
            value = self.__eval_var(param.value)
            if isinstance(value, ZapyFileInfo):
                file_info = (
                    value.file_name,
                    open(value.file_location, mode="rb"),
                    *([] if value.mime_type is ZapyAuto else [value.mime_type]),
                )
                files.append((param.key, file_info))
            else:
                result_dict[param.key].append(str(value))

        return dict(result_dict), files

    @error_location("url")
    def _convert_url(self, endpoint) -> dict:
        return self.__render(endpoint)

    @error_location("params")
    def _convert_params(self, parameter_list: list[KeyValueItem]) -> dict:
        active_params = filter(lambda x: x.active and x.key.strip(), parameter_list)
        groups = itertools.groupby(active_params, lambda x: x.key.strip())
        result_dict = {key: [self.__render(p.value) for p in params] for key, params in groups}

        return result_dict

    @error_location("headers")
    def _convert_headers(self, header_list: list[KeyValueItem], body_content_type=None) -> dict:
        headers = dict()
        for x in header_list:
            key = x.key.strip()
            if not (x.active and key):
                continue
            eval_var = self.__eval_var(x.value)
            if key.lower() == "content-type" and eval_var == ZapyAuto:
                if body_content_type not in ("None", "multipart/form-data"):
                    headers[key] = str(body_content_type)
            else:
                headers[key] = str(eval_var)

        return headers

    @error_location("variables")
    def _convert_variables(self, variable_list: list[KeyValueItem]):
        return {x.key.strip(): self.__eval_var(x.value) for x in variable_list if x.active and x.key.strip()}

    @error_location("script")
    def _load_script(self) -> tuple[RequestHook, dict]:
        script = self.__join_code(self.zapy_request.script)
        self.script = script

        module_context = build_context_module(self.ctx)
        vars = {
            "print": self.ctx.logger,
            "ctx": module_context,
        }

        if script is None or not script.strip():
            return RequestHook(), vars

        with Lock():
            sys.modules["zapy.ctx"] = module_context
            exec_sync(script, vars)
        request_hook = module_context.hooks.request_hook

        return request_hook, vars

    def __eval_var(self, value):
        return evaluate(value, self.variables)

    def __render(self, source):
        return render(source, self.variables)

    def __join_code(self, code):
        if type(code) == str:
            return code
        else:
            return "\n".join(code)
