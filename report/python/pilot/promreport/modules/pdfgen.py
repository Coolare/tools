import os
import subprocess

def use_wkhtml():
    """
    Decide to use wkhtmltopdf when env USE_WKHTMLTOPDF=1 or explicit WKHTMLTOPDF_PATH set.
    """
    return os.environ.get("USE_WKHTMLTOPDF", "") == "1" or bool(os.environ.get("WKHTMLTOPDF_PATH"))

def html_to_pdf_wkhtml(html_path, pdf_path, wk_path=None, extra_args=None):
    """
    Convert HTML to PDF using wkhtmltopdf binary.
    - html_path, pdf_path can be relative or absolute. This function will convert to absolute paths.
    - wk_path: optional path to wkhtmltopdf binary. If None, will use env WKHTMLTOPDF_PATH or 'wkhtmltopdf'.
    - extra_args: list of extra args to pass before input/output (e.g. ['--margin-top','10mm'])
    """
    if wk_path is None:
        wk_path = os.environ.get("WKHTMLTOPDF_PATH", "wkhtmltopdf")
    html_abspath = os.path.abspath(html_path)
    pdf_abspath = os.path.abspath(pdf_path)
    cmd = [wk_path]
    # recommended flags: enable local file access for embedded resources, quiet to reduce noise
    cmd += ["--enable-local-file-access", "--quiet"]
    # allow passing additional flags via env or arg
    if extra_args:
        cmd += extra_args
    cmd += [html_abspath, pdf_abspath]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"wkhtmltopdf failed (exit {e.returncode}): {' '.join(cmd)}") from e
    except FileNotFoundError as e:
        raise RuntimeError(f"wkhtmltopdf executable not found: {wk_path}") from e
    return pdf_abspath

def html_to_pdf(html_path, pdf_path):
    """
    Public entrypoint: use wkhtmltopdf if configured; otherwise raise (we no longer call pyppeteer here).
    """
    if use_wkhtml():
        return html_to_pdf_wkhtml(html_path, pdf_path)
    # If not set to use wkhtml, still prefer wkhtml by default to avoid pyppeteer issues.
    # But keep a clear error so caller can set env if needed.
    raise RuntimeError("PDF generation requires wkhtmltopdf. Set environment variable USE_WKHTMLTOPDF=1 or WKHTMLTOPDF_PATH to point to binary.")
