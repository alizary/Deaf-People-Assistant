import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import threading
import time
import cv2
import speech_recognition as sr
from moviepy.editor import VideoFileClip, concatenate_videoclips

# List of English words for digits
dg = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']

last_video_path = None  # Global variable to store the last played video path
def play_video(video_path):
    global last_video_path
    last_video_path = video_path
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    def update_frame():
        ret, frame = cap.read()
        if not ret:
            cap.release()
            video_label.config(image='', text='Video playback finished.')
            replay_button.config(state=tk.NORMAL)  # Enable the replay button when the video finishes
            return
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)
        video_label.img_tk = img_tk
        video_label.config(image=img_tk)
        video_label.after(10, update_frame)
    
    replay_button.config(state=tk.DISABLED)  # Disable the replay button while the video is playing
    update_frame()

def replay_video():
    if last_video_path:
        play_video(last_video_path)

def timer():
    global timer_running, seconds, minutes
    while timer_running:
        time.sleep(1)
        seconds += 1
        if seconds == 60:
            seconds = 0
            minutes += 1
        timer_label.config(text=f"Recording time: {minutes}:{seconds:02d}s")

def process_speech():
    global timer_running

    update_terminal("* Speak something .....")

    # Path to the directory containing video files
    video_files_path = "assets"

    # List all video files in the directory
    video_file_list = [os.path.join(video_files_path, filename) for filename in os.listdir(video_files_path) if filename.endswith('.mp4')]

    # Initialize an empty list to store recognized words that match video filenames
    recognized_words = []

    # Initialize a SpeechRecognition recognizer instance
    recognizer = sr.Recognizer()

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        audio_text = recognizer.listen(source)

    update_terminal("* Recording completed.")

    try:
        # Use Google's speech recognition to convert audio to text
        recognized_text = recognizer.recognize_google(audio_text)
        update_terminal(f":> Recognized text:[ {recognized_text} ]")

        # Split recognized text into individual words
        word_list = recognized_text.split()

        # Process each word in the recognized text
        for word in word_list:
            if word.isdigit():
                recognized_words.extend(list(word))
            elif word.capitalize() in dg:
                recognized_words.append(str(dg.index(word.capitalize())))
            else:
                recognized_words.append(word.capitalize())

        # Filter recognized words that match video filenames
        recognized_videos = [word for word in recognized_words if word in [os.path.splitext(os.path.basename(filename))[0] for filename in video_file_list]]

        if recognized_videos:
            # Load matched video clips into memory
            loaded_video_list = [VideoFileClip(os.path.join(video_files_path, video_name + '.mp4')) for video_name in recognized_videos]

            # Concatenate loaded video clips into a single video
            final_clip = concatenate_videoclips(loaded_video_list)

            # Define the name for the merged video file
            merged_video_name = "merged.mp4"

            # Write the merged video to a file
            final_clip.write_videofile(merged_video_name)

            # Play the merged video
            play_video(merged_video_name)
        else:
            messagebox.showinfo("No Match", "No matching video files found.")

    except sr.UnknownValueError:
        update_terminal("Sorry, speech recognition could not understand audio.")
    except sr.RequestError as e:
        update_terminal(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        update_terminal(f"An error occurred: {e}")

# Create the GUI
root = tk.Tk()
root.title("Speech Recognition Video Player")

# Set the GUI window to full screen
root.attributes('-fullscreen', True)

# Load the background image
background_image = Image.open("003.png")  # Replace with the path to your image
background_photo = ImageTk.PhotoImage(background_image)

# Function to resize the background image to fit the window
def resize_image(event):
    background_label.config(image=background_photo)
    background_label.image = background_photo

# Set the background image
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1.01)  # Make the image cover the whole window
root.bind('<Configure>', resize_image)

# Set the GUI background color
# Create a frame to hold the button with padding and set its background to be transparent
button_frame = ttk.Frame(root, padding="10 10 10 10")
button_frame.place(relx=0.5, rely=0.92, anchor='center')  # Center the frame

# Create a text widget to display messages
terminal_output = tk.Text(root, width=40, height=6, font=("Helvetica", 12), bg="#F0F0F0", bd=15)
terminal_output.place(relx=0.04, rely=0.05)

# Function to update the text widget with messages
def update_terminal(message):
    terminal_output.insert(tk.END, message + "\n")
    terminal_output.see(tk.END)  # Scroll to the bottom to show the latest message

# Timer variables
seconds = 0
minutes = 0
timer_running = False
recording = False

def start_or_stop_record():
    global recording, timer_running, seconds, minutes
    if recording:
        timer_running = False
        start_button.config(text="Start Record")
        recording = False
    else:
        seconds = 0
        minutes = 0
        timer_label.config(text="Recording time: 0:00s")
        timer_running = True
        threading.Thread(target=timer).start()
        threading.Thread(target=process_speech).start()
        start_button.config(text="Stop Record")
        recording = True

# Function to close the GUI
def close_gui(event=None):
    global timer_running
    timer_running = False
    root.quit()

# Bind 'q' key to close the GUI
root.bind('q', close_gui)

# Apply style
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14, "bold"), padding=7, background="white")
style.configure("TLabel", font=("Helvetica", 14, "bold"))

# Create a label to display the timer
timer_label = ttk.Label(button_frame, text="Recording time: 0:00s", style="TLabel")
timer_label.pack(padx=100,pady=5)

# Create a button to start/stop recording
start_button = ttk.Button(button_frame, text="Start Record", style="TButton", command=start_or_stop_record)
start_button.pack(pady=0, fill=tk.X)

# Create a button to replay the last video
replay_button = ttk.Button(button_frame, text="Replay the video", style="TButton", command=replay_video, state=tk.DISABLED)
replay_button.pack(pady=0, fill=tk.X)

# Change button color
style.map("TButton",
          background=[('active', '#87CEFA'), ('!active', '#FFFFFF')],
          foreground=[('active', '#000000'), ('!active', '#000000')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

# Create a label to display the video
video_label = tk.Label(root, borderwidth=5, relief="solid", highlightthickness=2, highlightbackground="black")
video_label.place(relx=0.5, rely=0.5, anchor='center', width=630, height=600)

# Run the GUI event loop
root.mainloop()