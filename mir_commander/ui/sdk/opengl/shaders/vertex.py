WBOIT_FINALIZE = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 2) in vec2 in_texcoord;

out vec2 fragment_texcoord;

void main() {
    gl_Position = vec4(position.xy, 0.0, 1.0);
    fragment_texcoord = in_texcoord;
}
"""


COMPUTE_POSITION_INSTANCED = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in vec4 instance_color;
layout (location = 4) in mat4 instance_model_matrix;

uniform mat4 scene_matrix;
uniform mat4 transform_matrix;

out vec3 normal;
out vec4 fragment_color;
out vec2 fragment_texcoord;

void main() {
    gl_Position = transform_matrix * instance_model_matrix * vec4(position, 1.0);

    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * instance_model_matrix))) * in_normal;
    fragment_color = instance_color;
    fragment_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
}
"""


COMPUTE_POSITION_INSTANCED_BILLBOARD = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in vec4 instance_color;
layout (location = 4) in mat4 instance_model_matrix;
layout (location = 8) in vec3 instance_char_local_position;
layout (location = 10) in vec3 instance_text_world_position;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform mat4 transform_matrix;

out vec2 fragment_texcoord;
out vec4 fragment_color;

void main() {
    vec3 view_scale;
    view_scale.x = length(vec3(view_matrix[0][0], view_matrix[0][1], view_matrix[0][2]));
    view_scale.y = length(vec3(view_matrix[1][0], view_matrix[1][1], view_matrix[1][2]));
    view_scale.z = length(vec3(view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]));

    vec3 scene_scale;
    scene_scale.x = length(vec3(scene_matrix[0][0], scene_matrix[0][1], scene_matrix[0][2]));
    scene_scale.y = length(vec3(scene_matrix[1][0], scene_matrix[1][1], scene_matrix[1][2]));
    scene_scale.z = length(vec3(scene_matrix[2][0], scene_matrix[2][1], scene_matrix[2][2]));

    vec3 model_scale;
    model_scale.x = length(vec3(instance_model_matrix[0][0], instance_model_matrix[0][1], instance_model_matrix[0][2]));
    model_scale.y = length(vec3(instance_model_matrix[1][0], instance_model_matrix[1][1], instance_model_matrix[1][2]));
    model_scale.z = length(vec3(instance_model_matrix[2][0], instance_model_matrix[2][1], instance_model_matrix[2][2]));

    vec3 scale = model_scale * scene_scale * view_scale;

    // Extract billboard center position from instance model matrix
    vec3 billboard_center = instance_text_world_position;

    // Transform center to view space
    vec4 view_center = view_matrix * scene_matrix * vec4(billboard_center, 1.0);

    // Apply billboard transformation: offset vertex in view space
    // This makes the quad always face the camera
    vec4 view_position = view_center;
    view_position.xy += position.xy * scale.xy + instance_char_local_position.xy * scale.xy;

    // Project to clip space
    gl_Position = projection_matrix * view_position;

    fragment_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
    fragment_color = instance_color;
}
"""


PICKING = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 3) in vec4 instance_color;
layout (location = 4) in mat4 instance_model_matrix;

uniform mat4 transform_matrix;

out vec4 fragment_color;

void main() {
    gl_Position = transform_matrix * instance_model_matrix * vec4(position, 1.0);
    fragment_color = instance_color;
}
"""
