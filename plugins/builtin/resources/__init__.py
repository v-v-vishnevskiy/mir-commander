from pathlib import Path

from mir_commander.api.plugin import Metadata, Plugin, Resource
from mir_commander.api.resources import ResourcesDetails, ResourcesPlugin


def register_plugins() -> list[Plugin]:
    return [
        ResourcesPlugin(
            id="resources",
            metadata=Metadata(
                name="Icons",
                version=(1, 0, 0),
                description="Icons for the builtin plugins",
                author="Mir Commander",
                contacts="https://mircmd.com",
                license="MirCommander",
            ),
            details=ResourcesDetails(),
            resources=[Resource(path=Path("icons.rcc"))],
        )
    ]
