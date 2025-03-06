import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import threading
import time
import pygame
#rom feature_window import open_feature_window  # Import the feature window
#from video_utils import update_frame_slider  # Import the frame update function
from datetime import datetime  # Import datetime for current time and date
import numpy as np
from moviepy.editor import VideoFileClip
from moviepy.editor import VideoFileClip, AudioFileClip

# Initialize Tkinter window
root = tk.Tk()
root.title("Video Player with Flip, Rotation, Color Filters, and Speed Control")
root.geometry("1000x600")  # Larger window to give enough space for controls

# Canvas for video preview (smaller canvas size)
canvas = tk.Canvas(root, width=600, height=400)  # Reduced canvas size
canvas.grid(row=0, column=0, padx=10, pady=10)

# Label for status
label = tk.Label(root, text="Choose a video file", font=("Arial", 14))
label.grid(row=1, column=0, pady=10)

# Global variables
video_path = ""
cap = None
paused = True  # Start with video paused
current_frame = 0
playback_thread = None
out = None  # Video writer for saving the video
flip_horizontal = False  # Flag for horizontal flip
flip_vertical = False  # Flag for vertical flip
rotation_angle = 0  # Angle to rotate the video
red_filter = False  # Flag for red filter
green_filter = False  # Flag for green filter
blue_filter = False  # Flag for blue filter
zoom_factor = 1.0  # Zoom factor
playback_speed = 1.0  # Default playback speed

# Function to load video


def load_video():
    global video_path, cap, current_frame, playback_thread, audio_clip
    video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])

    if video_path:
        # Load the video with OpenCV
        cap = cv2.VideoCapture(video_path)
        current_frame = 0  # Reset the current frame
        label.config(text=f"Loaded video: {video_path.split('/')[-1]}")

        # Load the audio with MoviePy
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio  # Extract audio from the video file

        # Set video to paused and show the first frame
        paused = True
        btn_pause_resume.config(text="Resume")

        # Show the first frame immediately
        show_frame()

        # Start video playback in a separate thread
        playback_thread = threading.Thread(target=play_video_audio)
        playback_thread.start()

# Function to play video on canvas
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def play_video_audio():
    global cap, paused, current_frame, out, flip_horizontal, flip_vertical, rotation_angle, red_filter, green_filter, blue_filter, zoom_factor, playback_speed, audio_clip

    # Start audio playback using pygame.mixer
    pygame.mixer.music.load(video_path)
    pygame.mixer.music.play(loops=0, start=0.0)  # Play audio from the start

    while cap is not None and cap.isOpened():
        if not paused:
            ret, frame = cap.read()
            if ret:
                # Apply video transformations if needed (flip, rotate, etc.)
                if flip_horizontal:
                    frame = cv2.flip(frame, 1)  # Horizontal flip
                if flip_vertical:
                    frame = cv2.flip(frame, 0)  # Vertical flip

                if rotation_angle != 0:
                    height, width = frame.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
                    frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

                # Apply color filters
                if red_filter:
                    frame[:, :, 1] = 0  # Zero out the green channel
                    frame[:, :, 2] = 0  # Zero out the blue channel
                if green_filter:
                    frame[:, :, 0] = 0  # Zero out the red channel
                    frame[:, :, 2] = 0  # Zero out the blue channel
                if blue_filter:
                    frame[:, :, 0] = 0  # Zero out the red channel
                    frame[:, :, 1] = 0  # Zero out the green channel

                if super_pixelate_enabled:
                    frame = super_pixelate(frame, pixel_size=10)  # Apply pixelation effect

                # Apply zoom if necessary
                if zoom_factor != 1.0:
                    height, width = frame.shape[:2]
                    new_width = int(width * zoom_factor)
                    new_height = int(height * zoom_factor)
                    frame = cv2.resize(frame, (new_width, new_height))

                # Convert BGR (OpenCV default) to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                # Display the image on the canvas
                canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
                canvas.image = img_tk  # Keep a reference to prevent garbage collection
                
                # Write the frame to the output file if we're saving
                if out is not None:
                    out.write(frame)
                
                # Update current frame and schedule next frame
                current_frame += 1
                time.sleep(1 / (30 * playback_speed))  # Adjust speed based on playback_speed value

            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video if it's finished

