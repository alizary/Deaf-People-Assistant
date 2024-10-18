import tkinter as tk
from tkinter import ttk, messagebox
import subprocess


def start_hand_detect():
    try:
        subprocess.Popen(["python", "signdetect.py"])
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while starting hand detection: {e}")

def start_speech_recognition():
    try:
        subprocess.Popen(["python", "speechrecognition.py"])
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while starting speech recognition: {e}")

def show_script_runner():
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Python Script Runner")

    # Create a frame to hold the buttons without padding and border
    button_frame = ttk.Frame(root, padding=0)
    button_frame.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)

    # Create a style for the buttons
    style = ttk.Style()
    
    # Configure the style for the normal state
    style.configure("Bold.TButton", foreground="black", background="#355070", font=("Helvetica", 12, "bold"))

    # Configure the style for the active state (when mouse hovers over)
    style.map("Bold.TButton",
              foreground=[("active", "black")],
              underline=[("active", True)])

    # Create a button to start hand detection
    hand_detect_button = ttk.Button(button_frame, text="Start Hand Detection", command=start_hand_detect)
    hand_detect_button.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    # Create a button to start speech recognition
    speech_recognition_button = ttk.Button(button_frame, text="Start Speech Recognition", command=start_speech_recognition)
    speech_recognition_button.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

    # Configure the grid to have the buttons fill the space evenly
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    button_frame.rowconfigure(0, weight=1)
    

# Create the GUI
root = tk.Tk()
root.title("Python Script Runner")
show_script_runner()  # Switch to the script runner GUI
root.geometry("600x300") # Create main window

# Create a function to close the GUI
def close_gui(event=None):
    root.quit()

# Bind 'q' key to close the GUI
root.bind('q', close_gui)



# Run the GUI event loop
root.mainloop()
