import random
import colorsys
import pygame
import numpy as np
import math
import cv2
import numpy as np
import pygame
import random
import colorsys
import math
from AudioAnalyzer import *
from moviepy.editor import VideoFileClip, AudioFileClip,ImageSequenceClip,concatenate_videoclips
from moviepy.editor import AudioFileClip

# Function to generate a random color
def rnd_color():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    return [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]



filename = "./audio/ultra.mp3"

analyzer = AudioAnalyzer()
analyzer.load(filename)

pygame.init()
infoObject = pygame.display.Info()

# Set screen dimensions
screen_w = 1366
screen_h = 768

frames=[]
# Load the background image
background = pygame.image.load("image/goku.jpg")
background = pygame.transform.scale(background, (screen_w, screen_h))

# Set up the drawing window
screen = pygame.display.set_mode([screen_w, screen_h])

t = pygame.time.get_ticks()
getTicksLastFrame = t

timeCount = 0

avg_bass = 0
bass_trigger = -30
bass_trigger_started = 0

min_decibel = -80
max_decibel = 80

circle_color = (40, 40, 40)
polygon_default_color = [255, 255, 255]
polygon_bass_color = polygon_default_color.copy()
polygon_color_vel = [0, 0, 0]

poly = []  # Define poly_color here
poly_color = polygon_default_color.copy()

circleX = int(screen_w / 2)
circleY = int(screen_h / 2)

min_radius = 50
max_radius = 70
radius = min_radius
radius_vel = 0

# Vibration variables for the logo image
vibration_amplitude = 5
vibration_frequency = 1
vibration_offset = 0

# Animation offset for the entire scene
animation_offset = (0, 0)

bass = {"start": 50, "stop": 100, "count": 12}
heavy_area = {"start": 120, "stop": 250, "count": 40}
low_mids = {"start": 251, "stop": 2000, "count": 50}
high_mids = {"start": 2001, "stop": 6000, "count": 20}

freq_groups = [bass, heavy_area, low_mids, high_mids]

bars = []
tmp_bars = []

length = 0

for group in freq_groups:
    g = []
    s = group["stop"] - group["start"]
    count = group["count"]
    reminder = s % count
    step = int(s / count)
    rng = group["start"]
    for i in range(count):
        arr = None
        if reminder > 0:
            reminder -= 1
            arr = np.arange(start=rng, stop=rng + step + 2)
            rng += step + 3
        else:
            arr = np.arange(start=rng, stop=rng + step + 1)
            rng += step + 2
        g.append(arr)
        length += 1
    tmp_bars.append(g)

angle_dt = 360 / length
ang = 0

for g in tmp_bars:
    gr = []
    for c in g:
        gr.append(
            RotatedAverageAudioBar(circleX + radius * math.cos(math.radians(ang - 90)),
                                   circleY + radius * math.sin(math.radians(ang - 90)), c, (255, 0, 255), angle=ang,
                                   width=4, max_height=200))
        ang += angle_dt
    bars.append(gr)

pygame.mixer.music.load("./audio/ultra.mp3")
pygame.mixer.music.play(0)

# Load the logo image
logo_image = pygame.image.load("./image/ring.png")
logo_image = pygame.transform.scale(logo_image, (int(max_radius * 2), int(max_radius * 2)))

# Calculate the duration of the audio
audio_duration = pygame.mixer.Sound("./audio/ultra.mp3").get_length()

desired_duration = audio_duration  # Set the desired duration to match the audio duration

start_time = pygame.time.get_ticks()  # Define start_time here

running = True
while running:
    avg_bass = 0
    poly = []

    # Create a copy of the background image
    screen_copy = background.copy()

    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t

    timeCount += deltaTime

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for b1 in bars:
        for b in b1:
            b.update_all(deltaTime, pygame.mixer.music.get_pos() / 1000.0, analyzer)

    for b in bars[0]:
        avg_bass += b.avg

    avg_bass /= len(bars[0])

    if avg_bass > bass_trigger:
        if bass_trigger_started == 0:
            bass_trigger_started = pygame.time.get_ticks()
        if (pygame.time.get_ticks() - bass_trigger_started) / 1000.0 > 2:
            polygon_bass_color = rnd_color()
            bass_trigger_started = 0
        if polygon_bass_color is None:
            polygon_bass_color = rnd_color()

        # Apply the vibration effect to the logo image
        vibration_offset = vibration_amplitude * math.sin(vibration_frequency * timeCount)
        vibration_frequency += 0.01

        # Apply the animation offset
        animation_offset = (random.randint(-5, 5), random.randint(-5, 5))

    else:
        bass_trigger_started = 0
        poly_color = polygon_default_color.copy()
        polygon_bass_color = None

    radius += radius_vel * deltaTime

    for x in range(len(polygon_color_vel)):
        value = polygon_color_vel[x] * deltaTime + poly_color[x]
        poly_color[x] = value

    for b1 in bars:
        for b in b1:
            b.x, b.y = circleX + radius * math.cos(math.radians(b.angle - 90)), circleY + radius * math.sin(
                math.radians(b.angle - 90))
            b.update_rect()
            poly.append(b.rect.points[3])
            poly.append(b.rect.points[2])

    # Draw the visualization elements on the copy
    for b1 in bars:
        for b in b1:
            pygame.draw.polygon(screen_copy, (173, 216, 230), b.rect.points)

    # Draw the logo on the center circle with animation offset
    logo_position = (circleX - max_radius + animation_offset[0], circleY - max_radius + animation_offset[1] + vibration_offset)
    screen_copy.blit(logo_image, logo_position)

    # Blit the modified background image to the screen
    screen.blit(screen_copy, (0, 0))
    pygame.display.flip()

    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # Calculate elapsed time

    if elapsed_time >= desired_duration:
        break

    frame = pygame.surfarray.array3d(screen)
    frame = np.swapaxes(frame, 0, 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frames.append(frame)
     # Write the frame to the video

# Calculate the frame rate based on the audio duration and the number of frames
audio_duration = pygame.mixer.Sound(filename).get_length()
num_frames = len(frames)
fps = round(num_frames / audio_duration)

# Define the VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, fps, (screen_w, screen_h))

for frame in frames:
    out.write(frame)
# Release the VideoWriter
out.release()


video_clip = VideoFileClip('output.avi')
audio_clip = AudioFileClip('./audio/ultra.mp3')

# Set the desired output file name
output_file = "output_video_with_audio.mp4"

# Combine the video and audio
final_video = video_clip.set_audio(audio_clip)

# Write the final video
final_video.write_videofile(output_file,codec='libx264', audio_codec='aac', threads=4)

pygame.quit()
