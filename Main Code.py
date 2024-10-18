import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd  # Import pandas
import subprocess


# Create database and users table
conn = sqlite3.connect('Users_database1.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# Uncomment the following lines if you want to see the users in the database when the script runs
df = pd.read_sql_query('SELECT * FROM users', conn)
print(df)


def signup():
    username = username_entry.get()
    password = password_entry.get()
    
    if username == "" or password == "":
        messagebox.showerror("Error", "Please fill in all fields.")
    else:
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Signup successful!")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose another one.")

def login():
    username = username_entry.get()
    password = password_entry.get()
    
    if username == "" or password == "":
        messagebox.showerror("Error", "Please fill in all fields.")
    else:
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            open_script_runner()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

def delete_user(event=None):
    username = username_entry.get()
    
    if username == "":
        messagebox.showerror("Error", "Please enter a username to delete.")
    else:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
            messagebox.showinfo("Success", f"User '{username}' deleted successfully!")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"User '{username}' not found.")

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

def open_script_runner():
    script_root = tk.Tk()
    script_root.title("Python Script Runner")
    script_root.geometry("600x300")

    # Create a frame to hold the buttons without padding and border
    button_frame = ttk.Frame(script_root, padding=0)
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

    def close_gui(event=None):
        script_root.quit()

    # Bind 'q' key to close the GUI
    script_root.bind('q', close_gui)

    script_root.mainloop()

def close_app(event=None):
    root.quit()

# Create main window
root = tk.Tk()
root.title("Unique Login & Signup")
root.geometry("600x300")

# Bind 'q' key to close the GUI
root.bind('<q>', close_app)

# Create a frame for the signature group name and group members
signature_frame = tk.Frame(root, bg="#391970", pady=20)
signature_frame.pack(side="top", fill="x")

signature_label = tk.Label(signature_frame, text="CodeCrafters Team", font=("Helvetica", 16, "bold"), fg="#E0FFFF", bg="Indigo")
signature_label.pack()

members_label = tk.Label(signature_frame, text="| Abdullah : Ali : Ayat : Rehab : Fatma : Mazen : Mohamed |", font=("Helvetica", 10), fg="#F5FFFA", bg="Indigo")
members_label.pack()

# Create a frame for the login and signup section
login_frame = tk.Frame(root, padx=20, pady=20)
login_frame.pack()

# Create labels for username and password
username_label = tk.Label(login_frame, text="Username:", font=("Helvetica", 14, "bold"), fg="Indigo", bg="#F5FFFA")
username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
password_label = tk.Label(login_frame, text="Password:", font=("Helvetica", 14, "bold"), fg="Indigo", bg="#F5FFFA")
password_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

# Create entry fields for username and password
username_entry = tk.Entry(login_frame, width=40, font=("Helvetica", 12))
username_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=2)
password_entry = tk.Entry(login_frame, width=40, show="*", font=("Helvetica", 12))
password_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2)

# Bind the delete function to the Delete key
username_entry.bind('<Delete>', delete_user)

# Create buttons for signup and login
signup_button = tk.Button(login_frame, text="Signup", font=("Helvetica", 12, "bold"), bg="#2ecc71", fg="white", width=15, command=signup)
signup_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

login_button = tk.Button(login_frame, text="Login", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white", width=15, command=login)
login_button.grid(row=2, column=2, padx=10, pady=10, sticky="e")

root.mainloop()
# Close the database connection
conn.close()