# Function to toggle pause and resume
def toggle_pause():
    global paused
    paused = not paused  # Toggle the paused state

    if paused:
        btn_pause_resume.config(text="Resume")  # Change button text to "Resume"
        enable_controls()  # Enable all other controls when paused
    else:
        btn_pause_resume.config(text="Pause")  # Change button text to "Pause"
        disable_controls()  # Disable all other controls during playback

# Function to enable all controls
def enable_controls():
    btn_load.config(state=tk.NORMAL)
    btn_rewind.config(state=tk.NORMAL)
    #btn_restart.config(state=tk.NORMAL)
    btn_save.config(state=tk.NORMAL)
    btn_flip_horizontal.config(state=tk.NORMAL)
    btn_flip_vertical.config(state=tk.NORMAL)
    btn_rotate.config(state=tk.NORMAL)
    btn_red_filter.config(state=tk.NORMAL)
    btn_green_filter.config(state=tk.NORMAL)
    btn_blue_filter.config(state=tk.NORMAL)
    btn_zoom_in.config(state=tk.NORMAL)
    btn_zoom_out.config(state=tk.NORMAL)
    speed_slider.config(state=tk.NORMAL)  # Enable speed control slider
    # Enable the forward button when paused
    btn_forward_5.config(state=tk.NORMAL)  # Enable forward button when paused
    btn_backward_5.config(state=tk.NORMAL)  # Enable forward button when paused
    frame_slider.config(state=tk.NORMAL)  # Enable frame slider when paused
    btn_super_pixelate.config(state=tk.NORMAL)  # Enable forward button when paused
    btn_save_frame_as_image.config(state=tk.NORMAL)
    
   

# Function to disable all controls except pause/resume
def disable_controls():
    btn_load.config(state=tk.DISABLED)
    btn_rewind.config(state=tk.DISABLED)
    #btn_restart.config(state=tk.DISABLED)
    btn_save.config(state=tk.DISABLED)
    btn_flip_horizontal.config(state=tk.DISABLED)
    btn_flip_vertical.config(state=tk.DISABLED)
    btn_rotate.config(state=tk.DISABLED)
    btn_red_filter.config(state=tk.DISABLED)
    btn_green_filter.config(state=tk.DISABLED)
    btn_blue_filter.config(state=tk.DISABLED)
    btn_zoom_in.config(state=tk.DISABLED)
    btn_zoom_out.config(state=tk.DISABLED)
    speed_slider.config(state=tk.DISABLED)  # Disable speed control slider
    # Disable the forward button while playing
    btn_forward_5.config(state=tk.DISABLED)  # Disable forward button while playing
    btn_backward_5.config(state=tk.DISABLED)  # Disable forward button while playing
    frame_slider.config(state=tk.DISABLED)  # Disable frame slider while playing
    btn_super_pixelate.config(state=tk.DISABLED)  # Disable forward button while playing
    btn_save_frame_as_image.config(state=tk.DISABLED)
    

# Function to rewind the video (show first frame while paused)
def rewind_video():
    global current_frame
    current_frame = 0  # Reset to the first frame
    if cap:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        show_frame()  # Show the first frame immediately

# Function to restart the video (show first frame while paused)
def restart_video():
    global current_frame
    current_frame = 0  # Reset to the first frame
    if cap:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        show_frame()  # Show the first frame immediately

# Function to show a specific frame on the canvas
def show_frame():
    global cap, current_frame, flip_horizontal, flip_vertical, rotation_angle, red_filter, green_filter, blue_filter, zoom_factor
    if cap is not None:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        if ret:
            # Apply flip if necessary
            if flip_horizontal:
                frame = cv2.flip(frame, 1)  # Horizontal flip
            if flip_vertical:
                frame = cv2.flip(frame, 0)  # Vertical flip

            # Apply rotation if necessary
            if rotation_angle != 0:
                # Get the rotation matrix
                height, width = frame.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
                frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

            # Apply color filters
            if red_filter:
                frame[:, :, 1] = 0  # Zero out the green channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if green_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if blue_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 1] = 0  # Zero out the green channel

            # Apply zoom if necessary
            if zoom_factor != 1.0:
                height, width = frame.shape[:2]
                new_width = int(width * zoom_factor)
                new_height = int(height * zoom_factor)
                frame = cv2.resize(frame, (new_width, new_height))
            
            if super_pixelate_enabled:
                frame=super_pixelate(frame)

            # Convert BGR (OpenCV default) to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            # Display the image on the canvas
            canvas.create_image(0, 0, image=img_tk, anchor=tk.NW)
            canvas.image = img_tk  # Keep a reference to prevent garbage collection

