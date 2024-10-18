import sqlite3
import tkinter as tk
from tkinter import messagebox
import pandas as pd  # Import pandas

# Create database and users table
conn = sqlite3.connect('Users_database.db')
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
