#!/usr/bin/env python3

import platform
from importlib.metadata import version

from dmgbuild import build_dmg

settings = dict(
    files=["build/Mir Commander.app", "resources/policy/LICENSE"],
    symlinks={"Applications": "/Applications"},
    icon="resources/building/macos/icon.icns",
    text_size=13.0,
    icon_size=72.0,
    background="build/background.tiff",
    window_rect=((800, 600), (480, 450)),
    icon_locations={"Mir Commander.app": (140, 90), "Applications": (340, 90), "LICENSE": (140, 250)},
)


def _operation_print(data: dict[str, str]):
    if "type" in data and "finished" in data["type"]:
        if op := data.get("operation", data.get("command")):
            if op == "size::calculate":
                print("Size calculated")
            elif op == "hdiutil::create":
                print(f"Disk image created: {data['output']}")
            elif op == "hdiutil::attach":
                print("Disk image attached")
            elif op == "hdiutil::detach":
                print("Disk image detached")
            elif op == "hdiutil::resize":
                print("Disk image resized")
            elif op == "hdiutil::convert":
                print(f"Disk image converted: {data['output']}")
            elif op == "file::add":
                print(f"File added: {data['file']}")
            elif op == "symlink::add":
                print(f"Symlink added: {data['file']} -> {data['target']}")
            elif op == "background::create":
                print("Background created")
            elif op == "dsstore::create":
                print("DSStore created")
            elif op == "dmg::create":
                print("DMG created")
            elif op == "dmg::shrink":
                print("DMG shrunken to fit the contents")
            elif op in ("extensions::hide", "symlinks::add", "files::add"):
                pass
            else:
                print(op)


if __name__ == "__main__":
    build_dmg(
        filename=f"build/MirCommander-{version('mir-commander')}-{platform.machine()}.dmg",
        volume_name="Mir Commander",
        settings=settings,
        lookForHiDPI=True,
        callback=_operation_print,
    )