# Function to save the video to a new file
def save_video():
    global cap, out, video_path, playback_speed, audio_clip

    if cap and cap.isOpened():
        # Ask the user for the output video file path
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])

        if not output_path:
            return  # If the user cancels, don't proceed
        
        # Get the frame width, height, and FPS from the original video
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Adjust the FPS based on the playback speed
        adjusted_fps = fps * playback_speed  # Change the FPS based on the playback speed

        # Initialize VideoWriter to save the video with adjusted FPS
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), adjusted_fps, (frame_width, frame_height))

        # Set the video to the first frame and start saving frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Apply flip if necessary
            if flip_horizontal:
                frame = cv2.flip(frame, 1)  # Horizontal flip
            if flip_vertical:
                frame = cv2.flip(frame, 0)  # Vertical flip

            # Apply rotation if necessary
            if rotation_angle != 0:
                height, width = frame.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
                frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

            # Apply color filters
            if red_filter:
                frame[:, :, 1] = 0  # Zero out the green channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if green_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if blue_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 1] = 0  # Zero out the green channel

            if super_pixelate_enabled:
                frame = super_pixelate(frame)  # Apply the pixelation effect

            out.write(frame)  # Write frame to output file

        out.release()  # Release the VideoWriter object

        # Extract the audio from the original video file
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio  # Extract audio from the video

        # Save the audio to a separate file (we'll combine it with the video later)
        audio_output_path = output_path.replace(".mp4", "_audio.mp3")
        audio_clip.write_audiofile(audio_output_path)

        # Combine the video and audio
        final_clip = VideoFileClip(output_path)
        audio = AudioFileClip(audio_output_path)
        final_clip = final_clip.set_audio(audio)  # Set the audio to the video

        # Save the final video with audio
        final_clip.write_videofile(output_path, codec='libx264')

        label.config(text=f"Video with audio saved as {output_path}")

        # Clean up temporary audio file
        os.remove(audio_output_path)

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the beginning of the video


# Speed control function
def update_speed(val):
    global playback_speed
    playback_speed = float(val)  # Adjust playback speed based on the slider value

# Flip and rotate control functions
def flip_horizontal_video():
    global flip_horizontal
    flip_horizontal = not flip_horizontal
    show_frame()  # Update the frame display

def flip_vertical_video():
    global flip_vertical
    flip_vertical = not flip_vertical
    show_frame()  # Update the frame display

def rotate_video():
    global rotation_angle
    try:
        rotation_angle = float(entry_rotation_angle.get()) % 360  # Rotate based on input angle
        show_frame()  # Update the frame display
    except ValueError:
        pass  # Handle invalid input gracefully

# Filter control functions
def apply_red_filter():
    global red_filter
    red_filter = not red_filter
    show_frame()  # Update the frame display

def apply_green_filter():
    global green_filter
    green_filter = not green_filter
    show_frame()  # Update the frame display

def apply_blue_filter():
    global blue_filter
    blue_filter = not blue_filter
    show_frame()  # Update the frame display

# Zoom control functions
def zoom_in():
    global zoom_factor
    zoom_factor += 0.1
    show_frame()  # Update the frame display

def zoom_out():
    global zoom_factor
    zoom_factor = max(0.1, zoom_factor - 0.1)  # Prevent zooming out too far
    show_frame()  # Update the frame display

# GUI elements (buttons, etc.)
btn_load = tk.Button(root, text="Load Video", command=load_video)
btn_load.grid(row=0, column=1, padx=10, pady=10)

btn_pause_resume = tk.Button(root, text="Pause", command=toggle_pause)
btn_pause_resume.grid(row=1, column=1, padx=10, pady=10)

btn_rewind = tk.Button(root, text="Rewind", command=rewind_video)
btn_rewind.grid(row=2, column=1, padx=10, pady=10)

#btn_restart = tk.Button(root, text="Restart", command=restart_video)
#btn_restart.grid(row=3, column=1, padx=10, pady=10)

btn_save = tk.Button(root, text="Save Video", command=save_video)
btn_save.grid(row=4, column=1, padx=10, pady=10)

