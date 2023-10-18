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
            const float Pi = 3.14159265;
            const float shininess = 16.0;
            const bool blinn = true;
            vec3 light_color = vec3(1.0, 1.0, 1.0) * 0.9;
            vec3 light_pos = vec3(0.3, 0.3, 1.0);
            vec3 light_dir = normalize(light_pos);
            vec3 norm = normalize(normal);
            float spec = 0.0;

            // Ambient
            float ambient_strength = 0.1;
            vec3 ambient = light_color * ambient_strength;

            // Diffuse
            float diff = max(dot(norm, light_dir), 0.0);
            vec3 diffuse = diff * light_color;

            // Specular
            float specular_strength = 1.0;

            if (blinn) {
                const float energy_conservation = ( 8.0 + shininess ) / ( 8.0 * Pi );
                spec = energy_conservation * pow(max(dot(norm, light_dir), 0.0), shininess);
            }
            else {
               const float energy_conservation = ( 2.0 + shininess ) / ( 2.0 * Pi );
               vec3 reflect_dir = reflect(-light_dir, norm);
               spec = energy_conservation * pow(max(dot(light_dir, reflect_dir), 0.0), shininess);
            }

            vec3 specular = specular_strength * spec * light_color;

            vec4 color = gl_Color;
            vec3 p = ((ambient + diffuse) * color.xyz) + specular;
            gl_FragColor = vec4(p, color.w);
        }
    """,
}
