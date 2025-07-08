TRANSPARENT = {
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
            vec3 norm = normalize(normal);

            // Simple lighting for the transparent sphere
            vec3 light_dir = normalize(vec3(0.3, 0.3, 1.0));
            float diff = max(dot(norm, light_dir), 0.0);

            vec4 color = gl_Color;
            // Make the sphere semi-transparent
            // color.a = 0.7;  // Fixed transparency

            // Add some diffuse lighting to the transparent sphere
            vec3 diffuse = diff * vec3(1.0, 1.0, 1.0) * 0.2;
            color.rgb = color.rgb + diffuse;
            
            gl_FragColor = color;
        }
    """,
}
