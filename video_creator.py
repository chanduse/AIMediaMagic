import os
import tempfile
import requests
import logging
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import numpy as np
from PIL import Image
import config

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoCreator:
    def __init__(self):
        self.duration = config.VIDEO_DURATION
        self.fps = config.FPS
        logger.info("VideoCreator initialized with duration: %s, fps: %s", self.duration, self.fps)

    def create_zoom_effect(self, image):
        """Create a zoom effect on the image"""
        logger.info("Creating zoom effect for image size: %sx%s", image.size[0], image.size[1])
        def make_frame(t):
            zoom_factor = 1 + (t / self.duration) * 0.1  # 10% zoom over duration
            img_array = np.array(image)

            h, w = img_array.shape[:2]
            center_y, center_x = h/2, w/2

            # Calculate new size
            new_h = int(h * zoom_factor)
            new_w = int(w * zoom_factor)

            # Calculate crop bounds
            y1 = int(center_y - h/2)
            y2 = int(center_y + h/2)
            x1 = int(center_x - w/2)
            x2 = int(center_x + w/2)

            # Create zoomed frame
            img = Image.fromarray(img_array).resize((new_w, new_h), Image.Resampling.LANCZOS)
            img_zoomed = np.array(img)

            # Crop to original size
            y_start = int((new_h - h) / 2)
            x_start = int((new_w - w) / 2)
            frame = img_zoomed[y_start:y_start+h, x_start:x_start+w]

            return frame

        return make_frame

    def download_audio(self, track_url):
        """Download audio track to temporary file"""
        logger.info("Downloading audio from URL: %s", track_url)
        try:
            response = requests.get(track_url, timeout=30)
            response.raise_for_status()

            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_audio.write(response.content)
            temp_audio.close()
            logger.info("Audio downloaded successfully to: %s", temp_audio.name)
            return temp_audio.name

        except requests.exceptions.RequestException as e:
            logger.error("Failed to download audio: %s", str(e))
            raise Exception(f"Failed to download audio track: {str(e)}")

    def create_video(self, image, music_choice):
        """Create video with zoom effect and background music"""
        logger.info("Starting video creation with music choice: %s", music_choice)
        temp_files = []  # Track temporary files for cleanup

        try:
            # Create video clip with zoom effect
            logger.info("Creating video clip with zoom effect")
            video_clip = ImageClip(self.create_zoom_effect(image), 
                               duration=self.duration)

            # Download and add background music
            music_track = config.MUSIC_TRACKS[music_choice]
            logger.info("Selected music track: %s", music_track['name'])
            audio_path = self.download_audio(music_track['url'])
            temp_files.append(audio_path)

            audio_clip = AudioFileClip(audio_path)

            # Trim or loop audio to match video duration
            audio_clip = audio_clip.subclip(0, self.duration)

            # Combine video and audio
            logger.info("Combining video and audio")
            final_clip = video_clip.set_audio(audio_clip)

            # Create temporary file for output
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_output.close()
            temp_files.append(temp_output.name)

            # Write final video
            logger.info("Writing final video to: %s", temp_output.name)
            final_clip.write_videofile(temp_output.name, 
                                   fps=self.fps, 
                                   codec='libx264', 
                                   audio_codec='aac',
                                   logger=logger)

            return temp_output.name

        except Exception as e:
            logger.error("Video creation failed: %s", str(e))
            raise Exception(f"Video creation failed: {str(e)}")

        finally:
            # Cleanup temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        logger.info("Cleaned up temporary file: %s", temp_file)
                except Exception as e:
                    logger.warning("Failed to cleanup temporary file %s: %s", temp_file, str(e))