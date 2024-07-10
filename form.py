import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import requests
import re
import os
from io import BytesIO

# Function to create gradient background
def create_gradient(canvas, color1, color2, width, height):
    for i in range(height):
        r = int(color1[1:3], 16) + i * (int(color2[1:3], 16) - int(color1[1:3], 16)) // height
        g = int(color1[3:5], 16) + i * (int(color2[3:5], 16) - int(color1[3:5], 16)) // height
        b = int(color1[5:7], 16) + i * (int(color2[5:7], 16) - int(color1[5:7], 16)) // height
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color)

# Function to open a file dialog to select an Excel file
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    entry_field.delete(0, tk.END)
    entry_field.insert(0, file_path)

# Function to validate the Excel file
def read_excel():
    file_path = entry_field.get()
    if file_path:
        try:
            if file_path.startswith('http://') or file_path.startswith('https://'):
                # Handling URL
                response = requests.get(file_path)
                if len(response.content) > 1_000_000:
                    messagebox.showerror("Error", "File size exceeds 1MB limit.")
                    return
                content = BytesIO(response.content)
                df = pd.read_excel(content)
            else:
                # Handling local file path
                if os.path.getsize(file_path) > 1_000_000:
                    messagebox.showerror("Error", "File size exceeds 1MB limit.")
                    return
                df = pd.read_excel(file_path)

            # Validate the dataframe and display if valid
            validate_and_display(df)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read Excel file: {e}")
    else:
        messagebox.showwarning("Input Error", "Please select an Excel file")

def validate_and_display(df):
    try:
        # Required fields
        required_fields = ['name', 'gender', 'phone number', 'date of birth']

        # Check if all required fields are present
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            messagebox.showerror("Error", f"Missing fields: {', '.join(missing_fields)}")
            return

        # Validate each row
        for _, row in df.iterrows():
            if str(row['gender']).lower() not in ['male', 'female']:
                messagebox.showerror("Error", "Invalid gender value. Must be 'male' or 'female'.")
                return

            if not re.match(r'^\+?\d[\d\s-]{7,}\d$', str(row['phone number'])):
                messagebox.showerror("Error", "Invalid phone number format.")
                return

            if not re.match(r'^\d{2}/\d{2}/\d{4}$', str(row['date of birth'])):
                messagebox.showerror("Error", "Invalid date of birth format. Must be 'day/month/year'.")
                return

        # Remove the original frame and contents
        entry_field.place_forget()
        browse_button.place_forget()
        submit_button.place_forget()

        # Change the background color of the main window
        root.configure(bg="white")

        # Create a new frame to display Excel data in table format
        new_frame = tk.Frame(root, bg="white", width=500, height=300)
        new_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Display headers in the first row
        for i, col in enumerate(df.columns):
            header_label = tk.Label(new_frame, text=col, font=("Helvetica", 14, "bold"), bg="white", fg="black", borderwidth=1, relief="solid")
            header_label.grid(row=0, column=i, padx=(0,1), pady=(0,1), sticky="nsew")

        # Display values in the second row
        for row_index in range(min(2, len(df))):  # Display at most 2 rows
            for i, col in enumerate(df.columns):
                value_label = tk.Label(new_frame, text=str(df[col][row_index]), font=("Helvetica", 14), bg="white", fg="black", borderwidth=1, relief="solid")
                value_label.grid(row=row_index + 1, column=i, padx=(0,1), pady=(0,1), sticky="nsew")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to validate Excel data: {e}")

# Create the main window
root = tk.Tk()
root.title("Excel File Reader")
root.geometry("800x600")
root.configure(bg="#f0f0f0")  # Set initial background color

# Create a canvas to draw the gradient
canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Function to draw rounded rectangle
def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius):
    canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, outline="", fill="white")
    canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, outline="", fill="white")
    canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, outline="", fill="white")
    canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, outline="", fill="white")
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, outline="", fill="white")
    canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, outline="", fill="white")

# Function to handle window resize and redraw canvas
def on_resize(event):
    canvas.delete("all")
    create_gradient(canvas, "#7f7fd5", "#86a8e7", event.width, event.height)

    # Recalculate frame coordinates
    global frame_x1, frame_y1, frame_x2, frame_y2
    frame_x1 = (event.width - frame_width) // 2
    frame_y1 = (event.height - frame_height) // 2
    frame_x2 = frame_x1 + frame_width
    frame_y2 = frame_y1 + frame_height

    # Redraw rounded rectangle
    draw_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius)

    # Reposition title label
    title_label.place(relx=0.5, rely=0.3, anchor="center")

# Bind the resize event to the root window
root.bind("<Configure>", on_resize)

# Calculate initial frame coordinates
frame_width = 500
frame_height = 300
frame_radius = 20

frame_x1 = (800 - frame_width) // 2
frame_y1 = (600 - frame_height) // 2
frame_x2 = frame_x1 + frame_width
frame_y2 = frame_y1 + frame_height

# Draw the initial rounded rectangle on the canvas
draw_rounded_rectangle(canvas, frame_x1, frame_y1, frame_x2, frame_y2, frame_radius)

# Create a label
title_label = tk.Label(root, text="Excel File Reader", font=("Helvetica", 24, "bold"), bg="white", fg="blue")
title_label.place(relx=0.5, rely=0.3, anchor="center")

# Placeholder functionality for the entry field
def set_placeholder(event):
    if entry_field.get() == "":
        entry_field.insert(0, "Add Excel file link")
        entry_field.config(fg="grey")

def clear_placeholder(event):
    if entry_field.get() == "Add Excel file link":
        entry_field.delete(0, tk.END)
        entry_field.config(fg="black")

# Create an entry field with padding and flat border
entry_field = tk.Entry(root, width=50, font=("Helvetica", 14), bg="white", fg="grey", bd=1, relief="flat",
                       highlightthickness=1, highlightbackground="grey", highlightcolor="grey", insertwidth=1)
entry_field.insert(0, "Add Excel file link")
entry_field.bind("<FocusIn>", clear_placeholder)
entry_field.bind("<FocusOut>", set_placeholder)
entry_field.place(relx=0.5, rely=0.4, anchor="center", relwidth=0.5, relheight=0.06)

# Custom button class with rounded corners
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.command = command
        self.radius = 20
        self.text = text
        self.create_rounded_rectangle(0, 0, 2 * self.radius, 2 * self.radius, self.radius, fill="#4CAF50", outline="")
        self.create_text(self.radius, self.radius, text=self.text, fill="white", font=("Helvetica", 14, "bold"))
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        self.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, **kwargs)
        self.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, **kwargs)
        self.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, **kwargs)
        self.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, **kwargs)
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)

    def on_click(self, event):
        self.command()

# Create the browse button inside the main window
browse_button = RoundedButton(root, text="Browse", command=open_file, width=120, height=40)
browse_button.place(relx=0.35, rely=0.5, anchor="center")

# Create the submit button inside the main window
submit_button = RoundedButton(root, text="Submit", command=read_excel, width=120, height=40)
submit_button.place(relx=0.65, rely=0.5, anchor="center")

# Start the main event loop
root.mainloop()
