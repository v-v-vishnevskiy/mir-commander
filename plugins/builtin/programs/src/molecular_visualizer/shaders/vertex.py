ATOM_LABEL = """
#version 330 core

layout (location = 0) in vec3 position;  // world vertex position
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in vec4 instance_color;
layout (location = 7) in mat4 instance_model_matrix;
layout (location = 11) in vec3 instance_char_local_position;
layout (location = 13) in vec3 instance_text_world_position;
layout (location = 14) in vec3 instance_atom_world_position;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec2 fragment_texcoord;
out vec4 fragment_color;
out float fragment_depth;

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

    // apply scale to char position
    vec3 scaled_char_local_position = (position + instance_char_local_position) * scale;

    // get atom position in world space
    vec3 world_atom_pos = vec3(view_matrix * scene_matrix * vec4(instance_atom_world_position, 1.0));
    vec3 world_text_pos = vec3(view_matrix * scene_matrix * vec4(instance_text_world_position, 1.0));

    gl_Position = projection_matrix * vec4(scaled_char_local_position + world_atom_pos, 1.0);
    fragment_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
    fragment_color = instance_color;

    float world_dist = length(world_text_pos - world_atom_pos);
    vec4 text_pos = projection_matrix * vec4(scaled_char_local_position + vec3(world_atom_pos.xy, world_atom_pos.z + world_dist), 1.0);
    fragment_depth = (text_pos.z / text_pos.w + 1.0) / 2.0;
}
"""
