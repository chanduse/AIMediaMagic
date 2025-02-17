import os
from openai import OpenAI
import requests
from io import BytesIO
from PIL import Image
import logging
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        self.client = OpenAI()  # Will automatically use OPENAI_API_KEY from environment

    def generate_image(self, prompt):
        try:
            logger.info("Generating image with prompt: %s", prompt)

            # Generate image using DALL-E
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )

            # Download the generated image
            image_url = response.data[0].url
            logger.info("Image generated successfully, downloading from URL")

            response = requests.get(image_url)
            if response.status_code != 200:
                logger.error("Failed to download image, status code: %d", response.status_code)
                raise Exception("Failed to download generated image")

            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            logger.info("Image downloaded and converted successfully")
            return image

        except Exception as e:
            error_message = str(e)
            logger.error("Image generation failed: %s", error_message)

            # Handle specific API errors
            if "billing_hard_limit_reached" in error_message:
                raise Exception(
                    "The AI image generation service is currently unavailable due to API limits. "
                    "Please try again later or contact support if this persists."
                )
            elif "invalid_api_key" in error_message:
                raise Exception(
                    "There was an authentication error with the image generation service. "
                    "Please contact support for assistance."
                )
            else:
                raise Exception(f"Failed to generate image: {error_message}")