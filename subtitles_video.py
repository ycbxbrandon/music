from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip

# Define input file paths
audio_file = './audio/vegeta.mp3'
subtitles_file = './sub/vegeta.srt'
image_file = './image/Vegeta.jpg'

# Define output file path
output_file = 'subtitle_video.mp4'

# Load the audio
audio_clip = AudioFileClip(audio_file)

# Create the background clip
background_clip = ImageClip(image_file, duration=audio_clip.duration)

# Load and process the subtitles
subtitles = []
current_subtitle = {"text": [], "start_time": None, "end_time": None}
with open(subtitles_file, 'r', encoding='utf-8') as subtitle_file:
    for line in subtitle_file:
        line = line.strip()
        if not line:
            if current_subtitle["text"]:
                subtitles.append(current_subtitle)
            current_subtitle = {"text": [], "start_time": None, "end_time": None}
        elif '-->' in line:
            start, end = line.split(' --> ')
            current_subtitle["start_time"] = start.strip()
            current_subtitle["end_time"] = end.strip()
        else:
            current_subtitle["text"].append(line)

# Define a custom generator to create styled subtitles with transitions
def subtitle_generator(subtitles, fontsize=55, font_color='white'):
    for i, subtitle in enumerate(subtitles):
        start_time = convert_to_seconds(subtitle["start_time"])
        end_time = convert_to_seconds(subtitle["end_time"])
        text = '\n'.join(subtitle["text"][1:])  # Skip the first line (numbering)
        text_clip = TextClip(
            text, fontsize=fontsize, font='Rasa-Bold', color=font_color,
            size=(background_clip.w, None), method='caption', align='center'
        ).set_position(("center", "center"))
        if i < len(subtitles) - 1:
            next_start = convert_to_seconds(subtitles[i + 1]["start_time"])
            duration = min(end_time, next_start) - start_time
        else:
            duration = end_time - start_time
        text_clip = (text_clip.set_start(start_time)
                              .set_duration(duration)
                              .crossfadein(0.5)
                              .crossfadeout(0.5))
        yield text_clip

def convert_to_seconds(time_str):
    h, m, s = map(float, time_str.replace(',', '.').split(':'))
    return 3600 * h + 60 * m + s

# Create a video with styled subtitles
subtitles_clip = CompositeVideoClip(list(subtitle_generator(subtitles)))

# Set the duration to match the audio
subtitles_clip = subtitles_clip.set_audio(audio_clip).set_duration(audio_clip.duration)
subtitles_clip = subtitles_clip.set_pos('center')
# Overlay the subtitles on the background clip
final_clip = CompositeVideoClip([background_clip, subtitles_clip])

# Write the final video to the output file
final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', fps=30, threads=4)
