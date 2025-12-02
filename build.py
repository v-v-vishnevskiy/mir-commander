#!/usr/bin/env python3
"""
Build script for compiling mir_commander core and ui with Cython.
"""

import argparse
import os
from multiprocessing import cpu_count
from pathlib import Path

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
COMPILER_DIRECTIVES = {
    "language_level": "3",
    "embedsignature": True,
    "boundscheck": True,
    "wraparound": True,
    "cdivision": True,
    "profile": False,
}


def _find_python_files(package_dir: str, skip_files: list[str], only_pyx: bool) -> list[str]:
    """Find all .py and .pyx files in a package directory."""
    package_path = PROJECT_ROOT / package_dir

    if package_path.is_file():
        relative = package_path.relative_to(PROJECT_ROOT)
        if only_pyx is True and relative.suffix != ".pyx":
            return []
        return [str(relative)]

    python_files: list[str] = []

    # Find .pyx files first (they have priority over .py)
    pyx_files = {py_file.with_suffix("").name: py_file for py_file in package_path.rglob("*.pyx")}

    if only_pyx is False:
        for py_file in package_path.rglob("*.py"):
            # Skip __init__.py files (they need special handling)
            if py_file.name == "__init__.py":
                continue

            if py_file.name in skip_files:
                continue

            # Skip .py files if there's a corresponding .pyx file
            if py_file.stem in pyx_files:
                continue

            # Convert to module path
            relative = py_file.relative_to(PROJECT_ROOT)
            python_files.append(str(relative))

    # Add all .pyx files
    for pyx_file in package_path.rglob("*.pyx"):
        relative = pyx_file.relative_to(PROJECT_ROOT)
        python_files.append(str(relative))

    return python_files


def _compile(
    package_dir: str, threads: int = 4, force: bool = False, skip_files: None | list[str] = None, only_pyx: bool = False
):
    extensions: list[Extension] = []

    for py_file in _find_python_files(package_dir, skip_files or [], only_pyx):
        module_name = str(Path(py_file).with_suffix("")).replace(os.sep, ".")
        extensions.append(
            Extension(
                module_name,
                [str(py_file)],
                language="c++",
                include_dirs=[np.get_include()],
                extra_compile_args=["-g0", "-O3"],
            )
        )

    setup(
        name="mir-commander",
        script_args=["build_ext", "--inplace", "--build-lib", "build/lib"],
        ext_modules=cythonize(
            extensions,
            compiler_directives=COMPILER_DIRECTIVES,
            nthreads=threads,
            force=force,
        ),
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build mir_commander")
    parser.add_argument("--threads", type=int, default=cpu_count(), help="Number of threads to use for compilation")
    parser.add_argument("--force", type=bool, default=False, help="Force recompilation")
    parser.add_argument("--only-pyx", type=bool, default=False, help="Only compile .pyx files")
    parser.add_argument("--only-plugins", type=bool, default=False, help="Only compile plugins")

    args = parser.parse_args()

    if args.only_plugins:
        _compile(
            package_dir="plugins",
            threads=args.threads,
            force=args.force,
            skip_files=["loader.py"],
            only_pyx=args.only_pyx,
        )
        return

    _compile(package_dir="mir_commander/core", threads=args.threads, force=args.force, only_pyx=args.only_pyx)
    _compile(package_dir="mir_commander/ui", threads=args.threads, force=args.force, only_pyx=args.only_pyx)
    _compile(package_dir="mir_commander/main.py", threads=args.threads, force=args.force, only_pyx=args.only_pyx)
    _compile(
        package_dir="plugins", threads=args.threads, force=args.force, skip_files=["loader.py"], only_pyx=args.only_pyx
    )


if __name__ == "__main__":
    main()
