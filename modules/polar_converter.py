import math # For mathematical functions like sqrt, cos, sin, etc. 
import cmath # For complex number operations like phase() 
import io # For creating in-memory image buffers 
import base64 # To encode images as base64 for embedding in HTML 
import matplotlib.pyplot as plt # For plotting vector representation 
import numpy as np # For numerical operations, especially with arrays
def create_complex_plot(x, y, title, show_coords=False):
    # Create a new plot figure and axis
    fig, ax = plt.subplots()

    # Draw the complex number vector from origin to point (x, y)
    ax.quiver(0, 0, x, y, angles='xy', scale_units='xy', scale=1, color='blue', linewidth=1)

    # Set the plot limits for x and y axes
    # Determine limits based on vector length
    max_val = max(abs(x), abs(y))
    margin = max_val * 0.2  # 20% margin around the vector
    if margin < 2:
        margin = 2  # keep minimum padding for small values

    x_min = - (max_val + margin)
    x_max = (max_val + margin)
    y_min = - (max_val + margin)
    y_max = (max_val + margin)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)


    # Draw the real and imaginary axes
    ax.axhline(0, color='gray', linestyle='--')
    ax.axvline(0, color='gray', linestyle='--')

    # Enable grid for better readability
    ax.grid(True)

    # Label the axes
    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginary")

    # Set the plot title (dynamic based on mode)
    ax.set_title(title)

    # Calculate modulus (|z|) and argument (θ)
    r = round(math.hypot(x, y), 2)
    angle_rad = math.atan2(y, x)
    angle_deg = round(math.degrees(angle_rad), 2)

    # --- Draw angle arc ---
    # Dynamic arc radius so it doesn't go out of bounds
    max_radius = min(10, max(abs(x), abs(y)) + 2)  # margin inside axes
    arc_radius = min(r * 0.3, max_radius * 0.3)

    # θ arc
    theta_arc = np.linspace(0, angle_rad, 100)
    ax.plot(arc_radius * np.cos(theta_arc), arc_radius * np.sin(theta_arc), 'r--', linewidth=2)

    # Adjusted θ label position to keep inside bounds
    label_x_pos = arc_radius * 1.1 * math.cos(angle_rad / 2)
    label_y_pos = arc_radius * 1.1 * math.sin(angle_rad / 2) - 0.1
    label_x_pos = max(-9.5, min(9.5, label_x_pos))
    label_y_pos = max(-9.5, min(9.5, label_y_pos))
    ax.text(label_x_pos, label_y_pos,
        f"θ = {angle_deg}°", color='crimson', fontsize=9, ha='left', va='bottom')

    # --- Show Cartesian coordinates if requested ---
    if show_coords:
        ax.text(x + 0.3, y, f"({round(x,2)}, {round(y,2)})",
                color='purple', fontsize=9, ha='left', va='center')

    # Save the plot to a bytes buffer in PNG format
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_data = base64.b64encode(img.read()).decode()
    plt.close()

    return f"data:image/png;base64,{plot_data}"


def polar_converter_handler(mode, input1, input2):
    input1 = float(input1)
    input2 = float(input2)
    
    if mode == 'cartesian':
        z = complex(input1, input2)
        r = abs(z)
        theta = math.degrees(cmath.phase(z))
        result = f"Polar Form for {input1} and {input2}:\n (r = {round(r, 2)}, θ = {round(theta, 2)}°)"
        explanation = f"This means the complex number lies {round(r,2)} units from origin and at an angle of {round(theta, 2)}° from the positive real axis."
        plot = create_complex_plot(input1, input2, "Cartesian to Polar", show_coords=False)

    elif mode == 'polar':
        r = input1
        theta = math.radians(input2)
        a = r * math.cos(theta)
        b = r * math.sin(theta)
        result = f"Cartesian Form: z = {round(a,2)} + {round(b,2)}i"
        explanation = f"This means the point lies at distance {r} from origin at angle {input2}°. Projecting onto real and imaginary axes gives coordinates ({round(a,2)}, {round(b,2)})."
        plot = create_complex_plot(a, b, "Polar to Cartesian", show_coords=True)

    else:
        result = "<strong>Error:</strong> Invalid mode selected."
        plot = ""
        explanation = ""
    
    return result, plot, explanation
