import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import customtkinter as ctk

# Initialize customtkinter window
ctk.set_appearance_mode("dark")  # Optional: Set appearance mode to dark or light
root = ctk.CTk()  # Create the main window
root.geometry("700x500")  # Set window size

# Create a matplotlib figure
fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

# Embed the plot into the customtkinter window
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea
canvas.draw()
canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)  # Pack it into the window

# Add a navigation toolbar for panning, zooming, etc.
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()  # Update toolbar to sync with current figure
toolbar.pack(side=ctk.TOP, fill=ctk.X)  # Position toolbar at the top

# Optional: Add other customtkinter widgets
label = ctk.CTkLabel(root, text="Interactive Matplotlib Plot in customtkinter")
label.pack(pady=10)

# Run the customtkinter main loop
root.mainloop()
