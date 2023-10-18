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
            vec3 light_color = vec3(1.0, 1.0, 1.0) * 0.9;
            vec3 light_pos = vec3(0.3, 0.3, 1.0);

            // Ambient
            float ambient_strength = 0.1;
            vec3 ambient = light_color * ambient_strength;

            // Diffuse
            vec3 norm = normalize(normal);
            vec3 light_dir = normalize(light_pos);
            float diff = max(dot(norm, light_dir), 0.0);
            vec3 diffuse = diff * light_color;

            // Specular
            float specular_strength = 1.0;
            vec3 FragPos = gl_FragCoord.xyz;
            vec3 viewDir = normalize(light_pos);
            vec3 reflectDir = reflect(-light_dir, norm);
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16.0);
            vec3 specular = specular_strength * spec * light_color;

            vec4 color = gl_Color;
            vec3 p = ((ambient + diffuse) * color.xyz) + specular;
            gl_FragColor = vec4(p, color.w);
        }
    """,
}
