from .scene_node import SceneNode


class RenderingContainer:
    def __init__(self, name: str):
        self.name = name
        self.nodes: dict = {}
        self.transform_dirty: dict[tuple, bool] = {}

    def __bool__(self):
        return bool(self.nodes)

    def add_node(self, node: SceneNode):
        group_id = node.group_id
        shader_name, model_name, material = group_id

        if shader_name not in self.nodes:
            self.nodes[shader_name] = {}
        if model_name not in self.nodes[shader_name]:
            self.nodes[shader_name][model_name] = {}
        if material not in self.nodes[shader_name][model_name]:
            self.nodes[shader_name][model_name][material] = []
        if node not in self.nodes[shader_name][model_name][material]:
            self.transform_dirty[group_id] = True
            self.nodes[shader_name][model_name][material].append(node)

    def remove_node(self, node: SceneNode):
        group_id = node.group_id
        shader_name, model_name, material = group_id

        try:
            self.nodes[shader_name][model_name][material].remove(node)
            self.transform_dirty[group_id] = True

            if len(self.nodes[shader_name][model_name][material]) == 0:
                del self.nodes[shader_name][model_name][material]
            if len(self.nodes[shader_name][model_name]) == 0:
                del self.nodes[shader_name][model_name]
            if len(self.nodes[shader_name]) == 0:
                del self.nodes[shader_name]
        except (KeyError, ValueError):
            # Node was already removed
            pass

    def set_transform_dirty(self, node: SceneNode):
        self.transform_dirty[node.group_id] = True

    def clear(self):
        self.nodes.clear()
        self.transform_dirty.clear()

    def clear_transform_dirty(self):
        self.transform_dirty.clear()

    def __repr__(self) -> str:
        result = []
        for key, value in self.nodes.items():
            result.append(f"{key}:")
            for key2, value2 in value.items():
                result.append(f"  {key2}:")
                for key3, value3 in value2.items():
                    result.append(f"    {key3}:")
                    for node in value3:
                        result.append(f"      {node}")

        nodes = "\n".join(result)

        return f"{self.__class__.__name__}(name={self.name}, nodes={nodes})"
