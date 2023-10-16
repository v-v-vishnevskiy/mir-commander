SHADED = {
    "vertex": """
        varying vec3 normal;
        void main() {
            normal = normalize(gl_NormalMatrix * gl_Normal);
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
        }
    """,
    "fragment": """
        varying vec3 normal;
        void main() {
            float p = dot(normal, normalize(vec3(1.0, 1.0, 1.0)));
            p = p < 0. ? 0. : p * 0.8;
            vec4 color = gl_Color;
            color.x = color.x * (0.2 + p);
            color.y = color.y * (0.2 + p);
            color.z = color.z * (0.2 + p);
            gl_FragColor = color;
        }
    """,
}
