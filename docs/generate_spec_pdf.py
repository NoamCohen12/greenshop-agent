"""
ממיר את מסמך האפיון מ-Markdown ל-PDF, עם תמיכה בעברית ובכיווניות RTL.
הרצה: python docs/generate_spec_pdf.py
"""

import os
import subprocess

import markdown

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
MARKDOWN_PATH = os.path.join(DOCS_DIR, "system_specification.md")
HTML_PATH = os.path.join(DOCS_DIR, "system_specification.html")
PDF_PATH = os.path.join(DOCS_DIR, "system_specification.pdf")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>מסמך אפיון - GreenShop</title>
<style>
  @page {{ size: A4; margin: 18mm 16mm; }}
  body {{
    font-family: "Segoe UI", Arial, sans-serif;
    line-height: 1.7; color: #222; max-width: 210mm; margin: 0 auto; padding: 10mm;
  }}
  h1 {{ color: #1a4d7a; border-bottom: 3px solid #1a4d7a; padding-bottom: 8px; }}
  h2 {{ color: #1a5d8a; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 28px; }}
  h3 {{ color: #2a6d9a; margin-top: 22px; }}
  h4 {{ color: #3a7daa; margin-top: 18px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 0.95em; }}
  th, td {{ border: 1px solid #bbb; padding: 7px 10px; text-align: right; }}
  th {{ background: #eaf2f8; font-weight: 600; }}
  code {{
    background: #f4f4f4; padding: 2px 5px; border-radius: 3px;
    font-family: Consolas, monospace; direction: ltr; display: inline-block; font-size: 0.9em;
  }}
  pre {{ background: #f7f7f7; padding: 12px; border-radius: 5px; direction: ltr; text-align: left; overflow-x: auto; }}
  pre code {{ background: none; }}
  blockquote {{ border-right: 4px solid #1a5d8a; margin: 12px 0; padding: 6px 14px; background: #f8fbfd; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 26px 0; }}
  ul, ol {{ padding-right: 24px; }}
</style>
</head>
<body>
{content}
</body>
</html>
"""


def find_chrome() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((path for path in candidates if os.path.exists(path)), None)


def main():
    with open(MARKDOWN_PATH, encoding="utf-8") as file:
        html_body = markdown.markdown(file.read(), extensions=["tables", "fenced_code"])

    with open(HTML_PATH, "w", encoding="utf-8") as file:
        file.write(HTML_TEMPLATE.format(content=html_body))
    print(f"נוצר HTML: {HTML_PATH}")

    browser = find_chrome()
    if not browser:
        print("לא נמצא Chrome/Edge - ניתן לפתוח את קובץ ה-HTML ולהדפיס ל-PDF ידנית.")
        return

    subprocess.run(
        [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_PATH}",
            HTML_PATH,
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    print(f"נוצר PDF: {PDF_PATH}")


if __name__ == "__main__":
    main()
