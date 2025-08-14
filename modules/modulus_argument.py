import math
import cmath
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from matplotlib.patches import Arc  # <-- Add this import

def create_complex_plot(a, b):
    z = complex(a, b)
    modulus = abs(z)
    argument_rad = cmath.phase(z)
    argument_deg = math.degrees(argument_rad)

    fig, ax = plt.subplots()
    ax.set_title(f'Vector Representation of z = {a} + {b}i')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.grid(True, linestyle='--', linewidth=0.5)

    # Plot vector z = a + bi
    ax.plot([0, a], [0, b], color='blue', linewidth=2, label='z')
    ax.scatter([a], [b], color='blue')
    ax.text(a, b+0.1, f'z = {a:.1f} + {b:.1f}i', fontsize=9, ha='left', va='bottom', color='blue')

    # Right triangle legs
    ax.plot([0, a], [0, 0], color='green', linestyle='--', label='Real Part')
    ax.plot([a, a], [0, b], color='purple', linestyle='--', label='Imaginary Part')

    # Annotate modulus (length) parallel and above the vector, inclined at the same angle
    label_fraction = 0.5  # midpoint of the line
    offset = 0.25         # distance above the line
    label_x = label_fraction * a
    label_y = label_fraction * b
    # Perpendicular direction (always above the vector)
    perp_dx = -np.sin(argument_rad)
    perp_dy = np.cos(argument_rad)
    label_x += offset * perp_dx
    label_y += offset * perp_dy
    ax.text(label_x, label_y, f'|z| = {modulus:.2f}', color='blue', fontsize=11,
            ha='center', va='center', rotation=argument_deg,
            rotation_mode='anchor',
            transform_rotates_text=True)

    # Annotate argument (angle) as an arc
    arc_radius = modulus * 0.3
    arc = Arc((0, 0), arc_radius, arc_radius, angle=0, theta1=0, theta2=argument_deg, color='crimson', lw=2)  # <-- Use Arc from patches
    ax.add_patch(arc)
    # Place angle label near arc
    ax.text(arc_radius*0.8*np.cos(argument_rad/2), arc_radius*0.8*np.sin(argument_rad/2),
            f'θ = {argument_deg:.2f}°', color='crimson', fontsize=11, ha='left', va='bottom')

    # Dynamic axes range
    x_values = [0, a]
    y_values = [0, b]
    x_margin = max(1, 0.2 * (max(map(abs, x_values)) + 1))
    y_margin = max(1, 0.2 * (max(map(abs, y_values)) + 1))
    ax.set_xlim(min(x_values) - x_margin, max(x_values) + x_margin)
    ax.set_ylim(min(y_values) - y_margin, max(y_values) + y_margin)

    ax.set_xlabel('Real')
    ax.set_ylabel('Imaginary')
    ax.legend(loc='upper left', fontsize=8)

    # Convert to base64 image
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return image_base64

def compute_mod_arg(a, b):
    z = complex(a, b)
    modulus = abs(z)
    argument = math.degrees(cmath.phase(z))
    return modulus,argument