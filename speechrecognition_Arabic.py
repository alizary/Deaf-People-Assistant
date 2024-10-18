import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import threading
import time
import cv2
import speech_recognition as sr
from moviepy.editor import VideoFileClip, concatenate_videoclips

# قائمة الكلمات الإنجليزية للأرقام
dg = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']

# متغير لتخزين مسار الفيديو الأخير الذي تم تشغيله
last_video_path = None

# متغير لتخزين عدد الفيديوهات التي تم تشغيلها
video_count = 0

# إضافة متغير لتحديد ما إذا تم الضغط على زر إعادة التشغيل
replay_pressed = False

def play_video(video_path):
    global last_video_path, video_count, replay_pressed
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
    if not replay_pressed:
        video_count += 1  # Increment the video count only if replay button was not pressed
        update_video_count_label()  # Update the video count label
    replay_pressed = False  # Reset replay_pressed after playing the video

def replay_video():
    global replay_pressed
    replay_pressed = True  # Set replay_pressed to True when replay button is pressed
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
    global timer_running, video_count

    update_terminal("* Speak something .....")

    # مسار الدليل الذي يحتوي على ملفات الفيديو
    video_files_path = "assets"

    # قائمة بجميع ملفات الفيديو في الدليل
    video_file_list = [os.path.join(video_files_path, filename) for filename in os.listdir(video_files_path) if filename.endswith('.mp4')]

    # قائمة فارغة لتخزين الكلمات المعترف بها التي تتطابق مع أسماء ملفات الفيديو
    recognized_words = []

    # إنشاء مثيل لمكتبة التعرف على الكلام
    recognizer = sr.Recognizer()

    # استخدام الميكروفون كمصدر للصوت
    with sr.Microphone() as source:
        audio_text = recognizer.listen(source)

    update_terminal("* Recording completed.")

    try:
        # استخدام التعرف على الكلام من جوجل لتحويل الصوت إلى نص
        recognized_text = recognizer.recognize_google(audio_text)
        update_terminal(f":> Recognized text:[ {recognized_text} ]")

        # تقسيم النص المعترف به إلى كلمات فردية
        word_list = recognized_text.split()

        # معالجة كل كلمة في النص المعترف به
        for word in word_list:
            if word.isdigit():
                recognized_words.extend(list(word))
            elif word.capitalize() in dg:
                recognized_words.append(str(dg.index(word.capitalize())))
            else:
                recognized_words.append(word.capitalize())

        # تصفية الكلمات المعترف بها التي تتطابق مع أسماء ملفات الفيديو
        recognized_videos = [word for word in recognized_words if word in [os.path.splitext(os.path.basename(filename))[0] for filename in video_file_list]]

        if recognized_videos:
            # تحميل مقاطع الفيديو المطابقة إلى الذاكرة
            loaded_video_list = [VideoFileClip(os.path.join(video_files_path, video_name + '.mp4')) for video_name in recognized_videos]

            # دمج مقاطع الفيديو المحملة في فيديو واحد
            final_clip = concatenate_videoclips(loaded_video_list)

            # تحديد اسم ملف الفيديو المدمج
            merged_video_name = "merged.mp4"

            # كتابة الفيديو المدمج إلى ملف
            final_clip.write_videofile(merged_video_name)

            # تشغيل الفيديو المدمج
            play_video(merged_video_name)

        else:
            messagebox.showinfo("No Match", "No matching video files found.")

    except sr.UnknownValueError:
        update_terminal("Sorry, speech recognition could not understand audio.")
    except sr.RequestError as e:
        update_terminal(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        update_terminal(f"An error occurred: {e}")

# دالة لتحديث ملصق عدد الفيديوهات
def update_video_count_label():
    video_count_label.config(text=f"Videos Played: {video_count}")

# إنشاء واجهة المستخدم
root = tk.Tk()
root.title("Speech Recognition Video Player")

# ضبط نافذة التطبيق لتكون ملء الشاشة
root.attributes('-fullscreen', True)

# تحميل صورة الخلفية
background_image = Image.open("003.png")  # استبدل بالمسار الخاص بالصورة الخاصة بك
background_photo = ImageTk.PhotoImage(background_image)

# دالة لضبط حجم صورة الخلفية لتناسب النافذة
def resize_image(event):
    background_label.config(image=background_photo)
    background_label.image = background_photo

# تعيين صورة الخلفية
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1.01)  # جعل الصورة تغطي النافذة بالكامل
root.bind('<Configure>', resize_image)

