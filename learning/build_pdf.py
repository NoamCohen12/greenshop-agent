"""
ממיר את חומרי הלימוד מ-Markdown ל-PDF אחד, לקריאה נוחה בנייד או בהדפסה.

הרצה: python learning/build_pdf.py
"""

import glob
import os
import subprocess

import markdown

LEARNING_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(LEARNING_DIR, "GreenShop_Learning.html")
PDF_PATH = os.path.join(LEARNING_DIR, "GreenShop_Learning.pdf")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>חומר לימוד - GreenShop</title>
<style>
  @page {{ size: A4; margin: 16mm 14mm; }}
  body {{
    font-family: "Segoe UI", Arial, sans-serif;
    line-height: 1.75; color: #1a1a1a; font-size: 11.5pt;
    max-width: 190mm; margin: 0 auto;
  }}
  h1 {{
    color: #1a4d7a; border-bottom: 3px solid #1a4d7a;
    padding-bottom: 8px; page-break-before: always; margin-top: 0;
  }}
  h1:first-of-type {{ page-break-before: avoid; }}
  h2 {{ color: #1a5d8a; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }}
  h3 {{ color: #2a6d9a; margin-top: 22px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 0.93em; }}
  th, td {{ border: 1px solid #bbb; padding: 7px 10px; text-align: right; vertical-align: top; }}
  th {{ background: #eaf2f8; font-weight: 600; }}
  code {{
    background: #f2f2f2; padding: 2px 5px; border-radius: 3px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 0.88em;
    /* בידוד דו-כיווני: מונע מסימני פיסוק עבריים לקפוץ לצד הלא נכון
       כשמונח באנגלית מופיע באמצע משפט בעברית */
    direction: ltr; unicode-bidi: isolate; display: inline;
  }}
  pre {{
    background: #f8f8f8; border: 1px solid #e0e0e0; padding: 12px;
    border-radius: 5px; direction: ltr; text-align: left;
    overflow-x: auto; page-break-inside: avoid; font-size: 0.85em; line-height: 1.5;
  }}
  pre code {{ background: none; padding: 0; font-size: 1em; }}
  blockquote {{
    border-right: 4px solid #1a5d8a; margin: 14px 0;
    padding: 8px 16px; background: #f6fafd; color: #333;
  }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 26px 0; }}
  ul, ol {{ padding-right: 26px; }}
  li {{ margin: 5px 0; }}
  strong {{ color: #0d3b5c; }}
</style>
</head>
<body>
{content}
</body>
</html>
"""


def find_browser() -> str | None:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((path for path in candidates if os.path.exists(path)), None)


def main():
    chapter_paths = sorted(glob.glob(os.path.join(LEARNING_DIR, "[0-9][0-9]_*.md")))
    if not chapter_paths:
        print("לא נמצאו קבצי חומר לימוד.")
        return

    sections = []
    for path in chapter_paths:
        with open(path, encoding="utf-8") as file:
            sections.append(file.read())
        print(f"נכלל: {os.path.basename(path)}")

    html_body = markdown.markdown("\n\n".join(sections), extensions=["tables", "fenced_code"])

    with open(HTML_PATH, "w", encoding="utf-8") as file:
        file.write(HTML_TEMPLATE.format(content=html_body))

    browser = find_browser()
    if not browser:
        print(f"\nנוצר HTML: {HTML_PATH}")
        print("לא נמצא Chrome/Edge — ניתן לפתוח את ה-HTML ולהדפיס ל-PDF ידנית.")
        return

    subprocess.run(
        [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={PDF_PATH}", HTML_PATH],
        check=True, capture_output=True, timeout=180,
    )
    print(f"\nנוצר PDF: {PDF_PATH}")


if __name__ == "__main__":
    main()
