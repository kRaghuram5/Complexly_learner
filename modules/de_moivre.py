# Force matplotlib to use a non-interactive backend suitable for web rendering
import matplotlib
matplotlib.use('Agg')  # Must come before importing pyplot for Flask or headless environments

import matplotlib.pyplot as plt        # For plotting
import numpy as np                    # For math operations (angles, trigonometry)
import io                             # To store image in-memory
import base64                         # To encode image to base64 for HTML embedding

# Function to visualize De Moivre's Theorem
# Parameters:
#   r         : magnitude of the complex number
#   theta_deg : angle in degrees
#   n         : exponent to raise the complex number to
def visualize_de_moivre(r, theta_deg, n):
    theta_rad = np.deg2rad(theta_deg)  # Convert angle from degrees to radians
    colors = ['green', 'orange', 'red', 'purple', 'blue', 'cyan']  # Cycle colors for different powers

    # Set up plot
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_title("De Moivre’s Theorem Visualization: zⁿ = [r cis(θ)]ⁿ", fontsize=13)
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)
    ax.set_aspect('equal')  # Keep scale of x and y same (important for Argand plane)

    # Loop through powers from 1 to n
    for k in range(1, n + 1):
        # Compute z^k using De Moivre's formula: z^k = r^k * cis(kθ)
        z_k = r ** k * (np.cos(k * theta_rad) + 1j * np.sin(k * theta_rad))

        # Draw line from origin to z^k on complex plane
        ax.plot([0, z_k.real], [0, z_k.imag],
                color=colors[k % len(colors)],    # Cycle through color list
                linestyle='-',
                linewidth=2,
                marker='o',
                label=f'z^{k} = {z_k.real:.2f} + {z_k.imag:.2f}i')
        
        # Annotate the power on the plot
        ax.text(z_k.real, z_k.imag, f' z^{k}', fontsize=10, ha='left', va='bottom')

        # Optional: Draw dashed arc to show angle visually
        arc_theta = np.linspace(0, k * theta_rad, 100)
        arc_r = r ** k
        arc_x = arc_r * np.cos(arc_theta)
        arc_y = arc_r * np.sin(arc_theta)
        ax.plot(arc_x, arc_y, linestyle='dashed', color='gray', alpha=0.3)

    # Set axis limits dynamically based on maximum radius
    lim = r ** n + 2  # Padding to prevent clipping
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    plt.legend(loc='upper left', fontsize=9)

    # Save plot to memory (not to disk) so it can be embedded in HTML
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')         # Save plot to memory as PNG
    buf.seek(0)                            # Rewind buffer to the beginning
    plot_data = base64.b64encode(buf.read()).decode('utf8')  # Convert to base64 string
    buf.close()
    plt.close()

    # Final computed result z^n
    z_n = r ** n * (np.cos(n * theta_rad) + 1j * np.sin(n * theta_rad))
    result = f"{z_n.real:.2f} + {z_n.imag:.2f}i"  # Convert to readable form

    # Explanation for educational display on webpage
    explanation = f"""
        <p><strong>Magnitude (r):</strong> You entered <strong>{r}</strong>. This defines the distance from the origin. When raised to the power {n}, it becomes rⁿ = {r ** n:.2f}, increasing the vector's length accordingly.</p>
        <p><strong>Angle (θ):</strong> You entered <strong>{theta_deg}°</strong>. This is the initial direction of the complex number. When raised to the power {n}, it becomes nθ = {n * theta_deg}°, rotating the point counterclockwise.</p>
        <p><strong>Power (n):</strong> Raising the number to the power <strong>{n}</strong> multiplies the magnitude and rotates the angle by that factor. Each successive power shows this geometric transformation.</p>
        <p>The final result is <strong>zⁿ = {result}</strong>, plotted in red in the graph.</p>
    """

    # Return image, result string, and HTML explanation
    return plot_data, result, explanation
