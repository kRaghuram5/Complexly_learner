import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
import base64

# Compute the n-th roots of unity (complex numbers on the unit circle)
def compute_roots_of_unity(n):
    return [np.exp(2j * np.pi * k / n) for k in range(n)]

# Generate and return a base64 image of the plot of n-th roots of unity
def get_plot_image(n):
    roots = compute_roots_of_unity(n)  # Get all n complex roots of unity

    fig = Figure(figsize=(5, 5))       # Create a new matplotlib figure
    ax = fig.subplots()                # Add subplot (single axis)
    ax.set_aspect('equal')            # Ensure equal scaling on x and y axes
    ax.set_title(f"{n}-th Roots of Unity", fontsize=14)
    ax.set_xlim(-1.5, 1.5)            # Set x-axis limits
    ax.set_ylim(-1.5, 1.5)            # Set y-axis limits
    ax.grid(True)                     # Show grid

    # Draw a light gray unit circle centered at origin
    circle = plt.Circle((0, 0), 1, color='lightgray', fill=False, linestyle='--')
    ax.add_artist(circle)

    # Plot each root as a blue dot and label with its index
    for i, z in enumerate(roots):
        ax.plot(z.real, z.imag, 'o', color='blue')  # Plot the root
        ax.text(z.real * 1.1, z.imag * 1.1, f"{i}", fontsize=9, color='blue')  # Label the root

    # Convert the plot to base64 image for embedding in HTML
    buf = io.BytesIO()
    fig.savefig(buf, format='png')     # Save the plot as PNG to buffer
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')  # Encode image to base64
    return img_base64
