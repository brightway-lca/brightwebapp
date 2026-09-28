"""
Tests the Pyodide web application end-to-end in a headless browser:
loads the application, loads the USEEIO database, and computes an LCA score.

Usage (from the repository root, with `pip install playwright` and `playwright install chromium`):

```bash
python app/smoke_test.py pyodide # serves and tests the local build in `pyodide/`
python app/smoke_test.py https://webapp.brightway.dev # tests the deployed web application
```
"""
import argparse
import asyncio
import functools
import http.server
import re
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import TimeoutError, async_playwright, expect

PRODUCT = 'Automobiles; at manufacturer'
SCORE = '37.688 [kg CO2 eq]' # of 100 USD of PRODUCT, with the default impact assessment method
TIMEOUT = 300_000 # [ms], loading all packages can be slow on CI runners


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


def serve(directory: Path) -> str:
    """
    Serves `directory` on a free local port in a background thread and returns its URL.
    """
    handler = functools.partial(QuietHandler, directory=directory)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f'http://127.0.0.1:{server.server_port}/'


class PageError(Exception):
    pass


async def smoke_test(url: str) -> list[str]:
    """
    Runs the smoke test against `url` and returns all errors.
    """
    errors = []
    page_error = asyncio.Event()

    def on_page_error(error) -> None:
        errors.append(f'Error in the page: {error}')
        page_error.set()

    def on_request(request) -> None:
        # all packages must be loaded from the lock file, never resolved from the PyPI index
        if urlparse(request.url).hostname == 'pypi.org':
            errors.append(f'Package resolved from PyPI instead of the lock file: {request.url}')

    async def wait(awaitable):
        """
        Awaits `awaitable`, but raises `PageError` as soon as the page raises an error.
        """
        task = asyncio.ensure_future(awaitable)
        error = asyncio.ensure_future(page_error.wait())
        await asyncio.wait({task, error}, return_when=asyncio.FIRST_COMPLETED)
        error.cancel()
        if page_error.is_set():
            task.cancel()
            raise PageError
        return task.result()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context(viewport={'width': 1600, 'height': 1000})
        context.set_default_timeout(TIMEOUT)
        context.on('request', on_request) # includes the requests of the web worker running Pyodide
        page = await context.new_page()
        page.on('pageerror', on_page_error)
        try:
            print(f'Loading {url}', flush=True)
            await page.goto(url)
            await wait(page.wait_for_function("() => !document.body.classList.contains('pn-loading')", timeout=TIMEOUT))

            print('Loading the USEEIO database', flush=True)
            await page.get_by_role('button', name='Load USEEIO Database').click()
            await wait(expect(page.locator('select')).to_have_value(re.compile('GCC'), timeout=TIMEOUT))

            print(f'Computing the LCA score of 100 USD of "{PRODUCT}"', flush=True)
            product = page.get_by_placeholder('Start typing your product name here...')
            await product.press_sequentially(PRODUCT.split(';')[0])
            await wait(page.locator('.bk-menu').get_by_text(PRODUCT, exact=True).click())
            await wait(expect(product).to_have_value(PRODUCT))
            await page.get_by_role('button', name='Compute LCA Score').click()
            await wait(page.locator('.notyf__message').get_by_text('Scope Analysis Complete!').wait_for())

            # the table and pie chart may still be rendering when the notification appears
            await wait(page.locator('.tabulator-row').nth(1).wait_for(timeout=30_000))
            await wait(page.locator('.js-plotly-plot .slice').first.wait_for(timeout=30_000))
            score = await page.get_by_text(re.compile(r'^-?[\d,.]+(e[+-]\d+)? \[kg CO2 eq\]$')).inner_text()
            rows = await page.locator('.tabulator-row').count()
            slices = await page.locator('.js-plotly-plot .slice').count()
            print(f'Score: {score!r}, table rows: {rows}, pie chart slices: {slices}', flush=True)
            if score != SCORE:
                errors.append(f'Expected the LCA score {SCORE!r}, found {score!r}.')
            if rows < 2:
                errors.append(f'Expected at least 2 rows in the table of upstream processes, found {rows}.')
            if slices < 1:
                errors.append('Expected the scope pie chart to show at least 1 slice.')
        except PageError:
            pass # the error is already in `errors`
        except (TimeoutError, AssertionError) as error: # `expect` raises AssertionError
            errors.append(f'{type(error).__name__}: {str(error).splitlines()[0]}')
        finally:
            await browser.close()
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('target', help='a directory to serve (e.g. `pyodide`) or the URL of the web application')
    args = parser.parse_args()
    url = serve(Path(args.target)) if Path(args.target).is_dir() else args.target
    errors = asyncio.run(smoke_test(url))
    if errors:
        sys.exit('Smoke test failed:\n' + '\n'.join(errors))
    print('Smoke test passed.')


if __name__ == '__main__':
    main()
