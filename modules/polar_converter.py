# Import necessary libraries
import math                   # For mathematical functions like sqrt, cos, sin, etc.
import cmath                  # For complex number operations like phase()
import io                     # For creating in-memory image buffers
import base64                 # To encode images as base64 for embedding in HTML
import matplotlib.pyplot as plt  # For plotting vector representation

# Function to create a vector plot for a complex number
def create_complex_plot(x, y, title):
    # Create a new plot figure and axis
    fig, ax = plt.subplots()

    # Draw the complex number vector from origin to point (x, y)
    ax.quiver(0, 0, x, y, angles='xy', scale_units='xy', scale=1, color='blue')

    # Set the plot limits for x and y axes
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)

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

    # Calculate modulus (|z|) and argument (θ) of the complex number
    r = round(math.hypot(x, y), 2)  # Equivalent to sqrt(x^2 + y^2)
    angle_deg = round(math.degrees(math.atan2(y, x)), 2)  # Angle in degrees

    # Annotate the modulus and angle on the vector
    ax.annotate(f"|z| = {r}", xy=(x/2, y/2), fontsize=10, color='green')
    ax.annotate(f"θ = {angle_deg}°", xy=(x/2, y/2 - 0.5), fontsize=10, color='purple')

    # Save the plot to a bytes buffer in PNG format
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the image buffer into base64 string to embed in HTML
    plot_data = base64.b64encode(img.read()).decode()

    # Close the plot to avoid memory leaks
    plt.close()

    # Return image as a base64 string that can be directly used in HTML
    return f"data:image/png;base64,{plot_data}"

# Function to handle both Cartesian → Polar and Polar → Cartesian conversions
def polar_converter_handler(mode, input1, input2):
    # Convert user input strings to floats
    input1 = float(input1)
    input2 = float(input2)
    
    # Case 1: Cartesian to Polar
    if mode == 'cartesian':
        z = complex(input1, input2)                  # Represent as complex number a + bi
        r = abs(z)                                   # Modulus (distance from origin)
        theta = math.degrees(cmath.phase(z))         # Argument (angle with positive real axis)
        result = f"Polar Form: (r = {round(r, 2)}, θ = {round(theta, 2)}°)"
        explanation = f"This means the complex number lies {round(r,2)} units from origin and at an angle of {round(theta, 2)}° from the positive real axis."
        plot = create_complex_plot(input1, input2, "Cartesian to Polar")

    # Case 2: Polar to Cartesian
    elif mode == 'polar':
        r = input1
        theta = math.radians(input2)                 # Convert degrees to radians
        a = r * math.cos(theta)                      # x = r cos(θ)
        b = r * math.sin(theta)                      # y = r sin(θ)
        result = f"Cartesian Form: z = {round(a,2)} + {round(b,2)}i"
        explanation = f"This means the point lies at distance {r} from origin at angle {input2}°. Projecting onto real and imaginary axes gives coordinates ({round(a,2)}, {round(b,2)})."
        plot = create_complex_plot(a, b, "Polar to Cartesian")

    # Case 3: Invalid mode
    else:
        result = "<strong>Error:</strong> Invalid mode selected."
        plot = ""
        explanation = ""
    
    # Return the conversion result, vector plot (base64), and explanation text
    return result, plot, explanation
