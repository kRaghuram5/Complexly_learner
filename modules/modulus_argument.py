import math
import cmath
import plotly.graph_objs as go

# Function to create a 2D plot of the complex number z = a + bi
def create_complex_plot(a, b):
    fig = go.Figure()

    # Add a vector from origin (0,0) to the point (a,b)
    fig.add_trace(go.Scatter(
        x=[0, a],  # Real axis: from 0 to a
        y=[0, b],  # Imaginary axis: from 0 to b
        mode='lines+markers+text',  # Show line, points, and label
        name="Complex Vector",
        text=[None, f"{a}+{b}i"],  # Only label the end point
        marker=dict(size=10),  # Marker size for points
        line=dict(width=4)  # Line thickness
    ))

    # Configure the layout of the plot
    fig.update_layout(
        title="Vector Representation of z = a + bi",  # Plot title
        xaxis=dict(title='Real', range=[-10, 10]),  # X-axis config
        yaxis=dict(title='Imaginary', range=[-10, 10]),  # Y-axis config
        width=500,
        height=500
    )

    # Return the plot as an embeddable HTML string
    return fig.to_html()

# Function to compute modulus and argument (angle in degrees) of z = a + bi
def compute_mod_arg(a, b):
    z = complex(a, b)  # Create complex number
    modulus = abs(z)  # Modulus = sqrt(a^2 + b^2)
    argument = math.degrees(cmath.phase(z))  # Argument in degrees
    return modulus, argument
