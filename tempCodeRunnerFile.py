import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import pygame
import threading
from moviepy.editor import VideoFileClip
from moviepy.video.fx import all as vfx  # Importing all video effects from MoviePy
from PIL import Image, ImageTk
import numpy as np
from moviepy.editor import AudioFileClip
from moviepy.audio.AudioClip import AudioArrayClip

# Global variables
is_paused = True
video_clip = None
video_path = None
audio_clip = None
cap = None
current_frame = 0
rotation_angle = 0  # Track the rotation angle
color_filter = (1, 1, 1)  # Default RGB multiplier for color (1 means no change)

# Function to initialize pygame mixer for audio playback
def initialize_audio():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Function to update the canvas with video frames
def update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter):
    global video_clip
    
    # Rotate the frame by the specified angle
    if rotation_angle != 0:
        frame = rotate_frame(frame, rotation_angle)
    
    # Apply color filter
    frame = apply_color_filter(frame, color_filter)
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img)
    canvas.create_image(canvas_width / 2, canvas_height / 2, image=img_tk)
    canvas.image = img_tk  # Keep reference to avoid garbage collection

# Function to rotate the frame
def rotate_frame(frame, angle):
    # Get the image center
    center = tuple(np.array(frame.shape[1::-1]) / 2)
    # Get the rotation matrix
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    # Perform the rotation
    rotated_frame = cv2.warpAffine(frame, rot_mat, (frame.shape[1], frame.shape[0]))
    return rotated_frame

# Function to apply color filter to the frame
def apply_color_filter(frame, color_filter):
    # Apply the color filter to each channel of the image
    frame = frame.astype(np.float32)
    frame[..., 0] *= color_filter[0]  # Red channel
    frame[..., 1] *= color_filter[1]  # Green channel
    frame[..., 2] *= color_filter[2]  # Blue channel
    frame = np.clip(frame, 0, 255).astype(np.uint8)  # Clip values to the valid range [0, 255]
    return frame

# Function to play video and audio
def play_video_and_audio():
    global is_paused, video_clip, video_path, audio_clip, cap, current_frame

    if video_clip is None:
        messagebox.showerror("Error", "No video loaded.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open video.")
        return

    # Start the audio playback
    pygame.mixer.music.load("temp_audio.wav")
    pygame.mixer.music.play()

    while cap.isOpened():
        if is_paused:
            pygame.mixer.music.pause()  # Pause audio when paused
            continue
        else:
            pygame.mixer.music.unpause()  # Unpause audio when playing

        ret, frame = cap.read()
        if not ret:
            break

        # Update the canvas with the new frame
        update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter)

        # Update the Tkinter window
        canvas.update_idletasks()
        canvas.update()

        cv2.waitKey(1)

    cap.release()
    pygame.mixer.music.stop()

# Function to toggle play/pause
def toggle_play_pause():
    global is_paused
    if is_paused:
        is_paused = False
        play_button.config(text="Pause")
        disable_buttons(True)  # Disable buttons when playing
    else:
        is_paused = True
        play_button.config(text="Play")
        disable_buttons(False)  # Enable buttons when paused

# Function to disable all buttons except play/pause
def disable_buttons(disable):
    if disable:
        restart_button.config(state=tk.DISABLED)
        save_button.config(state=tk.DISABLED)
        open_button.config(state=tk.DISABLED)
        rotate_button.config(state=tk.DISABLED)
        color_apply_button.config(state=tk.DISABLED)
    else:
        restart_button.config(state=tk.NORMAL)
        save_button.config(state=tk.NORMAL)
        open_button.config(state=tk.NORMAL)
        rotate_button.config(state=tk.NORMAL)
        color_apply_button.config(state=tk.NORMAL)

# Function to restart the video and audio
def restart_video():
    global is_paused, video_path, cap, current_frame, rotation_angle

    if video_clip is None:
        messagebox.showerror("Error", "No video loaded.")
        return

    # Reset video to the first frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    current_frame = 0
    is_paused = True
    play_button.config(text="Play")
    disable_buttons(False)  # Enable buttons when paused

    # Restart the audio
    pygame.mixer.music.stop()
    pygame.mixer.music.play()

    # Update the canvas with the first frame
    ret, frame = cap.read()
    if ret:
        update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter)

