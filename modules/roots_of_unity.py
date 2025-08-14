import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.figure import Figure
import io, base64

def compute_roots_of_unity(n):
    """Return the n complex n-th roots of unity."""
    return [np.exp(2j * np.pi * k / n) for k in range(n)]

def get_plot_image(n):
    roots = compute_roots_of_unity(n)

    fig = Figure(figsize=(5.5, 5.5))
    ax = fig.subplots()
    ax.set_aspect('equal')
    ax.set_title(f"{n}-th Roots of Unity", fontsize=14, fontweight="bold")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")
    ax.grid(True, linestyle="--", alpha=0.5)

    # Draw unit circle
    circle = patches.Circle((0, 0), 1, fill=False, linestyle='--', color='gray', alpha=0.7)
    ax.add_patch(circle)

    # Axes lines
    ax.axhline(0, color="gray", linestyle=":")
    ax.axvline(0, color="gray", linestyle=":")

    # Polygon perimeter
    polygon_points = [(z.real, z.imag) for z in roots] + [(roots[0].real, roots[0].imag)]
    ax.plot([p[0] for p in polygon_points], [p[1] for p in polygon_points],
            color="blue", linewidth=1, alpha=0.6)

    # Colors for points
    colors = plt.cm.tab10(np.linspace(0, 1, n))

    # Points & labels
    for i, z in enumerate(roots):
        ax.plot(z.real, z.imag, 'o', color=colors[i], markersize=8)
        ax.text(z.real * 1.15, z.imag * 1.15,
                f"{i}\n({z.real:.2f}, {z.imag:.2f})",
                fontsize=8, ha='center', color=colors[i])

    # Red arc for angle and radius from center
    if n > 1:
        arc_angle = 360 / n
        arc = patches.Arc((0, 0), 0.5, 0.5, angle=0,
                          theta1=0, theta2=arc_angle,
                          color='red', linewidth=1.2)
        ax.add_patch(arc)

        # Radius to first vertex after 0°
        ax.plot([0, roots[1].real], [0, roots[1].imag],
                color='red', linewidth=1.2)

        # Midpoint label for angle
        mid_x = (roots[0].real + roots[1].real) / 2
        mid_y = (roots[0].imag + roots[1].imag) / 2
        ax.text(mid_x * 0.7, mid_y * 0.7, f"{arc_angle:.1f}°",
                color="red", fontsize=8, fontweight="bold", ha='center')

    # Medians for triangle case
    if n == 3:
        for z in roots:
            ax.plot([z.real, 0], [z.imag, 0], linestyle="--", color="purple", alpha=0.6)

    # Save to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # Formula & root set string
    formula = f"z^n = 1 ⇒ zₖ = e^(2πik/{n}) = cos(2πk/{n}) + i·sin(2πk/{n})\n"
    roots_str = "{" + ", ".join([f"{z.real:.2f}{'+' if z.imag >= 0 else ''}{z.imag:.2f}i" for z in roots]) + "}"

    return img_base64, formula, roots_str
