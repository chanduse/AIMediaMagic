from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackContext
import config

def get_music_selection_keyboard():
    """Create inline keyboard for music selection"""
    keyboard = []
    row = []
    for track_id, track_info in config.MUSIC_TRACKS.items():
        button = InlineKeyboardButton(
            text=track_info['name'],
            callback_data=f"music_{track_id}"
        )
        row.append(button)
        if len(row) == 2:  # 2 buttons per row
            keyboard.append(row)
            row = []
    if row:  # Add any remaining buttons
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def send_error_message(update: Update, context: ContextTypes.DEFAULT_TYPE, error_message: str):
    """Send error message to user"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"❌ Error: {error_message}\n\nPlease try again or contact support if the issue persists."
    )