# Function to save the video to a new file (including rotation)
def save_video():
    global video_path, rotation_angle, color_filter
    if not video_path:
        messagebox.showerror("Error", "No video loaded to save.")
        return

    try:
        # Load the video using moviepy
        video_clip = VideoFileClip(video_path)

        # Apply rotation to the video using moviepy's fx method
        if rotation_angle != 0:
            video_clip = video_clip.fx(vfx.rotate, int(rotation_angle))  # Ensure it's an integer

        # Apply color filter to the video (using a lambda function to modify each frame)
        def apply_color_filter_frame(frame):
            # Apply color filter to the frame
            frame = frame.astype(np.float32)
            frame[..., 0] *= color_filter[0]  # Red channel
            frame[..., 1] *= color_filter[1]  # Green channel
            frame[..., 2] *= color_filter[2]  # Blue channel
            frame = np.clip(frame, 0, 255).astype(np.uint8)  # Clip values to valid range [0, 255]
            return frame

        # Apply the color filter to each frame
        video_clip = video_clip.fl_image(apply_color_filter_frame)

        # If you want to add audio, load it here (e.g., from a WAV file)
        audio_clip = AudioFileClip("temp_audio.wav")  # Make sure this file path is correct
        video_clip = video_clip.set_audio(audio_clip)

        # Save the rotated and color-filtered video with audio
        video_output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if not video_output_path:
            return

        # Write the video to the output file
        video_clip.write_videofile(video_output_path, codec='libx264', audio=True, threads=4)

        messagebox.showinfo("Success", "Video has been saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to open a video file
def open_file():
    global video_clip, video_path, cap
    video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if video_path:
        video_clip = VideoFileClip(video_path)
        cap = cv2.VideoCapture(video_path)

        # Display the first frame of the video as soon as it is loaded
        ret, frame = cap.read()
        if ret:
            update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter)

        # Start video and audio playback in a separate thread
        threading.Thread(target=play_video_and_audio, daemon=True).start()

# Function to rotate the video by 45 degrees
def rotate_video():
    global rotation_angle
    rotation_angle += 45  # Increase the rotation angle by 45 degrees each time
    if rotation_angle >= 360:  # Ensure the angle does not exceed 360 degrees
        rotation_angle -= 360
    if is_paused:  # If the video is paused, update the canvas immediately
        ret, frame = cap.read()
        if ret:
            update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter)

# Function to apply RGB color filter
def apply_color_changes():
    global color_filter
    try:
        r = int(r_entry.get())
        g = int(g_entry.get())
        b = int(b_entry.get())
        # Ensure RGB values are within the range [0, 255]
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            color_filter = (r / 255.0, g / 255.0, b / 255.0)  # Normalize to [0, 1]
            if is_paused:
                ret, frame = cap.read()
                if ret:
                    update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter)
        else:
            messagebox.showerror("Error", "RGB values must be between 0 and 255.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid integers for RGB values.")

# GUI Setup
root = tk.Tk()
root.title("Video Player & Editor")
root.geometry("800x700")

# Canvas to display video
canvas_width = 800
canvas_height = 450
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack(pady=20)

# Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Button to open video file
open_button = tk.Button(button_frame, text="Open Video File", command=open_file)
open_button.grid(row=0, column=0, padx=10)

# Play/Pause Button
play_button = tk.Button(button_frame, text="Play", command=toggle_play_pause)
play_button.grid(row=0, column=1, padx=10)

# Restart Button
restart_button = tk.Button(button_frame, text="Restart", command=restart_video)
restart_button.grid(row=0, column=2, padx=10)

# Save Button
save_button = tk.Button(button_frame, text="Save Video", command=save_video)
save_button.grid(row=0, column=3, padx=10)

# Rotate Button
rotate_button = tk.Button(button_frame, text="Rotate 45°", command=rotate_video)
rotate_button.grid(row=1, column=0, padx=10, pady=5)

# Color Input Frame
color_frame = tk.Frame(root)
color_frame.pack(pady=10)

tk.Label(color_frame, text="R:").grid(row=0, column=0)
r_entry = tk.Entry(color_frame)
r_entry.grid(row=0, column=1)

tk.Label(color_frame, text="G:").grid(row=0, column=2)
g_entry = tk.Entry(color_frame)
g_entry.grid(row=0, column=3)

tk.Label(color_frame, text="B:").grid(row=0, column=4)
b_entry = tk.Entry(color_frame)
b_entry.grid(row=0, column=5)

color_apply_button = tk.Button(color_frame, text="Apply Color", command=apply_color_changes)
color_apply_button.grid(row=1, column=0, columnspan=6)

# Function to reset the color filter
def reset_color():
    global color_filter, rotation_angle
    color_filter = (1, 1, 1)  # Reset to original (no color change)
    rotation_angle = 0  # Reset rotation angle to 0
    if is_paused:
        ret, frame = cap.read()
        if ret:
            update_canvas(cap, canvas, frame, canvas_width, canvas_height, rotation_angle, color_filter)

# Reset Color Button
reset_color_button = tk.Button(button_frame, text="Reset Effects", command=reset_color)
reset_color_button.grid(row=1, column=3, padx=10, pady=5)

# Global variable to track the mute status
is_muted = False
last_volume = 1.0  # Keep track of the last volume level

# Function to toggle mute/unmute
def toggle_mute():
    global is_muted, last_volume
    if is_muted:
        pygame.mixer.music.set_volume(last_volume)  # Restore the previous volume
        mute_button.config(text="Mute")  # Change button text back to 'Mute'
    else:
        last_volume = pygame.mixer.music.get_volume()  # Store the current volume before muting
        pygame.mixer.music.set_volume(0.0)  # Mute the audio
        mute_button.config(text="Unmute")  # Change button text to 'Unmute'
    is_muted = not is_muted

# Mute/Unmute button
mute_button = tk.Button(button_frame, text="Mute", command=toggle_mute)
mute_button.grid(row=1, column=4, padx=10, pady=5)

root.mainloop()
