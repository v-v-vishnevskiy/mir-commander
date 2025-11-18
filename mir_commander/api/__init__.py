"""
Mir Commander Plugin API.
"""

__api_version__ = (1, 0, 0)
__version__ = ".".join(map(str, __api_version__))


from .project_node_schema import ProjectNodeSchema, ProjectNodeSchemaV1

__all__ = [
    "__version__",
    "__api_version__",
    "ProjectNodeSchema",
    "ProjectNodeSchemaV1",
]
