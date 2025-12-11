from pathlib import Path

from mir_commander.api.plugin import Metadata, Plugin, Resource, Translation
from mir_commander.api.resources import ResourcesDetails, ResourcesPlugin


def register_plugins() -> list[Plugin]:
    return [
        ResourcesPlugin(
            id="resources",
            metadata=Metadata(
                name="Core resources",
                version=(1, 0, 0),
                description="Resources of the builtin plugins",
                publisher="mircmd.com",
            ),
            details=ResourcesDetails(),
            resources=[
                Resource(
                    path=Path("resources.rcc"),
                    translations=[Translation(filename="", prefix="", path="translations/i18n")],
                )
            ],
        )
    ]
