import os import json import time import asyncio import logging import aiohttp from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters from uuid import uuid4

=== CONFIG ===

OWNER_ID = 7841882010 API_ID = 22545644 API_HASH = "5b8f3b235407aea5242c04909e38d33d" BOT_TOKEN = "7840637941:AAEzl5YGgQ1Utl5hgRn_j_b3OQVmetLe6kw" DATA_FILE = "voices.json"

=== LOGGING ===

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

=== LOAD/SAVE DATA ===

def load_data(): if not os.path.exists(DATA_FILE): return {} with open(DATA_FILE, "r") as f: return json.load(f)

def save_data(data): with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2)

user_data = load_data()

=== VOICE DATABASE ===

VOICE_OPTIONS = { "English (US) 🇺🇸": ["en-US-JennyNeural", "en-US-GuyNeural"], "Hindi 🇮🇳": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"], "Japanese 🇯🇵": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"], "Arabic 🇸🇦": ["ar-SA-ZariyahNeural", "ar-SA-HamzaNeural"], "French 🇫🇷": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"], "Spanish 🇪🇸": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"], "Russian 🇷🇺": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"] # Add more voices here... }

=== WELCOME ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): text = """ 👋 Welcome to Microsoft TTS Bot!

🎙️ Convert text to speech in 50+ languages. 🗣️ Choose Male or Female voice. 📢 Use /broadcast to send messages to all users. 💁‍♂️ Made with ❤️ by @ll_ZORO_DEFAULTERS_ll """ keyboard = [ [InlineKeyboardButton("🗣️ Voices", callback_data="voices")], [InlineKeyboardButton("📖 Help", callback_data="help")], [InlineKeyboardButton("👑 Owner", url="https://t.me/ll_ZORO_DEFAULTERS_ll")] ] await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

=== HELP ===

async def help_msg(update: Update, context: ContextTypes.DEFAULT_TYPE): text = """ 📌 How to use this bot:

1. Click "🗣️ Voices" to choose a voice.


2. Send a message and the bot will reply with TTS audio.


3. Use /broadcast <message> to send announcements.



Only owner can use /broadcast. """ keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]] await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

=== CALLBACK HANDLER ===

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer()

if query.data == "voices":
    keyboard = []
    for lang, voices in VOICE_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(f"{lang}", callback_data=f"set_{voices[0]}")])
        keyboard.append([InlineKeyboardButton(f"{lang} (Male)", callback_data=f"set_{voices[1]}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
    await query.edit_message_text("🎙️ Choose your voice:", reply_markup=InlineKeyboardMarkup(keyboard))

elif query.data.startswith("set_"):
    voice = query.data.split("set_")[1]
    user_id = str(query.from_user.id)
    user_data[user_id] = {"voice": voice}
    save_data(user_data)
    await query.edit_message_text(f"✅ Voice set to `{voice}`.", parse_mode="Markdown")

elif query.data == "help":
    await help_msg(update, context)

elif query.data == "back":
    await start(update, context)

=== TTS GENERATOR ===

async def generate_tts(text, voice): url = "https://eastus.tts.speech.microsoft.com/cognitiveservices/v1" headers = { "Ocp-Apim-Subscription-Key": "YOUR_MS_API_KEY", "Content-Type": "application/ssml+xml", "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3", "User-Agent": "KiraTTSBot" } body = f""" <speak version='1.0' xml:lang='en-US'> <voice name='{voice}'>{text}</voice> </speak> """ async with aiohttp.ClientSession() as session: async with session.post(url, headers=headers, data=body.encode("utf-8")) as resp: if resp.status == 200: return await resp.read() else: return None

=== TEXT HANDLER ===

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = str(update.effective_user.id) voice = user_data.get(user_id, {}).get("voice") if not voice: await update.message.reply_text("⚠️ Please choose a voice first using /start → Voices") return

await update.message.reply_text("🎧 Generating audio...")
audio = await generate_tts(update.message.text, voice)
if audio:
    file_name = f"tts_{uuid4().hex}.mp3"
    with open(file_name, "wb") as f:
        f.write(audio)
    await update.message.reply_voice(voice=open(file_name, "rb"))
    os.remove(file_name)
else:
    await update.message.reply_text("❌ Failed to generate TTS. Try again.")

=== BROADCAST ===

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != OWNER_ID: return msg = " ".join(context.args) if not msg: await update.message.reply_text("⚠️ Usage: /broadcast <message>") return count = 0 for uid in user_data.keys(): try: await context.bot.send_message(chat_id=int(uid), text=msg) count += 1 await asyncio.sleep(0.2) except: pass await update.message.reply_text(f"✅ Sent to {count} users.")

=== MAIN ===

async def main(): app = Application.builder().token(BOT_TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("broadcast", broadcast)) app.add_handler(CallbackQueryHandler(handle_buttons)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)) print("Bot is running...") await app.run_polling()

if name == 'main': asyncio.run(main())

