from dataclasses import dataclass


@dataclass
class Metadata:
    """
    Metadata for plugins.

    Example:
        Metadata(
            name="My Format",
            version=(1, 0, 0),
            description="My Format",
            author="My Name",
            email="my@email.com",
            url="https://my.url.com",
            license="MIT",
        )
    """

    name: str
    version: tuple[int, int, int]
    description: str
    author: str
    email: str
    url: str
    license: str
