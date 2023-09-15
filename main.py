import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import json
from functools import partial
import threading

def get_media_tracks(mkv_file_path):
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        mkv_file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = json.loads(result.stdout)

    audio_tracks = []
    subtitle_tracks = []
    for index, stream in enumerate(data['streams']):
        if stream['codec_type'] == 'audio':
            audio_tracks.append((index, stream.get('tags', {}).get('language', 'unknown')))
        elif stream['codec_type'] == 'subtitle':
            subtitle_tracks.append((index, stream.get('tags', {}).get('language', 'unknown')))
    
    return audio_tracks, subtitle_tracks

def convert_file(mkv_file_path, audio_var, subtitle_var, preset_var, feedback_text, progress_bar):
    audio_index = audio_var.get()
    subtitle_index = subtitle_var.get()
    preset_value = preset_var.get()
    mp4_file_path = mkv_file_path.replace('.mkv', '_converted.mp4')
    
    cmd = [
        'ffmpeg',
        '-i', mkv_file_path,
        '-map', '0:v:0',
        '-map', f'0:{audio_index}',
        '-map', f'0:{subtitle_index}',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-ac', '2',
        '-c:s', 'mov_text',
        '-preset', preset_value,
        mp4_file_path
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    progress_bar.start(10)  # This starts the indeterminate progress bar

    for line in process.stdout:
        feedback_text.insert(tk.END, line)
        feedback_text.see(tk.END)

    progress_bar.stop()
    feedback_text.insert(tk.END, 'Conversion complete!')
    feedback_text.see(tk.END)

MAX_TRACKS_PER_COLUMN = 10

def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select MKV file", filetypes=[("MKV files", "*.mkv")])
    if not file_path:
        return

    audio_tracks, subtitle_tracks = get_media_tracks(file_path)

    for widget in root.winfo_children():
        widget.destroy()

    ttk.Label(root, text="Select an audio track:").grid(row=0, column=0, columnspan=2)
    
    audio_var = tk.IntVar()
    for idx, (track, lang) in enumerate(audio_tracks):
        col_idx = (idx // MAX_TRACKS_PER_COLUMN) * 2  # Column index is computed based on how many tracks we've already added.
        ttk.Radiobutton(root, text=f"Track {track} - Language: {lang}", variable=audio_var, value=track).grid(row=(idx % MAX_TRACKS_PER_COLUMN) + 1, column=col_idx)

    max_audio_col = -(-(len(audio_tracks) - 1) // MAX_TRACKS_PER_COLUMN) * 2  # Ceiling division to find the max column index for audio

    ttk.Label(root, text="Select a subtitle track:").grid(row=0, column=max_audio_col + 1, columnspan=2)

    subtitle_var = tk.IntVar()
    for idx, (track, lang) in enumerate(subtitle_tracks):
        col_idx = max_audio_col + 1 + (idx // MAX_TRACKS_PER_COLUMN) * 2
        ttk.Radiobutton(root, text=f"Track {track} - Language: {lang}", variable=subtitle_var, value=track).grid(row=(idx % MAX_TRACKS_PER_COLUMN) + 1, column=col_idx)

    max_subtitle_col = max_audio_col + 1 + -(-(len(subtitle_tracks) - 1) // MAX_TRACKS_PER_COLUMN) * 2

    ttk.Label(root, text="Select a preset:").grid(row=0, column=max_subtitle_col + 1)
    preset_var = tk.StringVar(value='medium')
    presets = ttk.Combobox(root, textvariable=preset_var, values=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'])
    presets.grid(row=1, column=max_subtitle_col + 1)
    presets.set('medium')

    feedback_text = tk.Text(root, height=10, width=50)
    feedback_text.grid(row=MAX_TRACKS_PER_COLUMN + 2, column=0, columnspan=max_subtitle_col + 3)

    progress_bar = ttk.Progressbar(root, mode='indeterminate')
    progress_bar.grid(row=MAX_TRACKS_PER_COLUMN + 3, column=0, columnspan=max_subtitle_col + 3, sticky="ew", pady=10)

    on_convert = partial(
        convert_file, file_path, audio_var, subtitle_var, preset_var, feedback_text, progress_bar
    )

    convert_button = ttk.Button(root, text="Convert", command=lambda: threading.Thread(target=on_convert).start())
    convert_button.grid(row=MAX_TRACKS_PER_COLUMN + 4, column=0, columnspan=max_subtitle_col + 3)

    back_button = ttk.Button(root, text="Back", command=create_main_ui)
    back_button.grid(row=MAX_TRACKS_PER_COLUMN + 5, column=0, columnspan=max_subtitle_col + 3)


def create_main_ui():
    for widget in root.winfo_children():
        widget.destroy()
    open_button = ttk.Button(root, text="Open MKV File", command=open_file_dialog)
    open_button.pack()

root = tk.Tk()
root.title("MKV to MP4 Converter")

create_main_ui()

root.mainloop()
