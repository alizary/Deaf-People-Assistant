import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk

# Initialize hand detector
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
data_folder = "Data"

# Function to create a folder
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    else:
        print("Folder already exists.")

# Function to create a new folder via GUI input
def create_new_folder():
    folder_name = simpledialog.askstring("Input", "Enter folder name:", parent=root)
    if folder_name:
        new_folder_path = os.path.join(data_folder, folder_name)
        create_folder(new_folder_path)
        return new_folder_path
    return ""

# Create the initial Data folder
create_folder(data_folder)

# Initialize current folder
current_folder = ""

# Initialize the GUI
root = tk.Tk()
root.title("Data Collect")
root.geometry("400x200")

# Apply style
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("TLabel", font=("Helvetica", 12))

# Frame for buttons
frame = ttk.Frame(root, padding="10 10 10 10")
frame.pack(fill=tk.BOTH, expand=True)

def add_new_folder():
    global current_folder
    current_folder = create_new_folder()
    if current_folder:
        messagebox.showinfo("Information", f"New folder created: {current_folder}")

# Button to add a new folder
add_folder_button = ttk.Button(frame, text="Add a New Word", command=add_new_folder)
add_folder_button.pack(pady=20, fill=tk.X)

# Function to start the camera and data collection
def start_data_collection():
    if not current_folder:
        messagebox.showinfo("Information", "Please add a new folder first.")
        return
    
    cap = cv2.VideoCapture(0)
    counter = 0
    
    while True:
        success, img = cap.read()
        if not success:
            break
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
            imgCropShape = imgCrop.shape

            aspectRatio = h / w
            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                imgResizeShape = imgResize.shape
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                imgResizeShape = imgResize.shape
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            cv2.imshow("ImageCrop", imgCrop)
            cv2.imshow("ImageWhite", imgWhite)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord("s"):
            counter += 1
            image_path = f'{current_folder}/Image_{counter}_{time.time()}.jpg'
            cv2.imwrite(image_path, imgWhite)
            print(f'Saved: {image_path}')
            print(f'Total images saved: {counter}')
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    root.quit()  # Quit the GUI loop when 'q' is pressed

# Button to start data collection
start_button = ttk.Button(frame, text="Start Data Collection", command=start_data_collection)
start_button.pack(pady=20, fill=tk.X)

def on_closing():
    cv2.destroyAllWindows()
    root.quit()

# Bind the 'q' key to close the GUI
root.bind('<KeyPress-q>', lambda event: on_closing())

root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the GUI
root.mainloop()