# Flip and rotation controls
frame_flip_rotate = tk.Frame(root)
frame_flip_rotate.grid(row=0, column=2, padx=10, pady=10)

btn_flip_horizontal = tk.Button(frame_flip_rotate, text="Flip Horizontal", command=flip_horizontal_video)
btn_flip_horizontal.grid(row=0, column=0, padx=5, pady=5)

btn_flip_vertical = tk.Button(frame_flip_rotate, text="Flip Vertical", command=flip_vertical_video)
btn_flip_vertical.grid(row=1, column=0, padx=5, pady=5)

btn_rotate = tk.Button(frame_flip_rotate, text="Rotate", command=rotate_video)
btn_rotate.grid(row=2, column=0, padx=5, pady=5)

entry_rotation_angle = tk.Entry(frame_flip_rotate)
entry_rotation_angle.grid(row=3, column=0, padx=5, pady=5)
entry_rotation_angle.insert(0, "0")  # Default rotation angle is 0

# Create a new frame for color filter controls
frame_color_filters = tk.Frame(root)
frame_color_filters.grid(row=2, column=2, padx=10, pady=10)

btn_red_filter = tk.Button(frame_color_filters, text="Blue Filter", command=apply_red_filter)
btn_red_filter.grid(row=0, column=0, padx=5, pady=5)

btn_green_filter = tk.Button(frame_color_filters, text="Green Filter", command=apply_green_filter)
btn_green_filter.grid(row=1, column=0, padx=5, pady=5)

btn_blue_filter = tk.Button(frame_color_filters, text="Red Filter", command=apply_blue_filter)
btn_blue_filter.grid(row=2, column=0, padx=5, pady=5)

# Zoom control buttons
btn_zoom_in = tk.Button(frame_color_filters, text="Zoom In", command=zoom_in)
btn_zoom_in.grid(row=3, column=0, padx=5, pady=5)

btn_zoom_out = tk.Button(frame_color_filters, text="Zoom Out", command=zoom_out)
btn_zoom_out.grid(row=4, column=0, padx=5, pady=5)

# Playback speed slider
speed_slider = tk.Scale(root, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Speed Control", command=update_speed)
speed_slider.set(1.0)  # Set initial speed to 1.0 (normal speed)
speed_slider.grid(row=3, column=0, padx=10, pady=10)


#btn_open_feature_window = tk.Button(root, text="Open Feature Window", command=lambda: open_feature_window(root, cap, show_frame, current_frame))
#btn_open_feature_window.grid(row=5, column=0, padx=10, pady=10)

# Function to move forward by 5 frames
def move_forward_5_frames():
    global current_frame
    current_frame += 5
    if cap:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if current_frame >= frame_count:  # Prevent exceeding total frame count
            current_frame = frame_count - 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        show_frame()  # Show updated frame

# Function to move backward by 5 frames
def move_backward_5_frames():
    global current_frame
    current_frame -= 5
    if current_frame < 0:  # Prevent going below frame 0
        current_frame = 0
    if cap:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        show_frame()  # Show updated frame

# Add the buttons to the GUI

# Frame for moving frames forward and backward
frame_navigation = tk.Frame(root)
frame_navigation.grid(row=2, column=1, padx=10, pady=10)

btn_forward_5 = tk.Button(frame_navigation, text="Forward 5 Frames", command=move_forward_5_frames)
btn_forward_5.grid(row=0, column=0, padx=5, pady=5)

btn_backward_5 = tk.Button(frame_navigation, text="Backward 5 Frames", command=move_backward_5_frames)
btn_backward_5.grid(row=1, column=0, padx=5, pady=5)


# Function to save the current frame as an image
def save_current_frame_as_image():
    global cap, current_frame, flip_horizontal, flip_vertical, rotation_angle, red_filter, green_filter, blue_filter, super_pixelate_enabled

    if cap and cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)  # Set to the current frame
        ret, frame = cap.read()
        
        if ret:
            # Apply flip if necessary
            if flip_horizontal:
                frame = cv2.flip(frame, 1)  # Horizontal flip
            if flip_vertical:
                frame = cv2.flip(frame, 0)  # Vertical flip

            # Apply rotation if necessary
            if rotation_angle != 0:
                height, width = frame.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
                frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

            # Apply color filters
            if red_filter:
                frame[:, :, 1] = 0  # Zero out the green channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if green_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if blue_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 1] = 0  # Zero out the green channel

            # Apply super pixelation effect if enabled
            if super_pixelate_enabled:
                frame = super_pixelate(frame)

            # Convert the frame to RGB format (from BGR, OpenCV default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Ask the user for the save location and file name
            output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")])
            
            if output_path:  # If the user chooses a location
                img.save(output_path)  # Save the image
                label.config(text=f"Frame saved as {output_path}")
        else:
            print("Error: Unable to read the current frame.")
    else:
        print("Error: Video capture not opened.")

