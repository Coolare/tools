import os
import asyncio
from pyppeteer import launch
import subprocess

def use_wkhtml():
    return os.environ.get("USE_WKHTMLTOPDF", "") == "1" or os.environ.get("WKHTMLTOPDF_PATH")

def html_to_pdf_wkhtml(html_path, pdf_path, wk_path=None):
    if wk_path is None:
        wk_path = os.environ.get("WKHTMLTOPDF_PATH", "wkhtmltopdf")
    cmd = [wk_path, "--enable-local-file-access", html_path, pdf_path]
    # ensure absolute paths
    cmd = [cmd[0], os.path.abspath(html_path), os.path.abspath(pdf_path)]
    subprocess.check_call(cmd)
    return pdf_path

async def _html_to_pdf_chrome(html_path, pdf_path):
    chrome_path = os.environ.get("CHROME_PATH")
    launch_kwargs = {
        "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        "headless": True,
    }
    if chrome_path:
        launch_kwargs["executablePath"] = chrome_path
    browser = await launch(**launch_kwargs)
    page = await browser.newPage()
    await page.goto("file://" + os.path.abspath(html_path), {"waitUntil": "networkidle0"})
    await page.pdf({"path": pdf_path, "printBackground": True, "format": "A4"})
    await browser.close()
    return pdf_path

def html_to_pdf(html_path, pdf_path):
    if use_wkhtml():
        return html_to_pdf_wkhtml(html_path, pdf_path)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_html_to_pdf_chrome(html_path, pdf_path))