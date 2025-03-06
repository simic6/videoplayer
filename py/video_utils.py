# video_utils.py
import cv2

# Function to update the frame based on slider value
def update_frame(frame_number, cap, show_frame):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)  # Set the video to the selected frame
    show_frame()  # Show the updated frame

# Function to update the frame slider during video playback
def update_frame_slider(frame_slider, cap):
    # Get the current frame position
    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    frame_slider.set(current_frame)  # Update the slider position
