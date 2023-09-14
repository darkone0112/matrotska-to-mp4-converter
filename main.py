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

def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select MKV file", filetypes=[("MKV files", "*.mkv")])
    if not file_path:
        return

    audio_tracks, subtitle_tracks = get_media_tracks(file_path)

    for widget in root.winfo_children():
        widget.destroy()

    ttk.Label(root, text="Select an audio track:").pack()
    
    audio_var = tk.IntVar()
    for idx, lang in audio_tracks:
        ttk.Radiobutton(root, text=f"Track {idx} - Language: {lang}", variable=audio_var, value=idx).pack()
    
    ttk.Label(root, text="Select a subtitle track:").pack()
    
    subtitle_var = tk.IntVar()
    for idx, lang in subtitle_tracks:
        ttk.Radiobutton(root, text=f"Track {idx} - Language: {lang}", variable=subtitle_var, value=idx).pack()

    preset_var = tk.StringVar(value='medium')
    ttk.Label(root, text="Select a preset:").pack()
    ttk.OptionMenu(root, preset_var, 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow').pack()

    feedback_text = tk.Text(root, height=10, width=50)
    feedback_text.pack()

    progress_bar = ttk.Progressbar(root, mode='indeterminate')
    progress_bar.pack()

    on_convert = partial(
        convert_file, file_path, audio_var, subtitle_var, preset_var, feedback_text, progress_bar
    )

    convert_button = ttk.Button(root, text="Convert", command=lambda: threading.Thread(target=on_convert).start())
    convert_button.pack()

    back_button = ttk.Button(root, text="Back", command=create_main_ui)
    back_button.pack()

def create_main_ui():
    for widget in root.winfo_children():
        widget.destroy()
    open_button = ttk.Button(root, text="Open MKV File", command=open_file_dialog)
    open_button.pack()

root = tk.Tk()
root.title("MKV to MP4 Converter")

create_main_ui()

root.mainloop()
