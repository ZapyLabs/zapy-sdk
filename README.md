<div>
    <a href="https://docs.zapy.dev">
        <img src="https://docs.zapy.dev/assets/core/zapy_logo_wide_alpha.svg" alt="zapy_logo" style="width: 250px;">
    </a>
</div>

_The pythonic REST client and testing tool._

<p>
<a href="https://github.com/ZapyLabs/zapy-sdk/actions/workflows/python-publish.yml/badge.svg" target="_blank">
    <img src="https://github.com/ZapyLabs/zapy-sdk/actions/workflows/python-publish.yml/badge.svg" alt="Test">
</a>
<a href="https://media.zapy.dev/htmlcov/index.html" target="_blank">
    <img src="https://media.zapy.dev/coverage-badge" alt="Coverage">
</a>
<a href="https://pypi.org/project/zapy-sdk" target="_blank">
    <img src="https://img.shields.io/badge/%F0%9F%9A%80%20release-alpha-yellow" alt="Version">
</a>
<a href="https://pypi.org/project/zapy-sdk" target="_blank">
    <img src="https://img.shields.io/pypi/v/zapy-sdk?label=package&logo=pypi&logoColor=f5f5f5" alt="Package version">
</a>
<a href="https://pypi.org/project/zapy-sdk" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/zapy-sdk?logo=python&logoColor=f5f5f5" alt="Supported Python versions">
</a>
</p>

# Zapy REST Client - SDK

Zapy REST Client is an extension for VSCode that serves as a tool for testing APIs. The accompanying Zapy SDK, a Python library, is an integral component that enables the utilization of Zapy request files, empowering the client and Python scripts to perform API operations. The primary goal is to streamline the process of API testing.

---

**Documentation**: [https://docs.zapy.dev](https://docs.zapy.dev)

**Github repo**: [https://github.com/ZapyLabs/zapy-sdk](https://github.com/ZapyLabs/zapy-sdk)

**FAQ**: [https://zapy.dev/faq](https://zapy.dev/faq)

---

### **Key features**

❤️ **Python/Jinja2 expressions**: Utilize 🐍 Python and Jinja2 expressions for variable declaration and string templating.

🗔 **Visual interface**: Enjoy the VSCode extension for rapid development, enhancing productivity and ease of use.

⚡️ **Async operations**: Support async functions, hooks and stores for handling requests and responses.

📝 **File based and git sync**: Manage your requests with file-based local storage and optional Git for collaboration 👨‍👩‍👧‍👦.

🐍 **Python scripting and tests**. Leverage Python scripting capabilities and conduct tests within the client. Import packages and use snippets for enhanced functionality and customization.

🚀 **CI/CD Ready**: Import and execute request files directly within your integration tests.

♻️ **Request reusability and invocation**: Reuse requests and integrate seamlessly with your favorite tools such as pytest, Playwright, or Robot Framework, enhancing interoperability and extensibility.

🔗 **Chaining**: Chain requests using Jupyter notebooks and/or stores, facilitating interactive exploration and collaboration.


## Requirements

Python 3.11+

For using the VSCode extension:
- Python virtual environment
- Zapy SDK
- VSCode

## Usage

1) Install [Zapy VSCode Extension](https://marketplace.visualstudio.com/items?itemName=zapydev.zapy-rest-client).

2) Install the python library under a virtual environment.

    ```sh
    pip install zapy-sdk
    ```

3) Create a `.zapy` file, for example `my_first_request.zapy`.
4) Start the Zapy server.
5) Send your request 🚀.

![installation](https://docs.zapy.dev/assets/docs/zapy_install.gif)


## Requests

Create requests visually using the [Zapy VSCode Extension](https://marketplace.visualstudio.com/items?itemName=zapydev.zapy-rest-client).

![first look](https://docs.zapy.dev/assets/docs/first_look.webp)

## Stores
Stores enable the persistence and inspection of Python data for use in multiple requests, including the creation and management of [environment variables](https://docs.zapy.dev/guides/environment_variables).


![stores](https://docs.zapy.dev/assets/docs/stores.webp)

## Hooks
Hooks can be global or request-specific, allowing interception and modification of requests, such as for [authentication](https://docs.zapy.dev/guides/authentication).

```python
from zapy.requests import hooks, HttpxArguments

@hooks.pre_request
async def on_each_request(httpx_args: HttpxArguments):
    httpx_args['auth'] = ('alice', 'ecila123')
    print(httpx_args)
```

## Chaining
[Chaining](https://docs.zapy.dev/guides/chaining) runs a sequence of requests with one click, using responses from one request in the next. It also offers the ability to use conditionals or to resume from a failed step.

![chaining](https://docs.zapy.dev/assets/docs/jupyter_chain.webp)

## Integration test
Requests and their tests can be invoked directly on your [integration tests](https://docs.zapy.dev/guides/testing/).

```python
import pytest
from zapy import requests

@pytest.mark.asyncio
async def test_single():
    request = requests.from_path("request1.zapy")
    # if raise_assert is enabled, it will perform all assertions defined in the request file
    _ = await request.send(raise_assert=True)
```

## Privacy

Data for authentication is collected when using Zapy VSCode Extension. No personal or request data is collected.


## License

Zapy REST Client - SDK (a.k.a. Zapy SDK) is licensed under the terms of the Business Source License 1.1 (BSL).
Zapy REST Client (a.k.a. Zapy VSCode Extension) is under End User Service Agreement.

By installing or running this software you expressly agree with the terms of use.
