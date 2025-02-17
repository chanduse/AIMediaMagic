import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Video Settings
VIDEO_DURATION = 5  # seconds
OUTPUT_SIZE = (1024, 1024)
FPS = 30

# Available background music tracks (using remote URLs to avoid storing files)
MUSIC_TRACKS = {
    '1': {
        'name': 'Calm Piano',
        'url': 'https://cdn.pixabay.com/download/audio/2022/02/22/audio_d1659fc8c9.mp3'
    },
    '2': {
        'name': 'Ambient',
        'url': 'https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8395384.mp3'
    },
    '3': {
        'name': 'Peaceful',
        'url': 'https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1bcc.mp3'
    }
}
