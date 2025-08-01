import math
import cmath
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

def create_complex_plot(a, b):
    z = complex(a, b)
    modulus = abs(z)

    fig, ax = plt.subplots()
    ax.set_title(f'Vector Representation of z = {a} + {b}i')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.grid(True, linestyle='--', linewidth=0.5)

    # Plot vector z = a + bi
    ax.plot([0, a], [0, b], color='blue', linewidth=2, label='z')
    ax.scatter([a], [b], color='blue')
    ax.text(a, b, f'z = {a:.1f} + {b:.1f}i', fontsize=9, ha='left', va='bottom', color='blue')

    # Optional: Right triangle legs (same as before, purely for clarity)
    ax.plot([0, a], [0, 0], color='green', linestyle='--', label='Real Part')
    ax.plot([a, a], [0, b], color='purple', linestyle='--', label='Imaginary Part')

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