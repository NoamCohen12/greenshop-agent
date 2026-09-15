"""
אורז את הפרויקט לקובץ ZIP להגשה, במבנה התיקיות הנדרש.
מוודא שקבצים רגישים (.env) וקבצים זמניים אינם נכללים.

הרצה: python build_submission.py
"""

import os
import zipfile

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TEAM_NAME = "Noam"
ARCHIVE_ROOT = f"{TEAM_NAME}_Project"
OUTPUT_ZIP = os.path.join(PROJECT_ROOT, f"{ARCHIVE_ROOT}.zip")

# קבצים ותיקיות שלא נכללים בהגשה
# learning/ הוא חומר לימוד אישי ואינו חלק מההגשה
EXCLUDED_DIRS = {"venv", ".venv", "__pycache__", "chroma_db", ".git", ".idea", ".vscode", "learning"}
EXCLUDED_FILES = {".env", ".DS_Store", os.path.basename(OUTPUT_ZIP)}
EXCLUDED_EXTENSIONS = {".pyc", ".pyo", ".zip"}

# קבצים שחייבים להופיע בהגשה לפי דרישות המסמך
REQUIRED_FILES = [
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "README.md",
    "docs/architecture_diagram.png",
    "docs/langgraph_visualization.png",
    "docs/system_specification.pdf",
]


def should_include(relative_path: str) -> bool:
    parts = relative_path.split(os.sep)

    if any(part in EXCLUDED_DIRS for part in parts):
        return False
    if parts[-1] in EXCLUDED_FILES:
        return False
    if os.path.splitext(parts[-1])[1] in EXCLUDED_EXTENSIONS:
        return False

    return True


def collect_files() -> list[str]:
    collected = []
    for directory, subdirectories, filenames in os.walk(PROJECT_ROOT):
        subdirectories[:] = [name for name in subdirectories if name not in EXCLUDED_DIRS]

        for filename in filenames:
            absolute_path = os.path.join(directory, filename)
            relative_path = os.path.relpath(absolute_path, PROJECT_ROOT)
            if should_include(relative_path):
                collected.append(relative_path)

    return sorted(collected)


def verify_required_files(collected: list[str]) -> list[str]:
    normalized = {path.replace(os.sep, "/") for path in collected}
    return [required for required in REQUIRED_FILES if required not in normalized]


def main():
    files = collect_files()

    missing = verify_required_files(files)
    if missing:
        print("שגיאה - חסרים קבצי חובה להגשה:")
        for path in missing:
            print(f"  - {path}")
        return 1

    # בדיקת בטיחות: לוודא שקובץ הסודות לא נכלל בטעות
    if any(".env" == os.path.basename(path) for path in files):
        print("שגיאה - קובץ .env נכלל בארכיון. ההגשה בוטלה.")
        return 1

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for relative_path in files:
            archive.write(
                os.path.join(PROJECT_ROOT, relative_path),
                os.path.join(ARCHIVE_ROOT, relative_path),
            )

    size_kb = os.path.getsize(OUTPUT_ZIP) / 1024
    print(f"נוצר: {OUTPUT_ZIP}  ({size_kb:.0f} KB, {len(files)} קבצים)\n")
    print("תוכן הארכיון:")
    for relative_path in files:
        print(f"  {ARCHIVE_ROOT}/{relative_path.replace(os.sep, '/')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
