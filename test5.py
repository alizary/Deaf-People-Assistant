import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import tkinter as tk
from PIL import Image, ImageTk
import threading
from gtts import gTTS
import os
import playsound

cap = None
stop_threads = False
video_playback = None

def start_hand_detection():
    global cap, video_playback, stop_threads

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)  # Set width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)  # Set height
    detector = HandDetector(maxHands=1)
    classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
    offset = 30
    imgSize = 500
    labels = ["hi", "good", "ok", "no", "i love you", "sorry", "thank you", "yes", "you"]
    last_spoken_text = None

    # Create a label for displaying hand type (left or right)
    hand_type_label = tk.Label(root, text="", bg="white", fg="black", font=("Helvetica", 20),
                               borderwidth=4, relief="raised", highlightthickness=5, highlightbackground="blue")
    hand_type_label.place(relx=0.5, rely=0.79, anchor="center")

    # Create a label for displaying classified text (label)
    classified_text_label = tk.Label(root, text="", bg="white", fg="black", font=("Helvetica", 20),
                                     borderwidth=4, relief="raised", highlightthickness=5, highlightbackground="blue")
    classified_text_label.place(relx=0.5, rely=0.9, anchor="center")

    def update_frame():
        global stop_threads, last_spoken_text
        if stop_threads:
            return

        ret, frame = cap.read()
        if not ret:
            cap.release()
            video_playback.config(image='', text='Video playback finished.')
            return

        frame = cv2.flip(frame, 1)
        hands, img = detector.findHands(frame)

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            handType = hand['type']  # Detect the type of hand (Left or Right)
            handType = "Right" if handType == "Left" else "Left"  # Switch the detected hand type
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
            aspectRatio = h / w

            try:
                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                else:
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize

                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                recognized_text = f"{handType} Hand"  # Include hand type in the recognized text
                hand_type_label.config(text=f"{labels[index]}")    # Update hand type label
                classified_text_label.config(text=recognized_text)  # Update classified text label

                # Draw bounding box and label on the original frame
                cv2.rectangle(img, (x - offset, y - offset), (x + w + offset, y + h + offset), (0, 255, 0), 4)
                cv2.rectangle(img, (x - offset, y - offset - 40), (x + w + offset, y - offset), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, recognized_text, (x, y - offset - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                if recognized_text != last_spoken_text:
                    threading.Thread(target=speak_text, args=(recognized_text,)).start()
                    last_spoken_text = recognized_text
            except Exception as e:
                print(f"Error: {e}")
        else:
            # Hide the classified text label if no hands are detected
            classified_text_label.place_forget()

        img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
        video_playback.img_tk = img_tk
        video_playback.config(image=img_tk)
        video_playback.after(3, update_frame)

    def speak_text(text):
        tts = gTTS(text=text, lang='en')
        filename = "temp_audio.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)

    def on_key(event):
        if event.char == 'q':
            end_program()

    root.bind('<Key>', on_key)
    update_frame()

def end_hand_detection():
    global stop_threads, cap
    stop_threads = True
    if cap:
        cap.release()
        cap = None
    cv2.destroyAllWindows()
    video_playback.config(image='', text='Video playback finished.', fg='Black')  # Display message after stopping detection

def end_program():
    end_hand_detection()
    root.quit()

# Function to start hand detection when the button is clicked
def start_detection():
    global stop_threads
    stop_threads = False
    video_playback.config(image='', text='')  # Clear the 'Video playback finished' message
    threading.Thread(target=start_hand_detection).start()

# Function to end hand detection when the button is clicked
def end_detection():
    end_hand_detection()

# Create GUI
root = tk.Tk()
root.title("Hand Detection Program")

# Set window size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Make the window full screen
root.attributes("-fullscreen", True)
root.overrideredirect(True)  # Hide window edges

# Set background image
background_image = Image.open(r"H:/suggested-project/New_project/proj/004.png")
background_image = background_image.resize((screen_width, screen_height))
background_image = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create a frame for video playback
video_playback = tk.Label(root, borderwidth=5, relief="solid",highlightthickness=2, highlightbackground="White", bg='White', fg='white')
video_playback.place(relx=0.5, rely=0.35, anchor='center', width=700, height=550)

# Create a frame for buttons and place it above the bottom
button_frame = tk.Frame(root, bg="White")
button_frame.pack(side="bottom", pady=210)  # Add padding to move it up slightly

# Create buttons
start_button = tk.Button(button_frame, text="Start Hand Detection", command=start_detection, bg="#4CAF50", fg="white", font=("Helvetica", 14))
start_button.pack(side="left", padx=10, pady=10)

end_button = tk.Button(button_frame, text="End Hand Detection", command=end_detection, bg="#FF5733", fg="white", font=("Helvetica", 14))
end_button.pack(side="left", padx=10, pady=10)

# Run the GUI event loop
root.mainloop()

