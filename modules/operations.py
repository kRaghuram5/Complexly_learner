import matplotlib.pyplot as plt  # For plotting complex vectors
import io                        # For in-memory image buffer
import base64                    # For encoding image to base64 string

# Function to perform arithmetic operations on two complex numbers and visualize the result
def perform_complex_operation(a, b, c, d, operation):
    try:
        # Convert input values to float
        a, b, c, d = float(a), float(b), float(c), float(d)
        
        # Create complex numbers z1 = a + bi and z2 = c + di
        z1 = complex(a, b)
        z2 = complex(c, d)

        op_name = ''   # Operator symbol for display
        result = None  # Placeholder for operation result

        # Perform selected operation
        if operation == "add":
            result = z1 + z2
            op_name = "+"
        elif operation == "subtract":
            result = z1 - z2
            op_name = "-"
        elif operation == "multiply":
            result = z1 * z2
            op_name = "×"
        elif operation == "divide":
            if z2 == 0:
                return "Division by zero is undefined.", None  # Handle divide-by-zero error
            result = z1 / z2
            op_name = "÷"

        if result is not None:
            # Format the result string to show operation performed
            result_str = f"z₁ {op_name} z₂ = {result:.2f}"

            # Start a new matplotlib figure
            fig, ax = plt.subplots()
            ax.set_title('Complex Number Operation Result')  # Title of the plot
            ax.axhline(0, color='gray', linewidth=0.5)       # Draw real axis (x-axis)
            ax.axvline(0, color='gray', linewidth=0.5)       # Draw imaginary axis (y-axis)
            ax.grid(True, linestyle='--', linewidth=0.5)     # Add grid lines

            # Helper function to draw a vector from origin to a complex number
            def plot_vector(z, color, label):
                ax.plot([0, z.real], [0, z.imag], color=color, linewidth=2, label=label)
                ax.scatter([z.real], [z.imag], color=color)

            # Plot z1, z2 and result on the complex plane
            plot_vector(z1, 'blue', 'z₁')
            plot_vector(z2, 'green', 'z₂')
            plot_vector(result, 'red', 'Result')

            # Calculate plot boundaries based on all vector points
            all_x = [0, z1.real, z2.real, result.real]
            all_y = [0, z1.imag, z2.imag, result.imag]
            x_range = max(all_x) - min(all_x)
            y_range = max(all_y) - min(all_y)
            x_margin = 0.2 * x_range if x_range != 0 else 1
            y_margin = 0.2 * y_range if y_range != 0 else 1
            ax.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
            ax.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)
            ax.legend()  # Show labels

            # Save plot to memory buffer and encode to base64 for HTML embedding
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode("ascii")
            buf.close()
            plt.close(fig)  # Close the figure to free memory

            # Return formatted result and base64-encoded image
            return result_str, plot_url

    except:
        # Handle any unexpected errors like invalid inputs
        return "Invalid input.", None
