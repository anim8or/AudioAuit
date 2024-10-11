import os
import subprocess
from pydub import AudioSegment

def safe_text(text):
    # Replace or escape special characters for FFmpeg drawtext
    return text.replace("'", "").replace('"', "").replace(":", "").replace("\\", "")

def create_video_for_audio(audio_file, image_file, output_video, duration):
    # Use a safe version of the filename for the drawtext
    safe_filename = safe_text(os.path.basename(audio_file))
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_file,
        "-i", audio_file,
        "-t", str(duration),
        "-vf", f"drawtext=text='{safe_filename}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-50",
        "-shortest",
        "-y",
        output_video
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)

def combine_audio_files(input_folder, image_file, output_video, clip_duration=60):
    audio_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(('.mp3', '.wav'))]
    temp_videos = []

    for audio_file in audio_files:
        audio = AudioSegment.from_file(audio_file)
        # Use the specified duration or the length of the audio file, whichever is shorter
        duration = min(clip_duration * 1000, len(audio)) / 1000

        if audio.channels != 1:
            audio = audio.set_channels(1)
            print(f"Converted '{os.path.basename(audio_file)}' to mono.")

        temp_video_file = os.path.join(input_folder, f"temp_{os.path.basename(audio_file)}.mp4")
        temp_videos.append(temp_video_file)
        create_video_for_audio(audio_file, image_file, temp_video_file, duration)

    # Write video file paths to temp_video_list.txt
    with open("temp_video_list.txt", "w") as f:
        for temp_video in temp_videos:
            quoted_path = temp_video.replace("'", "'\\''")
            f.write(f"file '{quoted_path}'\n")

    ffmpeg_concat_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "temp_video_list.txt",
        "-c", "copy",
        "-y", output_video
    ]

    try:
        subprocess.run(ffmpeg_concat_cmd, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr.decode()}")  # Capture and print FFmpeg error

    # Clean up temp files
    for temp_video in temp_videos:
        os.remove(temp_video)
    os.remove("temp_video_list.txt")

# Usage example
input_folder = ""# Place loaction of music files here
image_file = ""# Place location of image here
output_video = ""#Place Location to write video out here
clip_duration = 60  # Duration in seconds

combine_audio_files(input_folder, image_file, output_video, clip_duration)
