import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from image_generator import ImageGenerator
from video_creator import VideoCreator
from utils import get_music_selection_keyboard, send_error_message
import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VideoBot:
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.video_creator = VideoCreator()
        self.user_states = {}  # Store user states and data

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when /start is issued."""
        await update.message.reply_text(
            "👋 Welcome to the AI Video Creator Bot!\n\n"
            "Send me a text prompt describing the image you want to create, "
            "and I'll generate a video with animation and music.\n\n"
            "Use /help to see available commands."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when /help is issued."""
        await update.message.reply_text(
            "🤖 AI Video Creator Bot Help\n\n"
            "1. Simply send me a text description of the image you want to create\n"
            "2. I'll generate an image using AI\n"
            "3. Choose background music from the options\n"
            "4. I'll create an animated video with your chosen music\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message"
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user text input."""
        try:
            # Send processing message
            processing_message = await update.message.reply_text(
                "🎨 Generating image from your prompt..."
            )

            # Generate image
            try:
                image = self.image_generator.generate_image(update.message.text)
            except Exception as e:
                logger.error("Image generation failed: %s", str(e))
                await processing_message.edit_text(
                    f"❌ {str(e)}\n\n"
                    "You can try:\n"
                    "1. Using a different prompt\n"
                    "2. Waiting a few minutes before trying again\n"
                    "3. Contacting support if the issue persists"
                )
                return

            # Store image in user state
            user_id = update.effective_user.id
            self.user_states[user_id] = {
                'image': image,
                'prompt': update.message.text
            }

            # Update processing message
            await processing_message.edit_text(
                "🎵 Image generated! Now choose background music:",
                reply_markup=get_music_selection_keyboard()
            )

        except Exception as e:
            logger.error(f"Error handling text: {str(e)}")
            await send_error_message(update, context, 
                "An unexpected error occurred. Please try again later.")

    async def handle_music_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle music selection callback."""
        query = update.callback_query
        await query.answer()

        try:
            # Get user data
            user_id = update.effective_user.id
            user_data = self.user_states.get(user_id)

            if not user_data:
                raise Exception("Session expired. Please start over.")

            # Get selected music track
            music_choice = query.data.split('_')[1]

            # Update message
            await query.edit_message_text("🎬 Creating your video...")

            # Create video
            video_path = self.video_creator.create_video(
                user_data['image'],
                music_choice
            )

            # Send video
            with open(video_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption="✨ Here's your AI-generated video!"
                )

            # Cleanup
            os.unlink(video_path)
            del self.user_states[user_id]

        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            await query.edit_message_text(f"❌ Error: {str(e)}")

    def run(self):
        """Run the bot."""
        # Create application
        application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        application.add_handler(CallbackQueryHandler(self.handle_music_selection, pattern="^music_"))

        # Start the bot
        application.run_polling()

if __name__ == '__main__':
    bot = VideoBot()
    bot.run()