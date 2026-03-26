import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine, Triangle
import os
from datetime import datetime
# Use CustomTkinter instead of tk/ttk
import customtkinter as ctk
# Keep standard tkinter for messagebox and filedialog
from tkinter import messagebox
from tkinter import filedialog

# Set appearance mode (System, Light, Dark) and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


# --- Core Logic Functions (unchanged) ---
def generate_rhythm_pattern(duration_ms, bpm=130, bar_length=4):
    beat_duration = 60000 / bpm
    pattern_duration = duration_ms
    rhythm = AudioSegment.silent(duration=pattern_duration).set_channels(2)
    for i in range(int(pattern_duration / beat_duration)):
        if i % 4 == 0:
            kick = Sine(50).to_audio_segment(duration=beat_duration * 0.5, volume=-6).set_channels(2)
            rhythm = rhythm.overlay(kick, position=int(i * beat_duration))
        elif i % 4 == 2:
            snare = Sine(200).to_audio_segment(duration=beat_duration * 0.3, volume=-6).set_channels(2)
            rhythm = rhythm.overlay(snare, position=int(i * beat_duration))
    return rhythm

def generate_melody_pattern(duration_ms, bpm=130, bar_length=4):
    beat_duration = 60000 / bpm
    pattern_duration = duration_ms
    melody = AudioSegment.silent(duration=pattern_duration).set_channels(2)
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    num_beats = int(pattern_duration / beat_duration)
    for i in range(num_beats):
        frequency = np.random.choice(notes)
        duration = beat_duration * np.random.choice([0.5, 1, 1.5])
        note = Triangle(frequency).to_audio_segment(duration=duration * 0.8, volume=-9).set_channels(2)
        melody = melody.overlay(note, position=int(i * beat_duration))
    return melody

def generate_multiple_random_wavs(base_output_dir, base_filename, num_files, first_file_duration, bpm=130, duration_increment=1000):
    try:
        if num_files <= 0 or first_file_duration <= 0:
            raise ValueError("Number of tracks and duration must be positive integers.")
        if not base_filename:
             base_filename = "sample_audio"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_output_dir, timestamp)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i in range(num_files):
            duration_ms = first_file_duration * 1000 + i * duration_increment
            rhythm = generate_rhythm_pattern(duration_ms=duration_ms, bpm=bpm)
            melody = generate_melody_pattern(duration_ms=duration_ms, bpm=bpm)
            combined = rhythm.overlay(melody)
            file_path = os.path.join(output_dir, f"{base_filename}_{i+1}.wav")
            combined.export(file_path, format="wav")
            print(f"Generated {file_path} with duration {duration_ms / 1000} seconds")
        # Use standard tkinter messagebox
        messagebox.showinfo("Success", f"Generated {num_files} .wav files successfully in folder:\n{output_dir}")
    except ValueError as e:
        messagebox.showerror("Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
# --- End Core Logic ---


# --- GUI Functions ---
def browse_directory():
    # Use standard tkinter filedialog
    folder_selected = filedialog.askdirectory()
    if folder_selected: # Check if a folder was selected
        # Use ctk constants if applicable, otherwise Tkinter's END
        output_dir_entry.delete(0, "end") # Use string "end" which works for both
        output_dir_entry.insert(0, folder_selected)

def on_generate_button_click():
    base_output_dir = output_dir_entry.get()
    if not base_output_dir or not os.path.isdir(base_output_dir):
        messagebox.showerror("Input Error", "Please select a valid output directory.")
        return
    base_filename = base_filename_entry.get().strip()
    try:
        num_files_str = num_files_entry.get()
        first_duration_str = first_file_duration_entry.get()
        duration_inc_str = duration_increment_entry.get()

        # Add check for empty fields before converting to int
        if not num_files_str or not first_duration_str or not duration_inc_str:
             messagebox.showerror("Input Error", "Please fill in all numerical fields (Tracks, Duration, Increment).")
             return

        num_files = int(num_files_str)
        first_file_duration = int(first_duration_str)
        duration_increment = int(duration_inc_str)

        if num_files <= 0 or first_file_duration <= 0:
             messagebox.showerror("Input Error", "Number of tracks and duration must be positive numbers.")
             return

        generate_multiple_random_wavs(base_output_dir, base_filename, num_files, first_file_duration, duration_increment=duration_increment)
    except ValueError:
        # This catches errors if int() conversion fails
        messagebox.showerror("Input Error", "Please enter valid integer values for numerical fields.")
    except Exception as e:
         messagebox.showerror("Error", f"Could not start generation: {e}")

# --- GUI Setup ---
# Use CTk for the main window
root = ctk.CTk()
root.title("Random WAV Generator")
root.geometry("550x280") # Optional: Set a default size

# Use grid layout configuration
root.grid_columnconfigure(1, weight=1) # Allow column 1 (entries) to expand

# Create and place the widgets using CTk versions
# Row 0: Output Directory
# Use CTkLabel
label_dir = ctk.CTkLabel(root, text="Output Directory:")
label_dir.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
# Use CTkEntry
output_dir_entry = ctk.CTkEntry(root, width=300) # Adjusted width
output_dir_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
# Use CTkButton
button_browse = ctk.CTkButton(root, text="Browse...", command=browse_directory, width=80)
button_browse.grid(row=0, column=2, padx=(5, 10), pady=10)

# Row 1: Base Filename
label_base = ctk.CTkLabel(root, text="Base Filename:")
label_base.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
base_filename_entry = ctk.CTkEntry(root)
base_filename_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
base_filename_entry.insert(0, "sample_audio")

# Row 2: Number of Tracks
label_num = ctk.CTkLabel(root, text="Number of Tracks:")
label_num.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
num_files_entry = ctk.CTkEntry(root)
num_files_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Row 3: First File Duration
label_dur = ctk.CTkLabel(root, text="First File Duration (s):")
label_dur.grid(row=3, column=0, padx=(10, 5), pady=5, sticky="w")
first_file_duration_entry = ctk.CTkEntry(root)
first_file_duration_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Row 4: Duration Increment
label_inc = ctk.CTkLabel(root, text="Duration Increment (ms):")
label_inc.grid(row=4, column=0, padx=(10, 5), pady=5, sticky="w")
duration_increment_entry = ctk.CTkEntry(root)
duration_increment_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
duration_increment_entry.insert(0, "1000")

# Row 5: Generate Button
button_generate = ctk.CTkButton(root, text="Generate", command=on_generate_button_click)
# Place button spanning columns, centered below
button_generate.grid(row=5, column=0, columnspan=3, pady=20)

# Start the main event loop
root.mainloop()