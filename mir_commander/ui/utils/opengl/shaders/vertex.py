COMPUTE_POSITION = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform mat4 model_matrix;
uniform bool is_billboard;

out vec3 normal;
out vec3 fragment_position;

void main() {
    gl_Position = projection_matrix * view_matrix * scene_matrix * model_matrix * vec4(position, 1.0);
    
    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * model_matrix))) * in_normal;
    fragment_position = vec3(scene_matrix * model_matrix * vec4(position, 1.0));
}
"""

COMPUTE_POSITION_INSTANCED = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;

// Instanced attributes for transformation matrix
layout (location = 2) in mat4 instance_model_matrix;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform bool is_billboard;

out vec3 normal;
out vec3 fragment_position;

void main() {
    if (is_billboard) {
        gl_Position = projection_matrix * scene_matrix * instance_model_matrix * vec4(position, 1.0);
    }
    else {
        gl_Position = projection_matrix * view_matrix * scene_matrix * instance_model_matrix * vec4(position, 1.0);
    }

    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * instance_model_matrix))) * in_normal;
    fragment_position = vec3(scene_matrix * instance_model_matrix * vec4(position, 1.0));
}
"""


COMPUTE_POSITION_INSTANCED_WITH_TEXTURE = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in mat4 instance_model_matrix;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec3 normal;
out vec3 fragment_position;
out vec2 fragment_texcoord;

void main() {
    gl_Position = projection_matrix * view_matrix * scene_matrix * instance_model_matrix * vec4(position, 1.0);
    
    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * instance_model_matrix))) * in_normal;
    fragment_position = vec3(scene_matrix * instance_model_matrix * vec4(position, 1.0));
    fragment_texcoord = in_texcoord;
}
"""

TEXT = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in mat4 instance_model_matrix;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec2 fragment_texcoord;

void main() {
    vec3 camera_position = vec3(-view_matrix[3][0], -view_matrix[3][1], -view_matrix[3][2]);

    vec3 scene_scale;
    scene_scale.x = length(vec3(scene_matrix[0][0], scene_matrix[0][1], scene_matrix[0][2]));
    scene_scale.y = length(vec3(scene_matrix[1][0], scene_matrix[1][1], scene_matrix[1][2]));
    scene_scale.z = length(vec3(scene_matrix[2][0], scene_matrix[2][1], scene_matrix[2][2]));

    vec3 model_scale;
    model_scale.x = length(vec3(instance_model_matrix[0][0], instance_model_matrix[0][1], instance_model_matrix[0][2]));
    model_scale.y = length(vec3(instance_model_matrix[1][0], instance_model_matrix[1][1], instance_model_matrix[1][2]));
    model_scale.z = length(vec3(instance_model_matrix[2][0], instance_model_matrix[2][1], instance_model_matrix[2][2]));

    // apply scale to position
    vec3 scaled_position = position * model_scale * scene_scale;

    // get object position in world space
    vec3 object_pos = vec3(scene_matrix * instance_model_matrix * vec4(0.0, 0.0, 0.0, 1.0));

    float label_offset = 0.3 * 2;

    // direction from object to camera
    vec3 to_camera = normalize(camera_position - object_pos);

    // move label in front of the object
    vec3 billboard_pos = object_pos + scaled_position + to_camera * label_offset;

    vec4 world_pos = vec4(billboard_pos, 1.0);
    gl_Position = projection_matrix * view_matrix * world_pos;

    fragment_texcoord = in_texcoord;
}
"""
