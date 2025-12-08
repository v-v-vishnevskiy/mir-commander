import subprocess
from pathlib import Path


def _clean_files(app_dir: Path, pattern: str):
    for file in app_dir.rglob(pattern):
        if file.is_file():
            file.unlink()


if __name__ == "__main__":
    subprocess.run(["resources.cmd"], check=True)
    subprocess.run([str(Path(".venv/Scripts/python.exe")), str(Path("build_scripts/build_lib.py"))], check=True)
    _clean_files(Path.cwd() / "mir_commander", "*.cpp")
    subprocess.run([str(Path(".venv/Scripts/cxfreeze.exe")), "bdist_msi"], check=True)
