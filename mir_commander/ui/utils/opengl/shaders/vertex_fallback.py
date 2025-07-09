COMPUTE_POSITION = """
varying vec3 normal;
void main() {
    normal = normalize(gl_NormalMatrix * gl_Normal);
    gl_FrontColor = gl_Color;
    gl_BackColor = gl_Color;
    gl_Position = ftransform();
}
"""