# تعيين لون خلفية واجهة المستخدم
# إنشاء إطار يحتوي على الأزرار مع إضافة padding وضبط خلفيته ليكون شفاف
button_frame = ttk.Frame(root, padding="10 10 10 10")
button_frame.place(relx=0.5, rely=0.92, anchor='center')  # مركز الإطار

# إنشاء عنصر نصي لعرض الرسائل
terminal_output = tk.Text(root, width=40, height=6, font=("Helvetica", 12), bg="#F0F0F0", bd=15)
terminal_output.place(relx=0.04, rely=0.05)
# عرض عنصر النصي


# دالة لتحديث العنصر النصي بالرسائل
def update_terminal(message):
    terminal_output.insert(tk.END, message + "\n")
    terminal_output.see(tk.END)  # التمرير إلى الأسفل لعرض آخر رسالة

# متغيرات العداد الزمني
seconds = 0
minutes = 0
timer_running = False
recording = False

def start_or_stop_record():
    global recording, timer_running, seconds, minutes, is_new_audio
    if recording:
        timer_running = False
        start_button.config(text="Start Record")
        recording = False
        is_new_audio = False  # Set is_new_audio to False when stopping recording
    else:
        seconds = 0
        minutes = 0
        timer_label.config(text="Recording time: 0:00s")
        timer_running = True
        threading.Thread(target=timer).start()
        is_new_audio = True  # Set is_new_audio to True when starting recording
        threading.Thread(target=process_speech).start()
        start_button.config(text="Stop Record")
        recording = True

# دالة لإغلاق واجهة المستخدم
def close_gui(event=None):
    global timer_running
    timer_running = False
    root.quit()

# ربط المفتاح 'q' لإغلاق واجهة المستخدم
root.bind('q', close_gui)

# تطبيق الأسلوب
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14, "bold"), padding=7, background="white")
style.configure("TLabel", font=("Helvetica", 14, "bold"))

# إنشاء ملصق لعرض العداد الزمني
timer_label = ttk.Label(button_frame, text="Recording time: 0:00s", style="TLabel")
timer_label.pack(padx=100,pady=5)

# إنشاء زر لبدء/إيقاف التسجيل
start_button = ttk.Button(button_frame, text="Start Record", style="TButton", command=start_or_stop_record)
start_button.pack(pady=0, fill=tk.X)

# إنشاء زر لإعادة تشغيل الفيديو الأخير
replay_button = ttk.Button(button_frame, text="Replay the video", style="TButton", command=replay_video, state=tk.DISABLED)
replay_button.pack(pady=0, fill=tk.X)

# تغيير لون الزر
style.map("TButton",
          background=[('active', '#87CEFA'), ('!active', '#FFFFFF')],
          foreground=[('active', '#000000'), ('!active', '#000000')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

# إنشاء ملصق لعرض الفيديو
video_label = tk.Label(root, borderwidth=5, relief="solid", highlightthickness=2, highlightbackground="black")
video_label.place(relx=0.5, rely=0.5, anchor='center', width=630, height=600)

# إنشاء إطار لعرض عدد الفيديوهات
video_count_frame = tk.Frame(root, bg="#F0F0F0", bd=5)
video_count_frame.place(relx=0.17, rely=0.234, anchor='center')

# عرض عدد الفيديوهات
video_count_label = tk.Label(video_count_frame, text=f"Videos Played: {video_count}", font=("Helvetica", 14, "bold"), bg="#F0F0F0")
video_count_label.pack()

# تشغيل حلقة أحداث واجهة المستخدم
root.mainloop()

