import argparse
import os
import platform
import shutil
import subprocess
from importlib.metadata import version
from pathlib import Path
from urllib.request import urlretrieve

VERSION = version("mir-commander")
ARCH = platform.machine()

PYTHON_VERSION = platform.python_version().rsplit(".", 1)[0]

APPIMAGETOOL_DOWNLOAD_URL = (
    f"https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-{ARCH}.AppImage"
)
APPIMAGETOOL_CACHE_PATH = Path.home() / ".local" / "bin" / f"appimagetool-{ARCH}.AppImage"

RUNTIME_DOWNLOAD_URL = f"https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-{ARCH}"
RUNTIME_CACHE_PATH = Path.home() / ".cache" / "appimage" / f"runtime-{ARCH}"


def _download_file(url: str, cache_path: Path):
    if not cache_path.exists():
        print(f"Downloading {url} to {cache_path}")
        if not cache_path.parent.exists():
            cache_path.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(url, cache_path)
        os.chmod(cache_path, 0o0700)


def _save_desktop_entry(app_dir: Path, name: str, comment: str, category: str, terminal: bool):
    value = f"""
[Desktop Entry]
Type=Application
Version=1.5
Name={name}
Exec={name} %F
Comment={comment}
Icon={name}
Categories={category};
Terminal={"true" if terminal else "false"}
"""

    filename = app_dir / f"{name}.desktop"

    with filename.open("w") as f:
        f.write(value)

    os.chmod(filename, 0o0644)


def _save_entrypoint(app_dir: Path, name: str):
    value = f"""
#!/bin/sh
# If running from an extracted image, fix APPDIR
if [ -z "$APPIMAGE" ]; then
    self="$(readlink -f -- "$0")"
    export APPDIR="${{self%/*}}"
fi
# Call the application entry point
# Use 'exec' to avoid a new process from being started.
exec "$APPDIR/{name}" "$@"
"""

    filename = app_dir / "AppRun"

    with filename.open("w") as f:
        f.write(value)

    os.chmod(filename, 0o0755)


def _build_appimage(app_dir: Path, build_dir: Path, output: Path):
    cmd = [str(APPIMAGETOOL_CACHE_PATH)]
    cmd += ["--appimage-extract-and-run"]
    cmd += ["--runtime-file", str(RUNTIME_CACHE_PATH)]
    cmd += ["--no-appstream", str(app_dir), str(output)]

    _download_file(APPIMAGETOOL_DOWNLOAD_URL, APPIMAGETOOL_CACHE_PATH)
    _download_file(RUNTIME_DOWNLOAD_URL, RUNTIME_CACHE_PATH)

    subprocess.run(cmd, check=True, env={"ARCH": ARCH})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build AppImage for MirCommander")
    parser.add_argument("--app-dir", type=Path, default=Path("build") / "AppDir")
    parser.add_argument("--build-dir", type=Path, default=Path("build") / f"exe.linux-{ARCH}-{PYTHON_VERSION}")
    parser.add_argument("--output", type=Path, default=Path("build") / f"MirCommander-{VERSION}-{ARCH}.AppImage")
    parser.add_argument("--name", type=str, default="MirCommander")
    parser.add_argument(
        "--comment",
        type=str,
        default="A modern, powerful graphical user interface for molecular structure modeling and investigation.",
    )
    parser.add_argument("--category", type=str, default="Science")
    parser.add_argument("--terminal", type=bool, default=False)

    args = parser.parse_args()

    shutil.copytree(
        args.build_dir,
        args.app_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("*.c", "*.c++"),
    )
    shutil.move(args.app_dir / "icon.png", args.app_dir / f"{args.name}.png")
    _save_desktop_entry(args.app_dir, args.name, args.comment, args.category, args.terminal)
    _save_entrypoint(args.app_dir, args.name)
    _build_appimage(args.app_dir, args.build_dir, args.output)
