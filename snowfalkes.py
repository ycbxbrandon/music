import pygame
import random
import numpy as np
import moviepy.editor as mp
import librosa

# Initialize Pygame
pygame.init()

# Set screen dimensions to full screen
screen_w, screen_h = 1366, 768 

screen = pygame.display.set_mode((screen_w, screen_h), pygame.FULLSCREEN)

background = pygame.image.load('./image/scene.jpg')
background = pygame.transform.scale(background, (screen_w, screen_h))

background = pygame.transform.rotate(background, 0)

snowflake_image = pygame.image.load('./image/snow.png')
snowflake_image = pygame.transform.scale(snowflake_image, (20, 20)) 

fps = 30


audio = mp.AudioFileClip('./audio/faded.mp3')

audio_data, audio_sr = librosa.load('./audio/faded.mp3', sr=None)

tempo, _ = librosa.beat.beat_track(y=audio_data, sr=audio_sr)

speed_adjustment = tempo / 100 

# Create a Pygame clock
clock = pygame.time.Clock()

snowflakes = []
num_snowflakes = 100

for _ in range(num_snowflakes):
    x = random.uniform(0, screen_w)
    y = random.uniform(-50, -20)
    size = random.uniform(5, 10) 
    speed = random.uniform(4, 5) * speed_adjustment 
    start_time = random.uniform(0, audio.duration)  
    wind_effect = random.uniform(-0.5, 0.5)
    snowflakes.append([x, y, size, speed, start_time, wind_effect])

# Create a function to generate the video frame by frame
def make_frame(t):
    screen.blit(background, (0, 0))
    
    for flake in snowflakes:
        x, y, size, speed, start_time, wind_effect = flake

        if t >= start_time:
            y += speed  
            size += 0.1
            x += wind_effect  
            flake[1] = y
            flake[2] = size
            flake[0] = x

            if y > screen_h:
                flake[0] = random.uniform(0, screen_w)
                flake[1] = random.uniform(-50, -20)
                flake[2] = random.uniform(5, 10)
                flake[3] = random.uniform(4, 5) * speed_adjustment
                flake[4] = random.uniform(0, audio.duration)
                flake[5] = random.uniform(-0.5, 0.5)

            # Draw the snowflake
            screen.blit(pygame.transform.scale(snowflake_image, (int(size), int(size)),), (x, y))

    # Make sure there are snowflakes on the very left side
    if t < min(flake[4] for flake in snowflakes):
        for flake in snowflakes:
            x, y, size, speed, start_time, wind_effect = flake
            if x < 20:
                x = random.uniform(0, 50)
                y = random.uniform(-50, -20)
                size = random.uniform(5, 10)
                wind_effect = random.uniform(-0.5, 0.5)
                flake[0] = x
                flake[1] = y
                flake[2] = size
                flake[5] = wind_effect

            screen.blit(pygame.transform.scale(snowflake_image, (int(size), int(size)),), (x, y))

    pygame.display.flip()
    clock.tick(fps)

    screen_string = pygame.image.tostring(screen, 'RGB')

    screen_np = np.frombuffer(screen_string, dtype=np.uint8).reshape((screen_h, screen_w, 3))

    return screen_np

animation = mp.VideoClip(make_frame, duration=audio.duration)

animation = animation.set_audio(audio)

animation.write_videofile('snowflakes.mp4', codec='libx264', fps=fps)

pygame.quit()
