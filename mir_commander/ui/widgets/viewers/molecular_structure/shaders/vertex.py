ATOM_LABEL = """
#version 330 core

layout (location = 0) in vec3 position;  // world vertex position
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in vec4 instance_color;
layout (location = 4) in mat4 instance_model_matrix;
layout (location = 8) in vec3 instance_char_local_position;
layout (location = 9) in vec3 instance_text_local_position;
layout (location = 11) in vec3 instance_atom_world_position;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec2 fragment_texcoord;
out vec4 fragment_color;

void main() {
    vec3 scale_view;
    scale_view.x = length(vec3(view_matrix[0][0], view_matrix[0][1], view_matrix[0][2]));
    scale_view.y = length(vec3(view_matrix[1][0], view_matrix[1][1], view_matrix[1][2]));
    scale_view.z = length(vec3(view_matrix[2][0], view_matrix[2][1], view_matrix[2][2]));

    vec3 scene_scale;
    scene_scale.x = length(vec3(scene_matrix[0][0], scene_matrix[0][1], scene_matrix[0][2]));
    scene_scale.y = length(vec3(scene_matrix[1][0], scene_matrix[1][1], scene_matrix[1][2]));
    scene_scale.z = length(vec3(scene_matrix[2][0], scene_matrix[2][1], scene_matrix[2][2]));

    vec3 model_scale;
    model_scale.x = length(vec3(instance_model_matrix[0][0], instance_model_matrix[0][1], instance_model_matrix[0][2]));
    model_scale.y = length(vec3(instance_model_matrix[1][0], instance_model_matrix[1][1], instance_model_matrix[1][2]));
    model_scale.z = length(vec3(instance_model_matrix[2][0], instance_model_matrix[2][1], instance_model_matrix[2][2]));

    vec3 scale = model_scale * scene_scale * scale_view;

    // apply scale to char position
    vec3 scaled_char_local_position = (position + instance_char_local_position) * scale;

    vec3 diff = instance_text_local_position * scale;

    // get atom position in world space
    vec3 atom_pos = vec3(view_matrix * scene_matrix * vec4(instance_atom_world_position, 1.0));

    vec4 proj_atom = projection_matrix * vec4(scaled_char_local_position + atom_pos, 1.0);
    vec4 proj_char = projection_matrix * vec4(scaled_char_local_position + atom_pos + diff * 2.2, 1.0);

    gl_Position = vec4(proj_atom.xy, proj_char.z, proj_atom.w);

    fragment_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
    fragment_color = instance_color;
}
"""
