import os
from weasyprint import HTML, CSS

def use_weasy():
    return os.environ.get("USE_WEASYPRINT", "") == "1"

def html_to_pdf_weasy(html_path, pdf_path, css_paths=None):
    """
    Convert HTML to PDF using WeasyPrint.
    css_paths: optional list of CSS file paths (can be local paths)
    """
    html_abspath = os.path.abspath(html_path)
    pdf_abspath = os.path.abspath(pdf_path)
    html = HTML(filename=html_abspath)
    css_objs = []
    if css_paths:
        for p in css_paths:
            css_objs.append(CSS(filename=os.path.abspath(p)))
    # write_pdf will raise exceptions on failure
    html.write_pdf(pdf_abspath, stylesheets=css_objs)
    return pdf_abspath

def html_to_pdf(html_path, pdf_path):
    if use_weasy():
        return html_to_pdf_weasy(html_path, pdf_path)
    raise RuntimeError("PDF generation requires WeasyPrint. Set USE_WEASYPRINT=1 to enable.")