# Add the button to save the current frame as an image
btn_save_frame_as_image = tk.Button(root, text="Save Frame as Image", command=save_current_frame_as_image)
btn_save_frame_as_image.grid(row=0, column=3, padx=10, pady=10, sticky="e")  # Place it on the right side


# Function to update the current frame based on the slider position
def update_frame_slider(val):
    global cap, current_frame
    current_frame = int(val)
    if cap:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        show_frame()  # Show the updated frame

# Create a frame slider for navigation
frame_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Frame", command=update_frame_slider)
frame_slider.grid(row=0, column=4, padx=10, pady=10, sticky="ew")  # Place it to the right of the "Save Frame" button

# Function to update the slider range based on the total number of frames
def update_slider_range():
    global cap
    if cap:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_slider.config(to=total_frames-1)

# Call the update_slider_range function when the video is loaded
def load_video():
    global cap, current_frame
    # Code for loading the video goes here...
    update_slider_range()  # Update the slider range after video is loaded


# Function to apply super pixelation to the current frame
def super_pixelate(frame, pixel_size=10):
    height, width = frame.shape[:2]
    # Downscale the image to "pixelize" it
    small = cv2.resize(frame, (width // pixel_size, height // pixel_size), interpolation=cv2.INTER_LINEAR)
    # Upscale it back to the original size
    pixelated = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)
    return pixelated

# Global variable to toggle pixelation
super_pixelate_enabled = False

# Function to enable super pixelation effect
def enable_super_pixelate():
   
    global super_pixelate_enabled
    super_pixelate_enabled = not super_pixelate_enabled  # Toggle the flag
    show_frame()
    
  

btn_super_pixelate = tk.Button(frame_color_filters, text="Super Pixelate", command=enable_super_pixelate)
btn_super_pixelate.grid(row=5, column=0, padx=5, pady=5)


def save_video():
    global cap, out, video_path, playback_speed, flip_horizontal, flip_vertical, rotation_angle, red_filter, green_filter, blue_filter, super_pixelate_enabled
    if cap and cap.isOpened():
        # Ask the user for the output video file path
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        
        if not output_path:
            return  # If the user cancels, don't proceed
        
        # Get the frame width, height, and FPS from the original video
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Adjust the FPS based on the playback speed
        adjusted_fps = fps * playback_speed  # Change the FPS based on the playback speed
        
        # Initialize VideoWriter to save the video with adjusted FPS
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), adjusted_fps, (frame_width, frame_height))

        # Set the video to the first frame and start saving frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Apply flip if necessary
            if flip_horizontal:
                frame = cv2.flip(frame, 1)  # Horizontal flip
            if flip_vertical:
                frame = cv2.flip(frame, 0)  # Vertical flip

            # Apply rotation if necessary
            if rotation_angle != 0:
                height, width = frame.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
                frame = cv2.warpAffine(frame, rotation_matrix, (width, height))

            # Apply color filters
            if red_filter:
                frame[:, :, 1] = 0  # Zero out the green channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if green_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 2] = 0  # Zero out the blue channel
            if blue_filter:
                frame[:, :, 0] = 0  # Zero out the red channel
                frame[:, :, 1] = 0  # Zero out the green channel

            # Apply super pixelation effect if enabled
            if super_pixelate_enabled:
                frame = super_pixelate(frame)

            out.write(frame)  # Write the frame to the output file

        out.release()  # Release the VideoWriter object
        label.config(text=f"Video saved as {output_path}")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the beginning of the video

# Create the Save Video button
save_video_button = tk.Button(root, text="Save Video", command=save_video)

# Use grid layout to place the button at the end of the row
save_video_button.grid(row=1, column=3, padx=10, pady=10)  # Update the row/column index as per your current layout




root.mainloop()


##new window



