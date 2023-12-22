# Zapy REST client

Zapy is a Rest API client based on Python technologies. It aims to solve the duplication issue on integration testing.

---

**Documentation**: [https://docs.zapy.dev](https://docs.zapy.dev)

**Github repo**: [https://github.com/ZapyLabs/zapy-sdk](https://github.com/ZapyLabs/zapy-sdk)

**FAQ**: [https://zapy.dev/faq](https://zapy.dev/faq)

---

**Main feature:**
- You can use python on your requests and import any script or library.
- Your request files can be imported and executed in python.
- As it's used with pytest, it's ready for CI/CD and can be combined with Playwright or any other library.
- It's file based so it's git ready.
- It uses Jinja2 or Python syntax.
- Rapid development using low code user interface.
- Request chaining powered by Jupyter Notebooks.


## Usage

Install the python library under a virtual environment.

```pip install zapydev```

Install the VSCode Extension.
Create a `.zapy` file, for example `my_first_request.zapy` and open it using VSCode.


## Requests

Integrated on VSCode using an extension.

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
Requests and their tests can be invoked directly on your scripts or tests.

```python
from pathlib import Path
import pytest

from zapy import requests
from zapy.utils import module


@pytest.mark.asyncio
async def test_single():
    request = requests.from_path("request1.zapy")
    response = await request.send()
    response.json()

@pytest.mark.asyncio
async def test_chain(self):
    rel_path = Path('tests/assets')
    chain = await module.load_ipynb(
        rel_path / 'chain_import.ipynb',
        variables={
            'rel_path': rel_path
        },
    )
```

## Privacy

Data for authentication is collected when using the Zapy VSCode Extension. No personal or request data is collected.


## License

The Zapy SDK is licensed under the terms of the Business Source License 1.1 (BSL).
The Zapy VSCode Extension is under End User Service Agreement.

By installing or running this software you expressly agree with the terms of use.
