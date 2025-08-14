# Force matplotlib to use a backend suitable for Flask / headless environments
import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import io
import base64

def visualize_de_moivre(r, theta_deg, n):
    theta_rad = np.deg2rad(theta_deg)

    # Colors for steps (cyclic if n is large)
    colors = plt.cm.tab10(np.linspace(0, 1, min(n, 10)))

    # Create a single Argand diagram
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_title(f"De Moivre's Theorem: Raising to Power {n}", fontsize=14, pad=15)
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal')

    # Plot each step from z^1 to z^n
    max_radius = 0
    for k in range(1, n + 1):
        # De Moivre's formula
        z_k = r**k * (np.cos(k * theta_rad) + 1j * np.sin(k * theta_rad))

        # Vector from origin to z^k
        ax.plot([0, z_k.real], [0, z_k.imag],
                color=colors[(k - 1) % len(colors)],
                linewidth=2,
                marker='o',
                label=f"$z^{k}$ = {z_k.real:.2f} + {z_k.imag:.2f}i")

        # Dashed arc showing rotation
        arc_theta = np.linspace(0, k * theta_rad, 200)
        arc_x = r**k * np.cos(arc_theta)
        arc_y = r**k * np.sin(arc_theta)
        ax.plot(arc_x, arc_y, linestyle='--',
                color=colors[(k - 1) % len(colors)], alpha=0.4)

        max_radius = max(max_radius, abs(r**k))

    # Adjust limits dynamically
    lim = max_radius * 1.2 if max_radius > 0 else 1.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.legend(fontsize=8, loc='upper left')

    # Save image to base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=120)
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf8')
    buf.close()
    plt.close()

    # Final result z^n
    z_n = r**n * (np.cos(n * theta_rad) + 1j * np.sin(n * theta_rad))
    result = f"{z_n.real:.2f} + {z_n.imag:.2f}i"

    # Explanation
    explanation = f"""
    <h3>De Moivre's Theorem</h3>
    <p>Starting from $z = r(\\cosθ + i\\sinθ)$ with r = {r:.2f} and θ = {theta_deg:.2f}°:</p>
    <p>We apply De Moivre's Theorem: $z^n = r^n(\\cos(nθ) + i\\sin(nθ))$</p>
    <ul>
        <li><strong>Magnitude scaling:</strong> r → r<sup>n</sup> = {r**n:.2f}</li>
        <li><strong>Angle rotation:</strong> θ → nθ = {n*theta_deg:.2f}°</li>
    </ul>
    <p>The plot shows each intermediate step from $z^1$ up to $z^{n}$, 
    illustrating how the vector grows and rotates.</p>
    <p><strong>Final result:</strong> {result}</p>
    """

    return plot_data, result, explanation
