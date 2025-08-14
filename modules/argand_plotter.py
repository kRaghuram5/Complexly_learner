# Import necessary libraries
import matplotlib.pyplot as plt        # For plotting the Argand diagram
import numpy as np                    # For generating arcs (argument angle)
import math                           # For modulus and argument calculations
import io                             # To handle image buffer (in-memory file)
import base64                         # To encode the plot image for embedding in HTML

# Function to generate Argand diagram plot and return it as a base64 image
def generate_argand_plot(a, b, show_conj, show_modulus, show_arg):
    try:
        # Convert input strings to floats (real and imaginary parts)
        a, b = float(a), float(b)
        z = complex(a, b)             # Original complex number
        z_conj = complex(a, -b)       # Conjugate of the complex number
        modulus = abs(z)              # Magnitude of complex number
        argument_rad = math.atan2(b, a)           # Argument in radians
        argument_deg = math.degrees(argument_rad) # Argument in degrees

        # Create plot
        fig, ax = plt.subplots()
        ax.set_title('Argand Plane (Matplotlib)')  # Title of the plot
        ax.axhline(0, color='gray', linewidth=0.5) # X-axis line
        ax.axvline(0, color='gray', linewidth=0.5) # Y-axis line
        ax.grid(True, linestyle='--', linewidth=0.5)

        # Plot the complex number z
        ax.plot([0, a], [0, b], color='blue', linewidth=2, label='z')
        ax.scatter([a], [b], color='blue')  # Point marking z
        ax.text(a, b, f'z = {a:.1f} + {b:.1f}i', fontsize=9, ha='left', va='bottom', color='blue')

        # Optional: Show conjugate z̅ if selected
        if show_conj:
            ax.plot([0, a], [0, -b], color='red', linewidth=2, linestyle='dotted', label='z̅ (Conjugate)')
            ax.scatter([a], [-b], color='red')
            ax.text(a, -b, f'z̅ = {a:.1f} - {b:.1f}i', fontsize=9, ha='left', va='top', color='red')

        # Optional: Show modulus and components (real & imaginary projections)
        if show_modulus:
            ax.plot([0, a], [0, 0], color='green', linestyle='--', label='Real Part')         # Real part line
            ax.plot([a, a], [0, b], color='purple', linestyle='--', label='Imaginary Part')   # Imaginary part line

        # Optional: Show argument (angle between positive x-axis and z)
        if show_arg and (a != 0 or b != 0):
            arc_theta = np.linspace(0, argument_rad, 100)   # Create arc from 0 to argument
            arc_radius = 0.2*modulus # Smaller fixed fraction so it fits inside
            arc_x = arc_radius * np.cos(arc_theta)  # X coordinates
            arc_y = arc_radius * np.sin(arc_theta)  # Y coordinates
            ax.plot(arc_x, arc_y, color='orange', linewidth=2, label='Argument ∠')


        # Add legend to distinguish components
        ax.legend(loc='upper left', fontsize=8)

        # Dynamically calculate limits to keep plot centered and readable
        x_values = [0, a]
        y_values = [0, b, -b] if show_conj else [0, b]
        x_margin = max(1, 0.2 * (max(map(abs, x_values)) + 1))
        y_margin = max(1, 0.2 * (max(map(abs, y_values)) + 1))
        ax.set_xlim(min(x_values) - x_margin, max(x_values) + x_margin)
        ax.set_ylim(min(y_values) - y_margin, max(y_values) + y_margin)

        # Save plot to memory buffer as PNG (not as a file)
        buf = io.BytesIO()
        plt.tight_layout()  # Adjust spacing
        plt.savefig(buf, format='png')  # Save as PNG in buffer
        buf.seek(0)  # Reset buffer pointer to start

        # Convert image bytes to base64 string so it can be embedded in HTML
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()  # Close memory buffer
        plt.close()  # Close plot to avoid memory leaks

        # Return image along with numeric data (modulus, argument)
        return image_base64, {
            'real': a,
            'imag': b,
            'modulus': round(modulus, 2),
            'argument': round(argument_deg, 2)
        }

    # If any error occurs (e.g. input type issues), catch and return error message
    except Exception as e:
        return None, {'error': f"Invalid input. ({e})"}
