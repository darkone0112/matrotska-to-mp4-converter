import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import json
from functools import partial

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

def convert_file(mkv_file_path, audio_var, subtitle_var, preset_var):
    audio_index = audio_var.get()
    subtitle_index = subtitle_var.get()
    preset_value = preset_var.get()
    mp4_file_path = mkv_file_path.replace('.mkv', '_converted.mp4')
    
    cmd = [
        'ffmpeg',
        '-i', mkv_file_path,
        '-map', '0:v:0',  # This is mapping the first video stream
        '-map', f'0:{audio_index}',  # This is mapping the audio stream
        '-map', f'0:{subtitle_index}',  # This is mapping the subtitle stream
        '-c:v', 'copy',  # This is copying the video codec
        '-c:a', 'aac',  # This is converting the audio to AAC
        '-ac', '2',  # This is downmixing audio to stereo
        '-c:s', 'mov_text',  # This is converting subtitles to mov_text
        '-preset', preset_value,  # This is using the preset value for encoding
        mp4_file_path
    ]
    subprocess.run(cmd)



def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select MKV file", filetypes=[("MKV files", "*.mkv")])
    if not file_path:
        return

    audio_tracks, subtitle_tracks = get_media_tracks(file_path)

    new_window = tk.Toplevel(root)
    new_window.title("Select Tracks")
    
    ttk.Label(new_window, text="Select an audio track:").pack()
    
    audio_var = tk.IntVar()
    for idx, lang in audio_tracks:
        ttk.Radiobutton(new_window, text=f"Track {idx} - Language: {lang}", variable=audio_var, value=idx).pack()
    
    ttk.Label(new_window, text="Select a subtitle track:").pack()
    
    subtitle_var = tk.IntVar()
    for idx, lang in subtitle_tracks:
        ttk.Radiobutton(new_window, text=f"Track {idx} - Language: {lang}", variable=subtitle_var, value=idx).pack()

    # Adding a preset dropdown
    preset_var = tk.StringVar(value='medium')  # Default value
    ttk.Label(new_window, text="Select a preset:").pack()
    ttk.OptionMenu(new_window, preset_var, 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow').pack()

    on_convert = partial(convert_file, file_path, audio_var, subtitle_var, preset_var)
    
    ttk.Button(new_window, text="Convert", command=on_convert).pack()


root = tk.Tk()
root.title("MKV to MP4 Converter")

open_button = ttk.Button(root, text="Open MKV File", command=open_file_dialog)
open_button.pack()

root.mainloop()
